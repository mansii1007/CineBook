"""
CineBook - Booking Module
Handles theatre selection, show timing, and seat layout booking.
"""

import tkinter as tk
from tkinter import ttk

from payment import PaymentWindow
from ui import RoundedButton, Theme, UIHelpers


class BookingWindow:
    """Multi-step booking: date → theatre/show → seat selection."""

    ROWS = 6
    COLS = 8
    ROW_LABELS = ["A", "B", "C", "D", "E", "F"]

    def __init__(self, root: tk.Tk, db, app, movie: dict) -> None:
        self.root = root
        self.db = db
        self.app = app
        self.movie = movie
        self.selected_show = None
        self.selected_seats = []
        self.seat_buttons = {}
        self.booked_seats = set()
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the booking interface with theatre and seat panels."""
        self.header = tk.Frame(self.root, bg=Theme.BG_CARD, height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        RoundedButton(
            self.header,
            text="← Back",
            command=self._go_back,
            width=90,
            height=34,
            bg_color=Theme.BG_INPUT,
            hover_color=Theme.BORDER,
        ).pack(side="left", padx=15, pady=12)

        UIHelpers.create_label(
            self.header,
            f"Booking: {self.movie['movie_name']}",
            "heading",
            bg=Theme.BG_CARD,
        ).pack(side="left", padx=10)

        main = tk.Frame(self.root, bg=Theme.BG_DARK)
        main.pack(fill="both", expand=True, padx=20, pady=15)

        left = tk.Frame(main, bg=Theme.BG_CARD, width=340)
        left.pack(side="left", fill="y", padx=(0, 15))
        left.pack_propagate(False)

        UIHelpers.create_label(left, "Select Date", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        dates = self.db.get_show_dates(self.movie["id"])
        self.date_var = tk.StringVar(value=dates[0] if dates else "")
        date_combo = ttk.Combobox(
            left, textvariable=self.date_var, values=dates, state="readonly", width=28
        )
        date_combo.pack(padx=15, pady=5)
        date_combo.bind("<<ComboboxSelected>>", lambda _e: self._load_shows())

        UIHelpers.create_label(left, "Theatre & Show", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.show_list_frame = tk.Frame(left, bg=Theme.BG_CARD)
        self.show_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        right = tk.Frame(main, bg=Theme.BG_CARD)
        right.pack(side="right", fill="both", expand=True)

        UIHelpers.create_label(right, "Select Seats", "subheading", bg=Theme.BG_CARD).pack(
            pady=(15, 5)
        )

        screen = tk.Label(
            right,
            text="══════ SCREEN ══════",
            font=Theme.FONTS["small"],
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_CARD,
        )
        screen.pack(pady=5)

        self.seat_frame = tk.Frame(right, bg=Theme.BG_CARD)
        self.seat_frame.pack(pady=10)

        legend = tk.Frame(right, bg=Theme.BG_CARD)
        legend.pack(pady=10)
        for color, label in [
            (Theme.SEAT_AVAILABLE, "Available"),
            (Theme.SEAT_BOOKED, "Booked"),
            (Theme.SEAT_SELECTED, "Selected"),
        ]:
            f = tk.Frame(legend, bg=Theme.BG_CARD)
            f.pack(side="left", padx=10)
            tk.Canvas(f, width=16, height=16, bg=color, highlightthickness=0).pack(side="left")
            UIHelpers.create_label(f, label, "small", Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(
                side="left", padx=4
            )

        self.summary_label = UIHelpers.create_label(
            right, "Selected: None", "body", Theme.TEXT_SECONDARY, bg=Theme.BG_CARD
        )
        self.summary_label.pack(pady=5)

        RoundedButton(
            right,
            text="Proceed to Payment →",
            command=self._proceed_payment,
            width=220,
            height=40,
        ).pack(pady=15)

        self._load_shows()
        self._build_seat_grid()

    def _load_shows(self) -> None:
        """Load available shows for the selected date."""
        for widget in self.show_list_frame.winfo_children():
            widget.destroy()

        shows = self.db.get_shows_for_movie(self.movie["id"], self.date_var.get())
        if not shows:
            UIHelpers.create_label(
                self.show_list_frame, "No shows available.", "body", Theme.TEXT_MUTED, bg=Theme.BG_CARD
            ).pack(pady=10)
            return

        theatres = {}
        for show in shows:
            theatres.setdefault(show["theatre"], []).append(show)

        for theatre, theatre_shows in theatres.items():
            UIHelpers.create_label(
                self.show_list_frame, theatre, "subheading", Theme.ACCENT, bg=Theme.BG_CARD
            ).pack(anchor="w", padx=5, pady=(8, 4))

            timing_frame = tk.Frame(self.show_list_frame, bg=Theme.BG_CARD)
            timing_frame.pack(anchor="w", padx=5)

            for show in theatre_shows:
                btn = RoundedButton(
                    timing_frame,
                    text=show["timing"],
                    command=lambda s=show: self._select_show(s),
                    width=90,
                    height=32,
                    bg_color=Theme.BG_INPUT,
                    hover_color=Theme.INFO,
                )
                btn.pack(side="left", padx=4, pady=4)

    def _select_show(self, show: dict) -> None:
        """Select a show and refresh booked seats on the grid."""
        self.selected_show = show
        self.selected_seats.clear()
        self.booked_seats = set(self.db.get_booked_seats(show["id"]))
        self._refresh_seat_colors()
        self._update_summary()
        UIHelpers.show_message(
            self.root,
            "Show Selected",
            f"{show['theatre']} — {show['timing']}",
            "info",
        )

    def _build_seat_grid(self) -> None:
        """Create the 6×8 seat layout grid."""
        for r in range(self.ROWS):
            row_label = UIHelpers.create_label(
                self.seat_frame, self.ROW_LABELS[r], "body", bg=Theme.BG_CARD
            )
            row_label.grid(row=r, column=0, padx=5)

            for c in range(self.COLS):
                seat_id = f"{self.ROW_LABELS[r]}{c + 1}"
                btn = tk.Button(
                    self.seat_frame,
                    text=str(c + 1),
                    width=3,
                    height=1,
                    font=Theme.FONTS["small"],
                    bg=Theme.SEAT_AVAILABLE,
                    fg="white",
                    activebackground=Theme.SEAT_HOVER,
                    relief="flat",
                    cursor="hand2",
                    command=lambda s=seat_id: self._toggle_seat(s),
                )
                btn.grid(row=r, column=c + 1, padx=3, pady=3)
                self.seat_buttons[seat_id] = btn

    def _toggle_seat(self, seat_id: str) -> None:
        """Toggle seat selection if the seat is available."""
        if not self.selected_show:
            UIHelpers.show_message(
                self.root, "Select Show", "Please select a theatre and show timing first.", "warning"
            )
            return
        if seat_id in self.booked_seats:
            return

        if seat_id in self.selected_seats:
            self.selected_seats.remove(seat_id)
        else:
            if len(self.selected_seats) >= 10:
                UIHelpers.show_message(
                    self.root, "Limit Reached", "Maximum 10 seats per booking.", "warning"
                )
                return
            self.selected_seats.append(seat_id)

        self._refresh_seat_colors()
        self._update_summary()

    def _refresh_seat_colors(self) -> None:
        """Update seat button colors based on booking state."""
        for seat_id, btn in self.seat_buttons.items():
            if seat_id in self.booked_seats:
                btn.configure(bg=Theme.SEAT_BOOKED, state="disabled")
            elif seat_id in self.selected_seats:
                btn.configure(bg=Theme.SEAT_SELECTED, state="normal")
            else:
                btn.configure(bg=Theme.SEAT_AVAILABLE, state="normal")

    def _update_summary(self) -> None:
        """Update the selected seats summary label."""
        if self.selected_seats:
            seats = ", ".join(sorted(self.selected_seats))
            total = len(self.selected_seats) * self.movie["price"]
            self.summary_label.configure(
                text=f"Selected: {seats}  |  ₹{total:.0f}", fg=Theme.ACCENT
            )
        else:
            self.summary_label.configure(text="Selected: None", fg=Theme.TEXT_SECONDARY)

    def _proceed_payment(self) -> None:
        """Validate selection and open payment window."""
        if not self.selected_show:
            UIHelpers.show_message(self.root, "Error", "Please select a show timing.", "error")
            return
        if not self.selected_seats:
            UIHelpers.show_message(self.root, "Error", "Please select at least one seat.", "error")
            return

        for widget in self.root.winfo_children():
            widget.destroy()
        PaymentWindow(
            self.root,
            self.db,
            self.app,
            self.movie,
            self.selected_show,
            self.selected_seats,
        )

    def _go_back(self) -> None:
        """Return to the movie dashboard."""
        from dashboard import DashboardWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        DashboardWindow(self.root, self.db, self.app)
