#!/usr/bin/env python3
"""
Roopkund "Skeleton Lake" — ~20 s 9:16 Hinglish short.

Reuses the engine from ../tunguska_demo/make_video.py (narration, captions, SFX, glow,
labels, render loop) and adds this story's own scenes and sound cues.

Usage:  python3 make_video.py [--preview]
"""
import os, sys, math, random, importlib.util, subprocess
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
E.OUT = os.path.join(HERE, "out")
os.makedirs(E.OUT, exist_ok=True)

# ----------------------------------------------------------------------------- script (~20 s)
# Facts: Roopkund lake, Uttarakhand, ~5,000 m (~16,000 ft). Skeletons found 1942.
# 2019 DNA study (Nature Communications): distinct groups who died ~1,000 years apart
# (~800 CE South-Asian group, ~1800 CE group with Eastern-Mediterranean ancestry).
VIDEO_LANG = os.environ.get("VIDEO_LANG", "hi")   # "hi" = Hinglish, "en" = English

SEGMENTS_HI = [
    dict(scene="india", gap=0.3, hi="[slow] हिमालय में, सोलह हज़ार फ़ीट पर, एक झील है। | [punch] रूपकुंड!",
         cap=["Himalaya mein, 16,000 FEET par, ek jheel hai.", "ROOPKUND!"]),
    dict(scene="lake", gap=0.3, hi="उन्नीस सौ बयालीस में, यहाँ कुछ ऐसा मिला… | [punch] सैकड़ों इंसानी कंकाल!",
         cap=["1942 mein, yahan kuch aisa mila...", "SAIKDON insaani KANKAAL!"]),
    dict(scene="dna", gap=0.3, hi="[soft] लेकिन… | डीएनए जाँच ने सब बदल दिया। | [punch] ये लोग अलग-अलग सदियों में मरे थे!",
         cap=["Lekin...", "DNA JAANCH ne sab badal diya.", "Yeh log alag-alag SADIYON mein mare the!"]),
    dict(scene="world", gap=0.3, hi="[punch] और कुछ तो, भारत के थे ही नहीं! | [slow] उनका डीएनए, भूमध्य सागर के लोगों से मिलता था!",
         cap=["Aur kuch toh BHARAT ke the hi NAHI!", "Unka DNA, MEDITERRANEAN logon se milta tha!"]),
    dict(scene="end", gap=2.6, hi="[soft] तो आखिर… | [punch] वो यहाँ क्यों आए थे?",
         cap=["Toh aakhir...", "Woh yahan KYUN aaye the?"]),
]

SEGMENTS_EN = [
    dict(scene="india", gap=0.3, hi="[slow] Sixteen thousand feet up in the Himalayas, there's a lake. | [punch] Roopkund!",
         cap=["16,000 FEET up in the HIMALAYAS, there's a lake.", "ROOPKUND!"]),
    dict(scene="lake", gap=0.3, hi="In nineteen forty-two, something terrifying was found here... | [punch] Hundreds of human skeletons!",
         cap=["In 1942, something TERRIFYING was found here...", "HUNDREDS of human SKELETONS!"]),
    dict(scene="dna", gap=0.3, hi="[soft] But... | DNA tests changed everything. | [punch] These people died centuries apart!",
         cap=["But...", "DNA TESTS changed everything.", "These people died CENTURIES apart!"]),
    dict(scene="world", gap=0.3, hi="[punch] And some of them weren't from India at all! | [slow] Their DNA matched people from the Mediterranean!",
         cap=["And some of them weren't from INDIA at all!", "Their DNA matched people from the MEDITERRANEAN!"]),
    dict(scene="end", gap=2.6, hi="[soft] So... | [punch] why did they come here?",
         cap=["So...", "Why did they COME HERE?"]),
]

