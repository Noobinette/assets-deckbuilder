#!/usr/bin/env python3
"""Sépare logos (PNG transparent) et fonds (dos sans logo).

Sources Best : 01, 03, 03b, 03e, 07, 09, 42 (+ Old/logos).
Sortie : DosCartes/logos et DosCartes/fonds, cartes 750×1050.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BEST = ROOT
ALT = ROOT
OLD = ROOT / "Old" / "dos des cartes et echelle de l'or" / "Old"
AGARDER = ROOT.parent / "Agarder" / "logos" / "symboles"
OUT = ROOT
LOGOS = OUT / "logos"
FONDS = OUT / "fonds"

CARD_W, CARD_H = 750, 1050
RADIUS = 28
GOLD = (196, 148, 64)
GOLD_DK = (126, 78, 28)


# ---------------------------------------------------------------------------
# géométrie
# ---------------------------------------------------------------------------

def round_card(im: Image.Image, radius: int = RADIUS) -> Image.Image:
    card = im.convert("RGBA").resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
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


def crop_alpha(rgba: np.ndarray, pad: int = 8) -> np.ndarray:
    ys, xs = np.where(rgba[..., 3] > 12)
    if len(xs) == 0:
        return rgba
    x0 = max(0, int(xs.min()) - pad)
    x1 = min(rgba.shape[1], int(xs.max()) + 1 + pad)
    y0 = max(0, int(ys.min()) - pad)
    y1 = min(rgba.shape[0], int(ys.max()) + 1 + pad)
    return rgba[y0:y1, x0:x1]


def decontam(rgba: np.ndarray, bg, lo: int = 16, hi: int = 220) -> np.ndarray:
    out = rgba.astype(np.float32)
    a = out[..., 3] / 255.0
    edge = (a > lo / 255.0) & (a < hi / 255.0)
    a3 = np.clip(a, 1e-3, 1.0)
    fg = (out[..., :3] - (1.0 - a3[..., None]) * np.asarray(bg, np.float32)) / a3[..., None]
    out[..., :3] = np.where(edge[..., None], np.clip(fg, 0, 255), out[..., :3])
    return out.astype(np.uint8)


def force_rot180(arr: np.ndarray) -> np.ndarray:
    h, w = arr.shape[:2]
    rot = np.rot90(arr, 2)
    yy, xx = np.indices((h, w))
    first = (yy * w + xx) <= ((h - 1 - yy) * w + (w - 1 - xx))
    if arr.ndim == 2:
        return np.where(first, arr, rot)
    return np.where(first[..., None], arr, rot)


def checker(w: int, h: int, cell: int = 12) -> np.ndarray:
    y, x = np.indices((h, w))
    c = ((x // cell) + (y // cell)) % 2
    bg = np.zeros((h, w, 3), np.uint8)
    bg[c == 0] = (228, 228, 228)
    bg[c == 1] = (150, 150, 150)
    return bg


def preview_checker(rgba: np.ndarray) -> Image.Image:
    a = rgba.astype(np.float32) / 255.0
    bg = checker(rgba.shape[1], rgba.shape[0]).astype(np.float32) / 255.0
    out = a[..., :3] * a[..., 3:4] + bg * (1.0 - a[..., 3:4])
    return Image.fromarray((out * 255).clip(0, 255).astype(np.uint8))


def keep_cluster(mask: np.ndarray, min_main: int = 55, radius: int = 14) -> np.ndarray:
    """Garde les blobs assez gros (lettres). Le ROI serré exclut le grain du cuir."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask.astype(np.uint8)
    keep = np.zeros_like(mask, np.uint8)
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        bw = int(stats[i, cv2.CC_STAT_WIDTH])
        bh = int(stats[i, cv2.CC_STAT_HEIGHT])
        if area < min_main:
            continue
        if min(bw, bh) <= 6 and max(bw, bh) >= 40:
            continue
        keep[labels == i] = 1
    if keep.any():
        return keep
    biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    keep[labels == biggest] = 1
    return keep


