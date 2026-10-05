# Koppelrapport Joodse begraafplaatsen

Gegenereerd door `scripts/build_base_dataset.py`.
Provincie(s): **Drenthe, Flevoland, Fryslân, Gelderland, Groningen, Limburg, Noord-Brabant, Noord-Holland, Overijssel, Utrecht, Zeeland, Zuid-Holland**. Excel-rijen landelijk: 315.

## Samenvatting

- 315 begraafplaatsen: 239 in gebruik, 7 geruimd, 69 verdwenen.
- Elk record is via (reeks, Nr) aan precies één punt gekoppeld; sleutel `jb-<reeks>-<Nr>`.
- Terreinen gekoppeld: 244.

## Koppelwijze terrein

| koppelwijze | aantal |
|---|---|
| binnen_naam_gelijk | 191 |
| binnen_naamvariant | 41 |
| correctie_kmz | 2 |
| geen_terrein | 1 |
| geen_terrein_bevestigd | 1 |
| handmatig | 6 |
| nabij_naam_gelijk | 4 |
| niet_van_toepassing | 69 |

## Ter controle voor Dodenakkers: naamvarianten

Het punt ligt in (of vlak bij) het terrein, maar de naam van het terrein in de provincie-KMZ wijkt af van het label van het punt.

| id | label punt | naam terrein | koppelwijze | status |
|---|---|---|---|---|
| `jb-loc-3075` | Nieuwe Joodse begraafplaats, Emmen | Oude Joodse begraafplaats, Emmen | binnen_naamvariant | open |
| `jb-loc-2224` | Joodse begraafplaats, Nieuw Amsterdam | Joodse begraafplaats, Veenoord | binnen_naamvariant | open |
| `jb-loc-3499` | Joodse begraafplaats, Hoogersmilde | Joods Hoogersmilde | binnen_naamvariant | open |
| `jb-loc-3042` | Joods begraafplaats Tacozijl, Lemmer | Tacozijl | binnen_naamvariant | open |
| `jb-loc-1250` | Joodse begraafplaats, Harlingen | Joods Harlingen | binnen_naamvariant | open |
| `jb-loc-2962` | Joodse begraafplaats De Knipe, Heerenveen | joods De Knipe | binnen_naamvariant | open |
| `jb-loc-2947` | Joodse begraafplaats, Heerenveen | Joods H'veen | binnen_naamvariant | open |
| `jb-ger-80` | Oude joodse begraafplaats, Bolsward | Oude joodse begraafplaats, Bolsward (geruimd) | binnen_naamvariant | open |
| `jb-loc-3512` | Joodse begraafplaats, Sneek | Joods Sneek | binnen_naamvariant | open |
| `jb-loc-4304` | Joodse begraafplaats op de gemeentelijk begraafplaats, Sneek | Joodse begraafplaats op de gemeentelijke begraafplaats, Sneek | binnen_naamvariant | open |
| `jb-loc-3567` | Joodse begraafplaats, Workum | Joods Workum | binnen_naamvariant | open |
| `jb-loc-3992` | Joodse begraafplaats Lichtenvoorde, Vragender | Joodse begraafplaats, Vragender | binnen_naamvariant | open |
| `jb-loc-2701` | Joodse Begraafplaats Wisch, Heelweg | Joodse begraafplaats, Heelweg | binnen_naamvariant | open |
| `jb-loc-4219` | Oude Joodse begraafplaats, Wageningen | Joodse begraafplaats, Wageningen | binnen_naamvariant | open |
| `jb-loc-1669` | Joodse begraafplaats, Herwijnen | Joodse begraafplaats, Herwijnen | nabij_naam_gelijk | open |
| `jb-loc-2623` | Joodse begraafplaats Bossche Poort, Zaltbommel | Joodse begraafplaats Bossche Poort, Zaltbommel | nabij_naam_gelijk | open |
| `jb-loc-3529` | Joodse begraafplaats, Ommelanderwijk | Joodse begraafplaats, Ommelanderwijk | nabij_naam_gelijk | open |
| `jb-loc-3335` | Joodse begraafplaats Hebrecht, Vlagtwedde | Joodse begraafplaats, Vlagtwedde | binnen_naamvariant | open |
| `jb-loc-671` | Joodse begraafplaats, Maastricht | Joods Maastricht | binnen_naamvariant | open |
| `jb-loc-719` | Joodse begraafplaats, Rothem | Joods Rothem | binnen_naamvariant | open |
| `jb-loc-513` | Oud Joodse begraafplaats, Roermond | Oude Joodse | binnen_naamvariant | open |
| `jb-loc-562` | Nieuw Joodse begraafplaats, Roermond | Nieuwe Joodse | binnen_naamvariant | open |
| `jb-ger-43` | Joodse begraafplaats op Fort Sanderbout, Sittard (geruimd) | Joodse begraafplaats Fort Sanderbout, Sittard | binnen_naamvariant | open |
| `jb-loc-580` | Joodse begraafplaats, Sittard | Joodse begraafplaats Lahrhof, Sittard | binnen_naamvariant | open |
| `jb-loc-648` | Joodse begraafplaats, Valkenburg | Joods Valkenburg | binnen_naamvariant | open |
| `jb-loc-2175` | Joodse begraafplaats, Heusden | Joodse begraafplaats Heesbeen, Heusden | binnen_naamvariant | open |
| `jb-loc-192` | Sombre Hadas, Putte | Shomre Hadas, Putte | binnen_naamvariant | open |
| `jb-loc-2801` | Begraafplaats Psychiatrisch Ziekenhuis, Bloemendaal | Joodse begraafplaats Psych ziekenhuis, Bloemendaal | binnen_naamvariant | open |
| `jb-loc-1381` | Joodse begraafplaats, Diemen | Joodse begraafplaats A'dam, Diemen | binnen_naamvariant | open |
| `jb-loc-3369` | Joodse begraafplaats, Muiderberg | Joodse begraafplaats A'dam, Muiderberg | binnen_naamvariant | open |
| `jb-loc-1439` | Portugees-Joodse begraafplaats, Ouderkerk aan de Amstel | Beth Haim, Ouderkerk aan de Amstel | binnen_naamvariant | open |
| `jb-loc-2523` | Joodse begraafplaats, Monnickendam | Joodse begraafplaats, Monnickendam | nabij_naam_gelijk | open |
| `jb-loc-2400` | Nieuwe joodse begraafplaats, Almelo | Joodse begraafplaats, Almelo | binnen_naamvariant | open |
| `jb-loc-4015` | Joodse begraafplaats aan het Mulopaadje, Hardenberg | Joodse begraafplaats, Hardenberg | binnen_naamvariant | open |
| `jb-loc-3306` | Joodse begraafplaats De Pol, Willemsoord | Joodse begraafplaats, De Pol | binnen_naamvariant | open |
| `jb-loc-2740` | Joodse begraafplaats, Den Ham | Nieuwe Joodse begraafplaats, Den Ham | binnen_naamvariant | open |
| `jb-loc-1458` | Oud Joodse begraafplaats, Amersfoort | Oude joodse begraafplaats, Amersfoort | binnen_naamvariant | open |
| `jb-loc-1459` | Nieuw Joodse begraafplaats, Amersfoort | Nieuwe joodse begraafplaats, Amersfoort | binnen_naamvariant | open |
| `jb-loc-1643` | Joodse begraafplaats, Maarssen | Joods Maarssen | binnen_naamvariant | open |
| `jb-loc-4171` | Joodse begraafplaats, Veenendaal | Joods veenendaal | binnen_naamvariant | open |
| `jb-loc-21` | Hoogduitse begraafplaats, Middelburg | Hoogduitse Joodse begraafplaats, Middelburg | binnen_naamvariant | open |
| `jb-loc-908` | Joodse begraafplaats, Vlissingen | Nieuwe Joodse begraafplaats, Vlissingen | binnen_naamvariant | open |
| `jb-loc-874` | Joods deel begraafplaats Oud-Rijswijk, Rijswijk | Joods deel op Oud Rijswijk, Rijswijk | binnen_naamvariant | naam vastgesteld: Joods deel op Oud-Rijswijk (Leon/René) |
| `jb-loc-4200` | Joodse begraafplaats Toepad, Rotterdam | Joodse begraafplaats Het Toepad, Rotterdam | binnen_naamvariant | naam vastgesteld: Begraafplaats Toepad (Leon/René) |
| `jb-ger-64` | Joodse begraafplaats, Schiedam (geruimd) | Nieuwe Joodse begraafplaats, Schiedam (geruimd) | binnen_naamvariant | naam vastgesteld: Nieuwe Joodse begraafplaats (Leon/René) |

