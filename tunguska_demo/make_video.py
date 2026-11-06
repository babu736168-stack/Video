#!/usr/bin/env python3
"""
Tunguska Event (1908) — 9:16 Hinglish explainer short, generated 100% from code.

Pipeline:
  1. Narration  : Kokoro TTS (offline, Hindi voice) per script segment
  2. Sound      : music drone + heartbeat, whooshes, boom, ticks — synthesised in numpy
  3. Visuals    : every frame drawn with Pillow (maps, fireball, shockwave, charts, captions)
  4. Export     : frames piped into ffmpeg -> 1080x1920 H.264 MP4, loudness-normalised audio

Usage:  python3 make_video.py [--preview]      (DATA_DIR must hold kokoro.onnx, voices.bin, countries.geojson)
"""
import os, sys, json, math, random, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy.signal import butter, sosfilt

W, H, FPS, SR = 1080, 1920, 30, 24000
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DATA_DIR", os.path.join(ROOT, "data"))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- script
# hi  = what the voice says (Devanagari gives correct pronunciation)
# cap = on-screen Hinglish caption chunks; ALL-CAPS words / numbers are highlighted yellow
SEGMENTS = [
    # "|" separates COMPLETE sentences (or deliberate one-word cliffhangers like "और फिर…").
    # Never split mid-clause (after का / पर / से): the voice drops its pitch there and sounds cut off.
    # One caption chunk per piece.
    dict(scene="map",   gap=0.4, hi="[slow] तीस जून, उन्नीस सौ आठ। | साइबेरिया का घना जंगल।",
         cap=["30 JUNE 1908...", "Siberia ka ghana JUNGLE."]),
    dict(scene="sky",   gap=0.3, hi="सुबह सवा सात बजे, आसमान में कुछ अजीब दिखा… | [punch] आग का एक विशाल गोला!",
         cap=["Subah sawa 7 baje, aasmaan mein kuch AJEEB dikha...", "Aag ka ek VISHAAL GOLA!"]),
    dict(scene="sky",   gap=0.65, hi="[soft] और फिर… | [punch] एक ज़बरदस्त धमाका!",
         cap=["Aur phir...", "Ek zabardast DHAMAKA!"], boom=(1, 0.5)),  # boom halfway into chunk 1
    dict(scene="energy", gap=0.3, hi="[slow] हिरोशिमा बम याद है? | [punch] ये उससे सैकड़ों गुना ताक़तवर था!",
         cap=["HIROSHIMA BOMB yaad hai?", "Yeh usse SAIKDON GUNA taakatwar tha!"]),
    dict(scene="trees", gap=0.35, hi="दो हज़ार वर्ग किलोमीटर का जंगल, तबाह हो गया। | [punch] करीब आठ करोड़ पेड़, ज़मीन पर बिछ गए!",
         cap=["2,000 sq km jungle TABAAH ho gaya.", "Kareeb 8 CRORE PED zameen par BICHH GAYE!"]),
    dict(scene="crater", gap=0.3, hi="[soft] लेकिन… | [slow] सबसे बड़ा रहस्य? | [punch] वहाँ कोई गड्ढा ही नहीं मिला!",
         cap=["Lekin...", "Sabse bada RAHASYA?", "Wahan koi GADDHA hi NAHI MILA!"]),
    dict(scene="end",   gap=2.2, hi="[soft] तो आखिर… | [punch] वहाँ फटा क्या था?",
         cap=["Toh aakhir...", "Wahan PHATA KYA THA?"]),
]
LEAD = 0.45
VOICE = os.environ.get("VOICE", "hm_omega")
LANG = os.environ.get("TTS_LANG", "hi")  # "hi" Hindi, "en-us" / "en-gb" English


# ----------------------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def smooth(x):
    x = clamp(x); return x * x * (3 - 2 * x)

def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3

def back_out(x, s=2.2):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

def lerp(a, b, t):
    return a + (b - a) * t

def font_path(style):
    return subprocess.check_output(["fc-match", "-f", "%{file}", f"Inter:style={style}"]).decode()

FONT_FILES = {"black": font_path("Black"), "bold": font_path("Bold"), "semi": font_path("SemiBold")}
_fonts = {}
def F(size, w="black"):
    k = (int(size), w)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_FILES[w], int(size))
    return _fonts[k]

YELLOW = (255, 214, 10)
RED = (225, 29, 42)
WHITE = (255, 255, 255)


def label_box(img, cx, cy, text, size=60, bg=RED, fg=WHITE, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    f = F(size * scale)
    l, t, r, b = f.getbbox(text)
    tw, th = r - l, b - t
    px, py = int(28 * scale), int(18 * scale)
    bw, bh = tw + 2 * px, th + 2 * py
    tile = Image.new("RGBA", (bw + 16, bh + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle((8, 8, 8 + bw, 8 + bh), radius=int(12 * scale), fill=bg + (int(255 * alpha),))
    d.text((8 + px - l, 8 + py - t), text, font=f, fill=fg + (int(255 * alpha),))
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def down_arrow(d, x, y, s=1.0, color=YELLOW):
    """Chunky arrow pointing down, tip at (x, y)."""
    pts = [(0, 0), (-38, -40), (-16, -40), (-16, -90), (16, -90), (16, -40), (38, -40)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=color, outline=(0, 0, 0), width=4)


def add_glow(base, glow_small, blur):
    """glow_small: half-res RGB layer -> blur -> upscale -> additive."""
    g = glow_small.filter(ImageFilter.GaussianBlur(blur)).resize((W, H), Image.BILINEAR)
    return ImageChops.add(base, g)


def vignette_bg(c_center, c_edge, cy=0.45):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * cy) / H) ** 2)
    k = np.clip(r / 0.75, 0, 1)[..., None] ** 1.3
    arr = np.array(c_center, np.float32) * (1 - k) + np.array(c_edge, np.float32) * k
    return Image.fromarray(arr.astype(np.uint8))


