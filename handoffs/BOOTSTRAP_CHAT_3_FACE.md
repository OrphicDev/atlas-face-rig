# BOOTSTRAP — chat 3 : le visage

Tu deviens l'unique auteur de la géométrie faciale, des shape keys et du rig
facial maître. **Rien n'a encore été fait sur le visage.** Ce dépôt ne contient
que la mesure de l'asset source et les conventions à respecter — aucun travail
facial improvisé, aucune fausse promesse.

---

## 1. Dépôt et commit de départ

| | |
| --- | --- |
| dépôt | `OrphicDev/atlas-face-rig` |
| commit de départ | **ce commit de bootstrap** — le premier du dépôt |
| dépôt frère, les mains | `OrphicDev/atlas-hand-rig`, branche `wip/chat-1-honest-probe` |

---

## 2. L'asset exact à utiliser

**Human Base Meshes bundle v1.4.1 — Blender Studio, licence CC0.**

| | |
| --- | --- |
| obtention publique | https://studio.blender.org/tools/assets/human-base-meshes |
| fichier | `human_base_meshes_bundle.blend` |
| taille | 49 420 489 octets (47 Mio) |
| **SHA-256** | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| désignation | variable d'environnement `ATLAS_BASE_MESH` |
| Blender | **5.1.2** |

Le fichier n'est **pas versionné ici** : trop lourd, et le CC0 n'oblige pas à le
redistribuer. Télécharge-le, vérifie son SHA-256, et pointe `ATLAS_BASE_MESH`
dessus.

### Prends la collection « Head (Animation) », pas la tête du corps

Le paquet contient **19 collections**, dont deux têtes dédiées. Mesuré :

| source | sommets | quads | modificateur | UV |
| --- | ---: | ---: | --- | --- |
| **`Head (Animation) - Realistic`** | **3 242** (maillage seul) | **99,45 %** | MULTIRES | `UVMap` |
| `Head (Sculpting) - Realistic` | 3 307 | 99,38 % | MULTIRES | `UVMap` |
| tête extraite de `Body Male - Realistic` | 3 612 | — | MULTIRES | — |

**Recommandation : `Head (Animation) - Realistic`.** C'est la topologie prévue
pour l'animation, elle est la plus propre en quads, et elle sépare déjà l'iris
de la sclère — ce qui compte pour des yeux qui bougent.

Extraire la tête du corps serait un détour : le corps porte 10 582 sommets dont
seulement 3 612 au-dessus du cou, et la découpe créerait un bord à recoudre.

---

## 3. Topologie mesurée

### `Head (Animation) - Realistic` — 5 objets

| objet | sommets | faces |
| --- | ---: | ---: |
| `GEO-head_animation_realistic` | 3 242 | 3 234 |
| `.iris.L` / `.iris.R` | 400 chacun | 400 |
| `.sclera.L` / `.sclera.R` | 546 chacun | 544 |

- **99,45 % de quads** — 18 triangles et 10 n-gons sur 5 122 faces
- **une carte UV** (`UVMap`) sur chaque objet
- **modificateur MULTIRES** sur le maillage principal
- hauteur 0,3709 m, à l'échelle 1

### Densité autour des zones qui comptent

Sur le corps, **458 sommets dans un rayon de 30 mm autour d'un œil** — de quoi
travailler des paupières. La bouche n'a pas pu être mesurée par le même moyen :
mon repère sagittal n'a pas convergé, et je préfère le dire plutôt que rendre un
nombre douteux. **À mesurer par toi avant toute shape key.**

---

## 4. Problèmes connus du maillage — à traiter

1. **Aucune dent.** Mesuré : zéro objet contenant `teeth` ou `tooth`, dans les
   trois collections examinées.
2. **Aucune langue.**
3. **Aucun cil, aucun sourcil.**
4. **Aucun matériau** n'est assigné (liste vide) — sans objet pour cette V1, la
   matière étant hors périmètre.
5. **Aucune armature** dans le paquet, et **aucune shape key** : tout est à
   construire.
6. **10 n-gons** sur la tête d'animation : à localiser avant de sculpter, un
   n-gon sur un pli d'expression se voit.
7. Le multires est **présent** : décide tôt si tu travailles sur la cage ou sur
   le maillage subdivisé. Les mains ont souffert de ne pas trancher cette
   question (les arêtes de 0,02 mm ont faussé un invariant de déchirure).

---

## 5. Conventions à respecter, héritées des mains

- **suffixes `.L` / `.R`**, jamais autre chose ;
- préfixes de rôle : `CTRL_` (manipulé), `MCH_` (mécanisme caché, non
  déformant), `DEF_` (seul à déformer), `WGT_` (forme de contrôleur) ;
