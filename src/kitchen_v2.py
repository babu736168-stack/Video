"""The Great Laddoo Heist - detailed edition.

Same story, timing, camera, sound and comic words as kitchen_comedy, but every character is drawn from the detailed
cut-out rigs (rig_v2) with real expressions, joint motion and a lit kitchen.

Usage:  python3 kitchen_v2.py [output.mp4]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kitchen_art as K
import kitchen_comedy as Q
import rig_v2 as R
from railway_art import OL, SD, H, W, font
from railway_comedy import clamp, ease, lin, seg

X = K.SS
GROUND = K.GROUND
HEADS = {}


# ---------------------------------------------------------------- background with lighting
_BG = None


def bg_v2():
    global _BG
    if _BG is None:
        base = K.kitchen(X).convert("RGB")
        w, h = base.size
        light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(light)
        ld.polygon([(190, 330), (420, 330), (860, 690), (300, 690)], fill=(255, 238, 180, 56))
        ld.polygon([(215, 330), (400, 330), (700, 690), (400, 690)], fill=(255, 244, 200, 34))
        light = light.filter(ImageFilter.GaussianBlur(14)).resize((w, h), Image.BILINEAR)
        base = base.convert("RGBA")
        base.alpha_composite(light)
        a = np.array(base.convert("RGB")).astype(np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt(((xx - w * 0.42) / (w * 0.75)) ** 2 + ((yy - h * 0.38) / (h * 0.85)) ** 2)
        v = 1.04 - 0.30 * np.clip(d, 0, 1.3) ** 2
        floor = np.clip((yy - h * 0.86) / (h * 0.14), 0, 1)[..., None] * 0.07
        a = a * v[..., None] * (1 - floor)
        _BG = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
    return _BG


# ---------------------------------------------------------------- pose helpers
OLD_K = {"cat": 0.80, "mouse": 0.38, "dog": 0.74, "dadi": 0.78}


def swing(name, t, st):
    d, dy, v, vy = Q.motion_at(name, t)
    G = Q.GAIT[name]
    kind = "tip" if st.get("tiptoe") else ("run" if v > G["thr"] else "walk")
    S_ = G[kind][0] * (R.get(name).k / OLD_K[name])
    ph = 2 * math.pi * d / (2 * S_)
    return ph, clamp(v / 70), kind, v


def blink(f, k, eyes):
    return "closed" if eyes == "open" and (f + k * 37) % 90 < 3 else eyes


def talkamp(txt_flag, t):
    return (0.35 + 0.65 * abs(math.sin(t * 17))) if txt_flag else 0.0


def breathe(P, t, idx=0):
    """Resting breath and a slow weight shift."""
    b = math.sin(2 * math.pi * t / 3.3 + idx)
    P["sy"] = P.get("sy", 1.0) * (1 + 0.012 * b)
    P["bob"] = P.get("bob", 0.0) + 1.3 * b
    P["lean"] = P.get("lean", 0.0) + 0.9 * math.sin(2 * math.pi * t / 5.1 + idx)
    P["sway"] = P.get("sway", 0.0) + 1.6 * math.sin(2 * math.pi * t / 5.1 + idx)


def gesture(P, t, idx=0):
    """Hands and head move while the character is speaking."""
    P["armR"] = 20 + 26 * (0.5 + 0.5 * math.sin(t * 2.9 + idx))
    P["armL"] = 14 + 20 * (0.5 + 0.5 * math.sin(t * 2.3 + 1.0 + idx))
    P["tilt_gait"] = P.get("tilt_gait", 0.0) + 4 * math.sin(t * 2.6 + idx)
    P["bob"] = P.get("bob", 0.0) - 2.5 * abs(math.sin(t * 5.8 + idx))


def gait(P, name, ph, amp, kind, v, arm_swing=True, legs=True, arm_amp=45):
    A_leg = {"walk": 13, "run": 24, "tip": 8}[kind]
    L_lift = {"walk": 9, "run": 18, "tip": 14}[kind]
    if legs and amp > 0.04:
        P["legR"] = A_leg * amp * math.sin(ph)
        P["legL"] = -A_leg * amp * math.sin(ph)
        P["legR_lift"] = L_lift * amp * max(0.0, math.cos(ph))
        P["legL_lift"] = L_lift * amp * max(0.0, -math.cos(ph))
    if arm_swing and amp > 0.04:
        P["armR"] = P.get("armR", 8) - arm_amp * amp * math.sin(ph) * (1.3 if kind == "run" else 1)
        P["armL"] = P.get("armL", 8) + arm_amp * amp * math.sin(ph) * (1.3 if kind == "run" else 1)
    bounce = {"walk": 5, "run": 10, "tip": 3}[kind]
    P["bob"] = P.get("bob", 0) - bounce * amp * abs(math.sin(ph))
    P["sway"] = P.get("sway", 0.0) + 3.4 * amp * math.sin(ph)
    P["tilt_gait"] = P.get("tilt_gait", 0.0) - 2.6 * amp * math.sin(ph)
    P["roll_gait"] = P.get("roll_gait", 0.0) + 2.2 * amp * math.sin(ph)
    return P


def hand_off(rig, P, side, rest):
    """Offset (units, relative to the ground point) of a hand after the arm pose."""
    pivot, param, sign = rig.groups["armR" if side == "R" else "armL"]
    s = 1 if side == "R" else -1
    rest = (rest[0] * s, rest[1])
    v = (rest[0] - pivot[0], rest[1] - pivot[1])
    rv = R.rot(v, P.get(param, 0.0) * sign)
    return (pivot[0] + rv[0], pivot[1] + rv[1] + P.get("bob", 0.0)), pivot


def to_world(rig, off, xw, yw):
    return (xw + off[0] * rig.k, yw + (off[1] - rig.ground_y) * rig.k)


# ---------------------------------------------------------------- per-character poses
CAT_EYES = {"smirk": "open", "grin": "sly", "shock": "wide", "yeow": "wide", "dizzy": "dizzy", "angry": "angry",
            "nervous": "wide", "laddoo": "open", "sleep": "sleep", "one_eye": "wink"}


def cat_pose(C, t, f):
    st = C["st"]
    pose, face = st.get("pose", "idle"), st.get("face", "smirk")
    P = dict(armR=8, armL=8, tilt=0.0, bob=0.0, tail=10 * math.sin(t * 3), look=0.0, props=[])
    eyes = CAT_EYES.get(face, "open")
    if C["mode"] == "sleep":
        br = math.sin(2 * math.pi * t / 3.2)
        P.update(eyes="sleep", armR=-38, armL=-52, legR=-34, legL=34, legR_lift=70, legL_lift=76, tilt=46, tail=62,
                 mouth=0.2 * max(0.0, -br), sy=1 + 0.03 * br, bob=1.5 * br)
        return P
    ph, amp, kind, v = swing("cat", t, st)
    P["look"] = C.get("facing", 1) * 7
    moving = amp > 0.04 and C["mode"] == "stand" and abs(C.get("yoff", 0)) < 8
    if pose == "rub":
        j = 6 * math.sin(t * 30)
        P.update(armR=-30 + j, armL=-30 - j)
    elif pose == "reach":
        P.update(armR=98, armL=18)
    elif pose == "pan_up":
        P.update(armR=165, armL=14)
        P["props"].append(("pan", "R"))
    elif pose == "pan_swing":
        P.update(armR=100, armL=14)
        P["props"].append(("pan", "R"))
    elif pose == "hide_pan":
        P.update(armR=28, armL=22)
        P["props"].append(("pan", "R"))
    elif pose == "place":
        P.update(armR=-34, armL=-34)
    elif pose == "plate":
        P.update(armR=-52, armL=-52)
        P["props"].append(("plate", st.get("laddoos", 6)))
    elif pose == "cling":
        P.update(armR=172, armL=172, legR=10, legL=-10)
    elif pose == "flail":
        P.update(armR=120 + 50 * math.sin(t * 20), armL=120 + 50 * math.cos(t * 17), legR=25 * math.sin(t * 18), legL=-25 * math.sin(t * 18))
    elif pose == "shake":
        P.update(armR=60 + 25 * math.sin(t * 40), armL=60 - 25 * math.sin(t * 40))
    elif pose == "point":
        P.update(armR=118, armL=10)
    elif pose == "peek":
        P.update(armR=40, armL=40)
    if moving and pose not in ("cling", "flail"):
        gait(P, "cat", ph, amp, kind, v, arm_swing=pose in ("idle", "run"), arm_amp=50)
        P["lean"] = -C["facing"] * ((2 + amp * 5) if kind != "tip" else 6) + P.get("roll_gait", 0.0)
    crouch = st.get("crouch", 0)
    if crouch:
        P["bob"] += crouch * 0.5
        P["sy"] = 1 - crouch / 420
        P["legR"], P["legL"] = P.get("legR", 0) + 8, P.get("legL", 0) - 8
    if st.get("tail_floor"):
        P["tail"] = -50
    if st.get("trap"):
        P["props"].append(("trap_tail", None))
    if st.get("pot"):
        P["props"].append(("pot_head", None))
    if face == "laddoo":
        P["props"].append(("laddoo_mouth", None))
    if st.get("stars"):
        P["props"].append(("stars", None))
    if st.get("lump"):
        P["props"].append(("lump", None))
    talk = st.get("talk", False)
    mouth = 1.0 if face in ("yeow",) else (0.7 if face == "shock" else (0.5 if face == "grin" else 0.0))
    if talk:
        mouth = max(mouth, talkamp(True, t))
    P["mouth"] = mouth
    P["eyes"] = blink(f, 0, eyes)
    if not moving and not crouch:
        breathe(P, t, 0)
    if talk and pose == "idle" and not P["props"]:
        gesture(P, t, 0)
    if talk and P["eyes"] == "open" and math.sin(t * 1.7) > 0.55:
        P["eyes"] = "raised"
    P["tilt"] = (5 * math.sin(t * 4) if talk else (-10 if face == "dizzy" else 0)) + P.get("tilt_gait", 0.0)
    if st.get("flour"):
        P["tint"] = 0.82
    return P


MOUSE_EYES = {"smile": "open", "laugh": "happy", "shock": "wide", "wink": "wink", "tongue": "open", "sniff": "open"}


def mouse_pose(M, t, f):
    st = M["st"]
    pose, face = st.get("pose", "idle"), st.get("face", "smile")
    P = dict(armR=10, armL=10, tilt=0.0, bob=0.0, tail=12 * math.sin(t * 5), look=M.get("facing", 1) * 6, props=[])
    ph, amp, kind, v = swing("mouse", t, st)
    if pose in ("carry", "carry_run"):
        P.update(armR=168, armL=168)
        P["props"].append(("laddoo_up", None))
    elif pose == "climb":
        d, dy, vv, vy = Q.motion_at("mouse", t)
        a = dy / 18 * math.pi
        P.update(armR=150 + 20 * math.sin(a), armL=150 - 20 * math.sin(a), legR=14 * math.sin(a), legL=-14 * math.sin(a))
    elif pose == "laugh":
        P.update(armR=-38, armL=-38, bob=-3 * abs(math.sin(t * 14)))
    elif pose == "wave":
        P.update(armR=150 + 18 * math.sin(t * 14), armL=10)
    elif pose == "push":
        P.update(armR=95, armL=95)
    elif pose == "fork":
        P.update(armR=72, armL=10)
        P["props"].append(("fork", "R"))
    elif pose == "cheese":
        P.update(armR=62, armL=10)
        P["props"].append(("cheese", "R"))
    elif pose == "give":
        P.update(armR=82, armL=10)
        P["props"].append(("laddoo", "R"))
    elif pose == "eat":
        P.update(armR=118, armL=118)
        P["props"].append(("laddoo_mouth", None))
    moving = amp > 0.04 and M["mode"] == "stand" and pose != "climb"
    if moving:
        gait(P, "mouse", ph, amp, kind, v, arm_swing=pose in ("idle", "run"), arm_amp=45)
        P["lean"] = -M["facing"] * (2 + amp * 6) + P.get("roll_gait", 0.0)
    if st.get("behind"):
        P["armR"] = P["armL"] = 140
    talk = st.get("talk", False)
    mouth = 0.9 if face in ("laugh", "shock") else (0.6 if face == "tongue" else 0.0)
    if talk:
        mouth = max(mouth, talkamp(True, t))
    P["mouth"] = mouth
    P["eyes"] = blink(f, 1, MOUSE_EYES.get(face, "open"))
    if not moving and pose in ("idle", "sniff", "laugh", "eat", "give"):
        breathe(P, t, 1)
    if talk and pose == "idle":
        gesture(P, t, 1)
    if talk and P["eyes"] == "open" and math.sin(t * 1.9) > 0.55:
        P["eyes"] = "raised"
    P["tilt"] = (-6 if face == "sniff" else (5 * math.sin(t * 4) if talk else 0)) + P.get("tilt_gait", 0.0)
    if face == "laugh":
        P["tilt"] = 6 * math.sin(t * 14)
    return P


DOG_EYES = {"sleep": "sleep", "calm": "open", "angry": "angry", "laugh": "happy", "happy": "happy"}


def dog_pose(D, t, f):
    st = D["st"]
    pose, face = st.get("pose", "sleep"), st.get("face", "calm")
    P = dict(armR=4, armL=4, tilt=0.0, bob=0.0, tail=14 * math.sin(t * (16 if face == "happy" else 5)), look=D.get("facing", 1) * 6, props=[])
    if pose == "sleep":
        br = math.sin(2 * math.pi * t / 3.6)
        P.update(eyes="sleep", mouth=0.22 * max(0.0, -br), sy=1 + 0.03 * br, bob=1.5 * br, tail=4 + 3 * math.sin(t * 0.7),
                 lean=88 * (1 if D["facing"] < 0 else -1), tilt=38, armR=34, armL=34, legR=-20, legL=20)
        P["lying"] = True
        return P
    ph, amp, kind, v = swing("dog", t, st)
    if pose == "run" or amp > 0.2:
        P["armR"] = 4 + 34 * math.sin(ph * 1.6)
        P["armL"] = 4 - 34 * math.sin(ph * 1.6)
        P["legR"] = 18 * math.sin(ph * 1.6 + 1.4)
        P["legL"] = -18 * math.sin(ph * 1.6 + 1.4)
        P["bob"] = -14 * abs(math.sin(ph * 0.8))
        P["lean"] = -D["facing"] * 9
        P["tilt"] = 6 * math.sin(ph * 1.6)
        P["tail"] = 30 * math.sin(t * 22)
    else:
        breathe(P, t, 2)
        P["tilt"] = 3 * math.sin(t * 0.8)
    talk = st.get("talk", False)
    mouth = 1.0 if face in ("angry", "laugh", "happy") else 0.0
    if talk:
        mouth = max(mouth, talkamp(True, t))
    if face == "angry":
        mouth = 0.55 + 0.45 * abs(math.sin(t * 14))
    P["mouth"] = mouth
    P["eyes"] = blink(f, 2, DOG_EYES.get(face, "open"))
    if st.get("lump"):
        P["props"].append(("lump", None))
    if st.get("laddoo"):
        P["props"].append(("laddoo_mouth", None))
    return P


DADI_EYES = {"smile": "open", "angry": "angry", "shock": "wide"}


def dadi_pose(G, t, f):
    st = G["st"]
    pose, face = st.get("pose", "walk"), st.get("face", "smile")
    P = dict(armR=8, armL=8, tilt=0.0, bob=0.0, props=[], look=G.get("facing", -1) * 6)
    ph, amp, kind, v = swing("dadi", t, st)
    if pose == "walk" and amp > 0.04:
        gait(P, "dadi", ph, amp, kind, v, arm_swing=True, arm_amp=18)
        P["lean"] = math.sin(ph) * 1.6
    if pose == "carry":
        P.update(armR=62, armL=62)
        P["props"].append(("plate_dadi", st.get("laddoos", 6)))
    elif pose == "wag":
        P.update(armR=150 + 10 * math.sin(t * 16), armL=12)
    elif pose == "broom_up":
        P.update(armR=158, armL=20)
        P["props"].append(("broom", "up"))
    elif pose == "broom_swat":
        P.update(armR=102, armL=20)
        P["props"].append(("broom", "swat"))
    elif pose == "shock":
        P.update(armR=148, armL=148)
    elif pose == "hips":
        P.update(armR=30, armL=30)
    talk = st.get("talk", False)
    mouth = 0.8 if face == "shock" else (0.45 if face == "angry" and pose in ("wag", "broom_up") else 0.0)
    if talk:
        mouth = max(mouth, talkamp(True, t))
    P["mouth"] = mouth
    P["eyes"] = blink(f, 3, DADI_EYES.get(face, "open"))
    if amp <= 0.04 and pose in ("walk", "hips", "wag", "carry"):
        breathe(P, t, 3)
    if talk and pose in ("walk", "hips") and amp <= 0.04:
        gesture(P, t, 3)
    if talk and P["eyes"] == "open" and math.sin(t * 1.6) > 0.55:
        P["eyes"] = "raised"
    P["tilt"] = (4 * math.sin(t * 3) if talk else 0) + P.get("tilt_gait", 0.0)
    return P


# ---------------------------------------------------------------- drawing characters and props
WRIST = {"cat": (73, 84), "mouse": (49, 52), "dog": (42, 140), "dadi": (70, 66)}
HEADC = {"cat": (0, -72), "mouse": (0, -62), "dog": (0, -66), "dadi": (0, -144)}


def draw_char(img, name, P, xw, yw, tint=0.0, center_rot=None):
    rig = R.get(name)
    im, g, _ = rig.compose(P)
    pv = dict(P)
    if center_rot is not None:
        ang, cen = center_rot
        side = int(math.hypot(im.width, im.height)) + 4
        gx, gy = g
        big = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        big.paste(im, (int(side / 2 - gx), int(side / 2 - gy)))
        bc = (side / 2 + 0, side / 2 - rig.k * X * 0 - 150 * rig.S)
        im = big.rotate(ang, resample=Image.BICUBIC, center=bc)
        g = bc
        xw, yw = cen
        pv = dict(P, lean=0.0, sx=1.0, sy=1.0)
        fin, gg = im, g
    else:
        fin, gg = R.finish(im, g, pv, tint)
    img.paste(fin, (int(xw * X - gg[0]), int(yw * X - gg[1])), fin)
    return rig


def hand_world(name, P, side, xw, yw):
    rig = R.get(name)
    off, piv = hand_off(rig, P, side, WRIST[name])
    return to_world(rig, off, xw, yw), to_world(rig, (piv[0], piv[1] + P.get("bob", 0)), xw, yw)


def draw_props(img, sd, name, P, xw, yw):
    rig = R.get(name)
    for kind, arg in P.get("props", []):
        if kind in ("pan", "fork", "cheese", "laddoo"):
            hand, sh = hand_world(name, P, arg, xw, yw)
            ang = math.atan2(hand[1] - sh[1], hand[0] - sh[0])
            if kind == "pan":
                K.pan(sd, hand[0], hand[1], ang)
            elif kind == "laddoo":
                K.laddoo(sd, hand[0] + 8, hand[1] - 6, 15 if name == "mouse" else 12)
            elif kind == "cheese":
                sd.poly([(hand[0] - 6, hand[1] + 8), (hand[0] + 24, hand[1] + 8), (hand[0] + 9, hand[1] - 12)], fill=(255, 215, 60), outline=OL, width=2)
            else:
                sd.line([(hand[0], hand[1]), (hand[0] + 40 * math.cos(ang), hand[1] + 40 * math.sin(ang))], (190, 190, 200), 3)
        elif kind == "laddoo_up":
            a, _ = hand_world(name, P, "R", xw, yw)
            b, _ = hand_world(name, P, "L", xw, yw)
            K.laddoo(sd, (a[0] + b[0]) / 2, min(a[1], b[1]) - 12, 24)
        elif kind == "laddoo_mouth":
            hc = HEADC[name]
            p = to_world(rig, (hc[0] + P.get("look", 0) * 1.5, hc[1] + {"cat": 32, "mouse": 14, "dog": 30}.get(name, 20) + P.get("bob", 0)), xw, yw)
            K.laddoo(sd, p[0], p[1], 13 if name == "mouse" else 11)
        elif kind == "plate":
            a, _ = hand_world(name, P, "R", xw, yw)
            K.plate(sd, xw, a[1] - 4, arg)
        elif kind == "plate_dadi":
            a, _ = hand_world(name, P, "R", xw, yw)
            b, _ = hand_world(name, P, "L", xw, yw)
            K.plate(sd, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 2, arg)
        elif kind == "trap_tail":
            tip = to_world(rig, R.rot_point((-56, 96), (-104, -30), P.get("tail", 0)) if hasattr(R, "rot_point") else (-104, -30), xw, yw)
            K.trap(sd, tip[0], tip[1] + 14, closed=True)
        elif kind == "pot_head":
            hc = HEADC[name]
            p = to_world(rig, (hc[0], hc[1] + 36), xw, yw)
            K.pot(sd, p[0], p[1], True)
        elif kind == "stars":
            hc = HEADC[name]
            p = to_world(rig, (hc[0], hc[1] - 80), xw, yw)
            K.stars(sd, p[0], p[1], 0.0 + P.get("tt", 0), 4, 40)
        elif kind == "lump":
            hc = HEADC[name]
            p = to_world(rig, (hc[0] - 24, hc[1] - 74), xw, yw)
            sd.ellipse((p[0] - 18, p[1] - 14, p[0] + 18, p[1] + 14), fill=(255, 140, 120), outline=OL, width=2)
            sd.arc((p[0] - 10, p[1] - 9, p[0] + 2, p[1] - 1), 200, 280, (255, 200, 190), 2)
        elif kind == "broom":
            hand, sh = hand_world(name, P, "R", xw, yw)
            spec_img, ox, oy = R.part_image("dadi", rig.spec, "broom", rig.S)
            gx, gy = ox, oy - 40 * rig.S
            ang = -20 if arg == "up" else (-98 + 14 * math.sin(Q.STORY * 0 + P.get("tt", 0) * 18))
            im2, ox2, oy2 = R.xform(spec_img, gx, gy, 1.0, 1.0, ang, ("broom", arg))
            img.paste(im2, (int(hand[0] * X - ox2), int(hand[1] * X - oy2)), im2)


# ---------------------------------------------------------------- world render
def render_world(t, f):
    img = bg_v2().copy()
    d = ImageDraw.Draw(img)
    sd = SD(d, X)
    K.fan(sd, t, 8)
    K.rug(sd, 400, GROUND)
    C, Mo, D, G = Q.cat_state(t, f), Q.mouse_state(t, f), Q.dog_state(t, f), Q.dadi_state(t, f)
    sack_front = Q.inside(t, [(24.3, 26.6), (42.4, 51.2)])
    if not sack_front:
        K.flour_sack(sd, t >= 25.2)
    Q.draw_props(sd, t)

    def shade_under(S, x, w, ground=GROUND):
        if S["mode"] == "stand":
            air = clamp(-S.get("yoff", 0) / 300)
            Q.floor_shadow(img, x, ground + 2, w * (1 - 0.5 * air), X, round(1 - 0.7 * air, 1))
    if Mo["mode"] != "hidden" and Mo["y"] in (GROUND, Q.TABLE_TOP):
        shade_under(Mo, Mo["x"], 100, Mo["y"])
    if D["mode"] != "hidden":
        shade_under(D, D["x"], 330 if D["st"]["pose"] == "sleep" else 260)
    if C["mode"] == "stand":
        shade_under(C, C["x"], 230)
    elif C["mode"] == "rot":
        Q.floor_shadow(img, C["center"][0], GROUND + 2, 180, X, 0.5)
    if G["mode"] != "hidden":
        shade_under(G, G["x"], 220)

    def mouse():
        if Mo["mode"] == "hidden":
            return
        P = mouse_pose(Mo, t, f)
        P["tt"] = t
        yw = Mo["y"] + Mo["yoff"]
        draw_char(img, "mouse", P, Mo["x"], yw)
        draw_props(img, sd, "mouse", P, Mo["x"], yw)
        HEADS["mouse"] = (Mo["x"], yw + (R.get("mouse").head_top - R.get("mouse").ground_y) * R.get("mouse").k)

    if Mo["st"].get("behind"):
        mouse()
    if D["mode"] != "hidden":
        rg = R.get("dog")
        if 61.4 <= t < 62.7:
            # startled awake: leaps up from lying on his side
            u = ease((t - 61.4) / 1.1)
            Ds = dict(D, st=dict(D["st"], pose="sleep", face="sleep"), facing=-1)
            P = dog_pose(Ds, t, f)
            P.pop("lying", None)
            P["lean"] = 88 * (1 - u)
            P["tilt"] = 38 * (1 - u)
            P["armR"] = lin(34, 4, u) + 45 * math.sin(t * 26) * (1 - u)
            P["armL"] = lin(34, 4, u) - 45 * math.sin(t * 26) * (1 - u)
            P["legR"], P["legL"] = 20 * math.sin(t * 28) * (1 - u), -20 * math.sin(t * 28) * (1 - u)
            P["eyes"] = "wide" if u < 0.55 else "angry"
            P["mouth"] = lin(0.0, 1.0, u)
            P["bob"] = -30 * math.sin(math.pi * u)
            P["sy"] = 1.0
            P["tt"] = t
            xw, yw = D["x"], lin(GROUND - 100, GROUND, u)
            draw_char(img, "dog", P, xw, yw)
            HEADS["dog"] = (xw - (1 - u) * 235, lin(GROUND - 150, GROUND + (rg.head_top - rg.ground_y) * rg.k, u))
        else:
            P = dog_pose(D, t, f)
            P["tt"] = t
            xw, yw = D["x"], GROUND
            if P.get("lying"):
                yw = GROUND - 100
            draw_char(img, "dog", P, xw, yw)
            draw_props(img, sd, "dog", P, xw, yw)
            HEADS["dog"] = (xw, yw + (rg.head_top - rg.ground_y) * rg.k) if not P.get("lying") else (xw - 235, GROUND - 150)
            if P.get("lying"):
                Q.zzz(sd, D["x"] - 250, GROUND - 190, t)
    rgc = R.get("cat")
    ln = (rgc.ground_y - rgc.head_top) * rgc.k
    sx0 = 400 - 0.5 * ln
    if 19.2 <= t < 20.6 and C["mode"] in ("sleep", "stand"):
        # waking up: stretch, yawn, roll upright
        u = ease((t - 19.2) / 1.4)
        Cs = dict(C, mode="sleep")
        P = cat_pose(Cs, t, f)
        P["lean"] = -86 * (1 - u)
        P["tilt"] = 46 * (1 - u)
        stretch = math.sin(math.pi * clamp((u - 0.1) / 0.8))
        P["armR"] = lin(-38, 8, u) + 150 * stretch
        P["armL"] = lin(-52, 8, u) + 140 * stretch
        P["legR_lift"], P["legL_lift"] = lin(70, 0, u), lin(76, 0, u)
        P["legR"], P["legL"] = lin(-34, 0, u), lin(34, 0, u)
        P["tail"] = lin(62, 10, u)
        P["mouth"] = 0.95 * math.sin(math.pi * clamp((u - 0.12) / 0.55))
        P["eyes"] = "sleep" if u < 0.3 else ("sly" if u < 0.75 else "open")
        P["sy"] = 1.0 + 0.02 * stretch
        P["bob"] = 0.0
        xw, yw = lin(sx0, 400, u), lin(GROUND - 92, GROUND, u)
        draw_char(img, "cat", P, xw, yw)
        HEADS["cat"] = (xw + (1 - u) * ln * 0.85, lin(GROUND - 170, GROUND + (rgc.head_top - rgc.ground_y) * rgc.k, u))
        if u < 0.6:
            Q.zzz(sd, sx0 + ln * 0.95, GROUND - 190, t)
    elif C["mode"] == "sleep":
        P = cat_pose(C, t, f)
        P["lean"] = -86
        draw_char(img, "cat", P, sx0, GROUND - 92)
        Q.zzz(sd, sx0 + ln * 0.95, GROUND - 190, t)
        HEADS["cat"] = (sx0 + ln * 0.85, GROUND - 170)
    elif C["mode"] == "stand":
        P = cat_pose(C, t, f)
        P["tt"] = t
        yoff = C["yoff"] * (0.62 if C["yoff"] < -200 else 1.0)
        yw = GROUND + yoff
        draw_char(img, "cat", P, C["x"], yw, tint=P.get("tint", 0.0))
        draw_props(img, sd, "cat", P, C["x"], yw)
        rg = R.get("cat")
        HEADS["cat"] = (C["x"], yw + (rg.head_top - rg.ground_y) * rg.k)
    elif C["mode"] == "rot":
        P = cat_pose(C, t, f)
        P["tt"] = t
        draw_char(img, "cat", P, 0, 0, center_rot=(C["angle"], C["center"]))
        HEADS["cat"] = (C["center"][0], C["center"][1] - 100)
    if sack_front:
        K.flour_sack(sd, t >= 25.2)
    if not Mo["st"].get("behind"):
        mouse()
    if G["mode"] != "hidden":
        P = dadi_pose(G, t, f)
        P["tt"] = t
        draw_char(img, "dadi", P, G["x"], GROUND)
        draw_props(img, sd, "dadi", P, G["x"], GROUND)
        rg = R.get("dadi")
        HEADS["dadi"] = (G["x"], GROUND + (rg.head_top - rg.ground_y) * rg.k)
    Q.flour_puffs(sd, t)
    if 69.5 <= t < 72.0:
        K.fight_cloud(sd, 680 + 20 * math.sin(t * 7), 540, t)
    if t >= 92.6:
        Q.hearts(sd, 490, 430, t)
    if 23.0 <= t < 24.0:
        sd.text((Mo["x"], Mo["y"] - 120), "!", 44, (255, 230, 40), stroke=5)
    return img, C, Mo, D, G


def anchor(who, C, Mo, D, G):
    return HEADS.get(who, (640, 300))


# ---------------------------------------------------------------- cards, title, end
def neutral(name, t, face="open", talk=False, pose=None):
    P = dict(armR=8, armL=8, tilt=3 * math.sin(t * 2), bob=0.0, tail=10 * math.sin(t * 3), look=0.0, props=[],
             eyes=face, mouth=(0.4 + 0.5 * abs(math.sin(t * 15))) if talk else 0.0)
    if name == "dog":
        P["armR"] = P["armL"] = 3
    if pose == "hero":
        P.update(armR=150, armL=14)
    if pose == "broom":
        P.update(armR=156, armL=20, props=[("broom", "up")])
    return P


def char_big(name, P, target_h, t):
    rig = R.get(name)
    S = target_h / (rig.ground_y - rig.head_top)
    im, g, _ = rig.compose(P, S)
    fin, gg = R.finish(im, g, P)
    bb = fin.getbbox()
    return fin.crop(bb), (gg[0] - bb[0], gg[1] - bb[1])


def make_card(i):
    names = ["cat", "mouse", "dog", "dadi"]
    name = names[i]
    who = ["cat", "mouse", "dog", "dadi"][i]
    q = Q.CAST[i]
    color = Q.R.NAMES[who][1]
    bg = Q.R.gradient(tuple(int(c * 0.5) for c in color), (14, 10, 10))

    def render(t, f):
        img = bg.copy()
        d = ImageDraw.Draw(img)
        d.text((W / 2, 40), f"MEET THE CAST   {i + 1} / 4", font=font("Inter-Black.otf", 26), fill=(230, 230, 230), anchor="mm")
        talk = (f // 3) % 2 == 0 and 0.6 < t < 2.4
        pose = {"cat": "hero", "dog": None, "mouse": None, "dadi": "broom"}[name]
        face = "angry" if (name in ("dog",) and t > 1.8) else "open"
        if name == "dog" and t < 1.8:
            face = "sleep"
        P = neutral(name, t, face, talk, pose if t > 1.8 or name == "cat" else None)
        crop, g = char_big(name, P, 560 if name != "mouse" else 470, t)
        x = lin(-300, 330, ease(t / 0.5))
        img.paste(crop, (int(x - g[0]), int(690 - g[1] + 4 * math.sin(t * 3))), crop)
        d = ImageDraw.Draw(img)
        tx = lin(W + 60, 620, ease((t - 0.1) / 0.5))
        nm = q[1]
        d.text((tx, 200), nm, font=font("Inter-Black.otf", 56), fill=(255, 255, 255), stroke_width=3, stroke_fill=OL)
        d.text((tx, 278), q[2], font=font("Inter-Bold.otf", 34), fill=tuple(min(255, c + 80) for c in color))
        y = 360
        for txt in (q[3], q[4]):
            for l in Q.R.wrap(txt, font("Inter-SemiBold.otf", 29), 600):
                d.text((tx, y), l, font=font("Inter-SemiBold.otf", 29), fill=(240, 240, 240))
                y += 40
            y += 22
        return img
    return render


_TBG = None


def render_title(t, f):
    global _TBG
    if _TBG is None:
        _TBG = Image.blend(K.kitchen(1).filter(ImageFilter.GaussianBlur(6)), Image.new("RGB", (W, H), (30, 10, 0)), 0.5)
    img = _TBG.copy()
    d = ImageDraw.Draw(img)
    z = 0.6 + 0.4 * ease(t / 0.8)
    d.text((W / 2, 130), "THE GREAT", font=font("Inter-Black.otf", int(80 * z)), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(200, 60, 20))
    d.text((W / 2, 230), "LADDOO HEIST", font=font("Inter-Black.otf", int(118 * z)), fill=(255, 190, 40), anchor="mm", stroke_width=8, stroke_fill=OL)
    if t > 1.0:
        d.text((W / 2, 322), "An original cat & mouse comedy", font=font("Inter-SemiBold.otf", 32), fill=(255, 240, 220), anchor="mm")
    u = t / Q.TITLE
    mx = lin(-160, 1500, u * 1.15)
    ph = mx / 60
    for name, dx, ty in (("mouse", 0, 470), ("cat", -430, 230)):
        P = dict(armR=8, armL=8, tilt=0, bob=0.0, props=[], eyes="open" if name == "mouse" else "angry", mouth=0.0,
                 look=7, tail=18 * math.sin(t * 20))
        gait(P, name, ph, 1.0, "run", 120, True, True, 55)
        if name == "mouse":
            P.update(armR=168, armL=168, eyes="wide")
        P["lean"] = -9
        rig = R.get(name)
        S = (140 if name == "mouse" else 250) / (rig.ground_y - rig.head_top)
        im, g, _ = rig.compose(P, S)
        fin, gg = R.finish(im, g, P)
        img.paste(fin, (int(mx + dx - gg[0]), int(690 - gg[1])), fin)
    return img


def render_end(t, f):
    img = Q.R.gradient((70, 30, 10), (12, 8, 6))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 105), "THE END", font=font("Inter-Black.otf", 110), fill=(255, 200, 50), anchor="mm", stroke_width=7, stroke_fill=OL)
    d.text((W / 2, 215), "MORAL OF THE STORY", font=font("Inter-Bold.otf", 26), fill=(220, 200, 180), anchor="mm")
    for k, l in enumerate(("Greed gets you the broom...", "sharing gets you the laddoos!")):
        d.text((W / 2, 272 + k * 54), l, font=font("Inter-BoldItalic.otf", 42), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, 400), "Starring: TUBBY BILLA  -  CHHOTU  -  SHERU  -  DADI", font=font("Inter-SemiBold.otf", 22), fill=(220, 210, 200), anchor="mm")
    d.text((W / 2, 432), "All characters are original.", font=font("Inter-Regular.otf", 18), fill=(170, 160, 150), anchor="mm")
    for name, x, face, h in (("dog", 400, "happy", 190), ("mouse", 640, "happy", 120), ("cat", 880, "dizzy", 200)):
        P = neutral(name, t, face, False)
        if name == "cat":
            P["tilt"] = -10
        crop, g = char_big(name, P, h, t)
        img.paste(crop, (int(x - g[0]), int(700 - g[1])), crop)
    return img


SEGS = None
NFR = 0


# ---------------------------------------------------------------- cinematography
class Fx:
    """Camera x that follows a character."""
    def __init__(self, name, off=0.0):
        self.name, self.off = name, off


class Fy:
    def __init__(self, name, off=0.0):
        self.name, self.off = name, off


def _pos(name, t):
    if name == "cat":
        C = Q.cat_state(t, 0)
        if C["mode"] == "sleep":
            return (400, GROUND - 100)
        if C["mode"] == "rot":
            return tuple(C["center"])
        return (C["x"], GROUND + C["yoff"] * 0.62 - 190)
    if name == "mouse":
        M = Q.mouse_state(t, 0)
        if M["mode"] == "hidden":
            return (110, Q.WALL - 40)
        return (M["x"], M["y"] + M["yoff"] - 60)
    if name == "dog":
        D = Q.dog_state(t, 0)
        return (D["x"] if D["mode"] != "hidden" else 560, GROUND - 150)
    G = Q.dadi_state(t, 0)
    return (G["x"] if G["mode"] != "hidden" else 1000, GROUND - 240)


def _follow(name, axis, t, off):
    n = 7
    ts = [max(0.0, t - 0.55 * i / (n - 1)) for i in range(n)]
    vals = [_pos(name, tt)[0 if axis == "x" else 1] for tt in ts]
    w = [1.0 + 0.4 * i for i in range(n)][::-1]
    return sum(v * wi for v, wi in zip(vals, w)) / sum(w) + off


def _ev(v, t, axis):
    if isinstance(v, Fx):
        return _follow(v.name, "x", t, v.off)
    if isinstance(v, Fy):
        return _follow(v.name, "y", t, v.off)
    return v


# (story time, centre x, centre y, zoom, dutch roll in degrees, 'cut' | 'ease')
CAM_KEYS = [
    (0.0, 640, 360, 1.00, 0, "cut"), (4.3, 700, 390, 1.10, 0, "ease"),                          # establishing push-in
    (4.4, Fx("dadi", -10), 400, 1.40, 0, "cut"), (7.4, Fx("dadi", -10), 395, 1.52, 0, "ease"),   # Dadi speaks
    (7.5, 430, 560, 1.65, -2.5, "cut"), (9.1, 430, 556, 1.52, -2.5, "ease"),                     # sleeping cat, low angle
    (9.2, 640, 370, 1.02, 0, "cut"), (11.7, 660, 372, 1.08, 0, "ease"),
    (11.9, 235, 520, 1.70, 0, "cut"), (13.2, 235, 520, 1.70, 0, "ease"),                         # mouse peeks out
    (13.3, Fx("mouse", 90), 520, 1.35, 0, "cut"), (15.5, Fx("mouse", 90), 520, 1.35, 0, "ease"),  # tracks him across the floor
    (15.6, Fx("mouse", 60), Fy("mouse", -30), 1.55, 0, "cut"), (19.1, Fx("mouse", 0), Fy("mouse", -40), 1.55, 0, "ease"),
    (19.2, 440, 470, 1.18, 0, "cut"), (20.5, Fx("cat", 20), 430, 1.38, 2, "ease"),               # the cat wakes
    (21.0, Fx("cat", 30), 430, 1.35, 1.5, "cut"), (22.9, Fx("cat", 30), 430, 1.35, 1.5, "ease"),
    (23.2, Fx("cat", 90), 450, 1.15, -1.5, "cut"),                                              # the chase
    (26.4, Fx("mouse", 40), 520, 1.50, 0, "cut"),
    (28.6, 640, 400, 1.05, 0, "cut"),
    (30.0, Fx("cat", 60), 450, 1.20, 2.0, "cut"),
    (33.3, 700, 430, 1.05, 0, "cut"),
    (35.5, Fx("mouse", -60), 520, 1.35, 0, "cut"),
    (38.6, Fx("cat", -20), 440, 1.20, 0, "cut"),                                                # the trap plan
    (41.0, 230, 560, 1.50, 0, "cut"), (44.0, 230, 560, 1.50, 0, "ease"),
    (44.1, 200, 590, 1.70, 0, "cut"), (47.5, 215, 585, 1.62, 0, "ease"),
    (47.6, 240, 560, 1.45, 0, "cut"),
    (48.2, Fx("mouse", 130), 540, 1.20, 0, "cut"),
    (51.0, Fx("cat", 0), 470, 1.50, 0, "cut"),
    (52.3, 640, 300, 1.12, -3, "cut"), (55.3, 640, 300, 1.12, -3, "ease"),                       # up at the ceiling fan
    (55.4, 820, 420, 1.10, 0, "cut"),
    (56.8, 700, 400, 1.06, 0, "cut"),                                                           # never wake a sleeping dog
    (60.6, 1040, 520, 1.25, 0, "cut"), (62.4, 1060, 470, 1.70, 3, "ease"),
    (62.7, 1000, 500, 1.30, 3, "cut"),
    (63.4, Fx("cat", 0), 470, 1.50, -2, "cut"),
    (65.5, 640, 400, 1.05, 0, "cut"),
    (65.7, Fx("cat", 150), 440, 1.10, 2, "cut"),                                                # kitchen chaos
    (67.6, Fx("cat", 100), 440, 1.10, -2, "cut"),
    (69.4, 680, 520, 1.30, 0, "cut"),
    (72.0, Fx("cat", 20), 440, 1.20, 0, "cut"),
    (74.0, Fx("cat", 0), 470, 1.50, -2.5, "cut"),
    (77.0, 640, 400, 1.05, 0, "cut"),
    (78.6, Fx("cat", 0), 470, 1.45, 0, "cut"),                                                  # Dadi returns
    (81.9, Fx("dadi", -60), 430, 1.40, 3, "cut"),
    (83.6, Fx("cat", 0), 470, 1.50, -2, "cut"),
    (85.6, Fx("cat", 0), 450, 1.05, 0, "cut"),
    (90.1, 640, 400, 1.00, 0, "cut"),                                                           # friends share laddoos
    (91.8, 520, 540, 1.40, 0, "cut"), (94.0, 500, 500, 1.30, 0, "ease"), (100.0, 500, 470, 1.12, 0, "ease"),
]
SHAKES = [(25.2, 8), (32.6, 12), (46.0, 6), (51.3, 10), (52.6, 8), (56.5, 14), (61.4, 12), (69.8, 8), (70.5, 9),
          (71.2, 10), (73.0, 13), (73.5, 8), (74.3, 12), (86.2, 9), (87.0, 9), (90.5, 10)]


def camera(t):
    keys = CAM_KEYS
    i = max(k for k in range(len(keys)) if keys[k][0] <= t)
    k0 = keys[i]
    nxt = keys[i + 1] if i + 1 < len(keys) else None

    def val(k):
        return (_ev(k[1], t, "x"), _ev(k[2], t, "y"), k[3], k[4])
    a = val(k0)
    if nxt is None or nxt[5] == "cut":
        cx, cy, z, roll = a
    else:
        u = ease((t - k0[0]) / max(1e-6, nxt[0] - k0[0]))
        b = val(nxt)
        cx, cy, z, roll = [lin(a[j], b[j], u) for j in range(4)]
    # impact shake and a light handheld drift
    amp = sum(A * math.exp(-(t - T) / 0.16) for T, A in SHAKES if T <= t < T + 0.9)
    sx = amp * math.sin(t * 71) + 1.4 * math.sin(t * 0.9) + 0.7 * math.sin(t * 2.3)
    sy = amp * 0.8 * math.cos(t * 57) + 1.1 * math.sin(t * 0.7 + 1)
    roll += 0.12 * math.sin(t * 1.3) + (amp * 0.05) * math.sin(t * 43)
    return cx, cy, z, roll, sx, sy


_VIG = None


def vignette(img):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
        _VIG = Image.fromarray(np.clip((d - 0.62) * 120, 0, 90).astype(np.uint8), "L")
    img.paste(Image.new("RGB", (W, H), (14, 8, 6)), (0, 0), _VIG)


def render_story(t, f):
    world, C, Mo, D, G = render_world(t, f)
    cx, cy, z, roll, sx, sy = camera(t)
    infl = 1 + 0.022 * abs(roll) + 0.012
    vw, vh = W / z * infl, H / z * infl
    cx = clamp(cx, vw / 2, W - vw / 2) + sx
    cy = clamp(cy, vh / 2, H - vh / 2) + sy
    s = X / z
    th = math.radians(roll)
    c, sn = math.cos(th), math.sin(th)
    coeffs = (s * c, -s * sn, cx * X - s * (c * 640 - sn * 360), s * sn, s * c, cy * X - s * (sn * 640 + c * 360))
    img = world.transform((W, H), Image.AFFINE, coeffs, resample=Image.BICUBIC)

    def to_screen(p):
        rx, ry = (p[0] - cx) * z, (p[1] - cy) * z
        return (640 + c * rx + sn * ry, 360 - sn * rx + c * ry)
    d = ImageDraw.Draw(img)
    for t0, word, p, color, *rest in Q.WORDS:
        if t0 <= t < t0 + (rest[0] if rest else 1.0):
            u = seg(t, t0, t0 + 0.15)
            size = int(lin(30, 84, u) + 6 * math.sin(t * 30) * (1 - seg(t, t0, t0 + 0.6)))
            fnt = font("Inter-Black.otf", size)
            half = fnt.getlength(word) / 2 + 12
            x, y = to_screen(p)
            d.text((clamp(x, half, W - half), clamp(y, 70, H - 120)), word, font=fnt, fill=color, anchor="mm", stroke_width=7, stroke_fill=OL)
    for s_, e, who, kind, txt in Q.BUBBLES:
        if s_ <= t < e:
            hx, hy = to_screen(anchor(who, C, Mo, D, G))
            Q.R.bubble(img, who, kind, txt, clamp(hx, 60, W - 60), clamp(hy, 120, H - 40))
    for t0, cap in Q.CAPTIONS:
        if t0 <= t < t0 + 3.2:
            a = min(seg(t, t0, t0 + 0.3), 1 - seg(t, t0 + 2.8, t0 + 3.2))
            fnt = font("Inter-Black.otf", 26)
            w = fnt.getlength(cap) + 44
            y = H - 58 + (1 - a) * 70
            d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 44), 22, fill=(40, 20, 10), outline=(255, 190, 40), width=3)
            d.text((W / 2, y + 22), cap, font=fnt, fill=(255, 215, 90), anchor="mm")
    vignette(img)
    if t > 96.3:
        a = seg(t, 96.3, 96.9)
        ImageDraw.Draw(img).text((W / 2, 110 - (1 - a) * 80), "THE END", font=font("Inter-Black.otf", 110), fill=(255, 215, 60),
                                 anchor="mm", stroke_width=8, stroke_fill=OL)
    return img


def _frame(fr):
    t = fr / Q.FPS
    si = 0
    while si < len(SEGS) - 1 and t >= SEGS[si][0] + SEGS[si][1]:
        si += 1
    t0, dur, fn = SEGS[si]
    lt = t - t0
    img = fn(lt, fr).convert("RGB")
    fade = max(clamp(1 - lt / 0.3), clamp(1 - (dur - lt) / 0.3))
    if fade > 0:
        img = Image.blend(img, Image.new("RGB", (W, H)), fade)
    return img.tobytes()


def main():
    global SEGS, NFR
    import subprocess
    from multiprocessing import Pool
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "great_laddoo_heist_v2.mp4")
    Q.render_story = render_story
    Q.render_world = render_world
    Q.anchor = anchor
    Q.make_card = make_card
    Q.render_title = render_title
    Q.render_end = render_end
    out = os.path.abspath(out)
    SEGS, total = Q.timeline()
    wav = out + ".wav"
    Q.build_audio(wav, SEGS[-2][0], total)
    NFR = int(total * Q.FPS)
    print(f"Rendering {NFR} frames ({total:.1f}s) on 4 workers...", flush=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(Q.FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k",
                           "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, data in enumerate(pool.imap(_frame, range(NFR), chunksize=6)):
            ff.stdin.write(data)
            if i % 240 == 0:
                print(f"  frame {i}/{NFR}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print("Done:", out)


if __name__ == "__main__":
    main()
