package com.babu.voiceover

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.net.ServerSocket
import kotlin.concurrent.thread
import java.util.Base64

class SarvamTtsTest {
    private fun wav(seconds: Double, sr: Int = 24000) = AudioExporter.wavBytes(FloatArray((seconds * sr).toInt()) { 0.1f }, sr)

    @Test fun chunksStayUnderLimitAndKeepAllText() {
        val text = (1..40).joinToString(" ") { "यह वाक्य नंबर $it है।" }
        val parts = SarvamTts.chunk(text, 120)
        assertTrue(parts.all { it.length <= 120 })
        assertEquals(text.replace(" ", ""), parts.joinToString("").replace(" ", ""))
    }

    @Test fun decodesWav() {
        val (x, sr) = SarvamTts.decodeWav(wav(0.5))
        assertEquals(24000, sr); assertEquals(12000, x.size)
    }

    @Test fun speaksViaApiWithFallbackAndJoinsChunks() {
        val seen = mutableListOf<JSONObject>(); val keys = mutableListOf<String>()
        val server = FakeServer { path, h, body ->
            if (path == "/transliterate") 200 to """{"transliterated_text":"क्या आप"}"""
            else {
                val j = JSONObject(body); synchronized(seen) { seen += j; keys += h["api-subscription-key"] ?: "" }
                // simulate an API that only accepts the older "inputs" format
                if (j.has("text")) 422 to """{"detail":"text not allowed"}"""
                else 200 to JSONObject().put("request_id", "x").put("audios", JSONArray().put(Base64.getEncoder().encodeToString(wav(1.0)))).toString()
            }
        }
        try {
            val c = SarvamTts("test-key", server.url)
            assertEquals("क्या आप", c.transliterate("kya aap"))
            val long = (1..30).joinToString(" ") { "यह एक लंबा वाक्य है जो बार बार दोहराया गया है।" }
            val (audio, sr) = c.speak(long, "bulbul:v2", "abhilash", 1.0, 0.0)
            assertEquals(24000, sr)
            val chunks = SarvamTts.chunk(long).size
            assertTrue("several requests", chunks > 1)
            // 1 s per chunk + 0.25 s pauses between chunks
            assertEquals((chunks * 1.0 + (chunks - 1) * 0.25) * sr, audio.size.toDouble(), 2.0)
            val ok = seen.first { it.has("inputs") }
            assertEquals("hi-IN", ok.getString("target_language_code")); assertEquals("abhilash", ok.getString("speaker"))
            assertEquals("bulbul:v2", ok.getString("model")); assertTrue(keys.all { it == "test-key" })
        } finally { server.stop() }
    }

    @Test fun clearMessageForBadKey() {
        val server = FakeServer { _, _, _ -> 403 to "{}" }
        try {
            val e = runCatching { SarvamTts("bad", server.url).speak("नमस्ते।", "bulbul:v2", "anushka", 1.0, 0.0) }.exceptionOrNull()
            assertTrue(e?.message ?: "", e?.message?.contains("API key") == true)
        } finally { server.stop() }
    }
}

/** Minimal HTTP/1.1 server for tests: handler(path, headers, body) -> (status, json). */
class FakeServer(val handler: (String, Map<String, String>, String) -> Pair<Int, String>) {
    private val sock = ServerSocket(0)
    val url get() = "http://127.0.0.1:${sock.localPort}"
    init {
        thread(isDaemon = true) {
            while (!sock.isClosed) {
                val c = runCatching { sock.accept() }.getOrNull() ?: break
                c.use {
                    val inp = c.getInputStream().buffered()
                    fun line(): String { val b = StringBuilder(); while (true) { val ch = inp.read(); if (ch < 0 || ch == '\n'.code) break; if (ch != '\r'.code) b.append(ch.toChar()) }; return b.toString() }
                    val path = line().split(" ").getOrElse(1) { "/" }
                    val headers = mutableMapOf<String, String>()
                    while (true) { val l = line(); if (l.isEmpty()) break; val i = l.indexOf(':'); headers[l.substring(0, i).trim().lowercase()] = l.substring(i + 1).trim() }
                    val len = headers["content-length"]?.toInt() ?: 0
                    val body = ByteArray(len); var r = 0; while (r < len) { val n = inp.read(body, r, len - r); if (n < 0) break; r += n }
                    val (code, resp) = handler(path, headers, body.decodeToString())
                    val bytes = resp.toByteArray()
                    c.getOutputStream().apply {
                        write("HTTP/1.1 $code X\r\nContent-Type: application/json\r\nContent-Length: ${bytes.size}\r\nConnection: close\r\n\r\n".toByteArray()); write(bytes); flush()
                    }
                }
            }
        }
    }
    fun stop() = sock.close()
}
