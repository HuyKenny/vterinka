"""Watches & jewellery tree, classifier and attributes for vterinka.cz.

Departments: Hodinky (by who wears them: pánské / dámské / dětské / unisex, kapesní), Šperky (by kind of piece) and
Doplňky (straps, jewellery boxes, watch boxes and winders). Category URLs are flat (/panske-hodinky/, /nausnice/).

Everything is matched on a FOLDED text (lower case, no diacritics), so the patterns below are written without háčky.
Smart watches and fitness bands are NOT part of the site (Kenny 19. 11. 2026: classic watches only): VETO_ABS throws
them out wherever the word stands in the title, and so are wall/alarm clocks, craft beads, key rings and costume props.
The interface (names and signatures) is the one catalog.py / build.py / landings.py of the vian template expect.
"""
import re
import unicodedata

I = re.I


def fold(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"[®™©]", "", s or "")).strip()


def slugify(s):
    s = fold(clean(s).replace("&", " a "))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ------------------------------------------------------------------ tree
# department slug: (name, h1 phrase, short blurb, icon)
ROOMS = {
    "hodinky": ("Hodinky", "Náramkové hodinky", "Pánské, dámské a dětské hodinky od Casia po Tissot", "hodinky"),
    "sperky": ("Šperky", "Šperky", "Prsteny, náušnice, náhrdelníky, náramky a přívěsky", "sperky"),
    "doplnky": ("Doplňky", "Doplňky k hodinkám a šperkům", "Řemínky, šperkovnice, boxy a natahovače hodinek", "sperkovnice"),
}

# category slug: (name, department, h1 phrase, icon)
CATS = {
    "panske-hodinky": ("Pánské hodinky", "hodinky", "Pánské hodinky", "panske-hodinky"),
    "damske-hodinky": ("Dámské hodinky", "hodinky", "Dámské hodinky", "damske-hodinky"),
    "detske-hodinky": ("Dětské hodinky", "hodinky", "Dětské hodinky", "detske-hodinky"),
    "unisex-hodinky": ("Unisex hodinky", "hodinky", "Unisex hodinky", "hodinky"),
    "kapesni-hodinky": ("Kapesní hodinky", "hodinky", "Kapesní hodinky", "kapesni-hodinky"),
    "prsteny": ("Prsteny", "sperky", "Prsteny", "prsten"),
    "snubni-prsteny": ("Snubní prsteny", "sperky", "Snubní prsteny", "snubni-prsteny"),
    "zasnubni-prsteny": ("Zásnubní prsteny", "sperky", "Zásnubní prsteny", "zasnubni-prsten"),
    "nausnice": ("Náušnice", "sperky", "Náušnice", "nausnice"),
    "nahrdelniky": ("Náhrdelníky", "sperky", "Náhrdelníky", "nahrdelnik"),
    "privesky": ("Přívěsky", "sperky", "Přívěsky na krk", "privesek"),
    "retizky": ("Řetízky", "sperky", "Řetízky na krk", "retizek"),
    "naramky": ("Náramky", "sperky", "Náramky", "naramek"),
    "koralky-na-naramky": ("Korálky na náramky", "sperky", "Korálky a přívěsky na náramky", "koralek"),
    "nakotniky": ("Nákotníky", "sperky", "Náramky a řetízky na nohu (nákotníky)", "nakotnik"),
    "broze": ("Brože", "sperky", "Brože a jehlice", "broz"),
    "sperkove-soupravy": ("Soupravy šperků", "sperky", "Soupravy a sady šperků", "souprava"),
    "piercing": ("Piercing", "sperky", "Piercing do nosu, ucha a pupíku", "piercing"),
    "manzetove-knoflicky": ("Manžetové knoflíčky", "sperky", "Manžetové knoflíčky a spony na kravatu", "manzetove-knoflicky"),
    "reminky": ("Řemínky na hodinky", "doplnky", "Řemínky a tahy na hodinky", "reminek"),
    "sperkovnice": ("Šperkovnice", "doplnky", "Šperkovnice a stojany na šperky", "sperkovnice"),
    "boxy-na-hodinky": ("Boxy na hodinky", "doplnky", "Boxy, pouzdra a natahovače hodinek", "box-na-hodinky"),
}

TREE = {**{k: (v[0], None, v[1], v[2], v[3]) for k, v in ROOMS.items()},
        **{k: (v[0], v[1], v[2], "", v[3]) for k, v in CATS.items()}}
TOP = list(ROOMS)
ICON = {k: v[4] for k, v in TREE.items()}
WATCH_CATS = {k for k, v in CATS.items() if v[1] == "hodinky"}
JEWEL_CATS = {k for k, v in CATS.items() if v[1] == "sperky"}

# cheaper than this = a strap, a battery or a toy in the wrong place
PRICE_FLOOR = {"panske-hodinky": 250, "damske-hodinky": 200, "unisex-hodinky": 200, "detske-hodinky": 120, "kapesni-hodinky": 150,
               "snubni-prsteny": 300, "zasnubni-prsteny": 400, "boxy-na-hodinky": 150, "reminky": 59}

