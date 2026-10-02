# 04 – Vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-02, na West-Nederland (91), Gelderland (61), Overijssel (43) en Noord-Brabant (31): 226 begraafplaatsen.
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

## Beantwoord ronde 2 (opmerkingen in de PDF, Leon/René, 2026-10-02)

| Vraag | Antwoord | Verwerkt |
|---|---|---|
| A2 | Puttershoek stond fout in Geruimd.kmz; Leon heeft het gecorrigeerd | Wacht op nieuwe bronbestanden (zie N4) |
| A3 `NA` | "to" = tegenover | `adres_aanduiding` "tegenover" (ruwe waarde in `adres_aanduiding_bron`) |
| A3 `MIP` | Prima, extra informatie | Blijft in de popup |
| A3 `Met` | Klopt | Blijft |
| A3 `Muur` | Onvolledig, laat weg | Uit popup én uit de open data |
| A3 `Kadaster` | Hoeft niet getoond | Uit popup én uit de open data |
| A3 `Circa` | Akkoord; bij een concrete datum gaat "ja" weg | Blijft "ca. 1750" |
| A3 `Jaartal` | Jaar van aanleg of eerste begraving | Tekst bij het dateringsfilter aangepast |
| A3 `Grondvorm` | Niet van belang | Uit popup én uit de open data |
| A3 `Gemeentelijk monument` | "Geen" = "Nee" | Genormaliseerd (ruwe waarde bewaard) |
| A3 `Grootte` | Oppervlakte van de shape in Google Earth, niet het Kadaster | Uitleg op de methodepagina |
| A3 `Laatste bezoek` | Hoeft niet getoond | Uit popup én uit de open data |
| A3 `Rmon` | Eén cel; bij een complex is het complexnummer gekozen | Blijft zo (A6) |
| A4 / E3 | Joodse begraafplaatsen worden niet gesloten; geen onderscheid. Liever "In gebruik" | Status heet nu **In gebruik** (kaart, legenda, methode, og-afbeelding) |
| A5 | Punt ligt meestal waar de begraafplaats lag, maar zegt niets over grootte; zekerheid niet hoog | Altijd "bij benadering"; uitleg op methodepagina |
| A6 | Complex opzoeken is goed zo | Blijft; zie N1 voor de opmerking over de RCE-contour |
| A7 Bussum | 527225 hoort bij de gemeentelijke begraafplaats | Relatie "de algemene begraafplaats waar dit deel bij hoort" |
| A7 Overveen | 529524 = toegangspoort, hoort erbij | Relatie "hoort bij de begraafplaats" |
| A7 Middelburg | 508330 moet een metaheerhuisje zijn | Relatie "hoort bij de begraafplaats" |
| B2 / B4 | Gelijke oppervlakte is toeval; vormen zijn nooit gekopieerd. Vroege polygonen zijn weinig nauwkeurig | Geen actie; methodepagina noemt de beperkte nauwkeurigheid |
| B3 | Niet op letten; sommige shapes zijn oud | Geen actie |
| B5 | Houd de Excel-naam aan | Zo gedaan (KMZ-naam alleen in het koppelrapport) |
| B6 | Twee echte plekken; naam aanvullen met periode mag | `jb-ver-471` "… Crooswijk (1696–1807)", `jb-ver-872` "… Crooswijk (vanaf 1877)" via `corrections.csv` |
| B7 | De geruimde mag "Oude Joodse begraafplaats" heten | `jb-ver-182` hernoemd via `corrections.csv` |
| B8 | Maassluis: Leon past aan. Schiedam Grootte: nog niet bekend | Wacht op nieuwe bronbestanden |
| C1 | Grondvorm, eigenaren en laatste bezoek eruit | Gedaan |
| C2 | Eigenaren helemaal niet tonen (onvolledig) | Eigenaar en postadres uit popup én open data |
| C3 | Bijna alles is al openbaar (Wiki, Google Maps) | Alles blijft getoond |
| C4 | Iets voor later | Geen actie |
| C5 | Liever geen foto's | Geen foto's |
| C6 | Kan interessant zijn, doe maar | Popup "Overgebracht naar" / "Herbegraven vanuit" + kaartlaag "Herbegravingen" (6 eenduidige gevallen, `data/herbegravingen.csv`); rest zie N3 |
| C8 | Leon heeft de RCE al uitvoerig gecontroleerd | Geen controlelijst; niet meer voorstellen |
| C7 | Dat tabblad had niet mee gemoeten | Blijft ongeopend; geen dankwoord |
| C9 | 1829 geen zinvolle grens; generiek; geen focus op WOII | Indeling: vóór 1700 · 1700–1799 · 1800–1849 · 1850–1899 · 1900–1949 · 1950–heden |
| D1 | Prima. René: lichtroze slecht zichtbaar, moeite met kleurovergangen; liever harde contrasten | Statuskleuren blijven; gezichten zonder lichte vlakvulling, donkerpaarse dikkere stippellijn |
| D2 | Prima | — |
| E1 | Huisstijlkleur en logo apart aangeleverd | Scherper logo + kleur `#8d161c` voor titel, links, knoppen; nooit als datakleur |
| E4 | Geen namen op de kaart is prima | Blijft zo |
| F4 | Kaart blijft intern tot publicatie boeken; nog niet indexeren | `noindex` (meta + `X-Robots-Tag`), sitemap niet meer in robots.txt |

