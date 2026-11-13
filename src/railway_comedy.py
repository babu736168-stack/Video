"""Render "The Stylish Monkey and the Joker's Terrible Day" to MP4.

Usage:  python3 railway_comedy.py [output.mp4]
"""
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import railway_art as A
from audio import SR, Track
from railway_art import GROUND, OL, ROOF, SD, H, W, font

FPS = 24
TITLE, CARD, STORY, END = 5.0, 3.6, 110.0, 8.0


# ---------------------------------------------------------------- tiny helpers
def clamp(u, a=0.0, b=1.0):
    return max(a, min(b, u))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def lin(a, b, u):
    return a + (b - a) * clamp(u)


def lerp2(p, q, u):
    return (lin(p[0], q[0], u), lin(p[1], q[1], u))


def arc(p, q, u, h):
    u = clamp(u)
    return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u - h * 4 * u * (1 - u))


def inside(t, spans):
    return any(a <= t < b for a, b in spans)


# ---------------------------------------------------------------- script data
NAMES = {"joker": ("JOKER", (235, 175, 0)), "monkey": ("MONKEY", (190, 110, 40)),
         "bird": ("BIRDIE", (60, 145, 235)), "seller": ("EGG SELLER", (40, 140, 90)),
         "bb": ("BODYBUILDER", (210, 30, 40))}

# (start, end, who, kind, text)
BUBBLES = [
    (16.2, 19.6, "joker", "speech", "HA HA HA! Look at this silly monkey!"),
    (18.9, 21.2, "monkey", "thought", "...What kind of creature is THIS?"),
    (26.3, 28.3, "joker", "speech", "EWWW! Is that... bird poop?!"),
    (29.0, 31.3, "joker", "thought", "Just wait! I'll teach you a lesson!"),
    (35.4, 36.9, "joker", "thought", "A stone! Perfect..."),
    (39.0, 41.0, "monkey", "thought", "Hee hee... I have an idea!"),
    (50.2, 51.8, "joker", "thought", "Now I've got you!"),
    (52.8, 54.7, "joker", "speech", "MY MOBILE PHONE!!!"),
    (54.9, 56.5, "seller", "speech", "OUCH! Who threw that?!"),
    (56.6, 58.0, "seller", "speech", "My head?! Take THIS!"),
    (61.4, 63.4, "joker", "speech", "Why me...?"),
    (66.9, 68.0, "bb", "speech", "Hmm?!"),
    (68.2, 70.5, "joker", "speech", "S-sorry! It was an accident! Hehe..."),
    (70.7, 72.0, "bb", "speech", "GRRRR!"),
    (79.8, 81.6, "joker", "speech", "...worst... day... ever."),
    (85.6, 87.0, "bird", "speech", "Tweet tweet!"),
    (87.2, 89.2, "monkey", "speech", "Ooh ooh! High five, partner!"),
]

# (time, word, world point, colour)
WORDS = [
    (24.2, "SPLAT!", (650, 250), (255, 255, 255)),
    (52.3, "CRAAACK!", (900, 230), (255, 70, 60)),
    (54.0, "THWACK!", (1120, 340), (255, 150, 0)),
    (58.65, "SPLAT!", (520, 330), (255, 220, 40), 0.65),
    (59.35, "SPLAT!", (760, 260), (255, 220, 40), 0.65),
    (60.05, "SPLAT!!", (600, 200), (255, 220, 40)),
    (66.3, "THWACK!", (300, 290), (255, 150, 0)),
    (72.5, "GASP!", (640, 420), (255, 255, 255)),
    (75.9, "WHOOSH! BOOM!", (300, 500), (255, 120, 0)),
]

CAPTIONS = [
    (0.3, "SCENE 1  -  THE MONKEY ENJOYS HIS ROYAL LIFE"),
    (9.0, "SCENE 2  -  THE JOKER MAKES A GRAND ENTRANCE"),
    (21.0, "SCENE 3  -  THE BIRD'S UNEXPECTED REVENGE"),
    (31.3, "SCENE 4  -  THE JOKER SEARCHES FOR A STONE"),
    (41.0, "SCENE 5  -  THE MONKEY'S BRILLIANT TRICK"),
    (50.0, "SCENE 6  -  THE MOST EXPENSIVE THROW OF HIS LIFE"),
    (53.9, "SCENE 7  -  THE EGG SELLER GETS A SURPRISE"),
    (63.5, "SCENE 8  -  THE BODYBUILDER'S TERRIBLE TEMPER"),
    (83.0, "SCENE 9  -  THE MONKEY BECOMES THE REAL SUPERSTAR"),
    (93.0, "FINAL SCENE  -  THE JOKER'S SHAMEFUL EXIT"),
]

CAMERA = [  # (t, cx, cy, zoom)
    (0, 330, 225, 2.0), (1.2, 330, 225, 2.0), (5.5, 640, 360, 1.0),
    (23.9, 640, 360, 1.0), (24.3, 620, 330, 1.7), (26.0, 620, 330, 1.7), (27.0, 640, 360, 1.0),
    (40.6, 640, 360, 1.0), (41.4, 600, 470, 1.35), (49.0, 600, 470, 1.35), (49.8, 640, 360, 1.0),
    (52.6, 640, 360, 1.0), (52.9, 640, 380, 1.55), (54.7, 640, 380, 1.55), (55.4, 640, 360, 1.0),
    (79.0, 640, 360, 1.0), (79.4, 250, 470, 1.6), (81.7, 250, 470, 1.6), (82.4, 640, 360, 1.0),
    (93.0, 640, 360, 1.0), (95.0, 620, 420, 1.3), (97.0, 620, 420, 1.3), (103.0, 640, 360, 1.0),
    (104.0, 640, 360, 1.0), (106.0, 330, 225, 2.0), (STORY, 330, 225, 2.0),
]

BITES = [2, 4.6, 7.2, 11, 13.6, 30, 33, 36, 56, 63, 70, 90.5, 92, 105.5]
EGG_RELEASE = [58.2, 58.9, 59.6]
LUGGAGE_BIG, LUGGAGE_BAG = (550, 625), (690, 639)
STONE_SPOT, SUITCASE_TOP = (765, 652), (550, 582)
PILLAR_HIT = (850, 250)
BBX2 = 520


