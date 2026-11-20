"""HTML templates for vterinka.cz (plain f-strings, no dependencies). Design "Hodinářská dílna" — see static/assets/site.css.

A watchmaker's bench: ivory paper (#F4EFE4), ink (#16181D), dial blue (#1F3A5F) for the brand and links, bordeaux
(#962B2B) only for sales and the call to action, brass for minute-track marks. Hard offset shadows, price labels cut like
a jeweller's hang tag, a dial drawing with the case diameter on watch pages. Illustrations from Canva (one sheet, one hand).
"""
import html
import math
import json
import re
from urllib.parse import quote

import taxonomy as X

E = html.escape
PER_PAGE = 30          # Kenny 16. 11. 2026: 30 products per listing page, then a clear link to the next page
SUFFIX = " | Vteřinka"
# prerender on hover; never /go/ (a prerender would count as a click at the network), /data/ or the search page
SPECULATION = ('<script type="speculationrules">{"prerender":[{"where":{"and":[{"href_matches":"/*"},{"not":{"href_matches":"/data/*"}},'
               '{"not":{"href_matches":"/go/*"}},{"not":{"href_matches":"/hledat/*"}},'
               '{"not":{"selector_matches":"[rel~=nofollow],[target=_blank]"}}]},"eagerness":"moderate"}]}</script>')
SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>'
RULER_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="6"/>'
              '<path d="M9 6.5 9.6 2h4.8l.6 4.5M9 17.5l.6 4.5h4.8l.6-4.5M12 9v3l2 1.5"/></svg>')
SWATCH = {"bila": "#FFFFFF", "cerna": "#1E1E1E", "seda": "#8F9399", "hneda": "#7A5236", "zelena": "#3F6B4F", "modra": "#2F4E86",
          "ruzova": "#E7B3B8", "cervena": "#A3262A", "zlata": "#C9A043", "ruzove-zlata": "#D9A08B", "stribrna": "#C9CCCF"}
OPERATOR = {"name": "Ha Duy Huy", "address": "Bartáková 36, 140 00 Praha", "ico": "07876823", "ds": "dxmsrdt",
            "vat": "není plátce DPH", "email": "info@vterinka.cz"}   # public business-register data (ARES), the site operator on legal pages
LOGO = '<img src="/img/ui/logo.svg" alt="vteřinka" width="150" height="44">'
LOGO_LIGHT = '<img src="/img/ui/logo-light.svg" alt="vteřinka" width="150" height="44">'
FOOT_A = ["panske-hodinky", "damske-hodinky", "detske-hodinky", "unisex-hodinky", "kapesni-hodinky"]
FOOT_B = ["prsteny", "nausnice", "nahrdelniky", "naramky", "snubni-prsteny"]
# header strip: categories, not departments (a watch shopper thinks "pánské hodinky", not "Hodinky")
# header/home icon menu: watches first (by who wears them, then by type), jewellery after (search volume CZ 11/2026: snubní prsteny 5 500, náušnice 5 400, náhrdelník 3 600, prsteny 2 800, náramek 2 200)
NAV = ["panske-hodinky", "damske-hodinky", "detske-hodinky", "digitalni-hodinky", "klasicke-hodinky", "sportovni-hodinky",
       "prsteny", "nausnice", "nahrdelniky", "naramky", "snubni-prsteny"]
# watch types are cross-gender hub pages (landings), not categories: slug -> (menu name, icon file)
NAV_HUBS = {"digitalni-hodinky": ("Digitální hodinky", "digitalni-hodinky"), "klasicke-hodinky": ("Klasické hodinky", "klasicke-hodinky"),
            "sportovni-hodinky": ("Sportovní hodinky", "sportovni-hodinky")}
FOOT_DEPTS = ["privesky", "reminky", "sperkovnice", "retizky", "koralky-na-naramky", "piercing", "broze", "sperkove-soupravy", "manzetove-knoflicky", "boxy-na-hodinky"]


def kc(n):
    return f"{int(round(n)):,}".replace(",", " ") + " Kč"


def plural(n, one, few, many):
    return one if n == 1 else few if 1 < n < 5 else many


def shops_in(n):
    return f"v {n} obchodě" if n == 1 else f"ve {n} obchodech" if n in (2, 3, 4) else f"v {n} obchodech"


def shorten(text, limit, keep_tail=""):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    tail = keep_tail if keep_tail and text.endswith(keep_tail) else ""
    room = limit - len(tail) - 1
    head = text[:len(text) - len(tail)][:room].rsplit(" ", 1)[0].rstrip(" ,;:-–—(")
    return head + "…" + tail