LABELS = {
    "hi": dict(skel="300–800 KANKAAL!", est="(anumaan)", dna="DNA JAANCH (2019)", gap="~1000 SAAL KA FARAK!",
               away="~5,000 KM DOOR SE?", opts=["TEERTH YATRA?", "VYAPAAR?", "KUCH AUR?"], cta="COMMENT MEIN BATAO"),
    "en": dict(skel="300–800 SKELETONS!", est="(estimate)", dna="DNA TEST (2019)", gap="~1000 YEARS APART!",
               away="~5,000 KM AWAY?", opts=["PILGRIMAGE?", "TRADE?", "SOMETHING ELSE?"], cta="COMMENT BELOW"),
}
L = LABELS[VIDEO_LANG]
E.SEGMENTS = SEGMENTS_EN if VIDEO_LANG == "en" else SEGMENTS_HI
if VIDEO_LANG == "en":
    E.LANG = "en-us"
    E.VOICE = os.environ.get("VOICE", "am_michael")
    # English at 2x was too fast to follow: ~1.15x overall keeps every word clear
    E.SPEED = float(os.environ.get("SPEED", "1.05"))
    E.TEMPO = float(os.environ.get("TEMPO", "1.1"))
    E.PAUSE_SCALE = float(os.environ.get("PAUSE_SCALE", "0.8"))

ROOP = (79.73, 30.26)   # Roopkund (lon, lat)
CRETE = (24.9, 35.2)