def fill_holes(keep: np.ndarray) -> np.ndarray:
    h, w = keep.shape
    inv = (keep == 0).astype(np.uint8)
    flood = inv.copy()
    m = np.zeros((h + 2, w + 2), np.uint8)
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv2.floodFill(flood, m, seed, 2)
    holes = flood == 1
    out = keep.copy()
    out[holes] = 1
    return out


def to_rgba(crop: np.ndarray, keep: np.ndarray, bg) -> np.ndarray:
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    halo = cv2.dilate(keep, k, iterations=1)
    a = np.zeros(keep.shape, np.float32)
    a[keep == 1] = 255
    a[(halo == 1) & (keep == 0)] = 80
    rgba = np.dstack([crop, a]).astype(np.uint8)
    return crop_alpha(decontam(rgba, bg), pad=8)


# ---------------------------------------------------------------------------
# extraction logos
# ---------------------------------------------------------------------------

def extract_title(im: Image.Image, roi: tuple[int, int, int, int], dist_th: float = 52) -> np.ndarray:
    """Titre PIXEL OF GLORY sur cuir (bleu / or / rouge)."""
    rgb = np.asarray(im.convert("RGB"))
    x0, y0, x1, y1 = roi
    crop = rgb[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    ring = np.zeros((h, w), bool)
    m = 10
    ring[:m] = ring[-m:] = True
    ring[:, :m] = ring[:, -m:] = True
    bg = np.median(crop[ring].reshape(-1, 3), axis=0)
    dist = np.linalg.norm(crop.astype(np.float32) - bg, axis=-1)

    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    r, g, b = [crop[..., i].astype(np.int32) for i in range(3)]
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0]

    blue = (H > 90) & (H < 135) & (S > 60) & (b > r + 5)
    red = (H < 18) & (S > 100) & (V > 70) & (r > g + 35) & (r > 70)
    gold = (H > 12) & (H < 40) & (S > 80) & (V > 120) & (r > 140)
    leather_hue = (H >= 8) & (H <= 16) & (V < 90)
    core = blue | red | gold | ((dist > dist_th) & (~leather_hue) & (S > 50))

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    near = cv2.dilate(core.astype(np.uint8), k, iterations=1).astype(bool)
    dark = (L < 24) & near
    mask = (core | dark).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=1)
    keep = keep_cluster(mask, min_main=40, radius=16)
    return to_rgba(crop, keep, bg)


def extract_gold_title(im: Image.Image, roi: tuple[int, int, int, int]) -> np.ndarray:
    """Titre or 01 / 07, ROI serré autour des lettres."""
    rgb = np.asarray(im.convert("RGB"))
    x0, y0, x1, y1 = roi
    crop = rgb[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    r, g, b = [crop[..., i].astype(np.float32) for i in range(3)]
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV).astype(np.float32)
    S, V = hsv[..., 1], hsv[..., 2]
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0]
    ring = np.zeros((h, w), bool)
    m = 6
    ring[:m] = ring[-m:] = True
    ring[:, :m] = ring[:, -m:] = True
    bg = np.median(crop[ring].reshape(-1, 3), axis=0)
    L_bg = float(np.median(L[ring]))

    gold = (r > 150) & (g > 90) & (r > b + 35) & (S > 80) & (L > L_bg + 28)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    near = cv2.dilate(gold.astype(np.uint8), k, iterations=2).astype(bool)
    dark = (L < 28) & near
    gold_soft = (r > 130) & (g > 75) & (r > b + 24) & (S > 55) & near
    mask = (gold | dark | gold_soft).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=1)
    keep = keep_cluster(mask, min_main=40, radius=12)
    return to_rgba(crop, keep, bg)


