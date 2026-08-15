STATUS: F0 INCOMPLET — le raccord corps ne passe pas les seuils

| | |
| --- | --- |
| **statut global** | **F0 INCOMPLET** — voir `reports/f0-correction/RAPPORT_F0_CORRECTION.md` |
| dernière étape terminée | audit topologique, décision multires, décision de topologie, base verrouillée |
| étape suivante | **finir la correction F0** : trancher le raccord corps, banc multires anatomique. **F1 ne commence pas.** |
| branche active | `face/chat-3-caucasian-v1` |
| commit de départ | `4c6a4dbfbaddc52fbf1222afd7e07b65de915b96` |
| géométrie faciale | **verrouillée** : `source/FACE_BASE_LOCKED.blend` |
| shape keys | **aucune** — c'est voulu, F1 n'en demande pas |
| rig facial | **inexistant** |
| sondes vérifiées / total | comptées par registre, plus à la main : 5/5 préflight, 11/11 scellement, 15/15 raccord (dont 2 seuils en échec assumés) |
| processus actifs | **aucun** |

## Ce qui existe maintenant

- `source/FACE_BASE_LOCKED.blend` — 5 objets, 5 134 sommets, 5 122 faces,
  échelle 1, rotation nulle, position monde inchangée ;
- `tests/verrou-topologie.py` + `tests/verrou-topologie.json` — le test qui
  échoue si la topologie ou le neutre bouge ;
- `tests/f0-audit-topologie.py` — 15 sondes, chacune vérifiée sur une
  configuration à réponse connue avant tout verdict ;
- `tests/f0-multires.py` — banc A/B cage contre maillage subdivisé ;
- `tests/rendus-neutre.py` — rendus de référence à exposition calibrée puis
  verrouillée, histogramme publié pour chaque vue ;
- `reports/f0/RAPPORT_F0.md` et les deux JSON de mesures ;
- `renders/f0/` — 10 vues neutres, 0 % de noirs bouchés, ≤ 0,084 % de blancs
  brûlés ;
- `docs/DENTS_ET_LANGUE.md`, `docs/FACS_MATRIX.md`.

## Décisions prises, et sur quelle mesure

| décision | mesure qui la porte |
| --- | --- |
| **cage de 3 242 sommets conservée** (option 1) | topologie exactement symétrique, 0 non-manifold, aucun n-gon en zone d'expression, 5 boucles régulières aux lèvres |
| **shape keys sur la cage, multires gardé en fin de pile, jamais appliqué** | niveau 0 = cage à 0,000000000 mm ; le niveau 1 porte du sculpt réel (2,10 mm au pire sur le visage) ; 4× moins de points de contrôle |
| **échelle appliquée (1,1,1)** | l'application déplace la surface de 0,001213 mm, sous les 0,01 mm du critère de `docs/SCOPE_V1.md` |
| **asymétrie géométrique conservée** | 0,083 mm en médiane sur le visage ; elle sert le photoréalisme, et le miroir se fait par indice |
| **dents prises dans l'asset source** | `Jaw - Realistic`, 28 dents + mandibule, CC0, même paquet |

## Ce qui n'existe pas

Aucun os, aucun contrôleur, aucun driver, aucune shape key, aucun visème, aucune
vidéo. La langue n'existe pas et les dents ne sont pas encore recalées.

## Blocages et réserves connus

1. **Langue absente** du paquet source — à construire, procédurale et versionnée.
2. **Dents non recalées** : `Jaw - Realistic` est ailleurs dans la scène du
   paquet et à une autre échelle relative. Le recalage doit être mesuré.
3. **14 triangles au philtrum et à la lèvre inférieure**, 6 à 11 mm de la couture
   labiale. Seule réserve topologique du visage. À trancher **entre F1 et F2**.
4. **4 boucles de paupière seulement** dans 5,5 mm : juste suffisant pour un
   clignement. À vérifier en F2 avant d'aller plus loin.
5. **Narines à 7–8 sommets** de pourtour — grossières pour du pincement narinaire.
6. Le manifeste du bootstrap se référençait lui-même, ce qui est impossible à
   satisfaire. Corrigé : le manifeste ne se liste plus.
