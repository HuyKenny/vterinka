"""Long-tail landing pages: category x colour / material / style / feature / facet / case size / price, plus hand-written records.

People search "pánské automatické hodinky", "dámské hodinky s koženým řemínkem", "stříbrné náušnice kruhy",
"zlatý prsten s diamantem", "hodinky safírové sklo". Each family below turns the catalogue into such pages; a page exists only with enough products
(MIN, else nothing), and is indexable only from INDEX_MIN products (fewer = noindex,follow and out of the sitemap).
Hand-written records (content/landings/*.json) say WHAT a page is and the engine finds the products:
  {"slug": "...", "h1": "...", "rules": {"cat": ["sedacky"], "any": ["\\bchesterfield\\b"], "colors": ["seda"], "price": [null, 15000]}}
Rule keys: any / all / none (regex on the folded product titles; "scope": "text" adds description + shop paths), cat, brand,
colors, mats, styles, feats (any of), price [lo, hi], wmax / wmin (width in cm), size ("160x200"), offers (min shops).
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import taxonomy as X

APP = Path(__file__).resolve().parent.parent
MIN_DEFAULT, INDEX_MIN_DEFAULT = 6, 12
BRAND_GENDER_CATS = {"panske-hodinky", "damske-hodinky", "detske-hodinky"}
BRAND_GENDER_MIN = 10
fold = X.fold

# plural adjective forms: categories are feminine/masculine-inanimate plural ("pánské hodinky", "zlaté prsteny", "stříbrné náušnice"),
# a few neuter singular ("piercing" is masculine singular -> handled by NEUTER_SG ending "ý")
NEUTER_PL = set()
NEUTER_SG = set()
MASC_SG = {"piercing"}

COLOR_ADJ = {"zlata": "zlat", "ruzove-zlata": "růžově zlat", "stribrna": "stříbrn", "cerna": "čern", "bila": "bíl", "modra": "modr", "zelena": "zelen",
             "cervena": "červen", "ruzova": "růžov", "hneda": "hněd", "seda": "šed"}
MAT_ADJ = {"stribro": "stříbrn", "zlato": "zlat", "bile-zlato": "z bílého zlata#", "ruzove-zlato": "z růžového zlata#", "pozlacene": "pozlacen",
           "chirurgicka-ocel": "z chirurgické oceli#", "ocel": "ocelov", "titan": "titanov", "wolfram": "wolframov", "keramika": "keramick",
           "kuze": "s koženým řemínkem#", "drevo": "dřevěn", "silikon": "se silikonovým řemínkem#", "textil": "s textilním řemínkem#",
           "milansky-tah": "s milánským tahem#"}
STYLE_ADJ = {"sportovni": "sportovní*", "elegantni": "elegantní*", "luxusni": "luxusní*", "retro": "retro*", "minimalisticky": "minimalistick", "boho": "boho*"}
FEAT_ADJ = {"automaticke": "automatick", "mechanicke": "mechanick", "solarni": "solární*", "rizene-radiem": "řízené rádiem#", "chronograf": "s chronografem#",
            "digitalni": "digitální*", "potapecske": "potápěčsk", "pilotni": "pilotní*", "vojenske": "vojensk", "skeleton": "skeleton#",
            "s-perlou": "s perlou#", "s-diamantem": "s diamantem#", "se-zirkony": "se zirkony#", "s-krystaly": "s krystaly#", "s-kamenem": "s kamenem#",
            "srdce": "se srdcem#", "kriz": "s křížkem#", "strom-zivota": "se stromem života#", "nekonecno": "s nekonečnem#", "ctyrlistek": "se čtyřlístkem#",
            "andel": "s andělem#", "pismeno": "s písmenem#", "znameni": "se znamením zvěrokruhu#", "kruhove": "kruhov", "pecky": "pecky#",
            "visaci": "visací*", "klipsy": "klipsy#", "pro-muze": "pánsk", "pro-zeny": "dámsk", "pro-deti": "dětsk"}
COLOR_SLUG = {"zlata": "zlate", "ruzove-zlata": "rose-gold", "stribrna": "stribrne", "cerna": "cerne", "bila": "bile", "modra": "modre", "zelena": "zelene",
              "cervena": "cervene", "ruzova": "ruzove", "hneda": "hnede", "seda": "sede"}
MAT_SLUG = {"stribro": "ze-stribra", "zlato": "ze-zlata", "bile-zlato": "z-bileho-zlata", "ruzove-zlato": "z-ruzoveho-zlata", "pozlacene": "pozlacene",
            "chirurgicka-ocel": "z-chirurgicke-oceli", "ocel": "ocelove", "titan": "titanove", "wolfram": "wolframove", "keramika": "keramicke",
            "kuze": "s-kozenym-reminkem", "drevo": "drevene", "silikon": "se-silikonovym-reminkem", "textil": "s-textilnim-reminkem",
            "milansky-tah": "s-milanskym-tahem"}
STYLE_SLUG = {"sportovni": "sportovni", "elegantni": "elegantni", "luxusni": "luxusni", "retro": "retro", "minimalisticky": "minimalisticke", "boho": "boho"}
FEAT_SLUG = {"pro-muze": "panske", "pro-zeny": "damske", "pro-deti": "detske", "kruhove": "kruhove", "pecky": "pecky", "visaci": "visaci", "klipsy": "klipsy"}
# which features may make a landing in which categories (an earring type only on earrings, gender only on jewellery)
WATCH_ONLY_MATS = {"kuze", "silikon", "textil", "milansky-tah"}


def adj(stem, cat):
    """'šed' -> 'šedé' / 'šedá' / 'šedé' by the category's grammar; '*' = indeclinable before the noun, '#' = after the noun."""
    if stem.endswith("#"):
        return None, stem[:-1]
    if stem.endswith("*"):
        return stem[:-1], None
    if cat in MASC_SG:
        end = "ý"
    else:
        end = "é"
    return stem + ("í" if stem.endswith("í") else end), None


