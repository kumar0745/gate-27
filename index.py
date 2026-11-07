"""Vercel ASGI entrypoint for the GATEPath FastAPI application."""

from backend.app.main import app

__all__ = ["app"]
