"""Render "The Great Laddoo Heist" (an original cat-and-mouse cartoon) to MP4.

Usage:  python3 kitchen_comedy.py [output.mp4]
Reuses the camera, bubble, sound and encoding helpers from railway_comedy.
"""
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kitchen_art as K
import railway_comedy as R
from audio import SR
from kitchen_art import GROUND, TABLE_TOP, WALL, HOLE_X, SACK_X
from railway_art import OL, SD, H, W, font
from railway_comedy import arc, clamp, ease, inside, lin, seg

FPS = 24
TITLE, CARD, STORY, END = 5.0, 3.6, 100.0, 7.5

R.NAMES.update({"cat": ("TUBBY BILLA", (235, 130, 30)), "mouse": ("CHHOTU", (130, 110, 105)),
                "dog": ("SHERU", (150, 90, 45)), "dadi": ("DADI", (40, 150, 95))})

BUBBLES = [
    (4.8, 7.4, "dadi", "speech", "Nobody touches my laddoos! Especially YOU, Billa!"),
    (7.6, 9.2, "cat", "speech", "Zzz... yes, Dadi... zzz..."),
    (12.4, 13.8, "mouse", "thought", "Sniff sniff... LADDOOS!"),
    (17.6, 19.2, "mouse", "thought", "Yum! Just one..."),
    (20.8, 22.9, "cat", "speech", "Hehehe... dinner AND dessert!"),
    (25.6, 27.4, "mouse", "speech", "Ha ha! Look, a snow cat!"),
    (39.8, 41.6, "cat", "thought", "This time, I'll get him!"),
    (46.9, 48.0, "mouse", "thought", "Free cheese, thank you!"),
    (51.6, 53.2, "cat", "speech", "YEEEOOOWWW!!!"),
    (58.4, 60.0, "mouse", "speech", "Nyah nyah!"),
    (62.0, 63.5, "dog", "speech", "GRRRRRR!"),
    (63.6, 65.4, "cat", "speech", "Uh... nice doggy?"),
    (79.0, 80.5, "cat", "speech", "Mine! All mine! Hehe!"),
    (82.0, 83.5, "dadi", "speech", "BILLAAA!!!"),
    (83.6, 85.5, "cat", "speech", "It was the mouse! I swear!"),
    (92.0, 94.0, "mouse", "speech", "Friends share laddoos!"),
    (94.2, 95.8, "dog", "speech", "Woof! Thank you, Chhotu!"),
]

WORDS = [
    (24.2, "ZIP!", (480, 560), (120, 220, 255), 0.7),
    (25.2, "POOF!", (690, 470), (255, 255, 255)),
    (30.4, "WHIFF!", (560, 430), (200, 230, 255), 0.7),
    (32.6, "BONK!", (790, 400), (255, 150, 0)),
    (38.2, "POP!", (HOLE_X + 60, 560), (255, 220, 40), 0.7),
    (46.0, "SNAP!", (230, 580), (255, 80, 60), 0.8),
    (51.2, "SNAP!", (840, 560), (255, 80, 60), 0.8),
    (52.6, "CLANG!", (640, 600), (200, 220, 240), 0.8),
    (56.5, "CRASH!", (920, 520), (255, 120, 0)),
    (61.4, "BONK!", (980, 520), (255, 150, 0)),
    (69.8, "BIFF!", (560, 420), (255, 230, 40), 0.7),
    (70.5, "POW!", (800, 400), (255, 90, 60), 0.7),
    (71.2, "BANG!", (650, 380), (255, 230, 40), 0.7),
    (73.0, "CRASH!", (1000, 380), (255, 120, 0), 0.7),
    (73.5, "CLANG!", (880, 330), (200, 220, 240), 0.6),
    (73.95, "CLANG!", (1060, 330), (200, 220, 240), 0.6),
    (74.3, "BONGGG!", (980, 360), (255, 230, 40)),
    (86.2, "THWACK!", (700, 400), (255, 150, 0), 0.8),
    (87.0, "THWACK!", (640, 360), (255, 150, 0), 0.8),
    (90.5, "THWACK! YEOWW!", (300, 300), (255, 120, 0)),
]

CAPTIONS = [
    (0.3, "SCENE 1  -  DADI'S FAMOUS LADDOOS"),
    (11.6, "SCENE 2  -  CHHOTU SMELLS SOMETHING SWEET"),
    (23.0, "SCENE 3  -  THE GREAT CHASE"),
    (38.5, "SCENE 4  -  THE MOUSETRAP PLAN"),
    (56.6, "SCENE 5  -  NEVER WAKE A SLEEPING DOG"),
    (65.6, "SCENE 6  -  KITCHEN CHAOS"),
    (78.4, "SCENE 7  -  DADI RETURNS!"),
    (90.0, "FINAL SCENE  -  FRIENDS SHARE LADDOOS"),
]

CAMERA = [
    (0, 640, 360, 1.0), (11.8, 640, 360, 1.0), (12.3, 220, 560, 2.0), (13.4, 220, 560, 2.0), (14.2, 640, 360, 1.0),
    (20.1, 640, 360, 1.0), (20.5, 470, 470, 1.6), (22.8, 470, 470, 1.6), (23.3, 640, 360, 1.0),
    (74.0, 640, 360, 1.0), (74.5, 900, 430, 1.5), (76.5, 900, 430, 1.5), (77.0, 640, 360, 1.0),
    (81.8, 640, 360, 1.0), (82.2, 850, 420, 1.4), (83.5, 850, 420, 1.4), (84.1, 640, 360, 1.0),
    (92.0, 640, 360, 1.0), (94.0, 480, 540, 1.8), (STORY, 480, 540, 1.8),
]

PLATE_ON_TABLE = (670, TABLE_TOP - 2)
TRAP_SPOT = (185, GROUND - 4)
FLOOR_LADDOOS = [(620, 668), (690, 671), (745, 667), (850, 670), (930, 672)]
POTS = [(905, 296, 73.1, (880, GROUND - 2), False), (1040, 296, 73.55, (1070, GROUND - 2), False),
        (970, 296, 74.0, None, True)]


