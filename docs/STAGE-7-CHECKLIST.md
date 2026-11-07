# Stage 7 — Previous-Year Question Bank

Status: implemented for the GATE 2026 Computer Science & Information Technology CS-1 and CS-2 master papers.

## Delivered

- [x] Official source catalogue with year-wise/archive links.
- [x] 130 verified answer-key metadata records (65 CS-1 + 65 CS-2).
- [x] Session, year, question type, section, topic and bookmark filters.
- [x] MCQ, MSQ and NAT answer entry.
- [x] Server-side answer checking so keys are not exposed before submission.
- [x] GATE 2026 scoring rules: one-third negative marking for incorrect MCQs; no negative marking for MSQ/NAT; MSQ all-or-nothing; NAT accepted ranges.
- [x] Original worked explanation notes for selected CS-1 questions.
- [x] Student-private attempt history, time spent and bookmarks.
- [x] Latest-attempt accuracy and question-bank summary.
- [x] Syllabus topic mapping for reviewed CS-1 questions Q12–Q27 where the source topic was identified.
- [x] Official question paper and answer-key links for every imported session.
- [x] Question wording and figures remain hosted on the official IIT Guwahati PDFs; GATEPath stores source metadata, answer-key metadata and original explanation text.
- [x] Additive SQLite migration; existing student accounts and learning progress are preserved.

## Scope still pending

- Interactive year-wise imports for GATE 2025 and earlier papers.
- Verified interactive imports for papers other than CS.
- Topic mapping for the remaining imported CS questions.
- Editorial worked explanations for every question. Questions without a reviewed explanation are explicitly marked as pending after the student submits an answer.
- Production visual browser test and deployment validation.

## Main files

- `backend/app/data/pyq/catalog.json`
- `backend/app/data/pyq/CS-2026.json`
- `backend/app/main.py`
- `backend/app/database.py`
- `backend/tests/test_pyq.py`
- `frontend/app.js`
- `frontend/app.css`

## API

- `GET /api/pyq/catalog?paper_code=CS`
- `GET /api/pyq/questions?paper_code=CS&year=2026`
- `GET /api/pyq/questions/{question_id}`
- `POST /api/pyq/questions/{question_id}/attempt`
- `PUT /api/pyq/bookmarks/{question_id}`
- `GET /api/pyq/history`
- `GET /api/pyq/summary?paper_code=CS`

All student routes require a valid GATEPath session. The expected answer is not included in question-list/detail responses until the student has submitted an attempt.

## Validation

Run from the project root:

```bash
python -m pytest backend/tests -q
python -m compileall -q backend/app
node --check frontend/app.js
node --check frontend/auth.js
node --check frontend/landing.js
```
