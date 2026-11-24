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
    # ---- series and lines (what hodinky-365 / helveti / koscom rank for: GA-2100, DW-5600, Mr-G, PRX, Ballade, Collection…); dropped by the build until a feed brings >= min products
    ("casio-ga-2100", "Casio G-Shock GA-2100 (CasiOak)", dict(any=[r"\bga.?2100", r"casioak"]), dict(hubs=["/g-shock-hodinky/"], min=4, index_min=8)),
    ("casio-dw-5600", "Casio G-Shock DW-5600", dict(any=[r"\bdw.?5600", r"\bdw.?5610"]), dict(hubs=["/g-shock-hodinky/"], min=4, index_min=8)),
    ("casio-gw-m5610", "Casio G-Shock GW-M5610 solární", dict(any=[r"\bgw.?m5610", r"\bgw.?5000"]), dict(hubs=["/g-shock-hodinky/"], min=3, index_min=6)),
    ("g-shock-g-squad", "G-Shock G-Squad", dict(any=[r"g.?squad", r"\bgbd.?\d"]), dict(hubs=["/g-shock-hodinky/"], min=4, index_min=8)),
    ("g-shock-mudmaster", "G-Shock MudMaster", dict(any=[r"mudmaster", r"\bgg.?b100", r"\bgwg.?b1000"]), dict(hubs=["/g-shock-hodinky/"], min=3, index_min=6)),
    ("g-shock-mr-g", "G-Shock Mr-G", dict(any=[r"\bmr.?g\b", r"\bmrg.?"]), dict(hubs=["/g-shock-hodinky/"], min=3, index_min=6)),
    ("g-shock-frogman-rangeman", "G-Shock Frogman a Rangeman", dict(any=[r"frogman", r"rangeman", r"\bgw.?9400", r"\bgwf.?"]), dict(hubs=["/g-shock-hodinky/"], min=3, index_min=6)),
    ("casio-collection-hodinky", "Casio Collection hodinky", dict(brand=["Casio"], any=[r"\bcollection\b", r"\bmtp.?\d", r"\bltp.?\d"]), dict(hubs=["/znacky/casio/"])),
    ("casio-f-91w", "Casio F-91W a A168", dict(any=[r"\bf.?91w", r"\ba.?168", r"\ba.?158", r"\ba.?700"]), dict(hubs=["/casio-vintage-hodinky/"], min=4, index_min=8)),
    ("casio-pro-trek", "Casio Pro Trek", dict(any=[r"pro.?trek", r"\bprg.?\d", r"\bprw.?\d"]), dict(hubs=["/znacky/casio/"], min=4, index_min=8)),
    ("casio-baby-g", "Casio Baby-G", dict(any=[r"baby.?g\b", r"\bbga.?\d", r"\bbgd.?\d"]), dict(hubs=["/znacky/casio/"])),
    ("tissot-prx", "Tissot PRX", dict(any=[r"\bprx\b"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/"], min=3, index_min=6)),
    ("tissot-ballade", "Tissot Ballade", dict(any=[r"ballade"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/"], min=3, index_min=6)),
    ("tissot-le-locle-gentleman", "Tissot Le Locle a Gentleman", dict(any=[r"le locle", r"gentleman"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/"], min=3, index_min=6)),
    ("tissot-t-touch", "Tissot T-Touch", dict(any=[r"t.?touch"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/"], min=3, index_min=6)),
    ("tissot-seastar-prc-200", "Tissot Seastar a PRC 200", dict(any=[r"seastar", r"prc.?200", r"prc.?100", r"supersport"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/"], min=3, index_min=6)),
    ("seiko-5-sports", "Seiko 5 Sports", dict(any=[r"seiko 5\b", r"\bsrpd", r"\bsnk\d", r"\bsrp[a-z]\d"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("seiko-presage-prospex", "Seiko Presage a Prospex", dict(any=[r"presage", r"prospex"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("citizen-promaster-attesa", "Citizen Promaster a Attesa", dict(any=[r"promaster", r"attesa", r"\bsatellite wave"], brand=["Citizen"]), dict(hubs=["/znacky/citizen/"], min=3, index_min=6)),
    ("orient-bambino-mako", "Orient Bambino, Mako a Kamasu", dict(any=[r"bambino", r"\bmako\b", r"kamasu", r"\bstar\b"], brand=["Orient"]), dict(hubs=["/znacky/orient/"], min=3, index_min=6)),
    ("daniel-wellington-classic-petite", "Daniel Wellington Classic a Petite", dict(any=[r"classic", r"petite", r"quadro", r"iconic"], brand=["Daniel Wellington"]), dict(hubs=["/znacky/daniel-wellington/"])),
    ("timex-weekender-expedition", "Timex Weekender a Expedition", dict(any=[r"weekender", r"expedition", r"marlin", r"easy reader"], brand=["Timex"]), dict(hubs=["/znacky/timex/"])),
    ("swatch-sistem51-moonswatch", "Swatch Sistem51 a MoonSwatch", dict(any=[r"sistem ?51", r"moonswatch", r"moon ?swatch", r"royal pop"], brand=["Swatch"]), dict(hubs=["/znacky/swatch/"], min=3, index_min=6)),
    ("hamilton-khaki", "Hamilton Khaki Field", dict(any=[r"khaki"], brand=["Hamilton"]), dict(hubs=["/znacky/hamilton/"], min=3, index_min=6)),
    ("zlate-hodinky-casio", "Zlaté hodinky Casio", dict(brand=["Casio"], colors=["zlata"]), dict(hubs=["/znacky/casio/", "/zlate-hodinky/"])),
    ("hodinky-na-behani", "Sportovní hodinky na běhání a trénink", dict(any=[r"\brunning\b", r"\bbezeck\w*", r"\bbehani\b", r"\bsport\w* (hodink|chronograf)", r"\bpro.?trek", r"\bg.?shock"], none=[r"chytr\w*", r"smart\w*"]), dict(hubs=["/sportovni-hodinky/"], min=8)),
    ("hodinky-do-vody", "Vodotěsné hodinky do vody (10 ATM a víc)", dict(any=[r"\b(10|20|30|50|100) ?atm", r"\b(100|200|300) ?m\b", r"\bplavani\b", r"\bplavec\w*"]), dict(hubs=["/potapecske-hodinky/"], min=10)),
    # ---- round 3 (Ahrefs 24. 11. 2026, volumes Ahrefs CZ): series and brands competitors rank for
    ("seiko-alpinist", "Seiko Alpinist", dict(any=[r"alpinist", r"\bspb1(21|55|97|99)", r"\bsarb017"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("seiko-turtle", "Seiko Turtle (Prospex)", dict(any=[r"\bturtle\b", r"\bsrp(77[3-9]|78[0-9])", r"\bsrpe9", r"\bsrpg"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("seiko-astron", "Seiko Astron", dict(any=[r"astron"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("seiko-presage-cocktail-time", "Seiko Presage Cocktail Time", dict(any=[r"cocktail", r"\bsrpb4[13]", r"\bsrpe"], brand=["Seiko"]), dict(hubs=["/znacky/seiko/", "/seiko-presage-prospex/"], min=3, index_min=6)),
    ("seiko-automaticke-hodinky", "Seiko automatické hodinky", dict(brand=["Seiko"], feats=["automaticke"]), dict(hubs=["/znacky/seiko/", "/automaticke-hodinky/"])),
    ("citizen-tsuyosa", "Citizen Tsuyosa", dict(any=[r"tsuyosa", r"\bnj015"], brand=["Citizen"]), dict(hubs=["/znacky/citizen/"], min=3, index_min=6)),
    ("casio-duro", "Casio Duro (MDV-106)", dict(any=[r"\bduro\b", r"\bmdv.?10[67]", r"\bmdv.?107"], brand=["Casio"]), dict(hubs=["/znacky/casio/"], min=3, index_min=6)),
    ("casio-aq-230", "Casio AQ-230", dict(any=[r"\baq.?230"], brand=["Casio"]), dict(hubs=["/znacky/casio/", "/casio-vintage-hodinky/"], min=3, index_min=6)),
    ("casio-mtp-1302", "Casio MTP-1302", dict(any=[r"\bmtp.?1302"], brand=["Casio"]), dict(hubs=["/znacky/casio/"], min=3, index_min=6)),
    ("casio-illuminator", "Casio Illuminator", dict(any=[r"illuminator"], brand=["Casio"]), dict(hubs=["/znacky/casio/"], min=3, index_min=6)),
    ("casio-world-time", "Casio World Time", dict(any=[r"world ?time", r"\bae.?1200", r"\bae.?1000", r"\baw.?80\b"], brand=["Casio"]), dict(hubs=["/znacky/casio/"], min=3, index_min=6)),
    ("tissot-prx-powermatic-80", "Tissot PRX Powermatic 80", dict(any=[r"\bprx\b.*powermatic", r"powermatic.*\bprx\b", r"\bt137\.?407", r"\bt137\.?207"], brand=["Tissot"]), dict(hubs=["/znacky/tissot/", "/tissot-prx/"], min=3, index_min=6)),
    ("longines-hodinky", "Hodinky Longines", dict(brand=["Longines"]), dict(hubs=["/svycarske-hodinky/"], min=3, index_min=6)),
    ("hamilton-hodinky", "Hodinky Hamilton", dict(brand=["Hamilton"]), dict(hubs=["/svycarske-hodinky/"], min=3, index_min=6)),
    ("rado-hodinky", "Hodinky Rado", dict(brand=["Rado"]), dict(hubs=["/svycarske-hodinky/"], min=3, index_min=6)),
    ("tag-heuer-hodinky", "Hodinky TAG Heuer", dict(brand=["Tag Heuer", "TAG Heuer"]), dict(hubs=["/svycarske-hodinky/"], min=3, index_min=6)),
    ("grand-seiko", "Grand Seiko", dict(any=[r"grand seiko"]), dict(hubs=["/znacky/seiko/"], min=3, index_min=6)),
    ("diesel-hodinky", "Hodinky Diesel", dict(brand=["Diesel"]), dict(lead="Pánské hodinky Diesel: velká pouzdra, chronografy a výrazný industriální design. Porovnejte cenu stejného modelu ve více obchodech.")),
    ("guess-hodinky-damske", "Dámské hodinky Guess", dict(cat=[DAM], brand=["Guess"]), dict(parent="/damske-hodinky/", hubs=["/znacky/guess/"])),
    ("stribrne-hodinky", "Stříbrné hodinky", dict(colors=["stribrna"]), dict(lead="Hodinky ve stříbrné barvě s ocelovým pouzdrem i tahem, pánské i dámské. Porovnání cen stejného modelu.")),
    ("hodinky-s-velkym-cifernikem", "Hodinky s velkým ciferníkem", dict(any=[r"velk\w* cifern", r"\bxl\b", r"oversize"], scope="text"), dict(min=8)),
    ("outdoorove-hodinky", "Outdoorové hodinky", dict(any=[r"outdoor\w*", r"\btrek\w*", r"\bkompas\w*", r"\bvojensk\w*", r"\bfield\b"], none=[r"chytr\w*", r"smart\w*"]), dict(hubs=["/sportovni-hodinky/"], min=8)),
]

# ---- jewellery: what the 11/2026 gap showed as missing (volumes Google Ads CZ): tenisový náramek 880, pečetní prsten 480, bižuterie 2 900, krabička na šperky 880, stojan na šperky 590,
# náramky se jménem 320, řetízky se jménem 170, piercing do nosu/pupíku/ucha (nose 720, belly 590, helix 590, tragus 1 000)
J = [
    ("tenisove-naramky", "Tenisové náramky", dict(cat=["naramky"], any=[r"tenisov\w*", r"\btennis\b"]), dict(parent="/naramky/")),
    ("tenisove-nahrdelniky", "Tenisové náhrdelníky", dict(cat=["nahrdelniky", "retizky"], any=[r"tenisov\w*", r"\btennis\b"]), dict(parent="/nahrdelniky/")),
    ("pecetni-prsteny", "Pečetní prsteny", dict(cat=["prsteny"], any=[r"pecetn\w*", r"\bsignet\b"]), dict(parent="/prsteny/")),
    ("bizuterie", "Bižuterie", dict(cat=["sperky"], any=[r"bizuter\w*"], scope="text"), dict(lead="Bižuterie a módní šperky za pár stovek: náušnice, náhrdelníky, náramky a prsteny. Porovnání cen v českých e-shopech.", min=12)),
    ("bizuterie-nausnice", "Bižuterie náušnice", dict(cat=["nausnice"], any=[r"bizuter\w*"], scope="text"), dict(parent="/nausnice/")),
    ("bizuterie-nahrdelniky", "Bižuterie náhrdelníky", dict(cat=["nahrdelniky"], any=[r"bizuter\w*"], scope="text"), dict(parent="/nahrdelniky/")),
    ("naramky-se-jmenem", "Náramky se jménem", dict(cat=["naramky"], any=[r"\bjmen\w*", r"\binicial\w*", r"\bgravir\w*", r"\bpismen\w*"]), dict(parent="/naramky/")),
    ("retizky-se-jmenem", "Řetízky se jménem", dict(cat=["retizky", "nahrdelniky"], any=[r"\bjmen\w*", r"\binicial\w*", r"\bgravir\w*", r"\bpismen\w*"]), dict(parent="/retizky/")),
    ("sperkovnice-krabicky-na-sperky", "Krabičky na šperky", dict(cat=["sperkovnice"], any=[r"krabick\w*", r"\bbox\b", r"\betui\b", r"\bkazet\w*"]), dict(parent="/sperkovnice/")),
    ("sperkovnice-stojany-na-sperky", "Stojany na šperky", dict(cat=["sperkovnice"], any=[r"stojan\w*", r"stromek", r"\bvesak\w*", r"\bdrzak\w*"]), dict(parent="/sperkovnice/")),
    ("cestovni-sperkovnice", "Cestovní šperkovnice", dict(cat=["sperkovnice"], any=[r"cestovn\w*", r"\bmini\b"]), dict(parent="/sperkovnice/")),
    ("velke-sperkovnice", "Velké šperkovnice", dict(cat=["sperkovnice"], any=[r"\bvelk\w*", r"skrin\w*", r"komod\w*"]), dict(parent="/sperkovnice/")),
    ("piercing-do-nosu", "Piercing do nosu", dict(cat=["piercing"], any=[r"\bnos\w*", r"\bnostril", r"\bseptum"]), dict(parent="/piercing/")),
    ("piercing-do-pupiku", "Piercing do pupíku (belly piercing)", dict(cat=["piercing"], any=[r"\bpupik\w*", r"\bpupk\w*", r"\bbelly", r"\bnavel"]), dict(parent="/piercing/")),
    ("piercing-do-ucha", "Piercing do ucha (helix, tragus)", dict(cat=["piercing"], any=[r"\bhelix", r"\btragus", r"\bconch", r"\bdaith", r"\bucho\b", r"\buch\w*"]), dict(parent="/piercing/")),
    # ---- round 3 (Ahrefs 24. 11. 2026): Sofia / Majya / Moon Jewellery bring the gold & stone range
    ("prsteny-se-safirem", "Prsteny se safírem", dict(cat=["prsteny", "zasnubni-prsteny"], any=[r"\bsafir(?!ov\w* skl)\w*", r"\bsapphire"], scope="text"), dict(parent="/prsteny/")),
    ("prsteny-s-rubinem", "Prsteny s rubínem", dict(cat=["prsteny", "zasnubni-prsteny"], any=[r"\brubin\w*", r"\bruby\b"], scope="text"), dict(parent="/prsteny/")),
    ("prsteny-se-smaragdem", "Prsteny se smaragdem", dict(cat=["prsteny", "zasnubni-prsteny"], any=[r"\bsmaragd\w*", r"\bemerald"], scope="text"), dict(parent="/prsteny/")),
    ("prsteny-s-vltavinem", "Prsteny s vltavínem", dict(cat=["prsteny"], any=[r"\bvltavin\w*", r"\bmoldavit"]), dict(parent="/prsteny/")),
    ("prsteny-s-ametystem", "Prsteny s ametystem", dict(cat=["prsteny"], any=[r"\bametyst\w*", r"\bamethyst"]), dict(parent="/prsteny/")),
    ("prsteny-s-modrym-kamenem", "Prsteny s modrým kamenem", dict(cat=["prsteny", "zasnubni-prsteny"], any=[r"\bmodr\w* (kamen|kamin|zirkon|krystal|topaz|safir)", r"\bsafir\w*", r"\btopaz\w*", r"\btanzanit\w*", r"\bakvamarin\w*"], scope="text"), dict(parent="/prsteny/")),
    ("nausnice-s-vltavinem", "Náušnice s vltavínem", dict(cat=["nausnice"], any=[r"\bvltavin\w*", r"\bmoldavit"]), dict(parent="/nausnice/")),
    ("nausnice-s-opalem", "Náušnice s opálem", dict(cat=["nausnice"], any=[r"\bopal\w*"]), dict(parent="/nausnice/")),
    ("nahrdelniky-z-pravych-perel", "Náhrdelníky z pravých perel", dict(cat=["nahrdelniky"], any=[r"\bprav\w* perl", r"\bsladkovodn\w* perl", r"\bricn\w* perl", r"\bakoya", r"\bperl\w* (sladkovod|ricn)"], scope="text"), dict(parent="/nahrdelniky/s-perlou/")),
    ("retizky-s-privesky", "Řetízky s přívěskem", dict(cat=["retizky", "nahrdelniky"], any=[r"\b(retiz\w*|nahrdelnik\w*) s privesk\w*", r"\bs privesk\w*"]), dict(parent="/retizky/")),
    ("zlate-retizky-s-priveskem", "Zlaté řetízky s přívěskem", dict(cat=["retizky", "nahrdelniky"], mats=["zlato"], any=[r"\bs privesk\w*"]), dict(parent="/retizky/ze-zlata/")),
    ("stribrne-retizky-s-priveskem", "Stříbrné řetízky s přívěskem", dict(cat=["retizky", "nahrdelniky"], mats=["stribro"], any=[r"\bs privesk\w*"]), dict(parent="/retizky/ze-stribra/")),
    ("kozene-naramky", "Kožené náramky", dict(cat=["naramky"], any=[r"\bkozen\w*", r"\bleather"]), dict(parent="/naramky/")),
    ("panske-kozene-naramky", "Pánské kožené náramky", dict(cat=["naramky"], feats=["pro-muze"], any=[r"\bkozen\w*", r"\bleather"]), dict(parent="/naramky/panske/")),
    ("naramky-pratelstvi", "Náramky přátelství", dict(cat=["naramky"], any=[r"pratelstv\w*", r"\bfriendship", r"\bpro (nejlepsi )?kamarad\w*", r"\bbff\b"], scope="text"), dict(parent="/naramky/")),
    ("levne-snubni-prsteny", "Levné snubní prsteny", dict(cat=["snubni-prsteny"], price=[None, 2500]), dict(parent="/snubni-prsteny/", dedupe_all=True, lead="Snubní prsteny do 2 500 Kč za kus: ocel, wolfram, titan i stříbro. Cena je u většiny obchodů za jeden prsten, pár tedy vyjde na dvojnásobek.")),
    ("netradicni-snubni-prsteny", "Netradiční snubní prsteny", dict(cat=["snubni-prsteny"], any=[r"\bkarbon\w*", r"\bdrev\w*", r"\bwolfram\w*", r"\bmeteorit\w*", r"\bcern\w*", r"\bmodr\w*", r"\bkeramick\w*", r"\bnetradicn\w*", r"\boriginaln\w*"], scope="text"), dict(parent="/snubni-prsteny/")),
    ("snubni-prsteny-s-diamantem-pro-oba", "Snubní prsteny pro oba (pár)", dict(cat=["snubni-prsteny"], any=[r"\bpar\b", r"\bparov\w*", r"\bpro oba", r"\bsada"], scope="text"), dict(parent="/snubni-prsteny/")),
    ("pandora-harry-potter", "Pandora Harry Potter", dict(brand=["Pandora"], any=[r"harry potter", r"bradavic", r"hogwarts"], cat=["sperky"]), dict(hubs=["/znacky/pandora/"], min=3, index_min=6)),
    ("pandora-disney", "Pandora Disney", dict(brand=["Pandora"], any=[r"\bdisney", r"\bmickey", r"\bminnie", r"\bstitch", r"\bfrozen", r"\bmarvel", r"\bstar wars"], cat=["sperky"]), dict(hubs=["/znacky/pandora/"], min=3, index_min=6)),
    ("pandora-moments-naramky", "Pandora Moments náramky na přívěsky", dict(brand=["Pandora"], cat=["naramky"], any=[r"\bmoments\b", r"\bhad\w*", r"\bsnake"]), dict(parent="/naramky/pandora/")),
    ("piercing-do-oboci", "Piercing do obočí", dict(cat=["piercing"], any=[r"\boboc\w*", r"\beyebrow"]), dict(parent="/piercing/")),
    ("piercing-do-rtu", "Piercing do rtu (labret)", dict(cat=["piercing"], any=[r"\bret\b", r"\brtu\b", r"\blabret", r"\blip\b"]), dict(parent="/piercing/")),
]


def main():
    pages = []
    for slug, h1, rules, o in T + J:
        rules = dict(rules)
        if "cat" not in rules:
            rules["cat"] = [W]                   # a hub without a category is watches only: the room "hodinky" (jewellery has the same brands and words)
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
