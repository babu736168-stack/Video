package com.babu.voiceover

/**
 * Converts Devanagari (what the Hindi speech model outputs) into simple Roman Hindi
 * (how people type Hindi in English letters), e.g. "नहीं" -> "nahin", "क्या" -> "kyaa".
 * The result is only used for comparison, so it favours common spellings over strict transliteration.
 */
object Romanizer {
    private val consonants = mapOf(
        'क' to "k", 'ख' to "kh", 'ग' to "g", 'घ' to "gh", 'ङ' to "n",
        'च' to "ch", 'छ' to "chh", 'ज' to "j", 'झ' to "jh", 'ञ' to "n",
        'ट' to "t", 'ठ' to "th", 'ड' to "d", 'ढ' to "dh", 'ण' to "n",
        'त' to "t", 'थ' to "th", 'द' to "d", 'ध' to "dh", 'न' to "n",
        'प' to "p", 'फ' to "ph", 'ब' to "b", 'भ' to "bh", 'म' to "m",
        'य' to "y", 'र' to "r", 'ल' to "l", 'व' to "v", 'श' to "sh",
        'ष' to "sh", 'स' to "s", 'ह' to "h", 'ळ' to "l",
        // precomposed nukta letters
        'क़' to "q", 'ख़' to "kh", 'ग़' to "g", 'ज़' to "z", 'ड़' to "r", 'ढ़' to "rh", 'फ़' to "f", 'य़' to "y",
    )
    private val nuktaForms = mapOf('क' to "q", 'ख' to "kh", 'ग' to "g", 'ज' to "z", 'ड' to "r", 'ढ' to "rh", 'फ' to "f", 'य' to "y")
    private val vowels = mapOf(
        'अ' to "a", 'आ' to "aa", 'इ' to "i", 'ई' to "ee", 'उ' to "u", 'ऊ' to "oo", 'ऋ' to "ri",
        'ए' to "e", 'ऐ' to "ai", 'ओ' to "o", 'औ' to "au", 'ऑ' to "o", 'ऍ' to "e",
    )
    private val matras = mapOf(
        'ा' to "aa", 'ि' to "i", 'ी' to "ee", 'ु' to "u", 'ू' to "oo", 'ृ' to "ri",
        'े' to "e", 'ै' to "ai", 'ो' to "o", 'ौ' to "au", 'ॉ' to "o", 'ॅ' to "e",
    )
    private const val HALANT = '्'
    private const val NUKTA = '़'
    private val nasals = setOf('ं', 'ँ')
    private const val VISARGA = 'ः'
    private val digits = "०१२३४५६७८९"

    fun romanize(word: String): String {
        val s = word.trim()
        val out = StringBuilder()
        var i = 0
        while (i < s.length) {
            val c = s[i]
            when {
                c in consonants -> {
                    var rom = consonants.getValue(c)
                    var j = i + 1
                    if (j < s.length && s[j] == NUKTA) { rom = nuktaForms[c] ?: rom; j++ }
                    // ज्ञ is said "gy"
                    if (c == 'ज' && j + 1 < s.length && s[j] == HALANT && s[j + 1] == 'ञ') { out.append("gy"); i = j + 2; continue }
                    out.append(rom)
                    if (j < s.length && s[j] in matras) { out.append(matras.getValue(s[j])); j++ }
                    else if (j < s.length && s[j] == HALANT) { j++ }
                    else out.append('a') // inherent vowel (schwa); dropped later where it is usually silent
                    i = j
                }
                c in vowels -> { out.append(vowels.getValue(c)); i++ }
                c in matras -> { out.append(matras.getValue(c)); i++ }
                c in nasals -> { out.append('n'); i++ }
                c == VISARGA -> { out.append('h'); i++ }
                c in digits -> { out.append(digits.indexOf(c)); i++ }
                c.isLetterOrDigit() && c.code < 128 -> { out.append(c.lowercaseChar()); i++ }
                else -> i++
            }
        }
        // Final schwa is silent in Hindi: "राम" -> "ram", not "rama"
        var r = out.toString()
        if (r.length > 2 && r.endsWith("a") && !r.endsWith("aa") && r[r.length - 2] !in "aeiou") r = r.dropLast(1)
        return r
    }

    fun isDevanagari(s: String) = s.any { it in 'ऀ'..'ॿ' }
}
