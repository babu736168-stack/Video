#!/usr/bin/env python3
"""
Deodorant short v2 — built from the user's own AI-generated shots (images / short clips).

Per shot: normalise to 1080x1920 @30fps, strip audio, remove watermark, upscale + sharpen,
fit the clip to the exact length of its voice line, then add camera motion, stamps, counters,
labels and captions synced to the narration.

Usage:
  python3 make_video.py                         # placeholder TTS voice
  VOICE_FILE=narration.mp3 python3 make_video.py
  MEDIA_DIR=/path/with/01.mp4..19.png python3 make_video.py   # originals (any of .mp4/.mov/.png/.jpg/.gif/.webp)
"""
import os, sys, math, glob, json, random, subprocess, importlib.util
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(HERE, "..", "tunguska_demo")
os.environ.setdefault("DATA_DIR", os.path.join(ENGINE_DIR, "data"))
spec = importlib.util.spec_from_file_location("engine", os.path.join(ENGINE_DIR, "make_video.py"))
E = importlib.util.module_from_spec(spec); sys.modules["engine"] = E; spec.loader.exec_module(E)

W, H, FPS, SR = E.W, E.H, E.FPS, E.SR
F, label_box, clamp, smooth, ease_out, back_out, lerp = E.F, E.label_box, E.clamp, E.smooth, E.ease_out, E.back_out, E.lerp
RED, YELLOW, WHITE, DARK = E.RED, E.YELLOW, E.WHITE, (20, 20, 26)
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
WORK = os.environ.get("WORK_DIR", os.path.join(OUT, "work")); os.makedirs(WORK, exist_ok=True)
E.OUT = OUT
E.LANG, E.VOICE = "en-us", os.environ.get("VOICE", "am_michael")
E.SPEED, E.TEMPO, E.PAUSE_SCALE = 1.05, 1.08, 0.8

# ----------------------------------------------------------------------------- script: one segment per shot
# cap: " / " splits a long line into several on-screen captions (timed by text length)
LINES = [
    ("Do you use deodorant every morning?", "Do you use DEODORANT / every morning?"),
    ("But do you actually know what's inside it?", "But do you actually know / what's INSIDE it?"),
    ("Are you sure you're not inviting asthma and allergies... with every spray?",
     "Are you sure you're not inviting / ASTHMA and ALLERGIES... / with every spray?"),
    ("Because in Australia, many schools have already banned these sprays.",
     "Because in AUSTRALIA, / many schools have already BANNED these sprays."),
    ("And that's not even the scary part.", "And that's not even / the SCARY part."),
    ("In twenty twenty-one, one of the biggest companies on Earth, Procter and Gamble, pulled some of its own sprays off the shelves.",
     "In 2021, one of the BIGGEST companies on Earth, / PROCTER & GAMBLE, / pulled some of its own sprays OFF THE SHELVES."),
    ("The reason? Lab tests found benzene...", "The reason? / Lab tests found BENZENE..."),
    ("a chemical known to cause cancer.", "a chemical known to cause CANCER."),
    ("The amounts were tiny. But they should have been zero.", "The amounts were TINY. / But they should have been ZERO."),
    ("Now look inside the can.", "Now look INSIDE the can."),
    ("It's packed with butane... the same gas used in lighters.", "It's packed with BUTANE... / the same gas used in LIGHTERS."),
    ("If it's inhaled, it can stop the heart.", "If it's inhaled, / it can STOP THE HEART."),
    ("In the UK, deodorant inhalation was linked to eleven deaths.", "In the UK, deodorant inhalation / was linked to 11 DEATHS."),
    ("And that one word on the label... fragrance?", "And that one word on the label... / FRAGRANCE?"),
    ("Companies often don't have to tell you what's inside it. It's a trade secret.",
     "Companies often don't have to tell you what's inside it. / It's a TRADE SECRET."),
    ("In one Danish study, almost half the people, forty-two percent, said fragrances irritated their eyes or airways.",
     "In one Danish study, almost HALF the people, / 42% / said fragrances irritated their EYES or AIRWAYS."),
    ("So next time you press that button... ask yourself:", "So next time you press that button... / ask yourself:"),
    ("is this smell really worth it?", "Is this smell REALLY WORTH IT?"),
    ("Would you switch to a roll-on? Tell me in the comments.", "Would you switch to a ROLL-ON? / Tell me in the COMMENTS."),
]
E.SEGMENTS = [dict(scene=f"{i + 1:02d}", gap=(2.2 if i == len(LINES) - 1 else 0.25), hi=hi, cap=[cap])
              for i, (hi, cap) in enumerate(LINES)]