def vertical_grad(top, bottom, y0=0, y1=H):
    y = np.clip((np.arange(H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    arr = np.array(top, np.float32) * (1 - y) + np.array(bottom, np.float32) * y
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).astype(np.uint8))


# ----------------------------------------------------------------------------- 1. narration
# Delivery markup inside `hi`: phrases separated by "|", each may start with a tag.
#   [slow] tense build-up   [soft] quiet, suspense   [punch] the reveal word   [fast] quick aside
STYLES = {  # speed, gain, pause after (s)
    "":      (1.00, 0.95, 0.22),
    "slow":  (0.86, 0.90, 0.45),
    "soft":  (0.84, 0.72, 0.55),
    "punch": (1.02, 1.25, 0.30),
    "fast":  (1.12, 0.95, 0.15),
}
# deeper documentary tone, presence boost, compression, light room echo (duration preserved)
VOICE_FX = ("asetrate=24000*0.94,aresample=24000,atempo=1.0638,bass=g=4:f=120,"
            "equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=4:attack=5:release=120:makeup=4,"
            "aecho=0.8:0.6:45|90:0.16|0.08")
DRAMATIC = os.environ.get("DRAMATIC", "1") == "1"
SPEED = float(os.environ.get("SPEED", "1.45"))         # global talking-speed multiplier
PAUSE_SCALE = float(os.environ.get("PAUSE_SCALE", "0.6"))  # shrinks pauses between phrases/segments
TEMPO = float(os.environ.get("TEMPO", "1.6"))  # final playback-speed of the narration (pitch preserved)
# CONTINUOUS=1: each scene's narration is one TTS call (natural, unbroken delivery). "|" then only marks
# caption boundaries, and [tags] are ignored. CONTINUOUS=0 = the older per-sentence dramatic mode.
CONTINUOUS = os.environ.get("CONTINUOUS", "1") == "1"
LIGHT_FX = "bass=g=3:f=120,equalizer=f=3000:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3"


VOICE_FILE = os.environ.get("VOICE_FILE", "")      # use a recorded / VoiceStudio narration instead of TTS
VOICE_FILE_TEMPO = float(os.environ.get("VOICE_FILE_TEMPO", "1.0"))  # optional speed-up of that file


def use_voice_file(path):
    """Fit the video to an uploaded narration of the WHOLE script.
    Every caption chunk ("|" piece) must be spoken in order; the file is cut at the
    natural pauses nearest to where each piece is expected to start."""
    os.makedirs(os.path.join(OUT, "tts"), exist_ok=True)
    wav_path = os.path.join(OUT, "tts", "_voicefile.wav")
    af = "silenceremove=start_periods=1:start_threshold=-45dB"
    if VOICE_FILE_TEMPO != 1:
        af += f",atempo={VOICE_FILE_TEMPO}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "1", "-ar", str(SR), "-af", af, wav_path], check=True)
    v = trim_silence(sf.read(wav_path, dtype="float32")[0], 0.004)
    v = v / max(1e-6, np.abs(v).max()) * 0.9
    pieces = [(si, p) for si, seg in enumerate(SEGMENTS) for p, _ in parse_phrases(seg["hi"])]
    caps = [c for seg in SEGMENTS for c in seg["cap"]]
    assert len(pieces) == len(caps), "each '|' piece needs one caption chunk"
    lens = np.array([len(p) + 3 for _, p in pieces], float)
    expect = np.cumsum(lens)[:-1] / lens.sum() * len(v)
    cuts = align_cuts(expect, silent_runs(v, 60), len(v))
    starts = [0] + cuts
    ends = cuts + [len(v)]
    k = 0
    t0 = LEAD
    for si, seg in enumerate(SEGMENTS):
        n = len(seg["cap"])
        a, b = starts[k], ends[k + n - 1]
        seg["start"] = t0 + a / SR
        seg["wav"] = v[a:b]
        seg["dur"] = (b - a) / SR
        seg["end"] = seg["start"] + seg["dur"]
        seg["chunks"] = [(seg["cap"][j], t0 + starts[k + j] / SR, t0 + ends[k + j] / SR) for j in range(n)]
        k += n
        print(f"  voice {seg['dur']:5.2f}s  " + " | ".join(f"{c} @{x - seg['start']:.2f}" for c, x, _ in seg["chunks"]))
    return t0 + len(v) / SR + SEGMENTS[-1]["gap"]


def align_cuts(expect, runs, total):
    """Pick one pause per expected boundary, in order (dynamic programming).
    Cost = distance from the expected position, minus a bonus for long pauses
    (sentence ends pause longer than commas). Falls back to the expected position."""
    K, M = len(expect), len(runs)
    if K == 0:
        return []
    if M < K:
        return [int(e) for e in expect]
    mids = [(a + b) / 2 for a, b in runs]
    lens = [(b - a) / SR for a, b in runs]
    def cost(k, m):
        return ((mids[m] - expect[k]) / (0.12 * total)) ** 2 - 2.5 * min(lens[m], 0.6)
    INF = float("inf")
    D = [[INF] * M for _ in range(K)]
    P = [[-1] * M for _ in range(K)]
    for m in range(M):
        D[0][m] = cost(0, m)
    for k in range(1, K):
        best, arg = INF, -1
        for m in range(M):
            if m >= 1 and D[k - 1][m - 1] < best:
                best, arg = D[k - 1][m - 1], m - 1
            if arg >= 0:
                D[k][m] = best + cost(k, m)
                P[k][m] = arg
    m = min(range(M), key=lambda j: D[K - 1][j])
    picked = []
    for k in range(K - 1, -1, -1):
        picked.append(m)
        m = P[k][m]
    return [runs[j][1] for j in reversed(picked)]


def silent_runs(w, min_ms=40):
    fr = int(0.01 * SR)
    n = len(w) // fr
    if n == 0:
        return []
    rms = np.sqrt(np.mean(w[: n * fr].reshape(n, fr) ** 2, axis=1))
    silent = rms < 0.04 * rms.max()
    runs, i = [], 0
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            if i > 0 and j < n and (j - i) * 10 >= min_ms:
                runs.append((i * fr, j * fr))
            i = j
        else:
            i += 1
    return runs


def parse_phrases(hi):
    out = []
    for ph in hi.split("|"):
        ph = ph.strip()
        tag = ""
        if ph.startswith("["):
            tag, ph = ph[1:].split("]", 1)
            ph = ph.strip()
        out.append((ph, tag))
    return out


def tts_cached(k_holder, text, speed):
    import hashlib
    h = hashlib.md5(f"{VOICE}|{LANG}|{speed}|{text}".encode()).hexdigest()[:12]
    p = os.path.join(OUT, "tts", f"{h}.wav")
    if not os.path.exists(p):
        from kokoro_onnx import Kokoro
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if not k_holder:
            k_holder.append(Kokoro(os.path.join(DATA, "kokoro.onnx"), os.path.join(DATA, "voices.bin")))
        s, sr = k_holder[0].create(text, voice=VOICE, speed=speed, lang=LANG)
        assert sr == SR
        sf.write(p, s, SR)
    return sf.read(p, dtype="float32")[0]


def build_voice():
    """Each "|" piece is a COMPLETE sentence (or a deliberate one-word cliffhanger), spoken in its
    own TTS call so the intonation always finishes. Voice FX + speed-up are applied per piece, and the
    dramatic pauses are inserted afterwards in real time, so they survive the speed-up."""
    if VOICE_FILE:
        return use_voice_file(VOICE_FILE)
    kh = []
    tmp_in, tmp_out = os.path.join(OUT, "tts", "_in.wav"), os.path.join(OUT, "tts", "_out.wav")
    for seg in SEGMENTS:
        pieces, bounds, pos = [], [], 0
        phrases = parse_phrases(seg["hi"])
        if CONTINUOUS:
            # whole scene narration in ONE TTS call: no stop-start between sentences
            text = " ".join(p for p, _ in phrases)
            dry = trim_silence(tts_cached(kh, text, round(SPEED, 3)))
            dry = dry / max(1e-6, np.abs(dry).max()) * 0.85
            w = dry
            if TEMPO != 1 or LIGHT_FX:
                sf.write(tmp_in, np.concatenate([dry, np.zeros(int(0.2 * SR), np.float32)]), SR)
                fx = ",".join(x for x in [LIGHT_FX, f"atempo={TEMPO}" if TEMPO != 1 else ""] if x)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-af", fx, "-ar", str(SR), tmp_out], check=True)
                w = trim_silence(sf.read(tmp_out, dtype="float32")[0], 0.004)
            seg["wav"] = w.astype(np.float32)
            # caption boundaries: expected position from text length, snapped to the nearest real pause
            lens = np.array([len(p) + 2 for p, _ in phrases], float)
            expect = np.cumsum(lens)[:-1] / lens.sum() * len(dry)
            runs = silent_runs(dry)
            cuts, used = [], set()
            for e in expect:
                best = min((r for r in runs if r not in used), key=lambda r: abs((r[0] + r[1]) / 2 - e), default=None)
                if best is not None and abs((best[0] + best[1]) / 2 - e) < 0.25 * len(dry):
                    used.add(best); cuts.append(best[1])
                else:
                    cuts.append(int(e))
            cuts = sorted(cuts)
            starts = [0] + [int(c / TEMPO) for c in cuts]
            seg["bounds"] = [(a, b) for a, b in zip(starts, starts[1:] + [len(w)])]
            continue
        for j, (txt, tag) in enumerate(phrases):
            speed, gain, pause = STYLES[tag] if DRAMATIC else (1.08, 0.95, 0.12)
            speed, pause = round(speed * SPEED, 3), pause * PAUSE_SCALE
            w = trim_silence(tts_cached(kh, txt, speed))
            w = w / max(1e-6, np.abs(w).max()) * 0.8 * gain
            if DRAMATIC:
                sf.write(tmp_in, np.concatenate([w, np.zeros(int(0.25 * SR), np.float32)]), SR)
                fx = VOICE_FX + (f",atempo={TEMPO}" if TEMPO != 1 else "")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-af", fx, "-ar", str(SR), tmp_out], check=True)
                w = trim_silence(sf.read(tmp_out, dtype="float32")[0], 0.004)
            bounds.append((pos, pos + len(w)))
            pieces.append(w)
            pos += len(w)
            if j < len(phrases) - 1:
                z = int(max(pause, 0.1) * SR)
                pieces.append(np.zeros(z, np.float32)); pos += z
        seg["wav"] = np.concatenate(pieces).astype(np.float32)
        seg["bounds"] = bounds
    t = LEAD
    for seg in SEGMENTS:
        seg["start"] = t
        seg["dur"] = len(seg["wav"]) / SR
        seg["end"] = t + seg["dur"]
        gap = seg["gap"] if seg is SEGMENTS[-1] or "boom" in seg else seg["gap"] * PAUSE_SCALE
        t = seg["end"] + gap
        if len(seg["bounds"]) == len(seg["cap"]):  # one caption per spoken sentence: exact sync
            st = [seg["start"] + a / SR for a, b in seg["bounds"]]
            en = st[1:] + [seg["end"]]
            seg["chunks"] = list(zip(seg["cap"], st, en))
        else:  # fall back: proportional to text length
            w = np.array([len(c) + 4 for c in seg["cap"]], float)
            edges = seg["start"] + np.concatenate([[0], np.cumsum(w) / w.sum()]) * seg["dur"]
            seg["chunks"] = [(seg["cap"][j], edges[j], edges[j + 1]) for j in range(len(seg["cap"]))]
        print(f"  voice {seg['dur']:5.2f}s  " + " | ".join(f"{c} @{a - seg['start']:.2f}" for c, a, b in seg["chunks"]))
    return t


def trim_silence(x, thr=0.01):
    """Trim leading/trailing silence, keeping a generous tail so word endings are never clipped."""
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a, b = max(0, idx[0] - int(0.03 * SR)), min(len(x), idx[-1] + int(0.18 * SR))
    y = x[a:b].copy()
    f = min(len(y), int(0.04 * SR))
    y[-f:] *= np.linspace(1, 0, f)  # soft fade instead of a hard cut
    return y


# ----------------------------------------------------------------------------- 2. sound design
RNG = np.random.default_rng(7)

def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)

