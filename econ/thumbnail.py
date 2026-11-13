#!/usr/bin/env python3
"""YouTube thumbnails (1280x720) for a chapter video, in The VisualMind style.

python3 thumbnail.py out/thumbs        (run from econ/) -> Ch01 thumbnail A/B/C .png
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFilter
import render_econ as E
from render_econ import F, put, glow_text, txt

TW, TH = 1280, 720
NAVY0, NAVY1 = (6, 10, 26), (24, 38, 84)
GOLD, WHITE, RED, GREEN, ACC = (255, 209, 102), (245, 248, 255), (235, 50, 50), (70, 210, 140), (120, 200, 255)


def bg(accent=(40, 70, 160)):
    im = Image.new("RGB", (TW, TH), NAVY0)
    g = Image.new("RGB", (TW, TH), NAVY0); d = ImageDraw.Draw(g)
    for r in range(900, 0, -12):
        u = r / 900
        col = tuple(int(NAVY1[i] * (1 - u) + NAVY0[i] * u) for i in range(3))
        d.ellipse((TW * 0.62 - r, TH * 0.5 - r, TW * 0.62 + r, TH * 0.5 + r), fill=col)
    im = g.filter(ImageFilter.GaussianBlur(30))
    d = ImageDraw.Draw(im, "RGBA")
    for k in range(9):                                   # light streaks
        x = -200 + k * 190
        d.polygon([(x, 0), (x + 40, 0), (x - 260, TH), (x - 300, TH)], fill=accent + (18,))
    return im


def logo(im, size=150, pos=None):
    lg = Image.open(os.path.join(E.HERE, "assets/visualmind_logo.png")).convert("RGBA").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((2, 2, size - 2, size - 2), fill=255); lg.putalpha(m)
    x, y = pos or (TW - size - 24, TH - size - 24)
    ring = Image.new("RGBA", (size + 16, size + 16), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, size + 15, size + 15), fill=GOLD + (255,))
    im.paste(ring, (x - 8, y - 8), ring); im.paste(lg, (x, y), lg)


def outline_text(im, xy, s, font, fill, stroke=8, scol=(0, 0, 0), anchor="la"):
    d = ImageDraw.Draw(im)
    d.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=scol)


def badge(im, xy, s, fill, fg=(20, 14, 0), size=40, pad=(22, 10)):
    d = ImageDraw.Draw(im, "RGBA"); f = F("InterDisplay-Black", size)
    w = f.getlength(s) + 2 * pad[0]; h = size * 1.25 + 2 * pad[1]
    x, y = xy
    d.rounded_rectangle((x, y, x + w, y + h), radius=int(h / 2), fill=fill + (255,))
    d.text((x + w / 2, y + h / 2), s, font=f, fill=fg, anchor="mm")
    return w


def version_a():
    """Riya's choice: ₹100 and three options."""
    im = bg()
    badge(im, (40, 34), "RAMESH SINGH · CHAPTER 1", GOLD, size=30)
    outline_text(im, (40, 120), "₹100 mein", F("InterDisplay-Black", 96), WHITE)
    outline_text(im, (40, 232), "sirf EK?", F("InterDisplay-Black", 118), GOLD)
    outline_text(im, (44, 400), "Introduction to", F("InterDisplay-Black", 54), WHITE, stroke=6)
    outline_text(im, (44, 462), "ECONOMICS", F("InterDisplay-Black", 92), ACC, stroke=8)
    put(im, "🍕", (760, 250), 170); put(im, "🎬", (960, 200), 150); put(im, "📖", (1140, 260), 150)
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((815, 360, 1015, 560), fill=(0, 0, 0, 90))
    put(im, "🤔", (915, 460), 190)
    badge(im, (40, 610), "HINGLISH · FULL CLASS", RED, fg=WHITE, size=30)
    logo(im, 150)
    return im


def version_b():
    """The big question: who decides — market or government?"""
    im = bg((160, 60, 40))
    badge(im, (40, 34), "CHAPTER 1 · RAMESH SINGH 18e", GOLD, size=30)
    outline_text(im, (40, 118), "Market", F("InterDisplay-Black", 110), GREEN)
    outline_text(im, (40, 238), "ya", F("InterDisplay-Black", 70), WHITE, stroke=6)
    outline_text(im, (150, 226), "Government?", F("InterDisplay-Black", 110), GOLD)
    outline_text(im, (44, 400), "Capitalist · Socialist · Mixed", F("InterDisplay-Black", 46), WHITE, stroke=6)
    outline_text(im, (44, 470), "Introduction to ECONOMICS", F("InterDisplay-Black", 56), ACC, stroke=7)
    put(im, "🏪", (930, 470), 170); put(im, "⚖️", (1060, 300), 150); put(im, "🏛️", (1150, 470), 160)
    badge(im, (40, 610), "FULL CLASS · HINGLISH", RED, fg=WHITE, size=30)
    logo(im, 140, (TW - 140 - 24, 24))
    return im


