# F0-E — pile, résolution runtime et chemin glTF

## Ordre des modificateurs

Tranché dans [`DECISION_MODIFIER_ORDER.md`](DECISION_MODIFIER_ORDER.md) :
`ARMATURE PUIS MULTIRES`. Le banc a montré une **équivalence géométrique
stricte**, pas une supériorité — et c'est écrit comme tel.

## Résolution runtime — 7/7

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

## L'animation — §E.7

Une action de preuve `TMP_SPIKE` de neuf poses clefs (neutre, les deux
clignements, bouche fermée, mâchoire à 20° puis 32°, deux regards, retour au
neutre) est posée sur l'os `TMP_jaw` et sur les trois morphs, exportée, puis
**remesurée après réimport contre les valeurs écrites au moment de la pose** :

| mesure | pire écart sur les 9 poses |
| --- | --- |
| angle de mâchoire | **1.3e-05 °** |
| valeur de morph | **0.0** |

Passer de « le GLB contient une animation » à « l'animation vaut ce qu'elle
valait » a fait tomber une sonde, et elle avait raison de tomber : l'importeur
de Blender **range l'animation des morphs dans une piste NLA** au lieu de
l'activer. Je lisais des valeurs jamais évaluées — la même faute que
l'`Icosphere`, lire la scène au lieu du fichier. Le test active désormais
explicitement toute action laissée en NLA, et le dit dans son rapport.

**14 sondes sur 14** pour l'aller-retour.

## La conformité glTF 2.0 — §E.9

`tools/validate_glb.py` appelle le validateur **Khronos** s'il est présent et
publie sa sortie telle quelle. Il n'est pas installé sur cette machine, et je
n'ai pas décidé seul d'aller chercher un binaire : cette sonde est publiée
**SAUTÉE**, avec la raison. Un PASS venant d'un outil jamais exécuté serait un
mensonge. La commande qui la lèvera :

```
python3 tools/validate_glb.py --input exports/atlas-face-spike.glb \
  --report reports/f0-final/validation-glb.json --khronos /chemin/gltf-validator
```

À côté, un contrôle de conformité écrit dans le dépôt lit le fichier octet par
octet, sans rien installer : conteneur et alignement des chunks, bornes des
bufferViews, type/alignement/bornes de chaque accessor, **blocs sparse**,
min/max déclarés recalculés sur les données, indices dans les bornes, normales
unitaires, poids de peau normalisés, index d'os dans le skin, cohérence des
morph targets, hiérarchie sans double parent ni cycle, échantillonneurs
d'animation, quaternions unitaires, matrices de bind. **15 sur 16, une sautée.**

Là aussi j'ai dû corriger ma propre lecture avant d'accuser l'export : les
trois morph targets sont des accessors **sparse**, et mon décodeur ignorait le
bloc `sparse`. Il lisait des zéros et déclarait faux 18 min/max parfaitement
exacts.

### La contre-épreuve du contrôleur — 14 mutations

Un contrôleur qui dit PASS ne prouve rien tant qu'il n'a pas refusé des fautes
connues. `tests/validate-glb-negatif.py` fabrique 14 GLB mutants — longueur de
conteneur fausse, `asset.version` à 1.0, bufferView débordant, min déclaré
faux, indice hors bornes, normale de longueur 4, poids ne sommant plus à 1,
index d'os hors du skin, indices sparse non croissants, poids de morph
manquant, nœud à deux parents, canal d'animation vers un chemin inconnu,
quaternion non unitaire, joint sans matrice de bind. **Chacune tombe sur la
sonde qui la nomme, et sur elle seule : 15/15.**

Deux mutations « réussissaient » d'abord pour la mauvaise raison : mon harnais
écrivait 4 octets quel que soit le type du composant, ce qui raccourcissait le
BIN et décalait tout ce qui suit — une mutation en abîmait cinq. Et je
comptais une exception comme un refus, alors qu'une exception prouve seulement
que quelque chose a cassé.

## Le runtime — §E.11, et la faute que rien ne voyait

Trois évaluations de la même animation sont confrontées :

- **A** — Blender rejouant le blend runtime d'origine ;
- **B** — Blender rejouant le GLB réimporté ;
- **C** — `tools/runtime_eval.py`, une implémentation de la spécification glTF
  écrite ici, en Python pur, sans Blender, sans numpy, sans aucune
  bibliothèque : hiérarchie de nœuds, échantillonnage LINEAR / STEP /
  CUBICSPLINE, SLERP sur les rotations, morphs, matrices de peau.

| confrontation | ce qu'elle prouve | pire écart |
| --- | --- | ---: |
| B contre A | la déformation survit au transport | **0.000121 mm** au p95 |
| C contre B | un runtime qui ne connaît que la spéc retrouve la pose | **0.000268 mm** |

**0.000268 mm** : sur neuf poses et 51 791 sommets, un moteur qui n'a jamais vu
Blender reproduit la déformation à un demi-micron. Le fichier se suffit à
lui-même.

Deux échecs de départ venaient encore de moi, pas du fichier : l'horloge est
`f/fps` et non `(f−1)/fps` — elle est désormais **lue sur le fichier** et
vérifiée aux deux bouts —, et glTF est en **Y-haut** quand Blender est en
Z-haut. Je comparais deux repères et je lisais 1 936 mm d'écart.

### La faute que huit sondes ne voyaient pas

La sonde de garde `runtime.amplitude`, ajoutée seulement pour éviter de
comparer deux poses immobiles, a rendu **251 mm** de déplacement pour une
mâchoire à 32°. Une mâchoire fait 60 à 70 mm. En regardant, le maillage
exporté était à **1,46 m de son propre rig** : `rig/build-runtime-mesh.py`
faisait `run.parent = rig` **sans poser `matrix_parent_inverse`**, et la
matrice locale — qui valait déjà celle de la tête — se composait une seconde
fois avec celle de l'armature, au même endroit. Exactement le double.

Aucune des sondes de F0-E ne l'avait vu, et la raison compte : **elles
comparaient toutes le même montage fautif à lui-même**. L'aller-retour, la
conformité, le transport — tout était cohérent, et tout était décalé.

Le correctif est d'une ligne. Deux sondes le gardent maintenant à la
construction : `runtime.parentage` (le parentage ne déplace pas le maillage)
et `runtime.au_meme_endroit` (le runtime est là où est la tête d'auteur),
toutes deux à **0,0 m**.

### Et la sonde évidente ne marche pas

J'ai d'abord écrit la sonde qui semblait s'imposer : *la mâchoire tourne-t-elle
autour du pivot du contrat ?* — une rotation conserve la distance à son centre.
Elle passe à **0.000112 mm**. Mais `tests/runtime-pivot-negatif.py` remet la faute
sous ses yeux, et elle **ne la voit pas** : la dérive reste à 8.5e-05 mm alors que
le maillage est à 1,46 m.

C'est géométriquement forcé. Le modificateur d'armature ramène les os dans
l'espace **local du maillage** ; le centre de rotation en monde reste donc le
pivot, quelle que soit la distance. Seul le bras de levier change.

Ce qui voit la faute, c'est autre chose : la **course** (251,9 mm, hors des
bornes anatomiques) et un invariant tout bête — le milieu des conduits
auditifs est **à l'intérieur** d'une tête. `runtime.pivot_dans_la_boite`.
La contre-épreuve publie les trois verdicts : 5/5.

## Ce qui reste dû

Le validateur **Khronos** lui-même (§E.9) n'a pas tourné : il n'est pas sur la
machine, et je n'ai pas décidé seul d'aller chercher un binaire.
