"""Cut-out animation rigs for the detailed characters: parts rotate about their joints, faces swap expressions."""
import math

from PIL import Image

from charart import Cv
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
    """Scale about the origin pixel, then rotate about it (ang in degrees, counter-clockwise). Cached."""
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


class Rig:
    def __init__(self, name, mod, k, parts, groups, ground_y, box, head_top, leg_len=0, eye_key="eyes"):
        self.name, self.mod, self.k = name, mod, k
        self.parts, self.groups = parts, groups
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

    def compose(self, P, S=None):
        """Draw the character for pose P. Returns (image, ground-point px)."""
        S = S or self.S
        w, h, cx, cy = self.box
        char = Cv(w, h, S, cx, cy)
        bob = P.get("bob", 0.0)
        look = P.get("look", 0.0)
        items = []
        for part in self.parts:
            items.append(part)
        for (key, pos, z, mir, base, grp, *extra) in sorted(items, key=lambda p: p[2]):
            opt = extra[0] if extra else {}
            if key == "eyes":
                key = "eyes:" + P.get("eyes", "open")
            if key == "mouth":
                amp = P.get("mouth", 0.0)
                if amp <= 0.02:
                    continue
            spec = self.spec_for(key)
            self.spec[key] = spec
            ck = (self.name, key)
            sS = S
            im, ox, oy = part_image(self.name, self.spec, key, sS)
            if mir:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
                ox = im.width - ox
            ang = base
            sx = sy = 1.0
            px, py = pos
            g = self.groups.get(grp)
            lift = 0.0
            if g:
                pivot, param, sign = g
                a = P.get(param, 0.0) * sign
                v = (pos[0] - pivot[0], pos[1] - pivot[1])
                if param in ("legR", "legL"):
                    lift = P.get(param + "_lift", 0.0)
                    if self.leg_len:
                        v = (v[0], v[1] - lift * (v[1] / max(1.0, self.leg_len)) if key not in ("leg",) else v[1])
                        if key == "leg":
                            sy = max(0.2, 1 - lift / self.leg_len)
                rv = rot(v, a)
                px, py = pivot[0] + rv[0], pivot[1] + rv[1]
                ang += a * opt.get("rotmul", 1.0)
            if grp == "head" and key in ("eyes", "muzzle_asm", "snout_asm", "face"):
                px += look
            if key == "mouth":
                sc = opt.get("sc", 0.5) * (0.5 + 0.5 * P.get("mouth", 0.0))
                sx = sy = sc
                px, py = pos
                if g:
                    v = (pos[0] - g[0][0], pos[1] - g[0][1])
                    rv = rot(v, P.get(g[1], 0.0) * g[2])
                    px, py = g[0][0] + rv[0], g[0][1] + rv[1]
                px += look
            if grp not in ("legR", "legL"):
                px += P.get("sway", 0.0)
            if grp != "feet_fixed":
                py += bob
            im2, ox2, oy2 = xform(im, ox, oy, sx, sy, ang, (self.name, key, mir))
            X, Y = char.P(px, py)
            char.im.alpha_composite(im2, (int(round(X - ox2)), int(round(Y - oy2))))
        return char.im, char.P(0, self.ground_y), char

    def world_point(self, P, local, S=None):
        """Character-space point after pose (for props): returns offset in units from the ground point."""
        return None


def finish(im, g, P, tint=0.0):
    """Apply whole-body squash/stretch and lean about the ground point, optional flour tint."""
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
        a[..., :3] = (a[..., :3] * (1 - tint) + np.array([246, 246, 250]) * tint).astype(np.uint8)
        im = Image.fromarray(a, "RGBA")
    return im, (gx, gy)


# ------------------------------------------------------------------ rig definitions
def _cat():
    P = [("tail", (-56, 96), 0, False, 0, "tail"),
         ("leg", (30, 112), 1, False, 0, "legR"), ("leg", (-30, 112), 1, True, 0, "legL"),
         ("foot", (34, 210), 1.2, False, 0, "legR", {"rotmul": 0.3}), ("foot", (-34, 210), 1.2, True, 0, "legL", {"rotmul": 0.3}),
         ("torso", (0, 30), 2, False, 0, "root"),
         ("arm", (70, -24), 3, False, 0, "armR"), ("arm", (-70, -24), 3, True, 0, "armL"),
         ("glove", (73, 68), 4, False, 0, "armR"), ("glove", (-73, 68), 4, True, 0, "armL"),
         ("ear", (52, -130), 4, False, -16, "head"), ("ear", (-52, -130), 4, True, 16, "head"),
         ("head", (0, -72), 5, False, 0, "head"),
         ("eyes", (0, -86), 6, False, 0, "head"), ("muzzle_asm", (0, -44), 6, False, 0, "head"),
         ("mouth", (0, -30), 6.5, False, 0, "head", {"sc": 0.62})]
    G = {"tail": ((-56, 96), "tail", 1), "legR": ((30, 112), "legR", 1), "legL": ((-30, 112), "legL", -1),
         "armR": ((70, -24), "armR", 1), "armL": ((-70, -24), "armL", -1), "head": ((0, -24), "tilt", 1)}
    return Rig("cat", cat_v2, 1.08, P, G, 247, (640, 720, 0, 20), -150, leg_len=98)


