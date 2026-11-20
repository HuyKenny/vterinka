#!/usr/bin/env python3
"""Writes content/landings/gap-hodinky.json: landing pages for watch phrases that people search and we did not cover
(content gap 20. 11. 2026, reports/vterinka/content-gap-hodinky-2026-11.md; volumes = Google Ads CZ via DataForSEO).
One row = one page; rules run on the folded product title (+ shop names); a page with fewer than `min` products is dropped by the build,
so rows are safe for brands we do not carry yet and appear by themselves when a feed brings them.
Re-run after editing the table:  python3 scripts/gap_landings_gen.py"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content/landings/gap-hodinky.json"
W, PAN, DAM, DET = "hodinky", "panske-hodinky", "damske-hodinky", "detske-hodinky"
# slug | h1 | rules | opts (parent, hubs, min, index_min, lead, title, desc, dedupe_all)
SWISS = ["Tissot", "Certina", "Rado", "Hamilton", "Longines", "Swiss Military", "Victorinox", "Wenger", "Mido", "Edox", "Maurice Lacroix", "Frederique Constant", "Oris",
         "Tag Heuer", "Raymond Weil", "Rolex", "Omega", "Doxa", "Traser", "Balmain", "Swatch", "Candino", "Eterna", "Rotary", "Mondaine", "Zeno-Watch", "Epos", "Davosa"]
T = [
    # ---- Casio: the most searched watch brand (casio hodinky 9 900, g-shock 5 400, edifice 2 400, vintage 1 300, digital 320)
    ("g-shock-hodinky", "G-Shock hodinky", dict(any=[r"g.?shock"]), dict(hubs=["/znacky/casio/"], lead="Odolné hodinky Casio G-Shock: nárazuvzdorné, vodotěsné, s datem a stopkami. Porovnejte ceny stejného modelu ve více obchodech.")),
    ("casio-edifice-hodinky", "Casio Edifice hodinky", dict(any=[r"\bedifice\b"]), dict(hubs=["/znacky/casio/"], lead="Casio Edifice jsou sportovně elegantní chronografy s ocelovým pouzdrem. Najděte nejnižší cenu stejného modelu.")),
    ("casio-vintage-hodinky", "Casio Vintage hodinky", dict(any=[r"\bvintage\b"], brand=["Casio"]), dict(hubs=["/znacky/casio/"], lead="Retro digitálky Casio Vintage v kovovém i černém provedení, od klasické řady F-91W po zlaté A168.")),
    ("casio-digitalni-hodinky", "Casio digitální hodinky", dict(brand=["Casio"], feats=["digitalni"]), dict(hubs=["/znacky/casio/", "/digitalni-hodinky/"])),
    ("retro-digitalni-hodinky", "Retro digitální hodinky", dict(feats=["digitalni"], styles=["retro"]), dict(hubs=["/digitalni-hodinky/", "/retro-hodinky/"])),
    # ---- more brand hubs people type with "hodinky" first
    ("citizen-eco-drive-hodinky", "Citizen Eco-Drive hodinky", dict(any=[r"eco.?drive"]), dict(hubs=["/znacky/citizen/", "/solarni-hodinky/"], lead="Hodinky Citizen Eco-Drive se nabíjejí světlem a nepotřebují baterii. Srovnání cen napříč obchody.")),
    ("armani-hodinky", "Armani hodinky", dict(brand=["Emporio Armani", "Armani Exchange", "Armani"]), dict(hubs=["/znacky/emporio-armani/", "/znacky/armani-exchange/"], lead="Hodinky Emporio Armani a Armani Exchange pro muže i ženy na jednom místě.")),
    ("svycarske-hodinky", "Švýcarské hodinky", dict(brand=SWISS), dict(lead="Hodinky od švýcarských značek, od Swatch po Tissot, Certinu a Hamilton. Porovnejte cenu stejného modelu.", title="Švýcarské hodinky – ceny, srovnání obchodů")),
    # ---- who it is for / how much
    ("levne-hodinky", "Levné hodinky", dict(price=[None, 1000]), dict(lead="Hodinky do 1 000 Kč: kvalitní quartz, které vydrží roky. Seřazeno podle toho, co obchody skutečně prodávají.", dedupe_all=True)),
    ("levne-panske-hodinky", "Levné pánské hodinky", dict(cat=[PAN], price=[None, 1500]), dict(parent="/panske-hodinky/", dedupe_all=True)),
    ("levne-damske-hodinky", "Levné dámské hodinky", dict(cat=[DAM], price=[None, 1500]), dict(parent="/damske-hodinky/", dedupe_all=True)),
    ("nejlepsi-panske-hodinky", "Nejlepší pánské hodinky", dict(cat=[PAN], offers=3), dict(parent="/panske-hodinky/", lead="Pánské hodinky, které najdete ve třech a více obchodech. Když je nabízí víc prodejců, bývají prověřené a cena se dá srovnat.")),
    ("nejlepsi-damske-hodinky", "Nejlepší dámské hodinky", dict(cat=[DAM], offers=3), dict(parent="/damske-hodinky/", lead="Dámské hodinky, které najdete ve třech a více obchodech. Srovnání cen u nejčastěji nabízených modelů.")),
    ("hodinky-pro-seniory", "Hodinky pro seniory", dict(any=[r"senior", r"velk\w* (cifern|cisl)", r"snadno citeln", r"babick", r"dedecek"], scope="text"), dict(lead="Hodinky s velkým čitelným ciferníkem a pohodlným řemínkem, které se dobře odečítají i bez brýlí.")),
    ("damske-hodinky-s-kaminky", "Dámské hodinky s kamínky", dict(cat=[DAM], any=[r"kamin", r"zirkon", r"krystal", r"swarovsk", r"brilian"]), dict(parent="/damske-hodinky/")),
    ("detske-hodinky-pro-kluky", "Dětské hodinky pro kluky", dict(cat=[DET], any=[r"\bkluk\w*", r"\bchlapc\w*", r"\bboy\w*"], scope="text"), dict(parent="/detske-hodinky/")),
    ("detske-hodinky-pro-holky", "Dětské hodinky pro holky", dict(cat=[DET], any=[r"\bholk\w*", r"\bholc\w*", r"\bdivk\w*", r"\bgirl\w*", r"princez"], scope="text"), dict(parent="/detske-hodinky/")),
    ("detske-rucickove-hodinky", "Dětské ručičkové hodinky", dict(cat=[DET], any=[r"rucick", r"analog"], scope="text"), dict(parent="/detske-hodinky/", lead="Klasické hodinky s ručičkami pro děti. Na nich se dítě nejlépe naučí poznávat čas.")),
    # ---- straps by width and material (rem. 22 mm 480, 20 mm 210, 18 mm 90, kožený 170, kovový 140, nylonový 110)
    ("reminky-na-hodinky-22-mm", "Řemínky na hodinky 22 mm", dict(cat=["reminky"], any=[r"\b22 ?mm"]), dict(parent="/reminky/")),
    ("reminky-na-hodinky-20-mm", "Řemínky na hodinky 20 mm", dict(cat=["reminky"], any=[r"\b20 ?mm"]), dict(parent="/reminky/")),
    ("reminky-na-hodinky-18-mm", "Řemínky na hodinky 18 mm", dict(cat=["reminky"], any=[r"\b18 ?mm"]), dict(parent="/reminky/")),
    ("kozene-reminky-na-hodinky", "Kožené řemínky na hodinky", dict(cat=["reminky"], any=[r"kozen", r"\bkuze\b", r"\bkuzi\b"]), dict(parent="/reminky/")),
    ("kovove-reminky-na-hodinky", "Kovové řemínky na hodinky", dict(cat=["reminky"], any=[r"\bkovov", r"\bocelov", r"milansk", r"\btah\b"]), dict(parent="/reminky/")),
    ("silikonove-reminky-na-hodinky", "Silikonové řemínky na hodinky", dict(cat=["reminky"], any=[r"silikon", r"gumov"]), dict(parent="/reminky/")),
    ("nylonove-reminky-na-hodinky", "Nylonové a textilní řemínky na hodinky", dict(cat=["reminky"], any=[r"nylon", r"textil", r"\bnato\b"]), dict(parent="/reminky/")),
]


def main():
    pages = []
    for slug, h1, rules, o in T:
        rules = dict(rules)
        rules.setdefault("cat", [W])             # every hub is watches only: the room "hodinky" (jewellery has the same brands and words)
        r = {"slug": slug, "h1": h1, "group": "gap-hodinky", "rules": rules}
        r["parent"] = o.get("parent")
        for k in ("hubs", "min", "index_min", "lead", "title", "desc", "dedupe_all"):
            if k in o:
                r[k] = o[k]
        pages.append(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pages, ensure_ascii=False, indent=1))
    print(len(pages), "pages ->", OUT)


if __name__ == "__main__":
    main()
