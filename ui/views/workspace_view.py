"""
CVCraft Workspace View
The 3-column powerhouse editor:
Column 1: Section Navigation & Reordering
Column 2: Dynamic Rich Form with Validation & AI Assistant
Column 3: Live Real-Time Multi-Page PDF Preview
"""

import os
import copy
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QCheckBox, QScrollArea, QFrame, QFileDialog,
    QStackedWidget, QMessageBox, QDialog, QDialogButtonBox, QListWidget,
    QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from models.cv_model import (
    CVDocument, PersonalInfo, ExperienceItem, EducationItem,
    SkillItem, ProjectItem, CertificationItem, LanguageItem,
    AchievementItem, VolunteerItem, ReferenceItem, CustomSection, CustomSectionItem
)
from services.cv_service import CVService
from services.pdf_service import PDFService
from services.ai_service import AIService
from repositories.cv_repository import CVRepository
from ui.components.live_preview_widget import LivePreviewWidget
from config import TEMPLATES, COLOR_PALETTES, PHOTOS_DIR

class AIApprovalDialog(QDialog):
    def __init__(self, title: str, original: str, suggested: str, rationale: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 480)
        self.setStyleSheet("background-color: #1E293B; color: #F8FAFC;")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel("Review AI Improvement Proposal")
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(lbl)

        rat_lbl = QLabel(f"💡 {rationale}")
        rat_lbl.setWordWrap(True)
        rat_lbl.setStyleSheet("font-size: 12px; color: #818CF8; background-color: #1E1B4B; padding: 8px; border-radius: 6px;")
        layout.addWidget(rat_lbl)

        diff_box = QHBoxLayout()
        # Original box
        orig_box = QVBoxLayout()
        orig_lbl = QLabel("Current Content:")
        orig_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #94A3B8;")
        self.orig_edit = QTextEdit(original)
        self.orig_edit.setReadOnly(True)
        self.orig_edit.setStyleSheet("background-color: #0F172A; color: #94A3B8; border: 1px solid #334155; border-radius: 6px;")
        orig_box.addWidget(orig_lbl)
        orig_box.addWidget(self.orig_edit)
        diff_box.addLayout(orig_box)

        # Suggested box
        sugg_box = QVBoxLayout()
        sugg_lbl = QLabel("Suggested Enhancement:")
        sugg_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #10B981;")
        self.sugg_edit = QTextEdit(suggested)
        self.sugg_edit.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1.5px solid #10B981; border-radius: 6px;")
        sugg_box.addWidget(sugg_lbl)
        sugg_box.addWidget(self.sugg_edit)
        diff_box.addLayout(sugg_box)
        layout.addLayout(diff_box)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        cancel_btn = QPushButton("Decline")
        cancel_btn.setStyleSheet("background-color: #334155; color: #FFFFFF; padding: 8px 16px; border-radius: 6px;")
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("✓ Apply Changes")
        apply_btn.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: 700; padding: 8px 20px; border-radius: 6px;")
        apply_btn.clicked.connect(self.accept)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(apply_btn)
        layout.addLayout(btn_box)

    def get_approved_text(self) -> str:
        return self.sugg_edit.toPlainText().strip()


