"""Anatomy sheets for "The Great Laddoo Heist" characters.

For every character this draws each body part on its own, enlarged and labelled, next to the
assembled character with numbered markers. Joints (shoulder, elbow, wrist, hip, knee, ankle)
are marked on the limbs. Every part is also exported as a transparent PNG.

Usage:  python3 body_parts.py            -> output/anatomy_<name>.png + output/parts/<name>/*.png
"""
import math
import os
import re
import sys

from PIL import Image, ImageDraw

import kitchen_art as K
from kitchen_art import (CREAM, DOG_C, DOG_L, MOUSE_C, MOUSE_L, ORANGE, ORANGE_D, SKIN_D, cel, eye_shine,
                         ik, rlimb, tone)
from railway_art import OL, SD, font, limb

SS = 2
GOLD = (245, 195, 50)
PINK = (245, 170, 180)
CARD_BG, CARD_LINE = (255, 252, 246), (226, 216, 200)


# ====================================================================== TUBBY BILLA (cat)
HX, HY = 190, 145


def cat_head(sd):
    for s in (-1, 1):                                                       # cheek fluff
        sd.poly([(HX + s * 46, HY - 4), (HX + s * 70, HY + 2), (HX + s * 54, HY + 12), (HX + s * 68, HY + 24),
                 (HX + s * 48, HY + 26), (HX + s * 56, HY + 38), (HX + s * 30, HY + 34)],
                fill=ORANGE, outline=OL, width=3)
    sd.circle(HX, HY, 56, fill=ORANGE, outline=OL, width=4)
    cel(sd, (HX - 56, HY - 56, HX + 56, HY + 56), ORANGE)
    for k in (-14, 0, 14):                                                  # forehead stripes
        sd.line([(HX + k, HY - 54), (HX + k * 0.6, HY - 34)], ORANGE_D, 5)


def cat_ear(sd):
    ex, tip = -34, -60
    sd.poly([(HX + ex - 22, HY - 30), (HX + ex + tip * 0.1, HY + tip - 18), (HX + ex + 22, HY - 34)],
            fill=ORANGE, outline=OL, width=3)
    sd.poly([(HX + ex - 11, HY - 34), (HX + ex + tip * 0.08, HY + tip - 4), (HX + ex + 11, HY - 36)],
            fill=(255, 160, 180))


def cat_eyes(sd):
    for ex in (-18, 22):
        sd.ellipse((HX + ex - 15, HY - 30, HX + ex + 15, HY + 8), fill=(255, 255, 255), outline=OL, width=3)
        sd.ellipse((HX + ex - 8, HY - 20, HX + ex + 8, HY + 2), fill=(90, 190, 70))
        sd.chord((HX + ex - 8, HY - 20, HX + ex + 8, HY + 2), 180, 360, fill=(60, 150, 50))
        sd.ellipse((HX + ex - 3, HY - 15, HX + ex + 4, HY - 1), fill=OL)
        eye_shine(sd, HX + ex - 2, HY - 13, 2.6)
        sd.arc((HX + ex - 15, HY - 30, HX + ex + 15, HY + 8), 200, 340, OL, 5)
    sd.line([(HX - 34, HY - 36), (HX - 4, HY - 26)], OL, 5)
    sd.line([(HX + 40, HY - 36), (HX + 8, HY - 26)], OL, 5)


def cat_muzzle(sd):
    sd.ellipse((HX - 4, HY - 2, HX + 72, HY + 56), fill=ORANGE, outline=OL, width=3)   # fur patch behind, for contrast
    mz = CREAM
    sd.ellipse((HX + 6, HY + 8, HX + 40, HY + 42), fill=mz)
    sd.ellipse((HX + 30, HY + 8, HX + 64, HY + 42), fill=mz)
    sd.ellipse((HX + 22, HY + 30, HX + 48, HY + 50), fill=mz)
    for k in range(3):
        sd.circle(HX + 24 + k * 5, HY + 26 + (k % 2) * 4, 1.6, fill=tone(ORANGE, 0.7))
        sd.circle(HX + 48 + k * 5, HY + 26 + (k % 2) * 4, 1.6, fill=tone(ORANGE, 0.7))
    sd.poly([(HX + 28, HY + 10), (HX + 48, HY + 10), (HX + 38, HY + 22)], fill=(255, 110, 140), outline=OL, width=2)
    sd.circle(HX + 34, HY + 13, 2, fill=(255, 200, 215))
    sd.line([(HX + 38, HY + 22), (HX + 38, HY + 30)], OL, 2)
    for k in (-1, 0, 1):
        sd.line([(HX + 52, HY + 22 + k * 6), (HX + 84, HY + 16 + k * 12)], OL, 2)
        sd.line([(HX + 18, HY + 22 + k * 6), (HX - 14, HY + 16 + k * 12)], OL, 2)
    mx, my = HX + 36, HY + 32
    sd.arc((mx - 16, my - 6, mx + 2, my + 8), 10, 170, OL, 3)
    sd.arc((mx - 2, my - 6, mx + 16, my + 8), 10, 170, OL, 3)


