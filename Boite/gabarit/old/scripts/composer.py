#!/usr/bin/env python3
"""Compose l'exemple de boîte Pixel of Glory sur le gabarit, plus les sources."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None

def repo_root() -> Path:
    p = Path(__file__).resolve()
    for cand in [p, *p.parents]:
        if (cand / "AGENTS.md").exists() and (cand / "Boite").is_dir():
            return cand
    raise RuntimeError("repo root not found")


ROOT = repo_root()
OUT = ROOT / "Boite" / "gabarit"
FACES = OUT / "old" / "faces"
SOURCES = OUT / "old" / "sources"
WEB = OUT / "old" / "web"
PRINT = OUT / "old" / "print"
FONTS = ROOT / "Presentation" / "fonts"

GABARIT = Path(
    "/home/ubuntu/.cursor/projects/agent-repos-assets-deckbuilder/assets/"
    "67af3084-6f06-437a-8f64-8de9f9b6decb.png"
)
ART = Path("/opt/cursor/artifacts/assets")
LOGO = ROOT / "DosCartes" / "logos" / "03e_titre_trois_lignesV3.png"
LOGO_LIGNE = ROOT / "Agarder" / "logos" / "propositions" / "01_or_ligne.jpg"

# Gabarit 1024 px. SCALE 10 → dessus ~4070 px ≈ 69 cm à 150 dpi / 34,5 cm à 300 dpi.
SCALE = 10
DPI_PRINT = 300
CM_W = 70
LIFT = 1.10

PANELS = {
    "rabat_couvercle": (303, 16, 720, 145),
    "dessus": (308, 150, 715, 429),
    "oreille_gauche": (176, 160, 303, 418),
    "oreille_droite": (720, 160, 847, 418),
    "dos": (303, 433, 720, 569),
    "flap_dos_g": (197, 441, 299, 562),
    "flap_dos_d": (724, 441, 826, 562),
    "dessous": (301, 574, 722, 851),
    "cote_int_g": (160, 581, 296, 843),
    "cote_int_d": (727, 581, 863, 843),
    "cote_ext_g": (16, 583, 148, 841),
    "cote_ext_d": (875, 583, 1007, 841),
    "avant": (304, 855, 719, 982),
    "flap_avant_g": (199, 862, 301, 982),
    "flap_avant_d": (723, 862, 824, 982),
}

ROT180 = {
    "rabat_couvercle",
    "oreille_gauche",
    "oreille_droite",
    "dessous",
    "cote_ext_g",
    "cote_ext_d",
    "avant",
    "flap_avant_g",
    "flap_avant_d",
}

GOLD = (232, 196, 106, 255)
GOLD_DK = (120, 82, 28, 255)
INK = (62, 38, 18, 255)
INK_SOFT = (86, 54, 28, 255)
CREAM = (245, 228, 186, 255)
PLAQUE = (18, 14, 22, 210)


def cover(im: Image.Image, w: int, h: int, bias_y: float = 0.45) -> Image.Image:
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = max(w, int(round(iw * scale))), max(h, int(round(ih * scale)))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, (nw - w) // 2)
    y = int(round((nh - h) * bias_y))
    y = max(0, min(nh - h, y))
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


def lift(im: Image.Image, factor: float = LIFT) -> Image.Image:
    return ImageEnhance.Brightness(im.convert("RGBA")).enhance(factor)


CADRE_FT_SRC = 28
CADRE_FT = 8 * SCALE  # ~80 px à SCALE 10, proche du cadre déjà présent sur B


def strip_cadre(im: Image.Image, ft: int = CADRE_FT_SRC) -> Image.Image:
    """Retire le cadre d'origine des visuels pour n'en poser qu'un seul ensuite."""
    im = im.convert("RGBA")
    w, h = im.size
    ft = min(ft, w // 8, h // 8)
    return im.crop((ft, ft, w - ft, h - ft))


def cadre_slices(cadre: Image.Image, ft_src: int = CADRE_FT_SRC) -> dict[str, Image.Image]:
    c = cadre.convert("RGBA")
    cw, ch = c.size
    ft = min(ft_src, cw // 4, ch // 4)
    return {
        "tl": c.crop((0, 0, ft, ft)),
        "tr": c.crop((cw - ft, 0, cw, ft)),
        "bl": c.crop((0, ch - ft, ft, ch)),
        "br": c.crop((cw - ft, ch - ft, cw, ch)),
        "top": c.crop((ft, 0, cw - ft, ft)),
        "bot": c.crop((ft, ch - ft, cw - ft, ch)),
        "left": c.crop((0, ft, ft, ch - ft)),
        "right": c.crop((cw - ft, ft, cw, ch - ft)),
    }


def apply_cadre(tile: Image.Image, slices: dict[str, Image.Image], ft: int) -> Image.Image:
    """Pose le cadre bois (celui du dessus) sur les 4 bords du panneau."""
    tile = tile.convert("RGBA")
    w, h = tile.size
    ft = int(ft)
    ft = min(ft, max(4, w // 5), max(4, h // 5))
    if w < ft * 2 + 8 or h < ft * 2 + 8:
        return tile

    def rz(im: Image.Image, size: tuple[int, int]) -> Image.Image:
        return im.resize(size, Image.Resampling.LANCZOS)

    top = rz(slices["top"], (max(1, w - 2 * ft), ft))
    bot = rz(slices["bot"], (max(1, w - 2 * ft), ft))
    left = rz(slices["left"], (ft, max(1, h - 2 * ft)))
    right = rz(slices["right"], (ft, max(1, h - 2 * ft)))
    tl = rz(slices["tl"], (ft, ft))
    tr = rz(slices["tr"], (ft, ft))
    bl = rz(slices["bl"], (ft, ft))
    br = rz(slices["br"], (ft, ft))
    tile.paste(top, (ft, 0))
    tile.paste(bot, (ft, h - ft))
    tile.paste(left, (0, ft))
    tile.paste(right, (w - ft, ft))
    tile.paste(tl, (0, 0))
    tile.paste(tr, (w - ft, 0))
    tile.paste(bl, (0, h - ft))
    tile.paste(br, (w - ft, h - ft))
    return tile


def frame_panel(
    scene: Image.Image,
    w: int,
    h: int,
    slices: dict[str, Image.Image],
    ft: int,
    bias_y: float = 0.45,
    decorate=None,
) -> Image.Image:
    """Scène recadrée à l'intérieur, un seul cadre bois sur les 4 bords."""
    ft = max(8, min(int(ft), w // 6, h // 6))
    inner = lift(cover(scene, w - 2 * ft, h - 2 * ft, bias_y=bias_y))
    if decorate is not None:
        inner = decorate(inner)
    tile = Image.new("RGBA", (w, h), (28, 20, 16, 255))
    tile.paste(inner.convert("RGBA"), (ft, ft))
    return apply_cadre(tile, slices, ft)


def fill_interior_black(
    rgb: Image.Image, gabarit: Image.Image, slices: dict[str, Image.Image]
) -> Image.Image:
    """Bouche uniquement les trous de fond (encoches) isolés dans le filet."""
    gw, gh = gabarit.size
    small = np.array(rgb.resize((gw, gh), Image.Resampling.BOX))
    bg = np.abs(small.astype(np.int16) - np.array([10, 10, 14])).sum(axis=2) < 24
    sh, sw = bg.shape
    ext = np.zeros((sh, sw), dtype=bool)
    stack = [(0, 0)]
    ext[0, 0] = True
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < sh and 0 <= nx < sw and not ext[ny, nx] and bg[ny, nx]:
                ext[ny, nx] = True
                stack.append((ny, nx))
    holes = bg & ~ext
    if not holes.any():
        return rgb
    arr = np.array(rgb.convert("RGB"))
    H, W = arr.shape[:2]
    hole_hi = np.array(
        Image.fromarray(holes.astype(np.uint8) * 255).resize((W, H), Image.Resampling.NEAREST)
    ) > 127
    wood = np.array(slices["top"].convert("RGB"))
    row = wood[wood.shape[0] // 2]
    ys, xs = np.where(hole_hi)
    arr[ys, xs] = row[xs % len(row)]
    return Image.fromarray(arr)


def chroma_magenta(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    dist = np.sqrt((r - 255) ** 2 + g ** 2 + (b - 255) ** 2)
    magenta = (r > 150) & (b > 150) & (g < 110)
    alpha = np.clip((dist - 80) / 24, 0, 1)
    alpha = np.where(magenta, 0.0, alpha)
    aimg = Image.fromarray((alpha * 255).astype(np.uint8))
    aimg = aimg.filter(ImageFilter.MinFilter(5))
    arr[:, :, 3] = np.array(aimg)
    return Image.fromarray(arr)


def logo_from_black(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    lum = arr[:, :, :3].astype(np.int16).sum(axis=2)
    arr[:, :, 3] = np.clip((lum - 18) * 4, 0, 255).astype(np.uint8)
    out = Image.fromarray(arr)
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def logo_from_white(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(np.float32)
    dist = np.sqrt((rgb[:, :, 0] - 255) ** 2 + (rgb[:, :, 1] - 255) ** 2 + (rgb[:, :, 2] - 255) ** 2)
    arr[:, :, 3] = (np.clip((dist - 28) / 24, 0, 1) * 255).astype(np.uint8)
    out = Image.fromarray(arr)
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def fit_logo(logo: Image.Image, box_w: int, box_h: int, margin: float = 0.14) -> Image.Image:
    max_w, max_h = int(box_w * (1 - 2 * margin)), int(box_h * (1 - 2 * margin))
    lw, lh = logo.size
    scale = min(max_w / lw, max_h / lh)
    return logo.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.Resampling.LANCZOS)


def paste_centered(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sw, sh = src.size
    dst.alpha_composite(src, (x0 + (w - sw) // 2, y0 + (h - sh) // 2))


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=fnt)
    return x1 - x0, y1 - y0


def draw_outlined(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, outline, width: int = 2) -> None:
    x, y = xy
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text((x, y), text, font=fnt, fill=fill)


def wrap_words(draw, text: str, fnt, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def nameplate(text: str, panel_h: int) -> Image.Image:
    fnt = font("PixelifySans.ttf", max(32, int(panel_h * 0.042)))
    dummy = Image.new("RGBA", (8, 8))
    d = ImageDraw.Draw(dummy)
    tw, th = text_size(d, text, fnt)
    pad_x, pad_y = int(th * 0.7), int(th * 0.28)
    w, h = tw + pad_x * 2, th + pad_y * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=max(4, th // 4), fill=PLAQUE, outline=GOLD, width=max(3, th // 10))
    x0, y0, _, _ = dr.textbbox((0, 0), text, font=fnt)
    draw_outlined(dr, (pad_x - x0, pad_y - y0), text, fnt, GOLD, GOLD_DK, width=max(2, th // 12))
    return im


def decorate_cover(inner: Image.Image, logo: Image.Image) -> Image.Image:
    """Logo + DAVID / JEAN sur la scène intérieure du dessus."""
    tile = inner.convert("RGBA")
    w, h = tile.size
    lg = fit_logo(logo, int(w * 0.42), int(h * 0.28), margin=0.0)
    tile.alpha_composite(lg, ((w - lg.size[0]) // 2, int(h * 0.04)))
    david = nameplate("DAVID", h)
    jean = nameplate("JEAN", h)
    tile.alpha_composite(david, (int(w * 0.22) - david.size[0] // 2, int(h * 0.84)))
    tile.alpha_composite(jean, (int(w * 0.80) - jean.size[0] // 2, int(h * 0.83)))
    return tile


def compose_back(scene: Image.Image, parch: Image.Image, w: int, h: int) -> Image.Image:
    """Dos / dessous (E) : illustration + parchemin 90s + texte."""
    tile = lift(cover(scene, w, h, bias_y=0.50))
    pw, ph = int(w * 0.93), int(h * 0.86)
    panel = parch.resize((pw, ph), Image.Resampling.LANCZOS)
    # intérieur du cadre : assez loin des enrouleurs et des coins or
    ix0, iy0 = int(pw * 0.20), int(ph * 0.28)
    ix1, iy1 = int(pw * 0.80), int(ph * 0.76)
    inner_w = ix1 - ix0
    dr = ImageDraw.Draw(panel)
    s = max(1.0, pw / 1100)
    f_head = font("Cinzel.ttf", max(16, int(22 * s)))
    f_stat = font("Cinzel.ttf", max(16, int(22 * s)))
    f_body = font("SourceSerif4.ttf", max(16, int(20 * s)))
    f_feat = font("Cinzel.ttf", max(17, int(22 * s)))
    f_tiny = font("PixelifySans.ttf", max(12, int(14 * s)))

    y = iy0
    line1 = "CONFIGURATION MINIMALE   ·   2 joueurs"
    line2 = "DURÉE   ·   30 à 45 minutes"
    w1, h1 = text_size(dr, line1, f_head)
    w2, h2 = text_size(dr, line2, f_stat)
    dr.text((ix0 + (inner_w - w1) // 2, y), line1, font=f_head, fill=GOLD_DK)
    y += h1 + int(4 * s)
    dr.text((ix0 + (inner_w - w2) // 2, y), line2, font=f_stat, fill=INK)
    y += h2 + int(10 * s)
    dr.line((ix0 + int(8 * s), y, ix1 - int(8 * s), y), fill=GOLD_DK, width=max(1, int(s)))
    y += int(12 * s)

    paragraphs = [
        "Affrontez votre adversaire dans un duel de cartes fantasy intense et hautement stratégique ! Construisez votre deck, élaborez vos plans de bataille et menez vos troupes à l'assaut des citadelles ennemies.",
        "Ici, pas de mana : chaque carte peut être jouée, mais tout a un coût. Saurez-vous gérer votre or sans en payer le prix fort ? Utilisez vos plans pour dicter l'initiative, déploiez des créatures mythiques et gérez la dette pour épuiser le deck de votre rival avant qu'il ne détruise vos terres.",
        "Le combat pour la gloire commence maintenant !",
    ]
    lh = text_size(dr, "Ag", f_body)[1] + int(5 * s)
    for i, para in enumerate(paragraphs):
        lines = wrap_words(dr, para, f_body, inner_w)
        for line in lines:
            if y + lh > iy1 - int(52 * s):
                break
            color = GOLD_DK if i == 2 else INK
            dr.text((ix0, y), line, font=f_body, fill=color)
            y += lh
        y += int(8 * s)

    feat = "PLUS DE 650 CARTES DIFFÉRENTES"
    fw, fh = text_size(dr, feat, f_feat)
    fy = min(iy1 - fh - int(22 * s), y + int(6 * s))
    bx0 = ix0 + (inner_w - fw) // 2 - int(14 * s)
    by0 = fy - int(5 * s)
    dr.rounded_rectangle(
        (bx0, by0, bx0 + fw + int(28 * s), by0 + fh + int(12 * s)),
        radius=int(5 * s),
        outline=GOLD_DK,
        width=max(2, int(s)),
    )
    dr.text((ix0 + (inner_w - fw) // 2, fy), feat, font=f_feat, fill=GOLD_DK)
    easter = "ÉDITION BIG BOX  ·  16-BIT FANTASY"
    ew, _ = text_size(dr, easter, f_tiny)
    dr.text((ix0 + (inner_w - ew) // 2, by0 + fh + int(14 * s)), easter, font=f_tiny, fill=INK_SOFT)

    tile.alpha_composite(panel, ((w - pw) // 2, (h - ph) // 2))
    return tile


def decorate_bande(inner: Image.Image, logo_ligne: Image.Image) -> Image.Image:
    tile = inner.convert("RGBA")
    w, h = tile.size
    paste_centered(tile, fit_logo(logo_ligne, w, h, margin=0.12), (0, 0, w, h))
    return tile


def pierre_logo(stone: Image.Image, logo_ligne: Image.Image, w: int, h: int) -> Image.Image:
    inner = lift(cover(stone.rotate(90, expand=True), w, h, 0.5))
    return decorate_bande(inner, logo_ligne)


def interior_masks(gabarit: Image.Image) -> list[tuple[tuple[int, int, int, int], np.ndarray]]:
    arr = np.array(gabarit.convert("RGBA"))
    walls = arr[:, :, 3] > 20
    h, w = walls.shape
    walls2 = walls.copy()
    walls2[1:, :] |= walls[:-1, :]
    walls2[:-1, :] |= walls[1:, :]
    walls2[:, 1:] |= walls[:, :-1]
    walls2[:, :-1] |= walls[:, 1:]

    ext = np.zeros((h, w), dtype=bool)
    stack = [(0, 0)]
    ext[0, 0] = True
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not ext[ny, nx] and not walls2[ny, nx]:
                ext[ny, nx] = True
                stack.append((ny, nx))
    interior = ~ext & ~walls2
    vis = np.zeros_like(interior)
    ys, xs = np.where(interior)
    out = []
    for y, x in zip(ys, xs):
        if vis[y, x]:
            continue
        q = [(y, x)]
        vis[y, x] = True
        minx = maxx = x
        miny = maxy = y
        pix = []
        while q:
            cy, cx = q.pop()
            pix.append((cy, cx))
            minx, maxx = min(minx, cx), max(maxx, cx)
            miny, maxy = min(miny, cy), max(maxy, cy)
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < h and 0 <= nx < w and interior[ny, nx] and not vis[ny, nx]:
                    vis[ny, nx] = True
                    q.append((ny, nx))
        n = len(pix)
        ww, hh = maxx - minx + 1, maxy - miny + 1
        if n < 2500 or n / (ww * hh) < 0.45:
            continue
        mask = np.zeros((h, w), dtype=np.uint8)
        for cy, cx in pix:
            mask[cy, cx] = 255
        out.append(((minx, miny, maxx, maxy), mask))
    return out


def which_panel(bbox: tuple[int, int, int, int]) -> str | None:
    x0b, y0b, x1b, y1b = bbox
    if (x1b - x0b) > 450 or (y1b - y0b) > 400:
        return None
    cx = (x0b + x1b) / 2
    cy = (y0b + y1b) / 2
    if cy < 148:
        return "rabat_couvercle"
    best, best_d = None, 1e9
    for name, (x0, y0, x1, y1) in PANELS.items():
        if x0 - 20 <= cx <= x1 + 20 and y0 - 20 <= cy <= y1 + 20:
            d = abs(cx - (x0 + x1) / 2) + abs(cy - (y0 + y1) / 2)
            if d < best_d:
                best, best_d = name, d
    return best


def side_panel(stone: Image.Image, logo: Image.Image, w: int, h: int, rotate: str) -> Image.Image:
    standing_w, standing_h = h, w
    upright = lift(cover(stone, standing_w, standing_h, bias_y=0.5))
    paste_centered(upright, fit_logo(logo, standing_w, standing_h, margin=0.08), (0, 0, standing_w, standing_h))
    if rotate == "left":
        return upright.rotate(90, expand=True).resize((w, h), Image.Resampling.LANCZOS)
    if rotate == "right":
        return upright.rotate(-90, expand=True).resize((w, h), Image.Resampling.LANCZOS)
    return cover(upright, w, h)


def save_jpeg(im: Image.Image, path: Path, quality: int = 90, dpi: int = DPI_PRINT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(path, "JPEG", quality=quality, subsampling=0, optimize=True, dpi=(dpi, dpi))


def save_png(im: Image.Image, path: Path, dpi: int = DPI_PRINT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True, dpi=(dpi, dpi))


def paint_net(gabarit: Image.Image, masks, arts: dict, slices, logo, logo_ligne) -> Image.Image:
    gw, gh = gabarit.size
    W, H = gw * SCALE, gh * SCALE
    canvas = Image.new("RGBA", (W, H), (10, 10, 14, 255))
    pad_g = 6
    pad = pad_g * SCALE
    ft0 = CADRE_FT
    for bbox, mask in masks:
        name = which_panel(bbox)
        if not name:
            continue
        x0, y0, x1, y1 = bbox
        pw, ph = (x1 - x0 + 1) * SCALE, (y1 - y0 + 1) * SCALE
        sx0, sy0 = x0 * SCALE, y0 * SCALE
        x0p, y0p = max(0, x0 - pad_g), max(0, y0 - pad_g)
        x1p, y1p = min(gw - 1, x1 + pad_g), min(gh - 1, y1 + pad_g)
        pl, pt = (x0 - x0p) * SCALE, (y0 - y0p) * SCALE
        pr, pb = (x1p - x1) * SCALE, (y1p - y1) * SCALE
        tw, th = pw + pl + pr, ph + pt + pb
        ft = ft0 + pad

        def make(scene, bias, deco=None):
            return frame_panel(scene, tw, th, slices, ft, bias, deco)

        if name == "dessus":
            tile = make(arts["scene_b"], 0.42, lambda im: decorate_cover(im, logo))
        elif name == "dessous":
            tile = make(arts["scene_e"], 0.50)
        elif name == "rabat_couvercle":
            tile = make(arts["scene_magie"], 0.42, lambda im: decorate_bande(im, logo_ligne))
        elif name == "dos":
            tile = make(arts["scene_choc"], 0.48, lambda im: decorate_bande(im, logo_ligne))
        elif name == "avant":
            tile = make(arts["scene_apres"], 0.62, lambda im: decorate_bande(im, logo_ligne))
        elif name in ("flap_dos_g", "flap_dos_d", "flap_avant_g", "flap_avant_d"):
            tile = make(arts["scene_choc"], 0.50)
        elif name in ("oreille_gauche", "oreille_droite"):
            tile = make(arts["scene_magie"], 0.42)
        elif name in ("cote_int_g", "cote_int_d"):
            tile = make(arts["scene_choc"], 0.48)
        elif name in ("cote_ext_g", "cote_ext_d"):
            tile = make(arts["scene_apres"], 0.55)
        else:
            continue

        if name in ROT180:
            tile = tile.rotate(180)
        if tile.size != (tw, th):
            tile = tile.resize((tw, th), Image.Resampling.LANCZOS)

        msmall = Image.fromarray(mask).crop((x0p, y0p, x1p + 1, y1p + 1))
        msmall = msmall.filter(ImageFilter.MaxFilter(pad_g * 2 + 1))
        mlocal = msmall.resize((tw, th), Image.Resampling.NEAREST)
        tarr = np.array(tile.convert("RGBA"))
        tarr[:, :, 3] = (tarr[:, :, 3].astype(np.float32) * np.array(mlocal).astype(np.float32) / 255.0).astype(np.uint8)
        canvas.alpha_composite(Image.fromarray(tarr), (sx0 - pl, sy0 - pt))
        print("  painted", name, bbox, f"{tw}x{th}")

    out = canvas.convert("RGB")
    out = fill_interior_black(out, gabarit, slices)
    return out


def mockup(top: Image.Image, bot: Image.Image, front: Image.Image, stone, logo) -> Image.Image:
    pad, tw = 36, 980
    top = top.resize((tw, int(tw * top.size[1] / top.size[0])), Image.Resampling.LANCZOS)
    bot = bot.resize((tw, int(tw * bot.size[1] / bot.size[0])), Image.Resampling.LANCZOS)
    front_h = max(88, int(tw * 128 / 416))
    front = front.resize((tw, front_h), Image.Resampling.LANCZOS)
    sw = int(tw * 263 / 410)
    sh = max(110, int(tw * 137 / 410))
    side_up = lift(cover(stone, sw, sh, bias_y=0.5))
    paste_centered(side_up, fit_logo(logo, sw, sh, 0.08), (0, 0, sw, sh))
    mw = pad * 3 + sw + tw
    mh = pad * 4 + top.size[1] + front_h + bot.size[1]
    mock = Image.new("RGB", (mw, mh), (18, 16, 22))
    mock.paste(side_up.convert("RGB"), (pad, pad + (top.size[1] - sh) // 2))
    mock.paste(top.convert("RGB"), (pad * 2 + sw, pad))
    mock.paste(front.convert("RGB"), (pad * 2 + sw, pad * 2 + top.size[1]))
    mock.paste(bot.convert("RGB"), (pad * 2 + sw, pad * 3 + top.size[1] + front_h))
    return mock


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    gabarit = Image.open(GABARIT).convert("RGBA")
    scene1 = Image.open(ART / "necromancer-knight-landscape-01.jpg")
    e_chevalier = Image.open(ART / "e-victoire-chevalier.jpg")
    bande_magie = Image.open(ART / "bande-magie.jpg")
    bande_choc = Image.open(ART / "bande-choc.jpg")
    bande_apres = Image.open(ART / "bande-apres.jpg")

    logo = logo_from_black(LOGO)
    logo_ligne = logo_from_white(LOGO_LIGNE)

    print("compose…")
    slices = cadre_slices(scene1)
    arts = {
        "scene_b": strip_cadre(scene1, 28),
        "scene_e": strip_cadre(e_chevalier, 28),
        "scene_magie": strip_cadre(bande_magie, 42),
        "scene_choc": strip_cadre(bande_choc, 42),
        "scene_apres": strip_cadre(bande_apres, 42),
    }

    print("masks…")
    masks = interior_masks(gabarit)
    print("net…")
    net_c = paint_net(gabarit, masks, arts, slices, logo, logo_ligne)
    save_jpeg(net_c, OUT / "boite.jpg", quality=86)
    print("done", net_c.size)


if __name__ == "__main__":
    main()
