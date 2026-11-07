from __future__ import annotations

import base64
import hashlib
import json
import os
import random
import re
import secrets
import smtplib
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import Cookie, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .database import get_connection, init_db
from . import tutor as tutor_service

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
FRONTEND_DIR = BASE_DIR / "frontend"
PAPERS_FILE = Path(__file__).parent / "data" / "papers.json"
SYLLABI_DIR = Path(__file__).parent / "data" / "syllabi"
MATERIALS_DIR = Path(__file__).parent / "data" / "materials"
PYQ_DIR = Path(__file__).parent / "data" / "pyq"
PRACTICE_DIR = Path(__file__).parent / "data" / "practice"
MOCKS_DIR = Path(__file__).parent / "data" / "mocks"
MOCK_PATTERN_FILE = MOCKS_DIR / "gate2027_pattern.json"
OFFICIAL_SYLLABUS_URL = "https://gate2027.iitm.ac.in/exam_papers_and_syllabus"
OFFICIAL_PATTERN_URL = "https://gate2027.iitm.ac.in/question_paper_pattern"
SESSION_COOKIE = "gatepath_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 30
PASSWORD_ITERATIONS = 310_000
PASSWORD_MIN_LENGTH = 10

def bootstrap_admin_account() -> None:
    """Create the optional first administrator account once during startup."""
    admin_email = os.getenv("GATEPATH_ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("GATEPATH_ADMIN_PASSWORD", "")
    if not admin_email and not admin_password:
        return
    if not admin_email or not admin_password:
        raise RuntimeError("Set both GATEPATH_ADMIN_EMAIL and GATEPATH_ADMIN_PASSWORD to bootstrap the administrator")
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", admin_email):
        raise RuntimeError("GATEPATH_ADMIN_EMAIL must be a valid email address")
    if (len(admin_password) < PASSWORD_MIN_LENGTH or not re.search(r"[a-z]", admin_password)
            or not re.search(r"[A-Z]", admin_password) or not re.search(r"\d", admin_password)):
        raise RuntimeError("GATEPATH_ADMIN_PASSWORD must be at least 10 characters and include uppercase, lowercase and a number")
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
        if not existing:
            cursor = conn.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
                ("GATEPath Administrator", admin_email, password_hash(admin_password)),
            )
            conn.execute("INSERT INTO user_profiles (user_id) VALUES (?)", (cursor.lastrowid,))


def validate_production_configuration() -> None:
    """Fail fast when production is configured without HTTPS and secure cookies."""
    if os.getenv("APP_ENV", "development").lower() != "production":
        return
    base_url = os.getenv("APP_BASE_URL", "").strip().rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("Production requires APP_BASE_URL to be a valid HTTPS origin")
    if not secure_cookies_enabled():
        raise RuntimeError("Production requires GATEPATH_SECURE_COOKIES=true")


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize persistent storage and validate production configuration."""
    validate_production_configuration()
    init_db()
    bootstrap_admin_account()
    yield


app = FastAPI(
    title="GATEPath 2027 API",
    version="0.14.0",
    description="GATEPath learning platform API with individual student accounts.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ----------------------------- Request models -----------------------------

class RegisterPayload(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)
    paper_code: str = Field(default="CS", min_length=2, max_length=3)
    target: Literal["IIT admission", "Top GATE score", "PSU opportunity", "Strong subject mastery"] = "IIT admission"
    daily_hours: int = Field(default=5, ge=1, le=16)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Please enter your full name")
        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not re.search(r"[a-z]", value) or not re.search(r"[A-Z]", value) or not re.search(r"\d", value):
            raise ValueError("Use at least one uppercase letter, one lowercase letter and one number")
        return value


class LoginPayload(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return value.strip().lower()


class ProfileUpdate(BaseModel):
    paper_code: str = Field(min_length=2, max_length=3)
    target: Literal["IIT admission", "Top GATE score", "PSU opportunity", "Strong subject mastery"]
    daily_hours: int = Field(ge=1, le=16)


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=140)
    subject: str = Field(default="General", max_length=80)
    due_date: date | None = None
    duration_minutes: int = Field(default=30, ge=5, le=600)
    priority: Literal["Low", "Normal", "High"] = "Normal"


class TaskUpdate(BaseModel):
    completed: bool | None = None
    title: str | None = Field(default=None, min_length=2, max_length=140)
    subject: str | None = Field(default=None, max_length=80)
    duration_minutes: int | None = Field(default=None, ge=5, le=600)
    priority: Literal["Low", "Normal", "High"] | None = None


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return value.strip().lower()


class PasswordResetPayload(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not re.search(r"[a-z]", value) or not re.search(r"[A-Z]", value) or not re.search(r"\d", value):
            raise ValueError("Use at least one uppercase letter, one lowercase letter and one number")
        return value


class MaterialProgressPayload(BaseModel):
    status: Literal["not_started", "in_progress", "completed"] | None = None
    bookmarked: bool | None = None
    personal_note: str | None = Field(default=None, max_length=5000)


class PyqAttemptPayload(BaseModel):
    answer: str = Field(min_length=1, max_length=100)
    spent_seconds: int = Field(default=0, ge=0, le=14400)

    @field_validator("answer")
    @classmethod
    def clean_answer(cls, value: str) -> str:
        return " ".join(value.strip().upper().split())


class PyqBookmarkPayload(BaseModel):
    bookmarked: bool


class PracticeSessionPayload(BaseModel):
    paper_code: str | None = Field(default=None, min_length=2, max_length=3)
    mode: Literal["topic", "custom", "daily"] = "custom"
    section_code: str | None = Field(default=None, max_length=12)
    topic_id: str | None = Field(default=None, max_length=32)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] | None = None
    question_type: Literal["MCQ", "MSQ", "NAT"] | None = None
    question_count: int = Field(default=10, ge=1, le=30)
    duration_minutes: int = Field(default=15, ge=1, le=180)


class PracticeAttemptPayload(BaseModel):
    question_id: str = Field(min_length=5, max_length=60)
    answer: str = Field(min_length=1, max_length=100)
    spent_seconds: int = Field(default=0, ge=0, le=14400)

    @field_validator("answer")
    @classmethod
    def clean_answer(cls, value: str) -> str:
        return " ".join(value.strip().upper().split())


class MockSessionCreatePayload(BaseModel):
    paper_code: str | None = Field(default=None, min_length=2, max_length=3)
    test_id: str = Field(min_length=3, max_length=80)


class MockResponsePayload(BaseModel):
    answer: str | None = Field(default=None, max_length=100)
    marked_for_review: bool | None = None
    visited: bool | None = None
    spent_seconds: int = Field(default=0, ge=0, le=10800)

    @field_validator("answer")
    @classmethod
    def clean_answer(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().upper().split())


class PlannerPlanCreatePayload(BaseModel):
    paper_code: str | None = Field(default=None, min_length=2, max_length=3)
    plan_days: Literal[30, 60, 90] = 60
    daily_hours: int | None = Field(default=None, ge=1, le=16)
    start_date: date | None = None
    include_general_aptitude: bool = True
    include_weekly_mock: bool = True


class PlannerTaskCreatePayload(BaseModel):
    title: str = Field(min_length=2, max_length=140)
    subject: str = Field(default="General", max_length=80)
    scheduled_date: date | None = None
    duration_minutes: int = Field(default=30, ge=5, le=600)
    priority: Literal["low", "normal", "high"] = "normal"


class PlannerTaskUpdatePayload(BaseModel):
    status: Literal["pending", "completed", "skipped"] | None = None
    scheduled_date: date | None = None
    review_quality: Literal["again", "hard", "good", "easy"] = "good"


class TutorChatPayload(BaseModel):
    message: str = Field(min_length=3, max_length=5000)
    conversation_id: str | None = Field(default=None, max_length=80)
    paper_code: str | None = Field(default=None, min_length=2, max_length=3)
    topic_id: str | None = Field(default=None, max_length=40)
    explanation_level: Literal["beginner", "advanced"] = "beginner"
    image_data_url: str | None = Field(default=None, max_length=7_100_000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("Enter a question or describe what you need help with")
        return cleaned

    @field_validator("image_data_url")
    @classmethod
    def clean_image(cls, value: str | None) -> str | None:
        return tutor_service.validate_image_data_url(value)


class TutorSimilarQuestionsPayload(BaseModel):
    topic_id: str = Field(min_length=3, max_length=40)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = "Intermediate"
    count: int = Field(default=3, ge=1, le=5)



# ------------------------------- Utilities --------------------------------

def load_papers() -> list[dict]:
    with PAPERS_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def paper_codes() -> set[str]:
    return {paper["code"] for paper in load_papers()}


def load_syllabus_data(code: str) -> dict | None:
    path = SYLLABI_DIR / f"{code}-GATE-2027.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_materials_data(code: str) -> dict | None:
    path = MATERIALS_DIR / f"{code}-GATE-2027.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_pyq_data(code: str, year: int = 2026) -> dict | None:
    path = PYQ_DIR / f"{code}-{year}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_practice_data(code: str) -> dict | None:
    path = PRACTICE_DIR / f"{code}-GATE-2027.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_practice_question(question_id: str, paper_code: str | None = None) -> dict | None:
    if paper_code:
        dataset = load_practice_data(paper_code.upper())
        return next((item for item in (dataset or {}).get("questions", []) if item.get("id") == question_id), None)
    for path in PRACTICE_DIR.glob("*-GATE-2027.json"):
        try:
            dataset = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        found = next((item for item in dataset.get("questions", []) if item.get("id") == question_id), None)
        if found:
            return found
    return None


def public_practice_question(question: dict, attempt=None) -> dict:
    result = {key: question.get(key) for key in (
        "id", "paper_code", "section_code", "section_name", "topic_id", "topic_name",
        "difficulty", "question_type", "marks", "prompt", "options",
    )}
    result["attempted"] = attempt is not None
    result["last_attempt"] = None if attempt is None else {
        "submitted_answer": attempt["submitted_answer"],
        "is_correct": bool(attempt["is_correct"]),
        "awarded_marks": attempt["awarded_marks"],
        "spent_seconds": attempt["spent_seconds"],
    }
    return result


def normalise_practice_answer(question_type: str, answer: str) -> str:
    value = answer.strip().upper()
    if question_type == "MCQ":
        if value not in {"A", "B", "C", "D"}:
            raise HTTPException(status_code=422, detail="For MCQ, select one option: A, B, C or D")
        return value
    if question_type == "MSQ":
        parts = [part.strip() for part in value.replace(";", ",").replace(" ", ",").split(",") if part.strip()]
        if not parts or any(part not in {"A", "B", "C", "D"} for part in parts):
            raise HTTPException(status_code=422, detail="For MSQ, enter one or more options separated by commas")
        if len(parts) != len(set(parts)):
            raise HTTPException(status_code=422, detail="Do not select an MSQ option more than once")
        return ";".join(sorted(parts))
    try:
        numeric = float(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="For NAT, enter a valid number") from exc
    if not (float("-inf") < numeric < float("inf")):
        raise HTTPException(status_code=422, detail="Enter a finite numerical answer")
    return format(numeric, ".12g")


def check_practice_answer(question: dict, submitted: str) -> tuple[bool, float, str]:
    qtype = question["question_type"]
    expected = question["answer_key"]
    if qtype == "MCQ":
        correct = submitted == expected
        awarded = float(question["marks"]) if correct else -float(question["marks"]) / 3
    elif qtype == "MSQ":
        correct = submitted == ";".join(sorted(expected.split(";")))
        awarded = float(question["marks"]) if correct else 0.0
    else:
        accepted = question.get("answer_range") or []
        numeric = float(submitted)
        correct = len(accepted) == 2 and float(accepted[0]) <= numeric <= float(accepted[1])
        awarded = float(question["marks"]) if correct else 0.0
    return correct, awarded, expected


def load_mock_pattern() -> dict:
    if not MOCK_PATTERN_FILE.exists():
        return {}
    try:
        return json.loads(MOCK_PATTERN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def load_mock_manifest(paper_code: str, test_id: str) -> dict | None:
    code = paper_code.upper()
    for path in MOCKS_DIR.glob(f"{code}-FULL-MOCK-*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("paper_code") == code and data.get("test_id") == test_id:
            return data
    return None

def mock_manifest_is_valid(manifest: dict) -> tuple[bool, str]:
    """Validate question structure, scoring keys and section blueprint before publication."""
    blueprint = manifest.get("blueprint", {})
    questions = manifest.get("questions", [])
    try:
        expected_count = int(blueprint.get("total_questions", -1))
        expected_marks = float(blueprint.get("total_marks", -1))
    except (TypeError, ValueError):
        return False, "The paper blueprint has invalid totals."
    if len(questions) != expected_count:
        return False, "Question count does not match the paper blueprint."
    try:
        actual_marks = sum(float(item.get("marks", 0)) for item in questions)
    except (TypeError, ValueError):
        return False, "Question marks must be numeric."
    if round(actual_marks, 5) != expected_marks:
        return False, "Question marks do not add up to the paper total."
    ids = [item.get("id") for item in questions]
    if not all(ids) or len(ids) != len(set(ids)):
        return False, "Question identifiers must be present and unique."
    if any(item.get("question_type") not in {"MCQ", "MSQ", "NAT"} or item.get("marks") not in {1, 2} for item in questions):
        return False, "Question type or marks are outside the supported GATE pattern."
    for item in questions:
        qid = item.get("id", "unknown")
        qtype = item.get("question_type")
        answer_key = item.get("answer_key")
        options = item.get("options") or []
        if not answer_key:
            return False, f"Question {qid} is missing an answer key."
        if qtype in {"MCQ", "MSQ"}:
            option_keys = [option.get("key") for option in options if isinstance(option, dict)]
            if len(options) != 4 or set(option_keys) != {"A", "B", "C", "D"} or len(option_keys) != 4:
                return False, f"Question {qid} must contain the four unique options A, B, C and D."
            if qtype == "MCQ" and answer_key not in option_keys:
                return False, f"Question {qid} has an MCQ answer key that is not one of its options."
            if qtype == "MSQ":
                selected = str(answer_key).split(";")
                if not selected or any(key not in option_keys for key in selected) or len(selected) != len(set(selected)):
                    return False, f"Question {qid} has an invalid MSQ answer key."
        else:
            answer_range = item.get("answer_range")
            try:
                value = float(answer_key)
                if not isinstance(answer_range, list) or len(answer_range) != 2:
                    raise ValueError("range must contain two numeric bounds")
                low, high = float(answer_range[0]), float(answer_range[1])
                if low > high or not low <= value <= high:
                    raise ValueError("answer key falls outside the accepted range")
            except (TypeError, ValueError):
                return False, f"Question {qid} has an invalid NAT answer key or accepted range."
    for required in ("GENERAL_APTITUDE", "ENGINEERING_MATHEMATICS", "SUBJECT"):
        expected = next((row for row in manifest.get("section_summary", []) if row.get("code") == required), None)
        actual = [row for row in questions if row.get("section_group") == required]
        if expected and (len(actual) != expected.get("question_count") or sum(float(q["marks"]) for q in actual) != expected.get("marks")):
            return False, f"{required} does not match its configured question/marks total."
    return True, "ok"

def public_mock_question(question: dict, response=None, reveal: bool = False) -> dict:
    result = {key: question.get(key) for key in (
        "id", "question_number", "section_group", "section_code", "section_name",
        "topic_id", "topic_name", "difficulty", "question_type", "marks", "prompt", "options",
    )}
    result["response"] = {
        "answer": response["answer"] if response else "",
        "marked_for_review": bool(response["marked_for_review"]) if response else False,
        "visited": bool(response["visited"]) if response else False,
        "spent_seconds": int(response["spent_seconds"]) if response else 0,
    }
    if reveal:
        answer = response["answer"] if response else ""
        if answer:
            try:
                submitted = normalise_practice_answer(question["question_type"], answer)
                correct, awarded, expected = check_practice_answer(question, submitted)
            except HTTPException:
                correct, awarded, expected = False, 0.0, question["answer_key"]
        else:
            correct, awarded, expected = False, 0.0, question["answer_key"]
        result["result"] = {
            "submitted_answer": answer, "correct_answer": expected,
            "is_correct": bool(correct), "awarded_marks": round(float(awarded), 6),
            "maximum_marks": float(question["marks"]), "solution": question.get("solution", {}),
            "answer_range": question.get("answer_range"),
        }
    return result

def mock_session_result(session: dict, manifest: dict, responses: list[dict]) -> dict:
    response_map = {row["question_id"]: row for row in responses}
    questions = manifest.get("questions", [])
    sections: dict[str, dict] = {}
    subjects: dict[str, dict] = {}
    attempted = correct_count = wrong_count = 0
    score = 0.0
    detail = []
    for question in questions:
        response = response_map.get(question["id"])
        answer = (response["answer"] or "").strip() if response else ""
        did_attempt = bool(answer)
        is_correct = False
        awarded = 0.0
        expected = question["answer_key"]
        if did_attempt:
            attempted += 1
            try:
                submitted = normalise_practice_answer(question["question_type"], answer)
                is_correct, awarded, expected = check_practice_answer(question, submitted)
            except HTTPException:
                is_correct, awarded = False, 0.0
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1
        score += awarded
        group = question.get("section_group", "SUBJECT")
        for key, bucket_map, label in ((group, sections, question.get("section_name", group)), (question.get("section_code", group), subjects, question.get("section_name", group))):
            bucket = bucket_map.setdefault(key, {"code": key, "name": label, "question_count": 0, "attempted": 0, "correct": 0, "wrong": 0, "unattempted": 0, "score": 0.0, "maximum_marks": 0.0})
            bucket["question_count"] += 1
            bucket["maximum_marks"] += float(question["marks"])
            bucket["score"] += awarded
            if not did_attempt:
                bucket["unattempted"] += 1
            else:
                bucket["attempted"] += 1
                if is_correct:
                    bucket["correct"] += 1
                else:
                    bucket["wrong"] += 1
        detail.append(public_mock_question(question, response, reveal=True))
    for item in list(sections.values()) + list(subjects.values()):
        item["score"] = round(item["score"], 6)
        item["maximum_marks"] = round(item["maximum_marks"], 4)
        item["accuracy_percent"] = round(item["correct"] / item["attempted"] * 100) if item["attempted"] else 0
    total_questions = len(questions)
    unattempted = total_questions - attempted
    maximum_marks = float(manifest.get("blueprint", {}).get("total_marks", 100))
    duration = int(session["duration_seconds"])
    elapsed = max(0, min(duration, int(time.time() - float(session["started_at"]))))
    return {
        "id": session["id"], "test_id": session["test_id"], "paper_code": session["paper_code"],
        "status": session["status"], "question_count": total_questions,
        "attempted_count": attempted, "correct_count": correct_count, "wrong_count": wrong_count,
        "unattempted_count": unattempted, "score": round(score, 6), "maximum_marks": maximum_marks,
        "accuracy_percent": round(correct_count / attempted * 100) if attempted else 0,
        "score_percent": round(score / maximum_marks * 100, 2) if maximum_marks else 0,
        "elapsed_seconds": elapsed, "duration_seconds": duration,
        "section_breakdown": list(sections.values()), "subject_breakdown": list(subjects.values()),
        "questions": detail,
    }

def finalize_mock_session(session_id: str, user_id: int, final_status: str = "submitted") -> dict:
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ? AND user_id = ?", (session_id, user_id)).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Mock-test session not found")
        if session["status"] == "active":
            if final_status == "submitted" and time.time() >= float(session["expires_at"]):
                final_status = "expired"
            manifest = load_mock_manifest(session["paper_code"], session["test_id"])
            if not manifest:
                raise HTTPException(status_code=500, detail="Mock-test manifest is unavailable")
            responses = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ?", (session_id, user_id)).fetchall()
            result = mock_session_result({**dict(session), "status": final_status}, manifest, responses)
            conn.execute(
                "UPDATE mock_test_sessions SET status = ?, submitted_at = CURRENT_TIMESTAMP, score = ?, maximum_marks = ?, attempted_count = ?, correct_count = ?, wrong_count = ? WHERE id = ? AND user_id = ?",
                (final_status, result["score"], result["maximum_marks"], result["attempted_count"], result["correct_count"], result["wrong_count"], session_id, user_id),
            )
            session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ? AND user_id = ?", (session_id, user_id)).fetchone()
        manifest = load_mock_manifest(session["paper_code"], session["test_id"])
        responses = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ?", (session_id, user_id)).fetchall()
        return mock_session_result(dict(session), manifest, responses)

def mock_session_payload(session: dict, manifest: dict, responses: list[dict]) -> dict:
    response_map = {row["question_id"]: row for row in responses}
    active = session["status"] == "active"
    return {
        "id": session["id"], "test_id": session["test_id"], "paper_code": session["paper_code"],
        "title": manifest.get("title"), "status": session["status"],
        "question_count": len(manifest.get("questions", [])),
        "duration_seconds": int(session["duration_seconds"]), "started_at": float(session["started_at"]),
        "expires_at": float(session["expires_at"]),
        "remaining_seconds": max(0, int(float(session["expires_at"]) - time.time())) if active else 0,
        "questions": [public_mock_question(question, response_map.get(question["id"]), reveal=not active) for question in manifest.get("questions", [])],
        "result": None if active else mock_session_result(session, manifest, responses),
    }


def daily_practice_question_ids(code: str, day_key: str, questions: list[dict], count: int = 5) -> list[str]:
    if not questions:
        return []
    seed = int.from_bytes(hashlib.sha256(f"{code}:{day_key}".encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed)
    picked = rng.sample(questions, min(count, len(questions)))
    return [item["id"] for item in picked]


def practice_session_questions(session_id: str, user_id: int) -> list[dict]:
    with get_connection() as conn:
        session = conn.execute(
            "SELECT question_ids, paper_code FROM practice_sessions WHERE id = ? AND user_id = ?",
            (session_id, user_id),
        ).fetchone()
        attempts = conn.execute(
            "SELECT * FROM practice_attempts WHERE session_id = ? AND user_id = ?",
            (session_id, user_id),
        ).fetchall()
    if not session:
        return []
    attempt_map = {row["question_id"]: row for row in attempts}
    result = []
    for question_id in json.loads(session["question_ids"]):
        question = find_practice_question(question_id, session["paper_code"])
        if question:
            result.append(public_practice_question(question, attempt_map.get(question_id)))
    return result


def load_pyq_catalog(code: str) -> dict:
    path = PYQ_DIR / "catalog.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            catalog = json.load(handle)
    else:
        catalog = {"archive_sources": [], "notes": []}
    return {**catalog, "paper_code": code}


def find_pyq_question(question_id: str) -> dict | None:
    for path in PYQ_DIR.glob("*-*.json"):
        if path.name == "catalog.json":
            continue
        try:
            dataset = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for session in dataset.get("sessions", []):
            for question in session.get("questions", []):
                if question.get("id") == question_id:
                    return question
    return None


def pyq_public_item(question: dict, bookmarked: bool = False, last_attempt: dict | None = None) -> dict:
    item = {key: question.get(key) for key in (
        "id", "paper_code", "year", "session", "question_number", "question_type",
        "source_section_code", "section_name", "marks", "topic_id", "topic_name",
        "editorial_label", "pdf_page", "paper_url", "answer_key_url", "source_page_url",
        "source_title", "verification_status",
    )}
    item.update({"bookmarked": bookmarked, "last_attempt": last_attempt})
    return item


def normalise_pyq_answer(question_type: str, answer: str) -> str:
    value = answer.strip().upper()
    if question_type == "MSQ":
        letters = [part.strip() for part in value.replace(";", ",").replace(" ", ",").split(",") if part.strip()]
        if not letters or any(letter not in {"A", "B", "C", "D"} for letter in letters):
            raise HTTPException(status_code=422, detail="For MSQ, enter one or more options separated by commas, such as A,C,D")
        if len(set(letters)) != len(letters):
            raise HTTPException(status_code=422, detail="Do not select the same MSQ option more than once")
        return ";".join(sorted(letters))
    if question_type == "MCQ":
        if value not in {"A", "B", "C", "D"}:
            raise HTTPException(status_code=422, detail="For MCQ, choose one option from A, B, C or D")
        return value
    try:
        number = float(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="For NAT, enter a valid number") from exc
    if not (float("-inf") < number < float("inf")):
        raise HTTPException(status_code=422, detail="Enter a finite numerical answer")
    return format(number, ".12g")


def check_pyq_answer(question: dict, submitted: str) -> tuple[bool, float, str]:
    qtype = question["question_type"]
    expected = question["answer_key"]
    if qtype in {"MCQ", "MSQ"}:
        correct = submitted == ";".join(sorted(expected.split(";"))) if qtype == "MSQ" else submitted == expected
        if correct:
            return True, float(question["marks"]), expected
        penalty = float(question["marks"]) / 3 if qtype == "MCQ" else 0.0
        return False, -penalty, expected
    accepted = question.get("answer_range") or []
    number = float(submitted)
    correct = len(accepted) == 2 and float(accepted[0]) <= number <= float(accepted[1])
    return correct, float(question["marks"]) if correct else 0.0, expected


def pyq_last_attempt(row) -> dict | None:
    if not row:
        return None
    return {
        "submitted_answer": row["submitted_answer"],
        "is_correct": bool(row["is_correct"]),
        "awarded_marks": row["awarded_marks"],
        "spent_seconds": row["spent_seconds"],
        "created_at": row["created_at"],
    }


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


# A precomputed hash keeps unknown-email login attempts on a similar password-check path.
DUMMY_PASSWORD_HASH = password_hash("GATEPathDummyPassword2027")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def public_user(row) -> dict:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "role": row["role"],
        "created_at": row["created_at"],
    }


def profile_dict(row) -> dict:
    return {
        "paper_code": row["paper_code"],
        "target": row["target"],
        "daily_hours": row["daily_hours"],
        "updated_at": row["updated_at"],
    }


def task_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "subject": row["subject"],
        "due_date": row["due_date"],
        "duration_minutes": row["duration_minutes"],
        "priority": row["priority"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
    }


def create_session(user_id: int, request: Request) -> str:
    raw_token = secrets.token_urlsafe(48)
    expires_at = time.time() + SESSION_TTL_SECONDS
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO user_sessions (user_id, token_hash, expires_at, user_agent, ip_address)
               VALUES (?, ?, ?, ?, ?)""",
            (
                user_id,
                token_hash(raw_token),
                expires_at,
                request.headers.get("user-agent", "")[:300],
                request.client.host if request.client else None,
            ),
        )
        # Opportunistically remove expired sessions and used reset records.
        conn.execute("DELETE FROM user_sessions WHERE expires_at <= ?", (time.time(),))
        conn.execute("DELETE FROM password_reset_tokens WHERE expires_at <= ? OR used_at IS NOT NULL", (time.time(),))
    return raw_token


