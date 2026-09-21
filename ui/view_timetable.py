import customtkinter as ctk
from tkinter import messagebox, filedialog

from database.database import get_all_faculty, get_all_classes
from database.generator import (
    create_timetable_table,
    get_timetable_by_class,
    get_timetable_by_faculty,
    get_all_timetable,
)


class ViewTimetableWindow:
    def __init__(self, parent):
        self.parent = parent

        self.window = ctk.CTkToplevel(parent)
        self.window.title("View Timetable")
        self.window.geometry("1250x760")
        self.window.minsize(1050, 650)

        self.window.transient(parent)

        self.faculty_records = []
        self.class_records = []
        self.class_display_names = []

        self.current_mode = "class"
        self.current_id = None
        self.current_timetable_data = []

        self.build_ui()
        self.load_dropdowns()
        self.check_timetable()

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

    # ========================================================
    # MAIN UI
    # ========================================================

    def build_ui(self):

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            header_frame,
            text="View Timetable",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="View, refresh and download the generated timetable.",
            font=ctk.CTkFont(
                size=14
            ),
            text_color="gray"
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        # ----------------------------------------------------
        # VIEW MODE
        # ----------------------------------------------------

        mode_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )
        mode_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            mode_frame,
            text="View By",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        ).pack(
            side="left",
            padx=(20, 10),
            pady=18
        )

        self.class_mode_button = ctk.CTkButton(
            mode_frame,
            text="Class View",
            width=130,
            height=38,
            command=self.show_class_view
        )
        self.class_mode_button.pack(
            side="left",
            padx=5,
            pady=12
        )

        self.faculty_mode_button = ctk.CTkButton(
            mode_frame,
            text="Faculty View",
            width=130,
            height=38,
            fg_color="gray",
            hover_color="#555555",
            command=self.show_faculty_view
        )
        self.faculty_mode_button.pack(
            side="left",
            padx=5,
            pady=12
        )

        # ----------------------------------------------------
        # SELECTION FRAME
        # ----------------------------------------------------

        self.selection_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )
        self.selection_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.selection_label = ctk.CTkLabel(
            self.selection_frame,
            text="Select Class",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )
        self.selection_label.pack(
            side="left",
            padx=(20, 10),
            pady=18
        )

        self.selection_menu = ctk.CTkOptionMenu(
            self.selection_frame,
            width=360,
            height=40,
            command=self.selection_changed
        )
        self.selection_menu.pack(
            side="left",
            padx=5,
            pady=12
        )

        # Download button is placed beside Refresh.
        self.download_button = ctk.CTkButton(
            self.selection_frame,
            text="Download PDF",
            width=125,
            height=40,
            command=self.download_pdf,
            state="disabled"
        )
        self.download_button.pack(
            side="right",
            padx=(8, 20),
            pady=12
        )

        self.refresh_button = ctk.CTkButton(
            self.selection_frame,
            text="Refresh",
            width=100,
            height=40,
            command=self.refresh_timetable
        )
        self.refresh_button.pack(
            side="right",
            padx=8,
            pady=12
        )

        # ----------------------------------------------------
        # CURRENT VIEW TITLE
        # ----------------------------------------------------

        self.current_title = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )
        self.current_title.pack(
            anchor="w",
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # TIMETABLE CONTAINER
        # ----------------------------------------------------

        self.grid_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )
        self.grid_container.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # LOAD FACULTY AND CLASS DATA
    # ========================================================

    def load_dropdowns(self):

        try:
            self.faculty_records = get_all_faculty()
            self.class_records = get_all_classes()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Unable to load classes/faculty.\n\n{error}",
                parent=self.window
            )

            self.faculty_records = []
            self.class_records = []

        if self.class_records:
            self.load_class_dropdown()

        else:
            self.selection_menu.configure(
                values=["No Classes Available"]
            )
            self.selection_menu.set(
                "No Classes Available"
            )

    # ========================================================
    # CHECK GENERATED TIMETABLE
    # ========================================================

    def check_timetable(self):

        try:
            timetable = get_all_timetable()

            if not timetable:

                self.download_button.configure(
                    state="disabled"
                )

                self.show_empty_message(
                    "No timetable has been generated yet."
                )

                self.selection_menu.configure(
                    state="disabled"
                )

                return

            self.selection_menu.configure(
                state="normal"
            )

            self.show_class_view()

        except Exception as error:

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "Unable to load timetable."
            )

            messagebox.showerror(
                "Timetable Error",
                f"Unable to load timetable.\n\n{error}",
                parent=self.window
            )

    # ========================================================
    # CLASS VIEW
    # ========================================================

    def show_class_view(self):

        self.current_mode = "class"

        self.class_mode_button.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )

        self.faculty_mode_button.configure(
            fg_color="gray",
            hover_color="#555555"
        )

        self.selection_label.configure(
            text="Select Class"
        )

        self.load_class_dropdown()

        if self.selection_menu.get().startswith("No "):
            self.download_button.configure(
                state="disabled"
            )
            self.show_empty_message(
                "No classes available."
            )
            return

        self.selection_changed(
            self.selection_menu.get()
        )

    # ========================================================
    # FACULTY VIEW
    # ========================================================

    def show_faculty_view(self):

        self.current_mode = "faculty"

        self.faculty_mode_button.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )

        self.class_mode_button.configure(
            fg_color="gray",
            hover_color="#555555"
        )

        self.selection_label.configure(
            text="Select Faculty"
        )

        self.load_faculty_dropdown()

        if self.selection_menu.get().startswith("No "):
            self.download_button.configure(
                state="disabled"
            )
            self.show_empty_message(
                "No faculty available."
            )
            return

        self.selection_changed(
            self.selection_menu.get()
        )

    # ========================================================
    # LOAD CLASS DROPDOWN
    # ========================================================

    def load_class_dropdown(self):

        if not self.class_records:

            self.selection_menu.configure(
                values=["No Classes Available"],
                state="disabled"
            )

            self.selection_menu.set(
                "No Classes Available"
            )

            return

        values = []

        for record in self.class_records:

            class_name = record[1]

            department = (
                record[2]
                if len(record) > 2
                else ""
            )

            semester = (
                record[3]
                if len(record) > 3
                else ""
            )

            display_name = (
                f"{class_name} | "
                f"{department} | "
                f"Sem {semester}"
            )

            values.append(display_name)

        self.class_display_names = values

        self.selection_menu.configure(
            values=values,
            state="normal"
        )

        self.selection_menu.set(values[0])

    # ========================================================
    # LOAD FACULTY DROPDOWN
    # ========================================================

    def load_faculty_dropdown(self):

        if not self.faculty_records:

            self.selection_menu.configure(
                values=["No Faculty Available"],
                state="disabled"
            )

            self.selection_menu.set(
                "No Faculty Available"
            )

            return

        values = []

        for record in self.faculty_records:

            faculty_code = (
                record[1]
                if len(record) > 1
                else ""
            )

            faculty_name = (
                record[2]
                if len(record) > 2
                else ""
            )

            if faculty_code:

                display_name = (
                    f"{faculty_name} ({faculty_code})"
                )

            else:

                display_name = faculty_name

            values.append(display_name)

        self.selection_menu.configure(
            values=values,
            state="normal"
        )

        self.selection_menu.set(values[0])

    # ========================================================
    # SELECTION CHANGED
    # ========================================================

    def selection_changed(self, selected_value):

        if not selected_value:
            return

        if selected_value.startswith("No "):
            self.download_button.configure(
                state="disabled"
            )
            return

        try:

            if self.current_mode == "class":

                index = self.find_class_index(
                    selected_value
                )

                if index is None:
                    return

                class_id = self.class_records[index][0]
                self.current_id = class_id

                self.display_class_timetable(
                    class_id
                )

            else:

                index = self.find_faculty_index(
                    selected_value
                )

                if index is None:
                    return

                faculty_id = self.faculty_records[index][0]
                self.current_id = faculty_id

                self.display_faculty_timetable(
                    faculty_id
                )

        except Exception as error:

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "Unable to display timetable."
            )

            messagebox.showerror(
                "Display Error",
                str(error),
                parent=self.window
            )

    # ========================================================
    # FIND CLASS
    # ========================================================

    def find_class_index(self, selected_value):

        for index, record in enumerate(
            self.class_records
        ):

            class_name = record[1]

            department = (
                record[2]
                if len(record) > 2
                else ""
            )

            semester = (
                record[3]
                if len(record) > 3
                else ""
            )

            display_name = (
                f"{class_name} | "
                f"{department} | "
                f"Sem {semester}"
            )

            if display_name == selected_value:
                return index

        return None

    # ========================================================
    # FIND FACULTY
    # ========================================================

    def find_faculty_index(self, selected_value):

        for index, record in enumerate(
            self.faculty_records
        ):

            faculty_code = (
                record[1]
                if len(record) > 1
                else ""
            )

            faculty_name = (
                record[2]
                if len(record) > 2
                else ""
            )

            if faculty_code:

                display_name = (
                    f"{faculty_name} ({faculty_code})"
                )

            else:

                display_name = faculty_name

            if display_name == selected_value:
                return index

        return None

    # ========================================================
    # DISPLAY CLASS TIMETABLE
    # ========================================================

    def display_class_timetable(self, class_id):

        data = get_timetable_by_class(
            class_id
        )

        self.current_timetable_data = data or []

        self.current_title.configure(
            text=self.get_class_title(class_id)
        )

        self.draw_grid()

        if not data:

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "No timetable entries found for this class."
            )

            return

        self.download_button.configure(
            state="normal"
        )

        timetable_map = {}

        for row in data:

            day_order = row[0]
            period = row[1]

            class_name = row[2]
            subject_code = row[3]
            subject_name = row[4]
            faculty_name = row[5]

            timetable_map[
                (day_order, period)
            ] = {
                "class_name": class_name,
                "subject_code": subject_code,
                "subject_name": subject_name,
                "faculty_name": faculty_name
            }

        self.fill_grid(
            timetable_map,
            mode="class"
        )

    # ========================================================
    # DISPLAY FACULTY TIMETABLE
    # ========================================================

    def display_faculty_timetable(self, faculty_id):

        data = get_timetable_by_faculty(
            faculty_id
        )

        self.current_timetable_data = data or []

        self.current_title.configure(
            text=self.get_faculty_title(faculty_id)
        )

        self.draw_grid()

        if not data:

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "No timetable entries found for this faculty."
            )

            return

        self.download_button.configure(
            state="normal"
        )

        timetable_map = {}

        for row in data:

            day_order = row[0]
            period = row[1]

            faculty_name = row[2]
            class_name = row[3]
            subject_code = row[4]
            subject_name = row[5]

            timetable_map[
                (day_order, period)
            ] = {
                "faculty_name": faculty_name,
                "class_name": class_name,
                "subject_code": subject_code,
                "subject_name": subject_name
            }

        self.fill_grid(
            timetable_map,
            mode="faculty"
        )

    # ========================================================
    # DRAW 6 x 5 GRID
    # ========================================================

    def draw_grid(self):

        for widget in self.grid_container.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.grid_container,
            text="Day Order",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            corner_radius=8
        )

        header.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=4,
            pady=4,
            ipadx=5,
            ipady=8
        )

        for period in range(1, 6):

            label = ctk.CTkLabel(
                self.grid_container,
                text=f"Period {period}",
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                ),
                corner_radius=8
            )

            label.grid(
                row=0,
                column=period,
                sticky="nsew",
                padx=4,
                pady=4,
                ipadx=5,
                ipady=8
            )

        for day_order in range(1, 7):

            label = ctk.CTkLabel(
                self.grid_container,
                text=f"Day Order {day_order}",
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                ),
                corner_radius=8
            )

            label.grid(
                row=day_order,
                column=0,
                sticky="nsew",
                padx=4,
                pady=4,
                ipadx=5,
                ipady=8
            )

        for column in range(6):

            self.grid_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="timetable_column"
            )

        for row in range(7):

            self.grid_container.grid_rowconfigure(
                row,
                weight=1,
                uniform="timetable_row"
            )

    # ========================================================
    # FILL GRID
    # ========================================================

    def fill_grid(self, timetable_map, mode):

        for widget in self.grid_container.winfo_children():

            info = widget.grid_info()
            row = int(info.get("row", 0))

            if row > 0:
                widget.destroy()

        for day_order in range(1, 7):

            for period in range(1, 6):

                entry = timetable_map.get(
                    (day_order, period)
                )

                if entry:

                    if mode == "class":

                        text = (
                            f"{entry['subject_code']}\n"
                            f"{entry['subject_name']}\n"
                            f"{entry['faculty_name']}"
                        )

                    else:

                        text = (
                            f"{entry['subject_code']}\n"
                            f"{entry['subject_name']}\n"
                            f"{entry['class_name']}"
                        )

                else:

                    text = "FREE"

                cell = ctk.CTkFrame(
                    self.grid_container,
                    corner_radius=8
                )

                cell.grid(
                    row=day_order,
                    column=period,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

                label = ctk.CTkLabel(
                    cell,
                    text=text,
                    justify="center",
                    anchor="center",
                    font=ctk.CTkFont(
                        size=10,
                        weight="bold" if entry else "normal"
                    ),
                    wraplength=150
                )

                label.pack(
                    fill="both",
                    expand=True,
                    padx=4,
                    pady=4
                )

        for column in range(6):

            self.grid_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="timetable_column"
            )

        for row in range(7):

            self.grid_container.grid_rowconfigure(
                row,
                weight=1,
                uniform="timetable_row"
            )

    # ========================================================
    # EMPTY MESSAGE
    # ========================================================

    def show_empty_message(self, message):

        for widget in self.grid_container.winfo_children():
            widget.destroy()

        empty_label = ctk.CTkLabel(
            self.grid_container,
            text=message,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color="gray"
        )

        empty_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # ========================================================
    # GET CLASS TITLE
    # ========================================================

    def get_class_title(self, class_id):

        for record in self.class_records:

            if record[0] == class_id:

                class_name = record[1]

                department = (
                    record[2]
                    if len(record) > 2
                    else ""
                )

                semester = (
                    record[3]
                    if len(record) > 3
                    else ""
                )

                return (
                    f"{class_name}  •  "
                    f"{department}  •  "
                    f"Semester {semester}"
                )

        return "Class Timetable"

    # ========================================================
    # GET FACULTY TITLE
    # ========================================================

    def get_faculty_title(self, faculty_id):

        for record in self.faculty_records:

            if record[0] == faculty_id:

                faculty_code = (
                    record[1]
                    if len(record) > 1
                    else ""
                )

                faculty_name = (
                    record[2]
                    if len(record) > 2
                    else ""
                )

                if faculty_code:

                    return (
                        f"{faculty_name}  •  "
                        f"{faculty_code}"
                    )

                return faculty_name

        return "Faculty Timetable"

    # ========================================================
    # DOWNLOAD TIMETABLE AS PDF
    # ========================================================

    def download_pdf(self):

        if not self.current_timetable_data:
            messagebox.showwarning(
                "No Timetable",
                "There is no timetable available to download.",
                parent=self.window
            )
            return

        try:

            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )

        except ImportError:

            messagebox.showerror(
                "Missing Package",
                (
                    "ReportLab is not installed.\n\n"
                    "Install it using:\n"
                    "pip install reportlab"
                ),
                parent=self.window
            )
            return

        # ----------------------------------------------------
        # Default file name
        # ----------------------------------------------------

        if self.current_mode == "class":

            title_name = self.get_class_title(
                self.current_id
            )

            safe_name = (
                title_name
                .replace("•", "-")
                .replace("|", "-")
                .replace("/", "-")
                .replace("\\", "-")
                .replace(":", "-")
            )

            default_name = (
                f"{safe_name.strip()}_Timetable.pdf"
            )

        else:

            title_name = self.get_faculty_title(
                self.current_id
            )

            safe_name = (
                title_name
                .replace("•", "-")
                .replace("|", "-")
                .replace("/", "-")
                .replace("\\", "-")
                .replace(":", "-")
            )

            default_name = (
                f"{safe_name.strip()}_Timetable.pdf"
            )

        # ----------------------------------------------------
        # Save dialog
        # ----------------------------------------------------

        file_path = filedialog.asksaveasfilename(
            parent=self.window,
            title="Save Timetable PDF",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            page_width, page_height = landscape(A4)

            document = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                rightMargin=12 * mm,
                leftMargin=12 * mm,
                topMargin=12 * mm,
                bottomMargin=12 * mm
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "TimetableTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=19,
                leading=22,
                alignment=TA_CENTER,
                spaceAfter=5
            )

            subtitle_style = ParagraphStyle(
                "TimetableSubtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=11,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#555555"),
                spaceAfter=12
            )

            header_style = ParagraphStyle(
                "Header",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=10,
                alignment=TA_CENTER
            )

            day_style = ParagraphStyle(
                "Day",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                alignment=TA_CENTER
            )

            cell_style = ParagraphStyle(
                "Cell",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7.2,
                leading=8.5,
                alignment=TA_CENTER
            )

            free_style = ParagraphStyle(
                "Free",
                parent=cell_style,
                fontName="Helvetica-Oblique",
                textColor=colors.HexColor("#777777")
            )

            story = []

            story.append(
                Paragraph(
                    "SMART ACADEMIC TIMETABLE MANAGEMENT SYSTEM",
                    title_style
                )
            )

            if self.current_mode == "class":

                view_label = "Class Timetable"

            else:

                view_label = "Faculty Timetable"

            story.append(
                Paragraph(
                    f"{view_label} &nbsp; | &nbsp; {title_name}",
                    subtitle_style
                )
            )

            # ------------------------------------------------
            # Create PDF table
            # ------------------------------------------------

            table_data = []

            header_row = [
                Paragraph("Day Order", header_style),
                Paragraph("Period 1", header_style),
                Paragraph("Period 2", header_style),
                Paragraph("Period 3", header_style),
                Paragraph("Period 4", header_style),
                Paragraph("Period 5", header_style),
            ]

            table_data.append(header_row)

            # Convert current rows to an easy lookup map.
            timetable_map = {}

            for row in self.current_timetable_data:

                day_order = row[0]
                period = row[1]

                if self.current_mode == "class":

                    timetable_map[
                        (day_order, period)
                    ] = {
                        "subject_code": row[3],
                        "subject_name": row[4],
                        "faculty_name": row[5]
                    }

                else:

                    timetable_map[
                        (day_order, period)
                    ] = {
                        "subject_code": row[4],
                        "subject_name": row[5],
                        "class_name": row[3]
                    }

            for day_order in range(1, 7):

                row_data = [
                    Paragraph(
                        f"Day Order {day_order}",
                        day_style
                    )
                ]

                for period in range(1, 6):

                    entry = timetable_map.get(
                        (day_order, period)
                    )

                    if not entry:

                        row_data.append(
                            Paragraph(
                                "FREE",
                                free_style
                            )
                        )

                        continue

                    subject_code = str(
                        entry.get(
                            "subject_code",
                            ""
                        )
                    )

                    subject_name = str(
                        entry.get(
                            "subject_name",
                            ""
                        )
                    )

                    if self.current_mode == "class":

                        third_line = str(
                            entry.get(
                                "faculty_name",
                                ""
                            )
                        )

                    else:

                        third_line = str(
                            entry.get(
                                "class_name",
                                ""
                            )
                        )

                    cell_html = (
                        f"<b>{subject_code}</b><br/>"
                        f"{subject_name}<br/>"
                        f"<font size='6.5'>{third_line}</font>"
                    )

                    row_data.append(
                        Paragraph(
                            cell_html,
                            cell_style
                        )
                    )

                table_data.append(row_data)

            usable_width = (
                page_width
                - document.leftMargin
                - document.rightMargin
            )

            day_column_width = 30 * mm

            period_width = (
                usable_width - day_column_width
            ) / 5

            timetable_table = Table(
                table_data,
                colWidths=[
                    day_column_width,
                    period_width,
                    period_width,
                    period_width,
                    period_width,
                    period_width
                ],
                repeatRows=1,
                hAlign="CENTER"
            )

            timetable_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DCE3EA")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#102A43")
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (0, -1),
                        colors.HexColor("#EEF2F6")
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor("#AAB4BE")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                ])
            )

            story.append(timetable_table)
            story.append(Spacer(1, 8))

            story.append(
                Paragraph(
                    (
                        f"Total scheduled periods: "
                        f"{len(self.current_timetable_data)}"
                        " &nbsp; | &nbsp; "
                        "Generated by Smart Academic Timetable Management System"
                    ),
                    ParagraphStyle(
                        "Footer",
                        parent=styles["Normal"],
                        fontName="Helvetica",
                        fontSize=7.5,
                        alignment=TA_LEFT,
                        textColor=colors.HexColor("#666666")
                    )
                )
            )

            document.build(story)

            messagebox.showinfo(
                "PDF Downloaded",
                (
                    "Timetable PDF created successfully!\n\n"
                    f"Saved to:\n{file_path}"
                ),
                parent=self.window
            )

        except Exception as error:

            messagebox.showerror(
                "PDF Export Error",
                (
                    "Unable to create the timetable PDF.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_timetable(self):

        try:

            create_timetable_table()

            timetable = get_all_timetable()

            if not timetable:

                self.current_timetable_data = []
                self.current_id = None

                self.download_button.configure(
                    state="disabled"
                )

                self.show_empty_message(
                    "No timetable has been generated yet."
                )

                return

            self.load_dropdowns()

            if self.current_mode == "class":

                self.load_class_dropdown()

            else:

                self.load_faculty_dropdown()

            self.selection_changed(
                self.selection_menu.get()
            )

        except Exception as error:

            messagebox.showerror(
                "Refresh Error",
                f"Unable to refresh timetable.\n\n{error}",
                parent=self.window
            )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_window(self):

        try:
            self.window.grab_release()
        except Exception:
            pass

        self.window.destroy()


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()

    ViewTimetableWindow(root)

    root.mainloop()
