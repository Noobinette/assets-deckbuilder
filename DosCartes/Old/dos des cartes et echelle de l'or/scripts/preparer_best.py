#!/usr/bin/env python3
"""Recadre les 8 cartes Best, agrandit les pièces de 02, exporte les alt. 03."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BEST = ROOT / "Best"
ORIG = BEST / "original"
ALT = BEST / "alternative"
CARD_W, CARD_H = 750, 1050
RADIUS = 28
MARGIN = 22  # espace égal autour du cadre

spec = importlib.util.spec_from_file_location(
    "generer_echelle_or", Path(__file__).with_name("generer_echelle_or.py")
)
geo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo)


def sample_rim(arr: np.ndarray, band: int = 6) -> tuple[int, int, int]:
    rim = np.concatenate(
        [
            arr[:band].reshape(-1, 3),
            arr[-band:].reshape(-1, 3),
            arr[:, :band].reshape(-1, 3),
            arr[:, -band:].reshape(-1, 3),
        ]
    )
    return tuple(int(x) for x in rim.mean(0))


def sample_gold(arr: np.ndarray) -> tuple[int, int, int]:
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    gold = (r > 120) & (r > g + 8) & (r > b + 25) & (g > 50)
    if gold.sum() < 80:
        return (196, 148, 64)
    mean = arr[gold].mean(0)
    return tuple(int(x) for x in mean)


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


def rebalance(im: Image.Image, margin: int = MARGIN, frame: bool = True) -> Image.Image:
    """Réduit un peu, centre, mêmes marges, cadre or complet."""
    im = im.convert("RGB")
    arr = np.asarray(im)
    fill = sample_rim(arr)
    gold = sample_gold(arr)
    inner_w, inner_h = CARD_W - 2 * margin, CARD_H - 2 * margin
    src_w, src_h = im.size
    scale = min(inner_w / src_w, inner_h / src_h)
    nw, nh = max(1, round(src_w * scale)), max(1, round(src_h * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (CARD_W, CARD_H), fill)
    x = (CARD_W - nw) // 2
    y = (CARD_H - nh) // 2
    canvas.paste(resized, (x, y))

    if frame:
        d = ImageDraw.Draw(canvas)
        dark = tuple(max(0, c - 70) for c in gold)
        light = tuple(min(255, c + 40) for c in gold)
        # double filet, même inset des 4 côtés
        m1, m2, m3 = 8, 12, 16
        d.rounded_rectangle((m1, m1, CARD_W - 1 - m1, CARD_H - 1 - m1), radius=22, outline=dark, width=3)
        d.rounded_rectangle((m2, m2, CARD_W - 1 - m2, CARD_H - 1 - m2), radius=18, outline=light, width=2)
        d.rounded_rectangle((m3, m3, CARD_W - 1 - m3, CARD_H - 1 - m3), radius=16, outline=dark, width=1)
    return round_card(canvas)


def contain_poker(im: Image.Image, margin: int = MARGIN, frame: bool = True) -> Image.Image:
    """Fit entier (3:4 → poker) avec marges, sans couper le cadre."""
    im = im.convert("RGB")
    arr = np.asarray(im)
    fill = sample_rim(arr)
    gold = sample_gold(arr)
    inner_w, inner_h = CARD_W - 2 * margin, CARD_H - 2 * margin
    src_w, src_h = im.size
    scale = min(inner_w / src_w, inner_h / src_h)
    nw, nh = max(1, round(src_w * scale)), max(1, round(src_h * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (CARD_W, CARD_H), fill)
    canvas.paste(resized, ((CARD_W - nw) // 2, (CARD_H - nh) // 2))
    if frame:
        d = ImageDraw.Draw(canvas)
        dark = tuple(max(0, c - 70) for c in gold)
        light = tuple(min(255, c + 40) for c in gold)
        d.rounded_rectangle((8, 8, CARD_W - 9, CARD_H - 9), radius=22, outline=dark, width=3)
        d.rounded_rectangle((12, 12, CARD_W - 13, CARD_H - 13), radius=18, outline=light, width=2)
    return round_card(canvas)


# Centres mesurés sur 02_donjon_enroule (cy, cx) → valeur, rotation adversaire
COINS_02 = [
    (98.5, 298.2, 4, True),
    (94.2, 464.5, 5, True),
    (215.7, 612.3, 6, True),
    (197.6, 174.0, 3, True),
    (341.8, 135.1, 2, True),
    (477.2, 217.1, 1, True),
    (499.3, 344.9, 0, False),
    (533.7, 517.5, 1, False),
    (655.9, 608.2, 2, False),
    (833.9, 560.4, 3, False),
    (926.5, 407.3, 4, False),
    (905.8, 249.8, 5, False),
    (800.7, 137.4, 6, False),
]


def bigger_coins_02(src: Image.Image) -> Image.Image:
    """Repose des pièces plus grandes (chiffres plus lisibles) sur le donjon.

    Pas de nouveau ruban : on couvre les anciennes pièces, plein cadre.
    """
    canvas = src.convert("RGBA")
    coin_src = geo.chromakey_magenta(Image.open(ROOT / "Old" / "fonds" / "piece_or_pixel.jpg"))
    w, h = coin_src.size
    side = max(w, h)
    blank = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    blank.paste(coin_src, ((side - w) // 2, (side - h) // 2), coin_src)

    # Légèrement plus grandes, sans se chevaucher. 0 un peu plus large.
    coin_size, zero_size, digit = 118, 136, 7
    # Recalage visuel : le 0 d’origine a un gros médaillon décalé à droite.
    coins = []
    for cy, cx, val, rot in COINS_02:
        if val == 0:
            cx += 22
            cy += 2
        elif val == 1 and not rot:
            cx += 14
            cy += 6
        elif val == 2 and not rot:
            cx += 12
            cy += 10
        coins.append((cy, cx, val, rot))
    cover = ImageDraw.Draw(canvas)
    for cy, cx, val, rot in coins:
        size = zero_size if val == 0 else coin_size
        extra = 16 if val == 0 else 5
        r = size / 2 + extra
        # or : recouvre l’ancienne pièce / le médaillon sans manger le ruban
        cover.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(186, 132, 36, 255))
    coins.sort(key=lambda t: 1 if t[2] == 0 else 0)
    for cy, cx, val, rot in coins:
        size = zero_size if val == 0 else coin_size
        if val == 0:
            geo.draw_zero_medallion(canvas, cx, cy, size)
        geo.paste_shadow(canvas, size, cx, cy, strength=100)
        coin = blank.resize((size, size), Image.Resampling.LANCZOS)
        stamped = geo.stamp_number(coin, val, rot, digit if val != 0 else digit + 1)
        canvas.alpha_composite(stamped, (int(cx - size / 2), int(cy - size / 2)))
    return round_card(canvas.convert("RGB"))


ALTS = [
    ("alt03_a_pixel_ofglory.jpg", "03a_pixel_ofglory.png", "PIXEL / OF GLORY"),
    ("alt03_b_pixelof_glory.jpg", "03b_pixelof_glory.png", "PIXEL OF / GLORY"),
    ("alt03_c_oneline.jpg", "03c_une_ligne.png", "PIXEL OF GLORY (une ligne)"),
    ("alt03_d_logo_laurier.jpg", "03d_logo_laurier.png", "Logo laurier + titre"),
    ("alt03_e_three_lines.jpg", "03e_trois_lignes.png", "PIXEL / OF / GLORY"),
]


def main() -> None:
    ORIG.mkdir(parents=True, exist_ok=True)
    ALT.mkdir(parents=True, exist_ok=True)
    assets = Path("/opt/cursor/artifacts/assets")

    backs = [
        "01_brun_or_laurier.png",
        "03_brun_bleu_rouge.png",
        "07_bois_or.png",
        "10_pourpre_or_seul.png",
        "13_ivoire_or.png",
        "17_ivoire_bleu_laurier.png",
        "29_titre.png",
    ]
    for name in backs:
        src = ORIG / name
        im = Image.open(src)
        out = rebalance(im, margin=MARGIN, frame=True)
        dest = BEST / name
        out.save(dest, "PNG", optimize=True)
        print("rebalance", dest, out.size)

    # 02 : pièces plus grosses, plein cadre (pas de passe-partout brun)
    raw02 = Image.open(ORIG / "02_donjon_enroule.png")
    rec02 = bigger_coins_02(raw02)
    rec02.save(BEST / "02_donjon_enroule.png", "PNG", optimize=True)
    rec02.save(ALT / "02_donjon_enroule_pieces_grosses.png", "PNG", optimize=True)
    print("02 bigger coins")

    for src_name, dest_name, cap in ALTS:
        src = assets / src_name
        im = Image.open(src)
        out = contain_poker(im, margin=20, frame=True)
        dest = ALT / dest_name
        out.save(dest, "PNG", optimize=True)
        print("alt", cap, dest, out.size)

    print("ok")


if __name__ == "__main__":
    main()
