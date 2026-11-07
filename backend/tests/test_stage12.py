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
from app.main import app, find_practice_question


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-stage12.db")
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, email="stage12@example.com", paper_code="CS"):
    response = client.post("/api/auth/register", json={
        "full_name": "Stage Twelve Student", "email": email,
        "password": "GatePathTest2027", "paper_code": paper_code,
        "target": "IIT admission", "daily_hours": 5,
    })
    assert response.status_code == 201, response.text
    return response


def promote_current_to_admin(client: TestClient):
    me = client.get("/api/auth/me").json()["user"]
    with database.get_connection() as conn:
        conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (me["id"],))
    return me


def test_analytics_requires_authentication(client):
    assert client.get("/api/analytics").status_code == 401


def test_analytics_initially_reports_only_zero_recorded_activity(client):
    register(client)
    data = client.get("/api/analytics").json()
    assert data["paper_code"] == "CS"
    assert data["practice"]["unique_questions_attempted"] == 0
    assert data["practice"]["accuracy_percent"] == 0
    assert data["mock_tests"]["completed"] == 0
    assert data["syllabus"]["total_topics"] == 56
    assert len(data["activity"]) == 14
    assert "not estimated" in data["notice"]


def test_analytics_includes_topic_progress_and_practice_accuracy(client):
    register(client)
    progress = client.patch("/api/materials/CS-01-01/progress?paper_code=CS", json={"status": "completed"})
    assert progress.status_code == 200
    session = client.post("/api/practice/sessions", json={"mode": "topic", "topic_id": "CS-01-01", "question_count": 5}).json()
    question = session["questions"][0]
    source = find_practice_question(question["id"], "CS")
    assert source
    attempted = client.post(f"/api/practice/sessions/{session['id']}/attempt", json={"question_id": question["id"], "answer": source["answer_key"]})
    assert attempted.status_code == 200
    data = client.get("/api/analytics").json()
    assert data["syllabus"]["completed_topics"] == 1
    assert data["practice"]["unique_questions_attempted"] == 1
    assert data["practice"]["accuracy_percent"] == 100
    assert any(item["topic_id"] == source["topic_id"] for item in data["weak_topics"])


def test_analytics_rejects_unknown_paper(client):
    register(client)
    assert client.get("/api/analytics?paper_code=ZZ").status_code == 404


def test_analytics_is_account_scoped(client):
    register(client, "one@stage12.test")
    client.patch("/api/materials/CS-01-01/progress?paper_code=CS", json={"status": "completed"})
    client.post("/api/auth/logout", json={})
    register(client, "two@stage12.test")
    data = client.get("/api/analytics").json()
    assert data["syllabus"]["completed_topics"] == 0
    assert data["practice"]["unique_questions_attempted"] == 0


def test_community_requires_authentication(client):
    assert client.get("/api/community/feed").status_code == 401
    assert client.post("/api/community/posts", json={}).status_code == 401


def create_post(client, title="How should I revise graph algorithms?", body="I have studied BFS and DFS. What is a good way to compare their time and space complexity for GATE?"):
    response = client.post("/api/community/posts", json={"paper_code": "CS", "category": "Doubt", "title": title, "body": body})
    assert response.status_code == 201, response.text
    return response.json()


def test_community_create_feed_and_post_detail(client):
    register(client)
    post = create_post(client)
    feed = client.get("/api/community/feed?paper_code=CS").json()
    assert feed["total"] == 1
    assert feed["items"][0]["id"] == post["id"]
    detail = client.get(f"/api/community/posts/{post['id']}").json()
    assert detail["post"]["title"] == post["title"]
    assert detail["replies"] == []


def test_community_validation_and_paper_validation(client):
    register(client)
    assert client.post("/api/community/posts", json={"paper_code":"ZZ","category":"Doubt","title":"A sufficiently long title","body":"This discussion body has enough characters."}).status_code == 404
    assert client.post("/api/community/posts", json={"paper_code":"CS","category":"Unknown","title":"A sufficiently long title","body":"This discussion body has enough characters."}).status_code == 422


def test_community_reply_and_like_toggle(client):
    register(client)
    post = create_post(client)
    reply = client.post(f"/api/community/posts/{post['id']}/replies", json={"body":"Use a small graph and trace the queue to compare traversal order."})
    assert reply.status_code == 201
    first_like = client.put(f"/api/community/posts/{post['id']}/like", json={}).json()
    second_like = client.put(f"/api/community/posts/{post['id']}/like", json={}).json()
    assert first_like["liked"] is True and first_like["like_count"] == 1
    assert second_like["liked"] is False and second_like["like_count"] == 0
    assert len(client.get(f"/api/community/posts/{post['id']}").json()["replies"]) == 1


def test_community_scope_category_and_search_filters(client):
    register(client)
    create_post(client)
    create_post(client, "A resource for learning database normalisation", "I found that drawing functional dependencies before attempting a normalization problem is useful.")
    assert client.get("/api/community/feed?scope=mine").json()["total"] == 2
    assert client.get("/api/community/feed?category=Doubt").json()["total"] == 2
    assert client.get("/api/community/feed?q=normalisation").json()["total"] == 1
    assert client.get("/api/community/feed?scope=all").json()["total"] == 2


def test_community_reports_cannot_target_own_content(client):
    register(client)
    post = create_post(client)
    response = client.post("/api/community/reports", json={"target_type":"post","target_id":post["id"],"reason":"This is my own post and I am testing."})
    assert response.status_code == 422


