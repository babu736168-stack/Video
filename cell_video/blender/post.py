#!/usr/bin/env python3
"""Bloom + vignette for the Cycles stills: ../models/*.png -> ../models/final/*.jpg"""
import os, glob
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "models"); DST = os.path.join(SRC, "final"); os.makedirs(DST, exist_ok=True)


def bloom(p, out):
    from PIL import Image, ImageFilter, ImageChops
    im = Image.open(p).convert("RGB")
    a = np.asarray(im, np.float32)
    lum = a.max(2, keepdims=True)
    br = Image.fromarray(np.clip(a * np.clip((lum - 150) / 105, 0, 1), 0, 255).astype(np.uint8))
    b1 = np.asarray(br.filter(ImageFilter.GaussianBlur(a.shape[1] / 120)), np.float32)
    b2 = np.asarray(br.filter(ImageFilter.GaussianBlur(a.shape[1] / 40)), np.float32)
    o = a + b1 * 0.55 + b2 * 0.45
    # gentle vignette
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    v = 1 - 0.35 * (((xx / a.shape[1] - .5) ** 2 + (yy / a.shape[0] - .5) ** 2) * 2.2)
    Image.fromarray(np.clip(o * v[..., None], 0, 255).astype(np.uint8)).save(out, quality=94)



for p in sorted(glob.glob(os.path.join(SRC, "*.png"))):
    out = os.path.join(DST, os.path.basename(p).replace(".png", ".jpg"))
    bloom(p, out); print("wrote", out)
