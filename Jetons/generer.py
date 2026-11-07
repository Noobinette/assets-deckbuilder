#!/usr/bin/env python3
"""Logos PIXEL et GLORY pour le centre d'un jeton de poker.

Découpe les lettres du logo du jeu, les remet à l'échelle en pixels
entiers (le dessin reste net) et décline quatre couleurs de chaque mot.
Fond transparent, carré 2400×2400 : le site demande au moins 600×600.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
LOGO = ROOT.parent / "vitrine" / "img" / "logo.png"
TAILLE = 2400
ECHELLE = 5

# Centre du jeton (ivoire du configurateur). Sert seulement à la planche.
CREME = (243, 236, 216, 255)
ENCRE = (28, 20, 16, 255)

# Dégradés calés sur les pixels du logo : du creux vers l'arête claire.
OR = (
    (0.00, (118, 76, 26)),
    (0.30, (164, 110, 40)),
    (0.58, (200, 146, 58)),
    (0.80, (228, 178, 84)),
    (1.00, (250, 214, 132)),
)
BLEU = (
    (0.00, (12, 32, 72)),
    (0.35, (26, 58, 118)),
    (0.65, (42, 86, 162)),
    (1.00, (104, 152, 208)),
)
ROUGE = (
    (0.00, (72, 10, 8)),
    (0.40, (118, 20, 14)),
    (0.70, (156, 36, 26)),
    (1.00, (198, 78, 58)),
)
# Remplissage d'origine, pour l'échange des couleurs (le filet or reste).
BLEU_PATE = (
    (0.00, (8, 24, 52)),
    (0.50, (16, 42, 76)),
    (1.00, (28, 58, 96)),
)
ROUGE_PATE = (
    (0.00, (64, 8, 6)),
    (0.45, (104, 16, 12)),
    (1.00, (156, 40, 28)),
)


def luminance(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def role(r: int, g: int, b: int, a: int) -> str:
    if a == 0:
        return "vide"
    # Filet noir et ombre douce (alpha 80) : on les garde tels quels.
    if a < 250 or max(r, g, b) < 36:
        return "trait"
    if r > 85 and g > 48 and r > b + 28 and g > b + 8 and g > int(r * 0.38):
        return "or"
    if b > r + 6 and b + 6 >= g:
        return "bleu"
    if r > b + 12 and r > g:
        return "rouge"
    if r >= g and r > b:
        return "or"
    return "trait"


def resserrer(crop: Image.Image) -> Image.Image:
    pixels = crop.load()
    xs, ys = [], []
    for y in range(crop.height):
        for x in range(crop.width):
            if pixels[x, y][3] > 0:
                xs.append(x)
                ys.append(y)
    return crop.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def bande(logo: Image.Image, y0: int, y1: int) -> Image.Image:
    return resserrer(logo.crop((0, y0, logo.width, y1)))


def oter_of(glory: Image.Image) -> Image.Image:
    """Le bas du « OF » touche le haut du G. On ne garde que le G à gauche."""
    img = glory.copy()
    pixels = img.load()
    for y in range(8):
        for x in range(110, img.width):
            pixels[x, y] = (0, 0, 0, 0)
    return resserrer(img)


def rampe(t: float, stops: tuple) -> tuple[int, int, int]:
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1 or t1 == stops[-1][0]:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))
    return stops[-1][1]


def recolore(src: Image.Image, mode: str) -> Image.Image:
    """mode : couleurs | or | bleu | rouge | pate-rouge | pate-bleu."""
    if mode == "couleurs":
        return src.copy()

    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, dp = src.load(), out.load()
    pleins = []
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            kind = role(r, g, b, a)
            if kind == "vide":
                continue
            if kind == "trait":
                dp[x, y] = (r, g, b, a)
                continue
            if mode == "pate-rouge" and kind == "or":
                dp[x, y] = (r, g, b, a)
                continue
            if mode == "pate-bleu" and kind == "or":
                dp[x, y] = (r, g, b, a)
                continue
            pleins.append((x, y, luminance(r, g, b), a))

    if not pleins:
        return out
    lums = sorted(p[2] for p in pleins)
    lo = lums[max(0, int(len(lums) * 0.04))]
    hi = lums[min(len(lums) - 1, int(len(lums) * 0.96))]
    if hi <= lo:
        hi = lo + 1
    stops = {
        "or": OR,
        "bleu": BLEU,
        "rouge": ROUGE,
        "pate-rouge": ROUGE_PATE,
        "pate-bleu": BLEU_PATE,
    }[mode]
    for x, y, lum, a in pleins:
        t = (lum - lo) / (hi - lo)
        dp[x, y] = (*rampe(t, stops), 255 if a > 200 else a)
    return out


def poser(sprite: Image.Image) -> Image.Image:
    grand = sprite.resize(
        (sprite.width * ECHELLE, sprite.height * ECHELLE),
        Image.Resampling.NEAREST,
    )
    toile = Image.new("RGBA", (TAILLE, TAILLE), (0, 0, 0, 0))
    toile.paste(
        grand,
        ((TAILLE - grand.width) // 2, (TAILLE - grand.height) // 2),
        grand,
    )
    return toile


def disque(logo: Image.Image, diametre: int) -> Image.Image:
    """Le mot sur l'ivoire du jeton, pour juger le contraste."""
    img = Image.new("RGBA", (diametre, diametre), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, diametre - 1, diametre - 1), fill=CREME)
    # Le fichier uploadé est carré : on le réduit pour qu'il tienne dans le cercle.
    marge = int(diametre * 0.06)
    cote = diametre - 2 * marge
    logo_petit = logo.resize((cote, cote), Image.Resampling.NEAREST)
    img.paste(logo_petit, (marge, marge), logo_petit)
    return img


