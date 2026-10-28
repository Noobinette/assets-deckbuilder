#!/usr/bin/env python3
"""Génère 6 propositions de carte « échelle de l'OR ».

Piste unique en S : 6 → 0 → 6.
Chaque joueur lit SES chiffres à l'endroit (côté adverse tourné de 180°).
Les 13 pièces sont posées à pas (quasi) égal le long du serpentin.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "propositions"
FONDS = ROOT / "fonds"
CARD_W, CARD_H = 750, 1050

DIGITS = {
    "0": [
        "001111100",
        "011000110",
        "110000011",
        "110000011",
        "110000011",
        "110000011",
        "110000011",
        "110000011",
        "110000011",
        "011000110",
        "001111100",
    ],
    "1": [
        "000110000",
        "001110000",
        "110110000",
        "000110000",
        "000110000",
        "000110000",
        "000110000",
        "000110000",
        "000110000",
        "000110000",
        "111111111",
    ],
    "2": [
        "011111110",
        "110000011",
        "110000011",
        "000000011",
        "000000110",
        "000011100",
        "001110000",
        "011000000",
        "110000000",
        "110000011",
        "111111111",
    ],
    "3": [
        "011111110",
        "110000011",
        "000000011",
        "000000011",
        "001111110",
        "000000011",
        "000000011",
        "000000011",
        "000000011",
        "110000011",
        "011111110",
    ],
    "4": [
        "000001100",
        "000011100",
        "000110100",
        "001100100",
        "011000100",
        "110000100",
        "111111111",
        "000000100",
        "000000100",
        "000000100",
        "000001110",
    ],
    "5": [
        "111111111",
        "110000000",
        "110000000",
        "110000000",
        "111111110",
        "000000011",
        "000000011",
        "000000011",
        "110000011",
        "110000011",
        "011111110",
    ],
    "6": [
        "001111110",
        "011000011",
        "110000000",
        "110000000",
        "111111110",
        "110000011",
        "110000011",
        "110000011",
        "110000011",
        "011000110",
        "001111100",
    ],
}


def cover_crop(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    src_w, src_h = im.size
    scale = max(w / src_w, h / src_h)
    nw, nh = max(w, round(src_w * scale)), max(h, round(src_h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def chromakey_magenta(im: Image.Image, thresh: float = 75.0) -> Image.Image:
    rgba = im.convert("RGBA")
    arr = np.asarray(rgba).astype(np.float32)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    dist = np.sqrt((r - 255) ** 2 + (g - 0) ** 2 + (b - 255) ** 2)
    mag = np.minimum(r, b) - g
    alpha = np.clip((dist - thresh) / 40.0, 0, 1) * a
    alpha = np.where(mag > 80, alpha * 0.15, alpha)
    h, w = alpha.shape
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h / 2.0, w / 2.0
    rad = min(h, w) * 0.46
    circ = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rad ** 2
    inside = circ & (dist > 55)
    alpha = np.where(inside, np.maximum(alpha, 220), alpha)
    alpha = np.where(dist < 45, 0, alpha)
    arr[..., 3] = alpha
    out = Image.fromarray(arr.astype(np.uint8), "RGBA")
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def load_blank_coin() -> Image.Image:
    coin = chromakey_magenta(Image.open(FONDS / "piece_or_pixel.jpg"))
    w, h = coin.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(coin, ((side - w) // 2, (side - h) // 2), coin)
    return canvas


def render_digit(ch: str, scale: int, color=(42, 22, 8, 255)) -> Image.Image:
    rows = DIGITS[ch]
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, bit in enumerate(row):
            if bit == "1":
                px[x, y] = color
    return img.resize((w * scale, h * scale), Image.Resampling.NEAREST)


def stamp_number(coin: Image.Image, value: int, rotate: bool, scale: int) -> Image.Image:
    coin = coin.copy()
    digit = render_digit(str(value), scale=scale)
    halo = render_digit(str(value), scale=scale, color=(90, 50, 10, 140))
    highlight = render_digit(str(value), scale=scale, color=(255, 220, 120, 140))
    cw, ch = coin.size
    dw, dh = digit.size
    x, y = (cw - dw) // 2, (ch - dh) // 2 - scale
    coin.alpha_composite(halo, (x + scale, y + scale))
    coin.alpha_composite(highlight, (x - scale, y - scale))
    coin.alpha_composite(digit, (x, y))
    if rotate:
        coin = coin.rotate(180, resample=Image.Resampling.BICUBIC, expand=False)
    return coin


def equal_arc_points(samples: list[tuple[float, float]], count: int) -> list[tuple[float, float]]:
    if count == 1:
        return [samples[0]]
    dist = [0.0]
    for (x0, y0), (x1, y1) in zip(samples, samples[1:]):
        dist.append(dist[-1] + math.hypot(x1 - x0, y1 - y0))
    total = dist[-1] or 1.0
    targets = [total * i / (count - 1) for i in range(count)]
    out: list[tuple[float, float]] = []
    j = 0
    for t in targets:
        while j < len(dist) - 2 and dist[j + 1] < t:
            j += 1
        span = dist[j + 1] - dist[j]
        u = 0.0 if span <= 1e-6 else (t - dist[j]) / span
        x = samples[j][0] + (samples[j + 1][0] - samples[j][0]) * u
        y = samples[j][1] + (samples[j + 1][1] - samples[j][1]) * u
        out.append((x, y))
    return out


def catmull_rom(points: list[tuple[float, float]], n_per: int = 24) -> list[tuple[float, float]]:
    if len(points) < 2:
        return points
    pts = [points[0]] + points + [points[-1]]
    out: list[tuple[float, float]] = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t in range(n_per):
            s = t / n_per
            s2, s3 = s * s, s * s * s
            x = 0.5 * (
                (2 * p1[0])
                + (-p0[0] + p2[0]) * s
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * s2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * s3
            )
            y = 0.5 * (
                (2 * p1[1])
                + (-p0[1] + p2[1]) * s
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * s2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * s3
            )
            out.append((x, y))
    out.append(points[-1])
    return out


def layout_from_waypoints(
    w: int,
    h: int,
    a_points: list[tuple[float, float]],
    *,
    cx: float = 0.50,
    cy: float = 0.50,
) -> list[dict]:
    """S 180°-symétrique. `a_points` = forme du côté A (0 → 6), puis pas égal.

    A (bas, chiffres droits). B = rotation 180° autour de (cx, cy).
    """
    px = [(x * w, y * h) for x, y in a_points]
    samples = catmull_rom(px, n_per=48)
    half = equal_arc_points(samples, 7)
    half[0] = (cx * w, cy * h)

    nodes = [{"x": half[0][0], "y": half[0][1], "v": 0, "rot": False}]
    for i, (x, y) in enumerate(half[1:], start=1):
        nodes.append({"x": x, "y": y, "v": i, "rot": False})
    for i, (x, y) in enumerate(half[1:], start=1):
        nodes.append({"x": 2 * cx * w - x, "y": 2 * cy * h - y, "v": i, "rot": True})

    order = (
        [(6, True), (5, True), (4, True), (3, True), (2, True), (1, True)]
        + [(0, False)]
        + [(1, False), (2, False), (3, False), (4, False), (5, False), (6, False)]
    )
    by_key = {(n["v"], n["rot"]): n for n in nodes}
    return [by_key[k] for k in order]


# Formes du côté A (0 → 6), fractions de la carte. Virages arrondis, pas une grille.
SHAPES: dict[str, list[tuple[float, float]]] = {
    # S ouvert façon 1re proposition, mais on ré-espace ensuite.
    "ouvert": [
        (0.50, 0.50),
        (0.68, 0.505),
        (0.80, 0.58),
        (0.81, 0.71),
        (0.72, 0.845),
        (0.50, 0.885),
        (0.26, 0.875),
    ],
    # Plus enroulé / circulaire, pour qu’on voie bien la différence.
    "enroule": [
        (0.50, 0.50),
        (0.70, 0.53),
        (0.82, 0.66),
        (0.76, 0.80),
        (0.58, 0.89),
        (0.36, 0.88),
        (0.20, 0.78),
    ],
    # 0 calé sur le seuil d’or ; 4-5-6 entre les coffres.
    "seuil": [
        (0.50, 0.490),
        (0.66, 0.52),
        (0.74, 0.60),
        (0.74, 0.70),
        (0.64, 0.785),
        (0.50, 0.805),
        (0.34, 0.790),
    ],
    # Serpentin dans l’arche : coffres à gauche, escalier à droite.
    "arche": [
        (0.50, 0.50),
        (0.64, 0.53),
        (0.70, 0.63),
        (0.68, 0.74),
        (0.60, 0.84),
        (0.48, 0.875),
        (0.36, 0.86),
    ],
    # Mine galerie : colonne droite rentrée pour laisser le wagonnet.
    "mine_galerie": [
        (0.50, 0.48),
        (0.62, 0.505),
        (0.68, 0.60),
        (0.66, 0.72),
        (0.54, 0.83),
        (0.36, 0.855),
        (0.22, 0.83),
    ],
    # Mine filon : S plus large, 6 au sol, 3 au-dessus de la pelle.
    "mine_filon": [
        (0.50, 0.50),
        (0.66, 0.52),
        (0.78, 0.61),
        (0.78, 0.72),
        (0.68, 0.84),
        (0.48, 0.88),
        (0.28, 0.86),
    ],
}


def neighbor_distances(nodes: list[dict]) -> list[float]:
    ds = []
    for a, b in zip(nodes, nodes[1:]):
        ds.append(math.hypot(b["x"] - a["x"], b["y"] - a["y"]))
    return ds


def fit_coin_size(nodes: list[dict], desired: int, gap: int = 14) -> int:
    ds = neighbor_distances(nodes)
    min_d = min(ds) if ds else desired + gap
    size = min(desired, int(min_d - gap))
    return max(88, size)


def draw_ribbon(
    canvas: Image.Image,
    points: list[tuple[float, float]],
    width: float,
    style: str = "gold",
) -> None:
    samples = catmull_rom(points, n_per=28)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    if style == "stone":
        layers = [
            (width + 12, (22, 16, 8, 230)),
            (width + 6, (78, 56, 22, 245)),
            (width + 1, (148, 108, 32, 255)),
            (width - 6, (196, 150, 46, 255)),
        ]
    elif style == "glow":
        layers = [
            (width + 18, (255, 170, 32, 36)),
            (width + 10, (210, 140, 20, 80)),
            (width + 4, (72, 42, 8, 240)),
            (width - 1, (186, 132, 28, 255)),
            (width - 6, (230, 178, 52, 235)),
        ]
    else:
        layers = [
            (width + 8, (36, 20, 4, 240)),
            (width + 3, (132, 88, 16, 255)),
            (width - 2, (188, 140, 32, 255)),
            (width - 7, (226, 178, 56, 235)),
        ]
    for rad, color in layers:
        r = max(2, rad / 2)
        for x, y in samples:
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    canvas.alpha_composite(overlay)


def draw_zero_medallion(canvas: Image.Image, cx: float, cy: float, size: int) -> None:
    """Disque pierre/or derrière le 0, pour marquer la moitié."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r = size * 0.72
    d.ellipse((cx - r - 3, cy - r + 4, cx + r + 3, cy + r + 8), fill=(20, 10, 4, 90))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(92, 62, 18, 230))
    d.ellipse((cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5), fill=(168, 122, 36, 235))
    d.ellipse((cx - r + 11, cy - r + 11, cx + r - 11, cy + r - 11), fill=(58, 38, 12, 200))
    canvas.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(0.6)))


