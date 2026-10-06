#!/usr/bin/env python3
"""
Koppel oude kaarten uit Allmaps (https://allmaps.org) aan de begraafplaatsen:
welke gegeorefereerde historische kaarten liggen over elke begraafplaats?

Bron: de open dump van alle Allmaps-kaarten (https://files.allmaps.org/
maps.geojsonl, CC0, twee keer per dag ververst). Per kaart staat daarin de
omtrek (GeoJSON) en de IIIF-bron. Het kaartbeeld zelf blijft bij de instelling
en wordt in de viewer (src/oude-kaarten.html) via de Allmaps Tile Server
(allmaps.xyz) getoond.

Selectie, zodat er alleen bruikbare kaarten bij een begraafplaats staan:
  - de omtrek bevat het punt van de begraafplaats;
  - detailkaart: omtrek kleiner dan MAX_KM2 (geen overzichtskaarten van
    Nederland of Europa);
  - herkenbare titel (geen "Canvas 3", "Image", lege labels);
  - alleen collecties van bekende instellingen (COLLECTIES, HOSTS);
  - per scan (IIIF-image) een keer: bij meerdere georeferenties de nieuwste.

Jaartal: bij de Bonnebladen (TU Delft) uit de bestandsnaam van de scan
(b169-1912_scan.tif), via data/allmaps/bonnebladen_jaren.csv. Die tabel komt
uit de ingest-lijst van TU Delft Library (Observable-notebook van Jules
Schoonman, gespiegeld in github.com/ahhutama/download_bonnebladen); ververs
met --vernieuw-jaren. Bij andere kaarten: een jaartal in de titel, anders leeg.

Output: data/generated/oude_kaarten.json
  kaarten:            {map-id: {titel, collectie, jaar}}
  per_begraafplaats:  {jb-id: [map-id, ...]}  (Bonnebladen eerst, dan op jaar)

Gebruik
  python scripts/fetch_allmaps.py                    # dump downloaden
  python scripts/fetch_allmaps.py --dump maps.geojsonl
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import math
import re
from pathlib import Path

import requests
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
PUNTEN = REPO_ROOT / "data" / "generated" / "joodse-begraafplaatsen.geojson"
JAREN = REPO_ROOT / "data" / "allmaps" / "bonnebladen_jaren.csv"
OUT = REPO_ROOT / "data" / "generated" / "oude_kaarten.json"

DUMP_URL = "https://files.allmaps.org/maps.geojsonl"
JAREN_URL = "https://raw.githubusercontent.com/ahhutama/download_bonnebladen/main/ingest-collection-min@1.json"

# Nederland ruim (lon/lat); kaarten daarbuiten worden niet eens ingelezen.
NL = (3.2, 50.7, 7.3, 53.6)
# Bonneblad ~ 62 km2, Waterstaatskaart-blad 250-500 km2; provinciekaarten
# (850+ km2) zijn te grof om een begraafplaats op te zien.
MAX_KM2 = 600
# Alleen collecties van bekende instellingen. Iedereen kan in Allmaps
# georefereren; daardoor staan er ook testkaarten en verkeerd geplaatste
# kaarten in (bv. een Amerikaanse verzekeringskaart boven Assen).
COLLECTIES = {
    "TU Delft Library", "Universiteitsbibliotheek Utrecht", "Universiteitsbibliotheek VU",
    "Universiteitsbibliotheek van Amsterdam", "Universitaire Bibliotheken Leiden", "Nationaal Archief",
    "4TU.ResearchData", "University of Groningen", "Stadsarchief Amsterdam", "Gouda Tijdmachine",
    "Rotterdams Publiek", "Erfgoed Leiden en Omstreken", "Wageningen University & Research",
    "Library of Congress", "David Rumsey Map Collection", "Harvard Library Digital Collections",
    "Stanford Libraries", "Yale University Library", "Bibliothèque nationale de France",
}
# Instellingen zonder provider-label in de IIIF-bron: herkend aan de host.
HOSTS = {
    "proxy.archieven.nl": "Stadsarchief Rotterdam",
    "preserve-iiif.archieven.nl": "Stadsarchief Rotterdam",
    "iiif.tresoar.nl": "Tresoar",
    "facsimile.ub.rug.nl": "University of Groningen",
}
GENERIEK = re.compile(r"^(canvas \d+|image|\d+|my manifest|generated from .*|iiif manifest.*|.*zonder metadata.*|\?)$", re.I)
# Bonnebladen-scan: https://dlc.services/iiif-img/[v3/]7/4/<hash>
BONNE = re.compile(r"dlc\.services/iiif-img/(?:v3/)?7/4/([0-9a-f]{32})$")


def label(v) -> str:
    """IIIF-label ({"nl": ["..."]}) naar tekst; soms is het label zelf JSON-tekst."""
    if isinstance(v, dict):
        v = next(iter(v.values()), [""])
        v = v[0] if v else ""
    v = str(v or "").strip()
    if v.startswith("{"):
        try:
            return label(json.loads(v))
        except ValueError:
            pass
    v = re.sub(r"\s+", " ", v).strip(" /")
    # catalogusnummers en vulteksten (UB Utrecht, BnF): "KAART: *VII*...",
    # "*VII*.B.a.795 (Dk36-14)", "Page Info:", "NP", "-"
    v = re.sub(r"\s*KAART: \*.*$", "", v)
    v = re.sub(r"\s*\*[IVX]+\*\S*(\s*\([^)]*\))?", "", v)
    v = re.sub(r"^(page info:?|np|-)$", "", v, flags=re.I)
    v = v.replace("Waterstaatskaart van Nederland : op de schaal van 1:50.000", "Waterstaatskaart van Nederland")
    v = v.replace("NL-HaNA 4.TOPO Topografische Dienst en Rechtsvoorgangers: A6.1 TMK: veldminuten", "TMK, veldminuut")
    return v.strip(" :")


def bruikbaar(t: str) -> bool:
    return bool(t) and not GENERIEK.match(t)


def titel_van(resource: dict) -> tuple[str, str]:
    """(serie, blad) uit canvas- en manifestlabels."""
    serie = blad = ""
    for canvas in resource.get("partOf") or []:
        c = label(canvas.get("label"))
        if bruikbaar(c) and not blad:
            blad = c
        for man in canvas.get("partOf") or []:
            m = label(man.get("label"))
            mid = man.get("id", "")
            if "river-map" in mid and bruikbaar(m):
                m = f"Rivierkaart, {m[0].lower()}{m[1:]}"
            if "luchtfotos-kadaster" in mid:
                m = "Luchtfoto Kadaster"
            if bruikbaar(m) and not serie:
                serie = m
    return serie, blad


def collectie_van(resource: dict) -> str | None:
    """Naam van de instelling, of None als die niet in de lijst staat."""
    prov = resource.get("provider") or []
    t = label(prov[0].get("label")) if prov else ""
    if t in COLLECTIES:
        return t
    return HOSTS.get(re.sub(r"^https?://([^/]+).*", r"\1", resource["id"]))


def km2(g) -> float:
    lat = g.centroid.y
    return g.area * 111.32 ** 2 * math.cos(math.radians(lat))


def jaar_uit(t: str) -> int | None:
    m = re.findall(r"\b(1[5-9]\d\d)\b", t)
    return int(m[0]) if m else None


def bonnebladen_jaren(vernieuw: bool) -> dict[str, tuple[str, int]]:
    if vernieuw or not JAREN.exists():
        rijen = []
        for x in requests.get(JAREN_URL, timeout=60).json():
            m = re.match(r"b(\d{3})([a-z]?)-(\d{4})", x["filename"])
            if m:
                rijen.append({"image": x["id"], "blad": str(int(m[1])) + m[2], "jaar": m[3]})
        JAREN.parent.mkdir(parents=True, exist_ok=True)
        with JAREN.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, ["image", "blad", "jaar"], lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(rijen, key=lambda r: (r["image"])))
        print(f"{JAREN.relative_to(REPO_ROOT)}: {len(rijen)} scans")
    with JAREN.open(encoding="utf-8", newline="") as f:
        return {r["image"]: (r["blad"], int(r["jaar"])) for r in csv.DictReader(f)}


def regels(dump: str | None):
    if dump:
        with open(dump, encoding="utf-8") as f:
            yield from f
        return
    with requests.get(DUMP_URL, stream=True, timeout=600) as r:
        r.raise_for_status()
        yield from io.TextIOWrapper(r.raw, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", help="lokale kopie van maps.geojsonl")
    ap.add_argument("--vernieuw-jaren", action="store_true")
    args = ap.parse_args()

    jaren = bonnebladen_jaren(args.vernieuw_jaren)
    punten = [f["properties"] for f in json.loads(PUNTEN.read_text(encoding="utf-8"))["features"]]

    # Per scan alleen de nieuwste georeferentie.
    per_scan: dict[str, dict] = {}
    for regel in regels(args.dump):
        f = json.loads(regel)
        try:
            g = shape(f["geometry"])
        except Exception:
            continue
        x0, y0, x1, y1 = g.bounds
        if x1 < NL[0] or x0 > NL[2] or y1 < NL[1] or y0 > NL[3]:
            continue
        if not g.is_valid:
            g = g.buffer(0)
        if g.is_empty:
            continue
        p = f["properties"]
        res = p["resource"]
        collectie = collectie_van(res)
        if not collectie or km2(g) > MAX_KM2:
            continue
        serie, blad = titel_van(res)
        bonne = BONNE.search(res["id"])
        jaar = None
        if bonne and bonne.group(1) in jaren:
            nr, jaar = jaren[bonne.group(1)]
            m = re.match(r"Blad \d+\w?: (.*)", blad)
            titel = f"Bonneblad {nr} {m.group(1).title() if m else ''}".strip()
        else:
            if serie and blad and serie not in blad and blad not in serie:
                titel = f"{serie}: {blad}"
            else:
                titel = max(serie, blad, key=len)
            jaar = jaar_uit(titel)
        if not bruikbaar(titel):
            continue
        oud = per_scan.get(res["id"])
        if oud and oud["modified"] >= p.get("modified", ""):
            continue
        per_scan[res["id"]] = {
            "map": p["id"].rsplit("/", 1)[-1],
            "geom": g,
            "modified": p.get("modified", ""),
            "titel": titel,
            "collectie": collectie,
            "jaar": jaar,
            "bonne": bool(bonne),
        }

    kaarten = list(per_scan.values())
    tree = STRtree([k["geom"] for k in kaarten])
    per_bp: dict[str, list[str]] = {}
    gebruikt: dict[str, dict] = {}
    for bp in punten:
        pt = Point(bp["lon"], bp["lat"])
        hits = [kaarten[i] for i in tree.query(pt) if kaarten[i]["geom"].contains(pt)]
        hits.sort(key=lambda k: (not k["bonne"], k["jaar"] or 9999, k["titel"]))
        if hits:
            per_bp[bp["id"]] = [k["map"] for k in hits]
            for k in hits:
                gebruikt[k["map"]] = {"titel": k["titel"], "collectie": k["collectie"], "jaar": k["jaar"]}

    out = {
        "gegenereerd": datetime.date.today().isoformat(),
        "bron": "Allmaps (https://allmaps.org), georeferenties CC0; kaartbeelden van de genoemde collecties",
        "kaarten": dict(sorted(gebruikt.items())),
        "per_begraafplaats": dict(sorted(per_bp.items())),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    zonder = [bp["id"] for bp in punten if bp["id"] not in per_bp]
    print(f"{OUT.relative_to(REPO_ROOT)}: {len(per_bp)}/{len(punten)} begraafplaatsen, {len(gebruikt)} kaarten"
          + (f"; zonder: {', '.join(zonder)}" if zonder else ""))


if __name__ == "__main__":
    main()
