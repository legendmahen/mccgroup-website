"""Static site generator for mccgroup.in (en at root, /hi/, /mr/).

Run:  python3 tools/build.py          (all languages)
      LANGS=en python3 tools/build.py  (subset, for development)
"""
import html, importlib, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import site_config as S
import extras

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
IMG = json.load(open(os.path.join(ROOT, "tools", "images.json")))
LANGS = os.environ.get("LANGS", ",".join(S.LANGS)).split(",")
esc = html.escape


def q(s):
    return esc(s, quote=True)


def url(lang, key=None, article=None, absolute=False):
    path = "/" + S.LANG_PREFIX[lang]
    if key:
        path += S.PAGES[key]
    if article:
        path += S.PAGES["insights"] + article + "/"
    return (S.DOMAIN + path) if absolute else path


def picture(slug, alt, sizes="100vw", eager=False, cls=""):
    m = IMG[slug]
    ws = m["sizes"]
    srcset = ", ".join(f"/assets/img/{slug}-{w}.webp {w}w" for w in ws)
    jpg = f"/assets/img/{slug}-{m['jpg']}.jpg"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img{c} src="{jpg}" width="{m["w"]}" height="{m["h"]}" alt="{q(alt)}" {load}></picture>')


def wa_link(C):
    from urllib.parse import quote
    return f"https://wa.me/{S.PHONE_MOBILE['wa']}?text={quote(C['ui']['wa_text'])}"


# ---------- JSON-LD ----------
def org_node(C):
    return {
        "@type": ["GeneralContractor", "Organization"],
        "@id": S.DOMAIN + "/#org",
        "name": S.BRAND,
        "url": S.DOMAIN + "/",
        "logo": S.DOMAIN + "/assets/logo.png",
        "image": S.DOMAIN + "/assets/og-image.jpg",
        "description": "MCC Group is a civil construction group in Nagpur, Maharashtra, founded in 1984. Class 1A registered contractor with PWD Maharashtra. Roads, bridges, canals, dams, buildings and PEB structures in Maharashtra and Telangana.",
        "foundingDate": str(S.FOUNDED),
        "telephone": [S.PHONE_OFFICE["tel"], S.PHONE_MOBILE["tel"]],
        "email": S.EMAIL_ENQUIRY,
        "address": {"@type": "PostalAddress", "streetAddress": S.ADDRESS["street"], "addressLocality": S.ADDRESS["city"],
                    "addressRegion": S.ADDRESS["region"], "postalCode": S.ADDRESS["postal"], "addressCountry": "IN"},
        "areaServed": [{"@type": "AdministrativeArea", "name": "Maharashtra"}, {"@type": "AdministrativeArea", "name": "Telangana"}],
        "numberOfEmployees": {"@type": "QuantitativeValue", "minValue": 120},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "10:00", "closes": "18:00"}],
        "founder": {"@type": "Person", "name": "Sanjay Heda", "jobTitle": "Founder President"},
        "member": [{"@type": "Person", "name": "Mahendra Heda", "jobTitle": "Executive Director"}],
        "knowsAbout": ["Road construction", "Highway construction", "Bridge construction", "Canal construction", "Canal lining", "Dam construction", "Storm drain works", "Commercial buildings", "Residential buildings", "PEB structures", "Landscaping", "Civil construction"],
        "subOrganization": [{"@type": "Organization", "name": n} for n in S.CIVIL_COMPANIES + [S.CRUSHER_COMPANY]],
        "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": S.PHONE_MOBILE["tel"], "email": S.EMAIL_ENQUIRY, "areaServed": "IN", "availableLanguage": ["English", "Hindi", "Marathi"]}],
    }


def jsonld(*nodes):
    data = {"@context": "https://schema.org", "@graph": list(nodes)}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def faq_node(faq, lang):
    return {"@type": "FAQPage", "inLanguage": S.HREFLANG[lang],
            "mainEntity": [{"@type": "Question", "name": a, "acceptedAnswer": {"@type": "Answer", "text": b}} for a, b in faq]}


