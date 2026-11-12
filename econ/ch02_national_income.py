"""Ch02 - National Income: one full class for Ramesh Singh, Indian Economy (18e), Chapter 2. Hinglish; one connected
story (Riya, continuing from Chapter 1: her pizza and its chain from farm to shop). Welcome + subscribe, short master
map (Chapter 1 done, Chapter 2 today), the class, recap, next class, about us + subscribe.
DRAFT: concepts are the standard national-income concepts covered by Ramesh Singh Ch 2; to be checked against the book
pages before the video is made. Story numbers (₹20, ₹50, ₹200 pizza, oven) are illustrations, not data.
Standard facts: GDP = market value of all final goods and services produced within the domestic territory of a
country in a year (India uses the financial year, April to March); only final goods are counted (avoids double
counting); value added = value of output - intermediate consumption. NDP = GDP - depreciation. GNP = GDP + net factor
income from abroad (income of residents from abroad - income of non-residents from India). NNP = GNP - depreciation;
NNP at factor cost = national income. Factor cost; basic price = factor cost + production taxes - production subsidies;
market price = basic price + product taxes - product subsidies (older form: market price = factor cost + indirect
taxes - subsidies). GVA at basic prices; GDP = GVA + product taxes - product subsidies. Three methods: product
(value added), income (wages, rent, interest, profit), expenditure (C + I + G + exports - imports). Nominal (current
prices) vs real (constant prices of a base year); GDP deflator = nominal / real x 100. Per capita income = national
income / population. PPP compares price levels across countries; by PPP India is the world's third-largest economy.
In India national income is estimated by the National Statistical Office (NSO), MoSPI; NSO formed in 2019 by merging
the CSO and NSSO. The new series of January 2015 used base year 2011-12 and moved to GVA at basic prices.
"""
BOOK = ["Introduction to Economics", "National Income", "Growth, Development & Happiness", "Evolution of the Indian Economy",
        "Economic Planning", "Planning in India", "Economic Reforms", "Inflation & Business Cycle",
        "Agriculture & Food Management", "Industry & Infrastructure", "Services Sector", "Indian Financial Market",
        "Banking in India", "Insurance in India", "Security Market in India", "External Sector in India",
        "International Economic Organisations & India", "Tax Structure in India", "Public Finance in India",
        "Sustainability & Climate Change", "Human Development in India", "Burning Socio-Economic Issues"]

