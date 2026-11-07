# Stage 8 — Practice and Quiz Engine

Status: implemented for the GATE CS 2027 pilot. This stage extends the existing GATEPath project and does not create a separate build or ZIP package.

## Student-facing functionality

- [x] Practice catalogue mapped to the 10 structured CS syllabus sections.
- [x] 30 original GATEPath practice questions distributed across all 10 CS sections.
- [x] MCQ, MSQ and NAT question formats.
- [x] Beginner, Intermediate and Advanced difficulty labels.
- [x] Search and filter by section, topic, difficulty and question type.
- [x] Custom practice sessions with configurable question count and duration.
- [x] Topic/section-focused sessions.
- [x] Daily five-question challenge selected deterministically by paper and date.
- [x] Server-side session creation, expiry, answer submission and finish operation.
- [x] In-session question palette, answer state, timer and navigation.
- [x] Session recovery after page refresh through a stored session identifier and server expiry.
- [x] Per-question original explanation shown after answer submission.
- [x] Session score, attempted/correct count, accuracy and overall practice summary.
- [x] Latest-attempt-per-question accuracy and weak-topic reporting.
- [x] Recent incorrect answers shown as a review list.
- [x] Practice sessions and attempts scoped to the authenticated student.

## API routes

- `GET /api/practice/catalog?paper_code=CS`
- `GET /api/practice/questions?paper_code=CS&section_code=CS-08&difficulty=Intermediate&question_type=NAT`
- `GET /api/practice/daily-challenge?paper_code=CS`
- `POST /api/practice/sessions`
- `GET /api/practice/sessions/{session_id}`
- `POST /api/practice/sessions/{session_id}/attempt`
- `POST /api/practice/sessions/{session_id}/finish`
- `GET /api/practice/summary?paper_code=CS`

All routes except the app's public routes require a signed-in student session.

## Storage

- `practice_sessions`: paper, mode, selected question IDs, time window, status and aggregate result.
- `practice_attempts`: student-owned answer, correctness, score and time per question in a session.
- A unique constraint on `(session_id, question_id)` prevents repeated submissions for the same question in one session.
- Foreign keys cascade session/attempt cleanup when an account is removed.

## Scoring

- Incorrect MCQ: deduct one-third of the question marks.
- MSQ: exact option set required; no partial marking or negative marking.
- NAT: inclusive accepted numeric range; no negative marking.
- Unanswered questions receive zero marks.
- Scoring occurs on the backend; the initial question payload omits answer keys and explanations.
- The question answer and explanation become visible only after the student submits the answer.

## Content boundaries

- `backend/app/data/practice/CS-GATE-2027.json` contains 30 original GATEPath practice questions.
- The items are not official GATE questions and are not previous-year questions.
- The seed records identify their origin as original GATEPath content and state that academic review is required before public release.
- The 30 questions are mapped to the imported 2027 CS syllabus topic IDs. The seed is a feature pilot, not a complete CS practice bank.
- Other GATE papers return an explicit `awaiting_practice_import` state until paper-specific content is prepared and reviewed.

## Validation

- `pytest -q backend/tests/test_practice.py`
- `pytest -q backend/tests`
- `python -m py_compile backend/app/main.py backend/app/database.py`
- `node --check frontend/app.js`

Current full regression result at stage handoff: 59 passed. FastAPI's legacy startup event hook emits a deprecation warning; it is not a test failure and is logged for Stage 13 cleanup.
