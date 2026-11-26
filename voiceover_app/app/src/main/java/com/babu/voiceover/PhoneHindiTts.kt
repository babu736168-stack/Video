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
                .getOrDefault(emptyList()).sortedWith(compareByDescending<Voice> { it.quality }.thenBy { it.isNetworkConnectionRequired }.thenBy { it.name })
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

    /** Speaks Devanagari text into audio; long scripts are split at sentence ends and joined with short pauses. */
    fun synthesize(text: String, voice: Voice?, rate: Float, pitch: Float, progress: (Int, Int) -> Unit): Pair<FloatArray, Int> {
        if (voice != null) tts.voice = voice else tts.language = hindi
        tts.setSpeechRate(rate); tts.setPitch(pitch)
        val parts = SarvamTts.chunk(text, minOf(TextToSpeech.getMaxSpeechInputLength() - 50, 1500))
        val pcm = mutableListOf<FloatArray>(); var rate0 = 24000
        for ((i, part) in parts.withIndex()) {
            progress(i, parts.size)
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
            val (x, sr) = SarvamTts.decodeWav(f.readBytes()); rate0 = sr; pcm += x; f.delete()
        }
        progress(parts.size, parts.size)
        val gap = (0.25 * rate0).toInt()
        val y = FloatArray(pcm.sumOf { it.size } + gap * (pcm.size - 1).coerceAtLeast(0)); var n = 0
        pcm.forEachIndexed { i, x -> if (i > 0) n += gap; System.arraycopy(x, 0, y, n, x.size); n += x.size }
        return y to rate0
    }

    fun shutdown() = runCatching { tts.shutdown() }
}
