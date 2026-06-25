"""
CineBook - Login Module
Handles user authentication and navigation to register or dashboard.
"""

import tkinter as tk

from ui import RoundedButton, Theme, UIHelpers


class LoginWindow:
    """Login screen with username/password fields and validation."""

    def __init__(self, root: tk.Tk, db, app) -> None:
        self.root = root
        self.db = db
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the login interface layout."""
        container = tk.Frame(self.root, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True)

        left = tk.Frame(container, bg=Theme.BG_CARD, width=420)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        tk.Label(
            left,
            text="🎬",
            font=("Segoe UI", 48),
            bg=Theme.BG_CARD,
            fg=Theme.ACCENT,
        ).pack(pady=(80, 10))

        UIHelpers.create_label(
            left, "CineBook", "title", Theme.ACCENT, bg=Theme.BG_CARD
        ).pack()
        UIHelpers.create_label(
            left,
            "Your Ultimate Movie\nTicket Booking Experience",
            "body",
            Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD,
            justify="center",
        ).pack(pady=(10, 30))

        UIHelpers.create_label(
            left, "Demo: demo / demo123", "small", Theme.TEXT_MUTED, bg=Theme.BG_CARD
        ).pack()
        UIHelpers.create_label(
            left, "Admin: admin / admin123", "small", Theme.TEXT_MUTED, bg=Theme.BG_CARD
        ).pack(pady=(2, 0))

        right = tk.Frame(container, bg=Theme.BG_DARK)
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=Theme.BG_DARK)
        form.place(relx=0.5, rely=0.5, anchor="center")

        UIHelpers.create_label(form, "Welcome Back", "title").pack(anchor="w")
        UIHelpers.create_label(
            form, "Sign in to continue booking", "body", Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 25))

        UIHelpers.create_label(form, "Username", "subheading").pack(anchor="w")
        self.username_entry = UIHelpers.create_entry(form, width=35)
        self.username_entry.pack(pady=(5, 15), ipady=8)

        UIHelpers.create_label(form, "Password", "subheading").pack(anchor="w")
        self.password_entry = UIHelpers.create_entry(form, width=35, show="•")
        self.password_entry.pack(pady=(5, 20), ipady=8)
        self.password_entry.bind("<Return>", lambda _e: self._login())

        RoundedButton(
            form, text="Login", command=self._login, width=280, height=44
        ).pack(pady=(5, 15))

        reg_frame = tk.Frame(form, bg=Theme.BG_DARK)
        reg_frame.pack()
        UIHelpers.create_label(
            reg_frame, "Don't have an account?", "body", Theme.TEXT_SECONDARY
        ).pack(side="left")
        link = UIHelpers.create_label(
            reg_frame, " Register", "body", Theme.ACCENT, cursor="hand2"
        )
        link.pack(side="left")
        link.bind("<Button-1>", lambda _e: self._open_register())

    def _validate_inputs(self) -> bool:
        """Validate that username and password fields are not empty."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            UIHelpers.show_message(self.root, "Validation Error", "Username is required.", "error")
            return False
        if not password:
            UIHelpers.show_message(self.root, "Validation Error", "Password is required.", "error")
            return False
        if len(username) < 3:
            UIHelpers.show_message(
                self.root, "Validation Error", "Username must be at least 3 characters.", "error"
            )
            return False
        return True

    def _login(self) -> None:
        """Attempt login and navigate to dashboard on success."""
        if not self._validate_inputs():
            return

        user, message = self.db.login_user(
            self.username_entry.get().strip(),
            self.password_entry.get(),
        )
        if user:
            self.app.set_user(user)
            from dashboard import DashboardWindow

            for widget in self.root.winfo_children():
                widget.destroy()
            DashboardWindow(self.root, self.db, self.app)
        else:
            UIHelpers.show_message(self.root, "Login Failed", message, "error")

    def _open_register(self) -> None:
        """Open the registration window."""
        from register import RegisterWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        RegisterWindow(self.root, self.db, self.app)
