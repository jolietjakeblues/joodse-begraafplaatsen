# Werkafspraken Joodse Begraafplaatsen (voor AI-sessies)

Lees dit en `docs/` (01-data-analyse, 02-project-analyse, 03-planning, 04-vragen-dodenakkers) vóór je iets wijzigt. Algemene werkwijze en lessen: skill `dodenakkers`.

## Opdracht
Opdrachtgever: stichting Dodenakkers. Eén kaart met alle Joodse begraafplaatsen van Nederland, inclusief geruimd en verdwenen. Gestart 2026-10-02 met Zuid-Holland, daarna per provincie. **Stand 2026-10-05: heel Nederland** — alle 12 provincies, alle 315 begraafplaatsen uit de inventarisatie (239 in gebruik, 7 geruimd, 69 verdwenen).

AVG: de git-geschiedenis is op 2026-10-05 herschreven (eigenaarsgegevens en auteursnaam verwijderd). Nooit persoonsgegevens committen; ook niet in tussenversies.

Live (nog niet openbaar, `noindex`): https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev — de site wordt later bij een boek gepubliceerd.

## Besluiten
- Eigen project, los van dodenakkers-zh. Inbedbaar op dodenakkers.nl (`?embed=1`, CSP `frame-ancestors`, CORS op `/data/*`); later mogelijk op funerair-erfgoed.nl, alleen via eigen sites (E8).
- Titel "Joodse Begraafplaatsen"; logo Dodenakkers (`src/images/dodenakkers-logo.webp`); huisstijlkleur `#8d161c` alleen voor vormgeving, nooit als datakleur.
- Statussen op de kaart: **In gebruik** / **Geruimd** / **Verdwenen** (A4/E3: Joodse begraafplaatsen worden niet gesloten). Kleur + vorm (kleurenblind-veilig, reviewer René): in gebruik `#0072B2` ● · geruimd `#E69F00` ◆ · verdwenen `#3A3A3A` ○. Harde contrasten, geen lichte vlakvullingen (D1).
- Verdwenen: plek **bij benadering**. Geen terrein, geen afstandsrelaties.
- Contextlagen: provincie- en gemeentegrenzen, beschermde gezichten (hele provincie), rijksmonumenten gebouwd én archeologisch — **beide alleen ≤ 100 m** van een begraafplaats in gebruik of geruimd. **Geen** archeologische onderzoeksgebieden, geen CHS. Aantal per laag naast de laagnaam. Laag "Herbegravingen" (lijnen van oud naar nieuw).
- Ondergronden zoals dodenakkers-zh: PDOK grijs, luchtfoto, BGT (≥ z17), BRK-percelen als overlay (≥ z17).
- Popup: `NA` = nader adres ("to" = tegenover) vóór het adres; `Met` = metaheerhuis (huisje-icoon); `MIP` = Monumenten Inventarisatie Project; herbegravingen (beide richtingen); "Lees op Dodenakkers" (artikelen); link "Correctie doorgeven". **Niet** tonen én niet in de open data: eigenaar/postadres, grondvorm, muur, kadaster, laatste bezoek (C1/C2). Geen foto's (C5).
- Datering: vóór 1700 · 1700–1799 · 1800–1849 · 1850–1899 · 1900–1949 · 1950–heden (C9).
- Pagina's: kaart, `lezen` (artikelen, geen uitgelicht-blok), `statistieken` (E7), `methode`.
- Correcties van Dodenakkers: GitHub-issueformulier `.github/ISSUE_TEMPLATE/correctie.yml` (label `correctie`); popuplink vult kenmerk en naam in (F1). Verwerken via de correctielagen, PR met "Closes #nr".
- Hosting: Worker met static assets (`wrangler.jsonc`, assets = `site/`). **Deploy alleen via merge op `main`** (Cloudflare Workers Builds: build `python3 scripts/build_site.py`, deploy `npx wrangler deploy`; zie README). Niet handmatig deployen vanuit een werkmap. Domein op één plek: `SITE_URL` in `scripts/build_site.py`.
- Mobiel is een eis: paneel dicht + mini-legenda, aanraakdoelen ~44 px, testen op 375 px. Mobiele CSS staat achteraan in `style.css`.
- Toegankelijkheid: springlink opent het paneel en zet de focus (ook op lezen/methode/statistieken/404); filtertellingen gelden binnen alle overige actieve filters; na sluiten van een popup gaat de focus terug naar waar hij vandaan kwam (of de menuknop); geruimd-ruit en -terreinrand donkerbruin `#8a5a00` (contrast ≥ 3:1); kleinste tekst 12 px.
- Links naar buiten alleen naar bekende domeinen (`link()` in app.js; leeslijst alleen dodenakkers.nl).
- RCE-functies zonder code tussen haakjes ("Woonhuis(K)" → "Woonhuis"); ruwe waarde in `functie_bron`.
- Verdwenen begraafplaatsen: coördinaten op 4 decimalen (~10 m) in de open data.
- Publicatie: één schakelaar `PUBLICEREN` in `scripts/build_site.py` (nu `False`).

