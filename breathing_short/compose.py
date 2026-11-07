#!/usr/bin/env python3
"""Step 3: frames + narration -> out/breathing_short.mp4 (1080x1920, 30 fps, H.264/AAC, -14 LUFS).

Per shot: upscale the 15 fps Cycles frames to 1080x1920, motion-interpolate to 30 fps (per shot, so cuts
stay clean), then concat, burn the pop-in captions (ASS) and mix voice + synthesized music/SFX.
"""
import os, json, subprocess
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
WORK = os.path.join(OUT, "work"); os.makedirs(WORK, exist_ok=True)
TL = json.load(open(os.path.join(OUT, "timeline.json")))
SRC_FPS, FPS, SR = int(os.environ.get("SRC_FPS", 30)), 30, 48000
SHOTS = {s["id"]: s for s in TL["shots"]}
WIDE = os.environ.get("ASPECT", "16:9") == "16:9"
W_, H_ = (1920, 1080) if WIDE else (1080, 1920)
LAYOUT = dict(CAPSIZE="66" if WIDE else "78", CAPMARGIN="70" if WIDE else "520", BIGSIZE="170" if WIDE else "200",
              STAMP="1480,300" if WIDE else "540,560", O2POS="380,180" if WIDE else "230,380",
              CO2POS="1540,180" if WIDE else "850,380", ATPPOS="1450,300" if WIDE else "760,420")


def lay(text):
    for k, v in sorted(LAYOUT.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(k, v)
    return text.replace("W_", str(W_)).replace("H_", str(H_))


def run(cmd):
    subprocess.run(cmd, check=True)


# ----------------------------------------------------------------------------- video
def shot_clips():
    parts = []
    for s in TL["shots"]:
        dur = s["end"] - s["start"]
        out = os.path.join(WORK, f'{s["id"]}.mp4')
        src = os.path.join(OUT, "frames", s["id"], "%04d.png")
        if not os.path.exists(out):
            run(["ffmpeg", "-y", "-v", "error", "-framerate", str(SRC_FPS), "-i", src, "-vf",
                 f"scale={W_}:{H_}:flags=lanczos,unsharp=5:5:0.7:5:5:0.0,"
                 + (f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if SRC_FPS != FPS else "")
                 + "vignette=angle=PI/6,noise=alls=2:allf=t,"   # gentle lens vignette + film grain
                 f"tpad=stop_mode=clone:stop_duration=1,trim=duration={dur:.4f},setpts=PTS-STARTPTS,"
                 "eq=saturation=1.12:contrast=1.04",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-an", out])
        parts.append(out)
    lst = os.path.join(WORK, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    cat = os.path.join(WORK, "concat.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat])
    return cat


# ----------------------------------------------------------------------------- captions
def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def captions():
    ass = os.path.join(WORK, "caps.ass")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: W_
PlayResY: H_
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,CAPSIZE,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,6,4,2,60,60,CAPMARGIN,1
Style: Tag,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,5,60,60,0,1
Style: Credit,Inter,30,&H00E0E0E0,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,1,2,0,3,40,40,24,1
Style: Big,Inter Black,BIGSIZE,&H0018D8FF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,10,8,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for s in TL["shots"]:
        for c in s["caps"]:
            ev.append(f"Dialogue: 0,{ts(c['t0'])},{ts(c['t1'])},Cap,,0,0,0,,"
                      r"{\fscx70\fscy70\t(0,90,\fscx106\fscy106)\t(90,160,\fscx100\fscy100)}" + c["text"])
    # "MYTH!" stamp on "lactic acid isn't the villain"
    c = next(c for c in SHOTS["lactate"]["caps"] if "lactic" in c["text"])
    ev.append(f"Dialogue: 1,{ts(c['t0'])},{ts(c['t1'] + 0.9)},Big,,0,0,0,,"
              r"{\pos(STAMP)\1c&H2020FF&\fscx40\fscy40\frz-8\t(0,140,\fscx105\fscy105)\t(140,240,\fscx90\fscy90)}MYTH!")
    # gas labels in the microscopic shots
    for sid, a0 in (("mito", 0.1),):
        sh = SHOTS[sid]; t0 = sh["start"] + a0 * (sh["end"] - sh["start"])
        ev.append(f"Dialogue: 1,{ts(t0)},{ts(sh['end'] - 0.05)},Tag,,0,0,0,,"
                  r"{\pos(O2POS)\1c&HFF9A40&\fad(200,150)}O₂ in")
        ev.append(f"Dialogue: 1,{ts(t0 + 0.8)},{ts(sh['end'] - 0.05)},Tag,,0,0,0,,"
                  r"{\pos(CO2POS)\1c&HE0C8D0&\fad(200,150)}CO₂ out")
    if os.path.exists(os.path.join(HERE, "data", "anatomy.blend")):
        tl = TL["total"]
        ev.append(f"Dialogue: 2,{ts(tl - 2.6)},{ts(tl)},Credit,,0,0,0,,{{\\fad(300,0)}}Anatomy: Z-Anatomy / BodyParts3D (DBCLS), CC BY-SA 4.0")
    sh = SHOTS["muscles"]; t0 = sh["start"] + 0.3 * (sh["end"] - sh["start"])
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(sh['end'] - 0.05)},Tag,,0,0,0,,"
              r"{\pos(ATPPOS)\1c&H30D8FF&\fad(200,150)}ATP")
    open(ass, "w").write(lay(head + "\n".join(ev) + "\n"))
    return ass


# ----------------------------------------------------------------------------- audio
RNG = np.random.default_rng(11)


def env(n, a, r):
    e = np.ones(n); a = int(a * SR); r = int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def bandnoise(d, lo, hi):
    from scipy.signal import butter, sosfilt
    x = RNG.normal(0, 1, int(d * SR))
    return sosfilt(butter(4, [lo, hi], "band", fs=SR, output="sos"), x)


def whoosh(d=0.45):
    from scipy.signal import butter, sosfilt
    n = int(d * SR); x = RNG.normal(0, 1, n); out = np.zeros(n)
    for i in range(0, n, 512):  # swept band-pass
        f = 400 + 3000 * (i / n)
        seg = x[max(0, i - 2048): i + 512]
        y = sosfilt(butter(2, [f * 0.6, f * 1.4], "band", fs=SR, output="sos"), seg)[-512:]
        out[i:i + len(y)] = y[: n - i]
    return out * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5


def pop():
    n = int(0.25 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 90 * t * np.exp(-t * 8)) * np.exp(-t * 18) + bandnoise(0.25, 800, 5000) * 0.3 * np.exp(-t * 40)) * 0.9


def zap(d=0.5):
    t = np.arange(int(d * SR)) / SR
    return (np.sign(np.sin(2 * np.pi * (220 + 900 * t) * t)) * 0.15 + bandnoise(d, 2000, 7000) * 0.25) * np.exp(-t * 5)


def riser(d):
    t = np.arange(int(d * SR)) / SR
    f = 120 * (1 + 3 * (t / d) ** 2)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + bandnoise(d, 300, 3000) * 0.08) * (t / d) ** 1.5


def heartbeat(d, bpm=110):
    out = np.zeros(int(d * SR)); t = np.arange(int(0.18 * SR)) / SR
    thump = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 25)
    for k in np.arange(0, d, 60 / bpm):
        for off, g in ((0, 1.0), (0.22, 0.6)):
            i = int((k + off) * SR)
            if i + len(thump) < len(out):
                out[i:i + len(thump)] += thump * g
    return out


