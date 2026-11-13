"""Art for "The Great Laddoo Heist": an original cat-and-mouse cartoon.

Characters: Tubby Billa (cat), Chhotu (mouse), Sheru (dog), Dadi (grandmother).
Each character is drawn facing right on its own canvas; the renderer
mirrors the canvas to face left.
"""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageOps

from railway_art import OL, SD, H, W, font, limb

GROUND = 680          # floor line where characters stand
WALL = 640            # where the wall meets the floor
TABLE_TOP = 455
HOLE_X = 105
SACK_X = 690
FAN = (640, 46)

ORANGE, ORANGE_D, CREAM = (245, 150, 45), (200, 100, 25), (255, 235, 200)
MOUSE_C, MOUSE_L = (150, 130, 125), (205, 190, 180)
DOG_C, DOG_L = (160, 100, 55), (245, 230, 210)


def laddoo(sd, x, y, r=13):
    sd.circle(x, y, r, fill=(250, 165, 30), outline=(170, 90, 10), width=2)
    rng = random.Random(int(x * 7 + y))
    for _ in range(5):
        sd.circle(x + rng.uniform(-r * .6, r * .6), y + rng.uniform(-r * .6, r * .6), 1.6, fill=(200, 110, 10))
    sd.arc((x - r * .6, y - r * .7, x + r * .2, y), 200, 280, (255, 220, 140), 2)


def plate(sd, x, y, n=6):
    sd.ellipse((x - 62, y - 8, x + 62, y + 10), fill=(225, 230, 235), outline=OL, width=3)
    sd.ellipse((x - 46, y - 5, x + 46, y + 5), fill=(205, 210, 218))
    spots = [(-30, -10), (0, -10), (30, -10), (-15, -32), (15, -32), (0, -54)][:n]
    for dx, dy in spots:
        laddoo(sd, x + dx, y + dy)


def pan(sd, hx, hy, ang):
    """Frying pan held at (hx, hy); ang = direction of the pan head (radians)."""
    px, py = hx + 70 * math.cos(ang), hy + 70 * math.sin(ang)
    sd.line([(hx, hy), (hx + 35 * math.cos(ang), hy + 35 * math.sin(ang))], (110, 70, 40), 9)
    sd.circle(px, py, 36, fill=(45, 45, 50), outline=OL, width=4)
    sd.circle(px, py, 26, fill=(70, 70, 78))
    sd.arc((px - 22, py - 22, px + 10, py + 10), 200, 260, (150, 150, 160), 3)


def stars(sd, cx, cy, t, n=4, r=40):
    for k in range(n):
        a = t * 6 + k * 2 * math.pi / n
        x, y = cx + r * math.cos(a), cy + r * 0.35 * math.sin(a)
        pts = []
        for j in range(10):
            rr = 10 if j % 2 == 0 else 4
            b = j * math.pi / 5 - math.pi / 2
            pts.append((x + rr * math.cos(b), y + rr * math.sin(b)))
        sd.poly(pts, fill=(255, 225, 40), outline=OL, width=1)


# ====================================================================== CAT
CW, CH, CAX, CAY = 380, 380, 190, 370


def cat_hands(st, t):
    p = st.get("pose", "idle")
    c = st.get("crouch", 0)
    j = 3 * math.sin(t * 30)
    run = math.sin(t * 22) * 30
    return {
        "idle": ((150, 285 + c), (232, 285 + c)),
        "rub": ((185 + j, 245 + c), (210 - j, 245 + c)),
        "reach": ((285, 215 + c), (292, 240 + c)),
        "pan_up": ((150, 270 + c), (228, 110 + c)),
        "pan_swing": ((150, 270 + c), (300, 215 + c)),
        "place": ((255, 330), (268, 330)),
        "plate": ((262, 230 + c), (285, 230 + c)),
        "cling": ((150, 70), (232, 70)),
        "flail": ((120 + 20 * math.sin(t * 20), 90 + 20 * math.cos(t * 17)),
                  (260 + 20 * math.cos(t * 20), 90 + 20 * math.sin(t * 15))),
        "run": ((160 + run, 250), (215 - run, 250)),
        "hide_pan": ((130, 262 + c), (255 + 10 * math.sin(t * 10), 210 + c)),
        "point": ((150, 285 + c), (310, 175 + c)),
        "shake": ((140 + j * 4, 230), (240 - j * 4, 230)),
        "peek": ((250, 230 + c), (262, 250 + c)),
    }.get(p, ((150, 285 + c), (232, 285 + c)))