def lp(x, f):
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)

def hp(x, f):
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)

def sfx_whoosh(d=0.55):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * t / d) ** 2
    return bp(RNG.standard_normal(n), 400, 4000) * env * 0.5

def sfx_boom(d=4.0):
    n = int(d * SR); t = np.arange(n) / SR
    phase = 2 * np.pi * (28 * t + 40 * (1 - np.exp(-3 * t)) / 3)
    sub = np.sin(phase) * np.exp(-t * 1.1)
    rumble = lp(RNG.standard_normal(n), 500) * np.exp(-t * 1.6) * 3.0
    crack = hp(RNG.standard_normal(n), 2500) * np.exp(-t * 14) * 0.6
    x = sub + rumble + crack
    return x / np.abs(x).max()

def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 950 * np.exp(-t * 18) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.6

def sfx_tick():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (1800 + RNG.uniform(-300, 300)) * t) * np.exp(-t * 160) * 0.25

def sfx_thud():
    n = int(0.7 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (55 + 60 * np.exp(-t * 20)) * t) * np.exp(-t * 6)
    x += lp(RNG.standard_normal(n), 1500) * np.exp(-t * 25) * 0.6
    return x / np.abs(x).max() * 0.9

def sfx_riser(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR
    x = hp(RNG.standard_normal(n), 900) * (t / d) ** 3 * 0.35
    x += np.sin(2 * np.pi * (200 * t + 300 * t * t / d)) * (t / d) ** 2 * 0.15
    return x

def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


def build_audio(total, sc):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    voice = np.zeros(n, np.float32)
    for seg in SEGMENTS:
        place(voice, seg["wav"], seg["start"])
    voice *= 0.89 / max(1e-6, np.abs(voice).max())

    tb = sc["boom"]
    # music: dark drone that swells after the boom, plus a heartbeat pulse
    intensity = 0.55 + 0.45 * np.clip((t - tb + 0.2) * 3, 0, 1) * np.exp(-np.clip(t - tb, 0, None) * 0.15)
    drone = sum(a * np.sin(2 * np.pi * f * t + RNG.uniform(0, 6)) for f, a in
                [(55, 1.0), (55.4, 0.7), (82.4, 0.5), (110, 0.35), (164.8, 0.18), (220.6, 0.08)])
    drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * t)
    drone = lp(drone, 700) * intensity
    beat = np.zeros(n)
    hb = sfx_thud() * 0.5
    bt = 0.6
    while bt < total - 1.0:
        if not (tb - 0.1 < bt < tb + 2.5):
            place(beat, hb, bt); place(beat, hb * 0.6, bt + 0.22)
        bt += 60 / 72
    music = drone / max(1e-6, np.abs(drone).max()) * 0.5 + beat * 0.35

    # side-chain duck music under the voice
    env = lp(np.abs(voice), 8)
    env = np.clip(env / 0.06, 0, 1)
    music *= 1 - 0.55 * env

    fx = np.zeros(n)
    for s in sc["cuts"]:
        place(fx, sfx_whoosh(), max(0, s - 0.25), 0.55)
    place(fx, sfx_pop(), sc["pin"], 0.8)
    # fireball: rising roar from seg1 start up to boom
    a, b = SEGMENTS[1]["start"], tb
    m = int((b - a) * SR); tt = np.linspace(0, 1, m)
    roar = lp(RNG.standard_normal(m), 600) * tt ** 2.2 * 2.2 + bp(RNG.standard_normal(m), 1500, 5000) * tt ** 3 * 0.35
    place(fx, roar, a, 0.6)
    place(fx, sfx_boom(), tb, 1.0)
    for x in sc["ticks"]:
        place(fx, sfx_tick(), x, 0.8)
    place(fx, sfx_boom(2.5) * 0.35, sc["ring"], 0.7)  # tree-flattening rumble
    place(fx, sfx_thud(), sc["stamp"], 1.0)
    place(fx, sfx_thud(), sc["stamp2"], 0.8)
    place(fx, sfx_riser(1.4), sc["end_hit"] - 1.4, 0.8)
    place(fx, sfx_thud(), sc["end_hit"], 0.9)

    mix = voice + music * 0.33 + fx * 0.42
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    path = os.path.join(OUT, "mix.wav")
    sf.write(path, mix[: int(total * SR)].astype(np.float32), SR)
    return path


