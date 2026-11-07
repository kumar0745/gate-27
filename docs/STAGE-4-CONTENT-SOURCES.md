# GATE 2027 syllabus source register

Checked: 5 November 2026

The official GATE 2027 website states that the syllabi have been revised and lists 30 test papers. Each paper/code links to its official 2027 syllabus PDF. GATEPath stores those official source URLs in `backend/app/data/papers.json`.

## Official source catalogue

- GATE 2027 test papers and syllabus: https://gate2027.iitm.ac.in/exam_papers_and_syllabus
- GATE 2027 question paper pattern: https://gate2027.iitm.ac.in/question_paper_pattern
- Shared General Aptitude PDF: https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/GA_GATE2027_Syllabus.pdf

## Transcribed paper

- CS — Computer Science and Information Technology: https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf
- Local structured import: `backend/app/data/syllabi/CS-GATE-2027.json`
- Source checked: 5 November 2026
- PDF structure: 10 paper-specific sections across two pages.
- GATEPath representation: 10 sections, 52 topics and topic/subtopic navigation labels.

The topic `official_statement` fields preserve the source syllabus scope in a readable string. `subtopics` split that statement for navigation and tracking. They are not intended as additions to the official scope.

## Sectional papers

GATE 2027 uses revised sectional codes for XE, XH and XL. The paper catalogue records the official section codes and the common/optional section selection structure as published on the official syllabus page. The combined PDFs are linked directly from the catalogue.

## Coverage status

- CS: `imported_verified` — structured paper-specific content available.
- Remaining 29 papers: `official_source_linked` — official PDF link present; topic-level content import still pending.
- General Aptitude: official shared PDF link present; topic-level import pending.

Do not interpret `official_source_linked` as a completed structured syllabus import.
