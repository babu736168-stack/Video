package com.babu.voiceover

/**
 * Offline, free Roman Hindi -> Devanagari ("kya aap roz subah" -> "क्या आप रोज़ सुबह").
 * Common words come from a dictionary (exact spelling); everything else uses phonetic rules.
 * The result is shown to the user so any word can be corrected before it is spoken.
 */
object HindiTransliterator {

    private val dict: Map<String, String> = mapOf(
        "hai" to "है", "hain" to "हैं", "he" to "है", "ho" to "हो", "hoon" to "हूँ", "hu" to "हूँ", "hun" to "हूँ",
        "tha" to "था", "thi" to "थी", "the" to "थे", "nahi" to "नहीं", "nahin" to "नहीं", "nahee" to "नहीं", "nhi" to "नहीं",
        "mein" to "में", "me" to "में", "main" to "मैं", "mai" to "मैं", "hum" to "हम", "ham" to "हम", "tum" to "तुम",
        "aap" to "आप", "ap" to "आप", "ye" to "ये", "yeh" to "ये", "yah" to "यह", "wo" to "वो", "woh" to "वो", "vo" to "वो",
        "kya" to "क्या", "kyun" to "क्यों", "kyon" to "क्यों", "kyunki" to "क्योंकि", "kyonki" to "क्योंकि",
        "ka" to "का", "ki" to "की", "ke" to "के", "ko" to "को", "se" to "से", "par" to "पर", "pe" to "पे",
        "aur" to "और", "or" to "और", "ya" to "या", "bhi" to "भी", "hi" to "ही", "to" to "तो", "toh" to "तो",
        "ek" to "एक", "do" to "दो", "teen" to "तीन", "char" to "चार", "paanch" to "पांच", "das" to "दस", "sau" to "सौ",
        "hazaar" to "हज़ार", "hazar" to "हज़ार", "lakh" to "लाख", "crore" to "करोड़", "karod" to "करोड़",
        "yahan" to "यहाँ", "yaha" to "यहाँ", "wahan" to "वहाँ", "vahan" to "वहाँ", "kahan" to "कहाँ", "kaha" to "कहा",
        "jab" to "जब", "tab" to "तब", "ab" to "अब", "abhi" to "अभी", "sab" to "सब", "sabhi" to "सभी", "kuch" to "कुछ",
        "kaise" to "कैसे", "aise" to "ऐसे", "waise" to "वैसे", "jaise" to "जैसे", "kitna" to "कितना", "kaun" to "कौन",
        "lekin" to "लेकिन", "magar" to "मगर", "agar" to "अगर", "phir" to "फिर", "fir" to "फिर", "sirf" to "सिर्फ़",
        "bahut" to "बहुत", "bohot" to "बहुत", "zaroor" to "ज़रूर", "jaroor" to "ज़रूर", "sach" to "सच", "log" to "लोग",
        "duniya" to "दुनिया", "desh" to "देश", "bharat" to "भारत", "din" to "दिन", "raat" to "रात", "subah" to "सुबह",
        "shaam" to "शाम", "saal" to "साल", "paani" to "पानी", "pani" to "पानी", "dil" to "दिल", "baat" to "बात",
        "bataiye" to "बताइए", "dekhiye" to "देखिए", "suniye" to "सुनिए", "kijiye" to "कीजिए", "boliye" to "बोलिए",
        "chahiye" to "चाहिए", "liye" to "लिए", "diya" to "दिया", "kiya" to "किया", "gaya" to "गया", "gayi" to "गई",
        "gaye" to "गए", "raha" to "रहा", "rahi" to "रही", "rahe" to "रहे", "wala" to "वाला", "wali" to "वाली",
        "wale" to "वाले", "andar" to "अंदर", "bahar" to "बाहर", "upar" to "ऊपर", "neeche" to "नीचे", "saath" to "साथ",
        "baad" to "बाद", "pehle" to "पहले", "pahle" to "पहले", "kabhi" to "कभी", "hamesha" to "हमेशा", "aaj" to "आज",
        "kal" to "कल", "sabse" to "सबसे", "bada" to "बड़ा", "badi" to "बड़ी", "bade" to "बड़े", "chhota" to "छोटा",
        "pata" to "पता", "naya" to "नया", "nayi" to "नई", "naye" to "नए", "sath" to "साथ", "rata" to "रटा", "matlab" to "मतलब", "zindagi" to "ज़िंदगी", "khushboo" to "ख़ुशबू", "scientist" to "साइंटिस्ट",
        "deodorant" to "डिओडरेंट", "spray" to "स्प्रे", "company" to "कंपनी", "comment" to "कमेंट", "video" to "वीडियो",
"kai" to "कई", "in" to "इन", "un" to "उन", "is" to "इस", "us" to "उस", "inka" to "इनका", "unka" to "उनका",
        "ismein" to "इसमें", "usmein" to "उसमें", "inmein" to "इनमें", "jismein" to "जिसमें", "unhone" to "उन्होंने",
        "dar" to "डर", "darr" to "डर", "darawni" to "डरावनी", "darawna" to "डरावना", "dhadkan" to "धड़कन", "ladki" to "लड़की",
        "ladka" to "लड़का", "padh" to "पढ़", "padhai" to "पढ़ाई", "jagah" to "जगह", "thoda" to "थोड़ा", "thodi" to "थोड़ी",
        "chhod" to "छोड़", "jod" to "जोड़", "tod" to "तोड़", "ped" to "पेड़", "ghoda" to "घोड़ा", "sadak" to "सड़क",
        "kapde" to "कपड़े", "pakad" to "पकड़", "bhed" to "भेड़", "dabba" to "डब्बा", "daba" to "दबा", "dabayein" to "दबाएं",
        "aayein" to "आएं", "jaayein" to "जाएं", "karein" to "करें", "dekhein" to "देखें", "sochiye" to "सोचिए",
        "poochhiye" to "पूछिए", "puchiye" to "पूछिए", "laayak" to "लायक", "layak" to "लायक", "khatarnak" to "ख़तरनाक",
        "khatra" to "ख़तरा", "khabar" to "ख़बर", "zehar" to "ज़हर", "jahar" to "ज़हर", "sehat" to "सेहत", "bimari" to "बीमारी",
        "dimag" to "दिमाग़", "dimaag" to "दिमाग़", "naak" to "नाक", "aankh" to "आँख", "aankhon" to "आँखों", "saans" to "साँस",
        "mautein" to "मौतें", "maut" to "मौत", "rahasya" to "रहस्य", "dhamaka" to "धमाका", "taakat" to "ताक़त",
        // common English words in Hindi videos
        "australia" to "ऑस्ट्रेलिया", "india" to "इंडिया", "america" to "अमेरिका", "uk" to "यूके", "usa" to "यूएसए",
        "gas" to "गैस", "lighter" to "लाइटर", "button" to "बटन", "butane" to "ब्यूटेन", "ban" to "बैन", "banned" to "बैन",
        "chemical" to "केमिकल", "chemicals" to "केमिकल्स", "cancer" to "कैंसर", "study" to "स्टडी", "studies" to "स्टडीज़",
        "report" to "रिपोर्ट", "doctor" to "डॉक्टर", "hospital" to "हॉस्पिटल", "science" to "साइंस", "research" to "रिसर्च",
        "fragrance" to "फ्रेगरेंस", "perfume" to "परफ्यूम", "brand" to "ब्रांड", "product" to "प्रोडक्ट", "products" to "प्रोडक्ट्स",
        "market" to "मार्केट", "online" to "ऑनलाइन", "phone" to "फ़ोन", "mobile" to "मोबाइल", "internet" to "इंटरनेट",
        "youtube" to "यूट्यूब", "channel" to "चैनल", "subscribe" to "सब्सक्राइब", "like" to "लाइक", "share" to "शेयर",
        "comments" to "कमेंट्स", "roll" to "रोल", "on" to "ऑन", "switch" to "स्विच", "trade" to "ट्रेड", "secret" to "सीक्रेट",
        "benzene" to "बेंज़ीन", "procter" to "प्रॉक्टर", "gamble" to "गैंबल", "recall" to "रिकॉल", "denmark" to "डेनमार्क",
        "percent" to "प्रतिशत", "minute" to "मिनट", "second" to "सेकंड", "number" to "नंबर", "photo" to "फ़ोटो",
        "computer" to "कंप्यूटर", "car" to "कार", "bus" to "बस", "train" to "ट्रेन", "office" to "ऑफ़िस", "money" to "मनी",
        "lab" to "लैब", "tube" to "ट्यूब", "can" to "कैन", "level" to "लेवल", "zero" to "ज़ीरो", "asthma" to "अस्थमा",
        "allergy" to "एलर्जी", "allergies" to "एलर्जी", "plastic" to "प्लास्टिक", "water" to "वॉटर", "time" to "टाइम",
                "school" to "स्कूल", "schools" to "स्कूलों", "test" to "टेस्ट", "lab" to "लैब", "label" to "लेबल",
    )

