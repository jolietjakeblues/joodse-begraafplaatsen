// Joodse Begraafplaatsen - kaartviewer (startpunt).
//
// Statisch: laadt vooraf berekende GeoJSON (scripts/*.py), geen live SPARQL.
// Alle paden zijn relatief, zodat de map site/ ook in een submap of via een
// <iframe> op een andere website (bv. dodenakkers.nl) kan draaien.
// ES-modules zonder build-stap; maplibregl is een globale variabele.
//
// URL-parameters
//   ?embed=1       compacte weergave voor inbedden (paneel standaard dicht)
//   ?id=jb-loc-1   opent die begraafplaats
//   ?provincie=X   toont alleen die provincie en zoomt erop in
//   ?debug=1       zet window.kaartDebug (map, alle, openBegraafplaats) voor tests
//   #zoom/lat/lon  kaartpositie (MapLibre hash), deelbaar

import { DATA, KLEUR, STATUS } from "./config.js";
import { applyFilters, initFilters, zoomNaarSelectie } from "./filters.js";
import { loadJson } from "./gedeeld.js";
import { boundsOf, maakKaart } from "./kaart.js";
import { addBorders, initLagen, LAZY_LAYERS, setLayer, toonLaagAantallen } from "./lagen.js";
import { EMBED, IS_SMAL, params, panelToggleEl, sluitPaneel, START_HASH, toonFout, wisStatus } from "./paneel.js";
import { artikelenPerId, begraafplaatsPopup, gezichtPopup, monumentPopup, paginaPad } from "./popups.js";
import { makeSymbol } from "./symbolen.js";

const map = maakKaart();
initLagen(map);

// De data meteen ophalen, tegelijk met het opbouwen van de kaart: niet wachten
// tot de ondergrond (PDOK-tegels) geladen is (review 2026-10-05).
const KERNDATA = Promise.all([loadJson(DATA.begraafplaatsen), loadJson(DATA.terreinen), loadJson(DATA.provincies)]);
const LEESLIJST = loadJson(DATA.leeslijst);
KERNDATA.catch(() => {}); // fout wordt in main() gemeld
LEESLIJST.catch(() => {});

let alle = [];
let popup = null;

function openBegraafplaats(feature, vliegen) {
  const p = feature.properties;
  const lngLat = feature.geometry.coordinates;
  // Op smalle schermen het punt lager in beeld, zodat de popup erboven niet
  // onder de mini-legenda valt.
  if (vliegen) map.flyTo({ center: lngLat, zoom: Math.max(map.getZoom(), 16), offset: IS_SMAL() ? [0, 160] : [0, 80] });
  // Waar stond de focus (bv. een lijstitem)? Na sluiten van de popup gaat hij
  // daarheen terug (WCAG 2.4.3, review 2026-10-05).
  const terug = document.activeElement instanceof HTMLElement && !map.getContainer().contains(document.activeElement)
    ? document.activeElement
    : null;
  popup?.remove();
  const deze = new maplibregl.Popup({ maxWidth: "340px", focusAfterOpen: true }).setLngLat(lngLat).setHTML(begraafplaatsPopup(p)).addTo(map);
  popup = deze;
  const popupEl = deze.getElement();
  deze.on("close", () => {
    // Alleen terugzetten als de focus in deze popup stond (sluitknop) of al
    // verloren is; niet als intussen iets anders de focus heeft.
    const actief = document.activeElement;
    if (actief && actief !== document.body && !popupEl.contains(actief)) return;
    const doel = terug && terug.isConnected && !terug.closest("[inert]") ? terug : panelToggleEl;
    doel.focus();
  });
  if (EMBED || IS_SMAL()) sluitPaneel();
}

function voegLagenToe(begraafplaatsen, terreinen, provincies) {
  for (const [s, cfg] of Object.entries(STATUS)) map.addImage(`sym-${s}`, makeSymbol(cfg.vorm, cfg.kleur, cfg.rand), { pixelRatio: 2 });

  const statusKleur = ["match", ["get", "status"], ...Object.entries(STATUS).flatMap(([s, c]) => [s, c.kleur]), "#000"];
  const randKleur = ["match", ["get", "status"], ...Object.entries(STATUS).flatMap(([s, c]) => [s, c.rand || c.kleur]), "#000"];
  map.addSource("terreinen", { type: "geojson", data: terreinen });
  map.addLayer({ id: "terreinen-fill", type: "fill", source: "terreinen", paint: { "fill-color": statusKleur, "fill-opacity": 0.35 } });
  map.addLayer({ id: "terreinen-line", type: "line", source: "terreinen", paint: { "line-color": randKleur, "line-width": ["interpolate", ["linear"], ["zoom"], 12, 1, 17, 2.5] } });
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
      // in gebruik bovenop, verdwenen onderop
      "symbol-sort-key": ["match", ["get", "status"], "in_gebruik", 3, "geruimd", 2, 1],
      // Geen tekstlabels: die vereisen een externe glyph-server (CSP). Namen
      // staan in de lijst en de popup.
    },
  });
}

