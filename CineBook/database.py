"""
CineBook - Database Module
Handles SQLite connection, schema creation, seed data, and all data operations.
"""

import hashlib
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class Database:
    """Central database manager for the CineBook application."""

    def __init__(self, db_path: str = "database/cinebook.db") -> None:
        """Initialize database path and ensure the database folder exists."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password using SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def init_database(self) -> None:
        """Create tables and seed default data if the database is empty."""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_name TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration TEXT NOT NULL,
                language TEXT NOT NULL,
                rating REAL NOT NULL,
                price REAL NOT NULL,
                poster TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS Shows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                theatre TEXT NOT NULL,
                timing TEXT NOT NULL,
                show_date TEXT NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES Movies(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Bookings (
                booking_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                show_id INTEGER NOT NULL,
                seats TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                snack_combo TEXT DEFAULT '',
                coupon_code TEXT DEFAULT '',
                discount REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (movie_id) REFERENCES Movies(id),
                FOREIGN KEY (show_id) REFERENCES Shows(id)
            );

            CREATE TABLE IF NOT EXISTS Favorites (
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (movie_id) REFERENCES Movies(id)
            );

            CREATE TABLE IF NOT EXISTS Coupons (
                code TEXT PRIMARY KEY,
                discount_percent REAL NOT NULL,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS Snacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            );
            """
        )
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            self._seed_data(cursor)
            conn.commit()

        conn.close()

    def _seed_data(self, cursor: sqlite3.Cursor) -> None:
        """Insert default admin, sample movies, shows, coupons, and snacks."""
        cursor.execute(
            "INSERT INTO Users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ("admin", "admin@cinebook.com", self.hash_password("admin123"), 1),
        )
        cursor.execute(
            "INSERT INTO Users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ("demo", "demo@cinebook.com", self.hash_password("demo123"), 0),
        )

        movies = [
            ("Inception", "Sci-Fi", "2h 28m", "English", 8.8, 250.0, "inception.jpg"),
            ("Interstellar", "Sci-Fi", "2h 49m", "English", 8.6, 280.0, "interstellar.jpg"),
            ("The Dark Knight", "Action", "2h 32m", "English", 9.0, 300.0, "dark_knight.jpg"),
            ("3 Idiots", "Comedy", "2h 50m", "Hindi", 8.4, 200.0, "3_idiots.jpg"),
            ("RRR", "Action", "3h 2m", "Telugu", 8.0, 220.0, "rrr.jpg"),
            ("Dune: Part Two", "Sci-Fi", "2h 46m", "English", 8.7, 320.0, "dune2.jpg"),
        ]
        cursor.executemany(
            """INSERT INTO Movies (movie_name, genre, duration, language, rating, price, poster)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            movies,
        )

        today = datetime.now().date()
        theatres = ["PVR Phoenix", "INOX Megaplex", "Cinepolis Orion"]
        timings = ["10:00 AM", "1:30 PM", "4:45 PM", "8:00 PM", "10:30 PM"]

        for movie_id in range(1, 7):
            for day_offset in range(3):
                show_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                for theatre in theatres:
                    for timing in timings[:3 if theatre == "INOX Megaplex" else 4]:
                        cursor.execute(
                            """INSERT INTO Shows (movie_id, theatre, timing, show_date)
                               VALUES (?, ?, ?, ?)""",
                            (movie_id, theatre, timing, show_date),
                        )

        coupons = [("CINEBOOK10", 10), ("MOVIE20", 20), ("WEEKEND15", 15)]
        cursor.executemany(
            "INSERT INTO Coupons (code, discount_percent) VALUES (?, ?)", coupons
        )

        snacks = [
            ("Popcorn Combo", 150.0),
            ("Nachos & Soda", 180.0),
            ("Premium Combo", 250.0),
        ]
        cursor.executemany(
            "INSERT INTO Snacks (name, price) VALUES (?, ?)", snacks
        )

    # ------------------------------------------------------------------ Users
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user after validating uniqueness."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(), self.hash_password(password)),
            )
            conn.commit()
            conn.close()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username or email already exists."
        except sqlite3.Error as exc:
            return False, f"Database error: {exc}"

    def login_user(self, username: str, password: str) -> Tuple[Optional[Dict], str]:
        """Authenticate a user and return user details on success."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Users WHERE username = ? AND password = ?",
                (username.strip(), self.hash_password(password)),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row), "Login successful!"
            return None, "Invalid username or password."
        except sqlite3.Error as exc:
            return None, f"Database error: {exc}"

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Fetch a single user record by ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # ----------------------------------------------------------------- Movies
    def get_all_movies(
        self,
        search: str = "",
        genre: str = "All",
        sort_by: str = "name",
    ) -> List[Dict]:
        """Return movies with optional search, genre filter, and sorting."""
        query = "SELECT * FROM Movies WHERE 1=1"
        params: List[Any] = []

        if search.strip():
            query += " AND (movie_name LIKE ? OR language LIKE ? OR genre LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        if genre and genre != "All":
            query += " AND genre = ?"
            params.append(genre)

        if sort_by == "rating":
            query += " ORDER BY rating DESC"
        elif sort_by == "price_low":
            query += " ORDER BY price ASC"
        elif sort_by == "price_high":
            query += " ORDER BY price DESC"
        else:
            query += " ORDER BY movie_name ASC"

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        """Fetch a single movie by ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Movies WHERE id = ?", (movie_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def add_movie(self, data: Dict) -> Tuple[bool, str]:
        """Insert a new movie record."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Movies (movie_name, genre, duration, language, rating, price, poster)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["movie_name"],
                    data["genre"],
                    data["duration"],
                    data["language"],
                    float(data["rating"]),
                    float(data["price"]),
                    data.get("poster", ""),
                ),
            )
            conn.commit()
            conn.close()
            return True, "Movie added successfully!"
        except (sqlite3.Error, ValueError) as exc:
            return False, str(exc)

    def update_movie(self, movie_id: int, data: Dict) -> Tuple[bool, str]:
        """Update an existing movie record."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE Movies SET movie_name=?, genre=?, duration=?, language=?,
                   rating=?, price=?, poster=? WHERE id=?""",
                (
                    data["movie_name"],
                    data["genre"],
                    data["duration"],
                    data["language"],
                    float(data["rating"]),
                    float(data["price"]),
                    data.get("poster", ""),
                    movie_id,
                ),
            )
            conn.commit()
            conn.close()
            return True, "Movie updated successfully!"
        except (sqlite3.Error, ValueError) as exc:
            return False, str(exc)

    def delete_movie(self, movie_id: int) -> Tuple[bool, str]:
        """Delete a movie and its related shows."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Movies WHERE id = ?", (movie_id,))
            conn.commit()
            conn.close()
            return True, "Movie deleted successfully!"
        except sqlite3.Error as exc:
            return False, str(exc)

    def get_genres(self) -> List[str]:
        """Return distinct movie genres for filter dropdowns."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT genre FROM Movies ORDER BY genre")
        genres = [row[0] for row in cursor.fetchall()]
        conn.close()
        return genres

    # ------------------------------------------------------------------ Shows
    def get_shows_for_movie(self, movie_id: int, show_date: str = "") -> List[Dict]:
        """Return show timings grouped by theatre for a movie."""
        query = "SELECT * FROM Shows WHERE movie_id = ?"
        params: List[Any] = [movie_id]
        if show_date:
            query += " AND show_date = ?"
            params.append(show_date)
        query += " ORDER BY theatre, timing"

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_show_dates(self, movie_id: int) -> List[str]:
        """Return available show dates for a movie."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT show_date FROM Shows WHERE movie_id = ? ORDER BY show_date",
            (movie_id,),
        )
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates

    def add_show(self, movie_id: int, theatre: str, timing: str, show_date: str) -> Tuple[bool, str]:
        """Add a new show timing for a movie."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Shows (movie_id, theatre, timing, show_date) VALUES (?, ?, ?, ?)",
                (movie_id, theatre.strip(), timing.strip(), show_date),
            )
            conn.commit()
            conn.close()
            return True, "Show added successfully!"
        except sqlite3.Error as exc:
            return False, str(exc)

    def get_show_by_id(self, show_id: int) -> Optional[Dict]:
        """Fetch show details by ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Shows WHERE id = ?", (show_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # --------------------------------------------------------------- Bookings
    def get_booked_seats(self, show_id: int) -> List[str]:
        """Return all booked seat labels for a given show."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT seats FROM Bookings WHERE show_id = ? AND status = 'confirmed'",
            (show_id,),
        )
        booked: List[str] = []
        for row in cursor.fetchall():
            booked.extend(row[0].split(","))
        conn.close()
        return booked

    def create_booking(
        self,
        user_id: int,
        movie_id: int,
        show_id: int,
        seats: List[str],
        amount: float,
        payment_method: str,
        snack_combo: str = "",
        coupon_code: str = "",
        discount: float = 0,
    ) -> Tuple[Optional[str], str]:
        """Create a booking after verifying seats are still available."""
        seat_str = ",".join(sorted(seats))
        booked = set(self.get_booked_seats(show_id))
        overlap = booked.intersection(set(seats))
        if overlap:
            return None, f"Seats already booked: {', '.join(sorted(overlap))}"

        booking_id = f"CB-{uuid.uuid4().hex[:8].upper()}"
        booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Bookings
                   (booking_id, user_id, movie_id, show_id, seats, amount,
                    payment_method, booking_date, snack_combo, coupon_code, discount)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    booking_id,
                    user_id,
                    movie_id,
                    show_id,
                    seat_str,
                    amount,
                    payment_method,
                    booking_date,
                    snack_combo,
                    coupon_code,
                    discount,
                ),
            )
            conn.commit()
            conn.close()
            return booking_id, "Booking confirmed!"
        except sqlite3.Error as exc:
            return None, f"Booking failed: {exc}"

    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Return booking history for a user with movie and show details."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, m.movie_name, s.theatre, s.timing, s.show_date
            FROM Bookings b
            JOIN Movies m ON b.movie_id = m.id
            JOIN Shows s ON b.show_id = s.id
            WHERE b.user_id = ?
            ORDER BY b.booking_date DESC
            """,
            (user_id,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Fetch a single booking with joined movie and show info."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, m.movie_name, m.duration, s.theatre, s.timing, s.show_date,
                   u.username, u.email
            FROM Bookings b
            JOIN Movies m ON b.movie_id = m.id
            JOIN Shows s ON b.show_id = s.id
            JOIN Users u ON b.user_id = u.id
            WHERE b.booking_id = ?
            """,
            (booking_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def cancel_booking(self, booking_id: str, user_id: int) -> Tuple[bool, str]:
        """Cancel a booking if it belongs to the user and is still confirmed."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM Bookings WHERE booking_id = ? AND user_id = ?",
            (booking_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Booking not found."
        if row["status"] == "cancelled":
            conn.close()
            return False, "Booking is already cancelled."
        cursor.execute(
            "UPDATE Bookings SET status = 'cancelled' WHERE booking_id = ?",
            (booking_id,),
        )
        conn.commit()
        conn.close()
        return True, "Booking cancelled successfully."

    def get_all_bookings(self) -> List[Dict]:
        """Return all bookings for admin view."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, m.movie_name, s.theatre, s.timing, s.show_date, u.username
            FROM Bookings b
            JOIN Movies m ON b.movie_id = m.id
            JOIN Shows s ON b.show_id = s.id
            JOIN Users u ON b.user_id = u.id
            ORDER BY b.booking_date DESC
            """
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    # --------------------------------------------------------------- Analytics
    def get_revenue(self) -> Dict[str, Any]:
        """Calculate total and method-wise revenue from confirmed bookings."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COALESCE(SUM(amount), 0) FROM Bookings WHERE status = 'confirmed'"""
        )
        total = cursor.fetchone()[0]
        cursor.execute(
            """SELECT payment_method, COALESCE(SUM(amount), 0) as total
               FROM Bookings WHERE status = 'confirmed'
               GROUP BY payment_method"""
        )
        by_method = {row["payment_method"]: row["total"] for row in cursor.fetchall()}
        conn.close()
        return {"total": total, "by_method": by_method}

    def get_occupancy(self) -> List[Dict]:
        """Calculate seat occupancy per show."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.id, m.movie_name, s.theatre, s.timing, s.show_date,
                   COUNT(b.booking_id) as booking_count,
                   GROUP_CONCAT(b.seats) as all_seats
            FROM Shows s
            JOIN Movies m ON s.movie_id = m.id
            LEFT JOIN Bookings b ON s.id = b.show_id AND b.status = 'confirmed'
            GROUP BY s.id
            ORDER BY s.show_date, s.timing
            """
        )
        results = []
        total_seats = 6 * 8
        for row in cursor.fetchall():
            data = dict(row)
            seats_booked = 0
            if data["all_seats"]:
                seats_booked = len(data["all_seats"].replace(",", "").split(","))
                seats_booked = len([s for s in data["all_seats"].split(",") if s])
            data["seats_booked"] = seats_booked
            data["total_seats"] = total_seats
            data["occupancy_percent"] = round((seats_booked / total_seats) * 100, 1)
            results.append(data)
        conn.close()
        return results

    # ------------------------------------------------------------- Favorites
    def toggle_favorite(self, user_id: int, movie_id: int) -> bool:
        """Add or remove a movie from user favorites. Returns True if now favorited."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM Favorites WHERE user_id = ? AND movie_id = ?",
            (user_id, movie_id),
        )
        exists = cursor.fetchone()
        if exists:
            cursor.execute(
                "DELETE FROM Favorites WHERE user_id = ? AND movie_id = ?",
                (user_id, movie_id),
            )
            conn.commit()
            conn.close()
            return False
        cursor.execute(
            "INSERT INTO Favorites (user_id, movie_id) VALUES (?, ?)",
            (user_id, movie_id),
        )
        conn.commit()
        conn.close()
        return True

    def get_favorites(self, user_id: int) -> List[int]:
        """Return list of favorite movie IDs for a user."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT movie_id FROM Favorites WHERE user_id = ?", (user_id,))
        ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ids

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        """Check whether a movie is in the user's favorites."""
        return movie_id in self.get_favorites(user_id)

    # --------------------------------------------------------------- Coupons
    def validate_coupon(self, code: str) -> Tuple[Optional[float], str]:
        """Validate coupon code and return discount percentage."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT discount_percent FROM Coupons WHERE code = ? AND is_active = 1",
            (code.strip().upper(),),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return row["discount_percent"], "Coupon applied!"
        return None, "Invalid or expired coupon."

    # ----------------------------------------------------------------- Snacks
    def get_snacks(self) -> List[Dict]:
        """Return available snack combos."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Snacks ORDER BY price")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
