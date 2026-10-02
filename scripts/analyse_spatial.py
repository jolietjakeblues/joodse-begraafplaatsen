#!/usr/bin/env python3
"""
Verrijk de Joodse begraafplaatsen met gemeente en erfgoedrelaties.

Input
  data/generated/joodse-begraafplaatsen.geojson   (scripts/build_base_dataset.py)
  data/generated/terreinen.geojson
  data/pdok/gemeenten.geojson                      (scripts/fetch_pdok.py)
  data/rce/index.json + de per-provincie RCE-bestanden (scripts/fetch_rce.py)

Output
  data/generated/begraafplaatsen.geojson   punten + alle velden + relaties (voor de viewer)
  docs/data/erfgoedrelaties.md

Werkwijze (overgenomen uit dodenakkers/analyse_spatial.py)
  - Alle metrische bewerkingen in RD New (EPSG:28992).
  - Geometrie per record: het terrein als dat er is, anders het punt.
  - Verdwenen begraafplaatsen liggen maar bij benadering vast: daarvoor worden
    GEEN afstandsrelaties met monumenten/gezichten berekend (dat zou schijn-
    precisie zijn). Alleen gemeente.
  - Afstandsklassen zijn werkhypothesen; de ruwe afstand blijft bewaard.
  - Het rijksmonumentnummer uit de Excel (`Rmon`) wordt opgezocht in de
    RCE-extracten; afwijkingen gaan naar het rapport, niet stil weg.
"""
from __future__ import annotations

import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
RCE_DIR = REPO_ROOT / "data" / "rce"
PDOK_DIR = REPO_ROOT / "data" / "pdok"
RAPPORT = REPO_ROOT / "docs" / "data" / "erfgoedrelaties.md"

RM_NABIJ_M = 100  # besluit 2026-10-02 (zelfde grens als de rijksmonumentenlaag)
# Door Dodenakkers beoordeelde relaties: (begraafplaats-id, rijksmonumentnummer)
# -> relatie die de berekende overschrijft. De berekende relatie blijft bewaard
# als `relatie_berekend`; de afstand blijft de echte (meetkundige) afstand.
BEOORDEELDE_RELATIES = {
    ("jb-loc-819", "454310"): ("net_buiten", "Leon/René 2026-10-02 (vraag A7): valt er net buiten"),
}

# Spelling Excel -> officiele PDOK-naam (zelfde gemeente, geen afwijking)
GEMEENTE_ALIAS = {"Den Haag": "'s-Gravenhage"}

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def rd(feature: dict):
    return transform(to_rd, shape(feature["geometry"]))


class Laag:
    def __init__(self, features: list[dict]):
        self.features = features
        self.geoms = [rd(f) for f in features]
        self.tree = STRtree(self.geoms)


def gemeente_van(point_rd, laag: Laag) -> tuple[str, bool]:
    for i in laag.tree.query(point_rd):
        if laag.geoms[i].contains(point_rd):
            return laag.features[i]["properties"]["naam"], False
    return laag.features[laag.tree.nearest(point_rd)]["properties"]["naam"], True


def gezicht_relaties(geom, laag: Laag):
    rel = []
    for i in laag.tree.query(geom):
        g = laag.geoms[i]
        if geom.within(g):
            r = "binnen"
        elif geom.intersects(g):
            r = "deels"
        else:
            continue
        p = laag.features[i]["properties"]
        rel.append({"naam": p.get("naam"), "gezichtsnummer": p.get("gezichtsnummer"), "uri": p.get("gezicht_uri"), "relatie": r})
    rel.sort(key=lambda x: x["relatie"] != "binnen")
    return rel


def monument_relaties(geom, laag: Laag, max_m: float):
    rel = []
    for i in laag.tree.query(geom.buffer(max_m)):
        g = laag.geoms[i]
        d = geom.distance(g)
        if d > max_m:
            continue
        if d == 0:
            r = "op_terrein" if geom.contains(g) else "grenst_aan" if geom.touches(g) else "overlapt"
        elif d <= 25:
            r = "0-25m"
        else:
            r = "25-100m"
        p = laag.features[i]["properties"]
        rel.append(
            {
                "rijksmonumentnummer": p.get("rijksmonumentnummer"),
                "naam": p.get("naam"),
                "functie": p.get("oorspronkelijke_functie"),
                "url": p.get("monumentenregister_url"),
                "relatie": r,
                "afstand_m": round(d, 1),
            }
        )
    rel.sort(key=lambda x: x["afstand_m"])
    return rel