def talking(who, t, f):
    for s, e, w, kind, txt in BUBBLES:
        if w == who and kind == "speech" and s <= t < min(e, s + 0.4 + 0.05 * len(txt)):
            return (f // 3) % 2 == 0
    return False


# ---------------------------------------------------------------- character states
def joker_state(t, f):
    st = dict(face="smile", pose="idle", look=(0, 0), crouch=0, hat="on", glasses="ok")
    x, yoff, mode, angle, center = 620, 0, "stand", 0, None
    st["poop"] = 24.2 <= t < 63.5
    st["egg"] = sum(t >= r + 0.45 for r in EGG_RELEASE)
    if t >= 60.05:
        st["glasses"] = "crooked"
    if t >= 63.5:
        st["hat"] = "held" if t < 65.5 else "off"
    if t >= 79:
        st["dust"], st["glasses"] = True, "broken"
    if t < 9:
        mode = "hidden"
    elif t < 13.5:
        x = lin(-180, 620, (t - 9) / 4.5)
        yoff = -abs(math.sin(t * 7)) * 8
        st.update(pose="carry", swing=math.sin(t * 7) * 12, look=(0, -5))
    elif t < 14.2:
        st.update(pose="carry", crouch=28 * math.sin(math.pi * seg(t, 13.5, 14.2)), look=(0, -5))
    elif t < 15:
        st.update(pose="hips", look=(0, -6))
    elif t < 16:
        st.update(pose="hips", look=(-8, -7))
    elif t < 24.2:
        st.update(pose="point", face="laugh", look=(-8, -7))
        yoff = -abs(math.sin(t * 14)) * 4
    elif t < 25.2:
        st.update(pose="point", face="shock")
    elif t < 26.2:
        st.update(pose="head", face="shock", look=(0, -8))
    elif t < 28.5:
        st.update(pose="look_hand", face="disgust", look=(8, 2))
    elif t < 31.3:
        st.update(pose="fists", face="angry", look=(0, -9))
    elif t < 32.3:
        st.update(pose="pocket", face="angry", look=(0, -9))
    elif t < 33.0:
        st.update(pose="place", face="angry", look=(0, -9))
    elif t < 34.0:
        st.update(face="angry", look=(lin(0, 8, t - 33), -9))
    elif t < 36.8:
        found = t > 35.4
        st.update(face="grin" if found else "angry",
                  look=(8, 9) if found else (8 * math.sin((t - 34) * 4), 9))
    elif t < 37.0:
        st.update(face="focus", look=(8, -9))
    elif t < 50.0:
        c = 40 * ease(seg(t, 37, 39))
        st.update(pose="reach", crouch=c, face="focus" if t < 49.5 else "grin", look=(8, -9),
                  target=lerp2((288, 300 + c), (365, 422), ease(seg(t, 37, 49.5))))
    elif t < 50.6:
        u = seg(t, 50, 50.6)
        st.update(pose="reach", crouch=40 * (1 - u), face="grin", look=(8, -9),
                  target=lerp2((365, 422), (288, 288), u))
    elif t < 51.0:
        st.update(pose="hold", face="grin", look=(8, -9))
    elif t < 51.8:
        st.update(pose="windup", face="grin", look=(8, -9))
    elif t < 55.6:
        st.update(pose="throw", face="grin" if t < 52.6 else ("shock" if t < 53.2 else "horror"),
                  look=(8, -9) if t < 52.6 else ((10, -6) if t < 53.2 else (12, -2)))
    elif t < 58.6:
        st.update(pose="droop", face="sad", look=(10, 0))
    elif t < 60.6:
        st.update(pose="droop", face="wince", look=(10, 0))
    elif t < 61.2:
        st.update(pose="droop", face="shock", look=(10, 0))
    elif t < 63.5:
        st.update(pose="wipe", face="sad")
    elif t < 65.3:
        st.update(pose="hat_hold", face="disgust", shake=8 * math.sin(t * 30) if t > 64.3 else 0)
    elif t < 66.3:
        st.update(pose="throw_left", face="sad", look=(-8, 0))
    elif t < 68.2:
        st.update(face="shock", look=(-10, 0))
    elif t < 72.2:
        st.update(pose="plead", face="nervous", look=(-10, 0))
        x = lin(620, 660, seg(t, 70.6, 72.2))
    elif t < 75.9:
        mode = "rot"
        st.update(pose="flail", face="horror")
        top = (BBX2, GROUND - 440)
        if t < 73.2:
            u = ease(seg(t, 72.2, 73.2))
            center, angle = lerp2((660, GROUND - 215), top, u), 90 * u
        elif t < 75:
            center, angle = (top[0] + 4 * math.sin(t * 20), top[1]), 90
        else:
            u = seg(t, 75, 75.9)
            center, angle = arc(top, (140, 600), u, 120), 90 + 540 * u
    elif t < 79.2:
        mode = "hidden"
    elif t < 93:
        mode, x = "emerge", 150
        yoff = (1 - ease(seg(t, 79.2, 81))) * 260
        st.update(pose="droop", face="broken", look=(0, 4))
    elif t < 96:
        x = lin(150, 545, seg(t, 93, 96))
        yoff = -abs(math.sin(t * 4)) * 3
        st.update(pose="droop", face="sad", look=(0, 8))
    elif t < 97:
        x = 545
        st.update(pose="droop", face="sad", look=(0, 8), crouch=30 * math.sin(math.pi * seg(t, 96, 97)))
    else:
        x = lin(545, 1520, seg(t, 97, 107))
        yoff = -abs(math.sin(t * 4)) * 3
        st.update(pose="slump_carry", swing=math.sin(t * 4) * 5, face="sad", look=(0, 8))
    st["talk"] = talking("joker", t, f)
    return dict(st=st, x=x, yoff=yoff, mode=mode, angle=angle, center=center)


def joker_hand_world(J, t, which):
    L, R = A.joker_hands(J["st"], t)
    hx, hy = (L if which == "L" else R)
    return (J["x"] - A.JAX + hx, GROUND + J["yoff"] - A.JAY + hy)


def joker_head_world(J):
    if J["mode"] == "rot":
        return (J["center"][0], J["center"][1] - 60)
    return (J["x"], GROUND + J["yoff"] - A.JAY + 60 + J["st"].get("crouch", 0))


def monkey_state(t, f):
    bite = any(b <= t < b + 0.35 for b in BITES)
    st = dict(glasses="on", mouth="bite" if bite else "smile")
    if t < 83:
        st["banana"] = 1 - 0.09 * sum(b <= t for b in BITES if b < 83)
    elif t >= 89:
        st["banana"] = 1 - 0.25 * sum(b <= t for b in BITES if b >= 89)
    else:
        st["banana"] = None
    if inside(t, [(17, 21.2), (24.6, 28)]):
        st["glasses"] = "down"
    if not bite and inside(t, [(24.6, 29), (38.5, 49.4), (49.4, 52.6), (53, 56), (60, 63.5), (76, 83),
                               (85, 87.2), (93, 99), (101.5, 104)]):
        st["mouth"] = "grin"
    if talking("monkey", t, f):
        st["mouth"] = "talk"
    pose, x, y = "lie", 360, ROOF
    walk = [(42, 43.5, 430, 740), (44, 45.3, 740, 575), (46.3, 47.3, 575, 740), (47.8, 48.8, 740, 430)]
    if 41 <= t < 49.4:
        pose, st["banana"] = "stand", None
        st["face_dir"] = 1
        if t < 42:
            x, y = arc((330, ROOF), (430, GROUND), seg(t, 41, 42), 60)
        elif t >= 48.8:
            x, y = arc((430, GROUND), (330, ROOF), seg(t, 48.8, 49.4), 60)
            st["face_dir"] = -1
        else:
            y = GROUND
            x = {43.5: 740, 45.3: 575, 47.3: 740}.get(None, 740)
            for a, b, x0, x1 in walk:
                if a <= t < b:
                    x, st["moving"], st["face_dir"] = lin(x0, x1, seg(t, a, b)), True, 1 if x1 > x0 else -1
                    break
            else:
                x = 740 if (43.5 <= t < 44 or 47.3 <= t < 47.8) else 575
                st["face_dir"] = 1 if x == 740 else -1
        if 43.8 <= t < 45.6:
            st["item"] = "stone"
        elif 45.9 <= t < 47.5:
            st["item"] = "phone"
    elif 83 <= t < 102:
        pose = "sit"
        st["arm"] = ("glasses" if 84 <= t < 85.2 else "five" if 87.0 <= t < 88.0 else
                     "trophy" if 99 <= t < 101.5 else "bite" if bite else "rest")
    return dict(st=st, pose=pose, x=x, y=y)


def bird_state(t):
    if t < 21:
        return (90, 40 - abs(math.sin(t * 2.5)) * 3 * (int(t) % 3 == 0), False, 1)
    if t < 23:
        x, y = arc((90, 40), (620, 40), seg(t, 21, 23), 70)
        return (x, y, True, 1)
    if t < 33.2:
        return (620, 40, False, 1)
    if t < 34:
        x, y = arc((620, 40), (840, 40), seg(t, 33.2, 34), 40)
        return (x, y, True, 1)
    if t < 52.0:
        return (840, 40, False, -1)
    if t < 53.5:
        x, y = arc((840, 40), (1380, -60), seg(t, 52.0, 53.5), 80)
        return (x, y, True, 1)
    if t < 84:
        return None
    if t < 86.5:
        x, y = arc((1380, -60), (285, ROOF - 12), seg(t, 84, 86.5), -120)
        return (x, y, True, -1)
    return (285, ROOF - 12, False, 1)


def bb_state(t, f):
    st, x = dict(pose="idle", face="proud", look=0), 370
    if t < 66.3:
        st["pose"] = "flex" if int(t / 2.5) % 2 == 0 else "idle"
    elif t < 67.5:
        st.update(face="calm", look=-6)
    elif t < 70.6:
        st.update(pose="fists", face="angry", look=8)
    elif t < 72.2:
        x = lin(370, BBX2, seg(t, 70.6, 72.2))
        st.update(pose="fists", face="angry", look=8)
    elif t < 75:
        x = BBX2
        st.update(pose="lift", face="angry")
    elif t < 75.7:
        x = BBX2
        st.update(pose="throw", face="angry")
    else:
        x = BBX2
        st.update(pose="cross", face="proud" if t < 93 else "smile")
    st["talk"] = talking("bb", t, f)
    return x, st


def seller_state(t, f):
    st = dict(pose="arrange", face="calm", look=0)
    if 54 <= t < 55:
        st.update(pose="rub", face="ouch")
    elif 55 <= t < 56.5:
        st.update(pose="rub", face="confused", look=-6)
    elif 56.5 <= t < 63:
        st.update(pose="fists", face="angry", look=-10)
        for r in EGG_RELEASE:
            if r - 0.4 <= t < r:
                st.update(pose="windup", holding_egg=True)
            elif r <= t < r + 0.3:
                st["pose"] = "release"
    elif 63 <= t < 79.6:
        st.update(look=-6)
    elif t >= 79.6:
        st.update(pose="laugh", face="laugh", shake=5 * math.sin(t * 8) if t > 93 else 0)
    st["talk"] = talking("seller", t, f)
    return st


def passenger_mood(t, i, p):
    if t < 9:
        return "dance" if p.get("dance") else ("walk" if p.get("walk") and t < 7 else "idle")
    if inside(t, [(52.4, 53.6), (72.4, 76.5)]):
        return "gasp"
    if inside(t, [(26.5, 29.5), (60.2, 63.5), (79.6, STORY)]):
        return "point" if (t > 93 and i % 3 == 0) else "laugh"
    return "idle"


# ---------------------------------------------------------------- objects
FRAGS = [(-260, -300), (220, -380), (320, -120), (-120, -80), (90, -460), (-340, -180), (170, 60)]


def draw_objects(sd, t, J):
    # luggage on the platform
    if 14.2 <= t < 96.8:
        A.draw_suitcase(sd, *LUGGAGE_BIG)
        A.draw_bag(sd, *LUGGAGE_BAG)
    # stone
    if t < 43.8:
        A.draw_stone(sd, *STONE_SPOT)
    elif 45.6 <= t < 96.8:
        A.draw_stone(sd, SUITCASE_TOP[0], SUITCASE_TOP[1] - 2)
    elif t >= 96.8:
        A.draw_stone(sd, 520, 655)
    # phone
    if 31.8 <= t < 33.0:
        A.draw_phone(sd, *joker_hand_world(J, t, "L"))
    elif 33.0 <= t < 45.9:
        A.draw_phone(sd, SUITCASE_TOP[0], SUITCASE_TOP[1] - 2, math.pi / 2)
    elif 47.5 <= t < 49.5:
        A.draw_phone(sd, STONE_SPOT[0], STONE_SPOT[1], math.pi / 2)
    elif 49.5 <= t < 51.8:
        A.draw_phone(sd, *joker_hand_world(J, t, "R"))
    elif 51.8 <= t < 52.3:
        rel = (J["x"] - A.JAX + 352, GROUND - A.JAY + 108)
        x, y = arc(rel, PILLAR_HIT, seg(t, 51.8, 52.3), 30)
        A.draw_phone(sd, x, y, t * 25)
    elif t >= 52.3:
        dt = t - 52.3
        for k, (vx, vy) in enumerate(FRAGS):
            x = PILLAR_HIT[0] + vx * min(dt, 1.4)
            y = min(GROUND - 6, PILLAR_HIT[1] + vy * dt + 700 * dt * dt)
            a = dt * 9 + k if y < GROUND - 6 else k
            pts = [(x + 8 * math.cos(a + j * 2.1), y + 8 * math.sin(a + j * 2.1)) for j in range(3)]
            sd.poly(pts, fill=(80, 170, 255) if k % 2 else (20, 20, 25), outline=OL, width=1)
        # the special piece that hits the egg seller
        if t < 54.0:
            x, y = arc(PILLAR_HIT, (1065, 372), seg(t, 52.3, 54.0), 200)
        else:
            x, y = arc((1065, 372), (1030, 526), seg(t, 54.0, 54.6), 30)
        A.draw_phone(sd, x, y, t * 12 if t < 54.6 else 1.2)
    # poop
    if 23.6 <= t < 24.2:
        u = seg(t, 23.6, 24.2) ** 2
        y = lin(52, 280, u)
        sd.ellipse((614, y - 7, 626, y + 7), fill=(250, 250, 240), outline=(150, 150, 130), width=2)
    # eggs
    for r in EGG_RELEASE:
        if r <= t < r + 0.45:
            u = seg(t, r, r + 0.45)
            x, y = arc((1003, 430), (640, 385), u, 60)
            sd.ellipse((x - 8, y - 10, x + 8, y + 10), fill=(250, 245, 232), outline=OL, width=2)
    # hat
    if 65.5 <= t < 66.3:
        x, y = arc((470, 405), (380, 330), seg(t, 65.5, 66.3), 60)
        A.draw_hat(sd, x, y, True, False)
    elif t >= 66.3 and not (96.8 <= t):
        x, y = arc((380, 330), (305, 652), seg(t, 66.3, 66.9), 20)
        A.draw_hat(sd, x, y, True, False)


def dust_cloud(img, t):
    if not (75.9 <= t < 80.5):
        return
    u = (t - 75.9) / 4.6
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = random.Random(12)
    alpha = int(230 * (1 - u) ** 1.2)
    for _ in range(26):
        a, dist = rng.random() * math.pi, rng.uniform(10, 170)
        cx = 140 + math.cos(a) * dist * (0.6 + u)
        cy = 600 - math.sin(a) * dist * (0.6 + u) * 0.9
        r = rng.uniform(30, 60) * (0.7 + u)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(185, 160, 125, alpha))
    img.paste(ov, (0, 0), ov)


