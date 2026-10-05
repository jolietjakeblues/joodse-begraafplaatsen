// De MapLibre-kaart met ondergronden (PDOK) en de knoppen daarvoor.
// maplibregl is een globale variabele uit vendor/maplibre-gl/maplibre-gl.js.

import { BASEMAPS, BRK_PERCELEN } from "./config.js";

function maakStijl() {
  const style = { version: 8, sources: {}, layers: [] };
  for (const [id, cfg] of Object.entries(BASEMAPS)) {
    style.sources[`base-${id}`] = { type: "raster", tiles: cfg.tiles, tileSize: 256, minzoom: cfg.minzoom || 0, maxzoom: 19, attribution: cfg.attribution };
    style.layers.push({ id: `base-${id}`, type: "raster", source: `base-${id}`, layout: { visibility: id === "grijs" ? "visible" : "none" } });
  }
  style.sources["overlay-brk"] = { type: "raster", tiles: BRK_PERCELEN.tiles, tileSize: 256, minzoom: BRK_PERCELEN.minzoom, maxzoom: 19, attribution: BRK_PERCELEN.attribution };
  style.layers.push({ id: "overlay-brk", type: "raster", source: "overlay-brk", layout: { visibility: "none" } });
  return style;
}

export function maakKaart() {
  const map = new maplibregl.Map({
    container: "map",
    style: maakStijl(),
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
  return map;
}

/** Omhullende van alle coördinaten in een FeatureCollection. */
export function boundsOf(fc) {
  const b = new maplibregl.LngLatBounds();
  const ext = (c) => (typeof c[0] === "number" ? b.extend(c) : c.forEach(ext));
  fc.features.forEach((f) => ext(f.geometry.coordinates));
  return b;
}