# ------------------------------------------------------------------ veto
# anywhere in the title: not a classic watch / not jewellery, whatever comes first
VETO_ABS = re.compile(
    r"(\bchytr\w* (hodink|naramk|prsten)|\bsmart ?(watch|band|ring)|\bsmartwatch|\bsmart hodink|\bfitness|\bfitnes\b|\bfit naramek|\bsporttester|\bsport tester|"
    r"\bgps\b|\bsim kart\w*|\blokator|\bkrokomer|\btepov\w* frekv|\bmereni tepu|\bwear ?os\b|"
    r"\bgarmin\b|\bapple watch|\bamazfit|\bfitbit|\bsuunto|\bpolar (ignite|vantage|pacer|grit|unite)|\bcoros\b|\bwithings|\bhuawei|\bxiaomi|\bredmi\b|"
    r"\bgalaxy watch|\bmi band|\bhonor (band|watch)|\bniceboy|\bumax\b|\bcarneo|\bwatchy\b|\bforever (smart|kw|cw)|\bhammer watch|\bmyphone|\bvivoactive|\bforerunner|"
    r"\bbudik|\bbudicek|\bnastenn\w* hodin|\bstoln\w* hodin|\bkukack|\bmetronom|\bminutk|\bstopky\b|\bkuchynsk\w* hodin|\bhodiny\b|\bhodin s\b|"
    r"\bnahradn\w* (sklo|baterie|korunk)|\bbaterie (do|pro) hodin|\bknofl\w*ov\w* bateri|\bnaradi|\bpaska na hodinky|\botvirac\w* hodin|\bnastroj\w*|"
    r"\bnavlekan|\bna navlek|\bkomponent|\bzapinani (na|pro) sperk|\bkoralky (na|pro) (vyrob|navlek)|\bsada na vyrob|\bkreativn|\bfimo\b|\blanko na|\bkroucen\w* drat|"
    r"\bdo vlasu|\bcelenk|\bsponk|\bgumick|\bklicenk|\bna klice|\bprivesek na (kabelk|batoh|mobil|klic|tasku)|\bna mobil|\bobojek|\bpro psy|\bpro kocky|\bpro mazlick|"
    r"\bkostym|\bkarneval|\bhalloween|\bmaska\b|\bpro panenk|\bhrack|\bstavebnic|\blego\b|\bkniha\b|\bpuzzle|\bnalepk|\bplakat|\bobraz\b|\btapet|\bvanocn\w* ozdob|"
    r"\bparfem|\btoaletni voda|\bparfemovan|\bkosmetik|\bkrem\b|\btetovan|\bleseni|\bdeodorant|\bsprchov|\bmydl|\bsampon|"
    r"\bkabelk\w*(?! na sperk)|\bpenezenk|\bbatoh|\bslunecni bryle|\bbryle\b|\bopasek|\bpasek do kalhot|\bkravat(a|y)\b|\bmotyl(ek|ka) (pansk|k obleku)|"
    r"\btricko|\bmikina|\bsaty\b|\bpyzam|\bponozk|\bboty\b|\bcepice|\bsala\b|\bsatek|\brukavic)", I)
# a non-jewellery noun that comes BEFORE the jewellery word ("Taška s přívěskem", "Hrnek se srdíčkem")
VETO_TITLE = re.compile(r"\b(taska|hrnek|polstar|deka|svicka|svicen|vaza|ramecek|kosik|krabice od|podtacek|zapisnik|diar|propisk|privesek na klice)\w*", I)
VETO_PATH = re.compile(r"(chytre hodinky|smart ?watch|fitness|sporttester|hodiny a budiky|nastenne hodiny|budiky|dum a zahrada|elektronika|"
                       r"kabelky|penezenky|bryle|parfem|kosmetika|obuv|hracky|leciv|mineraly a krystaly|kameny od a do z|feng shui|vonne|"
                       r"dekorace domova|obrazy|misky)", I)

R = lambda s: re.compile(s, I)

# watches: the category is decided by who wears them (watch_cat); these rules only say "it is a watch"
WATCH_RX = R(r"\bhodink\w*|\bhodinek\b|\bwatch(es)?\b|\bchronograf\w*|\bnaramkov\w* hodin")
POCKET_RX = R(r"\bkapesn\w* hodin|\bpocket watch|\bhodink\w* na retiz|\bcibul\w* hodin")

# (category, pattern on the folded title). The rule whose match starts EARLIEST wins (Czech titles name the thing first);
# on the same start the longer match ("náramek na hodinky" beats "náramek").
TITLE_RULES = [
    ("reminky", R(r"\b(reminek|reminky|remen\w*|pasek|pasky|naramek|tah|nato pasek|nato reminek)\w* (na|k|pro|do) (naramkov\w* )?hodin\w*|\bnato reminek|\bnahradn\w* (reminek|pasek)|\b(reminek|reminky) (hirsch|condor|morellato|bros|nato)\b")),
    ("boxy-na-hodinky", R(r"\bnatahovac\w* (na |pro )?hodin\w*|\bwatch winder|\brotomat|\b(box|boxy|krabic\w*|kazet\w*|pouzdr\w*|vitrin\w*|stojan\w*|organizer\w*) (na|pro) (\w+ )?hodink\w*")),
    ("sperkovnice", R(r"\bsperkovnic\w*|\b(krabic\w*|krabick\w*|box\w*|kazet\w*|stojan\w*|stojanek|organizer\w*|pouzdr\w*|misk\w*|stromek|vesak\w*|panna) (na|pro) (\w+ )?(sperk|nausnic|naramk|retiz|prsten|privesk|nahrdelnik)\w*")),
    ("kapesni-hodinky", POCKET_RX),
    ("__watch__", WATCH_RX),
    ("snubni-prsteny", R(r"\bsnubn\w*|\bsnubak\w*|\bsnubni\b")),
    ("zasnubni-prsteny", R(r"\bzasnubn\w*")),
    ("sperkove-soupravy", R(r"\b(souprav\w*|sad\w*|set\w*|komplet\w*) (\w+ ){0,2}(sperk|bizuter)\w*|\bsperkov\w* (sada|souprava|set)|\bsouprava (nausnic|nahrdelnik|naramk)\w*|"
                            r"\b(nausnice|nahrdelnik|naramek|prsten|retizek|privesek)\w* (a|\+|s) (nausnic|nahrdelnik|naramk|prsten|retiz)\w*")),
    ("koralky-na-naramky", R(r"\bkoralek\b|\bkoralky\b(?! na krk)|\bkoral\w* (na|pro|k) naram\w*|\bcharms?\b|\bprivesk\w* (na|pro|k) naram\w*|\bklip\w* (na|pro) naram\w*|\bdistancni koral")),
    ("piercing", R(r"\bpiercing\w*|\bpiersing\w*|\bpirsing\w*|\b(do|na) (nosu|pupiku|obocí|oboci|jazyk|bradavk)\b|\btragus|\bhelix\b|\bseptum|\blabret|\bplug\w*\b|\btunel\w* do (ucha|usi)|\bexpander\w*|\bbanan(ek)? do")),
    ("nausnice", R(r"\bnausnic\w*|\bnausnick\w*|\bzausnic\w*|\bklips\w*|\bpecky\b|\bkruhy do usi|\bnausnicky")),
    ("nakotniky", R(r"\bnakotnik\w*|\b(retiz\w*|naram\w*) na (kotnik|nohu)")),
    ("nahrdelniky", R(r"\bnahrdelnik\w*|\bnahrdelni\b|\bkolier\w*|\bchoker\w*|\bperlov\w* (snur|nahrd)")),
    ("privesky", R(r"\bprivesek\b|\bprivesk\w*|\bprivesky\b|\bmedailon\w*|\bmedailonek|\bamulet\w*|\btalisman\w*|\bpendant\b")),
    ("retizky", R(r"\bretiz(ek|ky|ku|kem|ku|k)\b|\bretez\w* (na krk|stribrn|zlat|pansk|z chirurg)|\bkrcni retez|\bpancr\w* retez|\bpanzer\w* retez")),
    ("naramky", R(r"\bnaramek\b|\bnaramk(?!ov\w* hodin)\w*|\bnaramen\w*|\bnaramky\b")),
    ("broze", R(r"\bbroz\b|\bbroze\b|\bbrozi\b|\bbrozk\w*|\bjehlic\w*|\bspendlik\w* (do|na) klop\w*|\bodznak\w*")),
    ("manzetove-knoflicky", R(r"\bmanzetov\w*|\b(spon\w*|klip\w*|jehlic\w*) (na|do|ke) kravat\w*|\bkravatov\w* spon\w*")),
    ("prsteny", R(r"\bprsten\w*|\bprstynk\w*|\bpecetn\w*|\bprstinek")),
]

