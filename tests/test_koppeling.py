"""
Tests voor de koppelregels en controles (review 2026-10-05).

Draaien:  python -m unittest discover -s tests -v

Gebruikt geen bronbestanden (data-dodenakkers/): de terreinen zijn kleine
vierkanten rond een punt in Nederland. De gevallen komen uit de praktijk
(Rijswijk, Ouderkerk, Enschede, Uithuizen), zie docs/01-data-analyse.md.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from shapely.geometry import Point, box
from shapely.ops import transform
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import analyse_spatial as an  # noqa: E402
import build_base_dataset as b  # noqa: E402
import check_data  # noqa: E402

LON, LAT = 5.0, 52.0  # ergens in Utrecht


def terrein(naam: str, half_deg: float, dlon: float = 0.0) -> dict:
    """Vierkant terrein rond (LON + dlon, LAT); half_deg = halve zijde in graden."""
    g = box(LON + dlon - half_deg, LAT - half_deg, LON + dlon + half_deg, LAT + half_deg)
    return {"naam": naam, "geom": g, "rd": transform(b.to_rd, g), "bron": "test"}


def koppel(punt: Point, labels: list[str], terreinen: list[dict], handmatig: dict | None = None):
    tree = STRtree([t["rd"] for t in terreinen])
    return b.koppel_terrein(punt, labels, terreinen, tree, handmatig)


class Naamtoets(unittest.TestCase):
    def test_plaats_na_laatste_komma(self):
        self.assertEqual(b.split_plaats("Joodse begraafplaats, Den Haag"), ("Joodse begraafplaats", " Den Haag"))
        self.assertEqual(b.split_plaats("Joodse begraafplaats. Almere"), ("Joodse begraafplaats", "Almere"))

    def test_generieke_woorden_tellen_niet(self):
        # "Gem. begraafplaats Eikelenburg" mag niet op "Liberaal Joodse begraafplaats" lijken
        r = b.name_ratio("Liberaal Joodse begraafplaats, Rijswijk", "Gem. begraafplaats Eikelenburg, Rijswijk")
        self.assertLess(r, b.NAAM_MIN_RATIO)

    def test_kernwoorden_van_terrein_in_excel_naam(self):
        # Ouderkerk: terrein "Beth Haim", Excel-naam "Portugees Isr. begraafplaats Beth Haim"
        r = b.name_ratio("Portugees Isr. begraafplaats Beth Haim, Ouderkerk aan de Amstel", "Beth Haim")
        self.assertGreaterEqual(r, b.NAAM_MIN_RATIO)

    def test_synoniem_israelitisch_joods_faalt_bewust(self):
        # Enschede: bekende beperking -> oplossing is data/terrein_koppelingen.csv, niet de drempel
        r = b.name_ratio("Israelitische begraafplaats, Enschede", "Nw. Joodse begraafplaats, Enschede")
        self.assertLess(r, b.NAAM_MIN_RATIO)


class TerreinKoppeling(unittest.TestCase):
    punt = Point(LON, LAT)

    def test_genest_kleinste_wint(self):
        # Rijswijk: Joods deel ligt binnen de algemene begraafplaats
        groot = terrein("Joodse begraafplaats Oud-Rijswijk, Rijswijk", 0.002)
        klein = terrein("Joods deel op Oud Rijswijk, Rijswijk", 0.0002)
        t, wijze, _ = koppel(self.punt, ["Joods deel begraafplaats Oud-Rijswijk, Rijswijk"], [groot, klein])
        self.assertIs(t, klein)
        self.assertTrue(wijze.startswith("binnen"))

    def test_naam_alleen_op_ligging_is_niet_genoeg(self):
        alg = terrein("RK begraafplaats St. Laurentius, Rotterdam", 0.001)
        t, wijze, _ = koppel(self.punt, ["Portugees Israëlitische Begraafplaats Crooswijk, Rotterdam"], [alg])
        self.assertIsNone(t)
        self.assertEqual(wijze, "geen_terrein")

    def test_binnen_gaat_voor_nabij_valkuil_uithuizen(self):
        # Punt ligt in de algemene begraafplaats die toevallig de naamtoets haalt
        # ("joodse" ~ "oude"), en net naast het Joodse terrein. Zonder handmatige
        # koppeling wint de algemene: dit test dat de valkuil bestaat ...
        alg = terrein("Oude alg. begraafplaats, Uithuizen", 0.002)
        joods = terrein("Joodse begraafplaats, Uithuizen", 0.00005, dlon=0.00008)
        labels = ["Joodse begraafplaats, Uithuizen?"]
        t, _, _ = koppel(self.punt, labels, [alg, joods])
        self.assertIs(t, alg)
        # ... en dat de handmatige koppeling hem oplost.
        t, wijze, _ = koppel(self.punt, labels, [alg, joods], {"terrein_naam": "Joodse begraafplaats, Uithuizen"})
        self.assertIs(t, joods)
        self.assertEqual(wijze, "handmatig")

    def test_handmatig_te_ver_weg_faalt(self):
        ver = terrein("Joodse begraafplaats, Elders", 0.0001, dlon=0.01)  # ~700 m
        with self.assertRaises(AssertionError):
            koppel(self.punt, ["x, y"], [ver], {"terrein_naam": "Joodse begraafplaats, Elders"})


class Waarden(unittest.TestCase):
    def test_ja_nee_geen_is_nee(self):
        self.assertIs(b.ja_nee("Geen"), False)
        self.assertIs(b.ja_nee("Ja"), True)
        self.assertEqual(b.ja_nee("onbekend"), "onbekend")

    def test_bijzonderheden_getal_wordt_tekst(self):
        self.assertEqual(b.as_text(-1883.0), "-1883")

    def test_correcties_getypt_en_bron_bewaard(self):
        recs = {"jb-loc-1": {"id": "jb-loc-1", "rijksmonument": False, "rijksmonumentnummer": None, "naam": "Oud"}}
        b.apply_corrections(recs, [
            {"id": "jb-loc-1", "veld": "rijksmonument", "waarde": "ja", "reden": "t", "datum": "d", "bron": "b"},
            {"id": "jb-loc-1", "veld": "rijksmonumentnummer", "waarde": "516689", "reden": "t", "datum": "d", "bron": "b"},
            {"id": "jb-loc-1", "veld": "naam", "waarde": "Nieuw", "reden": "t", "datum": "d", "bron": "b"},
        ])
        r = recs["jb-loc-1"]
        self.assertIs(r["rijksmonument"], True)
        self.assertEqual(r["rijksmonumentnummer"], 516689)
        self.assertEqual((r["naam"], r["naam_bron"]), ("Nieuw", "Oud"))

    def test_rce_functie_zonder_haakjes(self):
        for ruw, kort in [("Woonhuis(K)", "Woonhuis"), ("Boerderij (M1)", "Boerderij"), ("Muur(D)", "Muur"),
                          ("Gedenkteken(D6)", "Gedenkteken"), ("Begraafplaats en -onderdelen", "Begraafplaats en -onderdelen"),
                          (None, None), ("", "")]:
            self.assertEqual(an.functie_kort(ruw), kort, ruw)


class DataControle(unittest.TestCase):
    """check_data.check() moet fouten vinden in kleine, opzettelijk kapotte datasets."""

    def maak(self, punten, terreinen=(), lijnen=(), inv=None):
        tmp = Path(tempfile.mkdtemp())
        gen = tmp / "data" / "generated"
        gen.mkdir(parents=True)
        fc = lambda feats: {"type": "FeatureCollection", "features": list(feats)}  # noqa: E731
        (gen / "begraafplaatsen.geojson").write_text(json.dumps(fc(
            {"type": "Feature", "properties": p, "geometry": {"type": "Point", "coordinates": [p.pop("_lon", 5.0), 52.0]}}
            for p in punten)), encoding="utf-8")
        (gen / "terreinen.geojson").write_text(json.dumps(fc({"properties": {"id": i}} for i in terreinen)), encoding="utf-8")
        (gen / "herbegravingen.geojson").write_text(json.dumps(fc({"properties": l} for l in lijnen)), encoding="utf-8")
        (gen / "leeslijst.json").write_text(json.dumps({"artikelen": []}), encoding="utf-8")
        provs = sorted({p["provincie"] for p in punten})
        (gen / "statistieken.json").write_text(json.dumps({"basis": {"totaal": len(punten)}, "provincies_op_kaart": provs}), encoding="utf-8")
        (tmp / "data" / "invarianten.json").write_text(json.dumps({"provincies": inv or {}}), encoding="utf-8")
        oud = (check_data.REPO_ROOT, check_data.GEN)
        check_data.REPO_ROOT, check_data.GEN = tmp, gen
        try:
            return check_data.check()
        finally:
            check_data.REPO_ROOT, check_data.GEN = oud

    INV = {"Utrecht": {"totaal": 2, "in_gebruik": 1, "geruimd": 0, "verdwenen": 1, "terreinen": 1}}

    def punten(self):
        return [{"id": "jb-loc-1", "status": "in_gebruik", "provincie": "Utrecht"},
                {"id": "jb-ver-1", "status": "verdwenen", "provincie": "Utrecht"}]

    def test_goede_data(self):
        self.assertEqual(self.maak(self.punten(), ["jb-loc-1"], inv=self.INV), [])

    def test_afwijkende_telling(self):
        fouten = self.maak(self.punten(), [], inv=self.INV)
        self.assertTrue(any("Utrecht: verwacht" in f for f in fouten), fouten)

    def test_terrein_bij_verdwenen(self):
        inv = {"Utrecht": {**self.INV["Utrecht"], "terreinen": 2}}
        fouten = self.maak(self.punten(), ["jb-loc-1", "jb-ver-1"], inv=inv)
        self.assertTrue(any("verdwenen" in f for f in fouten), fouten)

    def test_herbegraving_naar_onbekend(self):
        fouten = self.maak(self.punten(), ["jb-loc-1"], [{"van_id": "jb-ver-1", "naar_id": "jb-loc-999"}], inv=self.INV)
        self.assertTrue(any("jb-loc-999" in f for f in fouten), fouten)

    def test_persoonsgegevens_geweigerd(self):
        p = self.punten()
        p[0]["eigenaar"] = "Iemand"
        fouten = self.maak(p, ["jb-loc-1"], inv=self.INV)
        self.assertTrue(any("persoonsgegevens" in f for f in fouten), fouten)

    def test_coordinaat_buiten_nederland(self):
        p = self.punten()
        p[0]["_lon"] = 12.0
        fouten = self.maak(p, ["jb-loc-1"], inv=self.INV)
        self.assertTrue(any("buiten Nederland" in f for f in fouten), fouten)


if __name__ == "__main__":
    unittest.main()
