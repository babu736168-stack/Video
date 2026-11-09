#!/usr/bin/env python3
"""Economics class renderer: mind map + topic boards with an animation stage (moving symbols, live graphs).
python3 render_econ.py ds_sample "Econ01 - Demand and Supply (sample).mp4"      (run from econ/)
python3 render_econ.py --still ds_sample 40,80,... sheet.jpg

Board = header (catchy label + topic) | stage on the left (anim:<name> events) | points growing on the right.
"""
import os, sys, json, math, importlib, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.getcwd(); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "polity"))
import render as R                      # polity renderer: fonts, easing, text, sprites, audio mix
from render import F, ease, ease_out, back, lerp, wrap, txt, glow_text, pill_sprite, paste_center, curve, make_bg

W, H, FPS = R.W, R.H, R.FPS
WHITE, DIM, GOLD, AMBER = R.WHITE, R.DIM, R.GOLD, R.AMBER
BLUE, ORANGE, GREEN, RED = (90, 170, 255), (255, 140, 50), (70, 210, 140), (255, 90, 90)
ACC = (120, 200, 255)
BG = None
EMO = {}


def emo(ch, size):
    """Colour emoji sprite (Noto Color Emoji renders at 109 px; scaled)."""
    if ch not in EMO:
        f = ImageFont.truetype(R.EMOJI, 109)
        im = Image.new("RGBA", (200, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        EMO[ch] = im.crop(im.getbbox())
    e = EMO[ch]
    return e.resize((max(1, int(e.width * size / e.height)), size), Image.LANCZOS)


def put(im, ch, xy, size, alpha=1.0, flip=False):
    if alpha <= 0.01: return
    e = emo(ch, int(size))
    if flip: e = e.transpose(Image.FLIP_LEFT_RIGHT)
    paste_center(im, e, xy, 1, alpha)


# ------------------------------------------------------------------ graphs
class Graph:
    """Price (y) vs quantity (x) inside a stage box."""
    def __init__(self, box):
        x0, y0, x1, y1 = box
        self.ox, self.oy = x0 + 120, y1 - 90
        self.w, self.h = x1 - x0 - 200, y1 - y0 - 170

    def P(self, q, p):
        return (self.ox + q * self.w, self.oy - p * self.h)

    def axes(self, im, d, u=1.0):
        a = ease_out(u)
        d.line([self.P(0, 0), self.P(1.02 * a, 0)], fill=WHITE + (220,), width=4)
        d.line([self.P(0, 0), self.P(0, 1.02 * a)], fill=WHITE + (220,), width=4)
        if a > 0.9:
            x, y = self.P(1.03, 0); d.polygon([(x, y - 9), (x + 18, y), (x, y + 9)], fill=WHITE + (220,))
            x, y = self.P(0, 1.03); d.polygon([(x - 9, y), (x, y - 18), (x + 9, y)], fill=WHITE + (220,))
            txt(im, self.P(1.0, -0.08), "Quantity", F("Inter-SemiBold", 26), DIM, anchor="rm")
            txt(im, (self.ox - 20, self.oy - self.h - 30), "Price (₹)", F("Inter-SemiBold", 26), DIM, anchor="lm")

    def line(self, d, f, q0, q1, u, col, width=6):
        n = 60; pts = []
        for i in range(int(n * min(1, max(0, u))) + 1):
            q = q0 + (q1 - q0) * i / n; pts.append(self.P(q, f(q)))
        if len(pts) > 1: d.line(pts, fill=col, width=width, joint="curve")

    def dashed(self, d, a, b, col, dash=12):
        (x0, y0), (x1, y1) = a, b
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / dash))
        for i in range(0, n, 2):
            s, e = i / n, min(1, (i + 1) / n)
            d.line([(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s), (x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)], fill=col, width=3)

    def dot(self, im, d, q, p, col, label=None, r=13, guides=True, lab_q=None, lab_p=None):
        x, y = self.P(q, p)
        if guides:
            self.dashed(d, (x, y), self.P(q, 0), col + (170,)); self.dashed(d, (x, y), self.P(0, p), col + (170,))
            if lab_q: txt(im, (x, self.oy + 30), lab_q, F("Inter-Bold", 26), col, anchor="mm")
            if lab_p: txt(im, (self.ox - 18, y), lab_p, F("Inter-Bold", 26), col, anchor="rm")
        d.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill=col + (60,))
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))
        if label: txt(im, (x + 22, y - 24), label, F("InterDisplay-Black", 30), col)


D = lambda q, s=0.0: 0.88 - 0.76 * (q - s)
S = lambda q, s=0.0: 0.12 + 0.76 * (q - s)
D_inv = lambda p, s=0.0: (0.88 - p) / 0.76 + s
S_inv = lambda p, s=0.0: (p - 0.12) / 0.76 + s


