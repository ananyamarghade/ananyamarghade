#!/usr/bin/env python3
"""One-off: turns the original ASCII-art image into theme-coloured transparent PNGs in data/.

Needs Pillow + numpy (NOT needed for the normal build):
    python3 scripts/make_portrait.py path/to/ascii-art.png
Writes data/portrait-{dark,light}.png (base) and portrait-{dark,light}-hl.png (highlight pass).
"""
import pathlib
import sys

import numpy as np
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else "ascii-art.png"
out = pathlib.Path(__file__).resolve().parent.parent / "data"
im = Image.open(src).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
bg.alpha_composite(im)
g = np.array(bg.convert("L").crop((26, 0, 780, 800))).astype(float)   # crop the '=' border and dotted floor
ink = np.clip((255 - g) / 255 * 1.6, 0, 1)
h, w = ink.shape
s = 0.75
ink = np.array(Image.fromarray((ink * 255).astype("uint8")).resize((int(w * s), int(h * s)), Image.LANCZOS)) / 255.0
alpha = (np.round(ink * 11) / 11 * 255).astype("uint8")                # 12 alpha levels keeps the PNG small
H, W = alpha.shape
themes = {"dark": ((0xe8, 0xe6, 0xdf), (0x4f, 0xd1, 0xc5), (0xb8, 0xe6, 0x3c)),
          "light": ((0x14, 0x18, 0x1b), (0x0f, 0x76, 0x6e), (0x4d, 0x7c, 0x0f))}
for name, (top, bot, hl) in themes.items():
    t = np.clip((np.linspace(0, 1, H) - 0.55) / 0.45, 0, 1)[:, None, None]
    rgb = (np.array(top) * (1 - t) + np.array(bot) * t).astype("uint8")
    rgb = np.broadcast_to(rgb, (H, W, 3))
    base = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    base.save(out / f"portrait-{name}.png", optimize=True)
    hlimg = Image.fromarray(np.dstack([np.broadcast_to(np.array(hl, dtype="uint8"), (H, W, 3)), alpha]), "RGBA")
    hlimg.save(out / f"portrait-{name}-hl.png", optimize=True)
print("wrote", sorted(p.name for p in out.glob("portrait-*.png")), (W, H))
