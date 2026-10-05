# Joodse Begraafplaatsen

Kaart van de Joodse begraafplaatsen in Nederland; **in gebruik, geruimd en verdwenen**, op basis van de inventarisatie van [stichting Dodenakkers](https://www.dodenakkers.nl/). **Stand 2026-10-05: heel Nederland** — alle 12 provincies, alle 315 begraafplaatsen uit de inventarisatie (239 in gebruik, 7 geruimd, 69 verdwenen). Zie [docs/03-planning.md](docs/03-planning.md).

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
  ├─ scripts/compute_statistics.py  → data/generated/statistieken.json  (statistiekpagina)
  ├─ scripts/make_og_image.py       → src/images/og-image.png  (deelafbeelding)
  └─ scripts/build_site.py          → site/  (gitignored, voor Cloudflare)
                                       draait eerst scripts/check_data.py: bij inconsistente data
                                       geen build, dus in Cloudflare ook geen deploy
```

Volgorde en commando's:

```bash
pip install -r requirements.txt
python scripts/fetch_pdok.py
python scripts/build_base_dataset.py --alle       # altijd ALLE provincies die op de kaart moeten
python scripts/fetch_rce.py --provincie Utrecht   # per provincie (herhaalbaar); alleen voor verse RCE-data
python scripts/analyse_spatial.py
python scripts/fetch_leeslijst.py                # kaartlinks + popupverwijzingen bijwerken
python scripts/compute_statistics.py
python scripts/make_og_image.py
python -m unittest discover -s tests -v       # tests koppelregels en datacontrole
python scripts/build_site.py
python -m http.server -d site 8765                # lokaal bekijken
```

Live: **https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev** (Cloudflare Worker met static assets, `wrangler.jsonc`).

## Deploy: alleen via een merge op GitHub

Wat live staat = wat op `main` staat. Niet meer handmatig deployen vanaf een werkmap.

Eenmalig instellen in Cloudflare (Workers Builds, Git-koppeling):

1. Cloudflare-dashboard → **Workers & Pages** → `joodse-begraafplaatsen` → **Settings** → **Builds** → **Connect** → GitHub-repo `jolietjakeblues/joodse-begraafplaatsen`.
2. **Production branch:** `main`.
3. **Build command:** `python3 scripts/build_site.py` (alleen standaard-Python nodig; de data staat al in git).
4. **Deploy command:** `npx wrangler deploy` (leest `wrangler.jsonc`, publiceert `site/`).
5. Optioneel: **builds for non-production branches** aan → elke pull request krijgt een preview-adres om te controleren vóór de merge.

Daarna: branch → pull request → merge op `main` → Cloudflare bouwt en zet live (± 1 minuut). De status zie je bij de commit op GitHub en onder **Deployments** in Cloudflare.

Data bijwerken (RCE, PDOK, leeslijst, nieuwe provincie) gebeurt lokaal met de scripts hieronder; het resultaat gaat via een commit + merge live.

Noodgeval (Cloudflare-build stuk): lokaal vanaf een schone kopie van `origin/main` bouwen en deployen:

```bash
git worktree add ../jb-deploy origin/main --detach
cd ../jb-deploy
python scripts/build_site.py
npx wrangler deploy
```

Publiceren (bij het boek): `PUBLICEREN = True` in `scripts/build_site.py` haalt `noindex` (meta + `X-Robots-Tag`) weg en zet de Sitemap-regel in robots.txt aan; de build controleert dat html, `_headers` en robots.txt bij elkaar passen. Productiedomein staat op één plek: `SITE_URL` in `scripts/build_site.py` (canonical, og:url, robots.txt, sitemap.xml). Open Graph-afbeelding: `python scripts/make_og_image.py`.

## Kernregels

- **`Nr` in de Excel is niet uniek.** Alleen uniek per reeks: in gebruik → `Locaties.kmz`, verdwenen → `Verdwenen.kmz`, geruimd → `Geruimd.kmz`. Sleutel: `jb-<loc|ver|ger>-<Nr>`.
- **Terrein** = punt ligt in polygoon (provincie-KMZ) én naam lijkt erop; bij geneste terreinen wint het kleinste. Verdwenen = alleen punt, bij benadering.
- Correcties van Dodenakkers komen binnen als GitHub-issue met label `correctie` (formulier `.github/ISSUE_TEMPLATE/correctie.yml`, link "Correctie doorgeven" in elke kaartpopup met kenmerk ingevuld). Verwerken: wijziging in de juiste correctielaag hieronder, PR met "Closes #<nr>", merge → automatische deploy.
- Correcties alleen via `data/corrections.csv` (velden), `data/terrein_koppelingen.csv` (handmatige terreinkoppeling), `data/herbegravingen.csv`, `data/geen_terrein_bevestigd.csv` en `data-dodenakkers/funerair_nieuwedata.kmz` (door Dodenakkers nagestuurde terreinen + ingangen; vervangt het terrein met dezelfde naam), nooit in de bron.
- Gecontroleerde tellingen per provincie, met toelichting, in `data/invarianten.json`. `build_base_dataset.py` controleert die vóór het schrijven (een afgekeurde run laat de vorige uitvoer staan); `check_data.py` controleert de gecommitte data vóór elke sitebuild.
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
