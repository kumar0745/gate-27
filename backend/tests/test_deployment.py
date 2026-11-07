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
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gatepath-deployment-test.db")
    monkeypatch.delenv("GATEPATH_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("GATEPATH_ADMIN_PASSWORD", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "false")
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient):
    return client.post("/api/auth/register", json={
        "full_name": "Deployment QA Student",
        "email": "deployment-qa@example.test",
        "password": "GatePathTest2027",
        "paper_code": "CS",
        "target": "IIT admission",
        "daily_hours": 5,
    })


def test_health_and_readiness_endpoints(client):
    assert client.get("/api/health").status_code == 200
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"


def test_security_headers_are_present(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "fonts.googleapis.com" in response.headers["content-security-policy"]
    assert "fonts.gstatic.com" in response.headers["content-security-policy"]


def test_api_responses_are_not_cached(client):
    response = client.get("/api/health")
    assert "no-store" in response.headers.get("cache-control", "")


def test_cross_site_write_is_rejected(client):
    response = client.post("/api/auth/register", json={}, headers={"sec-fetch-site": "cross-site"})
    assert response.status_code == 403


def test_origin_mismatch_is_rejected(client, monkeypatch):
    monkeypatch.setenv("APP_BASE_URL", "https://gatepath.example")
    response = client.post("/api/auth/register", json={}, headers={"origin": "https://attacker.example"})
    assert response.status_code == 403


def test_configured_origin_is_accepted_and_production_cookie_is_secure(client, monkeypatch):
    monkeypatch.setenv("APP_BASE_URL", "https://gatepath.example")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "true")
    response = client.post("/api/auth/register", json={
        "full_name": "Deployment QA Student",
        "email": "secure-cookie@example.test",
        "password": "GatePathTest2027",
        "paper_code": "CS",
        "target": "IIT admission",
        "daily_hours": 5,
    }, headers={"origin": "https://gatepath.example"})
    assert response.status_code == 201, response.text
    cookie = response.headers.get("set-cookie", "").lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=strict" in cookie


def test_readiness_failure_is_reported_as_service_unavailable(client, monkeypatch):
    def broken_connection():
        raise database.sqlite3.OperationalError("test database outage")
    monkeypatch.setattr("app.main.get_connection", broken_connection)
    response = client.get("/api/ready")
    assert response.status_code == 503



def test_production_startup_rejects_non_https_base_url(client, tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_BASE_URL", "http://gatepath.example")
    monkeypatch.setenv("GATEPATH_SECURE_COOKIES", "false")
    with pytest.raises(RuntimeError, match="HTTPS"):
        with TestClient(app):
            pass


def test_admin_bootstrap_creates_account_only_when_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "admin-bootstrap.db")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GATEPATH_ADMIN_EMAIL", "first-admin@example.test")
    monkeypatch.setenv("GATEPATH_ADMIN_PASSWORD", "StrongAdminPass2027")
    with TestClient(app):
        with database.get_connection() as conn:
            admin = conn.execute("SELECT email, role FROM users WHERE email = ?", ("first-admin@example.test",)).fetchone()
    assert admin is not None
    assert admin["role"] == "admin"


def test_database_backup_script_produces_integrity_checked_copy(tmp_path, monkeypatch):
    import sys
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import backup_db

    source = tmp_path / "source.db"
    with database.sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE sample (value TEXT NOT NULL)")
        conn.execute("INSERT INTO sample(value) VALUES ('preserve me')")
    monkeypatch.setattr(backup_db, "DB_PATH", source)
    output = backup_db.backup_database(tmp_path / "backups" / "copy.db")
    with database.sqlite3.connect(output) as conn:
        assert conn.execute("SELECT value FROM sample").fetchone()[0] == "preserve me"
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
