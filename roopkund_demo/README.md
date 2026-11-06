# Roopkund "Skeleton Lake" — ~20 s Hinglish short (example)

Built on the engine in `../tunguska_demo/make_video.py` (voice, captions, SFX, render loop);
this folder only adds the story's script, scenes and sound cues.

```bash
python3 make_video.py            # -> out/roopkund_demo.mp4
python3 make_video.py --preview  # still frames only
```

Facts used: Roopkund lake (~5,000 m / ~16,000 ft, Uttarakhand); skeletons found 1942;
2019 DNA study found groups who died ~1,000 years apart, one with Eastern-Mediterranean ancestry.

## English version

```bash
VIDEO_LANG=en python3 make_video.py   # -> out/roopkund_demo_en.mp4 (voice am_michael, English captions + labels)
```

## Using your own narration (VoiceStudio, ElevenLabs, phone recording…)

Record/generate the **whole script in one file**, in order, with a short pause between sentences, then:

```bash
VIDEO_LANG=en VOICE_FILE=/path/to/narration.mp3 python3 make_video.py
# optional: VOICE_FILE_TEMPO=1.1 to speed the recording up without changing pitch
```

The file is cut at the natural pauses that best match each caption chunk (dynamic-programming alignment),
and every scene, caption, sound effect and the music ducking follow the recorded voice.
