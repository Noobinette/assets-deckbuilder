# Jetons — Pixel ou Glory

Logos pour le centre d’un jeton de poker (pile ou face). Les lettres sont celles du logo du jeu, en pixel art, recadrées pour le cercle central.

Chaque fichier est un **PNG 2400×2400**, fond transparent. Le configurateur demande au moins 600×600. Le mot est centré et tient dans le cercle : on laisse le curseur de taille vers **le centre**, pas sur « whole chip », sinon le mot recouvre les pastilles bleu et rouge.

## La paire du logo

Recto, les couleurs justes : Pixel en bleu, Glory en rouge, filet or.

| Face | Fichier |
|---|---|
| Pixel | `pixel-bleu-or.png` |
| Glory | `glory-rouge-or.png` |

Dos, couleurs échangées, filet or gardé. Un filtre « inverser » du logiciel retournerait aussi l’or : mieux vaut ces deux fichiers.

| Face | Fichier |
|---|---|
| Pixel en rouge | `pixel-rouge-or.png` |
| Glory en bleu | `glory-bleu-or.png` |

## Les autres variantes

Même dessin, autre couleur. On prend un Pixel et un Glory de la même colonne.

| | Pixel | Glory |
|---|---|---|
| Or | `pixel-or.png` | `glory-or.png` |
| Bleu et rouge, sans or | `pixel-bleu.png` | `glory-rouge.png` |

Ouvrir `apercu.html` ou `planche.jpg` pour comparer sur l’ivoire du centre.

Régénérer : `python3 generer.py` (lit `vitrine/img/logo.png`).