def draw_cat(sd, t, st):
    flour = st.get("flour", False)
    body = (238, 238, 240) if flour else ORANGE
    dark = (200, 200, 205) if flour else ORANGE_D
    c = st.get("crouch", 0)
    pose = st.get("pose", "idle")
    face = st.get("face", "smirk")
    L, R = cat_hands(st, t)
    # tail (with a mousetrap on it after the SNAP)
    wag = 12 * math.sin(t * 3)
    if st.get("tail_floor"):
        tail = [(150, 290 + c), (100, 330), (45, 352)]
    else:
        tail = [(146, 292 + c), (100, 318), (64, 280 + wag * 0.5), (70, 236 + wag)]
    limb(sd, tail, body, 11)
    sd.circle(tail[-1][0], tail[-1][1], 8, fill=dark)
    if st.get("trap"):
        tx, ty = tail[-1]
        sd.rect((tx - 30, ty - 12, tx + 30, ty + 12), fill=(200, 160, 100), outline=OL, width=3)
        sd.line([(tx - 24, ty - 10), (tx + 24, ty - 10)], (160, 160, 170), 4)
    # legs
    if pose == "run":
        a = t * 22
        feet = [(180 + 34 * math.cos(a), 345 + 14 * math.sin(a)), (180 + 34 * math.cos(a + math.pi), 345 + 14 * math.sin(a + math.pi))]
        for k in range(3):   # speed blur
            sd.arc((140 - k * 6, 315, 220 + k * 6, 372), 0, 180, (200, 200, 210), 2)
    else:
        feet = [(158, 352), (215, 352)]
    for hip, foot in zip(((168, 290 + c), (205, 290 + c)), feet):
        knee = ((hip[0] + foot[0]) / 2 + (c * 0.4 if hip[0] > 180 else -c * 0.4), (hip[1] + foot[1]) / 2)
        limb(sd, [hip, knee, foot], body, 24)
        sd.ellipse((foot[0] - 20, foot[1] - 10, foot[0] + 24, foot[1] + 12), fill=(255, 255, 255), outline=OL, width=3)
    # back arm
    limb(sd, [(160, 215 + c), L], body, 18)
    # body
    sd.ellipse((128, 185 + c, 238, 312 + c), fill=body, outline=OL, width=4)
    sd.ellipse((158, 205 + c, 222, 306 + c), fill=CREAM if not flour else (250, 250, 250))
    for k in range(3):
        y = 215 + c + k * 26
        sd.arc((122, y, 168, y + 30), 300, 60, dark, 6)
    # head
    hx, hy = 190, 145 + c
    if pose == "pot":
        hy += 0
    for ex, tip in ((-34, -60), (30, -62)):
        sd.poly([(hx + ex - 22, hy - 30), (hx + ex + tip * 0.1, hy + tip - 18), (hx + ex + 22, hy - 34)], fill=body, outline=OL, width=3)
        sd.poly([(hx + ex - 11, hy - 34), (hx + ex + tip * 0.08, hy + tip - 4), (hx + ex + 11, hy - 36)], fill=(255, 160, 180))
    sd.circle(hx, hy, 56, fill=body, outline=OL, width=4)
    for k in (-14, 0, 14):
        sd.line([(hx + k, hy - 54), (hx + k * 0.6, hy - 34)], dark, 5)
    if st.get("lump"):
        sd.ellipse((hx - 22, hy - 86, hx + 14, hy - 48), fill=(255, 140, 120), outline=OL, width=3)
    sd.ellipse((hx - 6, hy + 4, hx + 58, hy + 48), fill=CREAM if not flour else (250, 250, 250))
    # eyes
    lx = st.get("look", 0)
    if face == "sleep":
        for ex in (-18, 22):
            sd.arc((hx + ex - 15, hy - 16, hx + ex + 15, hy + 4), 20, 160, OL, 4)
    elif face == "dizzy":
        for ex in (-18, 22):
            for r in (13, 7):
                sd.arc((hx + ex - r, hy - 8 - r, hx + ex + r, hy - 8 + r), 0, 300, OL, 3)
    else:
        big = 1.3 if face in ("shock", "yeow") else 1.0
        for ex in (-18, 22):
            sd.ellipse((hx + ex - 15 * big, hy - 30 * big, hx + ex + 15 * big, hy + 8), fill=(255, 255, 255), outline=OL, width=3)
            if face == "one_eye" and ex == -18:
                sd.line([(hx + ex - 14, hy - 10), (hx + ex + 14, hy - 10)], OL, 4)
                continue
            sd.ellipse((hx + ex - 8 + lx, hy - 20, hx + ex + 8 + lx, hy + 2), fill=(90, 190, 70))
            sd.ellipse((hx + ex - 3 + lx, hy - 15, hx + ex + 4 + lx, hy - 1), fill=OL)
        if face in ("grin", "angry", "smirk"):
            sd.line([(hx - 34, hy - 36), (hx - 4, hy - 26)], OL, 5)
            sd.line([(hx + 40, hy - 36), (hx + 8, hy - 26)], OL, 5)
        if face == "nervous":
            sd.line([(hx - 34, hy - 30), (hx - 4, hy - 38)], OL, 4)
            sd.line([(hx + 40, hy - 30), (hx + 8, hy - 38)], OL, 4)
            sd.ellipse((hx + 50, hy - 46, hx + 62, hy - 26), fill=(140, 200, 255), outline=OL, width=2)
    # nose, whiskers, mouth
    sd.poly([(hx + 30, hy + 8), (hx + 46, hy + 8), (hx + 38, hy + 18)], fill=(255, 110, 140), outline=OL, width=2)
    for k in (-1, 0, 1):
        sd.line([(hx + 52, hy + 22 + k * 6), (hx + 84, hy + 16 + k * 12)], OL, 2)
        sd.line([(hx + 18, hy + 22 + k * 6), (hx - 14, hy + 16 + k * 12)], OL, 2)
    mx, my = hx + 36, hy + 32
    if st.get("talk") or face in ("yeow", "shock"):
        r = 16 if face == "yeow" else 11
        sd.ellipse((mx - r, my - 6, mx + r, my + r * 1.6), fill=(150, 25, 45), outline=OL, width=3)
    elif face in ("grin", "nervous"):
        sd.chord((mx - 22, my - 8, mx + 20, my + 16), 0, 180, fill=(255, 255, 255), outline=OL, width=3)
        sd.poly([(mx - 12, my + 3), (mx - 6, my + 3), (mx - 9, my + 10)], fill=OL)
    elif face == "laddoo":
        laddoo(sd, mx, my + 4, 11)
    elif face in ("sleep", "dizzy"):
        sd.arc((mx - 10, my - 4, mx + 10, my + 8), 20, 160, OL, 3)
    else:
        sd.arc((mx - 16, my - 10, mx + 10, my + 8), 20, 140, OL, 4)
    if st.get("pot"):
        sd.rrect((hx - 66, hy - 70, hx + 66, hy + 10), 12, fill=(185, 190, 200), outline=OL, width=4)
        sd.rect((hx - 74, hy + 2, hx + 74, hy + 16), fill=(160, 165, 175), outline=OL, width=3)
        sd.arc((hx - 50, hy - 60, hx - 10, hy - 20), 200, 260, (240, 240, 250), 4)
    # front arm
    limb(sd, [(215, 215 + c), R], body, 18)
    for hand in (L, R):
        sd.circle(hand[0], hand[1], 13, fill=(255, 255, 255), outline=OL, width=3)
    if pose in ("pan_up", "pan_swing", "hide_pan") and st.get("pan", True):
        hand = R if pose != "hide_pan" else L
        ang = {"pan_up": -1.2, "pan_swing": 0.15, "hide_pan": 2.2}[pose]
        pan(sd, hand[0], hand[1], ang)
    if pose == "plate":
        plate(sd, 274, 228 + c, st.get("laddoos", 6))
    if pose == "place":
        sd.rect((228, 330, 300, 350), fill=(200, 160, 100), outline=OL, width=3)
        sd.poly([(250, 330), (285, 330), (268, 312)], fill=(255, 215, 60), outline=OL, width=2)