def shorten_mid(text, limit):
    """Shorten from the middle: product names say what it is first and which variant last ("… 142/196 cm, levá"),
    so cutting the end made thousands of variants share one title (SEO lint 12. 11. 2026: 2 705 duplicates)."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    words = text.split(" ")
    tail = []
    while words and len(" ".join(tail + words[-1:])) <= limit * 0.4:
        tail = words[-1:] + tail
        words = words[:-1]
    while tail and tail[0].strip(",;:").lower() in ("cm", "mm", "m", "ks", "x", "×", "/", "-", "–"):   # never open with a lone unit
        tail = tail[1:]
    head =shorten(" ".join(words), limit - len(" ".join(tail)) - 1)
    return (head.rstrip("…").rstrip(" ,;:-–—(") + "… " + " ".join(tail)).strip() if tail else head


DOTIDOT = "https://image.dotidot.io/image_generator/"


def img_url(u, size="card"):
    """Smaller renditions — we never resize anything ourselves (0 CPU on Cloudflare).
    XXXLutz (Amplience) measured 11. 11. 2026: feed preset 44 kB -> ?fmt=webp&w=400 5 kB; Shoptet has its own presets.
    Every other shop sends originals (ezidle 136 kB, Upgates 555 kB PNG): those go through wsrv.nl (free image CDN, Kenny
    12. 11. 2026) as WebP at the size we show; when wsrv cannot deliver one, app.js (fixImg) shows the original."""
    if not u:
        return u
    card = size == "card"
    thumb = size == "thumb"      # 64 px gallery thumbnails
    if u.startswith(DOTIDOT):        # dotidot answers every image with a 302 to its storage host: skip the hop
        u = "https://dotidot-production-control-app-control-app-images.storage.dotidot.io/" + u[len(DOTIDOT):]
    if "a.allegroimg.com/original/" in u:     # Allegro renditions by path (wsrv.nl cannot fetch Allegro): s360 cards, s720 detail
        return u.replace("/original/", "/s128/" if thumb else "/s360/" if card else "/s720/")
    if "img2.ans-media.com/i/" in u:        # Answear renditions by path: 855x1290 (feed) -> 400x600 for cards (36 kB WebP)
        return re.sub(r"/i/\d+x\d+/", "/i/128x192/" if thumb else "/i/400x600/" if card else "/i/855x1290/", u)
    if "cdn.myshoptet.com" in u and "/user/shop/orig/" in u:
        return u.replace("/user/shop/orig/", "/user/shop/detail/" if (card or thumb) else "/user/shop/big/")
    if u.startswith("https://") and "cdn.myshoptet.com" not in u and "wsrv.nl" not in u:
        return f"https://wsrv.nl/?url={quote(u, safe='')}&w={128 if thumb else 480 if card else 960}&we&output=webp&q=78"
    return u


# Slot widths for `sizes`: two cards per row on phones, ~240 px cards on desktop; the gallery is full width below 980 px.
CARD_SIZES = "(max-width:640px) 46vw, 260px"
MAIN_SIZES = "(max-width:980px) 92vw, 600px"
_SRCSET = {   # host -> (pattern, {size: [(width, replacement), ...]}); renditions measured 19. 11. 2026
    "a.allegroimg.com/": (r"/s\d+/", {"card": [(240, "/s240/"), (360, "/s360/"), (512, "/s512/")],
                                      "main": [(360, "/s360/"), (512, "/s512/"), (720, "/s720/")]}),
    "img2.ans-media.com/i/": (r"/i/\d+x\d+/", {"card": [(300, "/i/300x450/"), (400, "/i/400x600/")],
                                                "main": [(400, "/i/400x600/"), (540, "/i/540x813/"), (855, "/i/855x1290/")]}),
    "wsrv.nl/": (r"&w=\d+", {"card": [(240, "&w=240"), (360, "&w=360"), (480, "&w=480")],
                             "main": [(480, "&w=480"), (720, "&w=720"), (960, "&w=960")]}),
}


def img_srcset(u, size="card"):
    """srcset for a shop picture (same renditions as img_url, several widths): a phone takes the smallest one that fills
    its slot instead of the desktop size. Empty when the host has no width presets (the plain src is used)."""
    src = img_url(u, size)
    for host, (rx, sizes) in _SRCSET.items():
        if src and host in src and re.search(rx, src):
            return ", ".join(re.sub(rx, rep, src, count=1) + f" {w}w" for w, rep in sizes[size])
    return ""


def img_host(u):
    """Origin of a picture (for preconnect and the CSP img-src list)."""
    m = re.match(r"https://[^/?#]+", u or "")
    return m.group(0) if m else ""


def pager_html(path, cur, pages, total=0, per=0):
    """Page numbers; on listings (total given) also a full-width "Další strana · 31–60 z 3 417" link above them, a plain
    crawlable link, so people and Google move on to the next page instead of only a small arrow."""
    if pages <= 1:
        return ""
    url = lambda k: path if k == 1 else f"{path}strana-{k}/"
    show = sorted({1, pages, cur - 2, cur - 1, cur, cur + 1, cur + 2} & set(range(1, pages + 1)))
    out, last = [], 0
    for k in show:
        if k - last > 1:
            out.append('<span class="gap">…</span>')
        out.append(f'<a aria-current="page" class="on">{k}</a>' if k == cur else f'<a href="{url(k)}">{k}</a>')
        last = k
    prev = f'<a class="pp" href="{url(cur - 1)}" rel="prev" aria-label="Předchozí strana">‹</a>' if cur > 1 else ""
    nxt = f'<a class="pp" href="{url(cur + 1)}" rel="next" aria-label="Další strana">›</a>' if cur < pages else ""
    big = ""
    if total and per and cur < pages:
        a, b, tot = cur * per + 1, min((cur + 1) * per, total), f"{total:,}".replace(",", "\u00a0")
        big = (f'<a class="pnext" href="{url(cur + 1)}">Další strana <small>{a}–{b} z {tot}</small>'
               '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M7 4l6 6-6 6" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></a>')
    return f'<nav class="pager" aria-label="Stránkování">{big}{prev}{"".join(out)}{nxt}</nav>'


def ld(x):
    return f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>'


def swatches(colors, n=4):
    if not colors:
        return ""
    return '<span class="sw">' + "".join(f'<i style="--c:{SWATCH[c]}" title="{X.COLOR_NAME[c]}"></i>' for c in colors[:n]) + "</span>"


def dims_svg(dm):
    """A watch face drawn to the case diameter, with the diameter arrow; ring size as a plain figure. Only real values."""
    if dm.get("size"):
        return (f'<figure class="dial"><svg viewBox="0 0 220 156" role="img" aria-label="Velikost prstenu {dm["size"]}"><circle cx="110" cy="66" r="46" class="face"/>'
                f'<circle cx="110" cy="66" r="34" class="face"/><text x="110" y="72" text-anchor="middle" font-size="18">{E(dm["size"])}</text>'
                f'<path d="M76 126h68M76 121v10M144 121v10" class="dm"/><text x="110" y="148" text-anchor="middle">obvod {E(dm["size"])} mm</text></svg>'
                f'<figcaption>Velikost prstenu = vnitřní obvod v milimetrech (EU)</figcaption></figure>')
    w = dm.get("w")
    if not w:
        return ""
    r = 30 + (min(max(w, 26), 50) - 26) * 1.6          # 26 mm -> r 30, 50 mm -> r 68: bigger cases look bigger
    cx, cy = 110, r + 8
    ticks = []
    for i in range(60):
        a_ = math.radians(i * 6)
        r0 = r - (9 if i % 5 == 0 else 5)
        ticks.append(f'<path d="M{cx + r0 * math.sin(a_):.1f} {cy - r0 * math.cos(a_):.1f}L{cx + (r - 2) * math.sin(a_):.1f} {cy - (r - 2) * math.cos(a_):.1f}" class="{"tick5" if i % 5 == 0 else "tick"}"/>')
    hands = (f'<path d="M{cx} {cy:.1f}L{cx} {cy - r * 0.55:.1f}" class="tick5"/><path d="M{cx} {cy:.1f}L{cx + r * 0.62:.1f} {cy + r * 0.12:.1f}" class="tick5"/>'
             f'<path d="M{cx} {cy + r * 0.2:.1f}L{cx - r * 0.3:.1f} {cy - r * 0.68:.1f}" class="dm"/><circle cx="{cx}" cy="{cy:.1f}" r="2.5"/>')
    y = cy + r + 14
    return (f'<figure class="dial"><svg viewBox="0 0 220 {y + 22:.0f}" role="img" aria-label="Průměr pouzdra {X.cz(w)} mm">'
            f'<circle cx="{cx}" cy="{cy:.1f}" r="{r:.1f}" class="face"/>{"".join(ticks)}{hands}'
            f'<path d="M{cx - r:.1f} {y:.1f}h{2 * r:.1f}M{cx - r:.1f} {y - 5:.1f}v10M{cx + r:.1f} {y - 5:.1f}v10" class="dm"/>'
            f'<text x="{cx}" y="{y + 18:.1f}" text-anchor="middle">průměr pouzdra {X.cz(w)} mm</text></svg>'
            f'<figcaption>Kresba v poměru k velikosti pouzdra</figcaption></figure>')


def shop_logo(m, big=False):
    """<img> of a shop's logo (kuponmat library, trimmed WebP in static/img/shops), display size balanced by sqrt of the aspect ratio; "" without a logo."""
    if not m.get("logo"):
        return ""
    w, h = m["lw"], m["lh"]
    area, mw, mh = (6200, 170, 56) if big else (3600, 112, 38)
    k = (area / (w * h)) ** 0.5
    dw, dh = w * k, h * k
    f = min(1, mw / dw, mh / dh)
    return (f'<img class="slogo{" slogo--big" if big else ""}" src="{m["logo"]}" alt="{E(m["name"])}" width="{round(dw * f)}" height="{round(dh * f)}" loading="lazy" decoding="async">')


