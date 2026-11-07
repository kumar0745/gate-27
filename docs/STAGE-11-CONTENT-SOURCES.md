# Stage 11 — Tutor source and provider notes

## Local retrieval corpus

Primary learning-note corpus:

- `backend/app/data/materials/CS-GATE-2027.json`
- Paper code: CS
- 52 topic entries across 10 sections
- Content status: GATEPath original editorial learning notes mapped to the official GATE 2027 CS syllabus
- Official topic scope reference: https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf

The RAG retriever returns note-specific excerpts with source IDs. The UI shows both the note status and the official syllabus link. A syllabus PDF link is not presented as the source of explanatory prose authored by GATEPath.

For paper codes with no imported materials file, the tutor displays the relevant official syllabus PDF link and states that topic-wise notes are not yet indexed.

## AI provider

The AI layer uses an OpenAI-compatible Chat Completions API over HTTPS, configured with `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` in the backend environment. The sample model value is an example and may be replaced with a model supported by the selected provider. A vision-capable model is required to inspect question images.

No AI API key is embedded in the frontend, database, or response payload. GATEPath does not claim that generated answers are verified or official. Provider use may be subject to the provider's own data-processing and retention terms.

## Image handling

Accepted formats are PNG, JPEG and WEBP. The backend checks declared MIME, base64 structure, file signature and a 5 MB limit. The raw image is not stored in conversation records; only an attachment flag is retained. If the provider is unconfigured, the tutor clearly states that it did not interpret the image.

## Similar-question content

With a configured provider, similar-question output is original AI-generated practice and explicitly not an official GATE PYQ. Without a provider, the API returns existing GATEPath practice items for the topic, without answer keys. No AI-generated item is silently inserted into the verified PYQ archive.