def rip(d=0.6):
    t = np.arange(int(d * SR)) / SR
    crack = bandnoise(d, 300, 4000) * (np.abs(np.sin(2 * np.pi * 38 * t)) ** 6)
    return crack * np.exp(-t * 4) * 1.2


def achoo():
    ah = bandnoise(0.55, 300, 1600) * env(int(0.55 * SR), 0.5, 0.05) * 0.25
    t = np.arange(int(0.6 * SR)) / SR
    choo = (bandnoise(0.6, 1500, 7000) * 0.9 + bandnoise(0.6, 200, 900) * 0.5) * np.exp(-t * 7) * env(len(t), 0.005, 0.1)
    return np.concatenate([ah, choo])


def music(total):
    """Light, curious pizzicato-ish loop: Am - F - C - G at 104 bpm, plus a soft pad."""
    bpm = 104; beat = 60 / bpm; n = int(total * SR); out = np.zeros(n)
    chords = [(57, 60, 64), (53, 57, 60), (48, 55, 64), (55, 59, 62)]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    t8 = np.arange(int(beat / 2 * SR)) / SR
    k = 0; tt = 0.0
    while tt < total:
        ch = chords[int(tt / (beat * 4)) % 4]
        note = ch[[0, 2, 1, 2, 0, 1, 2, 1][k % 8]] + 12
        tone = (np.sin(2 * np.pi * hz(note) * t8) + 0.3 * np.sin(4 * np.pi * hz(note) * t8)) * np.exp(-t8 * 9)
        i = int(tt * SR); out[i:i + len(tone)] += tone[: max(0, n - i)] * 0.22
        if k % 8 == 0:  # pad + bass per bar
            tb = np.arange(int(beat * 4 * SR)) / SR
            pad = sum(np.sin(2 * np.pi * hz(m_) * tb) for m_ in ch) * 0.05 * env(len(tb), 0.4, 0.6)
            bass = np.sin(2 * np.pi * hz(ch[0] - 12) * tb) * 0.12 * np.exp(-tb * 1.2)
            out[i:i + len(tb)] += (pad + bass)[: max(0, n - i)]
        k += 1; tt += beat / 2
    return out


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    clip = clip[: len(buf) - i]; buf[i:i + len(clip)] += clip * gain


