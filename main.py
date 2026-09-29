"""
CVCraft Application Entry Point
Product: CVCraft — "Build. Craft. Get Noticed."
"""

import sys
import os
import ctypes
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from config import APP_NAME, APP_VERSION, ASSETS_DIR
from ui.main_window import MainWindow
from ui.views.splash_view import SplashView

def main():
    # 1. Windows Taskbar Icon Integration
    if sys.platform == "win32":
        try:
            myappid = "cvcraft.professional.resumebuilder.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # 2. Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("CVCraft")

    # Set Window and Desktop Icon
    ico_path = ASSETS_DIR / "cvcraft.ico"
    if ico_path.exists():
        app.setWindowIcon(QIcon(str(ico_path)))

    # Set refined font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # 3. Splash Screen Startup Flow
    splash = SplashView()
    splash.resize(460, 320)
    splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    main_win = None

    def launch_main_window():
        nonlocal main_win
        main_win = MainWindow()
        main_win.show()
        splash.close()

    splash.finished.connect(launch_main_window)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
