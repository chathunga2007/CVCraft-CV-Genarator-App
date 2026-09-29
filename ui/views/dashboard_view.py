"""
CVCraft Dashboard View
Executive overview featuring statistics, quick actions, completion analysis, and recent CV cards.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any

from ui.components.stat_card import StatCard
from ui.components.cv_card import CVCard
from repositories.cv_repository import CVRepository

class DashboardView(QWidget):
    create_cv_requested = pyqtSignal()
    import_cv_requested = pyqtSignal()
    templates_requested = pyqtSignal()
    load_demo_requested = pyqtSignal()
    edit_cv_requested = pyqtSignal(str)
    export_cv_requested = pyqtSignal(str)
    duplicate_cv_requested = pyqtSignal(str)
    delete_cv_requested = pyqtSignal(str)
    version_cv_requested = pyqtSignal(str)

    def __init__(self, cv_repo: CVRepository, parent=None):
        super().__init__(parent)
        self.repo = cv_repo
        self.setProperty("class", "MainContent")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        # Header: Greeting & Subtitle
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        greeting = QLabel("Good to see you.")
        greeting.setProperty("class", "HeaderTitle")
        
        sub = QLabel("Build your next opportunity with CVCraft.")
        sub.setProperty("class", "HeaderSubtitle")
        
        title_box.addWidget(greeting)
        title_box.addWidget(sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Quick Actions in Header
        create_btn = QPushButton("+ Create New CV")
        create_btn.setFixedHeight(38)
        create_btn.setProperty("class", "PrimaryBtn")
        create_btn.clicked.connect(self.create_cv_requested.emit)
        header_layout.addWidget(create_btn)

        import_btn = QPushButton("📥 Import CV")
        import_btn.setFixedHeight(38)
        import_btn.setProperty("class", "SecondaryBtn")
        import_btn.clicked.connect(self.import_cv_requested.emit)
        header_layout.addWidget(import_btn)

        main_layout.addLayout(header_layout)

        # Scrollable Body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(24)

        # Statistics Cards Grid
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        
        self.stat_total = StatCard("Total CVs", "0", "📄", "#4F46E5", "All active documents")
        self.stat_drafts = StatCard("Draft CVs", "0", "✏️", "#F59E0B", "In-progress revisions")
        self.stat_completed = StatCard("Completed CVs", "0", "✅", "#10B981", "85%+ ready to submit")
        self.stat_exports = StatCard("Last Export", "Never", "🚀", "#8B5CF6", "Ready for submission")

        self.stats_layout.addWidget(self.stat_total)
        self.stats_layout.addWidget(self.stat_drafts)
        self.stats_layout.addWidget(self.stat_completed)
        self.stats_layout.addWidget(self.stat_exports)
        self.content_layout.addLayout(self.stats_layout)

        # CV Completion Summary Banner Card
        self.completion_banner = QFrame()
        self.completion_banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E1B4B, stop:1 #1E293B);
                border: 1px solid #4338CA;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        cb_layout = QHBoxLayout(self.completion_banner)
        cb_layout.setContentsMargins(16, 12, 16, 12)
        
        cb_info = QVBoxLayout()
        cb_title = QLabel("Overall Profile Readiness")
        cb_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        self.cb_desc = QLabel("Add metrics to experience and customize templates to reach 100% job readiness.")
        self.cb_desc.setStyleSheet("font-size: 12px; color: #C7D2FE;")
        cb_info.addWidget(cb_title)
        cb_info.addWidget(self.cb_desc)
        cb_layout.addLayout(cb_info)
        cb_layout.addStretch()

        self.cb_pct_lbl = QLabel("86%")
        self.cb_pct_lbl.setStyleSheet("font-size: 26px; font-weight: 800; color: #10B981;")
        cb_layout.addWidget(self.cb_pct_lbl)

        self.content_layout.addWidget(self.completion_banner)

        # Recent CVs Header
        sec_header = QHBoxLayout()
        rec_lbl = QLabel("Recent CVs")
        rec_lbl.setProperty("class", "SectionHeader")
        sec_header.addWidget(rec_lbl)
        sec_header.addStretch()

        demo_btn = QPushButton("✨ Load Demo CV")
        demo_btn.setProperty("class", "GhostBtn")
        demo_btn.clicked.connect(self.load_demo_requested.emit)
        sec_header.addWidget(demo_btn)
        self.content_layout.addLayout(sec_header)

        # Recent CVs Container (Grid)
        self.cv_grid_container = QWidget()
        self.cv_grid = QGridLayout(self.cv_grid_container)
        self.cv_grid.setContentsMargins(0, 0, 0, 0)
        self.cv_grid.setSpacing(16)
        self.content_layout.addWidget(self.cv_grid_container)

        self.content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def refresh(self):
        stats = self.repo.get_stats()
        self.stat_total.set_value(str(stats["total_cvs"]))
        self.stat_drafts.set_value(str(stats["draft_cvs"]))
        self.stat_completed.set_value(str(stats["completed_cvs"]))
        
        last_exp = stats["last_export"]
        if last_exp:
            exp_date = last_exp.get("exported_at", "")[:10]
            self.stat_exports.set_value(exp_date)
        else:
            self.stat_exports.set_value("None yet")

        # Clear existing grid
        while self.cv_grid.count():
            item = self.cv_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cvs = self.repo.list_all(sort_by="updated_at", desc=True)[:6]

        if not cvs:
            empty_card = QFrame()
            empty_card.setProperty("class", "Card")
            el = QVBoxLayout(empty_card)
            el.setContentsMargins(32, 32, 32, 32)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.setSpacing(12)
            
            lbl1 = QLabel("No CVs created yet")
            lbl1.setProperty("class", "SectionHeader")
            lbl2 = QLabel("Start from scratch or load a realistic sample developer CV.")
            lbl2.setProperty("class", "HeaderSubtitle")
            
            btn_box = QHBoxLayout()
            b1 = QPushButton("Create My First CV")
            b1.setProperty("class", "PrimaryBtn")
            b1.clicked.connect(self.create_cv_requested.emit)
            
            b2 = QPushButton("Load Demo CV")
            b2.setProperty("class", "SecondaryBtn")
            b2.clicked.connect(self.load_demo_requested.emit)
            btn_box.addWidget(b1)
            btn_box.addWidget(b2)

            el.addWidget(lbl1, alignment=Qt.AlignmentFlag.AlignCenter)
            el.addWidget(lbl2, alignment=Qt.AlignmentFlag.AlignCenter)
            el.addLayout(btn_box)
            cols = self._calc_cols()
            self.cv_grid.addWidget(empty_card, 0, 0, 1, cols)
            self.cb_pct_lbl.setText("0%")
        else:
            avg_comp = int(sum(c.get("completion_pct", 0) for c in cvs) / len(cvs))
            self.cb_pct_lbl.setText(f"{avg_comp}%")

            cols = self._calc_cols()
            self._current_cols = cols
            for idx, c in enumerate(cvs):
                card = CVCard(c)
                card.edit_requested.connect(self.edit_cv_requested.emit)
                card.export_requested.connect(self.export_cv_requested.emit)
                card.duplicate_requested.connect(self.duplicate_cv_requested.emit)
                card.delete_requested.connect(self.delete_cv_requested.emit)
                card.version_requested.connect(self.version_cv_requested.emit)
                r = idx // cols
                col = idx % cols
                self.cv_grid.addWidget(card, r, col)

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
        while self.cv_grid.count():
            item = self.cv_grid.takeAt(0)
            w = item.widget()
            if w:
                cards.append(w)
        cols = self._calc_cols()
        for idx, card in enumerate(cards):
            r = idx // cols
            c = idx % cols
            self.cv_grid.addWidget(card, r, c)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_cols = self._calc_cols()
        if getattr(self, "_current_cols", 3) != new_cols:
            self._current_cols = new_cols
            self._relayout_grid()

