"""Local development only: load API keys from the workspace credentials/ folder into os.environ.
In GitHub Actions the same names come from repository secrets. Values are never printed.
This file holds no secrets itself — only file and key NAMES."""
import os
from pathlib import Path

CRED = Path(os.environ.get("VT_CRED_DIR", "/home/kenny/ai/credentials"))
FILES = [".vterinka-credentials.env"]


def load():
    for name in FILES:
        p = CRED / name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v.strip().strip("\"'"))

    feeds = CRED / ".vterinka-feeds.json"        # {feed_key: URL}; URLs carry tokens, so they live only here and in the FEEDS_JSON secret
    if feeds.exists():
        import json
        os.environ.setdefault("FEEDS_JSON", json.dumps(json.load(feeds.open()), separators=(",", ":")))