def mark(sd, x, y, s, color=(255, 230, 40)):
    sd.text((x, y), s, 44, color, stroke=5)


def lightbulb(sd, x, y, t):
    for k in range(8):
        a = k * math.pi / 4 + t
        sd.line([(x + 30 * math.cos(a), y + 30 * math.sin(a)), (x + 42 * math.cos(a), y + 42 * math.sin(a))],
                (255, 220, 40), 4)
    sd.circle(x, y, 20, fill=(255, 240, 120), outline=OL, width=3)
    sd.rect((x - 9, y + 18, x + 9, y + 30), fill=(160, 160, 170), outline=OL, width=2)


# ---------------------------------------------------------------- world render
def render_world(t, f):
    img = A.background().copy()
    d = ImageDraw.Draw(img)
    sd = SD(d)
    for i, p in enumerate(A.PASSENGERS):
        x = p["x"] - p.get("walk", 0) * max(0, 7 - t) * 80
        A.draw_person(sd, x, A.BACK, p, t, passenger_mood(t, i, p), i * 1.7)
    bbx, bst = bb_state(t, f)
    A.draw_bb(sd, bbx, t, bst)
    A.draw_seller(sd, t, seller_state(t, f))
    A.draw_stall(sd)
    J = joker_state(t, f)
    draw_objects(sd, t, J)
    # joker
    if J["mode"] in ("stand", "emerge"):
        spr = A.joker_sprite(t, J["st"])
        px, py = int(J["x"] - A.JAX), int(GROUND + J["yoff"] - A.JAY)
        if J["mode"] == "emerge":
            keep = int(GROUND - 10 - py)
            if keep > 0:
                spr = spr.crop((0, 0, A.JW, min(A.JH, keep)))
                img.paste(spr, (px, py), spr)
        else:
            img.paste(spr, (px, py), spr)
    elif J["mode"] == "rot":
        spr = A.joker_sprite(t, J["st"]).rotate(J["angle"], resample=Image.BICUBIC, expand=True)
        cx, cy = J["center"]
        img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)
    # monkey
    M = monkey_state(t, f)
    A.draw_monkey(sd, M["x"], M["y"], M["pose"], t, M["st"])
    # bird
    B = bird_state(t)
    if B:
        A.draw_bird(sd, B[0], B[1], t, flying=B[2], facing=B[3], wing_up=87.2 <= t < 87.8)
        if inside(t, [(85.6, 88.5), (104, STORY)]):
            for k in range(2):
                ph = (t * 1.2 + k * 0.5) % 1
                d.text((B[0] + 10 + 30 * ph, B[1] - 30 - 40 * ph), "♪",
                       font=A.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26),
                       fill=(40, 90, 200))
    A.draw_heap(sd)
    dust_cloud(img, t)
    # marks
    jh = joker_head_world(J)
    if 15 <= t < 16:
        mark(sd, jh[0] + 40, jh[1] - 70, "?")
    if 35.4 <= t < 36.2:
        mark(sd, jh[0] + 40, jh[1] - 70, "!")
    if 55 <= t < 56.5:
        mark(sd, A.SELLER_X + 40, 335, "?")
    if 67.4 <= t < 68.2:
        mark(sd, bbx + 40, GROUND - 390, "!", (255, 60, 60))
    if 38.8 <= t < 41:
        lightbulb(sd, 302, ROOF - 125, t)
    return img, J, M, B, bbx


