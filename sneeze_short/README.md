# "What happens if you hold in a sneeze?" — 3D what-if short (English, ~33 s, 1080×1920)

An original short in the 3D "what-if body explainer" genre: a rendered character, quick cuts every
1–4 s, glowing x-ray anatomy (airway, brain, lungs, eardrum, eye veins, throat), and pop-in captions.
All of it is generated from code. It uses no stock footage, no AI video, and no paid APIs.

| Layer | How |
|---|---|
| Character | CC0 MakeHuman base mesh + CC0 male morph targets (`data/`), clothes painted by nearest-bone regions with a smooth per-vertex neckline, Cycles hair strands, shrink-wrapped brows, auto-weighted rig, arms posed by aiming bones at target points |
| Shots | `blender/shots.py`: one Python function per narration line (camera, pose, x-ray amount, props), rendered frame by frame in Cycles |
| Voice | Kokoro offline TTS (`am_michael`), or your own recording |
| Music / SFX | Synthesized in numpy (pluck loop, whooshes, zap, heartbeat, riser, eardrum pop, rip, "achoo") |
| Captions | ASS subtitles (Inter Black, white + outline, pop-in), big "20×" stamp |

## Run

```bash
# one-time: Blender as a Python module + TTS
uv venv --python 3.11 bpyenv && uv pip install --python bpyenv/bin/python bpy
pip install kokoro-onnx soundfile scipy numpy   # TTS model files: see ../tunguska_demo/README.md

python3 voice.py                                               # narration + out/timeline.json
cd blender && ../bpyenv/bin/python shots.py -- --preview        # one still per shot (quick check)
../bpyenv/bin/python shots.py -- --scale 0.5 --spp 12 --fps 15  # all frames (~2 h on 4 CPU cores; resumable)
cd .. && python3 compose.py                                    # -> out/sneeze_short.mp4
```

To make a new topic, edit `LINES` in `voice.py` (one line per shot) and add one shot function
per line in `blender/shots.py`.

Facts: holding a sneeze with the nose pinched and the mouth closed can raise upper-airway pressure to about 5–24× that of
a normal sneeze (BMJ Case Reports, 2023: a man tore his windpipe this way). Other reported cases include a
ruptured pharynx (BMJ Case Reports, 2018), burst eardrums, and broken blood vessels in the eye.
