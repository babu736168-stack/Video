"""Dadi (grandmother): detailed front-view parts."""
import math

from charart import Linear, Radial, bands, ell, limb_poly, mirror_pts, spline, tone
from cat_v2 import blur_blob, solid

SK_L, SK_M, SK_D = (240, 196, 152), (214, 158, 116), (170, 112, 80)
HAIR_L, HAIR_D = (248, 248, 252), (176, 178, 198)
GREEN_L, GREEN_M, GREEN_D = (84, 200, 138), (44, 160, 102), (22, 104, 68)
MAR_L, MAR_D = (190, 44, 92), (116, 14, 52)
GOLD_L, GOLD_D = (255, 226, 110), (214, 156, 24)
WHITE = (255, 255, 255)


def skin(cx=10, cy=-20, r=90):
    return Radial((cx, cy), r, [(0, SK_L), (0.55, SK_M), (1, SK_D)])


def gold(x0=0, y0=0, x1=0, y1=10):
    return Linear((x0, y0), (x1, y1), [(0, GOLD_L), (0.5, (240, 190, 50)), (1, GOLD_D)])


def bangle(cv, x, y, rx, ry):
    pts = ell(x, y, rx, ry, 0, 40)
    cv.paint(cv.mask(pts), gold(x - rx, y, x + rx, y))
    cv.outline(pts, 1.0, (150, 100, 10))
    cv.paint(cv.mask(ell(x - rx * 0.3, y - ry * 0.3, rx * 0.4, ry * 0.25, 0, 20)), (255, 250, 210), 0.8)


def head(cv):
    cv.paint(cv.mask([(-16, 40), (16, 40), (18, 86), (-18, 86)]), Linear((-18, 0), (18, 0), [(0, SK_D), (0.5, SK_M), (1, SK_D)]))
    cv.outline([(-16, 50), (-18, 86)], 1.6, (34, 24, 28), False)
    cv.outline([(16, 50), (18, 86)], 1.6, (34, 24, 28), False)
    for sx in (-1, 1):                                                   # ears and earrings
        ear_ = ell(sx * 62, 4, 9, 15, 0, 32)
        solid(cv, ear_, skin(sx * 62, 0, 24), None, 1.4, (0.3, 2, 1.5), None)
        cv.line([(sx * 62, 18), (sx * 62, 26)], 1.2, (200, 150, 30))
        cv.dot(sx * 62, 28, 5, GOLD_L, 1.2)
        cv.dot(sx * 62, 38, 3.4, (220, 40, 70), 1.0)
    right = [(0, -70), (30, -68), (52, -50), (60, -20), (58, 14), (46, 44), (24, 64), (0, 70)]
    face = spline(mirror_pts(right), True, 8)
    solid(cv, face, skin(10, -20, 100))
    hair = spline([(-66, 8), (-64, -46), (-36, -78), (0, -88), (36, -78), (64, -46), (66, 8), (52, -22), (32, -40), (0, -46), (-32, -40), (-52, -22)], True, 8)

    def strands(t):
        for k in range(-5, 6):
            t.line([(k * 4, -86), (k * 9, -62), (k * 14 + (4 if k > 0 else -4), -30)], 1.0, (150, 152, 178))
        t.stroke([(0, -88), (0, -46)], 5, 2, (130, 132, 160), alpha=0.6)
    solid(cv, hair, Radial((10, -50), 110, [(0, HAIR_L), (0.7, (226, 228, 240)), (1, HAIR_D)]), strands, 1.8)
    bun = ell(0, -98, 28, 22, 0, 56)
    solid(cv, bun, Radial((8, -104), 36, [(0, HAIR_L), (1, HAIR_D)]), lambda t: [t.line([(-20 + k * 6, -108), (-6, -98 - k), (14, -92)], 1.0, (150, 152, 178)) for k in range(5)])
    cv.line([(-30, -104), (30, -94)], 2.2, (200, 150, 30))
    cv.dot(30, -94, 3.4, GOLD_L, 1.0)
    return []


