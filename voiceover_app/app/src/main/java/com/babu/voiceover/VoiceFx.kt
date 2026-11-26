package com.babu.voiceover

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.log10
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt
import kotlin.math.tanh

/**
 * "Voice Studio" effects (like karaoke apps): EQ, compression, de-essing, warmth, reverb, echo.
 * Pure Kotlin DSP so it works offline on any phone.
 */
enum class VoicePreset(val title: String, val hint: String) {
    NATURAL("Natural", "Saaf, asli awaaz — sirf volume barabar"),
    STUDIO("Studio", "Professional studio sound, halka room"),
    WARM("Warm", "Garam, bhari awaaz — storytelling ke liye"),
    DEEP("Deep Radio", "Gehri, dramatic awaaz — documentary / news"),
    BRIGHT("Bright & Clear", "Saaf aur chamakdar — har shabd clear"),
    HALL("Concert Hall", "Bade hall ka reverb — dramatic intro"),
    ECHO("Echo (KTV)", "Echo ke saath — mysterious feel"),
}

object VoiceFx {

    fun apply(input: FloatArray, sr: Int, p: VoicePreset): FloatArray {
        val tail = when (p) { VoicePreset.HALL -> 2.0; VoicePreset.ECHO -> 1.6; VoicePreset.STUDIO, VoicePreset.WARM, VoicePreset.BRIGHT -> 0.6; else -> 0.0 }
        var x = if (tail > 0) input + FloatArray((tail * sr).toInt()) else input.copyOf()
        x = biquad(x, Biquad.highPass(sr, 85.0))
        when (p) {
            VoicePreset.NATURAL -> {
                x = compress(x, sr, thrDb = -22.0, ratio = 2.0, attackMs = 10.0, releaseMs = 150.0)
            }
            VoicePreset.STUDIO -> {
                x = eq(x, sr, low = 0.0, mud = -2.5, presence = 3.0, air = 2.5)
                x = deEss(x, sr, 0.5)
                x = compress(x, sr, -20.0, 3.0, 6.0, 120.0)
                x = reverb(x, sr, room = 0.55, damp = 0.45, wet = 0.10)
            }
            VoicePreset.WARM -> {
                x = eq(x, sr, low = 3.5, mud = -1.0, presence = 1.0, air = -1.5)
                x = compress(x, sr, -22.0, 3.0, 8.0, 150.0)
                x = saturate(x, 1.4)
                x = reverb(x, sr, room = 0.5, damp = 0.6, wet = 0.08)
            }
            VoicePreset.DEEP -> {
                x = eq(x, sr, low = 5.5, mud = -2.5, presence = 3.0, air = 0.5)
                x = deEss(x, sr, 0.4)
                x = compress(x, sr, -24.0, 3.0, 5.0, 110.0)
                x = saturate(x, 1.8)
            }
            VoicePreset.BRIGHT -> {
                x = eq(x, sr, low = -1.5, mud = -2.0, presence = 4.0, air = 4.0)
                x = deEss(x, sr, 0.7)
                x = compress(x, sr, -20.0, 2.5, 6.0, 120.0)
                x = reverb(x, sr, room = 0.45, damp = 0.4, wet = 0.06)
            }
            VoicePreset.HALL -> {
                x = eq(x, sr, low = 1.5, mud = -2.0, presence = 2.5, air = 2.0)
                x = deEss(x, sr, 0.5)
                x = compress(x, sr, -20.0, 3.0, 6.0, 120.0)
                x = reverb(x, sr, room = 0.86, damp = 0.35, wet = 0.24)
            }
            VoicePreset.ECHO -> {
                x = eq(x, sr, low = 1.0, mud = -2.0, presence = 2.5, air = 1.5)
                x = compress(x, sr, -20.0, 3.0, 6.0, 120.0)
                x = echo(x, sr, delayMs = 290.0, feedback = 0.32, mix = 0.28)
                x = reverb(x, sr, room = 0.65, damp = 0.45, wet = 0.12)
            }
        }
        return finish(x, sr)
    }

    /**
     * Makes a synthetic (text-to-speech) voice sound more human: warmer tone, softer "s", gentle
     * compression, a tiny room, and very faint room tone instead of dead digital silence.
     */
    fun humanize(input: FloatArray, sr: Int): FloatArray {
        var x = biquad(input, Biquad.highPass(sr, 70.0))
        x = eq(x, sr, low = 2.0, mud = -1.0, presence = 1.5, air = 0.5)
        x = deEss(x, sr, 0.5)
        x = compress(x, sr, -22.0, 2.0, 10.0, 160.0)
        x = reverb(x, sr, room = 0.3, damp = 0.55, wet = 0.05)
        x = finish(x, sr)
        var seed = 12345L
        for (i in x.indices) {   // room tone at about -60 dBFS (pink-ish noise)
            seed = seed * 6364136223846793005L + 1442695040888963407L
            x[i] += ((seed ushr 40).toInt() / 16777216f - 0.5f) * 0.002f
        }
        return x
    }