- **unités mètres**, échelle 1,1,1 et rotation nulle appliquées **avant** tout
  skinning ;
- pose neutre = repos ; `Fist = 0` doit redonner le repos **exactement**, et ce
  contrôle vaut aussi pour le visage : toute commande à 0 doit rendre le neutre
  à moins de 0,01 mm ;
- collections d'os `CONTROLS` / `MECHANISMS` / `DEFORM`.

### Lien avec le rig des mains

Aucun pour l'instant : les mains vivent dans leur propre dépôt et leur propre
`.blend`. Le jour où les deux se rejoindront, c'est le **corps** de
`Body Male - Realistic` qui sera le tronc commun — même paquet, même échelle,
même origine. Garde tes transformations compatibles avec lui.

---

## 6. Périmètre de la V1

**Inclus** : géométrie faciale, shape keys, rig facial maître, pour le
**personnage caucasien actuel uniquement** (`Head (Animation) - Realistic`,
masculin).

**Exclus, explicitement** : matière, texture, cheveux, barbe, pilosité. Ne perds
pas de temps dessus.

---

## 7. Risques et blocages

| risque | pourquoi |
| --- | --- |
| **dents et langue absentes** | une bouche qui s'ouvre sur le vide se voit immédiatement ; à modéliser ou à sourcer, et c'est un chantier en soi |
| **droits** | l'asset est CC0, donc publiable — mais **ne redistribue pas** le paquet de 47 Mo dans le dépôt, pointe vers la source |
| **multires non tranché** | voir le point 7 des problèmes connus |
| **la bouche non mesurée** | ma sonde n'a pas convergé ; ne pars pas d'un chiffre que je n'ai pas |

---

## 8. La leçon des mains, à ne pas réapprendre

Le rig des mains a été déclaré « validé » sur une sonde qui **ne voyait que
22 % des défauts** — elle testait 5 couples de surfaces sur 15, dans un seul
sens, sur 4 poses sur 13. Tout ce qui reposait dessus s'est effondré quand elle
a été corrigée.

Trois règles qui en sortent, et qui valent pour le visage :

1. **Vérifie ta sonde avant son verdict.** Fais-la tourner sur une
   configuration dont tu connais la réponse. Une sonde qui rend la même valeur
   pour toutes les entrées ne mesure pas son entrée.
2. **En mode fond, les drivers ne s'évaluent pas** sans changement d'image :
   `rig.update_tag()`, puis `bpy.context.scene.frame_set(...)`, puis
   `bpy.context.view_layer.update()`. Sans ça tu mesures un visage immobile —
   et un visage immobile revient toujours exactement au neutre, donc il passe.
3. **L'évaluateur d'expressions de driver n'accepte que des droites.** `min`,
   `max` et le produit de deux variables échouent **en silence**
   (`is_valid = false`, la valeur reste à 0).

Et une règle de sortie : `--python-exit-code 1`, sans quoi un script sort en
code 0 après un plantage. Déstampe aussi la sortie
(`sys.stdout.reconfigure(line_buffering=True)`), sinon Blender n'écrit rien
pendant des dizaines de minutes.

---

## 9. Ta première tâche recommandée

**Mesurer avant de modeler.** Charge `Head (Animation) - Realistic`, et produis
un rapport chiffré dans `reports/` :

- densité de boucles autour de **chaque paupière**, de **chaque lèvre**, du
  sillon nasogénien et des sourcils ;
- position exacte des **10 n-gons** et des 18 triangles ;
- symétrie gauche/droite du maillage, en millimètres ;
- décision, argumentée par la mesure, sur le **multires** : cage ou subdivisé.

Ce rapport décidera si la topologie tient pour des shape keys d'expression, ou
si une retopologie locale est nécessaire **avant** de commencer. Sur les mains,
cet audit-là a été fait (14 à 15 boucles par articulation) et c'est la seule
phase qui n'a jamais eu à être refaite.

Ne touche pas au visage avant d'avoir ces chiffres.

---

## 10. Reproduire l'inspection publiée ici

```bash
export ATLAS_BASE_MESH=/chemin/vers/human_base_meshes_bundle.blend
blender --background --factory-startup --python-exit-code 1 \
  --python tests/inspecter-asset-tetes.py -- ./tetes.json
```

Les résultats de référence sont dans `audit/inspection-asset-tetes.json` et
`audit/inspection-asset-corps.json`. Compare — un écart signifierait que tu n'as
pas le même asset.
