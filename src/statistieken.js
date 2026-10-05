// Joodse Begraafplaatsen - statistiekpagina (wens opdrachtgever 2026-10-05, vraag E7).
//
// Toont data/generated/statistieken.json (scripts/compute_statistics.py).
// Geen berekeningen hier, alleen weergave. Namen van begraafplaatsen linken
// naar de kaart (?id=...).

const STATUS = {
  in_gebruik: "In gebruik",
  geruimd: "Geruimd",
  verdwenen: "Verdwenen",
};

function el(tag, attrs = {}, ...kinderen) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "text") e.textContent = v;
    else e.setAttribute(k, v);
  }
  e.append(...kinderen.filter((k) => k !== null && k !== undefined));
  return e;
}

const fmt = (n) => (n === null || n === undefined ? "–" : Number(n).toLocaleString("nl-NL"));
const sym = (status) => el("span", { class: `sym sym-${status}`, "aria-hidden": "true" });
const kaartLink = (r) => el("a", { href: `./?id=${encodeURIComponent(r.id)}`, text: r.naam });

function sectie(id, kop, ...inhoud) {
  const s = document.getElementById(id);
  s.append(el("h2", { id: `h-${id.replace("stats-", "")}`, text: kop }), ...inhoud);
}

function kv(paren) {
  const dl = el("dl", { class: "stats-kv" });
  for (const [k, v] of paren) dl.append(el("dt", { text: k }), el("dd", {}, v));
  return dl;
}

// kolommen: [{kop, waarde: (rij) => string|Node, num?: true}]
function tabel(bijschrift, kolommen, rijen, totaal) {
  const t = el("table", { class: "stats-tabel" }, el("caption", { text: bijschrift }));
  t.append(el("thead", {}, el("tr", {}, ...kolommen.map((k) => el("th", { scope: "col", class: k.num ? "num" : "" , text: k.kop })))));
  const td = (k, r) => {
    const v = k.waarde(r);
    return el("td", { class: k.num ? "num" : "" }, typeof v === "number" ? fmt(v) : v ?? "–");
  };
  t.append(el("tbody", {}, ...rijen.map((r) => el("tr", {}, ...kolommen.map((k) => td(k, r))))));
  if (totaal) t.append(el("tfoot", {}, el("tr", {}, ...kolommen.map((k) => td(k, totaal)))));
  return el("div", { class: "stats-tabel-wrap" }, t);
}

const statusKolommen = Object.entries(STATUS).map(([s, label]) => ({ kop: label, waarde: (r) => r[s], num: true }));

function balken(klassen) {
  const max = Math.max(1, ...klassen.map((k) => k.aantal));
  return el("div", { class: "stats-balken", role: "img", "aria-label": klassen.map((k) => `${k.label}: ${k.aantal}`).join(", ") },
    ...klassen.map((k) => {
      const bar = el("span", { class: "histogram-bar" });
      bar.style.width = `${Math.round((k.aantal / max) * 100)}%`;
      return el("div", { class: "stats-balk", "aria-hidden": "true" },
        el("span", { class: "histogram-label", text: k.label }),
        el("span", { class: "histogram-bar-wrap" }, bar),
        el("span", { class: "histogram-count", text: fmt(k.aantal) }));
    }));
}

function renderBasis(s) {
  const b = s.basis;
  sectie("stats-basis", "Kerncijfers",
    kv([
      ["Begraafplaatsen", fmt(b.totaal)],
      ...Object.entries(STATUS).map(([st, label]) => [label, el("span", {}, sym(st), ` ${fmt(b.per_status[st])}`)]),
      ["Met getekend terrein", fmt(b.met_terrein)],
      ["Totale oppervlakte terreinen", `${fmt(Math.round(b.totaal_m2 / 1000) / 10)} ha`],
      ["Mediaan oppervlakte", `${fmt(b.mediaan_m2)} m²`],
      ["Grootste terrein", el("span", {}, kaartLink(b.grootste), `, ${b.grootste.plaats} (${fmt(b.grootste.m2)} m²)`)],
      ["Kleinste terrein", el("span", {}, kaartLink(b.kleinste), `, ${b.kleinste.plaats} (${fmt(b.kleinste.m2)} m²)`)],
    ]),
    el("p", { class: "hint", text: "Verdwenen begraafplaatsen hebben geen terrein: hun plek is alleen bij benadering bekend." }));
}

function renderProvincie(s) {
  const som = (k) => s.per_provincie.reduce((t, r) => t + r[k], 0);
  const totaal = { provincie: "Totaal", totaal: som("totaal"), in_gebruik: som("in_gebruik"), geruimd: som("geruimd"), verdwenen: som("verdwenen"), met_terrein: som("met_terrein"), totaal_m2: som("totaal_m2") };
  sectie("stats-provincie", "Per provincie",
    tabel("Begraafplaatsen per provincie en status", [
      { kop: "Provincie", waarde: (r) => r.provincie },
      { kop: "Totaal", waarde: (r) => r.totaal, num: true },
      ...statusKolommen,
      { kop: "Met terrein", waarde: (r) => r.met_terrein, num: true },
      { kop: "Oppervlakte (ha)", waarde: (r) => fmt(Math.round(r.totaal_m2 / 1000) / 10), num: true },
    ], s.per_provincie, totaal));
}

