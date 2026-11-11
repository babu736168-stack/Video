"""Econ02 - Har Cheez Kam Kyon Padti Hai? (Scarcity, Central Problems, PPC, Opportunity Cost).
Course plan: Ramesh Singh Ch 1 (Introduction to Economics), NCERT foundation class 2.
Source: NCERT Class 12 Introductory Microeconomics, Chapter 1 "Introduction".
Facts used: a society needs food, clothing, shelter, transport, health care, education; resources (land, labour,
tools, machines ...) are scarce: if all wants were produced, resources would fall short, so society must allocate
them (choice). Central problems: what to produce and in what quantities; how to produce (which technique, e.g. more
labour or more machines); for whom to produce (who gets how much; should everyone get a minimum, e.g. basic
education and health). Production possibility frontier: the combinations of two goods (corn and cotton) that can be
produced with the given resources and technology; NCERT table: A 0 corn 10 cotton, B 1 9, C 2 7, D 3 4, E 4 0.
Opportunity cost: the amount of the other good given up (in general, the gain foregone from the second-best
choice); from the table it rises 1, 2, 3, 4 cotton per extra unit of corn. Inside the frontier: resources
underutilised or wasted; outside: not attainable with the given resources. Organisation: centrally planned economy
(government / central authority takes the important decisions), market economy (free interaction of buyers and
sellers, prices act as signals), in reality all economies are mixed (government + market; differs in extent).
Positive economics: how things work; normative: whether they are desirable. Microeconomics: individual agents and
markets; macroeconomics: the economy as a whole (total output, employment, aggregate price level).
"""
CHAPTER = dict(num=2, title="Har Cheez Kam Kyon?", kicker="ECONOMICS · CLASS 2 · NCERT CLASS 12 MICRO", rain="⏳",
               outro_icons=("🌾", "🏭"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Teen Sectors — Kheti, Kaarkhana, Seva")

TOPICS = [
    dict(id="scarcity", name="Scarcity", label="Wants are many, means are few", icon="⏳"),
    dict(id="problems", name="3 Central Problems", label="What · How · For whom", icon="❓"),
    dict(id="ppc", name="PPC & Opportunity Cost", label="What you give up", icon="📈"),
    dict(id="systems", name="Who Decides?", label="Plan, market or mixed", icon="🏛️"),
    dict(id="branches", name="Two Pairs of Glasses", label="Positive · Normative · Micro · Macro", icon="👓"),
]

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सोचिए — आपकी जेब में {सौ रुपये|₹100|💵} हैं।"),
    (None, "और सामने हैं — एक {पिज़्ज़ा|Pizza|🍕}, एक {मूवी टिकट|Movie|🎬}, और एक नई {किताब|Kitaab|📖}।"),
    (None, "तीनों चाहिए — लेकिन पैसा? सिर्फ़ एक के लायक़!"),
    (None, "[punch] तो क्या करेंगे? {चुनना पड़ेगा|Choice!|🤔}"),
    (None, "और यही मुश्किल — सिर्फ़ आपकी नहीं। पूरे देश की है!"),

    # ---------------------------------------------------------------- today's class
    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {स्कार्सिटी|Scarcity|⏳}। यानी — हर चीज़ कम क्यों पड़ती है।"),
    (None, "दूसरा — हर देश के सामने, {तीन बड़े सवाल|3 Central Problems|❓}।"),
    (None, "तीसरा — {पी पी सी|PPC & Opportunity Cost|📈}। यानी — एक चीज़ पाने के लिए, क्या छोड़ना पड़ता है।"),
    (None, "और चौथा — ये फ़ैसले लेता कौन है, और इकॉनॉमिक्स को देखने के {दो चश्मे|Do Chashme|👓}।"),

    ("center", "[name] क्लास दो — हर चीज़ कम क्यों पड़ती है?"),
    ("topics", "चलिए — शुरू करते हैं, एक पूरे समाज की ज़रूरतों से!"),

    # ---------------------------------------------------------------- 1. Scarcity
    ("focus:scarcity", "[scene] एक समाज को चाहिए — {खाना|Khaana|🍚}, {कपड़ा|Kapda|👕}, {मकान|Makaan|🏠}, {आना-जाना|Transport|🚌}, {इलाज|Ilaaj|🏥}, और {पढ़ाई|Padhai|🎓}।"),
    (None, "और ये सब बनाने के लिए चाहिए — {साधन|Resources|🧰}। ज़मीन, लोगों की मेहनत, मशीनें, औज़ार — वही, जो हमने पिछली क्लास में पढ़े।"),
    (None, "[punch] लेकिन मुश्किल ये है — साधन {सीमित|Limited|🔒} हैं। और ज़रूरतें? {अनगिनत|Unlimited|♾️}!"),
    (None, "[name] इसी को कहते हैं — {स्कार्सिटी|Scarcity|⏳}। यानी — जितना चाहिए, उतना है ही नहीं।"),
    (None, "अगर हर चीज़ उतनी बनाएँ, जितनी लोग चाहते हैं — तो साधन कम पड़ जाएँगे।"),
    (None, "इसलिए समाज को तय करना पड़ता है — कौन-सा साधन, किस काम में लगे। इसे कहते हैं — {एलोकेशन|Allocation|🧩}, यानी बँटवारा।"),
    ("ex:", "बिल्कुल आपकी जेब के {सौ रुपये|₹100|💵} जैसा — पिज़्ज़ा लिया, तो मूवी गई!"),
    (None, "[punch] और यहीं से जन्म होता है — तीन बड़े सवालों का!"),

    # ---------------------------------------------------------------- 2. Central problems
    ("focus:problems", "[scene] हर देश — अमीर हो या गरीब — इन तीन सवालों का जवाब ढूँढता है।"),
    (None, "पहला — {क्या बनाएँ|What to produce?|🍞}, और कितना? ज़्यादा अनाज, या ज़्यादा कपड़ा? ज़्यादा स्कूल, या ज़्यादा सड़कें?"),
    (None, "दूसरा — {कैसे बनाएँ|How to produce?|⚙️}? ज़्यादा लोग लगाकर, या ज़्यादा मशीनें लगाकर?"),
    (None, "तीसरा — {किसके लिए बनाएँ|For whom?|👨‍👩‍👧}? जो बना, वो किसको कितना मिलेगा? क्या सबको, कम से कम, ज़रूरत भर मिलेगा? क्या पढ़ाई और इलाज, सबको मुफ़्त मिलना चाहिए?"),
    (None, "[name] इन्हें कहते हैं — इकॉनमी की {तीन सेंट्रल प्रॉब्लम्स|3 Central Problems|❓}!"),

    # ---------------------------------------------------------------- 3. PPC and opportunity cost
    ("focus:ppc", "[scene] अब सोचिए — एक इकॉनमी, सिर्फ़ दो चीज़ें बनाती है — {मक्का|Corn|🌽}, और {कपास|Cotton|☁️}।"),
    ("anim:ppf", "अगर सारे साधन कपास में लगा दें — तो {मक्का ज़ीरो, और कपास दस|A: 0 Corn, 10 Cotton|📍}।"),
    (None, "थोड़े साधन मक्के में लगाएँ — तो {एक मक्का, नौ कपास|B: 1 Corn, 9 Cotton|📍}।"),
    (None, "फिर — {दो मक्का, सात कपास|C: 2 Corn, 7 Cotton|📍}। और फिर — {तीन मक्का, चार कपास|D: 3 Corn, 4 Cotton|📍}।"),
    (None, "और सारे साधन मक्के में — {चार मक्का, कपास ज़ीरो|E: 4 Corn, 0 Cotton|📍}।"),
    (None, "[name] इन बिंदुओं को जोड़ें — तो बनती है एक कर्व — {प्रोडक्शन पॉसिबिलिटी फ़्रंटियर|PPF / PPC|📈}। यानी — इन साधनों से, ज़्यादा से ज़्यादा, क्या-क्या बन सकता है।"),
    (None, "[scene] अब ध्यान दीजिए — {ए से बी|A → B|➡️} जाने में, एक मक्का मिला — और एक कपास छोड़ना पड़ा।"),
    (None, "{बी से सी|B → C|➡️} में — एक और मक्का के लिए, दो कपास छोड़ने पड़े। फिर तीन। फिर चार!"),
    (None, "[name] जो छोड़ना पड़ा — उसे कहते हैं — {ऑपर्च्युनिटी कॉस्ट|Opportunity Cost|⚖️}। यानी — दूसरे सबसे अच्छे विकल्प को, छोड़ने की क़ीमत।"),
    ("ex:", "जैसे — आपने पिज़्ज़ा चुना, तो आपकी ऑपर्च्युनिटी कॉस्ट है — {वो मूवी|Movie chhooti|🎬}, जो आप नहीं देख पाए।"),
    (None, "[scene] और अगर कोई बिंदु, कर्व के {अंदर|Andar: Barbaadi|⬇️} हो? मतलब — साधन पूरे इस्तेमाल नहीं हुए, या बर्बाद हुए।"),
    (None, "और कर्व के {बाहर|Bahar: Namumkin|🚫}? वो — इन साधनों से, अभी मुमकिन ही नहीं।"),

    # ---------------------------------------------------------------- 4. Who decides?
    ("focus:systems", "[scene] अब सवाल — ये तीन फ़ैसले, लेता कौन है?"),
    (None, "पहला तरीक़ा — {सेंट्रली प्लान्ड इकॉनमी|Centrally Planned|🏛️}। यहाँ सरकार, या कोई केंद्रीय अथॉरिटी — सारे ज़रूरी फ़ैसले लेती है। क्या बने, कैसे बने, किसे मिले।"),
    (None, "दूसरा — {मार्केट इकॉनमी|Market Economy|🏪}। यहाँ लोग, अपनी मर्ज़ी से ख़रीदते-बेचते हैं। और {दाम|Price = Signal|🏷️} ही, इशारे का काम करते हैं।"),
    ("ex:", "जैसे — किसी चीज़ के {दाम बढ़े|Daam badhe|📈}, तो बनाने वालों को इशारा मिला — इसे और बनाओ!"),
    (None, "[punch] और असल दुनिया में? सारी इकॉनमी — {मिक्स्ड इकॉनमी|Mixed Economy|🤝} हैं। कुछ ज़रूरी फ़ैसले सरकार लेती है, बाक़ी काम ज़्यादातर बाज़ार से। फ़र्क़ सिर्फ़ इतना — सरकार का रोल, कितना बड़ा है।"),
    (None, "हमारा {भारत|India|🇮🇳} भी — एक मिक्स्ड इकॉनमी है।"),

    # ---------------------------------------------------------------- 5. Two pairs of glasses
    ("focus:branches", "[scene] और आख़िर में — इकॉनॉमिक्स को देखने के, दो जोड़ी चश्मे।"),
    (None, "पहली जोड़ी — {पॉज़िटिव|Positive|🔍}, यानी — चीज़ें असल में, कैसे काम करती हैं। और {नॉर्मेटिव|Normative|⚖️}, यानी — क्या ऐसा होना चाहिए? क्या ये अच्छा है?"),
    ("ex:", "जैसे — दाम बढ़े, तो लोग कम ख़रीदते हैं — ये है {पॉज़िटिव बात|Positive|🔍}। और — गरीबों को सस्ता अनाज मिलना चाहिए — ये है {नॉर्मेटिव बात|Normative|⚖️}।"),
    (None, "दूसरी जोड़ी — {माइक्रोइकॉनॉमिक्स|Microeconomics|🔬}, यानी — एक ग्राहक, एक दुकानदार, एक बाज़ार।"),
    (None, "और {मैक्रोइकॉनॉमिक्स|Macroeconomics|🌏}, यानी — पूरा देश एक साथ। कुल उत्पादन, कुल रोज़गार, और दामों का पूरा स्तर।"),

    # ---------------------------------------------------------------- recap
    ("recap", "[scene] तो याद रखिए —"),
    (None, "{स्कार्सिटी|Scarcity|⏳} — साधन कम, ज़रूरतें ज़्यादा।"),
    (None, "{तीन सवाल|What · How · For whom|❓} — क्या, कैसे, और किसके लिए।"),
    (None, "{पी पी सी|PPC|📈}, और {ऑपर्च्युनिटी कॉस्ट|Opportunity Cost|⚖️} — जो छोड़ा, वही क़ीमत।"),
    (None, "{मिक्स्ड इकॉनमी|Mixed Economy|🤝}, और {माइक्रो और मैक्रो|Micro & Macro|🔬}।"),

    # ---------------------------------------------------------------- next class + channel
    ("outro:Next: Teen Sectors", "[scene] लेकिन दोस्तों — पालमपुर में किसान थे, कारख़ाना था, और दुकानें भी। पूरे देश में, ये काम कैसे बँटे हैं?"),
    (None, "[punch] इकॉनमी के तीन सेक्टर — खेती, कारख़ाना, और सेवा — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
