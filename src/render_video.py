"""Render "The Jacket Must Go On" — a 5-character cartoon parody — to MP4.

Usage:  python3 render_video.py [output.mp4]
Needs:  Pillow, numpy, ffmpeg on PATH.
"""
import math
import os
import random
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import characters as C
from audio import Track

W, H, FPS = 1280, 720, 24
GROUND = 665
FD = "/usr/share/fonts/opentype/inter/"
OL = C.OL


@lru_cache(maxsize=64)
def font(name, size):
    return ImageFont.truetype(FD + name, size)


def clamp(u, a=0.0, b=1.0):
    return max(a, min(b, u))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * ease(u)


def line_dur(text):
    return max(2.3, 1.4 + 0.058 * len(text))


def talk_dur(text, dur):
    return min(dur - 0.45, 0.3 + 0.055 * len(text))


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def ctext(d, xy, text, f, fill, stroke=0, sfill=(0, 0, 0)):
    d.text(xy, text, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)


def vgrad(w, h, top, bottom):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        u = y / max(1, h - 1)
        d.line((0, y, w, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * u) for i in range(3)))
    return im


# ------------------------------------------------------------------ backgrounds
@lru_cache(maxsize=None)
def bg_backstage():
    im = vgrad(W, H, (55, 22, 45), (25, 10, 22))
    d = ImageDraw.Draw(im)
    for y in range(GROUND - 40, H, 22):                       # wooden floor
        d.rectangle((0, y, W, y + 22), fill=(118, 76, 44) if (y // 22) % 2 else (105, 66, 38))
        d.line((0, y, W, y), fill=(70, 42, 22), width=2)
    for side in (0, 1):                                        # curtains
        x0 = 0 if side == 0 else W - 170
        for i in range(0, 170, 28):
            d.rectangle((x0 + i, 0, x0 + i + 28, GROUND - 40), fill=(160, 22, 34))
            d.rectangle((x0 + i + 18, 0, x0 + i + 28, GROUND - 40), fill=(115, 12, 22))
    for x in range(0, W, 80):                                  # valance
        d.chord((x - 10, -40, x + 90, 60), 0, 180, fill=(140, 16, 28), outline=(90, 8, 16))
    # clothing rack with an EMPTY hanger
    d.line((200, 250, 200, GROUND - 40), fill=(170, 170, 180), width=6)
    d.line((330, 250, 330, GROUND - 40), fill=(170, 170, 180), width=6)
    d.line((190, 250, 340, 250), fill=(190, 190, 200), width=8)
    d.arc((245, 250, 285, 280), 180, 360, fill=(200, 200, 210), width=4)
    d.polygon([(265, 262), (225, 300), (305, 300)], outline=(200, 200, 210))
    d.rounded_rectangle((222, 310, 308, 340), 6, fill=(250, 240, 200), outline=OL, width=2)
    ctext(d, (265, 325), "JACKET", font("Inter-Bold.otf", 18), (60, 40, 20))
    # road cases
    for (x, y, w, h) in ((860, 520, 170, 105), (890, 440, 120, 80)):
        d.rectangle((x, y, x + w, y + h), fill=(30, 30, 34), outline=(150, 150, 160), width=3)
        for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
            d.rectangle((cx - 7, cy - 7, cx + 7, cy + 7), fill=(190, 190, 200))
    ctext(d, (945, 572), "KEYNOTE GEAR", font("Inter-Bold.otf", 16), (230, 230, 230))
    d.rounded_rectangle((640, 210, 840, 260), 8, fill=(30, 30, 30), outline=(240, 200, 60), width=3)
    ctext(d, (740, 235), "STAGE  >>>", font("Inter-Black.otf", 26), (240, 200, 60))
    return im


def _street(lit):
    sw = W * 3
    im = vgrad(sw, H, (10, 14, 40), (40, 30, 70))
    d = ImageDraw.Draw(im)
    rng = random.Random(11)
    for _ in range(220):
        x, y = rng.randrange(sw), rng.randrange(0, 380)
        d.point((x, y), fill=(255, 255, 230))
    for x in range(0, sw, W):                                   # a moon on each tile
        d.ellipse((x + 980, 60, x + 1080, 160), fill=(250, 245, 210))
        d.ellipse((x + 1010, 60, x + 1100, 150), fill=(30, 26, 60))
    x = 0
    rng = random.Random(4)
    while x < sw:
        bw, bh = rng.randrange(90, 200), rng.randrange(180, 460)
        top = GROUND - 30 - bh
        d.rectangle((x, top, x + bw, GROUND - 30), fill=(28, 28, 52), outline=(15, 15, 30))
        for wy in range(top + 18, GROUND - 50, 30):
            for wx in range(x + 14, x + bw - 18, 26):
                on = lit and rng.random() < 0.6
                d.rectangle((wx, wy, wx + 12, wy + 16), fill=(255, 215, 110) if on else (45, 45, 70))
        x += bw + rng.randrange(6, 30)
    d.rectangle((0, GROUND - 30, sw, GROUND + 10), fill=(90, 90, 100))
    d.rectangle((0, GROUND + 10, sw, H), fill=(45, 45, 52))
    return im


@lru_cache(maxsize=None)
def bg_street(lit=True):
    return _street(lit)


@lru_cache(maxsize=None)
def bg_diner():
    im = Image.new("RGB", (W, H), (150, 212, 198))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 430, W, 510), fill=(185, 40, 52))
    d.line((0, 430, W, 430), fill=(240, 240, 240), width=8)
    sq = 60
    for y in range(510, H, sq):
        for x in range(0, W, sq):
            d.rectangle((x, y, x + sq, y + sq), fill=(245, 245, 240) if ((x + y) // sq) % 2 else (30, 30, 35))
    # window with night view
    d.rectangle((60, 110, 500, 390), fill=(20, 26, 60), outline=(210, 210, 215), width=12)
    for bx, bh in ((80, 120), (150, 190), (240, 90), (310, 160), (400, 130)):
        d.rectangle((bx, 380 - bh, bx + 60, 380), fill=(35, 35, 70))
    d.line((280, 110, 280, 390), fill=(210, 210, 215), width=8)
    d.ellipse((410, 135, 460, 185), fill=(250, 245, 210))
    # neon sign with glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    ctext(gd, (840, 120), "DANNY'S DINER", font("Inter-Black.otf", 66), (255, 80, 170, 255))
    ctext(gd, (840, 185), "OPEN 24/7  -  COFFEE  -  BIG IDEAS", font("Inter-Bold.otf", 24), (120, 240, 255, 255))
    im.paste(glow.filter(ImageFilter.GaussianBlur(9)), (0, 0), glow.filter(ImageFilter.GaussianBlur(9)))
    im.paste(glow, (0, 0), glow)
    # plaque above the booth
    d.rounded_rectangle((900, 250, 1230, 320), 8, fill=(205, 165, 70), outline=(110, 80, 20), width=4)
    ctext(d, (1065, 272), "BOOTH #3", font("Inter-Black.otf", 22), (60, 40, 10))
    ctext(d, (1065, 300), "where it all began - 1993", font("Inter-Bold.otf", 18), (60, 40, 10))
    # booth back
    d.rounded_rectangle((880, 340, 1260, 600), 30, fill=(200, 35, 45), outline=OL, width=5)
    for x in range(920, 1240, 60):
        d.line((x, 360, x, 590), fill=(160, 20, 30), width=4)
    # wall clock
    d.ellipse((570, 260, 650, 340), fill=(255, 255, 255), outline=OL, width=5)
    d.line((610, 300, 610, 272), fill=OL, width=4)
    d.line((610, 300, 632, 308), fill=OL, width=4)
    return im


def diner_table(img, d):
    d.rectangle((1050, 490, 1080, GROUND), fill=(150, 150, 160), outline=OL, width=3)
    d.rounded_rectangle((880, 470, 1250, 498), 8, fill=(240, 240, 235), outline=OL, width=4)
    d.rectangle((1150, 430, 1190, 470), fill=(255, 255, 255), outline=OL, width=3)    # coffee mug
    d.arc((1180, 438, 1204, 462), 270, 90, fill=OL, width=4)
    for k in range(2):
        d.arc((1155 + k * 14, 395, 1175 + k * 14, 428), 100, 260, fill=(200, 200, 200), width=3)


@lru_cache(maxsize=None)
def bg_stage():
    im = vgrad(W, H, (8, 8, 18), (20, 20, 35))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 560, W, H), fill=(32, 32, 40))
    d.line((0, 560, W, 560), fill=(118, 185, 0), width=6)
    d.rounded_rectangle((140, 30, 1140, 400), 16, fill=(5, 5, 8), outline=(70, 70, 80), width=6)
    return im