## Oppervlakte terrein wijkt sterk af van Excel-kolom `Grootte`

Terreinoppervlak (KMZ, berekend in RD) buiten 75–133 % van `Grootte`. Mogelijk verkeerd terrein, of een verouderde/afwijkende maat in de Excel.

| id | label punt | terrein | terrein m² | Grootte m² |
|---|---|---|---|---|
| `jb-loc-2215` | Joodse begraafplaats, Rolde | Joodse begraafplaats, Rolde | 346 | 523 |
| `jb-loc-3202` | Joodse begraafplaats, Gees | Joodse begraafplaats, Gees | 531 | 275 |
| `jb-loc-2226` | Joodse begraafplaats, Sleen | Joodse begraafplaats, Sleen | 2.179 | 1.180 |
| `jb-loc-3316` | Joodse begraafplaats, Ruinen | Joodse begraafplaats, Ruinen | 426 | 740 |
| `jb-loc-2188` | Joodse begraafplaats, Roswinkel | Joodse begraafplaats, Roswinkel | 94 | 135 |
| `jb-loc-3301` | Oude Joodse begraafplaats, Hoogeveen | Oude joodse begraafplaats, Hoogeveen | 375 | 550 |
| `jb-loc-3295` | Joodse begraafplaats, Beilen | Joodse begraafplaats, Beilen | 667 | 910 |
| `jb-loc-3557` | Joodse begraafplaats, Zuidlaren | Joodse begraafplaats, Zuidlaren | 375 | 760 |
| `jb-loc-2369` | Joodse begraafplaats, Almere | Joodse begraafplaats, Almere | 2.854 | 4.875 |
| `jb-loc-1250` | Joodse begraafplaats, Harlingen | Joods Harlingen | 879 | 600 |
| `jb-loc-2962` | Joodse begraafplaats De Knipe, Heerenveen | joods De Knipe | 108 | 545 |
| `jb-loc-2947` | Joodse begraafplaats, Heerenveen | Joods H'veen | 399 | 814 |
| `jb-loc-4304` | Joodse begraafplaats op de gemeentelijk begraafplaats, Sneek | Joodse begraafplaats op de gemeentelijke begraafplaats, Sneek | 29 | 10 |
| `jb-loc-3059` | Joodse begraafplaats, De Maten | Joodse begraafplaats, De Maten | 178 | 55 |
| `jb-loc-1125` | Oude Joodse begraafplaats, Venlo | Oude Joodse begraafplaats, Venlo | 248 | 45 |
| `jb-loc-2804` | Joodse begraafplaats, Beverwijk | Joodse begraafplaats, Beverwijk | 137 | 870 |
| `jb-loc-2399` | Joodse begraafplaats, Borne | Joodse begraafplaats, Borne | 3.721 | 2.065 |
| `jb-loc-2297` | Joodse begraafplaats, Dalfsen | Joodse begraafplaats, Dalfsen | 420 | 830 |
| `jb-loc-4224` | Joodse begraafplaats, Deventer | Joodse begraafplaats, Deventer | 4.373 | 2.980 |
| `jb-loc-2531` | Joodse begraafplaats, Delden | Joodse begraafplaats, Delden | 778 | 8.100 |
| `jb-loc-1359` | Joodse begraafplaats, Raalte | Joodse begraafplaats, Raalte | 726 | 1.130 |
| `jb-loc-3306` | Joodse begraafplaats De Pol, Willemsoord | Joodse begraafplaats, De Pol | 165 | 300 |
| `jb-loc-238` | Joodse begraafplaats, Goes | Joodse begraafplaats, Goes | 1.057 | 670 |
| `jb-loc-9` | Joodse begraafplaats bij de Leeuwentrap, Vlissingen | Oude joodse begraafplaats, Vlissingen | 694 | 350 |

