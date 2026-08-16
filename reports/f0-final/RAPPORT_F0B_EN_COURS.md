# F0-B — avancement (B.0 à B.12)

**F0-B n'est pas terminée.** 9 sondes sur 18 passent. `mouth_close` passe trois
critères sur quatre ; le clignement reste au-dessus du seuil.

## Où en sont les trois poses, à t = 1

| pose | départ `c0885ae` | cage | dense | seuil | arêtes |
| --- | ---: | ---: | ---: | ---: | --- |
| `blink_L` | 2,3937 | 0.2752 | 0.2682 | 0.20 | 0.31–2.29 |
| `blink_R` | 4,0046 | 0.2860 | 0.4779 | 0.20 | 0.39–2.35 |
| `mouth_close` | 0,9688 | 0.2271 | 0.2394 | 0.30 | 0.52–1.40 |

Retour au neutre **exact** et jour **monotone** sur les onze valeurs, pour les
trois poses. La voie dense est **mesurée**, plus aucun SKIP.

## Une hypothèse posée, testée, et réfutée

J'avais écrit que le résidu venait de la discrétisation : deux arcs de 10 et 12
sommets mesurés sur 64 échantillons uniformes. **C'est faux.** Mesuré aux
sommets eux-mêmes, le jour vaut **0,3298 mm** contre **0,2752 mm** aux 64
échantillons — donc *plus grand*, pas plus petit. Le résidu vient de mon champ
de déformation, pas de la façon dont je le mesure.

## Deux corrections réelles

**L'itération sur le résidu.** Viser son vis-à-vis au neutre ne suffit pas : le
jour est mesuré après déformation. Une boucle amortie mesure le résidu sur les
échantillons et le redistribue. Les jours sont passés de 0,44/0,41/0,48 à
**0,275/0,286/0,227 mm**.

**Le falloff propageait n'importe quoi.** Un sommet hors marge suivait la
*moyenne* de toutes les graines à portée euclidienne — donc une direction qui
n'était celle d'aucune marge. Dix arêtes **hors marge** dépassaient 2,0×. Chaque
sommet suit maintenant la cible de la graine dont il descend **géodésiquement**,
et le pire ratio est tombé de **2,90 à 2,35**. `mouth_close` rentre entièrement
dans les bornes (0,52–1,40).

## B.12 — whitelist d'arêtes

`config/deformation-edge-whitelist.json` : 21 entrées, chacune avec pose, arête,
ratio, zone et justification. Seules les arêtes **sur la marge de contact** sont
justifiables — une marge se comprime en se fermant, c'est le geste lui-même.
Les arêtes hors marge ne le sont pas et ont été corrigées à la source.

## Ce qui bloque encore

Le clignement laisse **0,27 mm** au lieu de 0,20, et la séparation signée
descend à **−0,09 mm** au lieu de −0,05 : les deux marges se croisent
légèrement quelque part. Ce n'est ni la mesure ni la discrétisation — c'est la
répartition du déplacement le long de l'arc. Restent aussi B.13 (preuves à
caméra fixe) et la décision du §12.
