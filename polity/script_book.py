#!/usr/bin/env python3
"""One script book for many videos (read before any voice/video is made).

python3 ../polity/script_book.py "out/Economics Part 1 - Script Book.md" econ00p_promo econ00b_roadmap econ01_palampur ...
(run from econ/)

For every video: title, source, estimated length, then each line as
  Hindi narration (key words in bold) / the same line in Bengali letters / what appears on screen.
"""
import os, re, sys, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.getcwd()); sys.path.insert(0, HERE)
from bengali import to_bengali

KW = re.compile(r"\{([^{}|]+)\|([^{}]*)\}")
SEC = {"hook": "Hook", "agenda": "“AAJ KI CLASS MEIN”", "center": "Mind map", "recap": "Recap", "end": "End screen"}
SEC_PER_CHAR = 0.084          # measured on Econ01 (Sarvam, Sanchita, pace 1.0, incl. pauses)
MARK = {"punch": "🔊 ", "scene": "🐢 ", "name": "🐢 "}


def video_name(mod, S):
    C = S.CHAPTER; n = C.get("num", 0)
    if C.get("video"): return C["video"]
    if mod.endswith("promo"): return "Econ00p – Course Promo"
    if mod.endswith("roadmap"): return "Econ00b – Syllabus Roadmap"
    return f"Econ{n:02d} – {C['title']}"


def book(mods):
    toc, body, total = [], [], 0.0
    for mod in mods:
        S = importlib.import_module(mod)
        topics = {t["id"]: t for t in S.TOPICS}
        name = video_name(mod, S)
        doc = (S.__doc__ or "").strip().split("\n")
        src = next((l.strip() for l in doc if l.startswith("Source")), "")
        draft = any("DRAFT" in l for l in doc)
        chars = sum(len(KW.sub(lambda m: m.group(1), re.sub(r"^\[\w+\]\s*", "", l))) for _, l in S.LINES)
        mins = chars * SEC_PER_CHAR / 60 / (1.1 if mod.endswith("promo") else 1.0)
        tl = os.path.join(os.getcwd(), "out", mod, "timeline.json")
        made = os.path.exists(tl)
        if made:                                   # already voiced: use the real length
            import json; mins = json.load(open(tl))["total"] / 60
        total += mins
        anchor = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        toc.append(f"| [{name}](#{anchor}) | {len(S.LINES)} | ~{int(mins)} min {int(mins % 1 * 60)} s | "
                   f"{'⚠️ check against Ramesh Singh' if draft else 'NCERT / course plan'} | {'✅ made' if made else 'script only'} |")
        body += ["", "---", "", f"## {name}", "", f"*{doc[0]}*", ""]
        if src: body += [src, ""]
        if draft:
            body += ["> ⚠️ **Draft from standard facts.** Written without the Ramesh Singh book in hand: please check it "
                     "against the chapter (or send the pages) before the video is made.", ""]
        body += [f"**{len(S.LINES)} lines · about {int(mins)} min {int(mins % 1 * 60)} s**", ""]
        for i, (ev, line) in enumerate(S.LINES):
            ev = ev or ""; kind, _, b = ev.partition(":")
            head = SEC.get(kind) or (f"Topic: {topics[b]['name']} — “{topics[b]['label'].upper()}” {topics[b]['icon']}"
                                     if kind == "focus" else "Next class" if kind == "outro"
                                     else "Call to action" if kind == "outro" else None)
            if head: body += ["", f"### {head}", ""]
            tags = re.findall(r"^\[(\w+)\]", line)
            text = re.sub(r"^\[\w+\]\s*", "", line)
            hindi = KW.sub(lambda m: f"**{m.group(1)}**", text)
            plain = KW.sub(lambda m: m.group(1), text)
            screen = []
            for m in KW.finditer(text):
                p = [x.strip() for x in m.group(2).split("|")]
                if not p[0].startswith("@"): screen.append(f"{p[1] + ' ' if len(p) > 1 and p[1] else ''}{p[0]}")
            notes = []
            if kind == "anim": notes.append("stage back to pictures" if b == "none" else f"animation: {b.replace('_', ' ')}")
            if kind == "ex": notes.append("💡 example")
            if kind == "topics": notes.append("topics fly out on the map")
            mark = "".join(MARK[t] for t in tags if t in MARK)
            body.append(f"**{i + 1}.** {mark}{hindi}  ")
            body.append(f"   🔤 {to_bengali(plain)}  ")
            if screen or notes:
                body.append("   🖥 " + " · ".join(screen + [f"*{n}*" for n in notes]))
            body.append("")
    head = [f"# {os.environ.get('BOOK_TITLE', 'Economics · Part 1 (Neev) · Complete Script Book')}", "",
            "**The VisualMind** — See it. Understand it. Remember it.", "",
            "Course order: Ramesh Singh, *Indian Economy* (18th edition), Chapters 1–3, with the NCERT foundation "
            "classes first. Voice: Sarvam, Sanchita, speed 1.0 (promo 1.1).", "",
            "**How to read each line:** 1st line = what is spoken (Hindi; **bold** = key word), "
            "🔤 = the same line in Bengali letters (for recording in your own voice), "
            "🖥 = what pops on screen at that moment (English letters + emoji). No other subtitles. "
            "🔊 = punch line (louder), 🐢 = slower and firmer.", "",
            "## Contents", "", "| Video | Lines | Length | Source | Status |", "|---|---|---|---|---|"] + toc + \
           ["", f"**Total: {len(mods)} videos · about {int(total // 60)} h {int(total % 60)} min**"]
    return "\n".join(head + body) + "\n"


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    open(dst, "w").write(book(sys.argv[2:]))
    print("wrote", dst)