class WorkspaceView(QWidget):
    back_requested = pyqtSignal()
    tailor_requested = pyqtSignal(str) # passes cv_id

    def __init__(self, cv_repo: CVRepository, parent=None):
        super().__init__(parent)
        self.repo = cv_repo
        self.cv: Optional[CVDocument] = None
        self.ai = AIService()

        # Undo / Redo stacks
        self.undo_stack: List[str] = [] # stores serialized JSON
        self.redo_stack: List[str] = []
        self._is_undoing_or_redoing = False
        self._is_loading = False

        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(1500)
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.timeout.connect(self._auto_save)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Action & Status Bar
        top_bar = QFrame()
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #0B0F19;
                border-bottom: 1px solid #1E293B;
                padding: 6px 16px;
            }
        """)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setSpacing(12)

        back_btn = QPushButton("← Dashboard")
        back_btn.setStyleSheet("background: transparent; color: #94A3B8; font-weight: 600; border: none; padding: 6px 8px;")
        back_btn.clicked.connect(self._on_back)
        tb_layout.addWidget(back_btn)

        # CV Title Edit & Target Role
        self.name_edit = QLineEdit("Untitled CV")
        self.name_edit.setFixedWidth(200)
        self.name_edit.setStyleSheet("font-size: 14px; font-weight: 700; color: #FFFFFF; background: #1E293B; border: 1px solid #334155; padding: 4px 8px; border-radius: 6px;")
        self.name_edit.textChanged.connect(self._on_title_changed)
        tb_layout.addWidget(self.name_edit)

        # Template Selector
        tb_layout.addWidget(QLabel("Template:"))
        self.tpl_combo = QComboBox()
        for t in TEMPLATES:
            self.tpl_combo.addItem(t["name"], t["id"])
        self.tpl_combo.currentIndexChanged.connect(self._on_template_changed)
        tb_layout.addWidget(self.tpl_combo)

        # Accent Color Selector
        tb_layout.addWidget(QLabel("Palette:"))
        self.color_combo = QComboBox()
        for p in COLOR_PALETTES.keys():
            self.color_combo.addItem(p, p)
        self.color_combo.currentIndexChanged.connect(self._on_palette_changed)
        tb_layout.addWidget(self.color_combo)

        # Undo / Redo
        self.undo_btn = QPushButton("↶")
        self.undo_btn.setFixedSize(28, 28)
        self.undo_btn.setToolTip("Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo)
        tb_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↷")
        self.redo_btn.setFixedSize(28, 28)
        self.redo_btn.setToolTip("Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo)
        tb_layout.addWidget(self.redo_btn)

        # Status
        self.status_lbl = QLabel("Saved")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #10B981; font-weight: 600;")
        tb_layout.addWidget(self.status_lbl)

        tb_layout.addStretch()

        # Tailor / ATS Button
        tailor_btn = QPushButton("🎯 Tailor to Job")
        tailor_btn.setStyleSheet("background-color: #312E81; color: #C7D2FE; font-weight: 600; padding: 6px 12px; border-radius: 6px; border: 1px solid #4338CA;")
        tailor_btn.clicked.connect(lambda: self.tailor_requested.emit(self.cv.id if self.cv else ""))
        tb_layout.addWidget(tailor_btn)

        # Export PDF Button
        export_btn = QPushButton("Export PDF")
        export_btn.setStyleSheet("background-color: #4F46E5; color: #FFFFFF; font-weight: 700; padding: 6px 16px; border-radius: 6px; border: none;")
        export_btn.clicked.connect(self.export_pdf)
        tb_layout.addWidget(export_btn)

        main_layout.addWidget(top_bar)

        # 3-Column Workspace Body
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # COLUMN 1: Section Navigation List
        col1 = QFrame()
        col1.setFixedWidth(200)
        col1.setStyleSheet("background-color: #0B0F19; border-right: 1px solid #1E293B;")
        c1_layout = QVBoxLayout(col1)
        c1_layout.setContentsMargins(8, 12, 8, 12)
        c1_layout.setSpacing(6)

        c1_title = QLabel("SECTIONS")
        c1_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748B; padding-left: 8px; letter-spacing: 0.5px;")
        c1_layout.addWidget(c1_title)

        self.sec_list = QListWidget()
        self.sec_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #94A3B8;
                padding: 10px 12px;
                border-radius: 8px;
                font-weight: 500;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #1E293B;
                color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #4F46E5;
                color: #FFFFFF;
                font-weight: 700;
            }
        """)

        sections = [
            ("Personal Info", "👤"),
            ("Summary", "📝"),
            ("Experience", "💼"),
            ("Education", "🎓"),
            ("Skills", "⚡"),
            ("Projects", "🚀"),
            ("Certifications", "📜"),
            ("Languages", "🌐"),
            ("Achievements", "🏆"),
            ("Volunteer", "🤝"),
            ("References", "👥"),
            ("Custom Sections", "✨")
        ]
        for name, icon in sections:
            item = QListWidgetItem(f"{icon}  {name}")
            self.sec_list.addItem(item)
        
        self.sec_list.currentRowChanged.connect(self._on_section_selected)
        c1_layout.addWidget(self.sec_list)
        
        body_layout.addWidget(col1)

        # COLUMN 2: Form Editor Stack
        col2 = QFrame()
        col2.setStyleSheet("background-color: #0F172A;")
        c2_layout = QVBoxLayout(col2)
        c2_layout.setContentsMargins(16, 16, 16, 16)

        scroll_form = QScrollArea()
        scroll_form.setWidgetResizable(True)
        scroll_form.setStyleSheet("background: transparent; border: none;")

        self.form_stack = QStackedWidget()
        self._build_personal_form()
        self._build_summary_form()
        self._build_experience_form()
        self._build_education_form()
        self._build_skills_form()
        self._build_projects_form()
        self._build_certifications_form()
        self._build_languages_form()
        self._build_achievements_form()
        self._build_volunteer_form()
        self._build_references_form()
        self._build_custom_sections_form()

        scroll_form.setWidget(self.form_stack)
        c2_layout.addWidget(scroll_form)
        body_layout.addWidget(col2, stretch=5)

        # COLUMN 3: Live Preview
        self.preview_widget = LivePreviewWidget()
        body_layout.addWidget(self.preview_widget, stretch=6)

        main_layout.addWidget(body)

    # =========================================================================
    # FORM 1: PERSONAL INFORMATION
    # =========================================================================
    def _build_personal_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        hdr = QLabel("Personal Information")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(hdr)

        # Photo row
        photo_box = QHBoxLayout()
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(60, 60)
        self.photo_preview.setStyleSheet("border-radius: 30px; border: 1.5px dashed #4F46E5; background-color: #1E293B;")
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setText("Photo")
        photo_box.addWidget(self.photo_preview)

        upload_btn = QPushButton("Upload Photo")
        upload_btn.setStyleSheet("background-color: #1E293B; color: #FFFFFF; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px;")
        upload_btn.clicked.connect(self._upload_photo)
        photo_box.addWidget(upload_btn)

        remove_photo_btn = QPushButton("Remove")
        remove_photo_btn.setStyleSheet("background-color: transparent; color: #94A3B8; border: none; padding: 6px;")
        remove_photo_btn.clicked.connect(self._remove_photo)
        photo_box.addWidget(remove_photo_btn)

        photo_box.addStretch()
        layout.addLayout(photo_box)

        # Fields
        self.pi_name = self._add_field(layout, "Full Name *", "Alexander Mitchell")
        self.pi_title = self._add_field(layout, "Professional Title *", "Senior Software Engineer")
        
        row1 = QHBoxLayout()
        self.pi_email = self._add_field(row1, "Email *", "alex.mitchell@example.com")
        self.pi_phone = self._add_field(row1, "Phone *", "+1 (555) 234-5678")
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.pi_loc = self._add_field(row2, "Location (City, Country)", "San Francisco, CA")
        self.pi_web = self._add_field(row2, "Personal Website", "https://alexmitchell.tech")
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.pi_linkedin = self._add_field(row3, "LinkedIn URL", "https://linkedin.com/in/alexmitchell")
        self.pi_github = self._add_field(row3, "GitHub URL", "https://github.com/alexmitchell")
        layout.addLayout(row3)

        self.pi_portfolio = self._add_field(layout, "Portfolio URL", "https://alexmitchell.tech/portfolio")

        layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 2: PROFESSIONAL SUMMARY
    # =========================================================================
    def _build_summary_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Professional Summary")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        ai_btn = QPushButton("✨ AI Improve Summary")
        ai_btn.setStyleSheet("background-color: #312E81; color: #C7D2FE; font-weight: 600; padding: 6px 12px; border-radius: 6px; border: 1px solid #6366F1;")
        ai_btn.clicked.connect(self._ai_improve_summary)
        hdr_row.addWidget(ai_btn)
        layout.addLayout(hdr_row)

        desc = QLabel("Craft a compelling 2-4 sentence overview highlighting your core value and achievements.")
        desc.setStyleSheet("font-size: 12px; color: #94A3B8;")
        layout.addWidget(desc)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlaceholderText("Write your executive summary here...")
        self.summary_edit.setFixedHeight(180)
        self.summary_edit.textChanged.connect(self._on_form_change)
        layout.addWidget(self.summary_edit)

        self.summary_count_lbl = QLabel("0 characters | 0 words")
        self.summary_count_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(self.summary_count_lbl)

        layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 3: WORK EXPERIENCE
    # =========================================================================
    def _build_experience_form(self):
        page = QWidget()
        self.exp_page_layout = QVBoxLayout(page)
        self.exp_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Work Experience")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_btn = QPushButton("+ Add Position")
        add_btn.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_btn.clicked.connect(self._add_experience_item)
        hdr_row.addWidget(add_btn)
        self.exp_page_layout.addLayout(hdr_row)

        self.exp_container = QVBoxLayout()
        self.exp_container.setSpacing(14)
        self.exp_page_layout.addLayout(self.exp_container)

        self.exp_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 4: EDUCATION
    # =========================================================================
    def _build_education_form(self):
        page = QWidget()
        self.edu_page_layout = QVBoxLayout(page)
        self.edu_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Education")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_btn = QPushButton("+ Add Degree / School")
        add_btn.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_btn.clicked.connect(self._add_education_item)
        hdr_row.addWidget(add_btn)
        self.edu_page_layout.addLayout(hdr_row)

        self.edu_container = QVBoxLayout()
        self.edu_container.setSpacing(14)
        self.edu_page_layout.addLayout(self.edu_container)

        self.edu_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 5: SKILLS
    # =========================================================================
    def _build_skills_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Skills & Competencies")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        ai_btn = QPushButton("✨ AI Suggest Skills")
        ai_btn.setStyleSheet("background-color: #312E81; color: #C7D2FE; font-weight: 600; padding: 6px 12px; border-radius: 6px; border: 1px solid #6366F1;")
        ai_btn.clicked.connect(self._ai_suggest_skills)
        hdr_row.addWidget(ai_btn)
        layout.addLayout(hdr_row)

        add_box = QHBoxLayout()
        self.skill_name_input = QLineEdit()
        self.skill_name_input.setPlaceholderText("Skill name (e.g. Python, Docker, React)")
        self.skill_cat_combo = QComboBox()
        self.skill_cat_combo.addItems(["Technical Skills", "Programming Languages", "Frameworks", "Tools", "Soft Skills"])
        self.skill_prof_combo = QComboBox()
        self.skill_prof_combo.addItems(["Beginner", "Intermediate", "Advanced", "Expert"])
        
        add_skill_btn = QPushButton("Add")
        add_skill_btn.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_skill_btn.clicked.connect(self._add_skill)

        add_box.addWidget(self.skill_name_input, stretch=2)
        add_box.addWidget(self.skill_cat_combo, stretch=1)
        add_box.addWidget(self.skill_prof_combo, stretch=1)
        add_box.addWidget(add_skill_btn)
        layout.addLayout(add_box)

        # Skills list
        self.skills_list_widget = QListWidget()
        self.skills_list_widget.setFixedHeight(260)
        self.skills_list_widget.setStyleSheet("background: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 4px;")
        layout.addWidget(self.skills_list_widget)

        del_skill_btn = QPushButton("Delete Selected Skill")
        del_skill_btn.setStyleSheet("background-color: #BE123C; color: white; padding: 6px 12px; border-radius: 6px; max-width: 160px;")
        del_skill_btn.clicked.connect(self._delete_skill)
        layout.addWidget(del_skill_btn)

        layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 6: PROJECTS
    # =========================================================================
    def _build_projects_form(self):
        page = QWidget()
        self.proj_page_layout = QVBoxLayout(page)
        self.proj_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Key Projects")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_btn = QPushButton("+ Add Project")
        add_btn.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_btn.clicked.connect(self._add_project_item)
        hdr_row.addWidget(add_btn)
        self.proj_page_layout.addLayout(hdr_row)

        self.proj_container = QVBoxLayout()
        self.proj_container.setSpacing(14)
        self.proj_page_layout.addLayout(self.proj_container)

        self.proj_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 7: CERTIFICATIONS
    # =========================================================================
    def _build_certifications_form(self):
        page = QWidget()
        self.cert_page_layout = QVBoxLayout(page)
        self.cert_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Certifications & Licenses")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_btn = QPushButton("+ Add Certification")
        add_btn.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_btn.clicked.connect(self._add_cert_item)
        hdr_row.addWidget(add_btn)
        self.cert_page_layout.addLayout(hdr_row)

        self.cert_container = QVBoxLayout()
        self.cert_page_layout.addLayout(self.cert_container)
        self.cert_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 8: LANGUAGES
    # =========================================================================
    def _build_languages_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        hdr = QLabel("Languages")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(hdr)

        box = QHBoxLayout()
        self.lang_input = QLineEdit()
        self.lang_input.setPlaceholderText("Language (e.g. English, French, Japanese)")
        self.lang_prof_combo = QComboBox()
        self.lang_prof_combo.addItems(["Native", "Fluent", "Intermediate", "Conversational", "Basic"])
        add_b = QPushButton("Add")
        add_b.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_b.clicked.connect(self._add_language)
        box.addWidget(self.lang_input, stretch=2)
        box.addWidget(self.lang_prof_combo, stretch=1)
        box.addWidget(add_b)
        layout.addLayout(box)

        self.lang_list_widget = QListWidget()
        self.lang_list_widget.setFixedHeight(200)
        self.lang_list_widget.setStyleSheet("background: #0F172A; border: 1px solid #334155; border-radius: 8px;")
        layout.addWidget(self.lang_list_widget)

        del_b = QPushButton("Delete Selected")
        del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 6px 12px; border-radius: 6px; max-width: 140px;")
        del_b.clicked.connect(self._delete_language)
        layout.addWidget(del_b)

        layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 9: ACHIEVEMENTS
    # =========================================================================
    def _build_achievements_form(self):
        page = QWidget()
        self.ach_page_layout = QVBoxLayout(page)
        self.ach_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Honors & Achievements")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_b = QPushButton("+ Add Achievement")
        add_b.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_b.clicked.connect(self._add_achievement_item)
        hdr_row.addWidget(add_b)
        self.ach_page_layout.addLayout(hdr_row)

        self.ach_container = QVBoxLayout()
        self.ach_page_layout.addLayout(self.ach_container)
        self.ach_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 10: VOLUNTEER
    # =========================================================================
    def _build_volunteer_form(self):
        page = QWidget()
        self.vol_page_layout = QVBoxLayout(page)
        self.vol_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Volunteer & Community")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_b = QPushButton("+ Add Volunteer Entry")
        add_b.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_b.clicked.connect(self._add_volunteer_item)
        hdr_row.addWidget(add_b)
        self.vol_page_layout.addLayout(hdr_row)

        self.vol_container = QVBoxLayout()
        self.vol_page_layout.addLayout(self.vol_container)
        self.vol_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 11: REFERENCES
    # =========================================================================
    def _build_references_form(self):
        page = QWidget()
        self.ref_page_layout = QVBoxLayout(page)
        self.ref_page_layout.setSpacing(12)

        hdr = QLabel("References")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        self.ref_page_layout.addWidget(hdr)

        self.ref_upon_req_chk = QCheckBox("Display 'References available upon request'")
        self.ref_upon_req_chk.setStyleSheet("font-size: 13px; font-weight: 600; color: #C7D2FE;")
        self.ref_upon_req_chk.toggled.connect(self._on_ref_toggle)
        self.ref_page_layout.addWidget(self.ref_upon_req_chk)

        add_b = QPushButton("+ Add Reference Person")
        add_b.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600; max-width: 180px;")
        add_b.clicked.connect(self._add_ref_item)
        self.ref_page_layout.addWidget(add_b)

        self.ref_container = QVBoxLayout()
        self.ref_page_layout.addLayout(self.ref_container)
        self.ref_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # FORM 12: CUSTOM SECTIONS
    # =========================================================================
    def _build_custom_sections_form(self):
        page = QWidget()
        self.cust_page_layout = QVBoxLayout(page)
        self.cust_page_layout.setSpacing(12)

        hdr_row = QHBoxLayout()
        hdr = QLabel("Custom Sections (e.g. Publications, Patents, Interests)")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()

        add_b = QPushButton("+ Add Custom Section")
        add_b.setStyleSheet("background-color: #4F46E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        add_b.clicked.connect(self._add_custom_section)
        hdr_row.addWidget(add_b)
        self.cust_page_layout.addLayout(hdr_row)

        self.cust_container = QVBoxLayout()
        self.cust_page_layout.addLayout(self.cust_container)
        self.cust_page_layout.addStretch()
        self.form_stack.addWidget(page)

    # =========================================================================
    # LOAD & BIND CV DATA
    # =========================================================================
    def load_cv(self, cv: CVDocument):
        self._is_loading = True
        self.cv = cv
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._record_history()

        # Update Top Bar
        self.name_edit.setText(cv.name)
        
        idx = self.tpl_combo.findData(cv.template_id)
        if idx >= 0:
            self.tpl_combo.setCurrentIndex(idx)
        
        c_idx = self.color_combo.findData(cv.customization.accent_palette)
        if c_idx >= 0:
            self.color_combo.setCurrentIndex(c_idx)

        # Personal Info Fields
        self.pi_name.setText(cv.personal.full_name)
        self.pi_title.setText(cv.personal.professional_title)
        self.pi_email.setText(cv.personal.email)
        self.pi_phone.setText(cv.personal.phone)
        self.pi_loc.setText(cv.personal.location)
        self.pi_web.setText(cv.personal.website)
        self.pi_linkedin.setText(cv.personal.linkedin)
        self.pi_github.setText(cv.personal.github)
        self.pi_portfolio.setText(cv.personal.portfolio)
        self._update_photo_preview()

        # Summary
        self.summary_edit.setText(cv.summary)

        # Build dynamic items
        self._refresh_experience_ui()
        self._refresh_education_ui()
        self._refresh_skills_ui()
        self._refresh_projects_ui()
        self._refresh_certifications_ui()
        self._refresh_languages_ui()
        self._refresh_achievements_ui()
        self._refresh_volunteer_ui()
        self._refresh_references_ui()
        self._refresh_custom_sections_ui()

        self._is_loading = False

        # Trigger preview
        self.sec_list.setCurrentRow(0)
        self.preview_widget.update_preview(self.cv, immediate=True)

    def _on_section_selected(self, row: int):
        if row >= 0:
            self.form_stack.setCurrentIndex(row)

    def _on_title_changed(self, text: str):
        if self._is_loading or not self.cv:
            return
        self.cv.name = text.strip() or "Untitled CV"
        self._schedule_save()

    def _on_template_changed(self, idx: int):
        if self._is_loading or not self.cv:
            return
        self.cv.template_id = self.tpl_combo.currentData()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _on_palette_changed(self, idx: int):
        if self._is_loading or not self.cv:
            return
        pal_name = self.color_combo.currentData()
        self.cv.customization.accent_palette = pal_name
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _add_field(self, layout, label: str, placeholder: str) -> QLineEdit:
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setStyleSheet("background-color: #0F172A; color: #FFFFFF; border: 1px solid #334155; border-radius: 6px; padding: 6px 10px;")
        edit.textChanged.connect(self._on_form_change)
        layout.addWidget(lbl)
        layout.addWidget(edit)
        return edit

    def _on_form_change(self):
        if self._is_loading or not self.cv or self._is_undoing_or_redoing:
            return

        # Update Personal Info
        self.cv.personal.full_name = self.pi_name.text().strip()
        self.cv.personal.professional_title = self.pi_title.text().strip()
        self.cv.personal.email = self.pi_email.text().strip()
        self.cv.personal.phone = self.pi_phone.text().strip()
        self.cv.personal.location = self.pi_loc.text().strip()
        self.cv.personal.website = self.pi_web.text().strip()
        self.cv.personal.linkedin = self.pi_linkedin.text().strip()
        self.cv.personal.github = self.pi_github.text().strip()
        self.cv.personal.portfolio = self.pi_portfolio.text().strip()

        # Update Summary
        sum_text = self.summary_edit.toPlainText().strip()
        self.cv.summary = sum_text
        chars = len(sum_text)
        words = len(sum_text.split())
        self.summary_count_lbl.setText(f"{chars} characters | {words} words")

        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    # =========================================================================
    # DYNAMIC SECTION BUILDERS
    # =========================================================================
    def _refresh_experience_ui(self):
        while self.exp_container.count():
            item = self.exp_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for exp in self.cv.experience:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 12px;")
            cl = QVBoxLayout(card)
            cl.setSpacing(8)

            t_row = QHBoxLayout()
            jt = QLineEdit(exp.job_title)
            jt.setPlaceholderText("Job Title (e.g. Lead Software Engineer)")
            jt.textChanged.connect(lambda txt, e=exp: self._set_exp_field(e, 'job_title', txt))
            
            comp = QLineEdit(exp.company)
            comp.setPlaceholderText("Company Name")
            comp.textChanged.connect(lambda txt, e=exp: self._set_exp_field(e, 'company', txt))
            
            t_row.addWidget(jt, stretch=3)
            t_row.addWidget(comp, stretch=2)
            cl.addLayout(t_row)

            d_row = QHBoxLayout()
            s_date = QLineEdit(exp.start_date)
            s_date.setPlaceholderText("Start Date (e.g. 2021)")
            s_date.textChanged.connect(lambda txt, e=exp: self._set_exp_field(e, 'start_date', txt))
            
            e_date = QLineEdit(exp.end_date)
            e_date.setPlaceholderText("End Date (or Current)")
            e_date.textChanged.connect(lambda txt, e=exp: self._set_exp_field(e, 'end_date', txt))

            loc = QLineEdit(exp.location)
            loc.setPlaceholderText("Location")
            loc.textChanged.connect(lambda txt, e=exp: self._set_exp_field(e, 'location', txt))

            d_row.addWidget(s_date)
            d_row.addWidget(e_date)
            d_row.addWidget(loc)
            cl.addLayout(d_row)

            # Responsibilities
            resp = QTextEdit(exp.responsibilities)
            resp.setPlaceholderText("Key responsibilities and bullet points...")
            resp.setFixedHeight(75)
            resp.textChanged.connect(lambda r=resp, e=exp: self._set_exp_field(e, 'responsibilities', r.toPlainText()))
            cl.addWidget(resp)

            # Actions Row
            a_row = QHBoxLayout()
            polish_btn = QPushButton("✨ AI Polish Bullets")
            polish_btn.setStyleSheet("background-color: #312E81; color: #C7D2FE; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
            polish_btn.clicked.connect(lambda _, e=exp, r=resp: self._ai_polish_experience(e, r))
            a_row.addWidget(polish_btn)
            a_row.addStretch()

            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
            del_btn.clicked.connect(lambda _, e=exp: self._delete_experience(e))
            a_row.addWidget(del_btn)
            cl.addLayout(a_row)

            self.exp_container.addWidget(card)

    def _set_exp_field(self, exp_item, field_name, value):
        setattr(exp_item, field_name, value)
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _add_experience_item(self):
        new_exp = ExperienceItem(job_title="Software Engineer", company="Tech Corp", start_date="2022", end_date="Present")
        self.cv.experience.append(new_exp)
        self._refresh_experience_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_experience(self, exp_item):
        if exp_item in self.cv.experience:
            self.cv.experience.remove(exp_item)
            self._refresh_experience_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Education
    def _refresh_education_ui(self):
        while self.edu_container.count():
            item = self.edu_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for edu in self.cv.education:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 12px;")
            cl = QVBoxLayout(card)
            cl.setSpacing(6)

            r1 = QHBoxLayout()
            deg = QLineEdit(edu.degree)
            deg.setPlaceholderText("Degree (e.g. B.S. in Computer Science)")
            deg.textChanged.connect(lambda txt, ed=edu: self._set_edu_field(ed, 'degree', txt))
            inst = QLineEdit(edu.institution)
            inst.setPlaceholderText("Institution / University")
            inst.textChanged.connect(lambda txt, ed=edu: self._set_edu_field(ed, 'institution', txt))
            r1.addWidget(deg, stretch=3)
            r1.addWidget(inst, stretch=2)
            cl.addLayout(r1)

            r2 = QHBoxLayout()
            dates = QLineEdit(f"{edu.start_date} – {edu.end_date}")
            dates.setPlaceholderText("Dates (e.g. 2018 - 2022)")
            dates.textChanged.connect(lambda txt, ed=edu: self._set_edu_field(ed, 'start_date', txt))
            grd = QLineEdit(edu.grade)
            grd.setPlaceholderText("Grade / GPA (Optional)")
            grd.textChanged.connect(lambda txt, ed=edu: self._set_edu_field(ed, 'grade', txt))
            r2.addWidget(dates)
            r2.addWidget(grd)
            cl.addLayout(r2)

            act_row = QHBoxLayout()
            act_row.addStretch()
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
            del_b.clicked.connect(lambda _, ed=edu: self._delete_edu(ed))
            act_row.addWidget(del_b)
            cl.addLayout(act_row)

            self.edu_container.addWidget(card)

    def _set_edu_field(self, edu_item, field_name, value):
        setattr(edu_item, field_name, value)
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _add_education_item(self):
        new_edu = EducationItem(degree="Bachelor of Science", institution="University", start_date="2018", end_date="2022")
        self.cv.education.append(new_edu)
        self._refresh_education_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_edu(self, edu_item):
        if edu_item in self.cv.education:
            self.cv.education.remove(edu_item)
            self._refresh_education_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Skills
    def _refresh_skills_ui(self):
        self.skills_list_widget.clear()
        for s in self.cv.skills:
            item = QListWidgetItem(f"⚡ {s.name}  [{s.category}] — {s.proficiency}")
            self.skills_list_widget.addItem(item)

    def _add_skill(self):
        name = self.skill_name_input.text().strip()
        if not name:
            return
        cat = self.skill_cat_combo.currentText()
        prof = self.skill_prof_combo.currentText()
        self.cv.skills.append(SkillItem(name=name, category=cat, proficiency=prof))
        self.skill_name_input.clear()
        self._refresh_skills_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_skill(self):
        row = self.skills_list_widget.currentRow()
        if row >= 0 and row < len(self.cv.skills):
            self.cv.skills.pop(row)
            self._refresh_skills_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Projects
    def _refresh_projects_ui(self):
        while self.proj_container.count():
            item = self.proj_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for p in self.cv.projects:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 12px;")
            cl = QVBoxLayout(card)
            cl.setSpacing(6)

            r1 = QHBoxLayout()
            pn = QLineEdit(p.name)
            pn.setPlaceholderText("Project Name")
            pn.textChanged.connect(lambda txt, pr=p: setattr(pr, 'name', txt))
            tech = QLineEdit(p.technologies)
            tech.setPlaceholderText("Tech Stack (e.g. Python, Docker, React)")
            tech.textChanged.connect(lambda txt, pr=p: setattr(pr, 'technologies', txt))
            r1.addWidget(pn, stretch=2)
            r1.addWidget(tech, stretch=2)
            cl.addLayout(r1)

            r2 = QHBoxLayout()
            gh = QLineEdit(p.github_url)
            gh.setPlaceholderText("GitHub URL")
            gh.textChanged.connect(lambda txt, pr=p: setattr(pr, 'github_url', txt))
            demo = QLineEdit(p.live_demo_url)
            demo.setPlaceholderText("Live Demo URL")
            demo.textChanged.connect(lambda txt, pr=p: setattr(pr, 'live_demo_url', txt))
            r2.addWidget(gh)
            r2.addWidget(demo)
            cl.addLayout(r2)

            desc = QTextEdit(p.description)
            desc.setPlaceholderText("Project summary and impact...")
            desc.setFixedHeight(60)
            desc.textChanged.connect(lambda d=desc, pr=p: setattr(pr, 'description', d.toPlainText()))
            cl.addWidget(desc)

            act_row = QHBoxLayout()
            act_row.addStretch()
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
            del_b.clicked.connect(lambda _, pr=p: self._delete_project(pr))
            act_row.addWidget(del_b)
            cl.addLayout(act_row)

            self.proj_container.addWidget(card)

    def _add_project_item(self):
        new_proj = ProjectItem(name="New Project", technologies="Python, React")
        self.cv.projects.append(new_proj)
        self._refresh_projects_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_project(self, p):
        if p in self.cv.projects:
            self.cv.projects.remove(p)
            self._refresh_projects_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Certifications
    def _refresh_certifications_ui(self):
        while self.cert_container.count():
            item = self.cert_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for c in self.cv.certifications:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 10px;")
            cl = QVBoxLayout(card)
            cn = QLineEdit(c.name)
            cn.setPlaceholderText("Certificate Name")
            cn.textChanged.connect(lambda txt, cr=c: setattr(cr, 'name', txt))
            iss = QLineEdit(c.issuer)
            iss.setPlaceholderText("Issuing Organization")
            iss.textChanged.connect(lambda txt, cr=c: setattr(cr, 'issuer', txt))
            cl.addWidget(cn)
            cl.addWidget(iss)
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; max-width: 80px;")
            del_b.clicked.connect(lambda _, cr=c: self._delete_cert(cr))
            cl.addWidget(del_b)
            self.cert_container.addWidget(card)

    def _add_cert_item(self):
        self.cv.certifications.append(CertificationItem(name="AWS Solutions Architect", issuer="Amazon Web Services", issue_date="2024"))
        self._refresh_certifications_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_cert(self, cr):
        if cr in self.cv.certifications:
            self.cv.certifications.remove(cr)
            self._refresh_certifications_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Languages
    def _refresh_languages_ui(self):
        self.lang_list_widget.clear()
        for l in self.cv.languages:
            self.lang_list_widget.addItem(f"🌐 {l.name} ({l.proficiency})")

    def _add_language(self):
        name = self.lang_input.text().strip()
        if not name: return
        prof = self.lang_prof_combo.currentText()
        self.cv.languages.append(LanguageItem(name=name, proficiency=prof))
        self.lang_input.clear()
        self._refresh_languages_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_language(self):
        row = self.lang_list_widget.currentRow()
        if row >= 0 and row < len(self.cv.languages):
            self.cv.languages.pop(row)
            self._refresh_languages_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Achievements
    def _refresh_achievements_ui(self):
        while self.ach_container.count():
            item = self.ach_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for a in self.cv.achievements:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 10px;")
            cl = QVBoxLayout(card)
            t = QLineEdit(a.title)
            t.setPlaceholderText("Achievement Title")
            t.textChanged.connect(lambda txt, ac=a: setattr(ac, 'title', txt))
            d = QLineEdit(a.description)
            d.setPlaceholderText("Description")
            d.textChanged.connect(lambda txt, ac=a: setattr(ac, 'description', txt))
            cl.addWidget(t)
            cl.addWidget(d)
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; max-width: 80px;")
            del_b.clicked.connect(lambda _, ac=a: self._delete_ach(ac))
            cl.addWidget(del_b)
            self.ach_container.addWidget(card)

    def _add_achievement_item(self):
        self.cv.achievements.append(AchievementItem(title="Hackathon 1st Place", date="2023", description="Winner out of 40 teams"))
        self._refresh_achievements_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_ach(self, ac):
        if ac in self.cv.achievements:
            self.cv.achievements.remove(ac)
            self._refresh_achievements_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Volunteer
    def _refresh_volunteer_ui(self):
        while self.vol_container.count():
            item = self.vol_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for v in self.cv.volunteer:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 10px;")
            cl = QVBoxLayout(card)
            o = QLineEdit(v.organization)
            o.setPlaceholderText("Organization")
            o.textChanged.connect(lambda txt, vl=v: setattr(vl, 'organization', txt))
            r = QLineEdit(v.role)
            r.setPlaceholderText("Role / Contribution")
            r.textChanged.connect(lambda txt, vl=v: setattr(vl, 'role', txt))
            cl.addWidget(o)
            cl.addWidget(r)
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; max-width: 80px;")
            del_b.clicked.connect(lambda _, vl=v: self._delete_vol(vl))
            cl.addWidget(del_b)
            self.vol_container.addWidget(card)

    def _add_volunteer_item(self):
        self.cv.volunteer.append(VolunteerItem(organization="Community Center", role="Mentor"))
        self._refresh_volunteer_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_vol(self, vl):
        if vl in self.cv.volunteer:
            self.cv.volunteer.remove(vl)
            self._refresh_volunteer_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # References
    def _refresh_references_ui(self):
        self.ref_upon_req_chk.setChecked(self.cv.references_on_request)
        while self.ref_container.count():
            item = self.ref_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for ref in self.cv.references:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 10px;")
            cl = QVBoxLayout(card)
            n = QLineEdit(ref.name)
            n.setPlaceholderText("Reference Name")
            n.textChanged.connect(lambda txt, rf=ref: setattr(rf, 'name', txt))
            jt = QLineEdit(f"{ref.job_title}, {ref.company}")
            jt.setPlaceholderText("Title, Company")
            jt.textChanged.connect(lambda txt, rf=ref: setattr(rf, 'company', txt))
            em = QLineEdit(ref.email)
            em.setPlaceholderText("Email")
            em.textChanged.connect(lambda txt, rf=ref: setattr(rf, 'email', txt))
            cl.addWidget(n)
            cl.addWidget(jt)
            cl.addWidget(em)
            del_b = QPushButton("Delete")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; max-width: 80px;")
            del_b.clicked.connect(lambda _, rf=ref: self._delete_ref(rf))
            cl.addWidget(del_b)
            self.ref_container.addWidget(card)

    def _on_ref_toggle(self, checked: bool):
        if self.cv:
            self.cv.references_on_request = checked
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    def _add_ref_item(self):
        self.cv.references.append(ReferenceItem(name="Jane Doe", job_title="Director", company="Tech Corp", email="jane@example.com"))
        self._refresh_references_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_ref(self, rf):
        if rf in self.cv.references:
            self.cv.references.remove(rf)
            self._refresh_references_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # Custom Sections
    def _refresh_custom_sections_ui(self):
        while self.cust_container.count():
            item = self.cust_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for cs in self.cv.custom_sections:
            card = QFrame()
            card.setStyleSheet("background-color: #162032; border: 1px solid #27354A; border-radius: 8px; padding: 12px;")
            cl = QVBoxLayout(card)
            sn = QLineEdit(cs.section_name)
            sn.setPlaceholderText("Custom Section Title (e.g. Publications)")
            sn.textChanged.connect(lambda txt, c=cs: setattr(c, 'section_name', txt))
            cl.addWidget(sn)
            del_b = QPushButton("Delete Section")
            del_b.setStyleSheet("background-color: #BE123C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; max-width: 100px;")
            del_b.clicked.connect(lambda _, c=cs: self._delete_custom_sec(c))
            cl.addWidget(del_b)
            self.cust_container.addWidget(card)

    def _add_custom_section(self):
        self.cv.custom_sections.append(CustomSection(section_name="Publications & Research"))
        self._refresh_custom_sections_ui()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _delete_custom_sec(self, c):
        if c in self.cv.custom_sections:
            self.cv.custom_sections.remove(c)
            self._refresh_custom_sections_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # =========================================================================
    # PHOTO MANAGEMENT
    # =========================================================================
    def _upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Photo", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_path:
            self.cv.personal.profile_photo_path = file_path
            self._update_photo_preview()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    def _remove_photo(self):
        self.cv.personal.profile_photo_path = ""
        self._update_photo_preview()
        self._schedule_save()
        self.preview_widget.update_preview(self.cv)

    def _update_photo_preview(self):
        path = self.cv.personal.profile_photo_path if self.cv else ""
        if path and os.path.exists(path):
            pix = QPixmap(path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.photo_preview.setPixmap(pix)
            self.photo_preview.setText("")
        else:
            self.photo_preview.clear()
            self.photo_preview.setText("Photo")

    # =========================================================================
    # AI ASSISTANT INTERACTIONS
    # =========================================================================
    def _ai_improve_summary(self):
        current = self.summary_edit.toPlainText().strip()
        role = self.cv.personal.professional_title if self.cv else ""
        result = self.ai.improve_summary(current, role)

        dialog = AIApprovalDialog("AI Professional Summary Enhancement", result["original"], result["suggested"], result["rationale"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            approved = dialog.get_approved_text()
            self.summary_edit.setText(approved)
            self._on_form_change()

    def _ai_polish_experience(self, exp_item, text_widget: QTextEdit):
        current = text_widget.toPlainText().strip()
        result = self.ai.improve_experience_bullets(current, exp_item.job_title)

        dialog = AIApprovalDialog("AI Work Experience Enhancement", result["original"], result["suggested"], result["rationale"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            approved = dialog.get_approved_text()
            text_widget.setText(approved)
            exp_item.responsibilities = approved
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    def _ai_suggest_skills(self):
        role = self.cv.personal.professional_title if self.cv else "Software Engineer"
        suggestions = self.ai.suggest_skills_for_role(role)
        
        reply = QMessageBox.question(
            self,
            "AI Skill Suggestions",
            f"Add {len(suggestions)} top industry skills for '{role}'?\n\n" +
            "\n".join([f"• {s['name']} ({s['category']})" for s in suggestions]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for s in suggestions:
                if not any(existing.name.lower() == s["name"].lower() for existing in self.cv.skills):
                    self.cv.skills.append(SkillItem(**s))
            self._refresh_skills_ui()
            self._schedule_save()
            self.preview_widget.update_preview(self.cv)

    # =========================================================================
    # HISTORY & SAVE
    # =========================================================================
    def _schedule_save(self):
        self.status_lbl.setText("Saving...")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #F59E0B;")
        self._auto_save_timer.start()

    def _auto_save(self):
        if not self.cv:
            return
        score, _ = CVService.calculate_completion(self.cv)
        self.repo.save(self.cv, completion_pct=score)
        self._record_history()
        self.status_lbl.setText("Saved")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #10B981;")

    def _record_history(self):
        if not self.cv: return
        serialized = self.cv.to_dict()
        import json
        dumped = json.dumps(serialized)
        if not self.undo_stack or self.undo_stack[-1] != dumped:
            self.undo_stack.append(dumped)
            if len(self.undo_stack) > 30:
                self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 1:
            self._is_undoing_or_redoing = True
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            prev_dump = self.undo_stack[-1]
            import json
            prev_data = json.loads(prev_dump)
            self.load_cv(CVDocument.from_dict(prev_data))
            self._is_undoing_or_redoing = False

    def redo(self):
        if self.redo_stack:
            self._is_undoing_or_redoing = True
            next_dump = self.redo_stack.pop()
            self.undo_stack.append(next_dump)
            import json
            next_data = json.loads(next_dump)
            self.load_cv(CVDocument.from_dict(next_data))
            self._is_undoing_or_redoing = False

    def export_pdf(self):
        if not self.cv: return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", f"{self.cv.name.replace(' ', '_')}.pdf", "PDF Documents (*.pdf)"
        )
        if file_path:
            PDFService.export_pdf_file(self.cv, file_path)
            self.repo.record_export(self.cv.id, self.cv.name, file_path)
            QMessageBox.information(self, "Export Successful", f"Your CV has been exported to:\n{file_path}")

    def _on_back(self):
        self._auto_save()
        self.back_requested.emit()
