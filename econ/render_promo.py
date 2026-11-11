#!/usr/bin/env python3
"""Cinematic promo renderer (built on render_course.py): fast "slam" cuts with glimpses of the course in the opening,
a dark pause and a flash reveal, quick part-by-part journey, camera push and punch zooms, a big
"WATCH THE FULL CLASS" call-to-action screen, plus music and sound effects synced to the key words.

python3 render_promo.py econ00p_promo "Econ00p - Course Promo.mp4"            (run from econ/, after voice.py)
python3 render_promo.py --still econ00p_promo 2,10,20 sheet.jpg

Music is made here from scratch (no samples): drums, strings, a plucked ostinato, risers, whooshes and impacts.
It has no sustained low drone (the user heard the old music bed as a "vibrating" sound), strings are filtered above
200 Hz, and the whole music bus is ducked far under the voice whenever she speaks.
"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render_econ as E
import render_course as RC
from render_econ import F, W, H, R, WHITE, DIM, GOLD, AMBER, ACC, GREEN, ease, ease_out, back, txt, glow_text, \
    pill_sprite, paste_center, put, ANIMS

RED = (255, 90, 90)


def slam(t, t0, d=0.28):
    """1 -> big-to-normal scale curve for a 'slam' entrance."""
    u = (t - t0) / d
    return 1.0 + 1.4 * (1 - ease_out(u)) if u < 1 else 1.0


class Promo(RC.Course):
    def __init__(self, mod):
        super().__init__(mod)
        self.C = self.S.CHAPTER
        self.t_focus1 = self.focus_list[0][0] if self.focus_list else 1e9
        self.hook_kws = [k for k in self.kws if k["t"] < self.t_center and k["label"]]
        self.map_kws = [k for k in self.kws if self.t_center <= k["t"] < self.t_focus1 and k["label"]]
        self.cta_kws = [k for k in self.kws if self.t_outro and k["t"] >= self.t_outro and k["label"]]
        self.t_link = next((k["t"] for k in self.cta_kws if "link" in k["label"].lower()), None)
        self.all_kw_t = sorted(k["t"] for k in self.kws if k["label"])
        self._bgcache = {}

    # ---------------------------------------------------------------- opening
    def glimpse(self, name, t, a):
        """A course animation / the map, dimmed, as the backdrop of a hook card."""
        if name == "map":
            im = self.draw_map(1e9, done=tuple(self.topic))
        else:
            im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
            box = (415, 90, 1505, 990)
            d.rounded_rectangle(box, radius=30, fill=(16, 24, 50, 235), outline=ACC + (120,), width=2)
            ANIMS[name](im, d, box, a)
        z = 1.06 + 0.04 * min(1, a / 4)                         # slow push on the glimpse
        im = zoom(im, z, (960, 540))
        return Image.blend(im, Image.new("RGB", (W, H)), 0.58)

    def draw_hook(self, t):
        shown = [k for k in self.hook_kws if t >= k["t"]]
        if not shown:                                          # first half-second: dark, a glow gathering
            im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im, "RGBA")
            g = ease(t / 0.6)
            d.ellipse((960 - 500 * g, 540 - 160 * g, 960 + 500 * g, 540 + 160 * g), fill=GOLD + (int(40 * g),))
            return im.filter(ImageFilter.GaussianBlur(60))
        k = shown[-1]
        t_line_end = next((l["end"] for l in self.lines if l["i"] == k["line"]), k["t"] + 3)
        # the "pause" line after the last question: the card fades into darkness
        dark = ease((t - (t_line_end + 0.3)) / 1.2) if k is self.hook_kws[-1] else 0.0
        bgname = self.C.get("hook_bg", {}).get(k["label"])
        im = self.glimpse(bgname, t, t - k["t"] + 1.6) if bgname else E.BG.copy()
        d = ImageDraw.Draw(im, "RGBA")
        # light streaks across the frame
        for j in range(5):
            x = ((t * 900 + j * 420) % 2600) - 340
            d.polygon([(x, 0), (x + 60, 0), (x - 240, H), (x - 300, H)], fill=GOLD + (10,))
        sc = slam(t, k["t"])
        a = min(1, (t - k["t"]) / 0.08)
        # shake on impact
        sh = max(0, 1 - (t - k["t"]) / 0.25)
        ox, oy = 14 * sh * math.sin(t * 90), 10 * sh * math.cos(t * 77)
        if k["emoji"]: put(im, k["emoji"], (960 + ox, 330 + oy), int(210 * sc), a)
        f = F("InterDisplay-Black", int(150 * min(sc, 1.6)))
        glow_text(im, (960 + ox, 640 + oy), k["label"], f, GOLD, glow=GOLD, anchor="mm", alpha=a, radius=18)
        # white flash on each cut
        fl = max(0, 1 - (t - k["t"]) / 0.14)
        if fl > 0: im = Image.blend(im, Image.new("RGB", (W, H), (255, 255, 255)), 0.55 * fl)
        if dark > 0: im = Image.blend(im, Image.new("RGB", (W, H)), min(1, dark) * 0.92)
        return letterbox(im, 1 - ease((t - (self.t_center - 0.2)) / 0.6))

    # ---------------------------------------------------------------- call to action
    def draw_outro(self, t):
        im = E.BG.copy(); d = ImageDraw.Draw(im, "RGBA")
        t0 = self.t_outro
        for j in range(18):                                     # confetti of course icons
            x = 80 + (j * 211) % 1760; y = ((t * 120 + j * 157) % 1300) - 120
            put(im, ("🎓", "📚", "✨", "💡", "🗺️", "🚀")[j % 6], (x, y), 54 + (j % 3) * 16, 0.22)
        pul = 0.5 + 0.5 * math.sin(t * 3)
        d.ellipse((360, 120, 1560, 520), fill=GOLD + (int(18 + 14 * pul),))
        sc = slam(t, t0 + 0.2, 0.4)
        a = min(1, max(0, (t - t0 - 0.2) / 0.15))
        glow_text(im, (960, 270), "WATCH THE", F("InterDisplay-Black", int(70 * sc)), WHITE, anchor="mm", alpha=a, radius=10)
        glow_text(im, (960, 380), "FULL CLASS", F("InterDisplay-Black", int(150 * sc)), GOLD, glow=GOLD, anchor="mm",
                  alpha=a, radius=20)
        # the key words of the invitation, one at a time under the title
        shown = [k for k in self.cta_kws if t >= k["t"] and "link" not in k["label"].lower()]
        if shown and (self.t_link is None or t < self.t_link):
            k = shown[-1]; s2 = slam(t, k["t"], 0.22); a2 = min(1, (t - k["t"]) / 0.1)
            if k["emoji"]: put(im, k["emoji"], (960 - 260, 560), int(80 * s2), a2)
            txt(im, (960 + 40, 560), k["label"], F("InterDisplay-Bold", int(64 * min(s2, 1.4))), WHITE, alpha=a2, anchor="mm")
        # "Follow the link below" + bouncing arrows, from the moment "link" is spoken to the end
        if self.t_link is not None and t >= self.t_link:
            u = ease_out((t - self.t_link) / 0.4)
            s3 = slam(t, self.t_link, 0.3)
            pw, ph = int(1180 * min(1.15, s3)), int(150 * min(1.15, s3))
            y = 640
            d.rounded_rectangle((960 - pw // 2, y - ph // 2, 960 + pw // 2, y + ph // 2), radius=ph // 2,
                                fill=RED + (int(240 * u),), outline=(255, 255, 255, int(255 * u)), width=6)
            glow_text(im, (960, y), "FOLLOW THE LINK BELOW", F("InterDisplay-Black", int(78 * min(1.15, s3))), WHITE,
                      anchor="mm", alpha=u, radius=8)
            bob = 22 * abs(math.sin((t - self.t_link) * 4))
            for x in (760, 960, 1160):
                ay = 800 + bob
                d.polygon([(x - 60, ay), (x + 60, ay), (x, ay + 80)], fill=GOLD + (int(255 * u),))
                d.rectangle((x - 18, ay - 70, x + 18, ay), fill=GOLD + (int(255 * u),))
            txt(im, (960, 1010), "Click the link below to watch the complete class", F("Inter-SemiBold", 40), WHITE,
                alpha=u * (0.75 + 0.25 * pul), anchor="mm")
            fl = max(0, 1 - (t - self.t_link) / 0.14)
            if fl > 0: im = Image.blend(im, Image.new("RGB", (W, H), (255, 255, 255)), 0.45 * fl)
        return im

    # ---------------------------------------------------------------- the edit
    def frame(self, t):
        tc = self.t_center
        if t < tc: return self.draw_hook(t)
        if self.t_outro and t >= self.t_outro:
            u = ease((t - self.t_outro) / 0.35)
            im = self.draw_outro(t)
            if u < 1: im = Image.blend(self.draw_recap(t), im, u)
            f = ease((t - (self.total - 0.8)) / 0.8)
            return Image.blend(im, Image.new("RGB", (W, H)), f) if f > 0 else im
        if self.t_recap and t >= self.t_recap:
            u = ease((t - self.t_recap) / 0.4); im = self.draw_recap(t)
            if u < 1:
                tf, tid = self.focus_list[-1]; im = Image.blend(self.board(t, tid, tf), im, u)
            return self.camera(im, t, self.t_recap)
        cur = [(tf, tid) for tf, tid in self.focus_list if tf <= t]
        if not cur:
            im = self.draw_map(t)
            fl = max(0, 1 - (t - tc) / 0.25)                   # flash reveal of the title
            if fl > 0: im = Image.blend(im, Image.new("RGB", (W, H), (255, 255, 255)), 0.8 * fl)
            im = self.overlay_words(im, t)
            return self.camera(im, t, tc)
        k = len(cur) - 1; tf, tid = cur[-1]
        done = tuple(x for _, x in self.focus_list[:k])
        T_out = 0.35 if k else 0.0; T_hl, T_in = T_out + 0.7, T_out + 1.1     # quicker cuts than a class
        a = t - tf
        if a < T_out:
            ptf, ptid = self.focus_list[k - 1]
            im = self.zoom(self.draw_map(t, done=done), self.board(t, ptid, ptf), self.pos[ptid], 1 - ease(a / T_out))
        elif a < T_hl:
            im = self.draw_map(t, hl=tid, hl_u=(a - T_out) / 0.5, done=done, dim=ease((a - T_out) / 0.3))
        elif a < T_in:
            u = ease((a - T_hl) / (T_in - T_hl))
            im = self.zoom(self.draw_map(t, hl=tid, hl_u=1, done=done, dim=1), self.board(t, tid, tf), self.pos[tid], u)
        else:
            im = self.board(t, tid, tf)
        return self.camera(im, t, tf)

    def board(self, t, tid, tf):
        return self.draw_board(t, tid, tf + 1.1)

    def overlay_words(self, im, t):
        """Key words spoken over the map appear big in the lower third."""
        shown = [k for k in self.map_kws if t >= k["t"]]
        if not shown: return im
        k = shown[-1]; s = slam(t, k["t"], 0.22); a = min(1, (t - k["t"]) / 0.1)
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle((0, 900, W, 1040), fill=(5, 8, 18, int(200 * a)))
        f = F("InterDisplay-Black", int(84 * min(s, 1.4)))
        wd = f.getlength(k["label"]) + (110 if k["emoji"] else 0)
        x = 960 - wd / 2
        if k["emoji"]: put(im, k["emoji"], (x + 45, 970), int(80 * min(s, 1.4)), a); x += 110
        glow_text(im, (x, 970), k["label"], f, GOLD, glow=GOLD, anchor="lm", alpha=a, radius=12)
        return im

    def camera(self, im, t, t_scene):
        """Slow push-in over each scene + a small punch zoom on every key word."""
        z = 1.0 + 0.035 * min(1, (t - t_scene) / 6)
        last = max([x for x in self.all_kw_t if x <= t] or [-9])
        z += 0.025 * max(0, 1 - (t - last) / 0.22)
        return zoom(im, z, (960, 540))


def zoom(im, z, c):
    if z <= 1.001: return im
    w, h = W / z, H / z
    x0 = min(max(c[0] - w / 2, 0), W - w); y0 = min(max(c[1] - h / 2, 0), H - h)
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)


def letterbox(im, u):
    if u <= 0: return im
    d = ImageDraw.Draw(im); b = int(96 * min(1, u))
    d.rectangle((0, 0, W, b), fill=(0, 0, 0)); d.rectangle((0, H - b, W, H), fill=(0, 0, 0))
    return im


# ==================================================================== sound: music + effects + voice
SR = 48000


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def bandnoise(n, lo, hi, rng):
    from scipy.signal import butter, sosfilt
    x = rng.standard_normal(n)
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def add(buf, i, y, g=1.0):
    i = int(i)
    if i >= len(buf) or i + len(y) <= 0: return
    if i < 0: y = y[-i:]; i = 0
    m = min(len(y), len(buf) - i); buf[i:i + m] += g * y[:m]


def kick(rng):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 110 * np.exp(-tt / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.09)


def clap(rng):
    n = int(0.2 * SR); return bandnoise(n, 900, 5000, rng) * env_exp(n, 0.05) * 0.6


def hat(rng):
    n = int(0.05 * SR); return bandnoise(n, 7000, 15000, rng) * env_exp(n, 0.012) * 0.35


def impact(rng, big=1.0):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    f = 34 + 90 * np.exp(-tt / 0.06)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.35)
    crash = bandnoise(n, 300, 9000, rng) * env_exp(n, 0.5) * 0.35
    return (boom + crash) * big


def riser(rng, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 220 * (6 ** (tt / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    noi = bandnoise(n, 2000, 12000, rng) * 0.5
    return (tone + noi) * (tt / dur) ** 2


def whoosh(rng, dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    w = bandnoise(n, 500, 6000, rng)
    return w * np.sin(np.pi * tt / dur) ** 2 * 0.8


def pad_chord(freqs, dur):
    """Soft strings: detuned saws, filtered to 200 Hz - 2.4 kHz, slow attack/release."""
    from scipy.signal import butter, sosfilt
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for f0 in freqs:
        for det in (-0.006, 0, 0.007):
            ph = (f0 * (1 + det) * tt) % 1.0; y += 2 * ph - 1
    y = sosfilt(butter(2, [200, 2400], "band", fs=SR, output="sos"), y)
    a = np.minimum(1, tt / 0.6) * np.minimum(1, (dur - tt) / 0.6)
    return y * a / (len(freqs) * 3)


def pluck(f0, dur=0.22):
    n = int(dur * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * tt) + 0.3 * np.sin(4 * np.pi * f0 * tt)) * env_exp(n, 0.06)


NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
# A minor epic loop: Am - F - C - G (MIDI notes)
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]


def promo_mix(mod, total, out):
    import soundfile as sf
    from scipy.signal import resample_poly, butter, sosfiltfilt
    rng = np.random.default_rng(3)
    base = os.path.join(E.HERE, "out", mod)
    v, sr = sf.read(os.path.join(base, "voice.wav"))
    v = resample_poly(v, SR, sr); v = sosfiltfilt(butter(4, 75, "high", fs=SR, output="sos"), v)
    TL = json.load(open(os.path.join(base, "timeline.json")))
    ev = [(l["start"], l["ev"] or "") for l in TL["lines"]]
    t_center = next(t for t, e in ev if e == "center")
    t_focus = [t for t, e in ev if e.startswith("focus")]
    t_recap = next(t for t, e in ev if e.startswith("recap"))
    t_outro = next(t for t, e in ev if e.startswith("outro"))
    kws = [k for l in TL["lines"] for k in l.get("kw", []) if k.get("label")]
    hook_k = [k["t"] for k in kws if k["t"] < t_center]
    t_pause = max(hook_k) + 1.4 if hook_k else t_center - 3      # the dark "pause" before the reveal
    n = int(total * SR) + SR
    mus, sfx = np.zeros(n), np.zeros(n)
    BEAT = 60 / 120
    K, C_, Hh = kick(rng), clap(rng), hat(rng)

    def section(t):
        if t < t_pause: return "hook"
        if t < t_center: return "pause"
        if t < t_recap: return "drive"
        if t < t_outro: return "build"
        return "finale"

    # drums + ostinato on a 120 BPM grid
    step = BEAT / 4
    for s in range(int(total / step)):
        t = s * step; sec = section(t); b16 = s % 16
        if sec == "pause" or t > total - 3.2: continue
        if sec in ("hook", "drive", "finale"):
            if b16 % 4 == 0: add(mus, t * SR, K, 0.9)
            if b16 in (4, 12): add(mus, t * SR, C_, 0.8)
            if b16 % 2 == 0: add(mus, t * SR, Hh, 0.9)
        if sec == "build":
            if b16 in (0, 8): add(mus, t * SR, K, 0.8)
            if b16 % 4 == 2: add(mus, t * SR, Hh, 0.7)
        chord = CHORDS[int(t / (BEAT * 8)) % 4]
        if sec in ("hook", "drive", "finale") or (sec == "build" and b16 % 2 == 0):
            arp = [chord[0], chord[1], chord[2], chord[1] + 12][b16 % 4] + 12
            add(mus, t * SR, pluck(NOTE(arp)), 0.18)
    # strings, two bars per chord (not in the pause, so the reveal lands in silence)
    bar2 = BEAT * 8
    for c in range(int(total / bar2) + 1):
        t = c * bar2
        if section(t) == "pause": continue
        y = pad_chord([NOTE(m) for m in CHORDS[c % 4]], bar2 + 0.6)
        g = 0.5 if section(t) == "hook" else 0.7
        add(mus, t * SR, y, g)
    mus[int(t_pause * SR):int((t_center + 0.05) * SR)] *= 0          # the pause: music cuts out
    # effects
    for tk in hook_k: add(sfx, (tk - 0.02) * SR, impact(rng, 0.7))                 # a hit on every opening cut
    add(sfx, (t_center - 2.4) * SR, riser(rng, 2.4), 0.6)                          # suspense into the reveal
    add(sfx, (t_center - 0.02) * SR, impact(rng, 1.2))                             # the reveal
    for tf in t_focus: add(sfx, (tf - 0.3) * SR, whoosh(rng), 0.55)               # a whoosh into every part
    add(sfx, (t_recap - 0.3) * SR, whoosh(rng, 0.8), 0.6)
    add(sfx, (t_outro - 1.6) * SR, riser(rng, 1.6), 0.5)
    add(sfx, (t_outro - 0.02) * SR, impact(rng, 1.0))
    t_link = next((k["t"] for k in kws if "link" in k["label"].lower()), None)
    if t_link: add(sfx, (t_link - 0.02) * SR, impact(rng, 0.8))
    t_last = max(k["t"] for k in kws)
    add(sfx, (t_last - 0.02) * SR, impact(rng, 1.2))
    # bus processing: music never under 60 Hz, ducked far under the voice
    mus = sosfiltfilt(butter(2, 60, "high", fs=SR, output="sos"), mus)
    vv = np.zeros(n); vv[:min(n, len(v))] = v[:n]
    e = np.abs(vv); win = int(0.03 * SR)
    e = np.convolve(e, np.ones(win) / win, "same")
    speaking = (e > 0.02 * np.abs(vv).max()).astype(float)
    rel = int(0.35 * SR)                                                           # smooth release
    speaking = np.convolve(speaking, np.ones(rel) / rel, "same").clip(0, 1) ** 0.5
    duck = 1 - 0.78 * speaking                                                     # about -13 dB under speech
    def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 1e-6] ** 2)) if np.any(np.abs(x) > 1e-6) else 1
    v_rms = rms(vv)
    mus *= (v_rms * 10 ** (-9 / 20)) / rms(mus)                                    # music bed level vs. voice
    sfx *= (v_rms * 10 ** (-4 / 20)) / max(1e-9, np.abs(sfx).max() / 3)
    mix = vv + mus * duck + sfx * (1 - 0.5 * speaking)
    fade = int(2.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix /= np.abs(mix).max() / 0.95
    sf.write(out, mix.astype(np.float32), SR)


if __name__ == "__main__":
    E.Film = Promo
    R.audio_mix = promo_mix
    if sys.argv[1] == "--still":
        E.BG = E.make_bg(); fl = Promo(sys.argv[2])
        ims = [fl.frame(float(x)).resize((640, 360)) for x in sys.argv[3].split(",")]
        sheet = Image.new("RGB", (640 * 3, 360 * ((len(ims) + 2) // 3)))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(sys.argv[4])
    elif sys.argv[1] == "--audio":
        E.HERE = os.getcwd()
        tl = json.load(open(os.path.join("out", sys.argv[2], "timeline.json")))
        promo_mix(sys.argv[2], tl["total"], sys.argv[3])
    else:
        E.main()