UNAMBIGUOUS = {"reminky", "boxy-na-hodinky", "sperkovnice", "kapesni-hodinky", "snubni-prsteny", "zasnubni-prsteny", "sperkove-soupravy",
               "koralky-na-naramky", "piercing", "nausnice", "nakotniky", "nahrdelniky", "broze", "manzetove-knoflicky", "prsteny"}
VETOED = "__veto__"

# ------------------------------------------------------------------ who wears the watch
G_KIDS = R(r"\bdetsk\w*|\bpro deti\b|\bjunior\w*|\bkids?\b|\bchlapeck\w*|\bdivci\w*|\bpro kluk|\bpro holk|\bpro chlapce|\bpro divk|\bteen\b")
G_WOMEN = R(r"\bdamsk\w*|\blady\b|\bladies\b|\bwomen'?s?\b|\bwoman\b|\bpro zeny\b|\bpro zenu\b|\bfemme\b|\bdonna\b")
G_MEN = R(r"\bpansk\w*|\bmen'?s\b|\bmens\b|\bgents?\b|\bpro muze\b|\bpro muzy\b|\bhomme\b|\buomo\b")
G_UNI = R(r"\bunisex\b")


def gender_of(text):
    """'men' / 'women' / 'kids' / 'unisex' / '' from a folded text; both men and women = unisex."""
    if not text:
        return ""
    if G_UNI.search(text):
        return "unisex"
    k, w, m = G_KIDS.search(text), G_WOMEN.search(text), G_MEN.search(text)
    if k and not (m and m.start() < k.start()) and not (w and w.start() < k.start()):
        return "kids"
    if w and m:
        return "unisex"
    return "women" if w else "men" if m else ""


def gender_of_path(path):
    segs = [s.strip() for s in re.split(r"[>|/]", path or "") if s.strip()]
    for s in segs:
        if s in ("on", "muzi", "muz", "panske", "pani", "men") or s.startswith(("pansk", "pro muze")):
            return "men"
        if s in ("ona", "zeny", "zena", "damske", "women") or s.startswith(("damsk", "pro zeny")):
            return "women"
        if s.startswith(("detsk", "deti", "chlapec", "divk", "kids")):
            return "kids"
        if s == "unisex":
            return "unisex"
    return ""


WATCH_BY_GENDER = {"men": "panske-hodinky", "women": "damske-hodinky", "kids": "detske-hodinky", "unisex": "unisex-hodinky", "": "unisex-hodinky"}


# model-code families that say who a watch is for (the feed often does not: Vivantis "Casio Analogové hodinky LTP-1302PD-7A")
CODE_MEN = R(r"\b(casio|g ?shock|edifice|pro trek)\b.*\b(mtp|mq|aeq?|efr|efv|efb|efs|ecb|era|ga|gw|gm|gst|gbd|gd|dw|prw|prg|mrg|mtg|ef)[ -]?\d|\bprim\b.*\bw01[a-z]?\.|\bw01[pc]\.\d")
CODE_WOMEN = R(r"\b(casio|baby ?g|sheen)\b.*\b(ltp|lq|la|ltf|lte|lrw|she|msg|bga|lw|bgd)[ -]?\d|\bprim\b.*\bw02[a-z]?\.|\bw02[pc]\.\d")
CODE_KIDS = R(r"\bprim\b.*\bw05[a-z]?\.|\bw05[pc]\.\d")


def watch_cat(rec, t, p):
    """(category, strong): the title says who it is for > the shop's path (Answear 'On > Doplňky > Hodinky', Allegro
    '… Hodinky > Pánské') > the model-code family (Casio MTP/LTP, Prim W01/W02) > the description start. Unknown = unisex."""
    g = gender_of(t)
    if g:
        return WATCH_BY_GENDER[g], True
    prm = rec.get("prm") or {}
    g = gender_of(fold(" ".join(prm.get(k, "") for k in ("určení", "pro koho", "pohlaví"))))       # Hodinky.cz & co: "Určení: Pro muže" is the shop's own word
    if g:
        return WATCH_BY_GENDER[g], True
    tm = t + " " + fold(rec.get("mpn") or "")
    g = (gender_of_path(p) or ("kids" if CODE_KIDS.search(tm) else "women" if CODE_WOMEN.search(tm) else "men" if CODE_MEN.search(tm) else "")
         or gender_of(fold(rec.get("d") or "")[:400]))
    return WATCH_BY_GENDER[g], False


def title_class(rec):
    """What the TITLE says: (category, strong) or (VETOED, True) or (None, False)."""
    t = fold(clean(rec.get("t"))).replace("-", " ")
    p = fold(rec.get("cat") or "")
    if VETO_PATH.search(p) or VETO_ABS.search(t):
        return VETOED, True
    best = None
    for i, (slug, rx) in enumerate(TITLE_RULES):
        m = rx.search(t)
        if m:
            key = (m.start(), -(m.end() - m.start()), i)
            if best is None or key < best[0]:
                best = (key, slug, m.group(0))
    v = VETO_TITLE.search(t)
    if v and (best is None or v.start() < best[0][0]):
        return VETOED, True
    if not best:
        return None, False
    slug = best[1]
    if slug == "__watch__":
        return watch_cat(rec, t, p)
    return slug, slug in UNAMBIGUOUS or " " in best[2].strip()


