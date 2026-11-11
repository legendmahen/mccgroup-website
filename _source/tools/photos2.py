"""Second photo batch: captions, new/extended work sections, plant strip. Merged by extras.apply()."""
CAP = {
 "en": {
  "structure-5": "A concrete wall with barbed-wire fencing along a site boundary",
  "structure-6": "A gated barrage with stone pitching on the embankment",
  "earthwork-1": "A motor grader levelling an earthwork surface",
  "earthwork-2": "Tipper trucks and stockpiles of excavated material at an earthwork site",
  "earthwork-3": "The site team on a stone-pitched embankment",
  "fleet-1": "A line of tipper trucks decorated with flower garlands",
  "village-1": "A water tanker curing a concrete road in Bhisi, Maharashtra",
  "village-2": "Curing a concrete drain beside a village road in Bhisi",
  "village-3": "A paver-block road with a concrete drain in Bhisi",
  "village-4": "A roller compacting aggregate on a village road in Bhisi",
  "village-5": "A tractor-drawn tanker curing a concrete drain",
  "village-6": "Concrete from a transit mixer poured into drain shuttering",
 },
 "hi": {
  "structure-5": "साइट की सीमा पर कंटीले तार की बाड़ के साथ कंक्रीट की दीवार",
  "structure-6": "गेट वाला बैराज और तटबंध पर पत्थर की पिचिंग",
  "earthwork-1": "मिट्टी के काम की सतह को समतल करता मोटर ग्रेडर",
  "earthwork-2": "मिट्टी के काम की साइट पर टिप्पर ट्रक और खुदाई की सामग्री के ढेर",
  "earthwork-3": "पत्थर की पिचिंग वाले तटबंध पर साइट की टीम",
  "fleet-1": "फूलों की माला से सजे टिप्पर ट्रकों की कतार",
  "village-1": "भिसी, महाराष्ट्र में कंक्रीट सड़क की क्योरिंग करता पानी का टैंकर",
  "village-2": "भिसी में गाँव की सड़क के पास कंक्रीट नाली की क्योरिंग",
  "village-3": "भिसी में कंक्रीट नाली के साथ पेवर ब्लॉक सड़क",
  "village-4": "भिसी में गाँव की सड़क पर गिट्टी को दबाता रोलर",
  "village-5": "ट्रैक्टर से खींचा जा रहा टैंकर कंक्रीट नाली की क्योरिंग करते हुए",
  "village-6": "ट्रांज़िट मिक्सर से नाली की शटरिंग में कंक्रीट डालना",
 },
 "mr": {
  "structure-5": "साइटच्या हद्दीवर काटेरी तारेच्या कुंपणासह काँक्रीटची भिंत",
  "structure-6": "दरवाजे असलेला बंधारा आणि भरावावर दगडी पिचिंग",
  "earthwork-1": "मातीकामाचा पृष्ठभाग सपाट करणारा मोटर ग्रेडर",
  "earthwork-2": "मातीकामाच्या साइटवर टिप्पर ट्रक आणि खोदलेल्या साहित्याचे ढीग",
  "earthwork-3": "दगडी पिचिंग केलेल्या भरावावर साइटची टीम",
  "fleet-1": "फुलांच्या माळांनी सजवलेल्या टिप्पर ट्रकांची रांग",
  "village-1": "भिसी, महाराष्ट्र येथे काँक्रीट रस्त्याला क्युरिंग करणारा पाण्याचा टँकर",
  "village-2": "भिसी येथे गावातील रस्त्याशेजारी काँक्रीट गटाराचे क्युरिंग",
  "village-3": "भिसी येथे काँक्रीट गटारासह पेव्हर ब्लॉक रस्ता",
  "village-4": "भिसी येथे गावातील रस्त्यावर खडी दाबणारा रोलर",
  "village-5": "ट्रॅक्टरने ओढलेला टँकर काँक्रीट गटाराला क्युरिंग करताना",
  "village-6": "ट्रान्झिट मिक्सरमधून गटाराच्या शटरिंगमध्ये काँक्रीट ओतणे",
 },
}
SEC = {
 "en": ("Village roads and drains", "Concrete roads, drains and paver-block lanes being built and cured in Bhisi, Maharashtra."),
 "hi": ("गाँव की सड़कें और नालियाँ", "भिसी, महाराष्ट्र में बनाई और क्योर की जा रही कंक्रीट सड़कें, नालियाँ और पेवर ब्लॉक गलियाँ।"),
 "mr": ("गावातील रस्ते आणि गटारे", "भिसी, महाराष्ट्र येथे बांधल्या जाणाऱ्या आणि क्युरिंग होत असलेल्या काँक्रीट रस्ते, गटारे आणि पेव्हर ब्लॉक गल्ल्या."),
}

def apply(C, lang):
    C["photos"].update(CAP[lang])
    for s in C["work"]["sections"]:
        if s["id"] == "earthwork":
            s["photos"] += ["earthwork-1", "earthwork-2", "earthwork-3"]
        if s["id"] == "concrete":
            s["photos"] += ["structure-6", "structure-5"]
    n, t = SEC[lang]
    secs = C["work"]["sections"]
    i = [s["id"] for s in secs].index("concrete") + 1
    secs.insert(i, {"id": "village", "name": n, "text": t, "photos": ["village-1", "village-3", "village-4", "village-2", "village-5", "village-6"]})
    C["plant"]["photos"] = C["plant"]["photos"] + ["fleet-1", "earthwork-1"]
    return C
