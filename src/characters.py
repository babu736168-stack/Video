"""Cartoon character drawings for "The Jacket Must Go On".

Every character is drawn on its own transparent canvas (CW x CH) whose
anchor point (the spot that touches the ground) is ANCHOR. The renderer
scales and pastes these canvases into each frame.
"""
from functools import lru_cache
from PIL import Image, ImageDraw

CW, CH = 360, 520
ANCHOR = (180, 515)
OL = (25, 25, 30)          # outline colour
SKIN = (238, 200, 165)

# Canvas y of the top of each character's head (used to aim speech bubbles).
HEAD_TOP = {"jensen": 45, "jacket": 150, "chip": 235, "danny": 15, "wendy": 35}

INFO = {
    "jensen": dict(name="JENSEN", color=(118, 185, 0)),
    "jacket": dict(name="SIR LEATHERWORTH", color=(214, 160, 80)),
    "chip":   dict(name="CHIP", color=(0, 185, 225)),
    "danny":  dict(name="DANNY", color=(235, 85, 60)),
    "wendy":  dict(name="WENDY WALLSTREET", color=(230, 100, 200)),
}


def _eyes(d, left, right, blink, ko=False, pupil=(20, 20, 25), size=7):
    for (cx, cy) in (left, right):
        if ko:
            d.line((cx - 9, cy - 9, cx + 9, cy + 9), fill=OL, width=5)
            d.line((cx - 9, cy + 9, cx + 9, cy - 9), fill=OL, width=5)
        elif blink:
            d.line((cx - 10, cy, cx + 10, cy), fill=OL, width=5)
        else:
            d.ellipse((cx - size, cy - size, cx + size, cy + size), fill=pupil)
            d.ellipse((cx - size + 3, cy - size + 2, cx - size + 6, cy - size + 5), fill=(255, 255, 255))


