# 04 – Vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-02, na West-Nederland (Zuid-Holland, Utrecht, Noord-Holland, Zeeland, Flevoland; 91 begraafplaatsen).
Kaart: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev

Per vraag staat erbij **wat we nu doen**. Zonder antwoord blijft dat zo. Kenmerken als `jb-loc-1559` zijn onze sleutels: reeks (`loc` = in gebruik/Locaties.kmz, `ver` = Verdwenen.kmz, `ger` = Geruimd.kmz) + het Nr uit de Excel. In de kaartpopup staan ze onder "Kenmerk".

## Beantwoord (Leon/René, 2026-10-02)

| Vraag | Antwoord | Verwerkt |
|---|---|---|
| A3 `NA` | Nader adres | Toelichting aangepast; "bij/tegenover/achter" vóór het adres |
| A3 `Muur` | Muur rondom ja/nee | Als ja/nee gelezen; popup "Muur rondom: ja" (in West-NL nog overal leeg) |
| A3 `Kadaster` | Aldaar geregistreerd ja/nee | Popup "Geregistreerd bij Kadaster: ja/nee" |
| A5 / B1 | Van verdwenen is alleen een puntlocatie beschikbaar; Bilthoven ook alleen punt | Bilthoven vastgelegd als *bevestigd zonder terrein* |
| A6 | Complexnummer in `Rmon` kan voorkomen | Blijft zo: complex opgezocht, onderdelen getoond |
| A7 Wijk bij Duurstede | 454310 "Historische aanleg" valt er net buiten | Relatie vastgelegd als "net buiten het terrein" |
| B5 | Toepad → "Begraafplaats Toepad"; Rijswijk → "Joods deel op Oud-Rijswijk"; Schiedam → "Nieuwe Joodse begraafplaats" | Weergavenaam via `data/corrections.csv` (Excel-naam bewaard) |
| B8 | Juiste spelling is "Shomre Hadas" (Putte) | Excel klopt al; KMZ-tikfout, geen actie (Noord-Brabant volgt) |

Nog open hieronder: alles zonder ✅.

---

## A. Voor Leon – de bronbestanden

**A1. Nummerreeksen.** Het `Nr` in de Excel is niet uniek. Wij gaan ervan uit dat elke status een eigen reeks en een eigen bestand heeft: *In gebruik* → `Locaties.kmz`, *Verdwenen* → `Verdwenen.kmz` ("Verdwenen 0182"), *Geruimd* → `Geruimd.kmz`. Daarmee vinden we voor alle 315 rijen precies één punt. Klopt dit, en blijft het zo bij nieuwe versies?
*Nu:* zo gekoppeld.

**A2. Dubbel nummer in Geruimd.kmz.** Nr 245 staat twee keer in `Geruimd.kmz`: "NH kerkhof, Puttershoek" en "H Martinuskerkhof, Pannerden". Niet Joods, dus niet op onze kaart, maar wel een fout in de bron?

**A3. Betekenis van kolommen.** ✅ deels — `NA`, `Muur`, `Kadaster` beantwoord. Nog open: `Circa`, `Jaartal`, `Grondvorm`, `Gemeentelijk monument` ("Geen"), `Grootte`, `Laatste bezoek`.

| Kolom | Onze aanname | Vraag |
|---|---|---|
| `NA` | ✅ Nader adres | Nog open: is de waarde "to" (Beverwijk `jb-ver-896`) = "tegenover"? |
| `MIP` | Opgenomen in het Monumenten Inventarisatie Project | Klopt. Wil je dit in de popup? (nu: "opgenomen" als Ja) |
| `Met` | Metaheerhuis(je) aanwezig | Klopt dit? (nu: huisje-icoon + "Metaheerhuis: aanwezig") |
| `Muur` | ✅ Muur rondom ja/nee | — |
| `Kadaster` | ✅ Aldaar geregistreerd ja/nee | — (wordt nu getoond) |
| `Circa` | Jaartal is bij benadering | Klopt? (nu: "ca. 1750") |
| `Jaartal` | Jaar van aanleg / eerste begraving | Of iets anders? Voor verdwenen staat het eindjaar vaak alleen in Bijzonderheden. |
| `Grondvorm` | ? | Overal "Recht". Welke andere waarden zijn er? Tonen we dit? |
| `Gemeentelijk monument` | Ja/Nee | Soms "Geen". Is dat hetzelfde als Nee? |
| `Grootte` | Oppervlakte in m² | Gemeten hoe (kadaster, kaart, ter plekke)? |
| `Laatste bezoek` | Jaar van het laatste bezoek door Dodenakkers | Klopt? Willen jullie dat publiek tonen? |
| `Rmon` | Rijksmonumentnummer | Vaak een complexnummer, zie A6. |