def paste_shadow(canvas: Image.Image, size: int, cx: float, cy: float, strength=90) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    r = size / 2
    off = size * 0.06
    d.ellipse(
        (cx - r + off, cy - r + off * 1.4, cx + r + off, cy + r + off * 1.4),
        fill=(0, 0, 0, strength),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.08))
    canvas.alpha_composite(shadow)


def compose_card(
    background: Image.Image,
    nodes: list[dict],
    coin_src: Image.Image,
    *,
    ribbon: str = "gold",
    coin_size: int = 100,
    zero_size: int = 114,
    digit_scale: int = 6,
    vignette: float = 0.28,
    warmth: float = 1.0,
    path_width: float = 20,
) -> Image.Image:
    bg = cover_crop(background, CARD_W, CARD_H).convert("RGBA")
    if warmth != 1.0:
        bg = ImageEnhance.Color(bg).enhance(warmth)
        bg = ImageEnhance.Contrast(bg).enhance(1.04)

    canvas = bg.copy()
    if vignette > 0:
        vig = Image.new("L", (CARD_W, CARD_H), 0)
        vd = ImageDraw.Draw(vig)
        pad = 30
        vd.ellipse((-40, -20, CARD_W + 40, CARD_H + 20), fill=int(255 * (1 - vignette * 0.15)))
        vd.ellipse((pad, pad * 1.2, CARD_W - pad, CARD_H - pad * 1.2), fill=255)
        vig = vig.filter(ImageFilter.GaussianBlur(48))
        black = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, int(180 * vignette)))
        canvas = Image.composite(canvas, Image.alpha_composite(canvas, black), vig)

    zero = next(n for n in nodes if n["v"] == 0)
    draw_zero_medallion(canvas, zero["x"], zero["y"], zero_size)

    pts = [(n["x"], n["y"]) for n in nodes]
    draw_ribbon(canvas, pts, path_width, style=ribbon)

    for n in nodes:
        size = zero_size if n["v"] == 0 else coin_size
        paste_shadow(canvas, size, n["x"], n["y"], strength=90)
        ds = digit_scale if n["v"] != 0 else digit_scale + 1
        coin = coin_src.resize((size, size), Image.Resampling.LANCZOS)
        stamped = stamp_number(coin, n["v"], n["rot"], ds)
        x, y = int(n["x"] - size / 2), int(n["y"] - size / 2)
        canvas.alpha_composite(stamped, (x, y))

    return canvas.convert("RGB")


