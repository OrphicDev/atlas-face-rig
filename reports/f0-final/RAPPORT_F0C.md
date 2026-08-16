# F0-C — mâchoire

**10 sondes sur 10.** Le prototype est mesuré, pas illustré.

## Masque mandibulaire — 8/8

`rig/build-jaw-mask.py`, diffusion **géodésique** sur le graphe des arêtes,
graines dérivées des repères **déjà audités** — jamais d'un seuil Z.

| contrôle | résultat |
| --- | ---: |
| poids dans [0, 1] | oui |
| marge labiale inférieure | **1,0** |
| lèvre supérieure hors commissures | **0,0** |
| commissures (partagées par les deux lèvres) | **0,740**, intermédiaire |
| crâne | **0,0** |
| bas du cou | **0,0** |
| graines des deux côtés de la mandibule | 51 / 51 |

281 sommets pleins, 2 516 nuls.

> Deux sommets étaient à la fois graine mandibulaire **et** exclusion crânienne :
> les **commissures**, qui appartiennent aux deux lèvres. Les retirer des deux
> ensembles et laisser la diffusion leur donner un poids intermédiaire est la
> seule lecture anatomique juste.

## Axe de charnière — mesuré, pas supposé

Pivot **`[1,46299 ; −0,05097 ; 0,74003]`**, milieu des deux conduits auditifs
mesurés en F0. Axe à **0,8625°** de X monde. L'écart des deux condyles
(1,72 mm en Z, 1,18 mm en Y) est l'asymétrie du visage lui-même, déjà publiée.

## Cinq angles

| angle | jour central | marge inférieure | menton (x, y, z) mm |
| ---: | ---: | ---: | --- |
| 0° | 3,559 mm | 0,00 | 0 · 0 · 0 |
| 5° | 11,801 | 9,46 | −0,10 · +7,75 · −3,02 |
| 10° | 21,378 | 18,91 | −0,20 · +15,73 · −5,34 |
| 20° | 40,300 | 37,09 | −0,37 · +30,13 · −8,58 |
| 32° | **61,850** | **57,80** | −0,53 · +46,84 · −8,93 |

Jour strictement croissant · 0° rend le neutre à **0,000133 mm** · crâne et
lèvre supérieure **exactement fixes** · bas du cou fixe · transformation rigide
respectée à **0,000000 mm** sur les sommets entièrement entraînés.

## Deux mesures fausses, prises avant tout verdict

**Le « jour central » était la largeur de la bouche.** La première version
prenait le maximum sur *tous* les couples haut/bas et rendait **47 mm au
neutre** — la distance commissure à commissure. Elle mesure désormais les deux
sommets les plus proches du plan sagittal : **3,559 mm au neutre**, ce qui est
la fente réelle.

**L'erreur rigide de 2,34 mm n'était pas une faute de matrice.** Elle portait
sur les sommets de poids ≥ 0,95 : à 0,95, le mélange laisse 5 % du déplacement,
soit 2,3 mm sur une course de 60. Restreinte aux sommets **entièrement**
entraînés, elle vaut **0,000000 mm**.

## Réserve à porter en F1

Le menton recule de **46,8 mm** pour ne descendre que de **8,9 mm** à 32°. Une
charnière pure autour d'un axe situé haut et en arrière donne mathématiquement
ces composantes, mais une mandibule réelle descend davantage qu'elle ne recule.
La translation antéro-inférieure (6 mm à partir de 0,35) ne compense pas cet
écart. **Ce n'est pas validé comme trajectoire finale** : le pivot ou la
répartition rotation/translation devra être repris quand l'os permanent sera
construit.
