"""Cut-out animation rigs for the detailed characters.

Arms and legs are two-bone chains solved with inverse kinematics, so elbows and knees really bend and feet
stay planted while the body sways. Faces swap expressions and heads tilt.
"""
import math

from PIL import Image

from charart import Cv
from kitchen_art import ik
import expr_v2
import cat_v2, mouse_v2, dog_v2, dadi_v2

_PART_CACHE = {}
_XF_CACHE = {}


def part_image(char, spec, key, S):
    ck = (char, key, round(S, 3))
    if ck not in _PART_CACHE:
        fn, w, h, cx, cy = spec[key]
        cv = Cv(w, h, S, cx, cy)
        fn(cv)
        ox, oy = cv.P(0, 0)
        _PART_CACHE[ck] = (cv.im, ox, oy)
    return _PART_CACHE[ck]


def xform(im, ox, oy, sx, sy, ang, ck):
    key = (ck, im.size, round(sx, 2), round(sy, 2), round(ang))
    hit = _XF_CACHE.get(key)
    if hit is not None:
        return hit
    if abs(sx - 1) > 0.005 or abs(sy - 1) > 0.005:
        im = im.resize((max(1, round(im.width * sx)), max(1, round(im.height * sy))), Image.BILINEAR)
        ox, oy = ox * sx, oy * sy
    if round(ang) != 0:
        R = math.hypot(max(ox, im.width - ox), max(oy, im.height - oy))
        side = int(math.ceil(2 * R)) + 2
        big = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        big.paste(im, (int(side / 2 - ox), int(side / 2 - oy)))
        im = big.rotate(round(ang), resample=Image.BICUBIC)
        ox = oy = side / 2
    if len(_XF_CACHE) > 4000:
        _XF_CACHE.clear()
    _XF_CACHE[key] = (im, ox, oy)
    return im, ox, oy


def rot(v, a):
    """Rotate vector (screen coords, y down) counter-clockwise on screen by a degrees."""
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    return (v[0] * c + v[1] * s, -v[0] * s + v[1] * c)


