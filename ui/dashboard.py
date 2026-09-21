import customtkinter as ctk
from datetime import datetime

from ui.faculty import FacultyWindow
from ui.subjects import SubjectsWindow
from ui.classrooms import ClassroomsWindow
from ui.classes import ClassesWindow
from ui.generate import GenerateTimetableWindow
from ui.view_timetable import ViewTimetableWindow


class Dashboard:

    def __init__(self):

        self.window = ctk.CTk()

        self.window.title(
            "Homepage - Smart Academic Timetable Management System"
        )

        self.window.geometry("1200x700")
        self.window.minsize(1000, 600)

        # =========================
        # CHILD WINDOWS
        # =========================

        self.faculty_window = None
        self.subjects_window = None
        self.classrooms_window = None
        self.classes_window = None
        self.generate_window = None
        self.view_timetable_window = None

        # =========================
        # LIGHT THEME
        # =========================

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.create_dashboard()

    # =====================================================
    # CREATE HOMEPAGE
    # =====================================================

    def create_dashboard(self):

        # =========================
        # MAIN CONTAINER
        # =========================

        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#F5F7FA",
            corner_radius=0
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        # =========================
        # SIDEBAR
        # =========================

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

        sidebar.pack_propagate(False)

        # =========================
        # APPLICATION TITLE
        # =========================

        app_title = ctk.CTkLabel(
            sidebar,
            text="SMART\nTIMETABLE",
            font=("Arial", 22, "bold"),
            text_color="#1F2937"
        )

        app_title.pack(
            pady=(35, 40)
        )

        # =========================
        # MAIN MENU
        # =========================

        nav_label = ctk.CTkLabel(
            sidebar,
            text="MAIN MENU",
            font=("Arial", 11, "bold"),
            text_color="#9CA3AF"
        )

        nav_label.pack(
            anchor="w",
            padx=25,
            pady=(0, 12)
        )

        # =========================
        # NAVIGATION BUTTONS
        # =========================

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

        # =========================
        # SETTINGS
        # =========================

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

        # =========================
        # CONTENT AREA
        # =========================

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

        # =========================
        # TOP BAR
        # =========================

        top_bar = ctk.CTkFrame(
            content,
            height=75,
            fg_color="#FFFFFF",
            corner_radius=0
        )

        top_bar.pack(
            fill="x"
        )

        top_bar.pack_propagate(False)

        # =========================
        # PAGE TITLE
        # =========================

        page_title = ctk.CTkLabel(
            top_bar,
            text="Homepage",
            font=("Arial", 24, "bold"),
            text_color="#111827"
        )

        page_title.pack(
            side="left",
            padx=30
        )

        # =========================
        # USER LABEL
        # =========================

        user_label = ctk.CTkLabel(
            top_bar,
            text="Administrator",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        )

        user_label.pack(
            side="right",
            padx=30
        )

        # =========================
        # HOMEPAGE CONTENT
        # =========================

        homepage_content = ctk.CTkScrollableFrame(
            content,
            fg_color="#F5F7FA"
        )

        homepage_content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # =================================================
        # GREETING FRAME
        # =================================================

        greeting_frame = ctk.CTkFrame(
            homepage_content,
            fg_color="transparent"
        )

        greeting_frame.pack(
            anchor="w",
            padx=10,
            pady=(5, 0)
        )

        # =========================
        # DYNAMIC GREETING
        # =========================

        self.welcome_title = ctk.CTkLabel(
            greeting_frame,
            text="",
            font=("Arial", 26, "bold"),
            text_color="#111827"
        )

        self.welcome_title.pack(
            side="left"
        )

        # =========================
        # GREETING EMOJI
        # =========================

        self.greeting_emoji = ctk.CTkLabel(
            greeting_frame,
            text="",
            font=("Segoe UI Emoji", 22),
            text_color="#111827"
        )

        self.greeting_emoji.pack(
            side="left",
            padx=(10, 0)
        )

        # =========================
        # START GREETING UPDATE
        # =========================

        self.update_greeting()

        # =========================
        # WELCOME TEXT
        # =========================

        welcome_text = ctk.CTkLabel(
            homepage_content,
            text=(
                "Manage your academic timetable efficiently "
                "from one place."
            ),
            font=("Arial", 14),
            text_color="#6B7280"
        )

        welcome_text.pack(
            anchor="w",
            padx=10,
            pady=(5, 25)
        )

        # =========================
        # QUICK ACTIONS
        # =========================

        quick_title = ctk.CTkLabel(
            homepage_content,
            text="Quick Actions",
            font=("Arial", 19, "bold"),
            text_color="#111827"
        )

        quick_title.pack(
            anchor="w",
            padx=10,
            pady=(0, 15)
        )

        cards_frame = ctk.CTkFrame(
            homepage_content,
            fg_color="transparent"
        )

        cards_frame.pack(
            fill="x",
            padx=10
        )

        # =========================
        # GENERATE CARD
        # =========================

        self.create_card(
            cards_frame,
            "Generate Timetable",
            "Automatically create a conflict-free timetable.",
            "Generate",
            self.generate_clicked,
            0
        )

        # =========================
        # FACULTY CARD
        # =========================

        self.create_card(
            cards_frame,
            "Manage Faculty",
            "Add and manage faculty information.",
            "Faculty",
            self.faculty_clicked,
            1
        )

        # =========================
        # SUBJECTS CARD
        # =========================

        self.create_card(
            cards_frame,
            "Manage Subjects",
            "Add subjects and assign faculty.",
            "Subjects",
            self.subjects_clicked,
            2
        )

        # =========================
        # ACADEMIC OVERVIEW
        # =========================

        stats_title = ctk.CTkLabel(
            homepage_content,
            text="Academic Overview",
            font=("Arial", 19, "bold"),
            text_color="#111827"
        )

        stats_title.pack(
            anchor="w",
            padx=10,
            pady=(35, 15)
        )

        stats_frame = ctk.CTkFrame(
            homepage_content,
            fg_color="transparent"
        )

        stats_frame.pack(
            fill="x",
            padx=10
        )

        self.create_stat(
            stats_frame,
            "Faculty",
            "0",
            0
        )

        self.create_stat(
            stats_frame,
            "Subjects",
            "0",
            1
        )

        self.create_stat(
            stats_frame,
            "Classrooms",
            "0",
            2
        )

        self.create_stat(
            stats_frame,
            "Timetables",
            "0",
            3
        )

        # =========================
        # RECENT TIMETABLES
        # =========================

        recent_title = ctk.CTkLabel(
            homepage_content,
            text="Recent Timetables",
            font=("Arial", 19, "bold"),
            text_color="#111827"
        )

        recent_title.pack(
            anchor="w",
            padx=10,
            pady=(35, 15)
        )

        recent_box = ctk.CTkFrame(
            homepage_content,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        recent_box.pack(
            fill="x",
            padx=10,
            pady=(0, 20)
        )

        no_data = ctk.CTkLabel(
            recent_box,
            text="No timetables generated yet.",
            font=("Arial", 14),
            text_color="#9CA3AF"
        )

        no_data.pack(
            pady=35
        )

    # =====================================================
    # DYNAMIC TIME GREETING
    # =====================================================

    def update_greeting(self):

        current_hour = datetime.now().hour

        # =================================================
        # 12:00 AM - 11:59 AM
        # =================================================

        if 0 <= current_hour < 12:

            greeting = "Good Morning"
            emoji = "🌅"

        # =================================================
        # 12:00 PM - 2:59 PM
        # =================================================

        elif 12 <= current_hour < 15:

            greeting = "Good Afternoon"
            emoji = "☀️"

        # =================================================
        # 3:00 PM - 8:59 PM
        # =================================================

        elif 15 <= current_hour < 21:

            greeting = "Good Evening"
            emoji = "🌆"

        # =================================================
        # 9:00 PM - 11:59 PM
        # =================================================

        else:

            greeting = "Good Night"
            emoji = "🌙"

        # =========================
        # UPDATE TEXT
        # =========================

        self.welcome_title.configure(
            text=greeting
        )

        # =========================
        # UPDATE EMOJI
        # =========================

        self.greeting_emoji.configure(
            text=emoji
        )

        # =========================
        # UPDATE EVERY 60 SECONDS
        # =========================

        self.window.after(
            60000,
            self.update_greeting
        )

    # =====================================================
    # NAVIGATION BUTTON
    # =====================================================

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
            font=("Arial", 13),
            command=command
        )

        button.pack(
            fill="x",
            padx=15,
            pady=3
        )

    # =====================================================
    # QUICK ACTION CARD
    # =====================================================

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
            height=175,
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

        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 17, "bold"),
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
            font=("Arial", 12),
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
            pady=15
        )

    # =====================================================
    # STAT CARD
    # =====================================================

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

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 25, "bold"),
            text_color="#2563EB"
        )

        value_label.pack(
            pady=(18, 0)
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12),
            text_color="#6B7280"
        )

        title_label.pack()

    # =====================================================
    # STATUS WINDOW
    # =====================================================

    def _show_status(
        self,
        title,
        message
    ):

        status_window = ctk.CTkToplevel(
            self.window
        )

        status_window.title(title)
        status_window.geometry("420x180")
        status_window.resizable(False, False)
        status_window.transient(self.window)

        ctk.CTkLabel(
            status_window,
            text=title,
            font=("Arial", 18, "bold")
        ).pack(
            pady=(30, 10)
        )

        ctk.CTkLabel(
            status_window,
            text=message,
            font=("Arial", 13),
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

    # =====================================================
    # HOME
    # =====================================================

    def home_clicked(self):

        self._show_status(
            "Homepage",
            "You are already viewing the homepage."
        )

    # =====================================================
    # FACULTY
    # =====================================================

    def faculty_clicked(self):

        if (
            self.faculty_window is None
            or not self.faculty_window.window.winfo_exists()
        ):

            self.faculty_window = FacultyWindow(
                self.window
            )

        else:

            self.faculty_window.window.deiconify()
            self.faculty_window.window.lift()
            self.faculty_window.window.focus_force()

    # =====================================================
    # SUBJECTS
    # =====================================================

    def subjects_clicked(self):

        if (
            self.subjects_window is None
            or not self.subjects_window.window.winfo_exists()
        ):

            self.subjects_window = SubjectsWindow(
                self.window
            )

        else:

            self.subjects_window.window.deiconify()
            self.subjects_window.window.lift()
            self.subjects_window.window.focus_force()

    # =====================================================
    # CLASSROOMS
    # =====================================================

    def classrooms_clicked(self):

        if (
            self.classrooms_window is None
            or not self.classrooms_window.window.winfo_exists()
        ):

            self.classrooms_window = ClassroomsWindow(
                self.window
            )

        else:

            self.classrooms_window.window.deiconify()
            self.classrooms_window.window.lift()
            self.classrooms_window.window.focus_force()

    # =====================================================
    # CLASSES & SEMESTERS
    # =====================================================

    def classes_clicked(self):

        if (
            self.classes_window is None
            or not self.classes_window.window.winfo_exists()
        ):

            self.classes_window = ClassesWindow(
                self.window
            )

        else:

            self.classes_window.window.deiconify()
            self.classes_window.window.lift()
            self.classes_window.window.focus_force()

    # =====================================================
    # GENERATE TIMETABLE
    # =====================================================

    def generate_clicked(self):

        if (
            self.generate_window is None
            or not self.generate_window.window.winfo_exists()
        ):

            self.generate_window = GenerateTimetableWindow(
                self.window
            )

        else:

            self.generate_window.window.deiconify()
            self.generate_window.window.lift()
            self.generate_window.window.focus_force()

    # =====================================================
    # VIEW TIMETABLE
    # =====================================================

    def view_timetable_clicked(self):

        if (
            self.view_timetable_window is None
            or not self.view_timetable_window.window.winfo_exists()
        ):

            self.view_timetable_window = ViewTimetableWindow(
                self.window
            )

        else:

            self.view_timetable_window.window.deiconify()
            self.view_timetable_window.window.lift()
            self.view_timetable_window.window.focus_force()

    # =====================================================
    # SETTINGS
    # =====================================================

    def settings_clicked(self):

        self._show_status(
            "Settings",
            "Application settings will be available here."
        )

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.window.mainloop()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    dashboard = Dashboard()

    dashboard.run()