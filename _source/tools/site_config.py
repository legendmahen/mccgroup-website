"""Facts and settings shared by every language. Only facts supplied or confirmed by the client belong here."""

DOMAIN = "https://mccgroup.in"
BRAND = "MCC Group"
FOUNDED = 1984
PUBLISHED = "2026-11-11"

ADDRESS = {
    "street": "908, B Wing, Lokmat Building, Lokmat Square",
    "city": "Nagpur",
    "region": "Maharashtra",
    "postal": "440010",
    "country": "IN",
}
PHONE_OFFICE = {"display": "0712-4210767", "tel": "+917124210767"}
PHONE_MOBILE = {"display": "90497 70088", "tel": "+919049770088", "wa": "919049770088"}
EMAIL_ENQUIRY = "info@mccgroup.in"
EMAIL_CAREERS = "info@mccgroup.in"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + "908%2C+B+Wing%2C+Lokmat+Building%2C+Lokmat+Square%2C+Nagpur+440010"

LANGS = ["en", "hi", "mr"]
LANG_PREFIX = {"en": "", "hi": "hi/", "mr": "mr/"}
HREFLANG = {"en": "en-IN", "hi": "hi-IN", "mr": "mr-IN"}

# Group entities (names exactly as supplied)
CIVIL_COMPANIES = [
    "Mahendra Construction",
    "Mahendra Irricon Pvt Ltd",
    "Mahagauri Buildcon",
    "Mahagauri Infra",
    "Mahagauri Construction",
]
CRUSHER_COMPANY = "Mahagauri Stone Crusher Pvt Ltd"

# Page keys -> URL path (same in every language)
PAGES = {
    "home": "",
    "about": "about/",
    "capabilities": "capabilities/",
    "work": "our-work/",
    "plant": "plant-and-machinery/",
    "careers": "careers/",
    "insights": "blog/",
    "contact": "contact/",
}
ARTICLES = [
    "anatomy-of-a-road", "canal-lining-explained", "peb-vs-conventional-construction", "timeline-control-and-project-cost",
    "quality-checks-in-road-construction", "storm-drain-planning-in-layouts", "planning-rock-excavation-and-cuttings", "concrete-curing-basics",
    "monsoon-planning-for-civil-sites", "bridge-construction-stages", "how-to-choose-a-civil-contractor", "equipment-planning-on-infrastructure-sites",
]
ARTICLE_CATS = {
    "anatomy-of-a-road": "roads", "canal-lining-explained": "water", "peb-vs-conventional-construction": "buildings", "timeline-control-and-project-cost": "planning",
    "quality-checks-in-road-construction": "quality", "storm-drain-planning-in-layouts": "water", "planning-rock-excavation-and-cuttings": "roads", "concrete-curing-basics": "quality",
    "monsoon-planning-for-civil-sites": "planning", "bridge-construction-stages": "roads", "how-to-choose-a-civil-contractor": "planning", "equipment-planning-on-infrastructure-sites": "planning",
}

# Photos: slug -> (category, width, height) filled in from tools/images.json at build time