def talking(who, t, f):
    for s, e, w, kind, txt in BUBBLES:
        if w == who and kind == "speech" and s <= t < min(e, s + 0.4 + 0.05 * len(txt)):
            return (f // 3) % 2 == 0
    return False


def world_x(x, ax, cx, facing):
    return x + facing * (cx - ax)


# ---------------------------------------------------------------- cat
def cat_state(t, f):
    st = dict(pose="idle", face="smirk")
    S = dict(mode="stand", x=400, yoff=0, facing=1, angle=0, center=None)
    bob = 0
    if t < 20:
        S["mode"] = "sleep"
    elif t < 20.6:
        st["face"] = "one_eye"
    elif t < 23:
        st.update(pose="rub", face="grin")
    elif t < 24.3:
        st.update(pose="reach", face="grin", crouch=30 * ease(seg(t, 23, 23.6)))
    elif t < 25.2:
        S.update(mode="rot", center=arc((400, GROUND - 180), (650, 600), seg(t, 24.3, 25.2), 120),
                 angle=-75 * ease(seg(t, 24.3, 24.8)))
        st.update(pose="reach", face="shock")
    elif t < 26.6:
        S.update(mode="rot", center=(650 + 4 * math.sin(t * 30), 600), angle=-75)
        st.update(pose="flail", face="shock")
    elif t < 29.5:
        S.update(x=600, facing=-1)
        st.update(flour=True, face="shock" if t < 27.4 else "angry", pose="shake" if t >= 28 else "idle")
        if t >= 28:
            S["x"] = 600 + 6 * math.sin(t * 40)
    elif t < 31.0:
        S.update(x=600, facing=-1)
        st.update(face="angry", pose="reach" if 30.2 <= t < 30.7 else "idle")
    elif t < 31.6:
        S.update(x=600, facing=1)
        st["face"] = "angry"
    elif t < 32.6:
        S.update(x=lin(600, 745, seg(t, 31.6, 32.6)), facing=1)
        st.update(pose="run", face="angry")
    elif t < 35.8:
        S.update(x=735, facing=1)
        st.update(face="dizzy", crouch=40 * ease(seg(t, 32.6, 33.2)), lump=True, stars=True)
    elif t < 38.5:
        S.update(x=735, facing=-1)
        st.update(face="angry", lump=True)
    elif t < 39.6:
        S.update(x=lin(735, 260, seg(t, 38.5, 39.6)), facing=-1)
        bob = -abs(math.sin(t * 12)) * 8
        st.update(face="grin", pose="place")
    elif t < 41.0:
        S.update(x=260, facing=-1)
        st.update(face="grin", pose="place" if t < 40.6 else "rub")
    elif t < 42.4:
        S.update(x=lin(260, 690, seg(t, 41.0, 42.4)), facing=1)
        bob = -abs(math.sin(t * 10)) * 6
        st.update(face="grin", pose="pan_up", crouch=20, tiptoe=True)
    elif t < 51.2:
        S.update(x=SACK_X, facing=-1)
        st.update(face="grin", pose="pan_up", crouch=40, tail_floor=True, peek=True)
    elif t < 52.4:
        u = ease(seg(t, 51.2, 52.4))
        S.update(x=lin(690, 640, u), yoff=-334 * u)
        st.update(pose="flail", face="yeow", trap=True)
    elif t < 55.5:
        a = (t - 52.4) * 7
        S.update(x=640 + 170 * math.cos(a), yoff=-334, facing=1 if math.sin(a) < 0 else -1)
        st.update(pose="cling", face="yeow" if t < 53.5 else "dizzy", trap=True)
    elif t < 56.5:
        a_end = (55.5 - 52.4) * 7
        S.update(mode="rot", center=arc((640 + 170 * math.cos(a_end), GROUND - 334 - 180), (920, GROUND - 150),
                                        seg(t, 55.5, 56.5), 80), angle=720 * seg(t, 55.5, 56.5))
        st.update(pose="flail", face="yeow", trap=True)
    elif t < 57.5:
        S.update(x=920, facing=1)
        st.update(face="dizzy", crouch=50, stars=True)
    elif t < 58.5:
        S.update(x=920, facing=1)
        st.update(face="angry")
    elif t < 59.3:
        S.update(x=lin(920, 660, seg(t, 58.5, 59.3)), facing=-1)
        bob = -abs(math.sin(t * 12)) * 6
        st["face"] = "grin"
    elif t < 61.0:
        S.update(x=lin(660, 820, seg(t, 59.3, 61.0)), facing=1)
        bob = -abs(math.sin(t * 10)) * 5
        st.update(face="grin", pose="pan_up", crouch=15, tiptoe=True)
    elif t < 61.2:
        S.update(x=820, facing=1)
        st.update(face="grin", pose="pan_up")
    elif t < 63.5:
        S.update(x=820, facing=1)
        st.update(face="grin" if t < 62 else "shock", pose="pan_swing")
    elif t < 65.5:
        S.update(x=820, facing=1)
        st.update(face="nervous", pose="hide_pan")
    elif t < 67.0:
        S.update(x=lin(820, 150, seg(t, 65.5, 67.0)), facing=-1)
        st.update(pose="run", face="shock")
    elif t < 67.5:
        S.update(x=150, facing=1)
        st.update(face="shock")
    elif t < 69.5:
        S.update(x=lin(150, 620, seg(t, 67.5, 69.5)), facing=1)
        st.update(pose="run", face="shock")
    elif t < 72.0:
        S["mode"] = "hidden"
    elif t < 73.0:
        S.update(x=lin(700, 980, seg(t, 72.0, 73.0)), facing=1)
        st.update(pose="run", face="shock", lump=True)
    elif t < 74.3:
        S.update(x=975, facing=1)
        st.update(face="dizzy", lump=True, stars=True)
    elif t < 77.0:
        wob = (t - 74.3)
        S.update(x=960 - 50 * math.sin(wob * 2.2), facing=1 if math.cos(wob * 2.2) < 0 else -1)
        st.update(pose="reach", face="shock", pot=True)
    elif t < 77.6:
        S.update(x=930, facing=-1)
        st.update(face="angry", lump=True)
    elif t < 78.5:
        S.update(x=lin(930, 700, seg(t, 77.6, 78.5)), facing=-1)
        bob = -abs(math.sin(t * 12)) * 6
        st.update(face="grin", lump=True)
    elif t < 82.0:
        S.update(x=700, facing=-1)
        st.update(pose="plate", face="grin" if t < 80.5 else "laddoo", laddoos=5, lump=True)
    elif t < 86.2:
        S.update(x=700, facing=1)
        st.update(pose="plate", face="shock" if t < 83.6 else "nervous", laddoos=5, lump=True)
    elif t < 87.3:
        S.update(x=700, facing=-1, yoff=-60 * math.sin(math.pi * seg(t, 86.2, 86.8)))
        st.update(pose="flail", face="yeow", lump=True)
    elif t < 89.5:
        S.update(x=lin(700, -260, seg(t, 87.3, 89.5)), facing=-1)
        st.update(pose="run", face="yeow", lump=True)
    else:
        S["mode"] = "hidden"
    st["talk"] = talking("cat", t, f)
    S["st"] = st
    return S


def cat_head(S):
    if S["mode"] == "sleep":
        return (470, 610)
    if S["mode"] == "rot":
        return (S["center"][0], S["center"][1] - 80)
    return (S["x"] + S["facing"] * 10, GROUND + S["yoff"] - K.CAY + 90 + S["st"].get("crouch", 0))


# ---------------------------------------------------------------- mouse
def mouse_state(t, f):
    st = dict(pose="idle", face="smile")
    S = dict(mode="stand", x=HOLE_X, y=GROUND, yoff=0, facing=1)
    hop = lambda: 0
    if t < 12 or 38.2 <= t < 42.5:
        S["mode"] = "hidden"
    elif t < 13.2:
        S.update(y=WALL + 2)
        st.update(pose="sniff", face="sniff")
    elif t < 13.6:
        x, y = arc((HOLE_X, WALL + 2), (150, GROUND), seg(t, 13.2, 13.6), 30)
        S.update(x=x, y=y)
    elif t < 15.6:
        S.update(x=lin(150, 515, seg(t, 13.6, 15.6)), yoff=hop())
        st["tiptoe"] = True
    elif t < 17.0:
        S.update(x=515, y=lin(GROUND, TABLE_TOP, seg(t, 15.6, 17.0)))
        st["pose"] = "climb"
    elif t < 17.8:
        S.update(x=lin(515, 610, seg(t, 17.0, 17.8)), y=TABLE_TOP, yoff=hop())
    elif t < 19.2:
        S.update(x=610, y=TABLE_TOP)
        st["pose"] = "carry" if t >= 18.2 else "climb"
    elif t < 19.8:
        x, y = arc((610, TABLE_TOP), (600, GROUND), seg(t, 19.2, 19.8), 30)
        S.update(x=x, y=y, facing=-1)
        st["pose"] = "carry"
    elif t < 24.0:
        S.update(x=lin(600, 585, seg(t, 19.8, 23)), facing=-1)
        st.update(pose="carry", face="shock" if t >= 23 else "smile")
    elif t < 24.6:
        S.update(x=lin(585, 250, seg(t, 24.0, 24.6)), facing=-1)
        st.update(pose="carry_run", face="shock")
    elif t < 29.5:
        S.update(x=250, facing=1)
        st.update(pose="laugh" if t < 28.4 else "carry", face="laugh" if t < 28.4 else "tongue")
    elif t < 31.0:
        S.update(x=lin(250, 870, seg(t, 29.5, 31.0)), facing=1)
        st.update(pose="carry_run", face="smile")
    elif t < 35.5:
        S.update(x=870, facing=-1)
        st.update(pose="carry" if t < 32.6 else "laugh", face="tongue" if t < 32.6 else "laugh")
    elif t < 37.5:
        S.update(x=lin(870, HOLE_X + 10, seg(t, 35.5, 37.5)), facing=-1)
        st.update(pose="carry_run")
    elif t < 38.2:
        S.update(x=HOLE_X, y=lin(GROUND, WALL + 2, seg(t, 37.5, 37.8)), facing=-1)
        st.update(pose="carry", face="shock")
    elif t < 44.0:
        S.update(y=WALL + 2)
        st.update(pose="sniff", face="sniff")
    elif t < 44.6:
        x, y = arc((HOLE_X, WALL + 2), (140, GROUND), seg(t, 44.0, 44.6), 30)
        S.update(x=x, y=y)
    elif t < 46.2:
        S.update(x=lin(140, 150, seg(t, 44.6, 45)))
        st.update(pose="fork", face="tongue")
    elif t < 48.0:
        S.update(x=150)
        st.update(pose="cheese", face="wink" if t >= 46.9 else "smile")
    elif t < 50.5:
        S.update(x=lin(185, 815, seg(t, 48.0, 50.5)) - 52, yoff=hop())
        st.update(pose="push", face="grin" if False else "smile")
    elif t < 51.4:
        S.update(x=790)
        st.update(pose="push")
    elif t < 53.5:
        S.update(x=790, facing=-1)
        st.update(pose="laugh", face="laugh")
    elif t < 55.0:
        S.update(x=lin(790, 1150, seg(t, 53.5, 55.0)), facing=1)
        st["pose"] = "run"
    elif t < 66.0:
        peek = 58 <= t < 61
        S.update(x=1150, facing=-1, yoff=-48 if peek else 0)
        st.update(face="tongue" if peek else "smile", behind=True)
    elif t < 67.2:
        S.update(x=lin(1150, 810, seg(t, 66.0, 67.2)), facing=-1)
        st["pose"] = "run"
    elif t < 68.5:
        S.update(x=810, y=lin(GROUND, TABLE_TOP, seg(t, 67.2, 68.5)))
        st["pose"] = "climb"
    elif t < 77.5:
        S.update(x=770, y=TABLE_TOP, facing=-1)
        st.update(pose="laugh" if 69.5 <= t < 77 else "idle", face="laugh" if 69.5 <= t < 77 else "smile")
    elif t < 78.3:
        x, y = arc((770, TABLE_TOP), (420, GROUND), seg(t, 77.5, 78.3), 60)
        S.update(x=x, y=y, facing=-1)
        st["pose"] = "run"
    elif t < 79.0:
        S.update(x=lin(420, 230, seg(t, 78.3, 79.0)), facing=-1)
        st["pose"] = "run"
    elif t < 90.0:
        S.update(x=230, facing=1)
        st.update(pose="wave" if 83.6 <= t < 85.5 else ("laugh" if 87 <= t < 89.5 else "idle"),
                  face="laugh" if 87 <= t < 89.5 else "smile")
    elif t < 91.2:
        S.update(x=lin(230, 600, seg(t, 90.0, 91.2)), facing=1)
        st["pose"] = "run"
    elif t < 91.8:
        S.update(x=lin(600, 540, seg(t, 91.2, 91.8)), facing=-1)
        st["pose"] = "give"
    elif t < 92.8:
        S.update(x=540, facing=-1)
        st.update(pose="give")
    else:
        S.update(x=540, facing=-1)
        st.update(pose="eat" if (t < 96 or t > 98) else "idle", face="wink" if 96 <= t < 98 else "smile")
    st["talk"] = talking("mouse", t, f)
    S["st"] = st
    return S


def mouse_head(S):
    return (S["x"] + S["facing"] * 11, S["y"] + S["yoff"] - K.MAY + 40)


# ---------------------------------------------------------------- dog
def dog_state(t, f):
    st = dict(pose="sleep", face="sleep")
    S = dict(mode="stand", x=1080, facing=-1)
    if t < 61.8:
        pass
    elif t < 65.8:
        st.update(pose="sit", face="angry", lump=True)
    elif t < 67.5:
        S.update(x=lin(1080, 330, seg(t, 65.8, 67.5)))
        st.update(pose="run", face="angry", lump=True)
    elif t < 69.5:
        S.update(x=lin(330, 420, seg(t, 67.5, 69.5)), facing=1)
        st.update(pose="run", face="angry", lump=True)
    elif t < 72.0:
        S["mode"] = "hidden"
    else:
        S.update(x=420, facing=1)
        face = "laugh" if 72 <= t < 79 else ("happy" if t >= 92.6 else "calm")
        if 87 <= t < 90:
            face = "laugh"
        st.update(pose="sit", face=face, lump=True, laddoo=t >= 92.6)
    st["talk"] = talking("dog", t, f)
    S["st"] = st
    return S


def dog_head(S):
    st = S["st"]
    if st["pose"] == "sleep":
        return (S["x"] + S["facing"] * 100, GROUND - K.DAY + 210)
    return (S["x"] + S["facing"] * 15, GROUND - K.DAY + 60)


# ---------------------------------------------------------------- dadi
def dadi_state(t, f):
    st = dict(pose="walk", face="smile")
    S = dict(mode="stand", x=1320, facing=-1)
    if t < 1.0 or 11.5 <= t < 80.5 or t >= 90.5:
        S["mode"] = "hidden"
    elif t < 4.0:
        S["x"] = lin(1320, 760, seg(t, 1.0, 4.0))
        st.update(pose="carry")
    elif t < 4.6:
        S["x"] = 760
        st.update(pose="carry" if t < 4.4 else "walk", laddoos=6)
    elif t < 7.4:
        S["x"] = 760
        st.update(pose="wag", face="angry")
    elif t < 9.0:
        S["x"] = 760
        st.update(pose="hips")
    elif t < 11.5:
        S.update(x=lin(760, 1320, seg(t, 9.0, 11.5)), facing=1)
    elif t < 82.0:
        S["x"] = lin(1320, 1080, seg(t, 80.5, 82.0))
        st.update(pose="broom_up", face="angry")
    elif t < 85.5:
        S["x"] = 1080
        st.update(pose="broom_up" if t < 83.5 else "hips", face="angry")
    elif t < 86.0:
        S["x"] = lin(1080, 880, seg(t, 85.5, 86.0))
        st.update(pose="broom_up", face="angry")
    elif t < 87.3:
        S["x"] = 880
        st.update(pose="broom_swat" if (86.0 <= t < 86.4 or 86.8 <= t < 87.3) else "broom_up", face="angry")
    else:
        S["x"] = lin(880, -320, seg(t, 87.6, 90.5))
        st.update(pose="broom_up", face="angry")
    st["talk"] = talking("dadi", t, f)
    S["st"] = st
    return S


# ---------------------------------------------------------------- limb animation engine
GAIT = {
    "cat":   dict(base=[(160, 352), (214, 352)], walk=(42, 18), run=(78, 36), tip=(46, 30),
                  thr=320, lean=16, bob=7, skip=("cling", "flail")),
    "mouse": dict(base=[(74, 156), (98, 156)], walk=(16, 8), run=(30, 14), tip=(16, 12),
                  thr=220, lean=7, bob=3, skip=("climb",)),
    "dog":   dict(base=[(95, 302), (140, 302), (215, 302), (255, 302)], walk=(44, 16), run=(66, 30),
                  tip=(44, 16), thr=150, lean=0, bob=6, offs=[0.0, 0.5, 0.5, 0.0], skip=("sleep", "sit")),
    "dadi":  dict(base=[(140, 425), (174, 425)], walk=(34, 9), run=(46, 14), tip=(34, 9),
                  thr=380, lean=6, bob=3, skip=()),
}
STATE_FN = {}
_TABS = {}
TAB_DT = 1 / 96


def _table(name):
    """Distance travelled (x and y) and speed for a character, sampled across the whole story."""
    if name not in _TABS:
        fn = STATE_FN[name]
        ts = np.arange(0, STORY + 0.5, TAB_DT)
        xs, ys, ok = [], [], []
        for t in ts:
            S = fn(t, 0)
            xs.append(S["x"])
            ys.append(S.get("y", 0))
            ok.append(S["mode"] == "stand")
        xs, ys, ok = np.array(xs), np.array(ys), np.array(ok)
        dx, dy = np.abs(np.diff(xs, prepend=xs[0])), np.abs(np.diff(ys, prepend=ys[0]))
        bad = ~(ok & np.roll(ok, 1)) | (dx > 60) | (dy > 60)
        dx[bad], dy[bad] = 0, 0
        _TABS[name] = (np.cumsum(dx), np.cumsum(dy), dx / TAB_DT, dy / TAB_DT)
    return _TABS[name]


def motion_at(name, t):
    dX, dY, vx, vy = _table(name)
    i = int(clamp(t / TAB_DT, 0, len(dX) - 1))
    a, b = max(0, i - 4), min(len(dX), i + 5)
    return dX[i], dY[i], float(vx[a:b].mean()), float(vy[a:b].mean())


def gait_pose(name, d, v, st):
    """Distance-driven stepping: stance feet stay planted on the floor, swing feet lift and arc forward."""
    G = GAIT[name]
    kind = "tip" if st.get("tiptoe") else ("run" if v > G["thr"] else "walk")
    S_, H_ = G[kind]
    amp = clamp(v / 70)
    offs = G.get("offs", [0.0, 0.5])
    feet, us = [], []
    for i, (bx, by) in enumerate(G["base"]):
        p = (d / (2 * S_) + offs[i]) % 1
        if p < 0.5:
            u, h = S_ / 2 - S_ * (p / 0.5), 0.0
        else:
            q = (p - 0.5) / 0.5
            u, h = -S_ / 2 + S_ * ease(q), H_ * math.sin(math.pi * q)
        feet.append((bx + u * amp, by - h * amp))
        us.append(u * amp)
    p0 = (d / (2 * S_)) % 1
    bob = G["bob"] * amp * (0.5 - 0.5 * math.cos(4 * math.pi * p0)) * (1.5 if kind == "run" else 1)
    st["feet"] = feet
    st["swing"] = (us[0], us[1])
    st["lean"] = G["lean"] * amp * (1.0 if kind == "run" else 0.35)
    if name == "cat":
        st["bob"] = -bob
    else:
        st["bob_y"] = -bob
    if kind == "tip":
        st["tiptoe"] = True
    return st


def apply_gait(name, S, t):
    st = S["st"]
    if S["mode"] != "stand":
        return
    d, dy, v, vy = motion_at(name, t)
    if name == "mouse" and st.get("pose") == "climb" and vy > 10:
        ph = dy / 18 * math.pi
        st["hands"] = ((78, 50 + 12 * math.sin(ph)), (106, 50 - 12 * math.sin(ph)))
        st["feet"] = [(76, 150 - 9 * math.sin(ph)), (98, 150 + 9 * math.sin(ph))]
        return
    if v < 12 or st.get("pose") in GAIT[name]["skip"] or abs(S.get("yoff", 0)) > 8:
        return
    gait_pose(name, d, v, st)


HANDS_FN = {"cat": K.cat_hands, "mouse": K.mouse_hands, "dadi": K.dadi_hands}
WEIGHTS = (1.0, 0.85, 0.7, 0.55, 0.4, 0.28)


def animate(name, t, f):
    """State at time t with the gait applied and hand/crouch poses blended over the last ~0.18 s,
    so pose changes ease in instead of snapping."""
    fn = STATE_FN[name]
    S = fn(t, f)
    apply_gait(name, S, t)
    if name not in HANDS_FN or S["mode"] not in ("stand", "rot"):
        return S
    acc, wsum, cr = [0.0] * 4, 0.0, 0.0
    for k, w in enumerate(WEIGHTS):
        tk = t - k * 0.035
        if tk < 0:
            break
        Sk = S if k == 0 else fn(tk, f)
        if Sk["mode"] != S["mode"] or Sk.get("facing") != S.get("facing"):
            continue
        if k:
            apply_gait(name, Sk, tk)
        (lx, ly), (rx, ry) = HANDS_FN[name](Sk["st"], tk)
        acc[0] += w * lx
        acc[1] += w * ly
        acc[2] += w * rx
        acc[3] += w * ry
        cr += w * Sk["st"].get("crouch", 0)
        wsum += w
    st = S["st"]
    st["hands"] = ((acc[0] / wsum, acc[1] / wsum), (acc[2] / wsum, acc[3] / wsum))
    if name == "cat":
        st["crouch"] = cr / wsum
    return S


def paste(img, spr, x, y, ax, ay, facing):
    axx = ax if facing > 0 else spr.width - ax
    img.paste(spr, (int(x - axx), int(y - ay)), spr)


# ---------------------------------------------------------------- props
def draw_props(sd, t):
    if 4.4 <= t < 78.5:
        K.plate(sd, *PLATE_ON_TABLE, n=6 if t < 18.2 else 5)
    if t >= 86.2:
        u = seg(t, 86.2, 86.6)
        py = lin(560, GROUND - 6, u)
        K.plate(sd, 740, py, n=0)
        for k, (lx, ly) in enumerate(FLOOR_LADDOOS):
            if k == 0 and t >= 91.0:
                continue
            v = seg(t, 86.4, 87.4)
            x = lin(740, lx, v)
            y = ly - 60 * math.sin(math.pi * v) * (1 if v < 1 else 0)
            K.laddoo(sd, x, y)
    # mousetrap
    if 40.6 <= t < 48.0:
        K.trap(sd, *TRAP_SPOT, closed=46.0 <= t < 47.6, cheese=t < 46.2)
    elif 48.0 <= t < 51.2:
        K.trap(sd, lin(185, 830, seg(t, 48.0, 50.5)), TRAP_SPOT[1])
    elif t >= 56.5:
        K.trap(sd, 965, GROUND - 4, closed=True)
    # frying pan on the floor
    if 52.0 <= t < 52.6:
        K.pan_on_floor(sd, 640, lin(320, GROUND - 4, seg(t, 52.0, 52.6) ** 2))
    elif 52.6 <= t < 58.5 + 0.8:
        K.pan_on_floor(sd, 640, GROUND - 4)
    elif t >= 65.5:
        K.pan_on_floor(sd, 820, GROUND - 4)
    # pots
    for (px, py, tf, land, big) in POTS:
        if t < tf:
            K.pot(sd, px, py, big)
        elif land is None:
            if t < 74.3:
                K.pot(sd, px, lin(py, 400, seg(t, tf, 74.3) ** 2), big)
            elif t >= 77.3:
                K.pot(sd, 860, GROUND - 2, big)
        else:
            u = seg(t, tf, tf + 0.6)
            x, y = arc((px, py), land, u, -40)
            K.pot(sd, x, y, big)


def flour_puffs(sd, t):
    for t0, cx, cy in ((25.2, 690, 530), (28.0, 600, 470)):
        if t0 <= t < t0 + 1.6:
            u = seg(t, t0, t0 + 1.6)
            rng = random.Random(int(t0))
            for _ in range(14):
                a, dist = rng.random() * 6.28, rng.uniform(20, 110) * (0.4 + u)
                r = rng.uniform(16, 34) * (1 - u * 0.6)
                sd.circle(cx + math.cos(a) * dist, cy + math.sin(a) * dist * 0.7, r, fill=(250, 250, 250))


def zzz(sd, x, y, t):
    for k in range(3):
        u = (t * 0.6 + k / 3) % 1
        sd.text((x + 40 * u, y - 70 * u), "Z", int(18 + 16 * u), (90, 110, 200), stroke=2, sfill=(255, 255, 255))


def hearts(sd, x, y, t):
    for k in range(3):
        u = (t * 0.5 + k / 3) % 1
        hx, hy, r = x + 25 * math.sin(k + t), y - 90 * u, 7 + 4 * u
        sd.circle(hx - r * 0.6, hy, r * 0.7, fill=(240, 60, 100))
        sd.circle(hx + r * 0.6, hy, r * 0.7, fill=(240, 60, 100))
        sd.poly([(hx - r * 1.25, hy + 2), (hx + r * 1.25, hy + 2), (hx, hy + r * 1.5)], fill=(240, 60, 100))


# ---------------------------------------------------------------- frame
def render_world(t, f):
    img = K.kitchen().copy()
    d = ImageDraw.Draw(img)
    sd = SD(d)
    K.fan(sd, t, 8)
    K.rug(sd, 400, GROUND)
    C, Mo, D, G = animate("cat", t, f), animate("mouse", t, f), animate("dog", t, f), animate("dadi", t, f)
    sack_front = inside(t, [(24.3, 26.6), (42.4, 51.2)])
    if not sack_front:
        K.flour_sack(sd, t >= 25.2)
    draw_props(sd, t)
    # mouse hiding behind the dog is drawn before the dog
    def draw_mouse():
        if Mo["mode"] == "hidden":
            return
        spr = K.mouse_sprite(t, Mo["st"], Mo["facing"])
        paste(img, spr, Mo["x"], Mo["y"] + Mo["yoff"], K.MAX, K.MAY, Mo["facing"])
    if Mo["st"].get("behind"):
        draw_mouse()
    if D["mode"] != "hidden":
        spr = K.dog_sprite(t, D["st"], D["facing"])
        paste(img, spr, D["x"], GROUND, K.DAX, K.DAY, D["facing"])
        if D["st"]["pose"] == "sleep":
            zzz(sd, D["x"] - 70, GROUND - 140, t)
    if C["mode"] == "sleep":
        K.draw_cat_sleeping(sd, 400, GROUND, t)
        zzz(sd, 480, 570, t)
    elif C["mode"] == "stand":
        spr = K.cat_sprite(t, C["st"], C["facing"])
        paste(img, spr, C["x"], GROUND + C["yoff"], K.CAX, K.CAY, C["facing"])
        if C["st"].get("stars"):
            hx, hy = cat_head(C)
            K.stars(sd, hx, hy - 10, t)
    elif C["mode"] == "rot":
        spr = K.cat_sprite(t, C["st"], 1).rotate(C["angle"], resample=Image.BICUBIC, expand=True)
        cx, cy = C["center"]
        img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)
    if sack_front:
        K.flour_sack(sd, t >= 25.2)
    if not Mo["st"].get("behind"):
        draw_mouse()
    if G["mode"] != "hidden":
        spr = K.dadi_sprite(t, G["st"], G["facing"])
        paste(img, spr, G["x"], GROUND, K.GAX, K.GAY, G["facing"])
    flour_puffs(sd, t)
    if 69.5 <= t < 72.0:
        K.fight_cloud(sd, 680 + 20 * math.sin(t * 7), 540, t)
    if t >= 92.6:
        hearts(sd, 490, 430, t)
    if 23.0 <= t < 24.0:
        sd.text((Mo["x"], Mo["y"] - 120), "!", 44, (255, 230, 40), stroke=5)
    return img, C, Mo, D, G