**A4. Status "In gebruik".** Daaronder vallen ook begraafplaatsen die gesloten zijn maar nog bestaan, zoals Haarlem Kleverlaan ("1969 gesloten") en Rotterdam Delfshaven ("1865–1898"). Op de kaart noemen we de status daarom **"Bestaand"**. Willen jullie onderscheid tussen *in gebruik* en *gesloten*? Dan hebben we die informatie per begraafplaats nodig, bijvoorbeeld als extra kolom.

**A5. Verdwenen: hoe precies is de plek?** ✅ deels — er is alleen een puntlocatie. Nog open: waar is die op gebaseerd, en de twee "onbekend"-jaartallen. We tonen verdwenen begraafplaatsen als open ring met de tekst "plek bij benadering", en berekenen er geen afstanden tot monumenten voor.
- Waar is de plek op gebaseerd (archief, kadastrale minuut, overlevering)?
- Kunnen jullie per verdwenen begraafplaats aangeven hoe zeker de plek is (bv. *exact* / *straat* / *alleen de plaats*)? Dan kunnen we dat zichtbaar maken.
- Twee verdwenen begraafplaatsen hebben jaartal "onbekend": `jb-ver-774` (Oude Joodse begraafplaats, Leerdam) en `jb-ver-425` (Maassluis).

**A6. Rmon bevat vaak een complexnummer.** ✅ Kan voorkomen; blijft zo. Nog open: Wassenaar/Kerkehout. Van de 19 rijksmonumentnummers in West-Nederland zijn er 8 een complexnummer: Alkmaar, Bussum, Muiderberg, Amersfoort (nieuw), Leerdam, Utrecht, Gorinchem en Wassenaar. We zoeken het complex op en tonen de onderdelen (begraafplaats, baarhuisje, hek …) in de popup.
- Is dat de bedoeling, of moet het het monumentnummer van de begraafplaats zelf zijn?
- Wassenaar (`jb-loc-1343`) verwijst naar complex 524542 **"Begraafplaats Kerkehout"**. Is dat de algemene begraafplaats waar het Joodse deel bij hoort?

**A7. Rijksmonumenten op het terrein die niet in de Excel staan.** Volgens RCE ligt er een rijksmonument op of over het terrein dat niet in `Rmon` staat. Horen deze bij de begraafplaats?
- Alkmaar `jb-loc-2923`: 7464 "Begraafplaats en -onderdelen" (op het terrein). In de Excel staat complex 524892.
- Bussum `jb-loc-1503`: 527225 "Begraafplaats" (overlapt)
- Overveen `jb-loc-4201`: 529524 "Poortgebouw" (overlapt)
- ✅ Wijk bij Duurstede `jb-loc-819`: 454310 "Historische aanleg" — valt er net buiten
- Middelburg `jb-loc-21`: 508330 "Baarhuisje" (op het terrein)

## B. Voor Leon – specifieke begraafplaatsen

**B1. ✅ Bilthoven, Progressieve joodse begraafplaats** — alleen puntlocatie, geen terrein. (`jb-loc-4368`, 300 m²). In `Funerair Utrecht.kmz` staat geen terrein voor deze begraafplaats. Het punt ligt 10 m naast "Gem. begraafplaats Brandenburg". Kunnen jullie het terrein aanleveren, of is het een deel van Brandenburg zonder eigen grens?
*Nu:* alleen een punt, geen terrein.

**B2. Vlissingen.** Twee aparte polygonen, 551 m uit elkaar, met **exact dezelfde oppervlakte (694 m²)**. Dat wijst op een gekopieerde vorm.

