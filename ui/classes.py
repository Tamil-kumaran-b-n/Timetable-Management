import re
import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    add_class,
    get_all_classes,
    update_class,
    delete_class,
    search_classes
)


class ClassesWindow:

    def __init__(self, parent, container=None):

        self.embedded = container is not None
        self.window = container if self.embedded else ctk.CTkToplevel(parent)

        if not self.embedded:
            self.window.title("Classes & Semesters")
            self.window.geometry("1100x720")
            self.window.minsize(1000, 650)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.selected_id = None

        # =========================
        # MAIN FRAME
        # =========================

        self.main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="white",
            corner_radius=0
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # =========================
        # TITLE
        # =========================

        title = ctk.CTkLabel(
            self.main_frame,
            text="Classes & Semesters",
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

        # =========================
        # SUBTITLE
        # =========================

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text=(
                "Generate academic classes and semesters "
                "automatically from the course duration."
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

        # =========================
        # GENERATOR FORM
        # =========================

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
        # DEPARTMENT / COURSE
        # =================================================

        department_label = ctk.CTkLabel(
            form_frame,
            text="Department / Course *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        department_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=(18, 5),
            sticky="w"
        )

        self.department_entry = ctk.CTkEntry(
            form_frame,
            width=240,
            height=38,
            placeholder_text="Example: BCA"
        )

        self.department_entry.grid(
            row=1,
            column=0,
            padx=(20, 10),
            pady=(0, 15)
        )

        # =================================================
        # COURSE DURATION
        # =================================================

        duration_label = ctk.CTkLabel(
            form_frame,
            text="Course Duration *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        duration_label.grid(
            row=0,
            column=1,
            padx=10,
            pady=(18, 5),
            sticky="w"
        )

        self.duration_menu = ctk.CTkOptionMenu(
            form_frame,
            width=240,
            height=38,
            values=[
                "2 Years",
                "3 Years"
            ]
        )

        self.duration_menu.set(
            "3 Years"
        )

        self.duration_menu.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 15)
        )

        # =================================================
        # STARTING ACADEMIC YEAR
        # =================================================

        year_label = ctk.CTkLabel(
            form_frame,
            text="Starting Academic Year *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        year_label.grid(
            row=0,
            column=2,
            padx=10,
            pady=(18, 5),
            sticky="w"
        )

        self.start_year_entry = ctk.CTkEntry(
            form_frame,
            width=240,
            height=38,
            placeholder_text="Example: 2026"
        )

        self.start_year_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 15)
        )

        # =================================================
        # GENERATE BUTTON
        # =================================================

        self.generate_button = ctk.CTkButton(
            form_frame,
            text="Generate Classes",
            width=170,
            height=38,
            command=self.generate_classes
        )

        self.generate_button.grid(
            row=1,
            column=3,
            padx=(15, 20),
            pady=(0, 15)
        )

        # =================================================
        # INFO LABEL
        # =================================================

        info_label = ctk.CTkLabel(
            form_frame,
            text=(
                "Example: BCA + 3 Years + 2026 creates "
                "1st, 2nd and 3rd year classes with Semesters I-VI."
            ),
            font=ctk.CTkFont(
                size=11
            ),
            text_color="#6B7280"
        )

        info_label.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=20,
            pady=(0, 18),
            sticky="w"
        )

        # =================================================
        # BUTTON FRAME
        # =================================================

        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        # =================================================
        # UPDATE BUTTON
        # =================================================

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Selected",
            width=140,
            height=38,
            command=self.update_class_record
        )

        self.update_button.pack(
            side="left",
            padx=(0, 10)
        )

        # =================================================
        # CLEAR BUTTON
        # =================================================

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=100,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.clear_form
        )

        self.clear_button.pack(
            side="left",
            padx=5
        )

        # =================================================
        # SEARCH FRAME
        # =================================================

        search_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 10)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            height=38,
            placeholder_text="Search class..."
        )

        self.search_entry.pack(
            side="left",
            padx=(0, 10)
        )

        # =================================================
        # SEARCH BUTTON
        # =================================================

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            height=38,
            command=self.search_records
        )

        self.search_button.pack(
            side="left",
            padx=5
        )

        # =================================================
        # SHOW ALL BUTTON
        # =================================================

        self.show_all_button = ctk.CTkButton(
            search_frame,
            text="Show All",
            width=100,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_classes
        )

        self.show_all_button.pack(
            side="left",
            padx=5
        )

        # =================================================
        # TABLE FRAME
        # =================================================

        self.table_frame = ctk.CTkFrame(
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
        # LOAD DATA
        # =================================================

        self.load_classes()

    # =====================================================
    # VALIDATE GENERATOR FORM
    # =====================================================

    def validate_generator_form(self):

        department = (
            self.department_entry
            .get()
            .strip()
        )

        start_year = (
            self.start_year_entry
            .get()
            .strip()
        )

        duration = (
            self.duration_menu
            .get()
        )

        # =========================
        # DEPARTMENT
        # =========================

        if not department:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the department or course name."
            )

            self.department_entry.focus()

            return None

        # =========================
        # YEAR
        # =========================

        if not start_year:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the starting academic year."
            )

            self.start_year_entry.focus()

            return None

        if not re.fullmatch(
            r"\d{4}",
            start_year
        ):

            messagebox.showwarning(
                "Validation Error",
                (
                    "Starting academic year must be "
                    "a 4-digit year.\n\n"
                    "Example: 2026"
                )
            )

            self.start_year_entry.focus()

            return None

        start_year = int(
            start_year
        )

        # =========================
        # YEAR RANGE
        # =========================

        if start_year < 2000 or start_year > 2100:

            messagebox.showwarning(
                "Invalid Year",
                (
                    "Please enter a valid academic year "
                    "between 2000 and 2100."
                )
            )

            self.start_year_entry.focus()

            return None

        # =========================
        # DURATION
        # =========================

        if duration not in (
            "2 Years",
            "3 Years"
        ):

            messagebox.showwarning(
                "Validation Error",
                "Please select the course duration."
            )

            return None

        return (
            department,
            duration,
            start_year
        )

    # =====================================================
    # GENERATE CLASSES
    # =====================================================

    def generate_classes(self):

        data = self.validate_generator_form()

        if data is None:
            return

        (
            department,
            duration,
            start_year
        ) = data

        department = department.strip()

        # =================================================
        # DETERMINE COURSE YEARS
        # =================================================

        if duration == "2 Years":

            course_years = 2

        else:

            course_years = 3

        total_semesters = course_years * 2

        # =================================================
        # BUILD PREVIEW
        # =================================================

        preview_lines = []

        for year_number in range(
            1,
            course_years + 1
        ):

            first_semester = (
                (year_number - 1) * 2 + 1
            )

            second_semester = (
                first_semester + 1
            )

            # =============================================
            # IMPORTANT:
            # ONE ACADEMIC YEAR PER COURSE YEAR
            # =============================================

            academic_start = (
                start_year +
                year_number -
                1
            )

            academic_end = (
                academic_start + 1
            )

            class_name = self.get_class_name(
                year_number,
                department
            )

            preview_lines.append(
                (
                    f"{class_name}  →  "
                    f"Semester {self.to_roman(first_semester)}, "
                    f"Semester {self.to_roman(second_semester)}  "
                    f"({academic_start}-{academic_end})"
                )
            )

        preview_text = "\n".join(
            preview_lines
        )

        # =================================================
        # CONFIRM
        # =================================================

        confirm = messagebox.askyesno(
            "Generate Classes",
            (
                f"Department: {department}\n"
                f"Duration: {duration}\n"
                f"Starting Year: {start_year}\n\n"
                f"The system will create/update "
                f"{total_semesters} semester records:\n\n"
                f"{preview_text}\n\n"
                "Existing matching classes will be updated "
                "with the correct academic year.\n\n"
                "Do you want to continue?"
            )
        )

        if not confirm:
            return

        # =================================================
        # GET EXISTING CLASSES
        # =================================================

        existing_classes = get_all_classes()

        created_count = 0
        updated_count = 0
        failed_count = 0

        # =================================================
        # CREATE / UPDATE RECORDS
        # =================================================

        for year_number in range(
            1,
            course_years + 1
        ):

            first_semester_number = (
                (year_number - 1) * 2 + 1
            )

            second_semester_number = (
                first_semester_number + 1
            )

            # =============================================
            # CORRECT YEAR CALCULATION
            # =============================================

            academic_start = (
                start_year +
                year_number -
                1
            )

            academic_end = (
                academic_start + 1
            )

            academic_year = (
                f"{academic_start}-{academic_end}"
            )

            class_name = self.get_class_name(
                year_number,
                department
            )

            # =============================================
            # TWO SEMESTERS
            # =============================================

            semester_numbers = [
                first_semester_number,
                second_semester_number
            ]

            for semester_number in semester_numbers:

                semester_name = (
                    f"{self.to_roman(semester_number)} Semester"
                )

                existing_record = None

                # =========================================
                # FIND EXISTING SAME CLASS + SEMESTER
                # =========================================

                for record in existing_classes:

                    record_class_name = (
                        str(record[1]).strip()
                    )

                    record_department = (
                        str(record[2]).strip()
                    )

                    record_semester = (
                        str(record[3]).strip()
                    )

                    if (
                        record_class_name.lower()
                        == class_name.lower()
                        and
                        record_department.lower()
                        == department.lower()
                        and
                        record_semester.lower()
                        == semester_name.lower()
                    ):

                        existing_record = record

                        break

                # =========================================
                # UPDATE EXISTING RECORD
                # =========================================

                if existing_record is not None:

                    record_id = existing_record[0]

                    old_academic_year = (
                        existing_record[4]
                    )

                    # -------------------------------------
                    # Only update if year is different
                    # -------------------------------------

                    if old_academic_year != academic_year:

                        success = update_class(
                            record_id,
                            existing_record[1],
                            existing_record[2],
                            existing_record[3],
                            academic_year
                        )

                        if success:

                            updated_count += 1

                        else:

                            failed_count += 1

                    else:

                        # Already correct
                        updated_count += 1

                # =========================================
                # CREATE NEW RECORD
                # =========================================

                else:

                    success = add_class(
                        class_name,
                        department,
                        semester_name,
                        academic_year
                    )

                    if success:

                        created_count += 1

                    else:

                        failed_count += 1

        # =================================================
        # REFRESH TABLE
        # =================================================

        self.load_classes()

        # =================================================
        # RESULT
        # =================================================

        if failed_count == 0:

            messagebox.showinfo(
                "Generation Completed",
                (
                    f"Classes processed successfully.\n\n"
                    f"Created: {created_count}\n"
                    f"Updated/Verified: {updated_count}\n\n"
                    f"Department: {department}"
                )
            )

        else:

            messagebox.showwarning(
                "Generation Completed with Warnings",
                (
                    f"Created: {created_count}\n"
                    f"Updated/Verified: {updated_count}\n"
                    f"Failed: {failed_count}\n\n"
                    "Please check the class list."
                )
            )

        # =================================================
        # CLEAR GENERATOR INPUTS
        # =================================================

        self.clear_generator_fields()

    # =====================================================
    # CLASS NAME GENERATOR
    # =====================================================

    def get_class_name(
        self,
        year_number,
        department
    ):

        ordinal_names = {
            1: "1st",
            2: "2nd",
            3: "3rd"
        }

        prefix = ordinal_names.get(
            year_number,
            f"{year_number}th"
        )

        return (
            f"{prefix} {department}"
        )

    # =====================================================
    # ROMAN NUMBER
    # =====================================================

    def to_roman(
        self,
        number
    ):

        roman_map = {
            1: "I",
            2: "II",
            3: "III",
            4: "IV",
            5: "V",
            6: "VI"
        }

        return roman_map.get(
            number,
            str(number)
        )

    # =====================================================
    # UPDATE SELECTED CLASS
    # =====================================================

    def update_class_record(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Update Class",
                "Please select a class from the list first."
            )

            return

        classes = get_all_classes()

        selected = None

        for record in classes:

            if record[0] == self.selected_id:

                selected = record

                break

        if selected is None:

            messagebox.showerror(
                "Error",
                "Selected class could not be found."
            )

            return

        messagebox.showinfo(
            "Update Selected",
            (
                "The current class information is already "
                "managed by the automatic class generator.\n\n"
                "To change the academic year structure, use "
                "Generate Classes with the required starting year."
            )
        )

    # =====================================================
    # LOAD CLASSES
    # =====================================================

    def load_classes(self):

        classes = get_all_classes()

        self.display_classes(
            classes
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search_records(self):

        search_text = (
            self.search_entry
            .get()
            .strip()
        )

        if not search_text:

            self.load_classes()

            return

        results = search_classes(
            search_text
        )

        self.display_classes(
            results
        )

    # =====================================================
    # DISPLAY CLASSES
    # =====================================================

    def display_classes(
        self,
        classes
    ):

        for widget in self.table_frame.winfo_children():

            widget.destroy()

        # =========================
        # HEADERS
        # =========================

        headers = [
            "Class Name",
            "Department",
            "Semester",
            "Academic Year",
            "Action"
        ]

        column_widths = [
            200,
            170,
            180,
            180,
            180
        ]

        for column, (
            header,
            width
        ) in enumerate(
            zip(
                headers,
                column_widths
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

        # =========================
        # EMPTY TABLE
        # =========================

        if not classes:

            empty_label = ctk.CTkLabel(
                self.table_frame,
                text="No classes found.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#6B7280"
            )

            empty_label.grid(
                row=1,
                column=0,
                columnspan=5,
                pady=30
            )

            return

        # =========================
        # DATA
        # =========================

        for row_index, record in enumerate(
            classes,
            start=1
        ):

            record_id = record[0]

            class_name = record[1]
            department = record[2]
            semester = record[3]
            academic_year = record[4]

            values = [
                class_name,
                department,
                semester,
                academic_year
            ]

            for column, (
                value,
                width
            ) in enumerate(
                zip(
                    values,
                    column_widths
                )
            ):

                label = ctk.CTkLabel(
                    self.table_frame,
                    text=value,
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

            # =========================
            # SELECT BUTTON
            # =========================

            select_button = ctk.CTkButton(
                self.table_frame,
                text="Select",
                width=65,
                height=30,
                command=lambda rid=record_id:
                self.select_class(rid)
            )

            select_button.grid(
                row=row_index,
                column=4,
                padx=(3, 80),
                pady=4
            )

            # =========================
            # DELETE BUTTON
            # =========================

            delete_button = ctk.CTkButton(
                self.table_frame,
                text="🗑",
                width=45,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                font=ctk.CTkFont(
                    size=14
                ),
                command=lambda rid=record_id:
                self.confirm_delete(rid)
            )

            delete_button.grid(
                row=row_index,
                column=4,
                padx=(90, 3),
                pady=4
            )

    # =====================================================
    # SELECT CLASS
    # =====================================================

    def select_class(
        self,
        record_id
    ):

        classes = get_all_classes()

        selected = None

        for record in classes:

            if record[0] == record_id:

                selected = record

                break

        if selected is None:

            return

        self.selected_id = selected[0]

        self.department_entry.delete(
            0,
            "end"
        )

        self.department_entry.insert(
            0,
            selected[2]
        )

        self.start_year_entry.delete(
            0,
            "end"
        )

        academic_year = selected[4]

        match = re.match(
            r"(\d{4})-(\d{4})",
            academic_year
        )

        if match:

            self.start_year_entry.insert(
                0,
                match.group(1)
            )

        else:

            self.start_year_entry.insert(
                0,
                academic_year
            )

    # =====================================================
    # DELETE
    # =====================================================

    def confirm_delete(
        self,
        record_id
    ):

        confirm = messagebox.askyesno(
            "Delete Class",
            "Are you sure you want to delete this class?"
        )

        if not confirm:

            return

        delete_class(
            record_id
        )

        if self.selected_id == record_id:

            self.clear_form()

        self.load_classes()

        messagebox.showinfo(
            "Deleted",
            "Class deleted successfully."
        )

    # =====================================================
    # CLEAR GENERATOR FIELDS
    # =====================================================

    def clear_generator_fields(self):

        self.department_entry.delete(
            0,
            "end"
        )

        self.start_year_entry.delete(
            0,
            "end"
        )

        self.duration_menu.set(
            "3 Years"
        )

        self.selected_id = None

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_form(self):

        self.clear_generator_fields()

    # =====================================================
    # CLOSE
    # =====================================================

    def close_window(self):

        if self.embedded:
            return

        self.window.destroy()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()

    root.withdraw()

    app = ClassesWindow(
        root
    )

    root.mainloop()