class Site:
    def __init__(self, base, env, ga, css, js, shops, stats):
        self.base, self.env, self.ga, self.css, self.js = base, env, ga, css, js
        self.shops = shops
        self.stats = stats
        self.pg = None
        self.pg_noindex = False
        self.pending_ld = None
        self.nav_ok = None
        self.footer_links = []
        self.has_guides = False

    def url(self, path):
        return self.base + path

    def layout(self, path, title, desc, body, crumbs=None, noindex=False, jsonld=None, preload_img=None, og_img=None, full=False, og_type="website"):
        pn = self.pg[1] if self.pg and self.pg[1] > 1 else 0      # room for " – strana N" / "Strana N: " (SEO lint 19. 11.: 405 paginated titles > 75)
        title = shorten(title, 68 - (len(f" – strana {pn}") if pn else 0), SUFFIX)       # BEFORE the suffix, so paginated titles stay distinct
        desc = shorten(desc, 160 - (len(f"Strana {pn}: ") if pn else 0))
        robots = "noindex,follow" if (noindex or self.pg_noindex or self.env != "production") else "index,follow,max-image-preview:large"
        if self.pg and self.pg[1] > 1:
            n = self.pg[1]
            path = f"{self.pg[0]}strana-{n}/"
            title = title.replace(SUFFIX, f" – strana {n}{SUFFIX}") if title.endswith(SUFFIX) else f"{title} – strana {n}"
            desc = f"Strana {n}: {desc}"
            jsonld = [x for x in (jsonld or []) if x and x.get("@type") != "FAQPage"]
            body = re.sub(r'<section class="faq">.*?</section>', "", body, flags=re.S)
            body = re.sub(r'<div class="prose">.*?</div><!--/prose-->', "", body, flags=re.S)
            body = re.sub(r"</h1>", f' <small class="pgn">strana {n}</small></h1>', body, count=1)
        lds = list(jsonld or [])
        if self.pending_ld:
            lds.append(self.pending_ld)
            self.pending_ld = None
        head_ld = "".join(ld(x) for x in lds if x)
        cr = ""
        if crumbs:
            head_ld += ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": self.url(u)} for i, (n, u) in enumerate(crumbs)]})
            cr = '<nav class="crumbs" aria-label="Drobečková navigace">' + "<i>/</i>".join(
                f'<a href="{u}">{E(n)}</a>' if i < len(crumbs) - 1 else f"<span>{E(n)}</span>" for i, (n, u) in enumerate(crumbs)) + "</nav>"
        # preload_img: "url" or (url, srcset, sizes) - with a srcset the phone preloads only the rendition it will show
        pre_u, pre_ss, pre_sz = (preload_img if isinstance(preload_img, tuple) else (preload_img, "", ""))
        pre = ""
        if pre_u:
            pre = (f'<link rel="preload" as="image" href="{E(pre_u)}"' + (f' imagesrcset="{E(pre_ss)}" imagesizes="{E(pre_sz)}"' if pre_ss else "")
                   + ' fetchpriority="high">')
        host = img_host(pre_u) if pre_u and pre_u.startswith("https://") else ""
        pc = f'<link rel="preconnect" href="{host}">' if host else ('<link rel="preconnect" href="https://wsrv.nl">' if "wsrv.nl/" in body else "")
        ga = ""
        if self.ga and self.env == "production":
            boot = ('window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}'
                    'var g="denied";try{if(localStorage.getItem("vt-consent")==="yes")g="granted"}catch(e){}'
                    'gtag("consent","default",{analytics_storage:g,ad_storage:"denied",ad_user_data:"denied",ad_personalization:"denied",wait_for_update:500});'
                    'gtag("set","ads_data_redaction",true);')
            if self.ga.startswith("GTM-"):
                lib = f'dataLayer.push({{"gtm.start":Date.now(),event:"gtm.js"}});</script><script async src="https://www.googletagmanager.com/gtm.js?id={self.ga}"></script>'
            else:
                lib = f'gtag("js",new Date());gtag("config","{self.ga}");</script><script async src="https://www.googletagmanager.com/gtag/js?id={self.ga}"></script>'
            ga = f'<meta name="ga4" content="{self.ga}"><script>{boot}{lib}'
        content = body if full else f'<div class="wrap page">{cr}{body}</div>'
        if full and crumbs:
            content = content.replace("<!--crumbs-->", cr, 1)
        ok = self.nav_ok
        cok = getattr(self, "cat_ok", None)
        hubs_ok = getattr(self, "hub_ok", None)
        nav = "".join(f'<li><a href="/{k}/"><img src="/img/ic/72/{NAV_HUBS[k][1] if k in NAV_HUBS else X.ICON[k]}.webp" alt="" width="36" height="36" loading="lazy">{E(NAV_HUBS[k][0] if k in NAV_HUBS else X.CATS[k][0])}</a></li>'
                      for k in NAV if (k in NAV_HUBS and (hubs_ok is None or k in hubs_ok)) or (k not in NAV_HUBS and (cok is None or k in cok))) + '<li><a href="/kategorie/"><img src="/img/ic/72/sperky.webp" alt="" width="36" height="36" loading="lazy">Vše</a></li>'
        more = "".join(f'<li><a href="/{k}/">{E(X.CATS[k][0])}</a></li>' for k in FOOT_DEPTS if cok is None or k in cok)
        og = og_img or f"{self.base}/img/ui/og.png"
        n_shops = self.stats["shops"]
        return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{self.url(path)}"><meta name="robots" content="{robots}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{self.url(path)}"><meta property="og:type" content="{og_type}"><meta property="og:locale" content="cs_CZ"><meta property="og:site_name" content="Vteřinka"><meta property="og:image" content="{E(og)}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1F3A5F"><link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-192.png" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="/favicon-180.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/bodoni-cs.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/hanken-cs.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/{self.css}">{pc}{pre}{SPECULATION}{ga}{head_ld}</head><body>
