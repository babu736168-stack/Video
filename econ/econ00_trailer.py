"""Econ00 - Course Trailer: the whole Economics course (basic to advanced) in about 2 minutes.
Plan: COURSE_PLAN.md. Sources of the course: NCERT Class 9-12 and Ramesh Singh, Indian Economy.
Markup: {spoken words|Screen label|emoji} pops the label when spoken; see polity/voice.py.
"""
CHAPTER = dict(num=0, title="Economics", kicker="COURSE · ZERO TO ADVANCED", rain="💰",
               recap_title="VAADA", outro_icons=("🏡", "🌾"))

TOPICS = [
    dict(id="l1", name="Basics", label="Start from zero", icon="🌱"),
    dict(id="l2", name="Microeconomics", label="One buyer, one seller", icon="🔍"),
    dict(id="l3", name="Macroeconomics", label="The whole country", icon="🌏"),
    dict(id="l4", name="India's Story", label="1947 to today", icon="🇮🇳"),
    dict(id="l5", name="Advanced", label="Ramesh Singh level", icon="🎓"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक सवाल — {टमाटर|Tamatar|🍅} कभी बीस रुपये किलो, और कभी दो सौ रुपये किलो! ऐसा क्यों?"),
    (None, "{पेट्रोल|Petrol|⛽} का दाम — आख़िर कौन तय करता है?"),
    (None, "और {बैंक|Bank|🏦} में रखा आपका पैसा — बैंक उसका करता क्या है?"),
    (None, "[punch] इन सब सवालों का जवाब, एक ही जगह छुपा है!"),
    ("center", "[name] इकॉनमी! यानी — पैसा, काम, और चीज़ों का पूरा खेल।"),
    ("topics", "और इस कोर्स में, हम इसे बिल्कुल ज़ीरो से शुरू करेंगे — और ले जाएँगे एडवांस्ड लेवल तक। पाँच सीढ़ियों में!"),

    ("focus:l1", "[scene] पहली सीढ़ी — {बेसिक्स|Basics|🌱}।"),
    (None, "शुरुआत होगी एक {गाँव|Gaon|🏡} की कहानी से — {खेत|Khet|🌾}, {मज़दूर|Mazdoor|👷}, {पैसा और कर्ज़|Paisa aur Karz|💰}, और {गरीबी|Garibi|🏚️}।"),
    (None, "सब कुछ — {एन सी ई आर टी|NCERT Class 9 & 10|📗} की, क्लास नौ और दस की किताबों से।"),

    ("focus:l2", "[scene] दूसरी सीढ़ी — {माइक्रोइकॉनॉमिक्स|Microeconomics|🔍}।"),
    (None, "एक {ग्राहक|Grahak|🧍}, एक {दुकानदार|Dukaandaar|🏪} — और बीच में {डिमांड|Demand|🛒}, {सप्लाई|Supply|🚜}, और {दाम|Daam|🏷️} का खेल।"),

    ("focus:l3", "[scene] तीसरी सीढ़ी — {मैक्रोइकॉनॉमिक्स|Macroeconomics|🌏}। अब पूरा देश!"),
    (None, "{जीडीपी|GDP|📈}, {आर बी आई|RBI|🏦}, और सरकार का {बजट|Budget|🧾}।"),

    ("focus:l4", "[scene] चौथी सीढ़ी — {भारत की कहानी|Bharat ki Kahani|🇮🇳}।"),
    (None, "{उन्नीस सौ सैंतालीस|1947|🕊️} की आज़ादी से, {उन्नीस सौ इक्यानवे|1991|🔓} के सुधारों तक — और फिर, {आज का भारत|Aaj ka Bharat|🚀}।"),

    ("focus:l5", "[scene] और पाँचवीं सीढ़ी — {एडवांस्ड इंडियन इकॉनमी|Advanced Indian Economy|🎓}, {रमेश सिंह|Ramesh Singh|📘} की किताब के साथ।"),
    (None, "{महँगाई|Mehngai|🔥}, {बैंकिंग|Banking|💳}, {टैक्स|Tax|🧮}, {शेयर बाज़ार|Share Bazaar|📊} — सब कुछ!"),

    ("recap", "[scene] और मेरा वादा — {कोई रटना नहीं|Koi ratna nahi|🙅}।"),
    (None, "हर बात — एक {कहानी|Kahani|📖}। और हर कहानी के साथ — एक {मिसाल|Misaal|💡}।"),
    (None, "कोर्स के अंत में — {बजट|Budget ki khabar|🧾} की ख़बर हो, या महँगाई की — {आप ख़ुद समझेंगे|Aap khud samjhenge|💪}!"),
    ("outro:Pehli class — Ek Gaon ki Kahani", "[punch] तो चलिए, शुरू करते हैं — पहली क्लास, एक गाँव की कहानी से!"),
]