PATH_RULES = [
    ("reminky", R(r"reminky|pasky na hodinky|reminek")),
    ("sperkovnice", R(r"sperkovnic|krabicky na sperky|stojany na sperky")),
    ("boxy-na-hodinky", R(r"natahovac|boxy na hodinky")),
    ("snubni-prsteny", R(r"snubni prsten")), ("zasnubni-prsteny", R(r"zasnubni prsten")), ("manzetove-knoflicky", R(r"manzetove knofl")),
    ("nausnice", R(r"nausnic")), ("prsteny", R(r"prsten")), ("nahrdelniky", R(r"nahrdelni")), ("naramky", R(r"naramk")),
    ("privesky", R(r"privesk")), ("retizky", R(r"retiz")), ("broze", R(r"broz")), ("piercing", R(r"piercing")),
    ("sperkove-soupravy", R(r"soupravy|sady sperku")), ("nakotniky", R(r"nakotnik")),
]


def path_class(rec):
    p = fold(rec.get("cat") or "")
    if re.match(r"hodinky\b", p) and not (VETO_PATH.search(p) or VETO_ABS.search(fold(clean(rec.get("t")))) or re.match(r"hodinky\W+(prislusenstvi|hodiny|budiky)", p)):
        return watch_cat(rec, fold(clean(rec.get("t"))).replace("-", " "), p)[0]       # Hodinky.cz Google category "Hodinky -> Klasické hodinky": titles are brand + model, no word "hodinky"
    for slug, rx in PATH_RULES:
        if rx.search(p):
            return slug
    return None


def classify(rec, kids=False):
    slug, strong = title_class(rec)
    if slug == VETOED:
        return None
    return slug or path_class(rec)


def decide(rec, title, clean_path_cat, kids=False):
    """Final category from the title verdict and the shop's own category when that category is CLEAN (nearly all of its
    products are one kind of thing). A clean shop category beats a lone generic word; a specific title wins. For watches
    the gender from the title beats the shop path, the path beats the description."""
    slug, strong = title
    if slug == VETOED:
        return None, "veto"
    if clean_path_cat:
        if slug and strong and slug != clean_path_cat:
            return slug, "title>path"
        if slug in WATCH_CATS and clean_path_cat in WATCH_CATS and slug != clean_path_cat:
            return slug, "title"        # the watch rule already weighed path and title
        return clean_path_cat, "path"
    if slug:
        return slug, "title"
    fb = path_class(rec)
    return (fb, "path-rule") if fb else (None, "none")


# ------------------------------------------------------------------ attributes
COLORS = [  # slug, label, patterns (dial, case or piece colour)
    ("zlata", "zlatá", r"\bzlat[aeyouý]\w*|\bgold\b|\bpozlac\w*|\bzlatav"),
    ("ruzove-zlata", "růžově zlatá", r"\bruzov\w* zlat\w*|\brose ?gold|\brosegold|\brosé"),
    ("stribrna", "stříbrná", r"\bstribrn\w*|\bsilver\b|\bocelov\w* barv"),
    ("cerna", "černá", r"\bcern[aeyáéý]\w*|\bciern\w*|\bblack\b"),
    ("bila", "bílá", r"\bbil[aáeéyý]\w*|\bwhite\b|\bperletov\w*"),
    ("modra", "modrá", r"\bmodr\w*|\bnavy\b|\bblue\b|\btyrkys\w*"),
    ("zelena", "zelená", r"\bzelen\w*|\bgreen\b|\bolivov\w*|\bsmaragdov"),
    ("cervena", "červená", r"\bcerven\w*|\bbordo\w*|\bred\b|\bvinov"),
    ("ruzova", "růžová", r"\bruzov\w*(?! zlat)|\bpink\b"),
    ("hneda", "hnědá", r"\bhned[aeyáéý]\w*|\bbrown\b|\bkoniak"),
    ("seda", "šedá", r"\bsed[aeyáéý]\b|\bgrey\b|\bgray\b|\bgrafit\w*|\bgunmetal|\bantracit\w*"),
]
COLORS_RX = [(s, l, re.compile(r)) for s, l, r in COLORS]
COLOR_NAME = {s: l for s, l, _ in COLORS}

MATERIALS = [  # metal of the piece / case, strap material
    ("stribro", "stříbro", r"\bstribr(o|a|em|ny|na|ne|neho)\b|\bryzi stribr|\bag ?925\b|\b925\b|\bsterling\w*|\bstribrn\w* (prsten|nausnic|naramek|retiz|privesek|nahrdelnik)"),
    ("zlato", "zlato", r"(?<!po)\bzlat(o|a|em)\b|\b(14|18|9) ?k(t|ar\w*)?\b|\b585\b|\b750\b|\bzlat\w* (prsten|nausnic|naramek|retiz|privesek|nahrdelnik|snubn)"),
    ("bile-zlato", "bílé zlato", r"\bbil\w* zlat\w*|\bwhite gold"),
    ("ruzove-zlato", "růžové zlato", r"\bruzov\w* zlat\w*|\brose ?gold|\brosegold"),
    ("pozlacene", "pozlacené", r"\bpozlac\w*|\bgold ?plated|\bvermeil|\bpokryt\w* \w* ?zlat\w*"),
    ("chirurgicka-ocel", "chirurgická ocel", r"\bchirurg\w* ocel\w*|\b316 ?l\b"),
    ("ocel", "ocel", r"\bocel(?!ov\w* barv)\w*|\bnerez\w*|\bstainless"),
    ("titan", "titan", r"\btitan\w*"),
    ("wolfram", "wolfram", r"\bwolfram\w*|\btungsten"),
    ("keramika", "keramika", r"\bkeramick\w*|\bkeramik\w*|\bceramic"),
    ("kuze", "kůže", r"(?<!eko)\bkozen\w*|\bkuze\b|\bkuzi\b|\bleather"),
    ("drevo", "dřevo", r"\bdreven\w*|\bdrevo\b|\bdreva\b|\bwood\w*"),
    ("silikon", "silikon", r"\bsilikon\w*|\bpryz\w*|\bkaucuk\w*|\bresin\b|\bpryskyric"),
    ("textil", "textil", r"\bnato\b|\btextiln\w*|\bnylon\w*|\bplatenn\w*"),
    ("milansky-tah", "milánský tah", r"\bmilan\w* tah\w*|\bmilanese|\bmesh\b|\bmilan\w* (remin|pas|naramk)"),
]
MATERIALS_RX = [(s, l, re.compile(r)) for s, l, r in MATERIALS]
MATERIAL_NAME = {s: l for s, l, _ in MATERIALS}

