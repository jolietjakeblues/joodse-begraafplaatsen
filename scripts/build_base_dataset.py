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
bron), nooit door de bron te wijzigen. Staat het punt van een begraafplaats
onder een ander Nr in het puntbestand (twee nummers verwisseld), dan zegt
data/punt_correcties.csv (id, punt_nr, reden, datum, bron) welk punt uit
dezelfde reeks hoort bij die Excel-rij; het terrein volgt dan uit dat punt.

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
import datetime
import difflib
import json
import math
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
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
# Verwisselde nummers in het puntbestand (id -> punt_nr uit dezelfde reeks).
PUNT_CORRECTIES = REPO_ROOT / "data" / "punt_correcties.csv"
RAPPORT = REPO_ROOT / "docs" / "data" / "koppelrapport.md"
# Door Dodenakkers nagestuurde, gecorrigeerde terreinen + ingangen (Point +
# Polygon per naam, zelfde opbouw als de provincie-KMZ's). Een terrein hierin
# vervangt het terrein met exact dezelfde naam uit de provincie-KMZ, en het punt
# wordt de locatie (ingang) van de gekoppelde begraafplaats. De bronbestanden
# zelf blijven ongewijzigd. Eerste levering 2026-10-05: Venlo (oude), Dedemsvaart.
# Tweede levering 2026-10-06: Loppersum (nieuw terrein, stond niet in de
# provincie-KMZ) en Uithuizen (alleen een verbeterd punt).
CORRECTIE_KMZS = [BRON_DIR / "funerair_nieuwedata.kmz", BRON_DIR / "Voor Joop.kmz"]

# 2026-10-06: nieuwe Excel van Leon (vervangt "Joodse begraafplaatsen totaal
# voor Joop.xlsx"). Nieuwe kolommen Contactpersoon/Telefoon/E-mail/Website/
# Foto Beeldbank worden niet ingelezen (persoonsgegevens, niet gevraagd).
EXCEL = BRON_DIR / "Joodse begraafplaatsen voor Joop.xlsx"
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

# Gecontroleerde tellingen per provincie, met toelichting: data/invarianten.json
# (ook gelezen door scripts/check_data.py, vóór elke sitebuild).
INVARIANTEN_JSON = REPO_ROOT / "data" / "invarianten.json"
_inv = json.loads(INVARIANTEN_JSON.read_text(encoding="utf-8"))
INVARIANTEN = {prov: {k: v for k, v in t.items() if k != "toelichting"} for prov, t in _inv["provincies"].items()}
LANDELIJK_EXCEL_RIJEN = _inv["landelijk_excel_rijen"]

# Register van gepubliceerde kenmerken (links vanuit het boek mogen niet breken).
KENMERKEN_JSON = REPO_ROOT / "data" / "kenmerken.json"


def controleer_kenmerken(records: dict[str, dict], provincies: list[str]) -> dict | None:
    """Geeft het bijgewerkte register terug (nieuwe kenmerken toegevoegd), of None
    als er niets verandert. Faalt als een gepubliceerd kenmerk uit een van de
    gedraaide provincies verdwenen is zonder vermelding onder 'vervallen'."""
    reg = json.loads(KENMERKEN_JSON.read_text(encoding="utf-8"))
    weg = sorted(
        k for k, v in reg["kenmerken"].items()
        if v["provincie"] in provincies and k not in records and k not in reg["vervallen"]
    )
    assert not weg, (
        f"gepubliceerde kenmerken verdwenen: {weg}. Zet ze onder 'vervallen' in data/kenmerken.json "
        "(met 'naar', 'reden', 'datum', 'bron') zodat links blijven werken."
    )
    nieuw = sorted(k for k in records if k not in reg["kenmerken"])
    verhuisd = sorted(k for k in records if k in reg["kenmerken"] and reg["kenmerken"][k]["provincie"] != records[k]["provincie"])
    if not nieuw and not verhuisd:
        return None
    vandaag = datetime.date.today().isoformat()
    for k in nieuw:
        reg["kenmerken"][k] = {"sinds": vandaag, "provincie": records[k]["provincie"]}
    for k in verhuisd:
        reg["kenmerken"][k]["provincie"] = records[k]["provincie"]
    reg["kenmerken"] = dict(sorted(reg["kenmerken"].items()))
    print(f"  kenmerken: {len(nieuw)} nieuw geregistreerd, {len(verhuisd)} van provincie gewisseld")
    return reg