def version_c():
    """The whole book map: 22 chapters, chapter 1 starts now."""
    im = bg((60, 120, 200))
    badge(im, (40, 34), "RAMESH SINGH · INDIAN ECONOMY 18e", GOLD, size=28)
    outline_text(im, (40, 112), "22 Chapters", F("InterDisplay-Black", 100), WHITE)
    outline_text(im, (40, 222), "22 Classes", F("InterDisplay-Black", 100), GOLD)
    outline_text(im, (44, 360), "Shuru — Chapter 1", F("InterDisplay-Black", 64), ACC, stroke=7)
    outline_text(im, (44, 440), "Introduction to Economics", F("InterDisplay-Black", 52), WHITE, stroke=6)
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy = 980, 330
    for i in range(22):                                   # mini mind map
        a = math.radians(-90 + 360 * i / 22); x, y = cx + 220 * math.cos(a), cy + 200 * math.sin(a)
        d.line([(cx, cy), (x, y)], fill=ACC + (150,), width=3)
        col = GOLD if i == 0 else (30, 44, 90)
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=col + (255,), outline=ACC + (255,), width=2)
        txt(im, (x, y), str(i + 1), F("InterDisplay-Black", 20), (20, 14, 0) if i == 0 else WHITE, anchor="mm")
    d.rounded_rectangle((cx - 95, cy - 45, cx + 95, cy + 45), radius=30, fill=(20, 29, 58, 255), outline=GOLD + (255,), width=3)
    txt(im, (cx + 18, cy), "Economy", F("InterDisplay-Black", 30), WHITE, anchor="mm")
    put(im, "📘", (cx - 62, cy), 34)
    badge(im, (40, 610), "FULL CLASS · HINGLISH", RED, fg=WHITE, size=30)
    logo(im, 140)
    return im


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/thumbs"
    os.makedirs(out, exist_ok=True)
    for tag, fn in (("A", version_a), ("B", version_b), ("C", version_c)):
        p = os.path.join(out, f"Ch01 - Introduction to Economics - thumbnail {tag}.png")
        fn().save(p, optimize=True); print("wrote", p)


# ------------------------------------------------------------------ Chapter 2
def ch02_a():
    """₹20 + ₹50 + ₹100 = ₹170? The double-counting puzzle."""
    im = bg()
    badge(im, (40, 34), "RAMESH SINGH · CHAPTER 2", GOLD, size=30)
    outline_text(im, (40, 118), "₹20 + ₹50 + ₹100", F("InterDisplay-Black", 82), WHITE)
    outline_text(im, (40, 222), "= ₹170?", F("InterDisplay-Black", 104), GOLD)
    put(im, "❌", (560, 290), 96)
    outline_text(im, (44, 400), "GDP kaise ginte hain?", F("InterDisplay-Black", 56), WHITE, stroke=6)
    outline_text(im, (44, 470), "NATIONAL INCOME", F("InterDisplay-Black", 80), ACC, stroke=8)
    put(im, "🌾", (800, 230), 140); put(im, "🏭", (960, 230), 140); put(im, "🍕", (1120, 230), 150)
    put(im, "🧮", (1060, 420), 150)
    badge(im, (40, 610), "HINGLISH · FULL CLASS", RED, fg=WHITE, size=30)
    logo(im, 150)
    return im


def ch02_b():
    """GDP, GNP, NNP — the family."""
    im = bg((60, 120, 200))
    badge(im, (40, 34), "CHAPTER 2 · RAMESH SINGH 18e", GOLD, size=30)
    outline_text(im, (40, 118), "GDP · GNP · NNP", F("InterDisplay-Black", 100), GOLD)
    outline_text(im, (40, 250), "Ek pizza se", F("InterDisplay-Black", 76), WHITE)
    outline_text(im, (40, 340), "poori National Income!", F("InterDisplay-Black", 64), ACC, stroke=7)
    put(im, "🍕", (980, 330), 260)
    badge(im, (40, 610), "FULL CLASS · HINGLISH", RED, fg=WHITE, size=30)
    logo(im, 140, (TW - 140 - 24, 24))
    return im