STYLES = [
    ("sportovni", "sportovní", r"\bsport\w*"),
    ("elegantni", "elegantní", r"\belegant\w*|\bklasick\w*|\bdress\b|\bspolecensk\w*"),
    ("luxusni", "luxusní", r"\bluxus\w*|\bluxury\b"),
    ("retro", "retro", r"\bretro\b|\bvintage\b"),
    ("minimalisticky", "minimalistický", r"\bminimal\w*|\bultra ?tenk\w*|\bslim\b"),
    ("boho", "boho", r"\bboho\b|\betno\b|\bethno"),
]
STYLES_RX = [(s, l, re.compile(r)) for s, l, r in STYLES]
STYLE_NAME = {s: l for s, l, _ in STYLES}

# features: watch movement and functions, stones, motifs, earring types, who jewellery is for
FEATURES = [
    ("automaticke", "automatický strojek", r"\bautomat(ic|ick|ik)\w*|\bpowermatic|\bself.?winding|\bsamonatah\w*"),
    ("mechanicke", "ruční natahování", r"\bmechanick\w*|\brucni\w* natah\w*|\bhand.?wound|\bhand.?wind"),
    ("solarni", "solární", r"\bsolar\w*|\beco.?drive"),
    ("rizene-radiem", "řízené rádiem", r"\brizen\w* radi\w*|\bradio.?control\w*|\bwave ?ceptor|\bmulti band|\bdcf ?77"),
    ("chronograf", "chronograf", r"\bchrono\w*"),
    ("digitalni", "digitální", r"\bdigital\w*|\bdigi\b"),
    ("potapecske", "potápěčské", r"\bpotapec\w*|\bdiver'?s?\b|\bdivers\b|\b(20|30) ?atm|\b(200|300) ?m\b"),
    ("pilotni", "pilotní", r"\bpilot\w*|\baviat\w*|\bletec\w*|\bflieger"),
    ("vojenske", "vojenské", r"\bvojensk\w*|\bmilitary|\barmy\b|\bfield\b"),
    ("skeleton", "skeleton", r"\bskelet\w*|\bopen ?heart|\bprosvetlen\w* ciferni"),
    ("s-perlou", "s perlou", r"\bperl[aeyiou]\w*|\bperlov\w*|\bpearl"),
    ("s-diamantem", "s diamantem", r"\bdiamant\w*|\bbrilian\w*|\bdiamond"),
    ("se-zirkony", "se zirkony", r"\bzirkon\w*|\bcubic zirconia|\bcz kamen"),
    ("s-krystaly", "s krystaly", r"\bkrystal\w*|\bswarovski"),
    ("s-kamenem", "s polodrahokamem", r"\bpolodrahokam\w*|\bdrahokam\w*|\bametyst\w*|\bgranat\w*|\btopaz\w*|\bsafir(?!ov\w* skl)\w*|\bsmaragd(?!ov)\w*|\brubin\w*|\btyrkys(?!ov)\w*|\bonyx\w*|\bmesicn\w* kam\w*|\bopal\w*|\bachat\w*|\bjaspis\w*|\bmalachit\w*|\bvltavin\w*|\bjantar\w*|\bgranat\w*|\blabradorit\w*|\bkrisťal|\bkristal\w*|\bkrystal\w* (kremen|ruzen)"),
    ("srdce", "se srdcem", r"\bsrdc\w*|\bsrdick\w*|\bheart\b"),
    ("kriz", "s křížkem", r"\bkriz\w*|\bkrizek\b|\bcross\b"),
    ("strom-zivota", "se stromem života", r"\bstrom\w* zivota|\btree of life"),
    ("nekonecno", "s nekonečnem", r"\bnekonecn\w*|\binfinity"),
    ("ctyrlistek", "se čtyřlístkem", r"\bctyrlist\w*|\bjetel\w*"),
    ("andel", "s andělem", r"\bandel\w*|\bandil\w*|\bkridl\w*"),
    ("pismeno", "s písmenem", r"\bpismen\w*|\binicial\w*|\bsvym jmen\w*|\bjmenem\b"),
    ("znameni", "se znamením zvěrokruhu", r"\bznameni\b|\bzverokruh\w*|\bhoroskop\w*|\b(beran|blizenci|strelec|kozoroh|vodnar)\b"),
    ("kruhove", "kruhové", r"\bkruh\w*|\bkruhov\w*|\bhoop\w*|\bkrouzk\w*"),
    ("pecky", "pecky", r"\bpeck\w*|\bpuzet\w*|\bstud\b"),
    ("visaci", "visací", r"\bvisac\w*|\bdlouh\w* nausn|\bdrop\b"),
    ("klipsy", "klipsy", r"\bklips\w*|\bbez propichnut"),
    ("pro-muze", "pro muže", r"\bpansk\w*|\bmen'?s?\b|\bpro muze\b|\bgents?\b"),
    ("pro-zeny", "pro ženy", r"\bdamsk\w*|\bwomen'?s?\b|\bpro zeny\b|\blady\b|\bladies\b"),
    ("pro-deti", "pro děti", r"\bdetsk\w*|\bpro deti\b|\bdivci\w*|\bchlapeck\w*|\bkids?\b|\bjunior\b"),
]
FEATURES_RX = [(s, l, re.compile(r)) for s, l, r in FEATURES]
FEATURE_NAME = {s: l for s, l, _ in FEATURES}
WATCH_FEATS = {"automaticke", "mechanicke", "solarni", "rizene-radiem", "chronograf", "digitalni", "potapecske", "pilotni", "vojenske", "skeleton"}
GENDER_FEATS = {"pro-muze", "pro-zeny", "pro-deti"}
EARRING_FEATS = {"kruhove", "pecky", "visaci", "klipsy"}


