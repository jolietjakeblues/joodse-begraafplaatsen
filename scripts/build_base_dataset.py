#!/usr/bin/env python3
"""
Bouw de basisdataset Joodse begraafplaatsen uit het bronmateriaal van
stichting Dodenakkers (map data-dodenakkers/, niet in git).

Bronnen
  - Excel "Joodse begraafplaatsen totaal voor Joop.xlsx", ALLEEN tabblad
    "Joodse begraafplaatsen" (het tabblad "Dank en informeren" bevat
    persoonsgegevens en wordt nooit gelezen).
  - Locaties.kmz / Verdwenen.kmz / Geruimd.kmz: punten, per reeks genummerd.
  - Provincie-KMZ's (Zuid-Holland.kmz, Funerair <Provincie>.kmz): terreinen
    (Polygon) + ingangen (Point) van alle begraafplaatsen, alleen op naam.

Koppelregel (zie docs/01-data-analyse.md)
  `Nr` is NIET uniek. Het is alleen uniek binnen een reeks, en de reeks
  volgt uit de status:
      in gebruik -> loc (Locaties.kmz, name = Nr)
      verdwenen  -> ver (Verdwenen.kmz, name = "Verdwenen NNNN")
      geruimd    -> ger (Geruimd.kmz,   name = Nr)
  Sleutel: jb-<reeks>-<Nr>. Elke Excel-rij moet precies een punt vinden.

  Terrein (polygoon), alleen voor in gebruik en geruimd:
      punt ligt in polygoon (of binnen TERREIN_NABIJ_M) EN de naam lijkt
      genoeg op het label van het punt (NAAM_MIN_RATIO). Naam alleen of
      ruimte alleen geeft aantoonbaar foute koppelingen (Dordrecht,
      Crooswijk). Verdwenen = altijd alleen een punt, bij benadering.

Correcties gaan via data/corrections.csv (id, veld, waarde, reden, datum,
bron), nooit door de bron te wijzigen.

Output
  data/generated/joodse-begraafplaatsen.geojson   punten, alle kenmerken
  data/generated/terreinen.geojson                 polygonen (id, status)
  data/generated/joodse-begraafplaatsen.csv
  docs/data/koppelrapport.md                       voor Leon / review

Gebruik
  python scripts/build_base_dataset.py                  # Zuid-Holland
  python scripts/build_base_dataset.py --provincie Utrecht --provincie Zuid-Holland
  python scripts/build_base_dataset.py --alle
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import math
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, Polygon, mapping, shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
BRON_DIR = REPO_ROOT / "data-dodenakkers"
GENERATED_DIR = REPO_ROOT / "data" / "generated"
PDOK_DIR = REPO_ROOT / "data" / "pdok"
CORRECTIONS = REPO_ROOT / "data" / "corrections.csv"
RAPPORT = REPO_ROOT / "docs" / "data" / "koppelrapport.md"

EXCEL = BRON_DIR / "Joodse begraafplaatsen totaal voor Joop.xlsx"
EXCEL_SHEET = "Joodse begraafplaatsen"

KML_NS = "{http://www.opengis.net/kml/2.2}"

# Excel-provincienaam (= PDOK-naam) -> KMZ met terreinen
PROVINCIE_KMZ = {
    "Drenthe": "Funerair Drenthe.kmz",
    "Flevoland": "Funerair Flevoland.kmz",
    "Fryslân": "Funerair Friesland.kmz",
    "Gelderland": "Funerair Gelderland.kmz",
    "Groningen": "Funerair Groningen.kmz",
    "Limburg": "Funerair Limburg.kmz",
    "Noord-Brabant": "Funerair Noord-Brabant.kmz",
    "Noord-Holland": "Funerair Noord-Holland.kmz",
    "Overijssel": "Funerair Overijssel.kmz",
    "Utrecht": "Funerair Utrecht.kmz",
    "Zeeland": "Funerair Zeeland1.kmz",
    "Zuid-Holland": "Zuid-Holland.kmz",
}

STATUS_REEKS = {"in gebruik": "loc", "verdwenen": "ver", "geruimd": "ger"}
STATUS_CODE = {"in gebruik": "in_gebruik", "verdwenen": "verdwenen", "geruimd": "geruimd"}

TERREIN_NABIJ_M = 25     # punt net buiten de polygoon (ingang op de rand)
NAAM_MIN_RATIO = 0.6     # difflib-ratio op genormaliseerde namen

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform


# ---------------------------------------------------------------- helpers

def clean(value):
    """Lege/NaN-waarden -> None; strings gestript. NaN mag nooit in JSON."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def normalize_name(text: str | None) -> str:
    """Voor naamvergelijking: lowercase, accenten weg, leestekens -> spatie."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# Woorden die in vrijwel elke naam staan en de vergelijking anders opblazen
# ("Gem. begraafplaats Eikelenburg, Rijswijk" leek met plaats en
# "begraafplaats" erin voor 0.63 op "Liberaal Joodse begraafplaats, Rijswijk").
GENERIEKE_WOORDEN = {
    "begraafplaats", "begraafplaatsen", "begr", "kerkhof", "gem", "gemeentelijke", "gemeentelijk",
    "algemene", "alg", "de", "het", "op", "van", "geruimd",
}


def name_core(text: str | None) -> str:
    """Naam zonder plaats (deel na de laatste komma), statussuffix en generieke woorden."""
    if not text:
        return ""
    text = re.sub(r"\((geruimd|verdwenen)\)", "", text, flags=re.I)
    if "," in text:
        text = text.rsplit(",", 1)[0]
    return " ".join(w for w in normalize_name(text).split() if w not in GENERIEKE_WOORDEN)


def name_ratio(a: str | None, b: str | None) -> float:
    return difflib.SequenceMatcher(None, name_core(a), name_core(b)).ratio()


def ja_nee(value):
    """'Ja'/'ja'/'Nee'/'nee' -> True/False; overige waarden ongewijzigd (ruw blijft ook bewaard)."""
    v = clean(value)
    if isinstance(v, str) and v.lower() in ("ja", "nee"):
        return v.lower() == "ja"
    return v


def as_int(value):
    v = clean(value)
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return int(v)
    if isinstance(v, str) and re.fullmatch(r"\d+", v):
        return int(v)
    return None


def as_text(value):
    v = clean(value)
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


# ---------------------------------------------------------------- KMZ

def read_kml(kmz_path: Path) -> ET.Element:
    with zipfile.ZipFile(kmz_path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".kml"))
        return ET.fromstring(z.read(name))


def parse_coords(text: str) -> list[tuple[float, float]]:
    return [tuple(map(float, c.split(",")[:2])) for c in text.split()]


def read_placemarks(kmz_path: Path) -> list[dict]:
    """Alle placemarks met name, description en geometrieen (Point/Polygon)."""
    out = []
    for i, pm in enumerate(read_kml(kmz_path).iter(f"{KML_NS}Placemark")):
        geoms = []
        for el in pm.iter():
            tag = el.tag.replace(KML_NS, "")
            if tag == "Point":
                (lon, lat), *_ = parse_coords(el.find(f".//{KML_NS}coordinates").text)
                geoms.append(Point(lon, lat))
            elif tag == "Polygon":
                outer = parse_coords(el.find(f"{KML_NS}outerBoundaryIs//{KML_NS}coordinates").text)
                inner = [
                    parse_coords(r.text)
                    for r in el.findall(f"{KML_NS}innerBoundaryIs//{KML_NS}coordinates")
                ]
                geoms.append(Polygon(outer, inner))
        out.append(
            {
                "index": i,
                "name": clean(pm.findtext(f"{KML_NS}name")),
                "description": clean(pm.findtext(f"{KML_NS}description")),
                "geoms": geoms,
                "bron": kmz_path.name,
            }
        )
    return out


def load_reeks_punten() -> dict[tuple[str, int], list[dict]]:
    """(reeks, Nr) -> lijst punten. Een lijst, want ook binnen een reeks kan
    een nummer dubbel voorkomen (Geruimd.kmz Nr 245)."""
    index: dict[tuple[str, int], list[dict]] = {}
    for reeks, bestand, nr_from_name in [
        ("loc", "Locaties.kmz", lambda n: int(n)),
        ("ver", "Verdwenen.kmz", lambda n: int(n.split()[-1])),
        ("ger", "Geruimd.kmz", lambda n: int(n)),
    ]:
        for pm in read_placemarks(BRON_DIR / bestand):
            points = [g for g in pm["geoms"] if g.geom_type == "Point"]
            assert len(points) == 1, f"{bestand} placemark {pm['name']!r}: verwacht 1 punt"
            index.setdefault((reeks, nr_from_name(pm["name"])), []).append(
                {"label": pm["description"], "point": points[0], "bron": bestand, "kml_name": pm["name"]}
            )
    return index


def load_terreinen(provincies: list[str]) -> list[dict]:
    terreinen = []
    for prov in provincies:
        for pm in read_placemarks(BRON_DIR / PROVINCIE_KMZ[prov]):
            for g in pm["geoms"]:
                if g.geom_type == "Polygon":
                    terreinen.append({"naam": pm["name"], "geom": g, "rd": transform(to_rd, g), "bron": pm["bron"]})
    return terreinen


# ---------------------------------------------------------------- Excel

def load_excel() -> pd.DataFrame:
    df = pd.read_excel(EXCEL, sheet_name=EXCEL_SHEET)
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    assert "Plaats.1" in df.columns, "verwacht tweede kolom 'Plaats' (eigenaar) als 'Plaats.1'"
    return df


# ---------------------------------------------------------------- koppelen

def provincie_index():
    feats = json.loads((PDOK_DIR / "provincies.geojson").read_text(encoding="utf-8"))["features"]
    geoms = [shape(f["geometry"]) for f in feats]
    return feats, geoms, STRtree(geoms)


def provincie_van(point: Point, feats, geoms, tree) -> str | None:
    for i in tree.query(point):
        if geoms[i].contains(point):
            return feats[i]["properties"]["naam"]
    return feats[tree.nearest(point)]["properties"]["naam"]  # kustlijn / afronding


def koppel_terrein(point: Point, label: str, terreinen: list[dict], tree: STRtree | None):
    """Geeft (terrein | None, koppelwijze, kandidaten-info)."""
    if tree is None:
        return None, "geen_terrein", []
    pt_rd = transform(to_rd, point)
    kandidaten = []
    for i in tree.query(pt_rd.buffer(TERREIN_NABIJ_M)):
        t = terreinen[i]
        afstand = t["rd"].distance(pt_rd)
        if afstand > TERREIN_NABIJ_M:
            continue
        kandidaten.append((t, round(afstand, 1), round(name_ratio(label, t["naam"]), 2)))
    # Beste: binnen (afstand 0) gaat voor nabij; daarna het KLEINSTE terrein.
    # Geneste terreinen komen voor ("Joods deel op Oud Rijswijk" ligt binnen
    # "Begraafplaats Oud-Rijswijk"); het kleinste is het meest specifieke.
    # Een hogere naam-ratio mag dat niet overrulen -- de algemene begraafplaats
    # scoort daar soms net hoger. De naamtoets is een drempel, geen ranking.
    kandidaten.sort(key=lambda k: (k[1] > 0, k[1], k[0]["rd"].area, -k[2]))
    info = [{"naam": t["naam"], "afstand_m": d, "naam_ratio": r, "opp_m2": round(t["rd"].area)} for t, d, r in kandidaten]
    goed = [k for k in kandidaten if k[2] >= NAAM_MIN_RATIO]
    if not goed:
        return None, "geen_terrein", info
    t, d, r = goed[0]
    if normalize_name(t["naam"]) == normalize_name(label):
        wijze = "binnen_naam_gelijk" if d == 0 else "nabij_naam_gelijk"
    else:
        wijze = "binnen_naamvariant" if d == 0 else "nabij_naamvariant"
    return t, wijze, info


# ---------------------------------------------------------------- correcties

def load_corrections() -> list[dict]:
    if not CORRECTIONS.exists():
        return []
    with CORRECTIONS.open(encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("id")]


def apply_corrections(records: dict[str, dict], corrections: list[dict]) -> list[str]:
    log = []
    for c in corrections:
        rec = records.get(c["id"])
        if rec is None:
            log.append(f"- correctie voor onbekend id `{c['id']}` overgeslagen")
            continue
        oud = rec.get(c["veld"])
        rec[c["veld"]] = c["waarde"] or None
        rec.setdefault("correcties", []).append({k: c[k] for k in ("veld", "reden", "datum", "bron")} | {"oud": oud})
        log.append(f"- `{c['id']}` {c['veld']}: {oud!r} -> {c['waarde']!r} ({c['reden']}, {c['bron']}, {c['datum']})")
    return log


# ---------------------------------------------------------------- main

def build(provincies: list[str]) -> None:
    df = load_excel()
    punten = load_reeks_punten()
    prov_feats, prov_geoms, prov_tree = provincie_index()
    terreinen = load_terreinen(provincies)
    terrein_tree = STRtree([t["rd"] for t in terreinen]) if terreinen else None

    records: dict[str, dict] = {}
    terrein_features: dict[str, dict] = {}
    rapport = {"naamvariant": [], "geen_terrein": [], "provincie_afwijkend": [], "dubbel_punt": [], "polygoon_gedeeld": [], "genest": []}
    alle_excel = 0

    for r in df.to_dict("records"):
        alle_excel += 1
        status_bron = clean(r["Status"])
        status_key = status_bron.lower()
        assert status_key in STATUS_REEKS, f"onbekende status {status_bron!r} (Nr {r['Nr']})"
        reeks = STATUS_REEKS[status_key]
        nr = as_int(r["Nr"])
        sleutel = f"jb-{reeks}-{nr}"
        assert sleutel not in records, f"sleutel {sleutel} niet uniek"

        kandidaten = punten.get((reeks, nr), [])
        assert kandidaten, f"{sleutel}: geen punt in {reeks}-reeks"
        if len(kandidaten) > 1:
            # Kies het punt waarvan het label het meest op de Excel-naam+plaats lijkt.
            doel = f"{clean(r['Naam'])}, {clean(r['Plaats'])}"
            kandidaten = sorted(kandidaten, key=lambda p: -name_ratio(p["label"], doel))
            rapport["dubbel_punt"].append((sleutel, [p["label"] for p in punten[(reeks, nr)]], kandidaten[0]["label"]))
        punt = kandidaten[0]

        provincie_ruimtelijk = provincie_van(punt["point"], prov_feats, prov_geoms, prov_tree)
        provincie_excel = clean(r["Provincie"])
        if provincie_ruimtelijk not in provincies:
            continue
        if provincie_excel != provincie_ruimtelijk:
            rapport["provincie_afwijkend"].append((sleutel, clean(r["Naam"]), provincie_excel, provincie_ruimtelijk))

        status = STATUS_CODE[status_key]
        terrein, koppelwijze, terrein_info = (None, "niet_van_toepassing", [])
        if status != "verdwenen":
            terrein, koppelwijze, terrein_info = koppel_terrein(punt["point"], punt["label"], terreinen, terrein_tree)

        jaartal_bron = as_text(r["Jaartal"])
        grootte_bron = as_text(r["Grootte"])
        rmon_bron = as_text(r["Rmon"])
        adres = " ".join(x for x in [as_text(r["Bezoekadres"]), as_text(r["Huisnummer"])] if x) or None

        rec = {
            "id": sleutel,
            "reeks": reeks,
            "nr": nr,
            "naam": clean(r["Naam"]),
            "label_punt": punt["label"],
            "status": status,
            "status_bron": status_bron,
            "adres": adres,
            "adres_aanduiding": as_text(r["NA"]),  # bv. "bij" = bij dit adres
            "postcode": as_text(r["PC"]),
            "plaats": clean(r["Plaats"]),
            "gemeente_bron": clean(r["Gemeente"]),
            "provincie_bron": provincie_excel,
            "provincie": provincie_ruimtelijk,
            "mip": ja_nee(r["MIP"]),
            "rijksmonument": ja_nee(r["Rijksmonument"]),
            "gemeentelijk_monument": ja_nee(r["Gemeentelijk monument"]),
            "rijksmonumentnummer": as_int(r["Rmon"]),
            "rmon_bron": rmon_bron,
            "link": clean(r["Link"]),
            "beschermd_deel": clean(r["Beschermd deel"]),
            "eigenaar": clean(r["Eigenaar"]),
            "eigenaar_postadres": as_text(r["Postadres"]),
            "eigenaar_postcode": as_text(r["PC Eig."]),
            "eigenaar_plaats": clean(r["Plaats.1"]),
            "jaartal": as_int(r["Jaartal"]),
            "jaartal_bron": jaartal_bron,
            "circa": clean(r["Circa"]),
            "grondvorm": (clean(r["Grondvorm"]) or "").capitalize() or None,
            "met": ja_nee(r["Met"]),        # betekenis navragen bij Dodenakkers
            "muur": clean(r["Muur"]),
            "bijzonderheden": clean(r["Bijzonderheden"]),
            "grootte_m2": as_int(r["Grootte"]),
            "grootte_bron": grootte_bron,
            "kadaster": ja_nee(r["Kadaster"]),
            "laatste_bezoek": as_int(r["Laatste bezoek"]),
            "locatie_precisie": "bij_benadering" if status == "verdwenen" else "ingang",
            "terrein_koppelwijze": koppelwijze,
            "terrein_naam_kml": terrein["naam"] if terrein else None,
            "terrein_opp_m2": round(terrein["rd"].area) if terrein else None,
            "lon": round(punt["point"].x, 7),
            "lat": round(punt["point"].y, 7),
        }
        records[sleutel] = rec

        if terrein:
            prev = terrein_features.get(id(terrein))
            if prev:
                rapport["polygoon_gedeeld"].append((prev["properties"]["id"], sleutel, terrein["naam"]))
            terrein_features[id(terrein)] = {
                "type": "Feature",
                "properties": {"id": sleutel, "status": status, "naam": rec["naam"], "terrein_naam_kml": terrein["naam"]},
                "geometry": mapping(terrein["geom"]),
            }
        if koppelwijze.endswith("naamvariant") or koppelwijze.startswith("nabij"):
            rapport["naamvariant"].append((sleutel, punt["label"], terrein["naam"], koppelwijze, terrein_info))
        binnen_ok = [k for k in terrein_info if k["afstand_m"] == 0 and k["naam_ratio"] >= NAAM_MIN_RATIO]
        if len(binnen_ok) > 1:
            rapport["genest"].append((sleutel, punt["label"], binnen_ok))
        if koppelwijze == "geen_terrein":
            rapport["geen_terrein"].append((sleutel, punt["label"], terrein_info))

    correctie_log = apply_corrections(records, load_corrections())

    # Joodse polygonen in de provincie-KMZ's die door geen enkel record geclaimd zijn
    claimed = {id(t) for t in terreinen if id(t) in terrein_features}
    jood_re = re.compile(r"jood|joden|isra|portug|hoogduits", re.I)
    ongeclaimd = [t["naam"] for t in terreinen if jood_re.search(t["naam"] or "") and id(t) not in claimed]

    write_outputs(records, list(terrein_features.values()))
    write_rapport(provincies, alle_excel, records, rapport, ongeclaimd, correctie_log)

    tel = {s: sum(1 for r in records.values() if r["status"] == s) for s in ("in_gebruik", "geruimd", "verdwenen")}
    print(f"{len(records)} begraafplaatsen ({', '.join(provincies)}): {tel}")
    print(f"  terreinen gekoppeld: {len(terrein_features)}; zonder terrein (excl. verdwenen): {len(rapport['geen_terrein'])}")
    print(f"  naamvarianten/nabij: {len(rapport['naamvariant'])}; ongeclaimde Joodse polygonen: {len(ongeclaimd)}")
    print(f"  provincie Excel != ruimtelijk: {len(rapport['provincie_afwijkend'])}; correcties: {len(correctie_log)}")

    if provincies == ["Zuid-Holland"]:
        # Invarianten Zuid-Holland (docs/01-data-analyse.md, 2026-10-02). Wijzigt
        # de bron, dan bewust bijwerken -- niet stil laten meebewegen.
        assert len(records) == 36, len(records)
        assert tel == {"in_gebruik": 24, "geruimd": 2, "verdwenen": 10}, tel
        assert len(terrein_features) == 26, len(terrein_features)
        assert not ongeclaimd, ongeclaimd


def write_outputs(records: dict[str, dict], terrein_features: list[dict]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    punten_fc = {
        "type": "FeatureCollection",
        "name": "joodse_begraafplaatsen",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": [
            {"type": "Feature", "properties": rec, "geometry": {"type": "Point", "coordinates": [rec["lon"], rec["lat"]]}}
            for rec in sorted(records.values(), key=lambda r: (r["provincie"], r["plaats"] or "", r["naam"] or "", r["id"]))
        ],
    }
    (GENERATED_DIR / "joodse-begraafplaatsen.geojson").write_text(
        json.dumps(punten_fc, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    terreinen_fc = {"type": "FeatureCollection", "name": "terreinen", "features": terrein_features}
    (GENERATED_DIR / "terreinen.geojson").write_text(json.dumps(terreinen_fc, ensure_ascii=False), encoding="utf-8")

    cols = [k for k in next(iter(records.values())).keys() if k != "correcties"]
    with (GENERATED_DIR / "joodse-begraafplaatsen.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for f_ in punten_fc["features"]:
            w.writerow(f_["properties"])


def write_rapport(provincies, alle_excel, records, rapport, ongeclaimd, correctie_log) -> None:
    tel = {s: sum(1 for r in records.values() if r["status"] == s) for s in ("in_gebruik", "geruimd", "verdwenen")}
    L = [
        "# Koppelrapport Joodse begraafplaatsen",
        "",
        f"Gegenereerd door `scripts/build_base_dataset.py` op {datetime.now().strftime('%Y-%m-%d %H:%M')}.",
        f"Provincie(s): **{', '.join(provincies)}**. Excel-rijen landelijk: {alle_excel}.",
        "",
        "## Samenvatting",
        "",
        f"- {len(records)} begraafplaatsen: {tel['in_gebruik']} in gebruik, {tel['geruimd']} geruimd, {tel['verdwenen']} verdwenen.",
        "- Elk record is via (reeks, Nr) aan precies één punt gekoppeld; sleutel `jb-<reeks>-<Nr>`.",
        f"- Terreinen gekoppeld: {sum(1 for r in records.values() if r['terrein_naam_kml'])}.",
        "",
        "## Koppelwijze terrein",
        "",
        "| koppelwijze | aantal |",
        "|---|---|",
    ]
    for wijze in sorted({r["terrein_koppelwijze"] for r in records.values()}):
        L.append(f"| {wijze} | {sum(1 for r in records.values() if r['terrein_koppelwijze'] == wijze)} |")

    L += ["", "## Ter controle voor Dodenakkers: naamvarianten", "",
          "Het punt ligt in (of vlak bij) het terrein, maar de naam van het terrein in de provincie-KMZ wijkt af van het label van het punt.", "",
          "| id | label punt | naam terrein | koppelwijze |", "|---|---|---|---|"]
    for sleutel, label, tnaam, wijze, _ in rapport["naamvariant"]:
        L.append(f"| `{sleutel}` | {label} | {tnaam} | {wijze} |")
    if not rapport["naamvariant"]:
        L.append("| – | – | – | – |")

    L += ["", "## Zonder terrein (status in gebruik / geruimd)", ""]
    for sleutel, label, info in rapport["geen_terrein"]:
        kand = "; ".join(f"{k['naam']} ({k['afstand_m']} m, ratio {k['naam_ratio']})" for k in info[:3]) or "geen polygoon binnen bereik"
        L.append(f"- `{sleutel}` {label} — kandidaten: {kand}")
    if not rapport["geen_terrein"]:
        L.append("Geen.")

    L += ["", "## Joodse polygonen in de provincie-KMZ zonder record", ""]
    L += [f"- {n}" for n in ongeclaimd] or ["Geen."]

    L += ["", "## Provincie in Excel wijkt af van ruimtelijke ligging (PDOK)", ""]
    L += [f"- `{s}` {n}: Excel {pe}, ligt in {pr}" for s, n, pe, pr in rapport["provincie_afwijkend"]] or ["Geen."]

    L += ["", "## Dubbel nummer binnen een reeks", ""]
    L += [f"- `{s}`: {labels} → gekozen: {keuze}" for s, labels, keuze in rapport["dubbel_punt"]] or ["Geen."]

    L += ["", "## Punt ligt in meerdere terreinen (genest) — kleinste gekozen", ""]
    for s, label, kand in rapport["genest"]:
        L.append(f"- `{s}` {label}: " + "; ".join(f"{k['naam']} ({k['opp_m2']} m², ratio {k['naam_ratio']})" for k in kand)
                 + f" → gekozen: {kand[0]['naam']}")
    if not rapport["genest"]:
        L.append("Geen.")

    L += ["", "## Eén terrein door meerdere records geclaimd", ""]
    L += [f"- {a} en {b}: {n}" for a, b, n in rapport["polygoon_gedeeld"]] or ["Geen."]

    L += ["", "## Toegepaste correcties (`data/corrections.csv`)", ""]
    L += correctie_log or ["Geen."]

    L += ["", "## Verdwenen begraafplaatsen", "",
          "Verdwenen begraafplaatsen krijgen nooit een terrein. Het punt geeft de plek **bij benadering** aan "
          "(vermoedelijk op basis van archiefonderzoek).", ""]
    for r in sorted(records.values(), key=lambda r: r["id"]):
        if r["status"] == "verdwenen":
            L.append(f"- `{r['id']}` {r['naam']}, {r['plaats']} — {r['bijzonderheden'] or ''}")

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"rapport -> {RAPPORT.relative_to(REPO_ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provincie", action="append", choices=sorted(PROVINCIE_KMZ), help="herhaalbaar; standaard Zuid-Holland")
    ap.add_argument("--alle", action="store_true", help="alle provincies")
    args = ap.parse_args()
    provincies = sorted(PROVINCIE_KMZ) if args.alle else (args.provincie or ["Zuid-Holland"])
    build(provincies)


if __name__ == "__main__":
    main()
