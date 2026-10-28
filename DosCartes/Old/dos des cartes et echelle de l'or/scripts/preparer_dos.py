#!/usr/bin/env python3
"""Recadre les dos générés au format carte 750×1050 et construit les planches."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SRC = Path("/opt/cursor/artifacts/assets")
OUT = ROOT / "propositions_dos"
CARD_W, CARD_H = 750, 1050
RADIUS = 28  # coins arrondis façon cartes du jeu

ITEMS = [
    ("dos_01_epee_rocher.jpg", "01_epee_rocher.png", "Épée dans le roc"),
    ("dos_02_dragon.jpg", "02_dragon.png", "Dragon"),
    ("dos_03_cuir_filigrane.jpg", "03_cuir_filigrane.png", "Cuir et filigrane"),
    ("dos_04_couronne.jpg", "04_couronne.png", "Couronne"),
    ("dos_05_crane.jpg", "05_crane.png", "Crâne"),
    ("dos_06_epees_croisees.jpg", "06_epees_croisees.png", "Épées croisées"),
    ("dos_07_bouclier.jpg", "07_bouclier.png", "Bouclier"),
    ("dos_08_forteresse.jpg", "08_forteresse.png", "Forteresse"),
    ("dos_09_lion.jpg", "09_lion.png", "Lion"),
    ("dos_10_griffon.jpg", "10_griffon.png", "Griffon"),
    ("dos_11_heaume.jpg", "11_heaume.png", "Heaume"),
    ("dos_12_arbre.jpg", "12_arbre.png", "Arbre"),
    ("dos_13_lune.jpg", "13_lune.png", "Lune"),
    ("dos_14_oeil.jpg", "14_oeil.png", "Œil"),
    ("dos_15_piece_or.jpg", "15_piece_or.png", "Pièce d'or"),
    ("dos_16_cle.jpg", "16_cle.png", "Clé"),
    ("dos_17_calice.jpg", "17_calice.png", "Calice"),
    ("dos_18_phenix.jpg", "18_phenix.png", "Phénix"),
    ("dos_19_loup.jpg", "19_loup.png", "Loup"),
    ("dos_20_serpent.jpg", "20_serpent.png", "Serpent"),
    ("dos_21_tour.jpg", "21_tour.png", "Tour"),
    ("dos_22_enclume.jpg", "22_enclume.png", "Enclume"),
    ("dos_23_cristal.jpg", "23_cristal.png", "Cristal"),
    ("dos_24_hibou.jpg", "24_hibou.png", "Hibou"),
    ("dos_25_chevalier.jpg", "25_chevalier.png", "Chevalier"),
    ("dos_26_banniere.jpg", "26_banniere.png", "Bannière"),
    ("dos_27_soleil.jpg", "27_soleil.png", "Soleil"),
    ("dos_28_coffre.jpg", "28_coffre.png", "Coffre"),
    ("dos_29_titre.jpg", "29_titre.png", "Pixel of Glory"),
    ("dos_30_balance.jpg", "30_balance.png", "Balance"),
]


def cover_crop(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    src_w, src_h = im.size
    scale = max(w / src_w, h / src_h)
    nw, nh = max(w, round(src_w * scale)), max(h, round(src_h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def round_card(im: Image.Image, radius: int = RADIUS) -> Image.Image:
    """Coins arrondis + fond noir, comme les cartes du jeu."""
    card = im.convert("RGBA")
    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), radius=radius, fill=255)
    # léger adoucissement du bord
    mask = mask.filter(ImageFilter.GaussianBlur(0.4))
    out = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    out.paste(card, (0, 0))
    out.putalpha(mask)
    # recomposer sur noir opaque
    bg = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    return Image.alpha_composite(bg, out).convert("RGB")


FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)


def make_planche(paths_caps: list[tuple[Path, str]], dest: Path, title: str) -> None:
    thumbs_w = 160
    thumbs_h = int(CARD_H * thumbs_w / CARD_W)
    gap, pad, cap_h, title_h = 12, 22, 28, 44
    cols = 5
    rows = (len(paths_caps) + cols - 1) // cols
    W = pad * 2 + cols * thumbs_w + (cols - 1) * gap
    H = pad * 2 + title_h + rows * (thumbs_h + cap_h) + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), (22, 16, 10))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 12), title, fill=(243, 230, 196), font=FONT_TITLE)
    for i, (p, cap) in enumerate(paths_caps):
        r, c = divmod(i, cols)
        x = pad + c * (thumbs_w + gap)
        y = pad + title_h + r * (thumbs_h + cap_h + gap)
        im = Image.open(p).convert("RGB").resize((thumbs_w, thumbs_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x, y))
        d.rectangle((x, y, x + thumbs_w - 1, y + thumbs_h - 1), outline=(90, 68, 28), width=1)
        d.text((x + 4, y + thumbs_h + 6), cap, fill=(232, 213, 160), font=FONT)
    sheet.save(dest, "JPEG", quality=90)
    print("planche", dest, sheet.size)


def write_apercu(written: list[tuple[Path, str]]) -> None:
    cards = "\n".join(
        f"""
      <figure>
        <img src="{p.name}" alt="{cap}">
        <figcaption>{i:02d}. {cap}</figcaption>
      </figure>"""
        for i, (p, cap) in enumerate(written, start=1)
    )
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Dos de cartes — 30 propositions</title>
<style>
  :root {{ background:#1a1410; color:#f3e6c4; font-family:Georgia, serif; }}
  body {{ max-width:1400px; margin:32px auto; padding:0 20px; }}
  h1 {{ font-weight:normal; letter-spacing:.04em; }}
  p {{ color:#cbb98a; max-width:72ch; line-height:1.45; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:16px; margin-top:24px; }}
  figure {{ margin:0; background:#0e0b08; border:1px solid #5a4520; border-radius:8px; overflow:hidden; }}
  img {{ width:100%; height:auto; display:block; }}
  figcaption {{ padding:8px 10px 12px; font-size:13px; color:#e8d5a0; }}
  .planches img {{ width:100%; max-width:920px; border:1px solid #5a4520; border-radius:8px; margin:8px 0 18px; }}
</style>
</head>
<body>
  <h1>Dos de cartes — 30 propositions</h1>
  <p>Même famille que tes grimoires cuir/or : dos plein cadre, tranche de livre à gauche,
  cadre or, pixel art 32-bit. Format 750×1050 comme les cartes du jeu.</p>
  <p>Pistes fortes pour un dos de deck : <strong>01 épée</strong>, <strong>02 dragon</strong>,
  <strong>03 filigrane</strong> (le plus « carte à jouer »), <strong>06 épées croisées</strong>,
  <strong>10 griffon</strong>, <strong>18 phénix</strong>, <strong>29 titre</strong>.</p>
  <div class="planches">
    <img src="planche_1.jpg" alt="Planche 1-15">
    <img src="planche_2.jpg" alt="Planche 16-30">
  </div>
  <div class="grid">{cards}
  </div>
</body>
</html>
"""
    (OUT / "apercu.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written: list[tuple[Path, str]] = []
    for src_name, dest_name, cap in ITEMS:
        src = SRC / src_name
        if not src.exists():
            raise SystemExit(f"missing {src}")
        im = round_card(cover_crop(Image.open(src), CARD_W, CARD_H))
        dest = OUT / dest_name
        im.save(dest, "PNG", optimize=True)
        written.append((dest, cap))
        print("wrote", dest, im.size)

    make_planche(written[:15], OUT / "planche_1.jpg", "Dos de cartes  1-15")
    make_planche(written[15:], OUT / "planche_2.jpg", "Dos de cartes  16-30")
    write_apercu(written)
    print("apercu.html ok")


if __name__ == "__main__":
    main()
