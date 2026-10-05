// Zoeken, provincie, statusfilters, vinkjes, datering en de lijst.

import { DATERING, STATUS, ZOEK_ALIASSEN } from "./config.js";
import { esc, zoekNorm } from "./gedeeld.js";
import { HUISJE } from "./html.js";
import { boundsOf } from "./kaart.js";
import { IS_SMAL, params } from "./paneel.js";

let map = null;
let alle = [];
let openBegraafplaats = () => {};
const actieveDatering = new Set();
// id -> genormaliseerde zoektekst (naam, oude naam, plaats, gemeente, provincie,
// puntlabel, terreinnaam uit de KMZ en het kenmerk)
const zoekTekst = new Map();
const provincieEl = () => document.getElementById("filter-provincie");

/**
 * kaart, alle features en de functie die een begraafplaats opent.
 * Geeft true terug als de kaart via ?provincie= op een provincie start.
 */
export function initFilters(kaart, features, opener) {
  map = kaart;
  alle = features;
  openBegraafplaats = opener;
  for (const f of alle) {
    const p = f.properties;
    const velden = [p.naam, p.naam_bron, p.plaats, p.gemeente, p.gemeente_bron, p.provincie, p.label_punt, p.terrein_naam_kml, p.id];
    zoekTekst.set(p.id, zoekNorm(velden.filter(Boolean).join(" ")));
  }
  bouwDateringFilter();
  const provincies = [...new Set(alle.map((f) => f.properties.provincie))].sort((a, b) => a.localeCompare(b, "nl"));
  provincieEl().append(...provincies.map((prov) => Object.assign(document.createElement("option"), { value: prov, textContent: prov })));
  const gevraagd = params.get("provincie");
  const startProvincie = provincies.find((prov) => zoekNorm(prov) === zoekNorm(gevraagd || ""));
  if (startProvincie) provincieEl().value = startProvincie;

  document.querySelectorAll(".filter-status, #filter-rijksmonument, #filter-gezicht, #filter-herbegraving").forEach((el) => el.addEventListener("change", applyFilters));
  // Filter op herbegravingen zet ook de lijnen met pijlen aan (andersom niet:
  // de laag blijft een overlay boven elke selectie).
  document.getElementById("filter-herbegraving").addEventListener("change", (e) => {
    const laag = document.querySelector('.toggle-layer[value="herbegravingen"]');
    if (e.target.checked && !laag.checked) {
      laag.checked = true;
      laag.dispatchEvent(new Event("change"));
    }
  });
  // Zoeken filtert direct; zoomen pas als het typen even stilstaat (of bij
  // Enter), anders springt de kaart bij elke letter.
  const zoekEl = document.getElementById("search");
  let zoomTimer = null;
  zoekEl.addEventListener("input", () => {
    applyFilters();
    clearTimeout(zoomTimer);
    zoomTimer = setTimeout(zoomNaarSelectie, 600);
  });
  zoekEl.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    clearTimeout(zoomTimer);
    zoomNaarSelectie();
  });
  provincieEl().addEventListener("change", () => {
    applyFilters();
    zoomNaarSelectie();
  });
  applyFilters();
  return Boolean(startProvincie);
}

/** Zoom naar de getoonde begraafplaatsen (na het kiezen van een provincie). */
export function zoomNaarSelectie() {
  const { match } = selectie();
  const getoond = alle.filter((f) => match(f.properties));
  if (!getoond.length) return;
  map.fitBounds(boundsOf({ features: getoond }), { padding: IS_SMAL() ? 24 : 60, maxZoom: 12, duration: 0 });
}

