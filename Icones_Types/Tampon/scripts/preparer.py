#!/usr/bin/env python3
"""Découpe les planches tampon / esquisse, exporte PNG encre sur transparent, mockups."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path("/opt/cursor/artifacts/assets")
CARTES = Path("/workspace/Cartes")
TYPES_DIR = Path("/workspace/Icones_Types")

PARCHMENT = (226, 199, 146, 255)
INK = (24, 20, 16, 255)
BG_DARK = (22, 20, 22, 255)

TYPES = ["unite", "batiment", "equipement", "evenement", "plan", "lieu"]
TYPE_LABELS = {
    "unite": "Unité",
    "batiment": "Bâtiment",
    "equipement": "Équipement",
    "evenement": "Événement",
    "plan": "Plan",
    "lieu": "Lieu",
}
NAMES = {
    "unite": [
        "casque",
        "casque_profil",
        "heaume",
        "epees",
        "bouclier",
        "lance",
        "soldat",
        "gantelet",
        "cor",
        "banniere",
    ],
    "batiment": [
        "tour",
        "tour_drapeau",
        "donjon",
        "chateau",
        "portail",
        "maison",
        "rempart",
        "phare",
        "pont_levis",
        "grange",
    ],
    "equipement": [
        "sac",
        "coffre",
        "epee",
        "anneau",
        "sacoche",
        "hache",
        "marteau",
        "arc",
        "amulette",
        "bottes",
    ],
    "evenement": [
        "grimoire",
        "parchemin",
        "eclair",
        "potion",
        "rune",
        "flamme",
        "etincelle",
        "lune",
        "sablier",
        "oeil",
    ],
    "plan": [
        "lettre",
        "rouleau",
        "tactique",
        "plume",
        "decret",
        "enveloppe",
        "cachet",
        "pions",
        "fleches",
        "pli",
    ],
    "lieu": [
        "carte",
        "boussole",
        "drapeau",
        "montagne",
        "borne",
        "arbre",
        "pont",
        "grotte",
        "rose",
        "collines",
    ],
}
NAME_LABELS = {
    "casque": "Casque",
    "casque_profil": "Casque de profil",
    "heaume": "Heaume",
    "epees": "Épées croisées",
    "bouclier": "Bouclier",
    "lance": "Lance",
    "soldat": "Soldat",
    "gantelet": "Gantelet",
    "cor": "Cor",
    "banniere": "Bannière",
    "tour": "Tour",
    "tour_drapeau": "Tour au drapeau",
    "donjon": "Donjon",
    "chateau": "Château",
    "portail": "Portail",
    "maison": "Maison",
    "rempart": "Rempart",
    "phare": "Phare",
    "pont_levis": "Pont-levis",
    "grange": "Grange",
    "sac": "Sac",
    "coffre": "Coffre",
    "epee": "Épée",
    "anneau": "Anneau",
    "sacoche": "Sacoche",
    "hache": "Hache",
    "marteau": "Marteau",
    "arc": "Arc",
    "amulette": "Amulette",
    "bottes": "Bottes",
    "grimoire": "Grimoire",
    "parchemin": "Parchemin",
    "eclair": "Éclair",
    "potion": "Potion",
    "rune": "Rune",
    "flamme": "Flamme",
    "etincelle": "Étincelle",
    "lune": "Lune",
    "sablier": "Sablier",
    "oeil": "Œil",
    "lettre": "Lettre scellée",
    "rouleau": "Rouleau",
    "tactique": "Carte tactique",
    "plume": "Plume",
    "decret": "Décret",
    "enveloppe": "Enveloppe",
    "cachet": "Cachet",
    "pions": "Pions",
    "fleches": "Flèches",
    "pli": "Pli",
    "carte": "Carte",
    "boussole": "Boussole",
    "drapeau": "Drapeau",
    "montagne": "Montagne",
    "borne": "Borne",
    "arbre": "Arbre",
    "pont": "Pont",
    "grotte": "Grotte",
    "rose": "Rose des vents",
    "collines": "Collines",
}

STYLES = {
    "tampon": {
        "file": "planche_tampon_{t}.jpg",
        "label": "Tampon",
        "hint": "Encre noire, cercle un peu usé comme un tampon de poste.",
    },
    "esquisse": {
        "file": "planche_esquisse_simple_{t}.jpg",
        "label": "Esquisse",
        "hint": "Trait de crayon simple, presque un pictogramme.",
    },
    "crayon": {
        "file": "planche_esquisse_{t}.jpg",
        "label": "Crayon",
        "hint": "Esquisse plus travaillée — plus de volume, un peu plus chargée à 64 px.",
    },
}

HIRES = [
    ("tampon", "unite", "casque", "test_tampon_casque.jpg"),
    ("tampon", "batiment", "tour", "test_tampon_tour.jpg"),
    ("tampon", "equipement", "sac", "tampon_equipement_sac.jpg"),
    ("tampon", "evenement", "grimoire", "tampon_evenement_grimoire.jpg"),
    ("tampon", "evenement", "etincelle", "tampon_evenement_etincelle.jpg"),
    ("tampon", "plan", "lettre", "tampon_plan_sceau.jpg"),
    ("tampon", "lieu", "carte", "tampon_lieu_carte.jpg"),
    ("esquisse", "unite", "casque", "test_esquisse_casque.jpg"),
    ("esquisse", "batiment", "tour", "test_esquisse_tour.jpg"),
]

# Portrait cards (unité / bâtiment / équipement / événement)
ICON_PORTRAIT = (32, 660, 110, 738)
# Lieu / plan (parchemin à gauche, picto en haut)
ICON_ROTATED = (200, 32, 274, 110)

MOCK_CARDS = {
    "unite": ("Soldat.png", ICON_PORTRAIT),
    "batiment": ("Tour_des_Mysteres.png", ICON_PORTRAIT),
    "equipement": ("Epee_Magique.png", ICON_PORTRAIT),
    "evenement": ("Eclair.png", ICON_PORTRAIT),
    "plan": ("Quartier_d_hiver.png", ICON_ROTATED),
    "lieu": ("Grotte.png", ICON_ROTATED),
}

SIZES = (64, 128, 256)


def to_ink(img: Image.Image, white_cut: float = 242, black_cut: float = 48) -> Image.Image:
    rgb = np.array(img.convert("RGB"), dtype=np.float32)
    luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    alpha = (white_cut - luma) / (white_cut - black_cut) * 255.0
    alpha = np.clip(alpha, 0, 255).astype(np.uint8)
    out = np.zeros((luma.shape[0], luma.shape[1], 4), dtype=np.uint8)
    out[:, :, 0] = INK[0]
    out[:, :, 1] = INK[1]
    out[:, :, 2] = INK[2]
    out[:, :, 3] = alpha
    return Image.fromarray(out, "RGBA")


def content_bbox(gray: np.ndarray, thresh: int = 248):
    ink = gray < thresh
    if not ink.any():
        return 0, 0, gray.shape[1] - 1, gray.shape[0] - 1
    ys, xs = np.where(ink)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def square_pad(img: Image.Image, pad: int, thresh: int = 248) -> Image.Image:
    gray = np.array(img.convert("L"))
    x0, y0, x1, y1 = content_bbox(gray, thresh)
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img.width - 1, x1 + pad)
    y1 = min(img.height - 1, y1 + pad)
    crop = img.crop((x0, y0, x1 + 1, y1 + 1))
    w, h = crop.size
    s = max(w, h)
    canvas = Image.new("RGB", (s, s), (255, 255, 255))
    canvas.paste(crop, ((s - w) // 2, (s - h) // 2))
    return canvas


def crop_equal_grid(img: Image.Image, rows: int = 2, cols: int = 5, pad: int = 10) -> list[Image.Image]:
    gray = np.array(img.convert("L"))
    x0, y0, x1, y1 = content_bbox(gray, 250)
    # tiny outer pad
    x0 = max(0, x0 - 4)
    y0 = max(0, y0 - 4)
    x1 = min(img.width - 1, x1 + 4)
    y1 = min(img.height - 1, y1 + 4)
    cell_w = (x1 - x0 + 1) / cols
    cell_h = (y1 - y0 + 1) / rows
    cells = []
    for r in range(rows):
        for c in range(cols):
            cx0 = int(round(x0 + c * cell_w))
            cy0 = int(round(y0 + r * cell_h))
            cx1 = int(round(x0 + (c + 1) * cell_w))
            cy1 = int(round(y0 + (r + 1) * cell_h))
            cell = img.crop((cx0, cy0, cx1, cy1))
            cells.append(square_pad(cell, pad=pad))
    return cells


def export_icon(icon: Image.Image, style: str, typ: str, filename: str) -> None:
    src_dir = ROOT / "src" / style / typ
    src_dir.mkdir(parents=True, exist_ok=True)
    icon.save(src_dir / filename, "PNG")
    for size in SIZES:
        d = ROOT / f"png_{size}" / style / typ
        d.mkdir(parents=True, exist_ok=True)
        resized = icon.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(d / filename, "PNG")


def process_sheets() -> None:
    planche_dir = ROOT / "planches"
    planche_dir.mkdir(parents=True, exist_ok=True)
    for style, meta in STYLES.items():
        for typ in TYPES:
            src = ASSETS / meta["file"].format(t=typ)
            img = Image.open(src).convert("RGB")
            img.save(planche_dir / f"{style}_{typ}.png", "PNG")
            cells = crop_equal_grid(img, pad=12 if style == "tampon" else 16)
            names = NAMES[typ]
            for i, (cell, name) in enumerate(zip(cells, names), start=1):
                # Replace Star-of-David stamp with the dedicated spark.
                if style == "tampon" and typ == "evenement" and name == "etincelle":
                    cell = Image.open(ASSETS / "tampon_evenement_etincelle.jpg").convert("RGB")
                    cell = square_pad(cell, pad=8)
                icon = to_ink(cell)
                export_icon(icon, style, typ, f"{i:02d}_{name}.png")
            print(f"sheet {style}/{typ}: {len(cells)} icons")


def process_hires() -> None:
    for style, typ, name, fname in HIRES:
        img = Image.open(ASSETS / fname).convert("RGB")
        icon = to_ink(square_pad(img, pad=6))
        idx = NAMES[typ].index(name) + 1
        # The individual render is cleaner than the sheet crop: it becomes the main file.
        export_icon(icon, style, typ, f"{idx:02d}_{name}.png")
        hires_dir = ROOT / "hires" / style / typ
        hires_dir.mkdir(parents=True, exist_ok=True)
        icon.save(hires_dir / f"{idx:02d}_{name}.png", "PNG")
        print(f"hires {style}/{typ}/{name} {icon.size}")


def cover_and_paste(card: Image.Image, box: tuple[int, int, int, int], icon: Image.Image) -> Image.Image:
    out = card.convert("RGBA").copy()
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # Cover old medallion with parchment circle so the old art does not bleed.
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse((x0 - 5, y0 - 5, x1 + 5, y1 + 5), fill=PARCHMENT)
    out = Image.alpha_composite(out, overlay)
    icon_r = icon.resize((w, h), Image.Resampling.LANCZOS)
    out.alpha_composite(icon_r, (x0, y0))
    return out


ESQUISSE_MOCK = {
    "unite": "03_heaume.png",
    "batiment": "01_tour.png",
    "equipement": "01_sac.png",
    "evenement": "03_eclair.png",
    "plan": "01_lettre.png",
    "lieu": "02_boussole.png",
}


def load_icon(style: str, typ: str, fname: str) -> Image.Image:
    stem = Path(fname).stem
    hires = ROOT / "png_256" / style / typ / f"{stem}_hires.png"
    if hires.exists():
        return Image.open(hires)
    return Image.open(ROOT / "png_256" / style / typ / fname)


def make_mockups() -> None:
    mock_dir = ROOT / "mockups"
    mock_dir.mkdir(parents=True, exist_ok=True)
    for typ, (card_name, box) in MOCK_CARDS.items():
        card = Image.open(CARTES / card_name)
        picks = [
            ("actuel", None),
            ("tampon", f"01_{NAMES[typ][0]}.png"),
            ("tampon", f"04_{NAMES[typ][3]}.png"),
            ("esquisse", ESQUISSE_MOCK[typ]),
        ]
        tiles = []
        labels = []
        for style, fname in picks:
            if style == "actuel":
                tiles.append(card.convert("RGBA"))
                labels.append("Actuel")
            else:
                icon = load_icon(style, typ, fname)
                tiles.append(cover_and_paste(card, box, icon))
                labels.append(f"{STYLES[style]['label']} · {NAME_LABELS[NAMES[typ][int(fname[:2]) - 1]]}")
        mock = compose_row(tiles, labels)
        mock.save(mock_dir / f"mockup_{typ}.png", "PNG")
        # zoom strip of the icon only
        zooms = []
        zlabels = []
        for tile, lab in zip(tiles, labels):
            x0, y0, x1, y1 = box
            pad = 18
            crop = tile.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
            zooms.append(crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.NEAREST))
            zlabels.append(lab)
        zoom = compose_row(zooms, zlabels, scale_cards=False)
        zoom.save(mock_dir / f"zoom_{typ}.png", "PNG")
        print(f"mockup {typ}")


def compose_row(cards: list[Image.Image], labels: list[str], scale_cards: bool = True) -> Image.Image:
    if scale_cards:
        cards = [c.resize((360, int(360 * c.height / c.width)), Image.Resampling.LANCZOS) for c in cards]
    gap = 16
    label_h = 36
    w = sum(c.width for c in cards) + gap * (len(cards) + 1)
    h = max(c.height for c in cards) + gap * 2 + label_h
    out = Image.new("RGB", (w, h), (22, 20, 22))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = font_b = ImageFont.load_default()
    x = gap
    for card, lab in zip(cards, labels):
        out.paste(card.convert("RGB"), (x, gap + label_h))
        draw.text((x, 12), lab, fill=(212, 180, 106), font=font_b)
        x += card.width + gap
    return out


def make_planches() -> None:
    """Contact sheets of all icons on parchment, one per style."""
    mock_dir = ROOT / "mockups"
    cell = 132
    pad = 10
    cols = 10
    rows = len(TYPES)
    header = 48
    for style, meta in STYLES.items():
        w = pad + cols * cell + pad
        h = header + pad + rows * (cell + 28) + pad
        img = Image.new("RGB", (w, h), (22, 20, 22))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
            font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except OSError:
            font = font_b = font_s = ImageFont.load_default()
        draw.text((pad, 12), f"{meta['label']} — 10 pictos × 6 types", fill=(212, 180, 106), font=font_b)
        for r, typ in enumerate(TYPES):
            y = header + pad + r * (cell + 28)
            draw.text((pad, y - 2), TYPE_LABELS[typ], fill=(185, 170, 150), font=font)
            for c, name in enumerate(NAMES[typ]):
                x = pad + c * cell
                tile = Image.new("RGB", (cell - 8, cell - 8), PARCHMENT[:3])
                icon = Image.open(ROOT / "png_128" / style / typ / f"{c + 1:02d}_{name}.png")
                icon = icon.resize((112, 112), Image.Resampling.LANCZOS)
                tile.paste(icon, (4, 4), icon)
                img.paste(tile, (x, y + 16))
        img.save(mock_dir / f"planche_{style}_parchemin.png", "PNG")
        print(f"planche {style}")

    # tiny-size comparison: actuel refs vs tampon 01 vs esquisse 01
    refs = {
        "unite": TYPES_DIR / "_references" / "unite_actuel.png",
        "batiment": TYPES_DIR / "_references" / "batiment_actuel.png",
        "equipement": TYPES_DIR / "_references" / "equipement_actuel.png",
        "evenement": TYPES_DIR / "_references" / "evenement_actuel.png",
        "plan": TYPES_DIR / "_references" / "plan_actuel.png",
        "lieu": TYPES_DIR / "_references" / "lieu_actuel.png",
    }
    sizes_show = (48, 64, 96)
    cols_s = 3
    rows_s = len(TYPES)
    cell_s = 120
    img = Image.new("RGB", (1120, header + rows_s * 150 + pad), (22, 20, 22))
    draw = ImageDraw.Draw(img)
    try:
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        font = font_b = ImageFont.load_default()
    draw.text((pad, 12), "Lisibilité à la taille réelle de la carte  (48 / 64 / 96 px)", fill=(212, 180, 106), font=font_b)
    for r, typ in enumerate(TYPES):
        y = header + r * 150
        draw.text((pad, y), TYPE_LABELS[typ], fill=(185, 170, 150), font=font)
        variants = [
            ("Actuel", Image.open(refs[typ]).convert("RGBA")),
            ("Tampon", load_icon("tampon", typ, f"01_{NAMES[typ][0]}.png")),
            ("Esquisse", load_icon("esquisse", typ, f"01_{NAMES[typ][0]}.png")),
        ]
        x = 100
        for lab, icon in variants:
            draw.text((x, y), lab, fill=(232, 220, 200), font=font)
            xx = x
            ic0 = icon.convert("RGBA") if icon.mode != "RGBA" else icon
            for sz in sizes_show:
                tile = Image.new("RGBA", (sz + 16, sz + 16), PARCHMENT)
                ic = ic0.resize((sz, sz), Image.Resampling.LANCZOS)
                tile.paste(ic, (8, 8), ic)
                img.paste(tile.convert("RGB"), (xx, y + 22))
                xx += sz + 22
            x += 330
    img.save(mock_dir / "lisibilite_petite_taille.png", "PNG")
    print("petite taille")


def write_catalog() -> None:
    catalog = {
        "styles": {k: {"label": v["label"], "hint": v["hint"]} for k, v in STYLES.items()},
        "types": {
            t: {
                "label": TYPE_LABELS[t],
                "icons": [{"id": f"{i:02d}_{n}", "name": n, "label": NAME_LABELS[n]} for i, n in enumerate(NAMES[t], 1)],
            }
            for t in TYPES
        },
    }
    (ROOT / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")


def write_html() -> None:
    cards = []
    for typ in TYPES:
        items = []
        for i, name in enumerate(NAMES[typ], 1):
            items.append(
                f"""<article class="card" data-name="{name}">
  <div class="tile"><img data-src="{typ}/{i:02d}_{name}.png" alt="{NAME_LABELS[name]}"></div>
  <b>{i:02d} · {NAME_LABELS[name]}</b>
