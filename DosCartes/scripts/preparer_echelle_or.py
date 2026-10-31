#!/usr/bin/env python3
"""Compose l’échelle de l’or : fond donjon + piste, format des autres dos.

- Fond_Carte_Or.jpg (source) → fond 750×1050 et fond perdu 820×1120
- Piste (EchelleOr_piste_Simple.png) cadrée dans la zone utile :
  5 mm depuis le trim (fond perdu 3 mm + marge de sécu, 5 mm en tout
  depuis le bord de coupe). La piste ne rentre ni dans le bleed ni
  dans la marge.

Sortie (racine) :
- Fond_Carte_Or.png           fond seul, 750×1050
- Fond_Carte_Or_fondperdu.png fond seul, 820×1120
- EchelleOr.png               fond + piste, 750×1050
- EchelleOr_fondperdu.png     fond + piste, 820×1120
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from separer_logos_fonds import CARD_H, CARD_W

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]

BLEED_MM = 3
SAFE_TOTAL_MM = 5  # hors fond perdu + marge, depuis le trim
BLEED_PX = round(CARD_W * BLEED_MM / 63.5)  # 35
SAFE_PX = round(CARD_W * SAFE_TOTAL_MM / 63.5)  # 59
BLEED_W, BLEED_H = CARD_W + 2 * BLEED_PX, CARD_H + 2 * BLEED_PX

SRC_FOND = REPO / "Fond_Carte_Or.jpg"
SRC_PISTE = REPO / "EchelleOr_piste_Simple.png"


def cover_fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def opaque_bbox(im: Image.Image, thresh: int = 10) -> tuple[int, int, int, int]:
    a = im.getchannel("A")
    bb = a.point(lambda p: 255 if p > thresh else 0).getbbox()
    if bb is None:
        raise RuntimeError("piste vide")
    return bb


def fit_piste(piste: Image.Image, box_w: int, box_h: int) -> Image.Image:
    piste = piste.convert("RGBA")
    x0, y0, x1, y1 = opaque_bbox(piste)
    cropped = piste.crop((x0, y0, x1, y1))
    scale = min(box_w / cropped.width, box_h / cropped.height)
    nw = max(1, int(round(cropped.width * scale)))
    nh = max(1, int(round(cropped.height * scale)))
    return cropped.resize((nw, nh), Image.Resampling.LANCZOS)


def paste_centered(dest: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    x = x0 + (x1 - x0 - src.width) // 2
    y = y0 + (y1 - y0 - src.height) // 2
    dest.alpha_composite(src, (x, y))


def main() -> None:
    src = Image.open(SRC_FOND)
    fond_fp = cover_fit(src, BLEED_W, BLEED_H)
    fond_ras = fond_fp.crop((BLEED_PX, BLEED_PX, BLEED_PX + CARD_W, BLEED_PX + CARD_H))
    fond_ras.save(REPO / "Fond_Carte_Or.png", "PNG", optimize=True)
    fond_fp.save(REPO / "Fond_Carte_Or_fondperdu.png", "PNG", optimize=True)

    inner_w = CARD_W - 2 * SAFE_PX
    inner_h = CARD_H - 2 * SAFE_PX
    piste = fit_piste(Image.open(SRC_PISTE), inner_w, inner_h)

    ras = fond_ras.convert("RGBA")
    paste_centered(ras, piste, (SAFE_PX, SAFE_PX, CARD_W - SAFE_PX, CARD_H - SAFE_PX))
    ras.convert("RGB").save(REPO / "EchelleOr.png", "PNG", optimize=True)

    fp = fond_fp.convert("RGBA")
    paste_centered(
        fp,
        piste,
        (
            BLEED_PX + SAFE_PX,
            BLEED_PX + SAFE_PX,
            BLEED_PX + CARD_W - SAFE_PX,
            BLEED_PX + CARD_H - SAFE_PX,
        ),
    )
    fp.convert("RGB").save(REPO / "EchelleOr_fondperdu.png", "PNG", optimize=True)

    print("fond ras", fond_ras.size)
    print("fond perdu", fond_fp.size, f"bleed {BLEED_PX} px = {BLEED_MM} mm")
    print(
        "piste",
        piste.size,
        f"safe {SAFE_PX} px = {SAFE_TOTAL_MM} mm depuis le trim",
    )


if __name__ == "__main__":
    main()
