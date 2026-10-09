# 04 – Open vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-06 (nieuwe Excel verwerkt) · Kaart: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev · Gedeelde vragenpagina: https://claude.ai/artifact/9Rbm99cCckt7yGDwb52kg8

Alleen wat nog een antwoord nodig heeft. Alles wat beantwoord en verwerkt is staat in [05-vragen-beantwoord.md](05-vragen-beantwoord.md). Per vraag staat erbij **wat we nu doen**; zonder antwoord blijft dat zo.

Kenmerken als `jb-loc-1559` staan in de kaartpopup onder "Kenmerk": `loc` = in gebruik, `ver` = verdwenen, `ger` = geruimd, plus het Nr uit de Excel. Correcties kunnen ook via de link "Correctie doorgeven" in de popup.

## Samenvatting

| Code | Onderwerp | Wie |
|---|---|---|
| [Dr1](#dr1-emmen-welke-heet-westenesch) | Emmen: punten omgewisseld; graag de KMZ aanpassen | Leon |
| [OK1](#ok1-verdwenen-begraafplaatsen-op-oude-kaarten) | Verdwenen begraafplaatsen op oude kaarten: drie plekken | Leon |

---

### Dr1. Emmen: welke heet Westenesch?

De namen lijken gekruist tussen de Excel en de KMZ:

| Kenmerk | Excel-naam (jaar, Grootte) | Punt ligt in KMZ-terrein |
|---|---|---|
| `jb-loc-3075` | Begraafplaats **Westenesch** (1885, tot 1915; 400 m²) | "**Oude** Joodse begraafplaats, Emmen" (440 m²) |
| `jb-loc-2183` | Joodse Begraafplaats achter de Synagoge (1915; 480 m²) | "Joodse begraafplaats **Westenesch**, Emmen" (393 m²) |

Het puntlabel van 3075 is bovendien "**Nieuwe** Joodse begraafplaats, Emmen". Klopt de koppeling op ligging, en welke naam is juist?

*Antwoord Leon (2026-10-06):* "Ze zijn nu inderdaad verkeerd om." Hij controleert de KMZ nog.

*Nieuwe Excel (2026-10-06):* `jb-loc-3075` heet nu "Joodse begraafplaats Westenesch"; `jb-loc-2183` heet nog "Joodse Begraafplaats achter de Synagoge". De KMZ is niet nagestuurd, dus het terrein waarin het punt van 3075 ligt heet daar nog "Oude Joodse begraafplaats". Blijft dat zo (dan is de KMZ-naam fout), of komen de punten nog om?

*Leon (2026-10-09):* "Emmen lijkt nog steeds niet goed te gaan": de vragenpagina noemde Emmen al bij "nieuw", maar op de kaart stond Westenesch nog in het centrum.

*Oorzaak:* in `Locaties.kmz` staan de punten met Nr 3075 en 2183 op elkaars plek. De Excel klopt: Westenesch (1885–1915, 17 zerken) lag aan het Oranjekanaal in het westen ([JCK](https://jck.nl/joodse-gemeenten/emmen), [westenesch.nl](https://www.westenesch.nl/wp-content/uploads/2022/05/De-joodse-begraafplaats-aan-het-Oranjekanaal.pdf)); de begraafplaats achter de synagoge (1915, Beatrixstraat, 46 zerken) ligt in het centrum, waar het KMZ-punt ook al "Nieuwe Joodse begraafplaats, Emmen" heet.

*Nu:* de punten zijn omgewisseld via `data/punt_correcties.csv` (de handmatige terreinkoppeling van 2183 is vervallen). Gevraagd aan Leon: in `Locaties.kmz` de twee nummers omwisselen en in `Funerair Drenthe.kmz` het terrein in het centrum ("Oude Joodse begraafplaats, Emmen") hernoemen. Daarna kan de puntcorrectie weg.

### OK1. Verdwenen begraafplaatsen op oude kaarten

Elke begraafplaats heeft nu een link "Oude kaarten" (Bonnebladen, Waterstaatskaart en andere kaarten via Allmaps). Daarmee zijn de 69 verdwenen begraafplaatsen bekeken; het overzicht staat in [data/verdwenen-oude-kaarten.md](data/verdwenen-oude-kaarten.md). Bij 18 staat de begraafplaats op de oude kaart en klopt het punt. Bij drie wijst de oude kaart een andere plek aan:

- `jb-ver-491` De Bilt: het toponiem "Joden Kerkh." staat op het Bonneblad van 1872 50 tot 100 m oostzuidoostelijk van het punt.
- `jb-ver-613` Zwartsluis: "Begraafpl." circa 120 m noordelijk van het punt (1893). De Joodse of de algemene?
- `jb-ver-488` Zevenaar: "Begr.pl." 150 tot 200 m noordwestelijk (1866). Lag de Joodse begraafplaats daar?

Zelf kijken: open de begraafplaats, klik "Oude kaarten" en kies het jaar.

*Nu:* de punten blijven waar ze staan.

---

## Ter info (geen antwoord nodig)

Kleine dingen in de bronbestanden; we passen de bron niet aan.

- `Funerair Groningen.kmz`: "Joodse begraaf**plats**, Leens" (tikfout) en 7 lege "Naamloos Polygoon".
- `Locaties.kmz`: het label van `jb-loc-3574` is "Joodse begraafplaats, Uithuizen**?**" (met vraagteken). De kaart gebruikt sinds 2026-10-06 het nagestuurde punt uit `Voor Joop.kmz` (18 m verschoven).
- Denekamp (`jb-loc-2459`): in de nieuwe Excel staat Rmon 12342, maar Rijksmonument "Nee". De kaart zegt "ja" (antwoord R2).
- Maassluis en Puttershoek: in de nieuwe Excel geen verandering gezien. Zit die correctie in een KMZ, dan graag bij een volgende levering.
- Schiedam (`jb-ger-64`): Grootte "?"; de contour is volgens Leon nog niet bekend.
