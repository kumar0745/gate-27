from __future__ import annotations

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
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-practice-test.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "practice@example.com", paper_code: str = "CS"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Practice Student",
            "email": email,
            "password": "GatePathTest2027",
            "paper_code": paper_code,
            "target": "IIT admission",
            "daily_hours": 5,
        },
    )
    assert response.status_code == 201, response.text
    return response


def create_session(client: TestClient, **payload):
    response = client.post("/api/practice/sessions", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_practice_endpoints_require_authentication(client):
    assert client.get("/api/practice/catalog?paper_code=CS").status_code == 401
    assert client.get("/api/practice/questions?paper_code=CS").status_code == 401
    assert client.get("/api/practice/daily-challenge?paper_code=CS").status_code == 401
    assert client.post("/api/practice/sessions", json={}).status_code == 401


def test_catalog_maps_original_practice_pilot_to_official_cs_syllabus(client):
    register(client)
    payload = client.get("/api/practice/catalog?paper_code=CS").json()
    assert payload["content_status"] == "original_practice_pilot"
    assert payload["total_questions"] == 30
    assert len(payload["sections"]) == 10
    assert sum(section["question_count"] for section in payload["sections"]) == 30
    assert payload["editorial_status"].startswith("AI-drafted pilot")
    assert payload["difficulty_counts"] == {"Beginner": 18, "Intermediate": 7, "Advanced": 5}
    assert payload["question_type_counts"] == {"MCQ": 11, "NAT": 13, "MSQ": 6}


def test_practice_list_filters_questions_without_leaking_answers(client):
    register(client)
    response = client.get("/api/practice/questions?paper_code=CS&section_code=CS-08&difficulty=Intermediate&question_type=NAT")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    item = payload["items"][0]
    assert item["id"] == "GP-CS-022"
    assert item["topic_id"] == "CS-08-06"
    assert "answer_key" not in item
    assert "solution" not in item


def test_unknown_practice_papers_show_pending_content(client):
    register(client, paper_code="DA")
    catalog = client.get("/api/practice/catalog?paper_code=DA").json()
    questions = client.get("/api/practice/questions?paper_code=DA").json()
    assert catalog["content_status"] == "awaiting_practice_import"
    assert questions["content_status"] == "awaiting_practice_import"
    assert questions["items"] == []
    assert client.post("/api/practice/sessions", json={"paper_code": "DA"}).status_code == 409


def test_topic_session_only_contains_matching_topic_and_hides_answers(client):
    register(client)
    session = create_session(client, mode="topic", paper_code="CS", topic_id="CS-01-01", question_count=10)
    assert session["question_count"] == 1
    assert session["status"] == "active"
    question = session["questions"][0]
    assert question["topic_id"] == "CS-01-01"
    assert "answer_key" not in question
    assert "solution" not in question
    assert session["duration_seconds"] == 900


def test_mcq_correct_and_wrong_answers_apply_gate_style_scoring(client):
    register(client)
    correct_session = create_session(client, mode="topic", topic_id="CS-01-01")
    correct = client.post(
        f"/api/practice/sessions/{correct_session['id']}/attempt",
        json={"question_id": "GP-CS-001", "answer": "c", "spent_seconds": 18},
    )
    assert correct.status_code == 200, correct.text
    assert correct.json()["is_correct"] is True
    assert correct.json()["awarded_marks"] == 1

    wrong_session = create_session(client, mode="topic", topic_id="CS-02-01")
    wrong = client.post(
        f"/api/practice/sessions/{wrong_session['id']}/attempt",
        json={"question_id": "GP-CS-004", "answer": "A"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["is_correct"] is False
    assert wrong.json()["awarded_marks"] == pytest.approx(-1 / 3)
    assert wrong.json()["solution"]["steps"]


def test_msq_requires_exact_option_set_without_partial_marks(client):
    register(client)
    session = create_session(client, mode="topic", topic_id="CS-02-02")
    wrong = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-005", "answer": "A,B"})
    assert wrong.status_code == 200
    assert wrong.json()["is_correct"] is False
    assert wrong.json()["awarded_marks"] == 0

    second = create_session(client, mode="topic", topic_id="CS-02-02")
    right = client.post(f"/api/practice/sessions/{second['id']}/attempt", json={"question_id": "GP-CS-005", "answer": "C,A,B"})
    assert right.status_code == 200
    assert right.json()["is_correct"] is True
    assert right.json()["awarded_marks"] == 2


def test_nat_accepts_inclusive_range_and_rejects_outside(client):
    register(client)
    session = create_session(client, mode="topic", topic_id="CS-01-02")
    accepted = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-002", "answer": "1"})
    assert accepted.status_code == 200
    assert accepted.json()["is_correct"] is True

    session2 = create_session(client, mode="topic", topic_id="CS-01-02")
    rejected = client.post(f"/api/practice/sessions/{session2['id']}/attempt", json={"question_id": "GP-CS-002", "answer": "2"})
    assert rejected.status_code == 200
    assert rejected.json()["is_correct"] is False
    assert rejected.json()["awarded_marks"] == 0


def test_attempt_must_belong_to_session_and_cannot_be_submitted_twice(client):
    register(client)
    session = create_session(client, mode="topic", topic_id="CS-01-01")
    not_in_session = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-004", "answer": "B"})
    assert not_in_session.status_code == 404
    submitted = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-001", "answer": "C"})
    assert submitted.status_code == 200
    duplicate = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-001", "answer": "A"})
    assert duplicate.status_code == 409


def test_custom_session_filters_and_duration_are_applied(client):
    register(client)
    session = create_session(client, mode="custom", section_code="CS-10", difficulty="Beginner", question_type="MCQ", question_count=8, duration_minutes=7)
    assert session["question_count"] == 1
    assert session["duration_seconds"] == 420
    assert all(item["section_code"] == "CS-10" for item in session["questions"])


def test_daily_challenge_is_stable_and_can_be_completed(client):
    register(client)
    before = client.get("/api/practice/daily-challenge?paper_code=CS").json()
    again = client.get("/api/practice/daily-challenge?paper_code=CS").json()
    assert before["question_count"] == 5
    assert [q["id"] for q in before["questions"]] == [q["id"] for q in again["questions"]]
    session = create_session(client, mode="daily", paper_code="CS")
    assert session["question_count"] == 5
    for question in session["questions"]:
        # Deliberately skip answers; finishing should still record a transparent result.
        continue
    result = client.post(f"/api/practice/sessions/{session['id']}/finish").json()
    assert result["status"] == "completed"
    assert result["attempted_count"] == 0
    after = client.get("/api/practice/daily-challenge?paper_code=CS").json()
    assert after["completed"] is True


def test_session_finish_and_summary_include_topic_weaknesses(client):
    register(client)
    first = create_session(client, mode="topic", topic_id="CS-02-01")
    client.post(f"/api/practice/sessions/{first['id']}/attempt", json={"question_id": "GP-CS-004", "answer": "A"})
    finished = client.post(f"/api/practice/sessions/{first['id']}/finish").json()
    assert finished["status"] == "completed"
    assert finished["attempted_count"] == 1
    assert finished["awarded_marks"] == pytest.approx(-1 / 3)
    summary = client.get("/api/practice/summary?paper_code=CS").json()
    assert summary["attempted_questions"] == 1
    assert summary["accuracy_percent"] == 0
    assert summary["weak_topics"][0]["topic_id"] == "CS-02-01"
    assert summary["recent_mistakes"][0]["question_id"] == "GP-CS-004"


def test_get_session_reports_answers_only_after_submission(client):
    register(client)
    session = create_session(client, mode="topic", topic_id="CS-01-01")
    initial = client.get(f"/api/practice/sessions/{session['id']}").json()
    assert initial["questions"][0].get("result") is None
    client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": "GP-CS-001", "answer": "C"})
    updated = client.get(f"/api/practice/sessions/{session['id']}").json()
    assert updated["questions"][0]["result"]["correct_answer"] == "C"
    assert updated["questions"][0]["result"]["solution"]


def test_student_cannot_access_another_students_practice_session(client):
    register(client, "first-practice@example.com")
    session = create_session(client, mode="topic", topic_id="CS-01-01")
    client.post("/api/auth/logout", json={})
    register(client, "second-practice@example.com")
    assert client.get(f"/api/practice/sessions/{session['id']}").status_code == 404
    assert client.post(f"/api/practice/sessions/{session['id']}/finish").status_code == 404
    summary = client.get("/api/practice/summary?paper_code=CS").json()
    assert summary["attempted_questions"] == 0
    assert summary["sessions_total"] == 0


def test_practice_data_has_unique_ids_and_syllabus_topic_mapping():
    import json

    data = json.loads((ROOT / "backend/app/data/practice/CS-GATE-2027.json").read_text(encoding="utf-8"))
    syllabus = json.loads((ROOT / "backend/app/data/syllabi/CS-GATE-2027.json").read_text(encoding="utf-8"))
    topic_ids = {topic["id"] for section in syllabus["sections"] for topic in section["topics"]}
    questions = data["questions"]
    assert len(questions) == 30
    assert len({question["id"] for question in questions}) == 30
    assert all(question["topic_id"] in topic_ids for question in questions)
    assert all(question["id"].startswith("GP-CS-") for question in questions)
    assert "not official GATE questions" in data["content_origin"]


def test_workspace_contains_practice_engine_and_timed_player(client):
    register(client)
    html = client.get("/static/index.html").text
    js = client.get("/static/app.js").text
    css = client.get("/static/app.css").text
    assert 'data-view="practice"' in html
    for feature in ("async function renderPractice", "startPracticeSession", "submitPracticeAnswer", "finishPracticeSession", "practice-countdown"):
        assert feature in js
    assert ".practice-question-card" in css


def test_expired_session_is_server_enforced_and_persisted(client):
    register(client)
    session = create_session(client, mode="topic", topic_id="CS-01-01")
    with database.get_connection() as conn:
        conn.execute("UPDATE practice_sessions SET expires_at = 0 WHERE id = ?", (session["id"],))
    expired = client.post(
        f"/api/practice/sessions/{session['id']}/attempt",
        json={"question_id": "GP-CS-001", "answer": "C"},
    )
    assert expired.status_code == 410
    detail = client.get(f"/api/practice/sessions/{session['id']}").json()
    assert detail["status"] == "expired"
    assert detail["result"]["attempted_count"] == 0