def secure_cookies_enabled() -> bool:
    configured = os.getenv("GATEPATH_SECURE_COOKIES")
    if configured is not None:
        return configured.strip().lower() in {"1", "true", "yes", "on"}
    return os.getenv("APP_ENV", "development").lower() == "production"


def set_session_cookie(response: Response, request: Request, raw_token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=raw_token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=secure_cookies_enabled(),
        samesite="strict",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/", httponly=True,
                           secure=secure_cookies_enabled(), samesite="strict")


def session_record(raw_token: str | None):
    if not raw_token:
        return None
    with get_connection() as conn:
        row = conn.execute(
            """SELECT u.id, u.full_name, u.email, u.role, u.created_at,
                      p.paper_code, p.target, p.daily_hours, p.updated_at AS profile_updated_at
               FROM user_sessions s
               JOIN users u ON u.id = s.user_id
               JOIN user_profiles p ON p.user_id = u.id
               WHERE s.token_hash = ? AND s.expires_at > ? AND u.is_active = 1""",
            (token_hash(raw_token), time.time()),
        ).fetchone()
    return row


def require_user(gatepath_session: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    row = session_record(gatepath_session)
    if not row:
        raise HTTPException(status_code=401, detail="Please sign in to continue")
    return row


def require_admin(user=Depends(require_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


def smtp_is_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_FROM"))


def send_password_reset_email(email: str, token: str) -> None:
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("SMTP_FROM")
    if not host or not sender:
        raise RuntimeError("SMTP is not configured")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    reset_url = f"{base_url}/reset-password?token={token}"
    message = EmailMessage()
    message["Subject"] = "Reset your GATEPath password"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        "We received a request to reset your GATEPath password.\n\n"
        f"Use this one-time link within 30 minutes: {reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    with smtplib.SMTP(host, port, timeout=12) as server:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password or "")
        server.send_message(message)


@app.middleware("http")
async def security_and_origin_middleware(request: Request, call_next):
    """Apply baseline browser security headers and same-origin write protection."""
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        fetch_site = request.headers.get("sec-fetch-site", "").lower()
        if fetch_site == "cross-site":
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=403, content={"detail": "Cross-site request rejected"})
        if origin:
            configured_base = os.getenv("APP_BASE_URL", "").strip().rstrip("/")
            expected = configured_base or f"{request.url.scheme}://{request.url.netloc}"
            if origin.rstrip("/") != expected:
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=403, content={"detail": "Cross-origin request rejected"})

    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: blob: https:; "
        "font-src 'self' data: https://fonts.gstatic.com; connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "form-action 'self'; frame-ancestors 'none'",
    )
    response.headers.setdefault("X-XSS-Protection", "0")
    is_production = os.getenv("APP_ENV", "development").lower() == "production"
    if is_production and secure_cookies_enabled():
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    if request.url.path.startswith("/api/") or request.url.path in {"/app", "/workspace"}:
        response.headers.setdefault("Cache-Control", "no-store")
    return response


# --------------------------------- Pages -----------------------------------

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_DIR / "landing.html")


@app.get("/login", include_in_schema=False)
@app.get("/register", include_in_schema=False)
@app.get("/forgot-password", include_in_schema=False)
@app.get("/reset-password", include_in_schema=False)
def auth_page(request: Request, gatepath_session: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    if session_record(gatepath_session):
        return RedirectResponse(url="/app", status_code=303)
    return FileResponse(FRONTEND_DIR / "auth.html")


@app.get("/app", include_in_schema=False)
@app.get("/workspace", include_in_schema=False)
def student_workspace(request: Request, gatepath_session: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    if not session_record(gatepath_session):
        destination = request.url.path
        if request.url.query:
            destination += f"?{request.url.query}"
        return RedirectResponse(url=f"/login?next={destination}", status_code=303)
    return FileResponse(FRONTEND_DIR / "index.html")


# -------------------------------- Public API -------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "gatepath-api", "version": app.version}


@app.get("/api/ready")
def readiness():
    """Readiness check that verifies the persistent database is reachable."""
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "ready", "database": "ok", "version": app.version}
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database is not ready") from exc


@app.get("/api/papers")
def list_papers():
    items = load_papers()
    return {
        "items": items,
        "count": len(items),
        "source": OFFICIAL_SYLLABUS_URL,
        "syllabus_version": "GATE 2027",
    }


@app.get("/api/syllabus")
def get_syllabus(paper_code: str = "CS", user=Depends(require_user)):
    code = paper_code.upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    paper = next(item for item in load_papers() if item["code"] == code)
    structured = load_syllabus_data(code)
    if not structured:
        return {
            "paper": paper,
            "syllabus_version": "GATE 2027",
            "status": "awaiting_structured_import",
            "verified": False,
            "message": "The official GATE 2027 syllabus PDF is linked. Topic-level content will appear after transcription and review; no unverified topic list is presented as official content.",
            "sections": [],
            "official_url": paper.get("official_syllabus_url") or OFFICIAL_SYLLABUS_URL,
            "catalogue_url": OFFICIAL_SYLLABUS_URL,
            "last_checked": datetime.now().date().isoformat(),
        }

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT topic_id, status, bookmarked FROM student_material_progress WHERE user_id = ? AND paper_code = ?",
            (user["id"], code),
        ).fetchall()
    progress = {row["topic_id"]: {"status": row["status"], "bookmarked": bool(row["bookmarked"])} for row in rows}
    sections = []
    topic_total = 0
    topic_completed = 0
    for section in structured.get("sections", []):
        topics = []
        for topic in section.get("topics", []):
            topic_total += 1
            item = {**topic, **progress.get(topic["id"], {"status": "not_started", "bookmarked": False})}
            topic_completed += int(item["status"] == "completed")
            topics.append(item)
        sections.append({**section, "topics": topics})
    return {
        "paper": paper,
        "syllabus_version": structured.get("syllabus_version", "GATE 2027"),
        "status": structured.get("content_status", "imported_verified"),
        "verified": structured.get("content_status") == "imported_verified",
        "message": structured.get("transcription_note", "Structured syllabus content."),
        "common_section": structured.get("common_section"),
        "sections": sections,
        "official_url": structured.get("source_url") or paper.get("official_syllabus_url"),
        "catalogue_url": structured.get("catalogue_url") or OFFICIAL_SYLLABUS_URL,
        "last_checked": structured.get("source_verified_on", datetime.now().date().isoformat()),
        "progress": {"total": topic_total, "completed": topic_completed, "percent": round(topic_completed / topic_total * 100) if topic_total else 0},
    }


@app.get("/api/materials")
def list_materials(
    paper_code: str | None = None,
    section_code: str | None = None,
    q: str = Query(default="", max_length=120),
    bookmarked_only: bool = False,
    user=Depends(require_user),
):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    dataset = load_materials_data(code)
    paper = next(item for item in load_papers() if item["code"] == code)
    if not dataset:
        return {
            "paper_code": code,
            "paper_name": paper["name"],
            "content_status": "awaiting_content_import",
            "notice": "Verified topic-wise study notes have not yet been imported for this paper. Use the official syllabus PDF while the content is prepared and reviewed.",
            "official_syllabus_url": paper.get("official_syllabus_url"),
            "items": [], "sections": [],
            "summary": {"total": 0, "completed": 0, "in_progress": 0, "bookmarked": 0},
        }
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT topic_id, status, bookmarked, personal_note, updated_at FROM student_material_progress WHERE user_id = ? AND paper_code = ?",
            (user["id"], code),
        ).fetchall()
    progress = {row["topic_id"]: dict(row) for row in rows}
    items = []
    for item in dataset.get("materials", []):
        if section_code and item["section_code"] != section_code:
            continue
        row = progress.get(item["id"], {})
        status = row.get("status", "not_started")
        bookmarked = bool(row.get("bookmarked", 0))
        if bookmarked_only and not bookmarked:
            continue
        haystack = " ".join([item["topic_name"], item["section_name"], item["overview"], *item.get("common_mistakes", [])]).casefold()
        if q and q.casefold() not in haystack:
            continue
        items.append({
            "id": item["id"], "section_code": item["section_code"],
            "section_name": item["section_name"], "topic_name": item["topic_name"],
            "overview": item["overview"], "reading_minutes": item["reading_minutes"],
            "difficulty": item["difficulty"], "status": status,
            "bookmarked": bookmarked,
        })
    all_rows = [progress.get(item["id"], {}) for item in dataset.get("materials", [])]
    syllabus_for_sections = load_syllabus_data(code) or {}
    return {
        "paper_code": code,
        "paper_name": dataset.get("paper_name", paper["name"]),
        "syllabus_version": dataset.get("syllabus_version", "GATE 2027"),
        "content_version": dataset.get("content_version", "1.0.0"),
        "content_status": dataset.get("content_status", "editorial_notes"),
        "notice": dataset.get("notice", "GATEPath original notes. Verify scope against the official syllabus."),
        "official_syllabus_url": dataset.get("official_syllabus_url"),
        "sections": [{"code": section["code"], "name": section["name"]} for section in syllabus_for_sections.get("sections", [])],
        "items": items,
        "summary": {
            "total": len(dataset.get("materials", [])),
            "completed": sum(row.get("status") == "completed" for row in all_rows),
            "in_progress": sum(row.get("status") == "in_progress" for row in all_rows),
            "bookmarked": sum(bool(row.get("bookmarked")) for row in all_rows),
        },
    }


@app.get("/api/materials/{topic_id}")
def get_material(topic_id: str, paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    dataset = load_materials_data(code)
    if not dataset:
        raise HTTPException(status_code=409, detail="Study notes for this GATE paper are not available yet")
    material = next((item for item in dataset.get("materials", []) if item["id"] == topic_id), None)
    if not material:
        raise HTTPException(status_code=404, detail="Study note not found")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT status, bookmarked, personal_note, updated_at FROM student_material_progress WHERE user_id = ? AND paper_code = ? AND topic_id = ?",
            (user["id"], code, topic_id),
        ).fetchone()
    progress = dict(row) if row else {"status": "not_started", "bookmarked": 0, "personal_note": "", "updated_at": None}
    progress["bookmarked"] = bool(progress["bookmarked"])
    return {**material, "progress": progress}