def test_community_content_is_private_to_owner_when_hidden(client):
    register(client, "first@community.test")
    post = create_post(client)
    with database.get_connection() as conn:
        conn.execute("UPDATE community_posts SET status = 'hidden' WHERE id = ?", (post["id"],))
    client.post("/api/auth/logout", json={})
    register(client, "second@community.test")
    assert client.get(f"/api/community/posts/{post['id']}").status_code == 404
    assert client.get("/api/community/feed?scope=all").json()["total"] == 0


def test_student_can_remove_own_post_and_reply(client):
    register(client)
    post = create_post(client)
    reply = client.post(f"/api/community/posts/{post['id']}/replies", json={"body":"A useful reply for the discussion."}).json()
    assert client.delete(f"/api/community/replies/{reply['id']}").status_code == 204
    assert client.delete(f"/api/community/posts/{post['id']}").status_code == 204
    assert client.get("/api/community/feed").json()["total"] == 0


def test_student_cannot_access_admin_apis(client):
    register(client)
    assert client.get("/api/admin/overview").status_code == 403
    assert client.get("/api/admin/users").status_code == 403
    assert client.get("/api/admin/content/catalog").status_code == 403


def test_admin_overview_users_and_content_catalog(client):
    register(client)
    promote_current_to_admin(client)
    data = client.get("/api/admin/overview").json()
    assert data["users"] == 1 and data["admins"] == 1
    assert client.get("/api/admin/users").json()["total"] == 1
    catalog = client.get("/api/admin/content/catalog").json()["items"]
    assert len(catalog) == 1
    cs = next(item for item in catalog if item["paper_code"] == "CS")
    assert cs["study_notes"] == 56 and cs["practice_questions"] == 38
    assert data["total_content_items"] >= 212
    assert data["pending_content_reviews"] == data["total_content_items"]


def test_admin_can_review_material_and_practice_content(client):
    register(client)
    promote_current_to_admin(client)
    queue = client.get("/api/admin/content/review-queue?paper_code=CS&limit=300").json()
    assert queue["total_available"] >= 80
    material = next(item for item in queue["items"] if item["content_type"] == "material")
    result = client.put(f"/api/admin/content/reviews/material/{material['content_id']}?paper_code=CS", json={"status":"approved","note":"Reviewed definitions and scope."})
    assert result.status_code == 200
    updated = client.get("/api/admin/content/review-queue?paper_code=CS&content_type=material").json()
    found = next(item for item in updated["items"] if item["content_id"] == material["content_id"])
    assert found["review_status"] == "approved"
    assert found["review_note"] == "Reviewed definitions and scope."
    assert client.get("/api/admin/content/review-queue?paper_code=CS&content_type=material").json()["total_available"] == 56
    overview = client.get("/api/admin/overview").json()
    assert overview["approved_content_items"] == 1
    assert overview["pending_content_reviews"] == overview["total_content_items"] - 1


def test_admin_can_resolve_report_and_hide_post(client):
    register(client, "student@moderation.test")
    post = create_post(client)
    client.post("/api/community/posts/1/replies", json={"body":"This is a useful answer to the posted doubt."})
    client.post("/api/auth/logout", json={})
    register(client, "reporter@moderation.test")
    report = client.post("/api/community/reports", json={"target_type":"post","target_id":post["id"],"reason":"The discussion is spam and unrelated to GATE preparation."})
    assert report.status_code == 201
    client.post("/api/auth/logout", json={})
    register(client, "admin@moderation.test")
    promote_current_to_admin(client)
    reports = client.get("/api/admin/reports?status=pending").json()["items"]
    assert len(reports) == 1
    response = client.patch(f"/api/admin/reports/{reports[0]['id']}", json={"status":"resolved","action":"hide","note":"Hidden for review."})
    assert response.status_code == 200
    assert client.get("/api/community/feed?scope=all").json()["total"] == 0


def test_admin_can_pin_and_moderate_posts_and_replies(client):
    register(client, "student@pin.test")
    post = create_post(client)
    reply = client.post(f"/api/community/posts/{post['id']}/replies", json={"body":"Here is a helpful structured approach."}).json()
    client.post("/api/auth/logout", json={})
    register(client, "admin@pin.test")
    promote_current_to_admin(client)
    assert client.patch(f"/api/admin/community/posts/{post['id']}", json={"status":"published","pinned":True}).status_code == 200
    assert client.patch(f"/api/admin/community/replies/{reply['id']}", json={"status":"hidden"}).status_code == 200
    detail = client.get(f"/api/community/posts/{post['id']}").json()
    assert detail["post"]["pinned"] == 1
    assert detail["replies"] == []


def test_admin_can_deactivate_student_and_revoke_sessions(client):
    register(client, "admin@access.test")
    promote_current_to_admin(client)
    client.post("/api/auth/logout", json={})
    register(client, "student@access.test")
    student_id = client.get("/api/auth/me").json()["user"]["id"]
    client.post("/api/auth/logout", json={})
    client.post("/api/auth/login", json={"email":"admin@access.test","password":"GatePathTest2027"})
    response = client.patch(f"/api/admin/users/{student_id}", json={"is_active":False})
    assert response.status_code == 200 and response.json()["sessions_revoked"] is True
    client.post("/api/auth/logout", json={})
    login = client.post("/api/auth/login", json={"email":"student@access.test","password":"GatePathTest2027"})
    assert login.status_code == 401


def test_admin_cannot_deactivate_own_account(client):
    register(client)
    me = promote_current_to_admin(client)
    response = client.patch(f"/api/admin/users/{me['id']}", json={"is_active":False})
    assert response.status_code == 422
