"""
CVCraft Templates Showcase View
Displays the 8 professional templates with previews, badges, best-fit guidance,
and direct application buttons.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from config import TEMPLATES

TEMPLATE_EXTRAS = {
    "modern": {"best_for": "Software Engineers, Product Managers, Tech Specialists", "type": "Two-Column Split", "ats": "High"},
    "minimal": {"best_for": "Consultants, Designers, Architects, General Business", "type": "Clean Single-Column", "ats": "98%"},
    "executive": {"best_for": "Directors, VPs, Senior Executives, Dept Leads", "type": "Header Banner + Split", "ats": "Very High"},
    "professional": {"best_for": "Finance, Corporate, Operations, Legal, Banking", "type": "Structured Corporate 2-Col", "ats": "High"},
    "creative": {"best_for": "UI/UX Designers, Creative Directors, Media Specialists", "type": "Vibrant Color Accents", "ats": "Portfolio Focus"},
    "developer": {"best_for": "Full Stack, DevOps, Cloud Architects, Backend Engineers", "type": "Terminal Style + GitHub", "ats": "High"},
    "academic": {"best_for": "Researchers, Professors, Postdocs, Scientists", "type": "Formal Traditional Serif", "ats": "Universal"},
    "ats_friendly": {"best_for": "Large Enterprise Applications & Automated Job Portals", "type": "Zero Tables Linear OCR", "ats": "99.9% Best"}
}

class TemplatesView(QWidget):
    template_selected = pyqtSignal(str) # passes template_id
    create_with_template_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hdr_box = QVBoxLayout()
        title = QLabel("Architectural CV Templates")
        title.setProperty("class", "HeaderTitle")
        sub = QLabel("8 recruiter-tested layouts engineered for specific career milestones, visual impact, and automated ATS parsing.")
        sub.setProperty("class", "HeaderSubtitle")
        hdr_box.addWidget(title)
        hdr_box.addWidget(sub)
        layout.addLayout(hdr_box)

        # Scrollable Templates Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(20)

        cols = self._calc_cols()
        self._current_cols = cols
        for idx, tpl in enumerate(TEMPLATES):
            card = self._create_template_card(tpl)
            r = idx // cols
            c = idx % cols
            self.grid.addWidget(card, r, c)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

    def _calc_cols(self) -> int:
        w = self.width()
        if w >= 1100:
            return 3
        elif w >= 700:
            return 2
        else:
            return 1

    def _relayout_grid(self):
        cards = []
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                cards.append(w)
        cols = self._calc_cols()
        for idx, card in enumerate(cards):
            r = idx // cols
            c = idx % cols
            self.grid.addWidget(card, r, c)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_cols = self._calc_cols()
        if getattr(self, "_current_cols", 3) != new_cols:
            self._current_cols = new_cols
            self._relayout_grid()

    def _create_template_card(self, tpl: dict) -> QFrame:
        card = QFrame()
        card.setProperty("class", "Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 16, 18, 16)
        cl.setSpacing(10)

        extras = TEMPLATE_EXTRAS.get(tpl["id"], {"best_for": "All Professionals", "type": "Modern", "ats": "Standard"})

        # Banner graphic / color block
        banner = QFrame()
        banner.setFixedHeight(72)
        banner.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {tpl['preview_bg']}, stop:1 #1E1B4B);
            border-radius: 8px;
        """)
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(12, 10, 12, 10)
        
        type_lbl = QLabel(extras["type"])
        type_lbl.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px; font-weight: 600;")
        
        badge = QLabel(tpl["badge"])
        badge.setStyleSheet("background-color: rgba(255,255,255,0.25); color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 4px 8px; border-radius: 4px;")
        
        b_layout.addWidget(type_lbl, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        b_layout.addStretch()
        b_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        cl.addWidget(banner)

        # Title
        t_lbl = QLabel(tpl["name"])
        t_lbl.setProperty("class", "CardTitle")
        cl.addWidget(t_lbl)

        # Description
        d_lbl = QLabel(tpl["description"])
        d_lbl.setWordWrap(True)
        d_lbl.setProperty("class", "MutedText")
        d_lbl.setStyleSheet("min-height: 44px;")
        cl.addWidget(d_lbl)

        # Best For Box
        best_box = QHBoxLayout()
        best_box.setSpacing(4)
        bf_lbl = QLabel(f"<b>Best for:</b> {extras['best_for']}")
        bf_lbl.setWordWrap(True)
        bf_lbl.setStyleSheet("font-size: 11px; color: #818CF8;")
        best_box.addWidget(bf_lbl)
        cl.addLayout(best_box)

        cl.addSpacing(4)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)

        use_btn = QPushButton("Apply to Active CV")
        use_btn.setProperty("class", "PrimaryBtn")
        use_btn.clicked.connect(lambda _, tid=tpl["id"]: self.template_selected.emit(tid))
        btn_box.addWidget(use_btn)

        new_btn = QPushButton("+ New")
        new_btn.setProperty("class", "SecondaryBtn")
        new_btn.setToolTip("Create new CV with this template")
        new_btn.clicked.connect(lambda _, tid=tpl["id"]: self.create_with_template_requested.emit(tid))
        btn_box.addWidget(new_btn)

        cl.addLayout(btn_box)

        return card
