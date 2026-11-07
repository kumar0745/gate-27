# Stage 8 — Practice content provenance

## Content inventory

File: `backend/app/data/practice/CS-GATE-2027.json`

- 30 original GATEPath-authored pilot questions.
- 10 CS syllabus sections represented.
- Question types: 11 MCQ, 6 MSQ and 13 NAT.
- Difficulty labels: 18 Beginner, 7 Intermediate and 5 Advanced.
- Every item includes a topic ID, marks, prompt, answer key/range and an original explanation.

## Official scope reference

The question-to-topic mapping is based on the GATE 2027 CS syllabus published by IIT Madras:

- https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf
- Syllabus catalogue: https://gate2027.iitm.ac.in/exam_papers_and_syllabus
- Question-paper pattern and scoring reference: https://gate2027.iitm.ac.in/question_paper_pattern

The official syllabus is the source of paper/topic scope. GATEPath's optional subtopic grouping and difficulty classification are editorial learning metadata, not official GATE classifications.

## Originality and review status

- These are newly authored practice examples and are not copied or represented as official GATE questions.
- They are separate from the Stage 7 PYQ archive.
- Each data record carries the GATEPath practice origin through the dataset-level `content_origin` and `editorial_status` fields.
- The pilot content is AI-drafted and has not undergone independent faculty/subject-expert review. It must be academically reviewed, proofread and revalidated before being described as expert-verified or relied on as a complete preparation resource.
- Students are shown a clear in-product notice explaining this status.

## Scoring conventions implemented

The checker applies the familiar GATE-style question-type rules used for practice: one-third negative marking for an incorrect MCQ, no negative/partial marking for MSQ, and no negative marking for NAT. It applies the configured marks per practice item. These practice questions are not an official GATE exam or a rank/score predictor.
