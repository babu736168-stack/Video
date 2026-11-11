"""Econ05 - Production aur Cost. Course plan: Ramesh Singh Ch 1, NCERT foundation class 5.
Source: NCERT Class 12 Introductory Microeconomics, Chapter 3 "Production and Costs".
Facts used: production function q = f(L, K) = the maximum output from given inputs with a given technology; short
run: at least one input (e.g. capital) fixed; long run: all inputs variable; total product (TP), average product
(AP = TP / L), marginal product (MP = change in TP from one more unit of labour); law of diminishing marginal product
(law of variable proportions): with one input fixed, MP of the variable input first rises and then falls; returns to
scale (long run, all inputs raised in the same proportion): increasing (output rises by a larger proportion),
constant (same proportion), decreasing (smaller proportion). Costs: total fixed cost (does not change with output,
e.g. rent), total variable cost (changes with output, e.g. raw material, wages), TC = TFC + TVC; AFC = TFC/q falls
continuously as output rises; AVC, AC (= AFC + AVC) and MC (change in TC from one more unit) are U-shaped; MC cuts
AVC and AC at their minimum points. Long run: no fixed cost; LRAC and LRMC. The bakery is an illustration.
"""
CHAPTER = dict(num=5, title="Production aur Cost", kicker="ECONOMICS · CLASS 5 · NCERT CLASS 12 MICRO", rain="🍞",
               outro_icons=("🚜", "📦"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Supply — bechne wale ki kahani")

TOPICS = [
    dict(id="function", name="Production Function", label="Inputs in, output out", icon="⚙️"),
    dict(id="runs", name="Short Run vs Long Run", label="What can you change?", icon="⏱️"),
    dict(id="products", name="TP · AP · MP", label="Too many cooks", icon="👩‍🍳"),
    dict(id="scale", name="Returns to Scale", label="Double everything", icon="📐"),
    dict(id="costs", name="Costs", label="Fixed, variable, average, marginal", icon="💸"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक छोटी-सी {बेकरी|Bakery|🍞} सोचिए। एक {ओवन|Oven|🔥}, और एक {बेकर|Baker|👩‍🍳}।"),
    (None, "दूसरा बेकर रखा — तो ब्रेड दोगुनी से भी ज़्यादा! तीसरा रखा — और बढ़ी।"),
    (None, "लेकिन दसवाँ बेकर?"),
    (None, "[punch] अब सब एक-दूसरे से टकरा रहे हैं!"),
    (None, "[punch] ऐसा क्यों? यही है आज का सवाल!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {प्रोडक्शन फ़ंक्शन|Production Function|⚙️}, और शॉर्ट रन, लॉन्ग रन।"),
    (None, "दूसरा — {टी पी, ए पी, एम पी|TP · AP · MP|👩‍🍳} — और ज़्यादा लोग, कम फ़ायदा क्यों।"),
    (None, "तीसरा — सब कुछ दोगुना करें, तो क्या होता है — {रिटर्न्स टू स्केल|Returns to Scale|📐}।"),
    (None, "और चौथा — {लागत|Costs|💸} के सारे रूप।"),

    ("center", "[name] क्लास पाँच — प्रोडक्शन और कॉस्ट!"),
    ("topics", "चलिए — बेकरी के अंदर चलते हैं!"),

    ("focus:function", "[scene] ब्रेड बनाने के लिए चाहिए — {लेबर|Labour L|👩‍🍳}, और {कैपिटल|Capital K|🔥}, यानी ओवन जैसी मशीनें।"),
    (None, "[name] दिए गए साधनों और तकनीक से, ज़्यादा से ज़्यादा कितना बन सकता है — ये रिश्ता है — {प्रोडक्शन फ़ंक्शन|q = f(L, K)|⚙️}।"),

    ("focus:runs", "[scene] अब ज़रा सोचिए — कल से ज़्यादा ब्रेड चाहिए। नया बेकर? आज ही रख लो। लेकिन नया ओवन, नई दुकान? उसमें वक़्त लगेगा।"),
    (None, "[name] जब कम से कम एक साधन {फ़िक्स्ड|Fixed|🔒} हो — वो है {शॉर्ट रन|Short Run|⏱️}।"),
    (None, "और जब सारे साधन बदले जा सकें — वो है {लॉन्ग रन|Long Run|📅}।"),

    ("focus:products", "[scene] शॉर्ट रन में, ओवन एक ही है। बस बेकर बढ़ाते जाइए।"),
    (None, "कुल जितनी ब्रेड बनी — वो है {टोटल प्रोडक्ट|Total Product|🍞}।"),
    (None, "हर बेकर के हिस्से, औसतन कितनी — {एवरेज प्रोडक्ट|Average Product = TP / L|➗}।"),
    (None, "और एक नया बेकर जुड़ने से, कितनी ज़्यादा बनी — {मार्जिनल प्रोडक्ट|Marginal Product|➕}।"),
    (None, "[scene] शुरू में — नया बेकर, ज़्यादा फ़ायदा। काम बँट गया, रफ़्तार बढ़ी। मार्जिनल प्रोडक्ट {बढ़ा|MP ↑|📈}।"),
    (None, "लेकिन ओवन तो एक ही है! धीरे-धीरे हर नए बेकर से, फ़ायदा घटने लगा। मार्जिनल प्रोडक्ट {घटा|MP ↓|📉}।"),
    (None, "[name] इसे कहते हैं — {लॉ ऑफ़ डिमिनिशिंग मार्जिनल प्रोडक्ट|Diminishing MP|⬇️}। यानी — लॉ ऑफ़ वेरिएबल प्रोपोर्शन्स।"),
    ("ex:", "वही पुरानी कहावत — {ज़्यादा जोगी, मठ उजाड़|Too many cooks|🙃}!"),

    ("focus:scale", "[scene] अब लॉन्ग रन। सब कुछ बदल सकते हैं। तो चलिए — बेकर भी दोगुने, ओवन भी दोगुने!"),
    (None, "अगर ब्रेड {दोगुनी से ज़्यादा|IRS|🚀} हो गई — तो ये है इंक्रीज़िंग रिटर्न्स टू स्केल।"),
    (None, "ठीक {दोगुनी|CRS|⚖️} — तो कॉन्स्टेंट रिटर्न्स टू स्केल।"),
    (None, "और {दोगुनी से कम|DRS|🐢} — तो डिक्रीज़िंग रिटर्न्स टू स्केल।"),
    (None, "[punch] याद रखिए — रिटर्न्स टू स्केल, सिर्फ़ {लॉन्ग रन|Long Run only|📅} की बात है।"),

    ("focus:costs", "[scene] अब पैसे की बात — लागत!"),
    (None, "दुकान का {किराया|Rent|🏠} — ब्रेड बने या न बने, देना ही है। ये है {टोटल फ़िक्स्ड कॉस्ट|TFC|🔒}।"),
    (None, "{आटा, बिजली, बेकर की तनख़्वाह|Raw material · Wages|🌾} — ब्रेड जितनी ज़्यादा, ये उतना ज़्यादा। ये है {टोटल वेरिएबल कॉस्ट|TVC|🔄}।"),
    (None, "[name] और दोनों मिलाकर — {टोटल कॉस्ट|TC = TFC + TVC|💸}।"),
    (None, "अब एक ब्रेड पर — औसत लागत। किराया जितनी ज़्यादा ब्रेड पर बँटे, उतना कम — इसलिए {एवरेज फ़िक्स्ड कॉस्ट|AFC ↓ always|📉}, लगातार गिरती है।"),
    (None, "{एवरेज वेरिएबल कॉस्ट|AVC|🔄}, और {एवरेज कॉस्ट|AC = AFC + AVC|➗} — पहले गिरती हैं, फिर बढ़ती हैं। यानी अंग्रेज़ी के {यू|U-shape|🅤} जैसी।"),
    (None, "और एक और ब्रेड बनाने से, जितनी लागत बढ़ी — {मार्जिनल कॉस्ट|Marginal Cost|➕}। ये भी यू जैसी।"),
    (None, "[punch] और एक ख़ास बात — मार्जिनल कॉस्ट की कर्व, एवरेज कॉस्ट को — ठीक उसके {सबसे निचले बिंदु|MC cuts AC at minimum|🎯} पर काटती है!"),
    (None, "लॉन्ग रन में कोई लागत फ़िक्स्ड नहीं — तो वहाँ बस {एल आर ए सी|LRAC · LRMC|📅}, और एल आर एम सी।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{प्रोडक्शन फ़ंक्शन|q = f(L, K)|⚙️}, और {शॉर्ट रन, लॉन्ग रन|Short vs Long Run|⏱️}।"),
    (None, "{डिमिनिशिंग मार्जिनल प्रोडक्ट|Diminishing MP|⬇️} — ज़्यादा जोगी, मठ उजाड़।"),
    (None, "{रिटर्न्स टू स्केल|IRS · CRS · DRS|📐} — सब कुछ दोगुना करें, तो?"),
    (None, "{लागत|TFC · TVC · AC · MC|💸} — और एम सी, ए सी को, उसके सबसे निचले बिंदु पर काटती है।"),

    ("outro:Next: Supply", "[scene] अब बेकर जानता है — लागत कितनी है। लेकिन दोस्तों — वो कितनी ब्रेड बेचे, कि मुनाफ़ा सबसे ज़्यादा हो?"),
    (None, "[punch] सप्लाई की कहानी — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