# Door Dodenakkers bevestigd: er is geen terrein, alleen een puntlocatie
# (data/geen_terrein_bevestigd.csv: id, reden, datum, bron). Telt in het
# rapport niet meer als open punt.
with (REPO_ROOT / "data" / "geen_terrein_bevestigd.csv").open(encoding="utf-8", newline="") as _f:
    GEEN_TERREIN_BEVESTIGD = {r["id"]: f"{r['reden']} ({r['bron']}, {r['datum']})" for r in csv.DictReader(_f) if r.get("id")}

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


def load_correcties_kmz() -> dict[str, dict]:
    """naam -> {"polygon", "point", "bron"} uit CORRECTIE_KMZS (latere levering wint niet:
    dezelfde naam in twee leveringen is een fout)."""
    out: dict[str, dict] = {}
    for kmz in CORRECTIE_KMZS:
        if not kmz.exists():
            continue
        namen = set()
        for pm in read_placemarks(kmz):
            assert pm["name"] not in out or pm["name"] in namen, f"{pm['name']!r} staat in twee correctie-KMZ's"
            namen.add(pm["name"])
            entry = out.setdefault(pm["name"], {"polygon": None, "point": None, "bron": kmz.name})
            for g in pm["geoms"]:
                key = "polygon" if g.geom_type == "Polygon" else "point"
                # Exact dezelfde geometrie twee keer (Uithuizen, Voor Joop.kmz) is onschuldig.
                assert entry[key] is None or entry[key].equals(g), f"{kmz.name}: twee verschillende {key}s voor {pm['name']!r}"
                entry[key] = g
    return out


def load_terreinen(provincies: list[str], correcties: dict[str, dict]) -> list[dict]:
    terreinen = []
    for prov in provincies:
        for pm in read_placemarks(BRON_DIR / PROVINCIE_KMZ[prov]):
            for g in pm["geoms"]:
                if g.geom_type == "Polygon":
                    terreinen.append({"naam": pm["name"], "geom": g, "rd": transform(to_rd, g), "bron": pm["bron"]})
    for naam, c in correcties.items():
        if c["polygon"] is None:
            continue
        treffers = [t for t in terreinen if t["naam"] == naam]
        if not treffers:
            # Nieuw terrein dat niet in de provincie-KMZ staat (Loppersum). Wordt
            # alleen gekoppeld als een punt van deze run erin/ernaast ligt.
            terreinen.append({"naam": naam, "rd_oud_m2": None})
            treffers = terreinen[-1:]
        assert len(treffers) == 1, f"correctie {naam!r}: {len(treffers)} terreinen met die naam"
        t = treffers[0]
        t.setdefault("rd_oud_m2", round(t["rd"].area) if "rd" in t else None)
        t["geom"], t["rd"], t["bron"] = c["polygon"], transform(to_rd, c["polygon"]), c["bron"]
        t["gecorrigeerd"] = True
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


JA_NEE_VELDEN = {"rijksmonument", "gemeentelijk_monument", "mip", "met"}
GETAL_VELDEN = {"rijksmonumentnummer", "jaartal", "grootte_m2"}


