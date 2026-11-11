"""Econ15 - Ramesh Singh Ch 3: Growth, Development and Happiness (deep dive). Course plan: RS 18e Ch 3, class 15.
Last class of Part 1 (Neev).
DRAFT FROM STANDARD FACTS: written without the book in hand; check against Ramesh Singh 18e Ch 3 (send pages to
match exactly). No current rankings or index values are used until checked against the latest reports.
Facts used (standard): growth = rise in output/income (quantitative, e.g. GDP growth rate); development = growth plus
better lives (qualitative: health, education, choices). UNDP's first Human Development Report came out in 1990, led
by Mahbub ul Haq with Amartya Sen; HDI has three dimensions: a long and healthy life (life expectancy at birth),
knowledge (mean years and expected years of schooling) and a decent standard of living (GNI per capita at PPP).
Bhutan's Gross National Happiness idea is credited to its fourth king, Jigme Singye Wangchuck, in the 1970s. The World
Happiness Report has been published since 2012 (UN Sustainable Development Solutions Network and partners).
Sustainable development (Brundtland Commission report "Our Common Future", 1987): development that meets the needs of
the present without compromising the ability of future generations to meet their own needs. The UN adopted 17
Sustainable Development Goals in 2015, to be met by 2030. Inclusive growth = growth whose benefits reach all.
"""
CHAPTER = dict(num=15, title="Growth, Development, Happiness", kicker="ECONOMICS · CLASS 15 · RAMESH SINGH CH 3",
               rain="😊", outro_icons=("🕊️", "🇮🇳"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next: Part 2 — Bharat ka Safar begins (1947)")

TOPICS = [
    dict(id="gvd", name="Growth vs Development", label="Bigger or better?", icon="📈"),
    dict(id="hdi", name="HDI", label="Health · Knowledge · Living standard", icon="🌍"),
    dict(id="happy", name="Happiness", label="Can we measure joy?", icon="😊"),
    dict(id="sustain", name="Sustainable Development", label="For today and tomorrow", icon="♻️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक बच्चा हर साल {लंबा|Lamba|📏} होता जा रहा है। लेकिन न पढ़ाई, न सेहत, न ख़ुशी।"),
    (None, "[punch] क्या वो सच में, {बढ़ रहा|Growth?|🤔} है?"),
    (None, "देश के साथ भी, यही सवाल है!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {ग्रोथ और डेवलपमेंट|Growth vs Development|📈} का फ़र्क़।"),
    (None, "दूसरा — {एच डी आई|HDI|🌍}, यानी विकास का अंतरराष्ट्रीय पैमाना।"),
    (None, "तीसरा — क्या {ख़ुशी|Happiness|😊} भी नापी जा सकती है?"),
    (None, "और चौथा — {टिकाऊ विकास|Sustainable Development|♻️}, और दुनिया के सत्रह लक्ष्य।"),

    ("center", "[name] रमेश सिंह, चैप्टर तीन — ग्रोथ, डेवलपमेंट और हैप्पीनेस!"),
    ("topics", "चलिए — उस लंबे होते बच्चे से शुरू करते हैं!"),

    ("focus:gvd", "[scene] {ग्रोथ|Growth|📈} — यानी उत्पादन और कमाई का बढ़ना। जैसे — जीडीपी की ग्रोथ रेट। ये {मात्रा|Quantitative|🔢} की बात है।"),
    (None, "[name] {डेवलपमेंट|Development|🌱} — ग्रोथ के साथ-साथ, ज़िंदगी का बेहतर होना। सेहत, शिक्षा, आज़ादी, चुनने के मौक़े। ये {गुणवत्ता|Qualitative|✨} की बात है।"),
    (None, "[punch] यानी — ग्रोथ के बिना, डेवलपमेंट मुश्किल। लेकिन सिर्फ़ ग्रोथ से, डेवलपमेंट {पक्का नहीं|Growth ≠ Development|⚠️}!"),
    ("ex:", "और जब बढ़त का फ़ायदा, सब तक पहुँचे — उसे कहते हैं — {इनक्लूसिव ग्रोथ|Inclusive Growth|🤝}।"),

    ("focus:hdi", "[scene] {उन्नीस सौ नब्बे|1990|📅}। {यू एन डी पी|UNDP|🌐} की पहली {ह्यूमन डेवलपमेंट रिपोर्ट|Human Development Report|📘}।"),
    (None, "इसके पीछे थे — पाकिस्तान के अर्थशास्त्री {महबूब उल हक़|Mahbub ul Haq|👨‍🏫}, और भारत के {अमर्त्य सेन|Amartya Sen|🎓}।"),
    (None, "[name] और उन्होंने बनाया — {एच डी आई|Human Development Index|🌍}। तीन हिस्से।"),
    (None, "पहला — {लंबी और सेहतमंद ज़िंदगी|Long & healthy life|❤️}। यानी — जन्म के समय, औसत उम्र की उम्मीद।"),
    (None, "दूसरा — {ज्ञान|Knowledge|📚}। यानी स्कूल में बिताए, औसत साल — और उम्मीद के साल।"),
    (None, "तीसरा — {अच्छा जीवन स्तर|Decent living standard|🏠}। यानी — पी पी पी पर, हर व्यक्ति की जी एन आई।"),

    ("focus:happy", "[scene] अब सबसे मज़ेदार सवाल — क्या ख़ुशी भी नापी जा सकती है?"),
    (None, "हिमालय का छोटा-सा देश — {भूटान|Bhutan|🏔️}। उसके चौथे राजा, {जिग्मे सिंग्ये वांगचुक|Jigme Singye Wangchuck|👑} ने, सत्तर के दशक में कहा —"),
    (None, "[punch] {ग्रॉस नेशनल हैप्पीनेस|Gross National Happiness|😊} — ग्रॉस नेशनल प्रोडक्ट से ज़्यादा ज़रूरी है!"),
    (None, "और {दो हज़ार बारह|2012|📅} से, दुनिया भर के देशों की ख़ुशी पर — हर साल आती है — {वर्ल्ड हैप्पीनेस रिपोर्ट|World Happiness Report|🌍}।"),

    ("focus:sustain", "[scene] और आख़िरी बात — ऐसा विकास, जो कल को भी बचाए।"),
    (None, "{उन्नीस सौ सत्तासी|1987|📅}। {ब्रंटलैंड कमीशन|Brundtland Commission|📘} की रिपोर्ट — {आवर कॉमन फ़्यूचर|Our Common Future|🌍}।"),
    (None, "[name] उसकी परिभाषा — {सस्टेनेबल डेवलपमेंट|Sustainable Development|♻️} वो है, जो आज की ज़रूरतें पूरी करे — लेकिन आने वाली पीढ़ियों की, ज़रूरतें पूरी करने की ताक़त, न छीने।"),
    (None, "[punch] और {दो हज़ार पंद्रह|2015|📅} में, यू एन ने तय किए — {सत्रह सस्टेनेबल डेवलपमेंट गोल्स|17 SDGs|🎯} — जिन्हें {दो हज़ार तीस|2030|🏁} तक पूरा करना है।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{ग्रोथ बनाम डेवलपमेंट|Growth vs Development|📈} — मात्रा बनाम गुणवत्ता।"),
    (None, "{एच डी आई|HDI, 1990|🌍} — सेहत, ज्ञान, और जीवन स्तर।"),
    (None, "{ग्रॉस नेशनल हैप्पीनेस|GNH, Bhutan|😊}, और {वर्ल्ड हैप्पीनेस रिपोर्ट|Since 2012|🌍}।"),
    (None, "{टिकाऊ विकास|Brundtland 1987|♻️}, और {सत्रह एस डी जी|17 SDGs by 2030|🎯}।"),

    ("outro:Next: Part 2 — Bharat ka Safar", "[scene] और दोस्तों — इसी के साथ, हमारा पहला हिस्सा — {नींव|Neev complete|🧱} — पूरा हुआ!"),
    (None, "[punch] अब शुरू होता है दूसरा हिस्सा — भारत का सफ़र। उन्नीस सौ सैंतालीस — आज़ादी के वक़्त, भारत की इकॉनमी कैसी थी? अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
