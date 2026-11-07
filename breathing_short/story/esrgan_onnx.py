#!/usr/bin/env python3
"""Builds an ONNX model of Real-ESRGAN x4plus (RRDBNet, 23 blocks) straight from the .pth weights,
without PyTorch: the .pth zip is unpickled with stand-ins for torch's tensor rebuild functions.

  python3 story/esrgan_onnx.py RealESRGAN_x4plus.pth x4.onnx
"""
import sys, zipfile, pickle
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

DT = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64}


def load_pth(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    root = names[0].split("/")[0]
    pkl = next(n for n in names if n.endswith("data.pkl"))

    class Storage:
        def __init__(s, dtype, key):
            s.dtype, s.key = dtype, key

    def rebuild(storage, offset, size, stride, *a, **k):
        raw = np.frombuffer(z.read(f"{root}/data/{storage.key}"), storage.dtype)
        n = int(np.prod(size)) if size else 1
        if not size:
            return raw[offset:offset + 1].reshape(())
        st = [s * raw.itemsize for s in stride]
        return np.lib.stride_tricks.as_strided(raw[offset:], shape=size, strides=st).copy()

    class U(pickle.Unpickler):
        def find_class(s, mod, name):
            if name == "_rebuild_tensor_v2":
                return rebuild
            if name in DT:
                return name
            if mod == "collections" and name == "OrderedDict":
                import collections
                return collections.OrderedDict
            if mod.startswith("torch"):
                return lambda *a, **k: None
            return super().find_class(mod, name)

        def persistent_load(s, pid):
            # ('storage', storage_type, key, location, numel)
            typ, key = pid[1], pid[2]
            dtype = DT.get(typ if isinstance(typ, str) else getattr(typ, "__name__", "FloatStorage"), np.float32)
            return Storage(dtype, key)

    sd = U(z.open(pkl)).load()
    for k in ("params_ema", "params"):
        if k in sd:
            sd = sd[k]; break
    return {k: v.astype(np.float32) for k, v in sd.items()}


def build(sd, out):
    nodes, inits = [], []
    cnt = [0]

    def name(p):
        cnt[0] += 1; return f"{p}_{cnt[0]}"

    def conv(x, w):
        wn, bn = w + ".weight", w + ".bias"
        if wn not in [i.name for i in inits]:
            inits.append(numpy_helper.from_array(sd[wn], wn)); inits.append(numpy_helper.from_array(sd[bn], bn))
        y = name("conv"); nodes.append(helper.make_node("Conv", [x, wn, bn], [y], pads=[1, 1, 1, 1])); return y

    def lrelu(x):
        y = name("lr"); nodes.append(helper.make_node("LeakyRelu", [x], [y], alpha=0.2)); return y

    def cat(xs):
        y = name("cat"); nodes.append(helper.make_node("Concat", xs, [y], axis=1)); return y

    C02 = "c02"; inits.append(numpy_helper.from_array(np.array(0.2, np.float32), C02))

    def axpy(a, b):   # a*0.2 + b
        m = name("mul"); nodes.append(helper.make_node("Mul", [a, C02], [m]))
        y = name("add"); nodes.append(helper.make_node("Add", [m, b], [y])); return y

    def rdb(x, p):
        x1 = lrelu(conv(x, p + ".conv1")); x2 = lrelu(conv(cat([x, x1]), p + ".conv2"))
        x3 = lrelu(conv(cat([x, x1, x2]), p + ".conv3")); x4 = lrelu(conv(cat([x, x1, x2, x3]), p + ".conv4"))
        return axpy(conv(cat([x, x1, x2, x3, x4]), p + ".conv5"), x)

    def up(x):
        sc = "scales"
        if sc not in [i.name for i in inits]:
            inits.append(numpy_helper.from_array(np.array([1, 1, 2, 2], np.float32), sc))
        y = name("up"); nodes.append(helper.make_node("Resize", [x, "", sc], [y], mode="nearest")); return y

    f = conv("input", "conv_first")
    b = f
    nb = len({k.split(".")[1] for k in sd if k.startswith("body.")})
    for i in range(nb):
        p = f"body.{i}"
        b = axpy(rdb(rdb(rdb(b, p + ".rdb1"), p + ".rdb2"), p + ".rdb3"), b)
    f2 = name("add"); nodes.append(helper.make_node("Add", [f, conv(b, "conv_body")], [f2]))
    x = lrelu(conv(up(f2), "conv_up1")); x = lrelu(conv(up(x), "conv_up2"))
    y = conv(lrelu(conv(x, "conv_hr")), "conv_last")
    nodes.append(helper.make_node("Identity", [y], ["output"]))
    g = helper.make_graph(nodes, "rrdbnet", [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, None, None])],
                          [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3, None, None])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)]); m.ir_version = 8
    onnx.checker.check_model(m)
    onnx.save(m, out)
    print("blocks", nb, "nodes", len(nodes), "->", out)


if __name__ == "__main__":
    build(load_pth(sys.argv[1]), sys.argv[2])