# ----------------------------------------------------------------------------- 3. visuals: assets
random.seed(3)
BG_DARK = vignette_bg((26, 28, 36), (4, 4, 7))


def make_grid_bg():
    img = BG_DARK.copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    vx, vy, base = W / 2, 980, H + 200
    for i in range(-14, 15):
        d.line([(vx + i * 6, vy), (vx + i * 170, base)], fill=(255, 255, 255, 22), width=2)
    for k in range(1, 18):
        y = vy + (k / 17) ** 2.2 * (base - vy)
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 18), width=2)
    fade = vertical_grad((0, 0, 0), (255, 255, 255), vy, vy + 450).convert("L")
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), fade))
    img.paste(lay, (0, 0), lay)
    return img


BG_GRID = make_grid_bg()

# --- map
def load_map():
    gj = json.load(open(os.path.join(DATA, "countries.geojson")))
    polys = []
    for feat in gj["features"]:
        name = feat["properties"].get("ADMIN", "")
        g = feat["geometry"]
        rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in rings:
            ring = np.array(poly[0], float)
            lon, lat = ring[:, 0], ring[:, 1]
            if lon.min() < 10 or lat.max() < 30 or lat.min() > 84 or lon.max() > 181:
                continue
            if (lon.max() - lon.min()) * (lat.max() - lat.min()) < 0.4:
                continue
            if len(ring) > 1200:
                ring = ring[:: len(ring) // 1200 + 1]
            X = (ring[:, 0] - 100) * np.cos(np.radians(ring[:, 1]))
            polys.append((name == "Russia", np.stack([X, ring[:, 1]], 1)))
    polys.sort(key=lambda p: p[0])  # Russia drawn last (on top)
    return polys

MAP = load_map()
TUN = (101.9, 60.9)  # Tunguska epicentre (lon, lat)

def world(lon, lat):
    return ((lon - 100) * math.cos(math.radians(lat)), lat)

# --- sky scene assets
def make_sky_assets():
    night = vertical_grad((5, 7, 20), (38, 30, 58), 0, 1500)
    d = ImageDraw.Draw(night)
    for _ in range(260):
        x, y = random.uniform(0, W), random.uniform(0, 1350)
        r = random.choice([1, 1, 1, 2, 2, 3])
        c = random.randint(150, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c, min(255, c + 20)))
    warm = vertical_grad((70, 20, 12), (255, 150, 60), 0, 1500)

    def forest(color, base_y, hmin, hmax, step, seed):
        rnd = random.Random(seed)
        lay = Image.new("RGBA", (W + 200, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle((0, base_y, W + 200, H), fill=color)
        x = -40
        while x < W + 240:
            h = rnd.uniform(hmin, hmax); w = h * rnd.uniform(0.32, 0.42)
            y0 = base_y + rnd.uniform(-10, 25)
            for k in range(4):
                tt = k / 4
                ww = w * (1 - tt * 0.55)
                top = y0 - h * (0.45 + 0.55 * (k + 1) / 4)
                d.polygon([(x - ww / 2, y0 - h * tt * 0.75), (x + ww / 2, y0 - h * tt * 0.75), (x, top)], fill=color)
            d.rectangle((x - 3, y0 - 10, x + 3, y0 + 30), fill=color)
            x += step * rnd.uniform(0.6, 1.3)
        return lay

    far = forest((14, 14, 26, 255), 1480, 120, 220, 34, 1)
    near = forest((2, 2, 4, 255), 1640, 260, 420, 70, 2)
    return night, warm, far, near

SKY_NIGHT, SKY_WARM, FOREST_FAR, FOREST_NEAR = make_sky_assets()
EMBERS = [(random.uniform(-1, 1) * 900, -random.uniform(300, 1300), random.uniform(2, 6)) for _ in range(160)]

# --- tree-fall scene assets
def make_ground():
    rng = np.random.default_rng(1)
    n = rng.standard_normal((H // 8, W // 8)).astype(np.float32)
    img = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    a = np.asarray(img, np.float32)[..., None] / 255
    arr = np.array((24, 30, 18), np.float32) * (1 - a) + np.array((52, 58, 34), np.float32) * a
    g = Image.fromarray(arr.astype(np.uint8))
    return ImageChops.multiply(g, vignette_bg((255, 255, 255), (90, 90, 90), 0.45))

GROUND = make_ground()
TC = (540, 840)  # epicentre on screen

def rmax(theta):  # "butterfly" shaped damage zone
    return 640 * (0.78 + 0.22 * math.cos(2 * (theta - 0.45))) + 60 * math.sin(3 * theta)

TREES = []
_r = random.Random(11)
while len(TREES) < 1900:
    x, y = _r.uniform(-120, W + 120), _r.uniform(TC[1] - 1000, TC[1] + 1000)
    dx, dy = x - TC[0], y - TC[1]
    r = math.hypot(dx, dy)
    if r < 45:
        continue
    th = math.atan2(dy, dx)
    TREES.append((x, y, r, dx / r, dy / r, r < rmax(th), _r.uniform(0.85, 1.2)))
BUTTERFLY = [(TC[0] + rmax(a) * math.cos(a), TC[1] + rmax(a) * math.sin(a))
             for a in np.linspace(0, 2 * math.pi, 120)]


# ----------------------------------------------------------------------------- 3b. scenes
def scene_map(t, dur, ctx):
    SS = 2
    big = Image.new("RGB", (W * SS, H * SS), (10, 12, 18))
    d = ImageDraw.Draw(big)
    z = smooth((t - 0.55) / max(2.3, dur * 0.6))
    s = lerp(9.5, 30, z ** 1.4) * SS
    c0, c1 = world(97, 61.5), world(*TUN)
    cx, cy = lerp(c0[0], c1[0], z), lerp(c0[1], c1[1], z)
    ox, oy = W * SS / 2, H * SS * 0.47
    depth = 9 * SS
    for is_ru, P in MAP:
        sx = ox + (P[:, 0] - cx) * s
        sy = oy - (P[:, 1] - cy) * s
        if sx.max() < -50 or sx.min() > W * SS + 50 or sy.max() < -50 or sy.min() > H * SS + 50:
            continue
        pts = list(zip(sx.tolist(), sy.tolist()))
        side, top, edge = ((120, 12, 22), (222, 38, 48), (255, 140, 140)) if is_ru else ((22, 24, 30), (52, 56, 66), (88, 94, 108))
        d.polygon([(x, y + depth) for x, y in pts], fill=side)
        d.polygon(pts, fill=top, outline=edge, width=SS * 2)
    img = big.reduce(SS)
    img = ImageChops.multiply(img, vignette_bg((255, 255, 255), (60, 60, 70), 0.47))
    d = ImageDraw.Draw(img)

    # RUSSIA label while zoomed out
    a = 1 - smooth((t - 0.6) / 0.8)
    if a > 0:
        rx, ry = world(95, 63)
        px, py = W / 2 + (rx - cx) * s / SS, H * 0.47 - (ry - cy) * s / SS
        d.text((px, py), "RUSSIA", font=F(86), fill=(255, 255, 255), anchor="mm",
               stroke_width=5, stroke_fill=(90, 0, 10))
    # SIBERIA label fades in while zooming
    sib = max(1.6, dur * 0.35)
    a2 = smooth((t - sib) / 0.5)
    if a2 > 0:
        sx_, sy_ = world(84, 57.5)
        px, py = W / 2 + (sx_ - cx) * s / SS, H * 0.47 - (sy_ - cy) * s / SS
        label_box(img, px, py, "SIBERIA", 54, bg=(20, 20, 26), scale=back_out((t - sib) / 0.35))

    # pin drop on Tunguska
    pt = ctx["pin"] - ctx["scene_start"]
    if t > pt - 0.25:
        tx, ty = W / 2 + (c1[0] - cx) * s / SS, H * 0.47 - (c1[1] - cy) * s / SS
        k = clamp((t - (pt - 0.25)) / 0.25)
        drop = (1 - k) ** 2 * -300
        for j in range(3):  # pulse rings
            ph = ((t - pt) * 0.9 + j / 3) % 1
            if t > pt:
                rr = 20 + ph * 120
                d.ellipse((tx - rr, ty - rr * 0.45, tx + rr, ty + rr * 0.45),
                          outline=(255, 220, 120), width=max(1, int(6 * (1 - ph))))
        py = ty + drop
        d.ellipse((tx - 30, py - 110, tx + 30, py - 50), fill=(255, 214, 10), outline=(0, 0, 0), width=4)
        d.polygon([(tx - 25, py - 70), (tx + 25, py - 70), (tx, py)], fill=(255, 214, 10), outline=(0, 0, 0))
        d.ellipse((tx - 11, py - 91, tx + 11, py - 69), fill=(0, 0, 0))
        if t > pt + 0.15:
            label_box(img, tx, py - 230, "TUNGUSKA", 72, scale=back_out((t - pt - 0.15) / 0.35))

    # typed title
    title = "30 JUNE 1908"
    n = int(clamp(t / 0.9) * len(title) + 0.999)
    if n:
        d.text((W / 2, 250), title[:n], font=F(118), fill=WHITE, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
        wbar = smooth((t - 0.8) / 0.4) * 520
        if wbar > 0:
            d.rectangle((W / 2 - wbar / 2, 330, W / 2 + wbar / 2, 344), fill=RED)
    return img


def scene_sky(t, dur, ctx):
    tb = ctx["boom"] - ctx["scene_start"]
    p = clamp(t / tb) ** 1.5
    after = t - tb
    if after < 0:
        warm = 0.05 + 0.5 * p ** 3
    else:
        warm = 1.0 - 0.35 * smooth(after / 1.5)
    img = Image.blend(SKY_NIGHT, SKY_WARM, clamp(warm))

    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    A, B = (1250, -180), (560, 1430)
    if after < 0.05:
        for k in range(46, -1, -1):  # trail
            q = p - k * 0.010
            if q < 0:
                continue
            x, y = lerp(A[0], B[0], q), lerp(A[1], B[1], q)
            r = (14 + 44 * q) * (1 - k / 52)
            c = (255, int(lerp(220, 60, k / 46)), int(lerp(120, 10, k / 46)))
            gd.ellipse(((x - r) / 2, (y - r) / 2, (x + r) / 2, (y + r) / 2), fill=c)
        x, y = lerp(A[0], B[0], p), lerp(A[1], B[1], p)
        R = 60 + 140 * p
        gd.ellipse(((x - R) / 2, (y - R) / 2, (x + R) / 2, (y + R) / 2), fill=(255, 150, 50))
    else:
        bx, by = B
        Rg = 250 + 900 * (1 - math.exp(-after * 1.8))
        gd.ellipse(((bx - Rg) / 2, (by - Rg) / 2, (bx + Rg) / 2, (by + Rg * 0.6) / 2), fill=(255, 120, 30))
        Rc = 120 + 420 * (1 - math.exp(-after * 2.5))
        gd.ellipse(((bx - Rc) / 2, (by - Rc) / 2, (bx + Rc) / 2, (by + Rc * 0.5) / 2), fill=(255, 235, 170))
        rr = after * 1500
        if rr < 2400:
            a = int(255 * (1 - rr / 2400))
            gd.ellipse(((bx - rr) / 2, (by - rr * 0.22) / 2, (bx + rr) / 2, (by + rr * 0.22) / 2),
                       outline=(a, int(a * 0.8), int(a * 0.5)), width=10)
    img = add_glow(img, glow, 16)
    d = ImageDraw.Draw(img)
    if after < 0.05:
        x, y = lerp(A[0], B[0], p), lerp(A[1], B[1], p)
        r = 10 + 30 * p
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 225))
    else:
        for ex, ey, er in EMBERS:  # embers flying out
            k = after * 1.3
            x = B[0] + ex * k
            y = B[1] + ey * k + 600 * k * k
            if 0 < x < W and 0 < y < H:
                d.ellipse((x - er, y - er, x + er, y + er), fill=(255, 200, 90))

    drift = int(-t * 10)
    img.paste(FOREST_FAR, (drift - 40, 0), FOREST_FAR)
    img.paste(FOREST_NEAR, (int(drift * 2.2) - 60, 0), FOREST_NEAR)

    if after >= 0:
        flash = clamp(1 - after / 0.4)
        if flash > 0:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 250, 235)), flash)
        sh = 34 * math.exp(-after * 3.5)
        if sh > 1:
            r = random.Random(int(t * FPS))
            img = ImageChops.offset(img, int(r.uniform(-sh, sh)), int(r.uniform(-sh, sh)))
        if after > 0.25:
            label_box(img, W / 2, 300, "DHAMAKA!", 110, scale=back_out((after - 0.25) / 0.35), rot=-4)
    else:
        if t > 0.4:
            label_box(img, W / 2, 230, "Subah 7:14 AM", 58, bg=(20, 20, 26),
                      scale=back_out((t - 0.4) / 0.35), alpha=clamp((tb - 0.6 - t) / 0.4))
    return img


