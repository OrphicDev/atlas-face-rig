# Rapport F0 — audit topologique, décision multires, décision de topologie

Asset : `human_base_meshes_bundle.blend` v1.4.1, Blender Studio, **CC0**,
49 420 489 octets, SHA-256 `3c121505…c75c137` (vérifié avant toute lecture).
Collection : `Head (Animation) - Realistic`. Blender **5.1.2**.

Données brutes : [`audit-topologie.json`](audit-topologie.json) et
[`multires-ab.json`](multires-ab.json). Sondes :
[`tests/f0-audit-topologie.py`](../../tests/f0-audit-topologie.py),
[`tests/f0-multires.py`](../../tests/f0-multires.py).

---

## 0. Les sondes avant leurs verdicts

**15 sondes sur 15 vérifiées** sur des configurations à réponse connue, avant
toute mesure du visage. Le script sort en code 2 et ne publie **aucun chiffre**
si une seule échoue.

Deux sondes étaient fausses et l'auto-test les a prises :

| sonde | ce qu'elle rendait | la cause |
| --- | --- | --- |
| anneaux de bord | 32 anneaux d'une arête au lieu d'1 de 32 | les arêtes d'un tel bord sont des **barreaux parallèles** : elles ne partagent pas de sommet mais la face entre elles. Le groupement se fait par face. |
| symétrie | 0,0013 mm pour un décalage imposé de 1 mm | mon test déplaçait un sommet **posé sur le plan miroir** — il est son propre miroir, la sonde ne pouvait rien voir. |

Une troisième a été prise dans le banc multires : la contre-épreuve « décale de
1 mm » ne bougeait pas (7,251 → 7,245 mm). En mode fond, modifier un maillage
sans marquer le graphe de dépendances ne réévalue rien : la sonde comparait deux
fois la même chose. Corrigée, elle lit **1,000 mm** pour 1 mm imposé.

---

## 1. Intégrité — tout est propre

