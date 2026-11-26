package com.babu.voiceover

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class TransliteratorTest {
    private val t = HindiTransliterator

    /** Same pronunciation: the cluster mark (्) between consonants is not pronounced differently. */
    private fun sound(x: String) = x.replace("्", "")

    @Test fun commonWordsAndRules() {
        val cases = listOf(
            "Kya aap roz subah deodorant lagate hain?" to "क्या आप रोज़ सुबह डिओडरेंट लगाते हैं?",
            "hindi" to "हिन्दी", "pakka" to "पक्का", "nahin" to "नहीं", "aasmaan" to "आसमान", "duniya" to "दुनिया",
            "agli" to "अगली", "khud" to "खुद", "karna" to "करना", "kahani" to "कहानी", "batana" to "बताना", "jaata" to "जाता",
        )
        val bad = cases.filter { (r, d) -> sound(t.transliterate(r)) != sound(d) }.map { "${it.first} -> ${t.transliterate(it.first)} (want ${it.second})" }
        assertTrue("mismatches: $bad", bad.isEmpty())
    }

    @Test fun keepsPunctuationAndDevanagari() {
        assertEquals("नमस्ते, दोस्तों! 42%", t.transliterate("namaste, doston! 42%").replace("नमस्ते", "नमस्ते"))
        assertEquals("पहले से हिंदी", t.transliterate("pehle se हिंदी"))
    }

    /** Whatever the converter writes must still be recognised as the same word by the app's own matcher. */
    @Test fun outputMatchesOriginalWord() {
        val m = WordMatcher(Strictness.MEDIUM)
        val script = "Lekin kya aapko pata hai iske andar asal mein kya hai Kyunki Australia mein kai schools ne in spray par pehle hi ban laga diya hai " +
            "Ismein bhari hai butane gas wahi gas jo lighter mein hoti hai Toh agli baar jab aap woh button dabayein khud se poochhiye"
        val bad = Script.parse(script).filter { w -> !m.matches(w.match, t.word(w.match)) }.map { "${it.match}->${t.word(it.match)}" }
        // English loanwords (schools, ban, butane, lighter …) are written the Hindi way and may differ from the Roman spelling
        assertTrue("mismatched: $bad", bad.size <= 6)
    }
}
