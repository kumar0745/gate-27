# Stage 4 — Versioned GATE syllabus engine

Status: implemented in the local project; verified by automated API tests.

## Implemented

- [x] Central catalogue for all 30 GATE 2027 papers.
- [x] Official syllabus PDF link stored for each paper.
- [x] XE, XH and XL sectional codes and selection structure represented separately.
- [x] GATE CS topic hierarchy transcribed from the official 2027 two-page CS PDF.
- [x] 10 CS syllabus sections and 52 topic records, with scope statements and navigational subtopic chips.
- [x] Common General Aptitude section represented separately (15 marks) with the official PDF link.
- [x] Unimported papers remain clearly marked as source-linked; no speculative topic hierarchy is presented as official content.
- [x] Additive SQLite migrations for syllabus versions, student progress and admin topic edits.
- [x] Per-student topic progress (`not_started`, `in_progress`, `completed`) isolated by account, paper and syllabus version.
- [x] Syllabus search/filtering by topic, section and progress state.
- [x] Admin-only syllabus version review and topic edit APIs.
- [x] Student dashboard now reports real completed-topic percentage for imported paper tracks.
- [x] Workspace HTML/CSS shell restored so `/app` can serve the existing app.js workspace.
- [x] Root requirements, `.gitignore`, and local start scripts added.

## Deliberate content boundary

Only CS is fully transcribed into the topic engine in this stage. Its section titles and syllabus scope statements were checked against the official GATE 2027 CS syllabus PDF. Topic and subtopic boundaries are a navigational breakdown of those official statements; the `prerequisites` field is optional pedagogical guidance and is not represented as official GATE wording.

For the other 29 papers, the catalogue stores links to the corresponding official IIT Madras GATE 2027 syllabus PDFs. Their detailed topic imports will be populated in later content passes after the source PDFs are transcribed and reviewed. The site must not show guessed topics as official.

The common GA PDF link is recorded, but its topic-by-topic transcription is not yet included.

## Main files

- `backend/app/data/papers.json`
- `backend/app/data/syllabi/CS-GATE-2027.json`
- `backend/app/database.py`
- `backend/app/main.py`
- `frontend/index.html`
- `frontend/app.css`
- `frontend/app.js`
- `backend/tests/test_syllabus.py`

## Verification

Run from the project root:

```bash
python -m pytest backend/tests -q
node --check frontend/app.js
node --check frontend/auth.js
node --check frontend/landing.js
python -m compileall backend/app
```

API coverage includes the 30-paper catalogue, official source links, CS hierarchy, sectional paper sections, per-student progress, account isolation, search, student/admin permissions, admin edits and the authenticated workspace route.
