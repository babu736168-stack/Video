"""Tubby Billa (cat): detailed parts. Each part fn(cv) draws in local units and returns joint annotations."""
import math

from charart import (Cv, Linear, Radial, bands, ell, limb_poly, mirror_pts, mix, ribbon_poly, spline, tone, OL)
from PIL import ImageFilter

ORG_L, ORG_M, ORG_D = (255, 198, 96), (246, 152, 50), (212, 100, 24)
STRIPE = (160, 70, 20)
CREAM_L, CREAM_D = (255, 248, 230), (245, 220, 178)
PINK = (255, 170, 192)
WHITE = (255, 255, 255)


def orange(cx=14, cy=-34, r=120):
    return Radial((cx, cy), r, [(0, ORG_L), (0.5, ORG_M), (1, ORG_D)])


def cream(cx=0, cy=0, r=60):
    return Radial((cx, cy), r, [(0, (255, 252, 240)), (1, CREAM_D)])


def solid(cv, pts, fill, details=None, ow=1.7, shade=(0.32, 6, 3.5), hl=(0.36, 3.5, 2.2)):
    m = cv.mask(pts)
    cv.paint(m, fill)
    if details:
        cv.clip(m, details)
    if shade:
        cv.shade(m, *shade)
    if hl:
        cv.highlight(m, *hl)
    if ow:
        cv.outline(pts, ow)
    return m


def blur_blob(t, pts, color, alpha=1.0, blur=3):
    m = t.mask(pts).filter(ImageFilter.GaussianBlur(blur * t.S))
    t.overlay(m, color, alpha)


# ------------------------------------------------------------------ head
def head_poly():
    right = [(0, -72), (26, -69), (50, -58), (68, -38), (78, -12), (90, 6), (77, 18), (88, 33), (70, 44), (72, 58),
             (50, 63), (26, 71), (0, 73)]
    return spline(mirror_pts(right), True, 8)


def head(cv):
    poly = head_poly()

    def details(t):
        blur_blob(t, ell(0, 40, 50, 30), CREAM_L, 0.95, 3)
        for sx in (-1, 1):
            t.stroke([(sx * 78, -8), (sx * 56, -2), (sx * 40, 0)], 10, 1.5, STRIPE)
            t.stroke([(sx * 80, 14), (sx * 58, 16), (sx * 42, 16)], 9, 1.5, STRIPE)
            t.stroke([(sx * 18, -66), (sx * 14, -48), (sx * 10, -36)], 12, 2, STRIPE)
        t.stroke([(0, -66), (0, -48), (0, -34)], 13, 2, STRIPE)
    solid(cv, poly, orange(), details)
    return []


# ------------------------------------------------------------------ ear
def ear(cv):
    outer = spline([(-30, 44), (-34, 6), (-18, -30), (2, -54), (22, -28), (36, 10), (32, 44), (0, 50)], True, 10)
    inner = spline([(-18, 40), (-20, 8), (-8, -20), (4, -38), (14, -14), (22, 10), (20, 40)], True, 10)

    def details(t):
        pass
    solid(cv, outer, orange(10, -10, 80))
    mi = cv.mask(inner)
    cv.paint(mi, Radial((2, 14), 40, [(0, (255, 205, 215)), (0.6, PINK), (1, (226, 112, 142))]))
    cv.shade(mi, 0.35, 4, 2.5, (120, 30, 60))
    cv.outline(inner, 1.0, (150, 60, 80))

    def tufts(t):
        for i, x in enumerate((-12, -4, 4, 12)):
            t.stroke([(x, 42), (x * 0.7, 26), (x * 0.5, 8 + i % 2 * 6)], 6, 0.5, CREAM_L, alpha=0.95)
    cv.clip(mi, tufts)
    return []


