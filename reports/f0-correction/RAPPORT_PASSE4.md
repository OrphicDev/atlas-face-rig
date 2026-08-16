# Passe 4 — prototypes ancrés, hygiène du `.blend`

Suite de [`RAPPORT_PASSE3.md`](RAPPORT_PASSE3.md). **Statut inchangé :
`F0 INCOMPLET`.** F1 ne commence pas.

État réel au §1 : `HEAD` = `17f6828`, descendant vérifié de `f852c453…`, arbre
propre, manifeste sans échec, verrou positif code 0.

---

## 1. Les prototypes sont ancrés sur les bords publiés en F0

La passe 3 avait nommé la cause : la déformation portait sur un rayon autour du
globe, la métrique sur les sommets de bord audités — **deux ensembles
différents**. C'est corrigé : `Clignement` et `FermetureLabiale` prennent
maintenant en entrée les `indices` publiés dans
[`reports/f0/audit-topologie.json`](../f0/audit-topologie.json), et le poids
décroît avec la **distance à ce bord**.

Deuxième correction, énoncée avant la mesure : le poids latéral valait
`1 − lisse(|x|/demi)`, donc il décroissait **dès le centre** de la fente et
interdisait la fermeture sur les deux tiers latéraux. Une paupière se ferme sur
toute sa longueur et ne reste ouverte qu'aux canthus : `poids_canthus()` vaut
désormais 1 partout et ne retombe que dans les **15 % près des extrémités**.

Troisième correction, tirée du rendu de la passe 3 où tout le bas du visage
descendait en bloc : `Machoire` reçoit trois garde-fous — lèvre supérieure
rattachée au crâne, relâchement en arrière du pivot pour que la nuque ne suive
pas, relâchement vers le bas du cou.

## 2. Effet mesuré

| mesure | passe 3 | **passe 4** | seuil |
| --- | ---: | ---: | ---: |
| jour palpébral gauche à 100 % | 6,358 mm | **2,394 mm** | 0,20 |
| jour palpébral droit à 100 % | 7,143 mm | **4,005 mm** | 0,20 |
| jour labial à 100 % (bord audité) | — | **0,969 mm** | 0,30 |
| pénétration antérieure, voie A | 73 | **64** | ≤ 193 (neutre) |
| pénétration antérieure, voie B | 0 | **6** | ≤ 193 (neutre) |

Départ : **18,383 mm** à gauche, **16,337 mm** à droite, **5,691 mm** aux
lèvres. La fermeture atteint donc **87 %**, **75 %** et **83 %** de la course.
Le résidu se situe exactement dans la zone de garde des canthus et des
commissures — là où mon poids retombe volontairement à zéro.

Restent vrais et inchangés : **retour au neutre `0,000000 mm`** sur les deux
voies et les trois prototypes, **0° de mandibule rend exactement le neutre**,
**UV de la cage et UV évaluées intactes**.

**Registre : 21 PASS, 3 FAIL, 2 SKIP sur 26.** Les trois échecs sont les trois
seuils de fermeture ci-dessus. **Le §12 n'est toujours pas déclenché** : aucune
insuffisance de topologie n'est démontrée, ce qui est démontré c'est que la zone
de garde de mon prototype est trop large.

## 3. Preuves visuelles

14 vues dans [`renders/f0-correction/`](../../renders/f0-correction), même
éclairage, globes colorés. Le clignement à 100 % ferme visiblement l'œil — il ne
subsiste qu'un liseré au canthus latéral, cohérent avec les 2,39 mm mesurés. La
mandibule à 32 ° conserve désormais lèvres, philtrum et menton, là où la passe 3
les effaçait.

## 4. P1 §13 — hygiène et chemins · **MESURÉ**

[`tests/f0-hygiene-blend.py`](../../tests/f0-hygiene-blend.py) : le `.blend`
compressé est réécrit **non compressé** dans un dossier temporaire, puis scanné
octet par octet, et l'API Blender est interrogée séparément. Construction en
environnement isolé (`BLENDER_USER_CONFIG/SCRIPTS/DATAFILES` vers un `mktemp -d`,
`HOME` jamais touché).

Le scanner est vérifié sur deux fichiers témoins fabriqués : **5 sondes sur 5**
— il voit `/Users`, `/home`, le nom du paquet source et une adresse de courriel,
et ne produit **aucun faux positif** sur un fichier neutre.

| contrôle | résultat |
| --- | ---: |
| jetons, clés privées | **0** |
| adresses de courriel | **0** |
| bibliothèques liées | **0** |
| images externes | **0** |
| scripts embarqués | **0** |
| caches de simulation | **0** |
| **chaînes `/Users/…`** | **1** |

**L'audit avait raison.** Le paquet d'audit affirmait « aucun chemin
personnel » : c'est faux. Le fichier contient **une** occurrence de
`/Users/orphicagency`, dans l'en-tête où Blender inscrit le chemin de sa propre
dernière sauvegarde. Elle est **intrinsèque au format** — Blender l'écrit à
chaque `save_as_mainfile` et n'offre aucune option pour l'omettre. Risque : elle
divulgue le nom d'utilisateur macOS et l'arborescence du poste. Elle ne contient
ni secret, ni jeton, ni adresse.

`audit/AUDIT_PACKET_FACE.md` est corrigé en conséquence : l'affirmation est
remplacée par la mesure et par la documentation du risque, comme le §13.3
l'exige.

→ [`hygiene-blend.json`](hygiene-blend.json)

## 5. Ce qui reste dû

1. **resserrer la zone de garde** des canthus et des commissures, puis reprendre
   les trois seuils de fermeture ;
2. **trancher le raccord corps** entre remplacement complet et transfert, avec
   les preuves visuelles du §7.5 ;
3. **export glTF** aller-retour et empreintes UV d'export (§9.9) ;
4. **ordre des modificateurs** Armature/Multires (§9.6) et **stratégie de
   résolution** (§9.10) ;
5. coupe sagittale **deux couleurs avec règle** (§10), **vues bilatérales** et
   **wireframes** (§14).