CHAPTER = dict(num=2, title="National Income", kicker="RAMESH SINGH · CHAPTER 2", rain="💹",
               video="Ch02 – National Income", book=BOOK, master_all=True,
               outro_icons=("😊", "📈"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next: Chapter 3 — Growth, Development & Happiness")

TOPICS = [
    dict(id="gdp", name="GDP", label="Counting the whole country", icon="🧮"),
    dict(id="value", name="Final Goods & Value Added", label="Count only once", icon="🍕"),
    dict(id="family", name="NDP · GNP · NNP", label="The GDP family", icon="👨‍👩‍👧"),
    dict(id="prices", name="Factor Cost & Market Price", label="Which price?", icon="🏷️"),
    dict(id="methods", name="Three Methods", label="Product · Income · Expenditure", icon="🔢"),
    dict(id="real", name="Nominal vs Real", label="Is the rise real?", icon="🔍"),
    dict(id="percapita", name="Per Capita & PPP", label="Per person, across countries", icon="🌍"),
    dict(id="india", name="Who Counts in India?", label="NSO, new series", icon="🏛️"),
]

LINES = [
    # ---------------------------------------------------------------- welcome
    ("hook", "[scene] नमस्ते दोस्तों! वेलकम बैक — {द विज़ुअल माइंड|The VisualMind|🧠} पर!"),
    (None, "[punch] अगर आप नए हैं — तो चैनल को अभी {सब्सक्राइब|Subscribe|🔔} कीजिए, और बेल आइकन दबा दीजिए!"),

    # ---------------------------------------------------------------- master map (short)
    ("master", "[name] ये रहा हमारा मैप — रमेश सिंह की पूरी किताब।"),
    (None, "{चैप्टर वन|Chapter 1|✅} — हो गया! इकॉनॉमिक्स क्या है, इकॉनॉमिक सिस्टम्स, और पाँच सेक्टर्स।"),
    (None, "[punch] और आज — {चैप्टर टू|Chapter 2|💹}! नेशनल इनकम।"),

    # ---------------------------------------------------------------- today's story
    ("today", "[scene] याद है — {रिया|Riya|👩‍🎓}? पिछली क्लास में, उसने सौ रुपये में {पिज़्ज़ा|Pizza|🍕} चुना था।"),
    (None, "आज रिया के मन में, एक नया सवाल है।"),
    (None, "मेरे एक पिज़्ज़ा के पीछे — किसान, आटा मिल, और पिज़्ज़ा शॉप। सबने कुछ कमाया। तो पूरी {कंट्री|Country|🇮🇳} ने, एक साल में, कुल कितना कमाया?"),
    (None, "[punch] और ये गिनेगा कौन? और कैसे?"),
    (None, "आज की पूरी क्लास — रिया के इसी पिज़्ज़ा के साथ चलेगी!"),

    # ---------------------------------------------------------------- today's class
    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {जीडीपी|GDP|🧮} क्या है, और कमाई सिर्फ़ एक बार कैसे गिनें।"),
    (None, "दूसरा — जीडीपी की पूरी {फ़ैमिली|Family|👨‍👩‍👧} — एन डी पी, जी एन पी, एन एन पी।"),
    (None, "तीसरा — कौन-सा {प्राइस|Price|🏷️} लें, और गिनने के तीन तरीक़े।"),
    (None, "और चौथा — {रियल ग्रोथ|Real growth|🔍}, पर कैपिटा इनकम, और इंडिया में ये गिनती कौन करता है।"),

    ("center", "[name] रमेश सिंह, चैप्टर टू — नेशनल इनकम!"),
    ("topics", "और शुरुआत — रिया के पिज़्ज़ा से!"),

    # ---------------------------------------------------------------- 1. GDP
    ("focus:gdp", "[scene] पूरी कंट्री की कमाई को, एक नंबर में बताने का तरीक़ा है — {जीडीपी|GDP|🧮}। यानी {ग्रॉस डोमेस्टिक प्रोडक्ट|Gross Domestic Product|🧮}।"),
    (None, "[name] जीडीपी मतलब — एक साल में, कंट्री की {बाउंड्री के अंदर|Domestic territory|🗺️} बने, सारे {फ़ाइनल गुड्स और सर्विसेज़|Final goods & services|🍕} की {मार्केट वैल्यू|Market value|💰}।"),
    (None, "तीन शब्द याद रखिए। पहला — {डोमेस्टिक|Domestic|🗺️}। यानी कंट्री के अंदर बना। बनाने वाला कोई भी हो।"),
    (None, "दूसरा — {फ़ाइनल|Final|🍕}। यानी जो आख़िरी कस्टमर तक पहुँचा — जैसे रिया का पिज़्ज़ा।"),
    (None, "और तीसरा — {एक साल|Ek saal|📅}। इंडिया में ये साल है — {फ़ाइनेंशियल ईयर|Financial year|📅}, यानी {अप्रैल से मार्च|April se March|🗓️}।"),
    (None, "लेकिन रिया पूछती है — सिर्फ़ फ़ाइनल ही क्यों? गेहूँ और आटा क्यों नहीं?"),

    # ---------------------------------------------------------------- 2. Final goods and value added
    ("focus:value", "[scene] चलिए, रिया के पिज़्ज़ा की चेन देखते हैं। मान लीजिए — किसान ने गेहूँ बेचा, {बीस रुपये|₹20|🌾} में।"),
    (None, "आटा मिल ने उसका आटा बेचा — {पचास रुपये|₹50|🏭} में।"),
    (None, "और पिज़्ज़ा शॉप ने पिज़्ज़ा बेचा — {सौ रुपये|₹100|🍕} में।"),
    (None, "[scene] अब अगर तीनों जोड़ दें — बीस, पचास, और सौ — तो बने, {एक सौ सत्तर|₹170|➕}।"),
    (None, "[punch] लेकिन रुकिए! गेहूँ तो आटे में भी गिना गया, और पिज़्ज़ा में भी। एक ही चीज़ — बार-बार! इसे कहते हैं — {डबल काउंटिंग|Double counting|⚠️}।"),
    (None, "[name] इसलिए गेहूँ और आटा — {इंटरमीडिएट गुड्स|Intermediate goods|🌾}। और पिज़्ज़ा — {फ़ाइनल गुड|Final good|🍕}। जीडीपी में गिनते हैं — सिर्फ़ फ़ाइनल।"),
    (None, "[scene] या फिर — हर स्टेप पर, सिर्फ़ उतना गिनिए, जितना {नया जुड़ा|Naya juda|➕}।"),
    (None, "किसान ने जोड़े — {बीस|20|🌾}। मिल ने — {तीस|30|🏭}। और शॉप ने — {पचास|50|🍕}।"),
    (None, "[punch] बीस, तीस, और पचास — कुल {सौ|100|✅}! ठीक पिज़्ज़ा की क़ीमत!"),
    (None, "[name] हर स्टेप पर जो नया जुड़ा — उसे कहते हैं — {वैल्यू एडेड|Value Added|➕}। और पूरी कंट्री का वैल्यू एडेड जोड़ें — तो बनता है {जी वी ए|GVA|🏭}, यानी ग्रॉस वैल्यू एडेड।"),
    (None, "लेकिन पिज़्ज़ा बनाने में, शॉप का {ओवन|Oven|🔥} भी तो, थोड़ा घिस गया। उसका क्या?"),

    # ---------------------------------------------------------------- 3. The GDP family
    ("focus:family", "[scene] शॉप का ओवन, हर साल थोड़ा घिसता है। एक दिन उसे बदलना पड़ेगा। इस घिसाई को कहते हैं — {डेप्रिसिएशन|Depreciation|🔧}।"),
    (None, "[name] जीडीपी में से, डेप्रिसिएशन घटा दें — तो मिलता है {एन डी पी|NDP|➖}। यानी नेट डोमेस्टिक प्रोडक्ट।"),
    (None, "[scene] अब रिया का कज़िन — {दुबई|Dubai|✈️} में काम करता है, और कमाई घर भेजता है।"),
    (None, "और इंडिया में, एक {विदेशी कंपनी|Foreign company|🏢} कमाती है — और अपना प्रॉफ़िट, बाहर भेजती है।"),
    (None, "[name] बाहर से आई इंडियन्स की कमाई — घटा — बाहर गई विदेशियों की कमाई। इसे कहते हैं — {नेट फ़ैक्टर इनकम फ़्रॉम अब्रॉड|Net Factor Income from Abroad|🌐}।"),
    (None, "[name] जीडीपी में, ये जोड़ दें — तो मिलता है {जी एन पी|GNP|🌐}। यानी ग्रॉस नेशनल प्रोडक्ट।"),
    ("ex:", "यानी — {डोमेस्टिक|Domestic|🗺️} मतलब, कंट्री की बाउंड्री के अंदर। और {नेशनल|National|🇮🇳} मतलब, कंट्री के लोगों की कमाई — वो दुनिया में कहीं भी हों।"),
    (None, "[name] और जी एन पी में से, डेप्रिसिएशन घटा दें — तो {एन एन पी|NNP|➖}। यानी नेट नेशनल प्रोडक्ट।"),
    (None, "[punch] और फ़ैक्टर कॉस्ट पर एन एन पी — यही है — {नेशनल इनकम|National Income|👑}! यानी हमारे चैप्टर का नाम!"),
    (None, "लेकिन ये फ़ैक्टर कॉस्ट क्या है? इसके लिए, रिया के पिज़्ज़ा का बिल देखना पड़ेगा।"),

    # ---------------------------------------------------------------- 4. Factor cost and market price
    ("focus:prices", "[scene] रिया के पिज़्ज़ा का बिल खोलिए। उसमें छुपी हैं — {तीन क़ीमतें|Teen keemtein|🏷️}।"),
    (None, "[name] सबसे अंदर — {फ़ैक्टर कॉस्ट|Factor Cost|🧑‍🍳}। यानी पिज़्ज़ा बनाने वालों की कमाई — वेजेज़, रेंट, इंटरेस्ट, और प्रॉफ़िट।"),
    (None, "[name] उसमें जोड़िए — प्रोडक्शन पर लगे टैक्स, और घटाइए — प्रोडक्शन पर मिली सब्सिडी। तो बनता है — {बेसिक प्राइस|Basic Price|🏭}।"),
    (None, "[name] और उसमें जोड़िए — प्रोडक्ट पर लगे टैक्स, जैसे {जी एस टी|GST|🧾} — और घटाइए, प्रोडक्ट पर सब्सिडी। तो बनता है — {मार्केट प्राइस|Market Price|🏷️}। यानी वो क़ीमत, जो रिया ने दी।"),
    ("ex:", "यानी सीढ़ी — {फ़ैक्टर कॉस्ट से बेसिक प्राइस, और बेसिक प्राइस से मार्केट प्राइस|Factor Cost → Basic Price → Market Price|🪜}। हर सीढ़ी पर — टैक्स जुड़ा, सब्सिडी घटी।"),
    (None, "[scene] और इंडिया की रिपोर्ट में — हर सेक्टर की कमाई, {बेसिक प्राइस पर जी वी ए|GVA at basic prices|🏭} से दिखती है।"),
    (None, "[punch] और जीडीपी? {जी वी ए, जमा प्रोडक्ट टैक्स, घटा प्रोडक्ट सब्सिडी|GVA + Product taxes − Subsidies|🧮}!"),
    (None, "अब सवाल — इतनी बड़ी कंट्री की ये सारी कमाई, गिनी कैसे जाती है?"),

    # ---------------------------------------------------------------- 5. Three methods
    ("focus:methods", "[scene] गिनने के — {तीन तरीक़े|Teen tareeke|🔢}। और तीनों — एक ही जवाब तक पहुँचते हैं।"),
    (None, "[name] पहला — {प्रोडक्ट मेथड|Product Method|🏭}। जिसे {वैल्यू एडेड मेथड|Value Added Method|➕} भी कहते हैं। हर स्टेप पर, नया क्या जुड़ा — वही, जो हमने पिज़्ज़ा में किया।"),
    (None, "[name] दूसरा — {इनकम मेथड|Income Method|💵}। बनाने वालों को क्या मिला — {वेजेज़|Wages|👷}, {रेंट|Rent|🏠}, {इंटरेस्ट|Interest|🏦}, और {प्रॉफ़िट|Profit|💰}।"),
    ("ex:", "शॉप के वर्कर की सैलरी, दुकान का किराया, लोन का इंटरेस्ट, और मालिक का प्रॉफ़िट — सब जोड़िए।"),
    (None, "[name] और तीसरा — {एक्सपेंडिचर मेथड|Expenditure Method|🛒}। फ़ाइनल चीज़ों पर, किसने कितना ख़र्च किया।"),
    (None, "लोगों का ख़र्च — जैसे रिया का पिज़्ज़ा — {सी|C|🛒}। कंपनियों का इन्वेस्टमेंट — जैसे नया ओवन — {आई|I|🔥}। गवर्नमेंट का ख़र्च — {जी|G|🏛️}। और {एक्सपोर्ट घटा इम्पोर्ट|Exports − Imports|🚢}।"),
    (None, "[punch] क्योंकि जो बना — वो किसी की कमाई बना, और किसी ने उस पर ख़र्च किया। इसलिए तीनों का जवाब — {एक|Ek|⚖️}!"),
    (None, "लेकिन अगर पिज़्ज़ा का दाम ही बढ़ गया — तो क्या कंट्री सच में अमीर हुई?"),

    # ---------------------------------------------------------------- 6. Nominal vs real
    ("focus:real", "[scene] सोचिए — पिछले साल, रिया का पिज़्ज़ा सौ रुपये का था। और इस साल — {दो सौ|₹200|🍕} का।"),
    (None, "शॉप ने उतने ही पिज़्ज़ा बेचे — लेकिन कमाई, {डबल|Double|📈}!"),
    (None, "[punch] तो क्या शॉप ने, ज़्यादा पिज़्ज़ा बनाए? बिल्कुल नहीं! बस दाम बढ़ा।"),
    (None, "[name] आज के दामों पर गिनी गई जीडीपी — {नॉमिनल जीडीपी|Nominal GDP|💵}। यानी {करंट प्राइसेज़|Current prices|💵} पर।"),
    (None, "[name] और एक {बेस ईयर|Base year|📅} के, फ़िक्स्ड दामों पर गिनी गई — {रियल जीडीपी|Real GDP|🔍}। यानी {कॉन्स्टेंट प्राइसेज़|Constant prices|🔒} पर।"),
    (None, "[punch] रियल जीडीपी बताती है — सच में, {ज़्यादा बना|Zyada bana|🏭} या नहीं।"),
    (None, "[name] और दोनों का रेशियो — {जीडीपी डिफ़्लेटर|GDP Deflator|🎈}। नॉमिनल, भाग, रियल, गुणा सौ। ये बताता है — दाम कितने बढ़े।"),
    (None, "अब कंट्री की कमाई तो पता चली। लेकिन रिया के हिस्से में, कितनी आई?"),

    # ---------------------------------------------------------------- 7. Per capita and PPP
    ("focus:percapita", "[scene] पूरी नेशनल इनकम को, कंट्री की {पॉपुलेशन|Population|👥} से भाग दीजिए।"),
    (None, "[name] जो मिला — वो है {पर कैपिटा इनकम|Per Capita Income|🧍}। यानी एक इंसान के हिस्से की, एवरेज कमाई।"),
    (None, "[punch] लेकिन ध्यान दीजिए — ये {एवरेज|Average|➗} है। सबके पास, इतना हो — ज़रूरी नहीं।"),
    (None, "[scene] और अब — इंडिया और अमेरिका की कमाई, कैसे मिलाएँ?"),
    (None, "एक तरीक़ा — रुपये को, डॉलर में बदल दो — यानी {एक्सचेंज रेट|Exchange rate|💱} से।"),
    (None, "[punch] लेकिन इंडिया में, बहुत सी चीज़ें सस्ती हैं! रिया का पिज़्ज़ा — यहाँ और वहाँ, क़ीमत में बहुत फ़र्क़।"),
    (None, "[name] इसलिए दूसरा तरीक़ा — {पी पी पी|PPP|⚖️}। यानी {परचेज़िंग पावर पैरिटी|Purchasing Power Parity|⚖️}। ये दामों के फ़र्क़ को, बराबर करके देखता है।"),
    (None, "[punch] और पी पी पी के हिसाब से — इंडिया, दुनिया की {तीसरी सबसे बड़ी इकॉनमी|Third largest economy|🥉} है!"),
    (None, "लेकिन ये सारी गिनती — आख़िर करता कौन है?"),

    # ---------------------------------------------------------------- 8. Who counts in India
    ("focus:india", "[scene] इंडिया में, नेशनल इनकम का हिसाब रखता है — {एन एस ओ|NSO|🏛️}। यानी नेशनल स्टैटिस्टिकल ऑफ़िस।"),
    (None, "ये है — {मिनिस्ट्री ऑफ़ स्टैटिस्टिक्स एंड प्रोग्राम इम्प्लीमेंटेशन|MoSPI|📊} का हिस्सा।"),
    (None, "[name] {दो हज़ार उन्नीस|2019|📅} में — {सी एस ओ|CSO|📁} और {एन एस एस ओ|NSSO|📋} — दोनों को मिलाकर, बना एन एस ओ।"),
    (None, "[scene] और {जनवरी दो हज़ार पंद्रह|January 2015|📅} में, आई एक {नई सीरीज़|New series|🆕}।"),
    (None, "इसमें बेस ईयर हुआ — {दो हज़ार ग्यारह-बारह|2011-12|📅}। और सेक्टर्स की कमाई, दिखने लगी — {बेसिक प्राइस पर जी वी ए|GVA at basic prices|🏭} में।"),
    (None, "[punch] और बेस ईयर — {समय-समय पर बदला|Samay-samay par badla|🔄} जाता है। ताकि आज की इकॉनमी की, सही तस्वीर मिले।"),

    # ---------------------------------------------------------------- recap
    ("recap", "[scene] तो याद कीजिए, रिया के पिज़्ज़ा के साथ आज का सफ़र —"),
    (None, "{जीडीपी|GDP|🧮} — डोमेस्टिक, फ़ाइनल, और एक साल।"),
    (None, "{डबल काउंटिंग|Double counting|⚠️} से बचो — और {वैल्यू एडेड|Value Added|➕} गिनो।"),
    (None, "{एन डी पी, जी एन पी, एन एन पी|NDP, GNP, NNP|👨‍👩‍👧} — और {नेशनल इनकम|National Income|👑}।"),
    (None, "{तीन प्राइसेज़|Teen prices|🏷️} — और {तीन मेथड्स|Teen methods|🔢}।"),
    (None, "{नॉमिनल और रियल|Nominal aur Real|🔍}, {पर कैपिटा|Per Capita|🧍}, {पी पी पी|PPP|⚖️} — और {एन एस ओ|NSO|🏛️}।"),

    # ---------------------------------------------------------------- next class + about us + subscribe
    ("outro:Next: Chapter 3 — Growth, Development & Happiness", "[scene] लेकिन दोस्तों — मान लीजिए, कंट्री की कमाई बढ़ गई। लेकिन रिया के शहर में, न अच्छा हॉस्पिटल, न अच्छा स्कूल।"),
    (None, "[punch] तो क्या ये {डेवलपमेंट|Development|🌱} है? और क्या रिया ख़ुश है? इसका जवाब — चैप्टर थ्री — ग्रोथ, डेवलपमेंट एंड हैप्पीनेस! अगली क्लास में!"),
    ("end", "[scene] और दोस्तों — {द विज़ुअल माइंड|The VisualMind|🧠} पर, हम हर टॉपिक को — एनिमेशन, ग्राफ़, और डेली लाइफ़ के एग्ज़ाम्पल्स के साथ समझाते हैं। ताकि इकॉनमी — बोझ नहीं, मज़ा लगे!"),
    (None, "अगर आज की क्लास अच्छी लगी — तो वीडियो को {लाइक|Like|👍} कीजिए, अपने दोस्तों के साथ {शेयर|Share|📤} कीजिए, और {कमेंट|Comment|💬} में बताइए — आज आपको, सबसे इंटरेस्टिंग क्या लगा?"),
    (None, "[punch] और चैनल को {सब्सक्राइब|Subscribe|🔔} करना मत भूलिए — बेल आइकन ज़रूर दबाइए, ताकि अगली क्लास की नोटिफ़िकेशन, सबसे पहले आपको मिले!"),
    (None, "[punch] {देखिए|Dekhiye.|👀}। {समझिए|Samajhiye.|💡}। {याद रखिए|Yaad rakhiye.|🧠}। मिलते हैं, अगली क्लास में!"),
]
