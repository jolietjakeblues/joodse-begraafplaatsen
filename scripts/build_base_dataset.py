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
# Handmatige terreinkoppelingen (id, terrein_naam, reden, datum, bron) voor
# gevallen waar de naamtoets faalt maar de koppeling vaststaat.
TERREIN_KOPPELINGEN = REPO_ROOT / "data" / "terrein_koppelingen.csv"
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

# Gecontroleerde tellingen per provincie (zie docs/data/koppelrapport.md).
#   Zuid-Holland 2026-10-02: alle terreinen gekoppeld.
#   Utrecht 2026-10-02: Bilthoven (jb-loc-4368, Progressieve joodse begraafplaats)
#     heeft geen eigen terrein in Funerair Utrecht.kmz -> 13 van 14 bestaand.
#   Noord-Holland, Zeeland, Flevoland 2026-10-02: alle bestaande gekoppeld
#     (Vlissingen jb-loc-9 via data/terrein_koppelingen.csv; Ouderkerk via Excel-naam "Beth Haim").
#   Gelderland 2026-10-02: alle 45 in gebruik gekoppeld; alleen naamvarianten in schrijfwijze.
#   Overijssel 2026-10-02: alles gekoppeld; Enschede jb-loc-3027 en jb-loc-3002 via
#     data/terrein_koppelingen.csv (naamtoets faalt op Israelitisch <-> Joods, oppervlak klopt).
#   Noord-Brabant 2026-10-02: alles gekoppeld; Putte "Sombre Hadas" = KMZ-tikfout (vraag B8).
#   Limburg 2026-10-02: alles gekoppeld; alleen naamvarianten in schrijfwijze ("Joods Maastricht" e.d.).
INVARIANTEN = {
    "Zuid-Holland": {"totaal": 36, "in_gebruik": 24, "geruimd": 2, "verdwenen": 10, "terreinen": 26},
    "Utrecht": {"totaal": 20, "in_gebruik": 14, "geruimd": 0, "verdwenen": 6, "terreinen": 13},
    "Noord-Holland": {"totaal": 28, "in_gebruik": 22, "geruimd": 0, "verdwenen": 6, "terreinen": 22},
    "Zeeland": {"totaal": 6, "in_gebruik": 6, "geruimd": 0, "verdwenen": 0, "terreinen": 6},
    "Flevoland": {"totaal": 1, "in_gebruik": 1, "geruimd": 0, "verdwenen": 0, "terreinen": 1},
    "Gelderland": {"totaal": 61, "in_gebruik": 45, "geruimd": 0, "verdwenen": 16, "terreinen": 45},
    "Overijssel": {"totaal": 43, "in_gebruik": 34, "geruimd": 1, "verdwenen": 8, "terreinen": 35},
    "Noord-Brabant": {"totaal": 31, "in_gebruik": 21, "geruimd": 0, "verdwenen": 10, "terreinen": 21},
    "Limburg": {"totaal": 25, "in_gebruik": 18, "geruimd": 1, "verdwenen": 6, "terreinen": 19},
}

# Door Dodenakkers bevestigd: er is geen terrein, alleen een puntlocatie.
# Telt in het rapport niet meer als open punt.
GEEN_TERREIN_BEVESTIGD = {
    "jb-loc-4368": "Bilthoven: alleen puntlocatie beschikbaar (Leon/René 2026-10-02, vraag B1)",
}

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


def split_plaats(text: str) -> tuple[str, str | None]:
    """"Naam, Plaats" -> (naam, plaats). Valt terug op ". " als scheidingsteken
    ("Joodse begraafplaats. Almere" in Funerair Flevoland/Noord-Holland/Zeeland)."""
    if "," in text:
        naam, plaats = text.rsplit(",", 1)
        return naam, plaats
    m = re.match(r"^(.*\S)\.\s+([^.]+)$", text)
    if m:
        return m.group(1), m.group(2)
    return text, None


def name_core(text: str | None) -> str:
    """Naam zonder plaats, statussuffix en generieke woorden."""
    if not text:
        return ""
    text = re.sub(r"\((geruimd|verdwenen)\)", "", text, flags=re.I)
    text = split_plaats(text)[0]
    return " ".join(w for w in normalize_name(text).split() if w not in GENERIEKE_WOORDEN)


