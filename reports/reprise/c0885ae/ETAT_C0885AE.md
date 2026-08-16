# État de reprise au commit `c0885ae`

| | |
| --- | --- |
| commit | `c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0` |
| branche | `face/chat-3-caucasian-v1` |
| `git status --short` | **vide** |
| `git diff` / `--cached` | code **0** / **0** |
| descendant de `f852c453…` | **oui** (`git merge-base --is-ancestor` → 0) |
| Blender | **5.1.2** (`ec6e62d40fa9`) — pas dans le `PATH`, chemin absolu dans `work/blender-path.txt` |
| asset externe | 49 420 489 octets, SHA `3c121505…c75c137` — **conformes** |
| `source/FACE_BASE_LOCKED.blend` | SHA `cc9e55a4…831f2bd8` — **conforme au tutoriel** |
| les cinq empreintes | **identiques** au caractère près |

> **Écart de comptage, signalé et non corrigé.** Le §2 annonce « 40 entrées au
> manifeste, 41 fichiers suivis ». C'était vrai à `f852c453`. À `c0885ae` le
> dépôt en compte **72 et 73** : les passes de correction ont ajouté scripts,
> rapports et rendus. Le manifeste reste sans autoréférence et vérifie 0 échec.

## Les trois registres rejoués

| suite | mesuré | attendu par le tutoriel | code shell **avant** F0-A.5 | **après** |
| --- | --- | --- | ---: | ---: |
| multires V2 | **21 PASS / 3 FAIL / 2 SKIP** | 21 / 3 / 2 | 0 | **2** |
| raccord corps | **13 PASS / 2 FAIL** | 13 / 2 | 0 | **2** |
| hygiène brute | **10 PASS / 1 FAIL** | 10 / 1 | 1 | 1 |

## Les cinq mesures qui doivent échouer

| mesure | mesuré | limite | JSON |
| --- | ---: | ---: | --- |
| blink L à 100 % | **2,3937 mm** | 0,20 | `multires-ab-v2.json` |
| blink R à 100 % | **4,0046 mm** | 0,20 | `multires-ab-v2.json` |
| lèvres à 100 % | **0,9688 mm** | 0,30 | `multires-ab-v2.json` |
| raccord, écart d'échelle | **3,34463 %** | 1,0 | `raccord-corps.json` |
| raccord, résidu max | **4,0694 mm** | 2,0 | `raccord-corps.json` |

Reproduction **exacte**, au chiffre près. Aucun seuil n'a été touché.

## Verrou

Positif **code 0**. Négatif **code 0** : les neuf mutations sont refusées,
l'original est accepté, et le SHA du maître est identique avant et après.
`git diff` sur `FACE_BASE_LOCKED.blend` et `verrou-topologie.json` : **0**.
