from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")
_default_db = "backend/data/gatepath.db"
_configured_db = os.getenv("GATEPATH_DATABASE_PATH", _default_db).strip() or _default_db
_db_candidate = Path(_configured_db)
DB_PATH = (_db_candidate if _db_candidate.is_absolute() else PROJECT_ROOT / _db_candidate).resolve()

# A local SQLite file is acceptable for development and for the persistent
# Render disk defined in render.yaml, but not for Vercel production Functions.
# Vercel's writable temp directory is ephemeral and is not shared between
# instances, so fail fast instead of silently losing student records.
if os.getenv("VERCEL") == "1":
    app_env = os.getenv("APP_ENV", "").strip().lower()
    vercel_env = os.getenv("VERCEL_ENV", "").strip().lower()
    if app_env != "preview" or vercel_env == "production":
        raise RuntimeError(
            "GATEPath's SQLite adapter is not supported on Vercel production. "
            "Use APP_ENV=preview only for a temporary smoke test with "
            "GATEPATH_DATABASE_PATH=/tmp/gatepath.db. Production requires "
            "a migrated durable remote database; the Render persistent disk "
            "configured in render.yaml is another supported hosting path."
        )
    _configured_db = os.getenv("GATEPATH_DATABASE_PATH", "/tmp/gatepath.db").strip() or "/tmp/gatepath.db"
    _db_candidate = Path(_configured_db)
    DB_PATH = (_db_candidate if _db_candidate.is_absolute() else PROJECT_ROOT / _db_candidate).resolve()

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db() -> Iterator[sqlite3.Connection]:
    with get_connection() as conn:
        yield conn


