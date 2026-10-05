#!/usr/bin/env python3
"""
Bereken de cijfers voor de statistiekpagina (wens opdrachtgever 2026-10-05,
vraag E7: "statistiekpagina zoals bij Zuid-Holland is welkom").

Zelfde scheiding als in het dodenakkers-project: hier rekenen, in
src/statistieken.js alleen tonen. Alleen stdlib, zodat het ook in de
Cloudflare-build zou kunnen draaien; de uitvoer wordt gecommit.

Input
  data/generated/begraafplaatsen.geojson   (scripts/analyse_spatial.py)
  data/generated/herbegravingen.geojson    (idem)

Output
  data/generated/statistieken.json

Draai na scripts/analyse_spatial.py.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
OUT = GENERATED_DIR / "statistieken.json"

STATUSSEN = ["in_gebruik", "geruimd", "verdwenen"]
PROVINCIES = sorted([
    "Drenthe", "Flevoland", "Fryslân", "Gelderland", "Groningen", "Limburg",
    "Noord-Brabant", "Noord-Holland", "Overijssel", "Utrecht", "Zeeland", "Zuid-Holland",
])  # alfabetisch
# Zelfde indeling als het dateringsfilter op de kaart (src/app.js, vraag C9).
DATERING = [
    ("vóór 1700", None, 1700),
    ("1700–1799", 1700, 1800),
    ("1800–1849", 1800, 1850),
    ("1850–1899", 1850, 1900),
    ("1900–1949", 1900, 1950),
    ("1950–heden", 1950, None),
]
TOP = 10


def load(naam: str) -> list[dict]:
    return [f["properties"] for f in json.loads((GENERATED_DIR / naam).read_text(encoding="utf-8"))["features"]]


def per_status(recs: list[dict]) -> dict:
    tel = Counter(r["status"] for r in recs)
    return {s: tel.get(s, 0) for s in STATUSSEN}


def kort(r: dict) -> dict:
    return {"id": r["id"], "naam": r["naam"], "plaats": r["plaats"], "status": r["status"]}


def main() -> None:
    recs = load("begraafplaatsen.geojson")
    lijnen = load("herbegravingen.geojson")
    by_id = {r["id"]: r for r in recs}
    met_terrein = [r for r in recs if r["terrein_opp_m2"]]
    opp = [r["terrein_opp_m2"] for r in met_terrein]
    provs = [p for p in PROVINCIES if any(r["provincie"] == p for r in recs)]

    # --- kerncijfers ---
    basis = {
        "totaal": len(recs),
        "per_status": per_status(recs),
        "provincies": len(provs),
        "met_terrein": len(met_terrein),
        "totaal_m2": sum(opp),
        "mediaan_m2": round(statistics.median(opp)) if opp else None,
        "grootste": kort(max(met_terrein, key=lambda r: r["terrein_opp_m2"])) | {"m2": max(opp)} if opp else None,
        "kleinste": kort(min(met_terrein, key=lambda r: r["terrein_opp_m2"])) | {"m2": min(opp)} if opp else None,
    }

    # --- per provincie ---
    per_provincie = []
    for p in provs:
        rp = [r for r in recs if r["provincie"] == p]
        per_provincie.append({
            "provincie": p, "totaal": len(rp), **per_status(rp),
            "met_terrein": sum(1 for r in rp if r["terrein_opp_m2"]),
            "totaal_m2": sum(r["terrein_opp_m2"] or 0 for r in rp),
        })

    # --- per gemeente (actuele PDOK-indeling) ---
    gem = defaultdict(list)
    for r in recs:
        gem[r["gemeente"]].append(r)
    per_gemeente = sorted(
        ({"gemeente": g, "provincie": rs[0]["provincie"], "totaal": len(rs), **per_status(rs)} for g, rs in gem.items()),
        key=lambda x: (-x["totaal"], x["gemeente"]),
    )[:TOP]
    verdwenen_gem = sorted(
        ({"gemeente": g, "verdwenen_of_geruimd": sum(1 for r in rs if r["status"] != "in_gebruik"), "totaal": len(rs)} for g, rs in gem.items()),
        key=lambda x: (-x["verdwenen_of_geruimd"], x["gemeente"]),
    )
    verdwenen_gem = [x for x in verdwenen_gem if x["verdwenen_of_geruimd"] >= 2][:TOP]

    # --- datering (jaar van aanleg of eerste begraving) ---
    met_jaar = [r for r in recs if r["jaartal"] is not None]
    datering = []
    for label, van, tot in DATERING:
        rs = [r for r in met_jaar if (van is None or r["jaartal"] >= van) and (tot is None or r["jaartal"] < tot)]
        datering.append({"label": label, "aantal": len(rs), **per_status(rs)})
    oudste = [kort(r) | {"jaartal": r["jaartal"], "circa": bool(r["circa"])}
              for r in sorted(met_jaar, key=lambda r: (r["jaartal"], r["id"]))[:TOP]]
    oudste_in_gebruik = [kort(r) | {"jaartal": r["jaartal"], "circa": bool(r["circa"])}
                         for r in sorted((r for r in met_jaar if r["status"] == "in_gebruik"), key=lambda r: (r["jaartal"], r["id"]))[:TOP]]

    # --- erfgoed (alleen in gebruik + geruimd: verdwenen ligt maar bij benadering vast) ---
    berekend = [r for r in recs if r["relaties_berekend"]]
    # Een monument kan binnen 100 m van twee begraafplaatsen liggen. De functietabel
    # telt daarom UNIEKE monumenten; het aantal relaties staat er apart bij
    # (review 2026-10-05: 343 relaties naar 326 monumenten).
    relaties = [m for r in berekend for m in r["rijksmonumenten_nabij"] if m["afstand_m"] <= 100]
    uniek = {m["rijksmonumentnummer"]: m for m in relaties}
    functies = Counter((m["functie"] or "onbekend") for m in uniek.values())
    erfgoed = {
        "basis": len(berekend),
        "rijksmonument": sum(1 for r in recs if r["rijksmonument"] is True),
        "gemeentelijk_monument": sum(1 for r in recs if r["gemeentelijk_monument"] is True),
        "mip": sum(1 for r in recs if r["mip"] is True),
        "metaheerhuis": sum(1 for r in recs if r["met"] is True),
        "in_gezicht": sum(1 for r in berekend if r["in_gezicht"]),
        "met_rijksmonument_100m": sum(1 for r in berekend if any(m["afstand_m"] <= 100 for m in r["rijksmonumenten_nabij"])),
        "relaties_100m": len(relaties),
        "unieke_monumenten_100m": len(uniek),
        "top_functies_100m": [{"functie": f, "aantal": n} for f, n in functies.most_common(TOP)],
        "per_provincie": [
            {"provincie": p,
             "rijksmonument": sum(1 for r in recs if r["provincie"] == p and r["rijksmonument"] is True),
             "in_gezicht": sum(1 for r in berekend if r["provincie"] == p and r["in_gezicht"]),
             "metaheerhuis": sum(1 for r in recs if r["provincie"] == p and r["met"] is True)}
            for p in provs
        ],
    }

    # --- herbegravingen ---
    naar = Counter(l["naar_id"] for l in lijnen)
    herbegravingen = {
        "lijnen": len(lijnen),
        "bestemmingen": len(naar),
        "meeste_ontvangen": [kort(by_id[i]) | {"aantal": n} for i, n in sorted(naar.items(), key=lambda x: (-x[1], x[0])) if n >= 2],
        "met_tekst_overgebracht": sum(1 for r in recs if "overgebracht" in (r["bijzonderheden"] or "").lower()),
    }

    out = {
        "gegenereerd": datetime.now(timezone.utc).date().isoformat(),  # alleen de datum: minder ruis in diffs
        "provincies_op_kaart": provs,
        "basis": basis,
        "per_provincie": per_provincie,
        "per_gemeente": per_gemeente,
        "meeste_verdwenen_gemeente": verdwenen_gem,
        "datering": {"met_jaartal": len(met_jaar), "klassen": datering, "oudste": oudste, "oudste_in_gebruik": oudste_in_gebruik},
        "erfgoed": erfgoed,
        "herbegravingen": herbegravingen,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{OUT.relative_to(REPO_ROOT)}: {len(recs)} begraafplaatsen, {len(provs)} provincies")


if __name__ == "__main__":
    main()
