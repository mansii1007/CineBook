"""
CineBook - Shared UI Components
Theme colors, rounded buttons, and reusable UI helpers.
"""

import os
import tkinter as tk


class Theme:
    """Centralized dark theme colors and typography for the entire app."""

    BG_DARK = "#0f0f1a"
    BG_CARD = "#1a1a2e"
    BG_INPUT = "#16213e"
    ACCENT = "#e94560"
    ACCENT_HOVER = "#ff6b81"
    SUCCESS = "#2ecc71"
    WARNING = "#f39c12"
    ERROR = "#e74c3c"
    INFO = "#3498db"
    TEXT_PRIMARY = "#eaeaea"
    TEXT_SECONDARY = "#a0a0b0"
    TEXT_MUTED = "#6c6c7c"
    BORDER = "#2a2a4a"
    SEAT_AVAILABLE = "#27ae60"
    SEAT_BOOKED = "#c0392b"
    SEAT_SELECTED = "#2980b9"
    SEAT_HOVER = "#3498db"

    FONTS = {
        "title": ("Segoe UI", 24, "bold"),
        "heading": ("Segoe UI", 16, "bold"),
        "subheading": ("Segoe UI", 13, "bold"),
        "body": ("Segoe UI", 11),
        "small": ("Segoe UI", 9),
        "button": ("Segoe UI", 11, "bold"),
        "ticket": ("Courier New", 10),
    }


class RoundedButton(tk.Canvas):
    """Custom rounded button with hover effect built on Canvas."""

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        width: int = 160,
        height: int = 42,
        bg_color: str = Theme.ACCENT,
        hover_color: str = Theme.ACCENT_HOVER,
        text_color: str = Theme.TEXT_PRIMARY,
        font=None,
        **kwargs,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=Theme.BG_DARK,
            highlightthickness=0,
            **kwargs,
        )
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.btn_font = font or Theme.FONTS["button"]
        self.text = text
        self._draw(self.bg_color)
        self.bind("<Enter>", lambda _e: self._draw(self.hover_color))
        self.bind("<Leave>", lambda _e: self._draw(self.bg_color))
        self.bind("<Button-1>", self._on_click)

    def _draw(self, color: str) -> None:
        """Redraw the rounded rectangle and label."""
        self.delete("all")
        w, h = int(self["width"]), int(self["height"])
        r = 12
        self.create_arc(0, 0, r * 2, r * 2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, 0, w, r * 2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h - r * 2, r * 2, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w - r * 2, h - r * 2, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h - r, fill=color, outline=color)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.text_color, font=self.btn_font)

    def _on_click(self, _event) -> None:
        """Execute the button command when clicked."""
        if self.command:
            self.command()


class UIHelpers:
    """Reusable UI helper methods for consistent styling."""

    @staticmethod
    def configure_root(root: tk.Tk) -> None:
        """Apply global window and ttk styling."""
        root.configure(bg=Theme.BG_DARK)
        root.option_add("*Font", Theme.FONTS["body"])
        root.option_add("*Background", Theme.BG_DARK)
        root.option_add("*Foreground", Theme.TEXT_PRIMARY)

    @staticmethod
    def create_label(parent, text: str, style: str = "body", color: str = None, **kwargs) -> tk.Label:
        """Create a themed label with preset font styles."""
        return tk.Label(
            parent,
            text=text,
            font=Theme.FONTS.get(style, Theme.FONTS["body"]),
            fg=color or Theme.TEXT_PRIMARY,
            bg=kwargs.pop("bg", Theme.BG_DARK),
            **kwargs,
        )

    @staticmethod
    def create_entry(parent, **kwargs) -> tk.Entry:
        """Create a styled text entry field."""
        entry = tk.Entry(
            parent,
            font=Theme.FONTS["body"],
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT,
            **kwargs,
        )
        return entry

    @staticmethod
    def show_message(parent, title: str, message: str, msg_type: str = "info") -> None:
        """Display a styled message dialog."""
        colors = {
            "info": Theme.INFO,
            "success": Theme.SUCCESS,
            "error": Theme.ERROR,
            "warning": Theme.WARNING,
        }
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg=Theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        w, h = 380, 180
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(
            dialog,
            text=title,
            font=Theme.FONTS["heading"],
            fg=colors.get(msg_type, Theme.INFO),
            bg=Theme.BG_CARD,
        ).pack(pady=(20, 10))

        tk.Label(
            dialog,
            text=message,
            font=Theme.FONTS["body"],
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD,
            wraplength=340,
            justify="center",
        ).pack(pady=5, padx=20)

        RoundedButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100,
            height=36,
        ).pack(pady=15)

    @staticmethod
    def get_asset_path(filename: str) -> str:
        """Return absolute path to an asset file."""
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "assets", filename)

    @staticmethod
    def load_poster(poster_name: str, size=(140, 200)):
        """Load and resize a movie poster, returning a PhotoImage or None."""
        try:
            from PIL import Image, ImageTk

            base = os.path.dirname(os.path.abspath(__file__))
            poster_path = os.path.join(base, "assets", "posters", poster_name)
            if not os.path.exists(poster_path):
                img = Image.new("RGB", size, Theme.BG_INPUT)
            else:
                img = Image.open(poster_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None