# ------------------------------------------------------------------ eyes
def _eye(cv, cx, cy, s, ys=1.0, pup=1.0, lid=0.0, brow=0.0):
    def X(x, y):
        return (cx + s * x, cy + (y * ys if y < 0 else y))
    almond = spline([X(-24, 2), X(-13, -15), X(5, -21), X(22, -10), X(26, 4), X(14, 17), X(-4, 21), X(-18, 14)], True, 10)
    m = cv.mask(almond)
    cv.paint(m, Radial((cx, cy), 28, [(0, WHITE), (0.65, (250, 250, 255)), (1, (198, 208, 222))]))
    ix, iy = cx + s * 3, cy + 2

    def inside(t):
        iris = ell(ix, iy, 15, 15, n=64)
        t.paint(t.mask(iris), Radial((ix, iy - 3), 16, [(0, (214, 244, 120)), (0.4, (110, 192, 74)), (0.85, (34, 122, 52)), (1, (16, 72, 36))]))
        for k in range(14):                                                # iris fibres
            a = 2 * math.pi * k / 14
            t.stroke([(ix + 7 * math.cos(a), iy + 7 * math.sin(a)), (ix + 14 * math.cos(a), iy + 14 * math.sin(a))],
                     0.8, 0.3, (30, 110, 50), alpha=0.5)
        t.outline(iris, 1.0, (14, 60, 30))
        t.paint(t.mask(ell(ix, iy, 6 * pup, 9.5 * pup, n=48)), (18, 14, 18))
    cv.clip(m, inside)
    cv.shade(m, 0.45, 5, 2.4, (60, 40, 60), toward=(0, 1))
    cv.dot(cx + s * -2, cy - 6, 4.3, WHITE)
    cv.dot(cx + s * 10, cy + 7, 2.0, WHITE)
    if lid:
        yi, yo = -12 + lid * 32, -12 + lid * 6
        lidp = [X(-34, -60), X(34, -60), X(34, yi), X(-34, yo)]
        cv.clip(m, lambda t: t.paint(t.mask(lidp), orange(0, -30, 60)))
        cv.line([X(-30, yo), X(30, yi)], 4.6)
    cv.line([X(-27, 4), X(-14, -15), X(5, -22), X(22, -11), X(29, 3)], 4.4)               # upper lid
    cv.line([X(25, -8), X(35, -15)], 2.6)
    cv.line([X(26, -3), X(36, -4)], 2.2)
    cv.line([X(-20, 15), X(-4, 21), X(14, 17)], 1.2, (70, 50, 50))
    ob, ib = -33 - brow * 8, -31 + brow * 14
    cv.stroke([X(-28, ob), X(-4, (ob + ib) / 2 - 8), X(26, ib)], 3.5, 8, (120, 52, 16))


def eyes(cv):
    _eye(cv, -42, 0, 1)
    _eye(cv, 42, 0, -1)
    return []


# ------------------------------------------------------------------ muzzle & nose
def muzzle(cv, backing=True):
    if backing:
        patch = spline(ell(0, -4, 80, 54, n=24), True, 6)
        mp = cv.mask(patch)
        cv.paint(mp, orange(10, -20, 110))
        cv.shade(mp, 0.3, 6, 3.5)
        cv.outline(patch, 1.7)
    for cx_, cy_, rx, ry in ((-24, 12, 30, 25), (24, 12, 30, 25), (0, 32, 21, 15)):
        pts = ell(cx_, cy_, rx, ry, n=48)
        cv.paint(cv.mask(pts), cream(cx_, cy_ - 6, 34))
    for cx_, cy_, rx, ry in ((-24, 12, 30, 25), (24, 12, 30, 25)):
        cv.outline(ell(cx_, cy_, rx, ry, n=48), 0.9, (190, 140, 90))
    for sx in (-1, 1):
        for i, (dx, dy) in enumerate(((30, 4), (38, 12), (32, 20))):
            cv.dot(sx * dx, dy, 1.9, (176, 112, 64))
        for pts in (((30, 12), (62, 8), (96, 12)), ((30, 18), (62, 24), (94, 34)), ((30, 6), (62, -4), (92, -16))):
            cv.stroke([(sx * x, y) for x, y in pts], 2.4, 0.6, (52, 38, 40))
    nose = spline([(-14, -8), (0, -12), (14, -8), (9, 5), (0, 12), (-9, 5)], True, 8)
    nm = cv.mask(nose)
    cv.paint(nm, Radial((-2, -4), 18, [(0, (255, 205, 218)), (0.5, (255, 150, 178)), (1, (214, 92, 128))]))
    cv.shade(nm, 0.3, 3, 2, (120, 30, 60))
    cv.outline(nose, 1.5, (100, 30, 50))
    cv.paint(cv.mask(ell(-4, -6, 4, 2.4, -0.4, 24)), (255, 235, 242), 0.9)
    cv.line([(0, 12), (0, 22)], 2.0, (80, 40, 40))
    cv.line([(0, 22), (-7, 29), (-18, 27)], 2.4, (80, 40, 40))
    cv.line([(0, 22), (7, 29), (18, 27)], 2.4, (80, 40, 40))
    return []


