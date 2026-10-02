# Koppelrapport Joodse begraafplaatsen

Gegenereerd door `scripts/build_base_dataset.py` op 2026-10-02 14:06.
Provincie(s): **Zuid-Holland**. Excel-rijen landelijk: 315.

## Samenvatting

- 36 begraafplaatsen: 24 in gebruik, 2 geruimd, 10 verdwenen.
- Elk record is via (reeks, Nr) aan precies één punt gekoppeld; sleutel `jb-<reeks>-<Nr>`.
- Terreinen gekoppeld: 26.

## Koppelwijze terrein

| koppelwijze | aantal |
|---|---|
| binnen_naam_gelijk | 23 |
| binnen_naamvariant | 3 |
| niet_van_toepassing | 10 |

## Ter controle voor Dodenakkers: naamvarianten

Het punt ligt in (of vlak bij) het terrein, maar de naam van het terrein in de provincie-KMZ wijkt af van het label van het punt.

| id | label punt | naam terrein | koppelwijze |
|---|---|---|---|
| `jb-loc-874` | Joods deel begraafplaats Oud-Rijswijk, Rijswijk | Joods deel op Oud Rijswijk, Rijswijk | binnen_naamvariant |
| `jb-loc-4200` | Joodse begraafplaats Toepad, Rotterdam | Joodse begraafplaats Het Toepad, Rotterdam | binnen_naamvariant |
| `jb-ger-64` | Joodse begraafplaats, Schiedam (geruimd) | Nieuwe Joodse begraafplaats, Schiedam (geruimd) | binnen_naamvariant |

## Zonder terrein (status in gebruik / geruimd)

Geen.

## Joodse polygonen in de provincie-KMZ zonder record

Geen.

## Provincie in Excel wijkt af van ruimtelijke ligging (PDOK)

Geen.

## Dubbel nummer binnen een reeks

Geen.

## Punt ligt in meerdere terreinen (genest) — kleinste gekozen

- `jb-loc-874` Joods deel begraafplaats Oud-Rijswijk, Rijswijk: Joods deel op Oud Rijswijk, Rijswijk (112 m², ratio 1.0); Begraafplaats Oud-Rijswijk, Rijswijk (29510 m², ratio 0.69) → gekozen: Joods deel op Oud Rijswijk, Rijswijk

## Eén terrein door meerdere records geclaimd

Geen.

## Toegepaste correcties (`data/corrections.csv`)

Geen.

## Verdwenen begraafplaatsen

Verdwenen begraafplaatsen krijgen nooit een terrein. Het punt geeft de plek **bij benadering** aan (vermoedelijk op basis van archiefonderzoek).

- `jb-ver-105` Oude Joodse Begraafplaats, Leiden — na 1758 geruimd, overgebracht naar Katwijk. Nu Sterrenwacht
- `jb-ver-107` Joodse armenbegraafplaats, Leiden — in 1961 geruimd
- `jb-ver-177` Joodse Begraafplaats, Schiedam — Bij de Burcht van Mathenesse, geruimd 1962, overgebracht naar Toepad in Rotterdam
- `jb-ver-182` Joodse begraafplaats, Dordrecht — In 1871 gesloten. In 1958 geruimd. Overgebracht naar Strijen (maar ook nieuwe begraafplaats en Rotterdam?)
- `jb-ver-280` Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-281` Oude Joodse Begraafplaats, Gouda — In 1976 ivm hoge waterstand geruimd en overgebracht naar Wageningen
- `jb-ver-361` Joodse begraafplaats Dijkstraat, Rotterdam — -1940, overgebracht naar Toepad
- `jb-ver-425` Joodse begraafplaats, Maassluis — In 1950 geruimd, overgebracht naar gemeentelijke begraafplaats
- `jb-ver-471` Portugees Israëlitische Begraafplaats Crooswijk, Rotterdam — -1807. Later RK begraafplaats Crooswijk
- `jb-ver-872` Portugees Israëlitische Begraafplaats Crooswijk, Rotterdam — Eind 19de eeuw verdwenen
