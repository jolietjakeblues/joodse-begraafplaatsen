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
  gezichten: "data/rce/beschermde-gezichten.geojson",
  rijksmonumenten: "data/rce/rijksmonumenten.geojson",
  archeologisch: "data/rce/archeologische-rijksmonumenten.geojson",
};

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
  rijksmonument: "#6f6f6f",
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
function updatePanelToggle() {
  panelEl.classList.toggle("collapsed", !panelOpen);
  panelToggleEl.textContent = panelOpen ? "×" : "☰";
  panelToggleEl.setAttribute("aria-label", panelOpen ? "Paneel sluiten" : "Paneel openen");
  panelToggleEl.setAttribute("aria-expanded", String(panelOpen));
}
panelToggleEl.addEventListener("click", () => {
  panelOpen = !panelOpen;
  updatePanelToggle();
});
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
};

const style = { version: 8, sources: {}, layers: [] };
for (const [id, cfg] of Object.entries(BASEMAPS)) {
  style.sources[`base-${id}`] = { type: "raster", tiles: cfg.tiles, tileSize: 256, maxzoom: 19, attribution: cfg.attribution };
  style.layers.push({ id: `base-${id}`, type: "raster", source: `base-${id}`, layout: { visibility: id === "grijs" ? "visible" : "none" } });
}

const map = new maplibregl.Map({
  container: "map",
  style,
  center: [4.5, 52.0],
  zoom: 8.5,
  hash: true,
  attributionControl: { customAttribution: "Inventarisatie: stichting Dodenakkers · RCE" },
});
map.addControl(new maplibregl.NavigationControl(), "top-right");
map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-right");

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
  const adres = [p.adres_aanduiding, p.adres, p.postcode].filter(Boolean).join(" ");

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
      ["Gemeentelijk monument", p.gemeentelijk_monument === true ? "ja" : null],
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
    map.addSource("gezichten", { type: "geojson", data: await loadJson(DATA.gezichten) });
    map.addLayer({ id: "gezichten-fill", type: "fill", source: "gezichten", paint: { "fill-color": KLEUR.gezicht, "fill-opacity": 0.12 } }, "terreinen-fill");
    map.addLayer({ id: "gezichten-line", type: "line", source: "gezichten", paint: { "line-color": KLEUR.gezicht, "line-width": 1.5, "line-dasharray": [2, 1] } }, "terreinen-fill");
    return ["gezichten-fill", "gezichten-line"];
  },
  rijksmonumenten: async () => {
    statusEl.textContent = "Rijksmonumenten laden…";
    map.addSource("rm", { type: "geojson", data: await loadJson(DATA.rijksmonumenten) });
    map.addLayer({ id: "rm-fill", type: "fill", source: "rm", filter: ["==", ["geometry-type"], "Polygon"], minzoom: 12, paint: { "fill-color": KLEUR.rijksmonument, "fill-opacity": 0.3 } }, "terreinen-fill");
    map.addLayer({
      id: "rm-point", type: "circle", source: "rm", filter: ["==", ["geometry-type"], "Point"], minzoom: 11,
      paint: { "circle-color": KLEUR.rijksmonument, "circle-radius": ["interpolate", ["linear"], ["zoom"], 11, 1.5, 16, 4], "circle-stroke-color": "#fff", "circle-stroke-width": 0.5 },
    }, "begraafplaatsen-symbol");
    statusEl.textContent = "";
    return ["rm-fill", "rm-point"];
  },
  archeologisch: async () => {
    map.addSource("arch", { type: "geojson", data: await loadJson(DATA.archeologisch) });
    map.addLayer({ id: "arch-fill", type: "fill", source: "arch", filter: ["==", ["geometry-type"], "Polygon"], paint: { "fill-color": KLEUR.archeologisch, "fill-opacity": 0.25 } }, "terreinen-fill");
    map.addLayer({ id: "arch-line", type: "line", source: "arch", filter: ["==", ["geometry-type"], "Polygon"], paint: { "line-color": KLEUR.archeologisch, "line-width": 1 } }, "terreinen-fill");
    map.addLayer({ id: "arch-point", type: "circle", source: "arch", filter: ["==", ["geometry-type"], "Point"], paint: { "circle-color": KLEUR.archeologisch, "circle-radius": 4, "circle-stroke-color": "#fff", "circle-stroke-width": 1 } }, "begraafplaatsen-symbol");
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
      statusEl.textContent = `Laag kon niet laden: ${err.message}`;
      delete lazy[name];
      return;
    }
  }
  ids.forEach((id) => map.setLayoutProperty(id, "visibility", visible ? "visible" : "none"));
}

// ---------------------------------------------------------------- filters

let alle = [];
function selectie() {
  const statussen = new Set([...document.querySelectorAll(".filter-status:checked")].map((el) => el.value));
  const q = document.getElementById("search").value.trim().toLowerCase();
  const alleenRm = document.getElementById("filter-rijksmonument").checked;
  const alleenGezicht = document.getElementById("filter-gezicht").checked;
  const zoek = (p) => !q || [p.naam, p.plaats, p.gemeente, p.label_punt].some((v) => v && v.toLowerCase().includes(q));
  const basis = (p) => zoek(p) && (!alleenRm || p.rijksmonument === true) && (!alleenGezicht || !!p.in_gezicht);
  return { statussen, basis, match: (p) => statussen.has(p.status) && basis(p) };
}

function applyFilters() {
  const { statussen, basis, match } = selectie();
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
  document.getElementById("search-count").textContent = `${ids.length} van ${alle.length} begraafplaatsen getoond.`;
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
      btn.innerHTML = `<span class="sym sym-${esc(p.status)}" aria-hidden="true"></span> <span>${esc(p.naam)}<br><span class="muted">${esc(p.plaats || "")} · ${esc(STATUS[p.status].label.toLowerCase())}</span></span>`;
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
  if (vliegen) map.flyTo({ center: lngLat, zoom: Math.max(map.getZoom(), 16) });
  popup?.remove();
  popup = new maplibregl.Popup({ maxWidth: "340px", focusAfterOpen: true }).setLngLat(lngLat).setHTML(begraafplaatsPopup(p)).addTo(map);
  if (EMBED || window.matchMedia("(max-width: 700px)").matches) {
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
  document.getElementById("scope-label").textContent = provs.length > 3 ? "Nederland" : provs.join(", ");

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

  applyFilters();
  if (!START_HASH) map.fitBounds(boundsOf(begraafplaatsen), { padding: 60, maxZoom: 12, duration: 0 });
  statusEl.textContent = "";
}

map.on("load", () =>
  main().catch((err) => {
    console.error(err);
    statusEl.textContent = `Laden mislukt: ${err.message}`;
  })
);
