"""
CVCraft Toast Notification
Non-blocking modern toast banner for user feedback.
"""

from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

class Toast(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #4F46E5;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self.label = QLabel("")
        self.label.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.label)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        self.hide()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)

    def show_message(self, message: str, is_error: bool = False, duration_ms: int = 2500):
        if is_error:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4C0519;
                    border: 1px solid #F43F5E;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1E1B4B;
                    border: 1px solid #6366F1;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
            """)

        self.label.setText(message)
        self.adjustSize()
        
        # Position at bottom center of parent
        if self.parent():
            pw = self.parent().width()
            ph = self.parent().height()
            self.move((pw - self.width()) // 2, ph - self.height() - 32)
        
        self.show()
        self.raise_()

        # Fade in
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        self.timer.start(duration_ms)

    def _fade_out(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.hide)
        self.anim.start()
