"""Econ08 - Monopoly aur Doosre Bazaar. Course plan: Ramesh Singh Ch 1, NCERT foundation class 8.
Source: NCERT Class 12 Introductory Microeconomics, "Non-competitive Markets" (older editions; the rationalised
edition may not include it: check your copy).
Facts used: monopoly = a single seller of a good with no close substitute, entry of other firms blocked (barriers,
e.g. licence, patent, control of a resource); the monopolist faces the downward-sloping market demand curve, so to
sell more it must lower the price: MR is less than AR (price); profit is maximised where MR = MC; it can keep
super-normal profit in the long run because entry is blocked. Monopolistic competition: many firms, differentiated
products (brands of soap, toothpaste), free entry and exit, so super-normal profits are competed away in the long
run; each firm has some control over its price. Oligopoly: a few large firms, each must consider the others'
reactions (interdependence); duopoly = two firms. Brand and product names below are everyday illustrations.
"""
CHAPTER = dict(num=8, title="Monopoly aur Doosre Bazaar", kicker="ECONOMICS · CLASS 8 · NCERT CLASS 12 MICRO", rain="👑",
               outro_icons=("📘", "🌏"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Ramesh Singh Chapter 1 — gehraai mein")

TOPICS = [
    dict(id="mono", name="Monopoly", label="One seller, no substitute", icon="👑"),
    dict(id="mrmc", name="Monopoly's Choice", label="MR = MC", icon="🎯"),
    dict(id="moncomp", name="Monopolistic Competition", label="Many brands, small differences", icon="🧼"),
    dict(id="oligo", name="Oligopoly", label="A few giants watching each other", icon="♟️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, सोचिए — पूरे शहर में, सिर्फ़ {एक ही दुकान|Ek hi dukaan|🏪}। और कोई दूसरी, खुल भी नहीं सकती।"),
    (None, "[punch] क्या वो दुकानदार, जो चाहे वो दाम ले सकता है?"),
    (None, "जवाब — {हाँ भी, और नहीं भी|Haan bhi, nahi bhi|🤔}! चलिए समझते हैं।"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {मोनोपॉली|Monopoly|👑} क्या है।"),
    (None, "दूसरा — मोनोपॉली अपना {मुनाफ़ा|MR = MC|🎯} कैसे तय करती है।"),
    (None, "तीसरा — {मोनोपॉलिस्टिक कॉम्पिटिशन|Monopolistic Competition|🧼}, यानी ब्रांड्स का खेल।"),
    (None, "और चौथा — {ऑलिगोपॉली|Oligopoly|♟️}, जहाँ कुछ बड़े खिलाड़ी, एक-दूसरे पर नज़र रखते हैं।"),

    ("center", "[name] क्लास आठ — मोनोपॉली और दूसरे बाज़ार!"),
    ("topics", "चलिए — शुरू करते हैं, अकेले राजा से!"),

    ("focus:mono", "[scene] {मोनोपॉली|Monopoly|👑} — यानी बाज़ार में, {सिर्फ़ एक बेचने वाला|Single seller|1️⃣}।"),
    (None, "उसकी चीज़ का कोई {पास का विकल्प नहीं|No close substitute|🚫}। और नए बेचने वाले, अंदर {आ नहीं सकते|Entry blocked|🚧}।"),
    (None, "रुकावट कई तरह की — सरकार का {लाइसेंस|Licence|📜}, {पेटेंट|Patent|💡}, या किसी ज़रूरी कच्चे माल पर, उसका क़ब्ज़ा।"),

    ("focus:mrmc", "[scene] अब याद कीजिए — परफ़ेक्ट कॉम्पिटिशन में, दुकानदार बस दाम मानता था।"),
    (None, "लेकिन मोनोपॉली के सामने — पूरे बाज़ार की {डिमांड कर्व|Demand curve ↘|📉} है।"),
    (None, "[punch] ज़्यादा बेचना है? तो {दाम घटाना|Lower price to sell more|🏷️} पड़ेगा — और वो भी, सारे ग्राहकों के लिए!"),
    (None, "[name] इसलिए हर अगली यूनिट से, कमाई उतनी नहीं बढ़ती, जितना दाम है। यानी — {मार्जिनल रेवेन्यू, दाम से कम|MR < AR|⬇️}।"),
    (None, "और मुनाफ़ा सबसे ज़्यादा — जहाँ {एम आर बराबर एम सी|MR = MC|🎯}।"),
    (None, "[punch] और क्योंकि कोई नया आ नहीं सकता — लॉन्ग रन में भी, मोनोपॉली {सुपर-नॉर्मल प्रॉफ़िट|Super-normal profit|🤑} कमा सकती है।"),
    ("ex:", "तो जवाब — दाम ऊँचा रख सकती है, {हाँ|Haan|✅}। लेकिन जितना चाहे उतना? {नहीं|Nahi|❌} — क्योंकि दाम बढ़ा, तो ख़रीदार घटेंगे।"),

    ("focus:moncomp", "[scene] अब सुपरमार्केट में चलिए। {साबुन|Saabun|🧼} के बीसों ब्रांड! {टूथपेस्ट|Toothpaste|🪥} के बीसों ब्रांड!"),
    (None, "[name] बहुत सारी कंपनियाँ, लेकिन सबका माल {थोड़ा अलग|Differentiated products|🎨} — ख़ुशबू, रंग, पैकिंग, नाम। ये है — {मोनोपॉलिस्टिक कॉम्पिटिशन|Monopolistic Competition|🧼}।"),
    (None, "हर कंपनी का, अपने ब्रांड पर, थोड़ा-सा {दाम का कंट्रोल|Some price control|🏷️}।"),
    (None, "[punch] लेकिन {नई कंपनियाँ आ सकती हैं|Free entry|🚪} — इसलिए लॉन्ग रन में, सुपर-नॉर्मल प्रॉफ़िट, ख़त्म हो जाता है।"),

    ("focus:oligo", "[scene] और आख़िर में — जहाँ बाज़ार में, बस {कुछ बड़ी कंपनियाँ|A few big firms|🏢} हों।"),
    (None, "[name] ये है — {ऑलिगोपॉली|Oligopoly|♟️}। और अगर सिर्फ़ दो हों — तो {ड्यूओपॉली|Duopoly|2️⃣}।"),
    (None, "यहाँ हर कंपनी, कोई भी क़दम उठाने से पहले सोचती है — {दूसरी क्या करेगी|Interdependence|👀}?"),
    ("ex:", "जैसे शतरंज — एक ने दाम घटाया, तो दूसरी भी घटाएगी? या नया ऑफ़र लाएगी?"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{मोनोपॉली|Monopoly|👑} — एक बेचने वाला, कोई विकल्प नहीं, एंट्री बंद।"),
    (None, "{एम आर, दाम से कम|MR < AR|⬇️} — और मुनाफ़ा, {एम आर बराबर एम सी|MR = MC|🎯} पर।"),
    (None, "{मोनोपॉलिस्टिक कॉम्पिटिशन|Many brands|🧼} — थोड़ा अलग माल, फ़्री एंट्री।"),
    (None, "{ऑलिगोपॉली|Oligopoly|♟️} — कुछ बड़े खिलाड़ी, एक-दूसरे पर नज़र।"),

    ("outro:Next: Ramesh Singh Chapter 1", "[scene] दोस्तों — एन सी ई आर टी की नींव, अब पक्की हो गई! गाँव, सेक्टर, डिमांड, सप्लाई, और बाज़ार।"),
    (None, "[punch] अब बारी है — रमेश सिंह के चैप्टर एक की, पूरी गहराई की! अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
