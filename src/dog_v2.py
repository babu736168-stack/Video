"""Sheru (dog): detailed front-view parts."""
import math

from charart import Linear, Radial, bands, ell, limb_poly, mirror_pts, spline, tone
from cat_v2 import blur_blob, solid

BR_L, BR_M, BR_D = (204, 138, 78), (164, 102, 54), (112, 66, 34)
PATCH = (92, 54, 30)
CREAM_L, CREAM_D = (255, 246, 228), (238, 214, 176)
WHITE = (255, 255, 255)


def brown(cx=14, cy=-30, r=130):
    return Radial((cx, cy), r, [(0, BR_L), (0.5, BR_M), (1, BR_D)])


def head(cv):
    right = [(0, -80), (34, -78), (64, -62), (84, -32), (90, 4), (86, 36), (70, 62), (40, 80), (0, 86)]
    poly = spline(mirror_pts(right), True, 8)

    def details(t):
        t.stroke([(0, -80), (0, -46), (0, -14)], 22, 8, CREAM_L, alpha=0.95)
        blur_blob(t, ell(0, 52, 44, 36), CREAM_L, 0.95, 4)
    solid(cv, poly, brown(), details)
    return []


def ear(cv):
    poly = spline([(-18, -62), (10, -64), (32, -42), (42, 0), (36, 48), (16, 74), (-6, 66), (-20, 32), (-26, -20)], True, 10)

    def details(t):
        t.stroke([(-12, -50), (-6, -10), (-4, 40)], 8, 2, (200, 140, 90), alpha=0.5)
    solid(cv, poly, Radial((6, -20), 90, [(0, (150, 92, 52)), (0.6, (106, 62, 34)), (1, (72, 40, 22))]), details)
    return []


def _eye(cv, cx, s, ys=1.0, pup=1.0, lid=0.0, brow=0.0):
    almond = ell(cx, 0, 20, 23 * ys, 0, 64)
    m = cv.mask(almond)
    cv.paint(m, Radial((cx, 0), 26, [(0, WHITE), (0.7, (250, 250, 255)), (1, (205, 212, 224))]))
    ix, iy = cx + s * 2, 3

    def inside(t):
        iris = ell(ix, iy, 15, 16, 0, 56)
        t.paint(t.mask(iris), Radial((ix, iy - 3), 17, [(0, (150, 92, 50)), (0.5, (74, 42, 24)), (1, (26, 14, 10))]))
        t.paint(t.mask(ell(ix, iy, 7.2 * pup, 8 * pup, 0, 40)), (12, 8, 8))
    cv.clip(m, inside)
    cv.shade(m, 0.4, 5, 2.4, (60, 40, 60), toward=(0, 1))
    cv.dot(cx - s * 3, -5, 5.4, WHITE)
    cv.dot(cx + s * 9, 10, 2.4, WHITE)
    if lid:
        yi, yo = -10 + lid * 30, -10 + lid * 6
        lidp = [(cx - s * 32, -50), (cx + s * 32, -50), (cx + s * 32, yi), (cx - s * 32, yo)]
        cv.clip(m, lambda t: t.paint(t.mask(lidp), brown(0, -20, 50)))
        cv.line([(cx - s * 26, yo), (cx + s * 26, yi)], 3.6)
    cv.line([(cx - 20, 0), (cx - 13, -18), (cx + 5, -25), (cx + 18, -15), (cx + 21, 0)], 3.2)
    ob, ib = -34 - brow * 8, -34 + brow * 14
    cv.stroke([(cx + s * 20, ob), (cx, (ob + ib) / 2 - 8), (cx - s * 20, ib)], 3, 7, (70, 42, 24))


def eyes(cv):
    pm = ell(-44, 2, 40, 42, 0.2, 64)
    cv.paint(cv.mask(pm), Radial((-44, 0), 44, [(0, (122, 74, 42)), (1, PATCH)]), 1.0)
    cv.outline(pm, 1.4, (60, 34, 20))
    _eye(cv, -44, 1)
    _eye(cv, 44, -1)
    return []


