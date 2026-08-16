# Correction F0 — réponse à l'audit de `f852c453…`

**Statut : `F0 INCOMPLET`.** Suite dans [`RAPPORT_PASSE2.md`](RAPPORT_PASSE2.md) —
banc multires anatomique et préflight câblé.

**Statut : `F0 INCOMPLET`.** Le raccord tête–corps a été mesuré pour la première
fois, et il **ne satisfait pas les seuils du cahier**. F1 ne commence pas.

Base auditée : `f852c453bee9950d419037baf661fd5f0d707b2f`.
Contrôles §1 avant intervention : arbre propre, `HEAD` exact, branche
`face/chat-3-caucasian-v1`, manifeste 40/40 OK. Blender 5.1.2.

---

## 1. Ce que l'audit avait raison de refuser

Trois reproches se sont vérifiés **chiffres en main** :

| reproche | vérifié |
| --- | --- |
| « raccord corps non démontré » | **fondé.** Les deux assets ne se recouvrent même pas : recouvrement des boîtes en X = **0,000 m**. Ma phrase « la position monde inchangée préserve la compatibilité » ne mesurait rien. |
| « nombre de sondes compté à la main » | **fondé.** `grep -c "exige("` rend **19** et **5**, j'avais publié 15 et 4. Remplacé par un registre qui produit le compte. |
| « 0,073 % de blancs brûlés » | **faux dans mes Markdown.** Le JSON dit **0,084 % sur `neutre_profil_R`**. Corrigé partout. |

---

## 2. P0.1 — préflight cryptographique · **RÉSOLU**

`tests/asset-preflight.py` + `preflight()` dans `tests/atlas_commun.py`.

Ordre imposé : résoudre → exister → taille → SHA-256 **en flux** → comparer →
alors seulement `bpy.data.libraries.load`. Échec ⇒ code **2**, aucun `.blend` ni
mesure produits.

**5 auto-tests sur 5**, sur des fichiers fabriqués, sans exposer le vrai asset :

| id | configuration connue | attendu | obtenu |
| --- | --- | --- | --- |
| `preflight.fichier_conforme` | 252 octets, SHA connu | OK | OK |
| `preflight.meme_taille_contenu_modifie` | **même taille**, un octet retourné | ECHEC / SHA faux | idem |
| `preflight.taille_attendue_fausse` | bon contenu, taille attendue +1 | ECHEC / taille fausse | idem |
| `preflight.sha_flux_sans_taille_absente` | lecture en flux | `65537d4599059931` | idem |
| `preflight.fichier_absent` | chemin inexistant | ECHEC | ECHEC |

Asset réel : `49 420 489` octets, SHA `3c121505…c75c137`, **status OK**.
Appelé par `tests/f0-raccord-corps.py` via `exiger_asset()`.
→ [`preflight-asset.json`](preflight-asset.json)

## 3. P0.3 — verrou complet · **RÉSOLU**

### Cinq empreintes séparées

| empreinte | valeur |
| --- | --- |
| `signature_topologie` | `a3476f7a09faad77…` |
| `signature_neutre_basis` | `235b15cd0f8aca4b…` |
| `signature_uv` | `31694f627545bcff…` |
| `signature_configuration` | `0e7ca6d3db8e2453…` |
| `signature_inventaire_scene` | `aa192618c04d4ce9…` |

`signature_uv` porte les **coordonnées `u,v` dans l'ordre exact des loops**
(20 500 loops), plus le nom et l'index actif de chaque couche. `bool(uv_layers)`
a disparu du code.

`signature_configuration` refuse toute dérive : shape keys, armatures objet et
modificateur, liste **et ordre** des modificateurs, les treize champs du
`Multires` disponibles en 5.1.2, contraintes, drivers, animation, vertex groups,
matériaux, parent, et les **neuf drapeaux de verrouillage** par objet.

### Verrouillage Blender des transformations

`rig/sceller-face-base.py` pose `lock_location`, `lock_rotation`,
`lock_rotation_w` et `lock_scale` sur les cinq objets — **45 drapeaux
verrouillés**, publiés dans `tests/verrou-topologie.json`. Le scellement
**prouve** qu'il n'a rien déplacé : écart sommet à sommet et matrice monde
**0,000000000 mm**. Il a aussi vérifié que le parentage des yeux
(`iris` → `sclera` → tête) survit à la purge. **11 sondes sur 11.**

Aucun objet n'a eu à être retiré : la source ne contenait déjà que les cinq
meshes.

### Neuf contre-épreuves · **9 sur 9 refusées**

Le maître est rouvert avant chaque mutation et **jamais sauvegardé** — SHA-256
identique avant et après (vérifié dans le JSON).

| mutation | empreinte attendue | refusé | empreintes fautives |
| --- | --- | :---: | --- |
| sommet Basis +1 mm | `neutre_basis` | oui | `neutre_basis` |
| un sommet ajouté | `topologie` | oui | `configuration`, `neutre_basis`, `topologie` |
| objet déplacé de 1 mm | `neutre_basis` | oui | `neutre_basis` |
| coordonnée UV +0,01 | `uv` | oui | `uv` |
| shape key `TEST_INTERDITE` | `configuration` | oui | `configuration` |
| objet Armature ajouté | `inventaire_scene` | oui | `inventaire_scene` |
| `Multires.levels` → 0 | `configuration` | oui | `configuration` |
| un axe déverrouillé | `configuration` | oui | `configuration` |
| mesh étranger ajouté | `inventaire_scene` | oui | les cinq |

→ [`verrou-negatif.json`](verrou-negatif.json)

## 4. P0.2 — raccord tête–corps · **MESURÉ, SEUILS NON SATISFAITS**

### Le solveur d'abord, la mesure ensuite