def extract_solid(im: Image.Image, dist_th: float = 18.0, do_fill_holes: bool = True) -> np.ndarray:
    """Emblème sur aplat brun (09, 42, laurier)."""
    rgb = np.asarray(im.convert("RGB"))
    h, w = rgb.shape[:2]
    corners = np.concatenate(
        [
            rgb[:6, :6].reshape(-1, 3),
            rgb[:6, -6:].reshape(-1, 3),
            rgb[-6:, :6].reshape(-1, 3),
            rgb[-6:, -6:].reshape(-1, 3),
        ]
    )
    bg = np.median(corners, axis=0)
    dist = np.linalg.norm(rgb.astype(np.float32) - bg, axis=-1)
    bg_like = (dist < dist_th).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    bg_er = cv2.erode(bg_like, k, iterations=1)
    n, labels = cv2.connectedComponents(bg_er, 8)
    border = np.zeros((h, w), bool)
    border[0] = border[-1] = True
    border[:, 0] = border[:, -1] = True
    bgm = np.zeros((h, w), bool)
    for i in range(1, n):
        if np.any(border & (labels == i)):
            bgm[labels == i] = True
    bgm = cv2.dilate(bgm.astype(np.uint8), k, iterations=1).astype(bool)
    keep = (~bgm).astype(np.uint8)
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, k, iterations=1)
    if do_fill_holes:
        keep = fill_holes(keep)
    keep = keep_cluster(keep, min_main=80, radius=40)
    return to_rgba(rgb, keep, bg)


def extract_white(im: Image.Image) -> np.ndarray:
    rgb = np.asarray(im.convert("RGB"))
    mn = rgb.min(-1)
    keep = (mn < 236).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, k, iterations=1)
    keep = keep_cluster(keep, min_main=40, radius=80)
    return to_rgba(rgb, keep, (255, 255, 255))


def stack_logos(top: np.ndarray, bot: np.ndarray, gap: int = 16) -> np.ndarray:
    w = max(top.shape[1], bot.shape[1])
    h = top.shape[0] + gap + bot.shape[0]
    out = np.zeros((h, w, 4), np.uint8)
    x = (w - top.shape[1]) // 2
    out[: top.shape[0], x : x + top.shape[1]] = top
    x = (w - bot.shape[1]) // 2
    y = top.shape[0] + gap
    out[y : y + bot.shape[0], x : x + bot.shape[1]] = bot
    return out


# ---------------------------------------------------------------------------
# fonds
# ---------------------------------------------------------------------------

def draw_simple_frame(im: Image.Image, gold: tuple[int, int, int] = GOLD) -> Image.Image:
    canvas = im.convert("RGB")
    d = ImageDraw.Draw(canvas)
    W, H = canvas.size
    dark = tuple(max(0, c - 72) for c in gold)
    light = tuple(min(255, c + 42) for c in gold)
    for m, rad, col, width in ((10, 24, dark, 4), (16, 20, light, 3), (22, 16, dark, 1)):
        d.rounded_rectangle((m, m, W - 1 - m, H - 1 - m), radius=rad, outline=col, width=width)
    tick = 26
    m = 22
    for x, y, dx, dy in (
        (m, m, 1, 1),
        (W - 1 - m, m, -1, 1),
        (m, H - 1 - m, 1, -1),
        (W - 1 - m, H - 1 - m, -1, -1),
    ):
        d.line([(x, y + dy * tick), (x, y), (x + dx * tick, y)], fill=light, width=2)
    return canvas


def leather_field(im: Image.Image, clean: tuple[int, int, int, int]) -> np.ndarray:
    """Champ 180-sym : on prend une zone de cuir sans logo, on la colle à son 180°."""
    arr = np.asarray(im.convert("RGB"))
    cx0, cy0, cx1, cy1 = clean
    patch = arr[cy0:cy1, cx0:cx1].astype(np.float32)
    bot = np.rot90(patch, 2)
    ov = min(48, patch.shape[0] // 4)
    h = patch.shape[0] * 2 - ov
    w = patch.shape[1]
    field = np.zeros((h, w, 3), np.float32)
    field[: patch.shape[0]] = patch
    alpha = np.linspace(1.0, 0.0, ov, dtype=np.float32)[:, None, None]
    field[patch.shape[0] - ov : patch.shape[0]] = patch[-ov:] * alpha + bot[:ov] * (1.0 - alpha)
    field[patch.shape[0] :] = bot[ov:]
    return force_rot180(np.clip(field, 0, 255).astype(np.uint8))


def assemble_fond(field: np.ndarray, gold: tuple[int, int, int] = GOLD, margin: int = 34) -> Image.Image:
    med = tuple(int(x) for x in np.median(field.reshape(-1, 3), axis=0))
    canvas = Image.new("RGB", (CARD_W, CARD_H), med)
    inner_w, inner_h = CARD_W - 2 * margin, CARD_H - 2 * margin
    tex = Image.fromarray(field).resize((inner_w, inner_h), Image.Resampling.LANCZOS)
    canvas.paste(tex, (margin, margin))
    return round_card(draw_simple_frame(canvas, gold))


def hue_shift(arr: np.ndarray, dh: float, s_mul: float = 1.0, v_mul: float = 1.0) -> np.ndarray:
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + dh) % 180.0
    hsv[..., 1] = np.clip(hsv[..., 1] * s_mul, 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * v_mul, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)


