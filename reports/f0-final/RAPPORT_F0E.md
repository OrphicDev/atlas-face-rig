# F0-E — pile, résolution runtime et chemin glTF

## Ordre des modificateurs

Tranché dans [`DECISION_MODIFIER_ORDER.md`](DECISION_MODIFIER_ORDER.md) :
`ARMATURE PUIS MULTIRES`. Le banc a montré une **équivalence géométrique
stricte**, pas une supériorité — et c'est écrit comme tel.

## Résolution runtime — 5/5

`rig/build-runtime-mesh.py` matérialise le Multires au lieu de l'exporter.

| contrôle | résultat |
| --- | ---: |
| sommets denses | **12 950** — exactement la mesure F0 |
| morphs reconstruits à topologie identique | **3 / 3** |
| sommets sans poids | **0** |
| Multires sur le runtime | **0** |

## Export glTF — l'exporteur est interrogé avant d'être appelé

`experiments/gltf-spike/export_spike.py` lit d'abord les **108 propriétés RNA**
de l'opérateur sous Blender 5.1.2, puis n'utilise que celles qui existent, et
**refuse d'exporter** si une intention critique n'a pas d'équivalent. Aucune
option n'a été ignorée. `export_apply` reste **faux** : le mesh runtime porte
déjà ses morph targets.

`exports/atlas-face-spike.glb` — **3 630 880 octets**.

## Aller-retour — 9/9

| contrôle | résultat |
| --- | ---: |
| armature réimportée | **1** |
| morph targets | **3 / 3** |
| os de déformation | **2** |
| surface neutre, p95 | **0,000045 mm** |
| surface neutre, maximum | **0,000277 mm** |

La comparaison se fait par **plus proche point**, pas par indice : le glTF
triangule, dédouble les coutures UV et réordonne. Les 12 950 sommets deviennent
51 791 coins dédupliqués — c'est le comportement normal du format, et c'est
pourquoi comparer les indices n'aurait rien voulu dire.

## Le point ouvert est levé — et c'était mon test qui était faux

Le test comptait **2 meshes** au lieu d'un. En lisant le **chunk JSON du GLB**
lui-même, le fichier contient exactement :

```
meshes  : ['GEO-head_animation_realistic.001']
nodes   : TMP_jaw, TMP_head, GEO_face_runtime, TMP_F0_JAW_RIG
skins   : 1
attributs : JOINTS_0, NORMAL, POSITION, TEXCOORD_0, WEIGHTS_0
targets : 3
generator : Khronos glTF Blender I/O v5.1.20
```

Un seul mesh. L'`Icosphere` de 42 sommets est fabriquée **par l'importeur de
Blender** comme forme d'os ; elle n'a jamais été dans le fichier. Je comptais
des objets créés à l'import et je les attribuais à l'export.

Le test lit désormais le fichier, pas la scène qui en sort : **9 sondes sur 9**.

## Ce qui reste dû

Aucune **animation** n'est encore dans le GLB (`animations: []`) : le spike
d'action du §E.7 et son bake ne sont pas faits. Restent aussi la validation
Khronos (§E.9) et l'essai dans un runtime réel (§E.11).
