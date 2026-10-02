// Joodse Begraafplaatsen - kaartviewer
//
// Statisch: laadt vooraf berekende GeoJSON (scripts/*.py), geen live SPARQL.
// Alle paden zijn relatief, zodat de map site/ ook in een submap of via een
// <iframe> op een andere website (bv. dodenakkers.nl) kan draaien.
//
// URL-parameters
//   ?embed=1     compacte weergave voor inbedden (paneel standaard dicht)
//   #zoom/lat/lon  kaartpositie (MapLibre hash), deelbaar

const DATA = {
  begraafplaatsen: "data/generated/begraafplaatsen.geojson",
  terreinen: "data/generated/terreinen.geojson",
  provincies: "data/pdok/provincies.geojson",
  gemeenten: "data/pdok/gemeenten.geojson",
  // RCE-lagen staan per provincie in aparte bestanden; dit manifest
  // (scripts/fetch_rce.py) zegt welke. Rijksmonumenten: alleen binnen 100 m
  // van een begraafplaats (besluit 2026-10-02).
  rceManifest: "data/rce/index.json",
};

let manifestPromise = null;
async function loadRce(soort) {
  manifestPromise = manifestPromise || loadJson(DATA.rceManifest);
  const provincies = (await manifestPromise).provincies;
  const collecties = await Promise.all(Object.values(provincies).map((b) => loadJson(b[soort])));
  const gezien = new Set();
  const features = [];
  for (const fc of collecties) {
    for (const f of fc.features) {
      const key = f.properties.cho_uri || f.properties.gezicht_uri;
      if (gezien.has(key)) continue; // grensobjecten staan in twee provinciebestanden
      gezien.add(key);
      features.push(f);
    }
  }
  return { type: "FeatureCollection", features };
}

// Kleuren gekozen op onderscheidbaarheid bij protanopie, deuteranopie en
// tritanopie (gesimuleerd, minimale kleurafstand >= 38 Delta-E), en daarnaast
// een eigen VORM per status zodat kleur nooit de enige drager is.
const STATUS = {
  in_gebruik: { label: "Bestaand", kleur: "#0072B2", vorm: "cirkel" },
  geruimd: { label: "Geruimd", kleur: "#E69F00", vorm: "ruit" },
  verdwenen: { label: "Verdwenen", kleur: "#3A3A3A", vorm: "ring" },
};
const KLEUR = {
  provincie: "#4a4a4a",
  gemeente: "#8a8a8a",
  gezicht: "#7a5195",
  rijksmonument: "#3d3d3d",
  archeologisch: "#8b5a2b",
};

const params = new URLSearchParams(location.search);
// Vastleggen voordat MapLibre (hash: true) zelf een positie in de URL zet.
const START_HASH = location.hash;
const EMBED = params.get("embed") === "1";
document.body.classList.toggle("embed", EMBED);

const statusEl = document.getElementById("status");
const panelEl = document.getElementById("panel");
const panelToggleEl = document.getElementById("panel-toggle");

// ---------------------------------------------------------------- paneel

let panelOpen = !(EMBED || window.matchMedia("(max-width: 700px)").matches);

const miniLegendaEl = document.getElementById("mini-legenda");
function updatePanelToggle() {
  panelEl.classList.toggle("collapsed", !panelOpen);
  document.body.classList.toggle("panel-dicht", !panelOpen);
  // Met dichtgeklapt paneel blijft een mini-legenda zichtbaar (titel + symbolen).
  miniLegendaEl.hidden = panelOpen;
  panelEl.inert = !panelOpen; // dichtgeklapt paneel niet bereikbaar met Tab
  panelToggleEl.textContent = panelOpen ? "×" : "☰";
  panelToggleEl.setAttribute("aria-label", panelOpen ? "Paneel sluiten" : "Paneel openen");
  panelToggleEl.setAttribute("aria-expanded", String(panelOpen));
}
panelToggleEl.addEventListener("click", () => {
  panelOpen = !panelOpen;
  updatePanelToggle();
});
miniLegendaEl.addEventListener("click", () => {
  panelOpen = true;
  updatePanelToggle();
  panelEl.focus();
});
function toonFout(tekst) {
  statusEl.textContent = tekst;
  document.getElementById("mini-fout").textContent = tekst;
}
const IS_SMAL = () => window.matchMedia("(max-width: 700px)").matches;
updatePanelToggle();
if (EMBED) {
  const link = document.getElementById("open-volledig");
  link.href = "./" + location.hash;
}

