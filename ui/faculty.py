import re
import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    add_faculty,
    get_all_faculty,
    update_faculty,
    delete_faculty,
    search_faculty
)


class FacultyWindow:

    def __init__(self, parent=None, container=None, navigate=None):

        self.parent = parent
        self.embedded = container is not None
        self.navigate = navigate

        self.window = container if self.embedded else (
            ctk.CTkToplevel(parent) if parent else ctk.CTk()
        )

        if not self.embedded:
            self.window.title(
                "Faculty Management - Smart Academic Timetable Management System"
            )
            self.window.geometry("1200x720")
            self.window.minsize(1050, 650)

        self.selected_id = None

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")

        self.create_ui()
        self.load_faculty()

    # =====================================================
    # CREATE UI
    # =====================================================

    def create_ui(self):

        main = ctk.CTkScrollableFrame(
            self.window,
            fg_color=("#F4F4F5", "#121212"),
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
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=0
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Faculty Management",
            font=("Arial", 25, "bold"),
            text_color=("#111827", "#F8FAFC")
        ).pack(
            side="left",
            padx=30
        )

        ctk.CTkLabel(
            header,
            text="Manage faculty information and workloads",
            font=("Arial", 13),
            text_color=("#71717A", "#A1A1AA")
        ).pack(
            side="right",
            padx=30
        )

        # =================================================
        # FORM CARD
        # =================================================

        form_card = ctk.CTkFrame(
            main,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
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
        # FORM TITLE
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Faculty Details",
            font=("Arial", 18, "bold"),
            text_color=("#111827", "#F8FAFC")
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=25,
            pady=(20, 15)
        )

        # =================================================
        # FACULTY ID
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Faculty ID",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=5
        )

        self.faculty_id_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="Example: FAC001"
        )

        self.faculty_id_entry.grid(
            row=2,
            column=0,
            padx=25,
            pady=(0, 15),
            sticky="ew"
        )

        # =================================================
        # FACULTY NAME
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Faculty Name *",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=15,
            pady=5
        )

        self.name_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="Enter faculty name"
        )

        self.name_entry.grid(
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
            text_color=("#374151", "#E2E8F0")
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
        # EMAIL
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Email",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=25,
            pady=5
        )

        self.email_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="example@college.edu"
        )

        self.email_entry.grid(
            row=4,
            column=0,
            padx=25,
            pady=(0, 20),
            sticky="ew"
        )

        # =================================================
        # PHONE
        # =================================================

        ctk.CTkLabel(
            form_card,
            text="Phone",
            font=("Arial", 13, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=15,
            pady=5
        )

        self.phone_entry = ctk.CTkEntry(
            form_card,
            height=38,
            placeholder_text="10 digit mobile number"
        )

        self.phone_entry.grid(
            row=4,
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
            row=4,
            column=2,
            columnspan=2,
            padx=15,
            pady=(0, 20),
            sticky="w"
        )

        ctk.CTkButton(
            button_frame,
            text="Add Faculty",
            width=110,
            height=38,
            command=self.add_faculty_record
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            button_frame,
            text="Update",
            width=90,
            height=38,
            command=self.update_faculty_record
        ).pack(
            side="left",
            padx=4
        )

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
        # SEARCH
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
            text="Search Faculty",
            font=("Arial", 14, "bold"),
            text_color=("#374151", "#E2E8F0")
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=320,
            height=38,
            placeholder_text=(
                "Search by ID, name, department, email or phone"
            )
        )

        self.search_entry.pack(
            side="left"
        )

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

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=90,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_faculty
        ).pack(
            side="left"
        )

        # =================================================
        # FACULTY RECORDS CARD
        # =================================================

        list_card = ctk.CTkFrame(
            main,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
        )

        list_card.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        ctk.CTkLabel(
            list_card,
            text="Faculty Records",
            font=("Arial", 18, "bold"),
            text_color=("#111827", "#F8FAFC")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            list_card,
            text="Manage faculty members and add their workloads.",
            font=("Arial", 12),
            text_color=("#71717A", "#A1A1AA")
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
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=8
        )

        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

    # =====================================================
    # LOAD FACULTY
    # =====================================================

    def load_faculty(self):

        records = get_all_faculty()

        self.display_records(records)

    # =====================================================
    # DISPLAY RECORDS
    # =====================================================

    def display_records(self, records):

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        headers = [
            "Faculty ID",
            "Faculty Name",
            "Department",
            "Email",
            "Phone",
            "Action"
        ]

        widths = [
            120,
            190,
            140,
            250,
            150,
            270
        ]

        # =================================================
        # TABLE HEADER
        # =================================================

        for column, (header, width) in enumerate(
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
        # NO RECORDS
        # =================================================

        if not records:

            ctk.CTkLabel(
                self.list_frame,
                text="No faculty records found.",
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
        # RECORD ROWS
        # =================================================

        for row_number, record in enumerate(
            records,
            start=1
        ):

            record_id = record[0]
            faculty_id = record[1]
            name = record[2]
            department = record[3]
            email = record[4]
            phone = record[5]

            values = [
                faculty_id or "-",
                name or "-",
                department or "-",
                email or "-",
                phone or "-"
            ]

            # =================================================
            # DATA COLUMNS
            # =================================================

            for column, (value, width) in enumerate(
                zip(values, widths)
            ):

                ctk.CTkLabel(
                    self.list_frame,
                    text=str(value),
                    width=width,
                    height=42,
                    font=("Arial", 12),
                    text_color=("#374151", "#E2E8F0"),
                    fg_color=("#F4F4F5", "#2C2C2C"),
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
            # ACTION COLUMN
            # =================================================

            action_frame = ctk.CTkFrame(
                self.list_frame,
                width=270,
                height=42,
                fg_color=("#F4F4F5", "#2C2C2C"),
                corner_radius=4
            )

            action_frame.grid(
                row=row_number,
                column=5,
                padx=3,
                pady=3,
                sticky="ew"
            )

            action_frame.grid_propagate(False)

            # =================================================
            # SELECT
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Select",
                width=65,
                height=30,
                command=lambda r=record:
                    self.select_record(r)
            ).pack(
                side="left",
                padx=(7, 3),
                pady=6
            )

            # =================================================
            # ADD WORKLOAD
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Add Workload",
                width=105,
                height=30,
                command=lambda rid=record_id:
                    self.open_workload(rid)
            ).pack(
                side="left",
                padx=3,
                pady=6
            )

            # =================================================
            # DELETE
            # =================================================

            ctk.CTkButton(
                action_frame,
                text="Delete",
                width=65,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda rid=record_id,
                           fname=name:
                    self.delete_faculty_record(
                        rid,
                        fname
                    )
            ).pack(
                side="left",
                padx=(3, 7),
                pady=6
            )

    # =====================================================
    # VALIDATE FORM
    # =====================================================

    def validate_form(self):

        faculty_id = (
            self.faculty_id_entry
            .get()
            .strip()
        )

        name = (
            self.name_entry
            .get()
            .strip()
        )

        department = (
            self.department_entry
            .get()
            .strip()
        )

        email = (
            self.email_entry
            .get()
            .strip()
        )

        phone = (
            self.phone_entry
            .get()
            .strip()
        )

        # =================================================
        # REQUIRED FIELDS
        # =================================================

        if not name:

            messagebox.showwarning(
                "Missing Information",
                "Faculty Name is required.",
                parent=self.window
            )

            self.name_entry.focus()

            return None

        if not department:

            messagebox.showwarning(
                "Missing Information",
                "Department is required.",
                parent=self.window
            )

            self.department_entry.focus()

            return None

        # =================================================
        # EMAIL VALIDATION
        # =================================================

        if email:

            email_pattern = (
                r"^[A-Za-z0-9._%+-]+@"
                r"[A-Za-z0-9.-]+\."
                r"[A-Za-z]{2,}$"
            )

            if not re.match(
                email_pattern,
                email
            ):

                messagebox.showwarning(
                    "Invalid Email",
                    "Please enter a valid email address.",
                    parent=self.window
                )

                self.email_entry.focus()

                return None

        # =================================================
        # PHONE VALIDATION
        # =================================================

        if phone:

            if not phone.isdigit():

                messagebox.showwarning(
                    "Invalid Phone",
                    "Phone number must contain digits only.",
                    parent=self.window
                )

                self.phone_entry.focus()

                return None

            if len(phone) != 10:

                messagebox.showwarning(
                    "Invalid Phone",
                    "Phone number must contain exactly 10 digits.",
                    parent=self.window
                )

                self.phone_entry.focus()

                return None

        return (
            faculty_id or None,
            name,
            department,
            email,
            phone
        )

    # =====================================================
    # ADD FACULTY
    # =====================================================

    def add_faculty_record(self):

        data = self.validate_form()

        if data is None:
            return

        (
            faculty_id,
            name,
            department,
            email,
            phone
        ) = data

        success = add_faculty(
            faculty_id,
            name,
            department,
            email,
            phone
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Faculty added successfully.",
                parent=self.window
            )

            self.clear_form()
            self.load_faculty()

        else:

            messagebox.showerror(
                "Error",
                (
                    "Faculty ID already exists "
                    "or the faculty could not be added."
                ),
                parent=self.window
            )

    # =====================================================
    # SELECT FACULTY
    # =====================================================

    def select_record(self, record):

        self.selected_id = record[0]

        # Faculty ID
        self.faculty_id_entry.delete(
            0,
            "end"
        )

        if record[1]:
            self.faculty_id_entry.insert(
                0,
                record[1]
            )

        # Name
        self.name_entry.delete(
            0,
            "end"
        )

        self.name_entry.insert(
            0,
            record[2]
        )

        # Department
        self.department_entry.delete(
            0,
            "end"
        )

        self.department_entry.insert(
            0,
            record[3]
        )

        # Email
        self.email_entry.delete(
            0,
            "end"
        )

        if record[4]:
            self.email_entry.insert(
                0,
                record[4]
            )

        # Phone
        self.phone_entry.delete(
            0,
            "end"
        )

        if record[5]:
            self.phone_entry.insert(
                0,
                record[5]
            )

    # =====================================================
    # UPDATE FACULTY
    # =====================================================

    def update_faculty_record(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Select Faculty",
                "Please select a faculty record first.",
                parent=self.window
            )

            return

        data = self.validate_form()

        if data is None:
            return

        (
            faculty_id,
            name,
            department,
            email,
            phone
        ) = data

        success = update_faculty(
            self.selected_id,
            faculty_id,
            name,
            department,
            email,
            phone
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Faculty updated successfully.",
                parent=self.window
            )

            self.clear_form()
            self.load_faculty()

        else:

            messagebox.showerror(
                "Error",
                (
                    "Faculty ID already exists "
                    "or the faculty could not be updated."
                ),
                parent=self.window
            )

    # =====================================================
    # DELETE FACULTY
    # =====================================================

    def delete_faculty_record(
        self,
        record_id,
        faculty_name
    ):

        confirm = messagebox.askyesno(
            "Delete Faculty",
            (
                f'Are you sure you want to delete\n'
                f'"{faculty_name}"?\n\n'
                "All related workloads will also be removed."
            ),
            parent=self.window
        )

        if not confirm:
            return

        delete_faculty(record_id)

        self.clear_form()
        self.load_faculty()

        messagebox.showinfo(
            "Deleted",
            (
                f'Faculty "{faculty_name}" '
                "deleted successfully."
            ),
            parent=self.window
        )

    # =====================================================
    # OPEN FACULTY WORKLOAD MANAGEMENT
    # =====================================================

    def open_workload(self, faculty_id):

        try:

            from ui.assignments import AssignmentsWindow

            if self.embedded and self.navigate:
                self.navigate("assignments")
                return

            workload_window = AssignmentsWindow(
                self.window,
                preselected_faculty_id=faculty_id
            )

            return workload_window

        except Exception as error:

            messagebox.showerror(
                "Unable to Open Workload",
                (
                    "Faculty Workload Management "
                    "could not be opened.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

            return None

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

            self.load_faculty()

            return

        records = search_faculty(
            search_text
        )

        self.display_records(records)

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_form(self):

        self.selected_id = None

        self.faculty_id_entry.delete(
            0,
            "end"
        )

        self.name_entry.delete(
            0,
            "end"
        )

        self.department_entry.delete(
            0,
            "end"
        )

        self.email_entry.delete(
            0,
            "end"
        )

        self.phone_entry.delete(
            0,
            "end"
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

    app = FacultyWindow()
    app.run()
