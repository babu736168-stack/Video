#!/usr/bin/env python3
"""Step 1: narration (Kokoro offline TTS) -> out/voice.wav + out/timeline.json.

timeline.json holds, per shot, its start/end on the video timeline and the caption chunks
(2-3 words each, timed by syllable-ish length inside the line), so Blender can render each
shot with exactly the right number of frames.
Use your own recording instead:  VOICE_FILE=narration.wav python3 voice.py
(the file must contain the lines below in order with a short pause between them).
"""
import os, re, json, subprocess
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
DATA = os.environ.get("DATA_DIR", os.path.join(HERE, "..", "tunguska_demo", "data"))
VOICE = os.environ.get("VOICE", "am_michael")
SPEED = float(os.environ.get("SPEED", "1.12"))
SR = 24000
LEAD, TAIL = 0.15, 1.2

# (shot id, narration line) — one 3D shot per line
LINES = [
    ("intro",    "What happens if you hold in a sneeze?"),
    ("tickle",   "A sneeze starts when something tickles the inside of your nose."),
    ("brain",    "Your brain fires an alarm,"),
    ("lungs",    "and your chest muscles blast air out at incredible speed."),
    ("pinch",    "But if you pinch your nose and shut your mouth,"),
    ("trapped",  "all that air has nowhere to go."),
    ("pressure", "The pressure in your airway can jump up to twenty times higher than a normal sneeze."),
    ("ear",      "It can get forced into your ears and burst an eardrum,"),
    ("eye",      "or pop tiny blood vessels in your eyes."),
    ("throat",   "In rare cases, doctors have even seen it tear a hole in someone's throat."),
    ("elbow",    "So next time, don't fight it. Just sneeze into your elbow."),
]
GAP = 0.12  # silence between lines (s); shots cut on the line boundaries


def trim(x, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 240): idx[-1] + 600] if len(idx) else x


def chunks(text, n=3):
    words = text.split()
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else ""
        if re.search(r"[,.?!]$", w) or (len(cur) >= n and not re.search(r"[,.?!]$", nxt)) or len(cur) > n:
            out.append(" ".join(cur)); cur = []
    if cur:
        if out and len(cur) == 1:
            out[-1] += " " + cur[0]
        else:
            out.append(" ".join(cur))
    return out


def weight(s):
    return len(re.sub(r"[^a-z]", "", s.lower())) + 3 * len(re.findall(r"[,.?!]", s))


def main():
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(DATA, "kokoro.onnx"), os.path.join(DATA, "voices.bin"))
    pieces = []
    for sid, text in LINES:
        s, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        assert sr == SR
        pieces.append(trim(s.astype(np.float32)))
    t = LEAD
    audio = [np.zeros(int(LEAD * SR), np.float32)]
    shots = []
    for (sid, text), p in zip(LINES, pieces):
        d = len(p) / SR
        cs = chunks(text)
        ws = np.array([weight(c) for c in cs], float); ws /= ws.sum()
        edges = t + np.concatenate([[0], np.cumsum(ws)]) * d
        shots.append(dict(id=sid, text=text, voice_start=t, voice_end=t + d,
                          caps=[dict(text=c, t0=float(a), t1=float(b)) for c, a, b in zip(cs, edges[:-1], edges[1:])]))
        audio += [p, np.zeros(int(GAP * SR), np.float32)]
        t += d + GAP
    total = t + TAIL
    audio.append(np.zeros(int(TAIL * SR), np.float32))
    a = np.concatenate(audio)
    a = a / np.abs(a).max() * 0.9
    raw = os.path.join(OUT, "voice_raw.wav"); sf.write(raw, a, SR)
    # light "documentary" polish: warmth + presence + compression
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af",
                    "bass=g=3:f=120,equalizer=f=3000:t=q:w=1:g=2,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3",
                    os.path.join(OUT, "voice.wav")], check=True)
    # shot boundaries: each shot runs from its line start until the next line starts
    for i, s in enumerate(shots):
        s["start"] = 0.0 if i == 0 else s["voice_start"] - GAP / 2
        s["end"] = shots[i + 1]["voice_start"] - GAP / 2 if i + 1 < len(shots) else total
    json.dump(dict(total=total, shots=shots), open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    for s in shots:
        print(f'{s["id"]:9s} {s["start"]:6.2f}-{s["end"]:6.2f}  {[c["text"] for c in s["caps"]]}')
    print("total", round(total, 2))


if __name__ == "__main__":
    main()
