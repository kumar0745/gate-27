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
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-test.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "student@example.com", paper_code: str = "CS"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test Student",
            "email": email,
            "password": "GatePathTest2027",
            "paper_code": paper_code,
            "target": "IIT admission",
            "daily_hours": 5,
        },
    )
    assert response.status_code == 201, response.text
    return response


def test_materials_require_login(client):
    response = client.get("/api/materials")
    assert response.status_code == 401


def test_material_catalog_has_all_cs_topics(client):
    register(client)
    response = client.get("/api/materials?paper_code=CS")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["paper_code"] == "CS"
    assert payload["summary"]["total"] == 52
    assert len(payload["items"]) == 52
    assert payload["content_version"] == "1.0.0"


def test_material_detail_contains_learning_sections_and_sources(client):
    register(client)
    response = client.get("/api/materials/CS-08-04?paper_code=CS")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["topic_name"] == "Concurrency and Synchronization"
    assert payload["concepts"]
    assert payload["worked_example"]["kind"] == "illustrative_not_official_pyq"
    assert payload["formula_cards"]
    assert payload["resources"]
    assert payload["progress"]["status"] == "not_started"


def test_material_progress_bookmark_and_private_note_persist(client):
    register(client)
    payload = {
        "status": "completed",
        "bookmarked": True,
        "personal_note": "Review semaphore invariants before the test.",
    }
    response = client.patch("/api/materials/CS-08-04/progress?paper_code=CS", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "completed"
    assert response.json()["bookmarked"] is True
    saved = client.get("/api/materials/CS-08-04?paper_code=CS").json()["progress"]
    assert saved["personal_note"] == payload["personal_note"]


def test_other_student_cannot_see_another_students_progress(client):
    register(client, "first@example.com")
    client.patch(
        "/api/materials/CS-01-01/progress?paper_code=CS",
        json={"status": "completed", "bookmarked": True},
    )
    client.post("/api/auth/logout", json={})
    register(client, "second@example.com")
    response = client.get("/api/materials/CS-01-01?paper_code=CS")
    assert response.status_code == 200
    assert response.json()["progress"]["status"] == "not_started"
    assert response.json()["progress"]["bookmarked"] is False


def test_material_filters_work(client):
    register(client)
    response = client.get("/api/materials?paper_code=CS&section_code=CS-08&q=deadlock")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["section_code"] == "CS-08" for item in items)
    assert any("Deadlock" in item["topic_name"] for item in items)


def test_missing_content_for_another_paper_is_explicit(client):
    register(client, paper_code="DA")
    response = client.get("/api/materials?paper_code=DA")
    assert response.status_code == 200
    payload = response.json()
    assert payload["content_status"] == "awaiting_content_import"
    assert payload["items"] == []
    assert payload["official_syllabus_url"].endswith("DA_GATE2027_Syllabus.pdf")


def test_syllabus_endpoint_serves_cs_structure_and_progress(client):
    register(client)
    response = client.get("/api/syllabus?paper_code=CS")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["verified"] is True
    assert len(payload["sections"]) == 10
    assert sum(len(section["topics"]) for section in payload["sections"]) == 52
    assert payload["common_section"]["code"] == "GA"


def test_dashboard_reflects_completed_material_topics(client):
    register(client)
    client.patch("/api/materials/CS-01-01/progress?paper_code=CS", json={"status": "completed"})
    payload = client.get("/api/dashboard").json()
    assert payload["syllabus_topic_completed"] == 1
    assert payload["syllabus_topic_total"] == 52
    assert payload["syllabus_progress_percent"] == 2


def test_invalid_topic_and_empty_update_are_rejected(client):
    register(client)
    assert client.get("/api/materials/CS-99-99?paper_code=CS").status_code == 404
    assert client.patch("/api/materials/CS-01-01/progress?paper_code=CS", json={}).status_code == 400


def test_material_ids_match_the_official_topic_import():
    import json

    syllabus_path = ROOT / "backend/app/data/syllabi/CS-GATE-2027.json"
    material_path = ROOT / "backend/app/data/materials/CS-GATE-2027.json"
    syllabus = json.loads(syllabus_path.read_text(encoding="utf-8"))
    materials = json.loads(material_path.read_text(encoding="utf-8"))
    syllabus_ids = {topic["id"] for section in syllabus["sections"] for topic in section["topics"]}
    material_ids = {item["id"] for item in materials["materials"]}
    assert len(material_ids) == 52
    assert material_ids == syllabus_ids


def test_workspace_assets_expose_the_study_library(client):
    html = client.get("/static/index.html")
    js = client.get("/static/app.js")
    css = client.get("/static/app.css")
    assert html.status_code == 200
    assert "Study materials" in html.text
    assert js.status_code == 200
    assert "async function renderResources" in js.text
    assert "function renderMaterialDetail" in js.text
    assert css.status_code == 200
    assert ".material-card" in css.text


def test_completed_progress_is_reflected_in_syllabus_topic(client):
    register(client)
    client.patch("/api/materials/CS-01-01/progress?paper_code=CS", json={"status": "completed"})
    payload = client.get("/api/syllabus?paper_code=CS").json()
    topic = next(
        topic
        for section in payload["sections"]
        for topic in section["topics"]
        if topic["id"] == "CS-01-01"
    )
    assert topic["status"] == "completed"
