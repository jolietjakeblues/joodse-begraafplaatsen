# Koppelrapport Joodse begraafplaatsen

Gegenereerd door `scripts/build_base_dataset.py` op 2026-10-02 15:33.
Provincie(s): **Zuid-Holland, Utrecht, Noord-Holland, Zeeland, Flevoland**. Excel-rijen landelijk: 315.

## Samenvatting

- 91 begraafplaatsen: 67 in gebruik, 2 geruimd, 22 verdwenen.
- Elk record is via (reeks, Nr) aan precies één punt gekoppeld; sleutel `jb-<reeks>-<Nr>`.
- Terreinen gekoppeld: 68.

## Koppelwijze terrein

| koppelwijze | aantal |
|---|---|
| binnen_naam_gelijk | 53 |
| binnen_naamvariant | 13 |
| geen_terrein_bevestigd | 1 |
| handmatig | 1 |
| nabij_naam_gelijk | 1 |
| niet_van_toepassing | 22 |

## Ter controle voor Dodenakkers: naamvarianten

Het punt ligt in (of vlak bij) het terrein, maar de naam van het terrein in de provincie-KMZ wijkt af van het label van het punt.

| id | label punt | naam terrein | koppelwijze | status |
|---|---|---|---|---|
| `jb-loc-2801` | Begraafplaats Psychiatrisch Ziekenhuis, Bloemendaal | Joodse begraafplaats Psych ziekenhuis, Bloemendaal | binnen_naamvariant | open |
| `jb-loc-1381` | Joodse begraafplaats, Diemen | Joodse begraafplaats A'dam, Diemen | binnen_naamvariant | open |
| `jb-loc-3369` | Joodse begraafplaats, Muiderberg | Joodse begraafplaats A'dam, Muiderberg | binnen_naamvariant | open |
| `jb-loc-1439` | Portugees-Joodse begraafplaats, Ouderkerk aan de Amstel | Beth Haim, Ouderkerk aan de Amstel | binnen_naamvariant | open |
| `jb-loc-2523` | Joodse begraafplaats, Monnickendam | Joodse begraafplaats, Monnickendam | nabij_naam_gelijk | open |
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
| `jb-loc-2369` | Joodse begraafplaats, Almere | Joodse begraafplaats, Almere | 2.854 | 4.875 |
| `jb-loc-2804` | Joodse begraafplaats, Beverwijk | Joodse begraafplaats, Beverwijk | 137 | 870 |
| `jb-loc-238` | Joodse begraafplaats, Goes | Joodse begraafplaats, Goes | 1.057 | 670 |
| `jb-loc-9` | Joodse begraafplaats bij de Leeuwentrap, Vlissingen | Oude joodse begraafplaats, Vlissingen | 694 | 350 |

## Handmatige terreinkoppelingen (`data/terrein_koppelingen.csv`)

- `jb-loc-9` Joodse begraafplaats bij de Leeuwentrap, Vlissingen → Oude joodse begraafplaats, Vlissingen (694 m², Grootte 350)

## Joodse terreinen met exact dezelfde oppervlakte (mogelijk gekopieerde polygoon)

- Joodse begraafplaats, Rhenen en Joodse begraafplaats, Edam: 372 m² (afstand 70313 m)
- Oude joodse begraafplaats, Vlissingen en Nieuwe Joodse begraafplaats, Vlissingen: 694 m² (afstand 551 m)

## Bevestigd zonder terrein (alleen puntlocatie)

- `jb-loc-4368` Bilthoven: alleen puntlocatie beschikbaar (Leon/René 2026-10-02, vraag B1)

## Zonder terrein (status in gebruik / geruimd) — open

Geen.

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

## Verdwenen begraafplaatsen

Verdwenen begraafplaatsen krijgen nooit een terrein. Het punt geeft de plek **bij benadering** aan (vermoedelijk op basis van archiefonderzoek).

- `jb-ver-105` Oude Joodse Begraafplaats, Leiden — na 1758 geruimd, overgebracht naar Katwijk. Nu Sterrenwacht
- `jb-ver-107` Joodse armenbegraafplaats, Leiden — in 1961 geruimd
- `jb-ver-168` Joodse begraafplaats, Hoorn — 1762-1970, weg overheen aangelegd
- `jb-ver-177` Joodse Begraafplaats, Schiedam — Bij de Burcht van Mathenesse, geruimd 1962, overgebracht naar Toepad in Rotterdam
- `jb-ver-182` Joodse begraafplaats, Dordrecht — In 1871 gesloten. In 1958 geruimd. Overgebracht naar Strijen (maar ook nieuwe begraafplaats en Rotterdam?)
- `jb-ver-280` Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-281` Oude Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-293` Oude Joodse begraafplaats, Vianen — 1720-1810
- `jb-ver-294` Joodse begraafplaats Walsland, Vianen — 1807-1820, nu overbouwd
- `jb-ver-361` Joodse begraafplaats Dijkstraat, Rotterdam — -1940, overgebracht naar Toepad
- `jb-ver-395` Portugees Israëlitische Begraafplaats, Groet — 1602-1634 geen zerken, resten overgebracht naar Ouderkerk
- `jb-ver-425` Joodse begraafplaats, Maassluis — In 1950 geruimd, overgebracht naar gemeentelijke begraafplaats
- `jb-ver-471` Portugees Israëlitische Begraafplaats Crooswijk, Rotterdam — -1807. Later RK begraafplaats Crooswijk
- `jb-ver-491` Joodse begraafplaats, De Bilt — - 1807, verder gegaan in Utrecht, nu winkelcentrum
- `jb-ver-498` Joodse begraafplaats, Leerdam — Bebouwd, resten overgebracht naar voorste begraafplaats op Dijk (opgehoogd)
- `jb-ver-753` Joodse begraafplaats, Wijk bij Duurstede — Exacte locatie niet duidelijk….
- `jb-ver-774` Oude Joodse begraafplaats, Leerdam — 
- `jb-ver-872` Portugees Israëlitische Begraafplaats Crooswijk, Rotterdam — Eind 19de eeuw verdwenen
- `jb-ver-874` Oude Joodse begraafplaats, Hilversum — 1751-1863, haventerrein, later bebouwd
- `jb-ver-895` Oude Joodse begraafplaats, Naarden — Begin 20ste eeuw bebouwd
- `jb-ver-896` Joodse Begraafplaats, Beverwijk — 1809-1943. in 1950 geruimd, resten overgebracht naar Duinhof
- `jb-ver-98` Oude Joodse begraafplaats, Haarlem — 1770-1833, 1960 geruimd
