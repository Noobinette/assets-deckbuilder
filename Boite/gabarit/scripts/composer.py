#!/usr/bin/env python3
"""Compose l'exemple de boîte Pixel of Glory sur le gabarit, plus les sources."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

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

SCALE = 5
DPI_PRINT = 150
CM_W = 70
LIFT = 1.10  # léger éclaircissement

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

# A, C, E, F, H : 180° sur le filet. G et D inchangés.
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
    dst.alpha_composite(src, (x0 + (w - sw) // 2, y0 + (h - sh) // 2))


def bande_logo(bg: Image.Image, logo_ligne: Image.Image, w: int, h: int, bias_y: float = 0.5) -> Image.Image:
    tile = lift(cover(bg, w, h, bias_y=bias_y))
    paste_centered(tile, fit_logo(logo_ligne, w, h, margin=0.12), (0, 0, w, h))
    return tile


def pierre_logo(stone: Image.Image, logo_ligne: Image.Image, w: int, h: int) -> Image.Image:
    return bande_logo(stone.rotate(90, expand=True), logo_ligne, w, h, 0.5)


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
    ww, hh = x1b - x0b, y1b - y0b
    if ww > 450 or hh > 400:
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


def paint_net(gabarit: Image.Image, masks, arts: dict, stone, logo, logo_ligne) -> Image.Image:
    gw, gh = gabarit.size
    W, H = gw * SCALE, gh * SCALE
    canvas = Image.new("RGBA", (W, H), (10, 10, 14, 255))
    for bbox, mask in masks:
        name = which_panel(bbox)
        if not name:
            continue
        x0, y0, x1, y1 = bbox
        pw, ph = (x1 - x0 + 1) * SCALE, (y1 - y0 + 1) * SCALE
        sx0, sy0 = x0 * SCALE, y0 * SCALE

        if name == "dessus":
            tile = lift(cover(arts["dessus"], pw, ph, bias_y=0.42))
        elif name == "dessous":
            tile = lift(cover(arts["dessous"], pw, ph, bias_y=0.50))
        elif name == "rabat_couvercle":
            tile = arts["rabat"](pw, ph)
        elif name == "dos":
            tile = arts["dos"](pw, ph)
        elif name == "avant":
            tile = arts["avant"](pw, ph)
        elif name in ("flap_dos_g", "flap_dos_d", "flap_avant_g", "flap_avant_d"):
            tile = lift(cover(stone.rotate(90, expand=True), pw, ph, 0.5))
        elif name == "oreille_gauche":
            tile = side_panel(stone, logo, pw, ph, "left")
        elif name == "oreille_droite":
            tile = side_panel(stone, logo, pw, ph, "right")
        elif name == "cote_int_g":
            tile = side_panel(stone, logo, pw, ph, "left")
        elif name == "cote_int_d":
            tile = side_panel(stone, logo, pw, ph, "right")
        elif name == "cote_ext_g":
            tile = side_panel(stone, logo, pw, ph, "left")
        elif name == "cote_ext_d":
            tile = side_panel(stone, logo, pw, ph, "right")
        else:
            continue

        if name in ROT180:
            tile = tile.rotate(180)

        m = Image.fromarray(mask).resize((W, H), Image.Resampling.NEAREST)
        m = m.crop((sx0, sy0, sx0 + pw, sy0 + ph)).convert("L").filter(ImageFilter.MaxFilter(11))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(tile, (sx0, sy0), tile)
        la = np.array(layer)
        ma = np.zeros((H, W), dtype=np.uint8)
        ma[sy0 : sy0 + ph, sx0 : sx0 + pw] = np.array(m)
        la[:, :, 3] = (la[:, :, 3].astype(np.float32) * (ma.astype(np.float32) / 255.0)).astype(np.uint8)
        canvas.alpha_composite(Image.fromarray(la))
        print("  painted", name, bbox)

    lines = gabarit.resize((W, H), Image.Resampling.NEAREST)
    larr = np.array(lines)
    larr[larr[:, :, 3] > 20, 3] = 255
    canvas.alpha_composite(Image.fromarray(larr))
    return canvas.convert("RGB")


def mockup(scene, dessous, front, stone, logo, logo_ligne) -> Image.Image:
    pad, tw = 36, 980
    top = lift(cover(scene, tw, int(tw * 280 / 410), bias_y=0.42))
    bot = lift(cover(dessous, tw, int(tw * 278 / 422), bias_y=0.50))
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
    for d in (OUT, FACES, SOURCES, WEB, SOURCES / "dessous_variantes", WEB / "dessous", WEB / "bandes"):
        d.mkdir(parents=True, exist_ok=True)

    gabarit = Image.open(GABARIT).convert("RGBA")
    scene1 = Image.open(ART / "necromancer-knight-landscape-01.jpg")
    stone = Image.open(ART / "box-side-stone.jpg")
    vide = Image.open(ART / "box-bottom-castle-night.jpg")
    e_chevalier = Image.open(ART / "e-victoire-chevalier.jpg")
    e_necro = Image.open(ART / "e-victoire-necromancien.jpg")
    e_lendemain = Image.open(ART / "e-lendemain.jpg")
    bande_magie = Image.open(ART / "bande-magie.jpg")
    bande_choc = Image.open(ART / "bande-choc.jpg")
    bande_apres = Image.open(ART / "bande-apres.jpg")

    logo = logo_from_black(LOGO)
    logo_ligne = logo_from_white(LOGO_LIGNE)

    print_w = int(round(CM_W / 2.54 * DPI_PRINT))
    print_h = int(round(print_w * 9 / 16))

    def export_scene(im: Image.Image, name: str, folder: Path) -> None:
        save_jpeg(im.resize((print_w, print_h), Image.Resampling.LANCZOS), folder / f"{name}.jpg")
        save_jpeg(im.resize((1920, 1080), Image.Resampling.LANCZOS), WEB / "dessous" / f"{name}.jpg" if folder == SOURCES / "dessous_variantes" else WEB / f"{name}.jpg", quality=86)

    for key, im in (
        ("vide", vide),
        ("victoire_chevalier", e_chevalier),
        ("victoire_necromancien", e_necro),
        ("lendemain", e_lendemain),
    ):
        save_jpeg(im.resize((print_w, print_h), Image.Resampling.LANCZOS), SOURCES / "dessous_variantes" / f"{key}.jpg")
        save_jpeg(im.resize((1920, 1080), Image.Resampling.LANCZOS), WEB / "dessous" / f"{key}.jpg", quality=86)

    for key, im in (("magie", bande_magie), ("choc", bande_choc), ("apres", bande_apres)):
        save_jpeg(im.resize((print_w, print_h), Image.Resampling.LANCZOS), SOURCES / f"bande_{key}.jpg")
        save_jpeg(im.resize((1920, 1080), Image.Resampling.LANCZOS), WEB / "bandes" / f"{key}.jpg", quality=86)

    save_jpeg(vide.resize((print_w, print_h), Image.Resampling.LANCZOS), SOURCES / "dessous_chateau.jpg")

    # faces vues à l'endroit
    dx0, dy0, dx1, dy1 = PANELS["dessus"]
    save_jpeg(lift(cover(scene1, (dx1 - dx0) * SCALE, (dy1 - dy0) * SCALE, 0.42)), FACES / "dessus.jpg")
    bx0, by0, bx1, by1 = PANELS["dessous"]
    bw, bh = (bx1 - bx0) * SCALE, (by1 - by0) * SCALE
    save_jpeg(lift(cover(e_chevalier, bw, bh, 0.50)), FACES / "dessous.jpg")
    save_jpeg(lift(cover(e_chevalier, bw, bh, 0.50)), FACES / "dessous_victoire_chevalier.jpg")
    save_jpeg(lift(cover(e_necro, bw, bh, 0.50)), FACES / "dessous_victoire_necromancien.jpg")
    save_jpeg(lift(cover(e_lendemain, bw, bh, 0.50)), FACES / "dessous_lendemain.jpg")
    save_jpeg(lift(cover(vide, bw, bh, 0.55)), FACES / "dessous_vide.jpg")

    ax0, ay0, ax1, ay1 = PANELS["avant"]
    aw, ah = (ax1 - ax0) * SCALE, (ay1 - ay0) * SCALE
    face_avant_pierre = pierre_logo(stone, logo_ligne, aw, ah)
    face_avant_combat = bande_logo(bande_apres, logo_ligne, aw, ah, 0.62)
    save_jpeg(face_avant_pierre, FACES / "avant_pierre.jpg")
    save_jpeg(face_avant_combat, FACES / "avant_combat.jpg")
    save_jpeg(face_avant_combat, FACES / "avant.jpg")

    cx0, cy0, cx1, cy1 = PANELS["cote_int_g"]
    cw, ch = (cx1 - cx0) * SCALE, (cy1 - cy0) * SCALE
    save_jpeg(side_panel(stone, logo, cw, ch, "left"), FACES / "cote_gauche.jpg")
    save_jpeg(side_panel(stone, logo, cw, ch, "right"), FACES / "cote_droit.jpg")
    cote_hi = lift(cover(stone, 1600, 840, 0.5))
    paste_centered(cote_hi, fit_logo(logo, 1600, 840, 0.08), (0, 0, 1600, 840))
    save_jpeg(cote_hi, FACES / "cote_debout.jpg")

    dxw, dxh = (PANELS["dos"][2] - PANELS["dos"][0]) * SCALE, (PANELS["dos"][3] - PANELS["dos"][1]) * SCALE
    save_jpeg(pierre_logo(stone, logo_ligne, dxw, dxh), FACES / "bande_pierre.jpg")
    save_jpeg(bande_logo(bande_magie, logo_ligne, dxw, dxh, 0.45), FACES / "bande_magie.jpg")
    save_jpeg(bande_logo(bande_choc, logo_ligne, dxw, dxh, 0.48), FACES / "bande_choc.jpg")

    print("masks…")
    masks = interior_masks(gabarit)

    arts_pierre = {
        "dessus": scene1,
        "dessous": e_chevalier,
        "rabat": lambda w, h: pierre_logo(stone, logo_ligne, w, h),
        "dos": lambda w, h: pierre_logo(stone, logo_ligne, w, h),
        "avant": lambda w, h: pierre_logo(stone, logo_ligne, w, h),
    }
    arts_combat = {
        "dessus": scene1,
        "dessous": e_chevalier,
        "rabat": lambda w, h: bande_logo(bande_magie, logo_ligne, w, h, 0.42),
        "dos": lambda w, h: bande_logo(bande_choc, logo_ligne, w, h, 0.48),
        "avant": lambda w, h: bande_logo(bande_apres, logo_ligne, w, h, 0.62),
    }

    print("net pierre…")
    net_p = paint_net(gabarit, masks, arts_pierre, stone, logo, logo_ligne)
    save_jpeg(net_p, OUT / "exemple_net_pierre.jpg", quality=88)
    save_jpeg(net_p.resize((1280, 1248), Image.Resampling.LANCZOS), WEB / "exemple_net_pierre.jpg", quality=85)

    print("net combat…")
    net_c = paint_net(gabarit, masks, arts_combat, stone, logo, logo_ligne)
    save_jpeg(net_c, OUT / "exemple_net_combat.jpg", quality=88)
    save_jpeg(net_c, OUT / "exemple_net.jpg", quality=88)
    save_jpeg(net_c.resize((1280, 1248), Image.Resampling.LANCZOS), WEB / "exemple_net_combat.jpg", quality=85)
    save_jpeg(net_c.resize((1280, 1248), Image.Resampling.LANCZOS), WEB / "exemple_net.jpg", quality=85)

    mock_c = mockup(scene1, e_chevalier, face_avant_combat, stone, logo, logo_ligne)
    mock_p = mockup(scene1, e_chevalier, face_avant_pierre, stone, logo, logo_ligne)
    save_jpeg(mock_c, OUT / "exemple_mockup.jpg", quality=88)
    save_jpeg(mock_p, OUT / "exemple_mockup_pierre.jpg", quality=88)
    save_jpeg(mock_c.resize((1200, int(1200 * mock_c.size[1] / mock_c.size[0])), Image.Resampling.LANCZOS), WEB / "exemple_mockup.jpg", quality=85)
    save_jpeg(mock_p.resize((1200, int(1200 * mock_p.size[1] / mock_p.size[0])), Image.Resampling.LANCZOS), WEB / "exemple_mockup_pierre.jpg", quality=85)

    gabarit.convert("RGBA").save(OUT / "gabarit_source.png")
    print("done", OUT)


if __name__ == "__main__":
    main()