def cat_torso(sd):
    sd.ellipse((128, 185, 238, 312), fill=ORANGE, outline=OL, width=4)
    cel(sd, (128, 185, 238, 312), ORANGE)
    sd.ellipse((158, 205, 222, 306), fill=CREAM)
    sd.chord((160, 230, 220, 304), 100, 200, fill=tone(CREAM, 0.92))
    sd.poly([(162, 210), (172, 226), (180, 212), (190, 230), (200, 212), (208, 226), (218, 210), (210, 200),
             (170, 200)], fill=CREAM)
    for k in range(3):
        y = 215 + k * 26
        sd.arc((122, y, 168, y + 30), 300, 60, ORANGE_D, 6)


def cat_arm(sd):
    root, hand = (160, 215), (150, 285)
    j, _ = rlimb(sd, root, hand, 42, 40, -1, ORANGE, 18, 14)
    sd.circle(hand[0], hand[1], 13, fill=(255, 255, 255), outline=OL, width=3)
    return [(root[0], root[1], "shoulder", 30, -8), (j[0], j[1], "elbow", -62, 0), (hand[0], hand[1], "wrist / paw", 28, 22)]


def cat_leg(sd):
    hip, ankle = (166, 290), (180, 350)
    j, _ = rlimb(sd, hip, ankle, 35, 34, 1, ORANGE, 24, 19)
    return [(hip[0], hip[1], "hip", -52, 0), (j[0], j[1], "knee", 40, 0), (ankle[0], ankle[1], "ankle", -58, 0)]


def cat_foot(sd):
    fx, fy = 190, 352
    sd.poly([(fx - 18, fy - 8), (fx + 22, fy - 8), (fx + 26, fy + 8), (fx - 18, fy + 10)],
            fill=(255, 255, 255), outline=OL, width=3)
    sd.line([(fx - 16, fy + 6), (fx + 24, fy + 5)], (200, 200, 210), 3)


def cat_tail(sd):
    pts = [(146, 292), (100, 318), (64, 280), (70, 236)]
    limb(sd, pts, ORANGE, 11)
    sd.circle(70, 236, 8, fill=ORANGE_D)
    return [(70, 236, "dark tip", 20, -14)]


# ====================================================================== CHHOTU (mouse)
MX, MY = 96, 74


def mouse_head(sd):
    sd.circle(MX, MY, 26, fill=MOUSE_C, outline=OL, width=3)
    cel(sd, (MX - 26, MY - 26, MX + 26, MY + 26), MOUSE_C, 3)


def mouse_ear(sd):
    sd.circle(76, 54, 17, fill=MOUSE_C, outline=OL, width=3)
    sd.circle(76, 54, 10, fill=PINK)


def mouse_cap(sd):
    sd.chord((MX - 24, MY - 40, MX + 18, MY - 6), 180, 360, fill=(220, 30, 40), outline=OL, width=2)
    sd.poly([(MX + 10, MY - 18), (MX + 34, MY - 14), (MX + 12, MY - 8)], fill=(200, 20, 30), outline=OL, width=2)
    sd.arc((MX - 14, MY - 38, MX + 4, MY - 22), 200, 260, (255, 150, 150), 2)


def mouse_eyes(sd):
    for ex in (-2, 16):
        sd.ellipse((MX + ex - 7, MY - 12, MX + ex + 7, MY + 4), fill=(255, 255, 255), outline=OL, width=2)
        sd.circle(MX + ex + 2, MY - 3, 3.5, fill=OL)
        eye_shine(sd, MX + ex + 1, MY - 5, 1.4)


