// Instellingen van de kaart: databestanden, kleuren, ondergronden, teksten.

export const DATA = {
  begraafplaatsen: "data/generated/begraafplaatsen.geojson",
  terreinen: "data/generated/terreinen.geojson",
  herbegravingen: "data/generated/herbegravingen.geojson",
  // Artikelen op dodenakkers.nl (scripts/fetch_leeslijst.py); popup_ids zegt
  // bij welke begraafplaatsen het artikel in de popup staat.
  leeslijst: "data/generated/leeslijst.json",
  provincies: "data/pdok/provincies.geojson",
  gemeenten: "data/pdok/gemeenten.geojson",
  // RCE-lagen staan per provincie in aparte bestanden; dit manifest
  // (scripts/fetch_rce.py) zegt welke. Rijksmonumenten: alleen binnen 100 m
  // van een begraafplaats (besluit 2026-10-02).
  rceManifest: "data/rce/index.json",
  // Vervallen kenmerk -> nieuw kenmerk (scripts/build_site.py uit data/kenmerken.json).
  doorverwijzingen: "data/doorverwijzingen.json",
};

// Kleuren gekozen op onderscheidbaarheid bij protanopie, deuteranopie en
// tritanopie (gesimuleerd, minimale kleurafstand >= 38 Delta-E), en daarnaast
// een eigen VORM per status zodat kleur nooit de enige drager is.
// "In gebruik" (niet "Bestaand"): Joodse begraafplaatsen worden in principe
// niet gesloten (Leon 2026-10-02, vragen A4/E3).
export const STATUS = {
  in_gebruik: { label: "In gebruik", kleur: "#0072B2", vorm: "cirkel" },
  // Oranje haalt op wit/grijs maar ~2:1; de donkerbruine rand (5,3:1) maakt de
  // ruit en het terrein toch zichtbaar genoeg (WCAG 1.4.11, review 2026-10-05).
  geruimd: { label: "Geruimd", kleur: "#E69F00", rand: "#8a5a00", vorm: "ruit" },
  verdwenen: { label: "Verdwenen", kleur: "#3A3A3A", vorm: "ring" },
};

export const KLEUR = {
  provincie: "#4a4a4a",
  gemeente: "#8a8a8a",
  // donker paars, zonder lichte vlakvulling: René ziet lichtroze slecht en
  // vraagt om harde contrasten (vraag D1)
  gezicht: "#5b2a86",
  rijksmonument: "#3d3d3d",
  archeologisch: "#8b5a2b",
  herbegraving: "#3A3A3A",
};

export const BASEMAPS = {
  grijs: {
    tiles: [
      "https://service.pdok.nl/kadaster/brt-achtergrondkaart/wmts/v2_0?service=WMTS&request=GetTile&version=1.0.0&layer=grijs&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Kaart: <a href="https://www.pdok.nl/">PDOK</a> · BRT Kadaster',
  },
  luchtfoto: {
    tiles: [
      "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?service=WMTS&request=GetTile&version=1.0.0&layer=Actueel_orthoHR&style=default&tilematrixset=EPSG:3857&format=image/jpeg&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Luchtfoto: <a href="https://www.pdok.nl/">PDOK</a> · Beeldmateriaal.nl',
  },
  bgt: {
    tiles: [
      "https://service.pdok.nl/kadaster/bgt/wmts/v1_0?service=WMTS&request=GetTile&version=1.0.0&layer=standaardvisualisatie&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Kaart: <a href="https://www.pdok.nl/">PDOK</a> · BGT Kadaster',
    // PDOK geeft tot en met zoom 16 een lege (geldige) tegel; pas vanaf 17 beeld
    // (vastgesteld in het dodenakkers-project).
    minzoom: 17,
  },
};

// Overlay (transparant), geen eigen ondergrond. Zelfde zoomgrens als BGT.
export const BRK_PERCELEN = {
  tiles: [
    "https://service.pdok.nl/kadaster/kadastralekaart/wmts/v5_0?service=WMTS&request=GetTile&version=1.0.0&layer=Kadastralekaart&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
  ],
  attribution: 'Percelen: <a href="https://www.pdok.nl/">PDOK</a> · BRK Kadaster',
  minzoom: 17,
};

// Relatie van een rijksmonument tot het terrein (scripts/analyse_spatial.py),
// inclusief de door Dodenakkers beoordeelde relaties.
export const RELATIE = {
  op_terrein: "op het terrein",
  grenst_aan: "grenst aan het terrein",
  overlapt: "overlapt het terrein",
  "0-25m": "binnen 25 m",
  "25-100m": "25–100 m",
  "100-250m": "100–250 m",
  net_buiten: "net buiten het terrein",
  hoort_bij: "hoort bij de begraafplaats",
  hoort_bij_andere: "hoort bij een andere begraafplaats (de RCE plaatst het hier)",
  algemene_begraafplaats: "de algemene begraafplaats waar dit deel bij hoort",
};

// Datering: klikbare balkjes zoals in dodenakkers-zh, met een generieke
// indeling: 1829 is voor Joodse begraafplaatsen geen zinvolle grens en een
// aparte oorlogsperiode is niet gewenst (Leon 2026-10-02, vraag C9).
// `jaartal` = jaar van aanleg of eerste begraving; "ca." telt gewoon mee.
export const DATERING = [
  { id: "voor1700", label: "vóór 1700", test: (j) => j < 1700 },
  { id: "1700", label: "1700–1799", test: (j) => j >= 1700 && j < 1800 },
  { id: "1800", label: "1800–1849", test: (j) => j >= 1800 && j < 1850 },
  { id: "1850", label: "1850–1899", test: (j) => j >= 1850 && j < 1900 },
  { id: "1900", label: "1900–1949", test: (j) => j >= 1900 && j < 1950 },
  { id: "1950", label: "1950–heden", test: (j) => j >= 1950 },
];

// Andere namen bij het zoeken (al genormaliseerd: kleine letters, zonder accenten
// en leestekens). Zoekt iemand op de linkerkant, dan telt ook de rechterkant.
export const ZOEK_ALIASSEN = {
  "den haag": "s gravenhage",
  "s gravenhage": "den haag",
  "den bosch": "s hertogenbosch",
  "s hertogenbosch": "den bosch",
  "friesland": "fryslan",
  "fryslan": "friesland",
};
// Geen alias Joods <-> Israëlitisch: dan matcht vrijwel elke begraafplaats.

// Correcties gaan via een GitHub-issueformulier (.github/ISSUE_TEMPLATE/correctie.yml,
// vraag F1). Veldnamen kenmerk/naam moeten gelijk blijven aan de id's in dat formulier.
export const REPO_URL = "https://github.com/jolietjakeblues/joodse-begraafplaatsen";

// Externe links alleen naar bekende bronnen (monumentenregister RCE, dodenakkers.nl).
export const LINK_DOMEINEN = ["monumentenregister.cultureelerfgoed.nl", "www.dodenakkers.nl", "linkeddata.cultureelerfgoed.nl"];