def phrase(stem, cat, noun):
    pre, post = adj(stem, cat)
    noun_l = noun[:1].lower() + noun[1:] if not noun[:2].isupper() else noun
    if pre:
        return f"{pre[:1].upper() + pre[1:]} {noun_l}"
    return f"{noun} {post}"


def hay(p):
    h = p.get("_h")
    if h is None:
        h = fold(" ".join([p["name"], p["dry"], p["desc"][:600], p.get("paths", "")]))
        p["_h"] = h
    return h


def title_hay(p):
    h = p.get("_t")
    if h is None:
        h = fold(p["name"] + " " + p["dry"])
        p["_t"] = h
    return h


def compile_rules(r):
    rx = lambda lst: [re.compile(x) for x in lst]
    any_, all_, none_ = rx(r.get("any", [])), rx(r.get("all", [])), rx(r.get("none", []))
    cats, brands = tuple(r.get("cat", [])), {fold(b) for b in r.get("brand", [])}
    price, offers = r.get("price"), r.get("offers", 0)
    sets = {k: set(r[k]) for k in ("colors", "mats", "styles", "feats") if r.get(k)}
    wmax, wmin, size = r.get("wmax"), r.get("wmin"), r.get("size")
    haystack = hay if r.get("scope") == "text" else title_hay

    def pred(p):
        if cats and p["cat"] not in cats and X.TREE[p["cat"]][1] not in cats:
            return False
        if offers and len(p["offers"]) < offers:
            return False
        if price and ((price[0] is not None and p["price"] < price[0]) or (price[1] is not None and p["price"] > price[1])):
            return False
        if brands and fold(p["brand"]) not in brands:
            return False
        for k, want in sets.items():
            if not want & set(p[k]):
                return False
        if wmax is not None and not (p["wmin"] and p["wmin"] <= wmax):
            return False
        if wmin is not None and not (p["wmax"] and p["wmax"] >= wmin):
            return False
        if size and size not in p["sizes"]:
            return False
        if any_ or all_ or none_:
            h = haystack(p)
            if any_ and not any(x.search(h) for x in any_):
                return False
            if all_ and not all(x.search(h) for x in all_):
                return False
            if none_ and any(x.search(h) for x in none_):
                return False
        return True
    return pred


def load_records():
    recs = []
    for f in sorted((APP / "content/landings").glob("*.json")):
        data = json.loads(f.read_text())
        recs += data if isinstance(data, list) else data.get("pages", [])
    return recs


def nice_cap(n):
    return f"{n:,}".replace(",", " ")


