#!/usr/bin/env python3
"""Content gap for watches: competitor keywords (reports/vterinka/competitor-keywords-*.json, from kw_collect.py / DataForSEO) vs our live pages.

    python3 scripts/gap_hodinky.py paths.txt [competitor-keywords.json]  > reports/vterinka/content-gap-hodinky-2026-11.md

Merges the phrases (diacritics folded), drops competitor brand navigation, smart watches and noise, maps every phrase to one of our live paths by word stems
(>= 5 chars) and prints the uncovered ones ranked by search volume and number of competitors ranking. Google Ads CZ volumes are grouped (close variants share
one number): use the ORDER, not the exact value."""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

fold = lambda s: "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
BRAND_NAV = re.compile(r"\b(hodinky ?365|helveti\w*|hodinkovna|koscom|hodinarstvi|heureka|zbozi|alza|datart|allegro|glami|mall|zilka|timestore|modio|irisimo|kosik|tchibo|lidl|"
                       r"bazos|aukro|sbazar|planeo|hodinky\.cz|hodinkycz|eshop)\b")
NOISE = re.compile(r"\b(chytre|smart\w*|garmin|apple|fitbit|xiaomi|huawei|amazfit|polar|suunto|samsung|galaxy|fitness|naramek na cviceni|nastenne|kuchynske|budik\w*|stolni|"
                   r"hodiny|kukacky|piskove|slunecni|navijec|bazar|pujcovn\w*|oprava|servis\w*|baterie|vymena|navod|nastaveni|jak\b|film|pdf|zdarma|erotic\w*|sex|"
                   r"obchod\w*|prodejna|praha|brno|ostrava|plzen|olomouc|liberec|opava|cena|akce|sleva|black friday|vanoce)\b")
WATCH = re.compile(r"hodink|casio|g shock|gshock|seiko|citizen|tissot|prim\b|festina|orient|timex|fossil|swatch|lorus|hamilton|certina|bulova|edifice|baby g|wellington|"
                   r"michael kors|diesel|guess|skagen|emporio|rolex|omega|tag heuer|longines|ruzek|reminek|remínek|tah na hodinky|natahovac")
BRANDS = ["casio", "g shock", "seiko", "citizen", "tissot", "prim", "festina", "orient", "timex", "fossil", "swatch", "lorus", "hamilton", "certina", "bulova", "edifice",
          "baby g", "wellington", "michael kors", "diesel", "guess", "skagen", "emporio armani", "tommy hilfiger", "calvin klein", "lacoste", "hugo boss", "rolex", "omega",
          "tag heuer", "longines", "rado", "swiss military", "bentime", "garett", "q q", "pulsar", "lotus", "olympia star", "sector", "police", "esprit", "jacques lemans"]
stem = lambda w: w[: max(5, len(w) - 2)] if len(w) > 5 else w

paths = [p.strip() for p in Path(sys.argv[1]).read_text().split() if p.strip()]
GENERIC = {"hodinky", "hodinek", "hodinkach", "hodinka", "znacky", "kategorie", "obchody"}
toks = lambda t: {stem(w) for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in GENERIC}
pst = [(p, toks(fold(p))) for p in paths]
data = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else "/home/kenny/ai/reports/vterinka/competitor-keywords-2026-11-20.json").read_text())
rows = defaultdict(lambda: {"doms": {}, "vol": 0, "phrase": "", "urls": set()})
for dom, ks in data.items():
    for k in ks:
        key = " ".join(re.findall(r"[a-z0-9]+", fold(k["kw"])))
        if not key or BRAND_NAV.search(key) or NOISE.search(key) or not WATCH.search(key):
            continue
        r = rows[key]
        r["phrase"] = r["phrase"] or k["kw"]
        r["vol"] = max(r["vol"], k["vol"])
        r["doms"][dom] = min(r["doms"].get(dom, 99), k["pos"])
        r["urls"].add(k["url"][:70])
unc, cov = [], 0
for key, r in rows.items():
    st = toks(key)
    hit = next((p for p, ps in pst if st and st <= ps), None)
    if hit:
        cov += 1
        continue
    unc.append((key, r))
unc.sort(key=lambda x: (-x[1]["vol"], -len(x[1]["doms"])))
json.dump([{"kw": r["phrase"], "key": k, "vol": r["vol"], "n": len(r["doms"]), "best": min(r["doms"].values()), "doms": sorted(r["doms"]), "urls": sorted(r["urls"])[:2]} for k, r in unc],
          open("/home/kenny/ai/reports/vterinka/content-gap-hodinky-2026-11.json", "w"), ensure_ascii=False)
print(f"# Content gap: hodinky (vterinka.cz, 20. 11. 2026)\n\n{len(rows)} watch phrases from {len(data)} competitors, {cov} already covered by a live page, **{len(unc)} uncovered**.\n")
print("| fráze | objem | konkurentů | nejlepší pozice | URL konkurenta |\n|---|---:|---:|---:|---|")
for key, r in unc[:150]:
    print(f"| {r['phrase']} | {r['vol']} | {len(r['doms'])} | {min(r['doms'].values())} | {sorted(r['urls'])[0]} |")
