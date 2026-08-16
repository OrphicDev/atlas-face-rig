# Passe 3 — sondes de mesure vérifiées, verdicts anatomiques partiels

Suite de [`RAPPORT_PASSE2.md`](RAPPORT_PASSE2.md). **Statut inchangé :
`F0 INCOMPLET`.** F1 ne commence pas.

État réel au §1 : `HEAD` valait `ffdad5d`, descendant de `f852c453…` (vérifié
par `git merge-base --is-ancestor`), arbre propre, manifeste sans échec.

---

## 1. Le repère du globe — l'approximation est supprimée

La passe 2 s'arrêtait sur un repère faux : la sclère approchée par une sphère
laissait **0,6934 mm** de résidu sur 11,74 mm de rayon, et tout seuil de
pénétration bâti dessus était sans valeur.

**L'approximation a été supprimée.** Le globe, c'est maintenant le **maillage du
globe** : appartenance testée par **parité de rayon** contre un `BVHTree`
construit sur la sclère telle qu'elle est modélisée.

| sonde | configuration connue | attendu | obtenu | |
| --- | --- | ---: | ---: | :---: |
| appartenance, centre du globe | maillage de `sclera.L` | intérieur | intérieur | **PASS** |
| appartenance, point à 300 mm | idem | extérieur | extérieur | **PASS** |

## 2. La sonde de jour palpébral, enfin vérifiée

Elle reprend désormais **la définition déjà auditée en F0** — les `indices` de
bord publiés dans [`reports/f0/audit-topologie.json`](../f0/audit-topologie.json)
— au lieu d'en inventer une nouvelle.

| sonde | attendu (F0) | obtenu | écart | |
| --- | ---: | ---: | ---: | :---: |
| ouverture palpébrale gauche | 18,38 mm | **18,3834** | 0,003 | **PASS** |
| ouverture palpébrale droite | 16,34 mm | **16,3367** | 0,003 | **PASS** |

Trois définitions différentes avaient été essayées avant celle-ci, et chacune
rendait un nombre différent : 25,1 mm en prenant tout le pourtour de l'orbite,
10,84 mm en ne prenant que les sommets côté peau, 4,21 mm en mesurant colonne
par colonne. **F0 mesurait la hauteur de la boîte englobante de TOUS les sommets
du bord** ; il fallait reprendre exactement cet ensemble pour pouvoir comparer.

## 3. Un fait mesuré sur l'asset : il s'auto-intersecte au neutre

Test d'appartenance vérifié, appliqué au maillage **neutre** :

| | sommets |
| --- | ---: |
| antérieurs, à l'intérieur d'une sclère | **193** |
| postérieurs, à l'intérieur d'une sclère | 15 |
| **total** | **208** |

**L'asset livré traverse déjà ses propres globes oculaires au repos.** Le seuil
du cahier — « pénétration : 0 sommet » — est donc **inatteignable par
construction** sur cette source.

Le critère appliqué est par conséquent **différentiel**, et il est annoncé avant
la mesure : *le clignement ne doit pas ajouter de pénétration antérieure*. Ce
n'est pas un seuil élargi pour faire passer un résultat, c'est le seul critère
qui ait un sens quand la référence n'est pas nulle.

## 4. Banc V2 — résultats mesurés

**27 sondes : 22 PASS, 4 FAIL, 1 SKIP** — comptées par le registre, jamais à la
main. → [`multires-ab-v2.json`](multires-ab-v2.json)

### Ce qui passe

| critère | voie A — cage | voie B — haute résolution |
| --- | ---: | ---: |
| retour au neutre, 3 prototypes | **0,000000 mm** | **0,000000 mm** |
| 0° de mâchoire rend le neutre | **0,000000 mm** | **0,000000 mm** |
| UV de la cage, avant/après shape key | identiques | identiques |
| UV évaluées, neutre/déformé | identiques | identiques |
| pénétration antérieure au clignement (réf. 193) | **73** | **0** |
| fente labiale, médiane (neutre 1,935 mm) | **1,377** | **0,698** |

La voie B ne crée **aucune** pénétration ; la voie A en laisse 73, soit trois
fois moins qu'au neutre, mais la subdivision d'une cage déformée ramène de la
peau dans le globe. C'est le premier écart anatomique réel entre les deux voies.

### Ce qui échoue, et pourquoi

| critère | seuil | voie A | voie B |
| --- | ---: | ---: | ---: |
| jour palpébral à 100 % | ≤ 0,20 mm | **6,358 / 7,143 mm** | non mesuré (cage seule) |
| pire écart labial | ≤ 0,30 mm | **6,738 mm** | **6,609 mm** |

**Ces échecs sont ceux de mon prototype, pas de la topologie**, et la cause est
identifiée :

- le clignement n'agit que dans un rayon de **R + 5,5 mm** autour du globe,
  alors que la métrique auditée porte aussi sur les sommets **conjonctivaux**,
  qui sont hors de ce rayon et ne bougent donc jamais. La déformation et la
  mesure ne portent pas sur le même ensemble de sommets ;
- une première version faisait parcourir à chaque paupière 75 % et 25 % de **sa
  propre** course, si bien qu'elles ne pouvaient pas se rejoindre par
  construction. Corrigé — les deux marges visent désormais la même ligne de
  contact — et le jour est tombé de 9,06 / 10,73 mm à **6,358 / 7,143 mm** ;
- le pire écart labial se situe au bord de la bande échantillonnée, là où le
  poids latéral tend vers zéro pour tenir les commissures fixes.

**Le §12 n'est donc PAS déclenché.** Aucune insuffisance de topologie n'est
démontrée : ce qui est démontré, c'est que mon prototype de clignement ne
couvre pas encore toute la paupière. **Aucune retopologie n'est décidée.**

## 5. Temps et mémoire — mesurés

20 évaluations après 5 échauffements, par prototype et par voie :

| | voie A — cage | voie B — haute résolution |
| --- | ---: | ---: |
| points de contrôle | **3 242** | 12 950 |
| temps médian | 0,0365 s | **0,0255 s** |
| `.blend` compressé réel, Basis + une shape key | **~1 018 000 o** | ~1 774 000 o |

## 6. Ce qui reste dû pour lever `F0 INCOMPLET`

1. **étendre l'influence du clignement** à l'ensemble des sommets de bord
   audités, puis reprendre le seuil de jour ;
2. **trancher le raccord corps** entre remplacement complet et transfert de
   déformations, avec les preuves visuelles du §7.5 ;
3. **export glTF** aller-retour et empreintes UV d'export (§9.9) ;
4. **ordre des modificateurs** Armature/Multires (§9.6) et **stratégie de
   résolution de rendu** (§9.10) ;
5. **coupe sagittale** (§10), **hygiène des chemins** (§13), **vues
   bilatérales** et **wireframes** (§14) ;
6. **preuves visuelles** du banc (§9.11) et du raccord.
