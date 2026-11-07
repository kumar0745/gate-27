# Stage 14 — Final Deployment and Packaging Checklist

## Release implementation

- [x] Remove duplicated Stage 12 routes and duplicate model/helper definitions.
- [x] Set API version to `0.14.0`.
- [x] Use FastAPI lifespan for database initialization and first-admin bootstrap.
- [x] Add `/api/ready` database readiness endpoint.
- [x] Make SQLite database location configurable with `GATEPATH_DATABASE_PATH`.
- [x] Validate production HTTPS origin and Secure-cookie requirement at startup.
- [x] Make session cookie creation and deletion use the same secure-cookie policy.
- [x] Add response security headers, compatible external font sources and CSP support for generated inline progress styles.
- [x] Add `.gitignore` and `.dockerignore` rules for credentials, databases, caches and local artifacts.
- [x] Add Dockerfile and a root entrypoint that prepares a persistent data directory before dropping privileges.
- [x] Add Render Blueprint with a persistent disk and readiness health check.
- [x] Add SQLite online-backup script with post-backup integrity validation.
- [x] Add deployment instructions, local run steps, environment checklist and post-deploy smoke checklist.
- [x] Add final deployment/security test coverage.

## Verification performed in this workspace

- [x] `python scripts/check_project.py` — passed.
- [x] `python -m pytest backend/tests -q` — 125 passed.
- [x] `python -m compileall -q backend` — passed.
- [x] `node --check frontend/app.js` — passed.
- [x] `node --check frontend/auth.js` — passed.
- [x] `node --check frontend/landing.js` — passed.
- [x] YAML parsed for `render.yaml` and `.github/workflows/ci.yml`.
- [x] 80 unique API method/path pairs, zero duplicates.
- [x] SQLite backup script test creates a valid restorable copy.
- [ ] Docker image build: not run (Docker Engine unavailable in this workspace).
- [ ] Visual browser test: not run (Chromium executable unavailable).
- [ ] Public production deployment: requires user-owned repository, hosting account, domain and secret configuration.

## Deployment constraints

- Current deploy target uses one FastAPI instance with a persistent SQLite disk. It is not a horizontally scalable multi-instance design.
- Use a persistent disk; ephemeral container filesystems can lose SQLite data after restarts/redeploys.
- Render persistent disks require a paid web service and prevent multiple service instances. For higher scale, migrate to managed PostgreSQL before scaling out.
- SMTP and AI provider integrations are optional and require user-supplied credentials.
- Interactive topic-level content is still primarily populated for the CS pilot. Other GATE papers have official source links and explicit pending-import states.

See `docs/STAGE-14-DEPLOYMENT.md` for complete instructions.
