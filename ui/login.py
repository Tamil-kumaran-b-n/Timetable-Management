import customtkinter as ctk
from tkinter import messagebox

from database.database import (
    authenticate_user,
    add_user,
    get_app_setting
)


class LoginWindow:
    def __init__(self, window=None, on_login_success=None):
        self.on_login_success = on_login_success
        self.current_mode = "login"  # "login" or "register"

        # Apply saved appearance and scaling settings
        saved_mode = get_app_setting("appearance_mode", "Light")
        ctk.set_appearance_mode(saved_mode)
        ctk.set_default_color_theme("blue")

        saved_scaling = get_app_setting("ui_scaling", "100%")
        try:
            scale_factor = float(saved_scaling.replace("%", "").strip()) / 100.0
            ctk.set_widget_scaling(scale_factor)
        except Exception:
            pass

        if window is not None:
            self.window = window
            for widget in self.window.winfo_children():
                widget.destroy()
        else:
            self.window = ctk.CTk()

        self.window.title(
            "Login - Smart Academic Timetable Management System"
        )
        self.window.geometry("1000x680")
        self.window.minsize(900, 620)

        self.create_login_screen()

    def create_login_screen(self):
        # Main background container
        self.container = ctk.CTkFrame(
            self.window,
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True)

        # Main title
        self.title_label = ctk.CTkLabel(
            self.container,
            text="Smart Academic Timetable Management System",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack(pady=(45, 8))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.container,
            text="College Academic Management Portal",
            font=("Arial", 15),
            text_color="#6B7280"
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Center card container
        self.card = ctk.CTkFrame(
            self.container,
            width=440,
            corner_radius=16,
            border_width=1,
            border_color=("#E5E7EB", "#374151")
        )
        self.card.pack(pady=10)

        # Mode segment (Login vs Create Account)
        self.mode_segment = ctk.CTkSegmentedButton(
            self.card,
            values=["Sign In", "Create Account"],
            command=self.on_mode_change,
            font=("Arial", 13, "bold"),
            height=36
        )
        self.mode_segment.set("Sign In")
        self.mode_segment.pack(fill="x", padx=35, pady=(24, 15))

        # Dynamic form container inside the card
        self.form_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # Footer
        self.footer = ctk.CTkLabel(
            self.container,
            text="Smart Academic Timetable Management System • Secured with Salted PBKDF2 Encryption",
            font=("Arial", 11),
            text_color="#9CA3AF"
        )
        self.footer.pack(side="bottom", pady=16)

        # Render initial form
        self.render_login_form()

    def on_mode_change(self, mode_value):
        if mode_value == "Sign In":
            self.render_login_form()
        else:
            self.render_register_form()

    def render_login_form(self):
        self.current_mode = "login"
        for w in self.form_frame.winfo_children():
            w.destroy()

        # Login heading
        login_title = ctk.CTkLabel(
            self.form_frame,
            text="Sign In to Your Account",
            font=("Arial", 20, "bold")
        )
        login_title.pack(pady=(5, 18))

        # Username
        username_label = ctk.CTkLabel(
            self.form_frame,
            text="Account Name (Username)",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 4))

        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            height=38,
            placeholder_text="e.g. admin or username",
            font=("Arial", 13)
        )
        self.username_entry.pack(fill="x", pady=(0, 14))

        # Password
        password_label = ctk.CTkLabel(
            self.form_frame,
            text="Password",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            height=38,
            placeholder_text="Enter your password",
            show="*",
            font=("Arial", 13)
        )
        self.password_entry.pack(fill="x", pady=(0, 8))

        # Show password toggle
        self.show_password_var = ctk.BooleanVar(value=False)
        show_password_check = ctk.CTkCheckBox(
            self.form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_login_password,
            font=("Arial", 12)
        )
        show_password_check.pack(anchor="w", pady=(0, 18))

        # Login button
        self.submit_button = ctk.CTkButton(
            self.form_frame,
            text="Sign In",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.login
        )
        self.submit_button.pack(fill="x", pady=(0, 12))

        # Switch link button
        switch_btn = ctk.CTkButton(
            self.form_frame,
            text="Don't have an account? Create one",
            fg_color="transparent",
            hover=False,
            text_color=("#2563EB", "#60A5FA"),
            font=("Arial", 12, "underline"),
            command=lambda: [self.mode_segment.set("Create Account"), self.render_register_form()]
        )
        switch_btn.pack()

        # Bind Enter key
        self.window.bind("<Return>", lambda event: self.login())
        self.username_entry.focus()

    def render_register_form(self):
        self.current_mode = "register"
        for w in self.form_frame.winfo_children():
            w.destroy()

        # Register heading
        reg_title = ctk.CTkLabel(
            self.form_frame,
            text="Create New Account",
            font=("Arial", 20, "bold")
        )
        reg_title.pack(pady=(0, 14))

        # Username / Account Name
        reg_user_label = ctk.CTkLabel(
            self.form_frame,
            text="Account Name (Username)",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        reg_user_label.pack(fill="x", pady=(0, 3))

        self.reg_username_entry = ctk.CTkEntry(
            self.form_frame,
            height=36,
            placeholder_text="Enter new account name (min 3 chars)",
            font=("Arial", 13)
        )
        self.reg_username_entry.pack(fill="x", pady=(0, 10))

        # Role
        role_label = ctk.CTkLabel(
            self.form_frame,
            text="Role",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        role_label.pack(fill="x", pady=(0, 3))

        self.reg_role_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Administrator", "Faculty", "Staff"],
            height=36,
            font=("Arial", 13),
            state="readonly"
        )
        self.reg_role_combo.set("Administrator")
        self.reg_role_combo.pack(fill="x", pady=(0, 10))

        # Password
        reg_pwd_label = ctk.CTkLabel(
            self.form_frame,
            text="Password",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        reg_pwd_label.pack(fill="x", pady=(0, 3))

        self.reg_password_entry = ctk.CTkEntry(
            self.form_frame,
            height=36,
            placeholder_text="Enter password (min 4 chars)",
            show="*",
            font=("Arial", 13)
        )
        self.reg_password_entry.pack(fill="x", pady=(0, 10))

        # Confirm Password
        reg_confirm_label = ctk.CTkLabel(
            self.form_frame,
            text="Confirm Password",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        reg_confirm_label.pack(fill="x", pady=(0, 3))

        self.reg_confirm_entry = ctk.CTkEntry(
            self.form_frame,
            height=36,
            placeholder_text="Re-type password",
            show="*",
            font=("Arial", 13)
        )
        self.reg_confirm_entry.pack(fill="x", pady=(0, 6))

        # Show password toggle
        self.reg_show_pwd_var = ctk.BooleanVar(value=False)
        reg_show_pwd_check = ctk.CTkCheckBox(
            self.form_frame,
            text="Show passwords",
            variable=self.reg_show_pwd_var,
            command=self.toggle_reg_password,
            font=("Arial", 12)
        )
        reg_show_pwd_check.pack(anchor="w", pady=(0, 14))

        # Register button
        self.reg_submit_button = ctk.CTkButton(
            self.form_frame,
            text="Create Account & Sign In",
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self.register_user
        )
        self.reg_submit_button.pack(fill="x", pady=(0, 10))

        # Switch link button
        switch_btn = ctk.CTkButton(
            self.form_frame,
            text="Already have an account? Sign In",
            fg_color="transparent",
            hover=False,
            text_color=("#2563EB", "#60A5FA"),
            font=("Arial", 12, "underline"),
            command=lambda: [self.mode_segment.set("Sign In"), self.render_login_form()]
        )
        switch_btn.pack()

        # Bind Enter key
        self.window.bind("<Return>", lambda event: self.register_user())
        self.reg_username_entry.focus()

    def toggle_login_password(self):
        show_char = "" if self.show_password_var.get() else "*"
        self.password_entry.configure(show=show_char)

    def toggle_reg_password(self):
        show_char = "" if self.reg_show_pwd_var.get() else "*"
        self.reg_password_entry.configure(show=show_char)
        self.reg_confirm_entry.configure(show=show_char)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showwarning(
                "Login",
                "Please enter both username and password.",
                parent=self.window
            )
            return

        user = authenticate_user(username, password)
        if user:
            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {user.get('username', 'User')}!\n\n"
                f"Logged in as {user.get('role', 'Administrator')}.",
                parent=self.window
            )

            # Unbind enter key
            self.window.unbind("<Return>")

            # Open dashboard in the same window
            if self.on_login_success:
                try:
                    self.on_login_success(self.window, user)
                except TypeError:
                    try:
                        self.on_login_success(self.window)
                    except TypeError:
                        self.on_login_success()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.\n\nPlease check your credentials or create a new account.",
                parent=self.window
            )

    def register_user(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_pwd = self.reg_confirm_entry.get()
        role = self.reg_role_combo.get().strip() or "Administrator"

        if not username:
            messagebox.showwarning("Create Account", "Please enter an account name.", parent=self.window)
            self.reg_username_entry.focus()
            return

        if len(username) < 3:
            messagebox.showwarning("Create Account", "Account name must be at least 3 characters.", parent=self.window)
            self.reg_username_entry.focus()
            return

        if not password:
            messagebox.showwarning("Create Account", "Please enter a password.", parent=self.window)
            self.reg_password_entry.focus()
            return

        if len(password) < 4:
            messagebox.showwarning("Create Account", "Password must be at least 4 characters long.", parent=self.window)
            self.reg_password_entry.focus()
            return

        if password != confirm_pwd:
            messagebox.showerror("Create Account", "Passwords do not match. Please re-enter.", parent=self.window)
            self.reg_confirm_entry.focus()
            return

        success, msg = add_user(username, password, role)
        if not success:
            messagebox.showerror("Create Account Failed", msg, parent=self.window)
            return

        messagebox.showinfo(
            "Account Created",
            f"Account '{username}' created successfully!\n\nLogging you in now...",
            parent=self.window
        )

        user = authenticate_user(username, password)
        # Unbind enter key
        self.window.unbind("<Return>")

        # Open dashboard in the same window
        if self.on_login_success:
            try:
                self.on_login_success(self.window, user)
            except TypeError:
                try:
                    self.on_login_success(self.window)
                except TypeError:
                    self.on_login_success()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    from database.database import create_tables
    from ui.dashboard import Dashboard

    create_tables()

    def _on_success(win, user=None):
        Dashboard(window=win, current_user=user)

    login_app = LoginWindow(on_login_success=_on_success)
    login_app.run()