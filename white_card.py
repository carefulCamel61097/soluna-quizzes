#!/usr/bin/env python3
"""Crop the white question card from a language-reel frame.

The phrase ("what language is this?" in the target language) sits on a bright
white rectangle over the presenter. We threshold near-white pixels, take the
largest connected white blob, and crop to its bounding box (small margin).

Usage: python white_card.py IN.jpg OUT.jpg
"""
import sys
from collections import deque
from PIL import Image

def main(src, dst):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    px = im.load()
    # half-res mask for speed
    s = 2
    mw, mh = W // s, H // s
    white = [[False] * mw for _ in range(mh)]
    for y in range(mh):
        for x in range(mw):
            r, g, b = px[x * s, y * s]
            if r > 225 and g > 225 and b > 225:
                white[y][x] = True
    # largest connected white blob (4-connectivity BFS)
    seen = [[False] * mw for _ in range(mh)]
    best = None
    best_area = 0
    for y0 in range(mh):
        for x0 in range(mw):
            if white[y0][x0] and not seen[y0][x0]:
                q = deque([(x0, y0)])
                seen[y0][x0] = True
                minx = maxx = x0
                miny = maxy = y0
                area = 0
                while q:
                    x, y = q.popleft()
                    area += 1
                    if x < minx: minx = x
                    if x > maxx: maxx = x
                    if y < miny: miny = y
                    if y > maxy: maxy = y
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < mw and 0 <= ny < mh and white[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((nx, ny))
                if area > best_area:
                    best_area = area
                    best = (minx, miny, maxx, maxy)
    if not best:
        print("no white card found in", src)
        sys.exit(1)
    minx, miny, maxx, maxy = [v * s for v in best]
    m = 6
    box = (max(0, minx - m), max(0, miny - m), min(W, maxx + m), min(H, maxy + m))
    im.crop(box).save(dst, quality=92)
    print(f"{dst}: {box}  ({box[2]-box[0]}x{box[3]-box[1]})")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