def eyes(cv, state="open"):
    brow = {"angry": 1.0, "wide": -0.8, "raised": -0.6, "open": 0.0}.get(state, 0.0)
    for s in (-1, 1):
        cx = s * 34
        if state in ("closed", "sleep", "happy"):
            if state == "happy":
                cv.line([(cx - 14, 6), (cx, -7), (cx + 14, 6)], 3.0)
            else:
                cv.line([(cx - 14, 0), (cx, 7), (cx + 14, 0)], 3.0)
                cv.line([(cx + s * 14, 2), (cx + s * 20, 6)], 1.6)
        else:
            wide = state == "wide"
            almond = spline([(cx - 15, 2), (cx - 7, -8 - 3 * wide), (cx + 7, -9 - 3 * wide), (cx + 16, 1), (cx + 8, 8), (cx - 6, 8)], True, 8)
            m = cv.mask(almond)
            cv.paint(m, WHITE)

            def inside(t, cx=cx, wide=wide):
                pr = 0.6 if wide else 1.0
                t.paint(t.mask(ell(cx, 0, 7.4, 8, 0, 40)), Radial((cx, -1), 8, [(0, (130, 84, 52)), (1, (34, 20, 16))]))
                t.paint(t.mask(ell(cx, 0, 3.4 * pr, 3.8 * pr, 0, 24)), (14, 10, 10))
            cv.clip(m, inside)
            cv.dot(cx - 2.5, -3, 2.2, WHITE)
            cv.line([(cx - 16, 2), (cx - 7, -9), (cx + 7, -10), (cx + 17, 1)], 2.0)
            if state == "angry":
                cv.line([(cx + s * 18, -10), (cx - s * 18, 4)], 3.0, (150, 100, 70))
        ob, ib = -22 - brow * 5, -22 + brow * 7
        cv.stroke([(cx + s * 18, ob), (cx, (ob + ib) / 2 - 4), (cx - s * 18, ib)], 2.2, 4.4, (160, 160, 180))
        lens = ell(cx, 0, 24, 24, 0, 72)
        cv.paint(cv.mask(lens), Linear((cx - 20, -20), (cx + 20, 20), [(0, (200, 230, 255)), (1, (140, 180, 230))]), 0.22)
        cv.stroke([(cx - 14, -12), (cx - 8, -18), (cx - 2, -20)], 2.4, 0.6, WHITE, alpha=0.9)
        cv.outline(lens, 3.4, (168, 112, 36))
        cv.outline(ell(cx, 0, 24, 24, 0, 72), 0.8, (255, 220, 130))
    cv.line([(-10, -2), (0, -6), (10, -2)], 3.0, (168, 112, 36))
    for s in (-1, 1):
        cv.line([(s * 58, -4), (s * 74, -2)], 2.6, (168, 112, 36))
    return []


def face(cv):
    right = [(0, -70), (30, -68), (52, -50), (60, -20), (58, 14), (46, 44), (24, 64), (0, 70)]
    poly = spline(mirror_pts(right), True, 8)
    solid(cv, poly, skin(10, -20, 100))
    for s in (-1, 1):
        blur_blob(cv, ell(s * 36, 28, 16, 11), (240, 140, 130), 0.55, 4)
        cv.line([(s * 44, -2), (s * 48, 10), (s * 42, 22)], 1.4, (180, 120, 90))            # smile lines
        cv.line([(s * 52, -10), (s * 56, -4)], 1.1, (190, 130, 100))
    drop = spline([(0, -44), (6, -40), (6, -32), (0, -26), (-6, -32), (-6, -40)], True, 6)
    solid(cv, drop, Radial((0, -34), 9, [(0, (255, 90, 110)), (1, (170, 10, 40))]), None, 1.0, None, None)  # bindi
    cv.line([(0, -4), (-2, 16), (6, 22)], 1.8, (180, 120, 90))                                  # nose
    cv.line([(6, 22), (0, 26)], 1.6, (180, 120, 90))
    cv.dot(16, 20, 2.6, GOLD_L, 0.8)                                                            # nose pin
    cv.dot(15.4, 19.4, 0.9, WHITE)
    lip = spline([(-22, 40), (-8, 36), (0, 38), (8, 36), (22, 40), (10, 52), (0, 54), (-10, 52)], True, 8)
    solid(cv, lip, Radial((0, 44), 26, [(0, (226, 96, 104)), (1, (170, 52, 66))]), None, 1.4, (0.3, 2, 1.5), (0.4, 1.5, 1))
    cv.line([(-20, 41), (0, 44), (20, 41)], 1.2, (120, 30, 40))
    return []


