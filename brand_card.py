#!/usr/bin/env python3
"""brand_card.py IN.jpg OUT.jpg [YMIN] [YMAX]

Brand-logo reels float a white/coloured logo card low-centre over the presenter.
The presenter's bright shirt is the largest non-forest blob, so we restrict the
search to a band BELOW the shirt hem (default y 0.63-0.95): there the logo card
is the dominant non-forest, non-skin, non-grey-shorts blob. Largest blob -> bbox.
"""
import sys
from collections import deque
from PIL import Image

SCALE = 2
MARGIN = 0.02


def is_bg(r, g, b):
    # forest green foliage
    if g >= r - 6 and g >= b - 4 and g > 60:
        return True
    # brown leaf litter / bare skin (legs)
    if r > 105 and r >= g - 4 and g >= b - 12 and (r - b) > 14:
        return True
    # deep shadow / soil
    if max(r, g, b) < 58:
        return True
    # grey shorts / dull bluish neutral
    if abs(r - g) < 24 and abs(g - b) < 24 and max(r, g, b) < 150:
        return True
    return False


def main(inp, outp, ymin=0.63, ymax=0.95):
    im = Image.open(inp).convert("RGB")
    W, H = im.size
    small = im.resize((W // SCALE, H // SCALE))
    px = small.load()
    w, h = small.size
    y0, y1 = int(h * ymin), int(h * ymax)
    mask = [[(not is_bg(*px[x, y])) for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]
    best_area, best_box = 0, None
    for sy in range(y0, y1):
        for sx in range(w):
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
                        if y0 <= ny < y1 and 0 <= nx < w and mask[ny][nx] and not seen[ny][nx]:
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
    ymin = float(a[3]) if len(a) > 3 else 0.63
    ymax = float(a[4]) if len(a) > 4 else 0.95
    main(a[1], a[2], ymin, ymax)
