"""'Excited' delivery: higher pitch, wider intonation (WORLD vocoder), brighter EQ, gentle compression."""
import numpy as np, pyworld as pw
from scipy.signal import butter, sosfilt

def excite(a, sr, lift=1.12, spread=1.45, bright=0.35):
    x = a.astype(np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=60, f0_ceil=500, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
    v = f0 > 0
    if v.sum() > 10:
        lf = np.log(f0[v]); m = np.median(lf)
        f0[v] = np.exp(m + (lf - m) * spread) * lift
    y = pw.synthesize(f0, sp, ap, sr, frame_period=5.0)
    hp = sosfilt(butter(2, 2500, "high", fs=sr, output="sos"), y)          # presence
    y = y + bright * hp
    pk = np.max(np.abs(y)) + 1e-9; y = y / pk
    y = np.sign(y) * np.abs(y) ** 0.85                                        # light compression
    return (y / (np.max(np.abs(y)) + 1e-9) * 0.9).astype(np.float32)