    private val consonants = listOf(
        "chh" to "छ", "ksh" to "क्ष", "kh" to "ख", "gh" to "घ", "ch" to "च", "jh" to "झ", "th" to "थ", "dh" to "ध",
        "ph" to "फ", "bh" to "भ", "sh" to "श", "gy" to "ज्ञ", "k" to "क", "g" to "ग", "c" to "क", "j" to "ज",
        "t" to "त", "d" to "द", "n" to "न", "p" to "प", "f" to "फ़", "b" to "ब", "m" to "म", "y" to "य", "r" to "र",
        "l" to "ल", "v" to "व", "w" to "व", "s" to "स", "h" to "ह", "z" to "ज़", "q" to "क़", "x" to "क्स",
    )
    // roman vowel -> (independent letter, matra)
    private val vowels = listOf(
        "aa" to ("आ" to "ा"), "ai" to ("ऐ" to "ै"), "au" to ("औ" to "ौ"), "ee" to ("ई" to "ी"), "ii" to ("ई" to "ी"), "ei" to ("ए" to "े"),
        "oo" to ("ऊ" to "ू"), "uu" to ("ऊ" to "ू"), "a" to ("अ" to ""), "i" to ("इ" to "ि"), "u" to ("उ" to "ु"),
        "e" to ("ए" to "े"), "o" to ("ओ" to "ो"),
    )
    private const val HALANT = "्"

