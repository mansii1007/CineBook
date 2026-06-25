"""
CineBook - Ticket Module
Generates professional tickets with QR codes and manages booking history.
"""

import io
import os
import tkinter as tk
from tkinter import filedialog

from ui import RoundedButton, Theme, UIHelpers


class TicketWindow:
    """Display a generated ticket with QR code and print/save options."""

    def __init__(
        self,
        root: tk.Tk,
        db,
        app,
        booking: dict,
        is_new: bool = False,
    ) -> None:
        self.root = root
        self.db = db
        self.app = app
        self.booking = booking
        self.is_new = is_new
        self.qr_image = None
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the ticket display layout."""
        container = tk.Frame(self.root, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=Theme.BG_CARD, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = "Booking Confirmed! 🎉" if self.is_new else "Your Ticket"
        UIHelpers.create_label(header, title, "heading", Theme.SUCCESS, bg=Theme.BG_CARD).pack(
            side="left", padx=20, pady=15
        )

        ticket_outer = tk.Frame(container, bg=Theme.BG_DARK)
        ticket_outer.pack(expand=True, pady=20)

        ticket = tk.Frame(
            ticket_outer,
            bg="#ffffff",
            highlightbackground=Theme.ACCENT,
            highlightthickness=3,
            padx=30,
            pady=25,
        )
        ticket.pack()

        tk.Label(
            ticket,
            text="🎬 CINEBOOK",
            font=("Segoe UI", 20, "bold"),
            fg=Theme.ACCENT,
            bg="#ffffff",
        ).pack()
        tk.Label(
            ticket,
            text="MOVIE TICKET",
            font=("Segoe UI", 11),
            fg="#666666",
            bg="#ffffff",
        ).pack(pady=(0, 15))

        divider = tk.Frame(ticket, bg=Theme.ACCENT, height=2)
        divider.pack(fill="x", pady=5)

        details = [
            ("Booking ID", self.booking["booking_id"]),
            ("Movie", self.booking["movie_name"]),
            ("Theatre", self.booking["theatre"]),
            ("Date", self.booking["show_date"]),
            ("Time", self.booking["timing"]),
            ("Seats", self.booking["seats"]),
            ("Amount Paid", f"₹{self.booking['amount']:.0f}"),
            ("Payment", self.booking["payment_method"]),
        ]
        if self.booking.get("snack_combo"):
            details.append(("Snack Combo", self.booking["snack_combo"]))
        if self.booking.get("coupon_code"):
            details.append(("Coupon", f"{self.booking['coupon_code']} ({self.booking['discount']}% off)"))

        for label, value in details:
            row = tk.Frame(ticket, bg="#ffffff")
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=f"{label}:",
                font=Theme.FONTS["ticket"],
                fg="#888888",
                bg="#ffffff",
                width=14,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row,
                text=str(value),
                font=("Courier New", 10, "bold"),
                fg="#222222",
                bg="#ffffff",
                anchor="w",
            ).pack(side="left")

        qr_frame = tk.Frame(ticket, bg="#ffffff")
        qr_frame.pack(pady=15)
        qr_photo = self._generate_qr()
        if qr_photo:
            self.qr_image = qr_photo
            tk.Label(qr_frame, image=qr_photo, bg="#ffffff").pack()
            tk.Label(
                qr_frame,
                text="Scan for verification",
                font=Theme.FONTS["small"],
                fg="#888888",
                bg="#ffffff",
            ).pack()

        tk.Label(
            ticket,
            text="Enjoy your movie! 🍿",
            font=Theme.FONTS["body"],
            fg=Theme.ACCENT,
            bg="#ffffff",
        ).pack(pady=(10, 0))

        btn_frame = tk.Frame(container, bg=Theme.BG_DARK)
        btn_frame.pack(pady=15)

        RoundedButton(
            btn_frame,
            text="Save Ticket",
            command=self._save_ticket,
            width=130,
            height=38,
            bg_color=Theme.INFO,
            hover_color="#5dade2",
        ).pack(side="left", padx=8)

        RoundedButton(
            btn_frame,
            text="Dashboard",
            command=self._go_dashboard,
            width=130,
            height=38,
        ).pack(side="left", padx=8)

    def _generate_qr(self):
        """Generate a QR code image for the booking ID."""
        try:
            import qrcode
            from PIL import Image, ImageTk

            qr_data = (
                f"CineBook|{self.booking['booking_id']}|"
                f"{self.booking['movie_name']}|{self.booking['seats']}"
            )
            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((120, 120), Image.Resampling.NEAREST)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _save_ticket(self) -> None:
        """Save ticket details to a text file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"ticket_{self.booking['booking_id']}.txt",
        )
        if not filepath:
            return
        try:
            lines = [
                "=" * 40,
                "       CINEBOOK - MOVIE TICKET",
                "=" * 40,
                f"Booking ID: {self.booking['booking_id']}",
                f"Movie: {self.booking['movie_name']}",
                f"Theatre: {self.booking['theatre']}",
                f"Date: {self.booking['show_date']}",
                f"Time: {self.booking['timing']}",
                f"Seats: {self.booking['seats']}",
                f"Amount: ₹{self.booking['amount']:.0f}",
                f"Payment: {self.booking['payment_method']}",
                f"Status: {self.booking.get('status', 'confirmed')}",
                "=" * 40,
            ]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            UIHelpers.show_message(self.root, "Saved", f"Ticket saved to:\n{filepath}", "success")
        except OSError as exc:
            UIHelpers.show_message(self.root, "Error", str(exc), "error")

    def _go_dashboard(self) -> None:
        """Navigate back to the dashboard."""
        from dashboard import DashboardWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        DashboardWindow(self.root, self.db, self.app)


