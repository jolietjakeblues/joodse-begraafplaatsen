# 03 – Planning Joodse begraafplaatsen

Opdracht (stichting Dodenakkers): één kaart met alle Joodse begraafplaatsen van Nederland, inclusief geruimd en verdwenen. Gebouwd per provincie.

**Stand 2026-10-05: alle 12 provincies klaar**, 315 begraafplaatsen (315/315 Excel-rijen gekoppeld). Live: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev. Open vragen: [04-vragen-open.md](04-vragen-open.md) (beantwoord: [05](05-vragen-beantwoord.md)).

## Voortgang per provincie

| Provincie | Status | Totaal | In gebruik | Geruimd | Verdwenen | Terreinen | Bijzonderheden |
|---|---|---|---|---|---|---|---|
| Zuid-Holland | ✅ | 36 | 24 | 2 | 10 | 26 | Rijswijk: Joods deel genest in Oud-Rijswijk |
| Utrecht | ✅ | 20 | 14 | 0 | 6 | 13 | Bilthoven zonder terrein in KMZ |
| Noord-Holland | ✅ | 28 | 22 | 0 | 6 | 22 | Ouderkerk via Excel-naam "Beth Haim"; Beverwijk terrein veel kleiner dan `Grootte` |
| Zeeland | ✅ | 6 | 6 | 0 | 0 | 6 | Vlissingen: handmatige koppeling; twee polygonen met identieke oppervlakte |
| Flevoland | ✅ | 1 | 1 | 0 | 0 | 1 | Almere terrein kleiner dan `Grootte` |
| Gelderland | ✅ | 61 | 45 | 0 | 16 | 45 | Alles gekoppeld; 8 herbegravingen (o.a. Doesburg in twee stappen) |
| Overijssel | ✅ | 43 | 34 | 1 | 8 | 35 | Enschede (2×) handmatig gekoppeld (Israëlitisch ↔ Joods); 4 herbegravingen |
| Noord-Brabant | ✅ | 31 | 21 | 0 | 10 | 21 | Putte: Rmon 516689 hoort bij de Frechie Foundation (in de Excel sinds 2026-10-06); 3 herbegravingen (Cuijk in twee stappen) |
| Groningen | ✅ | 27 | 23 | 2 | 2 | 25 | Leens (KMZ-tikfout) en Uithuizen handmatig; Loppersum terrein en Uithuizen-ingang uit `Voor Joop.kmz` (2026-10-06) |
| Limburg | ✅ | 25 | 18 | 1 | 6 | 19 | Alles gekoppeld; Sittard "Vrangendael" en Venlo 37192 als vraag; 1 herbegraving |
| Drenthe | ✅ | 21 | 20 | 0 | 1 | 20 | Emmen: namen Westenesch/Oude gekruist tussen Excel en KMZ (vraag Dr1), gekoppeld op ligging; 1 herbegraving |
| Fryslân | ✅ | 16 | 11 | 1 | 4 | 12 | Alles gekoppeld; 1 herbegraving (Harlingen) |

Tellingen staan vast in `data/invarianten.json` (met toelichting); gecontroleerd door `build_base_dataset.py` (vóór het schrijven) en `check_data.py` (vóór elke sitebuild).

Draaien (alle provincies die op de kaart moeten, in één keer):

```bash
P="--provincie Zuid-Holland --provincie Utrecht --provincie Noord-Holland --provincie Zeeland --provincie Flevoland"
python scripts/build_base_dataset.py $P
python scripts/fetch_rce.py $P        # alleen nodig voor nieuwe provincies of verse RCE-data
python scripts/analyse_spatial.py
python scripts/fetch_leeslijst.py
python scripts/fetch_allmaps.py
python scripts/make_og_image.py
# daarna: branch → pull request → merge op main → Cloudflare deployt (zie README)
```

## Fasen

### Fase 0–2 – Fundament, basisdataset, verrijking ✅
- [x] Repo, `.gitignore` (bronmap buiten git), `requirements.txt`, `LICENSE` (CC BY 4.0), README, werkafspraken
- [x] `build_base_dataset.py`: sleutel `jb-<reeks>-<Nr>`; terrein via punt-in-polygoon + naamtoets (puntlabel én Excel-naam, kernwoorden, plaats ook zonder komma, woordinsluiting); genest → kleinste; verdwenen = alleen punt
- [x] Correctielagen: `data/corrections.csv` (velden), `data/terrein_koppelingen.csv` (6 handmatige terreinkoppelingen), `data/herbegravingen.csv` (35), `funerair_nieuwedata.kmz` (nagestuurde terreinen)
- [x] Controles in het koppelrapport: naamvarianten, oppervlakte vs `Grootte` (75–133 %), genest, identieke oppervlaktes, provincie Excel vs ligging
- [x] `fetch_pdok.py` (provincies + gemeenten), `fetch_rce.py` per provincie met manifest `data/rce/index.json`
- [x] Rijksmonumenten (gebouwd + archeologisch) alleen ≤ 100 m van een begraafplaats in gebruik of geruimd; gezichten hele provincie
- [x] Rmon-opzoeking als rijksmonument- óf complexnummer (8 van 19 zijn complexnummers)
- [x] RCE-controle op ontbrekende Joodse begraafplaatsen: niet nodig, Leon heeft dit al gedaan (C8)

