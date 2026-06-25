"""
CineBook - Main Entry Point
Launches the application and provides the app controller.
"""

import os
import tkinter as tk

from database import Database
from login import LoginWindow
from ui import UIHelpers


class CineBookApp:
    """Main application controller."""

    def __init__(self) -> None:
        """Initialize database and launch the login screen."""
        self.db = Database()
        self.root = tk.Tk()
        self.root.title("CineBook - Movie Ticket Booking System")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        UIHelpers.configure_root(self.root)

        try:
            icon_path = UIHelpers.get_asset_path("logo.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

        self.current_user = None
        LoginWindow(self.root, self.db, self)

    def set_user(self, user: dict) -> None:
        """Store the currently logged-in user."""
        self.current_user = user

    def logout(self) -> None:
        """Clear session and return to login screen."""
        self.current_user = None
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginWindow(self.root, self.db, self)

    def run(self) -> None:
        """Start the Tkinter main event loop."""
        self.root.mainloop()


def main() -> None:
    """Application entry point."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = CineBookApp()
    app.run()


if __name__ == "__main__":
    main()