def make_losanges(base: np.ndarray) -> np.ndarray:
    field = hue_shift(base, dh=165, s_mul=1.18, v_mul=0.78)
    h, w = field.shape[:2]
    cx, cy = w // 2, h // 2
    yy, xx = np.indices((h, w))
    color = np.array(GOLD_DK, np.int16)
    overlay = field.copy()
    step_x, step_y, rad = 130, 156, 20
    for iy in range(-6, 7):
        for ix in range(-5, 6):
            px = cx + ix * step_x + (step_x // 2 if iy % 2 else 0)
            py = cy + iy * (step_y // 2)
            if abs(px - cx) < 140 and abs(py - cy) < 180:
                continue
            manh = np.abs(xx - px) + np.abs(yy - py)
            ring = (manh >= rad - 1) & (manh <= rad + 1)
            overlay[ring] = np.clip(
                (overlay[ring].astype(np.int16) * 2 + color) // 3, 0, 255
            ).astype(np.uint8)
    return force_rot180(overlay)


# ---------------------------------------------------------------------------
# aperçu
# ---------------------------------------------------------------------------

def save_logo(rgba: np.ndarray, name: str, cap: str, items: list) -> None:
    dest = LOGOS / f"{name}.png"
    Image.fromarray(rgba).save(dest, "PNG")
    preview_checker(rgba).save(LOGOS / f"{name}_apercu.png", "PNG")
    items.append((name, cap, dest, rgba.shape))
    print("logo", dest.name, rgba.shape)


def paste_logo_on_fond(fond: Image.Image, logo_rgba: np.ndarray, scale: float = 0.72) -> Image.Image:
    card = fond.convert("RGBA")
    logo = Image.fromarray(logo_rgba)
    max_w = int(CARD_W * scale)
    if logo.width > max_w:
        nh = int(logo.height * max_w / logo.width)
        logo = logo.resize((max_w, nh), Image.Resampling.LANCZOS)
    max_h = int(CARD_H * 0.62)
    if logo.height > max_h:
        nw = int(logo.width * max_h / logo.height)
        logo = logo.resize((nw, max_h), Image.Resampling.LANCZOS)
    x = (CARD_W - logo.width) // 2
    y = (CARD_H - logo.height) // 2
    card.alpha_composite(logo.convert("RGBA"), (x, y))
    bg = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    return Image.alpha_composite(bg, card).convert("RGB")


def write_apercu(logos: list, fonds: list, mixes: list[Path]) -> None:
    def fig_logo(name, cap):
        return (
            f'<figure><img class="chk" src="logos/{name}_apercu.png" alt="{cap}">'
            f"<figcaption>{cap}<br><code>logos/{name}.png</code></figcaption></figure>"
        )

    def fig_fond(name, cap):
        return (
            f'<figure><img src="fonds/{name}.png" alt="{cap}">'
            f"<figcaption>{cap}<br><code>fonds/{name}.png</code></figcaption></figure>"
        )

    logo_html = "\n".join(fig_logo(n, c) for n, c, *_ in logos)
    cuir = [(n, c) for n, c, *_ in fonds if "livre" not in n]
    livres = [(n, c) for n, c, *_ in fonds if "livre" in n]
    fond_cuir_html = "\n".join(fig_fond(n, c) for n, c in cuir)
    fond_livre_html = "\n".join(fig_fond(n, c) for n, c in livres)
    mix_html = "\n".join(
        f'<figure><img src="exemples/{p.name}" alt="{p.stem}">'
        f"<figcaption>{p.stem.replace('_', ' ')}</figcaption></figure>"
        for p in mixes
    )
    (OUT / "apercu.html").write_text(
        f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>DosCartes — logos et fonds</title>
<style>
  :root {{ background:#12141c; color:#f3e6c4; font-family:Georgia, serif; }}
  body {{ max-width:1400px; margin:32px auto; padding:0 20px 64px; }}
  h1, h2 {{ font-weight:normal; letter-spacing:.04em; }}
  p {{ color:#cbb98a; max-width:80ch; line-height:1.45; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin:16px 0 36px; }}
  .wide {{ grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); }}
  figure {{ margin:0; background:#0e0b08; border:1px solid #5a4520; border-radius:8px; overflow:hidden; }}
  img {{ width:100%; height:auto; display:block; }}
  img.chk {{ background:repeating-conic-gradient(#c8c8c8 0% 25%, #8e8e8e 0% 50%) 50% / 18px 18px; }}
  figcaption {{ padding:8px 10px 12px; font-size:13px; color:#e8d5a0; }}
  code {{ font-size:11px; color:#bba56e; }}
</style>
</head>
<body>
  <h1>DosCartes — logos et fonds séparés</h1>
  <p>
    Logos extraits des dos Best (<code>01</code>, <code>03</code>, <code>03b</code>,
    <code>03e</code>, <code>07</code>, <code>09</code>, <code>42</code>) :
    tout ce qui n’est pas le logo est transparent. Fonds cuir plat 180°-symétriques
    (<code>01</code>–<code>05</code>) et fonds <strong>style livre</strong> avec tranche
    (<code>06</code>–<code>09</code>). N’importe quel logo se pose sur n’importe quel fond.
  </p>
  <h2>Logos (PNG transparent)</h2>
  <div class="grid wide">{logo_html}</div>
  <h2>Fonds cuir plat (750×1050, sans logo)</h2>
  <div class="grid">{fond_cuir_html}</div>
  <h2>Fonds style livre (tranche + cadre géométrique)</h2>
  <div class="grid">{fond_livre_html}</div>
  <h2>Exemples logo + fond</h2>
  <div class="grid">{mix_html}</div>
</body>
</html>
""",
        encoding="utf-8",
    )


def make_planche(items: list[tuple[Path, str]], dest: Path, title: str, thumb_w: int = 140) -> None:
    im0 = Image.open(items[0][0])
    tw, th = thumb_w, int(im0.height * thumb_w / im0.width)
    gap, pad, cap_h, title_h = 12, 20, 36, 42
    cols = min(5, len(items))
    rows = (len(items) + cols - 1) // cols
    W = pad * 2 + cols * tw + (cols - 1) * gap
    H = pad * 2 + title_h + rows * (th + cap_h) + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), (18, 16, 22))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = font_t = ImageFont.load_default()
    d.text((pad, 12), title, fill=(243, 230, 196), font=font_t)
    for i, (p, cap) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (tw + gap)
        y = pad + title_h + r * (th + cap_h + gap)
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        d.rectangle((x, y, x + tw - 1, y + th - 1), outline=(90, 68, 28), width=1)
        d.text((x + 4, y + th + 6), cap[:28], fill=(232, 213, 160), font=font)
    sheet.save(dest, "JPEG", quality=90)
    print("planche", dest)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    LOGOS.mkdir(parents=True, exist_ok=True)
    FONDS.mkdir(parents=True, exist_ok=True)
    logos: list = []

    im03 = Image.open(BEST / "03_brun_bleu_rouge.png")
    im03b = Image.open(BEST / "03b_pixelof_glory.png")
    im03e = Image.open(ALT / "03e_trois_lignes.png")
    im07 = Image.open(BEST / "07_bois_or.png")
    im01 = Image.open(BEST / "01_brun_or_laurier.png")

    l03 = extract_title(im03, (100, 430, 650, 665))
    save_logo(l03, "03_titre_bicolore", "03 — PIXEL / OF GLORY bleu-or-rouge", logos)

    l03b = extract_title(im03b, (95, 420, 665, 650))
    save_logo(l03b, "03b_titre_deux_lignes", "03b — PIXEL OF / GLORY", logos)

    l03e = extract_title(im03e, (115, 412, 640, 715))
    save_logo(l03e, "03e_titre_trois_lignes", "03e — PIXEL / OF / GLORY", logos)

    l07 = extract_gold_title(im07, (195, 455, 555, 610))
    save_logo(l07, "07_titre_or", "07 — titre or PIXEL OF GLORY", logos)

    laur_src = AGARDER / "01_laurier_diamant.jpg"
    if not laur_src.exists():
        laur_src = BEST / "01_brun_or_laurier.png"
        l01a = extract_gold_title(im01, (230, 320, 520, 590))
    else:
        l01a = extract_solid(Image.open(laur_src), dist_th=18, do_fill_holes=False)
    save_logo(l01a, "01a_laurier_diamant", "01 — laurier et diamant", logos)

    l01 = stack_logos(l01a, l07, gap=18)
    save_logo(l01, "01_laurier_et_titre_or", "01 — laurier + titre or", logos)

    l09 = extract_solid(Image.open(BEST / "09_couronne_diamant.jpg"), dist_th=20, do_fill_holes=False)
    save_logo(l09, "09_couronne_diamant", "09 — couronne et diamant", logos)

    l42 = extract_solid(Image.open(BEST / "42_griffon_entier.jpg"), dist_th=16, do_fill_holes=True)
    save_logo(l42, "42_griffon", "42 — griffon", logos)

    simple = OLD / "logos" / "logo_pixel_simple.jpg"
    if simple.exists():
        save_logo(extract_white(Image.open(simple)), "old_wordmark_simple", "Old — wordmark bleu / rouge", logos)

    # --- fonds ---
    # 03 / 03b / 03e : même cuir. Patch propre au-dessus du titre, collé à son 180°.
    field03 = leather_field(im03, clean=(125, 120, 625, 400))
    fond_cuir = assemble_fond(field03, GOLD)
    fond_cuir.save(FONDS / "01_cuir_brun.png", "PNG", optimize=True)

    field_sombre = hue_shift(field03, dh=0, s_mul=1.05, v_mul=0.72)
    fond_sombre = assemble_fond(field_sombre, GOLD)
    fond_sombre.save(FONDS / "02_cuir_sombre.png", "PNG", optimize=True)

    loz = make_losanges(field03)
    fond_loz = assemble_fond(loz, (186, 132, 64))
    fond_loz.save(FONDS / "03_losanges_bordeaux.png", "PNG", optimize=True)

    obs = hue_shift(field03, dh=115, s_mul=0.72, v_mul=0.38)
    fond_obs = assemble_fond(force_rot180(obs), (168, 140, 72))
    fond_obs.save(FONDS / "04_obsidienne.png", "PNG", optimize=True)

    eme = hue_shift(field03, dh=70, s_mul=0.95, v_mul=0.55)
    fond_eme = assemble_fond(force_rot180(eme), (150, 168, 88))
    fond_eme.save(FONDS / "05_emeraude.png", "PNG", optimize=True)

    fonds_meta = [
        ("01_cuir_brun", "Cuir brun — dos 03 / 03b / 03e sans logo"),
        ("02_cuir_sombre", "Cuir sombre — même grain, plus profond"),
        ("03_losanges_bordeaux", "Nouveau — losanges bordeaux, centre vide"),
        ("04_obsidienne", "Nouveau — obsidienne, grain cuir"),
        ("05_emeraude", "Nouveau — émeraude sombre"),
        ("06_livre_brun", "Livre — grimoire brun or (esprit du dos 01)"),
        ("07_livre_bordeaux", "Livre — grimoire bordeaux"),
        ("08_livre_nuit", "Livre — grimoire bleu nuit"),
        ("09_livre_foret", "Livre — grimoire vert forêt"),
    ]
    fonds_meta = [(n, c) for n, c in fonds_meta if (FONDS / f"{n}.png").exists()]
    for name, _ in fonds_meta:
        print("fond", name)

    exemples = OUT / "exemples"
    exemples.mkdir(parents=True, exist_ok=True)
    mixes = []
    for name, fond, logo, sc in (
        ("mix_03_sur_brun", fond_cuir, l03, 0.78),
        ("mix_laurier_sur_brun", fond_cuir, l01a, 0.46),
        ("mix_03e_sur_obsidienne", fond_obs, l03e, 0.70),
        ("mix_griffon_sur_bordeaux", fond_loz, l42, 0.52),
        ("mix_couronne_sur_sombre", fond_sombre, l09, 0.42),
        ("mix_01_sur_emeraude", fond_eme, l01, 0.55),
        ("mix_03b_sur_obsidienne", fond_obs, l03b, 0.78),
        ("mix_07_sur_bordeaux", fond_loz, l07, 0.62),
    ):
        p = exemples / f"{name}.png"
        paste_logo_on_fond(fond, logo, sc).save(p, "PNG", optimize=True)
        mixes.append(p)

    livres = {
        "06_livre_brun": (l01, 0.55),
        "07_livre_bordeaux": (l42, 0.52),
        "08_livre_nuit": (l07, 0.62),
        "09_livre_foret": (l03, 0.78),
    }
    mix_names = {
        "06_livre_brun": "mix_laurier_sur_livre_brun",
        "07_livre_bordeaux": "mix_griffon_sur_livre_bordeaux",
        "08_livre_nuit": "mix_07_sur_livre_nuit",
        "09_livre_foret": "mix_03_sur_livre_foret",
    }
    for fond_name, (logo, sc) in livres.items():
        fp = FONDS / f"{fond_name}.png"
        if not fp.exists():
            continue
        p = exemples / f"{mix_names[fond_name]}.png"
        paste_logo_on_fond(Image.open(fp), logo, sc).save(p, "PNG", optimize=True)
        mixes.append(p)

    write_apercu(logos, fonds_meta, mixes)
    make_planche(
        [(FONDS / f"{n}.png", c.split("—")[0].strip()) for n, c in fonds_meta],
        OUT / "planche_fonds.jpg",
        "Fonds sans logo — 750×1050",
    )
    (OUT / "README.md").write_text(
        """# DosCartes — logos et fonds séparés

Tout logo se pose sur tout fond. PNG 8 bits, fonds 750×1050.

## Logos (`logos/`)

| Fichier | Source | Contenu |
|---|---|---|
| `03_titre_bicolore.png` | Best/03 | PIXEL / OF GLORY bleu-or-rouge |
| `03b_titre_deux_lignes.png` | Best/03b | PIXEL OF / GLORY |
| `03e_titre_trois_lignes.png` | Best/03e | PIXEL / OF / GLORY |
| `07_titre_or.png` | Best/07 | PIXEL OF GLORY or |
| `01a_laurier_diamant.png` | emblème du dos 01 | laurier + diamant |
| `01_laurier_et_titre_or.png` | 01a + 07 | laurier + titre or (dos 01) |
| `09_couronne_diamant.png` | Best/09 | couronne et diamant |
| `42_griffon.png` | Best/42 | griffon |
| `old_wordmark_simple.png` | Old/logos | wordmark bleu / rouge |

Les `*_apercu.png` sont les mêmes logos sur damier (contrôle du alpha).

## Fonds (`fonds/`)

Deux familles : cuir plat 180°-symétrique (`01`–`05`) et style livre avec tranche (`06`–`09`).

| Fichier | Origine |
|---|---|
| `01_cuir_brun.png` | cuir des dos 03 / 03b / 03e |
| `02_cuir_sombre.png` | même grain, plus profond |
| `03_losanges_bordeaux.png` | nouveau |
| `04_obsidienne.png` | nouveau |
| `05_emeraude.png` | nouveau |
| `06_livre_brun.png` | grimoire brun or, esprit du dos 01 |
| `07_livre_bordeaux.png` | grimoire bordeaux |
| `08_livre_nuit.png` | grimoire bleu nuit |
| `09_livre_foret.png` | grimoire vert forêt |

Ouvrir `apercu.html` pour tout voir, y compris des exemples logo + fond.

Regénérer les logos et les fonds 01–05 : `python3 DosCartes/scripts/separer_logos_fonds.py`
(les fonds livre `06`–`09` ne sont pas écrasés).
""",
        encoding="utf-8",
    )
    print("ok", OUT)


if __name__ == "__main__":
    main()
