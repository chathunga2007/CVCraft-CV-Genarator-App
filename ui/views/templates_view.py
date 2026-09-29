"""
CVCraft Templates Showcase View
Displays the 8 professional templates with previews, badges, and layout descriptions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from config import TEMPLATES

class TemplatesView(QWidget):
    template_selected = pyqtSignal(str) # passes template_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hdr_box = QVBoxLayout()
        title = QLabel("Professional CV Templates")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        sub = QLabel("8 distinct architectural layouts engineered for recruiters, hiring managers, and ATS parsers.")
        sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
        hdr_box.addWidget(title)
        hdr_box.addWidget(sub)
        layout.addLayout(hdr_box)

        # Scrollable Templates Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(20)

        cols = 3
        for idx, tpl in enumerate(TEMPLATES):
            card = self._create_template_card(tpl)
            r = idx // cols
            c = idx % cols
            grid.addWidget(card, r, c)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

    def _create_template_card(self, tpl: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #6366F1;
                background-color: #232F42;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setSpacing(12)

        # Banner graphic / color block
        banner = QFrame()
        banner.setFixedHeight(70)
        banner.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {tpl['preview_bg']}, stop:1 #0F172A);
            border-radius: 8px;
        """)
        b_layout = QHBoxLayout(banner)
        badge = QLabel(tpl["badge"])
        badge.setStyleSheet("background-color: rgba(255,255,255,0.2); color: #FFFFFF; font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px;")
        b_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        cl.addWidget(banner)

        # Title
        t_lbl = QLabel(tpl["name"])
        t_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        cl.addWidget(t_lbl)

        # Description
        d_lbl = QLabel(tpl["description"])
        d_lbl.setWordWrap(True)
        d_lbl.setStyleSheet("font-size: 12px; color: #94A3B8; min-height: 48px;")
        cl.addWidget(d_lbl)

        # Apply Button
        btn = QPushButton(f"Use {tpl['name']}")
        btn.setStyleSheet("""
            background-color: #4F46E5;
            color: #FFFFFF;
            font-weight: 600;
            padding: 8px;
            border-radius: 6px;
            border: none;
        """)
        btn.clicked.connect(lambda _, tid=tpl["id"]: self.template_selected.emit(tid))
        cl.addWidget(btn)

        return card