def mouse_snout(sd):
    sd.ellipse((MX - 4, MY - 8, MX + 44, MY + 34), fill=MOUSE_C, outline=OL, width=3)
    sd.ellipse((MX + 4, MY - 2, MX + 36, MY + 22), fill=MOUSE_L)
    sd.circle(MX + 16, MY + 10, 5, fill=(250, 160, 175))
    sd.circle(MX + 36, MY + 6, 5, fill=OL)
    sd.circle(MX + 35, MY + 4, 1.5, fill=(200, 200, 210))
    for k in (-1, 1):
        sd.line([(MX + 34, MY + 10), (MX + 52, MY + 8 + k * 7)], OL, 1)
    mx, my = MX + 22, MY + 16
    sd.arc((mx - 8, my - 6, mx + 8, my + 6), 20, 160, OL, 2)
    sd.rect((mx - 3, my + 4, mx + 3, my + 10), fill=(255, 255, 255), outline=OL, width=1)
    sd.line([(mx, my + 4), (mx, my + 10)], OL, 1)


def mouse_body(sd):
    sd.ellipse((58, 92, 122, 146), fill=MOUSE_C, outline=OL, width=3)
    cel(sd, (58, 92, 122, 146), MOUSE_C, 3)
    sd.ellipse((76, 104, 116, 144), fill=MOUSE_L)


def mouse_arm(sd):
    sh, hand = (68, 110), (84, 124)
    j, _ = rlimb(sd, sh, hand, 12, 12, -1, MOUSE_C, 6, 5)
    sd.circle(hand[0], hand[1], 5, fill=PINK, outline=OL, width=1)
    return [(sh[0], sh[1], "shoulder", -40, -4), (j[0], j[1], "elbow", -34, 8), (hand[0], hand[1], "paw", 28, 6)]


def mouse_leg(sd):
    hip, ankle = (80, 130), (76, 155)
    j, _ = rlimb(sd, hip, ankle, 14, 14, 1, MOUSE_C, 8, 7)
    sd.ellipse((ankle[0] - 6, ankle[1] - 6, ankle[0] + 16, ankle[1] + 6), fill=PINK, outline=OL, width=2)
    return [(hip[0], hip[1], "hip", -38, 0), (j[0], j[1], "knee", 38, 0), (ankle[0], ankle[1], "ankle", -48, 6)]


def mouse_tail(sd):
    sd.arc((10, 100, 70, 150), 160, 330, (240, 160, 170), 4)


# ====================================================================== SHERU (dog)
DX, DY = 205, 112
EARC = (110, 65, 35)


def dog_head(sd):
    sd.circle(DX, DY, 52, fill=DOG_C, outline=OL, width=4)
    cel(sd, (DX - 52, DY - 52, DX + 52, DY + 52), DOG_C)


def dog_ear(sd):
    sd.ellipse((DX - 66, DY - 30, DX - 30, DY + 40), fill=EARC, outline=OL, width=3)
    sd.arc((DX - 62, DY - 22, DX - 40, DY + 30), 100, 200, tone(EARC, 1.3), 3)


def dog_eyes(sd):
    sd.ellipse((DX + 4, DY - 36, DX + 44, DY + 2), fill=EARC)                  # eye patch
    for ex in (-12, 22):
        sd.ellipse((DX + ex - 10, DY - 28, DX + ex + 10, DY - 4), fill=(255, 255, 255), outline=OL, width=2)
        sd.circle(DX + ex + 3, DY - 14, 4, fill=OL)
        eye_shine(sd, DX + ex + 2, DY - 16, 1.5)


def dog_snout(sd):
    sd.ellipse((DX - 2, DY - 4, DX + 70, DY + 46), fill=DOG_L, outline=OL, width=3)
    sd.chord((DX - 2, DY - 4, DX + 70, DY + 46), 60, 160, fill=tone(DOG_L, 0.9))
    sd.ellipse((DX + 52, DY - 2, DX + 74, DY + 16), fill=OL)
    sd.ellipse((DX + 56, DY + 1, DX + 64, DY + 6), fill=(150, 150, 160))
    mx, my = DX + 36, DY + 34
    sd.arc((mx - 16, my - 6, mx + 16, my + 10), 20, 160, OL, 3)