@app.patch("/api/materials/{topic_id}/progress")
def update_material_progress(topic_id: str, payload: MaterialProgressPayload, paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    dataset = load_materials_data(code)
    if not dataset or not any(item["id"] == topic_id for item in dataset.get("materials", [])):
        raise HTTPException(status_code=404, detail="Study note not found for this GATE paper")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No progress fields supplied")
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT status, bookmarked, personal_note FROM student_material_progress WHERE user_id = ? AND paper_code = ? AND topic_id = ?",
            (user["id"], code, topic_id),
        ).fetchone()
        values = {
            "status": existing["status"] if existing else "not_started",
            "bookmarked": existing["bookmarked"] if existing else 0,
            "personal_note": existing["personal_note"] if existing else "",
        }
        if "status" in updates and updates["status"] is not None:
            values["status"] = updates["status"]
        if "bookmarked" in updates and updates["bookmarked"] is not None:
            values["bookmarked"] = int(updates["bookmarked"])
        if "personal_note" in updates and updates["personal_note"] is not None:
            values["personal_note"] = updates["personal_note"].strip()
        conn.execute(
            """INSERT INTO student_material_progress
               (user_id, paper_code, topic_id, status, bookmarked, personal_note)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, paper_code, topic_id) DO UPDATE SET
                 status=excluded.status, bookmarked=excluded.bookmarked,
                 personal_note=excluded.personal_note, updated_at=CURRENT_TIMESTAMP""",
            (user["id"], code, topic_id, values["status"], values["bookmarked"], values["personal_note"]),
        )
        row = conn.execute(
            "SELECT status, bookmarked, personal_note, updated_at FROM student_material_progress WHERE user_id = ? AND paper_code = ? AND topic_id = ?",
            (user["id"], code, topic_id),
        ).fetchone()
    result = dict(row)
    result["bookmarked"] = bool(result["bookmarked"])
    return result


# ---------------------------- Practice engine -----------------------------

@app.get("/api/practice/catalog")
def practice_catalog(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    paper = next(item for item in load_papers() if item["code"] == code)
    dataset = load_practice_data(code)
    syllabus = load_syllabus_data(code) or {}
    if not dataset:
        return {
            "paper_code": code, "paper_name": paper["name"], "content_status": "awaiting_practice_import",
            "content_origin": None, "editorial_status": None, "total_questions": 0,
            "sections": [], "difficulty_counts": {}, "question_type_counts": {},
            "official_syllabus_url": paper.get("official_syllabus_url"),
        }
    questions = dataset.get("questions", [])
    with get_connection() as conn:
        latest = conn.execute(
            """SELECT COUNT(*) AS attempted, COALESCE(SUM(is_correct), 0) AS correct
               FROM practice_attempts a JOIN (
                 SELECT question_id, MAX(id) AS latest_id FROM practice_attempts
                 WHERE user_id = ? GROUP BY question_id
               ) x ON x.latest_id = a.id WHERE a.user_id = ? AND a.question_id LIKE ?""",
            (user["id"], user["id"], f"GP-{code}-%"),
        ).fetchone()
    section_counts = {section["code"]: 0 for section in syllabus.get("sections", [])}
    difficulty_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    for question in questions:
        section_counts[question["section_code"]] = section_counts.get(question["section_code"], 0) + 1
        difficulty_counts[question["difficulty"]] = difficulty_counts.get(question["difficulty"], 0) + 1
        type_counts[question["question_type"]] = type_counts.get(question["question_type"], 0) + 1
    sections = []
    for section in syllabus.get("sections", []):
        sections.append({
            "code": section["code"], "name": section["name"], "question_count": section_counts.get(section["code"], 0),
            "topics": [{"id": topic["id"], "name": topic["name"], "question_count": sum(1 for q in questions if q["topic_id"] == topic["id"])} for topic in section.get("topics", []) if any(q["topic_id"] == topic["id"] for q in questions)],
        })
    return {
        "paper_code": code, "paper_name": paper["name"], "content_status": dataset.get("content_status"),
        "content_origin": dataset.get("content_origin"), "editorial_status": dataset.get("editorial_status"),
        "total_questions": len(questions), "attempted_questions": latest["attempted"] or 0,
        "accuracy_percent": round((latest["correct"] or 0) / latest["attempted"] * 100) if latest["attempted"] else 0,
        "sections": sections, "difficulty_counts": difficulty_counts, "question_type_counts": type_counts,
        "official_syllabus_url": dataset.get("official_syllabus_url"),
    }


@app.get("/api/practice/questions")
def list_practice_questions(
    paper_code: str | None = None, section_code: str | None = None, topic_id: str | None = None,
    difficulty: str | None = None, question_type: str | None = None,
    q: str = Query(default="", max_length=120), limit: int = Query(default=60, ge=1, le=100),
    user=Depends(require_user),
):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    dataset = load_practice_data(code)
    if not dataset:
        return {"paper_code": code, "content_status": "awaiting_practice_import", "items": [], "count": 0}
    if difficulty and difficulty not in {"Beginner", "Intermediate", "Advanced"}:
        raise HTTPException(status_code=422, detail="Invalid difficulty filter")
    if question_type and question_type.upper() not in {"MCQ", "MSQ", "NAT"}:
        raise HTTPException(status_code=422, detail="Question type must be MCQ, MSQ or NAT")
    questions = dataset.get("questions", [])
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT a.* FROM practice_attempts a JOIN (
                 SELECT question_id, MAX(id) AS latest_id FROM practice_attempts
                 WHERE user_id = ? GROUP BY question_id
               ) x ON x.latest_id = a.id WHERE a.user_id = ?""", (user["id"], user["id"])
        ).fetchall()
    attempt_map = {row["question_id"]: row for row in rows}
    items = []
    for question in questions:
        if section_code and question["section_code"] != section_code:
            continue
        if topic_id and question["topic_id"] != topic_id:
            continue
        if difficulty and question["difficulty"] != difficulty:
            continue
        if question_type and question["question_type"] != question_type.upper():
            continue
        haystack = " ".join([question["id"], question["section_name"], question["topic_name"], question["prompt"]]).casefold()
        if q and q.casefold() not in haystack:
            continue
        items.append(public_practice_question(question, attempt_map.get(question["id"])))
    return {"paper_code": code, "content_status": dataset.get("content_status"), "count": len(items), "items": items[:limit]}


@app.get("/api/practice/daily-challenge")
def get_daily_practice_challenge(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    dataset = load_practice_data(code)
    if not dataset:
        return {"paper_code": code, "content_status": "awaiting_practice_import", "questions": [], "completed": False}
    day_key = date.today().isoformat()
    questions = dataset.get("questions", [])
    ids = daily_practice_question_ids(code, day_key, questions)
    by_id = {item["id"]: item for item in questions}
    with get_connection() as conn:
        sessions = conn.execute(
            "SELECT id, status, submitted_at FROM practice_sessions WHERE user_id = ? AND paper_code = ? AND mode = 'daily' AND date(created_at, 'localtime') = ? ORDER BY created_at DESC LIMIT 1",
            (user["id"], code, day_key),
        ).fetchone()
    return {
        "paper_code": code, "date": day_key, "content_status": "original_practice_pilot",
        "question_count": len(ids), "estimated_minutes": max(5, len(ids) * 2),
        "completed": bool(sessions and sessions["status"] == "completed"),
        "session_id": sessions["id"] if sessions else None,
        "questions": [public_practice_question(by_id[item]) for item in ids if item in by_id],
        "editorial_status": dataset.get("editorial_status"),
    }


@app.post("/api/practice/sessions", status_code=201)
def create_practice_session(payload: PracticeSessionPayload, user=Depends(require_user)):
    code = (payload.paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    dataset = load_practice_data(code)
    if not dataset:
        raise HTTPException(status_code=409, detail="Practice questions have not been imported for this paper yet")
    all_questions = dataset.get("questions", [])
    if payload.mode == "daily":
        ids = daily_practice_question_ids(code, date.today().isoformat(), all_questions)
        duration_seconds = max(300, len(ids) * 120)
    else:
        if payload.mode == "topic" and not (payload.topic_id or payload.section_code):
            raise HTTPException(status_code=422, detail="Choose a subject or topic for focused practice")
        filtered = []
        for question in all_questions:
            if payload.section_code and question["section_code"] != payload.section_code:
                continue
            if payload.topic_id and question["topic_id"] != payload.topic_id:
                continue
            if payload.difficulty and question["difficulty"] != payload.difficulty:
                continue
            if payload.question_type and question["question_type"] != payload.question_type:
                continue
            filtered.append(question)
        if not filtered:
            raise HTTPException(status_code=422, detail="No practice questions match these filters")
        selected = random.SystemRandom().sample(filtered, min(payload.question_count, len(filtered)))
        ids = [question["id"] for question in selected]
        duration_seconds = payload.duration_minutes * 60
    if not ids:
        raise HTTPException(status_code=409, detail="No daily challenge questions are available")
    session_id = secrets.token_urlsafe(18)
    now = time.time()
    expires_at = now + duration_seconds
    by_id = {question["id"]: question for question in all_questions}
    selected_questions = [by_id[question_id] for question_id in ids]
    maximum_marks = sum(float(question["marks"]) for question in selected_questions)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO practice_sessions
               (id, user_id, paper_code, mode, question_ids, question_count, duration_seconds, started_at, expires_at, maximum_marks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, user["id"], code, payload.mode, json.dumps(ids), len(ids), duration_seconds, now, expires_at, maximum_marks),
        )
    return {
        "id": session_id, "paper_code": code, "mode": payload.mode, "status": "active",
        "question_count": len(ids), "duration_seconds": duration_seconds, "expires_at": expires_at,
        "questions": [public_practice_question(question) for question in selected_questions],
    }


@app.get("/api/practice/sessions/{session_id}")
def get_practice_session(session_id: str, user=Depends(require_user)):
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM practice_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Practice session not found")
        if session["status"] == "active" and time.time() >= session["expires_at"]:
            conn.execute(
                """UPDATE practice_sessions SET status = 'expired', submitted_at = CURRENT_TIMESTAMP,
                   correct_count = (SELECT COALESCE(SUM(is_correct), 0) FROM practice_attempts WHERE session_id = ? AND user_id = ?),
                   awarded_marks = (SELECT COALESCE(SUM(awarded_marks), 0) FROM practice_attempts WHERE session_id = ? AND user_id = ?)
                   WHERE id = ? AND user_id = ?""",
                (session_id, user["id"], session_id, user["id"], session_id, user["id"]),
            )
            session = conn.execute("SELECT * FROM practice_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        attempts = conn.execute("SELECT * FROM practice_attempts WHERE session_id = ? AND user_id = ?", (session_id, user["id"])).fetchall()
    attempt_map = {row["question_id"]: row for row in attempts}
    questions = []
    for question_id in json.loads(session["question_ids"]):
        question = find_practice_question(question_id, session["paper_code"])
        if question:
            item = public_practice_question(question, attempt_map.get(question_id))
            if question_id in attempt_map:
                item["result"] = {
                    "is_correct": bool(attempt_map[question_id]["is_correct"]),
                    "awarded_marks": attempt_map[question_id]["awarded_marks"],
                    "correct_answer": question["answer_key"],
                    "solution": question["solution"],
                }
            questions.append(item)
    return {
        "id": session["id"], "paper_code": session["paper_code"], "mode": session["mode"],
        "status": session["status"], "question_count": session["question_count"],
        "duration_seconds": session["duration_seconds"], "expires_at": session["expires_at"],
        "remaining_seconds": max(0, int(session["expires_at"] - time.time())) if session["status"] == "active" else 0,
        "answered_count": len(attempts), "questions": questions,
        "result": {"correct_count": session["correct_count"], "attempted_count": len(attempts), "awarded_marks": session["awarded_marks"], "maximum_marks": session["maximum_marks"], "accuracy_percent": round(session["correct_count"] / len(attempts) * 100) if attempts else 0} if session["status"] != "active" else None,
    }


@app.post("/api/practice/sessions/{session_id}/attempt")
def submit_practice_answer(session_id: str, payload: PracticeAttemptPayload, user=Depends(require_user)):
    expired = False
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM practice_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Practice session not found")
        if session["status"] != "active":
            raise HTTPException(status_code=409, detail="This practice session is no longer active")
        if time.time() >= session["expires_at"]:
            conn.execute("UPDATE practice_sessions SET status = 'expired', submitted_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
            expired = True
        if expired:
            question_ids = []
        else:
            question_ids = json.loads(session["question_ids"])
        if not expired:
            if payload.question_id not in question_ids:
                raise HTTPException(status_code=404, detail="Question is not part of this practice session")
            existing = conn.execute("SELECT id FROM practice_attempts WHERE session_id = ? AND question_id = ?", (session_id, payload.question_id)).fetchone()
            if existing:
                raise HTTPException(status_code=409, detail="This question has already been submitted in this session")
            question = find_practice_question(payload.question_id, session["paper_code"])
            if not question:
                raise HTTPException(status_code=404, detail="Practice question not found")
            submitted = normalise_practice_answer(question["question_type"], payload.answer)
            correct, awarded, expected = check_practice_answer(question, submitted)
            conn.execute(
                """INSERT INTO practice_attempts
                   (session_id, user_id, question_id, submitted_answer, is_correct, awarded_marks, spent_seconds)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, user["id"], payload.question_id, submitted, int(correct), awarded, payload.spent_seconds),
            )
    if expired:
        raise HTTPException(status_code=410, detail="Practice time has expired")
    return {
        "question_id": payload.question_id, "submitted_answer": submitted,
        "is_correct": correct, "awarded_marks": awarded, "maximum_marks": question["marks"],
        "correct_answer": expected, "question_type": question["question_type"],
        "scoring_note": (
            "Incorrect MCQ: one-third of the question marks deducted." if question["question_type"] == "MCQ" else
            "MSQ requires the exact correct option set; no partial or negative marking." if question["question_type"] == "MSQ" else
            "NAT is checked against the inclusive accepted range; no negative marking."
        ),
        "answer_range": question.get("answer_range"), "solution": question["solution"],
        "content_origin": "GATEPath original practice question; not an official GATE question or PYQ.",
    }


