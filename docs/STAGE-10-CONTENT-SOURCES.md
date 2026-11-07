# Stage 10 — Planner content and logic sources

The study planner does not introduce new GATE syllabus scope. It consumes the existing versioned syllabus and learning content already held in the project:

- `backend/app/data/syllabi/CS-GATE-2027.json` — topic and section structure transcribed from the official GATE 2027 CS syllabus PDF.
- `backend/app/data/materials/CS-GATE-2027.json` — GATEPath-authored learning notes mapped to those topic IDs.
- `backend/app/data/practice/CS-GATE-2027.json` — original GATEPath practice question metadata used to identify topics with an available practice set. The practice set remains labelled as AI-drafted pilot content requiring academic review.
- `backend/app/data/mocks/CS-FULL-MOCK-01.json` — original GATEPath full-length mock manifest used only to decide whether a full mock block can be scheduled. It is not an official GATE paper and requires independent academic review.
- `https://gate2027.iitm.ac.in/exam_papers_and_syllabus` — official common General Aptitude and paper syllabus catalogue link shown in source-led GA study tasks.

The adaptive priority uses the latest recorded attempt for each question, not a student's entire retry history, to avoid inflating or depressing a topic's current accuracy based on repeated attempts. A topic with under 60% latest-attempt accuracy receives a higher scheduling priority.

The planner's study durations and scheduling heuristics are GATEPath product defaults, not official GATE rules or a guarantee of a particular score/rank. Students can customise their daily study-hour target and regenerate a plan.
