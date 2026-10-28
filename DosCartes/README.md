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

Deux familles :

- **Cuir plat** (`01`–`05`) : cadre or simple, 180°-symétriques, **sans** tranche de livre.
- **Style livre** (`06`–`09`) : tranche à gauche, cadre géométrique or, centre vide pour le logo.

| Fichier | Origine |
|---|---|
| `01_cuir_brun.png` | cuir des dos 03 / 03b / 03e |
| `02_cuir_sombre.png` | même grain, plus profond |
| `03_losanges_bordeaux.png` | nouveau |
| `04_obsidienne.png` | nouveau |
| `05_emeraude.png` | nouveau |
| `06_livre_brun.png` | grimoire brun or, dans l’esprit du dos 01 |
| `07_livre_bordeaux.png` | grimoire bordeaux |
| `08_livre_nuit.png` | grimoire bleu nuit |
| `09_livre_foret.png` | grimoire vert forêt |

Ouvrir `apercu.html` pour tout voir, y compris des exemples logo + fond.

Regénérer les logos et les fonds 01–05 : `python3 DosCartes/scripts/separer_logos_fonds.py`  
(les fonds livre `06`–`09` ne sont pas écrasés).