def anchor(who, C, Mo, D, G):
    return {"cat": lambda: cat_head(C), "mouse": lambda: mouse_head(Mo), "dog": lambda: dog_head(D),
            "dadi": lambda: (G["x"], GROUND - K.GAY + 82)}[who]()


def camera(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAMERA, CAMERA[1:]):
        if t0 <= t <= t1:
            u = ease(seg(t, t0, t1)) if t1 > t0 else 1
            return lin(x0, x1, u), lin(y0, y1, u), lin(z0, z1, u)
    return 640, 360, 1.0


def render_story(t, f):
    world, C, Mo, D, G = render_world(t, f)
    cx, cy, z = camera(t)
    vw, vh = W / z, H / z
    x0, y0 = clamp(cx - vw / 2, 0, W - vw), clamp(cy - vh / 2, 0, H - vh)
    img = world.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh)) if z > 1.001 else world
    to_screen = lambda p: ((p[0] - x0) * z, (p[1] - y0) * z)
    d = ImageDraw.Draw(img)
    for t0, word, p, color, *rest in WORDS:
        if t0 <= t < t0 + (rest[0] if rest else 1.0):
            u = seg(t, t0, t0 + 0.15)
            size = int(lin(30, 84, u) + 6 * math.sin(t * 30) * (1 - seg(t, t0, t0 + 0.6)))
            fnt = font("Inter-Black.otf", size)
            half = fnt.getlength(word) / 2 + 12
            x, y = to_screen(p)
            d.text((clamp(x, half, W - half), clamp(y, 70, H - 120)), word, font=fnt, fill=color, anchor="mm",
                   stroke_width=7, stroke_fill=OL)
    for s, e, who, kind, txt in BUBBLES:
        if s <= t < e:
            hx, hy = to_screen(anchor(who, C, Mo, D, G))
            R.bubble(img, who, kind, txt, clamp(hx, 60, W - 60), clamp(hy, 120, H - 40))
    for t0, cap in CAPTIONS:
        if t0 <= t < t0 + 3.2:
            a = min(seg(t, t0, t0 + 0.3), 1 - seg(t, t0 + 2.8, t0 + 3.2))
            fnt = font("Inter-Black.otf", 26)
            w = fnt.getlength(cap) + 44
            y = H - 58 + (1 - a) * 70
            d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 44), 22, fill=(40, 20, 10), outline=(255, 190, 40), width=3)
            d.text((W / 2, y + 22), cap, font=fnt, fill=(255, 215, 90), anchor="mm")
    if t > 96.3:
        a = seg(t, 96.3, 96.9)
        d.text((W / 2, 110 - (1 - a) * 80), "THE END", font=font("Inter-Black.otf", 110), fill=(255, 215, 60),
               anchor="mm", stroke_width=8, stroke_fill=OL)
    return img