def snout(cv, backing=True):
    if backing:
        patch = spline(ell(0, 6, 84, 62, n=24), True, 6)
        pm = cv.mask(patch)
        cv.paint(pm, brown(10, -10, 130))
        cv.shade(pm, 0.3, 6, 3.5)
        cv.outline(patch, 1.7)
    for cx_ in (-26, 26):
        pts = ell(cx_, 26, 36, 30, n=48)
        cv.paint(cv.mask(pts), Radial((cx_, 18), 46, [(0, CREAM_L), (1, CREAM_D)]))
        cv.outline(pts, 1.0, (186, 140, 100))
    for sx in (-1, 1):
        for dx, dy in ((28, 22), (38, 30), (30, 38)):
            cv.dot(sx * dx, dy, 1.9, (150, 100, 70))
    nose = spline([(-24, -6), (0, -14), (24, -6), (22, 12), (0, 22), (-22, 12)], True, 8)
    nm = cv.mask(nose)
    cv.paint(nm, Radial((-4, -2), 36, [(0, (92, 80, 86)), (0.5, (34, 28, 32)), (1, (14, 10, 14))]))
    cv.outline(nose, 1.6, (14, 10, 14))
    cv.paint(cv.mask(ell(-8, -4, 9, 4, -0.3, 32)), (200, 200, 214), 0.85)
    cv.line([(0, 22), (0, 36)], 2.2, (80, 50, 40))
    cv.line([(0, 36), (-12, 46), (-26, 42)], 2.6, (80, 50, 40))
    cv.line([(0, 36), (12, 46), (26, 42)], 2.6, (80, 50, 40))
    return []


def snout_asm(cv):
    return snout(cv, False)


def mouth(cv):
    right = [(0, -14), (24, -16), (44, -8), (50, 8), (40, 30), (20, 46), (0, 50)]
    poly = spline(mirror_pts(right), True, 8)
    m = cv.mask(poly)
    cv.paint(m, Radial((0, 12), 56, [(0, (186, 52, 70)), (0.7, (130, 24, 48)), (1, (80, 8, 28))]))

    def inside(t):
        tongue = spline([(-24, 52), (-26, 24), (-12, 8), (12, 8), (26, 24), (24, 62), (0, 74), (-24, 62)], True, 8)
        t.paint(t.mask(tongue), Radial((0, 30), 34, [(0, (255, 150, 168)), (1, (224, 84, 114))]))
        t.line([(0, 14), (0, 46)], 1.6, (184, 62, 92))
        for sx in (-1, 1):
            tooth = [(sx * 22, -16), (sx * 34, -14), (sx * 27, 0)]
            t.paint(t.mask(tooth), WHITE)
            t.outline(tooth, 1.0, (186, 160, 140))
    cv.clip(m, inside)
    cv.shade(m, 0.4, 5, 3, (40, 0, 10), toward=(0, 1))
    cv.outline(poly, 2.2)
    return []


def collar(cv):
    path = [(-100, -6), (-50, 12), (0, 18), (50, 12), (100, -6)]
    m, poly = cv.limb(path, [22, 22, 22, 22, 22], Linear((0, 0), (0, 30), [(0, (240, 70, 70)), (1, (170, 24, 40))]), 1.8)
    cv.line([(-96, -8), (-50, 6), (0, 11), (50, 6), (96, -8)], 1.2, (255, 190, 190))
    for x in range(-84, 90, 14):
        cv.dot(x, 14 - abs(x) * 0.07 + (x * x) * 0.0006 - 0.0, 1.2, (255, 220, 200))
    cv.dot(0, 38, 17, (255, 214, 70), 1.7)
    cv.dot(-4, 33, 5, (255, 244, 190))
    bone = [(-8, 40), (8, 40)]
    cv.line(bone, 3.0, (150, 100, 20))
    for x, y in ((-9, 38), (-9, 42), (9, 38), (9, 42)):
        cv.dot(x, y, 2.2, (150, 100, 20))
    return []


def body(cv):
    right = [(0, -110), (40, -104), (76, -80), (98, -30), (104, 30), (94, 84), (60, 118), (0, 128)]
    poly = spline(mirror_pts(right), True, 8)
    chest = spline(mirror_pts([(0, -90), (34, -80), (56, -30), (60, 30), (50, 88), (0, 108)]), True, 8)

    def details(t):
        blur_blob(t, chest, CREAM_L, 0.97, 3)
        for k in range(-3, 4):
            t.stroke([(k * 14, -92), (k * 15, -60), (k * 17, -30)], 8, 0.5, CREAM_L, alpha=0.9)
    solid(cv, poly, brown(18, -50, 170), details)
    return []


FRONT = [(0, 0), (0, 56), (0, 116)]


def front_leg(cv):
    m, poly = cv.limb(FRONT, [38, 32, 30], brown(8, 30, 90))
    cv.clip(m, lambda t: t.stroke([(0, 90), (0, 108), (0, 130)], 40, 40, CREAM_L, alpha=0.95))
    cv.outline(poly, 1.8)
    return [(0, 0, "shoulder", 54, -4), (0, 56, "elbow", -50, 0), (0, 116, "wrist", 52, 4)]


