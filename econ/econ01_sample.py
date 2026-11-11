"""Econ01 - The Story of Village Palampur: 2-minute SAMPLE (hook, today's class, first two topics).
Source: NCERT Class 9 Economics, Ch 1 "The Story of Village Palampur". Facts used: Palampur is a hypothetical
village; Raiganj, a big village, is 3 km away, joined by an all-weather road; about 450 families; most houses have
electricity, which also runs all the tubewells; two primary schools and one high school; a government primary health
centre and a private dispensary; farming is the main production activity. Four requirements of production: land
(and natural resources: water, forests, minerals), labour, physical capital (fixed capital: tools, machines,
buildings; working capital: raw materials and money in hand), human capital (knowledge and enterprise).
Land under cultivation is practically fixed.
"""
CHAPTER = dict(num=1, title="The Story of Village Palampur", kicker="ECONOMICS · CLASS 1 · NCERT CLASS 9", rain="☕",
               outro_icons=("🌾", "🚜"))

TOPICS = [
    dict(id="palampur", name="Palampur", label="A village like ours", icon="🏡"),
    dict(id="factors", name="Factors of Production", label="Four things to make anything", icon="🧰"),
    dict(id="farming", name="Farming", label="More grain, same land", icon="🌾"),
    dict(id="nonfarm", name="Non-farm Work", label="Beyond the fields", icon="🏪"),
]

LINES = [
    ("hook", "[scene] दोस्तों, सुबह की {चाय|Chai|☕} याद कीजिए।"),
    (None, "एक छोटा-सा कप। लेकिन क्या कभी सोचा — इसे बनाने में, कितनी चीज़ें लगती हैं?"),
    (None, "{दूध|Doodh|🥛}, {चाय पत्ती|Chai patti|🍃}, {चूल्हा|Chulha|🔥}, {दुकान|Dukaan|🏪} — और चाय वाले भैया की {मेहनत|Mehnat|💪}!"),
    (None, "[punch] कोई भी चीज़ बनती कैसे है — यही है आज का सवाल!"),

    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {पालमपुर|Palampur gaon|🏡} नाम का एक गाँव, और वहाँ की ज़िंदगी।"),
    (None, "दूसरा — कुछ भी बनाने के लिए, {चार ज़रूरी चीज़ें|4 zaroori cheezein|🧰}।"),
    (None, "तीसरा — {खेती|Kheti|🌾} कैसे होती है, और ज़मीन कम क्यों पड़ती है।"),
    (None, "और चौथा — खेती के अलावा, गाँव के {बाक़ी काम|Baaki kaam|🏪}।"),

    ("center", "[name] चैप्टर एक — एक गाँव की कहानी!"),
    ("topics", "चलिए — पहले पालमपुर की सैर करते हैं!"),

    ("focus:palampur", "[scene] {पालमपुर|Palampur|🏡} — एक काल्पनिक गाँव। यानी, किताब ने समझाने के लिए बनाया हुआ एक गाँव।"),
    (None, "पास में {रायगंज|Raiganj|🛣️} नाम का एक बड़ा गाँव है — सिर्फ़ तीन किलोमीटर दूर। और वहाँ तक जाती है, हर मौसम में चलने वाली पक्की सड़क।"),
    (None, "गाँव में लगभग {साढ़े चार सौ परिवार|450 parivaar|🏘️} रहते हैं।"),
    (None, "ज़्यादातर घरों में {बिजली|Bijli|💡} है — और खेतों के {ट्यूबवेल|Tubewell|🚿} भी, बिजली से ही चलते हैं।"),
    (None, "{दो प्राइमरी स्कूल|2 Primary School|🏫}, {एक हाई स्कूल|1 High School|🎒} — और इलाज के लिए, एक सरकारी {प्राइमरी हेल्थ सेंटर|Health Centre|🏥}, और एक प्राइवेट डिस्पेंसरी।"),
    (None, "और पालमपुर का सबसे बड़ा काम? — {खेती|Kheti|🌾}!"),

    ("focus:factors", "[scene] अब वापस चलते हैं — चाय की दुकान पर! कुछ भी बनाना हो — चार चीज़ें चाहिए।"),
    (None, "पहली — {ज़मीन|Land|🏞️}। दुकान की जगह, खेत की मिट्टी — और कुदरत की चीज़ें, जैसे {पानी|Paani|💧}, {जंगल|Jangal|🌳}, {खनिज|Khanij|⛏️}।"),
    (None, "दूसरी — {लेबर|Labour|👷}। यानी — काम करने वाले लोग, और उनकी मेहनत।"),
    (None, "तीसरी — {फ़िज़िकल कैपिटल|Physical Capital|🛠️}। चूल्हा, बर्तन, मशीन — जो सालों चलें, वो हैं {फ़िक्स्ड कैपिटल|Fixed Capital|🔧}।"),
    ("ex:", "और दूध, चाय पत्ती, हाथ का पैसा — जो हर रोज़ लगें, वो हैं {वर्किंग कैपिटल|Working Capital|🥛}।"),
    (None, "और चौथी — सबसे ख़ास — {ह्यूमन कैपिटल|Human Capital|🧠}। यानी {नॉलेज|Knowledge|📚} और {एंटरप्राइज़|Enterprise|🚀} — जानकारी, और काम शुरू करने का जज़्बा — जो बाक़ी तीनों को जोड़कर, कुछ बना दे!"),

    ("recap", "[scene] तो याद रखिए — चार चीज़ें:"),
    (None, "{ज़मीन|Land|🏞️}, {लेबर|Labour|👷}, {फ़िज़िकल कैपिटल|Physical Capital|🛠️}, और {ह्यूमन कैपिटल|Human Capital|🧠}।"),
    ("outro:Zameen fixed — phir zyada anaaj kaise?", "लेकिन दोस्तों — पालमपुर में ज़मीन तो बढ़ नहीं सकती। फिर ज़्यादा अनाज उगे — तो कैसे?"),
    (None, "[punch] ये कहानी — अगले हिस्से में!"),
]
