# Échelle de l’OR — 6 propositions

Carte d’aide de jeu (pas une carte du deck) : on y **déplace une pièce d’or**.

Une seule piste partagée, comme dans les règles :

`joueur A : 6-5-4-3-2-1` → `0` → `1-2-3-4-5-6 : joueur B`

Le pion part sur **0**. Payer un coût, c’est pousser le pion vers l’adversaire. Il ne dépasse jamais 6.

## Lecture des chiffres

Chaque joueur lit **son côté à l’endroit** : le demi-serpentin d’en face est tourné de 180°. Le **0** est au milieu, un peu plus grand, posé sur un médaillon.

Les marqueurs sont des **pièces rondes** (pas des cases carrées). La piste est un **S / serpentin**, pas une grille. Les 13 pièces sont posées à **pas quasi égal** le long du S.

## Les 6 exemples

| Fichier | Fond | Idée |
| --- | --- | --- |
| `propositions/01_donjon_serpentin.png` | ton `Fond_Carte_Or.jpg` | S ouvert, pièces rondes |
| `propositions/02_donjon_enroule.png` | ton `Fond_Carte_Or.jpg` | S plus enroulé, virages plus ronds |
| `propositions/03_tresor_moitie.png` | salle au trésor | **bas = coffres**, **haut = porte** ; le 0 est sur le seuil |
| `propositions/04_tresor_cotes.png` | salle au trésor de côté | **coffres à gauche**, **escalier à droite** ; le S passe dans l’arche |
| `propositions/05_mine_galerie.png` | mine | galerie, wagonnet, lanternes |
| `propositions/06_mine_filon.png` | mine | filons d’or dans la roche |

Aperçu : `propositions/apercu.html`

Format : 750×1050, comme les cartes du jeu.

## Régénérer

```bash
python3 "dos des cartes et echelle de l'or/scripts/generer_echelle_or.py"
```
