# GATEPath 2027

GATEPath is an independent GATE preparation platform. The project is being built in 14 stages. It is not an official GATE, IIT Madras or IIT-affiliated website.

## Current build status

- Stage 1 — Project foundation: complete.
- Stage 2 — Public landing page and UI foundation: complete.
- Stage 3 — Student accounts, authentication and profiles: complete.
- Stage 4 — Versioned syllabus engine: complete for the platform foundation and the first full CS paper import.
- Stage 5 — Study material library: complete for the 52-topic CS pilot; other-paper material imports remain queued.
- Stage 6 — Interactive mind maps: subject-level topic graphs, syllabus hierarchy, prerequisite relationships, topic-note links, student progress, pan/zoom, fullscreen and SVG export for the CS pilot.
- Stage 7 — Previous-year question bank: 130 GATE 2026 CS-1/CS-2 answer-key metadata records, server-side MCQ/MSQ/NAT checking, bookmarks and attempt history.
- Stage 8 — Practice and quiz engine: original topic-mapped CS pilot questions, difficulty/type filters, daily challenge, custom timed sessions, question palette, explanations, score summaries and weak-topic insights.
- Stage 9 — Full mock-test engine: paper-specific GATE 2027 pattern catalogue, 65-question/180-minute CS pilot mock, server-saved answers, review flags, server expiry/auto-submit, GATE-style scoring and detailed result review.
- Stage 10 — Personalised study planner: capacity-aware 30/60/90-day CS plans, daily tasks, weak-topic prioritisation, revision queue and overdue rescheduling.
- Stage 11 — AI GATE tutor: private conversation history, paper-aware lexical RAG over indexed CS notes, source references, beginner/advanced explanation modes, image-question handoff to a configured vision-capable provider, and AI-generated similar-question drafts.
- Stage 12 — Student analytics, moderated community discussions and administrator management/content-review workflows.
- Stage 13 — Integration and QA: codebase-wide API/content/frontend audit and regression preparation. The final source audit in Stage 14 removed an accidental duplicate Stage 12 route block and reconciled earlier QA counts with the test suite actually present in the project.
- Stage 14 — Release packaging: configurable persistent SQLite path, FastAPI lifespan startup, production HTTPS guard, secure cookies, readiness probe, security headers, Dockerfile, Render Blueprint, database backup utility, deployment documentation and consolidated source package.

The current version (API 0.14.0) contains the official GATE 2027 paper catalogue for all 30 papers and official syllabus PDF links for every paper. The topic-level syllabus is currently structured for CS (10 sections and 52 topics). The other 29 paper PDFs are linked but their detailed topic imports are pending; GATEPath intentionally does not invent topics. The shared General Aptitude PDF is linked separately and its topic-level transcription remains pending.

See `docs/STAGE-4-CHECKLIST.md` and `docs/STAGE-4-CONTENT-SOURCES.md` for content boundaries and provenance.

## Technology

- Frontend: semantic HTML, CSS and vanilla JavaScript. No frontend build step is needed.
- Backend: Python 3.11+ and FastAPI.
- AI tutor provider integration: optional OpenAI-compatible Chat Completions endpoint using `httpx`; local retrieval remains available without credentials.
- Database: SQLite with additive migrations and configurable project-relative or absolute storage path.
- Authentication: salted PBKDF2-HMAC-SHA256 password hashes, server-side session records, opaque HTTP-only cookies, same-origin write checks and secure-cookie deployment override.
- Browser protections: Content Security Policy, frame/content-type protections, restrictive referrer and permissions policies, and no-store caching for authenticated/API responses.
- API documentation: FastAPI Swagger UI at `/docs`.

## Run locally (Windows PowerShell)

From the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Then open:

- Public homepage: http://127.0.0.1:8000/
- Register: http://127.0.0.1:8000/register
- Login: http://127.0.0.1:8000/login
- Student workspace: http://127.0.0.1:8000/app
- API docs: http://127.0.0.1:8000/docs

PowerShell quick start (creates `.venv`, installs runtime dependencies and starts the API):

```powershell
.\scripts\start.ps1
```

