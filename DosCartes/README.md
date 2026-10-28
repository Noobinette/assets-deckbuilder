# DosCartes — logos et fonds séparés

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

Deux familles : cuir plat 180°-symétrique (`01`–`05`) et style livre cuir brun avec tranche (`06`).

| Fichier | Origine |
|---|---|
| `01_cuir_brun.png` | cuir des dos 03 / 03b / 03e |
| `02_cuir_sombre.png` | même grain, plus profond |
| `03_losanges_bordeaux.png` | nouveau |
| `04_obsidienne.png` | nouveau |
| `05_emeraude.png` | nouveau |
| `06_livre_brun.png` | grimoire cuir brun, cadre or complet (pas coupé) |

Ouvrir `apercu.html` pour tout voir, y compris des exemples logo + fond.

Regénérer les logos et les fonds 01–05 : `python3 DosCartes/scripts/separer_logos_fonds.py`
(le fond livre `06` n’est pas écrasé).
