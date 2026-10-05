// Leeslijst: artikelen van dodenakkers.nl met de tag "Joodse begraafplaats".
// Data: data/generated/leeslijst.json (scripts/fetch_leeslijst.py). Alleen
// titels en links; de inhoud staat op dodenakkers.nl.

import { el } from "./gedeeld.js";

const PROVINCIE_VOLGORDE = [
  "Zuid-Holland", "Noord-Holland", "Utrecht", "Zeeland", "Flevoland",
  "Gelderland", "Overijssel", "Noord-Brabant", "Limburg", "Groningen", "Drenthe", "Fryslân",
];


// Alleen links naar dodenakkers.nl (de leeslijst komt van die site); iets anders
// wordt gewone tekst, zodat er nooit een javascript:- of vreemde link ontstaat.
const DODENAKKERS = "https://www.dodenakkers.nl/";
const extern = (url, tekst) =>
  typeof url === "string" && url.startsWith(DODENAKKERS)
    ? el("a", { href: url, target: "_blank", rel: "noopener", text: tekst })
    : el("span", { text: tekst });
const datum = (iso) => new Date(iso).toLocaleDateString("nl-NL", { day: "numeric", month: "long", year: "numeric" });

function artikelItem(a) {
  const li = el("li", {}, extern(a.url, a.titel));
  if (a.kaart) {
    li.append(" ", el("a", { class: "lees-kaartlink", href: `./?id=${encodeURIComponent(a.kaart.id)}`, text: "Bekijk op de kaart" }));
  }
  return li;
}

async function main() {
  const bronEl = document.getElementById("lees-bron");
  try {
    const res = await fetch("data/generated/leeslijst.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const perProvincie = document.getElementById("per-provincie");
    for (const prov of PROVINCIE_VOLGORDE) {
      const items = data.artikelen.filter((a) => a.provincie === prov);
      if (!items.length) continue;
      perProvincie.append(el("h3", { text: `${prov} (${items.length})` }), el("ul", { class: "lees-lijst" }, ...items.map(artikelItem)));
    }
    const overig = data.artikelen.filter((a) => !a.provincie);
    document.getElementById("overig").append(...overig.map((a) => {
      const li = artikelItem(a);
      li.append(el("span", { class: "hint", text: ` · ${a.rubriek}` }));
      return li;
    }));

    bronEl.replaceChildren(
      `${data.artikelen.length} artikelen, opgehaald op ${datum(data.opgehaald)} van `,
      extern(data.bron, "dodenakkers.nl/tag/joodse-begraafplaats"),
      ". De artikelen zijn van stichting Dodenakkers en de auteurs."
    );
  } catch (err) {
    bronEl.replaceChildren(
      `De leeslijst kon niet worden geladen (${err.message}). Bekijk de artikelen op `,
      extern("https://www.dodenakkers.nl/tag/joodse-begraafplaats.html", "dodenakkers.nl"),
      "."
    );
  }
}

main();
