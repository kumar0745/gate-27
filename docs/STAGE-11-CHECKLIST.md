# Stage 11 — AI GATE Tutor

## Implemented

- [x] Authenticated tutor status endpoint with provider readiness, active paper, indexed-topic count, topic catalogue and privacy notice.
- [x] Paper-aware local retrieval over structured GATEPath study notes using an explainable BM25-like lexical ranker.
- [x] Retrieval returns stable source IDs, topic names, syllabus section, excerpt, source URL and editorial content status.
- [x] Beginner and advanced explanation modes.
- [x] OpenAI-compatible Chat Completions integration configured only through server-side environment variables.
- [x] Optional multimodal image-question handoff for a vision-capable configured model.
- [x] Image MIME, base64 signature and 5 MB size validation.
- [x] No raw image bytes or data URLs are persisted in GATEPath conversation storage.
- [x] Student-owned conversation and message history, recent history context, conversation deletion and owner isolation.
- [x] Transparent knowledge-only response mode if no provider key is configured.
- [x] Provider-failure fallback to local retrieved excerpts without claiming that an AI response was produced.
- [x] Source cards and a visible disclaimer in the frontend.
- [x] Original similar-question generation when an AI provider is configured.
- [x] Without AI configuration, similar-question endpoint returns related existing GATEPath practice items without revealing answer keys or claiming newly generated content.
- [x] Tutor screen integrated into existing workspace navigation, paper profile and global search.
- [x] Responsive conversation history, chat view, topic focus, image preview and composer.

## API endpoints

- `GET /api/tutor/status` — model/provider readiness, indexed notes and paper-specific source status.
- `GET /api/tutor/conversations` — list the authenticated student's conversations.
- `GET /api/tutor/conversations/{conversation_id}` — retrieve one owned conversation and source references.
- `DELETE /api/tutor/conversations/{conversation_id}` — delete an owned conversation and its messages.
- `POST /api/tutor/chat` — ask a question with optional paper topic focus, explanation level and image.
- `POST /api/tutor/similar-questions` — generate original practice items with AI, or return matching existing practice items in local mode.

## AI provider configuration

Set these values in the server `.env` file and restart FastAPI:

```dotenv
OPENAI_API_KEY=your-server-side-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

The provider must support the Chat Completions API. Image analysis additionally requires a vision-capable model. The key is not returned by any endpoint or sent to frontend code.

## Retrieval and content boundaries

- The CS pilot retrieves from `backend/app/data/materials/CS-GATE-2027.json` (52 GATEPath original editorial learning notes).
- Retrieved notes are labelled as GATEPath editorial content mapped to the official GATE 2027 syllabus. The official syllabus PDF is linked as topic-scope reference; it is not described as the author of GATEPath explanations.
- The lexical retriever ranks title, section and note-content matches and can force a selected topic to the top. This is a local retrieval-augmented generation context step; it does not require a hosted vector database.
- Other papers without an imported topic library remain in official-source-only mode. The tutor does not fabricate topic notes for them.
- The AI prompt treats uploaded image text and retrieved passages as untrusted content, prohibits fabricated official questions/keys/ranks, and asks the tutor to state when the evidence is insufficient.
- AI-generated explanations and questions may be wrong and are visibly labelled; generated questions are not PYQs.

## Privacy and safety

- Conversation records are scoped by `user_id` in all database queries.
- Images are validated and passed only to the configured provider for analysis; only an `image_attached` boolean is retained.
- Provider credentials remain server-side.
- Students are told that provider data-retention terms apply to images sent to the configured external provider.

## Validation

- Test suite includes authentication, RAG ranking, CS note context, non-imported paper behaviour, history persistence, owner isolation, conversation deletion, image validation/no-storage, vision handoff, provider failure fallback and similar-question generation/fallback.
- Python compilation and frontend JavaScript syntax checks pass.
- The API version is `0.8.0`.
- Visual browser automation remains unverified in this execution environment because Chromium blocks local navigation.

Final integrated validation after the version bump: 112 backend tests pass, Python compilation passes, all frontend JavaScript syntax checks pass, the local SQLite migration is applied, and API health/static tutor assets/authentication guard return expected responses. The external AI provider was not live-called because no production API key was supplied; provider request construction and vision payload substitution are tested with a mocked HTTP client.
