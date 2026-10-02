#!/usr/bin/env python3
"""
Maak de Open Graph-afbeelding (1200x630) voor het delen van de kaart op
sociale media: provinciegrens + begraafplaatsen in dezelfde kleuren en vormen
als de viewer. Output: src/images/og-image.png (gecommit).

Opnieuw draaien als er provincies bijkomen.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import shape

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS = {  # zelfde als src/app.js
    "in_gebruik": ("Bestaand", "#0072B2", "o", "#0072B2"),
    "geruimd": ("Geruimd", "#E69F00", "D", "#E69F00"),
    "verdwenen": ("Verdwenen", "#3A3A3A", "o", "white"),
}


def main() -> None:
    punten = json.loads((REPO_ROOT / "data/generated/begraafplaatsen.geojson").read_text(encoding="utf-8"))["features"]
    provs = {f["properties"]["provincie"] for f in punten}
    prov_feats = json.loads((REPO_ROOT / "data/pdok/provincies.geojson").read_text(encoding="utf-8"))["features"]

    fig = plt.figure(figsize=(12, 6.3), dpi=100)
    fig.patch.set_facecolor("#f4f4f2")
    ax = fig.add_axes([0.45, 0.04, 0.53, 0.92])
    ax.set_aspect(1 / 0.616)  # cos(52 graden): geen uitgerekte kaart
    ax.axis("off")
    for f in prov_feats:
        geom = shape(f["geometry"])
        actief = f["properties"]["naam"] in provs
        for poly in getattr(geom, "geoms", [geom]):
            x, y = poly.exterior.xy
            ax.fill(x, y, color="white" if actief else "#e6e6e3", zorder=1)
            ax.plot(x, y, color="#4a4a4a" if actief else "#c8c8c4", lw=1.2 if actief else 0.6, zorder=2)
    for s, (_, kleur, marker, vul) in reversed(list(STATUS.items())):
        xs = [f["geometry"]["coordinates"][0] for f in punten if f["properties"]["status"] == s]
        ys = [f["geometry"]["coordinates"][1] for f in punten if f["properties"]["status"] == s]
        ax.scatter(xs, ys, s=90 if marker == "o" else 70, marker=marker, c=vul, edgecolors=kleur if vul == "white" else "white",
                   linewidths=2.2 if vul == "white" else 1, zorder=3)
    b = [shape(f["geometry"]).bounds for f in prov_feats if f["properties"]["naam"] in provs]
    minx, miny, maxx, maxy = min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)
    ax.set_xlim(minx - 0.05, maxx + 0.05)
    ax.set_ylim(miny - 0.03, maxy + 0.03)

    fig.text(0.05, 0.78, "Joodse\nBegraafplaatsen", fontsize=46, fontweight="bold", color="#212529", va="top", linespacing=1.05)
    scope = ("Nederland" if len(provs) == 12 else f"{len(provs)} van 12 provincies") if len(provs) > 3 else ", ".join(sorted(provs))
    fig.text(0.05, 0.47, f"Bestaand, geruimd en verdwenen\n{scope}", fontsize=20, color="#444", va="top", linespacing=1.4)
    y = 0.27
    for s, (label, kleur, marker, vul) in STATUS.items():
        n = sum(1 for f in punten if f["properties"]["status"] == s)
        fig.add_artist(plt.Line2D([0.062], [y], marker=marker, markersize=13 if marker == "o" else 11, color=vul,
                                  markeredgecolor=kleur if vul == "white" else vul, markeredgewidth=2.5, transform=fig.transFigure))
        fig.text(0.085, y, f"{label} ({n})", fontsize=17, color="#212529", va="center")
        y -= 0.065
    fig.text(0.05, 0.035, "Inventarisatie: stichting Dodenakkers", fontsize=13, color="#5f5f5f")
    out = REPO_ROOT / "src/images/og-image.png"
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    print(f"-> {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
