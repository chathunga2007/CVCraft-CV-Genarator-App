import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set offscreen platform for headless Qt verification
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from repositories.cv_repository import CVRepository
from services.cv_service import CVService

print("1. Initializing Qt Application (offscreen)...")
app = QApplication(sys.argv)

print("2. Instantiating MainWindow...")
win = MainWindow()
assert win is not None
print("   [OK] MainWindow created successfully")

print("3. Testing Load Demo CV flow...")
win.load_demo_cv()
assert win.workspace_view.cv is not None
assert win.workspace_view.cv.personal.full_name == "Alexander Mitchell"
print("   [OK] Demo CV loaded into workspace")

print("4. Testing Template Switching in Workspace...")
for tpl_id in ["minimal", "developer", "executive", "ats_friendly"]:
    win.workspace_view.cv.template_id = tplpl_id = tpl_id
    win.workspace_view.preview_widget.update_preview(win.workspace_view.cv, immediate=True)
print("   [OK] Workspace live preview updated for all templates")

print("5. Testing Theme Toggle...")
win._toggle_theme()
win._toggle_theme()
print("   [OK] Theme toggling verified")

print("6. Testing Navigation switching...")
for nav in ["dashboard", "my_cvs", "templates", "job_match", "settings", "about"]:
    win._on_nav_clicked(nav)
print("   [OK] All navigation routes verified")

print("\nALL GUI & WORKSPACE TESTS PASSED 100%!")