def scene_energy(t, dur, ctx):
    img = BG_GRID.copy()
    d = ImageDraw.Draw(img)
    label_box(img, W / 2, 210, "KITNA BADA DHAMAKA?", 66, scale=back_out(t / 0.35))
    cols, rows, sp = 20, 18, 44
    x0, y0 = W / 2 - (cols - 1) * sp / 2, 440
    total = cols * rows
    f0 = min(1.1, dur * 0.25)
    n = int(total * clamp((t - f0) / max(0.4, dur * 0.85 - f0)) ** 1.7)
    if t > f0 * 0.4:
        n = max(n, 1)
    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    for i in range(total):
        cx, cy = x0 + (i % cols) * sp, y0 + (i // cols) * sp
        if i < n:
            r = 14
            gd.ellipse(((cx - 20) / 2, (cy - 20) / 2, (cx + 20) / 2, (cy + 20) / 2), fill=(170, 70, 10))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 150, 40))
        else:
            d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=(48, 50, 60))
    img = add_glow(img, glow, 6)
    d = ImageDraw.Draw(img)
    # explain the unit
    if f0 * 0.4 < t < f0 + 0.5:
        a = clamp((t - f0 * 0.4) / 0.15) * clamp((f0 + 0.5 - t) / 0.2)
        label_box(img, x0 + 300, y0 - 95, "1 dot = 1 Hiroshima bomb", 44, bg=(20, 20, 26), alpha=a)
    yb = y0 + rows * sp + 10
    d.text((W / 2, yb + 10), "Tunguska: ~3–15 megaton (estimate)   •   Hiroshima: 0.015 megaton",
           font=F(28, "semi"), fill=(160, 165, 180), anchor="mm")
    st = ctx["stamp2"] - ctx["scene_start"]
    if t > st:
        label_box(img, W / 2, 820, "SAIKDON GUNA!", 104, scale=back_out((t - st) / 0.3), rot=-5)
    return img


