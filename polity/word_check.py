#!/usr/bin/env python3
"""Word-by-word check of a narration: every word must be spoken, none skipped.

python3 ../polity/word_check.py ds_2min        (run from the project folder, after voice.py)

Each line of out/<script>/voice.wav (cut by timeline.json) is sent to Sarvam speech-to-text (saaras:v3,
verbatim mode, Hindi). The transcript is compared with the script word by word. Spelling variants that
sound the same (nukta, ं/ँ, न्/ं, ी/ि at word end ...) count as a match. Prints MISSING / CHANGED words
per line and writes out/<script>/word_check.json. Exit code 1 if any line has a missing word.
"""
import os, re, sys, io, json, time, difflib, unicodedata, urllib.request, urllib.error, uuid
import numpy as np
import soundfile as sf
import scipy.signal as ss

URL = "https://api.sarvam.ai/speech-to-text"


def stt(wav16):
    buf = io.BytesIO(); sf.write(buf, wav16, 16000, format="WAV", subtype="PCM_16")
    b = uuid.uuid4().hex
    parts = []
    for k, v in (("model", "saaras:v3"), ("mode", "verbatim"), ("language_code", "hi-IN")):
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"line.wav\"\r\n"
                 f"Content-Type: audio/wav\r\n\r\n".encode() + buf.getvalue() + b"\r\n")
    body = b"".join(parts) + f"--{b}--\r\n".encode()
    for attempt in range(8):
        req = urllib.request.Request(URL, data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={b}",
            "api-subscription-key": os.environ.get("SARVAM_API_KEY", "proxy-injected")})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["transcript"]
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 7: raise
            time.sleep(min(60, 5 * 2 ** attempt))


def norm(w):
    """Fold spellings that sound the same."""
    w = unicodedata.normalize("NFC", w)
    w = w.replace("़", "")                                   # nukta: ज़ = ज
    w = re.sub("[ँ]", "ं", w)                           # ँ = ं
    w = re.sub("[नमणङञ]्(?=[क-ह])", "ं", w)    # न्ड = ंड
    w = re.sub("ी$", "ि", w)                            # final ी = ि
    w = re.sub("ू$", "ु", w)                            # final ू = ु
    w = w.replace("ये", "ए").replace("यें", "एं")
    return w


def words(text):
    text = re.sub(r"[\[\]\(\)।?!,.:;—–\-‘’'\"…|]", " ", text)
    return [norm(w) for w in text.split() if w]


def main():
    mod = sys.argv[1]
    out = os.path.join(os.getcwd(), "out", mod)
    a, sr = sf.read(os.path.join(out, "voice.wav"), dtype="float32")
    tl = json.load(open(os.path.join(out, "timeline.json")))
    report, bad = [], 0
    for L in tl["lines"]:
        seg = a[int(L["start"] * sr): int(L["end"] * sr)]
        heard = stt(ss.resample_poly(seg, 16000, sr).astype(np.float32))
        said_w, heard_w = words(L["text"]), words(heard)
        sm = difflib.SequenceMatcher(a=said_w, b=heard_w, autojunk=False)
        missing, changed = [], []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "delete": missing += said_w[i1:i2]
            elif op == "replace" and "".join(said_w[i1:i2]) != "".join(heard_w[j1:j2]):   # फिसलपट्टी = फिसल पट्टी
                changed.append((" ".join(said_w[i1:i2]), " ".join(heard_w[j1:j2])))
        ok = difflib.SequenceMatcher(a="".join(said_w), b="".join(heard_w), autojunk=False).ratio()
        if missing: bad += 1
        flag = "OK " if not missing and not changed else ("MISS" if missing else "DIFF")
        print(f"{L['i']:3d} {flag} {ok:.2f}  SAID : {L['text']}\n               HEARD: {heard}", flush=True)
        for m in missing: print(f"               ✗ missing: {m}")
        for s_, h_ in changed: print(f"               ~ {s_}  →  {h_}")
        report.append(dict(i=L["i"], said=L["text"], heard=heard, match=round(ok, 3), missing=missing, changed=changed))
        time.sleep(0.5)
    json.dump(report, open(os.path.join(out, "word_check.json"), "w"), ensure_ascii=False, indent=1)
    n = len(report)
    print(f"\n{n - bad}/{n} lines with no missing word. Mean match {np.mean([r['match'] for r in report]):.2f}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
