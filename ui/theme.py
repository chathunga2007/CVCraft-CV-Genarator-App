"""
CVCraft Design System & Theme Engine
Supports Dark and Light modes with Deep Indigo & Royal Purple visual identity.
"""

DARK_THEME = """
/* Base Window & Global */
QMainWindow, QWidget#MainContent {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget#Sidebar {
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
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
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
    padding: 8px 16px;
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

QFrame.StatCard {
    background-color: #162032;
    border: 1px solid #27354A;
    border-radius: 12px;
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

/* Labels */
QLabel.HeaderTitle {
    font-size: 22px;
    font-weight: 700;
    color: #F8FAFC;
}

QLabel.HeaderSubtitle {
    font-size: 13px;
    color: #94A3B8;
}

QLabel.SectionHeader {
    font-size: 15px;
    font-weight: 600;
    color: #E2E8F0;
}

QLabel.FieldLabel {
    font-size: 12px;
    font-weight: 500;
    color: #CBD5E1;
}

QLabel.StatValue {
    font-size: 24px;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel.StatLabel {
    font-size: 12px;
    color: #94A3B8;
    font-weight: 500;
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

/* Dialogs */
QDialog {
    background-color: #1E293B;
    color: #F8FAFC;
}
"""

LIGHT_THEME = """
/* Base Window & Global */
QMainWindow, QWidget#MainContent {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget#Sidebar {
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
    color: #64748B;
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

QPushButton.SecondaryBtn {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
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
    padding: 8px 16px;
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

QFrame.StatCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #4F46E5;
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
}

/* Labels */
QLabel.HeaderTitle {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
}

QLabel.HeaderSubtitle {
    font-size: 13px;
    color: #64748B;
}

QLabel.SectionHeader {
    font-size: 15px;
    font-weight: 600;
    color: #1E293B;
}

QLabel.FieldLabel {
    font-size: 12px;
    font-weight: 500;
    color: #475569;
}

QLabel.StatValue {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
}

QLabel.StatLabel {
    font-size: 12px;
    color: #64748B;
    font-weight: 500;
}

/* Dialogs */
QDialog {
    background-color: #FFFFFF;
    color: #0F172A;
}
"""

def get_stylesheet(theme_name: str = "dark") -> str:
    return DARK_THEME if theme_name.lower() == "dark" else LIGHT_THEME