# ---------------------------------------------------------------- cards
CAST = [
    ("cat", "TUBBY BILLA", "The Proud House Cat",
     "Plan: catch the mouse AND eat all the laddoos.",
     "Problem: every plan he makes lands on his own head."),
    ("mouse", "CHHOTU", "The Tiny Genius Mouse",
     "Lives behind the kitchen wall, in a hole with his name on it.",
     "Talent: faster, smaller and much, much smarter than Billa."),
    ("dog", "SHERU", "The Sleepy Guard Dog",
     "Loves: naps on his blue mat.",
     "Hates: anyone who wakes him up with a frying pan."),
    ("dadi", "DADI", "Queen of the Kitchen",
     "Makes the best laddoos in the whole neighbourhood.",
     "Weapon of choice: one very fast broom."),
]


def draw_cast(d, who, t, f):
    bob = math.sin(t * 3) * 4
    talk = (f // 3) % 2 == 0 and 0.6 < t < 2.4
    if who == "cat":
        k = 1.55
        K.draw_cat(SD(d, k, 330 - K.CAX * k, 700 - K.CAY * k + bob), t,
                   dict(pose="rub" if t < 2 else "pan_up", face="grin", talk=talk))
    elif who == "mouse":
        k = 3.4
        K.draw_mouse(SD(d, k, 320 - K.MAX * k, 690 - K.MAY * k + bob), t,
                     dict(pose="carry" if t < 2 else "wave", face="smile", talk=talk))
    elif who == "dog":
        k = 1.6
        K.draw_dog(SD(d, k, 330 - K.DAX * k, 700 - K.DAY * k), t,
                   dict(pose="sleep" if t < 1.8 else "sit", face="sleep" if t < 1.8 else "angry"))
    else:
        k = 1.4
        K.draw_dadi(SD(d, k, 300 - K.GAX * k, 705 - K.GAY * k), t,
                    dict(pose="carry" if t < 1.8 else "broom_up", face="smile" if t < 1.8 else "angry", talk=talk))


def make_card(i):
    who, name, role, a, b = CAST[i]
    color = R.NAMES[who][1]
    bg = R.gradient(tuple(int(c * 0.5) for c in color), (14, 10, 10))

    def render(t, f):
        img = bg.copy()
        d = ImageDraw.Draw(img)
        d.text((W / 2, 40), f"MEET THE CAST   {i + 1} / 4", font=font("Inter-Black.otf", 26),
               fill=(230, 230, 230), anchor="mm")
        draw_cast(d, who, t, f)
        tx = lin(W + 60, 620, ease((t - 0.1) / 0.5))
        d.text((tx, 200), name, font=font("Inter-Black.otf", 56), fill=(255, 255, 255), stroke_width=3, stroke_fill=OL)
        d.text((tx, 278), role, font=font("Inter-Bold.otf", 34), fill=tuple(min(255, c + 80) for c in color))
        y = 360
        for txt in (a, b):
            for l in R.wrap(txt, font("Inter-SemiBold.otf", 29), 600):
                d.text((tx, y), l, font=font("Inter-SemiBold.otf", 29), fill=(240, 240, 240))
                y += 40
            y += 22
        return img
    return render


_tbg = None


def render_title(t, f):
    global _tbg
    if _tbg is None:
        _tbg = Image.blend(K.kitchen().filter(ImageFilter.GaussianBlur(6)), Image.new("RGB", (W, H), (30, 10, 0)), 0.5)
    img = _tbg.copy()
    d = ImageDraw.Draw(img)
    z = 0.6 + 0.4 * ease(t / 0.8)
    d.text((W / 2, 140), "THE GREAT", font=font("Inter-Black.otf", int(80 * z)), fill=(255, 255, 255),
           anchor="mm", stroke_width=6, stroke_fill=(200, 60, 20))
    d.text((W / 2, 240), "LADDOO HEIST", font=font("Inter-Black.otf", int(118 * z)), fill=(255, 190, 40),
           anchor="mm", stroke_width=8, stroke_fill=OL)
    if t > 1.0:
        d.text((W / 2, 335), "An original cat & mouse comedy", font=font("Inter-SemiBold.otf", 32),
               fill=(255, 240, 220), anchor="mm")
    # chase across the bottom
    u = (t / TITLE)
    mx = lin(-100, 1400, u * 1.2)
    k = 1.0
    v = 1500 * 1.2 / TITLE
    m = K.mouse_sprite(t, gait_pose("mouse", mx, v, dict(pose="carry_run", face="smile")), 1, 1.3)
    img.paste(m, (int(mx), 520), m)
    c = K.cat_sprite(t, gait_pose("cat", mx, v, dict(pose="run", face="grin")), 1)
    img.paste(c, (int(mx - 360), 350), c)
    return img


def render_end(t, f):
    img = R.gradient((70, 30, 10), (12, 8, 6))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 105), "THE END", font=font("Inter-Black.otf", 110), fill=(255, 200, 50), anchor="mm",
           stroke_width=7, stroke_fill=OL)
    d.text((W / 2, 215), "MORAL OF THE STORY", font=font("Inter-Bold.otf", 26), fill=(220, 200, 180), anchor="mm")
    for k, l in enumerate(("Greed gets you the broom...", "sharing gets you the laddoos!")):
        d.text((W / 2, 272 + k * 54), l, font=font("Inter-BoldItalic.otf", 42), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, 400), "Starring: TUBBY BILLA  -  CHHOTU  -  SHERU  -  DADI",
           font=font("Inter-SemiBold.otf", 22), fill=(220, 210, 200), anchor="mm")
    d.text((W / 2, 432), "All characters are original.", font=font("Inter-Regular.otf", 18),
           fill=(170, 160, 150), anchor="mm")
    K.draw_dog(SD(d, 0.9, 470 - K.DAX * 0.9, 700 - K.DAY * 0.9), t, dict(pose="sit", face="happy", laddoo=True))
    K.draw_mouse(SD(d, 1.6, 620 - K.MAX * 1.6, 700 - K.MAY * 1.6), t, dict(pose="eat"))
    K.draw_cat(SD(d, 0.75, 860 - K.CAX * 0.75, 700 - K.CAY * 0.75), t,
               dict(pose="idle", face="dizzy", lump=True))
    return img


