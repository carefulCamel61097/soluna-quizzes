#!/usr/bin/env python3
"""
isl_card.py  IN.jpg  OUT.jpg

The island reel floats a satellite card (island on an ocean background) over
the forest. The ocean wraps the island as a connected ring that reaches all
four card edges, so the bounding box of the LARGEST connected blue blob equals
the card. (Largest blob also rejects the presenter's blue shoes, which are a
separate, smaller blob.) Work at half-res for speed, then crop full-res.
"""
import sys
from collections import deque
from PIL import Image

YMIN_FRAC = 0.30
YMAX_FRAC = 0.88
MARGIN = 0.015
SCALE = 2  # downsample factor for the mask/labeling pass


def is_ocean(r, g, b):
    return b > 55 and b > r + 12 and b > g + 4 and r < 150


def main(inp, outp):
    im = Image.open(inp).convert("RGB")
    W, H = im.size
    small = im.resize((W // SCALE, H // SCALE))
    px = small.load()
    w, h = small.size
    y0, y1 = int(h * YMIN_FRAC), int(h * YMAX_FRAC)

    mask = [[False] * w for _ in range(h)]
    for y in range(y0, y1):
        for x in range(w):
            mask[y][x] = is_ocean(*px[x, y])

    seen = [[False] * w for _ in range(h)]
    best_area = 0
    best_box = None
    for sy in range(y0, y1):
        for sx in range(w):
            if mask[sy][sx] and not seen[sy][sx]:
                q = deque([(sx, sy)])
                seen[sy][sx] = True
                area = 0
                bxmin = bxmax = sx
                bymin = bymax = sy
                while q:
                    x, y = q.popleft()
                    area += 1
                    if x < bxmin: bxmin = x
                    if x > bxmax: bxmax = x
                    if y < bymin: bymin = y
                    if y > bymax: bymax = y
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if y0 <= ny < y1 and 0 <= nx < w and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((nx, ny))
                if area > best_area:
                    best_area = area
                    best_box = (bxmin, bymin, bxmax, bymax)

    if not best_box:
        print("No ocean/card found in", inp)
        sys.exit(2)

    minx, miny, maxx, maxy = (v * SCALE for v in best_box)
    bw, bh = maxx - minx, maxy - miny
    m = int(max(bw, bh) * MARGIN)
    box = (max(0, minx - m), max(0, miny - m), min(W, maxx + m + 1), min(H, maxy + m + 1))
    im.crop(box).save(outp, quality=92)
    print(f"{inp} -> {outp}  card {bw}x{bh}px  (area {best_area})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
