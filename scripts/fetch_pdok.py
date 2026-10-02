#!/usr/bin/env python3
"""
Haal provincie- en gemeentegrenzen (heel Nederland) op bij PDOK.

Bron: PDOK "bestuurlijkegebieden" WFS (Kadaster), lagen Provinciegebied en
Gemeentegebied. Alles wordt landelijk opgehaald (CQL_FILTER werkte niet
betrouwbaar in het dodenakkers-project); filteren gebeurt client-side.

De grenzen dienen twee doelen:
  1. analyse: in welke provincie/gemeente ligt een begraafplaats echt
     (de Excel kan verouderd zijn na herindelingen);
  2. contextlaag in de viewer.
Daarom vereenvoudigd (Douglas-Peucker, 0.00005 graad ~ 4-5 m) en afgerond op
6 decimalen: ruim nauwkeurig genoeg voor punt-in-gemeente en voor weergave,
en klein genoeg voor Cloudflare Pages (max 25 MB per bestand).

Output:
  data/pdok/provincies.geojson  + metadata/provincies.json
  data/pdok/gemeenten.geojson   + metadata/gemeenten.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from shapely.geometry import mapping, shape

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "pdok"
METADATA_DIR = OUTPUT_DIR / "metadata"

ENDPOINT = "https://service.pdok.nl/kadaster/bestuurlijkegebieden/wfs/v1_0"
SIMPLIFY_DEG = 0.00005
DECIMALS = 6

LAGEN = {
    "provincies": ("bestuurlijkegebieden:Provinciegebied", 12, ["naam", "code"]),
    "gemeenten": ("bestuurlijkegebieden:Gemeentegebied", None, ["naam", "code", "ligtInProvincieNaam"]),
}


def round_coords(coords):
    if coords and isinstance(coords[0], (int, float)):
        return [round(c, DECIMALS) for c in coords]
    return [round_coords(c) for c in coords]


def fetch_layer(type_name: str) -> list[dict]:
    resp = requests.get(
        ENDPOINT,
        params={
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": type_name,
            "outputFormat": "application/json",
            "srsName": "EPSG:4326",
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["features"]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, (type_name, expected, keep) in LAGEN.items():
        raw = fetch_layer(type_name)
        if expected is not None:
            assert len(raw) == expected, f"{name}: verwacht {expected}, gevonden {len(raw)}"
        features = []
        for f in raw:
            geom = shape(f["geometry"]).simplify(SIMPLIFY_DEG, preserve_topology=True)
            gj = mapping(geom)
            gj = {"type": gj["type"], "coordinates": round_coords(gj["coordinates"])}
            props = {k: f["properties"].get(k) for k in keep}
            features.append({"type": "Feature", "properties": props, "geometry": gj})
        fc = {"type": "FeatureCollection", "name": name, "features": features}
        path = OUTPUT_DIR / f"{name}.geojson"
        path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        metadata = {
            "source": "PDOK bestuurlijkegebieden WFS (Kadaster)",
            "endpoint": ENDPOINT,
            "layer": type_name,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "feature_count": len(features),
            "bewerking": f"vereenvoudigd {SIMPLIFY_DEG} graad, afgerond op {DECIMALS} decimalen",
        }
        (METADATA_DIR / f"{name}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{name}: {len(features)} features -> {path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
