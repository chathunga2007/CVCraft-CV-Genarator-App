"""
CVCraft Design System & Theme Engine
Supports Dark and Light modes with Deep Indigo & Royal Purple visual identity.
All widgets inherit theme tokens cleanly without hardcoded overriding styles.
"""

DARK_THEME = """
/* Base Window & Global */
QMainWindow, QWidget#MainContent, QStackedWidget#MainContent {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget#Sidebar {
    background-color: #0B0F19;
    border-right: 1px solid #1E293B;
}

QFrame#WorkspaceSidebar {
    background-color: #0B0F19;
    border-right: 1px solid #1E293B;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sidebar Nav Buttons */
QPushButton.NavBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-weight: 500;
    font-size: 13px;
}

QPushButton.NavBtn:hover {
    background-color: #1E293B;
    color: #FFFFFF;
}

QPushButton.NavBtn:checked, QPushButton.NavBtn[active="true"] {
    background-color: #4F46E5;
    color: #FFFFFF;
    font-weight: 600;
}

/* Primary, Secondary, Ghost, Danger Buttons */
QPushButton.PrimaryBtn {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryBtn:hover {
    background-color: #4338CA;
}

QPushButton.PrimaryBtn:pressed {
    background-color: #3730A3;
}

QPushButton.SecondaryBtn {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton.SecondaryBtn:hover {
    background-color: #27354A;
    border-color: #475569;
    color: #FFFFFF;
}

QPushButton.GhostBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}

QPushButton.GhostBtn:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}

QPushButton.DangerBtn {
    background-color: #BE123C;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}

QPushButton.DangerBtn:hover {
    background-color: #9F1239;
}

/* Cards & Containers */
QFrame.Card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame.Card:hover {
    border-color: #6366F1;
}

QFrame.StatCard {
    background-color: #162032;
    border: 1px solid #27354A;
    border-radius: 12px;
}

QFrame.StatCard:hover {
    border-color: #4F46E5;
}

QFrame.ItemCard {
    background-color: #162032;
    border: 1px solid #27354A;
    border-radius: 10px;
    padding: 10px;
}

QFrame.ItemCard:hover {
    border-color: #384860;
}

QFrame.TopBar {
    background-color: #0B0F19;
    border-bottom: 1px solid #1E293B;
}

/* Live Preview Area */
QFrame.PreviewArea {
    background-color: #0B0F19;
    border-left: 1px solid #1E293B;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #4F46E5;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1.5px solid #6366F1;
    background-color: #131D31;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F8FAFC;
    selection-background-color: #4F46E5;
    border: 1px solid #334155;
    border-radius: 8px;
    outline: none;
}

/* Lists */
QListWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    color: #94A3B8;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #1E293B;
    color: #FFFFFF;
}

QListWidget::item:selected {
    background-color: #4F46E5;
    color: #FFFFFF;
    font-weight: 600;
}

/* Labels */
QLabel {
    color: #F8FAFC;
}

QLabel.HeaderTitle {
    font-size: 24px;
    font-weight: 800;
    color: #FFFFFF;
}

QLabel.HeaderSubtitle {
    font-size: 13px;
    color: #94A3B8;
}

QLabel.SectionHeader {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel.FieldLabel {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
}

QLabel.StatValue {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
}

QLabel.StatLabel {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QLabel.MutedText {
    font-size: 12px;
    color: #94A3B8;
}

QLabel.CardTitle {
    font-size: 15px;
    font-weight: 700;
    color: #FFFFFF;
}

/* Progress Bars */
QProgressBar {
    background-color: #0F172A;
    border-radius: 4px;
    border: none;
}

QProgressBar::chunk {
    background-color: #4F46E5;
    border-radius: 4px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #1E293B;
}

QTabBar::tab {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #1E293B;
    color: #FFFFFF;
    font-weight: 600;
    border-bottom: 2px solid #4F46E5;
}

/* Checkbox */
QCheckBox {
    color: #E2E8F0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0F172A;
}

QCheckBox::indicator:checked {
    background-color: #4F46E5;
    border-color: #6366F1;
}

/* Dialogs & Menus */
QDialog, QMessageBox, QInputDialog, QFileDialog {
    background-color: #1E293B;
    color: #F8FAFC;
}

QDialog QLabel, QMessageBox QLabel {
    color: #F8FAFC;
}

QDialog QPushButton, QMessageBox QPushButton {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}

QDialog QPushButton:hover, QMessageBox QPushButton:hover {
    background-color: #4F46E5;
    color: #FFFFFF;
}

QMenu {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item:selected {
    background-color: #4F46E5;
    color: #FFFFFF;
}

QToolTip {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

LIGHT_THEME = """
/* Base Window & Global */
QMainWindow, QWidget#MainContent, QStackedWidget#MainContent {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

