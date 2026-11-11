"""Econ12 - Ramesh Singh Ch 2: National Income (deep dive). Course plan: RS 18e Ch 2, class 12.
DRAFT FROM STANDARD FACTS: written without the book in hand; check against Ramesh Singh 18e Ch 2 (send pages to
match exactly). Do not add the current base year or growth figures until checked against the latest official release.
Facts used (standard): India's national income is estimated by the National Statistical Office (NSO) of the Ministry
of Statistics and Programme Implementation; the NSO was formed in 2019 by merging the Central Statistics Office (CSO)
and the National Sample Survey Office (NSSO). Prices: factor cost; basic price = factor cost + production taxes -
production subsidies; market price = basic price + product taxes - product subsidies. Since the 2011-12 series India
reports GVA (gross value added) at basic prices for sectors and GDP at market prices = GVA + product taxes - product
subsidies. Real figures use constant prices of a base year; the base year is revised from time to time so the data
reflect today's economy. Per capita income = national income / population. GDP can be compared across countries
at market exchange rates or at purchasing power parity (PPP), which adjusts for price differences.
"""
CHAPTER = dict(num=12, title="National Income — Bharat ka Hisaab", kicker="ECONOMICS · CLASS 12 · RAMESH SINGH CH 2",
               rain="🧮", outro_icons=("📈", "😊"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Vikas kya hai?")

TOPICS = [
    dict(id="who", name="Who Counts?", label="NSO, MoSPI", icon="🏛️"),
    dict(id="prices", name="Which Price?", label="Factor cost · Basic · Market", icon="🏷️"),
    dict(id="gva", name="GVA and GDP", label="India's way of reporting", icon="🧮"),
    dict(id="base", name="Base Year & Per Capita", label="Real growth, per person", icon="📅"),
    dict(id="ppp", name="Comparing Countries", label="Exchange rate or PPP?", icon="🌍"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक ही समोसा — दुकान पर {दस रुपये|₹10|🥟}।"),
    (None, "लेकिन इसमें दुकानदार की कमाई कितनी? और सरकार का टैक्स कितना?"),
    (None, "[punch] देश की कमाई गिनते वक़्त — कौन-सा दाम लें? यहीं से शुरू होता है, असली हिसाब!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — भारत में ये {हिसाब रखता कौन है|NSO|🏛️}।"),
    (None, "दूसरा — {फ़ैक्टर कॉस्ट, बेसिक प्राइस, मार्केट प्राइस|3 Prices|🏷️} का फ़र्क़।"),
    (None, "तीसरा — {जी वी ए और जीडीपी|GVA & GDP|🧮} — भारत कैसे रिपोर्ट करता है।"),
    (None, "और चौथा — {बेस ईयर, पर कैपिटा, और पी पी पी|Base year · Per capita · PPP|📅}।"),

    ("center", "[name] रमेश सिंह, चैप्टर दो — नेशनल इनकम!"),
    ("topics", "चलिए — हिसाब की किताब खोलते हैं!"),

    ("focus:who", "[scene] भारत की नेशनल इनकम का हिसाब रखता है — {एन एस ओ|NSO|🏛️}। यानी नेशनल स्टैटिस्टिकल ऑफ़िस।"),
    (None, "ये है — {सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय|MoSPI|📊} का हिस्सा।"),
    (None, "[name] {दो हज़ार उन्नीस|2019|📅} में — {सी एस ओ|CSO|📁} और {एन एस एस ओ|NSSO|📋} — दोनों को मिलाकर, बना एन एस ओ।"),

    ("focus:prices", "[scene] अब समोसे के दाम को, परत-दर-परत खोलिए।"),
    (None, "सबसे अंदर — {फ़ैक्टर कॉस्ट|Factor Cost|🧑‍🍳}। यानी बनाने वालों की कमाई — मज़दूरी, किराया, ब्याज, मुनाफ़ा।"),
    (None, "उसमें जोड़िए — उत्पादन पर लगे टैक्स, घटाइए — उत्पादन पर मिली सब्सिडी। तो मिलता है — {बेसिक प्राइस|Basic Price|🏭}।"),
    (None, "और उसमें जोड़िए — माल पर लगे टैक्स, जैसे {जी एस टी|Product taxes|🧾} — घटाइए — माल पर सब्सिडी। तो मिलता है — {मार्केट प्राइस|Market Price|🏷️}, जो आप दुकान पर देते हैं।"),
    ("ex:", "यानी — {फ़ैक्टर कॉस्ट से बेसिक प्राइस, बेसिक से मार्केट प्राइस|FC → BP → MP|🪜}। हर सीढ़ी पर — टैक्स जुड़ा, सब्सिडी घटी।"),

    ("focus:gva", "[scene] अब भारत की रिपोर्ट पढ़िए।"),
    (None, "[name] हर सेक्टर ने कितना जोड़ा — वो है {जी वी ए|GVA at basic prices|🏭}। यानी ग्रॉस वैल्यू एडेड, बेसिक प्राइस पर।"),
    (None, "[punch] और {जीडीपी|GDP = GVA + Product taxes − Subsidies|🧮} — जी वी ए, जमा माल पर टैक्स, घटा माल पर सब्सिडी।"),
    (None, "इसलिए ख़बरों में दोनों दिखते हैं — सेक्टर की बढ़त, जी वी ए से। और पूरे देश की बढ़त, जीडीपी से।"),

    ("focus:base", "[scene] याद है — रियल जीडीपी, एक {बेस ईयर|Base Year|📅} के दामों पर गिनी जाती है।"),
    (None, "लेकिन इकॉनमी बदलती रहती है — नई चीज़ें, नए काम। इसलिए बेस ईयर भी, {समय-समय पर बदला|Revised from time to time|🔄} जाता है।"),
    (None, "[scene] और एक आदमी के हिस्से, औसतन कितनी कमाई? नेशनल इनकम को, आबादी से भाग दीजिए।"),
    (None, "[name] यही है — {पर कैपिटा इनकम|Per Capita Income = NI / Population|🧍}।"),

    ("focus:ppp", "[scene] आख़िर में — भारत और अमेरिका की जीडीपी, कैसे मिलाएँ?"),
    (None, "एक तरीक़ा — {एक्सचेंज रेट|Market exchange rate|💱}। यानी रुपये को, डॉलर में बदल दो।"),
    (None, "[punch] लेकिन भारत में, बहुत-सी चीज़ें सस्ती हैं! एक बाल कटाई — यहाँ और वहाँ, दाम में बहुत फ़र्क़।"),
    (None, "[name] इसलिए दूसरा तरीक़ा — {पी पी पी|PPP|⚖️}। यानी परचेज़िंग पावर पैरिटी — जो दामों के इस फ़र्क़ को, बराबर करके देखता है।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{एन एस ओ|NSO, 2019|🏛️} — सी एस ओ और एन एस एस ओ से बना।"),
    (None, "{तीन दाम|FC → BP → MP|🏷️} — फ़ैक्टर कॉस्ट, बेसिक, और मार्केट।"),
    (None, "{जी वी ए और जीडीपी|GVA & GDP|🧮}।"),
    (None, "{बेस ईयर|Base Year|📅}, {पर कैपिटा|Per Capita|🧍}, और {पी पी पी|PPP|⚖️}।"),

    ("outro:Next: Vikas kya hai?", "[scene] लेकिन दोस्तों — अगर कमाई बढ़ी, पर स्कूल नहीं, अस्पताल नहीं — तो क्या वो विकास है?"),
    (None, "[punch] विकास असल में क्या है — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
