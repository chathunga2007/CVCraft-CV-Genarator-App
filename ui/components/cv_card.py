"""
CVCraft CV Card Component
Displays CV metadata, completion indicator, template badge, and action buttons.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QMenu, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Dict, Any

class CVCard(QFrame):
    edit_requested = pyqtSignal(str)
    duplicate_requested = pyqtSignal(str)
    export_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)
    version_requested = pyqtSignal(str)

    def __init__(self, cv_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.cv_data = cv_data
        self.cv_id = cv_data["id"]
        self.setProperty("class", "Card")
        self.setStyleSheet("""
            QFrame.Card {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
            }
            QFrame.Card:hover {
                border-color: #6366F1;
                background-color: #232F42;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header: Name + Template Badge
        top_row = QHBoxLayout()
        name_lbl = QLabel(cv_data.get("name", "Untitled CV"))
        name_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        
        tpl_name = cv_data.get("template_id", "modern").replace("_", " ").title()
        tpl_badge = QLabel(tpl_name)
        tpl_badge.setStyleSheet("""
            background-color: #312E81;
            color: #C7D2FE;
            font-size: 10px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
        """)
        
        top_row.addWidget(name_lbl)
        top_row.addStretch()
        top_row.addWidget(tpl_badge)
        layout.addLayout(top_row)

        # Subtitle: Job Target / Version
        job_target = cv_data.get("job_target") or "No target title"
        version_label = cv_data.get("version_label", "Main")
        sub_text = f"🎯 {job_target}"
        if version_label and version_label != "Main":
            sub_text += f" • [{version_label}]"
        
        sub_lbl = QLabel(sub_text)
        sub_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        layout.addWidget(sub_lbl)

        # Completion Progress Bar
        comp_pct = cv_data.get("completion_pct", 0)
        progress_row = QHBoxLayout()
        comp_lbl = QLabel(f"Completion: {comp_pct}%")
        comp_lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: #CBD5E1;")
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(comp_pct)
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #0F172A;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {'#10B981' if comp_pct >= 85 else '#4F46E5'};
                border-radius: 3px;
            }}
        """)
        progress_row.addWidget(comp_lbl)
        progress_row.addSpacing(8)
        progress_row.addWidget(progress)
        layout.addLayout(progress_row)

        # Timestamp
        updated = cv_data.get("updated_at", "")[:10]
        time_lbl = QLabel(f"Last edited: {updated}")
        time_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(time_lbl)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        edit_btn = QPushButton("Edit CV")
        edit_btn.setProperty("class", "PrimaryBtn")
        edit_btn.setStyleSheet("""
            background-color: #4F46E5;
            color: #FFFFFF;
            font-weight: 600;
            border-radius: 6px;
            padding: 6px 12px;
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.cv_id))
        btn_row.addWidget(edit_btn)

        export_btn = QPushButton("PDF")
        export_btn.setProperty("class", "SecondaryBtn")
        export_btn.setStyleSheet("""
            background-color: #0F172A;
            color: #E2E8F0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px 10px;
        """)
        export_btn.clicked.connect(lambda: self.export_requested.emit(self.cv_id))
        btn_row.addWidget(export_btn)

        # More menu button (Duplicate, Version, Delete)
        more_btn = QPushButton("•••")
        more_btn.setStyleSheet("""
            background-color: #0F172A;
            color: #94A3B8;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px 10px;
            font-weight: bold;
        """)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #4F46E5;
            }
        """)
        dup_action = menu.addAction("Duplicate Copy")
        dup_action.triggered.connect(lambda: self.duplicate_requested.emit(self.cv_id))
        
        ver_action = menu.addAction("Create Job-Specific Version...")
        ver_action.triggered.connect(lambda: self.version_requested.emit(self.cv_id))
        
        menu.addSeparator()
        del_action = menu.addAction("Delete CV")
        del_action.triggered.connect(lambda: self.delete_requested.emit(self.cv_id))
        
        more_btn.setMenu(menu)
        btn_row.addWidget(more_btn)

        layout.addLayout(btn_row)
