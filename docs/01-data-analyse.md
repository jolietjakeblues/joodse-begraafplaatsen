# 01 – Data-analyse aangeleverde bestanden (Leon / Dodenakkers)

Datum: 2026-10-02 · Bron: `data-dodenakkers/` (aangeleverd door Leon Bok, niet in git)

## 1. Inventaris

| Bestand | Inhoud | Placemarks | Geometrie | Label staat in |
|---|---|---|---|---|
| `Joodse begraafplaatsen voor Joop.xlsx` (sinds 2026-10-06; daarvoor `… totaal voor Joop.xlsx`) | De lijst: 315 Joodse begraafplaatsen NL | – | geen | – |
| `Locaties.kmz` | Puntlocaties (ingang) van **alle** funeraire objecten NL in de hoofddatabase | 4352 | Point | `name` = Nr, `description` = "Naam, Plaats" |
| `Verdwenen.kmz` | Punten verdwenen begraafplaatsen (alle religies) | 911 | Point | `name` = "Verdwenen 0001", `description` = label |
| `Geruimd.kmz` | Punten geruimde begraafplaatsen (alle religies) | 292 | Point | `name` = Nr, `description` = label "(geruimd)" |
| `Zuid-Holland.kmz` | Terreinen + punten ZH (alle funeraire objecten) | 890 (446 polygon, 444 point) | Point + Polygon | `name` = "Naam, Plaats" |
| `Funerair <Provincie>.kmz` (11×) | Idem, overige provincies | 46 – 1379 | Point + Polygon | `name` = "Naam, Plaats" |

Let op: de provinciebestanden en de drie puntbestanden bevatten **alle** begraafplaatsen, niet alleen Joodse. De Excel is de selectie.
Zeeland heet `Funerair Zeeland1.kmz`; Zuid-Holland heeft een afwijkende bestandsnaam (zonder "Funerair") en ook een eigen KML-stijl.

## 2. De Excel

Tabblad **Joodse begraafplaatsen**: 315 rijen (rest leeg), 30 kolommen:

`Nr, Naam, Sign, Bezoekadres, Huisnummer, NA, PC, Plaats, Gemeente, Provincie, Status, MIP, Rijksmonument, Gemeentelijk monument, Rmon, Link, Beschermd deel, Eigenaar, Postadres, PC Eig., Plaats(eigenaar), Jaartal, Circa, Grondvorm, Met, Muur, Bijzonderheden, Grootte, Kadaster, Laatste bezoek`

Verdeling per provincie / status:

| Provincie | In gebruik | Verdwenen | Geruimd | Totaal |
|---|---|---|---|---|
| Gelderland | 45 | 16 | 0 | 61 |
| Overijssel | 34 | 8 | 1 | 43 |
| **Zuid-Holland** | **24** | **10** | **2** | **36** |
| Noord-Brabant | 21 | 10 | 0 | 31 |
| Noord-Holland | 22 | 6 | 0 | 28 |
| Groningen | 23 | 2 | 2 | 27 |
| Limburg | 18 | 6 | 1 | 25 |
| Drenthe | 20 | 1 | 0 | 21 |
| Utrecht | 14 | 6 | 0 | 20 |
| Fryslân | 11 | 4 | 1 | 16 |
| Zeeland | 6 | 0 | 0 | 6 |
| Flevoland | 1 | 0 | 0 | 1 |
| **Totaal** | **239** | **69** | **7** | **315** |

Overige tabbladen (alleen in de Excel tot 2026-10-06; de nieuwe Excel heeft er één tabblad met daarin ook de kolommen Contactpersoon, Telefoon, E-mail, Website en Foto Beeldbank, die niet worden ingelezen):
- `statistiek` – formules (COUNTIF) per provincie; afgeleid, niet nodig.
- `Archieven` – archief per gemeente (66 rijen); mogelijk later bruikbaar als verwijzing.
- **`Dank en informeren` – namen, e-mailadressen, telefoonnummers van privépersonen. Persoonsgegevens: nooit inlezen in de pipeline, nooit publiceren.**

## 3. Nummering — NIET uniek (belangrijkste bevinding)

