#!/usr/bin/env python3
"""
Controleer de gegenereerde viewerdata vóór een sitebuild (review 2026-10-05).

De Cloudflare-build draait alleen scripts/build_site.py op de gecommitte data;
build_base_dataset.py en analyse_spatial.py draaien daar niet. Deze controle
zorgt dat inconsistente data niet gedeployd wordt: build_site.py roept
check() aan en stopt bij een fout.

Alleen stdlib (draait in de Cloudflare-build).

Controles
  - begraafplaatsen.geojson: unieke kenmerken, geldige status, coördinaten in
    Nederland, tellingen per provincie = data/invarianten.json
  - terreinen.geojson: elk terrein hoort bij een bestaande begraafplaats
    (in gebruik of geruimd) en heeft hetzelfde aantal als de invarianten
  - herbegravingen.geojson: beide kanten bestaan
  - leeslijst.json: popup_ids bestaan
  - statistieken.json: zelfde totaal en provincies als de punten

Gebruik:  python scripts/check_data.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GEN = REPO_ROOT / "data" / "generated"
STATUSSEN = ("in_gebruik", "geruimd", "verdwenen")
NL_BBOX = (3.2, 50.7, 7.3, 53.7)  # lon_min, lat_min, lon_max, lat_max


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check() -> list[str]:
    fouten: list[str] = []
    inv = load(REPO_ROOT / "data" / "invarianten.json")["provincies"]
    punten = [f["properties"] | {"_geom": f["geometry"]} for f in load(GEN / "begraafplaatsen.geojson")["features"]]
    by_id = {p["id"]: p for p in punten}

    dubbel = [i for i, n in Counter(p["id"] for p in punten).items() if n > 1]
    if dubbel:
        fouten.append(f"dubbele kenmerken: {dubbel}")
    for p in punten:
        if p["status"] not in STATUSSEN:
            fouten.append(f"{p['id']}: onbekende status {p['status']!r}")
        lon, lat = p["_geom"]["coordinates"]
        if not (NL_BBOX[0] <= lon <= NL_BBOX[2] and NL_BBOX[1] <= lat <= NL_BBOX[3]) or math.isnan(lon) or math.isnan(lat):
            fouten.append(f"{p['id']}: coördinaat buiten Nederland ({lon}, {lat})")
        if p["status"] == "verdwenen" and p.get("terrein_naam_kml"):
            fouten.append(f"{p['id']}: verdwenen begraafplaats met terrein")

    terreinen = load(GEN / "terreinen.geojson")["features"]
    t_ids = Counter(t["properties"]["id"] for t in terreinen)
    for i, n in t_ids.items():
        if i not in by_id:
            fouten.append(f"terrein voor onbekend kenmerk {i}")
        elif by_id[i]["status"] == "verdwenen":
            fouten.append(f"terrein voor verdwenen begraafplaats {i}")
        if n > 1:
            fouten.append(f"{i}: {n} terreinen")

    provs = sorted({p["provincie"] for p in punten})
    for prov in provs:
        verwacht = inv.get(prov)
        if verwacht is None:
            fouten.append(f"{prov}: geen invariant in data/invarianten.json")
            continue
        recs = [p for p in punten if p["provincie"] == prov]
        werkelijk = {
            "totaal": len(recs),
            **{s: sum(1 for p in recs if p["status"] == s) for s in STATUSSEN},
            "terreinen": sum(1 for p in recs if p["id"] in t_ids),
        }
        verwacht = {k: v for k, v in verwacht.items() if k != "toelichting"}
        if werkelijk != verwacht:
            fouten.append(f"{prov}: verwacht {verwacht}, gevonden {werkelijk}")

    for lijn in load(GEN / "herbegravingen.geojson")["features"]:
        for kant in ("van_id", "naar_id"):
            if lijn["properties"][kant] not in by_id:
                fouten.append(f"herbegraving: onbekend {kant} {lijn['properties'][kant]}")

    for a in load(GEN / "leeslijst.json")["artikelen"]:
        for i in a.get("popup_ids", []):
            if i not in by_id:
                fouten.append(f"leeslijst: onbekend kenmerk {i} bij {a['titel']!r}")

    stats = load(GEN / "statistieken.json")
    if stats["basis"]["totaal"] != len(punten):
        fouten.append(f"statistieken: totaal {stats['basis']['totaal']} != {len(punten)} begraafplaatsen (draai compute_statistics.py)")
    if sorted(stats["provincies_op_kaart"]) != provs:
        fouten.append("statistieken: andere provincies dan de punten (draai compute_statistics.py)")
    return fouten


def main() -> None:
    fouten = check()
    if fouten:
        print("Datacontrole MISLUKT:", *fouten, sep="\n  - ")
        sys.exit(1)
    print("Datacontrole: in orde")


if __name__ == "__main__":
    main()
