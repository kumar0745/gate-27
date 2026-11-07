# Stage 12 — Analytics, Community and Admin Dashboard

Status: implemented in the shared GATEPath project.

## Student analytics

- [x] Authenticated `GET /api/analytics` endpoint, scoped to the signed-in user and requested paper.
- [x] Syllabus progress summary from the student's material-progress records.
- [x] Practice/PYQ accuracy from each question's latest recorded attempt, alongside total attempt count.
- [x] Section and topic performance summaries where imported question metadata supports mapping.
- [x] Weak-topic list based only on recorded attempts; no invented rank prediction or estimated work.
- [x] Completed planner task totals and 14-day activity series.
- [x] Completed mock-test score history, best score and average score.
- [x] Student-facing analytics screen with activity bars, section performance, weak-topic ranking and mock history.

## Student community

- [x] Paper-specific, all-paper and own-post feed scopes.
- [x] Category and text search filters with pagination metadata.
- [x] Create discussion, view detail, reply and remove own posts/replies.
- [x] Like/unlike toggle backed by a unique per-user reaction key.
- [x] Report posts/replies and reject self-reporting.
- [x] Owner-only visibility of hidden content; published feed excludes hidden/removed content.
- [x] Frontend renders user-generated content as escaped plain text.
- [x] Community UI includes content rules and reporting actions.

## Administrator workspace

- [x] Existing `require_admin` role guard applied to every admin API.
- [x] Admin overview with account, community and editorial-review counts.
- [x] Student account search/list and activate/deactivate controls.
- [x] Deactivation revokes all active sessions for the affected student.
- [x] Protect administrator accounts from the student deactivation endpoint; prevent self-deactivation.
- [x] Report queue with dismiss, hide and remove actions.
- [x] Post pinning and moderation, plus reply moderation.
- [x] Cross-paper content coverage catalogue.
- [x] Editorial review queue for materials, original practice items and PYQ answer-key records.
- [x] Persist review status, reviewer and note in `admin_content_reviews`.
- [x] UI displays content review states and filters by paper/content type.

## New database tables

- `community_posts`
- `community_replies`
- `community_post_likes`
- `community_reports`
- `admin_content_reviews`

All migrations are additive; existing student, test, planner and tutor data is retained.

## Admin bootstrap

Set `GATEPATH_ADMIN_EMAIL` and `GATEPATH_ADMIN_PASSWORD` (at least the configured minimum password length) in the server's `.env` before first startup. The bootstrap creates the account only when that email does not already exist. It does not silently promote an existing student account or overwrite an existing administrator password.

## Editorial and data boundaries

- Analytics describe activity stored in GATEPath only. Offline study time is not inferred.
- Weak-topic and accuracy calculations use latest question attempts rather than counting repeated attempts as separate unique questions.
- Student discussion text is stored as plain text and escaped in the browser; moderation is required for public deployment.
- Admin approval records are workflow metadata, not independent proof of answer correctness, syllabus accuracy or content licensing.
- Content queue entries are only generated for locally imported resources. CS is the populated pilot; other paper content remains pending until verified imports exist.
- No direct editing of the version-controlled content JSON files is exposed through the web UI. Admins can review/status-tag content without mutating source files from the browser.

## Automated verification

`backend/tests/test_stage12.py` covers analytics calculations and account isolation, community CRUD/filtering/likes/reports, admin role enforcement, account status controls, report moderation and content review workflow.

## Final stage verification

- [x] `pytest -q` — 115 passed across the complete backend test suite.
- [x] `node --check frontend/app.js` — passed.
- [x] `python -m py_compile backend/app/main.py backend/app/database.py` — passed.
- [x] Verified required Stage 12 source, test and documentation files exist.
- [x] Confirmed no ZIP archive was created during Stage 12.
- [ ] Full interactive visual browser pass remains for the final Stage 13 QA pass.

Two existing FastAPI `on_event` lifecycle deprecation warnings remain and are tracked for Stage 13 cleanup.
