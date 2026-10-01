"""
CVCraft Interactive Template Preview Dialog
Allows users to visually inspect and zoom in on any CV template with realistic data
before applying it to their active CV or creating a new document.
"""

import io
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from config import TEMPLATES, COLOR_PALETTES, ASSETS_DIR
from models.cv_model import CVDocument
from services.cv_service import CVService
from services.pdf_service import PDFService

class TemplatePreviewDialog(QDialog):
    template_applied = pyqtSignal(str) # passes template_id
    create_requested = pyqtSignal(str)  # passes template_id

    def __init__(self, initial_template_id: str = "classic_sidebar", active_cv: Optional[CVDocument] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Architectural Preview — CVCraft")
        self.resize(1020, 720)
        self.setMinimumSize(850, 580)

        # Set Window Icon
        ico_path = ASSETS_DIR / "cvcraft.ico"
        if ico_path.exists():
            self.setWindowIcon(QIcon(str(ico_path)))

        self.active_cv = active_cv
        self.current_tpl_id = initial_template_id
        self.zoom_factor = 0.95
        self.current_page_idx = 0
        self.rendered_pages: List[QPixmap] = []

        self._setup_ui()
        self._load_template(self.current_tpl_id)

    def _setup_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Left / Center Area: Document Viewer + Toolbar
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(16, 14, 16, 14)
        viewer_layout.setSpacing(10)

        # Viewer Toolbar: Zoom & Page navigation
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 4px 8px;
            }
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(6, 2, 6, 2)
        tb_layout.setSpacing(8)

        # Template switcher arrows in toolbar
        self.prev_tpl_btn = QPushButton("◀ Prev Template")
        self.prev_tpl_btn.setProperty("class", "GhostBtn")
        self.prev_tpl_btn.setFixedHeight(28)
        self.prev_tpl_btn.clicked.connect(self._goto_prev_template)
        tb_layout.addWidget(self.prev_tpl_btn)

        self.next_tpl_btn = QPushButton("Next Template ▶")
        self.next_tpl_btn.setProperty("class", "GhostBtn")
        self.next_tpl_btn.setFixedHeight(28)
        self.next_tpl_btn.clicked.connect(self._goto_next_template)
        tb_layout.addWidget(self.next_tpl_btn)

        tb_layout.addStretch()

        # Page controls
        self.prev_page_btn = QPushButton("◀")
        self.prev_page_btn.setFixedSize(28, 28)
        self.prev_page_btn.setProperty("class", "SecondaryBtn")
        self.prev_page_btn.clicked.connect(self._prev_page)
        tb_layout.addWidget(self.prev_page_btn)

        self.page_lbl = QLabel("Page 1 of 1")
        self.page_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; min-width: 75px; text-align: center;")
        self.page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.page_lbl)

        self.next_page_btn = QPushButton("▶")
        self.next_page_btn.setFixedSize(28, 28)
        self.next_page_btn.setProperty("class", "SecondaryBtn")
        self.next_page_btn.clicked.connect(self._next_page)
        tb_layout.addWidget(self.next_page_btn)

        tb_layout.addSpacing(12)

        # Zoom controls
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(28, 28)
        zoom_out_btn.setProperty("class", "SecondaryBtn")
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self._zoom_out)
        tb_layout.addWidget(zoom_out_btn)

        self.zoom_lbl = QLabel("95%")
        self.zoom_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; min-width: 40px; text-align: center;")
        self.zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.zoom_lbl)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(28, 28)
        zoom_in_btn.setProperty("class", "SecondaryBtn")
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self._zoom_in)
        tb_layout.addWidget(zoom_in_btn)

        viewer_layout.addWidget(toolbar)

        # Scroll Area with rendered document
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setStyleSheet("background-color: #090D16; border: none;")

        self.doc_label = QLabel()
        self.doc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doc_label.setStyleSheet("background-color: transparent;")
        self.scroll.setWidget(self.doc_label)

        viewer_layout.addWidget(self.scroll, stretch=1)
        root_layout.addWidget(viewer_container, stretch=1)

        # Right Sidebar: Template Info & Actions
        info_panel = QFrame()
        info_panel.setFixedWidth(300)
        info_panel.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-left: 1px solid #1E293B;
            }
        """)
        ip_layout = QVBoxLayout(info_panel)
        ip_layout.setContentsMargins(20, 20, 20, 20)
        ip_layout.setSpacing(14)

        # Top Badge
        self.badge_lbl = QLabel("FEATURED")
        self.badge_lbl.setStyleSheet("""
            background-color: #312E81;
            color: #C7D2FE;
            font-size: 10px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 6px;
        """)
        self.badge_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ip_layout.addWidget(self.badge_lbl)

        # Template Name
        self.tpl_name_lbl = QLabel("Classic Sidebar")
        self.tpl_name_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        self.tpl_name_lbl.setWordWrap(True)
        ip_layout.addWidget(self.tpl_name_lbl)

        # Description
        self.desc_lbl = QLabel("Description here")
        self.desc_lbl.setStyleSheet("font-size: 12px; color: #94A3B8; line-height: 1.4;")
        self.desc_lbl.setWordWrap(True)
        ip_layout.addWidget(self.desc_lbl)

        # Feature Highlights Box
        highlights_box = QFrame()
        highlights_box.setStyleSheet("""
            background-color: #1E293B;
            border-radius: 8px;
            padding: 10px;
        """)
        hl_layout = QVBoxLayout(highlights_box)
        hl_layout.setContentsMargins(10, 10, 10, 10)
        hl_layout.setSpacing(8)

        self.layout_type_lbl = QLabel("<b>Layout:</b> Two-Column Split")
        self.layout_type_lbl.setStyleSheet("font-size: 11.5px; color: #E2E8F0;")
        hl_layout.addWidget(self.layout_type_lbl)

        self.ats_score_lbl = QLabel("<b>ATS Compatibility:</b> 98% (High)")
        self.ats_score_lbl.setStyleSheet("font-size: 11.5px; color: #10B981;")
        hl_layout.addWidget(self.ats_score_lbl)

        self.best_for_lbl = QLabel("<b>Best for:</b> Software Engineers & Specialists")
        self.best_for_lbl.setStyleSheet("font-size: 11.5px; color: #818CF8;")
        self.best_for_lbl.setWordWrap(True)
        hl_layout.addWidget(self.best_for_lbl)

        ip_layout.addWidget(highlights_box)

        ip_layout.addStretch()

        # Action Buttons
        self.apply_btn = QPushButton("✓ Apply to Current CV")
        self.apply_btn.setProperty("class", "PrimaryBtn")
        self.apply_btn.setFixedHeight(40)
        self.apply_btn.clicked.connect(self._on_apply)
        ip_layout.addWidget(self.apply_btn)

        self.create_btn = QPushButton("+ Create New with This")
        self.create_btn.setProperty("class", "SecondaryBtn")
        self.create_btn.setFixedHeight(36)
        self.create_btn.clicked.connect(self._on_create)
        ip_layout.addWidget(self.create_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "GhostBtn")
        close_btn.setFixedHeight(32)
        close_btn.clicked.connect(self.accept)
        ip_layout.addWidget(close_btn)

        root_layout.addWidget(info_panel)

    def _load_template(self, template_id: str):
        self.current_tpl_id = template_id

        # Find template info from config
        tpl_info = next((t for t in TEMPLATES if t["id"] == template_id), TEMPLATES[0])
        from ui.views.templates_view import TEMPLATE_EXTRAS
        extras = TEMPLATE_EXTRAS.get(template_id, {"best_for": "General Professionals", "type": "Modern", "ats": "High"})

        self.tpl_name_lbl.setText(tpl_info["name"])
        self.desc_lbl.setText(tpl_info["description"])
        self.badge_lbl.setText(tpl_info["badge"].upper())
        self.layout_type_lbl.setText(f"<b>Layout:</b> {extras['type']}")
        self.ats_score_lbl.setText(f"<b>ATS Compatibility:</b> {extras['ats']}")
        self.best_for_lbl.setText(f"<b>Best for:</b> {extras['best_for']}")

        # Render preview using active CV if available, otherwise sample CV
        cv_to_render = None
        if self.active_cv:
            # Clone active CV so we don't modify the real one prematurely
            import copy
            cv_to_render = copy.deepcopy(self.active_cv)
            cv_to_render.template_id = template_id
        else:
            cv_to_render = CVService.create_sample_cv()
            cv_to_render.template_id = template_id
            # Provide sample photo if available
            sample_photo = ASSETS_DIR / "icon_256.png"
            if sample_photo.exists():
                cv_to_render.personal.profile_photo_path = str(sample_photo)

        try:
            pdf_bytes = PDFService.generate_pdf_bytes(cv_to_render)
            pil_images = PDFService.render_pdf_to_images(pdf_bytes, dpi=160)
            self.rendered_pages = []
            for img in pil_images:
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                pm = QPixmap()
                pm.loadFromData(buf.getvalue(), "PNG")
                self.rendered_pages.append(pm)

            self.current_page_idx = 0
            self._update_display()
        except Exception as e:
            self.doc_label.setText(f"Preview render error: {str(e)}")

    def _update_display(self):
        total = len(self.rendered_pages)
        if total == 0:
            self.doc_label.setText("No preview available")
            return

        if self.current_page_idx >= total:
            self.current_page_idx = total - 1

        self.page_lbl.setText(f"Page {self.current_page_idx + 1} of {total}")
        self.prev_page_btn.setEnabled(self.current_page_idx > 0)
        self.next_page_btn.setEnabled(self.current_page_idx < total - 1)

        pixmap = self.rendered_pages[self.current_page_idx]
        target_w = int(pixmap.width() * self.zoom_factor)
        target_h = int(pixmap.height() * self.zoom_factor)

        scaled = pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.doc_label.setPixmap(scaled)

    def _prev_page(self):
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self._update_display()

    def _next_page(self):
        if self.current_page_idx < len(self.rendered_pages) - 1:
            self.current_page_idx += 1
            self._update_display()

    def _zoom_in(self):
        if self.zoom_factor < 1.6:
            self.zoom_factor += 0.1
            self.zoom_lbl.setText(f"{int(self.zoom_factor * 100)}%")
            self._update_display()

    def _zoom_out(self):
        if self.zoom_factor > 0.4:
            self.zoom_factor -= 0.1
            self.zoom_lbl.setText(f"{int(self.zoom_factor * 100)}%")
            self._update_display()

    def _goto_prev_template(self):
        tpl_ids = [t["id"] for t in TEMPLATES]
        if self.current_tpl_id in tpl_ids:
            idx = tpl_ids.index(self.current_tpl_id)
            new_idx = (idx - 1) % len(tpl_ids)
            self._load_template(tpl_ids[new_idx])

    def _goto_next_template(self):
        tpl_ids = [t["id"] for t in TEMPLATES]
        if self.current_tpl_id in tpl_ids:
            idx = tpl_ids.index(self.current_tpl_id)
            new_idx = (idx + 1) % len(tpl_ids)
            self._load_template(tpl_ids[new_idx])

    def _on_apply(self):
        self.template_applied.emit(self.current_tpl_id)
        self.accept()

    def _on_create(self):
        self.create_requested.emit(self.current_tpl_id)
        self.accept()
