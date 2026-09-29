"""
CVCraft Database Layer
Local SQLite persistence with transaction support, auto-migrations, and schema integrity.
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from config import DB_PATH

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cv_documents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    job_target TEXT DEFAULT '',
    template_id TEXT DEFAULT 'modern',
    accent_palette TEXT DEFAULT 'Deep Indigo',
    completion_pct INTEGER DEFAULT 0,
    is_favorite INTEGER DEFAULT 0,
    parent_version_id TEXT,
    version_label TEXT DEFAULT 'Main',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    data_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cv_updated_at ON cv_documents(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_cv_parent_version ON cv_documents(parent_version_id);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS export_history (
    id TEXT PRIMARY KEY,
    cv_id TEXT NOT NULL,
    cv_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    exported_at TEXT NOT NULL
);
"""

DEFAULT_SETTINGS = {
    "theme": "dark",
    "default_template": "modern",
    "default_palette": "Deep Indigo",
    "default_font": "Helvetica",
    "auto_save": "true",
    "auto_save_interval_sec": "5",
    "ai_enabled": "false",
    "ai_provider": "gemini",
    "ai_api_key": "",
    "onboarding_completed": "false"
}

class Database:
    _instance = None

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    @classmethod
    def get_instance(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            
            # Seed default settings if empty
            for k, v in DEFAULT_SETTINGS.items():
                conn.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (k, v)
                )

db = Database.get_instance()
