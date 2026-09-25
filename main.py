import sys
from PySide6.QtWidgets import QApplication
from database.database import create_tables
from ui.login import LoginWindow
from ui.dashboard import Dashboard
from ui.theme import apply_theme, apply_scaling
active_dashboard = None
active_login = None

def open_dashboard(login_win=None, current_user=None):
    global active_dashboard, active_login
    if login_win is not None:
        login_win.close()
    active_dashboard = Dashboard(current_user=current_user)
    active_dashboard.show()

def main():
    global active_login
    create_tables()
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName('Smart Academic Timetable Management System')
    apply_theme(app)
    apply_scaling(app)
    active_login = LoginWindow(on_login_success=open_dashboard)
    active_login.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
