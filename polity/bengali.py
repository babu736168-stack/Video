"""Devanagari (Hindi) -> Bengali script transliteration: the words stay Hindi, only the letters change.
Conventions for reading Hindi from Bengali letters:  य -> য় (but ্য in conjuncts),  व -> ব,  ड़/ढ़ -> ড়/ঢ়,
ज़/फ़ -> জ়/ফ়,  ऑ/ॉ (English 'o' as in 'college') -> অ / no sign.
"""
import unicodedata

SPECIAL = {
    "व": "ব", "ै": "্যা", "ऐ": "অ্যা", "ॉ": "", "ऑ": "অ", "ॅ": "", "ऍ": "এ", "ळ": "ল", "ऱ": "র", "ऩ": "ন", "ॐ": "ওঁ",
    "क़": "ক়", "ख़": "খ়", "ग़": "গ়", "ज़": "জ়", "ड़": "ড়", "ढ़": "ঢ়", "फ़": "ফ়", "य़": "য়",
}
VIRAMA = "्"
NASAL = {}
for grp, n in (("कखगघ", "ङ"), ("चछजझ", "ञ"), ("टठडढ", "ण"), ("तथदध", "न"), ("पफबभ", "म")):
    for c in grp: NASAL[c] = n


def anusvara(nxt):
    """ं before a stop -> matching nasal + virama; before य र ल व श ष स ह -> ং; at a word end -> ঁ (nasal vowel)."""
    if nxt in NASAL: return to_bengali(NASAL[nxt]) + "্"
    if nxt and ("\u0915" <= nxt <= "\u0939" or "\u0958" <= nxt <= "\u095F"): return "ং"
    return "ঁ"


def to_bengali(s):
    s = unicodedata.normalize("NFC", s)
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if nxt == "़" and ch + nxt in SPECIAL:       # decomposed nukta letters
            out.append(SPECIAL[ch + nxt]); i += 2; continue
        if ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ch == "य":
            out.append("য" if out and out[-1] == "্" else "য়")
        elif ch == "ं":
            out.append(anusvara(nxt))
        elif ch == "़":
            out.append("়")
        elif ch in "।॥":
            out.append(ch)
        elif 0x0900 <= ord(ch) <= 0x097F:
            b = chr(ord(ch) + 0x80)
            if unicodedata.name(b, None) is None:
                raise ValueError(f"no Bengali letter for {ch!r} (U+{ord(ch):04X})")
            out.append(b)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


if __name__ == "__main__":
    for t in ["दोस्तों, सोचिए — ब्रिटिश पज़ेशन्स इन इंडिया", "गवर्नर-जनरल ऑफ़ बंगाल", "यानी, रेग्युलेट मतलब — नियमों में बाँधना",
              "बड़ा फ़ैसला, कॉलेज, विद्रोह, सत्रह सौ तिहत्तर"]:
        print(t, "->", to_bengali(t))
