# 01 – Data-analyse aangeleverde bestanden (Leon / Dodenakkers)

Datum: 2026-10-02 · Bron: `data-dodenakkers/` (aangeleverd door Leon Bok, niet in git)

## 1. Inventaris

| Bestand | Inhoud | Placemarks | Geometrie | Label staat in |
|---|---|---|---|---|
| `Joodse begraafplaatsen totaal voor Joop.xlsx` | De lijst: 315 Joodse begraafplaatsen NL | – | geen | – |
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

Overige tabbladen:
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
- Eigenaar/Postadres: organisaties (NIG, NIK) maar mogelijk ook personen → niet publiceren zonder akkoord.

## 6. Zuid-Holland in één oogopslag

36 objecten: 24 in gebruik (met terrein), 2 geruimd (met terrein), 10 verdwenen (alleen punt), verspreid over o.a. Rotterdam (7), Leiden (2), Gouda (2), Dordrecht (2), Schiedam (2), Rijswijk (2), Maassluis (2).
De verdwenen-records bevatten verwijzingen naar elkaar ("overgebracht naar Toepad", "naar Katwijk", "naar Strijen") — mogelijke latere feature: herbegravingslijnen.