    // ----------------------------------------------------------------- building blocks
    class Biquad(val b0: Double, val b1: Double, val b2: Double, val a1: Double, val a2: Double) {
        companion object {
            private fun make(b0: Double, b1: Double, b2: Double, a0: Double, a1: Double, a2: Double) =
                Biquad(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

            fun highPass(sr: Int, f: Double, q: Double = 0.707): Biquad {
                val w = 2 * PI * f / sr; val al = sin(w) / (2 * q); val c = cos(w)
                return make((1 + c) / 2, -(1 + c), (1 + c) / 2, 1 + al, -2 * c, 1 - al)
            }
            fun peaking(sr: Int, f: Double, db: Double, q: Double): Biquad {
                val a = 10.0.pow(db / 40); val w = 2 * PI * f / sr; val al = sin(w) / (2 * q); val c = cos(w)
                return make(1 + al * a, -2 * c, 1 - al * a, 1 + al / a, -2 * c, 1 - al / a)
            }
            fun lowShelf(sr: Int, f: Double, db: Double): Biquad {
                val a = 10.0.pow(db / 40); val w = 2 * PI * f / sr; val c = cos(w); val s = sin(w)
                val al = s / 2 * sqrt(2.0); val sq = 2 * sqrt(a) * al
                return make(a * ((a + 1) - (a - 1) * c + sq), 2 * a * ((a - 1) - (a + 1) * c), a * ((a + 1) - (a - 1) * c - sq),
                    (a + 1) + (a - 1) * c + sq, -2 * ((a - 1) + (a + 1) * c), (a + 1) + (a - 1) * c - sq)
            }
            fun highShelf(sr: Int, f: Double, db: Double): Biquad {
                val a = 10.0.pow(db / 40); val w = 2 * PI * f / sr; val c = cos(w); val s = sin(w)
                val al = s / 2 * sqrt(2.0); val sq = 2 * sqrt(a) * al
                return make(a * ((a + 1) + (a - 1) * c + sq), -2 * a * ((a - 1) + (a + 1) * c), a * ((a + 1) + (a - 1) * c - sq),
                    (a + 1) - (a - 1) * c + sq, 2 * ((a - 1) - (a + 1) * c), (a + 1) - (a - 1) * c - sq)
            }
        }
    }

    fun biquad(x: FloatArray, f: Biquad): FloatArray {
        var x1 = 0.0; var x2 = 0.0; var y1 = 0.0; var y2 = 0.0
        return FloatArray(x.size) { i ->
            val v = x[i].toDouble()
            val y = f.b0 * v + f.b1 * x1 + f.b2 * x2 - f.a1 * y1 - f.a2 * y2
            x2 = x1; x1 = v; y2 = y1; y1 = y; y.toFloat()
        }
    }

    /** low = bass shelf @150 Hz, mud = cut @300 Hz, presence = boost @3.5 kHz, air = shelf @10 kHz (all dB). */
    fun eq(x0: FloatArray, sr: Int, low: Double, mud: Double, presence: Double, air: Double): FloatArray {
        var x = x0
        if (low != 0.0) x = biquad(x, Biquad.lowShelf(sr, 150.0, low))
        if (mud != 0.0) x = biquad(x, Biquad.peaking(sr, 300.0, mud, 1.0))
        if (presence != 0.0) x = biquad(x, Biquad.peaking(sr, 3500.0, presence, 0.9))
        if (air != 0.0) x = biquad(x, Biquad.highShelf(sr, 10000.0, air))
        return x
    }

    /** Feed-forward compressor with automatic make-up gain. */
    fun compress(x: FloatArray, sr: Int, thrDb: Double, ratio: Double, attackMs: Double, releaseMs: Double): FloatArray {
        val at = exp(-1.0 / (attackMs * 0.001 * sr)); val rl = exp(-1.0 / (releaseMs * 0.001 * sr))
        var env = 0.0
        val makeup = 10.0.pow((-thrDb * (1 - 1 / ratio)) * 0.5 / 20)
        return FloatArray(x.size) { i ->
            val a = abs(x[i].toDouble())
            env = if (a > env) a + (env - a) * at else a + (env - a) * rl
            val db = 20 * log10(env + 1e-9)
            val over = db - thrDb
            val gainDb = if (over > 0) -over * (1 - 1 / ratio) else 0.0
            (x[i] * 10.0.pow(gainDb / 20) * makeup).toFloat()
        }
    }