def rug(sd, x, y):
    sd.ellipse((x - 150, y - 10, x + 150, y + 20), fill=(180, 40, 60), outline=OL, width=3)
    sd.ellipse((x - 130, y - 12, x + 130, y + 16), outline=(255, 210, 80), width=3)


def draw_cat_sleeping(sd, x, y, t):
    breath = 3 * math.sin(t * 2)
    limb(sd, [(x - 70, y - 20), (x - 110, y - 35), (x - 80, y - 60)], ORANGE, 16)
    sd.ellipse((x - 85, y - 75 - breath, x + 70, y - 2), fill=ORANGE, outline=OL, width=4)
    for k in range(3):
        sd.arc((x - 50 + k * 30, y - 80 - breath, x - 20 + k * 30, y - 40), 200, 340, ORANGE_D, 6)
    hx, hy = x + 70, y - 38
    for ex in (-28, 24):
        sd.poly([(hx + ex - 18, hy - 26), (hx + ex, hy - 66), (hx + ex + 18, hy - 30)], fill=ORANGE, outline=OL, width=3)
    sd.circle(hx, hy, 44, fill=ORANGE, outline=OL, width=4)
    sd.ellipse((hx - 4, hy + 2, hx + 46, hy + 36), fill=CREAM)
    for ex in (-14, 20):
        sd.arc((hx + ex - 12, hy - 14, hx + ex + 12, hy + 2), 20, 160, OL, 4)
    sd.poly([(hx + 24, hy + 6), (hx + 38, hy + 6), (hx + 31, hy + 14)], fill=(255, 110, 140), outline=OL, width=2)
    sd.arc((hx + 20, hy + 14, hx + 40, hy + 26), 20, 160, OL, 3)


