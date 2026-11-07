from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import database, tutor
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-tutor-test.db")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AI_PROVIDER_API_KEY", raising=False)
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "tutor@example.com", paper_code: str = "CS"):
    response = client.post("/api/auth/register", json={
        "full_name": "Tutor Student",
        "email": email,
        "password": "GatePathTest2027",
        "paper_code": paper_code,
        "target": "IIT admission",
        "daily_hours": 5,
    })
    assert response.status_code == 201, response.text
    return response


def png_data_url() -> str:
    # Minimal PNG signature + test payload; the service validates declared type/signature/size.
    payload = b"\x89PNG\r\n\x1a\n" + b"GATEPath-tutor-test-image"
    return "data:image/png;base64," + base64.b64encode(payload).decode("ascii")


def test_tutor_endpoints_require_authentication(client):
    assert client.get("/api/tutor/status").status_code == 401
    assert client.get("/api/tutor/conversations").status_code == 401
    assert client.post("/api/tutor/chat", json={"message": "Explain paging"}).status_code == 401


def test_tutor_status_discloses_ai_configuration_and_indexed_topics(client):
    register(client)
    response = client.get("/api/tutor/status")
    assert response.status_code == 200
    data = response.json()
    assert data["paper_code"] == "CS"
    assert data["ai_available"] is False
    assert data["mode"] == "knowledge_only"
    assert data["indexed_topic_count"] == 52
    assert data["privacy_note"]