# ------------------------------------------------------------------ open mouth
def mouth(cv):
    right = [(0, -18), (20, -20), (38, -12), (42, 4), (32, 28), (16, 42), (0, 46)]
    poly = spline(mirror_pts(right), True, 8)
    m = cv.mask(poly)
    cv.paint(m, Radial((0, 14), 46, [(0, (190, 54, 72)), (0.6, (140, 28, 50)), (1, (84, 8, 28))]))

    def inside(t):
        tongue = spline([(-20, 44), (-18, 24), (-6, 14), (6, 14), (18, 24), (20, 44)], True, 8)
        t.paint(t.mask(tongue), Radial((0, 26), 26, [(0, (255, 150, 168)), (1, (222, 84, 116))]))
        t.line([(0, 18), (0, 36)], 1.4, (180, 60, 90))
        for sx in (-1, 1):
            tooth = [(sx * 8, -20), (sx * 20, -20), (sx * 14, -4)]
            t.paint(t.mask(spline(tooth, True, 6)), (255, 252, 244))
            t.outline(spline(tooth, True, 6), 1.1, (180, 150, 130))
    cv.clip(m, inside)
    cv.shade(m, 0.4, 5, 3, (40, 0, 10), toward=(0, 1))
    cv.outline(poly, 2.2)
    return []


# ------------------------------------------------------------------ torso
def torso(cv):
    right = [(0, -100), (32, -96), (60, -74), (78, -34), (84, 14), (76, 60), (52, 94), (0, 104)]
    poly = spline(mirror_pts(right), True, 8)
    belly_r = [(0, -76), (24, -66), (42, -28), (49, 18), (40, 60), (20, 80), (0, 86)]
    belly = spline(mirror_pts(belly_r), True, 8)

    def details(t):
        t.paint(t.mask(belly), cream(0, -10, 80))
        for i in range(4):
            y = -52 + i * 36
            for sx in (-1, 1):
                t.stroke([(sx * 90, y), (sx * 64, y + 8), (sx * 46, y + 9)], 12, 1.5, STRIPE)
        for k in range(-3, 4):                                             # chest fluff
            t.stroke([(k * 8, -80), (k * 8 + (k * 1.5), -62), (k * 9, -50)], 7, 0.5, (255, 252, 240), alpha=0.95)
        t.outline(belly, 0.8, (214, 170, 120))
    solid(cv, poly, orange(16, -50, 150), details)
    return []


# ------------------------------------------------------------------ arm, glove, leg, foot, tail
ARM = [(0, 0), (-9, 46), (3, 92)]
LEG = [(0, 0), (14, 50), (4, 98)]


def arm(cv):
    m, poly = cv.limb(ARM, [27, 23, 18], orange(10, 20, 90))
    bands(cv, ARM, m, STRIPE, every=17, length=40, w=4.6, start=0.35, end=0.95)
    cv.outline(poly, 1.7)
    return [(0, 0, "shoulder", 52, -6), (-9, 46, "elbow", -50, 0), (3, 92, "wrist", 48, 4)]


def glove(cv):
    fingers = [(-14, 40, 8.5, 14, 0.18), (0, 46, 8.5, 15, 0.0), (14, 40, 8.5, 14, -0.18)]
    for fx, fy, rx, ry, rot in fingers:
        pts = ell(fx, fy, rx, ry, rot, 40)
        solid(cv, pts, Radial((fx, fy - 4), 16, [(0, WHITE), (1, (212, 220, 236))]), None, 1.5, (0.22, 3, 2), None)
    thumb = ell(-26, 24, 8, 14, 0.7, 40)
    solid(cv, thumb, Radial((-26, 20), 16, [(0, WHITE), (1, (212, 220, 236))]), None, 1.5, (0.22, 3, 2), None)
    palm = ell(0, 22, 25, 24, 0, 64)
    solid(cv, palm, Radial((6, 12), 38, [(0, WHITE), (0.7, (240, 244, 252)), (1, (200, 210, 230))]), None, 1.6, (0.3, 4, 3), (0.5, 3, 2))
    for x in (-7, 7):
        cv.line([(x, 38), (x * 0.9, 31)], 1.3, (150, 160, 190))
    cuff = spline([(-22, -8), (22, -8), (24, 8), (0, 12), (-24, 8)], True, 6)
    solid(cv, cuff, Linear((0, -8), (0, 12), [(0, (140, 170, 220)), (1, (84, 110, 176))]), None, 1.6, (0.3, 3, 2), (0.4, 2, 1.5))
    return []


def leg(cv):
    m, poly = cv.limb(LEG, [34, 29, 21], orange(14, 30, 100))
    bands(cv, LEG, m, STRIPE, every=17, length=46, w=4.6, start=0.4, end=0.95)
    cv.outline(poly, 1.7)
    return [(0, 0, "hip", -42, -4), (14, 50, "knee", 44, 0), (4, 98, "ankle", -44, 6)]