def cat_sprite(t, st, facing=1):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    draw_cat(SD(ImageDraw.Draw(im)), t, st)
    return im if facing > 0 else ImageOps.mirror(im)


# ====================================================================== MOUSE
MW, MH, MAX, MAY = 170, 170, 85, 162


def draw_mouse(sd, t, st):
    pose = st.get("pose", "idle")
    face = st.get("face", "smile")
    run = math.sin(t * 26) * 8 if pose in ("run", "carry_run") else 0
    sd.arc((10, 100, 70, 150), 160, 330, (240, 160, 170), 4)                 # tail
    for k, fx in enumerate((70 + run, 96 - run)):
        sd.line([(fx + 4, 132), (fx, 155)], MOUSE_C, 8)
        sd.ellipse((fx - 6, 150, fx + 16, 162), fill=(245, 170, 180), outline=OL, width=2)
    hands = {
        "idle": ((66, 128), (112, 128)), "run": ((70 + run, 118), (112 - run, 116)),
        "carry": ((70, 52), (100, 52)), "carry_run": ((70, 52), (100, 52)),
        "climb": ((78, 52), (106, 48)), "laugh": ((76, 122), (104, 122)),
        "wave": ((66, 128), (126, 64 + 8 * math.sin(t * 14))), "push": ((122, 110), (130, 104)),
        "fork": ((110, 110), (122, 106)), "cheese": ((110, 104), (122, 104)),
        "give": ((120, 96), (128, 96)), "eat": ((100, 88), (110, 90)), "sniff": ((66, 128), (112, 128)),
    }.get(pose, ((66, 128), (112, 128)))
    sd.ellipse((58, 92, 122, 146), fill=MOUSE_C, outline=OL, width=3)
    sd.ellipse((76, 104, 116, 144), fill=MOUSE_L)
    hx, hy = 96, 74
    if pose == "sniff":
        hy -= 4 + 2 * math.sin(t * 20)
    for ex, ey in ((-20, -20), (16, -24)):
        sd.circle(hx + ex, hy + ey, 17, fill=MOUSE_C, outline=OL, width=3)
        sd.circle(hx + ex, hy + ey, 10, fill=(245, 170, 180))
    sd.circle(hx, hy, 26, fill=MOUSE_C, outline=OL, width=3)
    sd.ellipse((hx + 4, hy - 2, hx + 36, hy + 22), fill=MOUSE_L)
    sd.chord((hx - 24, hy - 40, hx + 18, hy - 6), 180, 360, fill=(220, 30, 40), outline=OL, width=2)   # red cap
    sd.poly([(hx + 10, hy - 18), (hx + 34, hy - 14), (hx + 12, hy - 8)], fill=(200, 20, 30), outline=OL, width=2)
    for ex in (-2, 16):
        if face in ("laugh", "sniff") or (face == "wink" and ex == 16):
            sd.arc((hx + ex - 7, hy - 8, hx + ex + 7, hy + 2), 180, 360, OL, 3)
        else:
            big = 1.35 if face == "shock" else 1.0
            sd.ellipse((hx + ex - 7 * big, hy - 12 * big, hx + ex + 7 * big, hy + 4), fill=(255, 255, 255), outline=OL, width=2)
            sd.circle(hx + ex + 2, hy - 3, 3.5, fill=OL)
    sd.circle(hx + 36, hy + 6, 5, fill=OL)
    for k in (-1, 1):
        sd.line([(hx + 34, hy + 10), (hx + 52, hy + 8 + k * 7)], OL, 1)
    mx, my = hx + 22, hy + 16
    if face in ("laugh", "shock") or st.get("talk"):
        sd.ellipse((mx - 6, my - 2, mx + 6, my + 9), fill=(150, 25, 45), outline=OL, width=2)
    elif face == "tongue":
        sd.arc((mx - 8, my - 4, mx + 8, my + 6), 20, 160, OL, 2)
        sd.ellipse((mx - 3, my + 2, mx + 7, my + 14), fill=(255, 110, 140), outline=OL, width=1)
    else:
        sd.arc((mx - 8, my - 6, mx + 8, my + 6), 20, 160, OL, 2)
    for hand in hands:
        limb(sd, [(90, 104), hand], MOUSE_C, 6)
        sd.circle(hand[0], hand[1], 5, fill=(245, 170, 180), outline=OL, width=1)
    if pose in ("carry", "carry_run"):
        laddoo(sd, 85, 36, 18)
    elif pose == "fork":
        sd.line([(116, 108), (165, 140)], (190, 190, 200), 4)
        for k in (-4, 0, 4):
            sd.line([(165, 140), (172 + k, 150)], (190, 190, 200), 2)
    elif pose == "cheese":
        sd.poly([(108, 112), (140, 112), (124, 90)], fill=(255, 215, 60), outline=OL, width=2)
    elif pose == "give":
        laddoo(sd, 136, 92, 14)
    elif pose == "eat":
        laddoo(sd, 112, 86, 11)


