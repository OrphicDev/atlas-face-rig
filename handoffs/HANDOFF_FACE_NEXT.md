# HANDOFF — la suite du visage, à partir de F1

**F0 n'est PAS terminée.** Ce document affirmait le contraire pendant que
`STATUS.md` affirmait « F0 INCOMPLET » : la contradiction est levée ici.
L'état réellement démontré est dans
[`reports/f0-final/RAPPORT_F0_FINAL.md`](../reports/f0-final/RAPPORT_F0_FINAL.md).
**Rien n'est riggé.** Ne recommence pas ce qui est déjà mesuré, mais ne
commence pas F1 non plus : le gate F0 n'est pas passé.

## 1. Où reprendre

| | |
| --- | --- |
| dépôt | `OrphicDev/atlas-face-rig` |
| branche | `face/chat-3-caucasian-v1` |
| base | **`source/FACE_BASE_LOCKED.blend`** — pars de là, pas du paquet |
| asset source | `ATLAS_BASE_MESH`, toujours nécessaire pour les dents |
| Blender | 5.1.2 |

À lire, dans cet ordre : `reports/f0/RAPPORT_F0.md`, `STATUS.md`,
`docs/DENTS_ET_LANGUE.md`, `docs/FACS_MATRIX.md`.

## 2. La première chose à faire, avant toute autre

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python tests/verrou-topologie.py -- source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json
```

Il doit sortir en **0**. S'il sort en 1, la base a bougé et rien de ce qui suit
n'a de sens.

## 3. Ce que la mesure a déjà décidé pour toi

- **Les shape keys se posent sur la cage de 3 242 sommets.** Le multires reste
  en fin de pile et n'est **jamais** appliqué : son niveau 0 est exactement la
  cage (0,000000000 mm), son niveau 1 porte un sculpt réel (2,10 mm au pire sur
  le visage).
- **Le miroir `.L`/`.R` se fait par indice de sommet.** La topologie est
  exactement symétrique — c'est démontré, pas supposé. La géométrie ne l'est pas
  (0,083 mm de médiane) et cette asymétrie est **conservée volontairement**.
  `carte_miroir()` dans `tests/f0-audit-topologie.py` construit la table.
- **La subdivision atténue** : 4 mm posés sur la cage rendent 1,52 mm au
  clignement. Règle l'amplitude après subdivision.
- **Repère** : X latéral (+X = gauche du personnage), −Y vers l'avant, Z vers le
  haut. Plan sagittal en x local 0.
- **Repères anatomiques mesurés**, en coordonnées monde :
  globes oculaires rayon 11,702 mm, centres à ±32,29 mm de l'axe, z 0,766 69 ·
  fente labiale au centre `[1,46258 ; −0,14593 ; 0,69424]`, 47,73 mm de large ·
  pointe du nez `[1,46263 ; −0,16903 ; 0,72933]` · narines à ±8,3 mm, z 0,7271 ·
  conduits auditifs à ±69 mm, z 0,740.

## 4. F1 — mâchoire et regard : os seulement

**F1 ne pose aucune shape key.** C'est délibéré : cela laisse ouverte la seule
retopologie locale encore envisagée, sans jamais violer la règle « toute
modification du nombre ou de l'ordre des sommets intervient avant les shape
keys ».

À faire :

1. pivot mandibulaire **anatomique** — près du conduit auditif, pas au menton ;
   les conduits sont mesurés à ±69 mm de l'axe, z 0,740 ;
2. rotation et translation coordonnées, menton et joues conservés ;
3. yeux indépendants et conjoints, convergence sur cible proche ; les globes sont
   des objets séparés, de centre et rayon connus ;
4. limites naturelles, et `CTRL_ = 0` rend le neutre à moins de 0,01 mm.

Conventions : `CTRL_` / `MCH_` / `DEF_` / `WGT_`, suffixes `.L` / `.R`,
collections d'os `CONTROLS` / `MECHANISMS` / `DEFORM`, mètres, échelle 1.

## 5. La décision qui t'attend entre F1 et F2

**14 triangles au philtrum et à la lèvre inférieure**, 6 à 11 mm de la couture
labiale, et **4 boucles de paupière seulement** dans 5,5 mm. Si F2 montre que le
clignement ne ferme pas ou que le pli du philtrum casse, la retopologie locale se
fait **là**, avant la première shape key. Passé ce point, elle coûte tout le
travail déjà posé.

## 6. Dents et langue

`Jaw - Realistic` est dans le paquet source : **28 dents + mandibule, CC0, même
auteur, même paquet**. Voir `docs/DENTS_ET_LANGUE.md` pour les cotes et le plan
de recalage. La **langue n'existe pas** et doit être construite, procédurale et
versionnée, avec trois articulations réelles.

Ni visème ni grande ouverture de bouche validée tant que la cavité orale n'est
pas exploitable.

## 7. Les trois pièges qui ont déjà coûté

1. **Une sonde se vérifie avant son verdict.** Trois des miennes étaient fausses
   et leurs propres auto-tests les ont prises. Une sonde qui rend la même valeur
   pour toutes ses entrées ne mesure pas son entrée.
2. **En mode fond, rien ne se réévalue tout seul.** `ob.data.update()`,
   `ob.update_tag()`, `bpy.context.view_layer.update()` — sans quoi tu relis
   l'évaluation d'avant ta modification, et tout passe.
3. **Un seuil ne se choisit pas au jugé.** Celui des ouvertures (0,15) est retenu
   parce qu'il rend exactement les sept ouvertures qu'a une tête humaine ; celui
   de l'application d'échelle (0,01 mm) vient de `docs/SCOPE_V1.md`. Un seuil
   choisi pour faire passer une mesure laisse la faute en place.
