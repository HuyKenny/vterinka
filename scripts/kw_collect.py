#!/usr/bin/env python3
"""Keyword research for vterinka.cz from DataForSEO (Google, CZ). Every call is cached in content/keywords/cache/<hash>.json BEFORE the next one,
so an interrupted run resumes without paying twice; the running cost is added to content/keywords/cost.json.

    from kw_collect import dfs           # dfs("dataforseo_labs/google/ranked_keywords/live", {...}) -> task result list
    python3 scripts/kw_collect.py cost   # total spent so far

Credentials: DATAFORSEO_API_KEY (base64 login:password) from credentials/.rankizo-credentials.env. Never printed. (Ahrefs was out of units until 22. 11. 2026.)"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
CACHE = APP / "content/keywords/cache"
COST = APP / "content/keywords/cost.json"
BASE = {"location_code": 2203, "language_code": "cs"}


def _key():
    for l in open("/home/kenny/ai/credentials/.rankizo-credentials.env"):
        if l.startswith("DATAFORSEO_API_KEY="):
            return l.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("DATAFORSEO_API_KEY missing")


def dfs(endpoint, body, base=True):
    """POST one task; returns task['result'] (list). Cached by endpoint + body."""
    body = {**(BASE if base else {}), **body}
    h = hashlib.sha1((endpoint + json.dumps(body, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:16]
    f = CACHE / f"{endpoint.split('/')[-2]}-{h}.json"
    if f.exists():
        return json.loads(f.read_text())["result"]
    req = urllib.request.Request("https://api.dataforseo.com/v3/" + endpoint, data=json.dumps([body]).encode(),
                                 headers={"Authorization": "Basic " + _key(), "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    t = d["tasks"][0]
    if t["status_code"] != 20000:
        raise RuntimeError(f"{endpoint}: {t['status_code']} {t['status_message']}")
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"endpoint": endpoint, "body": body, "cost": d.get("cost"), "result": t.get("result")}, ensure_ascii=False))
    c = json.loads(COST.read_text()) if COST.exists() else {"total": 0, "calls": 0}
    c["total"] = round(c["total"] + (d.get("cost") or 0), 4)
    c["calls"] += 1
    COST.write_text(json.dumps(c))
    return t.get("result")


if __name__ == "__main__":
    if sys.argv[1:] == ["cost"]:
        print(COST.read_text() if COST.exists() else "{}")