def dog_collar(sd):
    sd.rect((DX - 44, DY + 40, DX + 44, DY + 54), fill=(220, 30, 40), outline=OL, width=2)
    for x in range(DX - 36, DX + 40, 14):
        sd.line([(x, DY + 43), (x, DY + 51)], (255, 150, 150), 2)
    sd.circle(DX, DY + 64, 9, fill=(255, 210, 50), outline=OL, width=2)
    sd.circle(DX - 2, DY + 62, 2.5, fill=(255, 245, 190))


def dog_body(sd):
    sd.ellipse((96, 250, 166, 312), fill=DOG_C, outline=OL, width=3)           # haunch
    sd.ellipse((110, 140, 270, 300), fill=DOG_C, outline=OL, width=4)
    cel(sd, (110, 140, 270, 300), DOG_C)
    sd.ellipse((150, 170, 240, 296), fill=DOG_L)


def dog_leg(sd):
    hip, paw = (100, 232), (110, 300)
    j, _ = rlimb(sd, hip, paw, 36, 36, 1, DOG_C, 20, 15)
    sd.ellipse((paw[0] - 14, paw[1] - 8, paw[0] + 16, paw[1] + 8), fill=DOG_L, outline=OL, width=2)
    return [(hip[0], hip[1], "shoulder / hip", -78, -6), (j[0], j[1], "elbow / knee", 36, 0), (paw[0], paw[1], "wrist / ankle", 52, 14)]


def dog_paws(sd):
    for x in (160, 222):
        sd.ellipse((x - 26, 284, x + 26, 314), fill=DOG_L, outline=OL, width=3)


def dog_tail(sd):
    limb(sd, [(95, 250), (55, 200)], DOG_C, 12)
    sd.circle(55, 200, 7, fill=tone(DOG_C, 0.85))


# ====================================================================== DADI (grandmother)
GX, GY = 160, 120
WHITE_H = (235, 235, 240)


def dadi_head(sd):
    sd.rect((148, 152, 172, 184), fill=SKIN_D, outline=OL, width=3)           # neck
    sd.circle(GX - 34, GY - 10, 22, fill=WHITE_H, outline=OL, width=3)         # bun
    sd.circle(GX, GY, 40, fill=SKIN_D, outline=OL, width=3)
    cel(sd, (GX - 40, GY - 40, GX + 40, GY + 40), SKIN_D, 3)
    sd.chord((GX - 42, GY - 44, GX + 42, GY + 6), 180, 360, fill=WHITE_H, outline=OL, width=3)


def dadi_eyes(sd):
    for ex in (-8, 24):
        sd.circle(GX + ex, GY, 11, fill=(240, 248, 255), outline=OL, width=3)
        sd.circle(GX + ex + 2, GY + 1, 3, fill=OL)
    sd.line([(GX + 3, GY), (GX + 13, GY)], OL, 2)


def dadi_face(sd):
    sd.circle(GX, GY, 40, fill=SKIN_D, outline=OL, width=3)
    sd.circle(GX - 34, GY + 22, 5, fill=GOLD, outline=OL, width=1)               # earring
    sd.circle(GX + 26, GY + 14, 6, fill=(240, 150, 140))                          # blush
    sd.circle(GX + 8, GY - 18, 4, fill=(220, 20, 40))                              # bindi
    for ex in (-8, 24):
        sd.arc((GX + ex + 9, GY - 2, GX + ex + 19, GY + 8), 300, 30, tone(SKIN_D, 0.7), 2)
    sd.arc((GX + 14, GY + 6, GX + 24, GY + 16), 200, 360, GOLD, 2)                 # nose ring
    mx, my = GX + 10, GY + 22
    sd.arc((mx - 10, my - 6, mx + 10, my + 8), 20, 160, OL, 3)


def dadi_saree(sd):
    green = (40, 150, 95)
    sd.poly([(122, 180), (198, 180), (222, 420), (98, 420)], fill=green, outline=OL, width=4)
    sd.poly([(122, 180), (160, 180), (150, 420), (98, 420)], fill=tone(green, 0.85))
    sd.rect((100, 398, 220, 420), fill=(240, 190, 40))
    for x in range(106, 218, 12):
        sd.circle(x, 409, 3, fill=(170, 30, 70))


def dadi_pallu(sd):
    sd.poly([(122, 182), (160, 182), (214, 330), (190, 344)], fill=(150, 30, 70), outline=OL, width=2)
    sd.line([(196, 336), (212, 326)], GOLD, 6)
    for k in range(5):
        sd.circle(134 + k * 16, 196 + k * 28, 3, fill=GOLD)