| Kenmerk | Excel-naam | Excel Grootte | Gekoppeld terrein |
|---|---|---|---|
| `jb-loc-9` | Joodse Begraafplaats bij de Leeuwentrap (1866–1907) | 350 m² | "Oude joodse begraafplaats, Vlissingen" (handmatig gekoppeld) |
| `jb-loc-908` | Joodse Begraafplaats op Begraafplaats Vredehof (1907–1970) | 865 m² | "Nieuwe Joodse begraafplaats, Vlissingen" |

Klopt de koppeling, en welke polygoon heeft de verkeerde vorm?

**B3. Terrein veel groter of kleiner dan `Grootte`.** Is het terrein fout getekend, of klopt de maat in de Excel niet?

| Kenmerk | Begraafplaats | Terrein (KMZ) | Grootte (Excel) |
|---|---|---|---|
| `jb-loc-2804` | Beverwijk (op Duinrust) | 137 m² | 870 m² |
| `jb-loc-2369` | Almere | 2.854 m² | 4.875 m² |
| `jb-loc-238` | Goes (op alg. begraafplaats) | 1.057 m² | 670 m² |
| `jb-loc-9` | Vlissingen, Leeuwentrap | 694 m² | 350 m² |

Ter vergelijking: de andere 64 terreinen liggen allemaal binnen 75–133 % van `Grootte`.

**B4. Rhenen en Edam.** Beide terreinen zijn exact 372 m² groot (70 km uit elkaar). Toeval, of ook een gekopieerde vorm?

**B5. Naamsverschillen KMZ ↔ puntbestand.** ✅ deels — Toepad, Oud-Rijswijk en Schiedam vastgesteld. De rest is nog open. Het punt ligt in het terrein en we hebben gekoppeld, maar de namen verschillen. Zijn het alleen schrijfvarianten?
- ✅ `jb-loc-874` → **Joods deel op Oud-Rijswijk**
- ✅ `jb-loc-4200` → **Begraafplaats Toepad**
- ✅ `jb-ger-64` → **Nieuwe Joodse begraafplaats** (Schiedam)
- `jb-loc-21` Hoogduitse begraafplaats, Middelburg ↔ Hoogduitse **Joodse** begraafplaats
- `jb-loc-908` Joodse begraafplaats, Vlissingen ↔ **Nieuwe** Joodse begraafplaats
- `jb-loc-1381` / `jb-loc-3369` Diemen / Muiderberg ↔ "Joodse begraafplaats **A'dam**, …"
- `jb-loc-2801` Begraafplaats Psychiatrisch Ziekenhuis, Bloemendaal ↔ Joodse begraafplaats Psych ziekenhuis
- `jb-loc-1458` / `1459` Oud / Nieuw Joodse begraafplaats, Amersfoort ↔ Oude / Nieuwe
- `jb-loc-1643` Maarssen ↔ "Joods Maarssen"; `jb-loc-4171` Veenendaal ↔ "Joods veenendaal"
- `jb-loc-1439` Ouderkerk: puntlabel "Portugees-Joodse begraafplaats" ↔ terrein "Beth Haim" (gekoppeld via de Excel-naam)

**B6. Twee keer dezelfde naam.** `jb-ver-471` (vanaf 1696, tot 1807) en `jb-ver-872` (vanaf 1877) heten in de Excel allebei "Portugees Israëlitische Begraafplaats Crooswijk" (Rotterdam). Ze liggen 430 m uit elkaar. Zijn dit twee verschillende begraafplaatsen? Mogen we de naam aanvullen, bijvoorbeeld met de periode?

**B7. Dordrecht.** De verdwenen `jb-ver-182` (1738, geruimd 1958) en de bestaande `jb-loc-1912` hebben exact dezelfde naam. Wij houden ze apart. Klopt dat?

**B8. Kleine fouten in de bronbestanden** (we passen niets aan, ter info):
- ✅ `Locaties.kmz`: "Sombre Hadas, Putte" — juist is "Shomre Hadas" (zoals in de Excel)
- `Verdwenen.kmz`: "Joodse begraafplats, Maassluis" (tikfout)
- `jb-ger-64` Schiedam: Grootte "?"

## C. Voor Leon/René – inhoud van de kaart

