"""Chapter 1 - Historical Background (Laxmikanth, Indian Polity, 6th ed.): SAMPLE part (hook, map, 1600-1858 intro,
Regulating Act 1773, Act of Settlement 1781, Pitt's India Act 1784, recap, tease).

LINES: (screen event, narration). Narration is Hinglish written fully in Devanagari (English terms spelled the
way they are spoken) so the Hindi voice reads them in one accent; years are written as spoken.
Screen events:
  hook                 opening hook screen
  center               chapter name in the centre of the mind map
  hub:<id>             a branch hub flies out of the centre
  acts                 all topics of the chapter fly out one by one
  focus:<id>           highlight the topic + its catchy label on the map, zoom into its board
  pt:<text>            a point grows out of the topic
  ex:<text>            an example (bulb) point
  recap:<id>|<text>    a recap row
  outro:<text>         teaser screen
Tags at the start of the narration (stripped before speaking): [scene] slower+firmer opener, [name] the line that
names the topic (slower), [punch] louder+slower.
"""

CHAPTER = dict(num=1, title="Historical Background",
               hook_en="A company came to sell spices…\nand ended up ruling India.",
               hook_hi="मसाले बेचने आई एक कंपनी… जो पूरे देश पर राज करने लगी")

# every topic of the chapter (for the mind map); side: company (left) / crown (right)
TOPICS = [
    dict(id="t1773", year="1773", name="Regulating Act", label="The first leash", side="company"),
    dict(id="t1781", year="1781", name="Act of Settlement", label="Fixing the cracks", side="company"),
    dict(id="t1784", year="1784", name="Pitt's India Act", label="Two bosses, one company", side="company"),
    dict(id="t1786", year="1786", name="Act of 1786", label="", side="company"),
    dict(id="t1793", year="1793", name="Charter Act", label="", side="company"),
    dict(id="t1813", year="1813", name="Charter Act", label="", side="company"),
    dict(id="t1833", year="1833", name="Charter Act", label="", side="company"),
    dict(id="t1853", year="1853", name="Charter Act", label="", side="company"),
    dict(id="t1858", year="1858", name="Govt of India Act", label="", side="crown"),
    dict(id="t1861", year="1861", name="Indian Councils Act", label="", side="crown"),
    dict(id="t1892", year="1892", name="Indian Councils Act", label="", side="crown"),
    dict(id="t1909", year="1909", name="Indian Councils Act", label="", side="crown"),
    dict(id="t1919", year="1919", name="Govt of India Act", label="", side="crown"),
    dict(id="t1927", year="1927", name="Simon Commission", label="", side="crown"),
    dict(id="t1932", year="1932", name="Communal Award", label="", side="crown"),
    dict(id="t1935", year="1935", name="Govt of India Act", label="", side="crown"),
    dict(id="t1947", year="1947", name="Indian Independence Act", label="", side="crown"),
]
HUBS = dict(company=dict(title="Company Rule", years="1773 – 1858", label="From traders to rulers"),
            crown=dict(title="Crown Rule", years="1858 – 1947", label=""))

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सोचिए — एक कंपनी, जो हमारे देश में मसाले और कपड़े का व्यापार करने आई थी… वो एक दिन पूरे भारत पर राज करने लगी!"),
    (None, "ऐसा हुआ कैसे? और उस कंपनी पर लगाम आख़िर किसने लगाई?"),
    (None, "और सबसे बड़ा सवाल — उसी लगाम से हमारा आज का संविधान कैसे निकला?"),
    ("center", "[name] यही है हमारे पहले चैप्टर की कहानी — हिस्टॉरिकल बैकग्राउंड। यानी, संविधान बनने से पहले का इतिहास।"),
    ("hub:company", "ये कहानी दो हिस्सों में चलती है। पहला हिस्सा — कंपनी रूल, सत्रह सौ तिहत्तर से अठारह सौ अट्ठावन तक।"),
    ("hub:crown", "और दूसरा हिस्सा — क्राउन रूल, अठारह सौ अट्ठावन से उन्नीस सौ सैंतालीस तक।"),
    ("acts", "इन दोनों के बीच आते हैं एक के बाद एक कई ऐक्ट्स। और हर नया ऐक्ट, पिछले ऐक्ट की किसी कमी को भरने आया।"),
    (None, "ध्यान दीजिए — आज के संविधान की बहुत सी चीज़ें, इन्हीं पुराने ऐक्ट्स से धीरे-धीरे बनकर निकली हैं।"),

    # ---------------------------------------------------------------- from traders to rulers
    ("focus:company", "[scene] चलिए, सोलह सौ में चलते हैं। इंग्लैंड के कुछ व्यापारी मिलकर एक कंपनी बनाते हैं — ईस्ट इंडिया कंपनी।"),
    ("pt:1600 – East India Company comes to India|Exclusive trading rights by a charter of Queen Elizabeth I",
     "महारानी एलिज़ाबेथ प्रथम उसे एक चार्टर देती हैं — यानी एक शाही इजाज़तनामा — कि भारत से व्यापार का एक्सक्लूसिव हक़ इसी कंपनी का होगा।"),
    (None, "एक्सक्लूसिव मतलब — सिर्फ़ इसका, किसी और का नहीं।"),
    (None, "शुरुआत में ये लोग सिर्फ़ व्यापारी थे। लेकिन भारतीय राजाओं की आपसी लड़ाइयों के बीच, इनकी फ़ौज भी बढ़ी, और ताक़त भी।"),
    (None, "सत्रह सौ चौंसठ में बक्सर की लड़ाई होती है, और कंपनी जीत जाती है।"),
    ("pt:1765 – Company gets the 'Diwani' of Bengal, Bihar & Orissa|Rights over revenue and civil justice",
     "और नतीजा? सत्रह सौ पैंसठ में कंपनी को मिल जाती है — बंगाल, बिहार और उड़ीसा की दीवानी।"),
    (None, "दीवानी मतलब — रेवेन्यू यानी लगान वसूलने का हक़, और सिविल जस्टिस यानी आम लोगों के दीवानी झगड़ों का फ़ैसला करने का हक़।"),
    ("ex:Diwani = the shop manager now collects ALL the money and settles ALL the disputes",
     "सोचिए — आपने दुकान पर एक मैनेजर रखा। और एक दिन वही मैनेजर, पूरी दुकान का पैसा भी वसूलने लगा, और हर झगड़े का फ़ैसला भी करने लगा!"),
    (None, "[punch] व्यापारी अब शासक बन चुका था।"),
    ("pt:1858 – after the 'Sepoy Mutiny', the British Crown takes direct control",
     "ये कंपनी राज चलता रहा अठारह सौ सत्तावन के बड़े विद्रोह तक, जिसे अंग्रेज़ों ने 'सिपॉय म्यूटिनी' कहा।"),
    (None, "उसके बाद, अठारह सौ अट्ठावन में, ब्रिटिश क्राउन — यानी ब्रिटेन की सरकार — ने भारत का शासन सीधे अपने हाथ में ले लिया।"),
    ("pt:Crown rule lasts till independence – 15 August 1947",
     "और ये क्राउन रूल चला पंद्रह अगस्त, उन्नीस सौ सैंतालीस तक, जब भारत आज़ाद हुआ।"),
    (None, "लेकिन एक सवाल अब भी बाक़ी था — जो कंपनी इतना बड़ा इलाक़ा चला रही थी, उस पर नज़र कौन रख रहा था?"),
    (None, "[punch] जवाब था — कोई नहीं!"),

    # ---------------------------------------------------------------- 1773
    ("focus:t1773", "[scene] सत्रह सौ सत्तर। बंगाल में भयानक अकाल पड़ता है, लाखों लोग भूख से मर जाते हैं।"),
    (None, "उधर कंपनी के अफ़सर अमीर बनकर इंग्लैंड लौट रहे हैं — लेकिन कंपनी ख़ुद कर्ज़ में डूबी है, और ब्रिटिश सरकार से मदद माँग रही है।"),
    (None, "ब्रिटिश संसद समझ गई — इस कंपनी को अब खुली छूट नहीं दी जा सकती।"),
    (None, "[name] और आया — रेग्युलेटिंग ऐक्ट, सत्रह सौ तिहत्तर।"),
    ("pt:First step by the British Govt to control & regulate the Company's affairs in India",
     "ये पहला क़दम था, जब ब्रिटिश सरकार ने भारत में कंपनी के कामकाज को कंट्रोल और रेग्युलेट करना शुरू किया।"),
    (None, "रेग्युलेट मतलब — नियमों में बाँधना।"),
    ("pt:Recognised, for the first time, the Company's political & administrative functions",
     "पहली बार माना गया कि कंपनी सिर्फ़ व्यापारी नहीं है — उसके पॉलिटिकल और ऐडमिनिस्ट्रेटिव काम भी हैं। यानी, वो शासन भी चला रही है।"),
    ("pt:Laid the foundations of central administration in India",
     "और इसी ऐक्ट ने भारत में सेंट्रल ऐडमिनिस्ट्रेशन की नींव रखी। सेंट्रल ऐडमिनिस्ट्रेशन मतलब — एक केंद्र से चलने वाला शासन।"),
    (None, "याद रखिए — आज दिल्ली से चलने वाली केंद्र सरकार का बीज, यहीं बोया गया था।"),
    (None, "तो इस पहली लगाम में था क्या-क्या?"),
    ("pt:Governor of Bengal → 'Governor-General of Bengal'|First: Lord Warren Hastings",
     "पहला — बंगाल के गवर्नर को बना दिया गया गवर्नर-जनरल ऑफ़ बंगाल। और पहले गवर्नर-जनरल बने — लॉर्ड वॉरेन हेस्टिंग्स।"),
    ("pt:An Executive Council of 4 members to assist him",
     "उनकी मदद के लिए बनी एक एग्ज़िक्यूटिव काउंसिल — चार मेंबर्स की।"),
    (None, "लेकिन मज़ेदार बात सुनिए — शुरू के सालों में इन चार में से तीन मेंबर अक्सर हेस्टिंग्स के ख़िलाफ़ वोट करते थे! गवर्नर-जनरल अपनी ही काउंसिल में हार जाते थे।"),
    ("ex:Like a cricket captain who wants one team, but the selection committee votes him down",
     "बिल्कुल वैसे, जैसे क्रिकेट टीम का कप्तान कुछ और चाहता है, लेकिन सिलेक्शन कमिटी का वोट कुछ और कहता है!"),
    ("pt:Governors of Bombay & Madras made subordinate to the Governor-General of Bengal",
     "दूसरा — बॉम्बे और मद्रास प्रेसिडेंसी के गवर्नर, अब बंगाल के गवर्नर-जनरल के अधीन हो गए।"),
    (None, "प्रेसिडेंसी मतलब — कंपनी का एक बड़ा प्रशासनिक इलाक़ा। और अधीन मतलब — उनके नीचे।"),
    (None, "इससे पहले ये तीनों प्रेसिडेंसी, एक-दूसरे से बिल्कुल आज़ाद थीं।"),
    ("ex:A school with 3 independent branches – suddenly the Calcutta principal becomes everyone's head",
     "सोचिए, एक स्कूल की तीन ब्रांच हैं, और तीनों के प्रिंसिपल अपनी मर्ज़ी के मालिक। और अचानक ऑर्डर आता है — अब कलकत्ता वाला प्रिंसिपल सबका हेड होगा!"),
    ("pt:Supreme Court at Calcutta (set up in 1774)|1 Chief Justice + 3 other judges",
     "तीसरा — कलकत्ता में एक सुप्रीम कोर्ट का प्रावधान, जो सत्रह सौ चौहत्तर में बनकर तैयार हुआ। इसमें थे एक चीफ़ जस्टिस, और तीन दूसरे जजेस।"),
    (None, "इसके पहले चीफ़ जस्टिस थे — सर एलाइजा इम्पी।"),
    (None, "ध्यान दीजिए — आज का सुप्रीम कोर्ट उन्नीस सौ पचास में बना। लेकिन भारत में सुप्रीम कोर्ट नाम की पहली अदालत, यही कलकत्ता वाली थी।"),
    ("pt:Company servants barred from private trade and from taking presents or bribes from 'natives'",
     "चौथा — कंपनी के कर्मचारियों पर रोक लगी। ना वो प्राइवेट ट्रेड करेंगे, और ना ही 'नेटिव्स' से, यानी भारतीयों से, कोई तोहफ़ा या रिश्वत लेंगे।"),
    (None, "आज के सरकारी कर्मचारियों पर भी तोहफ़े और रिश्वत को लेकर सख़्त नियम हैं — सोच वही पुरानी है।"),
    ("pt:Court of Directors must report on revenue, civil & military affairs in India to the British Govt",
     "और पाँचवाँ — कंपनी की गवर्निंग बॉडी, यानी कोर्ट ऑफ़ डायरेक्टर्स, को अब ब्रिटिश सरकार को रिपोर्ट देनी थी — भारत के रेवेन्यू, सिविल और मिलिट्री मामलों की।"),
    (None, "यानी अब कंपनी का पूरा हिसाब-किताब, सरकार की टेबल पर था।"),
    (None, "[punch] लगाम लग चुकी थी।"),
    (None, "लेकिन… लगाम कसते ही, कलकत्ता में एक नई लड़ाई शुरू हो गई।"),

    # ---------------------------------------------------------------- 1781
    ("focus:t1781", "[scene] कलकत्ता। एक तरफ़ गवर्नर-जनरल और उनकी काउंसिल। दूसरी तरफ़ नया-नया सुप्रीम कोर्ट। और दोनों को लगता था — असली ताक़त मेरी है!"),
    (None, "रेग्युलेटिंग ऐक्ट में ये साफ़ ही नहीं था कि किसकी हद कहाँ तक है। और टकराव बढ़ता गया।"),
    (None, "[name] इन कमियों को ठीक करने के लिए ब्रिटिश संसद लाई — अमेंडिंग ऐक्ट, सत्रह सौ इक्यासी। इसे ऐक्ट ऑफ़ सेटलमेंट भी कहते हैं।"),
    (None, "अमेंडिंग मतलब — सुधार करने वाला।"),
    ("pt:Governor-General & Council exempted from the Supreme Court for acts in their official capacity|Same for Company servants' official actions",
     "पहला — गवर्नर-जनरल और काउंसिल ने जो काम अपनी ऑफ़िशियल कैपेसिटी में किए, यानी सरकारी हैसियत से, उन पर सुप्रीम कोर्ट का ज़ोर नहीं चलेगा। और कंपनी के कर्मचारियों के सरकारी कामों पर भी नहीं।"),
    ("pt:Revenue matters (and matters of revenue collection) kept out of its jurisdiction",
     "दूसरा — रेवेन्यू के मामले, और रेवेन्यू वसूली से जुड़े मामले भी, सुप्रीम कोर्ट के दायरे से बाहर कर दिए गए।"),
    (None, "जूरिस्डिक्शन, यानी दायरा — मतलब, कोर्ट किन मामलों को सुन सकता है।"),
    ("pt:Jurisdiction over all inhabitants of Calcutta|Personal law of the defendant: Hindu law for Hindus, Mohammedan law for Muslims",
     "तीसरा — कलकत्ता के सारे निवासियों पर सुप्रीम कोर्ट का अधिकार होगा। और कोर्ट, प्रतिवादी का पर्सनल लॉ लागू करेगा। हिंदुओं का केस हिंदू लॉ से, और मुसलमानों का केस मोहम्मडन लॉ से।"),
    (None, "प्रतिवादी मतलब — वो व्यक्ति, जिस पर केस किया गया हो।"),
    ("ex:Even today, marriage, divorce & inheritance follow different personal laws",
     "आज भी शादी, तलाक़ और विरासत जैसे मामलों में अलग-अलग पर्सनल लॉ चलते हैं — इस सोच की जड़ें इतनी पुरानी हैं।"),
    ("pt:Appeals from Provincial Courts → Governor-General-in-Council, not the Supreme Court",
     "चौथा — प्रोविंशियल कोर्ट्स, यानी प्रांतों की अदालतों से अपील, सुप्रीम कोर्ट में नहीं, गवर्नर-जनरल-इन-काउंसिल के पास जाएगी।"),
    ("pt:Governor-General-in-Council can frame regulations for Provincial Courts & Councils",
     "और पाँचवाँ — गवर्नर-जनरल-इन-काउंसिल को प्रोविंशियल कोर्ट्स और काउंसिल्स के लिए रेग्युलेशन्स बनाने की पावर मिल गई।"),
    (None, "[punch] सरकार और अदालत के बीच, एक लकीर खिंच गई।"),
    (None, "लेकिन असली सवाल अब भी वहीं खड़ा था — भारत पर राज, एक प्राइवेट कंपनी करे… या ब्रिटिश सरकार?"),

    # ---------------------------------------------------------------- 1784
    ("focus:t1784", "[scene] लंदन, सत्रह सौ तिरासी। कंपनी को लेकर संसद में ज़बरदस्त बहस। एक इंडिया बिल गिरता है — और उसके साथ, सरकार भी गिर जाती है!"),
    (None, "नए प्रधानमंत्री बनते हैं — सिर्फ़ चौबीस साल के विलियम पिट। और उन्हीं के नाम पर आता है अगला ऐक्ट।"),
    (None, "[name] पिट्स इंडिया ऐक्ट, सत्रह सौ चौरासी।"),
    ("pt:Separated the Company's commercial and political functions",
     "इस ऐक्ट ने कंपनी के दो कामों को अलग-अलग कर दिया — कमर्शियल, यानी व्यापार वाले काम, और पॉलिटिकल, यानी शासन वाले काम।"),
    ("pt:Court of Directors → commercial affairs|New Board of Control → political affairs",
     "व्यापार संभालेगा — कोर्ट ऑफ़ डायरेक्टर्स। और पॉलिटिकल मामले संभालेगी एक नई बॉडी — बोर्ड ऑफ़ कंट्रोल।"),
    ("pt:= a system of 'Double Government'",
     "[name] इसी को कहते हैं — डबल गवर्नमेंट। यानी, दोहरी सरकार।"),
    ("ex:A family business: the son runs the shop, but grandpa signs off every big decision",
     "जैसे एक फ़ैमिली बिज़नेस — दुकान का रोज़ का काम बेटा देखता है, लेकिन हर बड़े फ़ैसले पर आख़िरी मुहर दादाजी की लगती है!"),
    ("pt:Board of Control to supervise & direct civil & military government and revenues",
     "बोर्ड ऑफ़ कंट्रोल को पावर मिली — भारत में अंग्रेज़ी इलाक़ों के सिविल और मिलिट्री शासन, और रेवेन्यू — सबकी निगरानी करने की, और उन्हें निर्देश देने की।"),
    ("pt:Company's territories called 'British possessions in India' – for the first time",
     "और ध्यान दीजिए — पहली बार, कंपनी के इलाक़ों को कहा गया — 'ब्रिटिश पज़ेशन्स इन इंडिया'। यानी, भारत में ब्रिटेन की संपत्ति!"),
    (None, "सोचिए, इन तीन शब्दों का मतलब — ये ज़मीन अब सिर्फ़ कंपनी की नहीं, ब्रिटेन की थी।"),
    ("pt:British Govt gets supreme control over the Company's affairs and its administration in India",
     "और ब्रिटिश सरकार को मिल गया, कंपनी के कामकाज और भारत में उसके प्रशासन पर, सुप्रीम कंट्रोल। सुप्रीम कंट्रोल मतलब — सबसे ऊपर का नियंत्रण।"),
    (None, "[punch] व्यापारी कंपनी, अब सरकार की मुट्ठी में थी।"),

    # ---------------------------------------------------------------- recap + tease
    ("recap:t1773|Regulating Act – first control, Governor-General of Bengal, Supreme Court at Calcutta",
     "तो कहानी अब तक — सत्रह सौ तिहत्तर का रेग्युलेटिंग ऐक्ट: पहली लगाम, गवर्नर-जनरल ऑफ़ बंगाल, और कलकत्ता का सुप्रीम कोर्ट।"),
    ("recap:t1781|Act of Settlement – a line between the Government and the Court",
     "फिर सत्रह सौ इक्यासी का ऐक्ट ऑफ़ सेटलमेंट: सरकार और अदालत के बीच की लकीर।"),
    ("recap:t1784|Pitt's India Act – Double Government, 'British possessions in India'",
     "और सत्रह सौ चौरासी का पिट्स इंडिया ऐक्ट: डबल गवर्नमेंट, और 'ब्रिटिश पज़ेशन्स इन इंडिया'।"),
    ("outro:Next: the Act of 1786 and the Charter Acts",
     "लेकिन दोस्तों, कहानी यहीं नहीं रुकती। दो बॉस वाली इस व्यवस्था में, भारत में बैठे गवर्नर-जनरल की असली ताक़त कितनी थी?"),
    (None, "[punch] अगले हिस्से में — सत्रह सौ छियासी का ऐक्ट, और फिर चार्टर ऐक्ट्स की पूरी सीरीज़!"),
]
