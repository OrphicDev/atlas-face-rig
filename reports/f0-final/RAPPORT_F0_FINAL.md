# F0 — rapport final

> **F0 — toutes les conditions du gate sont remplies, 2 SOUS RÉSERVE.** Le tutoriel demande de ne pas publier de clôture tant qu'un point n'est pas franc : ces réserves sont nommées sous le tableau, et F0 n'est pas déclarée terminée ici.

## Provenance et environnement

| | |
| --- | --- |
| commit | `f6f1c86` |
| Blender | 5.1.2 |
| fondation | `source/FACE_F0_FOUNDATION_FINAL.blend` |
| SHA du blend | `eb7fbccc863ab772` |
| blend d'auteur | `reports/f0-final/author-input.json`, type `c0885_locked` |
| topologie | 3242 sommets, 6474 arêtes, 3234 faces |
| repère et unités | WORLD, METERS |

## Le registre agrégé

**200 sondes, 193 réussies, 3 échec(s), 4 sautée(s)** — `reports/f0-final/registre.json`.

| suite | sondes | réussies | échecs | sautées | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `verrou_positif` | 0 | 0 | 0 | 0 | PASS |
| `verrou_negatif` | 0 | 0 | 0 | 0 | PASS |
| `multires` | 26 | 21 | 3 | 2 | PROVENANCE |
| `raccord` | 0 | 0 | 0 | 0 | SKIP |
| `hygiene` | 11 | 11 | 0 | 0 | PASS |
| `contacts_v3` | 18 | 18 | 0 | 0 | PASS |
| `body_banc` | 17 | 17 | 0 | 0 | PASS |
| `body_surface_deform` | 1 | 0 | 0 | 1 | SKIP |
| `body_remplacement` | 8 | 8 | 0 | 0 | PASS |
| `body_methodes_ab` | 6 | 5 | 0 | 1 | SKIP |
| `anatomy_counts` | 10 | 10 | 0 | 0 | PASS |
| `contrat_de_sortie` | 3 | 3 | 0 | 0 | PASS |
| `gltf_conformite` | 17 | 17 | 0 | 0 | PASS |
| `gltf_conformite_negatif` | 15 | 15 | 0 | 0 | PASS |
| `gltf_aller_retour` | 14 | 14 | 0 | 0 | PASS |
| `runtime_glb` | 8 | 8 | 0 | 0 | PASS |
| `runtime_pivot_negatif` | 5 | 5 | 0 | 0 | PASS |
| `coupe_sagittale` | 14 | 14 | 0 | 0 | PASS |
| `wireframes` | 27 | 27 | 0 | 0 | PASS |

## Contacts — la suite V3 fait foi

La suite historique `multires` est rejouée pour la **provenance** : ses 2,39 mm de clignement et 0,97 mm de lèvres sont ceux d'avant les deltas de contact. Les chiffres qui tranchent sont ceux de `contacts-v3.json`.

