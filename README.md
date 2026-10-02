# Joodse Begraafplaatsen

Kaart van de Joodse begraafplaatsen in Nederland — **bestaand, geruimd en verdwenen** — op basis van de inventarisatie van [stichting Dodenakkers](https://www.dodenakkers.nl/). Start: provincie Zuid-Holland (36 begraafplaatsen); de pipeline is per provincie uit te breiden.

Statische site (MapLibre GL + GeoJSON), geen backend. Los van het project *Dodenakkers Zuid-Holland* (provincieopdracht), maar met dezelfde werkwijze.

## Pipeline

```
data-dodenakkers/  (aangeleverd, niet in git)
  │
  ├─ scripts/fetch_pdok.py          → data/pdok/provincies.geojson, gemeenten.geojson
  ├─ scripts/build_base_dataset.py  → data/generated/joodse-begraafplaatsen.geojson/.csv, terreinen.geojson
  │                                    + docs/data/koppelrapport.md
  ├─ scripts/fetch_rce.py           → data/rce/<laag>-<provincie>.geojson + index.json, rmon-lookup.json
  │                                    (gebouwde rijksmonumenten alleen ≤ 100 m van een begraafplaats)
  ├─ scripts/analyse_spatial.py     → data/generated/begraafplaatsen.geojson  (viewer-data)
  │                                    + docs/data/erfgoedrelaties.md
  └─ scripts/build_site.py          → site/  (gitignored, voor Cloudflare Pages)
```

Volgorde en commando's:

```bash
pip install -r requirements.txt
python scripts/fetch_pdok.py
python scripts/build_base_dataset.py              # standaard Zuid-Holland; --provincie X (herhaalbaar) of --alle
python scripts/fetch_rce.py                       # zelfde --provincie-keuze
python scripts/analyse_spatial.py
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
- Correcties alleen via `data/corrections.csv` (id, veld, waarde, reden, datum, bron), nooit in de bron.
- Gemeente/provincie ruimtelijk bepaald (PDOK), Excel-waarde blijft als `_bron`.
- Het tabblad *Dank en informeren* (persoonsgegevens) wordt nooit gelezen.

Zie `docs/` voor de analyse, planning en rapporten, en `AI-joodse-begraafplaatsen.md` voor de werkafspraken.

## Inbedden

```html
<iframe src="https://<adres>/?embed=1" title="Kaart Joodse begraafplaatsen"
        width="100%" height="600" style="border:0" loading="lazy"></iframe>
```

`_headers` staat inbedden toe vanaf `dodenakkers.nl` (CSP `frame-ancestors`) en zet CORS open op `/data/*`, zodat de GeoJSON ook rechtstreeks door een andere site gebruikt kan worden.

## Licentie

CC BY 4.0 — zie `LICENSE`. Brondata onder de voorwaarden van de bronnen (Dodenakkers, RCE, PDOK/Kadaster).
