# 05 – Beantwoorde vragen van Dodenakkers (Leon, René)

Stand: 2026-10-06 · Open vragen: [04-vragen-open.md](04-vragen-open.md)

Alle vragen die Leon en René hebben beantwoord, in drie rondes (2 en 5 oktober 2026: opmerkingen bij de vragenlijst, opmerkingen in de PDF, het Word-document). Per vraag: de vraag in het kort, het antwoord (de laatste stand) en wat er op de kaart mee gedaan is. Tussenstanden staan in de git-geschiedenis.

## A. Bronbestanden

- **✅ A1. Nummerreeksen** — elke status een eigen reeks en bestand (`loc`/`ver`/`ger`)? *Antwoord:* prima, de nummers zijn te herleiden. *Verwerkt:* koppeling via `jb-<reeks>-<Nr>`; landelijk 315/315.
- **✅ A2. Dubbel Nr 245 in Geruimd.kmz** (Puttershoek / Pannerden). *Antwoord:* fout in de bron, door Leon gecorrigeerd. *Verwerkt:* niet Joods, geen gevolg voor de kaart.
- **✅ A3. Betekenis van kolommen.** *Antwoorden:* `NA` = nader adres ("to" = tegenover); `MIP` = Monumenten Inventarisatie Project (tonen); `Met` = metaheerhuis(je); `Muur` = muur rondom (onvolledig, niet tonen); `Kadaster` = aldaar geregistreerd (niet tonen); `Circa` = jaartal bij benadering; `Jaartal` = aanleg of eerste begraving; `Grondvorm` = niet van belang; `Gemeentelijk monument` "Geen" = "Nee"; `Grootte` = oppervlakte van de Google Earth-shape; `Laatste bezoek` = niet tonen; `Rmon` = één cel, bij een complex het complexnummer. *Verwerkt:* zo in popup en open data; niet-getoonde velden zitten ook niet in de open data.
- **✅ A4. "In gebruik" of "Bestaand"?** *Antwoord:* Joodse begraafplaatsen worden niet gesloten; liever "In gebruik". *Verwerkt:* status heet "In gebruik"; gesloten-informatie alleen in Bijzonderheden.
- **✅ A5. Precisie verdwenen begraafplaatsen.** *Antwoord:* alleen een punt, meestal waar de begraafplaats lag, zekerheid niet hoog. *Verwerkt:* open ring, "plek bij benadering", geen afstandsrelaties, coördinaten op 4 decimalen (~10 m).
- **✅ A6. Complexnummer in `Rmon`.** *Antwoord:* kan voorkomen; complex tonen is prima. Wassenaar: metaheerhuis staat formeel niet op de Joodse begraafplaats, nader onderzoek volgt (N1). *Verwerkt:* complex opgezocht, onderdelen in de popup.
- **✅ A7. Rijksmonumenten op het terrein, niet in de Excel.** *Antwoorden:* Alkmaar 7464 = de begraafplaats zelf (niet aan complex 524892 toegevoegd); Bussum 527225 = de gemeentelijke begraafplaats; Overveen 529524 = toegangspoort; Wijk bij Duurstede 454310 = net buiten; Middelburg 508330 = metaheerhuisje. *Verwerkt:* als beoordeelde relaties (`BEOORDEELDE_RELATIES`).

## B. Specifieke begraafplaatsen

