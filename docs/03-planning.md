# 03 – Planning Joodse begraafplaatsen (start: Zuid-Holland)

Opdracht (Leon / Dodenakkers): één kaart met alle Joodse begraafplaatsen van Nederland, inclusief verdwenen en geruimd. We bouwen het eerst voor Zuid-Holland en zorgen dat de pipeline per provincie uitbreidbaar is.

Stand 2026-10-02: fase 0–4 klaar; live op https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev (review Leon/René volgt).

## Fase 0 – Fundament ✅
- [x] Repo (bestond al, remote `jolietjakeblues/joodse-begraafplaatsen`), `.gitignore` (data-dodenakkers/ buiten git), `requirements.txt`, `LICENSE` (CC BY 4.0)
- [x] `AI-joodse-begraafplaatsen.md` (werkafspraken), `README.md`
- [x] Mapstructuur: `scripts/`, `data/{generated,pdok,rce}/`, `data/corrections.csv`, `queries/rce/`, `src/`, `docs/`

## Fase 1 – Basisdataset Zuid-Holland ✅
- [x] `scripts/build_base_dataset.py`: Excel (alleen tabblad *Joodse begraafplaatsen*) + Locaties/Verdwenen/Geruimd + provincie-KMZ (stdlib zipfile + ElementTree)
- [x] Sleutel `jb-<loc|ver|ger>-<Nr>`; asserts uniek en "elke rij vindt een punt"
- [x] Terrein: punt in polygoon (of ≤ 25 m) **én** naamtoets op kernwoorden; bij geneste terreinen wint het kleinste (Rijswijk: Joods deel in Oud-Rijswijk); verdwenen = alleen punt
- [x] Normaliseren met ruwe waarde ernaast (`*_bron`)
- [x] Correctielaag `data/corrections.csv` (nog leeg)
- [x] Output + `docs/data/koppelrapport.md`
- [x] Asserts ZH: 36 = 24/2/10; 26 terreinen; 0 ongekoppelde Joodse polygonen

## Fase 2 – Verrijking + contextlagen ✅

Besluit opdrachtgever (2026-10-02): wel gemeente- en provinciegrenzen, rijksmonumenten (gebouwd én archeologisch) en beschermde gezichten; **geen** archeologische onderzoeksgebieden, geen CHS.

- [x] `scripts/fetch_pdok.py`: provincies (12) + gemeenten (342), landelijk, vereenvoudigd
- [x] `scripts/fetch_rce.py`: gezichten (67), gebouwde rijksmonumenten (9.127), archeologische rijksmonumenten (60) voor ZH, bbox als parameter, geknipt op provinciegrens
- [x] Rmon-opzoeking: 7 nummers, waarvan 2 **complexnummers** (Gorinchem, Wassenaar) → onderdelen gekoppeld
- [x] `scripts/analyse_spatial.py`: gemeente, gezicht, rijksmonumenten ≤ 250 m (niet voor verdwenen) + `docs/data/erfgoedrelaties.md`
- [ ] Oppervlakte terrein (RD) vs Excel `Grootte` vergelijken
- [ ] Optioneel: RCE-objecten met functie "Joodse begraafplaats" die níet in de Excel staan → lijst voor Leon

## Fase 3 – Viewer ✅ (eerste versie)
- [x] MapLibre 4.7.1 (gevendord) + PDOK grijs/luchtfoto + `_headers`
- [x] Terreinen per status; punten met kleur + vorm (● bestaand, ◆ geruimd, ○ verdwenen)
- [x] Popup met alle kenmerken incl. eigenaar, rijksmonument/complex, gezicht, monumenten ≤ 100 m
- [x] Statusfilter met tellingen, zoeken, rijksmonument-/gezichtfilter, lijst, deelbare kaartpositie (hash)
- [x] Contextlagen: provincies, gemeenten, gezichten, rijksmonumenten (lazy), archeologisch
- [x] Inbedbaar: `?embed=1`, `frame-ancestors` dodenakkers.nl, CORS op `/data/*`
- [x] `methode.html`
- [ ] CSV/GeoJSON-export van de selectie (uit dodenakkers overnemen)
- [x] Front-end kwaliteitscontrole (2026-10-02): mobiel/tablet/desktop, mini-legenda, lege staat, foutmeldingen, 404, robots/sitemap, Open Graph, canonical
- [x] Ondergronden zoals dodenakkers-zh: grijs, luchtfoto, BGT, BRK-percelen (vanaf z17)
- [x] Popup: NA (bij/tegenover) bij adres, metaheerhuis met huisje-icoon, MIP
- [ ] Screenreadertest met echte schermlezer (NVDA/VoiceOver)

## Fase 4 – Oplevering ZH
- [x] Gedeployed als Worker met static assets (Wrangler 4.147 zet `pages project create` om naar Workers); `npx wrangler deploy`
- [ ] Eigen domein (bv. kaart.dodenakkers.nl) → `SITE_URL` in `scripts/build_site.py` aanpassen
- [ ] Review door Leon/René; feedback via `data/corrections.csv`

## Fase 5 – Landelijk (per provincie ½ dag)
- [ ] `--provincie X` voor de overige 11 provincies; per provincie koppelrapport + asserts
- [ ] Proefrun `--alle` (2026-10-02): 315 records, 228 terreinen, **18 zonder terrein** en **16 ongekoppelde Joodse polygonen** → per provincie uitzoeken
- [x] Rijksmonumenten: besluit 2026-10-02 — alleen ≤ 100 m van een begraafplaats, per provincie een bestand (`data/rce/index.json`)
- [ ] Volgorde voorstel: Utrecht, Noord-Holland, Gelderland, Overijssel, rest

## Risico's
- Naamsafwijkingen KML ↔ Excel (opgevangen door ruimtelijke koppeling + rapport).
- Persoonsgegevens: tabblad *Dank en informeren* wordt nooit gelezen; eigenaar/postadres mogen in de popup (akkoord 2026-10-02).
- Terrein kan in een ander provinciebestand liggen (grensgevallen) → bij landelijk alle KMZ's samen doorzoeken (`--alle` doet dat al).
