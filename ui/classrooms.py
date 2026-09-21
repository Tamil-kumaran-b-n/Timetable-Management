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

    def __init__(self, parent, container=None):

        self.embedded = container is not None
        self.window = container if self.embedded else ctk.CTkToplevel(parent)

        if not self.embedded:
            self.window.title("Classroom Management")
            self.window.geometry("1150x720")
            self.window.minsize(1000, 650)
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.selected_id = None

        # ====================================================
        # COLORS
        # ====================================================

        self.bg_color = ("#F4F4F5", "#121212")
        self.card_color = ("#FFFFFF", "#1E1E1E")
        self.header_color = ("#E4E4E7", "#27272A")
        self.row_color = ("#FFFFFF", "#1E1E1E")
        self.text_color = ("#18181B", "#F4F4F5")
        self.secondary_text = ("#71717A", "#A1A1AA")
        self.border_color = ("#E4E4E7", "#383838")

        self.button_blue = "#3B92D0"
        self.button_blue_hover = "#2F7FB9"

        self.delete_red = "#DC2626"
        self.delete_red_hover = "#B91C1C"

        self.gray_button = "#6B7280"
        self.gray_button_hover = "#4B5563"

        # ====================================================
        # MAIN CONTAINER
        # ====================================================

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color=self.bg_color,
            corner_radius=0
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # HEADER
        # ====================================================

        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header_frame.pack(
            fill="x",
            padx=30,
            pady=(24, 4)
        )

        title = ctk.CTkLabel(
            header_frame,
            text="Classroom Management",
            font=ctk.CTkFont(
                size=27,
                weight="bold"
            ),
            text_color=self.text_color
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            header_frame,
            text=(
                "Add and manage classrooms, laboratories "
                "and other learning spaces."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color=self.secondary_text
        )

        subtitle.pack(
            anchor="w",
            pady=(3, 16)
        )

        # ====================================================
        # FORM CARD
        # ====================================================

        form_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.card_color,
            corner_radius=12,
            border_width=1,
            border_color=self.border_color
        )

        form_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        # Configure columns

        form_frame.grid_columnconfigure(
            0,
            weight=1
        )

        form_frame.grid_columnconfigure(
            1,
            weight=1
        )

        form_frame.grid_columnconfigure(
            2,
            weight=1
        )

        # ====================================================
        # ROOM NUMBER
        # ====================================================

        room_number_label = ctk.CTkLabel(
            form_frame,
            text="Room Number *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )

        room_number_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=(16, 5),
            sticky="w"
        )

        self.room_number_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Example: 01",
            corner_radius=7,
            border_width=1
        )

        self.room_number_entry.grid(
            row=1,
            column=0,
            padx=(20, 10),
            pady=(0, 14),
            sticky="ew"
        )

        # ====================================================
        # ROOM NAME
        # ====================================================

        room_name_label = ctk.CTkLabel(
            form_frame,
            text="Room Name *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )

        room_name_label.grid(
            row=0,
            column=1,
            padx=10,
            pady=(16, 5),
            sticky="w"
        )

        self.room_name_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Example: BCA",
            corner_radius=7,
            border_width=1
        )

        self.room_name_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 14),
            sticky="ew"
        )

        # ====================================================
        # FLOORS
        # ====================================================

        floors_label = ctk.CTkLabel(
            form_frame,
            text="Floors *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )

        floors_label.grid(
            row=0,
            column=2,
            padx=(10, 20),
            pady=(16, 5),
            sticky="w"
        )

        self.building_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Example: 1st Floor",
            corner_radius=7,
            border_width=1
        )

        self.building_entry.grid(
            row=1,
            column=2,
            padx=(10, 20),
            pady=(0, 14),
            sticky="ew"
        )

        # ====================================================
        # ROOM TYPE
        # ====================================================

        room_type_label = ctk.CTkLabel(
            form_frame,
            text="Room Type *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )

        room_type_label.grid(
            row=2,
            column=0,
            padx=(20, 10),
            pady=(2, 5),
            sticky="w"
        )

        self.room_type_menu = ctk.CTkOptionMenu(
            form_frame,
            height=38,
            values=[
                "Classroom",
                "Computer Lab",
                "Laboratory",
                "Seminar Hall",
                "Auditorium"
            ],
            corner_radius=7,
            fg_color=self.button_blue,
            button_color=self.button_blue,
            button_hover_color=self.button_blue_hover
        )

        self.room_type_menu.set(
            "Classroom"
        )

        self.room_type_menu.grid(
            row=3,
            column=0,
            padx=(20, 10),
            pady=(0, 16),
            sticky="ew"
        )

        # ====================================================
        # CAPACITY
        # ====================================================

        capacity_label = ctk.CTkLabel(
            form_frame,
            text="Capacity *",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.text_color
        )

        capacity_label.grid(
            row=2,
            column=1,
            padx=10,
            pady=(2, 5),
            sticky="w"
        )

        self.capacity_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Example: 40",
            corner_radius=7,
            border_width=1
        )

        self.capacity_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=(0, 16),
            sticky="ew"
        )

        # ====================================================
        # BUTTON BAR
        # ====================================================

        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 14)
        )

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Classroom",
            width=140,
            height=38,
            corner_radius=7,
            fg_color=self.button_blue,
            hover_color=self.button_blue_hover,
            command=self.add_classroom_record
        )

        self.add_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update",
            width=110,
            height=38,
            corner_radius=7,
            fg_color=self.button_blue,
            hover_color=self.button_blue_hover,
            command=self.update_classroom_record
        )

        self.update_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=100,
            height=38,
            corner_radius=7,
            fg_color=self.gray_button,
            hover_color=self.gray_button_hover,
            command=self.clear_form
        )

        self.clear_button.pack(
            side="left"
        )

        # ====================================================
        # SEARCH BAR CARD
        # ====================================================

        search_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.card_color,
            corner_radius=10,
            border_width=1,
            border_color=self.border_color
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 12)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=38,
            width=320,
            placeholder_text="Search classroom...",
            corner_radius=7,
            border_width=1
        )

        self.search_entry.pack(
            side="left",
            padx=(12, 8),
            pady=10
        )

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            height=38,
            corner_radius=7,
            fg_color=self.button_blue,
            hover_color=self.button_blue_hover,
            command=self.search_records
        )

        self.search_button.pack(
            side="left",
            padx=5,
            pady=10
        )

        self.show_all_button = ctk.CTkButton(
            search_frame,
            text="Show All",
            width=100,
            height=38,
            corner_radius=7,
            fg_color=self.gray_button,
            hover_color=self.gray_button_hover,
            command=self.load_classrooms
        )

        self.show_all_button.pack(
            side="left",
            padx=5,
            pady=10
        )

        # ====================================================
        # TABLE CARD
        # ====================================================

        self.table_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.card_color,
            corner_radius=10,
            border_width=1,
            border_color=self.border_color
        )

        self.table_card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25)
        )

        # ====================================================
        # SCROLLABLE TABLE
        # ====================================================

        self.table_frame = ctk.CTkScrollableFrame(
            self.table_card,
            fg_color="transparent",
            corner_radius=8
        )

        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # ====================================================
        # INITIAL LOAD
        # ====================================================

        self.load_classrooms()

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_form(self):

        room_number = (
            self.room_number_entry
            .get()
            .strip()
        )

        room_name = (
            self.room_name_entry
            .get()
            .strip()
        )

        floors = (
            self.building_entry
            .get()
            .strip()
        )

        room_type = (
            self.room_type_menu
            .get()
            .strip()
        )

        capacity = (
            self.capacity_entry
            .get()
            .strip()
        )

        # --------------------------------------------
        # ROOM NUMBER
        # --------------------------------------------

        if not room_number:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the room number."
            )

            self.room_number_entry.focus()

            return None

        # --------------------------------------------
        # ROOM NAME
        # --------------------------------------------

        if not room_name:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the room name."
            )

            self.room_name_entry.focus()

            return None

        # --------------------------------------------
        # FLOORS
        # --------------------------------------------

        if not floors:

            messagebox.showwarning(
                "Validation Error",
                "Please enter the floor name."
            )

            self.building_entry.focus()

            return None

        # --------------------------------------------
        # ROOM TYPE
        # --------------------------------------------

        if not room_type:

            messagebox.showwarning(
                "Validation Error",
                "Please select a room type."
            )

            return None

        # --------------------------------------------
        # CAPACITY
        # --------------------------------------------

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

        capacity_value = int(
            capacity
        )

        if (
            capacity_value < 1
            or capacity_value > 1000
        ):

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

    # ========================================================
    # ADD
    # ========================================================

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

    # ========================================================
    # UPDATE
    # ========================================================

    def update_classroom_record(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Update Classroom",
                "Please select a classroom from the table first."
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

    # ========================================================
    # LOAD
    # ========================================================

    def load_classrooms(self):

        classrooms = get_all_classrooms()

        self.display_classrooms(
            classrooms
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_records(self):

        search_text = (
            self.search_entry
            .get()
            .strip()
        )

        if not search_text:

            self.load_classrooms()

            return

        results = search_classrooms(
            search_text
        )

        self.display_classrooms(
            results
        )

    # ========================================================
    # DISPLAY TABLE
    # ========================================================

    def display_classrooms(
        self,
        classrooms
    ):

        # --------------------------------------------
        # Clear old widgets
        # --------------------------------------------

        for widget in (
            self.table_frame
            .winfo_children()
        ):

            widget.destroy()

        # --------------------------------------------
        # Column configuration
        # --------------------------------------------

        columns = [
            ("Room No.", 120),
            ("Room Name", 190),
            ("Floors", 160),
            ("Room Type", 180),
            ("Capacity", 110),
            ("Action", 210)
        ]

        # --------------------------------------------
        # Configure table columns
        # --------------------------------------------

        for index in range(
            len(columns)
        ):

            self.table_frame.grid_columnconfigure(
                index,
                weight=0
            )

        # --------------------------------------------
        # Header row
        # --------------------------------------------

        for column, (
            header,
            width
        ) in enumerate(columns):

            header_label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                width=width,
                height=38,
                fg_color=self.header_color,
                text_color=self.text_color,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                corner_radius=5,
                anchor="center"
            )

            header_label.grid(
                row=0,
                column=column,
                padx=3,
                pady=3,
                sticky="ew"
            )

        # --------------------------------------------
        # Empty state
        # --------------------------------------------

        if not classrooms:

            empty_label = ctk.CTkLabel(
                self.table_frame,
                text="No classrooms found.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color=self.secondary_text
            )

            empty_label.grid(
                row=1,
                column=0,
                columnspan=6,
                pady=35
            )

            return

        # --------------------------------------------
        # Data rows
        # --------------------------------------------

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

            # ----------------------------------------
            # Row background
            # ----------------------------------------

            row_bg = ("#FFFFFF", "#1E1E1E") if row_index % 2 == 1 else ("#F9FAFB", "#242424")

            # ----------------------------------------
            # Data cells
            # ----------------------------------------

            for column, (
                value,
                column_info
            ) in enumerate(
                zip(
                    values,
                    columns[:5]
                )
            ):

                width = column_info[1]

                cell = ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    width=width,
                    height=42,
                    fg_color=row_bg,
                    text_color=("#374151", "#E2E8F0"),
                    font=ctk.CTkFont(
                        size=12
                    ),
                    anchor="w"
                )

                cell.grid(
                    row=row_index,
                    column=column,
                    padx=3,
                    pady=2,
                    sticky="ew"
                )

                # Clicking row data selects record
                cell.bind(
                    "<Button-1>",
                    lambda event,
                    rid=record_id:
                    self.select_classroom(rid)
                )

            # ----------------------------------------
            # ACTION CONTAINER
            # ----------------------------------------

            action_frame = ctk.CTkFrame(
                self.table_frame,
                width=210,
                height=42,
                fg_color=row_bg,
                corner_radius=0
            )

            action_frame.grid(
                row=row_index,
                column=5,
                padx=3,
                pady=2,
                sticky="ew"
            )

            action_frame.grid_propagate(
                False
            )

            # ----------------------------------------
            # Select button
            # ----------------------------------------

            select_button = ctk.CTkButton(
                action_frame,
                text="Select",
                width=68,
                height=30,
                corner_radius=6,
                fg_color=self.button_blue,
                hover_color=self.button_blue_hover,
                font=ctk.CTkFont(
                    size=12
                ),
                command=lambda rid=record_id:
                self.select_classroom(rid)
            )

            select_button.pack(
                side="left",
                padx=(8, 5),
                pady=6
            )

            # ----------------------------------------
            # Delete button
            # ----------------------------------------

            delete_button = ctk.CTkButton(
                action_frame,
                text="Delete",
                width=68,
                height=30,
                corner_radius=6,
                fg_color=self.delete_red,
                hover_color=self.delete_red_hover,
                font=ctk.CTkFont(
                    size=12
                ),
                command=lambda rid=record_id:
                self.confirm_delete(rid)
            )

            delete_button.pack(
                side="left",
                padx=5,
                pady=6
            )

    # ========================================================
    # SELECT
    # ========================================================

    def select_classroom(
        self,
        record_id
    ):

        classrooms = get_all_classrooms()

        selected = None

        for classroom in classrooms:

            if classroom[0] == record_id:

                selected = classroom

                break

        if selected is None:
            return

        self.selected_id = selected[0]

        # --------------------------------------------
        # Room Number
        # --------------------------------------------

        self.room_number_entry.delete(
            0,
            "end"
        )

        self.room_number_entry.insert(
            0,
            selected[1]
        )

        # --------------------------------------------
        # Room Name
        # --------------------------------------------

        self.room_name_entry.delete(
            0,
            "end"
        )

        self.room_name_entry.insert(
            0,
            selected[2]
        )

        # --------------------------------------------
        # Floors
        # --------------------------------------------

        self.building_entry.delete(
            0,
            "end"
        )

        self.building_entry.insert(
            0,
            selected[3]
        )

        # --------------------------------------------
        # Room Type
        # --------------------------------------------

        self.room_type_menu.set(
            selected[4]
        )

        # --------------------------------------------
        # Capacity
        # --------------------------------------------

        self.capacity_entry.delete(
            0,
            "end"
        )

        self.capacity_entry.insert(
            0,
            selected[5]
        )

    # ========================================================
    # DELETE CONFIRMATION
    # ========================================================

    def confirm_delete(
        self,
        record_id
    ):

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

    # ========================================================
    # CLEAR FORM
    # ========================================================

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

    # ========================================================
    # CLOSE
    # ========================================================

    def close_window(self):

        if self.embedded:
            return

        self.window.destroy()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    ctk.set_appearance_mode(
        "light"
    )

    ctk.set_default_color_theme(
        "dark-blue"
    )

    root = ctk.CTk()

    root.withdraw()

    app = ClassroomsWindow(
        root
    )

    root.mainloop()