def foot(cv):
    sole = spline([(-30, 26), (-30, 36), (62, 36), (72, 30), (66, 22)], True, 6)
    solid(cv, sole, Linear((0, 22), (0, 38), [(0, (226, 230, 240)), (1, (150, 160, 186))]), None, 1.6, None, None)
    upper = spline([(-20, -8), (-26, 10), (-30, 28), (-24, 30), (60, 30), (70, 26), (64, 14), (46, 4), (24, -2), (8, -8)], True, 6)
    m = solid(cv, upper, Radial((20, 0), 60, [(0, WHITE), (0.7, (240, 244, 252)), (1, (190, 202, 224))]), None, 1.7, (0.3, 5, 3), (0.5, 3, 2))
    cv.line([(40, 4), (52, 14), (56, 28)], 1.4, (120, 135, 170))                      # toe cap seam
    for i in range(3):
        cv.line([(6 + i * 11, -4 + i * 1.5), (14 + i * 11, 6 + i * 1.5)], 2.2, (70, 110, 200))   # laces
    cv.line([(-22, 0), (-8, 4)], 1.4, (120, 135, 170))
    cv.stroke([(-26, 20), (-26, 6), (-22, -4)], 4, 4, (100, 130, 200), alpha=0.9)
    return [(0, 0, "ankle", -44, -8)]


TAIL = [(0, 0), (-46, 6), (-86, -22), (-96, -70), (-76, -112), (-48, -126)]


def tail(cv):
    m, poly = cv.limb(TAIL, [28, 24, 21, 19, 17, 15], orange(-50, -40, 130))
    bands(cv, TAIL, m, STRIPE, every=20, length=44, w=5.4, start=0.1, end=0.92)
    cv.outline(poly, 1.7)
    cv.clip(m, lambda t: t.dot(-48, -126, 9, STRIPE, 0))
    cv.outline(poly, 1.7)
    return [(-48, -126, "tail tip", 36, -14)]


def _seg(cv, widths, L, fill, band_start=0.3):
    path = [(0, 0), (0, L / 2), (0, L)]
    m, poly = cv.limb(path, widths, fill)
    bands(cv, path, m, STRIPE, every=17, length=46, w=4.6, start=band_start, end=0.95)
    cv.outline(poly, 1.7)
    return []


def arm_up(cv):
    return _seg(cv, [28, 26, 23], 46, orange(10, 20, 90), 0.4)


def arm_lo(cv):
    return _seg(cv, [23, 21, 18], 46, orange(10, 20, 90), 0.25)


def leg_up(cv):
    return _seg(cv, [36, 33, 29], 50, orange(14, 30, 100), 0.4)


def leg_lo(cv):
    return _seg(cv, [29, 25, 21], 50, orange(14, 30, 100), 0.25)


def muzzle_asm(cv):
    return muzzle(cv, backing=False)


# part -> (draw fn, canvas w, canvas h, local x at canvas centre, local y at canvas centre)
SPEC = {
    "head": (head, 200, 180, 0, 0), "ear": (ear, 100, 110, 0, 0), "eyes": (eyes, 180, 110, 0, -10),
    "muzzle": (muzzle, 210, 140, 0, 0), "mouth": (mouth, 130, 110, 0, 10), "torso": (torso, 200, 230, 0, 0),
    "arm": (arm, 100, 120, 0, 46), "glove": (glove, 100, 90, 0, 24), "leg": (leg, 100, 130, 0, 50),
    "foot": (foot, 150, 70, 20, 14), "tail": (tail, 220, 190, -50, -60), "muzzle_asm": (muzzle_asm, 210, 140, 0, 0),
    "arm_up": (arm_up, 70, 90, 0, 22), "arm_lo": (arm_lo, 70, 90, 0, 22), "leg_up": (leg_up, 80, 90, 0, 24), "leg_lo": (leg_lo, 80, 90, 0, 24),
}

# assembled character: (part, x, y, z, mirror, rotation)
ASSEMBLY = [
    ("tail", -56, 96, 0, False, 0),
    ("leg", 30, 112, 1, False, 0), ("leg", -30, 112, 1, True, 0),
    ("foot", 34, 210, 1, False, 0), ("foot", -34, 210, 1, True, 0),
    ("torso", 0, 30, 2, False, 0),
    ("arm", 70, -24, 3, False, 0), ("arm", -70, -24, 3, True, 0),
    ("glove", 73, 68, 4, False, 0), ("glove", -73, 68, 4, True, 0),
    ("ear", 52, -130, 4, False, -16), ("ear", -52, -130, 4, True, 16),
    ("head", 0, -72, 5, False, 0),
    ("eyes", 0, -86, 6, False, 0), ("muzzle_asm", 0, -44, 6, False, 0),
]