def rmon_info(nr: str, lookup: dict, rm_op_nummer: dict) -> dict | None:
    e = lookup.get(nr)
    if not e:
        return None
    url = lambda n: f"https://monumentenregister.cultureelerfgoed.nl/monumenten/{n}"
    if e["soort"] == "rijksmonument":
        props = rm_op_nummer.get(nr, {})
        return {"soort": "rijksmonument", "nummer": nr, "naam": e["naam"] or props.get("naam"),
                "functie": props.get("oorspronkelijke_functie"), "uri": e["uri"], "url": url(nr), "onderdelen": []}
    onderdelen = [
        {"rijksmonumentnummer": o, "url": url(o), "functie": rm_op_nummer.get(o, {}).get("oorspronkelijke_functie"),
         "hoofdobject": o == e["hoofdobject"]}
        for o in e["onderdelen"]
    ]
    return {"soort": "complex", "nummer": nr, "naam": e["naam"], "uri": e["uri"],
            "url": url(e["hoofdobject"]) if e["hoofdobject"] else None, "onderdelen": onderdelen}


def main() -> None:
    punten = load(GENERATED_DIR / "joodse-begraafplaatsen.geojson")
    terreinen = {f["properties"]["id"]: f for f in load(GENERATED_DIR / "terreinen.geojson")}
    gemeenten = Laag(load(PDOK_DIR / "gemeenten.geojson"))
    manifest = json.loads((RCE_DIR / "index.json").read_text(encoding="utf-8"))["provincies"]
    provs_nodig = {f["properties"]["provincie"] for f in punten}
    ontbreekt = provs_nodig - set(manifest)
    assert not ontbreekt, f"geen RCE-data voor {ontbreekt}: draai scripts/fetch_rce.py --provincie ..."

    def laag(soort: str) -> Laag:
        feats, gezien = [], set()
        for prov in sorted(provs_nodig):
            for f in load(REPO_ROOT / manifest[prov][soort]):
                key = f["properties"].get("cho_uri") or f["properties"].get("gezicht_uri")
                if key not in gezien:  # grensobjecten staan in twee provinciebestanden
                    gezien.add(key)
                    feats.append(f)
        return Laag(feats)

    gezichten, rm, arch = laag("gezichten"), laag("rijksmonumenten"), laag("archeologisch")
    rm_op_nummer = {
        f["properties"]["rijksmonumentnummer"]: f["properties"] for f in rm.features + arch.features
    }
    # Rmon kan een rijksmonument- of een complexnummer zijn (scripts/fetch_rce.py)
    rmon_lookup = json.loads((RCE_DIR / "rmon-lookup.json").read_text(encoding="utf-8"))["nummers"]

    rapport = {"beoordeeld": [], "gemeente_afwijkend": [], "rmon_niet_in_rce": [], "rmon_is_complex": [], "rce_op_terrein_niet_in_excel": [], "fallback": []}
    out = []
    for f in punten:
        p = dict(f["properties"])
        pt_rd = rd(f)
        terrein = terreinen.get(p["id"])
        geom = rd(terrein) if terrein else pt_rd

        p["gemeente"], via_fallback = gemeente_van(pt_rd, gemeenten)
        if via_fallback:
            rapport["fallback"].append(p["id"])
        if p["gemeente_bron"] and p["gemeente"] != GEMEENTE_ALIAS.get(p["gemeente_bron"], p["gemeente_bron"]):
            rapport["gemeente_afwijkend"].append((p["id"], p["naam"], p["plaats"], p["gemeente_bron"], p["gemeente"]))

        nr = p.get("rijksmonumentnummer")
        p["rijksmonument_rce"] = rmon_info(str(nr), rmon_lookup, rm_op_nummer) if nr else None
        if nr and not p["rijksmonument_rce"]:
            rapport["rmon_niet_in_rce"].append((p["id"], p["naam"], p["plaats"], nr))
        elif nr and p["rijksmonument_rce"]["soort"] == "complex":
            rapport["rmon_is_complex"].append((p["id"], p["naam"], p["plaats"], p["rijksmonument_rce"]))

        if p["status"] == "verdwenen":
            p["gezichten"], p["rijksmonumenten_nabij"], p["archeologisch_nabij"] = [], [], []
            p["relaties_berekend"] = False
        else:
            p["gezichten"] = gezicht_relaties(geom, gezichten)
            p["rijksmonumenten_nabij"] = monument_relaties(geom, rm, RM_NABIJ_M)
            p["archeologisch_nabij"] = monument_relaties(geom, arch, RM_NABIJ_M)
            for r in p["rijksmonumenten_nabij"] + p["archeologisch_nabij"]:
                oordeel = BEOORDEELDE_RELATIES.get((p["id"], r["rijksmonumentnummer"]))
                if oordeel:
                    r["relatie_berekend"], r["relatie"] = r["relatie"], oordeel[0]
                    r["beoordeling"] = oordeel[1]
                    rapport["beoordeeld"].append((p["id"], p["naam"], p["plaats"], r))
            p["relaties_berekend"] = True
            excel_nrs = {str(nr)} if nr else set()
            if p["rijksmonument_rce"]:
                excel_nrs |= {o["rijksmonumentnummer"] for o in p["rijksmonument_rce"]["onderdelen"]}
            for r in p["rijksmonumenten_nabij"] + p["archeologisch_nabij"]:
                if r["relatie"] in ("op_terrein", "overlapt") and r["rijksmonumentnummer"] not in excel_nrs and terrein:
                    rapport["rce_op_terrein_niet_in_excel"].append((p["id"], p["naam"], p["plaats"], r))
        p["in_gezicht"] = p["gezichten"][0]["relatie"] if p["gezichten"] else None
        out.append({"type": "Feature", "properties": p, "geometry": f["geometry"]})

    fc = {"type": "FeatureCollection", "name": "joodse_begraafplaatsen", "features": out}
    path = GENERATED_DIR / "begraafplaatsen.geojson"
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    berekend = [f["properties"] for f in out if f["properties"]["relaties_berekend"]]
    stats = {
        "records": len(out),
        "relaties_berekend": len(berekend),
        "in_gezicht": sum(1 for p in berekend if p["in_gezicht"]),
        "rm_nabij": sum(1 for p in berekend if p["rijksmonumenten_nabij"]),
        "arch_nabij": sum(1 for p in berekend if p["archeologisch_nabij"]),
        "rmon_gekoppeld": sum(1 for f in out if f["properties"]["rijksmonument_rce"]),
    }
    print(f"{path.relative_to(REPO_ROOT)}: {stats}")
    write_rapport(stats, rapport)


