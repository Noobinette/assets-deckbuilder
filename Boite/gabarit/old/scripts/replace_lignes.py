#!/usr/bin/env python3
"""Remplace les traits de coupe/pli du filet par le cadre bois, sans retoucher le reste."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve()
while ROOT != ROOT.parent and not ((ROOT / "AGENTS.md").exists() and (ROOT / "Boite").is_dir()):
    ROOT = ROOT.parent

LINED = ROOT / "Boite" / "gabarit" / "old" / "boite_avec_lignes.jpg"
GABARIT = ROOT / "Boite" / "gabarit" / "old" / "gabarit_source.png"
OUT = ROOT / "Boite" / "gabarit" / "boite.jpg"


def line_mask(gabarit: Image.Image, size: tuple[int, int]) -> np.ndarray:
    alpha = np.array(gabarit.convert("RGBA"))[:, :, 3]
    small = Image.fromarray((alpha > 20).astype(np.uint8) * 255)
    small = small.filter(ImageFilter.MaxFilter(3))
    hi = small.resize(size, Image.Resampling.NEAREST)
    hi = hi.filter(ImageFilter.MaxFilter(11))
    return np.array(hi) > 127


def overlay_fringe(rgb: np.ndarray, near: np.ndarray) -> np.ndarray:
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    red = (r > 150) & (g < 95) & (b < 95)
    green = (g > 145) & (r < 100) & (b < 115)
    mag = (r > 145) & (b > 145) & (g < 115)
    cyan = (g > 130) & (b > 130) & (r < 100)
    return (red | green | mag | cyan) & near


def main() -> None:
    lined_im = Image.open(LINED).convert("RGB")
    rgb = np.array(lined_im)
    h, w = rgb.shape[:2]
    gabarit = Image.open(GABARIT)
    mask = line_mask(gabarit, (w, h))
    near = np.array(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(31))) > 127
    mask = mask | overlay_fringe(rgb, near)
    print("line pixels", int(mask.sum()))

    wood = rgb[1550:1592, 3600:6800]
    wood_v = np.rot90(wood, 1)
    wh, ww = wood.shape[:2]
    vh, vw = wood_v.shape[:2]

    pad = np.pad(mask.astype(np.uint8), 3)
    horiz = pad[3:-3, 1:-5].astype(np.int16) + pad[3:-3, 5:-1]
    vert = pad[1:-5, 3:-3].astype(np.int16) + pad[5:-1, 3:-3]
    use_h = horiz >= vert

    ys, xs = np.where(mask)
    pix = np.where(use_h[ys, xs][:, None], wood[ys % wh, xs % ww], wood_v[ys % vh, xs % vw])
    out = rgb.copy()
    out[ys, xs] = pix
    Image.fromarray(out).save(OUT, "JPEG", quality=86, subsampling=0, optimize=True, dpi=(300, 300))
    print("saved", OUT, out.shape)


if __name__ == "__main__":
    main()
