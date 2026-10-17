#!/usr/bin/env python3
"""Génère 5 propositions de carte « échelle de l'OR ».

Une seule piste partagée : 6 → 0 → 6.
Chaque joueur lit SES chiffres à l'endroit (côté adversaire tourné de 180°).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "propositions"
FONDS = ROOT / "fonds"
CARD_W, CARD_H = 750, 1050

# Chiffres pixel 9×11, style de la pièce 0 des cartes du jeu.
# 1 = encre, 0 = vide
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
    """Retire le magenta de fond, avec anti-aliasing sur les bords."""
    rgba = im.convert("RGBA")
    arr = np.asarray(rgba).astype(np.float32)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    # Distance au magenta (255, 0, 255)
    dist = np.sqrt((r - 255) ** 2 + (g - 0) ** 2 + (b - 255) ** 2)
    # Aussi : pixels très saturés magenta (R et B hauts, G bas)
    mag = np.minimum(r, b) - g
    alpha = np.clip((dist - thresh) / 40.0, 0, 1) * a
    alpha = np.where(mag > 80, alpha * 0.15, alpha)
    # Masque circulaire de sécurité : garde le disque central
    h, w = alpha.shape
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h / 2.0, w / 2.0
    rad = min(h, w) * 0.46
    circ = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rad ** 2
    # À l'intérieur du disque, on force opaque sauf vrai magenta
    inside = circ & (dist > 55)
    alpha = np.where(inside, np.maximum(alpha, 220), alpha)
    alpha = np.where(dist < 45, 0, alpha)
    arr[..., 3] = alpha
    out = Image.fromarray(arr.astype(np.uint8), "RGBA")
    # Recadre au bounding box
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def extract_game_coin() -> Image.Image:
    """Pièce d'or des cartes du jeu, sans le chiffre."""
    src = Image.open(REPO / "Cartes" / "Mine_d_or.png").convert("RGBA")
    # La pièce est en haut à gauche, ~88 px
    crop = src.crop((8, 8, 118, 118))
    arr = np.asarray(crop).astype(np.float32)
    h, w = arr.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h / 2.0 - 1, w / 2.0 - 1
    rad = min(h, w) * 0.48
    circ = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rad ** 2
    # Fond hors cercle → transparent
    arr[..., 3] = np.where(circ, 255, 0)
    # Inpaint grossier du « 0 » central : pixels très sombres au centre
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    luma = 0.3 * r + 0.59 * g + 0.11 * b
    inner = ((xx - cx) ** 2 + (yy - cy) ** 2) <= (rad * 0.42) ** 2
    ink = inner & (luma < 80) & circ
    # Couleur or moyenne de l'anneau autour du chiffre
    ring = inner & (~ink) & (luma > 120)
    if ring.any():
        fill = arr[ring].mean(axis=0)
    else:
        fill = np.array([212, 168, 48, 255], dtype=np.float32)
    # Un peu de variation
    noise = np.random.RandomState(3).randn(*arr.shape[:2], 1) * 4
    filled = np.clip(fill + noise, 0, 255)
    arr[ink] = filled[ink]
    # Légère flou local pour fondre le patch
    coin = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return coin


def load_blank_coin() -> Image.Image:
    """Pièce générée (centre vide) + pièce du jeu, on privilégie le centre vide."""
    generated = FONDS / "piece_or_pixel.jpg"
    coin = chromakey_magenta(Image.open(generated))
    # Recentre dans un carré
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


