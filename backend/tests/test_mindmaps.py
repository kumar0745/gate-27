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
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-mindmaps.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "mindmap@example.com", paper_code: str = "CS"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Mind Map Student",
            "email": email,
            "password": "GatePathTest2027",
            "paper_code": paper_code,
            "target": "IIT admission",
            "daily_hours": 5,
        },
    )
    assert response.status_code == 201, response.text
    return response


def test_mindmaps_require_authentication(client):
    assert client.get("/api/mindmaps?paper_code=CS").status_code == 401


def test_default_mindmap_loads_first_cs_subject(client):
    register(client)
    response = client.get("/api/mindmaps?paper_code=CS")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["paper_code"] == "CS"
    assert payload["active_section"]["code"] == "CS-01"
    assert payload["summary"]["topics"] == 4
    assert payload["summary"]["subtopics"] > 0
    assert payload["nodes"][0]["type"] == "root"


def test_subject_graph_contains_topic_and_subtopic_hierarchy(client):
    register(client)
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-02").json()
    node_types = [node["type"] for node in payload["nodes"]]
    assert payload["active_section"]["name"] == "Digital Logic"
    assert node_types.count("topic") == 3
    assert node_types.count("subtopic") == 8
    assert len(payload["edges"]) == 11


def test_topic_nodes_link_to_available_study_notes(client):
    register(client)
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-08").json()
    topic = next(node for node in payload["nodes"] if node.get("topic_id") == "CS-08-04")
    assert topic["label"] == "Concurrency and Synchronization"
    assert topic["note_available"] is True
    assert topic["status"] == "not_started"


def test_subtopics_have_parent_topic_references(client):
    register(client)
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-08").json()
    node = next(node for node in payload["nodes"] if node["id"] == "CS-08-04:sub:1")
    assert node["type"] == "subtopic"
    assert node["parent_id"] == "CS-08-04"
    assert node["label"] == "Concurrency"


def test_external_prerequisites_resolve_to_other_cs_subjects(client):
    register(client)
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-05").json()
    relations = payload["relationships"]
    relation = next(item for item in relations if item["topic_id"] == "CS-05-01")
    assert relation["prerequisite_id"] == "CS-04-03"
    assert relation["prerequisite_name"] == "Linear Data Structures"
    assert relation["section_code"] == "CS-04"
    assert relation["available_in_map"] is False


def test_intra_subject_prerequisite_edges_are_included_when_present(client):
    register(client)
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-07").json()
    assert any(edge["type"] == "prerequisite" for edge in payload["edges"])


def test_invalid_subject_code_returns_not_found(client):
    register(client)
    assert client.get("/api/mindmaps?paper_code=CS&section_code=CS-99").status_code == 404


def test_unimported_paper_has_explicit_pending_state(client):
    register(client, paper_code="DA")
    response = client.get("/api/mindmaps?paper_code=DA")
    assert response.status_code == 200
    payload = response.json()
    assert payload["content_status"] == "awaiting_structured_import"
    assert payload["nodes"] == []
    assert payload["official_syllabus_url"].endswith("DA_GATE2027_Syllabus.pdf")


def test_student_progress_is_reflected_in_mindmap_nodes(client):
    register(client)
    client.patch(
        "/api/materials/CS-08-04/progress?paper_code=CS",
        json={"status": "completed", "bookmarked": True},
    )
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-08").json()
    node = next(node for node in payload["nodes"] if node.get("topic_id") == "CS-08-04")
    assert node["status"] == "completed"
    assert node["bookmarked"] is True


def test_user_progress_is_not_shared_between_students(client):
    register(client, "first-mindmap@example.com")
    client.patch("/api/materials/CS-08-04/progress?paper_code=CS", json={"status": "completed"})
    client.post("/api/auth/logout", json={})
    register(client, "second-mindmap@example.com")
    payload = client.get("/api/mindmaps?paper_code=CS&section_code=CS-08").json()
    node = next(node for node in payload["nodes"] if node.get("topic_id") == "CS-08-04")
    assert node["status"] == "not_started"



def test_workspace_includes_interactive_mindmap_controls(client):
    register(client)
    html = client.get("/static/index.html")
    js = client.get("/static/app.js")
    css = client.get("/static/app.css")
    assert html.status_code == 200
    assert 'data-view="mindmaps"' in html.text
    assert js.status_code == 200
    for feature in ("async function renderMindmaps", "buildMindmapSvg", "downloadMindmapSvg", "mindmap-zoom-in", "open-mindmap-prerequisite"):
        assert feature in js.text
    assert css.status_code == 200
    assert ".mindmap-workspace" in css.text
    assert ".mindmap-svg-node" in css.text
