# Werkafspraken Joodse Begraafplaatsen (voor AI-sessies)

Lees dit en `docs/` (01-data-analyse, 02-project-analyse, 03-planning, 04-vragen-dodenakkers) vóór je iets wijzigt. Algemene werkwijze en lessen: skill `dodenakkers`.

## Opdracht
Opdrachtgever: stichting Dodenakkers. Eén kaart met alle Joodse begraafplaatsen van Nederland, inclusief geruimd en verdwenen. Gestart 2026-10-02 met Zuid-Holland; daarna per provincie. **Stand: West-Nederland klaar** (ZH, Utrecht, NH, Zeeland, Flevoland — 91 begraafplaatsen).

Live: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev

## Besluiten (2026-10-02)
- Eigen project, los van dodenakkers-zh. Inbedbaar op dodenakkers.nl (`?embed=1`, CSP `frame-ancestors`, CORS op `/data/*`).
- Titel "Joodse Begraafplaatsen"; logo Dodenakkers.
- Statussen op de kaart: **Bestaand** (Excel "In gebruik") / **Geruimd** / **Verdwenen**. Kleur + vorm (kleurenblind-veilig, reviewer René): bestaand `#0072B2` ● · geruimd `#E69F00` ◆ · verdwenen `#3A3A3A` ○.
- Verdwenen: plek **bij benadering**. Geen terrein, geen afstandsrelaties.
- Contextlagen: provincie- en gemeentegrenzen, beschermde gezichten (hele provincie), rijksmonumenten gebouwd én archeologisch — **beide alleen ≤ 100 m** van een bestaande/geruimde begraafplaats. **Geen** archeologische onderzoeksgebieden, geen CHS. Aantal per laag naast de laagnaam.
- Ondergronden zoals dodenakkers-zh: PDOK grijs, luchtfoto, BGT (≥ z17), BRK-percelen als overlay (≥ z17).
- Popup: eigenaar en postadres mogen; `NA` (bij/tegenover) vóór het adres; `Met` = metaheerhuis (huisje-icoon); `MIP` = Monumenten Inventarisatie Project.
- Hosting: Worker met static assets (`wrangler.jsonc`, assets = `site/`); deploy `python scripts/build_site.py && npx wrangler deploy`. Domein op één plek: `SITE_URL` in `scripts/build_site.py`.
- Mobiel is een eis: paneel dicht + mini-legenda, aanraakdoelen ~44 px, testen op 375 px.

## Pipeline (zie README)
`fetch_pdok.py` → `build_base_dataset.py --provincie …` → `fetch_rce.py --provincie …` → `analyse_spatial.py` → `make_og_image.py` → `build_site.py` → `wrangler deploy`.
Draai `build_base_dataset.py` altijd met **alle** provincies die op de kaart moeten (de output wordt overschreven).

## Correctielagen (nooit de bron wijzigen)
- `data/corrections.csv` — veldcorrecties (id, veld, waarde, reden, datum, bron).
- `data/terrein_koppelingen.csv` — handmatige terreinkoppeling als de naamtoets faalt (nu: Vlissingen `jb-loc-9`).
- `INVARIANTEN` in `build_base_dataset.py` — gecontroleerde tellingen per provincie.

## Niet doen
- Nooit `Nr` opzoeken zonder reeks; nooit Joods-zijn afleiden uit een trefwoord in de naam.
- Nooit een terrein koppelen op naam alleen of op ligging alleen; nooit aan de algemene begraafplaats ernaast hangen.
- Nooit het tabblad "Dank en informeren" inlezen.
- Geen asserts stil aanpassen: wijzigt een telling, dan uitzoeken en benoemen.
- Geen tekstlabels in MapLibre (vereist externe glyph-server, botst met CSP).
- Niet committen/pushen: de gebruiker doet dat zelf.

## Open vragen
Allemaal in [docs/04-vragen-dodenakkers.md](docs/04-vragen-dodenakkers.md) (A: bronbestanden, B: specifieke begraafplaatsen, C: inhoud, D: René/kleuren, E: layout, F: werkwijze). Antwoorden verwerken via de correctielagen en daar de vraagcode als `bron` noemen.
