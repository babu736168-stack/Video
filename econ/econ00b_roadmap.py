"""Econ00b - Syllabus Roadmap: the whole course as a mind map, Ramesh Singh Chapter 1 -> 22,
with the NCERT foundation classes inside each chapter. Plan: COURSE_PLAN.md.
Markup: {spoken words|Screen label|emoji}; "pt:<text>" shows <text> as the chapter heading of that row.
"""
CHAPTER = dict(num=0, title="Indian Economy", kicker="FULL SYLLABUS · RAMESH SINGH + NCERT", rain="🗺️",
               recap_title="POORA RAASTA", outro_icons=("🏡", "☕"))

TOPICS = [
    dict(id="p1", name="Neev", label="Ch 1–2 · Foundation", icon="🧱"),
    dict(id="p2", name="Bharat ka Safar", label="Ch 3–6 · India's journey", icon="🇮🇳"),
    dict(id="p3", name="Daam aur Sectors", label="Ch 7–10 · Prices & sectors", icon="🏭"),
    dict(id="p4", name="Paisa aur Bazaar", label="Ch 11–14 · Money & markets", icon="💰"),
    dict(id="p5", name="Duniya aur Sarkar", label="Ch 15–18 · World & government", icon="🌍"),
    dict(id="p6", name="Samaj aur Bhavishya", label="Ch 19–22 · People & future", icon="🌱"),
]

