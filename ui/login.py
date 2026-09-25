"""
Login and Faculty Registration screen in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QMessageBox, QFrame, QScrollArea, QSizePolicy
)

from database.database import (
    authenticate_user,
    add_user,
    get_all_subjects,
    get_app_setting
)
from ui.theme import apply_theme, apply_scaling


class LoginWindow(QMainWindow):
    def __init__(self, parent=None, on_login_success=None, window=None):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.current_mode = "login"  # "login" or "register"
        self.subjects_data = []

        # Setup application window
        self.setWindowTitle("Login - Smart Academic Timetable Management System")
        self.resize(1000, 720)
        self.setMinimumSize(900, 650)

        # Apply saved appearance settings
        apply_theme(mode=get_app_setting("appearance_mode", "Light"))

        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        scroll_content.setMinimumWidth(800)
        scroll.setWidget(scroll_content)

        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main title
        self.title_label = QLabel("Smart Academic Timetable Management System")
        self.title_label.setObjectName("Heading")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("College Academic Management Portal")
        self.subtitle_label.setObjectName("Secondary")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.subtitle_label)

        main_layout.addSpacing(10)

        # Card container
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card.setFixedWidth(500)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(35, 25, 35, 30)
        self.card_layout.setSpacing(14)

        # Segmented buttons (Sign In / Faculty Registration)
        mode_btn_layout = QHBoxLayout()
        mode_btn_layout.setSpacing(8)

        self.btn_mode_login = QPushButton("Sign In")
        self.btn_mode_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_login.clicked.connect(self.show_login_form)

        self.btn_mode_register = QPushButton("Faculty Registration")
        self.btn_mode_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_register.clicked.connect(self.show_register_form)

        mode_btn_layout.addWidget(self.btn_mode_login)
        mode_btn_layout.addWidget(self.btn_mode_register)
        self.card_layout.addLayout(mode_btn_layout)

        # Form content frame
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(0, 10, 0, 0)
        self.form_layout.setSpacing(12)
        self.card_layout.addWidget(self.form_container)

        main_layout.addWidget(self.card, 0, Qt.AlignmentFlag.AlignCenter)

        # Footer
        footer = QLabel("Smart Academic Timetable Management System • Secured with Salted PBKDF2 Encryption")
        footer.setObjectName("Secondary")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

        # Initial view
        self.show_login_form()

    def update_mode_buttons(self):
        if self.current_mode == "login":
            self.btn_mode_login.setProperty("btnStyle", "primary")
            self.btn_mode_register.setProperty("btnStyle", "secondary")
        else:
            self.btn_mode_login.setProperty("btnStyle", "secondary")
            self.btn_mode_register.setProperty("btnStyle", "primary")

        self.btn_mode_login.style().unpolish(self.btn_mode_login)
        self.btn_mode_login.style().polish(self.btn_mode_login)
        self.btn_mode_register.style().unpolish(self.btn_mode_register)
        self.btn_mode_register.style().polish(self.btn_mode_register)

    def clear_form(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_login_form(self):
        self.current_mode = "login"
        self.update_mode_buttons()
        self.clear_form()

        # Login heading
        title = QLabel("Sign In to Portal")
        title.setObjectName("Subheading")
        self.form_layout.addWidget(title)

        # Username
        lbl_user = QLabel("Account Name (Username)")
        lbl_user.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_user)

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("e.g. admin or faculty_username")
        self.username_entry.returnPressed.connect(self.login)
        self.form_layout.addWidget(self.username_entry)

        # Password
        lbl_pwd = QLabel("Password")
        lbl_pwd.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_pwd)

        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.returnPressed.connect(self.login)
        self.form_layout.addWidget(self.password_entry)

        # Show password toggle
        self.show_pwd_check = QCheckBox("Show password")
        self.show_pwd_check.toggled.connect(
            lambda checked: self.password_entry.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        self.form_layout.addWidget(self.show_pwd_check)

        # Submit button
        submit_btn = QPushButton("Sign In")
        submit_btn.setMinimumHeight(38)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self.login)
        self.form_layout.addWidget(submit_btn)

        # Switch link button
        switch_btn = QPushButton("New faculty member? Register here")
        switch_btn.setProperty("btnStyle", "ghost")
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.clicked.connect(self.show_register_form)
        self.form_layout.addWidget(switch_btn)

        self.username_entry.setFocus()

    def show_register_form(self):
        self.current_mode = "register"
        self.update_mode_buttons()
        self.clear_form()

        # Dynamic subjects from DB
        try:
            self.subjects_data = get_all_subjects() or []
        except Exception:
            self.subjects_data = []

        # Heading
        title = QLabel("Register Faculty Account")
        title.setObjectName("Subheading")
        self.form_layout.addWidget(title)

        # Username / Account ID
        lbl_user = QLabel("Username / Account ID")
        lbl_user.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_user)

        self.reg_username_entry = QLineEdit()
        self.reg_username_entry.setPlaceholderText("e.g. john_doe (min 3 chars)")
        self.form_layout.addWidget(self.reg_username_entry)

        # Faculty Full Name
        lbl_name = QLabel("Faculty Full Name")
        lbl_name.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_name)

        self.reg_fullname_entry = QLineEdit()
        self.reg_fullname_entry.setPlaceholderText("e.g. Dr. John Doe")
        self.form_layout.addWidget(self.reg_fullname_entry)

        # Primary Teaching Subject
        lbl_sub = QLabel("Primary Teaching Subject")
        lbl_sub.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_sub)

        self.reg_subject_combo = QComboBox()
        if self.subjects_data:
            for s in self.subjects_data:
                code = s[1] if len(s) > 1 else ""
                sname = s[2] if len(s) > 2 else ""
                dept = s[3] if len(s) > 3 else ""
                self.reg_subject_combo.addItem(f"{code} - {sname} ({dept})", s)
        else:
            self.reg_subject_combo.addItem("General (No subjects in database)")
        self.form_layout.addWidget(self.reg_subject_combo)

        # Password
        lbl_pwd = QLabel("Password")
        lbl_pwd.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_pwd)

        self.reg_password_entry = QLineEdit()
        self.reg_password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_entry.setPlaceholderText("Password (min 4 chars)")
        self.form_layout.addWidget(self.reg_password_entry)

        # Confirm Password
        lbl_cpwd = QLabel("Confirm Password")
        lbl_cpwd.setObjectName("FormLabel")
        self.form_layout.addWidget(lbl_cpwd)

        self.reg_confirm_entry = QLineEdit()
        self.reg_confirm_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm_entry.setPlaceholderText("Re-type password")
        self.reg_confirm_entry.returnPressed.connect(self.register_user)
        self.form_layout.addWidget(self.reg_confirm_entry)

        # Show passwords checkbox
        self.reg_show_pwd_check = QCheckBox("Show passwords")
        self.reg_show_pwd_check.toggled.connect(self.toggle_reg_passwords)
        self.form_layout.addWidget(self.reg_show_pwd_check)

        # Register button
        submit_btn = QPushButton("Create Faculty Account & Sign In")
        submit_btn.setProperty("btnStyle", "success")
        submit_btn.setMinimumHeight(38)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self.register_user)
        self.form_layout.addWidget(submit_btn)

        # Switch link button
        switch_btn = QPushButton("Already have an account? Sign In")
        switch_btn.setProperty("btnStyle", "ghost")
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.clicked.connect(self.show_login_form)
        self.form_layout.addWidget(switch_btn)

        self.reg_username_entry.setFocus()

    def toggle_reg_passwords(self, checked):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.reg_password_entry.setEchoMode(mode)
        self.reg_confirm_entry.setEchoMode(mode)

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text()

        if not username or not password:
            QMessageBox.warning(self, "Login", "Please enter both username and password.")
            return

        user = authenticate_user(username, password)
        if user:
            role = user.get("role", "Faculty")
            display_name = user.get("full_name") or user.get("username", "User")
            QMessageBox.information(
                self,
                "Login Successful",
                f"Welcome, {display_name}!\n\nLogged in as {role}."
            )

            if self.on_login_success:
                try:
                    self.on_login_success(self, user)
                except TypeError:
                    try:
                        self.on_login_success(self)
                    except TypeError:
                        self.on_login_success()
        else:
            QMessageBox.critical(
                self,
                "Login Failed",
                "Invalid username or password.\n\nPlease check your credentials or register as a faculty member."
            )

    def register_user(self):
        username = self.reg_username_entry.text().strip()
        fullname = self.reg_fullname_entry.text().strip()
        selected_subject_str = self.reg_subject_combo.currentText().strip()
        password = self.reg_password_entry.text()
        confirm_pwd = self.reg_confirm_entry.text()

        if not username:
            QMessageBox.warning(self, "Create Account", "Please enter an account name.")
            self.reg_username_entry.setFocus()
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Create Account", "Account name must be at least 3 characters.")
            self.reg_username_entry.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Create Account", "Please enter a password.")
            self.reg_password_entry.setFocus()
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Create Account", "Password must be at least 4 characters long.")
            self.reg_password_entry.setFocus()
            return

        if password != confirm_pwd:
            QMessageBox.critical(self, "Create Account", "Passwords do not match. Please re-enter.")
            self.reg_confirm_entry.setFocus()
            return

        department = "General"
        if self.subjects_data:
            for s in self.subjects_data:
                code = s[1] if len(s) > 1 else ""
                dept = s[3] if len(s) > 3 else ""
                if selected_subject_str.startswith(code) and dept:
                    department = dept
                    break

        success, msg = add_user(
            username=username,
            password=password,
            role="Faculty",
            full_name=fullname if fullname else username,
            department=department
        )

        if not success:
            QMessageBox.critical(self, "Registration Failed", msg)
            return

        QMessageBox.information(
            self,
            "Faculty Account Created",
            f"Faculty account '{username}' registered successfully!\n\nLogging in to your Faculty Portal..."
        )

        user = authenticate_user(username, password)
        if self.on_login_success:
            try:
                self.on_login_success(self, user)
            except TypeError:
                try:
                    self.on_login_success(self)
                except TypeError:
                    self.on_login_success()

    def run(self):
        self.show()


if __name__ == "__main__":
    from database.database import create_tables
    create_tables()

    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    login_app = LoginWindow()
    login_app.show()
    sys.exit(app.exec())
