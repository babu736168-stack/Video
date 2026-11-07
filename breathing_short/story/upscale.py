#!/usr/bin/env python3
"""4x AI upscale of the storyboard plates with Real-ESRGAN (RealESRGAN_x4plus weights, BSD-3-Clause,
github.com/xinntao/Real-ESRGAN), CPU, tiled.  story/plates/*.png -> story/plates_hd/*.png (long side 2880 px)

  ESRGAN=/path/to/RealESRGAN_x4plus.pth python3 story/upscale.py
Falls back to Lanczos + light sharpening when torch or the weights are missing.
"""
import os, glob
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, DST = os.path.join(HERE, "plates"), os.path.join(HERE, "plates_hd")
WEIGHTS = os.environ.get("ESRGAN", "/tmp/claude-0/assets/esr/x4.pth")
ONNX = os.environ.get("ESRGAN_ONNX", "/tmp/claude-0/assets/esr/x4.onnx")   # from story/esrgan_onnx.py
LONG = 2880


def rrdbnet():
    import torch, torch.nn as nn, torch.nn.functional as F

    class RDB(nn.Module):
        def __init__(s, nf=64, gc=32):
            super().__init__()
            s.conv1 = nn.Conv2d(nf, gc, 3, 1, 1); s.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
            s.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1); s.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
            s.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1); s.l = nn.LeakyReLU(0.2, True)

        def forward(s, x):
            x1 = s.l(s.conv1(x)); x2 = s.l(s.conv2(torch.cat((x, x1), 1)))
            x3 = s.l(s.conv3(torch.cat((x, x1, x2), 1))); x4 = s.l(s.conv4(torch.cat((x, x1, x2, x3), 1)))
            return s.conv5(torch.cat((x, x1, x2, x3, x4), 1)) * 0.2 + x

    class RRDB(nn.Module):
        def __init__(s, nf=64):
            super().__init__(); s.rdb1, s.rdb2, s.rdb3 = RDB(nf), RDB(nf), RDB(nf)

        def forward(s, x):
            return s.rdb3(s.rdb2(s.rdb1(x))) * 0.2 + x

    class Net(nn.Module):
        def __init__(s, nf=64, nb=23):
            super().__init__()
            s.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
            s.body = nn.Sequential(*[RRDB(nf) for _ in range(nb)])
            s.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
            s.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1); s.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
            s.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1); s.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
            s.l = nn.LeakyReLU(0.2, True)

        def forward(s, x):
            f = s.conv_first(x); f = f + s.conv_body(s.body(f))
            f = s.l(s.conv_up1(F.interpolate(f, scale_factor=2, mode="nearest")))
            f = s.l(s.conv_up2(F.interpolate(f, scale_factor=2, mode="nearest")))
            return s.conv_last(s.l(s.conv_hr(f)))

    net = Net()
    sd = torch.load(WEIGHTS, map_location="cpu")
    net.load_state_dict(sd.get("params_ema", sd.get("params", sd)), strict=True)
    return net.eval()


def esrgan(net, im, tile=192, pad=12):
    """net: callable numpy (1,3,h,w) float32 -> (1,3,4h,4w)."""
    x = (np.asarray(im, np.float32) / 255).transpose(2, 0, 1)[None]
    _, _, h, w = x.shape
    out = np.zeros((1, 3, h * 4, w * 4), np.float32)
    for y in range(0, h, tile):
        for x0 in range(0, w, tile):
            ya, yb, xa, xb = max(0, y - pad), min(h, y + tile + pad), max(0, x0 - pad), min(w, x0 + tile + pad)
            o = net(np.ascontiguousarray(x[:, :, ya:yb, xa:xb]))
            ty, tx = min(tile, h - y), min(tile, w - x0)
            out[:, :, y * 4:(y + ty) * 4, x0 * 4:(x0 + tx) * 4] = \
                o[:, :, (y - ya) * 4:(y - ya + ty) * 4, (x0 - xa) * 4:(x0 - xa + tx) * 4]
    a = (np.clip(out[0], 0, 1).transpose(1, 2, 0) * 255 + 0.5).astype(np.uint8)
    return Image.fromarray(a)


def onnx_net():
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
    s = ort.InferenceSession(ONNX, so, providers=["CPUExecutionProvider"])
    return lambda x: s.run(None, {"input": x})[0]


def main():
    os.makedirs(DST, exist_ok=True)
    net = None
    if os.path.exists(ONNX):
        net = onnx_net()
    else:
        try:
            import torch
            torch.set_num_threads(os.cpu_count())
            if os.path.exists(WEIGHTS):
                m = rrdbnet()
                net = lambda x: m(torch.from_numpy(x)).detach().numpy()
        except ImportError:
            pass
    print("upscaler:", "Real-ESRGAN x4" if net else "Lanczos fallback")
    for p in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        out = os.path.join(DST, os.path.basename(p))
        if os.path.exists(out):
            continue
        im = Image.open(p).convert("RGB")
        big = esrgan(net, im) if net else im.resize((im.width * 4, im.height * 4), Image.LANCZOS).filter(
            ImageFilter.UnsharpMask(2, 60, 2))
        s = LONG / max(big.size)
        big = big.resize((round(big.width * s), round(big.height * s)), Image.LANCZOS)
        big.save(out); print("wrote", out, big.size, flush=True)


if __name__ == "__main__":
    main()