## Run locally (macOS / Linux)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload
```

Or use `bash scripts/start.sh` (creates `.venv`, installs runtime dependencies and starts the API).

## Administrator bootstrap

Student accounts cannot assign themselves the administrator role. To create the first administrator, edit `.env` before starting the server:

```dotenv
GATEPATH_ADMIN_EMAIL=admin@example.com
GATEPATH_ADMIN_PASSWORD=Use-A-Long-Unique-Password-Here
```

The administrator is created only if that email does not already exist. Keep `.env` private and never commit it. Admin syllabus endpoints are available under `/api/admin/syllabus/*` and require the administrator role.

## Optional AI tutor configuration

The tutor works in two modes:

- **Knowledge-only mode:** retrieves relevant passages from the local GATEPath notes and links to the official syllabus. It does not pretend to generate an AI answer when no provider is configured.
- **AI + grounded retrieval mode:** configure an OpenAI-compatible chat-completions provider in `.env` to enable generated explanations, image-question analysis (with a vision-capable model), and new similar-question drafts.

```dotenv
OPENAI_API_KEY=your-server-side-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

Restart the backend after changing `.env`. The key is read only by the backend and is never returned by the tutor status API. Uploaded question images are validated, sent to the configured provider for visual analysis, and are not saved to GATEPath storage. Text messages and assistant responses are saved in the student's private conversation history. Review the configured provider's data-retention terms before sending personal or sensitive images.

Tutor endpoints (all require an authenticated student session):

- `GET /api/tutor/status` — AI configuration status, indexed topic count, topic catalogue and privacy note.
- `GET /api/tutor/conversations` — list the current student's conversations.
- `GET /api/tutor/conversations/{conversation_id}` — read one owned conversation and its source references.
- `DELETE /api/tutor/conversations/{conversation_id}` — delete a conversation and messages.
- `POST /api/tutor/chat` — grounded chat, optional topic focus and optional image data URL.
- `POST /api/tutor/similar-questions` — generate original practice questions when AI is configured; otherwise returns related existing practice questions without answer keys.

The tutor's local retrieval uses a BM25-like lexical ranker over GATEPath's structured notes. For the current CS pilot, notes are original editorial content mapped to the official syllabus. The official syllabus link is cited as a scope reference; it is not represented as the source of every explanatory sentence. Other papers remain in official-source-only mode until their notes are imported.

## Password recovery email

Email delivery for password recovery requires SMTP configuration in `.env`:

```dotenv
APP_BASE_URL=http://127.0.0.1:8000
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
```

Use a trusted SMTP service and an HTTPS `APP_BASE_URL` in production.

## Stage 5 study material content model

- `backend/app/data/materials/CS-GATE-2027.json` — 52 original editorial learning notes mapped to the CS topic IDs.
- Each note contains a scope statement, overview, learning outcomes, concept explanations, an original worked illustration, formula/rule cards, common mistakes, quick revision bullets and references.
- NPTEL links point to provider-hosted course pages; enrollment and certificate availability may vary. Book references are bibliographic suggestions only; no copyrighted PDF is redistributed.
- `student_material_progress` stores each student’s status, bookmarks and private notes separately by paper/topic.

## Stage 4 syllabus content model

- `backend/app/data/papers.json` — official 30-paper catalogue, per-paper official PDF URLs and special sectional-paper structures.
- `backend/app/data/syllabi/CS-GATE-2027.json` — structured CS 2027 syllabus import.
- `syllabus_versions` — database registry for paper/version source metadata and review status.
- `student_topic_progress` — student-specific progress by paper, version and topic.
- `syllabus_topic_edits` — administrator overrides with review status and editor attribution.

For CS, section/topic names and their `official_statement` field are based on the official two-page IIT Madras GATE 2027 CS syllabus PDF. Subtopic chips split official statements into smaller tracking units. Optional `prerequisites` are GATEPath study guidance, not official GATE syllabus requirements.

For other papers, the app displays the official syllabus PDF source and a clear pending-import notice until topic-level transcription and review are complete.

## Deployment and final release

The project includes a Dockerfile, Render Blueprint (`render.yaml`), persistent-database configuration and a SQLite online-backup utility. Read `docs/STAGE-14-DEPLOYMENT.md` before deploying. A public deployment is not included in the source package: it must be connected to a repository and hosting account controlled by the owner, then configured with a public HTTPS origin and secrets.

The included Render configuration uses a paid single-instance web service with a persistent disk because the current database is SQLite. It is not suitable for horizontal scaling. For multi-instance production, migrate the database to managed PostgreSQL and update the database access layer before scaling.

Final release status and known limitations are in `docs/STAGE-14-CHECKLIST.md`.

## Key API endpoints

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | API health |
| GET | `/api/papers` | Public | All 30 official GATE paper codes and PDF links |
| GET | `/api/syllabus?paper_code=CS` | Student | Structured syllabus and per-student progress |
| GET | `/api/materials?paper_code=CS` | Student | Topic-wise study library catalogue and progress |
| GET | `/api/materials/{topic_id}?paper_code=CS` | Student | Full topic note, formulas, examples and resources |
| PATCH | `/api/materials/{topic_id}/progress?paper_code=CS` | Student | Update topic status, bookmark or private note |
| GET | `/api/mindmaps?paper_code=CS&section_code=CS-01` | Student | Subject-level graph nodes, hierarchy, prerequisites and student progress |
| GET | `/api/pyq/catalog?paper_code=CS` | Student | Official PYQ archives and interactive import coverage |
| GET | `/api/pyq/questions?paper_code=CS&year=2026` | Student | Filtered question metadata without exposing answer keys |
| GET | `/api/pyq/questions/{question_id}` | Student | Question source links and previous-attempt review |
| POST | `/api/pyq/questions/{question_id}/attempt` | Student | Server-side MCQ/MSQ/NAT checking and GATE scoring |
| PUT | `/api/pyq/bookmarks/{question_id}` | Student | Save/remove a question bookmark |
| GET | `/api/pyq/history` | Student | Private question attempt history |
| GET | `/api/pyq/summary?paper_code=CS` | Student | Attempt count, latest accuracy and bookmarks |
| GET | `/api/practice/catalog?paper_code=CS` | Student | Practice coverage by section, topic, difficulty and question type |
| GET | `/api/practice/questions?paper_code=CS` | Student | Filtered original practice questions without answer keys |
| GET | `/api/practice/daily-challenge?paper_code=CS` | Student | Date-specific five-question challenge |
| POST | `/api/practice/sessions` | Student | Create topic, custom or daily timed practice session |
| GET | `/api/practice/sessions/{session_id}` | Student | Resume an owned practice session and inspect submitted answers |
| POST | `/api/practice/sessions/{session_id}/attempt` | Student | Server-side MCQ/MSQ/NAT answer checking and explanation |
| POST | `/api/practice/sessions/{session_id}/finish` | Student | Finish a timed session and save its score |
| GET | `/api/practice/summary?paper_code=CS` | Student | Latest accuracy, weak topics, recent mistakes and sessions |
| GET | `/api/mock-tests/pattern?paper_code=CS` | Student | Official paper-specific GATE 2027 pattern and marking rules |
| GET | `/api/mock-tests/catalog?paper_code=CS` | Student | Validated full mock catalogue and recent attempts |
| POST | `/api/mock-tests/sessions` | Student | Start a full-length mock session |
| GET | `/api/mock-tests/sessions/{session_id}` | Student | Resume an active mock or review a submitted/expired result |
| PATCH | `/api/mock-tests/sessions/{session_id}/responses/{question_id}` | Student | Save an answer, visit state, time spent or review flag |
| POST | `/api/mock-tests/sessions/{session_id}/submit` | Student | Submit/auto-finalise a mock and calculate score |
| GET | `/api/mock-tests/history?paper_code=CS` | Student | Recent mock attempts and scores |
| POST | `/api/auth/register` | Public | Create a student account |
| POST | `/api/auth/login` | Public | Sign in |
| POST | `/api/auth/logout` | Session | Sign out |
| GET | `/api/auth/me` | Session | Current user and profile |
| GET/PUT | `/api/profile` | Session | Read/update student preferences |
| GET/POST | `/api/tasks` | Session | Read/create study tasks |
| PATCH/DELETE | `/api/tasks/{id}` | Session | Update/delete an owned task |
| GET | `/api/dashboard` | Session | Student dashboard and learning progress |
| POST | `/api/planner/plans` | Student | Generate or regenerate a 30/60/90-day personal study plan |
| GET | `/api/planner/overview?paper_code=CS&selected_date=YYYY-MM-DD` | Student | Plan progress, selected-day tasks, weak topics and upcoming revisions |
| POST | `/api/planner/tasks` | Student | Add a personal task to the active plan |
| PATCH | `/api/planner/tasks/{task_id}` | Student | Complete, reopen, skip, reschedule or rate a revision task |
| POST | `/api/planner/reschedule-overdue` | Student | Redistribute overdue pending tasks into the next seven days |


The frontend syllabus explorer supports topic search, progress filters and opening linked study notes. The Stage 5 study library contains 52 original GATEPath learning notes for the CS 2027 pilot. Stage 6 adds interactive syllabus-derived topic/subtopic graphs. Stage 7 adds the CS 2026 answer-key metadata bank with official question-paper links. Stage 8 adds 30 original draft practice questions across all 10 CS sections, daily challenges, timed practice sessions, answer explanations and weak-topic reporting. Stage 9 adds a full-length GATE-style CS mock with a server-authoritative timer, response persistence, mark-for-review, auto-submit, GATE scoring and question-by-question review. Both practice and mock questions are GATEPath originals, not official PYQs; the mock is subject to independent academic review. Student learning progress and attempts are stored per account. Other papers retain clear pending-content states until paper-specific data is imported and reviewed. Stage 10 adds a student-specific 30/60/90-day study planner, task scheduling, capacity-aware study blocks, weak-topic prioritisation from latest practice attempts, spaced revision, weekly mock/review blocks, overdue rescheduling and dashboard integration. The topic-level planner is available for CS only until other papers receive verified topic-level imports; the shared GA blocks link to the official syllabus and clearly disclose that detailed GA topic cards remain pending.

## Test and validate

From the project root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q backend/app
node --check frontend/app.js
node --check frontend/auth.js
node --check frontend/landing.js
```


## Stage 9 full mock-test content model

- `backend/app/data/mocks/gate2027_pattern.json` — paper-specific GATE 2027 format, section/optional-paper metadata and marking rules transcribed from the IIT Madras official question-paper-pattern page.
- `backend/app/data/mocks/CS-FULL-MOCK-01.json` — one original GATEPath CS full-length mock pilot with 65 questions, 180 minutes and 100 marks. The paper includes 10 GA questions (15 marks), 9 Engineering Mathematics questions (13 marks) and 46 core CS subject questions (72 marks). The 9-question/46-question split is this mock's authored allocation; the official pattern specifies marks and aggregate question counts, not a fixed number of questions for each of those two subject subgroups.
- The question set is original GATEPath content, not an official GATE paper, a PYQ import or a forecast. It requires independent subject-matter review before being relied on as exam-grade content.
- `mock_test_sessions` stores each student's active/submitted/expired test, server-side start/expiry, selected paper, question IDs and aggregate result. A partial unique index permits only one active full mock per student.
- `mock_test_responses` stores the answer, visited state, review flag and time spent per question. Answer keys and solutions are withheld until final submission.
- The server owns the 180-minute expiry and submits expired sessions on the next request. Answers persist across refresh; the current question is also remembered within the browser tab.
- Scoring follows the official GATE 2027 rules: incorrect MCQ penalty is one-third of a 1-mark or two-thirds of a 2-mark question; MSQ/NAT have no negative marking; MSQ has no partial marking.
- Before publication, the manifest validator checks question/marks totals, unique IDs, valid MCQ/MSQ option keys and NAT answer ranges. The original dataset underwent an answer-key audit and one NAT key was corrected to agree with its worked solution.
- Only the CS full mock is imported in this stage. All other paper-specific mock content remains explicitly pending until a complete paper is authored and validated. Special-section formats are represented in the pattern catalogue but are not falsely presented as playable mock papers yet.

See `docs/STAGE-9-CHECKLIST.md` and `docs/STAGE-9-CONTENT-SOURCES.md` for implementation, verification and content-provenance details.

## Stage 8 practice and quiz content model

- `backend/app/data/practice/CS-GATE-2027.json` — 30 GATEPath-authored practice pilot items mapped to the CS syllabus topic IDs, covering MCQ, MSQ and NAT formats and three difficulty labels.
- The file-level metadata states the original content origin and that independent academic review is still required; these are not official GATE questions or PYQs.
- `practice_sessions` stores the paper, mode, selected question IDs, server-side expiry, state and score.
- `practice_attempts` stores each student's submitted answer, correctness, awarded marks and time spent. A unique session/question key prevents duplicate submissions.
- The frontend supports topic/section filters, custom quiz length and duration, a five-question daily challenge, a question palette, answer explanations, session resume and result/weakness summaries.
- MCQ negative marking, exact-set MSQ checking and NAT tolerance are evaluated on the server. Answer keys are omitted from initial question payloads.
- Only CS has imported practice items at this stage. Other papers report pending content rather than substituting generic questions.

See `docs/STAGE-8-CHECKLIST.md` and `docs/STAGE-8-CONTENT-SOURCES.md` for feature validation and content review boundaries.

## Stage 7 PYQ bank content model

- `backend/app/data/pyq/catalog.json` — official previous-paper archive references.
- `backend/app/data/pyq/CS-2026.json` — 130 verified answer-key metadata records across GATE 2026 CS-1 and CS-2 (65 per session).
- `pyq_attempts` — student-owned attempt history, submitted answer, score and time spent.
- `pyq_bookmarks` — private saved-question collection.
- The question wording and figures remain on the official IIT-hosted PDF links. GATEPath checks answers on the server after submission and reveals the official key only after an attempt.
- MCQ/MSQ/NAT scoring follows the GATE 2026 official master-paper/key guidance. Selected questions have original GATEPath explanation notes; remaining explanations are explicitly marked as pending review.
- GATE 2025 and earlier papers are linked to official archives but have not yet been imported into the interactive answer-checking bank. Other GATE papers are also awaiting topic/question imports.

See `docs/STAGE-7-CHECKLIST.md` and `docs/STAGE-7-CONTENT-SOURCES.md` for scope, verification and provenance details.

## Official GATE 2027 sources

- GATE 2027 homepage: https://gate2027.iitm.ac.in/
- Official test papers and syllabus catalogue: https://gate2027.iitm.ac.in/exam_papers_and_syllabus
- Official question paper pattern: https://gate2027.iitm.ac.in/question_paper_pattern
- Official CS syllabus PDF: https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf

The organising institute states that GATE 2027 syllabi have been revised and lists 30 test papers. Always use the relevant current-year PDF rather than assuming an older syllabus is unchanged.

## Development roadmap

1. Stage 1 — Project foundation (complete)
2. Stage 2 — Public website UI/UX (complete)
3. Stage 3 — Authentication and student profiles (complete)
4. Stage 4 — Versioned multi-paper syllabus engine (complete for catalogue and CS import; remaining topic imports pending)
5. Stage 5 — Study-material library (complete for CS pilot; other papers queued)
6. Stage 6 — Interactive mind maps (complete for CS pilot; other-paper maps await verified topic imports)
7. Stage 7 — Verified previous-year question bank (complete for GATE 2026 CS-1/CS-2 metadata import; earlier years and other papers remain queued)
8. Stage 8 — Practice and quiz engine (complete for original CS pilot; content requires expert review and other papers remain queued)
9. Stage 9 — GATE-style mock-test engine (complete for the original CS pilot; other-paper question imports pending)
10. Stage 10 — Personalised study planner and revision scheduling (complete for the CS topic import; other-paper topic planners await verified syllabus imports)
11. Stage 11 — AI tutor and grounded retrieval (complete for CS local retrieval; provider integration is optional)
12. Stage 12 — Analytics, community and admin experience (complete)
13. Stage 13 — Full integration, security, accessibility and QA (complete)
14. Stage 14 — Production deployment and final verification (next)


## Stage 10 planner data model

- `study_plans` stores a user's active/archived plan, selected paper, 30/60/90-day duration, daily study-hour capacity and date range.
- `planner_tasks` stores generated learning/practice/revision/mock blocks and personal tasks with per-student completion state.
- `planner_revision_queue` stores per-topic due dates, review intervals and recall-quality adaptation.
- The planner gives first priority to topics with under 60% latest-attempt accuracy, then in-progress and not-started topics. It does not use raw all-time retry counts.
- A completed learning block changes an uncompleted topic to `in_progress` while preserving a previously completed topic. Completing a revision task updates its next spaced-review date.
- The scheduler reserves weekly mock/review days from the normal topic workload, reports any imported topics that cannot fit the selected time horizon, and redistributes overdue tasks when possible.
- Only CS has topic-level syllabus imports at this stage. Other papers receive a pending-content response, not a fabricated plan. General Aptitude is scheduled as source-led study and still needs topic-level import.

See `docs/STAGE-10-CHECKLIST.md` and `docs/STAGE-10-CONTENT-SOURCES.md` for the planner routes, scheduling rules, source boundaries and validation record.

Stage 11 validation: `python -m pytest backend/tests -q` passes 112 tests. The tutor API, static UI assets, authentication guards and additive SQLite migration have been smoke-checked. Provider request construction and image handoff are covered with a mocked HTTP client; live generation requires the student's/server administrator's AI provider configuration.


## Stage 12 analytics, community and administration

- `GET /api/analytics` aggregates only the signed-in student's recorded syllabus progress, latest practice/PYQ attempts, planner completions, recent activity and mock-test history. It does not fabricate study time, topic mastery for unattempted content, a GATE score forecast or an AIR prediction.
- The Analytics workspace shows 14-day activity, subject/topic accuracy, weak topics and mock history. Accuracy groups latest results per question so retries do not inflate the unique-question count.
- Community data is stored in `community_posts`, `community_replies`, `community_post_likes` and `community_reports`. Students can create paper-specific discussions, reply, react, remove their own content and report posts/replies. Moderators can hide or remove content. The UI renders posts as escaped plain text.
- Admin review states are stored in `admin_content_reviews`; the admin queue covers imported study notes, original practice questions and PYQ answer-key metadata. Approval is editorial workflow status, not a warranty of academic correctness, official endorsement or licensing.
- The Admin workspace supports account search/status, session revocation on student deactivation, pending report handling, pin/hide/remove moderation, paper coverage and content review filters. Every `/api/admin/*` endpoint uses the `require_admin` role guard.
- Bootstrap the first administrator by setting `GATEPATH_ADMIN_EMAIL` and `GATEPATH_ADMIN_PASSWORD` in the backend `.env` before initial startup. The create-only bootstrap does not promote an existing student or overwrite an existing account. Never commit production credentials.
- New tables: `community_posts`, `community_replies`, `community_post_likes`, `community_reports`, `admin_content_reviews`. Migrations are additive.

See `docs/STAGE-12-CHECKLIST.md` and `docs/STAGE-12-CONTENT-SOURCES.md` for tests, content boundaries and operational notes.


## Stage 13 integration and quality assurance

- Duplicate Stage 12 route registrations were removed; each API method/path is registered once.
- FastAPI startup now uses the lifespan interface, removing the deprecated `on_event` startup hook.
- All 18 duplicate Stage 12 route registrations were removed; API method/path pairs are unique.
- Production startup refuses to run unless `APP_BASE_URL` uses HTTPS and `GATEPATH_SECURE_COOKIES=true`.
- `GET /api/health` is the liveness probe; `GET /api/health/ready` checks SQLite access and the required 30-paper catalogue.
- Security response headers include Content Security Policy, anti-framing, MIME sniffing protection, a restrictive referrer policy and permissions policy. API and authenticated-page responses use `Cache-Control: no-store`.
- Cookie `Secure` can be forced with `GATEPATH_SECURE_COOKIES=true` when TLS terminates at a reverse proxy. Set this only when the public app is served over HTTPS.
- `GATEPATH_DATABASE_PATH` controls the SQLite file location. Relative paths resolve from the project root. `DATABASE_URL` is accepted for backwards compatibility only when it is a SQLite URL.
- Install runtime dependencies from `requirements.txt`; install test dependencies from `requirements-dev.txt`.
- Run the static integration gate using `python scripts/check_project.py` and the automated suite using `python -m pytest -q`. Each test module can also be run independently, for example `python -m pytest -q backend/tests/test_stage13.py`.
- See `docs/STAGE-13-CHECKLIST.md` and `docs/STAGE-13-QA-REPORT.md` for the exact scope and verification limits.
- A GitHub Actions workflow checks Python 3.11, 3.12 and 3.13, data integrity, frontend syntax and tests on pushes and pull requests.

Visual, cross-device and live-provider checks still require a browser-capable local environment and the relevant SMTP/AI credentials. The app must be reviewed manually before public release; this automated QA stage is not a substitute for production security review or academic content validation.

## Deployment status and hosting

The application source includes a Render Docker deployment configuration with a persistent disk for the existing SQLite database. Vercel can be used for preview and API smoke testing via the root `index.py` entrypoint, but the current SQLite database is not durable on Vercel Functions. See [`docs/VERCEL_DEPLOYMENT.md`](docs/VERCEL_DEPLOYMENT.md) before enabling production traffic.