**C1. Popup.** Nu getoond: naam, status, plaats, gemeente, adres (met bij/tegenover), sinds (jaartal), grootte, grondvorm, rijksmonument (of complex met onderdelen), metaheerhuis, gemeentelijk monument, MIP, beschermd deel, eigenaar (met postadres), bijzonderheden, beschermd gezicht, rijksmonumenten binnen 100 m, laatste bezoek en kenmerk.
- Moet er iets uit, bijvoorbeeld *grondvorm*, *laatste bezoek* of *kenmerk*?
- Mist er iets?
- Klopt de volgorde?

**C2. Eigenaren.** Bij 36 bestaande begraafplaatsen is geen eigenaar bekend. Zijn alle eigenaren organisaties (NIG, NIK, Joodse gemeenten, gemeente Amsterdam)? Of staan er ook privépersonen tussen die we niet met naam en adres moeten tonen?

**C3. Gevoeligheid van locaties.** Moeten we bij kleine of kwetsbare begraafplaatsen rekening houden met vandalisme of antisemitisme? Bijvoorbeeld door geen exacte ingang of terrein te tonen? Of is alles al openbaar via dodenakkers.nl?
*Nu:* alles getoond.

**C4. Verwijzing naar dodenakkers.nl.** Heeft elke begraafplaats een eigen pagina op dodenakkers.nl? Dan zetten we per begraafplaats een link "Meer op Dodenakkers" in de popup. Waarschijnlijk hebben we daarvoor een kolom met URL of paginanummer nodig.

**C5. Foto's.** Zijn er foto's per begraafplaats die we in de popup mogen tonen (met naam van de fotograaf)? Hoe leveren jullie die aan?

**C6. Herbegravingen.** Veel records zeggen "overgebracht naar …" (Schiedam → Toepad, Leiden → Katwijk, Gouda → Wageningen, Dordrecht → Strijen). Willen jullie dat als lijn of verwijzing op de kaart?
*Nu:* alleen als tekst in Bijzonderheden.

**C7. Dankwoord.** Het tabblad "Dank en informeren" in de Excel hebben we bewust niet geopend, omdat er persoonsgegevens in staan. Moeten er namen van mensen of organisaties op de site komen (bijvoorbeeld op de methodepagina)? Zo ja: welke, en hebben zij daar toestemming voor gegeven?

**C8. Begraafplaatsen die nog niet in de lijst staan.** Moeten we RCE controleren op monumenten met functie "Joodse begraafplaats" die niet in de Excel staan, en die lijst aan jullie geven (niet op de kaart)?

**C9. Datering: indeling van de balkjes.** Het filter "Datering" gebruikt voorlopig dezelfde indeling als de kaart van Dodenakkers Zuid-Holland: vóór 1829 · 1829–1849 · 1850–1899 · 1900–1949 · 1950–1999 · 2000–heden. Op de kaart van Zuid-Holland verwees 1829 naar het verbod op begraven in en rond de kerk. Dat geldt niet voor Joodse begraafplaatsen, en daarom hebben we die uitleg weggelaten.
- Is 1829 hier een zinvolle grens, of past een andere indeling beter? Mogelijke grenzen zijn 1796 (gelijkberechtiging van Joden), 1869 (Begrafeniswet) en 1940–1945. Of een indeling die jullie zelf gebruiken.
- Nu valt meer dan de helft (48 van de 89 bekende jaartallen) in "vóór 1829". Is een splitsing in de 17e en 18e eeuw gewenst? Verdeling West-Nederland: vóór 1700: 10 · 1700–1799: 26 · 1800–1828: 12.
- Is `Jaartal` het jaar van aanleg (zie ook A3)? En willen jullie voor verdwenen en geruimde begraafplaatsen ook het eindjaar als apart veld? Dat staat nu alleen in Bijzonderheden.
*Nu:* indeling van dodenakkers-zh, zonder "Middeleeuws" (komt niet voor), zonder uitleg over 1829.

## D. Voor René – kleuren en leesbaarheid

