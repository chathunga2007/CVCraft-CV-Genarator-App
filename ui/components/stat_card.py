"""
CVCraft Stat Card Component
Modern statistics card inheriting from the active theme (Dark & Light).
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon_symbol: str, accent_color: str = "#4F46E5", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("class", "StatCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Top row: Title + Icon Badge
        top_row = QHBoxLayout()
        title_lbl = QLabel(title.upper())
        title_lbl.setProperty("class", "StatLabel")
        
        icon_badge = QLabel(icon_symbol)
        icon_badge.setStyleSheet(f"""
            background-color: {accent_color}22;
            color: {accent_color};
            font-size: 14px;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 6px;
        """)
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(icon_badge)
        layout.addLayout(top_row)

        # Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setProperty("class", "StatValue")
        layout.addWidget(self.val_lbl)

        # Subtitle
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setProperty("class", "MutedText")
            layout.addWidget(sub_lbl)

    def set_value(self, value: str):
        self.val_lbl.setText(value)
