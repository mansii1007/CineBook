"""
CineBook - Register Module
Handles new user registration with input validation.
"""

import re
import tkinter as tk

from ui import RoundedButton, Theme, UIHelpers


class RegisterWindow:
    """Registration form for creating new user accounts."""

    def __init__(self, root: tk.Tk, db, app) -> None:
        self.root = root
        self.db = db
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the registration form layout."""
        container = tk.Frame(self.root, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True)

        form = tk.Frame(container, bg=Theme.BG_DARK)
        form.place(relx=0.5, rely=0.5, anchor="center")

        UIHelpers.create_label(form, "Create Account", "title").pack(anchor="w")
        UIHelpers.create_label(
            form, "Join CineBook and start booking", "body", Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 25))

        fields = [
            ("Username", "username", False),
            ("Email", "email", False),
            ("Password", "password", True),
            ("Confirm Password", "confirm", True),
        ]
        self.entries = {}

        for label, key, hidden in fields:
            UIHelpers.create_label(form, label, "subheading").pack(anchor="w")
            entry = UIHelpers.create_entry(form, width=35, show="•" if hidden else "")
            entry.pack(pady=(5, 12), ipady=8)
            self.entries[key] = entry

        RoundedButton(
            form, text="Register", command=self._register, width=280, height=44
        ).pack(pady=(10, 15))

        back_frame = tk.Frame(form, bg=Theme.BG_DARK)
        back_frame.pack()
        UIHelpers.create_label(
            back_frame, "Already have an account?", "body", Theme.TEXT_SECONDARY
        ).pack(side="left")
        link = UIHelpers.create_label(
            back_frame, " Login", "body", Theme.ACCENT, cursor="hand2"
        )
        link.pack(side="left")
        link.bind("<Button-1>", lambda _e: self._back_to_login())

    def _validate_password(self, password: str) -> tuple:
        """Validate password strength requirements."""
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if not re.search(r"[A-Za-z]", password):
            return False, "Password must contain at least one letter."
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number."
        return True, ""

    def _validate_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _register(self) -> None:
        """Validate inputs and register the new user."""
        username = self.entries["username"].get().strip()
        email = self.entries["email"].get().strip().lower()
        password = self.entries["password"].get()
        confirm = self.entries["confirm"].get()

        if len(username) < 3:
            UIHelpers.show_message(
                self.root, "Validation Error", "Username must be at least 3 characters.", "error"
            )
            return
        if not self._validate_email(email):
            UIHelpers.show_message(
                self.root, "Validation Error", "Please enter a valid email address.", "error"
            )
            return

        valid, msg = self._validate_password(password)
        if not valid:
            UIHelpers.show_message(self.root, "Validation Error", msg, "error")
            return
        if password != confirm:
            UIHelpers.show_message(self.root, "Validation Error", "Passwords do not match.", "error")
            return

        success, message = self.db.register_user(username, email, password)
        if success:
            UIHelpers.show_message(self.root, "Success", message, "success")
            self._back_to_login()
        else:
            UIHelpers.show_message(self.root, "Registration Failed", message, "error")

    def _back_to_login(self) -> None:
        """Return to the login screen."""
        from login import LoginWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        LoginWindow(self.root, self.db, self.app)