LINES = [
    ("hook", "[scene] दोस्तों, पूरी इंडियन इकॉनमी — {बाईस चैप्टर|22 Chapters|📚}, {इक्यावन क्लास|51 Classes|🎬}।"),
    (None, "सुनने में बहुत बड़ा लगता है, है ना?"),
    (None, "[punch] लेकिन घबराइए मत! आज आप देखेंगे — {पूरा रास्ता|Poora Raasta|🗺️}, एक ही नक्शे पर।"),
    ("center", "[name] रमेश सिंह की इंडियन इकॉनमी — और साथ में, एन सी ई आर टी की नींव।"),
    ("topics", "ये बाईस चैप्टर, छह हिस्सों में बँटे हैं। और हर चैप्टर में — पहले एन सी ई आर टी से आसान नींव, फिर रमेश सिंह की गहराई।"),

    # ---------------- Part 1
    ("focus:p1", "[scene] पहला हिस्सा — {नींव|Neev|🧱}। यहीं से सब शुरू होता है।"),
    ("pt:Ch 1 · Introduction", "चैप्टर एक — इंट्रोडक्शन। पहले {पालमपुर की कहानी|Palampur|🏡}, इकॉनमी के {सेक्टर्स|Sectors|🏭}, फिर {डिमांड|Demand|🛒}, {सप्लाई|Supply|🚜}, और {बाज़ार|Market|🏷️} — यानी दाम तय कैसे होता है।"),
    ("pt:Ch 2 · Growth, Development & Happiness", "चैप्टर दो — ग्रोथ, डेवलपमेंट और हैप्पीनेस। {विकास|Development|📈}, {जीडीपी और नेशनल इनकम|GDP & National Income|💹}, और {भारत बनाम पड़ोसी|India vs Neighbours|🌏}।"),

    # ---------------- Part 2
    ("focus:p2", "[scene] दूसरा हिस्सा — {भारत का सफ़र|Bharat ka Safar|🇮🇳}।"),
    ("pt:Ch 3 · Evolution of the Indian Economy", "चैप्टर तीन — {उन्नीस सौ सैंतालीस|1947|🕊️}। आज़ादी के वक़्त, अंग्रेज़ कैसी इकॉनमी छोड़ गए?"),
    ("pt:Ch 4 · Economic Planning", "चैप्टर चार — {प्लानिंग|Planning|📝} क्या है, और {उन्नीस सौ पचास से नब्बे|1950–1990|🏗️} तक भारत ने क्या किया।"),
    ("pt:Ch 5 · Planning in India", "चैप्टर पाँच — {पंचवर्षीय योजनाएँ|Five-Year Plans|📅} से लेकर, {नीति आयोग|NITI Aayog|🏛️} तक।"),
    ("pt:Ch 6 · Economic Reforms", "चैप्टर छह — {उन्नीस सौ इक्यानवे|1991|🔓} का संकट, {एल पी जी सुधार|LPG Reforms|🚀}, और {ग्लोबलाइज़ेशन|Globalisation|🌐}।"),

    # ---------------- Part 3
    ("focus:p3", "[scene] तीसरा हिस्सा — {दाम और सेक्टर्स|Daam aur Sectors|🏭}।"),
    ("pt:Ch 7 · Inflation & Business Cycle", "चैप्टर सात — {महँगाई|Inflation|🔥} क्यों बढ़ती है, और इकॉनमी का {उतार-चढ़ाव|Business Cycle|🎢}।"),
    ("pt:Ch 8 · Agriculture & Food Management", "चैप्टर आठ — {खेती|Agriculture|🌾}, {सबके लिए खाना|Food Security|🍚}, और {गाँव का विकास|Rural Development|🏘️}।"),
    ("pt:Ch 9 · Industry & Infrastructure", "चैप्टर नौ — {कारख़ाने|Industry|🏭}, और {सड़क, बिजली, रेल|Infrastructure|🛤️}।"),
    ("pt:Ch 10 · Services Sector", "चैप्टर दस — {सर्विस सेक्टर|Services|💻}। जैसे {आईटी|IT|🖥️}, {ट्रांसपोर्ट|Transport|🚚}, और {टूरिज़्म|Tourism|✈️}।"),

    # ---------------- Part 4
    ("focus:p4", "[scene] चौथा हिस्सा — {पैसा और बाज़ार|Paisa aur Bazaar|💰}।"),
    ("pt:Ch 11 · Indian Financial Market", "चैप्टर ग्यारह — {पैसा और कर्ज़|Money & Credit|💰}, {मनी मार्केट|Money Market|🏦}, और {कैपिटल मार्केट|Capital Market|📊}।"),
    ("pt:Ch 12 · Banking in India", "चैप्टर बारह — {आर बी आई|RBI|🏦}, बैंक {पैसा कैसे बनाते हैं|Money Creation|🪙}, और {बैंकिंग सुधार|Banking Reforms|🔧}।"),
    ("pt:Ch 13 · Insurance in India", "चैप्टर तेरह — {बीमा|Insurance|☂️}। यानी — मुसीबत के दिन के लिए, आज की तैयारी।"),
    ("pt:Ch 14 · Security Market in India", "चैप्टर चौदह — {शेयर बाज़ार|Share Bazaar|📈}, और उसका चौकीदार — {सेबी|SEBI|🛡️}।"),

    # ---------------- Part 5
    ("focus:p5", "[scene] पाँचवाँ हिस्सा — {दुनिया और सरकार|Duniya aur Sarkar|🌍}।"),
    ("pt:Ch 15 · External Sector in India", "चैप्टर पंद्रह — {बैलेंस ऑफ़ पेमेंट्स|Balance of Payments|⚖️}, और {रुपया बनाम डॉलर|Rupee vs Dollar|💱}।"),
    ("pt:Ch 16 · International Economic Organisations", "चैप्टर सोलह — {आई एम एफ़|IMF|🌍}, {वर्ल्ड बैंक|World Bank|🏦}, {डब्ल्यू टी ओ|WTO|🤝} — और भारत।"),
    ("pt:Ch 17 · Tax Structure in India", "चैप्टर सत्रह — {इनकम टैक्स|Income Tax|🧾}, और {जी एस टी|GST|🧮}।"),
    ("pt:Ch 18 · Public Finance in India", "चैप्टर अठारह — सरकार का {बजट|Budget|📊}, {घाटा|Deficit|📉}, और {सरकारी कर्ज़|Public Debt|💳}।"),

    # ---------------- Part 6
    ("focus:p6", "[scene] और छठा हिस्सा — {समाज और भविष्य|Samaj aur Bhavishya|🌱}।"),
    ("pt:Ch 19 · Sustainability & Climate Change", "चैप्टर उन्नीस — {पर्यावरण|Environment|🌳}, {टिकाऊ विकास|Sustainable Development|♻️}, और {क्लाइमेट चेंज|Climate Change|🌡️}।"),
    ("pt:Ch 20 · Human Development in India", "चैप्टर बीस — {शिक्षा|Education|🎓}, {सेहत|Health|🏥}, {गरीबी|Poverty|🏚️}, और {ह्यूमन कैपिटल|Human Capital|🧠}।"),
    ("pt:Ch 21 · Burning Socio-Economic Issues", "चैप्टर इक्कीस — {रोज़गार|Employment|👷}, {ग्राहक के अधिकार|Consumer Rights|🛍️}, और आज के {बड़े मुद्दे|Big Issues|🔥}।"),
    ("pt:Ch 22 · Economic Concepts & Terminologies", "और चैप्टर बाईस — सारे {ज़रूरी शब्द|Key Terms|📖}, और पूरे कोर्स का {रिवीज़न|Revision|🔁}।"),

    ("recap", "[scene] तो ये रहा पूरा रास्ता —"),
    (None, "{नींव|Neev|🧱}, {भारत का सफ़र|Bharat ka Safar|🇮🇳}, {दाम और सेक्टर्स|Daam aur Sectors|🏭},"),
    (None, "{पैसा और बाज़ार|Paisa aur Bazaar|💰}, {दुनिया और सरकार|Duniya aur Sarkar|🌍}, और {समाज और भविष्य|Samaj aur Bhavishya|🌱}।"),
    (None, "[punch] एक-एक क़दम। एक-एक कहानी।"),
    ("outro:Pehla qadam — Ch 1 · Palampur ki Kahani", "तो पहला क़दम — चैप्टर एक, पालमपुर की कहानी से! मिलते हैं, पहली क्लास में।"),
]