def tag(im, d, xy, text, col, size=34, alpha=1.0):
    f = F("InterDisplay-Black", size)
    w = f.getlength(text) + 36; x, y = xy
    d.rounded_rectangle((x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.8), radius=14, fill=col + (int(235 * alpha),))
    txt(im, (x, y), text, f, (15, 15, 25), alpha=alpha, anchor="mm")


# ------------------------------------------------------------------ stage animations: f(im, d, box, a)  a = seconds since start
def a_icon(icon):
    def f(im, d, box, a):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        put(im, icon, (cx, cy + 8 * math.sin(a * 2)), 260 * back(a / 0.6), min(1, a * 3))
    return f


def a_wish(im, d, box, a):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    d.rounded_rectangle((cx - 60, y0 + 120, x1 - 60, y0 + 470), radius=24, outline=DIM + (160,), width=4)  # shop window
    txt(im, (cx + 180, y0 + 95), "TOY SHOP", F("InterDisplay-Black", 34), DIM, anchor="mm")
    put(im, "🚗", (cx + 190, y0 + 330 + 6 * math.sin(a * 3)), 150, min(1, a * 2))
    kx = x0 + 70 + min(1, a / 1.5) * 170
    put(im, "🧒", (kx, y1 - 250), 230, 1)
    # thought bubble
    b = ease_out((a - 1.2) / 0.5)
    if b > 0:
        d.ellipse((kx + 60, y1 - 520, kx + 260, y1 - 380), fill=(255, 255, 255, int(230 * b)))
        d.ellipse((kx + 50, y1 - 375, kx + 80, y1 - 345), fill=(255, 255, 255, int(230 * b)))
        put(im, "🚗", (kx + 160, y1 - 450), 80, b)
    w = ease_out((a - 2.6) / 0.5)
    if w > 0:
        put(im, "👛", (kx + 30, y1 - 70), 110, w)
        tag(im, d, (kx + 190, y1 - 70), "₹ 0", RED, 40, w)
    s = (a - 5.0) / 0.4
    if s > 0:
        sc = 1.6 - 0.6 * ease_out(s)
        sp = pill_sprite([("NOT DEMAND", "InterDisplay-Black", 64, RED)], RED, fill=(40, 10, 10), pad=(30, 14), border=6)
        sp = sp.rotate(-12, expand=True, resample=Image.BICUBIC)
        paste_center(im, sp, (cx + 120, y0 + 560), sc, min(1, s * 2))


def a_mango(im, d, box, a):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    # cart
    d.rounded_rectangle((cx - 230, y1 - 330, cx + 230, y1 - 210), radius=18, fill=(120, 70, 30, 255))
    for wx in (cx - 150, cx + 150):
        d.ellipse((wx - 48, y1 - 240, wx + 48, y1 - 144), fill=(40, 30, 20, 255), outline=(200, 160, 110, 255), width=6)
    for i in range(9):
        put(im, "🥭", (cx - 180 + (i % 5) * 90 + (45 if i >= 5 else 0), y1 - 360 - (40 if i >= 5 else 0)), 80)
    cheap = a > 3.2
    flip = ease_out((a - 3.2) / 0.4)
    price = "₹60 / kg" if cheap else "₹200 / kg"
    col = GREEN if cheap else RED
    tag(im, d, (cx, y1 - 520), price, col, 54, 1.0 if not cheap else max(0.3, flip))
    # buyers: 2 at high price (walking away), 8 at low price (walking in)
    n = 8 if cheap else 2
    for k in range(n):
        side = -1 if k % 2 == 0 else 1
        slot = k // 2
        tx = cx + side * (300 + slot * 70)
        if not cheap:
            x = tx + side * max(0, a - 1.8) * 140          # they walk away
            put(im, "🧍", (x, y1 - 150), 150, max(0, 1 - max(0, a - 2.2) / 1.0), flip=side > 0)
        else:
            u = ease_out((a - 3.4 - k * 0.15) / 0.8)
            x = tx + side * 500 * (1 - u)
            put(im, "🧍", (x, y1 - 150 - 4 * abs(math.sin(a * 6 + k))), 150, u, flip=side > 0)


