"""Ch01 - Introduction to Economics: one full video for Ramesh Singh, Indian Economy (18e), Chapter 1,
with the related NCERT points explained where they fit.
DRAFT: built from chapter summaries of Ramesh Singh Ch 1 (micro and macro; production, consumption, distribution;
market, socialist, communist and mixed economies with features, merits and demerits; distribution systems; primary,
secondary, tertiary, quaternary and quinary sectors) plus standard facts. To be checked line by line against the
book pages (coverage table) before the video is made.
NCERT links: Class 12 Micro ch1 (scarcity, central problems, PPC/opportunity cost, positive vs normative, planned /
market / mixed), Class 9 ch1 (factors of production), Class 12 Macro ch1 (Great Depression 1929; US unemployment
about 3% -> 25% in 1929-33; Keynes 1936), Class 10 ch2 (sectors, final vs intermediate goods, GDP, shift to
services, disguised unemployment, organised vs unorganised, public vs private).
Standard facts: Adam Smith, The Wealth of Nations (1776); Karl Marx: "from each according to his ability, to each
according to his needs" (Critique of the Gotha Programme, 1875); Soviet Union after the 1917 revolution; People's
Republic of China 1949; India's Industrial Policy Resolution of 1956 gave the public sector a leading role.
Everyday numbers (₹100, chai) are illustrations.
"""
CHAPTER = dict(num=1, title="Introduction to Economics", kicker="RAMESH SINGH · CHAPTER 1 · + NCERT", rain="📘",
               video="Ch01 – Introduction to Economics",
               outro_icons=("💹", "🧮"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next: Chapter 2 — National Income")

TOPICS = [
    dict(id="what", name="What is Economics?", label="Wants many, means few", icon="📜"),
    dict(id="micromacro", name="Micro vs Macro", label="The tree and the forest", icon="🌳"),
    dict(id="capitalist", name="Market Economy", label="Capitalism", icon="🏦"),
    dict(id="socialist", name="Socialist & Communist", label="The state decides", icon="🏛️"),
    dict(id="mixed", name="Mixed Economy", label="India's middle path", icon="🤝"),
    dict(id="distribution", name="Distribution Systems", label="Who gets what?", icon="🍽️"),
    dict(id="sectors", name="Sectors of the Economy", label="Five floors of work", icon="🏢"),
]

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सोचिए — आपकी जेब में {सौ रुपये|₹100|💵} हैं।"),
    (None, "और सामने — एक {पिज़्ज़ा|Pizza|🍕}, एक {मूवी टिकट|Movie|🎬}, और एक नई {किताब|Kitaab|📖}। तीनों चाहिए — पैसा, सिर्फ़ एक के लायक़!"),
    (None, "[punch] आपको {चुनना पड़ेगा|Choice!|🤔}।"),
    (None, "और यही मुश्किल — एक घर की भी है, और {एक सौ चालीस करोड़ लोगों के देश|Poora desh|🇮🇳} की भी!"),
    (None, "[punch] इसी चुनाव की कहानी का नाम है — इकॉनॉमिक्स!"),

    # ---------------------------------------------------------------- today's class
    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {इकॉनॉमिक्स और इकॉनमी|Economics & Economy|📜} आख़िर हैं क्या, और {माइक्रो, मैक्रो|Micro · Macro|🌳} का फ़र्क़।"),
    (None, "दूसरा — दुनिया के {इकॉनॉमिक सिस्टम|Economic Systems|🏛️} — कैपिटलिस्ट, सोशलिस्ट, कम्युनिस्ट, और मिक्स्ड — उनके फ़ायदे और नुक़सान।"),
    (None, "तीसरा — हर सिस्टम में, {चीज़ें बँटती कैसे हैं|Distribution|🍽️}।"),
    (None, "और चौथा — इकॉनमी के {पाँच सेक्टर|5 Sectors|🏢}।"),

    ("center", "[name] रमेश सिंह, चैप्टर एक — इंट्रोडक्शन टू इकॉनॉमिक्स!"),
    ("topics", "चलिए — शुरुआत करते हैं, सत्रह सौ छिहत्तर से!"),

    # ---------------------------------------------------------------- 1. What is economics?
    ("focus:what", "[scene] {सत्रह सौ छिहत्तर|1776|📅}। स्कॉटलैंड के {एडम स्मिथ|Adam Smith|👴} ने लिखी एक किताब — {द वेल्थ ऑफ़ नेशन्स|The Wealth of Nations|📖}।"),
    (None, "सवाल था — कुछ देश अमीर, और कुछ गरीब — क्यों?"),
    (None, "[punch] इसी किताब से, एडम स्मिथ को कहा जाता है — {इकॉनॉमिक्स का पिता|Father of Economics|👑}!"),
    (None, "[name] {इकॉनॉमिक्स|Economics|📜} मतलब — सीमित साधनों से, अनगिनत ज़रूरतें, कैसे पूरी की जाएँ — इसका अध्ययन।"),
    (None, "और {इकॉनमी|Economy|🌐} मतलब — वो पूरा तंत्र, जिसमें एक देश, चीज़ें और सेवाएँ बनाता, बाँटता, और इस्तेमाल करता है।"),
    (None, "इसकी तीन बुनियादी गतिविधियाँ — {प्रोडक्शन|Production|🏭}, यानी बनाना। {कंज़म्प्शन|Consumption|🛒}, यानी इस्तेमाल करना। और {डिस्ट्रीब्यूशन|Distribution|🍽️}, यानी बाँटना।"),
    (None, "[scene] अब एन सी ई आर टी की एक ज़रूरी बात। साधन {सीमित|Limited|🔒} हैं — और ज़रूरतें {अनगिनत|Unlimited|♾️}।"),
    (None, "[name] इसे कहते हैं — {स्कार्सिटी|Scarcity|⏳}। यानी — जितना चाहिए, उतना है ही नहीं।"),
    (None, "इसलिए हर देश को, तीन सवालों के जवाब देने पड़ते हैं — {क्या बनाएँ|What?|🍞}, {कैसे बनाएँ|How?|⚙️}, और {किसके लिए बनाएँ|For whom?|👨‍👩‍👧}।"),
    (None, "[scene] और बनाने के लिए चाहिए — {चार चीज़ें|Factors of Production|🧩}। चाय की दुकान याद कीजिए!"),
    (None, "{ज़मीन|Land|🏞️} — दुकान की जगह। {लेबर|Labour|👷} — चाय वाले भैया की मेहनत। {फ़िज़िकल कैपिटल|Physical Capital|🛠️} — चूल्हा, बर्तन, और दूध-चाय पत्ती। और {ह्यूमन कैपिटल|Human Capital|🧠} — चाय बनाने का हुनर, और दुकान खोलने की हिम्मत।"),
    ("ex:", "और जो छोड़ना पड़ा — उसकी क़ीमत! पिज़्ज़ा लिया, तो मूवी छूटी — यही है {ऑपर्च्युनिटी कॉस्ट|Opportunity Cost|⚖️}।"),

    # ---------------------------------------------------------------- 2. Micro vs macro
    ("focus:micromacro", "[scene] इकॉनॉमिक्स को देखने की, दो नज़रें हैं। एक {पेड़|Ek ped|🌳} देखिए — और फिर, {पूरा जंगल|Poora jungle|🌲}।"),
    (None, "[name] {माइक्रोइकॉनॉमिक्स|Microeconomics|🔬} — एक पेड़। यानी एक ग्राहक, एक फ़र्म, एक बाज़ार। जैसे — आलू का दाम कैसे तय हुआ।"),
    (None, "[name] {मैक्रोइकॉनॉमिक्स|Macroeconomics|🌏} — पूरा जंगल। यानी पूरे देश का कुल उत्पादन, कुल रोज़गार, और सारे दामों का स्तर — जैसे महँगाई।"),
    (None, "[scene] और मैक्रो का जन्म हुआ — एक बड़े संकट से। {उन्नीस सौ उनतीस|1929|📉} — {ग्रेट डिप्रेशन|Great Depression|🏚️}!"),
    (None, "अमेरिका में, उन्नीस सौ उनतीस से तैंतीस के बीच — बेरोज़गारी, क़रीब {तीन से पच्चीस प्रतिशत|3% → 25%|📈} तक पहुँच गई!"),
    (None, "फिर {उन्नीस सौ छत्तीस|1936|📖} में, {कीन्स|J. M. Keynes|🎩} ने पूरी इकॉनमी को, एक साथ देखना सिखाया। यहीं से बनी, आज की मैक्रोइकॉनॉमिक्स।"),
    ("ex:", "एक और जोड़ी — {पॉज़िटिव|Positive|🔍}, यानी चीज़ें कैसे काम करती हैं। और {नॉर्मेटिव|Normative|⚖️}, यानी क्या होना चाहिए।"),

    # ---------------------------------------------------------------- 3. Market economy
    ("focus:capitalist", "[scene] अब सबसे बड़ा सवाल — क्या, कैसे, और किसके लिए — ये फ़ैसले लेता कौन है? दुनिया ने इसके, अलग-अलग जवाब दिए। इन्हें कहते हैं — इकॉनॉमिक सिस्टम।"),
    (None, "[name] पहला — {कैपिटलिस्ट इकॉनमी|Capitalist / Market Economy|🏦}। यानी बाज़ार वाली इकॉनमी।"),
    (None, "इसकी पहचान — कारख़ाने, ज़मीन, दुकानें — {निजी मालिकों|Private property|🔑} के हाथ में। मक़सद — {मुनाफ़ा|Profit motive|💰}।"),
    (None, "और फ़ैसले करता है — {दाम|Price mechanism|🏷️}। जिस चीज़ की माँग ज़्यादा, उसका दाम बढ़ा — और बनाने वालों को इशारा मिला — इसे और बनाओ!"),
    (None, "ग्राहक जो चाहे, वही बिकेगा — इसे कहते हैं {कंज़्यूमर सॉवरेन्टी|Consumer sovereignty|👑}, यानी ग्राहक राजा। और बेचने वालों में {मुक़ाबला|Competition|🏁}।"),
    (None, "सरकार कम से कम दख़ल दे — इसे कहते हैं {लेसे-फ़ेयर|Laissez-faire|🕊️}। यानी — होने दो, जो हो रहा है।"),
    (None, "[scene] {फ़ायदे|Advantages|✅} — मुक़ाबले से अच्छा माल, नई खोजें, ज़्यादा विकल्प, और तेज़ बढ़त।"),
    (None, "[scene] {नुक़सान|Disadvantages|❌} — अमीर और गरीब के बीच, बड़ी खाई।"),
    (None, "गरीब की ज़रूरत पर ध्यान नहीं — क्योंकि उसके पास, ख़रीदने का पैसा नहीं। सड़क, स्कूल जैसे काम, जिनमें मुनाफ़ा कम — पीछे छूट जाते हैं।"),
    (None, "[punch] और कभी-कभी, बड़ा झटका — जैसे उन्नीस सौ उनतीस की ग्रेट डिप्रेशन!"),

    # ---------------------------------------------------------------- 4. Socialist and communist
    ("focus:socialist", "[scene] अब दूसरा रास्ता — {सोशलिस्ट इकॉनमी|Socialist Economy|🏛️}।"),
    (None, "यहाँ बड़े कारख़ानों, खदानों, बैंकों की मालिक — {सरकार|State ownership|🏛️}। और फ़ैसले होते हैं — {सेंट्रल प्लानिंग|Central planning|📝} से।"),
    (None, "मक़सद — मुनाफ़ा नहीं, बल्कि {सबकी भलाई|Welfare|❤️}, और {बराबरी|Equality|⚖️}।"),
    (None, "[scene] {फ़ायदे|Advantages|✅} — अमीर-गरीब की खाई कम। सबके लिए बुनियादी ज़रूरतें — खाना, घर, इलाज, पढ़ाई। और सरकार, ज़रूरी कामों को, पहले रख सकती है।"),
    (None, "[scene] {नुक़सान|Disadvantages|❌} — मेहनत का अलग इनाम नहीं — तो {जोश कम|Low incentive|😴}।"),
    (None, "सारे फ़ैसले ऊपर से — तो {लालफ़ीताशाही|Bureaucracy|📎}, धीमा काम, कम विकल्प, और कम नई खोजें।"),
    (None, "[scene] और {कम्युनिस्ट इकॉनमी|Communist Economy|🚩}? ये इस सोच का, सबसे आख़िरी रूप है।"),
    (None, "[name] {कार्ल मार्क्स|Karl Marx|🧔} का सपना — {निजी संपत्ति ख़त्म|No private property|🚫}, और एक बिना वर्गों का समाज। और उनका मशहूर वाक्य —"),
    (None, "[punch] {हर किसी से उसकी क्षमता के हिसाब से, हर किसी को उसकी ज़रूरत के हिसाब से|From each by ability, to each by needs|🤲}!"),
    (None, "सोशलिज़्म में — थोड़ी निजी संपत्ति, और {काम के हिसाब से इनाम|Reward by work|💵} चल सकता है। कम्युनिज़्म के आदर्श में — सब कुछ साझा, और बँटवारा, {ज़रूरत के हिसाब से|Reward by need|🤲}।"),
    (None, "[scene] असल दुनिया में — {उन्नीस सौ सत्रह|1917|🚩} की क्रांति के बाद का सोवियत संघ, और {उन्नीस सौ उनचास|1949|🇨🇳} के बाद का चीन — इसी रास्ते पर चले।"),

    # ---------------------------------------------------------------- 5. Mixed economy
    ("focus:mixed", "[scene] अब सोचिए — अगर दोनों की अच्छी बातें, एक साथ मिल जाएँ?"),
    (None, "[name] यही है — {मिक्स्ड इकॉनमी|Mixed Economy|🤝}। बाज़ार भी, और सरकार भी।"),
    (None, "मुनाफ़े वाले ज़्यादातर काम — {प्राइवेट सेक्टर|Private sector|🏢} के हाथ में। और ज़रूरी, बड़े, या भलाई वाले काम — जैसे रेल, बिजली, गरीबों के लिए राशन — {सरकार|Public sector|🏛️} के हाथ में। साथ में, सरकार {नियम|Regulation|📏} भी बनाती है।"),
    (None, "ग्रेट डिप्रेशन के बाद, और कीन्स की सोच से — दुनिया के ज़्यादातर देश, इसी रास्ते पर आ गए।"),
    (None, "[punch] एन सी ई आर टी तो यहाँ तक कहती है — असल में, सारी इकॉनमी मिक्स्ड हैं। फ़र्क़ बस इतना — सरकार का रोल, {कितना बड़ा|How big is the state?|📐} है।"),
    (None, "[scene] {फ़ायदे|Advantages|✅} — बाज़ार की रफ़्तार, और सरकार का सहारा, एक साथ। बढ़त भी, और भलाई भी।"),
    (None, "[scene] {नुक़सान|Disadvantages|❌} — कभी-कभी, दोनों की कमज़ोरियाँ भी साथ आ जाती हैं। सरकारी कंपनियों में {घाटा|Losses|📉}, और फ़ैसलों में {देरी|Delays|⏳}।"),
    (None, "[scene] और भारत? आज़ादी के बाद, भारत ने चुनी — {प्लानिंग के साथ मिक्स्ड इकॉनमी|India: Mixed + Planning|🇮🇳}।"),
    (None, "{उन्नीस सौ छप्पन|IPR 1956|📜} के इंडस्ट्रियल पॉलिसी रेज़ोल्यूशन ने, बड़े उद्योगों में — {पब्लिक सेक्टर|Public sector lead|🏭} को, आगे की भूमिका दी।"),
    (None, "[punch] ये भारत का सफ़र, हम आगे — चैप्टर चार से सात में, पूरा देखेंगे!"),

    # ---------------------------------------------------------------- 6. Distribution
    ("focus:distribution", "[scene] अब सवाल — जो बना, वो बँटा कैसे? हर सिस्टम का, अपना {बँटवारे का तरीक़ा|Distribution system|🍽️} है।"),
    (None, "[name] कैपिटलिस्ट सिस्टम में — {बाज़ार|By market price|🏷️} बाँटता है। जिसके पास ख़रीदने की ताक़त, उसे मिलता है।"),
    (None, "[name] स्टेट, यानी सोशलिस्ट सिस्टम में — {सरकार|By the state|🏛️} तय करती है, किसे कितना मिले — जैसे राशन।"),
    (None, "[name] और मिक्स्ड सिस्टम में — {दोनों|Market + Welfare|🤝}। ज़्यादातर चीज़ें बाज़ार से। लेकिन गरीबों के लिए — {सस्ता राशन|PDS|🍚}, और {सब्सिडी|Subsidy|🎁}।"),
    ("ex:", "जैसे भारत में — मोबाइल फ़ोन, बाज़ार से। और राशन की दुकान का अनाज — सरकार की मदद से!"),

    # ---------------------------------------------------------------- 7. Sectors
    ("focus:sectors", "[scene] आख़िर में — इकॉनमी को, एक पाँच मंज़िला इमारत की तरह देखिए।"),
    (None, "[name] पहली मंज़िल — {प्राइमरी सेक्टर|Primary|🌾}। कुदरत से सीधे लेना — {खेती|Kheti|🌱}, {डेयरी|Dairy|🐄}, {मछली|Fishing|🎣}, {जंगल|Forestry|🌳}, और {खदानें|Mining|⛏️}।"),
    (None, "[name] दूसरी — {सेकेंडरी सेक्टर|Secondary|🏭}। कुदरती चीज़ों से, नई चीज़ बनाना। {कपास से कपड़ा|Kapas → Kapda|👕}, {गन्ने से चीनी|Ganna → Cheeni|🍬}।"),
    (None, "[name] तीसरी — {टर्शियरी सेक्टर|Tertiary|🚚}। सेवाएँ — {ट्रांसपोर्ट|Transport|🚛}, {बैंक|Bank|🏦}, {व्यापार|Trade|🛒}, {टीचर, डॉक्टर|Teacher · Doctor|👩‍⚕️}।"),
    (None, "[name] चौथी — {क्वाटर्नरी सेक्टर|Quaternary|💡}। ज्ञान का काम — {रिसर्च|Research|🔬}, {आईटी|IT|💻}, {शिक्षा|Education|🎓}।"),
    (None, "[name] और पाँचवीं — {क्विनरी सेक्टर|Quinary|🎯}। सबसे ऊँचे फ़ैसले लेने वाले — बड़े अफ़सर, और बड़ी कंपनियों के मुखिया।"),
    (None, "कई किताबें, आख़िरी दोनों को — टर्शियरी का ही हिस्सा मानती हैं।"),
    (None, "[scene] अब एन सी ई आर टी की बातें, जो यहाँ जुड़ती हैं। गिनती में, सिर्फ़ {फ़ाइनल गुड्स|Final goods|🍪} जोड़े जाते हैं — बीच की चीज़ें नहीं, वरना {डबल काउंटिंग|Double counting|⚠️}।"),
    (None, "[name] एक साल में, देश के अंदर बने, सारे फ़ाइनल गुड्स और सर्विसेज़ की क़ीमत — {जीडीपी|GDP|🧮}। इसकी पूरी कहानी — चैप्टर दो में!"),
    (None, "[punch] और भारत में — उत्पादन में, {सर्विस सेक्टर|Services No. 1|🥇} सबसे आगे। लेकिन आज भी, {सबसे ज़्यादा लोग|Most workers: Primary|👨‍🌾} — प्राइमरी सेक्टर में काम करते हैं।"),
    (None, "छोटे खेत पर, ज़रूरत से ज़्यादा लोग — सब काम में दिखते हैं, पर पूरा काम किसी के पास नहीं। ये है {छुपी हुई बेरोज़गारी|Disguised Unemployment|🙈}।"),
    (None, "नौकरियाँ भी दो तरह की — {संगठित|Organised|📋}, जहाँ पक्की नौकरी, छुट्टी, और पी एफ़। और {असंगठित|Unorganised|🧺}, जहाँ कोई गारंटी नहीं।"),
    (None, "और मालिक के हिसाब से — {पब्लिक सेक्टर|Public|🏛️}, जैसे रेलवे। और {प्राइवेट सेक्टर|Private|🏢}, जैसे बड़ी निजी कंपनियाँ।"),

    # ---------------------------------------------------------------- recap
    ("recap", "[scene] तो याद रखिए —"),
    (None, "{इकॉनॉमिक्स|Scarcity & Choice|📜} — सीमित साधन, अनगिनत ज़रूरतें। और एडम स्मिथ, सत्रह सौ छिहत्तर।"),
    (None, "{माइक्रो और मैक्रो|Micro & Macro|🌳} — पेड़ और जंगल। ग्रेट डिप्रेशन, और कीन्स।"),
    (None, "{चार सिस्टम|Capitalist · Socialist · Communist · Mixed|🏛️} — और हर एक के, फ़ायदे और नुक़सान।"),
    (None, "{भारत|India: Mixed Economy|🇮🇳} — प्लानिंग के साथ, मिक्स्ड इकॉनमी।"),
    (None, "{बँटवारा|Market · State · Mixed|🍽️}, और {पाँच सेक्टर|5 Sectors|🏢}।"),

    # ---------------------------------------------------------------- next + channel
    ("outro:Next: Chapter 2 — National Income", "[scene] लेकिन दोस्तों — पाँचों सेक्टर मिलकर, पूरे साल में, देश ने कितना कमाया? ये गिनते कैसे हैं?"),
    (None, "[punch] रमेश सिंह, चैप्टर दो — नेशनल इनकम! अगले वीडियो में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