def scene_trees(t, dur, ctx):
    zoom = lerp(1.12, 0.96, smooth(t / dur))
    img = GROUND.copy()
    d = ImageDraw.Draw(img)
    speed = 720 / max(0.8, (dur - 1.0) * 0.7)
    ring = (t - 0.35) * speed

    def S(x, y):
        return TC[0] + (x - TC[0]) * zoom, TC[1] + (y - TC[1]) * zoom

    for x, y, r, ux, uy, falls, sz in TREES:
        X, Y = S(x, y)
        if X < -40 or X > W + 40 or Y < -40 or Y > H + 40:
            continue
        q = clamp((ring - r) / 70) if falls else 0
        if q <= 0:
            rr = 7 * sz * zoom
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=(34, 78, 40))
            d.ellipse((X - rr * 0.5, Y - rr * 0.6, X + rr * 0.2, Y - rr * 0.1), fill=(60, 110, 60))
        else:
            L = 30 * sz * zoom * ease_out(q)
            d.line((X, Y, X + ux * L, Y + uy * L), fill=(150, 120, 88), width=max(2, int(5 * zoom)))
            d.ellipse((X - 4, Y - 4, X + 4, Y + 4), fill=(80, 60, 40))
    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    if 0 < ring < 1100:
        a = int(255 * clamp(1 - ring / 1100))
        R = ring * zoom
        gd.ellipse(((TC[0] - R) / 2, (TC[1] - R) / 2, (TC[0] + R) / 2, (TC[1] + R) / 2),
                   outline=(a, int(a * .75), int(a * .45)), width=7)
    pulse = 0.5 + 0.5 * math.sin(t * 8)
    gd.ellipse(((TC[0] - 40) / 2, (TC[1] - 40) / 2, (TC[0] + 40) / 2, (TC[1] + 40) / 2),
               fill=(int(160 + 90 * pulse), 30, 30))
    img = add_glow(img, glow, 5)
    d = ImageDraw.Draw(img)
    d.ellipse((TC[0] - 12, TC[1] - 12, TC[0] + 12, TC[1] + 12), fill=RED, outline=WHITE, width=3)
    done = smooth((ring - 760) / 200)
    if done > 0:
        pts = [S(x, y) for x, y in BUTTERFLY]
        for i in range(0, len(pts) - 1, 2):
            d.line([pts[i], pts[i + 1]], fill=(255, 214, 10), width=5)
        label_box(img, W / 2, 1270, "~2,000 km²", 62, bg=(20, 20, 26), scale=back_out((ring - 760) / 120))
    crore = 8 * clamp(ring / 760)
    label_box(img, W / 2, 210, f"PED GIRE: {crore:.1f} CRORE" if crore < 8 else "PED GIRE: 8 CRORE",
              62, scale=back_out(t / 0.35))
    return img


