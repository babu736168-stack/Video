"""Econ14 - Bharat aur Uske Padosi (India, China, Pakistan). Course plan: Ramesh Singh Ch 3, NCERT class 14.
Source: NCERT Class 11 Indian Economic Development, Chapter 8 "Comparative Development Experiences of India and its
Neighbours".
Facts used: India and Pakistan became independent in 1947; the People's Republic of China was set up in 1949.
India's first Five Year Plan 1951-56; China's first Five Year Plan 1953; Pakistan's first five year plan (now called
the Medium Term Development Plan) 1956. China: Great Leap Forward campaign (1958) to industrialise on a massive
scale, people encouraged to set up industries in their backyards; communes in rural areas (collective farming);
Great Proletarian Cultural Revolution (1966-76): students and professionals sent to work and learn in the
countryside; reforms from 1978, first in agriculture, foreign trade and investment; commune land divided into plots
for individual households; Special Economic Zones to attract foreign investors. Pakistan: mixed economy with public
and private sectors; reforms from 1988; growth helped by the Green Revolution, mechanisation and remittances from
workers in the Middle East, but political instability and fluctuating growth. China introduced a one-child norm in
the late 1970s. China has grown fastest of the three and is ahead on human development indicators. Outside the book
(verified): the UN estimates India became the world's most populous country in 2023.
"""
CHAPTER = dict(num=14, title="Bharat aur Uske Padosi", kicker="ECONOMICS · CLASS 14 · NCERT CLASS 11", rain="🌏",
               outro_icons=("📘", "😊"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next class: Ramesh Singh Chapter 3 — Growth, Development, Happiness")

TOPICS = [
    dict(id="start", name="Same Start", label="1947 · 1949", icon="🏁"),
    dict(id="china", name="China's Path", label="Leap, revolution, reforms", icon="🇨🇳"),
    dict(id="pakistan", name="Pakistan's Path", label="Mixed economy, ups and downs", icon="🇵🇰"),
    dict(id="compare", name="Who Reached Where?", label="Growth & people", icon="📊"),
]

LINES = [
    ("hook", "[scene] दोस्तों, एक दौड़ सोचिए। तीन धावक — {भारत|India|🇮🇳}, {पाकिस्तान|Pakistan|🇵🇰}, और {चीन|China|🇨🇳}।"),
    (None, "तीनों ने, लगभग एक ही समय पर, दौड़ शुरू की।"),
    (None, "[punch] लेकिन रास्ते अलग चुने! तो आज कौन, कहाँ है?"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — तीनों की {एक जैसी शुरुआत|Same start|🏁}।"),
    (None, "दूसरा — {चीन का रास्ता|China's path|🇨🇳}, बड़ी छलाँग से सुधारों तक।"),
    (None, "तीसरा — {पाकिस्तान का रास्ता|Pakistan's path|🇵🇰}।"),
    (None, "और चौथा — आज, {कौन कहाँ पहुँचा|Who reached where?|📊}।"),

    ("center", "[name] क्लास चौदह — भारत और उसके पड़ोसी!"),
    ("topics", "चलिए — दौड़ की शुरुआती लाइन पर चलते हैं!"),

    ("focus:start", "[scene] भारत और पाकिस्तान — आज़ाद हुए {उन्नीस सौ सैंतालीस|1947|🕊️} में। और चीन में बना — {पीपल्स रिपब्लिक ऑफ़ चाइना|1949|🇨🇳}, उन्नीस सौ उनचास में।"),
    (None, "[punch] और तीनों ने चुनी — {पंचवर्षीय योजनाएँ|Five-Year Plans|📝}!"),
    (None, "भारत की पहली योजना — {उन्नीस सौ इक्यावन से छप्पन|India: 1951–56|🇮🇳}।"),
    (None, "चीन की पहली — {उन्नीस सौ तिरपन|China: 1953|🇨🇳}। और पाकिस्तान की पहली — {उन्नीस सौ छप्पन|Pakistan: 1956|🇵🇰}, जिसे अब कहते हैं — मीडियम टर्म डेवलपमेंट प्लान।"),

    ("focus:china", "[scene] {उन्नीस सौ अट्ठावन|1958|📅}। चीन शुरू करता है — {ग्रेट लीप फ़ॉरवर्ड|Great Leap Forward|🚀}। यानी एक बहुत बड़ी छलाँग!"),
    (None, "मक़सद — बहुत बड़े पैमाने पर, {तेज़ी से इंडस्ट्री|Rapid industrialisation|🏭}। लोगों से कहा गया — अपने {घर के पिछवाड़े|Backyard furnaces|🔥} में भी, उद्योग लगाओ!"),
    (None, "और गाँवों में — {कम्यून|Communes|👥}। यानी सब मिलकर, एक साथ खेती।"),
    (None, "[scene] फिर {उन्नीस सौ छियासठ से छिहत्तर|1966–76|📅} — {ग्रेट प्रोलेटेरियन कल्चरल रिवोल्यूशन|Cultural Revolution|🚩}। छात्रों और पढ़े-लिखे पेशेवरों को, गाँवों में भेजा गया — काम करने, और सीखने।"),
    (None, "[punch] और फिर — {उन्नीस सौ अठहत्तर|1978|🔓}। बड़े {सुधार|Reforms|🔧} शुरू!"),
    (None, "पहले खेती में — कम्यून की ज़मीन, छोटे-छोटे टुकड़ों में, {परिवारों को|Land to households|🏡} दी गई।"),
    (None, "फिर विदेशी व्यापार और निवेश। और विदेशी कंपनियों को बुलाने के लिए — {स्पेशल इकॉनॉमिक ज़ोन्स|SEZs|🏗️}।"),
    (None, "और आबादी पर लगाम के लिए, सत्तर के दशक के आख़िर में — {वन-चाइल्ड नॉर्म|One-child norm|👶}।"),

    ("focus:pakistan", "[scene] अब पाकिस्तान। उसने चुनी — {मिक्स्ड इकॉनमी|Mixed Economy|🤝}, सरकारी और प्राइवेट, दोनों सेक्टर के साथ।"),
    (None, "{ग्रीन रिवोल्यूशन|Green Revolution|🌾}, और खेती में मशीनें — इनसे कुछ बढ़त मिली।"),
    (None, "और बहुत मदद मिली — {मिडिल ईस्ट|Middle East remittances|✈️} में काम करने वाले पाकिस्तानियों के, घर भेजे गए पैसों से।"),
    (None, "{उन्नीस सौ अट्ठासी|1988|🔧} में, वहाँ भी सुधार शुरू हुए।"),
    (None, "[punch] लेकिन {राजनीतिक अस्थिरता|Political instability|⚠️} — और बढ़त, कभी ऊपर, कभी नीचे।"),

    ("focus:compare", "[scene] तो आज, दौड़ का नतीजा?"),
    (None, "[punch] बढ़त में सबसे आगे — {चीन|China: fastest growth|🥇}!"),
    (None, "और लोगों की ज़िंदगी — यानी {ह्यूमन डेवलपमेंट|Human Development|🏥} — में भी, चीन आगे।"),
    (None, "[scene] और एक नई बात — किताब से बाहर की। यू एन के अनुसार, {दो हज़ार तेईस|2023|📅} में — भारत, दुनिया का {सबसे ज़्यादा आबादी वाला देश|Most populous: India|🇮🇳} बन गया।"),
    (None, "[punch] यानी भारत के पास — सबसे बड़ी ताक़त भी, सबसे बड़ी चुनौती भी — {लोग|Log|👥}!"),

    ("recap", "[scene] तो याद रखिए —"),
    (None, "{उन्नीस सौ सैंतालीस, उनचास|1947 · 1949|🏁} — एक जैसी शुरुआत।"),
    (None, "{पहली योजनाएँ|1951 · 1953 · 1956|📝} — भारत, चीन, पाकिस्तान।"),
    (None, "{चीन|1958 · 1966 · 1978|🇨🇳} — छलाँग, कल्चरल रिवोल्यूशन, और सुधार।"),
    (None, "{पाकिस्तान|1988, remittances|🇵🇰} — और सबसे तेज़ बढ़त, {चीन की|China fastest|🥇}।"),

    ("outro:Next: Ramesh Singh Chapter 3", "[scene] दोस्तों — बढ़त, विकास, और ख़ुशी — क्या ये तीनों एक ही चीज़ हैं?"),
    (None, "[punch] रमेश सिंह का चैप्टर तीन — ग्रोथ, डेवलपमेंट और हैप्पीनेस — अगली क्लास में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
