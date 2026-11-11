# Handoff: Hinglish teaching videos (Polity + Economics)

Paste this whole file into a new Claude Code chat, then say what to do next
(for example: "Read HANDOFF.md and fix the two pending issues, then send me the 2-minute sample").

---

## 1. Who I am and what I make
- I make animated teaching videos in **Hinglish** (Hindi sentences, English technical terms), in the style of a friendly coaching teacher ("दोस्तों").
- Subjects:
  - **Indian Polity**: M. Laxmikanth, *Indian Polity*, 6th edition.
  - **Economics**: NCERT plus Ramesh Singh, *Indian Economy*. Both are sources.
- Process: **send me a short sample first (now 2 minutes), wait for my feedback, then make the full video.**
- File names: `ChNN - Chapter Title.mp4`, e.g. `Ch01 - Historical Background.mp4`. Economics files so far: `Econ01 - Demand and Supply (...).mp4`.

## 2. Content rules
- Cover every fact in the chapter. No exam questions.
- Fact-check every date, number, name and article. True background from outside the book is allowed (who, why, what happened next). Never invent facts, and never put made-up quotes in a real person's mouth.
- **Layman method**: simple everyday language, lively and excited delivery.
- Tell it as **one connected story**, not a list:
  - Open each topic with a short scene: the problem, the people, the tension.
  - Explain why it came, then what it did.
  - End each topic with a hook into the next ("लेकिन एक सवाल अब भी बाक़ी था…", "और फिर…").
- Explain every hard word right where it first appears ("सॉवरेन्टी मतलब — सबसे ऊँची ताक़त").
- Add everyday 💡 examples (shop, school, family, cricket) and links to today's India.
- Use questions, short punch lines, and "सोचिए / ध्यान दीजिए / याद रखिए" to keep it dramatic.
- Never say "we are going to discuss". Open the chapter with a hook question.

## 3. Video flow (mind-map style)
- Hook screen, then the chapter name in the centre with topics flying out one by one.
- For each topic, it is highlighted on the map with its catchy label (e.g. "THE FIRST LEASH"), then the view zooms into the topic board, where points grow out one by one as they are spoken.
- 💡 examples appear as separate amber points.
- Economics boards also have an **animation stage**:
  - moving emoji scenes: toy-shop child, mango cart with ₹200 vs ₹60 and crowds, summer kulfi, farmer and tractor;
  - live graphs: demand curve, movement along it, shifts, supply curve, equilibrium, surplus and shortage, the 2023 tomato supply shock.
- Recap screen, then an outro that teases the next topic.
- Maps or images can be added; I can provide them.

