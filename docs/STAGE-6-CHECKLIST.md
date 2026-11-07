# Stage 6 — Interactive Mind Map System

Status: **Implemented for the structured GATE CS 2027 pilot**

## Delivered

- Student-authenticated `GET /api/mindmaps` endpoint with paper and section selection.
- Graph nodes generated from the imported syllabus JSON; root, topic and subtopic hierarchy is data-driven.
- Hierarchy edges and explicit prerequisite relationships.
- Prerequisite references resolve to their source subject, including prerequisites outside the active subject map.
- Student-specific topic progress and bookmark state appears on topic nodes.
- Topic nodes link to the Stage 5 study note when an original note is available.
- Interactive SVG interface with topic selection, subject switching, zoom controls, drag/pan, fullscreen and SVG export.
- Optional subtopic visibility control.
- Responsive desktop/mobile layout with light and dark theme styling.
- Clear pending-import response for papers that do not yet have structured topic-level syllabus data.
- No generated mind map is labelled as an official exam prediction or marks-weightage forecast.

## API

`GET /api/mindmaps?paper_code=CS&section_code=CS-01`

Response contains:

- `sections`: subjects in the selected paper and topic/subtopic counts.
- `active_section`: selected subject.
- `nodes`: root, topic and subtopic nodes with source and progress metadata.
- `edges`: hierarchy links and same-subject prerequisite links.
- `relationships`: resolved prerequisites, including links to other subjects.
- `summary`: topic, subtopic and prerequisite counts.

The endpoint requires a logged-in student. A paper without a structured syllabus returns `content_status=awaiting_structured_import`, no fabricated topic nodes, and its official syllabus PDF URL.

## Content scope and limitations

The CS mind maps are generated from `backend/app/data/syllabi/CS-GATE-2027.json`. Topic and subtopic labels follow the imported syllabus. Prerequisite links in the data are GATEPath learning guidance and are not official examination requirements. The General Aptitude common-section topic import and topic-level syllabus imports for other papers remain pending.

## Validation

- Backend API and data tests are in `backend/tests/test_mindmaps.py`.
- Frontend JavaScript syntax is checked using `node --check frontend/app.js`.
- Full backend test suite is run using `python -m pytest backend/tests -q`.
- A Chromium visual smoke test was attempted, but local-page navigation returned `ERR_BLOCKED_BY_ADMINISTRATOR` in this runtime. Therefore, visual browser verification is not claimed as complete.