def make_parchemin(size: int, value: int, rotate: bool, scale: int) -> Image.Image:
    """Case parchemin façon EchelleGold, chiffre pixel."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = max(2, size // 18)
    # ombre
    d.rounded_rectangle((m + 3, m + 4, size - m + 3, size - m + 4), radius=size // 8, fill=(40, 22, 8, 120))
    # bordure or
    d.rounded_rectangle((m, m, size - m, size - m), radius=size // 8, fill=(92, 62, 22, 255))
    d.rounded_rectangle((m + 3, m + 3, size - m - 3, size - m - 3), radius=size // 9, fill=(214, 186, 128, 255))
    d.rounded_rectangle((m + 7, m + 7, size - m - 7, size - m - 7), radius=size // 11, fill=(236, 214, 164, 255))
    # fibre
    for i in range(m + 10, size - m - 10, max(4, size // 16)):
        d.line((m + 10, i, size - m - 10, i + 1), fill=(200, 172, 120, 70), width=1)
    return stamp_number(img, value, rotate, scale)


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


def polyline_samples(points: list[tuple[float, float]], step: float = 2.0) -> list[tuple[float, float]]:
    """Segments droits, coins arrondis par densité — pas de boucle de spline."""
    out: list[tuple[float, float]] = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dist = max(1.0, math.hypot(x1 - x0, y1 - y0))
        n = max(2, int(dist / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append(points[-1])
    return out


def draw_ribbon(
    canvas: Image.Image,
    points: list[tuple[float, float]],
    width: float,
    style: str = "gold",
    curved: bool = True,
) -> None:
    samples = catmull_rom(points, n_per=28) if curved else polyline_samples(points, step=1.8)
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
    else:  # gold
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


def layout_smooth(w: int, h: int) -> list[dict]:
    """S fluide : 6-5-4 en haut, colonne, 1-0-1, colonne, 4-5-6 en bas."""
    # (nx, ny, value, rotate) — rotate True = côté adversaire (haut de carte)
    raw = [
        (0.72, 0.125, 6, True),
        (0.50, 0.118, 5, True),
        (0.28, 0.175, 4, True),
        (0.22, 0.310, 3, True),
        (0.22, 0.430, 2, True),
        (0.32, 0.500, 1, True),
        (0.50, 0.500, 0, False),
        (0.68, 0.500, 1, False),
        (0.78, 0.570, 2, False),
        (0.78, 0.690, 3, False),
        (0.72, 0.825, 4, False),
        (0.50, 0.882, 5, False),
        (0.28, 0.875, 6, False),
    ]
    return [{"x": nx * w, "y": ny * h, "v": v, "rot": rot} for nx, ny, v, rot in raw]


def layout_manuscrit(w: int, h: int) -> list[dict]:
    """S en créneau, fidèle au croquis : 5-6 / 4-3-2 / 1-0-1 / 2-3-4 / 6-5.

    Colonne gauche = 4-3-2 adversaire, barre centrale, colonne droite = 2-3-4 joueur.
    """
    raw = [
        (0.74, 0.125, 6, True),
        (0.50, 0.125, 5, True),
        (0.26, 0.125, 4, True),
        (0.26, 0.250, 3, True),
        (0.26, 0.375, 2, True),
        (0.26, 0.500, 1, True),
        (0.50, 0.500, 0, False),
        (0.74, 0.500, 1, False),
        (0.74, 0.625, 2, False),
        (0.74, 0.750, 3, False),
        (0.74, 0.875, 4, False),
        (0.50, 0.875, 5, False),
        (0.26, 0.875, 6, False),
    ]
    return [{"x": nx * w, "y": ny * h, "v": v, "rot": rot} for nx, ny, v, rot in raw]


def layout_serré(w: int, h: int) -> list[dict]:
    """S un peu plus vertical, pièces plus groupées au centre."""
    raw = [
        (0.68, 0.135, 6, True),
        (0.50, 0.110, 5, True),
        (0.32, 0.155, 4, True),
        (0.24, 0.290, 3, True),
        (0.26, 0.410, 2, True),
        (0.36, 0.500, 1, True),
        (0.50, 0.500, 0, False),
        (0.64, 0.500, 1, False),
        (0.74, 0.590, 2, False),
        (0.76, 0.710, 3, False),
        (0.68, 0.845, 4, False),
        (0.50, 0.890, 5, False),
        (0.32, 0.865, 6, False),
    ]
    return [{"x": nx * w, "y": ny * h, "v": v, "rot": rot} for nx, ny, v, rot in raw]


def paste_shadow(canvas: Image.Image, size: int, cx: float, cy: float, strength=90) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    r = size / 2
    off = size * 0.06
    d.ellipse((cx - r + off, cy - r + off * 1.4, cx + r + off, cy + r + off * 1.4), fill=(0, 0, 0, strength))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.08))
    canvas.alpha_composite(shadow)


def compose_card(
    background: Image.Image,
    nodes: list[dict],
    coin_src: Image.Image,
    *,
    ribbon: str = "gold",
    coin_size: int = 108,
    zero_size: int = 124,
    digit_scale: int = 6,
    vignette: float = 0.35,
    warmth: float = 1.0,
    path_width: float = 22,
    curved: bool = True,
    marker: str = "coin",
) -> Image.Image:
    bg = cover_crop(background, CARD_W, CARD_H).convert("RGBA")
    if warmth != 1.0:
        bg = ImageEnhance.Color(bg).enhance(warmth)
        bg = ImageEnhance.Contrast(bg).enhance(1.05)

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

    pts = [(n["x"], n["y"]) for n in nodes]
    draw_ribbon(canvas, pts, path_width, style=ribbon, curved=curved)

    for n in nodes:
        size = zero_size if n["v"] == 0 else coin_size
        paste_shadow(canvas, size, n["x"], n["y"], strength=110 if marker == "parchemin" else 90)
        ds = digit_scale if n["v"] != 0 else digit_scale + 1
        if marker == "parchemin":
            stamped = make_parchemin(size, n["v"], n["rot"], ds)
        else:
            coin = coin_src.resize((size, size), Image.Resampling.LANCZOS)
            stamped = stamp_number(coin, n["v"], n["rot"], ds)
        x, y = int(n["x"] - size / 2), int(n["y"] - size / 2)
        canvas.alpha_composite(stamped, (x, y))

    return canvas.convert("RGB")


CAPTIONS = {
    "01_donjon_serpentin.png": "Donjon — S fluide, fond fourni, pièces d’or",
    "02_donjon_manuscrit.png": "Donjon — S en créneau (croquis à la main)",
    "03_donjon_piste.png": "Donjon — même fond, piste pierre/or un peu plus serrée",
    "04_salle_tresor.png": "Salle du trésor — autre fond, même S fluide",
    "05_table_bois.png": "Table de bois — cases parchemin, chiffres inversés",
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
<title>Échelle de l'OR — propositions</title>
<style>
  :root {{ background:#1a1410; color:#f3e6c4; font-family:Georgia, serif; }}
  body {{ max-width:1200px; margin:32px auto; padding:0 20px; }}
  h1 {{ font-weight:normal; letter-spacing:.04em; }}
  p {{ color:#cbb98a; max-width:70ch; line-height:1.45; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:22px; margin-top:28px; }}
  figure {{ margin:0; background:#0e0b08; border:1px solid #5a4520; border-radius:8px; overflow:hidden; }}
  img {{ width:100%; height:auto; display:block; }}
  figcaption {{ padding:10px 12px 14px; font-size:14px; color:#e8d5a0; }}
</style>
</head>
<body>
  <h1>Échelle de l'OR — 5 propositions</h1>
  <p>Piste unique 6 → 0 → 6. Les chiffres du côté adverse sont tournés de 180°,
  pour que chaque joueur lise les siens à l'endroit. On y déplace une pièce d'or.</p>
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
    fond_tresor = Image.open(FONDS / "fond_salle_tresor.jpg")
    fond_bois = Image.open(FONDS / "fond_table_bois.jpg")

    jobs = [
        (
            "01_donjon_serpentin.png",
            fond_or,
            layout_smooth(CARD_W, CARD_H),
            dict(ribbon="gold", coin_size=112, zero_size=128, path_width=20, vignette=0.26, warmth=1.0),
        ),
        (
            "02_donjon_manuscrit.png",
            fond_or,
            layout_manuscrit(CARD_W, CARD_H),
            dict(ribbon="glow", coin_size=108, zero_size=124, path_width=18, vignette=0.28, warmth=1.04, curved=False),
        ),
        (
            "03_donjon_piste.png",
            fond_or,
            layout_serré(CARD_W, CARD_H),
            dict(ribbon="stone", coin_size=110, zero_size=126, path_width=26, vignette=0.20, warmth=0.96),
        ),
        (
            "04_salle_tresor.png",
            fond_tresor,
            layout_smooth(CARD_W, CARD_H),
            dict(ribbon="glow", coin_size=112, zero_size=128, path_width=20, vignette=0.16, warmth=1.06),
        ),
        (
            "05_table_bois.png",
            fond_bois,
            layout_manuscrit(CARD_W, CARD_H),
            dict(
                ribbon="gold",
                coin_size=104,
                zero_size=118,
                path_width=16,
                vignette=0.10,
                warmth=1.0,
                curved=False,
                marker="parchemin",
            ),
        ),
    ]

    written: list[Path] = []
    for name, bg, nodes, kw in jobs:
        img = compose_card(bg, nodes, coin, **kw)
        dest = OUT / name
        img.save(dest, "PNG", optimize=True)
        written.append(dest)
        print(f"wrote {dest} {img.size}")

    write_apercu(written)
    print("apercu.html ok")


if __name__ == "__main__":
    main()
