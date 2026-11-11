"""Econ13 - Vikas Kya Hai? (Development). Course plan: Ramesh Singh Ch 3, NCERT foundation class 13.
Source: NCERT Class 10 Economics (Understanding Economic Development), Chapter 1 "Development".
Facts used: different people have different development goals (a landless rural labourer: more days of work, better
wages, a local school; a prosperous Punjab farmer: higher support prices; a girl from a rich urban family: as much
freedom as her brother, to decide what she wants to do); goals can conflict (industrialists may want more dams for
electricity, which may submerge land and displace people such as tribals). Besides income people want equal
treatment, freedom, security and respect; safe working environment. National development: countries are compared by
average income = per capita income (used by the World Bank in its World Development Report), but averages hide
disparities (illustration: two countries with the same average income, one equal and one very unequal). Income is not
enough: Haryana has a higher per capita income than Kerala, but Kerala does better on infant mortality, literacy and
school attendance because of adequate basic health and education facilities; Bihar is behind on all of them.
Infant mortality rate = children dying before age one per 1000 live births in that year; literacy rate = share of
literate people aged 7 and above; net attendance ratio = children aged 14-15 attending school as a percentage of all
children of that age. Public facilities (health, education, PDS) matter. UNDP's Human Development Report compares
countries by education, health and per capita income (HDI). Sustainability: groundwater is being overused,
non-renewable resources like crude oil will run out, and environmental damage crosses national boundaries.
"""
CHAPTER = dict(num=13, title="Vikas Kya Hai?", kicker="ECONOMICS · CLASS 13 · NCERT CLASS 10", rain="📈",
               outro_icons=("🇮🇳", "🇨🇳"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Bharat aur uske padosi",
               bars={"avg_bars": dict(title="Dono desh: average ₹10,000 — par sach?", bars=[
                   ("Desh A (sab)", 10000, (70, 210, 140)),
                   ("Desh B (4 log)", 500, (255, 90, 90)), ("Desh B (1 aadmi)", 48000, (255, 183, 3))])})

TOPICS = [
    dict(id="goals", name="Different Goals", label="My development, your development", icon="🎯"),
    dict(id="beyond", name="Beyond Income", label="Respect, freedom, safety", icon="🕊️"),
    dict(id="average", name="Average Income", label="What the average hides", icon="➗"),
    dict(id="kerala", name="Income Isn't Everything", label="Haryana, Kerala, Bihar", icon="🏥"),
    dict(id="hdi", name="HDI & Sustainability", label="Will it last?", icon="🌍"),
]

LINES = [
    ("hook", "[scene] दोस्तों, तीन लोगों से एक ही सवाल पूछिए — आपके लिए {विकास|Vikas|📈} क्या है?"),
    (None, "एक {खेत मज़दूर|Khet mazdoor|👷} कहेगा — साल भर काम, और अच्छी मज़दूरी।"),
    (None, "पंजाब का एक {अमीर किसान|Ameer kisaan|🚜} कहेगा — फ़सल का ऊँचा दाम।"),
    (None, "और शहर की एक {लड़की|Ladki|👧} कहेगी — उतनी ही आज़ादी, जितनी मेरे भाई को!"),
    (None, "[punch] एक सवाल — तीन जवाब! तो विकास है क्या?"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — हर इंसान के, {अलग लक्ष्य|Different goals|🎯}।"),
    (None, "दूसरा — {कमाई के अलावा|Beyond income|🕊️} भी, क्या-क्या चाहिए।"),
    (None, "तीसरा — देशों की तुलना, और {औसत आमदनी का धोखा|Average income|➗}।"),
    (None, "और चौथा — {केरल की सीख|Kerala, HDI|🏥}, और क्या ये विकास, टिकेगा?"),

    ("center", "[name] क्लास तेरह — विकास क्या है?"),
    ("topics", "चलिए — उन तीन जवाबों से शुरू करते हैं!"),

    ("focus:goals", "[scene] खेत मज़दूर चाहता है — {ज़्यादा दिन काम|Zyada din kaam|📅}, {अच्छी मज़दूरी|Achhi mazdoori|💵}, और बच्चों के लिए, {गाँव में स्कूल|Gaon mein school|🏫}।"),
    (None, "पंजाब का अमीर किसान चाहता है — फ़सल का {ऊँचा सपोर्ट प्राइस|Higher support price|🌾}।"),
    (None, "और शहर की लड़की चाहती है — {भाई जितनी आज़ादी|Equal freedom|🕊️}, और अपनी ज़िंदगी के फ़ैसले, ख़ुद लेना।"),
    (None, "[punch] और कभी-कभी — एक का विकास, दूसरे का नुक़सान भी बन जाता है!"),
    ("ex:", "जैसे — कारख़ानों को बिजली चाहिए, तो {बड़ा बाँध|Bada baandh|🌊}। लेकिन उससे ज़मीन डूबे — तो वहाँ रहने वाले लोग, जैसे आदिवासी — {उजड़ जाते हैं|Visthaapan|🏚️}।"),

    ("focus:beyond", "[scene] क्या सिर्फ़ पैसा ही सब कुछ है?"),
    (None, "[name] लोग चाहते हैं — {बराबरी का बर्ताव|Equal treatment|⚖️}, {आज़ादी|Freedom|🕊️}, {सुरक्षा|Security|🛡️}, और {इज़्ज़त|Respect|🙏}।"),
    ("ex:", "सोचिए — एक नौकरी में, तनख़्वाह ज़्यादा, लेकिन न सुरक्षा, न इज़्ज़त। और दूसरी में, थोड़ी कम तनख़्वाह — लेकिन {सुरक्षित माहौल|Safe workplace|🏢}। बहुत लोग, दूसरी चुनेंगे!"),

    ("focus:average", "[scene] अब पूरे देश का विकास, नापें कैसे?"),
    (None, "[name] सबसे आम तरीक़ा — {औसत आमदनी|Average income|➗}। यानी देश की कुल आमदनी, भाग — आबादी। इसे कहते हैं {पर कैपिटा इनकम|Per Capita Income|🧍}।"),
    (None, "{वर्ल्ड बैंक|World Bank|🏦} भी, अपनी {वर्ल्ड डेवलपमेंट रिपोर्ट|World Development Report|📘} में, देशों की तुलना इसी से करता है।"),
    ("anim:avg_bars", "[scene] लेकिन एक धोखा पकड़िए। मान लीजिए, दो देश — पाँच-पाँच लोग। {देश ए|Desh A|🟩} में सबकी आमदनी — क़रीब दस हज़ार।"),
    (None, "और {देश बी|Desh B|🟥} में — चार लोगों के पास, सिर्फ़ पाँच-पाँच सौ।"),
    (None, "और एक आदमी के पास — {अड़तालीस हज़ार|₹48,000|💰}!"),
    (None, "[punch] औसत — दोनों का, दस हज़ार! लेकिन कौन-सा देश, रहने लायक़? औसत, {असमानता छुपा लेता है|Average hides inequality|🙈}!"),

    ("focus:kerala", "[scene] अब भारत के तीन राज्य देखिए — {हरियाणा|Haryana|🟧}, {केरल|Kerala|🟩}, और {बिहार|Bihar|🟥}।"),
    (None, "आमदनी में — हरियाणा, केरल से आगे।"),
    (None, "[punch] लेकिन बच्चों की मौत की दर — यानी {इन्फ़ैंट मॉर्टैलिटी रेट|Infant Mortality Rate|👶} — केरल में सबसे कम! और पढ़ाई में भी, केरल आगे।"),
    (None, "[name] {आई एम आर|IMR|👶} मतलब — एक साल में पैदा हुए, हर हज़ार ज़िंदा बच्चों में से — कितने, एक साल की उम्र से पहले मर गए।"),
    (None, "{लिटरेसी रेट|Literacy Rate|📖} — सात साल और उससे बड़े लोगों में, पढ़े-लिखों का हिस्सा। और {नेट अटेंडेंस रेशियो|Net Attendance Ratio|🏫} — चौदह-पंद्रह साल के बच्चों में से, कितने स्कूल जाते हैं।"),
    (None, "केरल आगे क्यों? क्योंकि वहाँ — {बुनियादी सेहत और शिक्षा|Basic health & education|🏥} की सुविधाएँ, ठीक से हैं।"),
    (None, "और बिहार — इन सब में, पीछे है।"),
    (None, "[punch] सीख — पैसा, सब कुछ नहीं ख़रीद सकता। कुछ चीज़ें — {सरकारी सुविधाएँ|Public facilities|🏛️} ही, सबसे सस्ते में देती हैं — स्कूल, अस्पताल, और राशन की दुकान।"),

    ("focus:hdi", "[scene] इसलिए {यू एन डी पी|UNDP|🌐} ने बनाया — एक बड़ा पैमाना।"),
    (None, "[name] {ह्यूमन डेवलपमेंट रिपोर्ट|Human Development Report|📘} — जो देशों को मिलाती है, {शिक्षा|Education|🎓}, {सेहत|Health|🏥}, और {पर कैपिटा इनकम|Income|💰} से। यानी — {एच डी आई|HDI|🌍}।"),
    (None, "[scene] और आख़िरी सवाल — क्या ये विकास, {टिकेगा|Sustainability|♻️}?"),
    (None, "ज़मीन के नीचे का {पानी|Groundwater|💧} — ज़रूरत से ज़्यादा निकाला जा रहा है।"),
    (None, "{कच्चा तेल|Crude oil|🛢️} जैसे साधन — दोबारा नहीं बनते, एक दिन ख़त्म होंगे।"),
    (None, "[punch] और प्रदूषण — {सरहदें नहीं देखता|No borders|🌍}। एक देश का धुआँ, दूसरे देश तक जाता है!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{अलग लोग, अलग लक्ष्य|Different goals|🎯}।"),
    (None, "{कमाई के अलावा|Freedom · Security · Respect|🕊️} — आज़ादी, सुरक्षा, इज़्ज़त।"),
    (None, "{औसत आमदनी|Per capita income|➗} — लेकिन औसत, असमानता छुपाता है।"),
    (None, "{केरल की सीख|IMR · Literacy · Attendance|🏥}, {एच डी आई|HDI|🌍}, और {टिकाऊ विकास|Sustainability|♻️}।"),

    ("outro:Next: Bharat aur Padosi", "[scene] दोस्तों — भारत, चीन, और पाकिस्तान — तीनों ने, लगभग एक ही समय पर, सफ़र शुरू किया।"),
    (None, "[punch] फिर कौन कहाँ पहुँचा — और कैसे? अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
