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
    for y in range(h):
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
