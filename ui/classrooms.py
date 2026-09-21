import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    add_classroom,
    get_all_classrooms,
    update_classroom,
    delete_classroom,
    search_classrooms
)


class ClassroomsWindow:

    def __init__(self, parent):

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Classrooms")
        self.window.geometry("1100x700")
        self.window.minsize(950, 600)

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

        self.selected_id = None

        # =========================
        # MAIN FRAME
        # =========================

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color="white"
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
            text="Classroom Management",
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

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text=(
                "Add and manage classrooms, laboratories "
                "and other learning spaces."
            ),
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )

        subtitle.pack(
            anchor="w",
            padx=30,
            pady=(0, 20)
        )

        # =========================
        # FORM FRAME
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

        # =========================
        # ROOM NUMBER
        # =========================

        room_number_label = ctk.CTkLabel(
            form_frame,
            text="Room Number *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        room_number_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=(18, 5),
            sticky="w"
        )

        self.room_number_entry = ctk.CTkEntry(
            form_frame,
            width=220,
            height=38,
            placeholder_text="Example: A101"
        )

        self.room_number_entry.grid(
            row=1,
            column=0,
            padx=(20, 10),
            pady=(0, 15)
        )

        # =========================
        # ROOM NAME
        # =========================

        room_name_label = ctk.CTkLabel(
            form_frame,
            text="Room Name *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        room_name_label.grid(
            row=0,
            column=1,
            padx=10,
            pady=(18, 5),
            sticky="w"
        )

        self.room_name_entry = ctk.CTkEntry(
            form_frame,
            width=220,
            height=38,
            placeholder_text="Example: BCA Classroom"
        )

        self.room_name_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # FLOORS
        # =========================

        floors_label = ctk.CTkLabel(
            form_frame,
            text="Floors *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        floors_label.grid(
            row=0,
            column=2,
            padx=10,
            pady=(18, 5),
            sticky="w"
        )

        self.building_entry = ctk.CTkEntry(
            form_frame,
            width=200,
            height=38,
            placeholder_text="Example: Ground Floor"
        )

        self.building_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 15)
        )

        # =========================
        # ROOM TYPE
        # =========================

        room_type_label = ctk.CTkLabel(
            form_frame,
            text="Room Type *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        room_type_label.grid(
            row=2,
            column=0,
            padx=(20, 10),
            pady=(5, 5),
            sticky="w"
        )

        self.room_type_menu = ctk.CTkOptionMenu(
            form_frame,
            width=220,
            height=38,
            values=[
                "Classroom",
                "Computer Lab",
                "Laboratory",
                "Seminar Hall",
                "Auditorium"
            ]
        )

        self.room_type_menu.set(
            "Classroom"
        )

        self.room_type_menu.grid(
            row=3,
            column=0,
            padx=(20, 10),
            pady=(0, 18)
        )

        # =========================
        # CAPACITY
        # =========================

        capacity_label = ctk.CTkLabel(
            form_frame,
            text="Capacity *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#111827"
        )

        capacity_label.grid(
            row=2,
            column=1,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        self.capacity_entry = ctk.CTkEntry(
            form_frame,
            width=220,
            height=38,
            placeholder_text="Example: 60"
        )

        self.capacity_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=(0, 18)
        )

        # =========================
        # BUTTON FRAME
        # =========================

        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        # =========================
        # ADD BUTTON
        # =========================

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Classroom",
            width=140,
            height=38,
            command=self.add_classroom_record
        )

        self.add_button.pack(
            side="left",
            padx=(0, 10)
        )

        # =========================
        # UPDATE BUTTON
        # =========================

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update",
            width=110,
            height=38,
            command=self.update_classroom_record
        )

        self.update_button.pack(
            side="left",
            padx=5
        )

        # =========================
        # CLEAR BUTTON
        # =========================

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

        # =========================
        # SEARCH FRAME
        # =========================

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
            placeholder_text="Search classroom..."
        )

        self.search_entry.pack(
            side="left",
            padx=(0, 10)
        )

        # =========================
        # SEARCH BUTTON
        # =========================

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

        # =========================
        # SHOW ALL BUTTON
        # =========================

        self.show_all_button = ctk.CTkButton(
            search_frame,
            text="Show All",
            width=100,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_classrooms
        )

        self.show_all_button.pack(
            side="left",
            padx=5
        )

        # =========================
        # TABLE FRAME
        # =========================

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

        # =========================
        # LOAD DATA
        # =========================

        self.load_classrooms()

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_form(self):

        room_number = self.room_number_entry.get().strip()
        room_name = self.room_name_entry.get().strip()

        # Internal variable remains building_entry
        # because database column is still "building".
        floors = self.building_entry.get().strip()

        room_type = self.room_type_menu.get()
        capacity = self.capacity_entry.get().strip()

        # -------------------------
        # ROOM NUMBER
        # -------------------------

        if not room_number:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the room number."
            )

            self.room_number_entry.focus()

            return None

        # -------------------------
        # ROOM NAME
        # -------------------------

        if not room_name:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the room name."
            )

            self.room_name_entry.focus()

            return None

        # -------------------------
        # FLOORS
        # -------------------------

        if not floors:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the floor name."
            )

            self.building_entry.focus()

            return None

        # -------------------------
        # ROOM TYPE
        # -------------------------

        if not room_type:

            messagebox.showwarning(
                "Validation Error",
                "Please select a room type."
            )

            return None

        # -------------------------
        # CAPACITY
        # -------------------------

        if not capacity:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the classroom capacity."
            )

            self.capacity_entry.focus()

            return None

        if not capacity.isdigit():

            messagebox.showwarning(
                "Validation Error",
                "Capacity must contain numbers only."
            )

            self.capacity_entry.focus()

            return None

        capacity_value = int(capacity)

        if capacity_value < 1 or capacity_value > 1000:

            messagebox.showwarning(
                "Validation Error",
                "Capacity must be between 1 and 1000."
            )

            self.capacity_entry.focus()

            return None

        return (
            room_number,
            room_name,
            floors,
            room_type,
            capacity_value
        )

    # =====================================================
    # ADD CLASSROOM
    # =====================================================

    def add_classroom_record(self):

        data = self.validate_form()

        if data is None:
            return

        (
            room_number,
            room_name,
            floors,
            room_type,
            capacity
        ) = data

        success = add_classroom(
            room_number,
            room_name,
            floors,
            room_type,
            capacity
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Classroom added successfully."
            )

            self.clear_form()
            self.load_classrooms()

        else:

            messagebox.showerror(
                "Error",
                "Room Number already exists."
            )

    # =====================================================
    # UPDATE CLASSROOM
    # =====================================================

    def update_classroom_record(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Update Classroom",
                "Please select a classroom from the list first."
            )

            return

        data = self.validate_form()

        if data is None:
            return

        (
            room_number,
            room_name,
            floors,
            room_type,
            capacity
        ) = data

        success = update_classroom(
            self.selected_id,
            room_number,
            room_name,
            floors,
            room_type,
            capacity
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Classroom updated successfully."
            )

            self.clear_form()
            self.load_classrooms()

        else:

            messagebox.showerror(
                "Error",
                "Room Number already exists."
            )

    # =====================================================
    # LOAD CLASSROOMS
    # =====================================================

    def load_classrooms(self):

        classrooms = get_all_classrooms()

        self.display_classrooms(
            classrooms
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search_records(self):

        search_text = self.search_entry.get().strip()

        if not search_text:

            self.load_classrooms()

            return

        results = search_classrooms(
            search_text
        )

        self.display_classrooms(
            results
        )

    # =====================================================
    # DISPLAY CLASSROOMS
    # =====================================================

    def display_classrooms(self, classrooms):

        # Clear previous rows

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # =========================
        # TABLE HEADERS
        # =========================

        headers = [
            "Room No.",
            "Room Name",
            "Floors",
            "Room Type",
            "Capacity",
            "Action"
        ]

        column_widths = [
            120,
            190,
            150,
            170,
            100,
            130
        ]

        for column, (header, width) in enumerate(
            zip(headers, column_widths)
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
        # NO RECORDS
        # =========================

        if not classrooms:

            empty_label = ctk.CTkLabel(
                self.table_frame,
                text="No classrooms found.",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )

            empty_label.grid(
                row=1,
                column=0,
                columnspan=6,
                pady=30
            )

            return

        # =========================
        # DATA ROWS
        # =========================

        for row_index, classroom in enumerate(
            classrooms,
            start=1
        ):

            record_id = classroom[0]

            room_number = classroom[1]
            room_name = classroom[2]
            floors = classroom[3]
            room_type = classroom[4]
            capacity = classroom[5]

            values = [
                room_number,
                room_name,
                floors,
                room_type,
                str(capacity)
            ]

            # -------------------------
            # DATA COLUMNS
            # -------------------------

            for column, (value, width) in enumerate(
                zip(values, column_widths)
            ):

                label = ctk.CTkLabel(
                    self.table_frame,
                    text=value,
                    width=width,
                    height=38,
                    font=ctk.CTkFont(size=12),
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

                label.bind(
                    "<Button-1>",
                    lambda event, rid=record_id:
                    self.select_classroom(rid)
                )

            # -------------------------
            # SELECT BUTTON
            # -------------------------

            select_button = ctk.CTkButton(
                self.table_frame,
                text="Select",
                width=55,
                height=30,
                command=lambda rid=record_id:
                self.select_classroom(rid)
            )

            select_button.grid(
                row=row_index,
                column=5,
                padx=(3, 65),
                pady=4
            )

            # -------------------------
            # DELETE BUTTON
            # -------------------------

            delete_button = ctk.CTkButton(
                self.table_frame,
                text="🗑",
                width=40,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                font=ctk.CTkFont(size=14),
                command=lambda rid=record_id:
                self.confirm_delete(rid)
            )

            delete_button.grid(
                row=row_index,
                column=5,
                padx=(75, 3),
                pady=4
            )

    # =====================================================
    # SELECT CLASSROOM
    # =====================================================

    def select_classroom(self, record_id):

        classrooms = get_all_classrooms()

        selected = None

        for classroom in classrooms:

            if classroom[0] == record_id:

                selected = classroom

                break

        if selected is None:
            return

        self.selected_id = selected[0]

        # Room Number

        self.room_number_entry.delete(
            0,
            "end"
        )

        self.room_number_entry.insert(
            0,
            selected[1]
        )

        # Room Name

        self.room_name_entry.delete(
            0,
            "end"
        )

        self.room_name_entry.insert(
            0,
            selected[2]
        )

        # Floors

        self.building_entry.delete(
            0,
            "end"
        )

        self.building_entry.insert(
            0,
            selected[3]
        )

        # Room Type

        self.room_type_menu.set(
            selected[4]
        )

        # Capacity

        self.capacity_entry.delete(
            0,
            "end"
        )

        self.capacity_entry.insert(
            0,
            selected[5]
        )

    # =====================================================
    # DELETE CONFIRMATION
    # =====================================================

    def confirm_delete(self, record_id):

        confirm = messagebox.askyesno(
            "Delete Classroom",
            "Are you sure you want to delete this classroom?"
        )

        if not confirm:
            return

        delete_classroom(
            record_id
        )

        if self.selected_id == record_id:

            self.clear_form()

        self.load_classrooms()

        messagebox.showinfo(
            "Deleted",
            "Classroom deleted successfully."
        )

    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form(self):

        self.selected_id = None

        self.room_number_entry.delete(
            0,
            "end"
        )

        self.room_name_entry.delete(
            0,
            "end"
        )

        self.building_entry.delete(
            0,
            "end"
        )

        self.room_type_menu.set(
            "Classroom"
        )

        self.capacity_entry.delete(
            0,
            "end"
        )

    # =====================================================
    # CLOSE WINDOW
    # =====================================================

    def close_window(self):

        self.window.destroy()


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()

    root.withdraw()

    app = ClassroomsWindow(root)

    root.mainloop()