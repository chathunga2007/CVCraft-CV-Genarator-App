"""
CVCraft About View
Brand identity, architectural highlights, license, and developer information.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from config import LOGO_PATH, APP_NAME, APP_TAGLINE, APP_VERSION, APP_DEVELOPER, APP_LICENSE

class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "MainContent")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(560, 480)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 32px;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.setSpacing(14)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(logo_lbl)

        t_lbl = QLabel(APP_NAME)
        t_lbl.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFFFFF;")
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(t_lbl)

        tag_lbl = QLabel(f"“{APP_TAGLINE}”")
        tag_lbl.setStyleSheet("font-size: 14px; font-weight: 500; color: #818CF8; font-style: italic;")
        tag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(tag_lbl)

        cl.addSpacing(10)

        info_box = QVBoxLayout()
        info_box.setSpacing(6)
        
        def add_info_row(k, v):
            row = QHBoxLayout()
            kl = QLabel(k)
            kl.setStyleSheet("font-size: 12px; font-weight: 600; color: #94A3B8;")
            vl = QLabel(v)
            vl.setStyleSheet("font-size: 12px; color: #F8FAFC;")
            row.addWidget(kl)
            row.addStretch()
            row.addWidget(vl)
            info_box.addLayout(row)

        add_info_row("Version:", f"v{APP_VERSION} (Production Build)")
        add_info_row("Architecture:", "Python 3.13 + PyQt6 + SQLite3")
        add_info_row("PDF Vector Engine:", "ReportLab Multi-Page + PyMuPDF Preview")
        add_info_row("Data Privacy:", "100% Offline-First / Zero Telemetry")
        add_info_row("License:", APP_LICENSE)
        add_info_row("Platform:", "Cross-Platform Desktop (Windows / macOS / Linux)")

        cl.addLayout(info_box)

        cl.addSpacing(12)
        ft = QLabel("Crafted for ambitious professionals who want to stand out.")
        ft.setStyleSheet("font-size: 11px; color: #64748B;")
        ft.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(ft)

        layout.addWidget(card)
