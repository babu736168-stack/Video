package com.babu.voiceover

import java.io.ByteArrayOutputStream
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.sqrt
import kotlin.math.tan

/**
 * Turns the raw take into a clean voiceover:
 *  1. removes wrong words, fillers and error beeps (with 15 ms crossfades, no clicks)
 *  2. high-pass filter (removes fan / traffic rumble below 80 Hz)
 *  3. noise gate (background hiss between words is pushed down ~30 dB)
 *  4. optionally shortens long pauses
 *  5. normalises loudness
 */
object AudioExporter {

    fun readRaw(f: File): FloatArray {
        val b = f.readBytes()
        val sb = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer()
        return FloatArray(sb.remaining()) { sb.get(it) / 32768f }
    }

    fun process(x: FloatArray, sr: Int, cuts: List<Cut>, shortenPauses: Boolean, denoise: Boolean): FloatArray {
        var y = applyCuts(x, sr, cuts)
        y = highPass(y, sr, 80.0)
        if (denoise) y = gate(y, sr)
        if (shortenPauses) y = shortenSilences(y, sr, maxPause = 0.7, keep = 0.45)
        normalize(y, 0.89f)
        return y
    }

    /** Merge overlapping cuts and drop them, crossfading the joins. */
    fun applyCuts(x: FloatArray, sr: Int, cuts: List<Cut>): FloatArray {
        if (cuts.isEmpty()) return x.copyOf()
        val ranges = cuts.map { (it.start * sr).toInt().coerceIn(0, x.size) to (it.end * sr).toInt().coerceIn(0, x.size) }
            .filter { it.second > it.first }.sortedBy { it.first }
        val merged = mutableListOf<IntArray>()
        for ((a, b) in ranges) {
            val last = merged.lastOrNull()
            if (last != null && a <= last[1]) last[1] = maxOf(last[1], b) else merged += intArrayOf(a, b)
        }
        val keep = mutableListOf<IntArray>(); var pos = 0
        for (r in merged) { if (r[0] > pos) keep += intArrayOf(pos, r[0]); pos = r[1] }
        if (pos < x.size) keep += intArrayOf(pos, x.size)
        return joinWithCrossfade(x, keep, (0.015 * sr).toInt())
    }

    private fun joinWithCrossfade(x: FloatArray, keep: List<IntArray>, fade: Int): FloatArray {
        val out = FloatArray(keep.sumOf { it[1] - it[0] })
        var n = 0
        for ((idx, seg) in keep.withIndex()) {
            val a = seg[0]; val b = seg[1]
            if (idx == 0 || n < fade || b - a < fade) { System.arraycopy(x, a, out, n, b - a); n += b - a; continue }
            val start = n - fade
            for (i in 0 until fade) {   // overlap end of previous segment with start of this one
                val t = i / fade.toFloat()
                out[start + i] = out[start + i] * (1 - t) + x[a + i] * t
            }
            System.arraycopy(x, a + fade, out, n, b - a - fade); n += b - a - fade
        }
        return out.copyOf(n)
    }

    fun highPass(x: FloatArray, sr: Int, fc: Double): FloatArray {
        val k = tan(PI * fc / sr); val q = 0.7071
        val norm = 1 / (1 + k / q + k * k)
        val b0 = norm; val b1 = -2 * norm; val b2 = norm
        val a1 = 2 * (k * k - 1) * norm; val a2 = (1 - k / q + k * k) * norm
        var x1 = 0.0; var x2 = 0.0; var y1 = 0.0; var y2 = 0.0
        return FloatArray(x.size) { i ->
            val v = x[i].toDouble()
            val r = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            x2 = x1; x1 = v; y2 = y1; y1 = r; r.toFloat()
        }
    }

    private fun frameRms(x: FloatArray, sr: Int, frame: Int): FloatArray {
        val n = x.size / frame
        return FloatArray(n) { f -> var s = 0.0; for (i in f * frame until (f + 1) * frame) s += x[i] * x[i]; sqrt(s / frame).toFloat() }
    }

    fun gate(x: FloatArray, sr: Int): FloatArray {
        val frame = sr / 50 // 20 ms
        val rms = frameRms(x, sr, frame)
        if (rms.isEmpty()) return x
        val sorted = rms.sorted()
        val floor = sorted[(sorted.size * 0.15).toInt()]
        val thr = maxOf(floor * 3f, 0.004f)
        val attack = exp(-1.0 / (0.005 * sr)); val release = exp(-1.0 / (0.12 * sr))
        var g = 0.0; val y = FloatArray(x.size)
        for (i in x.indices) {
            val f = (i / frame).coerceAtMost(rms.size - 1)
            val target = if (rms[f] > thr) 1.0 else 0.03
            g = if (target > g) target + (g - target) * attack else target + (g - target) * release
            y[i] = (x[i] * g).toFloat()
        }
        return y
    }

    fun shortenSilences(x: FloatArray, sr: Int, maxPause: Double, keep: Double): FloatArray {
        val frame = sr / 50
        val rms = frameRms(x, sr, frame)
        if (rms.isEmpty()) return x
        val thr = maxOf(rms.sorted()[(rms.size * 0.15).toInt()] * 3f, 0.004f)
        val cuts = mutableListOf<Cut>(); var runStart = -1
        for (f in 0..rms.size) {
            val silent = f < rms.size && rms[f] <= thr
            if (silent && runStart < 0) runStart = f
            if (!silent && runStart >= 0) {
                val len = (f - runStart) * frame / sr.toDouble()
                if (len > maxPause) {
                    val mid = (runStart * frame / sr.toDouble()) + keep / 2
                    cuts += Cut(mid, mid + (len - keep))
                }
                runStart = -1
            }
        }
        return applyCuts(x, sr, cuts)
    }

    fun normalize(x: FloatArray, peak: Float) {
        var m = 0f; for (v in x) m = maxOf(m, abs(v))
        if (m > 1e-4f) { val g = peak / m; for (i in x.indices) x[i] *= g }
    }

    fun wavBytes(x: FloatArray, sr: Int): ByteArray {
        val data = ByteBuffer.allocate(x.size * 2).order(ByteOrder.LITTLE_ENDIAN)
        for (v in x) data.putShort((v.coerceIn(-1f, 1f) * 32767).toInt().toShort())
        val h = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN)
        h.put("RIFF".toByteArray()); h.putInt(36 + x.size * 2); h.put("WAVE".toByteArray())
        h.put("fmt ".toByteArray()); h.putInt(16); h.putShort(1); h.putShort(1); h.putInt(sr); h.putInt(sr * 2); h.putShort(2); h.putShort(16)
        h.put("data".toByteArray()); h.putInt(x.size * 2)
        return ByteArrayOutputStream().apply { write(h.array()); write(data.array()) }.toByteArray()
    }
}
