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
    dict(scene="end", gap=2.4, hi="So… | is your spray really worth it?",
         cap=["So...", "Is your spray REALLY WORTH IT?"]),
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


# ----------------------------------------------------------------------------- scenes (3D renders)
# Every key word gets its own 3D image (rendered by blender/shots.py into renders/).
RENDERS = {}
def R(name):
    if name not in RENDERS:
        RENDERS[name] = Image.open(os.path.join(HERE, "renders", name + ".png")).convert("RGB")
    return RENDERS[name]

def cam_move(img, k, focus=(0.5, 0.45), z0=1.0, z1=1.12):
    """Slow push-in towards focus (k = 0..1 progress through the shot)."""
    z = lerp(z0, z1, smooth(k))
    w2, h2 = int(W / z), int(H / z)
    fx, fy = focus
    x0 = int(clamp(fx * W - w2 / 2, 0, W - w2)); y0 = int(clamp(fy * H - h2 / 2, 0, H - h2))
    return img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BILINEAR)

DUST = [(random.Random(i).uniform(0, W), random.Random(i + 50).uniform(0, H), random.Random(i + 7).uniform(1.5, 4)) for i in range(70)]

def _shade():
    a = np.zeros((H, W), np.float32)
    y = np.arange(H, dtype=np.float32)
    band = np.exp(-((y - 1470) / 190) ** 2) * 175
    a[:] = band[:, None]
    m = Image.fromarray(a.astype(np.uint8), "L")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im.putalpha(m)
    return im

SHADE = _shade()


def dust(img, t):
    d = ImageDraw.Draw(img)
    for x, y, r in DUST:
        yy = (y - t * 22 * r) % H
        a = int(70 + 60 * math.sin(t * 2 + x))
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(a, a, min(255, a + 20)))

def shots_for(ctx, scene, plan):
    """plan: list of (chunk_index, fraction, render_name, focus). Returns active (name, focus, start, end) for local t."""
    out = []
    for item in plan:
        ci, frac, name, focus = item[:4]
        zz = item[4] if len(item) > 4 else (1.0, 1.12)
        out.append((chunk_t(ctx, scene, ci, frac), name, (focus, zz)))
    return out

def show(t, dur, ctx, plan):
    seq = shots_for(ctx, ctx["scene_name"], plan)
    seq[0] = (0.0,) + seq[0][1:]
    idx = max(i for i, (st, _, _) in enumerate(seq) if t >= st or i == 0)
    st, name, focus = seq[idx]
    en = seq[idx + 1][0] if idx + 1 < len(seq) else dur
    k = (t - st) / max(0.3, en - st)
    img = cam_move(R(name), k, focus[0], *focus[1])
    if idx > 0 and t - st < 0.18:  # punch-in on every image switch
        z = lerp(1.08, 1.0, ease_out((t - st) / 0.18))
        w2, h2 = int(W / z), int(H / z)
        img = img.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
    dust(img, t + ctx["scene_start"])
    img.paste(SHADE, (0, 0), SHADE)  # darken the caption area for readability
    return img, idx, t - st


def scene_ban(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "spray_can", (0.5, 0.42)), (0, 0.55, "australia_school", (0.47, 0.45), (1.35, 1.5)),
                                      (1, 0.0, "lungs", (0.5, 0.4))])
    if idx == 0:
        st = chunk_t(ctx, "ban", 0, 0.3)
        if t > st:
            label_box(img, W / 2, 560, "BANNED", 140, scale=lerp(1.8, 1.0, ease_out((t - st) / 0.18)), rot=-8)
    elif idx == 1:
        label_box(img, W / 2, 230, "AUSTRALIAN SCHOOLS", 64, scale=back_out(lt / 0.3))
    else:
        label_box(img, 270, 320, "ASTHMA", 60, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((lt - 0.25) / 0.3))
        label_box(img, 800, 420, "ALLERGIES", 60, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((lt - 0.6) / 0.3))
    return img


