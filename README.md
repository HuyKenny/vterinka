# vterinka.cz

Static price comparison of **classic watches** (no smart watches) and jewellery from Czech e-shops (affiliate feeds from CJ).
Watches are sorted by who wears them (men's, women's, kids', unisex, pocket), jewellery by kind of piece; the same model in
several shops is matched by EAN or by brand + reference number (Casio MTP-1302PD-1A, Tissot T137.407.11.041.00).

- `scripts/fetch.py` — download offers from the networks into `data/raw/` (not committed)
- `scripts/taxonomy.py` — departments and categories, classifier (smart-watch veto), gender, movement, glass, water resistance,
  strap, metal, stones, motifs, case diameter (mm) and ring size
- `scripts/catalog.py` — match offers across shops, merge sizes of one ring, stable slugs, price history
- `scripts/landings.py` — long-tail pages: category × movement / material / colour / style / glass / ATM / case size / price,
  jewellery metal × stone/motif, site-wide hubs ("automatické hodinky", "stříbrné šperky")
- `scripts/build.py` + `render.py` + `texts.py` — plain-Python static site generator → `dist/`
- `scripts/deploy.py` — Cloudflare Workers **static assets only** (no Worker script, nothing billed per request);
  product pages are split into shard Workers when one Worker would exceed 100 000 files
- `.github/workflows/build.yml` — nightly build in GitHub Actions (01:40 CET); manual run with `quick` = fix path for CSS/JS/text
- `scripts/make_logo.py` — logo and favicons from the Bodoni Moda outlines

## Secrets

This repository is public. It contains code only: no API keys, no feed URLs, no catalogue data.
Keys live in GitHub Actions secrets; the build state is stored as an **encrypted** release asset (`scripts/state.sh`).
`scripts/verify_no_secrets.py` and gitleaks run on every build and fail it if a secret value shows up in the repo or the output.
Affiliate IDs inside product links (CJ website id) are public by nature.

Python 3.11+, standard library only. Illustrations made in Canva; fonts Bodoni Moda and Hanken Grotesk (SIL OFL, see `static/fonts/`).
