"""Econ01 - The Story of Village Palampur (full class). Course plan: Ramesh Singh Ch 1, NCERT foundation class 1.
Source: NCERT Class 9 Economics, Chapter 1 "The Story of Village Palampur".
Facts used (from the NCERT chapter): Palampur is a hypothetical village; farming is the main activity, small-scale
manufacturing, dairy and transport are on a limited scale; Raiganj, a big village 3 km away, linked by an all-weather
road that goes on to the small town of Shahpur; bullock carts, tongas, buffalo carts (bogeys) with jaggery, motor
vehicles; about 450 families of several castes; 80 upper-caste families own most of the land (brick-and-cement
houses); SC (dalits) are one third of the population, in a corner of the village, small houses, some of mud and
straw; most houses have electricity, which runs all the tubewells and small businesses; two primary schools, one high
school, a government primary health centre and a private dispensary.
Four requirements of production (land and natural resources; labour; physical capital = fixed capital (tools,
machines, buildings) + working capital (raw materials such as the weaver's yarn and the potter's clay, money in
hand); human capital = knowledge and enterprise) = factors of production.
Farming: 75% of working people depend on farming; no expansion of cultivated land since 1960 (some wasteland had
been made cultivable before that); hectare = square of side 100 m; local units bigha, guintha. Kharif jowar and bajra
(cattle feed), potato October-December, rabi wheat (surplus sold at Raiganj), sugarcane once a year (raw or jaggery)
sold to traders in Shahpur. Irrigation: Persian wheels -> electric tubewells; first by government, then private; by
the mid-1970s the entire cultivated area of 200 hectares was irrigated. Multiple cropping = most common way to raise
production. Yield = crop produced on a given piece of land in a single season. Till the mid-1960s traditional seeds,
cow dung and natural manure; late 1960s Green Revolution: HYV seeds of wheat and rice, need much water, chemical
fertilisers and pesticides; first in Punjab, Haryana and western UP; some bought tractors and threshers. Palampur
wheat: 1300 kg/ha (traditional) -> 3200 kg/ha (HYV). Loss of soil fertility from chemical fertilisers; groundwater
table fell from continuous tubewell use; such resources are very hard to restore.
Land: of 450 families about one third (150) landless, mostly dalits; 240 families cultivate less than 2 ha; 60
medium and large farmers more than 2 ha; a few have 10 ha or more. Small farmers work their own fields with family;
medium and large farmers hire farm labourers (from landless or small-plot families), paid in cash or kind, sometimes
meals; wages and duration vary. Dala, a landless labourer on daily wages, and Ramkali get less than the minimum wage
set by the government. Capital: small farmers borrow from large farmers, moneylenders or traders at high interest.
Savita borrows from Tejpal Singh at 24% for four months and must work on his field at harvest. Medium and large
farmers have their own savings. Surplus wheat is sold mainly by medium and large farmers (Tejpal Singh at Raiganj);
earnings used for lending and for capital such as a tractor.
Non-farm: 25% of working people; dairy (buffaloes fed on grass, jowar and bajra; milk sold at Raiganj; two traders
from Shahpur set up collection-cum-chilling centres at Raiganj); small-scale manufacturing by less than fifty people,
at home or in fields with family labour (Mishrilal's electric sugarcane crushing machine, jaggery sold to Shahpur
traders); shopkeepers buying from wholesale markets in cities; small eateries near the bus stand; Kareem's computer
class centre with two women computer graduates (many students attend college in Shahpur); transport (Kishora, a farm
labourer, got a bank loan under a government scheme, bought a buffalo, sells milk, uses a wooden cart to bring clay
from the Ganga for the potter and sometimes jaggery to Shahpur). More non-farm work needs loans at low interest,
markets, and good roads, transport and telephone.
"""
CHAPTER = dict(num=1, title="The Story of Village Palampur", kicker="ECONOMICS · CLASS 1 · NCERT CLASS 9", rain="☕",
               outro_icons=("⏳", "🧩"), logo="assets/visualmind_logo.png", channel="The VisualMind",
               tagline="SEE IT. UNDERSTAND IT. REMEMBER IT.", next_title="Next class: Har cheez kam kyon padti hai?",
               bars={
                   "yield_bars": dict(title="Gehun ki paidavaar (kg / hectare)", bars=[
                       ("Purane beej", 1300, (150, 165, 205)), ("HYV beej", 3200, (70, 210, 140))]),
                   "land_bars": dict(title="450 parivaar: kiske paas kitni zameen?", bars=[
                       ("Zameen nahi", 150, (255, 90, 90)), ("2 ha se kam", 240, (255, 183, 3)),
                       ("2 ha se zyada", 60, (70, 210, 140))]),
               })