/** Zoekterm plus varianten (Den Haag -> 's-Gravenhage enz., zie ZOEK_ALIASSEN). */
function zoekVarianten(q) {
  const varianten = [q];
  for (const [van, naar] of Object.entries(ZOEK_ALIASSEN)) {
    if (` ${q} `.includes(` ${van} `)) varianten.push(` ${q} `.replace(` ${van} `, ` ${naar} `).trim());
  }
  return varianten;
}

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
  const varianten = zoekVarianten(zoekNorm(document.getElementById("search").value));
  const prov = provincieEl().value;
  const alleenRm = document.getElementById("filter-rijksmonument").checked;
  const alleenGezicht = document.getElementById("filter-gezicht").checked;
  const alleenHerbegraving = document.getElementById("filter-herbegraving").checked;
  // Een kenmerk ("jb-loc-366") moet exact matchen, anders vindt het ook jb-loc-3663.
  const kenmerk = /^jb (loc|ver|ger) \d+$/.test(varianten[0]) ? varianten[0] : null;
  const zoek = (p) =>
    !varianten[0] || (kenmerk ? zoekNorm(p.id) === kenmerk : varianten.some((v) => zoekTekst.get(p.id).includes(v)));
  const inProv = (p) => !prov || p.provincie === prov;
  const isRm = (p) => p.rijksmonument === true;
  const inGezicht = (p) => !!p.in_gezicht;
  const isHerbegraving = (p) => !!(p.herbegraven_naar?.length || p.herbegraven_van?.length);
  const vinkRm = (p) => !alleenRm || isRm(p);
  const vinkGezicht = (p) => !alleenGezicht || inGezicht(p);
  const vinkHerbegraving = (p) => !alleenHerbegraving || isHerbegraving(p);
  const vinkjes = (p) => vinkRm(p) && vinkGezicht(p) && vinkHerbegraving(p);
  // zonderDatering: alle filters behalve datering (voor de balkjestellingen)
  const zonderDatering = (p) => zoek(p) && inProv(p) && vinkjes(p);
  // voor de aantallen in de provinciekeuze: alle filters behalve de provincie
  const zonderProvincie = (p) => statussen.has(p.status) && zoek(p) && dateringMatch(p) && vinkjes(p);
  const basis = (p) => zonderDatering(p) && dateringMatch(p);
  // Facettellingen naast de vinkjes: binnen ALLE overige actieve filters (status,
  // zoekterm, datering, het andere vinkje), zodat het getal is wat je krijgt
  // als je het vinkje aanzet (review 2026-10-05).
  const overig = (p) => statussen.has(p.status) && zoek(p) && inProv(p) && dateringMatch(p);
  const telRm = (p) => overig(p) && vinkGezicht(p) && vinkHerbegraving(p) && isRm(p);
  const telGezicht = (p) => overig(p) && vinkRm(p) && vinkHerbegraving(p) && inGezicht(p);
  const telHerbegraving = (p) => overig(p) && vinkRm(p) && vinkGezicht(p) && isHerbegraving(p);
  return { statussen, basis, zonderDatering, zonderProvincie, telRm, telGezicht, telHerbegraving, match: (p) => statussen.has(p.status) && basis(p) };
}

export function applyFilters() {
  const { statussen, basis, zonderDatering, zonderProvincie, telRm, telGezicht, telHerbegraving, match } = selectie();
  const getoond = alle.filter((f) => match(f.properties));
  const ids = getoond.map((f) => f.properties.id);
  const filter = ["in", ["get", "id"], ["literal", ids]];
  map.setFilter("begraafplaatsen-symbol", filter);
  map.setFilter("terreinen-fill", filter);
  map.setFilter("terreinen-line", filter);

  // tellingen: per status binnen de overige filters (facet)
  for (const s of Object.keys(STATUS)) {
    const n = alle.filter((f) => f.properties.status === s && basis(f.properties)).length;
    document.querySelector(`[data-count="${s}"]`).textContent = `(${n})`;
  }
  document.querySelector('[data-count="rijksmonument"]').textContent = `(${alle.filter((f) => telRm(f.properties)).length})`;
  document.querySelector('[data-count="gezicht"]').textContent = `(${alle.filter((f) => telGezicht(f.properties)).length})`;
  document.querySelector('[data-count="herbegraving"]').textContent = `(${alle.filter((f) => telHerbegraving(f.properties)).length})`;
  // provinciekeuze: per provincie het aantal binnen de overige filters
  const perProv = new Map();
  for (const f of alle) if (zonderProvincie(f.properties)) perProv.set(f.properties.provincie, (perProv.get(f.properties.provincie) || 0) + 1);
  for (const opt of provincieEl().options) {
    const n = opt.value ? perProv.get(opt.value) || 0 : [...perProv.values()].reduce((a, b) => a + b, 0);
    opt.textContent = `${opt.value || "Alle provincies"} (${n})`;
  }

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
  document.getElementById("datering-summary").textContent =
    `${getoond.filter((f) => f.properties.jaartal != null).length} van ${getoond.length} getoonde begraafplaatsen hebben een jaartal.` +
    (actieveDatering.size ? " Klik nogmaals op een balk om hem uit te zetten." : "");

  document.getElementById("search-count").textContent = ids.length
    ? `${ids.length} van ${alle.length} begraafplaatsen getoond.`
    : "Geen begraafplaatsen gevonden. Pas de zoekterm of de filters aan.";
  document.getElementById("lijst-leeg").hidden = ids.length > 0;
  renderLijst(getoond);
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