## Handmatige terreinkoppelingen (`data/terrein_koppelingen.csv`)

- `jb-loc-2183` Joodse begraafplaats, Emmen → Joodse begraafplaats Westenesch, Emmen (393 m², Grootte 480)
- `jb-loc-3939` Joodse begraafplaats, Leens → Joodse begraafplats, Leens (150 m², Grootte 150)
- `jb-loc-3574` Joodse begraafplaats, Uithuizen? → Joodse begraafplaats, Uithuizen (202 m², Grootte 200)
- `jb-loc-3027` Oude Isr. begraafplaats, Enschede → Joodse begraafplaats Kneedweg, Enschede (3475 m², Grootte 3460)
- `jb-loc-3002` Israelitische begraafplaats, Enschede → Nw. Joodse begraafplaats, Enschede (16023 m², Grootte 18800)
- `jb-loc-9` Joodse begraafplaats bij de Leeuwentrap, Vlissingen → Oude joodse begraafplaats, Vlissingen (694 m², Grootte 350)

## Gecorrigeerde terreinen en ingangen (`funerair_nieuwedata.kmz`)

| id | terrein | oud m² | nieuw m² | ingang verschoven |
|---|---|---|---|---|
| `jb-loc-1125` | Oude Joodse begraafplaats, Venlo | 43 | 248 | 9.9 m |
| `jb-loc-4021` | Joodse begraafplaats, Dedemsvaart | 796 | 641 | 34.6 m |