`Nr` is niet uniek in de Excel: 5 nummers komen 2× voor (9, 21, 43, 369, 874). Maar:

**`Nr` is uniek binnen de status, en verwijst per status naar een ander bronbestand:**

| Status in Excel | `Nr` verwijst naar | Resultaat |
|---|---|---|
| In gebruik (239) | `Locaties.kmz` → placemark `name` | 239/239 gevonden |
| Verdwenen / verdwenen (69) | `Verdwenen.kmz` → "Verdwenen NNNN" | 69/69 gevonden |
| Geruimd (7) | `Geruimd.kmz` → placemark `name` | 7/7 gevonden |

De combinatie **(reeks, Nr)** is uniek in de Excel (0 dubbelen) en koppelt alle 315 rijen aan een punt. Dit bevestigt Leons opmerking dat "de nummers op puntlocatie wel alle gevonden kunnen worden".
Controle: 8 rijen leken op het eerste gezicht niet te matchen, maar hebben gewoon geen "Joods" in het KML-label (bv. "Oude Isr. begraafplaats, Winterswijk", "Sombre Hadas, Putte" ↔ Excel "Shomre Hadas"). Andersom: er zijn géén Joodse placemarks in Locaties/Verdwenen die niet in de Excel staan.

Verdere uniciteitsvalkuilen:
- `Geruimd.kmz` heeft zelf een dubbel nummer: **245** = "NH kerkhof, Puttershoek" én "H Martinuskerkhof, Pannerden" (niet Joods, maar de parser moet het aankunnen).
- Een Nr uit de ene reeks kan in een andere reeks een totaal ander object zijn (bv. Nr 874 in Locaties = Rijswijk (Joods), in Verdwenen = Oude joodse begraafplaats Hilversum). **Nooit opzoeken zonder reeks.**
- **Ook namen zijn niet uniek**: Excel 471 en 872 heten allebei "Portugees Israëlitische Begraafplaats Crooswijk" (Rotterdam), maar liggen 430 m uit elkaar en hebben andere jaartallen (1696 resp. 1877) → twee verschillende objecten.
- In de provinciale KML's komt elk object 2× voor (Point + Polygon met dezelfde naam), en sommige namen nog vaker (grensgebieden in meerdere bestanden, generieke namen als "Gem. begraafplaats, X").

→ **Interne sleutel voorstel:** `jb-<reeks>-<nr>` met reeks ∈ {`loc`, `ver`, `ger`}, bv. `jb-loc-1559`, `jb-ver-182`, `jb-ger-68`.

## 4. Koppeling punt → terrein (polygoon), Zuid-Holland

Polygonen zitten alleen in de provinciebestanden en zijn alleen **op naam** te vinden — daar zit de discrepantie waar Leon voor waarschuwde. Getest met point-in-polygon van het (reeks, Nr)-punt in `Zuid-Holland.kmz`:

| Groep ZH | Aantal | Punt ligt in polygoon | Naam KML = label puntbestand |
|---|---|---|---|
| In gebruik | 24 | 24 | 21 (3 afwijkend) |
| Geruimd | 2 | 2 | 1 (1 afwijkend) |
| Verdwenen | 10 | n.v.t. – geen terrein | – |

Naamsafwijkingen die alléén via ruimtelijke koppeling goed gaan:

| Nr | Label puntbestand | Naam polygoon in Zuid-Holland.kmz |
|---|---|---|
| loc-874 | Joods deel begraafplaats Oud-Rijswijk, Rijswijk | Joods deel op Oud Rijswijk, Rijswijk |
| loc-4200 | Joodse begraafplaats Toepad, Rotterdam | Joodse begraafplaats Het Toepad, Rotterdam |
| ger-64 | Joodse begraafplaats, Schiedam (geruimd) | Nieuwe Joodse begraafplaats, Schiedam (geruimd) |

