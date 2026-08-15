# Dents, langue et intérieur de bouche — stratégie V1

Une bouche photoréaliste ne peut pas s'ouvrir sur du vide. Ce document dit ce
qui existe, ce qui manque, et d'où viendra le reste.

## Ce qui est mesuré

La coupe sagittale du maillage montre **une véritable cavité orale** : une poche
fermée derrière les lèvres, 44 arêtes de bord à la fente labiale, une muqueuse
continue. Ce n'est pas un simple pli. Donc :

- l'ouverture de mâchoire ne découvrira **pas** le vide ;
- mais elle découvrira une muqueuse **sans dents, sans langue, sans gencives**.

Confirmé par la mesure sur les trois collections examinées : **zéro objet**
contenant `teeth`, `tooth` ou `tongue`.

## 1. Recherche dans les assets déjà présents sur la machine — faite

Balayage de `~/Desktop`, `~/Documents`, `~/Downloads`, `~/Projet de
développement` et de la configuration Blender. **Aucun asset dentaire
indépendant.**

En revanche, l'inspection du paquet source lui-même a trouvé mieux.

## 2. Les dents viennent de l'asset source — même paquet, même licence

`human_base_meshes_bundle.blend` contient un objet **`Jaw - Realistic`** qui
n'est dans aucune des collections listées au bootstrap, et qui n'avait donc pas
été vu.

| | mesuré |
| --- | ---: |
| sommets | 5 294 |
| faces | 5 058 |
| **coques séparées** | **29** |
| dont mandibule | 1 coque de 2 354 sommets |
| dont **dents** | **28 coques de 105 sommets chacune** |
| bords ouverts | 0 |
| UV | `UVMap` |
| échelle objet | 1,0 |
| modificateurs | aucun |

**28 dents** — une dentition adulte complète moins les dents de sagesse
(32 − 4). Elles se répartissent en deux arcades (deux bandes en z distinctes) et
sont symétriques gauche/droite. Dimensions par dent : de 6,1 × 7,0 × 12,8 mm
(incisive) à 12,9 × 13,5 × 14,3 mm (molaire) — des cotes anatomiques réelles.

### Provenance et droits

| | |
| --- | --- |
| source | `human_base_meshes_bundle.blend`, objet `Jaw - Realistic` |
| paquet | Human Base Meshes bundle **v1.4.1**, Blender Studio |
| licence | **CC0** — publiable, modifiable, sans obligation d'attribution |
| SHA-256 du paquet | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| taille du paquet | 49 420 489 octets |
| Blender | 5.1.2 |

**Aucune licence incertaine, aucun asset tiers, aucune redistribution du paquet
de 47 Mo.** C'est le même auteur, le même paquet et le même système d'unités que
la tête : c'est le meilleur choix possible et il était déjà là.

## 3. Ce qui reste à faire, et dans quel ordre

1. **Extraire** `Jaw - Realistic` et le versionner comme asset dérivé, avec son
   manifeste source / version / SHA-256.
2. **Recaler** : dans la scène du paquet, la mâchoire est à x 1,4251–1,5000,
   z 0,9283–0,9865, à l'échelle 1 — soit **ailleurs que la tête** (z 0,509–0,880).
   Elle est aussi à une autre échelle relative que la tête (que le paquet livrait
   à 0,9). Le recalage se fait **par la mesure** : alignement de l'arcade
   supérieure sur le palais de la cavité orale, occlusion vérifiée, et non à vue.
3. **Vérifier** l'échelle, la dentition, l'occlusion et la position au neutre.
4. **Séparer** les deux arcades : l'arcade supérieure suit le crâne, l'arcade
   inférieure suit `CTRL_jaw`. C'est ce qui rend l'ouverture de mâchoire
   crédible.
5. **Gencives et volume intérieur minimal** — à construire si la mesure montre
   un jour entre les dents et la muqueuse.
6. **Langue** : **absente du paquet, à construire**. Procédurale et versionnée,
   avec un rig réel à trois articulations — base, corps, pointe — assorties de
   limites et d'un contrôle de non-pénétration.

## 4. Règle de séquence

Ni visème, ni validation d'une grande ouverture de bouche **tant que la cavité
orale n'est pas exploitable** : dents recalées, arcades séparées, langue en
place. C'est un préalable à F3 et un bloqueur explicite de F6.
