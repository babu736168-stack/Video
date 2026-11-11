"""Econ03 - Teen Sectors: Kheti, Kaarkhana, Seva. Course plan: Ramesh Singh Ch 1, NCERT foundation class 3.
Source: NCERT Class 10 Economics (Understanding Economic Development), Chapter 2 "Sectors of the Indian Economy".
Facts used: primary sector = using natural resources directly (agriculture, dairy, fishing, forestry), also called
agriculture and related sector; secondary = changing natural products into other forms through manufacturing
(cotton -> cloth, sugarcane -> sugar/gur, earth -> bricks), also industrial sector; tertiary = activities that help
the other two and do not produce a good themselves (transport, storage, communication, banking, trade), also service
sector; also personal and professional services and IT. Final vs intermediate goods; counting intermediate goods
means double counting; GDP = value of all final goods and services produced within a country during a year; measured
by a central government ministry with the states and union territories. Historically primary first, then secondary,
then (in developed countries) tertiary; in India the tertiary sector has become the largest producing sector,
replacing the primary sector. Why services grew: basic services (hospitals, schools, post, police, courts, banks) are
the government's job; growth of farming and industry needs transport, trade, storage; higher incomes demand more
services (eating out, tourism, private schools and hospitals); IT. Not all services grow equally (many small
shopkeepers, repair workers). Primary sector is still the largest employer but produces a smaller share of GDP;
underemployment / disguised unemployment (more people than needed; nobody fully employed); in cities, casual work.
More jobs: irrigation, transport and storage, cheap bank loans, agro-based industries (dal mill, cold storage, honey,
fruit and vegetable processing), tourism, crafts, IT. MGNREGA 2005: 100 days of guaranteed work a year in rural
areas for those able and in need; otherwise unemployment allowance. Organised sector (registered, follows laws such
as the Factories Act, Minimum Wages Act, Payment of Gratuity Act, Shops and Establishments Act; job security, fixed
hours, overtime, paid leave, provident fund, gratuity, medical benefits) vs unorganised (small scattered units, low
pay, no job security, no paid leave). Protection needed for landless labourers, small farmers, sharecroppers,
artisans, casual workers, street vendors, construction workers. Public sector (government owns most assets: Railways,
post office) vs private sector (e.g. TISCO, Reliance Industries); government provides roads, bridges, railways,
harbours, electricity, dams, cheap electricity; FCI buys grain from farmers at a fair price and sells cheaper to
consumers (government bears part of the cost); health and education.
"""
CHAPTER = dict(num=3, title="Teen Sectors", kicker="ECONOMICS · CLASS 3 · NCERT CLASS 10", rain="🏭",
               outro_icons=("🛒", "📈"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Demand — chaahat, paisa aur man")

TOPICS = [
    dict(id="three", name="Three Sectors", label="Kheti · Kaarkhana · Seva", icon="🏭"),
    dict(id="gdp", name="Counting the Total", label="Final goods & GDP", icon="🧮"),
    dict(id="shift", name="The Big Shift", label="Who produces, who works", icon="🔄"),
    dict(id="jobs", name="Jobs", label="Disguised unemployment & MGNREGA", icon="👷"),
    dict(id="organised", name="Organised vs Unorganised", label="Safe job or no guarantee?", icon="📋"),
    dict(id="owner", name="Public vs Private", label="Who owns it?", icon="🏛️"),
]

LINES = [
    ("hook", "[scene] दोस्तों, सुबह की एक {रोटी|Roti|🫓} देखिए।"),
    (None, "{गेहूँ|Gehun|🌾} उगाया किसान ने। {आटा|Aata|🏭} बनाया चक्की ने। और आपके घर तक लाया — {दुकानदार|Dukaandaar|🚚}।"),
    (None, "[punch] एक रोटी — और उसके पीछे, इकॉनमी के तीनों हिस्से!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — इकॉनमी के {तीन सेक्टर|3 Sectors|🏭}।"),
    (None, "दूसरा — पूरे देश की कमाई कैसे गिनें — यानी {जीडीपी|GDP|🧮}।"),
    (None, "तीसरा — {रोज़गार|Rozgaar|👷} की असली तस्वीर।"),
    (None, "और चौथा — {संगठित और असंगठित|Organised · Public|📋} — और सरकारी या प्राइवेट।"),

    ("center", "[name] क्लास तीन — इकॉनमी के तीन सेक्टर!"),
    ("topics", "चलिए — खेत से शुरू करते हैं!"),

    ("focus:three", "[scene] पहला — {प्राइमरी सेक्टर|Primary Sector|🌾}। जहाँ हम कुदरत से, सीधे चीज़ें लेते हैं — {खेती|Kheti|🌱}, {डेयरी|Dairy|🐄}, {मछली पकड़ना|Fishing|🎣}, {जंगल|Forestry|🌳}। इसे खेती और उससे जुड़ा सेक्टर भी कहते हैं।"),
    (None, "दूसरा — {सेकेंडरी सेक्टर|Secondary Sector|🏭}। जहाँ कुदरती चीज़ों को, बनाकर नया रूप दिया जाता है। जैसे — {कपास से कपड़ा|Kapas → Kapda|👕}, {गन्ने से चीनी|Ganna → Cheeni|🍬}, {मिट्टी से ईंट|Mitti → Eent|🧱}। इसे इंडस्ट्रियल सेक्टर भी कहते हैं।"),
    (None, "तीसरा — {टर्शियरी सेक्टर|Tertiary Sector|🚚}। ये ख़ुद कोई चीज़ नहीं बनाता — बाक़ी दोनों की मदद करता है। {ट्रांसपोर्ट|Transport|🚛}, {गोदाम|Storage|📦}, {बैंक|Bank|🏦}, {व्यापार|Trade|🛒}। इसे सर्विस सेक्टर भी कहते हैं।"),
    ("ex:", "और {टीचर, डॉक्टर, नाई, वकील|Personal services|👩‍🏫} — और {आईटी|IT|💻} वाले भी — सब सर्विस सेक्टर में!"),

    ("focus:gdp", "[scene] अब सवाल — तीनों सेक्टर मिलकर, कितना बनाते हैं? गिनें कैसे?"),
    (None, "किसान ने गेहूँ बेचा चक्की को। चक्की ने आटा बेचा बिस्किट कंपनी को। और कंपनी ने बिस्किट बेचे आपको।"),
    (None, "[punch] अगर गेहूँ, आटा, और बिस्किट — तीनों जोड़ दें — तो गेहूँ तीन बार गिन लिया! इसे कहते हैं — {डबल काउंटिंग|Double counting|⚠️}।"),
    (None, "इसलिए सिर्फ़ {फ़ाइनल गुड्स|Final goods|🍪} गिने जाते हैं — जो आख़िरी ग्राहक तक पहुँचे। बीच की चीज़ें — गेहूँ, आटा — हैं {इंटरमीडिएट गुड्स|Intermediate goods|🌾}।"),
    (None, "[name] एक साल में, देश के अंदर बने, सारे फ़ाइनल गुड्स और सर्विसेज़ की क़ीमत — यही है — {जीडीपी|GDP|🧮}। यानी ग्रॉस डोमेस्टिक प्रोडक्ट।"),
    (None, "भारत में ये बड़ा काम — केंद्र सरकार का {एक मंत्रालय|Central Ministry|🏛️} करता है, सारे राज्यों और केंद्र शासित प्रदेशों की मदद से।"),

    ("focus:shift", "[scene] अब इतिहास की एक बड़ी कहानी। शुरुआत में — हर देश में सबसे बड़ा था, {प्राइमरी सेक्टर|Primary pehle|🌾}।"),
    (None, "फिर खेती के नए तरीक़े आए, और कारख़ाने बढ़े — तो आगे निकला {सेकेंडरी|Phir Secondary|🏭}।"),
    (None, "और विकसित देशों में, पिछले सौ सालों में — सबसे आगे निकल गया {सर्विस सेक्टर|Phir Services|🚚}।"),
    (None, "[punch] और भारत में? उत्पादन के मामले में — {टर्शियरी सेक्टर|Tertiary No. 1|🥇} सबसे बड़ा बन गया — प्राइमरी को पीछे छोड़कर!"),
    (None, "लेकिन क्यों? पहला — {बुनियादी सेवाएँ|Basic services|🏥}। अस्पताल, स्कूल, डाक, पुलिस, अदालत, बैंक — ये देना, सरकार की ज़िम्मेदारी है।"),
    (None, "दूसरा — खेती और कारख़ाने बढ़े, तो बढ़ी ज़रूरत — {ट्रांसपोर्ट, व्यापार, गोदाम|Transport · Trade|🚛} की।"),
    (None, "तीसरा — लोगों की {कमाई बढ़ी|Zyada kamaai|💰}, तो बढ़ी माँग — बाहर खाना, घूमना-फिरना, प्राइवेट स्कूल और अस्पताल।"),
    (None, "और चौथा — {आईटी|IT|💻}। इंटरनेट, सॉफ़्टवेयर, कॉल सेंटर।"),
    (None, "[scene] लेकिन ध्यान दीजिए — सर्विस सेक्टर में सब चमकता नहीं। बहुत से लोग — {छोटे दुकानदार|Chhote dukaandaar|🛠️}, मरम्मत करने वाले — मुश्किल से गुज़ारा करते हैं।"),

    ("focus:jobs", "[scene] अब सबसे बड़ा सवाल — लोग काम कहाँ करते हैं?"),
    (None, "[punch] जवाब चौंकाने वाला है। आज भी {सबसे ज़्यादा लोग|Sabse zyada log|👨‍🌾} — प्राइमरी सेक्टर में काम करते हैं। लेकिन जीडीपी में, उसका हिस्सा कहीं कम!"),
    (None, "[scene] सोचिए — एक छोटा-सा खेत, और उस पर काम कर रहा है, {पाँच लोगों का परिवार|5 log, 1 khet|👨‍👩‍👧‍👦}।"),
    (None, "सब काम में लगे दिखते हैं। लेकिन अगर दो लोग, कहीं और काम करने चले जाएँ — तो खेत की पैदावार, ज़रा भी नहीं घटेगी!"),
    (None, "[name] इसे कहते हैं — {छुपी हुई बेरोज़गारी|Disguised Unemployment|🙈}। यानी अंडर-एम्प्लॉयमेंट। सब काम कर रहे हैं — लेकिन कोई भी, पूरा काम नहीं कर रहा।"),
    (None, "शहरों में भी — {दिहाड़ी मज़दूर|Casual workers|🧰}, जैसे पेंटर, प्लंबर — रोज़ काम ढूँढते हैं।"),
    (None, "[scene] तो ज़्यादा काम आएँ कैसे? {सिंचाई|Sinchaai|💧} — तो साल में ज़्यादा फ़सल। {सड़क और गोदाम|Sadak aur Godaam|🛣️} — तो फ़सल बाज़ार तक।"),
    (None, "बैंक से {सस्ता लोन|Sasta loan|🏦}। और गाँव में ही {छोटे कारख़ाने|Agro industries|🫙} — दाल मिल, कोल्ड स्टोरेज, शहद, फल और सब्ज़ियों की प्रोसेसिंग। और {टूरिज़्म|Tourism|🏞️}, {हस्तकला|Crafts|🧶}, {आईटी|IT|💻} भी।"),
    (None, "[scene] और सरकार का एक बड़ा क़दम — {मनरेगा|MGNREGA 2005|📜}। यानी महात्मा गांधी नेशनल रूरल एम्प्लॉयमेंट गारंटी एक्ट, दो हज़ार पाँच।"),
    (None, "[punch] गाँव में, जो काम कर सकता है और जिसे काम चाहिए — उसे साल में {सौ दिन|100 din kaam|📅} काम की गारंटी! और अगर सरकार काम न दे पाए — तो {बेरोज़गारी भत्ता|Unemployment allowance|💵}।"),

    ("focus:organised", "[scene] अब दो तरह की नौकरियाँ देखिए।"),
    (None, "पहली — {संगठित सेक्टर|Organised Sector|📋}। कंपनी सरकार के पास रजिस्टर्ड है — और क़ानून मानती है। जैसे {फ़ैक्टरीज़ एक्ट|Factories Act|⚖️}, {मिनिमम वेजेज़ एक्ट|Minimum Wages Act|💵}।"),
    (None, "यहाँ मिलता है — {पक्की नौकरी|Job security|🔐}, तय घंटे, ओवरटाइम का पैसा, {छुट्टी का वेतन|Paid leave|🏖️}, {प्रोविडेंट फ़ंड|Provident Fund|🏦}, ग्रेच्युटी, और इलाज की सुविधा।"),
    (None, "दूसरी — {असंगठित सेक्टर|Unorganised Sector|🧺}। छोटी-छोटी, बिखरी हुई इकाइयाँ — जो सरकार की नज़र से, ज़्यादातर बाहर हैं।"),
    (None, "[punch] यहाँ — {कम तनख़्वाह|Kam tankhwaah|📉}, कोई गारंटी नहीं, छुट्टी का पैसा नहीं — और बिना वजह, काम से निकाला जा सकता है।"),
    (None, "इन्हें सबसे ज़्यादा {सुरक्षा|Suraksha|🛡️} चाहिए — बिना ज़मीन के मज़दूर, छोटे किसान, बटाईदार, कारीगर — और शहरों में दिहाड़ी मज़दूर, ठेले वाले, और इमारतें बनाने वाले।"),

    ("focus:owner", "[scene] आख़िरी सवाल — कंपनी का मालिक कौन?"),
    (None, "{पब्लिक सेक्टर|Public Sector|🏛️} — जहाँ ज़्यादातर चीज़ों की मालिक, सरकार है। जैसे — {रेलवे|Railways|🚆}, और {डाकघर|Post Office|📮}।"),
    (None, "{प्राइवेट सेक्टर|Private Sector|🏢} — जहाँ मालिक, लोग या कंपनियाँ हैं। जैसे — {टिस्को|TISCO|🔩}, या {रिलायंस इंडस्ट्रीज़|Reliance Industries|🏭}।"),
    (None, "[punch] प्राइवेट सेक्टर का मक़सद — {मुनाफ़ा|Munaafa|💰}। लेकिन सरकार का मक़सद — सिर्फ़ मुनाफ़ा नहीं, {लोगों की भलाई|Logon ki bhalaai|❤️}।"),
    (None, "सड़कें, पुल, रेलवे, बंदरगाह, बिजली, बाँध — इन पर बहुत बड़ा ख़र्च होता है। ये {सरकार|Sarkar banati hai|🌉} बनाती है।"),
    ("ex:", "जैसे — {एफ़ सी आई|FCI|🍚}। ये किसानों से, सही दाम पर अनाज ख़रीदती है — और लोगों को, कम दाम पर बेचती है। बीच का ख़र्च, सरकार उठाती है।"),
    (None, "और {सेहत और शिक्षा|Sehat aur Shiksha|🏥} — ये भी, सरकार की बड़ी ज़िम्मेदारी।"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{तीन सेक्टर|Primary · Secondary · Tertiary|🏭} — कुदरत से लेना, बनाना, और सेवा।"),
    (None, "{जीडीपी|GDP = Final goods|🧮} — सिर्फ़ फ़ाइनल गुड्स गिनो।"),
    (None, "उत्पादन में {सर्विसेज़ आगे|Services No. 1|🥇} — लेकिन रोज़गार में आज भी, खेती।"),
    (None, "{छुपी बेरोज़गारी|Disguised Unemployment|🙈}, और {मनरेगा|MGNREGA|📜}।"),
    (None, "{संगठित बनाम असंगठित|Organised vs Unorganised|📋}, और {सरकारी बनाम प्राइवेट|Public vs Private|🏛️}।"),

    ("outro:Next: Demand", "[scene] लेकिन दोस्तों — बाज़ार में दाम तय कैसे होता है? लोग कोई चीज़, कितनी ख़रीदेंगे?"),
    (None, "[punch] ये कहानी शुरू होती है — एक शब्द से — डिमांड! अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
