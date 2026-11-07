# Stage 12 — Data Sources and Interpretation

Stage 12 does not introduce new official GATE syllabus or question content. It aggregates records already stored by GATEPath.

## Analytics source records

- Syllabus completion: `student_material_progress` joined conceptually to the imported `CS-GATE-2027.json` topic map.
- Practice accuracy: latest `practice_attempts` row per question ID, with metadata from the paper's original practice JSON.
- PYQ accuracy: latest `pyq_attempts` row per question ID, with metadata from available PYQ JSON archives.
- Mock-test results: submitted/expired `mock_test_sessions` rows.
- Study time/activity: completed `planner_tasks`, recorded practice/PYQ attempts, and submitted mock sessions.

Analytics intentionally avoid extrapolating an all-India rank, predicted score, unrecorded study hours or mastery for topics without attempt data.

## Community content

Community discussions and replies are user-generated. Authors remain accountable for their posts. GATEPath includes report, hide, remove and pin actions for moderators. The application uses escaped plain text rather than rendering user-supplied HTML/Markdown.

## Admin review data

The review queue is constructed from locally imported materials, practice questions and PYQ key metadata. Review status and moderator notes are stored separately in `admin_content_reviews`, allowing content source files to remain version-controlled. A status of `approved` means an administrator completed the platform's editorial workflow; it is not a guarantee of correctness, official endorsement or copyright permission.

## Admin account bootstrap

The first administrator can be created with `GATEPATH_ADMIN_EMAIL` and `GATEPATH_ADMIN_PASSWORD` in the backend environment before the first database startup. The bootstrap is create-only; it does not alter an existing account with that email.
