#!/usr/bin/env python3
"""
card_detect.py  IN.jpg  OUT.jpg

History reels (portraits, artifacts) float a framed image card over the
full-height presenter in a forest. The card is the largest connected region of
NON-forest pixels in the lower band (forest = green foliage / brown leaf litter
/ dark soil). Crop to that blob's bbox. Half-res labeling for speed.
"""
import sys
from collections import deque
from PIL import Image

YMIN_FRAC = 0.50
YMAX_FRAC = 0.97
MARGIN = 0.012
SCALE = 2


def is_forest(r, g, b):
    if g >= r - 6 and g >= b - 4 and g > 60:          # green foliage / teal kit
        return True
    if r > 105 and r >= g - 4 and g >= b - 12 and (r - b) > 14:  # brown leaf litter
        return True
    if max(r, g, b) < 58:                              # deep shadow / soil
        return True
    # dark neutral / bluish clothing (presenter's navy jersey, grey shorts)
    if b >= r - 6 and abs(r - g) < 28 and max(r, g, b) < 135:
        return True
    return False


def main(inp, outp):
    im = Image.open(inp).convert("RGB")
    W, H = im.size
    small = im.resize((W // SCALE, H // SCALE))
    px = small.load()
    w, h = small.size
    y0, y1 = int(h * YMIN_FRAC), int(h * YMAX_FRAC)

    mask = [[(not is_forest(*px[x, y])) for x in range(w)] for y in range(h)]
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
    print(f"{inp} -> {outp}  card {bw}x{bh}px (area {best_area})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
