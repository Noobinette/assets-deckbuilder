# Boîte — gabarit paysage

Exemple d’habillage du gabarit (filet de découpe) : **dessus** et **dessous** différents, **logo Pixel of Glory** sur les côtés. Les 5 paysages et le parchemin restent des calques séparés, à superposer.

Ouvrir [`apercu.html`](apercu.html).

## Exemple sur le gabarit

| Fichier | Rôle |
|---|---|
| `exemple_net.jpg` | Filet complet, visuels + traits de découpe |
| `exemple_mockup.jpg` | Faces vues une fois la boîte montée |
| `gabarit_source.png` | Gabarit d’origine (traits seuls) |

### Faces

| Face | Image | Contenu |
|---|---|---|
| **Dessus** (couvercle) | `faces/dessus.jpg` | Bataille nécromancien / chevalier, **sans logo** |
| **Dessous** (fond) | `faces/dessous.jpg` | Même cour, château vide, **sans logo** |
| **Côtés** | `faces/cote_gauche.jpg`, `cote_droit.jpg` | Pierre + logo empilé (orientation filet) |
| **Côté débout** | `faces/cote_debout.jpg` | Même logo, vu une fois la boîte posée |
| **Avant / rabat** | `faces/avant.jpg` | Bande pierre + wordmark or |

Les côtés du filet ont le logo tourné à 90° : une fois le carton plié, les lettres se lisent à l’endroit.

## 5 paysages + parchemin (calques)

Style de l’illustration fournie, **sans titre**, format paysage.

| Fichier | Usage |
|---|---|
| `sources/paysage_01.jpg` … `05.jpg` | 70 cm de large, 16:9, 150 dpi (~70 × 39,4 cm) |
| `sources/parchemin.png` | Même taille, **fond transparent**, zone d’écriture vide |
| `sources/print_70x35/` | Recadrage 2:1, 70 × 35 cm à 150 dpi |

Superposition : le paysage en dessous, le PNG du parchemin au-dessus, le texte par-dessus le parchemin.

`web/` contient des copies 1920×1080 pour l’aperçu.

## Variantes

1. Composition proche de l’originale  
2. Plus de château, plus de squelettes  
3. Cape du chevalier au vent, vortex plus large  
4. Colonne au premier plan  
5. Cour plus ouverte, portail centré  

Le dessous de boîte (`sources/dessous_chateau.jpg`) reprend le lieu **sans** les personnages.

Relancer : `python3 Boite/gabarit/scripts/composer.py`
