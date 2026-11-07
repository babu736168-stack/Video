#!/usr/bin/env python3
"""Animates the storyboard plates (the user's images) into out/work/concat.mp4 (1920x1080, 30 fps, no audio),
timed to out/timeline.json, plus out/work/images.json (when each image is on screen) for compose.py.

Motion per image: an eased camera move (push / pull / pan / slight roll), optional local warps
(breathing lungs, beating heart), glow pulses on the bright parts, drifting O2 / CO2 / energy particles,
handheld shake for the sprint. Images cross-dissolve into each other.

  python3 story/animate.py [--preview t1,t2,...]   (preview: writes out/preview/img_<t>.jpg only)
"""
import os, sys, json, subprocess, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "out"); WORK = os.path.join(OUT, "work"); os.makedirs(WORK, exist_ok=True)
PL = os.path.join(HERE, "plates_hd") if os.path.isdir(os.path.join(HERE, "plates_hd")) else os.path.join(HERE, "plates")
TL = json.load(open(os.path.join(OUT, "timeline.json")))
SH = {s["id"]: s for s in TL["shots"]}
W, H, FPS = 1920, 1080, 30
XF = 0.4   # cross-dissolve length (s)

BLUE, GREY, GOLD, RED, WHITE = (255, 170, 60), (215, 215, 225), (60, 200, 255), (60, 60, 255), (255, 255, 255)  # BGR

# image -> motion. z0/z1 zoom (1 = full frame), c0/c1 centre (fraction of the image), rot degrees,
# fx: list of effects: ("breathe", cx, cy, radius, amp, hz) / ("beat", cx, cy, radius, amp, bpm) /
# ("glow", strength, hz) / ("parts", kind, n, (vx, vy)) / ("shake", amp)
# start: caption text where the image starts (first image of a shot starts with the shot)
IMAGES = {
    "intro": [dict(z0=1.0, z1=1.14, c0=(.5, .5), c1=(.52, .38), rot=(0, -1), fx=[("shake", 2.0), ("glow", .15, .5)])],
    "muscles": [dict(z0=1.04, z1=1.16, c0=(.42, .5), c1=(.55, .45), rot=(1, -1),
                     fx=[("glow", .35, 1.6), ("parts", "spark", 40, (2.0, -.4)), ("shake", 1.0)]),
                dict(start="energy", z0=1.0, z1=1.22, c0=(.45, .5), c1=(.72, .45), rot=(0, 1.5),
                     fx=[("glow", .5, 2.2), ("parts", "spark", 70, (1.2, -.6))])],
    "mito": [dict(z0=1.12, z1=1.0, c0=(.5, .5), c1=(.5, .5), rot=(-3, 2),
                  fx=[("glow", .3, .9), ("parts", "o2", 45, (-1.0, .25))]),
             dict(start="release", z0=1.0, z1=1.15, c0=(.4, .55), c1=(.6, .45), rot=(0, 0),
                  fx=[("parts", "co2", 45, (1.3, -.7)), ("glow", .15, 1)])],
    "brain": [dict(z0=1.0, z1=1.2, c0=(.5, .5), c1=(.55, .55), rot=(0, 0),
                   fx=[("glow", .6, 2.5), ("parts", "zap", 25, (0, 1.2))]),
              dict(start="drives", z0=1.15, z1=1.0, c0=(.5, .55), c1=(.5, .5), rot=(0, 0),
                   fx=[("breathe", .5, .62, .42, .05, 1.0), ("glow", .25, 1.0)])],
    "diaphragm": [dict(z0=1.0, z1=1.12, c0=(.5, .55), c1=(.5, .6), rot=(0, 0),
                       fx=[("breathe", .5, .62, .3, .05, 1.1), ("glow", .2, 1.1), ("parts", "o2", 30, (0, .9))]),
                  dict(start="oxygen in", z0=1.06, z1=1.2, c0=(.4, .5), c1=(.6, .5), rot=(0, 0),
                       fx=[("parts", "o2", 35, (1.2, .5)), ("parts", "co2", 30, (1.0, -.8)), ("glow", .2, 1)])],
    "heart": [dict(z0=1.04, z1=1.16, c0=(.5, .55), c1=(.5, .55), rot=(0, 0),
                   fx=[("beat", .5, .58, .38, .045, 150), ("glow", .55, 2.5)])],
    "buffer": [dict(z0=1.12, z1=1.2, c0=(.38, .5), c1=(.62, .45), rot=(-1, 1),
                    fx=[("shake", 5.0), ("glow", .35, 2), ("parts", "spark", 40, (-2.5, 0))]),
               dict(start="blood", z0=1.0, z1=1.18, c0=(.3, .45), c1=(.7, .45), rot=(0, 0),
                    fx=[("parts", "co2", 55, (.3, -1.6)), ("glow", .3, 1.5)]),
               dict(start="gasp", z0=1.0, z1=1.12, c0=(.5, .5), c1=(.55, .42), rot=(0, 0),
                    fx=[("breathe", .45, .75, .4, .03, 2.2), ("shake", 2.5)])],
    "lactate": [dict(z0=1.15, z1=1.02, c0=(.45, .5), c1=(.55, .5), rot=(-2, 0),
                     fx=[("glow", .25, .8)]),
                dict(start="Lactate", z0=1.0, z1=1.15, c0=(.3, .5), c1=(.7, .5), rot=(0, 0),
                     fx=[("parts", "spark", 50, (1.6, -.2)), ("glow", .35, 1.2)])],
    "trained": [dict(z0=1.18, z1=1.0, c0=(.5, .4), c1=(.5, .5), rot=(1, 0),
                     fx=[("breathe", .5, .6, .3, .02, .45), ("glow", .2, .45)])],
}


