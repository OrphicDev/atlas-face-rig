# F0 — rapport final

> **F0 INCOMPLÈTE.** Ce rapport ne clôture pas F0 : plusieurs conditions du gate ne sont pas remplies, et elles sont nommées plus bas.

## Provenance et environnement

| | |
| --- | --- |
| commit | `8a43c15` |
| Blender | 5.1.2 |
| fondation | `source/FACE_F0_FOUNDATION_FINAL.blend` |
| SHA du blend | `eb7fbccc863ab772` |
| blend d'auteur | `reports/f0-final/author-input.json`, type `c0885_locked` |
| topologie | 3242 sommets, 6474 arêtes, 3234 faces |
| repère et unités | WORLD, METERS |

## Le registre agrégé

**167 sondes, 154 réussies, 10 échec(s), 3 sautée(s)** — `reports/f0-final/registre.json`.

| suite | sondes | réussies | échecs | sautées | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `verrou_positif` | 0 | 0 | 0 | 0 | PASS |
| `verrou_negatif` | 0 | 0 | 0 | 0 | PASS |
| `multires` | 26 | 21 | 3 | 2 | PROVENANCE |
| `raccord` | 0 | 0 | 0 | 0 | SKIP |
| `hygiene` | 11 | 11 | 0 | 0 | PASS |
| `contacts_v3` | 18 | 15 | 3 | 0 | FAIL |
| `anatomy_counts` | 10 | 10 | 0 | 0 | PASS |
| `contrat_de_sortie` | 3 | 2 | 1 | 0 | FAIL |
| `gltf_conformite` | 16 | 15 | 0 | 1 | FAIL |
| `gltf_conformite_negatif` | 15 | 15 | 0 | 0 | PASS |
| `gltf_aller_retour` | 14 | 14 | 0 | 0 | PASS |
| `runtime_glb` | 8 | 8 | 0 | 0 | PASS |
| `runtime_pivot_negatif` | 5 | 5 | 0 | 0 | PASS |
| `coupe_sagittale` | 14 | 11 | 3 | 0 | FAIL |
| `wireframes` | 27 | 27 | 0 | 0 | PASS |

## Contacts — la suite V3 fait foi

La suite historique `multires` est rejouée pour la **provenance** : ses 2,39 mm de clignement et 0,97 mm de lèvres sont ceux d'avant les deltas de contact. Les chiffres qui tranchent sont ceux de `contacts-v3.json`.

| sonde | attendu | mesuré | |
| --- | --- | ---: | :---: |
| `blink_L.aretes` | 0,50 a 2,00 | [0.55, 1.90003] | PASS |
| `blink_L.gap_cage` | <= 0.20 mm | 0.21516 | FAIL |
| `blink_L.gap_dense` | <= 0.20 mm | 0.18044 | PASS |
| `blink_L.monotone` | True | True | PASS |
| `blink_L.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `blink_L.separation_signee` | >= -0,05 mm | -0.06136 | FAIL |
| `blink_R.aretes` | 0,50 a 2,00 | [0.55, 1.90002] | PASS |
| `blink_R.gap_cage` | <= 0.20 mm | 0.18756 | PASS |
| `blink_R.gap_dense` | <= 0.20 mm | 0.18595 | PASS |
| `blink_R.monotone` | True | True | PASS |
| `blink_R.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `blink_R.separation_signee` | >= -0,05 mm | -0.07108 | FAIL |
| `mouth_close.aretes` | 0,50 a 2,00 | [0.55, 1.57573] | PASS |
| `mouth_close.gap_cage` | <= 0.30 mm | 0.09203 | PASS |
| `mouth_close.gap_dense` | <= 0.30 mm | 0.09631 | PASS |
| `mouth_close.monotone` | True | True | PASS |
| `mouth_close.retour_neutre` | <= 0,01 mm | 0.0 | PASS |
| `mouth_close.separation_signee` | >= -0,05 mm | -0.00358 | PASS |

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
| conformité glTF 2.0 | 15/16, 1 sautée |
| runtime (spécification seule) | 0.000268 mm au pire |
| mâchoire : dérive au pivot | 0.000112 mm |
| mâchoire : course à 32° | 67.6269 mm |

## Le gate F0, condition par condition

