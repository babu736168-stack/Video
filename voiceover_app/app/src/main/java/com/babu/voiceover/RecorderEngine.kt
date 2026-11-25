package com.babu.voiceover

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.media.audiofx.NoiseSuppressor
import org.json.JSONObject
import org.vosk.Model
import org.vosk.Recognizer
import java.io.BufferedOutputStream
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.abs
import kotlin.math.sqrt

/** Time range (seconds from recording start) to remove from the final voiceover. */
data class Cut(val start: Double, val end: Double)

data class RecordingResult(val rawFile: File, val sampleRate: Int, val cuts: List<Cut>, val seconds: Double)

/**
 * Records from the microphone in studio quality (48 kHz) and, at the same time, feeds a 16 kHz copy
 * to the offline Hindi recognizer. Word results drive the [Aligner]; wrong words and the error beep
 * are remembered as [Cut]s so the exported file only contains correctly pronounced words.
 */
class RecorderEngine(
    private val model: Model,
    private val aligner: Aligner,
    private val rawFile: File,
    private val noiseSuppression: Boolean,
    private val vibrateOnError: Boolean,
    private val listener: Listener,
) {
    interface Listener {
        fun onProgress(committed: Int, preview: Int, heard: String)   // called on the recording thread
        fun onWrong(heard: String)
        fun onLevel(level: Float)
        fun onFinishedScript()
        fun onFailure(e: Throwable)
    }

    @Volatile private var running = false
    @Volatile var paused = false
    private var thread: Thread? = null
    private val cuts = mutableListOf<Cut>()
    private val spoken = ArrayDeque<Heard>()   // audio of each accepted word, so "Back" can cut it again
    private val pending = mutableListOf<() -> Unit>()   // UI commands (skip/back) run on the audio thread
    var sampleRate = 48000; private set
    private var fedSamples16k = 0L
    private var muteRecognizerUntil = 0L  // in 16k samples: ignore our own beep

    fun post(cmd: () -> Unit) = synchronized(pending) { pending += cmd }

    @SuppressLint("MissingPermission")
    fun start() {
        running = true
        thread = Thread({ try { loop() } catch (e: Throwable) { listener.onFailure(e) } }, "recorder").apply { start() }
    }

    fun stop(): RecordingResult {
        running = false
        thread?.join(4000)
        return RecordingResult(rawFile, sampleRate, synchronized(cuts) { cuts.toList() }, fedSamples16k / 16000.0)
    }

    /** The app makes NO sound on errors. Only if the user enabled vibration, the short buzz is cut out. */
    private fun cutVibration() {
        val now = fedSamples16k / 16000.0
        synchronized(cuts) { cuts += Cut(now - 0.03, now + 0.35) }
        muteRecognizerUntil = fedSamples16k + (0.35 * 16000).toLong()
    }

    @SuppressLint("MissingPermission")
    private fun loop() {
        val rates = intArrayOf(48000, 16000)
        var rec: AudioRecord? = null
        for (r in rates) {
            val min = AudioRecord.getMinBufferSize(r, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
            if (min <= 0) continue
            val a = AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION, r, AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT, maxOf(min, r / 5 * 2))
            if (a.state == AudioRecord.STATE_INITIALIZED) { rec = a; sampleRate = r; break } else a.release()
        }
        val audio = rec ?: throw IllegalStateException("Microphone not available")
        val ns = if (noiseSuppression && NoiseSuppressor.isAvailable()) NoiseSuppressor.create(audio.audioSessionId)?.apply { enabled = true } else null
        val factor = sampleRate / 16000
        val recognizer = Recognizer(model, 16000f).apply { setWords(true); setPartialWords(true) }
        val chunk = sampleRate / 10           // 100 ms
        val buf = ShortArray(chunk)
        val down = ShortArray(chunk / factor)
        val bytes = ByteBuffer.allocate(chunk * 2).order(ByteOrder.LITTLE_ENDIAN)
        BufferedOutputStream(FileOutputStream(rawFile), 1 shl 16).use { out ->
            audio.startRecording()
            try {
                while (running) {
                    val n = audio.read(buf, 0, chunk)
                    if (n <= 0) continue
                    synchronized(pending) { pending.forEach { it() }; pending.clear() }
                    if (paused) continue   // discard: nothing recorded, nothing recognised
                    // 1) keep the full-quality audio
                    bytes.clear(); for (i in 0 until n) bytes.putShort(buf[i]); out.write(bytes.array(), 0, n * 2)
                    // 2) level meter
                    var sum = 0.0; for (i in 0 until n) { val v = buf[i] / 32768.0; sum += v * v }
                    listener.onLevel(sqrt(sum / n).toFloat())
                    // 3) 16 kHz copy for the recognizer (average = simple anti-alias filter)
                    val m = n / factor
                    for (i in 0 until m) { var s = 0; for (k in 0 until factor) s += buf[i * factor + k]; down[i] = (s / factor).toShort() }
                    if (fedSamples16k < muteRecognizerUntil) java.util.Arrays.fill(down, 0, m, 0)
                    fedSamples16k += m
                    if (recognizer.acceptWaveForm(down, m)) handleFinal(recognizer.result) else handlePartial(recognizer.partialResult)
                    if (aligner.done) { listener.onFinishedScript(); break }
                }
                if (!aligner.done) handleFinal(recognizer.finalResult)
            } finally {
                audio.stop(); audio.release(); ns?.release(); recognizer.close()
            }
        }
    }

    private fun handlePartial(json: String) {
        val o = JSONObject(json)
        val words = o.optString("partial").split(" ").filter { it.isNotBlank() }
        listener.onProgress(aligner.index, aligner.preview(words), o.optString("partial"))
    }

    private fun handleFinal(json: String) {
        val o = JSONObject(json)
        val arr = o.optJSONArray("result") ?: run { listener.onProgress(aligner.index, aligner.index, ""); return }
        val heard = (0 until arr.length()).map { arr.getJSONObject(it) }.map { Heard(it.getString("word"), it.getDouble("start"), it.getDouble("end")) }
        val out = aligner.commit(heard)
        out.correct.forEach { spoken.addLast(it.second) }
        synchronized(cuts) {
            out.wrong.forEach { cuts += Cut(it.start - 0.08, it.end + 0.08) }
            out.fillers.forEach { cuts += Cut(it.start - 0.04, it.end + 0.04) }
        }
        listener.onProgress(out.index, out.index, o.optString("text"))
        if (out.wrong.isNotEmpty()) { if (vibrateOnError) cutVibration(); listener.onWrong(out.wrong.joinToString(" ") { it.word }) }
    }

    fun skip() = post { aligner.skip(); spoken.addLast(Heard("", -1.0, -1.0)); listener.onProgress(aligner.index, aligner.index, "") }
    fun back() = post {
        if (aligner.index > 0) {
            aligner.back()
            spoken.removeLastOrNull()?.takeIf { it.start >= 0 }?.let { synchronized(cuts) { cuts += Cut(it.start - 0.05, it.end + 0.05) } }
        }
        listener.onProgress(aligner.index, aligner.index, "")
    }

    @Suppress("unused") private fun peak(b: ShortArray, n: Int) = (0 until n).maxOf { abs(b[it].toInt()) }
}
