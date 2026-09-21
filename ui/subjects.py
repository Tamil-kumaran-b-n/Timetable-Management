import customtkinter as ctk
from tkinter import messagebox


from database.database import (
    add_subject,
    get_all_subjects,
    update_subject,
    delete_subject,
    search_subjects
)


class SubjectsWindow:

    def __init__(self, parent=None, container=None):

        self.parent = parent
        self.embedded = container is not None

        self.window = container if self.embedded else (
            ctk.CTkToplevel(parent) if parent else ctk.CTk()
        )

        if not self.embedded:
            self.window.title(
                "Subject Management - Smart Academic Timetable Management System"
            )
            self.window.geometry("1200x720")
            self.window.minsize(1050, 650)

        self.selected_id = None

        ctk.set_appearance_mode(
            "Light"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        self.create_ui()

        self.load_subjects()

    # =====================================================
    # CREATE UI
    # =====================================================

    def create_ui(self):

        main = ctk.CTkScrollableFrame(
            self.window,
            fg_color="#F5F7FA",
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
            fg_color="#FFFFFF",
            corner_radius=0
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Subject Management",
            font=("Arial", 25, "bold"),
            text_color="#111827"
        ).pack(
            side="left",
            padx=30
        )

        ctk.CTkLabel(
            header,
            text="Manage subject information and academic hours",
            font=("Arial", 13),
            text_color="#6B7280"
        ).pack(
            side="right",
            padx=30
        )

        # =================================================
        # FORM CARD
        # =================================================

        form_card = ctk.CTkFrame(
            main,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        form_card.pack(
            fill="x",
            padx=25,
            pady=20
        )

        # =================================================
        # GRID CONFIGURATION
        # =================================================

        for column in range(4):

            form_card.grid_columnconfigure(
                column,
                weight=1
            )

        # =================================================
        # FORM TITLE
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Subject Details",
            font=("Arial", 18, "bold"),
            text_color="#111827"
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=25,
            pady=(20, 15)
        )

        # =================================================
        # SUBJECT CODE
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Subject Code *",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=5
        )

        self.subject_code_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="Example: BCA101"
        )

        self.subject_code_entry.grid(
            row=2,
            column=0,
            padx=25,
            pady=(0, 15),
            sticky="ew"
        )

        # =================================================
        # SUBJECT NAME
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Subject Name *",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=15,
            pady=5
        )

        self.subject_name_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="Enter subject name"
        )

        self.subject_name_entry.grid(
            row=2,
            column=1,
            padx=15,
            pady=(0, 15),
            sticky="ew"
        )

        # =================================================
        # DEPARTMENT
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Department *",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=15,
            pady=5
        )

        self.department_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="Example: BCA"
        )

        self.department_entry.grid(
            row=2,
            column=2,
            padx=15,
            pady=(0, 15),
            sticky="ew"
        )

        # =================================================
        # SEMESTER
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Semester *",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=25,
            pady=5
        )

        self.semester_menu = ctk.CTkOptionMenu(
            form_card,
            height=38,
            values=[
                "Semester 1",
                "Semester 2",
                "Semester 3",
                "Semester 4",
                "Semester 5",
                "Semester 6"
            ]
        )

        self.semester_menu.set(
            "Semester 1"
        )

        self.semester_menu.grid(
            row=4,
            column=0,
            padx=25,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # HOURS / WEEK
        #
        # Kept in UI for compatibility with the existing
        # database. Actual workload periods are handled
        # in Faculty Workload Management.
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Hours / Week *",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=15,
            pady=5
        )

        self.hours_menu = ctk.CTkOptionMenu(
            form_card,
            height=38,
            values=[
                str(number)
                for number in range(1, 21)
            ]
        )

        self.hours_menu.set(
            "5"
        )

        self.hours_menu.grid(
            row=4,
            column=1,
            padx=15,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # BUTTON FRAME
        # =================================================

        button_frame = ctk.CTkFrame(
            form_card,
            fg_color="transparent"
        )

        button_frame.grid(
            row=4,
            column=2,
            columnspan=2,
            padx=15,
            pady=(0, 20),
            sticky="w"
        )

        # =================================================
        # ADD BUTTON
        # =================================================

        ctk.CTkButton(
            button_frame,
            text="Add Subject",
            width=110,
            height=38,
            command=self.add_subject_record
        ).pack(
            side="left",
            padx=4
        )

        # =================================================
        # UPDATE BUTTON
        # =================================================

        ctk.CTkButton(
            button_frame,
            text="Update",
            width=90,
            height=38,
            command=self.update_subject_record
        ).pack(
            side="left",
            padx=4
        )

        # =================================================
        # CLEAR BUTTON
        # =================================================

        ctk.CTkButton(
            button_frame,
            text="Clear",
            width=80,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.clear_form
        ).pack(
            side="left",
            padx=4
        )

        # =================================================
        # SEARCH SECTION
        # =================================================

        search_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 10)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search Subject",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=320,
            height=38,
            placeholder_text="Search by code, name, department or semester"
        )

        self.search_entry.pack(
            side="left"
        )

        # =================================================
        # SEARCH BUTTON
        # =================================================

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            command=self.search_records
        ).pack(
            side="left",
            padx=8
        )

        # =================================================
        # SHOW ALL BUTTON
        # =================================================

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=90,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_subjects
        ).pack(
            side="left"
        )

        # =================================================
        # SUBJECT RECORDS CARD
        # =================================================

        list_card = ctk.CTkFrame(
            main,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )

        list_card.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        # =================================================
        # RECORDS TITLE
        # =================================================

        ctk.CTkLabel(
            list_card,
            text="Subject Records",
            font=("Arial", 18, "bold"),
            text_color="#111827"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            list_card,
            text=(
                "View and manage subject code, name, "
                "department, semester and weekly hours."
            ),
            font=("Arial", 12),
            text_color="#6B7280"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        # =================================================
        # SCROLLABLE TABLE
        # =================================================

        self.list_frame = ctk.CTkFrame(
            list_card,
            fg_color="#FFFFFF",
            corner_radius=8
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

    # =====================================================
    # LOAD SUBJECTS
    # =====================================================

    def load_subjects(self):

        try:

            records = get_all_subjects()

            self.display_records(
                records
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Unable to load subjects.\n\n{error}",
                parent=self.window
            )

    # =====================================================
    # DISPLAY RECORDS
    # =====================================================

    def display_records(
        self,
        records
    ):

        # -------------------------------------------------
        # CLEAR OLD TABLE
        # -------------------------------------------------

        for widget in self.list_frame.winfo_children():

            widget.destroy()

        # =================================================
        # TABLE HEADERS
        # =================================================

        headers = [
            "Subject Code",
            "Subject Name",
            "Department",
            "Semester",
            "Hours / Week",
            "Action"
        ]

        widths = [
            150,
            300,
            150,
            150,
            150,
            210
        ]

        # =================================================
        # HEADER ROW
        # =================================================

        for column, (
            header,
            width
        ) in enumerate(
            zip(
                headers,
                widths
            )
        ):

            ctk.CTkLabel(
                self.list_frame,
                text=header,
                width=width,
                height=40,
                font=("Arial", 12, "bold"),
                text_color="#111827",
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
        # NO RECORDS
        # =================================================

        if not records:

            ctk.CTkLabel(
                self.list_frame,
                text="No subject records found.",
                font=("Arial", 14),
                text_color="#9CA3AF"
            ).grid(
                row=1,
                column=0,
                columnspan=6,
                pady=50
            )

            return

        # =================================================
        # DISPLAY EACH SUBJECT
        # =================================================

        for row_number, record in enumerate(
            records,
            start=1
        ):

            record_id = record[0]

            subject_code = record[1]

            subject_name = record[2]

            department = record[3]

            semester = record[4]

            # -------------------------------------------------
            # IMPORTANT:
            # Current database.get_all_subjects() returns
            # only 5 columns.
            #
            # If hours exists, use it.
            # Otherwise display 0.
            # -------------------------------------------------

            if len(record) > 5:

                hours_per_week = record[5]

            else:

                hours_per_week = 0

            # =================================================
            # FORMAT SEMESTER
            # =================================================

            semester_display = (
                self.format_semester(
                    semester
                )
            )

            values = [

                subject_code
                if subject_code
                else "-",

                subject_name
                if subject_name
                else "-",

                department
                if department
                else "-",

                semester_display
                if semester_display
                else "-",

                str(hours_per_week)
                if hours_per_week is not None
                else "-"
            ]

            # =================================================
            # DATA CELLS
            # =================================================

            for column, (
                value,
                width
            ) in enumerate(
                zip(
                    values,
                    widths
                )
            ):

                ctk.CTkLabel(
                    self.list_frame,
                    text=str(value),
                    width=width,
                    height=42,
                    font=("Arial", 12),
                    text_color="#374151",
                    fg_color="#F9FAFB",
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
                width=210,
                height=42,
                fg_color="#F9FAFB",
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
            # SELECT BUTTON
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Select",
                width=75,
                height=30,
                command=lambda r=record:
                    self.select_record(r)
            ).pack(
                side="left",
                padx=(10, 5),
                pady=6
            )

            # =================================================
            # DELETE BUTTON
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Delete",
                width=75,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda rid=record_id,
                           sname=subject_name:
                    self.delete_subject_record(
                        rid,
                        sname
                    )
            ).pack(
                side="left",
                padx=5,
                pady=6
            )

    # =====================================================
    # FORMAT SEMESTER FOR DISPLAY
    # =====================================================

    def format_semester(
        self,
        semester
    ):

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
            "VI Semester": "Semester 6",

            "Semester 1": "Semester 1",
            "Semester 2": "Semester 2",
            "Semester 3": "Semester 3",
            "Semester 4": "Semester 4",
            "Semester 5": "Semester 5",
            "Semester 6": "Semester 6"
        }

        return semester_map.get(
            value,
            value
        )

    # =====================================================
    # CONVERT SEMESTER TO DATABASE VALUE
    # =====================================================

    def database_semester_value(
        self,
        semester
    ):

        value = str(
            semester
        ).strip()

        semester_map = {

            "Semester 1": "1",
            "Semester 2": "2",
            "Semester 3": "3",
            "Semester 4": "4",
            "Semester 5": "5",
            "Semester 6": "6",

            "I Semester": "1",
            "II Semester": "2",
            "III Semester": "3",
            "IV Semester": "4",
            "V Semester": "5",
            "VI Semester": "6"
        }

        return semester_map.get(
            value,
            value
        )

    # =====================================================
    # VALIDATE FORM
    # =====================================================

    def validate_form(self):

        subject_code = (
            self.subject_code_entry
            .get()
            .strip()
        )

        subject_name = (
            self.subject_name_entry
            .get()
            .strip()
        )

        department = (
            self.department_entry
            .get()
            .strip()
        )

        semester = (
            self.semester_menu
            .get()
            .strip()
        )

        hours_text = (
            self.hours_menu
            .get()
            .strip()
        )

        # =================================================
        # SUBJECT CODE
        # =================================================

        if not subject_code:

            messagebox.showwarning(
                "Missing Information",
                "Subject Code is required.",
                parent=self.window
            )

            self.subject_code_entry.focus()

            return None

        # =================================================
        # SUBJECT NAME
        # =================================================

        if not subject_name:

            messagebox.showwarning(
                "Missing Information",
                "Subject Name is required.",
                parent=self.window
            )

            self.subject_name_entry.focus()

            return None

        # =================================================
        # DEPARTMENT
        # =================================================

        if not department:

            messagebox.showwarning(
                "Missing Information",
                "Department is required.",
                parent=self.window
            )

            self.department_entry.focus()

            return None

        # =================================================
        # HOURS
        # =================================================

        if not hours_text.isdigit():

            messagebox.showwarning(
                "Invalid Hours",
                "Hours / Week must contain numbers only.",
                parent=self.window
            )

            return None

        hours = int(
            hours_text
        )

        if hours < 1 or hours > 20:

            messagebox.showwarning(
                "Invalid Hours",
                "Hours / Week must be between 1 and 20.",
                parent=self.window
            )

            return None

        # =================================================
        # SEMESTER
        # =================================================

        semester_value = (
            self.database_semester_value(
                semester
            )
        )

        return (
            subject_code,
            subject_name,
            department,
            semester_value,
            hours
        )

    # =====================================================
    # ADD SUBJECT
    # =====================================================

    def add_subject_record(self):

        try:

            data = self.validate_form()

            if data is None:

                return

            (
                subject_code,
                subject_name,
                department,
                semester,
                hours
            ) = data

            # =================================================
            # IMPORTANT FIX:
            #
            # Database add_subject() accepts:
            #
            # code
            # name
            # department
            # semester
            #
            # Hours is NOT passed.
            # =================================================

            success = add_subject(
                subject_code,
                subject_name,
                department,
                semester
            )

            if success:

                messagebox.showinfo(
                    "Success",
                    "Subject added successfully.",
                    parent=self.window
                )

                self.clear_form()

                self.load_subjects()

            else:

                messagebox.showerror(
                    "Subject Not Added",
                    (
                        "Subject could not be added.\n\n"
                        "Possible reason:\n"
                        "Subject Code already exists."
                    ),
                    parent=self.window
                )

        except Exception as error:

            messagebox.showerror(
                "Add Subject Error",
                (
                    "An error occurred while adding "
                    "the subject.\n\n"
                    f"Error: {error}"
                ),
                parent=self.window
            )

    # =====================================================
    # SELECT SUBJECT
    # =====================================================

    def select_record(
        self,
        record
    ):

        self.selected_id = record[0]

        # =================================================
        # SUBJECT CODE
        # =================================================

        self.subject_code_entry.delete(
            0,
            "end"
        )

        if record[1]:

            self.subject_code_entry.insert(
                0,
                record[1]
            )

        # =================================================
        # SUBJECT NAME
        # =================================================

        self.subject_name_entry.delete(
            0,
            "end"
        )

        if record[2]:

            self.subject_name_entry.insert(
                0,
                record[2]
            )

        # =================================================
        # DEPARTMENT
        # =================================================

        self.department_entry.delete(
            0,
            "end"
        )

        if record[3]:

            self.department_entry.insert(
                0,
                record[3]
            )

        # =================================================
        # SEMESTER
        # =================================================

        semester_display = (
            self.format_semester(
                record[4]
            )
        )

        self.semester_menu.set(
            semester_display
        )

        # =================================================
        # HOURS
        # =================================================

        if len(record) > 5:

            if record[5] is not None:

                self.hours_menu.set(
                    str(
                        record[5]
                    )
                )

        else:

            self.hours_menu.set(
                "5"
            )

    # =====================================================
    # UPDATE SUBJECT
    # =====================================================

    def update_subject_record(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Select Subject",
                (
                    "Please select a subject "
                    "record first."
                ),
                parent=self.window
            )

            return

        try:

            data = self.validate_form()

            if data is None:

                return

            (
                subject_code,
                subject_name,
                department,
                semester,
                hours
            ) = data

            # =================================================
            # IMPORTANT FIX:
            #
            # Existing database.update_subject()
            # accepts only 5 parameters after record_id.
            #
            # Hours is intentionally not passed.
            # =================================================

            success = update_subject(
                self.selected_id,
                subject_code,
                subject_name,
                department,
                semester
            )

            if success:

                messagebox.showinfo(
                    "Success",
                    "Subject updated successfully.",
                    parent=self.window
                )

                self.clear_form()

                self.load_subjects()

            else:

                messagebox.showerror(
                    "Update Failed",
                    (
                        "Subject could not be updated.\n\n"
                        "Subject Code may already exist."
                    ),
                    parent=self.window
                )

        except Exception as error:

            messagebox.showerror(
                "Update Subject Error",
                (
                    "An error occurred while updating "
                    "the subject.\n\n"
                    f"Error: {error}"
                ),
                parent=self.window
            )

    # =====================================================
    # DELETE SUBJECT
    # =====================================================

    def delete_subject_record(
        self,
        record_id,
        subject_name
    ):

        confirm = messagebox.askyesno(
            "Delete Subject",
            (
                f'Are you sure you want to delete\n'
                f'"{subject_name}"?\n\n'
                "Related workload/class assignments "
                "may also be affected."
            ),
            parent=self.window
        )

        if not confirm:

            return

        try:

            success = delete_subject(
                record_id
            )

            # Current database delete_subject()
            # does not return a value, so deletion
            # is considered successful if no exception
            # occurs.

            self.clear_form()

            self.load_subjects()

            messagebox.showinfo(
                "Deleted",
                (
                    f'Subject "{subject_name}" '
                    "deleted successfully."
                ),
                parent=self.window
            )

        except Exception as error:

            messagebox.showerror(
                "Delete Subject Error",
                (
                    "Subject could not be deleted.\n\n"
                    f"Error: {error}"
                ),
                parent=self.window
            )

    # =====================================================
    # SEARCH SUBJECTS
    # =====================================================

    def search_records(self):

        try:

            search_text = (
                self.search_entry
                .get()
                .strip()
            )

            if not search_text:

                self.load_subjects()

                return

            records = search_subjects(
                search_text
            )

            self.display_records(
                records
            )

        except Exception as error:

            messagebox.showerror(
                "Search Error",
                (
                    "Unable to search subjects.\n\n"
                    f"Error: {error}"
                ),
                parent=self.window
            )

    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form(self):

        self.selected_id = None

        self.subject_code_entry.delete(
            0,
            "end"
        )

        self.subject_name_entry.delete(
            0,
            "end"
        )

        self.department_entry.delete(
            0,
            "end"
        )

        self.semester_menu.set(
            "Semester 1"
        )

        self.hours_menu.set(
            "5"
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

    app = SubjectsWindow()

    app.run()