def saree(cv):
    right = [(0, -118), (26, -116), (52, -100), (68, -66), (76, -10), (90, 70), (102, 140), (106, 170)]
    poly = spline(mirror_pts(right + [(0, 172)]), True, 8)

    def pleats(t):
        for k in range(-5, 6):
            t.line([(k * 8, -10), (k * 11, 60), (k * 14, 172)], 1.4, GREEN_D)
            t.line([(k * 8 + 3, -10), (k * 11 + 3, 60), (k * 14 + 3, 172)], 1.0, (150, 230, 180))
        t.stroke([(-110, 150), (0, 156), (110, 150)], 20, 20, GOLD_L, alpha=1.0)
        for x in range(-96, 100, 16):
            t.dot(x, 154 + abs(x) * 0.0, 3.4, MAR_D)
    solid(cv, poly, Radial((14, -50), 190, [(0, GREEN_L), (0.5, GREEN_M), (1, GREEN_D)]), pleats)
    return []


def pallu(cv):
    path = [(-44, -100), (-12, -36), (28, 34), (56, 108)]
    m, poly = cv.limb(path, [46, 50, 58, 66], Radial((10, 0), 150, [(0, MAR_L), (1, MAR_D)]), 1.8, n=12)
    bands(cv, path, m, GOLD_L, every=18, length=60, w=3.4, start=0.12, end=0.95, alpha=0.95)
    for t in (0.22, 0.45, 0.68, 0.9):
        sp = spline(path, False, 12)
        x, y = sp[int(t * (len(sp) - 1))]
        cv.clip(m, lambda c, x=x, y=y: c.dot(x, y, 5.4, (255, 214, 90)))
    cv.outline(poly, 1.8)
    return []


ARM = [(0, 0), (-12, 50), (2, 100)]


def arm(cv):
    m, poly = cv.limb(ARM, [24, 19, 15], skin(0, 40, 90), 1.7)
    sleeve = limb_poly([(0, -4), (-4, 28)], [34, 30])
    solid(cv, sleeve, Radial((0, 6), 40, [(0, MAR_L), (1, MAR_D)]), None, 1.7, (0.35, 4, 3), (0.4, 2.5, 2))
    for k in range(4):
        bangle(cv, 1.5, 84 + k * 3.6, 9.6, 3.6)
    return [(0, 0, "shoulder", 52, -6), (-12, 50, "elbow", -54, 0), (2, 100, "wrist", 52, 4)]


def hand(cv):
    for fx, fy, rot, ln in ((-9, 36, 0.28, 13), (-3, 40, 0.1, 15), (4, 40, -0.1, 14), (10, 35, -0.3, 11)):
        solid(cv, ell(fx, fy, 3.8, ln, rot, 32), skin(fx, fy - 6, 14), None, 1.3, (0.25, 2, 1.5), None)
    solid(cv, ell(-15, 18, 4, 11, 0.9, 32), skin(-15, 14, 14), None, 1.3, (0.25, 2, 1.5), None)
    solid(cv, ell(0, 18, 14, 14, 0, 40), skin(3, 12, 20), None, 1.5, (0.3, 3, 2), (0.4, 2, 1.5))
    cv.dot(-3, 54, 1.8, GOLD_L, 0.7)
    for k in range(3):
        bangle(cv, 0, 2 - k * 3.6, 10.5, 3.8)
    return []


