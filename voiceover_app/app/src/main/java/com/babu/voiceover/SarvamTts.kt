package com.babu.voiceover

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Sarvam AI "Bulbul" Hindi text-to-speech + Roman-Hindi -> Devanagari transliteration. */
class SarvamTts(private val apiKey: String, private val baseUrl: String = "https://api.sarvam.ai") {

    data class Voice(val id: String, val label: String)

    companion object {
        val MODELS = listOf("bulbul:v2", "bulbul:v3")
        /** Bulbul v2 Hindi voices. Any other voice ID can be typed in the app. */
        val VOICES = listOf(
            Voice("abhilash", "Abhilash — male, deep"), Voice("karun", "Karun — male"), Voice("hitesh", "Hitesh — male"),
            Voice("anushka", "Anushka — female"), Voice("manisha", "Manisha — female"),
            Voice("vidya", "Vidya — female"), Voice("arya", "Arya — female"),
        )
        const val CHUNK_CHARS = 450
        const val TRANSLIT_CHARS = 900

        /** Split long scripts at sentence ends (।  .  ?  !) so each request stays under the API limit. */
        fun chunk(text: String, max: Int = CHUNK_CHARS): List<String> {
            val sentences = Regex("(?<=[।.!?])\\s+").split(text.trim()).filter { it.isNotBlank() }
            val out = mutableListOf<String>(); val cur = StringBuilder()
            for (s0 in sentences) {
                var s = s0.trim()
                while (s.length > max) {   // very long sentence: split at the last space before the limit
                    val cut = s.lastIndexOf(' ', max).takeIf { it > max / 2 } ?: max
                    if (cur.isNotEmpty()) { out += cur.toString(); cur.clear() }
                    out += s.substring(0, cut).trim(); s = s.substring(cut).trim()
                }
                if (cur.length + s.length + 1 > max && cur.isNotEmpty()) { out += cur.toString(); cur.clear() }
                if (cur.isNotEmpty()) cur.append(' ')
                cur.append(s)
            }
            if (cur.isNotEmpty()) out += cur.toString()
            return out
        }

        /** Decodes a WAV (16-bit PCM) to floats; returns samples and sample rate. */
        fun decodeWav(bytes: ByteArray): Pair<FloatArray, Int> {
            val bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
            require(bytes.size > 44 && String(bytes, 0, 4) == "RIFF") { "Not a WAV file" }
            var pos = 12; var sr = 22050; var ch = 1; var bits = 16
            while (pos + 8 <= bytes.size) {
                val id = String(bytes, pos, 4); val len = bb.getInt(pos + 4)
                if (id == "fmt ") { ch = bb.getShort(pos + 10).toInt(); sr = bb.getInt(pos + 12); bits = bb.getShort(pos + 22).toInt() }
                if (id == "data") {
                    require(bits == 16) { "Unsupported WAV ($bits-bit)" }
                    val end = minOf(bytes.size, pos + 8 + if (len <= 0) bytes.size else len)
                    val n = (end - pos - 8) / 2 / ch
                    return FloatArray(n) { i -> bb.getShort(pos + 8 + i * 2 * ch) / 32768f } to sr
                }
                pos += 8 + len + (len and 1)
            }
            error("WAV has no data")
        }

        fun hasDevanagari(s: String) = Romanizer.isDevanagari(s)
    }

    private fun post(url: String, body: JSONObject): Pair<Int, String> {
        val c = URL(url).openConnection() as HttpURLConnection
        c.requestMethod = "POST"; c.connectTimeout = 20000; c.readTimeout = 90000; c.doOutput = true
        c.setRequestProperty("Content-Type", "application/json")
        c.setRequestProperty("api-subscription-key", apiKey)
        c.outputStream.use { it.write(body.toString().toByteArray()) }
        val code = c.responseCode
        val text = (if (code in 200..299) c.inputStream else c.errorStream)?.bufferedReader()?.readText() ?: ""
        c.disconnect()
        return code to text
    }

    private fun fail(code: Int, body: String): Nothing {
        val msg = runCatching { JSONObject(body).let { it.optJSONObject("error")?.optString("message") ?: it.optString("detail", it.optString("message")) } }.getOrNull()
        throw IllegalStateException(when (code) {
            401, 403 -> "API key not accepted (HTTP $code). Check your Sarvam key."
            429 -> "Sarvam rate limit / credits exhausted (HTTP 429). Try again later."
            else -> "Sarvam error HTTP $code: ${msg?.takeIf { it.isNotBlank() } ?: body.take(300)}"
        })
    }

    /** Roman Hindi ("kya aap") -> Devanagari ("क्या आप"), sentence by sentence. */
    fun transliterate(text: String): String = chunk(text, TRANSLIT_CHARS).joinToString(" ") { part ->
        val (code, body) = post("$baseUrl/transliterate", JSONObject().put("input", part)
            .put("source_language_code", "en-IN").put("target_language_code", "hi-IN"))
        if (code !in 200..299) fail(code, body)
        JSONObject(body).optString("transliterated_text", part)
    }

    /**
     * Speaks [text] (Devanagari or Hindi) and returns mono samples + sample rate.
     * Sends the current request format; if the server rejects the body (400/422) it retries with the
     * older format, so the app keeps working across API versions.
     */
    fun speak(text: String, model: String, speaker: String, pace: Double, pitch: Double,
              progress: (Int, Int) -> Unit = { _, _ -> }): Pair<FloatArray, Int> {
        val parts = chunk(text)
        val pcm = mutableListOf<FloatArray>(); var rate = 24000
        parts.forEachIndexed { i, part ->
            progress(i, parts.size)
            val common = { o: JSONObject ->
                o.put("target_language_code", "hi-IN").put("speaker", speaker).put("model", model)
                    .put("pace", pace).put("speech_sample_rate", 24000)
                if (model == "bulbul:v2") o.put("pitch", pitch).put("loudness", 1.0).put("enable_preprocessing", true)
                o
            }
            var (code, body) = post("$baseUrl/text-to-speech", common(JSONObject().put("text", part)))
            if (code == 400 || code == 422) {
                val retry = post("$baseUrl/text-to-speech", common(JSONObject().put("inputs", JSONArray().put(part))))
                if (retry.first in 200..299) { code = retry.first; body = retry.second }
            }
            if (code !in 200..299) fail(code, body)
            val audios = JSONObject(body).optJSONArray("audios") ?: error("Sarvam returned no audio")
            for (k in 0 until audios.length()) {
                val wav = java.util.Base64.getDecoder().decode(audios.getString(k))
                val (x, sr) = decodeWav(wav); rate = sr; pcm += x
            }
        }
        progress(parts.size, parts.size)
        // join chunks with a short natural pause
        val gap = FloatArray((0.25 * rate).toInt())
        val total = pcm.sumOf { it.size } + gap.size * (pcm.size - 1).coerceAtLeast(0)
        val y = FloatArray(total); var n = 0
        pcm.forEachIndexed { i, x -> if (i > 0) n += gap.size; System.arraycopy(x, 0, y, n, x.size); n += x.size }
        return y to rate
    }
}
