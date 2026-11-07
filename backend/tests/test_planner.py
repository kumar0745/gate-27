from __future__ import annotations

import sys
from datetime import date, timedelta
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
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-planner-test.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "planner@example.com", paper_code: str = "CS", daily_hours: int = 5):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Planner Student",
            "email": email,
            "password": "GatePathTest2027",
            "paper_code": paper_code,
            "target": "IIT admission",
            "daily_hours": daily_hours,
        },
    )
    assert response.status_code == 201, response.text
    return response


def create_plan(client, **payload):
    response = client.post("/api/planner/plans", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_planner_requires_authentication(client):
    assert client.get("/api/planner/overview").status_code == 401
    assert client.post("/api/planner/plans", json={"plan_days": 30}).status_code == 401
    assert client.post("/api/planner/tasks", json={"title": "Study"}).status_code == 401


def test_create_30_day_plan_uses_profile_hours_and_imported_cs_topics(client):
    register(client, daily_hours=5)
    plan = create_plan(client, plan_days=30, start_date="2026-11-06")
    assert plan["paper_code"] == "CS"
    assert plan["daily_hours"] == 5
    assert plan["planned_topic_count"] == 56
    assert plan["unplanned_topic_count"] == 0
    assert plan["task_count"] > 100
    overview = client.get("/api/planner/overview?selected_date=2026-11-06").json()
    assert overview["plan"]["id"] == plan["id"]
    assert overview["plan"]["completion_percent"] == 0
    assert overview["selected_day_tasks"]
    assert {item["task_type"] for item in overview["selected_day_tasks"]} & {"learn", "practice"}


def test_one_hour_plan_exposes_topics_that_do_not_fit_in_horizon(client):
    register(client, daily_hours=1)
    plan = create_plan(client, plan_days=30, daily_hours=1)
    assert plan["planned_topic_count"] == 18
    assert plan["unplanned_topic_count"] == 38
    assert "remain outside this plan" in plan["capacity_note"]
    with database.get_connection() as conn:
        loads = conn.execute(
            "SELECT scheduled_date, SUM(duration_minutes) AS minutes FROM planner_tasks WHERE user_id = 1 GROUP BY scheduled_date"
        ).fetchall()
    assert max((row["minutes"] for row in loads), default=0) <= 60


def test_plan_duration_is_limited_to_30_60_or_90_days(client):
    register(client)
    response = client.post("/api/planner/plans", json={"plan_days": 45})
    assert response.status_code == 422


def test_non_cs_papers_cannot_receive_a_planner(client):
    register(client)
    assert client.post("/api/planner/plans", json={"paper_code":"DA", "plan_days":30}).status_code == 404


def test_regenerating_plan_archives_previous_plan(client):
    register(client)
    first = create_plan(client, plan_days=30)
    second = create_plan(client, plan_days=60)
    assert first["id"] != second["id"]
    overview = client.get("/api/planner/overview").json()
    assert overview["plan"]["id"] == second["id"]


def test_task_completion_updates_plan_progress_and_topic_learning_state(client):
    register(client)
    create_plan(client, plan_days=30)
    overview = client.get("/api/planner/overview").json()
    learn_task = next(item for item in overview["selected_day_tasks"] if item["task_type"] == "learn")
    updated = client.patch(f"/api/planner/tasks/{learn_task['id']}", json={"status": "completed"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "completed"
    with database.get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM student_material_progress WHERE user_id = 1 AND paper_code = 'CS' AND topic_id = ?",
            (learn_task["topic_id"],),
        ).fetchone()
    assert row and row["status"] == "in_progress"
    summary = client.get("/api/planner/overview").json()["plan"]
    assert summary["completed_count"] == 1


def test_revision_completion_schedules_next_spaced_review(client):
    register(client)
    create_plan(client, plan_days=60)
    overview = client.get("/api/planner/overview").json()
    first_revision = next(item for item in overview["upcoming_tasks"] if item["task_type"] == "revision")
    response = client.patch(f"/api/planner/tasks/{first_revision['id']}", json={"status": "completed", "review_quality": "good"})
    assert response.status_code == 200
    with database.get_connection() as conn:
        queue = conn.execute(
            "SELECT * FROM planner_revision_queue WHERE user_id = 1 AND paper_code = 'CS' AND topic_id = ?",
            (first_revision["topic_id"],),
        ).fetchone()
    assert queue["review_count"] == 1
    assert queue["interval_days"] == 4
    assert date.fromisoformat(queue["due_date"]) >= date.today() + timedelta(days=4)


def test_revision_quality_again_uses_short_interval(client):
    register(client)
    create_plan(client, plan_days=60)
    overview = client.get("/api/planner/overview").json()
    first_revision = next(item for item in overview["upcoming_tasks"] if item["task_type"] == "revision")
    client.patch(f"/api/planner/tasks/{first_revision['id']}", json={"status": "completed", "review_quality": "again"})
    with database.get_connection() as conn:
        queue = conn.execute("SELECT * FROM planner_revision_queue WHERE user_id = 1 AND topic_id = ?", (first_revision["topic_id"],)).fetchone()
    assert queue["interval_days"] == 1


def test_custom_task_is_created_for_active_plan(client):
    register(client)
    create_plan(client, plan_days=30)
    response = client.post("/api/planner/tasks", json={"title": "Revise graph algorithms", "subject": "Algorithms", "duration_minutes": 45})
    assert response.status_code == 201
    assert response.json()["source"] == "manual"
    assert response.json()["task_type"] == "custom"


def test_custom_task_requires_active_plan(client):
    register(client)
    response = client.post("/api/planner/tasks", json={"title": "Revise graphs"})
    assert response.status_code == 409


def test_overdue_tasks_can_be_rescheduled_within_next_week(client):
    register(client, daily_hours=5)
    old_start = (date.today() - timedelta(days=5)).isoformat()
    create_plan(client, plan_days=30, start_date=old_start)
    response = client.post("/api/planner/reschedule-overdue")
    assert response.status_code == 200
    assert response.json()["rescheduled_count"] > 0
    overview = client.get("/api/planner/overview").json()
    assert all(task["scheduled_date"] >= date.today().isoformat() for task in overview["upcoming_tasks"] if task["status"] == "pending")


def test_students_cannot_read_or_update_another_students_plan_tasks(client):
    register(client, "first@planner.test")
    plan = create_plan(client, plan_days=30)
    task_id = client.get("/api/planner/overview").json()["selected_day_tasks"][0]["id"]
    client.post("/api/auth/logout", json={})
    register(client, "second@planner.test")
    assert client.get("/api/planner/overview").json()["plan"] is None
    assert client.patch(f"/api/planner/tasks/{task_id}", json={"status": "completed"}).status_code == 404
    assert plan["id"] != 0


def test_overview_returns_weak_topics_from_latest_attempts(client):
    register(client)
    session = client.post("/api/practice/sessions", json={"mode": "topic", "topic_id": "CS-01-01", "question_count": 5}).json()
    question = session["questions"][0]
    wrong_answer = "A" if question.get("answer_key") != "A" else "B"
    client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": question["id"], "answer": wrong_answer})
    create_plan(client, plan_days=30)
    overview = client.get("/api/planner/overview").json()
    assert any(topic["topic_id"] == "CS-01-01" for topic in overview["weak_topics"])


def test_overview_selected_date_returns_tasks_for_that_day(client):
    register(client)
    create_plan(client, plan_days=30, start_date="2026-11-06")
    response = client.get("/api/planner/overview?selected_date=2026-11-07")
    assert response.status_code == 200
    assert response.json()["selected_date"] == "2026-11-07"


def test_revision_queue_and_plan_data_are_owner_scoped(client):
    register(client, "owner@planner.test")
    create_plan(client, plan_days=30)
    first = client.get("/api/planner/overview").json()
    assert first["revision_due"]
    client.post("/api/auth/logout", json={})
    register(client, "other@planner.test")
    second = client.get("/api/planner/overview").json()
    assert second["plan"] is None
    assert second["revision_due"] == []


def test_planner_reserves_weekly_mock_days_and_respects_daily_capacity(client):
    register(client, daily_hours=5)
    create_plan(client, plan_days=30, daily_hours=5, start_date=date.today().isoformat())
    with database.get_connection() as conn:
        loads = conn.execute(
            "SELECT scheduled_date, SUM(duration_minutes) AS minutes FROM planner_tasks WHERE user_id = 1 GROUP BY scheduled_date"
        ).fetchall()
        for row in loads:
            assert row["minutes"] <= 5 * 60
        mock_day = (date.today() + timedelta(days=6)).isoformat()
        types = {row["task_type"] for row in conn.execute(
            "SELECT task_type FROM planner_tasks WHERE user_id = 1 AND scheduled_date = ?", (mock_day,)
        ).fetchall()}
    assert "mock" in types
    assert "learn" not in types
    assert "practice" not in types


def test_planner_rejects_non_cs_paper_filters(client):
    register(client)
    assert client.get("/api/planner/overview?paper_code=DA").status_code == 404