## Joodse terreinen met exact dezelfde oppervlakte (mogelijk gekopieerde polygoon)

- Joodse begraafplaats, Beilen en Nieuwe Joodse begraafplaats, Venlo: 667 m² (afstand 170397 m)
- Joodse begraafplaats, Zuidlaren en Oude joodse begraafplaats, Hoogeveen: 375 m² (afstand 42931 m)
- Joods H'veen en Joodse begraafplaats, Bellingwolde: 399 m² (afstand 84141 m)
- Joodse begraafplaats, Elburg en Joodse begraafplaats, Werkendam: 579 m² (afstand 95778 m)
- Joodse begraafplaats, Elburg en Joodse begraafplaats, Wijk bij Duurstede: 579 m² (afstand 62509 m)
- Joodse begraafplaats, Hattem en Joodse begraafplaats, Dalfsen: 420 m² (afstand 14070 m)
- Oude joodse begraafplaats, Zevenaar en Joodse begraafplaats Delfshaven, Rotterdam: 197 m² (afstand 111819 m)
- Oude Joodse begraafplaats, Venlo en Oude Joodse begraafplaats, Wijk bij Duurstede: 248 m² (afstand 89175 m)
- Joodse begraafplaats, Werkendam en Joodse begraafplaats, Wijk bij Duurstede: 579 m² (afstand 35530 m)
- Joodse begraafplaats, Bergen op Zoom en Joodse begraafplaats, Alphen aan den Rijn (geruimd): 1981 m² (afstand 73352 m)
- Joodse begraafplaats, Edam en Joodse begraafplaats, Rhenen: 372 m² (afstand 70313 m)
- Joodse begraafplaats, Den Helder en Nieuwe joodse begraafplaats, IJsselmuiden: 1584 m² (afstand 91241 m)
- Oude joodse begraafplaats, Delden en Joodse begraafplaats, Delft: 781 m² (afstand 163576 m)
- Oude joodse begraafplaats, Vlissingen en Nieuwe Joodse begraafplaats, Vlissingen: 694 m² (afstand 551 m)

## Bevestigd zonder terrein (alleen puntlocatie)

- `jb-loc-4368` Bilthoven: alleen puntlocatie beschikbaar, geen terrein in Funerair Utrecht.kmz (Leon/René (vraag B1), 2026-10-02)

## Zonder terrein (status in gebruik / geruimd) — open

- `jb-ger-247` Oude joodse begraafplaats, Loppersum — kandidaten: geen polygoon binnen bereik

## Joodse polygonen in de provincie-KMZ zonder record

Geen.

## Provincie in Excel wijkt af van ruimtelijke ligging (PDOK)