// ---------------------------------------------------------------- helpers

const HTML_ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
function esc(value) {
  return String(value).replace(/[&<>"']/g, (c) => HTML_ESCAPES[c]);
}
class SafeHtml {
  constructor(html) {
    this.html = html;
  }
}
const raw = (html) => new SafeHtml(html);
function link(url, text) {
  if (!url || !/^https:\/\//.test(url)) return text ? esc(text) : "";
  return `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(text || url)}</a>`;
}
function rows(pairs) {
  return pairs
    .filter(([, v]) => v !== null && v !== undefined && v !== "" && !(v instanceof SafeHtml && !v.html))
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v instanceof SafeHtml ? v.html : esc(v)}</dd>`)
    .join("");
}
// Huisje-icoon voor een metaheerhuis(je) (Excel-kolom "Met"); inline SVG, geen externe bron.
const HUISJE =
  '<svg class="icoon-huisje" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M8 1.5 1 7.5h2v7h4v-4h2v4h4v-7h2z" fill="currentColor"/></svg>';
const fmtInt = (n) => (n == null ? null : Number(n).toLocaleString("nl-NL"));
const jaNee = (v) => (v === true ? "ja" : v === false ? "nee" : v);

async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json();
}

function boundsOf(fc) {
  const b = new maplibregl.LngLatBounds();
  const ext = (c) => (typeof c[0] === "number" ? b.extend(c) : c.forEach(ext));
  fc.features.forEach((f) => ext(f.geometry.coordinates));
  return b;
}

// Statussymbolen als bitmap (cirkel / ruit / ring), met witte rand zodat ze
// op luchtfoto en op elkaar zichtbaar blijven.
function makeSymbol(vorm, kleur, size = 44) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const m = size / 2;
  ctx.lineJoin = "round";
  if (vorm === "ruit") {
    const r = size * 0.42;
    ctx.beginPath();
    ctx.moveTo(m, m - r);
    ctx.lineTo(m + r, m);
    ctx.lineTo(m, m + r);
    ctx.lineTo(m - r, m);
    ctx.closePath();
    ctx.fillStyle = kleur;
    ctx.fill();
    ctx.lineWidth = size * 0.08;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
  } else if (vorm === "ring") {
    ctx.beginPath();
    ctx.arc(m, m, size * 0.3, 0, Math.PI * 2);
    ctx.lineWidth = size * 0.22;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
    ctx.lineWidth = size * 0.13;
    ctx.strokeStyle = kleur;
    ctx.stroke();
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.beginPath();
    ctx.arc(m, m, size * 0.22, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.arc(m, m, size * 0.36, 0, Math.PI * 2);
    ctx.fillStyle = kleur;
    ctx.fill();
    ctx.lineWidth = size * 0.08;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
  }
  return ctx.getImageData(0, 0, size, size);
}

// ---------------------------------------------------------------- kaart

const BASEMAPS = {
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
const BRK_PERCELEN = {
  tiles: [
    "https://service.pdok.nl/kadaster/kadastralekaart/wmts/v5_0?service=WMTS&request=GetTile&version=1.0.0&layer=Kadastralekaart&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
  ],
  attribution: 'Percelen: <a href="https://www.pdok.nl/">PDOK</a> · BRK Kadaster',
  minzoom: 17,
};

const style = { version: 8, sources: {}, layers: [] };
for (const [id, cfg] of Object.entries(BASEMAPS)) {
  style.sources[`base-${id}`] = { type: "raster", tiles: cfg.tiles, tileSize: 256, minzoom: cfg.minzoom || 0, maxzoom: 19, attribution: cfg.attribution };
  style.layers.push({ id: `base-${id}`, type: "raster", source: `base-${id}`, layout: { visibility: id === "grijs" ? "visible" : "none" } });
}
style.sources["overlay-brk"] = { type: "raster", tiles: BRK_PERCELEN.tiles, tileSize: 256, minzoom: BRK_PERCELEN.minzoom, maxzoom: 19, attribution: BRK_PERCELEN.attribution };
style.layers.push({ id: "overlay-brk", type: "raster", source: "overlay-brk", layout: { visibility: "none" } });

const map = new maplibregl.Map({
  container: "map",
  style,
  center: [4.5, 52.0],
  zoom: 8.5,
  hash: true,
  // compact: op smalle schermen ingeklapt tot een (i)-knop
  attributionControl: { compact: true, customAttribution: "Inventarisatie: stichting Dodenakkers · RCE" },
});
map.addControl(new maplibregl.NavigationControl(), "top-right");
map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-right");

document.getElementById("toggle-brk").addEventListener("change", (e) =>
  map.setLayoutProperty("overlay-brk", "visibility", e.target.checked ? "visible" : "none")
);
document.querySelectorAll('input[name="basemap"]').forEach((el) =>
  el.addEventListener("change", () => {
    for (const id of Object.keys(BASEMAPS)) {
      map.setLayoutProperty(`base-${id}`, "visibility", el.value === id && el.checked ? "visible" : "none");
    }
  })
);

// ---------------------------------------------------------------- popups

const RELATIE = {
  op_terrein: "op het terrein",
  grenst_aan: "grenst aan het terrein",
  overlapt: "overlapt het terrein",
  "0-25m": "binnen 25 m",
  "25-100m": "25–100 m",
  "100-250m": "100–250 m",
};

function begraafplaatsPopup(p) {
  const st = STATUS[p.status];
  const jaartal = p.jaartal ? `${p.circa ? "ca. " : ""}${p.jaartal}` : p.jaartal_bron;
  // adres_aanduiding = Excel "NA" (nadere aanduiding): "bij" of "tegenover" het adres
  const adres = [[p.adres_aanduiding, p.adres].filter(Boolean).join(" "), p.postcode].filter(Boolean).join(", ");

  let rm = null;
  const r = p.rijksmonument_rce;
  if (r) {
    if (r.soort === "complex") {
      const onderdelen = r.onderdelen
        .map((o) => link(o.url, `${o.rijksmonumentnummer}${o.functie ? " (" + o.functie.toLowerCase() + ")" : ""}`))
        .join(", ");
      rm = raw(`complex ${esc(r.nummer)}${r.naam ? " " + esc(r.naam) : ""}: ${onderdelen}`);
    } else {
      rm = raw(link(r.url, `nr. ${r.nummer}`));
    }
  } else if (p.rijksmonument === true) {
    rm = "ja";
  }

  const eigenaar = [p.eigenaar, p.eigenaar_postadres, [p.eigenaar_postcode, p.eigenaar_plaats].filter(Boolean).join(" ")]
    .filter(Boolean)
    .join(", ");

  const gezicht = (p.gezichten || []).map((g) => `${g.naam || g.gezichtsnummer} (${g.relatie === "binnen" ? "binnen" : "deels"})`).join("; ");
  // monumenten die al onder "Rijksmonument" staan (het monument zelf of de
  // onderdelen van het complex) niet nog eens als "nabij" tonen
  const eigen = new Set(r ? [r.nummer, ...r.onderdelen.map((o) => o.rijksmonumentnummer)] : []);
  const nabij = (p.rijksmonumenten_nabij || []).filter((x) => x.afstand_m <= 100 && !eigen.has(x.rijksmonumentnummer));
  const nabijHtml = nabij.length
    ? raw(
        nabij
          .slice(0, 6)
          .map((x) => `${link(x.url, x.rijksmonumentnummer)} ${esc((x.functie || "").toLowerCase())} <span class="muted">${esc(RELATIE[x.relatie] || x.relatie)}</span>`)
          .join("<br>") + (nabij.length > 6 ? `<br><span class="muted">en nog ${nabij.length - 6}</span>` : "")
      )
    : null;

  const precisie =
    p.status === "verdwenen"
      ? '<p class="popup-note">Verdwenen: de plek is bij benadering aangegeven.</p>'
      : "";

  return `
    <h3>${esc(p.naam)}</h3>
    <p class="popup-status"><span class="sym sym-${esc(p.status)}" aria-hidden="true"></span> ${esc(st.label)} · ${esc(p.plaats || "")}</p>
    ${precisie}
    <dl>${rows([
      ["Gemeente", p.gemeente],
      ["Adres", adres],
      ["Sinds", jaartal],
      ["Grootte", p.grootte_m2 ? `${fmtInt(p.grootte_m2)} m²` : p.grootte_bron],
      ["Grondvorm", p.grondvorm],
      ["Rijksmonument", rm],
      ["Metaheerhuis", p.met === true ? raw(`${HUISJE} aanwezig`) : null],
      ["Gemeentelijk monument", p.gemeentelijk_monument === true ? "ja" : null],
      ["Monumenten Inventarisatie Project (MIP)", p.mip === true ? "opgenomen" : null],
      ["Beschermd deel", p.beschermd_deel],
      ["Eigenaar", eigenaar],
      ["Bijzonderheden", p.bijzonderheden],
      ["Beschermd gezicht", gezicht],
      ["Rijksmonumenten ≤ 100 m", nabijHtml],
      ["Laatste bezoek", p.laatste_bezoek],
      ["Kenmerk", p.id],
    ])}</dl>`;
}

function monumentPopup(p) {
  return `<h3>${p.naam ? esc(p.naam) : "Rijksmonument " + esc(p.rijksmonumentnummer)}</h3>
    <dl>${rows([
      ["Monumentnummer", raw(link(p.monumentenregister_url, p.rijksmonumentnummer))],
      ["Aard", p.monument_aard],
      ["Oorspronkelijke functie", p.oorspronkelijke_functie],
      ["Huidige functie", p.huidige_functie],
    ])}</dl>`;
}

function gezichtPopup(p) {
  return `<h3>${esc(p.naam || "Beschermd gezicht")}</h3>
    <dl>${rows([["Gezichtsnummer", p.gezichtsnummer], ["Status", "rijksbeschermd stads- of dorpsgezicht"]])}</dl>`;
}

// ---------------------------------------------------------------- lagen

const lazy = {}; // naam -> Promise (laag alleen laden als hij aangezet wordt)

function addBorders(id, fc, kleur, breedte, dash) {
  map.addSource(id, { type: "geojson", data: fc });
  map.addLayer(
    { id: `${id}-line`, type: "line", source: id, paint: { "line-color": kleur, "line-width": breedte, ...(dash ? { "line-dasharray": dash } : {}) } },
    "terreinen-fill"
  );
}

const LAZY_LAYERS = {
  gemeenten: async () => {
    addBorders("gemeenten", await loadJson(DATA.gemeenten), KLEUR.gemeente, 0.8, [3, 2]);
    return ["gemeenten-line"];
  },
  gezichten: async () => {
    map.addSource("gezichten", { type: "geojson", data: await loadRce("gezichten") });
    map.addLayer({ id: "gezichten-fill", type: "fill", source: "gezichten", paint: { "fill-color": KLEUR.gezicht, "fill-opacity": 0.12 } }, "terreinen-fill");
    map.addLayer({ id: "gezichten-line", type: "line", source: "gezichten", paint: { "line-color": KLEUR.gezicht, "line-width": 1.5, "line-dasharray": [2, 1] } }, "terreinen-fill");
    return ["gezichten-fill", "gezichten-line"];
  },
  rijksmonumenten: async () => {
    map.addSource("rm", { type: "geojson", data: await loadRce("rijksmonumenten") });
    // Boven de terreinen (de monumenten liggen er per definitie binnen 100 m
    // van, vaak óp), onder de begraafplaatssymbolen. Groot genoeg om naast
    // een begraafplaatssymbool op te vallen.
    map.addLayer({ id: "rm-fill", type: "fill", source: "rm", filter: ["==", ["geometry-type"], "Polygon"], paint: { "fill-color": KLEUR.rijksmonument, "fill-opacity": 0.45 } }, "begraafplaatsen-symbol");
    map.addLayer({
      id: "rm-point", type: "circle", source: "rm", filter: ["==", ["geometry-type"], "Point"],
      paint: {
        "circle-color": KLEUR.rijksmonument,
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 3.5, 13, 5, 17, 7],
        "circle-stroke-color": "#fff",
        "circle-stroke-width": 1.5,
      },
    }, "begraafplaatsen-symbol");
    return ["rm-fill", "rm-point"];
  },
  archeologisch: async () => {
    map.addSource("arch", { type: "geojson", data: await loadRce("archeologisch") });
    map.addLayer({ id: "arch-fill", type: "fill", source: "arch", filter: ["==", ["geometry-type"], "Polygon"], paint: { "fill-color": KLEUR.archeologisch, "fill-opacity": 0.35 } }, "begraafplaatsen-symbol");
    map.addLayer({ id: "arch-line", type: "line", source: "arch", filter: ["==", ["geometry-type"], "Polygon"], paint: { "line-color": KLEUR.archeologisch, "line-width": 1.5 } }, "begraafplaatsen-symbol");
    map.addLayer({ id: "arch-point", type: "circle", source: "arch", filter: ["==", ["geometry-type"], "Point"], paint: { "circle-color": KLEUR.archeologisch, "circle-radius": 5, "circle-stroke-color": "#fff", "circle-stroke-width": 1.5 } }, "begraafplaatsen-symbol");
    return ["arch-fill", "arch-line", "arch-point"];
  },
};
const EAGER_LAYERS = { terreinen: ["terreinen-fill", "terreinen-line"], provincies: ["provincies-line"] };

async function setLayer(name, visible) {
  let ids = EAGER_LAYERS[name];
  if (!ids) {
    if (!visible && !lazy[name]) return;
    lazy[name] = lazy[name] || LAZY_LAYERS[name]();
    try {
      ids = await lazy[name];
    } catch (err) {
      toonFout(`Kaartlaag kon niet worden geladen (${err.message}). Probeer het later opnieuw.`);
      document.querySelector(`.toggle-layer[value="${name}"]`).checked = false;
      delete lazy[name];
      return;
    }
  }
  ids.forEach((id) => map.setLayoutProperty(id, "visibility", visible ? "visible" : "none"));
}

// Aantallen per RCE-laag (uit het manifest) naast de laagnaam, zodat een lege
// laag ("0") niet voor een storing wordt aangezien.
async function toonLaagAantallen() {
  try {
    manifestPromise = manifestPromise || loadJson(DATA.rceManifest);
    const aantallen = Object.values((await manifestPromise).aantallen || {});
    for (const soort of ["gezichten", "rijksmonumenten", "archeologisch"]) {
      const el = document.querySelector(`[data-laag-count="${soort}"]`);
      if (!el || !aantallen.length) continue;
      const n = aantallen.reduce((som, a) => som + (a[soort] || 0), 0);
      el.textContent = `(${n.toLocaleString("nl-NL")})`;
    }
  } catch {
    /* aantallen zijn een extraatje; de lagen zelf melden hun fouten */
  }
}

// ---------------------------------------------------------------- filters

let alle = [];
// Datering: klikbare balkjes zoals in dodenakkers-zh (zelfde indeling, zonder
// "Middeleeuws" -- komt in deze data niet voor). Op `jaartal` uit de Excel van
// Dodenakkers; "ca." telt gewoon mee. Of deze indeling past bij Joodse
// begraafplaatsen is een open vraag aan Dodenakkers (docs/04, vraag C9).
const DATERING = [
  { id: "voor1829", label: "vóór 1829", test: (j) => j < 1829 },
  { id: "1829", label: "1829–1849", test: (j) => j >= 1829 && j < 1850 },
  { id: "1850", label: "1850–1899", test: (j) => j >= 1850 && j < 1900 },
  { id: "1900", label: "1900–1949", test: (j) => j >= 1900 && j < 1950 },
  { id: "1950", label: "1950–1999", test: (j) => j >= 1950 && j < 2000 },
  { id: "2000", label: "2000–heden", test: (j) => j >= 2000 },
];
const actieveDatering = new Set();
const dateringMatch = (p, ids = actieveDatering) =>
  ids.size === 0 || (p.jaartal != null && DATERING.some((b) => ids.has(b.id) && b.test(p.jaartal)));

function bouwDateringFilter() {
  const wrap = document.getElementById("datering-filter");
  wrap.replaceChildren(
    ...DATERING.map((b) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "histogram-row-button";
      btn.dataset.datering = b.id;
      btn.setAttribute("aria-pressed", "false");
      btn.innerHTML = `<span class="histogram-label">${esc(b.label)}</span><span class="histogram-bar-wrap"><span class="histogram-bar"></span></span><span class="histogram-count"></span>`;
      btn.addEventListener("click", () => {
        actieveDatering.has(b.id) ? actieveDatering.delete(b.id) : actieveDatering.add(b.id);
        applyFilters();
      });
      return btn;
    })
  );
}

function selectie() {
  const statussen = new Set([...document.querySelectorAll(".filter-status:checked")].map((el) => el.value));
  const q = document.getElementById("search").value.trim().toLowerCase();
  const alleenRm = document.getElementById("filter-rijksmonument").checked;
  const alleenGezicht = document.getElementById("filter-gezicht").checked;
  const zoek = (p) => !q || [p.naam, p.plaats, p.gemeente, p.label_punt].some((v) => v && v.toLowerCase().includes(q));
  // zonderDatering: alle filters behalve datering (voor de balkjestellingen)
  const zonderDatering = (p) => zoek(p) && (!alleenRm || p.rijksmonument === true) && (!alleenGezicht || !!p.in_gezicht);
  const basis = (p) => zonderDatering(p) && dateringMatch(p);
  return { statussen, basis, zonderDatering, match: (p) => statussen.has(p.status) && basis(p) };
}

function applyFilters() {
  const { statussen, basis, zonderDatering, match } = selectie();
  const ids = alle.filter((f) => match(f.properties)).map((f) => f.properties.id);
  const filter = ["in", ["get", "id"], ["literal", ids]];
  map.setFilter("begraafplaatsen-symbol", filter);
  map.setFilter("terreinen-fill", filter);
  map.setFilter("terreinen-line", filter);

  // tellingen: per status binnen de overige filters (facet)
  for (const s of Object.keys(STATUS)) {
    const n = alle.filter((f) => f.properties.status === s && basis(f.properties)).length;
    document.querySelector(`[data-count="${s}"]`).textContent = `(${n})`;
  }
  const inStatus = (p) => statussen.has(p.status);
  document.querySelector('[data-count="rijksmonument"]').textContent =
    `(${alle.filter((f) => inStatus(f.properties) && f.properties.rijksmonument === true).length})`;
  document.querySelector('[data-count="gezicht"]').textContent =
    `(${alle.filter((f) => inStatus(f.properties) && f.properties.in_gezicht).length})`;
  // Datering-balkjes: per balk het aantal als je die balk (ook) aanklikt
  const inStatusEnRest = alle.map((f) => f.properties).filter((p) => statussen.has(p.status) && zonderDatering(p));
  const tellingen = DATERING.map((b) => {
    const hyp = new Set(actieveDatering).add(b.id);
    return inStatusEnRest.filter((p) => dateringMatch(p, hyp)).length;
  });
  const max = Math.max(1, ...tellingen);
  DATERING.forEach((b, i) => {
    const btn = document.querySelector(`[data-datering="${b.id}"]`);
    btn.querySelector(".histogram-bar").style.width = `${Math.round((tellingen[i] / max) * 100)}%`;
    btn.querySelector(".histogram-count").textContent = tellingen[i];
    btn.setAttribute("aria-pressed", String(actieveDatering.has(b.id)));
    btn.setAttribute("aria-label", `${b.label}: ${tellingen[i]} begraafplaatsen${actieveDatering.has(b.id) ? ", geselecteerd" : ""}`);
  });
  const getoond = alle.filter((f) => match(f.properties));
  document.getElementById("datering-summary").textContent =
    `${getoond.filter((f) => f.properties.jaartal != null).length} van ${getoond.length} getoonde begraafplaatsen hebben een jaartal.` +
    (actieveDatering.size ? " Klik nogmaals op een balk om hem uit te zetten." : "");

  document.getElementById("search-count").textContent = ids.length
    ? `${ids.length} van ${alle.length} begraafplaatsen getoond.`
    : "Geen begraafplaatsen gevonden. Pas de zoekterm of de filters aan.";
  document.getElementById("lijst-leeg").hidden = ids.length > 0;
  renderLijst(alle.filter((f) => match(f.properties)));
}

function renderLijst(features) {
  const ol = document.getElementById("resultatenlijst");
  ol.replaceChildren(
    ...features.map((f) => {
      const p = f.properties;
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lijst-item";
      btn.innerHTML = `<span class="sym sym-${esc(p.status)}" aria-hidden="true"></span> <span>${esc(p.naam)}${p.met === true ? ` <span class="muted" title="met metaheerhuis">${HUISJE}</span>` : ""}<br><span class="muted">${esc(p.plaats || "")} · ${esc(STATUS[p.status].label.toLowerCase())}</span></span>`;
      btn.addEventListener("click", () => openBegraafplaats(f, true));
      li.append(btn);
      return li;
    })
  );
}

let popup = null;
function openBegraafplaats(feature, vliegen) {
  const p = feature.properties;
  const lngLat = feature.geometry.coordinates;
  // Op smalle schermen het punt lager in beeld, zodat de popup erboven niet
  // onder de mini-legenda valt.
  if (vliegen) map.flyTo({ center: lngLat, zoom: Math.max(map.getZoom(), 16), offset: IS_SMAL() ? [0, 160] : [0, 80] });
  popup?.remove();
  popup = new maplibregl.Popup({ maxWidth: "340px", focusAfterOpen: true }).setLngLat(lngLat).setHTML(begraafplaatsPopup(p)).addTo(map);
  if (EMBED || IS_SMAL()) {
    panelOpen = false;
    updatePanelToggle();
  }
}

// ---------------------------------------------------------------- start

async function main() {
  const [begraafplaatsen, terreinen, provincies] = await Promise.all([
    loadJson(DATA.begraafplaatsen),
    loadJson(DATA.terreinen),
    loadJson(DATA.provincies),
  ]);
  alle = begraafplaatsen.features;
  const byId = new Map(alle.map((f) => [f.properties.id, f]));

  const provs = [...new Set(alle.map((f) => f.properties.provincie))].sort();
  // Alleen "Nederland" als alle 12 provincies erin zitten; anders eerlijk het aantal.
  const scopeEl = document.getElementById("scope-label");
  scopeEl.textContent = provs.length === 12 ? "Nederland" : provs.length > 3 ? `${provs.length} van 12 provincies` : provs.join(", ");
  scopeEl.title = provs.join(", ");

  for (const [s, cfg] of Object.entries(STATUS)) map.addImage(`sym-${s}`, makeSymbol(cfg.vorm, cfg.kleur), { pixelRatio: 2 });

  const statusKleur = ["match", ["get", "status"], ...Object.entries(STATUS).flatMap(([s, c]) => [s, c.kleur]), "#000"];
  map.addSource("terreinen", { type: "geojson", data: terreinen });
  map.addLayer({ id: "terreinen-fill", type: "fill", source: "terreinen", paint: { "fill-color": statusKleur, "fill-opacity": 0.35 } });
  map.addLayer({ id: "terreinen-line", type: "line", source: "terreinen", paint: { "line-color": statusKleur, "line-width": ["interpolate", ["linear"], ["zoom"], 12, 1, 17, 2.5] } });
  addBorders("provincies", provincies, KLEUR.provincie, 1.6, null);

  map.addSource("begraafplaatsen", { type: "geojson", data: begraafplaatsen });
  map.addLayer({
    id: "begraafplaatsen-symbol",
    type: "symbol",
    source: "begraafplaatsen",
    layout: {
      "icon-image": ["concat", "sym-", ["get", "status"]],
      "icon-size": ["interpolate", ["linear"], ["zoom"], 7, 0.7, 12, 0.95, 16, 1.15],
      "icon-allow-overlap": true,
      "icon-ignore-placement": true,
      // bestaand bovenop, verdwenen onderop
      "symbol-sort-key": ["match", ["get", "status"], "in_gebruik", 3, "geruimd", 2, 1],
      // Geen tekstlabels: die vereisen een externe glyph-server (CSP). Namen
      // staan in de lijst en de popup.
    },
  });

  map.on("click", (e) => {
    const hit = map.queryRenderedFeatures(e.point, { layers: ["begraafplaatsen-symbol", "terreinen-fill"] })[0];
    if (hit) {
      const f = byId.get(hit.properties.id);
      if (f) return openBegraafplaats(f, false);
    }
    const ctx = map.queryRenderedFeatures(e.point).find((x) => ["rm", "arch", "gezichten"].includes(x.source));
    if (!ctx) return;
    popup?.remove();
    popup = new maplibregl.Popup({ maxWidth: "320px" })
      .setLngLat(e.lngLat)
      .setHTML(ctx.source === "gezichten" ? gezichtPopup(ctx.properties) : monumentPopup(ctx.properties))
      .addTo(map);
  });
  const hoverLayers = ["begraafplaatsen-symbol", "terreinen-fill"];
  hoverLayers.forEach((l) => {
    map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", l, () => (map.getCanvas().style.cursor = ""));
  });

  document.querySelectorAll(".filter-status, #filter-rijksmonument, #filter-gezicht").forEach((el) => el.addEventListener("change", applyFilters));
  document.getElementById("search").addEventListener("input", applyFilters);
  document.querySelectorAll(".toggle-layer").forEach((el) => {
    el.addEventListener("change", () => setLayer(el.value, el.checked));
    if (el.checked && LAZY_LAYERS[el.value]) setLayer(el.value, true);
  });

  toonLaagAantallen();
  bouwDateringFilter();
  applyFilters();
  // MapLibre toont de compacte bronvermelding eerst uitgeklapt; op smalle
  // schermen direct inklappen tot het (i)-knopje.
  if (IS_SMAL()) {
    map.once("idle", () => document.querySelector(".maplibregl-ctrl-attrib")?.classList.remove("maplibregl-compact-show"));
  }
  if (!START_HASH) map.fitBounds(boundsOf(begraafplaatsen), { padding: IS_SMAL() ? 24 : 60, maxZoom: 12, duration: 0 });
  statusEl.textContent = "";
}

map.on("load", () =>
  main().catch((err) => {
    console.error(err);
    toonFout(`De kaartgegevens konden niet worden geladen (${err.message}). Controleer de verbinding en herlaad de pagina.`);
  })
);
