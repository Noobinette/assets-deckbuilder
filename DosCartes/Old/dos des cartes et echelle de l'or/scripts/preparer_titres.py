#!/usr/bin/env python3
"""Recadre les 20 dos « Pixel of Glory » et construit la planche."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/opt/cursor/artifacts/assets")
OUT = ROOT / "propositions_dos" / "titre_pixel"

spec = importlib.util.spec_from_file_location("preparer_dos", Path(__file__).with_name("preparer_dos.py"))
pd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pd)

ITEMS = [
    ("titre_01_navy_laurier.jpg", "01_navy_laurier.png", "Navy et laurier"),
    ("titre_02_cramoisi.jpg", "02_cramoisi.png", "Cramoisi"),
    ("titre_03_split_bleu_rouge.jpg", "03_split_bleu_rouge.png", "Bleu / rouge"),
    ("titre_04_parchemin.jpg", "04_parchemin.png", "Parchemin"),
    ("titre_05_velours_nuit.jpg", "05_velours_nuit.png", "Velours nuit"),
    ("titre_06_blason.jpg", "06_blason.png", "Blason"),
    ("titre_07_bois_peint.jpg", "07_bois_peint.png", "Bois peint"),
    ("titre_08_pierre.jpg", "08_nuit_entrelacs.png", "Nuit et entrelacs"),
    ("titre_09_vitrail.jpg", "09_vitrail.png", "Vitrail"),
    ("titre_10_banniere.jpg", "10_banniere.png", "Bannière"),
    ("titre_11_ivoire.jpg", "11_ivoire.png", "Ivoire enluminé"),
    ("titre_12_metal.jpg", "12_metal.png", "Plaque métal"),
    ("titre_13_ciel_nuit.jpg", "13_ciel_nuit.png", "Ciel étoilé"),
    ("titre_14_entrelacs.jpg", "14_entrelacs.png", "Entrelacs"),
    ("titre_15_emeraude.jpg", "15_emeraude.png", "Émeraude"),
    ("titre_16_pourpre.jpg", "16_pourpre.png", "Pourpre"),
    ("titre_17_sceau.jpg", "17_sceau.png", "Sceau"),
    ("titre_18_mosaique.jpg", "18_mosaique.png", "Mosaïque"),
    ("titre_19_double_tranche.jpg", "19_double_tranche.png", "Double tranche"),
    ("titre_20_simple_etoile.jpg", "20_simple_etoile.png", "Titre simple"),
]


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
<title>Dos Pixel of Glory — 20 variantes</title>
<style>
  :root {{ background:#12141c; color:#f3e6c4; font-family:Georgia, serif; }}
  body {{ max-width:1400px; margin:32px auto; padding:0 20px; }}
  h1 {{ font-weight:normal; letter-spacing:.04em; }}
  p {{ color:#cbb98a; max-width:72ch; line-height:1.45; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:16px; margin-top:24px; }}
  figure {{ margin:0; background:#0e0b08; border:1px solid #3d4a7a; border-radius:8px; overflow:hidden; }}
  img {{ width:100%; height:auto; display:block; }}
  figcaption {{ padding:8px 10px 12px; font-size:13px; color:#e8d5a0; }}
  .planches img {{ width:100%; max-width:920px; border:1px solid #3d4a7a; border-radius:8px; margin:8px 0 18px; }}
</style>
</head>
<body>
  <h1>Dos « Pixel of Glory » — 20 variantes</h1>
  <p>Titre du jeu en bleu / rouge ancien, comme les logos. Format 750×1050.</p>
  <div class="planches">
    <img src="planche.jpg" alt="Planche des 20 dos titre">
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
        im = pd.round_card(pd.cover_crop(Image.open(src), pd.CARD_W, pd.CARD_H))
        dest = OUT / dest_name
        im.save(dest, "PNG", optimize=True)
        written.append((dest, cap))
        print("wrote", dest, im.size)
    pd.make_planche(written, OUT / "planche.jpg", "Dos Pixel of Glory  —  20 variantes")
    write_apercu(written)
    print("ok")


if __name__ == "__main__":
    main()
