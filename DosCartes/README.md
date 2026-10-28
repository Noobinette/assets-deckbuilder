# DosCartes — logos et fonds séparés

Tout logo se pose sur tout fond. PNG 8 bits, fonds 750×1050
(sauf le fond perdu livre : 820×1120).

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

Deux familles : cuir plat 180°-symétrique (`01`–`05`) et style livre cuir brun (`06`).

| Fichier | Origine |
|---|---|
| `01_cuir_brun.png` | cuir des dos 03 / 03b / 03e |
| `02_cuir_sombre.png` | même grain, plus profond |
| `03_losanges_bordeaux.png` | nouveau |
| `04_obsidienne.png` | nouveau |
| `05_emeraude.png` | nouveau |
| `06_livre_brun.png` | grimoire cuir brun, ras le livre |
| `06_livre_brun_fondperdu.png` | même livre + 3 mm (35 px) de noir de chaque côté, 820×1120 |

Quatre dos livre + logo 03e (`exemples/`) : droit et 90° antihoraire, ras et fond perdu.
Alternatives `*_plat_*` : même logo, centré sur le plat (reliure ignorée).

Ouvrir `apercu.html` pour tout voir, y compris des exemples logo + fond.

Regénérer les logos et les fonds 01–05 : `python3 DosCartes/scripts/separer_logos_fonds.py`  
Regénérer les deux fonds livre : `python3 DosCartes/scripts/preparer_livre_brun.py`