## Navragen (antwoord niet eenduidig)

- **N1 (A6).** "De contour die de RCE geeft van de Joodse begraafplaats klopt echt niet. Het metaheerhuis staat op de algemene begraafplaats … dat hele perceel is een gemeentelijke begraafplaats." Over welke begraafplaats gaat dit (Bussum? Wassenaar?), en wat moeten we op de kaart anders doen?
- **N2 (A7 Alkmaar).** "Geen complex, maar twee losse rijksmonumenten." Bedoel je dat 7464 en 524892 allebei bij de Joodse begraafplaats horen? (RCE registreert 524892 als complex met 524893 baarhuisje en 524894 hek.)
- **N3 (C6).** Herbegravingen waarvan de bestemming niet eenduidig is:
  - `jb-ver-896` Beverwijk → "Duinhof". Op de kaart staat `jb-loc-2804` *op Duinrust* (Beverwijk, vanaf 1950). Is dat dezelfde?
  - `jb-ver-498` Leerdam → "voorste begraafplaats op Dijk": `jb-loc-239` (Joods deel achter de Algemene begraafplaats) of `jb-loc-366` (Joodse begraafplaats op Algemene Begraafplaats)?
  - `jb-loc-2849` Hoorn: "228 zerken overgebracht" — van de verdwenen `jb-ver-168` (1762–1970)?
  - `jb-ver-182` Dordrecht → Strijen staat erin; de tekst noemt ook "nieuwe begraafplaats en Rotterdam?". Alleen Strijen?
  - Gouda (`jb-ver-280`, `jb-ver-281`) → Wageningen volgt met Gelderland.
- **N4 (A2/A3/B8).** Leon heeft bronbestanden gecorrigeerd (Puttershoek, Maassluis) en noemt een eindjaar bij verdwenen begraafplaatsen; in onze Excel staat geen kolom eindjaar. Kunnen we de nieuwste Excel en KMZ's krijgen?

## G. Gelderland (nieuw, 2026-10-02)

Alle 61 Gelderse begraafplaatsen zijn gekoppeld (45 in gebruik, elk met terrein; 16 verdwenen). Herbegravingen op de kaart: Arnhem (2×) → Moscowa, Hengelo → Zutphen, Afferden → Nijmegen (Huis der Levenden), Bredevoort oud → nieuw, Doesburg Ooipoortwal en Veerpoortwal → buiten de Meipoort → Doetinchem.

**G1. Gouda → Wageningen.** `jb-ver-280` en `jb-ver-281` (Gouda) zijn in 1976 "overgebracht naar Wageningen". Wageningen heeft er twee: `jb-loc-2887` (vanaf 1913) en `jb-loc-4219` (Kerkhofpad, 1668–1929). Naar welke?
*Nu:* alleen als tekst in Bijzonderheden.

**G2. Winterswijk, Oude Israëlitische Begraafplaats** (`jb-loc-2826`). `Rmon` verwijst naar complex 523457, met als onderdelen synagoge (39057), onderwijzerswoning, schoolgebouw en begraafplaatshek. Dat lijkt het synagogecomplex. Klopt het nummer, of hoort hier een ander nummer?
*Nu:* het complex en de onderdelen staan in de popup.

**G3. Moscowa, Arnhem** (`jb-loc-2615`). Volgens RCE liggen op het terrein 516728 (begraafplaatsaula) en 516729 (muur). Horen die bij het Joodse deel, of bij de algemene begraafplaats Moscowa?
*Nu:* getoond als "op het terrein".

