from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import database
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-pyq-test.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "pyq@example.com", paper_code: str = "CS"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "PYQ Student",
            "email": email,
            "password": "GatePathTest2027",
            "paper_code": paper_code,
            "target": "IIT admission",
            "daily_hours": 5,
        },
    )
    assert response.status_code == 201, response.text
    return response


def test_pyq_endpoints_require_authentication(client):
    assert client.get("/api/pyq/catalog?paper_code=CS").status_code == 401
    assert client.get("/api/pyq/questions?paper_code=CS").status_code == 401
    assert client.get("/api/pyq/summary?paper_code=CS").status_code == 401


def test_catalog_includes_official_sources_and_two_cs_sessions(client):
    register(client)
    payload = client.get("/api/pyq/catalog?paper_code=CS").json()
    assert payload["content_status"] == "interactive_metadata_imported"
    assert payload["interactive_question_count"] == 130
    assert {session["session"] for session in payload["sessions"]} == {"CS-1", "CS-2"}
    years = {str(item["year"]) for item in payload["archive_sources"]}
    assert {"2026", "2025", "2024", "2007–2025"}.issubset(years)


def test_pyq_list_has_verified_metadata_but_does_not_leak_answer_keys(client):
    register(client)
    response = client.get("/api/pyq/questions?paper_code=CS&year=2026")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["count"] == 130
    assert payload["content_status"] == "official_keys_metadata_imported"
    item = next(item for item in payload["items"] if item["id"] == "G26-CS-1-Q16")
    assert item["question_type"] == "MCQ"
    assert item["marks"] == 1
    assert item["topic_id"] == "CS-03-06"
    assert "answer_key" not in item
    assert "answer_range" not in item


def test_question_detail_hides_key_until_student_submits(client):
    register(client)
    response = client.get("/api/pyq/questions/G26-CS-1-Q16")
    assert response.status_code == 200
    payload = response.json()
    assert payload["question_text_hosted"] is False
    assert payload["paper_url"].endswith("/CS1.pdf")
    assert "verified_answer" not in payload
    assert payload["solution"] is None


def test_mcq_correct_answer_awards_full_marks_and_returns_editorial_solution(client):
    register(client)
    response = client.post("/api/pyq/questions/G26-CS-1-Q16/attempt", json={"answer": "b", "spent_seconds": 42})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["is_correct"] is True
    assert payload["awarded_marks"] == 1.0
    assert payload["correct_answer"] == "B"
    assert payload["solution_status"] == "editorial_explanation_available"
    assert "Read-after-write" in payload["solution"]["title"]


