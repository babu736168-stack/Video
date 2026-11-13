"""Art for "The Stylish Monkey and the Joker's Terrible Day".

All drawing goes through SD, a small wrapper that scales and offsets
coordinates, so the same character code draws in the scene (k=1) and
larger on the cast cards.
"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
GROUND = 660      # front of platform: where main characters stand
BACK = 580        # back of platform: where passengers stand
ROOF = 238        # top of the train roof
OL = (28, 24, 30)
FD = "/usr/share/fonts/opentype/inter/"

FUR, FACE = (125, 78, 42), (228, 188, 142)
SKIN_J = (245, 210, 175)


@lru_cache(maxsize=128)
def font(name, size):
    return ImageFont.truetype(FD + name, size)


class SD:
    """Scaled draw: maps scene coordinates to canvas coordinates."""

    def __init__(self, d, k=1.0, ox=0.0, oy=0.0):
        self.d, self.k, self.ox, self.oy = d, k, ox, oy

    def P(self, xy):
        if isinstance(xy[0], (tuple, list)):
            return [(self.ox + x * self.k, self.oy + y * self.k) for x, y in xy]
        return [self.ox + v * self.k if i % 2 == 0 else self.oy + v * self.k for i, v in enumerate(xy)]

    def w(self, width):
        return max(1, int(round(width * self.k)))

    @staticmethod
    def _box(b):
        x0, y0, x1, y1 = b
        return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(self._box(self.P(xy)), fill=fill, outline=outline, width=self.w(width))

    def circle(self, cx, cy, r, fill=None, outline=None, width=1):
        self.ellipse((cx - r, cy - r, cx + r, cy + r), fill, outline, width)

    def rect(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(self._box(self.P(xy)), fill=fill, outline=outline, width=self.w(width))

    def rrect(self, xy, r, fill=None, outline=None, width=1):
        b = self._box(self.P(xy))
        r = min(r * self.k, (b[2] - b[0]) / 2, (b[3] - b[1]) / 2)
        self.d.rounded_rectangle(b, radius=max(0, r), fill=fill, outline=outline, width=self.w(width))

    def line(self, pts, fill, width=1):
        self.d.line(self.P(pts), fill=fill, width=self.w(width), joint="curve")

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(self.P(pts), fill=fill, outline=outline, width=self.w(width))

    def arc(self, xy, a0, a1, fill, width=1):
        self.d.arc(self._box(self.P(xy)), a0, a1, fill=fill, width=self.w(width))

    def chord(self, xy, a0, a1, fill=None, outline=None, width=1):
        self.d.chord(self._box(self.P(xy)), a0, a1, fill=fill, outline=outline, width=self.w(width))

    def text(self, xy, s, size, fill, name="Inter-Black.otf", anchor="mm", stroke=0, sfill=OL):
        self.d.text(tuple(self.P(xy)), s, font=font(name, max(6, int(size * self.k))), fill=fill,
                    anchor=anchor, stroke_width=self.w(stroke) if stroke else 0, stroke_fill=sfill)


def limb(sd, pts, color, w):
    sd.line(pts, OL, w + 6)
    for x, y in (pts[0], pts[-1]):
        sd.circle(x, y, (w + 6) / 2, fill=OL)
    sd.line(pts, color, w)
    for x, y in pts:
        sd.circle(x, y, w / 2, fill=color)


def splat(sd, x, y, r, color, rng):
    for _ in range(7):
        a = rng.random() * 6.28
        d = rng.random() * r * 0.8
        rr = r * (0.3 + 0.35 * rng.random())
        sd.circle(x + math.cos(a) * d, y + math.sin(a) * d, rr, fill=color)
    sd.circle(x, y, r * 0.7, fill=color)


def egg_mess(sd, x, y, r=16, seed=0):
    rng = random.Random(seed)
    splat(sd, x, y, r * 1.3, (250, 250, 240), rng)
    sd.circle(x + 2, y - 1, r * 0.55, fill=(255, 190, 20), outline=(220, 140, 0), width=2)
    for k in range(3):
        dx = rng.randint(-int(r), int(r))
        sd.line([(x + dx, y + r * 0.4), (x + dx, y + r * (1.4 + rng.random()))], (255, 210, 60), 5)
        sd.circle(x + dx, y + r * 1.8, 4, fill=(255, 210, 60))


# ====================================================================== JOKER
JW, JH, JAX, JAY = 440, 440, 220, 430   # joker canvas size and ground anchor


def joker_hands(st, t):
    c = st.get("crouch", 0)
    p = st.get("pose", "idle")
    sw = st.get("swing", 0)
    sh = st.get("shake", 0)
    table = {
        "carry": ((150, 315 + c + sw), (290, 315 + c - sw)),
        "hips": ((168, 285 + c), (272, 285 + c)),
        "point": ((95, 95 + c), (232, 262 + c)),
        "head": ((150, 300 + c), (252, 88 + c)),
        "look_hand": ((150, 300 + c), (288, 170 + c)),
        "fists": ((148, 150 + c + 6 * math.sin(t * 25)), (292, 150 + c - 6 * math.sin(t * 25))),
        "pocket": ((150, 300 + c), (250, 282 + c)),
        "place": ((150, 353), (288, 300 + c)),
        "reach": ((192, 300 + c), st.get("target", (288, 300 + c))),
        "hold": ((150, 300 + c), (288, 288 + c)),
        "windup": ((150, 300 + c), (160, 68 + c)),
        "throw": ((150, 300 + c), (352, 108 + c)),
        "idle": ((155, 305 + c), (285, 305 + c)),
        "droop": ((168, 335 + c), (272, 335 + c)),
        "wipe": ((150, 300 + c), (242 + 14 * math.sin(t * 14), 168 + c)),
        "hat_hold": ((182 + sh, 92 + c), (258 + sh, 92 + c)),
        "throw_left": ((70, 165 + c), (285, 305 + c)),
        "plead": ((172 + 12 * math.sin(t * 12), 232 + c), (268 - 12 * math.sin(t * 12), 232 + c)),
        "flail": ((120 + 25 * math.sin(t * 22), 110 + 20 * math.cos(t * 19)),
                  (320 + 25 * math.cos(t * 22), 110 + 20 * math.sin(t * 17))),
        "slump_carry": ((168, 338 + c + sw), (272, 338 + c - sw)),
    }
    return table.get(p, table["idle"])


def joker_face(sd, cx, cy, face, talk, glasses, t):
    # eyebrows
    brows = {
        "smile": (-4, 0), "laugh": (-10, 0), "shock": (-16, 0), "disgust": (0, 8), "angry": (4, -12),
        "horror": (-18, 10), "sad": (-2, 12), "nervous": (-8, 10), "wince": (2, -6), "grin": (0, -8),
        "broken": (0, 12), "focus": (2, -8),
    }.get(face, (0, 0))
    lift, tilt = brows
    for s in (-1, 1):
        x0, x1 = cx + s * 40, cx + s * 10
        y0 = cy - 36 + lift + (tilt if s == -1 else tilt) * 0.5
        y1 = cy - 36 + lift - tilt * 0.5
        sd.line([(x0, y0), (x1, y1)], OL, 6)
    # oversized sunglasses
    dyL, dyR = (7, -3) if glasses in ("crooked", "broken") else (0, 0)
    lenses = [(cx - 42, cy - 22 + dyL, cx - 4, cy + 10 + dyL), (cx + 4, cy - 22 + dyR, cx + 42, cy + 10 + dyR)]
    for b in lenses:
        sd.ellipse(b, fill=(20, 20, 28), outline=(255, 60, 140), width=4)
        sd.arc((b[0] + 6, b[1] + 4, b[2] - 10, b[3] - 8), 200, 260, (200, 200, 230), 3)
    sd.line([(cx - 4, cy - 8 + dyL), (cx + 4, cy - 8 + dyR)], (255, 60, 140), 4)
    if glasses == "broken":
        bx0, by0, bx1, by1 = lenses[1]
        mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
        for a in (0.3, 1.6, 2.9, 4.2):
            sd.line([(mx, my), (mx + 16 * math.cos(a), my + 14 * math.sin(a))], (230, 230, 240), 2)
    # red nose
    sd.circle(cx, cy + 16, 10, fill=(230, 30, 40), outline=OL, width=3)
    sd.circle(cx - 3, cy + 12, 3, fill=(255, 170, 170))
    # cheeks
    sd.circle(cx - 32, cy + 26, 8, fill=(255, 160, 170))
    sd.circle(cx + 32, cy + 26, 8, fill=(255, 160, 170))
    my = cy + 33
    if talk:
        sd.ellipse((cx - 14, my - 8, cx + 14, my + 14), fill=(130, 20, 40), outline=OL, width=3)
    elif face in ("smile", "grin"):
        sd.chord((cx - 22, my - 14, cx + 22, my + 12), 0, 180, fill=(255, 255, 255), outline=OL, width=3)
    elif face == "laugh":
        sd.chord((cx - 24, my - 14, cx + 24, my + 22), 0, 180, fill=(130, 20, 40), outline=OL, width=3)
        sd.chord((cx - 10, my + 4, cx + 10, my + 20), 0, 180, fill=(240, 100, 120))
    elif face in ("shock", "horror"):
        h = 18 if face == "shock" else 26
        sd.ellipse((cx - 13, my - 8, cx + 13, my - 8 + h * 1.4), fill=(110, 15, 30), outline=OL, width=3)
    elif face == "disgust":
        sd.line([(cx - 20, my), (cx - 10, my - 5), (cx, my), (cx + 10, my - 5), (cx + 20, my)], OL, 4)
        sd.chord((cx - 2, my - 4, cx + 14, my + 14), 0, 180, fill=(240, 100, 120), outline=OL, width=2)
    elif face in ("angry", "focus"):
        sd.rect((cx - 18, my - 6, cx + 18, my + 8), fill=(255, 255, 255), outline=OL, width=3)
        sd.line([(cx - 18, my + 1), (cx + 18, my + 1)], OL, 2)
    elif face == "nervous":
        sd.rect((cx - 20, my - 6, cx + 20, my + 8), fill=(255, 255, 255), outline=OL, width=3)
        for x in (-10, 0, 10):
            sd.line([(cx + x, my - 6), (cx + x, my + 8)], OL, 2)
        sd.ellipse((cx + 40, cy - 40, cx + 52, cy - 20), fill=(140, 200, 255), outline=OL, width=2)
    elif face == "wince":
        sd.line([(cx - 16, my + 4), (cx - 6, my - 4), (cx + 6, my + 4), (cx + 16, my - 4)], OL, 4)
    else:  # sad / broken
        sd.arc((cx - 18, my, cx + 18, my + 22), 200, 340, OL, 5)
        if face == "broken":
            for k in range(3):
                a = t * 5 + k * 2.1
                sd.circle(cx + 50 * math.cos(a), cy - 70 + 10 * math.sin(a), 5, fill=(255, 220, 60))


def draw_joker(sd, t, st):
    c = st.get("crouch", 0)
    lx, ly = st.get("look", (0, 0))
    L, R = joker_hands(st, t)
    coat = (128, 62, 178)
    dust = st.get("dust", False)
    if dust:
        coat = (125, 100, 110)
    # legs: striped trousers
    for hx, fx in ((205, 195), (235, 245)):
        knee = (hx + (hx - 220) * c / 18, 370 + c * 0.4)
        pts = [(hx, 312 + c), knee, (fx, 412)]
        limb(sd, pts, (250, 250, 250) if not dust else (205, 195, 180), 26)
        for off in (-7, 7):
            sd.line([(p[0] + off, p[1]) for p in pts], (220, 40, 60), 4)
    sd.ellipse((160, 402, 214, 428), fill=(225, 30, 40), outline=OL, width=4)
    sd.ellipse((226, 402, 280, 428), fill=(225, 30, 40), outline=OL, width=4)
    # back arm first
    limb(sd, [(178, 208 + c), L], coat, 15)
    # torso: patchwork coat
    sd.rrect((172, 190 + c, 268, 320 + c), 18, fill=coat, outline=OL, width=4)
    sd.rect((178, 252 + c, 204, 276 + c), fill=(60, 190, 90) if not dust else (130, 120, 100))
    sd.rect((236, 282 + c, 262, 308 + c), fill=(255, 140, 30) if not dust else (150, 120, 90))
    sd.rect((236, 224 + c, 258, 244 + c), fill=(40, 160, 230) if not dust else (120, 120, 120))
    sd.poly([(204, 192 + c), (236, 192 + c), (220, 248 + c)], fill=(255, 220, 30))
    for y in (262, 286, 306):
        sd.circle(220, y + c, 4, fill=(255, 220, 30), outline=OL, width=1)
    # huge red bow tie
    sd.poly([(220, 214 + c), (170, 194 + c), (170, 236 + c)], fill=(225, 25, 40), outline=OL, width=3)
    sd.poly([(220, 214 + c), (270, 194 + c), (270, 236 + c)], fill=(225, 25, 40), outline=OL, width=3)
    sd.circle(220, 214 + c, 11, fill=(200, 15, 30), outline=OL, width=3)
    for x in (184, 196, 244, 256):
        sd.circle(x, 214 + c + (x % 3) * 4 - 4, 3, fill=(255, 255, 255))
    # head
    hx, hy = 220, 140 + c
    sd.ellipse((hx - 66, hy - 24, hx - 30, hy + 20), fill=(255, 120, 20), outline=OL, width=3)   # clown hair
    sd.ellipse((hx + 30, hy - 24, hx + 66, hy + 20), fill=(255, 120, 20), outline=OL, width=3)
    sd.circle(hx, hy, 46, fill=SKIN_J if not dust else (200, 175, 150), outline=OL, width=4)
    joker_face(sd, hx + lx, hy + ly, st.get("face", "smile"), st.get("talk", False), st.get("glasses", "ok"), t)
    # hat
    if st.get("hat", "on") == "on":
        draw_hat(sd, hx + lx * 0.4, hy - 46 + ly * 0.3, st.get("egg", 0) >= 2, st.get("poop", False))
    elif st.get("hat") == "held":
        mx, my = (L[0] + R[0]) / 2, (L[1] + R[1]) / 2
        draw_hat(sd, mx, my + 10, st.get("egg", 0) >= 2, False)
    # egg & dust mess
    egg = st.get("egg", 0)
    if egg >= 1:
        egg_mess(sd, hx + 26 + lx, hy + 12, 16, seed=1)
    if egg >= 3:
        egg_mess(sd, 198, 262 + c, 15, seed=3)
    if dust:
        rng = random.Random(9)
        for _ in range(45):
            x, y = rng.uniform(165, 275), rng.uniform(95, 420)
            sd.circle(x, y + (c if y < 320 else 0), rng.uniform(2, 6), fill=(140, 110, 80))
    # front arm
    limb(sd, [(262, 208 + c), R], coat, 15)
    for hand in (L, R):
        sd.circle(hand[0], hand[1], 12, fill=(255, 255, 255), outline=OL, width=3)
    # carried luggage
    if st.get("pose") in ("carry", "slump_carry"):
        draw_suitcase(sd, L[0], L[1] + 42, big=True)
        draw_bag(sd, R[0], R[1] + 30)


def draw_hat(sd, cx, base, eggy=False, poop=False):
    """cx = centre, base = y of the brim."""
    sd.poly([(cx + 20, base - 8), (cx + 46, base - 60), (cx + 80, base - 96), (cx + 58, base - 48)],
            fill=(255, 70, 160), outline=OL, width=2)                                  # feather
    sd.line([(cx + 22, base - 10), (cx + 76, base - 92)], (180, 20, 100), 2)
    sd.rrect((cx - 38, base - 58, cx + 38, base + 4), 14, fill=(255, 215, 40), outline=OL, width=4)
    sd.rect((cx - 38, base - 16, cx + 38, base - 4), fill=(225, 30, 40))
    sd.ellipse((cx - 62, base - 6, cx + 62, base + 12), fill=(255, 215, 40), outline=OL, width=4)
    if eggy:
        egg_mess(sd, cx - 8, base - 34, 18, seed=2)
    if poop:
        rng = random.Random(4)
        splat(sd, cx + 4, base - 58, 14, (245, 245, 235), rng)
        sd.circle(cx + 6, base - 60, 6, fill=(160, 150, 120))
        sd.line([(cx - 8, base - 50), (cx - 10, base - 30)], (245, 245, 235), 5)


def draw_suitcase(sd, cx, cy, big=True):
    w, h = (80, 70) if big else (50, 42)
    sd.rrect((cx - 14, cy - h / 2 - 12, cx + 14, cy - h / 2 + 2), 5, outline=OL, width=4)
    sd.rrect((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 8, fill=(40, 120, 200), outline=OL, width=4)
    sd.rect((cx - w / 2 + 10, cy - h / 2, cx - w / 2 + 18, cy + h / 2), fill=(250, 200, 40))
    sd.circle(cx + 14, cy + 4, 9, fill=(255, 90, 90))
    sd.rect((cx - 6, cy + 10, cx + 26, cy + 22), fill=(255, 255, 255))


def draw_bag(sd, cx, cy):
    sd.arc((cx - 16, cy - 36, cx + 16, cy - 6), 180, 360, OL, 5)
    sd.rrect((cx - 25, cy - 21, cx + 25, cy + 21), 10, fill=(220, 50, 60), outline=OL, width=4)
    sd.line([(cx - 25, cy - 4), (cx + 25, cy - 4)], (255, 220, 60), 4)


def joker_sprite(t, st):
    im = Image.new("RGBA", (JW, JH), (0, 0, 0, 0))
    draw_joker(SD(ImageDraw.Draw(im)), t, st)
    return im


# ====================================================================== MONKEY
def monkey_head(sd, x, y, st, t):
    glasses = st.get("glasses", "on")
    mouth = st.get("mouth", "smile")
    for s in (-1, 1):
        sd.circle(x + s * 27, y - 2, 11, fill=FUR, outline=OL, width=3)
        sd.circle(x + s * 27, y - 2, 6, fill=FACE)
    sd.circle(x, y, 26, fill=FUR, outline=OL, width=3)
    sd.ellipse((x - 20, y - 14, x + 20, y + 22), fill=FACE)
    sd.ellipse((x - 14, y + 6, x + 14, y + 24), fill=(238, 200, 158))
    gy = 7 if glasses == "down" else 0
    if glasses == "down":
        for s in (-1, 1):
            sd.circle(x + s * 9, y - 9, 6, fill=(255, 255, 255), outline=OL, width=2)
            sd.circle(x + s * 9 + 1, y - 8, 3, fill=OL)
            sd.line([(x + s * 4, y - 20), (x + s * 15, y - 22)], OL, 3)
    sd.rrect((x - 21, y - 8 + gy, x - 2, y + 4 + gy), 4, fill=(15, 15, 20), outline=OL, width=2)
    sd.rrect((x + 2, y - 8 + gy, x + 21, y + 4 + gy), 4, fill=(15, 15, 20), outline=OL, width=2)
    sd.line([(x - 21, y - 5 + gy), (x - 27, y - 7 + gy)], (15, 15, 20), 3)
    sd.line([(x + 21, y - 5 + gy), (x + 27, y - 7 + gy)], (15, 15, 20), 3)
    sd.line([(x - 16, y - 6 + gy), (x - 10, y - 6 + gy)], (120, 120, 140), 2)
    sd.circle(x - 4, y + 9, 2, fill=OL)
    sd.circle(x + 4, y + 9, 2, fill=OL)
    if mouth == "grin":
        sd.chord((x - 13, y + 8, x + 13, y + 24), 0, 180, fill=(255, 255, 255), outline=OL, width=2)
    elif mouth in ("bite", "talk"):
        sd.ellipse((x - 7, y + 11, x + 7, y + 23), fill=(120, 30, 40), outline=OL, width=2)
    else:
        sd.arc((x - 10, y + 6, x + 10, y + 20), 20, 160, OL, 3)


def banana(sd, x, y, frac=1.0, up=False):
    span = 110 * max(0.15, frac)
    a0 = 200 if not up else 250
    sd.arc((x - 6, y - 34, x + 30, y + 2), a0, a0 + span, (255, 220, 40), 9)
    sd.arc((x - 6, y - 34, x + 30, y + 2), a0, a0 + span, (180, 140, 0), 2)
    sd.circle(x, y - 2, 4, fill=(110, 80, 20))


def shirt_dots(sd, box, seed=1):
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(9):
        sd.circle(rng.uniform(x0 + 6, x1 - 6), rng.uniform(y0 + 6, y1 - 6), 3.5,
                  fill=rng.choice([(255, 230, 60), (255, 110, 160), (255, 255, 255)]))


SHIRT = (0, 170, 175)


def draw_monkey(sd, x, y, pose, t, st):
    if pose == "lie":
        bob = 3 * math.sin(t * 2 * math.pi * 1.6)
        wag = 5 * math.sin(t * 2 * math.pi * 1.6)
        sd.arc((x + 28, y - 30, x + 80, y + 22), 200, 330, FUR, 7)                      # tail
        limb(sd, [(x + 38, y - 14), (x + 62, y - 52), (x + 84, y - 8)], FUR, 12)        # bent leg
        sd.ellipse((x + 76, y - 14, x + 98, y - 1), fill=FACE, outline=OL, width=2)
        limb(sd, [(x + 40, y - 20), (x + 64, y - 52), (x + 102, y - 58 + wag)], FUR, 12)  # crossed leg
        sd.ellipse((x + 98, y - 66 + wag, x + 118, y - 50 + wag), fill=FACE, outline=OL, width=2)
        sd.rrect((x + 16, y - 36, x + 52, y - 4), 10, fill=(225, 35, 45), outline=OL, width=3)
        sd.rrect((x - 42, y - 40, x + 28, y - 2), 16, fill=SHIRT, outline=OL, width=3)
        shirt_dots(sd, (x - 42, y - 40, x + 28, y - 2))
        limb(sd, [(x - 32, y - 32), (x - 62, y - 70 + bob)], FUR, 10)                    # arm behind head
        monkey_head(sd, x - 58, y - 46 + bob, st, t)
        if st.get("banana") is not None:
            bx, by = x - 30, y - 60 + bob + (6 if st.get("mouth") == "bite" else 0)
            limb(sd, [(x - 18, y - 26), (bx, by)], FUR, 10)
            banana(sd, bx - 2, by, st["banana"])
            sd.circle(bx, by, 6, fill=FACE, outline=OL, width=2)
        else:
            limb(sd, [(x - 18, y - 26), (x + 4, y - 30)], FUR, 10)
        return (x - 58, y - 75 + bob)
    if pose == "sit":
        sd.arc((x + 10, y - 60, x + 70, y + 4), 270, 80, FUR, 7)
        sd.ellipse((x - 44, y - 26, x + 44, y), fill=FUR, outline=OL, width=3)
        sd.circle(x - 42, y - 12, 9, fill=FACE, outline=OL, width=2)
        sd.circle(x + 42, y - 12, 9, fill=FACE, outline=OL, width=2)
        sd.rrect((x - 28, y - 36, x + 28, y - 14), 8, fill=(225, 35, 45), outline=OL, width=3)
        sd.rrect((x - 27, y - 84, x + 27, y - 30), 14, fill=SHIRT, outline=OL, width=3)
        shirt_dots(sd, (x - 27, y - 84, x + 27, y - 30), 2)
        arm = st.get("arm", "rest")
        limb(sd, [(x - 22, y - 74), (x - 36, y - 34)], FUR, 10)
        sd.circle(x - 36, y - 34, 6, fill=FACE)
        monkey_head(sd, x, y - 108, st, t)
        hand = {"rest": (x + 34, y - 48), "glasses": (x + 16, y - 116), "trophy": (x + 40, y - 165),
                "five": (x - 70, y - 120), "bite": (x + 6, y - 92)}[arm]
        limb(sd, [(x + 22, y - 74), hand], FUR, 10)
        if st.get("banana") is not None and arm != "glasses":
            banana(sd, hand[0] - 4, hand[1], st["banana"], up=arm == "trophy")
        sd.circle(hand[0], hand[1], 7, fill=FACE, outline=OL, width=2)
        if arm == "five":
            for a in (-0.9, -0.5, -0.1, 0.3):
                sd.line([hand, (hand[0] + 14 * math.cos(math.pi + a), hand[1] + 14 * math.sin(math.pi + a))], FACE, 4)
        return (x, y - 138)
    # standing / sneaking on tiptoe
    f = st.get("face_dir", 1)
    step = 8 * math.sin(t * 22) if st.get("moving") else 0
    sd.arc((x - f * 55, y - 110, x - f * 5, y - 40), 180 if f > 0 else 270, 300 if f > 0 else 0, FUR, 7)
    limb(sd, [(x - 9, y - 36), (x - 12 + step, y - 4)], FUR, 11)
    limb(sd, [(x + 9, y - 36), (x + 12 - step, y - 4)], FUR, 11)
    sd.rrect((x - 22, y - 48, x + 22, y - 28), 8, fill=(225, 35, 45), outline=OL, width=3)
    sd.rrect((x - 22, y - 88, x + 22, y - 44), 12, fill=SHIRT, outline=OL, width=3)
    shirt_dots(sd, (x - 22, y - 88, x + 22, y - 44), 3)
    monkey_head(sd, x + f * 4, y - 110, st, t)
    limb(sd, [(x - f * 14, y - 80), (x + f * 2, y - 100)], FUR, 9)        # "shhh" finger at lips
    hand = (x + f * 34, y - 62)
    limb(sd, [(x + f * 16, y - 80), hand], FUR, 9)
    item = st.get("item")
    if item == "stone":
        draw_stone(sd, hand[0] + f * 6, hand[1])
    elif item == "phone":
        draw_phone(sd, hand[0] + f * 6, hand[1])
    sd.circle(hand[0], hand[1], 6, fill=FACE, outline=OL, width=2)
    return (x, y - 140)


def draw_stone(sd, x, y):
    sd.ellipse((x - 14, y - 9, x + 14, y + 9), fill=(140, 140, 135), outline=OL, width=3)
    sd.arc((x - 9, y - 6, x + 3, y + 2), 200, 280, (200, 200, 195), 2)


def draw_phone(sd, x, y, ang=0.0):
    c, s = math.cos(ang), math.sin(ang)
    def rot(px, py):
        return (x + px * c - py * s, y + px * s + py * c)
    sd.poly([rot(-9, -15), rot(9, -15), rot(9, 15), rot(-9, 15)], fill=(20, 20, 25), outline=OL, width=2)
    sd.poly([rot(-6, -11), rot(6, -11), rot(6, 10), rot(-6, 10)], fill=(80, 170, 255))


# ====================================================================== BIRD
def draw_bird(sd, x, y, t, flying=False, facing=1, wing_up=False):
    f = facing
    sd.poly([(x - f * 12, y), (x - f * 30, y - 6), (x - f * 28, y + 8)], fill=(40, 90, 190), outline=OL, width=2)
    sd.ellipse((x - 16, y - 12, x + 16, y + 10), fill=(60, 145, 235), outline=OL, width=3)
    sd.ellipse((x - 6, y - 2, x + 12, y + 9), fill=(250, 245, 220))
    sd.circle(x + f * 13, y - 12, 10, fill=(60, 145, 235), outline=OL, width=3)
    sd.circle(x + f * 16, y - 14, 3.5, fill=(255, 255, 255))
    sd.circle(x + f * 17, y - 14, 2, fill=OL)
    sd.poly([(x + f * 21, y - 13), (x + f * 32, y - 9), (x + f * 21, y - 6)], fill=(255, 150, 20), outline=OL, width=1)
    if flying or wing_up:
        flap = -1 if wing_up else math.sin(t * 32)
        sd.poly([(x - 8, y - 6), (x + 8, y - 6), (x - 4 * f, y - 6 - 24 * flap)], fill=(40, 100, 200), outline=OL, width=2)
    else:
        sd.ellipse((x - 10, y - 6, x + 8, y + 4), fill=(40, 100, 200), outline=OL, width=2)
        sd.line([(x - 4, y + 9), (x - 5, y + 14)], (255, 150, 20), 3)
        sd.line([(x + 4, y + 9), (x + 5, y + 14)], (255, 150, 20), 3)


# ====================================================================== EGG SELLER
SELLER_X = 1065


def draw_seller(sd, t, st):
    x = SELLER_X
    sh = st.get("shake", 0)
    face = st.get("face", "calm")
    skin = (200, 145, 100)
    # arms behind torso when arranging
    pose = st.get("pose", "arrange")
    hands = {
        "arrange": ((x - 34 + 6 * math.sin(t * 3), 524), (x + 36, 520 + 4 * math.sin(t * 4))),
        "rub": ((x - 34, 525), (x + 20, 372)),
        "windup": ((x - 34, 525), (x + 62, 372)),
        "release": ((x - 34, 525), (x - 62, 430)),
        "fists": ((x - 50, 470), (x + 50, 470)),
        "laugh": ((x - 26, 505), (x + 26, 505)),
    }[pose]
    sd.rrect((x - 44, 440, x + 44, 570), 20, fill=(250, 250, 245), outline=OL, width=3)
    sd.poly([(x - 44, 450), (x - 10, 450), (x - 8, 540), (x - 44, 540)], fill=(40, 140, 90), outline=OL, width=2)
    sd.poly([(x + 44, 450), (x + 10, 450), (x + 8, 540), (x + 44, 540)], fill=(40, 140, 90), outline=OL, width=2)
    hx = x + sh
    sd.rect((x - 12, 418, x + 12, 444), fill=skin, outline=OL, width=3)
    sd.circle(hx, 405, 32, fill=skin, outline=OL, width=3)
    sd.chord((hx - 30, 368, hx + 30, 410), 180, 360, fill=(255, 255, 255), outline=OL, width=3)   # topi
    lx = st.get("look", 0)
    ex = hx + lx
    if face == "laugh":
        for s in (-1, 1):
            sd.arc((ex + s * 12 - 6, 396, ex + s * 12 + 6, 406), 180, 360, OL, 3)
    else:
        for s in (-1, 1):
            sd.circle(ex + s * 12, 401, 4 if face != "ouch" else 2, fill=OL)
    if face in ("angry",):
        sd.line([(ex - 20, 388), (ex - 5, 395)], OL, 4)
        sd.line([(ex + 20, 388), (ex + 5, 395)], OL, 4)
    elif face in ("ouch", "confused"):
        sd.line([(ex - 20, 392), (ex - 5, 386)], OL, 3)
        sd.line([(ex + 20, 386), (ex + 5, 388)], OL, 3)
    sd.chord((ex - 22, 408, ex, 424), 180, 360, fill=OL)            # big moustache
    sd.chord((ex, 408, ex + 22, 424), 180, 360, fill=OL)
    if face == "laugh" or st.get("talk"):
        sd.ellipse((ex - 9, 416, ex + 9, 432), fill=(120, 30, 40), outline=OL, width=2)
    elif face == "angry":
        sd.line([(ex - 9, 424), (ex + 9, 424)], OL, 4)
    elif face in ("ouch", "confused"):
        sd.circle(ex, 425, 5, fill=(120, 30, 40))
    else:
        sd.arc((ex - 9, 414, ex + 9, 428), 20, 160, OL, 3)
    for s, hand in zip((-1, 1), hands):
        limb(sd, [(x + s * 38, 456), hand], (250, 250, 245), 13)
        sd.circle(hand[0], hand[1], 9, fill=skin, outline=OL, width=2)
    if st.get("holding_egg"):
        h = hands[1]
        sd.ellipse((h[0] - 7, h[1] - 18, h[0] + 7, h[1] - 2), fill=(250, 245, 235), outline=OL, width=2)


def draw_stall(sd):
    x = SELLER_X
    sd.line([(x + 110, 548), (x + 110, 420)], (110, 70, 40), 6)
    sd.rrect((x + 52, 392, x + 172, 444), 6, fill=(255, 250, 235), outline=OL, width=3)
    sd.text((x + 112, 408), "ANDE", 20, (200, 30, 40))
    sd.text((x + 112, 430), "EGGS  Rs 6", 14, (40, 40, 40), name="Inter-Bold.otf")
    sd.rect((x - 100, 548, x - 90, GROUND), fill=(110, 70, 40))
    sd.rect((x + 90, 548, x + 100, GROUND), fill=(110, 70, 40))
    sd.rrect((x - 110, 530, x + 110, 552), 4, fill=(160, 100, 50), outline=OL, width=3)
    sd.rect((x - 104, 552, x + 104, 615), fill=(185, 120, 60), outline=OL, width=3)
    for yy in (572, 594):
        sd.line([(x - 104, yy), (x + 104, yy)], (140, 90, 40), 2)
    for row, (y, n, off) in enumerate(((517, 12, 0), (504, 11, 8), (492, 4, 52))):
        for i in range(n):
            ex = x - 92 + off + i * 16.5
            if row == 2:
                ex = x - 92 + off + i * 16.5
            sd.ellipse((ex - 7, y - 9, ex + 7, y + 9), fill=(250, 245, 232), outline=(150, 140, 120), width=1)


# ====================================================================== BODYBUILDER
def draw_bb(sd, x, t, st):
    G = GROUND
    skin = (190, 125, 80)
    pose = st.get("pose", "idle")
    face = st.get("face", "proud")
    # legs + shorts
    for s in (-1, 1):
        sd.rrect((x + s * 30 - 18, G - 125, x + s * 30 + 18, G - 10), 14, fill=skin, outline=OL, width=3)
        sd.ellipse((x + s * 30 - 24, G - 18, x + s * 30 + 24, G + 4), fill=(30, 30, 30), outline=OL, width=3)
    sd.rrect((x - 58, G - 165, x + 58, G - 100), 16, fill=(30, 30, 40), outline=OL, width=4)
    sd.rect((x - 58, G - 165, x + 58, G - 150), fill=(250, 200, 30))
    # arms are posed
    arms = {
        "idle": [((x - 82, G - 268), (x - 108, G - 205), (x - 100, G - 148)),
                 ((x + 82, G - 268), (x + 108, G - 205), (x + 100, G - 148))],
        "flex": [((x - 82, G - 268), (x - 135, G - 262), (x - 118, G - 325)),
                 ((x + 82, G - 268), (x + 135, G - 262), (x + 118, G - 325))],
        "fists": [((x - 82, G - 268), (x - 112, G - 215), (x - 80, G - 190)),
                  ((x + 82, G - 268), (x + 112, G - 215), (x + 80, G - 190))],
        "lift": [((x - 82, G - 268), (x - 78, G - 355), (x - 50, G - 425)),
                 ((x + 82, G - 268), (x + 78, G - 355), (x + 50, G - 425))],
        "throw": [((x - 82, G - 268), (x - 125, G - 320), (x - 165, G - 370)),
                  ((x + 82, G - 268), (x + 20, G - 330), (x - 60, G - 380))],
        "cross": [((x - 82, G - 268), (x - 92, G - 225), (x + 55, G - 222)),
                  ((x + 82, G - 268), (x + 92, G - 240), (x - 55, G - 240))],
    }[pose]
    if pose != "cross":
        for a in arms:
            limb(sd, list(a), skin, 30)
            mx, my = (a[0][0] + a[1][0]) / 2, (a[0][1] + a[1][1]) / 2
            sd.circle(mx, my - 6, 24, fill=skin, outline=OL, width=3)
            sd.circle(a[2][0], a[2][1], 17, fill=skin, outline=OL, width=3)
    # torso
    sd.poly([(x - 84, G - 285), (x + 84, G - 285), (x + 48, G - 160), (x - 48, G - 160)], fill=skin, outline=OL, width=4)
    sd.poly([(x - 52, G - 280), (x + 52, G - 280), (x + 44, G - 162), (x - 44, G - 162)], fill=(210, 30, 40))
    sd.line([(x - 52, G - 280), (x - 40, G - 300)], (210, 30, 40), 10)
    sd.line([(x + 52, G - 280), (x + 40, G - 300)], (210, 30, 40), 10)
    sd.arc((x - 48, G - 285, x, G - 230), 0, 180, (170, 15, 30), 4)
    sd.arc((x, G - 285, x + 48, G - 230), 0, 180, (170, 15, 30), 4)
    sd.text((x, G - 205), "GYM", 22, (255, 220, 60))
    for s in (-1, 1):
        sd.circle(x + s * 82, G - 272, 30, fill=skin, outline=OL, width=3)
    if pose == "cross":
        for a in arms:
            limb(sd, list(a), skin, 30)
        for a in arms:
            sd.circle(a[2][0], a[2][1], 17, fill=skin, outline=OL, width=3)
    # head
    lx = st.get("look", 0)
    sd.rect((x - 22, G - 312, x + 22, G - 282), fill=skin, outline=OL, width=3)
    sd.circle(x, G - 325, 27, fill=skin, outline=OL, width=3)
    sd.rect((x - 26, G - 356, x + 26, G - 338), fill=(25, 25, 25))
    ex = x + lx
    for s in (-1, 1):
        sd.circle(ex + s * 10, G - 327, 3.5, fill=OL)
    if face == "angry":
        sd.line([(ex - 20, G - 342), (ex - 4, G - 334)], OL, 5)
        sd.line([(ex + 20, G - 342), (ex + 4, G - 334)], OL, 5)
        sd.rect((ex - 11, G - 312, ex + 11, G - 304), fill=(255, 255, 255), outline=OL, width=2)
    else:
        sd.line([(ex - 18, G - 338), (ex - 4, G - 338)], OL, 4)
        sd.line([(ex + 18, G - 338), (ex + 4, G - 338)], OL, 4)
        if face == "smile" or st.get("talk"):
            sd.chord((ex - 11, G - 316, ex + 11, G - 300), 0, 180, fill=(255, 255, 255), outline=OL, width=2)
        else:
            sd.line([(ex - 9, G - 307), (ex + 9, G - 309)], OL, 3)
    sd.chord((ex - 16, G - 320, ex + 16, G - 308), 180, 360, fill=(25, 25, 25))


# ====================================================================== PASSENGERS
PASSENGERS = [
    dict(x=95, kind="sari", c=(230, 70, 120), skin=(205, 150, 110), walk=1),
    dict(x=190, kind="kurta", c=(250, 200, 60), skin=(180, 125, 85), turban=(255, 120, 30), dance=True),
    dict(x=295, kind="shirt", c=(90, 170, 230), skin=(215, 165, 120), walk=1),
    dict(x=470, kind="sari", c=(130, 80, 200), skin=(190, 135, 95), dance=True),
    dict(x=700, kind="kurta", c=(255, 255, 255), skin=(200, 145, 100), cap=True, walk=-1),
    dict(x=905, kind="shirt", c=(240, 120, 60), skin=(175, 120, 80), dance=True),
    dict(x=1220, kind="sari", c=(40, 170, 120), skin=(210, 160, 115), walk=-1),
]


def draw_person(sd, x, y, p, t, mood, phase):
    s = 0.85
    bob = 0
    lean = 0
    if mood == "laugh":
        bob = abs(math.sin(t * 12 + phase)) * 6
        lean = 6 * math.sin(t * 6 + phase)
    elif mood == "dance":
        bob = abs(math.sin(t * 7 + phase)) * 10
    y = y - bob
    hy = y - 150 * s
    hx = x + lean
    walk = 7 * math.sin(t * 9 + phase) if mood == "walk" else 0
    if p["kind"] == "sari":
        sd.poly([(x - 18, y - 95 * s), (x + 18, y - 95 * s), (x + 26, y), (x - 26, y)], fill=p["c"], outline=OL, width=2)
        sd.line([(x - 18, y - 120 * s), (x + 22, y - 40 * s)], tuple(min(255, v + 60) for v in p["c"]), 8)
        sd.rrect((x - 18, y - 128 * s, x + 18, y - 90 * s), 8, fill=p["c"], outline=OL, width=2)
    else:
        for sx in (-1, 1):
            sd.line([(x + sx * 8, y - 60 * s), (x + sx * 9 + sx * walk, y)], (60, 60, 80), 9)
        sd.rrect((x - 20, y - 128 * s, x + 20, y - 50 * s), 9, fill=p["c"], outline=OL, width=2)
    # arms
    if mood == "dance":
        a = math.sin(t * 7 + phase) * 14
        arms = [(x - 34, y - 165 * s + a), (x + 34, y - 165 * s - a)]
    elif mood == "laugh":
        arms = [(x - 8, y - 80 * s), (x + 8, y - 78 * s)]
    elif mood == "gasp":
        arms = [(hx - 12, hy + 8), (hx + 12, hy + 8)]
    elif mood == "point":
        arms = [(x - 22, y - 65 * s), (x + 50, y - 150 * s)]
    else:
        arms = [(x - 24 - walk, y - 62 * s), (x + 24 + walk, y - 62 * s)]
    for sx, hand in zip((-1, 1), arms):
        sd.line([(x + sx * 18, y - 120 * s), hand], p["skin"], 7)
        sd.circle(hand[0], hand[1], 4, fill=p["skin"])
    sd.circle(hx, hy, 17, fill=p["skin"], outline=OL, width=2)
    if p.get("turban"):
        sd.chord((hx - 19, hy - 26, hx + 19, hy + 4), 180, 360, fill=p["turban"], outline=OL, width=2)
    elif p.get("cap"):
        sd.chord((hx - 16, hy - 22, hx + 16, hy + 2), 180, 360, fill=(255, 255, 255), outline=OL, width=2)
    else:
        sd.chord((hx - 18, hy - 20, hx + 18, hy + 6), 180, 360, fill=(30, 25, 25))
        if p["kind"] == "sari":
            sd.circle(hx - 14, hy - 10, 8, fill=(30, 25, 25))
    for sx in (-1, 1):
        if mood == "laugh":
            sd.arc((hx + sx * 6 - 4, hy - 4, hx + sx * 6 + 4, hy + 2), 180, 360, OL, 2)
        else:
            sd.circle(hx + sx * 6, hy - 2, 2, fill=OL)
    if mood == "laugh":
        sd.chord((hx - 8, hy + 2, hx + 8, hy + 14), 0, 180, fill=(120, 30, 40))
    elif mood == "gasp":
        sd.circle(hx, hy + 8, 4, fill=(120, 30, 40))
    else:
        sd.arc((hx - 6, hy + 2, hx + 6, hy + 10), 20, 160, OL, 2)
    if mood == "laugh" and (int(t * 3 + phase * 2) % 3 == 0):
        sd.text((hx + 22, hy - 30), "HA!", 18, (255, 140, 0), stroke=3)


# ====================================================================== SET
@lru_cache(maxsize=None)
def background():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        u = y / H
        d.line((0, y, W, y), fill=(int(140 + 90 * u), int(200 + 40 * u), int(245 + 5 * u)))
    sd = SD(d)
    rng = random.Random(3)
    for i in range(14):                                             # distant town & trees
        x = i * 100 + rng.randint(-20, 20)
        h = rng.randint(60, 150)
        sd.rect((x, 250 - h, x + rng.randint(50, 90), 250), fill=(rng.randint(170, 200), rng.randint(160, 185), 175))
    for i in range(18):
        x = i * 75 + rng.randint(-10, 10)
        sd.circle(x, 205 + rng.randint(-10, 10), rng.randint(26, 40), fill=(90, 160, 90))
    # train coach
    sd.rrect((-40, ROOF - 2, W + 40, 570), 26, fill=(35, 78, 155), outline=OL, width=4)
    sd.rect((-40, ROOF - 2, W + 40, ROOF + 16), fill=(155, 160, 170), outline=OL, width=3)
    sd.rect((-40, 288, W + 40, 300), fill=(240, 225, 170))
    sd.rect((-40, 470, W + 40, 482), fill=(240, 225, 170))
    for i in range(10):
        x = i * 150 - 40
        if i % 4 == 2:
            sd.rect((x + 25, 302, x + 105, 540), fill=(30, 65, 135), outline=OL, width=3)
            sd.rect((x + 40, 320, x + 90, 380), fill=(40, 60, 90), outline=(240, 225, 170), width=3)
            continue
        sd.rect((x + 25, 318, x + 125, 412), fill=(30, 45, 80), outline=(240, 225, 170), width=5)
        for bx in range(int(x + 37), int(x + 125), 12):
            sd.line([(bx, 318), (bx, 412)], (170, 170, 180), 2)
    sd.text((640, 500), "MASTIPUR EXPRESS   12345   SLEEPER CLASS", 18, (240, 225, 170))
    # platform
    sd.rect((0, 545, W, H), fill=(200, 194, 182))
    for x in range(0, W, 80):
        sd.line([(x, 562), (x - 40, H)], (175, 170, 160), 2)
    for y in (600, 650, 700):
        sd.line([(0, y), (W, y)], (175, 170, 160), 2)
    sd.rect((0, 545, W, 562), fill=(250, 205, 40), outline=OL, width=2)
    # canopy roof
    sd.rect((0, 0, W, 48), fill=(130, 62, 52))
    for x in range(0, W, 22):
        sd.line([(x, 0), (x, 48)], (105, 45, 40), 3)
    sd.rect((0, 48, W, 62), fill=(55, 70, 60), outline=OL, width=2)
    # iron pillars (pipes)
    for x in (240, 850, 1235):
        sd.rect((x - 12, 62, x + 12, GROUND + 4), fill=(55, 105, 85), outline=OL, width=3)
        sd.line([(x - 4, 66), (x - 4, GROUND)], (110, 165, 140), 3)
        sd.rect((x - 22, 62, x + 22, 78), fill=(45, 85, 70), outline=OL, width=2)
        sd.rect((x - 22, GROUND - 6, x + 22, GROUND + 8), fill=(45, 85, 70), outline=OL, width=2)
    # station sign
    for x in (1000, 1180):
        sd.line([(x, 62), (x, 80)], OL, 4)
    sd.rrect((960, 78, 1220, 134), 6, fill=(255, 215, 30), outline=OL, width=4)
    sd.text((1090, 98), "MASTIPUR JN.", 30, OL)
    sd.text((1090, 123), "PLATFORM 1", 14, OL, name="Inter-Bold.otf")
    # platform clock
    sd.line([(560, 62), (560, 78)], OL, 4)
    sd.circle(560, 98, 22, fill=(255, 255, 255), outline=OL, width=4)
    sd.line([(560, 98), (560, 83)], OL, 3)
    sd.line([(560, 98), (572, 102)], OL, 3)
    return im


def draw_heap(sd):
    sd.poly([(30, GROUND + 4), (60, 612), (110, 588), (170, 596), (225, 622), (250, GROUND + 4)],
            fill=(130, 110, 85), outline=OL, width=3)
    rng = random.Random(8)
    for _ in range(18):
        x, y = rng.uniform(60, 220), rng.uniform(610, 655)
        sd.circle(x, y, rng.uniform(3, 7), fill=rng.choice([(95, 80, 60), (160, 140, 110), (110, 95, 70)]))
    sd.rect((70, 618, 104, 640), fill=(200, 160, 100), outline=OL, width=2)       # box
    sd.poly([(160, 610), (190, 600), (196, 612), (166, 622)], fill=(90, 160, 90), outline=OL, width=2)  # bottle
    sd.poly([(118, 630), (148, 622), (152, 640), (122, 646)], fill=(245, 245, 235), outline=OL, width=1)  # paper