def a_demand_curve(im, d, box, a, along=False):
    g = Graph(box); g.axes(im, d, a / 0.6)
    g.line(d, D, 0.06, 0.94, (a - 0.5) / 1.3, BLUE + (255,))
    if a > 1.8: txt(im, g.P(0.95, D(0.95) - 0.06), "D", F("InterDisplay-Black", 44), BLUE)
    if a > 2.4 and not along:
        p = 0.75 - 0.45 * ease((a - 3.6) / 2.2)
        q = D_inv(p)
        g.dot(im, d, q, p, GOLD, lab_q="Q", lab_p="P")
        if a > 6: put(im, "🥭", lerp(g.P(q, p), g.P(q + 0.08, p + 0.12), 1), 70)
    if along:
        p = 0.5 + 0.25 * math.sin((a - 1.5) * 1.6)
        g.dot(im, d, D_inv(p), p, GOLD, lab_q="Q", lab_p="P")
        x, y = g.P(0.55, 0.62)
        txt(im, (x + 40, y - 40), "movement along", F("Inter-SemiBold", 30), GOLD)


def a_summer(im, d, box, a):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    s = ease_out(a / 1.2)
    put(im, "☀️", (x1 - 180, y0 + 260 - 120 * s), 200, s)
    txt(im, (x0 + 80, y0 + 100), "45°C", F("InterDisplay-Black", 90), (255, 120, 80), alpha=s)
    put(im, "🌡️", (x0 + 330, y0 + 110), 110, s)
    tag(im, d, (cx - 120, y1 - 420), "Kulfi ₹10 (same)", GOLD, 40)
    put(im, "🍦", (cx - 120, y1 - 560 + 6 * math.sin(a * 3)), 140)
    n = min(10, 2 + int(max(0, a - 1.5) * 2.2))
    for k in range(n):
        u = ease_out((a - 1.5 - k * 0.45) / 0.6) if k >= 2 else 1
        x = x0 + 90 + k * 92; y = y1 - 130 - 5 * abs(math.sin(a * 5 + k))
        put(im, "🧍", (x, y + 60 * (1 - u)), 140, u)
        put(im, "🍦", (x + 30, y - 40), 50, u)


def a_shift(im, d, box, a, sgn=1):
    g = Graph(box); g.axes(im, d, 1)
    sh = 0.2 * sgn * ease((a - 0.6) / 1.6)
    g.line(d, D, 0.06, 0.94, 1, BLUE + (110,), 5)
    txt(im, g.P(0.10, D(0.06) + 0.06), "D1", F("InterDisplay-Black", 38), BLUE, alpha=0.6, anchor="mm")
    q0, q1 = max(0.04, 0.06 + sh), min(1.0, 0.94 + sh)
    g.line(d, lambda q: D(q, sh), q0, q1, 1, (GREEN if sgn > 0 else RED) + (255,), 6)
    if a > 0.6:
        col = GREEN if sgn > 0 else RED
        txt(im, g.P(0.06 + sh, D(0.06) + 0.07), "D2", F("InterDisplay-Black", 44), col, alpha=min(1, (a - 0.6) * 2), anchor="mm")
        # same price, different quantity
        p = 0.5
        g.dot(im, d, D_inv(p), p, DIM, r=9, guides=True, lab_q="Q1", lab_p="P")
        if a > 2.2:
            g.dot(im, d, D_inv(p, sh), p, col, guides=True, lab_q="Q2")
            x0_, y_ = g.P(D_inv(p) + 0.03 * sgn, p + 0.06); x1_, _ = g.P(D_inv(p, sh) - 0.03 * sgn, p)
            d.line([(x0_, y_), (x1_, y_)], fill=col + (255,), width=5)
            d.polygon([(x1_, y_ - 12), (x1_ + 20 * sgn, y_), (x1_, y_ + 12)], fill=col + (255,))
            txt(im, g.P(0.62 if sgn > 0 else 0.12, 0.92), "Demand ↑ at the same price" if sgn > 0 else "Demand ↓ at the same price",
                F("Inter-SemiBold", 30), col)


