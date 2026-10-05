#!/usr/bin/env python3
"""
Maak een eigen pagina per begraafplaats: site/begraafplaats/<kenmerk>.html
(wens 2026-10-05: vaste adressen voor het boek, printbaar, toegankelijk).

Cloudflare serveert ze zonder ".html": /begraafplaats/jb-loc-366. Het kenmerk
is vast (data/kenmerken.json); voor een vervallen kenmerk komt er een
doorverwijspagina naar het nieuwe kenmerk.

Alleen stdlib: wordt aangeroepen door scripts/build_site.py, ook in de
Cloudflare-build. Alles wordt ge-escaped; links naar buiten alleen naar
bekende bronnen (zelfde lijst als src/js/config.js).
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse

REPO_URL = "https://github.com/jolietjakeblues/joodse-begraafplaatsen"
LINK_DOMEINEN = {"monumentenregister.cultureelerfgoed.nl", "www.dodenakkers.nl", "linkeddata.cultureelerfgoed.nl"}
STATUS = {"in_gebruik": "In gebruik", "geruimd": "Geruimd", "verdwenen": "Verdwenen"}
# Zelfde teksten als RELATIE in src/js/config.js
RELATIE = {
    "op_terrein": "op het terrein",
    "grenst_aan": "grenst aan het terrein",
    "overlapt": "overlapt het terrein",
    "0-25m": "binnen 25 m",
    "25-100m": "25–100 m",
    "100-250m": "100–250 m",
    "net_buiten": "net buiten het terrein",
    "hoort_bij": "hoort bij de begraafplaats",
    "hoort_bij_andere": "hoort bij een andere begraafplaats (de RCE plaatst het hier)",
    "algemene_begraafplaats": "de algemene begraafplaats waar dit deel bij hoort",
}

e = lambda v: escape(str(v), quote=True)  # noqa: E731


def link(url: str | None, tekst: str) -> str:
    """Link naar een bekende bron; anders alleen de tekst."""
    if url and urlparse(url).scheme == "https" and urlparse(url).hostname in LINK_DOMEINEN:
        return f'<a href="{e(url)}">{e(tekst)}</a>'
    return e(tekst)


def pagina_link(bp: dict) -> str:
    return f'<a href="{e(quote(bp["id"]))}">{e(bp["naam"])}</a>, {e(bp.get("plaats") or "")}'


def nl_getal(n) -> str:
    return f"{n:,}".replace(",", ".")


def correctie_url(p: dict) -> str:
    q = {"template": "correctie.yml", "title": f"Correctie: {p['naam']}, {p.get('plaats') or ''}".strip(),
         "kenmerk": p["id"], "naam": ", ".join(x for x in (p["naam"], p.get("plaats")) if x)}
    return f"{REPO_URL}/issues/new?{urlencode(q)}"


def rijen(paren) -> str:
    return "\n".join(f"      <dt>{e(k)}</dt><dd>{v}</dd>" for k, v in paren if v not in (None, ""))


def rijksmonument(p: dict) -> str | None:
    r = p.get("rijksmonument_rce")
    if r and r["soort"] == "complex":
        delen = ", ".join(
            link(o["url"], f"{o['rijksmonumentnummer']}" + (f" ({o['functie'].lower()})" if o.get("functie") else ""))
            for o in r["onderdelen"]
        )
        return f"complex {e(r['nummer'])}" + (f" {e(r['naam'])}" if r.get("naam") else "") + f": {delen}"
    if r:
        return link(r["url"], f"nr. {r['nummer']}")
    return "ja" if p.get("rijksmonument") is True else None


def nabij(p: dict) -> str | None:
    r = p.get("rijksmonument_rce")
    eigen = {r["nummer"], *(o["rijksmonumentnummer"] for o in r["onderdelen"])} if r else set()
    lijst = [x for x in p.get("rijksmonumenten_nabij") or [] if x["afstand_m"] <= 100 and x["rijksmonumentnummer"] not in eigen]
    if not lijst:
        return None
    items = "".join(
        f"<li>{link(x.get('url'), x['rijksmonumentnummer'])} {e((x.get('functie') or '').lower())} "
        f"<span class=\"muted\">{e(RELATIE.get(x['relatie'], x['relatie']))}</span></li>"
        for x in lijst
    )
    return f'<ul class="bp-lijst">{items}</ul>'


def kop(titel: str, beschrijving: str, canonical: str, noindex: bool, extra: str = "") -> str:
    robots = ('  <!-- Niet indexeren: de kaart blijft intern tot het onderzoek is afgerond (René 2026-10-02, vraag F4) -->\n'
              '  <meta name="robots" content="noindex, nofollow" />\n') if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8" />
  <title>{e(titel)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
{robots}  <meta name="description" content="{e(beschrijving)}" />
  <link rel="canonical" href="{e(canonical)}" />
{extra}  <link rel="icon" href="../images/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../pagina.css" />
</head>
"""