## Pipeline (zie README)
`fetch_pdok.py` → `build_base_dataset.py --alle` → `fetch_rce.py --provincie …` → `analyse_spatial.py` → `fetch_leeslijst.py` → `compute_statistics.py` → `make_og_image.py` → `build_site.py` (draait eerst `check_data.py`).
- Tests: `python -m unittest discover -s tests -v` (koppelregels, correcties, datacontrole). Draaien vóór elke PR.
- Rapporten en data zijn stabiel: geen tijdstempels, vaste sortering; een tweede run verandert niets.
- `build_base_dataset.py` controleert eerst (invarianten, ongekoppelde Joodse terreinen, 315 Excel-rijen) en schrijft pas daarna; een afgekeurde run laat de vorige uitvoer staan.
- `check_data.py` (stdlib) controleert de gecommitte viewerdata; `build_site.py` stopt bij een fout, dus ook de Cloudflare-build deployt dan niet.
- Leespagina: alleen titels en links van dodenakkers.nl, nooit artikeltekst. `popup_ids` bepaalt bij welke begraafplaatsen een artikel in de popup staat.

## Correctielagen (nooit de bron wijzigen)
- `data/corrections.csv` — veldcorrecties (id, veld, waarde, reden, datum, bron); de oorspronkelijke waarde blijft bewaard als `<veld>_bron`.
- `data/terrein_koppelingen.csv` — handmatige terreinkoppeling als de naamtoets faalt (Vlissingen, Enschede 2×, Leens, Uithuizen, Emmen).
- `data/herbegravingen.csv` — herbegravingen (van_id, naar_id, tekst uit de bron, toelichting); alleen als de bestemming eenduidig is.
- `data-dodenakkers/funerair_nieuwedata.kmz` — door Dodenakkers nagestuurde terreinen + ingangen; vervangt het terrein met dezelfde naam (Venlo oud, Dedemsvaart).
- `data/geen_terrein_bevestigd.csv` en `BEOORDEELDE_RELATIES` (analyse_spatial.py) — elk met bron en vraagcode.
- `data/invarianten.json` — gecontroleerde tellingen per provincie, met toelichting.

## Niet doen
- Nooit `Nr` opzoeken zonder reeks; nooit Joods-zijn afleiden uit een trefwoord in de naam.
- Nooit een terrein koppelen op naam alleen of op ligging alleen; nooit aan de algemene begraafplaats ernaast hangen (let op: "binnen gaat voor nabij" kan een algemene begraafplaats kiezen, zie Uithuizen).
- Nooit het tabblad "Dank en informeren" inlezen.
- Geen invarianten of drempels stil aanpassen: wijzigt een telling, dan uitzoeken en benoemen.
- Geen tekstlabels in MapLibre (vereist externe glyph-server, botst met CSP).
- Niet voorstellen om RCE te doorzoeken op Joodse begraafplaatsen buiten de Excel (Leon heeft dat al gedaan).
- Niet committen/pushen: de gebruiker doet dat zelf.

## Open vragen
Allemaal in [docs/04-vragen-dodenakkers.md](docs/04-vragen-dodenakkers.md) en op de gedeelde vragenpagina. Nu open: R1 (namen), R2 (Denekamp), R3 (gecorrigeerde Excel, incl. rest van Putte), Gr1 (Loppersum), Dr1 (Emmen), P1 (licentie en hergebruik bij publicatie), E8 (later). Antwoorden verwerken via de correctielagen en daar de vraagcode als `bron` noemen.