# ----------------------------------------------------------------------------- media
UP = "/root/.claude/uploads/0c879dd3-c0a5-5bb7-a4bb-10f7294dcc06"
DEFAULT_MEDIA = {  # first upload: tiny 9-frame GIF previews + two Veo clips
    "01": "66819fa2-image.gif", "02": "d3d14c0d-image.gif", "03": "6b3a51ff-image.gif", "04": "632c4857-image.gif",
    "05": "b69e531b-image.gif", "06": "b270d2c1-image.gif", "07": "93098554-image.gif", "08": "2392c6f7-image.gif",
    "09": "290c1d66-image.gif", "10": "0708d860-image.gif", "11": "cbbaabef-701483651_1793992625213058.mp4",
    "12": "486bba73-image.gif", "13": "d1466911-image.gif", "14": "a70a0699-image.gif", "15": "0d021c17-image.gif",
    "16": "41563f91-image.gif", "17": "41a55b7d-image.gif", "18": "82d2c20b-image.gif",
    "19": "e5dc6978-904008556_1793994032037426.mp4",
}
# watermark boxes (x, y, w, h) in source pixels, keyed by source size
WATERMARKS = {(720, 1280): (564, 1124, 100, 108)}

def media_for(shot):
    md = os.environ.get("MEDIA_DIR")
    if md:
        hits = sorted(glob.glob(os.path.join(md, f"{shot}.*")) + glob.glob(os.path.join(md, f"{int(shot)}.*")))
        if hits:
            return hits[0]
    return os.path.join(UP, DEFAULT_MEDIA[shot])

def probe(path):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=width,height:format=duration", "-of", "json", path])
    j = json.loads(o)
    s = j["streams"][0]
    return s["width"], s["height"], float(j["format"].get("duration", 0) or 0)

def cover(img, focus_y=0.45):
    """Scale to cover 1080x1920 and crop (keeps subject, no stretching)."""
    w, h = img.size
    sc = max(W / w, H / h)
    nw, nh = int(w * sc + 0.5), int(h * sc + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - W) // 2
    y0 = int(clamp((nh - H) * focus_y / 0.5 if nh > H else 0, 0, nh - H))
    return img.crop((x0, y0, x0 + W, y0 + H))

def enc_cmd(path):
    return ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", path]

def prepare_shot(shot, dur):
    """Make WORK/<shot>.mp4: 1080x1920, 30 fps, exactly `dur` seconds, no audio, no watermark."""
    src = media_for(shot)
    dst = os.path.join(WORK, f"{shot}.mp4")
    n = int(round(dur * FPS))
    ext = os.path.splitext(src)[1].lower()
    if ext in (".gif", ".png", ".jpg", ".jpeg", ".webp"):
        frames = [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(src))]
        if len(frames) > 24:  # long GIF: sample it
            frames = frames[:: len(frames) // 24 + 1]
        big = [cover(f).filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2)) for f in frames]
        arr = [np.asarray(b, np.float32) for b in big]
        p = subprocess.Popen(enc_cmd(dst), stdin=subprocess.PIPE)
        for i in range(n):
            u = (i / max(1, n - 1)) * (len(arr) - 1)  # play the motion once, slowly, with frame blending
            a = int(u); b = min(a + 1, len(arr) - 1); f = smooth(u - a)
            p.stdin.write((arr[a] * (1 - f) + arr[b] * f).astype(np.uint8).tobytes())
        p.stdin.close(); p.wait()
    else:
        w, h, sd = probe(src)
        speed = clamp(sd / max(dur, 0.1), 1.0, 1.6) if sd else 1.0
        vf = []
        wm = WATERMARKS.get((w, h))
        if wm:
            vf.append("delogo=x=%d:y=%d:w=%d:h=%d" % wm)
        vf += [f"setpts=PTS/{speed:.4f}", f"fps={FPS}",
               f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}",
               "unsharp=5:5:0.6", f"tpad=stop_mode=clone:stop_duration={dur + 1}"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", ",".join(vf), "-frames:v", str(n),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", dst], check=True)
    return dst


