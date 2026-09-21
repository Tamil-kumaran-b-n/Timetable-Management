import re
import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    get_all_faculty,
    get_all_classes,
    get_all_subjects
)

from database.workload import (
    add_workload,
    get_all_workloads,
    update_workload,
    delete_workload
)


class AssignmentsWindow:

    def __init__(
        self,
        parent=None,
        preselected_faculty_id=None,
        container=None
    ):

        self.parent = parent
        self.embedded = container is not None

        self.preselected_faculty_id = (
            preselected_faculty_id
        )

        self.selected_workload_id = None

        self.faculty_records = []
        self.class_records = []
        self.subject_records = []

        self.faculty_map = {}
        self.class_map = {}
        self.subject_map = {}

        self.window = container if self.embedded else (
            ctk.CTkToplevel(parent) if parent else ctk.CTk()
        )

        if not self.embedded:
            self.window.title("Faculty Workload Management")
            self.window.geometry("1200x760")
            self.window.minsize(1050, 680)

        ctk.set_appearance_mode(
            "Light"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        self.create_ui()

        self.load_dropdowns()

        self.load_workloads()

    # =====================================================
    # CREATE UI
    # =====================================================

    def create_ui(self):

        main = ctk.CTkScrollableFrame(
            self.window,
            fg_color=("#F5F7FA", "#0F172A"),
            corner_radius=0
        )

        main.pack(
            fill="both",
            expand=True
        )

        # =================================================
        # HEADER
        # =================================================

        header = ctk.CTkFrame(
            main,
            height=80,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=0
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Faculty Workload Management",
            font=("Arial", 25, "bold"),
            text_color=("#111827", "#F8FAFC")
        ).pack(
            side="left",
            padx=30
        )

        ctk.CTkLabel(
            header,
            text=(
                "Add multiple classes and subjects "
                "for each faculty"
            ),
            font=("Arial", 13),
            text_color=("#6B7280", "#94A3B8")
        ).pack(
            side="right",
            padx=30
        )

        # =================================================
        # FORM CARD
        # =================================================

        form_card = ctk.CTkFrame(
            main,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E5E7EB", "#334155")
        )

        form_card.pack(
            fill="x",
            padx=25,
            pady=20
        )

        for column in range(4):

            form_card.grid_columnconfigure(
                column,
                weight=1
            )

        # =================================================
        # FACULTY
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Faculty",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(20, 5)
        )

        self.faculty_menu = ctk.CTkOptionMenu(
            form_card,
            width=250,
            height=38,
            values=["Loading..."],
            command=self.on_faculty_change
        )

        self.faculty_menu.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # CLASS / YEAR
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Class / Year",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=15,
            pady=(20, 5)
        )

        self.class_menu = ctk.CTkOptionMenu(
            form_card,
            width=300,
            height=38,
            values=["Loading..."],
            command=self.on_class_change
        )

        self.class_menu.grid(
            row=1,
            column=1,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # SUBJECT
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Subject",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=15,
            pady=(20, 5)
        )

        self.subject_menu = ctk.CTkOptionMenu(
            form_card,
            width=250,
            height=38,
            values=["Select Class First"]
        )

        self.subject_menu.grid(
            row=1,
            column=2,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # PRIORITY
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Priority",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 5)
        )

        self.priority_menu = ctk.CTkOptionMenu(
            form_card,
            width=250,
            height=38,
            values=[
                "Normal",
                "Important"
            ]
        )

        self.priority_menu.set(
            "Normal"
        )

        self.priority_menu.grid(
            row=3,
            column=0,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # PERIODS PER WEEK
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Periods / Week",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=15,
            pady=(0, 5)
        )

        period_values = [
            str(number)
            for number in range(1, 21)
        ]

        self.periods_menu = ctk.CTkOptionMenu(
            form_card,
            width=300,
            height=38,
            values=period_values
        )

        self.periods_menu.set(
            "5"
        )

        self.periods_menu.grid(
            row=3,
            column=1,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # BUTTONS
        # =================================================

        button_frame = ctk.CTkFrame(
            form_card,
            fg_color="transparent"
        )

        button_frame.grid(
            row=3,
            column=2,
            columnspan=2,
            padx=15,
            pady=(0, 20),
            sticky="w"
        )

        # -------------------------------------------------
        # ADD WORKLOAD
        # -------------------------------------------------

        self.add_button = ctk.CTkButton(
            button_frame,
            text="＋ Add Workload",
            width=150,
            height=38,
            command=self.add_workload_record
        )

        self.add_button.pack(
            side="left",
            padx=4
        )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update",
            width=90,
            height=38,
            command=self.update_workload_record
        )

        self.update_button.pack(
            side="left",
            padx=4
        )

        # -------------------------------------------------
        # CLEAR
        # -------------------------------------------------

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=85,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.clear_form
        )

        self.clear_button.pack(
            side="left",
            padx=4
        )

        # =================================================
        # INFORMATION TEXT
        # =================================================

        ctk.CTkLabel(
            main,
            text=(
                "A faculty member can have multiple classes "
                "and multiple subjects. Each workload stores "
                "priority and required periods per week."
            ),
            font=("Arial", 12),
            text_color=("#6B7280", "#94A3B8")
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 12)
        )

        # =================================================
        # WORKLOAD LIST CARD
        # =================================================

        list_card = ctk.CTkFrame(
            main,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E5E7EB", "#334155")
        )

        list_card.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        # =================================================
        # LIST TITLE
        # =================================================

        ctk.CTkLabel(
            list_card,
            text="Assigned Faculty Workloads",
            font=("Arial", 18, "bold"),
            text_color=("#111827", "#F8FAFC")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            list_card,
            text=(
                "View and manage faculty, class, "
                "subject, priority and weekly periods."
            ),
            font=("Arial", 12),
            text_color=("#6B7280", "#94A3B8")
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        # =================================================
        # TABLE
        # =================================================

        self.list_frame = ctk.CTkFrame(
            list_card,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=8
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

    # =====================================================
    # LOAD DROPDOWNS
    # =====================================================

    def load_dropdowns(self):

        # -------------------------------------------------
        # FACULTY
        # -------------------------------------------------

        self.faculty_records = get_all_faculty()

        self.faculty_map = {}

        faculty_values = []

        for record in self.faculty_records:

            record_id = record[0]
            faculty_id = record[1]
            faculty_name = record[2]

            if faculty_id:

                display = (
                    f"{faculty_name} "
                    f"[ID: {faculty_id}]"
                )

            else:

                display = faculty_name

            self.faculty_map[display] = record_id

            faculty_values.append(
                display
            )

        if not faculty_values:

            faculty_values = [
                "No Faculty Available"
            ]

        self.faculty_menu.configure(
            values=faculty_values
        )

        # -------------------------------------------------
        # PRESELECT FACULTY
        # -------------------------------------------------

        selected_faculty_display = None

        if self.preselected_faculty_id is not None:

            for record in self.faculty_records:

                if record[0] == self.preselected_faculty_id:

                    faculty_id = record[1]
                    faculty_name = record[2]

                    if faculty_id:

                        selected_faculty_display = (
                            f"{faculty_name} "
                            f"[ID: {faculty_id}]"
                        )

                    else:

                        selected_faculty_display = (
                            faculty_name
                        )

                    break

        if selected_faculty_display:

            self.faculty_menu.set(
                selected_faculty_display
            )

        elif faculty_values:

            self.faculty_menu.set(
                faculty_values[0]
            )

        # -------------------------------------------------
        # CLASS
        # -------------------------------------------------

        self.class_records = get_all_classes()

        self.class_map = {}

        class_values = []

        for record in self.class_records:

            record_id = record[0]
            class_name = record[1]
            department = record[2]
            semester = record[3]
            academic_year = record[4]

            semester_display = (
                self.format_semester(
                    semester
                )
            )

            # ---------------------------------------------
            # IMPORTANT:
            # Department is NOT shown separately.
            #
            # Example:
            # 1st BCA | Semester 1 | 2024-2025
            # ---------------------------------------------

            display = (
                f"{class_name} | "
                f"{semester_display} | "
                f"{academic_year}"
            )

            self.class_map[display] = record_id

            class_values.append(
                display
            )

        if not class_values:

            class_values = [
                "No Class Available"
            ]

        self.class_menu.configure(
            values=class_values
        )

        if class_values:

            self.class_menu.set(
                class_values[0]
            )

            self.on_class_change(
                class_values[0]
            )

    # =====================================================
    # FORMAT SEMESTER
    # =====================================================

    def format_semester(self, semester):

        value = str(
            semester
        ).strip()

        semester_map = {
            "1": "Semester 1",
            "2": "Semester 2",
            "3": "Semester 3",
            "4": "Semester 4",
            "5": "Semester 5",
            "6": "Semester 6",

            "I Semester": "Semester 1",
            "II Semester": "Semester 2",
            "III Semester": "Semester 3",
            "IV Semester": "Semester 4",
            "V Semester": "Semester 5",
            "VI Semester": "Semester 6"
        }

        return semester_map.get(
            value,
            value
        )

    # =====================================================
    # FACULTY CHANGE
    # =====================================================

    def on_faculty_change(self, selected_value):

        # Faculty change does not remove subjects.
        # Subject availability depends on class.

        if (
            selected_value
            == "No Faculty Available"
        ):

            return

    # =====================================================
    # CLASS CHANGE
    # =====================================================

    def on_class_change(self, selected_value):

        class_id = self.class_map.get(
            selected_value
        )

        if class_id is None:

            self.subject_map = {}

            self.subject_menu.configure(
                values=["No Matching Subject"]
            )

            self.subject_menu.set(
                "No Matching Subject"
            )

            return

        # -------------------------------------------------
        # Get selected class details
        # -------------------------------------------------

        selected_class = None

        for record in self.class_records:

            if record[0] == class_id:

                selected_class = record

                break

        if selected_class is None:

            return

        class_department = str(
            selected_class[2]
        ).strip()

        class_semester = str(
            selected_class[3]
        ).strip()

        # -------------------------------------------------
        # Load ALL subjects
        #
        # We intentionally do NOT require
        # subject_faculty assignment here.
        #
        # New workload system itself stores:
        # Faculty + Class + Subject + Priority + Periods
        # -------------------------------------------------

        all_subjects = get_all_subjects()

        self.subject_records = []
        self.subject_map = {}

        subject_values = []

        for subject in all_subjects:

            subject_id = subject[0]
            subject_code = subject[1]
            subject_name = subject[2]

            subject_department = str(
                subject[3]
            ).strip()

            subject_semester = str(
                subject[4]
            ).strip()

            # ---------------------------------------------
            # Department must match class department
            # ---------------------------------------------

            department_match = (
                subject_department.lower()
                ==
                class_department.lower()
            )

            # ---------------------------------------------
            # Semester must match class semester
            # ---------------------------------------------

            semester_match = (
                subject_semester.lower()
                ==
                class_semester.lower()
            )

            # Backward compatibility:
            # 1 == I Semester, etc.

            if not semester_match:

                semester_pairs = {
                    ("1", "I Semester"),
                    ("I Semester", "1"),

                    ("2", "II Semester"),
                    ("II Semester", "2"),

                    ("3", "III Semester"),
                    ("III Semester", "3"),

                    ("4", "IV Semester"),
                    ("IV Semester", "4"),

                    ("5", "V Semester"),
                    ("V Semester", "5"),

                    ("6", "VI Semester"),
                    ("VI Semester", "6")
                }

                semester_match = (
                    (
                        subject_semester,
                        class_semester
                    )
                    in semester_pairs
                )

            if (
                department_match
                and semester_match
            ):

                self.subject_records.append(
                    subject
                )

                display = (
                    f"{subject_code} - "
                    f"{subject_name}"
                )

                self.subject_map[display] = (
                    subject_id
                )

                subject_values.append(
                    display
                )

        # -------------------------------------------------
        # SUBJECT DROPDOWN
        # -------------------------------------------------

        if not subject_values:

            self.subject_menu.configure(
                values=[
                    "No Matching Subject"
                ]
            )

            self.subject_menu.set(
                "No Matching Subject"
            )

            return

        self.subject_menu.configure(
            values=subject_values
        )

        self.subject_menu.set(
            subject_values[0]
        )

    # =====================================================
    # GET SELECTED FACULTY ID
    # =====================================================

    def get_selected_faculty_id(self):

        selected = self.faculty_menu.get()

        return self.faculty_map.get(
            selected
        )

    # =====================================================
    # GET SELECTED CLASS ID
    # =====================================================

    def get_selected_class_id(self):

        selected = self.class_menu.get()

        return self.class_map.get(
            selected
        )

    # =====================================================
    # GET SELECTED SUBJECT ID
    # =====================================================

    def get_selected_subject_id(self):

        selected = self.subject_menu.get()

        return self.subject_map.get(
            selected
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate_form(self):

        faculty_id = (
            self.get_selected_faculty_id()
        )

        class_id = (
            self.get_selected_class_id()
        )

        subject_id = (
            self.get_selected_subject_id()
        )

        priority = (
            self.priority_menu
            .get()
            .strip()
        )

        periods_text = (
            self.periods_menu
            .get()
            .strip()
        )

        # =================================================
        # FACULTY
        # =================================================

        if faculty_id is None:

            messagebox.showwarning(
                "Missing Faculty",
                "Please select a faculty member.",
                parent=self.window
            )

            return None

        # =================================================
        # CLASS
        # =================================================

        if class_id is None:

            messagebox.showwarning(
                "Missing Class",
                "Please select a class.",
                parent=self.window
            )

            return None

        # =================================================
        # SUBJECT
        # =================================================

        if subject_id is None:

            messagebox.showwarning(
                "Missing Subject",
                (
                    "No valid subject is selected "
                    "for this class."
                ),
                parent=self.window
            )

            return None

        # =================================================
        # PERIODS
        # =================================================

        if not periods_text.isdigit():

            messagebox.showwarning(
                "Invalid Periods",
                "Periods per Week must be a number.",
                parent=self.window
            )

            return None

        periods = int(
            periods_text
        )

        if periods < 1 or periods > 20:

            messagebox.showwarning(
                "Invalid Periods",
                (
                    "Periods per Week must be "
                    "between 1 and 20."
                ),
                parent=self.window
            )

            return None

        # =================================================
        # PRIORITY
        # =================================================

        if priority not in (
            "Normal",
            "Important"
        ):

            priority = "Normal"

        return (
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods
        )

    # =====================================================
    # ADD WORKLOAD
    # =====================================================

    def add_workload_record(self):

        data = self.validate_form()

        if data is None:

            return

        (
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods
        ) = data

        workload_id = add_workload(
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods
        )

        if workload_id:

            messagebox.showinfo(
                "Success",
                "Faculty workload added successfully.",
                parent=self.window
            )

            self.clear_form(
                keep_faculty=True
            )

            self.load_workloads()

        else:

            messagebox.showerror(
                "Duplicate Workload",
                (
                    "This faculty member is already "
                    "assigned to this subject for this class."
                ),
                parent=self.window
            )

    # =====================================================
    # LOAD WORKLOADS
    # =====================================================

    def load_workloads(self):

        records = get_all_workloads()

        self.display_workloads(
            records
        )

    # =====================================================
    # CLASS + SUBJECT SORT KEY
    # =====================================================

    def get_class_sort_key(self, record):
        """
        Sort workload assignments using:

        1. Course
        2. Year
        3. Subject number
        4. Faculty name

        Example:

            1st BCA
                BCA01
                BCA02
                BCA03
                BCA04
                BCA05
                BCA06

            1st BCOM
                BCOM01
                BCOM02
                BCOM03
                BCOM04
                BCOM06

        Faculty name is NOT used as the primary ordering.
        """

        # -------------------------------------------------
        # CLASS DETAILS
        # -------------------------------------------------

        class_name = str(
            record[5]
        ).strip()

        department = str(
            record[6]
        ).strip()

        normalized_class = re.sub(
            r"[^A-Z0-9]+",
            "",
            class_name.upper()
        )

        normalized_department = re.sub(
            r"[^A-Z0-9]+",
            "",
            department.upper()
        )

        # -------------------------------------------------
        # COURSE ORDER
        # -------------------------------------------------

        course_order = {
            "BCA": 1,
            "BSC": 2,
            "BCOM": 3
        }

        course_rank = 99

        for course, rank in course_order.items():

            if course in normalized_class:

                course_rank = rank
                break

        # If course is not present in class name,
        # check department.

        if course_rank == 99:

            for course, rank in course_order.items():

                if course in normalized_department:

                    course_rank = rank
                    break

        # -------------------------------------------------
        # YEAR / CLASS NUMBER
        # -------------------------------------------------

        year_rank = 99

        year_patterns = [
            (1, r"\b(?:1ST|FIRST|1|I)\b"),
            (2, r"\b(?:2ND|SECOND|2|II)\b"),
            (3, r"\b(?:3RD|THIRD|3|III)\b"),
            (4, r"\b(?:4TH|FOURTH|4|IV)\b"),
            (5, r"\b(?:5TH|FIFTH|5|V)\b"),
            (6, r"\b(?:6TH|SIXTH|6|VI)\b")
        ]

        class_upper = class_name.upper()

        for year, pattern in year_patterns:

            if re.search(
                pattern,
                class_upper
            ):

                year_rank = year
                break

        # -------------------------------------------------
        # SUBJECT CODE
        # -------------------------------------------------

        subject_code = str(
            record[10]
        ).strip().upper()

        # Extract numeric part from:
        #
        # BCA01
        # BCA02
        # BCOM01
        # BCOM06
        #
        # Result:
        # BCA01  -> 1
        # BCA02  -> 2
        # BCOM06 -> 6

        number_match = re.search(
            r"(\d+)",
            subject_code
        )

        if number_match:

            subject_number = int(
                number_match.group(1)
            )

        else:

            subject_number = 999

        # -------------------------------------------------
        # FACULTY
        #
        # Only used as final tie-breaker.
        # -------------------------------------------------

        faculty_name = str(
            record[3]
        ).strip().lower()

        return (
            course_rank,
            year_rank,
            subject_number,
            subject_code,
            faculty_name,
            record[0]
        )

    # =====================================================
    # DISPLAY WORKLOADS
    # =====================================================

    def display_workloads(self, records):

        for widget in self.list_frame.winfo_children():

            widget.destroy()

        # =================================================
        # TABLE HEADERS
        # =================================================

        headers = [
            "Faculty",
            "Class",
            "Subject",
            "Priority",
            "Periods / Week",
            "Action"
        ]

        widths = [
            170,
            270,
            220,
            120,
            130,
            190
        ]

        # =================================================
        # HEADER ROW
        # =================================================

        for column, (
            header,
            width
        ) in enumerate(
            zip(headers, widths)
        ):

            ctk.CTkLabel(
                self.list_frame,
                text=header,
                width=width,
                height=40,
                font=("Arial", 12, "bold"),
                text_color=("#111827", "#F8FAFC"),
                fg_color="#E5E7EB",
                corner_radius=5,
                anchor="center"
            ).grid(
                row=0,
                column=column,
                padx=3,
                pady=4,
                sticky="ew"
            )

        # =================================================
        # NO DATA
        # =================================================

        if not records:

            ctk.CTkLabel(
                self.list_frame,
                text="No faculty workloads assigned.",
                font=("Arial", 14),
                text_color=("#9CA3AF", "#64748B")
            ).grid(
                row=1,
                column=0,
                columnspan=6,
                pady=50
            )

            return

        # =================================================
        # SORT DATA BY CLASS
        #
        # Class is the primary ordering.
        # Faculty name is NOT the primary ordering.
        # =================================================

        records = sorted(
            records,
            key=self.get_class_sort_key
        )

        # =================================================
        # DATA ROWS
        # =================================================

        for row_number, record in enumerate(
            records,
            start=1
        ):

            workload_id = record[0]

            faculty_name = record[3]

            class_name = record[5]
            class_department = record[6]
            class_semester = record[7]
            academic_year = record[8]

            subject_code = record[10]
            subject_name = record[11]

            priority = record[12]
            periods = record[13]

            # -------------------------------------------------
            # Class display
            #
            # Department intentionally removed.
            # -------------------------------------------------

            semester_display = (
                self.format_semester(
                    class_semester
                )
            )

            class_display = (
                f"{class_name} | "
                f"{semester_display} | "
                f"{academic_year}"
            )

            # -------------------------------------------------
            # Subject display
            # -------------------------------------------------

            subject_display = (
                f"{subject_code} - "
                f"{subject_name}"
            )

            values = [
                faculty_name,
                class_display,
                subject_display,
                priority,
                periods
            ]

            # =================================================
            # DATA CELLS
            # =================================================

            for column, (
                value,
                width
            ) in enumerate(
                zip(values, widths)
            ):

                ctk.CTkLabel(
                    self.list_frame,
                    text=str(value),
                    width=width,
                    height=42,
                    font=("Arial", 12),
                    text_color=("#374151", "#E2E8F0"),
                    fg_color=("#F9FAFB", "#334155"),
                    corner_radius=4,
                    anchor="w"
                ).grid(
                    row=row_number,
                    column=column,
                    padx=3,
                    pady=3,
                    sticky="ew"
                )

            # =================================================
            # ACTION FRAME
            # =================================================

            action_frame = ctk.CTkFrame(
                self.list_frame,
                width=190,
                height=42,
                fg_color=("#F9FAFB", "#334155"),
                corner_radius=4
            )

            action_frame.grid(
                row=row_number,
                column=5,
                padx=3,
                pady=3,
                sticky="ew"
            )

            action_frame.grid_propagate(
                False
            )

            # =================================================
            # SELECT
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Select",
                width=75,
                height=30,
                command=lambda rid=workload_id:
                    self.select_workload(rid)
            ).pack(
                side="left",
                padx=(8, 4),
                pady=6
            )

            # =================================================
            # DELETE
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Delete",
                width=75,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda rid=workload_id:
                    self.delete_workload_record(rid)
            ).pack(
                side="left",
                padx=4,
                pady=6
            )

    # =====================================================
    # SELECT WORKLOAD
    # =====================================================

    def select_workload(
        self,
        workload_id
    ):

        records = get_all_workloads()

        selected_record = None

        for record in records:

            if record[0] == workload_id:

                selected_record = record

                break

        if selected_record is None:

            messagebox.showerror(
                "Error",
                "Workload record could not be found.",
                parent=self.window
            )

            return

        self.selected_workload_id = (
            workload_id
        )

        # =================================================
        # FACULTY
        # =================================================

        faculty_db_id = selected_record[1]

        for display, record_id in (
            self.faculty_map.items()
        ):

            if record_id == faculty_db_id:

                self.faculty_menu.set(
                    display
                )

                break

        # =================================================
        # CLASS
        # =================================================

        class_db_id = selected_record[4]

        selected_class_display = None

        for display, record_id in (
            self.class_map.items()
        ):

            if record_id == class_db_id:

                selected_class_display = display

                break

        if selected_class_display:

            self.class_menu.set(
                selected_class_display
            )

            self.on_class_change(
                selected_class_display
            )

        # =================================================
        # SUBJECT
        # =================================================

        subject_db_id = selected_record[9]

        for display, record_id in (
            self.subject_map.items()
        ):

            if record_id == subject_db_id:

                self.subject_menu.set(
                    display
                )

                break

        # =================================================
        # PRIORITY
        # =================================================

        self.priority_menu.set(
            selected_record[12]
        )

        # =================================================
        # PERIODS
        # =================================================

        self.periods_menu.set(
            str(
                selected_record[13]
            )
        )

    # =====================================================
    # UPDATE WORKLOAD
    # =====================================================

    def update_workload_record(self):

        if self.selected_workload_id is None:

            messagebox.showwarning(
                "Select Workload",
                (
                    "Please select a workload record "
                    "first."
                ),
                parent=self.window
            )

            return

        data = self.validate_form()

        if data is None:

            return

        (
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods
        ) = data

        success = update_workload(
            self.selected_workload_id,
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Faculty workload updated successfully.",
                parent=self.window
            )

            self.selected_workload_id = None

            self.clear_form(
                keep_faculty=True
            )

            self.load_workloads()

        else:

            messagebox.showerror(
                "Update Failed",
                (
                    "This workload already exists "
                    "or could not be updated."
                ),
                parent=self.window
            )

    # =====================================================
    # DELETE WORKLOAD
    # =====================================================

    def delete_workload_record(
        self,
        workload_id
    ):

        confirm = messagebox.askyesno(
            "Delete Workload",
            (
                "Are you sure you want to delete "
                "this faculty workload?\n\n"
                "This action cannot be undone."
            ),
            parent=self.window
        )

        if not confirm:

            return

        success = delete_workload(
            workload_id
        )

        if success:

            if (
                self.selected_workload_id
                == workload_id
            ):

                self.selected_workload_id = None

                self.clear_form(
                    keep_faculty=True
                )

            self.load_workloads()

            messagebox.showinfo(
                "Deleted",
                "Faculty workload deleted successfully.",
                parent=self.window
            )

        else:

            messagebox.showerror(
                "Delete Failed",
                "The workload could not be deleted.",
                parent=self.window
            )

    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form(
        self,
        keep_faculty=False
    ):

        self.selected_workload_id = None

        # -------------------------------------------------
        # Keep currently selected faculty when adding
        # multiple workloads from Faculty Management.
        # -------------------------------------------------

        current_faculty = None

        if keep_faculty:

            current_faculty = (
                self.faculty_menu.get()
            )

        # -------------------------------------------------
        # Priority
        # -------------------------------------------------

        self.priority_menu.set(
            "Normal"
        )

        # -------------------------------------------------
        # Periods
        # -------------------------------------------------

        self.periods_menu.set(
            "5"
        )

        # -------------------------------------------------
        # Restore faculty
        # -------------------------------------------------

        if keep_faculty and current_faculty:

            self.faculty_menu.set(
                current_faculty
            )

        elif self.faculty_map:

            first_faculty = next(
                iter(
                    self.faculty_map
                )
            )

            self.faculty_menu.set(
                first_faculty
            )

        # -------------------------------------------------
        # Restore first class
        # -------------------------------------------------

        if self.class_map:

            first_class = next(
                iter(
                    self.class_map
                )
            )

            self.class_menu.set(
                first_class
            )

            self.on_class_change(
                first_class
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

    app = AssignmentsWindow()

    app.run()
