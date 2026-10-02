# 02 – Analyse voorbeeldproject `dodenakkers` (Zuid-Holland)

Bron: `C:\AI\projects\dodenakkers` (live: https://dodenakkers-zh.pages.dev/). Doel: bepalen wat we hergebruiken, wat we aanpassen en wat we laten liggen.

## Architectuur dodenakkers

Een statische onderzoeksviewer zonder backend. Alle data wordt vooraf lokaal berekend en als GeoJSON/JSON gecommit. Cloudflare Pages kopieert alleen.

```
bron-CSV (WKT, naam, plaats, geruimd, ingang/terrein)
 → build_base_dataset.py   terrein↔ingang koppelen, opp/omtrek in RD  → begraafplaatsen.geojson
 → fetch_rce.py            RCE SPARQL (gezichten, rijksmonumenten, archeologie) → data/rce/*.geojson + metadata
 → fetch_provinciegrens / fetch_gemeentegrenzen (PDOK WFS)
 → analyse_spatial.py      relaties met erfgoed (RD, STRtree)        → analyse.geojson
 → compute_statistics.py   → statistieken.json
 → build_verdwenen_begraafplaatsen.py → verdwenen-begraafplaatsen.geojson
 → build_site.py           whitelist kopiëren naar site/ + paden herschrijven
 → Cloudflare Pages (Git-integratie of `wrangler pages deploy site --branch main`)
```

Stack: Python (pandas, shapely, pyproj, requests; KML met stdlib `zipfile` + `ElementTree`). Frontend: vanilla JS + **MapLibre GL 4.7.1 lokaal gevendord**, PDOK-ondergronden (BRT grijs, luchtfoto, BGT ≥ z17, BRK-overlay), strikte CSP in `_headers`, WCAG AA, CC BY 4.0.

## Belangrijkste ontwerpregels (uit `AI-dodenakkers.md`)

- Geen live SPARQL in de browser; alles vooraf berekenen.
- Afstanden/oppervlaktes in RD New (EPSG:28992).
- Nooit een ingang verzinnen (geen centroid als ingang).
- Status nooit uit naam afleiden; conflicten zichtbaar maken, niet stil oplossen.
- Geen eigen classificatie zonder expliciet akkoord ("no silent curation").
- Persoonsnamen geanonimiseerd in docs/code.

## Lessen / valkuilen

1. **Bron werd steeds gemuteerd met eenmalige `fix_*.py`-scripts** (11 stuks, Oudenhoorn in 5 rondes), met handmatig bijgewerkte assert-tellingen. → Nu: een **correctielaag** (`data/corrections.csv` met reden/datum/bron) die tijdens de build wordt toegepast; bron blijft onaangeroerd.
2. IDs `zh-0001` waren volgorde-afhankelijk. → Nu: stabiele sleutel `jb-<reeks>-<nr>`.
3. Matching op naam vereiste unieke naam+plaats (assert). → Hier zijn naam én nummer niet uniek; daarom: reeks+Nr voor het punt, punt-in-polygoon + naamcheck voor het terrein.
4. Herindelingen (Vijfheerenlanden) → gemeente/provincie ruimtelijk bepalen via PDOK, niet uit de Excel overnemen.
5. bbox-randeffecten bij RCE-extracts → filteren op echte grenzen.
6. RCE: labels buiten `GRAPH`, multi-valued velden, `geof:sfWithin` timeouts → bbox-filter op WKT-string; 25 MB-limiet per bestand.
7. PDOK BGT/Kadastralekaart WMTS pas zichtbaar vanaf zoom ~17.
8. MapLibre: `circle` slaat polygonen stil over, `fill` punten → per geometrietype lagen.
9. pandas NaN → `None` vóór JSON.
10. Domein: Joodse begraafplaatsen liggen bewust ver van de synagoge — afstand tot synagoge is geen signaal.
11. Een verdwenen punt is een gegeven, geen kandidaat.

## Hergebruik

| Onderdeel | Oordeel |
|---|---|
| `AI-dodenakkers.md`, docs-structuur | Sjabloon → `AI-joodse-begraafplaatsen.md` |
| KMZ-parsing (`build_verdwenen_begraafplaatsen.py`, `add_tijdelijk_zuidholland_kmz.py`) | Patroon hergebruiken, nieuwe loader schrijven |
| `build_base_dataset.py` (normalize, RD-transformer, opp/omtrek, write_geojson/csv/audit, asserts) | Functies hergebruiken; koppellogica nieuw |
| `fetch_rce.py` + `queries/rce/*.sparql` | Hergebruiken, bbox parametriseren (later landelijk) |
| `analyse_spatial.py` | Hergebruiken (fase 2): gezichten + rijksmonumenten; archeologie-onderdelen weglaten |
| `fetch_provinciegrens.py` / `fetch_gemeentegrenzen.py` | Hergebruiken, provinciefilter generiek |
| `compute_statistics.py` | Aanpassen op statusenum |
| Frontend (`app.js`, `style.css`, vendor MapLibre, `_headers`, `methode.html`) | Hergebruiken als basis, sterk vereenvoudigen |
| `build_site.py` + Cloudflare Pages | Hergebruiken, nieuw Pages-project |
| `fetch_chs_archeologie.py`, alle `fix_*`/`add_tijdelijk_*`, kandidatenpagina | **Niet** meenemen |

**Niet automatisch overnemen:** de data van dodenakkers (CSV, KML, gegenereerde GeoJSON). De nieuwe bron is Leons Excel + KMZ's. Wel later vergelijken: de ongetrackte pipe-CSV `dodenakkers/data/Begraafplaatsen Zuid-Holland.csv` bevat 26 rijen `Sign=Joods` en heeft hetzelfde nummerprobleem (geruimd-reeks overlapt) — bevestigt het reeks-model.
