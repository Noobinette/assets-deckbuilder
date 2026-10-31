#!/usr/bin/env python3
"""Jaquette griffon → fond perdu 820×1120 (même format que les dos).

Source : scripts/src_griffon_ciel.jpg (1500×2000).
Sortie : DosCartes/griffon_ciel_fondperdu.png — image qui remplit
le 820×1120, recadrage centré (légèrement sur les côtés, le 3:4
est un peu plus large que le poker).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from separer_logos_fonds import CARD_H, CARD_W

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

BLEED_MM = 3
BLEED_PX = round(CARD_W * BLEED_MM / 63.5)  # 35
BLEED_W, BLEED_H = CARD_W + 2 * BLEED_PX, CARD_H + 2 * BLEED_PX

SRC = SCRIPTS / "src_griffon_ciel.jpg"
OUT = ROOT / "griffon_ciel_fondperdu.png"


def cover_fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(SRC)
    src = Image.open(SRC)
    out = cover_fit(src, BLEED_W, BLEED_H)
    out.save(OUT, "PNG", optimize=True)
    print("src", src.size)
    print("out", out.size, OUT.name)


if __name__ == "__main__":
    main()
