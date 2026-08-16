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

## Aller-retour — 5/6

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

## Le point ouvert, et il l'est

Le test compte **2 meshes** dans le GLB au lieu d'un. Le blend runtime ne
contient pourtant que `GEO_face_runtime` et `TMP_F0_JAW_RIG`, et l'export est
fait sur sélection explicite. **Je n'ai pas identifié l'origine du second mesh**,
et je ne la devine pas ici. Tant qu'elle n'est pas nommée, ce chemin d'export
n'est pas validé — même si la géométrie, les morphs et les os traversent
l'aller-retour intacts.

Restent également dus : la validation Khronos (§E.9) et l'essai dans un runtime
réel (§E.11).