def anchor(who, t, J, M, B, bbx):
    if who == "joker":
        return joker_head_world(J)
    if who == "monkey":
        return (M["x"] - 58, M["y"] - 80) if M["pose"] == "lie" else (M["x"], M["y"] - 140)
    if who == "bird":
        return (B[0], B[1] - 16) if B else (300, 200)
    if who == "seller":
        return (A.SELLER_X, 372)
    return (bbx, GROUND - 360)


# ---------------------------------------------------------------- camera & overlays
def camera(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAMERA, CAMERA[1:]):
        if t0 <= t <= t1:
            u = ease(seg(t, t0, t1)) if t1 > t0 else 1
            return lin(x0, x1, u), lin(y0, y1, u), lin(z0, z1, u)
    return 640, 360, 1.0


def apply_camera(img, t):
    cx, cy, z = camera(t)
    vw, vh = W / z, H / z
    x0 = clamp(cx - vw / 2, 0, W - vw)
    y0 = clamp(cy - vh / 2, 0, H - vh)
    if z > 1.001:
        img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))
    return img, (lambda p: ((p[0] - x0) * z, (p[1] - y0) * z))


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def bubble(img, who, kind, text, hx, hy):
    d = ImageDraw.Draw(img)
    f = font("Inter-Bold.otf" if kind == "speech" else "Inter-BoldItalic.otf", 30)
    lines = wrap(text, f, 470)
    lh = 38
    tw = max(f.getlength(l) for l in lines)
    bw, bh = tw + 50, len(lines) * lh + 38
    bx = clamp(hx - bw / 2, 16, W - 16 - bw)
    by = hy - 50 - bh
    if by < 24:
        by = 24
    hy = max(hy, by + bh + 20)
    base = clamp(hx, bx + 40, bx + bw - 40)
    fill = (255, 255, 255) if kind == "speech" else (240, 246, 255)
    d.rounded_rectangle((bx + 6, by + 6, bx + bw + 6, by + bh + 6), 26, fill=(0, 0, 0))
    if kind == "speech":
        tip = (hx, hy - 6)
        d.polygon([(base - 18, by + bh - 6), (base + 18, by + bh - 6), tip], fill=fill)
        d.line([(base - 18, by + bh - 6), tip, (base + 18, by + bh - 6)], fill=OL, width=4)
    else:
        for k, r in enumerate((11, 8, 5)):
            u = (k + 1) / 4
            px, py = base + (hx - base) * u, by + bh + (hy - by - bh) * u
            d.ellipse((px - r, py - r, px + r, py + r), fill=fill, outline=OL, width=3)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 26, fill=fill, outline=OL, width=4)
    if kind == "speech":
        d.polygon([(base - 15, by + bh - 8), (base + 15, by + bh - 8), (base, by + bh + 4)], fill=fill)
    for i, l in enumerate(lines):
        d.text((bx + 25, by + 20 + i * lh), l, font=f, fill=(20, 20, 25))
    name, color = NAMES[who]
    tag = name if kind == "speech" else name + " (thinking)"
    nf = font("Inter-Black.otf", 18)
    nw = nf.getlength(tag) + 24
    d.rounded_rectangle((bx + 18, by - 16, bx + 18 + nw, by + 14), 10, fill=color, outline=OL, width=3)
    d.text((bx + 30, by - 11), tag, font=nf, fill=(255, 255, 255), stroke_width=2, stroke_fill=OL)