def test_offline_chat_retrieves_relevant_notes_and_persists_private_conversation(client):
    register(client)
    response = client.post("/api/tutor/chat", json={
        "message": "Explain eigenvalues and the characteristic equation",
        "explanation_level": "beginner",
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ai_used"] is False
    assert data["mode"] == "knowledge_only"
    assert data["conversation_id"]
    assert data["sources"]
    assert any("Linear Algebra" in item["topic_name"] for item in data["sources"])
    history = client.get("/api/tutor/conversations").json()["items"]
    assert len(history) == 1
    detail = client.get(f"/api/tutor/conversations/{data['conversation_id']}").json()
    assert [message["role"] for message in detail["messages"]] == ["user", "assistant"]
    assert detail["messages"][1]["sources"]


def test_topic_scoped_chat_validates_topic_id(client):
    register(client)
    bad = client.post("/api/tutor/chat", json={"message": "Explain this topic", "topic_id": "NOT-A-TOPIC"})
    assert bad.status_code == 404
    good = client.post("/api/tutor/chat", json={"message": "Explain this topic", "topic_id": "CS-01-02"})
    assert good.status_code == 200
    assert good.json()["sources"][0]["topic_id"] == "CS-01-02"


def test_unsupported_paper_uses_official_source_only_mode(client):
    register(client, paper_code="DA")
    data = client.get("/api/tutor/status").json()
    assert data["mode"] == "official_source_only"
    assert data["indexed_topic_count"] == 0
    chat = client.post("/api/tutor/chat", json={"message": "Explain a data science topic"})
    assert chat.status_code == 200
    assert chat.json()["mode"] == "official_source_only"
    assert chat.json()["sources"][0]["content_status"] == "official_source"


def test_image_is_not_stored_and_is_not_claimed_analyzed_without_ai(client):
    register(client)
    image = png_data_url()
    response = client.post("/api/tutor/chat", json={
        "message": "Please explain the question in this image",
        "image_data_url": image,
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["image_attached"] is True
    assert data["image_analyzed"] is False
    assert "not interpreted" in data["answer"].lower()
    detail = client.get(f"/api/tutor/conversations/{data['conversation_id']}").json()
    user_message = detail["messages"][0]
    assert user_message["image_attached"] is True
    assert image not in user_message["content"]


def test_image_validation_rejects_wrong_signature_and_unsupported_mime(client):
    register(client)
    wrong_signature = "data:image/png;base64," + base64.b64encode(b"not a png").decode("ascii")
    assert client.post("/api/tutor/chat", json={"message": "Explain image", "image_data_url": wrong_signature}).status_code == 422
    assert client.post("/api/tutor/chat", json={"message": "Explain image", "image_data_url": "data:image/gif;base64,R0lGODlh"}).status_code == 422


def test_conversation_history_isolated_between_students(client):
    register(client, "first@example.com")
    first = client.post("/api/tutor/chat", json={"message": "Explain process scheduling"}).json()
    client.post("/api/auth/logout", json={})
    register(client, "second@example.com")
    assert client.get("/api/tutor/conversations").json()["items"] == []
    assert client.get(f"/api/tutor/conversations/{first['conversation_id']}").status_code == 404
    assert client.delete(f"/api/tutor/conversations/{first['conversation_id']}").status_code == 404


def test_student_can_delete_own_conversation(client):
    register(client)
    data = client.post("/api/tutor/chat", json={"message": "Explain deadlock prevention"}).json()
    response = client.delete(f"/api/tutor/conversations/{data['conversation_id']}")
    assert response.status_code == 204
    assert client.get(f"/api/tutor/conversations/{data['conversation_id']}").status_code == 404


def test_similar_questions_offline_returns_related_original_practice_not_generated(client):
    register(client)
    response = client.post("/api/tutor/similar-questions", json={"topic_id": "CS-01-02", "count": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["generated"] is False
    assert "instead" in data["message"].lower()
    assert all(item["content_label"] == "GATEPath original practice question" for item in data["related_questions"])
    assert all("answer_key" not in item for item in data["related_questions"])


def test_similar_questions_rejects_unknown_topic(client):
    register(client)
    assert client.post("/api/tutor/similar-questions", json={"topic_id": "BAD-ID"}).status_code == 404


def test_chat_rejects_a_different_paper_than_the_student_profile(client):
    register(client, paper_code="CS")
    response = client.post("/api/tutor/chat", json={"message": "Explain databases", "paper_code": "DA"})
    assert response.status_code == 409


def test_rag_retrieval_prioritises_explicit_topic_and_returns_source_metadata():
    sources = tutor.retrieve_context("CS", "please help", topic_id="CS-02-01", limit=3)
    assert sources
    assert sources[0]["topic_id"] == "CS-02-01"
    assert sources[0]["source_url"].startswith("https://")
    assert "editorial" in sources[0]["content_status"]


def test_ai_chat_calls_provider_and_supports_vision(client, monkeypatch):
    register(client)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    captured = {}

    async def fake_completion(messages, *, image_data_url=None, max_tokens=1800):
        captured["messages"] = messages
        captured["image_data_url"] = image_data_url
        return "The uploaded diagram represents a directed graph. [S1]"

    monkeypatch.setattr(tutor, "call_chat_completion", fake_completion)
    image = png_data_url()
    response = client.post("/api/tutor/chat", json={
        "message": "Explain the graph in this image",
        "image_data_url": image,
        "explanation_level": "advanced",
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ai_used"] is True
    assert data["image_analyzed"] is True
    assert captured["image_data_url"] == image
    assert "__IMAGE_DATA_URL__" in str(captured["messages"])


def test_ai_similar_question_generation_uses_grounded_context(client, monkeypatch):
    register(client)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    captured = {}

    async def fake_completion(messages, *, image_data_url=None, max_tokens=1800):
        captured["messages"] = messages
        return "Original practice question 1: ... Answer: B. Explanation: ..."

    monkeypatch.setattr(tutor, "call_chat_completion", fake_completion)
    response = client.post("/api/tutor/similar-questions", json={"topic_id": "CS-01-02", "difficulty": "Advanced", "count": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["generated"] is True
    assert "not an official GATE PYQ" in data["content_label"]
    assert "Linear Algebra" in str(captured["messages"])


def test_provider_error_falls_back_to_transparent_knowledge_mode(client, monkeypatch):
    register(client)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")

    async def failing_completion(messages, *, image_data_url=None, max_tokens=1800):
        raise RuntimeError("temporary provider outage")

    monkeypatch.setattr(tutor, "call_chat_completion", failing_completion)
    response = client.post("/api/tutor/chat", json={"message": "Explain normalization in DBMS"})
    assert response.status_code == 200
    data = response.json()
    assert data["ai_used"] is False
    assert data["provider_error"] == "temporary provider outage"
    assert "could not complete" in data["answer"].lower()


def test_image_data_url_length_is_limited(client):
    register(client)
    response = client.post("/api/tutor/chat", json={"message": "Explain image", "image_data_url": "x" * 7_100_001})
    assert response.status_code == 422


def test_chat_completion_posts_provider_payload_and_replaces_image_placeholder(monkeypatch):
    import asyncio

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("OPENAI_MODEL", "vision-model-test")
    captured = {}

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"choices": [{"message": {"content": "A grounded test response [S1]."}}]}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            captured["timeout"] = kwargs.get("timeout")

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, *, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json
            return FakeResponse()

    monkeypatch.setattr(tutor.httpx, "AsyncClient", FakeAsyncClient)
    image = png_data_url()
    messages = tutor.build_tutor_messages(
        paper_code="CS", paper_name="Computer Science", question="Explain this diagram",
        mode="beginner", sources=[{"source_id": "S1", "topic_name": "Graphs", "section_name": "Algorithms", "excerpt": "A graph contains vertices and edges."}],
        history=[], image_attached=True,
    )
    answer = asyncio.run(tutor.call_chat_completion(messages, image_data_url=image))
    assert answer == "A grounded test response [S1]."
    assert captured["url"] == "https://provider.example/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key-not-a-real-secret"
    assert captured["payload"]["model"] == "vision-model-test"
    assert image in str(captured["payload"]["messages"])
    assert "__IMAGE_DATA_URL__" not in str(captured["payload"]["messages"])
