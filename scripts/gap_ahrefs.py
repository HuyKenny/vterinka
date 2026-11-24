#!/usr/bin/env python3
"""Content gap round 3 (24. 11. 2026, Ahrefs): organic keywords of CZ watch and jewellery shops that vterinka.cz has no page for.

    python3 scripts/gap_ahrefs.py comp <domain>     # organic competitors of a domain (pick the list below)
    python3 scripts/gap_ahrefs.py pull [domain …]   # organic-keywords (CZ, position <= 20, volume >= 40) per competitor -> content/keywords/cache/ahrefs-<dom>.json
    python3 scripts/gap_ahrefs.py gap               # group, match against our live sitemap URLs and page titles -> ~/ai/reports/vterinka/content-gap-ahrefs-2026-11-24.json

Token from ~/ai/credentials/.ahrefs-credentials.env (never printed). Responses are cached; a second run costs nothing."""
import datetime
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
CACHE = APP / "content/keywords/cache"
REPORT = Path.home() / "ai/reports/vterinka/content-gap-ahrefs-2026-11-24.json"
CRED = Path.home() / "ai/credentials/.ahrefs-credentials.env"
COMP = ["sofia.cz", "timestore.cz", "hodinky-koscom.cz", "helveti.cz", "hodinkovna.cz", "hodinky-365.cz", "klenotyaurum.cz", "sperky4u.eu",
        "zlatnictvi-klenoty.cz", "danfil.cz", "pandora.net", "goldhouse.cz", "snubni-prsteny-4u.cz", "minet.cz", "zlatokov.cz"]
TOPIC = r"hodin|sperk|šperk|prsten|nausn|náušn|naram|náram|retiz|řetíz|privesek|přívěs|nahrdel|náhrdel|koral|korál|charm|snubn|zasnub|zásnub|brož|broz|manžet|manzet|piercing|řemín|remin|chrono|casio|g-shock|seiko|tissot|citizen|pandora|swarovski|thomas sabo|guess|zlat|stříbr|stribr|diamant|briliant"


def token():
    for line in CRED.read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() in ("AHREFS_API_KEY", "AHREFS_API_TOKEN"):
            return v.strip().strip("\"'")
    raise SystemExit("no Ahrefs token")


def call(path, **p):
    """Ahrefs MCP over HTTP: the key in credentials is an MCP token, REST /v3 answers 401 (credentials/README.md)."""
    tool = path.replace("/", "-")
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": p}}
    req = urllib.request.Request("https://api.ahrefs.com/mcp/mcp", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        t = urllib.request.urlopen(req, timeout=300).read().decode()
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read()[:300].decode("utf8", "replace"))
        return {}
    if t.startswith("event:") or "\ndata:" in t:
        t = [x[5:] for x in t.splitlines() if x.startswith("data:")][-1]
    d = json.loads(t)
    if "error" in d:
        print("ERR", json.dumps(d["error"])[:300])
        return {}
    parts = [c.get("text", "") for c in d["result"]["content"]]
    for x in parts[1:]:
        if "apiUsageCosts" in x:
            try:
                COST[0] += json.loads(x[x.index("{"):])["apiUsageCosts"].get("units-cost-total-actual", 0)
            except (ValueError, KeyError):
                pass
    try:
        return json.loads(parts[0])
    except ValueError:
        print("non-JSON:", parts[0][:200])
        return {}


COST = [0]


def comp(dom):
    r = call("site-explorer/organic-competitors", target=dom, country="cz", mode="subdomains", date=datetime.date.today().isoformat(), limit=40,
             select="competitor_domain,keywords_common,keywords_competitor,traffic,domain_rating", order_by="keywords_common:desc")
    for x in r.get("competitors", []):
        print(f"{x['competitor_domain']:34} common {x['keywords_common']:>6}  kw {x['keywords_competitor']:>7}  traffic {x.get('traffic', 0):>8}  DR {x.get('domain_rating')}")


def pull(doms, limit=500, minvol=50, maxpos=20):
    """Max 250 rows per call -> page down by volume."""
    for d in doms:
        f = CACHE / f"ahrefs-{d}.json"
        if f.exists():
            print(d, "cached"); continue
        rows, seen, vmax = [], set(), None
        while len(rows) < limit:
            cond = [{"field": "best_position", "is": ["lte", maxpos]}, {"field": "volume", "is": ["gte", minvol]}]
            if vmax is not None:
                cond.append({"field": "volume", "is": ["lte", vmax]})
            r = call("site-explorer/organic-keywords", target=d, country="cz", mode="subdomains", date=datetime.date.today().isoformat(), limit=250,
                     order_by="volume:desc", select="keyword,volume,keyword_difficulty,best_position,best_position_url,sum_traffic", where=json.dumps({"and": cond}))
            batch = r.get("keywords", [])
            new = [x for x in batch if x["keyword"] not in seen]
            seen.update(x["keyword"] for x in new)
            rows += new
            if len(batch) < 250 or not new:
                break
            nv = batch[-1]["volume"]
            vmax = nv if nv != vmax else nv - 1
        f.write_text(json.dumps(rows, ensure_ascii=False))
        print(d, len(rows), flush=True)


