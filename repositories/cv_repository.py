"""
CVCraft CV Repository
Data access object for CV documents and version management.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from database.db import db
from models.cv_model import CVDocument

class CVRepository:
    def __init__(self, database=db):
        self.db = database

    def save(self, cv: CVDocument, completion_pct: int = 0) -> None:
        cv.updated_at = datetime.now().isoformat()
        data_json = json.dumps(cv.to_dict())
        with self.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO cv_documents (
                    id, name, job_target, template_id, accent_palette,
                    completion_pct, is_favorite, parent_version_id,
                    version_label, created_at, updated_at, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    job_target=excluded.job_target,
                    template_id=excluded.template_id,
                    accent_palette=excluded.accent_palette,
                    completion_pct=excluded.completion_pct,
                    is_favorite=excluded.is_favorite,
                    parent_version_id=excluded.parent_version_id,
                    version_label=excluded.version_label,
                    updated_at=excluded.updated_at,
                    data_json=excluded.data_json
            """, (
                cv.id, cv.name, cv.job_target, cv.template_id,
                cv.customization.accent_palette, completion_pct,
                1 if cv.is_favorite else 0, cv.parent_version_id,
                cv.version_label, cv.created_at, cv.updated_at, data_json
            ))

    def get_by_id(self, cv_id: str) -> Optional[CVDocument]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT data_json FROM cv_documents WHERE id = ?", (cv_id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row["data_json"])
                return CVDocument.from_dict(data)
        return None

    def list_all(self, search: str = "", sort_by: str = "updated_at", desc: bool = True) -> List[Dict[str, Any]]:
        query = """
            SELECT id, name, job_target, template_id, accent_palette,
                   completion_pct, is_favorite, parent_version_id,
                   version_label, created_at, updated_at
            FROM cv_documents
        """
        params = []
        if search.strip():
            query += " WHERE name LIKE ? OR job_target LIKE ?"
            term = f"%{search.strip()}%"
            params.extend([term, term])
        
        valid_sort_cols = {
            "updated_at": "updated_at",
            "name": "name",
            "completion_pct": "completion_pct",
            "created_at": "created_at"
        }
        col = valid_sort_cols.get(sort_by, "updated_at")
        direction = "DESC" if desc else "ASC"
        query += f" ORDER BY {col} {direction}"

        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete(self, cv_id: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM cv_documents WHERE id = ?", (cv_id,))
            return cursor.rowcount > 0

    def duplicate(self, cv_id: str, as_version: bool = False, version_label: str = "") -> Optional[CVDocument]:
        original = self.get_by_id(cv_id)
        if not original:
            return None
        
        new_id = str(uuid.uuid4())
        data = original.to_dict()
        data["id"] = new_id
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()

        if as_version:
            data["parent_version_id"] = cv_id
            data["version_label"] = version_label or f"Version {datetime.now().strftime('%b %d')}"
            data["name"] = f"{original.name} ({data['version_label']})"
        else:
            data["parent_version_id"] = None
            data["version_label"] = "Main"
            data["name"] = f"{original.name} (Copy)"

        new_cv = CVDocument.from_dict(data)
        self.save(new_cv, completion_pct=80)
        return new_cv

    def get_stats(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM cv_documents").fetchone()["cnt"]
            completed = conn.execute("SELECT COUNT(*) as cnt FROM cv_documents WHERE completion_pct >= 85").fetchone()["cnt"]
            drafts = total - completed
            last_export_row = conn.execute("SELECT cv_name, exported_at FROM export_history ORDER BY exported_at DESC LIMIT 1").fetchone()
            last_export = dict(last_export_row) if last_export_row else None
            
            return {
                "total_cvs": total,
                "completed_cvs": completed,
                "draft_cvs": drafts,
                "last_export": last_export
            }

    def record_export(self, cv_id: str, cv_name: str, file_path: str):
        with self.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO export_history (id, cv_id, cv_name, file_path, exported_at)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), cv_id, cv_name, file_path, datetime.now().isoformat()))
