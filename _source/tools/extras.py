"""Strings added in the design/blog update, per language. build.py merges these into each content dict."""

X = {
    "en": {
        "ui": {
            "chat_wa": "Chat on WhatsApp", "wa_short": "WhatsApp", "min_read": "min read", "latest": "Latest", "all_posts": "All posts",
            "cats": {"roads": "Roads", "water": "Water", "buildings": "Buildings", "planning": "Planning", "quality": "Quality"},
            "share_wa": "Share on WhatsApp", "email_us": "Email us", "figures": "Key facts", "learn_more": "Learn more",
        },
        "nav": {"insights": "Blog"},
        "meta_insights": ("Blog | Infrastructure and construction explainers | MCC Group", "Plain-language articles on roads, bridges, canals, concrete, PEB structures, site planning and choosing a contractor. By Mahendra Heda, MCC Group."),
        "insights": {"h1": "Blog", "lede": "Plain-language articles on infrastructure and construction, by Mahendra Heda, Executive Director."},
        "home": {
            "figures": [("1984", "Year founded"), ("120+", "People in the team"), ("2", "States: Maharashtra and Telangana"), ("6", "Companies in the group")],
            "insights_title": "From the blog", "insights_intro": "Explainers on roads, canals, concrete, planning and choosing a contractor.",
            "join_title": "Build a long-term career with us", "join_text": "We want people who grow with the company. No positions are open at the moment, but we keep CVs for the future.", "join_link": "Careers at MCC Group",
            "tiles_more": "Also part of our work",
        },
    },
    "hi": {
        "ui": {
            "chat_wa": "व्हाट्सऐप पर चैट करें", "wa_short": "व्हाट्सऐप", "min_read": "मिनट में पढ़ें", "latest": "नवीनतम", "all_posts": "सभी लेख",
            "cats": {"roads": "सड़कें", "water": "जल", "buildings": "भवन", "planning": "नियोजन", "quality": "गुणवत्ता"},
            "share_wa": "व्हाट्सऐप पर शेयर करें", "email_us": "ईमेल करें", "figures": "मुख्य तथ्य", "learn_more": "और जानें",
        },
        "nav": {"insights": "ब्लॉग"},
        "meta_insights": ("ब्लॉग | इंफ्रास्ट्रक्चर और निर्माण की जानकारी | MCC Group", "सड़क, पुल, नहर, कंक्रीट, PEB संरचनाएँ, साइट योजना और ठेकेदार चुनने पर सरल भाषा में लेख। लेखक: महेंद्र हेडा, MCC Group।"),
        "insights": {"h1": "ब्लॉग", "lede": "इंफ्रास्ट्रक्चर और निर्माण पर सरल भाषा में लेख, कार्यकारी निदेशक महेंद्र हेडा द्वारा।"},
        "home": {
            "figures": [("1984", "स्थापना वर्ष"), ("120+", "टीम में लोग"), ("2", "राज्य: महाराष्ट्र और तेलंगाना"), ("6", "समूह की कंपनियाँ")],
            "insights_title": "ब्लॉग से", "insights_intro": "सड़क, नहर, कंक्रीट, योजना और ठेकेदार चुनने पर जानकारी।",
            "join_title": "हमारे साथ लंबा करियर बनाएँ", "join_text": "हम ऐसे लोग चाहते हैं जो कंपनी के साथ आगे बढ़ें। अभी कोई पद रिक्त नहीं है, पर हम भविष्य के लिए CV रखते हैं।", "join_link": "MCC Group में करियर",
            "tiles_more": "हमारे काम का हिस्सा",
        },
    },
    "mr": {
        "ui": {
            "chat_wa": "व्हॉट्सॲपवर चॅट करा", "wa_short": "व्हॉट्सॲप", "min_read": "मिनिटांत वाचा", "latest": "ताजे", "all_posts": "सर्व लेख",
            "cats": {"roads": "रस्ते", "water": "जल", "buildings": "इमारती", "planning": "नियोजन", "quality": "दर्जा"},
            "share_wa": "व्हॉट्सॲपवर शेअर करा", "email_us": "ईमेल करा", "figures": "मुख्य माहिती", "learn_more": "अधिक जाणून घ्या",
        },
        "nav": {"insights": "ब्लॉग"},
        "meta_insights": ("ब्लॉग | पायाभूत सुविधा आणि बांधकामाविषयी माहिती | MCC Group", "रस्ते, पूल, कालवे, काँक्रीट, PEB संरचना, साइट नियोजन आणि कंत्राटदार निवडणे यावर सोप्या भाषेत लेख. लेखक: महेंद्र हेडा, MCC Group."),
        "insights": {"h1": "ब्लॉग", "lede": "पायाभूत सुविधा आणि बांधकामावर सोप्या भाषेत लेख, कार्यकारी संचालक महेंद्र हेडा यांनी लिहिलेले."},
        "home": {
            "figures": [("1984", "स्थापना वर्ष"), ("120+", "टीममधील जण"), ("2", "राज्ये: महाराष्ट्र आणि तेलंगणा"), ("6", "समूहातील कंपन्या")],
            "insights_title": "ब्लॉगमधून", "insights_intro": "रस्ते, कालवे, काँक्रीट, नियोजन आणि कंत्राटदार निवडणे यावर माहिती.",
            "join_title": "आमच्यासोबत दीर्घकालीन करिअर घडवा", "join_text": "कंपनीसोबत वाढणारी माणसे आम्हाला हवी आहेत. सध्या कोणतीही पदे रिक्त नाहीत, पण आम्ही भविष्यासाठी CV ठेवतो.", "join_link": "MCC Group मधील करिअर",
            "tiles_more": "आमच्या कामाचा भाग",
        },
    },
}


def apply(C, lang):
    x = X[lang]
    C["ui"].update(x["ui"])
    C["nav"].update(x["nav"])
    C["meta"]["insights"] = x["meta_insights"]
    C["insights"].update(x["insights"])
    C["home"].update(x["home"])
    return C
