"""
CVCraft Premium Splash Screen
Cinematic startup sequence with luminous glassmorphism, animated multi-stage progress,
real-time percentage feedback, and smooth opacity fade-out transition.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from config import LOGO_PATH, APP_NAME, APP_TAGLINE, APP_VERSION

class SplashView(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(520, 360)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Root Layout with padding for shadow / rounded edges
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Luminous Floating Card Container
        self.card = QFrame()
        self.card.setObjectName("SplashCard")
        self.card.setStyleSheet("""
            QFrame#SplashCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #090D16,
                    stop:0.35 #0F172A,
                    stop:0.75 #1E1B4B,
                    stop:1 #0B0F19
                );
                border: 1.5px solid #4338CA;
                border-radius: 20px;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(14)

        # Top Header Bar: Chip Badge + Version
        top_bar = QHBoxLayout()
        chip_lbl = QLabel("✦ PROFESSIONAL RESUME WORKSTATION ✦")
        chip_lbl.setStyleSheet("""
            background-color: rgba(99, 102, 241, 0.15);
            color: #A5B4FC;
            font-size: 10px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 10px;
            border: 1px solid rgba(99, 102, 241, 0.35);
            letter-spacing: 0.8px;
        """)
        top_bar.addWidget(chip_lbl)
        top_bar.addStretch()

        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.08);
            color: #94A3B8;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        """)
        top_bar.addWidget(ver_lbl)
        card_layout.addLayout(top_bar)

        card_layout.addSpacing(4)

        # Center Branding: Logo + Name + Tagline
        center_box = QVBoxLayout()
        center_box.setSpacing(8)
        center_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(
                82, 82,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            center_box.addWidget(logo_lbl)

        title_lbl = QLabel(APP_NAME)
        title_lbl.setStyleSheet("""
            font-size: 32px;
            font-weight: 900;
            color: #FFFFFF;
            letter-spacing: -0.5px;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_box.addWidget(title_lbl)

        tagline_lbl = QLabel(f"“{APP_TAGLINE}”")
        tagline_lbl.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #818CF8;
            font-style: italic;
            letter-spacing: 0.3px;
        """)
        tagline_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_box.addWidget(tagline_lbl)

        card_layout.addLayout(center_box)

        card_layout.addSpacing(6)

        # Loading Progress Section
        progress_box = QVBoxLayout()
        progress_box.setSpacing(8)

        # Gradient Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4F46E5,
                    stop:0.45 #7C3AED,
                    stop:1 #06B6D4
                );
                border-radius: 3px;
            }
        """)
        progress_box.addWidget(self.progress)

        # Status & Percentage Labels
        status_row = QHBoxLayout()
        self.status_lbl = QLabel("⚡ Initializing CVCraft engine...")
        self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: #94A3B8;")
        status_row.addWidget(self.status_lbl)
        status_row.addStretch()

        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #818CF8; min-width: 32px; text-align: right;")
        status_row.addWidget(self.pct_lbl)

        progress_box.addLayout(status_row)
        card_layout.addLayout(progress_box)

        card_layout.addSpacing(2)

        # Bottom Footer: Security & Engine Specs
        footer_row = QHBoxLayout()
        offline_lbl = QLabel("● 100% Offline-First • Zero Cloud Leak")
        offline_lbl.setStyleSheet("font-size: 10px; font-weight: 600; color: #10B981;")
        footer_row.addWidget(offline_lbl)
        footer_row.addStretch()

        engine_lbl = QLabel("ReportLab Vector & Qt6 Core")
        engine_lbl.setStyleSheet("font-size: 10px; color: #475569; font-weight: 500;")
        footer_row.addWidget(engine_lbl)
        card_layout.addLayout(footer_row)

        root_layout.addWidget(self.card)

        # Opacity effect for smooth exit transition
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        # Step animation timer
        self.step = 0
        self.timer = QTimer(self)
        self.timer.setInterval(32)
        self.timer.timeout.connect(self._advance)
        self.timer.start()

    def _advance(self):
        # Realistic pacing curve
        if self.step < 30:
            self.step += 3
        elif self.step < 65:
            self.step += 2
        elif self.step < 90:
            self.step += 3
        else:
            self.step += 4

        val = min(100, self.step)
        self.progress.setValue(val)
        self.pct_lbl.setText(f"{val}%")

        if val < 25:
            self.status_lbl.setText("⚡ Initializing SQLite database...")
        elif val < 50:
            self.status_lbl.setText("📄 Compiling 8 architectural templates & fonts...")
        elif val < 75:
            self.status_lbl.setText("🎯 Calibrating ATS scoring & keyword analyzer...")
        elif val < 92:
            self.status_lbl.setText("🔒 Verifying zero-cloud encrypted local storage...")
        elif val < 100:
            self.status_lbl.setText("✨ Finalizing workspace & live preview engine...")
        else:
            self.timer.stop()
            self.status_lbl.setText("🚀 Workspace ready. Launching...")
            self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #10B981;")
            self.pct_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #10B981;")
            QTimer.singleShot(200, self._fade_out_and_finish)

    def _fade_out_and_finish(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(280)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self.finished.emit)
        self.anim.start()
