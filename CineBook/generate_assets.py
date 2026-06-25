"""Generate placeholder poster images and logo for CineBook."""

import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
POSTERS_DIR = os.path.join(BASE, "assets", "posters")
ASSETS_DIR = os.path.join(BASE, "assets")

COLORS = {
    "inception.jpg": "#1a1a2e",
    "interstellar.jpg": "#0f3460",
    "dark_knight.jpg": "#2c003e",
    "3_idiots.jpg": "#1b4332",
    "rrr.jpg": "#7f1d1d",
    "dune2.jpg": "#78350f",
}

os.makedirs(POSTERS_DIR, exist_ok=True)


def create_poster(filename: str, color: str, title: str) -> None:
    """Create a simple colored poster with movie title text."""
    img = Image.new("RGB", (300, 420), color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 180), title, fill="white", font=font)
    img.save(os.path.join(POSTERS_DIR, filename))


for fname, color in COLORS.items():
    title = fname.replace(".jpg", "").replace("_", " ").title()
    create_poster(fname, color, title)

logo = Image.new("RGB", (64, 64), "#e94560")
draw = ImageDraw.Draw(logo)
draw.ellipse([8, 8, 56, 56], fill="#0f0f1a")
draw.text((22, 20), "CB", fill="#e94560")
logo.save(os.path.join(ASSETS_DIR, "logo.png"))
print("Assets generated successfully.")