def price_caps(items):
    """2-3 round price caps that split the category sensibly (do 5 000 Kč, do 10 000 Kč…)."""
    ps = sorted(p["price"] for p in items)
    steps = [300, 500, 1000, 2000, 3000, 5000, 7000, 10000, 15000, 20000, 30000, 50000]
    out = []
    for q in (0.25, 0.5):
        v = ps[int(len(ps) * q)]
        cap = next((s for s in steps if s >= v), None)
        if cap and cap not in out:
            out.append(cap)
    return out


def generated_records(products, by_cat):
    recs = []
    for cat, items in by_cat.items():
        if cat not in X.CATS or len(items) < MIN_DEFAULT:
            continue
        name = X.CATS[cat][0]
        noun = name
        watch = cat in X.WATCH_CATS
        base = {"parent": f"/{cat}/", "cat": cat}
        cnt = lambda key: Counter(x for p in items for x in p[key])
        for c, n in cnt("colors").most_common():
            if n >= MIN_DEFAULT and not (not watch and c in ("zlata", "stribrna", "ruzove-zlata")):    # jewellery: the metal pages say it
                recs.append({**base, "slug": f"{cat}/{COLOR_SLUG[c]}", "h1": phrase(COLOR_ADJ[c], cat, noun), "group": f"{cat}-color",
                             "_pred": (lambda c: lambda p: c in p["colors"])(c), "facet": ("colors", c)})
        for m, n in cnt("mats").most_common():
            if n >= MIN_DEFAULT and (watch or m not in WATCH_ONLY_MATS) and cat not in ("reminky",) and not (watch and m in ("stribro", "zlato", "pozlacene")):
                recs.append({**base, "slug": f"{cat}/{MAT_SLUG[m]}", "h1": phrase(MAT_ADJ[m], cat, noun), "group": f"{cat}-mat",
                             "_pred": (lambda m: lambda p: m in p["mats"])(m), "facet": ("mats", m)})
        for s_, n in cnt("styles").most_common():
            if n >= MIN_DEFAULT:
                klas = watch and s_ == "elegantni"       # watches: people say "klasické hodinky" (110/month) as much as "elegantní" (140); the style rule catches both words
                recs.append({**base, "slug": f"{cat}/{'klasicke' if klas else STYLE_SLUG[s_]}", "h1": phrase("klasick" if klas else STYLE_ADJ[s_], cat, noun),
                             "group": f"{cat}-style", "_pred": (lambda s_: lambda p: s_ in p["styles"])(s_), "facet": ("styles", s_)})
        if cat in BRAND_GENDER_CATS:      # "pánské hodinky Casio", "dámské hodinky Michael Kors": the biggest uncovered family in the 11/2026 gap (brand x gender, 100-900 searches each)
            for b, n in Counter(p["brand"] for p in items if p["brand"]).most_common():
                bs = X.slugify(b)
                if n >= BRAND_GENDER_MIN and bs and bs not in X.TREE:
                    recs.append({**base, "slug": f"{cat}/{bs}", "h1": f"{noun} {b}", "group": f"{cat}-brand", "hubs": [f"/znacky/{bs}/"],
                                 "_pred": (lambda b: lambda p: p["brand"] == b)(b), "facet": ("brand", b)})
        for f_, n in cnt("feats").most_common():
            if n < MIN_DEFAULT or (f_ in X.EARRING_FEATS and cat != "nausnice"):
                continue
            h1 = phrase(FEAT_ADJ[f_], cat, noun)
            if f_ in X.GENDER_FEATS:
                h1 = FEAT_ADJ[f_][:1].upper() + FEAT_ADJ[f_][1:] + ("ý" if cat in MASC_SG else "é") + " " + noun[:1].lower() + noun[1:]
            recs.append({**base, "slug": f"{cat}/{FEAT_SLUG.get(f_, f_)}", "h1": h1, "group": f"{cat}-feat",
                         "_pred": (lambda f_: lambda p: f_ in p["feats"])(f_), "facet": ("feats", f_)})
        for key, (lab, cats, vals) in X.FACETS.items():          # watch facets people search: "hodinky safírové sklo", "vodotěsné hodinky 10 ATM"
            if cat not in cats or key == "display":
                continue
            for v, n in Counter(x for p in items for x in (p.get("fx") or {}).get(key, [])).most_common():
                if n >= MIN_DEFAULT:
                    vl = X.FACET_VALUE[key][v]
                    h1 = {"glass": f"{name} se {'safírovým' if v == 'safirove' else 'minerálním' if v == 'mineralni' else 'plastovým'} sklíčkem",
                          "wr": f"{name} {vl.split(' (')[0]}", "strap": f"{name} – řemínek {vl}"}[key]
                    recs.append({**base, "slug": f"{cat}/{key}-{v}", "h1": h1, "group": f"{cat}-{key}",
                                 "_pred": (lambda key, v: lambda p: v in (p.get("fx") or {}).get(key, []))(key, v)})
        for cap in price_caps(items):
            recs.append({**base, "slug": f"{cat}/do-{cap}-kc", "h1": f"{name} do {nice_cap(cap)} Kč", "group": f"{cat}-cap",
                         "_pred": (lambda cap: lambda p: p["price"] <= cap)(cap), "facet": ("price", cap)})
        if watch:     # case size: "pánské hodinky 40 mm", "malé dámské hodinky"
            ws = [p["wmin"] for p in items if p["wmin"]]
            if len(ws) >= 20:
                for lo, hi, lab in ((0, 34, "malé (do 34 mm)"), (34, 38.9, "střední (34–38 mm)"), (39, 42.9, "39–42 mm"), (43, 99, "velké (43 mm a víc)")):
                    sel = sum(1 for w in ws if lo <= w <= hi)
                    if sel >= MIN_DEFAULT:
                        recs.append({**base, "slug": f"{cat}/pouzdro-{int(lo)}-{int(hi) if hi < 99 else 'plus'}-mm", "h1": f"{name} {lab}", "group": f"{cat}-size",
                                     "_pred": (lambda lo, hi: lambda p: p["wmin"] is not None and lo <= p["wmin"] <= hi)(lo, hi),
                                     "title": f"{name} {lab} – srovnání cen"})
    # combinations people type: movement x material for men's/women's watches, metal x stone/motif for jewellery
    for cat in ("panske-hodinky", "damske-hodinky"):
        items = by_cat.get(cat, [])
        for f_ in ("automaticke", "solarni", "chronograf"):
            for m in ("ocel", "titan", "kuze"):
                n = sum(1 for p in items if f_ in p["feats"] and m in p["mats"])
                if n >= INDEX_MIN_DEFAULT:
                    h1 = phrase(FEAT_ADJ[f_], cat, X.CATS[cat][0])
                    pre, post = adj(MAT_ADJ[m], cat)
                    h1 = (f"{h1} {post}" if post else pre[:1].upper() + pre[1:] + " " + h1[:1].lower() + h1[1:])
                    recs.append({"parent": f"/{cat}/{f_}/", "cat": cat, "slug": f"{cat}/{f_}/{MAT_SLUG[m]}", "h1": h1, "group": f"{cat}-combo",
                                 "_pred": (lambda f_, m: lambda p: f_ in p["feats"] and m in p["mats"])(f_, m)})
    for cat in ("prsteny", "nausnice", "nahrdelniky", "naramky", "privesky", "retizky"):
        items = by_cat.get(cat, [])
        for m in ("stribro", "zlato", "chirurgicka-ocel"):
            for f_ in ("s-perlou", "s-diamantem", "se-zirkony", "s-kamenem", "srdce", "kriz", "strom-zivota", "pro-muze", "pro-deti", "kruhove", "pecky"):
                n = sum(1 for p in items if f_ in p["feats"] and m in p["mats"])
                if n >= INDEX_MIN_DEFAULT and not (f_ in X.EARRING_FEATS and cat != "nausnice"):
                    noun = X.CATS[cat][0]
                    pre, post = adj(MAT_ADJ[m], cat)
                    if f_ in X.GENDER_FEATS:
                        g = FEAT_ADJ[f_] + "é"
                        h1 = f"{g[:1].upper() + g[1:]} {pre or ''} {noun.lower()}{' ' + post if post else ''}".replace("  ", " ")
                    else:
                        fp, fpost = adj(FEAT_ADJ[f_], cat)
                        h1 = f"{(pre + ' ') if pre else ''}{(fp + ' ') if fp else ''}{noun.lower()}{' ' + post if post else ''}{' ' + fpost if fpost else ''}"
                        h1 = h1[:1].upper() + h1[1:]
                    recs.append({"parent": f"/{cat}/{MAT_SLUG[m]}/", "cat": cat, "slug": f"{cat}/{MAT_SLUG[m]}/{FEAT_SLUG.get(f_, f_)}", "h1": h1,
                                 "group": f"{cat}-combo", "_pred": (lambda f_, m: lambda p: f_ in p["feats"] and m in p["mats"])(f_, m)})
    # whole-site hubs searched as one phrase: "automatické hodinky", "hodinky s chronografem", "stříbrné šperky", "pánské šperky"
    watches = [p for c, ps in by_cat.items() if c in X.WATCH_CATS for p in ps]
    jewels = [p for c, ps in by_cat.items() if c in X.JEWEL_CATS for p in ps]
    hubs = [("automaticke-hodinky", "Automatické hodinky", watches, "feats", "automaticke"), ("mechanicke-hodinky", "Mechanické hodinky", watches, "feats", "mechanicke"),
            ("solarni-hodinky", "Solární hodinky", watches, "feats", "solarni"), ("hodinky-rizene-radiem", "Hodinky řízené rádiem", watches, "feats", "rizene-radiem"),
            ("hodinky-s-chronografem", "Hodinky s chronografem", watches, "feats", "chronograf"), ("digitalni-hodinky", "Digitální hodinky", watches, "feats", "digitalni"),
            ("potapecske-hodinky", "Potápěčské hodinky", watches, "feats", "potapecske"), ("pilotni-hodinky", "Pilotní hodinky", watches, "feats", "pilotni"),
            ("vojenske-hodinky", "Vojenské hodinky", watches, "feats", "vojenske"), ("titanove-hodinky", "Titanové hodinky", watches, "mats", "titan"),
            ("keramicke-hodinky", "Keramické hodinky", watches, "mats", "keramika"), ("drevene-hodinky", "Dřevěné hodinky", watches, "mats", "drevo"),
            ("zlate-hodinky", "Zlaté hodinky", watches, "colors", "zlata"), ("luxusni-hodinky", "Luxusní hodinky", watches, "styles", "luxusni"),
            ("sportovni-hodinky", "Sportovní hodinky", watches, "styles", "sportovni"), ("klasicke-hodinky", "Klasické hodinky", watches, "styles", "elegantni"),
            ("retro-hodinky", "Retro hodinky", watches, "styles", "retro"),
            ("stribrne-sperky", "Stříbrné šperky", jewels, "mats", "stribro"), ("zlate-sperky", "Zlaté šperky", jewels, "mats", "zlato"),
            ("sperky-z-chirurgicke-oceli", "Šperky z chirurgické oceli", jewels, "mats", "chirurgicka-ocel"), ("ocelove-sperky", "Ocelové šperky", jewels, "mats", "ocel"),
            ("panske-sperky", "Pánské šperky", jewels, "feats", "pro-muze"), ("detske-sperky", "Dětské šperky", jewels, "feats", "pro-deti"),
            ("perlove-sperky", "Perlové šperky", jewels, "feats", "s-perlou"), ("sperky-s-diamanty", "Šperky s diamanty", jewels, "feats", "s-diamantem"),
            ("sperky-se-zirkony", "Šperky se zirkony", jewels, "feats", "se-zirkony"), ("sperky-s-polodrahokamy", "Šperky s polodrahokamy", jewels, "feats", "s-kamenem"),
            ("boho-sperky", "Boho šperky", jewels, "styles", "boho"), ("minimalisticke-sperky", "Minimalistické šperky", jewels, "styles", "minimalisticky")]
    for slug, h1, pool, key, val in hubs:
        recs.append({"slug": slug, "h1": h1, "group": "hub-" + key, "parent": None, "home": True,
                     "_items": [p for p in pool if val in p[key]], "facet": (key, val)})
    return recs


