package com.babu.voiceover

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.sin

class AudioExporterTest {
    private val sr = 48000
    private fun tone(sec: Double, f: Double, amp: Float) = FloatArray((sec * sr).toInt()) { (amp * sin(2 * PI * f * it / sr)).toFloat() }

    @Test fun cutsRemoveWrongTakeAndBeep() {
        // 1 s good word, 0.5 s wrong word, 1 s good word
        val x = tone(1.0, 220.0, 0.3f) + tone(0.5, 330.0, 0.3f) + tone(1.0, 220.0, 0.3f)
        val y = AudioExporter.applyCuts(x, sr, listOf(Cut(1.0, 1.5)))
        val expected = (2.0 * sr).toInt() - (0.015 * sr).toInt()   // minus one crossfade overlap
        assertEquals(expected.toDouble(), y.size.toDouble(), sr * 0.002)
        // overlapping cuts are merged
        val z = AudioExporter.applyCuts(x, sr, listOf(Cut(1.0, 1.3), Cut(1.2, 1.5), Cut(-1.0, 0.0)))
        assertEquals(y.size, z.size)
    }

    @Test fun gateSilencesBackgroundButKeepsVoice() {
        val noise = FloatArray(sr) { ((it * 7919 % 1000) / 1000f - 0.5f) * 0.004f }   // faint hiss
        val x = noise + tone(1.0, 200.0, 0.4f) + noise
        val y = AudioExporter.gate(x, sr)
        val hissIn = noise.map { abs(it) }.average(); val hissOut = (0 until sr / 2).map { abs(y[it]) }.average()
        assertTrue("hiss reduced", hissOut < hissIn * 0.2)
        val voiceOut = (sr + sr / 4 until sr + 3 * sr / 4).map { abs(y[it]) }.average()
        assertTrue("voice kept", voiceOut > 0.2)
    }

    @Test fun wavHeaderIsValid() {
        val b = AudioExporter.wavBytes(FloatArray(480), sr)
        assertEquals(44 + 960, b.size)
        assertEquals("RIFF", String(b, 0, 4)); assertEquals("WAVE", String(b, 8, 4))
    }
}
