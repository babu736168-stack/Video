"""Chhotu (mouse): detailed front-view parts."""
import math

from PIL import ImageFilter

from charart import Linear, Radial, bands, ell, limb_poly, mirror_pts, spline, tone
from cat_v2 import blur_blob, solid

G_L, G_M, G_D = (206, 192, 188), (156, 138, 134), (110, 94, 96)
CREAM = (238, 224, 212)
PINK, PINK_D = (248, 182, 192), (214, 128, 146)
RED_L, RED_M, RED_D = (246, 86, 84), (222, 40, 52), (150, 16, 34)
WHITE = (255, 255, 255)


def grey(cx=10, cy=-20, r=90):
    return Radial((cx, cy), r, [(0, G_L), (0.55, G_M), (1, G_D)])


def head(cv):
    right = [(0, -60), (24, -58), (44, -46), (57, -26), (61, 0), (60, 24), (48, 42), (26, 54), (0, 58)]
    poly = spline(mirror_pts(right), True, 8)

    def details(t):
        blur_blob(t, ell(0, 30, 34, 24), CREAM, 0.95, 3)
        for sx in (-1, 1):
            blur_blob(t, ell(sx * 40, 22, 10, 8), PINK, 0.8, 3)
    solid(cv, poly, grey(), details)
    return []


def ear(cv):
    outer = ell(0, 0, 36, 35, 0, 72)
    solid(cv, outer, Radial((8, -8), 50, [(0, G_L), (0.6, G_M), (1, G_D)]))
    inner = ell(0, 3, 24, 24, 0, 64)
    m = cv.mask(inner)
    cv.paint(m, Radial((2, 4), 28, [(0, (255, 210, 218)), (0.6, PINK), (1, PINK_D)]))
    cv.shade(m, 0.4, 4, 2.5, (130, 40, 70))
    cv.outline(inner, 1.0, (160, 80, 100))
    cv.line([(-14, 10), (-6, -6), (8, -14)], 1.4, (190, 110, 130))
    return []


def cap(cv):
    dome = spline([(-52, 18), (-50, -8), (-36, -32), (-12, -45), (14, -45), (38, -32), (51, -8), (52, 18), (26, 25), (0, 27), (-26, 25)], True, 8)

    def seams(t):
        for sx in (-1, 1):
            t.line([(sx * 12, -46), (sx * 26, -16), (sx * 34, 22)], 1.5, (150, 18, 34))
        t.line([(0, -46), (0, 26)], 1.5, (150, 18, 34))
    m = solid(cv, dome, Radial((12, -22), 66, [(0, RED_L), (0.5, RED_M), (1, RED_D)]), seams)
    cv.dot(0, -46, 4.5, RED_D, 1.3)
    brim = spline([(-58, 18), (-30, 32), (0, 36), (30, 32), (58, 18), (40, 12), (0, 20), (-40, 12)], True, 8)
    solid(cv, brim, Linear((0, 12), (0, 36), [(0, RED_M), (1, RED_D)]))
    cv.stroke([(-40, 22), (-10, 30), (20, 30)], 3, 0.5, (255, 190, 190), alpha=0.7)
    return []


def _eye(cv, cx, s):
    almond = ell(cx, 0, 18, 22, 0, 64)
    m = cv.mask(almond)
    cv.paint(m, Radial((cx, 0), 24, [(0, WHITE), (0.7, (250, 250, 255)), (1, (205, 212, 224))]))
    ix, iy = cx + s * 2, 3

    def inside(t):
        iris = ell(ix, iy, 13.5, 14.5, 0, 56)
        t.paint(t.mask(iris), Radial((ix, iy - 3), 15, [(0, (186, 120, 70)), (0.5, (96, 54, 32)), (1, (34, 18, 14))]))
        t.paint(t.mask(ell(ix, iy, 6.4, 7.2, 0, 40)), (14, 10, 12))
    cv.clip(m, inside)
    cv.shade(m, 0.4, 5, 2.4, (60, 40, 60), toward=(0, 1))
    cv.dot(cx - s * 3 + s * 0, -5, 5.0, WHITE)
    cv.dot(cx + s * 8, 9, 2.2, WHITE)
    cv.line([(cx - 19, 0), (cx - 12, -17), (cx + 4, -23), (cx + 17, -14), (cx + 20, 0)], 3.4)
    cv.line([(cx + s * 17, -12), (cx + s * 26, -18)], 2.2)
    cv.stroke([(cx - 18, -34), (cx, -40), (cx + 18, -32)], 2.5, 5, (86, 70, 72))


