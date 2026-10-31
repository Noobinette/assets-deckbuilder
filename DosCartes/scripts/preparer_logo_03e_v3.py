#!/usr/bin/env python3
"""03e V3 : le titre V2 + ombre pixel noire (bas-droite).

À partir de logos/03e_titre_trois_lignesV2.png. L’ombre est un tampon
de pixels noirs décalés, pas un flou — pour voir si ça accroche le titre
sur les fonds cuir.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from separer_logos_fonds import (
    FONDS,
    LOGOS,
    crop_alpha,
    paste_logo_on_fond,
    paste_logo_visual_center,
    preview_checker,
)

DX, DY, THICK = 3, 3, 2
SHADOW = (0, 0, 0, 255)


def add_pixel_shadow(
    rgba: np.ndarray,
    dx: int = DX,
    dy: int = DY,
    thick: int = THICK,
    color: tuple[int, int, int, int] = SHADOW,
) -> np.ndarray:
    h, w = rgba.shape[:2]
    extra = 6
    pad_l = max(0, -min(0, dx) * thick) + extra
    pad_t = max(0, -min(0, dy) * thick) + extra
    pad_r = max(0, max(0, dx) * thick) + extra
    pad_b = max(0, max(0, dy) * thick) + extra
    oh, ow = h + pad_t + pad_b, w + pad_l + pad_r
    out = np.zeros((oh, ow, 4), np.uint8)
    core = rgba[..., 3] >= 200
    sx = int(np.sign(dx)) if dx else 0
    sy = int(np.sign(dy)) if dy else 0
    stamps = list(dict.fromkeys((dx - sx * t, dy - sy * t) for t in range(thick)))
    ys, xs = np.where(core)
    for sdx, sdy in stamps:
        ys2, xs2 = ys + pad_t + sdy, xs + pad_l + sdx
        ok = (ys2 >= 0) & (ys2 < oh) & (xs2 >= 0) & (xs2 < ow)
        out[ys2[ok], xs2[ok]] = color
    y0, x0 = pad_t, pad_l
    src = rgba.astype(np.float32) / 255.0
    dst = out[y0 : y0 + h, x0 : x0 + w].astype(np.float32) / 255.0
    sa = src[..., 3:4]
    rgb = src[..., :3] * sa + dst[..., :3] * (1 - sa)
    a = sa[..., 0] + dst[..., 3] * (1 - sa[..., 0])
    out[y0 : y0 + h, x0 : x0 + w, :3] = np.clip(rgb * 255, 0, 255).astype(np.uint8)
    out[y0 : y0 + h, x0 : x0 + w, 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return crop_alpha(out, pad=6)


def main() -> None:
    src = LOGOS / "03e_titre_trois_lignesV2.png"
    v2 = np.asarray(Image.open(src).convert("RGBA"))
    v3 = add_pixel_shadow(v2)
    dest = LOGOS / "03e_titre_trois_lignesV3.png"
    Image.fromarray(v3).save(dest, "PNG")
    preview_checker(v3).save(LOGOS / "03e_titre_trois_lignesV3_apercu.png", "PNG")
    preview_checker(v2).save(LOGOS / "03e_titre_trois_lignesV2_apercu.png", "PNG")
    print("v3", dest.name, v3.shape)

    exemples = LOGOS.parent / "exemples"
    exemples.mkdir(parents=True, exist_ok=True)
    for fond_name, mix_name, sc, centered in (
        ("01_cuir_brun", "mix_03e_v3_sur_brun", 0.72, False),
        ("04_obsidienne", "mix_03e_v3_sur_obsidienne", 0.72, False),
        ("06_livre_brun", "mix_03e_v3_sur_livre_brun", 0.72, True),
        ("06_livre_brun_fondperdu", "mix_03e_v3_sur_livre_fondperdu", 0.72, True),
    ):
        fp = FONDS / f"{fond_name}.png"
        if not fp.exists():
            continue
        p = exemples / f"{mix_name}.png"
        paste = paste_logo_visual_center if centered else paste_logo_on_fond
        paste(Image.open(fp), v3, sc).save(p, "PNG", optimize=True)
        print("mix", p.name)


if __name__ == "__main__":
    main()
