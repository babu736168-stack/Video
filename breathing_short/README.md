# "Why do you breathe faster when you run?" — 3D body-explainer short (English, ~50 s, 1080×1920)

Same pipeline as `../sneeze_short` (all code: Blender/Cycles character, x-ray anatomy, Kokoro TTS,
numpy-synthesized music/SFX, ASS pop-in captions), with a running character: the runner stays at the
origin while the track texture and trees scroll past; legs use a two-bone IK solved in `blender/shots.py`
so the stance foot moves exactly with the ground, and the arms swing opposite the legs.

| Shot | Visual | Narration |
|---|---|---|
| intro | runner on a track, breathing hard | Why do you breathe faster when you run? |
| muscles | x-ray legs, ATP sparks | Every stride makes your leg muscles burn through ATP, their energy, much faster. |
| mito | microscopic: mitochondria, O₂ in, CO₂ out | To make more, tiny mitochondria use extra oxygen, and release extra carbon dioxide. |
| brain | runner starts; brain → brainstem → phrenic nerves → diaphragm | But your brain doesn't wait for that to build up. It speeds up your breathing from the very first step, |
| diaphragm | diaphragm pumping, lungs/ribs expanding | pulling your diaphragm down harder, for deeper, faster breaths. |
| alveoli | microscopic: alveoli + capillaries | In your lungs, oxygen floods into your blood, and carbon dioxide gets breathed out. |
| heart | heart pumping fast, blood flow | Your heart pumps faster to deliver it all. |
| sprint | sprint; acid (H⁺) builds in the muscles | Sprint hard, and acid builds up in your muscles. |
| buffer | bicarbonate meets acid → CO₂ bubbles → lungs → mouth | Your blood buffers it, releasing even more carbon dioxide, so you gasp. |
| lactate | "MYTH!" — lactate carried to the heart as fuel | And no, lactic acid isn't the villain. Lactate is actually fuel for your heart and muscles. |
| after | hands on hips, panting (EPOC) | Even after you stop, you keep panting while your body recovers. |
| trained | easy jog, heart/muscles glow green | Train regularly, and your heart and muscles adapt, so the same pace feels easier. |

## Run

```bash
python3 voice.py                                                    # narration + out/timeline.json
cd blender && /path/to/bpyenv/bin/python shots.py -- --preview      # one still per shot
/path/to/bpyenv/bin/python shots.py -- --scale 0.5 --spp 12 --fps 15  # all frames (~2-3 h on 4 cores; resumable)
cd .. && python3 compose.py                                         # -> out/breathing_short.mp4
```

The character mesh/morphs are read from `../sneeze_short/data` (override with `CHAR_DATA`).

## Science notes (what the script deliberately says, and why)

* Breathing rises **immediately** at the start of exercise (central command + feedback from moving
  muscles/joints, "feed-forward"), not only after CO₂ or acid build up. In moderate running, ventilation
  tracks CO₂ production and arterial CO₂/O₂ stay close to resting values.
* Above the threshold, bicarbonate buffering of H⁺ produces **extra (non-metabolic) CO₂**, and H⁺ drives the
  peripheral (carotid) chemoreceptors, so breathing rises disproportionately — the "gasp".
* **Lactate is not the cause of the acidosis**: the pyruvate → lactate reaction consumes an H⁺; H⁺
  comes mainly from high ATP turnover. Lactate is oxidised as fuel by the heart and slow-twitch muscle.
* Training mainly adapts the **heart, blood and muscles** (stroke volume, mitochondria, capillaries) —
  the lungs themselves change little, so the script does not claim "stronger lungs".

Sources: Forster et al., *Control of breathing during exercise*, Compr Physiol 2012; Robergs et al.,
*Biochemistry of exercise-induced metabolic acidosis*, Am J Physiol 2004; Brooks, *The science and
translation of lactate shuttle theory*, Cell Metab 2018; Dempsey et al., on lung adaptations to training.