def audio(total):
    v, sr = sf.read(os.path.join(OUT, "voice.wav"), dtype="float64")
    if v.ndim > 1: v = v.mean(1)
    if sr != SR:
        from scipy.signal import resample_poly
        v = resample_poly(v, SR, sr)
    n = int(total * SR); voice = np.zeros(n); voice[: min(n, len(v))] = v[:n]
    sfx = np.zeros(n)
    for s in TL["shots"][1:]:
        place(sfx, whoosh(), s["start"] - 0.2, 0.35)
    S = SHOTS
    sh = lambda k, u: S[k]["start"] + u * (S[k]["end"] - S[k]["start"])
    # footsteps: one thump per foot contact, matching the rendered gait (blender/shots.py GAITS)
    step = np.zeros(int(0.12 * SR)); tt = np.arange(len(step)) / SR
    step = (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 40) + bandnoise(0.12, 1500, 6000) * 0.25 * np.exp(-tt * 60))
    gait = dict(intro=0.72, muscles=0.72, brain=0.72, diaphragm=0.72, heart=0.72, buffer=0.56, lactate=0.72, trained=0.76)
    for k, P in gait.items():
        if k not in S:
            continue
        a_, b_ = S[k]["start"], S[k]["end"]
        if k == "brain": a_ = sh("brain", 0.45)
        j = int(np.ceil(a_ / (P / 2)))
        while j * P / 2 < b_:
            place(sfx, step, j * P / 2, 0.55 if P < 0.6 else 0.4); j += 1
    place(sfx, zap(), sh("brain", 0.28), 0.5)
    place(sfx, zap(0.3), sh("brain", 0.55), 0.3)
    # breaths (filtered noise swells)
    def breath(d, lo, hi, g):
        x = bandnoise(d, lo, hi); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * g
    for k, rate, g in (("diaphragm", 0.8, 0.5), ("buffer", 1.1, 0.45)):
        t_ = S[k]["start"]
        while t_ < S[k]["end"] - 0.3:
            place(sfx, breath(0.45 / rate, 400, 2500, g), t_); place(sfx, breath(0.5 / rate, 300, 1800, g * 0.8), t_ + 0.5 / rate)
            t_ += 1 / rate
    place(sfx, heartbeat(S["heart"]["end"] - S["heart"]["start"], 160), S["heart"]["start"], 0.9)
    place(sfx, heartbeat(S["lactate"]["end"] - S["lactate"]["start"], 150), S["lactate"]["start"], 0.4)
    place(sfx, riser(0.32 * (S["buffer"]["end"] - S["buffer"]["start"])), S["buffer"]["start"], 0.5)
    for i in range(10):  # CO2 bubbles in the buffer shot
        place(sfx, pop() * 0.5, sh("buffer", 0.52 + 0.04 * i), 0.25)
    place(sfx, pop(), sh("lactate", 0.1), 0.7)  # stamp
    place(sfx, whoosh(0.7), sh("mito", 0.05), 0.4)
    mus = music(total)
    # duck music under the voice
    from scipy.ndimage import uniform_filter1d
    lvl = uniform_filter1d(np.abs(voice), int(0.25 * SR))
    duck = 1 - 0.55 * np.clip(lvl / (lvl.max() * 0.3), 0, 1)
    mix = voice * 1.0 + sfx * 0.6 + mus * 0.5 * duck
    mix *= env(n, 0.02, 0.8)
    mix /= np.abs(mix).max() / 0.95
    p = os.path.join(WORK, "mix.wav"); sf.write(p, mix.astype(np.float32), SR)
    return p


def main():
    total = TL["total"]
    cat = shot_clips()
    ass = captions()
    mix = audio(total)
    final = os.path.join(OUT, "breathing_short.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", cat, "-i", mix, "-vf", f"ass={ass}",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
         "-movflags", "+faststart", final])
    print("wrote", final)


if __name__ == "__main__":
    main()
