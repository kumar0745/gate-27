# Stage 6 — Mind Map Content Sources and Provenance

## Primary source

- GATE 2027 official exam papers and syllabus catalogue: https://gate2027.iitm.ac.in/exam_papers_and_syllabus
- Official GATE 2027 Computer Science and Information Technology syllabus PDF: https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf

## Data handling

The mind-map graph is not independently transcribed from memory. It is generated from the Stage 4 structured syllabus JSON at `backend/app/data/syllabi/CS-GATE-2027.json`.

- Section labels, topic labels, official statement text and subtopic labels are loaded from the imported syllabus data.
- Topic-to-subtopic hierarchy edges are generated from the `subtopics` arrays.
- Prerequisite relationships are read from the optional `prerequisites` topic-ID arrays. These are GATEPath learning guidance, not statements from IIT Madras and not predictions of exam questions or marks weightage.
- A topic node exposes a study-note action only when its topic ID exists in `backend/app/data/materials/CS-GATE-2027.json`.
- Student completion and bookmark labels are loaded from account-owned progress records.

Other papers and the shared General Aptitude section remain explicitly pending structured topic imports. No topic nodes are fabricated for those papers.