def attrs(title, color_field, desc, path="", cat=None):
    """Colours, materials, styles and features from what the shop says (title + colour field + description start; the
    shop path adds who jewellery is for: Answear 'On > …')."""
    t = fold(clean(title))
    c = fold(color_field or "")
    d = fold((desc or "")[:1200])
    p = fold(path or "")
    colors = [s for s, _, rx in COLORS_RX if rx.search(c) or rx.search(t)]
    if "ruzove-zlata" in colors and "ruzova" in colors:
        colors.remove("ruzova")
    mats = [s for s, _, rx in MATERIALS_RX if rx.search(t) or rx.search(d)]
    if "pozlacene" in mats and "zlato" in mats:
        mats.remove("zlato")
    if "chirurgicka-ocel" in mats and "ocel" in mats:
        mats.remove("ocel")
    if ("bile-zlato" in mats or "ruzove-zlato" in mats) and "zlato" not in mats:
        mats.append("zlato")
    if cat in WATCH_CATS and not re.search(r"\b(585|750|14 ?k|18 ?k|karat\w*|ryzi)\b", t + " " + d):
        mats = [m for m in mats if m not in ("zlato", "ruzove-zlato", "bile-zlato")]    # "rose gold" on a watch is a colour, not gold
    styles = [s for s, _, rx in STYLES_RX if rx.search(t) or rx.search(d[:300])]
    feats = [s for s, _, rx in FEATURES_RX if rx.search(t) or (s not in GENDER_FEATS and s not in EARRING_FEATS and rx.search(d[:300]))]
    if cat in WATCH_CATS or cat is None and WATCH_RX.search(t):
        feats = [f for f in feats if f in WATCH_FEATS]
    else:
        feats = [f for f in feats if f not in WATCH_FEATS]
        g = gender_of_path(p)
        if g == "men" and "pro-muze" not in feats:
            feats.append("pro-muze")
        elif g == "women" and "pro-zeny" not in feats:
            feats.append("pro-zeny")
        if cat and cat != "nausnice":
            feats = [f for f in feats if f not in EARRING_FEATS]
    return colors[:3], mats[:4], styles[:2], feats


# ------------------------------------------------------------------ sizes: case diameter (mm) and ring size (EU)
NUMMM = r"(\d{2}(?:[,.]\d{1,2})?)\s*mm"
# the CASE, labelled: "průměr pouzdra 40 mm", "pouzdro: 42 mm", "obálka: šířka 42 mm", "velikost pouzdra 38 mm", "case 41 mm", "40 mm pouzdro"
RX_CASE = [re.compile(r"(?:prumer|velikost|sirka|diameter|size)\s+(?:pouzdr\w*|obalk\w*|case|hodinek)\s*[:\-]?\s*(?:cca\s*)?" + NUMMM, I),
           re.compile(r"(?:pouzdr\w*|obalk\w*|case)\s*[:\-]\s*(?:sirka|prumer|velikost)?\s*[:\-]?\s*(?:cca\s*)?" + NUMMM, I),
           re.compile(NUMMM + r"\s*(?:pouzdr\w*|case\b)", I)]
# a bare "40 mm" in the TITLE is the case (Allegro "Orient Mako RA-AC0Q01B10B 39,90 mm 20ATM"), unless a strap / lug / dial / thickness word stands right before it
RX_MM = re.compile(r"(?<![\d,.])" + NUMMM + r"\b", I)
NOT_CASE = re.compile(r"(remin\w*|remen\w*|pas\w*|tah\w*|trn\w*|ciferni\w*|kotouc\w*|tloust\w*|vysk\w*|delk\w*|sirk\w* (remin|pas|tah)\w*|skl\w*|lug|strap|band)\W{0,4}(\w+\W{0,3}){0,2}$", I)
RX_RING = [re.compile(r"\beu:?\s*(\d{2})(?:\s*[-–]\s*\d{2})?\)", I), re.compile(r"\bobvod\w*:?\s*(\d{2})\s*mm", I),
           re.compile(r"\bvelikost\w*:?\s*(\d{2})\b", I), re.compile(r"\b(4[4-9]|5\d|6[0-8])\s*mm\b", I)]


def num(s):
    return float(s.replace(",", "."))


def dims(title, desc, cat):
    """Watches: {'w': case diameter in mm} (title first, then a labelled value in the description). Rings: {'size': EU
    ring size = inner circumference in mm}. Only plausible values are kept."""
    t = fold(title or "")
    d = fold((desc or "")[:1500])
    out = {}
    if cat in WATCH_CATS:
        v = None
        for src in (t, d):
            for rx in RX_CASE:
                m = rx.search(src)
                if m:
                    v = num(m.group(1))
                    break
            if v:
                break
        if v is None:
            for m in RX_MM.finditer(t):
                if not NOT_CASE.search(t[max(0, m.start() - 30):m.start()]):
                    v = num(m.group(1))
                    break
        if v and 24 <= v <= 55:
            out["w"] = v
    elif cat in ("prsteny", "snubni-prsteny", "zasnubni-prsteny"):
        for rx in RX_RING:
            m = rx.search(t)
            if m:
                v = int(m.group(1))
                if 44 <= v <= 72:
                    out["size"] = str(v)
                    break
    return out


def cz(v):
    return f"{v:g}".replace(".", ",")


def size_label(dm):
    if not dm:
        return ""
    if dm.get("size"):
        return f"velikost {dm['size']}"
    if dm.get("w"):
        return f"⌀ {cz(dm['w'])} mm"
    return ""


# "Elenys prsten Jemné city Velikost: 8 (EU: 57-58)" -> name + variant parameters
RX_PARAMS = re.compile(r"\s+(?=(?:[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)(?: [a-záčďéěíňóřšťúůýž]+){0,2}: )")


def split_variant(title):
    title = clean(title)
    m = RX_PARAMS.search(title)
    if m and m.start() > 8:
        return title[:m.start()].rstrip(" ,-–"), title[m.end():]
    return title, ""