def dadi_arm(sd):
    sh, hand = (126, 196), (112, 300)
    j, _ = rlimb(sd, sh, hand, 62, 58, -1, SKIN_D, 13, 11)
    sd.circle(hand[0], hand[1], 9, fill=SKIN_D, outline=OL, width=2)
    sd.circle(hand[0], hand[1] - 12, 6, outline=GOLD, width=3)
    return [(sh[0], sh[1], "shoulder", 44, -6), (j[0], j[1], "elbow", -56, 0), (hand[0], hand[1], "wrist / hand", 54, 8)]


def dadi_hand(sd):
    limb(sd, [(122, 262), (112, 300)], SKIN_D, 11)
    sd.circle(112, 300, 9, fill=SKIN_D, outline=OL, width=2)
    for k, r in enumerate((6, 6)):
        sd.circle(112, 288 - k * 7, r, outline=GOLD, width=3)


def dadi_feet(sd):
    for fx in (140, 174):
        sd.ellipse((fx - 16, 418, fx + 18, 432), fill=SKIN_D, outline=OL, width=2)
    sd.rect((130, 408, 184, 420), fill=(240, 190, 40))


def dadi_broom(sd):
    tip = (35, -70)
    sd.line([(-40, 160), tip], (170, 120, 60), 7)
    bx, by = tip
    sd.poly([(bx - 8, by - 8), (bx + 70, by - 34), (bx + 78, by + 30), (bx + 8, by + 10)],
            fill=(225, 190, 110), outline=OL, width=3)
    for k in range(5):
        sd.line([(bx, by), (bx + 74, by - 28 + k * 14)], (180, 140, 70), 2)


