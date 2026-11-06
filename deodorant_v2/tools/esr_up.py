"""Real-ESRGAN x4 upscaling on CPU via ncnn. Usage: python esr_up.py MODEL_DIR in.png out.png"""
import sys, time
import numpy as np
import ncnn
from PIL import Image

_net = None
def net(model_dir):
    global _net
    if _net is None:
        n = ncnn.Net()
        n.opt.use_vulkan_compute = False
        n.opt.num_threads = 4
        n.load_param(f"{model_dir}/realesrgan-x4plus.param")
        n.load_model(f"{model_dir}/realesrgan-x4plus.bin")
        _net = n
    return _net

def upscale(img, model_dir, tile=200, pad=10):
    """img: PIL RGB -> PIL RGB x4. Tiled to keep memory/latency sane."""
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    h, w, _ = a.shape
    out = np.zeros((h * 4, w * 4, 3), np.float32)
    n = net(model_dir)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            y0, x0 = max(0, y - pad), max(0, x - pad)
            y1, x1 = min(h, y + tile + pad), min(w, x + tile + pad)
            patch = np.ascontiguousarray(a[y0:y1, x0:x1].transpose(2, 0, 1))
            ex = n.create_extractor()
            ex.input("data", ncnn.Mat(patch))
            _, o = ex.extract("output")
            o = np.array(o).transpose(1, 2, 0)
            ty, tx = (y - y0) * 4, (x - x0) * 4
            th, tw = (min(h, y + tile) - y) * 4, (min(w, x + tile) - x) * 4
            out[y * 4:y * 4 + th, x * 4:x * 4 + tw] = o[ty:ty + th, tx:tx + tw]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))

if __name__ == "__main__":
    t = time.time()
    upscale(Image.open(sys.argv[2]), sys.argv[1]).save(sys.argv[3])
    print("seconds", round(time.time() - t, 1))