class BookingHistoryWindow:
    """Modal window showing user's past bookings with cancel/print options."""

    def __init__(self, root: tk.Tk, db, app) -> None:
        self.root = root
        self.db = db
        self.app = app
        self.window = tk.Toplevel(root)
        self.window.title("My Bookings")
        self.window.configure(bg=Theme.BG_DARK)
        self.window.geometry("750x500")
        self.window.transient(root)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build scrollable booking history list."""
        UIHelpers.create_label(
            self.window, "Booking History", "title"
        ).pack(pady=(15, 10))

        canvas = tk.Canvas(self.window, bg=Theme.BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas, bg=Theme.BG_DARK)

        list_frame.bind(
            "<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y", pady=10)

        bookings = self.db.get_user_bookings(self.app.current_user["id"])
        if not bookings:
            UIHelpers.create_label(
                list_frame, "No bookings yet.", "body", Theme.TEXT_MUTED
            ).pack(pady=30)
            return

        for booking in bookings:
            self._create_booking_row(list_frame, booking)

        RoundedButton(
            self.window,
            text="Close",
            command=self.window.destroy,
            width=100,
            height=36,
        ).pack(pady=10)

    def _create_booking_row(self, parent, booking: dict) -> None:
        """Render a single booking row with action buttons."""
        status = booking.get("status", "confirmed")
        status_color = Theme.SUCCESS if status == "confirmed" else Theme.ERROR

        card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        card.pack(fill="x", pady=6, padx=5)

        info = (
            f"{booking['movie_name']}  |  {booking['theatre']}  |  "
            f"{booking['show_date']} {booking['timing']}  |  "
            f"Seats: {booking['seats']}  |  ₹{booking['amount']:.0f}"
        )
        UIHelpers.create_label(
            card, info, "body", bg=Theme.BG_CARD
        ).pack(side="left", padx=12, pady=10)

        UIHelpers.create_label(
            card, status.upper(), "small", status_color, bg=Theme.BG_CARD
        ).pack(side="left", padx=5)

        btn_frame = tk.Frame(card, bg=Theme.BG_CARD)
        btn_frame.pack(side="right", padx=10)

        RoundedButton(
            btn_frame,
            text="Ticket",
            command=lambda b=booking: self._view_ticket(b),
            width=70,
            height=30,
            bg_color=Theme.INFO,
            hover_color="#5dade2",
        ).pack(side="left", padx=3)

        if status == "confirmed":
            RoundedButton(
                btn_frame,
                text="Cancel",
                command=lambda b=booking: self._cancel_booking(b),
                width=70,
                height=30,
                bg_color=Theme.ERROR,
                hover_color="#ec7063",
            ).pack(side="left", padx=3)

    def _view_ticket(self, booking: dict) -> None:
        """Open ticket view for a past booking."""
        full_booking = self.db.get_booking_by_id(booking["booking_id"])
        if full_booking:
            TicketWindow(self.root, self.db, self.app, full_booking)

    def _cancel_booking(self, booking: dict) -> None:
        """Cancel a confirmed booking."""
        success, message = self.db.cancel_booking(
            booking["booking_id"], self.app.current_user["id"]
        )
        msg_type = "success" if success else "error"
        UIHelpers.show_message(self.root, "Cancel Booking", message, msg_type)
        if success:
            self.window.destroy()
            BookingHistoryWindow(self.root, self.db, self.app)
