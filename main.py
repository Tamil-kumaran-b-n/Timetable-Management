from database.database import create_tables
from ui.login import LoginWindow
from ui.dashboard import Dashboard


def open_dashboard():
    dashboard = Dashboard()
    dashboard.run()


def main():
    # Create database tables
    create_tables()

    # Start login screen
    login = LoginWindow(
        on_login_success=open_dashboard
    )

    login.run()


if __name__ == "__main__":
    main()