@app.post("/api/practice/sessions/{session_id}/finish")
def finish_practice_session(session_id: str, user=Depends(require_user)):
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM practice_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Practice session not found")
        if session["status"] == "active":
            status = "expired" if time.time() >= session["expires_at"] else "completed"
            conn.execute(
                """UPDATE practice_sessions SET status = ?, submitted_at = CURRENT_TIMESTAMP,
                   correct_count = (SELECT COALESCE(SUM(is_correct), 0) FROM practice_attempts WHERE session_id = ? AND user_id = ?),
                   awarded_marks = (SELECT COALESCE(SUM(awarded_marks), 0) FROM practice_attempts WHERE session_id = ? AND user_id = ?)
                   WHERE id = ? AND user_id = ?""",
                (status, session_id, user["id"], session_id, user["id"], session_id, user["id"]),
            )
        updated = conn.execute("SELECT * FROM practice_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        attempts = conn.execute("SELECT COUNT(*) AS count, COALESCE(SUM(is_correct), 0) AS correct FROM practice_attempts WHERE session_id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
    return {
        "id": updated["id"], "status": updated["status"], "mode": updated["mode"],
        "paper_code": updated["paper_code"], "question_count": updated["question_count"],
        "attempted_count": attempts["count"], "correct_count": attempts["correct"],
        "awarded_marks": round(float(updated["awarded_marks"]), 6),
        "maximum_marks": round(float(updated["maximum_marks"]), 6),
        "accuracy_percent": round(attempts["correct"] / attempts["count"] * 100) if attempts["count"] else 0,
    }


@app.get("/api/practice/summary")
def practice_summary(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    with get_connection() as conn:
        attempt_rows = conn.execute(
            """SELECT a.* FROM practice_attempts a JOIN practice_sessions s ON s.id = a.session_id
               WHERE a.user_id = ? AND s.paper_code = ? ORDER BY a.id DESC""", (user["id"], code)
        ).fetchall()
        session_rows = conn.execute(
            "SELECT * FROM practice_sessions WHERE user_id = ? AND paper_code = ? ORDER BY created_at DESC LIMIT 10",
            (user["id"], code),
        ).fetchall()
        session_counts = conn.execute(
            """SELECT COUNT(*) AS total,
                      COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) AS completed
               FROM practice_sessions WHERE user_id = ? AND paper_code = ?""",
            (user["id"], code),
        ).fetchone()
    latest_by_question: dict[str, object] = {}
    for row in attempt_rows:
        latest_by_question.setdefault(row["question_id"], row)
    topic_stats: dict[str, dict] = {}
    mistakes = []
    for question_id, row in latest_by_question.items():
        question = find_practice_question(question_id, code)
        if not question:
            continue
        topic_id = question["topic_id"]
        bucket = topic_stats.setdefault(topic_id, {"topic_id": topic_id, "topic_name": question["topic_name"], "attempted": 0, "correct": 0})
        bucket["attempted"] += 1
        bucket["correct"] += int(row["is_correct"])
        if not row["is_correct"]:
            mistakes.append({"question_id": question_id, "topic_id": topic_id, "topic_name": question["topic_name"], "section_name": question["section_name"], "difficulty": question["difficulty"], "prompt": question["prompt"], "submitted_answer": row["submitted_answer"], "correct_answer": question["answer_key"]})
    for item in topic_stats.values():
        item["accuracy_percent"] = round(item["correct"] / item["attempted"] * 100) if item["attempted"] else 0
    ordered_topics = sorted(topic_stats.values(), key=lambda item: (item["accuracy_percent"], -item["attempted"]))
    return {
        "paper_code": code, "attempted_questions": len(latest_by_question), "attempt_count": len(attempt_rows),
        "correct_questions_latest": sum(row["is_correct"] for row in latest_by_question.values()),
        "accuracy_percent": round(sum(row["is_correct"] for row in latest_by_question.values()) / len(latest_by_question) * 100) if latest_by_question else 0,
        "sessions_completed": session_counts["completed"] or 0,
        "sessions_total": session_counts["total"] or 0, "weak_topics": ordered_topics[:5],
        "recent_mistakes": mistakes[:10],
        "recent_sessions": [{"id": row["id"], "mode": row["mode"], "status": row["status"], "question_count": row["question_count"], "correct_count": row["correct_count"], "awarded_marks": round(float(row["awarded_marks"]), 3), "maximum_marks": round(float(row["maximum_marks"]), 3), "created_at": row["created_at"]} for row in session_rows],
    }



# ---------------------------- Full mock tests -----------------------------

def mock_pattern_for_paper(code: str) -> dict:
    pattern = load_mock_pattern()
    common = dict(pattern.get("common", {}))
    classes = pattern.get("paper_classes", {})
    if code in classes.get("engineering_mathematics_13", []):
        class_name = "engineering_mathematics_13"
        math_marks = 13
        subject_marks = 72
    elif code in classes.get("subject_85_no_engineering_mathematics_13", []):
        class_name = "subject_85_no_engineering_mathematics_13"
        math_marks = 0
        subject_marks = 85
    else:
        class_name = "special_section_structure"
        math_marks = None
        subject_marks = 85
    return {
        "paper_code": code, "paper_class": class_name,
        "common": common, "engineering_mathematics_marks": math_marks,
        "subject_marks": subject_marks,
        "special_structure": classes.get("special_section_structure", {}).get(code),
        "source_url": pattern.get("source_url"), "verified_on": pattern.get("verified_on"),
    }

@app.get("/api/mock-tests/pattern")
def get_mock_test_pattern(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    return mock_pattern_for_paper(code)

@app.get("/api/mock-tests/catalog")
def get_mock_test_catalog(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    paper = next(item for item in load_papers() if item["code"] == code)
    pattern = mock_pattern_for_paper(code)
    tests = []
    for path in sorted(MOCKS_DIR.glob(f"{code}-FULL-MOCK-*.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        valid, message = mock_manifest_is_valid(manifest)
        blueprint = manifest.get("blueprint", {})
        tests.append({
            "test_id": manifest.get("test_id"), "title": manifest.get("title"),
            "subtitle": manifest.get("subtitle"), "mode": manifest.get("mode", "full_length"),
            "question_count": len(manifest.get("questions", [])),
            "duration_minutes": blueprint.get("duration_minutes"),
            "total_marks": blueprint.get("total_marks"),
            "section_summary": manifest.get("section_summary", []),
            "content_status": manifest.get("content_status"),
            "content_origin": manifest.get("content_origin"),
            "editorial_status": manifest.get("editorial_status"),
            "available": valid, "availability_note": message,
        })
    with get_connection() as conn:
        recent = conn.execute(
            "SELECT id, test_id, paper_code, status, score, maximum_marks, attempted_count, correct_count, wrong_count, created_at FROM mock_test_sessions WHERE user_id = ? AND paper_code = ? ORDER BY created_at DESC LIMIT 8",
            (user["id"], code),
        ).fetchall()
    return {
        "paper_code": code, "paper_name": paper["name"], "pattern": pattern,
        "official_pattern_url": pattern.get("source_url"),
        "content_status": "available" if tests else "awaiting_mock_import",
        "tests": tests, "recent_attempts": [dict(row) for row in recent],
    }

@app.post("/api/mock-tests/sessions", status_code=201)
def create_mock_test_session(payload: MockSessionCreatePayload, user=Depends(require_user)):
    code = (payload.paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    manifest = load_mock_manifest(code, payload.test_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="This mock test has not been imported for the selected paper")
    valid, message = mock_manifest_is_valid(manifest)
    if not valid:
        raise HTTPException(status_code=409, detail=f"Mock test is not ready: {message}")
    blueprint = manifest["blueprint"]
    question_ids = [question["id"] for question in manifest["questions"]]
    duration_seconds = int(blueprint["duration_minutes"]) * 60
    maximum_marks = float(blueprint["total_marks"])
    session_id = secrets.token_urlsafe(24)
    now = time.time()
    expires_at = now + duration_seconds

    # Expire any abandoned full mock before enforcing the one-active-session rule.
    # Otherwise an expired paper that was never reopened could block a new attempt.
    with get_connection() as conn:
        abandoned = conn.execute(
            "SELECT id, expires_at FROM mock_test_sessions WHERE user_id = ? AND status = 'active'",
            (user["id"],),
        ).fetchall()
    for old_session in abandoned:
        if now >= float(old_session["expires_at"]):
            finalize_mock_session(old_session["id"], user["id"], "expired")

    try:
        with get_connection() as conn:
            active = conn.execute(
                "SELECT id FROM mock_test_sessions WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
                (user["id"],),
            ).fetchone()
            if active:
                raise HTTPException(status_code=409, detail="You already have an active mock test. Resume or submit it before starting another.")
            conn.execute(
                "INSERT INTO mock_test_sessions (id, user_id, test_id, paper_code, question_ids, duration_seconds, started_at, expires_at, maximum_marks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, user["id"], payload.test_id, code, json.dumps(question_ids), duration_seconds, now, expires_at, maximum_marks),
            )
            conn.executemany(
                "INSERT INTO mock_test_responses (session_id, user_id, question_id) VALUES (?, ?, ?)",
                [(session_id, user["id"], question_id) for question_id in question_ids],
            )
            session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ?", (session_id,)).fetchone()
            responses = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ?", (session_id, user["id"])).fetchall()
    except sqlite3.IntegrityError as exc:
        # The partial unique index protects against two simultaneous starts.
        raise HTTPException(status_code=409, detail="A mock test was started in another window. Resume that attempt before starting another.") from exc
    return mock_session_payload(dict(session), manifest, responses)

@app.get("/api/mock-tests/sessions/{session_id}")
def get_mock_test_session(session_id: str, user=Depends(require_user)):
    expired = False
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Mock-test session not found")
        expired = session["status"] == "active" and time.time() >= float(session["expires_at"])
    if expired:
        finalize_mock_session(session_id, user["id"], "expired")
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        manifest = load_mock_manifest(session["paper_code"], session["test_id"]) if session else None
        responses = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ? ORDER BY id", (session_id, user["id"])).fetchall()
    if not session:
        raise HTTPException(status_code=404, detail="Mock-test session not found")
    if not manifest:
        raise HTTPException(status_code=500, detail="Mock-test manifest is unavailable")
    return mock_session_payload(dict(session), manifest, responses)

@app.patch("/api/mock-tests/sessions/{session_id}/responses/{question_id}")
def save_mock_test_response(session_id: str, question_id: str, payload: MockResponsePayload, user=Depends(require_user)):
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM mock_test_sessions WHERE id = ? AND user_id = ?", (session_id, user["id"])).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Mock-test session not found")
        if session["status"] != "active":
            raise HTTPException(status_code=409, detail="This mock test is no longer active")
        if time.time() >= float(session["expires_at"]):
            expired = True
        else:
            expired = False
        if expired:
            # Finalise after leaving this connection to avoid nested writes.
            pass
        else:
            question_ids = json.loads(session["question_ids"])
            if question_id not in question_ids:
                raise HTTPException(status_code=404, detail="Question is not part of this mock test")
            manifest = load_mock_manifest(session["paper_code"], session["test_id"])
            question = next((item for item in manifest["questions"] if item["id"] == question_id), None) if manifest else None
            if not question:
                raise HTTPException(status_code=404, detail="Mock question not found")
            existing = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ? AND question_id = ?", (session_id, user["id"], question_id)).fetchone()
            answer = existing["answer"] if existing else ""
            marked = bool(existing["marked_for_review"]) if existing else False
            visited = bool(existing["visited"]) if existing else False
            if "answer" in payload.model_fields_set:
                raw = payload.answer or ""
                answer = normalise_practice_answer(question["question_type"], raw) if raw else ""
            if payload.marked_for_review is not None:
                marked = payload.marked_for_review
            if payload.visited is not None:
                visited = payload.visited
            spent = (int(existing["spent_seconds"]) if existing else 0) + payload.spent_seconds
            conn.execute(
                "UPDATE mock_test_responses SET answer = ?, marked_for_review = ?, visited = ?, spent_seconds = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ? AND user_id = ? AND question_id = ?",
                (answer, int(marked), int(visited), spent, session_id, user["id"], question_id),
            )
            row = conn.execute("SELECT * FROM mock_test_responses WHERE session_id = ? AND user_id = ? AND question_id = ?", (session_id, user["id"], question_id)).fetchone()
    if expired:
        finalize_mock_session(session_id, user["id"], "expired")
        raise HTTPException(status_code=410, detail="Mock-test time has expired and the paper was auto-submitted")
    return {
        "question_id": question_id,
        "response": {"answer": row["answer"], "marked_for_review": bool(row["marked_for_review"]), "visited": bool(row["visited"]), "spent_seconds": int(row["spent_seconds"])},
        "saved": True,
    }

@app.post("/api/mock-tests/sessions/{session_id}/submit")
def submit_mock_test_session(session_id: str, user=Depends(require_user)):
    return finalize_mock_session(session_id, user["id"], "submitted")

@app.get("/api/mock-tests/history")
def get_mock_test_history(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, test_id, paper_code, status, score, maximum_marks, attempted_count, correct_count, wrong_count, created_at, submitted_at FROM mock_test_sessions WHERE user_id = ? AND paper_code = ? ORDER BY created_at DESC LIMIT 20",
            (user["id"], code),
        ).fetchall()
    return {"paper_code": code, "items": [dict(row) for row in rows]}


# ------------------------------- Auth API ----------------------------------

# ------------------------------ Mind maps ---------------------------------

@app.get("/api/mindmaps")
def get_mindmap(
    paper_code: str | None = None, section_code: str | None = None,
    user=Depends(require_user),
):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    paper = next(item for item in load_papers() if item["code"] == code)
    syllabus = load_syllabus_data(code)
    if not syllabus:
        return {"paper_code": code, "paper_name": paper["name"], "content_status": "awaiting_structured_import", "nodes": [], "edges": [], "relationships": [], "summary": {"topics": 0, "subtopics": 0}, "official_syllabus_url": paper.get("official_syllabus_url")}
    sections = syllabus.get("sections", [])
    if not sections:
        return {"paper_code": code, "paper_name": paper["name"], "content_status": "awaiting_structured_import", "nodes": [], "edges": [], "relationships": [], "summary": {"topics": 0, "subtopics": 0}, "official_syllabus_url": syllabus.get("source_url")}
    active = next((section for section in sections if section["code"] == section_code), sections[0]) if section_code else sections[0]
    if section_code and not any(section["code"] == section_code for section in sections):
        raise HTTPException(status_code=404, detail="Syllabus section not found")
    topic_lookup = {topic["id"]: (section, topic) for section in sections for topic in section.get("topics", [])}
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT topic_id, status, bookmarked FROM student_material_progress WHERE user_id = ? AND paper_code = ?",
            (user["id"], code),
        ).fetchall()
    progress = {row["topic_id"]: {"status": row["status"], "bookmarked": bool(row["bookmarked"])} for row in rows}
    topics = active.get("topics", [])
    nodes = [{"id": f"{active['code']}:root", "type": "root", "label": active["name"], "section_code": active["code"]}]
    edges = []
    relationships = []
    subtopic_total = 0
    for topic in topics:
        status = progress.get(topic["id"], {"status": "not_started", "bookmarked": False})
        material_data = load_materials_data(code) or {}
        note_available = any(item.get("id") == topic["id"] for item in material_data.get("materials", []))
        nodes.append({"id": topic["id"], "type": "topic", "topic_id": topic["id"], "label": topic["name"], "parent_id": f"{active['code']}:root", "note_available": note_available, **status})
        edges.append({"id": f"{active['code']}:root->{topic['id']}", "source": f"{active['code']}:root", "target": topic["id"], "type": "hierarchy"})
        for index, subtopic in enumerate(topic.get("subtopics", []), 1):
            node_id = f"{topic['id']}:sub:{index}"
            nodes.append({"id": node_id, "type": "subtopic", "label": subtopic, "parent_id": topic["id"], "topic_id": topic["id"]})
            edges.append({"id": f"{topic['id']}->{node_id}", "source": topic["id"], "target": node_id, "type": "hierarchy"})
            subtopic_total += 1
        for prerequisite_id in topic.get("prerequisites", []):
            prerequisite = topic_lookup.get(prerequisite_id)
            if not prerequisite:
                continue
            prerequisite_section, prerequisite_topic = prerequisite
            relationship = {"topic_id": topic["id"], "topic_name": topic["name"], "prerequisite_id": prerequisite_id, "prerequisite_name": prerequisite_topic["name"], "section_code": prerequisite_section["code"], "available_in_map": prerequisite_section["code"] == active["code"]}
            relationships.append(relationship)
            if relationship["available_in_map"]:
                edges.append({"id": f"{prerequisite_id}->{topic['id']}:prerequisite", "source": prerequisite_id, "target": topic["id"], "type": "prerequisite"})
    return {
        "paper_code": code, "paper_name": paper["name"], "syllabus_version": syllabus.get("syllabus_version", "GATE 2027"),
        "content_status": syllabus.get("content_status", "imported_verified"), "active_section": {"code": active["code"], "name": active["name"], "order": active.get("order")},
        "sections": [{"code": section["code"], "name": section["name"], "order": section.get("order")} for section in sections],
        "nodes": nodes, "edges": edges, "relationships": relationships,
        "summary": {"topics": len(topics), "subtopics": subtopic_total},
        "official_syllabus_url": syllabus.get("source_url") or paper.get("official_syllabus_url"),
    }


# ------------------------------ PYQ bank ----------------------------------

@app.get("/api/pyq/catalog")
def pyq_catalog(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    catalog = load_pyq_catalog(code)
    dataset = load_pyq_data(code, 2026)
    sessions = []
    if dataset:
        sessions = [{"session": item["session"], "question_count": item["question_count"], "paper_url": item["paper_url"], "answer_key_url": item["answer_key_url"]} for item in dataset.get("sessions", [])]
    return {
        "paper_code": code, "paper_name": next(item["name"] for item in load_papers() if item["code"] == code),
        "content_status": "interactive_metadata_imported" if dataset else "official_archive_links_only",
        "interactive_years": [2026] if dataset else [], "interactive_question_count": sum(x["question_count"] for x in sessions),
        "sessions": sessions, "archive_sources": catalog.get("archive_sources", []), "notes": catalog.get("notes", []),
    }


@app.get("/api/pyq/questions")
def list_pyq_questions(
    paper_code: str | None = None, year: int = 2026, session: str | None = None,
    question_type: str | None = None, section_code: str | None = None, topic_id: str | None = None,
    q: str = Query(default="", max_length=100), bookmarked_only: bool = False,
    user=Depends(require_user),
):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    dataset = load_pyq_data(code, year)
    if not dataset:
        return {"paper_code": code, "year": year, "content_status": "awaiting_interactive_import", "notice": "Use the linked official archive. Question-level metadata has not yet been imported for this paper and year.", "items": [], "count": 0}
    if question_type and question_type.upper() not in {"MCQ", "MSQ", "NAT"}:
        raise HTTPException(status_code=422, detail="Question type must be MCQ, MSQ or NAT")
    all_questions = [question for group in dataset.get("sessions", []) for question in group.get("questions", [])]
    with get_connection() as conn:
        bookmarks = {row["question_id"] for row in conn.execute("SELECT question_id FROM pyq_bookmarks WHERE user_id = ?", (user["id"],)).fetchall()}
        attempts = conn.execute(
            """SELECT a.* FROM pyq_attempts a JOIN (
                 SELECT question_id, MAX(id) AS latest_id FROM pyq_attempts WHERE user_id = ? GROUP BY question_id
               ) latest ON latest.latest_id = a.id WHERE a.user_id = ?""", (user["id"], user["id"])
        ).fetchall()
    last_map = {row["question_id"]: pyq_last_attempt(row) for row in attempts}
    items = []
    for question in all_questions:
        if session and question["session"] != session:
            continue
        if question_type and question["question_type"] != question_type.upper():
            continue
        if section_code == "CS" and question["source_section_code"] == "GA":
            continue
        if section_code and section_code != "CS" and question["source_section_code"] != section_code:
            continue
        if topic_id and question.get("topic_id") != topic_id:
            continue
        if bookmarked_only and question["id"] not in bookmarks:
            continue
        haystack = " ".join(str(question.get(key) or "") for key in ("id", "session", "question_number", "question_type", "section_name", "topic_name", "editorial_label"))
        if q and q.casefold() not in haystack.casefold():
            continue
        items.append(pyq_public_item(question, question["id"] in bookmarks, last_map.get(question["id"])))
    items.sort(key=lambda item: (item["session"], item["question_number"]))
    return {"paper_code": code, "year": year, "content_status": dataset.get("content_status"), "count": len(items), "items": items}


@app.get("/api/pyq/questions/{question_id}")
def get_pyq_question(question_id: str, user=Depends(require_user)):
    question = find_pyq_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in the imported PYQ catalogue")
    with get_connection() as conn:
        bookmark = conn.execute("SELECT 1 FROM pyq_bookmarks WHERE user_id = ? AND question_id = ?", (user["id"], question_id)).fetchone() is not None
        last = conn.execute("SELECT * FROM pyq_attempts WHERE user_id = ? AND question_id = ? ORDER BY id DESC LIMIT 1", (user["id"], question_id)).fetchone()
    payload = pyq_public_item(question, bookmark, pyq_last_attempt(last))
    payload["question_text_hosted"] = False
    payload["question_text_notice"] = "Open the official master question paper PDF for the question wording and figures. GATEPath stores the verified answer-key metadata and original explanation notes, not a copied question statement."
    payload["solution"] = question.get("solution") if last else None
    if last:
        payload["verified_answer"] = question.get("answer_key")
        payload["answer_range"] = question.get("answer_range")
    return payload


@app.post("/api/pyq/questions/{question_id}/attempt")
def submit_pyq_attempt(question_id: str, payload: PyqAttemptPayload, user=Depends(require_user)):
    question = find_pyq_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in the imported PYQ catalogue")
    submitted = normalise_pyq_answer(question["question_type"], payload.answer)
    correct, awarded, expected = check_pyq_answer(question, submitted)
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO pyq_attempts (user_id, question_id, submitted_answer, is_correct, awarded_marks, spent_seconds)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user["id"], question_id, submitted, int(correct), awarded, payload.spent_seconds),
        )
        attempt_id = cursor.lastrowid
    return {
        "attempt_id": attempt_id, "question_id": question_id, "submitted_answer": submitted,
        "is_correct": correct, "awarded_marks": awarded, "maximum_marks": question["marks"],
        "correct_answer": expected, "answer_range": question.get("answer_range"),
        "question_type": question["question_type"], "scoring_note": (
            "Incorrect MCQ: one-third of the question marks deducted." if question["question_type"] == "MCQ" else
            "MSQ: all correct options are required; no partial marking or negative marking." if question["question_type"] == "MSQ" else
            "NAT: accepted when the numerical response falls within the official answer-key range; no negative marking."
        ),
        "solution": question.get("solution"),
        "solution_status": "editorial_explanation_available" if question.get("solution") else "editorial_explanation_pending",
        "paper_url": question["paper_url"], "answer_key_url": question["answer_key_url"],
    }


@app.put("/api/pyq/bookmarks/{question_id}")
def update_pyq_bookmark(question_id: str, payload: PyqBookmarkPayload, user=Depends(require_user)):
    if not find_pyq_question(question_id):
        raise HTTPException(status_code=404, detail="Question not found in the imported PYQ catalogue")
    with get_connection() as conn:
        if payload.bookmarked:
            conn.execute("INSERT OR IGNORE INTO pyq_bookmarks (user_id, question_id) VALUES (?, ?)", (user["id"], question_id))
        else:
            conn.execute("DELETE FROM pyq_bookmarks WHERE user_id = ? AND question_id = ?", (user["id"], question_id))
    return {"question_id": question_id, "bookmarked": payload.bookmarked}


@app.get("/api/pyq/history")
def pyq_history(limit: int = Query(default=20, ge=1, le=100), user=Depends(require_user)):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM pyq_attempts WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user["id"], limit)).fetchall()
        bookmarks = {row["question_id"] for row in conn.execute("SELECT question_id FROM pyq_bookmarks WHERE user_id = ?", (user["id"],)).fetchall()}
    items = []
    for row in rows:
        question = find_pyq_question(row["question_id"])
        if not question:
            continue
        item = pyq_public_item(question, bookmarked=row["question_id"] in bookmarks, last_attempt=pyq_last_attempt(row))
        item["verified_answer"] = question.get("answer_key")
        item["solution"] = question.get("solution")
        items.append(item)
    return {"items": items, "count": len(items)}


@app.get("/api/pyq/summary")
def pyq_summary(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    dataset = load_pyq_data(code, 2026)
    total = sum(len(session.get("questions", [])) for session in dataset.get("sessions", [])) if dataset else 0
    question_prefix = f"G26-{code}-%"
    with get_connection() as conn:
        aggregate = conn.execute(
            """SELECT COUNT(*) AS attempts, COALESCE(SUM(awarded_marks), 0) AS marks
               FROM pyq_attempts WHERE user_id = ? AND question_id LIKE ?""", (user["id"], question_prefix)
        ).fetchone()
        latest = conn.execute(
            """SELECT COUNT(*) AS attempted, COALESCE(SUM(is_correct), 0) AS correct
               FROM pyq_attempts a JOIN (
                 SELECT question_id, MAX(id) AS latest_id FROM pyq_attempts
                 WHERE user_id = ? AND question_id LIKE ? GROUP BY question_id
               ) latest ON latest.latest_id = a.id""", (user["id"], question_prefix)
        ).fetchone()
        bookmarks = conn.execute("SELECT COUNT(*) AS count FROM pyq_bookmarks WHERE user_id = ? AND question_id LIKE ?", (user["id"], question_prefix)).fetchone()["count"]
    attempted = latest["attempted"] or 0
    correct = latest["correct"] or 0
    return {"paper_code": code, "year": 2026, "total_questions": total, "attempted_questions": attempted, "attempt_count": aggregate["attempts"] or 0, "correct_questions_latest": correct, "bookmarked_questions": bookmarks, "accuracy_percent": round(correct / attempted * 100) if attempted else 0, "marks_earned_total": round(float(aggregate["marks"] or 0), 3)}


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterPayload, request: Request, response: Response):
    if payload.paper_code.upper() not in paper_codes():
        raise HTTPException(status_code=400, detail="Select a valid GATE paper")
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (payload.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        cursor = conn.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (payload.full_name, payload.email, password_hash(payload.password)),
        )
        user_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO user_profiles (user_id, paper_code, target, daily_hours) VALUES (?, ?, ?, ?)",
            (user_id, payload.paper_code.upper(), payload.target, payload.daily_hours),
        )
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    raw_token = create_session(user_id, request)
    set_session_cookie(response, request, raw_token)
    return {"message": "Your GATEPath account is ready", "user": public_user(user)}


@app.post("/api/auth/login")
def login(payload: LoginPayload, request: Request, response: Response):
    ip_address = request.client.host if request.client else "unknown"
    now = time.time()
    locked_until = 0.0
    valid = False
    user = None
    with get_connection() as conn:
        attempt = conn.execute(
            "SELECT * FROM auth_login_attempts WHERE email = ? AND ip_address = ?",
            (payload.email, ip_address),
        ).fetchone()
        if attempt and attempt["locked_until"] > now:
            locked_until = attempt["locked_until"]
        else:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (payload.email,)).fetchone()
            # Run PBKDF2 for both known and unknown emails to reduce timing-based email discovery.
            password_matches = verify_password(payload.password, user["password_hash"] if user else DUMMY_PASSWORD_HASH)
            valid = bool(user and user["is_active"] and password_matches)
            if not valid:
                if not attempt or now - attempt["window_started"] > 15 * 60:
                    attempts = 1
                    window_started = now
                else:
                    attempts = attempt["attempts"] + 1
                    window_started = attempt["window_started"]
                locked_until = now + 15 * 60 if attempts >= 5 else 0.0
                conn.execute(
                    """INSERT INTO auth_login_attempts (email, ip_address, attempts, window_started, locked_until)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(email, ip_address) DO UPDATE SET attempts = excluded.attempts,
                         window_started = excluded.window_started, locked_until = excluded.locked_until""",
                    (payload.email, ip_address, attempts, window_started, locked_until),
                )
            else:
                conn.execute("DELETE FROM auth_login_attempts WHERE email = ? AND ip_address = ?", (payload.email, ip_address))
    if locked_until > now:
        retry_after = max(1, int(locked_until - now))
        raise HTTPException(status_code=429, detail=f"Too many sign-in attempts. Try again in about {max(1, retry_after // 60)} minute(s).")
    if not valid:
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    raw_token = create_session(user["id"], request)
    set_session_cookie(response, request, raw_token)
    return {"message": "You are signed in", "user": public_user(user)}