// Vast adres van de begraafplaatspagina, ook vanuit ?embed=1 (zelfde site).
function kopieerLink(knop) {
  const basis = location.href.split(/[?#]/)[0];
  const url = new URL(paginaPad(knop.dataset.deelId), basis).href;
  const melding = knop.parentElement.querySelector(".deel-melding");
  navigator.clipboard
    .writeText(url)
    .then(() => {
      melding.textContent = "Link gekopieerd.";
    })
    .catch(() => {
      // Geen toegang tot het klembord: toon de link zodat hij te kopiëren is.
      melding.replaceChildren(Object.assign(document.createElement("input"), { value: url, readOnly: true, className: "deel-url", ariaLabel: "Link naar deze begraafplaats" }));
      melding.querySelector("input").select();
    });
}

function koppelKlikken(byId) {
  // Knoppen in de popup: herbegravingen openen de andere begraafplaats,
  // "Link kopiëren" zet het vaste adres van de begraafplaatspagina op het klembord.
  document.getElementById("map").addEventListener("click", (e) => {
    const knop = e.target.closest("[data-open-id]");
    const f = knop && byId.get(knop.dataset.openId);
    if (f) return openBegraafplaats(f, true);
    const deel = e.target.closest("[data-deel-id]");
    if (deel) kopieerLink(deel);
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
  for (const l of ["begraafplaatsen-symbol", "terreinen-fill"]) {
    map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", l, () => (map.getCanvas().style.cursor = ""));
  }
}

async function main() {
  const [begraafplaatsen, terreinen, provincies] = await KERNDATA;
  alle = begraafplaatsen.features;
  // Artikelen zijn een extraatje: kan de leeslijst niet laden, dan werkt de kaart gewoon.
  // Wel wachten voordat een popup via ?id= opent, anders mist die de artikelen.
  const leeslijstKlaar = LEESLIJST
    .then((ll) => {
      for (const a of ll.artikelen) {
        for (const id of a.popup_ids || []) {
          if (!artikelenPerId.has(id)) artikelenPerId.set(id, []);
          artikelenPerId.get(id).push(a);
        }
      }
    })
    .catch((err) => console.warn("leeslijst niet geladen:", err.message));
  const byId = new Map(alle.map((f) => [f.properties.id, f]));

  const provs = [...new Set(alle.map((f) => f.properties.provincie))].sort();
  // Alleen "Nederland" als alle 12 provincies erin zitten; anders eerlijk het aantal.
  const scopeEl = document.getElementById("scope-label");
  scopeEl.textContent = provs.length === 12 ? "Nederland" : provs.length > 3 ? `${provs.length} van 12 provincies` : provs.join(", ");
  scopeEl.title = provs.join(", ");

  voegLagenToe(begraafplaatsen, terreinen, provincies);
  koppelKlikken(byId);

  document.querySelectorAll(".toggle-layer").forEach((el) => {
    el.addEventListener("change", () => setLayer(el.value, el.checked));
    if (el.checked && LAZY_LAYERS[el.value]) setLayer(el.value, true);
  });
  toonLaagAantallen();
  const opProvincie = initFilters(map, alle, openBegraafplaats);

  if (params.get("debug") === "1") window.kaartDebug = { map, alle, openBegraafplaats, applyFilters };

  // MapLibre toont de compacte bronvermelding eerst uitgeklapt; op smalle
  // schermen direct inklappen tot het (i)-knopje.
  if (IS_SMAL()) {
    map.once("idle", () => document.querySelector(".maplibregl-ctrl-attrib")?.classList.remove("maplibregl-compact-show"));
  }
  // ?id=jb-loc-4200 opent direct die begraafplaats (links vanaf de leespagina, delen)
  let startId = params.get("id");
  if (startId && !byId.has(startId)) {
    // Vervallen kenmerk (bv. een oude link uit het boek): doorverwijzen.
    const naar = await loadJson(DATA.doorverwijzingen).then((d) => d[startId]).catch(() => null);
    if (naar) startId = naar;
  }
  if (startId && byId.has(startId)) {
    await leeslijstKlaar;
    const f = byId.get(startId);
    map.jumpTo({ center: f.geometry.coordinates, zoom: 16 });
    openBegraafplaats(f, false);
  } else if (opProvincie) {
    zoomNaarSelectie(); // ?provincie=Gelderland
  } else if (!START_HASH) {
    map.fitBounds(boundsOf(begraafplaatsen), { padding: IS_SMAL() ? 24 : 60, maxZoom: 12, duration: 0 });
  }
  wisStatus();
}

// Lagen toevoegen zodra de kaartstijl klaar is ("style.load"), niet pas na "load"
// (dat wacht ook op de eerste ondergrondtegels).
let gestart = false;
function start() {
  if (gestart) return;
  gestart = true;
  main().catch((err) => {
    console.error(err);
    toonFout(`De kaartgegevens konden niet worden geladen (${err.message}). Controleer de verbinding en herlaad de pagina.`);
  });
}
if (map.isStyleLoaded()) start();
else map.once("style.load", start);
map.once("load", start); // vangnet
