"""
CVCraft Main Window
The central desktop application shell coordinating navigation, router,
shortcuts, theme switching, and global actions.
"""

import sys
import os
import ctypes
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFileDialog, QMessageBox, QInputDialog, QFrame
)
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtCore import Qt

from config import LOGO_PATH, APP_NAME, APP_VERSION, ASSETS_DIR
from repositories.cv_repository import CVRepository
from repositories.settings_repository import SettingsRepository
from services.cv_service import CVService
from services.import_export import ImportExportService
from services.pdf_service import PDFService
from models.cv_model import CVDocument
from ui.theme import get_stylesheet
from ui.components.logo_widget import LogoWidget
from ui.components.toast import Toast

from ui.views.splash_view import SplashView
from ui.views.onboarding_view import OnboardingView
from ui.views.dashboard_view import DashboardView
from ui.views.my_cvs_view import MyCVsView
from ui.views.workspace_view import WorkspaceView
from ui.views.templates_view import TemplatesView
from ui.views.job_match_view import JobMatchView
from ui.views.settings_view import SettingsView
from ui.views.about_view import AboutView

def get_multi_icon() -> QIcon:
    ico_p = ASSETS_DIR / "cvcraft.ico"
    if ico_p.exists():
        return QIcon(str(ico_p.resolve()))
    logo_p = ASSETS_DIR / "CVCraft-logo.png"
    if logo_p.exists():
        return QIcon(str(logo_p.resolve()))
    return QIcon()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Build. Craft. Get Noticed.")
        self.resize(1200, 760)
        self.setMinimumSize(960, 560)

        # Center on primary screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.geometry()
            self.move(
                max(0, (screen_geom.width() - 1200) // 2),
                max(0, (screen_geom.height() - 760) // 2)
            )

        # Set Multi-Resolution Window Icon & Taskbar Identity
        self.setWindowIcon(get_multi_icon())
        self._apply_windows_taskbar_icon()

        self.cv_repo = CVRepository()
        self.settings_repo = SettingsRepository()

        # Apply Saved Theme Globally
        current_theme = self.settings_repo.get("theme", "dark")
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(current_theme))
        self.setStyleSheet(get_stylesheet(current_theme))

        # Root Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self._setup_sidebar()
        self._setup_router()
        self._setup_shortcuts()

        # Toast overlay
        self.toast = Toast(self)

        # First Launch Check
        is_first_launch = (self.settings_repo.get("onboarding_completed", "false") != "true")
        if is_first_launch and self.cv_repo.get_stats()["total_cvs"] == 0:
            self.router.setCurrentWidget(self.onboarding_view)
        else:
            self.show_dashboard()

    def _setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(225)
        s_layout = QVBoxLayout(self.sidebar)
        s_layout.setContentsMargins(10, 16, 10, 16)
        s_layout.setSpacing(6)

        # Header Row: Logo + Sidebar Toggle
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.setSpacing(4)
        self.logo_w = LogoWidget(compact=False)
        logo_row.addWidget(self.logo_w)
        logo_row.addStretch()

        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setFixedSize(28, 28)
        self.sidebar_toggle_btn.setProperty("class", "GhostBtn")
        self.sidebar_toggle_btn.setToolTip("Toggle Sidebar (Ctrl+B)")
        self.sidebar_toggle_btn.clicked.connect(self._toggle_sidebar)
        logo_row.addWidget(self.sidebar_toggle_btn)

        s_layout.addLayout(logo_row)
        s_layout.addSpacing(10)

        # Nav Buttons Definition
        self.nav_definitions = {
            "dashboard": ("📊", "Dashboard"),
            "my_cvs": ("📁", "My CVs"),
            "create_cv": ("➕", "Create CV"),
            "templates": ("🎨", "Templates"),
            "job_match": ("🎯", "Job Match / ATS"),
            "settings": ("⚙️", "Settings"),
            "about": ("ℹ️", "About CVCraft")
        }

        self.nav_btns = {}
        for key, (icon, label) in self.nav_definitions.items():
            btn = QPushButton(f"{icon}  {label}")
            btn.setProperty("class", "NavBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._on_nav_clicked(k))
            s_layout.addWidget(btn)
            self.nav_btns[key] = btn

        s_layout.addStretch()

        # Bottom Sidebar: Theme toggle, profile info, version
        bottom_box = QVBoxLayout()
        bottom_box.setSpacing(6)

        current_theme = self.settings_repo.get("theme", "dark")
        toggle_label = "☀️  Switch to Light" if current_theme == "dark" else "🌙  Switch to Dark"
        self.theme_toggle_btn = QPushButton(toggle_label)
        self.theme_toggle_btn.setProperty("class", "SecondaryBtn")
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        bottom_box.addWidget(self.theme_toggle_btn)

        self.profile_lbl = QLabel("● Local Profile • Offline")
        self.profile_lbl.setStyleSheet("font-size: 11px; color: #10B981; font-weight: 500;")
        bottom_box.addWidget(self.profile_lbl)

        self.ver_lbl = QLabel(f"{APP_NAME} v{APP_VERSION}")
        self.ver_lbl.setStyleSheet("font-size: 10px; color: #64748B;")
        bottom_box.addWidget(self.ver_lbl)

        s_layout.addLayout(bottom_box)
        self.root_layout.addWidget(self.sidebar)

    def _setup_router(self):
        self.router = QStackedWidget()
        self.router.setObjectName("MainContent")

        # Views
        self.onboarding_view = OnboardingView()
        self.onboarding_view.create_cv_clicked.connect(self.create_new_cv)
        self.onboarding_view.load_sample_clicked.connect(self.load_demo_cv)
        self.onboarding_view.explore_templates_clicked.connect(lambda: self._on_nav_clicked("templates"))

        self.dashboard_view = DashboardView(self.cv_repo)
        self.dashboard_view.create_cv_requested.connect(self.create_new_cv)
        self.dashboard_view.import_cv_requested.connect(self.import_cv)
        self.dashboard_view.templates_requested.connect(lambda: self._on_nav_clicked("templates"))
        self.dashboard_view.load_demo_requested.connect(self.load_demo_cv)
        self.dashboard_view.edit_cv_requested.connect(self.open_editor)
        self.dashboard_view.export_cv_requested.connect(self.quick_export_pdf)
        self.dashboard_view.duplicate_cv_requested.connect(self.duplicate_cv)
        self.dashboard_view.delete_cv_requested.connect(self.delete_cv)
        self.dashboard_view.version_cv_requested.connect(self.create_cv_version)

        self.my_cvs_view = MyCVsView(self.cv_repo)
        self.my_cvs_view.create_cv_requested.connect(self.create_new_cv)
        self.my_cvs_view.edit_cv_requested.connect(self.open_editor)
        self.my_cvs_view.export_cv_requested.connect(self.quick_export_pdf)
        self.my_cvs_view.duplicate_cv_requested.connect(self.duplicate_cv)
        self.my_cvs_view.version_cv_requested.connect(self.create_cv_version)

        self.workspace_view = WorkspaceView(self.cv_repo)
        self.workspace_view.back_requested.connect(self.show_dashboard)
        self.workspace_view.tailor_requested.connect(self.open_tailor_for_cv)

        self.templates_view = TemplatesView()
        self.templates_view.template_selected.connect(self._on_template_selected)
        self.templates_view.create_with_template_requested.connect(self.create_new_cv_with_template)

        self.job_match_view = JobMatchView(self.cv_repo)
        self.job_match_view.cv_updated.connect(self._on_cv_updated)

        self.settings_view = SettingsView(self.settings_repo)
        self.settings_view.theme_changed.connect(self._apply_theme)

        self.about_view = AboutView()
        self.about_view.load_demo_requested.connect(self.load_demo_cv)

        # Add to stack
        self.router.addWidget(self.onboarding_view)
        self.router.addWidget(self.dashboard_view)
        self.router.addWidget(self.my_cvs_view)
        self.router.addWidget(self.workspace_view)
        self.router.addWidget(self.templates_view)
        self.router.addWidget(self.job_match_view)
        self.router.addWidget(self.settings_view)
        self.router.addWidget(self.about_view)

        self.root_layout.addWidget(self.router, stretch=1)

    def _setup_shortcuts(self):
        # Global shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_cv)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_active_cv)
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_active_cv)
        QShortcut(QKeySequence("Ctrl+B"), self, self._toggle_sidebar)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.workspace_view.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.workspace_view.redo)

    def _toggle_sidebar(self):
        self._sidebar_collapsed = not getattr(self, "_sidebar_collapsed", False)
        if self._sidebar_collapsed:
            self.sidebar.setFixedWidth(56)
            self.logo_w.hide()
            self.profile_lbl.hide()
            self.ver_lbl.hide()
            current_theme = self.settings_repo.get("theme", "dark")
            self.theme_toggle_btn.setText("☀️" if current_theme == "dark" else "🌙")
            self.theme_toggle_btn.setToolTip("Toggle Theme")
            for key, (icon, label) in self.nav_definitions.items():
                btn = self.nav_btns[key]
                btn.setText(icon)
                btn.setToolTip(label)
                btn.setStyleSheet("padding: 9px 0px; text-align: center; font-size: 15px;")
        else:
            self.sidebar.setFixedWidth(225)
            self.logo_w.show()
            self.profile_lbl.show()
            self.ver_lbl.show()
            current_theme = self.settings_repo.get("theme", "dark")
            self.theme_toggle_btn.setText("☀️  Switch to Light" if current_theme == "dark" else "🌙  Switch to Dark")
            self.theme_toggle_btn.setToolTip("")
            for key, (icon, label) in self.nav_definitions.items():
                btn = self.nav_btns[key]
                btn.setText(f"{icon}  {label}")
                btn.setToolTip("")
                btn.setStyleSheet("")

    def _set_active_nav(self, active_key: str):
        for k, btn in self.nav_btns.items():
            btn.setChecked(k == active_key)

    def _on_nav_clicked(self, key: str):
        self._set_active_nav(key)
        if key == "dashboard":
            self.show_dashboard()
        elif key == "my_cvs":
            self.my_cvs_view.refresh()
            self.router.setCurrentWidget(self.my_cvs_view)
        elif key == "create_cv":
            self.create_new_cv()
        elif key == "templates":
            self.router.setCurrentWidget(self.templates_view)
        elif key == "job_match":
            self.job_match_view.refresh()
            self.router.setCurrentWidget(self.job_match_view)
        elif key == "settings":
            self.router.setCurrentWidget(self.settings_view)
        elif key == "about":
            self.router.setCurrentWidget(self.about_view)

    def show_dashboard(self):
        self._set_active_nav("dashboard")
        self.dashboard_view.refresh()
        self.router.setCurrentWidget(self.dashboard_view)

    def create_new_cv(self):
        from models.cv_model import ExperienceItem, EducationItem, SkillItem
        cv = CVDocument(name="My Professional CV", job_target="Target Role")
        cv.personal.full_name = "Your Name"
        cv.personal.professional_title = "Professional Title"
        cv.summary = "A brief summary of your background, core strengths, and career highlights."
        cv.experience = [
            ExperienceItem(
                company="Company Name",
                job_title="Job Title",
                location="City, Country",
                start_date="2022",
                end_date="Present",
                is_current=True,
                responsibilities="• Spearheaded key projects and delivered measurable outcomes.\n• Collaborated cross-functionally to achieve strategic goals."
            )
        ]
        cv.education = [
            EducationItem(
                institution="University Name",
                degree="Bachelor's Degree",
                field_of_study="Field of Study",
                start_date="2018",
                end_date="2022"
            )
        ]
        cv.skills = [
            SkillItem(name="Project Management", category="Soft Skills", proficiency="Advanced"),
            SkillItem(name="Strategic Planning", category="Soft Skills", proficiency="Expert"),
            SkillItem(name="Core Technical Skill", category="Technical Skills", proficiency="Advanced")
        ]
        default_tpl = self.settings_repo.get("default_template", "modern")
        default_pal = self.settings_repo.get("default_palette", "Deep Indigo")
        cv.template_id = default_tpl
        cv.customization.accent_palette = default_pal
        self.cv_repo.save(cv, completion_pct=45)
        self.settings_repo.set("onboarding_completed", "true")
        self.open_editor(cv.id)
        self.toast.show_message("Created new CV document")

    def load_demo_cv(self):
        demo_cv = CVService.create_sample_cv()
        score, _ = CVService.calculate_completion(demo_cv)
        self.cv_repo.save(demo_cv, completion_pct=score)
        self.settings_repo.set("onboarding_completed", "true")
        self.open_editor(demo_cv.id)
        self.toast.show_message("Loaded realistic Demo CV (Alex Mitchell)")

    def open_editor(self, cv_id: str):
        cv = self.cv_repo.get_by_id(cv_id)
        if cv:
            for btn in self.nav_btns.values():
                btn.setChecked(False)
            self.workspace_view.load_cv(cv)
            self.router.setCurrentWidget(self.workspace_view)

    def quick_export_pdf(self, cv_id: str):
        cv = self.cv_repo.get_by_id(cv_id)
        if not cv: return
        try:
            suggested_name = f"{cv.name.replace(' ', '_')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Document", suggested_name, "PDF Documents (*.pdf);;High-Res Images (*.png)",
                options=QFileDialog.Option.DontUseNativeDialog
            )
            if file_path:
                if file_path.lower().endswith(".png"):
                    saved = PDFService.export_images(cv, file_path, dpi=300)
                    if saved:
                        self.cv_repo.record_export(cv.id, cv.name, saved[0])
                        self.toast.show_message(f"Exported {len(saved)} image(s) (300 DPI)")
                else:
                    if not file_path.lower().endswith(".pdf"):
                        file_path += ".pdf"
                    PDFService.export_pdf_file(cv, file_path)
                    self.cv_repo.record_export(cv.id, cv.name, file_path)
                    self.toast.show_message(f"Exported to {Path(file_path).name}")
                self.dashboard_view.refresh()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Export Failed", f"An error occurred while exporting:\n\n{str(e)}")

    def duplicate_cv(self, cv_id: str):
        new_cv = self.cv_repo.duplicate(cv_id, as_version=False)
        if new_cv:
            self.toast.show_message(f"Duplicated: {new_cv.name}")
            if self.router.currentWidget() == self.my_cvs_view:
                self.my_cvs_view.refresh()
            else:
                self.dashboard_view.refresh()

    def create_cv_version(self, cv_id: str):
        orig = self.cv_repo.get_by_id(cv_id)
        if not orig: return
        label, ok = QInputDialog.getText(
            self, "Create Job-Specific Version",
            "Enter target version label (e.g. 'Backend Engineer', 'Internship'):",
            text="Specialized Version"
        )
        if ok and label.strip():
            new_cv = self.cv_repo.duplicate(cv_id, as_version=True, version_label=label.strip())
            if new_cv:
                self.toast.show_message(f"Created version '{label.strip()}'")
                self.open_editor(new_cv.id)

    def delete_cv(self, cv_id: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to permanently delete this CV?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cv_repo.delete(cv_id)
            self.dashboard_view.refresh()
            self.toast.show_message("CV deleted")

    def import_cv(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import CVCraft Document", "", "CVCraft Files (*.cvcv);;JSON Files (*.json)",
                options=QFileDialog.Option.DontUseNativeDialog
            )
            if file_path:
                cv = ImportExportService.import_cvcv_file(file_path)
                if cv:
                    score, _ = CVService.calculate_completion(cv)
                    self.cv_repo.save(cv, completion_pct=score)
                    self.toast.show_message(f"Imported: {cv.name}")
                    self.open_editor(cv.id)
        except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Could not import file: {str(e)}")

    def open_tailor_for_cv(self, cv_id: str):
        self._set_active_nav("job_match")
        self.job_match_view.refresh(preselect_cv_id=cv_id)
        self.router.setCurrentWidget(self.job_match_view)

    def _on_template_selected(self, template_id: str):
        # If workspace currently has an active CV, apply it directly; otherwise create new with template
        if self.workspace_view.cv:
            self.workspace_view.cv.template_id = template_id
            self.workspace_view._schedule_save()
            self.workspace_view.preview_widget.update_preview(self.workspace_view.cv)
            self.router.setCurrentWidget(self.workspace_view)
            self.toast.show_message(f"Applied template: {template_id.title()}")
        else:
            self.create_new_cv_with_template(template_id)

    def create_new_cv_with_template(self, template_id: str):
        from models.cv_model import ExperienceItem, EducationItem, SkillItem
        tpl_name = template_id.replace("_", " ").title()
        cv = CVDocument(name=f"My {tpl_name} CV", job_target="Target Role", template_id=template_id)
        cv.personal.full_name = "Alex Mitchell"
        cv.personal.professional_title = "Senior Professional"
        cv.personal.email = "alex.mitchell@example.com"
        cv.personal.phone = "+1 (555) 234-5678"
        cv.personal.location = "San Francisco, CA"
        cv.personal.linkedin = "linkedin.com/in/alexmitchell"
        cv.personal.github = "github.com/alexmitchell"
        cv.summary = "Accomplished professional with a proven track record of engineering scalable solutions, optimizing operations, and delivering measurable impact across high-growth initiatives."
        cv.experience = [
            ExperienceItem(
                company="Apex Innovations Inc.",
                job_title="Lead Engineer / Project Lead",
                location="San Francisco, CA",
                start_date="2021",
                end_date="Present",
                is_current=True,
                responsibilities="• Spearheaded core product architecture reducing latency by 42% and serving 2M+ daily requests.\n• Led a cross-functional agile team of 8 engineers delivering major quarterly milestones on schedule.\n• Designed and maintained automated CI/CD deployment pipelines with 99.98% uptime.",
                achievements="Awarded Excellence in Technical Leadership (2023)"
            ),
            ExperienceItem(
                company="Vertex Technologies",
                job_title="Software Engineer",
                location="San Jose, CA",
                start_date="2018",
                end_date="2021",
                is_current=False,
                responsibilities="• Built scalable REST APIs and microservices handling 50k+ transactions per minute.\n• Optimized database queries and caching layers resulting in a 35% reduction in compute costs.\n• Mentored 3 junior developers through onboarding and code review standards."
            )
        ]
        cv.education = [
            EducationItem(
                institution="University of California, Berkeley",
                degree="B.S. in Computer Science",
                field_of_study="Computer Science & Engineering",
                start_date="2014",
                end_date="2018",
                grade="Magna Cum Laude (3.88 GPA)"
            )
        ]
        cv.skills = [
            SkillItem(name="Python & TypeScript", category="Technical Skills", proficiency="Expert"),
            SkillItem(name="Cloud Architecture (AWS / GCP)", category="Technical Skills", proficiency="Advanced"),
            SkillItem(name="System Design & Scalability", category="Technical Skills", proficiency="Expert"),
            SkillItem(name="Agile Project Leadership", category="Soft Skills", proficiency="Expert"),
            SkillItem(name="Strategic Planning", category="Soft Skills", proficiency="Advanced")
        ]
        default_pal = self.settings_repo.get("default_palette", "Deep Indigo")
        cv.customization.accent_palette = default_pal
        self.cv_repo.save(cv, completion_pct=85)
        self.settings_repo.set("onboarding_completed", "true")
        self.open_editor(cv.id)
        self.toast.show_message(f"Created new CV with '{tpl_name}' template")

    def _on_cv_updated(self, cv_id: str):
        if self.workspace_view.cv and self.workspace_view.cv.id == cv_id:
            cv = self.cv_repo.get_by_id(cv_id)
            if cv: self.workspace_view.load_cv(cv)

    def _save_active_cv(self):
        if self.router.currentWidget() == self.workspace_view:
            self.workspace_view._auto_save()
            self.toast.show_message("Saved (Ctrl+S)")

    def _export_active_cv(self):
        if self.router.currentWidget() == self.workspace_view:
            self.workspace_view.export_pdf()

    def _toggle_theme(self):
        current = self.settings_repo.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        self.settings_repo.set("theme", new_theme)
        self._apply_theme(new_theme)

    def _apply_theme(self, theme_name: str):
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        stylesheet = get_stylesheet(theme_name)
        if app:
            app.setStyleSheet(stylesheet)
        self.setStyleSheet(stylesheet)

        # Update sidebar button text
        if getattr(self, "_sidebar_collapsed", False):
            self.theme_toggle_btn.setText("☀️" if theme_name == "dark" else "🌙")
        else:
            if theme_name == "dark":
                self.theme_toggle_btn.setText("☀️  Switch to Light")
            else:
                self.theme_toggle_btn.setText("🌙  Switch to Dark")

        # Sync SettingsView theme combobox if open
        if hasattr(self, 'settings_view') and hasattr(self.settings_view, 'theme_combo'):
            idx = 0 if theme_name == "dark" else 1
            if self.settings_view.theme_combo.currentIndex() != idx:
                self.settings_view.theme_combo.blockSignals(True)
                self.settings_view.theme_combo.setCurrentIndex(idx)
                self.settings_view.theme_combo.blockSignals(False)

        self.toast.show_message(f"Switched to {theme_name.title()} mode")

    def _apply_windows_taskbar_icon(self):
        """
        Binds the high-resolution CVCraft icon directly to the Windows Taskbar and HWND.
        Uses COM IPropertyStore to explicitly set AppUserModelID and RelaunchIconResource.
        """
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                ico_path = str((ASSETS_DIR / "cvcraft.ico").resolve())
                app_id = "CVCraft.ProfessionalResumeBuilder.App.1.0"

                # 1. Bind Windows Taskbar Shell Property Store (Windows 10/11 Taskbar Grouping & Icon)
                try:
                    from win32com.propsys import propsys, pscon
                    store = propsys.SHGetPropertyStoreForWindow(hwnd)
                    if store:
                        store.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType(app_id))
                        store.SetValue(pscon.PKEY_AppUserModel_RelaunchIconResource, propsys.PROPVARIANTType(f"{ico_path},0"))
                        store.SetValue(pscon.PKEY_AppUserModel_RelaunchDisplayNameResource, propsys.PROPVARIANTType("CVCraft"))
                        store.Commit()
                except Exception:
                    pass

                # 2. Bind Win32 Class and Window Icons (Titlebar, Alt-Tab, Taskbar fallback)
                if os.path.exists(ico_path):
                    from ctypes import wintypes
                    user32 = ctypes.windll.user32
                    user32.LoadImageW.argtypes = [
                        wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                        ctypes.c_int, ctypes.c_int, wintypes.UINT
                    ]
                    user32.LoadImageW.restype = wintypes.HANDLE
                    user32.SendMessageW.argtypes = [
                        wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
                    ]
                    user32.SendMessageW.restype = wintypes.LPARAM

                    IMAGE_ICON = 1
                    LR_LOADFROMFILE = 0x00000010
                    hicon_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
                    hicon_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                    if hicon_big:
                        user32.SendMessageW(hwnd, 0x0080, 1, hicon_big)
                    if hicon_small:
                        user32.SendMessageW(hwnd, 0x0080, 0, hicon_small)

                    # Force Window Class Icon for Windows Taskbar Shell
                    SetClassLongPtr = getattr(user32, 'SetClassLongPtrW', getattr(user32, 'SetClassLongW', None))
                    if SetClassLongPtr:
                        SetClassLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.HANDLE]
                        SetClassLongPtr.restype = wintypes.HANDLE
                        if hicon_big:
                            SetClassLongPtr(hwnd, -14, hicon_big)
                        if hicon_small:
                            SetClassLongPtr(hwnd, -34, hicon_small)
            except Exception:
                pass

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_windows_taskbar_icon()

