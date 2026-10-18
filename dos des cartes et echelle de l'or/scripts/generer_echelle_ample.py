#!/usr/bin/env python3
"""Serpentin plus grand, pièces espacées, fond donjon propre (sans double pièce)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BEST = ROOT / "Best"
ALT = BEST / "alternative"
CARD_W, CARD_H = 750, 1050
RADIUS = 28

spec = importlib.util.spec_from_file_location(
    "geo", Path(__file__).with_name("generer_echelle_or.py")
)
geo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo)


def round_card(im: Image.Image, radius: int = RADIUS) -> Image.Image:
    card = im.convert("RGBA")
    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, CARD_W - 1, CARD_H - 1), radius=radius, fill=255
    )
    mask = mask.filter(ImageFilter.GaussianBlur(0.35))
    out = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    out.paste(card, (0, 0))
    out.putalpha(mask)
    bg = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    return Image.alpha_composite(bg, out).convert("RGB")


def inner_dungeon(im: Image.Image) -> Image.Image:
    """Enlève le parchemin du fond pour coller au recadrage poker."""
    w, h = im.size
    # cadre parchemin + filet orange
    l, t, r, b = int(w * 0.075), int(h * 0.055), int(w * 0.925), int(h * 0.945)
    return im.crop((l, t, r, b))


# Formes du côté A (0 → 6). S plus ample, 180°-symétrique.
SHAPES = {
    # Boucles plus grandes, même esprit que la 02 originale.
    "ample_rond": [
        (0.50, 0.50),
        (0.76, 0.545),
        (0.88, 0.70),
        (0.76, 0.87),
        (0.50, 0.93),
        (0.24, 0.87),
        (0.14, 0.72),
    ],
    # Encore plus ouvert en hauteur (serpentin plus long).
    "ample_haut": [
        (0.50, 0.50),
        (0.74, 0.56),
        (0.84, 0.72),
        (0.74, 0.88),
        (0.50, 0.91),
        (0.26, 0.88),
        (0.16, 0.74),
    ],
    # Plus large, boucles ovales.
    "ample_ovale": [
        (0.50, 0.50),
        (0.76, 0.53),
        (0.86, 0.68),
        (0.78, 0.85),
        (0.52, 0.91),
        (0.24, 0.86),
        (0.15, 0.70),
    ],
    # S plus étiré, moins circulaire.
    "ample_ouvert": [
        (0.50, 0.50),
        (0.72, 0.57),
        (0.86, 0.74),
        (0.70, 0.90),
        (0.46, 0.935),
        (0.22, 0.86),
        (0.12, 0.68),
    ],
}

JOBS = [
    (
        "02_donjon_enroule.png",
        BEST,
        "ample_rond",
        "Donjon — grand serpentin rond, pièces espacées",
        dict(ribbon="gold", desired=118, path_width=20, vignette=0.16, warmth=1.02, gap=26),
    ),
    (
        "02a_serpentin_haut.png",
        ALT,
        "ample_haut",
        "Variante A — serpentin plus haut",
        dict(ribbon="gold", desired=110, path_width=20, vignette=0.14, warmth=1.02, gap=30),
    ),
    (
        "02b_serpentin_ovale.png",
        ALT,
        "ample_ovale",
        "Variante B — boucles ovales plus larges",
        dict(ribbon="glow", desired=110, path_width=20, vignette=0.16, warmth=1.03, gap=28),
    ),
    (
        "02c_serpentin_ouvert.png",
        ALT,
        "ample_ouvert",
        "Variante C — S plus étiré",
        dict(ribbon="gold", desired=110, path_width=18, vignette=0.14, warmth=1.01, gap=30),
    ),
]


def report(nodes, coin_size, name):
    ds = geo.neighbor_distances(nodes)
    print(
        f"  {name}: min {min(ds):.0f}  mean {sum(ds)/len(ds):.0f}  "
        f"max {max(ds):.0f}  coin {coin_size}  gap min {min(ds)-coin_size:.0f}"
    )
    r = coin_size / 2 + 6
    for n in nodes:
        if n["x"] < r or n["x"] > CARD_W - r or n["y"] < r or n["y"] > CARD_H - r:
            print(f"    EDGE {n['v']}{'R' if n['rot'] else ''} x={n['x']:.0f} y={n['y']:.0f}")


def main() -> None:
    ALT.mkdir(parents=True, exist_ok=True)
    coin = geo.chromakey_magenta(Image.open(ROOT / "Old" / "fonds" / "piece_or_pixel.jpg"))
    w, h = coin.size
    side = max(w, h)
    blank = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    blank.paste(coin, ((side - w) // 2, (side - h) // 2), coin)

    fond = inner_dungeon(Image.open(ROOT / "Old" / "Fond_Carte_Or.jpg"))

    written: list[tuple[Path, str]] = []
    for name, dest_dir, shape, cap, kw in JOBS:
        gap = kw.pop("gap")
        desired = kw.pop("desired")
        nodes = geo.layout_from_waypoints(CARD_W, CARD_H, SHAPES[shape], cx=0.50, cy=0.50)
        coin_size = geo.fit_coin_size(nodes, desired, gap=gap)
        zero_size = coin_size + 16
        report(nodes, coin_size, Path(name).stem)
        geo.debug_layout(nodes, coin_size, Path(name).stem)
        img = geo.compose_card(
            fond, nodes, blank, coin_size=coin_size, zero_size=zero_size, digit_scale=7, **kw
        )
        img = round_card(img)
        dest = dest_dir / name
        img.save(dest, "PNG", optimize=True)
        written.append((dest, cap))
        print("wrote", dest, img.size, "coin", coin_size)

    # copie aussi la principale dans alternative pour comparer
    main_png = BEST / "02_donjon_enroule.png"
    alt_copy = ALT / "02_donjon_enroule_grand.png"
    Image.open(main_png).save(alt_copy, "PNG", optimize=True)
    print("ok")


if __name__ == "__main__":
    main()
