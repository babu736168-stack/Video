# Cartoon Comedy Videos

## 🐒 The Stylish Monkey and the Joker's Terrible Day
A 2.5-minute cartoon comedy at a busy Indian railway station, with 5 characters (Monkey, Joker, Bird, Egg Seller, Bodybuilder).

| File | What it is |
|---|---|
| `output/stylish_monkey_and_the_joker.mp4` | The finished video (1280×720, 24 fps, with sound) |
| `output/stylish_monkey_cast.png` | The cast sheet |
| `docs/stylish_monkey_story.md` | Characters and scene-by-scene breakdown |
| `src/railway_comedy.py`, `src/railway_art.py` | The renderer (`cd src && python3 railway_comedy.py`) |

---

## The Jacket Must Go On 🧥

A 2.5-minute animated cartoon parody with 5 original characters, plus a detailed analysis of NVIDIA CEO Jensen Huang that the story is based on.

| File | What it is |
|---|---|
| `output/the_jacket_must_go_on.mp4` | The finished video (1280×720, 24 fps, with sound) |
| `output/character_sheet.png` | All 5 characters side by side |
| `docs/jensen_huang_analysis.md` | Detailed analysis of Jensen Huang: life, career, leadership, strengths, risks |
| `docs/characters_and_script.md` | Character bios and the full script |
| `src/` | The Python code that draws every frame and synthesizes all the audio |

## Re-render the video

```bash
pip install pillow numpy        # ffmpeg must also be installed
cd src && python3 render_video.py
```

To change the story, edit the `lines` lists in `src/render_video.py`. Scene length and voice timing adjust automatically.

*A fictional, good-natured parody. Not affiliated with or endorsed by NVIDIA or Jensen Huang.*