</article>"""
            )
        cards.append(
            f"""<section id="{typ}">
  <h2>{TYPE_LABELS[typ]}</h2>
  <p class="lead">Dix lectures, même famille. La 01 reprend le symbole actuel (casque, tour, sac, grimoire, lettre, carte).</p>
  <div class="grid">
    {''.join(items)}
  </div>
</section>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Icônes tampon / esquisse — Pixel of Glory</title>
  <style>
    :root {{
      --bg: #161416;
      --panel: #221e22;
      --ink: #efe6d6;
      --muted: #b9aa96;
      --gold: #d4b46a;
      --parchment: #e2c792;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: "Segoe UI", Tahoma, sans-serif; }}
    header {{ padding: 28px 32px 12px; border-bottom: 1px solid #3a3330; }}
    header h1 {{ margin: 0 0 6px; font-size: 1.55rem; }}
    header p {{ margin: 0; color: var(--muted); max-width: 860px; line-height: 1.45; }}
    .toolbar {{
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      padding: 16px 32px; position: sticky; top: 0; background: #161416ee; z-index: 2;
      backdrop-filter: blur(8px);
    }}
    .toolbar button, .toolbar a {{
      background: #2c272c; color: var(--ink); border: 1px solid #4a4240;
      border-radius: 999px; padding: 6px 12px; cursor: pointer; font-size: 13px; text-decoration: none;
    }}
    .toolbar button.active {{ background: var(--gold); color: #1a140c; border-color: var(--gold); font-weight: 700; }}
    .toolbar .hint {{ color: var(--muted); font-size: 12px; margin-left: 8px; }}
    main {{ padding: 8px 32px 64px; }}
    section {{ margin: 28px 0 40px; }}
    h2 {{ margin: 0 0 6px; font-size: 1.2rem; color: var(--gold); }}
    .lead {{ color: var(--muted); margin: 0 0 16px; font-size: .95rem; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 14px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid #3a3330;
      border-radius: 12px;
      padding: 10px 10px 12px;
      text-align: center;
    }}
    .tile {{
      width: 128px; height: 128px; margin: 0 auto 8px;
      border-radius: 10px;
      display: grid; place-items: center;
      background: var(--parchment);
    }}
    body.bg-dark .tile {{ background: #1b181c; }}
    body.bg-check .tile {{
      background-color: #cfcfcf;
      background-image:
        linear-gradient(45deg, #9a9a9a 25%, transparent 25%),
        linear-gradient(-45deg, #9a9a9a 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #9a9a9a 75%),
        linear-gradient(-45deg, transparent 75%, #9a9a9a 75%);
      background-size: 16px 16px;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0;
    }}
    .tile img {{ width: 112px; height: 112px; }}
    .card b {{ display: block; font-size: .92rem; }}
    .mock img, .planche {{ width: min(100%, 1100px); border-radius: 10px; border: 1px solid #3a3330; }}
    footer {{ padding: 0 32px 40px; color: var(--muted); font-size: .85rem; }}
  </style>
</head>
<body class="bg-parchment" data-style="tampon" data-size="128">
  <header>
    <h1>Icônes de type — tampon &amp; esquisse</h1>
    <p>
      Noir et blanc, peu de détails, lisibles tout petits sur le parchemin.
      <strong>Tampon</strong> : encre, cercle un peu effacé comme un cachet de poste.
      <strong>Esquisse</strong> : trait de crayon simple.
      Une vingtaine de propositions par type (10 tampon + 10 esquisse), plus une série crayon plus travaillée.
    </p>
  </header>
  <div class="toolbar">
    <button class="active" data-style="tampon">Tampon</button>
    <button data-style="esquisse">Esquisse</button>
    <button data-style="crayon">Crayon</button>
    <button data-bg="bg-parchment" class="active">Fond parchemin</button>
    <button data-bg="bg-dark">Fond sombre</button>
    <button data-bg="bg-check">Damier</button>
    <span class="hint" id="style-hint">Encre noire, cercle un peu usé comme un tampon de poste.</span>
  </div>
  <main>
    <section>
      <h2>À la taille de la carte</h2>
      <p class="lead">48 / 64 / 96 px — c’est à peu près le médaillon actuel. Le tampon reste un pictogramme, l’ancien pixel se noie.</p>
      <img class="planche" src="mockups/lisibilite_petite_taille.png" alt="Comparaison petite taille">
    </section>
    <section>
      <h2>Planche tampon</h2>
      <img class="planche" src="mockups/planche_tampon_parchemin.png" alt="Planche tampon">
    </section>
    <section>
      <h2>Planche esquisse</h2>
      <img class="planche" src="mockups/planche_esquisse_parchemin.png" alt="Planche esquisse">
    </section>
    {''.join(cards)}
    <section>
      <h2>Sur les cartes</h2>
      <p class="lead">Médaillon actuel, tampon du symbole actuel, autre tampon, esquisse. Le zoom dessous est à 3×.</p>
      {''.join(f'<div class="mock" style="margin-top:18px"><img src="mockups/mockup_{t}.png" alt="Mockup {TYPE_LABELS[t]}"></div><div class="mock" style="margin-top:8px"><img src="mockups/zoom_{t}.png" alt="Zoom {TYPE_LABELS[t]}"></div>' for t in TYPES)}
    </section>
  </main>
  <footer>
    Dossier <code>Icones_Types/nb/</code> — PNG 64 / 128 / 256, fond transparent.
    Rien n’est encore branché sur le générateur de cartes.
    Les pictos pixel colorés restent dans <a href="../apercu.html">Icones_Types/apercu.html</a>.
  </footer>
  <script>
    const hints = {{
      tampon: "Encre noire, cercle un peu usé comme un tampon de poste.",
      esquisse: "Trait de crayon simple, presque un pictogramme.",
      crayon: "Esquisse plus travaillée — plus de volume, un peu plus chargée à 64 px."
    }};
    const styleBtns = document.querySelectorAll('[data-style]');
    const bgBtns = document.querySelectorAll('[data-bg]');
    function applyStyle(style) {{
      document.body.dataset.style = style;
      document.querySelectorAll('.tile img').forEach(img => {{
        img.src = 'png_128/' + style + '/' + img.dataset.src;
      }});
      document.getElementById('style-hint').textContent = hints[style];
      styleBtns.forEach(b => b.classList.toggle('active', b.dataset.style === style));
    }}
    styleBtns.forEach(btn => btn.addEventListener('click', () => applyStyle(btn.dataset.style)));
    bgBtns.forEach(btn => btn.addEventListener('click', () => {{
      document.body.classList.remove('bg-parchment', 'bg-dark', 'bg-check');
      document.body.classList.add(btn.dataset.bg);
      bgBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}));
    applyStyle('tampon');
  </script>
</body>
</html>
"""
    (ROOT / "apercu.html").write_text(html, encoding="utf-8")


def main() -> None:
    process_sheets()
    process_hires()
    make_mockups()
    make_planches()
    write_catalog()
    write_html()
    print("done", ROOT)


if __name__ == "__main__":
    main()