En valse treffers die je krijgt als je **alleen** op naam of **alleen** ruimtelijk koppelt:
- **ver-182** "Joodse begraafplaats, Dordrecht" (verdwenen, 1738–1958) heeft exact dezelfde naam als de huidige begraafplaats loc-1912 — die ligt 833 m verderop. Naam-match zou de verdwenen plek het terrein van de huidige geven. Fout.
- **ver-471** Crooswijk (verdwenen 1807) ligt ruimtelijk ín de polygoon "RK St. Laurentius, Rotterdam" – klopt historisch ("later RK begraafplaats"), maar het is niet het Joodse terrein. Ruimtelijk alleen zou fout koppelen.

→ **Regel:** polygoon alleen koppelen voor `in gebruik` en `geruimd`, via *punt ligt in polygoon* **én** naamsimilariteit (genormaliseerd, "Joods" in naam). Verdwenen = altijd alleen punt. Afwijkingen in een rapport voor Leon, niet stil oplossen.

Alle 26 Joodse polygonen in Zuid-Holland.kmz zijn hiermee gekoppeld; er blijven er 0 over.

## 5. Datakwaliteit Excel (normaliseren, niet stil corrigeren)

- `Status`: "Verdwenen" en "verdwenen" (2×) → normaliseren naar 3 waarden.
- `Grondvorm`: "Recht"/"recht"; `Rmon`: "Geen"/"geen"/nummer; `Met`, `Kadaster`: ja/nee/Ja/Nee.
- `Jaartal`: getal of tekst ("onbekend"); `Circa` als losse vlag. `Grootte`: m² of "?".
- `Rijksmonument` = Ja/Nee; `Rmon` = rijksmonumentnummer → koppelbaar aan RCE. `Link` (70×) = monumentenregister-URL.
- Spelfouten in labels (bv. "Joodse begraafplats, Maassluis" in Verdwenen.kmz; "Sombre Hadas" vs "Shomre Hadas").
- `Bijzonderheden` bevat historisch waardevolle vrije tekst (sluiting, ruiming, "overgebracht naar ...") → in popup tonen.
- Provincie "Fryslân" in Excel (Friesland in bestandsnaam).
- Gemeentelijke herindelingen: Excel-`Gemeente` kan verouderd zijn (vgl. Vijfheerenlanden in dodenakkers) → later checken tegen PDOK-gemeentegrenzen.
- Eigenaar/Postadres: organisaties (NIG, NIK) maar mogelijk ook personen → niet publiceren. Besluit ronde 2 (C2): helemaal niet tonen en niet in de open data.

## 6. Zuid-Holland in één oogopslag

36 objecten: 24 in gebruik (met terrein), 2 geruimd (met terrein), 10 verdwenen (alleen punt), verspreid over o.a. Rotterdam (7), Leiden (2), Gouda (2), Dordrecht (2), Schiedam (2), Rijswijk (2), Maassluis (2).
De verdwenen-records bevatten verwijzingen naar elkaar ("overgebracht naar Toepad", "naar Katwijk", "naar Strijen") — mogelijke latere feature: herbegravingslijnen.

## 7. Bevindingen bij uitbreiding naar West-Nederland (2026-10-02)

Na Zuid-Holland zijn Utrecht, Noord-Holland, Zeeland en Flevoland verwerkt (91 begraafplaatsen). Alle tellingen per provincie kloppen met de Excel. Nieuw geleerd over de bron:

- **Polygoonnamen volgen niet altijd "Naam, Plaats"** — Utrecht-KMZ heeft o.a. "Joods veenendaal", "Joods Maarssen". De naamtoets haalt de plaats daarom ook zonder komma weg.
- **Excel-naam is soms de enige brug**: Ouderkerk heet in het puntbestand "Portugees-Joodse begraafplaats", in de KMZ "Beth Haim"; alleen de Excel-naam ("… Beth Haim") verbindt ze. De naamtoets gebruikt nu puntlabel én Excel-naam, en telt het als goed als alle kernwoorden van de terreinnaam in de andere naam staan.
- **Oppervlakte als controle**: terreinoppervlak (RD) vs `Grootte` — 64 van 68 terreinen binnen 75–133 %. Afwijkers: Beverwijk (137 vs 870), Almere (2.854 vs 4.875), Goes (1.057 vs 670), Vlissingen Leeuwentrap (694 vs 350).
- **Waarschijnlijk gekopieerde polygonen**: Vlissingen oud/nieuw (beide exact 694 m², 551 m uit elkaar); Rhenen/Edam (beide 372 m²) mogelijk toeval.
- **Ontbrekend terrein**: Bilthoven, Progressieve joodse begraafplaats — geen polygoon in de KMZ.
- **`Rmon` is vaak een complexnummer** (8 van 19) — opgelost via RCE (`ceo:complexnummer` → onderdelen).
- **"In gebruik" omvat ook gesloten begraafplaatsen** (Haarlem Kleverlaan "1969 gesloten") → eerst "Bestaand" genoemd; sinds ronde 2 (A4/E3) weer "In gebruik".
- Kolomwaarden: `NA` ∈ {bij, tegenover, achter, to}; `Muur` leeg in heel West; `Grondvorm` overal "Recht"; `Gemeentelijk monument` soms "Geen".

