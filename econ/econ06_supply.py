"""Econ06 - Supply: Bechne Wale ki Kahani. Course plan: Ramesh Singh Ch 1, NCERT foundation class 6.
Source: NCERT Class 12 Introductory Microeconomics, Chapter 4 "The Theory of the Firm under Perfect Competition".
Facts used: perfect competition: many buyers and sellers, identical (homogeneous) product, free entry and exit,
perfect information; each firm is a price-taker. Total revenue TR = p x q; average revenue AR = p; marginal revenue
MR = p. Profit = TR - TC. Profit maximisation (price-taking firm): p = MC, MC not falling at that output; in the short
run the firm produces only if p >= minimum AVC (shut-down point); in the long run only if p >= minimum AC; normal
profit = minimum profit to stay in business (counted in cost), super-normal profit above it; break-even point =
minimum AC (only normal profit). Short-run supply curve of a firm = rising part of SMC above minimum AVC; long-run
supply = rising part of LRMC above minimum LRAC. Supply curve shifts with technological progress (right), input
prices (rise -> left) and a unit tax (left). Market supply = sum of all firms' supply at each price. Price elasticity
of supply = % change in quantity supplied / % change in price. The 2023 tomato supply shock (crop damage) is from
the approved Demand & Supply sample.
"""
CHAPTER = dict(num=6, title="Supply", kicker="ECONOMICS · CLASS 6 · NCERT CLASS 12 MICRO", rain="🚜",
               outro_icons=("⚖️", "🤝"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Daam kaise tay hota hai?")

TOPICS = [
    dict(id="perfect", name="Perfect Competition", label="Many sellers, same product", icon="🥔"),
    dict(id="revenue", name="Revenue", label="TR · AR · MR", icon="💰"),
    dict(id="profit", name="Best Output", label="Price = MC", icon="🎯"),
    dict(id="curve", name="Supply Curve", label="The seller's side", icon="📈"),
    dict(id="shifts", name="Supply Shifts", label="When the curve moves", icon="🌧️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, सब्ज़ी मंडी में चलिए। सौ दुकानें — और सब पर, एक जैसे {आलू|Aloo|🥔}।"),
    (None, "अब एक दुकानदार कहता है — मेरे आलू, बाक़ी सबसे महँगे!"),
    (None, "[punch] क्या होगा? एक भी ग्राहक नहीं आएगा!"),
    (None, "[punch] तो फिर बेचने वाला, कितना बेचे — और किस दाम पर? यही है आज का सवाल!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {परफ़ेक्ट कॉम्पिटिशन|Perfect Competition|🥔} क्या है।"),
    (None, "दूसरा — बेचने वाले की {कमाई|TR · AR · MR|💰}।"),
    (None, "तीसरा — सबसे ज़्यादा मुनाफ़ा कहाँ — {दाम बराबर एम सी|Price = MC|🎯}।"),
    (None, "और चौथा — {सप्लाई कर्व|Supply Curve & Shifts|📈}, और वो कब खिसकती है।"),

    ("center", "[name] क्लास छह — सप्लाई!"),
    ("topics", "चलिए — मंडी के नियम समझते हैं!"),

    ("focus:perfect", "[scene] परफ़ेक्ट कॉम्पिटिशन में — {बहुत सारे ख़रीदार|Many buyers|👥}, और {बहुत सारे बेचने वाले|Many sellers|🏪}।"),
    (None, "सबका माल {एक जैसा|Same product|🥔}। कोई भी आ सकता है, कोई भी जा सकता है — {फ़्री एंट्री और एग्ज़िट|Free entry & exit|🚪}। और सबको, सारी {जानकारी|Perfect information|📢}।"),
    (None, "[name] इसलिए कोई अकेला दुकानदार, दाम तय नहीं कर सकता। दाम बाज़ार तय करता है — दुकानदार बस मानता है। वो है — {प्राइस टेकर|Price-taker|🏷️}।"),

    ("focus:revenue", "[scene] दुकानदार ने बेचे — क्यू किलो आलू, पी रुपये किलो।"),
    (None, "[name] कुल कमाई — {टोटल रेवेन्यू|TR = p × q|💰}।"),
    (None, "एक किलो पर औसत कमाई — {एवरेज रेवेन्यू|AR = p|➗}। और एक किलो और बेचने से, जितनी कमाई बढ़ी — {मार्जिनल रेवेन्यू|MR = p|➕}।"),
    (None, "[punch] प्राइस टेकर के लिए — एवरेज रेवेन्यू, मार्जिनल रेवेन्यू, और दाम — {तीनों बराबर|AR = MR = p|⚖️}!"),
    (None, "और मुनाफ़ा? {कमाई घटा लागत|Profit = TR − TC|📊}।"),

    ("focus:profit", "[scene] अब दुकानदार सोचता है — एक किलो और बेचूँ, या नहीं?"),
    (None, "अगर एक किलो और से, कमाई बढ़ी पी — और लागत बढ़ी, उससे कम — तो बेचो! मुनाफ़ा बढ़ेगा।"),
    (None, "[name] वो तब तक बढ़ाता है, जब तक — {दाम बराबर मार्जिनल कॉस्ट|p = MC|🎯}। और वहाँ एम सी, गिर नहीं रही हो।"),
    (None, "[scene] लेकिन अगर दाम, {एवरेज वेरिएबल कॉस्ट|p < min AVC|🚫} के सबसे निचले बिंदु से भी नीचे आ जाए? तो शॉर्ट रन में भी — दुकान बंद करना बेहतर। इसे कहते हैं — {शट-डाउन पॉइंट|Shut-down point|🔒}।"),
    (None, "और लॉन्ग रन में, दाम कम से कम — {एवरेज कॉस्ट|p ≥ min AC|📅} के सबसे निचले बिंदु जितना होना चाहिए।"),
    (None, "जहाँ दाम, ठीक सबसे कम एवरेज कॉस्ट के बराबर हो — वहाँ मिलता है बस {नॉर्मल प्रॉफ़िट|Normal profit|🙂} — यानी धंधे में टिके रहने लायक़। इसे कहते हैं — {ब्रेक-ईवन पॉइंट|Break-even point|⚖️}।"),
    (None, "उससे ऊपर जो मिले — वो है {सुपर-नॉर्मल प्रॉफ़िट|Super-normal profit|🤑}।"),

    ("focus:curve", "[scene] अब हर दाम पर, दुकानदार कितना बेचेगा — इसे जोड़ें, तो मिलती है — सप्लाई कर्व।"),
    ("anim:supply_curve", "दाम बढ़ा — तो बेचने वाले, {ज़्यादा बेचना|Daam ↑ Supply ↑|📈} चाहते हैं। इसलिए सप्लाई कर्व — ऊपर चढ़ती है!"),
    (None, "[name] असल में, एक फ़र्म की शॉर्ट रन सप्लाई कर्व — उसकी {मार्जिनल कॉस्ट कर्व|SMC above min AVC|📈} का, वो चढ़ता हुआ हिस्सा है — जो सबसे कम ए वी सी से ऊपर हो।"),
    (None, "और सारी फ़र्मों की सप्लाई जोड़ दें — तो मिलती है {मार्केट सप्लाई|Market Supply|🏪}।"),
    (None, "दाम में बदलाव पर, सप्लाई कितनी बदली — इसे नापती है — {प्राइस इलास्टिसिटी ऑफ़ सप्लाई|Elasticity of Supply|🧂}।"),

    ("focus:shifts", "[scene] और कब पूरी सप्लाई कर्व खिसक जाती है?"),
    (None, "{नई तकनीक|Technology ↑|🤖} — कम लागत में ज़्यादा माल। कर्व दाईं ओर।"),
    (None, "{कच्चा माल महँगा|Input price ↑|⛽}, या सरकार ने हर यूनिट पर {टैक्स|Unit tax|🧾} लगाया — कर्व बाईं ओर।"),
    ("anim:tomato_up", "[scene] याद है टमाटर? दो हज़ार तेईस में, {फ़सल ख़राब|Crop damage|🌧️} हुई — सप्लाई बाईं ओर खिसकी — और दाम आसमान पर!"),
    (None, "[punch] यानी दाम में खेल — डिमांड और सप्लाई, दोनों मिलकर खेलते हैं!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{परफ़ेक्ट कॉम्पिटिशन|Price-taker|🥔} — दाम बाज़ार तय करता है।"),
    (None, "{ए आर बराबर एम आर बराबर पी|AR = MR = p|⚖️}।"),
    (None, "{दाम बराबर एम सी|p = MC|🎯} — सबसे ज़्यादा मुनाफ़ा। और {शट-डाउन, ब्रेक-ईवन|Shut-down · Break-even|🔒}।"),
    (None, "{सप्लाई कर्व|Supply Curve ↗|📈} ऊपर चढ़ती है — और तकनीक, लागत, टैक्स से खिसकती है।"),

    ("outro:Next: Daam kaise tay hota hai?", "[scene] अब हमारे पास डिमांड भी है, और सप्लाई भी। लेकिन दोस्तों — दोनों मिलें कहाँ? असली दाम, तय कैसे हो?"),
    (None, "[punch] मार्केट इक्विलिब्रियम — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
