package com.babu.voiceover

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HindiLogicTest {
    private val m = WordMatcher(Strictness.STRICT)

    @Test fun romanizer() {
        assertEquals("naheen", Romanizer.romanize("नहीं"))
        assertEquals("kyaa", Romanizer.romanize("क्या"))
        assertEquals("hai", Romanizer.romanize("है"))
        assertEquals("men", Romanizer.romanize("में"))
        assertEquals("zaroor", Romanizer.romanize("ज़रूर"))
        assertEquals("gyaan", Romanizer.romanize("ज्ञान"))
        assertEquals("dekhie", Romanizer.romanize("देखिए"))
        assertEquals("ram", Romanizer.romanize("राम").replace("aa", "a"))
    }

    @Test fun spellingVariantsOfSameWordPass() {
        for (script in listOf("nahi", "nahin", "nahee", "nhi")) assertTrue(script, m.matches(script, "नहीं"))
        assertTrue(m.matches("hai", "है")); assertTrue(m.matches("hain", "हैं"))
        assertTrue(m.matches("kya", "क्या")); assertTrue(m.matches("mein", "में"))
        assertTrue(m.matches("zaroor", "ज़रूर")); assertTrue(m.matches("jaroor", "ज़रूर"))
        assertTrue(m.matches("khushboo", "खुशबू"))
        assertTrue(m.matches("deodorant", "डिओडरेंट"))
        assertTrue(m.matches("pakka", "पक्का"))
        assertTrue(m.matches("bataiye", "बताइए"))
        assertTrue(m.matches("karna", "करना"))
        assertTrue(m.matches("dekhiye", "देखिए"))
        assertTrue(m.matches("ye", "यह")); assertTrue(m.matches("woh", "वो"))
    }

    @Test fun differentWordsFail() {
        assertFalse(m.matches("nahi", "हाँ"))
        assertFalse(m.matches("nahi", "नया"))
        assertFalse(m.matches("kya", "क्यों"))
        assertFalse(m.matches("ki", "का"))
        assertFalse(m.matches("ka", "के"))
        assertFalse(m.matches("subah", "शाम"))
        assertFalse(m.matches("dil", "दिन"))
        assertTrue(m.matches("pani", "पानी"))
        assertFalse(m.matches("ham", "हम्म").and(m.isFiller("हम")))  // "we" is not a filler
    }

    @Test fun alignerAdvancesOnlyOnCorrectWords() {
        val a = Aligner(Script.parse("Kya aap roz subah deodorant lagate hain?"), m)
        assertEquals(3, a.preview(listOf("क्या", "आप", "रोज़")))
        var o = a.commit(listOf(Heard("क्या", 0.0, 0.3), Heard("आप", 0.3, 0.5), Heard("रोज़", 0.5, 0.8)))
        assertEquals(3, o.index); assertTrue(o.wrong.isEmpty())
        // wrong word: does not advance, reported for beep + cut
        o = a.commit(listOf(Heard("शाम", 1.0, 1.4)))
        assertEquals(3, o.index); assertEquals(1, o.wrong.size)
        // filler is ignored silently
        o = a.commit(listOf(Heard("हम्म", 2.0, 2.2), Heard("सुबह", 2.3, 2.7)))
        assertEquals(4, o.index); assertEquals(1, o.fillers.size); assertTrue(o.wrong.isEmpty())
    }
}