def debug_layout(nodes: list[dict], coin_size: int, name: str) -> None:
    img = Image.new("RGB", (CARD_W, CARD_H), (24, 18, 12))
    d = ImageDraw.Draw(img)
    pts = [(n["x"], n["y"]) for n in nodes]
    samples = catmull_rom(pts, 20)
    for (x0, y0), (x1, y1) in zip(samples, samples[1:]):
        d.line((x0, y0, x1, y1), fill=(180, 140, 40), width=4)
    ds = neighbor_distances(nodes)
    print(f"  {name}: min {min(ds):.1f}  mean {sum(ds)/len(ds):.1f}  max {max(ds):.1f}  coin {coin_size}")
    for n, dist in zip(nodes, ds + [None]):
        r = (coin_size + 8) / 2 if n["v"] == 0 else coin_size / 2
        d.ellipse((n["x"] - r, n["y"] - r, n["x"] + r, n["y"] + r), outline=(240, 200, 80), width=2)
        label = f"{n['v']}{'R' if n['rot'] else ''}"
        d.text((n["x"] - 8, n["y"] - 6), label, fill=(255, 230, 160))
        if dist is not None:
            mx = (n["x"] + nodes[nodes.index(n) + 1]["x"]) / 2
            my = (n["y"] + nodes[nodes.index(n) + 1]["y"]) / 2
            d.text((mx, my), f"{dist:.0f}", fill=(120, 200, 120))
    Path("/tmp/echelle_debug").mkdir(parents=True, exist_ok=True)
    img.save(Path("/tmp/echelle_debug") / f"{name}.png")


