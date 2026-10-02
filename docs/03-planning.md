# 03 – Planning Joodse begraafplaatsen (start: Zuid-Holland)

Opdracht (Leon / Dodenakkers): één kaart met alle Joodse begraafplaatsen van Nederland, inclusief verdwenen en geruimd. We bouwen het eerst voor Zuid-Holland en zorgen dat de pipeline per provincie uitbreidbaar is.

## Fase 0 – Fundament (½ dag)
- [ ] `git init`, `.gitignore` (data-dodenakkers/ blijft buiten git), `requirements.txt`, `LICENSE` (CC BY 4.0?)
- [ ] `AI-joodse-begraafplaatsen.md` briefing (afgeleid van `AI-dodenakkers.md`)
- [ ] Mapstructuur: `scripts/`, `data/generated/`, `data/pdok/`, `data/corrections.csv`, `src/`, `docs/`

## Fase 1 – Basisdataset Zuid-Holland (1 dag)
- [ ] `scripts/load_sources.py`: Excel (alleen tabblad *Joodse begraafplaatsen*) + Locaties/Verdwenen/Geruimd/provincie-KMZ inlezen (stdlib zipfile + ElementTree)
- [ ] Sleutel `jb-<loc|ver|ger>-<Nr>`; assert uniek; assert elke rij vindt een punt
- [ ] Terrein koppelen (alleen in gebruik + geruimd): punt-in-polygoon in de provincie-KMZ **én** naamcheck; verdwenen = alleen punt
- [ ] Normaliseren: status (3 waarden), ja/nee-velden, jaartal/circa, grootte; ruwe waarden bewaren naast genormaliseerde
- [ ] Correctielaag `data/corrections.csv` (reden, datum, bron) i.p.v. fix-scripts
- [ ] Output: `data/generated/joodse-begraafplaatsen.geojson` + `.csv` + `docs/data/koppelrapport-zuid-holland.md` (naamsafwijkingen, twijfelgevallen voor Leon)
- [ ] Asserts ZH: 36 rijen = 24/10/2; 26 terreinen; 0 ongekoppelde Joodse polygonen

## Fase 2 – Verrijking + contextlagen (½–1 dag)

Besluit opdrachtgever (2026-10-02): **wel** gemeente- en provinciegrenzen, rijksmonumenten en beschermde gezichten; **geen** archeologische onderzoeksgebieden (en geen CHS-laag).

- [ ] Lagen gemeentegrenzen + provinciegrenzen (PDOK WFS bestuurlijke gebieden) — `fetch_gemeentegrenzen.py`/`fetch_provinciegrens.py` uit dodenakkers, provinciefilter generiek
- [ ] Laag rijksmonumenten + laag beschermde gezichten (RCE CHO SPARQL, `fetch_rce.py` + `queries/rce/` uit dodenakkers, bbox als parameter); relatie per begraafplaats via `analyse_spatial.py` (in gezicht / rijksmonument binnen X m)
- [ ] Provincie/gemeente ruimtelijk via PDOK (herindelingen signaleren t.o.v. Excel)
- [ ] Rijksmonument via `Rmon` → RCE CHO (naam, URI, monumentenregister-link); controleren tegen kolom `Link`
- [ ] Oppervlakte terrein in RD vs Excel-kolom `Grootte` (verschillen signaleren)
- [ ] Optioneel: RCE-objecten met functie "Joodse begraafplaats" die níet in de Excel staan → lijst voor Leon (niet op de kaart)

## Fase 3 – Viewer (1–2 dagen)
- [ ] MapLibre + PDOK-ondergronden + `_headers` uit dodenakkers
- [ ] Lagen: terreinen (fill per status), punten per status (in gebruik / geruimd / verdwenen — kleurenblind-veilig)
- [ ] Popup: naam, plaats, status, jaartal, bijzonderheden, monumentstatus + link, laatste bezoek
- [ ] Filters status/provincie/monument, zoeken, permalink, CSV/GeoJSON-export, toegankelijke lijst
- [ ] `methode.html`: bronnen, koppelmethode, beperkingen

## Fase 4 – Oplevering ZH (½ dag)
- [ ] `build_site.py`, nieuw Cloudflare Pages-project, `--branch main`
- [ ] Review door Leon; feedback in correctielaag

## Fase 5 – Landelijk (per provincie ½ dag)
- [ ] Zelfde pipeline voor de overige 11 provincies; Excel `Provincie` ↔ bestandsnaam mapping (Fryslân↔Friesland, Zeeland1)
- [ ] Per provincie koppelrapport + asserts; daarna één landelijke kaart
- [ ] Volgorde voorstel: Utrecht, Noord-Holland, Gelderland, Overijssel, rest

## Risico's
- Naamsafwijkingen KML ↔ Excel (opgevangen door ruimtelijke koppeling + rapport).
- Verdwenen punten: precisie onbekend (plek of alleen plaats?) → navragen.
- Persoonsgegevens in Excel (tabblad *Dank en informeren*, eventueel `Eigenaar`/`Postadres`) → uitsluiten.
- Terrein in provincie-KMZ kan in een ander provinciebestand liggen (grensgevallen) → bij landelijk alle KMZ's samen doorzoeken.
