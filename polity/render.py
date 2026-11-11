#!/usr/bin/env python3
"""Mind-map video renderer.  python3 render.py ch01_sample "Ch01 - Historical Background (sample).mp4"

Reads out/<script>/timeline.json (voice.py) and draws 1920x1080 frames with PIL:
hook screen -> chapter in the centre -> hubs and topics fly out -> per topic: highlight + catchy label on the map,
zoom into the topic board, points grow out one by one as they are spoken (💡 examples in amber) -> recap -> outro.
"""
import os, sys, json, math, importlib, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
INTER = "/usr/share/fonts/opentype/inter/"
DEVA = "/usr/local/share/fonts/noto/NotoSansDevanagari-Black.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

BG0, BG1 = (8, 12, 26), (18, 27, 54)
WHITE, DIM = (241, 245, 255), (150, 165, 205)
GOLD, AMBER = (255, 209, 102), (255, 183, 3)
SIDE = dict(company=(255, 140, 50), crown=(46, 196, 182))
CENTER = (120, 160, 255)

_fc = {}


_fname = {}
DEVA_DIR = os.path.dirname(DEVA) + "/NotoSansDevanagari-"


def F(name, size):
    k = (name, size)
    if k not in _fc:
        if name == "deva": path = DEVA
        elif name.startswith("deva-"): path = DEVA_DIR + name[5:] + ".ttf"
        else: path = INTER + name + ".otf"
        _fc[k] = ImageFont.truetype(path, size)
        _fname[id(_fc[k])] = k
    return _fc[k]


def is_deva(text):
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def fit(font, text):
    """Inter has no Devanagari: for Hindi text swap to Noto Sans Devanagari of a similar weight, same size."""
    k = _fname.get(id(font))
    if not k or not is_deva(text) or k[0].startswith("deva"): return font
    n = k[0]
    w = ("Black" if "Black" in n else "Bold" if "Bold" in n and "Semi" not in n else
         "SemiBold" if "SemiBold" in n else "Medium" if "Medium" in n else "Regular")
    return F("deva-" + w, k[1])


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1, max(0, x)); return 1 - (1 - x) ** 3


def back(x):
    x = min(1, max(0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def lerp(a, b, u):
    return tuple(p + (q - p) * u for p, q in zip(a, b))


def wrap(text, font, width):
    font = fit(font, text)
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out


# ------------------------------------------------------------------ static backgrounds
def make_bg():
    yy, xx = np.mgrid[:H, :W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 1.6
    a = np.clip(r, 0, 1)[..., None]
    img = (np.array(BG1) * (1 - a) + np.array(BG0) * a)
    # dot grid
    g = ((xx % 48 == 0) & (yy % 48 == 0))
    img[g] += 14
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


BG = None
BULB = None


def bulb(size):
    global BULB
    if BULB is None:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), "💡", font=f, embedded_color=True)
        BULB = im.crop(im.getbbox())
    return BULB.resize((int(BULB.width * size / BULB.height), size), Image.LANCZOS)


def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al); return im


def txt(base, xy, text, font, fill, alpha=1.0, anchor="la"):
    """Alpha-blended text (ImageDraw ignores fill alpha for text on RGB images)."""
    if alpha <= 0.01: return
    font = fit(font, text)
    if alpha >= 0.999 and len(fill) == 3:
        ImageDraw.Draw(base).text(xy, text, font=font, fill=fill, anchor=anchor); return
    a = (fill[3] / 255 if len(fill) == 4 else 1) * alpha
    bb = ImageDraw.Draw(base).textbbox(xy, text, font=font, anchor=anchor)
    box = (int(bb[0]) - 2, int(bb[1]) - 2, int(bb[2]) + 2, int(bb[3]) + 2)
    lay = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0] - box[0], xy[1] - box[1]), text, font=font, fill=tuple(fill[:3]) + (int(255 * a),), anchor=anchor)
    base.paste(lay, box[:2], lay)