def scene_recall(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "recall_shelf", (0.5, 0.5)), (1, 0.0, "benzene", (0.5, 0.42)),
                                      (2, 0.0, "test_tubes", (0.5, 0.5))])
    if idx == 0:
        label_box(img, W / 2, 230, "USA · 2021 · P&G", 62, bg=DARK, scale=back_out(lt / 0.3))
        if lt > 0.6:
            label_box(img, W / 2, 760, "RECALLED", 140, scale=lerp(1.8, 1.0, ease_out((lt - 0.6) / 0.18)), rot=-7)
    elif idx == 1:
        label_box(img, W / 2, 230, "BENZENE  (C6H6)", 70, scale=back_out(lt / 0.3))
        if lt > 0.6:
            label_box(img, W / 2, 1180, "GROUP 1 CARCINOGEN · WHO-IARC", 50, bg=DARK, scale=back_out((lt - 0.6) / 0.3))
    else:
        label_box(img, W / 2, 230, "FDA: LEVELS WERE LOW", 62, bg=DARK, scale=back_out(lt / 0.3))
        if lt > 0.7:
            label_box(img, W / 2, 1200, "BUT SHOULD BE ZERO", 66, scale=back_out((lt - 0.7) / 0.3), rot=-3)
    return img


def scene_butane(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "can_cutaway", (0.5, 0.42)), (1, 0.0, "uk_map", (0.52, 0.45))])
    if idx == 0:
        label_box(img, W / 2, 230, "WHAT'S INSIDE?", 66, bg=DARK, scale=back_out(lt / 0.3))
        if lt > 0.5:
            label_box(img, 820, 620, "BUTANE GAS", 54, bg=(200, 120, 20), scale=back_out((lt - 0.5) / 0.3))
            d = ImageDraw.Draw(img)
            d.line((690, 650, 600, 700), fill=YELLOW, width=8)
    else:
        label_box(img, W / 2, 230, "UNITED KINGDOM", 64, bg=DARK, scale=back_out(lt / 0.3))
        n = int(11 * clamp((lt - 0.2) / 1.0))
        if lt > 0.2:
            d = ImageDraw.Draw(img)
            d.text((W / 2, 400), f"{n} DEATHS", font=F(120), fill=(255, 80, 80), anchor="mm", stroke_width=8, stroke_fill=(30, 0, 0))
            d.text((W / 2, 490), "deodorant inhalation · 2001–2020 (ONS)", font=F(36, "semi"), fill=(220, 225, 235),
                   anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    return img


def scene_fragrance(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "perfume", (0.5, 0.42))])
    label_box(img, W / 2, 230, "FRAGRANCE = ?", 72, scale=back_out(t / 0.3))
    st = dur * 0.55
    if t > st:
        label_box(img, W / 2, 1180, "TRADE SECRET", 104, scale=lerp(1.8, 1.0, ease_out((t - st) / 0.18)), rot=-6)
    return img


def scene_study(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "figurines", (0.5, 0.45))])
    label_box(img, W / 2, 230, "DENMARK · 1,189 PEOPLE", 60, bg=DARK, scale=back_out(t / 0.3))
    n = int(42 * clamp((t - 0.4) / max(0.8, dur * 0.5)))
    if t > 0.4:
        d = ImageDraw.Draw(img)
        d.text((W / 2, 420), f"{n}%", font=F(170), fill=(255, 80, 80), anchor="mm", stroke_width=8, stroke_fill=(30, 0, 0))
    return img


def scene_end(t, dur, ctx):
    img, idx, lt = show(t, dur, ctx, [(0, 0, "question", (0.5, 0.42))])
    for i, opt in enumerate(["SWITCH TO ROLL-ON?", "FRAGRANCE-FREE?", "KEEP SPRAYING?"]):
        st = 0.5 + i * 0.3
        if t > st:
            label_box(img, W / 2, 230 + i * 110, opt, 56, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((t - st) / 0.3))
    if t > 1.6:
        label_box(img, W / 2, 1700, "COMMENT BELOW", 64, scale=back_out((t - 1.6) / 0.3))
        d = ImageDraw.Draw(img)
        E.down_arrow(d, W / 2, 1845 + 18 * math.sin(t * 9), 0.9)
        d.text((W / 2, 1585), "Never inhale sprays · use them in ventilated rooms", font=F(32, "semi"),
               fill=(220, 225, 235), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    return img


def _with_name(fn, name):
    def f(t, dur, ctx):
        return fn(t, dur, dict(ctx, scene_name=name))
    return f

E.SCENES = {n: _with_name(f, n) for n, f in {"ban": scene_ban, "recall": scene_recall, "butane": scene_butane,
            "fragrance": scene_fragrance, "study": scene_study, "end": scene_end}.items()}


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
               banned=by["ban"][0][1] + 0.3 * (by["ban"][0][2] - by["ban"][0][1]),
               recalled=sc["recall"]["start"] + 0.6,
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
