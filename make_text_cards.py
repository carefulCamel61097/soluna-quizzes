#!/usr/bin/env python3
"""Generate clue cards for the text-only 'name the leader' quiz (#14)."""
import os
from PIL import Image, ImageDraw, ImageFont

BG = (22, 32, 46)
PANEL = (33, 44, 61)
WHITE = (238, 242, 247)
ACCENT = (111, 176, 255)
MUTED = (159, 176, 195)

W, H = 1000, 750
OUT = "docs/img/leaders"
os.makedirs(OUT, exist_ok=True)

CLUES = [
    ("King of France", "1715 – 1774"),
    ("President of the United States", "1801 – 1809"),
    ("King of England", "1509 – 1547"),
    ("Tsar of Russia", "1894 – 1917"),
    ("Emperor of Japan", "1867 – 1912"),
    ("President of Venezuela", "2002 – 2013"),
    ("President of Egypt", "1970 – 1981"),
    ("Ottoman Sultan", "1451 – 1481"),
    ("President of Germany", "1925 – 1934"),
    ("Emperor of Rome", "AD 17 – 37"),
]

def font(path, size):
    return ImageFont.truetype(path, size)

BOLD = "C:/Windows/Fonts/arialbd.ttf"
REG = "C:/Windows/Fonts/arial.ttf"

def centered(draw, cy, text, fnt, fill, w=W):
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((w - (r - l)) / 2 - l, cy - (b - t) / 2 - t), text, font=fnt, fill=fill)

for i, (role, dates) in enumerate(CLUES, 1):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # rounded panel
    d.rounded_rectangle([40, 40, W - 40, H - 40], radius=28, fill=PANEL)
    f_role = font(BOLD, 62 if len(role) < 22 else 50)
    f_dates = font(BOLD, 78)
    f_tag = font(REG, 30)
    centered(d, 250, "WHO RULED?", f_tag, MUTED)
    centered(d, 360, role, f_role, WHITE)
    centered(d, 480, dates, f_dates, ACCENT)
    im.save(f"{OUT}/{i:02d}.jpg", quality=92)
    print(f"{OUT}/{i:02d}.jpg  {role} ({dates})")