def test_mcq_wrong_answer_applies_one_third_negative_marking(client):
    register(client)
    response = client.post("/api/pyq/questions/G26-CS-1-Q16/attempt", json={"answer": "A"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_correct"] is False
    assert payload["awarded_marks"] == pytest.approx(-1 / 3)


def test_msq_requires_exact_option_set_without_partial_marking(client):
    register(client)
    partial = client.post("/api/pyq/questions/G26-CS-1-Q19/attempt", json={"answer": "A,C"})
    assert partial.status_code == 200
    assert partial.json()["is_correct"] is False
    assert partial.json()["awarded_marks"] == 0
    exact = client.post("/api/pyq/questions/G26-CS-1-Q19/attempt", json={"answer": "D;A;C"})
    assert exact.status_code == 200
    assert exact.json()["is_correct"] is True
    assert exact.json()["awarded_marks"] == 1


def test_nat_checks_official_inclusive_answer_range(client):
    register(client)
    inside = client.post("/api/pyq/questions/G26-CS-1-Q58/attempt", json={"answer": "4.25"})
    outside = client.post("/api/pyq/questions/G26-CS-1-Q58/attempt", json={"answer": "4.3"})
    assert inside.json()["is_correct"] is True
    assert inside.json()["awarded_marks"] == 2
    assert inside.json()["answer_range"] == [4.24, 4.26]
    assert outside.json()["is_correct"] is False
    assert outside.json()["awarded_marks"] == 0


def test_bookmark_and_attempt_history_are_persisted(client):
    register(client)
    question_id = "G26-CS-1-Q18"
    saved = client.put(f"/api/pyq/bookmarks/{question_id}", json={"bookmarked": True})
    assert saved.status_code == 200
    client.post(f"/api/pyq/questions/{question_id}/attempt", json={"answer": "D", "spent_seconds": 31})
    history = client.get("/api/pyq/history").json()
    item = next(item for item in history["items"] if item["id"] == question_id)
    assert item["bookmarked"] is True
    assert item["last_attempt"]["is_correct"] is True
    detail = client.get(f"/api/pyq/questions/{question_id}").json()
    assert detail["verified_answer"] == "D"
    assert detail["solution"]


def test_bookmark_filter_and_remove_work(client):
    register(client)
    question_id = "G26-CS-1-Q16"
    client.put(f"/api/pyq/bookmarks/{question_id}", json={"bookmarked": True})
    payload = client.get("/api/pyq/questions?paper_code=CS&bookmarked_only=true").json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == question_id
    assert payload["items"][0]["bookmarked"] is True
    removed = client.put(f"/api/pyq/bookmarks/{question_id}", json={"bookmarked": False})
    assert removed.json()["bookmarked"] is False
    assert client.get("/api/pyq/questions?paper_code=CS&bookmarked_only=true").json()["count"] == 0


def test_filters_support_session_type_section_and_topic(client):
    register(client)
    response = client.get("/api/pyq/questions?paper_code=CS&session=CS-1&question_type=MCQ&section_code=CS-1&topic_id=CS-03-06")
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["id"] for item in items] == ["G26-CS-1-Q16"]
    combined = client.get("/api/pyq/questions?paper_code=CS&section_code=CS").json()
    assert combined["count"] == 110
    assert all(item["source_section_code"] != "GA" for item in combined["items"])


def test_non_imported_year_and_paper_show_honest_pending_state(client):
    register(client)
    older = client.get("/api/pyq/questions?paper_code=CS&year=2025").json()
    other_paper = client.get("/api/pyq/questions?paper_code=DA&year=2026").json()
    assert older["content_status"] == "awaiting_interactive_import"
    assert older["items"] == []
    assert other_paper["content_status"] == "awaiting_interactive_import"
    assert other_paper["items"] == []


def test_summary_uses_latest_attempt_per_question_for_accuracy(client):
    register(client)
    question_id = "G26-CS-1-Q16"
    client.post(f"/api/pyq/questions/{question_id}/attempt", json={"answer": "A"})
    client.post(f"/api/pyq/questions/{question_id}/attempt", json={"answer": "B"})
    summary = client.get("/api/pyq/summary?paper_code=CS").json()
    assert summary["total_questions"] == 130
    assert summary["attempt_count"] == 2
    assert summary["attempted_questions"] == 1
    assert summary["correct_questions_latest"] == 1
    assert summary["accuracy_percent"] == 100


def test_students_cannot_see_another_students_pyq_records(client):
    register(client, "first-pyq@example.com")
    client.put("/api/pyq/bookmarks/G26-CS-1-Q16", json={"bookmarked": True})
    client.post("/api/pyq/questions/G26-CS-1-Q16/attempt", json={"answer": "B"})
    client.post("/api/auth/logout", json={})
    register(client, "second-pyq@example.com")
    question = client.get("/api/pyq/questions/G26-CS-1-Q16").json()
    summary = client.get("/api/pyq/summary").json()
    assert question["bookmarked"] is False
    assert question["last_attempt"] is None
    assert summary["attempt_count"] == 0
    assert summary["bookmarked_questions"] == 0


def test_invalid_answer_format_and_unknown_question_are_rejected(client):
    register(client)
    assert client.post("/api/pyq/questions/G26-CS-1-Q16/attempt", json={"answer": "E"}).status_code == 422
    assert client.post("/api/pyq/questions/G26-CS-1-Q32/attempt", json={"answer": "not-a-number"}).status_code == 422
    assert client.post("/api/pyq/questions/G26-CS-1-Q19/attempt", json={"answer": "A,A"}).status_code == 422
    assert client.get("/api/pyq/questions/unknown").status_code == 404
    assert client.put("/api/pyq/bookmarks/unknown", json={"bookmarked": True}).status_code == 404


def test_seed_data_has_130_source_verified_questions_and_safe_metadata():
    path = ROOT / "backend/app/data/pyq/CS-2026.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    questions = [question for session in dataset["sessions"] for question in session["questions"]]
    assert len(questions) == 130
    assert len({question["id"] for question in questions}) == 130
    assert all(question["verification_status"] == "official_answer_key_verified" for question in questions)
    assert all(question["question_text_hosted"] is False for question in questions)
    assert all(question["answer_key_url"].endswith(("CS1_Keys.pdf", "CS2_Keys.pdf")) for question in questions)


def test_workspace_contains_live_pyq_bank_and_controls(client):
    register(client)
    html = client.get("/static/index.html")
    js = client.get("/static/app.js")
    css = client.get("/static/app.css")
    assert html.status_code == 200 and 'data-view="questions"' in html.text
    assert js.status_code == 200
    for feature in ("async function renderPyqBank", "submitPyqAnswer", "togglePyqBookmark", "pyq-year-filter", "Open official question paper"):
        assert feature in js.text
    assert css.status_code == 200 and ".pyq-question-grid" in css.text