def stage_screen(img, d, mode):
    scr = vgrad(980, 350, (10, 40, 10), (0, 0, 0))
    sd = ImageDraw.Draw(scr)
    if mode == 0:
        ctext(sd, (490, 140), "KEYNOTE 2026", font("Inter-Black.otf", 96), (118, 185, 0))
        ctext(sd, (490, 240), "ACCELERATED  EVERYTHING", font("Inter-Bold.otf", 36), (220, 220, 220))
    elif mode == 1:
        ctext(sd, (490, 175), "THE MORE YOU BUY,", font("Inter-Black.otf", 62), (255, 255, 255))
        ctext(sd, (490, 260), "THE MORE YOU SAVE", font("Inter-Black.otf", 62), (118, 185, 0))
    else:
        pts = [(60, 300), (200, 270), (300, 285), (430, 220), (560, 240), (700, 140), (900, 40)]
        sd.line(pts, fill=(118, 185, 0), width=10)
        sd.polygon([(900, 20), (930, 70), (870, 60)], fill=(118, 185, 0))
        ctext(sd, (300, 70), "STOCK: +8%", font("Inter-Black.otf", 58), (255, 255, 255))
    img.paste(scr, (150, 40))


# ------------------------------------------------------------------ drawing helpers
def paste_sprite(img, name, x, s, talk, blink, yoff=0, angle=0, **flags):
    sp = C.sprite(name, s, talk, blink, **flags)
    ax, ay = C.ANCHOR[0] * s, C.ANCHOR[1] * s
    if angle:
        side = int(2 * C.CH * s)
        big = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        big.paste(sp, (int(side / 2 - ax), int(side / 2 - ay)), sp)
        big = big.rotate(angle, resample=Image.BICUBIC)
        py = GROUND + yoff - 40 * s * abs(math.sin(math.radians(angle)))
        img.paste(big, (int(x - side / 2), int(py - side / 2)), big)
    else:
        img.paste(sp, (int(x - ax), int(GROUND + yoff - ay)), sp)


