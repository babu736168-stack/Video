package com.babu.voiceover

import android.content.Context
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import java.io.File
import java.util.Locale
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * FREE Hindi voice: the phone's own Google text-to-speech (no account, no key, no charges).
 * "network" voices are the most natural (need internet, still free); "local" voices work offline.
 */
class PhoneHindiTts(private val ctx: Context, onReady: (PhoneHindiTts, String?) -> Unit) {
    private val hindi = Locale("hi", "IN")
    private lateinit var tts: TextToSpeech
    var voices: List<Voice> = emptyList(); private set

    init {
        val listener = TextToSpeech.OnInitListener { status ->
            if (status != TextToSpeech.SUCCESS) { onReady(this, "Text-to-speech engine not available on this phone"); return@OnInitListener }
            val r = tts.setLanguage(hindi)
            voices = runCatching { tts.voices.filter { it.locale.language == "hi" && !it.features.contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED) } }
                .getOrDefault(emptyList()).sortedWith(compareByDescending<Voice> { it.quality }.thenByDescending { it.isNetworkConnectionRequired }.thenBy { it.name })
            onReady(this, if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED)
                "Hindi voice data is not installed. Open: Settings → Text-to-speech → Google → Install voice data → हिन्दी" else null)
        }
        // prefer Google's engine (best Hindi voices); fall back to the phone's default engine
        tts = runCatching { TextToSpeech(ctx, listener, "com.google.android.tts") }.getOrElse { TextToSpeech(ctx, listener) }
    }

    fun label(v: Voice): String {
        val kind = if (v.isNetworkConnectionRequired) "online, most natural" else "offline"
        val q = when { v.quality >= Voice.QUALITY_VERY_HIGH -> "★★★"; v.quality >= Voice.QUALITY_HIGH -> "★★"; else -> "★" }
        return "${v.name.removePrefix("hi-in-x-").removePrefix("hi-IN-")}  ($kind) $q"
    }

    /**
     * Speaks Devanagari text sentence by sentence. To sound less robotic, every sentence gets a slightly
     * different pitch and pace (as a human speaker does), questions rise a little, and pauses follow the
     * punctuation (longer after "…", "?" and "!").
     */
    fun synthesize(text: String, voice: Voice?, rate: Float, pitch: Float, progress: (Int, Int) -> Unit): Pair<FloatArray, Int> {
        if (voice != null) tts.voice = voice else tts.language = hindi
        val max = minOf(TextToSpeech.getMaxSpeechInputLength() - 50, 1500)
        val sentences = Regex("(?<=[।.!?…])\\s+").split(text.trim()).filter { it.isNotBlank() }.flatMap { SarvamTts.chunk(it, max) }
        val rateVar = floatArrayOf(0f, 0.03f, -0.02f, 0.015f, -0.025f, 0.01f)
        val pitchVar = floatArrayOf(0f, -0.02f, 0.02f, -0.01f, 0.015f, -0.015f)
        val pcm = mutableListOf<Pair<FloatArray, Double>>(); var rate0 = 24000
        for ((i, part) in sentences.withIndex()) {
            progress(i, sentences.size)
            val question = part.trimEnd().endsWith("?")
            tts.setSpeechRate(rate * (1 + rateVar[i % rateVar.size]))
            tts.setPitch(pitch * (1 + pitchVar[i % pitchVar.size] + if (question) 0.03f else 0f))
            val f = File(ctx.cacheDir, "tts_$i.wav")
            val latch = CountDownLatch(1); var err: String? = null
            tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(id: String?) {}
                override fun onDone(id: String?) { latch.countDown() }
                @Deprecated("Deprecated in Java") override fun onError(id: String?) { err = "Voice engine error"; latch.countDown() }
                override fun onError(id: String?, code: Int) { err = "Voice engine error ($code)" + if (code == TextToSpeech.ERROR_NETWORK || code == TextToSpeech.ERROR_NETWORK_TIMEOUT) " — this voice needs internet, choose an offline voice" else ""; latch.countDown() }
            })
            if (tts.synthesizeToFile(part, Bundle(), f, "u$i") != TextToSpeech.SUCCESS) throw IllegalStateException("Could not start the voice engine")
            if (!latch.await(120, TimeUnit.SECONDS)) throw IllegalStateException("Voice engine timed out")
            err?.let { throw IllegalStateException(it) }
            val (x, sr) = SarvamTts.decodeWav(f.readBytes()); rate0 = sr; f.delete()
            val end = part.trimEnd()
            val pause = when {
                end.endsWith("…") || end.endsWith("...") -> 0.6
                end.endsWith("?") || end.endsWith("!") -> 0.45
                end.endsWith("।") || end.endsWith(".") -> 0.38
                else -> 0.25
            }
            pcm += trimEdges(x, sr) to pause
        }
        progress(sentences.size, sentences.size)
        val total = pcm.sumOf { it.first.size } + pcm.dropLast(1).sumOf { (it.second * rate0).toInt() }
        val y = FloatArray(total); var n = 0
        pcm.forEachIndexed { i, (x, pause) ->
            System.arraycopy(x, 0, y, n, x.size); n += x.size
            if (i < pcm.size - 1) n += (pause * rate0).toInt()
        }
        return VoiceFx.humanize(y, rate0) to rate0
    }

    /** Removes the engine's own leading/trailing silence so our pauses are exact. */
    private fun trimEdges(x: FloatArray, sr: Int): FloatArray {
        var a = 0; var b = x.size - 1
        while (a < b && kotlin.math.abs(x[a]) < 0.003f) a++
        while (b > a && kotlin.math.abs(x[b]) < 0.003f) b--
        val pad = (0.03 * sr).toInt()
        return x.copyOfRange(maxOf(0, a - pad), minOf(x.size, b + pad + 1))
    }

    fun shutdown() = runCatching { tts.shutdown() }
}
