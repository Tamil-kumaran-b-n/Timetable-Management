from database.database import create_tables
from ui.login import LoginWindow
from ui.dashboard import Dashboard


def open_dashboard(window=None, current_user=None):
    dashboard = Dashboard(window=window, current_user=current_user)
    if window is None:
        dashboard.run()


def main():
    # Create database tables & seed initial data
    create_tables()

    # Start login screen
    login = LoginWindow(
        on_login_success=open_dashboard
    )

    login.run()


if __name__ == "__main__":
    main()