| condition | remplie | preuve |
| --- | :---: | --- |
| blink L et R ≤ 0,20 mm sur cage et dense | **non** | V3 : `blink_L.gap_cage` = 0.21516, `blink_L.gap_dense` = 0.18044, `blink_R.gap_cage` = 0.18756, `blink_R.gap_dense` = 0.18595 |
| lèvres ≤ 0,30 mm sans croisement | **oui** | V3 : `mouth_close.gap_cage` = 0.09203, `mouth_close.gap_dense` = 0.09631, `mouth_close.separation_signee` = -0.00358 |
| jaw ouvre aux cinq angles | **oui** | `jaw-prototype.json` → angles [0.0, 5.0, 10.0, 20.0, 32.0], erreur rigide [0.0] mm |
| stratégie tête-corps décidée et prouvée | **oui** | [DECISION_RACCORD_CORPS.md](DECISION_RACCORD_CORPS.md) |
| ordre Armature/Multires et résolution runtime décidés par mesure | **oui** | [DECISION_MODIFIER_ORDER.md](DECISION_MODIFIER_ORDER.md), `runtime-resolution.json` → 12950 sommets denses |
| spike GLB : zéro erreur Khronos | **non** | **validateur Khronos absent de la machine** — sonde publiée SAUTÉE, jamais PASS |
| spike GLB : aller-retour | **oui** | `roundtrip.json` → 14/14 |
| spike GLB : runtime réel | **oui** | `runtime-glb.json` → 8/8, spécification à 0.000268 mm |
| UV, neutralité, topologie et inventaire signés | **oui** | contrat de sortie → cinq empreintes |
| preuves bilatérales, wireframes et coupes présentes | **non** | wireframes 27/27, coupe 11/14 |
| runner final et replay propre à 0, sans FAIL ni SKIP critique | **non** | `registre.json` → FAIL, 10 échec(s), 3 sautée(s) |
| FACE_BASE_LOCKED.blend a gardé son SHA | **oui** | `author-input.json` → cc9e55a4… |
| la fondation ne contient ni armature ni shape key | **oui** | contrat de sortie |
| le manifeste se vérifie | **oui** | `build-f0-manifest.py --verify` → 2/2 |

## Limites connues — les 10 échecs et 3 sondes sautées

| sonde en échec | ce qu'elle mesure |
| --- | --- |
| `multires/clignement.A_cage.gap_ferme_L` | le clignement referme l'ouverture publiee en F0 — attendu <= 0,20 mm, mesuré 2.3937 |
| `multires/clignement.A_cage.gap_ferme_R` | le clignement referme l'ouverture publiee en F0 — attendu <= 0,20 mm, mesuré 4.0046 |
| `multires/levres.A_cage.gap_max` | pire jour le long du bord publie en F0 — attendu <= 0,30 mm, mesuré 0.9688 |
| `contacts_v3/blink_L.gap_cage` | jour final sur la cage — attendu <= 0.20 mm, mesuré 0.21516 |
| `contacts_v3/blink_L.separation_signee` | pas de croisement des marges — attendu >= -0,05 mm, mesuré -0.06136 |
| `contacts_v3/blink_R.separation_signee` | pas de croisement des marges — attendu >= -0,05 mm, mesuré -0.07108 |
| `contrat_de_sortie/contrat.verification` | chaque artefact retrouve son SHA — attendu 0, mesuré 3 |
| `coupe_sagittale/sagittal.image.median_bouche` | l'image n'est pas un clay uniforme et montre la section — attendu >= 8 teintes, >= 20 px de section, >= 200 px de peau, mesuré 128 teintes, 19 section, 8 muqueuse, 0 globe, 375044 peau |
| `coupe_sagittale/sagittal.image.median_cavite_orale` | l'image n'est pas un clay uniforme et montre la section — attendu >= 8 teintes, >= 20 px de section, >= 200 px de peau, mesuré 98 teintes, 0 section, 4 muqueuse, 0 globe, 348087 peau |
| `coupe_sagittale/sagittal.image.median_cou` | l'image n'est pas un clay uniforme et montre la section — attendu >= 8 teintes, >= 20 px de section, >= 200 px de peau, mesuré 82 teintes, 0 section, 0 muqueuse, 0 globe, 563195 peau |

| sonde sautée | raison |
| --- | --- |
| `multires/clignement.B_haute_resolution.gap` | mesure definie sur la cage seulement |
| `multires/levres.B_haute_resolution.gap` | mesure definie sur la cage seulement |
| `gltf_conformite/khronos.validator` | validateur Khronos absent de la machine : ni `gltf-validator` dans le PATH ni --khronos fourni |

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

- coupe sagittale : [`RAPPORT_F0F4_SAGITTAL.md`](RAPPORT_F0F4_SAGITTAL.md) — 11/14
- wireframes bilatéraux : [`RAPPORT_F0F5_WIREFRAMES.md`](RAPPORT_F0F5_WIREFRAMES.md) — 27/27
- chemin glTF : [`RAPPORT_F0E.md`](RAPPORT_F0E.md)
- contre-épreuve du runner : `runner-negatif.json` — 6/6