def jaccard(a, b):
    return len(a & b) / max(1, len(a | b))


def plan(products, reserved=()):
    """Evaluate all records. Returns landing dicts (path, h1, items, ...) in priority order; skips tiny, duplicate and reserved ones."""
    by_cat = defaultdict(list)
    for p in products:
        by_cat[p["cat"]].append(p)
    recs = load_records() + generated_records(products, by_cat)
    late = ("kw2", "gap7")       # phrase pages last: they only add what the families do not cover; gap7 (round 7 facets) after kw2 so live kw2 URLs keep their products
    recs = [r for r in recs if r.get("group") not in late] + [r for g in late for r in recs if r.get("group") == g]
    seen_paths, groups, out, dropped = set(reserved), defaultdict(list), [], defaultdict(int)
    seen_h1 = set()
    all_sets = []        # product-id sets of every accepted page: records with "dedupe_all" must differ from all of them
    for r in recs:
        path = "/" + r["slug"].strip("/") + "/"
        if r["h1"].lower() in seen_h1:
            dropped["same h1 as an earlier page"] += 1
            continue
        if path in seen_paths:
            dropped["path exists"] += 1
            continue
        if "_items" in r:
            items = r["_items"]
        elif r.get("_pred"):
            pool = by_cat.get(r["cat"], products) if r.get("cat") else products
            items = [p for p in pool if r["_pred"](p)]
        else:
            pred = compile_rules(r.get("rules", {}))
            cats = (r.get("rules") or {}).get("cat", [])
            pool = [p for c in cats for p in by_cat.get(c, [])] + [p for c in cats if c in X.ROOMS for k in X.CATS if X.CATS[k][1] == c for p in by_cat.get(k, [])] if cats else products
            items = [p for p in pool if pred(p)]
        items = [p for p in items if p.get("page", True)]
        if len(items) < r.get("min", MIN_DEFAULT):
            dropped["too few"] += 1
            continue
        if r.get("cat") and len(items) >= 0.95 * len(by_cat.get(r["cat"], [])):
            dropped["same as the category"] += 1
            continue
        ids = {p["id"] for p in items}
        g = r.get("group") or r["slug"].split("/")[0]
        if any(jaccard(ids, o) > 0.9 for o in groups[g]):
            dropped["duplicate of a sibling"] += 1
            continue
        if r.get("dedupe_all") and any(0.85 <= len(ids) / max(1, len(o)) <= 1 / 0.85 and jaccard(ids, o) > 0.85 for o in all_sets):
            dropped["same products as an existing page"] += 1
            continue
        all_sets.append(ids)
        groups[g].append(ids)
        seen_paths.add(path)
        seen_h1.add(r["h1"].lower())
        prices = sorted(p["price"] for p in items)
        out.append({"path": path, "slug": r["slug"].strip("/"), "h1": r["h1"], "title": r.get("title"), "lead": r.get("lead"), "desc": r.get("desc"), "items": items,
                    "parent": r.get("parent"), "hubs": r.get("hubs", []), "group": g, "cat": r.get("cat") or ((r.get("rules") or {}).get("cat") or [None])[0],
                    "home": r.get("home", False), "facet": r.get("facet"),
                    "index": len(items) >= r.get("index_min", INDEX_MIN_DEFAULT), "lo": prices[0], "n": len(items)})
    return out, dict(dropped)