Geen.

## Dubbel nummer binnen een reeks

Geen.

## Punt ligt in meerdere terreinen (genest) — kleinste gekozen

- `jb-loc-1361` Joodse begraafplaats Kleverlaan, Haarlem: Joodse begraafplaats Kleverlaan, Haarlem (1198 m², ratio 1.0); Gem. begraafplaats Kleverlaan, Haarlem (82050 m², ratio 0.9) → gekozen: Joodse begraafplaats Kleverlaan, Haarlem

## Eén terrein door meerdere records geclaimd

Geen.

## Toegepaste correcties (`data/corrections.csv`)

- `jb-loc-4200` naam: 'Het Toepad' -> 'Begraafplaats Toepad' (Weergavenaam volgens Dodenakkers (vraag B5), Leon/René, 2026-10-02)
- `jb-loc-874` naam: 'Joodse Begraafplaats op Algemene Begraafplaats' -> 'Joods deel op Oud-Rijswijk' (Weergavenaam volgens Dodenakkers (vraag B5), Leon/René, 2026-10-02)
- `jb-ger-64` naam: 'Joodse begraafplaats' -> 'Nieuwe Joodse begraafplaats' (Weergavenaam volgens Dodenakkers (vraag B5), Leon/René, 2026-10-02)
- `jb-ver-471` naam: 'Portugees Israëlitische Begraafplaats Crooswijk' -> 'Portugees Israëlitische Begraafplaats Crooswijk (1696–1807)' (Twee verschillende plekken met dezelfde naam; aanvullen met periode mag (vraag B6), Leon, 2026-10-02)
- `jb-ver-872` naam: 'Portugees Israëlitische Begraafplaats Crooswijk' -> 'Portugees Israëlitische Begraafplaats Crooswijk (vanaf 1877)' (Twee verschillende plekken met dezelfde naam; aanvullen met periode mag (vraag B6), Leon, 2026-10-02)
- `jb-ver-182` naam: 'Joodse begraafplaats' -> 'Oude Joodse begraafplaats' (De geruimde Dordtse begraafplaats mag Oude Joodse begraafplaats heten (vraag B7), Leon, 2026-10-02)
- `jb-loc-189` rijksmonumentnummer: 516689 -> '' (Nummer 516689 hoort bij de Frechie Foundation, niet bij Mahsike Hadas; in de Excel gecorrigeerd door Leon (vraag NB1), Leon/René (vraag NB1), 2026-10-05)
- `jb-loc-195` rijksmonumentnummer: None -> '516689' (Nummer 516689 hoort bij de Frechie Foundation; in de Excel gecorrigeerd door Leon (vraag NB1), Leon/René (vraag NB1), 2026-10-05)
- `jb-loc-195` rijksmonument: False -> 'ja' (Volgt uit het rijksmonumentnummer (vraag NB1), Leon/René (vraag NB1), 2026-10-05)

## Verdwenen begraafplaatsen

Verdwenen begraafplaatsen krijgen nooit een terrein. Het punt geeft de plek **bij benadering** aan (vermoedelijk op basis van archiefonderzoek).

