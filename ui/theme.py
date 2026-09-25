from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from database.database import get_app_setting, set_app_setting
from ui.styles.theme_generator import generate_stylesheet
from ui.styles.colors import LightPalette, DarkPalette

def get_current_theme_mode() -> str:
    mode = get_app_setting('appearance_mode', 'Light')
    if mode == 'System':
        try:
            import darkdetect
            return 'Dark' if darkdetect.isDark() else 'Light'
        except Exception:
            return 'Light'
    return mode if mode in ['Light', 'Dark'] else 'Light'

def get_active_palette():
    return DarkPalette if get_current_theme_mode() == 'Dark' else LightPalette

def get_current_scale_factor() -> float:
    scale_str = get_app_setting('ui_scaling', '100%')
    try:
        return float(scale_str.replace('%', '').strip()) / 100.0
    except Exception:
        return 1.0

def apply_theme(app: QApplication=None, mode: str=None, scale_str: str=None):
    if app is None:
        app = QApplication.instance()
        if app is None:
            return
    if mode is None:
        effective_mode = get_current_theme_mode()
    elif mode == 'System':
        try:
            import darkdetect
            effective_mode = 'Dark' if darkdetect.isDark() else 'Light'
        except Exception:
            effective_mode = 'Light'
    else:
        effective_mode = mode
    if scale_str is not None:
        try:
            scale_factor = float(scale_str.replace('%', '').strip()) / 100.0
        except Exception:
            scale_factor = get_current_scale_factor()
    else:
        scale_factor = get_current_scale_factor()
    if app.style().objectName() != 'fusion':
        app.setStyle('Fusion')
    qss = generate_stylesheet(mode=effective_mode, scale_factor=scale_factor)
    app.setStyleSheet(qss)
    base_size = max(9, int(10 * scale_factor))
    font = app.font()
    font.setPointSize(base_size)
    app.setFont(font)

def apply_scaling(app: QApplication=None, scale_str: str=None):
    apply_theme(app=app, scale_str=scale_str)
