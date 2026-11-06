#!/usr/bin/env python3
"""
"Is your deodorant spray safe?" — ~30 s English 9:16 short, built on ../tunguska_demo engine.

Fact-checked against the source transcript (claims that did not hold up were corrected or dropped):
  * Many Australian schools ban AEROSOL sprays (asthma / allergy risk).
  * Nov 2021: P&G VOLUNTARILY recalled some Old Spice & Secret aerosol sprays after benzene was found;
    FDA said levels found were not expected to cause harm. Benzene = IARC Group 1 carcinogen.
  * Aerosol cans use butane/propane as propellant. UK ONS: 11 death certificates 2001-2020 named deodorant
    inhalation (likely an undercount).
  * "Fragrance/parfum" on labels can hide undisclosed ingredients (trade secret).
  * Danish population study (n=1,189, Clin Exp Allergy 2005): 42% reported eye/airway symptoms from fragrance products.

Usage:  python3 make_video.py [--preview]        VOICE_FILE=narration.mp3 python3 make_video.py
"""
import os, sys, math, random, importlib.util, subprocess, json
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(HERE, "..", "tunguska_demo")
os.environ.setdefault("DATA_DIR", os.path.join(ENGINE_DIR, "data"))
spec = importlib.util.spec_from_file_location("engine", os.path.join(ENGINE_DIR, "make_video.py"))
E = importlib.util.module_from_spec(spec)
sys.modules["engine"] = E
spec.loader.exec_module(E)

W, H, FPS, SR = E.W, E.H, E.FPS, E.SR
F, label_box, add_glow, clamp, smooth, ease_out, back_out, lerp = (
    E.F, E.label_box, E.add_glow, E.clamp, E.smooth, E.ease_out, E.back_out, E.lerp)
RED, YELLOW, WHITE = E.RED, E.YELLOW, E.WHITE
DARK = (20, 20, 26)
E.OUT = os.path.join(HERE, "out")
os.makedirs(E.OUT, exist_ok=True)
E.LANG = "en-us"
E.VOICE = os.environ.get("VOICE", "am_michael")
E.SPEED = float(os.environ.get("SPEED", "1.08"))
E.TEMPO = float(os.environ.get("TEMPO", "1.1"))
E.PAUSE_SCALE = float(os.environ.get("PAUSE_SCALE", "0.8"))

E.SEGMENTS = [
    dict(scene="ban", gap=0.3,
         hi="This spray is banned in many Australian schools. | It can trigger asthma and allergies.",
         cap=["This spray is BANNED in many Australian schools.", "It can trigger ASTHMA and ALLERGIES."]),
    dict(scene="recall", gap=0.3,
         hi="In twenty twenty-one, Procter and Gamble recalled some aerosol sprays. | Tests found benzene, a cancer-causing chemical. | The levels were low, but it shouldn't be there at all.",
         cap=["In 2021, P&G RECALLED some aerosol sprays.", "Tests found BENZENE, a CANCER-causing chemical.",
              "The levels were low, but it shouldn't be there AT ALL."]),
    dict(scene="butane", gap=0.3,
         hi="Every can is filled with butane gas. | In the UK, inhaling deodorant was linked to eleven deaths.",
         cap=["Every can is filled with BUTANE gas.", "In the UK, INHALING deodorant was linked to 11 DEATHS."]),
    dict(scene="fragrance", gap=0.3,
         hi="And fragrance? It can hide chemicals no one has to disclose.",
         cap=["And FRAGRANCE? It can hide chemicals no one has to DISCLOSE."]),
    dict(scene="study", gap=0.3,
         hi="In one Danish study, forty-two percent said fragrances irritated their eyes or airways.",
         cap=["In one Danish study, 42% said fragrances irritated their EYES or AIRWAYS."]),
    dict(scene="end", gap=2.4, hi="So… is your spray really worth it?",
         cap=["So... is your spray REALLY WORTH IT?"]),
]