| contrôle | mesuré |
| --- | ---: |
| bords ouverts | **0** |
| arêtes non-manifold | **0** |
| arêtes sans face | **0** |
| sommets lâches | **0** |
| paires de doublons à 10 µm | **0** |
| faces de normale incohérente | **0** |
| faces dégénérées | **0** |
| volume signé | **+0,00827 m³** (normales vers l'extérieur) |

Le maillage principal est une surface **close et manifold**.

## 2. Comptes

| | sommets | faces |
| --- | ---: | ---: |
| `GEO-head_animation_realistic` | 3 242 | 3 234 |
| iris `.L` / `.R` | 400 / 400 | 400 / 400 |
| sclère `.L` / `.R` | 546 / 546 | 544 / 544 |
| **total collection** | **5 134** | **5 122** |

Sur le **maillage principal seul** : 3 206 quads, **18 triangles**, **10 n-gons**
→ **99,134 % de quads**. Le chiffre de 99,45 % du bootstrap portait sur la
collection entière, yeux compris ; les deux sont justes, ils ne comptent pas la
même chose.

Encombrement monde : 273,66 × 246,59 × **370,90 mm** — **cou et épaules inclus**.
La tête seule fait environ 230 mm du menton au sommet.

Pointe du nez : `[1,46263 ; −0,16903 ; 0,72933]`.
Globes oculaires : rayon **11,702 mm**, centres à **±32,29 mm** de l'axe, z 0,76669.

## 3. Symétrie — la topologie et la géométrie ne disent pas la même chose

Une carte miroir **combinatoire** est construite par propagation de voisin en
voisin depuis un couple sûr, puis vérifiée. Résultat :

| contrôle | résultat |
| --- | --- |
| appariement bijectif | **oui** |
| involutif (`m(m(i)) = i`) | **oui** |
| arêtes sans image miroir | **0** / 6 474 |
| faces sans image miroir | **0** / 3 234 |
| sommets sur l'axe | 112 |

**La topologie est exactement symétrique.** Ce n'est pas supposé : c'est démontré.
Conséquence directe — les shape keys `.L` / `.R` peuvent être miroitées par
**indice de sommet**, sans passer par la position.

La géométrie, elle, ne l'est pas :

| | mm (repère monde) |
| --- | ---: |
| médiane | **0,083** |
| moyenne | 0,140 |
| p99 | 0,872 |
| maximum | **1,689** (oreilles) |
| sommets au-delà de 1 mm | 22 / 3 242 |

Par zone : oreilles 1,689 · épaules/bas du cou 1,512 · œil 1,014 · nez 0,510 ·
bouche 0,503. **Le visage lui-même est symétrique à 0,1 mm près en médiane** ;
l'asymétrie vit dans les oreilles et le bas du buste. Une asymétrie légère est
un atout pour le photoréalisme : elle est conservée, pas gommée.

## 4. Ouvertures — sept, et exactement sept

Un sommet est dit *extérieur* si les rayons partant de sa normale s'échappent ;
*intérieur* s'il est enfermé par le maillage. Le bord entre les deux est une
ouverture. Au seuil **0,15**, la sonde rend **exactement les sept ouvertures
qu'a une tête humaine** — et pas une de plus :

| ouverture | écart à l'axe | largeur | hauteur | arêtes de bord | cavité derrière |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fente_labiale` | −0,1 mm | **47,73 mm** | 5,88 mm | 44 | **oui, réelle** |
| `fente_palpebrale.L` | +34,3 mm | 23,34 mm | 18,38 mm | 24 | orbite |
| `fente_palpebrale.R` | −34,6 mm | 23,27 mm | 16,34 mm | 24 | orbite |
| `narine.L` | +8,3 mm | 8,45 mm | 5,39 mm | 9 | oui |
| `narine.R` | −8,3 mm | 8,38 mm | 5,34 mm | 8 | oui |
| `conduit_auditif.L` | +69,6 mm | 9,89 mm | 14,31 mm | 17 | oui |
| `conduit_auditif.R` | −69,0 mm | 9,86 mm | 13,68 mm | 11 | oui |

Le choix du seuil est **justifié par cette conformité anatomique**, pas choisi
au jugé ; la table `stabilite_du_seuil` du JSON montre 4 anneaux à 0,05, 5 à
0,10, **7 à 0,15**, 8 à 0,20, 10 à 0,30.

> **Correction d'une erreur de ma propre sonde.** À un stade antérieur elle
> étiquetait « narines » les deux ouvertures à ±69 mm de l'axe : ce sont les
> **conduits auditifs**. Les vraies narines sont à ±8,3 mm et sont peu
> profondes — elles n'apparaissent qu'à partir du seuil 0,15.

**La coupe sagittale confirme une véritable cavité orale** : une poche fermée
derrière les lèvres, et non un simple pli. Une mâchoire qui s'ouvre ne
découvrira donc pas le vide, mais une muqueuse sans dents ni langue.

## 5. Boucles concentriques — la densité là où ça compte

Nombre de sommets par boucle successive autour de chaque ouverture, et distance
moyenne à l'ouverture :

| zone | b1 | b2 | b3 | b4 | b5 | b6 |
| --- | --- | --- | --- | --- | --- | --- |
| **lèvres** (38 au bord) | 38 · 2,8 mm | 38 · 5,6 | 38 · 8,7 | 38 · 12,2 | 38 · 16,5 | 40 · 21,3 |
| **paupière L** (20) | 20 · 1,6 | 22 · 3,0 | 25 · 4,2 | 26 · 5,5 | 26 · 7,7 | 25 · 10,9 |
| **paupière R** (20) | 21 · 1,6 | 23 · 3,0 | 25 · 4,1 | 26 · 5,5 | 25 · 7,9 | 25 · 11,2 |
| **narine L** (7) | 10 · 2,8 | 10 · 4,9 | 13 · 7,8 | 17 · 11,2 | 22 · 14,7 | 27 · 18,0 |

Lecture :

- **cinq boucles régulières et parfaitement constantes (38 sommets) autour des
  lèvres**, jusqu'à 16,5 mm — c'est une topologie faite pour l'animation labiale ;
- **quatre boucles de paupière** entre la marge et 5,5 mm, puis le flux s'ouvre
  vers l'orbite. C'est **juste suffisant** pour un clignement, et c'est la zone
  la plus tendue du maillage ;
- les **narines sont grossières** : 7 à 8 sommets sur le pourtour.

## 6. Densités mesurées

| région | sommets/cm² | arête moyenne |
| --- | ---: | ---: |
| commissure `.L` / `.R` | 22,27 / 22,43 | 2,68 / 2,67 mm |
| œil, 10 mm | 23,18 / 24,34 | 3,28 / 3,27 mm |
| lèvres, 10 mm | 12,48 | 4,38 mm |
| lèvres, 20 mm | 6,34 | 4,61 mm |
| sillon nasogénien | 6,19 / 6,06 | 4,57 / 4,62 mm |
| sourcil et front | 3,31 / 3,36 | 6,74 / 6,70 mm |
| cou sous le menton | 1,27 | 12,09 mm |

Les commissures et les yeux sont les zones les plus denses — c'est le bon ordre.
Le front est quatre fois moins dense que l'œil, ce qui est cohérent avec des
sourcils portés par des shape keys larges plutôt que par du détail local.

**La densité autour de la bouche, que le bootstrap n'avait pas pu mesurer, l'est
maintenant** : 12,48 sommets/cm² à 10 mm, 6,34 à 20 mm, arête de 4,4 mm.

## 7. Continuité et pôles

Dans le tiers avant du visage (1 635 sommets) : **88 pôles**, dont 36 de
valence 3 et 52 de valence 5. Aucun pôle de valence supérieure à 5. Le flux
bouche–joues–nez est continu et entièrement en quads hors des triangles listés
plus bas.

## 8. Où sont les n-gons et les triangles

**10 n-gons** :

- **2 pentagones** de 16 mm², un par **conduit auditif** ;
- **8 n-gons** de 1 867 à 10 044 mm², tous à la **base du cou** — ce sont les
  faces de fermeture du buste.

**Aucun n-gon dans une zone d'expression.**

**18 triangles** :

- **4** aux conduits auditifs ;
- **14** dans un rayon de 20 mm de l'axe sagittal, 6 à 11 mm **au-dessus et
  au-dessous** de la ligne des lèvres : **philtrum** et **lèvre inférieure /
  menton**. Aucun ne se trouve sur la couture des lèvres elle-même.

C'est **la seule réserve topologique mesurée du visage**, et elle est nommée.

---

## 9. Décision F0.2 — multires

### Ce que le multires contient réellement

| mesure | résultat |
| --- | ---: |
| niveaux | 1 (`levels` = `sculpt_levels` = `render_levels` = `total_levels` = 1) |
| niveau 0 comparé à la cage | **0,000000000 mm** — le niveau 0 **est** la cage |
| niveau 1 évalué | 12 950 sommets / 12 948 faces |
| contre-épreuve : 1 mm imposé, 1 mm lu | **1,000 mm** ✔ |

Le niveau 1 ne coïncide **ni** avec une subdivision en raffinement simple
(max 7,251 mm · médiane 0,290) **ni** avec une subdivision sur surface limite
(max 8,488 · médiane 0,379). L'écart n'est donc pas un artefact de schéma :
**le multires porte un véritable déplacement sculpté**.

Où ? La question décide de tout :

| zone | max | médiane |
| --- | ---: | ---: |
| cou et épaules | **7,251 mm** | 1,149 mm |
| crâne | 2,079 | 0,341 |
| oreilles | 2,295 | 0,337 |
| **visage avant** | **2,098 mm** | **0,240 mm** |

Les 7 mm sont au bas du cou, pas sur le visage. Sur le visage, jeter le multires
coûterait 0,24 mm en médiane et 2,1 mm au pire — **2,1 mm sont visibles sur une
silhouette photoréaliste**.

### Banc A/B, trois prototypes jetables

Même geste (bourrelet cosinus de 4 mm) posé de deux façons :

| prototype | voie | points de contrôle déplacés | poids d'une shape key | amplitude obtenue | retour au neutre |
| --- | --- | ---: | ---: | ---: | ---: |
| clignement | cage puis subdivision | **57** / 3 242 | **38 904 o** | 1,515 mm | **0,000000 mm** |
| | sur maillage subdivisé | 246 / 12 950 | 155 400 o | 1,730 mm | 0,000000 mm |
| fermeture labiale | cage puis subdivision | **36** | **38 904 o** | 2,987 mm | **0,000000 mm** |
| | sur maillage subdivisé | 135 | 155 400 o | 3,617 mm | 0,000000 mm |
| ouverture de mâchoire | cage puis subdivision | **667** | **38 904 o** | 3,938 mm | **0,000000 mm** |
| | sur maillage subdivisé | 2 651 | 155 400 o | 3,981 mm | 0,000000 mm |

Résolution évaluée **identique** dans les deux voies (12 950 / 12 948). **UV
conservée** dans les deux. Temps indiscernables à cette échelle (0,21 s).

Ce que le banc dit vraiment :

1. la cage fait le même geste avec **4 fois moins de points de contrôle** et une
   shape key **4 fois plus légère** ;
2. la cage **atténue** davantage un même déplacement (1,52 contre 1,73 mm au
   clignement, 2,99 contre 3,62 à la fermeture labiale) : elle donne des plis
   plus doux, le subdivisé donne un contrôle local plus fin ;
3. les deux reviennent **exactement** au neutre.

### Décision

**Shape keys sur la cage de 3 242 sommets ; le multires est conservé, en fin de
pile, et n'est jamais appliqué.**

- le niveau 0 étant exactement la cage, travailler sur la cage ne perd rien ;
- le déplacement sculpté du niveau 1 est réel et doit être gardé ;
- 4× moins de points de contrôle par action, et un miroir `.L`/`.R` par indice
  rendu possible par la symétrie topologique démontrée ;
- l'atténuation par subdivision se compense par l'amplitude de l'action, pas par
  un changement d'architecture.

`Apply` sur le multires reste **interdit**, et le nombre de sommets de la source
n'a pas été touché.

---

## 10. Décision F0.3 — topologie

**Option retenue : 1 — la cage actuelle suffit.** Motifs mesurés :

1. topologie **exactement symétrique** (démontré, § 3) ;
2. intégrité parfaite : 0 non-manifold, 0 doublon, 0 bord, 0 normale inversée ;
3. **aucun n-gon dans une zone d'expression** ;
4. **5 boucles régulières de 38 sommets** autour des lèvres ;
5. **7 ouvertures anatomiques conformes**, dont une **vraie cavité orale** ;
6. UV `UVMap` présente sur les 5 objets, à préserver telle quelle.

**Réserves nommées, à ne pas oublier :**

| réserve | mesure | quand la trancher |
| --- | --- | --- |
| 14 triangles au philtrum et à la lèvre inférieure | 6 à 11 mm de la couture labiale | **avant F2**, si le pli s'y casse |
| 4 boucles de paupière seulement, dans 5,5 mm | § 5 | **avant F2**, si le clignement ne ferme pas |
| narines à 7–8 sommets de pourtour | § 4 | F4, si le pincement narinaire est raide |

L'ordre de production le permet : **F1 (mâchoire et regard) est du travail d'os,
sans aucune shape key.** Une retopologie locale reste donc possible entre F1 et
F2 sans jamais violer la règle « toute modification du nombre ou de l'ordre des
sommets intervient avant les shape keys ».

### Base verrouillée

`source/FACE_BASE_LOCKED.blend` — 5 objets, **5 134 sommets, 5 122 faces**,
980 099 octets.

Transformations figées : **échelle 1,1,1 · rotation nulle** sur les 5 objets
(l'asset les livrait à 0,9 et 0,639556). L'application a été mesurée avant d'être
retenue : elle déplace la surface de **0,001213 mm**, sous la tolérance de
0,01 mm que le projet s'est lui-même donnée dans `docs/SCOPE_V1.md`. La position
monde est **inchangée**, donc la compatibilité avec `Body Male - Realistic` est
préservée.

| empreinte | valeur |
| --- | --- |
| topologie | `d29e2af3ef67aec5bad705c5e5a4b72428f906f01af94c33880c85a47722e5ae` |
| pose neutre | `9246d8acb2d68a38a6f355db90df967e8f6e71907343ce1cf028549bed20c324` |
| SHA-256 du .blend | `669ccdb7858adea2e3091218bdfeed4fe1b4d955d866497ad20e8559c95e55bd` |

`tests/verrou-topologie.py` échoue en code 1 si l'une des deux empreintes bouge.

---

## 11. Rendus neutres de référence

10 vues dans `renders/f0/` : face, deux profils, deux trois-quarts, plongée,
contre-plongée, gros plans œil / bouche / nez. Clay neutre, key rasante, fill
faible, contre-jour discret, transformation de vue `Standard`, exposition
**calibrée puis verrouillée** (le 99,5ᵉ centile de la vue de face amené juste
sous la saturation, facteur 7,2204, identique pour toutes les vues).

Histogrammes publiés dans `renders/f0/histogrammes.json` :
**0,000 % de noirs bouchés et au plus 0,073 % de blancs brûlés** sur les dix vues.

Un premier jeu de rendus a été jeté : il brûlait jusqu'à **95,5 %** de l'image.
C'est l'histogramme qui l'a dit, pas l'œil.

L'asset est livré en **ombrage plat** ; les rendus de référence sont lissés, et
c'est écrit dans `histogrammes.json` (`faces_lissees_pour_le_rendu`). Le fichier
verrouillé, lui, garde l'ombrage d'origine.