# ----------------------------------------------------------------------------- overlays per shot (lt = time into shot)
def stamp(img, x, y, text, size, lt, at, rot=-7):
    if lt > at:
        label_box(img, x, y, text, size, scale=lerp(1.8, 1.0, ease_out((lt - at) / 0.18)), rot=rot)

def tag(img, text, lt, at=0.1, y=230, size=62, bg=DARK, fg=WHITE):
    if lt > at:
        label_box(img, W / 2, y, text, size, bg=bg, fg=fg, scale=back_out((lt - at) / 0.3))

def counter(img, text, y=430, size=170, col=(255, 80, 80)):
    ImageDraw.Draw(img).text((W / 2, y), text, font=F(size), fill=col, anchor="mm", stroke_width=9, stroke_fill=(30, 0, 0))

def ov(shot, img, lt, D):
    if shot == "02": tag(img, "WHAT'S INSIDE?", lt)
    elif shot == "03":
        if lt > 0.3: label_box(img, 280, 330, "ASTHMA", 62, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((lt - 0.3) / 0.3))
        if lt > 0.7: label_box(img, 800, 430, "ALLERGIES", 62, bg=(245, 245, 248), fg=(15, 15, 20), scale=back_out((lt - 0.7) / 0.3))
    elif shot == "04":
        tag(img, "AUSTRALIAN SCHOOLS", lt, bg=RED); stamp(img, W / 2, 560, "BANNED", 150, lt, D * 0.55)
    elif shot == "06":
        tag(img, "USA · 2021 · P&G", lt); stamp(img, W / 2, 620, "RECALLED", 150, lt, D * 0.5)
    elif shot == "07": tag(img, "LAB TEST", lt)
    elif shot == "08":
        tag(img, "BENZENE  (C6H6)", lt, bg=RED, size=70)
        if lt > 0.5: label_box(img, W / 2, 330, "GROUP 1 CARCINOGEN · WHO-IARC", 46, bg=DARK, scale=back_out((lt - 0.5) / 0.3))
    elif shot == "09":
        tag(img, "SAFE LEVEL", lt);
        if lt > D * 0.5: counter(img, "0", y=480, size=260, col=(110, 255, 140))
    elif shot == "10": tag(img, "INSIDE THE CAN", lt)
    elif shot == "11": tag(img, "BUTANE = LIGHTER GAS", lt, bg=(200, 120, 20))
    elif shot == "12": stamp(img, W / 2, 300, "CAN STOP THE HEART", 80, lt, 0.4, rot=-4)
    elif shot == "13":
        tag(img, "UNITED KINGDOM", lt)
        if lt > 0.3: counter(img, f"{int(11 * clamp((lt - 0.3) / max(0.8, D * 0.5)))} DEATHS", y=400, size=120)
    elif shot == "14":
        if lt > D * 0.55: label_box(img, W / 2, 330, '"FRAGRANCE"', 90, bg=YELLOW, fg=(10, 10, 10), scale=back_out((lt - D * 0.55) / 0.3))
    elif shot == "15": stamp(img, W / 2, 330, "TRADE SECRET", 120, lt, D * 0.6, rot=-6)
    elif shot == "16":
        tag(img, "DENMARK · 1,189 PEOPLE", lt)
        if lt > 0.4: counter(img, f"{int(42 * clamp((lt - 0.4) / max(0.8, D * 0.45)))}%", y=420, size=180)
    elif shot == "18": tag(img, "WORTH IT?", lt, bg=RED, size=90, y=260)
    elif shot == "19":
        if lt > 0.3: label_box(img, W / 2, 230, "ROLL-ON  vs  SPRAY", 64, bg=DARK, scale=back_out((lt - 0.3) / 0.3))
        if lt > D * 0.45:
            label_box(img, W / 2, 1700, "COMMENT BELOW", 66, scale=back_out((lt - D * 0.45) / 0.3))
            E.down_arrow(ImageDraw.Draw(img), W / 2, 1850 + 18 * math.sin(lt * 9), 0.9)