def overlays(img, t, to_screen, J, M, B, bbx):
    d = ImageDraw.Draw(img)
    for t0, word, p, color, *rest in WORDS:
        if t0 <= t < t0 + (rest[0] if rest else 1.1):
            u = seg(t, t0, t0 + 0.15)
            size = int(lin(30, 86, u) + 6 * math.sin(t * 30) * (1 - seg(t, t0, t0 + 0.6)))
            x, y = to_screen(p)
            half = font("Inter-Black.otf", size).getlength(word) / 2 + 12
            x, y = clamp(x, half, W - half), clamp(y, 70, H - 120)
            d.text((x, y), word, font=font("Inter-Black.otf", size), fill=color, anchor="mm",
                   stroke_width=7, stroke_fill=OL)
    for s, e, who, kind, txt in BUBBLES:
        if s <= t < e:
            hx, hy = to_screen(anchor(who, t, J, M, B, bbx))
            bubble(img, who, kind, txt, clamp(hx, 60, W - 60), clamp(hy, 120, H - 40))
    for t0, cap in CAPTIONS:
        if t0 <= t < t0 + 3.2:
            a = min(seg(t, t0, t0 + 0.3), 1 - seg(t, t0 + 2.8, t0 + 3.2))
            f = font("Inter-Black.otf", 26)
            w = f.getlength(cap) + 44
            y = H - 58 + (1 - a) * 70
            d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 44), 22, fill=(20, 20, 30), outline=(255, 205, 40), width=3)
            d.text((W / 2, y + 22), cap, font=f, fill=(255, 225, 90), anchor="mm")
    if t > 106.4:
        a = seg(t, 106.4, 107.0)
        d.text((W / 2, 120 - (1 - a) * 80), "THE END", font=font("Inter-Black.otf", 110),
               fill=(255, 225, 60), anchor="mm", stroke_width=8, stroke_fill=OL)


def render_story(t, f):
    world, J, M, B, bbx = render_world(t, f)
    img, to_screen = apply_camera(world, t)
    overlays(img, t, to_screen, J, M, B, bbx)
    return img


