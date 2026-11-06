# Tunguska Event — code-generated Hinglish short (demo)

A 30-second, 1080×1920 explainer short made entirely from code: no stock footage,
no AI image or video generator, no paid APIs.

| Layer | How |
|---|---|
| Narration | [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) offline TTS, Hindi voice `hm_omega` |
| Music & SFX | Synthesised in numpy/scipy (drone, heartbeat, whooshes, boom, ticks, riser) with side-chain ducking |
| Visuals | Every frame drawn with Pillow: 3D-ish map (Natural Earth data), fireball/shockwave, dot chart, tree-fall top view, crater cross-section |
| Captions | Word-chunk pop-in captions, CAPS words highlighted yellow, timed to the narration |
| Export | Frames piped into ffmpeg → H.264 + AAC, loudness normalised to −14 LUFS |

## Run

```bash
pip install kokoro-onnx soundfile scipy pillow numpy
mkdir -p data
curl -L -o data/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -L -o data/voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
curl -L -o data/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
python3 make_video.py            # -> out/tunguska_demo.mp4  (~35 s on 4 cores)
python3 make_video.py --preview  # -> out/preview/*.png still frames only
```

Edit `SEGMENTS` at the top of `make_video.py` to change the script, captions or pacing.
Swap in a recorded voice-over or AI-generated clips by replacing the narration or scene functions.