@app.post("/api/auth/logout")
def logout(
    response: Response,
    gatepath_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    if gatepath_session:
        with get_connection() as conn:
            conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (token_hash(gatepath_session),))
    clear_session_cookie(response)
    return {"message": "You have been signed out"}


@app.get("/api/auth/me")
def who_am_i(user=Depends(require_user)):
    return {
        "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "role": user["role"], "created_at": user["created_at"]},
        "profile": {"paper_code": user["paper_code"], "target": user["target"], "daily_hours": user["daily_hours"], "updated_at": user["profile_updated_at"]},
    }


@app.post("/api/auth/request-password-reset")
def request_password_reset(payload: PasswordResetRequest):
    # Do not reveal whether the supplied email is registered. A real reset flow
    # requires SMTP configuration; the UI reports this explicitly when absent.
    if not smtp_is_configured():
        raise HTTPException(status_code=503, detail="Password recovery email is not configured yet. Please contact the site administrator.")
    with get_connection() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ? AND is_active = 1", (payload.email,)).fetchone()
        if user:
            raw_token = secrets.token_urlsafe(36)
            conn.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (user["id"],))
            conn.execute(
                "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
                (user["id"], token_hash(raw_token), time.time() + 30 * 60),
            )
    if user:
        try:
            send_password_reset_email(payload.email, raw_token)
        except Exception as exc:  # no SMTP secrets or token are returned to the client
            with get_connection() as conn:
                conn.execute("DELETE FROM password_reset_tokens WHERE token_hash = ?", (token_hash(raw_token),))
            raise HTTPException(status_code=503, detail="The reset email could not be sent. Please try again later.") from exc
    return {"message": "If an active account exists for this email, password reset instructions have been sent."}


