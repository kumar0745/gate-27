# Stage 9 — Full GATE Mock Test Engine

Status: implemented for the GATE CS 2027 pilot. This extends the existing GATEPath project; no ZIP/package is produced during staged development.

## Student experience

- [x] Full-length mock catalogue with content-origin and review-status labels.
- [x] Paper-specific GATE 2027 pattern endpoint for all 30 paper codes.
- [x] Full-length CS pilot: 65 questions, 180 minutes and 100 marks.
- [x] GATE-style question player with MCQ, MSQ and NAT controls.
- [x] Numbered question palette with answered, unanswered, current and marked-for-review states.
- [x] Previous/next navigation, direct question jump, clear response and mark/unmark review.
- [x] Answer autosave to the backend and restore after refresh.
- [x] Server-authoritative expiry; the browser countdown is display-only and derives from the server expiry timestamp.
- [x] Expired sessions are finalised as expired on the next request; an abandoned expired session does not block a new attempt.
- [x] One active full-length mock per student, enforced by a partial unique database index and a conflict response.
- [x] Manual submit, automatic expiry submit and idempotent result retrieval.
- [x] Section-wise and subject-wise performance summary.
- [x] Question-by-question answer review with original worked explanations.
- [x] Recent history and result reopening.
- [x] Browser-tab current-question recovery; saved responses are authoritative across sessions/devices.

## API routes

- `GET /api/mock-tests/pattern?paper_code=CS`
- `GET /api/mock-tests/catalog?paper_code=CS`
- `POST /api/mock-tests/sessions`
- `GET /api/mock-tests/sessions/{session_id}`
- `PATCH /api/mock-tests/sessions/{session_id}/responses/{question_id}`
- `POST /api/mock-tests/sessions/{session_id}/submit`
- `GET /api/mock-tests/history?paper_code=CS`

All mock-test routes require an authenticated student. Sessions and response rows are scoped by user ID; another student receives not-found for another student's session.

## Database

- `mock_test_sessions`: user, test/paper code, question IDs, duration, server start and expiry timestamps, status, aggregate score and submission timestamp.
- `mock_test_responses`: one row per session/question, with answer, review flag, visited state, time spent and update timestamp.
- A partial unique index permits at most one row with `status = 'active'` per student. Expired-but-abandoned sessions are finalised before creating a new test.
- Schema updates are additive. No prior tables or student progress records are removed.

## Paper structure and scoring

- The current CS mock is authored against the published GATE 2027 CS pattern: 10 General Aptitude questions (15 marks), 55 subject questions (85 marks), 65 questions overall and 180 minutes.
- Inside the 85 subject marks, this authored mock allocates 13 marks to Engineering Mathematics and 72 marks to other CS topics. Its 9-question/46-question split is an editorial allocation for this mock, not a separately fixed official question-count requirement.
- One-mark incorrect MCQ: −1/3. Two-mark incorrect MCQ: −2/3. Incorrect MSQ/NAT: no negative marking. MSQ: no partial marking.
- The pattern catalogue also records the official special section/choice structures for AR, GE, GG, RA, XE, XH and XL. It does not claim those papers have playable mock question banks until their content is imported and validated.

## Content provenance and review boundary

- `backend/app/data/mocks/gate2027_pattern.json` is the official pattern metadata/source register.
- `backend/app/data/mocks/CS-FULL-MOCK-01.json` is one original GATEPath practice mock, not an official GATE question paper, not a PYQ import, and not an exam prediction.
- The mock is labelled as original content and subject to independent academic/SME review. It must not be marketed as expert-verified until that review is completed.
- MCQ/MSQ keys must match the option keys; NAT answer keys must be numeric and fall inside their accepted inclusive ranges. The manifest validator enforces these conditions, along with unique IDs and question/marks/section totals.
- One NAT answer key was corrected during the final content audit so that it matches its own worked solution (FCFS average waiting time = 13/3 ms).

## Validation

- `python -m pytest backend/tests -q` — 75 passed at Stage 9 handoff.
- `python -m compileall -q backend/app` — passed.
- `node --check frontend/app.js` — passed.
- `node --check frontend/auth.js` — passed.
- `node --check frontend/landing.js` — passed.
- Test suite includes authentication, ownership, answer secrecy before submission, autosave/resume, MCQ/MSQ/NAT scoring, section breakdown, expired-session finalisation, abandoned-session cleanup, manifest integrity and static asset delivery.
- Two non-blocking FastAPI deprecation warnings remain from the existing startup event hook. Stage 13 includes lifecycle cleanup.
- Full Chromium visual automation could not be completed in this environment because the browser policy blocks navigation to the local app (`ERR_BLOCKED_BY_ADMINISTRATOR`). API, static-resource and automated integration tests are the verification basis; do not claim visual browser acceptance.
