"""
Dynamic stylesheet generator for PySide6.
Generates responsive QSS for Light/Dark themes and dynamic UI scaling factors.
"""

from ui.styles.colors import LightPalette, DarkPalette


def generate_stylesheet(mode="Light", scale_factor=1.0) -> str:
    """Generate complete QSS with responsive font sizes, paddings, and palette colors."""
    p = DarkPalette if mode == "Dark" else LightPalette

    # Scaled dimensions & typography
    f_base = max(9, int(13 * scale_factor))
    f_small = max(8, int(11 * scale_factor))
    f_h1 = max(16, int(22 * scale_factor))
    f_h2 = max(14, int(17 * scale_factor))
    f_h3 = max(12, int(15 * scale_factor))
    f_metric = max(18, int(26 * scale_factor))

    pad_v = max(4, int(7 * scale_factor))
    pad_h = max(8, int(12 * scale_factor))
    btn_pad_v = max(6, int(9 * scale_factor))
    btn_pad_h = max(12, int(18 * scale_factor))
    input_min_h = max(24, int(26 * scale_factor))
    btn_min_h = max(24, int(26 * scale_factor))
    nav_btn_size = max(30, int(38 * scale_factor))
    f_arrow = max(15, int(19 * scale_factor))

    qss = f"""
    /* =======================================================
       BASE WINDOW & GLOBAL SETTINGS
       ======================================================= */
    QMainWindow, QDialog {{
        background-color: {p.BG_WINDOW};
        color: {p.TEXT_PRIMARY};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: {f_base}px;
    }}

    QWidget {{
        color: {p.TEXT_PRIMARY};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: {f_base}px;
        background: transparent;
    }}

    QWidget#CentralWidget, QWidget#ScrollContent, QWidget#PageContent {{
        background-color: {p.BG_WINDOW};
    }}

    QScrollArea {{
        background-color: transparent;
        border: none;
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}

    /* =======================================================
       CARD & FRAME CONTAINERS
       ======================================================= */
    QFrame#Card, QFrame[card="true"] {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 12px;
    }}

    QFrame#Header, QFrame[header="true"] {{
        background-color: {p.BG_HEADER};
        border-bottom: 1px solid {p.BORDER_DEFAULT};
    }}

    QFrame#Sidebar {{
        background-color: {p.BG_SIDEBAR};
        border-right: 1px solid {p.BORDER_DEFAULT};
    }}

    /* Metric Stat Box (e.g. Dashboard & Timetable Generation) */
    QFrame#MetricCard, QFrame[metricCard="true"] {{
        background-color: {p.BG_METRIC};
        border: 1px solid {p.BORDER_METRIC};
        border-radius: 10px;
    }}

    /* User Profile Badge */
    QLabel#UserBadge, QLabel[userBadge="true"] {{
        background-color: {p.BG_BADGE};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 6px 14px;
        font-weight: 600;
        color: {p.TEXT_PRIMARY};
    }}

    /* =======================================================
       TYPOGRAPHY / LABELS
       ======================================================= */
    QLabel {{
        background: transparent;
        color: {p.TEXT_PRIMARY};
        font-size: {f_base}px;
    }}

    QLabel#Heading, QLabel[heading="true"] {{
        font-size: {f_h1}px;
        font-weight: bold;
        color: {p.TEXT_PRIMARY};
    }}

    QLabel#Subheading, QLabel[subheading="true"] {{
        font-size: {f_h3}px;
        font-weight: 600;
        color: {p.TEXT_PRIMARY};
    }}

    QLabel#SectionTitle, QLabel[sectionTitle="true"] {{
        font-size: {f_h2}px;
        font-weight: bold;
        color: {p.TEXT_PRIMARY};
    }}

    QLabel#FormLabel, QLabel[formLabel="true"] {{
        font-size: {f_base}px;
        font-weight: 600;
        color: {p.TEXT_PRIMARY};
        margin-bottom: 2px;
    }}

    QLabel#Secondary, QLabel[secondary="true"] {{
        color: {p.TEXT_MUTED};
        font-size: {f_small}px;
    }}

    QLabel#MetricValue, QLabel[metricValue="true"] {{
        font-size: {f_metric}px;
        font-weight: bold;
        color: {p.PRIMARY};
    }}

    QLabel#MetricLabel, QLabel[metricLabel="true"] {{
        font-size: {f_small}px;
        color: {p.TEXT_METRIC_LABEL};
    }}

    QLabel#NoticeText, QLabel[noticeText="true"] {{
        color: {p.TEXT_SECONDARY};
        font-size: {f_base}px;
    }}

    /* =======================================================
       FORM INPUTS (LINEEDIT, COMBOBOX, SPINBOX)
       ======================================================= */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.BORDER_INPUT};
        border-radius: 8px;
        padding: {pad_v}px {pad_h}px;
        min-height: {input_min_h}px;
        color: {p.TEXT_PRIMARY};
        selection-background-color: {p.PRIMARY};
        selection-color: {p.PRIMARY_TEXT};
        font-size: {f_base}px;
    }}

    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1px solid {p.BORDER_INPUT_HOVER};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1.5px solid {p.BORDER_INPUT_FOCUS};
        background-color: {p.BG_INPUT};
    }}

    QLineEdit:disabled, QTextEdit:disabled {{
        background-color: {p.BG_WINDOW};
        color: {p.TEXT_PLACEHOLDER};
        border: 1px solid {p.BORDER_DEFAULT};
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.BORDER_INPUT};
        border-radius: 8px;
        padding: {pad_v}px {pad_h}px;
        color: {p.TEXT_PRIMARY};
        min-height: {input_min_h}px;
        font-size: {f_base}px;
    }}

    QComboBox:hover {{
        border: 1px solid {p.BORDER_INPUT_HOVER};
    }}

    QComboBox:focus {{
        border: 1.5px solid {p.BORDER_INPUT_FOCUS};
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: none;
        background: transparent;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {p.TEXT_MUTED};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 8px;
        selection-background-color: {p.PRIMARY};
        selection-color: {p.PRIMARY_TEXT};
        padding: 4px;
        outline: none;
        color: {p.TEXT_PRIMARY};
        font-size: {f_base}px;
    }}

    /* =======================================================
       BUTTONS & VARIANTS
       ======================================================= */
    QPushButton {{
        background-color: {p.PRIMARY};
        color: {p.PRIMARY_TEXT};
        border: none;
        border-radius: 8px;
        padding: {btn_pad_v}px {btn_pad_h}px;
        font-weight: 600;
        font-size: {f_base}px;
        min-height: {btn_min_h}px;
    }}

    QPushButton:hover {{
        background-color: {p.PRIMARY_HOVER};
    }}

    QPushButton:pressed {{
        background-color: {p.PRIMARY_PRESSED};
    }}

    QPushButton:disabled {{
        background-color: {p.BORDER_DEFAULT};
        color: {p.TEXT_PLACEHOLDER};
    }}

    QPushButton[btnStyle="secondary"] {{
        background-color: {p.SECONDARY_BG};
        color: {p.SECONDARY_TEXT};
        border: 1px solid {p.BORDER_INPUT};
    }}
    QPushButton[btnStyle="secondary"]:hover {{
        background-color: {p.SECONDARY_HOVER};
        border-color: {p.BORDER_INPUT_HOVER};
    }}

    QPushButton[btnStyle="success"] {{
        background-color: {p.SUCCESS};
        color: {p.SUCCESS_TEXT};
    }}
    QPushButton[btnStyle="success"]:hover {{
        background-color: {p.SUCCESS_HOVER};
    }}

    QPushButton[btnStyle="danger"] {{
        background-color: {p.DANGER};
        color: {p.DANGER_TEXT};
    }}
    QPushButton[btnStyle="danger"]:hover {{
        background-color: {p.DANGER_HOVER};
    }}

    QPushButton[btnStyle="outline-danger"] {{
        background-color: {p.OUTLINE_DANGER_BG};
        color: {p.OUTLINE_DANGER_TEXT};
        border: 1px solid {p.OUTLINE_DANGER_BORDER};
    }}
    QPushButton[btnStyle="outline-danger"]:hover {{
        background-color: {p.OUTLINE_DANGER_HOVER};
    }}

    QPushButton[btnStyle="nav"] {{
        background-color: transparent;
        color: {p.NAV_TEXT};
        border: none;
        border-radius: 8px;
        text-align: left;
        padding: 10px 16px;
        font-size: {f_base}px;
        font-weight: 600;
    }}
    QPushButton[btnStyle="nav"]:hover {{
        background-color: {p.NAV_HOVER_BG};
        color: {p.NAV_HOVER_TEXT};
    }}
    QPushButton[btnStyle="nav"][active="true"] {{
        background-color: {p.NAV_ACTIVE_BG};
        color: {p.NAV_ACTIVE_TEXT};
        font-weight: bold;
    }}

    QPushButton[btnStyle="ghost"] {{
        background-color: transparent;
        color: {p.TEXT_MUTED};
        border: none;
    }}
    QPushButton[btnStyle="ghost"]:hover {{
        color: {p.TEXT_PRIMARY};
        background-color: {p.SECONDARY_HOVER};
    }}

    /* Navigation / Arrow Square Buttons */
    QPushButton#NavArrow, QPushButton[btnStyle="icon"] {{
        background-color: {p.SECONDARY_BG};
        color: {p.SECONDARY_TEXT};
        border: 1px solid {p.BORDER_INPUT};
        border-radius: 8px;
        padding: 0px;
        min-width: {nav_btn_size}px;
        max-width: {nav_btn_size}px;
        min-height: {nav_btn_size}px;
        max-height: {nav_btn_size}px;
        font-size: {f_arrow}px;
        font-weight: bold;
        text-align: center;
    }}
    QPushButton#NavArrow:hover, QPushButton[btnStyle="icon"]:hover {{
        background-color: {p.SECONDARY_HOVER};
        border-color: {p.BORDER_INPUT_HOVER};
    }}
    QPushButton#NavArrow:pressed, QPushButton[btnStyle="icon"]:pressed {{
        background-color: {p.SECONDARY_HOVER};
    }}
    QPushButton#NavArrow:disabled, QPushButton[btnStyle="icon"]:disabled {{
        background-color: {p.BORDER_DEFAULT};
        color: {p.TEXT_PLACEHOLDER};
        border: 1px solid transparent;
    }}

    /* =======================================================
       CHECKBOX & RADIOBUTTON
       ======================================================= */
    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: {p.TEXT_PRIMARY};
        font-weight: 500;
        background: transparent;
        font-size: {f_base}px;
    }}

    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1.5px solid {p.BORDER_INPUT_HOVER};
        border-radius: 4px;
        background-color: {p.BG_INPUT};
    }}

    QRadioButton::indicator {{
        border-radius: 9px;
    }}

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {p.PRIMARY};
        border-color: {p.PRIMARY};
    }}

    /* =======================================================
       TABLES
       ======================================================= */
    QTableWidget, QTableView {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 10px;
        gridline-color: {p.BORDER_DEFAULT};
        selection-background-color: {p.NAV_ACTIVE_BG};
        selection-color: {p.PRIMARY_TEXT if mode == 'Dark' else p.NAV_ACTIVE_TEXT};
        outline: none;
        color: {p.TEXT_PRIMARY};
        font-size: {f_base}px;
    }}

    QTableWidget::item, QTableView::item {{
        padding: 8px 12px;
        border-bottom: 1px solid {p.BORDER_DEFAULT};
    }}

    QHeaderView::section {{
        background-color: {p.BG_TABLE_HEADER};
        color: {p.TEXT_MUTED};
        font-weight: bold;
        font-size: {f_small}px;
        border: none;
        border-bottom: 2px solid {p.BORDER_DEFAULT};
        padding: 8px 12px;
    }}

    /* =======================================================
       SCROLLBARS
       ======================================================= */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background: {p.BORDER_INPUT};
        min-height: 25px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {p.BORDER_INPUT_HOVER};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 10px;
        margin: 0px;
        border-radius: 5px;
    }}

    QScrollBar::handle:horizontal {{
        background: {p.BORDER_INPUT};
        min-width: 25px;
        border-radius: 5px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {p.BORDER_INPUT_HOVER};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* =======================================================
       PROGRESS BAR
       ======================================================= */
    QProgressBar {{
        background-color: {p.BORDER_DEFAULT};
        border: none;
        border-radius: 6px;
        text-align: center;
        color: {p.TEXT_PRIMARY};
        font-weight: 600;
        font-size: {f_small}px;
    }}

    QProgressBar::chunk {{
        background-color: {p.PRIMARY};
        border-radius: 6px;
    }}

    /* =======================================================
       TAB WIDGET
       ======================================================= */
    QTabWidget::pane {{
        border: 1px solid {p.BORDER_DEFAULT};
        background-color: {p.BG_CARD};
        border-radius: 8px;
    }}

    QTabBar::tab {{
        background-color: {p.SECONDARY_BG};
        color: {p.TEXT_MUTED};
        padding: 8px 18px;
        font-weight: 600;
        font-size: {f_base}px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}

    QTabBar::tab:selected {{
        background-color: {p.BG_CARD};
        color: {p.PRIMARY};
        border: 1px solid {p.BORDER_DEFAULT};
        border-bottom: none;
    }}

    /* =======================================================
       DIALOGS & MESSAGE BOXES
       ======================================================= */
    QDialog, QMessageBox {{
        background-color: {p.BG_CARD};
        color: {p.TEXT_PRIMARY};
    }}

    QMessageBox QLabel {{
        color: {p.TEXT_PRIMARY};
        background: transparent;
        font-size: {f_base}px;
    }}

    QMessageBox QPushButton {{
        background-color: {p.PRIMARY};
        color: {p.PRIMARY_TEXT};
        border-radius: 6px;
        min-width: 80px;
        min-height: 28px;
        padding: 6px 14px;
        font-weight: 600;
    }}

    QMessageBox QPushButton:hover {{
        background-color: {p.PRIMARY_HOVER};
    }}

    /* =======================================================
       TOOLTIPS
       ======================================================= */
    QToolTip {{
        background-color: {p.BG_CARD};
        color: {p.TEXT_PRIMARY};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {f_small}px;
    }}
    """
    return qss
