"""
CVCraft First-Launch Onboarding View
Welcomes user and provides fast zero-friction paths: Create New CV, Load Sample CV, Browse Templates.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from config import LOGO_PATH, APP_NAME

class OnboardingView(QWidget):
    create_cv_clicked = pyqtSignal()
    load_sample_clicked = pyqtSignal()
    explore_templates_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0F172A;")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(540, 480)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 32px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(16)

        # Logo
        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(logo_lbl)

        # Welcome Text
        w_title = QLabel(f"Welcome to {APP_NAME}")
        w_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        w_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(w_title)

        w_sub = QLabel("Create a standout, ATS-optimized professional CV in minutes.")
        w_sub.setStyleSheet("font-size: 13px; color: #94A3B8;")
        w_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(w_sub)

        card_layout.addSpacing(16)

        # Buttons
        create_btn = QPushButton("🚀 Create My First CV")
        create_btn.setFixedHeight(42)
        create_btn.setStyleSheet("""
            background-color: #4F46E5;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            border: none;
        """)
        create_btn.clicked.connect(self.create_cv_clicked.emit)
        card_layout.addWidget(create_btn)

        sample_btn = QPushButton("✨ Load Demo CV (Alex Mitchell)")
        sample_btn.setFixedHeight(40)
        sample_btn.setStyleSheet("""
            background-color: #312E81;
            color: #C7D2FE;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #4338CA;
        """)
        sample_btn.clicked.connect(self.load_sample_clicked.emit)
        card_layout.addWidget(sample_btn)

        tpl_btn = QPushButton("🎨 Explore Templates")
        tpl_btn.setFixedHeight(40)
        tpl_btn.setStyleSheet("""
            background-color: #0F172A;
            color: #E2E8F0;
            font-size: 13px;
            font-weight: 500;
            border-radius: 8px;
            border: 1px solid #334155;
        """)
        tpl_btn.clicked.connect(self.explore_templates_clicked.emit)
        card_layout.addWidget(tpl_btn)

        main_layout.addWidget(card)