CAPTIONS = {
    "01_donjon_serpentin.png": "Donjon (ton fond) — S ouvert, pièces rondes, pas plus régulier",
    "02_donjon_enroule.png": "Donjon (ton fond) — S plus enroulé, virages plus ronds",
    "03_tresor_moitie.png": "Salle au trésor — bas = coffres, haut = porte, 0 sur le seuil",
    "04_tresor_cotes.png": "Salle au trésor de côté — coffres à gauche, escalier à droite",
    "05_mine_galerie.png": "Mine d’or — galerie et wagonnet, S ouvert",
    "06_mine_filon.png": "Mine d’or — filons dans la roche, S un peu plus ample",
}


def write_apercu(paths: list[Path]) -> None:
    cards = "\n".join(
        f"""
      <figure>
        <img src="{p.name}" alt="{p.stem}">
        <figcaption>{CAPTIONS.get(p.name, p.stem)}</figcaption>
      </figure>"""
        for p in paths
    )
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Échelle de l'OR — 6 propositions</title>
<style>
  :root {{ background:#1a1410; color:#f3e6c4; font-family:Georgia, serif; }}
  body {{ max-width:1400px; margin:32px auto; padding:0 20px; }}
  h1 {{ font-weight:normal; letter-spacing:.04em; }}
  p {{ color:#cbb98a; max-width:72ch; line-height:1.45; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:22px; margin-top:28px; }}
  figure {{ margin:0; background:#0e0b08; border:1px solid #5a4520; border-radius:8px; overflow:hidden; }}
  img {{ width:100%; height:auto; display:block; }}
  figcaption {{ padding:10px 12px 14px; font-size:14px; color:#e8d5a0; }}
</style>
</head>
<body>
  <h1>Échelle de l'OR — 6 propositions</h1>
  <p>Pièces <strong>rondes</strong>, piste en <strong>serpentin</strong> (pas la grille carrée).
  Chiffres espacés à pas plus régulier. Côté adverse tourné de 180°.
  Deux cartes sur ton donjon, deux salles au trésor avec l’autre côté distinct,
  deux mines.</p>
  <div class="grid">{cards}
  </div>
</body>
</html>
"""
    (OUT / "apercu.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    coin = load_blank_coin()
    fond_or = Image.open(ROOT / "Fond_Carte_Or.jpg")
    fond_moitie = Image.open(FONDS / "fond_tresor_moitie.jpg")
    fond_cotes = Image.open(FONDS / "fond_tresor_cotes.jpg")
    fond_galerie = Image.open(FONDS / "fond_mine_galerie.jpg")
    fond_filon = Image.open(FONDS / "fond_mine_filon.jpg")

    jobs = [
        (
            "01_donjon_serpentin.png",
            fond_or,
            "ouvert",
            0.50,
            0.50,
            dict(ribbon="gold", desired=102, path_width=18, vignette=0.24, warmth=1.0),
        ),
        (
            "02_donjon_enroule.png",
            fond_or,
            "enroule",
            0.50,
            0.50,
            dict(ribbon="glow", desired=100, path_width=18, vignette=0.20, warmth=1.03),
        ),
        (
            "03_tresor_moitie.png",
            fond_moitie,
            "seuil",
            0.50,
            0.490,
            dict(ribbon="glow", desired=98, path_width=18, vignette=0.10, warmth=1.04),
        ),
        (
            "04_tresor_cotes.png",
            fond_cotes,
            "arche",
            0.50,
            0.50,
            dict(ribbon="glow", desired=96, path_width=16, vignette=0.08, warmth=1.02),
        ),
        (
            "05_mine_galerie.png",
            fond_galerie,
            "mine_galerie",
            0.50,
            0.48,
            dict(ribbon="gold", desired=100, path_width=18, vignette=0.16, warmth=1.05),
        ),
        (
            "06_mine_filon.png",
            fond_filon,
            "mine_filon",
            0.50,
            0.50,
            dict(ribbon="glow", desired=100, path_width=18, vignette=0.14, warmth=1.06),
        ),
    ]

    written: list[Path] = []
    for name, bg, shape, cx, cy, kw in jobs:
        nodes = layout_from_waypoints(CARD_W, CARD_H, SHAPES[shape], cx=cx, cy=cy)
        desired = kw.pop("desired")
        coin_size = fit_coin_size(nodes, desired, gap=20)
        zero_size = coin_size + 14
        debug_layout(nodes, coin_size, Path(name).stem)
        img = compose_card(
            bg, nodes, coin, coin_size=coin_size, zero_size=zero_size, **kw
        )
        dest = OUT / name
        img.save(dest, "PNG", optimize=True)
        written.append(dest)
        print(f"wrote {dest} {img.size}")

    write_apercu(written)
    print("apercu.html ok")


if __name__ == "__main__":
    main()
