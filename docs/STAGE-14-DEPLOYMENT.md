# Stage 14 — Deployment and Release Guide

## Release status

The repository is packaged for deployment. A public production URL is **not** claimed by this build because it has not been connected to a hosting account, domain, or user-controlled secrets.

## Runtime architecture

- FastAPI serves the public website and authenticated workspace pages.
- Static frontend assets are served from `/static`.
- SQLite stores accounts, sessions, learning progress, attempts, plans, conversations, community posts and admin review records.
- The database path is configurable with `GATEPATH_DATABASE_PATH`.
- `/api/health` checks process health; `/api/ready` checks database readiness.

## Local run (Windows PowerShell)

```powershell
Copy-Item .env.example .env
# Edit .env and set GATEPATH_ADMIN_EMAIL and GATEPATH_ADMIN_PASSWORD.
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/check_project.py
python -m pytest backend/tests -q
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The workspace is at `/app` and API docs at `/docs` in development.

## Local run (Linux/macOS)

```bash
cp .env.example .env
# Edit .env and set GATEPATH_ADMIN_EMAIL and GATEPATH_ADMIN_PASSWORD.
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/check_project.py
python -m pytest backend/tests -q
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

## Docker

```bash
docker build -t gatepath-2027 .
docker run --rm -p 8000:8000 \
  -e APP_ENV=development \
  -e APP_BASE_URL=http://localhost:8000 \
  -e GATEPATH_SECURE_COOKIES=false \
  -e GATEPATH_DATABASE_PATH=/var/data/gatepath.db \
  -e GATEPATH_ADMIN_EMAIL=admin@example.com \
  -e GATEPATH_ADMIN_PASSWORD='ReplaceWithALongUniquePassword123' \
  -v gatepath-data:/var/data \
  gatepath-2027
```

For a real HTTPS deployment, set `APP_BASE_URL` to the final `https://` origin and set `GATEPATH_SECURE_COOKIES=true`. Do not put credentials in the Docker image or commit them to source control.

## Render Blueprint

The root `render.yaml` and `Dockerfile` configure a single Docker web service with `/api/ready` as its health check and a persistent volume at `/var/data`.

1. Push this project to a Git repository you control.
2. In Render, create a new Blueprint and connect that repository.
3. Enter `APP_BASE_URL` as the final service URL (for example, `https://your-service.onrender.com`).
4. Enter a valid administrator email. Render generates the initial admin password if you keep `generateValue: true`; save it securely from the service environment settings.
5. Optionally configure `OPENAI_API_KEY` and SMTP values. The offline knowledge-only tutor works without an AI key; password-reset email delivery requires SMTP.
6. Deploy and wait for `/api/ready` to return HTTP 200.
7. Sign in as the bootstrap admin, change/store credentials safely, create a student account and complete the smoke checklist below.

**Hosting requirement:** Render persistent disks require a paid web service. The blueprint uses a persistent disk because the current database is SQLite; without persistence, account and learning data can be lost on redeploy. A persistent disk also limits the service to one instance. For a multi-instance/high-scale deployment, migrate the app from SQLite to managed PostgreSQL and review connection pooling before scaling. See Render's official [Blueprint reference](https://render.com/docs/blueprint-spec) and [Persistent Disks documentation](https://render.com/docs/disks).

## Production environment checklist

- `APP_ENV=production`
- `APP_BASE_URL=https://<your-domain>`
- `GATEPATH_SECURE_COOKIES=true`
- `GATEPATH_DATABASE_PATH=/var/data/gatepath.db` (when using the included Render disk)
- Strong bootstrap admin credentials, stored only in the hosting provider's secret manager
- SMTP settings tested with a real inbox before advertising password reset
- AI provider key configured only if live model answers are enabled
- Backups of `/var/data/gatepath.db` scheduled and restore tested
- Domain HTTPS enabled and final redirect/origin behavior tested

## Post-deployment smoke checklist

1. `GET /api/health` returns HTTP 200.
2. `GET /api/ready` returns HTTP 200 with `database: ok`.
3. Landing page `/` loads and assets under `/static/` return HTTP 200.
4. Registration, login, logout and protected `/app` redirect work.
5. Admin login can open the admin workspace; a student receives HTTP 403 from admin APIs.
6. A syllabus topic can be opened and marked complete.
7. A practice question can be attempted and appears in analytics.
8. A mock can be started, saved, submitted and reviewed.
9. Community post/report moderation works.
10. Restart/redeploy preserves the database and user accounts.

## Content coverage disclosure

The application architecture supports the official GATE paper catalogue. The structured topic syllabus, study notes, mind maps, practice set and full mock are currently populated primarily for the CS pilot. Official paper links and explicit pending-import states are shown for other papers; do not advertise every paper as having a complete interactive question/notes library until it has been transcribed, reviewed and tested. The CS 2026 PYQ import stores answer-key metadata and official paper links; it does not redistribute the full question-paper text.