def mouse_sprite(t, st, facing=1, k=1.0):
    im = Image.new("RGBA", (int(MW * k), int(MH * k)), (0, 0, 0, 0))
    draw_mouse(SD(ImageDraw.Draw(im), k), t, st)
    return im if facing > 0 else ImageOps.mirror(im)


# ====================================================================== DOG
DW, DH, DAX, DAY = 380, 320, 190, 312


def draw_dog(sd, t, st):
    pose = st.get("pose", "sleep")
    face = st.get("face", "sleep")
    if pose == "sleep":
        breath = 4 * math.sin(t * 1.6)
        sd.ellipse((40, 300, 330, 318), fill=(90, 130, 200), outline=OL, width=3)   # mat
        sd.ellipse((60, 205 - breath, 300, 308), fill=DOG_C, outline=OL, width=4)
        sd.ellipse((140, 230 - breath, 220, 290), fill=DOG_L)
        hx, hy = 290, 262
        sd.ellipse((240, 286, 300, 310), fill=DOG_L, outline=OL, width=3)
    elif pose == "run":
        a = t * 24
        for k in range(4):
            fx = 100 + k * 55 + 25 * math.cos(a + k * 1.6)
            limb(sd, [(100 + k * 55, 240), (fx, 300)], DOG_C, 20)
        sd.ellipse((60, 170, 290, 260), fill=DOG_C, outline=OL, width=4)
        sd.ellipse((140, 200, 240, 256), fill=DOG_L)
        hx, hy = 300, 168
    else:   # sitting
        sd.ellipse((96, 250, 166, 312), fill=DOG_C, outline=OL, width=3)
        sd.ellipse((110, 140, 270, 300), fill=DOG_C, outline=OL, width=4)
        sd.ellipse((150, 170, 240, 296), fill=DOG_L)
        for x in (160, 222):
            sd.ellipse((x - 26, 284, x + 26, 314), fill=DOG_L, outline=OL, width=3)
        hx, hy = 205, 112
    if pose != "sleep":
        wag = 20 * math.sin(t * (18 if face == "happy" else 6))
        limb(sd, [(95, 250 if pose != "run" else 200), (55, 200 + wag if pose != "run" else 160 + wag)], DOG_C, 12)
    # collar
    if pose != "sleep":
        sd.rect((hx - 44, hy + 40, hx + 44, hy + 54), fill=(220, 30, 40), outline=OL, width=2)
        sd.circle(hx, hy + 64, 9, fill=(255, 210, 50), outline=OL, width=2)
    # head
    sd.ellipse((hx - 66, hy - 30, hx - 30, hy + 40), fill=(110, 65, 35), outline=OL, width=3)     # ear
    sd.circle(hx, hy, 52, fill=DOG_C, outline=OL, width=4)
    sd.ellipse((hx - 2, hy - 4, hx + 70, hy + 46), fill=DOG_L, outline=OL, width=3)              # snout
    sd.ellipse((hx + 52, hy - 2, hx + 74, hy + 16), fill=OL)
    sd.ellipse((hx + 22, hy - 60, hx + 54, hy - 4), fill=(110, 65, 35), outline=OL, width=3)     # ear 2
    if st.get("lump"):
        sd.ellipse((hx - 20, hy - 84, hx + 18, hy - 44), fill=(255, 140, 120), outline=OL, width=3)
    if face in ("sleep", "laugh", "happy"):
        for ex in (-12, 22):
            sd.arc((hx + ex - 11, hy - 22, hx + ex + 11, hy - 6), 200 if face == "sleep" else 180,
                   340 if face == "sleep" else 360, OL, 4)
    else:
        for ex in (-12, 22):
            sd.ellipse((hx + ex - 10, hy - 28, hx + ex + 10, hy - 4), fill=(255, 255, 255), outline=OL, width=2)
            sd.circle(hx + ex + 3, hy - 14, 4, fill=OL)
        if face == "angry":
            sd.line([(hx - 26, hy - 40), (hx + 4, hy - 26)], OL, 6)
            sd.line([(hx + 40, hy - 40), (hx + 14, hy - 26)], OL, 6)
    mx, my = hx + 36, hy + 34
    if face == "angry" or st.get("talk"):
        sd.rect((mx - 26, my - 6, mx + 26, my + 12), fill=(255, 255, 255), outline=OL, width=3)
        for x in (-13, 0, 13):
            sd.line([(mx + x, my - 6), (mx + x, my + 12)], OL, 2)
    elif face in ("laugh", "happy"):
        sd.chord((mx - 24, my - 8, mx + 24, my + 26), 0, 180, fill=(150, 25, 45), outline=OL, width=3)
        if face == "happy":
            sd.ellipse((mx - 8, my + 6, mx + 10, my + 30), fill=(255, 110, 140), outline=OL, width=2)
    else:
        sd.arc((mx - 16, my - 6, mx + 16, my + 10), 20, 160, OL, 3)
    if st.get("laddoo"):
        laddoo(sd, hx + 60, hy + 70, 14)


