#!/usr/bin/env python3
"""Découpe le grimoire cuir brun en deux fonds.

- 06_livre_brun.png            : ras le livre, 750×1050
- 06_livre_brun_fondperdu.png  : même carte + 3 mm de noir de chaque côté
                                 (820×1120)

Carte poker 63,5 × 88,9 mm → 750×1050 px (~300 dpi) → 3 mm = 35 px.
Source : scripts/src_livre_brun.jpg
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from separer_logos_fonds import CARD_H, CARD_W, round_card

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent / "src_livre_brun.jpg"
FONDS = ROOT / "fonds"

# Poker 63.5 × 88.9 mm at 750×1050 (~300 dpi)
BLEED_MM = 3
BLEED_PX = round(CARD_W * BLEED_MM / 63.5)  # 35

# Bbox du livre seul sur la source 864×1152 (x1/y1 exclus).
# Hors cadre brun clair et filet or de la carte.
BOOK_BOX = (23, 29, 833, 1112)


def main() -> None:
    FONDS.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGB")
    book = src.crop(BOOK_BOX)

    ras = round_card(book.resize((CARD_W, CARD_H), Image.Resampling.LANCZOS))
    ras.save(FONDS / "06_livre_brun.png", "PNG", optimize=True)

    bleed_w = CARD_W + 2 * BLEED_PX
    bleed_h = CARD_H + 2 * BLEED_PX
    canvas = Image.new("RGB", (bleed_w, bleed_h), (0, 0, 0))
    canvas.paste(ras, (BLEED_PX, BLEED_PX))
    canvas.save(FONDS / "06_livre_brun_fondperdu.png", "PNG", optimize=True)
    print("livre ras", CARD_W, CARD_H)
    print("livre fond perdu", bleed_w, bleed_h, f"({BLEED_PX} px = {BLEED_MM} mm)")


if __name__ == "__main__":
    main()