# ------------------------------------------------------------------ brands
BRAND_ALIAS = {"casio": "Casio", "seiko": "Seiko", "citizen": "Citizen", "orient": "Orient", "tissot": "Tissot", "prim": "Prim", "tous": "Tous",
               "boss": "BOSS", "hugo boss": "BOSS", "maserati": "Maserati", "elenys": "Elenys", "royal fashion": "Royal Fashion", "guess": "Guess",
               "fossil": "Fossil", "festina": "Festina", "lorus": "Lorus", "bentime": "Bentime", "jvd": "JVD", "swatch": "Swatch",
               "daniel wellington": "Daniel Wellington", "michael kors": "Michael Kors", "tommy hilfiger": "Tommy Hilfiger", "lacoste": "Lacoste",
               "calvin klein": "Calvin Klein", "pandora": "Pandora", "swarovski": "Swarovski", "morellato": "Morellato", "skagen": "Skagen",
               "emporio armani": "Emporio Armani", "armani exchange": "Armani Exchange", "q&q": "Q&Q", "timex": "Timex", "certina": "Certina",
               "hamilton": "Hamilton", "doxa": "Doxa", "bulova": "Bulova", "invicta": "Invicta", "versace": "Versace", "diesel": "Diesel"}
BAD_BRANDS = {"", "none", "null", "neuvedeno", "ostatni", "nezarazeno", "bez znacky", "noname", "no name", "-", "n/a", "unknown", "generic",
              "vyrobce", "nezname", "vivantis", "answear", "allegro", "zesmakiem", "mode", "demix", "imago", "nefertitis eshop", "sperky"}


def brand_of(rec):
    b = clean(rec.get("b"))
    k = fold(b)
    if k in BAD_BRANDS or len(k) < 2:
        return ""
    if k in BRAND_ALIAS:
        return BRAND_ALIAS[k]
    if b.isupper() and len(b) > 4:
        b = b.title()
    return b[:40]


# words that only tell variants of one model apart (size, colour, "velikost"); stripped to build the model key
VARIANT_WORDS = re.compile(
    r"\b(\d+([,.]\d+)?\s*(mm|cm)|velikost\w*|vel|eu|obvod|delka|\d{1,2}|"
    + "|".join(r[2].replace(r"\b", "") for r in COLORS) + r"|svetl\w*|tmav\w*|matn\w*|leskl\w*|varianta|barva|provedeni|odstin|rozmer)\b", I)