- `jb-ver-105` Oude Joodse Begraafplaats, Leiden — na 1758 geruimd, overgebracht naar Katwijk. Nu Sterrenwacht
- `jb-ver-107` Joodse armenbegraafplaats, Leiden — in 1961 geruimd
- `jb-ver-12` Joodse begraafplaats op Alg. Begraafplaats, Sittard — na 1889, geruimd, overgebracht naar Vrangendael
- `jb-ver-168` Joodse begraafplaats, Hoorn — 1762-1970, weg overheen aangelegd
- `jb-ver-177` Joodse Begraafplaats, Schiedam — Bij de Burcht van Mathenesse, geruimd 1962, overgebracht naar Toepad in Rotterdam
- `jb-ver-182` Oude Joodse begraafplaats, Dordrecht — In 1871 gesloten. In 1958 geruimd. Overgebracht naar Strijen (maar ook nieuwe begraafplaats en Rotterdam?)
- `jb-ver-205` Joodse begraafplaats, Werkendam — Gebruikt tot 1853
- `jb-ver-21` Joodse begraafplaats Tongelre, Eindhoven — ca. In 1962 geruimd voor aanleg Eisenhowerlaan, lijken overgebracht naar Woensel
- `jb-ver-24` Joodse begraafplaats op De Gelenberg, Afferden — In 1961 overgebracht naar Nijmegen, nu voetbalveld
- `jb-ver-246` Oude Joodse begraafplaats, Harlingen — Geruim in 1953, overgebracht naar nieuwe begraafplaats
- `jb-ver-253` Joodse begraafplaats, Coevorden — Eind 19de eeuw opgeheven, overgebracht naar nieuwe
- `jb-ver-260` Oude Joodse begraafplaats, Borne — Oude stenen van toegang resteren en zijn beschermd.
- `jb-ver-264` Israëlitische Begraafplaats, Enschede — 1841 gesloten, in 1947 geruimd, 360m2, wegverbreding
- `jb-ver-280` Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-281` Oude Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-284` Oude Joodse begraafplaats, Borculo — Na 1823 niet meer gebruikt
- `jb-ver-293` Oude Joodse begraafplaats, Vianen — 1720-1810
- `jb-ver-294` Joodse begraafplaats Walsland, Vianen — 1807-1820, nu overbouwd
- `jb-ver-296` Joodse begraafplaats, Culemborg — 1764-1869, overbouwd
- `jb-ver-301` Oude Begraafplaats, Heerlen — tot 1898 in gebruik, later synagoge overheen gebouwd!
- `jb-ver-306` Joodse begraafplaats, Ede — Gebruikt tot 1863, 1925-1930 verdwenen, nadien bebouwd
- `jb-ver-354` Oude Israëlitische begraafplaats, Deventer — 1870 gesloten, geruimd in 1961, 620 m2
- `jb-ver-357` Nieuwe Joodse begraafplaats, Cuijk — Geruimd in 1963, al in 1924 werden hier de graven v/d Smidstraat (1761) overgebracht
- `jb-ver-358` Oude Joodse begraafplaats, Cuijk — In 1924 geruimd
- `jb-ver-361` Joodse begraafplaats Dijkstraat, Rotterdam — -1940, overgebracht naar Toepad
- `jb-ver-369` Nieuwe Joodse begraafplaats, Arnhem — tot 1858 gebruik, resten overgebracht naar Moscowa
- `jb-ver-395` Portugees Israëlitische Begraafplaats, Groet — 1602-1634 geen zerken, resten overgebracht naar Ouderkerk
- `jb-ver-417` Oude Joodse begraafplaats, Hasselt — In 1825 weggespoeld
- `jb-ver-418` Joodse Begraafplaats, Linne — Heeft waarschijnlijk nooit bestaan, zou van 1828-1860 zijn gebruikt
- `jb-ver-425` Joodse begraafplaats, Maassluis — In 1950 geruimd, overgebracht naar gemeentelijke begraafplaats
- `jb-ver-43` Eerste Joodse begraafplaats, Leeuwarden — 1670-1833, 520m2, geruimd na WO II nu Tresoar
- `jb-ver-436` Joodse Begraafplaats, Losser — Gesloten in 1954, geruimd in 1964, overgebracht naar Enschede
- `jb-ver-44` Tweede joodse begraafplaats, Leeuwarden — 1785-1833, 1190m2
- `jb-ver-440` Joodse Begraafplaats de Hagen, Rijssen — Niet meer gebruikt na 1878, in 1949 resten overgebracht naar Arend Baanstraat
- `jb-ver-471` Portugees Israëlitische Begraafplaats Crooswijk (1696–1807), Rotterdam — -1807. Later RK begraafplaats Crooswijk
- `jb-ver-488` Joodse begraafplaats, Zevenaar — 
- `jb-ver-491` Joodse begraafplaats, De Bilt — - 1807, verder gegaan in Utrecht, nu winkelcentrum
- `jb-ver-498` Joodse begraafplaats, Leerdam — Bebouwd, resten overgebracht naar voorste begraafplaats op Dijk (opgehoogd)
- `jb-ver-508` Joodse begraafplaats Ter Borg, Sellingen — Niet bekend of hier ook daadwerkelijk begraven is
- `jb-ver-509` Portugees-Joodse begraafplaats, Nijkerk — Bebouwd
- `jb-ver-510` Joodse begraafplaats, Nijkerk — Bebouwd
- `jb-ver-512` Oude Joodse begraafplaats, Bredevoort — In 1953 verkocht tbv woning, resten overgebracht naar nieuwe
- `jb-ver-528` Joodse begraafplaats, Hengelo — Resten in 1965 overgebracht naar Zutphen
- `jb-ver-53` Joodse begraafplaats, Breda — In 1961 gesloten tbv aanleg snelweg, resten overgebracht naar Oosterhout
- `jb-ver-576` Joodse begraafplaats aan de Luurderschans, Zwolle — Bij Koggepad. In 1981 ontruimd, overgebracht naar nieuwe joodse begraafplaats, nu parkeerplaats
- `jb-ver-59` Joodse begraafplaats, Arnhem — Tot 1863 gebruikt, in 1985 geruimd, overgebracht naar Moscowa
- `jb-ver-613` Oude Joodse begraafplaats, Zwartsluis — Na 1851 niet meer gebruikt. Geruimd 2e helft 20ste eeuw
- `jb-ver-628` Oude Joodse begraafplaats, Lochem — - 1848. 1955 geruimd. Bij oude synagoge. Nu deels bebouwd
- `jb-ver-67` Oude Joodse begraafplaats Jodenkamp, Groningen — in 1838 gesloten, 1954 overgebracht naar Noorderbegraafplaats. Bebouwd
- `jb-ver-676` Joodse begraafplaats Veerpoortwal, Doesburg — in 1952 geruimd, eerst overgebracht naar buiten de Meipoort, daarna naar Doetinchem
- `jb-ver-677` Joodse begraafplaats Ooipoortwal, Doesburg — In 1952 geruimd, eerst overgebracht naar buiten de Meipoort, daarna naar Doetinchem
- `jb-ver-678` Joodse begraafplaats buiten de Meipoort, Doesburg — In 1963 overgebracht naar Doetinchem
- `jb-ver-703` Joodse begraafplaats, Hindeloopen — Niet duidelijk of het terrein gebruikt is, ± 1870 verkocht!
- `jb-ver-710` Joodse begraafplaats, s-Hertogenbosch — Niet duidelijk of het terrein gebruikt is
- `jb-ver-723` Joodse begraafplaats, Hilvarenbeek — 
- `jb-ver-74` Oude Joodse begraafplaats Den Dries, Maastricht — Gebruikt tot ca. 1812
- `jb-ver-75` Oude Joodse begraafplaats, Nijmegen — 1683-1961, Laatste begraving 1890, nu parkeergarage
- `jb-ver-753` Joodse begraafplaats, Wijk bij Duurstede — Exacte locatie niet duidelijk….
- `jb-ver-774` Oude Joodse begraafplaats, Leerdam — 
- `jb-ver-825` Eerste Joodse begraafplaats, Heerlen — Tot 1811 in gebruik geweest
- `jb-ver-872` Portugees Israëlitische Begraafplaats Crooswijk (vanaf 1877), Rotterdam — Eind 19de eeuw verdwenen
- `jb-ver-874` Oude Joodse begraafplaats, Hilversum — 1751-1863, haventerrein, later bebouwd
- `jb-ver-880` Joodse begraafplaats Horst, Kaatsheuvel — Tot 1825 gebruikt
- `jb-ver-881` Joodse begraafplaats Besoyen, Waalwijk — gebruikt tot 1853
- `jb-ver-895` Oude Joodse begraafplaats, Naarden — Begin 20ste eeuw bebouwd
- `jb-ver-896` Joodse Begraafplaats, Beverwijk — 1809-1943. in 1950 geruimd, resten overgebracht naar Duinhof
- `jb-ver-9` Joodse begraafplaats, Vaals — Na WO II overgebracht naar Linderweg
- `jb-ver-918` Joodse begraafplaats, Woudrichem — Na 1798 al niet meer gebruikt (zie archief)
- `jb-ver-98` Oude Joodse begraafplaats, Haarlem — 1770-1833, 1960 geruimd
