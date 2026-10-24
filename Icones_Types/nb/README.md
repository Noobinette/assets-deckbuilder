# Icônes de type — tampon & esquisse

Noir et blanc, peu de détails, prévus pour le petit médaillon sur le parchemin (~70 px).

Les pictos pixel colorés (`../png_128/`, casque, tour, sac…) se noient à cette taille. Ici l’idée est un **cachet d’encre** (cercle un peu usé, comme un tampon de poste) ou un **trait de crayon**.

Ouvrir [`apercu.html`](apercu.html) pour tout comparer.

## Styles

| Style | Fichiers | Intention |
|---|---|---|
| **Tampon** | `png_*/tampon/` | Encre noire, silhouette, cercle usé. Le plus lisible tout petit. |
| **Esquisse** | `png_*/esquisse/` | Trait de crayon simple, presque un pictogramme. |
| **Crayon** | `png_*/crayon/` | Esquisse plus travaillée. Plus de volume, un peu plus chargée à 64 px. |

Dix lectures par type × tampon + esquisse = **20 propositions par type**. La série crayon est en plus.

## Types

| Type | Symbole actuel | Variantes tampon / esquisse |
|---|---|---|
| **Unité** | Casque | casque, casque de profil, heaume, épées, bouclier, lance, soldat, gantelet, cor, bannière |
| **Bâtiment** | Tour | tour, tour au drapeau, donjon, château, portail, maison, rempart, phare, pont-levis, grange |
| **Équipement** | Sac | sac, coffre, épée, anneau, sacoche, hache, marteau, arc, amulette, bottes |
| **Événement** | Grimoire | grimoire, parchemin, éclair, potion, rune, flamme, étincelle, lune, sablier, œil |
| **Plan** | Parchemin scellé | lettre, rouleau, tactique, plume, décret, enveloppe, cachet, pions, flèches, pli |
| **Lieu** | Carte | carte, boussole, drapeau, montagne, borne, arbre, pont, grotte, rose des vents, collines |

Les variantes **01** reprennent le symbole actuel, en version tampon ou esquisse.

## Ce qui reste clair à ~64 px

- **Unité** — tampon `casque` ou `epees`
- **Bâtiment** — tampon `tour`
- **Équipement** — tampon `sac` ou `epee`
- **Événement** — tampon `grimoire` ou `eclair`
- **Plan** — tampon `lettre` ou `rouleau`
- **Lieu** — tampon `boussole` ou `drapeau`

## Dossiers

| Dossier | Usage |
|---|---|
| `png_64/` | taille réelle sur la carte |
| `png_128/` | preview |
| `png_256/` | composition |
| `hires/` | rendus individuels des 01 (et de l’étincelle) |
| `src/` | recadrages natifs, fond transparent |
| `planches/` | planches source 5×2 |
| `mockups/` | cartes actuelles vs propositions |
| `scripts/preparer.py` | découpe, encre, mockups |

PNG 32 bits, encre noire, **fond transparent** — collé directement sur le parchemin beige.

Rien n’est encore branché sur le générateur de cartes.
