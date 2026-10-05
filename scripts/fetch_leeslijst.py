#!/usr/bin/env python3
"""
Haal de leeslijst op: alle artikelen op dodenakkers.nl met de tag
"Joodse begraafplaats" (https://www.dodenakkers.nl/tag/joodse-begraafplaats.html).

Alleen titel, URL en rubriek (uit het URL-pad) worden overgenomen -- geen
artikeltekst. De lezer gaat voor de inhoud naar dodenakkers.nl.

Per artikel over een plaats wordt gekeken of die plaats op de kaart staat
(data/generated/begraafplaatsen.geojson). Zo ja, dan krijgt het artikel een
kaartpositie voor de link "Bekijk op de kaart" (de best passende
begraafplaats), plus de kenmerken van alle begraafplaatsen in die plaats
(`plaats_ids`) zodat de kaartpopup naar het artikel kan verwijzen. Dat is een
gemak, geen koppeling in de data: het artikel kan meerdere begraafplaatsen in
die plaats behandelen.

Geen uitgelichte artikelen meer (wens opdrachtgever 2026-10-05): alles staat
in de gewone lijst. Draai na elke nieuwe provincie opnieuw.

Output: data/generated/leeslijst.json

Opnieuw draaien houdt de lijst actueel; daarna scripts/build_site.py.
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
BASIS = "https://www.dodenakkers.nl"
TAG_URL = f"{BASIS}/tag/joodse-begraafplaats.html?limit=0"
OUT = REPO_ROOT / "data" / "generated" / "leeslijst.json"

# URL-padsegment -> provincie (zoals in PDOK / de Excel)
PROVINCIE_PAD = {
    "begraafplaatsen-in-zuid-holland": "Zuid-Holland",
    "begraafplaatsen-in-noord-holland": "Noord-Holland",
    "begraafplaatsen-in-utrecht": "Utrecht",
    "begraafplaatsen-in-zeeland": "Zeeland",
    "begraafplaatsen-in-groningen": "Groningen",
    "begraafplaatsen-in-overijssel": "Overijssel",
    "begraafplaatsen-in-noord-brabant": "Noord-Brabant",
    "begraafplaatsen-in-limburg": "Limburg",
    "gelderland": "Gelderland",
    "drenthe": "Drenthe",
    "fryslan": "Fryslân",
    "flevoland": "Flevoland",
}
RUBRIEK_PAD = {"grafpoezie": "Grafpoëzie", "extra-s": "Extra's", "oorlog": "Oorlog", "algemeen": "Algemeen"}


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def plaats_uit_titel(titel: str) -> str | None:
    """"Dordrecht - Joodse begraafplaats(en)" -> "Dordrecht"; "Groet/Schoorl - …" -> "Groet/Schoorl"."""
    m = re.match(r"^(.+?)\s+[-–]\s+", titel)
    return m.group(1).strip() if m else None


def kaartposities() -> dict[str, list[dict]]:
    """genormaliseerde plaats/gemeente -> begraafplaatsen op de kaart in die plaats."""
    path = REPO_ROOT / "data" / "generated" / "begraafplaatsen.geojson"
    pos: dict[str, list[dict]] = {}
    for f in json.loads(path.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        # Ook de plaats uit het puntlabel ("Joodse begraafplaats, Den Nul" heeft
        # in de Excel Olst als plaats).
        label_plaats = p["label_punt"].rsplit(",", 1)[1].strip() if p.get("label_punt") and "," in p["label_punt"] else None
        for naam in {p.get("plaats"), p.get("gemeente"), label_plaats} - {None}:
            pos.setdefault(norm(naam), []).append(p)
    return pos


def op_naam(woord: str) -> list[dict]:
    """Begraafplaatsen waarvan de naam het woord als los woord bevat
    ("Tacozijl" in "Joadetsjerkhof bij Tacozijl"; de plaats is daar Lemmer)."""
    path = REPO_ROOT / "data" / "generated" / "begraafplaatsen.geojson"
    w = norm(woord)
    uit = []
    for f in json.loads(path.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        namen = " ".join(norm(n) for n in [p.get("naam"), p.get("label_punt"), p.get("terrein_naam_kml")] if n)
        if w and f" {w} " in f" {namen} ":
            uit.append(p)
    return uit


def beste_begraafplaats(titel: str, kandidaten: list[dict]) -> dict:
    """Bij meerdere begraafplaatsen in een plaats: de naam die het meest op de
    artikeltitel lijkt."""
    t = norm(titel)
    voorkeur = "verdwenen" if "verdwenen" in t else "in_gebruik"
    def naamscore(p):
        namen = [p.get("naam"), p.get("naam_bron"), p.get("label_punt"), p.get("terrein_naam_kml")]
        return max(difflib.SequenceMatcher(None, t, norm(n)).ratio() for n in namen if n)
    beste = max(naamscore(p) for p in kandidaten)
    # Bijna gelijke namen (verschil < 0.1): de status uit de titel gaat voor
    # ("De verdwenen ..."), anders de bestaande begraafplaats.
    bijna = [p for p in kandidaten if naamscore(p) >= beste - 0.1]
    p = max(bijna, key=lambda p: (p["status"] == voorkeur, naamscore(p)))
    return {"lon": p["lon"], "lat": p["lat"], "id": p["id"], "naam": p["naam"]}


def main() -> None:
    r = requests.get(TAG_URL, timeout=60, headers={"User-Agent": "joodse-begraafplaatsen-kaart (leeslijst)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tabel = soup.select_one("table.com-tags-tag-list__category")
    assert tabel, "tabel met getagde artikelen niet gevonden -- is de opbouw van dodenakkers.nl veranderd?"

    posities = kaartposities()

    artikelen = []
    for a in tabel.select("tr th.list-title a[href]"):
        url = BASIS + a["href"] if a["href"].startswith("/") else a["href"]
        # Alleen artikelen op dodenakkers.nl zelf (geen javascript:/externe links in de pagina).
        if not url.startswith(BASIS + "/"):
            print(f"overgeslagen (geen dodenakkers.nl-link): {url[:80]}")
            continue
        titel = a.get_text(" ", strip=True)
        delen = a["href"].strip("/").split("/")
        provincie = next((PROVINCIE_PAD[d] for d in delen if d in PROVINCIE_PAD), None)
        rubriek = None if provincie else next((RUBRIEK_PAD[d] for d in delen if d in RUBRIEK_PAD), "Overig")
        plaats = plaats_uit_titel(titel)
        kaart, plaats_ids = None, []
        if plaats:
            for kandidaat in [plaats, *plaats.split("/")]:
                if norm(kandidaat) in posities:
                    kaart = beste_begraafplaats(titel, posities[norm(kandidaat)])
                    plaats_ids = sorted({p["id"] for p in posities[norm(kandidaat)]})
                    break
            else:
                treffers = op_naam(plaats)
                if treffers:
                    kaart = beste_begraafplaats(titel, treffers)
                    plaats_ids = sorted({p["id"] for p in treffers})
        artikelen.append({
            "titel": titel,
            "url": url,
            "provincie": provincie,
            "rubriek": rubriek,
            "plaats": plaats,
            "kaart": kaart,
            "plaats_ids": plaats_ids,
            # Popup-verwijzing: titel over meerdere begraafplaatsen ("begraafplaatsen",
            # "begraafplaats(en)") -> alle in die plaats; anders alleen de best passende.
            "popup_ids": plaats_ids if re.search(r"begraafplaatsen|\(en\)", titel, re.I) else ([kaart["id"]] if kaart else []),
        })

    assert artikelen, "geen artikelen gevonden"
    out = {
        "bron": TAG_URL.split("?")[0],
        "opgehaald": datetime.now(timezone.utc).isoformat(),
        "artikelen": artikelen,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    met_kaart = sum(1 for x in artikelen if x["kaart"])
    print(f"{len(artikelen)} artikelen -> {OUT.relative_to(REPO_ROOT)} ({met_kaart} met link naar de kaart)")


if __name__ == "__main__":
    main()
