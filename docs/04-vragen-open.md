# 04 – Open vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-06 · Kaart: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev · Gedeelde vragenpagina: https://claude.ai/artifact/9Rbm99cCckt7yGDwb52kg8

Alleen wat nog een antwoord nodig heeft. Alles wat beantwoord en verwerkt is staat in [05-vragen-beantwoord.md](05-vragen-beantwoord.md). Per vraag staat erbij **wat we nu doen**; zonder antwoord blijft dat zo.

Kenmerken als `jb-loc-1559` staan in de kaartpopup onder "Kenmerk": `loc` = in gebruik, `ver` = verdwenen, `ger` = geruimd, plus het Nr uit de Excel. Correcties kunnen ook via de link "Correctie doorgeven" in de popup.

## Samenvatting

| Code | Onderwerp | Wie |
|---|---|---|
| [R1](#r1-welke-naam-komt-op-de-kaart) | Welke naam op de kaart: Excel-naam of KMZ-naam? | Leon |
| [R2](#r2-denekamp-is-12342-het-rijksmonument-van-de-joodse-begraafplaats) | Denekamp: is 12342 het rijksmonument van de Joodse begraafplaats? | Leon |
| [R3](#r3-de-gecorrigeerde-excel) | De gecorrigeerde Excel | Leon |
| [R3b](#r3b-putte-de-rest-van-de-gegevens-van-mahsike-hadas) | Putte: de rest van de gegevens van Mahsike Hadas | Leon |
| [Gr1](#gr1-loppersum-terrein-van-de-geruimde-begraafplaats) | Loppersum: terrein van de geruimde begraafplaats? | Leon |
| [Dr1](#dr1-emmen-welke-heet-westenesch) | Emmen: welke heet Westenesch? | Leon |
| [OK1](#ok1-verdwenen-begraafplaatsen-op-oude-kaarten) | Verdwenen begraafplaatsen op oude kaarten: drie plekken | Leon |
| [P1](#p1-hergebruik-en-licentie-bij-de-publicatie) | Hergebruik en licentie bij de publicatie | Leon, René |
| [E8](#e8-inbedden-later) | Inbedden op funerair-erfgoed.nl (later) | Dodenakkers |

---

### R1. Welke naam komt op de kaart?

Ronde 2: "houd de Excel-naam aan". Ronde 3: "groen is de juiste", en groen waren de terreinnamen uit de KMZ (bijvoorbeeld "Hoogduitse Joodse begraafplaats" in Middelburg, "Nieuwe Joodse begraafplaats" in Vlissingen, "Beth Haim" in Ouderkerk, "Joodse begraafplaats Diemen / Muiderberg"). Past Leon de namen in de Excel aan, of moeten wij de groene namen als weergavenaam instellen?

*Nu:* de naam uit de Excel (drie weergavenamen via `data/corrections.csv`: Toepad, Oud-Rijswijk, Schiedam).

### R2. Denekamp: is 12342 het rijksmonument van de Joodse begraafplaats?

Antwoord ronde 3: "Het overlapt inderdaad, maar onze contour is de daadwerkelijke begraafplaats, niet het hele perceel." Is RCE-monument 12342 dan het rijksmonument van de Joodse begraafplaats (met een ruimere grens)? Dan zou de Excel bij `jb-loc-2459` "rijksmonument: ja" en Rmon 12342 moeten hebben.

*Nu:* in de popup als "overlapt het terrein".

### R3. De gecorrigeerde Excel

Leon heeft in de Excel Putte (516689 bij de Frechie Foundation), Maassluis en Puttershoek gecorrigeerd. Die versie hebben we nog niet. Graag in de gedeelde map.

*Nu:* Putte is alvast via `data/corrections.csv` aangepast; de rest wacht op de nieuwe Excel.

### R3b. Putte: de rest van de gegevens van Mahsike Hadas

Bij Mahsike Hadas (`jb-loc-189`) staan in de Excel ook "rijksmonument: ja" en als beschermd deel "poorten, aula, ontvangstgebouw, grafmonument". Die aula en grafmonumenten liggen volgens de RCE op de Frechie Foundation (`jb-loc-195`).

- Horen die gegevens ook bij de Frechie Foundation?
- Is Mahsike Hadas zelf een rijksmonument?

*Nu:* Mahsike Hadas "rijksmonument: ja" zonder nummer.

### Gr1. Loppersum: terrein van de geruimde begraafplaats?

Voor `jb-ger-247` (Oude Joodse begraafplaats, Grootte 104 m²) staat geen terrein in `Funerair Groningen.kmz`; het dichtstbijzijnde Joodse terrein is de huidige begraafplaats, 353 m verderop. Is er een terrein, of blijft het een punt (zoals Bilthoven)?

*Nu:* alleen een punt.

### Dr1. Emmen: welke heet Westenesch?

De namen lijken gekruist tussen de Excel en de KMZ:

| Kenmerk | Excel-naam (jaar, Grootte) | Punt ligt in KMZ-terrein |
|---|---|---|
| `jb-loc-3075` | Begraafplaats **Westenesch** (1885, tot 1915; 400 m²) | "**Oude** Joodse begraafplaats, Emmen" (440 m²) |
| `jb-loc-2183` | Joodse Begraafplaats achter de Synagoge (1915; 480 m²) | "Joodse begraafplaats **Westenesch**, Emmen" (393 m²) |

Het puntlabel van 3075 is bovendien "**Nieuwe** Joodse begraafplaats, Emmen". Klopt de koppeling op ligging, en welke naam is juist?

*Nu:* gekoppeld op ligging, met de namen uit de Excel.

### OK1. Verdwenen begraafplaatsen op oude kaarten

Elke begraafplaats heeft nu een link "Oude kaarten" (Bonnebladen, Waterstaatskaart en andere kaarten via Allmaps). Daarmee zijn de 69 verdwenen begraafplaatsen bekeken; het overzicht staat in [data/verdwenen-oude-kaarten.md](data/verdwenen-oude-kaarten.md). Bij 18 staat de begraafplaats op de oude kaart en klopt het punt. Bij drie wijst de oude kaart een andere plek aan:

- `jb-ver-491` De Bilt: het toponiem "Joden Kerkh." staat op het Bonneblad van 1872 50 tot 100 m oostzuidoostelijk van het punt.
- `jb-ver-613` Zwartsluis: "Begraafpl." circa 120 m noordelijk van het punt (1893). De Joodse of de algemene?
- `jb-ver-488` Zevenaar: "Begr.pl." 150 tot 200 m noordwestelijk (1866). Lag de Joodse begraafplaats daar?

Zelf kijken: open de begraafplaats, klik "Oude kaarten" en kies het jaar.

*Nu:* de punten blijven waar ze staan.

### P1. Hergebruik en licentie bij de publicatie

Onder welke voorwaarden mogen anderen de kaart en de gegevens hergebruiken als de kaart bij het boek openbaar wordt? Bijvoorbeeld vrij hergebruik met naamsvermelding van stichting Dodenakkers (CC BY 4.0), of alleen bekijken. Mag de kaart dan ook op andere websites getoond worden?

*Nu:* de methodepagina zegt alleen dat dit bij de publicatie bekend wordt gemaakt. De repository heeft een `LICENSE` (CC BY 4.0) die we daarna gelijktrekken.

### E8. Inbedden (later)

Antwoord ronde 3: later misschien op www.funerair-erfgoed.nl, alleen via de eigen sites van Dodenakkers.

*Nu:* inbedden mag alleen vanaf dodenakkers.nl. Bij een besluit voegen we funerair-erfgoed.nl toe.

---

## Ter info (geen antwoord nodig)

Kleine dingen in de bronbestanden; we passen de bron niet aan.

- `Funerair Groningen.kmz`: "Joodse begraaf**plats**, Leens" (tikfout) en 7 lege "Naamloos Polygoon".
- `Locaties.kmz`: het label van `jb-loc-3574` is "Joodse begraafplaats, Uithuizen**?**" (met vraagteken). Het punt ligt 1 m buiten het Joodse terrein, binnen de oude algemene begraafplaats; met de hand aan het Joodse terrein gekoppeld.
- Schiedam (`jb-ger-64`): Grootte "?"; de contour is volgens Leon nog niet bekend.
