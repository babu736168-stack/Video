#!/usr/bin/env python3
"""Recording script: one clip per narration line, Hindi in Bengali letters, with delivery marks and the screen.
python3 recording_script.py ch01_sample "out/Ch01 - Historical Background (sample) - recording script.md"
Marks come from the same rules the synthetic voice uses (voice.py), so both deliveries match.
"""
import os, sys, json, importlib
from bengali import to_bengali

HERE = os.path.dirname(os.path.abspath(__file__))

LEGEND = """## How to read the marks

| Mark | Meaning |
|---|---|
| ⏸ | pause (before the sentence = dramatic pause; after a question = let it sink in, about 1 second) |
| 🐢 | slower and firmer |
| ⚡ | faster |
| 🔊 | louder (punch line / exclamation) |
| 🔉 | softer (a quick explanation: “যানী… / মতলব…”) |
| — | a short breath |

Reading the letters: য় = य (ya), ব = ब and व, জ় = ज़ (za), ফ় = फ़ (fa), ড় / ঢ় = ड़ / ढ़, ঁ = nasal sound (as in দোস্তোঁ, মেঁ).
English terms are written the way they are spoken (গবর্নর-জনরল, সুপ্রীম কোর্ট).

Save each clip as its own file named by its clip ID (for example `C01-007.wav`). I will place every clip on its
screen moment and rebuild the timing around your voice.
"""


def screen_of(ev, S, state):
    if not ev:
        return state["screen"] + " (continues)"
    kind, _, body = ev.partition(":")
    if kind == "hook":
        s = "Hook screen: “" + S.CHAPTER["hook_en"].replace("\n", " ") + "”"
    elif kind == "center":
        s = f"Mind map: “Chapter {S.CHAPTER['num']} · {S.CHAPTER['title']}” appears in the centre"
    elif kind == "hub":
        h = S.HUBS[body]; s = f"Mind map: “{h['title']} {h['years']}” flies out of the centre"
    elif kind == "acts":
        s = "Mind map: all acts of the chapter fly out one by one"
    elif kind == "focus":
        if body in S.HUBS:
            name, lab = S.HUBS[body]["title"], S.HUBS[body]["label"]
        else:
            tp = next(t for t in S.TOPICS if t["id"] == body); name, lab = f"{tp['year']} {tp['name']}", tp["label"]
        s = f"Topic highlighted on the map with label “{lab.upper()}”, zoom into the board: {name}"
        state["board"] = name
    elif kind == "pt":
        s = f"Board ({state.get('board', '')}): new point → “{body.replace('|', ' — ')}”"
    elif kind == "ex":
        s = f"Board ({state.get('board', '')}): 💡 example → “{body}”"
    elif kind == "recap":
        s = "Recap screen: row → “" + body.split("|", 1)[1] + "”"
    elif kind == "outro":
        s = "Outro: map with the next topic pulsing, text “" + body + "”"
    else:
        s = ev
    state["screen"] = s.split(":")[0] if kind in ("pt", "ex") else s
    if kind in ("pt", "ex"): state["screen"] = f"Board ({state.get('board', '')})"
    return s


def main():
    mod, dst = sys.argv[1], sys.argv[2]
    S = importlib.import_module(mod)
    TL = json.load(open(os.path.join(HERE, "out", mod, "timeline.json")))
    C = S.CHAPTER
    out = [f"# Ch{C['num']:02d} – {C['title']}: recording script", "",
           "Laxmikanth, *Indian Polity*, 6th edition. Hindi narration written in Bengali letters (transliteration, not translation).",
           f"{len(TL['lines'])} clips · about {TL['total'] / 60:.1f} minutes with the synthetic voice.", "", LEGEND, "", "## Clips", ""]
    state = dict(screen="")
    for l in TL["lines"]:
        cid = f"C{C['num']:02d}-{l['i'] + 1:03d}"
        scr = screen_of(l["ev"], S, state)
        parts = []
        for s in l["sents"]:
            m = s["marks"]
            pre = "⏸ " if (m and m[0] == "⏸" and len(m) > 1 and m.count("⏸") > 1) or (m and m[0] == "⏸" and not s["text"].endswith("?")) else ""
            style = "".join(x for x in m if x != "⏸")
            post = " ⏸" if s["text"].endswith("?") else ""
            parts.append(f"{pre}{style + ' ' if style else ''}{to_bengali(s['text'])}{post}")
        mm, ss = divmod(l["start"], 60)
        out += [f"**{cid}** · `{int(mm)}:{ss:04.1f}` · 🖥 *{scr}*", "", "> " + "  ".join(parts), ""]
    open(dst, "w").write("\n".join(out))
    print("wrote", dst)


if __name__ == "__main__":
    main()