# ----------------------------------------------------------------------------- map helpers
def load_polys(box, lon0, styles):
    import json
    gj = json.load(open(os.path.join(os.environ["DATA_DIR"], "countries.geojson")))
    lo0, lo1, la0, la1 = box
    polys = []
    for feat in gj["features"]:
        name = feat["properties"].get("ADMIN", "")
        g = feat["geometry"]
        rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in rings:
            r = np.array(poly[0], float)
            if r[:, 0].max() < lo0 or r[:, 0].min() > lo1 or r[:, 1].max() < la0 or r[:, 1].min() > la1:
                continue
            if (np.ptp(r[:, 0]) * np.ptp(r[:, 1])) < 0.05:
                continue
            if len(r) > 1000:
                r = r[:: len(r) // 1000 + 1]
            X = (r[:, 0] - lon0) * np.cos(np.radians(r[:, 1]))
            polys.append((styles.get(name, 0), np.stack([X, r[:, 1]], 1)))
    polys.sort(key=lambda p: p[0])
    return polys

PALETTE = {  # side, top, edge
    0: ((22, 24, 30), (52, 56, 66), (88, 94, 108)),
    1: ((120, 12, 22), (222, 38, 48), (255, 140, 140)),   # highlight red
    2: ((140, 100, 0), (245, 190, 30), (255, 230, 140)),  # highlight yellow
}

def draw_map(polys, lon0, cx, cy, s, oy=0.47, SS=2, depth=8):
    big = Image.new("RGB", (W * SS, H * SS), (10, 12, 18))
    d = ImageDraw.Draw(big)
    S = s * SS
    ox, oyp = W * SS / 2, H * SS * oy
    for st, P in polys:
        sx = ox + (P[:, 0] - cx) * S
        sy = oyp - (P[:, 1] - cy) * S
        if sx.max() < -50 or sx.min() > W * SS + 50 or sy.max() < -50 or sy.min() > H * SS + 50:
            continue
        pts = list(zip(sx.tolist(), sy.tolist()))
        side, top, edge = PALETTE[st]
        d.polygon([(x, y + depth * SS) for x, y in pts], fill=side)
        d.polygon(pts, fill=top, outline=edge, width=SS * 2)
    img = big.reduce(SS)
    return ImageChops.multiply(img, E.vignette_bg((255, 255, 255), (60, 60, 70), oy))

def proj(lon, lat, lon0, cx, cy, s, oy=0.47):
    X = (lon - lon0) * math.cos(math.radians(lat))
    return W / 2 + (X - cx) * s, H * oy - (lat - cy) * s

def pin(d, x, y, k=1.0):
    drop = (1 - clamp(k)) ** 2 * -300
    py = y + drop
    d.ellipse((x - 30, py - 110, x + 30, py - 50), fill=YELLOW, outline=(0, 0, 0), width=4)
    d.polygon([(x - 25, py - 70), (x + 25, py - 70), (x, py)], fill=YELLOW, outline=(0, 0, 0))
    d.ellipse((x - 11, py - 91, x + 11, py - 69), fill=(0, 0, 0))

def skull(d, x, y, s=1.0, col=(232, 226, 210)):
    w, h = 34 * s, 30 * s
    d.ellipse((x - w / 2, y - h, x + w / 2, y + h * 0.15), fill=col, outline=(40, 36, 30), width=max(1, int(2 * s)))
    d.rounded_rectangle((x - w * 0.3, y - h * 0.1, x + w * 0.3, y + h * 0.35), radius=int(4 * s), fill=col,
                        outline=(40, 36, 30), width=max(1, int(2 * s)))
    for ex in (-0.2, 0.2):
        d.ellipse((x + ex * w - 5 * s, y - h * 0.55, x + ex * w + 5 * s, y - h * 0.25), fill=(20, 18, 16))
    d.polygon([(x, y - h * 0.18), (x - 3 * s, y - h * 0.02), (x + 3 * s, y - h * 0.02)], fill=(20, 18, 16))


# ----------------------------------------------------------------------------- scenes
IND_LON0 = 80
IND_POLYS = load_polys((60, 100, 5, 40), IND_LON0, {"India": 1})

def scene_india(t, dur, ctx):
    pt = ctx["pin"] - ctx["scene_start"]
    z = smooth((t - 0.2) / max(1.5, pt + 0.3))
    s = lerp(26, 95, z ** 1.3)
    c0 = ((80 - IND_LON0) * math.cos(math.radians(22)), 22.5)
    c1 = ((ROOP[0] - IND_LON0) * math.cos(math.radians(ROOP[1])), ROOP[1])
    cx, cy = lerp(c0[0], c1[0], z), lerp(c0[1], c1[1], z)
    img = draw_map(IND_POLYS, IND_LON0, cx, cy, s)
    d = ImageDraw.Draw(img)
    a = 1 - smooth((t - 0.5) / 0.6)
    if a > 0.02:
        x, y = proj(79, 22, IND_LON0, cx, cy, s)
        d.text((x, y), "INDIA", font=F(90), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=(90, 0, 10))
    if t > 0.9:
        x, y = proj(79.0, 29.6, IND_LON0, cx, cy, s)
        label_box(img, x - 120, y + 120, "UTTARAKHAND", 48, bg=(20, 20, 26), scale=back_out((t - 0.9) / 0.35))
    x, y = proj(*ROOP, IND_LON0, cx, cy, s)
    if t > pt - 0.25:
        k = (t - (pt - 0.25)) / 0.25
        if t > pt:
            for j in range(3):
                ph = ((t - pt) * 0.9 + j / 3) % 1
                rr = 20 + ph * 120
                d.ellipse((x - rr, y - rr * 0.45, x + rr, y + rr * 0.45), outline=(255, 220, 120), width=max(1, int(6 * (1 - ph))))
        pin(d, x, y, k)
        if t > pt + 0.1:
            label_box(img, x, y - 230, "ROOPKUND", 76, scale=back_out((t - pt - 0.1) / 0.3))
    title = "SKELETON LAKE?"
    n = int(clamp(t / 0.8) * len(title) + 0.999)
    d.text((W / 2, 250), title[:n], font=F(104), fill=WHITE, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    wbar = smooth((t - 0.7) / 0.4) * 560
    if wbar > 0:
        d.rectangle((W / 2 - wbar / 2, 322, W / 2 + wbar / 2, 336), fill=RED)
    label_box(img, W / 2, 420, "~16,000 FEET", 50, bg=(20, 20, 26), scale=back_out((t - 0.35) / 0.3))
    return img


def make_lake_bg():
    img = E.vertical_grad((8, 14, 34), (70, 92, 128), 0, 900)
    d = ImageDraw.Draw(img)
    r = random.Random(4)
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(0, 600)
        c = r.randint(140, 230)
        d.point((x, y), fill=(c, c, c + 20 if c < 235 else 255))
    def ridge(base, amp, col, snow, seed, step):
        rr = random.Random(seed)
        pts, x = [(0, H)], -50
        peaks = []
        while x < W + 100:
            y = base - rr.uniform(0.3, 1) * amp
            pts.append((x, y)); peaks.append((x, y))
            x += step * rr.uniform(0.6, 1.4)
            pts.append((x, base - rr.uniform(0, 0.35) * amp))
            x += step * rr.uniform(0.4, 0.9)
        pts.append((W + 100, H))
        d.polygon(pts, fill=col)
        if snow:
            for px, py in peaks:
                hw = step * 0.35
                d.polygon([(px, py), (px - hw, py + hw * 0.9), (px - hw * 0.3, py + hw * 0.6),
                           (px + hw * 0.2, py + hw * 0.95), (px + hw, py + hw * 0.85)], fill=snow)
    ridge(820, 420, (58, 68, 92), (205, 215, 232), 1, 170)
    ridge(930, 300, (40, 46, 62), (185, 195, 212), 2, 140)
    d.rectangle((0, 960, W, H), fill=(74, 70, 66))
    ground = E.vertical_grad((92, 88, 82), (40, 38, 36), 960, H)
    img.paste(ground.crop((0, 960, W, H)), (0, 960))
    d = ImageDraw.Draw(img)
    for _ in range(60):  # rocks + a few snow patches
        x, y = r.uniform(0, W), r.uniform(980, H)
        s = r.uniform(4, 16) * (0.6 + (y - 960) / 960)
        col = (150, 156, 166) if r.random() < 0.12 else (r.randint(58, 78),) * 3
        d.ellipse((x - s * 1.6, y - s * 0.6, x + s * 1.6, y + s * 0.6), fill=col)
    lake = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lake).ellipse((150, 1010, 930, 1290), fill=255)
    lake = lake.filter(ImageFilter.GaussianBlur(3))
    water = E.vertical_grad((40, 96, 112), (16, 44, 60), 1010, 1290)
    img.paste(water, (0, 0), lake)
    d = ImageDraw.Draw(img)
    d.ellipse((150, 1010, 930, 1290), outline=(150, 190, 200), width=3)
    for k in range(5):
        y = 1060 + k * 40
        d.line((320 + k * 12, y, 760 - k * 20, y), fill=(70, 130, 145), width=2)
    return img

LAKE_BG = make_lake_bg()
_r = random.Random(9)
SKULLS = []
for i in range(46):
    a = _r.uniform(0, 2 * math.pi)
    k = _r.uniform(1.05, 1.55)
    x, y = 540 + 390 * k * math.cos(a), 1150 + 140 * k * math.sin(a)
    if 0 < x < W and 960 < y < 1380:
        SKULLS.append((x, y, 0.7 + (y - 960) / 420 * 0.8, _r.uniform(0, 0.9)))
SKULLS.sort(key=lambda s: s[1])

def scene_lake(t, dur, ctx):
    zoom = lerp(1.0, 1.08, smooth(t / dur))
    img = LAKE_BG
    if zoom > 1.001:
        w2, h2 = int(W / zoom), int(H / zoom)
        x0, y0 = (W - w2) // 2, int((H - h2) * 0.6)
        img = img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BILINEAR)
    else:
        img = img.copy()
    d = ImageDraw.Draw(img)
    ht = ctx["hit"] - ctx["scene_start"]
    if t > ht - 0.1:
        for x, y, s, delay in SKULLS:
            k = (t - ht - delay * 0.7) / 0.18
            if k > 0:
                X = W / 2 + (x - W / 2) * zoom
                Y = (y - H * 0.6) * zoom + H * 0.6
                skull(d, X, Y, s * zoom * back_out(k))
        flash = clamp(1 - (t - ht) / 0.25)
        if flash > 0 and t >= ht:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), flash * 0.5)
        label_box(img, W / 2, 470, L["skel"], 92, scale=back_out((t - ht - 0.15) / 0.3), rot=-4)
        d2 = ImageDraw.Draw(img)
        if t > ht + 0.4:
            d2.text((W / 2, 560), L["est"], font=F(34, "semi"), fill=(220, 225, 235), anchor="mm",
                    stroke_width=3, stroke_fill=(0, 0, 0))
    label_box(img, W / 2, 230, "ROOPKUND, 1942", 66, bg=(20, 20, 26), scale=back_out(t / 0.3))
    return img


