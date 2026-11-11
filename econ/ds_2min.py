"""Economics Class 1 - Demand & Supply: 2-minute SAMPLE in layman style (excited coaching voice).
Sources: NCERT Class 12 Introductory Microeconomics (Ch 2 consumer behaviour & demand: quantity a consumer is willing
and able to buy at a price; law of demand: price and quantity demanded move in opposite directions, other things
remaining the same) and Ramesh Singh, Indian Economy (uses demand-supply to explain prices and inflation).
Real-life fact: tomato retail prices crossed Rs 200/kg in several Indian cities in July 2023.
"""
from ds_sample import TOPICS

CHAPTER = dict(num=1, title="Demand & Supply", kicker="ECONOMICS · CLASS 1",
               hook_en="Tamatar kabhi bees rupaye kilo,\naur kabhi do sau rupaye kilo!",
               hook_hi="Tamatar wahi, khet wahi — phir ye daam ka khel khelta kaun hai?", outro_icons=("☀️", "🍦"))

LINES = [
    ("hook", "[scene] अरे दोस्तों! एक बात बताइए — टमाटर कभी बीस रुपये किलो, और कभी दो सौ रुपये किलो! ऐसा क्यों?"),
    (None, "दो हज़ार तेईस की जुलाई में तो कई शहरों में, टमाटर सच में दो सौ के पार चला गया था!"),
    (None, "टमाटर वही, खेत वही — फिर ये दाम का खेल खेलता कौन है?"),
    ("center", "[name] इस खेल का नाम है — डिमांड और सप्लाई!"),
    ("topics", "और इसकी पहली चाबी है — डिमांड। चलिए, बिल्कुल आसान भाषा में समझते हैं!"),

    ("focus:demand", "[scene] सोचिए, एक छोटा बच्चा खिलौने की दुकान पर खड़ा है। उसे वो रिमोट वाली कार चाहिए!"),
    ("anim:wish", "लेकिन जेब में? एक रुपया भी नहीं!"),
    (None, "तो क्या ये डिमांड है?"),
    (None, "[punch] बिल्कुल नहीं!"),
    ("pt:Demand matlab — cheez chahiye, paise bhi hain, aur kharch karne ka man bhi hai|Teenon ek saath!",
     "डिमांड का सीधा-सा मतलब — चीज़ चाहिए, पैसे भी हैं, और ख़र्च करने का मन भी है। तीनों एक साथ!"),
    ("ex:Sirf chahne se kuch nahi hota — wo to bas sapna hai!",
     "सिर्फ़ चाहने से कुछ नहीं होता — वो तो बस सपना है!"),
    ("pt:Kisi daam par aap jitna khareedna chahte hain, aur khareed bhi sakte hain — wahi aapki Demand hai|NCERT ki baat ka nichod",
     "एन सी ई आर टी की बात का निचोड़ भी यही है — किसी दाम पर आप जितना ख़रीदना चाहते हैं, और ख़रीद भी सकते हैं — वही आपकी डिमांड है।"),

    ("focus:law", "[scene] अब चलिए आम वाले ठेले पर! सीज़न का पहला आम — दो सौ रुपये किलो। लोग देखते हैं, और चुपचाप आगे बढ़ जाते हैं।"),
    ("anim:mango", "कुछ हफ़्ते बाद — वही आम, साठ रुपये किलो! और अब? ठेले पर भीड़ ही भीड़!"),
    (None, "[name] यही है — लॉ ऑफ़ डिमांड!"),
    ("pt:Daam badha, to log kam khareedte hain. Daam ghata, to zyada.|Bas itni-si baat hai!",
     "दाम बढ़ा, तो लोग कम ख़रीदते हैं। दाम घटा, तो ज़्यादा। बस इतनी-सी बात है!"),
    ("pt:Bas ek shart — baaki sab kuch waisa hi rahe|Salary, pasand — sab wahi. Badle sirf aam ka daam.",
     "बस एक शर्त — बाक़ी सब कुछ वैसा ही रहे। यानी आपकी सैलरी, आपकी पसंद — सब वही। बदले सिर्फ़ आम का दाम।"),
    ("anim:demand_curve", "और इसे ग्राफ़ पर बनाएँ, तो बनती है फिसलपट्टी जैसी, नीचे उतरती एक लाइन!"),
    ("ex:Demand Curve — phisalpatti jaisi, neeche utarti ek line!",
     "[name] इसे कहते हैं — डिमांड कर्व!"),

    ("recap:demand|Chaahat, paisa aur man — yahi hai Demand.", "तो याद रखिए — चाहत, पैसा और मन — यही है डिमांड।"),
    ("recap:law|Daam upar, to khareed neeche!", "और दाम ऊपर, तो ख़रीद नीचे!"),
    ("outro:Agar daam wahi rahe, aur phir bhi bheed badh jaaye, to?",
     "लेकिन दोस्तों — अगर दाम वही रहे, और फिर भी भीड़ बढ़ जाए, तो? गर्मी में कुल्फ़ी के साथ यही होता है!"),
    (None, "[punch] वो मज़ेदार कहानी — अगली क्लास में!"),
]
