"""Econ09 - Ramesh Singh Ch 1: Introduction to Economics (deep dive). Course plan: RS 18e Ch 1, class 9.
DRAFT FROM STANDARD FACTS: written without the book in hand; check every topic against Ramesh Singh 18e Ch 1
(or send the chapter pages to match it exactly).
Facts used (standard): Adam Smith, "An Inquiry into the Nature and Causes of the Wealth of Nations" (1776), often
called the father of economics; an economy = the system by which a country produces, distributes and consumes goods
and services. Economic systems: capitalist / market (private ownership, profit motive, prices decide; laissez-faire),
state / socialist (state owns the means of production, planning; the Soviet Union after the 1917 revolution, China
after 1949), mixed (both; gained ground after the Great Depression that began in 1929 and J. M. Keynes's "General
Theory" of 1936; India chose a mixed economy with planning after independence). Sectors: primary, secondary,
tertiary; in some classifications also quaternary (knowledge: research, IT, education) and quinary (top
decision-makers). World Bank groups countries by GNI per person into low, lower-middle, upper-middle and high income;
India is in the lower-middle group. Developed vs developing economies.
"""
CHAPTER = dict(num=9, title="Introduction to Economics", kicker="ECONOMICS · CLASS 9 · RAMESH SINGH CH 1", rain="📘",
               outro_icons=("🌏", "💹"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Poore desh ki economy")

TOPICS = [
    dict(id="what", name="What is Economics?", label="From 1776 to today", icon="📜"),
    dict(id="systems", name="Economic Systems", label="Market, state or mixed", icon="🏛️"),
    dict(id="sectors", name="Sectors, Extended", label="Beyond three", icon="🏗️"),
    dict(id="income", name="Rich or Developing?", label="How the world groups countries", icon="🌍"),
]

LINES = [
    ("hook", "[scene] दोस्तों, सत्रह सौ छिहत्तर। {स्कॉटलैंड|Scotland|🏴}। एक प्रोफ़ेसर, एक मोटी किताब लिखता है।"),
    (None, "नाम — {द वेल्थ ऑफ़ नेशन्स|The Wealth of Nations|📖}। सवाल — कुछ देश अमीर, और कुछ गरीब — क्यों?"),
    (None, "[punch] उस प्रोफ़ेसर को आज कहते हैं — {इकॉनॉमिक्स का पिता|Adam Smith|👴}!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {इकॉनॉमिक्स|Economics|📜} और इकॉनमी, आख़िर हैं क्या।"),
    (None, "दूसरा — दुनिया के {तीन इकॉनॉमिक सिस्टम|3 Economic Systems|🏛️}।"),
    (None, "तीसरा — तीन से आगे, {सेक्टर्स का नया नक्शा|Sectors, extended|🏗️}।"),
    (None, "और चौथा — दुनिया, देशों को {अमीर और विकासशील|Income groups|🌍} में कैसे बाँटती है।"),

    ("center", "[name] रमेश सिंह, चैप्टर एक — इंट्रोडक्शन टू इकॉनॉमिक्स!"),
    ("topics", "चलिए — सत्रह सौ छिहत्तर से शुरू करते हैं!"),

    ("focus:what", "[scene] {एडम स्मिथ|Adam Smith|👴} की किताब का पूरा नाम — एन इंक्वायरी इनटू द नेचर एंड कॉज़ेज़ ऑफ़ द वेल्थ ऑफ़ नेशन्स। साल — {सत्रह सौ छिहत्तर|1776|📅}।"),
    (None, "[name] और {इकॉनमी|Economy|🌐} मतलब — वो पूरा तंत्र, जिससे कोई देश, चीज़ें और सेवाएँ — {बनाता|Utpaadan|🏭}, {बाँटता|Vitaran|🚚}, और {इस्तेमाल करता|Upbhog|🛒} है।"),
    (None, "और याद है पिछली क्लासें? स्कार्सिटी, तीन सवाल, माइक्रो और मैक्रो — ये सब, इसी एक विषय के हिस्से हैं।"),

    ("focus:systems", "[scene] अब सबसे बड़ा सवाल — तीन फ़ैसले, यानी क्या, कैसे, किसके लिए — लेता कौन है? दुनिया ने, तीन जवाब दिए।"),
    (None, "पहला — {कैपिटलिस्ट इकॉनमी|Capitalist / Market|🏦}। साधन, लोगों के निजी हाथ में। मक़सद — मुनाफ़ा। और फ़ैसले — बाज़ार के दाम करते हैं। सरकार कम से कम दख़ल दे — इसे कहते हैं {लेसे-फ़ेयर|Laissez-faire|🕊️}।"),
    (None, "दूसरा — {स्टेट या सोशलिस्ट इकॉनमी|State / Socialist|🏛️}। साधनों की मालिक — सरकार। फ़ैसले — {प्लानिंग|Planning|📝} से।"),
    (None, "जैसे — {उन्नीस सौ सत्रह|1917|🚩} की क्रांति के बाद का सोवियत संघ। और {उन्नीस सौ उनचास|1949|🇨🇳} के बाद का चीन।"),
    (None, "[scene] फिर आया एक बड़ा झटका — {उन्नीस सौ उनतीस|1929|📉} में शुरू हुई, {ग्रेट डिप्रेशन|Great Depression|🏚️}। बाज़ार अकेले, संभाल नहीं पाया।"),
    (None, "और {उन्नीस सौ छत्तीस|1936|📖} में, {जॉन मेनार्ड कीन्स|J. M. Keynes|🎩} ने कहा — मुश्किल वक़्त में, सरकार को आगे आना चाहिए।"),
    (None, "[name] यहीं से मज़बूत हुआ तीसरा रास्ता — {मिक्स्ड इकॉनमी|Mixed Economy|🤝}। बाज़ार भी, और सरकार भी।"),
    (None, "[punch] और आज़ादी के बाद, {भारत|India|🇮🇳} ने चुनी — प्लानिंग के साथ, मिक्स्ड इकॉनमी!"),

    ("focus:sectors", "[scene] तीन सेक्टर हम जानते हैं — {प्राइमरी|Primary|🌾}, {सेकेंडरी|Secondary|🏭}, {टर्शियरी|Tertiary|🚚}।"),
    (None, "लेकिन कुछ वर्गीकरणों में, सेवाओं को और बाँटा जाता है।"),
    (None, "{क्वाटर्नरी सेक्टर|Quaternary|💡} — ज्ञान का काम। रिसर्च, आईटी, शिक्षा।"),
    (None, "और {क्विनरी सेक्टर|Quinary|🎯} — सबसे ऊँचे फ़ैसले लेने वाले। बड़े अफ़सर, बड़ी कंपनियों के मुखिया।"),

    ("focus:income", "[scene] आख़िर में — दुनिया, देशों को अमीर और गरीब में, बाँटती कैसे है?"),
    (None, "{वर्ल्ड बैंक|World Bank|🏦} देखता है — हर व्यक्ति की औसत आमदनी, यानी {जी एन आई पर कैपिटा|GNI per capita|💰}।"),
    (None, "और देशों को रखता है चार समूहों में — {लो इनकम|Low|🟥}, {लोअर-मिडल|Lower-middle|🟧}, {अपर-मिडल|Upper-middle|🟨}, और {हाई इनकम|High|🟩}।"),
    (None, "[punch] और भारत? अभी — {लोअर-मिडल इनकम|India: Lower-middle|🇮🇳} देशों में।"),
    (None, "आमतौर पर — ऊँची आमदनी वाले देश, {विकसित|Developed|🏙️} कहलाते हैं। और बाक़ी — {विकासशील|Developing|🌱}।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{एडम स्मिथ|Adam Smith, 1776|👴} — द वेल्थ ऑफ़ नेशन्स।"),
    (None, "{तीन सिस्टम|Capitalist · Socialist · Mixed|🏛️} — और भारत, मिक्स्ड।"),
    (None, "{ग्रेट डिप्रेशन|1929 → Keynes 1936|📉} ने बदली सोच।"),
    (None, "{वर्ल्ड बैंक के चार समूह|4 income groups|🌍} — और भारत, लोअर-मिडल।"),

    ("outro:Next: Poore desh ki economy", "[scene] अब तक हमने, एक ग्राहक और एक दुकानदार को देखा। लेकिन दोस्तों — पूरे देश की इकॉनमी, एक साथ कैसे देखें?"),
    (None, "[punch] मैक्रोइकॉनॉमिक्स की दुनिया — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