def glow_text(base, xy, text, font, fill, glow=None, anchor="la", alpha=1.0, radius=10):
    """Text with a soft glow, alpha-blended onto base (RGB)."""
    x, y = xy
    font = fit(font, text)
    bb = ImageDraw.Draw(base).textbbox((x, y), text, font=font, anchor=anchor)
    pad = radius * 3
    box = (int(bb[0] - pad), int(bb[1] - pad), int(bb[2] + pad), int(bb[3] + pad))
    lay = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if glow:
        d.text((x - box[0], y - box[1]), text, font=font, fill=glow + (int(150 * alpha),), anchor=anchor)
        lay = lay.filter(ImageFilter.GaussianBlur(radius)); d = ImageDraw.Draw(lay)
    d.text((x - box[0], y - box[1]), text, font=font, fill=fill + (int(255 * alpha),), anchor=anchor)
    base.paste(lay, box[:2], lay)


# ------------------------------------------------------------------ node sprites
def pill_sprite(lines, accent, w=None, h=None, pad=(26, 14), fill=(20, 29, 58), border=2, glow=False):
    """lines: [(text, fontname, size, color)] centred. Returns RGBA sprite."""
    ws = [fit(F(f, s), t).getlength(t) for t, f, s, c in lines]
    hs = [s * 1.25 for t, f, s, c in lines]
    w = w or int(max(ws) + 2 * pad[0]); h = h or int(sum(hs) + 2 * pad[1])
    G = 40 if glow else 0
    im = Image.new("RGBA", (w + 2 * G, h + 2 * G), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if glow:
        d.rounded_rectangle((G, G, G + w, G + h), radius=h // 2, fill=accent + (200,))
        im = im.filter(ImageFilter.GaussianBlur(16)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((G, G, G + w - 1, G + h - 1), radius=min(h // 2, 40), fill=fill + (245,), outline=accent + (255,), width=border)
    y = G + (h - sum(hs)) / 2
    for (t, f, s, c), hh in zip(lines, hs):
        d.text((G + w / 2, y + hh / 2), t, font=fit(F(f, s), t), fill=c + (255,), anchor="mm"); y += hh
    return im


def paste_center(base, sp, xy, scale=1.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01: return
    if abs(scale - 1) > 0.01:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BILINEAR)
    sp = with_alpha(sp, alpha)
    base.paste(sp, (int(xy[0] - sp.width / 2), int(xy[1] - sp.height / 2)), sp)


def curve(d, p0, p1, u, color, width=3, bend=0.0):
    """Cubic from p0 to p1 (horizontal tangents), drawn up to fraction u."""
    if u <= 0: return
    (x0, y0), (x1, y1) = p0, p1
    mx = (x0 + x1) / 2
    c1, c2 = (mx, y0 + bend), (mx, y1 - bend)
    n = 40; pts = []
    for i in range(int(n * u) + 1):
        s = i / n
        x = (1 - s) ** 3 * x0 + 3 * (1 - s) ** 2 * s * c1[0] + 3 * (1 - s) * s * s * c2[0] + s ** 3 * x1
        y = (1 - s) ** 3 * y0 + 3 * (1 - s) ** 2 * s * c1[1] + 3 * (1 - s) * s * s * c2[1] + s ** 3 * y1
        pts.append((x, y))
    if len(pts) > 1: d.line(pts, fill=color, width=width, joint="curve")


# ------------------------------------------------------------------ the film
class Film:
    def __init__(self, mod):
        self.S = importlib.import_module(mod)
        self.out = os.path.join(HERE, "out", mod)
        self.TL = json.load(open(os.path.join(self.out, "timeline.json")))
        self.total = self.TL["total"]
        self.ev = [(l["start"], l["ev"]) for l in self.TL["lines"] if l["ev"]]
        self.t_of = lambda name: next((t for t, e in self.ev if e == name), None)
        self.topic = {tp["id"]: tp for tp in self.S.TOPICS}
        self.layout()
        self.focus_list = [(t, e.split(":", 1)[1]) for t, e in self.ev if e.startswith("focus:")]
        # points per focus
        self.points = {}
        for k, (tf, tid) in enumerate(self.focus_list):
            t_end = self.focus_list[k + 1][0] if k + 1 < len(self.focus_list) else 1e9
            self.points[tid] = [(t, e.split(":", 1)[0], e.split(":", 1)[1]) for t, e in self.ev
                                if tf <= t < t_end and e.split(":")[0] in ("pt", "ex")]
        self.t_recap = next((t for t, e in self.ev if e.startswith("recap")), None)
        self.t_outro = next((t for t, e in self.ev if e.startswith("outro")), None)
        self.sprites()

    # ---- map geometry
    def layout(self):
        self.pos = {"center": (960, 540), "company": (545, 540), "crown": (1375, 540)}
        for side, hub, sgn in (("company", self.pos["company"], -1), ("crown", self.pos["crown"], 1)):
            ids = [tp["id"] for tp in self.S.TOPICS if tp["side"] == side]
            n = len(ids)
            for i, tid in enumerate(ids):
                a = math.radians(-66 + 132 * i / max(1, n - 1))
                self.pos[tid] = (hub[0] + sgn * 330 * math.cos(a), hub[1] + 440 * math.sin(a))
        self.parent = {"company": "center", "crown": "center"}
        for tp in self.S.TOPICS: self.parent[tp["id"]] = tp["side"]
        acts_t = self.t_of("acts") or 0
        order = [tp["id"] for tp in self.S.TOPICS]
        self.appear = {"center": self.t_of("center") or 0,
                       "company": self.t_of("hub:company") or 0, "crown": self.t_of("hub:crown") or 0}
        for i, tid in enumerate(order): self.appear[tid] = acts_t + 0.3 + i * 0.16

    def sprites(self):
        C = self.S.CHAPTER
        self.sp = {"center": pill_sprite([(f"CHAPTER {C['num']}", "Inter-SemiBold", 22, DIM),
                                          (C["title"], "InterDisplay-Black", 36, WHITE)], CENTER, pad=(30, 20), border=3)}
        for side, hb in self.S.HUBS.items():
            self.sp[side] = pill_sprite([(hb["title"], "InterDisplay-Bold", 30, WHITE), (hb["years"], "Inter-Medium", 21, SIDE[side])],
                                        SIDE[side], pad=(24, 14), border=3)
        for tp in self.S.TOPICS:
            acc = SIDE[tp["side"]]
            self.sp[tp["id"]] = pill_sprite([(tp["year"], "InterDisplay-Black", 26, acc), (tp["name"], "Inter-Medium", 18, WHITE)],
                                            acc, w=250, pad=(16, 8))
            self.sp[tp["id"] + "_hl"] = pill_sprite([(tp["year"], "InterDisplay-Black", 26, acc), (tp["name"], "Inter-Medium", 18, WHITE)],
                                                    acc, w=250, pad=(16, 8), border=3, glow=True)
        for side in ("company", "crown"):
            hb = self.S.HUBS[side]
            self.sp[side + "_hl"] = pill_sprite([(hb["title"], "InterDisplay-Bold", 30, WHITE), (hb["years"], "Inter-Medium", 21, SIDE[side])],
                                                SIDE[side], pad=(24, 14), border=3, glow=True)

    def label_of(self, tid):
        return (self.topic[tid]["label"] if tid in self.topic else self.S.HUBS[tid]["label"]).upper()

    def side_of(self, tid):
        return self.topic[tid]["side"] if tid in self.topic else tid

    # ---- map view
    def draw_map(self, t, hl=None, hl_u=0.0, done=(), dim_others=0.0, pulse=None):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        for nid, ta in self.appear.items():
            if t < ta: continue
            u = (t - ta) / 0.7
            par = self.parent.get(nid)
            p = self.pos[nid]
            if par:
                pp = self.pos[par]
                cur = lerp(pp, p, back(u)) if u < 1 else p
                col = SIDE.get(self.side_of(nid) if nid in self.topic else nid, CENTER)
                al = 0.35 if (hl and nid != hl and dim_others) else 0.8
                curve(d, pp, p, ease_out(u * 1.2), col + (int(255 * al),), width=3 if nid in self.topic else 4)
            else:
                cur = p
        for nid, ta in self.appear.items():
            if t < ta: continue
            u = (t - ta) / 0.7
            par = self.parent.get(nid)
            cur = lerp(self.pos[par], self.pos[nid], back(u)) if (par and u < 1) else self.pos[nid]
            sc = 0.3 + 0.7 * back(u) if u < 1 else 1
            al = min(1, u * 2)
            if hl and nid != hl: al *= 1 - 0.55 * dim_others
            key = nid
            if nid == hl or nid == pulse:
                key = nid + "_hl" if (nid + "_hl") in self.sp else nid
                sc *= 1 + 0.06 * math.sin(t * 5) * (hl_u if nid == hl else 1)
            paste_center(im, self.sp[key], cur, sc, al)
            if nid in done:
                x, y = cur; r = 15
                d.ellipse((x + 105, y - 40, x + 105 + 2 * r, y - 40 + 2 * r), fill=(60, 200, 120, 255))
                d.line([(x + 112, y - 25), (x + 118, y - 19), (x + 128, y - 33)], fill=(255, 255, 255, 255), width=4)
        if hl and hl_u > 0:
            lab = self.label_of(hl)
            if lab:
                sp = pill_sprite([(lab, "InterDisplay-Black", 30, (25, 18, 0))], GOLD, fill=GOLD, pad=(28, 12), border=0)
                x, y = self.pos[hl]
                y_lab = y - 95 if y > 200 else y + 95
                x = min(max(x, sp.width / 2 + 30), W - sp.width / 2 - 30)
                paste_center(im, sp, (x, y_lab), back(hl_u * 1.3), min(1, hl_u * 3))
        return im

    # ---- topic board
    def board_layout(self, tid):
        """Rows at a readable size, split into pages that each fit the screen; each page centred vertically."""
        if hasattr(self, "_bl") and self._bl[0] == tid: return self._bl[1]
        items = self.points.get(tid, [])
        X0, X1, fs, gap, HMAX = 820, 1840, 34, 30, 860
        rows = []
        for (te, kind, text) in items:
            head, _, sub = text.partition("|")
            hf = F("Inter-SemiBold" if kind == "pt" else "Inter-MediumItalic", fs)
            sf_ = F("Inter-Regular", int(fs * 0.82))
            tw = X1 - X0 - (80 if kind == "ex" else 0)
            hl = wrap(head, hf, tw); sl = wrap(sub, sf_, tw) if sub else []
            h = len(hl) * fs * 1.28 + len(sl) * fs * 0.82 * 1.3 + (20 if kind == "ex" else 0)
            rows.append(dict(t=te, kind=kind, hl=hl, sl=sl, h=h, fs=fs))
        pages, cur, hh = [], [], 0
        for r in rows:
            if cur and hh + gap + r["h"] > HMAX:
                pages.append(cur); cur, hh = [], 0
            hh += (gap if cur else 0) + r["h"]; cur.append(r)
        if cur: pages.append(cur)
        for pg in pages:
            tot = sum(r["h"] for r in pg) + gap * (len(pg) - 1)
            y = 540 - tot / 2
            for r in pg:
                r["y"] = y; y += r["h"] + gap
        self._bl = (tid, pages)
        return pages

    def board_header(self, tid):
        if tid in self.topic:
            tp = self.topic[tid]; return tp["year"], tp["name"], self.S.HUBS[tp["side"]]["title"]
        hb = self.S.HUBS[tid]; return "1600", "The Company arrives", hb["title"] + "  ·  " + hb["years"]

    def draw_board(self, t, tid, t0):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        acc = SIDE[self.side_of(tid)]
        year, name, sub = self.board_header(tid)
        # watermark year
        txt(im, (1880, 1060), year, F("InterDisplay-Black", 380), acc, alpha=0.06, anchor="rd")
        # card
        u = ease_out((t - t0) / 0.6)
        cx0, cy0, cx1, cy1 = 80, 300, 660, 780
        d.rounded_rectangle((cx0, cy0, cx1, cy1), radius=28, fill=(22, 32, 64, int(235 * u)), outline=acc + (int(255 * u),), width=3)
        d.rectangle((cx0, cy0 + 30, cx0 + 8, cy1 - 30), fill=acc + (int(255 * u),))
        lab = self.label_of(tid)
        if lab:
            sp = pill_sprite([(lab, "InterDisplay-Black", 28, (25, 18, 0))], GOLD, fill=GOLD, pad=(24, 10), border=0)
            paste_center(im, sp, (cx0 + 40 + sp.width / 2 - 40, cy0), back((t - t0) / 0.5), min(1, (t - t0) * 3))
        glow_text(im, (cx0 + 50, cy0 + 70), year, F("InterDisplay-Black", 140), acc, glow=acc, alpha=u, radius=14)
        yy = cy0 + 240
        for ln in wrap(name, F("InterDisplay-Bold", 50), cx1 - cx0 - 90):
            txt(im, (cx0 + 50, yy), ln, F("InterDisplay-Bold", 50), WHITE, alpha=u); yy += 62
        txt(im, (cx0 + 50, cy1 - 60), sub.upper(), F("Inter-SemiBold", 22), DIM, alpha=u)
        # points (paged: when a new page starts, the old one slides up and fades)
        pages = self.board_layout(tid)
        pi = max([i for i, pg in enumerate(pages) if t >= pg[0]["t"] + 0.15] or [0])
        if pi > 0:
            o = ease((t - pages[pi][0]["t"]) / 0.5)
            if o < 1: self.draw_rows(im, d, t, pages[pi - 1], acc, cx1, shift=-80 * o, fade=1 - o)
        self.draw_rows(im, d, t, pages[pi], acc, cx1)
        return im

    def draw_rows(self, im, d, t, rows, acc, cx1, shift=0.0, fade=1.0):
        shown = [r for r in rows if t >= r["t"] + 0.15]
        for k, r in enumerate(shown):
            a = t - r["t"] - 0.15
            g = ease_out(a / 0.45)
            y = r["y"] + shift
            fs = r["fs"]; cy = y + fs * 0.64 + (6 if r["kind"] == "ex" else 0)
            col = AMBER if r["kind"] == "ex" else acc
            curve(d, (cx1, 540), (790, cy), g, col + (int(200 * fade),), width=3)
            if a > 0.3:
                rr = 9 * back((a - 0.3) / 0.25)
                d.ellipse((798 - rr, cy - rr, 798 + rr, cy + rr), fill=col + (int(255 * fade),))
            ta = ease_out((a - 0.3) / 0.45) * fade
            if ta <= 0: continue
            newest = k == len(shown) - 1 and fade == 1.0
            x = 830 + 30 * (1 - ease_out((a - 0.3) / 0.45))
            if r["kind"] == "ex":
                d.rounded_rectangle((x - 10, y - 8, 1860, y + r["h"] - 8), radius=18, fill=(70, 50, 5, int(150 * ta)),
                                    outline=AMBER + (int(200 * ta),), width=2)
                paste_center(im, bulb(int(fs * 1.25)), (x + 32, y + r["h"] / 2 - 8), 1, ta)
                x += 78; y += 6
            hc = (255, 225, 160) if r["kind"] == "ex" else (WHITE if newest else (200, 210, 238))
            for ln in r["hl"]:
                txt(im, (x, y), ln, F("Inter-SemiBold" if r["kind"] == "pt" else "Inter-MediumItalic", fs), hc, alpha=ta)
                y += fs * 1.28
            for ln in r["sl"]:
                txt(im, (x, y), ln, F("Inter-Regular", int(fs * 0.82)), DIM, alpha=ta)
                y += fs * 0.82 * 1.3

    # ---- hook / recap / outro
    def draw_hook(self, t):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        C = self.S.CHAPTER
        l1, l2 = C["hook_en"].split("\n")
        words = (l1 + " | " + l2).split()
        f = F("InterDisplay-Black", 82)
        y = 330; x0 = 960
        line, k = 1, 0
        for ln, col, yy in ((l1, WHITE, 360), (l2, GOLD, 470)):
            ws = ln.split()
            full = f.getlength(ln); x = x0 - full / 2
            for w in ws:
                ta = 0.5 + k * 0.32
                a = ease_out((t - ta) / 0.4)
                if a > 0:
                    glow_text(im, (x, yy + 18 * (1 - a)), w, f, col, glow=col if col == GOLD else None, alpha=a, radius=12)
                x += f.getlength(w + " "); k += 1
            k += 2
        a = ease_out((t - 6.0) / 0.8)
        if a > 0:
            txt(im, (960, 640), C["hook_hi"], F("Inter-SemiBold", 48), DIM, alpha=a, anchor="mm")
        q = ease_out((t - 9.5) / 0.6)
        if q > 0:
            txt(im, (960, 790), "?", F("InterDisplay-Black", 120), GOLD, alpha=q, anchor="mm")
        return im

    def draw_recap(self, t):
        im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        a = ease_out((t - self.t_recap) / 0.6)
        txt(im, (960, 170), "RECAP", F("InterDisplay-Black", 72), GOLD, alpha=a, anchor="mm")
        rows = [(te, e.split(":", 1)[1]) for te, e in self.ev if e.startswith("recap:")]
        y = 300
        for te, body in rows:
            tid, _, body_t = body.partition("|")
            u = ease_out((t - te) / 0.5)
            if u <= 0: continue
            tp = self.topic[tid]; acc = SIDE[tp["side"]]
            x = 260 + 40 * (1 - u)
            d.rounded_rectangle((x, y, x + 200, y + 92), radius=46, fill=acc + (int(255 * u),))
            txt(im, (x + 100, y + 46), tp["year"], F("InterDisplay-Black", 46), (15, 15, 25), alpha=u, anchor="mm")
            txt(im, (x + 240, y + 6), tp["name"], F("InterDisplay-Bold", 40), WHITE, alpha=u)
            for i, ln in enumerate(wrap(body_t.split("–", 1)[-1].strip(), F("Inter-Medium", 28), 1150)):
                txt(im, (x + 240, y + 58 + i * 36), ln, F("Inter-Medium", 28), DIM, alpha=u)
            y += 180
        return im

    def draw_outro(self, t):
        nxt = next((tp["id"] for tp in self.S.TOPICS if tp["id"] not in self.points), None)
        done = tuple(self.points)
        im = self.draw_map(t, hl=None, done=done, pulse=nxt)
        d = ImageDraw.Draw(im, "RGBA")
        a = ease_out((t - self.t_outro - 0.5) / 0.6)
        otext = next(e for _, e in self.ev if e.startswith("outro:")).split(":", 1)[1]
        d.rectangle((0, 920, W, 1080), fill=(5, 8, 18, int(220 * a)))
        glow_text(im, (960, 1000), otext, F("InterDisplay-Black", 54), GOLD, glow=GOLD, anchor="mm", alpha=a, radius=10)
        return im

    # ---- frame dispatcher
    def frame(self, t):
        tc = self.t_of("center") or 0
        if t < tc:
            return self.draw_hook(t)
        if t < tc + 0.8:   # hook dissolves into the map
            u = ease((t - tc) / 0.8)
            return Image.blend(self.draw_hook(t), self.draw_map(t), u)
        if self.t_outro and t >= self.t_outro:
            u = ease((t - self.t_outro) / 0.7)
            im = self.draw_outro(t)
            if u < 1: im = Image.blend(self.draw_recap(t), im, u)
            f = ease((t - (self.total - 1.2)) / 1.2)
            if f > 0: im = Image.blend(im, Image.new("RGB", (W, H)), f)
            return im
        if self.t_recap and t >= self.t_recap:
            u = ease((t - self.t_recap) / 0.7)
            im = self.draw_recap(t)
            if u < 1:
                tf, tid = self.focus_list[-1]
                im = Image.blend(self.draw_board(t, tid, tf + 2.6), im, u)
            return im
        cur = [(tf, tid) for tf, tid in self.focus_list if tf <= t]
        if not cur:
            return self.draw_map(t)
        k = len(cur) - 1; tf, tid = cur[-1]
        done = tuple(x for _, x in self.focus_list[:k])
        from_board = k > 0
        T_out = 0.6 if from_board else 0.0
        T_hl, T_in = T_out + 1.7, T_out + 2.5
        a = t - tf
        if a < T_out:      # zoom back out of the previous board
            ptf, ptid = self.focus_list[k - 1]
            return self.zoom(self.draw_map(t, done=done), self.draw_board(t, ptid, ptf + 2.6), self.pos[ptid], 1 - ease(a / T_out))
        if a < T_hl:
            return self.draw_map(t, hl=tid, hl_u=(a - T_out) / 0.8, done=done, dim_others=ease((a - T_out) / 0.5))
        if a < T_in:
            u = ease((a - T_hl) / (T_in - T_hl))
            mp = self.draw_map(t, hl=tid, hl_u=1, done=done, dim_others=1)
            return self.zoom(mp, self.draw_board(t, tid, tf + T_in), self.pos[tid], u)
        return self.draw_board(t, tid, tf + T_in)

    def zoom(self, mp, board, p, u):
        """u=0: map; u=1: board. Zoom into point p of the map while the board fades in."""
        z = 1 + 2.2 * u
        cx, cy = lerp((960, 540), p, u)
        w, h = W / z, H / z
        cx = min(max(cx, w / 2), W - w / 2); cy = min(max(cy, h / 2), H - h / 2)
        crop = mp.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((W, H), Image.BILINEAR)
        b = ease((u - 0.45) / 0.55)
        return Image.blend(crop, board, b) if b > 0 else crop


FILM = None


def seg_worker(args):
    mod, k, f0, f1, path = args
    global FILM, BG
    BG = make_bg(); FILM = Film(mod)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(FILM.frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    return path


def still(mod, times, dst):
    global BG
    BG = make_bg(); fl = Film(mod)
    ims = [fl.frame(t).resize((640, 360)) for t in times]
    cols = 3; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols, 360 * rows))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sheet.save(dst)


def audio_mix(mod, total, out):
    """Clean voice only: low rumble filtered out, plus a soft tick when a point appears.
    (No music bed or whooshes: the ducked drone under the voice was heard as a vibrating background sound.)"""
    import soundfile as sf
    from scipy.signal import resample_poly, butter, sosfiltfilt
    SR = 48000
    v, sr = sf.read(os.path.join(HERE, "out", mod, "voice.wav"))
    v = resample_poly(v, SR, sr)
    v = sosfiltfilt(butter(4, 75, "high", fs=SR, output="sos"), v)
    n = int(total * SR) + SR; mix = np.zeros(n); mix[:len(v)] += v[:n]
    TL = json.load(open(os.path.join(HERE, "out", mod, "timeline.json")))
    for l in TL["lines"]:
        if (l["ev"] or "").startswith(("pt:", "ex:")):
            i = int(l["start"] * SR) + int(0.45 * SR); tt = np.arange(int(0.08 * SR)) / SR
            y = np.sin(2 * np.pi * 1320 * tt) * np.exp(-tt * 60) * 0.025
            mix[i:i + len(y)] += y[:max(0, n - i)]
    mix /= np.abs(mix).max() / 0.9
    sf.write(out, mix.astype(np.float32), SR)


def main():
    mod = sys.argv[1]; name = sys.argv[2]
    out = os.path.join(HERE, "out", mod)
    total = json.load(open(os.path.join(out, "timeline.json")))["total"]
    nf = int(total * FPS); P = 4
    cuts = [nf * k // P for k in range(P + 1)]
    jobs = [(mod, k, cuts[k], cuts[k + 1], os.path.join(out, f"seg{k}.mp4")) for k in range(P)]
    with Pool(P) as pool:
        segs = pool.map(seg_worker, jobs)
    lst = os.path.join(out, "segs.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    vid = os.path.join(out, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    wav = os.path.join(out, "mix.wav"); audio_mix(mod, total, wav)
    final = os.path.join(HERE, "out", name)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", wav, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
    print("wrote", final)


if __name__ == "__main__":
    if sys.argv[1] == "--still":
        still(sys.argv[2], [float(x) for x in sys.argv[3].split(",")], sys.argv[4])
    else:
        main()
