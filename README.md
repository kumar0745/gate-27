# GATEPath 2027 — Computer Science and Information Technology (CS)

GATEPath is a single-paper preparation workspace for **GATE 2027 CS**. It covers the official Computer Science and Information Technology syllabus and the shared General Aptitude section. It does not offer DA, IN, or any other GATE paper.

The website opens directly into a guest workspace. There is no sign-in or registration screen. A random browser session cookie keeps study activity associated with the current guest workspace; it is not an account or cross-device identity system.

## Official GATE 2027 sources

- [CS syllabus PDF — IIT Madras](https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf)
- [General Aptitude syllabus PDF — IIT Madras](https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/GA_GATE2027_Syllabus.pdf)
- [Official paper list and syllabus page](https://gate2027.iitm.ac.in/exam_papers_and_syllabus)
- [Official question-paper pattern](https://gate2027.iitm.ac.in/question_paper_pattern)
- [Official question-paper and answer-key archive](https://gate2027.iitm.ac.in/download)

The app's exam-pattern reference is 180 minutes, 65 questions and 100 marks. General Aptitude is 10 questions / 15 marks; CS is 85 marks, including 13 marks for Engineering Mathematics and 72 marks for the remaining CS subject syllabus. Question types are MCQ, MSQ and NAT. Only MCQs carry negative marking; MSQ/NAT wrong answers do not, and MSQs have no partial marks. Always check the official instructions for the applicable examination year.

## What's included

- One CS-only paper catalogue entry.
- Ten CS subject syllabus sections plus General Aptitude (Verbal, Quantitative, Analytical and Spatial Aptitude).
- 56 GATEPath-authored study notes mapped to the official syllabus.
- 38 GATEPath-authored practice questions, including a General Aptitude practice set.
- 130 GATE 2026 CS-1/CS-2 answer-key metadata records with topic mappings, links to official question PDFs and official answer keys.
- Official CS question-paper and answer-key PDF links for 2021–2026.
- CS mind maps, topic-level progress, study planner, revision, timed practice, mock tests, analytics and a study assistant.

**Content provenance matters:** the syllabus statements and official-paper links are sourced from IIT Madras. GATEPath notes, worked examples, practice questions and mock questions are supplemental editorial content, not official GATE questions. The 130 interactive PYQ records are answer-key metadata and mappings; the app does not republish the copyrighted original question stems or figures. Open the official PDFs for the original papers.

## Run locally

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/check_project.py
python -m pytest backend/tests -q
python -m uvicorn index:app --reload --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/check_project.py
python -m pytest backend/tests -q
python -m uvicorn index:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The app creates a guest workspace automatically. `/api/health` is a liveness check and `/api/ready` checks database readiness.

## Database and deployment

- Local development uses SQLite.
- `render.yaml` configures a persistent Render disk for the SQLite database.
- Vercel preview uses `/tmp/gatepath.db` strictly for smoke tests. That filesystem is ephemeral and may be reset or differ between instances.
- **Do not use the Vercel preview for durable student records.** Production on Vercel requires migrating the SQLite adapter/schema to a managed persistent database (for example, Postgres) and configuring its production connection. The application intentionally fails fast on Vercel production while only the ephemeral SQLite adapter is configured.

See [CS-only track and content provenance](docs/CS-ONLY-TRACK.md) and [deployment guide](docs/STAGE-14-DEPLOYMENT.md).

## Repository layout

```text
backend/app/main.py                  FastAPI routes and application logic
backend/app/database.py              SQLite adapter and persistence safeguards
backend/app/data/papers.json         CS-only paper catalogue
backend/app/data/syllabi/            CS + General Aptitude syllabus
backend/app/data/materials/          Editorial study notes
backend/app/data/practice/           Original practice question bank
backend/app/data/pyq/                Official archive links and answer-key metadata
backend/app/data/mocks/              GATE pattern and CS mock manifest
backend/tests/                       Automated API/content tests
frontend/index.html                  Guest workspace shell
frontend/app.js                      Workspace client
frontend/app.css                     Workspace styling
scripts/check_project.py             Data and integration checks
index.py                             Vercel FastAPI entrypoint
vercel.json                          Vercel routing/configuration
render.yaml                          Persistent-disk Render configuration
```

## Verification

```bash
python scripts/check_project.py
python -m compileall -q backend
node --check frontend/app.js
python -m pytest backend/tests -q
```

The CI workflow runs these integrity and test checks on Python 3.11, 3.12 and 3.13.
