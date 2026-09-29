"""
CVCraft Splash Screen
Polished startup screen with logo, tagline, and animated loading progress.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from config import LOGO_PATH, APP_NAME, APP_TAGLINE

class SplashView(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0F172A;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Logo
        logo_lbl = QLabel()
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaled(
                96, 96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_lbl)

        # App Name
        title_lbl = QLabel(APP_NAME)
        title_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # Tagline
        tagline_lbl = QLabel(APP_TAGLINE)
        tagline_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #818CF8; letter-spacing: 0.5px;")
        tagline_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline_lbl)

        layout.addSpacing(20)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedSize(280, 4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border-radius: 2px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #4F46E5;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status label
        self.status_lbl = QLabel("Initializing local database...")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)

        # Step animation timer
        self.step = 0
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._advance)
        self.timer.start()

    def _advance(self):
        self.step += 4
        self.progress.setValue(self.step)
        if self.step == 30:
            self.status_lbl.setText("Loading typography & 8 templates...")
        elif self.step == 70:
            self.status_lbl.setText("Syncing offline storage...")
        elif self.step >= 100:
            self.timer.stop()
            self.status_lbl.setText("Ready.")
            QTimer.singleShot(150, self.finished.emit)
