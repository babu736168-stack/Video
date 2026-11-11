"""Econ11 - GDP aur National Income. Course plan: Ramesh Singh Ch 2, NCERT foundation class 11.
Source: NCERT Class 12 Introductory Macroeconomics, Chapter 2 "National Income Accounting".
Facts used: final goods (for final use, not resold or used up in production) vs intermediate goods; consumption goods
vs capital goods (used for production over many years); stocks (at a point in time, e.g. capital) vs flows (over a
period, e.g. output, income); gross investment, depreciation (wear and tear of capital), net investment = gross
investment - depreciation. Circular flow of income: households give factor services to firms and get factor payments
(wages, rent, interest, profit), and spend that income on firms' goods; so aggregate income = aggregate expenditure =
value of production. Three methods: product (value added) method, expenditure method, income method; all give GDP.
Value added = value of output - value of intermediate goods. GNP = GDP + net factor income from abroad. NNP = GNP -
depreciation. NNP at market prices - (indirect taxes - subsidies) = NNP at factor cost = national income. Nominal GDP
(current prices) vs real GDP (constant prices of a base year); GDP deflator = nominal GDP / real GDP (x 100). GDP and
welfare: GDP need not show welfare because of the distribution of GDP, non-monetary exchanges (work at home, barter)
and externalities (pollution). The baker example uses round illustrative numbers.
"""
CHAPTER = dict(num=11, title="GDP aur National Income", kicker="ECONOMICS · CLASS 11 · NCERT CLASS 12 MACRO", rain="💹",
               outro_icons=("📘", "🧮"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Ramesh Singh Chapter 2 — National Income")

TOPICS = [
    dict(id="basics", name="The Building Blocks", label="Final, capital, stock, flow", icon="🧱"),
    dict(id="flow", name="Circular Flow", label="Money goes round", icon="🔁"),
    dict(id="methods", name="Three Ways to Count", label="Product · Expenditure · Income", icon="🧮"),
    dict(id="family", name="The GDP Family", label="GNP · NNP · National Income", icon="👨‍👩‍👧"),
    dict(id="real", name="Real vs Nominal", label="Is the rise real?", icon="🔍"),
    dict(id="welfare", name="GDP and Welfare", label="What GDP misses", icon="❤️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, ख़बरों में रोज़ सुनते हैं — भारत की {जीडीपी|GDP|📈} बढ़ी!"),
    (None, "लेकिन एक सौ चालीस करोड़ से ज़्यादा लोगों की, पूरे साल की कमाई — कोई गिनता कैसे है?"),
    (None, "[punch] और क्या जीडीपी बढ़ी — मतलब सब ख़ुश हैं? चलिए देखते हैं!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {फ़ाइनल गुड्स, स्टॉक और फ़्लो|Building blocks|🧱} जैसी बुनियादी बातें।"),
    (None, "दूसरा — {सर्कुलर फ़्लो|Circular Flow|🔁}, और गिनने के तीन तरीक़े।"),
    (None, "तीसरा — {जी एन पी, एन एन पी, नेशनल इनकम|GNP · NNP · NI|👨‍👩‍👧} का पूरा परिवार।"),
    (None, "और चौथा — {असली बढ़त|Real GDP & Welfare|🔍} और जीडीपी की कमियाँ।"),

    ("center", "[name] क्लास ग्यारह — जीडीपी और नेशनल इनकम!"),
    ("topics", "चलिए — ईंट से ईंट जोड़ते हैं!"),

    ("focus:basics", "[scene] बेकर ने आटा ख़रीदा, ब्रेड बनाई। आटा — {इंटरमीडिएट गुड|Intermediate|🌾}, क्योंकि वो बनाने में ख़त्म हो गया। ब्रेड — {फ़ाइनल गुड|Final|🍞}।"),
    (None, "ब्रेड खाई — वो {कंज़म्प्शन गुड|Consumption good|🍞}। और बेकर का ओवन, सालों चलता है — वो {कैपिटल गुड|Capital good|🔥}।"),
    (None, "[scene] अब एक टंकी सोचिए। उसमें {कितना पानी है|Stock|🪣} — किसी एक पल में — वो है स्टॉक।"),
    (None, "और नल से {हर घंटे कितना आया|Flow|🚰} — वो है फ़्लो। कमाई और उत्पादन — फ़्लो हैं, एक समय में नापे जाते हैं।"),
    (None, "[scene] ओवन हर साल थोड़ा घिसता है — इसे कहते हैं {डेप्रिसिएशन|Depreciation|🔧}।"),
    (None, "[name] नए ओवन पर कुल ख़र्च — {ग्रॉस इन्वेस्टमेंट|Gross Investment|🏗️}। उसमें से घिसावट घटाएँ — तो {नेट इन्वेस्टमेंट|Net = Gross − Depreciation|➖}।"),

    ("focus:flow", "[scene] अब पूरी इकॉनमी को, एक गोल चक्कर की तरह देखिए।"),
    (None, "{परिवार|Households|🏠} — फ़र्मों को अपनी मेहनत, ज़मीन, पूँजी देते हैं।"),
    (None, "बदले में {फ़र्म्स|Firms|🏭} देती हैं — {मज़दूरी, किराया, ब्याज, मुनाफ़ा|Wages · Rent · Interest · Profit|💵}।"),
    (None, "और परिवार, यही पैसा — फ़र्मों का सामान ख़रीदने में, वापस ख़र्च कर देते हैं।"),
    (None, "[name] पैसा गोल-गोल घूमता है — इसे कहते हैं {सर्कुलर फ़्लो ऑफ़ इनकम|Circular Flow|🔁}।"),
    (None, "[punch] और इसीलिए — कुल उत्पादन, कुल कमाई, और कुल ख़र्च — {तीनों बराबर|Output = Income = Spending|⚖️}!"),

    ("focus:methods", "[scene] तो गिनने के, तीन रास्ते।"),
    (None, "पहला — {प्रोडक्ट मेथड|Product / Value Added|🏭}। हर फ़र्म ने कितना जोड़ा? यानी उसके माल की क़ीमत — घटा — ख़रीदा हुआ कच्चा माल। इसे कहते हैं {वैल्यू एडेड|Value Added|➕}।"),
    ("ex:", "जैसे — किसान का गेहूँ, सौ रुपये। बेकर ने उससे ब्रेड बनाई, डेढ़ सौ की। तो बेकर ने जोड़ा — {पचास रुपये|Value added ₹50|🍞}।"),
    (None, "दूसरा — {एक्सपेंडिचर मेथड|Expenditure|🛒}। फ़ाइनल चीज़ों पर, कुल कितना ख़र्च हुआ?"),
    (None, "तीसरा — {इनकम मेथड|Income|💵}। मज़दूरी, किराया, ब्याज, मुनाफ़ा — सबकी कुल कमाई कितनी?"),
    (None, "[punch] तीनों रास्ते — एक ही मंज़िल तक — {जीडीपी|GDP|🧮}!"),

    ("focus:family", "[scene] अब जीडीपी का परिवार।"),
    (None, "देश के अंदर कमाई — जीडीपी। लेकिन कुछ भारतीय, विदेश में कमाते हैं — और कुछ विदेशी, भारत में।"),
    (None, "[name] जीडीपी में, विदेश से आई कुल कमाई का फ़र्क़ जोड़ें — यानी {नेट फ़ैक्टर इनकम फ़्रॉम अब्रॉड|NFIA|✈️} — तो मिलता है {जी एन पी|GNP = GDP + NFIA|🌐}।"),
    (None, "जी एन पी में से, घिसावट घटाएँ — तो {एन एन पी|NNP = GNP − Depreciation|➖}।"),
    (None, "[scene] और दाम में छुपे, {अप्रत्यक्ष टैक्स|Indirect taxes|🧾} हटाएँ, और {सब्सिडी|Subsidies|🎁} जोड़ें — तो मिलता है, फ़ैक्टर कॉस्ट पर एन एन पी।"),
    (None, "[punch] और यही है — {नेशनल इनकम|National Income = NNP at factor cost|👑}!"),

    ("focus:real", "[scene] अब एक धोखा पकड़िए। पिछले साल सौ ब्रेड, दस रुपये की। इस साल भी सौ ब्रेड — लेकिन बीस रुपये की।"),
    (None, "[punch] कमाई दोगुनी दिखी — लेकिन ब्रेड तो, उतनी ही बनी!"),
    (None, "[name] आज के दामों पर गिनी गई — {नॉमिनल जीडीपी|Nominal GDP|💵}। और एक बेस ईयर के, स्थिर दामों पर — {रियल जीडीपी|Real GDP|🔍}।"),
    (None, "दोनों का अनुपात — {जीडीपी डिफ़्लेटर|GDP Deflator = Nominal / Real|🎈}। ये बताता है, दाम कितने बढ़े।"),

    ("focus:welfare", "[scene] आख़िरी सवाल — जीडीपी बढ़ी, तो क्या सब ख़ुश?"),
    (None, "पहली बात — {बँटवारा|Distribution|⚖️}। अगर बढ़त, सिर्फ़ कुछ लोगों तक पहुँची — तो ज़्यादातर लोगों का भला, नहीं हुआ।"),
    (None, "दूसरी — {बिना पैसे के काम|Non-monetary work|🏠}। घर का खाना, बच्चों की देखभाल, अदला-बदली — ये जीडीपी में गिने ही नहीं जाते।"),
    (None, "तीसरी — {प्रदूषण|Externalities|🏭}। कारख़ाने ने माल बनाया — जीडीपी बढ़ी। लेकिन नदी गंदी हुई — वो नुक़सान, कहीं नहीं गिना।"),
    (None, "[punch] यानी — जीडीपी ज़रूरी है, लेकिन पूरी {ख़ुशहाली|Welfare|❤️} की तस्वीर नहीं!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{फ़ाइनल बनाम इंटरमीडिएट|Final vs Intermediate|🍞}, {स्टॉक बनाम फ़्लो|Stock vs Flow|🪣}।"),
    (None, "{सर्कुलर फ़्लो|Circular Flow|🔁} — और तीन तरीक़े, एक जवाब।"),
    (None, "{जीडीपी से नेशनल इनकम|GDP → GNP → NNP → NI|👑}।"),
    (None, "{रियल जीडीपी|Real GDP|🔍}, और {जीडीपी की कमियाँ|GDP ≠ Welfare|❤️}।"),

    ("outro:Next: Ramesh Singh Chapter 2", "[scene] दोस्तों — एन सी ई आर टी ने हमें, नेशनल इनकम की नींव दे दी।"),
    (None, "[punch] अब रमेश सिंह के चैप्टर दो में — भारत की नेशनल इनकम, असल में कैसे गिनी जाती है — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
