"""Run a Piper VITS voice with onnxruntime; Hindi phonemes from espeak-ng (via phonemizer + espeakng_loader)."""
import json, numpy as np, onnxruntime as ort
import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
from phonemizer.backend import EspeakBackend
_BE = EspeakBackend("hi", preserve_punctuation=True, with_stress=True, language_switch="remove-flags")

class Piper:
    def __init__(self, onnx_path):
        self.cfg = json.load(open(onnx_path + ".json"))
        self.map = self.cfg["phoneme_id_map"]; self.sr = self.cfg["audio"]["sample_rate"]
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        self.s = ort.InferenceSession(onnx_path, o, providers=["CPUExecutionProvider"])
    def ids(self, text):
        ph = _BE.phonemize([text], strip=True)[0]
        ids = list(self.map["^"])
        for ch in ph:
            if ch in self.map: ids += self.map[ch] + self.map["_"]
        return ids + self.map["$"], ph
    def __call__(self, text, speed=1.0, noise=0.667, noise_w=0.8):
        ids, ph = self.ids(text)
        sc = np.array([noise, 1.0 / speed, noise_w], np.float32)
        a = self.s.run(None, {"input": np.array([ids], np.int64), "input_lengths": np.array([len(ids)], np.int64), "scales": sc})[0]
        return a.squeeze().astype(np.float32), self.sr
