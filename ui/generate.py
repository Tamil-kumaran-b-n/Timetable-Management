import customtkinter as ctk
from tkinter import messagebox

from database.database import get_all_classes
from database.workload import get_all_workloads
from database.generator import (
    generate_timetable,
    get_all_timetable,
)


class GenerateTimetableWindow:
    def __init__(self, parent, container=None, navigate=None):
        self.parent = parent
        self.embedded = container is not None
        self.navigate = navigate
        self.classes_data = []
        self.selected_class_id = None

        self.window = container if self.embedded else ctk.CTkToplevel(parent)
        if not self.embedded:
            self.window.title("Generate Timetable")
            self.window.geometry("1050x700")
            self.window.minsize(900, 600)
            self.window.transient(parent)
            self.window.grab_set()

        self.build_ui()
        self.load_classes_dropdown()
        self.load_workload_summary()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # Main container
        self.main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent"
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        ctk.CTkLabel(
            self.main_frame,
            text="Generate Timetable",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color=("#18181B", "#F4F4F5")
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            self.main_frame,
            text=(
                "Generate a balanced, conflict-free timetable across all classes "
                "or generate for an individual class separately."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color=("#71717A", "#A1A1AA")
        ).pack(
            anchor="w",
            pady=(5, 20)
        )

        # ----------------------------------------------------
        # Scope Selection Card (All Classes vs Single Class)
        # ----------------------------------------------------

        scope_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
        )
        scope_card.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            scope_card,
            text="Generation Scope",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=("#18181B", "#F4F4F5")
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 4)
        )

        scope_sublabel = ctk.CTkLabel(
            scope_card,
            text="Select whether to generate schedules for the entire college or regenerate a single class independently:",
            font=ctk.CTkFont(size=12),
            text_color=("#71717A", "#A1A1AA")
        )
        scope_sublabel.pack(anchor="w", padx=20, pady=(0, 10))

        scope_row = ctk.CTkFrame(scope_card, fg_color="transparent")
        scope_row.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(
            scope_row,
            text="Target Scope:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#18181B", "#F4F4F5")
        ).pack(side="left", padx=(0, 12))

        self.scope_combo = ctk.CTkComboBox(
            scope_row,
            values=["All Classes (Full Generation)"],
            width=380,
            height=38,
            font=("Arial", 12),
            command=self.on_scope_changed
        )
        self.scope_combo.set("All Classes (Full Generation)")
        self.scope_combo.pack(side="left", padx=(0, 12))

        # ----------------------------------------------------
        # Rules Card
        # ----------------------------------------------------

        rules_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
        )
        rules_card.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            rules_card,
            text="Timetable Structure & Constraint Rules",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=("#18181B", "#F4F4F5")
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 8)
        )

        rules_text = (
            "• 6 Day Orders (Day 1 through Day 6)\n"
            "• 5 Periods per Day (30 Total Slots per Class)\n"
            "• 29 Teaching Periods + 1 Mandatory FREE Period (Period 5)\n"
            "• Workloads distributed evenly across Day Orders to avoid subject clustering\n"
            "• Consecutive periods for the same subject avoided where possible\n"
            "• High-priority workloads scheduled with morning/core period priority\n"
            "• Zero faculty double-booking clashes across all simultaneous classes"
        )

        ctk.CTkLabel(
            rules_card,
            text=rules_text,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=("#374151", "#D1D5DB")
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 16)
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        stats_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        self.workload_value = self.create_stat_card(
            stats_frame,
            "Total Workloads"
        )

        self.important_value = self.create_stat_card(
            stats_frame,
            "Important"
        )

        self.normal_value = self.create_stat_card(
            stats_frame,
            "Normal"
        )

        self.period_value = self.create_stat_card(
            stats_frame,
            "Required Periods"
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
        )
        self.status_card.pack(
            fill="x",
            pady=(0, 25)
        )

        self.status_label = ctk.CTkLabel(
            self.status_card,
            text="Ready to generate timetable.",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=("#18181B", "#F4F4F5")
        )
        self.status_label.pack(
            anchor="w",
            padx=20,
            pady=16
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        button_frame.pack(
            fill="x"
        )

        self.generate_button = ctk.CTkButton(
            button_frame,
            text="Generate Timetable",
            height=44,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.generate
        )
        self.generate_button.pack(
            side="left",
            padx=(0, 12)
        )

        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh Workload",
            height=44,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_workload_summary
        )
        self.refresh_button.pack(
            side="left",
            padx=(0, 12)
        )

        self.view_button = ctk.CTkButton(
            button_frame,
            text="View Timetable",
            height=44,
            command=self.open_timetable
        )
        self.view_button.pack(
            side="left"
        )

    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(self, parent, title):

        card = ctk.CTkFrame(
            parent,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E4E4E7", "#383838")
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=12
            ),
            text_color=("#71717A", "#A1A1AA")
        ).pack(
            pady=(12, 2)
        )

        value = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            ),
            text_color=("#18181B", "#F4F4F5")
        )

        value.pack(
            pady=(0, 12)
        )

        return value

    # ========================================================
    # LOAD CLASSES DROPDOWN
    # ========================================================

    def load_classes_dropdown(self):
        try:
            self.classes_data = get_all_classes() or []
        except Exception:
            self.classes_data = []

        options = ["All Classes (Full Generation)"]
        for c in self.classes_data:
            cid = c[0]
            cname = c[1] if len(c) > 1 else ""
            dept = c[2] if len(c) > 2 else ""
            sem = c[3] if len(c) > 3 else ""
            options.append(f"{cname} | {dept} | Sem {sem} (ID: {cid})")

        self.scope_combo.configure(values=options)

    def on_scope_changed(self, choice):
        if choice.startswith("All Classes"):
            self.selected_class_id = None
            self.generate_button.configure(text="Generate All Timetables")
        else:
            # Parse class ID from choice string (ID: <num>)
            try:
                cid_str = choice.split("(ID:")[-1].replace(")", "").strip()
                self.selected_class_id = int(cid_str)
                self.generate_button.configure(text="Generate for Selected Class")
            except Exception:
                self.selected_class_id = None
                self.generate_button.configure(text="Generate Timetable")

        self.load_workload_summary()

    # ========================================================
    # LOAD WORKLOAD SUMMARY
    # ========================================================

    def load_workload_summary(self):

        try:
            workloads = get_all_workloads()

            if self.selected_class_id is not None:
                workloads = [w for w in workloads if w[2] == self.selected_class_id]

            total = len(workloads)

            important = sum(
                1
                for row in workloads
                if len(row) > 12 and str(row[12]).strip().lower() == "important"
            )

            normal = total - important

            total_periods = sum(
                int(row[13])
                for row in workloads
                if len(row) > 13 and str(row[13]).isdigit()
            )

            self.workload_value.configure(
                text=str(total)
            )

            self.important_value.configure(
                text=str(important)
            )

            self.normal_value.configure(
                text=str(normal)
            )

            self.period_value.configure(
                text=str(total_periods)
            )

            scope_desc = "for selected class" if self.selected_class_id else "across all classes"

            if total == 0:
                self.status_label.configure(
                    text=(
                        f"No workload found {scope_desc}. "
                        "Please assign faculty workload before generating."
                    )
                )
                self.generate_button.configure(
                    state="disabled"
                )
            else:
                self.status_label.configure(
                    text=(
                        f"{total} workload assignment(s) ready {scope_desc} ({total_periods} periods to schedule)."
                    )
                )
                self.generate_button.configure(
                    state="normal"
                )

        except Exception as error:
            self.status_label.configure(
                text=f"Unable to load workload information: {error}"
            )
            self.generate_button.configure(
                state="disabled"
            )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(self):

        workloads = get_all_workloads()

        if self.selected_class_id is not None:
            workloads = [w for w in workloads if w[2] == self.selected_class_id]

        if not workloads:
            messagebox.showwarning(
                "No Workload",
                "No faculty workload is available for the selected scope.\n\nPlease assign workload first.",
                parent=self.window
            )
            return

        scope_msg = (
            "Regenerate timetable for only the selected class?\n\nExisting schedules of all other classes will remain preserved."
            if self.selected_class_id is not None
            else "Generate a new timetable for ALL classes?\n\nAll existing timetable entries will be replaced."
        )

        confirm = messagebox.askyesno(
            "Confirm Generation",
            scope_msg,
            parent=self.window
        )

        if not confirm:
            return

        orig_text = self.generate_button.cget("text")
        self.generate_button.configure(
            state="disabled",
            text="Generating..."
        )

        self.refresh_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Generating timetable schedule. Please wait..."
        )

        self.window.update_idletasks()

        try:
            result = generate_timetable(target_class_id=self.selected_class_id)

            if result:
                timetable = get_all_timetable()

                self.status_label.configure(
                    text=(
                        "Timetable generated successfully! "
                        f"{len(timetable)} total slot(s) currently active."
                    )
                )

                self.view_button.configure(
                    state="normal"
                )

                succ_msg = (
                    "Timetable generated successfully for selected class!\n\nNo clashes with existing classes."
                    if self.selected_class_id is not None
                    else f"Complete system timetable generated successfully!\n\nTotal slots created: {len(timetable)}"
                )

                messagebox.showinfo(
                    "Generation Complete",
                    succ_msg,
                    parent=self.window
                )

        except ValueError as error:
            self.status_label.configure(
                text="Timetable generation could not be completed."
            )
            messagebox.showerror(
                "Generation Failed",
                str(error),
                parent=self.window
            )

        except Exception as error:
            self.status_label.configure(
                text="Unexpected error during generation."
            )
            messagebox.showerror(
                "Error",
                f"An unexpected error occurred while generating:\n\n{error}",
                parent=self.window
            )

        finally:
            self.generate_button.configure(
                state="normal",
                text=orig_text
            )
            self.refresh_button.configure(
                state="normal"
            )

    # ========================================================
    # OPEN TIMETABLE
    # ========================================================

    def open_timetable(self):
        try:
            from ui.view_timetable import ViewTimetableWindow

            if not self.embedded:
                self.window.grab_release()

            if self.navigate:
                self.navigate("view_timetable")
            else:
                ViewTimetableWindow(self.parent)

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error),
                parent=self.window
            )


if __name__ == "__main__":
    from database.database import create_tables
    create_tables()

    root = ctk.CTk()
    GenerateTimetableWindow(root)
    root.mainloop()