# ----------------------------------------------------------------------------- drawing helpers
def draw_can(img, cx, cy, h=520, body=(36, 70, 160), label="DEO", alpha_fill=True, cut=False, t=0.0):
    """Aerosol can, centre (cx, cy). cut=True draws a cross-section with butane inside."""
    d = ImageDraw.Draw(img)
    w = h * 0.38
    top, bot = cy - h / 2, cy + h / 2
    # cap + nozzle
    d.rounded_rectangle((cx - w * 0.32, top - h * 0.16, cx + w * 0.32, top + 8), radius=12, fill=(220, 224, 232), outline=(0, 0, 0), width=3)
    d.rectangle((cx + w * 0.2, top - h * 0.12, cx + w * 0.38, top - h * 0.08), fill=(60, 60, 70))
    d.ellipse((cx - w / 2, top - 18, cx + w / 2, top + 30), fill=(170, 175, 185), outline=(0, 0, 0), width=3)
    if not cut:
        # shaded cylinder: vertical stripes
        for i in range(int(w)):
            u = i / w
            shade = 0.55 + 0.6 * math.sin(math.pi * u) ** 0.8 - (0.25 if u > 0.8 else 0)
            col = tuple(int(clamp(c * shade / 255) * 255) for c in body)
            d.line((cx - w / 2 + i, top + 6, cx - w / 2 + i, bot - 6), fill=col)
        d.rectangle((cx - w * 0.28, top + 6, cx - w * 0.2, bot - 6), fill=tuple(min(255, c + 90) for c in body))
        d.rounded_rectangle((cx - w / 2, top + 4, cx + w / 2, bot), radius=14, outline=(0, 0, 0), width=4)
        d.text((cx, cy), label, font=F(h * 0.16), fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    else:
        d.rounded_rectangle((cx - w / 2, top + 4, cx + w / 2, bot), radius=14, fill=(18, 22, 34), outline=(220, 225, 235), width=6)
        liq = cy + h * 0.15
        d.rectangle((cx - w / 2 + 6, liq, cx + w / 2 - 6, bot - 8), fill=(60, 140, 190))
        d.line((cx, top + 10, cx, bot - 30), fill=(230, 230, 240), width=6)  # dip tube
        r = random.Random(7)
        for k in range(26):  # rising gas bubbles
            bx = cx + r.uniform(-w / 2 + 25, w / 2 - 25)
            ph = (t * r.uniform(0.25, 0.5) + r.random()) % 1
            by = lerp(liq - 10, top + 40, ph)
            br = r.uniform(6, 14)
            d.ellipse((bx - br, by - br, bx + br, by + br), outline=(255, 200, 90), width=4)
    d.ellipse((cx - w / 2, bot - 20, cx + w / 2, bot + 16), outline=(0, 0, 0), width=3)


def spray(d, x, y, t, n=70, length=420, spread=0.35, seed=1, col=(210, 230, 255)):
    r = random.Random(seed)
    for _ in range(n):
        ph = (t * 1.6 + r.random()) % 1
        a = r.uniform(-spread, spread)
        L = ph * length
        px, py = x + math.cos(a) * L, y + math.sin(a) * L - 40 * ph
        s = 3 + 9 * ph
        c = tuple(int(v * (1 - ph * 0.6)) for v in col)
        d.ellipse((px - s, py - s, px + s, py + s), fill=c)


def load_country(name, lon0):
    gj = json.load(open(os.path.join(os.environ["DATA_DIR"], "countries.geojson")))
    out = []
    for f in gj["features"]:
        if f["properties"].get("ADMIN") != name:
            continue
        g = f["geometry"]
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            r = np.array(poly[0], float)
            if np.ptp(r[:, 0]) * np.ptp(r[:, 1]) < 1:
                continue
            out.append(np.stack([(r[:, 0] - lon0) * np.cos(np.radians(r[:, 1])), r[:, 1]], 1))
    return out

AUS = load_country("Australia", 134)

def benzene(d, cx, cy, R, k=1.0):
    pts = [(cx + R * math.cos(math.pi / 6 + i * math.pi / 3), cy + R * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    n = int(6 * clamp(k) + 0.999)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % 6]
        d.line((a, b), fill=WHITE, width=10)
        if i % 2 == 0:  # alternating double bonds
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ia = (a[0] + (cx - mx) * 0.22, a[1] + (cy - my) * 0.22)
            ib = (b[0] + (cx - mx) * 0.22, b[1] + (cy - my) * 0.22)
            sh = 0.18
            d.line(((ia[0] * (1 - sh) + ib[0] * sh), (ia[1] * (1 - sh) + ib[1] * sh),
                    (ib[0] * (1 - sh) + ia[0] * sh), (ib[1] * (1 - sh) + ia[1] * sh)), fill=WHITE, width=8)
    for (x, y) in pts[:n]:
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(80, 80, 90), outline=WHITE, width=4)


def person(d, x, y, s, col):
    d.ellipse((x - 9 * s, y - 30 * s, x + 9 * s, y - 12 * s), fill=col)
    d.rounded_rectangle((x - 13 * s, y - 9 * s, x + 13 * s, y + 18 * s), radius=int(8 * s), fill=col)


def chunk_t(ctx, seg, j, frac=0.0):
    c = ctx["chunks_by_scene"][seg][j]
    return c[1] + frac * (c[2] - c[1]) - ctx["scene_start"]


# ----------------------------------------------------------------------------- scenes
def scene_ban(t, dur, ctx):
    img = E.BG_GRID.copy()
    d = ImageDraw.Draw(img)
    # Australia map (top)
    s, cx, cy = 13.5, 0, -26
    for P in AUS:
        pts = [(W / 2 + (x - cx) * s, 470 - (y - cy) * s) for x, y in P]
        d.polygon([(x, y + 8) for x, y in pts], fill=(120, 12, 22))
        d.polygon(pts, fill=(222, 38, 48), outline=(255, 140, 140), width=3)
    a = back_out((t - 0.1) / 0.3)
    label_box(img, W / 2, 230, "AUSTRALIAN SCHOOLS", 60, bg=DARK, scale=a)
    # can spraying
    bob = 6 * math.sin(t * 3)
    draw_can(img, 400, 1010 + bob, 470)
    d = ImageDraw.Draw(img)
    spray(d, 400 + 110, 1010 + bob - 300, t, length=480, spread=0.3)
    st = chunk_t(ctx, "ban", 0, 0.55)
    if t > st:
        label_box(img, 470, 1000, "BANNED", 130, scale=lerp(1.8, 1.0, ease_out((t - st) / 0.18)), rot=12)
    c1 = chunk_t(ctx, "ban", 1, 0.25)
    for i, txt in enumerate(["ASTHMA", "ALLERGIES"]):
        tt = c1 + i * 0.35
        if t > tt:
            label_box(img, 820, 760 + i * 120, txt, 54, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((t - tt) / 0.3))
    return img


def scene_recall(t, dur, ctx):
    img = E.BG_GRID.copy()
    c1 = chunk_t(ctx, "recall", 1)
    c2 = chunk_t(ctx, "recall", 2)
    if t < c1:
        label_box(img, W / 2, 230, "USA · 2021 · P&G", 60, bg=DARK, scale=back_out(t / 0.3))
        cols, rows = 4, 3
        for i in range(cols * rows):
            x = 190 + (i % cols) * 233
            y = 560 + (i // cols) * 300
            k = back_out((t - 0.1 - i * 0.05) / 0.25)
            if k > 0.05:
                draw_can(img, x, y, 230 * k, body=[(36, 70, 160), (150, 40, 60), (40, 120, 90)][i % 3], label="")
        st = 0.9
        if t > st:
            label_box(img, W / 2, 860, "RECALLED", 130, scale=lerp(1.8, 1.0, ease_out((t - st) / 0.18)), rot=-8)
    else:
        k = t - c1
        d = ImageDraw.Draw(img)
        glow = Image.new("RGB", (W // 2, H // 2))
        ImageDraw.Draw(glow).ellipse(((W / 2 - 300) / 2, (720 - 300) / 2, (W / 2 + 300) / 2, (720 + 300) / 2), fill=(90, 20, 20))
        img = add_glow(img, glow, 30)
        d = ImageDraw.Draw(img)
        benzene(d, W / 2, 720, 190, ease_out(k / 0.6))
        d.text((W / 2, 720), "C6H6", font=F(54), fill=(220, 225, 235), anchor="mm")
        label_box(img, W / 2, 230, "BENZENE", 78, scale=back_out(k / 0.3))
        if k > 0.7:
            label_box(img, W / 2, 1010, "GROUP 1 CARCINOGEN", 64, scale=back_out((k - 0.7) / 0.3), rot=-3)
            d = ImageDraw.Draw(img)
            d.text((W / 2, 1090), "WHO · IARC", font=F(34, "semi"), fill=(200, 205, 220), anchor="mm")
        if t > c2:
            label_box(img, W / 2, 1200, "FDA: levels found were low", 42, bg=DARK, scale=back_out((t - c2) / 0.3))
    return img


def scene_butane(t, dur, ctx):
    img = E.BG_GRID.copy()
    c1 = chunk_t(ctx, "butane", 1)
    if t < c1:
        draw_can(img, W / 2, 880, 760, cut=True, t=t)
        d = ImageDraw.Draw(img)
        k = back_out((t - 0.4) / 0.3)
        label_box(img, W / 2 + 330, 640, "BUTANE GAS", 50, bg=(200, 120, 20), scale=k)
        label_box(img, W / 2 - 330, 1080, "LIQUID", 46, bg=(40, 110, 160), scale=back_out((t - 0.7) / 0.3))
        for j in range(3):  # pressure arrows
            y = 760 - ((t * 120 + j * 70) % 210)
            d.polygon([(W / 2 - 240, y), (W / 2 - 220, y + 26), (W / 2 - 260, y + 26)], fill=YELLOW)
        label_box(img, W / 2, 230, "WHAT'S INSIDE?", 64, bg=DARK, scale=back_out(t / 0.3))
    else:
        k = t - c1
        d = ImageDraw.Draw(img)
        glow = Image.new("RGB", (W // 2, H // 2))
        n = int(11 * clamp(k / 1.2))
        ImageDraw.Draw(glow).text((W / 4, 640 / 2), str(n), font=F(230), fill=(140, 20, 20), anchor="mm")
        img = add_glow(img, glow, 18)
        d = ImageDraw.Draw(img)
        d.text((W / 2, 640), str(n), font=F(460), fill=(255, 70, 70), anchor="mm", stroke_width=8, stroke_fill=(40, 0, 0))
        label_box(img, W / 2, 230, "UNITED KINGDOM", 60, bg=DARK, scale=back_out(k / 0.3))
        if k > 0.4:
            label_box(img, W / 2, 960, "DEATHS · 2001–2020", 66, scale=back_out((k - 0.4) / 0.3))
            d = ImageDraw.Draw(img)
            d.text((W / 2, 1060), "deodorant inhalation (ONS)", font=F(36, "semi"), fill=(200, 205, 220), anchor="mm")
    return img


FR_MOLS = [(random.Random(i).uniform(-1, 1), random.Random(i + 99).uniform(-1, 1)) for i in range(26)]

def scene_fragrance(t, dur, ctx):
    img = E.BG_GRID.copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 120, 380, 960, 900
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(240, 238, 230), outline=(0, 0, 0), width=4)
    d.text((x0 + 40, y0 + 40), "INGREDIENTS:", font=F(46), fill=(20, 20, 20))
    lines = ["Butane, Isobutane, Propane,", "Alcohol Denat., Cyclopentasiloxane,", "Aluminium Chlorohydrate,"]
    for i, ln in enumerate(lines):
        d.text((x0 + 40, y0 + 120 + i * 62), ln, font=F(38, "semi"), fill=(60, 60, 60))
    fy = y0 + 120 + 3 * 62
    hl = smooth((t - 0.5) / 0.3)
    if hl > 0:
        pw = F(46).getlength("PARFUM (FRAGRANCE)")
        d.rounded_rectangle((x0 + 30, fy - 8, x0 + 50 + pw, fy + 58), radius=8, fill=YELLOW)
    d.text((x0 + 40, fy), "PARFUM (FRAGRANCE)", font=F(46), fill=(10, 10, 10))
    # hidden chemicals bursting out of the word
    k = ease_out((t - 0.9) / 1.0)
    if k > 0:
        ox, oy = x0 + 260, fy + 30
        for i, (ux, uy) in enumerate(FR_MOLS):
            px = ox + ux * 420 * k + 120 * k
            py = oy + 220 + abs(uy) * 330 * k
            r = 34
            d.ellipse((px - r, py - r, px + r, py + r), fill=(60, 64, 80), outline=(255, 214, 10), width=3)
            d.text((px, py), "?", font=F(40), fill=YELLOW, anchor="mm")
    label_box(img, W / 2, 230, "READ THE LABEL", 64, bg=DARK, scale=back_out(t / 0.3))
    st = dur * 0.55
    if t > st:
        label_box(img, W / 2, 1270, "TRADE SECRET", 92, scale=lerp(1.8, 1.0, ease_out((t - st) / 0.18)), rot=-6)
    return img


def scene_study(t, dur, ctx):
    img = E.BG_GRID.copy()
    d = ImageDraw.Draw(img)
    label_box(img, W / 2, 230, "DENMARK · 1,189 PEOPLE", 58, bg=DARK, scale=back_out(t / 0.3))
    n = int(42 * clamp((t - 0.6) / max(0.8, dur * 0.55)))
    for i in range(100):
        x = 165 + (i % 10) * 83
        y = 420 + (i // 10) * 80
        person(d, x, y, 1.45, (235, 60, 60) if i < n else (70, 74, 88))
    label_box(img, W / 2, 1250, f"{n}%  EYE / AIRWAY SYMPTOMS", 54, scale=back_out((t - 0.6) / 0.3))
    return img


def scene_end(t, dur, ctx):
    img = E.BG_GRID.copy()
    glow = Image.new("RGB", (W // 2, H // 2))
    sz = 480 * back_out(t / 0.45) * (1 + 0.06 * math.sin(t * 5))
    if sz > 5:
        ImageDraw.Draw(glow).text((W / 4, 290), "?", font=F(sz / 2), fill=(200, 120, 20), anchor="mm")
    img = add_glow(img, glow, 22)
    d = ImageDraw.Draw(img)
    if sz > 5:
        d.text((W / 2, 580), "?", font=F(sz), fill=(255, 226, 120), anchor="mm", stroke_width=6, stroke_fill=(60, 20, 0))
    for i, opt in enumerate(["SWITCH TO ROLL-ON?", "FRAGRANCE-FREE?", "KEEP SPRAYING?"]):
        st = 0.5 + i * 0.3
        if t > st:
            label_box(img, W / 2, 940 + i * 115, opt, 58, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((t - st) / 0.3))
    if t > 1.6:
        label_box(img, W / 2, 1680, "COMMENT BELOW", 64, scale=back_out((t - 1.6) / 0.3))
        E.down_arrow(d, W / 2, 1830 + 18 * math.sin(t * 9), 0.9)
        d.text((W / 2, 1290), "Never inhale sprays · use them in ventilated rooms", font=F(32, "semi"),
               fill=(190, 195, 210), anchor="mm")
    return img


E.SCENES = {"ban": scene_ban, "recall": scene_recall, "butane": scene_butane, "fragrance": scene_fragrance,
            "study": scene_study, "end": scene_end}


# ----------------------------------------------------------------------------- timeline + sound
def build_timeline(total):
    scenes, cur = [], None
    for seg in E.SEGMENTS:
        if cur is None or seg["scene"] != cur["name"]:
            start = 0.0 if cur is None else seg["start"] - 0.08
            if cur:
                cur["end"] = start
            cur = dict(name=seg["scene"], start=start)
            scenes.append(cur)
    cur["end"] = total
    chunks = []
    for i, seg in enumerate(E.SEGMENTS):
        nxt = E.SEGMENTS[i + 1]["start"] if i + 1 < len(E.SEGMENTS) else total
        for j, (txt, a, b) in enumerate(seg["chunks"]):
            end = b if j < len(seg["chunks"]) - 1 else min(nxt - 0.1, seg["end"] + 0.7)
            chunks.append((txt, a, end))
    by = {s["scene"]: s["chunks"] for s in E.SEGMENTS}
    sc = {s["name"]: s for s in scenes}
    ctx = dict(chunks_by_scene=by, cuts=[s["start"] for s in scenes[1:]],
               banned=by["ban"][0][1] + 0.55 * (by["ban"][0][2] - by["ban"][0][1]),
               recalled=sc["recall"]["start"] + 0.9,
               benzene=by["recall"][1][1], deaths=by["butane"][1][1],
               secret=sc["fragrance"]["start"] + 0.55 * (sc["fragrance"]["end"] - sc["fragrance"]["start"]),
               study=sc["study"]["start"], study_dur=sc["study"]["end"] - sc["study"]["start"],
               end=sc["end"]["start"])
    return scenes, chunks, ctx


def sfx_hiss(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.clip(t / 0.05, 0, 1) * np.exp(-np.clip(t - d * 0.7, 0, None) * 8)
    return E.hp(E.RNG.standard_normal(n), 3000) * env * 0.35


def build_audio(total, ctx):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    voice = np.zeros(n, np.float32)
    for seg in E.SEGMENTS:
        E.place(voice, seg["wav"], seg["start"])
    voice *= 0.89 / max(1e-6, np.abs(voice).max())
    R = E.RNG
    drone = sum(a * np.sin(2 * np.pi * f * t + R.uniform(0, 6)) for f, a in
                [(55, 1.0), (55.3, 0.7), (82.4, 0.45), (110, 0.3), (164.8, 0.15)])
    drone = E.lp(drone * (0.75 + 0.25 * np.sin(2 * np.pi * 0.15 * t)), 700)
    pulse = np.zeros(n)
    bt = 0.4
    while bt < total - 1:  # ticking-clock pulse
        E.place(pulse, E.sfx_tick() * 1.4, bt); bt += 0.5
    music = drone / np.abs(drone).max() * 0.5 + pulse * 0.5
    env = np.clip(E.lp(np.abs(voice), 8) / 0.06, 0, 1)
    music *= 1 - 0.55 * env
    fx = np.zeros(n)
    for c in ctx["cuts"]:
        E.place(fx, E.sfx_whoosh(), max(0, c - 0.25), 0.55)
    E.place(fx, sfx_hiss(1.4), 0.15, 0.8)
    for at in (ctx["banned"], ctx["recalled"], ctx["secret"]):
        E.place(fx, E.sfx_thud(), at, 0.9)
    E.place(fx, E.sfx_riser(0.8), ctx["benzene"] - 0.8, 0.6)
    E.place(fx, E.sfx_boom(2.0), ctx["deaths"], 0.5)
    for k in range(42):
        E.place(fx, E.sfx_tick(), ctx["study"] + 0.6 + k * max(0.8, ctx["study_dur"] * 0.55) / 42, 0.5)
    E.place(fx, E.sfx_riser(1.0), ctx["end"] - 1.0, 0.7)
    E.place(fx, E.sfx_thud(), ctx["end"], 0.8)
    mix = voice + music * 0.3 + fx * 0.42
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    path = os.path.join(E.OUT, "mix.wav")
    sf.write(path, mix[: int(total * SR)].astype(np.float32), SR)
    return path


def main():
    total = E.build_voice()
    E.TL = build_timeline(total)
    scenes, chunks, ctx = E.TL
    print("duration %.2fs" % total)
    for s in scenes:
        print(f"  {s['name']:9s} {s['start']:6.2f} -> {s['end']:6.2f}")
    audio = build_audio(total, ctx)
    nframes = int(total * FPS)
    if "--preview" in sys.argv:
        pdir = os.path.join(E.OUT, "preview"); os.makedirs(pdir, exist_ok=True)
        for f in os.listdir(pdir):
            os.remove(os.path.join(pdir, f))
        for s in scenes:
            for frac in (0.2, 0.5, 0.85):
                fi = int((s["start"] + (s["end"] - s["start"]) * frac) * FPS)
                Image.frombytes("RGB", (W, H), E.render_frame(fi)).resize((360, 640)).save(
                    os.path.join(pdir, f"{fi:04d}_{s['name']}.png"))
        return
    dst = os.path.join(E.OUT, "deodorant_en.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", audio, "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-ar", "48000",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-shortest", dst]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    import multiprocessing as mp
    with mp.get_context("fork").Pool(os.cpu_count()) as pool:
        for buf in pool.imap(E.render_frame, range(nframes), chunksize=4):
            proc.stdin.write(buf)
    proc.stdin.close(); proc.wait()
    print("wrote", dst)


if __name__ == "__main__":
    main()
