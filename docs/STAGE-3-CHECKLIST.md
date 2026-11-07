# Stage 3 — Authentication and Student Profiles

**Status:** Implemented in the shared GATEPath project.

## Student-facing capabilities

- [x] Registration with full name, unique email, password, GATE paper, target and daily hours.
- [x] Login and logout.
- [x] HTTP-only server-managed session cookie.
- [x] Signed-in account identity in the workspace header and sidebar.
- [x] Protected `/app` and `/workspace` routes.
- [x] Unauthenticated student API requests return `401`.
- [x] Student can update paper and daily preparation preferences.
- [x] Student tasks are isolated by account.
- [x] Student role is assigned by the server; clients cannot choose their role.
- [x] Administrator-only overview route returns `403` for student accounts.

## Security and account recovery

- [x] PBKDF2-HMAC-SHA256 password hashing with a unique random salt.
- [x] Opaque random session tokens; only SHA-256 token hashes are stored.
- [x] 30-day session expiry and server-side logout revocation.
- [x] `HttpOnly`, `SameSite=Strict` cookie; `Secure` on HTTPS.
- [x] Same-origin check on browser write requests.
- [x] Login throttling after five failed attempts in a 15-minute window.
- [x] Password reset token hashes, expiry and one-time use.
- [x] Password reset email delivery through environment-configured SMTP.
- [x] Explicit UI/API message when SMTP is not configured.
- [x] Optional administrator bootstrap through environment variables.

## Database changes

- [x] `users`
- [x] `user_profiles`
- [x] `user_sessions`
- [x] `user_tasks`
- [x] `password_reset_tokens`
- [x] `auth_login_attempts`
- [x] Additive migration; original local demo tables are retained.

## Routes

- [x] `/login`
- [x] `/register`
- [x] `/forgot-password`
- [x] `/reset-password`
- [x] `/api/auth/register`
- [x] `/api/auth/login`
- [x] `/api/auth/logout`
- [x] `/api/auth/me`
- [x] `/api/auth/request-password-reset`
- [x] `/api/auth/reset-password`
- [x] Authenticated profile, dashboard and task APIs

## Automated verification

- [x] Python compilation
- [x] Frontend JavaScript syntax checks
- [x] API health and public catalogue
- [x] Registration, login, logout and session verification
- [x] Duplicate account and weak password rejection
- [x] Private API authentication checks
- [x] Student profile and task CRUD
- [x] Cross-account task and profile isolation
- [x] Student/admin role separation
- [x] Login attempt throttling
- [x] SMTP-not-configured recovery response
- [x] Public landing, auth pages and static assets

## Known configuration requirement

Password recovery requires SMTP credentials. The reset UI is present, but email sending remains disabled until `SMTP_HOST` and `SMTP_FROM` (and, where needed, SMTP credentials) are configured in `.env`. The repository does not include real email credentials.

## Remaining product work

The administrator summary endpoint is a role gate for the future admin application, not the full Stage 12 content management dashboard. Email verification, production deployment, external security review, database backup policy and monitoring remain part of later hardening/deployment work.
