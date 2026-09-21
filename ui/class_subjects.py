import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    get_all_classes,
    get_subjects_for_class_assignment,
    assign_subject_to_class,
    get_all_class_subjects,
    get_class_subjects_by_class,
    delete_class_subject
)


class ClassSubjectsWindow:

    def __init__(
        self,
        parent,
        preselected_class_id=None
    ):

        self.window = ctk.CTkToplevel(parent)

        self.window.title(
            "Class - Subject Assignment"
        )

        self.window.geometry(
            "1150x680"
        )

        self.window.minsize(
            1000,
            600
        )

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

        self.preselected_class_id = (
            preselected_class_id
        )

        self.classes = []

        self.available_subjects = []

        # =================================================
        # MAIN FRAME
        # =================================================

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#FFFFFF",
            corner_radius=0
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # =================================================
        # TITLE
        # =================================================

        title = ctk.CTkLabel(
            self.main_frame,
            text="Class - Subject Assignment",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            ),
            text_color="#111827"
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(25, 5)
        )

        # =================================================
        # SUBTITLE
        # =================================================

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text=(
                "Assign subjects to academic classes. "
                "Faculty information is selected automatically."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#6B7280"
        )

        subtitle.pack(
            anchor="w",
            padx=30,
            pady=(0, 20)
        )

        # =================================================
        # FORM FRAME
        # =================================================

        form_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#F8FAFC",
            corner_radius=10
        )

        form_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        # =================================================
        # CLASS LABEL
        # =================================================

        class_label = ctk.CTkLabel(
            form_frame,
            text="Class *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        class_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=(20, 5),
            sticky="w"
        )

        # =================================================
        # CLASS MENU
        # =================================================

        self.class_menu = ctk.CTkOptionMenu(
            form_frame,
            width=330,
            height=40,
            values=[
                "No classes available"
            ],
            command=self.class_changed
        )

        self.class_menu.set(
            "No classes available"
        )

        self.class_menu.grid(
            row=1,
            column=0,
            padx=(20, 10),
            pady=(0, 20)
        )

        # =================================================
        # SUBJECT LABEL
        # =================================================

        subject_label = ctk.CTkLabel(
            form_frame,
            text="Subject *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        subject_label.grid(
            row=0,
            column=1,
            padx=10,
            pady=(20, 5),
            sticky="w"
        )

        # =================================================
        # SUBJECT MENU
        # =================================================

        self.subject_menu = ctk.CTkOptionMenu(
            form_frame,
            width=380,
            height=40,
            values=[
                "Select a class first"
            ],
            command=self.subject_changed
        )

        self.subject_menu.set(
            "Select a class first"
        )

        self.subject_menu.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 20)
        )

        # =================================================
        # ASSIGN BUTTON
        # =================================================

        self.assign_button = ctk.CTkButton(
            form_frame,
            text="Assign Subject",
            width=150,
            height=40,
            command=self.assign_subject
        )

        self.assign_button.grid(
            row=1,
            column=2,
            padx=(10, 20),
            pady=(0, 20)
        )

        # =================================================
        # FACULTY INFORMATION
        # =================================================

        self.faculty_info = ctk.CTkLabel(
            form_frame,
            text="Assigned Faculty: -",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#2563EB"
        )

        self.faculty_info.grid(
            row=2,
            column=0,
            columnspan=3,
            padx=20,
            pady=(0, 20),
            sticky="w"
        )

        # =================================================
        # FILTER / SHOW ALL
        # =================================================

        filter_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        filter_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 10)
        )

        self.current_class_label = ctk.CTkLabel(
            filter_frame,
            text="Showing all class-subject assignments",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        self.current_class_label.pack(
            side="left"
        )

        show_all_button = ctk.CTkButton(
            filter_frame,
            text="Show All",
            width=100,
            height=34,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.show_all_assignments
        )

        show_all_button.pack(
            side="right"
        )

        # =================================================
        # TABLE
        # =================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#F8FAFC",
            corner_radius=10
        )

        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25)
        )

        # =================================================
        # LOAD
        # =================================================

        self.load_classes()

        self.show_all_assignments()

    # =====================================================
    # CLASS DISPLAY TEXT
    # =====================================================

    def class_display_text(
        self,
        record
    ):

        return (
            f"{record[1]} - "
            f"{record[2]} - "
            f"{record[3]} "
            f"({record[4]})"
        )

    # =====================================================
    # SUBJECT DISPLAY TEXT
    # =====================================================

    def subject_display_text(
        self,
        record
    ):

        return (
            f"{record[1]} - "
            f"{record[2]}"
        )

    # =====================================================
    # LOAD CLASSES
    # =====================================================

    def load_classes(self):

        self.classes = get_all_classes()

        if not self.classes:

            self.class_menu.configure(
                values=[
                    "No classes available"
                ]
            )

            self.class_menu.set(
                "No classes available"
            )

            self.load_subjects_for_class(
                None
            )

            return

        values = [
            self.class_display_text(record)
            for record in self.classes
        ]

        self.class_menu.configure(
            values=values
        )

        selected_record = None

        # =================================================
        # PRESELECT CLASS
        # =================================================

        if self.preselected_class_id is not None:

            for record in self.classes:

                if (
                    record[0]
                    == self.preselected_class_id
                ):

                    selected_record = record

                    break

        if selected_record is None:

            selected_record = self.classes[0]

        self.class_menu.set(
            self.class_display_text(
                selected_record
            )
        )

        self.load_subjects_for_class(
            selected_record[0]
        )

    # =====================================================
    # GET SELECTED CLASS
    # =====================================================

    def get_selected_class(self):

        selected_text = (
            self.class_menu.get()
        )

        for record in self.classes:

            if (
                self.class_display_text(record)
                == selected_text
            ):

                return record

        return None

    # =====================================================
    # CLASS CHANGED
    # =====================================================

    def class_changed(
        self,
        selected_value=None
    ):

        selected_class = (
            self.get_selected_class()
        )

        if selected_class is None:

            self.load_subjects_for_class(
                None
            )

            return

        class_id = selected_class[0]

        self.load_subjects_for_class(
            class_id
        )

        self.load_assignments_for_class(
            class_id
        )

    # =====================================================
    # LOAD SUBJECTS
    # =====================================================

    def load_subjects_for_class(
        self,
        class_id
    ):

        self.available_subjects = []

        self.faculty_info.configure(
            text="Assigned Faculty: -"
        )

        if class_id is None:

            self.subject_menu.configure(
                values=[
                    "Select a class first"
                ]
            )

            self.subject_menu.set(
                "Select a class first"
            )

            return

        self.available_subjects = (
            get_subjects_for_class_assignment(
                class_id
            )
        )

        if not self.available_subjects:

            self.subject_menu.configure(
                values=[
                    "No available subjects"
                ]
            )

            self.subject_menu.set(
                "No available subjects"
            )

            return

        values = [
            self.subject_display_text(record)
            for record in self.available_subjects
        ]

        self.subject_menu.configure(
            values=values
        )

        self.subject_menu.set(
            values[0]
        )

        self.subject_changed()

    # =====================================================
    # GET SELECTED SUBJECT
    # =====================================================

    def get_selected_subject(self):

        selected_text = (
            self.subject_menu.get()
        )

        for record in self.available_subjects:

            if (
                self.subject_display_text(record)
                == selected_text
            ):

                return record

        return None

    # =====================================================
    # SUBJECT CHANGED
    # =====================================================

    def subject_changed(
        self,
        selected_value=None
    ):

        subject = (
            self.get_selected_subject()
        )

        if subject is None:

            self.faculty_info.configure(
                text="Assigned Faculty: -"
            )

            return

        faculty_name = subject[7]

        hours_per_week = subject[5]

        self.faculty_info.configure(
            text=(
                f"Assigned Faculty: {faculty_name}"
                f"     |     "
                f"Hours / Week: {hours_per_week}"
            )
        )

    # =====================================================
    # ASSIGN SUBJECT
    # =====================================================

    def assign_subject(self):

        selected_class = (
            self.get_selected_class()
        )

        selected_subject = (
            self.get_selected_subject()
        )

        if selected_class is None:

            messagebox.showwarning(
                "Assignment Error",
                "Please select a class."
            )

            return

        if selected_subject is None:

            messagebox.showwarning(
                "Assignment Error",
                (
                    "No subject is available "
                    "for this class."
                )
            )

            return

        class_id = selected_class[0]

        subject_id = selected_subject[0]

        result = assign_subject_to_class(
            class_id,
            subject_id
        )

        # =================================================
        # SUCCESS
        # =================================================

        if result == "SUCCESS":

            messagebox.showinfo(
                "Success",
                (
                    "Subject assigned to "
                    "class successfully."
                )
            )

            self.load_subjects_for_class(
                class_id
            )

            self.load_assignments_for_class(
                class_id
            )

        # =================================================
        # DUPLICATE
        # =================================================

        elif result == "DUPLICATE":

            messagebox.showwarning(
                "Duplicate Assignment",
                (
                    "This subject is already "
                    "assigned to this class."
                )
            )

        # =================================================
        # NO FACULTY
        # =================================================

        elif result == "NO_FACULTY":

            messagebox.showwarning(
                "Faculty Not Assigned",
                (
                    "This subject does not have "
                    "an assigned faculty member.\n\n"
                    "Assign a faculty member to "
                    "the subject first."
                )
            )

    # =====================================================
    # SHOW ALL
    # =====================================================

    def show_all_assignments(self):

        assignments = (
            get_all_class_subjects()
        )

        self.current_class_label.configure(
            text=(
                "Showing all class-subject "
                "assignments"
            )
        )

        self.display_assignments(
            assignments
        )

    # =====================================================
    # LOAD CLASS ASSIGNMENTS
    # =====================================================

    def load_assignments_for_class(
        self,
        class_id
    ):

        assignments = (
            get_class_subjects_by_class(
                class_id
            )
        )

        selected_class = (
            self.get_selected_class()
        )

        if selected_class:

            self.current_class_label.configure(
                text=(
                    f"Showing subjects for: "
                    f"{selected_class[1]} "
                    f"({selected_class[3]})"
                )
            )

        self.display_assignments(
            assignments
        )

    # =====================================================
    # DISPLAY
    # =====================================================

    def display_assignments(
        self,
        assignments
    ):

        for widget in self.table_frame.winfo_children():

            widget.destroy()

        # =================================================
        # HEADERS
        # =================================================

        headers = [
            "Class",
            "Semester",
            "Subject Code",
            "Subject",
            "Hours/Week",
            "Faculty",
            "Action"
        ]

        widths = [
            140,
            140,
            120,
            230,
            110,
            180,
            100
        ]

        for column, (
            header,
            width
        ) in enumerate(
            zip(
                headers,
                widths
            )
        ):

            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                width=width,
                height=35,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                text_color="#111827",
                fg_color="#E5E7EB",
                corner_radius=4
            )

            label.grid(
                row=0,
                column=column,
                padx=3,
                pady=3,
                sticky="nsew"
            )

        # =================================================
        # EMPTY
        # =================================================

        if not assignments:

            empty_label = ctk.CTkLabel(
                self.table_frame,
                text=(
                    "No class-subject "
                    "assignments found."
                ),
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#6B7280"
            )

            empty_label.grid(
                row=1,
                column=0,
                columnspan=7,
                pady=35
            )

            return

        # =================================================
        # ROWS
        # =================================================

        for row_index, record in enumerate(
            assignments,
            start=1
        ):

            assignment_id = record[0]

            class_name = record[2]
            semester = record[4]

            subject_code = record[7]
            subject_name = record[8]

            hours_per_week = record[9]

            faculty_name = (
                record[11]
                if record[11]
                else "Not Assigned"
            )

            values = [
                class_name,
                semester,
                subject_code,
                subject_name,
                hours_per_week,
                faculty_name
            ]

            for column, (
                value,
                width
            ) in enumerate(
                zip(
                    values,
                    widths
                )
            ):

                label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    width=width,
                    height=38,
                    font=ctk.CTkFont(
                        size=12
                    ),
                    text_color="#374151",
                    anchor="w"
                )

                label.grid(
                    row=row_index,
                    column=column,
                    padx=3,
                    pady=2,
                    sticky="nsew"
                )

            # =================================================
            # DELETE
            # =================================================

            delete_button = ctk.CTkButton(
                self.table_frame,
                text="🗑 Delete",
                width=90,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda aid=assignment_id:
                self.confirm_delete(aid)
            )

            delete_button.grid(
                row=row_index,
                column=6,
                padx=5,
                pady=4
            )

    # =====================================================
    # DELETE
    # =====================================================

    def confirm_delete(
        self,
        assignment_id
    ):

        confirm = messagebox.askyesno(
            "Remove Subject",
            (
                "Are you sure you want to remove "
                "this subject from the class?"
            )
        )

        if not confirm:

            return

        delete_class_subject(
            assignment_id
        )

        messagebox.showinfo(
            "Removed",
            (
                "Subject removed from "
                "class successfully."
            )
        )

        selected_class = (
            self.get_selected_class()
        )

        if selected_class:

            self.load_subjects_for_class(
                selected_class[0]
            )

            self.load_assignments_for_class(
                selected_class[0]
            )

        else:

            self.show_all_assignments()

    # =====================================================
    # CLOSE
    # =====================================================

    def close_window(self):

        self.window.destroy()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    ctk.set_appearance_mode(
        "light"
    )

    ctk.set_default_color_theme(
        "blue"
    )

    root = ctk.CTk()

    root.withdraw()

    app = ClassSubjectsWindow(
        root
    )

    root.mainloop()