def pagina(p: dict, by_id: dict, artikelen: list[dict], site_url: str, noindex: bool) -> str:
    status = STATUS[p["status"]]
    plaats = p.get("plaats") or ""
    jaartal = f"{'ca. ' if p.get('circa') else ''}{p['jaartal']}" if p.get("jaartal") else p.get("jaartal_bron")
    adres = ", ".join(x for x in (" ".join(x for x in (p.get("adres_aanduiding"), p.get("adres")) if x), p.get("postcode")) if x)
    gezicht = "; ".join(f"{g.get('naam') or g.get('gezichtsnummer')} ({'binnen' if g['relatie'] == 'binnen' else 'deels'})" for g in p.get("gezichten") or [])
    naar = "<br>".join(pagina_link(by_id[h["id"]]) for h in p.get("herbegraven_naar") or [] if h["id"] in by_id)
    van = "<br>".join(pagina_link(by_id[h["id"]]) for h in p.get("herbegraven_van") or [] if h["id"] in by_id)
    lees = "<br>".join(link(a["url"], a["titel"]) for a in artikelen)
    ligging = f"{p['lat']:.5f}, {p['lon']:.5f}" + (" (bij benadering)" if p["status"] == "verdwenen" else " (ingang)")
    precisie = ('    <p class="popup-note">Verdwenen: de plek is bij benadering aangegeven.</p>\n' if p["status"] == "verdwenen" else "")
    beschrijving = f"{p['naam']}, {plaats}: Joodse begraafplaats ({status.lower()}), uit de inventarisatie van stichting Dodenakkers."

    gegevens = rijen([
        ("Status", e(status)),
        ("Plaats", e(plaats)),
        ("Gemeente", e(p.get("gemeente") or "")),
        ("Provincie", e(p.get("provincie") or "")),
        ("Adres", e(adres)),
        ("Sinds", e(jaartal) if jaartal else None),
        ("Grootte", f"{nl_getal(p['grootte_m2'])} m²" if p.get("grootte_m2") else (e(p["grootte_bron"]) if p.get("grootte_bron") else None)),
        ("Rijksmonument", rijksmonument(p)),
        ("Metaheerhuis", "aanwezig" if p.get("met") is True else None),
        ("Gemeentelijk monument", "ja" if p.get("gemeentelijk_monument") is True else None),
        ("Monumenten Inventarisatie Project (MIP)", "opgenomen" if p.get("mip") is True else None),
        ("Beschermd deel", e(p["beschermd_deel"]) if p.get("beschermd_deel") else None),
        ("Bijzonderheden", e(p["bijzonderheden"]) if p.get("bijzonderheden") else None),
        ("Overgebracht naar", naar or None),
        ("Herbegraven vanuit", van or None),
        ("Beschermd gezicht", e(gezicht) if gezicht else None),
        ("Rijksmonumenten binnen 100 m", nabij(p)),
        ("Lees op Dodenakkers", lees or None),
        ("Ligging", e(ligging)),
        ("Kenmerk", f"<code>{e(p['id'])}</code>"),
    ])
    return kop(f"{p['naam']}, {plaats} – Joodse Begraafplaatsen", beschrijving, f"{site_url}/begraafplaats/{p['id']}", noindex) + f"""<body class="pagina">
  <a class="skip-link" href="#inhoud">Ga naar de inhoud</a>
  <main id="inhoud" tabindex="-1" class="bp">
    <p><a href="../?id={e(quote(p['id']))}">&larr; Bekijk op de kaart</a> &middot; <a href="../lezen">Lezen</a> &middot; <a href="../statistieken">Statistieken</a> &middot; <a href="../methode">Methode en bronnen</a></p>
    <img src="../images/dodenakkers-logo.webp" alt="Dodenakkers – funerair erfgoed" class="logo" width="480" height="146" />
    <h1>{e(p['naam'])}</h1>
    <p class="bp-status"><span class="sym sym-{e(p['status'])}" aria-hidden="true"></span> {e(status)} · {e(plaats)} · {e(p.get('provincie') or '')}</p>
{precisie}    <dl class="bp-gegevens">
{gegevens}
    </dl>
    <p class="bp-acties"><a href="../?id={e(quote(p['id']))}">Bekijk op de kaart</a> · <a href="{e(correctie_url(p))}">Klopt er iets niet? Correctie doorgeven</a></p>
    <p class="hint bp-bron">Inventarisatie: stichting Dodenakkers. Rijksmonumenten en beschermde gezichten: Rijksdienst voor het Cultureel Erfgoed. Gemeente en provincie: PDOK. Vaste link naar deze pagina: <span class="bp-url">{e(site_url)}/begraafplaats/{e(p['id'])}</span></p>
  </main>
</body>
</html>
"""