Similarité d'Umeyama, **5 auto-tests sur 5** : une similarité exacte
(rotation 37°, échelle 1,37, translation connue) est retrouvée à `1,37` et
résidu `0,0` ; un point déplacé de 50 mm laisse un résidu de `0,0379` — la sonde
répond bien à son entrée ; le déterminant reste `+1` sur une cible réfléchie.

### Une sonde fausse, prise ici et non publiée

Première version : la détection du nez et du menton balayait **tout** le
maillage. Appliquée à `GEO-body_male_realistic`, qui est un **corps entier**,
elle a rendu les orteils et les pieds — et le solveur a conclu à une échelle de
**8,06** alors que les distances interoculaires ne diffèrent que de 2 %.

Corrigé : recherche bornée à une boule de 140 mm autour du plan des yeux, et
**chaque repère soumis à des bornes anatomiques** publiées. Hors bornes, aucun
chiffre n'est publié et le script sort en 2.

| borne | tête | corps |
| --- | ---: | ---: |
| yeux antérieurs au centre | +16,33 mm | +18,23 mm |
| saillie du nez (20–90 mm) | **56,85** | **54,36** |
| chute du menton (50–140 mm) | **119,21** | **124,88** |
| interoculaire (50–80 mm) | **64,578** | **65,855** |

### Le résultat

| mesure | valeur | seuil | verdict |
| --- | ---: | ---: | :---: |
| facteur d'échelle | **1,033446** | — | — |
| écart à 1 | **3,3446 %** | ≤ 1,0 % | **échec** |
| résidu œil L | 2,584 mm | ≤ 2,00 | échec |
| résidu œil R | **4,069 mm** | ≤ 2,00 | **échec** |
| résidu nez | 3,437 mm | ≤ 2,00 | échec |
| résidu menton | 2,339 mm | ≤ 2,00 | échec |
| recouvrement des boîtes, sans transformation | **X = 0,000 m** | — | les deux assets ne se superposent pas |

### La cause, cherchée et nommée

Ce n'est **ni** un mauvais objet **ni** un mauvais repère — les quatre bornes
anatomiques passent des deux côtés. C'est une **morphologie différente** : le
paquet contient deux sculpts de tête distincts. Le bootstrap l'avait déjà
mesuré sans en tirer la conséquence — la tête du corps porte **3 612 sommets
au-dessus du cou** contre 3 242 pour la tête d'animation. Ce ne sont pas les
mêmes têtes, et 3,3 % d'échelle avec 2 à 4 mm de résidu est exactement l'écart
attendu entre deux sculpts voisins mais non identiques.

### Décision d'intégration

La **greffe par couture fermée est exclue par la mesure**, et non par
préférence : le maillage de la tête a **0 bord ouvert** — il n'existe aucune
boucle de couture à souder — et les nombres de sommets diffèrent, donc la
correspondance ne peut pas être bijective. Le cahier interdit alors de forcer
une soudure.

Restent le remplacement complet et le transfert de déformations. **Aucune des
deux n'est validée dans cette passe** : le remplacement exige la carte exacte
des faces du corps à exclure et la preuve qu'il ne reste ni double surface, ni
trou, ni intersection ; le transfert exige un banc de déformation qui n'existe
pas encore. Les mesures ne les départagent pas aujourd'hui, et je refuse
d'écrire une décision que rien ne porte.

**Conséquence : `F0 INCOMPLET`,** conformément au §7.6.

→ [`raccord-corps.json`](raccord-corps.json)

## 5. P0.4 et P0.5 — **NON TRAITÉS**

Le banc multires anatomique (clignement, fermeture labiale, mandibule sur cinq
ouvertures, ordre des modificateurs, mémoire et temps sur 20 évaluations, export
glTF, stratégie de résolution) et les empreintes UV avant/après/export **n'ont
pas été faits** dans cette passe. Le banc V1 reste dans l'historique ; il prouve
la mécanique d'évaluation, pas la qualité anatomique. Ce reproche de l'audit
**reste entier**.

## 6. P1 et P2 — état

| point | état |
| --- | --- |
| registre automatique des sondes | **fait** — `Registre` dans `tests/atlas_commun.py`, chaque sonde porte `id`, description, configuration connue, attendu, obtenu, statut ; le compte est calculé, plus saisi |
| préflight appelé par les scripts | **fait** pour `f0-raccord-corps.py` ; **reste à câbler** dans `f0-audit-topologie.py` et le futur `f0-multires-v2.py` |
| contre-épreuve publique du verrou | **fait**, 9 mutations |
| histogrammes : 0,084 % et non 0,073 % | **corrigé** dans les trois documents concernés |
| coupe sagittale publiée | **non fait** dans cette passe |
| hygiène des chemins du `.blend` | **non fait** |
| vues bilatérales à éclairage miroir | **non fait** |
| wireframes lèvres/paupières/narines/cou | **non fait** |

## 7. Source finale

`source/FACE_BASE_LOCKED.blend` — **5 meshes, 5 134 sommets, 5 122 faces,
20 500 loops.** Zéro shape key, zéro armature, zéro driver, zéro contrainte,
zéro animation, zéro dent, zéro langue. Un `Multires` non appliqué sur la tête
seule. Échelle 1, rotation nulle, **45 drapeaux verrouillés**. `UVMap` sur les
cinq objets.

## 8. Ce qui manque pour lever `F0 INCOMPLET`

1. **trancher le raccord corps** entre remplacement complet et transfert de
   déformations, avec les mesures et les preuves visuelles que le §7.4 et le
   §7.5 exigent ;
2. **le banc multires anatomique** (P0.4) et les empreintes UV d'export (P0.5) ;
3. coupe sagittale, hygiène des chemins, vues bilatérales, wireframes.