Alle open punten: [04-vragen-open.md](04-vragen-open.md); afgehandeld: [05-vragen-beantwoord.md](05-vragen-beantwoord.md).

## 8. Antwoorden Dodenakkers (2026-10-02)

- `NA` = nader adres; `Muur` = muur rondom (ja/nee); `Kadaster` = als begraafplaats geregistreerd bij het Kadaster (ja/nee); `Met` = metaheerhuis; `MIP` = Monumenten Inventarisatie Project.
- Verdwenen begraafplaatsen: alleen een puntlocatie beschikbaar. Bilthoven (`jb-loc-4368`): alleen punt, geen terrein.
- Een complexnummer in `Rmon` kan voorkomen.
- Weergavenamen vastgesteld voor Toepad, Oud-Rijswijk en Schiedam (via `data/corrections.csv`).

## 9. Bevindingen rest van Nederland en ronde 2–3 (2026-10-05)

Alle 12 provincies verwerkt; alle 315 Excel-rijen gekoppeld (239 in gebruik, 7 geruimd, 69 verdwenen; 244 terreinen). Nieuw geleerd:

- **Synoniemen en tikfouten breken de naamtoets**: "Israëlitisch" ↔ "Joods" (Enschede 2×), "begraafplats" (Leens). Oplossing: `data/terrein_koppelingen.csv` als het punt in het terrein ligt en het oppervlak ≈ `Grootte`; de drempel nooit verlagen.
- **"Binnen gaat voor nabij" kan misgaan**: in Uithuizen ligt het punt 1 m buiten het Joodse terrein maar binnen de oude algemene begraafplaats, die toevallig de naamtoets haalde ("joodse" ~ "oude"). Per provincie de lijst kenmerk/label/terrein/oppervlak nalopen.
- **Gekruiste namen** (Emmen, vraag Dr1): de Excel noemt een ander terrein "Westenesch" dan de KMZ. Gekoppeld op ligging.
- **Geen terrein**: Bilthoven (bevestigd). Loppersum kreeg op 2026-10-06 een terrein uit `Voor Joop.kmz`.
- **RCE-punten op de verkeerde begraafplaats**: Venlo 37192 en Putte 516689 liggen volgens de RCE op een buurbegraafplaats → `BEOORDEELDE_RELATIES` (`hoort_bij_andere`), niet verplaatsen.
- **Nagestuurde terreinen** in `funerair_nieuwedata.kmz` (Venlo oud, Dedemsvaart): vervangen het terrein met dezelfde naam; het punt wordt de ingang.
- **Bijzonderheden kunnen een getal zijn** in de Excel ("-1883", Loppersum) → altijd als tekst inlezen.
- **Provincie-KMZ kan lege polygonen bevatten** ("Naamloos Polygoon", Groningen 7×).
- Antwoorden Leon/René: `Grootte` = oppervlakte van de Google Earth-shape; `Jaartal` = aanleg of eerste begraving; `Circa` = bij benadering; "Geen" = "Nee"; Muur, Kadaster, Grondvorm, Laatste bezoek en Eigenaar niet tonen; "In gebruik" blijft de statusnaam (Joodse begraafplaatsen worden niet gesloten).
