package com.babu.voiceover

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.media.AudioManager
import android.media.MediaPlayer
import android.media.ToneGenerator
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
    private val beep by lazy { ToneGenerator(AudioManager.STREAM_MUSIC, 85) }

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
        setup = buildSetup(); recView = buildRecorder()
        root.addView(setup); root.addView(recView)
        recView.visibility = View.GONE
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
        col.addView(label("Script Roman Hindi mein likhiye. Har sahi bola gaya shabd aage badhega; galat shabd par beep hogi aur woh hissa recording se kat jayega.", 14f))

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
        col.addView(cbNoise); col.addView(cbPauses)

        btnStart = button("●  START RECORDING", Color.rgb(210, 30, 45)) { startRecording() }.apply { textSize = 20f; minHeight = dp(64) }
        col.addView(Space(this).apply { minimumHeight = dp(14) }); col.addView(btnStart)

        lastLabel = label("", 14f)
        lastRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; visibility = View.GONE }
        lastRow.addView(button("▶ Play") { play() }, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f))
        lastRow.addView(button("Share") { share() }, LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f))
        col.addView(lastLabel); col.addView(lastRow)
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
            .putBoolean("noise", cbNoise.isChecked).putBoolean("pauses", cbPauses.isChecked).apply()
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
                val eng = RecorderEngine(m, al, File(cacheDir, "take.pcm"), cbNoise.isChecked, listener)
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
            redUntil = SystemClock.elapsedRealtime() + 800
            beep.startTone(ToneGenerator.TONE_SUP_ERROR, 250)
            (getSystemService(VIBRATOR_MANAGER_SERVICE) as VibratorManager).defaultVibrator.vibrate(VibrationEffect.createOneShot(250, 255))
            heardText.text = "✗ Galat: \"$heard\"  — dobara boliye"
            render(); ui.postDelayed({ render() }, 820)
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
        heardText.text = "Saving…"
        val shorten = cbPauses.isChecked; val denoise = cbNoise.isChecked
        thread {
            try {
                val res = e.stop()
                val x = AudioExporter.readRaw(res.rawFile)
                val y = AudioExporter.process(x, res.sampleRate, res.cuts, shorten, denoise)
                val name = "voiceover_" + SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date()) + ".wav"
                val uri = saveWav(name, AudioExporter.wavBytes(y, res.sampleRate))
                ui.post {
                    lastUri = uri
                    lastLabel.text = "✅ Saved: Music/HindiVoiceover/$name  (${y.size / res.sampleRate} s, ${res.cuts.size} cuts)"
                    lastRow.visibility = View.VISIBLE
                    showSetup()
                }
            } catch (ex: Exception) {
                ui.post { toast("Save failed: ${ex.message}"); showSetup() }
            }
        }
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
        recView.visibility = View.GONE; setup.visibility = View.VISIBLE
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
        } else super.onBackPressed()
    }

    override fun onDestroy() { super.onDestroy(); player?.release(); engine?.stop() }

    private fun toast(t: String) { Toast.makeText(this, t, Toast.LENGTH_LONG).show() }
}