def _mouth(d, cx, cy, talk, w=22, smile=True):
    if talk:
        d.ellipse((cx - w // 2 - 2, cy - 10, cx + w // 2 + 2, cy + 14), fill=(120, 30, 40), outline=OL, width=4)
        d.chord((cx - 8, cy + 2, cx + 8, cy + 14), 0, 180, fill=(230, 100, 110))
    elif smile:
        d.arc((cx - w, cy - 16, cx + w, cy + 10), 25, 155, fill=OL, width=5)
    else:
        d.line((cx - w // 2, cy, cx + w // 2, cy), fill=OL, width=5)


def _jacket_details(d, x0, x1, top, bottom):
    """Lapels, zipper and leather shine for a jacket torso."""
    mid = (x0 + x1) // 2
    d.polygon([(mid - 30, top), (mid + 30, top), (mid, top + 75)], fill=(12, 12, 14))
    d.polygon([(mid - 30, top), (mid, top + 75), (mid - 18, top + 88), (x0 + 12, top + 12)],
              fill=(62, 62, 70), outline=OL)
    d.polygon([(mid + 30, top), (mid, top + 75), (mid + 18, top + 88), (x1 - 12, top + 12)],
              fill=(62, 62, 70), outline=OL)
    d.line((mid, top + 80, mid, bottom - 4), fill=(140, 140, 150), width=3)
    d.arc((x0 + 6, top + 8, x0 + 60, top + 90), 200, 270, fill=(175, 175, 190), width=5)
    d.arc((x1 - 60, top + 8, x1 - 6, top + 90), 270, 340, fill=(175, 175, 190), width=5)
    d.line((x0 + 22, bottom - 60, x0 + 22, bottom - 20), fill=(110, 110, 120), width=4)


def _jacket_face(d, cx, cy, talk, blink, small=False):
    """Sir Leatherworth's face: eyes, monocle, curly mustache."""
    k = 0.55 if small else 1.0
    ex = int(22 * k)
    er = int(15 * k)
    for sx in (-1, 1):
        x = cx + sx * ex
        d.ellipse((x - er, cy - er, x + er, cy + er), fill=(255, 255, 255), outline=OL, width=3)
    _eyes(d, (cx - ex, cy), (cx + ex, cy), blink, size=int(6 * k) + 1)
    d.ellipse((cx + ex - er - 4, cy - er - 4, cx + ex + er + 4, cy + er + 4), outline=(225, 180, 60), width=4)
    d.line((cx + ex + er + 2, cy + 4, cx + ex + er + 14, cy + int(60 * k)), fill=(225, 180, 60), width=2)
    my = cy + int(36 * k)
    mw = int(28 * k)
    d.chord((cx - mw - 10, my - 12, cx, my + 10), 180, 360, fill=(90, 55, 30))
    d.chord((cx, my - 12, cx + mw + 10, my + 10), 180, 360, fill=(90, 55, 30))
    d.arc((cx - mw - 22, my - 16, cx - mw + 2, my + 4), 90, 270, fill=(90, 55, 30), width=4)
    d.arc((cx + mw - 2, my - 16, cx + mw + 22, my + 4), 270, 90, fill=(90, 55, 30), width=4)
    if talk:
        d.ellipse((cx - 10 * k - 4, my + 2, cx + 10 * k + 4, my + 4 + 22 * k), fill=(120, 30, 40), outline=OL, width=3)


def draw_jensen(talk, blink, jacket=False, jacket_talk=False, ko=False):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pants = (55, 58, 70)
    d.rounded_rectangle((132, 380, 174, 500), 10, fill=pants, outline=OL, width=4)
    d.rounded_rectangle((186, 380, 228, 500), 10, fill=pants, outline=OL, width=4)
    d.ellipse((112, 484, 178, 515), fill=(30, 30, 30), outline=OL, width=4)
    d.ellipse((182, 484, 248, 515), fill=(30, 30, 30), outline=OL, width=4)
    d.rectangle((160, 188, 200, 225), fill=SKIN, outline=OL, width=4)
    sleeve = (40, 40, 46) if jacket else (30, 30, 34)
    d.rounded_rectangle((76, 228, 120, 372), 20, fill=sleeve, outline=OL, width=4)
    d.rounded_rectangle((240, 228, 284, 372), 20, fill=sleeve, outline=OL, width=4)
    d.ellipse((78, 356, 118, 396), fill=SKIN, outline=OL, width=4)
    d.ellipse((242, 356, 282, 396), fill=SKIN, outline=OL, width=4)
    d.rounded_rectangle((108, 215, 252, 398), 30, fill=sleeve, outline=OL, width=4)
    if jacket:
        _jacket_details(d, 108, 252, 215, 398)
        _jacket_face(d, 180, 330, jacket_talk, blink, small=True)
    # head
    d.ellipse((96, 118, 120, 158), fill=SKIN, outline=OL, width=4)
    d.ellipse((240, 118, 264, 158), fill=SKIN, outline=OL, width=4)
    d.ellipse((106, 55, 254, 205), fill=SKIN, outline=OL, width=4)
    # hair: dark, swept, with silver streaks
    hair = (38, 38, 44)
    d.chord((100, 42, 260, 150), 180, 360, fill=hair, outline=OL, width=4)
    d.polygon([(104, 98), (130, 60), (200, 44), (262, 80), (258, 104), (215, 86), (150, 92)], fill=hair)
    for x in (140, 170, 205, 232):
        d.arc((x - 30, 50, x + 30, 120), 220, 300, fill=(150, 150, 160), width=3)
    # glasses
    d.rounded_rectangle((126, 112, 174, 148), 10, fill=(225, 240, 250), outline=(20, 20, 20), width=4)
    d.rounded_rectangle((186, 112, 234, 148), 10, fill=(225, 240, 250), outline=(20, 20, 20), width=4)
    d.line((174, 126, 186, 126), fill=(20, 20, 20), width=4)
    _eyes(d, (150, 130), (210, 130), blink, ko)
    d.line((130, 104, 168, 100), fill=hair, width=5)
    d.line((192, 100, 230, 104), fill=hair, width=5)
    _mouth(d, 180, 178, talk)
    return im


def draw_jacket(talk, blink, ko=False):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    leather = (38, 38, 44)
    # sleeves (arms)
    d.polygon([(105, 190), (50, 300), (68, 330), (112, 260)], fill=leather, outline=OL)
    d.polygon([(255, 190), (310, 300), (292, 330), (248, 260)], fill=leather, outline=OL)
    d.ellipse((44, 312, 76, 344), fill=(255, 255, 255), outline=OL, width=3)    # white gloves
    d.ellipse((284, 312, 316, 344), fill=(255, 255, 255), outline=OL, width=3)
    d.rounded_rectangle((103, 168, 257, 430), 28, fill=leather, outline=OL, width=4)
    # popped collar
    d.polygon([(118, 175), (138, 140), (172, 172)], fill=(60, 60, 68), outline=OL)
    d.polygon([(242, 175), (222, 140), (188, 172)], fill=(60, 60, 68), outline=OL)
    _jacket_details(d, 103, 257, 168, 430)
    _jacket_face(d, 180, 300, talk, blink and not ko)
    if ko:
        _eyes(d, (158, 300), (202, 300), False, ko=True)
    return im


def draw_chip(talk, blink, hot=False, ko=False):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # legs & arms
    d.line((145, 420, 138, 500), fill=OL, width=7)
    d.line((215, 420, 222, 500), fill=OL, width=7)
    d.ellipse((118, 490, 152, 512), fill=(30, 30, 30))
    d.ellipse((208, 490, 242, 512), fill=(30, 30, 30))
    d.line((95, 330, 55, 370), fill=OL, width=7)
    d.line((265, 330, 305, 290), fill=OL, width=7)
    d.ellipse((42, 358, 68, 384), fill=(255, 255, 255), outline=OL, width=3)
    d.ellipse((292, 276, 318, 302), fill=(255, 255, 255), outline=OL, width=3)
    # gold pins
    for i in range(6):
        y = 268 + i * 26
        d.rectangle((80, y, 95, y + 10), fill=(225, 185, 60), outline=OL)
        d.rectangle((265, y, 280, y + 10), fill=(225, 185, 60), outline=OL)
        x = 112 + i * 26
        d.rectangle((x, 236, x + 10, 250), fill=(225, 185, 60), outline=OL)
    d.rounded_rectangle((95, 250, 265, 420), 14, fill=(52, 56, 62), outline=OL, width=4)
    die = (225, 70, 45) if hot else (118, 185, 0)
    d.rounded_rectangle((115, 270, 245, 400), 10, fill=die, outline=OL, width=3)
    for i in range(4):   # circuit traces
        y = 290 + i * 30
        d.line((122, y, 140, y), fill=(255, 255, 255, 90), width=2)
        d.line((220, y, 238, y), fill=(255, 255, 255, 90), width=2)
    for x in (155, 205):
        d.ellipse((x - 18, 300, x + 18, 340), fill=(255, 255, 255), outline=OL, width=3)
    _eyes(d, (155, 322), (205, 322), blink, ko)
    _mouth(d, 180, 368, talk, w=18)
    if hot:
        for x, y in ((112, 262), (248, 270)):
            d.ellipse((x - 6, y - 10, x + 6, y + 8), fill=(120, 200, 255), outline=OL, width=2)
    return im


def draw_danny(talk, blink, ko=False):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((140, 360, 175, 500), 10, fill=(40, 40, 50), outline=OL, width=4)
    d.rounded_rectangle((185, 360, 220, 500), 10, fill=(40, 40, 50), outline=OL, width=4)
    d.ellipse((122, 486, 178, 515), fill=(25, 25, 25), outline=OL, width=4)
    d.ellipse((182, 486, 238, 515), fill=(25, 25, 25), outline=OL, width=4)
    d.rectangle((162, 160, 198, 195), fill=SKIN, outline=OL, width=4)
    shirt = (250, 250, 250)
    d.rounded_rectangle((86, 195, 126, 330), 18, fill=shirt, outline=OL, width=4)
    d.rounded_rectangle((234, 195, 274, 330), 18, fill=shirt, outline=OL, width=4)
    d.rounded_rectangle((115, 185, 245, 380), 26, fill=shirt, outline=OL, width=4)
    d.rectangle((128, 270, 232, 420), fill=(240, 236, 220), outline=OL, width=4)  # apron
    d.rectangle((150, 300, 210, 340), outline=OL, width=3)
    d.polygon([(165, 190), (180, 200), (165, 212)], fill=(210, 40, 40), outline=OL)   # bow tie
    d.polygon([(195, 190), (180, 200), (195, 212)], fill=(210, 40, 40), outline=OL)
    # coffee pot in left hand
    d.ellipse((60, 300, 140, 380), fill=(150, 90, 40, 230), outline=OL, width=4)
    d.rectangle((80, 286, 120, 304), fill=(30, 30, 30), outline=OL, width=3)
    d.arc((118, 310, 150, 360), 270, 90, fill=(30, 30, 30), width=7)
    # notepad in right hand
    d.rectangle((244, 300, 294, 360), fill=(255, 250, 200), outline=OL, width=3)
    for y in (315, 328, 341):
        d.line((250, y, 288, y), fill=(120, 120, 160), width=2)
    d.ellipse((240, 320, 270, 350), fill=SKIN, outline=OL, width=3)
    # head
    d.ellipse((120, 50, 240, 175), fill=SKIN, outline=OL, width=4)
    # paper diner hat
    d.polygon([(118, 70), (130, 18), (230, 18), (242, 70)], fill=(255, 255, 255), outline=OL)
    d.rectangle((126, 42, 234, 54), fill=(210, 40, 40))
    # sleepy eyes
    if ko:
        _eyes(d, (155, 110), (205, 110), False, ko=True)
    else:
        for cx in (155, 205):
            d.chord((cx - 14, 98, cx + 14, 124), 0, 180, fill=(255, 255, 255), outline=OL, width=3)
            if not blink:
                d.ellipse((cx - 5, 108, cx + 5, 120), fill=(20, 20, 25))
            d.line((cx - 15, 110, cx + 15, 110), fill=OL, width=4)
    d.chord((145, 130, 215, 158), 180, 360, fill=(110, 70, 40))   # mustache
    _mouth(d, 180, 158, talk, w=16, smile=False)
    return im


def draw_wendy(talk, blink, ko=False, chart_up=False):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((148, 430, 168, 500), 8, fill=SKIN, outline=OL, width=3)
    d.rounded_rectangle((192, 430, 212, 500), 8, fill=SKIN, outline=OL, width=3)
    d.polygon([(136, 498), (172, 494), (172, 514), (136, 514)], fill=(210, 30, 50), outline=OL)
    d.polygon([(188, 494), (224, 498), (224, 514), (188, 514)], fill=(210, 30, 50), outline=OL)
    d.rectangle((165, 205, 195, 235), fill=SKIN, outline=OL, width=4)
    suit = (40, 58, 115)
    d.polygon([(122, 380), (238, 380), (250, 440), (110, 440)], fill=suit, outline=OL)
    d.rounded_rectangle((80, 235, 120, 360), 18, fill=suit, outline=OL, width=4)
    d.rounded_rectangle((240, 235, 280, 330), 18, fill=suit, outline=OL, width=4)
    d.rounded_rectangle((110, 225, 250, 390), 28, fill=suit, outline=OL, width=4)
    d.polygon([(160, 228), (200, 228), (180, 275)], fill=(255, 255, 255))
    d.ellipse((84, 345, 118, 379), fill=SKIN, outline=OL, width=3)
    # phone with stock chart
    d.rounded_rectangle((250, 250, 312, 360), 10, fill=(20, 20, 25), outline=OL, width=3)
    d.rectangle((256, 262, 306, 346), fill=(240, 245, 255))
    if chart_up:
        d.line([(260, 335), (272, 320), (282, 326), (302, 272)], fill=(30, 170, 60), width=4)
    else:
        d.line([(260, 275), (272, 290), (282, 284), (302, 338)], fill=(220, 40, 40), width=4)
    d.ellipse((240, 300, 272, 332), fill=SKIN, outline=OL, width=3)
    # head with bun
    hair = (110, 65, 35)
    d.ellipse((150, 22, 210, 78), fill=hair, outline=OL, width=4)
    d.ellipse((114, 70, 246, 212), fill=SKIN, outline=OL, width=4)
    d.chord((110, 62, 250, 170), 180, 360, fill=hair, outline=OL, width=4)
    d.rounded_rectangle((132, 120, 172, 150), 8, outline=(160, 30, 90), width=4)
    d.rounded_rectangle((188, 120, 228, 150), 8, outline=(160, 30, 90), width=4)
    d.line((172, 132, 188, 132), fill=(160, 30, 90), width=4)
    _eyes(d, (152, 136), (208, 136), blink, ko)
    for cx in (152, 208):
        d.line((cx - 12, 118, cx - 16, 112), fill=OL, width=3)
        d.line((cx + 12, 118, cx + 16, 112), fill=OL, width=3)
    d.ellipse((126, 158, 146, 172), fill=(250, 160, 170))
    d.ellipse((214, 158, 234, 172), fill=(250, 160, 170))
    _mouth(d, 180, 182, talk, w=18)
    return im


DRAW = {"jensen": draw_jensen, "jacket": draw_jacket, "chip": draw_chip,
        "danny": draw_danny, "wendy": draw_wendy}


@lru_cache(maxsize=512)
def sprite(name, scale, talk=False, blink=False, **flags):
    im = DRAW[name](talk, blink, **flags)
    if scale != 1.0:
        im = im.resize((int(CW * scale), int(CH * scale)), Image.LANCZOS)
    return im