# ---------------------------------------------------------------- cards
def gradient(top, bottom):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        u = y / H
        d.line((0, y, W, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * u) for i in range(3)))
    return im


_title_bg = None


def render_title(t, f):
    global _title_bg
    if _title_bg is None:
        _title_bg = Image.blend(A.background().filter(ImageFilter.GaussianBlur(6)), Image.new("RGB", (W, H), (15, 10, 30)), 0.55)
    img = _title_bg.copy()
    d = ImageDraw.Draw(img)
    z = 0.6 + 0.4 * ease(t / 0.8)
    d.text((W / 2, 150), "THE STYLISH MONKEY", font=font("Inter-Black.otf", int(92 * z)), fill=(255, 225, 60),
           anchor="mm", stroke_width=7, stroke_fill=OL)
    d.text((W / 2, 260), "AND THE JOKER'S TERRIBLE DAY", font=font("Inter-Black.otf", int(64 * z)),
           fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(220, 40, 90))
    if t > 1.0:
        d.text((W / 2, 345), "A cinematic comedy at a busy Indian railway station", font=font("Inter-SemiBold.otf", 30),
               fill=(230, 230, 240), anchor="mm")
    sd = SD(d, 2.0, 0, 0)
    A.draw_monkey(SD(d, 2.0, 640 - 0 * 2, 690), 0, 0, "sit", t,
                  dict(banana=1.0, arm="rest", mouth="grin"))
    A.draw_bird(SD(d, 2.6, 0, 0), 330, 255, t, flying=True, facing=1)
    return img


CAST = [
    ("monkey", "THE STYLISH MONKEY", "King of the Train Roof",
     "Style: colourful shirt, red shorts, black sunglasses.",
     "Talent: genius-level pranks and world-class banana eating."),
    ("joker", "THE JOKER", "Self-Declared Celebrity",
     "Style: feathered yellow hat, giant red bow tie, striped trousers.",
     "Weakness: mocks others before checking who their friends are."),
    ("bird", "BIRDIE", "The Monkey's Feathered Best Friend",
     "Talent: precision air strikes from the platform roof.",
     "Motto: mock my friend? SPLAT."),
    ("seller", "THE EGG SELLER", "Master of the Egg Stall",
     "Talent: arranges eggs perfectly. Throws them even better.",
     "Weakness: a very short temper about his head."),
    ("bb", "THE BODYBUILDER", "Strongest Man on Platform 1",
     "Talent: lifts joker-sized objects with zero effort.",
     "Weakness: really, really hates flying hats."),
]