def scene_dna(t, dur, ctx):
    img = E.BG_GRID.copy()
    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    tl = ctx["timeline"] - ctx["scene_start"]
    shrink = smooth((t - tl + 0.1) / 0.4)
    y0, y1 = 360, lerp(1000, 780, shrink)
    amp = lerp(170, 120, shrink)
    appear = smooth(t / 0.5)
    pts_a, pts_b = [], []
    n = 40
    for i in range(n + 1):
        y = lerp(y0, y1, i / n)
        ph = i * 0.42 + t * 3.2
        pts_a.append((W / 2 + amp * math.sin(ph) * appear, y, math.cos(ph)))
        pts_b.append((W / 2 - amp * math.sin(ph) * appear, y, -math.cos(ph)))
    d = ImageDraw.Draw(img)
    for i in range(0, n + 1, 2):  # rungs
        (xa, ya, za), (xb, yb, zb) = pts_a[i], pts_b[i]
        c = int(90 + 60 * (za + 1) / 2)
        d.line((xa, ya, xb, yb), fill=(c, c, c + 30), width=5)
    for pts, col in ((pts_a, (80, 200, 255)), (pts_b, (255, 90, 160))):
        for (x, y, z) in pts:
            r = 9 + 5 * (z + 1) / 2
            b = 0.55 + 0.45 * (z + 1) / 2
            cc = tuple(int(v * b) for v in col)
            d.ellipse((x - r, y - r, x + r, y + r), fill=cc)
            gd.ellipse(((x - r * 1.8) / 2, (y - r * 1.8) / 2, (x + r * 1.8) / 2, (y + r * 1.8) / 2),
                       fill=tuple(v // 3 for v in col))
    img = add_glow(img, glow, 8)
    d = ImageDraw.Draw(img)
    label_box(img, W / 2, 230, L["dna"], 64, scale=back_out(t / 0.3))
    if t > tl - 0.05:
        k = t - tl
        ly = 1110
        wline = smooth(k / 0.35)
        d.line((W / 2 - 420 * wline, ly, W / 2 + 420 * wline, ly), fill=(200, 205, 220), width=6)
        for yr, x, col in ((800, 260, (80, 200, 255)), (1800, 820, (255, 90, 160))):
            kk = (k - (0.15 if yr == 800 else 0.45)) / 0.3
            if kk > 0:
                d.ellipse((x - 14, ly - 14, x + 14, ly + 14), fill=col, outline=WHITE, width=3)
                for j, dx in enumerate((-50, 0, 50)):
                    skull(d, x + dx, ly - 70 - (12 if j == 1 else 0), 1.25 * back_out(kk))
                label_box(img, x, ly + 75, f"~{yr} CE", 50, bg=(20, 20, 26), scale=back_out(kk))
        if k > 0.8:
            label_box(img, W / 2, 900, L["gap"], 70, scale=back_out((k - 0.8) / 0.3), rot=-3)
    return img


WLD_LON0 = 50
WLD_POLYS = load_polys((-15, 110, -5, 65), WLD_LON0, {"India": 1, "Greece": 2})

def scene_world(t, dur, ctx):
    s = lerp(9.6, 10.6, smooth(t / dur))
    cx, cy = (52 - WLD_LON0) * math.cos(math.radians(33)), 33
    img = draw_map(WLD_POLYS, WLD_LON0, cx, cy, s, oy=0.42, depth=5)
    d = ImageDraw.Draw(img)
    ax, ay = proj(*CRETE, WLD_LON0, cx, cy, s, 0.42)
    bx, by = proj(*ROOP, WLD_LON0, cx, cy, s, 0.42)
    mx, my = (ax + bx) / 2, min(ay, by) - 260
    prog = ease_out((t - 0.25) / 1.0)
    pts = []
    for i in range(61):
        u = i / 60 * prog
        pts.append(((1 - u) ** 2 * ax + 2 * (1 - u) * u * mx + u * u * bx,
                    (1 - u) ** 2 * ay + 2 * (1 - u) * u * my + u * u * by))
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=YELLOW, width=9)
    if prog > 0.02:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        al = 36
        d.polygon([(x2 + math.cos(ang) * 10, y2 + math.sin(ang) * 10),
                   (x2 - al * math.cos(ang - 0.5), y2 - al * math.sin(ang - 0.5)),
                   (x2 - al * math.cos(ang + 0.5), y2 - al * math.sin(ang + 0.5))], fill=YELLOW, outline=(0, 0, 0))
    for x, y, col in ((ax, ay, YELLOW), (bx, by, RED)):
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=col, outline=WHITE, width=4)
    label_box(img, ax + 20, ay + 95, "E. MEDITERRANEAN", 40, bg=(140, 100, 0), scale=back_out((t - 0.15) / 0.3))
    label_box(img, bx, by + 90, "ROOPKUND", 44, scale=back_out((t - 0.9) / 0.3))
    if t > 1.1:
        label_box(img, W / 2, 330, L["away"], 74, bg=(20, 20, 26), scale=back_out((t - 1.1) / 0.3))
    label_box(img, W / 2, 210, "DNA MATCH", 62, scale=back_out(t / 0.3))
    return img


