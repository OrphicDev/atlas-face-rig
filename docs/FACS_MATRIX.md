# Matrice FACS — actions faciales

**État : aucune action implémentée.** F0 est terminée, F1 n'a pas commencé. Ce
document est le registre que chaque action devra remplir avant d'être comptée.

Colonnes obligatoires — une action sans preuve ne compte pas :

| colonne | ce qu'elle contient |
| --- | --- |
| `id` | identifiant stable, `AU06`, `AU12`… |
| `nom` | nom anatomique |
| `contrôleur` | `CTRL_…`, avec son axe et sa plage |
| `côté` | `.L`, `.R` ou axial |
| `amplitude` | déplacement mesuré en mm à la valeur 1 |
| `statut` | `absent` · `prototype` · `mesuré` · `validé` |
| `tests` | quels critères passent, avec leurs chiffres |
| `rendus` | chemin des planches-contact |

## Registre

| id | nom | contrôleur | côté | amplitude | statut | tests | rendus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | **aucune action** | — | — |

## Ce que la mesure F0 impose déjà à cette matrice

- **Le miroir se fait par indice de sommet**, pas par position : la topologie est
  exactement symétrique (bijection involutive, 0 arête et 0 face orphelines),
  alors que la géométrie ne l'est pas (0,083 mm de médiane sur le visage). Une
  action `.L` mirroitée par position introduirait cette asymétrie dans la
  déformation ; par indice, elle ne l'introduit pas.
- **Les shape keys se posent sur la cage de 3 242 sommets**, jamais sur le
  maillage subdivisé — 4× moins de points de contrôle pour le même geste.
- **La subdivision atténue** : mesuré, 4 mm posés sur la cage rendent 1,52 mm au
  clignement et 2,99 mm à la fermeture labiale. Une amplitude cible se règle
  après subdivision, pas avant.
- **Toute commande à 0 doit rendre le neutre à moins de 0,01 mm.** Les deux voies
  du banc F0.2 rendent 0,000000 mm ; c'est la référence à tenir.
- **Zones à surveiller**, nommées par la mesure : le philtrum et la lèvre
  inférieure portent 14 triangles ; la paupière n'a que 4 boucles dans 5,5 mm ;
  les narines n'ont que 7 à 8 sommets de pourtour.


> **État F0 (2026-08-16, commit `ab26ab2`).** F0 est **incomplète** : 167 sondes, 154 réussies, 10 échec(s), 3 sautée(s). Vérité unique : [`reports/f0-final/RAPPORT_F0_FINAL.md`](../reports/f0-final/RAPPORT_F0_FINAL.md). F1 n'a pas commencé.
