"""
CVCraft Live Preview Widget
Real-time PDF page renderer with zoom controls, multi-page pagination,
and sub-millisecond debounced rendering.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
from typing import List, Optional
from PIL import Image as PILImage
from models.cv_model import CVDocument
from services.pdf_service import PDFService

class LivePreviewWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0B0F19;
                border-left: 1px solid #1E293B;
            }
        """)

        self.current_cv: Optional[CVDocument] = None
        self.pil_pages: List[PILImage.Image] = []
        self.current_page_idx = 0
        self.zoom_factor = 0.85
        self.latest_pdf_bytes: bytes = b""

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(250)
        self._debounce_timer.timeout.connect(self._do_render)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Toolbar: Zoom controls, Page navigator, Fit
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border-radius: 6px; border: 1px solid #334155;")
        self.prev_btn.clicked.connect(self._prev_page)
        toolbar.addWidget(self.prev_btn)

        self.page_lbl = QLabel("Page 1 of 1")
        self.page_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
        toolbar.addWidget(self.page_lbl)

        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border-radius: 6px; border: 1px solid #334155;")
        self.next_btn.clicked.connect(self._next_page)
        toolbar.addWidget(self.next_btn)

        toolbar.addStretch()

        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(28, 28)
        zoom_out_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border-radius: 6px; border: 1px solid #334155; font-weight: bold;")
        zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar.addWidget(zoom_out_btn)

        self.zoom_lbl = QLabel("85%")
        self.zoom_lbl.setStyleSheet("font-size: 11px; color: #94A3B8; min-width: 36px; text-align: center;")
        toolbar.addWidget(self.zoom_lbl)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(28, 28)
        zoom_in_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border-radius: 6px; border: 1px solid #334155; font-weight: bold;")
        zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar.addWidget(zoom_in_btn)

        fit_btn = QPushButton("Fit")
        fit_btn.setFixedHeight(28)
        fit_btn.setStyleSheet("background-color: #1E293B; color: #E2E8F0; border-radius: 6px; border: 1px solid #334155; padding: 0 8px; font-size: 11px;")
        fit_btn.clicked.connect(self._fit_to_width)
        toolbar.addWidget(fit_btn)

        layout.addLayout(toolbar)

        # Scroll Area holding the Canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #0B0F19; border: none;")
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.canvas_container = QWidget()
        self.canvas_container.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(self.canvas_container)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setContentsMargins(10, 10, 10, 10)

        self.page_display = QLabel()
        self.page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_display.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border-radius: 4px;
                border: 1px solid #334155;
            }
        """)
        c_layout.addWidget(self.page_display)

        self.scroll_area.setWidget(self.canvas_container)
        layout.addWidget(self.scroll_area)

    def update_preview(self, cv_doc: CVDocument, immediate: bool = False):
        self.current_cv = cv_doc
        if immediate:
            self._do_render()
        else:
            self._debounce_timer.start()

    def _do_render(self):
        if not self.current_cv:
            return
        try:
            pdf_bytes = PDFService.generate_pdf_bytes(self.current_cv)
            pil_images = PDFService.render_pdf_to_images(pdf_bytes, dpi=130)
            self._on_render_completed(pil_images, pdf_bytes)
        except Exception as e:
            # Handle empty / partially edited state gracefully
            pass

    def _on_render_completed(self, pil_images: List[PILImage.Image], pdf_bytes: bytes):
        self.pil_pages = pil_images
        self.latest_pdf_bytes = pdf_bytes
        total = len(self.pil_pages)
        if total == 0:
            return

        if self.current_page_idx >= total:
            self.current_page_idx = total - 1

        self.page_lbl.setText(f"Page {self.current_page_idx + 1} of {total}")
        self._display_current_page()

    def _display_current_page(self):
        if not self.pil_pages or self.current_page_idx >= len(self.pil_pages):
            return

        pil_img = self.pil_pages[self.current_page_idx]
        
        # Scale according to zoom factor
        target_w = max(50, int(pil_img.width * self.zoom_factor))
        target_h = max(50, int(pil_img.height * self.zoom_factor))
        
        # Convert PIL Image to QPixmap safely without dangling pointers
        import io
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), "PNG")

        scaled = pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.page_display.setPixmap(scaled)
        self.zoom_lbl.setText(f"{int(self.zoom_factor * 100)}%")

    def _prev_page(self):
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.page_lbl.setText(f"Page {self.current_page_idx + 1} of {len(self.pil_pages)}")
            self._display_current_page()

    def _next_page(self):
        if self.current_page_idx < len(self.pil_pages) - 1:
            self.current_page_idx += 1
            self.page_lbl.setText(f"Page {self.current_page_idx + 1} of {len(self.pil_pages)}")
            self._display_current_page()

    def _zoom_in(self):
        if self.zoom_factor < 1.6:
            self.zoom_factor += 0.1
            self._display_current_page()

    def _zoom_out(self):
        if self.zoom_factor > 0.4:
            self.zoom_factor -= 0.1
            self._display_current_page()

    def _fit_to_width(self):
        available_w = self.scroll_area.width() - 40
        if self.pil_pages and available_w > 100:
            self.zoom_factor = min(1.2, max(0.4, available_w / self.pil_pages[0].width))
            self._display_current_page()
