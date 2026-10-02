# 03 – Planning Joodse begraafplaatsen

Opdracht (stichting Dodenakkers): één kaart met alle Joodse begraafplaatsen van Nederland, inclusief geruimd en verdwenen. Gebouwd per provincie.

**Stand 2026-10-02: 9 van 12 provincies klaar** (t/m Limburg), 251 begraafplaatsen. Live: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev. Open vragen: [04-vragen-dodenakkers.md](04-vragen-dodenakkers.md).

## Voortgang per provincie

| Provincie | Status | Totaal | Bestaand | Geruimd | Verdwenen | Terreinen | Bijzonderheden |
|---|---|---|---|---|---|---|---|
| Zuid-Holland | ✅ | 36 | 24 | 2 | 10 | 26 | Rijswijk: Joods deel genest in Oud-Rijswijk |
| Utrecht | ✅ | 20 | 14 | 0 | 6 | 13 | Bilthoven zonder terrein in KMZ |
| Noord-Holland | ✅ | 28 | 22 | 0 | 6 | 22 | Ouderkerk via Excel-naam "Beth Haim"; Beverwijk terrein veel kleiner dan `Grootte` |
| Zeeland | ✅ | 6 | 6 | 0 | 0 | 6 | Vlissingen: handmatige koppeling; twee polygonen met identieke oppervlakte |
| Flevoland | ✅ | 1 | 1 | 0 | 0 | 1 | Almere terrein kleiner dan `Grootte` |
| Gelderland | ✅ | 61 | 45 | 0 | 16 | 45 | Alles gekoppeld; 8 herbegravingen (o.a. Doesburg in twee stappen) |
| Overijssel | ✅ | 43 | 34 | 1 | 8 | 35 | Enschede (2×) handmatig gekoppeld (Israëlitisch ↔ Joods); 4 herbegravingen |
| Noord-Brabant | ✅ | 31 | 21 | 0 | 10 | 21 | Putte: Rmon 516689 ligt op Frechie Foundation (vraag); 3 herbegravingen (Cuijk in twee stappen) |
| Groningen | ⏳ | 27 | | | | | |
| Limburg | ✅ | 25 | 18 | 1 | 6 | 19 | Alles gekoppeld; Sittard "Vrangendael" en Venlo 37192 als vraag; 1 herbegraving |
| Drenthe | ⏳ | 21 | | | | | |
| Fryslân | ⏳ | 16 | | | | | |

Tellingen staan vast in `INVARIANTEN` (`scripts/build_base_dataset.py`).

Draaien (alle provincies die op de kaart moeten, in één keer):

```bash
P="--provincie Zuid-Holland --provincie Utrecht --provincie Noord-Holland --provincie Zeeland --provincie Flevoland"
python scripts/build_base_dataset.py $P
python scripts/fetch_rce.py $P        # alleen nodig voor nieuwe provincies of verse RCE-data
python scripts/analyse_spatial.py
python scripts/fetch_leeslijst.py
python scripts/make_og_image.py
# daarna: branch → pull request → merge op main → Cloudflare deployt (zie README)
```

## Fasen

### Fase 0–2 – Fundament, basisdataset, verrijking ✅
- [x] Repo, `.gitignore` (bronmap buiten git), `requirements.txt`, `LICENSE` (CC BY 4.0), README, werkafspraken
- [x] `build_base_dataset.py`: sleutel `jb-<reeks>-<Nr>`; terrein via punt-in-polygoon + naamtoets (puntlabel én Excel-naam, kernwoorden, plaats ook zonder komma, woordinsluiting); genest → kleinste; verdwenen = alleen punt
- [x] Correctielagen: `data/corrections.csv` (velden) en `data/terrein_koppelingen.csv` (handmatige terreinkoppeling, nu 1: Vlissingen)
- [x] Controles in het koppelrapport: naamvarianten, oppervlakte vs `Grootte` (75–133 %), genest, identieke oppervlaktes, provincie Excel vs ligging
- [x] `fetch_pdok.py` (provincies + gemeenten), `fetch_rce.py` per provincie met manifest `data/rce/index.json`
- [x] Rijksmonumenten (gebouwd + archeologisch) alleen ≤ 100 m van een bestaande/geruimde begraafplaats; gezichten hele provincie
- [x] Rmon-opzoeking als rijksmonument- óf complexnummer (8 van 19 zijn complexnummers)
- [ ] Optioneel: RCE-objecten met functie "Joodse begraafplaats" die níet in de Excel staan → lijst voor Leon

