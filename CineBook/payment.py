"""
CineBook - Payment Module
Simulates payment via UPI, Credit Card, or Cash with coupon and snack support.
"""

import re
import tkinter as tk

from ticket import TicketWindow
from ui import RoundedButton, Theme, UIHelpers


class PaymentWindow:
    """Payment form with method selection, coupons, and snack combos."""

    def __init__(
        self,
        root: tk.Tk,
        db,
        app,
        movie: dict,
        show: dict,
        seats: list,
    ) -> None:
        self.root = root
        self.db = db
        self.app = app
        self.movie = movie
        self.show = show
        self.seats = seats
        self.payment_method = tk.StringVar(value="UPI")
        self.snack_var = tk.StringVar(value="None")
        self.coupon_discount = 0.0
        self.coupon_code = ""
        self._build_ui()

    def _calculate_total(self) -> float:
        """Calculate total amount including snacks and coupon discount."""
        ticket_total = len(self.seats) * self.movie["price"]
        snack_total = 0.0
        snack_name = self.snack_var.get()
        if snack_name != "None":
            for snack in self.db.get_snacks():
                if snack["name"] == snack_name:
                    snack_total = snack["price"]
                    break
        subtotal = ticket_total + snack_total
        discount = subtotal * (self.coupon_discount / 100)
        return max(subtotal - discount, 0)

    def _build_ui(self) -> None:
        """Construct payment summary and input forms."""
        container = tk.Frame(self.root, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True, padx=30, pady=20)

        UIHelpers.create_label(container, "Payment", "title").pack(anchor="w")
        UIHelpers.create_label(
            container, "Complete your booking", "body", Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        content = tk.Frame(container, bg=Theme.BG_DARK)
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg=Theme.BG_CARD, padx=20, pady=20)
        left.pack(side="left", fill="both", expand=True, padx=(0, 15))

        UIHelpers.create_label(left, "Booking Summary", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w"
        )

        summary_lines = [
            f"Movie: {self.movie['movie_name']}",
            f"Theatre: {self.show['theatre']}",
            f"Date: {self.show['show_date']}",
            f"Time: {self.show['timing']}",
            f"Seats: {', '.join(sorted(self.seats))}",
            f"Tickets: {len(self.seats)} × ₹{self.movie['price']:.0f}",
        ]
        for line in summary_lines:
            UIHelpers.create_label(
                left, line, "body", Theme.TEXT_SECONDARY, bg=Theme.BG_CARD
            ).pack(anchor="w", pady=2)

        UIHelpers.create_label(left, "Snack Combo", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w", pady=(15, 5)
        )
        snack_options = ["None"] + [s["name"] for s in self.db.get_snacks()]
        for snack in snack_options:
            tk.Radiobutton(
                left,
                text=self._snack_label(snack),
                variable=self.snack_var,
                value=snack,
                font=Theme.FONTS["body"],
                fg=Theme.TEXT_PRIMARY,
                bg=Theme.BG_CARD,
                selectcolor=Theme.BG_INPUT,
                activebackground=Theme.BG_CARD,
                command=self._update_total_label,
            ).pack(anchor="w")

        coupon_frame = tk.Frame(left, bg=Theme.BG_CARD)
        coupon_frame.pack(fill="x", pady=(15, 5))
        UIHelpers.create_label(coupon_frame, "Coupon Code", "subheading", bg=Theme.BG_CARD).pack(
            anchor="w"
        )
        entry_row = tk.Frame(coupon_frame, bg=Theme.BG_CARD)
        entry_row.pack(fill="x", pady=5)
        self.coupon_entry = UIHelpers.create_entry(entry_row, width=20)
        self.coupon_entry.pack(side="left", ipady=4)
        self.coupon_entry.insert(0, "CINEBOOK10")
        RoundedButton(
            entry_row,
            text="Apply",
            command=self._apply_coupon,
            width=80,
            height=32,
            bg_color=Theme.INFO,
            hover_color="#5dade2",
        ).pack(side="left", padx=8)

        right = tk.Frame(content, bg=Theme.BG_CARD, padx=20, pady=20)
        right.pack(side="right", fill="both", expand=True)

        UIHelpers.create_label(
            right, "Payment Method", "subheading", bg=Theme.BG_CARD
        ).pack(anchor="w")

        methods = [
            ("UPI", "📱 UPI Payment"),
            ("Credit Card", "💳 Credit Card"),
            ("Cash", "💵 Cash at Counter"),
        ]
        for value, label in methods:
            tk.Radiobutton(
                right,
                text=label,
                variable=self.payment_method,
                value=value,
                font=Theme.FONTS["body"],
                fg=Theme.TEXT_PRIMARY,
                bg=Theme.BG_CARD,
                selectcolor=Theme.BG_INPUT,
                activebackground=Theme.BG_CARD,
                command=self._toggle_payment_fields,
            ).pack(anchor="w", pady=4)

        self.payment_fields = tk.Frame(right, bg=Theme.BG_CARD)
        self.payment_fields.pack(fill="x", pady=15)

        self.total_label = UIHelpers.create_label(
            right, "", "heading", Theme.ACCENT, bg=Theme.BG_CARD
        )
        self.total_label.pack(pady=10)
        self._update_total_label()
        self._toggle_payment_fields()

        btn_row = tk.Frame(right, bg=Theme.BG_CARD)
        btn_row.pack(pady=10)

        RoundedButton(
            btn_row,
            text="← Back",
            command=self._go_back,
            width=100,
            height=38,
            bg_color=Theme.BG_INPUT,
            hover_color=Theme.BORDER,
        ).pack(side="left", padx=5)

        RoundedButton(
            btn_row,
            text="Pay & Confirm",
            command=self._confirm_payment,
            width=160,
            height=38,
            bg_color=Theme.SUCCESS,
            hover_color="#58d68d",
        ).pack(side="left", padx=5)

    def _snack_label(self, snack_name: str) -> str:
        """Return display label for a snack option with price."""
        if snack_name == "None":
            return "No Snacks"
        for snack in self.db.get_snacks():
            if snack["name"] == snack_name:
                return f"{snack['name']} — ₹{snack['price']:.0f}"
        return snack_name

    def _toggle_payment_fields(self) -> None:
        """Show relevant input fields based on payment method."""
        for widget in self.payment_fields.winfo_children():
            widget.destroy()

        method = self.payment_method.get()
        if method == "UPI":
            UIHelpers.create_label(
                self.payment_fields, "UPI ID", "body", bg=Theme.BG_CARD
            ).pack(anchor="w")
            self.upi_entry = UIHelpers.create_entry(self.payment_fields, width=30)
            self.upi_entry.pack(fill="x", ipady=6, pady=5)
            self.upi_entry.insert(0, "user@upi")
        elif method == "Credit Card":
            fields = [("Card Number", "card"), ("CVV", "cvv"), ("Expiry (MM/YY)", "expiry")]
            self.card_entries = {}
            for label, key in fields:
                UIHelpers.create_label(
                    self.payment_fields, label, "body", bg=Theme.BG_CARD
                ).pack(anchor="w")
                entry = UIHelpers.create_entry(
                    self.payment_fields, width=30, show="•" if key == "cvv" else ""
                )
                entry.pack(fill="x", ipady=6, pady=(0, 8))
                self.card_entries[key] = entry
            self.card_entries["card"].insert(0, "4111 1111 1111 1111")
            self.card_entries["expiry"].insert(0, "12/28")

    def _apply_coupon(self) -> None:
        """Validate and apply a discount coupon."""
        code = self.coupon_entry.get().strip()
        if not code:
            UIHelpers.show_message(self.root, "Coupon", "Enter a coupon code.", "warning")
            return
        discount, message = self.db.validate_coupon(code)
        if discount:
            self.coupon_discount = discount
            self.coupon_code = code.upper()
            self._update_total_label()
            UIHelpers.show_message(
                self.root, "Coupon Applied", f"{message} ({discount}% off)", "success"
            )
        else:
            self.coupon_discount = 0
            self.coupon_code = ""
            self._update_total_label()
            UIHelpers.show_message(self.root, "Invalid Coupon", message, "error")

    def _update_total_label(self) -> None:
        """Refresh the total amount display."""
        total = self._calculate_total()
        discount_text = f" ({self.coupon_discount}% off)" if self.coupon_discount else ""
        self.total_label.configure(text=f"Total: ₹{total:.0f}{discount_text}")

    def _validate_payment(self) -> bool:
        """Validate payment details based on selected method."""
        method = self.payment_method.get()
        if method == "UPI":
            upi = getattr(self, "upi_entry", None)
            if upi and not re.match(r"^[\w.\-]+@[\w]+$", upi.get().strip()):
                UIHelpers.show_message(self.root, "Invalid UPI", "Enter a valid UPI ID.", "error")
                return False
        elif method == "Credit Card":
            card = self.card_entries.get("card", None)
            cvv = self.card_entries.get("cvv", None)
            expiry = self.card_entries.get("expiry", None)
            if card and len(card.get().replace(" ", "")) < 16:
                UIHelpers.show_message(self.root, "Invalid Card", "Enter a valid card number.", "error")
                return False
            if cvv and len(cvv.get()) < 3:
                UIHelpers.show_message(self.root, "Invalid CVV", "Enter a valid CVV.", "error")
                return False
            if expiry and not re.match(r"^\d{2}/\d{2}$", expiry.get()):
                UIHelpers.show_message(
                    self.root, "Invalid Expiry", "Use MM/YY format.", "error"
                )
                return False
        return True

    def _confirm_payment(self) -> None:
        """Process payment simulation and create booking."""
        if not self._validate_payment():
            return

        total = self._calculate_total()
        snack_name = self.snack_var.get() if self.snack_var.get() != "None" else ""

        booking_id, message = self.db.create_booking(
            user_id=self.app.current_user["id"],
            movie_id=self.movie["id"],
            show_id=self.show["id"],
            seats=self.seats,
            amount=total,
            payment_method=self.payment_method.get(),
            snack_combo=snack_name,
            coupon_code=self.coupon_code,
            discount=self.coupon_discount,
        )

        if booking_id:
            booking = self.db.get_booking_by_id(booking_id)
            for widget in self.root.winfo_children():
                widget.destroy()
            TicketWindow(self.root, self.db, self.app, booking, is_new=True)
        else:
            UIHelpers.show_message(self.root, "Booking Failed", message, "error")

    def _go_back(self) -> None:
        """Return to seat selection."""
        from booking import BookingWindow

        for widget in self.root.winfo_children():
            widget.destroy()
        BookingWindow(self.root, self.db, self.app, self.movie)
