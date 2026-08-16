# CHANGELOG

## F0 — audit topologique, décisions, base verrouillée

Aucun rig, aucune shape key : F0 ne devait pas en produire. Détail chiffré dans
[`reports/f0/RAPPORT_F0.md`](reports/f0/RAPPORT_F0.md).

### Mesuré

- **intégrité parfaite** : 0 bord ouvert, 0 non-manifold, 0 doublon à 10 µm,
  0 normale incohérente, 0 face dégénérée, volume signé positif ;
- **topologie exactement symétrique** — carte miroir combinatoire bijective et
  involutive, 0 arête et 0 face sans image, 112 sommets sur l'axe ;
- **géométrie légèrement asymétrique** : 0,083 mm en médiane, 1,689 mm au
  maximum (oreilles). Conservée volontairement ;
- **sept ouvertures anatomiques** et pas une de plus : bouche (47,73 mm),
  deux fentes palpébrales, deux narines (±8,3 mm), deux conduits auditifs ;
- **une vraie cavité orale** derrière les lèvres — vue en coupe sagittale ;
- **cinq boucles régulières de 38 sommets** autour des lèvres jusqu'à 16,5 mm ;
  **quatre boucles de paupière** dans 5,5 mm ;
- **densité autour de la bouche**, que le bootstrap n'avait pas pu mesurer :
  12,48 sommets/cm² à 10 mm, 6,34 à 20 mm, arête moyenne 4,4 mm ;
- **n-gons** : 2 aux conduits auditifs, 8 à la base du cou — **aucun en zone
  d'expression** ; **18 triangles** dont 14 au philtrum et à la lèvre inférieure ;
- 99,134 % de quads sur le maillage principal seul (99,45 % portait sur la
  collection entière, yeux compris : les deux sont justes).

### Décidé, sur mesure

- **cage de 3 242 sommets conservée** (option 1, pas de retopologie) ;
- **shape keys sur la cage, multires gardé en fin de pile et jamais appliqué** :
  son niveau 0 est exactement la cage (0,000000000 mm), son niveau 1 porte un
  sculpt réel — 2,10 mm au pire sur le visage, 7,25 mm au bas du cou ;
- banc A/B : la cage fait le même geste avec **4× moins de points de contrôle**
  et une shape key **4× plus légère** ; les deux voies reviennent exactement au
  neutre et conservent l'UV ;
- **échelle appliquée** (1,1,1, rotation nulle) : l'opération déplace la surface
  de 0,001213 mm, sous les 0,01 mm du critère de `docs/SCOPE_V1.md` ;
- **dents prises dans l'asset source** : `Jaw - Realistic`, 28 dents +
  mandibule, CC0, même paquet. La langue reste à construire.

### Vérifié avant d'être publié

**19 sondes sur 19** passées sur des configurations à réponse connue. **Trois
sondes fausses ont été prises par leurs propres auto-tests** et corrigées avant
publication : groupement des anneaux de bord par face et non par sommet ; test de
symétrie qui déplaçait un sommet posé sur le plan miroir ; contre-épreuve du banc
multires qui ne marquait pas le graphe de dépendances.

### Livré

`source/FACE_BASE_LOCKED.blend` (5 objets, 5 134 sommets, 5 122 faces), son
verrou de topologie et de pose neutre, dix rendus neutres à exposition calibrée
puis verrouillée (0 % de noirs bouchés, ≤ 0,084 % de blancs brûlés).

### Corrigé

Le manifeste du bootstrap se listait lui-même, ce qu'aucun fichier ne peut
satisfaire. Il ne se liste plus.

## Bootstrap — aucun travail facial

Premier commit. Il contient la mesure de l'asset source et les conventions,
**rien d'autre**.

### Mesuré

- asset : Human Base Meshes bundle v1.4.1 (Blender Studio, CC0), SHA-256
  `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`,
  49 420 489 octets, Blender 5.1.2 ;
- **19 collections** dans le paquet, dont deux têtes dédiées ;
- `Head (Animation) - Realistic` retenue : 3 242 sommets, **99,45 % de quads**,
  18 triangles, 10 n-gons, UV présente, MULTIRES, iris et sclère séparés ;
- corps `Body Male - Realistic` : 10 582 sommets, 3 612 au-dessus du cou,
  458 sommets dans 30 mm autour d'un œil ;
- **absents** : dents, langue, cils, sourcils, matériaux, armature, shape keys.

### Non mesuré, et dit comme tel

La densité autour de la bouche : la sonde n'a pas convergé. **Mesurée depuis, en F0.**

### Aucune modification de l'asset

L'inspection est en lecture seule. Le visage n'a pas été touché.


> **État F0 (2026-08-16, commit `f6f1c86`).** F0 est **incomplète** : 200 sondes, 193 réussies, 3 échec(s), 4 sautée(s). Vérité unique : [`reports/f0-final/RAPPORT_F0_FINAL.md`](reports/f0-final/RAPPORT_F0_FINAL.md). F1 n'a pas commencé.
