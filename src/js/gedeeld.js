// Gedeelde hulpfuncties voor alle pagina's (kaart, lezen, statistieken).

const HTML_ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

/** Tekst veilig maken voor gebruik in HTML. */
export function esc(value) {
  return String(value).replace(/[&<>"']/g, (c) => HTML_ESCAPES[c]);
}

/**
 * Element maken. attrs.text wordt textContent; andere attrs worden attributen
 * (null/undefined worden overgeslagen). Kinderen: nodes of tekst; null en
 * undefined worden overgeslagen.
 */
export function el(tag, attrs = {}, ...kinderen) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined) continue;
    if (k === "text") e.textContent = v;
    else e.setAttribute(k, v);
  }
  e.append(...kinderen.filter((k) => k !== null && k !== undefined));
  return e;
}

export async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json();
}

/**
 * Tekst voor zoeken: kleine letters, zonder accenten (ë -> e, â -> a) en
 * zonder leestekens ("'s-Gravenhage" -> "s gravenhage").
 */
export function zoekNorm(tekst) {
  return String(tekst ?? "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/** Getal met Nederlandse scheidingstekens; null blijft null. */
export const fmtInt = (n) => (n == null ? null : Number(n).toLocaleString("nl-NL"));