STAMPS = {"04": 0.55, "06": 0.5, "15": 0.6}  # fraction of the shot where a stamp hits (for the thud SFX)


# ----------------------------------------------------------------------------- timeline
def split_caps():
    """Turn ' / ' caption parts into separate caption chunks timed by text length within each line."""
    for seg in E.SEGMENTS:
        out = []
        for txt, a, b in seg["chunks"]:
            parts = [p.strip() for p in txt.split(" / ")]
            w = np.array([len(p) + 6 for p in parts], float)
            edges = a + np.concatenate([[0], np.cumsum(w) / w.sum()]) * (b - a)
            out += [(parts[i], edges[i], edges[i + 1]) for i in range(len(parts))]
        seg["chunks"] = out

def timeline(total):
    shots = []
    for i, seg in enumerate(E.SEGMENTS):
        st = 0.0 if i == 0 else seg["start"] - 0.08
        shots.append(dict(id=seg["scene"], start=st))
    for i, s in enumerate(shots):
        s["end"] = shots[i + 1]["start"] if i + 1 < len(shots) else total
    caps = []
    for i, seg in enumerate(E.SEGMENTS):
        nxt = E.SEGMENTS[i + 1]["start"] if i + 1 < len(E.SEGMENTS) else total
        for j, (t, a, b) in enumerate(seg["chunks"]):
            caps.append((t, a, b if j < len(seg["chunks"]) - 1 else min(nxt - 0.06, seg["end"] + 0.6)))
    return shots, caps


# ----------------------------------------------------------------------------- audio
def build_audio(total, shots):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    voice = np.zeros(n, np.float32)
    for seg in E.SEGMENTS:
        E.place(voice, seg["wav"], seg["start"])
    voice *= 0.89 / max(1e-6, np.abs(voice).max())
    drone = sum(a * np.sin(2 * np.pi * f * t + E.RNG.uniform(0, 6)) for f, a in
                [(55, 1.0), (55.3, 0.7), (82.4, 0.45), (110, 0.3), (164.8, 0.15)])
    drone = E.lp(drone * (0.75 + 0.25 * np.sin(2 * np.pi * 0.15 * t)), 700)
    pulse = np.zeros(n); bt = 0.4
    while bt < total - 1:
        E.place(pulse, E.sfx_thud() * 0.35, bt); E.place(pulse, E.sfx_thud() * 0.2, bt + 0.22); bt += 60 / 80
    music = drone / np.abs(drone).max() * 0.5 + pulse * 0.4
    music *= 1 - 0.55 * np.clip(E.lp(np.abs(voice), 8) / 0.06, 0, 1)
    fx = np.zeros(n)
    for s in shots[1:]:
        E.place(fx, E.sfx_whoosh(0.45), max(0, s["start"] - 0.2), 0.45)
    for s in shots:
        D = s["end"] - s["start"]
        if s["id"] in STAMPS:
            E.place(fx, E.sfx_thud(), s["start"] + STAMPS[s["id"]] * D, 0.9)
        if s["id"] == "05":
            E.place(fx, E.sfx_riser(0.9), s["end"] - 0.9, 0.6)
        if s["id"] == "08":
            E.place(fx, E.sfx_boom(2.0), s["start"], 0.45)
        if s["id"] in ("13", "16"):
            for k in range(12):
                E.place(fx, E.sfx_tick(), s["start"] + 0.35 + k * max(0.8, D * 0.5) / 12, 0.6)
        if s["id"] == "12":
            E.place(fx, E.sfx_thud(), s["start"] + 0.4, 0.9); E.place(fx, E.sfx_thud(), s["start"] + 0.75, 0.7)
        if s["id"] == "18":
            E.place(fx, E.sfx_riser(1.0), s["start"] - 1.0, 0.6); E.place(fx, E.sfx_thud(), s["start"], 0.8)
    mix = voice + music * 0.3 + fx * 0.42
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    p = os.path.join(OUT, "mix.wav")
    sf.write(p, mix[: int(total * SR)].astype(np.float32), SR)
    return p