def scene_end(t, dur, ctx):
    img = E.BG_GRID.copy()
    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    sz = 520 * back_out(t / 0.45) * (1 + 0.06 * math.sin(t * 5))
    if sz > 5:
        gd.text((W / 4, 310), "?", font=F(sz / 2), fill=(200, 120, 20), anchor="mm")
    img = add_glow(img, glow, 22)
    d = ImageDraw.Draw(img)
    if sz > 5:
        d.text((W / 2, 620), "?", font=F(sz), fill=(255, 226, 120), anchor="mm", stroke_width=6, stroke_fill=(60, 20, 0))
    hit = ctx["end_hit"] - ctx["scene_start"]
    for i, opt in enumerate(L["opts"]):
        st = hit + 0.2 + i * 0.3
        if t > st:
            label_box(img, W / 2, 1000 + i * 120, opt, 64, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((t - st) / 0.3))
    ct = hit + 1.2
    if t > ct:
        label_box(img, W / 2, 1680, L["cta"], 64, scale=back_out((t - ct) / 0.3))
        E.down_arrow(d, W / 2, 1830 + 18 * math.sin(t * 9), 0.9)
    return img


E.SCENES = {"india": scene_india, "lake": scene_lake, "dna": scene_dna, "world": scene_world, "end": scene_end}


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
    S = {s["scene"]: s for s in E.SEGMENTS}
    ctx = dict(
        pin=S["india"]["chunks"][1][1],
        hit=S["lake"]["chunks"][1][1],
        timeline=S["dna"]["chunks"][2][1],
        nahi=S["world"]["chunks"][0][1] + 0.7 * (S["world"]["chunks"][0][2] - S["world"]["chunks"][0][1]),
        end_hit=S["end"]["chunks"][1][1],
        cuts=[s["start"] for s in scenes[1:]],
    )
    return scenes, chunks, ctx