**D1. Kleuren.** Bestaand = blauw rondje ●, geruimd = oranje ruit ◆, verdwenen = donkergrijze open ring ○. Gekozen omdat ze onderscheidbaar blijven bij de drie vormen van kleurenblindheid (gesimuleerd), en omdat elke status ook een eigen vorm heeft. Graag testen:
- Zie je de drie statussen goed uit elkaar, op de grijze kaart én op de luchtfoto?
- Is de terreinkleur (blauw/oranje vlak) duidelijk genoeg?
- Welke vorm van kleurenblindheid heb je? Dan kunnen we gericht testen.

**D2. Contextlagen.** Gezichten (paars gestippeld), rijksmonumenten (donkergrijze stip), archeologische monumenten (bruin) en gemeentegrenzen (grijs gestippeld). Zijn deze goed te onderscheiden van de begraafplaatsen?

**D3. Leesbaarheid.** Is de tekstgrootte in het paneel en de popup goed, ook op je telefoon?

## E. Layout en presentatie

**E1. Huisstijl.** De kaart gebruikt het Dodenakkers-logo (`.webp`, klein formaat) en verder een neutrale stijl (systeemlettertype, wit paneel).
- Is er een scherpere versie van het logo (SVG of PNG van minstens 400 px breed)?
- Zijn er huisstijlkleuren of een lettertype die we moeten gebruiken?

**E2. Titel en introtekst.** Nu: titel "Joodse Begraafplaatsen" met als intro "Bestaande, geruimde en verdwenen Joodse begraafplaatsen, uit de inventarisatie van stichting Dodenakkers."
- Willen jullie een eigen introtekst, bijvoorbeeld over de Joodse begraafcultuur, de eeuwige grafrust of de oorlog?
- Wie schrijft die, en moet hij langs een Joodse organisatie?

**E3. Statusnamen.** "Bestaand / Geruimd / Verdwenen", of liever de termen uit de Excel ("In gebruik")? Zie ook A4.

**E4. Namen op de kaart.** Er staan nu geen namen bij de punten; die zie je in de lijst en de popup. Namen op de kaart vragen een eigen set lettertypebestanden op de server (kan, kost wat werk). Gewenst?

**E5. Wat staat standaard aan?** Nu: terreinen en provinciegrenzen. Gemeentegrenzen, gezichten en monumenten staan uit. Ondergrond: grijze topografische kaart. Andere wensen?

**E6. Mobiel.** Op de telefoon start de kaart met het paneel dicht en een kleine legenda linksboven; via ☰ open je het paneel. Werkt dat zo voor jullie?

**E7. Extra pagina's of functies.** Moeten er nog bij:
- een statistiekpagina (aantallen per provincie, status, monumentstatus), zoals bij dodenakkers-zh;
- een download van de selectie als CSV/GeoJSON;
- een Engelse versie?

**E8. Inbedden op dodenakkers.nl.** De kaart kan als iframe op jullie site (`?embed=1`, inbedden vanaf dodenakkers.nl is al toegestaan).
- Op welke pagina komt hij, en hoe hoog moet het kader zijn?
- Kan jullie websitesysteem iframes plaatsen?
- Moet het inbedden ook vanaf andere domeinen kunnen?

**E9. Eigen webadres.** Nu `joodse-begraafplaatsen.jolietjakeblues64.workers.dev`. Willen jullie een eigen adres, zoals `joodsebegraafplaatsen.dodenakkers.nl`? Wie beheert de DNS van dodenakkers.nl?

## F. Werkwijze

**F1. Correcties.** Hoe willen jullie fouten doorgeven?
- (a) aangepaste Excel/KMZ opnieuw sturen;
- (b) een lijstje per begraafplaats (kenmerk + wat er anders moet), dat wij in `data/corrections.csv` zetten;
- (c) een invulformulier op de site.

**F2. Updates.** Hoe vaak verandert de inventarisatie? Komen er nieuwe versies van de KMZ-bestanden?

**F3. Volgorde rest van Nederland.** Voorstel: Gelderland (61), Overijssel (43), Noord-Brabant (31), Limburg (25), Groningen (27), Drenthe (21), Fryslân (16). Voorkeur of deadline?

**F4. Publiek of niet.** Mag de kaart nu al openbaar gedeeld worden? Of eerst intern blijven tot alle provincies klaar zijn? Zoekmachines mogen hem nu indexeren (robots.txt staat open).