QFrame#WorkspaceSidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    border: none;
    background: #F8FAFC;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sidebar Nav Buttons */
QPushButton.NavBtn {
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-weight: 500;
    font-size: 13px;
}

QPushButton.NavBtn:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.NavBtn:checked, QPushButton.NavBtn[active="true"] {
    background-color: #EEF2FF;
    color: #4F46E5;
    font-weight: 600;
}

/* Primary, Secondary, Ghost, Danger Buttons */
QPushButton.PrimaryBtn {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryBtn:hover {
    background-color: #4338CA;
}

QPushButton.PrimaryBtn:pressed {
    background-color: #3730A3;
}

QPushButton.SecondaryBtn {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton.SecondaryBtn:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
    color: #0F172A;
}

QPushButton.GhostBtn {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}

QPushButton.GhostBtn:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.DangerBtn {
    background-color: #E11D48;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}

QPushButton.DangerBtn:hover {
    background-color: #BE123C;
}

/* Cards & Containers */
QFrame.Card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

QFrame.Card:hover {
    border-color: #818CF8;
}

QFrame.StatCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

QFrame.StatCard:hover {
    border-color: #4F46E5;
}

QFrame.ItemCard {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px;
}

QFrame.ItemCard:hover {
    border-color: #CBD5E1;
}

QFrame.TopBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
}

/* Live Preview Area */
QFrame.PreviewArea {
    background-color: #F1F5F9;
    border-left: 1px solid #CBD5E1;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1.5px solid #4F46E5;
    background-color: #FFFFFF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #0F172A;
    selection-background-color: #EEF2FF;
    selection-color: #4F46E5;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    outline: none;
}

/* Lists */
QListWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    color: #475569;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QListWidget::item:selected {
    background-color: #EEF2FF;
    color: #4F46E5;
    font-weight: 600;
}

/* Labels */
QLabel {
    color: #0F172A;
}

QLabel.HeaderTitle {
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
}

QLabel.HeaderSubtitle {
    font-size: 13px;
    color: #64748B;
}

QLabel.SectionHeader {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
}

QLabel.FieldLabel {
    font-size: 11px;
    font-weight: 600;
    color: #64748B;
}

QLabel.StatValue {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
}

QLabel.StatLabel {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QLabel.MutedText {
    font-size: 12px;
    color: #64748B;
}

QLabel.CardTitle {
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
}

/* Progress Bars */
QProgressBar {
    background-color: #E2E8F0;
    border-radius: 4px;
    border: none;
}

QProgressBar::chunk {
    background-color: #4F46E5;
    border-radius: 4px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F1F5F9;
    color: #64748B;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #4F46E5;
    font-weight: 600;
    border-bottom: 2px solid #4F46E5;
}

/* Checkbox */
QCheckBox {
    color: #334155;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #4F46E5;
    border-color: #4F46E5;
}

/* Dialogs & Menus */
QDialog, QMessageBox, QInputDialog, QFileDialog {
    background-color: #FFFFFF;
    color: #0F172A;
}

QDialog QLabel, QMessageBox QLabel {
    color: #0F172A;
}

QDialog QPushButton, QMessageBox QPushButton {
    background-color: #F1F5F9;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}

QDialog QPushButton:hover, QMessageBox QPushButton:hover {
    background-color: #4F46E5;
    color: #FFFFFF;
}

QMenu {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item:selected {
    background-color: #EEF2FF;
    color: #4F46E5;
}

QToolTip {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

def get_stylesheet(theme_name: str = "dark") -> str:
    return DARK_THEME if theme_name.lower() == "dark" else LIGHT_THEME