# ---------------------------------------------------------------- audio
class KTrack(R.RailTrack):
    def speak(self, t, who, dur):
        if who == "dog" and dur > 0:
            s, tt = self._tone(95, 95, min(1.4, dur), wav="saw")
            self.add(t, np.convolve(s, np.ones(10) / 10, mode="same") * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt)), 0.3)
            return
        base, rate = {"cat": (210, 11), "mouse": (720, 16), "dadi": (280, 10)}.get(who, (200, 10))
        rng = random.Random(int(t * 100))
        for k in range(max(1, int(dur * rate))):
            f = base * 2 ** (rng.choice([0, 2, 3, 5, 7, 9, 12]) / 12)
            L = 0.75 / rate
            tt = np.arange(int(L * SR)) / SR
            ph = 2 * np.pi * np.cumsum(f * (1 + 0.15 * tt / L)) / SR
            sig = 0.6 * np.sin(ph) + 0.25 * np.sign(np.sin(ph)) + 0.15 * np.sin(2 * ph)
            self.add(t + k / rate, sig * np.minimum(1, tt / 0.006) * np.exp(-tt / (L * 0.45)), 0.2)

    def _poof(self, t):
        n = self._noise(int(0.8 * SR), 60, 21)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt / 0.2), 3.0)

    def _snap(self, t):
        n = self._noise(int(0.08 * SR), 1, 22)
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt / 0.008), 0.8)
        s, tt = self._tone(1800, 900, 0.1)
        self.add(t, s * np.exp(-tt / 0.02), 0.3)

    def _clang(self, t):
        tt = np.arange(int(1.4 * SR)) / SR
        s = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((520, 1), (1230, .7), (1870, .5), (2650, .4), (3310, .3)))
        self.add(t, s * np.exp(-tt / 0.35), 0.12)

    def _bonk(self, t):
        s, tt = self._tone(520, 160, 0.25)
        self.add(t, s * np.exp(-tt / 0.08), 0.5)
        self._thwack(t)

    def _skid(self, t):
        n = np.diff(self._noise(int(0.6 * SR), 1, 23), prepend=0)
        tt = np.arange(len(n)) / SR
        s, _ = self._tone(1400, 900, 0.6)
        self.add(t, (n * 0.3 + s * 0.5) * np.sin(np.pi * tt / 0.6), 0.25)

    def _yeow(self, t):
        tt = np.arange(int(1.4 * SR)) / SR
        f = 450 + 800 * np.sin(np.pi * tt / 1.4) ** 0.6
        f = f * (1 + 0.04 * np.sin(2 * np.pi * 9 * tt))
        ph = np.cumsum(f) / SR
        s = np.convolve(2 * (ph % 1) - 1, np.ones(5) / 5, mode="same")
        self.add(t, s * np.minimum(1, tt / 0.05) * np.minimum(1, (1.4 - tt) / 0.2), 0.18)

    def _zip(self, t):
        s, tt = self._tone(700, 2600, 0.25)
        self.add(t, s * np.sin(np.pi * tt / 0.25), 0.15)

    def _fight(self, t):
        rng = random.Random(5)
        for k in range(14):
            self.sfx(t + k * 0.17 + rng.uniform(0, 0.05), rng.choice(["thwack", "bonk", "clang", "thwack"]))
        self.laugh(t, 2.4, n=3, gain=0.15, seed=9)