def doorverwijzing(oud: str, naar: str | None, by_id: dict, site_url: str, noindex: bool) -> str:
    if naar:
        doel = by_id[naar]
        extra = f'  <meta http-equiv="refresh" content="0; url={e(quote(naar))}" />\n'
        tekst = f'<p>Deze begraafplaats heeft een nieuw kenmerk. Je wordt doorgestuurd naar {pagina_link(doel)}.</p>'
    else:
        extra = ""
        tekst = '<p>Deze begraafplaats staat niet meer in de inventarisatie. <a href="../">Naar de kaart</a>.</p>'
    return kop(f"{oud} – Joodse Begraafplaatsen", "Doorverwijzing naar een nieuw kenmerk.", f"{site_url}/begraafplaats/{naar or oud}", noindex, extra) + f"""<body class="pagina">
  <main id="inhoud" tabindex="-1">
    <h1>Kenmerk {e(oud)}</h1>
    {tekst}
  </main>
</body>
</html>
"""


def bouw(repo_root: Path, site_dir: Path, site_url: str, noindex: bool) -> list[str]:
    """Schrijft de pagina's; geeft de paden (zonder .html) terug voor de sitemap."""
    gen = repo_root / "data" / "generated"
    punten = [f["properties"] for f in json.loads((gen / "begraafplaatsen.geojson").read_text(encoding="utf-8"))["features"]]
    by_id = {p["id"]: p for p in punten}
    artikelen: dict[str, list[dict]] = {}
    for a in json.loads((gen / "leeslijst.json").read_text(encoding="utf-8"))["artikelen"]:
        for i in a.get("popup_ids") or []:
            artikelen.setdefault(i, []).append(a)
    register = json.loads((repo_root / "data" / "kenmerken.json").read_text(encoding="utf-8"))

    doel = site_dir / "begraafplaats"
    doel.mkdir(parents=True, exist_ok=True)
    paden = []
    for p in punten:
        (doel / f"{p['id']}.html").write_text(pagina(p, by_id, artikelen.get(p["id"], []), site_url, noindex), encoding="utf-8")
        paden.append(f"begraafplaats/{p['id']}")
    for oud, v in register["vervallen"].items():
        (doel / f"{oud}.html").write_text(doorverwijzing(oud, v.get("naar"), by_id, site_url, noindex), encoding="utf-8")
    return paden