## O. Overijssel (nieuw, 2026-10-02)

Alle 43 Overijsselse begraafplaatsen zijn gekoppeld (34 in gebruik, 1 geruimd, 8 verdwenen; 35 terreinen). Enschede Kneedweg (`jb-loc-3027`) en Esmarkerrondweg (`jb-loc-3002`) zijn handmatig aan hun terrein gekoppeld: het punt ligt erin en de oppervlakte klopt, alleen de namen verschillen (Israëlitisch ↔ Joods). Herbegravingen op de kaart: Kampen → IJsselmuiden, Losser → Enschede (Kneedweg), Rijssen De Hagen → Arend Baanstraat, Zwolle Luurderschans → Kuyerhuislaan.

**O1. Denekamp** (`jb-loc-2459`). In de Excel staat geen rijksmonument, maar RCE-monument 12342 "Begraafplaats en -onderdelen" overlapt het terrein. Is dat de Joodse begraafplaats zelf, of een andere begraafplaats ernaast?
*Nu:* getoond als "overlapt het terrein".

**O2. Dedemsvaart** (`jb-loc-4021`, Joodse begraafplaats op de gemeentelijke begraafplaats). RCE-monument 515827 "De Mulderij" (begraafplaats) overlapt het terrein. Is dat de algemene begraafplaats waar het Joodse deel bij hoort, zoals in Bussum?
*Nu:* getoond als "overlapt het terrein".

## NB. Noord-Brabant (nieuw, 2026-10-02)

Alle 31 Brabantse begraafplaatsen zijn gekoppeld (21 in gebruik, elk met terrein; 10 verdwenen). Herbegravingen op de kaart: Breda → Oosterhout (Vrachelse Heide; Breda noemt 1961, Oosterhout 1958), Cuijk Smidstraat → Wilhelminastraat (1924) → Kouwenberg (1963).

**NB1. Putte: bij welke begraafplaats hoort rijksmonument 516689?** In de Excel staat complex 516689 ("Israëlitische begraafplaats") bij Mahsike Hadas (`jb-loc-189`). Maar de onderdelen van dat complex (aula 525638, grafmonumenten 516691 en 525640, 525639) liggen volgens de RCE allemaal op het terrein van de **Frechie Foundation** (`jb-loc-195`), ruim 200 m van het terrein van Mahsike Hadas. Hoort het nummer bij de Frechie Foundation, of staan de monumenten bij de RCE op de verkeerde plek?
*Nu:* het complex staat in de popup van Mahsike Hadas; bij de Frechie Foundation staan de onderdelen als "op het terrein".

**NB2. Eindhoven Tongelre → "Woensel".** `jb-ver-21` zegt "lijken overgebracht naar Woensel". De enige Joodse begraafplaats in gebruik in Eindhoven is `jb-loc-986` (Groenewoudseweg). Is dat de bedoelde plek in Woensel, of zijn ze naar een algemene begraafplaats gegaan?
*Nu:* alleen als tekst in Bijzonderheden.

Nog open hieronder: alles zonder ✅. Nog helemaal onbeantwoord: A1, D3 (René kijkt nog), E2, E5–E9, F1–F3.

---

## A. Voor Leon – de bronbestanden

**A1. Nummerreeksen.** Het `Nr` in de Excel is niet uniek. Wij gaan ervan uit dat elke status een eigen reeks en een eigen bestand heeft: *In gebruik* → `Locaties.kmz`, *Verdwenen* → `Verdwenen.kmz` ("Verdwenen 0182"), *Geruimd* → `Geruimd.kmz`. Daarmee vinden we voor alle 315 rijen precies één punt. Klopt dit, en blijft het zo bij nieuwe versies?
*Nu:* zo gekoppeld.

**✅ A2. Dubbel nummer in Geruimd.kmz.** Nr 245 staat twee keer in `Geruimd.kmz`: "NH kerkhof, Puttershoek" en "H Martinuskerkhof, Pannerden". Niet Joods, dus niet op onze kaart, maar wel een fout in de bron?

**✅ A3. Betekenis van kolommen.** Alle kolommen beantwoord (zie de tabellen bovenaan).

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

