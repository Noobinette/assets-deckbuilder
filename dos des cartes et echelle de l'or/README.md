# Échelle de l’OR — propositions

Carte d’aide de jeu (pas une carte du deck) : on y **déplace une pièce d’or**.

Une seule piste partagée, comme dans les règles :

`joueur A : 6-5-4-3-2-1` → `0` → `1-2-3-4-5-6 : joueur B`

Le pion part sur **0**. Payer un coût, c’est pousser le pion vers l’adversaire. Il ne dépasse jamais 6.

## Lecture des chiffres

Sur le croquis à la main, tous les chiffres étaient dans le même sens. Ici, **chaque joueur lit son côté à l’endroit** : le demi-serpentin d’en face est tourné de 180°.

## Les 5 exemples

| Fichier | Fond | Serpentin | Marqueurs |
| --- | --- | --- | --- |
| `propositions/01_donjon_serpentin.png` | `Fond_Carte_Or.jpg` | S fluide | pièces d’or |
| `propositions/02_donjon_manuscrit.png` | `Fond_Carte_Or.jpg` | S en créneau (croquis) | pièces d’or |
| `propositions/03_donjon_piste.png` | `Fond_Carte_Or.jpg` | S un peu plus serré | pièces + piste pierre/or |
| `propositions/04_salle_tresor.png` | salle du trésor | S fluide | pièces d’or |
| `propositions/05_table_bois.png` | parquet | S en créneau | cases parchemin |

Aperçu : `propositions/apercu.html`

Format : 750×1050, comme les cartes du jeu.

## Régénérer

```bash
python3 "dos des cartes et echelle de l'or/scripts/generer_echelle_or.py"
```