@app.post("/api/auth/reset-password")
def reset_password(payload: PasswordResetPayload, response: Response):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, user_id FROM password_reset_tokens WHERE token_hash = ? AND expires_at > ? AND used_at IS NULL",
            (token_hash(payload.token), time.time()),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="This password reset link is invalid or has expired")
        conn.execute("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (password_hash(payload.new_password), row["user_id"]))
        conn.execute("UPDATE password_reset_tokens SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))
        conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (row["user_id"],))
    clear_session_cookie(response)
    return {"message": "Your password has been updated. Please sign in again."}


# ------------------------- Authenticated student API ----------------------

@app.get("/api/profile")
def get_profile(user=Depends(require_user)):
    return {"paper_code": user["paper_code"], "target": user["target"], "daily_hours": user["daily_hours"], "updated_at": user["profile_updated_at"]}


@app.put("/api/profile")
def update_profile(payload: ProfileUpdate, user=Depends(require_user)):
    code = payload.paper_code.upper()
    if code not in paper_codes():
        raise HTTPException(status_code=400, detail="Unknown GATE paper code")
    with get_connection() as conn:
        conn.execute(
            """UPDATE user_profiles SET paper_code = ?, target = ?, daily_hours = ?, updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (code, payload.target, payload.daily_hours, user["id"]),
        )
        row = conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user["id"],)).fetchone()
    return profile_dict(row)


@app.get("/api/tasks")
def list_tasks(user=Depends(require_user), on_date: date | None = Query(default=None, alias="date")):
    chosen_date = on_date or date.today()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM user_tasks WHERE user_id = ? AND due_date = ?
               ORDER BY completed ASC, CASE priority WHEN 'High' THEN 0 WHEN 'Normal' THEN 1 ELSE 2 END, id ASC""",
            (user["id"], chosen_date.isoformat()),
        ).fetchall()
    return {"items": [task_to_dict(row) for row in rows], "date": chosen_date.isoformat()}


@app.post("/api/tasks", status_code=201)
def create_task(payload: TaskCreate, user=Depends(require_user)):
    due = payload.due_date or date.today()
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO user_tasks (user_id, title, subject, due_date, duration_minutes, priority)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user["id"], payload.title.strip(), payload.subject.strip() or "General", due.isoformat(), payload.duration_minutes, payload.priority),
        )
        row = conn.execute("SELECT * FROM user_tasks WHERE id = ? AND user_id = ?", (cursor.lastrowid, user["id"])).fetchone()
    return task_to_dict(row)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, user=Depends(require_user)):
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=400, detail="No update fields supplied")
    if "completed" in values and values["completed"] is not None:
        values["completed"] = int(values["completed"])
    if "subject" in values and values["subject"] is not None:
        values["subject"] = values["subject"].strip() or "General"
    if "title" in values and values["title"] is not None:
        values["title"] = values["title"].strip()
    allowed = {"completed", "title", "subject", "duration_minutes", "priority"}
    if set(values) - allowed:
        raise HTTPException(status_code=400, detail="Unsupported task field")
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM user_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Task not found")
        assignments = ", ".join(f"{key} = ?" for key in values)
        conn.execute(f"UPDATE user_tasks SET {assignments} WHERE id = ? AND user_id = ?", (*values.values(), task_id, user["id"]))
        row = conn.execute("SELECT * FROM user_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])).fetchone()
    return task_to_dict(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user=Depends(require_user)):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM user_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"]))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return None


@app.get("/api/dashboard")
def dashboard(user=Depends(require_user)):
    today = date.today().isoformat()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM user_tasks WHERE user_id = ? AND due_date = ? ORDER BY completed ASC, id ASC", (user["id"], today)).fetchall()
        all_count = conn.execute("SELECT COUNT(*) AS count FROM user_tasks WHERE user_id = ?", (user["id"],)).fetchone()["count"]
        completed_count = conn.execute("SELECT COUNT(*) AS count FROM user_tasks WHERE user_id = ? AND completed = 1", (user["id"],)).fetchone()["count"]
        material_completed = conn.execute("SELECT COUNT(*) AS count FROM student_material_progress WHERE user_id = ? AND paper_code = ? AND status = 'completed'", (user["id"], user["paper_code"])).fetchone()["count"]
    syllabus_data = load_syllabus_data(user["paper_code"])
    material_data = load_materials_data(user["paper_code"])
    syllabus_total = len(material_data.get("materials", [])) if material_data else sum(len(section.get("topics", [])) for section in (syllabus_data or {}).get("sections", []))
    syllabus_percent = round(material_completed / syllabus_total * 100) if syllabus_total else 0
    exam_day = date(2027, 2, 6)
    days_left = max((exam_day - date.today()).days, 0)
    tasks = [task_to_dict(row) for row in rows]
    return {
        "profile": {"paper_code": user["paper_code"], "target": user["target"], "daily_hours": user["daily_hours"]},
        "today": today,
        "days_until_first_scheduled_exam": days_left,
        "tasks": tasks,
        "today_task_count": len(tasks),
        "today_completed_count": sum(1 for task in tasks if task["completed"]),
        "all_task_count": all_count,
        "all_completed_count": completed_count,
        "syllabus_progress_percent": syllabus_percent,
        "syllabus_status": "topic_notes_available" if material_data else ("syllabus_imported" if syllabus_data else "not_imported"),
        "syllabus_topic_total": syllabus_total,
        "syllabus_topic_completed": material_completed,
        "official_sources": {"syllabus": OFFICIAL_SYLLABUS_URL, "pattern": OFFICIAL_PATTERN_URL},
    }


# ----------------------------- Smart study planner -----------------------------


def planner_topics_for_paper(code: str) -> list[dict]:
    syllabus = load_syllabus_data(code)
    if not syllabus or not syllabus.get("sections"):
        return []
    topics: list[dict] = []
    for section in syllabus.get("sections", []):
        for topic in section.get("topics", []):
            topics.append({
                "topic_id": topic["id"],
                "topic_name": topic["name"],
                "section_code": section.get("code", ""),
                "section_name": section.get("name", "Subject"),
                "section_order": section.get("order", 99),
                "official_statement": topic.get("official_statement", ""),
            })
    return topics


def planner_topic_performance(user_id: int, code: str) -> dict[str, dict]:
    data = load_practice_data(code)
    if not data:
        return {}
    question_map = {item["id"]: item for item in data.get("questions", [])}
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT a.question_id, a.is_correct, a.id
               FROM practice_attempts a JOIN practice_sessions s ON s.id = a.session_id
               WHERE a.user_id = ? AND s.paper_code = ? ORDER BY a.id DESC""",
            (user_id, code),
        ).fetchall()
    latest: dict[str, object] = {}
    for row in rows:
        latest.setdefault(row["question_id"], row)
    buckets: dict[str, dict] = {}
    for question_id, row in latest.items():
        question = question_map.get(question_id)
        if not question:
            continue
        topic_id = question.get("topic_id")
        if not topic_id:
            continue
        bucket = buckets.setdefault(topic_id, {"attempted": 0, "correct": 0})
        bucket["attempted"] += 1
        bucket["correct"] += int(row["is_correct"])
    for bucket in buckets.values():
        bucket["accuracy_percent"] = round(bucket["correct"] / bucket["attempted"] * 100) if bucket["attempted"] else 0
    return buckets


def planner_task_dict(row) -> dict:
    metadata = {}
    try:
        metadata = json.loads(row["metadata_json"] or "{}")
    except (TypeError, json.JSONDecodeError):
        pass
    return {
        "id": row["id"], "plan_id": row["plan_id"], "paper_code": row["paper_code"],
        "scheduled_date": row["scheduled_date"], "task_type": row["task_type"],
        "topic_id": row["topic_id"], "title": row["title"], "description": row["description"],
        "duration_minutes": row["duration_minutes"], "priority": row["priority"],
        "status": row["status"], "source": row["source"], "metadata": metadata,
        "completed_at": row["completed_at"],
    }


def insert_planner_task(conn, *, plan_id: int, user_id: int, paper_code: str, scheduled_date: date,
                         task_type: str, title: str, description: str = "", duration_minutes: int = 25,
                         priority: str = "normal", topic_id: str | None = None, source: str = "generated",
                         metadata: dict | None = None) -> int:
    cursor = conn.execute(
        """INSERT INTO planner_tasks
           (plan_id, user_id, paper_code, scheduled_date, task_type, topic_id, title, description,
            duration_minutes, priority, source, metadata_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (plan_id, user_id, paper_code, scheduled_date.isoformat(), task_type, topic_id,
         title, description, duration_minutes, priority, source, json.dumps(metadata or {})),
    )
    return int(cursor.lastrowid)


def build_study_plan(conn, user: dict, payload: PlannerPlanCreatePayload) -> dict:
    code = (payload.paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    topics = planner_topics_for_paper(code)
    if not topics:
        raise HTTPException(status_code=409, detail="A topic-level syllabus import is not available for this paper yet. The planner will be available after its official syllabus has been structured.")
    start = payload.start_date or date.today()
    hours = payload.daily_hours or int(user["daily_hours"])
    end = start + timedelta(days=payload.plan_days - 1)

    progress_rows = conn.execute(
        "SELECT topic_id, status FROM student_material_progress WHERE user_id = ? AND paper_code = ?",
        (user["id"], code),
    ).fetchall()
    progress = {row["topic_id"]: row["status"] for row in progress_rows}
    performance = planner_topic_performance(user["id"], code)
    for topic in topics:
        topic["status"] = progress.get(topic["topic_id"], "not_started")
        topic["performance"] = performance.get(topic["topic_id"], {"attempted": 0, "correct": 0, "accuracy_percent": None})
        accuracy = topic["performance"]["accuracy_percent"]
        if accuracy is not None and accuracy < 60:
            topic["priority_rank"] = 0
        elif topic["status"] == "in_progress":
            topic["priority_rank"] = 1
        elif topic["status"] == "not_started":
            topic["priority_rank"] = 2
        else:
            topic["priority_rank"] = 3
    topics.sort(key=lambda item: (
        item["priority_rank"],
        item["performance"]["accuracy_percent"] if item["performance"]["accuracy_percent"] is not None else 101,
        item["section_order"], item["topic_id"],
    ))

    # Keep the daily load realistic: a topic usually receives one 35-minute
    # learning block and one 20-minute retrieval/practice block.
    minutes_per_topic = 55
    topic_capacity = max(1, min(5, (hours * 60) // minutes_per_topic))
    active_days = max(1, min(payload.plan_days, round(payload.plan_days * 0.65)))
    mock_day_indexes = set(range(6, payload.plan_days, 7)) if payload.include_weekly_mock else set()
    # Reserve weekly review/mock days so a full mock is not stacked on top of
    # the normal topic-learning workload.
    topic_day_indexes = [index for index in range(active_days) if index not in mock_day_indexes]
    topic_limit = min(len(topics), len(topic_day_indexes) * topic_capacity)
    selected_topics = topics[:topic_limit]
    unplanned_count = len(topics) - len(selected_topics)
    topic_slots: dict[int, list[dict]] = {}
    for index, topic in enumerate(selected_topics):
        day_position = min(len(topic_day_indexes) - 1, (index * len(topic_day_indexes)) // max(1, len(selected_topics)))
        day_index = topic_day_indexes[day_position]
        topic_slots.setdefault(day_index, []).append(topic)

    # Archive any existing plan for this paper and create a fresh active plan.
    conn.execute(
        "UPDATE study_plans SET status = 'archived', updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND paper_code = ? AND status = 'active'",
        (user["id"], code),
    )
    conn.execute(
        "DELETE FROM planner_revision_queue WHERE user_id = ? AND paper_code = ?",
        (user["id"], code),
    )
    cursor = conn.execute(
        """INSERT INTO study_plans
           (user_id, paper_code, title, plan_days, daily_hours, start_date, end_date,
            planned_topic_count, unplanned_topic_count, config_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user["id"], code, f"{payload.plan_days}-day {code} preparation plan", payload.plan_days,
         hours, start.isoformat(), end.isoformat(), len(selected_topics), unplanned_count,
         json.dumps({"include_general_aptitude": payload.include_general_aptitude,
                     "include_weekly_mock": payload.include_weekly_mock,
                     "daily_capacity_minutes": hours * 60, "topic_minutes": minutes_per_topic})),
    )
    plan_id = int(cursor.lastrowid)
    practice_data = load_practice_data(code) or {"questions": []}
    practice_topic_ids = {item.get("topic_id") for item in practice_data.get("questions", [])}
    task_count = 0
    for day_index, day_topics in topic_slots.items():
        scheduled = start + timedelta(days=day_index)
        for topic in day_topics:
            topic_id = topic["topic_id"]
            priority = "high" if topic["priority_rank"] == 0 else ("normal" if topic["status"] != "completed" else "low")
            if topic["status"] != "completed":
                insert_planner_task(
                    conn, plan_id=plan_id, user_id=user["id"], paper_code=code, scheduled_date=scheduled,
                    task_type="learn", topic_id=topic_id,
                    title=f"Learn: {topic['topic_name']}",
                    description=f"Study the mapped concepts and learning outcomes for {topic['topic_name']}. Open the topic notes after completing this block.",
                    duration_minutes=35, priority=priority,
                    metadata={"section_code": topic["section_code"], "section_name": topic["section_name"], "accuracy_percent": topic["performance"]["accuracy_percent"]},
                )
                task_count += 1
            practice_title = f"Practise: {topic['topic_name']}" if topic_id in practice_topic_ids else f"Active recall: {topic['topic_name']}"
            practice_description = ("Solve topic-matched GATEPath practice questions and review every explanation." if topic_id in practice_topic_ids
                                    else "Close your notes and write key definitions, methods and one worked example from memory. Practice questions for this topic are not yet imported.")
            insert_planner_task(
                conn, plan_id=plan_id, user_id=user["id"], paper_code=code, scheduled_date=scheduled,
                task_type="practice", topic_id=topic_id, title=practice_title,
                description=practice_description, duration_minutes=20, priority=priority,
                metadata={"section_code": topic["section_code"], "section_name": topic["section_name"], "question_bank_available": topic_id in practice_topic_ids},
            )
            task_count += 1
            first_review = scheduled + timedelta(days=1)
            while (first_review - start).days in mock_day_indexes and first_review <= end:
                first_review += timedelta(days=1)
            first_review_minutes = 5 if hours == 1 else 10
            conn.execute(
                """INSERT OR REPLACE INTO planner_revision_queue
                   (user_id, paper_code, topic_id, topic_name, due_date, interval_days, review_count, ease_factor, status)
                   VALUES (?, ?, ?, ?, ?, 1, 0, 2.5, 'due')""",
                (user["id"], code, topic_id, topic["topic_name"], first_review.isoformat()),
            )
            if first_review <= end:
                insert_planner_task(
                    conn, plan_id=plan_id, user_id=user["id"], paper_code=code, scheduled_date=first_review,
                    task_type="revision", topic_id=topic_id, title=f"First review: {topic['topic_name']}",
                    description="Use active recall first, then check your notes. Mark this review complete to schedule the next spaced repetition.",
                    duration_minutes=first_review_minutes, priority="high" if priority == "high" else "normal", source="revision",
                    metadata={"review_stage": 1},
                )
                task_count += 1

    if payload.include_general_aptitude:
        # The official shared GA PDF is linked, but topic-level GA transcription
        # has not yet been imported; the planner labels this as source-led review.
        ga_day_indexes = [index for index in range(active_days, payload.plan_days, 3) if index not in mock_day_indexes]
        for day_index in ga_day_indexes:
            scheduled = start + timedelta(days=day_index)
            insert_planner_task(
                conn, plan_id=plan_id, user_id=user["id"], paper_code=code, scheduled_date=scheduled,
                task_type="practice", title="General Aptitude: source-led practice",
                description="Review the official shared General Aptitude syllabus and solve a short set from a trusted resource. GATEPath topic-level GA content is pending import.",
                duration_minutes=20, priority="normal", metadata={"shared_section": "GA", "official_syllabus_url": "https://gate2027.iitm.ac.in/exam_papers_and_syllabus", "topic_content_pending": True},
            )
            task_count += 1

    if payload.include_weekly_mock:
        mock_catalog = load_mock_manifest(code, f"{code}-FULL-MOCK-01")
        for day_index in sorted(mock_day_indexes):
            scheduled = start + timedelta(days=day_index)
            if mock_catalog:
                duration = 180 if hours >= 3 else max(45, hours * 30)
                title = "Weekly GATE-style mock examination" if duration == 180 else "Weekly sectional mock practice"
                description = "Take the available full-length mock in exam conditions." if duration == 180 else "Your daily study budget is below three hours; complete a shorter sectional practice session rather than squeezing in a full mock."
            else:
                duration = min(60, hours * 30)
                title = "Weekly mixed-topic review"
                description = "Review completed topics and attempt a mixed-topic practice set available for your paper."
            insert_planner_task(
                conn, plan_id=plan_id, user_id=user["id"], paper_code=code, scheduled_date=scheduled,
                task_type="mock", title=title, description=description,
                duration_minutes=duration, priority="high", metadata={"full_mock_available": bool(mock_catalog)},
            )
            task_count += 1

    conn.execute("UPDATE study_plans SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (plan_id,))
    return {
        "id": plan_id, "paper_code": code, "title": f"{payload.plan_days}-day {code} preparation plan",
        "plan_days": payload.plan_days, "daily_hours": hours, "start_date": start.isoformat(),
        "end_date": end.isoformat(), "planned_topic_count": len(selected_topics),
        "unplanned_topic_count": unplanned_count, "task_count": task_count,
        "capacity_note": (f"Your {hours}-hour daily target supports about {topic_capacity} topic block(s) per day. {unplanned_count} syllabus topics remain outside this plan and should be included in an extended plan." if unplanned_count else "All currently imported topics are scheduled within this plan."),
    }


@app.post("/api/planner/plans", status_code=201)
def create_study_plan(payload: PlannerPlanCreatePayload, user=Depends(require_user)):
    with get_connection() as conn:
        return build_study_plan(conn, user, payload)


@app.get("/api/planner/overview")
def planner_overview(paper_code: str | None = None, selected_date: date | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    selected = selected_date or date.today()
    today = date.today()
    with get_connection() as conn:
        plan = conn.execute(
            "SELECT * FROM study_plans WHERE user_id = ? AND paper_code = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
            (user["id"], code),
        ).fetchone()
        if not plan:
            syllabus = load_syllabus_data(code)
            return {"paper_code": code, "plan": None, "tasks": [], "selected_date": selected.isoformat(),
                    "today": today.isoformat(), "revision_due": [], "weak_topics": [],
                    "content_available": bool(syllabus and syllabus.get("sections")),
                    "official_syllabus_url": (syllabus or {}).get("source_url", OFFICIAL_SYLLABUS_URL),
                    "message": ("Create a 30, 60 or 90-day plan to begin scheduling your preparation." if syllabus and syllabus.get("sections") else "Topic-level syllabus content has not yet been imported for this paper. The planner will become available after verified topic data is added.")}
        task_rows = conn.execute(
            """SELECT * FROM planner_tasks WHERE user_id = ? AND plan_id = ?
               AND scheduled_date BETWEEN ? AND ? ORDER BY scheduled_date, priority DESC, id""",
            (user["id"], plan["id"], selected.isoformat(), (selected + timedelta(days=6)).isoformat()),
        ).fetchall()
        selected_rows = conn.execute(
            "SELECT * FROM planner_tasks WHERE user_id = ? AND plan_id = ? AND scheduled_date = ? ORDER BY priority DESC, id",
            (user["id"], plan["id"], selected.isoformat()),
        ).fetchall()
        counts = conn.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                      SUM(CASE WHEN status = 'pending' AND scheduled_date < ? THEN 1 ELSE 0 END) AS overdue,
                      SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) AS skipped
               FROM planner_tasks WHERE user_id = ? AND plan_id = ?""",
            (today.isoformat(), user["id"], plan["id"]),
        ).fetchone()
        due_rows = conn.execute(
            "SELECT * FROM planner_revision_queue WHERE user_id = ? AND paper_code = ? AND status = 'due' AND due_date <= ? ORDER BY due_date LIMIT 12",
            (user["id"], code, (selected + timedelta(days=6)).isoformat()),
        ).fetchall()
    performance = planner_topic_performance(user["id"], code)
    weak_topics = []
    for topic_id, stats in performance.items():
        if stats["accuracy_percent"] < 70:
            weak_topics.append({"topic_id": topic_id, **stats})
    weak_topics.sort(key=lambda item: (item["accuracy_percent"], -item["attempted"]))
    topic_lookup = {topic["topic_id"]: topic["topic_name"] for topic in planner_topics_for_paper(code)}
    due_revisions = [{"topic_id": row["topic_id"], "topic_name": row["topic_name"], "due_date": row["due_date"],
                      "interval_days": row["interval_days"], "review_count": row["review_count"]} for row in due_rows]
    task_count = int(counts["total"] or 0)
    completed_count = int(counts["completed"] or 0)
    plan_dict = {
        "id": plan["id"], "title": plan["title"], "paper_code": plan["paper_code"],
        "plan_days": plan["plan_days"], "daily_hours": plan["daily_hours"],
        "start_date": plan["start_date"], "end_date": plan["end_date"],
        "planned_topic_count": plan["planned_topic_count"], "unplanned_topic_count": plan["unplanned_topic_count"],
        "task_count": task_count, "completed_count": completed_count,
        "completion_percent": round(completed_count / task_count * 100) if task_count else 0,
        "overdue_count": int(counts["overdue"] or 0), "skipped_count": int(counts["skipped"] or 0),
        "days_remaining": max((date.fromisoformat(plan["end_date"]) - today).days, 0),
    }
    selected_minutes = sum(row["duration_minutes"] for row in selected_rows if row["status"] != "skipped")
    day_map: dict[str, dict] = {}
    for row in task_rows:
        key = row["scheduled_date"]
        bucket = day_map.setdefault(key, {"date": key, "task_count": 0, "completed_count": 0, "minutes": 0})
        bucket["task_count"] += 1
        bucket["completed_count"] += int(row["status"] == "completed")
        if row["status"] != "skipped":
            bucket["minutes"] += row["duration_minutes"]
    with get_connection() as conn:
        selected_task_rows = conn.execute(
            "SELECT * FROM planner_tasks WHERE user_id = ? AND plan_id = ? AND scheduled_date = ? ORDER BY priority DESC, id",
            (user["id"], plan["id"], selected.isoformat()),
        ).fetchall()
    return {
        "paper_code": code, "plan": plan_dict, "selected_date": selected.isoformat(), "today": today.isoformat(),
        "selected_day_minutes": selected_minutes,
        "selected_day_tasks": [planner_task_dict(row) for row in selected_task_rows],
        "upcoming_tasks": [planner_task_dict(row) for row in task_rows],
        "week_summary": sorted(day_map.values(), key=lambda item: item["date"]),
        "revision_due": due_revisions,
        "weak_topics": [{**item, "topic_name": topic_lookup.get(item["topic_id"], item["topic_id"])} for item in weak_topics[:6]],
    }


@app.post("/api/planner/tasks", status_code=201)
def create_planner_custom_task(payload: PlannerTaskCreatePayload, user=Depends(require_user)):
    code = user["paper_code"]
    with get_connection() as conn:
        plan = conn.execute("SELECT * FROM study_plans WHERE user_id = ? AND paper_code = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (user["id"], code)).fetchone()
        if not plan:
            raise HTTPException(status_code=409, detail="Create a study plan before adding scheduled tasks")
        task_id = insert_planner_task(
            conn, plan_id=plan["id"], user_id=user["id"], paper_code=code,
            scheduled_date=payload.scheduled_date or date.today(), task_type="custom",
            title=payload.title.strip(), description="Student-created study task.",
            duration_minutes=payload.duration_minutes, priority=payload.priority, source="manual",
        )
        row = conn.execute("SELECT * FROM planner_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])).fetchone()
    return planner_task_dict(row)


@app.patch("/api/planner/tasks/{task_id}")
def update_planner_task(task_id: int, payload: PlannerTaskUpdatePayload, user=Depends(require_user)):
    values = payload.model_dump(exclude_unset=True)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM planner_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Planner task not found")
        if row["status"] in ("completed", "skipped") and values.get("status") == "completed":
            return planner_task_dict(row)
        assignments = []
        params: list[object] = []
        if "status" in values and values["status"] is not None:
            assignments.append("status = ?")
            params.append(values["status"])
            assignments.append("completed_at = ?")
            params.append(datetime.now(timezone.utc).isoformat() if values["status"] == "completed" else None)
        if "scheduled_date" in values and values["scheduled_date"] is not None:
            assignments.append("scheduled_date = ?")
            params.append(values["scheduled_date"].isoformat())
        if assignments:
            assignments.append("updated_at = CURRENT_TIMESTAMP")
            conn.execute(f"UPDATE planner_tasks SET {', '.join(assignments)} WHERE id = ? AND user_id = ?", (*params, task_id, user["id"]))
        if values.get("status") == "completed" and row["task_type"] == "learn" and row["topic_id"]:
            conn.execute(
                """INSERT INTO student_material_progress (user_id, paper_code, topic_id, status)
                   VALUES (?, ?, ?, 'in_progress')
                   ON CONFLICT(user_id, paper_code, topic_id) DO UPDATE SET
                   status = CASE WHEN student_material_progress.status = 'completed'
                                 THEN 'completed' ELSE 'in_progress' END,
                   updated_at = CURRENT_TIMESTAMP""",
                (user["id"], row["paper_code"], row["topic_id"]),
            )
        if values.get("status") == "completed" and row["task_type"] == "revision" and row["topic_id"]:
            queue = conn.execute(
                "SELECT * FROM planner_revision_queue WHERE user_id = ? AND paper_code = ? AND topic_id = ?",
                (user["id"], row["paper_code"], row["topic_id"]),
            ).fetchone()
            if queue:
                quality = values.get("review_quality", "good")
                base_intervals = {"again": 1, "hard": 2, "good": 4, "easy": 7}
                interval = min(45, base_intervals[quality] * (1 + int(queue["review_count"])))
                next_due = date.today() + timedelta(days=interval)
                conn.execute(
                    """UPDATE planner_revision_queue SET due_date = ?, interval_days = ?, review_count = review_count + 1,
                       ease_factor = MAX(1.3, ease_factor + ?), last_reviewed_at = ?, status = 'due', updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (next_due.isoformat(), interval, {"again": -0.2, "hard": -0.1, "good": 0.0, "easy": 0.15}[quality], datetime.now(timezone.utc).isoformat(), queue["id"]),
                )
                plan = conn.execute("SELECT id, end_date FROM study_plans WHERE id = ?", (row["plan_id"],)).fetchone()
                if plan and next_due <= date.fromisoformat(plan["end_date"]):
                    exists = conn.execute(
                        "SELECT id FROM planner_tasks WHERE plan_id = ? AND topic_id = ? AND task_type = 'revision' AND scheduled_date = ?",
                        (row["plan_id"], row["topic_id"], next_due.isoformat()),
                    ).fetchone()
                    if not exists:
                        insert_planner_task(
                            conn, plan_id=row["plan_id"], user_id=user["id"], paper_code=row["paper_code"],
                            scheduled_date=next_due, task_type="revision", topic_id=row["topic_id"],
                            title=f"Spaced review: {queue['topic_name']}",
                            description="Review from memory, check your notes and rate how well you recalled the concept.",
                            duration_minutes=10, priority="normal", source="revision",
                            metadata={"review_stage": int(queue["review_count"]) + 2},
                        )
        updated = conn.execute("SELECT * FROM planner_tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])).fetchone()
    return planner_task_dict(updated)


@app.post("/api/planner/reschedule-overdue")
def reschedule_overdue_planner_tasks(user=Depends(require_user)):
    today = date.today()
    with get_connection() as conn:
        plan = conn.execute("SELECT * FROM study_plans WHERE user_id = ? AND paper_code = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (user["id"], user["paper_code"])).fetchone()
        if not plan:
            raise HTTPException(status_code=409, detail="Create a study plan before rescheduling tasks")
        overdue = conn.execute(
            "SELECT * FROM planner_tasks WHERE user_id = ? AND plan_id = ? AND status = 'pending' AND scheduled_date < ? ORDER BY scheduled_date, priority DESC, id",
            (user["id"], plan["id"], today.isoformat()),
        ).fetchall()
        daily_capacity = int(plan["daily_hours"]) * 60
        daily_load: dict[str, int] = {}
        for row in conn.execute(
            "SELECT scheduled_date, SUM(duration_minutes) AS minutes FROM planner_tasks WHERE user_id = ? AND plan_id = ? AND status = 'pending' AND scheduled_date >= ? GROUP BY scheduled_date",
            (user["id"], plan["id"], today.isoformat()),
        ).fetchall():
            daily_load[row["scheduled_date"]] = int(row["minutes"] or 0)
        moved = 0
        for task in overdue:
            candidate = today
            for offset in range(7):
                candidate = today + timedelta(days=offset)
                key = candidate.isoformat()
                if daily_load.get(key, 0) + int(task["duration_minutes"]) <= daily_capacity:
                    break
            key = candidate.isoformat()
            conn.execute("UPDATE planner_tasks SET scheduled_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", (key, task["id"], user["id"]))
            daily_load[key] = daily_load.get(key, 0) + int(task["duration_minutes"])
            moved += 1
    return {"rescheduled_count": moved, "message": f"Moved {moved} overdue task(s) into the next seven days within your daily study-hour target where possible."}


# --------------------------- Stage 11: AI tutor ---------------------------

def tutor_conversation_dict(row) -> dict:
    return {
        "id": row["id"],
        "paper_code": row["paper_code"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def tutor_message_dict(row) -> dict:
    try:
        source_refs = json.loads(row["source_refs_json"] or "[]")
    except (TypeError, json.JSONDecodeError):
        source_refs = []
    return {
        "id": row["id"],
        "role": row["role"],
        "content": row["content"],
        "sources": source_refs,
        "image_attached": bool(row["image_attached"]),
        "provider": row["provider"],
        "created_at": row["created_at"],
    }


def validate_tutor_paper(user, requested_code: str | None) -> tuple[str, dict]:
    code = (requested_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=400, detail="Unknown GATE paper code")
    if code != user["paper_code"]:
        raise HTTPException(status_code=409, detail="Switch your selected GATE paper in profile settings before using its tutor")
    paper = tutor_service.paper_record(code) or {"code": code, "name": code, "official_syllabus_url": OFFICIAL_SYLLABUS_URL}
    return code, paper


@app.get("/api/tutor/status")
def tutor_status(user=Depends(require_user)):
    code, paper = validate_tutor_paper(user, None)
    materials = tutor_service.material_documents(code)
    config = tutor_service.ai_configuration()
    return {
        "paper_code": code,
        "paper_name": paper.get("name", code),
        "ai_available": config["available"],
        "provider": config["provider"],
        "model": config["model"],
        "vision_available": config["vision_available"],
        "indexed_topic_count": len(materials),
        "indexed_topics": [{"id": item["id"], "name": item["topic_name"], "section": item["section_name"]} for item in materials],
        "official_syllabus_url": paper.get("official_syllabus_url", OFFICIAL_SYLLABUS_URL),
        "mode": "ai_rag" if config["available"] else ("knowledge_only" if materials else "official_source_only"),
        "privacy_note": "Uploaded images are sent to the configured AI provider only for visual analysis and are not stored in GATEPath. Text conversations are stored privately in your account.",
    }


@app.get("/api/tutor/conversations")
def list_tutor_conversations(limit: int = Query(default=30, ge=1, le=100), user=Depends(require_user)):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tutor_conversations WHERE user_id = ? ORDER BY updated_at DESC, id DESC LIMIT ?",
            (user["id"], limit),
        ).fetchall()
        return {"items": [tutor_conversation_dict(row) for row in rows]}


@app.get("/api/tutor/conversations/{conversation_id}")
def get_tutor_conversation(conversation_id: str, user=Depends(require_user)):
    with get_connection() as conn:
        conversation = conn.execute(
            "SELECT * FROM tutor_conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user["id"]),
        ).fetchone()
        if not conversation:
            raise HTTPException(status_code=404, detail="Tutor conversation not found")
        messages = conn.execute(
            "SELECT * FROM tutor_messages WHERE conversation_id = ? AND user_id = ? ORDER BY id",
            (conversation_id, user["id"]),
        ).fetchall()
    return {"conversation": tutor_conversation_dict(conversation), "messages": [tutor_message_dict(row) for row in messages]}


@app.delete("/api/tutor/conversations/{conversation_id}", status_code=204)
def delete_tutor_conversation(conversation_id: str, user=Depends(require_user)):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tutor_conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user["id"]),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tutor conversation not found")
    return Response(status_code=204)


@app.post("/api/tutor/chat")
async def tutor_chat(payload: TutorChatPayload, user=Depends(require_user)):
    code, paper = validate_tutor_paper(user, payload.paper_code)
    docs = tutor_service.material_documents(code)
    if payload.topic_id and not any(item["id"] == payload.topic_id for item in docs):
        raise HTTPException(status_code=404, detail="That topic is not part of the indexed study library for this paper")
    sources = tutor_service.retrieve_context(code, payload.message, payload.topic_id, limit=5)
    if not sources:
        official_url = paper.get("official_syllabus_url", OFFICIAL_SYLLABUS_URL)
        sources = [{
            "source_id": "OFFICIAL-1", "topic_id": None,
            "topic_name": "Official GATE syllabus", "section_name": "Official source",
            "excerpt": "Use the official paper syllabus as the source of truth. GATEPath has not yet indexed topic-wise learning notes for this paper.",
            "source_url": official_url, "source_label": "Official GATE 2027 syllabus PDF",
            "content_status": "official_source", "retrieval_score": 0.0,
        }]
    conversation_id = payload.conversation_id
    history: list[dict] = []
    with get_connection() as conn:
        if conversation_id:
            conversation = conn.execute(
                "SELECT * FROM tutor_conversations WHERE id = ? AND user_id = ? AND paper_code = ?",
                (conversation_id, user["id"], code),
            ).fetchone()
            if not conversation:
                raise HTTPException(status_code=404, detail="Tutor conversation not found")
            history_rows = conn.execute(
                "SELECT role, content FROM tutor_messages WHERE conversation_id = ? AND user_id = ? ORDER BY id DESC LIMIT 8",
                (conversation_id, user["id"]),
            ).fetchall()
            history = [{"role": row["role"], "content": row["content"]} for row in reversed(history_rows)]
        else:
            conversation_id = secrets.token_urlsafe(18)
    message_pack = tutor_service.build_tutor_messages(
        paper_code=code, paper_name=paper.get("name", code), question=payload.message,
        mode=payload.explanation_level, sources=sources, history=history,
        image_attached=bool(payload.image_data_url),
    )
    config = tutor_service.ai_configuration()
    provider = "knowledge"
    ai_used = False
    provider_error = None
    if config["available"]:
        try:
            answer = await tutor_service.call_chat_completion(message_pack, image_data_url=payload.image_data_url)
            provider = config["provider"] or "AI provider"
            ai_used = True
        except Exception as exc:
            provider_error = str(exc)[:240]
            answer = tutor_service.offline_grounded_answer(payload.message, sources, image_attached=bool(payload.image_data_url))
            answer += "\n\nThe configured AI service could not complete this request. Your retrieved source notes are still available above."
    else:
        answer = tutor_service.offline_grounded_answer(payload.message, sources, image_attached=bool(payload.image_data_url))

    title = payload.message[:64].strip() or "Image question"
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM tutor_conversations WHERE id = ? AND user_id = ?", (conversation_id, user["id"])).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO tutor_conversations (id, user_id, paper_code, title) VALUES (?, ?, ?, ?)",
                (conversation_id, user["id"], code, title),
            )
        conn.execute(
            "INSERT INTO tutor_messages (conversation_id, user_id, role, content, source_refs_json, image_attached, provider) VALUES (?, ?, 'user', ?, '[]', ?, 'student')",
            (conversation_id, user["id"], payload.message, int(bool(payload.image_data_url))),
        )
        conn.execute(
            "INSERT INTO tutor_messages (conversation_id, user_id, role, content, source_refs_json, image_attached, provider) VALUES (?, ?, 'assistant', ?, ?, 0, ?)",
            (conversation_id, user["id"], answer, json.dumps(sources, ensure_ascii=False), provider),
        )
        conn.execute("UPDATE tutor_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", (conversation_id, user["id"]))
    return {
        "conversation_id": conversation_id,
        "answer": answer,
        "sources": sources,
        "ai_used": ai_used,
        "mode": "ai_rag" if ai_used else ("knowledge_only" if docs else "official_source_only"),
        "image_attached": bool(payload.image_data_url),
        "image_analyzed": bool(payload.image_data_url and ai_used),
        "provider_error": provider_error,
        "notice": "AI-generated explanations may contain errors. Verify formulas and exam rules against official or trusted references." if ai_used else "Knowledge-only response: no AI-generated solution was produced.",
    }


@app.post("/api/tutor/similar-questions")
async def tutor_similar_questions(payload: TutorSimilarQuestionsPayload, user=Depends(require_user)):
    code, paper = validate_tutor_paper(user, None)
    docs = tutor_service.material_documents(code)
    material = next((item for item in docs if item["id"] == payload.topic_id), None)
    if not material:
        raise HTTPException(status_code=404, detail="Topic notes are not indexed for this paper")
    sources = tutor_service.retrieve_context(code, material["topic_name"], payload.topic_id, limit=3)
    config = tutor_service.ai_configuration()
    if not config["available"]:
        practice_data = load_practice_data(code) or {}
        related = [item for item in practice_data.get("questions", []) if item.get("topic_id") == payload.topic_id]
        return {
            "generated": False,
            "message": "AI question generation is unavailable until an AI provider is configured. Here are existing GATEPath original practice questions for this topic instead.",
            "topic_name": material["topic_name"],
            "related_questions": [{"id": item["id"], "prompt": item["prompt"], "question_type": item["question_type"], "difficulty": item["difficulty"], "content_label": "GATEPath original practice question"} for item in related[:payload.count]],
            "sources": sources,
        }
    messages = tutor_service.build_similar_question_prompt(
        paper_code=code, topic_name=material["topic_name"], difficulty=payload.difficulty,
        count=payload.count, sources=sources,
    )
    try:
        generated = await tutor_service.call_chat_completion(messages, max_tokens=2600)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Question generation service is unavailable: {str(exc)[:180]}") from exc
    return {
        "generated": True,
        "topic_name": material["topic_name"],
        "content_label": "AI-generated original practice · not an official GATE PYQ",
        "content": generated,
        "sources": sources,
    }


# ---------------- Stage 12: analytics, community and administration ----------------

class CommunityPostPayload(BaseModel):
    paper_code: str = Field(default="CS", min_length=2, max_length=3)
    category: Literal["Doubt", "Study tips", "Resources", "Exam strategy", "General"] = "Doubt"
    title: str = Field(min_length=8, max_length=120)
    body: str = Field(min_length=20, max_length=5000)

    @field_validator("title", "body")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()


class CommunityReplyPayload(BaseModel):
    body: str = Field(min_length=2, max_length=2000)

    @field_validator("body")
    @classmethod
    def trim_body(cls, value: str) -> str:
        return value.strip()


class CommunityReportPayload(BaseModel):
    target_type: Literal["post", "reply"]
    target_id: int = Field(ge=1)
    reason: str = Field(min_length=5, max_length=500)

    @field_validator("reason")
    @classmethod
    def trim_reason(cls, value: str) -> str:
        return value.strip()


class AdminUserStatusPayload(BaseModel):
    is_active: bool


class AdminReportResolutionPayload(BaseModel):
    status: Literal["resolved", "dismissed"]
    action: Literal["none", "hide", "remove"] = "none"
    note: str = Field(default="", max_length=500)


class AdminModerationPayload(BaseModel):
    status: Literal["published", "hidden", "removed"]
    pinned: bool | None = None


class AdminContentReviewPayload(BaseModel):
    status: Literal["approved", "needs_changes", "rejected", "pending_review"]
    note: str = Field(default="", max_length=1000)


def _latest_attempt_rows(conn, table: str, user_id: int, question_prefix: str):
    # table is selected only from the fixed internal call sites below.
    if table not in {"practice_attempts", "pyq_attempts"}:
        raise ValueError("Unsupported analytics source")
    return conn.execute(
        f"""SELECT a.* FROM {table} a
            JOIN (SELECT question_id, MAX(id) AS latest_id FROM {table}
                  WHERE user_id = ? AND question_id LIKE ? GROUP BY question_id) latest
              ON latest.latest_id = a.id
            ORDER BY a.id DESC""",
        (user_id, question_prefix),
    ).fetchall()


def _analytics_question_metadata(code: str) -> dict[str, dict]:
    mapping: dict[str, dict] = {}
    practice = load_practice_data(code) or {}
    for question in practice.get("questions", []):
        mapping[question.get("id", "")] = {
            "section_code": question.get("section_code", ""),
            "section_name": question.get("section_name", "Other"),
            "topic_id": question.get("topic_id", ""),
            "topic_name": question.get("topic_name", "Other"),
        }
    pyq = load_pyq_data(code, 2026) or {}
    for session in pyq.get("sessions", []):
        for question in session.get("questions", []):
            mapping[question.get("id", "")] = {
                "section_code": question.get("source_section_code", ""),
                "section_name": question.get("section_name", "Other"),
                "topic_id": question.get("topic_id", ""),
                "topic_name": question.get("topic_name", "Other"),
            }
    return mapping


@app.get("/api/analytics")
def student_analytics(paper_code: str | None = None, user=Depends(require_user)):
    code = (paper_code or user["paper_code"]).upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    syllabus = load_syllabus_data(code) or {}
    questions_meta = _analytics_question_metadata(code)
    with get_connection() as conn:
        progress_rows = conn.execute(
            "SELECT status, COUNT(*) AS count FROM student_material_progress WHERE user_id = ? AND paper_code = ? GROUP BY status",
            (user["id"], code),
        ).fetchall()
        practice_latest = _latest_attempt_rows(conn, "practice_attempts", user["id"], f"GP-{code}-%")
        pyq_latest = _latest_attempt_rows(conn, "pyq_attempts", user["id"], f"G26-{code}-%")
        practice_attempt_total = conn.execute(
            "SELECT COUNT(*) AS count FROM practice_attempts WHERE user_id = ? AND question_id LIKE ?",
            (user["id"], f"GP-{code}-%"),
        ).fetchone()["count"]
        pyq_attempt_total = conn.execute(
            "SELECT COUNT(*) AS count FROM pyq_attempts WHERE user_id = ? AND question_id LIKE ?",
            (user["id"], f"G26-{code}-%"),
        ).fetchone()["count"]
        mock_rows = conn.execute(
            """SELECT id, test_id, status, score, maximum_marks, attempted_count, correct_count,
                      wrong_count, created_at, submitted_at
               FROM mock_test_sessions WHERE user_id = ? AND paper_code = ? AND status IN ('submitted', 'expired')
               ORDER BY created_at DESC LIMIT 20""",
            (user["id"], code),
        ).fetchall()
        completed_tasks = conn.execute(
            """SELECT scheduled_date, SUM(duration_minutes) AS minutes, COUNT(*) AS task_count
               FROM planner_tasks WHERE user_id = ? AND paper_code = ? AND status = 'completed'
               GROUP BY scheduled_date""",
            (user["id"], code),
        ).fetchall()
        planner_task_counts = conn.execute(
            """SELECT COUNT(*) AS total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed
               FROM planner_tasks WHERE user_id = ? AND paper_code = ?""",
            (user["id"], code),
        ).fetchone()

    progress = {row["status"]: row["count"] for row in progress_rows}
    topic_total = sum(len(section.get("topics", [])) for section in syllabus.get("sections", []))
    topic_completed = int(progress.get("completed", 0))
    topic_in_progress = int(progress.get("in_progress", 0))
    all_latest = list(practice_latest) + list(pyq_latest)
    attempts_by_topic: dict[str, dict] = {}
    attempts_by_section: dict[str, dict] = {}
    for row in all_latest:
        metadata = questions_meta.get(row["question_id"], {})
        section_code = metadata.get("section_code") or "unmapped"
        section_name = metadata.get("section_name") or "Unmapped questions"
        topic_id = metadata.get("topic_id") or "unmapped"
        topic_name = metadata.get("topic_name") or "Unmapped topic"
        for bucket, key, name in ((attempts_by_section, section_code, section_name), (attempts_by_topic, topic_id, topic_name)):
            item = bucket.setdefault(key, {"code" if bucket is attempts_by_section else "topic_id": key,
                                            "name" if bucket is attempts_by_section else "topic_name": name,
                                            "attempted": 0, "correct": 0})
            item["attempted"] += 1
            item["correct"] += int(row["is_correct"])
    for item in attempts_by_section.values():
        item["accuracy_percent"] = round(item["correct"] / item["attempted"] * 100) if item["attempted"] else 0
    for item in attempts_by_topic.values():
        item["accuracy_percent"] = round(item["correct"] / item["attempted"] * 100) if item["attempted"] else 0
    section_performance = sorted(attempts_by_section.values(), key=lambda item: (item["accuracy_percent"], item["name"]))
    weak_topics = sorted((item for item in attempts_by_topic.values() if item["attempted"] >= 1), key=lambda item: (item["accuracy_percent"], -item["attempted"]))[:8]
    attempt_count = len(all_latest)
    correct_count = sum(int(row["is_correct"]) for row in all_latest)
    accuracy = round(correct_count / attempt_count * 100) if attempt_count else 0

    today = date.today()
    activity_map: dict[str, dict] = {}
    for day_offset in range(13, -1, -1):
        key = (today - timedelta(days=day_offset)).isoformat()
        activity_map[key] = {"date": key, "study_minutes": 0, "completed_tasks": 0, "practice_attempts": 0, "mock_tests": 0}
    for row in completed_tasks:
        if row["scheduled_date"] in activity_map:
            activity_map[row["scheduled_date"]]["study_minutes"] += int(row["minutes"] or 0)
            activity_map[row["scheduled_date"]]["completed_tasks"] += int(row["task_count"] or 0)
    # Attempt and mock dates use the DB's stored UTC-like timestamp; date substrings keep grouping deterministic.
    with get_connection() as conn:
        daily_practice = conn.execute(
            "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS count FROM practice_attempts WHERE user_id = ? AND question_id LIKE ? AND created_at >= date('now', '-13 days') GROUP BY day",
            (user["id"], f"GP-{code}-%"),
        ).fetchall()
        daily_pyq = conn.execute(
            "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS count FROM pyq_attempts WHERE user_id = ? AND question_id LIKE ? AND created_at >= date('now', '-13 days') GROUP BY day",
            (user["id"], f"G26-{code}-%"),
        ).fetchall()
        daily_mocks = conn.execute(
            "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS count FROM mock_test_sessions WHERE user_id = ? AND paper_code = ? AND status IN ('submitted','expired') AND created_at >= date('now', '-13 days') GROUP BY day",
            (user["id"], code),
        ).fetchall()
    for rows in (daily_practice, daily_pyq):
        for row in rows:
            if row["day"] in activity_map:
                activity_map[row["day"]]["practice_attempts"] += int(row["count"])
    for row in daily_mocks:
        if row["day"] in activity_map:
            activity_map[row["day"]]["mock_tests"] += int(row["count"])
    activity = list(activity_map.values())
    active_days = sum(1 for item in activity if item["study_minutes"] or item["practice_attempts"] or item["mock_tests"])
    streak = 0
    for item in reversed(activity):
        if item["study_minutes"] or item["practice_attempts"] or item["mock_tests"]:
            streak += 1
        else:
            break
    mock_history = [dict(row) for row in mock_rows]
    mock_scores = [float(row["score"] or 0) for row in mock_rows]
    return {
        "paper_code": code,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "syllabus": {"total_topics": topic_total, "completed_topics": topic_completed,
                     "in_progress_topics": topic_in_progress,
                     "completion_percent": round(topic_completed / topic_total * 100) if topic_total else 0,
                     "content_status": syllabus.get("content_status", "awaiting_structured_import")},
        "practice": {"unique_questions_attempted": attempt_count, "attempts_total": int(practice_attempt_total) + int(pyq_attempt_total),
                     "correct_latest": correct_count, "accuracy_percent": accuracy,
                     "practice_attempts": int(practice_attempt_total), "pyq_attempts": int(pyq_attempt_total)},
        "planner": {"tasks_total": int(planner_task_counts["total"] or 0), "tasks_completed": int(planner_task_counts["completed"] or 0)},
        "mock_tests": {"completed": len(mock_rows), "best_score": round(max(mock_scores), 2) if mock_scores else None,
                       "average_score": round(sum(mock_scores) / len(mock_scores), 2) if mock_scores else None,
                       "history": mock_history},
        "section_performance": section_performance,
        "weak_topics": weak_topics,
        "activity": activity,
        "active_days_last_14": active_days,
        "current_study_streak_days": streak,
        "notice": "Analytics summarise recorded GATEPath activity only. Unattempted topics and unrecorded offline study are not estimated.",
    }


@app.get("/api/community/feed")
def community_feed(
    paper_code: str | None = None,
    category: str | None = None,
    scope: Literal["paper", "all", "mine"] = "paper",
    q: str = Query(default="", max_length=100),
    page: int = Query(default=1, ge=1, le=10000),
    limit: int = Query(default=20, ge=1, le=50),
    user=Depends(require_user),
):
    code = (paper_code or user["paper_code"]).upper()
    if scope == "paper" and code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    if category and category not in {"Doubt", "Study tips", "Resources", "Exam strategy", "General"}:
        raise HTTPException(status_code=422, detail="Unknown community category")
    clauses = ["p.status = 'published'"]
    params: list[object] = []
    if scope == "paper":
        clauses.append("p.paper_code = ?"); params.append(code)
    elif scope == "mine":
        clauses.append("p.user_id = ?"); params.append(user["id"])
    if category:
        clauses.append("p.category = ?"); params.append(category)
    if q.strip():
        clauses.append("(p.title LIKE ? OR p.body LIKE ?)")
        pattern = f"%{q.strip()}%"; params.extend([pattern, pattern])
    where = " AND ".join(clauses)
    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) AS count FROM community_posts p WHERE {where}", params).fetchone()["count"]
        rows = conn.execute(
            f"""SELECT p.id, p.user_id, p.paper_code, p.category, p.title, p.body, p.pinned, p.created_at, p.updated_at,
                       u.full_name AS author_name,
                       (SELECT COUNT(*) FROM community_replies r WHERE r.post_id = p.id AND r.status = 'published') AS reply_count,
                       (SELECT COUNT(*) FROM community_post_likes l WHERE l.post_id = p.id) AS like_count,
                       EXISTS(SELECT 1 FROM community_post_likes l WHERE l.post_id = p.id AND l.user_id = ?) AS liked_by_me
                FROM community_posts p JOIN users u ON u.id = p.user_id
                WHERE {where}
                ORDER BY p.pinned DESC, p.created_at DESC LIMIT ? OFFSET ?""",
            [user["id"], *params, limit, (page - 1) * limit],
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["is_owner"] = int(row["user_id"]) == int(user["id"])
        del item["user_id"]
        items.append(item)
    return {"items": items, "page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit,
            "paper_code": code, "scope": scope}


@app.post("/api/community/posts", status_code=201)
def community_create_post(payload: CommunityPostPayload, user=Depends(require_user)):
    code = payload.paper_code.upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO community_posts(user_id, paper_code, category, title, body) VALUES (?, ?, ?, ?, ?)",
            (user["id"], code, payload.category, payload.title, payload.body),
        )
        post_id = cursor.lastrowid
    return {"id": post_id, "paper_code": code, "category": payload.category, "title": payload.title,
            "body": payload.body, "status": "published"}


@app.get("/api/community/posts/{post_id}")
def community_post_detail(post_id: int, user=Depends(require_user)):
    with get_connection() as conn:
        post = conn.execute(
            """SELECT p.id, p.user_id, p.paper_code, p.category, p.title, p.body, p.status, p.pinned, p.created_at,
                      u.full_name AS author_name,
                      (SELECT COUNT(*) FROM community_post_likes l WHERE l.post_id = p.id) AS like_count,
                      EXISTS(SELECT 1 FROM community_post_likes l WHERE l.post_id = p.id AND l.user_id = ?) AS liked_by_me
               FROM community_posts p JOIN users u ON u.id = p.user_id WHERE p.id = ?""",
            (user["id"], post_id),
        ).fetchone()
        if not post or (post["status"] != "published" and int(post["user_id"]) != int(user["id"]) and user["role"] != "admin"):
            raise HTTPException(status_code=404, detail="Discussion not found")
        replies = conn.execute(
            """SELECT r.id, r.post_id, r.user_id, r.body, r.created_at, u.full_name AS author_name
               FROM community_replies r JOIN users u ON u.id = r.user_id
               WHERE r.post_id = ? AND r.status = 'published' ORDER BY r.created_at""",
            (post_id,),
        ).fetchall()
    post_data = dict(post); post_data["is_owner"] = int(post["user_id"]) == int(user["id"]); post_data["can_moderate"] = user["role"] == "admin"; del post_data["user_id"]
    reply_items = []
    for row in replies:
        item = dict(row); item["is_owner"] = int(row["user_id"]) == int(user["id"]); del item["user_id"]
        reply_items.append(item)
    return {"post": post_data, "replies": reply_items}


@app.post("/api/community/posts/{post_id}/replies", status_code=201)
def community_create_reply(post_id: int, payload: CommunityReplyPayload, user=Depends(require_user)):
    with get_connection() as conn:
        post = conn.execute("SELECT id FROM community_posts WHERE id = ? AND status = 'published'", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Discussion not found")
        cursor = conn.execute("INSERT INTO community_replies(post_id, user_id, body) VALUES (?, ?, ?)", (post_id, user["id"], payload.body))
        conn.execute("UPDATE community_posts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (post_id,))
    return {"id": cursor.lastrowid, "post_id": post_id, "body": payload.body, "status": "published"}


@app.put("/api/community/posts/{post_id}/like")
def community_toggle_like(post_id: int, user=Depends(require_user)):
    with get_connection() as conn:
        post = conn.execute("SELECT id FROM community_posts WHERE id = ? AND status = 'published'", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Discussion not found")
        existing = conn.execute("SELECT 1 FROM community_post_likes WHERE post_id = ? AND user_id = ?", (post_id, user["id"])).fetchone()
        if existing:
            conn.execute("DELETE FROM community_post_likes WHERE post_id = ? AND user_id = ?", (post_id, user["id"]))
            liked = False
        else:
            conn.execute("INSERT OR IGNORE INTO community_post_likes(post_id, user_id) VALUES (?, ?)", (post_id, user["id"]))
            liked = True
        count = conn.execute("SELECT COUNT(*) AS count FROM community_post_likes WHERE post_id = ?", (post_id,)).fetchone()["count"]
    return {"post_id": post_id, "liked": liked, "like_count": count}


@app.delete("/api/community/posts/{post_id}", status_code=204)
def community_remove_own_post(post_id: int, user=Depends(require_user)):
    with get_connection() as conn:
        post = conn.execute("SELECT user_id FROM community_posts WHERE id = ? AND status = 'published'", (post_id,)).fetchone()
        if not post or (int(post["user_id"]) != int(user["id"]) and user["role"] != "admin"):
            raise HTTPException(status_code=404, detail="Discussion not found")
        conn.execute("UPDATE community_posts SET status = 'removed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (post_id,))
    return Response(status_code=204)


@app.post("/api/community/reports", status_code=201)
def community_report(payload: CommunityReportPayload, user=Depends(require_user)):
    with get_connection() as conn:
        if payload.target_type == "post":
            row = conn.execute("SELECT user_id FROM community_posts WHERE id = ? AND status = 'published'", (payload.target_id,)).fetchone()
        else:
            row = conn.execute("SELECT user_id FROM community_replies WHERE id = ? AND status = 'published'", (payload.target_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Content to report was not found")
        if int(row["user_id"]) == int(user["id"]):
            raise HTTPException(status_code=422, detail="You cannot report your own content")
        cursor = conn.execute(
            "INSERT INTO community_reports(reporter_id, target_type, target_id, reason) VALUES (?, ?, ?, ?)",
            (user["id"], payload.target_type, payload.target_id, payload.reason),
        )
    return {"report_id": cursor.lastrowid, "status": "pending"}


@app.get("/api/admin/overview")
def admin_overview(user=Depends(require_admin)):
    with get_connection() as conn:
        users_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        students_count = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'student'").fetchone()["count"]
        admins_count = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin'").fetchone()["count"]
        active_students = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'student' AND is_active = 1").fetchone()["count"]
        posts_count = conn.execute("SELECT COUNT(*) AS count FROM community_posts WHERE status = 'published'").fetchone()["count"]
        pending_reports = conn.execute("SELECT COUNT(*) AS count FROM community_reports WHERE status = 'pending'").fetchone()["count"]
        reviewed_rows = conn.execute("SELECT status, COUNT(*) AS count FROM admin_content_reviews GROUP BY status").fetchall()
    review_counts = {row["status"]: int(row["count"]) for row in reviewed_rows}
    total_content = 0
    for paper in load_papers():
        code = paper["code"]
        total_content += len((load_materials_data(code) or {}).get("materials", []))
        total_content += len((load_practice_data(code) or {}).get("questions", []))
        for path in PYQ_DIR.glob(f"{code}-*.json"):
            try:
                pyq_data = json.loads(path.read_text(encoding="utf-8"))
                total_content += sum(len(session.get("questions", [])) for session in pyq_data.get("sessions", []))
            except (OSError, json.JSONDecodeError):
                continue
    approved_content = review_counts.get("approved", 0)
    rejected_content = review_counts.get("rejected", 0)
    pending_content = max(0, total_content - approved_content - rejected_content)
    return {"users": users_count, "students": students_count, "admins": admins_count, "active_students": active_students,
            "published_posts": posts_count, "pending_reports": pending_reports,
            "total_content_items": total_content, "approved_content_items": approved_content,
            "needs_changes_content_items": review_counts.get("needs_changes", 0),
            "pending_content_reviews": pending_content}


@app.get("/api/admin/users")
def admin_list_users(q: str = Query(default="", max_length=100), status: Literal["all", "active", "inactive"] = "all",
                    page: int = Query(default=1, ge=1), limit: int = Query(default=30, ge=1, le=100), user=Depends(require_admin)):
    clauses = ["1=1"]; params: list[object] = []
    if q.strip():
        pattern = f"%{q.strip()}%"; clauses.append("(full_name LIKE ? OR email LIKE ?)"); params.extend([pattern, pattern])
    if status == "active": clauses.append("is_active = 1")
    elif status == "inactive": clauses.append("is_active = 0")
    where = " AND ".join(clauses)
    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) AS count FROM users WHERE {where}", params).fetchone()["count"]
        rows = conn.execute(f"SELECT id, full_name, email, role, is_active, created_at FROM users WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                            [*params, limit, (page - 1) * limit]).fetchall()
    return {"items": [dict(row) for row in rows], "total": total, "page": page, "limit": limit}


@app.patch("/api/admin/users/{user_id}")
def admin_update_user_status(user_id: int, payload: AdminUserStatusPayload, user=Depends(require_admin)):
    if user_id == user["id"] and not payload.is_active:
        raise HTTPException(status_code=422, detail="You cannot deactivate your own administrator account")
    with get_connection() as conn:
        target = conn.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target or target["role"] != "student":
            raise HTTPException(status_code=404, detail="Student account not found")
        conn.execute("UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (int(payload.is_active), user_id))
        if not payload.is_active:
            conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    return {"user_id": user_id, "is_active": payload.is_active, "sessions_revoked": not payload.is_active}


@app.get("/api/admin/reports")
def admin_list_reports(status: Literal["pending", "resolved", "dismissed", "all"] = "pending",
                       limit: int = Query(default=50, ge=1, le=100), user=Depends(require_admin)):
    where = "1=1" if status == "all" else "r.status = ?"
    params: list[object] = [] if status == "all" else [status]
    with get_connection() as conn:
        rows = conn.execute(
            f"""SELECT r.*, reporter.full_name AS reporter_name,
                CASE WHEN r.target_type = 'post' THEN p.title ELSE substr(reply.body, 1, 120) END AS target_excerpt,
                CASE WHEN r.target_type = 'post' THEN p.status ELSE reply.status END AS target_status
                FROM community_reports r JOIN users reporter ON reporter.id = r.reporter_id
                LEFT JOIN community_posts p ON r.target_type = 'post' AND p.id = r.target_id
                LEFT JOIN community_replies reply ON r.target_type = 'reply' AND reply.id = r.target_id
                WHERE {where} ORDER BY r.created_at DESC LIMIT ?""",
            [*params, limit],
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@app.patch("/api/admin/reports/{report_id}")
def admin_resolve_report(report_id: int, payload: AdminReportResolutionPayload, user=Depends(require_admin)):
    with get_connection() as conn:
        report = conn.execute("SELECT * FROM community_reports WHERE id = ? AND status = 'pending'", (report_id,)).fetchone()
        if not report:
            raise HTTPException(status_code=404, detail="Pending report not found")
        if payload.action in {"hide", "remove"}:
            table = "community_posts" if report["target_type"] == "post" else "community_replies"
            target_status = "hidden" if payload.action == "hide" else "removed"
            conn.execute(f"UPDATE {table} SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (target_status, report["target_id"]))
        conn.execute("UPDATE community_reports SET status = ?, resolution_note = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (payload.status, payload.note.strip(), user["id"], report_id))
    return {"report_id": report_id, "status": payload.status, "action": payload.action}


@app.get("/api/admin/content/catalog")
def admin_content_catalog(user=Depends(require_admin)):
    output = []
    for paper in load_papers():
        code = paper["code"]
        syllabus = load_syllabus_data(code) or {}
        materials = load_materials_data(code) or {}
        practice = load_practice_data(code) or {}
        pyq_count = 0
        for path in PYQ_DIR.glob(f"{code}-*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                pyq_count += sum(len(session.get("questions", [])) for session in data.get("sessions", []))
            except (OSError, json.JSONDecodeError):
                continue
        output.append({"paper_code": code, "paper_name": paper["name"],
                       "syllabus_topics": sum(len(section.get("topics", [])) for section in syllabus.get("sections", [])),
                       "study_notes": len(materials.get("materials", [])),
                       "practice_questions": len(practice.get("questions", [])), "pyq_records": pyq_count,
                       "syllabus_status": syllabus.get("content_status", "pending_import"),
                       "materials_status": materials.get("content_status", "pending_import"),
                       "practice_status": practice.get("editorial_status", "pending_import")})
    return {"items": output}


@app.get("/api/admin/content/review-queue")
def admin_content_review_queue(paper_code: str = "CS", content_type: str = "all", limit: int = Query(default=100, ge=1, le=300), user=Depends(require_admin)):
    code = paper_code.upper()
    if code not in paper_codes():
        raise HTTPException(status_code=404, detail="GATE paper not found")
    if content_type not in {"all", "material", "practice_question", "pyq_answer"}:
        raise HTTPException(status_code=422, detail="Unknown content type")
    candidates: list[dict] = []
    material_data = load_materials_data(code) or {}
    for item in material_data.get("materials", []):
        candidates.append({"paper_code": code, "content_type": "material", "content_id": item["id"], "title": item.get("topic_name", item["id"]),
                           "section_name": item.get("section_name", ""), "source_status": item.get("content_status", "editorial_learning_note")})
    practice_data = load_practice_data(code) or {}
    for item in practice_data.get("questions", []):
        candidates.append({"paper_code": code, "content_type": "practice_question", "content_id": item["id"], "title": item.get("prompt", item["id"]),
                           "section_name": item.get("section_name", ""), "source_status": practice_data.get("editorial_status", "review_required")})
    for path in sorted(PYQ_DIR.glob(f"{code}-*.json"), reverse=True):
        try:
            pyq_data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for session in pyq_data.get("sessions", []):
            for item in session.get("questions", []):
                candidates.append({"paper_code": code, "content_type": "pyq_answer", "content_id": item["id"],
                                   "title": f"{item.get('year', pyq_data.get('year'))} · {item.get('session')} · Question {item.get('question_number')}",
                                   "section_name": item.get("section_name", ""), "source_status": item.get("verification_status", "source_check_required")})
    if content_type != "all":
        candidates = [item for item in candidates if item["content_type"] == content_type]
    with get_connection() as conn:
        reviews = conn.execute("SELECT content_type, content_id, status, note, reviewed_at FROM admin_content_reviews WHERE paper_code = ?", (code,)).fetchall()
    review_map = {(row["content_type"], row["content_id"]): dict(row) for row in reviews}
    for item in candidates:
        review = review_map.get((item["content_type"], item["content_id"]), {})
        item["review_status"] = review.get("status", "pending_review")
        item["review_note"] = review.get("note", "")
        item["reviewed_at"] = review.get("reviewed_at")
    return {"paper_code": code, "items": candidates[:limit], "total_available": len(candidates),
            "notice": "Review status is editorial workflow metadata; approving an item does not independently certify its academic correctness or licensing."}


@app.put("/api/admin/content/reviews/{content_type}/{content_id}")
def admin_update_content_review(content_type: str, content_id: str, payload: AdminContentReviewPayload,
                               paper_code: str = "CS", user=Depends(require_admin)):
    code = paper_code.upper()
    if code not in paper_codes() or content_type not in {"material", "practice_question", "pyq_answer"}:
        raise HTTPException(status_code=404, detail="Content item not found")
    queue = admin_content_review_queue(code, content_type, 300, user)
    candidate = next((item for item in queue["items"] if item["content_id"] == content_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Content item not found")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO admin_content_reviews(paper_code, content_type, content_id, status, note, reviewed_by, reviewed_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(paper_code, content_type, content_id) DO UPDATE SET
                 status = excluded.status, note = excluded.note, reviewed_by = excluded.reviewed_by,
                 reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP""",
            (code, content_type, content_id, payload.status, payload.note.strip(), user["id"]),
        )
    return {"paper_code": code, "content_type": content_type, "content_id": content_id,
            "status": payload.status, "note": payload.note.strip()}


@app.patch("/api/admin/community/posts/{post_id}")
def admin_moderate_post(post_id: int, payload: AdminModerationPayload, user=Depends(require_admin)):
    with get_connection() as conn:
        post = conn.execute("SELECT id FROM community_posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Discussion not found")
        if payload.pinned is None:
            conn.execute("UPDATE community_posts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (payload.status, post_id))
        else:
            conn.execute("UPDATE community_posts SET status = ?, pinned = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (payload.status, int(payload.pinned), post_id))
    return {"post_id": post_id, "status": payload.status, "pinned": payload.pinned}


@app.patch("/api/admin/community/replies/{reply_id}")
def admin_moderate_reply(reply_id: int, payload: AdminModerationPayload, user=Depends(require_admin)):
    with get_connection() as conn:
        reply = conn.execute("SELECT id FROM community_replies WHERE id = ?", (reply_id,)).fetchone()
        if not reply:
            raise HTTPException(status_code=404, detail="Reply not found")
        conn.execute("UPDATE community_replies SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (payload.status, reply_id))
    return {"reply_id": reply_id, "status": payload.status}


# ---------------- Stage 12: analytics, community and administration ----------------


@app.delete("/api/community/replies/{reply_id}", status_code=204)
def community_remove_reply(reply_id: int, user=Depends(require_user)):
    with get_connection() as conn:
        reply = conn.execute("SELECT user_id FROM community_replies WHERE id = ? AND status = 'published'", (reply_id,)).fetchone()
        if not reply or (int(reply["user_id"]) != int(user["id"]) and user["role"] != "admin"):
            raise HTTPException(status_code=404, detail="Reply not found")
        conn.execute("UPDATE community_replies SET status = 'removed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (reply_id,))
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
