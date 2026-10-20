# 04 – Open vragen aan Dodenakkers (Leon, René)

Stand: 2026-10-20 · Kaart: https://joodse-begraafplaatsen.jolietjakeblues64.workers.dev · Gedeelde vragenpagina: https://claude.ai/artifact/9Rbm99cCckt7yGDwb52kg8

Alleen wat nog een antwoord nodig heeft. Alles wat beantwoord en verwerkt is staat in [05-vragen-beantwoord.md](05-vragen-beantwoord.md). Per vraag staat erbij **wat we nu doen**; zonder antwoord blijft dat zo.

Kenmerken als `jb-loc-1559` staan in de kaartpopup onder "Kenmerk": `loc` = in gebruik, `ver` = verdwenen, `ger` = geruimd, plus het Nr uit de Excel. Correcties kunnen ook via de link "Correctie doorgeven" in de popup.

## Samenvatting

Er staan geen vragen open (stand 2026-10-20). Emmen is volgens Leon "geheel correct nu, klopt ook met alle eigen gegevens".

## Verwacht van Dodenakkers (geen vraag)

Dingen die Leon in de bron aanpast. Wij doen er nu niets aan, zodat de juiste waarde op één plek staat: in de Excel of KMZ van Dodenakkers.

- **Zerken → stèles.** Bij veel begraafplaatsen staat in Bijzonderheden "… zerken", maar volgens Leon (2026-10-20) moeten dat bij de meeste "stèles" zijn. Leon corrigeert dat in de Excel. We vervangen het niet zelf: het geldt voor "de meeste", niet voor alle, en alleen Leon weet welke. Assen (`jb-loc-3642`) is al aangepast via issue #21. Na de nieuwe Excel: de correctieregel van Assen in `data/corrections.csv` weghalen als de Excel dezelfde tekst heeft.
- **Nieuwe jaartallen.** Dodenakkers doet onderzoek naar Joodse begraafplaatsen; er kunnen nog jaartallen veranderen. Graag via het correctieformulier (losse punten) of een volledige nieuwe Excel. Goedereede (1802) en Dirksland (1812) staan sinds 2026-10-19 in `data/corrections.csv`; Leon heeft ze ook in de bron aangepast, dus die regels kunnen weg zodra die Excel er is.
- **Emmen in de KMZ.** De kaart klopt dankzij `data/punt_correcties.csv` (3075 ↔ 2183). Leon is tevreden; als hij de nummers in `Locaties.kmz` ooit omwisselt, moet die puntcorrectie weg, anders staan ze weer verkeerd om (de build zou dat niet merken).

---

## Ter info (geen antwoord nodig)

Kleine dingen in de bronbestanden; we passen de bron niet aan.

- `Funerair Groningen.kmz`: "Joodse begraaf**plats**, Leens" (tikfout) en 7 lege "Naamloos Polygoon".
- `Locaties.kmz`: het label van `jb-loc-3574` is "Joodse begraafplaats, Uithuizen**?**" (met vraagteken). De kaart gebruikt het nagestuurde punt (18 m verschoven) en sinds 2026-10-09 de nagestuurde contour uit `Voor Joop_2.kmz` (229 m²).
- Denekamp (`jb-loc-2459`): in de nieuwe Excel staat Rmon 12342, maar Rijksmonument "Nee". De kaart zegt "ja" (antwoord R2).
- Maassluis en Puttershoek: in de nieuwe Excel geen verandering gezien. Zit die correctie in een KMZ, dan graag bij een volgende levering.
- Schiedam (`jb-ger-64`): Grootte "?"; de contour is volgens Leon nog niet bekend.