def model_key(name):
    t = fold(clean(name))
    t = re.sub(r"\(.*?\)|\[.*?\]", " ", t)
    t = VARIANT_WORDS.sub(" ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return t


# ------------------------------------------------------------------ shapes / seats: not used on this site (interface of the template)
SHAPE_NAME = {}


def shapes_of(text, cat):
    return []


def seats_of(text, cat):
    return 0


# ------------------------------------------------------------------ category facets (filters): facet -> (label, categories, [(value, label, pattern)])
_COLOR_VALS = [(slug, label, rx) for slug, label, rx in COLORS]      # the same colour words as the colour filter, applied to the dial / strap colour parameter
FACETS = {
    "mov": ("Typ strojku", WATCH_CATS, [
        ("quartz", "quartz (baterie)", r"\bquartz|\bkvarc\w*|\bbaterie\b|\bbateri\w*"),
        ("automat", "automatický", r"\bautomat(ic|ick|ik)\w*|\bpowermatic|\bself.?winding|\bsamonatah\w*|\bautomat\b"),
        ("mechanicky", "ruční natahování", r"\bmechanick\w*|\brucni\w* natah\w*|\bhand.?wound|\bhand.?wind|\bnatahovac\w*"),
        ("solarni", "solární", r"\bsolar\w*|\beco.?drive"),
        ("kinetic", "kinetic", r"\bkinetic"),
        ("radiem", "řízené rádiem", r"\brizen\w* radi\w*|\bradio.?control\w*|\bwave ?ceptor|\bmulti band|\bdcf ?77")]),
    "func": ("Funkce", WATCH_CATS, [
        ("datum", "datum", r"\bdat(um|em|a|u)\b|\bdatum\w*|\bdate\b|\bkalend\w*"),
        ("den", "den v týdnu", r"\bden v tydnu|\bday.?date|\bdny v tydnu"),
        ("mesic", "fáze měsíce", r"\bfaz\w* mesic\w*|\bmoon ?phase"),
        ("budik", "budík", r"\bbudik\w*|\balarm\w*"),
        ("stopky", "stopky / chronograf", r"\bstopk\w*|\bchrono\w*"),
        ("gmt", "druhé časové pásmo / GMT", r"\bgmt\b|\bdruh\w* casov\w*|\bdual ?time|\bworld ?time|\bsvetov\w* cas"),
        ("tachymetr", "tachymetr", r"\btachymetr\w*"),
        ("podsviceni", "podsvícení / svítící ručičky", r"\bpodsvic\w*|\bsvitici\w*|\bluminov\w*|\bsuperluminova|\bsvetel\w* ruck\w*|\billuminator|\bluminiscen\w*")]),
    "casemat": ("Materiál pouzdra", WATCH_CATS, [
        ("ocel", "ocel", r"\bocel\w*|\bnerez\w*|\bsteel"),
        ("titan", "titan", r"\btitan\w*"),
        ("keramika", "keramika", r"\bkeramik\w*|\bceramic"),
        ("plast", "plast / karbon / pryskyřice", r"\bplast\w*|\bkarbon\w*|\bcarbon|\bpryskyric\w*|\bresin|\bpryz\w*"),
        ("zlato", "zlato / pozlacené", r"\bzlat\w*|\bpozlac\w*|\bgold"),
        ("bronz", "bronz / mosaz", r"\bbronz\w*|\bmosaz\w*"),
        ("hlinik", "hliník", r"\bhlinik\w*|\baluminium")]),
    "strap": ("Řemínek", WATCH_CATS, [
        ("kuze", "kožený", r"\bkozen\w*|\bleather|\bkuze\b"),
        ("kov", "kovový tah", r"\bocelov\w* (tah|naram|remin|pas)|\bkovov\w* (tah|naram|remin|pas)|\bsegmentov\w*|\btah\b|\bbracelet\b|^(obecny )?kov\b|^ocel\w*|^titan\w*"),
        ("milansky", "milánský tah", r"\bmilan\w*|\bmesh\b"),
        ("silikon", "silikonový / pryžový", r"\bsilikon\w*|\bpryz\w*|\bkaucuk\w*|\bresin\b|\bpryskyric"),
        ("textil", "textilní / NATO", r"\bnato\b|\btextil\w*|\bnylon\w*|\bplatenn\w*")]),
    "shape": ("Tvar pouzdra", WATCH_CATS, [
        ("kulate", "kulaté", r"\bkulat\w*|\bround\b"),
        ("hranate", "hranaté / čtvercové", r"\bhranat\w*|\bctvercov\w*|\bsquare\b"),
        ("obdelnikove", "obdélníkové", r"\bobdelnik\w*|\brectang\w*"),
        ("ovalne", "oválné", r"\boval\w*"),
        ("tonneau", "soudkovité (tonneau)", r"\btonneau|\bsoudkovit\w*|\bsudovit\w*")]),
    "dialcol": ("Barva ciferníku", WATCH_CATS, _COLOR_VALS),
    "strapcol": ("Barva řemínku", WATCH_CATS, _COLOR_VALS),
    "glass": ("Sklíčko", WATCH_CATS, [
        ("safirove", "safírové", r"\bsafir\w* skl\w*|\bsafirov\w* (krystal|skl)|\bsapphire\b|\bsafir\b|^safirov\w*"),
        ("mineralni", "minerální", r"\bminer\w* skl\w*|\bhardlex|\bmineral (crystal|glass)|\bkrystal(?!y)|^mineraln\w*"),
        ("plexi", "plexisklo / akryl", r"\bplexi\w*|\bakryl\w*|\bplast\w* skl\w*|^plast\w*")]),
    "wr": ("Vodotěsnost", WATCH_CATS, [
        ("3atm", "3 ATM (stříkající voda)", r"\b3 ?(atm|bar)\b|\bwr ?30\b|\b30 ?(m|metr\w*)\b"),
        ("5atm", "5 ATM (mytí rukou, déšť)", r"\b5 ?(atm|bar)\b|\bwr ?50\b|\b50 ?(m|metr\w*)\b"),
        ("10atm", "10 ATM (plavání)", r"\b10 ?(atm|bar)\b|\bwr ?100\b|\b100 ?(m|metr\w*)\b"),
        ("20atm", "20 ATM a víc (potápění)", r"\b(20|30|50|100) ?(atm|bar)\b|\bwr ?(200|300)\b|\b(200|300|500|1000) ?(m|metr\w*)\b")]),
    "origin": ("Země původu", WATCH_CATS, [
        ("svycarsko", "Švýcarsko", r"\bsvycar\w*|\bswiss\b|\bswitzerland"),
        ("japonsko", "Japonsko", r"\bjapon\w*|\bjapan\w*"),
        ("cesko", "Česko", r"\bcesk\w*|\bczech"),
        ("nemecko", "Německo", r"\bnemec\w*|\bgerman\w*"),
        ("dansko", "Dánsko", r"\bdansk\w*|\bdenmark"),
        ("francie", "Francie", r"\bfrancouz\w*|\bfrancie|\bfrance\b")]),
    "strapw": ("Šířka řemínku", WATCH_CATS | {"reminky"}, [
        (str(w), f"{w} mm", rf"(?<![\d,.]){w} ?mm\b") for w in (12, 14, 16, 18, 19, 20, 21, 22, 24, 26)]),
    "display": ("Ciferník", WATCH_CATS, [
        ("analogovy", "analogový", r"\banalog(?!\w* ?-? ?digit)\w*|\bručičk|\brucick"),
        ("digitalni", "digitální", r"(?<!analog )(?<!analogove )\bdigital\w*"),
        ("kombinovany", "analogově-digitální", r"\banalog\w* ?-? ?digital\w*|\bana.?digi|^kombinovan\w*")]),
}
# shop parameters that decide a facet (folded text of these values); the product title and description are the fallback where TEXT_OK allows it
PRM_SRC = {"mov": ["typ strojku", "pohon"], "func": ["funkce hodinek", "funkce hodinek add", "ukazatel data", "luminiscence", "alarm"], "casemat": ["materiál pouzdra", "pouzdro"],
           "strap": ["materiál řemínku", "řemínek"], "shape": ["tvar pouzdra", "tvar hodinek"], "dialcol": ["barva ciferníku"], "strapcol": ["barva řemínku/tahu", "barva řemínku"],
           "glass": ["sklo", "sklíčko"], "wr": ["vodotěsnost"], "origin": ["původ"], "strapw": ["šířka řemínku"], "display": ["typ", "typ ciferníku"]}
# where the title/description may decide a facet when the shop gave no parameter (colour words in a title describe the whole watch, not the dial)
TEXT_OK = {"mov": WATCH_CATS, "func": WATCH_CATS, "strap": WATCH_CATS, "glass": WATCH_CATS, "wr": WATCH_CATS, "display": WATCH_CATS, "strapw": {"reminky"}}
FACETS_RX = {k: (lab, cats, [(v, vl, re.compile(rx)) for v, vl, rx in vals]) for k, (lab, cats, vals) in FACETS.items()}
FACET_VALUE = {k: {v: vl for v, vl, _ in vals} for k, (_, _, vals) in FACETS.items()}


def facet_values(text, cat, prm=None):
    """{facet: [values]} for the category-specific facets of this product: the shop's own parameters first (prm), the folded name + description start
    where the facet allows text (TEXT_OK)."""
    t = None
    out = {}
    for key, (_, cats, vals) in FACETS_RX.items():
        if cat not in cats:
            continue
        src = " ".join((prm or {}).get(k, "") for k in PRM_SRC.get(key, [])).strip()
        if src:
            body = fold(src)
        elif cat in TEXT_OK.get(key, ()):
            t = t if t is not None else fold(text)
            body = t
        else:
            continue
        hit = [v for v, _, rx in vals if rx.search(body)]
        if hit:
            out[key] = hit[:3]
    return out


# wrist circumference (cm) -> the case diameters (mm) that usually look right (rule of thumb of watch shops)
WRIST = [(14.5, 32, 37), (15.5, 34, 39), (16.5, 36, 41), (17.5, 38, 43), (18.5, 40, 45), (19.5, 42, 47), (99, 44, 50)]