**✅ A4. Status "In gebruik".** Daaronder vallen ook begraafplaatsen die gesloten zijn maar nog bestaan, zoals Haarlem Kleverlaan ("1969 gesloten") en Rotterdam Delfshaven ("1865–1898"). Op de kaart noemen we de status daarom **"Bestaand"**. Willen jullie onderscheid tussen *in gebruik* en *gesloten*? Dan hebben we die informatie per begraafplaats nodig, bijvoorbeeld als extra kolom.

**✅ A5. Verdwenen: hoe precies is de plek?** Alleen een puntlocatie, zekerheid niet hoog → altijd bij benadering. We tonen verdwenen begraafplaatsen als open ring met de tekst "plek bij benadering", en berekenen er geen afstanden tot monumenten voor.
- Waar is de plek op gebaseerd (archief, kadastrale minuut, overlevering)?
- Kunnen jullie per verdwenen begraafplaats aangeven hoe zeker de plek is (bv. *exact* / *straat* / *alleen de plaats*)? Dan kunnen we dat zichtbaar maken.
- Twee verdwenen begraafplaatsen hebben jaartal "onbekend": `jb-ver-774` (Oude Joodse begraafplaats, Leerdam) en `jb-ver-425` (Maassluis).

**✅ A6. Rmon bevat vaak een complexnummer.** Kan voorkomen; blijft zo. Nog open: Wassenaar/Kerkehout en N1. Van de 19 rijksmonumentnummers in West-Nederland zijn er 8 een complexnummer: Alkmaar, Bussum, Muiderberg, Amersfoort (nieuw), Leerdam, Utrecht, Gorinchem en Wassenaar. We zoeken het complex op en tonen de onderdelen (begraafplaats, baarhuisje, hek …) in de popup.
- Is dat de bedoeling, of moet het het monumentnummer van de begraafplaats zelf zijn?
- Wassenaar (`jb-loc-1343`) verwijst naar complex 524542 **"Begraafplaats Kerkehout"**. Is dat de algemene begraafplaats waar het Joodse deel bij hoort?

**A7. Rijksmonumenten op het terrein die niet in de Excel staan.** Volgens RCE ligt er een rijksmonument op of over het terrein dat niet in `Rmon` staat. Horen deze bij de begraafplaats?
- Alkmaar (zie N2) `jb-loc-2923`: 7464 "Begraafplaats en -onderdelen" (op het terrein). In de Excel staat complex 524892.
- ✅ Bussum `jb-loc-1503`: 527225 "Begraafplaats" (overlapt) — deel van de gemeentelijke begraafplaats
- ✅ Overveen `jb-loc-4201`: 529524 "Poortgebouw" (overlapt) — toegangspoort, hoort erbij
- ✅ Wijk bij Duurstede `jb-loc-819`: 454310 "Historische aanleg" — valt er net buiten
- ✅ Middelburg `jb-loc-21`: 508330 "Baarhuisje" (op het terrein) — metaheerhuisje, hoort erbij

## B. Voor Leon – specifieke begraafplaatsen

**B1. ✅ Bilthoven, Progressieve joodse begraafplaats** — alleen puntlocatie, geen terrein. (`jb-loc-4368`, 300 m²). In `Funerair Utrecht.kmz` staat geen terrein voor deze begraafplaats. Het punt ligt 10 m naast "Gem. begraafplaats Brandenburg". Kunnen jullie het terrein aanleveren, of is het een deel van Brandenburg zonder eigen grens?
*Nu:* alleen een punt, geen terrein.

**✅ B2. Vlissingen.** Twee aparte polygonen, 551 m uit elkaar, met **exact dezelfde oppervlakte (694 m²)**. Dat wijst op een gekopieerde vorm.

| Kenmerk | Excel-naam | Excel Grootte | Gekoppeld terrein |
|---|---|---|---|
| `jb-loc-9` | Joodse Begraafplaats bij de Leeuwentrap (1866–1907) | 350 m² | "Oude joodse begraafplaats, Vlissingen" (handmatig gekoppeld) |
| `jb-loc-908` | Joodse Begraafplaats op Begraafplaats Vredehof (1907–1970) | 865 m² | "Nieuwe Joodse begraafplaats, Vlissingen" |

Klopt de koppeling, en welke polygoon heeft de verkeerde vorm?

**✅ B3. Terrein veel groter of kleiner dan `Grootte`.** Is het terrein fout getekend, of klopt de maat in de Excel niet?

