#!/usr/bin/env python3
"""Narration with sentence-level prosody (Kokoro, Hindi voice), shared rules with the recording script.

python3 voice.py ch01_script  ->  out/<script>/voice.wav + timeline.json
Base speed 1.5x. Per sentence:
  slow+firm  scene openers, सोचिए / ध्यान दीजिए / याद रखिए, the line naming the topic
  loud+slow  exclamations and short punch lines
  soft       यानी / मतलब explanations
  pause after questions; dramatic pause before लेकिन / और फिर / नतीजा; short breath at "—"
  small random speed/level variation so no two sentences sound the same.
"""
import os, re, sys, json, importlib
import numpy as np
import soundfile as sf

HERE = os.getcwd()          # run from the project folder (polity/, econ/ ...)
sys.path.insert(0, HERE)
TTS = "/tmp/claude-0/tts"
VOICE = os.environ.get("VOICE", "hm_omega")
BASE = 1.5
SR = 24000

SLOW_START = ("सोचिए", "ध्यान दीजिए", "याद रखिए")
DRAMA_START = ("लेकिन", "और फिर", "नतीजा", "और नतीजा")
SOFT_START = ("यानी", "मतलब")


def sentences(text):
    """Split a line into sentences, keeping the end mark."""
    parts = re.findall(r"[^।?!]+[।?!]*", text)
    return [p.strip() for p in parts if p.strip()]


def style(sent, tags, first):
    """-> dict(speed, gain_db, pre, post, marks) for one sentence."""
    s = sent.strip("‘’'\" ")
    words = len(s.split())
    st = dict(speed=BASE, gain=0.0, pre=0.0, post=0.32, marks=[])
    soft = s.startswith(SOFT_START) or re.match(r"^[^—]{1,40}मतलब —", s) or re.match(r"^[^—,]{1,30}, यानी", s)
    if s.startswith(DRAMA_START) or s.startswith("लेकिन…"):
        st["pre"] = 0.6; st["marks"].append("⏸")
    if soft and not first:
        st.update(speed=1.42, gain=-4.0); st["marks"].append("🔉")
    elif (first and ("scene" in tags or "name" in tags)) or s.startswith(SLOW_START):
        st.update(speed=1.28, gain=1.0); st["marks"].append("🐢")
    elif s.endswith("?") and words <= 5:
        st.update(speed=1.3, gain=1.0); st["marks"].append("🐢")
    elif "punch" in tags or (s.endswith("!") and words <= 9) or words <= 5:
        st.update(speed=1.3, gain=3.0); st["marks"] += ["🔊", "🐢"]
    elif soft:
        st.update(speed=1.42, gain=-4.0); st["marks"].append("🔉")
    elif s.endswith("!"):
        st.update(speed=1.38, gain=2.0); st["marks"].append("🔊")
    if s.endswith("?"):
        st["post"] = 0.75; st["marks"].append("⏸")
    return st


def parse(line):
    tags = re.findall(r"^\[(\w+)\]\s*", line)
    return tags, re.sub(r"^\[\w+\]\s*", "", line)


def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx): return a
    return a[max(0, idx[0] - 240): idx[-1] + 480]


def main():
    mod = sys.argv[1] if len(sys.argv) > 1 else "ch01_script"
    S = importlib.import_module(mod)
    out = os.path.join(HERE, "out", mod); os.makedirs(out, exist_ok=True)
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{TTS}/kokoro-v1.0.onnx", f"{TTS}/voices-v1.0.bin")
    rng = np.random.default_rng(7)
    audio, t, tl = [np.zeros(int(0.6 * SR))], 0.6, []
    prev_ev = None
    for i, (ev, line) in enumerate(S.LINES):
        tags, text = parse(line)
        # longer breath at a new screen section
        gap = 0.0
        if ev and (ev.startswith(("focus", "hub", "center", "recap", "outro", "acts"))):
            gap = 0.9 if ev.startswith("focus") else 0.4
        audio.append(np.zeros(int(gap * SR))); t += gap
        start = t; rec = []
        for j, sent in enumerate(sentences(text)):
            st = style(sent, tags, j == 0)
            chunks = [c.strip() for c in sent.split("—")]
            if st["pre"]:
                audio.append(np.zeros(int(st["pre"] * SR))); t += st["pre"]
            spd = float(np.clip(st["speed"] * (1 + rng.uniform(-0.04, 0.04)), 1.0, 1.8))
            g = 10 ** ((st["gain"] + rng.uniform(-0.8, 0.8)) / 20)
            for c_i, c in enumerate(chunks):
                if not c: continue
                a, sr = k.create(c, voice=VOICE, speed=spd, lang="hi")
                a = trim(np.asarray(a, np.float32)) * g
                audio.append(a); t += len(a) / SR
                if c_i + 1 < len(chunks):
                    b = 0.22 + rng.uniform(-0.04, 0.05)
                    audio.append(np.zeros(int(b * SR))); t += b
            post = st["post"] + rng.uniform(-0.05, 0.08)
            audio.append(np.zeros(int(post * SR))); t += post
            rec.append(dict(text=sent, speed=round(spd, 2), gain=st["gain"], marks=st["marks"]))
        tl.append(dict(i=i, ev=ev, text=text, tags=tags, start=round(start, 3), end=round(t, 3), sents=rec))
        print(f"{i:3d} {start:7.2f} {ev or '':12.12s} {text[:60]}")
    audio.append(np.zeros(int(1.5 * SR))); t += 1.5
    a = np.concatenate(audio); a = a / max(1e-6, np.abs(a).max()) * 0.9
    sf.write(os.path.join(out, "voice.wav"), a, SR)
    json.dump(dict(total=t, lines=tl, voice=VOICE), open(os.path.join(out, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("total", round(t, 1), "s")


if __name__ == "__main__":
    main()
