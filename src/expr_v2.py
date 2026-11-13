"""Expression variants (eyes, mouths) for the detailed characters."""
import math

from charart import OL, ell, spline
import cat_v2, mouse_v2, dog_v2, dadi_v2

STATE_KW = {"open": {}, "wide": dict(ys=1.2, pup=0.6, brow=-0.8), "angry": dict(lid=1.0, brow=1.0),
            "sly": dict(lid=0.55, brow=0.55), "worried": dict(brow=-0.6)}
EYE_CFG = {   # module, eye centres with inward sign, half width, call(cv, cx, s, **kw)
    "cat": (cat_v2, ((-42, 1), (42, -1)), 24, lambda cv, cx, s, kw: cat_v2._eye(cv, cx, 0, s, **kw)),
    "mouse": (mouse_v2, ((-32, 1), (32, -1)), 18, lambda cv, cx, s, kw: mouse_v2._eye(cv, cx, s, **kw)),
    "dog": (dog_v2, ((-44, 1), (44, -1)), 20, lambda cv, cx, s, kw: dog_v2._eye(cv, cx, s, **kw)),
}


def _spiral(cv, cx, r):
    pts = []
    for i in range(40):
        a = i * 0.55
        rr = r * (0.15 + 0.85 * i / 40)
        pts.append((cx + rr * math.cos(a), rr * math.sin(a)))
    cv.line(pts, 1.8, (60, 40, 70))


def eyes_fn(char, state):
    if char == "dadi":
        return lambda cv: dadi_v2.eyes(cv, state)
    mod, centres, w, call = EYE_CFG[char]

    def fn(cv):
        for i, (cx, s) in enumerate(centres):
            st = state
            if state == "wink":
                st = "closed" if i == 0 else "open"
            if st in ("closed", "sleep"):
                cv.line([(cx - w, 2), (cx, 9 if st == "sleep" else 8), (cx + w, 2)], 4.2)
                cv.line([(cx + s * w, 3), (cx + s * (w + 8), 8)], 2.2)
                cv.line([(cx + s * (w - 6), 6), (cx + s * (w + 4), 14)], 2.0)
            elif st == "happy":
                cv.line([(cx - w + 2, 8), (cx, -9), (cx + w - 2, 8)], 4.6)
            elif st == "dizzy":
                e = ell(cx, 0, w * 0.9, w * 0.9, 0, 48)
                cv.paint(cv.mask(e), (250, 250, 255))
                cv.outline(e, 2.2)
                _spiral(cv, cx, w * 0.8)
            else:
                call(cv, cx, s, STATE_KW.get(st, {}))
        return []
    return fn


def variant_spec(char, base_spec, key):
    """('eyes:angry') -> spec tuple with the matching draw function."""
    name, _, state = key.partition(":")
    fn, w, h, cx, cy = base_spec["eyes"]
    return (eyes_fn(char, state), w, h, cx, cy)
