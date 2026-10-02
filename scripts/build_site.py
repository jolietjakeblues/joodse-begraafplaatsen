#!/usr/bin/env python3
"""
Stel de statische site samen in site/ (gitignored) voor Cloudflare Pages.

src/ wordt 1-op-1 gekopieerd (alle paden in src/ zijn al relatief aan de
site-root: data/..., images/..., vendor/...), plus de data die de viewer
gebruikt en _headers. Geen herschrijfstap nodig, anders dan in dodenakkers.

Lokaal bekijken:  python scripts/build_site.py && python -m http.server -d site 8000
Deploy:           npx wrangler pages deploy site --project-name joodse-begraafplaatsen --branch main
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
MAX_BESTAND = 25 * 1024 * 1024  # Cloudflare Pages-limiet per bestand

DATA_FILES = [
    "data/generated/begraafplaatsen.geojson",
    "data/generated/terreinen.geojson",
    "data/pdok/provincies.geojson",
    "data/pdok/gemeenten.geojson",
    "data/rce/beschermde-gezichten.geojson",
    "data/rce/rijksmonumenten.geojson",
    "data/rce/archeologische-rijksmonumenten.geojson",
]


def main() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    shutil.copytree(REPO_ROOT / "src", SITE_DIR)
    for rel in DATA_FILES:
        dst = SITE_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dst)
    shutil.copyfile(REPO_ROOT / "_headers", SITE_DIR / "_headers")

    files = [f for f in SITE_DIR.rglob("*") if f.is_file()]
    te_groot = [f for f in files if f.stat().st_size > MAX_BESTAND]
    assert not te_groot, f"bestand(en) boven 25 MB: {te_groot}"
    total = sum(f.stat().st_size for f in files)
    print(f"site/ klaar: {len(files)} bestanden, {total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