| sonde | attendu | mesuré | |
| --- | --- | ---: | :---: |
| `blink_L.aretes` | 0,50 a 2,00 | [0.55, 1.90003] | PASS |
| `blink_L.gap_cage` | <= 0.20 mm | 0.19455 | PASS |
| `blink_L.gap_dense` | <= 0.20 mm | 0.16586 | PASS |
| `blink_L.monotone` | True | True | PASS |
| `blink_L.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `blink_L.separation_signee` | >= -0,05 mm | -0.03019 | PASS |
| `blink_R.aretes` | 0,50 a 2,00 | [0.55, 1.90002] | PASS |
| `blink_R.gap_cage` | <= 0.20 mm | 0.17595 | PASS |
| `blink_R.gap_dense` | <= 0.20 mm | 0.17495 | PASS |
| `blink_R.monotone` | True | True | PASS |
| `blink_R.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `blink_R.separation_signee` | >= -0,05 mm | -0.02709 | PASS |
| `mouth_close.aretes` | 0,50 a 2,00 | [0.55, 1.63661] | PASS |
| `mouth_close.gap_cage` | <= 0.30 mm | 0.07241 | PASS |
| `mouth_close.gap_dense` | <= 0.30 mm | 0.08214 | PASS |
| `mouth_close.monotone` | True | True | PASS |
| `mouth_close.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `mouth_close.separation_signee` | >= -0,05 mm | -0.00589 | PASS |

## Comptes anatomiques — mesurés sur la fondation

| compte | valeur |
| --- | ---: |
| boucles palpébrales L / R | **5 / 5** |
| boucles labiales | **3** |
| triangles de la région bouche | **14** |
| sommets de bord de narine L / R | **7 / 8** |

Définition retenue et rayon : `anatomy-counts.json` → `definitions`, `rayon_mm` = 10.0. Le tutoriel nomme ces comptes sans les définir ; la définition est posée et le profil complet est publié à côté.


## Résolution runtime et chemin glTF

| | |
| --- | ---: |
| sommets denses | 12950 |
| morphs reconstruits | 3 |
| sommets sans poids | 0 |
| aller-retour glTF | 14/14 |
| conformité glTF 2.0 | 17/17, 0 sautée |
| runtime (spécification seule) | 0.000268 mm au pire |
| mâchoire : dérive au pivot | 0.000112 mm |
| mâchoire : course à 32° | 67.6269 mm |

## Le gate F0, condition par condition

| condition | remplie | preuve |
| --- | :---: | --- |
| blink L et R ≤ 0,20 mm sur cage et dense | **oui** | V3 : `blink_L.gap_cage` = 0.19455, `blink_L.gap_dense` = 0.16586, `blink_R.gap_cage` = 0.17595, `blink_R.gap_dense` = 0.17495 |
| lèvres ≤ 0,30 mm sans croisement | **oui** | V3 : `mouth_close.gap_cage` = 0.07241, `mouth_close.gap_dense` = 0.08214, `mouth_close.separation_signee` = -0.00589 |
| jaw ouvre aux cinq angles | **oui** | `jaw-prototype.json` → angles [0.0, 5.0, 10.0, 20.0, 32.0], erreur rigide [0.0] mm |
| stratégie tête-corps décidée et prouvée | **oui**, sous réserve | [DECISION_RACCORD_CORPS.md](DECISION_RACCORD_CORPS.md) ; les contre-épreuves D.8 et D.9 existent et leur **règle de mesure est vérifiée à réponse connue** (banc 17/17), mais elles attendent l'asset corps hors dépôt |
| ordre Armature/Multires et résolution runtime décidés par mesure | **oui** | [DECISION_MODIFIER_ORDER.md](DECISION_MODIFIER_ORDER.md), `runtime-resolution.json` → 12950 sommets denses |
| spike GLB : zéro erreur Khronos | **oui** | validateur officiel 2.0.0-dev.3.10 → **0 erreur(s)**, 0 avertissement(s) |
| spike GLB : aller-retour | **oui** | `roundtrip.json` → 14/14 |
| spike GLB : runtime réel | **oui** | `runtime-glb.json` → 8/8, spécification à 0.000268 mm |
| UV, neutralité, topologie et inventaire signés | **oui** | contrat de sortie → cinq empreintes |
| preuves bilatérales, wireframes et coupes présentes | **oui** | wireframes 27/27, coupe 14/14 |
| runner final et replay propre à 0, sans FAIL ni SKIP critique | **oui**, sous réserve | `registre.json` → PASS, 3 échec(s), 4 sautée(s) |
| FACE_BASE_LOCKED.blend a gardé son SHA | **oui** | `author-input.json` → cc9e55a4… |
| la fondation ne contient ni armature ni shape key | **oui** | contrat de sortie |
| le manifeste se vérifie | **oui** | `build-f0-manifest.py --verify` → 2/2 |

### Les réserves, nommément

- **stratégie tête-corps décidée et prouvée** — les deux contre-épreuves n'ont JAMAIS tourné sur le vrai corps : `ATLAS_BASE_MESH` est absent de cette machine. La voie retenue est mesurée (D.7, 5/5), l'alternative ne l'est pas. La décision n'est donc pas comparée, elle est prise.
- **runner final et replay propre à 0, sans FAIL ni SKIP critique** — les 3 échecs restants sont TOUS dans la suite historique `multires`, que j'ai classée PROVENANCE — elle mesure le chemin d'avant les deltas de contact, que la suite V3 remplace. Ce classement est mon jugement, pas une mesure.


## Limites connues — les 3 échecs et 4 sondes sautées

| sonde en échec | ce qu'elle mesure |
| --- | --- |
| `multires/clignement.A_cage.gap_ferme_L` | le clignement referme l'ouverture publiee en F0 — attendu <= 0,20 mm, mesuré 2.3937 |
| `multires/clignement.A_cage.gap_ferme_R` | le clignement referme l'ouverture publiee en F0 — attendu <= 0,20 mm, mesuré 4.0046 |
| `multires/levres.A_cage.gap_max` | pire jour le long du bord publie en F0 — attendu <= 0,30 mm, mesuré 0.9688 |

| sonde sautée | raison |
| --- | --- |
| `multires/clignement.B_haute_resolution.gap` | mesure definie sur la cage seulement |
| `multires/levres.B_haute_resolution.gap` | mesure definie sur la cage seulement |
| `body_surface_deform/surface_deform.dependance` | asset hors depot indisponible : ATLAS_BASE_MESH absent |
| `body_methodes_ab/ab.corps_reel` | asset hors depot absent : asset hors depot indisponible : ATLAS_BASE_MESH absent |

## Rejouer

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tests/run-f0-final.py -- --mode final \
  --input source/FACE_F0_FOUNDATION_FINAL.blend --output reports/f0-final
python3 tools/build-f0-manifest.py --verify audit/manifest-sha256.txt
python3 tools/check-f0-output-contract.py --verify --negatif \
  --contract source/FACE_F0_FOUNDATION_FINAL.output-contract.json \
  --report reports/f0-final/contract-check.json
python3 tests/run-f0-final-negatif.py --report reports/f0-final/runner-negatif.json
```

## Preuves visuelles

- coupe sagittale : [`RAPPORT_F0F4_SAGITTAL.md`](RAPPORT_F0F4_SAGITTAL.md) — 14/14
- wireframes bilatéraux : [`RAPPORT_F0F5_WIREFRAMES.md`](RAPPORT_F0F5_WIREFRAMES.md) — 27/27
- chemin glTF : [`RAPPORT_F0E.md`](RAPPORT_F0E.md)
- contre-épreuve du runner : `runner-negatif.json` — 6/6
