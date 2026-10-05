// Kaartlagen: grenzen, RCE-contextlagen en herbegravingen. De contextlagen
// worden pas geladen als ze aangezet worden.

import { DATA, KLEUR } from "./config.js";
import { loadJson } from "./gedeeld.js";
import { toonFout } from "./paneel.js";

let map = null;
let manifestPromise = null;
const lazy = {}; // naam -> Promise (laag alleen laden als hij aangezet wordt)

export function initLagen(kaart) {
  map = kaart;
}

function manifest() {
  manifestPromise = manifestPromise || loadJson(DATA.rceManifest);
  return manifestPromise;
}

// RCE-lagen staan per provincie in aparte bestanden (zie data/rce/index.json).
async function loadRce(soort) {
  const provincies = (await manifest()).provincies;
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

// Pijlpunt naar rechts (= richting van de lijn), met witte rand voor contrast.
function maakPijl(kleur, size = 28) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  ctx.beginPath();
  ctx.moveTo(size * 0.25, size * 0.2);
  ctx.lineTo(size * 0.8, size * 0.5);
  ctx.lineTo(size * 0.25, size * 0.8);
  ctx.closePath();
  ctx.lineJoin = "round";
  ctx.lineWidth = size * 0.12;
  ctx.strokeStyle = "#fff";
  ctx.stroke();
  ctx.fillStyle = kleur;
  ctx.fill();
  return ctx.getImageData(0, 0, size, size);
}

export function addBorders(id, fc, kleur, breedte, dash) {
  map.addSource(id, { type: "geojson", data: fc });
  map.addLayer(
    { id: `${id}-line`, type: "line", source: id, paint: { "line-color": kleur, "line-width": breedte, ...(dash ? { "line-dasharray": dash } : {}) } },
    "terreinen-fill"
  );
}

export const LAZY_LAYERS = {
  gemeenten: async () => {
    addBorders("gemeenten", await loadJson(DATA.gemeenten), KLEUR.gemeente, 0.8, [3, 2]);
    return ["gemeenten-line"];
  },
  gezichten: async () => {
    map.addSource("gezichten", { type: "geojson", data: await loadRce("gezichten") });
    // Vlak onzichtbaar (alleen om op te kunnen klikken); de rand draagt het beeld.
    map.addLayer({ id: "gezichten-fill", type: "fill", source: "gezichten", paint: { "fill-color": KLEUR.gezicht, "fill-opacity": 0 } }, "terreinen-fill");
    map.addLayer({ id: "gezichten-line", type: "line", source: "gezichten", paint: { "line-color": KLEUR.gezicht, "line-width": 2.5, "line-dasharray": [2, 1] } }, "terreinen-fill");
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
  herbegravingen: async () => {
    map.addSource("herbegravingen", { type: "geojson", data: await loadJson(DATA.herbegravingen) });
    map.addLayer({
      id: "herbegravingen-line", type: "line", source: "herbegravingen",
      layout: { "line-cap": "round" },
      paint: { "line-color": KLEUR.herbegraving, "line-width": 2.5, "line-dasharray": [1, 2] },
    }, "begraafplaatsen-symbol");
    // Pijlen langs de lijn in de richting van de lijn (van -> naar, zie
    // analyse_spatial.py): van de oude naar de nieuwe plek.
    if (!map.hasImage("pijl")) map.addImage("pijl", maakPijl(KLEUR.herbegraving), { pixelRatio: 2 });
    map.addLayer({
      id: "herbegravingen-pijl", type: "symbol", source: "herbegravingen",
      layout: {
        "symbol-placement": "line",
        "symbol-spacing": 70,
        "icon-image": "pijl",
        "icon-rotation-alignment": "map",
        "icon-allow-overlap": true,
        "icon-ignore-placement": true,
      },
    }, "begraafplaatsen-symbol");
    return ["herbegravingen-line", "herbegravingen-pijl"];
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

export async function setLayer(name, visible) {
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
export async function toonLaagAantallen() {
  try {
    const aantallen = Object.values((await manifest()).aantallen || {});
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
