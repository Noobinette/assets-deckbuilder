#!/usr/bin/env python3
"""Prépare le fond 06 — dos plat à cadres géométriques.

- 06_livre_brun.png            : ras 750×1050, coins arrondis
- 06_livre_brun_fondperdu.png  : même motif agrandi, 820×1120, sans bande noire
                                 (3 mm / 35 px de cadre qui continue)

Plus de tranche de livre : le générateur a refait un dos de carte normal
à partir des cadres du grimoire.

Source : scripts/src_livre_brun.png (sinon .jpg)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from separer_logos_fonds import CARD_H, CARD_W, round_card

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
FONDS = ROOT / "fonds"

BLEED_MM = 3
BLEED_PX = round(CARD_W * BLEED_MM / 63.5)  # 35
BLEED_W, BLEED_H = CARD_W + 2 * BLEED_PX, CARD_H + 2 * BLEED_PX


def cover_fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def load_src() -> Image.Image:
    for name in ("src_livre_brun.png", "src_livre_brun.jpg"):
        p = SCRIPTS / name
        if p.exists():
            return Image.open(p).convert("RGB")
    raise FileNotFoundError("src_livre_brun.png / .jpg manquant")


def main() -> None:
    FONDS.mkdir(parents=True, exist_ok=True)
    bleed = cover_fit(load_src(), BLEED_W, BLEED_H)
    ras = round_card(bleed.crop((BLEED_PX, BLEED_PX, BLEED_PX + CARD_W, BLEED_PX + CARD_H)))
    ras.save(FONDS / "06_livre_brun.png", "PNG", optimize=True)
    bleed.save(FONDS / "06_livre_brun_fondperdu.png", "PNG", optimize=True)
    print("06 ras", CARD_W, CARD_H)
    print("06 fond perdu", BLEED_W, BLEED_H, f"({BLEED_PX} px = {BLEED_MM} mm, motif continu)")


if __name__ == "__main__":
    main()
