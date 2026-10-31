#!/usr/bin/env python3
"""Prépare EchelleOr.png (750×1050) et EchelleOr_fondperdu.png (820×1120).

Le fond perdu n’est plus la carte collée sur du noir : le donjon continue
sur les 3 mm. Les pièces d’or du trim d’origine restent à la même place.
Les bandes gauche/droite recopiées (~15–30 px) sont remplacées par du
décor unique, pour éviter le doublon.

Sources :
- src_echelle_or_etendu.jpg  : donjon étendu (généré)
- src_echelle_or_trim.png    : trim d’origine, pour verrouiller l’échelle
Sortie : racine du dépôt.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from separer_logos_fonds import CARD_H, CARD_W

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]

BLEED_MM = 3
BLEED_PX = round(CARD_W * BLEED_MM / 63.5)  # 35
BLEED_W, BLEED_H = CARD_W + 2 * BLEED_PX, CARD_H + 2 * BLEED_PX
EDGE = 32  # largeur des bandes doublées à jeter sur le trim d’origine


def cover_fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def compose(etendu: Image.Image, trim: Image.Image) -> Image.Image:
    bg = np.array(cover_fit(etendu, BLEED_W, BLEED_H))
    orig = np.array(trim.convert("RGB"))
    if orig.shape[1] != CARD_W or orig.shape[0] != CARD_H:
        orig = np.array(trim.convert("RGB").resize((CARD_W, CARD_H), Image.Resampling.LANCZOS))
    mask = np.ones((CARD_H, CARD_W), np.float32)
    mask[:, :EDGE] = 0.0
    mask[:, CARD_W - EDGE :] = 0.0
    yy, xx = np.ogrid[:CARD_H, :CARD_W]
    for cx, cy in ((0, 0), (CARD_W - 1, 0), (0, CARD_H - 1), (CARD_W - 1, CARD_H - 1)):
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        mask = np.minimum(mask, np.clip((dist - 12) / 28.0, 0, 1))
    mask = cv2.GaussianBlur(mask, (25, 25), 0)
    roi = bg[BLEED_PX : BLEED_PX + CARD_H, BLEED_PX : BLEED_PX + CARD_W].astype(np.float32)
    blended = orig.astype(np.float32) * mask[..., None] + roi * (1.0 - mask[..., None])
    bg[BLEED_PX : BLEED_PX + CARD_H, BLEED_PX : BLEED_PX + CARD_W] = np.clip(
        blended, 0, 255
    ).astype(np.uint8)
    return Image.fromarray(bg)


def main() -> None:
    etendu = Image.open(SCRIPTS / "src_echelle_or_etendu.jpg")
    trim = Image.open(SCRIPTS / "src_echelle_or_trim.png")
    fondperdu = compose(etendu, trim)
    ras = fondperdu.crop((BLEED_PX, BLEED_PX, BLEED_PX + CARD_W, BLEED_PX + CARD_H))
    ras.save(REPO / "EchelleOr.png", "PNG", optimize=True)
    fondperdu.save(REPO / "EchelleOr_fondperdu.png", "PNG", optimize=True)
    print("echelle ras", CARD_W, CARD_H)
    print("echelle fond perdu", BLEED_W, BLEED_H, f"({BLEED_PX} px = {BLEED_MM} mm, donjon continu)")


if __name__ == "__main__":
    main()
