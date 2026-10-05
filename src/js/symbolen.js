// Statussymbolen als bitmap (cirkel / ruit / ring), met witte rand zodat ze
// op luchtfoto en op elkaar zichtbaar blijven.

export function makeSymbol(vorm, kleur, rand, size = 44) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const m = size / 2;
  ctx.lineJoin = "round";
  if (vorm === "ruit") {
    const r = size * 0.42;
    ctx.beginPath();
    ctx.moveTo(m, m - r);
    ctx.lineTo(m + r, m);
    ctx.lineTo(m, m + r);
    ctx.lineTo(m - r, m);
    ctx.closePath();
    ctx.fillStyle = kleur;
    ctx.fill();
    // witte buitenrand (luchtfoto) en daarbinnen een donkere rand (contrast)
    ctx.lineWidth = size * 0.14;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
    ctx.lineWidth = size * 0.07;
    ctx.strokeStyle = rand || kleur;
    ctx.stroke();
  } else if (vorm === "ring") {
    ctx.beginPath();
    ctx.arc(m, m, size * 0.3, 0, Math.PI * 2);
    ctx.lineWidth = size * 0.22;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
    ctx.lineWidth = size * 0.13;
    ctx.strokeStyle = kleur;
    ctx.stroke();
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.beginPath();
    ctx.arc(m, m, size * 0.22, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.arc(m, m, size * 0.36, 0, Math.PI * 2);
    ctx.fillStyle = kleur;
    ctx.fill();
    ctx.lineWidth = size * 0.08;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
  }
  return ctx.getImageData(0, 0, size, size);
}
