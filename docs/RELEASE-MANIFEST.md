# GATEPath 2027 — Final Release Manifest

**Release:** 14-stage consolidated source delivery  
**API version:** 0.14.0  
**Application status:** Locally runnable; prepared for owner-controlled hosting deployment.

## Included

- FastAPI backend and SQLite schema/migrations.
- Public landing page, authentication screens and signed-in student workspace.
- All 30 GATE 2027 paper catalogue entries and official syllabus links.
- Structured CS syllabus (10 sections / 52 topics) and topic-linked original study notes.
- CS mind-map generation and export.
- GATE 2026 CS-1/CS-2 answer-key metadata bank with official paper links.
- Original CS topic practice questions and one original 65-question CS mock pilot.
- Personalised CS study planner and revision queue.
- Paper-aware RAG tutor with optional server-side AI provider configuration.
- Student analytics, community and administrator moderation/content review.
- Automated tests, static project-integrity checks, CI workflow, backup script and deployment files.
- Documentation for all 14 stages, content provenance and deployment.

## Excluded intentionally

- `.env` secrets and API credentials.
- SQLite database files, WAL/SHM files and local user data.
- Virtual environments, Python bytecode, pytest caches and editor-specific state.
- Backups and previous ZIP archives.

## Verification at packaging

- 125 automated tests passed.
- Project integrity checker passed.
- 80 unique API method/path registrations; no duplicates.
- Python compilation and JavaScript syntax checks passed.
- Render Blueprint and CI workflow YAML parsed successfully.
- Live Uvicorn smoke test passed: readiness, homepage, paper catalogue, registration and authenticated session.

## Deployment and content limitations

- Public hosting was not performed: it requires the owner-controlled repository, Render account, public HTTPS service URL and deployment secrets.
- Docker image build was not run because Docker Engine/CLI is unavailable in the packaging environment.
- Visual browser automation was not run because a Chromium executable is unavailable.
- The structured interactive content is primarily populated for the CS pilot. Other papers have official catalogue links and explicit pending-import states; they should not be represented as having complete notes/PYQs/mock libraries yet.
- SMTP and live AI-provider calls require credentials and were not live-tested.
- Review `docs/STAGE-14-DEPLOYMENT.md` before publishing.