def fold(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", "".join(c for c in s if not unicodedata.combining(c)))).strip()


def stem(w):
    return w[:4] if len(w) > 4 else w


def key(s):
    return " ".join(sorted({stem(w) for w in fold(s).split() if w not in ("a", "na", "s", "se", "z", "pro", "do", "v", "cz", "eshop", "e", "shop")}))


def our_pages():
    """Live sitemap URLs (slug words) - every indexable page we have."""
    def get(u):
        return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 vterinka-gap"}), timeout=60).read().decode()
    urls = []
    idx = get("https://vterinka.cz/sitemap_index.xml")
    for sm in re.findall(r"<loc>(.*?)</loc>", idx):
        if sm.endswith(".xml"):
            if "produkt" in sm:
                continue
            urls += re.findall(r"<loc>(.*?)</loc>", get(sm))
        else:
            urls.append(sm)
    return [u for u in urls if "/produkt/" not in u]


def titles(pages):
    """Page title before the ' – N kusů' tail (cached), read from the first bytes of each page."""
    from concurrent.futures import ThreadPoolExecutor
    f = CACHE / "vterinka-titles.json"
    done = json.loads(f.read_text()) if f.exists() else {}

    def one(u):
        try:
            h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 vterinka-gap"}), timeout=60).read(80000).decode("utf8", "ignore")
            m = re.search(r"<title>([^<]*)", h)
            return u, re.split(r" [–|] ", m.group(1))[0].strip() if m else ""
        except Exception:
            return u, ""
    todo = [u for u in pages if not done.get(u)]
    with ThreadPoolExecutor(1) as ex:
        for u, t in ex.map(one, todo):
            done[u] = t
    f.write_text(json.dumps(done, ensure_ascii=False))
    return {u: done.get(u, "") for u in pages}


def gap():
    rows = defaultdict(lambda: {"vol": 0, "kd": None, "sites": {}})
    for f in sorted(CACHE.glob("ahrefs-*.json")):
        d = f.stem[7:]
        for x in json.loads(f.read_text()):
            kw = x["keyword"].lower()
            if not re.search(TOPIC, kw):
                continue
            r = rows[kw]
            r["vol"] = max(r["vol"], x["volume"] or 0)
            r["kd"] = x.get("keyword_difficulty")
            r["sites"][d] = [x["best_position"], (x.get("best_position_url") or "").split("?")[0]]
    pages = our_pages()
    have = {}
    for u, title in titles(pages).items():
        path = urllib.parse.urlparse(u).path.strip("/").replace("/", " ").replace("-", " ")
        have.setdefault(key(path), u)
        if title:
            have.setdefault(key(title), u)
            if title.lower().startswith("hodinky "):          # "Hodinky Casio" also answers "casio"
                have.setdefault(key(title[8:]), u)
    out = []
    for kw, r in rows.items():
        k = key(kw)
        page = have.get(k)
        if not page:   # all our slug stems inside the keyword (e.g. "panske hodinky casio" -> /hodinky-casio/panske/)
            ks = set(k.split())
            best = [u for kk, u in have.items() if kk and set(kk.split()) == ks]
            page = best[0] if best else ""
        out.append({"kw": kw, "vol": r["vol"], "kd": r["kd"], "n_sites": len(r["sites"]), "sites": r["sites"], "ours": page})
    out.sort(key=lambda x: -x["vol"])
    REPORT.write_text(json.dumps({"date": "2026-11-24", "pages": len(pages), "rows": out}, ensure_ascii=False, indent=0))
    miss = [x for x in out if not x["ours"]]
    print(f"keywords {len(out)}, ours {len(out) - len(miss)}, missing {len(miss)}, our pages {len(pages)}")
    for x in miss[:150]:
        print(f"{x['vol']:>7} kd{x['kd'] if x['kd'] is not None else '-':>3} n{x['n_sites']} {x['kw']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "comp":
        comp(a[1])
    elif a[0] == "pull":
        pull(a[1:] or COMP)
    elif a[0] == "gap":
        gap()
    if COST[0]:
        print("Ahrefs units:", COST[0])
