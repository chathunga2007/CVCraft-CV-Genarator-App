"""
CVCraft Settings View
Customization, appearance, storage, backup/restore, AI settings, and privacy guarantee.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QScrollArea, QFrame, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from repositories.settings_repository import SettingsRepository
from services.import_export import ImportExportService
from config import DB_PATH, EXPORTS_DIR, BACKUPS_DIR, TEMPLATES, COLOR_PALETTES, AVAILABLE_FONTS

class SettingsView(QWidget):
    theme_changed = pyqtSignal(str) # "dark" or "light"

    def __init__(self, settings_repo: SettingsRepository, parent=None):
        super().__init__(parent)
        self.settings = settings_repo
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hdr_box = QVBoxLayout()
        title = QLabel("Settings & Preferences")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        sub = QLabel("Configure appearance, document defaults, storage, AI integration, and privacy.")
        sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
        hdr_box.addWidget(title)
        hdr_box.addWidget(sub)
        layout.addLayout(hdr_box)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(24)

        # 1. Appearance Section
        c_layout.addWidget(self._create_section_header("Appearance & Theme"))
        app_card = self._create_card()
        ac_layout = QVBoxLayout(app_card)
        
        t_row = QHBoxLayout()
        t_lbl = QLabel("Application Theme:")
        t_lbl.setStyleSheet("font-size: 13px; color: #E2E8F0;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark Mode (Recommended)", "dark")
        self.theme_combo.addItem("Light Mode", "light")
        current_theme = self.settings.get("theme", "dark")
        self.theme_combo.setCurrentIndex(0 if current_theme == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        t_row.addWidget(t_lbl)
        t_row.addStretch()
        t_row.addWidget(self.theme_combo)
        ac_layout.addLayout(t_row)
        c_layout.addWidget(app_card)

        # 2. CV Document Defaults
        c_layout.addWidget(self._create_section_header("CV Document Defaults"))
        def_card = self._create_card()
        dc_layout = QVBoxLayout(def_card)
        dc_layout.setSpacing(12)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Default Template:"))
        self.def_tpl_combo = QComboBox()
        for t in TEMPLATES:
            self.def_tpl_combo.addItem(t["name"], t["id"])
        idx = self.def_tpl_combo.findData(self.settings.get("default_template", "modern"))
        if idx >= 0: self.def_tpl_combo.setCurrentIndex(idx)
        self.def_tpl_combo.currentIndexChanged.connect(lambda: self.settings.set("default_template", self.def_tpl_combo.currentData()))
        r1.addStretch()
        r1.addWidget(self.def_tpl_combo)
        dc_layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Default Color Palette:"))
        self.def_pal_combo = QComboBox()
        for p in COLOR_PALETTES.keys():
            self.def_pal_combo.addItem(p, p)
        idx_p = self.def_pal_combo.findData(self.settings.get("default_palette", "Deep Indigo"))
        if idx_p >= 0: self.def_pal_combo.setCurrentIndex(idx_p)
        self.def_pal_combo.currentIndexChanged.connect(lambda: self.settings.set("default_palette", self.def_pal_combo.currentData()))
        r2.addStretch()
        r2.addWidget(self.def_pal_combo)
        dc_layout.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Default Font Family:"))
        self.def_font_combo = QComboBox()
        for f in AVAILABLE_FONTS:
            self.def_font_combo.addItem(f, f)
        idx_f = self.def_font_combo.findData(self.settings.get("default_font", "Helvetica"))
        if idx_f >= 0: self.def_font_combo.setCurrentIndex(idx_f)
        self.def_font_combo.currentIndexChanged.connect(lambda: self.settings.set("default_font", self.def_font_combo.currentData()))
        r3.addStretch()
        r3.addWidget(self.def_font_combo)
        dc_layout.addLayout(r3)
        c_layout.addWidget(def_card)

        # 3. Storage & Backup
        c_layout.addWidget(self._create_section_header("Storage & System Backups"))
        stor_card = self._create_card()
        sc_layout = QVBoxLayout(stor_card)
        sc_layout.setSpacing(10)

        db_lbl = QLabel(f"<b>Local SQLite Database:</b> {DB_PATH}")
        db_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        sc_layout.addWidget(db_lbl)

        btn_row = QHBoxLayout()
        backup_btn = QPushButton("💾 Create Full System Backup (.zip)")
        backup_btn.setStyleSheet("background-color: #312E81; color: #C7D2FE; padding: 8px 14px; border-radius: 6px; font-weight: 600;")
        backup_btn.clicked.connect(self._create_backup)
        
        restore_btn = QPushButton("📂 Restore From Backup (.zip)")
        restore_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border: 1px solid #334155; padding: 8px 14px; border-radius: 6px;")
        restore_btn.clicked.connect(self._restore_backup)

        btn_row.addWidget(backup_btn)
        btn_row.addWidget(restore_btn)
        btn_row.addStretch()
        sc_layout.addLayout(btn_row)
        c_layout.addWidget(stor_card)

        # 4. AI Integration (Optional)
        c_layout.addWidget(self._create_section_header("AI Assistant Configuration"))
        ai_card = self._create_card()
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setSpacing(10)

        ai_desc = QLabel("CVCraft includes a powerful offline-first rule-based NLP assistant by default. You can optionally connect Google Gemini or Groq API for cloud AI.")
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("font-size: 12px; color: #94A3B8;")
        ai_layout.addWidget(ai_desc)

        ai_p_row = QHBoxLayout()
        ai_p_row.addWidget(QLabel("AI Provider:"))
        self.ai_prov_combo = QComboBox()
        self.ai_prov_combo.addItem("Built-in Offline Smart Engine (Default)", "offline")
        self.ai_prov_combo.addItem("Google Gemini API", "gemini")
        self.ai_prov_combo.addItem("Groq Cloud API", "groq")
        self.ai_prov_combo.currentIndexChanged.connect(lambda: self.settings.set("ai_provider", self.ai_prov_combo.currentData()))
        ai_p_row.addStretch()
        ai_p_row.addWidget(self.ai_prov_combo)
        ai_layout.addLayout(ai_p_row)

        ai_k_row = QHBoxLayout()
        ai_k_row.addWidget(QLabel("API Key (Optional):"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter optional API key for cloud provider...")
        self.api_key_input.setText(self.settings.get("ai_api_key", ""))
        self.api_key_input.textChanged.connect(lambda txt: self.settings.set("ai_api_key", txt))
        ai_k_row.addWidget(self.api_key_input)
        ai_layout.addLayout(ai_k_row)
        c_layout.addWidget(ai_card)

        # 5. Privacy & Security
        c_layout.addWidget(self._create_section_header("Privacy & Security Guarantee"))
        priv_card = self._create_card()
        priv_layout = QVBoxLayout(priv_card)
        priv_p = QLabel(
            "🔒 <b>100% Offline-First Architecture</b><br/><br/>"
            "CVCraft stores all your resumes, personal contact details, work history, and photos strictly on your local computer in a secure SQLite database. "
            "No telemetry, tracking, or document data is uploaded to any remote server without your explicit configuration."
        )
        priv_p.setWordWrap(True)
        priv_p.setStyleSheet("font-size: 12px; color: #CBD5E1; line-height: 1.5;")
        priv_layout.addWidget(priv_p)
        c_layout.addWidget(priv_card)

        c_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _create_section_header(self, title: str) -> QLabel:
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        return lbl

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 16px;")
        return card

    def _on_theme_changed(self):
        theme = self.theme_combo.currentData()
        self.settings.set("theme", theme)
        self.theme_changed.emit(theme)

    def _create_backup(self):
        try:
            path = ImportExportService.create_full_backup()
            QMessageBox.information(self, "Backup Created", f"Full system backup successfully saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Could not create backup: {str(e)}")

    def _restore_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup Zip File", str(BACKUPS_DIR), "Zip Archives (*.zip)")
        if file_path:
            reply = QMessageBox.warning(
                self, "Confirm Restore",
                "Restoring a backup will overwrite the current database and profile photos.\nDo you wish to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                ok = ImportExportService.restore_full_backup(file_path)
                if ok:
                    QMessageBox.information(self, "Restore Completed", "Backup restored successfully! Please restart CVCraft.")
                else:
                    QMessageBox.critical(self, "Restore Failed", "Could not restore the selected backup archive.")
