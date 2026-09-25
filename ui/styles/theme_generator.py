import sys
import os
from ui.styles.colors import LightPalette, DarkPalette

if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    ICONS_DIR = os.path.abspath(os.path.join(base_dir, 'ui', 'styles', 'icons')).replace('\\', '/')
else:
    ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons')).replace('\\', '/')

def ensure_triangle_icons():
    os.makedirs(ICONS_DIR, exist_ok=True)
    down_l = os.path.join(ICONS_DIR, 'arrow_down_light.png')
    down_d = os.path.join(ICONS_DIR, 'arrow_down_dark.png')
    up_l = os.path.join(ICONS_DIR, 'arrow_up_light.png')
    up_d = os.path.join(ICONS_DIR, 'arrow_up_dark.png')
    if not all((os.path.exists(p) for p in [down_l, down_d, up_l, up_d])):
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QPixmap, QPainter, QColor, QPolygonF, QBrush
            from PySide6.QtCore import Qt, QPointF
            _app = QApplication.instance()
            if _app is not None:
                def render_poly(filename, is_down, color_hex, size=64):
                    pix = QPixmap(size, size)
                    pix.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pix)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(QColor(color_hex)))
                    if is_down:
                        poly = QPolygonF([QPointF(12, 22), QPointF(52, 22), QPointF(32, 46)])
                    else:
                        poly = QPolygonF([QPointF(32, 18), QPointF(12, 42), QPointF(52, 42)])
                    painter.drawPolygon(poly)
                    painter.end()
                    pix.save(filename, 'PNG')
                render_poly(down_l, True, '#52525B')
                render_poly(down_d, True, '#CBD5E1')
                render_poly(up_l, False, '#52525B')
                render_poly(up_d, False, '#CBD5E1')
        except Exception:
            pass

def generate_stylesheet(mode='Light', scale_factor=1.0) -> str:
    ensure_triangle_icons()
    p = DarkPalette if mode == 'Dark' else LightPalette
    arrow_down_icon = f'{ICONS_DIR}/arrow_down_dark.png' if mode == 'Dark' else f'{ICONS_DIR}/arrow_down_light.png'
    arrow_up_icon = f'{ICONS_DIR}/arrow_up_dark.png' if mode == 'Dark' else f'{ICONS_DIR}/arrow_up_light.png'
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
    drop_btn_w = max(28, int(34 * scale_factor))
    arrow_size = max(10, int(12 * scale_factor))
    qss = f'''
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

    QFrame#MetricCard, QFrame[metricCard="true"] {{
        background-color: {p.BG_METRIC};
        border: 1px solid {p.BORDER_METRIC};
        border-radius: 10px;
    }}

    QLabel#UserBadge, QLabel[userBadge="true"] {{
        background-color: {p.BG_BADGE};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 6px 14px;
        font-weight: 600;
        color: {p.TEXT_PRIMARY};
    }}

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

    QLabel#MetricValue, QLabel[metricValue="true"] {{\n        font-size: {f_metric}px;
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

    QComboBox {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.BORDER_INPUT};
        border-radius: 8px;
        padding: {pad_v}px {pad_h + drop_btn_w}px {pad_v}px {pad_h}px;
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
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: {drop_btn_w}px;
        border: none;
        border-left: 1px solid {p.BORDER_INPUT};
        border-top-right-radius: 7px;
        border-bottom-right-radius: 7px;
        background-color: {p.SECONDARY_BG};
    }}

    QComboBox::drop-down:hover {{
        background-color: {p.SECONDARY_HOVER};
    }}

    QComboBox::down-arrow {{
        image: url("{arrow_down_icon}");
        width: {arrow_size}px;
        height: {arrow_size}px;
    }}

    QComboBox::down-arrow:on {{
        image: url("{arrow_up_icon}");
        width: {arrow_size}px;
        height: {arrow_size}px;
    }}

    QComboBox QAbstractItemView, QComboBox QListView {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 0px;
        selection-background-color: {p.PRIMARY};
        selection-color: {p.PRIMARY_TEXT};
        padding: 2px;
        outline: 0px;
        color: {p.TEXT_PRIMARY};
        font-size: {f_base}px;
    }}

    QComboBox QAbstractItemView::item, QComboBox QListView::item {{
        min-height: {max(24, int(28 * scale_factor))}px;
        padding: 4px 10px;
        border: none;
        border-radius: 4px;
        color: {p.TEXT_PRIMARY};
        background: transparent;
    }}

    QComboBox QAbstractItemView::item:hover,
    QComboBox QAbstractItemView::item:selected,
    QComboBox QListView::item:hover,
    QComboBox QListView::item:selected {{
        background-color: {p.PRIMARY};
        color: {p.PRIMARY_TEXT};
        border: none;
    }}

    QMenu {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 4px;
        color: {p.TEXT_PRIMARY};
    }}

    QMenu::item {{
        padding: 6px 16px;
        border-radius: 4px;
        color: {p.TEXT_PRIMARY};
        background: transparent;
    }}

    QMenu::item:selected {{
        background-color: {p.PRIMARY};
        color: {p.PRIMARY_TEXT};
    }}

    QSpinBox, QDoubleSpinBox {{
        padding-right: {drop_btn_w}px;
    }}

    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: {drop_btn_w}px;
        border: none;
        border-left: 1px solid {p.BORDER_INPUT};
        border-bottom: 1px solid {p.BORDER_INPUT};
        border-top-right-radius: 7px;
        background-color: {p.SECONDARY_BG};
    }}

    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background-color: {p.SECONDARY_HOVER};
    }}

    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url("{arrow_up_icon}");
        width: {max(7, int(8 * scale_factor))}px;
        height: {max(7, int(8 * scale_factor))}px;
    }}

    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: {drop_btn_w}px;
        border: none;
        border-left: 1px solid {p.BORDER_INPUT};
        border-bottom-right-radius: 7px;
        background-color: {p.SECONDARY_BG};
    }}

    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {p.SECONDARY_HOVER};
    }}

    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url("{arrow_down_icon}");
        width: {max(7, int(8 * scale_factor))}px;
        height: {max(7, int(8 * scale_factor))}px;
    }}

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

    QTableWidget, QTableView {{
        background-color: {p.BG_CARD};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 10px;
        gridline-color: {p.BORDER_DEFAULT};
        selection-background-color: {p.NAV_ACTIVE_BG};
        selection-color: {(p.PRIMARY_TEXT if mode == 'Dark' else p.NAV_ACTIVE_TEXT)};
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

    QToolTip {{
        background-color: {p.BG_CARD};
        color: {p.TEXT_PRIMARY};
        border: 1px solid {p.BORDER_DEFAULT};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {f_small}px;
    }}
    '''
    return qss
