#!/usr/bin/env python3
"""Create a consistent SQLite backup using SQLite's online backup API."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from app.database import DB_PATH  # noqa: E402


def backup_database(destination: Path) -> Path:
    source_path = Path(DB_PATH)
    if not source_path.exists():
        raise FileNotFoundError(f"Database does not exist yet: {source_path}")
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(source_path)
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
        result = target.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"Backup integrity check failed: {result}")
    finally:
        target.close()
        source.close()
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination", nargs="?",
        help="Backup file path (default: backups/gatepath-<UTC timestamp>.db)",
    )
    args = parser.parse_args()
    if args.destination:
        destination = Path(args.destination)
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = ROOT / "backups" / f"gatepath-{stamp}.db"
    try:
        output = backup_database(destination)
    except (OSError, sqlite3.Error, RuntimeError) as exc:
        print(f"Backup failed: {exc}", file=sys.stderr)
        return 1
    print(f"Backup created and verified: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
