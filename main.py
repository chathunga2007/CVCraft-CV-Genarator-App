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

import traceback
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from config import APP_NAME, APP_VERSION, ASSETS_DIR, LOGS_DIR
from ui.main_window import MainWindow
from ui.views.splash_view import SplashView

def setup_exception_handling():
    """Captures unhandled exceptions, writes to disk, and prevents silent crash."""
    crash_log_file = LOGS_DIR / "crash.log"

    def excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        try:
            with open(crash_log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().isoformat()}] CRITICAL APPLICATION ERROR:\n{err_msg}\n")
        except Exception:
            pass

        # Attempt to show a user-visible message box if Qt event loop is active
        app = QApplication.instance()
        if app:
            try:
                QMessageBox.critical(
                    None,
                    "CVCraft — Error Detected",
                    f"An unexpected error occurred:\n\n{str(exc_value)}\n\nDetailed crash details have been saved to:\n{crash_log_file}"
                )
            except Exception:
                pass

    sys.excepthook = excepthook

def get_app_icon() -> QIcon:
    ico_p = ASSETS_DIR / "cvcraft.ico"
    if ico_p.exists():
        return QIcon(str(ico_p.resolve()))
    logo_p = ASSETS_DIR / "CVCraft-logo.png"
    if logo_p.exists():
        return QIcon(str(logo_p.resolve()))
    return QIcon()

def main():
    setup_exception_handling()

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
