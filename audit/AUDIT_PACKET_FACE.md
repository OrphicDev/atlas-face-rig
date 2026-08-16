# Paquet d'audit — phase F0

## Dépôt et commits

| | |
| --- | --- |
| dépôt | `https://github.com/OrphicDev/atlas-face-rig` |
| branche | `face/chat-3-caucasian-v1` |
| commit de bootstrap | `4c6a4dbfbaddc52fbf1222afd7e07b65de915b96` |
| commit de phase F0 | *voir `CHANGELOG.md` et le dernier commit de la branche* |
| comparaison | `https://github.com/OrphicDev/atlas-face-rig/compare/4c6a4db...face/chat-3-caucasian-v1` |

## Environnement

| | |
| --- | --- |
| Blender | **5.1.2** (`ec6e62d40fa9`, 2026-05-19) |
| système | macOS, Darwin 25.5.0 |
| Git LFS | **absent de la machine** — aucun fichier n'en dépend, le `.blend` fait 980 099 octets et les rendus 21 Mo au total |

## Asset source

| | |
| --- | --- |
| fichier | `human_base_meshes_bundle.blend` |
| paquet | Human Base Meshes bundle **v1.4.1**, Blender Studio, **CC0** |
| taille attendue / **mesurée** | 49 420 489 / **49 420 489 octets** ✔ |
| SHA-256 attendu / **mesuré** | `3c121505…c75c137` / **identique** ✔ |
| désignation | `ATLAS_BASE_MESH` |
| **non redistribué** | le paquet n'est pas versionné dans ce dépôt |
| collection retenue | `Head (Animation) - Realistic` |
| objet supplémentaire retenu | `Jaw - Realistic` (dents), même paquet, même licence |

## Topologie verrouillée

`source/FACE_BASE_LOCKED.blend`

| | |
| --- | --- |
| objets | 5 |
| sommets | **5 134** |
| faces | **5 122** |
| octets | 980 099 |
| SHA-256 | `669ccdb7858adea2e3091218bdfeed4fe1b4d955d866497ad20e8559c95e55bd` |
| empreinte de topologie | `d29e2af3ef67aec5bad705c5e5a4b72428f906f01af94c33880c85a47722e5ae` |
| empreinte de pose neutre | `9246d8acb2d68a38a6f355db90df967e8f6e71907343ce1cf028549bed20c324` |
| transformations | échelle 1,1,1 · rotation nulle · position monde inchangée |

## Commandes et codes de sortie

Toutes lancées avec `--background --factory-startup --python-exit-code 1`.

| commande | code |
| --- | ---: |
| `blender … --python tests/f0-audit-topologie.py -- reports/f0/audit-topologie.json` | **0** |
| `blender … --python tests/f0-multires.py -- reports/f0/multires-ab.json` | **0** |
| `blender … --python rig/construire-face-base.py -- source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json` | **0** |
| `blender … --python tests/verrou-topologie.py -- source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json` | **0** |
| `blender … --python tests/rendus-neutre.py -- source/FACE_BASE_LOCKED.blend renders/f0` | **0** |

## Sondes et tests

**19 sondes vérifiées sur 19**, chacune sur une configuration à réponse connue,
avant tout verdict. Les scripts sortent en code 2 sans publier de chiffre si une
seule échoue.

| script | sondes | résultat |
| --- | ---: | --- |
| `tests/f0-audit-topologie.py` | 15 | toutes OK |
| `tests/f0-multires.py` | 4 | toutes OK |
| `tests/verrou-topologie.py` | verrou topologie + verrou neutre | OK |

**Trois sondes fausses ont été prises par leur propre auto-test** et corrigées
avant publication : le groupement des anneaux de bord (par face, non par
sommet) ; le test de symétrie (qui déplaçait un sommet posé sur le plan miroir) ;
la contre-épreuve du banc multires (qui ne marquait pas le graphe de dépendances
et relisait donc la même évaluation).

## FACS

**Aucune action implémentée.** `docs/FACS_MATRIX.md` est le registre vide, avec
les contraintes que la mesure F0 impose déjà.

## Défauts et réserves

| | |
| --- | --- |
| langue | **absente**, à construire |
| dents | trouvées (`Jaw - Realistic`, 28 dents + mandibule, CC0) mais **non recalées** |
| 14 triangles | philtrum et lèvre inférieure, 6 à 11 mm de la couture labiale |
| paupières | 4 boucles seulement dans 5,5 mm |
| narines | 7 à 8 sommets de pourtour |
| asymétrie géométrique | 1,689 mm au maximum (oreilles), 0,083 mm en médiane — conservée volontairement |
| manifeste du bootstrap | se référençait lui-même ; corrigé |
| premier jeu de rendus | brûlait jusqu'à 95,5 % de l'image ; jeté, éclairage recalibré |

## Fichiers publics

```text
source/FACE_BASE_LOCKED.blend
tests/f0-audit-topologie.py   tests/f0-multires.py
tests/verrou-topologie.py     tests/verrou-topologie.json
tests/rendus-neutre.py
rig/construire-face-base.py
reports/f0/RAPPORT_F0.md      reports/f0/audit-topologie.json
reports/f0/multires-ab.json
renders/f0/*.png              renders/f0/histogrammes.json
docs/DENTS_ET_LANGUE.md       docs/FACS_MATRIX.md   docs/SCOPE_V1.md
handoffs/BOOTSTRAP_CHAT_3_FACE.md   handoffs/HANDOFF_FACE_NEXT.md
audit/AUDIT_PACKET_FACE.md    audit/manifest-sha256.txt
```

Aucun secret, aucune conversation, aucun asset sans droits — **mesuré**, pas
affirmé, par `tests/f0-hygiene-blend.py` : 0 jeton, 0 clé privée, 0 courriel,
0 bibliothèque liée, 0 image externe, 0 script embarqué.

> **Correction d'une affirmation fausse.** Ce paquet annonçait « aucun chemin
> personnel ». C'est faux et l'audit l'avait vu : `FACE_BASE_LOCKED.blend`
> contient **une** chaîne `/Users/orphicagency`, dans l'en-tête où Blender
> inscrit le chemin de sa propre dernière sauvegarde
> (`.../atlas-face-rig/source/FACE_BASE_LOCKED.blend`). Elle est intrinsèque au
> format : Blender l'écrit à chaque `save_as_mainfile` et il n'existe pas
> d'option pour l'omettre. Risque : elle divulgue le nom d'utilisateur macOS et
> l'arborescence du poste de travail. Elle ne contient ni secret, ni jeton, ni
> adresse. Mesure et détail dans
> [`reports/f0-correction/hygiene-blend.json`](../reports/f0-correction/hygiene-blend.json).

## Temps

Une session. F0 seule : audit topologique, banc multires, base verrouillée,
verrou, rendus, rapports.
