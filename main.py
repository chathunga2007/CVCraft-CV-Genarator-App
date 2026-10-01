"""
CVCraft Application Entry Point
Product: CVCraft — "Build. Craft. Get Noticed."
"""

import sys
import os
import ctypes

# 1. Windows Taskbar AppUserModelID Integration (MUST execute before any PyQt6 or COM imports!)
if sys.platform == "win32":
    try:
        from ctypes import wintypes
        shell32 = ctypes.windll.shell32
        shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = [wintypes.LPCWSTR]
        shell32.SetCurrentProcessExplicitAppUserModelID.restype = ctypes.c_long
        shell32.SetCurrentProcessExplicitAppUserModelID("CVCraft.ProfessionalResumeBuilder.App.1.0")
    except Exception:
        pass
    try:
        import threading
        from register_app import register_shortcuts_and_app_id
        threading.Thread(target=register_shortcuts_and_app_id, daemon=True).start()
    except Exception:
        pass

from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from config import APP_NAME, APP_VERSION, ASSETS_DIR
from ui.main_window import MainWindow
from ui.views.splash_view import SplashView

def get_app_icon() -> QIcon:
    ico_p = ASSETS_DIR / "cvcraft.ico"
    if ico_p.exists():
        return QIcon(str(ico_p.resolve()))
    logo_p = ASSETS_DIR / "CVCraft-logo.png"
    if logo_p.exists():
        return QIcon(str(logo_p.resolve()))
    return QIcon()

def main():
    # 2. Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("CVCraft")

    # Set Multi-resolution Window and Desktop Icon
    app_icon = get_app_icon()
    app.setWindowIcon(app_icon)

    # Set refined font with standard point size directly
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # 3. Splash Screen Startup Flow
    splash = SplashView()
    splash.setWindowIcon(app_icon)
    screen = app.primaryScreen()
    if screen:
        screen_geom = screen.geometry()
        splash.move(
            (screen_geom.width() - splash.width()) // 2,
            (screen_geom.height() - splash.height()) // 2
        )
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
