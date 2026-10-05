// HTML van de popups: begraafplaats, rijksmonument en beschermd gezicht.

import { RELATIE, REPO_URL, STATUS } from "./config.js";
import { esc, fmtInt } from "./gedeeld.js";
import { functieKort, HUISJE, link, raw, rows } from "./html.js";

/** Link naar het GitHub-correctieformulier met kenmerk en naam ingevuld. */
function correctieUrl(p) {
  const q = new URLSearchParams({
    template: "correctie.yml",
    title: `Correctie: ${p.naam}, ${p.plaats || ""}`.trim(),
    kenmerk: p.id,
    naam: [p.naam, p.plaats].filter(Boolean).join(", "),
  });
  return `${REPO_URL}/issues/new?${q}`;
}

/** Relatief pad naar de eigen pagina van een begraafplaats (scripts/build_site.py). */
export const paginaPad = (id) => `begraafplaats/${encodeURIComponent(id)}`;

// begraafplaats-id -> artikelen op dodenakkers.nl (gevuld door app.js)
export const artikelenPerId = new Map();

function artikelenHtml(id) {
  const lijst = artikelenPerId.get(id);
  if (!lijst) return null;
  return raw(lijst.map((a) => link(a.url, a.titel)).join("<br>"));
}

// Herbegravingen (data/herbegravingen.csv): knoppen openen de andere begraafplaats
// (afgehandeld in app.js via data-open-id).
function herbegravingHtml(lijst) {
  if (!lijst || !lijst.length) return null;
  return raw(
    lijst
      .map((h) => `<button type="button" class="link-knop" data-open-id="${esc(h.id)}">${esc(h.naam)}</button>, ${esc(h.plaats || "")}`)
      .join("<br>")
  );
}

function rijksmonumentHtml(p) {
  const r = p.rijksmonument_rce;
  if (r) {
    if (r.soort === "complex") {
      const onderdelen = r.onderdelen
        .map((o) => link(o.url, `${o.rijksmonumentnummer}${o.functie ? " (" + o.functie.toLowerCase() + ")" : ""}`))
        .join(", ");
      return raw(`complex ${esc(r.nummer)}${r.naam ? " " + esc(r.naam) : ""}: ${onderdelen}`);
    }
    return raw(link(r.url, `nr. ${r.nummer}`));
  }
  return p.rijksmonument === true ? "ja" : null;
}

function nabijHtml(p) {
  const r = p.rijksmonument_rce;
  // monumenten die al onder "Rijksmonument" staan (het monument zelf of de
  // onderdelen van het complex) niet nog eens als "nabij" tonen
  const eigen = new Set(r ? [r.nummer, ...r.onderdelen.map((o) => o.rijksmonumentnummer)] : []);
  const nabij = (p.rijksmonumenten_nabij || []).filter((x) => x.afstand_m <= 100 && !eigen.has(x.rijksmonumentnummer));
  if (!nabij.length) return null;
  return raw(
    nabij
      .slice(0, 6)
      .map((x) => `${link(x.url, x.rijksmonumentnummer)} ${esc((x.functie || "").toLowerCase())} <span class="muted">${esc(RELATIE[x.relatie] || x.relatie)}</span>`)
      .join("<br>") + (nabij.length > 6 ? `<br><span class="muted">en nog ${nabij.length - 6}</span>` : "")
  );
}

export function begraafplaatsPopup(p) {
  const st = STATUS[p.status];
  const jaartal = p.jaartal ? `${p.circa ? "ca. " : ""}${p.jaartal}` : p.jaartal_bron;
  // adres_aanduiding = Excel "NA" (nadere aanduiding): "bij" of "tegenover" het adres
  const adres = [[p.adres_aanduiding, p.adres].filter(Boolean).join(" "), p.postcode].filter(Boolean).join(", ");
  const gezicht = (p.gezichten || []).map((g) => `${g.naam || g.gezichtsnummer} (${g.relatie === "binnen" ? "binnen" : "deels"})`).join("; ");
  const precisie = p.status === "verdwenen" ? '<p class="popup-note">Verdwenen: de plek is bij benadering aangegeven.</p>' : "";

  return `
    <h3>${esc(p.naam)}</h3>
    <p class="popup-status"><span class="sym sym-${esc(p.status)}" aria-hidden="true"></span> ${esc(st.label)} · ${esc(p.plaats || "")}</p>
    ${precisie}
    <dl>${rows([
      ["Gemeente", p.gemeente],
      ["Adres", adres],
      ["Sinds", jaartal],
      ["Grootte", p.grootte_m2 ? `${fmtInt(p.grootte_m2)} m²` : p.grootte_bron],
      ["Rijksmonument", rijksmonumentHtml(p)],
      ["Metaheerhuis", p.met === true ? raw(`${HUISJE} aanwezig`) : null],
      ["Gemeentelijk monument", p.gemeentelijk_monument === true ? "ja" : null],
      ["Monumenten Inventarisatie Project (MIP)", p.mip === true ? "opgenomen" : null],
      ["Beschermd deel", p.beschermd_deel],
      ["Bijzonderheden", p.bijzonderheden],
      ["Overgebracht naar", herbegravingHtml(p.herbegraven_naar)],
      ["Herbegraven vanuit", herbegravingHtml(p.herbegraven_van)],
      ["Lees op Dodenakkers", artikelenHtml(p.id)],
      ["Beschermd gezicht", gezicht],
      ["Rijksmonumenten ≤ 100 m", nabijHtml(p)],
      ["Kenmerk", p.id],
    ])}</dl>
    <p class="popup-acties">
      <a href="${esc(paginaPad(p.id))}">Meer over deze begraafplaats</a>
      <span aria-hidden="true">·</span>
      <button type="button" class="link-knop" data-deel-id="${esc(p.id)}">Link kopiëren</button>
      <span class="deel-melding" role="status" aria-live="polite"></span>
    </p>
    <p class="popup-correctie"><a href="${esc(correctieUrl(p))}" target="_blank" rel="noopener">Klopt er iets niet? Correctie doorgeven</a></p>`;
}

export function monumentPopup(p) {
  return `<h3>${p.naam ? esc(p.naam) : "Rijksmonument " + esc(p.rijksmonumentnummer)}</h3>
    <dl>${rows([
      ["Monumentnummer", raw(link(p.monumentenregister_url, p.rijksmonumentnummer))],
      ["Aard", p.monument_aard],
      ["Oorspronkelijke functie", functieKort(p.oorspronkelijke_functie)],
      ["Huidige functie", functieKort(p.huidige_functie)],
    ])}</dl>`;
}

export function gezichtPopup(p) {
  return `<h3>${esc(p.naam || "Beschermd gezicht")}</h3>
    <dl>${rows([["Gezichtsnummer", p.gezichtsnummer], ["Status", "rijksbeschermd stads- of dorpsgezicht"]])}</dl>`;
}