### Fase 3 – Viewer ✅
- [x] MapLibre 4.7.1 (gevendord), ondergronden PDOK grijs/luchtfoto/BGT + BRK-percelen
- [x] Kleur + vorm per status (● in gebruik, ◆ geruimd, ○ verdwenen), kleurenblind getest; huisstijl `#8d161c` + logo
- [x] Popup (adres met NA, metaheerhuis 🏠, MIP, rijksmonument/complex, gezicht, monumenten ≤ 100 m, herbegravingen, artikelen, correctielink); eigenaar e.d. eruit (C1/C2)
- [x] Filters met tellingen, zoeken, lijst, deelbare positie, inbedden (`?embed=1`)
- [x] Front-end kwaliteitscontrole: mobiel (mini-legenda, aanraakdoelen), lege staat, foutmeldingen, 404, robots/sitemap, Open Graph, canonical
- [x] Dateringsfilter (klikbare balkjes; generieke indeling vóór 1700 … 1950–heden, C9)
- [x] Leespagina `lezen.html`: 43 artikelen van dodenakkers.nl (tag "Joodse begraafplaats"), per provincie, 39 met "Bekijk op de kaart"; geen uitgelicht-blok meer (2026-10-05); popup "Lees op Dodenakkers" (`scripts/fetch_leeslijst.py`, `popup_ids`)
- [x] Oude kaarten (2026-10-06): link "Oude kaarten" in popup en pagina per begraafplaats naar `oude-kaarten.html` (Bonnebladen met jaartal, Waterstaatskaart e.a. via Allmaps; geen laag op de hoofdkaart). 69 verdwenen begraafplaatsen bekeken: `docs/data/verdwenen-oude-kaarten.md`, vraag OK1
- [x] Statistiekpagina `statistieken.html` (vraag E7, 2026-10-05; `scripts/compute_statistics.py`)
- [x] Correctieformulier (vraag F1): GitHub-issueformulier `correctie.yml` + popuplink "Correctie doorgeven" (2026-10-05)
- [x] Review 2026-10-05: filtertellingen binnen alle actieve filters, springlink opent paneel, mobiele CSS achteraan, controle vóór schrijven + `check_data.py` in de sitebuild, unieke monumenten in de statistiek
- [x] Directe link naar een begraafplaats: `?id=<kenmerk>` (nog visueel te controleren)
- [x] CSV/GeoJSON-export van de selectie: niet gewenst (E7)
- [x] Eigen review 2026-10-05: AVG-opschoning git-geschiedenis; Putte via corrections.csv; contrast geruimd-ruit; focus na popup; linkcontrole; data laden los van de ondergrond; stabiele rapporten; 17 tests; springlinks op alle pagina's; 12 px; favicon; 404 met grafpaaltje; RCE-functies zonder haakjes; verdwenen op 4 decimalen; publicatieschakelaar
- [x] Na eigen voorstellen (2026-10-05): vaste kenmerken (`data/kenmerken.json` + doorverwijzingen), pagina per begraafplaats, zoeken zonder accenten/met aliassen, provinciefilter, pijlen op herbegravingen, "Link kopiëren"
- [ ] Vast webadres vóór het boek naar de drukker gaat (`SITE_URL`; komt eraan)
- [ ] Screenreadertest (NVDA/VoiceOver)
- [x] Wensen uit de vragenlijst (layout, teksten): E2/E5/E6 "prima zo"; Engelse versie later

### Fase 4 – Oplevering ✅ (doorlopend)
- [x] Live als Cloudflare Worker met static assets
- [x] Deploy gekoppeld aan merge op `main` (Cloudflare Workers Builds; eerste automatische build bij PR #6, 2026-10-02, geslaagd)
- [ ] Eigen domein → `SITE_URL` in `scripts/build_site.py`
- [x] Review Leon/René ronde 1–3 verwerkt (2026-10-02 en 2026-10-05; zie docs/04)
- [ ] Gecorrigeerde Excel van Leon verwerken (R3) en navragen R1, R2, Gr1, Dr1
- [ ] Publicatie bij het boek: `PUBLICEREN = True` in `scripts/build_site.py` (haalt noindex weg, zet sitemap aan), licentie/hergebruik volgens P1, eventueel eigen domein (E9)
- [ ] GitHub Support vragen om oude commits achter PR-verwijzingen (`refs/pull/*`) te verwijderen (AVG)

### Fase 5 – Rest van Nederland
- [x] Oost/Noord/Zuid per provincie: ✅ Gelderland, ✅ Overijssel, ✅ Noord-Brabant, ✅ Limburg, ✅ Groningen, ✅ Drenthe, ✅ Fryslân (2026-10-05)
- [x] Per provincie uitgezocht; landelijk 315/315, 0 ongekoppelde Joodse polygonen
- [x] Label "Nederland" en deelafbeelding opnieuw (2026-10-05)

## Risico's
- Naamsafwijkingen KMZ ↔ Excel: opgevangen door ruimtelijke koppeling + rapport + handmatige koppelingen.
- Fouten in de KMZ zelf (gekopieerde polygoon Vlissingen, te klein terrein Beverwijk) kunnen we signaleren maar niet oplossen → Dodenakkers.
- Persoonsgegevens: tabblad *Dank en informeren* wordt nooit gelezen; eigenaar/postadres worden niet getoond en zitten niet in de open data (C2).
- Grensgevallen: een terrein kan in het bestand van de buurprovincie staan → buurprovincies samen draaien.