def dog_sprite(t, st, facing=1):
    im = Image.new("RGBA", (DW, DH), (0, 0, 0, 0))
    draw_dog(SD(ImageDraw.Draw(im)), t, st)
    return im if facing > 0 else ImageOps.mirror(im)


# ====================================================================== DADI
GW, GH, GAX, GAY = 460, 440, 160, 430
SKIN_D = (215, 160, 120)


def draw_dadi(sd, t, st):
    pose = st.get("pose", "walk")
    face = st.get("face", "smile")
    sw = 14 * math.sin(t * 7) if pose == "walk" else 0
    for fx in (138 + sw * 0.5, 172 - sw * 0.5):
        sd.ellipse((fx - 16, 418, fx + 18, 432), fill=SKIN_D, outline=OL, width=2)
    sd.poly([(122, 180), (198, 180), (222, 420), (98, 420)], fill=(40, 150, 95), outline=OL, width=4)  # saree
    sd.rect((100, 398, 220, 420), fill=(240, 190, 40))
    sd.poly([(122, 182), (160, 182), (214, 330), (190, 344)], fill=(150, 30, 70), outline=OL, width=2)  # pallu
    sd.line([(196, 336), (212, 326)], (240, 190, 40), 6)
    hands = {
        "walk": ((112 - sw, 300), (206 + sw, 300)),
        "carry": ((232, 236), (252, 236)),
        "wag": ((112, 300), (236, 118 + 8 * math.sin(t * 16))),
        "broom_up": ((112, 300), (205, 60)),
        "broom_swat": ((112, 300), (275, 250)),
        "shock": ((128, 128), (192, 128)),
        "hips": ((118, 270), (202, 270)),
    }.get(pose, ((112, 300), (206, 300)))
    for sx, hand in zip((126, 194), hands):
        limb(sd, [(sx, 196), hand], SKIN_D, 13)
        sd.circle(hand[0], hand[1], 9, fill=SKIN_D, outline=OL, width=2)
        sd.circle(hand[0], hand[1] - 12, 6, outline=(240, 190, 40), width=3)   # bangle
    if pose == "carry":
        plate(sd, 244, 228, st.get("laddoos", 6))
    if pose in ("broom_up", "broom_swat", "walk_broom"):
        h = hands[1]
        ang = -2.3 if pose == "broom_up" else 0.05
        ex, ey = h[0] + 150 * math.cos(ang + math.pi), h[1] + 150 * math.sin(ang + math.pi)
        if pose == "broom_up":
            ex, ey = h[0] - 40, h[1] + 160
            tip = (h[0] + 35, h[1] - 70)
        else:
            ex, ey = h[0] - 120, h[1] + 20
            tip = (h[0] + 60, h[1] - 6)
        sd.line([(ex, ey), tip], (170, 120, 60), 7)
        bx, by = tip
        sd.poly([(bx - 8, by - 8), (bx + 70, by - 34), (bx + 78, by + 30), (bx + 8, by + 10)],
                fill=(225, 190, 110), outline=OL, width=3)
        for k in range(5):
            sd.line([(bx, by), (bx + 74, by - 28 + k * 14)], (180, 140, 70), 2)
    hx, hy = 160, 120
    sd.rect((148, 152, 172, 184), fill=SKIN_D, outline=OL, width=3)
    sd.circle(hx - 34, hy - 10, 22, fill=(235, 235, 240), outline=OL, width=3)   # bun
    sd.circle(hx, hy, 40, fill=SKIN_D, outline=OL, width=3)
    sd.chord((hx - 42, hy - 44, hx + 42, hy + 6), 180, 360, fill=(235, 235, 240), outline=OL, width=3)
    sd.circle(hx + 8, hy - 18, 4, fill=(220, 20, 40))                              # bindi
    for ex in (-8, 24):
        sd.circle(hx + ex, hy, 11, fill=(240, 248, 255), outline=OL, width=3)
        if face == "angry":
            sd.line([(hx + ex - 10, hy - 18), (hx + ex + 10, hy - 10 if ex < 0 else hy - 22)], OL, 4)
        sd.circle(hx + ex + 2, hy + 1, 3, fill=OL)
    sd.line([(hx + 3, hy), (hx + 13, hy)], OL, 2)
    mx, my = hx + 10, hy + 22
    if st.get("talk") or face == "shock":
        sd.ellipse((mx - 9, my - 4, mx + 9, my + 12), fill=(150, 25, 45), outline=OL, width=2)
    elif face == "angry":
        sd.arc((mx - 10, my, mx + 10, my + 12), 200, 340, OL, 3)
    else:
        sd.arc((mx - 10, my - 6, mx + 10, my + 8), 20, 160, OL, 3)


