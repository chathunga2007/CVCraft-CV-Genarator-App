"""
CVCraft Settings Repository
Persistent application configuration and user preferences.
"""

from typing import Dict, Any, Optional
from database.db import db

class SettingsRepository:
    def __init__(self, database=db):
        self.db = database

    def get(self, key: str, default: str = "") -> str:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str):
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, str(value))
            )

    def get_all(self) -> Dict[str, str]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT key, value FROM settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}
