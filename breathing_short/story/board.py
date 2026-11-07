#!/usr/bin/env python3
"""Storyboard from the user's own images: one or more images per narration line.

  python3 story/board.py   -> story/plates/<shot>_<n>.png (clean 16:9 crops) + story/storyboard.jpg

Each entry: (image index in uniq.txt, vertical anchor 0=top..1=bottom, side) where side is
None / "L" / "R" for half of a side-by-side image.
"""
import os, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.environ.get("UPLOADS", "/root/.claude/uploads/32770705-7d9b-5f9f-9b3a-9f911fd69f71/")
LIST = os.environ.get("UNIQ", "/tmp/claude-0/-home-user-Video/32770705-7d9b-5f9f-9b3a-9f911fd69f71/scratchpad/uniq.txt")
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT2 = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"

BOARD = [
    ("intro", "Why do you breathe faster when you run?", [(35, .4, None)]),
    ("muscles", "Every stride, your muscles burn through their energy, called ATP.", [(40, .5, None), (34, .5, None)]),
    ("mito", "To make more, mitochondria use oxygen, and release carbon dioxide.", [(45, .5, None), (44, .4, None)]),
    ("brain", "Your brain doesn't wait. From the very first step, it drives your diaphragm harder,",
     [(42, .4, None), (37, .5, None)]),
    ("diaphragm", "so you breathe deeper and faster: oxygen in, carbon dioxide out.", [(25, .5, None), (38, .5, None)]),
    ("heart", "Your heart races to deliver it all.", [(29, .45, None)]),
    ("buffer", "Sprint hard, and acid builds up. Your blood buffers it, releasing even more carbon dioxide, so you gasp.",
     [(21, .5, None), (36, .5, None), (31, 0.0, "L")]),
    ("lactate", "And no, lactic acid isn't the villain. Lactate is actually fuel.", [(26, .5, None), (43, .5, None)]),
    ("trained", "Train regularly, and the same pace feels easier.", [(59, .35, None)]),
]


def trim_borders(im):
    """Cuts white/black frame lines and strips of neighbouring panels off the edges."""
    a = np.asarray(im.convert("L"), float)
    def bad(v):
        return v.mean() > 225 or v.mean() < 12 and v.std() < 6
    t, b, l, r = 0, a.shape[0], 0, a.shape[1]
    for _ in range(2):   # a white line can hide a second strip of another panel behind it
        while t < b - 10 and bad(a[t, l:r]): t += 1
        while b > t + 10 and bad(a[b - 1, l:r]): b -= 1
        while l < r - 10 and bad(a[t:b, l]): l += 1
        while r > l + 10 and bad(a[t:b, r - 1]): r -= 1
        # thin strips (< 16 % of the size) cut off by a white line near an edge
        for y in range(t, t + int(0.16 * (b - t))):
            if a[y, l:r].mean() > 205: t = y + 1
        for y in range(b - 1, b - int(0.16 * (b - t)), -1):
            if a[y, l:r].mean() > 205: b = y
        for x in range(l, l + int(0.16 * (r - l))):
            if a[t:b, x].mean() > 205: l = x + 1
        for x in range(r - 1, r - int(0.16 * (r - l)), -1):
            if a[t:b, x].mean() > 205: r = x
    return im.crop((l, t, r, b))


def plate(entry, uniq):
    idx, anchor, side = entry
    im = Image.open(os.path.join(UP, uniq[idx])).convert("RGB")
    w, h = im.size
    if side:
        im = im.crop((0, 0, w // 2, h)) if side == "L" else im.crop((w // 2, 0, w, h))
    im = trim_borders(im)
    w, h = im.size
    th = w * 9 / 16
    if th <= h:
        t = (h - th) * anchor; im = im.crop((0, int(t), w, int(t + th)))
    else:
        tw = h * 16 / 9; l = (w - tw) / 2; im = im.crop((int(l), 0, int(l + tw), h))
    return im


def main():
    uniq = open(LIST).read().split()
    os.makedirs(os.path.join(HERE, "plates"), exist_ok=True)
    TW, TH, LW = 480, 270, 400
    rows = len(BOARD)
    W = Image.new("RGB", (LW + TW * 3 + 20, rows * (TH + 24) + 10), (18, 18, 22)); d = ImageDraw.Draw(W)
    F, F2 = ImageFont.truetype(FONT, 26), ImageFont.truetype(FONT2, 21)
    for r, (sid, text, ents) in enumerate(BOARD):
        y = r * (TH + 24) + 12
        d.text((14, y), f"{r + 1}. {sid.upper()}", font=F, fill=(255, 200, 60))
        d.multiline_text((14, y + 40), textwrap.fill(text, 30), font=F2, fill=(232, 232, 232), spacing=6)
        for c, e in enumerate(ents):
            p = plate(e, uniq)
            p.save(os.path.join(HERE, "plates", f"{sid}_{c}.png"))
            W.paste(p.resize((TW, TH), Image.LANCZOS), (LW + c * (TW + 6), y))
            d.text((LW + c * (TW + 6) + 8, y + 6), f"#{e[0]}", font=F2, fill=(255, 255, 255))
    W.save(os.path.join(HERE, "storyboard.jpg"), quality=90)
    print("storyboard", W.size)


if __name__ == "__main__":
    main()
