from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import database
from app.main import app


def test_home_opens_workspace_without_authentication(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "guest.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "false")
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "My workspace" in response.text
        cookie = response.headers.get("set-cookie", "")
        assert "gatepath_session=" in cookie
        assert "httponly" in cookie.lower()
        workspace = client.get("/api/workspace")
        assert workspace.status_code == 200
        assert workspace.json()["workspace_mode"] == "guest"
        assert workspace.json()["paper_code"] == "CS"


def test_login_and_registration_pages_redirect_to_guest_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "routes.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "false")
    with TestClient(app) as client:
        for path in ("/login", "/register", "/forgot-password", "/reset-password"):
            response = client.get(path, follow_redirects=False)
            assert response.status_code == 303
            assert response.headers["location"] == "/app"
        workspace = client.get("/app")
        assert workspace.status_code == 200
        assert "auth-form" not in workspace.text


def test_active_catalog_contains_only_cs_and_ga_is_included(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "scope.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "false")
    with TestClient(app) as client:
        client.get("/")
        catalogue = client.get("/api/papers").json()
        assert catalogue["count"] == 1
        assert [paper["code"] for paper in catalogue["items"]] == ["CS"]
        assert client.get("/api/syllabus?paper_code=DA").status_code == 404
        syllabus = client.get("/api/syllabus?paper_code=CS").json()
        assert syllabus["common_section"]["marks"] == 15
        ga = next(section for section in syllabus["sections"] if section["code"] == "GA")
        assert {topic["name"] for topic in ga["topics"]} == {
            "Verbal Aptitude", "Quantitative Aptitude", "Analytical Aptitude", "Spatial Aptitude"
        }
        material = client.get("/api/materials/GA-QUANT-01?paper_code=CS")
        assert material.status_code == 200
        assert "chart" in material.json()["overview"].lower() or "data" in material.json()["overview"].lower()
