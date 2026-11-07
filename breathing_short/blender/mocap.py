"""Motion-capture run cycles (CMU Graphics Lab Motion Capture Database, BVH conversion by B. Hahne;
free to use) -> looping joint positions for the runner.

  load(path)        -> dict(names, parent, P[frames, joints, 3] in metres, Z up, facing -Y, dt)
  cycle(clip, ...)  -> a seamless loop: joint positions relative to the hips' ground point, plus the
                       ground speed, so the track can scroll under planted feet (treadmill style).
Pure numpy so it can be analysed outside Blender too.
"""
import re
import numpy as np


def _rot(axis, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    R = np.zeros(a.shape + (3, 3)); i = "XYZ".index(axis); j, k = [(1, 2), (2, 0), (0, 1)][i]
    R[..., i, i] = 1; R[..., j, j] = c; R[..., k, k] = c; R[..., j, k] = -s; R[..., k, j] = s
    return R


def load(path):
    txt = open(path).read()
    head, motion = txt.split("MOTION")
    names, parent, offs, chans, stack = [], [], [], [], []
    tok = iter(re.findall(r"\S+", head))
    for t in tok:
        if t in ("ROOT", "JOINT"):
            names.append(next(tok)); parent.append(stack[-1] if stack else -1); chans.append([])
            offs.append(None)
        elif t == "End":
            next(tok); names.append(names[-1] + "_end"); parent.append(stack[-1]); chans.append([]); offs.append(None)
        elif t == "{":
            stack.append(len(names) - 1)
        elif t == "}":
            stack.pop()
        elif t == "OFFSET":
            offs[stack[-1]] = [float(next(tok)) for _ in range(3)]
        elif t == "CHANNELS":
            chans[stack[-1]] = [next(tok) for _ in range(int(next(tok)))]
    lines = motion.strip().splitlines()
    dt = float(lines[1].split(":")[1])
    D = np.array([[float(x) for x in l.split()] for l in lines[2:] if l.strip()])
    F, n = len(D), len(names)
    G = np.zeros((F, n, 4, 4)); col = 0
    for j in range(n):
        T = np.tile(np.eye(4), (F, 1, 1)); T[:, :3, 3] = offs[j]
        R = np.tile(np.eye(3), (F, 1, 1))
        for c in chans[j]:
            v = D[:, col]; col += 1
            if c.endswith("position"):
                T[:, "XYZ".index(c[0]), 3] = v + (0 if parent[j] < 0 else offs[j]["XYZ".index(c[0])])
            else:
                R = R @ _rot(c[0], v)
        T[:, :3, :3] = R
        G[:, j] = T if parent[j] < 0 else G[:, parent[j]] @ T
    P = G[:, :, :3, 3]
    P = np.stack([P[..., 0], -P[..., 2], P[..., 1]], -1)       # BVH Y-up -> Z-up
    idx = {k: i for i, k in enumerate(names)}
    # units -> metres: hip-to-ankle length of an adult ~ 0.86 m
    leg = np.linalg.norm(P[:, idx["LeftUpLeg"]] - P[:, idx["LeftLeg"]], axis=-1).mean() + \
        np.linalg.norm(P[:, idx["LeftLeg"]] - P[:, idx["LeftFoot"]], axis=-1).mean()
    P = P * (0.86 / leg)
    P[..., 2] -= np.percentile(np.minimum(P[:, idx["LeftToeBase"], 2], P[:, idx["RightToeBase"], 2]), 5) - 0.03
    return dict(names=names, idx=idx, parent=parent, P=P, dt=dt)


def _face_minus_y(clip):
    """Rotate about Z so the overall travel goes along -Y, centred laterally."""
    P, i = clip["P"], clip["idx"]["Hips"]
    d = P[-1, i, :2] - P[0, i, :2]
    a = np.arctan2(d[1], d[0]) - np.arctan2(-1, 0)
    c, s = np.cos(-a), np.sin(-a); R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    P = P @ R.T
    clip = dict(clip); clip["P"] = P
    return clip


def cycle(clip, n_strides=1):
    """Finds the most similar pair of frames n_strides gait cycles apart, returns a seamless loop:
    dict(Q[frames, joints, 3] hips-relative (x,y) / absolute z, speed m/s, period s)."""
    clip = _face_minus_y(clip)
    P, ix = clip["P"], clip["idx"]
    hip = P[:, ix["Hips"]]
    rel = P - hip[:, None, :] * np.array([1, 1, 0])
    # left ankle forward oscillation -> gait period estimate
    s = rel[:, ix["LeftFoot"], 1] - rel[:, ix["RightFoot"], 1]
    s = s - s.mean()
    ac = np.correlate(s, s, "full")[len(s) - 1:]
    lo = int(0.45 / clip["dt"])
    per = lo + int(np.argmax(ac[lo:min(len(ac) - 1, int(1.1 / clip["dt"]))]))   # one full gait cycle (2 steps), frames
    best = None
    L = per * n_strides
    for a in range(0, len(P) - L - 4):
        for b in range(a + L - 6, min(len(P), a + L + 7)):
            e = np.abs(rel[a] - rel[b]).mean() + 0.3 * abs(hip[a, 2] - hip[b, 2])
            if best is None or e < best[0]:
                best = (e, a, b)
    e, a, b = best
    # keep the hips' natural surge/sway inside the stride: subtract only the straight-line travel
    lin = hip[a] + (hip[b] - hip[a]) * (np.arange(b - a) / (b - a))[:, None]
    Q = P[a:b] - (lin * np.array([1, 1, 0]))[:, None, :]
    # remove residual mismatch linearly across the loop so it closes exactly
    drift = (P[b] - hip[b] * np.array([1, 1, 0])) - (P[a] - hip[a] * np.array([1, 1, 0]))
    Q -= drift[None] * (np.arange(b - a) / (b - a))[:, None, None]
    Q[:, :, 0] -= Q[:, ix["Hips"], 0].mean()
    dist = -(hip[b, 1] - hip[a, 1])
    T = (b - a) * clip["dt"]
    return dict(Q=Q, idx=ix, dt=clip["dt"], period=T, speed=dist / T, err=e, frames=(a, b))


def sample(cyc, t):
    """Joint positions at time t (s), linear interpolation, looping."""
    n = len(cyc["Q"]); x = (t / cyc["dt"]) % n
    i = int(x); f = x - i
    return cyc["Q"][i] * (1 - f) + cyc["Q"][(i + 1) % n] * f


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        c = load(p)
        try:
            y = cycle(c)
            print(p, f"frames={len(c['P'])} dur={len(c['P'])*c['dt']:.2f}s  loop={y['period']:.2f}s "
                     f"speed={y['speed']:.2f}m/s err={y['err']:.4f} frames={y['frames']}")
        except Exception as ex:
            print(p, "ERR", ex)