## 4. Voice (latest decisions, in order)
- Engine: **Kokoro**, voice **`hf_alpha`**, **base speed 1.4×**. This was matched to my sample file "Layman style voice sample 1.4x.mp3" (median pitch 219 Hz vs hf_alpha's 206 Hz, the closest of all 54 voices).
- Per-sentence variation around 1.4×:
  - slower and firmer for scene openers, सोचिए / ध्यान दीजिए / याद रखिए, and topic names;
  - louder for punch lines and exclamations;
  - softer for यानी / मतलब explanations;
  - a pause after questions;
  - a dramatic pause before लेकिन / और फिर / नतीजा;
  - a short breath at "—";
  - small random variation.
- **No background music or whooshes.** The ducked music drone was heard as a "vibrating" background sound, so it was removed. The voice gets a 75 Hz high-pass filter. Only a quiet tick plays when a point appears.
- Earlier rejected:
  - Kokoro `hm_omega` at 1.5× ("sound is very bad").
  - Piper `pratham` (clearer, but not chosen).
  - `hm_psi` at 1.3× (replaced by hf_alpha at 1.4×).

## 5. Recording script (so I can record in my own voice)
- The full narration, read in Hindi but **written in Bengali letters** (transliteration, not translation).
- One line per clip, each with a clip ID (`C01-007`), a timestamp, and what is on screen at that moment.
- Marks: ⏸ pause · 🐢 slower · ⚡ faster · 🔊 louder · 🔉 softer · — short breath.
- Letter conventions:

  | Hindi | Bengali letters |
  |---|---|
  | य | য় (্য inside conjuncts) |
  | व | ব |
  | ऐ / ै | অ্যা / ্যা (অ্যাক্ট, হ্যাঁ) |
  | ं at a word end | ঁ |
  | ं before a consonant | joined nasal (ইণ্ডিয়া, হিন্দূ) |
  | ज़, फ़ | জ়, ফ় |
  | ड़, ढ़ | ড়, ঢ় |

## 6. Status of the two issues (fixed 2026-11-11, waiting for feedback)
1. **Unclear words.** The cause was espeak's Hindi spelling-to-sound rules inside Kokoro.
   `polity/voice.py` now has:
   - `SAY_PH`: corrected sounds for डिमांड, ख़रीद/ख़रीदते/ख़रीदना, ख़र्च, मतलब, पहली (TTS only; screen and script unchanged);
   - `HARD`: lines with hard words are spoken at 0.9× of their speed;
   - `ACRONYMS`: एन सी ई आर टी is spoken letter by letter with short gaps.

   Whisper check after the fix: पहली ✓, मतलब ✓, ख़रीदते "रहीते" → "खरीते", डिमांड "दिमान" → "दिमान्द",
   NCERT letters now separate. Still weak: hf_alpha makes ट/ड sound like त/द (टमाटर → "तमाटर"), a limit of the
   voice itself; corrected sounds did not help. Sarvam (below) is the likely real fix.
2. **Screen text now matches speech.** Points, 💡 examples, recap, outro, hook and the stage labels in
   `econ/ds_2min.py` / `render_econ.py` are the spoken Hinglish phrases in Devanagari.
   `polity/render.py` swaps to Noto Sans Devanagari (same size, similar weight) whenever text is Hindi.
   Fonts: `/usr/local/share/fonts/noto/NotoSansDevanagari-{Black,Bold,SemiBold,Medium,Regular}.ttf`
   from raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSansDevanagari/hinted/ttf/.

**Sarvam voice (user wants it):** `ENGINE=sarvam python3 ../polity/voice.py ds_2min`
(defaults: `VOICE=ritu_hi_edtech`, `SARVAM_MODEL=bulbul:v4-flash`, `BASE=1.0`; pace range 0.5–2.0).
The key saved in the cloud environment for api.sarvam.ai was rejected (403 invalid_api_key_error) on 2026-11-11;
a new key from indus.sarvam.ai/key-management is needed.

## 7. What exists (repo `babu736168-stack/Video`, branch `ccr-a809289b-ssj04s`, all pushed)
- `polity/`
  - `ch01_script.py`: the full Ch01 narration so far (hook, map, 1600–1858 background, Regulating Act 1773, Act of Settlement 1781, Pitt's India Act 1784, recap).
  - `ch01_sample.py`: the 5-minute sample (through 1773).
  - `voice.py`: narration with prosody. Settings: `ENGINE` (kokoro/piper), `VOICE`, `BASE`.
  - `render.py`: the mind-map renderer; also has the shared drawing helpers and `audio_mix`.
  - `recording_script.py` and `bengali.py`: the recording script in Bengali letters.
  - `piper_hi.py` and `excite.py`: the Piper voice and pitch "excitement" tools (not used now).
- `econ/`
  - `ds_sample.py`: the 5-minute Demand & Supply class.
  - `ds_2min.py`: the 2-minute layman sample (the latest).
  - `render_econ.py`: mind map, board and animation stage.
- Videos already delivered:
  - `Ch01 - Historical Background (sample).mp4` (5 min, old voice);
  - `Econ01 - Demand and Supply (sample).mp4` (5 min, old voice);
  - `Econ01 - Demand and Supply (2-min sample).mp4`, latest version: hf_alpha at 1.4×, no music.
- Facts to confirm in my 6th-edition copy: the Polity chapter map assumes the Act of Settlement 1781, Act of 1786, and Charter Acts 1793/1813 are in the chapter.
- The old projects (breathing video, cell film, demos) were deleted at my request.

## 8. How to set up and run (cloud container; models are not in the repo)
```bash
pip install kokoro-onnx sherpa-onnx pyworld soundfile scipy pillow
mkdir -p /tmp/claude-0/tts && cd /tmp/claude-0/tts
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# clarity check (Whisper small, Hindi):
curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar xj
# fonts used: Inter / Inter Display (/usr/share/fonts/opentype/inter), Noto Sans Devanagari Black, Noto Color Emoji

cd /home/user/Video/econ
python3 ../polity/voice.py ds_2min                         # -> out/ds_2min/voice.wav + timeline.json
python3 ../polity/recording_script.py ds_2min "out/Econ01 - Demand and Supply (2-min sample) - recording script.md"
python3 render_econ.py --still ds_2min 10,40,80 sheet.jpg   # quick check frames
python3 render_econ.py ds_2min "Econ01 - Demand and Supply (2-min sample).mp4"
# Polity: cd polity; python3 voice.py ch01_sample; python3 render.py ch01_sample "Ch01 - ... .mp4"
```
Notes:
- Hugging Face and pytorch.org are blocked in that environment; GitHub release downloads and PyPI work.
- Write English terms in Devanagari in the TTS text (Latin text switches the engine to an English accent).
- Write years as spoken ("सत्रह सौ तिहत्तर").