- **✅ B1. Bilthoven zonder terrein.** *Antwoord:* alleen een punt; deel nog niet goed af te bakenen. *Verwerkt:* `data/geen_terrein_bevestigd.csv`.
- **✅ B2. Vlissingen, twee terreinen van 694 m².** *Antwoord:* toeval; vroege polygonen zijn weinig nauwkeurig. *Verwerkt:* koppeling blijft (Leeuwentrap handmatig).
- **✅ B3. Terrein wijkt sterk af van `Grootte`.** *Antwoord:* niet op letten; sommige shapes zijn oud. *Verwerkt:* niet meer als vraag gemeld; methodepagina noemt de beperkte nauwkeurigheid.
- **✅ B4. Rhenen en Edam, beide 372 m².** *Antwoord:* vormen zijn nooit gekopieerd. *Verwerkt:* geen actie.
- **✅ B5. Naamsverschillen KMZ ↔ puntbestand.** *Antwoorden:* ronde 1: Toepad, Oud-Rijswijk, Schiedam vastgesteld; ronde 2: houd de Excel-naam aan; ronde 3: "groen is de juiste" (Diemen, Muiderberg e.a.). *Verwerkt:* Excel-namen, met drie weergavenamen via `corrections.csv`. Tegenstrijdigheid tussen ronde 2 en 3 → navraag [R1](04-vragen-open.md#r1-welke-naam-komt-op-de-kaart).
- **✅ B6. Twee keer "Crooswijk".** *Antwoord:* twee echte plekken; periode toevoegen mag. *Verwerkt:* "(1696–1807)" en "(vanaf 1877)".
- **✅ B7. Dordrecht, verdwenen en bestaand met dezelfde naam.** *Antwoord:* de geruimde heet "Oude Joodse begraafplaats". *Verwerkt:* `jb-ver-182` hernoemd; herbegraving naar Dordrecht en Strijen.
- **✅ B8. Kleine fouten in de bron.** *Antwoorden:* Shomre Hadas klopt in de Excel; Maassluis aangepast in de bron; contour Schiedam nog niet bekend. *Verwerkt:* wacht op de nieuwe Excel ([R3](04-vragen-open.md#r3-de-gecorrigeerde-excel)).

## C. Inhoud van de kaart

- **✅ C1. Popup.** *Antwoord:* grondvorm, eigenaren en laatste bezoek eruit. *Verwerkt:* gedaan; erbij gekomen: herbegravingen, artikelen ("Lees op Dodenakkers") en "Correctie doorgeven".
- **✅ C2. Eigenaren.** *Antwoord:* helemaal niet tonen (onvolledig). *Verwerkt:* uit popup en open data; op 2026-10-05 ook uit de git-geschiedenis verwijderd (AVG).
- **✅ C3. Gevoeligheid van locaties.** *Antwoord:* bijna alles is al openbaar. *Verwerkt:* alles blijft getoond.
- **✅ C4. Link naar dodenakkers.nl per begraafplaats.** *Antwoord:* iets voor later. *Verwerkt:* wel artikelverwijzingen via de leeslijst.
- **✅ C5. Foto's.** *Antwoord:* liever geen foto's. *Verwerkt:* geen foto's.
- **✅ C6. Herbegravingen.** *Antwoord:* doe maar. *Verwerkt:* 35 herbegravingen (`data/herbegravingen.csv`), popup in beide richtingen en kaartlaag.
- **✅ C7. Dankwoord.** *Antwoord:* dat tabblad had niet mee gemoeten. *Verwerkt:* blijft ongeopend; geen dankwoord.
- **✅ C8. RCE-controle op ontbrekende begraafplaatsen.** *Antwoord:* niet nodig, Leon heeft dit al gedaan. *Verwerkt:* niet meer voorstellen.
- **✅ C9. Datering.** *Antwoord:* 1829 geen zinvolle grens; generiek; geen focus op WOII. *Verwerkt:* vóór 1700 · 1700–1799 · 1800–1849 · 1850–1899 · 1900–1949 · 1950–heden.

## D. Kleuren en leesbaarheid (René)

- **✅ D1. Kleuren.** *Antwoord:* prima; lichtroze en kleurovergangen zijn lastig, liever harde contrasten. *Verwerkt:* statuskleuren blijven; gezichten zonder lichte vulling; geruimd-ruit en -terrein met donkerbruine rand (contrast ≥ 3:1).
- **✅ D2. Contextlagen.** *Antwoord:* prima.
- **✅ D3. Leesbaarheid.** *Antwoord:* prima, zelfde als Zuid-Holland; telefoon wordt waarschijnlijk weinig gebruikt. *Verwerkt:* kleinste tekst nu 12 px.

## E. Layout en presentatie

- **✅ E1. Huisstijl.** *Antwoord:* logo en huisstijlkleur aangeleverd. *Verwerkt:* scherper logo; `#8d161c` voor titel, links en knoppen; favicon met grafpaaltje.
- **✅ E2. Introtekst.** *Antwoord:* prima zo.
- **✅ E3. Statusnamen.** *Antwoord:* "In gebruik" (zie A4).
- **✅ E4. Namen op de kaart.** *Antwoord:* geen namen is prima.
- **✅ E5. Standaard aan.** *Antwoord:* prima.
- **✅ E6. Mobiel.** *Antwoord:* werkt prima.
- **✅ E7. Extra pagina's.** *Antwoord:* statistiekpagina welkom; geen CSV-download; Engels misschien later. *Verwerkt:* statistiekpagina gebouwd.
- **✅ E8. Inbedden.** *Antwoord:* later misschien op www.funerair-erfgoed.nl, alleen via hun eigen sites; 2026-10-06: blijft hetzelfde. *Verwerkt:* inbedden alleen vanaf dodenakkers.nl; bij een besluit komt funerair-erfgoed.nl erbij.
- **✅ E9. Eigen webadres.** *Antwoord:* voorlopig goed zo; later met hun webmaster. *Verwerkt:* `SITE_URL` op één plek in `scripts/build_site.py`.

## F. Werkwijze

- **✅ F1. Correcties doorgeven.** *Antwoord:* een invulformulier met het nummer erbij. *Verwerkt:* GitHub-issueformulier; link "Correctie doorgeven" in elke popup.
- **✅ F2. Updates.** *Antwoord:* de Excel verandert vaker dan de KMZ's; shapes liggen redelijk vast. *Verwerkt:* elke run bouwt alles opnieuw uit de bron; controles per provincie.
- **✅ F3. Volgorde rest van Nederland.** *Antwoord:* geen voorkeur gegeven. *Verwerkt:* alle 12 provincies op de kaart (2026-10-05).
- **✅ F4. Publiek of niet.** *Antwoord:* intern tot de publicatie van het boek; niet indexeren. *Verwerkt:* `noindex`; publiceren met één schakelaar (`PUBLICEREN` in `scripts/build_site.py`), licentie: voorlopig zo laten (P1, hieronder).

## Navragen en vragen per provincie (ronde 2–3)

| Vraag | Antwoord | Verwerkt |
|---|---|---|
| N1 Wassenaar | Het metaheerhuis staat formeel niet op de Joodse begraafplaats; nader onderzoek volgt | Niets op de kaart veranderd |
| N2 Alkmaar | 7464 is de begraafplaats zelf; de RCE heeft hem niet aan complex 524892 toegevoegd | 7464 "hoort bij de begraafplaats" |
| N3 Beverwijk | "Duinhof" moet Duinrust zijn | Herbegraving `jb-ver-896` → `jb-loc-2804` |
| N3 Leerdam | Twee overbrengingen naar de voorste (grotere) begraafplaats | `jb-ver-498` en `jb-ver-774` → `jb-loc-366`. Dat 774 de tweede is, is afgeleid: de enige andere verdwenen begraafplaats in Leerdam |
| N3 Hoorn | Ja, inclusief stoffelijke resten | `jb-ver-168` → `jb-loc-2849` |
| N3 Dordrecht | Eerst naar de begraafplaats bij de gemeentelijke begraafplaats van Dordrecht, later een deel naar Strijen | `jb-ver-182` → `jb-loc-1912` én → `jb-loc-1945` |
| N4 | De eindjaar-kolom hoeft niet mee | Geen actie |
| G1 Gouda → Wageningen | Naar de nieuwe Joodse begraafplaats op de algemene begraafplaats | `jb-ver-280`, `jb-ver-281` → `jb-loc-2887` |
| G2 Winterswijk | Klopt helemaal | Blijft |
| G3 Moscowa | Aula en muur horen bij de Joodse begraafplaats | 516728 en 516729 "hoort bij de begraafplaats" |
| O1 Denekamp | Onze contour is de begraafplaats zelf, niet het hele perceel | Zie R2 hieronder |
| O2 Dedemsvaart | Contour opnieuw getekend; ligt naast het rijksmonument | Nieuw terrein + ingang uit `funerair_nieuwedata.kmz` (796 → 641 m²) |
| R2 Denekamp | Rijksmonument 12342 beschermt beide Joodse begraafplaatsen (uitzondering); de RCE-contour ligt om de nieuwe, voor de oude is geen contour (Leon 2026-10-06) | `jb-loc-2459` via `data/corrections.csv` rijksmonument 12342 (`jb-loc-2455` had het al) |
| P1 Licentie | Voorlopig zo laten; bij de publicatie kan er nog wat veranderen, zoals de icoontjes (Leon 2026-10-06) | Geen wijziging; `LICENSE` CC BY 4.0 blijft tot de publicatie |
| NB1 Putte | 516689 hoort bij de Frechie Foundation | Via `data/corrections.csv`; rest navraag [R3b](04-vragen-open.md#r3b-putte-de-rest-van-de-gegevens-van-mahsike-hadas) |
| NB2 Eindhoven | Woensel is in 1920 bij Eindhoven gevoegd; = Groenewoudseweg | `jb-ver-21` → `jb-loc-986` |
| L1 Sittard | Vrangendael = volksnaam van Lahrhof | `jb-ger-43`, `jb-ver-12` → `jb-loc-580` |
| L2 Venlo | 37192 hoort bij de Oude begraafplaats (`jb-loc-1125`); contour stond verkeerd | Nieuw terrein + ingang uit `funerair_nieuwedata.kmz` (43 → 248 m²); bij de Nieuwe "hoort bij een andere begraafplaats" |
| L3 Linne | Laat voorlopig staan | Blijft |

## Overige opmerkingen

- Joop (2026-10-05): op de leespagina geen "Uitgelicht" meer, alle artikelen gewoon in de lijst; vanuit de popup naar de artikelen verwijzen. *Verwerkt:* popup "Lees op Dodenakkers".
- Provincies zonder vragen: Fryslân (16 begraafplaatsen) en Flevoland (1).
