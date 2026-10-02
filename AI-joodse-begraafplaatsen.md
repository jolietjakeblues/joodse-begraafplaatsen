# Werkafspraken Joodse Begraafplaatsen (voor AI-sessies)

Lees dit en `docs/` (01-data-analyse, 02-project-analyse, 03-planning) vóór je iets wijzigt. Algemene werkwijze: skill `dodenakkers`.

## Opdracht
Opdrachtgever: stichting Dodenakkers. Eén kaart met alle Joodse begraafplaatsen van Nederland, inclusief geruimd en verdwenen. Gestart 2026-10-02 met Zuid-Holland; daarna per provincie.

## Besluiten (2026-10-02)
- Contextlagen: provincie- en gemeentegrenzen, rijksmonumenten (gebouwd én archeologisch), beschermde gezichten. **Geen** archeologische onderzoeksgebieden, geen CHS.
- Eigen project en eigen Cloudflare Pages-project, los van dodenakkers-zh. Moet inbedbaar zijn op de website van Dodenakkers (`?embed=1`, `frame-ancestors`, CORS op data).
- Titel: "Joodse Begraafplaatsen"; logo Dodenakkers.
- Verdwenen: plek **bij benadering** (vermoedelijk uit archiefonderzoek). Geen terrein, geen afstandsrelaties.
- Kleuren (kleurenblind-veilig, reviewer René): bestaand `#0072B2` ● · geruimd `#E69F00` ◆ · verdwenen `#3A3A3A` ○. Vorm is altijd een tweede drager naast kleur.
- Eigenaar en postadres mogen in de popup.
- Rijksmonumenten (gebouwd) alleen binnen **100 m** van een bestaande/geruimde begraafplaats, één bestand per provincie (`data/rce/index.json`). Archeologische RM ook alleen ≤ 100 m (besluit 2026-10-02, ZH: 0); gezichten: hele provincie. Aantallen per laag staan in het manifest en naast de laagnaam.
- Ondergronden zoals dodenakkers-zh: PDOK grijs, luchtfoto, BGT (vanaf z17) en BRK-percelen als overlay (vanaf z17).
- Hosting: Wrangler 4.147 maakte van `pages project create` een **Worker met static assets** (`wrangler.jsonc`, assets = `site/`). Live: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev. Deploy: `python scripts/build_site.py && npx wrangler deploy`. `_headers` werkt daar ook.

## Niet doen
- Nooit `Nr` opzoeken zonder reeks; nooit Joods-zijn afleiden uit een trefwoord in de naam.
- Nooit een terrein koppelen op naam alleen of op ligging alleen.
- Nooit de bron wijzigen; correcties via `data/corrections.csv`.
- Nooit het tabblad "Dank en informeren" inlezen.
- Geen asserts stil aanpassen: wijzigt een telling, dan uitzoeken en benoemen.
- Geen tekstlabels in MapLibre (vereist externe glyph-server, botst met CSP).

## Open vragen voor Dodenakkers
- Kloppen de nummerreeksen (loc/ver/ger) zoals hier gebruikt?
- Naamsvarianten in het koppelrapport: spelvarianten of verschillende objecten?
- Betekenis van de kolommen `Muur` en `Kadaster` (nog navragen). Bekend: `NA` = nadere aanduiding ("bij"/"tegenover"), `MIP` = Monumenten Inventarisatie Project, `Met` = metaheerhuis(je) aanwezig (opdrachtgever, nog bevestigen bij Leon).
- Rmon bevat soms een complexnummer (Gorinchem 525108, Wassenaar 524542 = complex "Begraafplaats Kerkehout"): bedoeld?