| Kenmerk | Begraafplaats | Terrein (KMZ) | Grootte (Excel) |
|---|---|---|---|
| `jb-loc-2804` | Beverwijk (op Duinrust) | 137 m² | 870 m² |
| `jb-loc-2369` | Almere | 2.854 m² | 4.875 m² |
| `jb-loc-238` | Goes (op alg. begraafplaats) | 1.057 m² | 670 m² |
| `jb-loc-9` | Vlissingen, Leeuwentrap | 694 m² | 350 m² |

Ter vergelijking: de andere 64 terreinen liggen allemaal binnen 75–133 % van `Grootte`.

**✅ B4. Rhenen en Edam.** Beide terreinen zijn exact 372 m² groot (70 km uit elkaar). Toeval, of ook een gekopieerde vorm?

**✅ B5. Naamsverschillen KMZ ↔ puntbestand.** Op de kaart staat de Excel-naam ("houd de Excel-naam aan"). Het punt ligt in het terrein en we hebben gekoppeld, maar de namen verschillen. Zijn het alleen schrijfvarianten?
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

**✅ B6. Twee keer dezelfde naam.** `jb-ver-471` (vanaf 1696, tot 1807) en `jb-ver-872` (vanaf 1877) heten in de Excel allebei "Portugees Israëlitische Begraafplaats Crooswijk" (Rotterdam). Ze liggen 430 m uit elkaar. Zijn dit twee verschillende begraafplaatsen? Mogen we de naam aanvullen, bijvoorbeeld met de periode?

**✅ B7. Dordrecht.** De verdwenen `jb-ver-182` (1738, geruimd 1958) en de bestaande `jb-loc-1912` hebben exact dezelfde naam. Wij houden ze apart. Klopt dat?

**B8. Kleine fouten in de bronbestanden** (we passen niets aan, ter info):
- ✅ `Locaties.kmz`: "Sombre Hadas, Putte" — juist is "Shomre Hadas" (zoals in de Excel)
- `Verdwenen.kmz`: "Joodse begraafplats, Maassluis" (tikfout)
- `jb-ger-64` Schiedam: Grootte "?"

## C. Voor Leon/René – inhoud van de kaart

**✅ C1. Popup.** Nu getoond: naam, status, plaats, gemeente, adres (met bij/tegenover), sinds (jaartal), grootte, grondvorm, rijksmonument (of complex met onderdelen), metaheerhuis, gemeentelijk monument, MIP, beschermd deel, eigenaar (met postadres), bijzonderheden, beschermd gezicht, rijksmonumenten binnen 100 m, laatste bezoek en kenmerk.
- Moet er iets uit, bijvoorbeeld *grondvorm*, *laatste bezoek* of *kenmerk*?
- Mist er iets?
- Klopt de volgorde?

**✅ C2. Eigenaren.** Bij 36 bestaande begraafplaatsen is geen eigenaar bekend. Zijn alle eigenaren organisaties (NIG, NIK, Joodse gemeenten, gemeente Amsterdam)? Of staan er ook privépersonen tussen die we niet met naam en adres moeten tonen?

**✅ C3. Gevoeligheid van locaties.** Moeten we bij kleine of kwetsbare begraafplaatsen rekening houden met vandalisme of antisemitisme? Bijvoorbeeld door geen exacte ingang of terrein te tonen? Of is alles al openbaar via dodenakkers.nl?
*Nu:* alles getoond.

**✅ C4. Verwijzing naar dodenakkers.nl.** Heeft elke begraafplaats een eigen pagina op dodenakkers.nl? Dan zetten we per begraafplaats een link "Meer op Dodenakkers" in de popup. Waarschijnlijk hebben we daarvoor een kolom met URL of paginanummer nodig.

**✅ C5. Foto's.** Zijn er foto's per begraafplaats die we in de popup mogen tonen (met naam van de fotograaf)? Hoe leveren jullie die aan?

**✅ C6. Herbegravingen.** Veel records zeggen "overgebracht naar …" (Schiedam → Toepad, Leiden → Katwijk, Gouda → Wageningen, Dordrecht → Strijen). Willen jullie dat als lijn of verwijzing op de kaart?
*Nu:* alleen als tekst in Bijzonderheden.

**✅ C7. Dankwoord.** Het tabblad "Dank en informeren" in de Excel hebben we bewust niet geopend, omdat er persoonsgegevens in staan. Moeten er namen van mensen of organisaties op de site komen (bijvoorbeeld op de methodepagina)? Zo ja: welke, en hebben zij daar toestemming voor gegeven?

