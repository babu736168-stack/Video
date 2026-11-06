"""Upscale 5 key frames of every GIF shot with Real-ESRGAN x4 -> OUT_DIR/<shot>_<k>.png (skips existing)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageSequence
from esr_up import upscale

MODELS, OUT_DIR, UP = sys.argv[1], sys.argv[2], sys.argv[3]
GIFS = {"01": "66819fa2", "02": "d3d14c0d", "03": "6b3a51ff", "04": "632c4857", "05": "b69e531b", "06": "b270d2c1",
        "07": "93098554", "08": "2392c6f7", "09": "290c1d66", "10": "0708d860", "12": "486bba73", "13": "d1466911",
        "14": "a70a0699", "15": "0d021c17", "16": "41563f91", "17": "41a55b7d", "18": "82d2c20b"}
os.makedirs(OUT_DIR, exist_ok=True)
t0 = time.time(); done = 0
for shot, gid in GIFS.items():
    frames = [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(f"{UP}/{gid}-image.gif"))]
    picks = sorted(set(round(i * (len(frames) - 1) / 4) for i in range(5)))
    for k, fi in enumerate(picks):
        dst = f"{OUT_DIR}/{shot}_{k}.png"
        if not os.path.exists(dst):
            upscale(frames[fi], MODELS).save(dst)
        done += 1
        print(f"{shot}_{k} done ({done}/85, {time.time() - t0:.0f}s)", flush=True)
print("ALL_DONE", flush=True)
