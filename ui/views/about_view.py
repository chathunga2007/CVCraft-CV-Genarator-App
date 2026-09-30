"""
CVCraft About & Product Showcase View
Comprehensive product identity, architectural pillars, diagnostic information,
and quick system actions.
"""

import sys
import os
import sqlite3
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from config import (
    LOGO_PATH, APP_NAME, APP_TAGLINE, APP_VERSION, APP_DEVELOPER,
    APP_LICENSE, USER_DATA_DIR, DB_PATH
)
from services.import_export import ImportExportService

class AboutView(QWidget):
    load_demo_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Scroll Area for clean presentation on any window size
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(24)

        # 1. Hero Brand Card
        hero_card = QFrame()
        hero_card.setProperty("class", "Card")
        hero_card.setStyleSheet("""
            QFrame.Card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E1B4B, stop:0.6 #0F172A, stop:1 #1E293B);
                border: 1.5px solid #4338CA;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        h_layout = QHBoxLayout(hero_card)
        h_layout.setSpacing(24)

        # Logo
        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(
                84, 84,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            h_layout.addWidget(logo_lbl)

        # Brand Text
        brand_box = QVBoxLayout()
        brand_box.setSpacing(6)

        t_lbl = QLabel(APP_NAME)
        t_lbl.setStyleSheet("font-size: 28px; font-weight: 900; color: #FFFFFF; letter-spacing: -0.5px;")

        tag_lbl = QLabel(f"“{APP_TAGLINE}”")
        tag_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #818CF8; font-style: italic;")

        desc_lbl = QLabel(
            "CVCraft is an offline-first professional desktop workstation engineered for ambitious individuals "
            "to craft, fine-tune, ATS-optimize, and export presentation-grade career documents."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 13px; color: #CBD5E1; line-height: 1.4;")

        # Badges row
        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)
        for badge_text in [f"Version {APP_VERSION}", "100% Offline-First", "Commercial Grade", "ReportLab Vector Engine"]:
            b = QLabel(badge_text)
            b.setStyleSheet("""
                background-color: rgba(99, 102, 241, 0.2);
                color: #C7D2FE;
                font-size: 10px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 6px;
                border: 1px solid rgba(99, 102, 241, 0.3);
            """)
            badges_row.addWidget(b)
        badges_row.addStretch()

        brand_box.addWidget(t_lbl)
        brand_box.addWidget(tag_lbl)
        brand_box.addWidget(desc_lbl)
        brand_box.addSpacing(4)
        brand_box.addLayout(badges_row)
        h_layout.addLayout(brand_box)
        c_layout.addWidget(hero_card)

        # 2. Key Product Pillars (Grid)
        sec_title = QLabel("Architectural Pillars & Capabilities")
        sec_title.setProperty("class", "SectionHeader")
        c_layout.addWidget(sec_title)

        pillars_grid = QGridLayout()
        pillars_grid.setSpacing(16)

        pillars = [
            ("📄 Vector PDF Engine", "Produces standard A4 documents with pixel-perfect margins, clean font embeddings, and guaranteed vector sharpness for both digital submission and physical printing.", "#4F46E5"),
            ("🎯 ATS-Friendly Layouts", "Includes certified single-column linear templates without confusing tables or graphical blocks, ensuring 99%+ parsing accuracy across corporate applicant tracking systems.", "#10B981"),
            ("⚡ 8 Tailored Templates", "Carefully architectural designs from Modern Tech, Software Engineer, and Minimalist to Executive Leadership and Academic Research formats.", "#8B5CF6"),
            ("🔒 Zero-Cloud Privacy", "All your data, career experiences, and profile photos live exclusively on your local computer in a robust SQLite database. Zero remote telemetry.", "#0EA5E9")
        ]

        for idx, (p_title, p_desc, color) in enumerate(pillars):
            card = QFrame()
            card.setProperty("class", "Card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(8)

            tl = QLabel(p_title)
            tl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {color};")
            dl = QLabel(p_desc)
            dl.setWordWrap(True)
            dl.setProperty("class", "MutedText")

            cl.addWidget(tl)
            cl.addWidget(dl)
            pillars_grid.addWidget(card, idx // 2, idx % 2)

        c_layout.addLayout(pillars_grid)

        # 3. System Diagnostics & Local Environment Card
        diag_title = QLabel("Environment & Diagnostic Information")
        diag_title.setProperty("class", "SectionHeader")
        c_layout.addWidget(diag_title)

        diag_card = QFrame()
        diag_card.setProperty("class", "Card")
        dc_layout = QVBoxLayout(diag_card)
        dc_layout.setContentsMargins(20, 16, 20, 16)
        dc_layout.setSpacing(10)

        def add_info(label: str, value: str):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setProperty("class", "FieldLabel")
            v = QLabel(value)
            v.setStyleSheet("font-weight: 600; font-family: Consolas, monospace; font-size: 12px;")
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            dc_layout.addLayout(row)

        add_info("Python Runtime:", f"Python {sys.version.split()[0]} ({sys.platform})")
        add_info("GUI Toolkit:", "PyQt6 & Qt 6.11 Architecture")
        add_info("Local Database Path:", str(DB_PATH))
        add_info("Storage Directory:", str(USER_DATA_DIR))
        add_info("Licensing Model:", f"{APP_LICENSE} — Offline Distribution")
        add_info("Developer:", APP_DEVELOPER)

        dc_layout.addSpacing(10)

        # Quick Actions Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        open_folder_btn = QPushButton("📂 Open Local Data Folder")
        open_folder_btn.setProperty("class", "SecondaryBtn")
        open_folder_btn.clicked.connect(self._open_data_folder)
        actions_row.addWidget(open_folder_btn)

        backup_btn = QPushButton("💾 Create Instant Backup (.zip)")
        backup_btn.setProperty("class", "SecondaryBtn")
        backup_btn.clicked.connect(self._create_instant_backup)
        actions_row.addWidget(backup_btn)

        actions_row.addStretch()
        dc_layout.addLayout(actions_row)
        c_layout.addWidget(diag_card)

        # 4. Release Changelog
        log_title = QLabel("What's New in v1.0.0")
        log_title.setProperty("class", "SectionHeader")
        c_layout.addWidget(log_title)

        log_card = QFrame()
        log_card.setProperty("class", "Card")
        lc_layout = QVBoxLayout(log_card)
        lc_layout.setContentsMargins(20, 16, 20, 16)
        lc_layout.setSpacing(8)

        changes = [
            "✨ 8 Production Architectural Templates with distinct layouts, headers, and section hierarchies.",
            "🚀 High-DPI Real-time Live Preview with sub-millisecond debounced compilation and multi-page pagination.",
            "🎯 'Tailor My CV' ATS Match Engine with keyword analysis, formatting checks, and one-click integration.",
            "💡 Offline-First AI Assistant with STAR-method bullet points and executive summary polishing.",
            "🌓 Dynamic Theme Engine supporting both Deep Indigo Dark Mode and Clean Light Mode.",
            "🔄 Document Version Control allowing multiple specialized versions per profile.",
            "📦 Lossless Import & Export (.cvcv) and portable zip backup/restore."
        ]

        for ch in changes:
            lbl = QLabel(f"• {ch}")
            lbl.setProperty("class", "MutedText")
            lbl.setWordWrap(True)
            lc_layout.addWidget(lbl)

        c_layout.addWidget(log_card)

        c_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _open_data_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(str(USER_DATA_DIR))
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(USER_DATA_DIR)])
        except Exception as e:
            QMessageBox.information(self, "Data Directory", f"Your data directory is located at:\n{USER_DATA_DIR}")

    def _create_instant_backup(self):
        try:
            backup_file = ImportExportService.create_full_backup()
            QMessageBox.information(
                self, "Backup Successful",
                f"Full portable backup archive successfully generated:\n{backup_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Could not generate backup: {str(e)}")
