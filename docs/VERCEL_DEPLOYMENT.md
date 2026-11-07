# Vercel deployment notes

The FastAPI entrypoint is the repository-root `index.py`, also declared in
`pyproject.toml`. The function serves GATEPath's API and page routes; Vercel
uses `vercel.json` for its function duration.

## Preview only

For an initial Vercel preview, configure these variables in the **Preview**
environment:

- `APP_ENV=preview`
- `GATEPATH_DATABASE_PATH=/tmp/gatepath.db`
- `GATEPATH_SECURE_COOKIES=true`
- `APP_BASE_URL` to the preview's HTTPS origin

This `/tmp` SQLite file is ephemeral and instance-local. Accounts, sessions,
practice attempts, plans, bookmarks, and other user records may disappear
when a function instance is recycled and may not be visible to another
instance. It is only suitable for a deployment smoke test, not real users.

## Production database requirement

The application currently uses SQLite (`backend/app/database.py`). The
provided `render.yaml` and Dockerfile configure a persistent disk for that
SQLite database on Render. That disk is not available to Vercel Functions.
The database module deliberately fails fast on Vercel unless `APP_ENV=preview`
and the deployment is not the production target. A production deployment cannot
start with the SQLite adapter, even if `APP_ENV` is accidentally omitted.

Before enabling a Vercel production deployment, migrate the database adapter
and schema to a managed durable database (for example, PostgreSQL or a
SQLite-compatible remote database), configure its production credentials in
Vercel Environment Variables, run migrations, and verify `/api/health` and
`/api/ready`. Never commit `.env`, credentials, or database files to Git.