<a class="skip" href="#main">Přeskočit na obsah</a>
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="Vteřinka – úvod">{LOGO}</a>
<form class="search" role="search" action="/hledat/" method="get"><label class="sr" for="q">Hledat hodinky, šperky, značku nebo obchod</label>{SEARCH_ICON}<input id="q" name="q" type="search" placeholder="Prim automat, Casio Edifice, stříbrné náušnice…" autocomplete="off"><button type="submit">Hledat</button><div class="sugg" id="sugg" role="listbox"></div></form>
<nav class="hl" aria-label="Rychlé odkazy"><a href="/slevy/">Slevy</a>{'<a href="/poradna/">Poradna</a>' if self.has_guides else ""}</nav></div>
<nav class="rooms" aria-label="Kategorie"><div class="wrap"><ul>{nav}</ul></div></nav></header>
<main id="main">{content}</main>
<footer><div class="wrap cols"><div class="fabout"><a class="logo" href="/">{LOGO_LIGHT}</a><p>Vteřinka srovnává ceny hodinek a šperků z {n_shops} českých e‑shopů. Nic neprodáváme: nakoupíte přímo v obchodě za stejnou cenu. Když nakoupíte přes náš odkaz, obchod nám může zaplatit provizi. Z ní web žije a pořadí nabídek neovlivňuje.</p></div>
<div><h3>Hodinky</h3><ul>{self.flinks(FOOT_A)}{"".join(f'<li><a href="{u}">{E(t)}</a></li>' for u, t in self.footer_links)}<li><a href="/kategorie/">Všechny kategorie</a></li></ul></div>
<div><h3>Šperky</h3><ul>{self.flinks(FOOT_B)}<li><a href="/slevy/">Hodinky a šperky ve slevě</a></li></ul></div>
<div><h3>Další</h3><ul>{more}<li><a href="/obchody/">Obchody A–Z</a></li></ul></div>
<div><h3>Vteřinka</h3><ul><li><a href="/jak-srovnavame/">Jak srovnáváme</a></li>{'<li><a href="/poradna/">Poradna</a></li>' if self.has_guides else ""}{'<li><a href="/studie/">Datové studie</a></li>' if getattr(self, "has_studies", False) else ""}<li><a href="/obchody/">Obchody</a></li><li><a href="/znacky/">Značky</a></li><li><a href="/kontakt/">Kontakt</a></li><li><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a></li><li><a href="#" id="consent-open">Nastavení cookies</a></li></ul></div></div>
<div class="wrap fine"><p>Ceny, parametry a dostupnost přebíráme od obchodů a mohou se změnit; platí údaj v e‑shopu v okamžiku nákupu. Poslední aktualizace {self.stats["updated"]}.</p>
<p>Provozovatel: {OPERATOR["name"]}, {OPERATOR["address"]}, IČO {OPERATOR["ico"]}, {OPERATOR["vat"]}. <a href="/kontakt/">Kontakt</a> · <a href="mailto:{OPERATOR["email"]}">{OPERATOR["email"]}</a></p></div></footer>
<div class="consent" id="consent" role="dialog" aria-label="Cookies" hidden><p>Smíme měřit návštěvnost (Google Analytics)? Bez souhlasu nic neměříme.</p>
<div class="row"><button class="btn" data-consent="yes">Souhlasím</button><button class="btn btn--g" data-consent="no">Nesouhlasím</button><a href="/ochrana-osobnich-udaju/" class="lnk">Více</a></div></div>
<script src="/assets/{self.js}" defer></script></body></html>"""

    # ------------------------------------------------------------ pieces

    def flinks(self, cats):
        ok = getattr(self, "cat_ok", None)
        return "".join(f'<li><a href="/{k}/">{E(X.CATS[k][0])}</a></li>' for k in cats if ok is None or k in ok)

    def shop(self, sid):
        return self.shops.get(sid, {"name": sid, "color": "#888"})

    def go_attrs(self, shop):
        return f'rel="sponsored nofollow noopener" target="_blank" data-go="{E(shop)}"'

    @staticmethod
    def discount(p):
        o = p["offers"][0]
        if o.get("was") and o["was"] > o["price"]:
            d = round((o["was"] - o["price"]) / o["was"] * 100)
            return d if d <= 80 else 0      # "−95 %" is a broken "was" price in the feed, not a real sale
        return 0

    def tag(self, price, prefix="", big=False, was=0):
        pre = f"<small>{prefix}</small>" if prefix else ""
        old = f"<s>{kc(was)}</s>" if was and was > price else ""
        return f'<span class="ptag{" ptag--xl" if big else ""}">{pre}{old}<b>{kc(price)}</b></span>'

    @staticmethod
    def tape(p):
        dm = p.get("dims") or {}
        if p.get("sizes") and len(p["sizes"]) > 1:
            return f'{len(p["sizes"])} rozměry' if len(p["sizes"]) < 5 else f'{len(p["sizes"])} rozměrů'
        return X.size_label(dm)

    def card(self, p, lazy=True):
        n = len(p["offers"])
        href = f'/produkt/{p["slug"]}/'
        img = E(img_url(p["img"]) or "/img/ui/placeholder.svg")
        ss = img_srcset(p["img"]) if p["img"] else ""
        if ss:
            img += f'" srcset="{E(ss)}" sizes="{CARD_SIZES}'
        # lazy=True below the fold; "high" = the first row (LCP candidates), False = eager without priority
        load = ' loading="lazy" decoding="async"' if lazy is True else (' fetchpriority="high"' if lazy == "high" else "")
        d = self.discount(p)
        sale = f'<span class="flag">−{d} %</span>' if d >= 10 else ""
        tp = self.tape(p)
        tape = f'<span class="tape">{E(tp)}</span>' if tp else ""
        nv = len(p.get("variants") or [])
        meta = shops_in(n) + (f" · {nv} {plural(nv, 'varianta', 'varianty', 'variant')}" if nv > 1 else "")
        alt_u = next((img_url(u) for u in p.get("imgs") or [] if u and u != p["img"]), "")
        alt = f' data-alt="{E(alt_u)}"' if alt_u and p["img"] else ""
        best = p["offers"][0]
        go, ga = E(best["go"]), self.go_attrs(best["shop"])
        where = ("nejlevněji " if n > 1 else "") + self.shop(best["shop"])["name"]
        return (f'<li class="pc"><a class="pc__img" href="{go}" {ga} tabindex="-1" aria-hidden="true"><img src="{img}" alt=""{load}{alt} referrerpolicy="no-referrer" width="400" height="400">{sale}{tape}</a>'
                f'<div class="pc__b"><span class="pc__brand">{E(p["brand"])}</span><h3><a href="{go}" {ga}>{E(p["name"])}</a></h3>'
                f'{swatches(p.get("colors")) or "<span class=sw></span>"}<div class="pc__f">{self.tag(p["price"], "od" if (n > 1 or nv > 1) else "")}<span class="pc__n">{meta}</span></div>'
                f'<div class="pc__a"><span class="pc__w">{E(where)}</span><a class="pc__d" href="{href}">Detail</a></div></div></li>')

    def item_json(self, p, bidx):
        """Compact row for client-side filtering:
        [name, slug, img, price, shops, brand#, colors, mats, styles, wmin, wmax, discount, shopids, variants, tape, feats,
         go (cheapest offer), its shop, height, depth, sizes, shapes, seats, category facets ["key:value"]]"""
        dm = p.get("dims") or {}
        return [p["name"], p["slug"], img_url(p["img"]), p["price"], len(p["offers"]), bidx.get(p["brand"], -1), p["colors"], p["mats"], p["styles"],
                p["wmin"] or 0, p["wmax"] or 0, self.discount(p), [o["shop"] for o in p["offers"]], len(p.get("variants") or []), self.tape(p), p["feats"],
                p["offers"][0]["go"], p["offers"][0]["shop"], dm.get("h") or 0, dm.get("d") or 0, p.get("sizes") or [], p.get("shape") or [], p.get("seats") or 0,
                [f"{k}:{v}" for k, vs in (p.get("fx") or {}).items() for v in vs]]

    def grid(self, items, first_lazy=True, cls="grid"):
        return f'<ul class="{cls}">' + "".join(self.card(p, lazy=True if (first_lazy or i > 3) else ("high" if i < 2 else False)) for i, p in enumerate(items)) + "</ul>"

    def faq(self, qa):
        if not qa:
            return "", None
        h = '<section class="faq"><h2>Časté otázky</h2>' + "".join(f"<details><summary>{E(q)}</summary><div>{a}</div></details>" for q, a in qa) + "</section>"
        data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in qa]}
        return h, data

    def tiles(self, cats, cls="subtiles", size=56):
        """Equal tiles (icon, name in max. 2 lines, count) for categories: one size for all, whatever the name length."""
        if not cats:
            return ""
        return f'<ul class="{cls}">' + "".join(
            f'<li><a href="/{k}/"><img src="/img/ic/{icon or X.ICON[k]}.webp" alt="" width="{size}" height="{size}" loading="lazy"><span>{E(name.partition("|")[0])}{('<span class="sr"> ' + E(name.partition("|")[2]) + "</span>") if "|" in name else ""}</span><small>{n} {plural(n, "kus", "kusy", "kusů")}</small></a></li>'
            for k, name, n, *ic in cats for icon in [ic[0] if ic else None]) + "</ul>"

    def chips(self, links, cls="chips"):
        return f'<ul class="{cls}">' + "".join(f'<li><a href="{u}">{E(t)}{f"<small>{n}</small>" if n else ""}</a></li>' for u, t, n in links) + "</ul>" if links else ""

    def listing(self, items, json_url, order="pop", facets=None):
        path, cur, pages = self.pg or ("", 1, 1)
        chunk = items[(cur - 1) * PER_PAGE:cur * PER_PAGE]
        self.pending_ld = {"@context": "https://schema.org", "@type": "ItemList", "numberOfItems": len(items),
                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": self.url(f'/produkt/{p["slug"]}/'), "name": p["name"]}
                                               for i, p in enumerate(chunk[:24], (cur - 1) * PER_PAGE)]} if chunk else None
        facets = facets or {}
        filt = self.filters(items, facets)
        n = len(items)
        cats = facets.get("cats")
        refine = (f'<nav class="refine" data-scroll aria-label="{E(facets.get("cats_label", "Upřesnit"))}"><span>{E(facets.get("cats_label", "Upřesnit"))}:</span>'
                  + "".join(f'<a href="{u}">{E(t)}</a>' for u, t, _ in cats[:40]) + "</nav>") if cats else ""
        return (f'<div class="layout">{refine}{filt}<div class="factive" id="factive" hidden></div><div class="results"><div class="listhead"><p><b id="count">{n}</b> {plural(n, "kus", "kusy", "kusů")}</p>'
                f'<label class="sort">Řadit <select id="sort"><option value="pop">doporučené</option><option value="price"{" selected" if order == "price" else ""}>nejlevnější</option>'
                f'<option value="pricedesc">nejdražší</option><option value="sale">největší sleva</option></select></label></div>'
                '<h2 class="sr">Nabídka</h2>'      # cards are h3: keep the heading order h1 > h2 > h3 (Lighthouse a11y)
                f'<ul class="grid grid--list" id="plist" data-json="{json_url}" data-page="{cur}" data-per="{PER_PAGE}" data-order="{order}">{"".join(self.card(p, lazy=True if i > 3 else ("high" if i < 2 else False)) for i, p in enumerate(chunk))}</ul>'
                f'{pager_html(path, cur, pages, n, PER_PAGE) if path else ""}</div></div>')

    @staticmethod
    def quick_caps(items):
        ps = sorted(p["price"] for p in items)
        if not ps:
            return []
        steps = [500, 1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000]
        med = ps[len(ps) // 2]
        lo = next((s for s in steps if s >= ps[len(ps) // 5]), steps[0])
        hi = next((s for s in steps if s >= med), steps[-1])
        return sorted({lo, hi})

    def filters(self, items, facets):
        """Favi-like filter bar: one <form>, every group a <details> pill whose popover holds the inputs; "Všechny filtry" turns
        the same form into a drawer with all groups open (also the mobile view). app.js filters the category JSON."""
        def pill(key, label, inner):
            return (f'<details class="fb" data-g="{key}"><summary>{E(label)}<span class="fb__n"></span></summary><div class="fb__pop">'
                    f'<fieldset><legend>{E(label)}</legend>{inner}</fieldset><button class="btn fb__ok" type="button">Zobrazit</button></div></details>')

        def rng(name, unit, step, label, show=True):
            return (f'<div class="fprice">{f"<b>{E(label)}</b>" if show else ""}<input type="number" name="{name}min" min="0" step="{step}" placeholder="od" aria-label="{E(label)} od ({unit})">'
                    f'<span>–</span><input type="number" name="{name}max" min="0" step="{step}" placeholder="do" aria-label="{E(label)} do ({unit})"><span>{unit}</span></div>')

        def checks(name, vals):
            return '<div class="flinks">' + "".join(f'<label><input type="checkbox" name="{name}" value="{E(str(v))}"> {E(t)}<span class="count">{n}</span></label>' for v, t, n in vals) + "</div>"

        pills = []
        caps = self.quick_caps(items)
        quick = '<div class="fquick">' + "".join(f'<button type="button" data-pmax="{c}">do {kc(c)}</button>' for c in caps) + "</div>" if caps else ""
        pills.append(pill("price", "Cena", rng("p", "Kč", 100, "Cena", show=False) + quick))
        dims = ""
        if facets.get("width"):
            dims += ('<label class="fprice"><b>Obvod zápěstí</b><input id="fwrist" type="number" min="12" max="25" step="0.5" inputmode="decimal" placeholder="např. 17" aria-label="Obvod zápěstí v cm"><span>cm</span></label>'
                     '<p class="muted">Podle zápěstí nastavíme průměr pouzdra, který se na něm obvykle nosí. Nebo ho zadejte sami:</p>' + rng("w", "mm", 1, label="Průměr pouzdra"))
        if facets.get("sizes"):
            dims += '<p class="fsub">Velikost prstenu (obvod v mm)</p><div class="fchips">' + "".join(
                f'<label><input type="checkbox" name="size" value="{E(z)}"><span>{E(z)}</span></label>' for z, n in sorted(facets["sizes"], key=lambda x: int(x[0]))) + "</div>"
        if dims:
            pills.append(pill("dims", "Velikost", dims))
        cols = facets.get("colors")
        if cols:
            pills.append(pill("colors", "Barva", '<div class="fsw">' + "".join(
                f'<label title="{X.COLOR_NAME[c]}"><input type="checkbox" name="colors" value="{c}"><i style="--c:{SWATCH[c]}"></i><span>{X.COLOR_NAME[c]}</span><span class="count">{n}</span></label>'
                for c, n in cols) + "</div>"))
        for key, legend, names in (("feats", "Vlastnosti", X.FEATURE_NAME), ("mats", "Materiál", X.MATERIAL_NAME), ("styles", "Styl", X.STYLE_NAME)):
            vals = facets.get(key)
            if vals:
                pills.append(pill(key, legend, checks(key, [(v, names[v], n) for v, n in vals])))
        for key, vals in (facets.get("fx") or {}).items():
            pills.append(pill("fx-" + key, X.FACETS[key][0], checks("fx", [(f"{key}:{v}", X.FACET_VALUE[key][v], n) for v, n in vals])))
        seats = facets.get("seats")
        if seats:
            pills.append(pill("seats", "Počet míst", checks("seats", [(v, f"{v} a více" if v == 4 else f"{v} místa", n) for v, n in seats])))
        shops = facets.get("shop")
        if shops and len(shops) > 1:
            srch = '<input class="fsearch" type="search" placeholder="Hledat obchod" aria-label="Hledat obchod">' if len(shops) > 10 else ""
            pills.append(pill("shop", "Obchod", srch + checks("shop", [(sid, self.shop(sid)["name"], n) for sid, n in shops])))
        brands = facets.get("brand")
        if brands:
            srch = '<input class="fsearch" type="search" placeholder="Hledat značku" aria-label="Hledat značku">' if len(brands) > 10 else ""
            pills.append(pill("brand", "Značka", srch + checks("brand", [(i, b, n) for i, b, n in brands])))
        order = ["price", "brand", "feats", "styles", "mats", "fx", "dims", "colors", "seats", "shop"]      # what shoppers narrow by first (sidebar reads top to bottom)
        gkey = lambda h: order.index(re.search(r'data-g="([a-z]+)', h).group(1)) if re.search(r'data-g="([a-z]+)', h).group(1) in order else len(order)
        pills.sort(key=gkey)
        toggles = ('<label class="fbt"><input type="checkbox" name="sale" value="1"><span>Ve slevě</span></label>'
                   '<label class="fbt"><input type="checkbox" name="multi" value="1"><span>Ve více obchodech</span></label>')
        return ('<form class="filters" id="filters" aria-label="Filtry"><div class="fhead"><b>Všechny filtry</b><button class="fx" type="button" aria-label="Zavřít">✕</button></div>'
                '<div class="fbar" data-scroll><button class="fall" type="button"><svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><path d="M3 5h14M6 10h8M8 15h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>Všechny filtry</button>'
                + "".join(pills) + toggles + '</div><div class="ffoot"><button class="btn btn--g freset" type="button">Zrušit vše</button>'
                '<button class="btn fclose" type="button">Zobrazit <span class="fcount"></span></button></div></form><div class="fshade" hidden></div>')

    def band(self, h1, lead, icon=None, extra=""):
        art = f'<img class="band__ic" src="/img/ic/{icon}.webp" alt="" width="120" height="120">' if icon else ""
        return f'<section class="band"><div class="wrap"><div class="band__t"><!--crumbs--><h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div>{art}</div></section>'


def svg_history(hist, today):
    """Step chart of our own price observations (no JS)."""
    if not hist or len(hist) < 2:
        return ""
    pts = hist + [[today, hist[-1][1]]]
    x0, x1 = pts[0][0], max(pts[-1][0], pts[0][0] + 1)
    ys = [p[1] for p in pts]
    lo, hi = min(ys), max(ys)
    if hi == lo:
        hi = lo + 1
    W, H = 320, 90
    Xf = lambda d: round((d - x0) / (x1 - x0) * (W - 10) + 5, 1)
    Y = lambda v: round(H - 12 - (v - lo) / (hi - lo) * (H - 30), 1)
    d = f"M{Xf(pts[0][0])},{Y(pts[0][1])}"
    for a, b in zip(pts, pts[1:]):
        d += f" H{Xf(b[0])} V{Y(b[1])}"
    return (f'<svg class="hist" viewBox="0 0 {W} {H}" role="img" aria-label="Vývoj nejnižší ceny: od {kc(lo)} do {kc(hi)}">'
            f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<text x="5" y="{H - 1}" font-size="11">{kc(lo)}</text><text x="{W - 5}" y="12" font-size="11" text-anchor="end">{kc(hi)}</text></svg>')
