"""Econ00p - Course Promo: a cinematic mix of the best moments of the Course Trailer (econ00_trailer)
and the Syllabus Roadmap (econ00b_roadmap), with music, sound effects and a "watch the full class" call to action.
Same facts as the two source videos (Ramesh Singh 18e chapter plan + NCERT). Rendered by render_promo.py.
"""
CHAPTER = dict(num=0, title="Indian Economy", kicker="ZERO TO ADVANCED · RAMESH SINGH 18e + NCERT", rain="✨",
               recap_title="VAADA", cta=True,
               # glimpses of the course behind the opening questions (animations from the classes)
               hook_bg={"Tamatar": "tomato_up", "₹20": "tomato_up", "₹200": "tomato_up", "Petrol": "supply_curve", "Bank": "equilibrium",
                        "1991": "map"})

TOPICS = [
    dict(id="p1", name="Neev", label="Ch 1–3", icon="🧱"),
    dict(id="p2", name="Bharat ka Safar", label="Ch 4–7", icon="🇮🇳"),
    dict(id="p3", name="Daam aur Sectors", label="Ch 8–11", icon="🏭"),
    dict(id="p4", name="Paisa aur Bazaar", label="Ch 12–15", icon="💰"),
    dict(id="p5", name="Duniya aur Sarkar", label="Ch 16–19", icon="🌍"),
    dict(id="p6", name="Samaj aur Bhavishya", label="Ch 20–22", icon="🌱"),
]

LINES = [
    # ---- grand hook: fast questions, each with a glimpse of the course behind it
    ("hook", "[scene] {टमाटर|Tamatar|🍅} — कभी {बीस रुपये|₹20|💸}, कभी {दो सौ|₹200|🔥}!"),
    (None, "{पेट्रोल|Petrol|⛽} का दाम — कौन तय करता है?"),
    (None, "आपके {बैंक|Bank|🏦} में रखा पैसा — जाता कहाँ है?"),
    (None, "[punch] और {उन्नीस सौ इक्यानवे|1991|🔓} में — भारत के साथ, आख़िर हुआ क्या था?"),
    (None, "[scene] इन सब सवालों का जवाब — एक ही कहानी में छुपा है।"),
    # ---- reveal
    ("center", "[name] इंडियन इकॉनमी!"),
    ("topics", "{बाईस चैप्टर|22 Chapters|📚}। {बावन क्लास|52 Classes|🎬}। {छह हिस्से|6 Parts|🗺️}। और एक ही नक्शा!"),
    # ---- the journey, part by part (strongest moments only)
    ("focus:p1", "शुरुआत — {नींव|Neev|🧱} से। एक {गाँव की कहानी|Gaon ki Kahani|🏡}, {डिमांड|Demand|🛒}, {सप्लाई|Supply|🚜}, और {जीडीपी|GDP|💹}।"),
    ("focus:p2", "फिर — {भारत का सफ़र|Bharat ka Safar|🇮🇳}। {उन्नीस सौ सैंतालीस|1947|🕊️} से, {उन्नीस सौ इक्यानवे|1991|🔓} तक।"),
    ("focus:p3", "{महँगाई|Inflation|🔥} क्यों बढ़ती है? {खेती|Agriculture|🌾}, {कारख़ाने|Industry|🏭}, {सर्विस सेक्टर|Services|💻}।"),
    ("focus:p4", "{पैसा और बाज़ार|Paisa aur Bazaar|💰} — {आर बी आई|RBI|🏦}, {बीमा|Insurance|☂️}, {शेयर बाज़ार|Share Bazaar|📈}।"),
    ("focus:p5", "{दुनिया और सरकार|Duniya aur Sarkar|🌍} — {आई एम एफ़|IMF|🌍}, {जी एस टी|GST|🧮}, और सरकार का {बजट|Budget|📊}।"),
    ("focus:p6", "और आख़िर में — {समाज और भविष्य|Samaj aur Bhavishya|🌱}। {क्लाइमेट चेंज|Climate Change|🌡️}, {शिक्षा|Education|🎓}, {रोज़गार|Employment|👷}।"),
    # ---- the promise
    ("recap", "[scene] {कोई रटना नहीं|Koi ratna nahi|🙅}। हर बात — एक {कहानी|Kahani|📖}। हर कहानी — एक {मिसाल|Misaal|💡}।"),
    (None, "कोर्स के अंत में — बजट की ख़बर हो, या महँगाई की — {आप ख़ुद समझेंगे|Aap khud samjhenge|💪}!"),
    # ---- call to action
    ("outro:cta", "[scene] और ये तो बस एक {झलक|Sirf ek jhalak!|✨} है! पूरी क्लास आपको, हर कॉन्सेप्ट की गहराई में ले जाएगी — {क़दम-दर-क़दम|Step by step|🪜}।"),
    (None, "[punch] ये पूरा सफ़र — {मिस मत कीजिए|Miss mat kijiye!|⚡}"),
    (None, "नीचे दिए गए {लिंक|Link below|👇} पर क्लिक कीजिए, और पूरी क्लास देखिए।"),
    (None, "[punch] चलिए — {खोज का सफ़र|Let's begin!|🚀} शुरू करते हैं!"),
]
