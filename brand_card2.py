#!/usr/bin/env python3
"""brand_card2.py IN.jpg OUT.jpg x0 y0 x1 y1

Crop the logo card from a brand reel. The caller passes a rough window
(fractions of frame) that contains the card but excludes the presenter's
torso. Inside the window we take the largest connected blob of card-like
pixels (non forest / soil / grey-shorts / skin) and crop to its bbox.
Black-background cards (e.g. Guinness) crop to the bright emblem, which is
fine. Pure-red-on-grass logos (Atari) defeat the mask -> crop those by hand.
"""
import sys
from collections import deque
from PIL import Image

SCALE = 2
MARGIN = 0.04


def is_bg(r, g, b):
    if g >= r - 6 and g >= b - 4 and g > 60:                      # green foliage
        return True
    if r > 105 and r >= g - 4 and g >= b - 12 and (r - b) > 14:   # brown litter / skin
        return True
    if max(r, g, b) < 58:                                          # shadow / black
        return True
    if abs(r - g) < 24 and abs(g - b) < 24 and max(r, g, b) < 150: # grey shorts
        return True
    return False


def main(inp, outp, fx0, fy0, fx1, fy1):
    im = Image.open(inp).convert("RGB")
    W, H = im.size
    small = im.resize((W // SCALE, H // SCALE))
    px = small.load()
    w, h = small.size
    x0, x1 = int(w * fx0), int(w * fx1)
    y0, y1 = int(h * fy0), int(h * fy1)
    mask = [[False] * w for _ in range(h)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not is_bg(*px[x, y]):
                mask[y][x] = True
    seen = [[False] * w for _ in range(h)]
    best_area, best_box = 0, None
    for sy in range(y0, y1):
        for sx in range(x0, x1):
            if mask[sy][sx] and not seen[sy][sx]:
                q = deque([(sx, sy)]); seen[sy][sx] = True
                area = 0; bxmin = bxmax = sx; bymin = bymax = sy
                while q:
                    x, y = q.popleft(); area += 1
                    if x < bxmin: bxmin = x
                    if x > bxmax: bxmax = x
                    if y < bymin: bymin = y
                    if y > bymax: bymax = y
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if y0 <= ny < y1 and x0 <= nx < x1 and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True; q.append((nx, ny))
                if area > best_area:
                    best_area, best_box = area, (bxmin, bymin, bxmax, bymax)
    if not best_box:
        print("No card found in", inp); sys.exit(2)
    minx, miny, maxx, maxy = (v * SCALE for v in best_box)
    bw, bh = maxx - minx, maxy - miny
    m = int(max(bw, bh) * MARGIN)
    box = (max(0, minx - m), max(0, miny - m), min(W, maxx + m + 1), min(H, maxy + m + 1))
    im.crop(box).save(outp, quality=92)
    print(f"{outp}: {box}  ({box[2]-box[0]}x{box[3]-box[1]})")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]), float(a[4]), float(a[5]), float(a[6]))
