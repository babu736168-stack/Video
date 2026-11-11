"""Econ07 - Daam Kaise Tay Hota Hai? (Market Equilibrium). Course plan: Ramesh Singh Ch 1, NCERT foundation class 7.
Source: NCERT Class 12 Introductory Microeconomics, Chapter 5 "Market Equilibrium".
Facts used: equilibrium = market demand equals market supply; equilibrium price and quantity; above it excess
supply (surplus) pushes the price down, below it excess demand (shortage) pushes the price up; Adam Smith's
"invisible hand" (prices adjust by themselves). Shifts: demand rises -> price and quantity rise; supply falls ->
price rises, quantity falls (2023 tomato example from the approved sample). Price ceiling = maximum price set by the
government below the equilibrium price (essential goods such as wheat, rice, kerosene, sugar through ration shops):
excess demand, rationing, ration cards, long queues, black market. Price floor = minimum price set above equilibrium
(minimum support price for some crops, minimum wage): excess supply; the government buys the surplus (crops).
"""
CHAPTER = dict(num=7, title="Daam Kaise Tay Hota Hai?", kicker="ECONOMICS · CLASS 7 · NCERT CLASS 12 MICRO", rain="⚖️",
               outro_icons=("👑", "🏪"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Monopoly aur doosre bazaar")

TOPICS = [
    dict(id="eq", name="Equilibrium", label="Where both shake hands", icon="🤝"),
    dict(id="gaps", name="Surplus & Shortage", label="The invisible hand", icon="🫳"),
    dict(id="shifts", name="When Curves Move", label="New price, new deal", icon="🔄"),
    dict(id="ceiling", name="Price Ceiling", label="Government caps the price", icon="⬇️"),
    dict(id="floor", name="Price Floor", label="Government sets a minimum", icon="⬆️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, मंडी में एक {ख़रीदार|Khareedaar|🧍} कहता है — दाम कम करो! और {बेचने वाला|Bechne wala|🧑‍🌾} कहता है — दाम बढ़ाओ!"),
    (None, "दोनों खींच रहे हैं, अलग-अलग दिशा में।"),
    (None, "[punch] फिर भी — हर शाम, सौदा हो जाता है! कैसे?"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {इक्विलिब्रियम|Equilibrium|🤝}, जहाँ दोनों हाथ मिलाते हैं।"),
    (None, "दूसरा — {सरप्लस और शॉर्टेज|Surplus & Shortage|🫳}, और बाज़ार का अदृश्य हाथ।"),
    (None, "तीसरा — कर्व खिसकीं, तो {नया दाम|New price|🔄} कैसे बनता है।"),
    (None, "और चौथा — जब सरकार दाम पर, {छत या फ़र्श|Ceiling & Floor|🏛️} लगाती है।"),

    ("center", "[name] क्लास सात — दाम कैसे तय होता है?"),
    ("topics", "चलिए — डिमांड और सप्लाई को, आमने-सामने लाते हैं!"),

    ("focus:eq", "[scene] एक तरफ़ — {डिमांड कर्व|Demand ↘|🛒}, नीचे उतरती हुई। दूसरी तरफ़ — {सप्लाई कर्व|Supply ↗|🚜}, ऊपर चढ़ती हुई।"),
    ("anim:equilibrium", "और जहाँ दोनों कटती हैं — वहाँ जितना लोग ख़रीदना चाहते हैं, ठीक उतना ही, बेचने वाले बेचना चाहते हैं।"),
    (None, "[name] यही है — {मार्केट इक्विलिब्रियम|Equilibrium: D = S|🤝}। और वहाँ का दाम — {इक्विलिब्रियम प्राइस|Equilibrium Price|🏷️}।"),

    ("focus:gaps", "[scene] अब मान लीजिए, दाम इक्विलिब्रियम से {ऊपर|Daam zyada|⬆️} है।"),
    ("anim:surplus", "बेचने वाले, ढेर सारा माल ले आए — लेकिन ख़रीदार कम! माल बचा पड़ा है — ये है {सरप्लस|Excess Supply|📦}।"),
    (None, "[punch] तो क्या करेंगे? दाम घटाएँगे! और दाम नीचे आता है — इक्विलिब्रियम की ओर।"),
    ("anim:shortage", "[scene] और अगर दाम {नीचे|Daam kam|⬇️} है? सब ख़रीदना चाहते हैं — माल कम! ये है {शॉर्टेज|Excess Demand|🧍}।"),
    (None, "ख़रीदार ज़्यादा दाम देने को तैयार — और दाम ऊपर जाता है, इक्विलिब्रियम की ओर।"),
    (None, "[name] बिना किसी के कहे, दाम ख़ुद सही जगह पहुँच जाता है। एडम स्मिथ ने इसे कहा — {इनविज़िबल हैंड|Invisible Hand|🫳}, यानी अदृश्य हाथ।"),

    ("focus:shifts", "[scene] अब कर्व खिसकाइए। गर्मी आई — कुल्फ़ी की {डिमांड बढ़ी|Demand ↑|🍦}।"),
    ("anim:shift_right", "डिमांड कर्व दाईं ओर — और नया इक्विलिब्रियम: {दाम भी ऊपर, मात्रा भी ऊपर|Price ↑ Quantity ↑|📈}।"),
    ("anim:tomato_up", "[scene] और दो हज़ार तेईस का टमाटर? फ़सल ख़राब — {सप्लाई घटी|Supply ↓|🌧️}।"),
    (None, "[punch] सप्लाई कर्व बाईं ओर — {दाम ऊपर, मात्रा नीचे|Price ↑ Quantity ↓|🍅}!"),

    ("focus:ceiling", "[scene] लेकिन कभी-कभी, सरकार बीच में आती है।"),
    (None, "ज़रूरी चीज़ें — {गेहूँ, चावल, केरोसिन, चीनी|Zaroori cheezein|🍚} — सबको मिलें, इसलिए सरकार उनका ज़्यादा से ज़्यादा दाम तय करती है — इक्विलिब्रियम से भी नीचे।"),
    (None, "[name] इसे कहते हैं — {प्राइस सीलिंग|Price Ceiling|⬇️}। यानी दाम पर छत।"),
    (None, "[punch] लेकिन दाम कम — तो माँग ज़्यादा, माल कम — यानी {शॉर्टेज|Shortage|🧍}।"),
    (None, "तो सरकार करती है {राशनिंग|Rationing|🎫} — राशन कार्ड, राशन की दुकानें। और कभी-कभी — लंबी कतारें, और {काला बाज़ार|Black market|🕶️}।"),

    ("focus:floor", "[scene] और उल्टा भी होता है।"),
    (None, "किसान को उसकी फ़सल का, कम से कम एक सही दाम मिले — इसलिए सरकार, इक्विलिब्रियम से ऊपर, एक न्यूनतम दाम तय करती है।"),
    (None, "[name] इसे कहते हैं — {प्राइस फ़्लोर|Price Floor|⬆️}। यानी दाम का फ़र्श। जैसे — कुछ फ़सलों का {मिनिमम सपोर्ट प्राइस|MSP|🌾}, और मज़दूरों की {मिनिमम वेज|Minimum wage|💵}।"),
    (None, "[punch] लेकिन दाम ऊपर — तो माल ज़्यादा, ख़रीदार कम — यानी {सरप्लस|Surplus|📦}। तो बचा हुआ अनाज, {सरकार ख़रीदती है|Govt buys surplus|🏛️}।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{इक्विलिब्रियम|D = S|🤝} — जहाँ डिमांड और सप्लाई बराबर।"),
    (None, "{सरप्लस और शॉर्टेज|Surplus & Shortage|🫳} — और {अदृश्य हाथ|Invisible Hand|✋} दाम ठीक करता है।"),
    (None, "{कर्व खिसकीं|Shifts|🔄} — तो नया दाम, नई मात्रा।"),
    (None, "{प्राइस सीलिंग|Ceiling → Shortage|⬇️}, और {प्राइस फ़्लोर|Floor → Surplus|⬆️}।"),

    ("outro:Next: Monopoly", "[scene] लेकिन दोस्तों — अगर बाज़ार में, सिर्फ़ एक ही बेचने वाला हो? तो क्या वो, जो चाहे वो दाम ले सकता है?"),
    (None, "[punch] मोनोपॉली, और दूसरे बाज़ार — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