def init_db() -> None:
    """Create the original demo tables and the Stage 3 account-owned tables.

    This is intentionally additive so existing local Stage 1/2 databases are
    upgraded without deleting the sample workspace data.
    """
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS student_preferences (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                paper_code TEXT NOT NULL DEFAULT 'CS',
                target TEXT NOT NULL DEFAULT 'IIT admission',
                daily_hours INTEGER NOT NULL DEFAULT 5,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS study_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                due_date TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 30,
                priority TEXT NOT NULL DEFAULT 'Normal',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            INSERT OR IGNORE INTO student_preferences (id, paper_code, target, daily_hours)
            VALUES (1, 'CS', 'IIT admission', 5);

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL DEFAULT 'CS',
                target TEXT NOT NULL DEFAULT 'IIT admission',
                daily_hours INTEGER NOT NULL DEFAULT 5,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at REAL NOT NULL,
                used_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS auth_login_attempts (
                email TEXT NOT NULL COLLATE NOCASE,
                ip_address TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                window_started REAL NOT NULL,
                locked_until REAL NOT NULL DEFAULT 0,
                PRIMARY KEY (email, ip_address)
            );

            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                due_date TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 30,
                priority TEXT NOT NULL DEFAULT 'Normal',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_user_tasks_user_date ON user_tasks(user_id, due_date, completed);

            CREATE TABLE IF NOT EXISTS student_material_progress (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'not_started'
                    CHECK (status IN ('not_started', 'in_progress', 'completed')),
                bookmarked INTEGER NOT NULL DEFAULT 0 CHECK (bookmarked IN (0, 1)),
                personal_note TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, paper_code, topic_id)
            );
            CREATE INDEX IF NOT EXISTS idx_material_progress_user_paper
                ON student_material_progress(user_id, paper_code, status);
            CREATE INDEX IF NOT EXISTS idx_material_bookmarks_user
                ON student_material_progress(user_id, bookmarked);

            CREATE TABLE IF NOT EXISTS pyq_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_id TEXT NOT NULL,
                submitted_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
                awarded_marks REAL NOT NULL,
                spent_seconds INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_pyq_attempts_user_time
                ON pyq_attempts(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_pyq_attempts_user_question
                ON pyq_attempts(user_id, question_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS pyq_bookmarks (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, question_id)
            );
            CREATE INDEX IF NOT EXISTS idx_pyq_bookmarks_user
                ON pyq_bookmarks(user_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS practice_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                mode TEXT NOT NULL CHECK (mode IN ('topic', 'custom', 'daily')),
                question_ids TEXT NOT NULL,
                question_count INTEGER NOT NULL,
                duration_seconds INTEGER NOT NULL,
                started_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired')),
                submitted_at TEXT,
                correct_count INTEGER NOT NULL DEFAULT 0,
                awarded_marks REAL NOT NULL DEFAULT 0,
                maximum_marks REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_practice_sessions_user_time
                ON practice_sessions(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_practice_sessions_user_status
                ON practice_sessions(user_id, status, expires_at);

            CREATE TABLE IF NOT EXISTS practice_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES practice_sessions(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_id TEXT NOT NULL,
                submitted_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
                awarded_marks REAL NOT NULL,
                spent_seconds INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, question_id)
            );
            CREATE INDEX IF NOT EXISTS idx_practice_attempts_user_time
                ON practice_attempts(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_practice_attempts_user_question
                ON practice_attempts(user_id, question_id, created_at DESC);

            -- Stage 9: full-length computer-based mock examinations.
            CREATE TABLE IF NOT EXISTS mock_test_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                test_id TEXT NOT NULL,
                paper_code TEXT NOT NULL,
                question_ids TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                started_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'submitted', 'expired')),
                selected_sections TEXT NOT NULL DEFAULT '{}',
                submitted_at TEXT,
                score REAL NOT NULL DEFAULT 0,
                maximum_marks REAL NOT NULL DEFAULT 0,
                attempted_count INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                wrong_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_mock_sessions_user_time
                ON mock_test_sessions(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_mock_sessions_user_status
                ON mock_test_sessions(user_id, status, expires_at);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_mock_one_active_session_per_user
                ON mock_test_sessions(user_id) WHERE status = 'active';

            CREATE TABLE IF NOT EXISTS mock_test_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES mock_test_sessions(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_id TEXT NOT NULL,
                answer TEXT NOT NULL DEFAULT '',
                marked_for_review INTEGER NOT NULL DEFAULT 0 CHECK (marked_for_review IN (0, 1)),
                visited INTEGER NOT NULL DEFAULT 0 CHECK (visited IN (0, 1)),
                spent_seconds INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, question_id)
            );
            CREATE INDEX IF NOT EXISTS idx_mock_responses_user_session
                ON mock_test_responses(user_id, session_id);

            -- Stage 10: personalised plans, scheduled learning blocks and spaced revision.
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                title TEXT NOT NULL,
                plan_days INTEGER NOT NULL CHECK (plan_days IN (30, 60, 90)),
                daily_hours INTEGER NOT NULL CHECK (daily_hours BETWEEN 1 AND 16),
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
                planned_topic_count INTEGER NOT NULL DEFAULT 0,
                unplanned_topic_count INTEGER NOT NULL DEFAULT 0,
                config_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_study_plans_user_paper_status
                ON study_plans(user_id, paper_code, status, created_at DESC);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_study_plans_one_active_per_paper
                ON study_plans(user_id, paper_code) WHERE status = 'active';

            CREATE TABLE IF NOT EXISTS planner_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                task_type TEXT NOT NULL CHECK (task_type IN ('learn', 'practice', 'revision', 'mock', 'custom', 'review')),
                topic_id TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                duration_minutes INTEGER NOT NULL DEFAULT 25 CHECK (duration_minutes BETWEEN 5 AND 600),
                priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high')),
                status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'skipped')),
                source TEXT NOT NULL DEFAULT 'generated' CHECK (source IN ('generated', 'manual', 'revision')),
                metadata_json TEXT NOT NULL DEFAULT '{}',
                completed_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_planner_tasks_user_date
                ON planner_tasks(user_id, paper_code, scheduled_date, status);
            CREATE INDEX IF NOT EXISTS idx_planner_tasks_plan_status
                ON planner_tasks(plan_id, status, scheduled_date);

            CREATE TABLE IF NOT EXISTS planner_revision_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                interval_days INTEGER NOT NULL DEFAULT 1,
                review_count INTEGER NOT NULL DEFAULT 0,
                ease_factor REAL NOT NULL DEFAULT 2.5,
                last_reviewed_at TEXT,
                status TEXT NOT NULL DEFAULT 'due' CHECK (status IN ('due', 'snoozed', 'mastered')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, paper_code, topic_id)
            );
            CREATE INDEX IF NOT EXISTS idx_revision_queue_user_due
                ON planner_revision_queue(user_id, paper_code, status, due_date);

            -- Stage 11: private AI tutor conversations and grounded source references.
            CREATE TABLE IF NOT EXISTS tutor_conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'New tutor conversation',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tutor_conversations_user_updated
                ON tutor_conversations(user_id, updated_at DESC);

            CREATE TABLE IF NOT EXISTS tutor_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES tutor_conversations(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                source_refs_json TEXT NOT NULL DEFAULT '[]',
                image_attached INTEGER NOT NULL DEFAULT 0 CHECK (image_attached IN (0, 1)),
                provider TEXT NOT NULL DEFAULT 'knowledge',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tutor_messages_conversation
                ON tutor_messages(conversation_id, id);
            CREATE INDEX IF NOT EXISTS idx_tutor_messages_user
                ON tutor_messages(user_id, created_at DESC);

            -- Stage 12: community discussions, reactions, reports and admin content review.
            CREATE TABLE IF NOT EXISTS community_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                paper_code TEXT NOT NULL,
                category TEXT NOT NULL CHECK (category IN ('Doubt', 'Study tips', 'Resources', 'Exam strategy', 'General')),
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'published' CHECK (status IN ('published', 'hidden', 'removed')),
                pinned INTEGER NOT NULL DEFAULT 0 CHECK (pinned IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_community_posts_paper_status
                ON community_posts(paper_code, status, pinned DESC, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_community_posts_user
                ON community_posts(user_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS community_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'published' CHECK (status IN ('published', 'hidden', 'removed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_community_replies_post
                ON community_replies(post_id, status, created_at);

            CREATE TABLE IF NOT EXISTS community_post_likes (
                post_id INTEGER NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(post_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS community_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                target_type TEXT NOT NULL CHECK (target_type IN ('post', 'reply')),
                target_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'dismissed')),
                resolution_note TEXT NOT NULL DEFAULT '',
                reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                reviewed_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_community_reports_status
                ON community_reports(status, created_at DESC);

            CREATE TABLE IF NOT EXISTS admin_content_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_code TEXT NOT NULL,
                content_type TEXT NOT NULL CHECK (content_type IN ('material', 'practice_question', 'pyq_answer')),
                content_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending_review' CHECK (status IN ('pending_review', 'approved', 'needs_changes', 'rejected')),
                note TEXT NOT NULL DEFAULT '',
                reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                reviewed_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(paper_code, content_type, content_id)
            );
            CREATE INDEX IF NOT EXISTS idx_admin_content_reviews_status
                ON admin_content_reviews(paper_code, status, content_type);
            """
        )
        # Preserve the original anonymous sample tasks for backward-compatible
        # local development. Authenticated accounts receive their own empty list.
        row = conn.execute("SELECT COUNT(*) AS count FROM study_tasks").fetchone()
        if row["count"] == 0:
            conn.executemany(
                """INSERT INTO study_tasks
                   (title, subject, due_date, duration_minutes, priority, completed)
                   VALUES (?, ?, date('now', 'localtime'), ?, ?, 0)""",
                [
                    ("Review the GATE 2027 paper pattern", "Exam strategy", 25, "High"),
                    ("Choose the first topic for focused study", "Planning", 15, "Normal"),
                    ("Create a baseline practice target", "Practice", 30, "Normal"),
                ],
            )
