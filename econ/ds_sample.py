"""Economics Class 1 - Demand & Supply: 5-minute SAMPLE (same conventions as polity/ch01_script.py).

Extra screen event:  anim:<name>  starts an animation on the topic's stage (see econ/render_econ.py).
Concepts are standard economics (law of demand / supply, shifts, equilibrium); real-life facts used:
tomato retail prices crossed Rs 200/kg in several Indian cities in July 2023 after heat, heavy rain and pests hit
the crop, and fell back once new arrivals reached the mandis; Alfred Marshall, Principles of Economics (1890).
"""

CHAPTER = dict(num=1, title="Demand & Supply", kicker="ECONOMICS · CLASS 1",
               hook_en="Same tomato. Same farm.\nWhy ₹20 one month… and ₹200 the next?",
               hook_hi="वही टमाटर — कभी ₹20, कभी ₹200… क्यों?")

TOPICS = [
    dict(id="demand", name="Demand", label="Wanting isn't enough", icon="🛒"),
    dict(id="law", name="Law of Demand", label="Price up, buyers down", icon="🥭"),
    dict(id="shift", name="Shift in Demand", label="When the whole curve moves", icon="🍦"),
    dict(id="supply", name="Supply", label="The seller's side", icon="🚜"),
    dict(id="eq", name="Equilibrium", label="Where both shake hands", icon="⚖️"),
    dict(id="elast", name="Elasticity", label="", icon="🧂"),
]

