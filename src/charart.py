"""Drawing toolkit for the detailed character art.

Everything is drawn in "units" on a transparent canvas at S pixels per unit, so shapes are smooth
(smooth spline outlines, radial/linear gradients, soft shading, clipped patterns).
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

OL = (34, 24, 28)


def tone(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ geometry
def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * p1[i]) + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2
                        + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3) for i in range(2))


def spline(pts, closed=False, n=10):
    P = [tuple(p) for p in pts]
    k = len(P)
    seq = (P[-1:] + P + P[:2]) if closed else ([P[0]] + P + [P[-1]])
    out = []
    for i in range(1, (k + 1) if closed else k):
        for j in range(n):
            out.append(_cr(seq[i - 1], seq[i], seq[i + 1], seq[i + 2], j / n))
    if not closed:
        out.append(P[-1])
    return out


def mirror_pts(right):
    """Right half (top to bottom, x >= 0) -> closed outline symmetric about x = 0."""
    left = [(-x, y) for x, y in reversed(right) if x != 0]
    return list(right) + left


def ell(cx, cy, rx, ry, rot=0.0, n=96):
    out = []
    c, s = math.cos(rot), math.sin(rot)
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def limb_poly(path, widths, smooth=True, n=10):
    """Closed outline (with round caps) of a tapered limb following `path`."""
    pts = spline(path, False, n) if smooth else list(path)
    N = len(pts)
    ws = np.interp(np.linspace(0, 1, N), np.linspace(0, 1, len(widths)), widths)
    L, Rr, nrm = [], [], []
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(N - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        d = math.hypot(tx, ty) or 1
        tx, ty = tx / d, ty / d
        nx, ny = -ty, tx
        nrm.append((nx, ny))
        L.append((p[0] + nx * ws[i] / 2, p[1] + ny * ws[i] / 2))
        Rr.append((p[0] - nx * ws[i] / 2, p[1] - ny * ws[i] / 2))
    out = list(L)
    th = math.atan2(nrm[-1][1], nrm[-1][0])
    for k in range(1, 12):
        a = th - math.pi * k / 12
        out.append((pts[-1][0] + math.cos(a) * ws[-1] / 2, pts[-1][1] + math.sin(a) * ws[-1] / 2))
    out += Rr[::-1]
    th0 = math.atan2(-nrm[0][1], -nrm[0][0])
    for k in range(1, 12):
        a = th0 - math.pi * k / 12
        out.append((pts[0][0] + math.cos(a) * ws[0] / 2, pts[0][1] + math.sin(a) * ws[0] / 2))
    return out


def ribbon_poly(path, widths, n=10):
    """Open tapered ribbon (pointed ends allowed) for stripes, whiskers, fur strokes."""
    pts = spline(path, False, n)
    N = len(pts)
    ws = np.interp(np.linspace(0, 1, N), np.linspace(0, 1, len(widths)), widths)
    L, Rr = [], []
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(N - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        d = math.hypot(tx, ty) or 1
        nx, ny = -ty / d, tx / d
        L.append((p[0] + nx * ws[i] / 2, p[1] + ny * ws[i] / 2))
        Rr.append((p[0] - nx * ws[i] / 2, p[1] - ny * ws[i] / 2))
    return L + Rr[::-1]


# ------------------------------------------------------------------ gradients
class Radial:
    def __init__(self, c, r, stops):
        self.c, self.r, self.stops = c, r, stops

    def render(self, cv, bb):
        x0, y0, x1, y1 = bb
        xs = np.arange(x0, x1) + 0.5
        ys = np.arange(y0, y1) + 0.5
        cx, cy = cv.P(*self.c)
        d = np.sqrt((xs[None, :] - cx) ** 2 + (ys[:, None] - cy) ** 2) / (self.r * cv.S)
        return _apply(d, self.stops, bb)


class Linear:
    def __init__(self, p0, p1, stops):
        self.p0, self.p1, self.stops = p0, p1, stops

    def render(self, cv, bb):
        x0, y0, x1, y1 = bb
        xs = np.arange(x0, x1) + 0.5
        ys = np.arange(y0, y1) + 0.5
        ax, ay = cv.P(*self.p0)
        bx, by = cv.P(*self.p1)
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1
        t = ((xs[None, :] - ax) * dx + (ys[:, None] - ay) * dy) / L2
        return _apply(t, self.stops, bb)


def _apply(t, stops, bb):
    t = np.clip(t, 0, 1)
    ts = [s[0] for s in stops]
    out = np.zeros(t.shape + (4,), dtype=np.uint8)
    for ch in range(3):
        out[..., ch] = np.interp(t, ts, [s[1][ch] for s in stops]).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, "RGBA")


# ------------------------------------------------------------------ canvas
class Cv:
    def __init__(self, w, h, S=4, cx=0.0, cy=0.0):
        """w x h units; (cx, cy) is the local coordinate shown at the canvas centre."""
        self.w, self.h, self.S, self.cx, self.cy = w, h, S, cx, cy
        self.im = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))

    def like(self):
        return Cv(self.w, self.h, self.S, self.cx, self.cy)

    def P(self, x, y):
        return ((x - self.cx + self.w / 2) * self.S, (y - self.cy + self.h / 2) * self.S)

    def PP(self, pts):
        return [self.P(x, y) for x, y in pts]

    def mask(self, pts):
        m = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(m).polygon(self.PP(pts), fill=255)
        return m

    def overlay(self, mask, color, alpha=1.0):
        bb = mask.getbbox()
        if not bb:
            return
        layer = Image.new("RGBA", (bb[2] - bb[0], bb[3] - bb[1]), tuple(color[:3]) + (255,))
        a = mask.crop(bb)
        if alpha < 1:
            a = a.point(lambda v: int(v * alpha))
        layer.putalpha(a)
        self.im.alpha_composite(layer, (bb[0], bb[1]))

    def paint(self, mask, fill, alpha=1.0):
        bb = mask.getbbox()
        if not bb:
            return
        if isinstance(fill, tuple):
            layer = Image.new("RGBA", (bb[2] - bb[0], bb[3] - bb[1]), tuple(fill[:3]) + (255,))
        else:
            layer = fill.render(self, bb)
        a = mask.crop(bb)
        if alpha < 1:
            a = a.point(lambda v: int(v * alpha))
        layer.putalpha(a)
        self.im.alpha_composite(layer, (bb[0], bb[1]))

    def outline(self, pts, w=1.6, color=OL, closed=True):
        m = Image.new("L", self.im.size, 0)
        pp = self.PP(pts)
        if closed:
            pp = pp + [pp[0]]
        ImageDraw.Draw(m).line(pp, fill=255, width=max(1, int(w * self.S)), joint="curve")
        self.overlay(m, color)

    def shade(self, mask, alpha=0.3, d=5, blur=3, color=(70, 30, 20), toward=(1, -1)):
        """Darken the edge of `mask` facing away from `toward` (default: light from the upper right)."""
        dpx = int(d * self.S)
        sm = Image.new("L", self.im.size, 0)
        sm.paste(mask, (int(toward[0] * dpx), int(toward[1] * dpx)))
        reg = ImageChops.subtract(mask, sm).filter(ImageFilter.GaussianBlur(blur * self.S))
        reg = ImageChops.multiply(reg, mask)
        self.overlay(reg, color, alpha)

    def highlight(self, mask, alpha=0.4, d=4, blur=2.5, color=(255, 250, 225)):
        self.shade(mask, alpha, d, blur, color, toward=(-1, 1))

    def shape(self, pts, fill, ow=1.6, shade=(0.32, 6, 3.5), hl=(0.38, 3.5, 2.2), ol=OL):
        m = self.mask(pts)
        self.paint(m, fill)
        if shade:
            self.shade(m, shade[0], shade[1], shade[2])
        if hl:
            self.highlight(m, hl[0], hl[1], hl[2])
        if ow:
            self.outline(pts, ow, ol)
        return m

    def clip(self, mask, fn):
        t = self.like()
        fn(t)
        a = ImageChops.multiply(t.im.getchannel("A"), mask)
        t.im.putalpha(a)
        self.im.alpha_composite(t.im)

    def stroke(self, path, w0, w1, color, n=10, ow=0, alpha=1.0):
        poly = ribbon_poly(path, [w0, (w0 + w1) / 2, w1], n)
        m = self.mask(poly)
        self.overlay(m, color, alpha)
        if ow:
            self.outline(poly, ow)
        return m

    def line(self, path, w, color=OL, smooth=True, n=10):
        pts = spline(path, False, n) if smooth else path
        m = Image.new("L", self.im.size, 0)
        d = ImageDraw.Draw(m)
        pp = self.PP(pts)
        d.line(pp, fill=255, width=max(1, int(w * self.S)), joint="curve")
        r = w * self.S / 2
        for p in (pp[0], pp[-1]):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)
        self.overlay(m, color)

    def dot(self, x, y, r, color, ow=0):
        pts = ell(x, y, r, r, n=40)
        m = self.mask(pts)
        self.overlay(m, color)
        if ow:
            self.outline(pts, ow)

    def limb(self, path, widths, fill, ow=1.6, shade=(0.34, 5, 3), hl=(0.35, 3, 2), n=10):
        poly = limb_poly(path, widths, True, n)
        m = self.shape(poly, fill, ow, shade, hl)
        return m, poly


def bands(cv, path, mask, color, every=14.0, length=44, w=5.0, alpha=0.9, start=0.15, end=0.9):
    """Stripes that cross a limb/tail path at regular spacing, clipped to `mask`."""
    pts = spline(path, False, 10)
    total = 0.0
    seg = [0.0]
    for a, b in zip(pts, pts[1:]):
        total += math.hypot(b[0] - a[0], b[1] - a[1])
        seg.append(total)

    def draw(t):
        d = start * total
        while d < end * total:
            i = min(range(len(seg)), key=lambda k: abs(seg[k] - d))
            a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            n = math.hypot(tx, ty) or 1
            nx, ny = -ty / n, tx / n
            p = pts[i]
            t.stroke([(p[0] - nx * length / 2, p[1] - ny * length / 2), p, (p[0] + nx * length / 2, p[1] + ny * length / 2)],
                     w, w, color, alpha=alpha)
            d += every
    cv.clip(mask, draw)
