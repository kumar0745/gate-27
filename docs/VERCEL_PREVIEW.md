# GATEPath Vercel preview

This branch is a smoke-test deployment only.

- The FastAPI entrypoint is `index.py`.
- Runtime dependencies are declared in `pyproject.toml`.
- Preview deployments use `APP_ENV=preview` and `GATEPATH_DATABASE_PATH=/tmp/gatepath.db`.
- The SQLite file is ephemeral and instance-local. Do not use this preview for real student accounts or persistent study progress.
- Production remains guarded until the SQLite adapter and schema have been migrated to a durable managed database and the production database connection is configured.

The main branch remains the canonical source branch.