def dadi_sprite(t, st, facing=-1):
    im = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
    draw_dadi(SD(ImageDraw.Draw(im)), t, st)
    return im if facing > 0 else ImageOps.mirror(im)


# ====================================================================== SET
@lru_cache(maxsize=None)
def kitchen():
    im = Image.new("RGB", (W, H), (250, 220, 150))
    d = ImageDraw.Draw(im)
    sd = SD(d)
    for y in range(0, WALL, 60):                          # wallpaper stripes
        for x in range(0, W, 60):
            sd.circle(x + 30 + (15 if (y // 60) % 2 else 0), y + 30, 4, fill=(240, 195, 120))
    sd.rect((0, 0, W, 22), fill=(235, 235, 230))
    sd.rect((0, WALL - 34, W, WALL), fill=(160, 90, 50), outline=OL, width=2)        # skirting board
    sd.rect((0, WALL, W, H), fill=(190, 100, 70))
    for x in range(-200, W + 200, 90):
        sd.line([(x, WALL), (x + (x - 640) * 0.25, H)], (165, 82, 55), 3)
    for y in (668, 700):
        sd.line([(0, y), (W, y)], (165, 82, 55), 3)
    # window with curtains
    sd.rect((180, 110, 420, 320), fill=(150, 210, 245), outline=(120, 70, 40), width=10)
    sd.circle(370, 160, 24, fill=(255, 235, 120))
    sd.line([(300, 110), (300, 320)], (120, 70, 40), 6)
    sd.line([(180, 215), (420, 215)], (120, 70, 40), 6)
    for x0, x1 in ((160, 215), (385, 440)):
        sd.poly([(x0, 95), (x1, 95), (x1 - 10, 340), (x0 + 6, 340)], fill=(220, 60, 90), outline=OL, width=2)
    sd.rect((150, 88, 450, 100), fill=(120, 70, 40))
    # mouse hole
    sd.chord((HOLE_X - 40, WALL - 70, HOLE_X + 40, WALL + 20), 180, 360, fill=(30, 20, 20), outline=OL, width=4)
    sd.rect((HOLE_X - 40, WALL - 26, HOLE_X + 40, WALL), fill=(30, 20, 20))
    sd.rrect((HOLE_X - 26, WALL - 104, HOLE_X + 26, WALL - 82), 4, fill=(255, 250, 230), outline=OL, width=2)
    sd.text((HOLE_X, WALL - 93), "CHHOTU", 11, (200, 30, 40))
    # wall clock & calendar
    sd.circle(780, 150, 40, fill=(255, 255, 255), outline=OL, width=5)
    sd.line([(780, 150), (780, 120)], OL, 4)
    sd.line([(780, 150), (800, 160)], OL, 4)
    sd.rect((490, 130, 570, 230), fill=(255, 255, 255), outline=OL, width=3)
    sd.rect((490, 130, 570, 160), fill=(220, 40, 40))
    sd.text((530, 146), "DIWALI", 14, (255, 255, 255))
    for r in range(4):
        for c in range(4):
            sd.rect((498 + c * 18, 168 + r * 15, 510 + c * 18, 178 + r * 15), fill=(230, 230, 230))
    # shelf with steel pots and spice jars
    sd.rect((860, 296, 1110, 310), fill=(140, 85, 45), outline=OL, width=3)
    for x in (880, 1090):
        sd.poly([(x - 6, 310), (x + 6, 310), (x, 340)], fill=(140, 85, 45), outline=OL, width=2)
    for x, c in ((1070, (220, 60, 30)), (1090, (240, 190, 30))):
        sd.rrect((x - 9, 262, x + 9, 296), 4, fill=c, outline=OL, width=2)
    # hanging ladle hooks
    for x in (900, 940):
        sd.line([(x, 340), (x, 400)], (160, 160, 170), 5)
        sd.circle(x, 408, 12, fill=(170, 170, 180), outline=OL, width=2)
    # door (open)
    sd.rect((1140, 220, 1270, WALL), fill=(120, 200, 120), outline=(110, 60, 30), width=10)
    sd.rect((1150, 470, 1260, WALL - 4), fill=(80, 160, 90))
    sd.circle(1210, 300, 26, fill=(255, 255, 255))
    sd.poly([(1140, 220), (1100, 240), (1100, WALL + 10), (1140, WALL)], fill=(150, 90, 45), outline=OL, width=3)
    # table (front legs drawn later? no: whole table is set dressing)
    sd.rect((500, TABLE_TOP, 840, TABLE_TOP + 22), fill=(150, 90, 45), outline=OL, width=4)
    sd.poly([(500, TABLE_TOP + 22), (840, TABLE_TOP + 22), (830, TABLE_TOP + 52), (510, TABLE_TOP + 52)],
            fill=(250, 250, 245), outline=OL, width=2)   # table cloth
    for x in range(515, 830, 30):
        sd.circle(x, TABLE_TOP + 52, 6, fill=(220, 60, 90))
    for x in (530, 810):
        sd.rect((x - 11, TABLE_TOP + 22, x + 11, GROUND), fill=(130, 75, 38), outline=OL, width=3)
    return im


def fan(sd, t, speed=8):
    x, y = FAN
    sd.line([(x, 0), (x, y)], (90, 90, 95), 6)
    a = t * speed
    for k in range(3):
        b = a + k * 2 * math.pi / 3
        ex, ey = x + 170 * math.cos(b), y + 20 * math.sin(b)
        sd.line([(x, y), (ex, ey)], (110, 110, 120), 14)
        sd.line([(x, y), (ex, ey)], (190, 190, 200), 8)
    sd.ellipse((x - 26, y - 12, x + 26, y + 14), fill=(120, 120, 130), outline=OL, width=3)


def flour_sack(sd, floury=False):
    x = SACK_X
    sd.poly([(x - 55, GROUND), (x - 48, 560), (x - 30, 540), (x + 30, 540), (x + 48, 560), (x + 55, GROUND)],
            fill=(215, 185, 135), outline=OL, width=4)
    sd.line([(x - 32, 552), (x + 32, 552)], (150, 120, 80), 4)
    sd.text((x, 612), "ATTA", 26, (170, 40, 40))
    sd.text((x, 636), "5 KG", 14, (120, 80, 50), name="Inter-Bold.otf")
    if floury:
        for dx in (-30, -5, 22):
            sd.circle(x + dx, 545, 14, fill=(250, 250, 250))


def trap(sd, x, y, closed=False, cheese=False):
    sd.rect((x - 32, y - 12, x + 32, y + 4), fill=(200, 160, 100), outline=OL, width=3)
    sd.circle(x, y - 12, 5, fill=(160, 160, 170), outline=OL, width=1)
    if closed:
        sd.line([(x - 26, y - 14), (x + 26, y - 14)], (170, 170, 180), 5)
    else:
        sd.line([(x, y - 12), (x - 26, y - 46)], (170, 170, 180), 4)
        sd.line([(x - 26, y - 46), (x + 6, y - 50)], (170, 170, 180), 4)
    if cheese:
        sd.poly([(x + 6, y - 12), (x + 30, y - 12), (x + 18, y - 30)], fill=(255, 215, 60), outline=OL, width=2)


def pot(sd, x, y, big=False):
    """Steel pot standing with its bottom at y."""
    w, h = (58, 48) if big else (44, 38)
    sd.rrect((x - w, y - h * 2, x + w, y), 10, fill=(185, 190, 200), outline=OL, width=3)
    sd.rect((x - w - 8, y - h * 2, x + w + 8, y - h * 2 + 10), fill=(160, 165, 175), outline=OL, width=2)
    sd.arc((x - w + 8, y - h * 2 + 14, x - w + 40, y - 10), 160, 220, (240, 240, 250), 4)
    for s in (-1, 1):
        sd.rect((x + s * w, y - h * 1.5, x + s * (w + 14), y - h * 1.3), fill=(90, 90, 95), outline=OL, width=1)


def pan_on_floor(sd, x, y):
    sd.line([(x + 30, y - 4), (x + 90, y - 8)], (110, 70, 40), 9)
    sd.ellipse((x - 40, y - 14, x + 40, y + 6), fill=(45, 45, 50), outline=OL, width=3)


def fight_cloud(sd, x, y, t):
    rng = random.Random(int(t * 12))
    for k in range(16):
        a = k * 2 * math.pi / 16 + t * 3
        r = 90 + 25 * math.sin(t * 9 + k)
        sd.circle(x + r * math.cos(a), y + r * 0.6 * math.sin(a), 52, fill=(225, 205, 170), outline=(150, 120, 90), width=2)
    sd.ellipse((x - 120, y - 80, x + 120, y + 80), fill=(225, 205, 170))
    for _ in range(4):   # limbs poking out
        a = rng.random() * 2 * math.pi
        c = rng.choice([ORANGE, DOG_C])
        limb(sd, [(x + 80 * math.cos(a), y + 50 * math.sin(a)), (x + 160 * math.cos(a), y + 100 * math.sin(a))], c, 16)
        sd.circle(x + 160 * math.cos(a), y + 100 * math.sin(a), 13, fill=(255, 255, 255), outline=OL, width=2)
    stars(sd, x, y - 90, t, 5, 70)
