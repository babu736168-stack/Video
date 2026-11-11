"""Ch01 - Introduction to Economics: one full, detailed video for Ramesh Singh, Indian Economy (18e), Chapter 1 only
(no NCERT add-ins, at the user's request). Added after the user said points were missing: economic agents;
capitalism's failure in the Great Depression -> mixed economy; the Washington Consensus (term by John Williamson, 1989;
IMF, World Bank, US Treasury; first for Latin America's debt crises; ten policies incl. fiscal discipline, tax reform,
trade liberalisation, openness to FDI, privatisation, deregulation, property rights; criticised as one-size-fits-all,
more so after the 2008 crisis), the Beijing Consensus (term by Joshua Cooper Ramo, 2004: experimentation, gradual
reform, strong state role, selective adoption of foreign ideas) and the Santiago Consensus (social inclusion, local
development; details to check against the book).
DRAFT: the chapter's topic list is from chapter summaries of Ramesh Singh Ch 1 (definitions; micro and macro;
production, consumption, distribution; capitalist / market, socialist, communist and mixed economies with features,
merits and demerits; distribution systems; primary, secondary, tertiary, quaternary, quinary sectors). The detail is
from standard facts. To be checked line by line against the book pages (coverage table) before the video is made.
Standard facts: Adam Smith, The Wealth of Nations (1776), wealth definition, "invisible hand"; Alfred Marshall,
Principles of Economics (1890), welfare definition ("a study of mankind in the ordinary business of life"); Lionel
Robbins, An Essay on the Nature and Significance of Economic Science (1932), scarcity definition (human behaviour as a
relationship between ends and scarce means which have alternative uses); Ragnar Frisch is credited with the terms
micro- and macro-economics (1933); Great Depression from 1929; J. M. Keynes, The General Theory (1936); Industrial
Revolution in 18th-century Britain; Russian Revolution 1917, USSR formed 1922, first Soviet Five-Year Plan 1928;
People's Republic of China 1949, China's reforms from 1978; fall of the Berlin Wall 1989; dissolution of the USSR
1991; India's 1991 reforms moved the economy towards the market; WTO set up in 1995. Distinction often drawn
(check against the book): in a socialist state economy the state controls property (means of production); in a
communist one the state controls both property and labour. Marx's slogan "from each according to his ability, to
each according to his needs" (1875). India's Industrial Policy Resolution of 1956 gave the public sector the lead in
basic and heavy industry. Everyday examples (₹100, chai, mobile phone) are illustrations.
"""
CHAPTER = dict(num=1, title="Introduction to Economics", kicker="RAMESH SINGH · CHAPTER 1", rain="📘",
               video="Ch01 – Introduction to Economics",
               outro_icons=("💹", "🧮"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               next_title="Next: Chapter 2 — National Income")

TOPICS = [
    dict(id="defs", name="What is Economics?", label="Three famous definitions", icon="📜"),
    dict(id="economy", name="Economy & Micro-Macro", label="The tree and the forest", icon="🌳"),
    dict(id="capitalist", name="Capitalist Economy", label="The market decides", icon="🏦"),
    dict(id="state", name="State Economy", label="Socialist & communist", icon="🏛️"),
    dict(id="mixed", name="Mixed Economy", label="The middle path", icon="🤝"),
    dict(id="world", name="How the World Changed", label="1929 → 1991 → today", icon="🌍"),
    dict(id="consensus", name="Three Consensuses", label="Washington · Beijing · Santiago", icon="🧭"),
    dict(id="distribution", name="Distribution Systems", label="Who gets what?", icon="🍽️"),
    dict(id="sectors", name="Sectors of the Economy", label="Five floors of work", icon="🏢"),
]

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सोचिए — आपकी जेब में {सौ रुपये|₹100|💵} हैं।"),
    (None, "और सामने — एक {पिज़्ज़ा|Pizza|🍕}, एक {मूवी टिकट|Movie|🎬}, और एक नई {किताब|Kitaab|📖}। तीनों चाहिए — पैसा, सिर्फ़ एक के लायक़!"),
    (None, "[punch] आपको {चुनना पड़ेगा|Choice!|🤔}।"),
    (None, "अब यही सवाल, एक {पूरे देश|Poora desh|🇮🇳} के सामने रखिए। अनाज बनाएँ या हथियार? स्कूल या सड़कें? और ये फ़ैसला — लेगा कौन? बाज़ार, या सरकार?"),
    (None, "[punch] इन्हीं सवालों से शुरू होता है — इकॉनॉमिक्स!"),

    # ---------------------------------------------------------------- today's class
    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {इकॉनॉमिक्स की परिभाषाएँ|Definitions|📜}, इकॉनमी, और {माइक्रो-मैक्रो|Micro · Macro|🌳}।"),
    (None, "दूसरा — {तीन इकॉनॉमिक सिस्टम|3 Economic Systems|🏛️}, उनकी ख़ूबियाँ, और कमियाँ।"),
    (None, "तीसरा — सत्रह सौ छिहत्तर से आज तक, {दुनिया कैसे बदली|World · 3 Consensuses|🌍} — वॉशिंगटन, बीजिंग, और सैंटियागो कंसेंसस — और हर सिस्टम में, बँटवारा।"),
    (None, "और चौथा — इकॉनमी के {पाँच सेक्टर|5 Sectors|🏢}।"),

    ("center", "[name] रमेश सिंह, चैप्टर एक — इंट्रोडक्शन टू इकॉनॉमिक्स!"),
    ("topics", "चलिए — शुरुआत करते हैं, तीन मशहूर परिभाषाओं से!"),

    # ---------------------------------------------------------------- 1. Definitions
    ("focus:defs", "[scene] {सत्रह सौ छिहत्तर|1776|📅}। स्कॉटलैंड के {एडम स्मिथ|Adam Smith|👴} ने लिखी — {द वेल्थ ऑफ़ नेशन्स|The Wealth of Nations|📖}।"),
    (None, "पूरा नाम — एन इंक्वायरी इनटू द नेचर एंड कॉज़ेज़ ऑफ़ द वेल्थ ऑफ़ नेशन्स। यानी — देशों की दौलत का स्वभाव, और उसके कारण।"),
    (None, "[name] स्मिथ के लिए इकॉनॉमिक्स था — {दौलत का विज्ञान|Science of Wealth|💰}। इसीलिए उन्हें कहा जाता है — {इकॉनॉमिक्स का पिता|Father of Economics|👑}।"),
    (None, "[scene] लेकिन सवाल उठा — क्या दौलत ही सब कुछ है? इंसान का क्या?"),
    (None, "{अट्ठारह सौ नब्बे|1890|📅}। {अल्फ़्रेड मार्शल|Alfred Marshall|🎓} की किताब — {प्रिंसिपल्स ऑफ़ इकॉनॉमिक्स|Principles of Economics|📘}।"),
    (None, "[name] मार्शल ने कहा — इकॉनॉमिक्स है, {रोज़मर्रा की ज़िंदगी में इंसान का अध्ययन|Study of mankind|🧍}। यानी केंद्र में दौलत नहीं — {इंसान की भलाई|Welfare|❤️}।"),
    (None, "[scene] फिर {उन्नीस सौ बत्तीस|1932|📅}। {लायनल रॉबिन्स|Lionel Robbins|🧐} ने, सबसे मशहूर परिभाषा दी।"),
    (None, "[name] इकॉनॉमिक्स वो विज्ञान है, जो इंसान के व्यवहार को पढ़ता है — {लक्ष्यों|Ends|🎯} और {सीमित साधनों|Scarce means|🔒} के बीच के रिश्ते के रूप में — जिन साधनों के, {कई इस्तेमाल|Alternative uses|🔀} हो सकते हैं।"),
    ("ex:", "आपके सौ रुपये — {सीमित साधन|₹100 = scarce means|💵}। पिज़्ज़ा, मूवी, किताब — {कई लक्ष्य|Many ends|🎯}। और सौ रुपये, तीनों में से किसी पर भी ख़र्च हो सकते हैं — यही {कई इस्तेमाल|Alternative uses|🔀}!"),
    (None, "[punch] यानी — दौलत से शुरू हुई कहानी, भलाई से होती हुई, {चुनाव|Choice|🤔} तक पहुँची!"),

    # ---------------------------------------------------------------- 2. Economy, micro and macro
    ("focus:economy", "[scene] अब {इकॉनमी|Economy|🌐} क्या है? एक देश का वो पूरा तंत्र, जिसमें चीज़ें और सेवाएँ — बनती हैं, बँटती हैं, और इस्तेमाल होती हैं।"),
    (None, "[name] इसकी तीन बुनियादी गतिविधियाँ — {प्रोडक्शन|Production|🏭}, यानी बनाना।"),
    (None, "{कंज़म्प्शन|Consumption|🛒}, यानी इस्तेमाल करना।"),
    (None, "और {डिस्ट्रीब्यूशन|Distribution|🍽️}, यानी बाँटना — कौन, कितना पाए।"),
    ("ex:", "जैसे चाय — किसान ने पत्ती उगाई, फ़ैक्टरी ने पैक की — ये प्रोडक्शन। दुकान से आप तक पहुँची — ये डिस्ट्रीब्यूशन। और आपने पी — ये कंज़म्प्शन!"),
    (None, "[scene] अब इकॉनमी को पढ़ने की, दो नज़रें। {उन्नीस सौ तैंतीस|1933|📅} में, नॉर्वे के {रैगनर फ़्रिश|Ragnar Frisch|🎓} ने, इन्हें दो नाम दिए।"),
    (None, "[name] {माइक्रोइकॉनॉमिक्स|Microeconomics|🔬} — एक पेड़। यानी अलग-अलग {इकॉनॉमिक एजेंट्स|Economic agents|👥} — जैसे एक ग्राहक, एक कंपनी, एक बाज़ार। जैसे — प्याज़ का दाम कैसे तय हुआ, या एक कंपनी कितना बनाए।"),
    (None, "[name] {मैक्रोइकॉनॉमिक्स|Macroeconomics|🌏} — पूरा जंगल। यानी पूरे देश का {कुल उत्पादन|Total output|🏭}, {रोज़गार|Employment|👷}, {महँगाई|Inflation|🔥}, और {विकास दर|Growth rate|📈}।"),
    (None, "[punch] और याद रखिए — दोनों अलग नहीं। हज़ारों पेड़ मिलकर ही, जंगल बनाते हैं!"),

    # ---------------------------------------------------------------- 3. Capitalist economy
    ("focus:capitalist", "[scene] अब सबसे बड़ा सवाल — क्या बने, कैसे बने, किसे मिले — ये फ़ैसले लेता कौन है? इसके जवाब से बनते हैं — {इकॉनॉमिक सिस्टम|Economic Systems|🏛️}।"),
    (None, "[name] पहला — {कैपिटलिस्ट इकॉनमी|Capitalist Economy|🏦}। इसे {मार्केट इकॉनमी|Market Economy|🏪} भी कहते हैं।"),
    (None, "इसकी जड़ें — एडम स्मिथ के विचारों, और अट्ठारहवीं सदी के ब्रिटेन की {औद्योगिक क्रांति|Industrial Revolution|🏭} में।"),
    (None, "[scene] इसकी पहचान, एक-एक करके देखिए। पहली — {निजी संपत्ति|Private property|🔑}। कारख़ाने, ज़मीन, दुकानें — लोगों और कंपनियों की।"),
    (None, "दूसरी — {मुनाफ़े का मक़सद|Profit motive|💰}। कोई भी काम, मुनाफ़े के लिए।"),
    (None, "तीसरी — {दाम का तंत्र|Price mechanism|🏷️}। क्या बने, कितना बने — ये बाज़ार के दाम तय करते हैं।"),
    ("ex:", "जैसे — किसी फ़ोन की माँग बढ़ी, तो उसका दाम बढ़ा — और कंपनियों को इशारा मिला: इसे और बनाओ! एडम स्मिथ ने इसे कहा — {अदृश्य हाथ|Invisible Hand|🫳}।"),
    (None, "चौथी — {ग्राहक राजा|Consumer sovereignty|👑}। जो ग्राहक चाहे, वही बिकेगा।"),
    (None, "पाँचवीं — {मुक़ाबला|Competition|🏁}। बेचने वाले, एक-दूसरे से आगे निकलने की होड़ में।"),
    (None, "और छठी — सरकार का दख़ल, कम से कम। इसे कहते हैं — {लेसे-फ़ेयर|Laissez-faire|🕊️}। यानी — होने दो।"),
    (None, "[scene] {ख़ूबियाँ|Merits|✅} — मुक़ाबले से, बेहतर और सस्ता माल।"),
    (None, "मुनाफ़े की चाह से — {नई खोजें|Innovation|💡}, और तेज़ बढ़त। और ग्राहक के लिए — ढेरों विकल्प।"),
    (None, "[scene] {कमियाँ|Demerits|❌} — अमीर और गरीब के बीच, {गहरी खाई|Inequality|⚖️}।"),
    (None, "बाज़ार सुनता है पैसे की आवाज़ — इसलिए गरीब की ज़रूरत, अक्सर {अनसुनी|Poor are ignored|🙉}।"),
    (None, "जिन कामों में मुनाफ़ा कम — जैसे गाँव की सड़क, या मुफ़्त इलाज — वो {पीछे छूट|Public needs neglected|🛣️} जाते हैं।"),
    (None, "कुछ बड़ी कंपनियाँ, पूरे बाज़ार पर {क़ब्ज़ा|Monopoly|👑} कर सकती हैं।"),
    (None, "[punch] और कभी-कभी — {बड़ी मंदी|Depression|📉}, जब कारख़ाने बंद, और लाखों बेरोज़गार!"),

    # ---------------------------------------------------------------- 4. State economy
    ("focus:state", "[scene] अब दूसरा रास्ता — {स्टेट इकॉनमी|State Economy|🏛️}। जहाँ फ़ैसले, सरकार लेती है।"),
    (None, "[scene] {उन्नीस सौ सत्रह|1917|🚩}। रूस में क्रांति। और {उन्नीस सौ बाईस|1922|📅} में बना — {सोवियत संघ|USSR|🚩}।"),
    (None, "{उन्नीस सौ अट्ठाईस|1928|📝} में, वहाँ शुरू हुई — पहली {पंचवर्षीय योजना|Five-Year Plan|📝}। यानी पूरे देश की इकॉनमी, एक योजना से!"),
    (None, "[name] इस सोच के, दो रूप हैं — {सोशलिस्ट|Socialist|🏛️}, और {कम्युनिस्ट|Communist|🚩}।"),
    (None, "सोशलिस्ट सिस्टम में — बड़े कारख़ानों, खदानों, बैंकों जैसे {उत्पादन के साधनों|Means of production|🏭} की मालिक, सरकार। मक़सद — {सबकी भलाई|Welfare|❤️}, और {बराबरी|Equality|⚖️}।"),
    (None, "और कम्युनिस्ट सिस्टम में — सरकार का कंट्रोल, और भी आगे। अक्सर कहा जाता है — यहाँ {संपत्ति के साथ, लोगों की मेहनत भी|Property + Labour|👷} सरकार के कंट्रोल में।"),
    (None, "[name] इसके पीछे थे — {कार्ल मार्क्स|Karl Marx|🧔} के विचार। उनका सपना — {बिना वर्गों का समाज|Classless society|🤲}, और ये मशहूर वाक्य —"),
    (None, "[punch] {हर किसी से उसकी क्षमता के हिसाब से, हर किसी को उसकी ज़रूरत के हिसाब से|From each by ability, to each by needs|🤲}!"),
    (None, "[scene] {उन्नीस सौ उनचास|1949|🇨🇳} में चीन, और दूसरे विश्व युद्ध के बाद, पूर्वी यूरोप के कई देश — इसी रास्ते पर चले।"),
    (None, "[scene] {ख़ूबियाँ|Merits|✅} — अमीर-गरीब की खाई कम।"),
    (None, "सबके लिए {बुनियादी ज़रूरतें|Basic needs|🍚} — खाना, घर, इलाज, पढ़ाई। और सरकार, देश की ज़रूरी चीज़ों को — जैसे भारी उद्योग — पहले रख सकती है।"),
    (None, "[scene] {कमियाँ|Demerits|❌} — मेहनत करो या न करो, इनाम लगभग बराबर — तो {जोश कम|Low incentive|😴}।"),
    (None, "सारे फ़ैसले ऊपर से — तो {लालफ़ीताशाही|Bureaucracy|📎}, और धीमा काम।"),
    (None, "ग्राहक के लिए — {कम विकल्प|Less choice|🚫}। और नई खोजें भी, कम।"),
    (None, "[punch] और कई देशों में — लोगों की {आज़ादी|Freedom|🕊️} पर भी पाबंदियाँ।"),

    # ---------------------------------------------------------------- 5. Mixed economy
    ("focus:mixed", "[scene] अब सोचिए — अगर दोनों रास्तों की, अच्छी बातें मिला दें?"),
    (None, "[name] यही है — {मिक्स्ड इकॉनमी|Mixed Economy|🤝}। बाज़ार भी, और सरकार भी — एक साथ।"),
    (None, "इसकी पहचान — {प्राइवेट सेक्टर|Private sector|🏢} और {पब्लिक सेक्टर|Public sector|🏛️}, दोनों साथ-साथ।"),
    (None, "मुनाफ़े वाले ज़्यादातर काम — प्राइवेट सेक्टर के हाथ में। और ज़रूरी, बड़े, या भलाई वाले काम — जैसे रेल, बिजली, बाँध, गरीबों के लिए राशन — सरकार के हाथ में।"),
    (None, "और बाज़ार ठीक से चले, किसी के साथ ग़लत न हो — इसके लिए सरकार बनाती है, {नियम|Regulation|📏}।"),
    (None, "[scene] ये रास्ता मज़बूत हुआ — उन्नीस सौ उनतीस की {ग्रेट डिप्रेशन|Great Depression|🏚️} के बाद। जब अकेला बाज़ार — यानी शुद्ध कैपिटलिज़्म — {नाकाम|Capitalism failed|💥} दिखा।"),
    (None, "{उन्नीस सौ छत्तीस|1936|📖} में, {जॉन मेनार्ड कीन्स|J. M. Keynes|🎩} ने कहा — मुश्किल वक़्त में, सरकार को, ख़र्च करके आगे आना चाहिए।"),
    (None, "[scene] {ख़ूबियाँ|Merits|✅} — बाज़ार की रफ़्तार, और सरकार का सहारा — एक साथ। बढ़त भी, और भलाई भी।"),
    (None, "[scene] {कमियाँ|Demerits|❌} — कभी-कभी दोनों की कमज़ोरियाँ भी, साथ आ जाती हैं। सरकारी कंपनियों में {घाटा|Losses|📉}, फ़ैसलों में {देरी|Delays|⏳}, और {भ्रष्टाचार|Corruption|🕳️} का ख़तरा।"),
    (None, "[scene] और भारत? आज़ादी के बाद, भारत ने चुना — {प्लानिंग के साथ, मिक्स्ड इकॉनमी|India: Mixed + Planning|🇮🇳}।"),
    (None, "{उन्नीस सौ छप्पन|IPR 1956|📜} के इंडस्ट्रियल पॉलिसी रेज़ोल्यूशन ने — बुनियादी और भारी उद्योगों में, {पब्लिक सेक्टर|Public sector lead|🏭} को आगे रखा।"),
    (None, "[punch] और {उन्नीस सौ इक्यानवे|1991|🔓} के सुधारों के बाद — भारत, धीरे-धीरे, {बाज़ार की ओर|Towards the market|➡️} बढ़ा। ये पूरी कहानी — चैप्टर चार से सात में!"),

    # ---------------------------------------------------------------- 6. How the world changed
    ("focus:world", "[scene] अब इन तीनों सिस्टम्स की, पूरी दौड़ देखिए — एक नक्शे पर।"),
    (None, "{सत्रह सौ छिहत्तर|1776|📖} — एडम स्मिथ, और बाज़ार का दौर।"),
    (None, "{उन्नीस सौ सत्रह|1917|🚩} — रूस की क्रांति, और स्टेट इकॉनमी का जन्म।"),
    (None, "{उन्नीस सौ उनतीस|1929|📉} — ग्रेट डिप्रेशन। बाज़ार पर से, भरोसा हिला।"),
    (None, "{उन्नीस सौ छत्तीस|1936|🎩} — कीन्स। मिक्स्ड इकॉनमी की राह।"),
    (None, "[scene] और फिर, उल्टी हवा। {उन्नीस सौ अठहत्तर|1978|🇨🇳} — चीन में, बाज़ार वाले सुधार शुरू।"),
    (None, "{उन्नीस सौ नवासी|1989|🧱} — {बर्लिन की दीवार|Berlin Wall falls|🧱} गिरी।"),
    (None, "{उन्नीस सौ इक्यानवे|1991|🚩} — {सोवियत संघ बिखरा|USSR dissolves|💥}। और उसी साल — भारत में, बड़े आर्थिक सुधार!"),
    (None, "{उन्नीस सौ पचानवे|1995|🤝} — {डब्ल्यू टी ओ|WTO|🌐} बना। दुनिया के बाज़ार, और क़रीब आए।"),
    (None, "[punch] आज — लगभग हर देश, कहीं न कहीं, {मिक्स्ड|Almost all are mixed|🤝} है। फ़र्क़ बस इतना — बाज़ार कितना, और सरकार कितनी!"),

    # ---------------------------------------------------------------- 7. Three consensuses
    ("focus:consensus", "[scene] अब एक बड़ा सवाल — एक गरीब देश अमीर कैसे बने? इस पर दुनिया में, तीन बड़ी सोच आईं। इन्हें कहते हैं — {कंसेंसस|Consensus|🧭}, यानी आम सहमति।"),
    (None, "[name] पहली — {वॉशिंगटन कंसेंसस|Washington Consensus|🇺🇸}। ये नाम दिया, अर्थशास्त्री {जॉन विलियमसन|John Williamson|🎓} ने — {उन्नीस सौ नवासी|1989|📅} में।"),
    (None, "नाम वॉशिंगटन क्यों? क्योंकि इसके पीछे थे — वॉशिंगटन में बैठे, {आई एम एफ़|IMF|🏦}, {वर्ल्ड बैंक|World Bank|🌐}, और {अमेरिका का ट्रेज़री विभाग|US Treasury|🇺🇸}।"),
    (None, "शुरुआत में ये नुस्ख़ा था — {लैटिन अमेरिका|Latin America crisis|🌎} के, क़र्ज़ और संकट में फँसे देशों के लिए।"),
    (None, "इसकी दस सिफ़ारिशें थीं। मुख्य बातें — {सरकारी ख़र्च में अनुशासन|Fiscal discipline|📏}, {टैक्स सुधार|Tax reform|🧾}, {व्यापार खोलना|Trade liberalisation|🚢}, {विदेशी निवेश को आने देना|Open to FDI|🌍}, {निजीकरण|Privatisation|🏢}, {नियमों में ढील|Deregulation|🔓}, और {संपत्ति के अधिकार|Property rights|🔑}।"),
    (None, "[punch] यानी सीधा संदेश — सरकार पीछे हटे, बाज़ार आगे आए!"),
    (None, "[scene] लेकिन धीरे-धीरे, आलोचना भी हुई — हर देश के लिए, {एक ही नुस्ख़ा|One size fits all?|👕} कैसे सही? और ख़ासकर, दो हज़ार आठ के वैश्विक संकट के बाद — सरकार की भूमिका पर, फिर से ज़ोर आया।"),
    (None, "[name] दूसरी — {बीजिंग कंसेंसस|Beijing Consensus|🇨🇳}। यानी चीन का मॉडल। ये नाम दिया — {जोशुआ कूपर रामो|Joshua Cooper Ramo|✍️} ने, {दो हज़ार चार|2004|📅} में।"),
    (None, "इसकी बातें — {नए प्रयोग|Experimentation|🧪}, {धीरे-धीरे सुधार|Gradual reforms|🐢}, सरकार की मज़बूत भूमिका — और बाहर के विचारों में से, सिर्फ़ {काम के विचार|Selective adoption|🎯} लेना।"),
    (None, "[name] और तीसरी — {सैंटियागो कंसेंसस|Santiago Consensus|🇨🇱}। इसका ज़ोर — सिर्फ़ बढ़त पर नहीं, बल्कि {सबको साथ लेकर|Social inclusion|🤝} चलने पर, और {स्थानीय विकास|Local development|🏘️} पर।"),
    ("ex:", "यानी — {वॉशिंगटन|Market first|🏪} कहता है, बाज़ार पहले। {बीजिंग|State-guided experiments|🧪} कहता है, सरकार की निगरानी में प्रयोग। और {सैंटियागो|Inclusion first|🤝} कहता है — सबकी भलाई, साथ-साथ।"),

    # ---------------------------------------------------------------- 8. Distribution systems
    ("focus:distribution", "[scene] अब सवाल — जो बना, वो बँटा कैसे? हर सिस्टम का, अपना {बँटवारे का तरीक़ा|Distribution system|🍽️} है।"),
    (None, "[name] कैपिटलिस्ट सिस्टम में — बँटवारा करता है {बाज़ार|Market price|🏷️}। जिसके पास ख़रीदने की ताक़त — उसे मिलता है।"),
    (None, "यानी — अमीर को ज़्यादा, गरीब को कम। तेज़ और आसान — लेकिन बराबर नहीं।"),
    (None, "[name] स्टेट सिस्टम में — बँटवारा करती है {सरकार|The state|🏛️}। किसे, कितना मिले — ये सरकार तय करती है। जैसे — {राशन|Ration / quota|🎫}।"),
    (None, "यानी — ज़्यादा बराबर, लेकिन धीमा। और अक्सर, लंबी कतारें।"),
    (None, "[name] और मिक्स्ड सिस्टम में — {दोनों|Market + State|🤝}। ज़्यादातर चीज़ें बाज़ार से — और ज़रूरतमंदों के लिए, सरकार की मदद।"),
    ("ex:", "जैसे भारत में — मोबाइल फ़ोन, बाज़ार से। और राशन की दुकान का सस्ता अनाज — यानी {पी डी एस|PDS|🍚} — और {सब्सिडी|Subsidy|🎁}, सरकार की ओर से!"),

    # ---------------------------------------------------------------- 9. Sectors
    ("focus:sectors", "[scene] आख़िर में — इकॉनमी को, एक {पाँच मंज़िला इमारत|5 floors|🏢} की तरह देखिए। हर मंज़िल पर, अलग तरह का काम।"),
    (None, "[name] पहली मंज़िल — {प्राइमरी सेक्टर|Primary|🌾}। कुदरत से सीधे लेना।"),
    (None, "{खेती|Agriculture|🌱}, {पशुपालन और डेयरी|Dairy|🐄}, {मछली पालन|Fishing|🎣}, {जंगल|Forestry|🌳}, और {खदानें|Mining|⛏️}।"),
    (None, "[name] दूसरी मंज़िल — {सेकेंडरी सेक्टर|Secondary|🏭}। कुदरत से मिली चीज़ों को, बनाकर नया रूप देना।"),
    (None, "{कपास से कपड़ा|Kapas → Kapda|👕}, {गन्ने से चीनी|Ganna → Cheeni|🍬}, {लोहे से स्टील|Iron → Steel|🔩}। यानी {उद्योग|Industry|🏭}, और {निर्माण|Construction|🏗️}।"),
    (None, "[name] तीसरी मंज़िल — {टर्शियरी सेक्टर|Tertiary|🚚}। यानी {सेवाएँ|Services|🛎️}। ये ख़ुद चीज़ नहीं बनाता — बाक़ी दोनों का काम आसान करता है।"),
    (None, "{ट्रांसपोर्ट|Transport|🚛}, {बैंक|Banking|🏦}, {व्यापार|Trade|🛒}, {बीमा|Insurance|☂️}, {होटल|Hotels|🏨}, और {टीचर, डॉक्टर, वकील|Professionals|👩‍⚕️}।"),
    (None, "[name] चौथी मंज़िल — {क्वाटर्नरी सेक्टर|Quaternary|💡}। यानी {ज्ञान का सेक्टर|Knowledge sector|📚}।"),
    (None, "{रिसर्च|Research|🔬}, {शिक्षा|Education|🎓}, {आईटी|IT|💻}, और जानकारी से जुड़े काम।"),
    (None, "[name] और पाँचवीं, सबसे ऊपर की मंज़िल — {क्विनरी सेक्टर|Quinary|🎯}।"),
    (None, "यहाँ बैठते हैं — {सबसे ऊँचे फ़ैसले लेने वाले|Top decision-makers|🧑‍💼}। सरकार के बड़े अफ़सर, बड़ी कंपनियों के मुखिया, बड़े वैज्ञानिक, और बड़े संस्थानों के प्रमुख।"),
    (None, "[punch] ध्यान दीजिए — कई किताबें, चौथी और पाँचवीं मंज़िल को — टर्शियरी का ही, ऊँचा हिस्सा मानती हैं।"),
    ("ex:", "एक मोबाइल फ़ोन में, पाँचों मंज़िलें! धातु — {खदान से|Primary|⛏️}। फ़ोन बना — {फ़ैक्टरी में|Secondary|🏭}। आप तक पहुँचा — {दुकान से|Tertiary|🚚}। उसका सॉफ़्टवेयर — {रिसर्च से|Quaternary|💻}। और कंपनी का बड़ा फ़ैसला — {बोर्डरूम से|Quinary|🎯}!"),

    # ---------------------------------------------------------------- recap
    ("recap", "[scene] तो याद रखिए —"),
    (None, "{तीन परिभाषाएँ|Smith · Marshall · Robbins|📜} — दौलत, भलाई, और चुनाव।"),
    (None, "{प्रोडक्शन, कंज़म्प्शन, डिस्ट्रीब्यूशन|Production · Consumption · Distribution|🏭} — और {माइक्रो-मैक्रो|Micro & Macro|🌳}।"),
    (None, "{तीन सिस्टम|Capitalist · State · Mixed|🏛️} — हर एक की, ख़ूबियाँ और कमियाँ।"),
    (None, "{भारत|India: Mixed → Market-friendly|🇮🇳} — प्लानिंग वाली मिक्स्ड इकॉनमी, और फिर, उन्नीस सौ इक्यानवे।"),
    (None, "{तीन कंसेंसस|Washington · Beijing · Santiago|🧭} — बाज़ार पहले, प्रयोग, और सबको साथ।"),
    (None, "{तीन तरह का बँटवारा|Market · State · Mixed|🍽️}, और {पाँच सेक्टर|5 Sectors|🏢}।"),

    # ---------------------------------------------------------------- next + channel
    ("outro:Next: Chapter 2 — National Income", "[scene] लेकिन दोस्तों — पाँचों मंज़िलें मिलकर, पूरे साल में, देश ने कितना कमाया? ये गिनते कैसे हैं?"),
    (None, "[punch] रमेश सिंह, चैप्टर दो — नेशनल इनकम! अगले वीडियो में!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
