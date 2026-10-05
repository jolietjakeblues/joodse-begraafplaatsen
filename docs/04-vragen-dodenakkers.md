# 04 – Vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-05, 9 van 12 provincies (251 begraafplaatsen), na drie rondes antwoorden.
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

## Beantwoord ronde 3 (Word-document, Leon/René, 2026-10-05)

De vragen N1–N4, G1–G3, O1–O2, NB1–NB2 en L1–L3 uit ronde 2 en de provincies zijn hiermee beantwoord.

| Vraag | Antwoord | Verwerkt |
|---|---|---|
| N1 | Gaat over Wassenaar (`jb-loc-1343`); metaheerhuis staat formeel niet op de Joodse begraafplaats; nader onderzoek volgt | Niets op de kaart |
| N2 Alkmaar | 7464 is de begraafplaats zelf; RCE heeft hem niet aan complex 524892 toegevoegd | 7464 "hoort bij de begraafplaats" (`BEOORDEELDE_RELATIES`) |
| N3 Beverwijk | "Duinhof" moet Duinrust zijn | Herbegraving `jb-ver-896` → `jb-loc-2804` |
| N3 Leerdam | Twee overbrengingen naar de voorste (grotere) begraafplaats; twee pijlen | `jb-ver-498` en `jb-ver-774` → `jb-loc-366` (272 m² tegen 37 m² voor 239). Dat 774 de tweede is, is afgeleid: de enige andere verdwenen in Leerdam |
| N3 Hoorn | Ja, inclusief stoffelijke resten | `jb-ver-168` → `jb-loc-2849` |
| N3 Dordrecht | Eerst naar die bij de gemeentelijke begraafplaats van Dordrecht, later een deel naar Strijen | `jb-ver-182` → `jb-loc-1912` én → `jb-loc-1945` |
| N4 | Eindjaar-kolom hoeft niet mee | Geen actie |
| G1 / N3 Gouda | Naar de nieuwe Joodse begraafplaats van Wageningen | `jb-ver-280`, `jb-ver-281` → `jb-loc-2887` |
| G2 Winterswijk | Klopt helemaal | Blijft |
| G3 Moscowa | Aula en muur horen bij de Joodse begraafplaats | 516728 en 516729 "hoort bij de begraafplaats" |
| O2 Dedemsvaart | Contour opnieuw gedaan; ligt naast het rijksmonument | Nieuw terrein + ingang uit `funerair_nieuwedata.kmz` (796 → 641 m², ingang 35 m verschoven); 515827 nu "binnen 25 m" |
| NB1 Putte | Nummer 516689 hoort bij de Frechie Foundation; gecorrigeerd in de Excel | Wacht op de nieuwe Excel (zie R3) |
| NB2 Eindhoven | Woensel is in 1920 bij Eindhoven gevoegd; = Groenewoudseweg | `jb-ver-21` → `jb-loc-986` |
| L1 Sittard | Vrangendael = volksnaam van Lahrhof | `jb-ger-43`, `jb-ver-12` → `jb-loc-580` |
| L2 Venlo | 37192 hoort bij `jb-loc-1125` (Oude); contour stond verkeerd door de bomen | Nieuw terrein + ingang uit `funerair_nieuwedata.kmz` (43 → 248 m²). Het RCE-punt van 37192 ligt op de Nieuwe (1110): daar "hoort bij een andere begraafplaats" |
| L3 Linne | Laat voorlopig staan | Blijft |
| A1 | Nummering is prima en te herleiden | Afgesloten |
| A6 | Complex tonen is prima | Afgesloten |
| B8 | Maassluis aangepast in de brondata; contour Schiedam nog onbekend | Wacht op nieuwe bronbestanden |
| D3 | Prima, zelfde als Zuid-Holland | Afgesloten |
| E2 | Prima zo | Afgesloten |
| E5 / E6 | Prima | Afgesloten |
| E7 | Statistiekpagina welkom; geen CSV; Engels later | Statistiekpagina gebouwd (`statistieken.html`, `scripts/compute_statistics.py`) |
| E8 | Misschien later op www.funerair-erfgoed.nl; alleen via hun eigen sites | Nog niets |
| E9 | Voorlopig goed zo | Geen actie |
| F1 | Liefst een invulformulier met het nummer uit de lijst | GitHub-issueformulier: link "Correctie doorgeven" in elke popup, kenmerk al ingevuld (gratis GitHub-account nodig; meldingen zijn openbaar) |
| F2 | Excel verandert vaker dan de KMZ's; shapes liggen redelijk vast | Past bij de werkwijze |
| F3 | (leeg) | Volgorde Groningen, Drenthe, Fryslân |

Opmerking Joop (2026-10-05): op de leespagina geen "Uitgelicht" meer, alle artikelen gewoon in de lijst; en vanuit de popup naar de artikelen verwijzen. Gedaan: popup "Lees op Dodenakkers".

## Navragen ronde 3

- **R1 (B5, namen).** "Groen is de juiste" — groen waren de terreinnamen uit de KMZ (bv. "Hoogduitse Joodse begraafplaats", "Nieuwe Joodse begraafplaats" Vlissingen, "Beth Haim", "Joodse begraafplaats Diemen/Muiderberg"). In ronde 2 schreef Leon "houd de Excel-naam aan". Past Leon de namen in de Excel aan, of moeten wij de groene namen als weergavenaam instellen?
- **R2 (O1 Denekamp).** "Onze contour is de daadwerkelijke begraafplaats, niet het hele perceel." Is RCE-monument 12342 dan het rijksmonument van de Joodse begraafplaats (met een ruimere grens)? Dan zou de Excel bij `jb-loc-2459` "rijksmonument ja" moeten hebben.
- **R3 (NB1, B8).** De gecorrigeerde Excel (Putte, Maassluis, Puttershoek) hebben we nog niet. Graag in de gedeelde map.

Nog open: R1–R3, E8 (later).

De gedetailleerde vragen hieronder zijn het archief van ronde 1–2; de tabellen hierboven zijn leidend.

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
