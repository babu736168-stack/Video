"""Econ10 - Poore Desh ki Economy (Introduction to Macroeconomics). Course plan: Ramesh Singh Ch 2, NCERT class 10.
Source: NCERT Class 12 Introductory Macroeconomics, Chapter 1 "Introduction".
Facts used: macroeconomics studies the economy as a whole: aggregate output, employment, the general price level,
interest rate; microeconomics studies individual markets. Before the 1930s economists generally believed markets
would keep everyone employed; the Great Depression began in 1929; in the USA unemployment rose from about 3 per cent
to about 25 per cent between 1929 and 1933; J. M. Keynes's "The General Theory of Employment, Interest and Money"
(1936) founded modern macroeconomics. A capitalist economy: means of production privately owned, production for sale
in the market, labour bought and sold at a wage rate; entrepreneurs organise production. Four sectors (major
decision-makers): households, firms, the government, and the external sector (rest of the world).
"""
CHAPTER = dict(num=10, title="Poore Desh ki Economy", kicker="ECONOMICS · CLASS 10 · NCERT CLASS 12 MACRO", rain="🌏",
               outro_icons=("💹", "🧮"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: GDP aur National Income")

TOPICS = [
    dict(id="micromacro", name="Micro vs Macro", label="The tree and the forest", icon="🌳"),
    dict(id="birth", name="Birth of Macro", label="1929 to 1936", icon="📉"),
    dict(id="capitalist", name="A Capitalist Economy", label="Owners, workers, markets", icon="🏭"),
    dict(id="sectors", name="Four Players", label="Households · Firms · Govt · World", icon="👥"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक {पेड़|Ek ped|🌳} देखिए। उसकी पत्तियाँ, उसकी शाखाएँ।"),
    (None, "और अब ऊपर उड़िए — {पूरा जंगल|Poora jungle|🌲} देखिए।"),
    (None, "[punch] इकॉनॉमिक्स में भी, यही दो नज़रें हैं!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {माइक्रो और मैक्रो|Micro vs Macro|🌳} का असली फ़र्क़।"),
    (None, "दूसरा — {मैक्रोइकॉनॉमिक्स का जन्म|1929 → 1936|📉}, एक बड़े संकट से।"),
    (None, "तीसरा — {कैपिटलिस्ट इकॉनमी|Capitalist Economy|🏭} कैसे चलती है।"),
    (None, "और चौथा — इकॉनमी के {चार खिलाड़ी|4 Sectors|👥}।"),

    ("center", "[name] क्लास दस — पूरे देश की इकॉनमी!"),
    ("topics", "चलिए — पेड़ से जंगल की ओर!"),

    ("focus:micromacro", "[scene] {माइक्रोइकॉनॉमिक्स|Microeconomics|🔬} — एक पेड़। यानी एक ग्राहक, एक फ़र्म, एक बाज़ार। जैसे — आलू का दाम।"),
    (None, "[name] {मैक्रोइकॉनॉमिक्स|Macroeconomics|🌏} — पूरा जंगल। पूरे देश का {कुल उत्पादन|Aggregate output|🏭}, {कुल रोज़गार|Employment|👷}, सारे {दामों का स्तर|Price level|🏷️}, और {ब्याज दर|Interest rate|🏦}।"),
    ("ex:", "आलू कितने का बिका — ये माइक्रो। और {महँगाई|Inflation|🔥} पूरे देश में कितनी बढ़ी — ये मैक्रो!"),

    ("focus:birth", "[scene] उन्नीस सौ तीस से पहले, ज़्यादातर अर्थशास्त्री मानते थे — बाज़ार अपने आप, सबको काम दे देगा।"),
    (None, "[punch] फिर आया — {उन्नीस सौ उनतीस|1929|📉}। {ग्रेट डिप्रेशन|Great Depression|🏚️}!"),
    (None, "अमेरिका में, उन्नीस सौ उनतीस से तैंतीस के बीच — बेरोज़गारी, क़रीब {तीन प्रतिशत से पच्चीस प्रतिशत|3% → 25%|📈} तक पहुँच गई!"),
    (None, "कारख़ाने बंद, माल बिका नहीं, लोग बेकार। और बाज़ार — अपने आप, कुछ नहीं कर पाया।"),
    (None, "[scene] तब, {उन्नीस सौ छत्तीस|1936|📖} में — {जॉन मेनार्ड कीन्स|J. M. Keynes|🎩} ने लिखी एक किताब — द जनरल थ्योरी ऑफ़ एम्प्लॉयमेंट, इंटरेस्ट एंड मनी।"),
    (None, "[name] उन्होंने पूरी इकॉनमी को, एक साथ देखा। और यहीं से जन्म हुआ — आज की {मैक्रोइकॉनॉमिक्स|Macroeconomics born|🌱} का।"),

    ("focus:capitalist", "[scene] अब एक {कैपिटलिस्ट इकॉनमी|Capitalist Economy|🏭} को पहचानिए — तीन निशान।"),
    (None, "पहला — कारख़ाने, मशीनें, ज़मीन — यानी उत्पादन के साधन — {निजी मालिकों|Private ownership|🔑} के हाथ में।"),
    (None, "दूसरा — चीज़ें बनती हैं, {बाज़ार में बेचने|Production for market|🏪} के लिए।"),
    (None, "तीसरा — लोग अपनी मेहनत बेचते हैं — {मज़दूरी|Wage rate|💵} के बदले।"),
    (None, "और इन सबको जोड़कर, कारोबार खड़ा करता है — {आंत्रप्रेन्योर|Entrepreneur|🚀}, यानी उद्यमी।"),

    ("focus:sectors", "[scene] अब इकॉनमी के, चार बड़े खिलाड़ी।"),
    (None, "पहला — {हाउसहोल्ड्स|Households|🏠}, यानी परिवार। ये मेहनत देते हैं, और चीज़ें ख़रीदते हैं।"),
    (None, "दूसरा — {फ़र्म्स|Firms|🏭}, यानी कंपनियाँ। ये चीज़ें बनाती हैं।"),
    (None, "तीसरा — {सरकार|Government|🏛️}। टैक्स लेती है, ख़र्च करती है, नियम बनाती है।"),
    (None, "और चौथा — {बाहरी दुनिया|External sector|🌍}। यानी दूसरे देश — जिनके साथ हम, माल ख़रीदते और बेचते हैं।"),
    (None, "[punch] इन चारों के बीच, पैसा और सामान — गोल-गोल घूमता है। इसकी पूरी कहानी — अगली क्लास में!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{माइक्रो|Micro = ek ped|🔬} — एक पेड़। {मैक्रो|Macro = poora jungle|🌏} — पूरा जंगल।"),
    (None, "{ग्रेट डिप्रेशन|1929|📉}, और {कीन्स|Keynes, 1936|🎩}।"),
    (None, "{कैपिटलिस्ट इकॉनमी|Private · Market · Wages|🏭} — तीन निशान।"),
    (None, "{चार सेक्टर|Households · Firms · Govt · World|👥}।"),

    ("outro:Next: GDP", "[scene] दोस्तों — पूरे देश ने, एक साल में, कितना कमाया? ये गिनें कैसे?"),
    (None, "[punch] जीडीपी, और नेशनल इनकम — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