# ====================================================================== sheet layout
# part: (label, description, fn, anchor x, anchor y, scale)
CHARS = {
    "tubby_billa": dict(
        name="TUBBY BILLA", role="The Proud House Cat", color=(235, 130, 30),
        blurb="Orange striped cat, green eyes, cream chest and white-gloved paws.",
        fig=(K.draw_cat, dict(pose="idle", face="smirk"), 182, 215, 2.0),
        marks=[(1, 205, 112, "R"), (2, 150, 80, "L"), (3, 172, 125, "L"), (4, 232, 172, "R"), (5, 172, 262, "L"),
               (6, 222, 252, "R"), (7, 172, 322, "L"), (8, 214, 354, "R"), (9, 70, 250, "L")],
        parts=[
            ("Head", "Round skull with fluffy cheek tufts, forehead stripes and soft shading.", cat_head, HX, HY, 3.0),
            ("Ears", "Pointed outer ear with a pink inner ear. One on each side.", cat_ear, 156, 90, 3.4),
            ("Eyes & brows", "Big green eyes with shine, heavy lids and angled brows.", cat_eyes, 190, 128, 4.2),
            ("Muzzle, nose & whiskers", "Two-lobed cream muzzle, pink nose, whiskers and a 'w' mouth.", cat_muzzle, 232, 172, 3.4),
            ("Torso", "Egg-shaped body, cream belly with a fluffy chest and tiger stripes.", cat_torso, 183, 248, 1.75),
            ("Arm & glove", "Two-bone arm (shoulder, elbow, wrist) ending in a white glove.", cat_arm, 154, 252, 2.9),
            ("Leg", "Two-bone leg: hip, knee and ankle bend as he walks, runs or tiptoes.", cat_leg, 174, 320, 3.0),
            ("Foot", "White shoe with a grey sole. It stays planted while he steps.", cat_foot, 194, 352, 5.4),
            ("Tail", "Long curling tail with a darker tip. It can catch a mousetrap!", cat_tail, 100, 272, 2.6),
        ]),
    "chhotu": dict(
        name="CHHOTU", role="The Tiny Genius Mouse", color=(130, 110, 105),
        blurb="Small grey mouse in a red cap with big ears, buck teeth and a pink tail.",
        fig=(K.draw_mouse, dict(pose="idle", face="smile"), 70, 95, 4.0),
        marks=[(1, 84, 92, "L"), (2, 64, 48, "L"), (3, 92, 38, "R"), (4, 98, 70, "L"), (5, 118, 86, "R"),
               (6, 90, 135, "L"), (7, 108, 118, "R"), (8, 98, 150, "R"), (9, 30, 108, "L")],
        parts=[
            ("Head", "Round head with a shaded crescent on the lower-left edge.", mouse_head, MX, MY, 5.4),
            ("Ears", "Big round ear with a pink inner ear. He has two.", mouse_ear, 76, 54, 7.0),
            ("Red cap", "His trademark red cap, with a short brim and a shine on the dome.", mouse_cap, 100, 50, 6.2),
            ("Eyes", "Large white eyes with black pupils and a sparkle highlight.", mouse_eyes, 105, 70, 10.0),
            ("Snout, nose & teeth", "Light muzzle, black nose, thin whiskers and two buck teeth.", mouse_snout, 122, 84, 7.6),
            ("Body", "Chubby pear-shaped body with a light belly patch.", mouse_body, 90, 119, 3.9),
            ("Arm & paw", "Tiny two-bone arm ending in a pink paw.", mouse_arm, 78, 118, 9.5),
            ("Leg & foot", "Short bending leg with a big pink foot.", mouse_leg, 80, 142, 8.0),
            ("Tail", "Long thin pink tail that curls behind him.", mouse_tail, 42, 122, 6.2),
        ]),
    "sheru": dict(
        name="SHERU", role="The Sleepy Guard Dog", color=(150, 90, 45),
        blurb="Big brown dog with floppy ears, a patch over one eye and a red collar.",
        fig=(K.draw_dog, dict(pose="sit", face="calm"), 167, 185, 2.2),
        marks=[(1, 198, 72, "R"), (2, 157, 95, "L"), (3, 229, 98, "R"), (4, 260, 140, "R"), (5, 205, 166, "L"),
               (6, 232, 235, "R"), (7, 222, 300, "R"), (8, 60, 215, "L")],
        parts=[
            ("Head", "Large round head with shading.", dog_head, DX, DY, 3.0),
            ("Floppy ear", "Long dark-brown ear that flops beside his face.", dog_ear, DX - 48, DY + 5, 4.6),
            ("Eyes & eye patch", "Round eyes with a brown patch around the right one.", dog_eyes, DX + 5, DY - 16, 5.6),
            ("Snout & nose", "Cream muzzle, shiny black nose and a soft mouth line.", dog_snout, DX + 36, DY + 22, 4.2),
            ("Collar & tag", "Red collar with stitching and a gold name tag.", dog_collar, DX, DY + 54, 3.4),
            ("Body & haunch", "Big sitting body with a cream chest and a round back haunch.", dog_body, 188, 226, 1.7),
            ("Front paws", "Two cream paws, used when he sits.", dog_paws, 191, 299, 3.4),
            ("Tail", "Thick brown tail that wags faster the happier he is.", dog_tail, 75, 225, 4.6),
            ("Leg (running pose)", "Two-bone leg, seen when he runs. All four legs bend like this.", dog_leg, 105, 268, 3.4),
        ]),
    "dadi": dict(
        name="DADI", role="Queen of the Kitchen", color=(40, 150, 95),
        blurb="Grandmother in a green saree with a white bun, round glasses and gold jewellery.",
        fig=(K.draw_dadi, dict(pose="hips", face="smile"), 160, 255, 1.8),
        marks=[(1, 192, 100, "R"), (2, 152, 120, "L"), (3, 178, 140, "R"), (4, 140, 330, "L"), (5, 198, 332, "R"),
               (6, 85, 226, "L"), (7, 118, 272, "L"), (8, 157, 425, "R")],
        parts=[
            ("Head, hair & bun", "Round face, white hair swept back and a bun at the back.", dadi_head, 150, 125, 3.1),
            ("Glasses & eyes", "Round glasses over small dark eyes.", dadi_eyes, GX + 8, GY, 6.8),
            ("Face details", "Red bindi, gold nose ring and earring, blush and smile lines.", dadi_face, GX + 4, GY + 8, 4.6),
            ("Saree", "Long green saree with a shaded fold and a golden border.", dadi_saree, 160, 300, 1.2),
            ("Pallu", "Maroon shoulder cloth with gold dots and a gold pin.", dadi_pallu, 168, 262, 1.8),
            ("Arm", "Two-bone arm (shoulder, elbow, wrist) with a gold bangle.", dadi_arm, 119, 250, 2.4),
            ("Bangles & hand", "Hand with gold bangles on the wrist.", dadi_hand, 114, 285, 7.0),
            ("Feet", "Bare feet peeking out below the saree hem.", dadi_feet, 157, 420, 5.6),
            ("Broom (prop)", "Her favourite weapon: a straw broom on a long wooden pole.", dadi_broom, 30, 40, 1.25),
        ]),
}


