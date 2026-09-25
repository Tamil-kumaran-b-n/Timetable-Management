"""
Main Application Dashboard in PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QMessageBox, QStackedWidget, QSizePolicy
)

from ui.faculty import FacultyWindow
from ui.subjects import SubjectsWindow
from ui.classrooms import ClassroomsWindow
from ui.classes import ClassesWindow
from ui.generate import GenerateTimetableWindow
from ui.view_timetable import ViewTimetableWindow
from ui.assignments import AssignmentsWindow
from ui.theme import apply_theme, apply_scaling

from database.database import (
    get_all_faculty,
    get_all_subjects,
    get_all_classrooms,
    get_app_setting,
    set_app_setting,
    get_connection
)
from database.generator import get_all_timetable


class Dashboard(QMainWindow):
    def __init__(self, parent=None, current_user=None, window=None):
        super().__init__(parent)
        self.current_user = current_user or {"username": "Administrator", "role": "Administrator"}

        self.setWindowTitle("Smart Academic Timetable Management System")
        self.resize(1200, 720)
        self.setMinimumSize(950, 620)

        # Apply saved appearance settings
        apply_theme(
            mode=get_app_setting("appearance_mode", "Light"),
            scale_str=get_app_setting("ui_scaling", "100%")
        )

        # Navigation history
        self.history = ["home"]
        self.history_index = 0

        self.nav_buttons = {}
        self.stat_labels = {}

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================================
        # SIDEBAR
        # =====================================================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setSpacing(6)

        is_admin = (self.current_user.get("role") in ["Administrator", "Admin", "admin"])

        # Title
        app_title = QLabel("SMART\nTIMETABLE" if is_admin else "FACULTY\nPORTAL")
        app_title.setObjectName("Heading")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        sidebar_layout.addSpacing(10)

        nav_header = QLabel("MAIN MENU" if is_admin else "FACULTY MENU")
        nav_header.setObjectName("Secondary")
        sidebar_layout.addWidget(nav_header)

        # Nav items
        self.nav_buttons["home"] = self.create_nav_button("Home", lambda: self.show_page("home"), sidebar_layout)

        if is_admin:
            self.nav_buttons["faculty"] = self.create_nav_button("Faculty", lambda: self.show_page("faculty"), sidebar_layout)
            self.nav_buttons["subjects"] = self.create_nav_button("Subjects", lambda: self.show_page("subjects"), sidebar_layout)
            self.nav_buttons["classrooms"] = self.create_nav_button("Classrooms", lambda: self.show_page("classrooms"), sidebar_layout)
            self.nav_buttons["classes"] = self.create_nav_button("Classes & Semesters", lambda: self.show_page("classes"), sidebar_layout)
            self.nav_buttons["assignments"] = self.create_nav_button("Faculty Workload", lambda: self.show_page("assignments"), sidebar_layout)
            self.nav_buttons["generate"] = self.create_nav_button("Generate Timetable", lambda: self.show_page("generate"), sidebar_layout)
            self.nav_buttons["view_timetable"] = self.create_nav_button("View Timetable", lambda: self.show_page("view_timetable"), sidebar_layout)
        else:
            self.nav_buttons["view_timetable"] = self.create_nav_button("My Timetable", lambda: self.show_page("view_timetable"), sidebar_layout)

        sidebar_layout.addStretch()

        # Bottom buttons
        self.nav_buttons["settings"] = self.create_nav_button("Settings", lambda: self.show_page("settings"), sidebar_layout)

        btn_logout = QPushButton("Logout")
        btn_logout.setProperty("btnStyle", "outline-danger")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setMinimumHeight(38)
        btn_logout.clicked.connect(self.confirm_logout)
        sidebar_layout.addWidget(btn_logout)

        root_layout.addWidget(sidebar)

        # =====================================================
        # RIGHT CONTENT AREA
        # =====================================================
        content_area = QWidget()
        content_area.setObjectName("PageContent")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("Header")
        top_bar.setFixedHeight(65)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(25, 10, 30, 10)

        # Back & Forward buttons
        self.btn_back = QPushButton("←")
        self.btn_back.setProperty("btnStyle", "secondary")
        self.btn_back.setFixedSize(36, 34)
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self.go_back)
        top_bar_layout.addWidget(self.btn_back)

        self.btn_forward = QPushButton("→")
        self.btn_forward.setProperty("btnStyle", "secondary")
        self.btn_forward.setFixedSize(36, 34)
        self.btn_forward.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forward.setEnabled(False)
        self.btn_forward.clicked.connect(self.go_forward)
        top_bar_layout.addWidget(self.btn_forward)

        top_bar_layout.addSpacing(15)

        # Page Title
        self.lbl_page_title = QLabel("Homepage")
        self.lbl_page_title.setObjectName("Heading")
        top_bar_layout.addWidget(self.lbl_page_title)

        top_bar_layout.addStretch()

        # User Profile Badge
        display_name = self.current_user.get("full_name") or self.current_user.get("username", "Administrator")
        role_str = self.current_user.get("role", "Administrator")
        user_badge = QLabel(f"{display_name} ({role_str})")
        user_badge.setObjectName("UserBadge")
        top_bar_layout.addWidget(user_badge)

        content_layout.addWidget(top_bar)

        # Container for pages (Stacked Widget)
        self.page_container = QStackedWidget()
        content_layout.addWidget(self.page_container)

        root_layout.addWidget(content_area)

        # Show Initial Page
        self.show_page("home", add_history=False)

    def create_nav_button(self, text, command, parent_layout):
        btn = QPushButton(text)
        btn.setProperty("btnStyle", "nav")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(40)
        btn.clicked.connect(command)
        parent_layout.addWidget(btn)
        return btn

    def update_nav_active(self, current_page):
        for page_key, btn in self.nav_buttons.items():
            is_active = (page_key == current_page)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def show_page(self, page, add_history=True):
        is_admin = (self.current_user.get("role") in ["Administrator", "Admin", "admin"])
        if not is_admin and page in ["faculty", "subjects", "classrooms", "classes", "assignments", "generate"]:
            page = "home"

        if add_history:
            if self.history[self.history_index] != page:
                self.history = self.history[:self.history_index + 1]
                self.history.append(page)
                self.history_index += 1

        titles = {
            "home": "Homepage",
            "faculty": "Faculty Management",
            "subjects": "Subject Management",
            "classrooms": "Classroom Management",
            "classes": "Classes & Semesters",
            "assignments": "Faculty Workload Management",
            "generate": "Generate Timetable",
            "view_timetable": "View Timetable",
            "settings": "System & Application Settings",
        }
        self.lbl_page_title.setText(titles.get(page, "Homepage"))
        self.update_nav_active(page)

        # Clear existing page inside page_container and construct new widget
        while self.page_container.count() > 0:
            w = self.page_container.widget(0)
            self.page_container.removeWidget(w)
            w.deleteLater()

        if page == "home":
            new_widget = self.build_home_page()
        elif page == "faculty":
            new_widget = FacultyWindow(parent=self, navigate=self.show_page)
        elif page == "subjects":
            new_widget = SubjectsWindow(parent=self)
        elif page == "classrooms":
            new_widget = ClassroomsWindow(parent=self)
        elif page == "classes":
            new_widget = ClassesWindow(parent=self)
        elif page == "assignments":
            new_widget = AssignmentsWindow(parent=self)
        elif page == "generate":
            new_widget = GenerateTimetableWindow(parent=self, navigate=self.show_page)
        elif page == "view_timetable":
            is_faculty = (self.current_user.get("role") == "Faculty")
            new_widget = ViewTimetableWindow(parent=self, faculty_user=self.current_user if is_faculty else None)
        else:
            new_widget = self.build_settings_page()

        self.page_container.addWidget(new_widget)
        self.page_container.setCurrentWidget(new_widget)

        self.btn_back.setEnabled(self.history_index > 0)
        self.btn_forward.setEnabled(self.history_index < len(self.history) - 1)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.show_page(self.history[self.history_index], add_history=False)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.show_page(self.history[self.history_index], add_history=False)

    # =====================================================
    # HOMEPAGE BUILDER
    # =====================================================
    def build_home_page(self):
        is_faculty = (self.current_user.get("role") == "Faculty")
        if is_faculty:
            return self.build_faculty_home()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("ScrollContent")
        content.setMinimumWidth(850)
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 30, 35, 35)
        layout.setSpacing(25)

        # Welcome banner
        banner = QFrame()
        banner.setObjectName("Card")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(25, 20, 25, 20)
        banner_layout.setSpacing(4)

        lbl_greet = QLabel("Good Day")
        lbl_greet.setObjectName("Heading")
        lbl_sub = QLabel("Manage your college academic timetable and schedules efficiently from one central dashboard.")
        lbl_sub.setObjectName("Secondary")

        banner_layout.addWidget(lbl_greet)
        banner_layout.addWidget(lbl_sub)
        layout.addWidget(banner)

        # Quick Actions
        lbl_qa = QLabel("Quick Actions")
        lbl_qa.setObjectName("SectionTitle")
        layout.addWidget(lbl_qa)

        qa_layout = QHBoxLayout()
        qa_layout.setSpacing(16)

        qa_layout.addWidget(self.create_action_card(
            "Generate Timetable",
            "Automatically solve and generate a conflict-free schedule.",
            "Generate",
            lambda: self.show_page("generate")
        ))
        qa_layout.addWidget(self.create_action_card(
            "Manage Faculty",
            "Add faculty profiles, qualifications, and max hours.",
            "Faculty",
            lambda: self.show_page("faculty")
        ))
        qa_layout.addWidget(self.create_action_card(
            "Manage Subjects",
            "Create curriculum subjects, credits, and lab requirements.",
            "Subjects",
            lambda: self.show_page("subjects")
        ))

        layout.addLayout(qa_layout)

        # Academic Overview Stats
        stats_header_layout = QHBoxLayout()
        lbl_stats = QLabel("Academic Overview")
        lbl_stats.setObjectName("SectionTitle")
        stats_header_layout.addWidget(lbl_stats)
        stats_header_layout.addStretch()

        btn_refresh = QPushButton("Refresh Overview")
        btn_refresh.setProperty("btnStyle", "secondary")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.refresh_stats)
        stats_header_layout.addWidget(btn_refresh)
        layout.addLayout(stats_header_layout)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        stats_grid.setColumnStretch(0, 1)
        stats_grid.setColumnStretch(1, 1)
        stats_grid.setColumnStretch(2, 1)
        stats_grid.setColumnStretch(3, 1)

        self.stat_labels["faculty"] = self.create_stat_card("Faculty Members", "0", 0, 0, stats_grid)
        self.stat_labels["subjects"] = self.create_stat_card("Curriculum Subjects", "0", 0, 1, stats_grid)
        self.stat_labels["classrooms"] = self.create_stat_card("Available Classrooms", "0", 0, 2, stats_grid)
        self.stat_labels["timetables"] = self.create_stat_card("Active Timetable Slots", "0", 0, 3, stats_grid)

        layout.addLayout(stats_grid)

        # Recent Timetables card
        recent_card = QFrame()
        recent_card.setObjectName("Card")
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(25, 20, 25, 20)
        recent_layout.setSpacing(8)

        lbl_rec_title = QLabel("System Timetable Status")
        lbl_rec_title.setObjectName("Subheading")
        recent_layout.addWidget(lbl_rec_title)

        self.lbl_recent_status = QLabel("Loading timetable status...")
        self.lbl_recent_status.setObjectName("NoticeText")
        recent_layout.addWidget(self.lbl_recent_status)

        layout.addWidget(recent_card)
        layout.addStretch()

        # Populate stats
        self.refresh_stats()

        return scroll

    def create_action_card(self, title, desc, btn_text, command):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        t = QLabel(title)
        t.setObjectName("Subheading")
        card_layout.addWidget(t)

        d = QLabel(desc)
        d.setWordWrap(True)
        d.setObjectName("Secondary")
        card_layout.addWidget(d)
        card_layout.addStretch()

        b = QPushButton(btn_text)
        b.setProperty("btnStyle", "primary")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(command)
        card_layout.addWidget(b, 0, Qt.AlignmentFlag.AlignLeft)

        return card

    def create_stat_card(self, title, init_val, row, col, grid):
        card = QFrame()
        card.setObjectName("MetricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(4)

        v = QLabel(init_val)
        v.setObjectName("MetricValue")
        t = QLabel(title)
        t.setObjectName("MetricLabel")

        card_layout.addWidget(v)
        card_layout.addWidget(t)
        grid.addWidget(card, row, col)
        return v

    def refresh_stats(self):
        try:
            conn = get_connection()
            cursor = conn.execute("""
                SELECT
                    (SELECT COUNT(*) FROM faculty),
                    (SELECT COUNT(*) FROM subjects),
                    (SELECT COUNT(*) FROM classrooms),
                    (SELECT COUNT(*) FROM timetable)
            """)
            row = cursor.fetchone()
            conn.close()
            f_count, s_count, c_count, t_count = row if row else (0, 0, 0, 0)
        except Exception:
            f_count = s_count = c_count = t_count = 0

        if "faculty" in self.stat_labels:
            self.stat_labels["faculty"].setText(str(f_count))
        if "subjects" in self.stat_labels:
            self.stat_labels["subjects"].setText(str(s_count))
        if "classrooms" in self.stat_labels:
            self.stat_labels["classrooms"].setText(str(c_count))
        if "timetables" in self.stat_labels:
            self.stat_labels["timetables"].setText(str(t_count))

        if hasattr(self, "lbl_recent_status"):
            if t_count > 0:
                self.lbl_recent_status.setText(f"{t_count} scheduled timetable slots are currently active in the database. You can view, filter, and export the timetable from the View Timetable section.")
            else:
                self.lbl_recent_status.setText("No timetables generated yet. Go to Generate Timetable to create full college schedules.")

    def build_faculty_home(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("ScrollContent")
        content.setMinimumWidth(850)
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 30, 35, 35)
        layout.setSpacing(25)

        display_name = self.current_user.get("full_name") or self.current_user.get("username", "Faculty")

        banner = QFrame()
        banner.setObjectName("Card")
        b_layout = QVBoxLayout(banner)
        b_layout.setContentsMargins(25, 20, 25, 20)
        b_layout.setSpacing(6)

        t = QLabel(f"Welcome, {display_name}")
        t.setObjectName("Heading")
        sub = QLabel("Faculty Academic Portal • View your allocated classes, lecture slots, and teaching schedules.")
        sub.setObjectName("Secondary")

        b_layout.addWidget(t)
        b_layout.addWidget(sub)
        layout.addWidget(banner)

        # My Timetable Card
        tt_card = QFrame()
        tt_card.setObjectName("Card")
        tt_layout = QVBoxLayout(tt_card)
        tt_layout.setContentsMargins(25, 20, 25, 20)
        tt_layout.setSpacing(12)

        tt_title = QLabel("My Weekly Teaching Schedule")
        tt_title.setObjectName("Subheading")
        tt_desc = QLabel("Access your weekly lecture schedule with subject codes, allocated classrooms, and time slots.")
        tt_desc.setObjectName("Secondary")

        btn_open = QPushButton("Open My Timetable")
        btn_open.setProperty("btnStyle", "primary")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setMinimumHeight(40)
        btn_open.clicked.connect(lambda: self.show_page("view_timetable"))

        tt_layout.addWidget(tt_title)
        tt_layout.addWidget(tt_desc)
        tt_layout.addWidget(btn_open, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(tt_card)

        # Guidelines Card
        guide_card = QFrame()
        guide_card.setObjectName("Card")
        g_layout = QVBoxLayout(guide_card)
        g_layout.setContentsMargins(25, 20, 25, 20)
        g_layout.setSpacing(10)

        g_title = QLabel("Faculty Guidelines & Notice")
        g_title.setObjectName("Subheading")
        g_text = QLabel(
            "• Timetables are generated and managed centrally by the Academic Administrator.\n"
            "• You can download and print a structured PDF of your weekly schedule directly from the timetable page.\n"
            "• For schedule adjustments, subject changes, or classroom reassignment, please contact the Administrator."
        )
        g_text.setObjectName("NoticeText")

        g_layout.addWidget(g_title)
        g_layout.addWidget(g_text)
        layout.addWidget(guide_card)
        layout.addStretch()

        return scroll

    # =====================================================
    # SETTINGS PAGE
    # =====================================================
    def build_settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("ScrollContent")
        content.setMinimumWidth(850)
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 30, 35, 35)
        layout.setSpacing(20)

        # 1. Theme Card
        theme_card = QFrame()
        theme_card.setObjectName("Card")
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setContentsMargins(25, 20, 25, 20)
        theme_layout.setSpacing(12)

        lbl_t = QLabel("Theme & Appearance (Dark / Light Mode)")
        lbl_t.setObjectName("Subheading")
        lbl_ts = QLabel("Switch between Light, Dark, or System mode across the entire application instantly.")
        lbl_ts.setObjectName("Secondary")

        theme_layout.addWidget(lbl_t)
        theme_layout.addWidget(lbl_ts)

        theme_btn_layout = QHBoxLayout()
        theme_btn_layout.setSpacing(10)
        current_theme = get_app_setting("appearance_mode", "Light")

        for m in ["Light", "Dark", "System"]:
            b = QPushButton(m)
            b.setProperty("btnStyle", "primary" if m == current_theme else "secondary")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda checked=False, mode=m: self.change_theme(mode))
            theme_btn_layout.addWidget(b)

        theme_btn_layout.addStretch()
        theme_layout.addLayout(theme_btn_layout)
        layout.addWidget(theme_card)

        # 2. Scaling Card
        scale_card = QFrame()
        scale_card.setObjectName("Card")
        scale_layout = QVBoxLayout(scale_card)
        scale_layout.setContentsMargins(25, 20, 25, 20)
        scale_layout.setSpacing(12)

        lbl_s = QLabel("Text Size & Interface Scaling")
        lbl_s.setObjectName("Subheading")
        lbl_ss = QLabel("Adjust text and element sizes program-wide for comfortable viewing.")
        lbl_ss.setObjectName("Secondary")

        scale_layout.addWidget(lbl_s)
        scale_layout.addWidget(lbl_ss)

        scale_btn_layout = QHBoxLayout()
        scale_btn_layout.setSpacing(10)
        current_scale = get_app_setting("ui_scaling", "100%")

        for sc in ["80%", "90%", "100%", "110%", "120%"]:
            b = QPushButton(sc)
            b.setProperty("btnStyle", "primary" if sc == current_scale else "secondary")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda checked=False, scale=sc: self.change_scaling(scale))
            scale_btn_layout.addWidget(b)

        scale_btn_layout.addStretch()
        scale_layout.addLayout(scale_btn_layout)
        layout.addWidget(scale_card)

        # 3. Account Card
        acc_card = QFrame()
        acc_card.setObjectName("Card")
        acc_layout = QVBoxLayout(acc_card)
        acc_layout.setContentsMargins(25, 20, 25, 20)
        acc_layout.setSpacing(12)

        lbl_a = QLabel("User Account & Security")
        lbl_a.setObjectName("Subheading")
        acc_layout.addWidget(lbl_a)

        display_name = self.current_user.get("full_name") or self.current_user.get("username", "Administrator")
        info_text = QLabel(f"• Active Account: {display_name} ({self.current_user.get('role', 'Faculty')})\n• Security: Salted PBKDF2 Password Encryption (SHA-256, 100,000 rounds)")
        info_text.setObjectName("NoticeText")
        acc_layout.addWidget(info_text)

        btn_logout = QPushButton("Log Out of Account")
        btn_logout.setProperty("btnStyle", "danger")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setMinimumHeight(38)
        btn_logout.clicked.connect(self.confirm_logout)
        acc_layout.addWidget(btn_logout, 0, Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(acc_card)
        layout.addStretch()

        return scroll

    def change_theme(self, mode):
        set_app_setting("appearance_mode", mode)
        apply_theme(mode=mode)
        self.show_page("settings", add_history=False)

    def change_scaling(self, scale_str):
        set_app_setting("ui_scaling", scale_str)
        apply_scaling(scale_str=scale_str)
        self.show_page("settings", add_history=False)

    def confirm_logout(self):
        confirm = QMessageBox.question(
            self,
            "Logout Confirmation",
            "Are you sure you want to log out of your session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            from ui.login import LoginWindow
            from main import open_dashboard
            self.login_window = LoginWindow(on_login_success=open_dashboard)
            self.login_window.show()
            self.close()

    def run(self):
        self.show()


if __name__ == "__main__":
    from database.database import create_tables
    create_tables()

    app = QApplication.instance() or QApplication(sys.argv)
    apply_theme()
    d = Dashboard()
    d.show()
    sys.exit(app.exec())
