#!/usr/bin/env python3
"""montage_big.py COLS CELL OUT.jpg label1 img1 ...  -> large labelled grid"""
import sys
from PIL import Image, ImageDraw
cols = int(sys.argv[1]); CELL = int(sys.argv[2]); out = sys.argv[3]
rest = sys.argv[4:]
pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
rows = (len(pairs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CELL, rows * CELL), (30, 30, 30))
draw = ImageDraw.Draw(sheet)
for idx, (label, path) in enumerate(pairs):
    im = Image.open(path).convert("RGB")
    im.thumbnail((CELL - 16, CELL - 28))
    cx = (idx % cols) * CELL; cy = (idx // cols) * CELL
    ox = cx + (CELL - im.width) // 2; oy = cy + 24 + (CELL - 24 - im.height) // 2
    sheet.paste(im, (ox, oy))
    draw.text((cx + 6, cy + 4), label, fill=(255, 90, 90))
sheet.save(out, quality=90)
print("wrote", out, sheet.size)
