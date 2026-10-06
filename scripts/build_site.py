#!/usr/bin/env python3
"""
Stel de statische site samen in site/ (gitignored) voor Cloudflare Pages.

src/ wordt 1-op-1 gekopieerd (alle paden in src/ zijn al relatief aan de
site-root: data/..., images/..., vendor/...), plus de data die de viewer
gebruikt en _headers. Geen herschrijfstap nodig, anders dan in dodenakkers.

Lokaal bekijken:  python scripts/build_site.py && python -m http.server -d site 8000
Deploy:           npx wrangler deploy   (Worker met static assets, zie wrangler.jsonc)
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
MAX_BESTAND = 25 * 1024 * 1024  # Cloudflare-limiet per bestand

# Productiedomein, op EEN plek: canonical, og:url, robots.txt en sitemap.xml
# gebruiken {{SITE_URL}}. Bij een eigen domein (bv. kaart.dodenakkers.nl)
# alleen hier aanpassen.
SITE_URL = "https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev"

# Publicatie (bij het boek): op True zetten. Dan bouwt de site ZONDER noindex
# (meta robots in de html, X-Robots-Tag in _headers) en MET de Sitemap-regel in
# robots.txt. Zolang de kaart intern is (vraag F4): False.
PUBLICEREN = False
HTML_PAGINAS = ["index.html", "methode.html", "lezen.html", "statistieken.html", "oude-kaarten.html", "404.html"]
TEMPLATED = ["index.html", "methode.html", "lezen.html", "statistieken.html", "oude-kaarten.html", "robots.txt", "sitemap.xml"]

DATA_FILES = [
    "data/generated/begraafplaatsen.geojson",
    "data/generated/terreinen.geojson",
    "data/generated/herbegravingen.geojson",
    "data/generated/leeslijst.json",
    "data/generated/statistieken.json",
    "data/generated/oude_kaarten.json",
    "data/pdok/provincies.geojson",
    "data/pdok/gemeenten.geojson",
    "data/rce/index.json",
]


def main() -> None:
    # Eerst de gegenereerde data controleren: bij een fout niet bouwen (en dus
    # in de Cloudflare-build ook niet deployen).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_data import check
    fouten = check()
    if fouten:
        sys.exit("Datacontrole mislukt, site niet gebouwd:\n  - " + "\n  - ".join(fouten))
    print("Datacontrole: in orde")

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    shutil.copytree(REPO_ROOT / "src", SITE_DIR)
    manifest = json.loads((REPO_ROOT / "data/rce/index.json").read_text(encoding="utf-8"))["provincies"]
    rce_files = [f for bestanden in manifest.values() for f in bestanden.values()]
    for rel in DATA_FILES + rce_files:
        dst = SITE_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dst)
    shutil.copyfile(REPO_ROOT / "_headers", SITE_DIR / "_headers")

    # Vervallen kenmerken -> nieuw kenmerk, voor ?id= op de kaart en voor de
    # pagina's per begraafplaats (data/kenmerken.json; links blijven werken).
    register = json.loads((REPO_ROOT / "data/kenmerken.json").read_text(encoding="utf-8"))
    doorverwijzingen = {k: v.get("naar") for k, v in register["vervallen"].items()}
    (SITE_DIR / "data/doorverwijzingen.json").write_text(json.dumps(doorverwijzingen, ensure_ascii=False), encoding="utf-8")

    for rel in TEMPLATED:
        f = SITE_DIR / rel
        text = f.read_text(encoding="utf-8")
        assert "{{SITE_URL}}" in text, f"{rel}: geen {{{{SITE_URL}}}} gevonden"
        f.write_text(text.replace("{{SITE_URL}}", SITE_URL), encoding="utf-8")

    if PUBLICEREN:
        for rel in HTML_PAGINAS:
            f = SITE_DIR / rel
            regels = f.read_text(encoding="utf-8").splitlines(keepends=True)
            regels = [r for r in regels if 'name="robots"' not in r and "Niet indexeren:" not in r]
            f.write_text("".join(regels), encoding="utf-8")
        h = SITE_DIR / "_headers"
        h.write_text("".join(r for r in h.read_text(encoding="utf-8").splitlines(keepends=True) if "X-Robots-Tag" not in r), encoding="utf-8")
        r = SITE_DIR / "robots.txt"
        r.write_text(r.read_text(encoding="utf-8").replace("#   Sitemap: ", "Sitemap: "), encoding="utf-8")
    # Een pagina per begraafplaats (scripts/paginas.py), met dezelfde
    # noindex-keuze; in de sitemap voor als de kaart gepubliceerd wordt.
    from paginas import bouw as bouw_paginas
    paden = bouw_paginas(REPO_ROOT, SITE_DIR, SITE_URL, noindex=not PUBLICEREN)
    sitemap = SITE_DIR / "sitemap.xml"
    regels = "".join(f"  <url><loc>{SITE_URL}/{pad}</loc></url>\n" for pad in paden)
    sitemap.write_text(sitemap.read_text(encoding="utf-8").replace("</urlset>", regels + "</urlset>"), encoding="utf-8")
    print(f"Pagina's per begraafplaats: {len(paden)}")

    # Controle: alle html, _headers en robots.txt moeten bij elkaar passen.
    alle_html = sorted(p.relative_to(SITE_DIR).as_posix() for p in SITE_DIR.rglob("*.html") if "vendor" not in p.parts)
    noindex = [rel for rel in alle_html if 'name="robots"' in (SITE_DIR / rel).read_text(encoding="utf-8")]
    kop = "X-Robots-Tag" in (SITE_DIR / "_headers").read_text(encoding="utf-8")
    if PUBLICEREN:
        assert not noindex and not kop, f"publiceren, maar nog noindex in {noindex or '_headers'}"
    else:
        assert len(noindex) == len(alle_html) and kop, f"intern, maar noindex ontbreekt in {sorted(set(alle_html) - set(noindex))}"
    print("Zoekmachines:", "toegestaan (gepubliceerd)" if PUBLICEREN else f"geweerd (noindex op {len(alle_html)} pagina's, intern)")

    # MapLibre verwijst naar een source map die we niet meeleveren (geeft een
    # 404 in de ontwikkelaarstools); die verwijzing weghalen.
    js = SITE_DIR / "vendor/maplibre-gl/maplibre-gl.js"
    js.write_text(re.sub(r"\n//# sourceMappingURL=\S+\s*$", "\n", js.read_text(encoding="utf-8")), encoding="utf-8")

    files = [f for f in SITE_DIR.rglob("*") if f.is_file()]
    te_groot = [f for f in files if f.stat().st_size > MAX_BESTAND]
    assert not te_groot, f"bestand(en) boven 25 MB: {te_groot}"
    total = sum(f.stat().st_size for f in files)
    print(f"site/ klaar: {len(files)} bestanden, {total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
