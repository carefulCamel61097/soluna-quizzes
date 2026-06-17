#!/usr/bin/env python3
"""
map_card.py  IN.jpg  OUT.jpg

Birth/death-map reels show a white world-map card (grey continents, green=birth
/ red=death pins) in the lower part of the frame over the presenter. Find the
white card via the longest near-white run per row and crop to it. The spoken
answer caption sits ABOVE the card, so it's excluded automatically.
"""
import sys
from PIL import Image

YMIN_FRAC = 0.40
YMAX_FRAC = 0.92
MARGIN = 0.005


def is_map(r, g, b):
    # the map card is light + desaturated: white sea (~245) and grey land
    # (~200). Forest greens/browns are darker and more saturated.
    return min(r, g, b) > 162 and (max(r, g, b) - min(r, g, b)) < 46


def main(inp, outp):
    im = Image.open(inp).convert("RGB")
    px = im.load()
    w, h = im.size
    y0, y1 = int(h * YMIN_FRAC), int(h * YMAX_FRAC)
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(y0, y1):
        cnt = 0
        rxmin, rxmax = w, -1
        for x in range(w):
            if is_map(*px[x, y]):
                cnt += 1
                if x < rxmin: rxmin = x
                if x > rxmax: rxmax = x
        # whole map rows are mostly light; caption text rows are sparse
        if cnt > 0.45 * w:
            minx = min(minx, rxmin); maxx = max(maxx, rxmax)
            miny = min(miny, y);     maxy = max(maxy, y)

    if maxx < 0:
        print("No map card found in", inp); sys.exit(2)
    bw, bh = maxx - minx, maxy - miny
    m = int(max(bw, bh) * MARGIN)
    box = (max(0, minx - m), max(0, miny - m), min(w, maxx + m + 1), min(h, maxy + m + 1))
    im.crop(box).save(outp, quality=92)
    print(f"{inp} -> {outp}  card {bw}x{bh}px")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