### Fase 3 – Viewer ✅
- [x] MapLibre 4.7.1 (gevendord), ondergronden PDOK grijs/luchtfoto/BGT + BRK-percelen
- [x] Kleur + vorm per status (● bestaand, ◆ geruimd, ○ verdwenen), kleurenblind getest
- [x] Popup (adres met NA, metaheerhuis 🏠, MIP, rijksmonument/complex, gezicht, monumenten ≤ 100 m, eigenaar)
- [x] Filters met tellingen, zoeken, lijst, deelbare positie, inbedden (`?embed=1`)
- [x] Front-end kwaliteitscontrole: mobiel (mini-legenda, aanraakdoelen), lege staat, foutmeldingen, 404, robots/sitemap, Open Graph, canonical
- [x] Dateringsfilter (klikbare balkjes, zoals dodenakkers-zh; indeling is vraag C9)
- [x] Leespagina `lezen.html`: 43 artikelen van dodenakkers.nl (tag "Joodse begraafplaats"), per provincie, 2 uitgelicht (archeologie verdwenen begraafplaatsen), 15 met "Bekijk op de kaart" (`scripts/fetch_leeslijst.py`, uitgelicht in `data/leeslijst_uitgelicht.json`)
- [x] Directe link naar een begraafplaats: `?id=<kenmerk>` (nog visueel te controleren)
- [ ] CSV/GeoJSON-export van de selectie
- [ ] Screenreadertest (NVDA/VoiceOver)
- [ ] Wensen uit de vragenlijst (layout, legenda, teksten)

### Fase 4 – Oplevering ✅ (doorlopend)
- [x] Live als Cloudflare Worker met static assets
- [x] Deploy gekoppeld aan merge op `main` (Cloudflare Workers Builds; eerste automatische build bij PR #6, 2026-10-02, geslaagd)
- [ ] Eigen domein → `SITE_URL` in `scripts/build_site.py`
- [x] Review Leon/René ronde 1 en 2 verwerkt (2026-10-02; zie docs/04, navragen N1–N4 open)
- [ ] Nieuwe bronbestanden van Leon verwerken (N4) en herbegravingen aanvullen (N3)

### Fase 5 – Rest van Nederland
- [ ] Oost/Noord/Zuid per provincie, volgorde voorstel: ✅ Gelderland, ✅ Overijssel, ✅ Noord-Brabant, ✅ Limburg, Groningen, Drenthe, Fryslân
- [ ] Proefrun `--alle` (2026-10-02, vóór de verbeteringen van West): 18 zonder terrein, 16 ongekoppelde Joodse polygonen → per provincie uitzoeken
- [ ] Bij landelijke dekking: label "Nederland", deelafbeelding opnieuw

## Risico's
- Naamsafwijkingen KMZ ↔ Excel: opgevangen door ruimtelijke koppeling + rapport + handmatige koppelingen.
- Fouten in de KMZ zelf (gekopieerde polygoon Vlissingen, te klein terrein Beverwijk) kunnen we signaleren maar niet oplossen → Dodenakkers.
- Persoonsgegevens: tabblad *Dank en informeren* wordt nooit gelezen; eigenaar/postadres mogen in de popup (akkoord 2026-10-02).
- Grensgevallen: een terrein kan in het bestand van de buurprovincie staan → buurprovincies samen draaien.