def _mouse():
    P = [("tail", (36, 70), 0, False, 0, "tail"),
         ("leg", (16, 82), 1, False, 0, "legR"), ("leg", (-16, 82), 1, True, 0, "legL"),
         ("foot", (20, 130), 1.2, False, 8, "legR", {"rotmul": 0.3}), ("foot", (-20, 130), 1.2, True, -8, "legL", {"rotmul": 0.3}),
         ("body", (0, 20), 2, False, 0, "root"),
         ("arm", (46, -14), 3, False, 0, "armR"), ("arm", (-46, -14), 3, True, 0, "armL"),
         ("paw", (49, 38), 4, False, 0, "armR"), ("paw", (-49, 38), 4, True, 0, "armL"),
         ("ear", (56, -100), 4, False, 0, "head"), ("ear", (-56, -100), 4, True, 0, "head"),
         ("head", (0, -62), 5, False, 0, "head"),
         ("eyes", (0, -68), 6, False, 0, "head"), ("snout_asm", (0, -52), 6, False, 0, "head"),
         ("mouth", (0, -26), 6.5, False, 0, "head", {"sc": 0.5}),
         ("cap", (0, -118), 7, False, 0, "head")]
    G = {"tail": ((36, 70), "tail", 1), "legR": ((16, 82), "legR", 1), "legL": ((-16, 82), "legL", -1),
         "armR": ((46, -14), "armR", 1), "armL": ((-46, -14), "armL", -1), "head": ((0, -20), "tilt", 1)}
    return Rig("mouse", mouse_v2, 0.56, P, G, 154, (520, 560, 0, 0), -170, leg_len=50)


def _dog():
    P = [("tail", (92, 130), 0, False, 0, "tail"),
         ("hind_leg", (84, 96), 1, False, 0, "legR"), ("hind_leg", (-84, 96), 1, True, 0, "legL"),
         ("body", (0, 56), 2, False, 0, "root"),
         ("front_leg", (42, 24), 3, False, 0, "armR"), ("front_leg", (-42, 24), 3, True, 0, "armL"),
         ("ear", (82, -64), 4, False, 0, "head", {"rotmul": 1.0}), ("ear", (-82, -64), 4, True, 0, "head"),
         ("head", (0, -66), 5, False, 0, "head"),
         ("eyes", (0, -80), 6, False, 0, "head"), ("snout_asm", (0, -38), 6, False, 0, "head"),
         ("mouth", (0, 6), 6.5, False, 0, "head", {"sc": 0.7}),
         ("collar", (0, 2), 7, False, 0, "head")]
    G = {"tail": ((92, 130), "tail", 1), "legR": ((84, 96), "legR", 1), "legL": ((-84, 96), "legL", -1),
         "armR": ((42, 24), "armR", 1), "armL": ((-42, 24), "armL", -1), "head": ((0, -6), "tilt", 1)}
    return Rig("dog", dog_v2, 0.98, P, G, 184, (560, 620, 0, 20), -150)


def _dadi():
    P = [("foot_one", (26, 244), 0, False, 0, "legR"), ("foot_one", (-26, 244), 0, True, 0, "legL"),
         ("saree", (0, 60), 1, False, 0, "root"), ("pallu", (-4, 16), 2, False, 0, "root"),
         ("arm", (68, -46), 3, False, 0, "armR"), ("arm", (-68, -46), 3, True, 0, "armL"),
         ("hand", (70, 54), 4, False, 0, "armR"), ("hand", (-70, 54), 4, True, 0, "armL"),
         ("head", (0, -144), 5, False, 0, "head"),
         ("face", (0, -144), 5.5, False, 0, "head"), ("eyes", (0, -152), 6, False, 0, "head"),
         ("mouth", (0, -100), 6.5, False, 0, "head", {"sc": 0.85})]
    G = {"legR": ((26, 244), "legR", 1), "legL": ((-26, 244), "legL", -1),
         "armR": ((68, -46), "armR", 1), "armL": ((-68, -46), "armL", -1), "head": ((0, -76), "tilt", 1)}
    return Rig("dadi", dadi_v2, 1.00, P, G, 271, (700, 760, 0, 20), -240)


RIGS = {}


def get(name):
    if name not in RIGS:
        RIGS[name] = {"cat": _cat, "mouse": _mouse, "dog": _dog, "dadi": _dadi}[name]()
    return RIGS[name]
