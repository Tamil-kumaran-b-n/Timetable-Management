import customtkinter as ctk
from tkinter import messagebox


class LoginWindow:
    def __init__(self, on_login_success=None):
        self.on_login_success = on_login_success

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title(
            "Login - Smart Academic Timetable Management System"
        )
        self.window.geometry("1000x650")
        self.window.minsize(900, 600)

        self.create_login_screen()

    def create_login_screen(self):

        # Main background
        container = ctk.CTkFrame(
            self.window,
            fg_color="white",
            corner_radius=0
        )
        container.pack(fill="both", expand=True)

        # Main title
        title = ctk.CTkLabel(
            container,
            text="Smart Academic Timetable Management System",
            font=("Arial", 28, "bold"),
            text_color="#1F2937"
        )
        title.pack(pady=(65, 10))

        # Subtitle
        subtitle = ctk.CTkLabel(
            container,
            text="College Academic Management Portal",
            font=("Arial", 15),
            text_color="#6B7280"
        )
        subtitle.pack(pady=(0, 30))

        # Login card
        card = ctk.CTkFrame(
            container,
            width=420,
            height=400,
            fg_color="#F8FAFC",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.pack()
        card.pack_propagate(False)

        # Login heading
        login_title = ctk.CTkLabel(
            card,
            text="Login",
            font=("Arial", 24, "bold"),
            text_color="#111827"
        )
        login_title.pack(pady=(28, 22))

        # Username
        username_label = ctk.CTkLabel(
            card,
            text="Username",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        )
        username_label.pack(anchor="w", padx=50)

        self.username_entry = ctk.CTkEntry(
            card,
            width=320,
            height=40,
            placeholder_text="Enter username",
            font=("Arial", 14)
        )
        self.username_entry.pack(pady=(5, 18))

        # Password
        password_label = ctk.CTkLabel(
            card,
            text="Password",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        )
        password_label.pack(anchor="w", padx=50)

        self.password_entry = ctk.CTkEntry(
            card,
            width=320,
            height=40,
            placeholder_text="Enter password",
            show="*",
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=(5, 10))

        # Show password
        self.show_password = ctk.BooleanVar(value=False)

        show_password_check = ctk.CTkCheckBox(
            card,
            text="Show password",
            variable=self.show_password,
            command=self.toggle_password,
            font=("Arial", 12)
        )
        show_password_check.pack(
            anchor="w",
            padx=50,
            pady=(0, 18)
        )

        # Login button
        login_button = ctk.CTkButton(
            card,
            text="Login",
            width=320,
            height=42,
            font=("Arial", 15, "bold"),
            command=self.login
        )
        login_button.pack()

        # Footer
        footer = ctk.CTkLabel(
            container,
            text="Smart Academic Timetable Management System",
            font=("Arial", 11),
            text_color="#9CA3AF"
        )
        footer.pack(side="bottom", pady=18)

        # Enter key
        self.window.bind(
            "<Return>",
            lambda event: self.login()
        )

        # Focus username
        self.username_entry.focus()

    def toggle_password(self):

        if self.show_password.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showwarning(
                "Login",
                "Please enter username and password.",
                parent=self.window
            )
            return

        # Temporary administrator login
        if username == "admin" and password == "admin123":

            messagebox.showinfo(
                "Login Successful",
                "Welcome, Administrator!\n\n"
                "Login successful.",
                parent=self.window
            )

            # Close login window
            self.window.destroy()

            # Open dashboard through main.py
            if self.on_login_success:
                self.on_login_success()

        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.",
                parent=self.window
            )

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.run()