def apply_corrections(records: dict[str, dict], corrections: list[dict]) -> list[str]:
    log = []
    for c in corrections:
        rec = records.get(c["id"])
        if rec is None:
            log.append(f"- correctie voor onbekend id `{c['id']}` overgeslagen")
            continue
        oud = rec.get(c["veld"])
        rec.setdefault(f"{c['veld']}_bron", oud)  # oorspronkelijke waarde blijft zichtbaar
        # Zelfde type als bij het inlezen: ja/nee -> bool, nummers -> int, anders tekst.
        if c["veld"] in JA_NEE_VELDEN:
            rec[c["veld"]] = ja_nee(c["waarde"])
        elif c["veld"] in GETAL_VELDEN:
            rec[c["veld"]] = as_int(c["waarde"])
        else:
            rec[c["veld"]] = c["waarde"] or None
        rec.setdefault("correcties", []).append({k: c[k] for k in ("veld", "reden", "datum", "bron")} | {"oud": oud})
        log.append(f"- `{c['id']}` {c['veld']}: {oud!r} -> {c['waarde']!r} ({c['reden']}, {c['bron']}, {c['datum']})")
    return log


# ---------------------------------------------------------------- main

def build(provincies: list[str]) -> None:
    df = load_excel()
    punten = load_reeks_punten()
    prov_feats, prov_geoms, prov_tree = provincie_index()
    correcties_kmz = load_correcties_kmz()
    terreinen = load_terreinen(provincies, correcties_kmz)
    terrein_tree = STRtree([t["rd"] for t in terreinen]) if terreinen else None

    handmatige = {}
    if TERREIN_KOPPELINGEN.exists():
        with TERREIN_KOPPELINGEN.open(encoding="utf-8", newline="") as f:
            handmatige = {r["id"]: r for r in csv.DictReader(f) if r.get("id")}
    punt_correcties = {}
    if PUNT_CORRECTIES.exists():
        with PUNT_CORRECTIES.open(encoding="utf-8", newline="") as f:
            punt_correcties = {r["id"]: r for r in csv.DictReader(f) if r.get("id")}
    records: dict[str, dict] = {}
    terrein_features: dict[str, dict] = {}
    rapport = {"oppervlak": [], "naamvariant": [], "geen_terrein": [], "provincie_afwijkend": [], "dubbel_punt": [], "polygoon_gedeeld": [], "genest": [], "correctie_kmz": [], "punt_correctie": []}
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

        punt_nr = nr
        if sleutel in punt_correcties:
            punt_nr = int(punt_correcties[sleutel]["punt_nr"])
            rapport["punt_correctie"].append((sleutel, nr, punt_nr, punt_correcties[sleutel]["reden"]))
        kandidaten = punten.get((reeks, punt_nr), [])
        assert kandidaten, f"{sleutel}: geen punt in {reeks}-reeks"
        if len(kandidaten) > 1:
            # Kies het punt waarvan het label het meest op de Excel-naam+plaats lijkt.
            doel = f"{clean(r['Naam'])}, {clean(r['Plaats'])}"
            kandidaten = sorted(kandidaten, key=lambda p: -name_ratio(p["label"], doel))
            rapport["dubbel_punt"].append((sleutel, [p["label"] for p in punten[(reeks, punt_nr)]], kandidaten[0]["label"]))
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

        # Nagestuurde ingang (CORRECTIE_KMZS) met de naam van het terrein -> die
        # ingang is de locatie; ook als alleen het punt is gecorrigeerd (Uithuizen).
        locatie, locatie_bron = punt["point"], punt["bron"]
        correctie = correcties_kmz.get(terrein["naam"]) if terrein else None
        if correctie and correctie["point"] is not None:
            locatie, locatie_bron = correctie["point"], correctie["bron"]
            koppelwijze = "correctie_kmz"  # terrein + ingang door Dodenakkers nagestuurd; geen naamvariant
            rapport["correctie_kmz"].append((sleutel, terrein["naam"], terrein.get("rd_oud_m2", round(terrein["rd"].area)), round(terrein["rd"].area),
                                             round(transform(to_rd, punt["point"]).distance(transform(to_rd, locatie)), 1)))

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
            "bijzonderheden": as_text(r["Bijzonderheden"]),  # tekst, ook als de Excel er een getal van maakt ("-1883")
            "grootte_m2": as_int(r["Grootte"]),
            "grootte_bron": grootte_bron,
            "locatie_precisie": "bij_benadering" if status == "verdwenen" else "ingang",
            "terrein_koppelwijze": koppelwijze,
            "terrein_naam_kml": terrein["naam"] if terrein else None,
            "terrein_opp_m2": round(terrein["rd"].area) if terrein else None,
            "locatie_bron": locatie_bron,
            "terrein_bron": terrein["bron"] if terrein else None,
            # Verdwenen: plek bij benadering -> 4 decimalen (~10 m), geen schijnprecisie
            # in de open data. De bron (KMZ) blijft ongewijzigd.
            "lon": round(locatie.x, 4 if status == "verdwenen" else 7),
            "lat": round(locatie.y, 4 if status == "verdwenen" else 7),
        }
        if punt_nr != nr:  # punt van een ander Nr gebruikt (data/punt_correcties.csv)
            rec["punt_nr_bron"] = punt_nr
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
    tel = {s: sum(1 for r in records.values() if r["status"] == s) for s in ("in_gebruik", "geruimd", "verdwenen")}
    print(f"{len(records)} begraafplaatsen ({', '.join(provincies)}): {tel}")
    print(f"  terreinen gekoppeld: {len(terrein_features)}; zonder terrein (excl. verdwenen): {len(rapport['geen_terrein'])}")
    print(f"  naamvarianten/nabij: {len(rapport['naamvariant'])}; ongeclaimde Joodse polygonen: {len(ongeclaimd)}")
    print(f"  provincie Excel != ruimtelijk: {len(rapport['provincie_afwijkend'])}; correcties: {len(correctie_log)}")

    # Invarianten per provincie (data/invarianten.json). Wijzigt de bron, dan
    # bewust bijwerken -- niet stil laten meebewegen.
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
    assert alle_excel == LANDELIJK_EXCEL_RIJEN, f"Excel heeft {alle_excel} rijen, verwacht {LANDELIJK_EXCEL_RIJEN} (data/invarianten.json)"

    register = controleer_kenmerken(records, provincies)

    # Pas schrijven als alle controles hierboven geslaagd zijn: een afgekeurde
    # run laat de vorige (goedgekeurde) uitvoer staan (review 2026-10-05).
    if register is not None:
        KENMERKEN_JSON.write_text(json.dumps(register, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_outputs(records, list(terrein_features.values()))
    write_rapport(provincies, alle_excel, records, rapport, ongeclaimd, correctie_log)


def write_outputs(records: dict[str, dict], terrein_features: list[dict]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    punten_fc = {
        "type": "FeatureCollection",
        "name": "joodse_begraafplaatsen",
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
        # Geen tijdstempel: dan verandert het rapport alleen als de inhoud verandert
        # (stabiele diffs; review 2026-10-05). Wanneer: zie git log.
        "Gegenereerd door `scripts/build_base_dataset.py`.",
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

    L += ["", "## Verwisselde punten (`data/punt_correcties.csv`)", "",
          "| id | Excel-Nr | punt van Nr | reden |", "|---|---|---|---|"]
    L += [f"| `{i}` | {a} | {b} | {r} |" for i, a, b, r in rapport["punt_correctie"]] or ["| – | – | – | – |"]

    L += ["", f"## Gecorrigeerde terreinen en ingangen ({', '.join(f'`{k.name}`' for k in CORRECTIE_KMZS)})", "",
          "Oud m² is leeg bij een terrein dat niet in de provincie-KMZ stond; gelijk aan nieuw m² als alleen de ingang is nagestuurd.", "",
          "| id | terrein | oud m² | nieuw m² | ingang verschoven |", "|---|---|---|---|---|"]
    L += [f"| `{i}` | {n} | {nl(o) if o is not None else '–'} | {nl(nw)} | {d} m |" for i, n, o, nw, d in rapport["correctie_kmz"]] or ["| – | – | – | – | – |"]

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