def feet(cv):
    for sx in (-1, 1):
        cx = sx * 26
        solid(cv, spline(ell(cx, 14, 17, 11, 0, 40), True, 6), skin(cx, 8, 30), None, 1.5, (0.3, 3, 2), (0.4, 2, 1.5))
        for k, (dx, r) in enumerate(((-9, 3.6), (-3, 3.8), (3, 3.6), (9, 3.2), (14, 2.8))):
            solid(cv, ell(cx + sx * dx, 24, r, r * 0.8, 0, 20), skin(cx, 20, 10), None, 1.0, None, None)
        cv.line([(cx - 15, 0), (cx + 15, 0)], 2.4, (214, 156, 24))
        cv.dot(cx, 3, 2.6, GOLD_L, 0.9)
    return []


def broom(cv):
    m, poly = cv.limb([(0, -130), (0, 40)], [9, 9], Linear((-5, 0), (5, 0), [(0, (214, 160, 90)), (0.5, (170, 118, 60)), (1, (110, 72, 34))]), 1.5, None, (0.4, 1.5, 1))
    straw = spline([(-14, 56), (14, 56), (30, 100), (50, 150), (30, 156), (10, 150), (-8, 158), (-30, 150), (-50, 150), (-30, 100)], True, 6)

    def strands(t):
        for k in range(-9, 10):
            t.stroke([(k * 1.4, 58), (k * 3.2, 110), (k * 5.2, 152)], 1.4, 0.6, (160, 116, 48) if k % 2 else (236, 200, 120), alpha=0.9)
    solid(cv, straw, Linear((0, 56), (0, 156), [(0, (240, 206, 130)), (1, (198, 150, 70))]), strands, 1.6, (0.28, 4, 3), (0.3, 2, 1.5))
    for k in range(4):
        cv.line([(-13, 40 + k * 4), (0, 44 + k * 4), (13, 40 + k * 4)], 1.6, (110, 70, 30))
    return []


def foot_one(cv):
    cx = 0
    solid(cv, spline(ell(cx, 14, 17, 11, 0, 40), True, 6), skin(cx, 8, 30), None, 1.5, (0.3, 3, 2), (0.4, 2, 1.5))
    for k, (dx, r) in enumerate(((-9, 3.6), (-3, 3.8), (3, 3.6), (9, 3.2), (14, 2.8))):
        solid(cv, ell(cx + dx, 24, r, r * 0.8, 0, 20), skin(cx, 20, 10), None, 1.0, None, None)
    cv.line([(cx - 15, 0), (cx + 15, 0)], 2.4, (214, 156, 24))
    cv.dot(cx, 3, 2.6, GOLD_L, 0.9)
    return []


def mouth(cv):
    right = [(0, -8), (14, -9), (24, -3), (24, 8), (14, 20), (0, 24)]
    poly = spline(mirror_pts(right), True, 8)
    m = cv.mask(poly)
    cv.paint(m, Radial((0, 8), 28, [(0, (150, 40, 56)), (1, (84, 10, 30))]))
    cv.clip(m, lambda t: t.paint(t.mask(spline([(-14, 24), (-10, 12), (0, 8), (10, 12), (14, 24)], True, 6)), (232, 110, 128)))
    cv.outline(poly, 2.4, (140, 40, 50))
    return []


SPEC = {
    "head": (head, 190, 230, 0, -16), "eyes": (eyes, 170, 80, 0, 0), "face": (face, 160, 160, 0, 0),
    "saree": (saree, 230, 300, 0, 26), "pallu": (pallu, 150, 250, 8, 4), "arm": (arm, 70, 130, 0, 50),
    "hand": (hand, 70, 90, 0, 26), "feet": (feet, 110, 60, 0, 12), "foot_one": (foot_one, 60, 50, 0, 12), "mouth": (mouth, 70, 50, 0, 8), "broom": (broom, 120, 300, 0, 14),
}

ASSEMBLY = [
    ("feet", 0, 244, 0, False, 0),
    ("saree", 0, 60, 1, False, 0),
    ("pallu", -4, 16, 2, False, 0),
    ("arm", 68, -46, 3, False, 0), ("arm", -68, -46, 3, True, 0),
    ("hand", 70, 54, 4, False, 0), ("hand", -70, 54, 4, True, 0),
    ("head", 0, -144, 5, False, 0),
    ("eyes", 0, -152, 6, False, 0), ("face", 0, -144, 5.5, False, 0),
]
