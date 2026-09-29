"""
CVCraft Import & Export Service
Lossless JSON export (*.cvcv), portable backup and restore, and migration tools.
"""

import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from models.cv_model import CVDocument
from config import DB_PATH, PHOTOS_DIR, BACKUPS_DIR, APP_VERSION

CVCV_SIGNATURE = "CVCRAFT_DOCUMENT_V1"

class ImportExportService:
    @staticmethod
    def export_cvcv_file(cv: CVDocument, destination_path: str) -> str:
        payload = {
            "signature": CVCV_SIGNATURE,
            "version": APP_VERSION,
            "exported_at": datetime.now().isoformat(),
            "cv_data": cv.to_dict()
        }
        with open(destination_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return destination_path

    @staticmethod
    def import_cvcv_file(source_path: str) -> Optional[CVDocument]:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if data.get("signature") != CVCV_SIGNATURE:
            # Try raw dict if user exported plain JSON
            if "name" in data and "personal" in data:
                return CVDocument.from_dict(data)
            raise ValueError("Invalid CVCraft document format (*.cvcv).")

        cv_data = data.get("cv_data", {})
        return CVDocument.from_dict(cv_data)

    @staticmethod
    def create_full_backup(backup_name: Optional[str] = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = backup_name or f"cvcraft_backup_{timestamp}.zip"
        backup_file = BACKUPS_DIR / name

        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if DB_PATH.exists():
                zipf.write(DB_PATH, arcname="cvcraft.db")
            if PHOTOS_DIR.exists():
                for root, _, files in os.walk(PHOTOS_DIR):
                    for file in files:
                        p = Path(root) / file
                        arcname = p.relative_to(PHOTOS_DIR.parent)
                        zipf.write(p, arcname=str(arcname))
        return str(backup_file)

    @staticmethod
    def restore_full_backup(backup_zip_path: str) -> bool:
        if not Path(backup_zip_path).exists():
            return False
        
        with zipfile.ZipFile(backup_zip_path, 'r') as zipf:
            for member in zipf.namelist():
                if member == "cvcraft.db":
                    zipf.extract(member, path=DB_PATH.parent)
                elif member.startswith("photos/"):
                    zipf.extract(member, path=PHOTOS_DIR.parent)
        return True
