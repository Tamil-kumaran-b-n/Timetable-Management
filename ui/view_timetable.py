import re
from datetime import datetime
from pathlib import Path

from tkinter import messagebox

import customtkinter as ctk

from database.database import (
    get_all_faculty,
    get_all_classes
)

from database.generator import (
    create_timetable_table,
    get_timetable_by_class,
    get_timetable_by_faculty,
    get_all_timetable
)


class ViewTimetableWindow:

    def __init__(self, parent, container=None, faculty_user=None):

        self.parent = parent
        self.embedded = container is not None
        self.faculty_user = faculty_user

        self.window = container if self.embedded else ctk.CTkToplevel(parent)

        if not self.embedded:
            self.window.title("View Timetable")
            self.window.geometry("1280x800")
            self.window.minsize(1100, 700)
            self.window.transient(parent)

        # ==================================================
        # DATA
        # ==================================================

        self.faculty_records = []
        self.class_records = []

        # Only classes/faculty that actually have
        # generated timetable entries
        self.generated_class_records = []
        self.generated_faculty_records = []

        self.current_mode = "class"

        self.current_id = None

        self.current_timetable_data = []

        # ==================================================
        # BUILD
        # ==================================================

        self.build_ui()

        self.load_dropdowns()

        self.check_timetable()

        if not self.embedded:
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    # ======================================================
    # MAIN UI
    # ======================================================

    def build_ui(self):

        self.main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=18
        )

        # ==================================================
        # HEADER
        # ==================================================

        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header_frame.pack(
            fill="x",
            pady=(0, 14)
        )

        ctk.CTkLabel(
            header_frame,
            text="View Timetable",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            header_frame,
            text=(
                "View the generated timetable by class "
                "or faculty and download it as a structured PDF."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="gray"
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        # ==================================================
        # VIEW MODE
        # ==================================================

        mode_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )

        if not getattr(self, "faculty_user", None):
            mode_frame.pack(
                fill="x",
                pady=(0, 12)
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
            padx=(18, 10),
            pady=14
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
            pady=10
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
            pady=10
        )

        # ==================================================
        # SELECTION AREA
        # ==================================================

        self.selection_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )

        self.selection_frame.pack(
            fill="x",
            pady=(0, 12)
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
            padx=(18, 10),
            pady=14
        )

        self.selection_menu = ctk.CTkOptionMenu(
            self.selection_frame,
            width=380,
            height=40,
            command=self.selection_changed
        )

        self.selection_menu.pack(
            side="left",
            padx=5,
            pady=10
        )

        # ==================================================
        # DOWNLOAD PDF
        # ==================================================

        self.download_button = ctk.CTkButton(
            self.selection_frame,
            text="Download PDF",
            width=130,
            height=40,
            command=self.download_pdf,
            state="disabled"
        )

        self.download_button.pack(
            side="right",
            padx=(8, 18),
            pady=10
        )

        # ==================================================
        # REFRESH
        # ==================================================

        self.refresh_button = ctk.CTkButton(
            self.selection_frame,
            text="Refresh",
            width=100,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self.refresh_timetable
        )

        self.refresh_button.pack(
            side="right",
            padx=8,
            pady=10
        )

        # ==================================================
        # CURRENT TITLE
        # ==================================================

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
            pady=(0, 8)
        )

        # ==================================================
        # TIMETABLE GRID
        # ==================================================

        self.grid_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )

        self.grid_container.pack(
            fill="both",
            expand=True
        )

    # ======================================================
    # LOAD DATABASE DATA
    # ======================================================

    def load_dropdowns(self):

        try:

            self.faculty_records = (
                get_all_faculty()
                or []
            )

            self.class_records = (
                get_all_classes()
                or []
            )

        except Exception as error:

            self.faculty_records = []
            self.class_records = []

            messagebox.showerror(
                "Database Error",
                (
                    "Unable to load classes/faculty.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

        # Build ONLY generated lists
        self.build_generated_class_list()
        self.build_generated_faculty_list()

    # ======================================================
    # FIND GENERATED CLASSES
    # ======================================================

    def build_generated_class_list(self):

        self.generated_class_records = []

        for record in self.class_records:

            if not record:
                continue

            class_id = record[0]

            try:

                timetable_data = (
                    get_timetable_by_class(
                        class_id
                    )
                    or []
                )

            except Exception:

                timetable_data = []

            # ----------------------------------------------
            # IMPORTANT
            #
            # Only classes that actually have timetable
            # entries are added.
            # ----------------------------------------------

            if timetable_data:

                self.generated_class_records.append(
                    record
                )

    # ======================================================
    # FIND GENERATED FACULTY
    # ======================================================

    def build_generated_faculty_list(self):

        self.generated_faculty_records = []

        for record in self.faculty_records:

            if not record:
                continue

            faculty_id = record[0]

            try:

                timetable_data = (
                    get_timetable_by_faculty(
                        faculty_id
                    )
                    or []
                )

            except Exception:

                timetable_data = []

            if timetable_data:

                self.generated_faculty_records.append(
                    record
                )

    # ======================================================
    # CHECK GENERATED TIMETABLE
    # ======================================================

    def check_timetable(self):

        try:

            timetable = (
                get_all_timetable()
                or []
            )

            if not timetable:

                self.current_id = None

                self.current_timetable_data = []

                self.download_button.configure(
                    state="disabled"
                )

                self.selection_menu.configure(
                    state="disabled"
                )

                self.show_empty_message(
                    "No timetable has been generated yet."
                )

                return

            # ------------------------------------------
            # Rebuild generated-only lists
            # ------------------------------------------

            self.build_generated_class_list()

            self.build_generated_faculty_list()

            self.selection_menu.configure(
                state="normal"
            )

            if getattr(self, "faculty_user", None):
                self.show_faculty_view()
            else:
                self.show_class_view()

        except Exception as error:

            self.current_id = None

            self.current_timetable_data = []

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "Unable to load timetable."
            )

            messagebox.showerror(
                "Timetable Error",
                (
                    "Unable to load timetable.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

    # ======================================================
    # CLASS VIEW
    # ======================================================

    def show_class_view(self):

        self.current_mode = "class"

        self.class_mode_button.configure(
            fg_color=ctk.ThemeManager.theme[
                "CTkButton"
            ][
                "fg_color"
            ]
        )

        self.faculty_mode_button.configure(
            fg_color="gray",
            hover_color="#555555"
        )

        self.selection_label.configure(
            text="Select Class"
        )

        self.load_class_dropdown()

        selected = self.selection_menu.get()

        if selected.startswith("No "):

            self.current_id = None

            self.current_timetable_data = []

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "No generated classes available."
            )

            return

        self.selection_changed(
            selected
        )

    # ======================================================
    # FACULTY VIEW
    # ======================================================

    def show_faculty_view(self):

        self.current_mode = "faculty"

        self.faculty_mode_button.configure(
            fg_color=ctk.ThemeManager.theme[
                "CTkButton"
            ][
                "fg_color"
            ]
        )

        self.class_mode_button.configure(
            fg_color="gray",
            hover_color="#555555"
        )

        self.selection_label.configure(
            text="Select Faculty"
        )

        self.load_faculty_dropdown()

        selected = self.selection_menu.get()

        if selected.startswith("No "):

            self.current_id = None

            self.current_timetable_data = []

            self.download_button.configure(
                state="disabled"
            )

            self.show_empty_message(
                "No generated faculty available."
            )

            return

        self.selection_changed(
            selected
        )

    # ======================================================
    # LOAD ONLY GENERATED CLASSES
    # ======================================================

    def load_class_dropdown(self):

        # --------------------------------------------------
        # IMPORTANT:
        # Use generated_class_records instead of
        # class_records.
        # --------------------------------------------------

        records = (
            self.generated_class_records
        )

        if not records:

            self.selection_menu.configure(
                values=[
                    "No Generated Classes"
                ]
            )

            self.selection_menu.set(
                "No Generated Classes"
            )

            return

        values = []

        for record in records:

            class_name = (
                record[1]
                if len(record) > 1
                else ""
            )

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

            values.append(
                f"{class_name} | "
                f"{department} | "
                f"Sem {semester}"
            )

        self.selection_menu.configure(
            values=values
        )

        if (
            self.selection_menu.get()
            not in values
        ):

            self.selection_menu.set(
                values[0]
            )

    # ======================================================
    # LOAD ONLY GENERATED FACULTY
    # ======================================================

    def load_faculty_dropdown(self):

        records = (
            self.generated_faculty_records
        )

        if not records:

            self.selection_menu.configure(
                values=[
                    "No Generated Faculty"
                ]
            )

            self.selection_menu.set(
                "No Generated Faculty"
            )

            return

        values = []

        for record in records:

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
                values.append(f"{faculty_name} ({faculty_code})")
            else:
                values.append(faculty_name)

        if getattr(self, "faculty_user", None):
            uname = self.faculty_user.get("username", "").strip().lower()
            matched_val = None
            for idx, record in enumerate(records):
                f_code = record[1].lower() if len(record) > 1 and record[1] else ""
                f_name = record[2].lower() if len(record) > 2 and record[2] else ""
                if uname in [f_name, f_code, f_code.replace("fac-", "")]:
                    matched_val = values[idx]
                    break

            if matched_val:
                self.selection_menu.configure(values=[matched_val], state="disabled")
                self.selection_menu.set(matched_val)
                self.selection_label.configure(text="Faculty Member:")
            else:
                self.selection_menu.configure(values=["No Schedule Generated"], state="disabled")
                self.selection_menu.set("No Schedule Generated")
                self.selection_label.configure(text="Faculty Member:")
        else:
            self.selection_menu.configure(values=values, state="normal")
            if self.selection_menu.get() not in values:
                self.selection_menu.set(values[0])

    # ======================================================
    # SELECTION CHANGED
    # ======================================================

    def selection_changed(
        self,
        selected_value
    ):

        if (
            not selected_value
            or selected_value.startswith("No ")
        ):

            return

        try:

            if self.current_mode == "class":

                index = (
                    self.find_class_index(
                        selected_value
                    )
                )

                if index is None:
                    return

                generated_records = (
                    self.generated_class_records
                )

                class_id = (
                    generated_records[index][0]
                )

                self.current_id = class_id

                self.display_class_timetable(
                    class_id
                )

            else:

                index = (
                    self.find_faculty_index(
                        selected_value
                    )
                )

                if index is None:
                    return

                generated_records = (
                    self.generated_faculty_records
                )

                faculty_id = (
                    generated_records[index][0]
                )

                self.current_id = faculty_id

                self.display_faculty_timetable(
                    faculty_id
                )

        except Exception as error:

            self.current_id = None

            self.current_timetable_data = []

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

    # ======================================================
    # FIND CLASS INDEX
    # ======================================================

    def find_class_index(
        self,
        selected_value
    ):

        records = (
            self.generated_class_records
        )

        for index, record in enumerate(
            records
        ):

            class_name = (
                record[1]
                if len(record) > 1
                else ""
            )

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

            if (
                display_name
                == selected_value
            ):

                return index

        return None

    # ======================================================
    # FIND FACULTY INDEX
    # ======================================================

    def find_faculty_index(
        self,
        selected_value
    ):

        records = (
            self.generated_faculty_records
        )

        for index, record in enumerate(
            records
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
                    f"{faculty_name} "
                    f"({faculty_code})"
                )

            else:

                display_name = (
                    faculty_name
                )

            if (
                display_name
                == selected_value
            ):

                return index

        return None

    # ======================================================
    # DISPLAY CLASS TIMETABLE
    # ======================================================

    def display_class_timetable(
        self,
        class_id
    ):

        data = (
            get_timetable_by_class(
                class_id
            )
            or []
        )

        self.current_id = class_id

        self.current_timetable_data = data

        self.current_title.configure(
            text=self.get_class_title(
                class_id
            )
        )

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

        self.draw_grid()

        timetable_map = {}

        for row in data:

            timetable_map[
                (
                    row[0],
                    row[1]
                )
            ] = {
                "subject_code": row[3],
                "subject_name": row[4],
                "faculty_name": row[5]
            }

        self.fill_grid(
            timetable_map,
            mode="class"
        )

    # ======================================================
    # DISPLAY FACULTY TIMETABLE
    # ======================================================

    def display_faculty_timetable(
        self,
        faculty_id
    ):

        data = (
            get_timetable_by_faculty(
                faculty_id
            )
            or []
        )

        self.current_id = faculty_id

        self.current_timetable_data = data

        self.current_title.configure(
            text=self.get_faculty_title(
                faculty_id
            )
        )

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

        self.draw_grid()

        timetable_map = {}

        for row in data:

            timetable_map[
                (
                    row[0],
                    row[1]
                )
            ] = {
                "faculty_name": row[2],
                "class_name": row[3],
                "subject_code": row[4],
                "subject_name": row[5]
            }

        self.fill_grid(
            timetable_map,
            mode="faculty"
        )

    # ======================================================
    # DRAW GRID
    # ======================================================

    def draw_grid(self):

        for widget in (
            self.grid_container.winfo_children()
        ):

            widget.destroy()

        self.grid_container.grid_columnconfigure(
            0,
            weight=0
        )

        for column in range(1, 6):

            self.grid_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="timetable_column"
            )

        for row in range(0, 7):

            self.grid_container.grid_rowconfigure(
                row,
                weight=0,
                minsize=58 if row == 0 else 82
            )

        self._make_header_cell(
            "Day Order",
            0,
            0,
            width=110
        )

        for period in range(1, 6):

            self._make_header_cell(
                f"Period {period}",
                0,
                period
            )

        for day_order in range(1, 7):

            self._make_header_cell(
                f"Day Order {day_order}",
                day_order,
                0,
                width=110
            )

    # ======================================================
    # HEADER CELL
    # ======================================================

    def _make_header_cell(
        self,
        text,
        row,
        column,
        width=None
    ):

        label = ctk.CTkLabel(
            self.grid_container,
            text=text,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            corner_radius=8,
            height=46
        )

        if width:

            label.configure(
                width=width
            )

        label.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=4,
            pady=4
        )

    # ======================================================
    # FILL GRID
    # ======================================================

    def fill_grid(
        self,
        timetable_map,
        mode
    ):

        for day_order in range(1, 7):

            for period in range(1, 6):

                entry = timetable_map.get(
                    (
                        day_order,
                        period
                    )
                )

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

                # ------------------------------------------
                # FREE SLOT
                # ------------------------------------------

                if not entry:

                    ctk.CTkLabel(
                        cell,
                        text="FREE",
                        font=ctk.CTkFont(
                            size=11
                        ),
                        text_color="gray"
                    ).pack(
                        fill="both",
                        expand=True,
                        padx=4,
                        pady=4
                    )

                    continue

                # ------------------------------------------
                # SUBJECT
                # ------------------------------------------

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

                # ------------------------------------------
                # THIRD LINE
                # ------------------------------------------

                if mode == "class":

                    third_line = str(
                        entry.get(
                            "faculty_name",
                            ""
                        )
                    )

                    third_prefix = "Faculty"

                else:

                    third_line = str(
                        entry.get(
                            "class_name",
                            ""
                        )
                    )

                    third_prefix = "Class"

                # ------------------------------------------
                # SUBJECT CODE
                # ------------------------------------------

                ctk.CTkLabel(
                    cell,
                    text=subject_code,
                    font=ctk.CTkFont(
                        size=12,
                        weight="bold"
                    ),
                    anchor="center"
                ).pack(
                    fill="x",
                    padx=6,
                    pady=(7, 1)
                )

                # ------------------------------------------
                # SUBJECT NAME
                # ------------------------------------------

                ctk.CTkLabel(
                    cell,
                    text=subject_name,
                    font=ctk.CTkFont(
                        size=10,
                        weight="bold"
                    ),
                    wraplength=150,
                    justify="center",
                    anchor="center"
                ).pack(
                    fill="both",
                    expand=True,
                    padx=6,
                    pady=1
                )

                # ------------------------------------------
                # FACULTY / CLASS
                # ------------------------------------------

                ctk.CTkLabel(
                    cell,
                    text=(
                        f"{third_prefix}: "
                        f"{third_line}"
                    ),
                    font=ctk.CTkFont(
                        size=9
                    ),
                    wraplength=150,
                    justify="center",
                    anchor="center",
                    text_color="gray"
                ).pack(
                    fill="x",
                    padx=5,
                    pady=(1, 7)
                )

    # ======================================================
    # EMPTY MESSAGE
    # ======================================================

    def show_empty_message(
        self,
        message
    ):

        for widget in (
            self.grid_container.winfo_children()
        ):

            widget.destroy()

        ctk.CTkLabel(
            self.grid_container,
            text=message,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color="gray"
        ).pack(
            expand=True,
            pady=80
        )

    # ======================================================
    # CLASS TITLE
    # ======================================================

    def get_class_title(
        self,
        class_id
    ):

        for record in self.class_records:

            if record[0] == class_id:

                class_name = (
                    record[1]
                    if len(record) > 1
                    else ""
                )

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

    # ======================================================
    # FACULTY TITLE
    # ======================================================

    def get_faculty_title(
        self,
        faculty_id
    ):

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

    # ======================================================
    # SAFE FILE NAME
    # ======================================================

    @staticmethod
    def _safe_filename(value):

        value = re.sub(
            r'[<>:"/\\|?*]',
            "-",
            str(value)
        )

        value = value.replace(
            "•",
            "-"
        )

        value = re.sub(
            r"\s+",
            " ",
            value
        ).strip(
            " ."
        )

        return (
            value
            or "Timetable"
        )

    # ======================================================
    # DOWNLOADS FOLDER
    # ======================================================

    @staticmethod
    def _downloads_folder():

        downloads = (
            Path.home()
            / "Downloads"
        )

        downloads.mkdir(
            parents=True,
            exist_ok=True
        )

        return downloads

    # ======================================================
    # UNIQUE PDF PATH
    # ======================================================

    def _unique_pdf_path(
        self,
        title_name
    ):

        folder = (
            self._downloads_folder()
        )

        base_name = (
            self._safe_filename(
                title_name
            )
        )

        path = (
            folder
            / f"{base_name}_Timetable.pdf"
        )

        if not path.exists():

            return path

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        return (
            folder
            / (
                f"{base_name}_Timetable_"
                f"{timestamp}.pdf"
            )
        )

    # ======================================================
    # PDF EXPORT
    # ======================================================

    def download_pdf(self):

        if not self.current_timetable_data:

            messagebox.showwarning(
                "No Timetable",
                (
                    "There is no timetable "
                    "available to download."
                ),
                parent=self.window
            )

            return

        try:

            from reportlab.lib import colors

            from reportlab.lib.enums import (
                TA_CENTER
            )

            from reportlab.lib.pagesizes import (
                A4,
                landscape
            )

            from reportlab.lib.styles import (
                ParagraphStyle,
                getSampleStyleSheet
            )

            from reportlab.lib.units import mm

            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle
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

        # ==================================================
        # TITLE
        # ==================================================

        if self.current_mode == "class":

            title_name = (
                self.get_class_title(
                    self.current_id
                )
            )

            view_label = (
                "Class Timetable"
            )

        else:

            title_name = (
                self.get_faculty_title(
                    self.current_id
                )
            )

            view_label = (
                "Faculty Timetable"
            )

        file_path = (
            self._unique_pdf_path(
                title_name
            )
        )

        try:

            page_width, page_height = (
                landscape(A4)
            )

            document = SimpleDocTemplate(
                str(file_path),
                pagesize=landscape(A4),
                rightMargin=10 * mm,
                leftMargin=10 * mm,
                topMargin=10 * mm,
                bottomMargin=10 * mm,
                title=(
                    f"{view_label} - "
                    f"{title_name}"
                ),
                author=(
                    "Smart Academic "
                    "Timetable Management System"
                )
            )

            styles = (
                getSampleStyleSheet()
            )

            title_style = ParagraphStyle(
                "TimetableTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#102A43"
                ),
                spaceAfter=4
            )

            subtitle_style = ParagraphStyle(
                "TimetableSubtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=11,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#52606D"
                ),
                spaceAfter=3
            )

            info_style = ParagraphStyle(
                "Info",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#52606D"
                ),
                spaceAfter=8
            )

            header_style = ParagraphStyle(
                "Header",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#102A43"
                )
            )

            day_style = ParagraphStyle(
                "Day",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=7.5,
                leading=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#102A43"
                )
            )

            cell_style = ParagraphStyle(
                "Cell",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=6.8,
                leading=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#243B53"
                )
            )

            free_style = ParagraphStyle(
                "Free",
                parent=cell_style,
                fontName="Helvetica-Oblique",
                fontSize=7,
                textColor=colors.HexColor(
                    "#829AB1"
                )
            )

            story = []

            story.append(
                Paragraph(
                    (
                        "SMART ACADEMIC "
                        "TIMETABLE MANAGEMENT SYSTEM"
                    ),
                    title_style
                )
            )

            story.append(
                Paragraph(
                    (
                        f"{view_label} "
                        f"&nbsp; | &nbsp; "
                        f"{title_name}"
                    ),
                    subtitle_style
                )
            )

            story.append(
                Paragraph(
                    (
                        f"Generated on "
                        f"{datetime.now().strftime('%d-%m-%Y %I:%M %p')} "
                        f"&nbsp; | &nbsp; "
                        f"Total scheduled periods: "
                        f"{len(self.current_timetable_data)}"
                    ),
                    info_style
                )
            )

            # ==================================================
            # BUILD TIMETABLE MAP
            # ==================================================

            timetable_map = {}

            for row in (
                self.current_timetable_data
            ):

                day_order = row[0]
                period = row[1]

                if self.current_mode == "class":

                    timetable_map[
                        (
                            day_order,
                            period
                        )
                    ] = {
                        "subject_code": row[3],
                        "subject_name": row[4],
                        "third": row[5],
                        "third_label": "Faculty"
                    }

                else:

                    timetable_map[
                        (
                            day_order,
                            period
                        )
                    ] = {
                        "subject_code": row[4],
                        "subject_name": row[5],
                        "third": row[3],
                        "third_label": "Class"
                    }

            # ==================================================
            # TABLE HEADER
            # ==================================================

            table_data = [

                [
                    Paragraph(
                        "Day Order",
                        header_style
                    ),

                    Paragraph(
                        "Period 1",
                        header_style
                    ),

                    Paragraph(
                        "Period 2",
                        header_style
                    ),

                    Paragraph(
                        "Period 3",
                        header_style
                    ),

                    Paragraph(
                        "Period 4",
                        header_style
                    ),

                    Paragraph(
                        "Period 5",
                        header_style
                    )
                ]
            ]

            # ==================================================
            # TABLE ROWS
            # ==================================================

            for day_order in range(
                1,
                7
            ):

                row_data = [

                    Paragraph(
                        f"Day Order {day_order}",
                        day_style
                    )
                ]

                for period in range(
                    1,
                    6
                ):

                    entry = (
                        timetable_map.get(
                            (
                                day_order,
                                period
                            )
                        )
                    )

                    if not entry:

                        row_data.append(
                            Paragraph(
                                "FREE",
                                free_style
                            )
                        )

                        continue

                    code = (
                        self._escape_pdf_text(
                            entry[
                                "subject_code"
                            ]
                        )
                    )

                    name = (
                        self._escape_pdf_text(
                            entry[
                                "subject_name"
                            ]
                        )
                    )

                    third = (
                        self._escape_pdf_text(
                            entry[
                                "third"
                            ]
                        )
                    )

                    label = (
                        self._escape_pdf_text(
                            entry[
                                "third_label"
                            ]
                        )
                    )

                    content = (
                        f"<b>{code}</b><br/>"
                        f"{name}<br/><br/>"
                        f"<font size='6'>"
                        f"{label}: {third}"
                        f"</font>"
                    )

                    row_data.append(
                        Paragraph(
                            content,
                            cell_style
                        )
                    )

                table_data.append(
                    row_data
                )

            # ==================================================
            # TABLE WIDTH
            # ==================================================

            usable_width = (
                page_width
                - document.leftMargin
                - document.rightMargin
            )

            day_column_width = (
                28 * mm
            )

            period_width = (
                usable_width
                - day_column_width
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

            # ==================================================
            # TABLE STYLE
            # ==================================================

            timetable_table.setStyle(
                TableStyle(
                    [

                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#DCE3EA"
                            )
                        ),

                        (
                            "BACKGROUND",
                            (0, 1),
                            (0, -1),
                            colors.HexColor(
                                "#EEF2F6"
                            )
                        ),

                        (
                            "BACKGROUND",
                            (1, 1),
                            (-1, -1),
                            colors.white
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.55,
                            colors.HexColor(
                                "#AAB4BE"
                            )
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
                            4
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            4
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6
                        )
                    ]
                )
            )

            story.append(
                timetable_table
            )

            story.append(
                Spacer(
                    1,
                    7
                )
            )

            footer_style = ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7,
                leading=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor(
                    "#7B8794"
                )
            )

            story.append(
                Paragraph(
                    (
                        "Generated by Smart Academic "
                        "Timetable Management System"
                    ),
                    footer_style
                )
            )

            # ==================================================
            # BUILD PDF
            # ==================================================

            document.build(
                story
            )

            messagebox.showinfo(
                "PDF Downloaded",
                (
                    "Timetable PDF created successfully!\n\n"
                    "Saved in Downloads:\n"
                    f"{file_path}"
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

    # ======================================================
    # ESCAPE PDF TEXT
    # ======================================================

    @staticmethod
    def _escape_pdf_text(
        value
    ):

        value = str(
            value
            if value is not None
            else ""
        )

        return (
            value
            .replace(
                "&",
                "&amp;"
            )
            .replace(
                "<",
                "&lt;"
            )
            .replace(
                ">",
                "&gt;"
            )
        )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh_timetable(self):

        try:

            create_timetable_table()

            timetable = (
                get_all_timetable()
                or []
            )

            # ----------------------------------------------
            # No generated timetable
            # ----------------------------------------------

            if not timetable:

                self.current_id = None

                self.current_timetable_data = []

                self.download_button.configure(
                    state="disabled"
                )

                self.build_generated_class_list()

                self.build_generated_faculty_list()

                self.show_empty_message(
                    "No timetable has been generated yet."
                )

                return

            # ----------------------------------------------
            # Reload database data
            # ----------------------------------------------

            self.load_dropdowns()

            # ----------------------------------------------
            # Reload correct mode
            # ----------------------------------------------

            if self.current_mode == "class":

                self.load_class_dropdown()

            else:

                self.load_faculty_dropdown()

            # ----------------------------------------------
            # Display selected timetable
            # ----------------------------------------------

            selected = (
                self.selection_menu.get()
            )

            if selected.startswith("No "):

                self.current_id = None

                self.current_timetable_data = []

                self.download_button.configure(
                    state="disabled"
                )

                self.show_empty_message(
                    (
                        "No generated timetable "
                        "entries available."
                    )
                )

                return

            self.selection_changed(
                selected
            )

        except Exception as error:

            messagebox.showerror(
                "Refresh Error",
                (
                    "Unable to refresh timetable.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

    # ======================================================
    # CLOSE
    # ======================================================

    def close_window(self):

        if self.embedded:
            return

        try:

            self.window.grab_release()

        except Exception:

            pass

        self.window.destroy()


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    ctk.set_appearance_mode(
        "System"
    )

    ctk.set_default_color_theme(
        "blue"
    )

    root = ctk.CTk()

    root.withdraw()

    ViewTimetableWindow(
        root
    )

    root.mainloop()