def build_audio(total, ctx):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    voice = np.zeros(n, np.float32)
    for seg in E.SEGMENTS:
        E.place(voice, seg["wav"], seg["start"])
    voice *= 0.89 / max(1e-6, np.abs(voice).max())
    R = E.RNG
    drone = sum(a * np.sin(2 * np.pi * f * t + R.uniform(0, 6)) for f, a in
                [(49, 1.0), (49.3, 0.7), (73.4, 0.5), (98, 0.35), (146.8, 0.18), (196.5, 0.1)])
    drone = E.lp(drone * (0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * t)), 700)
    # eerie high shimmer
    drone += 0.08 * np.sin(2 * np.pi * 784 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.31 * t))
    beat = np.zeros(n)
    hb, bt = E.sfx_thud() * 0.5, 0.5
    while bt < total - 1:
        E.place(beat, hb, bt); E.place(beat, hb * 0.6, bt + 0.22); bt += 60 / 76
    music = drone / np.abs(drone).max() * 0.5 + beat * 0.35
    env = np.clip(E.lp(np.abs(voice), 8) / 0.06, 0, 1)
    music *= 1 - 0.55 * env
    fx = np.zeros(n)
    for c in ctx["cuts"]:
        E.place(fx, E.sfx_whoosh(), max(0, c - 0.25), 0.55)
    E.place(fx, E.sfx_pop(), ctx["pin"], 0.8)
    E.place(fx, E.sfx_riser(1.0), ctx["hit"] - 1.0, 0.7)
    E.place(fx, E.sfx_boom(2.5), ctx["hit"], 0.75)
    for k in range(12):
        E.place(fx, E.sfx_tick(), ctx["hit"] + 0.05 + k * 0.055, 0.7)
    E.place(fx, E.sfx_thud(), ctx["timeline"] + 0.15, 0.7)
    E.place(fx, E.sfx_thud(), ctx["timeline"] + 0.45, 0.7)
    E.place(fx, E.sfx_whoosh(0.9), ctx["cuts"][2] + 0.2, 0.6)
    E.place(fx, E.sfx_thud(), ctx["nahi"], 0.9)
    E.place(fx, E.sfx_riser(1.2), ctx["end_hit"] - 1.2, 0.8)
    E.place(fx, E.sfx_thud(), ctx["end_hit"], 0.9)
    mix = voice + music * 0.33 + fx * 0.42
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    path = os.path.join(E.OUT, f"mix_{VIDEO_LANG}.wav")
    sf.write(path, mix[: int(total * SR)].astype(np.float32), SR)
    return path


def main():
    total = E.build_voice()
    E.TL = build_timeline(total)
    scenes, chunks, ctx = E.TL
    print("duration %.2fs" % total)
    for s in scenes:
        print(f"  {s['name']:7s} {s['start']:6.2f} -> {s['end']:6.2f}")
    audio = build_audio(total, ctx)
    nframes = int(total * FPS)
    if "--preview" in sys.argv:
        pdir = os.path.join(E.OUT, "preview"); os.makedirs(pdir, exist_ok=True)
        for s in scenes:
            for frac in (0.2, 0.55, 0.92):
                fi = int((s["start"] + (s["end"] - s["start"]) * frac) * FPS)
                Image.frombytes("RGB", (W, H), E.render_frame(fi)).resize((360, 640)).save(
                    os.path.join(pdir, f"{fi:04d}_{s['name']}.png"))
        return
    dst = os.path.join(E.OUT, "roopkund_demo.mp4" if VIDEO_LANG == "hi" else f"roopkund_demo_{VIDEO_LANG}.mp4")
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