def ez(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)


def spans():
    """[(shot, index, t0, t1)] -- each image's time on screen."""
    out = []
    for s in TL["shots"]:
        ims = IMAGES[s["id"]]
        starts = [s["start"]]
        for im in ims[1:]:
            c = next(c for c in s["caps"] if im["start"].lower() in c["text"].lower())
            starts.append(c["t0"] - 0.1)
        ends = starts[1:] + [s["end"]]
        out += [(s["id"], i, a, b) for i, (a, b) in enumerate(zip(starts, ends))]
    return out


SPANS = spans()
PLATES = {}


def plate(sid, i):
    k = (sid, i)
    if k not in PLATES:
        im = cv2.imread(os.path.join(PL, f"{sid}_{i}.png"))
        if im.shape[1] < W * 1.25:   # low-res fallback: upscale once with Lanczos
            s = W * 1.4 / im.shape[1]
            im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
        PLATES[k] = im.astype(np.float32)
    return PLATES[k]


# ----------------------------------------------------------------------------- particles
def sprite(r, col):
    n = int(r * 3) * 2 + 1; y, x = np.mgrid[:n, :n] - n // 2
    g = np.exp(-(x * x + y * y) / (2 * (r / 1.6) ** 2))[..., None]
    core = np.exp(-(x * x + y * y) / (2 * (r / 4) ** 2))[..., None]
    return (g * np.array(col, np.float32) * 0.8 + core * 255 * 0.6)


SPR = {}
KIND = dict(o2=(BLUE, (12, 24)), co2=(GREY, (12, 26)), spark=(GOLD, (4, 10)), zap=((255, 230, 120), (3, 7)))


def particles(frame, kind, n, vel, t, seed):
    col, (r0, r1) = KIND[kind]
    rng = np.random.default_rng(seed)
    x0, y0 = rng.uniform(0, W, n), rng.uniform(0, H, n)
    r = rng.uniform(r0, r1, n); sp = rng.uniform(0.6, 1.4, n); ph = rng.uniform(0, 6.3, n)
    vx, vy = vel
    xs = (x0 + vx * 120 * sp * t + 25 * np.sin(t * 1.3 + ph)) % (W + 80) - 40
    ys = (y0 + vy * 120 * sp * t + 20 * np.cos(t * 1.1 + ph)) % (H + 80) - 40
    tw = 0.55 + 0.45 * np.sin(t * 5 * sp + ph) if kind in ("spark", "zap") else np.ones(n)
    for x, y, rr, a in zip(xs, ys, r, tw):
        key = (kind, int(rr))
        if key not in SPR:
            SPR[key] = sprite(int(rr), col)
        s = SPR[key]; h = s.shape[0] // 2
        xi, yi = int(x), int(y)
        xa, xb, ya, yb = max(0, xi - h), min(W, xi + h + 1), max(0, yi - h), min(H, yi + h + 1)
        if xa >= xb or ya >= yb:
            continue
        frame[ya:yb, xa:xb] += s[ya - (yi - h): yb - (yi - h), xa - (xi - h): xb - (xi - h)] * a
    return frame


# ----------------------------------------------------------------------------- warps
GY, GX = np.mgrid[:H, :W].astype(np.float32)


