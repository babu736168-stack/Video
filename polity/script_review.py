#!/usr/bin/env python3
"""Readable script for review BEFORE any voice or video is made.

python3 ../polity/script_review.py econ02_scarcity "out/Econ02 - script for review.md"     (run from econ/)

Per line: number, narration (key words in bold), and what appears on screen at that moment.
Sections follow the screens (hook, agenda, map, each topic, recap, next class, end screen).
"""
import os, re, sys, importlib

sys.path.insert(0, os.getcwd())
KW = re.compile(r"\{([^{}|]+)\|([^{}]*)\}")
SEC = {"hook": "Hook", "agenda": "“AAJ KI CLASS MEIN”", "center": "Mind map", "recap": "Recap", "end": "End screen"}
SEC_PER_CHAR = 0.084          # measured on Econ01 (Sarvam, Sanchita, pace 1.0, incl. pauses)


def main():
    mod, dst = sys.argv[1], sys.argv[2]
    S = importlib.import_module(mod)
    C = S.CHAPTER; topics = {t["id"]: t for t in S.TOPICS}
    src = (S.__doc__ or "").split("\n")
    out = [f"# Econ{C['num']:02d} – {C['title']}: script for review", "",
           f"*{src[0].strip()}*", "", next((l.strip() for l in src if l.startswith("Source")), ""), "",
           "**How to read:** each line is spoken as written. **Bold** words are the key words: at the moment they are "
           "spoken, the label after → pops on screen (in English letters) with its emoji. No other subtitles.", ""]
    n_chars = 0
    for i, (ev, line) in enumerate(S.LINES):
        ev = ev or ""
        kind, _, body = ev.partition(":")
        head = None
        if kind in SEC: head = SEC[kind]
        elif kind == "focus": head = f"Topic: {topics[body]['name']} — “{topics[body]['label'].upper()}” {topics[body]['icon']}"
        elif kind == "outro": head = "Next class teaser"
        if head: out += ["", f"## {head}", ""]
        text = re.sub(r"^\[\w+\]\s*", "", line)
        tags = re.findall(r"^\[(\w+)\]", line)
        spoken = KW.sub(lambda m: f"**{m.group(1)}**", text)
        n_chars += len(KW.sub(lambda m: m.group(1), text))
        screen = []
        for m in KW.finditer(text):
            p = [x.strip() for x in m.group(2).split("|")]
            if not p[0].startswith("@"): screen.append(f"{p[1] + ' ' if len(p) > 1 and p[1] else ''}{p[0]}")
        notes = []
        if kind == "anim": notes.append(f"animation: {body}" if body != "none" else "stage back to pictures")
        if kind == "ex": notes.append("💡 example (amber)")
        if kind == "topics": notes.append("topics fly out on the map")
        if "punch" in tags: notes.append("punch line")
        out.append(f"{i + 1}. {spoken}")
        extra = ("  \n   ↳ *on screen:* " + " · ".join(screen)) if screen else ""
        if notes: extra += ("  \n   ↳ " if not screen else " · ") + "*" + ", ".join(notes) + "*"
        if extra: out[-1] += extra
    mins = n_chars * SEC_PER_CHAR / 60
    out[4:4] = [f"**{len(S.LINES)} lines · about {int(mins)} min {int(mins % 1 * 60)} s** (estimate)", ""]
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    open(dst, "w").write("\n".join(out) + "\n")
    print("wrote", dst, f"(~{mins:.1f} min)")


if __name__ == "__main__":
    main()
