package com.babu.voiceover

import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.sin

class VoiceFxTest {
    private val sr = 48000

    @Test fun everyPresetIsSafeAndFast() {
        // voice-like test signal: 3 harmonics with a syllable envelope, plus pauses
        val x = FloatArray(sr * 6) { i ->
            val t = i / sr.toDouble(); val env = if ((t * 3).toInt() % 3 == 2) 0.0 else sin(PI * ((t * 3) % 1.0))
            (env * (0.3 * sin(2 * PI * 140 * t) + 0.15 * sin(2 * PI * 280 * t) + 0.05 * sin(2 * PI * 4200 * t))).toFloat()
        }
        for (p in VoicePreset.values()) {
            val t0 = System.nanoTime()
            val y = VoiceFx.apply(x, sr, p)
            val ms = (System.nanoTime() - t0) / 1e6
            assertTrue("$p length", y.size >= x.size)
            assertTrue("$p finite", y.all { it.isFinite() })
            assertTrue("$p peak ${y.maxOf { abs(it) }}", y.maxOf { abs(it) } <= 0.9f)
            val active = y.filter { abs(it) > 0.01f }
            val rms = kotlin.math.sqrt(active.sumOf { (it * it).toDouble() } / active.size)
            assertTrue("$p loudness $rms", rms in 0.06..0.2)   // speech-like level, about -18 dBFS
            println("FX $p ${"%.0f".format(ms)} ms for 6 s")
        }
    }

    @Test fun humanizeIsSafe() {
        val x = FloatArray(sr * 3) { i -> val t = i / sr.toDouble(); (0.3 * sin(2 * PI * 150 * t) * (if (t in 1.0..1.5) 0.0 else 1.0)).toFloat() }
        val y = VoiceFx.humanize(x, sr)
        assertTrue(y.size == x.size && y.all { it.isFinite() } && y.maxOf { abs(it) } <= 0.9f)
        // silence becomes faint room tone, not dead digital zero
        val gap = (sr * 1.2).toInt() until (sr * 1.3).toInt()
        val level = gap.map { abs(y[it]) }.average()
        assertTrue("room tone $level", level in 0.00005..0.01)
    }

    /** Optional: FX_DEMO_IN=voice.wav (48 kHz mono 16-bit) FX_DEMO_OUT=dir -> one demo file per preset. */
    @Test fun renderDemos() {
        val inp = System.getenv("FX_DEMO_IN") ?: return
        val out = File(System.getenv("FX_DEMO_OUT") ?: return).apply { mkdirs() }
        val b = File(inp).readBytes()
        val sb = ByteBuffer.wrap(b, 44, b.size - 44).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer()
        val x = FloatArray(sb.remaining()) { sb.get(it) / 32768f }
        for ((i, p) in VoicePreset.values().withIndex())
            File(out, "${i + 1}_${p.name.lowercase()}.wav").writeBytes(AudioExporter.wavBytes(VoiceFx.apply(x, sr, p), sr))
    }
}
