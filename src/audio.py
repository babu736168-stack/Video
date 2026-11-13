"""Synthesized soundtrack: cartoon 'blip' voices, music loops and sound effects."""
import random
import wave
import numpy as np

SR = 44100

# base pitch (Hz) and syllables per second for each voice
VOICES = {
    "jensen": (190, 11), "jacket": (105, 8), "chip": (620, 15),
    "danny": (135, 6.5), "wendy": (330, 17), "all": (220, 9),
}
SCALE = [0, 2, 3, 5, 7, 9, 12]


class Track:
    def __init__(self, seconds):
        self.buf = np.zeros(int(seconds * SR) + SR, dtype=np.float64)
        self.rng = random.Random(7)

    def add(self, t, sig, gain=1.0):
        i = int(t * SR)
        if i >= len(self.buf):
            return
        sig = sig[: len(self.buf) - i]
        self.buf[i:i + len(sig)] += sig * gain

    # ---------- voices ----------
    def voice(self, t, who, dur):
        base, rate = VOICES[who]
        n = max(1, int(dur * rate))
        for k in range(n):
            f = base * 2 ** (self.rng.choice(SCALE) / 12)
            length = 0.75 / rate
            tt = np.arange(int(length * SR)) / SR
            slide = f * (1 + 0.15 * (tt / length))
            ph = 2 * np.pi * np.cumsum(slide) / SR
            sig = 0.6 * np.sin(ph) + 0.25 * np.sign(np.sin(ph)) + 0.15 * np.sin(2 * ph)
            env = np.minimum(1, tt / 0.006) * np.exp(-tt / (length * 0.45))
            if who == "all":       # crowd: several voices together
                sig = sig + 0.6 * np.sin(ph * 1.26) + 0.5 * np.sin(ph * 0.75)
            self.add(t + k / rate, sig * env, 0.22)

    # ---------- sound effects ----------
    def sfx(self, t, name):
        getattr(self, "_" + name)(t)

    def _tone(self, f0, f1, dur, wav="sin", vib=0.0):
        tt = np.arange(int(dur * SR)) / SR
        f = f0 + (f1 - f0) * tt / dur
        f = f * (1 + vib * np.sin(2 * np.pi * 14 * tt))
        ph = 2 * np.pi * np.cumsum(f) / SR
        if wav == "saw":
            return 2 * (ph / (2 * np.pi) % 1) - 1, tt
        return np.sin(ph), tt

    def _boing(self, t):      # cartoon faint
        s, tt = self._tone(700, 90, 0.9, vib=0.08)
        self.add(t, s * np.exp(-tt * 2.2), 0.5)

    def _ding(self, t):       # diner door bell
        tt = np.arange(int(1.5 * SR)) / SR
        s = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((1320, 1), (2640, .4), (3960, .2)))
        self.add(t, s * np.exp(-tt * 3), 0.25)

    def _powerdown(self, t):
        s, tt = self._tone(900, 40, 1.4, wav="saw")
        self.add(t, s * np.exp(-tt * 1.2), 0.25)

    def _whoosh(self, t):
        n = np.random.default_rng(1).standard_normal(int(0.5 * SR))
        n = np.convolve(n, np.ones(25) / 25, mode="same")
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.sin(np.pi * tt / 0.5) ** 2, 0.9)

    def _cheer(self, t):
        rng = np.random.default_rng(3)
        n = rng.standard_normal(int(3.5 * SR))
        n = np.convolve(n, np.ones(9) / 9, mode="same")
        tt = np.arange(len(n)) / SR
        am = 0.7 + 0.3 * np.sin(2 * np.pi * 5.3 * tt) * np.sin(2 * np.pi * 1.7 * tt)
        env = np.minimum(1, tt / 0.15) * np.minimum(1, (3.5 - tt) / 1.2)
        self.add(t, n * am * env, 0.35)
        for k in range(6):  # whistles
            s, ts = self._tone(1800 + 300 * k, 2600 + 200 * k, 0.35)
            self.add(t + 0.2 + k * 0.4, s * np.sin(np.pi * ts / 0.35), 0.05)

    def _dundun(self, t):     # dramatic sting
        for k, (f, d) in enumerate(((110, .35), (104, .35), (98, 1.2))):
            s, tt = self._tone(f, f, d, wav="saw")
            self.add(t + k * 0.38, s * np.exp(-tt * 1.5), 0.3)

    def _tada(self, t):
        for k, f in enumerate((523, 659, 784, 1047)):
            s, tt = self._tone(f, f, 1.2)
            self.add(t + k * 0.06, s * np.exp(-tt * 2.5), 0.15)

    def _rimshot(self, t):
        n = np.random.default_rng(5).standard_normal(int(0.25 * SR))
        tt = np.arange(len(n)) / SR
        self.add(t, n * np.exp(-tt * 25), 0.35)
        self.add(t + 0.18, n * np.exp(-tt * 18), 0.3)
        s, tt2 = self._tone(5000, 5000, 1.0)
        self.add(t + 0.36, (s + np.random.default_rng(6).standard_normal(len(s)) * 0.5) * np.exp(-tt2 * 4), 0.12)

    # ---------- music ----------
    def music(self, t0, t1, bpm, chords, style):
        beat = 60 / bpm
        n_beats = int((t1 - t0) / beat)
        for b in range(n_beats):
            root = chords[(b // 4) % len(chords)]
            t = t0 + b * beat
            f = 55 * 2 ** (root / 12)
            # bass
            pattern = [0, 7, 12, 7] if style != "chase" else [0, 0, 12, 0]
            s, tt = self._tone(f * 2 ** (pattern[b % 4] / 12), f * 2 ** (pattern[b % 4] / 12), beat * 0.9)
            self.add(t, (s + 0.3 * np.sign(s)) * np.exp(-tt * 4), 0.10)
            # hats / brushes
            hat = np.random.default_rng(b).standard_normal(int(0.05 * SR))
            th = np.arange(len(hat)) / SR
            self.add(t + beat / 2, np.diff(hat, prepend=0) * np.exp(-th * 80), 0.05)
            if style == "chase":
                self.add(t, np.diff(hat, prepend=0) * np.exp(-th * 80), 0.05)
            # chord stabs
            if b % 2 == 1 and style in ("jazzy", "keynote", "chase"):
                for iv in (12, 16, 19) if style != "jazzy" else (12, 15, 19, 22):
                    s, tt = self._tone(f * 2 ** (iv / 12), f * 2 ** (iv / 12), beat * 0.6)
                    self.add(t, s * np.exp(-tt * 6), 0.025)

    def write(self, path):
        x = self.buf
        x = x / max(1e-9, np.max(np.abs(x))) * 0.9
        pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
        st = np.repeat(pcm[:, None], 2, axis=1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(st.tobytes())
