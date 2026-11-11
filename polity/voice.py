#!/usr/bin/env python3
"""Narration with sentence-level prosody (Kokoro, Hindi voice), shared rules with the recording script.

python3 voice.py ch01_script  ->  out/<script>/voice.wav + timeline.json
Base speed 1.4x (ENGINE=kokoro, VOICE=hf_alpha). ENGINE=sarvam uses the Sarvam Bulbul API. Per sentence:
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
ENGINE = os.environ.get("ENGINE", "kokoro")           # kokoro (user-chosen hf_alpha, 1.4x) | piper | sarvam
VOICE = os.environ.get("VOICE", {"piper": "pratham", "sarvam": "ritu_hi_edtech"}.get(ENGINE, "hf_alpha"))
BASE = float(os.environ.get("BASE", "1.0" if ENGINE == "sarvam" else "1.4"))
SR = 22050 if ENGINE == "piper" else 24000

# ---- clarity fixes (Kokoro only; screen text and the recording script keep the normal spelling).
# Found with a Whisper check: espeak's Hindi rules drop the n in डिमांड, turn ख़ into a sound heard as "र",
# and add a vowel inside मतलब / पहली. These words get corrected phonemes.
SAY_PH = {
    "डिमांड": "ɖɪmˈaːnɖ",
    "ख़रीदते": "kʰəɾˈiːdteː", "ख़रीदना": "kʰəɾˈiːdnaː", "ख़रीद": "kʰəɾˈiːd", "ख़र्च": "kʰˈʌɾtʃ",
    "मतलब": "mˈʌtləb",
    "पहली": "pˈɛhliː",
}
# Lines with these words are spoken a little slower.
HARD = ("डिमांड", "टमाटर", "ख़रीद", "बढ़", "पहली", "मतलब")
HARD_SLOW = 0.9
# Letter-by-letter abbreviations: each letter is its own small clip with a short gap.
ACRONYMS = ("एन सी ई आर टी",)
TAKE = [0]
# excitement per delivery: (pitch lift, intonation spread)
PITCH = {"🔊": (1.07, 1.25), "🐢": (1.03, 1.15), "🔉": (1.0, 1.05), "": (1.05, 1.2)}

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
        st.update(speed=BASE * 0.95, gain=-4.0); st["marks"].append("🔉")
    elif (first and ("scene" in tags or "name" in tags)) or s.startswith(SLOW_START):
        st.update(speed=BASE * 0.86, gain=1.0); st["marks"].append("🐢")
    elif s.endswith("?") and words <= 5:
        st.update(speed=BASE * 0.88, gain=1.0); st["marks"].append("🐢")
    elif "punch" in tags or (s.endswith("!") and words <= 9) or words <= 5:
        st.update(speed=BASE * 0.88, gain=3.0); st["marks"] += ["🔊", "🐢"]
    elif soft:
        st.update(speed=BASE * 0.95, gain=-4.0); st["marks"].append("🔉")
    elif s.endswith("!"):
        st.update(speed=BASE * 0.95, gain=2.0); st["marks"].append("🔊")
    if s.endswith("?"):
        st["post"] = 0.75; st["marks"].append("⏸")
    return st


def parse(line):
    tags = re.findall(r"^\[(\w+)\]\s*", line)
    return tags, re.sub(r"^\[\w+\]\s*", "", line)


# ---- key words: {spoken words|Screen label|emoji} or {spoken words|@topic_id}
# The voice says the spoken words; the label/emoji pops on screen (or the topic flies out) at that moment.
KW = re.compile(r"\{([^{}|]+)\|([^{}]*)\}")
PUNCT = "।?!,.:;—–-‘’'\"…()"


def toks(text):
    """Word tokens (pure punctuation like — is not a word)."""
    return [w for w in text.split() if w.strip(PUNCT)]


def keywords(text):
    """-> (spoken text, [dict(word=index of first spoken word, label, emoji, topic)])"""
    out, spoken, pos = [], "", 0
    for m in KW.finditer(text):
        spoken += text[pos:m.start()]
        parts = [p.strip() for p in m.group(2).split("|")]
        topic = parts[0][1:] if parts[0].startswith("@") else None
        out.append(dict(word=len(toks(spoken)), label="" if topic else parts[0],
                        emoji=parts[1] if len(parts) > 1 else "", topic=topic, said=m.group(1)))
        spoken += m.group(1); pos = m.end()
    return spoken + text[pos:], out


def word_starts(a, words):
    """Start time (s) of each word inside one synthesized chunk.
    Time is shared by syllable length; pauses found in the audio are matched to the commas."""
    if not words: return []
    def syl(w):
        return max(1, len(re.findall("[\u0905-\u0914\u0915-\u0939\u0958-\u095f][\u093e-\u094c]?", w)) +
                   len(re.findall("[\u093e\u0940\u0947\u0948\u094b\u094c]", w)) * 0.5)
    dur = len(a) / SR
    # internal pauses: 20 ms frames below -35 dB of the peak, lasting >= 120 ms
    fr = int(0.02 * SR); n = len(a) // fr
    rms = np.sqrt(np.mean(a[:n * fr].reshape(n, fr) ** 2, axis=1) + 1e-12) if n else np.zeros(0)
    quiet = rms < (rms.max() if n else 1) * 10 ** (-35 / 20)
    gaps, k = [], 0
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]: j += 1
            if j - k >= 6 and k > 0 and j < n: gaps.append((k * fr / SR, j * fr / SR))
            k = j
        else: k += 1
    commas = [i for i, w in enumerate(words[:-1]) if w[-1:] in ",;:"]
    # split the chunk at the pauses that belong to commas (largest pauses, kept in order)
    use = sorted(sorted(gaps, key=lambda g: g[0] - g[1])[:len(commas)]) if len(gaps) >= len(commas) else []
    bounds = [0] + [c + 1 for c in commas] + [len(words)] if use else [0, len(words)]
    times = [0.0] + [g[1] for g in use] + [dur] if use else [0.0, dur]
    ends = [g[0] for g in use] + [dur] if use else [dur]
    st = []
    for s_i in range(len(bounds) - 1):
        ws = words[bounds[s_i]:bounds[s_i + 1]]; t0, t1 = times[s_i], ends[s_i]
        w8 = [syl(w) for w in ws]; tot = sum(w8); acc = 0
        for w in w8: st.append(t0 + (t1 - t0) * acc / tot); acc += w
    return st


def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx): return a
    return a[max(0, idx[0] - int(SR * 0.01)): idx[-1] + int(SR * 0.02)]


def main():
    mod = sys.argv[1] if len(sys.argv) > 1 else "ch01_script"
    S = importlib.import_module(mod)
    out = os.path.join(HERE, "out", mod); os.makedirs(out, exist_ok=True)
    if ENGINE == "piper":
        from piper_hi import Piper
        from excite import excite
        P = Piper(f"{TTS}/vits-piper-hi_IN-{VOICE}-medium/hi_IN-{VOICE}-medium.onnx")
        def synth(c, spd, marks):
            a, sr = P(c, speed=spd, noise=0.7, noise_w=0.9)
            key = "🔊" if "🔊" in marks else "🐢" if "🐢" in marks else "🔉" if "🔉" in marks else ""
            lift, spread = PITCH[key]
            return excite(a, sr, lift=lift, spread=spread, bright=0.15) * 0.8
    elif ENGINE == "kokoro":
        from kokoro_onnx import Kokoro
        k = Kokoro(f"{TTS}/kokoro-v1.0.onnx", f"{TTS}/voices-v1.0.bin")
        fix = [(k.tokenizer.phonemize(w, "hi"), ph) for w, ph in SAY_PH.items()]
        fix.sort(key=lambda x: -len(x[0]))

        def say(c, spd):
            ph = k.tokenizer.phonemize(c, "hi")
            for bad, good in fix: ph = ph.replace(bad, good)
            return np.asarray(k.create(ph, voice=VOICE, speed=spd, lang="hi", is_phonemes=True)[0], np.float32)

        def synth(c, spd, marks):
            parts = re.split("(" + "|".join(map(re.escape, ACRONYMS)) + ")", c)
            out = []
            for p in parts:
                p = p.strip(" ,")
                if not p: continue
                if p in ACRONYMS:
                    for L in p.split():
                        out += [trim(np.asarray(k.create(L, voice=VOICE, speed=min(spd, 1.2), lang="hi")[0], np.float32)),
                                np.zeros(int(0.1 * SR), np.float32)]
                else:
                    out += [trim(say(p, spd)), np.zeros(int(0.08 * SR), np.float32)]
            return np.concatenate(out[:-1]) if out else np.zeros(1, np.float32)
    if ENGINE == "sarvam":
        # Sarvam Bulbul REST API. In a cloud session the network proxy adds the key; elsewhere set SARVAM_API_KEY.
        import base64, io, urllib.request
        MODEL = os.environ.get("SARVAM_MODEL", "bulbul:v4-flash")

        import hashlib, time, urllib.error
        CACHE = os.path.join(TTS, "sarvam_cache"); os.makedirs(CACHE, exist_ok=True)

        def synth(c, spd, marks):
            body = dict(text=c, language_code="hi-IN", model=MODEL, speaker=VOICE, pace=round(spd, 2),
                        speech_sample_rate=SR, output_audio_codec="wav")
            tag = dict(body, take=TAKE[0]) if TAKE[0] else body      # a retake = a fresh recording of the same text
            key = os.path.join(CACHE, hashlib.sha1(json.dumps(tag, sort_keys=True).encode()).hexdigest() + ".wav")
            if not os.path.exists(key):
                for attempt in range(8):          # the API rate-limits (429): wait and retry
                    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", data=json.dumps(body).encode(),
                                                 headers={"Content-Type": "application/json",
                                                          "api-subscription-key": os.environ.get("SARVAM_API_KEY", "proxy-injected")})
                    try:
                        with urllib.request.urlopen(req, timeout=120) as r:
                            wav = base64.b64decode("".join(json.load(r)["audios"])); break
                    except urllib.error.HTTPError as e:
                        if e.code != 429 or attempt == 7: raise
                        time.sleep(min(60, 5 * 2 ** attempt))
                open(key, "wb").write(wav)
                time.sleep(float(os.environ.get("SARVAM_GAP", "1.0")))
            a, sr = sf.read(key, dtype="float32")
            return a if a.ndim == 1 else a.mean(1)
    rng = np.random.default_rng(7)
    audio, t, tl = [np.zeros(int(0.6 * SR))], 0.6, []
    prev_ev = None
    # out/<script>/retakes.json: {"line number": take number} for lines the word check flagged
    rt_path = os.path.join(out, "retakes.json")
    retakes = json.load(open(rt_path)) if os.path.exists(rt_path) else {}
    for i, (ev, line) in enumerate(S.LINES):
        TAKE[0] = int(retakes.get(str(i), 0))
        tags, text = parse(line)
        text, kws = keywords(text)
        wtimes = []                       # start time of every spoken word in this line
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
            spd = float(np.clip(st["speed"] * (1 + rng.uniform(-0.04, 0.04)), 0.6 if ENGINE == "sarvam" else 0.9, 1.8))
            if ENGINE == "kokoro" and any(w in sent for w in HARD):
                spd = round(spd * HARD_SLOW, 3)
                if "🐢" not in st["marks"]: st["marks"].append("🐢")
            g = 10 ** ((st["gain"] + rng.uniform(-0.8, 0.8)) / 20)
            for c_i, c in enumerate(chunks):
                if not c: continue
                a = trim(synth(c, spd, st["marks"])) * g
                wtimes += [t + x for x in word_starts(a, toks(c))]
                audio.append(a); t += len(a) / SR
                if c_i + 1 < len(chunks):
                    b = 0.22 + rng.uniform(-0.04, 0.05)
                    audio.append(np.zeros(int(b * SR))); t += b
            post = st["post"] + rng.uniform(-0.05, 0.08)
            audio.append(np.zeros(int(post * SR))); t += post
            rec.append(dict(text=sent, speed=round(spd, 2), gain=st["gain"], marks=st["marks"]))
        for kw in kws:
            kw["t"] = round(wtimes[kw["word"]] if kw["word"] < len(wtimes) else start, 3)
        tl.append(dict(i=i, ev=ev, text=text, tags=tags, start=round(start, 3), end=round(t, 3), sents=rec, kw=kws))
        print(f"{i:3d} {start:7.2f} {ev or '':12.12s} {text[:60]}")
    audio.append(np.zeros(int(1.5 * SR))); t += 1.5
    a = np.concatenate(audio); a = a / max(1e-6, np.abs(a).max()) * 0.9
    sf.write(os.path.join(out, "voice.wav"), a, SR)
    json.dump(dict(total=t, lines=tl, voice=VOICE), open(os.path.join(out, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("total", round(t, 1), "s")


if __name__ == "__main__":
    main()
