#!/usr/bin/env python3
"""
Haal RCE-contextlagen op (RCE CHO Linked Data) voor de gekozen provincie(s):

  - beschermde stads- en dorpsgezichten   (landelijk opgehaald, lokaal gefilterd)
  - rijksmonumenten (gebouwd)             (serverside bbox-filter op WKT-string)
  - archeologische rijksmonumenten        (idem)
  - Rmon-opzoeking: de Rmon-nummers uit de Excel (via
    data/generated/joodse-begraafplaatsen.geojson) als rijksmonument- of
    complexnummer -> data/rce/rmon-lookup.json

Queries en aanpak zijn overgenomen uit het dodenakkers-project (zie de
toelichting in queries/rce/*.sparql): geen geof:sfWithin (timeouts op
Virtuoso), labels buiten GRAPH, polygoon wint van punt per CHO.

Archeologische onderzoeksgebieden worden bewust NIET opgehaald (besluit
opdrachtgever 2026-10-02).

Na ophalen wordt alles geknipt op de echte provinciegrens (+ BUFFER_M), want
een bbox bevat ook stukken buurprovincie / België / Duitsland.

Output: data/rce/<naam>.geojson + data/rce/metadata/<naam>.json

Gebruik
  python scripts/fetch_rce.py                       # Zuid-Holland
  python scripts/fetch_rce.py --provincie Utrecht
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from pyproj import Transformer
from shapely import wkt as shapely_wkt
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

ENDPOINT = "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql"
REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_DIR = REPO_ROOT / "queries" / "rce"
OUTPUT_DIR = REPO_ROOT / "data" / "rce"
METADATA_DIR = OUTPUT_DIR / "metadata"
PDOK_DIR = REPO_ROOT / "data" / "pdok"

BUFFER_M = 1000
BBOX_MARGE_DEG = 0.02
ARCHEOLOGISCH_AARD = "https://data.cultureelerfgoed.nl/term/id/rn/2/b673c8c1-5d93-496d-8f9e-89133d579d77"

QUERY_BLOCK_RE = re.compile(r"# --- QUERY: (?P<name>[a-z]+) ---\n(?P<body>.*?)(?=\n# --- QUERY:|\Z)", re.DOTALL)
FUNCTIE_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform
to_wgs = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True).transform


def split_queries(sparql_text: str) -> dict[str, str]:
    blocks = {m.group("name"): m.group("body").strip() for m in QUERY_BLOCK_RE.finditer(sparql_text)}
    return blocks or {"default": sparql_text.strip()}


def fill_bbox(query: str, bbox: dict) -> str:
    # Geen str.format: SPARQL zit vol accolades.
    for k, v in bbox.items():
        query = query.replace("{" + k + "}", f"{v:.4f}")
    assert "{MIN_" not in query and "{MAX_" not in query
    return query


def run_query(sparql_query: str, pogingen: int = 3) -> list[dict]:
    for poging in range(1, pogingen + 1):
        try:
            resp = requests.post(
                ENDPOINT,
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=300,
            )
            resp.raise_for_status()
            return [{k: v["value"] for k, v in b.items()} for b in resp.json()["results"]["bindings"]]
        except (requests.RequestException, ValueError) as exc:
            if poging == pogingen:
                raise
            print(f"  poging {poging} mislukt ({exc}); opnieuw over {10 * poging}s")
            time.sleep(10 * poging)
    return []


def strip_functie_suffix(label: str | None) -> str | None:
    if not label:
        return label
    return FUNCTIE_SUFFIX_RE.sub("", label).strip() or label


def gebied(provincies: list[str]):
    feats = json.loads((PDOK_DIR / "provincies.geojson").read_text(encoding="utf-8"))["features"]
    geoms = [shape(f["geometry"]) for f in feats if f["properties"]["naam"] in provincies]
    assert len(geoms) == len(provincies), f"provincie(s) niet gevonden in PDOK: {provincies}"
    wgs = unary_union(geoms)
    clip = transform(to_wgs, transform(to_rd, wgs).buffer(BUFFER_M))
    minx, miny, maxx, maxy = wgs.bounds
    bbox = {
        "MIN_LON": minx - BBOX_MARGE_DEG,
        "MAX_LON": maxx + BBOX_MARGE_DEG,
        "MIN_LAT": miny - BBOX_MARGE_DEG,
        "MAX_LAT": maxy + BBOX_MARGE_DEG,
    }
    return clip, bbox


def build_gezichten(clip) -> tuple[dict, dict]:
    rows = run_query(split_queries((QUERIES_DIR / "beschermde-gezichten.sparql").read_text(encoding="utf-8"))["default"])
    features, buiten = [], 0
    for row in rows:
        geom = shapely_wkt.loads(row["wkt"])
        if not geom.intersects(clip):
            buiten += 1
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "gezicht_uri": row["gezicht"],
                    "gezichtsnummer": row.get("gezichtsnummer"),
                    "naam": row.get("naam"),
                },
                "geometry": mapping(geom),
            }
        )
    return (
        {"type": "FeatureCollection", "name": "beschermde_gezichten", "features": features},
        {"rows_from_endpoint": len(rows), "features_in_gebied": len(features), "buiten_gebied": buiten},
    )


def build_rijksmonumenten(query_file: Path, bbox: dict, clip, feature_name: str) -> tuple[dict, dict]:
    blocks = split_queries(query_file.read_text(encoding="utf-8"))
    point_rows = run_query(fill_bbox(blocks["points"], bbox))
    polygon_rows = run_query(fill_bbox(blocks["polygons"], bbox))

    by_cho: dict[str, dict] = {}
    for row in point_rows:
        by_cho.setdefault(row["cho"], {"row": row, "geometry_type": "Point", "wkt": row["wkt"]})
    for row in polygon_rows:
        by_cho[row["cho"]] = {"row": row, "geometry_type": "Polygon", "wkt": row["wkt"]}  # polygoon wint

    features, buiten = [], 0
    for cho, entry in by_cho.items():
        geom = shapely_wkt.loads(entry["wkt"])
        if not geom.intersects(clip):
            buiten += 1
            continue
        row = entry["row"]
        nr = row.get("rijksmonumentnummer")
        aard = row.get("aard")
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "cho_uri": cho,
                    "rijksmonumentnummer": nr,
                    "naam": row.get("naam"),
                    "geometry_bron": entry["geometry_type"],
                    "monumentenregister_url": f"https://monumentenregister.cultureelerfgoed.nl/monumenten/{nr}" if nr else None,
                    "oorspronkelijke_functie": row.get("oorspronkelijkeFunctie"),
                    "oorspronkelijke_functie_kort": strip_functie_suffix(row.get("oorspronkelijkeFunctie")),
                    "huidige_functie": row.get("huidigeFunctie"),
                    "type": row.get("type"),
                    "datum_inschrijving_monumentenregister": row.get("datumInschrijving"),
                    "monument_aard": (
                        "archeologisch" if aard == ARCHEOLOGISCH_AARD else "onroerend gebouwd" if aard else None
                    ),
                },
                "geometry": mapping(geom),
            }
        )
    stats = {
        "point_rows_from_endpoint": len(point_rows),
        "polygon_rows_from_endpoint": len(polygon_rows),
        "distinct_cho": len(by_cho),
        "buiten_gebied": buiten,
        "features": len(features),
    }
    return {"type": "FeatureCollection", "name": feature_name, "features": features}, stats


def write_extract(name: str, fc: dict, query_file: Path, stats: dict, provincies: list[str], bbox: dict, notes: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.geojson"
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    metadata = {
        "source": "RCE Linked Data Voorziening (CHO)",
        "endpoint": ENDPOINT,
        "query_file": str(query_file.relative_to(REPO_ROOT)).replace("\\", "/"),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "provincies": provincies,
        "bbox_wgs84": {k: round(v, 4) for k, v in bbox.items()},
        "clip": f"provinciegrens PDOK + {BUFFER_M} m",
        "feature_count": len(fc["features"]),
        "stats": stats,
        "notes": notes,
    }
    (METADATA_DIR / f"{name}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{name}: {len(fc['features'])} features ({path.stat().st_size / 1e6:.1f} MB)  {stats}")


def build_rmon_lookup() -> dict:
    punten = json.loads((REPO_ROOT / "data" / "generated" / "joodse-begraafplaatsen.geojson").read_text(encoding="utf-8"))
    nummers = sorted({str(f["properties"]["rijksmonumentnummer"]) for f in punten["features"]
                      if f["properties"].get("rijksmonumentnummer")})
    query = (QUERIES_DIR / "rmon-lookup.sparql").read_text(encoding="utf-8")
    query = query.replace("{NUMMERS}", " ".join(f'"{n}"' for n in nummers))
    lookup: dict[str, dict] = {}
    for row in run_query(query):
        e = lookup.setdefault(row["nummer"], {"soort": row["soort"], "uri": row["object"], "naam": None,
                                              "onderdelen": set(), "hoofdobject": None})
        if row["soort"] == "complex" and e["soort"] != "complex":
            # zelfde nummer als monument en complex: komt niet voor, maar dan niet stil kiezen
            e["ook_complex"] = row["object"]
        e["naam"] = e["naam"] or row.get("naam")
        if row.get("onderdeelNummer"):
            e["onderdelen"].add(row["onderdeelNummer"])
        if row.get("hoofdobjectNummer"):
            e["hoofdobject"] = row["hoofdobjectNummer"]
    for e in lookup.values():
        e["onderdelen"] = sorted(e["onderdelen"], key=int)
    out = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "gezocht": nummers,
           "niet_gevonden": [n for n in nummers if n not in lookup], "nummers": lookup}
    (OUTPUT_DIR / "rmon-lookup.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    soorten = {s: sum(1 for e in lookup.values() if e["soort"] == s) for s in ("rijksmonument", "complex")}
    print(f"rmon-lookup: {len(nummers)} nummers, {soorten}, niet gevonden: {out['niet_gevonden']}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provincie", action="append", help="herhaalbaar; standaard Zuid-Holland")
    provincies = ap.parse_args().provincie or ["Zuid-Holland"]
    clip, bbox = gebied(provincies)

    fc, stats = build_gezichten(clip)
    write_extract("beschermde-gezichten", fc, QUERIES_DIR / "beschermde-gezichten.sparql", stats, provincies, bbox,
                  "Rijksbeschermde stads- en dorpsgezichten; landelijk opgehaald, geknipt op provinciegrens.")

    q = QUERIES_DIR / "rijksmonumenten.sparql"
    fc, stats = build_rijksmonumenten(q, bbox, clip, "rijksmonumenten")
    # De gebouwd-laag bevat geen archeologische monumenten (die hebben een eigen extract).
    zonder_aard = sum(1 for f in fc["features"] if f["properties"]["monument_aard"] is None)
    fc["features"] = [f for f in fc["features"] if f["properties"]["monument_aard"] != "archeologisch"]
    stats["na_uitsluiten_archeologisch"] = len(fc["features"])
    stats["zonder_monument_aard"] = zonder_aard
    write_extract("rijksmonumenten", fc, q, stats, provincies, bbox,
                  "Rijksmonumenten (juridische status rijksmonument) exclusief monumentaard archeologisch. "
                  "Monumenten zonder monumentaard blijven in deze laag (aantal in stats).")

    q = QUERIES_DIR / "archeologische-rijksmonumenten.sparql"
    fc, stats = build_rijksmonumenten(q, bbox, clip, "archeologische_rijksmonumenten")
    write_extract("archeologische-rijksmonumenten", fc, q, stats, provincies, bbox,
                  "Rijksmonumenten met heeftMonumentAard = archeologisch (concept-URI, geen trefwoord).")

    build_rmon_lookup()


if __name__ == "__main__":
    main()
