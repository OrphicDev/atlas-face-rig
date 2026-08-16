# Décision — ordre Armature / Multires

```
ORDRE RETENU : ARMATURE PUIS MULTIRES
```

## Ce que le banc a réellement mesuré

Deux scènes construites par script, dont le manifeste prouve qu'elles ne
diffèrent **que** par l'ordre des deux modificateurs — mêmes objets, mêmes
shape keys, mêmes poids, mêmes UV, même niveau de Multires.

Six poses, cinq échauffements puis **vingt évaluations chronométrées** par pose,
chaque voie dans un processus Blender distinct.

| pose | écart au neutre, A | écart au neutre, B | mêmes UV |
| --- | ---: | ---: | :---: |
| `neutral` | 0,0000 mm | 0,0000 mm | oui |
| `blink_L_100` | 8,4962 | **8,4962** | oui |
| `blink_R_100` | 8,4264 | **8,4264** | oui |
| `mouthClose_100` | 1,8196 | **1,8196** | oui |
| `jaw_20` | 42,6041 | **42,6041** | oui |
| `jaw_32` | 67,6269 | **67,6269** | oui |

**La géométrie est strictement identique dans les deux ordres**, à la
quatrième décimale du millimètre, et les empreintes UV coïncident. Le retour au
neutre vaut `0,000000000 mm` des deux côtés.

| | A — Armature puis Multires | B — Multires puis Armature |
| --- | ---: | ---: |
| somme des temps médians, six poses | **0,22496 s** | 0,22635 s |
| médiane `jaw_32` | 0,03734 s | 0,03741 s |

## Pourquoi A, et sur quoi la décision ne repose pas

L'écart de temps est de **0,6 %** — c'est du bruit, pas un argument. **Le banc
ne départage pas les deux ordres sur la géométrie** : il montre qu'ils sont
équivalents ici, parce que le déplacement du Multires est appliqué en espace
tangent et suit donc la base déformée dans les deux cas.

A est retenu pour une raison qui n'est pas une mesure et qui est écrite comme
telle : c'est l'ordre **conventionnel** d'un rig — la déformation d'os précède
la subdivision de rendu — et il reste le seul des deux qui garde un sens si le
Multires devait un jour porter un niveau supplémentaire non sculpté.

> Le cahier annonçait « la décision attendue est probablement Armature avant
> Multires ». Elle l'est. Mais **pas pour la raison qu'on pouvait attendre** :
> le banc ne montre aucune supériorité géométrique, il montre une équivalence.
> Publier « A est meilleur » serait faux.
