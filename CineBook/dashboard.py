"""
CineBook - Dashboard Module
Displays movie cards with search, filter, sort, and favorites.
"""

import tkinter as tk
from tkinter import ttk

from booking import BookingWindow
from ticket import BookingHistoryWindow
from ui import RoundedButton, Theme, UIHelpers


class DashboardWindow:
    """Main movie browsing dashboard after login."""

    def __init__(self, root: tk.Tk, db, app) -> None:
        self.root = root
        self.db = db
        self.app = app
        self.user = app.current_user
        self.poster_refs = []
        self._build_ui()
        self._load_movies()

    def _build_ui(self) -> None:
        """Construct header, filters, and scrollable movie grid."""
        self.header = tk.Frame(self.root, bg=Theme.BG_CARD, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        UIHelpers.create_label(
            self.header, "🎬 CineBook", "heading", Theme.ACCENT, bg=Theme.BG_CARD
        ).pack(side="left", padx=20, pady=15)

        welcome = UIHelpers.create_label(
            self.header,
            f"Hello, {self.user['username']}!",
            "body",
            Theme.TEXT_SECONDARY,
            bg=Theme.BG_CARD,
        )
        welcome.pack(side="left", padx=10)

        btn_frame = tk.Frame(self.header, bg=Theme.BG_CARD)
        btn_frame.pack(side="right", padx=15)

        RoundedButton(
            btn_frame,
            text="My Bookings",
            command=self._open_history,
            width=130,
            height=36,
            bg_color=Theme.INFO,
            hover_color="#5dade2",
        ).pack(side="left", padx=5)

        if self.user.get("is_admin"):
            RoundedButton(
                btn_frame,
                text="Admin Panel",
                command=self._open_admin,
                width=130,
                height=36,
                bg_color=Theme.WARNING,
                hover_color="#f5b041",
            ).pack(side="left", padx=5)

        RoundedButton(
            btn_frame,
            text="Logout",
            command=self.app.logout,
            width=90,
            height=36,
            bg_color=Theme.BG_INPUT,
            hover_color=Theme.BORDER,
        ).pack(side="left", padx=5)

        filter_bar = tk.Frame(self.root, bg=Theme.BG_DARK)
        filter_bar.pack(fill="x", padx=20, pady=15)

        UIHelpers.create_label(filter_bar, "Search:", "body").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_movies())
        search_entry = UIHelpers.create_entry(filter_bar, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=(8, 20), ipady=4)

        UIHelpers.create_label(filter_bar, "Genre:", "body").pack(side="left")
        self.genre_var = tk.StringVar(value="All")
        genres = ["All"] + self.db.get_genres()
        genre_combo = ttk.Combobox(
            filter_bar, textvariable=self.genre_var, values=genres, width=14, state="readonly"
        )
        genre_combo.pack(side="left", padx=(8, 20))
        genre_combo.bind("<<ComboboxSelected>>", lambda _e: self._load_movies())

        UIHelpers.create_label(filter_bar, "Sort:", "body").pack(side="left")
        self.sort_var = tk.StringVar(value="name")
        sort_combo = ttk.Combobox(
            filter_bar,
            textvariable=self.sort_var,
            values=["name", "rating", "price_low", "price_high"],
            width=14,
            state="readonly",
        )
        sort_combo.pack(side="left", padx=8)
        sort_combo.bind("<<ComboboxSelected>>", lambda _e: self._load_movies())

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=Theme.BG_INPUT, background=Theme.BG_CARD)

        canvas_frame = tk.Frame(self.root, bg=Theme.BG_DARK)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.canvas = tk.Canvas(canvas_frame, bg=Theme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.movie_frame = tk.Frame(self.canvas, bg=Theme.BG_DARK)

        self.movie_frame.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.movie_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event) -> None:
        """Scroll the movie grid with mouse wheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_movies(self) -> None:
        """Fetch and render movie cards based on current filters."""
        for widget in self.movie_frame.winfo_children():
            widget.destroy()
        self.poster_refs.clear()

        movies = self.db.get_all_movies(
            search=self.search_var.get(),
            genre=self.genre_var.get(),
            sort_by=self.sort_var.get(),
        )

        if not movies:
            UIHelpers.create_label(
                self.movie_frame, "No movies found.", "heading", Theme.TEXT_MUTED
            ).pack(pady=50)
            return

        favorites = self.db.get_favorites(self.user["id"])
        cols = 3
        for idx, movie in enumerate(movies):
            row, col = divmod(idx, cols)
            self._create_movie_card(movie, row, col, movie["id"] in favorites)

    def _create_movie_card(self, movie: dict, row: int, col: int, is_fav: bool) -> None:
        """Render a single movie card with poster and book button."""
        card = tk.Frame(
            self.movie_frame,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

        poster = UIHelpers.load_poster(movie.get("poster", ""), (150, 210))
        if poster:
            self.poster_refs.append(poster)
            tk.Label(card, image=poster, bg=Theme.BG_CARD).pack(pady=(12, 8))
        else:
            placeholder = tk.Label(
                card,
                text="🎬",
                font=("Segoe UI", 40),
                bg=Theme.BG_INPUT,
                width=10,
                height=5,
            )
            placeholder.pack(pady=(12, 8))

        UIHelpers.create_label(
            card, movie["movie_name"], "subheading", bg=Theme.BG_CARD
        ).pack(anchor="w", padx=12)

        info = f"{movie['genre']} | {movie['language']} | ⭐ {movie['rating']}"
        UIHelpers.create_label(
            card, info, "small", Theme.TEXT_SECONDARY, bg=Theme.BG_CARD
        ).pack(anchor="w", padx=12, pady=2)

        UIHelpers.create_label(
            card,
            f"⏱ {movie['duration']}  |  ₹{movie['price']:.0f}",
            "body",
            Theme.ACCENT,
            bg=Theme.BG_CARD,
        ).pack(anchor="w", padx=12, pady=(2, 10))

        btn_row = tk.Frame(card, bg=Theme.BG_CARD)
        btn_row.pack(pady=(0, 12))

        fav_text = "♥" if is_fav else "♡"
        RoundedButton(
            btn_row,
            text=fav_text,
            command=lambda m=movie: self._toggle_favorite(m),
            width=40,
            height=36,
            bg_color=Theme.BG_INPUT,
            hover_color=Theme.ACCENT,
        ).pack(side="left", padx=4)

        RoundedButton(
            btn_row,
            text="Book Now",
            command=lambda m=movie: self._book_movie(m),
            width=120,
            height=36,
        ).pack(side="left", padx=4)

        for c in range(3):
            self.movie_frame.grid_columnconfigure(c, weight=1)

    def _toggle_favorite(self, movie: dict) -> None:
        """Add or remove a movie from favorites and refresh cards."""
        is_fav = self.db.toggle_favorite(self.user["id"], movie["id"])
        msg = f"'{movie['movie_name']}' added to favorites!" if is_fav else f"Removed from favorites."
        UIHelpers.show_message(self.root, "Favorites", msg, "success")
        self._load_movies()

    def _book_movie(self, movie: dict) -> None:
        """Open the booking flow for the selected movie."""
        for widget in self.root.winfo_children():
            widget.destroy()
        BookingWindow(self.root, self.db, self.app, movie)

    def _open_history(self) -> None:
        """Open booking history window."""
        BookingHistoryWindow(self.root, self.db, self.app)

    def _open_admin(self) -> None:
        """Open admin panel for admin users."""
        from admin import AdminPanel

        for widget in self.root.winfo_children():
            widget.destroy()
        AdminPanel(self.root, self.db, self.app)
