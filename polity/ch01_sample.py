"""5-minute sample of Chapter 1: hook, mind map, 1600-1858 background, Regulating Act 1773, recap, tease."""
from ch01_script import CHAPTER, TOPICS, HUBS, LINES as FULL

_end = next(i for i, (ev, _) in enumerate(FULL) if ev == "focus:t1781")
LINES = FULL[:_end - 1] + [   # drop the 1773 hook line; the tease below replaces it
    ("recap:t1773|Regulating Act – first control, Governor-General of Bengal, Supreme Court at Calcutta",
     "तो याद रखिए — सत्रह सौ तिहत्तर का रेग्युलेटिंग ऐक्ट: पहली लगाम, गवर्नर-जनरल ऑफ़ बंगाल, और कलकत्ता का सुप्रीम कोर्ट।"),
    ("outro:Next: the Act of Settlement, 1781",
     "लेकिन… लगाम कसते ही, कलकत्ता में एक नई लड़ाई शुरू हो गई — सरकार बनाम सुप्रीम कोर्ट!"),
    (None, "[punch] वो लड़ाई कैसे सुलझी? अगले हिस्से में — ऐक्ट ऑफ़ सेटलमेंट, सत्रह सौ इक्यासी!"),
]
