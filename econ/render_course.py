#!/usr/bin/env python3
"""Course renderer: the screen follows the voice. No sentence subtitles, only the key words.

python3 render_course.py econ00_trailer "Econ00 - Course Trailer.mp4"        (run from econ/, after voice.py)
python3 render_course.py --still econ00_trailer 5,20,40 sheet.jpg

Script markup (see voice.py): {spoken words|Label|emoji} pops "Label" + emoji at the moment the words are
spoken; {spoken words|@topic} makes that topic fly out on the mind map at that moment.
Screens: hook (key words + emoji, big) -> "agenda" (Aaj ki class mein: numbered items) -> mind map ->
topic boards (stage with emoji / animations on the left, key-word chips on the right) -> recap -> outro.
"""
import os, sys, math
import render_econ as E
from render_econ import (Film, F, W, H, R, BG, WHITE, DIM, GOLD, AMBER, ACC, GREEN, ease, ease_out, back, txt,
                         glow_text, pill_sprite, paste_center, put, ANIMS)
from PIL import Image, ImageDraw

CHIP = {"pt": ((24, 44, 92), ACC), "ex": ((70, 50, 5), AMBER)}


def pop(t, t0, d=0.35):
    return back((t - t0) / d) if t >= t0 else 0.0


class Course(Film):
    def __init__(self, mod):
        super().__init__(mod)
        self.lines = self.TL["lines"]
        self.kws = [dict(k, line=l["i"], ev=l["ev"] or "") for l in self.lines for k in l.get("kw", [])]
        for k in self.kws:
            if k["topic"] and k["topic"] in self.appear: self.appear[k["topic"]] = k["t"]
        self.t_center = self.t_of("center") or 0
        self.t_agenda = next((t for t, e in self.ev if e.startswith("agenda")), None)
        self.sections = sorted([l["start"] for l in self.lines if (l["ev"] or "").startswith(
            ("hook", "agenda", "center", "focus", "recap", "outro", "end"))] + [1e9])
        self.t_end = next((t for t, e in self.ev if e == "end"), None)
        self._logo = None

    def kw_between(self, t0, t1):
        return [k for k in self.kws if t0 <= k["t"] < t1 and k["label"]]

    def next_section(self, t):
        return next(s for s in self.sections if s > t + 1e-6)

    # ---- hook: key words appear big, one under the other, with their emoji
    def draw_hook(self, t):
        im = E.BG.copy()
        C = self.S.CHAPTER
        for k in range(14):
            x = 120 + (k * 137) % 1700; y = ((t * 90 + k * 211) % 1300) - 150
            put(im, C.get("rain", "✨"), (x, y), 60 + (k % 3) * 20, 0.18)
        end = self.t_agenda if self.t_agenda is not None else self.t_center
        ks = self.kw_between(0, end)
        shown = [k for k in ks if t >= k["t"]][-4:]
        y0 = 540 - 75 * (len(shown) - 1)
        for j, k in enumerate(shown):
            u = pop(t, k["t"]); newest = j == len(shown) - 1
            f = F("InterDisplay-Black", 92 if newest else 64)
            col = GOLD if newest else (200, 210, 238)
            w = f.getlength(k["label"]) + (130 if k["emoji"] else 0)
            x = 960 - w / 2; y = y0 + j * 150
            if k["emoji"]: put(im, k["emoji"], (x + 50, y), int((100 if newest else 70) * max(0.01, u)), min(1, u * 2))
            glow_text(im, (x + (130 if k["emoji"] else 0), y + 20 * (1 - min(1, u))), k["label"], f, col,
                      glow=GOLD if newest else None, anchor="lm", alpha=min(1, u * 2) * (1 if newest else 0.7), radius=14)
        return im

    # ---- "Aaj ki class mein": numbered items appear as they are spoken
    def draw_agenda(self, t):
        im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        u = ease_out((t - self.t_agenda) / 0.6)
        glow_text(im, (960, 130), self.S.CHAPTER.get("agenda_title", "AAJ KI CLASS MEIN"), F("InterDisplay-Black", 74), GOLD,
                  glow=GOLD, anchor="mm", alpha=u, radius=12)
        items = self.kw_between(self.t_agenda, self.t_center)
        for j, k in enumerate(items):
            a = ease_out((t - k["t"]) / 0.45)
            if a <= 0: continue
            y = 260 + j * 170; x = 330 + 60 * (1 - a)
            d.rounded_rectangle((x - 30, y, 1620, y + 140), radius=36, fill=(22, 32, 64, int(235 * a)),
                                outline=ACC + (int(160 * a),), width=3)
            d.ellipse((x, y + 30, x + 80, y + 110), fill=GOLD + (int(255 * a),))
            txt(im, (x + 40, y + 70), str(j + 1), F("InterDisplay-Black", 46), (25, 18, 0), alpha=a, anchor="mm")
            if k["emoji"]: put(im, k["emoji"], (x + 160, y + 70), 84, a)
            txt(im, (x + 230, y + 70), k["label"], F("InterDisplay-Bold", 54), WHITE, alpha=a, anchor="lm")
        return im

    # ---- topic board: stage on the left, key-word chips on the right
    def chip_layout(self, tid, tf):
        if getattr(self, "_cl", (None,))[0] == tid: return self._cl[1]
        t_end = self.next_section(tf)
        X0, X1, fs = 1190, 1870, 40
        rows, y = [], 190
        for l in self.lines:
            if not (tf <= l["start"] < t_end): continue
            ks = [k for k in l.get("kw", []) if k["label"]]
            if not ks: continue
            ev = l["ev"] or ""
            kind = "ex" if ev.startswith("ex:") else "pt"
            pre = ev.split(":", 1)[1] if ev.startswith(("pt:", "ex:")) else ""
            items, x = [], X0
            if pre:
                f = F("InterDisplay-Bold", 34)
                items.append(dict(kind="pre", text=pre, x=x, y=y, t=l["start"], f=f)); y += 52
            for k in ks:
                f = F("InterDisplay-Bold", fs)
                ew = E.emo(k["emoji"], 40).width + 12 if k["emoji"] else 0
                w = f.getlength(k["label"]) + 44 + ew
                if w > X1 - X0:                               # very long label: smaller font so it fits
                    f = F("InterDisplay-Bold", max(22, int(fs * (X1 - X0 - 44 - ew) / f.getlength(k["label"]))))
                    w = f.getlength(k["label"]) + 44 + ew
                if x + w > X1 and x > X0: x = X0; y += 76
                items.append(dict(kind=kind, text=k["label"], emoji=k["emoji"], ew=ew, x=x, y=y, w=w, t=k["t"], f=f))
                x += w + 16
            y += 76 + 26
            rows.append(items)
        # keep the newest rows on screen: page when the column is full
        pages, cur, top = [], [], 190
        for r in rows:
            h = r[-1]["y"] - r[0]["y"] + 76
            if cur and r[0]["y"] - top + h > 860:
                pages.append(cur); top = r[0]["y"] - 190; cur = []
            for it in r: it["page_dy"] = top - 190
            cur.append(r)
        if cur: pages.append(cur)
        self._cl = (tid, pages)
        return pages

    def draw_board(self, t, tid, t0):
        im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        tp = self.topic[tid]
        u = ease_out((t - t0) / 0.6)
        lab = tp["label"].upper()
        sp = pill_sprite([(lab, "InterDisplay-Black", 30, (25, 18, 0))], GOLD, fill=GOLD, pad=(26, 10), border=0)
        paste_center(im, sp, (70 + sp.width / 2, 70), back((t - t0) / 0.5), min(1, (t - t0) * 3))
        glow_text(im, (70 + sp.width + 30, 70), tp["name"], F("InterDisplay-Black", 56), WHITE, glow=ACC, anchor="lm", alpha=u, radius=10)
        put(im, tp["icon"], (1830, 70), 70, u)
        box = (50, 140, 1140, 1040)
        d.rounded_rectangle(box, radius=30, fill=(16, 24, 50, int(235 * u)), outline=ACC + (int(120 * u),), width=2)
        tf = next(f for f, x in self.focus_list if x == tid)
        anims = [(ta, n) for ta, n in self.anims.get(tid, []) if ta <= t]
        bars = self.S.CHAPTER.get("bars", {})
        if anims and anims[-1][1] in bars:
            ta, name = anims[-1]; self.bars(im, d, box, t, ta, bars[name])
        elif anims and anims[-1][1] != "none":
            ta, name = anims[-1]; ANIMS[name](im, d, box, t - ta)
        else:
            self.stage(im, d, box, t, tid, tf)
        pages = self.chip_layout(tid, tf)
        pi = max([i for i, pg in enumerate(pages) if t >= pg[0][0]["t"]] or [0])
        for row in (pages[pi] if pages else []):
            for it in row:
                a = ease_out((t - it["t"]) / 0.35)
                if a <= 0: continue
                y = it["y"] - it["page_dy"]
                if it["kind"] == "pre":
                    txt(im, (it["x"], y), it["text"], it["f"], GOLD, alpha=a); continue
                fill, edge = CHIP[it["kind"]]
                sc = 1 + 0.25 * max(0, 1 - (t - it["t"]) / 0.3)
                x0, w = it["x"], it["w"]
                d.rounded_rectangle((x0, y, x0 + w, y + 64), radius=32, fill=fill + (int(240 * a),), outline=edge + (int(255 * a),), width=3)
                tx = x0 + 22
                if it["emoji"]: put(im, it["emoji"], (tx + (it["ew"] - 12) / 2, y + 32), int(40 * sc), a); tx += it["ew"]
                txt(im, (tx, y + 32), it["text"], it["f"], WHITE if it["kind"] == "pt" else (255, 225, 160), alpha=a, anchor="lm")
        return im

    def bars(self, im, d, box, t, ta, spec):
        """Bar chart on the stage: bar i grows when the i-th key word after the chart starts is spoken."""
        x0, y0, x1, y1 = box
        txt(im, ((x0 + x1) / 2, y0 + 70), spec["title"], F("InterDisplay-Bold", 40), WHITE, anchor="mm")
        ks = [k for k in self.kws if k["t"] >= ta - 0.05 and k["label"]][:len(spec["bars"])]
        vmax = max(v for _, v, _ in spec["bars"])
        n = len(spec["bars"]); bw = min(240, (x1 - x0 - 200) / n - 60)
        base = y1 - 140; hmax = y1 - y0 - 330
        d.line([(x0 + 80, base), (x1 - 80, base)], fill=WHITE + (200,), width=4)
        for i, (lab, v, col) in enumerate(spec["bars"]):
            tk = ks[i]["t"] if i < len(ks) else 1e9
            u = ease_out((t - tk) / 0.8)
            cx = x0 + 100 + (i + 0.5) * (x1 - x0 - 200) / n
            h = hmax * v / vmax * u
            if u > 0:
                d.rounded_rectangle((cx - bw / 2, base - h, cx + bw / 2, base), radius=16, fill=col + (255,))
                txt(im, (cx, base - h - 40), f"{int(round(v * u)):,}", F("InterDisplay-Black", 54), col, anchor="mm")
            txt(im, (cx, base + 50), lab, F("InterDisplay-Bold", 32), WHITE if u > 0 else DIM, anchor="mm")

    def draw_end(self, t):
        """Channel end screen: logo, tagline words as they are spoken, next-class card."""
        im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        C = self.S.CHAPTER
        if self._logo is None:
            lg = Image.open(os.path.join(E.HERE, C["logo"])).convert("RGBA")
            sz = 520; lg = lg.resize((sz, sz), Image.LANCZOS)
            m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((4, 4, sz - 4, sz - 4), fill=255)
            lg.putalpha(m); self._logo = lg
        a = ease_out((t - self.t_end) / 0.7)
        pul = 0.5 + 0.5 * math.sin(t * 2.5)
        r = 290 + 10 * pul
        for w_, al in ((26, 0.18), (14, 0.35), (6, 1.0)):                          # soft glowing gold ring
            d.ellipse((960 - r, 420 - r, 960 + r, 420 + r), outline=GOLD + (int(255 * al * a * (0.7 + 0.3 * pul)),), width=w_)
        paste_center(im, self._logo, (960, 420), 0.85 + 0.15 * back((t - self.t_end) / 0.7), a)
        allk = [k for k in self.kws if k["t"] >= self.t_end and k["label"] and k["label"] != C.get("channel")]
        acts = [k for k in allk if not k["label"].endswith(".")]          # Like, Share, Comment, Subscribe
        ks = [k for k in allk if k["label"].endswith(".")]                # See it. Understand it. Remember it.
        if acts:
            fb = F("InterDisplay-Bold", 40); bw = [fb.getlength(k["label"]) + 120 for k in acts]
            bx = 960 - (sum(bw) + 24 * (len(acts) - 1)) / 2
            for j, k in enumerate(acts):
                u = ease_out((t - k["t"]) / 0.3); x0b = bx; bx += bw[j] + 24
                if u <= 0: continue
                sub = "ubscribe" in k["label"]
                col = (230, 40, 40) if sub else (30, 44, 84)
                sc = 1 + 0.15 * max(0, 1 - (t - k["t"]) / 0.3)
                h2 = 36 * sc
                d.rounded_rectangle((x0b, 765 - h2, x0b + bw[j], 765 + h2), radius=int(h2), fill=col + (int(245 * u),),
                                    outline=(WHITE if sub else ACC) + (int(255 * u),), width=3)
                if k["emoji"]: put(im, k["emoji"], (x0b + 40, 765), int(40 * sc), u)
                txt(im, (x0b + 72, 765), k["label"], fb, WHITE, alpha=u, anchor="lm")
        ft = F("InterDisplay-Black", 58); gap = 60
        widths = [ft.getlength(k["label"]) for k in ks]
        x = 960 - (sum(widths) + gap * (len(ks) - 1)) / 2
        for j, k in enumerate(ks):
            u = ease_out((t - k["t"]) / 0.35)
            cx = x + widths[j] / 2; x += widths[j] + gap
            if u <= 0: continue
            glow_text(im, (cx, (855 if acts else 790) + 20 * (1 - u)), k["label"], ft, (GOLD, WHITE, (70, 210, 140))[j % 3],
                      glow=GOLD if j == 0 else None, anchor="mm", alpha=u, radius=10)
        nt = C.get("next_title")
        if nt:
            u = ease_out((t - self.t_end - 0.4) / 0.6)
            d.rounded_rectangle((560, 900, 1360, 1010), radius=55, fill=(22, 32, 64, int(235 * u)), outline=ACC + (int(200 * u),), width=3)
            txt(im, (960, 955), "▶  " + nt, F("InterDisplay-Bold", 38), WHITE, alpha=u, anchor="mm")
        f = ease((t - (self.total - 1.0)) / 1.0)
        return Image.blend(im, Image.new("RGB", (W, H)), f) if f > 0 else im

    def stage(self, im, d, box, t, tid, tf):
        """No hand-made animation: the topic's emoji pop onto the stage as their words are spoken."""
        x0, y0, x1, y1 = box
        ks = [k for k in self.kw_between(tf, self.next_section(tf)) if k["emoji"]]
        shown = [k for k in ks if t >= k["t"]]
        if not shown:
            put(im, self.topic[tid]["icon"], ((x0 + x1) / 2, (y0 + y1) / 2 + 6 * math.sin(t * 2)), 260, 1); return
        newest = shown[-1]
        older = shown[:-1][-8:]
        for j, k in enumerate(older):                       # small ones along the bottom
            cx = x0 + 110 + j * 125; cy = y1 - 120
            put(im, k["emoji"], (cx, cy), 90, 0.85)
        u = pop(t, newest["t"], 0.45)
        put(im, newest["emoji"], ((x0 + x1) / 2, y0 + 330 + 8 * math.sin(t * 3)), int(300 * max(0.05, u)), min(1, u * 2))
        fsz = 64
        while fsz > 30 and F("InterDisplay-Black", fsz).getlength(newest["label"]) > (x1 - x0) - 80: fsz -= 2
        glow_text(im, ((x0 + x1) / 2, y0 + 580), newest["label"], F("InterDisplay-Black", fsz), GOLD, glow=GOLD,
                  anchor="mm", alpha=min(1, u * 2), radius=12)

    # ---- recap: the same items, ticked as they are spoken
    def draw_recap(self, t):
        im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        a = ease_out((t - self.t_recap) / 0.6)
        txt(im, (960, 120), self.S.CHAPTER.get("recap_title", "RECAP"), F("InterDisplay-Black", 72), GOLD, alpha=a, anchor="mm")
        items = self.kw_between(self.t_recap, self.t_outro or 1e9)
        for j, k in enumerate(items):
            u = ease_out((t - k["t"]) / 0.4)
            if u <= 0: continue
            y = 230 + j * 130; x = 420
            d.rounded_rectangle((x - 30, y, 1500, y + 104), radius=30, fill=(22, 32, 64, int(230 * u)), outline=ACC + (int(150 * u),), width=2)
            d.ellipse((x, y + 27, x + 50, y + 77), fill=GREEN + (int(255 * u),))
            d.line([(x + 13, y + 52), (x + 22, y + 62), (x + 38, y + 40)], fill=(255, 255, 255, int(255 * u)), width=5)
            if k["emoji"]: put(im, k["emoji"], (x + 110, y + 52), 64, u)
            txt(im, (x + 170, y + 52), k["label"], F("InterDisplay-Bold", 44), WHITE, alpha=u, anchor="lm")
        return im

    def frame(self, t):
        if self.t_end is not None and t >= self.t_end:
            u = ease((t - self.t_end) / 0.7); im = self.draw_end(t)
            return Image.blend(self.draw_outro(t), im, u) if u < 1 else im
        if self.t_agenda is not None and self.t_agenda <= t < self.t_center:
            u = ease((t - self.t_agenda) / 0.7); im = self.draw_agenda(t)
            return Image.blend(self.draw_hook(t), im, u) if u < 1 else im
        if self.t_agenda is not None and self.t_center <= t < self.t_center + 0.8:
            return Image.blend(self.draw_agenda(t), self.draw_map(t), ease((t - self.t_center) / 0.8))
        return super().frame(t)


E.Film = Course

if __name__ == "__main__":
    sys.argv = sys.argv  # same command line as render_econ
    import render_econ
    render_econ.Film = Course
    if sys.argv[1] == "--still":
        render_econ.BG = E.make_bg(); fl = Course(sys.argv[2])
        ims = [fl.frame(float(x)).resize((640, 360)) for x in sys.argv[3].split(",")]
        sheet = Image.new("RGB", (640 * 3, 360 * ((len(ims) + 2) // 3)))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(sys.argv[4])
    else:
        render_econ.main()
