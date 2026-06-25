"""
CineBook - Admin Panel Module
Provides movie management, show scheduling, bookings overview, and analytics.
"""

import tkinter as tk
from tkinter import ttk

from ui import RoundedButton, Theme, UIHelpers


class AdminPanel:
    """Admin dashboard for managing movies, shows, and viewing analytics."""

    def __init__(self, root: tk.Tk, db, app) -> None:
        self.root = root
        self.db = db
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct tabbed admin interface."""
        header = tk.Frame(self.root, bg=Theme.BG_CARD, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        UIHelpers.create_label(
            header, "⚙ Admin Panel", "heading", Theme.WARNING, bg=Theme.BG_CARD
        ).pack(side="left", padx=20, pady=15)

        RoundedButton(
            header,
            text="← Dashboard",
            command=self._go_dashboard,
            width=130,
            height=34,
            bg_color=Theme.BG_INPUT,
            hover_color=Theme.BORDER,
        ).pack(side="right", padx=15, pady=12)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=Theme.BG_DARK)
        style.configure("TNotebook.Tab", padding=[12, 6])

        tabs = {
            "Movies": self._build_movies_tab,
            "Shows": self._build_shows_tab,
            "Bookings": self._build_bookings_tab,
            "Revenue": self._build_revenue_tab,
            "Occupancy": self._build_occupancy_tab,
        }
        for name, builder in tabs.items():
            frame = tk.Frame(notebook, bg=Theme.BG_DARK)
            notebook.add(frame, text=name)
            builder(frame)

    def _build_movies_tab(self, parent) -> None:
        """Build movie CRUD management tab."""
        top = tk.Frame(parent, bg=Theme.BG_DARK)
        top.pack(fill="x", pady=10)

        RoundedButton(
            top, text="+ Add Movie", command=self._add_movie_dialog, width=130, height=36
        ).pack(side="left", padx=5)

        list_frame = tk.Frame(parent, bg=Theme.BG_CARD)
        list_frame.pack(fill="both", expand=True, pady=10)

        columns = ("id", "name", "genre", "duration", "language", "rating", "price")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        headings = {
            "id": "ID",
            "name": "Movie Name",
            "genre": "Genre",
            "duration": "Duration",
            "language": "Language",
            "rating": "Rating",
            "price": "Price (₹)",
        }
        for col, heading in headings.items():
            tree.heading(col, text=heading)
            tree.column(col, width=100 if col != "name" else 180)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        movies = self.db.get_all_movies()
        for movie in movies:
            tree.insert(
                "",
                "end",
                values=(
                    movie["id"],
                    movie["movie_name"],
                    movie["genre"],
                    movie["duration"],
                    movie["language"],
                    movie["rating"],
                    f"{movie['price']:.0f}",
                ),
            )

        btn_row = tk.Frame(parent, bg=Theme.BG_DARK)
        btn_row.pack(pady=10)

        RoundedButton(
            btn_row,
            text="Edit Selected",
            command=lambda: self._edit_movie_dialog(tree),
            width=130,
            height=36,
            bg_color=Theme.INFO,
            hover_color="#5dade2",
        ).pack(side="left", padx=5)

        RoundedButton(
            btn_row,
            text="Delete Selected",
            command=lambda: self._delete_movie(tree),
            width=130,
            height=36,
            bg_color=Theme.ERROR,
            hover_color="#ec7063",
        ).pack(side="left", padx=5)

    def _build_shows_tab(self, parent) -> None:
        """Build show timing management tab."""
        form = tk.Frame(parent, bg=Theme.BG_CARD, padx=20, pady=20)
        form.pack(fill="x", pady=10)

        UIHelpers.create_label(form, "Add Show Timing", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w"
        )

        movies = self.db.get_all_movies()
        movie_names = [f"{m['id']} - {m['movie_name']}" for m in movies]

        row1 = tk.Frame(form, bg=Theme.BG_CARD)
        row1.pack(fill="x", pady=8)
        UIHelpers.create_label(row1, "Movie:", "body", bg=Theme.BG_CARD).pack(side="left")
        self.show_movie_var = tk.StringVar(value=movie_names[0] if movie_names else "")
        ttk.Combobox(row1, textvariable=self.show_movie_var, values=movie_names, width=35).pack(
            side="left", padx=10
        )

        row2 = tk.Frame(form, bg=Theme.BG_CARD)
        row2.pack(fill="x", pady=8)
        UIHelpers.create_label(row2, "Theatre:", "body", bg=Theme.BG_CARD).pack(side="left")
        self.show_theatre_entry = UIHelpers.create_entry(row2, width=25)
        self.show_theatre_entry.pack(side="left", padx=10, ipady=4)
        self.show_theatre_entry.insert(0, "PVR Phoenix")

        row3 = tk.Frame(form, bg=Theme.BG_CARD)
        row3.pack(fill="x", pady=8)
        UIHelpers.create_label(row3, "Timing:", "body", bg=Theme.BG_CARD).pack(side="left")
        self.show_timing_entry = UIHelpers.create_entry(row3, width=15)
        self.show_timing_entry.pack(side="left", padx=10, ipady=4)
        self.show_timing_entry.insert(0, "6:00 PM")

        UIHelpers.create_label(row3, "Date (YYYY-MM-DD):", "body", bg=Theme.BG_CARD).pack(
            side="left", padx=(20, 0)
        )
        self.show_date_entry = UIHelpers.create_entry(row3, width=15)
        self.show_date_entry.pack(side="left", padx=10, ipady=4)

        from datetime import datetime

        self.show_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        RoundedButton(
            form, text="Add Show", command=self._add_show, width=120, height=36
        ).pack(anchor="w", pady=10)

    def _build_bookings_tab(self, parent) -> None:
        """Build all bookings overview tab."""
        list_frame = tk.Frame(parent, bg=Theme.BG_CARD)
        list_frame.pack(fill="both", expand=True, pady=10)

        columns = ("id", "user", "movie", "theatre", "date", "seats", "amount", "method", "status")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col, heading in zip(
            columns,
            ["Booking ID", "User", "Movie", "Theatre", "Date/Time", "Seats", "Amount", "Payment", "Status"],
        ):
            tree.heading(col, text=heading)
            tree.column(col, width=90 if col != "movie" else 140)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for b in self.db.get_all_bookings():
            tree.insert(
                "",
                "end",
                values=(
                    b["booking_id"],
                    b["username"],
                    b["movie_name"],
                    b["theatre"],
                    f"{b['show_date']} {b['timing']}",
                    b["seats"],
                    f"₹{b['amount']:.0f}",
                    b["payment_method"],
                    b["status"],
                ),
            )

    def _build_revenue_tab(self, parent) -> None:
        """Build revenue analytics tab."""
        data = self.db.get_revenue()

        card = tk.Frame(parent, bg=Theme.BG_CARD, padx=30, pady=30)
        card.pack(fill="x", pady=20, padx=20)

        UIHelpers.create_label(
            card, f"Total Revenue: ₹{data['total']:.0f}", "title", Theme.SUCCESS, bg=Theme.BG_CARD
        ).pack(anchor="w", pady=(0, 20))

        UIHelpers.create_label(
            card, "Revenue by Payment Method", "subheading", bg=Theme.BG_CARD
        ).pack(anchor="w")

        for method, amount in data["by_method"].items():
            UIHelpers.create_label(
                card,
                f"  {method}: ₹{amount:.0f}",
                "body",
                Theme.TEXT_SECONDARY,
                bg=Theme.BG_CARD,
            ).pack(anchor="w", pady=4)

        UIHelpers.create_label(
            card,
            f"\nTotal Bookings: {len(self.db.get_all_bookings())}",
            "body",
            bg=Theme.BG_CARD,
        ).pack(anchor="w", pady=(15, 0))

        confirmed = sum(1 for b in self.db.get_all_bookings() if b["status"] == "confirmed")
        cancelled = sum(1 for b in self.db.get_all_bookings() if b["status"] == "cancelled")
        UIHelpers.create_label(
            card, f"Confirmed: {confirmed}  |  Cancelled: {cancelled}", "body", bg=Theme.BG_CARD
        ).pack(anchor="w")

    def _build_occupancy_tab(self, parent) -> None:
        """Build seat occupancy analytics tab."""
        list_frame = tk.Frame(parent, bg=Theme.BG_CARD)
        list_frame.pack(fill="both", expand=True, pady=10)

        columns = ("movie", "theatre", "date", "time", "booked", "total", "percent")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col, heading in zip(
            columns, ["Movie", "Theatre", "Date", "Time", "Booked", "Total", "Occupancy %"]
        ):
            tree.heading(col, text=heading)
            tree.column(col, width=110)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in self.db.get_occupancy():
            tree.insert(
                "",
                "end",
                values=(
                    item["movie_name"],
                    item["theatre"],
                    item["show_date"],
                    item["timing"],
                    item["seats_booked"],
                    item["total_seats"],
                    f"{item['occupancy_percent']}%",
                ),
            )

    def _add_movie_dialog(self) -> None:
        """Open dialog to add a new movie."""
        self._movie_form_dialog("Add Movie", self._save_new_movie)

    def _edit_movie_dialog(self, tree) -> None:
        """Open dialog to edit the selected movie."""
        selected = tree.selection()
        if not selected:
            UIHelpers.show_message(self.root, "Select Movie", "Please select a movie to edit.", "warning")
            return
        values = tree.item(selected[0])["values"]
        movie = self.db.get_movie_by_id(values[0])
        if movie:
            self._movie_form_dialog("Edit Movie", lambda data: self._save_edit_movie(values[0], data), movie)

    def _movie_form_dialog(self, title: str, on_save, movie: dict = None) -> None:
        """Reusable movie add/edit form dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=Theme.BG_CARD)
        dialog.geometry("420x480")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = {}
        field_defs = [
            ("movie_name", "Movie Name"),
            ("genre", "Genre"),
            ("duration", "Duration (e.g. 2h 30m)"),
            ("language", "Language"),
            ("rating", "Rating (0-10)"),
            ("price", "Ticket Price (₹)"),
            ("poster", "Poster Filename"),
        ]

        for key, label in field_defs:
            UIHelpers.create_label(dialog, label, "body", bg=Theme.BG_CARD).pack(anchor="w", padx=20, pady=(8, 2))
            entry = UIHelpers.create_entry(dialog, width=35)
            entry.pack(padx=20, ipady=5)
            if movie and key in movie:
                val = movie[key if key != "movie_name" else "movie_name"]
                if key == "movie_name":
                    val = movie["movie_name"]
                elif key == "poster":
                    val = movie.get("poster", "")
                else:
                    val = movie.get(key, "")
                entry.insert(0, str(val))
            fields[key] = entry

        def save():
            try:
                data = {k: v.get().strip() for k, v in fields.items()}
                if not all(data[k] for k in ["movie_name", "genre", "duration", "language", "rating", "price"]):
                    UIHelpers.show_message(dialog, "Error", "Fill all required fields.", "error")
                    return
                float(data["rating"])
                float(data["price"])
                on_save(data)
                dialog.destroy()
                self._refresh_admin()
            except ValueError:
                UIHelpers.show_message(dialog, "Error", "Rating and price must be numbers.", "error")

        RoundedButton(dialog, text="Save", command=save, width=120, height=38).pack(pady=20)

    def _save_new_movie(self, data: dict) -> None:
        """Save a newly added movie."""
        success, message = self.db.add_movie(data)
        UIHelpers.show_message(self.root, "Add Movie", message, "success" if success else "error")

    def _save_edit_movie(self, movie_id: int, data: dict) -> None:
        """Save edits to an existing movie."""
        success, message = self.db.update_movie(movie_id, data)
        UIHelpers.show_message(self.root, "Edit Movie", message, "success" if success else "error")

    def _delete_movie(self, tree) -> None:
        """Delete the selected movie."""
        selected = tree.selection()
        if not selected:
            UIHelpers.show_message(self.root, "Select Movie", "Please select a movie to delete.", "warning")
            return
        movie_id = tree.item(selected[0])["values"][0]
        success, message = self.db.delete_movie(movie_id)
        UIHelpers.show_message(self.root, "Delete Movie", message, "success" if success else "error")
        self._refresh_admin()

    def _add_show(self) -> None:
        """Add a new show timing from the form."""
        movie_str = self.show_movie_var.get()
        if not movie_str:
            UIHelpers.show_message(self.root, "Error", "Select a movie.", "error")
            return
        movie_id = int(movie_str.split(" - ")[0])
        success, message = self.db.add_show(
            movie_id,
            self.show_theatre_entry.get(),
            self.show_timing_entry.get(),
            self.show_date_entry.get(),
        )
        UIHelpers.show_message(self.root, "Add Show", message, "success" if success else "error")

    def _refresh_admin(self) -> None:
        """Reload the admin panel."""
        for widget in self.root.winfo_children():
            widget.destroy()
        AdminPanel(self.root, self.db, self.app)

    def _go_dashboard(self) -> None:
        """Return to user dashboard."""
        from dashboard import DashboardWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        DashboardWindow(self.root, self.db, self.app)
