"""
CVCraft Logo Widget
Displays the CVCraft brand identity: icon, typography, and tagline.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from config import LOGO_PATH, APP_NAME, APP_TAGLINE

class LogoWidget(QWidget):
    def __init__(self, compact: bool = False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 4, 4, 4)
        layout.setSpacing(10)

        icon_label = QLabel()
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaled(
                36 if compact else 42,
                36 if compact else 42,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pix)
        else:
            icon_label.setText("⚡")
            icon_label.setStyleSheet("font-size: 24px; color: #4F46E5;")
        layout.addWidget(icon_label)

        if not compact:
            text_container = QWidget()
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)

            title_label = QLabel(APP_NAME)
            title_label.setProperty("class", "LogoTitle")

            tagline_label = QLabel(APP_TAGLINE)
            tagline_label.setProperty("class", "LogoTagline")
            tagline_label.setWordWrap(False)

            text_layout.addWidget(title_label)
            text_layout.addWidget(tagline_label)
            layout.addWidget(text_container)

        layout.addStretch()
