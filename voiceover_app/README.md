# Hindi Voiceover Recorder (Android)

Teleprompter + recorder for Hindi voiceovers written in **Roman Hindi**.

* The script is shown big on screen. The current word is **yellow**.
* A word disappears only after it is **pronounced correctly** (offline Hindi speech recognition, Vosk).
* A wrong / skipped / repeated word: **beep + vibration + red word**, the script does not move,
  and the wrong attempt **and** the beep are **cut out** of the final file automatically.
* Spelling variants of the same word are accepted (`nahi / nahin / nahee`, `hai / hain`, `kya / kyaa`, `mein / me` …);
  short words must match exactly in Strict mode (`ka / ki / ke`, `kya / kyon`).
* Fillers (`hmm`, `umm`) are cut silently.
* **Text → Hindi Voice**
  * **FREE (default):** the phone's own Google Hindi voices — no account, no key, no charges; offline voices or the more
    natural online ones (picked automatically). Less robotic: per-sentence pitch/pace variation, punctuation-based
    breathing pauses, warm "natural polish" and faint room tone. Roman Hindi → देवनागरी offline (editable), speed + pitch.
  * **PREMIUM (optional):** Sarvam AI Bulbul with your own API key (paid credits).
  * Result opens in Voice Studio (Deep Radio, Warm …) before saving.
* Clean audio: 48 kHz mono WAV, noise suppression, 80 Hz rumble filter, noise gate, optional pause shortening,
  no background music. Saved to `Music/HindiVoiceover/`, with Play and Share buttons.
* Buttons while recording: **Back** (re-say previous word; the old take is cut), **Skip** (when the recognizer
  can't get a word), **Pause**, **Save**.

## Install
Copy `release/HindiVoiceover-1.0.apk` to the phone (Android 10+), open it, allow "install unknown apps".
On first start tap **Download Hindi model** (≈42 MB, once). After that it works offline.
If the download fails, download `https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip`
in the browser and use **Import model .zip**.

## Build
```bash
export ANDROID_HOME=/path/to/android-sdk     # platform 35, build-tools 35
./gradlew :app:testDebugUnitTest :app:assembleRelease
```
`keystore/voiceover-release.jks` (password `voiceover123`) signs the APK so future versions install as updates.
It is a personal side-loading key only; do not use it for a Play Store app.