def name_ratio(a: str | None, b: str | None) -> float:
    """a = label van het punt ("Naam, Plaats"), b = naam van de polygoon.
    De plaats uit a wordt ook uit b gehaald als die daar zonder komma in staat
    ("Joods veenendaal", Utrecht-KMZ)."""
    plaats = set(normalize_name(split_plaats(a)[1] or "").split()) if a else set()
    ca = " ".join(w for w in name_core(a).split() if w not in plaats)
    cb = " ".join(w for w in name_core(b).split() if w not in plaats)
    ratio = difflib.SequenceMatcher(None, ca, cb).ratio()
    # Alle kernwoorden van de terreinnaam komen in de andere naam voor
    # ("Beth Haim" in "Portugees Isr. begraafplaats Beth Haim") -> telt als goed.
    if cb and len(cb) >= 5 and set(cb.split()) <= set(ca.split()):
        ratio = max(ratio, 0.9)
    return ratio


def ja_nee(value):
    """'Ja'/'ja'/'Nee'/'nee' -> True/False; overige waarden ongewijzigd (ruw blijft ook bewaard).
    "Geen" = "Nee" (verspringing tussen de delen van de Excel; Leon 2026-10-02, vraag A3)."""
    v = clean(value)
    if isinstance(v, str) and v.lower() in ("ja", "nee", "geen"):
        return v.lower() == "ja"
    return v


# Excel "NA" (nader adres): "to" = "tegenover" (Leon 2026-10-02, vraag A3)
ADRES_AANDUIDING = {"to": "tegenover"}


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