def radial_warp(frame, cx, cy, rad, amp):
    """Scales the region around (cx, cy) (output fractions) by 1+amp with a smooth falloff."""
    px, py, R = cx * W, cy * H, rad * H
    dx, dy = GX - px, GY - py
    f = np.exp(-(dx * dx + dy * dy) / (2 * R * R)) * amp
    mx, my = GX - dx * f, GY - dy * f
    return cv2.remap(frame, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def heart_curve(t, bpm):
    p = (t * bpm / 60) % 1.0
    return math.exp(-((p - .06) / .05) ** 2) + .55 * math.exp(-((p - .28) / .05) ** 2)


def render_image(sid, i, t_local, dur, t_abs):
    spec = IMAGES[sid][i]; img = plate(sid, i)
    ih, iw = img.shape[:2]
    u = ez(t_local / max(dur, 1e-3))
    z = spec["z0"] + (spec["z1"] - spec["z0"]) * u
    cx = spec["c0"][0] + (spec["c1"][0] - spec["c0"][0]) * u
    cy = spec["c0"][1] + (spec["c1"][1] - spec["c0"][1]) * u
    rot = spec["rot"][0] + (spec["rot"][1] - spec["rot"][0]) * u
    base = max(W / iw, H / ih) * z            # image pixels -> output pixels
    # keep the view inside the image
    vw, vh = W / base, H / base
    px = min(max(cx * iw, vw / 2), iw - vw / 2); py = min(max(cy * ih, vh / 2), ih - vh / 2)
    sx = sy = 0.0
    for fx in spec["fx"]:
        if fx[0] == "shake":
            a = fx[1]
            sx += a * (math.sin(t_abs * 11.3) * .6 + math.sin(t_abs * 23.7) * .4)
            sy += a * (math.sin(t_abs * 13.9) * .6 + math.sin(t_abs * 19.1) * .4)
    M = cv2.getRotationMatrix2D((px, py), rot, base)
    M[0, 2] += W / 2 - px + sx; M[1, 2] += H / 2 - py + sy
    fr = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    for k, fx in enumerate(spec["fx"]):
        if fx[0] == "breathe":
            _, bx, by, rad, amp, hz = fx
            fr = radial_warp(fr, bx, by, rad, amp * (0.5 - 0.5 * math.cos(2 * math.pi * hz * t_abs)))
        elif fx[0] == "beat":
            _, bx, by, rad, amp, bpm = fx
            fr = radial_warp(fr, bx, by, rad, amp * heart_curve(t_abs, bpm))
    for k, fx in enumerate(spec["fx"]):
        if fx[0] == "glow":
            _, st, hz = fx
            pulse = 0.5 + 0.5 * math.sin(2 * math.pi * hz * t_abs)
            if sid == "heart":
                pulse = heart_curve(t_abs, 150)
            lum = fr.max(2, keepdims=True)
            bright = fr * np.clip((lum - 150) / 105, 0, 1)
            bl = cv2.GaussianBlur(bright, (0, 0), 18)
            fr = fr + bl * st * (0.4 + 0.6 * pulse)
        elif fx[0] == "parts":
            _, kind, n, vel = fx
            fr = particles(fr, kind, n, vel, t_abs, seed=hash((sid, i, k)) % 2 ** 31)
    return fr


def frame_at(t):
    # which images are visible (cross-dissolve around each boundary)
    out = None
    for j, (sid, i, a, b) in enumerate(SPANS):
        a_ = a - (XF / 2 if j else 0); b_ = b + (XF / 2 if j + 1 < len(SPANS) else 0)
        if not (a_ <= t < b_ or (j + 1 == len(SPANS) and t >= a_)):
            continue
        w = 1.0
        if j and t < a + XF / 2:
            w = ez((t - (a - XF / 2)) / XF)
        fr = render_image(sid, i, t - a_, b_ - a_, t)
        out = fr * w if out is None else out * (1 - w) + fr * w
    return out


def finish(fr, t):
    # dip-to-dark at the very start/end, vignette, grain, mild contrast
    fr = np.clip(fr, 0, 255)
    fade = min(1.0, t / 0.35, (TL["total"] - t) / 0.6)
    return (fr * max(0.0, fade)).astype(np.uint8)


def main():
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
        for t in ts:
            cv2.imwrite(os.path.join(OUT, "preview", f"img_{t:05.2f}.jpg"), finish(frame_at(t), t), [cv2.IMWRITE_JPEG_QUALITY, 90])
        return
    json.dump([dict(shot=s, i=i, t0=a, t1=b) for s, i, a, b in SPANS], open(os.path.join(WORK, "images.json"), "w"), indent=1)
    n = int(round(TL["total"] * FPS))
    out = os.path.join(WORK, "concat.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-vf", "vignette=angle=PI/6,noise=alls=3:allf=t,eq=contrast=1.04:saturation=1.06",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE)
    for f in range(n):
        t = (f + 0.5) / FPS
        p.stdin.write(finish(frame_at(t), t).tobytes())
        if f % 60 == 0:
            print(f"frame {f}/{n}", flush=True)
    p.stdin.close(); p.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