def seg_angle(a, b):
    """Rotation (PIL, ccw degrees) that turns a part drawn pointing straight down so it points from a to b."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


class Rig:
    def __init__(self, name, mod, k, parts, groups, chains, ground_y, box, head_top, leg_len=0):
        self.name, self.mod, self.k = name, mod, k
        self.parts, self.groups, self.chains = parts, groups, chains
        self.ground_y, self.box, self.head_top, self.leg_len = ground_y, box, head_top, leg_len
        self.spec = dict(mod.SPEC)
        self.S = 2.0 * k

    def spec_for(self, key):
        if key not in self.spec:
            if key.startswith("eyes:"):
                self.spec[key] = expr_v2.variant_spec(self.name, self.mod.SPEC, key)
            else:
                raise KeyError(key)
        return self.spec[key]

    # ---- limb chains (two-bone IK)
    def solve(self, P, ch):
        """Return (root, elbow, end) in character space for chain ch under pose P."""
        sx, bob = P.get("sway", 0.0), P.get("bob", 0.0)
        px, py = ch["pivot"]
        s = ch["side"]
        L = ch["l1"] + ch["l2"]
        if ch["kind"] == "arm":
            root = (px + sx, py + bob)
            reach = P.get(ch["param"] + "_r", ch["reach"])
            v = rot((0, L * reach), P.get(ch["param"], 0.0))
            target = (root[0] + s * v[0], root[1] + v[1])
        else:  # leg: the foot stays on the ground while the hip moves with the body
            root = (px + sx, py + bob)
            lift = P.get(ch["param"] + "_lift", 0.0)
            v = rot((0, L * ch["reach"] - lift), P.get(ch["param"], 0.0))
            target = (px + s * v[0], py + v[1])
        j1 = ik(root, target, ch["l1"], ch["l2"], 1)
        j2 = ik(root, target, ch["l1"], ch["l2"], -1)
        elbow = j1 if s * (j1[0] - root[0]) >= s * (j2[0] - root[0]) else j2
        d = math.hypot(target[0] - root[0], target[1] - root[1])
        if d >= L:   # fully stretched: the end sits on the straight line
            k = L / d
            target = (root[0] + (target[0] - root[0]) * k, root[1] + (target[1] - root[1]) * k)
        return root, elbow, target

    def end_pos(self, P, chain_name):
        for ch in self.chains:
            if ch["name"] == chain_name:
                return self.solve(P, ch)
        raise KeyError(chain_name)

    def compose(self, P, S=None):
        S = S or self.S
        w, h, cx, cy = self.box
        char = Cv(w, h, S, cx, cy)
        bob = P.get("bob", 0.0)
        look = P.get("look", 0.0)
        jobs = []

        def paste(key, pos, ang, mir, z, ck, sx=1.0, sy=1.0, rotmul_key=None):
            jobs.append((z, key, pos, ang, mir, ck, sx, sy))

        for (key, pos, z, mir, base, grp, *extra) in self.parts:
            opt = extra[0] if extra else {}
            if key == "mouth" and P.get("mouth", 0.0) <= 0.02:
                continue
            if key == "eyes":
                key = "eyes:" + P.get("eyes", "open")
            ang = base
            sx = sy = 1.0
            px, py = pos
            g = self.groups.get(grp)
            if g:
                pivot, param, sign = g
                a = P.get(param, 0.0) * sign
                v = (pos[0] - pivot[0], pos[1] - pivot[1])
                rv = rot(v, a)
                px, py = pivot[0] + rv[0], pivot[1] + rv[1]
                ang += a * opt.get("rotmul", 1.0)
            if grp == "head" and key.split(":")[0] in ("eyes", "muzzle_asm", "snout_asm", "face", "mouth"):
                px += look
            if key == "mouth":
                sc = opt.get("sc", 0.5) * (0.5 + 0.5 * P.get("mouth", 0.0))
                sx = sy = sc
            if grp in ("legR", "legL"):
                py -= P.get(grp + "_lift", 0.0)
            px += P.get("sway", 0.0)
            py += bob
            jobs.append((z, key, (px, py), ang, mir, (self.name, key, mir), sx, sy))
        for ch in self.chains:
            root, elbow, end = self.solve(P, ch)
            mir = ch["side"] < 0
            a_up, a_lo = seg_angle(root, elbow), seg_angle(elbow, end)
            z = ch["z"]
            jobs.append((z, ch["up"], root, a_up, mir, (self.name, ch["up"], mir), 1.0, 1.0))
            jobs.append((z + 0.05, ch["lo"], elbow, a_lo, mir, (self.name, ch["lo"], mir), 1.0, 1.0))
            for ekey, off, ez, ratio in ch["ends"]:
                ang = a_lo * ratio
                jobs.append((ez, ekey, (end[0] + off[0], end[1] + off[1]), ang, mir, (self.name, ekey, mir), 1.0, 1.0))
        for (z, key, pos, ang, mir, ck, sx, sy) in sorted(jobs, key=lambda j: j[0]):
            spec = self.spec_for(key)
            im, ox, oy = part_image(self.name, self.spec, key, S)
            if mir:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
                ox = im.width - ox
            im2, ox2, oy2 = xform(im, ox, oy, sx, sy, ang, ck)
            X, Y = char.P(pos[0], pos[1])
            char.im.alpha_composite(im2, (int(round(X - ox2)), int(round(Y - oy2))))
        return char.im, char.P(0, self.ground_y), char


def finish(im, g, P, tint=0.0):
    sx, sy = P.get("sx", 1.0), P.get("sy", 1.0)
    lean = P.get("lean", 0.0)
    gx, gy = g
    if abs(sx - 1) > 0.004 or abs(sy - 1) > 0.004:
        im = im.resize((int(im.width * sx), int(im.height * sy)), Image.BILINEAR)
        gx, gy = gx * sx, gy * sy
    if abs(lean) > 0.3:
        R = math.hypot(max(gx, im.width - gx), max(gy, im.height - gy))
        side = int(2 * R) + 2
        big = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        big.paste(im, (int(side / 2 - gx), int(side / 2 - gy)))
        im = big.rotate(lean, resample=Image.BICUBIC)
        gx = gy = side / 2
    if tint > 0:
        import numpy as np
        a = np.array(im)
        rgb = a[..., :3].astype(np.float32)
        bright = rgb.max(axis=2)
        w = np.clip((bright - 55) / 60.0, 0, 1)[..., None] * tint       # keep the dark outlines so he stays solid
        shade = (0.86 + 0.14 * bright / 255.0)[..., None]                  # a little shading survives under the flour
        a[..., :3] = (rgb * (1 - w) + np.array([246, 246, 250]) * shade * w).astype(np.uint8)
        im = Image.fromarray(a, "RGBA")
    return im, (gx, gy)


# ------------------------------------------------------------------ rig definitions
def chain(name, param, pivot, side, l1, l2, up, lo, z, kind, ends, reach):
    return dict(name=name, param=param, pivot=pivot, side=side, l1=l1, l2=l2, up=up, lo=lo, z=z, kind=kind, ends=ends, reach=reach)


def _cat():
    P = [("tail", (-56, 96), 0, False, 0, "tail"),
         ("torso", (0, 30), 2, False, 0, "root"),
         ("ear", (52, -130), 4, False, -16, "head"), ("ear", (-52, -130), 4, True, 16, "head"),
         ("head", (0, -72), 5, False, 0, "head"),
         ("eyes", (0, -86), 6, False, 0, "head"), ("muzzle_asm", (0, -44), 6, False, 0, "head"),
         ("mouth", (0, -30), 6.5, False, 0, "head", {"sc": 0.62})]
    G = {"tail": ((-56, 96), "tail", 1), "head": ((0, -24), "tilt", 1)}
    C = [chain("armR", "armR", (70, -24), 1, 46, 46, "arm_up", "arm_lo", 3, "arm", [("glove", (0, 0), 4, 0.9)], 0.93),
         chain("armL", "armL", (-70, -24), -1, 46, 46, "arm_up", "arm_lo", 3, "arm", [("glove", (0, 0), 4, 0.9)], 0.93),
         chain("legR", "legR", (30, 112), 1, 50, 50, "leg_up", "leg_lo", 1, "leg", [("foot", (0, 0), 1.3, 0.2)], 0.985),
         chain("legL", "legL", (-30, 112), -1, 50, 50, "leg_up", "leg_lo", 1, "leg", [("foot", (0, 0), 1.3, 0.2)], 0.985)]
    return Rig("cat", cat_v2, 1.08, P, G, C, 247, (640, 720, 0, 20), -150, leg_len=100)


def _mouse():
    P = [("tail", (36, 70), 0, False, 0, "tail"),
         ("body", (0, 20), 2, False, 0, "root"),
         ("ear", (56, -100), 4, False, 0, "head"), ("ear", (-56, -100), 4, True, 0, "head"),
         ("head", (0, -62), 5, False, 0, "head"),
         ("eyes", (0, -68), 6, False, 0, "head"), ("snout_asm", (0, -52), 6, False, 0, "head"),
         ("mouth", (0, -26), 6.5, False, 0, "head", {"sc": 0.5}),
         ("cap", (0, -118), 7, False, 0, "head")]
    G = {"tail": ((36, 70), "tail", 1), "head": ((0, -20), "tilt", 1)}
    C = [chain("armR", "armR", (46, -14), 1, 26, 26, "arm_up", "arm_lo", 3, "arm", [("paw", (0, 0), 4, 0.9)], 0.93),
         chain("armL", "armL", (-46, -14), -1, 26, 26, "arm_up", "arm_lo", 3, "arm", [("paw", (0, 0), 4, 0.9)], 0.93),
         chain("legR", "legR", (16, 82), 1, 25, 25, "leg_up", "leg_lo", 1, "leg", [("foot", (0, 0), 1.3, 0.2)], 0.985),
         chain("legL", "legL", (-16, 82), -1, 25, 25, "leg_up", "leg_lo", 1, "leg", [("foot", (0, 0), 1.3, 0.2)], 0.985)]
    return Rig("mouse", mouse_v2, 0.56, P, G, C, 154, (520, 560, 0, 0), -170, leg_len=50)


def _dog():
    P = [("tail", (92, 130), 0, False, 0, "tail"),
         ("hind_leg", (84, 96), 1, False, 0, "legR"), ("hind_leg", (-84, 96), 1, True, 0, "legL"),
         ("body", (0, 56), 2, False, 0, "root"),
         ("ear", (82, -64), 4, False, 0, "head"), ("ear", (-82, -64), 4, True, 0, "head"),
         ("head", (0, -66), 5, False, 0, "head"),
         ("eyes", (0, -80), 6, False, 0, "head"), ("snout_asm", (0, -38), 6, False, 0, "head"),
         ("mouth", (0, 6), 6.5, False, 0, "head", {"sc": 0.7}),
         ("collar", (0, 2), 7, False, 0, "head")]
    G = {"tail": ((92, 130), "tail", 1), "legR": ((84, 96), "legR", 1), "legL": ((-84, 96), "legL", -1),
         "head": ((0, -6), "tilt", 1)}
    C = [chain("armR", "armR", (42, 24), 1, 58, 58, "front_up", "front_lo", 3, "arm", [], 0.992),
         chain("armL", "armL", (-42, 24), -1, 58, 58, "front_up", "front_lo", 3, "arm", [], 0.992)]
    return Rig("dog", dog_v2, 0.98, P, G, C, 184, (560, 620, 0, 20), -150)


def _dadi():
    P = [("foot_one", (26, 244), 0, False, 0, "legR"), ("foot_one", (-26, 244), 0, True, 0, "legL"),
         ("saree", (0, 60), 1, False, 0, "root"), ("pallu", (-4, 16), 2, False, 0, "root"),
         ("head", (0, -144), 5, False, 0, "head"),
         ("face", (0, -144), 5.5, False, 0, "head"), ("eyes", (0, -152), 6, False, 0, "head"),
         ("mouth", (0, -100), 6.5, False, 0, "head", {"sc": 0.85})]
    G = {"legR": ((26, 244), "legR", 1), "legL": ((-26, 244), "legL", -1), "head": ((0, -76), "tilt", 1)}
    C = [chain("armR", "armR", (68, -46), 1, 50, 50, "arm_up", "arm_lo", 3, "arm", [("hand", (0, 0), 4, 0.9)], 0.94),
         chain("armL", "armL", (-68, -46), -1, 50, 50, "arm_up", "arm_lo", 3, "arm", [("hand", (0, 0), 4, 0.9)], 0.94)]
    return Rig("dadi", dadi_v2, 1.00, P, G, C, 271, (700, 760, 0, 20), -240)


RIGS = {}


def get(name):
    if name not in RIGS:
        RIGS[name] = {"cat": _cat, "mouse": _mouse, "dog": _dog, "dadi": _dadi}[name]()
    return RIGS[name]
