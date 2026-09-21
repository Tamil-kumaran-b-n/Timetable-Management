import customtkinter as ctk
from tkinter import messagebox

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

        self.window = container if self.embedded else ctk.CTkToplevel(parent)
        if not self.embedded:
            self.window.title("Generate Timetable")
            self.window.geometry("1050x700")
            self.window.minsize(900, 600)
            self.window.transient(parent)
            self.window.grab_set()

        self.build_ui()
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
            )
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            self.main_frame,
            text=(
                "Generate a balanced timetable from the faculty "
                "workload."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="gray"
        ).pack(
            anchor="w",
            pady=(5, 25)
        )

        # ----------------------------------------------------
        # Rules Card
        # ----------------------------------------------------

        rules_card = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12
        )
        rules_card.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            rules_card,
            text="Timetable Structure",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        rules_text = (
            "• 6 Day Orders\n"
            "• 5 Periods per Day\n"
            "• 30 Total Slots per Class\n"
            "• Workloads are distributed across different Day Orders\n"
            "• Consecutive periods for the same subject are avoided\n"
            "• Important workloads receive scheduling priority\n"
            "• Faculty and class clashes are avoided"
        )

        ctk.CTkLabel(
            rules_card,
            text=rules_text,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(
                size=13
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
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
            corner_radius=12
        )
        self.status_card.pack(
            fill="x",
            pady=(0, 25)
        )

        self.status_label = ctk.CTkLabel(
            self.status_card,
            text="Ready to generate timetable.",
            font=ctk.CTkFont(
                size=14
            )
        )
        self.status_label.pack(
            anchor="w",
            padx=20,
            pady=18
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
            height=48,
            font=ctk.CTkFont(
                size=15,
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
            height=48,
            fg_color="gray",
            hover_color="#555555",
            command=self.load_workload_summary
        )
        self.refresh_button.pack(
            side="left",
            padx=(0, 12)
        )

        self.view_button = ctk.CTkButton(
            button_frame,
            text="View Timetable",
            height=48,
            state="disabled",
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
            corner_radius=12
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
                size=13
            ),
            text_color="gray"
        ).pack(
            pady=(15, 3)
        )

        value = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        value.pack(
            pady=(0, 15)
        )

        return value

    # ========================================================
    # LOAD WORKLOAD SUMMARY
    # ========================================================

    def load_workload_summary(self):

        try:
            workloads = get_all_workloads()

            total = len(workloads)

            important = sum(
                1
                for row in workloads
                if row[12] == "Important"
            )

            normal = total - important

            total_periods = sum(
                row[13]
                for row in workloads
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

            if total == 0:

                self.status_label.configure(
                    text=(
                        "No workload found. "
                        "Please add faculty workload before generating."
                    )
                )

                self.generate_button.configure(
                    state="disabled"
                )

            else:

                self.status_label.configure(
                    text=(
                        f"{total} workload(s) ready. "
                        f"{total_periods} period(s) will be scheduled."
                    )
                )

                self.generate_button.configure(
                    state="normal"
                )

        except Exception as error:

            self.status_label.configure(
                text="Unable to load workload information."
            )

            self.generate_button.configure(
                state="disabled"
            )

            messagebox.showerror(
                "Error",
                f"Unable to load workload information.\n\n{error}",
                parent=self.window
            )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(self):

        workloads = get_all_workloads()

        if not workloads:

            messagebox.showwarning(
                "No Workload",
                (
                    "No faculty workload is available.\n\n"
                    "Please add workload first."
                ),
                parent=self.window
            )

            return

        confirm = messagebox.askyesno(
            "Generate Timetable",
            (
                "Generate a new timetable using the current "
                "faculty workload?\n\n"
                "The previously generated timetable will be replaced."
            ),
            parent=self.window
        )

        if not confirm:
            return

        self.generate_button.configure(
            state="disabled",
            text="Generating..."
        )

        self.refresh_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Generating timetable. Please wait..."
        )

        self.window.update_idletasks()

        try:

            result = generate_timetable()

            if result:

                timetable = get_all_timetable()

                self.status_label.configure(
                    text=(
                        "Timetable generated successfully. "
                        f"{len(timetable)} slot(s) created."
                    )
                )

                self.view_button.configure(
                    state="normal"
                )

                messagebox.showinfo(
                    "Generation Complete",
                    (
                        "Timetable generated successfully!\n\n"
                        f"Total timetable entries: {len(timetable)}"
                    ),
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
                (
                    "An unexpected error occurred while "
                    "generating the timetable.\n\n"
                    f"{error}"
                ),
                parent=self.window
            )

        finally:

            self.generate_button.configure(
                state="normal",
                text="Generate Timetable"
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

        except ImportError:

            messagebox.showinfo(
                "View Timetable",
                (
                    "Timetable has been generated successfully.\n\n"
                    "The timetable viewing screen will be connected next."
                ),
                parent=self.window
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error),
                parent=self.window
            )


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()

    root.withdraw()

    GenerateTimetableWindow(root)

    root.mainloop()