def eyes(cv):
    _eye(cv, -32, 1)
    _eye(cv, 32, -1)
    return []


def snout(cv, backing=True):
    if backing:
        patch = spline(ell(0, 4, 66, 48, n=24), True, 6)
        pm = cv.mask(patch)
        cv.paint(pm, grey(8, -10, 90))
        cv.shade(pm, 0.3, 6, 3.5)
        cv.outline(patch, 1.7)
    pts = spline(ell(0, 14, 40, 28, n=40), True, 6)
    cv.paint(cv.mask(pts), Radial((0, 8), 44, [(0, (250, 240, 232)), (1, CREAM)]))
    cv.outline(pts, 0.9, (190, 160, 140))
    for sx in (-1, 1):
        for dx, dy in ((22, 10), (28, 18), (22, 24)):
            cv.dot(sx * dx, dy, 1.7, (170, 130, 130))
        for pts_ in (((30, 14), (62, 8), (96, 10)), ((30, 20), (64, 24), (94, 34)), ((30, 8), (60, -4), (90, -14))):
            cv.stroke([(sx * x, y) for x, y in pts_], 2.1, 0.6, (70, 56, 58))
    nose = spline([(-13, -2), (0, -7), (13, -2), (8, 10), (0, 15), (-8, 10)], True, 8)
    nm = cv.mask(nose)
    cv.paint(nm, Radial((-2, 1), 18, [(0, (255, 196, 208)), (0.5, (244, 130, 160)), (1, (196, 76, 108))]))
    cv.shade(nm, 0.3, 3, 2, (120, 30, 60))
    cv.outline(nose, 1.5, (110, 40, 60))
    cv.paint(cv.mask(ell(-4, -1, 4.2, 2.4, -0.4, 24)), (255, 238, 244), 0.9)
    cv.line([(0, 15), (0, 24)], 1.8, (100, 60, 64))
    cv.line([(0, 24), (-9, 31), (-20, 28)], 2.2, (100, 60, 64))
    cv.line([(0, 24), (9, 31), (20, 28)], 2.2, (100, 60, 64))
    for sx in (-1, 1):                                                     # buck teeth
        tooth = spline([(sx * 0.8, 27), (sx * 9, 27), (sx * 9, 40), (sx * 4.5, 43), (sx * 0.8, 40)] if sx > 0 else
                       [(-0.8, 27), (-9, 27), (-9, 40), (-4.5, 43), (-0.8, 40)], True, 5)
        solid(cv, tooth, Linear((0, 27), (0, 44), [(0, WHITE), (1, (232, 226, 214))]), None, 1.3, None, None)
    return []


def snout_asm(cv):
    return snout(cv, False)


def mouth(cv):
    right = [(0, -16), (16, -18), (30, -10), (32, 4), (24, 22), (10, 32), (0, 34)]
    poly = spline(mirror_pts(right), True, 8)
    m = cv.mask(poly)
    cv.paint(m, Radial((0, 10), 36, [(0, (196, 66, 86)), (0.7, (140, 28, 54)), (1, (90, 10, 30))]))

    def inside(t):
        t.paint(t.mask(spline([(-14, 34), (-12, 18), (0, 12), (12, 18), (14, 34)], True, 8)),
                Radial((0, 22), 20, [(0, (255, 156, 172)), (1, (222, 90, 120))]))
        for sx in (-1, 1):
            tooth = [(sx * 1, -17), (sx * 10, -17), (sx * 10, -2), (sx * 5, 1), (sx * 1, -2)]
            t.paint(t.mask(tooth), WHITE)
            t.outline(tooth, 1.0, (180, 160, 150))
    cv.clip(m, inside)
    cv.shade(m, 0.4, 4, 2.5, (40, 0, 10), toward=(0, 1))
    cv.outline(poly, 2.0)
    return []


def body(cv):
    right = [(0, -70), (26, -66), (48, -44), (58, -6), (57, 34), (42, 62), (0, 74)]
    poly = spline(mirror_pts(right), True, 8)

    def details(t):
        blur_blob(t, ell(0, 14, 34, 50), CREAM, 0.97, 4)
    solid(cv, poly, grey(14, -30, 100), details)
    return []


