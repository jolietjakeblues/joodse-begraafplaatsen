// Oude kaarten bij een begraafplaats (oude-kaarten.html?id=jb-loc-1).
//
// Welke kaarten er over een begraafplaats liggen staat vooraf berekend in
// data/generated/oude_kaarten.json (scripts/fetch_allmaps.py). Het kaartbeeld
// komt als tegels van de Allmaps Tile Server: die vervormt de scan van de
// collectie (IIIF) naar de juiste plek. Geen extra bibliotheek nodig.
//
// URL-parameters
//   ?id=jb-loc-1   de begraafplaats (verplicht)
//   &kaart=<id>    een bepaalde oude kaart (Allmaps map-id); anders de eerste

import { BASEMAPS, DATA, STATUS } from "./config.js";
import { el, loadJson } from "./gedeeld.js";
import { makeSymbol } from "./symbolen.js";

const params = new URLSearchParams(location.search);
const ID = params.get("id");
const statusEl = document.getElementById("status");
const keuzeEl = document.getElementById("ok-keuze");
const bronEl = document.getElementById("ok-bron");
const dekkingEl = document.getElementById("ok-dekking");

const tegels = (kaart) => `https://allmaps.xyz/maps/${encodeURIComponent(kaart)}/{z}/{x}/{y}.png`;
const viewerUrl = (kaart) => `https://viewer.allmaps.org/?url=${encodeURIComponent(`https://annotations.allmaps.org/maps/${kaart}`)}`;

function maakStijl() {
  const style = { version: 8, sources: {}, layers: [] };
  for (const id of ["grijs", "luchtfoto"]) {
    const cfg = BASEMAPS[id];
    style.sources[`base-${id}`] = { type: "raster", tiles: cfg.tiles, tileSize: 256, maxzoom: 19, attribution: cfg.attribution };
    style.layers.push({ id: `base-${id}`, type: "raster", source: `base-${id}`, layout: { visibility: id === "grijs" ? "visible" : "none" } });
  }
  return style;
}

function toonKaart(map, kaart, info) {
  if (map.getLayer("oud")) map.removeLayer("oud");
  if (map.getSource("oud")) map.removeSource("oud");
  map.addSource("oud", {
    type: "raster",
    tiles: [tegels(kaart)],
    tileSize: 256,
    // De tile server rekent elke tegel uit; boven zoom 18 vergroten we zelf.
    maxzoom: 18,
    attribution: `Oude kaart: ${info.collectie} · <a href="https://allmaps.org/">Allmaps</a>`,
  });
  map.addLayer({ id: "oud", type: "raster", source: "oud", paint: { "raster-opacity": dekkingEl.value / 100, "raster-fade-duration": 0 } }, "terrein-line");
  bronEl.replaceChildren(
    `${info.collectie}${info.jaar ? ` · ${info.jaar}` : ""} · `,
    el("a", { href: viewerUrl(kaart), target: "_blank", rel: "noopener", text: "hele kaart in Allmaps" })
  );
  const url = new URL(location.href);
  url.searchParams.set("kaart", kaart);
  history.replaceState(null, "", url);
}

async function main() {
  if (!ID) throw new Error("Geen begraafplaats gekozen.");
  const [punten, terreinen, oud] = await Promise.all([
    loadJson(DATA.begraafplaatsen),
    loadJson(DATA.terreinen),
    loadJson(DATA.oudeKaarten),
  ]);
  const f = punten.features.find((x) => x.properties.id === ID);
  if (!f) throw new Error(`Onbekende begraafplaats: ${ID}`);
  const p = f.properties;
  const lijst = oud.per_begraafplaats[ID] || [];

  document.title = `Oude kaarten: ${p.naam}, ${p.plaats || ""} – Joodse Begraafplaatsen`;
  document.getElementById("ok-naam").textContent = `${p.naam}, ${p.plaats || ""} (${STATUS[p.status].label.toLowerCase()})`;
  document.getElementById("ok-verdwenen").hidden = p.status !== "verdwenen";
  document.getElementById("ok-terug").href = `begraafplaats/${encodeURIComponent(ID)}`;
  document.getElementById("ok-kaartlink").href = `./?id=${encodeURIComponent(ID)}`;

  for (const k of lijst) {
    const info = oud.kaarten[k];
    keuzeEl.append(el("option", { value: k, text: `${info.jaar ? info.jaar + " · " : ""}${info.titel}` }));
  }
  const gekozen = lijst.includes(params.get("kaart")) ? params.get("kaart") : lijst[0];
  if (gekozen) keuzeEl.value = gekozen;
  keuzeEl.disabled = !lijst.length;

  const map = new maplibregl.Map({
    container: "map",
    style: maakStijl(),
    center: f.geometry.coordinates,
    zoom: 15.5,
    maxPitch: 0,
    attributionControl: { compact: true, customAttribution: "Inventarisatie: stichting Dodenakkers" },
  });
  map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-right");
  await new Promise((r) => map.on("load", r));
  // Zoals op de hoofdkaart: op smalle schermen de bronvermelding inklappen.
  if (matchMedia("(max-width: 700px)").matches) {
    map.once("idle", () => document.querySelector(".maplibregl-ctrl-attrib")?.classList.remove("maplibregl-compact-show"));
  }

  const st = STATUS[p.status];
  map.addImage(`sym-${p.status}`, makeSymbol(st.vorm, st.kleur, st.rand), { pixelRatio: 2 });
  const terrein = { type: "FeatureCollection", features: terreinen.features.filter((t) => t.properties.id === ID) };
  map.addSource("terrein", { type: "geojson", data: terrein });
  map.addLayer({ id: "terrein-line", type: "line", source: "terrein", paint: { "line-color": "#fff", "line-width": 4 } });
  map.addLayer({ id: "terrein-line2", type: "line", source: "terrein", paint: { "line-color": st.rand || st.kleur, "line-width": 2 } });
  map.addSource("punt", { type: "geojson", data: f });
  map.addLayer({ id: "punt", type: "symbol", source: "punt", layout: { "icon-image": `sym-${p.status}`, "icon-allow-overlap": true } });

  if (gekozen) toonKaart(map, gekozen, oud.kaarten[gekozen]);
  keuzeEl.addEventListener("change", () => toonKaart(map, keuzeEl.value, oud.kaarten[keuzeEl.value]));
  dekkingEl.addEventListener("input", () => {
    dekkingEl.setAttribute("aria-valuetext", `${dekkingEl.value} procent zichtbaar`);
    if (map.getLayer("oud")) map.setPaintProperty("oud", "raster-opacity", dekkingEl.value / 100);
  });
  document.querySelectorAll('input[name="basemap"]').forEach((r) =>
    r.addEventListener("change", () => {
      for (const id of ["grijs", "luchtfoto"]) map.setLayoutProperty(`base-${id}`, "visibility", r.value === id && r.checked ? "visible" : "none");
    })
  );
  statusEl.textContent = lijst.length
    ? `${lijst.length} oude ${lijst.length === 1 ? "kaart" : "kaarten"} over deze plek. Tegels kunnen een paar seconden laden.`
    : "Voor deze plek zijn (nog) geen oude kaarten gevonden.";
}

main().catch((e) => {
  statusEl.textContent = e.message;
  statusEl.classList.add("fout");
});