def planche(paires: list[tuple[str, Image.Image, Image.Image]]) -> Image.Image:
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Bold.ttf", 42)
    fonte_petit = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Regular.ttf", 28)
    disque_px = 760
    pad = 48
    titre_h = 130
    cols = len(paires)
    largeur = pad + cols * (disque_px + pad)
    hauteur = pad + titre_h + 2 * (disque_px + 70) + pad
    img = Image.new("RGBA", (largeur, hauteur), (246, 241, 230, 255))
    draw = ImageDraw.Draw(img)
    legendes = (
        ("Pixel", ""),
        ("Glory", ""),
    )
    for col, (nom, _a, _b) in enumerate(paires):
        x = pad + col * (disque_px + pad)
        draw.text((x, 36), nom, font=fonte, fill=ENCRE[:3])
    y0 = pad + titre_h
    for row, (mot, sous) in enumerate(legendes):
        y = y0 + row * (disque_px + 70)
        draw.text((pad, y - 58), mot, font=fonte, fill=ENCRE[:3])
        if sous:
            draw.text((pad + 160, y - 50), sous, font=fonte_petit, fill=(90, 70, 50))
        for col, (_nom, pix, glo) in enumerate(paires):
            x = pad + col * (disque_px + pad)
            src = pix if row == 0 else glo
            pastille = disque(src, disque_px)
            img.paste(pastille, (x, y), pastille)
    return img


def main() -> None:
    logo = Image.open(LOGO).convert("RGBA")
    pixel = bande(logo, 18, 132)
    # 196 : le haut du G. Le bas du OF est encore là, au centre : on le retire.
    glory = oter_of(bande(logo, 196, 307))
    print(f"PIXEL {pixel.size}  GLORY {glory.size}")

    variantes = (
        ("couleurs", "Pixel en bleu, Glory en rouge, filet or. La paire du logo.", "couleurs", "couleurs"),
        ("or", "Les deux mots en or, filet sombre. Lisibles sur l'ivoire.", "or", "or"),
        ("bleu-rouge", "La couleur du logo sans or : Pixel bleu, Glory rouge.", "bleu", "rouge"),
        ("inverse", "Couleurs échangées pour le dos : Pixel rouge, Glory bleu, filet or gardé.", "pate-rouge", "pate-bleu"),
    )
    fichiers = {
        "couleurs": ("pixel-bleu-or.png", "glory-rouge-or.png"),
        "or": ("pixel-or.png", "glory-or.png"),
        "bleu-rouge": ("pixel-bleu.png", "glory-rouge.png"),
        "inverse": ("pixel-rouge-or.png", "glory-bleu-or.png"),
    }
    titres = {
        "couleurs": "Couleurs du logo",
        "or": "Or",
        "bleu-rouge": "Bleu et rouge",
        "inverse": "Dos inversé",
    }

    paires = []
    for cle, _texte, mode_p, mode_g in variantes:
        nom_p, nom_g = fichiers[cle]
        img_p = poser(recolore(pixel, mode_p))
        img_g = poser(recolore(glory, mode_g))
        img_p.save(ROOT / nom_p, optimize=True)
        img_g.save(ROOT / nom_g, optimize=True)
        print(nom_p, img_p.size, (ROOT / nom_p).stat().st_size)
        print(nom_g, img_g.size, (ROOT / nom_g).stat().st_size)
        paires.append((titres[cle], img_p, img_g))

    brute = planche(paires)
    fond = Image.new("RGB", brute.size, (246, 241, 230))
    fond.paste(brute, mask=brute.split()[-1])
    fond.save(ROOT / "planche.jpg", quality=90)
    print("planche.jpg")


if __name__ == "__main__":
    main()
