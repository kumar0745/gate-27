#!/usr/bin/env python3
"""Static integration checks for the GATEPath 2027 project."""
from __future__ import annotations

import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.routing import APIRoute  # noqa: E402
from app.main import app, mock_manifest_is_valid  # noqa: E402


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        for key in ("src", "href"):
            value = attributes.get(key, "")
            if value.startswith("/static/"):
                self.assets.append(value.removeprefix("/static/"))


def check_json_and_content() -> list[str]:
    issues: list[str] = []
    data_root = BACKEND / "app" / "data"
    for path in sorted(data_root.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"Invalid JSON: {path.relative_to(ROOT)} ({exc})")

    def read(path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        papers = read(data_root / "papers.json")
        codes = [paper["code"] for paper in papers]
        if codes != ["CS"]:
            issues.append("CS-only release must contain exactly the CS paper")

        syllabus = read(data_root / "syllabi" / "CS-GATE-2027.json")
        materials = read(data_root / "materials" / "CS-GATE-2027.json")
        topic_ids = {topic["id"] for section in syllabus["sections"] for topic in section["topics"]}
        material_ids = {item["id"] for item in materials["materials"]}
        if topic_ids != material_ids:
            issues.append("CS syllabus topic IDs and study-material IDs do not match")

        practice = read(data_root / "practice" / "CS-GATE-2027.json")
        practice_ids = [item["id"] for item in practice["questions"]]
        if len(practice_ids) != len(set(practice_ids)):
            issues.append("Practice question IDs are not unique")
        if not {item["topic_id"] for item in practice["questions"]} <= topic_ids:
            issues.append("Practice question references an unknown CS topic")

        mock = read(data_root / "mocks" / "CS-FULL-MOCK-01.json")
        valid, reason = mock_manifest_is_valid(mock)
        if not valid:
            issues.append(f"CS mock manifest failed validation: {reason}")
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        issues.append(f"Core content integrity check failed: {exc}")
    return issues


def check_api_routes() -> list[str]:
    counts: Counter[tuple[str, str]] = Counter()
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods or set():
                if method not in {"HEAD", "OPTIONS"}:
                    counts[(method, route.path)] += 1
    return [f"Duplicate API route: {method} {path} ({count} registrations)"
            for (method, path), count in counts.items() if count > 1]


def check_frontend_assets() -> list[str]:
    issues: list[str] = []
    for page in ("index.html",):
        path = ROOT / "frontend" / page
        if not path.is_file():
            issues.append(f"Missing frontend page: {page}")
            continue
        parser = AssetParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for asset in parser.assets:
            if not (ROOT / "frontend" / asset).is_file():
                issues.append(f"{page} references missing asset: {asset}")
    for required in (
        "requirements.txt", "requirements-dev.txt", "scripts/start.sh", "scripts/start.ps1",
        "scripts/docker-entrypoint.sh", "scripts/backup_db.py", ".env.example", ".gitignore", "Dockerfile",
        ".dockerignore", "render.yaml", "docs/STAGE-14-DEPLOYMENT.md", "docs/STAGE-14-CHECKLIST.md",
        "docs/CS-ONLY-TRACK.md",
    ):
        if not (ROOT / required).is_file():
            issues.append(f"Missing project setup file: {required}")
    return issues


def main() -> int:
    checks = [
        ("API route registry", check_api_routes()),
        ("Data and content integrity", check_json_and_content()),
        ("Frontend assets and setup files", check_frontend_assets()),
    ]
    failed = False
    for label, issues in checks:
        if issues:
            failed = True
            print(f"FAIL · {label}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS · {label}")
    if failed:
        return 1
    print("\nGATEPath static integration checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
