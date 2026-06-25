# CineBook - Movie Ticket Booking System

A complete, beginner-friendly **Movie Ticket Booking System** built with Python, Tkinter, and SQLite. Designed as a portfolio-ready desktop application with a modern dark UI, seat selection, payment simulation, QR ticket generation, and an admin panel.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)

## Features

### User Authentication
- Register & Login with validation
- Secure password hashing (SHA-256)
- Demo and admin accounts pre-seeded

### Movie Dashboard
- Movie cards with posters, genre, language, rating, duration, and price
- Search movies by name, genre, or language
- Filter by genre
- Sort by rating or price
- Favorite movies

### Booking Flow
- Multiple theatres and show timings
- Date selection
- **6×8 interactive seat layout**
  - Green = Available
  - Red = Booked
  - Blue = Selected
- Multi-seat booking (up to 10 seats)

### Payment Simulation
- UPI, Credit Card, and Cash
- Snack combo add-ons
- Discount coupon support (`CINEBOOK10`, `MOVIE20`, `WEEKEND15`)

### Ticket Generation
- Professional ticket design
- QR code for verification
- Save ticket to file

### Booking History
- View past bookings
- Cancel bookings
- Re-print tickets

### Admin Panel
- Add / Edit / Delete movies
- Add show timings
- View all bookings
- Revenue analytics
- Seat occupancy reports

## Project Structure

```
CineBook/
│
├── main.py              # Application entry point
├── database.py          # SQLite schema & data operations
├── login.py             # Login screen
├── register.py          # User registration
├── dashboard.py         # Movie browsing dashboard
├── booking.py           # Theatre & seat selection
├── payment.py           # Payment simulation
├── admin.py             # Admin management panel
├── ticket.py            # Ticket & booking history
├── ui.py                # Shared theme & UI components
├── generate_assets.py   # Poster/logo generator script
│
├── database/
│      cinebook.db       # Auto-created SQLite database
│
├── assets/
│      posters/          # Movie poster images
│      logo.png          # App logo
│
├── requirements.txt
└── README.md
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| Tkinter | Desktop GUI |
| SQLite | Local database |
| Pillow | Image handling & posters |
| qrcode | QR code on tickets |
| OOP | Modular class-based design |

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cinebook.git
cd CineBook

# Install dependencies
pip install -r requirements.txt

# Generate poster assets (optional — placeholders are auto-created at runtime)
python generate_assets.py

# Run the application
python main.py
```

## Default Login Credentials

| Role | Username | Password |
|---|---|---|
| Demo User | `demo` | `demo123` |
| Admin | `admin` | `admin123` |

## Usage Guide

1. **Login** with demo credentials or register a new account
2. **Browse movies** on the dashboard — search, filter, and sort
3. Click **Book Now** on any movie
4. Select **date**, **theatre**, and **show timing**
5. Pick seats on the **6×8 grid**
6. Choose **payment method**, optional **snacks**, and apply a **coupon**
7. View your **ticket** with QR code
8. Access **My Bookings** from the header to view history or cancel

### Admin Access
Login as `admin` to access the **Admin Panel** for movie management and analytics.

## Database Schema

| Table | Key Fields |
|---|---|
| Users | id, username, email, password, is_admin |
| Movies | id, movie_name, genre, duration, language, rating, price, poster |
| Shows | id, movie_id, theatre, timing, show_date |
| Bookings | booking_id, user_id, movie_id, show_id, seats, amount, payment_method |
| Favorites | user_id, movie_id |
| Coupons | code, discount_percent |
| Snacks | id, name, price |

## License

This project is open source and available for educational and portfolio use.
