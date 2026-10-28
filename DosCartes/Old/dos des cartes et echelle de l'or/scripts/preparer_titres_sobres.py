#!/usr/bin/env python3
"""Recadre les 20 dos « Pixel of Glory » sobres et construit la planche."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/opt/cursor/artifacts/assets")
OUT = ROOT / "propositions_dos" / "titre_sobre"

spec = importlib.util.spec_from_file_location("preparer_dos", Path(__file__).with_name("preparer_dos.py"))
pd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pd)

ITEMS = [
    ("sobre_01_brun_or_laurier.jpg", "01_brun_or_laurier.png", "Brun, or, laurier"),
    ("sobre_02_brun_or_seul.jpg", "02_brun_or_seul.png", "Brun, titre or"),
    ("sobre_03_brun_bleu_rouge.jpg", "03_brun_bleu_rouge.png", "Brun, bleu/rouge"),
    ("sobre_04_parchemin_or.jpg", "04_parchemin_or.png", "Parchemin or"),
    ("sobre_05_parchemin_bleu_rouge.jpg", "05_parchemin_bleu_rouge.png", "Parchemin couleur"),
    ("sobre_06_parchemin_laurier.jpg", "06_parchemin_laurier.png", "Parchemin, laurier"),
    ("sobre_07_bois_or.jpg", "07_bois_or.png", "Bois, titre or"),
    ("sobre_08_bois_bleu_rouge.jpg", "08_bois_bleu_rouge.png", "Bois, bleu/rouge"),
    ("sobre_09_pourpre_or_laurier.jpg", "09_pourpre_or_laurier.png", "Pourpre, laurier"),
    ("sobre_10_pourpre_or_seul.jpg", "10_pourpre_or_seul.png", "Pourpre, titre or"),
    ("sobre_11_pourpre_bleu_rouge.jpg", "11_pourpre_bleu_rouge.png", "Pourpre, bleu/or"),
    ("sobre_12_brun_losange.jpg", "12_brun_losange.png", "Brun, losange"),
    ("sobre_13_ivoire_or.jpg", "13_ivoire_or.png", "Ivoire, titre or"),
    ("sobre_14_bois_laurier.jpg", "14_bois_laurier.png", "Bois, laurier"),
    ("sobre_15_prune_or.jpg", "15_prune_or.png", "Prune, titre or"),
    ("sobre_16_espresso_or.jpg", "16_espresso_or.png", "Espresso, titre or"),
    ("sobre_17_ivoire_bleu_laurier.jpg", "17_ivoire_bleu_laurier.png", "Ivoire, couleur"),
    ("sobre_18_pourpre_laurier_couleur.jpg", "18_pourpre_laurier_couleur.png", "Pourpre, couleur"),
    ("sobre_19_cuir_beige.jpg", "19_cuir_beige.png", "Cuir beige"),
    ("sobre_20_chene_or.jpg", "20_chene_or.png", "Chêne, titre or"),
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
<title>Dos Pixel of Glory — 20 variantes sobres</title>
<style>
  :root {{ background:#12141c; color:#f3e6c4; font-family:Georgia, serif; }}
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
  <h1>Dos « Pixel of Glory » — 20 variantes sobres</h1>
  <p>Titre plus discret, police pixel, sans gantelets ni volutes.
  Fonds brun, parchemin clair, bois peint et pourpre. Format 750×1050.</p>
  <div class="planches">
    <img src="planche.jpg" alt="Planche des 20 dos sobres">
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
    pd.make_planche(written, OUT / "planche.jpg", "Dos Pixel of Glory  —  20 variantes sobres")
    write_apercu(written)
    print("ok")


if __name__ == "__main__":
    main()