def render_part(fn, ax, ay, k, w, h, ss=SS):
    layer = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    sd = SD(ImageDraw.Draw(layer), k * ss, (w / 2 - ax * k) * ss, (h / 2 - ay * k) * ss)
    ann = fn(sd) or []
    return layer, ann


def fit(fn, ax, ay, w, h, kmax=11.0, sidepad=90, vpad=60):
    """Find the scale and centre that make a part fill its cell without clipping."""
    K0, N = 5.0, 2400
    layer, _ = render_part(fn, ax, ay, K0, N, N, 1)
    bb = layer.getbbox() or (N // 2 - 10, N // 2 - 10, N // 2 + 10, N // 2 + 10)
    ew, eh = (bb[2] - bb[0]) / K0, (bb[3] - bb[1]) / K0
    cx = ax + ((bb[0] + bb[2]) / 2 - N / 2) / K0
    cy = ay + ((bb[1] + bb[3]) / 2 - N / 2) / K0
    k = min((w - sidepad) / max(ew, 1), (h - vpad) / max(eh, 1), kmax)
    return cx, cy, k


def annotate(d, ann, ax, ay, k, w, h, ox, oy):
    f = font("Inter-Bold.otf", 15)
    for x, y, text, dx, dy in ann:
        px, py = ox + (x - ax) * k + w / 2, oy + (y - ay) * k + h / 2
        tx, ty = px + dx, py + dy
        d.line((px, py, tx, ty), fill=(90, 90, 100), width=2)
        d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(255, 90, 60), outline=(255, 255, 255), width=2)
        tw = f.getlength(text) + 14
        d.rounded_rectangle((tx - tw / 2, ty - 12, tx + tw / 2, ty + 12), 8, fill=(255, 255, 255), outline=(90, 90, 100), width=2)
        d.text((tx, ty), text, font=f, fill=(50, 50, 60), anchor="mm")


