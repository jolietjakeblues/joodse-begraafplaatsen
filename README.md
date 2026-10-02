# Joodse Begraafplaatsen

Kaart van de Joodse begraafplaatsen in Nederland — **bestaand, geruimd en verdwenen** — op basis van de inventarisatie van [stichting Dodenakkers](https://www.dodenakkers.nl/). **Stand 2026-10-02: West-Nederland** — Zuid-Holland, Utrecht, Noord-Holland, Zeeland en Flevoland (91 begraafplaatsen: 67 bestaand, 2 geruimd, 22 verdwenen). De overige provincies volgen; zie [docs/03-planning.md](docs/03-planning.md).

Statische site (MapLibre GL + GeoJSON), geen backend. Los van het project *Dodenakkers Zuid-Holland* (provincieopdracht), maar met dezelfde werkwijze.

## Pipeline

```
data-dodenakkers/  (aangeleverd, niet in git)
  │
  ├─ scripts/fetch_pdok.py          → data/pdok/provincies.geojson, gemeenten.geojson
  ├─ scripts/build_base_dataset.py  → data/generated/joodse-begraafplaatsen.geojson/.csv, terreinen.geojson
  │                                    + docs/data/koppelrapport.md
  ├─ scripts/fetch_rce.py           → data/rce/<laag>-<provincie>.geojson + index.json, rmon-lookup.json
  │                                    (rijksmonumenten alleen ≤ 100 m van een begraafplaats)
  ├─ scripts/analyse_spatial.py     → data/generated/begraafplaatsen.geojson  (viewer-data)
  │                                    + docs/data/erfgoedrelaties.md
  ├─ scripts/fetch_leeslijst.py     → data/generated/leeslijst.json  (artikelen dodenakkers.nl, tag "Joodse begraafplaats")
  ├─ scripts/make_og_image.py       → src/images/og-image.png  (deelafbeelding)
  └─ scripts/build_site.py          → site/  (gitignored, voor Cloudflare)
```

Volgorde en commando's:

```bash
pip install -r requirements.txt
python scripts/fetch_pdok.py
P="--provincie Zuid-Holland --provincie Utrecht --provincie Noord-Holland --provincie Zeeland --provincie Flevoland"
python scripts/build_base_dataset.py $P           # altijd ALLE provincies die op de kaart moeten
python scripts/fetch_rce.py $P                    # alleen nodig voor nieuwe provincies / verse RCE-data
python scripts/analyse_spatial.py
python scripts/fetch_leeslijst.py                # leespagina actueel houden (na analyse_spatial: kaartlinks)
python scripts/make_og_image.py
python scripts/build_site.py
python -m http.server -d site 8765                # lokaal bekijken
```

Live: **https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev** (Cloudflare Worker met static assets, `wrangler.jsonc`). Deploy:

```bash
python scripts/build_site.py
npx wrangler deploy
```

Productiedomein staat op één plek: `SITE_URL` in `scripts/build_site.py` (canonical, og:url, robots.txt, sitemap.xml). Open Graph-afbeelding: `python scripts/make_og_image.py`.

## Kernregels

- **`Nr` in de Excel is niet uniek.** Alleen uniek per reeks: in gebruik → `Locaties.kmz`, verdwenen → `Verdwenen.kmz`, geruimd → `Geruimd.kmz`. Sleutel: `jb-<loc|ver|ger>-<Nr>`.
- **Terrein** = punt ligt in polygoon (provincie-KMZ) én naam lijkt erop; bij geneste terreinen wint het kleinste. Verdwenen = alleen punt, bij benadering.
- Correcties alleen via `data/corrections.csv` (velden) en `data/terrein_koppelingen.csv` (handmatige terreinkoppeling), nooit in de bron.
- Gecontroleerde tellingen per provincie in `INVARIANTEN` (`scripts/build_base_dataset.py`).
- Gemeente/provincie ruimtelijk bepaald (PDOK), Excel-waarde blijft als `_bron`.
- Het tabblad *Dank en informeren* (persoonsgegevens) wordt nooit gelezen.

## Documentatie

| Bestand | Inhoud |
|---|---|
| [docs/01-data-analyse.md](docs/01-data-analyse.md) | Analyse van de aangeleverde Excel en KMZ's |
| [docs/02-project-analyse.md](docs/02-project-analyse.md) | Wat is overgenomen uit dodenakkers-zh |
| [docs/03-planning.md](docs/03-planning.md) | Voortgang per provincie en fasen |
| [docs/04-vragen-dodenakkers.md](docs/04-vragen-dodenakkers.md) | Open vragen voor Leon, René en Dodenakkers |
| [docs/data/koppelrapport.md](docs/data/koppelrapport.md) | Gegenereerd: koppeling punten/terreinen, afwijkingen |
| [docs/data/erfgoedrelaties.md](docs/data/erfgoedrelaties.md) | Gegenereerd: gezichten, rijksmonumenten, complexen |
| [AI-joodse-begraafplaatsen.md](AI-joodse-begraafplaatsen.md) | Werkafspraken en besluiten |

Pagina's van de site: `index.html` (kaart; `?id=jb-loc-4200` opent een begraafplaats, `?embed=1` voor inbedden), `lezen.html` (leeslijst met artikelen van dodenakkers.nl), `methode.html`.

## Inbedden

```html
<iframe src="https://<adres>/?embed=1" title="Kaart Joodse begraafplaatsen"
        width="100%" height="600" style="border:0" loading="lazy"></iframe>
```

`_headers` staat inbedden toe vanaf `dodenakkers.nl` (CSP `frame-ancestors`) en zet CORS open op `/data/*`, zodat de GeoJSON ook rechtstreeks door een andere site gebruikt kan worden.

## Licentie

CC BY 4.0 — zie `LICENSE`. Brondata onder de voorwaarden van de bronnen (Dodenakkers, RCE, PDOK/Kadaster).
