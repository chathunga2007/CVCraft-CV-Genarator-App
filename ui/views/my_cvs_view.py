"""
CVCraft My CVs Management View
Full document inventory with search, sorting, filtering, and version management.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QScrollArea, QGridLayout, QFrame, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, List

from ui.components.cv_card import CVCard
from repositories.cv_repository import CVRepository

class MyCVsView(QWidget):
    edit_cv_requested = pyqtSignal(str)
    export_cv_requested = pyqtSignal(str)
    duplicate_cv_requested = pyqtSignal(str)
    create_cv_requested = pyqtSignal()
    version_cv_requested = pyqtSignal(str)

    def __init__(self, cv_repo: CVRepository, parent=None):
        super().__init__(parent)
        self.repo = cv_repo
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header Row
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("My CVs & Resumes")
        title.setProperty("class", "HeaderTitle")
        sub = QLabel("Manage your career documents, job-specific versions, and exports.")
        sub.setProperty("class", "HeaderSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        header.addLayout(title_box)
        header.addStretch()

        create_btn = QPushButton("+ New CV")
        create_btn.setFixedHeight(38)
        create_btn.setProperty("class", "PrimaryBtn")
        create_btn.clicked.connect(self.create_cv_requested.emit)
        header.addWidget(create_btn)
        layout.addLayout(header)

        # Filter & Search Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by CV name or target role...")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.refresh)
        filter_bar.addWidget(self.search_input, stretch=2)

        self.sort_combo = QComboBox()
        self.sort_combo.setFixedHeight(38)
        self.sort_combo.addItem("Sort: Recently Modified", "updated_at")
        self.sort_combo.addItem("Sort: Alphabetical (A-Z)", "name")
        self.sort_combo.addItem("Sort: Completion %", "completion_pct")
        self.sort_combo.currentIndexChanged.connect(self.refresh)
        filter_bar.addWidget(self.sort_combo, stretch=1)

        layout.addLayout(filter_bar)

        # Scroll Area for CV Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(16)
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

    def refresh(self):
        # Clear existing
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search_query = self.search_input.text().strip()
        sort_by = self.sort_combo.currentData() or "updated_at"
        desc = (sort_by != "name")

        cvs = self.repo.list_all(search=search_query, sort_by=sort_by, desc=desc)

        if not cvs:
            empty_frame = QFrame()
            empty_frame.setProperty("class", "Card")
            el = QVBoxLayout(empty_frame)
            el.setContentsMargins(48, 48, 48, 48)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.setSpacing(12)
            
            lbl1 = QLabel("No CVs found" if search_query else "No CVs yet")
            lbl1.setProperty("class", "SectionHeader")
            lbl2 = QLabel("Try a different search term or click '+ New CV' to create one.")
            lbl2.setProperty("class", "HeaderSubtitle")
            el.addWidget(lbl1, alignment=Qt.AlignmentFlag.AlignCenter)
            el.addWidget(lbl2, alignment=Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(empty_frame, 0, 0, 1, self._calc_cols())
            return

        cols = self._calc_cols()
        self._current_cols = cols
        for idx, c in enumerate(cvs):
            card = CVCard(c)
            card.edit_requested.connect(self.edit_cv_requested.emit)
            card.export_requested.connect(self.export_cv_requested.emit)
            card.duplicate_requested.connect(self.duplicate_cv_requested.emit)
            card.delete_requested.connect(self._confirm_delete)
            card.version_requested.connect(self.version_cv_requested.emit)
            r = idx // cols
            col = idx % cols
            self.grid.addWidget(card, r, col)

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

    def _confirm_delete(self, cv_id: str):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to permanently delete this CV?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.repo.delete(cv_id)
            self.refresh()

