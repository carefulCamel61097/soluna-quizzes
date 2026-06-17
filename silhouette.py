#!/usr/bin/env python3
"""
silhouette.py  IN.jpg  OUT.jpg

Isolate the bright-green country outline from a solunaaaa16 "name the outline"
frame and render it as a clean filled silhouette on a plain background,
tightly cropped to the shape.
"""
import sys
from PIL import Image

FILL = (46, 170, 70)      # green shape colour on output
BG = (245, 247, 250)      # near-white background
MARGIN = 0.08             # padding around the shape, fraction of max dimension
YMIN_FRAC = 0.52          # ignore green above this fraction of height
                          # (some reels render the answer caption in green, up top)


def is_green(r, g, b):
    # The overlay outline is a pure saturated green (~14,193,5);
    # forest foliage is muted (G~114, R~97), so this excludes it.
    return g > 150 and r < 80 and b < 80


def main(inp, outp):
    im = Image.open(inp).convert("RGB")
    px = im.load()
    w, h = im.size

    minx, miny, maxx, maxy = w, h, -1, -1
    mask = Image.new("1", (w, h), 0)
    mpx = mask.load()
    y0 = int(h * YMIN_FRAC)
    for y in range(y0, h):
        for x in range(w):
            r, g, b = px[x, y]
            if is_green(r, g, b):
                mpx[x, y] = 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y

    if maxx < 0:
        print("No green outline found in", inp)
        sys.exit(2)

    # Strip a green answer-caption band: some reels render the answer text in
    # the same green, sitting ABOVE the shape with a clear empty gap between.
    # Walk rows from the top of the green bbox; if the first green cluster is
    # followed by a gap and holds far fewer pixels than what's below, it's text.
    row_count = [0] * (maxy + 1)
    for y in range(miny, maxy + 1):
        c = 0
        for x in range(minx, maxx + 1):
            if mpx[x, y]:
                c += 1
        row_count[y] = c
    empty = max(1, int(0.008 * w))      # a row this sparse counts as "blank"
    gap_need = max(3, int(0.03 * h))     # blank run this long = a real gap
    y = miny
    while y <= maxy and row_count[y] <= empty:
        y += 1
    top_start = y
    while y <= maxy and row_count[y] > empty:
        y += 1
    top_end = y                          # first blank row after the top cluster
    blank = y
    while blank <= maxy and row_count[blank] <= empty:
        blank += 1
    if (blank - top_end) >= gap_need and blank <= maxy:
        above = sum(row_count[top_start:top_end])
        below = sum(row_count[blank:maxy + 1])
        if above < 0.35 * below:         # top cluster is a thin caption, not the shape
            miny = blank
            minx, maxx = w, -1
            for yy in range(miny, maxy + 1):
                for xx in range(w):
                    if mpx[xx, yy]:
                        if xx < minx: minx = xx
                        if xx > maxx: maxx = xx

    out = Image.new("RGB", (w, h), BG)
    opx = out.load()
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            if mpx[x, y]:
                opx[x, y] = FILL

    bw, bh = maxx - minx, maxy - miny
    m = int(max(bw, bh) * MARGIN)
    box = (max(0, minx - m), max(0, miny - m),
           min(w, maxx + m + 1), min(h, maxy + m + 1))
    out.crop(box).save(outp, quality=92)
    print(f"{inp} -> {outp}  shape {bw}x{bh}px")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