    fun transliterate(text: String): String =
        Regex("[A-Za-z]+").replace(text) { m -> word(m.value) }

    fun word(w0: String): String {
        var w = w0.lowercase()
        dict[w]?.let { return it }
        // Roman writers often type the long "aa" of verb/noun endings as a single "a":
        // lagate -> लगाते, batana -> बताना, kahani -> कहानी, jata -> जाता
        if (w.length >= 4) w = w.replace(Regex("(?<=[^aeiou])a(?=[tn][aei]$)"), "aa")
        if (w.length >= 4) w = w.replace(Regex("(?<=[^aeiou])a(?=y(?:e|ein|en|i)$)"), "aa")   // dabayein -> dabaayein
        // a word-final "i" is almost always long in Hindi: hindi -> हिन्दी, abhi -> अभी, kahani -> कहानी
        if (w.length >= 3 && w.endsWith("i") && w[w.length - 2] !in "aeiou") w = w.dropLast(1) + "ee"
        // a word-final "a" is long too (a short final "a" is silent in Hindi, so nobody writes it): pakka -> पक्का
        if (w.length >= 2 && w.endsWith("a") && !w.endsWith("aa") && w[w.length - 2] !in "aeiou") w += "a"
        val out = StringBuilder()
        var i = 0
        var prevConsonant = false
        while (i < w.length) {
            // nasal "n" at the end of a word after a vowel other than a/aa -> anusvara (nahin -> नहीं)
            if (w[i] == 'n' && i == w.length - 1 && i >= 2 && (w[i - 1] in "eo" || w.substring(i - 2, i) in setOf("ee", "ai", "ei", "oo", "au"))) {
                out.append("ं"); i++; prevConsonant = false; continue
            }
            val c = consonants.firstOrNull { w.startsWith(it.first, i) }
            if (c != null) {
                if (prevConsonant) out.append(HALANT)          // consonant cluster: hindi -> हिन्दी, pakka -> पक्का
                out.append(c.second); i += c.first.length; prevConsonant = true
                continue
            }
            val v = vowels.firstOrNull { w.startsWith(it.first, i) }
            if (v != null) {
                out.append(if (prevConsonant) v.second.second else v.second.first)
                i += v.first.length; prevConsonant = false
                continue
            }
            out.append(w[i]); i++; prevConsonant = false
        }
        return out.toString()
    }
}
