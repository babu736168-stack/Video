"""Econ04 - Demand: Chaahat, Paisa aur Man. Course plan: Ramesh Singh Ch 1, NCERT foundation class 4.
Source: NCERT Class 12 Introductory Microeconomics, Chapter 2 "Theory of Consumer Behaviour".
Builds on the approved 2-minute sample (ds_2min: mango cart, tomato July 2023 above Rs 200/kg in several cities).
Facts used: utility = want-satisfying capacity of a good; total utility, marginal utility (change in total utility
from one more unit); law of diminishing marginal utility; consumer's bundle; budget set and budget line
(p1x1 + p2x2 = M; bundles costing more than M are not affordable); consumer's optimum: the best affordable bundle
(on the budget line, where the indifference curve just touches it); indifference curve = bundles giving the same
satisfaction, slopes down; demand = quantity a consumer is willing and able to buy at a price; law of demand: other
things remaining the same, price and quantity demanded move in opposite directions; demand curve slopes down;
movement along vs shift of the demand curve (income, prices of related goods, tastes); normal goods (demand rises
with income) and inferior goods (demand falls as income rises, e.g. coarse cereals); substitutes (tea and coffee) and
complements (tea and sugar); market demand = sum of all consumers' demands at each price; price elasticity of
demand = % change in quantity demanded / % change in price; elastic (>1), inelastic (<1), unitary (=1); necessities
are inelastic, goods with close substitutes are elastic; if demand is inelastic, a price rise raises total
expenditure. Everyday numbers in the stories (₹200, ₹60, plates of golgappe) are illustrations, not textbook data.
"""
CHAPTER = dict(num=4, title="Demand", kicker="ECONOMICS · CLASS 4 · NCERT CLASS 12 MICRO", rain="🛒",
               outro_icons=("🏭", "⚙️"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Production aur Cost")

TOPICS = [
    dict(id="utility", name="Utility", label="Why the 3rd plate tastes less", icon="😋"),
    dict(id="budget", name="Budget Line", label="What you can afford", icon="💳"),
    dict(id="demand", name="Demand", label="Wanting isn't enough", icon="🛒"),
    dict(id="law", name="Law of Demand", label="Price up, buyers down", icon="🥭"),
    dict(id="shift", name="Shift in Demand", label="When the whole curve moves", icon="🍦"),
    dict(id="elastic", name="Elasticity", label="How strongly buyers react", icon="🧂"),
]

LINES = [
    ("hook", "[scene] अरे दोस्तों! एक बात बताइए — {टमाटर|Tamatar|🍅} कभी बीस रुपये किलो, और कभी दो सौ रुपये किलो! ऐसा क्यों?"),
    (None, "{दो हज़ार तेईस|July 2023|📅} की जुलाई में तो, कई शहरों में टमाटर, सच में {दो सौ के पार|₹200+|🔥} चला गया था!"),
    (None, "[punch] टमाटर वही, खेत वही — फिर ये दाम का खेल, खेलता कौन है?"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {तीसरी प्लेट|Utility|😋} पहली जितनी मज़ेदार क्यों नहीं लगती।"),
    (None, "दूसरा — आपकी जेब, आपकी {हद|Budget Line|💳} कैसे तय करती है।"),
    (None, "तीसरा — {डिमांड|Demand & Law of Demand|🛒} असल में क्या है, और दाम बढ़ने पर लोग कम क्यों ख़रीदते हैं।"),
    (None, "और चौथा — पूरी कर्व कब {खिसकती है|Shift & Elasticity|🍦}, और लोग दाम पर कितना भड़कते हैं।"),

    ("center", "[name] क्लास चार — डिमांड!"),
    ("topics", "चलिए — शुरुआत, गोलगप्पे के ठेले से!"),

    ("focus:utility", "[scene] भूख लगी है, और सामने {गोलगप्पे|Golgappe|🥟}! पहली प्लेट — वाह, क्या मज़ा!"),
    (None, "दूसरी प्लेट — अच्छी है। तीसरी — ठीक है। और चौथी? बस भाई, अब नहीं!"),
    (None, "[name] किसी चीज़ से मिलने वाली संतुष्टि को कहते हैं — {यूटिलिटी|Utility|😋}।"),
    (None, "सारी प्लेटों का कुल मज़ा — {टोटल यूटिलिटी|Total Utility|➕}। और हर नई प्लेट से, जो मज़ा जुड़ा — {मार्जिनल यूटिलिटी|Marginal Utility|📉}।"),
    (None, "[punch] और हर अगली प्लेट से, मज़ा कम होता जाता है — इसे कहते हैं — {लॉ ऑफ़ डिमिनिशिंग मार्जिनल यूटिलिटी|Diminishing MU|⬇️}।"),
    ("ex:", "इसीलिए — चौथी प्लेट के लिए, आप उतने पैसे नहीं देना चाहते, जितने पहली के लिए।"),

    ("focus:budget", "[scene] लेकिन मज़ा ही सब कुछ नहीं। जेब भी तो देखनी है!"),
    (None, "मान लीजिए आपके पास है — कुछ {पैसे|Income M|💵}। और दो चीज़ें — {गोलगप्पे|Good 1|🥟} और {आइसक्रीम|Good 2|🍦}।"),
    (None, "दोनों का कोई भी मेल — इसे कहते हैं — एक {बंडल|Bundle|🧺}।"),
    (None, "जो बंडल आपकी जेब में फ़िट हों — वो हैं {बजट सेट|Budget Set|✅}। और जिन बंडलों पर, पूरा पैसा ख़र्च हो जाए — वो बनाते हैं एक सीधी लाइन — {बजट लाइन|Budget Line|📏}।"),
    (None, "[scene] और आपकी पसंद? जिन बंडलों से, एक जैसा मज़ा मिले — उनकी कर्व को कहते हैं — {इनडिफ़रेंस कर्व|Indifference Curve|〰️}।"),
    (None, "[punch] और समझदार ग्राहक चुनता है — जेब के अंदर, सबसे मज़ेदार बंडल। यही है — {कंज़्यूमर्स ऑप्टिमम|Consumer's Optimum|🎯}।"),

    ("focus:demand", "[scene] अब सोचिए, एक छोटा बच्चा, खिलौने की दुकान पर खड़ा है। उसे वो {रिमोट वाली कार|Remote car|🚗} चाहिए!"),
    ("anim:wish", "लेकिन जेब में? {एक रुपया भी नहीं|₹0|👛}!"),
    (None, "तो क्या ये डिमांड है?"),
    (None, "[punch] बिल्कुल नहीं!"),
    (None, "[name] {डिमांड|Demand|🛒} का सीधा-सा मतलब — चीज़ {चाहिए|Chahiye|❤️}, {पैसे भी हैं|Paise|💵}, और ख़र्च करने का {मन भी है|Man|✅}। तीनों एक साथ!"),
    (None, "एन सी ई आर टी की बात का निचोड़ भी यही है — किसी दाम पर, आप जितना ख़रीदना चाहते हैं, और ख़रीद भी सकते हैं — वही आपकी डिमांड है।"),

    ("focus:law", "[scene] अब चलिए, आम वाले ठेले पर! सीज़न का पहला आम — {दो सौ रुपये किलो|₹200|🥭}। लोग देखते हैं, और चुपचाप आगे बढ़ जाते हैं।"),
    ("anim:mango", "कुछ हफ़्ते बाद — वही आम, {साठ रुपये किलो|₹60|🥭}! और अब? ठेले पर भीड़ ही भीड़!"),
    (None, "[name] यही है — {लॉ ऑफ़ डिमांड|Law of Demand|📉}!"),
    (None, "{दाम बढ़ा|Daam ↑ Kharid ↓|📈}, तो लोग कम ख़रीदते हैं। दाम घटा, तो ज़्यादा। बस एक शर्त — बाक़ी सब कुछ, वैसा ही रहे।"),
    ("anim:demand_curve", "और इसे ग्राफ़ पर बनाएँ — तो बनती है, फिसलपट्टी जैसी, नीचे उतरती एक लाइन — {डिमांड कर्व|Demand Curve|📉}!"),
    ("anim:move_along", "दाम बदला — तो हम इसी कर्व पर, ऊपर-नीचे चलते हैं। इसे कहते हैं — {मूवमेंट अलॉन्ग द कर्व|Movement along|↕️}।"),
    (None, "और जब सब ग्राहकों की डिमांड जोड़ दें — तो मिलती है {मार्केट डिमांड|Market Demand|👥}।"),

    ("focus:shift", "[scene] अब एक मज़ेदार बात। गर्मी आई — {पैंतालीस डिग्री|45°C|☀️}!"),
    ("anim:summer", "{कुल्फ़ी|Kulfi|🍦} का दाम वही — लेकिन भीड़ दोगुनी!"),
    ("anim:shift_right", "[punch] दाम नहीं बदला — फिर भी डिमांड बढ़ी! यानी पूरी कर्व, दाईं ओर खिसक गई — {शिफ़्ट इन डिमांड|Shift in Demand|➡️}।"),
    (None, "कर्व खिसकती है जब बदलें — {आमदनी|Income|💰}, {पसंद|Taste|❤️}, या {दूसरी चीज़ों के दाम|Related prices|🏷️}।"),
    ("anim:none", "आमदनी बढ़ी, और डिमांड भी बढ़ी — ये हैं {नॉर्मल गुड्स|Normal goods|🛍️}। लेकिन कुछ चीज़ें, आमदनी बढ़ने पर, कम ख़रीदी जाती हैं — जैसे {मोटा अनाज|Inferior goods|🌾} — ये हैं इन्फ़ीरियर गुड्स।"),
    (None, "{चाय और कॉफ़ी|Substitutes|☕} — एक-दूसरे की जगह ले सकते हैं — ये हैं सब्स्टीट्यूट्स। और {चाय और चीनी|Complements|🍬} — साथ-साथ चलते हैं — ये हैं कॉम्प्लिमेंट्स।"),

    ("focus:elastic", "[scene] आख़िरी सवाल — दाम बढ़ने पर, लोग कितना भड़कते हैं?"),
    (None, "[name] इसे नापते हैं — {प्राइस इलास्टिसिटी ऑफ़ डिमांड|Price Elasticity|🧂}। यानी — डिमांड में प्रतिशत बदलाव, भाग — दाम में प्रतिशत बदलाव।"),
    (None, "अगर ये एक से ज़्यादा — तो डिमांड {इलास्टिक|Elastic > 1|🎈}। एक से कम — तो {इनइलास्टिक|Inelastic < 1|🧱}। और ठीक एक — तो {यूनिटरी|Unitary = 1|⚖️}।"),
    ("ex:", "{नमक|Namak|🧂} का दाम बढ़े — तो भी आप, उतना ही ख़रीदेंगे। ज़रूरी चीज़ — इनइलास्टिक। लेकिन जिन चीज़ों के {बहुत विकल्प|Substitutes = Elastic|🍫} हों — उनकी डिमांड, इलास्टिक।"),
    (None, "[punch] और ध्यान दीजिए — अगर डिमांड इनइलास्टिक है, और दाम बढ़ा — तो लोगों का {कुल ख़र्च|Total expenditure ↑|💸}, बढ़ जाता है!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{डिमिनिशिंग मार्जिनल यूटिलिटी|Diminishing MU|😋} — हर अगली प्लेट, कम मज़ा।"),
    (None, "{बजट लाइन|Budget Line|📏}, और {कंज़्यूमर्स ऑप्टिमम|Consumer's Optimum|🎯}।"),
    (None, "{डिमांड|Demand|🛒} — चाहत, पैसा और मन। {लॉ ऑफ़ डिमांड|Law of Demand|📉} — दाम ऊपर, तो ख़रीद नीचे।"),
    (None, "{शिफ़्ट|Shift|➡️} — दाम वही, फिर भी कर्व खिसकी। और {इलास्टिसिटी|Elasticity|🧂} — भड़कने का पैमाना।"),

    ("outro:Next: Production aur Cost", "[scene] अब तक हमने ख़रीदार की बात की। लेकिन दोस्तों — बेचने वाला, चीज़ें बनाता कैसे है? और उसकी लागत कितनी आती है?"),
    (None, "[punch] प्रोडक्शन और कॉस्ट की कहानी — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
