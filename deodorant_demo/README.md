# Deodorant spray short (English, 3D)

1. Render the 3D shots (Blender 5 Python module `bpy`, Python 3.11):
   ```bash
   uv venv --python 3.11 bpyenv && uv pip install --python bpyenv/bin/python bpy
   cd blender && ../bpyenv/bin/python shots.py -- ../renders          # ~10 min on 4 CPU cores
   ```
   Every key word in the script has its own procedural 3D shot (can, Australia map + school, lungs,
   recalled cans, benzene molecule, test tubes, cut-away can, UK map, perfume bottle, 100 figurines, question mark).
2. Build the video: `python3 make_video.py` → `out/deodorant_en.mp4`
   (or `VOICE_FILE=narration.mp3 python3 make_video.py` to use a VoiceStudio / AI Awaaz narration).