# ----------------------------------------------------------------------------- render
SHADE = None
def shade():
    global SHADE
    if SHADE is None:
        y = np.arange(H, dtype=np.float32)
        a = (np.exp(-((y - 1470) / 200) ** 2) * 170)[:, None].repeat(W, 1)
        SHADE = Image.new("RGBA", (W, H)); SHADE.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    return SHADE

def main():
    total = E.build_voice()
    split_caps()
    shots, caps = timeline(total)
    print("duration %.2fs" % total)
    for s in shots:
        print(f"  shot {s['id']}  {s['start']:6.2f} -> {s['end']:6.2f}  ({s['end'] - s['start']:.2f}s)  {os.path.basename(media_for(s['id']))}")
    audio = build_audio(total, shots)
    for s in shots:
        s["file"] = prepare_shot(s["id"], s["end"] - s["start"] + 0.2)
    dst = os.path.join(OUT, os.environ.get("OUT_NAME", "deodorant_v2.mp4"))
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", audio, "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-ar", "48000",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", dst], stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    preview = "--preview" in sys.argv
    si, reader, local = -1, None, 0
    for fi in range(nframes):
        t = fi / FPS
        k = max(i for i, s in enumerate(shots) if s["start"] <= t or i == 0)
        if k != si:
            if reader:
                reader.kill()
            si, local = k, 0
            reader = subprocess.Popen(["ffmpeg", "-v", "error", "-i", shots[k]["file"], "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                      stdout=subprocess.PIPE)
        buf = reader.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            last = buf
        img = Image.frombytes("RGB", (W, H), last)
        s = shots[k]; lt = t - s["start"]; D = s["end"] - s["start"]
        z = lerp(1.0, 1.07, smooth(lt / D))  # slow push-in
        if k > 0 and lt < 0.18:
            z *= lerp(1.08, 1.0, ease_out(lt / 0.18))  # punch on cut
        if z > 1.001:
            w2, h2 = int(W / z), int(H / z)
            img = img.crop(((W - w2) // 2, int((H - h2) * 0.45), (W - w2) // 2 + w2, int((H - h2) * 0.45) + h2)).resize((W, H), Image.BILINEAR)
        if s["id"] == "05" and lt > D - 0.25:  # flash into the scary part
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), (lt - (D - 0.25)) / 0.25 * 0.6)
        img.paste(shade(), (0, 0), shade())
        ov(s["id"], img, lt, D)
        for txt, a, b in caps:
            if a <= t < b:
                E.draw_caption(img, txt, t - a); break
        if t < 0.2:
            img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.2)
        if preview and fi % int(FPS * 1.5) == 0:
            os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
            img.resize((270, 480)).save(os.path.join(OUT, "preview", f"{fi:05d}.png"))
        enc.stdin.write(img.tobytes())
    if reader:
        reader.kill()
    enc.stdin.close(); enc.wait()
    print("wrote", dst)


if __name__ == "__main__":
    main()