def build_audio(path, story0, total):
    tr = KTrack(total)
    tr.imusic(0, story0, 120, "chaos")
    tr._zip(0.4)
    tr._tada(1.0)
    for i in range(4):
        tr._whoosh(TITLE + i * CARD)
    S = story0
    for a, b, bpm, style in ((0, 11.5, 104, "happy"), (11.5, 23, 92, "sneak"), (23, 38.5, 140, "chaos"),
                             (38.5, 51.2, 90, "sneak"), (51.2, 78.4, 140, "chaos"), (78.4, 90, 120, "chaos"),
                             (90, STORY, 104, "happy")):
        tr.imusic(S + a, S + b, bpm, style)
    for s, e, who, kind, txt in BUBBLES:
        if kind == "speech":
            tr.speak(S + s, who, min(e - s, 0.4 + 0.05 * len(txt)))
    events = [(24.2, "zip"), (25.2, "poof"), (28.0, "poof"), (30.4, "whoosh"), (32.3, "skid"), (32.6, "bonk"),
              (38.2, "ding"), (46.0, "snap"), (51.2, "snap"), (51.3, "yeow"), (52.6, "clang"), (56.5, "boom"),
              (61.4, "bonk"), (65.5, "zip"), (67.0, "skid"), (69.5, "fight"), (73.0, "boom"), (73.5, "clang"),
              (73.95, "clang"), (74.3, "clang"), (77.3, "clang"), (86.2, "thwack"), (87.0, "thwack"),
              (87.0, "yeow"), (90.5, "thwack"), (90.6, "yeow"), (96.3, "tada"), (13.2, "boing"), (19.2, "boing"),
              (55.5, "whoosh"), (12.4, "slideup")]
    events += [(13.6 + k * 0.2, "tiptoe") for k in range(10)] + [(59.3 + k * 0.2, "tiptoe") for k in range(8)]
    events += [(41.0 + k * 0.2, "tiptoe") for k in range(7)]
    for t, name in events:
        tr.sfx(S + t, name)
    for t, d in ((25.6, 2.0), (32.8, 2.5), (51.5, 2.0), (72.5, 4.0), (87.2, 2.5)):
        tr.laugh(S + t, d, n=4, gain=0.25, seed=int(t))
    tr.music(S + STORY, total, 100, [0, 5, 7, 0], "keynote")
    tr.write(path)


STATE_FN.update(cat=cat_state, mouse=mouse_state, dog=dog_state, dadi=dadi_state)


def timeline():
    segs = [(TITLE, render_title)] + [(CARD, make_card(i)) for i in range(4)] + [(STORY, render_story), (END, render_end)]
    out, t = [], 0.0
    for dur, fn in segs:
        out.append((t, dur, fn))
        t += dur
    return out, t


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                              "output", "great_laddoo_heist.mp4")
    out = os.path.abspath(out)
    segs, total = timeline()
    wav = out + ".wav"
    build_audio(wav, segs[-2][0], total)
    n = int(total * FPS)
    print(f"Rendering {n} frames ({total:.1f}s)...", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264",
                           "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-af",
                           "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k",
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
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print("Done:", out)


if __name__ == "__main__":
    main()
