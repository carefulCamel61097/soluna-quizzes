#!/usr/bin/env python3
"""
de_card.py  IN.jpg  OUT.jpg

The German-federal-state reel shows a BLACK outline on a WHITE rounded card
(slightly rotated) over a forest background. Cropping the card itself catches
forest in the rotated corners, so instead we:
  1. locate the solid white card (longest near-white run per row),
  2. find the black outline strokes INSIDE that card,
  3. crop to the outline's bbox (+margin) from the original — background stays
     white because the outline sits well within the card.
"""
import sys
from PIL import Image

YMIN_FRAC = 0.15
MARGIN = 0.06


def near_white(r, g, b):
    return r > 225 and g > 225 and b > 225


def is_dark(r, g, b):
    return r < 110 and g < 110 and b < 110


def main(inp, outp):
    im = Image.open(inp).convert("RGB")
    px = im.load()
    w, h = im.size
    y0 = int(h * YMIN_FRAC)

    # 1. Find the card via the longest run of near-white pixels per row.
    cminx, cminy, cmaxx, cmaxy = w, h, -1, -1
    for y in range(y0, h):
        run = best = 0
        rs = bs = 0
        x = 0
        while x < w:
            if near_white(*px[x, y]):
                if run == 0:
                    rs = x
                run += 1
                if run > best:
                    best, bs = run, rs
            else:
                run = 0
            x += 1
        if best > 0.30 * w:                 # this row is part of the card
            be = bs + best
            cminx = min(cminx, bs); cmaxx = max(cmaxx, be)
            cminy = min(cminy, y);  cmaxy = max(cmaxy, y)

    if cmaxx < 0:
        print("No white card found in", inp)
        sys.exit(2)

    # 2. Black outline pixels inside the card region (inset to dodge rotated corners).
    ins = int(0.04 * (cmaxx - cminx))
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(cminy + ins, cmaxy - ins + 1):
        for x in range(cminx + ins, cmaxx - ins + 1):
            if is_dark(*px[x, y]):
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y

    if maxx < 0:
        print("No outline found in", inp)
        sys.exit(2)

    bw, bh = maxx - minx, maxy - miny
    m = int(max(bw, bh) * MARGIN)
    box = (max(0, minx - m), max(0, miny - m),
           min(w, maxx + m + 1), min(h, maxy + m + 1))
    im.crop(box).save(outp, quality=92)
    print(f"{inp} -> {outp}  outline {bw}x{bh}px")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