def kids_map(landings):
    """path of a hub page -> [(path, h1, n)] of landing pages that belong under it (parent) or want a link from it (hubs)."""
    kids = defaultdict(list)
    for L in landings:
        for hub in set(([L["parent"]] if L["parent"] else []) + list(L["hubs"])):
            kids[hub].append((L["path"], L["h1"], L["n"]))
    return kids


# ---------------------------------------------------------------- guides (content/guides): _index.json = metadata + product-pick rules, <slug>.json = text
def load_guides():
    gd = APP / "content/guides"
    if not (gd / "_index.json").exists():
        return []
    meta = {g["slug"]: g for g in json.loads((gd / "_index.json").read_text())}
    out = []
    for slug, g in meta.items():
        f = gd / f"{slug}.json"
        if f.exists():
            t = json.loads(f.read_text())
            out.append({**g, "intro": t.get("intro", ""), "body": t.get("body", ""), "faq": t.get("faq", []), "description": t.get("description")})
    return out


def guide_picks(products, g, limit=8):
    rules = dict(g.get("rules") or {})
    if g.get("cat"):
        rules["cat"] = g["cat"]
    pred = compile_rules(rules)
    cats = set(rules.get("cat", []))
    pool = [p for p in products if p["cat"] in cats or X.TREE[p["cat"]][1] in cats] if cats else products
    items = [p for p in pool if pred(p) and p["img"] and p.get("page", True)]
    items.sort(key=lambda p: (-len(p["offers"]), p["price"]))
    return items[:limit]