def draw_cast_member(d, who, t, f):
    bob = math.sin(t * 3) * 4
    if who == "monkey":
        A.draw_monkey(SD(d, 2.8, 330, 660 + bob), 0, 0, "sit", t,
                      dict(banana=1.0, mouth="talk" if (f // 3) % 2 and 0.6 < t < 2.4 else "grin"))
    elif who == "joker":
        k = 1.4
        A.draw_joker(SD(d, k, 330 - A.JAX * k, 690 - A.JAY * k + bob), t,
                     dict(pose="hips" if t < 1.8 else "point", face="smile" if t < 1.8 else "laugh", look=(0, -5)))
    elif who == "bird":
        A.draw_bird(SD(d, 6.0, 330, 430 + bob), 0, 0, t, flying=t > 1.5, facing=1)
    elif who == "seller":
        k = 1.55
        sd = SD(d, k, 290 - A.SELLER_X * k, 700 - GROUND * k)
        A.draw_seller(sd, t, dict(pose="windup" if t > 1.8 else "arrange", face="angry" if t > 1.8 else "calm",
                                  holding_egg=t > 1.8))
        A.draw_stall(sd)
    else:
        k = 1.45
        A.draw_bb(SD(d, k, 330, 700 - GROUND * k + bob), 0, t, dict(pose="flex" if int(t * 1.2) % 2 else "idle"))


def make_card(i):
    who, name, role, a, b = CAST[i]
    color = NAMES[who][1]
    bg = gradient(tuple(int(c * 0.45) for c in color), (12, 10, 18))

    def render(t, f):
        img = bg.copy()
        d = ImageDraw.Draw(img)
        d.text((W / 2, 40), f"MEET THE CAST   {i + 1} / 5", font=font("Inter-Black.otf", 26),
               fill=(220, 220, 220), anchor="mm")
        draw_cast_member(d, who, t, f)
        tx = lin(W + 60, 620, ease((t - 0.1) / 0.5))
        d.text((tx, 200), name, font=font("Inter-Black.otf", 54), fill=(255, 255, 255), stroke_width=3, stroke_fill=OL)
        d.text((tx, 275), role, font=font("Inter-Bold.otf", 34), fill=tuple(min(255, c + 60) for c in color))
        y = 360
        for txt in (a, b):
            for l in wrap(txt, font("Inter-SemiBold.otf", 29), 600):
                d.text((tx, y), l, font=font("Inter-SemiBold.otf", 29), fill=(235, 235, 235))
                y += 40
            y += 22
        return img
    return render


def render_end(t, f):
    img = gradient((40, 20, 60), (10, 8, 16))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 110), "THE END", font=font("Inter-Black.otf", 110), fill=(255, 225, 60), anchor="mm",
           stroke_width=7, stroke_fill=OL)
    d.text((W / 2, 225), "COMEDY MORAL", font=font("Inter-Bold.otf", 26), fill=(190, 190, 200), anchor="mm")
    for k, l in enumerate(("Never underestimate a clever monkey...",
                           "and never mock someone before checking who their friends are!")):
        d.text((W / 2, 285 + k * 52), l, font=font("Inter-BoldItalic.otf", 38), fill=(255, 255, 255), anchor="mm")
    names = "  -  ".join(n for _, n, *_ in CAST)
    d.text((W / 2, 420), "Starring: " + names, font=font("Inter-SemiBold.otf", 20), fill=(200, 200, 210), anchor="mm")
    A.draw_monkey(SD(d, 1.9, 560, 690), 0, 0, "sit", t,
                  dict(banana=1.0, arm="trophy" if int(t) % 2 == 0 else "rest", mouth="grin"))
    A.draw_bird(SD(d, 2.6, 0, 0), 290, 245 + math.sin(t * 3) * 3, t, flying=False, facing=-1)
    k = 0.75
    A.draw_joker(SD(d, k, 900 - A.JAX * k, 700 - A.JAY * k), t,
                 dict(pose="droop", face="broken", hat="off", dust=True, glasses="broken", egg=3))
    return img


# ---------------------------------------------------------------- audio
class RailTrack(Track):
    def _noise(self, n, smooth=1, seed=0):
        x = np.random.default_rng(seed).standard_normal(n)
        return np.convolve(x, np.ones(smooth) / smooth, mode="same") if smooth > 1 else x

    def pluck(self, t, f, dur=0.45, gain=0.05):
        tt = np.arange(int(dur * SR)) / SR
        ff = f * (1 + 0.06 * np.exp(-tt / 0.025))
        ph = np.cumsum(ff) / SR
        sig = 2 * (ph % 1) - 1
        sig = np.convolve(sig, np.ones(6) / 6, mode="same") + 0.3 * np.sin(2 * np.pi * 2 * ph)
        self.add(t, sig * np.exp(-tt / (dur * 0.35)), gain)

    def dha(self, t, g=1.0):
        s, tt = self._tone(150, 70, 0.3)
        self.add(t, s * np.exp(-tt / 0.12), 0.22 * g)
        self.tin(t, 0.6 * g)

    def tin(self, t, g=1.0):
        tt = np.arange(int(0.12 * SR)) / SR
        s = np.sin(2 * np.pi * 680 * tt) + 0.4 * np.sin(2 * np.pi * 1360 * tt)
        self.add(t, s * np.exp(-tt / 0.03), 0.10 * g)

    def imusic(self, t0, t1, bpm, style):
        beat = 60 / bpm
        rng = random.Random(int(t0 * 7) + 3)
        scale = {"happy": [0, 2, 4, 5, 7, 9, 10, 12, 14], "chaos": [0, 2, 4, 5, 7, 9, 10, 12, 14],
                 "sneak": [0, 1, 4, 5, 7, 8, 11, 12], "sad": [0, 2, 3, 5, 7, 8, 10, 12]}[style]
        base = 146.8
        dur = t1 - t0
        tt = np.arange(int(dur * SR)) / SR
        drone = (2 * ((base / 2 * tt) % 1) - 1) + 0.6 * (2 * ((base * 0.75 * tt) % 1) - 1)
        drone = np.convolve(drone, np.ones(60) / 60, mode="same")
        fade = np.minimum(1, np.minimum(tt / 0.5, (dur - tt) / 0.5))
        self.add(t0, drone * fade * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * tt)), 0.05)
        pat = {"happy": "D..dT.D.D..dT.d.", "chaos": "D.dTD.dTD.dTDdTT", "sneak": "D.......T.......",
               "sad": "D.......T...T..."}[style]
        eighth = beat / 2
        idx = 3
        for k in range(int(dur / eighth)):
            t = t0 + k * eighth
            ch = pat[k % 16]
            if ch == "D":
                self.dha(t)
            elif ch == "d":
                self.dha(t, 0.5)
            elif ch == "T":
                self.tin(t)
            p = {"happy": 0.65, "chaos": 0.85, "sneak": 0.45, "sad": 0.4}[style]
            if style == "sneak" and k % 2:
                continue
            if rng.random() < p:
                idx = max(0, min(len(scale) - 1, idx + rng.choice([-2, -1, -1, 1, 1, 2])))
                octave = 1 if style in ("sneak", "sad") else 2
                self.pluck(t, base * octave * 2 ** (scale[idx] / 12) / (2 if style == "sneak" else 1),
                           0.25 if style == "sneak" else 0.5)

    def speak(self, t, who, dur):
        if who == "monkey":
            for k in range(int(dur * 4)):
                s, tt = self._tone(380, 760, 0.18)
                self.add(t + k * 0.25, s * np.sin(np.pi * tt / 0.18), 0.12)
            return
        if who == "bird":
            for k in range(int(dur * 6)):
                s, tt = self._tone(2600, 4200, 0.08)
                self.add(t + k * 0.16, s * np.sin(np.pi * tt / 0.08), 0.07)
            return
        base, rate = {"joker": (240, 13), "seller": (165, 10), "bb": (85, 7)}[who]
        rng = random.Random(int(t * 100))
        for k in range(max(1, int(dur * rate))):
            f = base * 2 ** (rng.choice([0, 2, 3, 5, 7, 9, 12]) / 12)
            L = 0.75 / rate
            tt = np.arange(int(L * SR)) / SR
            ph = 2 * np.pi * np.cumsum(f * (1 + 0.15 * tt / L)) / SR
            sig = 0.6 * np.sin(ph) + 0.25 * np.sign(np.sin(ph)) + 0.15 * np.sin(2 * ph)
            self.add(t + k / rate, sig * np.minimum(1, tt / 0.006) * np.exp(-tt / (L * 0.45)), 0.2)

    def laugh(self, t, dur, n=8, gain=0.5, seed=1):
        rng = np.random.default_rng(seed)
        for v in range(n):
            f0, tt0 = rng.uniform(170, 340), t + rng.uniform(0, 0.4)
            while tt0 < t + dur:
                L = rng.uniform(0.09, 0.14)
                ts = np.arange(int(L * SR)) / SR
                ph = np.cumsum(f0 * (1 - 0.15 * ts / L)) / SR
                sig = np.convolve(2 * (ph % 1) - 1, np.ones(7) / 7, mode="same") + 0.15 * rng.standard_normal(len(ts))
                self.add(tt0, sig * np.sin(np.pi * ts / L) ** 1.5, gain / n)
                tt0 += rng.uniform(0.17, 0.27)
                f0 *= 0.99

    def joker_laugh(self, t, dur):
        for k in range(int(dur * 4.5)):
            L = 0.15
            ts = np.arange(int(L * SR)) / SR
            ph = np.cumsum(300 * (1 - 0.25 * ts / L) * (1 - 0.02 * k)) / SR
            sig = np.convolve(2 * (ph % 1) - 1, np.ones(5) / 5, mode="same")
            self.add(t + k * 0.22, sig * np.sin(np.pi * ts / L), 0.3)

    def _splat(self, t):
        n = self._noise(int(0.3 * SR), 30, 7)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt / 0.06), 2.2)
        s, tt = self._tone(140, 50, 0.25)
        self.add(t, s * np.exp(-tt / 0.07), 0.5)

    def _thwack(self, t):
        n = self._noise(int(0.15 * SR), 3, 8)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt / 0.02), 0.6)
        s, tt = self._tone(220, 80, 0.2)
        self.add(t, s * np.exp(-tt / 0.05), 0.6)

    def _crack(self, t):
        n = np.diff(self._noise(int(0.6 * SR), 1, 9), prepend=0)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt / 0.08), 0.35)
        rng = random.Random(4)
        for k in range(14):
            s, ts = self._tone(rng.uniform(3000, 7000), rng.uniform(3000, 7000), 0.12)
            self.add(t + rng.uniform(0, 0.7), s * np.exp(-ts / 0.03), 0.12)

    def _boom(self, t):
        s, tt = self._tone(80, 30, 1.6)
        self.add(t, s * np.exp(-tt / 0.4), 0.8)
        n = self._noise(int(1.6 * SR), 80, 10)
        self.add(t, n * np.exp(-tt[:len(n)] / 0.5), 3.0)

    def _gasp(self, t):
        n = self._noise(int(0.6 * SR), 4, 11)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.sin(np.pi * tt / 0.6) ** 2, 0.25)

    def _slideup(self, t):
        s, tt = self._tone(250, 1100, 0.9, vib=0.04)
        self.add(t, s * np.sin(np.pi * tt / 0.9), 0.2)

    def _tiptoe(self, t):
        s, tt = self._tone(900, 900, 0.07)
        self.add(t, s * np.exp(-tt / 0.02), 0.12)

    def _horn(self, t):
        tt = np.arange(int(2.2 * SR)) / SR
        sig = sum(2 * ((f * tt) % 1) - 1 for f in (311, 370, 466))
        sig = np.convolve(sig, np.ones(12) / 12, mode="same")
        env = np.minimum(1, tt / 0.1) * np.minimum(1, (2.2 - tt) / 0.4)
        self.add(t, sig * env, 0.06)

    def _chime(self, t):
        for k, f in enumerate((659, 523, 784, 659)):
            tt = np.arange(int(1.2 * SR)) / SR
            self.add(t + k * 0.35, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 3), 0.12)

    def _trombone(self, t):
        for k, (f, d) in enumerate(((293, .45), (277, .45), (261, .45), (247, 1.4))):
            s, tt = self._tone(f, f * (0.97 if d > 1 else 1), d, wav="saw", vib=0.02 if d > 1 else 0)
            s = np.convolve(s, np.ones(8) / 8, mode="same")
            self.add(t + k * 0.5, s * np.minimum(1, tt / 0.05) * np.minimum(1, (d - tt) / 0.1), 0.15)

    def _murmur(self, t0, t1):
        n = self._noise(int((t1 - t0) * SR), 200, 13)
        self.add(t0, n * 6, 0.05)


