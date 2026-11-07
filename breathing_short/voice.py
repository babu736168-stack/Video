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
SPEED = float(os.environ.get("SPEED", "1.2"))
SR = 24000
LEAD, TAIL = 0.15, 1.2

# (shot id, narration line) — one 3D shot per line
LINES = [
    ("intro",     "Why do you breathe faster when you run?"),
    ("muscles",   "Every stride makes your leg muscles burn through ATP, their energy, much faster."),
    ("mito",      "To make more, tiny mitochondria use extra oxygen, and release extra carbon dioxide."),
    ("brain",     "But your brain doesn't wait for that to build up. It speeds up your breathing from the very first step,"),
    ("diaphragm", "pulling your diaphragm down harder, for deeper, faster breaths."),
    ("alveoli",   "In your lungs, oxygen floods into your blood, and carbon dioxide gets breathed out."),
    ("heart",     "Your heart pumps faster to deliver it all."),
    ("sprint",    "Sprint hard, and acid builds up in your muscles."),
    ("buffer",    "Your blood buffers it, releasing even more carbon dioxide, so you gasp."),
    ("lactate",   "And no, lactic acid isn't the villain. Lactate is actually fuel for your heart and muscles."),
    ("after",     "Even after you stop, you keep panting while your body recovers."),
    ("trained",   "Train regularly, and your heart and muscles adapt, so the same pace feels easier."),
]
# Hindi version: LANG_CODE=hi python3 voice.py (voice hm_omega, speed 1.25).
LINES_HI = [
    ("intro",     "दौड़ते समय हमारी साँस इतनी तेज़ क्यों हो जाती है?"),
    ("muscles",   "हर कदम के साथ, टांगों की मांसपेशियाँ अपनी ऊर्जा, यानी ए टी पी, बहुत तेज़ी से खर्च करती हैं।"),
    ("mito",      "इसे दोबारा बनाने के लिए, माइटोकॉन्ड्रिया ज़्यादा ऑक्सीजन लेते हैं, और ज़्यादा कार्बन डाइऑक्साइड छोड़ते हैं।"),
    ("brain",     "लेकिन दिमाग इसके जमा होने का इंतज़ार नहीं करता। पहले ही कदम से वह साँस तेज़ कर देता है,"),
    ("diaphragm", "और डायाफ्राम को ज़ोर से नीचे खींचता है, ताकि साँसें गहरी और तेज़ हों।"),
    ("alveoli",   "फेफड़ों में ऑक्सीजन खून में जाती है, और कार्बन डाइऑक्साइड बाहर निकल जाती है।"),
    ("heart",     "दिल भी तेज़ धड़कता है, ताकि यह सब मांसपेशियों तक पहुँचे।"),
    ("sprint",    "तेज़ स्प्रिंट करने पर, मांसपेशियों में एसिड बढ़ने लगता है।"),
    ("buffer",    "खून का बाइकार्बोनेट इसे संभालता है, जिससे और कार्बन डाइऑक्साइड बनती है, और आप हाँफने लगते हैं।"),
    ("lactate",   "और हाँ, लैक्टिक एसिड विलेन नहीं है। लैक्टेट तो दिल और मांसपेशियों के लिए ईंधन है।"),
    ("after",     "रुकने के बाद भी आप हाँफते रहते हैं, क्योंकि शरीर रिकवरी कर रहा होता है।"),
    ("trained",   "नियमित ट्रेनिंग से दिल और मांसपेशियाँ मज़बूत होती हैं, और वही रफ़्तार आसान लगने लगती है।"),
]
LANG = os.environ.get("LANG_CODE", "en")
if LANG == "hi":
    LINES = LINES_HI
    VOICE = os.environ.get("VOICE", "hm_omega")
    SPEED = float(os.environ.get("SPEED", "1.25"))
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
        if re.search(r"[,.?!।]$", w) or (len(cur) >= n and not re.search(r"[,.?!।]$", nxt)) or len(cur) > n:
            out.append(" ".join(cur)); cur = []
    if cur:
        if out and len(cur) == 1:
            out[-1] += " " + cur[0]
        else:
            out.append(" ".join(cur))
    return out


def weight(s):
    return len(re.sub(r"[\W\d_]", "", s.lower())) + 3 * len(re.findall(r"[,.?!।]", s))


def main():
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(DATA, "kokoro.onnx"), os.path.join(DATA, "voices.bin"))
    pieces = []
    for sid, text in LINES:
        s, sr = k.create(text, voice=VOICE, speed=SPEED, lang="hi" if LANG == "hi" else "en-us")
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
