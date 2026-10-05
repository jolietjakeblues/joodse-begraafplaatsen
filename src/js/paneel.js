// Bedieningspaneel, mini-legenda, springlink en foutmeldingen.
//
// URL-parameters
//   ?embed=1     compacte weergave voor inbedden (paneel standaard dicht)
//   ?id=...      opent die begraafplaats (zie app.js)

export const params = new URLSearchParams(location.search);
// Vastleggen voordat MapLibre (hash: true) zelf een positie in de URL zet.
export const START_HASH = location.hash;
export const EMBED = params.get("embed") === "1";
export const IS_SMAL = () => window.matchMedia("(max-width: 700px)").matches;

document.body.classList.toggle("embed", EMBED);

const statusEl = document.getElementById("status");
const panelEl = document.getElementById("panel");
export const panelToggleEl = document.getElementById("panel-toggle");
const miniLegendaEl = document.getElementById("mini-legenda");

let panelOpen = !(EMBED || IS_SMAL());

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

function openPaneelEnFocus() {
  panelOpen = true;
  updatePanelToggle();
  panelEl.focus();
}

/** Paneel dichtklappen (na het openen van een popup op mobiel of in embed). */
export function sluitPaneel() {
  panelOpen = false;
  updatePanelToggle();
}

/** Foutmelding in het paneel én in de mini-legenda (anders onzichtbaar bij dicht paneel). */
export function toonFout(tekst) {
  statusEl.textContent = tekst;
  document.getElementById("mini-fout").textContent = tekst;
}

/** Statusregel ("Data laden…") leegmaken. */
export function wisStatus() {
  statusEl.textContent = "";
}

panelToggleEl.addEventListener("click", () => {
  panelOpen = !panelOpen;
  updatePanelToggle();
});
miniLegendaEl.addEventListener("click", openPaneelEnFocus);
// Springlink "Ga naar het bedieningspaneel": bij een dicht paneel (mobiel, embed)
// is #panel inert en niet focusbaar, dus eerst openen. preventDefault houdt
// #panel uit de URL; die is van de kaartpositie (MapLibre hash).
document.querySelector(".skip-link").addEventListener("click", (e) => {
  e.preventDefault();
  openPaneelEnFocus();
});
updatePanelToggle();
if (EMBED) {
  document.getElementById("open-volledig").href = "./" + location.hash;
}
