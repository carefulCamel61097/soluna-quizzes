import sys
from PIL import Image, ImageDraw
inp, outp = sys.argv[1], sys.argv[2]
im = Image.open(inp).convert("RGB")
w, h = im.size
d = ImageDraw.Draw(im)
for i in range(1, 10):
    x = w * i // 10
    d.line([(x, 0), (x, h)], fill=(255, 0, 0), width=2)
    d.text((x + 2, 2), f"{i*10}", fill=(255, 255, 0))
for i in range(1, 20):
    y = h * i // 20
    d.line([(0, y), (w, y)], fill=(255, 0, 0), width=1)
    d.text((2, y + 1), f"{i*5}", fill=(0, 255, 255))
im.save(outp, quality=90)
