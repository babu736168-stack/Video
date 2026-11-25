package com.babu.voiceover

/** One word of the script: what is shown, and what is compared. */
data class ScriptWord(val display: String, val match: String)

object Script {
    fun parse(text: String): List<ScriptWord> =
        text.split(Regex("\\s+")).filter { it.isNotBlank() }.mapNotNull { tok ->
            val m = tok.lowercase().filter { it in 'a'..'z' || it.isDigit() }
            if (m.isEmpty()) null else ScriptWord(tok, m)
        }

    fun hasDigits(words: List<ScriptWord>) = words.any { w -> w.match.any { it.isDigit() } }
}

/** A word the recognizer heard, with its time (seconds since recording start). */
data class Heard(val word: String, val start: Double, val end: Double)

data class FinalOutcome(
    val index: Int,               // next word to say
    val correct: List<Pair<Int, Heard>>,
    val wrong: List<Heard>,       // mispronounced / extra words -> beep + cut
    val fillers: List<Heard>,     // "hmm", "umm" -> silently cut
)

/**
 * Walks through the script word by word. A word only counts once it is pronounced correctly;
 * anything else (wrong word, repeated word, skipped word) does not advance.
 */
class Aligner(val words: List<ScriptWord>, val matcher: WordMatcher) {
    var index = 0
        private set
    val done get() = index >= words.size

    /** Live preview while speaking: how far the current (unfinished) phrase has matched. */
    fun preview(partial: List<String>): Int {
        var i = index
        for (w in partial) {
            if (i >= words.size) break
            if (matcher.matches(words[i].match, w)) i++ else if (!matcher.isFiller(w)) break
        }
        return i
    }

    /** Commit a finished phrase. */
    fun commit(heard: List<Heard>): FinalOutcome {
        val correct = mutableListOf<Pair<Int, Heard>>()
        val wrong = mutableListOf<Heard>()
        val fillers = mutableListOf<Heard>()
        for (h in heard) {
            if (h.word.isBlank() || h.word == "[unk]") continue
            if (index < words.size && matcher.matches(words[index].match, h.word)) {
                correct += index to h; index++
            } else if (matcher.isFiller(h.word)) {
                fillers += h
            } else {
                wrong += h
            }
        }
        return FinalOutcome(index, correct, wrong, fillers)
    }

    fun skip() { if (index < words.size) index++ }
    fun back() { if (index > 0) index-- }
}