    /** Tames harsh "s"/"sh" sounds: compresses only the 5 kHz+ band. */
    fun deEss(x: FloatArray, sr: Int, amount: Double): FloatArray {
        val hi = biquad(x, Biquad.highPass(sr, 5000.0))
        val rl = exp(-1.0 / (0.06 * sr)); val at = exp(-1.0 / (0.002 * sr))
        var env = 0.0; val thr = 0.04
        return FloatArray(x.size) { i ->
            val a = abs(hi[i].toDouble())
            env = if (a > env) a + (env - a) * at else a + (env - a) * rl
            val g = if (env > thr) 1 - amount * (1 - thr / env) else 1.0
            (x[i] - hi[i] + hi[i] * g).toFloat()
        }
    }

    /** Gentle tube-like warmth. Level is normalised first so the drive is always the same, never harsh. */
    fun saturate(x: FloatArray, drive: Double): FloatArray {
        var peak = 0f; for (v in x) peak = maxOf(peak, abs(v))
        val pre = if (peak > 1e-5f) 0.5f / peak else 1f
        val n = tanh(drive * 0.5)
        return FloatArray(x.size) { (tanh(drive * x[it] * pre) / n * 0.5).toFloat() }
    }

    /** Freeverb-style reverb (8 combs + 4 allpasses), mixed in parallel. */
    fun reverb(x: FloatArray, sr: Int, room: Double, damp: Double, wet: Double): FloatArray {
        val scale = sr / 44100.0
        val combs = intArrayOf(1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617).map { (it * scale).toInt() }
        val aps = intArrayOf(556, 441, 341, 225).map { (it * scale).toInt() }
        val pre = (0.02 * sr).toInt()
        val out = FloatArray(x.size)
        val cb = combs.map { FloatArray(it) }; val ci = IntArray(combs.size); val cl = DoubleArray(combs.size)
        val ab = aps.map { FloatArray(it) }; val ai = IntArray(aps.size)
        val fb = 0.7 + 0.28 * room
        for (n in x.indices) {
            val inp = (if (n >= pre) x[n - pre] else 0f) * 0.015
            var s = 0.0
            for (k in combs.indices) {
                val buf = cb[k]; val o = buf[ci[k]].toDouble()
                cl[k] = o * (1 - damp) + cl[k] * damp
                buf[ci[k]] = (inp + cl[k] * fb).toFloat()
                ci[k] = (ci[k] + 1) % buf.size; s += o
            }
            for (k in aps.indices) {
                val buf = ab[k]; val o = buf[ai[k]].toDouble()
                buf[ai[k]] = (s + o * 0.5).toFloat()
                s = o - s; ai[k] = (ai[k] + 1) % buf.size
            }
            out[n] = (x[n] * (1 - wet * 0.5) + s * wet * 3.0).toFloat()
        }
        return out
    }

    fun echo(x: FloatArray, sr: Int, delayMs: Double, feedback: Double, mix: Double): FloatArray {
        val d = (delayMs * 0.001 * sr).toInt()
        val buf = FloatArray(d); var i = 0; var lp = 0.0
        return FloatArray(x.size) { n ->
            val delayed = buf[i].toDouble()
            lp = delayed * 0.6 + lp * 0.4             // darker repeats
            buf[i] = (x[n] + lp * feedback).toFloat()
            i = (i + 1) % d
            (x[n] + delayed * mix).toFloat()
        }
    }

    /** Peak limiter + loudness: speech RMS around -18 dBFS, never above -1 dBFS. */
    fun finish(x: FloatArray, sr: Int): FloatArray {
        var sum = 0.0; var cnt = 0
        for (v in x) if (abs(v) > 0.01f) { sum += v * v; cnt++ }
        val rms = if (cnt > 0) sqrt(sum / cnt) else 0.0
        val g = if (rms > 1e-5) (0.125 / rms).coerceIn(0.2, 8.0) else 1.0
        val ceil = 0.89
        return FloatArray(x.size) { i ->
            val v = x[i] * g
            (if (abs(v) <= 0.7) v else (0.7 + (ceil - 0.7) * tanh((abs(v) - 0.7) / (ceil - 0.7))) * Math.signum(v)).toFloat()
        }
    }
}