def koppel_terrein(point: Point, labels: list[str], terreinen: list[dict], tree: STRtree | None,
                   handmatig: dict | None = None):
    """Geeft (terrein | None, koppelwijze, kandidaten-info).

    labels: het label van het punt en de Excel-naam ("Naam, Plaats"); de beste
    naam-ratio telt ("Beth Haim" staat alleen in de Excel-naam, Ouderkerk).
    handmatig: regel uit data/terrein_koppelingen.csv -> die terreinnaam,
    mits het terrein binnen TERREIN_NABIJ_M van het punt ligt."""
    if tree is None:
        return None, "geen_terrein", []
    label = labels[0]
    pt_rd = transform(to_rd, point)
    kandidaten = []
    for i in tree.query(pt_rd.buffer(TERREIN_NABIJ_M)):
        t = terreinen[i]
        afstand = t["rd"].distance(pt_rd)
        if afstand > TERREIN_NABIJ_M:
            continue
        kandidaten.append((t, round(afstand, 1), round(max(name_ratio(l, t["naam"]) for l in labels if l), 2)))
    # Beste: binnen (afstand 0) gaat voor nabij; daarna het KLEINSTE terrein.
    # Geneste terreinen komen voor ("Joods deel op Oud Rijswijk" ligt binnen
    # "Begraafplaats Oud-Rijswijk"); het kleinste is het meest specifieke.
    # Een hogere naam-ratio mag dat niet overrulen -- de algemene begraafplaats
    # scoort daar soms net hoger. De naamtoets is een drempel, geen ranking.
    kandidaten.sort(key=lambda k: (k[1] > 0, k[1], k[0]["rd"].area, -k[2]))
    info = [{"naam": t["naam"], "afstand_m": d, "naam_ratio": r, "opp_m2": round(t["rd"].area)} for t, d, r in kandidaten]
    if handmatig:
        keuze = [k for k in kandidaten if k[0]["naam"] == handmatig["terrein_naam"]]
        assert keuze, f"handmatige koppeling {handmatig}: terrein niet binnen {TERREIN_NABIJ_M} m van het punt"
        return keuze[0][0], "handmatig", info
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
        rec.setdefault(f"{c['veld']}_bron", oud)  # oorspronkelijke waarde blijft zichtbaar
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

    handmatige = {}
    if TERREIN_KOPPELINGEN.exists():
        with TERREIN_KOPPELINGEN.open(encoding="utf-8", newline="") as f:
            handmatige = {r["id"]: r for r in csv.DictReader(f) if r.get("id")}
    records: dict[str, dict] = {}
    terrein_features: dict[str, dict] = {}
    rapport = {"oppervlak": [], "naamvariant": [], "geen_terrein": [], "provincie_afwijkend": [], "dubbel_punt": [], "polygoon_gedeeld": [], "genest": []}
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
            excel_label = f"{clean(r['Naam'])}, {clean(r['Plaats'])}"
            terrein, koppelwijze, terrein_info = koppel_terrein(
                punt["point"], [punt["label"], excel_label], terreinen, terrein_tree, handmatige.get(sleutel)
            )

        jaartal_bron = as_text(r["Jaartal"])
        grootte_bron = as_text(r["Grootte"])
        rmon_bron = as_text(r["Rmon"])
        adres = " ".join(x for x in [as_text(r["Bezoekadres"]), as_text(r["Huisnummer"])] if x) or None

        # Niet overgenomen (Leon 2026-10-02, vragen A3/C1/C2): Eigenaar + postadres
        # (onvolledig, "helemaal niet tonen"), Grondvorm, Muur (onvolledig),
        # Kadaster en Laatste bezoek. Ze komen dus ook niet in de open data.
        rec = {
            "id": sleutel,
            "reeks": reeks,
            "nr": nr,
            "naam": clean(r["Naam"]),
            "label_punt": punt["label"],
            "status": status,
            "status_bron": status_bron,
            "adres": adres,
            # NA = nader adres: "bij" / "tegenover" / "achter" het adres (Leon/René 2026-10-02)
            "adres_aanduiding": ADRES_AANDUIDING.get(as_text(r["NA"]), as_text(r["NA"])),
            "adres_aanduiding_bron": as_text(r["NA"]),
            "postcode": as_text(r["PC"]),
            "plaats": clean(r["Plaats"]),
            "gemeente_bron": clean(r["Gemeente"]),
            "provincie_bron": provincie_excel,
            "provincie": provincie_ruimtelijk,
            "mip": ja_nee(r["MIP"]),        # MIP = Monumenten Inventarisatie Project
            "rijksmonument": ja_nee(r["Rijksmonument"]),
            "gemeentelijk_monument": ja_nee(r["Gemeentelijk monument"]),
            "gemeentelijk_monument_bron": as_text(r["Gemeentelijk monument"]),
            "rijksmonumentnummer": as_int(r["Rmon"]),
            "rmon_bron": rmon_bron,
            "link": clean(r["Link"]),
            "beschermd_deel": clean(r["Beschermd deel"]),
            "jaartal": as_int(r["Jaartal"]),
            "jaartal_bron": jaartal_bron,
            "circa": clean(r["Circa"]),
            "met": ja_nee(r["Met"]),        # Met = metaheerhuis(je) aanwezig
            "bijzonderheden": clean(r["Bijzonderheden"]),
            "grootte_m2": as_int(r["Grootte"]),
            "grootte_bron": grootte_bron,
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
        if terrein and rec["grootte_m2"]:
            verhouding = rec["terrein_opp_m2"] / rec["grootte_m2"]
            if not 0.75 <= verhouding <= 1.33:
                rapport["oppervlak"].append((sleutel, punt["label"], terrein["naam"], rec["terrein_opp_m2"], rec["grootte_m2"]))
        if koppelwijze.endswith("naamvariant") or koppelwijze.startswith("nabij"):
            rapport["naamvariant"].append((sleutel, punt["label"], terrein["naam"], koppelwijze, terrein_info))
        binnen_ok = [k for k in terrein_info if k["afstand_m"] == 0 and k["naam_ratio"] >= NAAM_MIN_RATIO]
        if len(binnen_ok) > 1:
            rapport["genest"].append((sleutel, punt["label"], binnen_ok))
        if koppelwijze == "geen_terrein" and sleutel in GEEN_TERREIN_BEVESTIGD:
            koppelwijze = rec["terrein_koppelwijze"] = "geen_terrein_bevestigd"
        if koppelwijze == "geen_terrein":
            rapport["geen_terrein"].append((sleutel, punt["label"], terrein_info))

    correctie_log = apply_corrections(records, load_corrections())

    # Joodse polygonen in de provincie-KMZ's die door geen enkel record geclaimd zijn
    claimed = {id(t) for t in terreinen if id(t) in terrein_features}
    jood_re = re.compile(r"jood|joden|isra|portug|hoogduits", re.I)
    ongeclaimd = [t["naam"] for t in terreinen if jood_re.search(t["naam"] or "") and id(t) not in claimed]

    joodse_t = [t for t in terreinen if jood_re.search(t["naam"] or "")]
    rapport["zelfde_opp"] = [
        (a["naam"], b["naam"], round(a["rd"].area), round(a["rd"].distance(b["rd"])))
        for i, a in enumerate(joodse_t) for b in joodse_t[i + 1:]
        if round(a["rd"].area) == round(b["rd"].area) and not a["geom"].equals(b["geom"])
    ]
    write_outputs(records, list(terrein_features.values()))
    write_rapport(provincies, alle_excel, records, rapport, ongeclaimd, correctie_log)

    tel = {s: sum(1 for r in records.values() if r["status"] == s) for s in ("in_gebruik", "geruimd", "verdwenen")}
    print(f"{len(records)} begraafplaatsen ({', '.join(provincies)}): {tel}")
    print(f"  terreinen gekoppeld: {len(terrein_features)}; zonder terrein (excl. verdwenen): {len(rapport['geen_terrein'])}")
    print(f"  naamvarianten/nabij: {len(rapport['naamvariant'])}; ongeclaimde Joodse polygonen: {len(ongeclaimd)}")
    print(f"  provincie Excel != ruimtelijk: {len(rapport['provincie_afwijkend'])}; correcties: {len(correctie_log)}")

    # Invarianten per provincie (vastgesteld na handmatige controle). Wijzigt de
    # bron, dan bewust bijwerken -- niet stil laten meebewegen.
    for prov in provincies:
        verwacht = INVARIANTEN.get(prov)
        if not verwacht:
            continue
        recs = [r for r in records.values() if r["provincie"] == prov]
        werkelijk = {
            "totaal": len(recs),
            **{s_: sum(1 for r in recs if r["status"] == s_) for s_ in ("in_gebruik", "geruimd", "verdwenen")},
            "terreinen": sum(1 for r in recs if r["terrein_naam_kml"]),
        }
        assert werkelijk == verwacht, f"{prov}: verwacht {verwacht}, gevonden {werkelijk}"
    assert not ongeclaimd, f"ongekoppelde Joodse polygonen: {ongeclaimd}"


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
          "| id | label punt | naam terrein | koppelwijze | status |", "|---|---|---|---|---|"]
    for sleutel, label, tnaam, wijze, _ in rapport["naamvariant"]:
        vast = next((c for c in records[sleutel].get("correcties", []) if c["veld"] == "naam"), None)
        status = f"naam vastgesteld: {records[sleutel]['naam']} ({vast['bron']})" if vast else "open"
        L.append(f"| `{sleutel}` | {label} | {tnaam} | {wijze} | {status} |")
    if not rapport["naamvariant"]:
        L.append("| – | – | – | – | – |")

    L += ["", "## Oppervlakte terrein wijkt sterk af van Excel-kolom `Grootte`", "",
          "Terreinoppervlak (KMZ, berekend in RD) buiten 75–133 % van `Grootte`. Mogelijk verkeerd terrein, "
          "of een verouderde/afwijkende maat in de Excel.", "",
          "| id | label punt | terrein | terrein m² | Grootte m² |", "|---|---|---|---|---|"]
    nl = lambda n: f"{n:,}".replace(",", ".")
    L += [f"| `{a}` | {b} | {c} | {nl(d)} | {nl(e)} |" for a, b, c, d, e in rapport["oppervlak"]] or ["| – | – | – | – | – |"]

    L += ["", "## Handmatige terreinkoppelingen (`data/terrein_koppelingen.csv`)", ""]
    hand = [r for r in records.values() if r["terrein_koppelwijze"] == "handmatig"]
    L += [f"- `{r['id']}` {r['label_punt']} → {r['terrein_naam_kml']} ({r['terrein_opp_m2']} m², Grootte {r['grootte_m2']})"
          for r in hand] or ["Geen."]

    L += ["", "## Joodse terreinen met exact dezelfde oppervlakte (mogelijk gekopieerde polygoon)", ""]
    L += [f"- {a} en {b}: {opp} m² (afstand {afst} m)" for a, b, opp, afst in rapport.get("zelfde_opp", [])] or ["Geen."]

    L += ["", "## Bevestigd zonder terrein (alleen puntlocatie)", ""]
    L += [f"- `{k}` {v}" for k, v in GEEN_TERREIN_BEVESTIGD.items() if k in records] or ["Geen."]

    L += ["", "## Zonder terrein (status in gebruik / geruimd) — open", ""]
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
