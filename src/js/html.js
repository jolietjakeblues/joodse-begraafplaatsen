// Veilige HTML voor popups en de lijst: alles wordt ge-escaped, behalve wat
// expliciet als raw() is gemarkeerd.

import { LINK_DOMEINEN } from "./config.js";
import { esc } from "./gedeeld.js";

export class SafeHtml {
  constructor(html) {
    this.html = html;
  }
}
export const raw = (html) => new SafeHtml(html);

function veiligeUrl(url) {
  try {
    const u = new URL(url);
    return u.protocol === "https:" && LINK_DOMEINEN.includes(u.hostname);
  } catch {
    return false;
  }
}

/** Link naar een bekende bron; anders alleen de (ge-escapete) tekst. */
export function link(url, text) {
  if (!url || !veiligeUrl(url)) return text ? esc(text) : "";
  return `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(text || url)}</a>`;
}

/** Definitielijst: lege waarden worden overgeslagen. */
export function rows(pairs) {
  return pairs
    .filter(([, v]) => v !== null && v !== undefined && v !== "" && !(v instanceof SafeHtml && !v.html))
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v instanceof SafeHtml ? v.html : esc(v)}</dd>`)
    .join("");
}

// Huisje-icoon voor een metaheerhuis(je) (Excel-kolom "Met"); inline SVG, geen externe bron.
export const HUISJE =
  '<svg class="icoon-huisje" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M8 1.5 1 7.5h2v7h4v-4h2v4h4v-7h2z" fill="currentColor"/></svg>';

// RCE-functie zonder code tussen haakjes ("Woonhuis(K)" -> "Woonhuis"); zelfde
// regel als functie_kort() in scripts/analyse_spatial.py.
export const functieKort = (f) => {
  if (!f) return f;
  let k = f;
  while (/\s*\([^()]*\)\s*$/.test(k)) k = k.replace(/\s*\([^()]*\)\s*$/, "");
  return k || f;
};