def scene_crater(t, dur, ctx):
    img = vertical_grad((10, 12, 22), (46, 40, 52), 0, 1100)
    d = ImageDraw.Draw(img)
    gy = 1080
    strata = [(64, 46, 32), (56, 40, 28), (48, 34, 24), (40, 28, 20), (32, 22, 16)]
    for i, c in enumerate(strata):
        d.rectangle((0, gy + i * 170, W, H), fill=c)
    d.rectangle((0, gy - 6, W, gy + 10), fill=(70, 88, 46))
    r = random.Random(5)
    for i in range(46):  # fallen trunks lying flat, pointing away from centre
        x = r.uniform(0, W)
        if abs(x - W / 2) < 120:
            continue
        L = r.uniform(70, 150)
        dirx = 1 if x > W / 2 else -1
        d.line((x, gy - 8 - r.uniform(0, 14), x + dirx * L, gy - 4 - r.uniform(0, 14)), fill=(130, 100, 70), width=9)
    for x in (W / 2 - 70, W / 2 - 20, W / 2 + 40, W / 2 + 85):  # stripped trees still standing at epicentre
        hgt = r.uniform(170, 260)
        d.line((x, gy, x, gy - hgt), fill=(110, 86, 62), width=11)
    # expected crater (dashed)
    a = smooth((t - 0.3) / 0.4)
    if a > 0:
        R = 300
        for k in range(0, 18, 2):
            a0, a1 = k * 10, (k + 1) * 10
            d.arc((W / 2 - R, gy - R * 0.9, W / 2 + R, gy + R * 0.9), a0, a1, fill=(255, 255, 255), width=6)
        label_box(img, W / 2, gy + 150, "CRATER YAHAN HONA CHAHIYE THA?", 38, bg=(20, 20, 26), alpha=a)
    # magnifier sweep
    mt = clamp((t - 0.3) / max(0.6, ctx["stamp"] - ctx["scene_start"] - 0.5))
    if 0 < mt < 1:
        mx = lerp(150, W - 150, smooth(mt))
        my = gy - 60 + 30 * math.sin(mt * 9)
        d.ellipse((mx - 110, my - 110, mx + 110, my + 110), outline=(230, 230, 240), width=14)
        d.line((mx + 78, my + 78, mx + 190, my + 190), fill=(230, 230, 240), width=26)
    st = ctx["stamp"] - ctx["scene_start"]
    if t > st:
        k = t - st
        label_box(img, W / 2, 560, "NO CRATER!", 128, scale=lerp(1.8, 1.0, ease_out(k / 0.18)), rot=-7)
        sh = 22 * math.exp(-k * 9)
        if sh > 1:
            img = ImageChops.offset(img, int(random.Random(int(t * 99)).uniform(-sh, sh)), int(sh / 2))
    label_box(img, W / 2, 210, "EPICENTER: GROUND ZERO", 54, bg=(20, 20, 26), scale=back_out(t / 0.35))
    return img