**✅ C8. Begraafplaatsen die nog niet in de lijst staan.** Niet nodig: Leon heeft dit al uitvoerig gecontroleerd. Moeten we RCE controleren op monumenten met functie "Joodse begraafplaats" die niet in de Excel staan, en die lijst aan jullie geven (niet op de kaart)?

**✅ C9. Datering: indeling van de balkjes.** Het filter "Datering" gebruikt voorlopig dezelfde indeling als de kaart van Dodenakkers Zuid-Holland: vóór 1829 · 1829–1849 · 1850–1899 · 1900–1949 · 1950–1999 · 2000–heden. Op de kaart van Zuid-Holland verwees 1829 naar het verbod op begraven in en rond de kerk. Dat geldt niet voor Joodse begraafplaatsen, en daarom hebben we die uitleg weggelaten.
- Is 1829 hier een zinvolle grens, of past een andere indeling beter? Mogelijke grenzen zijn 1796 (gelijkberechtiging van Joden), 1869 (Begrafeniswet) en 1940–1945. Of een indeling die jullie zelf gebruiken.
- Nu valt meer dan de helft (48 van de 89 bekende jaartallen) in "vóór 1829". Is een splitsing in de 17e en 18e eeuw gewenst? Verdeling West-Nederland: vóór 1700: 10 · 1700–1799: 26 · 1800–1828: 12.
- Is `Jaartal` het jaar van aanleg (zie ook A3)? En willen jullie voor verdwenen en geruimde begraafplaatsen ook het eindjaar als apart veld? Dat staat nu alleen in Bijzonderheden.
*Nu:* indeling van dodenakkers-zh, zonder "Middeleeuws" (komt niet voor), zonder uitleg over 1829.

## D. Voor René – kleuren en leesbaarheid

**✅ D1. Kleuren.** Bestaand = blauw rondje ●, geruimd = oranje ruit ◆, verdwenen = donkergrijze open ring ○. Gekozen omdat ze onderscheidbaar blijven bij de drie vormen van kleurenblindheid (gesimuleerd), en omdat elke status ook een eigen vorm heeft. Graag testen:
- Zie je de drie statussen goed uit elkaar, op de grijze kaart én op de luchtfoto?
- Is de terreinkleur (blauw/oranje vlak) duidelijk genoeg?
- Welke vorm van kleurenblindheid heb je? Dan kunnen we gericht testen.

**✅ D2. Contextlagen.** Gezichten (paars gestippeld), rijksmonumenten (donkergrijze stip), archeologische monumenten (bruin) en gemeentegrenzen (grijs gestippeld). Zijn deze goed te onderscheiden van de begraafplaatsen?

**D3. Leesbaarheid.** Is de tekstgrootte in het paneel en de popup goed, ook op je telefoon?

## E. Layout en presentatie

**✅ E1. Huisstijl.** De kaart gebruikt het Dodenakkers-logo (`.webp`, klein formaat) en verder een neutrale stijl (systeemlettertype, wit paneel).
- Is er een scherpere versie van het logo (SVG of PNG van minstens 400 px breed)?
- Zijn er huisstijlkleuren of een lettertype die we moeten gebruiken?

**E2. Titel en introtekst.** Nu: titel "Joodse Begraafplaatsen" met als intro "Bestaande, geruimde en verdwenen Joodse begraafplaatsen, uit de inventarisatie van stichting Dodenakkers."
- Willen jullie een eigen introtekst, bijvoorbeeld over de Joodse begraafcultuur, de eeuwige grafrust of de oorlog?
- Wie schrijft die, en moet hij langs een Joodse organisatie?

**✅ E3. Statusnamen.** "Bestaand / Geruimd / Verdwenen", of liever de termen uit de Excel ("In gebruik")? Zie ook A4.

**✅ E4. Namen op de kaart.** Er staan nu geen namen bij de punten; die zie je in de lijst en de popup. Namen op de kaart vragen een eigen set lettertypebestanden op de server (kan, kost wat werk). Gewenst?

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

**✅ F4. Publiek of niet.** Mag de kaart nu al openbaar gedeeld worden? Of eerst intern blijven tot alle provincies klaar zijn? Zoekmachines mogen hem nu indexeren (robots.txt staat open).
