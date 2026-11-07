# Boîte — gabarit paysage

Ouvrir [`apercu.html`](apercu.html).

## Corrections d’orientation

Sur le filet, tournés de **180°** : A (rabat), C (oreilles du couvercle), E (dessous), F (rabats latéraux extérieurs), H (avant). G (côtés intérieurs) et D (dos) restent dans le même sens.

Léger éclaircissement sur toutes les faces.

## Zones noires à gauche / droite de D et H

Ce sont des **rabats du carton** (pas des faces visibles). Elles étaient vides par oubli. Remplies de pierre, **sans logo**.

## Deux traitements pour A, D, H

Plus de personnages coupés sur les bandes.

| Variante | A (rabat) | D (dos) | H (avant) | Fichier |
|---|---|---|---|---|
| **Combat** (défaut) | L’incantation | Le choc | Après le coup | `exemple_net_combat.jpg` |
| **Pierre** | Pierre + wordmark | Pierre + wordmark | Pierre + wordmark | `exemple_net_pierre.jpg` |

## Dessous (E)

Tournées de 180° sur le filet. Défaut : victoire du chevalier.

| Fichier | Sujet |
|---|---|
| `faces/dessous.jpg` | Victoire du chevalier (nécromancien à terre) |
| `faces/dessous_victoire_necromancien.jpg` | Victoire du nécromancien (chevalier à genoux) |
| `faces/dessous_lendemain.jpg` | Personne : robe, épée, bouclier |
| `faces/dessous_vide.jpg` | Cour vide |

Sources 16:9 dans `sources/dessous_variantes/`.

## Calques paysage + parchemin

`sources/paysage_01.jpg` … `05.jpg` et `sources/parchemin.png`. Recadrage 70×35 cm : `sources/print_70x35/`.

Relancer : `python3 Boite/gabarit/scripts/composer.py`