ARM = [(0, 0), (-6, 26), (3, 52)]
LEG = [(0, 0), (2, 26), (0, 50)]


def arm(cv):
    cv.limb(ARM, [13, 11, 9], grey(0, 20, 50), 1.5)
    return [(0, 0, "shoulder", 34, -4), (-6, 26, "elbow", -32, 0), (3, 52, "wrist", 32, 6)]


def paw(cv):
    for fx, fy, rot in ((-8, 22, 0.25), (0, 25, 0), (8, 22, -0.25)):
        solid(cv, ell(fx, fy, 3.8, 8, rot, 32), Radial((fx, fy - 3), 9, [(0, (255, 222, 226)), (1, PINK_D)]), None, 1.2, (0.25, 2, 1.5), None)
    solid(cv, ell(-13, 8, 3.6, 7, 0.7, 32), Radial((-13, 5), 9, [(0, (255, 222, 226)), (1, PINK_D)]), None, 1.2, (0.25, 2, 1.5), None)
    solid(cv, ell(0, 10, 12, 11, 0, 40), Radial((3, 6), 16, [(0, (255, 226, 230)), (0.7, PINK), (1, PINK_D)]), None, 1.4, (0.3, 3, 2), (0.4, 2, 1.5))
    cv.line([(-5, 12), (0, 16), (5, 12)], 1.0, (190, 100, 120))
    return []


def leg(cv):
    cv.limb(LEG, [17, 14, 12], grey(0, 20, 50), 1.5)
    return [(0, 0, "hip", -34, -2), (2, 26, "knee", 34, 0), (0, 50, "ankle", -36, 4)]


def foot(cv):
    top = ell(0, 6, 22, 12, 0, 48)
    solid(cv, top, grey(0, 0, 34), None, 1.5, (0.3, 3, 2), (0.4, 2, 1.5))
    for x in (-11, 0, 11):
        solid(cv, ell(x, 18, 6.5, 6, 0, 24), Radial((x, 16), 8, [(0, (255, 214, 220)), (1, PINK_D)]), None, 1.3, (0.25, 2, 1.5), None)
    return [(0, -4, "ankle", -36, -6)]


TAIL = [(0, 0), (34, 6), (62, -14), (76, -44), (62, -70), (40, -74)]


def tail(cv):
    m, poly = cv.limb(TAIL, [10, 9, 8, 7, 6, 5], Linear((0, 0), (60, -70), [(0, (250, 196, 204)), (1, PINK_D)]), 1.4)
    bands(cv, TAIL, m, (212, 128, 148), every=12, length=14, w=1.5, start=0.05, end=0.98, alpha=0.7)
    cv.outline(poly, 1.4)
    return []


SPEC = {
    "head": (head, 180, 160, 0, 0), "ear": (ear, 90, 90, 0, 0), "cap": (cap, 150, 100, 0, 0),
    "eyes": (eyes, 170, 100, 0, -6), "snout": (snout, 190, 120, 0, 10), "mouth": (mouth, 100, 80, 0, 8),
    "body": (body, 150, 170, 0, 0), "arm": (arm, 60, 80, 0, 26), "paw": (paw, 60, 60, 0, 16),
    "leg": (leg, 60, 80, 0, 26), "foot": (foot, 80, 50, 0, 8), "tail": (tail, 140, 130, 30, -36),
    "snout_asm": (snout_asm, 190, 120, 0, 10),
}

ASSEMBLY = [
    ("tail", 36, 70, 0, False, 0),
    ("leg", 16, 82, 1, False, 0), ("leg", -16, 82, 1, True, 0),
    ("foot", 20, 130, 1, False, 8), ("foot", -20, 130, 1, True, -8),
    ("body", 0, 20, 2, False, 0),
    ("arm", 46, -14, 3, False, 0), ("arm", -46, -14, 3, True, 0),
    ("paw", 49, 38, 4, False, 0), ("paw", -49, 38, 4, True, 0),
    ("ear", 56, -100, 4, False, 0), ("ear", -56, -100, 4, True, 0),
    ("head", 0, -62, 5, False, 0),
    ("eyes", 0, -68, 6, False, 0), ("snout_asm", 0, -52, 6, False, 0),
    ("cap", 0, -118, 7, False, 0),
]
