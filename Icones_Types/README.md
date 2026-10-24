# Icônes de type — propositions

Deux pistes :

1. **Tampon / esquisse, noir et blanc** — [`nb/apercu.html`](nb/apercu.html)  
   Une vingtaine de pictos par type, encre ou trait de crayon, peu de détails. C’est la réponse au « trop de détail sur une petite carte ».
2. **Pixel art 32-bit, couleur** — [`apercu.html`](apercu.html)  
   Cinq lectures par type, sans médaillon. Plus riches, moins lisibles à ~70 px.

Les pictos actuels (casque, tour, sac, grimoire, parchemin scellé, carte) se lisent mal sur le parchemin beige.

## Pixel art 32-bit (cette page)

## Types

| Type | Icône actuelle | Variantes proposées |
|---|---|---|
| **Unité** | Casque | casque, casque ailé, épées croisées, bouclier, buste de soldat |
| **Bâtiment** | Tour | tour, château, portail, maison à colombages, rempart |
| **Équipement** | Sac à dos | sac, coffre, épée, anneau, sacoche |
| **Événement** | Grimoire | grimoire, parchemin, éclair, potion, rune |
| **Plan** | Parchemin scellé | sceau, rouleau, carte tactique, plume, décret |
| **Lieu** | Carte | carte, boussole, drapeau, montagne, borne |

Les variantes **01** reprennent le symbole actuel, plus soigné. Les autres disent la même chose avec un autre objet.

## Tailles

| Dossier | Usage |
|---|---|
| `png_64/` | taille proche du picto sur la carte (~70 px) |
| `png_128/` | preview et composition |
| `png_512/` | source haute définition |
| `mockups/` | planches + cartes actuelles vs propositions |
| `_references/` | recadrages des pictos actuels |

## Lisibilité à petite taille

Ce qui reste le plus clair à ~64–70 px :

- **Unité** — `casque` ou `epees`
- **Bâtiment** — `tour` ou `rempart`
- **Équipement** — `sac` ou `anneau`
- **Événement** — `grimoire` ou `eclair`
- **Plan** — `sceau` ou `rouleau`
- **Lieu** — `boussole` ou `drapeau`

Les lectures plus chargées (`buste`, `carte`, `tactique`, `chateau`) passent mieux en 128 px.