def a_farmer(im, d, box, a):
    x0, y0, x1, y1 = box; cx = (x0 + x1) / 2
    d.rectangle((x0 + 30, y1 - 160, x1 - 30, y1 - 40), fill=(60, 110, 50, 255))           # field
    u = (a * 120) % (x1 - x0 + 300) - 150
    put(im, "🚜", (x0 + u, y1 - 200), 150, 1, flip=True)
    tag(im, d, (x0 + 230, y0 + 110), "Mandi price ↑", GREEN, 40, ease_out(a / 0.6))
    n = min(12, 2 + int(max(0, a - 1.5) * 2.5))
    for k in range(n):
        uu = ease_out((a - 1.5 - k * 0.4) / 0.5) if k >= 2 else 1
        put(im, "📦", (cx - 60 + (k % 6) * 85, y1 - 300 - (k // 6) * 80 - 40 * (1 - uu)), 80, uu)
        put(im, "🍅", (cx - 60 + (k % 6) * 85, y1 - 350 - (k // 6) * 80 - 40 * (1 - uu)), 44, uu)
    txt(im, (cx + 150, y0 + 220), "More crop → more supply", F("Inter-SemiBold", 32), WHITE, alpha=ease_out((a - 3) / 0.5), anchor="mm")


def a_supply_curve(im, d, box, a):
    g = Graph(box); g.axes(im, d, a / 0.6)
    g.line(d, S, 0.06, 0.94, (a - 0.5) / 1.3, ORANGE + (255,))
    if a > 1.8: txt(im, g.P(0.95, S(0.95) + 0.02), "S", F("InterDisplay-Black", 44), ORANGE)
    if a > 2.2:
        p = 0.25 + 0.5 * ease((a - 2.6) / 2.5)
        g.dot(im, d, S_inv(p), p, GOLD, lab_q="Q", lab_p="P")
        x, y = g.P(S_inv(p), p); put(im, "📦", (x + 60, y + 10), 60)


def eq_base(im, d, g, sd=0.0, ss=0.0, pulse=0.0):
    g.axes(im, d, 1)
    g.line(d, lambda q: D(q, sd), 0.06 + sd, 0.94 + sd, 1, BLUE + (255,))
    g.line(d, lambda q: S(q, ss), max(0.02, 0.06 + ss), min(1.0, 0.94 + ss), 1, ORANGE + (255,))
    txt(im, g.P(0.95 + sd, D(0.95) - 0.06), "D", F("InterDisplay-Black", 44), BLUE)
    txt(im, g.P(min(0.97, 0.95 + ss), S(0.95) + 0.02), "S", F("InterDisplay-Black", 44), ORANGE)
    q = 0.5 + (sd + ss) / 2; p = D(q, sd)
    return q, p


def a_equilibrium(im, d, box, a):
    g = Graph(box); g.axes(im, d, a / 0.5)
    g.line(d, D, 0.06, 0.94, (a - 0.3) / 1.0, BLUE + (255,))
    g.line(d, S, 0.06, 0.94, (a - 0.8) / 1.0, ORANGE + (255,))
    if a > 1.3: txt(im, g.P(0.95, D(0.95) - 0.06), "D", F("InterDisplay-Black", 44), BLUE)
    if a > 1.8: txt(im, g.P(0.95, S(0.95) + 0.02), "S", F("InterDisplay-Black", 44), ORANGE)
    if a > 2.0:
        r = 13 + 4 * math.sin(a * 5)
        g.dot(im, d, 0.5, 0.5, GOLD, label="E", r=r, lab_q="Q*", lab_p="P*")
        put(im, "🤝", lerp(g.P(0.5, 0.5), g.P(0.62, 0.72), 1), 90, ease_out((a - 2.3) / 0.5))


def a_gap(im, d, box, a, high=True):
    g = Graph(box); eq_base(im, d, g)
    p = 0.72 if high else 0.28
    qd, qs = D_inv(p), S_inv(p)
    u = ease_out(a / 0.6)
    col = AMBER if high else RED
    lo, hi = sorted((qd, qs))
    x0, y = g.P(lo, p); x1, _ = g.P(lo + (hi - lo) * u, p)
    d.rectangle((x0, y - 10, x1, y + 10), fill=col + (200,))
    g.dot(im, d, qd, p, BLUE, r=10, guides=False); g.dot(im, d, qs, p, ORANGE, r=10, guides=False)
    g.dashed(d, g.P(0, p), g.P(lo, p), col + (200,))
    txt(im, (g.ox - 18, y), "P", F("Inter-Bold", 28), col, anchor="rm")
    txt(im, ((x0 + x1) / 2, y + (-48 if high else 48)), "SURPLUS" if high else "SHORTAGE", F("InterDisplay-Black", 44), col,
        alpha=u, anchor="mm")
    put(im, "📦" if high else "🧍", ((x0 + x1) / 2 + 180, y + (-48 if high else 48)), 60, u)
    # price pushed back to E
    k = ease((a - 2.0) / 1.5)
    if k > 0:
        py = p + (0.5 - p) * k
        ax, ay = g.P(0.0, py)
        d.polygon([(ax - 40, ay), (ax - 60, ay + (-24 if high else 24)), (ax - 20, ay + (-24 if high else 24))], fill=col + (255,))
        g.dot(im, d, 0.5, 0.5, GOLD, label="E", r=11, guides=False)


def a_tomato(im, d, box, a, up=True):
    g = Graph(box)
    s0, s1 = (0.0, -0.25) if up else (-0.25, 0.0)
    ss = s0 + (s1 - s0) * ease((a - 0.5) / 2.0)
    if ss != s0 or True:
        g.line(d, S, 0.06, 0.94, 1, ORANGE + (90,), 4)
    q, p = eq_base(im, d, g, ss=ss)
    g.dot(im, d, q, p, RED if p > 0.55 else GREEN, label="E", lab_p="₹↑" if p > 0.55 else "₹")
    put(im, "🍅", (box[2] - 150, box[1] + 130), 130)
    lab = "Supply ↓ (crop damage)" if up else "Supply ↑ (new crop)"
    tag(im, d, (box[0] + 330, box[1] + 110), lab, RED if up else GREEN, 34, ease_out(a / 0.5))
    if up and a > 3:
        put(im, "🌧️", (box[2] - 330, box[1] + 120 + 6 * math.sin(a * 3)), 100)


ANIMS = dict(wish=a_wish, mango=a_mango, demand_curve=a_demand_curve,
             move_along=lambda im, d, b, a: a_demand_curve(im, d, b, a + 2.0, along=True),
             summer=a_summer, shift_right=lambda im, d, b, a: a_shift(im, d, b, a, 1),
             shift_left=lambda im, d, b, a: a_shift(im, d, b, a, -1), farmer=a_farmer, supply_curve=a_supply_curve,
             equilibrium=a_equilibrium, surplus=lambda im, d, b, a: a_gap(im, d, b, a, True),
             shortage=lambda im, d, b, a: a_gap(im, d, b, a, False),
             tomato_up=lambda im, d, b, a: a_tomato(im, d, b, a, True),
             tomato_down=lambda im, d, b, a: a_tomato(im, d, b, a, False))


# ------------------------------------------------------------------ film
class Film:
    def __init__(self, mod):
        self.S = importlib.import_module(mod)
        self.TL = json.load(open(os.path.join(HERE, "out", mod, "timeline.json")))
        self.total = self.TL["total"]
        self.ev = [(l["start"], l["ev"]) for l in self.TL["lines"] if l["ev"]]
        self.t_of = lambda name: next((t for t, e in self.ev if e == name), None)
        self.topic = {tp["id"]: tp for tp in self.S.TOPICS}
        self.focus_list = [(t, e.split(":", 1)[1]) for t, e in self.ev if e.startswith("focus:")]
        self.points, self.anims = {}, {}
        for k, (tf, tid) in enumerate(self.focus_list):
            t_end = self.focus_list[k + 1][0] if k + 1 < len(self.focus_list) else 1e9
            sel = [(t, e) for t, e in self.ev if tf <= t < t_end]
            self.points[tid] = [(t, e.split(":", 1)[0], e.split(":", 1)[1]) for t, e in sel if e.split(":")[0] in ("pt", "ex")]
            self.anims[tid] = [(t, e.split(":", 1)[1]) for t, e in sel if e.startswith("anim:")]
        self.t_recap = next((t for t, e in self.ev if e.startswith("recap")), None)
        self.t_outro = next((t for t, e in self.ev if e.startswith("outro")), None)
        # map: centre + topics on an ellipse
        n = len(self.S.TOPICS)
        self.pos = {"center": (960, 560)}
        for i, tp in enumerate(self.S.TOPICS):
            ang = math.radians(-90 + 360 * i / n)
            self.pos[tp["id"]] = (960 + 640 * math.cos(ang), 560 + 340 * math.sin(ang))
        t_topics = self.t_of("topics") or 0
        self.appear = {"center": self.t_of("center") or 0}
        for i, tp in enumerate(self.S.TOPICS): self.appear[tp["id"]] = t_topics + 0.4 + i * 1.1
        C = self.S.CHAPTER
        self.sp = {"center": pill_sprite([(C["kicker"], "Inter-SemiBold", 22, DIM), (C["title"], "InterDisplay-Black", 52, WHITE)],
                                         ACC, pad=(40, 24), border=3)}
        for tp in self.S.TOPICS:
            for hl in (False, True):
                sp = pill_sprite([("", "Inter-Medium", 50, WHITE), (tp["name"], "InterDisplay-Bold", 32, WHITE)], ACC,
                                 w=330, pad=(20, 14), border=3, glow=hl)
                put(sp, tp["icon"], (sp.width / 2, sp.height / 2 - 26), 54)
                self.sp[tp["id"] + ("_hl" if hl else "")] = sp

    def draw_map(self, t, hl=None, hl_u=0.0, done=(), dim=0.0, pulse=None):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        c = self.pos["center"]
        for tp in self.S.TOPICS:
            ta = self.appear[tp["id"]]
            if t < ta: continue
            u = (t - ta) / 0.7
            al = 0.3 if (hl and tp["id"] != hl) and dim else 0.85
            curve(d, c, self.pos[tp["id"]], ease_out(u * 1.2), ACC + (int(255 * al),), width=4)
        if t >= self.appear["center"]:
            u = (t - self.appear["center"]) / 0.6
            paste_center(im, self.sp["center"], c, 0.5 + 0.5 * back(u) if u < 1 else 1, min(1, u * 2) * (1 - 0.5 * dim if hl else 1))
        for tp in self.S.TOPICS:
            tid = tp["id"]; ta = self.appear[tid]
            if t < ta: continue
            u = (t - ta) / 0.7
            cur = lerp(c, self.pos[tid], back(u)) if u < 1 else self.pos[tid]
            sc = 0.3 + 0.7 * back(u) if u < 1 else 1
            al = min(1, u * 2)
            if hl and tid != hl: al *= 1 - 0.6 * dim
            key = tid + "_hl" if (tid == hl or tid == pulse) else tid
            if tid == hl or tid == pulse: sc *= 1 + 0.05 * math.sin(t * 5)
            paste_center(im, self.sp[key], cur, sc, al)
            if tid in done:
                x, y = cur
                d.ellipse((x + 140, y - 60, x + 176, y - 24), fill=GREEN + (255,))
                d.line([(x + 149, y - 42), (x + 156, y - 34), (x + 168, y - 50)], fill=(255, 255, 255, 255), width=4)
        if hl and hl_u > 0 and self.topic[hl]["label"]:
            sp = pill_sprite([(self.topic[hl]["label"].upper(), "InterDisplay-Black", 32, (25, 18, 0))], GOLD, fill=GOLD, pad=(28, 12), border=0)
            x, y = self.pos[hl]; y += -110 if y > 300 else 110
            x = min(max(x, sp.width / 2 + 30), W - sp.width / 2 - 30)
            paste_center(im, sp, (x, y), back(hl_u * 1.3), min(1, hl_u * 3))
        return im

    # ---- board
    def layout(self, tid):
        if getattr(self, "_bl", (None,))[0] == tid: return self._bl[1]
        X0, X1, fs, gap, HMAX = 1190, 1860, 30, 26, 820
        rows = []
        for te, kind, text in self.points.get(tid, []):
            head, _, sub = text.partition("|")
            hf = F("Inter-SemiBold" if kind == "pt" else "Inter-MediumItalic", fs)
            tw = X1 - X0 - (70 if kind == "ex" else 0)
            hl = wrap(head, hf, tw); sl = wrap(sub, F("Inter-Regular", int(fs * 0.85)), tw) if sub else []
            rows.append(dict(t=te, kind=kind, hl=hl, sl=sl, fs=fs,
                             h=len(hl) * fs * 1.3 + len(sl) * fs * 0.85 * 1.3 + (22 if kind == "ex" else 0)))
        pages, cur, hh = [], [], 0
        for r in rows:
            if cur and hh + gap + r["h"] > HMAX: pages.append(cur); cur, hh = [], 0
            hh += (gap if cur else 0) + r["h"]; cur.append(r)
        if cur: pages.append(cur)
        for pg in pages:
            y = 200
            for r in pg: r["y"] = y; y += r["h"] + gap
        self._bl = (tid, pages)
        return pages

    def draw_board(self, t, tid, t0):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        tp = self.topic[tid]
        u = ease_out((t - t0) / 0.6)
        # header
        lab = tp["label"].upper()
        sp = pill_sprite([(lab, "InterDisplay-Black", 30, (25, 18, 0))], GOLD, fill=GOLD, pad=(26, 10), border=0)
        paste_center(im, sp, (70 + sp.width / 2, 70), back((t - t0) / 0.5), min(1, (t - t0) * 3))
        glow_text(im, (70 + sp.width + 30, 70), tp["name"], F("InterDisplay-Black", 56), WHITE, glow=ACC, anchor="lm", alpha=u, radius=10)
        put(im, tp["icon"], (1830, 70), 70, u)
        # stage
        box = (50, 140, 1140, 1040)
        d.rounded_rectangle(box, radius=30, fill=(16, 24, 50, int(235 * u)), outline=ACC + (int(120 * u),), width=2)
        anims = [(ta, n) for ta, n in self.anims.get(tid, []) if ta <= t]
        if anims:
            ta, name = anims[-1]
            ANIMS[name](im, d, box, t - ta)
            if len(anims) > 1 and t - ta < 0.4:           # quick dissolve between stage animations
                pass
        else:
            a_icon(tp["icon"])(im, d, box, t - t0)
        # points
        pages = self.layout(tid)
        pi = max([i for i, pg in enumerate(pages) if t >= pg[0]["t"] + 0.15] or [0])
        if pi > 0 and t - pages[pi][0]["t"] < 0.5:
            o = ease((t - pages[pi][0]["t"]) / 0.5)
            self.rows(im, d, t, pages[pi - 1], -60 * o, 1 - o)
        self.rows(im, d, t, pages[pi] if pages else [])
        return im

    def rows(self, im, d, t, rows, shift=0.0, fade=1.0):
        shown = [r for r in rows if t >= r["t"] + 0.15]
        for k, r in enumerate(shown):
            a = t - r["t"] - 0.15
            ta = ease_out(a / 0.45) * fade
            if ta <= 0: continue
            y = r["y"] + shift; fs = r["fs"]
            x = 1190 + 30 * (1 - ease_out(a / 0.45))
            col = AMBER if r["kind"] == "ex" else ACC
            d.ellipse((1162, y + fs * 0.65 - 8, 1178, y + fs * 0.65 + 8), fill=col + (int(255 * ta),))
            if r["kind"] == "ex":
                d.rounded_rectangle((x - 10, y - 8, 1880, y + r["h"] - 8), radius=16, fill=(70, 50, 5, int(150 * ta)),
                                    outline=AMBER + (int(200 * ta),), width=2)
                paste_center(im, R.bulb(int(fs * 1.25)), (x + 28, y + r["h"] / 2 - 8), 1, ta)
                x += 70; y += 5
            newest = k == len(shown) - 1 and fade == 1.0
            hc = (255, 225, 160) if r["kind"] == "ex" else (WHITE if newest else (200, 210, 238))
            for ln in r["hl"]:
                txt(im, (x, y), ln, F("Inter-SemiBold" if r["kind"] == "pt" else "Inter-MediumItalic", fs), hc, alpha=ta); y += fs * 1.3
            for ln in r["sl"]:
                txt(im, (x, y), ln, F("Inter-Regular", int(fs * 0.85)), DIM, alpha=ta); y += fs * 0.85 * 1.3

    # ---- hook / recap / outro
    def draw_hook(self, t):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        C = self.S.CHAPTER
        # tomato price tag flipping between ₹20 and ₹200, tomatoes raining
        for k in range(14):
            x = 120 + (k * 137) % 1700; y = ((t * 90 + k * 211) % 1300) - 150
            put(im, "🍅", (x, y), 60 + (k % 3) * 20, 0.25)
        l1, l2 = C["hook_en"].split("\n")
        f = F("InterDisplay-Black", 76)
        k = 0
        for ln, col, yy in ((l1, WHITE, 300), (l2, GOLD, 410)):
            x = 960 - f.getlength(ln) / 2
            for w in ln.split():
                a = ease_out((t - (0.5 + k * 0.3)) / 0.4)
                if a > 0: glow_text(im, (x, yy + 18 * (1 - a)), w, f, col, glow=col if col == GOLD else None, alpha=a, radius=12)
                x += f.getlength(w + " "); k += 1
            k += 2
        a = ease_out((t - 5.0) / 0.8)
        if a > 0:
            cheap = int(t * 1.2) % 2 == 0
            tag(im, d, (960, 640), "₹20 / kg" if cheap else "₹200 / kg", GREEN if cheap else RED, 64, a)
            put(im, "🍅", (720, 640), 120, a); put(im, "🍅", (1200, 640), 120, a)
        a = ease_out((t - 7.0) / 0.8)
        if a > 0: txt(im, (960, 800), C["hook_hi"], F("deva", 46), DIM, alpha=a, anchor="mm")
        return im

    def draw_recap(self, t):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        a = ease_out((t - self.t_recap) / 0.6)
        txt(im, (960, 120), "RECAP", F("InterDisplay-Black", 72), GOLD, alpha=a, anchor="mm")
        y = 220
        for te, e in self.ev:
            if not e.startswith("recap:"): continue
            tid, _, body = e.split(":", 1)[1].partition("|")
            u = ease_out((t - te) / 0.5)
            if u <= 0: y += 160; continue
            tp = self.topic[tid]; x = 250 + 40 * (1 - u)
            d.rounded_rectangle((x - 20, y, 1680, y + 130), radius=30, fill=(22, 32, 64, int(230 * u)), outline=ACC + (int(150 * u),), width=2)
            put(im, tp["icon"], (x + 60, y + 65), 80, u)
            txt(im, (x + 140, y + 22), tp["name"], F("InterDisplay-Bold", 40), WHITE, alpha=u)
            txt(im, (x + 140, y + 78), body, F("Inter-Medium", 28), DIM, alpha=u)
            y += 160
        return im

    def draw_outro(self, t):
        nxt = next((tp["id"] for tp in self.S.TOPICS if tp["id"] not in self.points), None)
        im = self.draw_map(t, done=tuple(self.points), pulse=nxt)
        d = ImageDraw.Draw(im, "RGBA")
        a = ease_out((t - self.t_outro - 0.5) / 0.6)
        otext = next(e for _, e in self.ev if e.startswith("outro:")).split(":", 1)[1]
        d.rectangle((0, 940, W, 1080), fill=(5, 8, 18, int(220 * a)))
        glow_text(im, (960, 1010), otext, F("InterDisplay-Black", 54), GOLD, glow=GOLD, anchor="mm", alpha=a, radius=10)
        # salt vs smartphone teaser
        b = ease_out((t - self.t_outro - 2) / 0.6)
        if b > 0:
            i1, i2 = self.S.CHAPTER.get("outro_icons", ("🧂", "📱"))
            put(im, i1, (330, 1008), 90, b); put(im, i2, (1590, 1008), 90, b)
        return im

    def zoom(self, mp, board, p, u):
        z = 1 + 2.2 * u
        cx, cy = lerp((960, 540), p, u); w, h = W / z, H / z
        cx = min(max(cx, w / 2), W - w / 2); cy = min(max(cy, h / 2), H - h / 2)
        crop = mp.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((W, H), Image.BILINEAR)
        b = ease((u - 0.45) / 0.55)
        return Image.blend(crop, board, b) if b > 0 else crop

    def frame(self, t):
        tc = self.t_of("center") or 0
        if t < tc: return self.draw_hook(t)
        if t < tc + 0.8: return Image.blend(self.draw_hook(t), self.draw_map(t), ease((t - tc) / 0.8))
        if self.t_outro and t >= self.t_outro:
            u = ease((t - self.t_outro) / 0.7); im = self.draw_outro(t)
            if u < 1: im = Image.blend(self.draw_recap(t), im, u)
            f = ease((t - (self.total - 1.2)) / 1.2)
            return Image.blend(im, Image.new("RGB", (W, H)), f) if f > 0 else im
        if self.t_recap and t >= self.t_recap:
            u = ease((t - self.t_recap) / 0.7); im = self.draw_recap(t)
            if u < 1:
                tf, tid = self.focus_list[-1]; im = Image.blend(self.draw_board(t, tid, tf + 2.6), im, u)
            return im
        cur = [(tf, tid) for tf, tid in self.focus_list if tf <= t]
        if not cur: return self.draw_map(t)
        k = len(cur) - 1; tf, tid = cur[-1]
        done = tuple(x for _, x in self.focus_list[:k])
        T_out = 0.6 if k else 0.0; T_hl, T_in = T_out + 1.7, T_out + 2.5
        a = t - tf
        if a < T_out:
            ptf, ptid = self.focus_list[k - 1]
            return self.zoom(self.draw_map(t, done=done), self.draw_board(t, ptid, ptf + 2.6), self.pos[ptid], 1 - ease(a / T_out))
        if a < T_hl:
            return self.draw_map(t, hl=tid, hl_u=(a - T_out) / 0.8, done=done, dim=ease((a - T_out) / 0.5))
        if a < T_in:
            u = ease((a - T_hl) / (T_in - T_hl))
            return self.zoom(self.draw_map(t, hl=tid, hl_u=1, done=done, dim=1), self.draw_board(t, tid, tf + T_in), self.pos[tid], u)
        return self.draw_board(t, tid, tf + T_in)


def seg_worker(args):
    mod, f0, f1, path = args
    global BG
    BG = make_bg(); fl = Film(mod)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(fl.frame(f / FPS).tobytes())
    p.stdin.close(); p.wait(); return path


def main():
    mod, name = sys.argv[1], sys.argv[2]
    out = os.path.join(HERE, "out", mod)
    total = json.load(open(os.path.join(out, "timeline.json")))["total"]
    nf = int(total * FPS); P = 4; cuts = [nf * k // P for k in range(P + 1)]
    with Pool(P) as pool:
        segs = pool.map(seg_worker, [(mod, cuts[k], cuts[k + 1], os.path.join(out, f"seg{k}.mp4")) for k in range(P)])
    lst = os.path.join(out, "segs.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    vid = os.path.join(out, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    R.HERE = HERE
    wav = os.path.join(out, "mix.wav"); R.audio_mix(mod, total, wav)
    final = os.path.join(HERE, "out", name)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", wav, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
    print("wrote", final)


if __name__ == "__main__":
    if sys.argv[1] == "--still":
        BG = make_bg(); fl = Film(sys.argv[2])
        ims = [fl.frame(float(x)).resize((640, 360)) for x in sys.argv[3].split(",")]
        sheet = Image.new("RGB", (640 * 3, 360 * ((len(ims) + 2) // 3)))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(sys.argv[4])
    else:
        main()
