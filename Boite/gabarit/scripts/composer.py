#!/usr/bin/env python3
"""Compose l'exemple de boîte Pixel of Glory sur le gabarit, plus les sources."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "Boite" / "gabarit"
FACES = OUT / "faces"
SOURCES = OUT / "sources"
WEB = OUT / "web"

GABARIT = Path(
    "/home/ubuntu/.cursor/projects/agent-repos-assets-deckbuilder/assets/"
    "67af3084-6f06-437a-8f64-8de9f9b6decb.png"
)
ART = Path("/opt/cursor/artifacts/assets")
LOGO = ROOT / "DosCartes" / "logos" / "03e_titre_trois_lignesV3.png"
LOGO_LIGNE = ROOT / "Agarder" / "logos" / "propositions" / "01_or_ligne.jpg"

SCALE = 5  # gabarit 1024×999 → 5120×4995
DPI_PRINT = 150
CM_W = 70

# Panneaux utiles (coords gabarit 1024×999), d'après flood-fill.
PANELS = {
    "rabat_couvercle": (303, 16, 720, 145),
    "dessus": (308, 150, 715, 429),
    "oreille_gauche": (176, 160, 303, 418),
    "oreille_droite": (720, 160, 847, 418),
    "dos": (303, 433, 720, 569),
    "dessous": (301, 574, 722, 851),
    "cote_int_g": (160, 581, 296, 843),
    "cote_int_d": (727, 581, 863, 843),
    "cote_ext_g": (16, 583, 148, 841),
    "cote_ext_d": (875, 583, 1007, 841),
    "avant": (304, 855, 719, 982),
}


def cover(im: Image.Image, w: int, h: int, bias_y: float = 0.45) -> Image.Image:
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = max(w, int(round(iw * scale))), max(h, int(round(ih * scale)))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, (nw - w) // 2)
    y = int(round((nh - h) * bias_y))
    y = max(0, min(nh - h, y))
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


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
    rgb = arr[:, :, :3].astype(np.int16)
    lum = rgb.sum(axis=2)
    alpha = np.clip((lum - 18) * 4, 0, 255).astype(np.uint8)
    arr[:, :, 3] = alpha
    out = Image.fromarray(arr)
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def logo_from_white(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(np.float32)
    dist = np.sqrt(
        (rgb[:, :, 0] - 255) ** 2 + (rgb[:, :, 1] - 255) ** 2 + (rgb[:, :, 2] - 255) ** 2
    )
    alpha = np.clip((dist - 28) / 24, 0, 1)
    arr[:, :, 3] = (alpha * 255).astype(np.uint8)
    out = Image.fromarray(arr)
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def fit_logo(logo: Image.Image, box_w: int, box_h: int, margin: float = 0.14) -> Image.Image:
    max_w, max_h = int(box_w * (1 - 2 * margin)), int(box_h * (1 - 2 * margin))
    lw, lh = logo.size
    scale = min(max_w / lw, max_h / lh)
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    return logo.resize((nw, nh), Image.Resampling.LANCZOS)


def paste_centered(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sw, sh = src.size
    x = x0 + (w - sw) // 2
    y = y0 + (h - sh) // 2
    dst.alpha_composite(src, (x, y))


def interior_masks(gabarit: Image.Image) -> list[tuple[tuple[int, int, int, int], np.ndarray]]:
    """Masques des zones intérieures (panneaux) du gabarit source."""
    arr = np.array(gabarit.convert("RGBA"))
    walls = arr[:, :, 3] > 20
    h, w = walls.shape
    # légère dilatation pour fermer les traits
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
            if cx < minx:
                minx = cx
            if cx > maxx:
                maxx = cx
            if cy < miny:
                miny = cy
            if cy > maxy:
                maxy = cy
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
    ww, hh = x1b - x0b, y1b - y0b
    if ww > 450 or hh > 400:
        return None
    cx = (x0b + x1b) / 2
    cy = (y0b + y1b) / 2
    if cy < 148:
        return "rabat_couvercle"
    best, best_d = None, 1e9
    for name, (x0, y0, x1, y1) in PANELS.items():
        if x0 - 36 <= cx <= x1 + 36 and y0 - 36 <= cy <= y1 + 36:
            d = abs(cx - (x0 + x1) / 2) + abs(cy - (y0 + y1) / 2)
            if d < best_d:
                best, best_d = name, d
    return best


def side_panel(stone: Image.Image, logo: Image.Image, w: int, h: int, rotate: str) -> Image.Image:
    """Panneau latéral : pierre + logo, rotation pour lecture une fois plié."""
    base = cover(stone, w, h, bias_y=0.5)
    # logo à l'endroit dans l'espace « debout » (haut du carton = bord extérieur)
    standing_w, standing_h = h, w  # après pliage : hauteur boîte × profondeur
    # On dessine d'abord comme si le panneau était vu debout, puis on rabat dans le filet.
    upright = cover(stone, standing_w, standing_h, bias_y=0.5)
    lg = fit_logo(logo, standing_w, standing_h, margin=0.08)
    paste_centered(upright, lg, (0, 0, standing_w, standing_h))
    if rotate == "left":
        # bord extérieur à gauche dans le filet → haut du logo vers la gauche
        return upright.rotate(90, expand=True).resize((w, h), Image.Resampling.LANCZOS)
    if rotate == "right":
        return upright.rotate(-90, expand=True).resize((w, h), Image.Resampling.LANCZOS)
    return cover(upright, w, h)


def save_jpeg(im: Image.Image, path: Path, quality: int = 90, dpi: int = DPI_PRINT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = im.convert("RGB")
    rgb.save(path, "JPEG", quality=quality, subsampling=0, optimize=True, dpi=(dpi, dpi))


def save_png(im: Image.Image, path: Path, dpi: int = DPI_PRINT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True, dpi=(dpi, dpi))


def main() -> None:
    for d in (OUT, FACES, SOURCES, WEB):
        d.mkdir(parents=True, exist_ok=True)

    gabarit = Image.open(GABARIT).convert("RGBA")
    gw, gh = gabarit.size

    scene1 = Image.open(ART / "necromancer-knight-landscape-01.jpg")
    scene2 = Image.open(ART / "necromancer-knight-landscape-02.jpg")
    scene3 = Image.open(ART / "necromancer-knight-landscape-03.jpg")
    scene4 = Image.open(ART / "necromancer-knight-landscape-04.jpg")
    scene5 = Image.open(ART / "necromancer-knight-landscape-05.jpg")
    dessous_src = Image.open(ART / "box-bottom-castle-night.jpg")
    stone = Image.open(ART / "box-side-stone.jpg")
    parch_raw = Image.open(ART / "parchemin-overlay-chroma-v2.jpg")

    scenes = [scene1, scene2, scene3, scene4, scene5]

    # --- sources paysage 70 cm de large, 16:9, 150 dpi ---
    print_w = int(round(CM_W / 2.54 * DPI_PRINT))
    print_h = int(round(print_w * 9 / 16))
    for i, sc in enumerate(scenes, 1):
        out = sc.resize((print_w, print_h), Image.Resampling.LANCZOS)
        save_jpeg(out, SOURCES / f"paysage_0{i}.jpg")
        save_jpeg(out.resize((1920, 1080), Image.Resampling.LANCZOS), WEB / f"paysage_0{i}.jpg", quality=86)

    parch = chroma_magenta(parch_raw)
    parch_print = parch.resize((print_w, print_h), Image.Resampling.LANCZOS)
    save_png(parch_print, SOURCES / "parchemin.png")
    save_png(parch.resize((1920, 1080), Image.Resampling.LANCZOS), WEB / "parchemin.png")

    # overlays aperçu
    for i in range(1, 6):
        base = Image.open(WEB / f"paysage_0{i}.jpg").convert("RGBA")
        ov = Image.open(WEB / "parchemin.png")
        comp = Image.alpha_composite(base, ov)
        save_jpeg(comp, WEB / f"overlay_0{i}.jpg", quality=86)

    save_jpeg(dessous_src.resize((print_w, print_h), Image.Resampling.LANCZOS), SOURCES / "dessous_chateau.jpg")
    save_jpeg(stone, SOURCES / "cote_pierre.jpg")

    logo = logo_from_black(LOGO)
    logo_ligne = logo_from_white(LOGO_LIGNE)

    # --- faces détourées ---
    dx0, dy0, dx1, dy1 = PANELS["dessus"]
    face_dessus = cover(scene1, (dx1 - dx0) * SCALE, (dy1 - dy0) * SCALE, bias_y=0.42)
    save_jpeg(face_dessus, FACES / "dessus.jpg")

    bx0, by0, bx1, by1 = PANELS["dessous"]
    face_dessous = cover(dessous_src, (bx1 - bx0) * SCALE, (by1 - by0) * SCALE, bias_y=0.55)
    save_jpeg(face_dessous, FACES / "dessous.jpg")

    cx0, cy0, cx1, cy1 = PANELS["cote_int_g"]
    cw, ch = (cx1 - cx0) * SCALE, (cy1 - cy0) * SCALE
    face_g = side_panel(stone, logo, cw, ch, "left")
    face_d = side_panel(stone, logo, cw, ch, "right")
    save_jpeg(face_g, FACES / "cote_gauche.jpg")
    save_jpeg(face_d, FACES / "cote_droit.jpg")

    ax0, ay0, ax1, ay1 = PANELS["avant"]
    aw, ah = (ax1 - ax0) * SCALE, (ay1 - ay0) * SCALE
    face_avant = cover(stone.rotate(90, expand=True), aw, ah, bias_y=0.5)
    lg_h = fit_logo(logo_ligne, aw, ah, margin=0.10)
    paste_centered(face_avant, lg_h, (0, 0, aw, ah))
    save_jpeg(face_avant, FACES / "avant.jpg")

    # --- filet haute résol ---
    W, H = gw * SCALE, gh * SCALE
    canvas = Image.new("RGBA", (W, H), (8, 8, 12, 255))
    print("masks…")
    masks = interior_masks(gabarit)

    art_for = {
        "dessus": scene1,
        "dessous": dessous_src,
        "rabat_couvercle": scene1,
        "dos": scene1,
        "avant": None,
        "oreille_gauche": None,
        "oreille_droite": None,
        "cote_int_g": None,
        "cote_int_d": None,
        "cote_ext_g": None,
        "cote_ext_d": None,
    }

    for bbox, mask in masks:
        name = which_panel(bbox)
        if not name:
            continue
        x0, y0, x1, y1 = bbox
        pw, ph = (x1 - x0 + 1) * SCALE, (y1 - y0 + 1) * SCALE
        sx0, sy0 = x0 * SCALE, y0 * SCALE

        if name == "dessus":
            tile = cover(scene1, pw, ph, bias_y=0.42)
        elif name == "dessous":
            tile = cover(dessous_src, pw, ph, bias_y=0.55)
        elif name == "rabat_couvercle":
            # bande ciel / lune + logo horizontal
            tile = cover(scene1, pw, ph, bias_y=0.12)
            dim = ImageEnhance.Brightness(tile).enhance(0.72)
            tile = dim
            lg_h = fit_logo(logo_ligne, pw, ph, margin=0.12)
            paste_centered(tile, lg_h, (0, 0, pw, ph))
        elif name == "dos":
            tile = cover(scene1, pw, ph, bias_y=0.78)
            tile = ImageEnhance.Brightness(tile).enhance(0.8)
            lg_h = fit_logo(logo_ligne, pw, ph, margin=0.14)
            paste_centered(tile, lg_h, (0, 0, pw, ph))
        elif name == "avant":
            tile = cover(stone.rotate(90, expand=True), pw, ph)
            lg_h = fit_logo(logo_ligne, pw, ph, margin=0.10)
            paste_centered(tile, lg_h, (0, 0, pw, ph))
        elif name in ("oreille_gauche", "cote_int_g", "cote_ext_g"):
            tile = side_panel(stone, logo, pw, ph, "left")
        elif name in ("oreille_droite", "cote_int_d", "cote_ext_d"):
            tile = side_panel(stone, logo, pw, ph, "right")
        else:
            continue

        m = Image.fromarray(mask).resize((W, H), Image.Resampling.NEAREST)
        m = m.crop((sx0, sy0, sx0 + pw, sy0 + ph)).convert("L")
        # un peu de dilatation pour recouvrir le fond perdu interne
        m = m.filter(ImageFilter.MaxFilter(11))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(tile, (sx0, sy0), tile)
        # appliquer le masque du panneau
        la = np.array(layer)
        ma = np.array(Image.new("L", (W, H), 0))
        ma_crop = np.array(m)
        ma[sy0 : sy0 + ph, sx0 : sx0 + pw] = ma_crop
        la[:, :, 3] = (la[:, :, 3].astype(np.float32) * (ma.astype(np.float32) / 255.0)).astype(np.uint8)
        canvas.alpha_composite(Image.fromarray(la))
        print("  painted", name, bbox)

    # overlay du gabarit (traits)
    lines = gabarit.resize((W, H), Image.Resampling.NEAREST)
    # rendre les traits plus lisibles
    larr = np.array(lines)
    vis = larr[:, :, 3] > 20
    larr[vis, 3] = 255
    lines = Image.fromarray(larr)
    canvas.alpha_composite(lines)

    net = canvas.convert("RGB")
    save_jpeg(net, OUT / "exemple_net.jpg", quality=88, dpi=DPI_PRINT)
    save_jpeg(net.resize((1280, 1248), Image.Resampling.LANCZOS), WEB / "exemple_net.jpg", quality=85)

    # --- mockup : faces vues une fois la boîte montée ---
    pad = 36
    tw = 980
    top = cover(scene1, tw, int(tw * 280 / 410), bias_y=0.42)
    bot = cover(dessous_src, tw, int(tw * 278 / 422), bias_y=0.55)
    front_h = max(88, int(tw * 128 / 416))
    front = cover(stone.rotate(90, expand=True), tw, front_h)
    paste_centered(front, fit_logo(logo_ligne, tw, front_h, 0.10), (0, 0, tw, front_h))
    # côté debout : profondeur × hauteur, logo empilé à l'endroit
    sw = int(tw * 263 / 410)
    sh = max(110, int(tw * 137 / 410))
    side_up = cover(stone, sw, sh, bias_y=0.5)
    paste_centered(side_up, fit_logo(logo, sw, sh, 0.08), (0, 0, sw, sh))

    mw = pad * 3 + sw + tw
    mh = pad * 4 + top.size[1] + front_h + bot.size[1]
    mock = Image.new("RGB", (mw, mh), (18, 16, 22))
    mock.paste(side_up.convert("RGB"), (pad, pad + (top.size[1] - sh) // 2))
    mock.paste(top.convert("RGB"), (pad * 2 + sw, pad))
    mock.paste(front.convert("RGB"), (pad * 2 + sw, pad * 2 + top.size[1]))
    mock.paste(bot.convert("RGB"), (pad * 2 + sw, pad * 3 + top.size[1] + front_h))
    cote_hi = cover(stone, 1600, 840, bias_y=0.5)
    paste_centered(cote_hi, fit_logo(logo, 1600, 840, 0.08), (0, 0, 1600, 840))
    save_jpeg(cote_hi, FACES / "cote_debout.jpg")

    save_jpeg(mock, OUT / "exemple_mockup.jpg", quality=88)
    save_jpeg(
        mock.resize((1200, int(1200 * mh / mw)), Image.Resampling.LANCZOS),
        WEB / "exemple_mockup.jpg",
        quality=85,
    )

    # crops 70×35 cm (2:1) des 5 paysages
    print_h_21 = print_w // 2
    crop_dir = SOURCES / "print_70x35"
    for i in range(1, 6):
        src = Image.open(SOURCES / f"paysage_0{i}.jpg")
        w, h = src.size
        y = max(0, (h - print_h_21) // 2)
        save_jpeg(src.crop((0, y, w, y + print_h_21)), crop_dir / f"paysage_0{i}_70x35.jpg")
    parch21 = parch_print.crop((0, y, print_w, y + print_h_21))
    save_png(parch21, crop_dir / "parchemin_70x35.png")

    gabarit.convert("RGBA").save(OUT / "gabarit_source.png")
    print("done", OUT)


if __name__ == "__main__":
    main()
