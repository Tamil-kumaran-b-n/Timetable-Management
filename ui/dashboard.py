import customtkinter as ctk

from ui.faculty import FacultyWindow
from ui.subjects import SubjectsWindow
from ui.classrooms import ClassroomsWindow
from ui.classes import ClassesWindow
from ui.generate import GenerateTimetableWindow
from ui.view_timetable import ViewTimetableWindow
from ui.assignments import AssignmentsWindow

from database.database import (
    get_all_faculty,
    get_all_subjects,
    get_all_classrooms
)

from database.generator import (
    get_all_timetable
)


class Dashboard:

    def __init__(self):

        self.window = ctk.CTk()

        self.window.title(
            "Homepage - Smart Academic Timetable Management System"
        )

        self.window.geometry(
            "1200x700"
        )

        self.window.minsize(
            1000,
            600
        )

        # Browser-style history for pages rendered in the dashboard.
        self.history = ["home"]
        self.history_index = 0

        # ====================================================
        # STATISTIC LABELS
        # ====================================================

        self.stat_value_labels = {}

        # ====================================================
        # LIGHT THEME
        # ====================================================

        ctk.set_appearance_mode(
            "Light"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ====================================================
        # CREATE DASHBOARD
        # ====================================================

        self.create_dashboard()

        # ====================================================
        # AUTOMATIC REFRESH
        # ====================================================

        self.window.bind(
            "<FocusIn>",
            self.on_dashboard_focus
        )

    # ========================================================
    # CREATE DASHBOARD
    # ========================================================

    def create_dashboard(self):

        # ====================================================
        # MAIN CONTAINER
        # ====================================================

        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#F5F7FA",
            corner_radius=0
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = ctk.CTkFrame(
            main_frame,
            width=240,
            fg_color="#FFFFFF",
            corner_radius=0
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(
            False
        )

        # ====================================================
        # APPLICATION TITLE
        # ====================================================

        app_title = ctk.CTkLabel(
            sidebar,
            text="SMART\nTIMETABLE",
            font=(
                "Arial",
                22,
                "bold"
            ),
            text_color="#1F2937"
        )

        app_title.pack(
            pady=(35, 40)
        )

        # ====================================================
        # MAIN MENU
        # ====================================================

        nav_label = ctk.CTkLabel(
            sidebar,
            text="MAIN MENU",
            font=(
                "Arial",
                11,
                "bold"
            ),
            text_color="#9CA3AF"
        )

        nav_label.pack(
            anchor="w",
            padx=25,
            pady=(0, 12)
        )

        # ====================================================
        # NAVIGATION
        # ====================================================

        self.create_nav_button(
            sidebar,
            "⌂   Home",
            self.home_clicked
        )

        self.create_nav_button(
            sidebar,
            "▣   Faculty",
            self.faculty_clicked
        )

        self.create_nav_button(
            sidebar,
            "▤   Subjects",
            self.subjects_clicked
        )

        self.create_nav_button(
            sidebar,
            "▥   Classrooms",
            self.classrooms_clicked
        )

        self.create_nav_button(
            sidebar,
            "◈   Classes & Semesters",
            self.classes_clicked
        )

        self.create_nav_button(
            sidebar,
            "▦   Generate Timetable",
            self.generate_clicked
        )

        self.create_nav_button(
            sidebar,
            "☷   View Timetable",
            self.view_timetable_clicked
        )

        # ====================================================
        # SETTINGS
        # ====================================================

        settings_button = ctk.CTkButton(
            sidebar,
            text="⚙   Settings",
            height=40,
            fg_color="transparent",
            hover_color="#EAF2FF",
            text_color="#374151",
            anchor="w",
            command=self.settings_clicked
        )

        settings_button.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=(5, 20)
        )

        # ====================================================
        # CONTENT AREA
        # ====================================================

        content = ctk.CTkFrame(
            main_frame,
            fg_color="#F5F7FA",
            corner_radius=0
        )

        content.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ====================================================
        # TOP BAR
        # ====================================================

        top_bar = ctk.CTkFrame(
            content,
            height=75,
            fg_color="#FFFFFF",
            corner_radius=0
        )

        top_bar.pack(
            fill="x"
        )

        top_bar.pack_propagate(
            False
        )

        self.back_button = ctk.CTkButton(
            top_bar,
            text="←",
            width=36,
            height=32,
            state="disabled",
            command=self.go_back
        )
        self.back_button.pack(side="left", padx=(20, 6))

        self.forward_button = ctk.CTkButton(
            top_bar,
            text="→",
            width=36,
            height=32,
            state="disabled",
            command=self.go_forward
        )
        self.forward_button.pack(side="left", padx=(0, 16))

        self.page_title = ctk.CTkLabel(
            top_bar,
            text="Homepage",
            font=(
                "Arial",
                24,
                "bold"
            ),
            text_color="#111827"
        )

        self.page_title.pack(
            side="left",
            padx=30
        )

        user_label = ctk.CTkLabel(
            top_bar,
            text="Administrator",
            font=(
                "Arial",
                14,
                "bold"
            ),
            text_color="#374151"
        )

        user_label.pack(
            side="right",
            padx=30
        )

        # ====================================================
        # DASHBOARD CONTENT
        # ====================================================

        self.page_container = ctk.CTkFrame(
            content,
            fg_color="#F5F7FA",
            corner_radius=0
        )

        self.page_container.pack(
            fill="both",
            expand=True
        )

        self.show_page("home", add_history=False)

    def build_homepage(self):

        dashboard_content = ctk.CTkScrollableFrame(
            self.page_container,
            fg_color="#F5F7FA"
        )

        dashboard_content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ====================================================
        # WELCOME
        # ====================================================

        welcome_title = ctk.CTkLabel(
            dashboard_content,
            text="Good Evening 👋",
            font=(
                "Arial",
                26,
                "bold"
            ),
            text_color="#111827"
        )

        welcome_title.pack(
            anchor="w",
            padx=10,
            pady=(5, 5)
        )

        welcome_text = ctk.CTkLabel(
            dashboard_content,
            text=(
                "Manage your academic timetable efficiently "
                "from one place."
            ),
            font=(
                "Arial",
                14
            ),
            text_color="#6B7280"
        )

        welcome_text.pack(
            anchor="w",
            padx=10,
            pady=(0, 25)
        )

        # ====================================================
        # QUICK ACTIONS
        # ====================================================

        quick_title = ctk.CTkLabel(
            dashboard_content,
            text="Quick Actions",
            font=(
                "Arial",
                19,
                "bold"
            ),
            text_color="#111827"
        )

        quick_title.pack(
            anchor="w",
            padx=10,
            pady=(0, 15)
        )

        cards_frame = ctk.CTkFrame(
            dashboard_content,
            fg_color="transparent"
        )

        cards_frame.pack(
            fill="x",
            padx=10
        )

        # Generate

        self.create_card(
            cards_frame,
            "Generate Timetable",
            "Automatically create a conflict-free timetable.",
            "Generate",
            self.generate_clicked,
            0
        )

        # Faculty

        self.create_card(
            cards_frame,
            "Manage Faculty",
            "Add and manage faculty information.",
            "Faculty",
            self.faculty_clicked,
            1
        )

        # Subjects

        self.create_card(
            cards_frame,
            "Manage Subjects",
            "Add subjects and assign faculty.",
            "Subjects",
            self.subjects_clicked,
            2
        )

        # ====================================================
        # ACADEMIC OVERVIEW
        # ====================================================

        stats_title = ctk.CTkLabel(
            dashboard_content,
            text="Academic Overview",
            font=(
                "Arial",
                19,
                "bold"
            ),
            text_color="#111827"
        )

        stats_title.pack(
            anchor="w",
            padx=10,
            pady=(35, 15)
        )

        # ====================================================
        # STATISTICS FRAME
        # ====================================================

        stats_frame = ctk.CTkFrame(
            dashboard_content,
            fg_color="transparent"
        )

        stats_frame.pack(
            fill="x",
            padx=10
        )

        # Allow cards to expand evenly

        for column in range(4):

            stats_frame.grid_columnconfigure(
                column,
                weight=1
            )

        # ====================================================
        # STAT CARDS
        # ====================================================

        self.create_stat(
            stats_frame,
            "Faculty",
            0,
            0
        )

        self.create_stat(
            stats_frame,
            "Subjects",
            0,
            1
        )

        self.create_stat(
            stats_frame,
            "Classrooms",
            0,
            2
        )

        self.create_stat(
            stats_frame,
            "Timetables",
            0,
            3
        )

        # ====================================================
        # REFRESH BUTTON
        # ====================================================

        refresh_frame = ctk.CTkFrame(
            dashboard_content,
            fg_color="transparent"
        )

        refresh_frame.pack(
            fill="x",
            padx=10,
            pady=(12, 0)
        )

        refresh_button = ctk.CTkButton(
            refresh_frame,
            text="↻  Refresh Overview",
            width=150,
            height=34,
            corner_radius=7,
            command=self.refresh_dashboard
        )

        refresh_button.pack(
            anchor="e"
        )

        # ====================================================
        # RECENT TIMETABLES
        # ====================================================

        recent_title = ctk.CTkLabel(
            dashboard_content,
            text="Recent Timetables",
            font=(
                "Arial",
                19,
                "bold"
            ),
            text_color="#111827"
        )

        recent_title.pack(
            anchor="w",
            padx=10,
            pady=(35, 15)
        )

        self.recent_box = ctk.CTkFrame(
            dashboard_content,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        self.recent_box.pack(
            fill="x",
            padx=10,
            pady=(0, 20)
        )

        # ====================================================
        # FIRST LOAD
        # ====================================================

        self.refresh_dashboard()

    # ========================================================
    # NAVIGATION BUTTON
    # ========================================================

    def create_nav_button(
        self,
        parent,
        text,
        command
    ):

        button = ctk.CTkButton(
            parent,
            text=text,
            height=42,
            fg_color="transparent",
            hover_color="#EAF2FF",
            text_color="#374151",
            anchor="w",
            font=(
                "Arial",
                13
            ),
            command=command
        )

        button.pack(
            fill="x",
            padx=15,
            pady=3
        )

    # ========================================================
    # QUICK ACTION CARD
    # ========================================================

    def create_card(
        self,
        parent,
        title,
        description,
        button_text,
        command,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            width=280,
            height=145,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        card.grid(
            row=0,
            column=column,
            padx=8,
            sticky="nsew"
        )

        card.grid_propagate(
            False
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=(
                "Arial",
                17,
                "bold"
            ),
            text_color="#111827"
        )

        title_label.pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        description_label = ctk.CTkLabel(
            card,
            text=description,
            font=(
                "Arial",
                12
            ),
            text_color="#6B7280",
            wraplength=235,
            justify="left"
        )

        description_label.pack(
            anchor="w",
            padx=20
        )

        action_button = ctk.CTkButton(
            card,
            text=button_text,
            width=110,
            height=32,
            command=command
        )

        action_button.pack(
            anchor="w",
            padx=20,
            pady=12
        )

    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat(
        self,
        parent,
        title,
        value,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            height=100,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        card.grid(
            row=0,
            column=column,
            padx=8,
            sticky="nsew"
        )

        card.grid_propagate(
            False
        )

        # Store value label

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=(
                "Arial",
                25,
                "bold"
            ),
            text_color="#2563EB"
        )

        value_label.pack(
            pady=(18, 0)
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=(
                "Arial",
                12
            ),
            text_color="#6B7280"
        )

        title_label.pack()

        # Store reference

        self.stat_value_labels[
            title.lower()
        ] = value_label

    # ========================================================
    # REFRESH DASHBOARD STATISTICS
    # ========================================================

    def refresh_dashboard(self):

        # ====================================================
        # FACULTY COUNT
        # ====================================================

        try:

            faculty_records = get_all_faculty()

            faculty_count = len(
                faculty_records
            )

        except Exception:

            faculty_count = 0

        # ====================================================
        # SUBJECT COUNT
        # ====================================================

        try:

            subject_records = get_all_subjects()

            subject_count = len(
                subject_records
            )

        except Exception:

            subject_count = 0

        # ====================================================
        # CLASSROOM COUNT
        # ====================================================

        try:

            classroom_records = get_all_classrooms()

            classroom_count = len(
                classroom_records
            )

        except Exception:

            classroom_count = 0

        # ====================================================
        # TIMETABLE COUNT
        # ====================================================

        try:

            timetable_records = get_all_timetable()

            timetable_count = len(
                timetable_records
            )

        except Exception:

            timetable_count = 0

        # ====================================================
        # UPDATE LABELS
        # ====================================================

        if "faculty" in self.stat_value_labels:

            self.stat_value_labels[
                "faculty"
            ].configure(
                text=str(
                    faculty_count
                )
            )

        if "subjects" in self.stat_value_labels:

            self.stat_value_labels[
                "subjects"
            ].configure(
                text=str(
                    subject_count
                )
            )

        if "classrooms" in self.stat_value_labels:

            self.stat_value_labels[
                "classrooms"
            ].configure(
                text=str(
                    classroom_count
                )
            )

        if "timetables" in self.stat_value_labels:

            self.stat_value_labels[
                "timetables"
            ].configure(
                text=str(
                    timetable_count
                )
            )

        # ====================================================
        # UPDATE RECENT TIMETABLE SECTION
        # ====================================================

        self.refresh_recent_timetables()

    # ========================================================
    # RECENT TIMETABLES
    # ========================================================

    def refresh_recent_timetables(self):

        if not hasattr(
            self,
            "recent_box"
        ):

            return

        # Clear old content

        for widget in (
            self.recent_box
            .winfo_children()
        ):

            widget.destroy()

        try:

            timetable_records = get_all_timetable()

        except Exception:

            timetable_records = []

        # ====================================================
        # NO TIMETABLE
        # ====================================================

        if not timetable_records:

            no_data = ctk.CTkLabel(
                self.recent_box,
                text="No timetables generated yet.",
                font=(
                    "Arial",
                    14
                ),
                text_color="#9CA3AF"
            )

            no_data.pack(
                pady=35
            )

            return

        # ====================================================
        # TIMETABLE EXISTS
        # ====================================================

        info = ctk.CTkLabel(
            self.recent_box,
            text=(
                f"{len(timetable_records)} "
                f"timetable entries are currently generated."
            ),
            font=(
                "Arial",
                14
            ),
            text_color="#374151"
        )

        info.pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        # Show a small status line

        status = ctk.CTkLabel(
            self.recent_box,
            text=(
                "The generated timetable is available "
                "from the View Timetable section."
            ),
            font=(
                "Arial",
                12
            ),
            text_color="#6B7280"
        )

        status.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    # ========================================================
    # DASHBOARD FOCUS
    # ========================================================

    def on_dashboard_focus(
        self,
        event=None
    ):

        try:

            self.refresh_dashboard()

        except Exception:

            pass

    # ========================================================
    # STATUS WINDOW
    # ========================================================

    def _show_status(
        self,
        title,
        message
    ):

        status_window = ctk.CTkToplevel(
            self.window
        )

        status_window.title(
            title
        )

        status_window.geometry(
            "420x180"
        )

        status_window.resizable(
            False,
            False
        )

        status_window.transient(
            self.window
        )

        ctk.CTkLabel(
            status_window,
            text=title,
            font=(
                "Arial",
                18,
                "bold"
            )
        ).pack(
            pady=(30, 10)
        )

        ctk.CTkLabel(
            status_window,
            text=message,
            font=(
                "Arial",
                13
            ),
            wraplength=360
        ).pack(
            pady=(0, 20)
        )

        ctk.CTkButton(
            status_window,
            text="OK",
            width=90,
            command=status_window.destroy
        ).pack()

    # ========================================================
    # HOME
    # ========================================================

    def home_clicked(self):
        self.show_page("home")

    # ========================================================
    # FACULTY
    # ========================================================

    def faculty_clicked(self):
        self.show_page("faculty")

    # ========================================================
    # SUBJECTS
    # ========================================================

    def subjects_clicked(self):
        self.show_page("subjects")

    # ========================================================
    # CLASSROOMS
    # ========================================================

    def classrooms_clicked(self):
        self.show_page("classrooms")

    # ========================================================
    # CLASSES & SEMESTERS
    # ========================================================

    def classes_clicked(self):
        self.show_page("classes")

    # ========================================================
    # GENERATE TIMETABLE
    # ========================================================

    def generate_clicked(self):
        self.show_page("generate")

    # ========================================================
    # VIEW TIMETABLE
    # ========================================================

    def view_timetable_clicked(self):
        self.show_page("view_timetable")

    # ========================================================
    # SETTINGS
    # ========================================================

    def settings_clicked(self):
        self.show_page("settings")

    # ========================================================
    # IN-PLACE PAGE NAVIGATION
    # ========================================================

    def show_page(self, page, add_history=True):
        if add_history:
            if self.history[self.history_index] == page:
                return
            self.history = self.history[:self.history_index + 1]
            self.history.append(page)
            self.history_index += 1

        for child in self.page_container.winfo_children():
            child.destroy()

        titles = {
            "home": "Homepage",
            "faculty": "Faculty Management",
            "subjects": "Subject Management",
            "classrooms": "Classroom Management",
            "classes": "Classes & Semesters",
            "assignments": "Faculty Workload Management",
            "generate": "Generate Timetable",
            "view_timetable": "View Timetable",
            "settings": "Settings",
        }
        self.page_title.configure(text=titles[page])

        if page == "home":
            self.build_homepage()
        elif page == "faculty":
            FacultyWindow(self.window, container=self.page_container,
                          navigate=self.show_page)
        elif page == "subjects":
            SubjectsWindow(self.window, container=self.page_container)
        elif page == "classrooms":
            ClassroomsWindow(self.window, container=self.page_container)
        elif page == "classes":
            ClassesWindow(self.window, container=self.page_container)
        elif page == "assignments":
            AssignmentsWindow(self.window, container=self.page_container)
        elif page == "generate":
            GenerateTimetableWindow(self.window, container=self.page_container,
                                    navigate=self.show_page)
        elif page == "view_timetable":
            ViewTimetableWindow(self.window, container=self.page_container)
        else:
            self.build_settings_page()

        self.update_navigation_buttons()

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.show_page(self.history[self.history_index], add_history=False)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.show_page(self.history[self.history_index], add_history=False)

    def update_navigation_buttons(self):
        self.back_button.configure(
            state="normal" if self.history_index > 0 else "disabled"
        )
        self.forward_button.configure(
            state=("normal" if self.history_index < len(self.history) - 1
                   else "disabled")
        )

    def build_settings_page(self):
        page = ctk.CTkFrame(self.page_container, fg_color="#F5F7FA")
        page.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(
            page,
            text="Settings",
            font=("Arial", 26, "bold"),
            text_color="#111827"
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            page,
            text="Application settings will be available here.",
            font=("Arial", 14),
            text_color="#6B7280"
        ).pack(anchor="w")

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        self.window.mainloop()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    dashboard = Dashboard()

    dashboard.run()
