#!/usr/bin/env python3
"""Render a two-line hook title as a transparent PNG to overlay on a vertical video.

    python3 make_hook.py "TOP LINE" "BOX LINE" Poppins-Bold.ttf hook.png
        [--width 1080] [--height 1920] [--color "#E83454"] [--y 0.22]

Top line: white with a dark outline. Bottom line: white text inside a rounded colour box.
A soft dark backdrop keeps both readable on busy footage. Text is used exactly as given
(no automatic upper-casing, which breaks Turkish İ/ı).
"""
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("top"); ap.add_argument("box"); ap.add_argument("font"); ap.add_argument("out")
ap.add_argument("--width", type=int, default=1080); ap.add_argument("--height", type=int, default=1920)
ap.add_argument("--color", default="#E83454")
ap.add_argument("--y", type=float, default=0.22, help="top of the hook as a fraction of height")
a = ap.parse_args()

W, H = a.width, a.height
sc = W / 1080
col = tuple(int(a.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
f1 = ImageFont.truetype(a.font, int(66 * sc)); f2 = ImageFont.truetype(a.font, int(118 * sc))
b2 = d.textbbox((0, 0), a.box, font=f2)
if b2[2] - b2[0] > W - 120 * sc:
    f2 = ImageFont.truetype(a.font, int(118 * sc * (W - 120 * sc) / (b2[2] - b2[0]))); b2 = d.textbbox((0, 0), a.box, font=f2)
b1 = d.textbbox((0, 0), a.top, font=f1)
if b1[2] - b1[0] > W - 80 * sc:
    f1 = ImageFont.truetype(a.font, int(66 * sc * (W - 80 * sc) / (b1[2] - b1[0]))); b1 = d.textbbox((0, 0), a.top, font=f1)
y1 = int(H * a.y); y2 = y1 + (b1[3] - b1[1]) + int(40 * sc); h2 = b2[3] - b2[1]

back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(back).rounded_rectangle([20, y1 - 50 * sc, W - 20, y2 + h2 + 60 * sc], radius=int(40 * sc), fill=(0, 0, 0, 140))
im = Image.alpha_composite(im, back.filter(ImageFilter.GaussianBlur(int(28 * sc)))); d = ImageDraw.Draw(im)

x = (W - (b1[2] - b1[0])) // 2
d.text((x - b1[0], y1 - b1[1]), a.top, font=f1, fill="white", stroke_width=max(2, int(4 * sc)), stroke_fill="black")
w2 = b2[2] - b2[0]; x = (W - w2) // 2; px, py = int(32 * sc), int(16 * sc)
d.rounded_rectangle([x - px, y2 - py, x + w2 + px, y2 + h2 + py + int(6 * sc)], radius=int(24 * sc), fill=col)
d.text((x - b2[0], y2 - b2[1]), a.box, font=f2, fill="white")
im.save(a.out)
print("hook ->", a.out)