def head_pos(name, x, s, yoff=0):
    return x, GROUND + yoff - (C.ANCHOR[1] - C.HEAD_TOP[name]) * s


def bubble(img, who, text, hx, hy):
    d = ImageDraw.Draw(img)
    f = font("Inter-Bold.otf", 30)
    lines = wrap(text, f, 520)
    lh = 38
    tw = max(f.getlength(l) for l in lines)
    bw, bh = tw + 50, len(lines) * lh + 38
    bx = clamp(hx - bw / 2, 20, W - 20 - bw)
    by = max(30, hy - 45 - bh)
    base = clamp(hx, bx + 40, bx + bw - 40)
    tip = (hx, min(hy - 6, by + bh + 40))
    d.rounded_rectangle((bx + 6, by + 6, bx + bw + 6, by + bh + 6), 24, fill=(0, 0, 0))
    d.polygon([(base - 20, by + bh - 6), (base + 20, by + bh - 6), tip], fill=(255, 255, 255), outline=OL)
    d.line([(base - 20, by + bh - 6), tip, (base + 20, by + bh - 6)], fill=OL, width=4)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 24, fill=(255, 255, 255), outline=OL, width=4)
    d.polygon([(base - 17, by + bh - 8), (base + 17, by + bh - 8), (tip[0] * .2 + base * .8, by + bh + 6)],
              fill=(255, 255, 255))
    for i, l in enumerate(lines):
        d.text((bx + 25, by + 20 + i * lh), l, font=f, fill=(20, 20, 25))
    info = C.INFO[who]
    nf = font("Inter-Black.otf", 18)
    nw = nf.getlength(info["name"]) + 24
    d.rounded_rectangle((bx + 18, by - 16, bx + 18 + nw, by + 14), 10, fill=info["color"], outline=OL, width=3)
    d.text((bx + 30, by - 11), info["name"], font=nf, fill=(255, 255, 255), stroke_width=2, stroke_fill=OL)