def paw(cv):
    """Paw seen from underneath: big pad and four toe pads."""
    outer = spline(ell(0, 0, 40, 36, n=40), True, 6)
    solid(cv, outer, Radial((6, -8), 50, [(0, CREAM_L), (1, CREAM_D)]), None, 1.8, (0.3, 5, 3), (0.4, 3, 2))
    PAD, PAD_H = (96, 62, 70), (130, 90, 98)
    big = spline([(-16, 4), (-10, -4), (0, -6), (10, -4), (16, 4), (12, 18), (0, 24), (-12, 18)], True, 8)
    solid(cv, big, Radial((0, 8), 22, [(0, PAD_H), (1, PAD)]), None, 1.2, (0.3, 3, 2), (0.3, 2, 1.5))
    for x, y in ((-28, -12), (-10, -26), (10, -26), (28, -12)):
        solid(cv, ell(x, y, 7, 9, 0, 28), Radial((x, y - 2), 10, [(0, PAD_H), (1, PAD)]), None, 1.1, (0.3, 2, 1.5), (0.3, 1.5, 1))
    return []


def hind_leg(cv):
    thigh = spline(ell(0, 0, 46, 54, 0.15, 48), True, 6)
    solid(cv, thigh, Radial((10, -16), 70, [(0, BR_L), (0.5, BR_M), (1, BR_D)]), None, 1.8)
    foot = spline(ell(8, 62, 36, 16, 0, 40), True, 6)
    solid(cv, foot, Radial((8, 56), 40, [(0, CREAM_L), (1, CREAM_D)]), None, 1.6)
    for x in (-8, 8, 24):
        cv.line([(x, 54), (x - 1, 72)], 1.2, (180, 140, 100))
    return [(0, -20, "hip", -54, -4), (14, 38, "knee", 50, 0), (8, 62, "ankle", -52, 6)]


TAIL = [(0, 0), (30, 4), (56, -16), (66, -52), (54, -86)]


def tail(cv):
    m, poly = cv.limb(TAIL, [30, 26, 22, 18, 14], brown(30, -30, 110))
    cv.clip(m, lambda t: t.dot(54, -86, 18, CREAM_L))
    for i in range(6):
        t0 = i / 6
    cv.outline(poly, 1.8)
    return []


def front_up(cv):
    path = [(0, 0), (0, 29), (0, 58)]
    m, poly = cv.limb(path, [40, 36, 33], brown(8, 20, 80))
    cv.outline(poly, 1.8)
    return []


def front_lo(cv):
    path = [(0, 0), (0, 29), (0, 58)]
    m, poly = cv.limb(path, [33, 31, 30], brown(8, 20, 80))
    cv.clip(m, lambda t: t.stroke([(0, 34), (0, 50), (0, 70)], 40, 40, CREAM_L, alpha=0.95))
    cv.outline(poly, 1.8)
    return []


SPEC = {
    "head": (head, 220, 200, 0, 0), "ear": (ear, 110, 160, 0, 0), "eyes": (eyes, 230, 120, 0, -6),
    "snout": (snout, 220, 160, 0, 14), "mouth": (mouth, 150, 130, 0, 10), "collar": (collar, 230, 90, 0, 14),
    "body": (body, 250, 260, 0, 0), "front_leg": (front_leg, 100, 190, 0, 66), "paw": (paw, 100, 100, 0, 0),
    "hind_leg": (hind_leg, 120, 170, 0, 20), "tail": (tail, 140, 160, 20, -40), "snout_asm": (snout_asm, 220, 160, 0, 14),
    "front_up": (front_up, 80, 100, 0, 28), "front_lo": (front_lo, 80, 100, 0, 28),
}

ASSEMBLY = [
    ("tail", 92, 130, 0, False, 0),
    ("hind_leg", 84, 96, 1, False, 0), ("hind_leg", -84, 96, 1, True, 0),
    ("body", 0, 56, 2, False, 0),
    ("front_leg", 42, 24, 3, False, 0), ("front_leg", -42, 24, 3, True, 0),
    ("ear", 82, -64, 4, False, 0), ("ear", -82, -64, 4, True, 0),
    ("head", 0, -66, 5, False, 0),
    ("eyes", 0, -80, 6, False, 0), ("snout_asm", 0, -38, 6, False, 0),
    ("collar", 0, 2, 7, False, 0),
]