def crumb_node(C, lang, trail):
    items = [{"@type": "ListItem", "position": 1, "name": C["ui"]["home"], "item": url(lang, "home", absolute=True)}]
    for i, (name, u) in enumerate(trail, 2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": S.DOMAIN + u})
    return {"@type": "BreadcrumbList", "itemListElement": items}


# ---------- layout ----------
def head(C, lang, key, title, desc, path_for_alt, extra_ld=(), og_type="website", noindex=False):
    """path_for_alt: function(lang)-> path (no domain) for hreflang alternates."""
    canon = S.DOMAIN + path_for_alt(lang)
    alts = "".join(f'<link rel="alternate" hreflang="{S.HREFLANG[l]}" href="{S.DOMAIN + path_for_alt(l)}">' for l in S.LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{S.DOMAIN + path_for_alt("en")}">'
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    ld = jsonld({"@type": "WebSite", "@id": S.DOMAIN + "/#site", "url": S.DOMAIN + "/", "name": S.BRAND, "publisher": {"@id": S.DOMAIN + "/#org"}, "inLanguage": S.LANGS and [S.HREFLANG[l] for l in S.LANGS]},
                org_node(C), *extra_ld)
    other_locales = "".join(f'<meta property="og:locale:alternate" content="{LC[l]["locale"]}">' for l in S.LANGS if l != lang)
    return f"""<!doctype html>
<html lang="{lang}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{q(desc)}">
{robots}
<link rel="canonical" href="{canon}">
{alts}
<meta name="theme-color" content="#0f1c26">
<meta property="og:site_name" content="{S.BRAND}"><meta property="og:type" content="{og_type}"><meta property="og:title" content="{q(title)}"><meta property="og:description" content="{q(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{S.DOMAIN}/assets/og-image.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="{C['locale']}">{other_locales}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/fonts/inter-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{ld}
</head>
"""


PHONE_PATH = "M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"


def wa_svg(hole, cls="wa-ico", color="#fff"):
    """WhatsApp-style chat bubble with a handset. `color` is the bubble, `hole` the handset (match the background)."""
    return (f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
            f'<path fill="{color}" d="M16 3C8.8 3 3 8.8 3 16c0 2.3.6 4.5 1.7 6.4L3 29l6.8-1.8A12.9 12.9 0 0 0 16 29c7.2 0 13-5.8 13-13S23.2 3 16 3z"/>'
            f'<path transform="translate(9.6 9.4) scale(.55)" fill="{hole}" stroke="{hole}" stroke-width="1" stroke-linejoin="round" d="{PHONE_PATH}"/></svg>')


def ico_call():
    return f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{PHONE_PATH}"/></svg>'


def ico_mail():
    return '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>'


def rich(s):
    """Escape text and turn e-mail addresses and the two phone numbers into links."""
    s = esc(s)
    s = re.sub(r"([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', s)
    s = s.replace(S.PHONE_OFFICE["display"], f'<a href="tel:{S.PHONE_OFFICE["tel"]}">{S.PHONE_OFFICE["display"]}</a>')
    s = s.replace(S.PHONE_MOBILE["display"], f'<a href="tel:{S.PHONE_MOBILE["tel"]}">{S.PHONE_MOBILE["display"]}</a>')
    return s


def read_minutes(a):
    words = len(a["summary"].split())
    for kind, val in a["body"]:
        words += len(val.split()) if isinstance(val, str) else sum(len(i.split()) for i in val)
    return max(3, round(words / 190))


def header(C, lang, key, path_for_alt):
    nav_keys = ["about", "capabilities", "work", "plant", "careers", "insights", "contact"]
    links = "".join(f'<a href="{url(lang, k)}"{" aria-current=\"page\"" if k == key else ""}>{esc(C["nav"][k])}</a>' for k in nav_keys if k != "contact")
    langs = "".join(f'<a href="{path_for_alt(l)}" lang="{l}" hreflang="{S.HREFLANG[l]}"{" aria-current=\"true\"" if l == lang else ""}>{LC[l]["short"] if l == "en" else LC[l]["label"]}</a>' for l in S.LANGS)
    return f"""<body>
<a class="skip" href="#main">{esc(C['ui']['skip'])}</a>
<div class="topbar"><div class="wrap"><span>{esc(S.ADDRESS['city'])}, Maharashtra &middot; {esc(C['ui']['hours'])}</span><span class="tb-links"><a href="tel:{S.PHONE_OFFICE['tel']}">{S.PHONE_OFFICE['display']}</a><a href="tel:{S.PHONE_MOBILE['tel']}">{S.PHONE_MOBILE['display']}</a><a href="mailto:{S.EMAIL_ENQUIRY}">{S.EMAIL_ENQUIRY}</a></span></div></div>
<header class="site-head"><div class="wrap head-in">
<a class="brand" href="{url(lang, 'home')}" aria-label="MCC Group, {esc(C['ui']['home'])}"><img src="/assets/logo.webp" width="{IMG['_logo']['w']}" height="{IMG['_logo']['h']}" alt="MCC Group"></a>
<button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">{esc(C['ui']['menu'])}</button>
<nav class="nav" id="site-nav" aria-label="{q(C['ui']['explore'])}">{links}
<div class="head-act"><a class="head-wa" href="{wa_link(C)}" target="_blank" rel="noopener" aria-label="{q(C['ui']['chat_wa'])}" title="{q(C['ui']['chat_wa'])}">{wa_svg('#25d366')}</a>
<a class="btn btn-navy head-cta" href="{url(lang, 'contact')}">{esc(C['ui']['enquire'])}</a></div>
<div class="lang" role="group" aria-label="{q(C['ui']['language'])}">{langs}</div></nav>
</div></header>
<main id="main">
"""


def footer(C, lang):
    nav_keys = ["about", "capabilities", "work", "plant", "careers", "insights", "contact"]
    pages = "".join(f'<li><a href="{url(lang, k)}">{esc(C["nav"][k])}</a></li>' for k in nav_keys)
    cos = "".join(f"<li>{esc(n)}</li>" for n in S.CIVIL_COMPANIES + [S.CRUSHER_COMPANY])
    a = S.ADDRESS
    first = re.split(r"(?<=[.।])\s", C["home"]["who"])[0]
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div class="foot-brand"><img src="/assets/logo.webp" width="{IMG['_logo']['w']}" height="{IMG['_logo']['h']}" alt="MCC Group" loading="lazy"><p>{esc(first)}</p>
<a class="foot-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg('#0a1a28', color='#25d366')} {esc(C['ui']['chat_wa'])}</a></div>
<nav aria-label="{q(C['ui']['explore'])}"><h2>{esc(C['ui']['explore'])}</h2><ul>{pages}</ul></nav>
<div><h2>{esc(C['ui']['group_companies'])}</h2><ul>{cos}</ul></div>
<div><h2>{esc(C['ui']['contact'])}</h2>
<address style="font-style:normal"><p>{esc(a['street'])}, {esc(a['city'])} {esc(a['postal'])}<br><a href="{S.MAPS_URL}" rel="noopener" target="_blank">{esc(C['ui']['open_maps'])}</a></p>
<p><a href="tel:{S.PHONE_OFFICE['tel']}">{S.PHONE_OFFICE['display']}</a><br><a href="tel:{S.PHONE_MOBILE['tel']}">{S.PHONE_MOBILE['display']}</a> ({esc(C['ui']['whatsapp'])})<br><a href="mailto:{S.EMAIL_ENQUIRY}">{S.EMAIL_ENQUIRY}</a></p>
<p>{esc(C['ui']['hours'])}</p></address></div>
</div>
<div class="foot-base">&copy; {S.FOUNDED}&ndash;2026 {S.BRAND}. {esc(C['ui']['rights'])}</div>
</div></footer>
<a class="wa-float" href="{wa_link(C)}" target="_blank" rel="noopener" aria-label="{q(C['ui']['chat_wa'])}" title="{q(C['ui']['chat_wa'])}">{wa_svg('#25d366')}</a>
<div class="actbar"><a href="tel:{S.PHONE_OFFICE['tel']}">{ico_call()}{esc(C['ui']['call'])}</a><a class="a-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg('#0f7d43')}{esc(C['ui']['wa_short'])}</a><a href="{url(lang, 'contact')}">{esc(C['ui']['enquire'])}</a></div>
<script src="/assets/app.js" defer></script>
</body>
</html>
"""


def page_head(C, lang, h1, lede, trail):
    crumbs = f'<li><a href="{url(lang, "home")}">{esc(C["ui"]["home"])}</a></li>' + "".join(
        f'<li><a href="{u}">{esc(n)}</a></li>' if u else f'<li aria-current="page">{esc(n)}</li>' for n, u in trail)
    return f"""<div class="page-head"><div class="wrap">
<nav class="crumbs" aria-label="{q(C['ui']['breadcrumb'])}"><ol>{crumbs}</ol></nav>
<h1>{esc(h1)}</h1>{f'<p class="rich">{rich(lede)}</p>' if lede else ''}</div></div>
"""


def faq_html(C, faq):
    items = "".join(f'<details><summary>{esc(a)}</summary><p class="rich">{rich(b)}</p></details>' for a, b in faq)
    return f'<div class="faq">{items}</div>'


def cta(C, lang, title=None, text=None):
    return f"""<section class="cta"><div class="wrap cta-in">
<div><h2>{esc(title or C['home']['cta_title'])}</h2><p class="rich">{rich(text or C['home']['cta_text'])}</p></div>
<div class="btns"><a class="btn btn-gold" href="{url(lang, 'contact')}">{esc(C['ui']['enquire'])}</a><a class="btn btn-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg('#0f7d43')}{esc(C['ui']['chat_wa'])}</a></div>
</div></section>
"""


def lightbox(C):
    return f"""<dialog class="lb" id="lightbox" aria-label="{q(C['ui']['see_work'])}"><div class="lb-in"><img alt="" width="1600" height="1067"><p></p>
<div class="lb-bar"><button type="button" data-prev>{esc(C['ui']['prev'])}</button><button type="button" data-next>{esc(C['ui']['next'])}</button><button type="button" data-close>{esc(C['ui']['close'])}</button></div></div></dialog>
"""


def shot(C, slug, sizes, lightboxed=True, cls=""):
    alt = C["photos"][slug]
    m = IMG[slug]
    full = f"/assets/img/{slug}-{max(m['sizes'])}.webp"
    pic = picture(slug, alt, sizes)
    c = f' class="shot {cls}"'.replace(" ", " ", 1) if cls else ' class="shot"'
    if lightboxed:
        return f'<figure{c}><button type="button" data-full="{full}" data-alt="{q(alt)}" aria-label="{q(alt)}">{pic}</button></figure>'
    return f"<figure{c}>{pic}</figure>"


def write(lang, rel, content):
    folder = os.path.join(DIST, S.LANG_PREFIX[lang], rel)
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(content)


def alt_fn(key=None, article=None):
    return lambda l: url(l, key, article)


def article_card(C, lang, slug, featured=False):
    a = ARTS[lang][slug]
    cat = C["ui"]["cats"][S.ARTICLE_CATS[slug]]
    meta = f'{read_minutes(a)} {esc(C["ui"]["min_read"])}'
    tag = "h2" if featured else "h3"
    if featured:
        return (f'<a class="featured" href="{url(lang, article=slug)}"><div><span class="cat">{esc(cat)} &middot; {esc(C["ui"]["latest"])}</span><{tag}>{esc(a["title"])}</{tag}></div>'
                f'<div><p>{esc(a["desc"])}</p><span class="meta">{esc(C["ui"]["by"])} Mahendra Heda &middot; {meta}</span></div></a>')
    return (f'<a class="card" href="{url(lang, article=slug)}"><span class="cat">{esc(cat)}</span><{tag}>{esc(a["title"])}</{tag}>'
            f'<p>{esc(a["desc"])}</p><span class="meta">{esc(C["ui"]["by"])} Mahendra Heda &middot; {meta}</span></a>')


# ---------- pages ----------
def page_home(C, lang):
    H = C["home"]
    alt = alt_fn("home")
    out = head(C, lang, "home", C["meta"]["home"][0], C["meta"]["home"][1], alt) + header(C, lang, "home", alt)
    figs = "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in H["figures"])
    slides = [("canal-lining-1", None)] + [("road-2", C["groups"][0]), ("canal-lining-2", C["groups"][1]), ("market-2", C["groups"][2])]
    sl = ""
    for i, (img, g) in enumerate(slides):
        if g is None:
            body = (f'<h1>{esc(H["h1"])}</h1><p class="hero-sub">{esc(H["sub"])}</p>'
                    f'<div class="btns"><a class="btn btn-gold" href="{url(lang, "contact")}">{esc(C["ui"]["enquire"])}</a><a class="btn btn-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg("#0f7d43")}{esc(C["ui"]["chat_wa"])}</a><a class="btn btn-line" href="{url(lang, "work")}">{esc(C["ui"]["see_work"])}</a></div>')
        else:
            body = (f'<p class="slide-h">{esc(g["name"])}</p><p class="hero-sub">{esc(g["text"])}</p>'
                    f'<div class="btns"><a class="btn btn-gold" href="{url(lang, "capabilities")}#{g["id"]}">{esc(C["ui"]["learn_more"])}</a><a class="btn btn-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg("#0f7d43")}{esc(C["ui"]["chat_wa"])}</a></div>')
        sl += (f'<div class="slide{" is-active" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{i+1} / {len(slides)}"><div class="hero-bg">{picture(img, C["photos"][img], "100vw", eager=(i == 0))}</div>'
               f'<div class="wrap hero-in">{body}</div></div>')
    dots = "".join(f'<button type="button" aria-label="{i+1}"{" aria-current=\"true\"" if i == 0 else ""}></button>' for i in range(len(slides)))
    out += f"""<section class="hero hero-slider" aria-roledescription="carousel" aria-label="MCC Group">{sl}
<div class="wrap"><div class="hero-ctrl"><button type="button" data-slide-prev aria-label="{q(C['ui']['prev'])}">&lsaquo;</button><div class="dots">{dots}</div><button type="button" data-slide-next aria-label="{q(C['ui']['next'])}">&rsaquo;</button></div></div></section>
<section class="figures"><div class="wrap"><ul class="fig-grid" aria-label="{q(C['ui']['figures'])}">{figs}</ul></div></section>
<section><div class="wrap split"><div><div class="mark"></div><h2>{esc(H['who_title'])}</h2><p class="lede">{esc(H['who'])}</p><p><a class="tlink" href="{url(lang, 'about')}">{esc(C['nav']['about'])}</a></p></div>
<div class="split-img">{picture('rock-cut-1', C['photos']['rock-cut-1'], '(min-width:56rem) 40vw, 100vw')}</div></div></section>
<section class="tint"><div class="wrap"><div class="sec-head"><h2>{esc(H['build_title'])}</h2><p>{esc(H['build_intro'])}</p></div>
<div class="tiles">"""
    for g in C["groups"][:3]:
        out += f'<a class="tile" href="{url(lang, "capabilities")}#{g["id"]}">{picture(g["img"], C["photos"][g["img"]], "(min-width:48rem) 33vw, 100vw")}<div class="tile-t"><h3>{esc(g["name"])}</h3><p>{esc(g["text"])}</p></div></a>'
    out += '</div><div class="more-list">'
    for g in C["groups"][3:]:
        out += f'<div><h3>{esc(g["name"])}</h3><p>{esc(g["text"])}</p></div>'
    out += f'</div><p style="margin-top:2rem"><a class="tlink" href="{url(lang, "capabilities")}">{esc(C["ui"]["capabilities_link"])}</a></p></div></section>'
    out += f"""<section class="dark"><div class="wrap"><div class="sec-head"><h2>{esc(H['how_title'])}</h2></div>
<ul class="principles">{''.join(f'<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for a, b in H['how'])}</ul></div></section>
<section><div class="wrap"><div class="sec-head"><h2>{esc(H['work_title'])}</h2><p>{esc(H['work_intro'])}</p></div>
<div class="mosaic">{shot(C, 'road-1', '(min-width:48rem) 50vw, 100vw', False, 'm1')}{shot(C, 'rock-excavation-4', '(min-width:48rem) 50vw, 100vw', False)}{shot(C, 'paving-1', '(min-width:48rem) 50vw, 100vw', False)}</div>
<p style="margin-top:2rem"><a class="tlink" href="{url(lang, 'work')}">{esc(C['ui']['view_work'])}</a></p></div></section>
<section class="tint"><div class="wrap cols2"><div><div class="mark"></div><h2>{esc(H['group_title'])}</h2><p>{esc(H['group_intro'])}</p></div>
<ul class="cos">{''.join(f'<li>{esc(n)}<span>{esc(C["companies"]["civil_label"])}</span></li>' for n in S.CIVIL_COMPANIES)}<li>{esc(S.CRUSHER_COMPANY)}<span>{esc(C['companies']['crusher_label'])}</span></li></ul></div></section>
<section><div class="wrap"><div class="sec-head"><h2>{esc(H['people_title'])}</h2></div>
<div class="leaders">{''.join(f'<div class="leader"><h3>{esc(l["name"])}</h3><p class="role">{esc(l["role"])}</p><p>{esc(l["bio"])}</p></div>' for l in C['leaders'])}</div></div></section>
<section class="tint"><div class="wrap"><div class="sec-head"><h2>{esc(H['insights_title'])}</h2><p>{esc(H['insights_intro'])}</p></div>
<div class="cards">{''.join(article_card(C, lang, s) for s in S.ARTICLES[:3])}</div>
<p style="margin-top:2rem"><a class="tlink" href="{url(lang, 'insights')}">{esc(C['ui']['all_posts'])}</a></p></div></section>
<section class="join"><div class="wrap join-in"><div><h2>{esc(H['join_title'])}</h2><p>{esc(H['join_text'])}</p></div><div class="btns"><a class="btn btn-navy" href="{url(lang, 'careers')}">{esc(H['join_link'])}</a></div></div></section>
{cta(C, lang)}"""
    write(lang, "", out + footer(C, lang))


def page_about(C, lang):
    A = C["about"]
    alt = alt_fn("about")
    ld = [crumb_node(C, lang, [(C["nav"]["about"], url(lang, "about"))]),
          {"@type": "AboutPage", "url": url(lang, "about", absolute=True), "name": C["meta"]["about"][0], "about": {"@id": S.DOMAIN + "/#org"}, "inLanguage": S.HREFLANG[lang]}]
    out = head(C, lang, "about", *C["meta"]["about"], alt, ld) + header(C, lang, "about", alt) + page_head(C, lang, A["h1"], A["lede"], [(C["nav"]["about"], None)])
    out += f"""<section><div class="wrap split"><div><div class="mark"></div><h2>{esc(A['stand_title'])}</h2>{''.join(f'<p class="lede">{esc(p)}</p>' for p in A['stand'])}</div>
<div class="split-img">{picture('rock-cut-2', C['photos']['rock-cut-2'], '(min-width:56rem) 40vw, 100vw')}</div></div></section>
<section class="tint"><div class="wrap cols2"><div><div class="mark"></div><h2>{esc(A['glance_title'])}</h2></div>
<dl class="glance">{''.join(f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in A['glance'])}</dl></div></section>
<section><div class="wrap"><div class="sec-head"><h2>{esc(C['home']['people_title'])}</h2></div>
<div class="leaders">{''.join(f'<div class="leader"><h3>{esc(l["name"])}</h3><p class="role">{esc(l["role"])}</p><p>{esc(l["bio"])}</p></div>' for l in C['leaders'])}</div></div></section>
<section class="tint"><div class="wrap cols2"><div><div class="mark"></div><h2>{esc(C['home']['group_title'])}</h2><p>{esc(C['home']['group_intro'])}</p></div>
<ul class="cos">{''.join(f'<li>{esc(n)}<span>{esc(C["companies"]["civil_label"])}</span></li>' for n in S.CIVIL_COMPANIES)}<li>{esc(S.CRUSHER_COMPANY)}<span>{esc(C['companies']['crusher_label'])}</span></li></ul></div></section>
{cta(C, lang, A['cta_title'], A['cta_text'])}"""
    write(lang, S.PAGES["about"], out + footer(C, lang))


def page_capabilities(C, lang):
    K = C["capabilities"]
    alt = alt_fn("capabilities")
    ld = [crumb_node(C, lang, [(C["nav"]["capabilities"], url(lang, "capabilities"))]), faq_node(K["faq"], lang)]
    out = head(C, lang, "capabilities", *C["meta"]["capabilities"], alt, ld) + header(C, lang, "capabilities", alt) + page_head(C, lang, K["h1"], K["lede"], [(C["nav"]["capabilities"], None)])
    out += '<section><div class="wrap">'
    for g in C["groups"]:
        items = "".join(f"<li>{esc(i)}</li>" for i in g["items"])
        extra = ""
        if g["id"] == "steel":
            extra = f'<p><a class="tlink" href="{url(lang, article="peb-vs-conventional-construction")}">{esc(K["steel_link"])}</a></p>'
        if g["id"] == "water":
            extra = f'<p><a class="tlink" href="{url(lang, article="storm-drain-planning-in-layouts")}">{esc(K["water_link"])}</a></p>'
        img = f'<div class="cap-img">{picture(g["img"], C["photos"][g["img"]], "(min-width:56rem) 28vw, 100vw")}</div>' if g["img"] else ""
        out += f'<div class="cap{"" if g["img"] else " no-img"}" id="{g["id"]}"><h2>{esc(g["name"])}</h2><div><p>{esc(g["long"])}</p>{extra}<ul>{items}</ul></div>{img}</div>\n'
    out += f'</div></section><section class="tint"><div class="wrap"><div class="sec-head"><h2>{esc(C["ui"]["faq_title"])}</h2></div>{faq_html(C, K["faq"])}</div></section>'
    out += cta(C, lang)
    write(lang, S.PAGES["capabilities"], out + footer(C, lang))


def page_work(C, lang):
    W = C["work"]
    alt = alt_fn("work")
    ld = [crumb_node(C, lang, [(C["nav"]["work"], url(lang, "work"))]),
          {"@type": "CollectionPage", "name": C["meta"]["work"][0], "url": url(lang, "work", absolute=True), "inLanguage": S.HREFLANG[lang]}]
    out = head(C, lang, "work", *C["meta"]["work"], alt, ld) + header(C, lang, "work", alt) + page_head(C, lang, W["h1"], W["lede"], [(C["nav"]["work"], None)])
    for s in W["sections"]:
        out += f'<section class="work-sec" id="{s["id"]}"><div class="wrap"><h2>{esc(s["name"])}</h2><p>{esc(s["text"])}</p><div class="gallery">{"".join(shot(C, p, "(min-width:62rem) 33vw, (min-width:36rem) 50vw, 100vw") for p in s["photos"])}</div></div></section>\n'
    out += cta(C, lang) + lightbox(C)
    write(lang, S.PAGES["work"], out + footer(C, lang))


def page_plant(C, lang):
    P = C["plant"]
    alt = alt_fn("plant")
    out = head(C, lang, "plant", *C["meta"]["plant"], alt, [crumb_node(C, lang, [(C["nav"]["plant"], url(lang, "plant"))])]) + header(C, lang, "plant", alt) + page_head(C, lang, P["h1"], P["lede"], [(C["nav"]["plant"], None)])
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in P["rows"])
    out += f"""<section><div class="wrap"><table class="tbl"><thead><tr><th scope="col">{esc(P['th'][0])}</th><th scope="col">{esc(P['th'][1])}</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="tint"><div class="wrap"><div class="sec-head"><h2>{esc(P['photos_title'])}</h2></div><div class="strip">{''.join(shot(C, s, '(min-width:48rem) 33vw, 100vw', False) for s in P['photos'])}</div></div></section>
{cta(C, lang)}"""
    write(lang, S.PAGES["plant"], out + footer(C, lang))


def page_careers(C, lang):
    R = C["careers"]
    alt = alt_fn("careers")
    out = head(C, lang, "careers", *C["meta"]["careers"], alt, [crumb_node(C, lang, [(C["nav"]["careers"], url(lang, "careers"))])]) + header(C, lang, "careers", alt) + page_head(C, lang, R["h1"], R["lede"], [(C["nav"]["careers"], None)])
    mail = f"mailto:{S.EMAIL_CAREERS}?subject={R['subject'].replace(' ', '%20')}"
    out += f"""<section><div class="wrap"><div class="sec-head"><h2>{esc(R['why_title'])}</h2></div>
<ul class="principles light-principles">{''.join(f'<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for a, b in R['why'])}</ul></div></section>
<section class="tint"><div class="wrap cols2"><div><div class="mark"></div><h2>{esc(R['status_title'])}</h2></div><div><p class="lede rich">{rich(R['status'])}</p><p><a class="btn btn-navy" href="{mail}">{ico_mail()}{esc(R['apply'])}</a></p></div></div></section>"""
    write(lang, S.PAGES["careers"], out + footer(C, lang))


def page_insights(C, lang):
    I = C["insights"]
    alt = alt_fn("insights")
    items = [{"@type": "ListItem", "position": i, "url": url(lang, article=s, absolute=True), "name": ARTS[lang][s]["title"]} for i, s in enumerate(S.ARTICLES, 1)]
    ld = [crumb_node(C, lang, [(C["nav"]["insights"], url(lang, "insights"))]),
          {"@type": "Blog", "name": C["meta"]["insights"][0], "url": url(lang, "insights", absolute=True), "inLanguage": S.HREFLANG[lang], "publisher": {"@id": S.DOMAIN + "/#org"}},
          {"@type": "ItemList", "itemListElement": items}]
    out = head(C, lang, "insights", *C["meta"]["insights"], alt, ld) + header(C, lang, "insights", alt) + page_head(C, lang, I["h1"], I["lede"], [(C["nav"]["insights"], None)])
    first, rest = S.ARTICLES[0], S.ARTICLES[1:]
    out += f'<section><div class="wrap">{article_card(C, lang, first, True)}<div class="cards">{"".join(article_card(C, lang, s) for s in rest)}</div></div></section>' + cta(C, lang)
    write(lang, S.PAGES["insights"], out + footer(C, lang))


def render_blocks(blocks):
    o = ""
    for kind, val in blocks:
        if kind == "h2":
            o += f"<h2>{esc(val)}</h2>"
        elif kind == "p":
            o += f"<p>{esc(val)}</p>"
        elif kind == "ul":
            o += "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in val) + "</ul>"
        elif kind == "ol":
            o += "<ol>" + "".join(f"<li>{esc(i)}</li>" for i in val) + "</ol>"
    return o


def page_article(C, lang, slug):
    from urllib.parse import quote
    a = ARTS[lang][slug]
    alt = alt_fn(article=slug)
    u = url(lang, article=slug, absolute=True)
    cat = S.ARTICLE_CATS[slug]
    ld = [crumb_node(C, lang, [(C["nav"]["insights"], url(lang, "insights")), (a["title"], url(lang, article=slug))]),
          {"@type": "Article", "@id": u + "#article", "headline": a["title"], "description": a["desc"], "inLanguage": S.HREFLANG[lang], "articleSection": C["ui"]["cats"][cat],
           "datePublished": S.PUBLISHED, "dateModified": S.PUBLISHED, "mainEntityOfPage": u, "image": S.DOMAIN + "/assets/og-image.jpg",
           "author": {"@type": "Person", "name": "Mahendra Heda", "jobTitle": "Executive Director", "worksFor": {"@id": S.DOMAIN + "/#org"}},
           "publisher": {"@id": S.DOMAIN + "/#org"}},
          faq_node(a["faq"], lang)]
    out = head(C, lang, "insights", a["title"] + " | MCC Group", a["desc"], alt, ld, og_type="article") + header(C, lang, "insights", alt)
    out += page_head(C, lang, a["title"], None, [(C["nav"]["insights"], url(lang, "insights")), (a["title"], None)])
    key = "".join(f"<li>{esc(k)}</li>" for k in a["key"])
    related = [s for s in S.ARTICLES if s != slug and S.ARTICLE_CATS[s] == cat][:3]
    related += [s for s in S.ARTICLES if s != slug and s not in related][: 3 - len(related)]
    share = f"https://wa.me/?text={quote(a['title'] + ' ' + u)}"
    out += f"""<article class="article"><div class="wrap read">
<p class="meta">{esc(C['ui']['cats'][cat])} &middot; {esc(C['ui']['by'])} Mahendra Heda, {esc(C['leaders'][1]['role'])} &middot; <time datetime="{S.PUBLISHED}">{S.PUBLISHED}</time> &middot; {read_minutes(a)} {esc(C['ui']['min_read'])}</p>
<div class="insight-box"><h2>{esc(C['ui']['in_short'])}</h2><p>{esc(a['summary'])}</p><ul>{key}</ul></div>
{render_blocks(a['body'])}
<h2>{esc(C['ui']['faq_title'])}</h2>{faq_html(C, a['faq'])}
<div class="share on-light"><a class="btn btn-wa" href="{share}" target="_blank" rel="noopener">{wa_svg('#0f7d43')}{esc(C['ui']['share_wa'])}</a><a class="btn btn-line" href="{url(lang, 'insights')}">{esc(C['ui']['all_posts'])}</a></div>
</div></article>
<section class="tint"><div class="wrap"><div class="sec-head"><h2>{esc(C['ui']['related'])}</h2></div><div class="cards">{''.join(article_card(C, lang, s) for s in related)}</div></div></section>"""
    out += cta(C, lang)
    write(lang, S.PAGES["insights"] + slug + "/", out + footer(C, lang))


def page_contact(C, lang):
    T = C["contact"]
    F = C["form"]
    alt = alt_fn("contact")
    ld = [crumb_node(C, lang, [(C["nav"]["contact"], url(lang, "contact"))]), {"@type": "ContactPage", "url": url(lang, "contact", absolute=True), "inLanguage": S.HREFLANG[lang], "about": {"@id": S.DOMAIN + "/#org"}}]
    out = head(C, lang, "contact", *C["meta"]["contact"], alt, ld) + header(C, lang, "contact", alt) + page_head(C, lang, T["h1"], T["lede"], [(C["nav"]["contact"], None)])
    opts = "".join(f"<option>{esc(t)}</option>" for t in F["types"])
    a = S.ADDRESS
    out += f"""<section><div class="wrap contact-grid">
<div><h2>{esc(F['title'])}</h2><div class="alert"><p class="rich" style="margin:0">{rich(F['error'])}</p></div>
<form class="enq" method="post" action="/enquiry.php">
<input type="hidden" name="lang" value="{lang}">
<div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<div class="f"><label for="n">{esc(F['name'])}</label><input id="n" name="name" required maxlength="100" autocomplete="name"></div>
<div class="f"><label for="p">{esc(F['phone'])}</label><input id="p" name="phone" type="tel" required maxlength="20" autocomplete="tel" inputmode="tel"></div>
<div class="f"><label for="e">{esc(F['email'])}</label><input id="e" name="email" type="email" maxlength="120" autocomplete="email"></div>
<div class="f"><label for="t">{esc(F['type'])}</label><select id="t" name="type">{opts}</select></div>
<div class="f"><label for="m">{esc(F['message'])}</label><textarea id="m" name="message" required maxlength="2000"></textarea><small>{esc(F['message_hint'])}</small></div>
<div><button class="btn btn-navy" type="submit">{esc(F['send'])}</button></div>
<p class="note">{esc(F['note'])}</p></form></div>
<div><div class="quick on-light"><a class="btn btn-wa" href="{wa_link(C)}" target="_blank" rel="noopener">{wa_svg('#0f7d43')}{esc(C['ui']['wa_short'])}</a><a class="btn btn-navy" href="tel:{S.PHONE_OFFICE['tel']}">{ico_call()}{esc(C['ui']['call'])}</a><a class="btn btn-line" href="mailto:{S.EMAIL_ENQUIRY}">{ico_mail()}{esc(C['ui']['email_us'])}</a></div>
<h2>{esc(T['details_title'])}</h2><dl class="details-list">
<div><dt>{esc(C['ui']['phone_label'])}</dt><dd><a href="tel:{S.PHONE_OFFICE['tel']}">{S.PHONE_OFFICE['display']}</a></dd></div>
<div><dt>{esc(C['ui']['mobile_label'])}</dt><dd><a href="tel:{S.PHONE_MOBILE['tel']}">{S.PHONE_MOBILE['display']}</a> &middot; <a href="{wa_link(C)}" rel="noopener" target="_blank">{esc(C['ui']['chat_wa'])}</a></dd></div>
<div><dt>{esc(C['ui']['email_label'])}</dt><dd><a href="mailto:{S.EMAIL_ENQUIRY}">{S.EMAIL_ENQUIRY}</a></dd></div>
<div><dt>{esc(C['ui']['address_label'])}</dt><dd>{esc(a['street'])}, {esc(a['city'])} {esc(a['postal'])}<br><a href="{S.MAPS_URL}" rel="noopener" target="_blank">{esc(C['ui']['open_maps'])}</a></dd></div>
<div><dt>{esc(C['ui']['hours_label'])}</dt><dd>{esc(C['ui']['hours'])}</dd></div>
</dl></div></div></section>"""
    write(lang, S.PAGES["contact"], out + footer(C, lang))


def page_thanks(C, lang):
    T = C["thanks"]
    alt = lambda l: "/" + S.LANG_PREFIX[l] + "thank-you/"
    out = head(C, lang, "contact", T["title"], T["text"], alt, noindex=True) + header(C, lang, "contact", alt)
    out += f'<section class="center-page"><div class="wrap"><h1 style="font-size:clamp(2rem,5vw,3.4rem)">{esc(T["title"])}</h1><p class="lede rich">{rich(T["text"])}</p><a class="btn btn-navy" href="{url(lang, "home")}">{esc(T["back"])}</a></div></section>'
    write(lang, "thank-you/", out + footer(C, lang))


def page_404(C, lang):
    N = C["notfound"]
    alt = lambda l: url(l, "home")
    out = head(C, lang, "home", N["title"], N["text"], alt, noindex=True) + header(C, lang, "home", alt)
    out += f'<section class="center-page"><div class="wrap"><h1 style="font-size:clamp(2rem,5vw,3.4rem)">{esc(N["title"])}</h1><p class="lede">{esc(N["text"])}</p><div class="btns on-light"><a class="btn btn-navy" href="{url(lang, "home")}">{esc(N["home"])}</a><a class="btn btn-line" href="{url(lang, "capabilities")}">{esc(C["ui"]["see_capabilities"])}</a></div></div></section>'
    if lang == "en":
        open(os.path.join(DIST, "404.html"), "w", encoding="utf-8").write(out + footer(C, lang))


# ---------- site files ----------
def site_files():
    urls = []
    for key in S.PAGES:
        urls.append(lambda l, k=key: url(l, k))
    for slug in S.ARTICLES:
        urls.append(lambda l, s=slug: url(l, article=s))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for f in urls:
        for l in LANGS:
            xml.append(f"<url><loc>{S.DOMAIN}{f(l)}</loc><lastmod>{S.PUBLISHED}</lastmod>")
            for l2 in LANGS:
                xml.append(f'<xhtml:link rel="alternate" hreflang="{S.HREFLANG[l2]}" href="{S.DOMAIN}{f(l2)}"/>')
            xml.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{S.DOMAIN}{f("en")}"/></url>')
    xml.append("</urlset>")
    open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(xml))
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /enquiry.php\n\nSitemap: {S.DOMAIN}/sitemap.xml\n")
    c = LC["en"]
    ll = [f"# {S.BRAND}", "",
          "> MCC Group is a civil construction group based in Nagpur, Maharashtra, founded in 1984. It is a Class 1A registered contractor with PWD Maharashtra, has more than 120 people, and works in Maharashtra and Telangana. Roads, bridges, canals, dams, buildings, PEB structures and related civil works.", "",
          "## Key facts",
          f"- Founded: {S.FOUNDED}", "- Leadership: Sanjay Heda (Founder President), Mahendra Heda (Executive Director)",
          "- Group companies: " + ", ".join(S.CIVIL_COMPANIES) + " (civil construction); " + S.CRUSHER_COMPANY + " (stone crushing)",
          f"- Address: {S.ADDRESS['street']}, {S.ADDRESS['city']} {S.ADDRESS['postal']}", f"- Telephone: {S.PHONE_OFFICE['display']}; mobile and WhatsApp {S.PHONE_MOBILE['display']}", f"- Email: {S.EMAIL_ENQUIRY}", "- Office hours: Monday to Saturday, 10 AM to 6 PM IST", "", "## Pages"]
    for k in S.PAGES:
        if k != "home":
            ll.append(f"- [{c['nav'][k]}]({S.DOMAIN}{url('en', k)}): {c['meta'][k][1]}")
    ll += ["", "## Articles (by Mahendra Heda; English, Hindi and Marathi)"]
    for s in S.ARTICLES:
        ll.append(f"- [{ARTS['en'][s]['title']}]({S.DOMAIN}{url('en', article=s)}): {ARTS['en'][s]['desc']}")
    ll += ["", "## Languages", f"- English: {S.DOMAIN}/", f"- Hindi: {S.DOMAIN}/hi/", f"- Marathi: {S.DOMAIN}/mr/", ""]
    open(os.path.join(DIST, "llms.txt"), "w", encoding="utf-8").write("\n".join(ll))
    open(os.path.join(DIST, "manifest.webmanifest"), "w").write(json.dumps({"name": "MCC Group", "short_name": "MCC", "start_url": "/", "display": "browser", "background_color": "#f8f9f8", "theme_color": "#0f1c26",
                                                                           "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}))
    open(os.path.join(DIST, ".htaccess"), "w").write("""# MCC Group static site (Apache / cPanel)
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html
RedirectMatch 404 ^/api/

# Enable after SSL is installed and working:
# RewriteEngine On
# RewriteCond %{HTTPS} off
# RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [L,R=301]

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json application/xml image/svg+xml
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType text/css "access plus 1 month"
ExpiresByType application/javascript "access plus 1 month"
ExpiresByType text/html "access plus 0 seconds"
</IfModule>
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
""")


PHP = r"""<?php
// Enquiry handler for mccgroup.in. Sends the enquiry to the sales mailbox and redirects to the thank-you page.
$to = 'info@mccgroup.in';
$from = 'no-reply@mccgroup.in';
$thanks = ['en' => '/thank-you/', 'hi' => '/hi/thank-you/', 'mr' => '/mr/thank-you/'];
$contact = ['en' => '/contact/', 'hi' => '/hi/contact/', 'mr' => '/mr/contact/'];
$lang = isset($_POST['lang']) && isset($thanks[$_POST['lang']]) ? $_POST['lang'] : 'en';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: ' . $contact[$lang]); exit; }
if (!empty($_POST['website'])) { header('Location: ' . $thanks[$lang]); exit; } // honeypot: pretend success

function clean($v, $max, $multiline = false) {
    $v = isset($v) ? trim((string)$v) : '';
    $v = $multiline ? str_replace("\r", '', $v) : preg_replace('/[\r\n]+/', ' ', $v);
    return mb_substr($v, 0, $max);
}
$name = clean($_POST['name'] ?? '', 100);
$phone = clean($_POST['phone'] ?? '', 20);
$email = clean($_POST['email'] ?? '', 120);
$type = clean($_POST['type'] ?? '', 100);
$msg = clean($_POST['message'] ?? '', 2000, true);

$fail = $name === '' || $phone === '' || $msg === '' || ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL));
if ($fail) { header('Location: ' . $contact[$lang] . '?error=1'); exit; }

$subject = '=?UTF-8?B?' . base64_encode('Website enquiry: ' . $name) . '?=';
$body = "Name: $name\nPhone: $phone\nEmail: " . ($email ?: '-') . "\nType of work: $type\nLanguage of page: $lang\n\n$msg\n";
$headers = "From: MCC Group Website <$from>\r\n";
if ($email !== '') { $headers .= "Reply-To: $email\r\n"; }
$headers .= "Content-Type: text/plain; charset=UTF-8\r\nMIME-Version: 1.0\r\n";

if (@mail($to, $subject, $body, $headers)) { header('Location: ' . $thanks[$lang]); }
else { header('Location: ' . $contact[$lang] . '?error=1'); }
exit;
"""


LC = {}
ARTS = {}


def main():
    for l in S.LANGS:
        LC[l] = importlib.import_module(f"content_{l}").C if os.path.exists(os.path.join(ROOT, "tools", f"content_{l}.py")) else None
        if os.path.exists(os.path.join(ROOT, "tools", f"articles_{l}.py")):
            ARTS[l] = dict(importlib.import_module(f"articles_{l}").A)
            ARTS[l].update(importlib.import_module(f"articles2_{l}").A2)
        else:
            ARTS[l] = None
        if LC[l] is not None:
            extras.apply(LC[l], l)
    for l in LANGS:
        if LC[l] is None or ARTS[l] is None:
            sys.exit(f"missing content for {l}")
    for l in S.LANGS:  # hreflang needs labels for all languages even in subset builds
        if LC[l] is None:
            LC[l] = LC["en"]
            ARTS[l] = ARTS["en"]
    for l in LANGS:
        C = LC[l]
        page_home(C, l); page_about(C, l); page_capabilities(C, l); page_work(C, l); page_plant(C, l)
        page_careers(C, l); page_insights(C, l); page_contact(C, l); page_thanks(C, l); page_404(C, l)
        for s in S.ARTICLES:
            page_article(C, l, s)
    site_files()
    open(os.path.join(DIST, "enquiry.php"), "w").write(PHP)
    print("built:", ",".join(LANGS))


if __name__ == "__main__":
    main()