def note_card(img, text):
    d = ImageDraw.Draw(img)
    d.rectangle((388, 78, 900, 320), fill=(0, 0, 0))
    d.rectangle((380, 70, 892, 312), fill=(255, 248, 205), outline=OL, width=4)
    for y in range(120, 310, 34):
        d.line((395, y, 878, y), fill=(170, 190, 230), width=2)
    d.line((430, 70, 430, 312), fill=(230, 120, 120), width=3)
    d.rectangle((600, 55, 680, 85), fill=(240, 230, 150))   # tape
    body, sig = text.split("|")
    f = font("Inter-BoldItalic.otf", 40)
    for i, l in enumerate(wrap(body, f, 420)):
        d.text((455, 112 + i * 50), l, font=f, fill=(40, 40, 90))
    d.text((560, 250), sig, font=font("Inter-Italic.otf", 30), fill=(40, 40, 90))


def shout(img, text):
    d = ImageDraw.Draw(img)
    ctext(d, (W // 2, 625), text, font("Inter-Black.otf", 74), (255, 230, 60), stroke=6)


# ------------------------------------------------------------------ scene system
class Scene:
    def __init__(self, bg=None, lines=(), cast=None, music=None, fx=None, post=None,
                 sfx=None, pad=0.6, end_pad=0.9, dur=None, draw=None, anchors=None):
        self.bg, self.lines, self.cast = bg, list(lines), cast or {}
        self.music, self.fx, self.post, self.sfx_fn = music, fx, post, sfx
        self.pad, self.end_pad, self.fixed, self.draw_fn = pad, end_pad, dur, draw
        self.anchors = anchors or {}
        self.ls, self.ld = [], []

    def build(self, t0):
        self.t0 = t0
        t = self.pad
        for ln in self.lines:
            d = ln[2] if len(ln) > 2 else line_dur(ln[1])
            self.ls.append(t)
            self.ld.append(d)
            t += d
        self.dur = self.fixed or (t + self.end_pad)
        return t0 + self.dur

    def current(self, lt):
        for i, s in enumerate(self.ls):
            if s <= lt < s + self.ld[i]:
                return i
        return None

    def render(self, lt, f):
        if self.draw_fn:
            return self.draw_fn(self, lt, f)
        img = self.bg(self, lt).copy() if callable(self.bg) else self.bg.copy()
        d = ImageDraw.Draw(img)
        if self.fx:
            self.fx(img, d, self, lt, f)
        i = self.current(lt)
        spk, txt = (self.lines[i][0], self.lines[i][1]) if i is not None else (None, "")
        mouth = (i is not None and lt - self.ls[i] < talk_dur(txt, self.ld[i]) and (f // 3) % 2 == 0)
        heads = {}
        for k, (name, fn) in enumerate(self.cast.items()):
            st = dict(x=0, s=0.8, yoff=0, angle=0, visible=True)
            st.update(fn(self, lt))
            if not st.pop("visible"):
                continue
            flags = dict(st.pop("flags", {}))
            if name == "jensen" and flags.get("jacket"):
                flags["jacket_talk"] = spk == "jacket" and mouth
            blink = (f + k * 37) % 84 < 3
            paste_sprite(img, name, st["x"], st["s"], spk == name and mouth, blink,
                         st["yoff"], st["angle"], **flags)
            heads[name] = head_pos(name, st["x"], st["s"], st["yoff"])
        if self.post:
            self.post(img, ImageDraw.Draw(img), self, lt, f)
        if spk == "note":
            note_card(img, txt)
        elif spk == "all":
            shout(img, txt)
        elif spk:
            hx, hy = self.anchors[spk](self, lt) if spk in self.anchors else heads[spk]
            bubble(img, spk, txt, hx, hy)
        return img


def at(x, s=0.8, **kw):
    return lambda sc, lt: dict(x=x, s=s, **kw)


# ------------------------------------------------------------------ cards
def card_bg(color):
    return vgrad(W, H, tuple(int(c * 0.35) for c in color), (10, 10, 14))


def draw_title(sc, lt, f):
    img = vgrad(W, H, (20, 30, 15), (5, 5, 8))
    d = ImageDraw.Draw(img)
    rng = random.Random(2)
    for _ in range(60):
        x, y, ph = rng.randrange(W), rng.randrange(H), rng.random() * 6
        r = 2 + 2 * math.sin(lt * 4 + ph)
        if r > 0.5:
            d.ellipse((x - r, y - r, x + r, y + r), fill=(160, 230, 90))
    z = 0.6 + 0.4 * ease(lt / 0.8)
    ctext(d, (W // 2, 230), "THE JACKET", font("Inter-Black.otf", int(130 * z)), (255, 255, 255), 6, (118, 185, 0))
    ctext(d, (W // 2, 370), "MUST GO ON", font("Inter-Black.otf", int(130 * z)), (255, 255, 255), 6, (118, 185, 0))
    if lt > 1.0:
        ctext(d, (W // 2, 500), "a fictional cartoon parody  -  5 characters  -  1 missing jacket",
              font("Inter-SemiBold.otf", 32), (210, 210, 210))
    sp = C.sprite("jacket", 0.45, (f // 4) % 2 == 0, False)
    img.paste(sp, (int(W // 2 - 81 + 30 * math.sin(lt * 2)), 520 + int(8 * math.sin(lt * 3))), sp)
    return img


CAST_CARDS = [
    ("jensen", "The Visionary CEO",
     "Superpower: explains matrix multiplication until stadiums cheer.",
     "Weakness: completely powerless without his leather jacket.", {}),
    ("jacket", "The Legendary Leather Jacket",
     "Superpower: has more fans than most rock stars.",
     "Weakness: dry clean only. Prone to existential crises.", {}),
    ("chip", "The Tiny Super-GPU",
     "Superpower: ten trillion calculations per second.",
     "Weakness: runs hot. Secretly just wants to play video games.", {"hot": False}),
    ("danny", "The Diner Waiter",
     "Superpower: has refilled the same coffee cup since 1993.",
     "Weakness: still waiting for someone to order actual food.", {}),
    ("wendy", "The Wall Street Analyst",
     "Superpower: tracks every 0.01% move of the stock.",
     "Weakness: faints at every 0.01% move of the stock.", {}),
]


def make_card(idx):
    name, role, power, weak, flags = CAST_CARDS[idx]
    color = C.INFO[name]["color"]
    bg = card_bg(color)

    def draw(sc, lt, f):
        img = bg.copy()
        d = ImageDraw.Draw(img)
        ctext(d, (W // 2, 50), f"MEET THE CAST  {idx + 1}/5", font("Inter-Black.otf", 28), (200, 200, 200))
        x = lerp(-250, 290, lt / 0.5)
        sp = C.sprite(name, 1.15, (f // 3) % 2 == 0 and 0.6 < lt < 2.6, (f % 70) < 3, **flags)
        img.paste(sp, (int(x - C.ANCHOR[0] * 1.15), int(700 - C.ANCHOR[1] * 1.15)), sp)
        tx = lerp(W + 50, 560, (lt - 0.15) / 0.5)
        d.text((tx, 190), C.INFO[name]["name"], font=font("Inter-Black.otf", 62), fill=(255, 255, 255))
        d.text((tx, 270), role, font=font("Inter-Bold.otf", 38), fill=color)
        y = 360
        for txt in (power, weak):
            for l in wrap(txt, font("Inter-SemiBold.otf", 30), 640):
                d.text((tx, y), l, font=font("Inter-SemiBold.otf", 30), fill=(230, 230, 230))
                y += 42
            y += 22
        return img
    return Scene(draw=draw, dur=3.8, sfx=lambda sc: [(0.0, "whoosh")])


def draw_end(sc, lt, f):
    img = vgrad(W, H, (20, 30, 15), (5, 5, 8))
    d = ImageDraw.Draw(img)
    ctext(d, (W // 2, 120), "THE END", font("Inter-Black.otf", 110), (255, 255, 255), 6, (118, 185, 0))
    ctext(d, (W // 2, 225), "STARRING", font("Inter-Bold.otf", 26), (170, 170, 170))
    for i, (n, role, *_r) in enumerate(CAST_CARDS):
        y = 270 + i * 46
        d.text((W // 2 - 20, y), C.INFO[n]["name"], font=font("Inter-Black.otf", 30), fill=C.INFO[n]["color"], anchor="ra")
        d.text((W // 2 + 20, y), role, font=font("Inter-SemiBold.otf", 30), fill=(220, 220, 220))
    for i, l in enumerate(("A fictional, good-natured parody. Not affiliated with or endorsed by NVIDIA or Jensen Huang.",
                           "No jackets were harmed. The jacket insists on a sequel.")):
        ctext(d, (W // 2, 560 + i * 36), l, font("Inter-Regular.otf", 22), (170, 170, 170))
    for k, n in enumerate(C.DRAW):
        sp = C.sprite(n, 0.22, False, (f + 9 * k) % 60 < 3, **({"ko": True} if n == "wendy" else {}))
        img.paste(sp, (330 + k * 130, 615 - int(abs(math.sin(lt * 4 + k)) * 12)), sp)
    return img


# ------------------------------------------------------------------ story scenes
def backstage():
    lines = [
        ("jensen", "Ten minutes to the keynote. Where is my jacket?"),
        ("chip", "Bad news, boss. The jacket left a note!"),
        ("note", "Gone to find myself.|- Sir Leatherworth", 3.4),
        ("jensen", "He's been doing this ever since we hit a trillion dollars."),
        ("wendy", "EMERGENCY! The internet says the CEO was spotted in a CARDIGAN!"),
        ("wendy", "Stock down 0.01 percent! That's... a small country!!"),
        ("chip", "Relax. I know exactly where he went."),
        ("jensen", "Where it all started... The diner!"),
    ]

    def wendy(sc, lt):
        enter = sc.ls[4]
        faint = sc.ls[5] + sc.ld[5] - 0.5
        ang = -90 * ease((lt - faint) / 0.35)
        return dict(x=lerp(1450, 990, (lt - enter + 0.7) / 0.6), visible=lt > enter - 0.8,
                    angle=ang, flags={"ko": lt > faint + 0.2})

    def fx(img, d, sc, lt, f):
        secs = max(0, 600 - int(lt * 7))
        d.rounded_rectangle((20, 70, 300, 140), 10, fill=(10, 10, 10), outline=(200, 40, 40), width=3)
        d.text((40, 78), "KEYNOTE IN", font=font("Inter-Bold.otf", 18), fill=(200, 200, 200))
        d.text((40, 96), f"{secs // 60:02d}:{secs % 60:02d}", font=font("Inter-Black.otf", 38), fill=(255, 60, 60))

    return Scene(bg=bg_backstage(), lines=lines, fx=fx,
                 cast={"jensen": at(470), "chip": at(700, 0.75), "wendy": wendy},
                 music=(84, [0, 3, 5, 3], "keynote"),
                 sfx=lambda sc: [(sc.ls[4] - 0.8, "whoosh"), (sc.ls[5] + sc.ld[5] - 0.5, "boing"),
                                 (sc.ls[7] + 1.4, "dundun")])


def street():
    lines = [
        ("chip", "I'll compute the fastest route! Ten trillion calculations... GO!"),
        ("jensen", "Chip! You're using the power of an entire city!"),
        ("chip", "Totally worth it. Turn left at the moon."),
    ]

    def dark(sc, lt):
        return lt > sc.ls[1] - 0.3 and (int(lt * 9) % 4 != 0)

    def bg(sc, lt):
        src = bg_street(not dark(sc, lt))
        off = int(lt * 520) % (src.width - W)
        return src.crop((off, 0, off + W, H))

    def run(x, s, ph):
        return lambda sc, lt: dict(x=x + 20 * math.sin(lt * 2 + ph), s=s,
                                   yoff=-abs(math.sin(lt * 11 + ph)) * 22,
                                   flags={"hot": lt > sc.ls[0] + 1.0} if s < 0.8 else {})

    def post(img, d, sc, lt, f):
        rng = random.Random(f // 2)
        for _ in range(9):
            y = rng.randrange(150, GROUND)
            x = rng.randrange(0, W)
            d.line((x, y, x + rng.randrange(80, 200), y), fill=(230, 230, 255), width=3)
        if lt > sc.ls[0] + 1.0:   # chip steam
            cx = 820 + 20 * math.sin(lt * 2 + 1)
            for k in range(5):
                u = (lt * 1.6 + k / 5) % 1
                r = 10 + 30 * u
                y = GROUND - 230 - 160 * u
                d.ellipse((cx - r + 30 * math.sin(k + lt), y - r, cx + r + 30 * math.sin(k + lt), y + r),
                          outline=(220, 220, 230), width=4)
        if dark(sc, lt):
            d.text((40, 670), "CITY POWER: 3%", font=font("Inter-Black.otf", 34), fill=(255, 80, 80))

    return Scene(bg=bg, lines=lines, post=post, pad=0.8,
                 cast={"jensen": run(470, 0.8, 0), "chip": run(820, 0.72, 1.3)},
                 music=(150, [0, 0, 5, 7], "chase"),
                 sfx=lambda sc: [(sc.ls[1] - 0.3, "powerdown")])


def diner():
    lines = [
        ("danny", "Welcome back. Booth number 3... just like 1993?"),
        ("jacket", "I needed to remember where we came from."),
        ("jacket", "Three founders. One big idea. Zero customers."),
        ("danny", "And one cup of coffee. For four hours."),
        ("chip", "Wait... you built a GPU empire on ONE coffee?"),
        ("jensen", "Leatherworth, without you I'm just a guy explaining matrix multiplication."),
        ("jacket", "...Fine. But I want my own spotlight. And a fan club."),
        ("danny", "So... can I finally take your order?"),
        ("jensen", "No time! To the keynote!"),
    ]

    def walk(x, s, delay):
        return lambda sc, lt: dict(x=lerp(-200, x, (lt - delay) / 1.2), s=s,
                                   yoff=-abs(math.sin(lt * 9)) * 14 if lt < delay + 1.2 else 0)

    def jacket(sc, lt):
        fly = sc.ls[8] + 0.9
        u = (lt - fly) / 0.7
        return dict(x=lerp(1065, 400, u), s=0.75, yoff=lerp(-110, -60, u) - 25 * math.sin(math.pi * clamp(u)),
                    visible=u < 1.0)

    def post(img, d, sc, lt, f):
        diner_table(img, d)

    return Scene(bg=bg_diner(), lines=lines, post=post, pad=1.2,
                 cast={"jacket": jacket, "danny": at(760, 0.8), "jensen": walk(430, 0.8, 0.1),
                       "chip": walk(200, 0.72, 0.4)},
                 music=(96, [0, 5, 7, 5], "jazzy"),
                 sfx=lambda sc: [(0.15, "ding"), (sc.ls[8] + 0.9, "whoosh")])


def stage():
    lines = [
        ("jensen", "Ladies and gentlemen... the more you buy..."),
        ("all", "...THE MORE YOU SAVE!!", 2.6),
        ("wendy", "Stock UP 8 percent!! I can't feel my spreadsheets!"),
        ("jacket", "Thank you, thank you. I'm here all week. Dry clean only."),
        ("danny", "Sir. Your coffee bill. Since 1993. With interest."),
        ("jensen", "FOUR POINT TWO TRILLION DOLLARS?!"),
        ("jensen", "...Do you accept GPUs?"),
        ("chip", "Wait. Am I the tip?!"),
    ]
    S = 0.85

    def wendy(sc, lt):
        faint = sc.ls[2] + sc.ld[2] - 0.5
        return dict(x=230, s=0.78, angle=-90 * ease((lt - faint) / 0.35),
                    flags={"ko": lt > faint + 0.2, "chart_up": lt > sc.ls[2]})

    def danny(sc, lt):
        return dict(x=lerp(1450, 1090, (lt - sc.ls[4] + 1.0) / 0.9), s=0.8, visible=lt > sc.ls[4] - 1.1)

    def fx(img, d, sc, lt, f):
        stage_screen(img, d, 0 if lt < sc.ls[1] else (1 if lt < sc.ls[2] else 2))
        cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cone)
        sway = 60 * math.sin(lt * 0.8)
        cd.polygon([(600 + sway, 0), (680 + sway, 0), (840, GROUND + 10), (440, GROUND + 10)], fill=(255, 255, 210, 45))
        cd.ellipse((440, GROUND - 25, 840, GROUND + 25), fill=(255, 255, 210, 70))
        img.paste(cone, (0, 0), cone)

    def post(img, d, sc, lt, f):
        hype = lt > sc.ls[1]
        for k in range(26):
            x = k * 52 - 10
            bob = abs(math.sin(lt * (9 if hype else 2) + k)) * (18 if hype else 4)
            y = 668 - bob + (k % 3) * 10
            if hype and k % 2:
                d.line((x + 8, y + 20, x - 6, y - 40), fill=(5, 5, 8), width=12)
                d.line((x + 40, y + 20, x + 54, y - 40), fill=(5, 5, 8), width=12)
            d.ellipse((x, y, x + 48, y + 52), fill=(5, 5, 8))
            d.rectangle((x - 6, min(y + 40, H - 1), x + 54, H), fill=(5, 5, 8))
        if sc.ls[5] - 0.2 < lt < sc.ls[7]:                       # the bill
            yy = lerp(-420, 70, (lt - sc.ls[5] + 0.2) / 0.4)
            yy = yy + 70
            d.rectangle((28, yy + 8, 408, yy + 388), fill=(0, 0, 0))
            d.rectangle((20, yy, 400, yy + 380), fill=(255, 255, 245), outline=OL, width=4)
            ctext(d, (210, yy + 40), "DANNY'S DINER - GUEST CHECK", font("Inter-Black.otf", 20), (180, 30, 40))
            rows = [("Coffee (1 cup, 1993)", "$1.29"), ("Refills (33 years)", "$2,840.00"),
                    ("Interest", "$4,199,999,997,158.71")]
            for i, (a, b) in enumerate(rows):
                d.text((40, yy + 90 + i * 56), a, font=font("Inter-SemiBold.otf", 20), fill=(40, 40, 40))
                d.text((380, yy + 136 + i * 56), b, font=font("Inter-Bold.otf", 20), fill=(40, 40, 40), anchor="rs")
            d.line((40, yy + 270, 380, yy + 270), fill=OL, width=3)
            d.text((40, yy + 290), "TOTAL", font=font("Inter-Black.otf", 28), fill=(20, 20, 20))
            d.text((380, yy + 345), "$4.2 TRILLION", font=font("Inter-Black.otf", 28), fill=(200, 30, 40), anchor="rs")

    return Scene(bg=bg_stage(), lines=lines, fx=fx, post=post, end_pad=1.6,
                 cast={"wendy": wendy, "jensen": at(640, S, flags={"jacket": True}),
                       "chip": at(870, 0.72), "danny": danny},
                 anchors={"jacket": lambda sc, lt: (640, GROUND - (C.ANCHOR[1] - 300) * S)},
                 music=(112, [0, 5, 3, 7], "keynote"),
                 sfx=lambda sc: [(sc.ls[1], "cheer"), (sc.ls[2] + sc.ld[2] - 0.5, "boing"),
                                 (sc.ls[3] + sc.ld[3] - 0.6, "rimshot"), (sc.ls[5], "dundun"),
                                 (sc.ls[7] + 1.4, "tada")])


def build_timeline():
    scenes = [Scene(draw=draw_title, dur=4.5, sfx=lambda sc: [(0.2, "tada")])]
    scenes += [make_card(i) for i in range(5)]
    scenes += [backstage(), street(), diner(), stage(), Scene(draw=draw_end, dur=6.5)]
    t = 0.0
    for sc in scenes:
        t = sc.build(t)
    return scenes, t


def build_audio(scenes, total, path):
    tr = Track(total)
    tr.music(0, scenes[5].t0 + scenes[5].dur, 100, [0, 5, 7, 5], "keynote")
    for sc in scenes:
        if sc.music:
            bpm, chords, style = sc.music
            tr.music(sc.t0, sc.t0 + sc.dur, bpm, chords, style)
        for i, ln in enumerate(sc.lines):
            if ln[0] != "note":
                tr.voice(sc.t0 + sc.ls[i], ln[0], talk_dur(ln[1], sc.ld[i]))
        if sc.sfx_fn:
            for lt, name in sc.sfx_fn(sc):
                tr.sfx(sc.t0 + lt, name)
    tr.music(scenes[-1].t0, total, 100, [0, 5, 7, 0], "keynote")
    tr.write(path)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "output",
                                                              "the_jacket_must_go_on.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    scenes, total = build_timeline()
    wav = os.path.abspath(out) + ".wav"
    build_audio(scenes, total, wav)
    n = int(total * FPS)
    print(f"Rendering {n} frames ({total:.1f}s)...", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    si = 0
    for fr in range(n):
        t = fr / FPS
        while si < len(scenes) - 1 and t >= scenes[si].t0 + scenes[si].dur:
            si += 1
        sc = scenes[si]
        lt = t - sc.t0
        img = sc.render(lt, fr).convert("RGB")
        fade = max(clamp(1 - lt / 0.3), clamp(1 - (sc.dur - lt) / 0.3))
        if fade > 0:
            img = Image.blend(img, black, fade)
        ff.stdin.write(img.tobytes())
        if fr % 240 == 0:
            print(f"  frame {fr}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print("Done:", out)


if __name__ == "__main__":
    main()