TOPICS = [
    dict(id="palampur", name="Palampur", label="A village like ours", icon="🏡"),
    dict(id="factors", name="Factors of Production", label="Four things to make anything", icon="🧰"),
    dict(id="kheti", name="Same Land, More Crops", label="Multiple cropping", icon="🌱"),
    dict(id="green", name="Green Revolution", label="More grain per hectare", icon="🌾"),
    dict(id="labour", name="Land & Labour", label="Who owns, who works", icon="👷"),
    dict(id="capital", name="Capital & Surplus", label="Loans and the market", icon="💰"),
    dict(id="nonfarm", name="Non-farm Work", label="Beyond the fields", icon="🏪"),
]

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सुबह की {चाय|Chai|☕} याद कीजिए।"),
    (None, "एक छोटा-सा कप। लेकिन क्या कभी सोचा — इसे बनाने में, कितनी चीज़ें लगती हैं?"),
    (None, "{दूध|Doodh|🥛}, {चाय पत्ती|Chai patti|🍃}, {चूल्हा|Chulha|🔥}, {दुकान|Dukaan|🏪} — और चाय वाले भैया की {मेहनत|Mehnat|💪}!"),
    (None, "[punch] कोई भी चीज़ बनती कैसे है — यही है आज का सवाल!"),

    # ---------------------------------------------------------------- today's class
    ("agenda", "[name] तो आज की क्लास में आप जानेंगे —"),
    (None, "पहला — {पालमपुर|Palampur gaon|🏡} नाम का एक गाँव, और वहाँ की ज़िंदगी।"),
    (None, "दूसरा — कुछ भी बनाने के लिए, {चार ज़रूरी चीज़ें|4 zaroori cheezein|🧰}।"),
    (None, "तीसरा — {खेती|Kheti|🌾} कैसे होती है, और ज़मीन कम क्यों पड़ती है।"),
    (None, "और चौथा — खेती के अलावा, गाँव के {बाक़ी काम|Baaki kaam|🏪}।"),

    ("center", "[name] चैप्टर एक — एक गाँव की कहानी!"),
    ("topics", "चलिए — पहले पालमपुर की सैर करते हैं!"),

    # ---------------------------------------------------------------- 1. Palampur
    ("focus:palampur", "[scene] {पालमपुर|Palampur|🏡} — एक काल्पनिक गाँव। यानी, किताब ने समझाने के लिए बनाया हुआ एक गाँव।"),
    (None, "यहाँ का मुख्य काम है — {खेती|Kheti|🌾}। बाक़ी काम — जैसे {छोटे कारख़ाने|Chhote kaarkhane|🔨}, {डेयरी|Dairy|🐃}, और {ट्रांसपोर्ट|Transport|🛺} — थोड़े पैमाने पर होते हैं।"),
    (None, "पास में {रायगंज|Raiganj|🛣️} नाम का एक बड़ा गाँव है — सिर्फ़ तीन किलोमीटर दूर। हर मौसम में चलने वाली पक्की सड़क, गाँव को रायगंज से, और आगे {शाहपुर|Shahpur|🏙️} नाम के छोटे शहर से जोड़ती है।"),
    (None, "इस सड़क पर चलती हैं — {बैलगाड़ियाँ|Bailgaadi|🐂}, {ताँगे|Tonga|🐎}, गुड़ से लदी भैंसा-गाड़ियाँ — और {मोटरसाइकिल, जीप, ट्रैक्टर, ट्रक|Motor gaadiyan|🚚}।"),
    (None, "गाँव में लगभग {साढ़े चार सौ परिवार|450 parivaar|🏘️} रहते हैं — अलग-अलग जातियों के।"),
    (None, "इनमें से {अस्सी परिवार|80 parivaar|🏠} ऊँची जातियों के हैं — और गाँव की ज़्यादातर ज़मीन, इन्हीं के पास है। इनके कई घर बड़े हैं — ईंट और सीमेंट के।"),
    (None, "और {दलित परिवार|Dalit parivaar|🛖} — यानी अनुसूचित जातियाँ — गाँव की आबादी का {एक तिहाई|1/3 aabaadi|👥} हैं। ये गाँव के एक कोने में, बहुत छोटे घरों में रहते हैं — कुछ घर मिट्टी और फूस के।"),
    (None, "ज़्यादातर घरों में {बिजली|Bijli|💡} है। खेतों के सारे {ट्यूबवेल|Tubewell|🚿} भी, बिजली से ही चलते हैं — और छोटे-मोटे धंधे भी।"),
    (None, "{दो प्राइमरी स्कूल|2 Primary School|🏫}, {एक हाई स्कूल|1 High School|🎒} — और इलाज के लिए, एक सरकारी {प्राइमरी हेल्थ सेंटर|Health Centre|🏥}, और एक प्राइवेट डिस्पेंसरी।"),
    (None, "[punch] लेकिन सवाल वही है — इस गाँव में, चीज़ें बनती कैसे हैं?"),

    # ---------------------------------------------------------------- 2. Factors of production
    ("focus:factors", "[scene] चलिए, वापस चाय की दुकान पर! कुछ भी बनाना हो — अनाज हो, या चाय — {चार चीज़ें|4 cheezein|🧰} चाहिए।"),
    (None, "पहली — {ज़मीन|Land|🏞️}। और कुदरत की बाक़ी चीज़ें भी — जैसे {पानी|Paani|💧}, {जंगल|Jangal|🌳}, {खनिज|Khanij|⛏️}।"),
    (None, "दूसरी — {लेबर|Labour|👷}। यानी — काम करने वाले लोग। कुछ कामों में {पढ़े-लिखे लोग|Padhe-likhe log|🎓} चाहिए, कुछ में {हाथ का काम|Haath ka kaam|✋} करने वाले।"),
    (None, "तीसरी — {फ़िज़िकल कैपिटल|Physical Capital|🛠️}। इसके दो हिस्से हैं।"),
    (None, "{औज़ार|Auzaar|🔧}, {मशीनें|Machine|⚙️}, {इमारतें|Imaarat|🏭} — ये सालों-साल काम आती हैं। इन्हें कहते हैं — {फ़िक्स्ड कैपिटल|Fixed Capital|🔒}।"),
    ("ex:", "और {कच्चा माल|Kachcha maal|🧶} — जैसे बुनकर का धागा, कुम्हार की मिट्टी — और {हाथ का पैसा|Haath ka paisa|💵}। ये काम में ख़र्च हो जाते हैं। इन्हें कहते हैं — {वर्किंग कैपिटल|Working Capital|🔄}।"),
    (None, "और चौथी — {ह्यूमन कैपिटल|Human Capital|🧠}। यानी {नॉलेज|Knowledge|📚} और {एंटरप्राइज़|Enterprise|🚀} — जानकारी, और काम शुरू करने का जज़्बा — जो बाक़ी तीनों को जोड़कर, कुछ बना दे।"),
    (None, "[name] इन चारों का एक नाम याद रखिए — {फ़ैक्टर्स ऑफ़ प्रोडक्शन|Factors of Production|🧩}!"),

    # ---------------------------------------------------------------- 3. Same land, more crops
    ("focus:kheti", "[scene] अब पालमपुर के खेतों में चलते हैं। यहाँ काम करने वालों में से, {पचहत्तर प्रतिशत|75%|👨‍🌾} लोग, रोज़ी-रोटी के लिए खेती पर निर्भर हैं — किसान हों, या खेत मज़दूर।"),
    (None, "लेकिन एक मुश्किल है — {ज़मीन बढ़ नहीं सकती|Zameen fixed|🔒}।"),
    (None, "{उन्नीस सौ साठ|1960|📅} के बाद से, पालमपुर में खेती की ज़मीन ज़रा भी नहीं बढ़ी। उससे पहले ही, कुछ बंजर ज़मीन खेती लायक़ बना ली गई थी। अब नई ज़मीन, बची ही नहीं।"),
    (None, "ज़मीन नापने की इकाई है — {हेक्टेयर|Hectare|📐}। एक हेक्टेयर मतलब — सौ मीटर लंबा, और सौ मीटर चौड़ा, एक चौकोर खेत। गाँव में लोग, {बीघा|Bigha|🌾} और गुंठा जैसी इकाइयाँ भी बोलते हैं।"),
    (None, "[punch] तो फिर — उसी ज़मीन से ज़्यादा अनाज, कैसे उगे?"),
    (None, "पहला तरीक़ा — साल में, एक ही खेत में, कई फ़सलें!"),
    (None, "बरसात यानी {खरीफ़|Kharif|🌧️} में — {ज्वार और बाजरा|Jowar-Bajra|🌾}, जो जानवरों का चारा बनते हैं।"),
    (None, "फिर अक्टूबर से दिसंबर तक — {आलू|Aloo|🥔}।"),
    (None, "और सर्दी यानी {रबी|Rabi|❄️} में — {गेहूँ|Gehun|🌾}। घर के लिए रखकर, बचा हुआ गेहूँ, रायगंज के बाज़ार में बिकता है।"),
    (None, "कुछ ज़मीन पर {गन्ना|Ganna|🎋} भी — जो साल में एक बार कटता है। गन्ना, या उससे बना {गुड़|Gud|🍯}, शाहपुर के व्यापारियों को बिकता है।"),
    (None, "[name] एक खेत, साल में कई फ़सलें — इसे कहते हैं — {मल्टीपल क्रॉपिंग|Multiple Cropping|🔁}। उत्पादन बढ़ाने का, सबसे आम तरीक़ा।"),
    (None, "लेकिन ये मुमकिन कैसे हुआ? जवाब है — {सिंचाई|Sinchaai|💧}।"),
    (None, "पहले कुओं से पानी निकालने के लिए, {रहट|Persian Wheel|☸️} चलता था। फिर बिजली आई — और बिजली वाले {ट्यूबवेल|Tubewell|🚿}, कहीं ज़्यादा ज़मीन सींचने लगे।"),
    (None, "पहले कुछ ट्यूबवेल सरकार ने लगाए — फिर किसानों ने अपने निजी ट्यूबवेल लगा लिए। और {उन्नीस सौ सत्तर के दशक के बीच|Mid-1970s|📅} तक — पूरी {दो सौ हेक्टेयर|200 hectare|💧} खेती की ज़मीन, सिंचित हो गई!"),

    # ---------------------------------------------------------------- 4. Green Revolution
    ("focus:green", "[scene] दूसरा तरीक़ा — हर हेक्टेयर से, ज़्यादा फ़सल। इसे कहते हैं — {यील्ड|Yield|⚖️}। यानी एक सीज़न में, ज़मीन के एक टुकड़े पर, कितनी फ़सल हुई।"),
    (None, "{उन्नीस सौ साठ के दशक के बीच|Mid-1960s|📅} तक — बीज पुराने थे, पैदावार कम। खाद के नाम पर — {गोबर|Gobar|🐄} और कुदरती खाद।"),
    (None, "फिर, {साठ के दशक के आख़िर में|Late 1960s|📅} आई — {ग्रीन रिवोल्यूशन|Green Revolution|🌾}। यानी हरित क्रांति।"),
    (None, "गेहूँ और चावल के नए बीज — {एच वाई वी|HYV Seeds|🌱}, यानी हाई यील्डिंग वैरायटी। एक पौधे पर, कहीं ज़्यादा अनाज!"),
    (None, "लेकिन इन्हें चाहिए था — बहुत सारा {पानी|Paani|💧}, {रासायनिक खाद|Chemical khaad|🧪}, और {कीटनाशक|Keetnaashak|🐛}।"),
    (None, "सबसे पहले इसे अपनाया — {पंजाब|Punjab|📍}, {हरियाणा|Haryana|📍}, और {पश्चिमी उत्तर प्रदेश|Western UP|📍} के किसानों ने। कुछ ने {ट्रैक्टर|Tractor|🚜} और थ्रेशर जैसी मशीनें भी ख़रीदीं।"),
    ("anim:yield_bars", "और पालमपुर में? पुराने बीजों से, गेहूँ की पैदावार थी — {तेरह सौ किलो|1300 kg|🌾} प्रति हेक्टेयर।"),
    (None, "[punch] और नए बीजों से — {बत्तीस सौ किलो|3200 kg|🚀}! क़रीब ढाई गुना!"),
    ("anim:none", "[scene] लेकिन रुकिए — क्या ज़मीन ये बोझ, हमेशा उठा पाएगी?"),
    (None, "ज़्यादा रासायनिक खाद से — {मिट्टी की ताक़त|Soil fertility|🟤} घटने लगी।"),
    (None, "और ट्यूबवेल से लगातार पानी खींचने से — {ज़मीन के नीचे का पानी|Groundwater|💧} और नीचे चला गया।"),
    (None, "[punch] याद रखिए — मिट्टी और पानी, सालों में बनते हैं। एक बार ख़त्म हुए — तो वापस लाना, बहुत मुश्किल।"),

    # ---------------------------------------------------------------- 5. Land & labour
    ("focus:labour", "[scene] अब सवाल — पालमपुर की ज़मीन, है किसके पास?"),
    ("anim:land_bars", "साढ़े चार सौ परिवारों में से — क़रीब एक तिहाई, यानी {डेढ़ सौ परिवारों|150 parivaar|🚫} के पास, खेती की ज़मीन ही नहीं। ज़्यादातर दलित।"),
    (None, "{दो सौ चालीस परिवार|240 parivaar|🌱} — दो हेक्टेयर से छोटे खेत जोतते हैं।"),
    (None, "और {साठ परिवार|60 parivaar|🌾} — यानी मँझोले और बड़े किसान — दो हेक्टेयर से ज़्यादा। कुछ बड़े किसानों के पास, दस हेक्टेयर, या उससे भी ज़्यादा!"),
    ("anim:none", "तो खेतों में काम कौन करता है? छोटे किसान — अपने परिवार के साथ, ख़ुद। मँझोले और बड़े किसान — {खेत मज़दूर|Khet mazdoor|👷} रखते हैं।"),
    (None, "ये मज़दूर — बिना ज़मीन वाले, या बहुत छोटे खेत वाले परिवारों से आते हैं। फ़सल पर इनका कोई हक़ नहीं। इन्हें {मज़दूरी|Mazdoori|💵} मिलती है — {नक़द|Nakad|💵}, या फ़सल के रूप में। कभी-कभी खाना भी।"),
    (None, "मज़दूरी — इलाक़े, फ़सल, और काम के हिसाब से बदलती है। और काम भी — कभी {रोज़ का|Rozana|📅}, कभी सिर्फ़ कटाई के लिए, कभी पूरे साल के लिए।"),
    (None, "[scene] मिलिए {डाला|Dala|🧑} से — पालमपुर का, एक बिना ज़मीन वाला मज़दूर। दिहाड़ी पर काम करता है — और उसे, रोज़ नया काम ढूँढना पड़ता है।"),
    (None, "[punch] सरकार ने खेत मज़दूर की {न्यूनतम मज़दूरी|Minimum wage|⚖️} तय की है — लेकिन डाला को, उससे भी कम मिलती है। यही हाल है, {रामकली|Ramkali|👩} का भी।"),

    # ---------------------------------------------------------------- 6. Capital & surplus
    ("focus:capital", "[scene] अब बात — {पैसे|Capital|💰} की। बीज, खाद, कीटनाशक, पानी — सबके लिए पैसा चाहिए।"),
    (None, "ज़्यादातर छोटे किसान {उधार|Udhaar|🤝} लेते हैं — बड़े किसानों से, गाँव के साहूकार से, या बीज-खाद बेचने वाले व्यापारियों से। और ब्याज — बहुत ज़्यादा!"),
    (None, "[scene] मिलिए {सविता|Savita|👩‍🌾} से — एक छोटी किसान। एक हेक्टेयर में गेहूँ बोना है — लेकिन पैसे नहीं।"),
    (None, "वो बड़े किसान {तेजपाल सिंह|Tejpal Singh|🧔} से उधार लेती है — {चौबीस प्रतिशत|24% byaaj|📈} ब्याज पर, {चार महीने|4 mahine|📅} के लिए।"),
    (None, "[punch] और शर्त ये भी — कटाई के मौसम में, उसे तेजपाल के खेत पर, मज़दूर बनकर काम करना होगा!"),
    (None, "दूसरी तरफ़ — मँझोले और बड़े किसानों के पास, खेती से हुई {अपनी बचत|Apni bachat|🏦} होती है।"),
    (None, "[scene] और फ़सल कटने के बाद? किसान घर के लिए अनाज रखकर, {बचा हुआ|Surplus|📦} बाज़ार में बेचते हैं।"),
    (None, "छोटे किसानों के पास, बचता ही बहुत कम है। बाज़ार में गेहूँ ज़्यादातर — मँझोले और बड़े किसान ही बेचते हैं। जैसे तेजपाल सिंह — {रायगंज के बाज़ार|Raiganj bazaar|🏪} में।"),
    (None, "और इस कमाई से? कुछ पैसा — छोटे किसानों को {उधार|Udhaar|💸} देने में जाता है। कुछ से — अगले सीज़न की तैयारी, और {ट्रैक्टर|Tractor|🚜} जैसी चीज़ें।"),

    # ---------------------------------------------------------------- 7. Non-farm work
    ("focus:nonfarm", "[scene] अब खेत से बाहर! पालमपुर में काम करने वालों में से, {पच्चीस प्रतिशत|25%|🏪} लोग — खेती के अलावा, दूसरे काम करते हैं।"),
    (None, "पहला — {डेयरी|Dairy|🐃}। कई परिवार भैंस पालते हैं — घास, और ज्वार-बाजरा खिलाते हैं। दूध बिकता है — रायगंज में।"),
    (None, "शाहपुर के {दो व्यापारियों|2 vyaapaari|🧊} ने, रायगंज में दूध इकट्ठा करके ठंडा रखने के सेंटर खोले हैं — वहाँ से दूध, दूर के शहरों तक जाता है।"),
    (None, "दूसरा — {छोटे कारख़ाने|Chhote kaarkhane|🔨}। पालमपुर में पचास से भी कम लोग, ये काम करते हैं — घर पर, या खेत में, परिवार के साथ।"),
    (None, "जैसे {मिश्रीलाल|Mishrilal|👨‍🔧} — उसने बिजली से चलने वाली, गन्ना पेरने की {मशीन|Machine|⚙️} ख़रीदी है। उससे {गुड़|Gud|🍯} बनाता है, और शाहपुर के व्यापारियों को बेचता है।"),
    (None, "तीसरा — {दुकानदार|Dukaandaar|🏪}। ये शहर के थोक बाज़ार से सामान लाते हैं — {चावल, गेहूँ, चीनी, चाय, तेल|Raashan|🛒}, {साबुन, टूथपेस्ट|Saabun-Toothpaste|🧼}, {कॉपी, पेन|Copy-Pen|✏️} — और गाँव में बेचते हैं।"),
    (None, "बस स्टैंड के पास के कुछ परिवारों ने, घर के एक हिस्से में, {खाने-पीने की छोटी दुकानें|Chhoti dukaanein|🍪} खोल ली हैं।"),
    (None, "[scene] और {करीम|Kareem|👨‍🏫} की कहानी! आजकल गाँव के बहुत से बच्चे, शाहपुर में कॉलेज जाते हैं — और कंप्यूटर सीखना चाहते हैं।"),
    (None, "तो करीम ने गाँव में खोल दिया — {कंप्यूटर सेंटर|Computer Centre|💻}! और पढ़ाने के लिए रखीं — {दो कंप्यूटर ग्रेजुएट महिलाएँ|2 women graduates|👩‍💻}।"),
    (None, "चौथा — {ट्रांसपोर्ट|Transport|🛺}, जो तेज़ी से बढ़ रहा है। रिक्शा, ताँगा, जीप, ट्रैक्टर, ट्रक — और बैलगाड़ी, भैंसा-गाड़ी चलाने वाले।"),
    (None, "[scene] जैसे {किशोरा|Kishora|🧑‍🌾} — एक खेत मज़दूर। सरकार की सस्ते क़र्ज़ वाली योजना से, उसे {बैंक से लोन|Bank loan|🏦} मिला — और उसने एक {भैंस|Bhains|🐃} ख़रीदी।"),
    (None, "अब वो दूध बेचता है। भैंस के पीछे, एक {लकड़ी की गाड़ी|Lakdi ki gaadi|🛒} जोड़ दी है — कभी {गंगा नदी|Ganga|🌊} से कुम्हार के लिए मिट्टी लाता है, कभी गुड़, शाहपुर ले जाता है।"),
    (None, "[punch] एक लोन, एक भैंस — और कमाई के, कई रास्ते!"),
    (None, "गाँव में ऐसे काम बढ़ें — इसके लिए चाहिए: {कम ब्याज पर लोन|Sasta loan|💸}, सामान बेचने के लिए {बाज़ार|Bazaar|🏪}, और अच्छी {सड़कें, ट्रांसपोर्ट, टेलीफ़ोन|Sadak aur Phone|📞}।"),

    # ---------------------------------------------------------------- recap
    ("recap", "[scene] तो याद रखिए —"),
    (None, "{फ़ैक्टर्स ऑफ़ प्रोडक्शन|4 Factors of Production|🧩} — ज़मीन, लेबर, फ़िज़िकल कैपिटल, और ह्यूमन कैपिटल।"),
    (None, "ज़मीन फ़िक्स्ड है — इसलिए {मल्टीपल क्रॉपिंग|Multiple Cropping|🔁}, और {ज़्यादा यील्ड|Zyada Yield|🌾}।"),
    (None, "लेकिन {मिट्टी और पानी|Mitti aur Paani|💧} का ध्यान, ज़रूरी है।"),
    (None, "ज़मीन बराबर नहीं बँटी — इसलिए {मज़दूर और उधार|Mazdoor aur Udhaar|👷} की कहानियाँ।"),
    (None, "और खेती के अलावा — {डेयरी, दुकान, कारख़ाने, ट्रांसपोर्ट|Non-farm kaam|🏪}।"),

    # ---------------------------------------------------------------- next class + channel
    ("outro:Next: Har cheez kam kyon padti hai?", "[scene] लेकिन दोस्तों, एक बात सोचिए — ज़मीन कम, पानी कम, पैसा कम — हर चीज़ कम क्यों पड़ती है?"),
    (None, "[punch] यही है इकॉनमी का सबसे बड़ा सवाल — और यही है, हमारी अगली क्लास!"),
    ("end", "तो अगला वीडियो ज़रूर देखिए। और ऐसे ही — देखकर समझने, और समझकर याद रखने के लिए — जुड़े रहिए, {द विज़ुअल माइंड|The VisualMind|🧠} के साथ!"),
    (None, "[punch] {देखिए|See it.|👀}। {समझिए|Understand it.|💡}। {याद रखिए|Remember it.|🧠}।"),
]