def scene_end(t, dur, ctx):
    img = BG_GRID.copy()
    glow = Image.new("RGB", (W // 2, H // 2))
    gd = ImageDraw.Draw(glow)
    pulse = 1 + 0.06 * math.sin(t * 5)
    sz = 520 * back_out(t / 0.45) * pulse
    if sz > 5:
        gd.text((W / 4, 620 / 2), "?", font=F(sz / 2), fill=(200, 120, 20), anchor="mm")
    img = add_glow(img, glow, 22)
    d = ImageDraw.Draw(img)
    if sz > 5:
        d.text((W / 2, 620), "?", font=F(sz), fill=(255, 226, 120), anchor="mm", stroke_width=6, stroke_fill=(60, 20, 0))
    hit = ctx["end_hit"] - ctx["scene_start"]
    for i, opt in enumerate(["ASTEROID?", "COMET?", "KUCH AUR?"]):
        st = hit + 0.25 + i * 0.35
        if t > st:
            label_box(img, W / 2, 1000 + i * 120, opt, 64, bg=(245, 245, 248), fg=(15, 15, 20),
                      scale=back_out((t - st) / 0.3))
    ct = hit + 1.5
    if t > ct:
        label_box(img, W / 2, 1680, "COMMENT MEIN BATAO", 64, scale=back_out((t - ct) / 0.3))
        down_arrow(d, W / 2, 1830 + 18 * math.sin(t * 9), 0.9)
    return img


SCENES = {"map": scene_map, "sky": scene_sky, "energy": scene_energy,
          "trees": scene_trees, "crater": scene_crater, "end": scene_end}


# ----------------------------------------------------------------------------- captions
def draw_caption(img, text, age):
    sc = back_out(age / 0.16, 2.6) * 0.18 + 0.82 if age < 0.3 else 1.0
    words = text.split()
    base = 80
    fb, line_w, nlines = F(base), 0, 1  # shrink long sentences so they fit in two lines
    for w_ in words:
        wl = fb.getlength(w_)
        if line_w and line_w + fb.getlength(" ") + wl > 930:
            nlines, line_w = nlines + 1, wl
        else:
            line_w += (fb.getlength(" ") if line_w else 0) + wl
    if nlines > 2:
        base = 66
    sc *= base / 80
    f = F(80 * sc)
    d = ImageDraw.Draw(img)
    space = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w_ in words:
        wl = f.getlength(w_)
        if cur and cw + space + wl > 930:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (space if cur else 0) + wl
        cur.append((w_, wl))
    lines.append((cur, cw))
    y = 1460 - (len(lines) - 1) * 50 * sc
    for ln, lw in lines:
        x = W / 2 - lw / 2
        for w_, wl in ln:
            core = "".join(ch for ch in w_ if ch.isalnum())
            hi = core and (core.isupper() or core.isdigit() or any(ch.isdigit() for ch in core))
            d.text((x, y), w_, font=f, fill=YELLOW if hi else WHITE, anchor="lm",
                   stroke_width=int(9 * sc), stroke_fill=(0, 0, 0))
            x += wl + space
        y += 100 * sc


# ----------------------------------------------------------------------------- timeline
def build_timeline(total):
    scenes, cur = [], None
    for i, seg in enumerate(SEGMENTS):
        if cur is None or seg["scene"] != cur["name"]:
            start = 0.0 if cur is None else seg["start"] - 0.08
            if cur:
                cur["end"] = start
            cur = dict(name=seg["scene"], start=start)
            scenes.append(cur)
    cur["end"] = total
    chunks = []
    for i, seg in enumerate(SEGMENTS):
        nxt = SEGMENTS[i + 1]["start"] if i + 1 < len(SEGMENTS) else total
        for j, (txt, a, b) in enumerate(seg["chunks"]):
            end = b if j < len(seg["chunks"]) - 1 else min(nxt - 0.1, seg["end"] + 0.7)
            chunks.append((txt, a, end))
    sb = next(s for s in SEGMENTS if "boom" in s)
    ci, frac = sb["boom"]
    boom = sb["chunks"][ci][1] + frac * (sb["chunks"][ci][2] - sb["chunks"][ci][1])
    s_en = next(s for s in SEGMENTS if s["scene"] == "energy")
    s_tr = next(s for s in SEGMENTS if s["scene"] == "trees")
    s_cr = next(s for s in SEGMENTS if s["scene"] == "crater")
    s_end = SEGMENTS[-1]
    tr_scene = next(s for s in scenes if s["name"] == "trees")
    ctx = dict(
        boom=boom,
        pin=SEGMENTS[0]["start"] + SEGMENTS[0]["dur"] * 0.62,
        stamp2=s_en["chunks"][1][1] + 0.35,
        stamp=s_cr["chunks"][2][1] + 0.45 * (s_cr["chunks"][2][2] - s_cr["chunks"][2][1]),
        end_hit=s_end["chunks"][1][1],
        ring=tr_scene["start"] + 0.35,
        cuts=[s["start"] for s in scenes[1:] if s["name"] != "sky"] + [scenes[1]["start"]],
    )
    # ticks while energy dots fill
    en = next(s for s in scenes if s["name"] == "energy")
    ticks, x = [], en["start"] + 1.1
    while x < en["end"] - 0.3:
        ticks.append(x)
        x += max(0.045, 0.22 * (1 - (x - en["start"]) / (en["end"] - en["start"])))
    ctx["ticks"] = ticks
    return scenes, chunks, ctx


TL = None

def render_frame(fi):
    scenes, chunks, ctx = TL
    t = fi / FPS
    sc = next(s for s in scenes if s["start"] <= t < s["end"]) if t < scenes[-1]["end"] else scenes[-1]
    lt = t - sc["start"]
    ctx2 = dict(ctx, scene_start=sc["start"])
    img = SCENES[sc["name"]](lt, sc["end"] - sc["start"], ctx2)
    if lt < 0.2 and sc["start"] > 0:  # punch-in on every cut
        k = lerp(1.07, 1.0, ease_out(lt / 0.2))
        w2, h2 = int(W / k), int(H / k)
        img = img.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
    for txt, a, b in chunks:
        if a <= t < b:
            draw_caption(img, txt, t - a)
            break
    if t < 0.25:
        img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.25)
    return img.tobytes()


def main():
    global TL
    preview = "--preview" in sys.argv
    total = build_voice()
    total += 0.0
    TL = build_timeline(total)
    scenes, chunks, ctx = TL
    print("duration %.2fs" % total)
    for s in scenes:
        print(f"  {s['name']:7s} {s['start']:6.2f} -> {s['end']:6.2f}")
    audio = build_audio(total, ctx)
    nframes = int(total * FPS)
    if preview:
        os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
        for s in scenes:
            for frac in (0.15, 0.5, 0.9):
                fi = int((s["start"] + (s["end"] - s["start"]) * frac) * FPS)
                Image.frombytes("RGB", (W, H), render_frame(fi)).resize((360, 640)).save(
                    os.path.join(OUT, "preview", f"{s['name']}_{fi:04d}.png"))
        return
    dst = os.path.join(OUT, "tunguska_demo.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", audio, "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-ar", "48000",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-shortest", dst]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    import multiprocessing as mp
    with mp.get_context("fork").Pool(os.cpu_count()) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(nframes), chunksize=4)):
            proc.stdin.write(buf)
            if i % 150 == 0:
                print(f"  frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", dst)


if __name__ == "__main__":
    main()