def write_rapport(stats: dict, rapport: dict) -> None:
    L = [
        "# Erfgoedrelaties Joodse begraafplaatsen",
        "",
        "Gegenereerd door `scripts/analyse_spatial.py`. Relaties alleen voor begraafplaatsen in gebruik en geruimd "
        "(verdwenen: locatie bij benadering, dus geen afstandsrelaties). Metrisch in RD New.",
        "",
        "## Samenvatting",
        "",
        f"- {stats['records']} begraafplaatsen, waarvan {stats['relaties_berekend']} met berekende relaties.",
        f"- Binnen of deels in een rijksbeschermd gezicht: **{stats['in_gezicht']}**.",
        f"- Gebouwd rijksmonument binnen {RM_NABIJ_M} m: **{stats['rm_nabij']}**.",
        f"- Archeologisch rijksmonument binnen {RM_NABIJ_M} m: **{stats['arch_nabij']}**.",
        f"- Rijksmonumentnummer uit de Excel teruggevonden in RCE: **{stats['rmon_gekoppeld']}**.",
        "",
        "## Rijksmonumentnummer (Excel `Rmon`) niet gevonden in de RCE-extracten",
        "",
    ]
    L += [f"- `{i}` {n}, {pl}: Rmon {nr}" for i, n, pl, nr in rapport["rmon_niet_in_rce"]] or ["Geen."]
    L += ["", "## Rmon in de Excel is een complexnummer (geen rijksmonumentnummer)", "",
          "Het complex is opgezocht en de onderdelen zijn gekoppeld. Ter info voor Dodenakkers.", ""]
    L += [
        f"- `{i}` {n}, {pl}: complex {c['nummer']} \"{c['naam']}\" — onderdelen "
        + ", ".join(f"{o['rijksmonumentnummer']} ({o['functie'] or '–'})" for o in c["onderdelen"])
        for i, n, pl, c in rapport["rmon_is_complex"]
    ] or ["Geen."]
    L += ["", "## Rijksmonument op/overlappend met het terrein, maar niet als Rmon in de Excel", "",
          "Mogelijk een monument dat bij de begraafplaats hoort (hek, metaheerhuis, graftekens) — ter beoordeling.", ""]
    L += [
        f"- `{i}` {n}, {pl}: [{r['rijksmonumentnummer']}]({r['url']}) {r['naam'] or ''} ({r['functie'] or '–'}, {r['relatie']})"
        for i, n, pl, r in rapport["rce_op_terrein_niet_in_excel"]
    ] or ["Geen."]
    L += ["", "## Door Dodenakkers beoordeelde relaties", ""]
    L += [
        f"- `{i}` {n}, {pl}: {r['rijksmonumentnummer']} — berekend `{r['relatie_berekend']}`, beoordeeld `{r['relatie']}` ({r['beoordeling']})"
        for i, n, pl, r in rapport["beoordeeld"]
    ] or ["Geen."]
    L += ["", "## Gemeente in Excel wijkt af van ruimtelijke ligging (PDOK, actuele indeling)", ""]
    L += [f"- `{i}` {n}, {pl}: Excel {gb} → PDOK {g}" for i, n, pl, gb, g in rapport["gemeente_afwijkend"]] or ["Geen."]
    if rapport["fallback"]:
        L += ["", f"Gemeente via dichtstbijzijnde gemeente (punt viel buiten alle grenzen): {', '.join(rapport['fallback'])}"]
    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"rapport -> {RAPPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