LINES = [
    # ---------------------------------------------------------------- hook
    ("hook", "[scene] दोस्तों, सोचिए — दो हज़ार तेईस की जुलाई। आप सब्ज़ी लेने गए, और टमाटर का भाव सुनकर चौंक गए। कई शहरों में टमाटर दो सौ रुपये किलो के पार चला गया था!"),
    (None, "और कुछ ही महीनों बाद, वही टमाटर फिर से सस्ता हो गया।"),
    (None, "टमाटर वही, खेत वही। फिर दाम इतना ऊपर-नीचे क्यों होता है?"),
    ("center", "[name] इसका जवाब छिपा है इकोनॉमिक्स के सबसे बुनियादी खेल में — डिमांड और सप्लाई।"),
    ("topics", "इस खेल के पाँच हिस्से हैं — डिमांड, लॉ ऑफ़ डिमांड, कर्व का खिसकना, सप्लाई, और आख़िर में इक्विलिब्रियम।"),
    (None, "ध्यान दीजिए — चाय हो, मोबाइल हो, या क्रिकेट मैच का टिकट — बाज़ार में ज़्यादातर चीज़ों का दाम, इसी खेल से तय होता है।"),

    # ---------------------------------------------------------------- demand
    ("focus:demand", "[scene] एक छोटा बच्चा, खिलौने की दुकान के सामने खड़ा है। उसे वो रिमोट वाली कार बहुत पसंद है।"),
    ("anim:wish", "लेकिन जेब में पैसे? एक भी नहीं।"),
    (None, "तो क्या ये डिमांड है?"),
    (None, "[punch] नहीं!"),
    ("pt:Demand = desire + ability to pay + willingness to pay",
     "इकोनॉमिक्स में डिमांड का मतलब सिर्फ़ चाहना नहीं है। डिमांड मतलब — चाहत, ख़रीदने की ताक़त, और ख़र्च करने की तैयारी — तीनों एक साथ।"),
    ("pt:…always at a given price, for a given time",
     "और डिमांड हमेशा किसी एक दाम पर, और किसी एक समय के लिए बताई जाती है।"),
    ("ex:Want a toy car with ₹0 in the pocket = a wish, not demand",
     "यानी जेब ख़ाली हो, तो वो सिर्फ़ ख़्वाहिश है — डिमांड नहीं।"),
    (None, "लेकिन अगर जेब में पैसे हों — तो आप कितना ख़रीदेंगे, ये किस बात पर टिका है?"),

    # ---------------------------------------------------------------- law of demand
    ("focus:law", "[scene] आम का मौसम शुरू हुआ है। ठेले पर पहला आम — दो सौ रुपये किलो। लोग देखते हैं, और आगे बढ़ जाते हैं।"),
    ("anim:mango", "कुछ हफ़्तों बाद, वही आम साठ रुपये किलो। और अब? ठेले के चारों तरफ़ भीड़!"),
    (None, "[name] यही है — लॉ ऑफ़ डिमांड।"),
    ("pt:Price ↑ → quantity demanded ↓|Price ↓ → quantity demanded ↑",
     "जब दाम बढ़ता है, तो ख़रीदी जाने वाली मात्रा घटती है। और दाम घटता है, तो मात्रा बढ़ती है।"),
    ("pt:An inverse relationship",
     "यानी दाम और डिमांड की मात्रा, उल्टी दिशा में चलते हैं — इसे कहते हैं इनवर्स रिलेशनशिप।"),
    ("pt:Condition: ceteris paribus – other things remaining the same",
     "लेकिन एक शर्त के साथ — सेटेरिस पैरिबस। ये लैटिन शब्द है, मतलब — बाक़ी सब कुछ वैसा ही रहे।"),
    (None, "यानी लोगों की आमदनी, उनकी पसंद, दूसरी चीज़ों के दाम — कुछ न बदले। बदले सिर्फ़ आम का दाम।"),
    ("pt:Explained classically by Alfred Marshall (Principles of Economics, 1890)",
     "इस नियम को सबसे साफ़ ढंग से समझाया था ब्रिटिश अर्थशास्त्री अल्फ़्रेड मार्शल ने, अठारह सौ नब्बे की किताब, प्रिंसिपल्स ऑफ़ इकोनॉमिक्स में।"),
    ("anim:demand_curve", "अब यही कहानी, एक ग्राफ़ पर देखिए। ऊपर की तरफ़ दाम, और नीचे की तरफ़ मात्रा।"),
    ("pt:Demand curve slopes downward, left to right",
     "दाम ऊँचा — तो मात्रा कम। दाम नीचा — तो मात्रा ज़्यादा। और बन जाती है एक ढलान वाली लाइन — डिमांड कर्व।"),
    ("anim:move_along", "याद रखिए — अगर सिर्फ़ दाम बदले, तो हम इसी कर्व पर ऊपर-नीचे चलते हैं।"),
    ("pt:Only price changes → movement ALONG the same curve",
     "[name] इसे कहते हैं — मूवमेंट अलॉन्ग द कर्व।"),
    (None, "लेकिन अगर दाम ना बदले, और फिर भी लोग ज़्यादा ख़रीदने लगें — तो?"),

    # ---------------------------------------------------------------- shift in demand
    ("focus:shift", "[scene] मई की दोपहर। पारा पैंतालीस डिग्री। कुल्फ़ी का दाम वही — दस रुपये।"),
    ("anim:summer", "लेकिन अब, उसी दस रुपये पर, लोग पहले से कहीं ज़्यादा कुल्फ़ी ख़रीद रहे हैं!"),
    ("anim:shift_right", "[name] यहाँ पूरा का पूरा डिमांड कर्व ही, दाईं तरफ़ खिसक जाता है। इसे कहते हैं — शिफ़्ट इन डिमांड।"),
    ("pt:A non-price factor changes → the whole curve SHIFTS",
     "कर्व तब खिसकता है, जब दाम के अलावा कोई और चीज़ बदले।"),
    ("pt:Income – salary ↑ → demand for normal goods ↑",
     "पहली चीज़ — आमदनी। सैलरी बढ़ी, तो ज़्यादातर चीज़ों की डिमांड भी बढ़ जाती है। इन्हें कहते हैं नॉर्मल गुड्स।"),
    ("pt:Tastes, season, fashion",
     "दूसरी — पसंद, मौसम और फ़ैशन। गर्मी में कुल्फ़ी, सर्दी में गरम चाय।"),
    ("pt:Prices of related goods – substitutes & complements",
     "तीसरी — जुड़ी हुई चीज़ों के दाम। चाय महँगी हुई, तो कुछ लोग कॉफ़ी की तरफ़ जाएँगे। ये हैं सब्स्टिट्यूट्स — यानी एक-दूसरे की जगह लेने वाली चीज़ें।"),
    ("ex:Car + petrol = complements: costly petrol hits demand for petrol cars",
     "और कार के साथ पेट्रोल — ये हैं कॉम्प्लिमेंट्स, जो साथ-साथ इस्तेमाल होती हैं। पेट्रोल बहुत महँगा हो, तो पेट्रोल गाड़ियों की डिमांड पर भी असर पड़ता है।"),
    ("pt:Expectations & population",
     "और चौथी — उम्मीदें और आबादी। लोगों को लगे कि कल सोना और महँगा होगा, तो आज ही ख़रीदने दौड़ पड़ते हैं।"),
    ("anim:shift_left", "और ये चीज़ें उल्टी दिशा में चलें — तो कर्व बाईं तरफ़ खिसक जाता है।"),
    (None, "लेकिन बाज़ार में दूसरी तरफ़ भी कोई खड़ा है — बेचने वाला।"),

    # ---------------------------------------------------------------- supply
    ("focus:supply", "[scene] गाँव में रामू काका टमाटर उगाते हैं। इस बार मंडी में भाव अच्छा मिल रहा है।"),
    ("anim:farmer", "तो रामू काका क्या करेंगे? अगली बार और ज़्यादा ज़मीन पर टमाटर लगाएँगे, और ज़्यादा माल मंडी लाएँगे।"),
    (None, "[name] यही है — लॉ ऑफ़ सप्लाई।"),
    ("pt:Price ↑ → quantity supplied ↑ – a direct relationship",
     "दाम बढ़े, तो बेचने वाले ज़्यादा माल लाते हैं। दाम घटे, तो कम। यानी दाम और सप्लाई, एक ही दिशा में चलते हैं।"),
    ("anim:supply_curve", "इसीलिए सप्लाई कर्व, ग्राफ़ पर ऊपर की तरफ़ चढ़ता है।"),
    ("pt:Supply curve slopes upward", "बाएँ से दाएँ, ऊपर की ओर।"),
    ("ex:Why? Higher price = more profit = more reason to produce",
     "क्योंकि ऊँचा दाम मतलब — ज़्यादा मुनाफ़ा। और मुनाफ़ा, हर बेचने वाले की सबसे बड़ी प्रेरणा है।"),
    (None, "अब सोचिए — एक तरफ़ ख़रीदार, जो सस्ता चाहता है। दूसरी तरफ़ बेचने वाला, जो महँगा चाहता है। दाम तय कैसे होगा?"),

    # ---------------------------------------------------------------- equilibrium
    ("focus:eq", "[scene] मंडी की सुबह। एक तरफ़ ख़रीदारों की भीड़, दूसरी तरफ़ टमाटर के ढेर।"),
    ("anim:equilibrium", "[name] जिस दाम पर, ख़रीदार जितना ख़रीदना चाहते हैं, ठीक उतना ही बेचने वाले बेचना चाहते हैं — उसे कहते हैं इक्विलिब्रियम प्राइस।"),
    ("pt:Equilibrium: quantity demanded = quantity supplied", "इक्विलिब्रियम मतलब — संतुलन। जहाँ डिमांड और सप्लाई के कर्व मिलते हैं।"),
    ("anim:surplus", "अगर दाम ज़्यादा रखा, तो माल बचा रह जाता है — इसे कहते हैं सरप्लस।"),
    ("pt:Price above equilibrium → surplus → sellers cut the price", "और माल निकालने के लिए, बेचने वाले दाम घटाते हैं।"),
    ("anim:shortage", "और अगर दाम बहुत कम हो, तो माल कम पड़ जाता है — शॉर्टेज।"),
    ("pt:Price below equilibrium → shortage → price rises", "लोग लाइन में लगते हैं, और दाम ऊपर चढ़ता है।"),
    (None, "[punch] यानी बाज़ार ख़ुद, दाम को संतुलन की तरफ़ खींच लाता है।"),
    ("anim:tomato_up", "अब वापस चलते हैं, उस टमाटर पर। दो हज़ार तेईस में तेज़ गर्मी, भारी बारिश और कीड़ों ने कई इलाक़ों में फ़सल को नुक़सान पहुँचाया।"),
    ("ex:2023: crop damage → supply curve shifts LEFT → tomato price shoots up",
     "सप्लाई अचानक घट गई। सप्लाई कर्व बाईं तरफ़ खिसका — और इक्विलिब्रियम दाम, आसमान पर!"),
    ("anim:tomato_down", "फिर नई फ़सल मंडी में पहुँची, सप्लाई बढ़ी, और दाम फिर नीचे आ गया।"),
    ("pt:New arrivals → supply ↑ → price falls again", "[punch] टमाटर वही था। बदली थी — सप्लाई।"),

    # ---------------------------------------------------------------- recap + tease
    ("recap:demand|Demand = desire + ability + willingness to pay", "तो याद रखिए — डिमांड मतलब: चाहत, ताक़त और तैयारी।"),
    ("recap:law|Price ↑, quantity demanded ↓ – movement along the curve", "लॉ ऑफ़ डिमांड: दाम ऊपर, मात्रा नीचे।"),
    ("recap:shift|Income, tastes, related goods, expectations → the curve shifts", "दाम के अलावा कुछ बदले, तो पूरा कर्व खिसकता है।"),
    ("recap:supply|Price ↑, quantity supplied ↑", "लॉ ऑफ़ सप्लाई: दाम ऊपर, सप्लाई भी ऊपर।"),
    ("recap:eq|Where demand meets supply – the market price", "और जहाँ दोनों मिलें — वही है बाज़ार का दाम।"),
    ("outro:Next class: Elasticity of Demand",
     "लेकिन दोस्तों, एक सवाल — नमक का दाम दोगुना हो जाए, तो क्या आप नमक खाना आधा कर देंगे? नहीं ना! और स्मार्टफ़ोन का दाम दोगुना हो जाए, तो?"),
    (None, "[punch] यही राज़ खुलेगा अगली क्लास में — इलास्टिसिटी ऑफ़ डिमांड!"),
]