function renderGemeente(s) {
  sectie("stats-gemeente", "Per gemeente",
    tabel("Gemeenten met de meeste Joodse begraafplaatsen", [
      { kop: "Gemeente", waarde: (r) => r.gemeente },
      { kop: "Provincie", waarde: (r) => r.provincie },
      { kop: "Totaal", waarde: (r) => r.totaal, num: true },
      ...statusKolommen,
    ], s.per_gemeente),
    s.meeste_verdwenen_gemeente.length
      ? tabel("Gemeenten met twee of meer verdwenen of geruimde begraafplaatsen", [
          { kop: "Gemeente", waarde: (r) => r.gemeente },
          { kop: "Verdwenen of geruimd", waarde: (r) => r.verdwenen_of_geruimd, num: true },
          { kop: "Totaal in gemeente", waarde: (r) => r.totaal, num: true },
        ], s.meeste_verdwenen_gemeente)
      : null);
}

function renderDatering(s) {
  const d = s.datering;
  const jaar = (r) => `${r.circa ? "ca. " : ""}${r.jaartal}`;
  const oudKolommen = [
    { kop: "Jaar", waarde: jaar, num: true },
    { kop: "Begraafplaats", waarde: (r) => kaartLink(r) },
    { kop: "Plaats", waarde: (r) => r.plaats },
    { kop: "Status", waarde: (r) => el("span", {}, sym(r.status), ` ${STATUS[r.status]}`) },
  ];
  sectie("stats-datering", "Datering",
    el("p", { class: "hint", text: `Jaar van aanleg of eerste begraving. ${fmt(d.met_jaartal)} van ${fmt(s.basis.totaal)} begraafplaatsen hebben een jaartal; "ca." telt mee.` }),
    balken(d.klassen),
    tabel("Aantal begraafplaatsen per periode en status", [
      { kop: "Periode", waarde: (r) => r.label },
      { kop: "Totaal", waarde: (r) => r.aantal, num: true },
      ...statusKolommen,
    ], d.klassen),
    tabel("De oudste begraafplaatsen", oudKolommen, d.oudste),
    tabel("De oudste begraafplaatsen die nog in gebruik zijn", oudKolommen, d.oudste_in_gebruik));
}

function renderErfgoed(s) {
  const e = s.erfgoed;
  sectie("stats-erfgoed", "Erfgoed",
    kv([
      ["Rijksmonument (volgens de inventarisatie)", fmt(e.rijksmonument)],
      ["Gemeentelijk monument", fmt(e.gemeentelijk_monument)],
      ["Opgenomen in het MIP", fmt(e.mip)],
      ["Met metaheerhuis", fmt(e.metaheerhuis)],
      ["In of deels in een beschermd gezicht", `${fmt(e.in_gezicht)} van ${fmt(e.basis)}`],
      ["Met een rijksmonument binnen 100 m", `${fmt(e.met_rijksmonument_100m)} van ${fmt(e.basis)}`],
      ["Rijksmonumenten binnen 100 m van een begraafplaats", `${fmt(e.unieke_monumenten_100m)} (${fmt(e.relaties_100m)} relaties; een monument kan bij meer dan één begraafplaats liggen)`],
    ]),
    el("p", { class: "hint", text: `Gezichten en rijksmonumenten in de buurt zijn alleen berekend voor de ${fmt(e.basis)} begraafplaatsen in gebruik of geruimd; van verdwenen begraafplaatsen is de plek niet precies genoeg bekend.` }),
    tabel("Erfgoed per provincie", [
      { kop: "Provincie", waarde: (r) => r.provincie },
      { kop: "Rijksmonument", waarde: (r) => r.rijksmonument, num: true },
      { kop: "In beschermd gezicht", waarde: (r) => r.in_gezicht, num: true },
      { kop: "Metaheerhuis", waarde: (r) => r.metaheerhuis, num: true },
    ], e.per_provincie),
    tabel("Rijksmonumenten binnen 100 m naar oorspronkelijke functie (elk monument één keer geteld)", [
      { kop: "Functie", waarde: (r) => r.functie },
      { kop: "Monumenten", waarde: (r) => r.aantal, num: true },
    ], e.top_functies_100m));
}

function renderHerbegraving(s) {
  const h = s.herbegravingen;
  sectie("stats-herbegraving", "Herbegravingen",
    kv([
      ["Herbegravingen op de kaart", fmt(h.lijnen)],
      ["Naar verschillende begraafplaatsen", fmt(h.bestemmingen)],
      ["Records met “overgebracht” in de bijzonderheden", fmt(h.met_tekst_overgebracht)],
    ]),
    el("p", { class: "hint", text: "Alleen herbegravingen waarvan de bestemming eenduidig een begraafplaats op de kaart is, staan als lijn op de kaart." }),
    h.meeste_ontvangen.length
      ? tabel("Begraafplaatsen die van twee of meer plekken resten ontvingen", [
          { kop: "Begraafplaats", waarde: (r) => kaartLink(r) },
          { kop: "Plaats", waarde: (r) => r.plaats },
          { kop: "Herbegravingen", waarde: (r) => r.aantal, num: true },
        ], h.meeste_ontvangen)
      : null);
}

async function main() {
  const statusEl = document.getElementById("stats-status");
  try {
    const res = await fetch("data/generated/statistieken.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const s = await res.json();
    const n = s.provincies_op_kaart.length;
    document.getElementById("stats-scope").textContent =
      n === 12 ? "Heel Nederland." : `${n} van de 12 provincies staan op de kaart: ${s.provincies_op_kaart.join(", ")}.`;
    renderBasis(s);
    renderProvincie(s);
    renderGemeente(s);
    renderDatering(s);
    renderErfgoed(s);
    renderHerbegraving(s);
    statusEl.textContent = `Berekend op ${new Date(s.gegenereerd).toLocaleDateString("nl-NL", { day: "numeric", month: "long", year: "numeric" })}.`;
  } catch (err) {
    statusEl.textContent = `De cijfers konden niet worden geladen (${err.message}). Herlaad de pagina.`;
  }
}

main();
