package com.babu.voiceover

enum class Strictness { STRICT, MEDIUM, EASY }

/**
 * Decides whether a heard word (Devanagari from the recognizer, or Roman) is the expected
 * Roman-Hindi script word. Spelling variants of the SAME pronunciation always pass
 * (nahi / nahin / nahee, hai / hain, kya / kyaa ...); genuinely different words fail.
 */
class WordMatcher(var strictness: Strictness = Strictness.STRICT) {

    /** Common words whose Roman spellings vary a lot. Any member matches any other member. */
    private val groups: List<Set<String>> = listOf(
        setOf("nahi", "nahin", "nahee", "nahiin", "nhi", "nai", "nahi", "naheen"),
        setOf("hai", "hain", "he", "hei", "hae", "hay"),
        setOf("ye", "yeh", "yah", "yae", "ya"),
        setOf("wo", "woh", "vo", "voh", "vah", "wah", "vaha"),
        setOf("mein", "me", "men", "mei", "mae", "mai"),
        setOf("main", "mai", "mein", "maen", "mai"),
        setOf("kya", "kyaa", "kia", "kiya"),
        setOf("kyun", "kyon", "kyu", "kyoon", "kyoun", "kyunki", "kyonki", "kyuki"),
        setOf("hum", "ham"), setOf("aap", "ap", "aapp"), setOf("toh", "to", "tou", "tau"),
        setOf("bhi", "bhee"), setOf("hoon", "hu", "hun", "hoo", "hu"), setOf("ho", "hoo"),
        setOf("kaise", "kese", "kaisay", "kaisey"), setOf("aise", "ese", "aisay", "aisey"),
        setOf("vaise", "waise", "vese", "wese"), setOf("jaise", "jese", "jaisay"),
        setOf("aur", "or", "aor", "awr"), setOf("par", "pe", "pr"), setOf("thi", "thee"), setOf("tha", "thaa"),
        setOf("ki", "kee"), setOf("se", "say", "sey"), setOf("ko", "koo"), setOf("hi", "hee"),
        setOf("ek", "aek", "ik"), setOf("yahan", "yaha", "yahaan", "yhan"), setOf("vahan", "wahan", "waha", "vaha", "wahaan"),
        setOf("kahan", "kaha", "kahaan"), setOf("abhi", "abhee"), setOf("sabhi", "sabhee"),
    )
    private val groupIndex: Map<String, Set<Int>> = buildMap<String, MutableSet<Int>> {
        groups.forEachIndexed { i, g -> g.forEach { w -> getOrPut(key(w)) { mutableSetOf() }.add(i) } }
    }

    /** Short sounds that are ignored (cut silently) when they don't match the expected word. */
    val fillers = setOf("hm", "hmm", "hamm", "hammm", "hmmm", "um", "umm", "amm", "umh", "uh", "uhh", "ah", "aah", "ahh", "unh", "ahm", "mm", "mmm")

    /** Checked on the raw sound before normalising, so "हम्म" (hmm) is not confused with "हम" (we). */
    fun isFiller(heard: String) = toRoman(heard).lowercase().filter { it in 'a'..'z' } in fillers

    fun toRoman(w: String) = if (Romanizer.isDevanagari(w)) Romanizer.romanize(w) else w

    /** Normalised spelling: removes the usual Roman-Hindi spelling differences. */
    fun key(w0: String): String {
        var w = w0.lowercase().filter { it in 'a'..'z' }
        val reps = listOf(
            "chh" to "ch", "ksh" to "ksh", "ph" to "f", "w" to "v", "z" to "j", "q" to "k", "x" to "ks",
            "ck" to "k", "aa" to "a", "ee" to "i", "ii" to "i", "oo" to "u", "uu" to "u", "ou" to "o", "au" to "o",
            "ai" to "e", "ei" to "e", "ae" to "e", "ay" to "e", "ey" to "e", "yi" to "i",
        )
        for ((a, b) in reps) w = w.replace(a, b)
        w = w.replace(Regex("c(?!h)"), "k")
        w = w.replace(Regex("(?<=[aeiou])y(?=[aeiou])"), "")  // dekhiye -> dekhie, aaye -> aae
        w = w.replace(Regex("(.)\\1+"), "$1")              // pakka -> paka
        if (w.length > 2 && w.endsWith("h") && w[w.length - 2] in "aeiou") w = w.dropLast(1)  // yeh -> ye
        if (w.length > 2 && w.endsWith("n") && w[w.length - 2] in "aeiou") w = w.dropLast(1)  // nahin -> nahi (nasal)
        return w
    }

    private fun skeleton(k: String) = k.filter { it !in "aeiou" }

    fun matches(scriptWord: String, heardWord: String): Boolean {
        val a = key(scriptWord)
        val b = key(toRoman(heardWord))
        if (a.isEmpty() || b.isEmpty()) return false
        if (a == b) return true
        val ga = groupIndex[a]; val gb = groupIndex[b]
        if (ga != null && gb != null && ga.any { it in gb }) return true
        val sim = similarity(a, b)
        val sd = levenshtein(skeleton(a), skeleton(b))
        return when (strictness) {
            // short words (ka/ki/ke, kya/kyon): one vowel changes the meaning -> must be exact
            Strictness.STRICT -> if (maxOf(a.length, b.length) <= 3) false else (sd == 0 && sim >= 0.6) || sim >= 0.86
            Strictness.MEDIUM -> if (maxOf(a.length, b.length) <= 3) sd == 0 && sim >= 0.66 else (sd <= 1 && sim >= 0.5) || sim >= 0.75
            Strictness.EASY -> (sd <= 2 && sim >= 0.4) || sim >= 0.65
        }
    }

    companion object {
        fun levenshtein(a: String, b: String): Int {
            val dp = IntArray(b.length + 1) { it }
            for (i in 1..a.length) {
                var prev = dp[0]; dp[0] = i
                for (j in 1..b.length) {
                    val tmp = dp[j]
                    dp[j] = minOf(dp[j] + 1, dp[j - 1] + 1, prev + if (a[i - 1] == b[j - 1]) 0 else 1)
                    prev = tmp
                }
            }
            return dp[b.length]
        }

        fun similarity(a: String, b: String): Double {
            val m = maxOf(a.length, b.length)
            return if (m == 0) 1.0 else 1.0 - levenshtein(a, b).toDouble() / m
        }
    }
}