def make_sheet(key, spec, outdir):
    parts = spec["parts"]
    cols, cell_w, cell_h, draw_h, gap = 3, 440, 414, 300, 20
    rows = math.ceil(len(parts) / cols)
    left_w, margin, band = 560, 30, 124
    W = margin * 2 + left_w + gap + cols * cell_w + (cols - 1) * gap
    H = band + rows * (cell_h + gap) + margin - 6
    img = Image.new("RGB", (W, H), (248, 243, 234))
    d = ImageDraw.Draw(img)
    color = spec["color"]
    # title band
    d.rectangle((0, 0, W, band - 14), fill=color)
    d.text((margin + 6, 40), spec["name"], font=font("Inter-Black.otf", 58), fill=(255, 255, 255), anchor="lm")
    d.text((margin + 8, 88), spec["role"], font=font("Inter-Bold.otf", 28), fill=tone(color, 1.55)[:3], anchor="lm")
    d.text((W - margin, 62), "ANATOMY SHEET  -  THE GREAT LADDOO HEIST", font=font("Inter-Bold.otf", 22),
           fill=(255, 255, 255), anchor="rm")
    d.text((W - margin, 92), spec["blurb"], font=font("Inter-Regular.otf", 19), fill=(255, 255, 255), anchor="rm")
    # left card: assembled figure + numbered markers
    lx, ly, lh = margin, band, rows * (cell_h + gap) - gap
    d.rounded_rectangle((lx, ly, lx + left_w, ly + lh), 22, fill=CARD_BG, outline=CARD_LINE, width=3)
    d.text((lx + left_w / 2, ly + 30), "ASSEMBLED", font=font("Inter-Black.otf", 20), fill=(150, 140, 125), anchor="mm")
    fn, st, fax, fay, fk = spec["fig"]
    cx, cy = lx + left_w / 2, ly + lh / 2 + 14
    layer = Image.new("RGBA", (left_w * SS, lh * SS), (0, 0, 0, 0))
    fn(SD(ImageDraw.Draw(layer), fk * SS, (left_w / 2 - fax * fk) * SS, (lh / 2 + 14 - fay * fk) * SS), 0.4, dict(st))
    layer = layer.resize((left_w, lh), Image.LANCZOS)
    img.paste(layer, (lx, ly), layer)
    d = ImageDraw.Draw(img)
    pts = []
    for n, x, y, side in spec["marks"]:
        pts.append([n, cx + (x - fax) * fk, cy + (y - fay) * fk, side])
    for side in ("L", "R"):                                                   # spread badges apart
        grp = sorted((p for p in pts if p[3] == side), key=lambda p: p[2])
        by = []
        for i, p in enumerate(grp):
            y = p[2] if i == 0 else max(p[2], by[-1] + 48)
            by.append(y)
        for p, y in zip(grp, by):
            bx = lx + 40 if side == "L" else lx + left_w - 40
            d.line((p[1], p[2], bx, y), fill=(120, 110, 100), width=2)
            d.ellipse((p[1] - 6, p[2] - 6, p[1] + 6, p[2] + 6), fill=(255, 90, 60), outline=(255, 255, 255), width=2)
            d.ellipse((bx - 19, y - 19, bx + 19, y + 19), fill=color, outline=(255, 255, 255), width=3)
            d.text((bx, y), str(p[0]), font=font("Inter-Black.otf", 22), fill=(255, 255, 255), anchor="mm")
    # parts grid
    gx0 = margin + left_w + gap
    safe = re.sub(r"[^a-z0-9]+", "_", key.lower())
    os.makedirs(os.path.join(outdir, "parts", safe), exist_ok=True)
    for i, (label, desc, pfn, ax, ay, k) in enumerate(parts):
        c, r = i % cols, i // cols
        x0, y0 = gx0 + c * (cell_w + gap), band + r * (cell_h + gap)
        d.rounded_rectangle((x0, y0, x0 + cell_w, y0 + cell_h), 22, fill=CARD_BG, outline=CARD_LINE, width=3)
        ax, ay, k = fit(pfn, ax, ay, cell_w, draw_h)
        layer, ann = render_part(pfn, ax, ay, k, cell_w, draw_h)
        layer = layer.resize((cell_w, draw_h), Image.LANCZOS)
        img.paste(layer, (x0, y0 + 8), layer)
        d = ImageDraw.Draw(img)
        annotate(d, ann, ax, ay, k, cell_w, draw_h, x0, y0 + 8)
        d.line((x0 + 22, y0 + draw_h + 16, x0 + cell_w - 22, y0 + draw_h + 16), fill=CARD_LINE, width=2)
        d.ellipse((x0 + 14, y0 + 14, x0 + 50, y0 + 50), fill=color, outline=(255, 255, 255), width=3)
        d.text((x0 + 32, y0 + 32), str(i + 1), font=font("Inter-Black.otf", 21), fill=(255, 255, 255), anchor="mm")
        d.text((x0 + 22, y0 + draw_h + 40), label, font=font("Inter-Black.otf", 25), fill=(45, 40, 40), anchor="lm")
        yy = y0 + draw_h + 64
        words, line = desc.split(), ""
        dfont = font("Inter-Regular.otf", 17)
        for wd in words:
            if dfont.getlength((line + " " + wd).strip()) > cell_w - 44 and line:
                d.text((x0 + 22, yy), line, font=dfont, fill=(90, 85, 80), anchor="lm")
                yy += 22
                line = wd
            else:
                line = (line + " " + wd).strip()
        d.text((x0 + 22, yy), line, font=dfont, fill=(90, 85, 80), anchor="lm")
        # individual transparent export
        ex_k = min(k * 3.0, 14)
        big, _ = render_part(pfn, ax, ay, ex_k, 1100, 1100, 2)
        bb = big.getbbox()
        if bb:
            pad = 24
            big = big.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(big.width, bb[2] + pad), min(big.height, bb[3] + pad)))
            big.save(os.path.join(outdir, "parts", safe, f"{i + 1:02d}_{re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')}.png"))
    path = os.path.join(outdir, f"anatomy_{safe}.png")
    img.save(path)
    print("Saved", path)
    return path


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
    outdir = os.path.abspath(outdir)
    os.makedirs(outdir, exist_ok=True)
    for key, spec in CHARS.items():
        make_sheet(key, spec, outdir)


if __name__ == "__main__":
    main()
