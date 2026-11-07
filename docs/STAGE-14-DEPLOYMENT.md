# GATEPath CS-only deployment guide

## Current release

GATEPath contains one preparation track: **GATE 2027 CS — Computer Science and Information Technology**, with General Aptitude included. The root route opens the guest workspace directly. `/login`, `/register`, `/forgot-password` and `/reset-password` redirect to `/app`; no account creation or sign-in screen is part of this release.

## Runtime

- FastAPI serves the workspace, public health endpoints and CS preparation APIs.
- Static workspace assets are served from `/static/`.
- A random browser session cookie scopes a guest's progress, plans, practice and activity to that browser workspace.
- SQLite is used for local development and for the included Render persistent-disk setup.
- `/api/health` checks process liveness. `/api/ready` checks database readiness.

## Local run

```bash
python -m venv .venv
# Activate .venv using the command for your shell.
python -m pip install -r requirements-dev.txt
python scripts/check_project.py
python -m pytest backend/tests -q
python -m uvicorn index:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The guest study workspace is created automatically.

## Render with persistent disk

The root `render.yaml` and `Dockerfile` configure a Docker web service, `/api/ready` health checking and a disk mounted at `/var/data`.

1. Connect this repository to Render and create the Blueprint service.
2. Configure the final public URL and secure-cookie environment settings.
3. Ensure the service plan supports persistent disks and that the disk is mounted at `/var/data`.
4. Confirm `/api/health` and `/api/ready` both return HTTP 200.
5. Verify guest workspace creation, progress writes, restarts and persistence.

A persistent disk is required for SQLite-backed records. Multi-instance scale requires a managed shared database and a database adapter/schema migration.

## Vercel

The verified Vercel preview deployment is a smoke-test environment only. It uses `APP_ENV=preview` and `GATEPATH_DATABASE_PATH=/tmp/gatepath.db` so the FastAPI app can be tested on Vercel. `/tmp` storage is ephemeral and instance-local: user progress may disappear and must not be presented as durable storage.

The database adapter deliberately fails fast on Vercel production while the project only has SQLite. Before promoting a production deployment, migrate the adapter/schema to a durable managed database (for example PostgreSQL), configure the production connection securely in Vercel, and test migrations, guest progress writes, restarts and backup/restore.

## Release checks

```bash
python scripts/check_project.py
python -m compileall -q backend
node --check frontend/app.js
python -m pytest backend/tests -q
```

Then smoke-test:

- `/` loads the CS workspace without sign-in.
- `/app` loads and sets a guest workspace cookie.
- `/api/papers` returns only `CS`.
- `/api/syllabus?paper_code=CS` returns the ten CS sections plus General Aptitude.
- requests for other paper codes are rejected.
- CS notes, topic maps, practice, mock, PYQ archive links, planner and analytics load.
- `/api/health` and `/api/ready` return HTTP 200.
- in a persistent production environment, progress survives process restarts.

## Data provenance

Official syllabus statements, General Aptitude scope, question-paper pattern, 2021–2026 CS paper links and 2026 CS-1/CS-2 answer-key metadata are sourced from the IIT Madras GATE 2027 website/archive. GATEPath-authored notes, examples, practice questions and mock questions are supplemental editorial content and are labelled as such. The official question stems and diagrams are not republished; the PYQ workspace links to the official question-paper PDFs and stores answer-key metadata separately.