def build_audio(path, story0, total):
    tr = RailTrack(total)
    tr.imusic(0, story0, 112, "happy")
    tr._horn(0.3)
    tr._tada(0.6)
    for i in range(5):
        tr._whoosh(TITLE + i * CARD)
    S = story0
    tr._murmur(S, S + STORY)
    tr._chime(S + 2.0)
    for a, b, bpm, style in ((0, 31.3, 112, "happy"), (31.3, 50, 92, "sneak"), (50, 83, 128, "chaos"),
                             (83, 93, 112, "happy"), (93, 104, 80, "sad"), (104, STORY, 112, "happy")):
        tr.imusic(S + a, S + b, bpm, style)
    for s, e, who, kind, txt in BUBBLES:
        if kind != "speech":
            continue
        dur = min(e - s, 0.4 + 0.05 * len(txt))
        if txt.startswith("HA HA"):
            tr.joker_laugh(S + s, 2.4)
        else:
            tr.speak(S + s, who, dur)
    events = [(23.6, "slideup"), (24.2, "splat"), (52.3, "crack"), (54.0, "thwack"), (66.3, "thwack"),
              (72.2, "slideup"), (72.5, "gasp"), (75.0, "whoosh"), (75.9, "boom"), (41.0, "boing"), (48.8, "boing"),
              (93.0, "trombone"), (38.8, "ding"), (35.4, "ding"), (106.4, "tada"), (51.8, "whoosh"), (65.5, "whoosh")]
    events += [(r + 0.45, "splat") for r in EGG_RELEASE]
    events += [(42 + k * 0.18, "tiptoe") for k in range(int(6.8 / 0.18))]
    for t, name in events:
        tr.sfx(S + t, name)
    for t, d in ((26.5, 3), (60.2, 3.5), (79.8, 3), (84, 5), (93.6, 10)):
        tr.laugh(S + t, d, n=10, gain=0.7, seed=int(t))
    tr.music(S + STORY, total, 100, [0, 5, 7, 0], "keynote")
    tr.write(path)


# ---------------------------------------------------------------- main
def timeline():
    segs = [(TITLE, render_title)] + [(CARD, make_card(i)) for i in range(5)] + [(STORY, render_story), (END, render_end)]
    out, t = [], 0.0
    for dur, fn in segs:
        out.append((t, dur, fn))
        t += dur
    return out, t


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output",
                                                              "stylish_monkey_and_the_joker.mp4")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    segs, total = timeline()
    story0 = segs[-2][0]
    wav = out + ".wav"
    build_audio(wav, story0, total)
    n = int(total * FPS)
    print(f"Rendering {n} frames ({total:.1f}s)...", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264",
                           "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                           "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    black = Image.new("RGB", (W, H))
    si = 0
    for fr in range(n):
        t = fr / FPS
        while si < len(segs) - 1 and t >= segs[si][0] + segs[si][1]:
            si += 1
        t0, dur, fn = segs[si]
        lt = t - t0
        img = fn(lt, fr).convert("RGB")
        fade = max(clamp(1 - lt / 0.3), clamp(1 - (dur - lt) / 0.3))
        if fade > 0:
            img = Image.blend(img, black, fade)
        ff.stdin.write(img.tobytes())
        if fr % 480 == 0:
            print(f"  frame {fr}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print("Done:", out)


if __name__ == "__main__":
    main()
