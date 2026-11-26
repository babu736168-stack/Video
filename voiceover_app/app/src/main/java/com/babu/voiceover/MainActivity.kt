package com.babu.voiceover

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.os.VibrationEffect
import android.os.VibratorManager
import android.provider.MediaStore
import android.text.SpannableStringBuilder
import android.text.Spanned
import android.text.style.BackgroundColorSpan
import android.text.style.ForegroundColorSpan
import android.text.style.RelativeSizeSpan
import android.view.Gravity
import android.animation.ObjectAnimator
import android.view.View
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.view.WindowManager
import android.widget.*
import org.vosk.LibVosk
import org.vosk.LogLevel
import org.vosk.Model
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private val ui = Handler(Looper.getMainLooper())
    private val prefs by lazy { getSharedPreferences("settings", MODE_PRIVATE) }
    private val models by lazy { ModelManager(this) }
    private var model: Model? = null
    private var engine: RecorderEngine? = null
    private var aligner: Aligner? = null
    private var lastUri: Uri? = null
    private var player: MediaPlayer? = null
    // voice studio
    private lateinit var studio: View
    private lateinit var ttsView: View
    private lateinit var ttsKey: EditText
    private lateinit var ttsText: EditText
    private lateinit var ttsModel: Spinner
    private lateinit var ttsVoice: Spinner
    private lateinit var ttsCustomVoice: EditText
    private lateinit var ttsPace: SeekBar
    private lateinit var ttsPaceLabel: TextView
    private lateinit var ttsStatus: TextView
    private lateinit var ttsGo: Button
    private lateinit var studioStatus: TextView
    private lateinit var presetButtons: Map<VoicePreset, Button>
    private var studioBase: FloatArray? = null      // cleaned take (cuts, noise gate) before effects
    private var studioRate = 48000
    private var selected = VoicePreset.STUDIO
    private val rendered = HashMap<VoicePreset, FloatArray>()
    @Volatile private var previewTrack: AudioTrack? = null

    // setup screen
    private lateinit var setup: View
    private lateinit var modelStatus: TextView
    private lateinit var modelProgress: ProgressBar
    private lateinit var btnDownload: Button
    private lateinit var btnImport: Button
    private lateinit var scriptBox: EditText
    private lateinit var strictGroup: RadioGroup
    private lateinit var cbNoise: CheckBox
    private lateinit var cbPauses: CheckBox
    private lateinit var cbVibrate: CheckBox
    private lateinit var btnStart: Button
    private lateinit var lastLabel: TextView
    private lateinit var lastRow: LinearLayout

    // recording screen
    private lateinit var recView: View
    private lateinit var prompter: TextView
    private lateinit var prompterScroll: ScrollView
    private lateinit var heardText: TextView
    private lateinit var timerText: TextView
    private lateinit var countText: TextView
    private lateinit var levelBar: ProgressBar
    private lateinit var btnPause: Button

    private var committed = 0; private var preview = 0; private var redUntil = 0L
    private var startedAt = 0L; private var pausedTotal = 0L; private var pausedAt = 0L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LibVosk.setLogLevel(LogLevel.WARNINGS)
        val root = FrameLayout(this)
        setup = buildSetup(); recView = buildRecorder(); studio = buildStudio(); ttsView = buildTts()
        root.addView(setup); root.addView(recView); root.addView(studio); root.addView(ttsView)
        recView.visibility = View.GONE; studio.visibility = View.GONE; ttsView.visibility = View.GONE
        setContentView(root)
        refreshModel()
    }

    // ------------------------------------------------------------------ UI building
    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private fun label(t: String, size: Float = 15f, bold: Boolean = false) = TextView(this).apply {
        text = t; textSize = size; setTextColor(Color.WHITE); if (bold) typeface = Typeface.DEFAULT_BOLD; setPadding(0, dp(10), 0, dp(4))
    }
    private fun button(t: String, color: Int = Color.rgb(60, 64, 80), onClick: () -> Unit) = Button(this).apply {
        text = t; isAllCaps = false; setTextColor(Color.WHITE); setBackgroundColor(color); setOnClickListener { onClick() }
    }

    private fun buildSetup(): View {
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(18), dp(18), dp(18), dp(30)) }
        col.addView(label("🎙  Hindi Voiceover Recorder", 24f, true))
        col.addView(label("Script Roman Hindi mein likhiye. Har sahi bola gaya shabd aage badhega; galat shabd laal ho jayega (koi awaaz nahi) aur woh hissa recording se kat jayega.", 14f))

        modelStatus = label("", 14f)
        modelProgress = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply { max = 100; visibility = View.GONE }
        btnDownload = button("Download Hindi model (${ModelManager.MODEL_SIZE_MB} MB, one time)", Color.rgb(30, 110, 200)) { downloadModel() }
        btnImport = button("Import model .zip") { pickModelZip() }
        col.addView(modelStatus); col.addView(modelProgress); col.addView(btnDownload); col.addView(btnImport)

        col.addView(label("Script (Roman Hindi)", 16f, true))
        scriptBox = EditText(this).apply {
            setText(prefs.getString("script", "Kya aap roz subah deodorant lagate hain? Lekin kya aapko pata hai, iske andar asal mein kya hai?"))
            minLines = 7; gravity = Gravity.TOP; textSize = 17f; setTextColor(Color.WHITE); setHintTextColor(Color.GRAY)
            hint = "Yahan apna script paste kijiye…"; setBackgroundColor(Color.rgb(32, 34, 44)); setPadding(dp(12), dp(12), dp(12), dp(12))
        }
        col.addView(scriptBox)

        col.addView(label("Pronunciation check", 16f, true))
        strictGroup = RadioGroup(this).apply { orientation = RadioGroup.HORIZONTAL }
        listOf("Strict" to Strictness.STRICT, "Medium" to Strictness.MEDIUM, "Easy" to Strictness.EASY).forEachIndexed { i, (t, s) ->
            strictGroup.addView(RadioButton(this).apply { id = 100 + i; text = t; setTextColor(Color.WHITE); tag = s })
        }
        strictGroup.check(100 + prefs.getInt("strict", 0))
        col.addView(strictGroup)
        cbNoise = CheckBox(this).apply { text = "Remove background noise"; setTextColor(Color.WHITE); isChecked = prefs.getBoolean("noise", true) }
        cbPauses = CheckBox(this).apply { text = "Shorten long pauses"; setTextColor(Color.WHITE); isChecked = prefs.getBoolean("pauses", true) }
        cbVibrate = CheckBox(this).apply { text = "Vibrate on mistake (off = only red word, zero sound)"; setTextColor(Color.WHITE); isChecked = prefs.getBoolean("vibrate", false) }
        col.addView(cbNoise); col.addView(cbPauses); col.addView(cbVibrate)

        btnStart = button("●  START RECORDING", Color.rgb(210, 30, 45)) { startRecording() }.apply { textSize = 20f; minHeight = dp(64) }
        col.addView(Space(this).apply { minimumHeight = dp(14) }); col.addView(btnStart)

        lastLabel = label("", 14f)
        lastRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; visibility = View.GONE }
        lastRow.addView(button("▶ Play") { play() }, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f))
        lastRow.addView(button("Share") { share() }, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f))
        col.addView(lastLabel); col.addView(lastRow)
        col.addView(Space(this).apply { minimumHeight = dp(18) })
        col.addView(button("🗣  TEXT → HINDI VOICE (free)", Color.rgb(30, 110, 200)) { openTts() }.apply { textSize = 17f; minHeight = dp(58) })
        return ScrollView(this).apply { setBackgroundColor(Color.rgb(18, 19, 26)); addView(col) }
    }

    private fun buildRecorder(): View {
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(Color.BLACK); setPadding(dp(14), dp(14), dp(14), dp(14)) }
        val top = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        timerText = label("● 00:00", 18f, true).apply { setTextColor(Color.rgb(255, 70, 70)) }
        countText = label("0 / 0", 16f).apply { gravity = Gravity.END }
        top.addView(timerText, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f)); top.addView(countText, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f))
        levelBar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply { max = 100 }
        prompter = TextView(this).apply { textSize = 34f; setTextColor(Color.WHITE); setLineSpacing(0f, 1.25f); typeface = Typeface.DEFAULT_BOLD }
        prompterScroll = ScrollView(this).apply { addView(prompter) }
        heardText = label("", 13f).apply { setTextColor(Color.GRAY) }
        val btns = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        val lp = { LinearLayout.LayoutParams(0, dp(58), 1f).apply { setMargins(dp(3), 0, dp(3), 0) } }
        btns.addView(button("◀ Back") { engine?.back() }, lp())
        btns.addView(button("Skip ▶") { engine?.skip() }, lp())
        btnPause = button("❚❚ Pause") { togglePause() }; btns.addView(btnPause, lp())
        btns.addView(button("■ Save", Color.rgb(210, 30, 45)) { stopAndSave() }, lp())
        col.addView(top); col.addView(levelBar)
        col.addView(prompterScroll, LinearLayout.LayoutParams(MATCH_PARENT, 0, 1f))
        col.addView(heardText); col.addView(btns)
        return col
    }

    // ------------------------------------------------------------------ model
    private fun refreshModel() {
        val ready = models.isReady()
        modelStatus.text = if (ready) "✅ Hindi speech model installed (works offline)" else "⬇ Hindi speech model needed (one-time download, internet required)"
        btnDownload.visibility = if (ready) View.GONE else View.VISIBLE
        btnImport.visibility = if (ready) View.GONE else View.VISIBLE
    }

    private fun downloadModel() {
        btnDownload.isEnabled = false; modelProgress.visibility = View.VISIBLE
        thread {
            try {
                models.download { p -> ui.post { modelProgress.progress = p; modelStatus.text = "Downloading… $p%" } }
                ui.post { modelProgress.visibility = View.GONE; refreshModel() }
            } catch (e: Exception) {
                ui.post {
                    modelProgress.visibility = View.GONE; btnDownload.isEnabled = true
                    modelStatus.text = "Download failed: ${e.message}. Try again, or download the zip in your browser and use Import:\n${ModelManager.MODEL_URL}"
                }
            }
        }
    }

    private fun pickModelZip() = startActivityForResult(Intent(Intent.ACTION_OPEN_DOCUMENT).apply { addCategory(Intent.CATEGORY_OPENABLE); type = "application/zip" }, 7)

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val uri = data?.data ?: return
        if (requestCode == 7 && resultCode == RESULT_OK) {
            modelStatus.text = "Importing…"
            thread {
                val err = runCatching { models.import(uri) }.exceptionOrNull()
                ui.post { refreshModel(); if (err != null) modelStatus.text = "Import failed: ${err.message}" }
            }
        }
    }

    // ------------------------------------------------------------------ recording
    private fun startRecording() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 1); return
        }
        val path = models.modelPath() ?: return toast("Pehle Hindi model download kijiye")
        val words = Script.parse(scriptBox.text.toString())
        if (words.isEmpty()) return toast("Script khaali hai")
        val strict = strictGroup.findViewById<RadioButton>(strictGroup.checkedRadioButtonId)?.tag as? Strictness ?: Strictness.STRICT
        prefs.edit().putString("script", scriptBox.text.toString()).putInt("strict", strict.ordinal)
            .putBoolean("noise", cbNoise.isChecked).putBoolean("pauses", cbPauses.isChecked).putBoolean("vibrate", cbVibrate.isChecked).apply()
        if (Script.hasDigits(words)) {
            AlertDialog.Builder(this).setTitle("Numbers in script")
                .setMessage("Numbers like 2021 are hard to check. Better write them in words (e.g. \"do hazaar ikkees\"). Continue anyway?")
                .setPositiveButton("Continue") { _, _ -> begin(path, words, strict) }.setNegativeButton("Edit", null).show()
        } else begin(path, words, strict)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) startRecording() else toast("Microphone permission is needed")
    }

    private fun begin(path: String, words: List<ScriptWord>, strict: Strictness) {
        btnStart.isEnabled = false; btnStart.text = "Loading Hindi model…"
        thread {
            try {
                val m = model ?: Model(path).also { model = it }
                val al = Aligner(words, WordMatcher(strict))
                val eng = RecorderEngine(m, al, File(cacheDir, "take.pcm"), cbNoise.isChecked, cbVibrate.isChecked, listener)
                ui.post {
                    aligner = al; engine = eng; committed = 0; preview = 0
                    setup.visibility = View.GONE; recView.visibility = View.VISIBLE
                    window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                    startedAt = SystemClock.elapsedRealtime(); pausedTotal = 0; btnPause.text = "❚❚ Pause"
                    render(); tick(); eng.start()
                    btnStart.isEnabled = true; btnStart.text = "●  START RECORDING"
                }
            } catch (e: Exception) {
                ui.post { btnStart.isEnabled = true; btnStart.text = "●  START RECORDING"; toast("Could not start: ${e.message}") }
            }
        }
    }

    private val listener = object : RecorderEngine.Listener {
        override fun onProgress(committed: Int, preview: Int, heard: String) = ui.post {
            this@MainActivity.committed = committed; this@MainActivity.preview = preview
            if (heard.isNotBlank()) heardText.text = "Suna: $heard"
            render()
        }.let { }
        override fun onWrong(heard: String) = ui.post {
            redUntil = SystemClock.elapsedRealtime() + 900
            // no sound at all: red word + shake (+ optional vibration)
            ObjectAnimator.ofFloat(prompter, "translationX", 0f, 22f, -22f, 16f, -16f, 8f, -8f, 0f).setDuration(450).start()
            if (cbVibrate.isChecked) (getSystemService(VIBRATOR_MANAGER_SERVICE) as VibratorManager).defaultVibrator.vibrate(VibrationEffect.createOneShot(120, 180))
            heardText.text = "✗ Galat: \"$heard\"  — dobara boliye"
            render(); ui.postDelayed({ render() }, 920)
        }.let { }
        override fun onLevel(level: Float) = ui.post { levelBar.progress = (level * 400).toInt().coerceIn(0, 100) }.let { }
        override fun onFinishedScript() = ui.post { stopAndSave() }.let { }
        override fun onFailure(e: Throwable) = ui.post { toast("Recording error: ${e.message}"); showSetup() }.let { }
    }

    private fun render() {
        val words = aligner?.words ?: return
        val sb = SpannableStringBuilder()
        val red = SystemClock.elapsedRealtime() < redUntil
        for (i in committed until words.size) {
            val s = sb.length
            sb.append(words[i].display).append(' ')
            val e = s + words[i].display.length
            when {
                i < preview -> sb.setSpan(ForegroundColorSpan(Color.rgb(110, 230, 140)), s, e, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                i == preview -> {
                    sb.setSpan(BackgroundColorSpan(if (red) Color.rgb(220, 30, 40) else Color.rgb(255, 214, 10)), s, e, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    sb.setSpan(ForegroundColorSpan(if (red) Color.WHITE else Color.BLACK), s, e, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    sb.setSpan(RelativeSizeSpan(1.12f), s, e, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                }
                else -> sb.setSpan(ForegroundColorSpan(Color.rgb(200, 200, 210)), s, e, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            }
        }
        prompter.text = sb
        prompterScroll.scrollTo(0, 0)
        countText.text = "${minOf(committed, words.size)} / ${words.size}"
    }

    private fun tick() {
        if (recView.visibility != View.VISIBLE) return
        val now = SystemClock.elapsedRealtime()
        val ms = (if (engine?.paused == true) pausedAt else now) - startedAt - pausedTotal
        timerText.text = String.format(Locale.US, "%s %02d:%02d", if (engine?.paused == true) "❚❚" else "●", ms / 60000, ms / 1000 % 60)
        ui.postDelayed({ tick() }, 250)
    }

    private fun togglePause() {
        val e = engine ?: return
        e.paused = !e.paused
        if (e.paused) { pausedAt = SystemClock.elapsedRealtime(); btnPause.text = "▶ Resume" }
        else { pausedTotal += SystemClock.elapsedRealtime() - pausedAt; btnPause.text = "❚❚ Pause" }
    }

    private fun stopAndSave() {
        val e = engine ?: return
        engine = null
        heardText.text = "Processing…"
        val shorten = cbPauses.isChecked; val denoise = cbNoise.isChecked
        thread {
            try {
                val res = e.stop()
                val x = AudioExporter.readRaw(res.rawFile)
                val y = AudioExporter.process(x, res.sampleRate, res.cuts, shorten, denoise)
                ui.post { openStudio(y, res.sampleRate, "Recording ready: ${y.size / res.sampleRate} s, ${res.cuts.size} galat hisse kaat diye gaye.") }
            } catch (ex: Exception) {
                ui.post { toast("Processing failed: ${ex.message}"); showSetup() }
            }
        }
    }

    // ------------------------------------------------------------------ text -> Hindi voice (FREE phone voice or Sarvam AI)
    private val freeEngine get() = ttsEngine.selectedItemPosition == 0
    private var phoneTts: PhoneHindiTts? = null
    private lateinit var ttsEngine: Spinner
    private lateinit var premiumBox: LinearLayout
    private lateinit var ttsPitch: SeekBar
    private lateinit var ttsPitchLabel: TextView
    private lateinit var ttsFixData: Button

    private fun buildTts(): View {
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(18), dp(18), dp(18), dp(24)) }
        col.addView(label("🗣 Text → Hindi Voice", 24f, true))
        fun spinner(items: List<String>, sel: Int) = Spinner(this).apply {
            adapter = ArrayAdapter(this@MainActivity, android.R.layout.simple_spinner_dropdown_item, items)
            setSelection(sel.coerceIn(0, maxOf(0, items.size - 1))); setBackgroundColor(Color.rgb(200, 200, 210))
        }
        col.addView(label("Voice engine", 15f, true))
        ttsEngine = spinner(listOf("FREE — Google Hindi voice (on your phone, no charges)", "PREMIUM — Sarvam AI Bulbul (uses paid credits)"), prefs.getInt("tts_engine", 0))
        col.addView(ttsEngine)

        premiumBox = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        premiumBox.addView(label("Sarvam API key (dashboard.sarvam.ai)", 15f, true))
        ttsKey = EditText(this).apply {
            setText(prefs.getString("sarvam_key", "")); hint = "sk_…"; textSize = 15f; setTextColor(Color.WHITE); setHintTextColor(Color.GRAY)
            inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
            setBackgroundColor(Color.rgb(32, 34, 44)); setPadding(dp(12), dp(10), dp(12), dp(10))
        }
        premiumBox.addView(ttsKey)
        premiumBox.addView(label("Sarvam model", 15f, true))
        ttsModel = spinner(SarvamTts.MODELS, prefs.getInt("tts_model", 0)); premiumBox.addView(ttsModel)
        ttsCustomVoice = EditText(this).apply {
            setText(prefs.getString("tts_custom_voice", "")); hint = "…or type another Sarvam voice ID (optional)"; textSize = 14f
            setTextColor(Color.WHITE); setHintTextColor(Color.GRAY); setBackgroundColor(Color.rgb(32, 34, 44)); setPadding(dp(12), dp(8), dp(12), dp(8))
        }
        premiumBox.addView(ttsCustomVoice, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT).apply { setMargins(0, dp(6), 0, 0) })
        col.addView(premiumBox)

        col.addView(label("Script (Roman Hindi ya हिंदी)", 15f, true))
        ttsText = EditText(this).apply {
            minLines = 7; gravity = Gravity.TOP; textSize = 17f; setTextColor(Color.WHITE); setHintTextColor(Color.GRAY)
            hint = "Yahan script likhiye ya paste kijiye…"; setBackgroundColor(Color.rgb(32, 34, 44)); setPadding(dp(12), dp(12), dp(12), dp(12))
        }
        col.addView(ttsText)
        col.addView(button("अ  Roman Hindi → देवनागरी (check & correct words)") { convertScript() },
            LinearLayout.LayoutParams(MATCH_PARENT, dp(50)).apply { setMargins(0, dp(6), 0, 0) })

        col.addView(label("Voice", 15f, true))
        ttsVoice = spinner(listOf("Loading voices…"), 0); col.addView(ttsVoice)
        ttsFixData = button("Install Hindi voice on phone (free)") {
            runCatching { startActivity(Intent(android.speech.tts.TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA)) }
                .onFailure { startActivity(Intent("com.android.settings.TTS_SETTINGS")) }
        }.apply { visibility = View.GONE }
        col.addView(ttsFixData)

        ttsPaceLabel = label("", 15f, true)
        ttsPace = SeekBar(this).apply { max = 150; progress = prefs.getInt("tts_pace", 50) }   // 0.5 .. 2.0
        ttsPitchLabel = label("", 15f, true)
        ttsPitch = SeekBar(this).apply { max = 100; progress = prefs.getInt("tts_pitch", 45) }  // 0.5 .. 1.5 (lower = deeper)
        val upd = object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, p: Int, u: Boolean) = updateSliderLabels()
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        }
        ttsPace.setOnSeekBarChangeListener(upd); ttsPitch.setOnSeekBarChangeListener(upd)
        col.addView(ttsPaceLabel); col.addView(ttsPace); col.addView(ttsPitchLabel); col.addView(ttsPitch)
        updateSliderLabels()

        ttsStatus = label("", 14f)
        ttsGo = button("🎙  GENERATE HINDI VOICE", Color.rgb(210, 30, 45)) { generateTts() }.apply { textSize = 18f }
        col.addView(ttsGo, LinearLayout.LayoutParams(MATCH_PARENT, dp(62)).apply { setMargins(0, dp(14), 0, 0) })
        col.addView(ttsStatus)
        col.addView(label("Tip: generate karne ke baad Voice Studio mein \"Deep Radio\" ya \"Warm\" lagaiye — awaaz aur bhari aur natural lagegi.", 13f))
        col.addView(button("◀ Back") { showSetup() }, LinearLayout.LayoutParams(MATCH_PARENT, dp(50)).apply { setMargins(0, dp(10), 0, 0) })

        ttsEngine.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) = applyEngine()
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }
        return ScrollView(this).apply { setBackgroundColor(Color.rgb(18, 19, 26)); addView(col) }
    }

    private fun pace() = 0.5 + ttsPace.progress / 100.0
    private fun pitch() = 0.5 + ttsPitch.progress / 100.0
    private fun updateSliderLabels() {
        ttsPaceLabel.text = String.format(Locale.US, "Speed: %.2fx", pace())
        ttsPitchLabel.text = String.format(Locale.US, "Pitch: %.2f  (kam = gehri awaaz)", pitch())
    }

    private fun setVoices(items: List<String>, sel: Int) {
        ttsVoice.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, items)
        ttsVoice.setSelection(sel.coerceIn(0, maxOf(0, items.size - 1)))
    }

    /** Shows the right options for the chosen engine. */
    private fun applyEngine() {
        premiumBox.visibility = if (freeEngine) View.GONE else View.VISIBLE
        ttsPitch.visibility = if (freeEngine) View.VISIBLE else View.GONE; ttsPitchLabel.visibility = ttsPitch.visibility
        ttsFixData.visibility = View.GONE
        if (!freeEngine) { setVoices(SarvamTts.VOICES.map { it.label }, prefs.getInt("tts_voice_sarvam", 0)); return }
        val p = phoneTts
        if (p == null) {
            setVoices(listOf("Loading phone voices…"), 0)
            phoneTts = PhoneHindiTts(this) { tts, problem ->
                ui.post {
                    if (problem != null) { ttsStatus.text = "⚠ $problem"; ttsFixData.visibility = View.VISIBLE }
                    if (freeEngine) setVoices(tts.voices.map { tts.label(it) }.ifEmpty { listOf("Default Hindi voice") }, prefs.getInt("tts_voice_phone", 0))
                }
            }
        } else setVoices(p.voices.map { p.label(it) }.ifEmpty { listOf("Default Hindi voice") }, prefs.getInt("tts_voice_phone", 0))
    }

    private fun openTts() {
        if (ttsText.text.isBlank()) ttsText.setText(prefs.getString("tts_text", null) ?: scriptBox.text)
        setup.visibility = View.GONE; ttsView.visibility = View.VISIBLE
        applyEngine()
    }

    private fun saveTtsPrefs() = prefs.edit().putString("sarvam_key", ttsKey.text.toString().trim())
        .putInt("tts_engine", ttsEngine.selectedItemPosition)
        .putString("tts_text", ttsText.text.toString())
        .putInt(if (freeEngine) "tts_voice_phone" else "tts_voice_sarvam", ttsVoice.selectedItemPosition)
        .putString("tts_custom_voice", ttsCustomVoice.text.toString().trim())
        .putInt("tts_model", ttsModel.selectedItemPosition).putInt("tts_pace", ttsPace.progress).putInt("tts_pitch", ttsPitch.progress).apply()

    private fun client(): SarvamTts? {
        val key = ttsKey.text.toString().trim()
        if (key.isEmpty()) { toast("Pehle Sarvam API key daaliye"); return null }
        return SarvamTts(key)
    }

    /** Shows the Devanagari version so wrong words can be corrected before speaking. Free engine = offline converter. */
    private fun convertScript() {
        saveTtsPrefs()
        val text = ttsText.text.toString()
        if (SarvamTts.hasDevanagari(text)) return toast("Script pehle se Devanagari mein hai")
        if (freeEngine) {
            ttsText.setText(HindiTransliterator.transliterate(text))
            ttsStatus.text = "✅ Converted (free, offline). Galat shabd ho to yahin theek kar dijiye, phir Generate."
            return
        }
        val c = client() ?: return
        ttsStatus.text = "Converting to Devanagari…"
        thread {
            val r = runCatching { c.transliterate(text) }
            ui.post {
                r.onSuccess { ttsText.setText(it); ttsStatus.text = "✅ Converted. Galat shabd ho to yahin theek kar dijiye, phir Generate." }
                 .onFailure { ttsStatus.text = "✗ ${it.message}" }
            }
        }
    }

    private fun generateTts() {
        saveTtsPrefs()
        val text0 = ttsText.text.toString().trim()
        if (text0.isEmpty()) return toast("Script khaali hai")
        val pace = pace(); val pitch = pitch()
        if (freeEngine) {
            val p = phoneTts ?: return toast("Phone voice is still loading…")
            val voice = p.voices.getOrNull(ttsVoice.selectedItemPosition)
            // Roman Hindi -> Devanagari first, so it is spoken as pure Hindi (not as English letters)
            val text = if (SarvamTts.hasDevanagari(text0)) text0 else HindiTransliterator.transliterate(text0).also { ttsText.setText(it) }
            ttsGo.isEnabled = false
            thread {
                try {
                    val (audio, sr) = p.synthesize(text, voice, pace.toFloat(), pitch.toFloat()) { i, n -> ui.post { ttsStatus.text = "Generating voice… ${minOf(i + 1, n)}/$n" } }
                    ui.post { ttsGo.isEnabled = true; ttsStatus.text = ""; openStudio(audio, sr, "Free Hindi voice ready: ${audio.size / sr} s.") }
                } catch (e: Exception) { ui.post { ttsGo.isEnabled = true; ttsStatus.text = "✗ ${e.message}" } }
            }
            return
        }
        val c = client() ?: return
        val voice = ttsCustomVoice.text.toString().trim().ifEmpty { SarvamTts.VOICES[ttsVoice.selectedItemPosition.coerceIn(0, SarvamTts.VOICES.size - 1)].id }
        val model = SarvamTts.MODELS[ttsModel.selectedItemPosition]
        ttsGo.isEnabled = false
        thread {
            try {
                val text = if (SarvamTts.hasDevanagari(text0)) text0 else {
                    ui.post { ttsStatus.text = "Converting Roman Hindi → देवनागरी…" }
                    c.transliterate(text0).also { t -> ui.post { ttsText.setText(t) } }
                }
                val (audio, sr) = c.speak(text, model, voice, pace, 0.0) { i, n -> ui.post { ttsStatus.text = "Generating voice… ${minOf(i + 1, n)}/$n" } }
                ui.post { ttsGo.isEnabled = true; ttsStatus.text = ""; openStudio(audio, sr, "Hindi voice ready: ${audio.size / sr} s (voice: $voice).") }
            } catch (e: Exception) {
                ui.post { ttsGo.isEnabled = true; ttsStatus.text = "✗ ${e.message}" }
            }
        }
    }

    // ------------------------------------------------------------------ voice studio (effects)
    private fun buildStudio(): View {
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(18), dp(18), dp(18), dp(24)) }
        col.addView(label("✨ Voice Studio", 24f, true))
        studioStatus = label("Effect chuniye, sun kar dekhiye, phir save kijiye.", 14f)
        col.addView(studioStatus)
        val map = LinkedHashMap<VoicePreset, Button>()
        for (p in VoicePreset.values()) {
            val b = button("${p.title}\n${p.hint}") { choose(p) }.apply { gravity = Gravity.START or Gravity.CENTER_VERTICAL; setPadding(dp(14), dp(10), dp(14), dp(10)); textSize = 15f }
            col.addView(b, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT).apply { setMargins(0, dp(4), 0, dp(4)) })
            map[p] = b
        }
        presetButtons = map
        val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        row.addView(button("▶ Preview") { preview() }, LinearLayout.LayoutParams(0, dp(56), 1f).apply { setMargins(0, dp(10), dp(4), 0) })
        row.addView(button("■ Stop") { stopPreview() }, LinearLayout.LayoutParams(0, dp(56), 1f).apply { setMargins(dp(4), dp(10), 0, 0) })
        col.addView(row)
        col.addView(button("💾  SAVE WITH THIS EFFECT", Color.rgb(210, 30, 45)) { saveStudio(true) }.apply { textSize = 18f },
            LinearLayout.LayoutParams(MATCH_PARENT, dp(62)).apply { setMargins(0, dp(12), 0, 0) })
        col.addView(button("Save without effect (clean)") { saveStudio(false) }, LinearLayout.LayoutParams(MATCH_PARENT, dp(52)).apply { setMargins(0, dp(8), 0, 0) })
        col.addView(button("Discard recording") {
            AlertDialog.Builder(this).setMessage("Delete this recording?").setPositiveButton("Delete") { _, _ -> stopPreview(); studioBase = null; rendered.clear(); showSetup() }
                .setNegativeButton("Cancel", null).show()
        }, LinearLayout.LayoutParams(MATCH_PARENT, dp(52)).apply { setMargins(0, dp(8), 0, 0) })
        return ScrollView(this).apply { setBackgroundColor(Color.rgb(18, 19, 26)); addView(col) }
    }

    private fun openStudio(base: FloatArray, sr: Int, message: String) {
        studioBase = base; studioRate = sr; rendered.clear()
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        recView.visibility = View.GONE; setup.visibility = View.GONE; ttsView.visibility = View.GONE; studio.visibility = View.VISIBLE
        studioStatus.text = "$message\nEffect chuniye aur ▶ Preview dabaiye."
        choose(VoicePreset.valueOf(prefs.getString("preset", VoicePreset.STUDIO.name) ?: VoicePreset.STUDIO.name))
    }

    private fun choose(p: VoicePreset) {
        selected = p
        presetButtons.forEach { (k, b) -> b.setBackgroundColor(if (k == p) Color.rgb(255, 214, 10) else Color.rgb(60, 64, 80)); b.setTextColor(if (k == p) Color.BLACK else Color.WHITE) }
        prefs.edit().putString("preset", p.name).apply()
    }

    /** Renders the chosen effect (cached) on a background thread. */
    private fun render(p: VoicePreset, done: (FloatArray) -> Unit) {
        rendered[p]?.let { return done(it) }
        val base = studioBase ?: return
        studioStatus.text = "Applying ${p.title}…"
        thread {
            val y = VoiceFx.apply(base, studioRate, p)
            ui.post { rendered[p] = y; studioStatus.text = "${p.title}: ${p.hint}"; done(y) }
        }
    }

    private fun preview() {
        stopPreview()
        render(selected) { y ->
            thread {
                val sr = studioRate
                val track = AudioTrack.Builder()
                    .setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build())
                    .setAudioFormat(AudioFormat.Builder().setEncoding(AudioFormat.ENCODING_PCM_16BIT).setSampleRate(sr).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).build())
                    .setTransferMode(AudioTrack.MODE_STREAM).build()
                previewTrack = track; track.play()
                val chunk = ShortArray(sr / 10); var i = 0
                while (i < y.size && previewTrack === track) {
                    val n = minOf(chunk.size, y.size - i)
                    for (k in 0 until n) chunk[k] = (y[i + k].coerceIn(-1f, 1f) * 32767).toInt().toShort()
                    track.write(chunk, 0, n); i += n
                }
                runCatching { track.stop(); track.release() }
            }
        }
    }

    private fun stopPreview() { previewTrack = null }

    private fun saveStudio(withEffect: Boolean) {
        stopPreview()
        val sr = studioRate
        val finishSave = { y: FloatArray, tag: String ->
            thread {
                try {
                    val name = "voiceover_" + SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date()) + "_" + tag + ".wav"
                    val uri = saveWav(name, AudioExporter.wavBytes(y, sr))
                    ui.post {
                        lastUri = uri
                        lastLabel.text = "✅ Saved: Music/HindiVoiceover/$name  (${y.size / sr} s)"
                        lastRow.visibility = View.VISIBLE
                        studioBase = null; rendered.clear(); showSetup()
                    }
                } catch (ex: Exception) { ui.post { toast("Save failed: ${ex.message}") } }
            }
        }
        if (withEffect) render(selected) { finishSave(it, selected.name.lowercase()) }
        else studioBase?.let { finishSave(VoiceFx.finish(it, sr), "clean") }
    }

    private fun saveWav(name: String, bytes: ByteArray): Uri {
        val values = ContentValues().apply {
            put(MediaStore.Audio.Media.DISPLAY_NAME, name)
            put(MediaStore.Audio.Media.MIME_TYPE, "audio/wav")
            put(MediaStore.Audio.Media.RELATIVE_PATH, Environment.DIRECTORY_MUSIC + "/HindiVoiceover")
            put(MediaStore.Audio.Media.IS_PENDING, 1)
        }
        val uri = contentResolver.insert(MediaStore.Audio.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY), values)!!
        contentResolver.openOutputStream(uri)!!.use { it.write(bytes) }
        values.clear(); values.put(MediaStore.Audio.Media.IS_PENDING, 0)
        contentResolver.update(uri, values, null, null)
        return uri
    }

    private fun showSetup() {
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        recView.visibility = View.GONE; studio.visibility = View.GONE; ttsView.visibility = View.GONE; setup.visibility = View.VISIBLE
    }

    private fun play() {
        val u = lastUri ?: return
        player?.release(); player = MediaPlayer.create(this, u)?.apply { start() }
    }

    private fun share() {
        val u = lastUri ?: return
        startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
            type = "audio/wav"; putExtra(Intent.EXTRA_STREAM, u); addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }, "Share voiceover"))
    }

    override fun onBackPressed() {
        if (recView.visibility == View.VISIBLE) {
            AlertDialog.Builder(this).setMessage("Stop and save the recording?")
                .setPositiveButton("Save") { _, _ -> stopAndSave() }.setNegativeButton("Continue", null).show()
        } else if (ttsView.visibility == View.VISIBLE) {
            showSetup()
        } else if (studio.visibility == View.VISIBLE) {
            AlertDialog.Builder(this).setMessage("Save with the selected effect?")
                .setPositiveButton("Save") { _, _ -> saveStudio(true) }.setNegativeButton("Stay", null).show()
        } else super.onBackPressed()
    }

    override fun onDestroy() { super.onDestroy(); phoneTts?.shutdown(); stopPreview(); player?.release(); engine?.stop() }

    private fun toast(t: String) { Toast.makeText(this, t, Toast.LENGTH_LONG).show() }
}
