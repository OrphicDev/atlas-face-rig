Suis strictement ce tuto :

Atlas Face Rig — vrai tutoriel Blender pas à pas

> Opérateur principal : Claude Code  
> Blender : 5.1.2  
> Départ : [branche `face/chat-3-caucasian-v1`](https://github.com/OrphicDev/atlas-face-rig/tree/face/chat-3-caucasian-v1),
> [commit `c0885ae8…`](https://github.com/OrphicDev/atlas-face-rig/commit/c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0)  
> Historique audité : [comparaison `f852c453…c0885ae8`](https://github.com/OrphicDev/atlas-face-rig/compare/f852c453bee9950d419037baf661fd5f0d707b2f...c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0)  
> But : construire le rig facial, le tester visuellement, puis produire un GLB
> réellement utilisable.

Ce document est un mode d’emploi. Il ne te demande pas seulement de « vérifier
la topologie » ou de « créer une shape key ». Il décrit l’action à exécuter,
l’endroit où l’exécuter, ce qui doit apparaître à l’écran et ce qu’il faut
corriger si le résultat n’est pas celui attendu.

Quand une action peut être faite dans l’interface et en Python, la manipulation
Blender est donnée d’abord. Le script vient ensuite pour rendre le résultat
reproductible dans le dépôt.

────────

Leçon 0 — préparer Blender et le dépôt

Étape 0.1 — repartir exactement du bon commit

Ouvre un terminal dans le dépôt, puis exécute une commande à la fois :

```bash
git status --short
git branch --show-current
git rev-parse HEAD
```

Tu dois lire :

```text
face/chat-3-caucasian-v1
c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0
```

Si git status --short affiche des fichiers, ne les supprime pas. Copie la
liste dans le compte rendu et travaille uniquement dans les nouveaux fichiers
de phase décrits ci-dessous, sans toucher aux changements existants. Ne change
pas de branche sans instruction du responsable du dépôt.

Reste sur la branche fournie. Si tu n’y es pas, bascule dessus :

```bash
git switch face/chat-3-caucasian-v1
mkdir -p work reports/tutorial renders/tutorial exports
```

Résultat attendu : git branch --show-current affiche
face/chat-3-caucasian-v1.

Ne crée une autre branche que si le responsable du dépôt le demande. Si la
branche contient déjà des changements non commités, ne les écrase pas et ne
les mets pas de côté automatiquement : note-les, puis demande quelle copie de
travail utiliser.

Étape 0.2 — vérifier la version de Blender

Dans le terminal :

```bash
blender --version
```

La première ligne doit commencer par Blender 5.1.2.

Si le terminal répond command not found :

1. localise l’exécutable Blender ;
2. utilise son chemin absolu pour les commandes du tutoriel ;
3. n’installe pas une autre version au hasard ;
4. écris ce chemin dans work/blender-path.txt.

Exemple macOS :

```bash
/Applications/Blender.app/Contents/MacOS/Blender --version
```

Étape 0.3 — ouvrir le fichier sans modifier le master

1. Lance Blender 5.1.2.
2. Dans la barre du haut, clique File → Open.
3. Ouvre source/FACE_BASE_LOCKED.blend.
4. Si Blender propose Load UI, laisse l’option activée pour cette première
inspection.
5. N’appuie sur aucun bouton Save.

Dans l’Outliner, en haut à droite, tu dois retrouver cinq meshes. Le mesh
principal du visage s’appelle :

```text
GEO-head_animation_realistic
```

Les objets d’yeux attendus sont :

```text
GEO-head_animation_realistic.sclera.L
GEO-head_animation_realistic.sclera.R
GEO-head_animation_realistic.iris.L
GEO-head_animation_realistic.iris.R
```

Si un nom manque, arrête-toi : tu n’as pas ouvert le fichier attendu.

Étape 0.4 — apprendre les quatre zones de Blender utilisées ici

Dans l’interface par défaut :

• la grande zone centrale est la 3D Viewport ;
• la liste en haut à droite est l’Outliner ;
• les onglets verticaux en bas à droite sont les Properties ;
• la bande horizontale du bas est la Timeline.

Raccourcis utilisés tout au long du tutoriel :

|Action                 |Raccourci          |
|-----------------------|-------------------|
|rechercher une commande|`F3`               |
|vue de face            |`Numpad 1`         |
|vue de profil droit    |`Numpad 3`         |
|vue opposée            |`Ctrl + Numpad 1/3`|
|cadrer la sélection    |`Numpad .`         |
|mode Objet/Édition     |`Tab`              |
|menu des modes         |`Ctrl + Tab`       |
|console Python         |`Shift + F4`       |
|éditeur de texte       |`Shift + F11`      |
|annuler                |`Ctrl + Z`         |
|sauvegarder sous       |`Ctrl + Shift + S` |

Si le clavier n’a pas de pavé numérique, clique Edit → Preferences → Input,
puis active Emulate Numpad.

Étape 0.5 — activer les outils utiles au diagnostic

1. Clique Edit → Preferences.
2. Ouvre Interface.
3. Active Developer Extras.
4. Ferme la fenêtre Preferences.
5. Dans la 3D Viewport, ouvre le menu Overlays — icône de deux cercles en
haut à droite.
6. Vérifie que Text Info, Relationship Lines et Outline Selected sont
activés.

Developer Extras permettra de faire un clic droit sur une propriété puis
Copy Python Command. C’est utile quand Claude doit reproduire en bpy une
action faite dans l’interface.

Étape 0.6 — fabriquer la première copie de travail

Le master reste ouvert uniquement pour contrôle. Crée maintenant une copie :

1. Clique File → Save As.
2. Navigue vers le dossier work/ du dépôt.
3. saisis FACE_F0_WORK.blend ;
4. vérifie que Compress est activé ;
5. clique Save As ;
6. confirme si Blender le demande.

Regarde le titre de la fenêtre. Il doit maintenant se terminer par :

```text
work/FACE_F0_WORK.blend
```

Si le titre affiche encore source/FACE_BASE_LOCKED.blend, ferme Blender sans
sauvegarder et recommence.

Étape 0.7 — créer une vue de diagnostic reproductible

1. Sélectionne GEO-head_animation_realistic dans l’Outliner.
2. Appuie sur Numpad . pour cadrer le visage.
3. Appuie sur Numpad 1.
4. Dans la 3D Viewport, ouvre View → Align View → Align Active Camera to View seulement si une caméra de preuve dédiée existe déjà.
5. Sinon, crée une caméra : Shift + A → Camera.
6. Renomme-la CAM_FACE_PROOF dans l’Outliner.
7. Avec la vue toujours cadrée, appuie sur Ctrl + Alt + Numpad 0 pour aligner
la caméra.
8. Dans Output Properties, règle Resolution X = 1024 et
Resolution Y = 1024.
9. Dans Render Properties, sélectionne le moteur déjà utilisé par les preuves
du dépôt ; ne change pas de moteur pour embellir le résultat.
10. Dans Color Management, conserve le transform et l’exposition du fichier.

Duplique cette caméra pour les vues de profil seulement après avoir sauvegardé
sa matrice dans un script. Les poses ne doivent jamais recadrer la caméra.

Étape 0.8 — effectuer un premier rendu témoin

1. Remets tous les objets en position neutre.
2. Appuie sur F12.
3. Quand le rendu apparaît, clique Image → Save As.
4. Enregistre :

```text
renders/tutorial/00_neutral_front.png
```

Ce rendu est le témoin visuel. À chaque chapitre, tu utiliseras le même cadrage,
la même lumière et la même exposition.

Étape 0.8 bis — reconnaître les trois défauts de départ

Avant de corriger quoi que ce soit, ouvre les trois preuves produites au commit
c0885ae8…. Elles montrent l’état à dépasser, pas le résultat final.

Clignement à 100 %

Clignement du checkpoint c0885 à 100 %

Observe la fente résiduelle entre les marges. La mesure actuelle est
2,3937 mm à gauche et 4,0046 mm à droite. La phase F0-B devra descendre à
0,20 mm ou moins sur la cage et sur le mesh évalué dense.

Fermeture des lèvres à 100 %

Fermeture labiale du checkpoint c0885 à 100 %

Observe la fente centrale et les commissures. La mesure actuelle est
0,9688 mm. F0-B devra obtenir 0,30 mm ou moins, sans croisement des lèvres.

Mâchoire à 32°

Prototype de mâchoire du checkpoint c0885 à 32°

Ne juge pas seulement l’angle du menton : regarde le pivot près des condyles,
la translation vers l’avant, le plancher buccal et le raccord joue–mâchoire.
F0-C reconstruira ce mouvement avant d’installer l’os permanent.

Étape 0.9 — créer le journal de séance

Crée reports/tutorial/JOURNAL.md avec :

```markdown
# Journal Atlas Face Rig

## Environnement
- Commit :
- Branche :
- Blender :
- OS :
- Fichier de travail :

## Étape en cours
- Leçon :
- Dernière action réussie :
- Résultat visible :
- Problème actuel :
- Capture :
```

À chaque blocage, remplis ces cinq lignes avant de chercher une solution. Une
recherche utile décrit une action précise et un symptôme visible, par exemple :

```text
Blender 5.1 Multires active shape key edits displacement grid
```

et non :

```text
face rig broken
```

────────

Comment suivre les leçons suivantes

Carte de progression

|Phase      |Ce que tu construis réellement                                   |Fichier qui autorise la suite           |
|-----------|-----------------------------------------------------------------|----------------------------------------|
|F0-A à F0-F|contacts, mâchoire prototype, transfert corps, pile et spike glTF|`source/FACE_F0_FOUNDATION_FINAL.blend` |
|F1         |armature permanente de mâchoire et regard                        |`source/ATLAS_FACE_F1.blend`            |
|F1.5       |topologie et UV définitivement signées                           |`source/FACE_TOPOLOGY_FINAL.blend`      |
|F2         |dents, gencives et langue                                        |`source/ATLAS_FACE_F2_ORAL.blend`       |
|F3         |blink, wide, squint et suivi des paupières                       |`source/ATLAS_FACE_F3_EYELIDS.blend`    |
|F4         |lèvres, sourire, pucker/funnel et correctives jaw                |`source/ATLAS_FACE_F4_MOUTH.blend`      |
|F5         |sourcils, front, joues et nez                                    |`source/ATLAS_FACE_F5_UPPER.blend`      |
|F6         |mapping FACS mesuré                                              |`source/ATLAS_FACE_F6_FACS.blend`       |
|F7         |correctives de combinaisons                                      |`source/ATLAS_FACE_F7_CORRECTIVES.blend`|
|F8         |contrôleurs, drivers et panneau d’animation                      |`source/ATLAS_FACE_F8_CONTROLS.blend`   |
|F9         |visèmes français et coarticulation                               |`source/ATLAS_FACE_F9_SPEECH.blend`     |
|F10        |intégration au corps et LOD                                      |`source/ATLAS_FACE_F10_BODY.blend`      |
|F11        |mesh dense, bake, GLB et round-trip                              |`runtime/ATLAS_FACE_RUNTIME.blend`      |
|F12        |recette humaine, preuves et release                              |`reports/f12/FINAL_QA.json`             |

Une ligne n’autorise la suivante qu’après réouverture du fichier et passage du
mini-test indiqué. Le tableau sert à se repérer ; il ne remplace aucune action.

Chaque leçon utilise ce rythme :

1. ouvrir le fichier produit par la leçon précédente ;
2. sauvegarder immédiatement sous le nouveau nom demandé ;
3. effectuer un seul geste Blender ;
4. vérifier le résultat dans au moins deux vues ;
5. exécuter le mini-test ;
6. corriger avant de continuer ;
7. sauvegarder ;
8. automatiser le geste en bpy ;
9. fermer/réouvrir pour prouver que le résultat persiste.

Les encadrés Arrête-toi ici si… sont de vrais points d’arrêt. Les listes de
validation arrivent après la manipulation, jamais à sa place.

────────

Partie I — F0 : construire une fondation mesurée

Destinataire : Claude Code, avec Blender 5.1.2 disponible en ligne de commande.

Ce chapitre part exactement du commit c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0 de la branche face/chat-3-caucasian-v1. Il ne suppose pas que F0 est terminée : elle ne l’est pas. Le but est d’obtenir une fondation mesurée, reproductible et honnête avant de créer le premier rig permanent.

Le fichier source source/FACE_BASE_LOCKED.blend est une pièce à conviction. Tu peux l’ouvrir et le mesurer, mais tu ne l’enregistres jamais par-dessus. Toute expérience se fait dans experiments, toute sortie de production dans un nouveau fichier source, et tout résultat machine dans reports.

Repères et vérité de départ

Le maillage facial se nomme GEO-head_animation_realistic. Il contient 3 242 sommets et 3 234 faces au checkpoint c0885. La scène verrouillée contient cinq meshes, 5 134 sommets, 5 122 faces et 20 500 loops. Les quatre objets oculaires sont :

• GEO-head_animation_realistic.sclera.L
• GEO-head_animation_realistic.sclera.R
• GEO-head_animation_realistic.iris.L
• GEO-head_animation_realistic.iris.R

Le repère utilisé dans les mesures existantes est : X positif vers la gauche du personnage, Y négatif vers l’avant, Z positif vers le haut. Une unité Blender vaut un mètre ; multiplie donc une distance par 1 000 pour l’exprimer en millimètres.

Le SHA-256 attendu de source/FACE_BASE_LOCKED.blend est :

```
cc9e55a47b1496fa81ed42deee6ee3a6f498c309d5b86610e5cd2407831f2bd8
```

Les cinq empreintes attendues dans tests/verrou-topologie.json sont :

```
topologie      a3476f7a09faad775129abd5eb0b8bc66c39b32a2a252404b0935d5109f4fd45
Basis neutre   235b15cd0f8aca4be7c8ef6600bd9734ac5862905b3e9178a6551b5b82d81986
UV             31694f627545bcff9b61ead0b5851c4a8acd5539a0a3f6e1fa6924b08f973424
configuration  0e7ca6d3db8e2453a5d6d652a00a78725baf636b285b5606a3ba6a9a7601b7d5
inventaire     aa192618c04d4ce9244a8f4458fc227733cecb1be4153dce438d872adea0b00e
```

Au départ, les mesures qui doivent échouer sont :

```
blink L à 100 %    2,3937 mm, limite 0,20 mm
blink R à 100 %    4,0046 mm, limite 0,20 mm
lèvres à 100 %     0,9688 mm, limite 0,30 mm
raccord échelle    3,34463 %, limite 1 %
raccord résidu max 4,0694 mm, limite 2 mm
```

Le registre Multires V2 doit produire 21 PASS, 3 FAIL et 2 SKIP. Le registre de raccord doit produire 13 PASS et 2 FAIL. Le test d’hygiène publié produit 10 PASS et 1 FAIL, mais son protocole peut injecter lui-même le chemin absolu qu’il prétend détecter. Ne transforme jamais ces échecs attendus en succès en augmentant les seuils.

Chaque micro-étape ci-dessous comporte cinq rubriques. Action indique exactement quoi faire. Résultat visible indique ce que tu dois constater avant de continuer. Sauvegarde nomme l’artefact à écrire. Mini-test donne une vérification immédiate. Si ce n’est pas le cas donne la correction locale ; n’avance pas au chapitre suivant tant que cette correction n’est pas faite.

────────

F0-A — Reproduire c0885 et rendre le pipeline honnête

F0-A.1 — Ouvrir une reprise sans toucher à l’historique

Action

Dans un terminal placé à la racine du dépôt, exécute :

```
git status --short
git branch --show-current
git rev-parse HEAD
git merge-base --is-ancestor \
  f852c453bee9950d419037baf661fd5f0d707b2f \
  c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0
git diff --exit-code
git diff --cached --exit-code
mkdir -p reports/reprise/c0885ae
```

N’utilise ni git reset, ni git checkout sur un fichier modifié par quelqu’un d’autre. Si le dépôt est sale, note les chemins dans reports/reprise/c0885ae/ETAT_C0885AE.md et continue seulement si tes sorties peuvent être isolées.

Résultat visible attendu

Le terminal affiche face/chat-3-caucasian-v1 puis le SHA complet c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0. Les trois commandes de vérification Git terminent avec le code 0. Le dossier reports/reprise/c0885ae existe et les anciens JSON de reports/f0-correction ne changent pas.

Sauvegarde

Crée reports/reprise/c0885ae/ETAT_C0885AE.md. Écris-y le commit, la branche, la sortie de git status et la date UTC. Ce fichier est un nouveau rapport ; ne modifie pas reports/f0-correction.

Mini-test immédiat

Exécute :

```
test "$(git rev-parse HEAD)" = \
  "c0885ae8c535b02925a217b1fb6ad4d0bbdf67b0"
test -f source/FACE_BASE_LOCKED.blend
```

Si ce n’est pas le cas

Si HEAD diffère, arrête. Ne transpose pas les valeurs c0885 sur une autre révision. Si l’arbre contient des modifications, ne les efface pas : crée un worktree propre sur c0885 ou demande au responsable quelle copie employer.

F0-A.2 — Vérifier Blender et l’asset externe

Action

Dans le même terminal :

```
blender --version
test -n "$ATLAS_BASE_MESH"
test -f "$ATLAS_BASE_MESH"
shasum -a 256 "$ATLAS_BASE_MESH"
wc -c "$ATLAS_BASE_MESH"
```

Sur Linux sans shasum, remplace seulement cette commande par :

```
sha256sum "$ATLAS_BASE_MESH"
```

Résultat visible attendu

La première ligne annonce Blender 5.1.2. L’asset externe fait 49 420 489 octets et son SHA-256 vaut :

```
3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137
```

Sauvegarde

Écris reports/reprise/c0885ae/environnement.json avec au minimum : version Blender complète, système, chemin de dépôt relatif, taille et SHA de l’asset, commit Git et heure UTC. N’écris pas le chemin absolu de l’utilisateur dans un rapport destiné à être publié ; stocke une valeur expurgée pour le champ asset_path.

Mini-test immédiat

Fais lire le JSON par Python :

```
python3 -m json.tool \
  reports/reprise/c0885ae/environnement.json >/dev/null
```

Si ce n’est pas le cas

Si Blender n’est pas en 5.1.2, installe ou sélectionne le binaire correct avant de mesurer. Si l’asset externe diffère, ne lance pas le raccord ni l’extraction dentaire : documente le SHA réel et retrouve la version auditée.

F0-A.3 — Rejouer le verrou positif et ses mutations négatives

Action

Exécute les scripts existants, sans les modifier d’abord :

```
blender --background --factory-startup --python-exit-code 1 \
  --python tests/verrou-topologie.py -- \
  source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json

blender --background --factory-startup --python-exit-code 1 \
  --python tests/verrou-topologie-negatif.py -- \
  source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json \
  reports/reprise/c0885ae/verrou-negatif.json
```

Ouvre ensuite tests/verrou-topologie.json dans l’éditeur de Claude Code. Compare chaque valeur à la section Repères et vérité de départ, caractère par caractère.

Résultat visible attendu

Le verrou positif affiche un résultat OK et termine avec le code 0. Le test négatif refuse neuf mutations. Le SHA du blend et les cinq empreintes correspondent exactement au checkpoint.

Sauvegarde

Conserve reports/reprise/c0885ae/verrou-negatif.json. Dans commandes.json, qui sera assemblé plus tard, réserve déjà deux entrées contenant la commande exacte et le code observé.

Mini-test immédiat

Exécute immédiatement :

```
shasum -a 256 source/FACE_BASE_LOCKED.blend
git diff --exit-code -- source/FACE_BASE_LOCKED.blend \
  tests/verrou-topologie.json
```

Si ce n’est pas le cas

Si le SHA du blend a changé, arrête et restaure-le depuis une copie sûre du commit, sans écraser d’autres fichiers du worktree. Si une mutation négative passe, ne touche pas au maillage : corrige d’abord le test de verrou et ajoute le cas exact à son rapport.

F0-A.4 — Rejouer les trois registres en échec

Action

Exécute :

```
blender --background --factory-startup --python-exit-code 1 \
  --python tests/f0-multires-v2.py -- \
  source/FACE_BASE_LOCKED.blend \
  reports/reprise/c0885ae/multires-ab-v2.json

blender --background --factory-startup --python-exit-code 1 \
  --python tests/f0-raccord-corps.py -- \
  reports/reprise/c0885ae/raccord-corps.json

blender --background --factory-startup --python-exit-code 1 \
  --python tests/f0-hygiene-blend.py -- \
  source/FACE_BASE_LOCKED.blend \
  reports/reprise/c0885ae/hygiene-blend-raw.json
```

Ne déduis pas la réussite du code shell actuel : les deux premiers scripts peuvent produire un registre FAIL tout en laissant Blender sortir avec 0. Ouvre les trois JSON et lis les champs de statut.

Résultat visible attendu

Le JSON Multires contient 21 PASS, 3 FAIL, 2 SKIP et les trois gaps exacts. Le JSON de raccord contient 13 PASS, 2 FAIL, 3,34463 % et 4,0694 mm. Le JSON d’hygiène contient 10 PASS et 1 FAIL.

Sauvegarde

Garde les trois JSON sous reports/reprise/c0885ae. Ajoute dans ETAT_C0885AE.md un tableau court avec statut, mesure, seuil et chemin du JSON.

Mini-test immédiat

Utilise ce contrôle indépendant, en adaptant seulement les noms de clés si le schéma existant les nomme autrement :

```
python3 -m json.tool \
  reports/reprise/c0885ae/multires-ab-v2.json >/dev/null
python3 -m json.tool \
  reports/reprise/c0885ae/raccord-corps.json >/dev/null
python3 -m json.tool \
  reports/reprise/c0885ae/hygiene-blend-raw.json >/dev/null
```

Puis recherche visuellement les chaînes FAIL et SKIP :

```
rg -n '"(statut|status)".*"(FAIL|SKIP)"|FAIL|SKIP' \
  reports/reprise/c0885ae/*.json
```

Si ce n’est pas le cas

Si les valeurs numériques diffèrent de plus que l’arrondi d’affichage, vérifie d’abord Blender 5.1.2, le SHA du blend, le SHA de l’asset externe et les variables d’environnement. Ne commence aucune correction géométrique avant d’avoir expliqué l’écart.

F0-A.5 — Corriger les codes de sortie sans changer les seuils

Action

Ouvre tests/f0-multires-v2.py. À l’endroit final où le script appelle reg.conclure(), conserve la valeur retournée et quitte explicitement :

```
ok = reg.conclure()
print("RESULTAT_FINAL", "OK" if ok else "ECHEC")
sys.exit(0 if ok else 2)
```

Fais la même modification dans tests/f0-raccord-corps.py. Importe sys en tête du fichier si nécessaire. Ne modifie aucune constante de seuil.

Dans tests/f0-preuves-visuelles.py, remplace l’impression inconditionnelle PREUVES_OK par une validation : chaque image attendue doit exister, avoir une largeur et une hauteur positives, contenir plus d’une couleur, être associée à la caméra signée et avoir un côté L ou R conforme à son nom. Écris le résultat dans un JSON et termine par 0 si tout passe, 2 sinon.

Utilise apply_patch pour ces modifications. N’emploie pas de réécriture globale qui reformaterait tout le fichier.

Résultat visible attendu

Une relance du banc Multires et du raccord affiche encore les mêmes FAIL, mais le code shell devient 2. Une exception Python véritable produit le code configuré 1. Le texte du JSON et le code shell racontent enfin la même chose.

Sauvegarde

Sauvegarde les scripts modifiés. Crée experiments/f0-exit-code avec un script minimal PASS, un script qui appelle sys.exit(2) et un script qui lève RuntimeError ; conserve dans un petit README la commande et le code réellement observé sous Blender 5.1.2.

Mini-test immédiat

Relance une sortie dans un nouveau fichier et affiche le code :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/f0-multires-v2.py -- \
  source/FACE_BASE_LOCKED.blend \
  reports/reprise/c0885ae/multires-ab-v2-after-exit-fix.json
code=$?
test "$code" -eq 2
```

Si ce n’est pas le cas

Si le JSON contient FAIL mais le shell retourne 0, vérifie que sys.exit est exécuté dans le bloc principal et non dans une fonction jamais appelée. Si Blender convertit le code différemment sur la plateforme, garde le code brut, documente-le dans experiments/f0-exit-code et normalise-le dans le runner ; ne masque jamais une exception comme un échec métier attendu.

F0-A.6 — Construire le runner baseline/final

Action

Crée tests/baselines/c0885ae-expected.json. Mets-y les identifiants précis, pas seulement les nombres :

• les trois FAIL de contact ;
• les deux SKIP de mesure haute résolution ;
• les deux FAIL de raccord ;
• le FAIL d’hygiène brute.

Crée ensuite tests/run-f0-final.py. Il lance chaque commande avec subprocess, enregistre argv sous forme de liste, temps, code brut, stdout, stderr et chemins produits. Le mode baseline parse les JSON après exécution et accepte un code métier non nul uniquement si chaque identifiant correspond à c0885ae-expected.json. Le mode final refuse tout FAIL, tout code non nul et tout SKIP critique.

Ne lance jamais les scripts via shell=True. Passe une liste d’arguments afin que les espaces d’un chemin ne changent pas la commande.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/run-f0-final.py -- \
  --mode baseline \
  --expected tests/baselines/c0885ae-expected.json \
  --output reports/reprise/c0885ae
```

Résultat visible attendu

Le runner termine avec 0 parce que les échecs correspondent exactement au baseline, non parce qu’ils ont disparu. reports/reprise/c0885ae/commandes.json contient chaque code brut et chaque statut normalisé. La suppression volontaire d’un identifiant attendu dans une copie du baseline doit faire échouer le runner.

Sauvegarde

Sauvegarde tests/run-f0-final.py, tests/baselines/c0885ae-expected.json et reports/reprise/c0885ae/commandes.json.

Mini-test immédiat

Copie le baseline dans un temporaire, retire un identifiant, puis relance le runner contre cette copie. Le runner doit refuser. Supprime seulement le temporaire, pas le baseline versionné.

Si ce n’est pas le cas

Si le runner passe en comptant simplement les FAIL, remplace la comparaison de compte par une comparaison d’ensemble sur identifiant, suite, objet, côté, métrique et seuil. Si un nouveau FAIL apparaît, le baseline doit échouer même si le total reste identique.

F0-A.7 — Refaire proprement le test d’hygiène

Action

Le test actuel ouvre le fichier depuis un chemin contenant /Users/orphicagency puis enregistre une copie non compressée. Ce geste peut introduire la chaîne recherchée. Crée un protocole neutre dans tests/f0-hygiene-neutral.py :

1. copie les octets du blend publié dans un dossier temporaire dont le nom ne contient ni utilisateur ni atlas ;
2. place BLENDER_USER_CONFIG, BLENDER_USER_SCRIPTS et BLENDER_USER_DATAFILES dans trois autres dossiers temporaires ;
3. scanne la copie avant de l’ouvrir ;
4. ouvre cette copie avec Blender ;
5. enregistre une version non compressée dans le temporaire ;
6. scanne le fichier publié, la copie avant ouverture et la copie après sauvegarde ;
7. répète le protocole avec un blend minimal créé dans le même environnement.

Lance ce test depuis le runner, mais écris son résultat séparément du baseline historique.

Résultat visible attendu

Le rapport permet de dire à quel moment précis le chemin apparaît. Il ne conclut intrinsèque que si la chaîne est présente avant toute ouverture dans le protocole neutre ou si le témoin démontre le même comportement sans injection.

Sauvegarde

Écris reports/reprise/c0885ae/hygiene-blend-neutral.json. Conserve les chemins temporaires expurgés. Ne versionne pas les copies binaires temporaires.

Mini-test immédiat

Vérifie que le rapport contient trois scans distincts et un témoin :

```
python3 -m json.tool \
  reports/reprise/c0885ae/hygiene-blend-neutral.json >/dev/null
rg -n 'published|before_open|after_save|control' \
  reports/reprise/c0885ae/hygiene-blend-neutral.json
```

Si ce n’est pas le cas

Si le test ne sait pas distinguer avant et après ouverture, il n’est pas probant. Ajoute les étapes et les SHA de chaque copie. Si le chemin vient seulement du protocole, classe le FAIL historique comme artefact de test et corrige le test ; ne réécris pas le rapport historique.

Gate F0-A

F0-A est terminée uniquement si le verrou positif passe, les neuf mutations sont refusées, le preflight passe, les registres bruts reproduisent exactement 21/3/2, 13/2 et 10/1, le runner baseline compare les identifiants exacts, les codes shell ne cachent plus les FAIL, le protocole d’hygiène neutre est publié et le SHA du master n’a pas changé.

────────

F0-B — Fermer réellement paupières et lèvres

Cette phase ne crée aucune shape key permanente. Elle construit des deltas de prototype reproductibles sur la cage, les mesure sur la cage et sur la surface Multires évaluée, puis publie ces deltas pour F3 et F4.

F0-B.0 — Signer l’unique fichier d’auteur utilisé par toute la suite de F0

Action

Crée tools/write-f0-author-input.py. Exécuté par Blender, ce script reçoit --kind c0885_locked ou --kind retopo, refuse tout chemin absolu dans sa sortie, vérifie la présence de GEO-head_animation_realistic et des quatre meshes oculaires, puis écrit le chemin relatif du blend, son SHA-256, le SHA topologique de la tête, les comptes cage et la nature de la source dans reports/f0-final/author-input.json.

Au premier passage, la seule entrée autorisée est le verrou c0885 :

```
mkdir -p reports/f0-final
blender -b source/FACE_BASE_LOCKED.blend \
  --python tools/write-f0-author-input.py -- \
  --kind c0885_locked \
  --output reports/f0-final/author-input.json
```

Dans chaque nouveau terminal F0, résous ensuite la variable depuis ce JSON ; ne la retape jamais à la main :

```
FACE_AUTHOR_BLEND="$(python3 -c 'import json; print(json.load(open("reports/f0-final/author-input.json", encoding="utf-8"))["face_author_blend"])')"
export FACE_AUTHOR_BLEND
test -f "$FACE_AUTHOR_BLEND"
```

reports/f0-final/author-input.json est la seule autorité pour F0-B à F0-F. Si la gate F0-B impose une retopologie, le fichier est régénéré sur source/FACE_F0_AUTHOR_RETOPO.blend avec --kind retopo, puis toute la phase F0-B est rejouée depuis ce nouvel auteur.

Résultat visible attendu

La dernière commande ne produit aucune erreur. Le JSON contient face_author_blend, kind, blend_sha256, topology_sha256, vertices, edges et polygons. Au premier passage, face_author_blend vaut source/FACE_BASE_LOCKED.blend et blend_sha256 vaut le SHA c0885 verrouillé.

Sauvegarde

Sauvegarde tools/write-f0-author-input.py et reports/f0-final/author-input.json. Ne versionne jamais seulement une variable shell sans son JSON signé.

Mini-test immédiat

Crée tests/check-f0-author-input.py, puis lance :

```
blender -b "$FACE_AUTHOR_BLEND" \
  --python tests/check-f0-author-input.py -- \
  --contract reports/f0-final/author-input.json
```

Le test recalcule les deux SHA et tous les comptes, compare le chemin ouvert au chemin déclaré et termine avec le code 0. Modifie un caractère du SHA dans une copie temporaire : le test doit terminer non-zéro.

Si ce n’est pas le cas

Si le SHA ou les comptes diffèrent, arrête F0 : le JSON et le blend ne forment plus une paire. Régénère le JSON depuis le blend intentionnellement choisi ; ne modifie pas le SHA à la main. Si FACE_AUTHOR_BLEND est vide, relance exactement la commande de résolution depuis la racine du dépôt.

F0-B.1 — Créer un fichier de travail visuel

Action

Ouvre Blender 5.1.2 avec l’auteur signé :

```
blender "$FACE_AUTHOR_BLEND"
```

Dans Blender, choisis File > Save As. Saisis :

```
experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend
```

Active Save Copy, puis clique Save As. Si le dossier n’existe pas, crée-le d’abord dans le terminal :

```
mkdir -p experiments/f0-contacts \
  reports/f0-final/deformations \
  renders/f0-final/contacts \
  config
```

Dans l’Outliner, développe la collection du visage et clique GEO-head_animation_realistic. Vérifie que l’objet actif est bien le maillage de peau, pas une sclère. Appuie sur Pavé numérique / pour passer en Local View. N’enregistre jamais cette vue sur le fichier pointé par FACE_AUTHOR_BLEND.

Résultat visible attendu

Le titre de la fenêtre Blender contient FACE_F0_CONTACTS_WORK.blend. La tête seule est visible en Local View. Le compte cage affiché dans Object Data est exactement le champ vertices de reports/f0-final/author-input.json ; 3 242 n’est attendu que pour l’auteur c0885 non retopologisé.

Sauvegarde

Enregistre experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend.

Mini-test immédiat

Dans le terminal, pendant que Blender reste ouvert :

```
test -f experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend
test "$(shasum -a 256 source/FACE_BASE_LOCKED.blend | awk '{print $1}')" = \
  "cc9e55a47b1496fa81ed42deee6ee3a6f498c309d5b86610e5cd2407831f2bd8"
```

Si ce n’est pas le cas

Si le titre montre encore le nom du fichier d’auteur, fais immédiatement Save As vers le fichier de travail avant toute modification. Si le compte de sommets diffère du JSON signé, remets le Multires au niveau cage sans l’appliquer et vérifie que tu as sélectionné le bon objet.

F0-B.2 — Afficher les régions candidates sans deviner à l’œil

Action

Crée tools/f0-show-contact-candidates.py. Le script ouvre reports/f0/audit-topologie.json et réutilise les sélections déjà employées par tests/anatomie.py pour créer des vertex groups de diagnostic :

```
DBG_eye_margin.L
DBG_eye_margin.R
DBG_lip_margin
```

Il ne modifie aucune coordonnée. Il assigne en plus trois matériaux très visibles aux duplicatas de diagnostic : cyan pour les sommets candidats, jaune pour le reste du visage, rouge pour les points sélectionnés.

Lance le script sur le fichier de travail :

```
blender -b experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend \
  --python tools/f0-show-contact-candidates.py -- \
  --report reports/f0-final/contact-candidates.json
```

Rouvre le fichier de travail. Sélectionne GEO-head_animation_realistic dans l’Outliner, appuie sur Tab pour Edit Mode, puis 1 pour Vertex Select. Dans Object Data Properties > Vertex Groups, choisis DBG_eye_margin.L et clique Select. Active Viewport Overlays > Vertex Indices.

Résultat visible attendu

Les sommets candidats entourent exactement la fente palpébrale gauche ; ils ne sélectionnent ni la sclère, ni le sourcil, ni une boucle entière de l’orbite. Répète avec DBG_eye_margin.R et DBG_lip_margin. La bouche doit montrer les deux marges, supérieure et inférieure.

Sauvegarde

Sauvegarde reports/f0-final/contact-candidates.json et le fichier de travail. Ce JSON doit contenir le SHA topologique et les indices triés de chaque groupe.

Mini-test immédiat

Dans Blender, avec un groupe sélectionné, ouvre Scripting > Python Console et exécute :

```
obj = bpy.context.edit_object
len([v for v in obj.data.vertices if v.select])
```

Compare le résultat au compte publié dans contact-candidates.json.

Si ce n’est pas le cas

Si les groupes sont vides, le script a probablement lu un mauvais objet ou un mauvais schéma JSON : imprime le nom exact du mesh et refuse de poursuivre. Si un groupe déborde, ne corrige pas à la main silencieusement ; corrige la logique de sélection et ajoute au rapport les indices ajoutés ou retirés.

F0-B.3 — Enregistrer les canthus et commissures par indices

Action

Reste sur GEO-head_animation_realistic en Edit Mode et Vertex Select. Désélectionne tout avec Alt+A. Affiche la vue de face avec Pavé numérique 1, puis passe en vue orthographique avec Pavé numérique 5. Active X-Ray avec Alt+Z afin de distinguer les marges, mais désactive-le avant de cliquer un sommet pour éviter de sélectionner l’arrière.

Pour l’œil gauche, clique un seul sommet à l’extrémité médiale de la marge supérieure. Vérifie qu’un seul sommet est orange. Dans la Python Console, exécute :

```
[v.index for v in bpy.context.edit_object.data.vertices if v.select]
```

Note l’indice comme eye.L.medial.upper. Répète pour medial.lower, lateral.upper et lateral.lower. Fais la même chose pour l’œil droit puis pour les deux commissures de la bouche, haute et basse.

Crée config/landmarks-contact.json avec ces indices. Ajoute mesh, topology_sha, space = OBJECT_LOCAL et une note visuelle pour chaque landmark. N’emploie jamais min(X) ou max(X) pour remplacer cette saisie.

Résultat visible attendu

Chaque clic sélectionne un sommet situé sur la marge, pas sur une boucle voisine. À un vrai canthus déjà partagé, upper et lower peuvent avoir le même indice. À une extrémité encore ouverte, les deux indices sont distincts.

Sauvegarde

Sauvegarde config/landmarks-contact.json. Fais aussi trois captures de viewport par ouverture : indices visibles, médial annoté, latéral annoté, dans renders/f0-final/contacts/landmarks.

Mini-test immédiat

Crée tests/check-contact-landmarks.py. Pour chaque indice, il vérifie : indice valide, appartenance au groupe candidat, degré topologique non nul et côté cohérent avec le plan sagittal. Lance :

```
blender -b --factory-startup \
  --python tests/check-contact-landmarks.py -- \
  "$FACE_AUTHOR_BLEND" \
  config/landmarks-contact.json \
  reports/f0-final/contact-landmarks-check.json
```

Si ce n’est pas le cas

Si un landmark n’appartient pas au groupe candidat, retourne dans Blender et vérifie le clic. Si upper et lower sont identiques alors qu’un jour visible existe, tu as sélectionné un point voisin commun : zoome, passe en wireframe et recommence. Si plusieurs interprétations restent possibles, publie une capture et bloque la phase pour revue humaine.

F0-B.4 — Reconstruire les deux marges comme chemins topologiques

Action

Crée tests/anatomie_marges.py. Ne cherche pas les paires en arrondissant X. Pour chaque ouverture :

1. lis le groupe candidat et les quatre landmarks ;
2. construis le graphe induit par les arêtes du mesh dont les deux sommets appartiennent au groupe ;
3. retire temporairement les canthus partagés pour séparer les deux marges si le graphe forme un cycle ;
4. calcule le chemin simple supérieur et le chemin simple inférieur entre médial et latéral ;
5. refuse un sommet interne dont le degré dans son chemin n’est pas deux ;
6. oriente les deux chemins du médial vers le latéral ;
7. calcule la longueur cumulée puis le paramètre s de 0 à 1 ;
8. classe upper/lower avec l’axe vertical du repère facial neutre, pas avec le Z monde supposé.

Crée tests/test_anatomie_marges.py avec trois meshes synthétiques : rectangle, ellipse asymétrique et deux marges de cardinalités différentes. Mélange l’ordre des indices avant chaque appel.

Lance d’abord les tests hors Blender s’ils n’importent que mathutils, sinon via Blender :

```
blender -b --factory-startup \
  --python tests/test_anatomie_marges.py
```

Puis lance l’extraction réelle :

```
blender -b --factory-startup \
  --python tests/anatomie_marges.py -- \
  "$FACE_AUTHOR_BLEND" \
  config/landmarks-contact.json \
  reports/f0-final/correspondances-marges.json
```

Résultat visible attendu

Le rapport contient deux listes ordonnées par ouverture, toutes orientées médial vers latéral. Une visualisation numérote 0, 25, 50, 75 et 100 % sans croisement. Les marges peuvent avoir des nombres de sommets différents : les paires sont des points interpolés sur segments, pas des indices forcés un à un.

Sauvegarde

Sauvegarde tests/anatomie_marges.py, tests/test_anatomie_marges.py et reports/f0-final/correspondances-marges.json.

Mini-test immédiat

Le test doit vérifier automatiquement :

```
s[0] == 0
s[-1] == 1
s[i + 1] > s[i]
aucune arête partagée entre chemins hors canthus déclaré
mêmes résultats après permutation des indices candidats
```

Si ce n’est pas le cas

Si le graphe offre plus de deux chemins, n’utilise pas le plus court au hasard. Ajoute un landmark intermédiaire explicitement sélectionné dans Blender, versionne-le dans la configuration et relance. Si upper et lower se croisent, le repère facial ou l’orientation d’un chemin est faux.

F0-B.5 — Décider quels points terminaux sont réellement fixes

Action

Dans anatomie_marges.py, mesure la distance entre upper et lower à s = 0 et s = 1 sur le neutre. Compare-la au seuil de contact de l’ouverture : 0,20 mm pour un œil, 0,30 mm pour les lèvres.

Si la distance est inférieure ou égale au seuil et si les deux chemins partagent effectivement le même sommet ou la même position topologique, marque l’extrémité anchor_shared. Sinon marque-la must_close. Écris la décision, les indices et la distance dans correspondances-marges.json.

Dans Blender, charge une visualisation générée par tools/f0-display-contact-anchors.py : vert pour anchor_shared, magenta pour must_close.

Résultat visible attendu

Un vrai canthus commun apparaît en vert et reste immobile dans les prototypes. L’extrémité actuellement ouverte apparaît en magenta et devra rejoindre sa cible. Aucun terminal n’est figé uniquement parce qu’il est proche du minimum ou maximum X.

Sauvegarde

Sauvegarde la décision dans correspondances-marges.json et rends renders/f0-final/contacts/contact-anchors.png avec les indices annotés.

Mini-test immédiat

Déplace artificiellement de 1 mm une copie d’un terminal must_close dans un test synthétique : son statut doit rester must_close parce que le statut dépend de la géométrie neutre signée, pas de la pose courante.

Si ce n’est pas le cas

Si tout est marqué anchor_shared malgré les jours visibles, vérifie la conversion mètres vers millimètres. Si aucun point partagé n’est détecté, vérifie la connectivité réelle avant d’inventer deux indices différents.

F0-B.6 — Apparier les marges par longueur d’arc

Action

Pour chaque ouverture, choisis un nombre d’échantillons au moins égal au plus grand nombre de sommets des deux chemins, avec un minimum de 64 pour les mesures continues. Pour chaque s uniforme, trouve le segment qui l’encadre sur upper et lower et stocke :

```
upper_segment = [i0, i1]
upper_t
lower_segment = [j0, j1]
lower_t
```

Calcule les deux positions interpolées. Enregistre cette table dans correspondances-marges.json. Ne rééchantillonne pas indépendamment après déformation : la correspondance se définit au neutre.

Résultat visible attendu

Dans l’image annotée, chaque trait relie une marge à l’autre sans croisement et reste localement perpendiculaire à la fente. Les traits près des extrémités ne sautent pas vers une autre région.

Sauvegarde

Mets à jour correspondances-marges.json et rends une image par ouverture dans renders/f0-final/contacts/pairing.

Mini-test immédiat

Calcule le produit scalaire entre deux vecteurs de paire successifs. Une inversion brutale ou un segment croisé doit faire échouer le test. Vérifie aussi que les mêmes paires sont reconstruites après fermeture puis retour au neutre.

Si ce n’est pas le cas

Si les traits se croisent, les chemins n’ont pas la même orientation. Inverse l’un des chemins en te fondant sur les landmarks, pas sur une heuristique de distance. Si les traits s’évasent fortement, augmente les échantillons et vérifie la longueur cumulée.

F0-B.6 bis — Produire et verrouiller la carte miroir d’indices

Action

Sur GEO-head_animation_realistic, crée config/mirror-landmarks.json. Dans Blender, sélectionne successivement des paires homologues L/R faciles à reconnaître — canthi, commissures, ailes du nez, pommettes, oreilles, crâne et base du cou — puis relève leurs indices avec :

```
[v.index for v in bpy.context.edit_object.data.vertices if v.select]
```

Sélectionne aussi plusieurs sommets réellement situés sur la couture sagittale et enregistre-les dans midline_fixed. Le JSON contient le topology_sha256 de l’auteur signé, space = OBJECT_LOCAL, les paires L/R et les indices médians. Il doit être recréé si une retopologie change un seul indice.

Crée ensuite tools/build-mirror-map.py. Il reçoit le blend auteur et les landmarks, propage les paires sur la connectivité des arêtes et des faces, et n’utilise la distance à la position réfléchie que pour départager deux candidats topologiquement équivalents. Il refuse une carte partielle, non bijective, non involutive, une arête qui ne se transforme pas en arête ou une face dont l’homologue est absent. Lance :

```
blender -b "$FACE_AUTHOR_BLEND" --python-exit-code 1 \
  --python tools/build-mirror-map.py -- \
  --object GEO-head_animation_realistic \
  --landmarks config/mirror-landmarks.json \
  --output reports/f0-final/carte-miroir.json \
  --debug-blend experiments/f0-contacts/FACE_F0_MIRROR_MAP.blend
```

Le fichier de sortie contient au minimum mesh, author_blend_sha256, topology_sha256, sagittal_plane_object_local, mirror_indices, midline_fixed, seed_pairs, method et son propre semantic_sha256. Chaque élément mirror_indices[i] est l’indice homologue de i.

Résultat visible attendu

Dans FACE_F0_MIRROR_MAP.blend, le script crée uniquement un duplicata de diagnostic : chaque paire reçoit la même couleur, les sommets médians sont blancs et les paires L/R reliées ne traversent jamais une région sans rapport. La base asymétrique n’est pas symétrisée et aucun sommet de l’auteur n’est déplacé.

Sauvegarde

Sauvegarde config/mirror-landmarks.json, tools/build-mirror-map.py, reports/f0-final/carte-miroir.json et une capture renders/f0-final/contacts/mirror-map-check.png. La même commande est obligatoire dans la branche c0885 et dans la branche retopologisée.

Mini-test immédiat

Crée tests/check-mirror-map.py, puis lance :

```
blender -b "$FACE_AUTHOR_BLEND" --python-exit-code 1 \
  --python tests/check-mirror-map.py -- \
  --map reports/f0-final/carte-miroir.json \
  --report reports/f0-final/mirror-map-check.json
```

Le test vérifie la taille égale au nombre de sommets signé, la permutation de 0..n-1, map[map[i]] == i, les sommets médians fixes, toutes les paires de landmarks, la conservation arêtes/faces et les SHA. Inverse volontairement deux valeurs dans une copie temporaire : il doit échouer.

Si ce n’est pas le cas

Si la carte est bijective mais relie deux zones anatomiques différentes, ajoute des paires de graines identifiées visuellement et reconstruis-la ; n’édite pas seulement deux nombres dans la sortie. Si la propagation trouve deux connectivités incompatibles après retopologie, corrige la symétrie topologique du master retopo, régénère son empreinte et recommence F0-B depuis F0-B.0.

F0-B.7 — Construire la cible de contact des paupières

Action

Crée tests/anatomie_globe.py afin que le test numérique et le rendu utilisent exactement la même géométrie. Pour chaque sclère, construis un BVH à partir du mesh évalué. Ajuste une sphère seulement sur la partie postérieure sphérique, en excluant la calotte cornéenne ; conserve aussi le BVH réel pour la distance finale.

Pour chaque paire de paupière au neutre, prends comme cible initiale :

```
target = 0.25 * upper + 0.75 * lower
```

Cette cible fait parcourir environ 75 % du trajet à la paupière supérieure et 25 % à l’inférieure. Déplace chaque point sur un arc autour du centre ajusté, puis projette le résultat à l’extérieur du BVH de sclère avec l’épaisseur de sécurité signée mesurée sur le neutre. Un anchor_shared garde exactement sa position.

Ne remplace pas le BVH par centroïde plus rayon moyen : la cornée dépasse la sphère moyenne.

Résultat visible attendu

À 100 %, la marge supérieure glisse autour du globe et rencontre l’inférieure. Elle ne descend pas comme un rideau vertical, ne traverse pas la cornée et ne laisse pas de triangle ouvert au canthus externe.

Sauvegarde

Écris config/globe-fit.json avec un schéma stable : schema_version = 1, author_blend_sha256, space = WORLD, puis eyes.L et eyes.R. Chaque œil contient sclera_object, center_world_xyz (trois nombres), radius_mm, posterior_vertex_indices et fit_residual_mm. Sauvegarde tests/anatomie_globe.py et une image latérale montrant sphère ajustée, cornée réelle et trajectoire.

Mini-test immédiat

Le même appel depuis le script de mesure et le script de rendu doit retourner des centres identiques à 1e-9 unité Blender. Au checkpoint, la mesure fitted-sphere actuelle est proche de 11,7449 mm de rayon ; une valeur proche de 11,702 mm indique que tu as repris l’ancien audit au lieu du calcul courant.

Si ce n’est pas le cas

Si les paupières pénètrent la cornée, inspecte la distance au BVH réel et l’orientation de la normale. Si la trajectoire gonfle l’orbite, la portée cutanée est trop large, pas la cible de marge. Si les deux scripts donnent des centres différents, supprime leurs implémentations locales et importe anatomie_globe.py des deux côtés.

F0-B.8 — Construire la cible de contact des lèvres

Action

Pour chaque paire labiale, commence au milieu local :

```
midpoint = 0.5 * upper + 0.5 * lower
```

Calcule la tangente de la ligne labiale et une normale locale au visage. Redistribue le déplacement sur l’épaisseur de chaque lèvre afin que la marge atteigne midpoint sans aplatir toute la lèvre sur un plan Z constant. Aux commissures, anchor_shared reste fixe ; must_close rejoint une cible commune.

Affiche les dents si elles sont disponibles dans une copie de diagnostic, mais ne les importe pas encore dans le master F0. La fermeture ne doit pas pousser la lèvre à l’intérieur d’un futur volume dentaire plausible.

Résultat visible attendu

À 100 %, les lèvres se touchent sur toute leur longueur. Le vermillon garde un volume, la courbure de la bouche reste asymétrique comme le Basis et aucune commissure ne reste ouverte ou écrasée.

Sauvegarde

Écris la cible labiale et les paramètres locaux dans reports/f0-final/correspondances-marges.json. Rends face, profils L/R et coupe sagittale du prototype.

Mini-test immédiat

Mesure la distance non signée et la séparation signée de toutes les paires. La distance maximale doit être au plus 0,30 mm ; la séparation signée minimale doit rester au moins -0,05 mm et aucun segment upper-lower ne doit se croiser.

Si ce n’est pas le cas

Si le centre ferme mais pas la commissure, vérifie que celle-ci est must_close et que le falloff longitudinal a été supprimé. Si les lèvres se traversent avec une petite distance non signée, corrige la normale de contact et garde le gate signé.

F0-B.9 — Étendre le mouvement vers la peau sans dents de scie

Action

La marge reçoit un poids 1. Pour les boucles voisines, calcule une distance géodésique sur les arêtes depuis la marge, puis :

```
q = clamp(distance / portée, 0, 1)
poids = 1 - q*q*(3 - 2*q)
```

Calibre la portée paupière pour couvrir les quatre boucles c0885 sans entraîner l’orbite entière. Calibre la portée lèvres pour couvrir les cinq boucles c0885 sans déplacer le nez ni le menton. Si une retopologie a été décidée, mesure les boucles sur le nouveau FACE_AUTHOR_BLEND avec anatomie_marges.py au lieu de conserver ces nombres historiques ; le contrat F0-F signera ensuite ces mesures.

N’utilise plus la distance au sommet de bord le plus proche. Si tu as besoin d’une solution intermédiaire, mesure la distance au segment le plus proche de la polyligne ; la solution de production reste géodésique.

Résultat visible attendu

Le wireframe se déforme en bandes continues. Aucun motif en cellules de Voronoï ni dentelure ne suit les sommets de marge. La peau éloignée ne bouge pas.

Sauvegarde

Sauvegarde config/contact-falloff.json avec portée en millimètres, courbe, groupes graines et SHA topologique. Rends une heatmap du poids et une image wireframe à 50 % et 100 %.

Mini-test immédiat

Sur chaque arête de la zone de falloff, calcule la différence absolue de poids. Signale les 20 plus fortes. Affiche-les en rouge dans Blender ; aucune discontinuité ne doit correspondre au changement de sommet le plus proche.

Si ce n’est pas le cas

Si l’orbite entière bouge, réduis la portée, mais ne remets pas un falloff le long de la fente. Si le contour reste dentelé, vérifie que la distance est géodésique ou segmentaire continue et que les poids sont calculés au neutre.

F0-B.10 — Générer les deltas de prototype sans shape key permanente

Action

Crée rig/build-f0-contact-deltas.py. Il ouvre le master en lecture, vérifie les cinq empreintes, copie les coordonnées Basis en mémoire, génère les poses blink_L, blink_R et mouth_close à t = 1, puis écrit pour chaque sommet déplacé :

```
index
delta_object_local_xyz
```

Trie les indices. Ajoute mesh, unité, repère, SHA topologique, SHA du tableau et paramètres de construction. Le script peut créer des objets DBG temporaires dans experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend, mais il ne crée aucune shape key dans le master.

Lance :

```
blender -b --factory-startup \
  --python rig/build-f0-contact-deltas.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --landmarks config/landmarks-contact.json \
  --pairs reports/f0-final/correspondances-marges.json \
  --falloff config/contact-falloff.json \
  --output-dir reports/f0-final/deformations \
  --debug-blend experiments/f0-contacts/FACE_F0_CONTACTS_DEBUG.blend
```

Résultat visible attendu

Le debug blend contient le head neutre et trois duplicatas clairement nommés DBG_blink_L_100, DBG_blink_R_100 et DBG_mouth_close_100. Le master reste sans shape key. Les trois duplicatas se ferment visiblement.

Sauvegarde

Sauvegarde :

```
reports/f0-final/deformations/blink_L.cage-delta.json
reports/f0-final/deformations/blink_R.cage-delta.json
reports/f0-final/deformations/mouth_close.cage-delta.json
experiments/f0-contacts/FACE_F0_CONTACTS_DEBUG.blend
```

Mini-test immédiat

Applique chaque delta à une copie du Basis, puis son opposé. Le delta maximal après aller-retour doit être inférieur ou égal à 0,01 mm. Vérifie aussi que le nombre de sommets du master et son SHA restent identiques.

Si ce n’est pas le cas

Si l’aller-retour dérive, tu as accumulé les deltas sur une pose précédente : reconstruis chaque pose depuis le Basis. Si le master contient une nouvelle key block, supprime-la seulement dans la copie de travail et corrige le builder pour qu’il n’enregistre jamais le master.

F0-B.11 — Mesurer cage et Multires sur onze valeurs

Action

Crée tests/f0-contacts-v3.py. Pour t allant de 0,0 à 1,0 par pas de 0,1, reconstruis la pose depuis Basis et mesure :

• distance maximale des paires par longueur d’arc ;
• séparation signée minimale ;
• croisement de paires ;
• distance signée peau-globe ;
• arêtes étirées et comprimées ;
• faces inversées ;
• nouvelles auto-intersections par rapport au neutre ;
• variation de volume ;
• retour neutre.

Pour la voie Multires, évalue réellement le depsgraph au niveau 1 et projette les paires cage vers la surface évaluée par correspondance barycentrique. N’accepte plus SKIP parce que les indices denses diffèrent.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/f0-contacts-v3.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --deltas reports/f0-final/deformations \
  --pairs reports/f0-final/correspondances-marges.json \
  --output reports/f0-final/contacts-v3.json
```

Résultat visible attendu

Les gaps diminuent de façon monotone. À t = 1 : chaque œil est à 0,20 mm ou moins, les lèvres à 0,30 mm ou moins, signed_gap_min reste au moins -0,05 mm, et la voie dense raconte le même geste que la cage.

Sauvegarde

Sauvegarde reports/f0-final/contacts-v3.json et la correspondance cage-vers-dense utilisée par le test avec son SHA.

Mini-test immédiat

Relance deux fois. Les JSON, après exclusion explicite des horodatages et temps, doivent avoir le même SHA. Vérifie que la pose t = 0 est identique au Basis à 0,01 mm.

Si ce n’est pas le cas

Si la cage passe et le dense échoue, corrige la projection cage-vers-Multires ; ne baisse pas le niveau et ne transforme pas le dense en SKIP. Si le gap n’est pas monotone, inspecte la trajectoire du pire s annoté.

F0-B.12 — Fixer les déformations extrêmes

Action

Le checkpoint contient des rapports d’arêtes allant jusqu’à 0,1185 fois et 4,8428 fois sur le blink, et 0,3927 à 1,6003 sur les lèvres. Crée une heatmap des vingt arêtes les plus comprimées et étirées. Dans Blender, ouvre FACE_F0_CONTACTS_DEBUG.blend, sélectionne l’objet de pose, passe en Edit Mode et localise chaque arête par ses deux indices.

Corrige le falloff, la trajectoire ou la cible. Une whitelist n’est permise que pour un pli anatomique volontaire identifié avant la relance. Écris chaque exception dans config/deformation-edge-whitelist.json avec arête, zone, pose, minimum, maximum et justification.

Résultat visible attendu

Hors whitelist, chaque ratio reste entre 0,50 et 2,00 ; le p95 global reste entre 0,80 et 1,25. Dans une whitelist justifiée, le ratio reste entre 0,25 et 3,00. Aucune face n’est inversée.

Sauvegarde

Sauvegarde config/deformation-edge-whitelist.json, la heatmap et le registre V3 mis à jour.

Mini-test immédiat

Retire temporairement une entrée de whitelist dans une copie du fichier et vérifie que le test échoue sur l’arête correspondante. Le fichier versionné reste intact.

Si ce n’est pas le cas

Si une arête demande encore 0,1185 ou 4,8428, elle ne peut pas être blanchie : corrige la géométrie du déplacement. Si plusieurs arêtes voisines échouent, ajuste la distribution sur les boucles, pas chaque sommet à la main.

F0-B.13 — Rendre des preuves comparables

Action

Dans tools/f0-render-contacts.py, ouvre le neutre, calcule une seule fois la caméra, le crop, l’exposition et les lumières, puis signe leurs matrices. Ne recalcule pas la bounding box après déformation.

Rends chaque pose avec la même caméra :

```
blink_L_000.png
blink_L_050.png
blink_L_100.png
blink_R_000.png
blink_R_050.png
blink_R_100.png
blink_L_100_wire.png
blink_R_100_wire.png
lips_000.png
lips_050.png
lips_100.png
lips_100_wire.png
lips_100_gap_annotated.png
```

Ajoute les cartes de distance signée et une vidéo 0 vers 1 vers 0.

Résultat visible attendu

Le visage ne change pas de taille dans le cadre entre 000 et 100. Les deux côtés sont présents. Les canthus et commissures sont lisibles, les wireframes ne sont pas dentelés et aucune sclère n’est visible à travers une paupière fermée.

Sauvegarde

Sauvegarde les images sous renders/f0-final/contacts et reports/f0-final/contact-render-settings.json avec matrices, résolution, moteur, exposition et SHA des deltas.

Mini-test immédiat

tests/f0-preuves-visuelles.py doit confirmer : fichiers présents, dimensions identiques, caméra identique, images non vides, côtés conformes et annotations présentes. Il termine par 0 seulement si tout passe.

Si ce n’est pas le cas

Si le visage bouge dans le cadre, la caméra ou le crop est recalculé après pose : utilise les matrices signées du neutre. Si l’image est valide techniquement mais ne montre pas la zone, le test doit aussi vérifier la projection des landmarks dans le cadre.

Gate F0-B

F0-B est terminée seulement si les deux yeux sont à 0,20 mm ou moins, les lèvres à 0,30 mm ou moins, signed_gap_min est au moins -0,05 mm, aucun croisement ni nouvelle intersection n’existe, le gap est monotone sur onze valeurs, le retour neutre est à 0,01 mm, les arêtes respectent leurs bornes, cage et Multires sont réellement mesurés, les caméras sont fixes et tous les scripts terminent avec le code attendu.

Si ces conditions restent impossibles après vérification des chemins, des cibles, du BVH et du falloff, décide une retopologie locale maintenant. Crée source/FACE_F0_AUTHOR_RETOPO.blend, refais UV et contrôles anatomiques, puis signe-le avant toute autre commande :

```
blender -b source/FACE_F0_AUTHOR_RETOPO.blend \
  --python tools/write-f0-author-input.py -- \
  --kind retopo \
  --output reports/f0-final/author-input.json
FACE_AUTHOR_BLEND="$(python3 -c 'import json; print(json.load(open("reports/f0-final/author-input.json", encoding="utf-8"))["face_author_blend"])')"
export FACE_AUTHOR_BLEND
```

Recommence ensuite F0-B depuis F0-B.1 : landmarks, empreintes, correspondances, carte miroir, globe-fit et deltas doivent tous être reconstruits depuis ce même FACE_AUTHOR_BLEND. Dans cette branche, 3 242 sommets devient uniquement le compte historique c0885.

────────

F0-C — Construire une mâchoire qui ouvre réellement

Le rendu c0885 annoncé à 32 degrés reste presque fermé. Le prototype actuel pondère surtout selon Z et le test ne prouve que le retour à zéro à 0 degré. Dans cette phase, tu construis un masque mandibulaire anatomique et une trajectoire mesurée. Le rig créé ici est temporaire ; le fichier F0 final restera sans armature permanente.

F0-C.1 — Créer une expérience de mâchoire isolée

Action

Crée les dossiers :

```
mkdir -p experiments/f0-jaw \
  renders/f0-final/jaw \
  reports/f0-final/deformations \
  config
```

Résous de nouveau l’auteur si tu as ouvert un nouveau terminal, puis ouvre exactement ce blend dans Blender 5.1.2 :

```
FACE_AUTHOR_BLEND="$(python3 -c 'import json; print(json.load(open("reports/f0-final/author-input.json", encoding="utf-8"))["face_author_blend"])')"
export FACE_AUTHOR_BLEND
blender "$FACE_AUTHOR_BLEND"
```

Fais File > Save As > Save Copy vers :

```
experiments/f0-jaw/FACE_F0_JAW_WORK.blend
```

Dans l’Outliner, sélectionne GEO-head_animation_realistic. Cache les quatre objets oculaires avec l’icône œil, sans les supprimer. Passe en Local View avec Pavé numérique /. Passe en vue de face, puis en profil gauche et droit afin de repérer lèvre inférieure, menton, bord mandibulaire, angle de mâchoire et zone des condyles.

Résultat visible attendu

Le titre de Blender indique FACE_F0_JAW_WORK.blend. La tête est visible sans les globes, et aucun objet n’a été déplacé. Le master publié garde son SHA.

Sauvegarde

Sauvegarde experiments/f0-jaw/FACE_F0_JAW_WORK.blend.

Mini-test immédiat

Dans la Python Console Blender :

```
obj = bpy.data.objects["GEO-head_animation_realistic"]
print(len(obj.data.vertices), len(obj.data.polygons))
print([k.name for k in obj.data.shape_keys.key_blocks] if obj.data.shape_keys else [])
```

Les deux comptes sont exactement vertices et polygons de reports/f0-final/author-input.json — respectivement 3 242 et 3 234 seulement si l’auteur est resté c0885 — puis une liste vide ou aucune donnée de shape keys permanentes.

Si ce n’est pas le cas

Si une shape key de l’expérience précédente est présente, repars du master et refais Save Copy. Si les yeux ont été supprimés au lieu d’être cachés, ferme sans enregistrer puis recommence.

F0-C.2 — Sélectionner les graines mandibulaires

Action

Dans Object Mode, sélectionne GEO-head_animation_realistic, puis Tab pour Edit Mode et 1 pour Vertex Select. Dans Object Data Properties > Vertex Groups, sélectionne le groupe de marge labiale construit en F0-B. Distingue la marge inférieure avec le chemin lower de correspondances-marges.json.

Crée quatre groupes de diagnostic :

```
DBG_jaw_seed_lower_lip
DBG_jaw_seed_chin
DBG_jaw_seed_mandible
DBG_jaw_exclude_upper
```

Pour DBG_jaw_seed_lower_lip, sélectionne exactement les sommets de la marge inférieure et clique Assign avec poids 1. Pour DBG_jaw_seed_chin, sélectionne une petite ligne médiane depuis le sillon labio-mentonnier vers la pointe du menton. Pour DBG_jaw_seed_mandible, sélectionne quelques sommets le long du corps mandibulaire gauche et droit, sans prendre le cou. Pour DBG_jaw_exclude_upper, sélectionne marge supérieure, philtrum, nez, front, crâne et nuque haute.

Affiche les indices et note tous les groupes dans config/jaw-mask.json avec le SHA topologique. Claude Code peut automatiser l’Assign à partir des indices choisis, mais il ne doit pas inventer les graines par simple seuil Z.

Résultat visible attendu

Les graines de lèvre forment seulement la marge inférieure. Les graines du menton et de la mandibule suivent le volume osseux. Le groupe d’exclusion contient clairement la lèvre supérieure et le crâne. Aucun sommet du bas du cou n’est une graine mandibulaire.

Sauvegarde

Sauvegarde config/jaw-mask.json et trois captures : face, profil L, profil R, avec indices et couleurs, dans renders/f0-final/jaw/seeds.

Mini-test immédiat

Crée tests/check-jaw-seeds.py. Il refuse toute intersection entre lower_lip et exclude_upper, vérifie que les deux côtés de la mandibule ont des graines et que chaque indice appartient au mesh signé.

Si ce n’est pas le cas

Si la lèvre supérieure apparaît dans le groupe inférieur, retourne à F0-B et vérifie l’orientation upper/lower. Si le masque n’a des graines que d’un côté, ajoute le côté manquant manuellement ; ne miroir pas les positions absolues d’un visage asymétrique.

F0-C.3 — Diffuser un masque par géodésique

Action

Crée rig/build-jaw-mask.py. Le script construit le graphe d’arêtes du visage et calcule une distance géodésique multisource depuis les graines mandibulaires. Il met :

• poids 1 sur la marge inférieure, le menton osseux et le bord mandibulaire ;
• poids 0 sur la marge supérieure, le philtrum, le nez, le crâne et les exclusions ;
• transition lisse dans les joues basses et le sillon labio-mentonnier ;
• poids 0 avant le bas du cou.

Utilise une interpolation smoothstep entre deux distances signées, puis réimpose exactement les contraintes 0 et 1. N’utilise pas uniquement coordonnée Z. Écris le tableau complet en float32 et son SHA.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python rig/build-jaw-mask.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --config config/jaw-mask.json \
  --output reports/f0-final/deformations/jaw-mask.npy \
  --report reports/f0-final/deformations/jaw-mask.json \
  --debug-blend experiments/f0-jaw/FACE_F0_JAW_MASK.blend
```

Résultat visible attendu

Dans FACE_F0_JAW_MASK.blend, la heatmap va du rouge poids 1 sur mandibule et menton au bleu poids 0 sur crâne et cou. La transition est lisse sur les joues. La lèvre inférieure est rouge ; la supérieure et le philtrum sont bleus.

Sauvegarde

Sauvegarde le NPY, son rapport JSON, la configuration et les images jaw-mask-front.png, jaw-mask-profile-L.png et jaw-mask-profile-R.png.

Mini-test immédiat

Le script vérifie :

```
0 <= poids <= 1
marge inférieure >= 0,95
marge supérieure == 0
crâne == 0
cou hors transition == 0
mêmes SHA après deux constructions
```

Si ce n’est pas le cas

Si la joue haute devient rouge, réduis la portée ou ajoute une barrière anatomique, mais ne reviens pas à un seuil Z. Si des îlots isolés apparaissent, vérifie les composantes du graphe et les graines.

F0-C.4 — Mesurer l’axe de charnière

Action

Dans Blender, garde GEO-head_animation_realistic visible et ouvre une coupe ou un profil. Les conduits auditifs audités se trouvent approximativement à plus ou moins 69 mm du plan sagittal et autour de Z = 0,740 m. Ces valeurs servent à trouver la région, pas à fixer aveuglément le pivot.

En Edit Mode, clique un landmark de condyle gauche et un droit, à proximité de l’articulation temporo-mandibulaire. Note leurs indices dans config/jaw-motion.json. Le script calcule leurs positions monde, leur milieu et l’axe normalisé droite-vers-gauche. Vérifie que cet axe est parallèle à X monde à moins de 0,1 degré ; sinon inspecte les landmarks et publie l’axe mesuré réel.

Crée un Empty temporaire : Object Mode, Shift+A > Empty > Plain Axes. Renomme-le TMP_jaw_pivot et place Location au milieu mesuré depuis le panneau N > Item.

Résultat visible attendu

L’Empty se trouve près des articulations, derrière la bouche et au-dessus du bord mandibulaire, jamais au menton. En vue de face, il est sur le plan sagittal. En profil, il se situe dans la région des condyles.

Sauvegarde

Enregistre un schéma sans ambiguïté dans config/jaw-motion.json : schema_version = 1, author_blend_sha256, space = WORLD, units = METERS, les deux condyle_landmarks, leurs positions_world_xyz, le milieu sous la clé obligatoire pivot_world_xyz et l’axe unitaire sous hinge_axis_world_xyz. Les paramètres de trajectoire ajoutés en F0-C.6 restent dans ce même objet JSON. Sauvegarde une capture de face et de profil avec l’Empty.

Mini-test immédiat

Le script calcule la distance de chaque landmark au plan sagittal et l’écart de hauteur gauche/droite. Il vérifie la symétrie mesurée et signale tout écart supérieur à la tolérance définie avant réglage.

Si ce n’est pas le cas

Si l’Empty est au menton, tu as confondu pivot et point suivi. Si les deux condyles sont du même côté, corrige les indices. Si l’axe n’est pas proche de X, ne force pas le bone roll avant d’avoir contrôlé les landmarks.

F0-C.5 — Créer une armature temporaire lisible

Action

Dans FACE_F0_JAW_WORK.blend, Object Mode, Shift+A > Armature > Single Bone. Renomme l’objet TMP_F0_JAW_RIG. Mets Location et Rotation à zéro et Scale à un. Dans Object Data Properties, active Viewport Display > In Front.

Passe en Edit Mode. Renomme l’os TMP_jaw_hinge. Place sa head au pivot central. Oriente sa tail vers le bas de façon que la rotation locale X soit l’axe d’ouverture ; ajuste Armature > Bone Roll > Recalculate Roll puis corrige numériquement. Ajoute un second os TMP_jaw_payload enfant de la charnière si tu veux séparer rotation et translation.

Ajoute un Armature modifier au duplicata de tête de l’expérience, jamais au master. Crée les groupes TMP_head et TMP_jaw. Assigne TMP_jaw avec jaw-mask.npy et TMP_head avec 1 moins TMP_jaw. Normalise.

Résultat visible attendu

En Pose Mode, une rotation positive test de 5 degrés autour de l’axe local prévu fait descendre le menton sans le déplacer latéralement. Crâne, lèvre supérieure et cou restent fixes.

Sauvegarde

Sauvegarde experiments/f0-jaw/FACE_F0_JAW_RIG.blend et renders/f0-final/jaw/bone-roll-axes.png.

Mini-test immédiat

Avec une pose de 5 degrés, mesure le déplacement X du point médian du menton. Il doit rester sous la tolérance latérale décidée. Vérifie que la rotation 0 reproduit le neutre à 0,01 mm.

Si ce n’est pas le cas

Si le menton part de côté, corrige le bone roll et l’axe avant les poids. Si la lèvre supérieure bouge, corrige le masque. Si le cou bouge, examine le groupe TMP_jaw et l’ordre des modificateurs.

F0-C.6 — Ajouter la translation condylienne mesurée

Action

Le contrôle open va de 0 à 1. La rotation vaut 32 degrés fois open. La translation commence après 0,35 :

```
t = clamp((open - 0.35) / 0.65, 0, 1)
s = t*t*(3 - 2*t)
translation = s * translation_max * direction
```

Dans le repère tête, la direction doit être antérieure et légèrement inférieure : globalement vers Y négatif et Z négatif, mais mesure-la sur Atlas. Dans Blender, crée des marqueurs de menton et de future incisive, teste plusieurs translations sur la copie, et choisis la plus petite trajectoire qui évite une simple rotation en charnière et garde une ouverture crédible.

Écris translation_max_mm et translation_direction_head_local dans config/jaw-motion.json. La direction doit être unitaire. N’utilise pas la constante historique avance_par_degre = 0.00030 sans preuve.

Résultat visible attendu

De 0 à environ 10 degrés, la rotation domine. À 20 et 32 degrés, le menton avance légèrement et descend davantage. Aucun glissement latéral n’apparaît.

Sauvegarde

Sauvegarde config/jaw-motion.json et renders/f0-final/jaw/jaw-trajectory.png avec les positions à 0, 5, 10, 20 et 32 degrés.

Mini-test immédiat

Vérifie numériquement :

```
norm(direction) = 1 à 1e-6
translation(0) = 0
translation continue à open = 0.35
déplacement antérieur monotone après 0.35
```

Si ce n’est pas le cas

Si le menton recule, l’axe de direction est inversé. Si la translation saute à 0,35, le clamp ou smoothstep est mal appliqué. Si la bouche paraît disloquée, réduis l’amplitude et inspecte la trajectoire en profil.

F0-C.7 — Construire le test direct sur matrice

Action

Crée rig/build-f0-jaw-prototype.py. Pour éviter que le test dépende d’un rig UI, le script applique directement à chaque sommet la transformation rigide de mâchoire pondérée par jaw-mask :

1. transforme le point du repère objet vers tête-local ;
2. applique rotation autour du pivot ;
3. applique translation de jaw-motion.json ;
4. mélange position neutre et position rigide selon le poids ;
5. transforme vers objet-local ;
6. reconstruit chaque angle depuis le Basis.

Le script crée seulement des duplicatas DBG_jaw_00, 05, 10, 20 et 32 dans le debug blend.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python rig/build-f0-jaw-prototype.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --mask reports/f0-final/deformations/jaw-mask.npy \
  --motion config/jaw-motion.json \
  --output experiments/f0-jaw/FACE_F0_JAW_PROTOTYPE.blend \
  --report reports/f0-final/jaw-prototype.json
```

Résultat visible attendu

Les cinq duplicatas montrent une ouverture croissante. À 32 degrés, la bouche est clairement ouverte ; la lèvre inférieure et le menton suivent la mandibule, tandis que philtrum et lèvre supérieure restent à leur place.

Sauvegarde

Sauvegarde le blend de prototype, le JSON et une planche de cinq angles.

Mini-test immédiat

Compare la position de chaque sommet de poids au moins 0,95 à la transformation rigide prédite. L’erreur doit rester à 0,25 mm ou moins. Le prototype UI et le prototype matriciel doivent correspondre au même seuil.

Si ce n’est pas le cas

Si les deux prototypes diffèrent, examine les repères et l’ordre rotation-translation. Ne corrige pas les poids pour compenser une matrice fausse.

F0-C.8 — Mesurer les cinq angles

Action

Crée tests/f0-jaw-motion.py. Pour 0, 5, 10, 20 et 32 degrés, mesure :

• gap vertical central des lèvres ;
• déplacement médian de la marge inférieure de poids au moins 0,95 ;
• déplacement de la marge supérieure et du philtrum ;
• déplacement du crâne et du bas du cou ;
• trajectoire du menton ;
• ratios d’arêtes ;
• volume ;
• nouvelles auto-intersections ;
• faces inversées.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/f0-jaw-motion.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --mask reports/f0-final/deformations/jaw-mask.npy \
  --motion config/jaw-motion.json \
  --output reports/f0-final/jaw-motion.json
```

Résultat visible attendu

À 0 degré, le delta maximal est 0,01 mm. Le gap augmente strictement après zéro. À 32 degrés, le gap central est au moins 8 mm et la marge inférieure fortement pondérée se déplace d’au moins 10 mm. Crâne, philtrum et composante rigide de la lèvre supérieure restent à 0,01 mm ; le cou hors transition reste à 0,5 mm.

Sauvegarde

Sauvegarde reports/f0-final/jaw-motion.json.

Mini-test immédiat

Le test doit échouer si tu remplaces temporairement la pose 32 par la pose 0. Cela prouve qu’il ne valide plus seulement 0 degré égal neutre.

Si ce n’est pas le cas

Si le gap n’augmente pas, vérifie d’abord le poids de la marge inférieure. Si le crâne bouge, corrige le masque. Si le mouvement est grand mais la bouche reste fermée, l’appariement des lèvres ou le point de mesure est faux.

F0-C.9 — Rendre une preuve à caméra fixe

Action

Dans tools/f0-render-jaw.py, calcule les caméras face et profils sur le neutre et réutilise leurs matrices. Rends les cinq faces, les profils L à 0/10/20/32, les profils R à 0/32, un wireframe 32, la heatmap du masque, la trajectoire et une vidéo 0 vers 32 vers 0.

Résultat visible attendu

Le cadre ne bouge pas. Le menton décrit une trajectoire continue, la bouche ouvre vraiment et le cou ne suit pas la mandibule. Les deux profils racontent le même mécanisme sans masquer l’asymétrie du visage.

Sauvegarde

Écris sous renders/f0-final/jaw et videos/f0-final/jaw-sweep.mp4.

Mini-test immédiat

Le script de preuves vérifie matrices de caméra identiques, présence des cinq angles, dimensions identiques et projection visible des landmarks de menton et pivot.

Si ce n’est pas le cas

Si la caméra suit le menton, retire tout recalcul de bounding box par pose. Si le wireframe montre une cassure dans la joue, corrige la transition du masque et rejoue toutes les mesures.

Gate F0-C

F0-C est terminée uniquement si les cinq angles sont générés depuis Basis, le gap est strictement croissant, le gap 32 est au moins 8 mm, la marge inférieure se déplace d’au moins 10 mm, la transformation rigide est respectée à 0,25 mm, crâne et lèvre supérieure restent fixes à 0,01 mm, cou hors transition à 0,5 mm, aucune face n’est inversée, config/jaw-mask.json et config/jaw-motion.json sont complets et signés, et le test échoue réellement sur une fausse pose 32.

────────

F0-D — Décider le raccord tête-corps par une expérience mesurée

La tête d’animation est fermée, manifold et sans bord ouvert. Elle n’a donc pas de boucle de couture à souder directement au corps. Le checkpoint mesure en outre 3,34463 % d’écart d’échelle et jusqu’à 4,0694 mm de résidu. Tu dois comparer un transfert de déformations vers le corps continu à un remplacement complet, puis écrire une décision.

F0-D.1 — Charger les bonnes collections et les bons objets

Action

Crée :

```
mkdir -p experiments/body-transfer \
  renders/f0-final/body-transfer \
  renders/f0-final/body-replacement
```

Résous FACE_AUTHOR_BLEND depuis reports/f0-final/author-input.json, puis dans Blender choisis File > New > General. Fais un premier File > Append vers $FACE_AUTHOR_BLEND > Object et charge explicitement GEO-head_animation_realistic. Cette tête — et non la collection Head de l’asset externe — est l’entrée d’auteur signée.

Fais un second File > Append vers $ATLAS_BASE_MESH > Collection et charge uniquement :

```
Body Male - Realistic
```

Body Male - Realistic est une collection, pas un objet. Dans l’Outliner, développe-la et sélectionne explicitement son mesh :

```
GEO-body_male_realistic
```

Duplique la tête auteur et ce mesh corps avec Shift+D puis clic droit pour annuler le déplacement. Renomme les copies EXP_head_source et EXP_body_target. Cache les originaux.

Résultat visible attendu

L’Outliner contient la tête provenant du blend auteur, la collection corps et les deux duplicatas. La tête d’animation et le corps se superposent approximativement, mais le raccord n’est pas parfait. Aucun script ne cherche bpy.data.objects avec un nom de collection.

Sauvegarde

Sauvegarde experiments/body-transfer/F0_BODY_TRANSFER_WORK.blend.

Mini-test immédiat

Dans la Python Console :

```
print(bpy.data.collections.get("Body Male - Realistic"))
print(bpy.data.objects.get("GEO-head_animation_realistic"))
print(bpy.data.objects.get("GEO-body_male_realistic"))
```

Les trois résultats doivent être non nuls. Vérifie aussi que le SHA du blend d’où vient la tête est celui de author-input.json; experiments/body-transfer/F0_BODY_TRANSFER_WORK.blend doit recopier cette provenance dans une propriété de scène atlas_face_author_sha256.

Si ce n’est pas le cas

Si les collections sont absentes, vérifie le SHA de l’asset. Si l’objet corps a un autre nom, n’invente pas une correspondance : relance asset-preflight et documente la version réellement chargée.

F0-D.2 — Reproduire les deux échecs de raccord

Action

Relance le script existant contre l’asset signé :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/f0-raccord-corps.py -- \
  reports/f0-final/raccord-corps-baseline.json
```

Dans Blender, affiche EXP_head_source en cyan semi-transparent et EXP_body_target en magenta. Passe successivement en face, profils et vue arrière du cou. N’applique aucune transformation avant cette observation.

Résultat visible attendu

Le JSON montre 13 PASS et 2 FAIL : échelle 3,34463 % au lieu de 1 %, résidu maximum 4,0694 mm au lieu de 2 mm. L’overlay montre que l’écart n’est pas une simple couture à fermer.

Sauvegarde

Sauvegarde le JSON et quatre captures baseline.

Mini-test immédiat

Compare le rapport aux nombres de départ. Si un nombre diffère, vérifie ATLAS_BASE_MESH et Blender avant d’avancer.

Si ce n’est pas le cas

Si le script retourne code 0 malgré les FAIL, F0-A n’est pas correctement appliquée. Si le visuel semble parfait mais le résidu échoue, affiche les repères annotés ; ne remplace pas la mesure par l’impression visuelle.

F0-D.3 — Calculer une similarité initiale sur duplicata

Action

Crée rig/fit-head-to-body.py. Sur EXP_head_source uniquement, définis des landmarks homologues : centres oculaires, base du nez, pointe du menton et deux repères latéraux. Résous une transformation de similarité avec rotation, translation et échelle uniforme. Refuse toute échelle non uniforme.

Applique la matrice au duplicata source, jamais au master. Dans Blender, utilise N > Item pour afficher la matrice résultante et vérifie qu’aucun shear n’apparaît. Rends les repères avant/après.

Résultat visible attendu

Les yeux, le nez et le menton se rapprochent des homologues du corps. L’écart global diminue, mais des différences morphologiques locales persistent. Le corps ne bouge pas.

Sauvegarde

Écris reports/f0-final/head-body-fit.json avec landmarks, matrice 4x4, échelle uniforme, p50/p95/max résidu et SHA des deux meshes.

Mini-test immédiat

Recompose la matrice depuis le JSON dans un fichier Blender neuf. Les positions transformées doivent correspondre à 0,01 mm. Vérifie aussi :

```
abs(scale_x - scale_y) <= 1e-6
abs(scale_y - scale_z) <= 1e-6
```

Si ce n’est pas le cas

Si l’échelle devient non uniforme, le solveur n’est pas une similarité. Si un landmark domine, vérifie les correspondances ou emploie des poids signés, mais publie-les avant la nouvelle résolution.

F0-D.4 — Peindre le masque facial cible sur le corps

Action

Dans Blender, sélectionne EXP_body_target, Tab pour Edit Mode, puis crée le vertex group VG_F0_FACE_TRANSFER. Assigne poids 1 aux paupières, nez, lèvres, joues, menton et avant du visage. Crée une transition vers tempes, oreilles et sous-menton. Le poids doit atteindre exactement zéro avant l’anneau de cou ; tronc et arrière du crâne restent zéro.

Pour rendre l’opération reproductible, exporte les indices et poids dans config/body-face-transfer-mask.json. Crée ensuite rig/build-body-transfer-mask.py qui reconstruit le groupe depuis ce fichier et vérifie le SHA topologique du corps.

Résultat visible attendu

La heatmap est rouge sur la face, devient progressivement bleue avant le cou et reste entièrement bleue sur le tronc. Aucun îlot rouge n’apparaît sur l’arrière de la tête.

Sauvegarde

Sauvegarde la configuration et les heatmaps face, profil et cou.

Mini-test immédiat

Le script vérifie que tout sommet de l’anneau de cou et tout sommet du tronc signé a un poids zéro. Il refuse les poids hors 0 à 1 et les composantes isolées.

Si ce n’est pas le cas

Si le cou bouge, déplace la fin de falloff vers le haut, mais conserve une transition douce. Si le menton n’est pas rouge, ajoute la région faciale manquante avant le transfert.

F0-D.5 — Segmenter les régions avant la correspondance

Action

Crée config/body-transfer-regions.json. Sur la tête auteur et le corps cible, définis au minimum :

```
outer_skin
eye_margin_upper.L
eye_margin_lower.L
eye_margin_upper.R
eye_margin_lower.R
lip_upper
lip_lower
oral_mucosa
nose
neck
```

Dans Blender, vérifie chaque région avec une couleur distincte. Aucun sommet de lèvre supérieure ne doit appartenir à lip_lower, et aucun sommet de peau ne doit se mapper sur une sclère.

Résultat visible attendu

Les couleurs suivent les frontières anatomiques. Les marges restent séparées même si elles sont proches spatialement.

Sauvegarde

Sauvegarde body-transfer-regions.json et une planche de segmentation.

Mini-test immédiat

Le test refuse les chevauchements interdits et vérifie que chaque sommet de masque 1 appartient à une région compatible.

Si ce n’est pas le cas

Si une lèvre appartient aux deux régions, corrige les groupes à partir des chemins F0-B. Si des trous de segmentation existent dans la zone de masque 1, assigne-les explicitement avant de mapper.

F0-D.6 — Construire la correspondance barycentrique

Action

Crée rig/build-body-transfer-map.py. Pour chaque sommet du corps dont le masque est supérieur à zéro :

1. recherche le triangle le plus proche uniquement dans la région source compatible ;
2. stocke les trois indices du triangle et les poids barycentriques ;
3. calcule l’offset normal signé et ses composantes tangentielles dans le repère du triangle neutre ;
4. rejette une correspondance au-delà de la distance maximale pré-enregistrée ;
5. écrit la région, le masque et le résidu neutre.

Lance :

```
blender -b experiments/body-transfer/F0_BODY_TRANSFER_WORK.blend \
  --python rig/build-body-transfer-map.py -- \
  --regions config/body-transfer-regions.json \
  --mask config/body-face-transfer-mask.json \
  --output reports/f0-final/body-transfer-map.json
```

Résultat visible attendu

Dans le debug blend, des traits courts relient le corps à la tête de même région. Aucun trait ne traverse la bouche, ne part d’une paupière vers le globe ni ne rejoint l’autre lèvre.

Sauvegarde

Sauvegarde la map JSON, son SHA et trois rendus de traits de correspondance.

Mini-test immédiat

Vérifie pour chaque entrée que les poids barycentriques somment à un à 1e-6 et restent dans la plage tolérée. Tire au hasard 100 correspondances avec une graine fixe et affiche-les pour revue.

Si ce n’est pas le cas

Si un trait traverse une frontière, la segmentation est fausse ou la recherche n’est pas filtrée. Ne corrige pas en augmentant la distance maximale globale ; corrige la région.

F0-D.7 — Transférer les deltas de six poses

Action

Crée rig/apply-body-transfer.py. Pour une pose source, reconstruis chaque point sur son triangle déformé, transporte l’offset dans le nouveau repère tangent-normal, puis calcule :

```
delta_ref = point_source_pose_avec_offset - point_source_neutre_avec_offset
delta_candidat = poids_masque * delta_ref
cible_pose = cible_neutre + delta_candidat
```

N’évalue pas l’erreur sur les positions absolues du neutre. Applique les six poses :

```
neutral
blink_L_100
blink_R_100
lips_close_100
jaw_20
jaw_32
```

Résultat visible attendu

Le corps reste un mesh continu. Les expressions se lisent sur son visage, tandis que le cou et le tronc restent immobiles. Le neutre est strictement identique au corps d’entrée.

Sauvegarde

Sauvegarde experiments/body-transfer/F0_BODY_TRANSFER_RESULT.blend et reports/f0-final/body-transfer.json.

Mini-test immédiat

Pour les sommets de masque 1, mesure erreur_delta entre delta candidat et delta référence : médiane au plus 0,25 mm, p95 au plus 0,75 mm, maximum au plus 2 mm. Pour masque 0, déplacement maximum 0,01 mm.

Si ce n’est pas le cas

Si le neutre change, tu as transféré une position absolue au lieu d’un delta. Si p95 échoue localement, affiche les pires correspondances et corrige région ou offset. Si le cou bouge, corrige le masque.

F0-D.8 — Faire une contre-épreuve Surface Deform

Action

Dans F0_BODY_TRANSFER_WORK.blend, sélectionne EXP_body_target. Modifiers > Add Modifier > Deform > Surface Deform. Dans Target, choisis EXP_head_source. Dans Vertex Group, choisis VG_F0_FACE_TRANSFER. Place le modifier sur une copie du corps réservée à l’expérience et clique Bind au neutre.

Vérifie dans la Python Console que modifier.is_bound est vrai. Joue les mêmes six poses sur la tête source. Bake seulement dans le duplicata de test.

Résultat visible attendu

Surface Deform suit la face source sans déplacer les sommets hors groupe. Il peut être meilleur ou pire que la map barycentrique, mais son comportement est mesurable.

Sauvegarde

Sauvegarde reports/f0-final/body-surface-deform.json et les mêmes vues que la méthode barycentrique.

Mini-test immédiat

Le test compare p50, p95, max, mouvement hors groupe, intersections, UV et temps pour les deux méthodes.

Si ce n’est pas le cas

Si Bind échoue, vérifie transforms appliqués sur les duplicatas et proximité des surfaces. Ne change pas le master. Si le hors-groupe bouge au-delà de 0,01 mm, vérifie l’assignation du Vertex Group au modifier.

F0-D.9 — Tester le remplacement complet comme A/B

Action

Duplique encore les assets dans une collection EXP_REPLACEMENT. Sur ces copies seulement, définis les faces du corps qui seraient retirées et le volume de tête conservé. Ne supprime rien tant que les indices ne sont pas écrits dans reports/f0-final/body-replacement-plan.json.

Réalise le prototype, puis inspecte face, profils, arrière du cou et rotation de tête. Cherche trous, double surface, intersections, bords visibles et perte du visage choisi.

Résultat visible attendu

La voie remplacement expose clairement son coût. Elle ne peut être retenue que si elle montre zéro trou, zéro double surface, zéro intersection et une jonction invisible dans toutes les vues.

Sauvegarde

Sauvegarde experiments/body-transfer/F0_BODY_REPLACEMENT.blend, body-replacement.json et les rendus.

Mini-test immédiat

Utilise Select > Select All by Trait > Non-Manifold en Edit Mode sur le résultat, puis un test automatisé d’arêtes ouvertes, volumes superposés et faces inversées.

Si ce n’est pas le cas

Si un bord ou une double surface demeure, la voie ne passe pas. Ne masque pas la couture avec un matériau ou une caméra éloignée.

F0-D.10 — Écrire la décision

Action

Crée reports/f0-final/DECISION_RACCORD_CORPS.md. Compare, pour les six poses et les deux voies : neutralité, topologie, UV, p50/p95/max de delta, intersections, cou, complexité d’export et reproductibilité.

Écris exactement une décision :

```
STRATÉGIE RETENUE : TRANSFERT DE DÉFORMATIONS
```

ou :

```
STRATÉGIE RETENUE : REMPLACEMENT COMPLET
```

Si le transfert respecte ses seuils, retiens-le : il conserve le corps watertight et ses UV tout en gardant la cage faciale comme auteur.

Résultat visible attendu

Le document ne contient plus à trancher. Chaque affirmation renvoie à un JSON et à une vue.

Sauvegarde

Sauvegarde la décision, les rapports et les rendus des deux voies.

Mini-test immédiat

Un script simple vérifie qu’une et une seule chaîne STRATÉGIE RETENUE existe et que tous les chemins référencés sont présents.

Si ce n’est pas le cas

Si aucune voie ne passe, n’invente pas une décision positive. Marque F0-D bloquée, localise la métrique défaillante et améliore la correspondance ou le prototype avant de reprendre.

Gate F0-D

F0-D est terminée seulement si les six poses ont été comparées, le neutre et les UV du corps restent inchangés, la voie retenue n’a ni trou ni double surface, le masque atteint zéro avant le cou, le transfert retenu respecte 0,25 mm médiane, 0,75 mm p95 et 2 mm maximum dans la région de masque 1, les profils L/R et le cou sont rendus, et DECISION_RACCORD_CORPS.md contient une décision unique appuyée par les rapports.

────────

F0-E — Décider la pile de modificateurs et prouver le chemin glTF

Cette phase répond à trois questions avant de créer F1 : dans quel ordre Armature et Multires doivent-ils être évalués, quelle surface devient le runtime, et est-ce qu’un petit rig Atlas conserve réellement os et morph targets après export et réimport. Toutes les scènes de cette phase sont jetables et reconstruites par script.

F0-E.1 — Relever la pile actuelle sans la modifier

Action

Résous FACE_AUTHOR_BLEND depuis reports/f0-final/author-input.json, puis ouvre-le avec blender "$FACE_AUTHOR_BLEND" dans Blender 5.1.2. Dans l’Outliner, sélectionne GEO-head_animation_realistic. Va dans Properties > Modifiers. Déplie chaque modifier et note, dans l’ordre de haut en bas : type, nom, show_viewport, show_render, levels, sculpt_levels et render_levels.

Dans Scripting > Python Console, exécute :

```
obj = bpy.data.objects["GEO-head_animation_realistic"]
for i, m in enumerate(obj.modifiers):
    print(i, m.name, m.type)
```

Crée tools/inspect-modifier-stack.py afin de produire le même relevé sans interface.

Résultat visible attendu

Le Multires du checkpoint est présent avec un niveau sculpté réel conservé. Aucun Armature modifier permanent n’existe encore. Aucun bouton Apply n’est utilisé sur le master.

Sauvegarde

Écris reports/f0-final/modifier-stack-input.json avec le SHA du blend, le nom de l’objet et toutes les propriétés RNA pertinentes du Multires.

Mini-test immédiat

Ferme Blender sans enregistrer, relance le script en background et compare le JSON. Les valeurs doivent être identiques.

Si ce n’est pas le cas

Si le Multires manque, vérifie que tu n’as pas ouvert un fichier de debug. Si un Armature permanent apparaît, le master a été contaminé : arrête, identifie la copie correcte de c0885 et ne sauvegarde rien.

F0-E.2 — Construire deux scènes strictement équivalentes

Action

Crée experiments/modifier-order/build-ab.py. Le script ouvre le master et construit deux fichiers séparés, pas deux objets dans une même scène :

```
experiments/modifier-order/A_ARMATURE_THEN_MULTIRES.blend
experiments/modifier-order/B_MULTIRES_THEN_ARMATURE.blend
```

Dans chaque fichier :

1. conserve seulement la tête, les quatre meshes d’œil et une armature temporaire ;
2. purge les datablocks non utilisés ;
3. crée la même armature temporaire de mâchoire à partir de config/jaw-motion.json ;
4. crée les mêmes groupes de poids depuis jaw-mask.npy ;
5. crée trois shape keys temporaires sur la copie de tête à partir des deltas F0-B : TMP_blink.L, TMP_blink.R et TMP_mouthClose ;
6. garde le même Multires et le même niveau sculpté ;
7. dans A, place Armature au-dessus de Multires ;
8. dans B, place Multires au-dessus de Armature ;
9. sauvegarde après rechargement et réévalue.

Les shape keys sont évaluées avant les modificateurs ; elles ne constituent pas une ligne déplaçable de la pile. Ne présente donc pas Shape Keys comme un modifier que l’on glisse.

Lance :

```
mkdir -p experiments/modifier-order
blender -b --factory-startup --python-exit-code 1 \
  --python experiments/modifier-order/build-ab.py -- \
  --input "$FACE_AUTHOR_BLEND" \
  --deltas reports/f0-final/deformations \
  --jaw-mask reports/f0-final/deformations/jaw-mask.npy \
  --jaw-motion config/jaw-motion.json \
  --output-dir experiments/modifier-order
```

Résultat visible attendu

Les deux fichiers contiennent exactement un head, quatre meshes oculaires et une armature temporaire. Le neutre est visuellement identique. Seul l’ordre Armature/Multires change.

Sauvegarde

Sauvegarde les deux blends et experiments/modifier-order/build-manifest.json avec inventaire de chaque scène.

Mini-test immédiat

Le builder compare les inventaires, les coordonnées Basis, les UV et les poids. Il échoue si une différence autre que l’ordre des deux modificateurs existe.

Si ce n’est pas le cas

Si la scène B contient aussi la tête originale cachée, supprime-la du builder et purge les datablocks ; sinon la comparaison mémoire est fausse. Si le neutre diffère, vérifie la création des shape keys et les niveaux Multires.

F0-E.3 — Vérifier visuellement la pile A

Action

Ouvre A_ARMATURE_THEN_MULTIRES.blend. Sélectionne GEO-head_animation_realistic. Dans Modifiers, vérifie que Armature se trouve au-dessus de Multires. Dans Object Data Properties > Shape Keys, mets TMP_blink.L à 1, puis 0. Mets TMP_mouthClose à 1, puis 0. Passe l’armature en Pose Mode et joue jaw à 20 puis 32 degrés.

Affiche successivement la cage et le niveau Multires 1. Utilise un éclairage rasant sur paupières, lèvres, joues et menton.

Résultat visible attendu

La surface dense suit les déformations de cage et garde le détail sculpté. Le blink, la fermeture labiale et la mâchoire restent lisibles. Le retour à zéro rend exactement le neutre.

Sauvegarde

Rends renders/f0-final/modifier-order/A avec neutre, blink, lèvres et jaw 32, plus un wireframe cage/dense.

Mini-test immédiat

Dans la Python Console, évalue le depsgraph à deux reprises après retour à zéro et calcule le delta maximum par rapport au neutre signé. Il doit rester à 0,01 mm.

Si ce n’est pas le cas

Si le détail glisse, vérifie que le Multires a été copié avec sa grille sculptée. Si le neutre dérive, remets chaque pose à zéro et force view_layer.update ; si la dérive persiste, le builder accumule des poses.

F0-E.4 — Vérifier visuellement la pile B

Action

Ouvre B_MULTIRES_THEN_ARMATURE.blend. Vérifie dans Modifiers que Multires est au-dessus d’Armature. Joue exactement les mêmes valeurs et utilise les mêmes caméras, lumières et frame que dans A.

Résultat visible attendu

La différence avec A est visible uniquement si l’ordre affecte détail, volume, temps ou stabilité. Aucune comparaison ne repose sur une caméra ou un matériau différent.

Sauvegarde

Rends les mêmes fichiers sous renders/f0-final/modifier-order/B.

Mini-test immédiat

Calcule une image différence A/B et un rapport de distance surface. Si toutes les valeurs sont identiques dans la tolérance, le rapport doit le dire au lieu d’inventer une préférence visuelle.

Si ce n’est pas le cas

Si les fichiers ont des inventaires différents, reconstruis-les. Si B manque de poids dense, vérifie l’évaluation du modifier et non le masque.

F0-E.5 — Mesurer performance, mémoire et géométrie

Action

Crée tests/f0-modifier-order-ab.py. Pour chaque voie, ferme et rouvre le blend, effectue cinq évaluations de chauffe puis vingt évaluations chronométrées pour :

```
neutral
blink_L_100
blink_R_100
mouthClose_100
jaw_20
jaw_32
```

Mesure temps médian/p95, mémoire du processus, taille du fichier, nombre de sommets évalués, UV, normales, volume, distance au résultat cage attendu, détail sculpté et stabilité après reload.

Lance chaque voie dans un processus Blender distinct :

```
blender -b experiments/modifier-order/A_ARMATURE_THEN_MULTIRES.blend \
  --python tests/f0-modifier-order-ab.py -- \
  --label A --output reports/f0-final/modifier-order-A.json

blender -b experiments/modifier-order/B_MULTIRES_THEN_ARMATURE.blend \
  --python tests/f0-modifier-order-ab.py -- \
  --label B --output reports/f0-final/modifier-order-B.json
```

Puis agrège :

```
python3 tools/compare-modifier-order.py \
  --a reports/f0-final/modifier-order-A.json \
  --b reports/f0-final/modifier-order-B.json \
  --output reports/f0-final/modifier-order-ab.json
```

Résultat visible attendu

Le rapport permet de choisir A ou B avec des nombres. Le candidat attendu est Armature avant Multires, mais il ne gagne que si le banc le confirme.

Sauvegarde

Sauvegarde les trois JSON et reports/f0-final/DECISION_MODIFIER_ORDER.md.

Mini-test immédiat

Le comparateur refuse les fichiers dont l’inventaire, les poses ou le nombre d’itérations diffèrent. Il publie la dispersion, pas seulement une mesure unique.

Si ce n’est pas le cas

Si la mémoire de B est presque doublée, vérifie qu’une tête source cachée n’a pas été conservée. Si les temps varient fortement, augmente les répétitions après avoir isolé la scène et garde les cinq warmups.

F0-E.6 — Choisir la résolution runtime

Action

Crée rig/build-runtime-mesh.py. Le runtime n’exporte pas Multires comme comportement. Le script :

1. ouvre le master final candidat en lecture ;
2. remet toutes les poses à zéro ;
3. évalue la surface au niveau Multires retenu ;
4. crée GEO_face_runtime depuis la surface évaluée ;
5. signe topologie, UV, normales et ordre ;
6. pour chaque delta temporaire, réévalue la même topologie dense à 1 ;
7. crée un morph target dense avec les positions évaluées ;
8. retire Multires de la copie runtime ;
9. transfère les poids de cage vers dense par barycentrique dans la même région ;
10. garde au plus quatre influences, puis renormalise ;
11. conserve uniquement les os de déformation de la copie de spike.

Le nombre de sommets dense est lu du mesh évalué et enregistré ; ne le devine pas à partir de 3 242.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python rig/build-runtime-mesh.py -- \
  --input experiments/modifier-order/A_ARMATURE_THEN_MULTIRES.blend \
  --level 1 \
  --output experiments/gltf-spike/atlas-runtime-spike.blend \
  --report reports/f0-final/runtime-resolution.json
```

Si B a gagné le banc, remplace seulement le fichier d’entrée par B et documente la décision.

Résultat visible attendu

Le runtime contient GEO_face_runtime sans Multires, avec des morph targets temporaires de même cardinalité et une armature de déformation. La surface neutre ressemble au rendu dense du master.

Sauvegarde

Sauvegarde le blend runtime et runtime-resolution.json.

Mini-test immédiat

Vérifie zéro sommet sans poids, somme des poids égale à un à 1e-6, au plus quatre influences, erreur maximale de pose après troncature au plus 0,25 mm et UV sémantiquement identiques.

Si ce n’est pas le cas

Si les morphs denses n’ont pas le même nombre de sommets, l’évaluation change de topologie entre poses : bloque l’export et corrige le builder. Si des sommets n’ont pas de poids, examine la correspondance barycentrique avant de les assigner au bone le plus proche.

F0-E.7 — Construire le spike de rig

Action

Crée experiments/gltf-spike/build_spike.py. À partir du runtime, garde :

```
DEF_face_root
DEF_head
DEF_jaw
DEF_eye.L
DEF_eye.R
```

Si F1 n’existe pas encore, crée ces cinq os temporairement selon les données F0-C et les centres oculaires mesurés. Ajoute une action TMP_SPIKE avec des frames distinctes :

```
1  neutral
10 blink_L_100
20 blink_R_100
30 mouthClose_100
40 jaw_20
50 jaw_32
60 gaze_left
70 gaze_right
80 neutral
```

Keyframe les TRS des bones et les valeurs de morph, pas les contrôleurs ni les contraintes. Enregistre le résultat dans experiments/gltf-spike/spike.blend.

Résultat visible attendu

En jouant la timeline dans Blender, chaque pose apparaît à sa frame. Les yeux tournent rigidement, la mâchoire ouvre et les trois morphs agissent. Le retour frame 80 est neutre.

Sauvegarde

Sauvegarde spike.blend et experiments/gltf-spike/spike-reference.json avec positions et rotations de référence par frame.

Mini-test immédiat

Ferme puis rouvre spike.blend et rejoue les frames en background. Compare les matrices et morph values au JSON de référence.

Si ce n’est pas le cas

Si la timeline dépend d’un driver, bake la valeur évaluée en keyframes. Si une contrainte est nécessaire pour construire la pose, conserve-la dans la scène auteur temporaire mais bake le résultat sur les DEF avant export.

F0-E.8 — Interroger l’exporteur au lieu de deviner ses options

Action

Crée experiments/gltf-spike/export_spike.py. Avant l’appel, interroge RNA :

```
op = bpy.ops.export_scene.gltf
props = {
    p.identifier
    for p in op.get_rna_type().properties
    if p.identifier != "rna_type"
}
print("GLTF_OPERATOR_PROPERTIES", sorted(props))
```

Associe ensuite les intentions aux identifiants réellement présents dans Blender 5.1.2 :

```
format GLB
export de la sélection
Apply Modifiers désactivé
skins activés
morph targets activés
animation des morphs activée
animations activées
```

Avant l’export, désélectionne tout. Sélectionne seulement l’armature et les meshes runtime. Refuse caméra, lumière, head source ou objet DBG. Écris les options effectives dans export-settings.json.

Lance :

```
blender -b experiments/gltf-spike/spike.blend \
  --python experiments/gltf-spike/export_spike.py -- \
  --output experiments/gltf-spike/spike.glb \
  --settings experiments/gltf-spike/export-settings.json
```

Résultat visible attendu

Le terminal affiche la liste RNA, puis le chemin du GLB. Le fichier existe et sa taille est non nulle. Apply Modifiers est faux afin de ne pas perdre les shape keys.

Sauvegarde

Sauvegarde export_spike.py, export-settings.json et spike.glb.

Mini-test immédiat

Le script rouvre son JSON et vérifie que toutes les intentions critiques ont trouvé un identifiant RNA. Il échoue si une option manque au lieu de l’ignorer.

Si ce n’est pas le cas

Si l’opérateur n’existe pas, vérifie l’installation de l’exporteur glTF dans cette version. Si les morphs manquent, contrôle Apply Modifiers et l’existence des key blocks sur le runtime. Si des objets source sont exportés, corrige la sélection explicite.

F0-E.9 — Valider le GLB

Action

Crée tools/validate_glb.py comme wrapper versionné autour du Khronos glTF Validator. Le wrapper enregistre version du validateur, commande, stdout, stderr et rapport JSON. Il ne transforme pas un avertissement en erreur silencieusement, et exige zéro erreur.

Lance :

```
python3 tools/validate_glb.py \
  --input experiments/gltf-spike/spike.glb \
  --output experiments/gltf-spike/validator.json
```

Résultat visible attendu

Le validateur annonce zéro erreur. Le JSON contient la version exacte du validateur et l’inventaire du GLB.

Sauvegarde

Sauvegarde validator.json. Si le binaire du validateur n’est pas versionné, ajoute tools/bootstrap-validator.md avec version, SHA et installation reproductible.

Mini-test immédiat

Teste le wrapper sur une copie tronquée du GLB dans un dossier temporaire. Il doit terminer non zéro. Ne conserve pas la copie corrompue.

Si ce n’est pas le cas

Si une erreur vise le skin ou les accessors de morph, corrige le builder/exporteur avant round-trip. Ne passe pas directement au viewer parce que Blender réimporte parfois un fichier invalide.

F0-E.10 — Réimporter dans un Blender vide

Action

Crée experiments/gltf-spike/import_spike.py. Il part de –factory-startup, importe le GLB, inventorie nodes, meshes, bones, morph targets et actions, joue chaque frame de référence et compare la géométrie au spike source.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python experiments/gltf-spike/import_spike.py -- \
  --input experiments/gltf-spike/spike.glb \
  --reference experiments/gltf-spike/spike-reference.json \
  --report experiments/gltf-spike/roundtrip.json \
  --save experiments/gltf-spike/roundtrip.blend
```

Résultat visible attendu

Le fichier réimporté contient les bones DEF attendus, les trois morphs et l’action. Les frames neutral, blink, lèvres, jaw et regard sont lisibles.

Sauvegarde

Sauvegarde roundtrip.json et roundtrip.blend.

Mini-test immédiat

Applique ces seuils :

```
neutre position max  0,01 mm
morph position max   0,05 mm
os translation max   0,01 mm
os rotation max      0,01 degré
UV max               1e-6
```

Pour UV, compare des triangles canoniques composés de tuples position/UV/normale. Ne compare pas naïvement l’ordre des loops : glTF peut trianguler, dupliquer les coutures et réordonner les sommets.

Si ce n’est pas le cas

Si le nombre de sommets diffère mais les triangles canoniques correspondent, le réordonnancement glTF est normal. Si la géométrie dépasse les seuils, localise la frame et le morph. Si l’action manque, vérifie l’export des animations et le bake des DEF.

F0-E.11 — Tester dans le runtime réel

Action

Charge spike.glb dans le runtime cible, idéalement Three.js avec GLTFLoader. Affiche une interface minimale permettant de choisir une frame ou de régler morphTargetInfluences. Active un matériau simple et une lumière qui montrent les paupières et la bouche.

Résultat visible attendu

Le runtime joue les mêmes poses que Blender. Aucun driver, Damped Track, Bone Collection, widget ou Multires n’est requis : seuls TRS, skin et morph targets sont utilisés.

Sauvegarde

Écris reports/f0-final/gltf-runtime-smoke.json avec version du runtime, navigateur ou moteur, captures et résultat de chaque pose.

Mini-test immédiat

Recharge la page ou le moteur depuis un cache vide. Vérifie jaw, yeux et morphs sans dépendre du blend source.

Si ce n’est pas le cas

Si Blender round-trip passe mais pas le runtime, réduis le cas au spike et inspecte le mapping de morph targets et de skeleton. Ne modifie pas encore le rig complet.

Gate F0-E

F0-E est terminée uniquement si les scènes A/B ne diffèrent que par l’ordre, le choix est écrit après vingt mesures et reload, la résolution runtime est signée, le mesh dense n’a ni Multires ni sommet sans poids, le GLB contient skin, morphs et animation, Khronos rapporte zéro erreur, le round-trip respecte 0,01 mm/0,05 mm/0,01 degré/1e-6, le runtime réel joue toutes les poses et aucune fonction Blender non exportable n’est supposée survivre.

────────

F0-F — Produire la fondation finale, les preuves et une seule vérité documentaire

F0-F ne crée pas encore le rig F1. Elle rassemble le neutral final, les contrats, les deltas de prototype, le masque jaw, les décisions de raccord et d’export, puis prouve que tout est rejouable.

F0-F.1 — Choisir la géométrie neutre qui devient la fondation

Action

Résous FACE_AUTHOR_BLEND depuis reports/f0-final/author-input.json, vérifie-le avec tests/check-f0-author-input.py, puis ouvre exactement ce fichier et fais File > Save As > Save Copy vers :

```
source/FACE_F0_FOUNDATION_FINAL.blend
```

Cette commande est identique que l’auteur signé soit le verrou c0885 ou source/FACE_F0_AUTHOR_RETOPO.blend; aucune branche ultérieure ne choisit de nouveau sa source. Sélectionne GEO-head_animation_realistic et vérifie :

• aucune armature temporaire ;
• aucun objet TMP ou DBG ;
• aucune shape key permanente ;
• Multires réel conservé et non appliqué ;
• quatre meshes oculaires présents ;
• neutral Basis et UV du contrat courant.

Supprime uniquement du dérivé les objets temporaires identifiés par le manifeste de l’expérience. N’emploie pas Select All > Delete.

Résultat visible attendu

Le fichier final montre le visage neutre et les yeux, sans contrôleur, sans bone et sans duplicata de pose. Les expériences restent dans experiments, les deltas dans reports.

Sauvegarde

Sauvegarde source/FACE_F0_FOUNDATION_FINAL.blend.

Mini-test immédiat

Crée tests/check-f0-final-inventory.py. Il refuse tout objet dont le nom commence par TMP_ ou DBG_, toute armature et toute shape key permanente. Il exige les cinq meshes attendus et le Multires.

Si ce n’est pas le cas

Si une armature ou une key block est nécessaire pour reproduire une preuve, la preuve n’est pas correctement externalisée : reconstruis-la depuis les deltas. Si un objet oculaire manque, repars du master au lieu de le réimporter à la main.

F0-F.2 — Écrire le contrat de sortie

Action

Crée d’abord tests/measure-f0-anatomy-counts.py. Sur la fondation finale, il
relit les chemins de marges, les groupes de région bouche et les bords de narine
du même SHA topologique, compte sans modifier le mesh, puis écrit
reports/f0-final/anatomy-counts.json. Lance-le avant le contrat :

```
blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
  --python tests/measure-f0-anatomy-counts.py -- \
  --margins reports/f0-final/correspondances-marges.json \
  --output reports/f0-final/anatomy-counts.json
```

Le script échoue si une région n’est pas définie ou si son SHA diffère ; il ne
remplace jamais une valeur absente par 4, 5, 14 ou 7–8. Crée ensuite
rig/write-f0-output-contract.py. Le contrat contient :

```
commit source
Blender
SHA du blend final
inventaire objets
topologie
Basis
UV
configuration modificateurs
inventaire scène
niveau Multires
repère et unités
chemin, nature et SHA du FACE_AUTHOR_BLEND signé
chemins et SHA des trois deltas
chemin et SHA de la carte miroir
chemin et SHA de globe-fit.json
chemins et SHA jaw-mask/jaw-motion
anatomy_counts : boucles palpébrales L/R, boucles labiales, triangles de la région bouche et sommets de bord de narine L/R
décision raccord
décision pile
décision runtime
résultat glTF
absence armature/shape keys
```

Dans le JSON, range les dépendances de fichiers sous artifacts. Les entrées author_input, mirror_map, globe_fit, jaw_mask, jaw_motion et anatomy_counts possèdent chacune exactement path et sha256; F1 et F3 liront ces champs au lieu de reconstruire un chemin implicite. Le contenu de l’artefact anatomy_counts est aussi recopié sous la clé top-level du même nom pour les tests Blender ; il est calculé sur la fondation finale, jamais recopié d’une constante c0885 après retopologie.

Lance :

```
blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
  --python rig/write-f0-output-contract.py -- \
  --output source/FACE_F0_FOUNDATION_FINAL.output-contract.json
```

Résultat visible attendu

Le contrat se parse et relie chaque artefact à un SHA. Si la topologie est restée c0885, les valeurs de départ sont retrouvées. Si elle a changé, le contrat publie les nouvelles valeurs et cite c0885 seulement comme provenance.

Sauvegarde

Sauvegarde le contrat.

Mini-test immédiat

Copie un delta dans un temporaire, modifie un chiffre et vérifie que le validateur du contrat le refuse. Ne modifie pas l’artefact versionné.

Si ce n’est pas le cas

Si le contrat accepte un fichier dont le SHA diffère, corrige la validation avant F1. Si le contrat contient des chemins absolus utilisateur, remplace-les par chemins dépôt relatifs.

F0-F.3 — Lancer le runner en mode final

Action

Étends tests/run-f0-final.py pour qu’il prenne la fondation finale et les nouveaux tests F0-B à F0-E. En mode final, il ne charge pas c0885ae-expected.json et n’accepte aucun code métier non nul.

Lance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/run-f0-final.py -- \
  --mode final \
  --input source/FACE_F0_FOUNDATION_FINAL.blend \
  --output reports/f0-final
```

Résultat visible attendu

Toutes les commandes terminent code 0. Aucun FAIL n’apparaît. Aucun SKIP critique n’apparaît. Le rapport distingue les tests historiques rejoués à titre de provenance des tests V3 qui font foi.

Sauvegarde

Sauvegarde reports/f0-final/registre.json et reports/f0-final/commandes.json avec stdout/stderr.

Mini-test immédiat

Force dans une copie temporaire un seuil blink à 0,00001 mm : le runner doit échouer. Force ensuite un script à lever RuntimeError : il doit enregistrer une erreur technique, pas la classer comme FAIL métier autorisé.

Si ce n’est pas le cas

Si le runner passe malgré FAIL dans un JSON, ajoute un scan de tous les registres et compare les statuts, pas seulement les codes. S’il s’arrête sans rapport sur exception, écris d’abord le journal partiel puis retourne non zéro.

F0-F.4 — Faire une coupe sagittale probante

Action

Crée tools/render-f0-sagittal.py. Sur des duplicatas de rendu uniquement :

1. coupe au vrai plan sagittal du repère facial ;
2. cap les sections ;
3. assigne gris à la peau extérieure ;
4. assigne cyan ou magenta aux sections et muqueuses ;
5. assigne rouge aux globes ;
6. ajoute une règle de 10 mm avec graduations ;
7. ajoute texte Blender 5.1.2, pose, côté et SHA court ;
8. cadre bouche, œil, cavité orale et cou.

N’applique pas le Bisect au fichier de production. Lance :

```
blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
  --python tools/render-f0-sagittal.py -- \
  --output-dir renders/f0-final/sagittal \
  --report reports/f0-final/sagittal-render.json
```

Résultat visible attendu

La coupe montre clairement intérieur et extérieur en deux couleurs. La section est capée, la règle est lisible et les globes se distinguent de la peau.

Sauvegarde

Sauvegarde les images et le rapport de rendu.

Mini-test immédiat

Le script vérifie la présence des deux matériaux de coupe, de la règle projetée et du texte. Une image clay uniforme doit échouer.

Si ce n’est pas le cas

Si la coupe est creuse, corrige le cap du duplicata. Si tout est gris, vérifie les material slots après bisect. Si la règle n’a pas 10 mm en scène, corrige les unités avant de rendre.

F0-F.5 — Rendre les wireframes bilatéraux

Action

Avec tools/render-f0-wireframes.py, charge les deltas et crée les poses sur des duplicatas temporaires. Rends :

```
paupière L neutre et fermée
paupière R neutre et fermée
lèvres neutres et fermées
narines L/R
philtrum et lèvre inférieure
cou et raccord
cage et surface Multires évaluée
jaw 0/5/10/20/32
```

Utilise les mêmes caméras neutres signées. Affiche les indices seulement sur les gros plans où ils restent lisibles.

Résultat visible attendu

Les deux côtés sont visibles. Les boucles de contact se lisent, la surface dense suit la cage, le cou ne présente pas de couture cachée et jaw ouvre réellement.

Sauvegarde

Sauvegarde sous renders/f0-final/wireframes et un contact sheet indexé.

Mini-test immédiat

Le test de preuve vérifie une image L et R pour chaque zone bilatérale, même résolution, même matrice de caméra et SHA de pose correspondant.

Si ce n’est pas le cas

Si une seule moitié paraît correcte, ne miroir pas l’image : corrige ou documente la géométrie du côté défaillant. Si le dense masque la cage, rends deux passes séparées et une superposition.

F0-F.6 — Construire le manifeste SHA

Action

Crée tools/build-f0-manifest.py. Il parcourt uniquement la liste explicite des livrables, calcule SHA-256 et taille, trie par chemin relatif et écrit audit/manifest-sha256.txt. N’inclus pas les fichiers temporaires, caches, logs locaux ni l’asset externe de 49 Mo.

Inclue au minimum :

```
source/FACE_F0_FOUNDATION_FINAL.blend
source/FACE_F0_FOUNDATION_FINAL.output-contract.json
reports/f0-final/registre.json
reports/f0-final/contacts-v3.json
reports/f0-final/jaw-motion.json
reports/f0-final/DECISION_RACCORD_CORPS.md
reports/f0-final/modifier-order-ab.json
reports/f0-final/runtime-resolution.json
reports/f0-final/gltf-runtime-smoke.json
les trois deltas
jaw-mask.npy
config/jaw-mask.json
config/jaw-motion.json
config/globe-fit.json
config/mirror-landmarks.json
reports/f0-final/author-input.json
reports/f0-final/carte-miroir.json
reports/f0-final/mirror-map-check.json
reports/f0-final/anatomy-counts.json
```

Résultat visible attendu

Le manifeste contient une ligne par livrable et aucun chemin absolu. Deux exécutions sans changement produisent le même contenu.

Sauvegarde

Sauvegarde audit/manifest-sha256.txt.

Mini-test immédiat

Ajoute un mode –verify qui relit chaque fichier et échoue sur SHA ou taille différente. Lance-le immédiatement.

Si ce n’est pas le cas

Si le manifeste change à cause d’un timestamp interne, retire les champs non déterministes de l’artefact concerné ou exclue-les explicitement du hash sémantique tout en gardant le hash binaire séparé.

F0-F.7 — Corriger les documents vivants

Action

Ouvre :

```
README.md
STATUS.md
CHANGELOG.md
handoffs/HANDOFF_FACE_NEXT.md
docs/FACS_MATRIX.md
audit/AUDIT_PACKET_FACE.md
```

Remplace les affirmations obsolètes par le statut réellement démontré. Ne réécris pas reports/f0/RAPPORT_F0.md : c’est un rapport historique. Ajoute dans les documents vivants un lien vers reports/f0-final/RAPPORT_F0_FINAL.md et explique que les anciennes empreintes 669ccd, d29e2a et 9246d8 ne sont pas celles du verrou c0885/final.

N’écris F0 TERMINÉE — F1 peut commencer qu’après la réussite du runner final.

Résultat visible attendu

Une recherche dépôt ne trouve plus de document vivant affirmant simultanément F0 complète et F0 incomplète. Les anciens rapports sont clairement étiquetés historiques.

Sauvegarde

Sauvegarde les six documents vivants et le rapport final.

Mini-test immédiat

Exécute :

```
rg -n 'F0 (TERMINÉE|INCOMPLÈTE|INCOMPLET)|669ccd|d29e2a|9246d8' \
  README.md STATUS.md CHANGELOG.md handoffs docs audit reports/f0-final
```

Lis chaque occurrence ; aucune contradiction non expliquée ne doit rester.

Si ce n’est pas le cas

Si un ancien hash doit rester pour l’historique, ajoute la date, le commit et la mention obsolète. Si un gate final n’est pas passé, garde F0 INCOMPLÈTE et explique le blocage au lieu de publier une clôture.

F0-F.8 — Écrire le rapport humain à partir des JSON

Action

Crée reports/f0-final/RAPPORT_F0_FINAL.md. Génère ses tableaux depuis les JSON, puis ajoute une lecture humaine :

• provenance et environnement ;
• contacts cage/dense ;
• jaw 0 à 32 ;
• décision raccord ;
• décision pile ;
• résolution runtime ;
• validation glTF et runtime ;
• inventaire final ;
• limites connues ;
• commandes exactes de reprise.

Chaque nombre renvoie au chemin et à la clé JSON. Chaque image a une légende indiquant pose, côté, caméra et SHA court du delta.

Résultat visible attendu

Le rapport permet à une autre personne de comprendre pourquoi F0 passe et de rejouer les commandes sans ouvrir d’abord le code source.

Sauvegarde

Sauvegarde RAPPORT_F0_FINAL.md.

Mini-test immédiat

Crée tools/check-report-links.py. Il vérifie tous les chemins Markdown locaux, les valeurs principales recopiées depuis JSON et l’absence de lien vers un fichier temporaire.

Si ce n’est pas le cas

Si une valeur a été saisie à la main et diffère du JSON, régénère le tableau. Si une preuve manque, ne retire pas son lien : rends la preuve manquante ou garde le gate en échec.

F0-F.9 — Faire une reprise complète depuis un Blender neuf

Action

Dans un environnement sans fichier Blender ouvert, relance :

```
blender -b --factory-startup --python-exit-code 1 \
  --python tests/run-f0-final.py -- \
  --mode final \
  --input source/FACE_F0_FOUNDATION_FINAL.blend \
  --output reports/f0-final/replay-clean
```

Puis vérifie le manifeste :

```
python3 tools/build-f0-manifest.py --verify \
  audit/manifest-sha256.txt
```

Enfin, ouvre manuellement source/FACE_F0_FOUNDATION_FINAL.blend. Dans l’Outliner, vérifie l’inventaire. Dans Object Data Properties, vérifie l’absence de shape keys. Dans Modifiers, vérifie le Multires. Ferme sans enregistrer.

Résultat visible attendu

Le replay propre termine avec 0, reproduit les mêmes mesures déterministes, puis le manifeste passe. Le fichier final s’ouvre sans erreur et reste neutre, sans rig permanent.

Sauvegarde

Sauvegarde reports/f0-final/replay-clean/commandes.json et le SHA final dans le contrat.

Mini-test immédiat

Refais le SHA du master historique :

```
shasum -a 256 source/FACE_BASE_LOCKED.blend
```

Il doit toujours valoir cc9e55a47b1496fa81ed42deee6ee3a6f498c309d5b86610e5cd2407831f2bd8.

Si ce n’est pas le cas

Si le replay propre dépend d’un fichier hors dépôt non déclaré, ajoute cette dépendance au preflight et au contrat. Si le SHA historique a changé, F0 ne peut pas être clôturée avant restauration et analyse.

Gate final F0

F0 peut être déclarée terminée seulement lorsque toutes les conditions suivantes sont simultanément vraies :

• blink L et R mesurent chacun 0,20 mm ou moins sur cage et dense ;
• les lèvres mesurent 0,30 mm ou moins sans croisement ;
• jaw ouvre réellement aux cinq angles, avec au moins 8 mm de gap central à 32 degrés ;
• la stratégie tête-corps est décidée et prouvée ;
• l’ordre Armature/Multires et la résolution runtime sont décidés par mesure ;
• le spike GLB a zéro erreur Khronos, passe le round-trip et le runtime réel ;
• UV, neutralité, topologie et inventaire sont signés ;
• toutes les preuves bilatérales, wireframes et coupes sont présentes ;
• le runner final et le replay propre terminent avec 0, sans FAIL ni SKIP critique ;
• source/FACE_BASE_LOCKED.blend a gardé son SHA ;
• source/FACE_F0_FOUNDATION_FINAL.blend ne contient ni armature ni shape key permanente ;
• le manifeste se vérifie ;
• les documents vivants racontent tous la même vérité.

Après seulement ce gate, écris dans STATUS.md :

```
F0 TERMINÉE — F1 peut commencer
```

Le prochain fichier de travail devra être dérivé de source/FACE_F0_FOUNDATION_FINAL.blend et valider son output-contract avant de créer la première armature permanente.

Partie II — F1 à F4 : construire les mécanismes du visage

Ce guide commence après la validation de source/FACE_F0_FOUNDATION_FINAL.blend.
Il conduit jusqu’à source/ATLAS_FACE_F4_MOUTH.blend. Il est écrit pour un
opérateur qui pilote Blender avec Claude Code, mais chaque action est décrite de
façon à pouvoir être exécutée et contrôlée dans l’interface.

L’objectif de chaque étape est simple : faire une petite modification, regarder
immédiatement son effet, lancer un test ciblé, puis sauvegarder. Ne construis pas
toute une phase avant de regarder le visage.

0. Préparer la session de travail

0.1 — Ouvrir le bon fichier sans toucher à la fondation

Depuis la racine du dépôt :

```bash
mkdir -p rig tests config reports/f1 reports/f2 reports/f3 reports/f4 renders/f1 renders/f2 renders/f3 renders/f4 exports
blender source/FACE_F0_FOUNDATION_FINAL.blend
```

Dans Blender :

1. vérifie la version dans Help → About Blender : elle doit être 5.1.2 ;
2. passe en Object Mode avec Tab si nécessaire ;
3. ouvre l’Outliner et vérifie la présence de
GEO-head_animation_realistic ;
4. vérifie que les quatre objets d’œil sont présents :
GEO-head_animation_realistic.sclera.L, .sclera.R, .iris.L, .iris.R ;
5. ouvre File → Save As…, saisis source/ATLAS_FACE_F1.blend, désactive toute
option qui écraserait l’original, puis clique Save As ;
6. confirme dans la barre de titre que le fichier ouvert est bien
ATLAS_FACE_F1.blend.

Résultat visuel attendu : le personnage est strictement identique à F0 et
aucune armature n’est encore visible.

0.2 — Préparer un script de contrôle dans Blender

Passe dans l’espace de travail Scripting, clique New, nomme le texte
atlas_f1_build.py, colle le bloc suivant et clique Run Script.

```python
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(bpy.path.abspath("//")).parent

HEAD = "GEO-head_animation_realistic"
RIG = "RIG_Atlas_Face"
EYE_OBJECTS = {
    "L": (
        "GEO-head_animation_realistic.sclera.L",
        "GEO-head_animation_realistic.iris.L",
    ),
    "R": (
        "GEO-head_animation_realistic.sclera.R",
        "GEO-head_animation_realistic.iris.R",
    ),
}

def require_object(name, object_type=None):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Objet absent : {name}")
    if object_type and obj.type != object_type:
        raise RuntimeError(f"{name}: type {obj.type}, attendu {object_type}")
    return obj

def require_file(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"Fichier absent : {path}")
    return path

def save_checkpoint(relative_path):
    target = ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    print("ATLAS_SAVE", target)

def set_active(obj, mode="OBJECT"):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if mode != "OBJECT":
        bpy.ops.object.mode_set(mode=mode)

def assert_object_identity(obj, eps=1e-7):
    if obj.location.length > eps:
        raise RuntimeError(f"{obj.name}: Location non nulle {tuple(obj.location)}")
    if max(abs(a) for a in obj.rotation_euler) > eps:
        raise RuntimeError(f"{obj.name}: Rotation non nulle")
    if max(abs(s - 1.0) for s in obj.scale) > eps:
        raise RuntimeError(f"{obj.name}: Scale non unitaire {tuple(obj.scale)}")

def evaluated_coords(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    try:
        return [v.co.copy() for v in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()

def max_coordinate_error_mm(before, after):
    if len(before) != len(after):
        raise RuntimeError(f"Topologie différente : {len(before)} != {len(after)}")
    return 1000.0 * max((a - b).length for a, b in zip(before, after))

head = require_object(HEAD, "MESH")
for pair in EYE_OBJECTS.values():
    for name in pair:
        require_object(name, "MESH")

contract_path = require_file("source/FACE_F0_FOUNDATION_FINAL.output-contract.json")
F0_CONTRACT = json.loads(contract_path.read_text(encoding="utf-8"))

for artifact_name in ("author_input", "mirror_map", "globe_fit",
                      "jaw_mask", "jaw_motion", "anatomy_counts"):
    ref = F0_CONTRACT.get("artifacts", {}).get(artifact_name)
    if not isinstance(ref, dict) or not {"path", "sha256"} <= set(ref):
        raise RuntimeError(f"Artefact F0 non signé : {artifact_name}")
    artifact_path = require_file(ref["path"])
    actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    if actual_sha != ref["sha256"]:
        raise RuntimeError(f"SHA F0 incorrect : {artifact_name}")

JAW_CONFIG = json.loads(require_file(
    F0_CONTRACT["artifacts"]["jaw_motion"]["path"]
).read_text(encoding="utf-8"))
GLOBE_FIT = json.loads(require_file(
    F0_CONTRACT["artifacts"]["globe_fit"]["path"]
).read_text(encoding="utf-8"))

if JAW_CONFIG.get("space") != "WORLD" or JAW_CONFIG.get("units") != "METERS":
    raise RuntimeError("Repère jaw-motion inattendu")
for field in ("pivot_world_xyz", "hinge_axis_world_xyz"):
    if len(JAW_CONFIG.get(field, [])) != 3:
        raise RuntimeError(f"Champ jaw-motion invalide : {field}")
if GLOBE_FIT.get("space") != "WORLD":
    raise RuntimeError("globe-fit doit publier des centres WORLD")
for side in ("L", "R"):
    if len(GLOBE_FIT.get("eyes", {}).get(side, {}).get("center_world_xyz", [])) != 3:
        raise RuntimeError(f"Centre de globe absent : {side}")

print("ATLAS_PREFLIGHT_OK", bpy.app.version_string, len(head.data.vertices))
```

Test immédiat : la console système ou la zone Info doit afficher
ATLAS_PREFLIGHT_OK. Si le script s’arrête sur un nom absent, ne renomme pas au
hasard : compare l’Outliner avec le contrat F0.

Pour exécuter la suite sans effet de bord, ne concatène pas tous les blocs dans
un seul bouton Run Script. Garde les définitions de fonctions dans un texte
Blender ATLAS_HELPERS, et remplace le contenu d’un second texte ATLAS_STEP
par le bloc d’action courant. Après une fermeture/réouverture de Blender,
réexécute d’abord les blocs de helpers déjà rencontrés dans le tutoriel, puis le
bloc de l’étape. Les datablocks sont sauvegardés dans le .blend, les variables
Python comme mirror_indices ne le sont pas : recharge alors leur fichier JSON
avant de continuer.

0.3 — Règles de manipulation pendant F1–F4

• laisse les transformations objet des meshes existants telles que signées ;
• n’applique jamais Ctrl+A → All Transforms sur la tête après création des
shape keys ;
• passe toujours en Object Mode avant de changer d’objet actif ;
• dans Pose Mode, Alt+G, Alt+R, Alt+S remet un contrôle au neutre ;
• dans les panneaux de shape keys, remets toutes les valeurs à zéro avant de
sauvegarder un checkpoint ;
• sauvegarde après chaque sous-étape validée, jamais pendant une pose de test.

────────

F1 — Construire la mâchoire et le regard

1. Créer l’armature et ses collections

Manipulation dans Blender

1. passe en Object Mode ;
2. utilise Shift+A → Armature → Single Bone ;
3. dans l’Outliner, renomme l’objet RIG_Atlas_Face ;
4. dans Object Properties → Transform, saisis exactement :
Location 0,0,0, Rotation 0°,0°,0°, Scale 1,1,1 ;
5. dans Armature Data Properties → Viewport Display, coche In Front ;
6. passe en Edit Mode, sélectionne l’os par défaut et supprime-le avec X → Bones ;
7. reviens en Object Mode et sauvegarde.

La création par script est plus fiable. Si l’armature manuelle n’existe pas
encore, exécute :

```python
def create_face_armature():
    existing = bpy.data.objects.get(RIG)
    if existing:
        if existing.type != "ARMATURE":
            raise RuntimeError(f"{RIG} existe mais n'est pas une armature")
        return existing

    data = bpy.data.armatures.new("RIG_Atlas_Face_DATA")
    rig = bpy.data.objects.new(RIG, data)
    bpy.context.scene.collection.objects.link(rig)
    rig.matrix_world = Matrix.Identity(4)
    rig.show_in_front = True
    for name in ("CONTROLS", "MECHANISMS", "DEFORM", "EXPORT"):
        data.collections.new(name)
    return rig

rig = create_face_armature()
assert_object_identity(rig)
print("ATLAS_ARMATURE_OK", [c.name for c in rig.data.collections])
```

Dans Armature Data Properties → Bone Collections, quatre lignes doivent être
visibles : CONTROLS, MECHANISMS, DEFORM, EXPORT.

Test immédiat : sélectionne puis désélectionne l’armature. Aucun point du visage
ne doit bouger. Enregistre source/ATLAS_FACE_F1.blend avec Ctrl+S.

2. Créer les os racine, tête et mâchoire

2.1 — Placer d’abord le curseur sur le pivot mandibulaire

Le pivot de production est celui mesuré en F0-C, pas le menton. Ouvre
config/jaw-motion.json dans l’éditeur de texte et relève :

• rotation_max_deg — attendu : 32.0 ;
• translation_start — attendu : 0.35 ;
• translation_max_mm — valeur numérique signée en F0-C ;
• translation_direction_head_local — trois nombres, norme 1 ;
• pivot_world_xyz — les trois coordonnées du pivot, en mètres monde ;
• hinge_axis_world_xyz — l’axe de charnière unitaire mesuré.

Le centre sagittal X = 1.462567 m et la hauteur Z = 0.740 m ne sont que des
repères visuels du checkpoint c0885. Les trois coordonnées de production viennent
ensemble de pivot_world_xyz; n’en remplace aucune par une constante historique.

Dans Blender :

1. affiche une vue latérale orthographique avec Numpad 3, puis Numpad 5 si
la vue est en perspective ;
2. active View → Viewpoint → Left/Right selon le côté lisible ;
3. ouvre le panneau N → View → 3D Cursor ;
4. entre les trois coordonnées du pivot signé ;
5. contrôle en vue de face (Numpad 1) que le curseur est sur le plan médian ;
6. contrôle en vue latérale qu’il est près des condyles, jamais au menton.

2.2 — Construire les os avec des coordonnées explicites

Le code suivant recharge les deux JSON signés même après une réouverture de
Blender, convertit le pivot monde dans le repère de l’armature et refuse un axe
non unitaire. Il n’y a aucune valeur de pivot à recopier à la main. Les longueurs
servent à afficher les os ; elles ne redimensionnent pas les meshes.

```python
JAW_CONFIG = json.loads(require_file(
    F0_CONTRACT["artifacts"]["jaw_motion"]["path"]
).read_text(encoding="utf-8"))
GLOBE_FIT = json.loads(require_file(
    F0_CONTRACT["artifacts"]["globe_fit"]["path"]
).read_text(encoding="utf-8"))

jaw_pivot_world = Vector(JAW_CONFIG["pivot_world_xyz"])
JAW_HINGE_AXIS_WORLD = Vector(JAW_CONFIG["hinge_axis_world_xyz"])
if abs(JAW_HINGE_AXIS_WORLD.length - 1.0) > 1e-6:
    raise RuntimeError("hinge_axis_world_xyz n'est pas unitaire")
JAW_HINGE_AXIS_WORLD.normalize()

eye_mid_world = 0.5 * (
    Vector(GLOBE_FIT["eyes"]["L"]["center_world_xyz"])
    + Vector(GLOBE_FIT["eyes"]["R"]["center_world_xyz"])
)

rig = require_object(RIG, "ARMATURE")
assert_object_identity(rig)
world_to_rig = rig.matrix_world.inverted()
JAW_PIVOT = world_to_rig @ jaw_pivot_world
HEAD_BASE = JAW_PIVOT + Vector((0, 0, -0.025))
HEAD_TOP = JAW_PIVOT + Vector((0, 0, 0.095))
GAZE_REST = world_to_rig @ Vector((
    eye_mid_world.x, eye_mid_world.y - 0.325, eye_mid_world.z
))

def add_edit_bone(arm, name, head, tail, parent=None, use_deform=False, roll=0.0):
    eb = arm.data.edit_bones.get(name) or arm.data.edit_bones.new(name)
    eb.head = Vector(head)
    eb.tail = Vector(tail)
    if (eb.tail - eb.head).length < 0.001:
        raise RuntimeError(f"Os trop court : {name}")
    eb.roll = roll
    eb.parent = arm.data.edit_bones.get(parent) if parent else None
    eb.use_connect = False
    eb.use_deform = use_deform
    return eb

set_active(rig, "EDIT")

add_edit_bone(rig, "CTRL_face_root", HEAD_BASE, HEAD_BASE + Vector((0, 0, 0.08)))
add_edit_bone(rig, "DEF_face_root", HEAD_BASE, HEAD_BASE + Vector((0, 0, 0.06)),
              "CTRL_face_root", True)
add_edit_bone(rig, "DEF_head", HEAD_BASE, HEAD_TOP, "DEF_face_root", True)

# Le contrôle reste lisible sous le menton. Son orientation n'est pas l'axe de
# charnière ; il porte seulement la propriété open.
add_edit_bone(rig, "CTRL_jaw", JAW_PIVOT + Vector((0, -0.025, -0.025)),
              JAW_PIVOT + Vector((0, -0.025, -0.095)), "CTRL_face_root")

# Slide et hinge commencent au même pivot. Un os Blender pointe selon son +Y
# local. Le roll sera contrôlé juste après.
add_edit_bone(rig, "MCH_jaw_slide", JAW_PIVOT,
              JAW_PIVOT + Vector((0, 0, -0.050)), "CTRL_jaw")
add_edit_bone(rig, "MCH_jaw_hinge", JAW_PIVOT,
              JAW_PIVOT + Vector((0, 0, -0.070)), "MCH_jaw_slide")
add_edit_bone(rig, "DEF_jaw", JAW_PIVOT,
              JAW_PIVOT + Vector((0, -0.055, -0.080)), "MCH_jaw_hinge", True)

bpy.ops.object.mode_set(mode="OBJECT")

collections = {
    "CONTROLS": ("CTRL_face_root", "CTRL_jaw"),
    "MECHANISMS": ("MCH_jaw_slide", "MCH_jaw_hinge"),
    "DEFORM": ("DEF_face_root", "DEF_head", "DEF_jaw"),
}
for collection_name, bone_names in collections.items():
    collection = rig.data.collections[collection_name]
    for bone_name in bone_names:
        collection.assign(rig.data.bones[bone_name])

for bone in rig.data.bones:
    bone.use_deform = bone.name.startswith("DEF_")

print("ATLAS_JAW_BONES_OK", sorted(rig.data.bones.keys()))
```

2.3 — Régler le roll avant les drivers

1. sélectionne RIG_Atlas_Face, passe en Edit Mode ;
2. sélectionne MCH_jaw_hinge ;
3. active l’affichage des axes dans Armature Data Properties → Viewport Display → Axes ;
4. utilise Armature → Bone Roll → Recalculate Roll… seulement comme point de
départ ;
5. ajuste avec Ctrl+R jusqu’à ce que l’axe local X de la charnière soit
parallèle à hinge_axis_world_xyz publié par F0-C ;
6. passe en Pose Mode, sélectionne MCH_jaw_hinge, tape R, X, 5,
Enter ;
7. le menton doit descendre droit, sans dérive latérale ;
8. annule avec Alt+R.

Test immédiat par script :

```python
rig = require_object(RIG, "ARMATURE")
axis_world = (rig.matrix_world.to_3x3()
              @ rig.data.bones["MCH_jaw_hinge"].matrix_local.to_3x3()
              @ Vector((1, 0, 0))).normalized()
signed_axis = Vector(JAW_CONFIG["hinge_axis_world_xyz"]).normalized()
error_deg = math.degrees(axis_world.angle(signed_axis))
error_deg = min(error_deg, abs(180.0 - error_deg))
print("JAW_AXIS_ERROR_DEG", error_deg)
if error_deg > 0.1:
    raise RuntimeError("Roll de mâchoire incorrect : axe local X différent de F0-C")
```

Ne poursuis pas tant que ce test échoue. Sauvegarde avec Ctrl+S une fois le
roll validé.

3. Faire fonctionner CTRL_jaw.open

3.1 — Ajouter la propriété dans l’interface

1. sélectionne l’armature et passe en Pose Mode ;
2. sélectionne CTRL_jaw dans la vue ou dans l’Outliner de données ;
3. ouvre Bone Properties → Custom Properties ;
4. clique New, puis la roue dentée ;
5. nomme la propriété open ;
6. mets Default = 0, Min = 0, Max = 1, Soft Min = 0, Soft Max = 1 ;
7. mets la valeur à 0 avant de fermer le panneau.

Code équivalent et drivers complets :

```python
def add_single_prop_variable(driver, name, id_block, data_path):
    var = driver.variables.new()
    var.name = name
    var.type = "SINGLE_PROP"
    target = var.targets[0]
    target.id = id_block
    target.data_path = data_path
    return var

def replace_driver(id_block, data_path, index, expression, rig, prop_path):
    try:
        id_block.driver_remove(data_path, index)
    except (TypeError, RuntimeError):
        pass
    fcurve = id_block.driver_add(data_path, index)
    fcurve.driver.type = "SCRIPTED"
    fcurve.driver.expression = expression
    add_single_prop_variable(fcurve.driver, "open", rig, prop_path)
    return fcurve

def install_jaw_drivers(rig, jaw_config_path):
    config = json.loads(Path(jaw_config_path).read_text(encoding="utf-8"))
    rotation_max_deg = float(config["rotation_max_deg"])
    start = float(config["translation_start"])
    maximum_mm = float(config["translation_max_mm"])
    direction = Vector(config["translation_direction_head_local"])
    if abs(direction.length - 1.0) > 1e-6:
        raise RuntimeError("translation_direction_head_local n'est pas unitaire")
    if not 0.0 <= start < 1.0 or maximum_mm <= 0.0:
        raise RuntimeError("jaw-motion.json contient une amplitude invalide")

    ctrl = rig.pose.bones["CTRL_jaw"]
    ctrl["open"] = 0.0
    ui = ctrl.id_properties_ui("open")
    ui.update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
              default=0.0, description="Ouverture de mâchoire Atlas")

    prop_path = 'pose.bones["CTRL_jaw"]["open"]'
    hinge = rig.pose.bones["MCH_jaw_hinge"]
    hinge.rotation_mode = "XYZ"
    rotation_rad = math.radians(rotation_max_deg)
    replace_driver(hinge, "rotation_euler", 0,
                   f"{rotation_rad:.17g}*open", rig, prop_path)

    # Vecteur de translation : données head-local → armature → bone-local.
    v_arm = rig.data.bones["DEF_head"].matrix_local.to_3x3() @ direction
    v_local = (rig.data.bones["MCH_jaw_slide"].matrix_local.to_3x3().inverted()
               @ v_arm)
    amplitude_m = maximum_mm / 1000.0
    t = f"min(max((open-{start:.17g})/{1.0-start:.17g},0.0),1.0)"
    smooth = f"(({t})*({t})*(3.0-2.0*({t})))"
    slide = rig.pose.bones["MCH_jaw_slide"]
    for axis in range(3):
        coefficient = amplitude_m * v_local[axis]
        replace_driver(slide, "location", axis,
                       f"{coefficient:.17g}*{smooth}", rig, prop_path)

    bpy.context.view_layer.update()
    bad = [fc.data_path for fc in rig.animation_data.drivers
           if not fc.driver.is_valid]
    if bad:
        raise RuntimeError(f"Drivers invalides : {bad}")

rig = require_object(RIG, "ARMATURE")
install_jaw_drivers(rig, ROOT / "config/jaw-motion.json")
print("ATLAS_JAW_DRIVERS_OK")
```

3.2 — Tester le mouvement juste après

Dans Pose Mode, fais glisser open dans le panneau des propriétés :

• 0.00 : aucun mouvement ;
• 0.15625 : environ 5° ;
• 0.31250 : environ 10° ;
• 0.62500 : environ 20° ;
• 1.00 : 32° et translation maximale.

À ce stade le mesh ne suit pas encore : observe seulement les axes d’os. Le
slide doit démarrer après open = 0.35, puis avancer et descendre sans saut.

Exécute ce test :

```python
rig = require_object(RIG, "ARMATURE")
ctrl = rig.pose.bones["CTRL_jaw"]
hinge = rig.pose.bones["MCH_jaw_hinge"]
slide = rig.pose.bones["MCH_jaw_slide"]
previous = -1.0
for value in (0.0, 0.15625, 0.3125, 0.625, 1.0):
    ctrl["open"] = value
    bpy.context.view_layer.update()
    angle = math.degrees(hinge.rotation_euler.x)
    distance_mm = 1000.0 * slide.location.length
    print("JAW_SAMPLE", value, angle, distance_mm)
    if distance_mm + 1e-6 < previous:
        raise RuntimeError("Translation de mâchoire non monotone")
    previous = distance_mm
ctrl["open"] = 0.0
bpy.context.view_layer.update()
```

Résultat attendu : les angles affichés sont proches de 0/5/10/20/32 et la
distance du slide ne décroît jamais. Remets open = 0 et sauvegarde.

4. Peindre et installer les poids tête/mâchoire

4.1 — Ajouter le modifier Armature au bon endroit

Dans Blender :

1. passe en Object Mode et sélectionne GEO-head_animation_realistic ;
2. ouvre Modifiers ;
3. clique Add Modifier → Deform → Armature ;
4. choisis RIG_Atlas_Face dans le champ Object ;
5. coche Vertex Groups, décoche Bone Envelopes ;
6. décoche Preserve Volume : Atlas V1 utilise le skinning linéaire ;
7. avec les flèches du modifier, place Armature avant Multires ;
8. ne clique pas Apply.

4.2 — Charger le masque signé plutôt que lancer Automatic Weights

Le helper suivant attend le tableau .npy produit en F0-C. Il crée deux groupes
dont la somme vaut 1 sur chaque sommet.

```python
def ensure_armature_modifier(obj, rig):
    modifier = next((m for m in obj.modifiers if m.type == "ARMATURE"), None)
    if modifier is None:
        modifier = obj.modifiers.new("Armature", "ARMATURE")
    modifier.object = rig
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    modifier.use_deform_preserve_volume = False
    multires_index = next((i for i, m in enumerate(obj.modifiers)
                           if m.type == "MULTIRES"), None)
    arm_index = list(obj.modifiers).index(modifier)
    if multires_index is not None and arm_index > multires_index:
        while list(obj.modifiers).index(modifier) > multires_index:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_move_up(modifier=modifier.name)
    return modifier

def reset_group(obj, name):
    old = obj.vertex_groups.get(name)
    if old:
        obj.vertex_groups.remove(old)
    return obj.vertex_groups.new(name=name)

def install_jaw_weights(obj, mask_path, rig):
    import numpy as np
    weights = np.asarray(np.load(mask_path), dtype=float).reshape(-1)
    if len(weights) != len(obj.data.vertices):
        raise RuntimeError(f"Masque {len(weights)} != mesh {len(obj.data.vertices)}")
    if not np.isfinite(weights).all():
        raise RuntimeError("NaN/Inf dans le masque mandibulaire")
    weights = np.clip(weights, 0.0, 1.0)
    head_group = reset_group(obj, "DEF_head")
    jaw_group = reset_group(obj, "DEF_jaw")
    for index, jaw_weight in enumerate(weights):
        jaw_weight = 0.0 if jaw_weight < 1e-5 else float(jaw_weight)
        head_weight = 1.0 - jaw_weight
        if head_weight > 0.0:
            head_group.add([index], head_weight, "REPLACE")
        if jaw_weight > 0.0:
            jaw_group.add([index], jaw_weight, "REPLACE")
    ensure_armature_modifier(obj, rig)
    return weights

head = require_object(HEAD, "MESH")
rig = require_object(RIG, "ARMATURE")
neutral_before = evaluated_coords(head)
jaw_weights = install_jaw_weights(
    head,
    ROOT / "reports/f0-final/deformations/jaw-mask.npy",
    rig,
)
bpy.context.view_layer.update()
neutral_after = evaluated_coords(head)
error = max_coordinate_error_mm(neutral_before, neutral_after)
print("JAW_WEIGHT_NEUTRAL_ERROR_MM", error)
if error > 0.01:
    raise RuntimeError("Le skinning déplace le neutre")
```

4.3 — Inspecter les poids comme un humain

1. sélectionne la tête ;
2. passe en Weight Paint Mode ;
3. dans Object Data Properties → Vertex Groups, active DEF_jaw ;
4. vue de face : crâne, front, nez et lèvre supérieure doivent être bleus ;
5. vue latérale : menton et mandibule doivent être rouges ;
6. la joue basse doit montrer un dégradé sans tache isolée ;
7. la nuque et le bas du cou doivent rester bleus ;
8. active DEF_head : le motif doit être complémentaire ;
9. reviens en Object Mode.

Test immédiat : en Pose Mode, mets CTRL_jaw.open = 1. Le menton et la lèvre
inférieure descendent, le crâne ne bouge pas et le cou ne part pas avec la
mâchoire. Remets open = 0 avant Ctrl+S.

5. Créer les centres, os et cibles du regard

5.1 — Vérifier les centres signés par F0-B

Charge config/globe-fit.json par le chemin et le SHA du contrat F0. Pour le
checkpoint c0885 non retopologisé seulement, les valeurs de comparaison étaient :

```text
L = (1.494856, -0.125396, 0.766688)
R = (1.430278, -0.125396, 0.766688)
```

Ces nombres ne sont pas des entrées de production. Pour chaque œil, utilise le
champ courant eyes.<côté>.center_world_xyz :

1. sélectionne la sclère en Object Mode ;
2. passe en vue latérale orthographique ;
3. saisis les trois coordonnées JSON dans N → View → 3D Cursor ;
4. mets temporairement le pivot de transformation sur 3D Cursor ;
5. tourne la sclère de 30° ; son centre ne doit pas orbiter ;
6. annule avec Ctrl+Z et remets le pivot sur Median Point.

Le rayon postérieur c0885 était proche de 11.7449 mm; compare cette baseline au
champ courant radius_mm, sans l’imposer après retopologie. La cornée n’est pas
une sphère parfaite : juge le centre sur la sclère postérieure, pas sur la pointe
de cornée.

5.2 — Ajouter les os yeux et gaze

```python
globe_ref = F0_CONTRACT["artifacts"]["globe_fit"]
globe_path = require_file(globe_ref["path"])
if hashlib.sha256(globe_path.read_bytes()).hexdigest() != globe_ref["sha256"]:
    raise RuntimeError("SHA globe-fit différent du contrat F0")
GLOBE_FIT = json.loads(globe_path.read_text(encoding="utf-8"))
if GLOBE_FIT.get("space") != "WORLD":
    raise RuntimeError("globe-fit doit être exprimé en WORLD")

EYE_CENTERS_WORLD = {}
for side in ("L", "R"):
    values = GLOBE_FIT.get("eyes", {}).get(side, {}).get("center_world_xyz")
    if not isinstance(values, list) or len(values) != 3:
        raise RuntimeError(f"Centre globe signé absent : {side}")
    center = Vector((float(values[0]), float(values[1]), float(values[2])))
    if not all(math.isfinite(v) for v in center):
        raise RuntimeError(f"Centre globe non fini : {side}")
    EYE_CENTERS_WORLD[side] = center

rig = require_object(RIG, "ARMATURE")
set_active(rig, "EDIT")

# CTRL_gaze et ses deux enfants ont volontairement la même matrice de repos.
gaze_head = GAZE_REST
gaze_tail = GAZE_REST + Vector((0, 0, 0.035))
add_edit_bone(rig, "CTRL_gaze", gaze_head, gaze_tail, "CTRL_face_root")
add_edit_bone(rig, "CTRL_eye_target.L", gaze_head, gaze_tail, "CTRL_gaze")
add_edit_bone(rig, "CTRL_eye_target.R", gaze_head, gaze_tail, "CTRL_gaze")

for side, world_center in EYE_CENTERS_WORLD.items():
    center = rig.matrix_world.inverted() @ world_center
    tail = center + Vector((0, -0.030, 0))
    add_edit_bone(rig, f"MCH_eye_track.{side}", center, tail,
                  "CTRL_face_root")
    add_edit_bone(rig, f"DEF_eye.{side}", center, tail,
                  f"MCH_eye_track.{side}", True)

bpy.ops.object.mode_set(mode="OBJECT")
for bone_name in ("CTRL_gaze", "CTRL_eye_target.L", "CTRL_eye_target.R"):
    rig.data.collections["CONTROLS"].assign(rig.data.bones[bone_name])
for side in ("L", "R"):
    rig.data.collections["MECHANISMS"].assign(
        rig.data.bones[f"MCH_eye_track.{side}"])
    rig.data.collections["DEFORM"].assign(rig.data.bones[f"DEF_eye.{side}"])
    rig.data.bones[f"MCH_eye_track.{side}"].use_deform = False
    rig.data.bones[f"DEF_eye.{side}"].use_deform = True

for side in ("L", "R"):
    a = rig.data.bones[f"CTRL_eye_target.{side}"].matrix_local
    b = rig.data.bones["CTRL_gaze"].matrix_local
    if max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4)) > 1e-6:
        raise RuntimeError(f"Target {side} décalé au repos")
print("ATLAS_EYE_BONES_OK")
```

Dans Edit Mode, regarde les os avec In Front : les deux MCH_eye_track.*
doivent partir exactement du centre de leur globe et pointer vers l’avant du
personnage, donc vers -Y. Les deux petits targets peuvent être invisibles car
ils se superposent à CTRL_gaze ; c’est volontaire.

5.3 — Ajouter Damped Track puis les limites

```python
def install_eye_constraints(rig, side):
    pb = rig.pose.bones[f"MCH_eye_track.{side}"]
    for constraint in list(pb.constraints):
        if constraint.name.startswith("ATLAS_"):
            pb.constraints.remove(constraint)

    track = pb.constraints.new("DAMPED_TRACK")
    track.name = "ATLAS_DampedTrack"
    track.target = rig
    track.subtarget = f"CTRL_eye_target.{side}"
    track.track_axis = "TRACK_Y"  # +Y local = head→tail = avant -Y monde
    track.influence = 1.0

    limit = pb.constraints.new("LIMIT_ROTATION")
    limit.name = "ATLAS_LimitRotation"
    limit.owner_space = "LOCAL"
    # Avec le roll créé ci-dessus : X = pitch, Z = yaw, Y = twist/roll.
    limit.use_limit_x = True
    limit.min_x = math.radians(-35.0)
    limit.max_x = math.radians(25.0)
    limit.use_limit_y = True
    limit.min_y = 0.0
    limit.max_y = 0.0
    limit.use_limit_z = True
    limit.min_z = math.radians(-35.0)
    limit.max_z = math.radians(35.0)
    limit.influence = 1.0
    return pb

rig = require_object(RIG, "ARMATURE")
for side in ("L", "R"):
    install_eye_constraints(rig, side)
bpy.context.view_layer.update()
print("ATLAS_EYE_CONSTRAINTS_OK")
```

Vérifie l’ordre dans Bone Constraints : ATLAS_DampedTrack doit être au-dessus
de ATLAS_LimitRotation. Si le regard haut produit le mouvement bas, le roll ou
le signe X ne correspond pas : corrige le roll, puis inverse min_x/max_x ; ne
compense pas en inversant arbitrairement une sclère.

5.4 — Tester regard conjoint, convergence et limites

1. passe en Pose Mode ;
2. sélectionne CTRL_gaze ;
3. touche G, X : les deux yeux regardent latéralement ensemble ;
4. annule avec Alt+G ;
5. touche G, Z : les deux yeux regardent haut/bas ;
6. annule ;
7. touche G, Y et rapproche le contrôle du visage : les deux axes doivent
converger vers le même point ;
8. déplace CTRL_eye_target.L seul : seul l’œil L se décale ;
9. remets les trois contrôles au neutre avec Alt+G.

Pour éprouver les limites, déplace la cible très loin à gauche, droite, haut et
bas. Le mécanisme doit s’arrêter vers ±35° horizontal, +25° haut et -35° bas,
sans twist. Si Damped Track + Limit Rotation flippe, n’élargis pas les limites :
calcule un target clampé en eye-local avant le Damped Track.

6. Rendre les quatre meshes oculaires rigidement solidaires

Manipulation dans l’interface

Pour chaque sclère et iris :

1. Object Mode, sélectionne l’objet ;
2. si un parent ancien existe, fais Alt+P → Clear Parent (Keep Transform) ;
3. ajoute un modifier Armature, objet RIG_Atlas_Face ;
4. décoche Bone Envelopes et Preserve Volume ;
5. dans Object Data Properties → Vertex Groups, supprime les anciens groupes
de déformation ;
6. crée DEF_eye.L ou DEF_eye.R ;
7. passe en Edit Mode, sélectionne tout avec A, mets Weight = 1.000, puis
clique Assign ;
8. reviens en Object Mode.

Code équivalent :

```python
def rigid_bind(obj, rig, bone_name):
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = world
    for group in list(obj.vertex_groups):
        obj.vertex_groups.remove(group)
    group = obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    ensure_armature_modifier(obj, rig)

rig = require_object(RIG, "ARMATURE")
eye_neutral = {}
for side, names in EYE_OBJECTS.items():
    for name in names:
        obj = require_object(name, "MESH")
        eye_neutral[name] = evaluated_coords(obj)
        rigid_bind(obj, rig, f"DEF_eye.{side}")

bpy.context.view_layer.update()
for name, before in eye_neutral.items():
    err = max_coordinate_error_mm(before, evaluated_coords(bpy.data.objects[name]))
    print("EYE_NEUTRAL_ERROR_MM", name, err)
    if err > 0.01:
        raise RuntimeError(f"Double transform ou bind incorrect : {name}")
```

Test visuel immédiat : déplace CTRL_gaze en grand cercle. Pour chaque côté,
iris et sclère tournent comme une seule pièce, le centre du globe reste fixe et
aucun objet ne double son mouvement. Remets les contrôles au neutre.

7. Fermer F1 par une vraie séance de tests

7.1 — Échantillonner la mâchoire

Dans une vue de profil orthographique :

1. open = 0 : prends une capture ;
2. open = 0.15625 : vérifie une ouverture visible ;
3. open = 0.3125 ;
4. open = 0.625 ;
5. open = 1 : vérifie au moins 8 mm de gap central selon le gate F0-C ;
6. affiche les poids de DEF_jaw et recherche une traction du front, du nez ou
du cou ;
7. remets open = 0.

7.2 — Échantillonner le regard

Teste centre, gauche, droite, haut, bas, proche, loin. À chaque
pose :

• le centre géométrique reste à moins de 0,01 mm de sa position neutre ;
• sclère et iris restent rigides ;
• l’axe tête→tail de DEF_eye.* passe par la cible avant clamp ;
• aucune contrainte ne devient rouge dans l’interface.

7.3 — Vérifier la structure et sauvegarder

```python
def test_f1_structure():
    rig = require_object(RIG, "ARMATURE")
    required = {
        "CTRL_face_root", "DEF_face_root", "DEF_head", "CTRL_jaw",
        "MCH_jaw_slide", "MCH_jaw_hinge", "DEF_jaw", "CTRL_gaze",
        "CTRL_eye_target.L", "CTRL_eye_target.R", "MCH_eye_track.L",
        "MCH_eye_track.R", "DEF_eye.L", "DEF_eye.R",
    }
    missing = required - set(rig.data.bones.keys())
    if missing:
        raise RuntimeError(f"Os F1 absents : {sorted(missing)}")
    for bone in rig.data.bones:
        expected = bone.name.startswith("DEF_")
        if bone.name in required and bone.use_deform != expected:
            raise RuntimeError(f"use_deform incorrect : {bone.name}")
    head = require_object(HEAD, "MESH")
    types = [m.type for m in head.modifiers]
    if "MULTIRES" in types and types.index("ARMATURE") > types.index("MULTIRES"):
        raise RuntimeError("Armature doit précéder Multires")
    if head.data.shape_keys:
        raise RuntimeError("F1 ne doit encore contenir aucune shape key")
    for fc in (rig.animation_data.drivers if rig.animation_data else []):
        if not fc.driver.is_valid:
            raise RuntimeError(f"Driver invalide : {fc.data_path}")
    print("ATLAS_F1_STRUCTURE_OK")

rig = require_object(RIG, "ARMATURE")
rig.pose.bones["CTRL_jaw"]["open"] = 0.0
for name in ("CTRL_gaze", "CTRL_eye_target.L", "CTRL_eye_target.R"):
    rig.pose.bones[name].location = Vector((0, 0, 0))
bpy.context.view_layer.update()
test_f1_structure()
save_checkpoint("source/ATLAS_FACE_F1.blend")
```

Lance ensuite depuis le terminal :

```bash
blender -b source/ATLAS_FACE_F1.blend --python tests/f1-jaw-eyes.py -- --mode final --report reports/f1/registre.json
```

Le fichier est prêt pour le gel topologique uniquement si Blender rend le code
0, si l’image neutre est inchangée et si les deux sweeps sont propres.

────────

F1.5 — Geler définitivement la topologie

À partir de cette sauvegarde, ajouter, supprimer, fusionner ou réordonner un
sommet invaliderait toutes les shape keys à venir.

8. Faire la dernière inspection en Edit Mode

Avant l’inspection, charge les valeurs qui font foi :

```python
contract_path = require_file("source/FACE_F0_FOUNDATION_FINAL.output-contract.json")
F0_CONTRACT = json.loads(contract_path.read_text(encoding="utf-8"))
ANATOMY_COUNTS = F0_CONTRACT.get("anatomy_counts")
required_counts = {
    "eye_margin_loops", "lip_margin_loops",
    "mouth_region_triangles", "nostril_border_vertices",
}
if not isinstance(ANATOMY_COUNTS, dict) or not required_counts <= set(ANATOMY_COUNTS):
    raise RuntimeError("anatomy_counts absent ou incomplet dans le contrat F0")
print("ATLAS_ANATOMY_COUNTS", ANATOMY_COUNTS)
```

Sur l’auteur c0885 non retopologisé, les anciennes valeurs 4 boucles de paupière,
5 boucles labiales, 14 triangles de bouche et 7–8 sommets de bord de narine
servent uniquement de comparaison. Après retopologie, seuls les champs du JSON
font foi.

1. ouvre source/ATLAS_FACE_F1.blend ;
2. sélectionne la tête, Tab vers Edit Mode ;
3. désélectionne tout, puis inspecte avec Alt+Clic le nombre de boucles de
paupière signé dans ANATOMY_COUNTS["eye_margin_loops"] pour L et R ;
4. inspecte exactement ANATOMY_COUNTS["lip_margin_loops"] boucles autour des
lèvres ;
5. vérifie les commissures, le philtrum et le nombre signé
ANATOMY_COUNTS["mouth_region_triangles"] dans la région contractuelle ;
6. vérifie chaque bord de narine contre
ANATOMY_COUNTS["nostril_border_vertices"]["L"], puis la valeur R ;
7. reviens en Object Mode sans effectuer aucune commande de fusion.

Pour détecter des doublons sans mutation, crée
tests/check-near-duplicate-vertices.py. Il construit un KDTree des coordonnées
objet, signale les paires distinctes à moins de 1e-7 m, n’appelle aucun
opérateur Merge, puis écrit un rapport. Lance sur le fichier non modifié :

```bash
blender -b source/ATLAS_FACE_F1.blend --python-exit-code 1 \
  --python tests/check-near-duplicate-vertices.py -- \
  --object GEO-head_animation_realistic \
  --epsilon-m 1e-7 \
  --report reports/f1/near-duplicate-vertices.json
```

Le résultat attendu est le code 0 et zéro paire non autorisée. Si une paire est
signalée, ne fusionne rien dans F1 : reviens au master d’auteur pré-gel, corrige
la topologie, puis reconstruis tous les artefacts F0 et F1.

Teste aussi jaw = 32°, regard haut/bas et blink prototype F0. Si une boucle
empêche une déformation essentielle, ferme F1 sans enregistrer de changement
topologique et repars du master d’auteur pré-gel. Sur une branche dédiée,
retopologise ce master, refais UV, empreinte, landmarks/correspondances, carte
miroir, globe-fit, trois deltas et masque jaw, régénère le contrat F0-F, puis
reconstruis F1 depuis la nouvelle fondation. Ne retopologise jamais dans un
checkpoint F1.5, F3 ou F4.

9. Produire une empreinte reproductible

```python
def mesh_topology_fingerprint(obj):
    h = hashlib.sha256()
    h.update(obj.name.encode("utf-8"))
    h.update(str(len(obj.data.vertices)).encode())
    h.update(str(len(obj.data.edges)).encode())
    h.update(str(len(obj.data.polygons)).encode())
    for vertex in obj.data.vertices:
        h.update(vertex.index.to_bytes(8, "little"))
        for value in vertex.co:
            h.update(float(value).hex().encode())
    for polygon in obj.data.polygons:
        h.update(len(polygon.vertices).to_bytes(4, "little"))
        for index in polygon.vertices:
            h.update(int(index).to_bytes(8, "little"))
    for uv_layer in obj.data.uv_layers:
        h.update(uv_layer.name.encode("utf-8"))
        for item in uv_layer.data:
            h.update(float(item.uv.x).hex().encode())
            h.update(float(item.uv.y).hex().encode())
    return {
        "object": obj.name,
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "polygons": len(obj.data.polygons),
        "sha256": h.hexdigest(),
    }

contract_path = require_file("source/FACE_F0_FOUNDATION_FINAL.output-contract.json")
contract_bytes = contract_path.read_bytes()
f0_contract = json.loads(contract_bytes.decode("utf-8"))
if "anatomy_counts" not in f0_contract:
    raise RuntimeError("anatomy_counts absent du contrat F0")

head = require_object(HEAD, "MESH")
fingerprint = mesh_topology_fingerprint(head)
fingerprint["f0_contract_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
fingerprint["anatomy_counts"] = f0_contract["anatomy_counts"]
report_path = ROOT / "tests/verrou-topologie-final.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(fingerprint, indent=2), encoding="utf-8")
print("ATLAS_TOPOLOGY_LOCK", fingerprint)
save_checkpoint("source/FACE_TOPOLOGY_FINAL.blend")
```

Résultat attendu : tests/verrou-topologie-final.json existe, la tête ne
contient toujours aucune shape key et le fichier ouvert est maintenant
FACE_TOPOLOGY_FINAL.blend.

────────

F2 — Installer dents, gencives et langue

10. Dériver le fichier F2 et vérifier que le rig F1 est toujours là

Ouvre source/FACE_TOPOLOGY_FINAL.blend, puis File → Save As… vers
source/ATLAS_FACE_F2_ORAL.blend.

Exécute immédiatement :

```python
rig = require_object(RIG, "ARMATURE")
for name in ("DEF_head", "DEF_jaw", "DEF_eye.L", "DEF_eye.R"):
    if name not in rig.data.bones:
        raise RuntimeError(f"F2 ne peut pas commencer : {name} absent")
head = require_object(HEAD, "MESH")
for name in ("DEF_head", "DEF_jaw"):
    if head.vertex_groups.get(name) is None:
        raise RuntimeError(f"Groupe facial absent : {name}")
if head.data.shape_keys:
    raise RuntimeError("Le gel F1.5 doit précéder la première shape key")
print("ATLAS_F2_PREFLIGHT_OK")
```

Si ce test échoue, ne rattache pas les dents à une armature incomplète : reviens
au checkpoint F1.5.

11. Extraire et identifier les 28 dents

11.1 — Charger seulement Jaw - Realistic

Dans un terminal, vérifie que la variable d’environnement pointe vers le paquet
source, puis lance Blender :

```bash
test -n "$ATLAS_BASE_MESH" && test -f "$ATLAS_BASE_MESH"
blender source/ATLAS_FACE_F2_ORAL.blend
```

Dans Blender, tu peux utiliser File → Append, ouvrir le .blend indiqué par
$ATLAS_BASE_MESH, entrer dans Object, choisir Jaw - Realistic, puis
Append. Le code équivalent évite d’importer tout le paquet :

```python
import os

def append_named_object(blend_path, object_name):
    blend_path = Path(blend_path)
    if not blend_path.is_file():
        raise RuntimeError(f"Asset introuvable : {blend_path}")
    with bpy.data.libraries.load(str(blend_path), link=False) as (source, dest):
        if object_name not in source.objects:
            raise RuntimeError(f"{object_name} absent de {blend_path}")
        dest.objects = [object_name]
    obj = dest.objects[0]
    if obj is None:
        raise RuntimeError("Append de Jaw - Realistic échoué")
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    return obj

asset_path = os.environ.get("ATLAS_BASE_MESH")
if not asset_path:
    raise RuntimeError("ATLAS_BASE_MESH n'est pas défini dans l'environnement")

old = bpy.data.objects.get("Jaw - Realistic")
if old:
    raise RuntimeError("Jaw - Realistic est déjà chargé : inspecter avant de dupliquer")
jaw_source = append_named_object(asset_path, "Jaw - Realistic")

counts = (len(jaw_source.data.vertices), len(jaw_source.data.polygons))
print("JAW_SOURCE_COUNTS", counts, list(jaw_source.data.uv_layers.keys()))
if counts != (5294, 5058):
    raise RuntimeError("Version de l'asset dentaire inattendue")
if "UVMap" not in jaw_source.data.uv_layers:
    raise RuntimeError("UVMap absente de l'asset dentaire")
```

Résultat visuel attendu : un seul nouvel objet apparaît, souvent loin d’Atlas.
Ne tente pas encore de l’aligner.

11.2 — Séparer par coques connexes

Dans l’interface :

1. sélectionne Jaw - Realistic en Object Mode ;
2. passe en Edit Mode ;
3. sélectionne tout avec A ;
4. fais P → Separate → By Loose Parts ;
5. reviens en Object Mode ;
6. dans l’Outliner, mets les objets nouvellement créés dans une collection
ORAL_SOURCE_WORK.

Automatisation équivalente :

```python
def separate_loose_parts(obj):
    before = set(bpy.data.objects)
    set_active(obj, "EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    created = [o for o in set(bpy.data.objects) - before if o.type == "MESH"]
    # L'objet d'origine est l'une des coques et n'est pas dans `created`.
    selected = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    parts = list({o.name: o for o in created + selected + [obj]}.values())
    return parts

parts = separate_loose_parts(jaw_source)
teeth = [o for o in parts if len(o.data.vertices) == 105]
shells = [o for o in parts if len(o.data.vertices) != 105]
print("ORAL_PARTS", len(parts), "TEETH", len(teeth),
      "SHELLS", [(o.name, len(o.data.vertices)) for o in shells])
if len(parts) != 29 or len(teeth) != 28 or len(shells) != 1:
    raise RuntimeError("Séparation attendue : 28 dents + 1 coque")
if len(shells[0].data.vertices) != 2354:
    raise RuntimeError("Coque principale inattendue")
shells[0].name = "GEO_jaw_shell_SOURCE_UNCLASSIFIED"
```

11.3 — Former les deux arcades sans perdre le split 14/14

1. cache la coque principale avec l’icône œil de l’Outliner ;
2. cadre les 28 dents avec Home ;
3. passe en vue orthographique correspondant à l’axe vertical documenté de
l’asset source ;
4. active X-Ray avec Alt+Z ;
5. sélectionne par boîte les 14 dents de la rangée supérieure ;
6. vérifie dans la barre d’état que 14 objets sont sélectionnés ;
7. Ctrl+J les joint, puis renomme l’objet GEO_teeth_upper ;
8. sélectionne les 14 autres, Ctrl+J, renomme GEO_teeth_lower ;
9. réaffiche la coque et renomme-la seulement après inspection. Si ses faces
sont bien des gencives utilisables, sépare-les en GEO_gums_upper et
GEO_gums_lower. Sinon, laisse-la cachée et construis les gencives à l’étape
13.

Test immédiat : sélectionne GEO_teeth_upper, passe en Edit Mode, survole une
dent et appuie L. Une dent seulement doit être sélectionnée. Répète sur trois
dents, puis vérifie Select → Select All by Trait → Loose Geometry sans modifier
le maillage. Chaque arcade doit contenir exactement 14 composantes.

Ce helper compte les composantes sans les séparer :

```python
def connected_component_sizes(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen = set(range(len(mesh.vertices)))
    sizes = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbour in adjacency[current]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        sizes.append(size)
    return sorted(sizes)

for name in ("GEO_teeth_upper", "GEO_teeth_lower"):
    obj = require_object(name, "MESH")
    sizes = connected_component_sizes(obj.data)
    print(name, sizes)
    if sizes != [105] * 14:
        raise RuntimeError(f"Arcade incorrecte : {name}")
```

12. Recaler les arcades par mesure

12.1 — Utiliser un seul transform commun

Crée un Empty d’alignement :

1. Object Mode → Shift+A → Empty → Plain Axes ;
2. renomme-le ALIGN_oral_source_to_atlas ;
3. sélectionne les deux arcades et les gencives source éventuelles ;
4. sélectionne l’Empty en dernier ;
5. Ctrl+P → Object (Keep Transform) ;
6. ne transforme ensuite que l’Empty.

Dans quatre vues synchronisées, ajuste dans cet ordre :

1. translation X pour aligner la ligne médiane sur X = 1.462567 m ;
2. rotation pour rendre le plan occlusal cohérent avec la bouche ;
3. échelle uniforme uniquement ;
4. translation Y pour placer les incisives derrière les lèvres ;
5. translation Z pour placer l’arcade supérieure sous le palais ;
6. contrôle de l’arcade inférieure contre la mandibule.

Utilise N → Item → Transform et entre les nombres au clavier. Ne valide pas un
recalage fait seulement à la souris en perspective.

12.2 — Contrôler en coupe

1. passe en vue latérale orthographique ;
2. active X-Ray ou utilise un plan de coupe ;
3. affiche la peau en matériau semi-transparent et les dents dans une couleur
vive ;
4. vérifie que les incisives supérieures sont au moins 0,50 mm derrière
l’enveloppe intérieure de la lèvre ;
5. vérifie au moins 0,20 mm entre palais et couronnes hors contact voulu ;
6. au neutre, cherche une clearance postérieure de 0,05 à 0,75 mm de chaque
côté ;
7. aucune dent ne doit traverser la peau ou une autre dent.

Quand le placement est validé, publie le transform exact :

```python
align = require_object("ALIGN_oral_source_to_atlas", "EMPTY")
if max(abs(align.scale[i] - align.scale[0]) for i in range(3)) > 1e-6:
    raise RuntimeError("Le recalage dentaire doit utiliser une échelle uniforme")

oral_config_path = ROOT / "config/oral-build.json"
config = json.loads(oral_config_path.read_text(encoding="utf-8")) \
    if oral_config_path.exists() else {}
config["dental_alignment_matrix_world"] = [
    [float(align.matrix_world[r][c]) for c in range(4)] for r in range(4)
]
oral_config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
print("DENTAL_ALIGNMENT_SAVED", oral_config_path)
```

12.3 — Figer le placement dans la copie F2

Après avoir sauvegardé la matrice :

1. sélectionne chaque arcade et gencive ;
2. Alt+P → Clear Parent (Keep Transform) ;
3. pour chacune, Object → Apply → All Transforms ;
4. vérifie Location 0,0,0, Rotation 0,0,0, Scale 1,1,1 ;
5. supprime uniquement l’Empty ALIGN_oral_source_to_atlas ;
6. compare la position avant/après : elle ne doit pas changer visuellement.

13. Lier rigidement les dents et construire les gencives si nécessaire

13.1 — Skinning rigide des arcades

```python
rig = require_object(RIG, "ARMATURE")
for object_name, bone_name in (
    ("GEO_teeth_upper", "DEF_head"),
    ("GEO_teeth_lower", "DEF_jaw"),
    ("GEO_gums_upper", "DEF_head"),
    ("GEO_gums_lower", "DEF_jaw"),
):
    obj = bpy.data.objects.get(object_name)
    if obj:
        rigid_bind(obj, rig, bone_name)
print("ATLAS_DENTAL_BIND_OK")
```

Test immédiat : CTRL_jaw.open = 1. L’arcade inférieure doit suivre exactement
la mandibule ; l’arcade supérieure ne bouge pas. Mesure la distance entre deux
molaires d’une même arcade avant/après : variation maximale 0,01 mm. Remets
open = 0.

13.2 — Ne créer des gencives que si elles sont visibles

Si la coque source couvre proprement les collets, sépare-la en deux objets et
utilise-la. Sinon :

1. sélectionne une arcade, Tab vers Edit Mode ;
2. Alt+Clic sélectionne une boucle cervicale fermée autour des collets ;
3. fais Shift+D, puis clic droit pour laisser la copie exactement en place ;
4. fais P → Selection, reviens en Object Mode et sélectionne le nouvel objet
de boucle ;
5. passe ce nouvel objet en Edit Mode ;
6. extrude-la de 2 à 4 mm vers la base de l’arcade avec E ;
7. si tu pars de deux anneaux distincts, sélectionne-les puis
Edge → Bridge Edge Loops ;
8. ajoute un modifier Solidify, Thickness = 0.0015 m, Offset = -1 comme
point de départ ;
9. applique le modifier uniquement sur cette nouvelle gencive sans shape key ;
10. ferme les extrémités avec des quads, évite les n-gons concaves ;
11. A, puis Mesh → Normals → Recalculate Outside ;
12. utilise Select → Select All by Trait → Non-Manifold. Rien ne doit être
sélectionné ;
13. mesure au moins 0,8 mm d’épaisseur et au plus 0,20 mm de gap visible au
collet ;
14. nomme GEO_gums_upper ou GEO_gums_lower, puis applique le skinning rigide
correspondant.

Teste la gencive à jaw = 0, 0.625, 1. Si elle traverse une couronne, corrige la
géométrie de la gencive, pas le transform de toute l’arcade.

14. Placer les landmarks et générer une langue volumique

14.1 — Placer six Empty de mesure

Dans Object Mode, utilise Shift+A → Empty → Plain Axes et crée :

```text
LM_tongue_base
LM_tongue_tip
LM_tongue_left_molar
LM_tongue_right_molar
LM_tongue_floor
LM_tongue_palate
```

Place-les dans une coupe sagittale et une vue du dessus :

• base : racine visible de la langue, derrière le corps ;
• tip : pointe neutre, derrière les incisives inférieures ;
• left/right_molar : largeur disponible entre les arcades ;
• floor : plancher buccal ;
• palate : point le plus proche du palais au-dessus du corps.

Utilise le panneau N → Item pour lire les coordonnées. La pointe doit rester
contenue au neutre et la ligne base→pointe doit aller globalement vers -Y.

```python
landmark_names = (
    "LM_tongue_base", "LM_tongue_tip", "LM_tongue_left_molar",
    "LM_tongue_right_molar", "LM_tongue_floor", "LM_tongue_palate",
)
landmarks = {name: list(require_object(name).matrix_world.translation)
             for name in landmark_names}
config_path = ROOT / "config/oral-build.json"
config = json.loads(config_path.read_text(encoding="utf-8")) \
    if config_path.exists() else {}
config["tongue_landmarks_world"] = landmarks
config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
print("TONGUE_LANDMARKS_SAVED", landmarks)
```

14.2 — Générer 13 × 7 sections, dessus et dessous

Le générateur ci-dessous produit un volume fermé. Les paramètres sont des
valeurs initiales ; inspecte le résultat dans Atlas avant de les signer.

```python
def build_tongue_from_landmarks(config_path):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    lm = {k: Vector(v) for k, v in config["tongue_landmarks_world"].items()}
    base = lm["LM_tongue_base"]
    tip = lm["LM_tongue_tip"]
    width_available = (lm["LM_tongue_left_molar"]
                       - lm["LM_tongue_right_molar"]).length
    palate_clearance = max(0.004, lm["LM_tongue_palate"].z - base.z)
    floor_z = lm["LM_tongue_floor"].z

    sections = 13
    columns = 7
    vertices = []
    faces = []

    def top_index(i, j):
        return i * columns + j

    def bottom_index(i, j):
        return sections * columns + i * columns + j

    for underside in (False, True):
        for i in range(sections):
            u = i / (sections - 1)
            center = base.lerp(tip, u)
            # Corps plus large, pointe arrondie à 2–4 mm de rayon.
            body_factor = math.sin(math.pi * min(1.0, u * 0.92)) ** 0.65
            half_width = max(0.003, 0.42 * width_available *
                             (0.45 + 0.55 * body_factor) * (1.0 - 0.72 * u**5))
            thickness = 0.008 + 0.007 * (1.0 - u)
            arch = min(0.006, 0.35 * palate_clearance) * math.sin(math.pi * u)
            for j in range(columns):
                s = -1.0 + 2.0 * j / (columns - 1)
                z_arch = arch * (1.0 - s * s)
                z = center.z + z_arch
                if underside:
                    z = max(floor_z + 0.001, z - thickness * (0.70 + 0.30 * (1-s*s)))
                vertices.append((center.x + s * half_width, center.y, z))

    for i in range(sections - 1):
        for j in range(columns - 1):
            a, b = top_index(i, j), top_index(i + 1, j)
            c, d = top_index(i + 1, j + 1), top_index(i, j + 1)
            faces.append((a, b, c, d))
            a, b = bottom_index(i, j), bottom_index(i, j + 1)
            c, d = bottom_index(i + 1, j + 1), bottom_index(i + 1, j)
            faces.append((a, b, c, d))

    for i in range(sections - 1):
        # Flanc gauche et flanc droit.
        faces.append((top_index(i, 0), bottom_index(i, 0),
                      bottom_index(i + 1, 0), top_index(i + 1, 0)))
        j = columns - 1
        faces.append((top_index(i, j), top_index(i + 1, j),
                      bottom_index(i + 1, j), bottom_index(i, j)))

    for j in range(columns - 1):
        # Cap base.
        faces.append((top_index(0, j + 1), top_index(0, j),
                      bottom_index(0, j), bottom_index(0, j + 1)))
        # Cap pointe.
        i = sections - 1
        faces.append((top_index(i, j), top_index(i, j + 1),
                      bottom_index(i, j + 1), bottom_index(i, j)))

    old = bpy.data.objects.get("GEO_tongue")
    if old:
        raise RuntimeError("GEO_tongue existe déjà ; ne pas l'écraser silencieusement")
    mesh = bpy.data.meshes.new("GEO_tongue_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new("GEO_tongue", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = True

    set_active(obj, "EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj, sections, columns

tongue, TONGUE_SECTIONS, TONGUE_COLUMNS = build_tongue_from_landmarks(
    ROOT / "config/oral-build.json")
print("ATLAS_TONGUE_CREATED", len(tongue.data.vertices),
      len(tongue.data.polygons))
```

Résultat attendu : une langue fermée et épaisse, non une plane. Elle reste sous
le palais, au-dessus du plancher et derrière les incisives. Si elle dépasse,
replace d’abord les landmarks, supprime seulement GEO_tongue, puis régénère.

Dans Edit Mode, lance Select → Select All by Trait → Non-Manifold. Zéro
arête doit être sélectionnée. Utilise Mesh → Clean Up → Degenerate Dissolve
uniquement si le rapport signale une face dégénérée, puis régénère le verrou de
la langue.

15. Créer les os et contrôles de langue

15.1 — Ajouter la chaîne dans l’armature existante

```python
config = json.loads((ROOT / "config/oral-build.json").read_text(encoding="utf-8"))
lm = {k: Vector(v) for k, v in config["tongue_landmarks_world"].items()}
rig = require_object(RIG, "ARMATURE")
base = rig.matrix_world.inverted() @ lm["LM_tongue_base"]
tip = rig.matrix_world.inverted() @ lm["LM_tongue_tip"]
body = base.lerp(tip, 0.58)

set_active(rig, "EDIT")
add_edit_bone(rig, "CTRL_tongue", base, body, "DEF_jaw")
add_edit_bone(rig, "CTRL_tongue_tip", body, tip, "CTRL_tongue")
add_edit_bone(rig, "MCH_tongue_base", base, body, "DEF_jaw")
add_edit_bone(rig, "DEF_tongue_base", base, body, "MCH_tongue_base", True)
add_edit_bone(rig, "DEF_tongue_body", body, body.lerp(tip, 0.62),
              "DEF_tongue_base", True)
add_edit_bone(rig, "DEF_tongue_tip", body.lerp(tip, 0.62), tip,
              "DEF_tongue_body", True)
bpy.ops.object.mode_set(mode="OBJECT")

for name in ("CTRL_tongue", "CTRL_tongue_tip"):
    rig.data.collections["CONTROLS"].assign(rig.data.bones[name])
for name in ("MCH_tongue_base",):
    rig.data.collections["MECHANISMS"].assign(rig.data.bones[name])
for name in ("DEF_tongue_base", "DEF_tongue_body", "DEF_tongue_tip"):
    rig.data.collections["DEFORM"].assign(rig.data.bones[name])
print("ATLAS_TONGUE_BONES_OK")
```

15.2 — Distribuer la rotation du contrôle sur la chaîne

Le contrôle principal déplace la base et répartit sa rotation : 35 % à la base,
65 % au corps. Le contrôle pointe ajoute une flexion locale.

```python
def copy_constraint(pb, constraint_type, name, target_bone, influence=1.0):
    constraint = pb.constraints.new(constraint_type)
    constraint.name = name
    constraint.target = rig
    constraint.subtarget = target_bone
    constraint.owner_space = "LOCAL"
    constraint.target_space = "LOCAL"
    constraint.influence = influence
    return constraint

rig = require_object(RIG, "ARMATURE")
for bone_name in ("MCH_tongue_base", "DEF_tongue_body", "DEF_tongue_tip",
                  "CTRL_tongue", "CTRL_tongue_tip"):
    for constraint in list(rig.pose.bones[bone_name].constraints):
        if constraint.name.startswith("ATLAS_"):
            rig.pose.bones[bone_name].constraints.remove(constraint)

copy_constraint(rig.pose.bones["MCH_tongue_base"], "COPY_LOCATION",
                "ATLAS_CopyTongueLocation", "CTRL_tongue", 1.0)
copy_constraint(rig.pose.bones["MCH_tongue_base"], "COPY_ROTATION",
                "ATLAS_CopyTongueBaseRotation", "CTRL_tongue", 0.35)
copy_constraint(rig.pose.bones["DEF_tongue_body"], "COPY_ROTATION",
                "ATLAS_CopyTongueBodyRotation", "CTRL_tongue", 0.65)
copy_constraint(rig.pose.bones["DEF_tongue_tip"], "COPY_ROTATION",
                "ATLAS_CopyTongueTipRotation", "CTRL_tongue_tip", 1.0)

main_limit = rig.pose.bones["CTRL_tongue"].constraints.new("LIMIT_ROTATION")
main_limit.name = "ATLAS_TongueMainLimit"
main_limit.owner_space = "LOCAL"
main_limit.use_limit_x = True
main_limit.min_x, main_limit.max_x = map(math.radians, (-15.0, 15.0))
main_limit.use_limit_z = True
main_limit.min_z, main_limit.max_z = map(math.radians, (-12.0, 12.0))
main_limit.use_limit_y = True
main_limit.min_y = main_limit.max_y = 0.0

tip_limit = rig.pose.bones["CTRL_tongue_tip"].constraints.new("LIMIT_ROTATION")
tip_limit.name = "ATLAS_TongueTipLimit"
tip_limit.owner_space = "LOCAL"
tip_limit.use_limit_x = True
tip_limit.min_x, tip_limit.max_x = map(math.radians, (-25.0, 25.0))
tip_limit.use_limit_z = True
tip_limit.min_z, tip_limit.max_z = map(math.radians, (-20.0, 20.0))
tip_limit.use_limit_y = True
tip_limit.min_y = tip_limit.max_y = 0.0

main_location = rig.pose.bones["CTRL_tongue"].constraints.new("LIMIT_LOCATION")
main_location.name = "ATLAS_TongueAdvanceLimit"
main_location.owner_space = "LOCAL"
main_location.use_min_x = main_location.use_max_x = True
main_location.min_x = main_location.max_x = 0.0
main_location.use_min_y = main_location.use_max_y = True
main_location.min_y, main_location.max_y = -0.008, 0.008
main_location.use_min_z = main_location.use_max_z = True
main_location.min_z = main_location.max_z = 0.0

tip_location = rig.pose.bones["CTRL_tongue_tip"].constraints.new("LIMIT_LOCATION")
tip_location.name = "ATLAS_TongueTipLocationLock"
tip_location.owner_space = "LOCAL"
for axis in "xyz":
    setattr(tip_location, "use_min_" + axis, True)
    setattr(tip_location, "use_max_" + axis, True)
    setattr(tip_location, "min_" + axis, 0.0)
    setattr(tip_location, "max_" + axis, 0.0)
print("ATLAS_TONGUE_CONSTRAINTS_OK")
```

Dans Pose Mode, le contrôle principal peut se déplacer de ±8 mm le long de
son axe avant/arrière et tourner jusqu’aux limites ci-dessus. Si son axe local Y
ne suit pas base→pointe, corrige le roll en Edit Mode avant de poursuivre.

15.3 — Peindre les trois zones de poids par section

```python
def smoothstep(edge0, edge1, x):
    t = min(max((x - edge0) / (edge1 - edge0), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)

def install_tongue_weights(obj, rig, sections=13, columns=7):
    groups = {name: reset_group(obj, name) for name in (
        "DEF_tongue_base", "DEF_tongue_body", "DEF_tongue_tip")}
    layer_size = sections * columns
    if len(obj.data.vertices) != 2 * layer_size:
        raise RuntimeError("Topologie de langue différente du générateur 13×7×2")
    for vertex_index in range(len(obj.data.vertices)):
        within_layer = vertex_index % layer_size
        section = within_layer // columns
        u = section / (sections - 1)
        base_weight = 1.0 - smoothstep(0.00, 0.45, u)
        tip_weight = smoothstep(0.62, 1.00, u)
        body_weight = max(0.0, 1.0 - base_weight - tip_weight)
        total = base_weight + body_weight + tip_weight
        for name, weight in (
            ("DEF_tongue_base", base_weight / total),
            ("DEF_tongue_body", body_weight / total),
            ("DEF_tongue_tip", tip_weight / total),
        ):
            if weight > 1e-6:
                groups[name].add([vertex_index], weight, "REPLACE")
    ensure_armature_modifier(obj, rig)

tongue = require_object("GEO_tongue", "MESH")
install_tongue_weights(tongue, rig)
print("ATLAS_TONGUE_WEIGHTS_OK")
```

Inspecte successivement les groupes en Weight Paint Mode. La racine est rouge
pour DEF_tongue_base, le milieu pour DEF_tongue_body, la pointe pour
DEF_tongue_tip; les transitions sont continues et la somme vaut 1.

16. Tester et sauvegarder F2

Teste exactement ces poses en affichant dents, gencives, langue et peau :

```text
neutral
jaw_20
jaw_32
tongue_up
tongue_down
tongue_left
tongue_right
tongue_out
tongue_tip_up
```

Pour chacune :

1. vérifie la coupe sagittale ;
2. vérifie la vue intérieure de la bouche ;
3. recherche une sortie par la joue ou le palais ;
4. recherche une collision langue/dent ;
5. vérifie que la racine ne se détache pas du plancher ;
6. remets tous les contrôles à zéro avant de passer à la pose suivante.

Le retour au neutre se teste numériquement :

```python
rig = require_object(RIG, "ARMATURE")
rig.pose.bones["CTRL_jaw"]["open"] = 0.0
for name in ("CTRL_tongue", "CTRL_tongue_tip"):
    pb = rig.pose.bones[name]
    pb.location = Vector((0, 0, 0))
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = Vector((0, 0, 0))
    pb.scale = Vector((1, 1, 1))
bpy.context.view_layer.update()

for name in ("GEO_teeth_upper", "GEO_teeth_lower", "GEO_tongue"):
    obj = require_object(name, "MESH")
    for vertex in obj.data.vertices:
        total = sum(g.weight for g in vertex.groups)
        if abs(total - 1.0) > 1e-5:
            raise RuntimeError(f"{name} v{vertex.index}: somme poids {total}")
print("ATLAS_F2_NEUTRAL_AND_WEIGHTS_OK")
save_checkpoint("source/ATLAS_FACE_F2_ORAL.blend")
```

Puis :

```bash
blender -b source/ATLAS_FACE_F2_ORAL.blend --python tests/f2-oral.py -- --mode final --report reports/f2/registre.json
```

Ne commence pas les paupières tant que la langue sort de la cavité ou que les
arcades perdent leur rigidité.

────────

F3 — Construire blink, wide, squint et suivi du regard

17. Créer la copie F3 et neutraliser tous les contrôles

Ouvre source/ATLAS_FACE_F2_ORAL.blend, puis sauvegarde immédiatement sous
source/ATLAS_FACE_F3_EYELIDS.blend.

Avant toute shape key :

1. sélectionne RIG_Atlas_Face, passe en Pose Mode ;
2. mets CTRL_jaw.open = 0 ;
3. sélectionne tous les CTRL_* et fais Alt+G, Alt+R, Alt+S ;
4. passe en Object Mode ;
5. sélectionne GEO-head_animation_realistic ;
6. dans Modifiers, vérifie l’ordre Armature puis Multires ;
7. vérifie que Preserve Volume est décoché sur Armature ;
8. ne clique jamais Apply sur l’un de ces deux modifiers.

Capture la surface neutre évaluée avant les clés :

```python
head = require_object(HEAD, "MESH")
rig = require_object(RIG, "ARMATURE")
rig.pose.bones["CTRL_jaw"]["open"] = 0.0
for name in ("CTRL_gaze", "CTRL_eye_target.L", "CTRL_eye_target.R",
             "CTRL_tongue", "CTRL_tongue_tip"):
    if name in rig.pose.bones:
        pb = rig.pose.bones[name]
        pb.location = Vector((0, 0, 0))
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Vector((0, 0, 0))
        pb.scale = Vector((1, 1, 1))
bpy.context.view_layer.update()
F3_NEUTRAL_REFERENCE = evaluated_coords(head)
import numpy as np
neutral_reference_path = ROOT / "reports/f3/neutral-reference.npy"
neutral_reference_path.parent.mkdir(parents=True, exist_ok=True)
np.save(neutral_reference_path,
        np.asarray([tuple(co) for co in F3_NEUTRAL_REFERENCE], dtype=float))
print("F3_NEUTRAL_CAPTURED", len(F3_NEUTRAL_REFERENCE))
```

18. Ajouter les shape keys initiales sans toucher au Basis

Manipulation dans Blender

1. sélectionne la tête en Object Mode ;
2. ouvre Object Data Properties (triangle vert) ;
3. dans Shape Keys, clique + une première fois : Blender crée Basis ;
4. clique quatre fois de plus et renomme les clés :
SK_eyeBlink.L, SK_eyeBlink.R, SK_eyeWide.L, SK_eyeWide.R ;
5. laisse chaque Value = 0.000 ;
6. n’active pas Vertex Group sur ces clés ;
7. n’entre pas en Edit Mode sur Basis.

Code idempotent :

```python
def ensure_shape_key(obj, name):
    if obj.data.shape_keys is None:
        basis = obj.shape_key_add(name="Basis", from_mix=False)
        basis.interpolation = "KEY_LINEAR"
    key = obj.data.shape_keys.key_blocks.get(name)
    if key is None:
        key = obj.shape_key_add(name=name, from_mix=False)
    key.relative_key = obj.data.shape_keys.key_blocks["Basis"]
    key.value = 0.0
    key.slider_min = 0.0
    key.slider_max = 1.0
    return key

head = require_object(HEAD, "MESH")
for name in (
    "SK_eyeBlink.L", "SK_eyeBlink.R",
    "SK_eyeWide.L", "SK_eyeWide.R",
):
    ensure_shape_key(head, name)

count = len(head.data.vertices)
for key in head.data.shape_keys.key_blocks:
    if len(key.data) != count:
        raise RuntimeError(f"{key.name}: nombre de points incorrect")
    if key.name != "Basis" and key.relative_key.name != "Basis":
        raise RuntimeError(f"{key.name}: clé relative différente de Basis")
print("ATLAS_F3_KEYS_CREATED", list(head.data.shape_keys.key_blocks.keys()))
```

Test immédiat : mets chaque clé à 1 puis à 0. Comme elles sont encore vides, le
visage ne doit pas bouger. Une variation indique que la clé a été créée depuis
un mix actif : supprime seulement cette clé et recrée-la avec toutes les valeurs
à zéro.

19. Installer le workflow de sculpture détachée sûr sous 5.1.2

Avec Multires, ne sculpte pas directement la shape key dans le master. La voie
de production est : extraire une cage sans modifier, la sculpter, puis injecter
ses coordonnées dans le KeyBlock par indice.

Ajoute ces fonctions au texte atlas_f1_build.py :

```python
def sculpt_collection():
    collection = bpy.data.collections.get("SCULPT_TARGETS_AUTHOR")
    if collection is None:
        collection = bpy.data.collections.new("SCULPT_TARGETS_AUTHOR")
        bpy.context.scene.collection.children.link(collection)
    return collection

def local_coords_for_key(obj, key_name):
    key = obj.data.shape_keys.key_blocks[key_name]
    return [point.co.copy() for point in key.data]

def mixed_shape_coords(obj, key_names):
    keys = obj.data.shape_keys.key_blocks
    basis = keys["Basis"]
    coords = [point.co.copy() for point in basis.data]
    for key_name in key_names:
        key = keys[key_name]
        for index in range(len(coords)):
            coords[index] += key.data[index].co - basis.data[index].co
    return coords

def create_cage_target(obj, target_name, coords):
    if bpy.data.objects.get(target_name):
        raise RuntimeError(f"Cible déjà présente : {target_name}")
    if len(coords) != len(obj.data.vertices):
        raise RuntimeError("Coordonnées incompatibles avec la cage")
    mesh = bpy.data.meshes.new(target_name + "_MESH")
    edges = [tuple(edge.vertices) for edge in obj.data.edges]
    faces = [tuple(poly.vertices) for poly in obj.data.polygons]
    mesh.from_pydata([tuple(co) for co in coords], edges, faces)
    mesh.update()
    target = bpy.data.objects.new(target_name, mesh)
    sculpt_collection().objects.link(target)
    target.matrix_world = obj.matrix_world.copy()
    target.color = (0.18, 0.55, 1.0, 1.0)
    for material in obj.data.materials:
        target.data.materials.append(material)
    target["atlas_source_object"] = obj.name
    target["atlas_vertex_count"] = len(coords)
    return target

def create_target_from_key(obj, key_name):
    return create_cage_target(obj, "SCULPT__" + key_name,
                              local_coords_for_key(obj, key_name))

def target_coords_in_source_space(source, target):
    matrix = source.matrix_world.inverted() @ target.matrix_world
    return [matrix @ vertex.co for vertex in target.data.vertices]

def commit_target_to_key(source, target, key_name):
    if len(target.data.vertices) != len(source.data.vertices):
        raise RuntimeError("Le sculpt target a changé de topologie")
    key = ensure_shape_key(source, key_name)
    coords = target_coords_in_source_space(source, target)
    for index, co in enumerate(coords):
        key.data[index].co = co
    source.data.update()
    return key

def set_all_key_values_zero(obj):
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            if key.name != "Basis":
                key.value = 0.0

def inspect_key(obj, key_name, value=1.0):
    set_all_key_values_zero(obj)
    obj.data.shape_keys.key_blocks[key_name].value = value
    bpy.context.view_layer.update()

print("ATLAS_SCULPT_WORKFLOW_READY")
```

Lorsque tu crées une cible :

1. cache la tête master avec l’icône écran, mais garde les globes visibles ;
2. sélectionne SCULPT__… ;
3. passe en Sculpt Mode ;
4. désactive X Symmetry pour une clé .L ou .R ;
5. utilise principalement Grab, Smooth et Inflate avec une intensité
faible ;
6. ne fais jamais Voxel Remesh, Dyntopo, Subdivide ou Decimate ;
7. reviens en Object Mode, lance commit_target_to_key, puis cache la cible ;
8. réaffiche le master, mets la clé à 1 et inspecte le Multires évalué ;
9. conserve la cible cachée jusqu’au test final de la phase.

20. Construire le blink gauche depuis le delta F0

20.1 — Injecter le delta audité comme point de départ

```python
def read_index_deltas(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = (payload.get("deltas") or payload.get("vertices") or
           payload.get("index_to_delta"))
    if raw is None:
        raise RuntimeError(f"Aucune liste de deltas reconnue dans {path}")
    result = {}
    if isinstance(raw, dict):
        for index, delta in raw.items():
            result[int(index)] = Vector(delta)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                index = item.get("index", item.get("vertex"))
                delta = item.get("delta", item.get("xyz"))
            else:
                index, delta = item
            result[int(index)] = Vector(delta)
    else:
        raise RuntimeError("Format de deltas non pris en charge")
    return result

def apply_sparse_delta(obj, key_name, deltas):
    key = ensure_shape_key(obj, key_name)
    basis = obj.data.shape_keys.key_blocks["Basis"]
    for index, point in enumerate(key.data):
        point.co = basis.data[index].co
    for index, delta in deltas.items():
        if not 0 <= index < len(key.data):
            raise RuntimeError(f"Index hors cage : {index}")
        key.data[index].co = basis.data[index].co + delta
    obj.data.update()

head = require_object(HEAD, "MESH")
blink_l_path = ROOT / "reports/f0-final/deformations/blink_L.cage-delta.json"
apply_sparse_delta(head, "SK_eyeBlink.L", read_index_deltas(blink_l_path))
print("BLINK_L_PROTOTYPE_IMPORTED")
```

Mets SK_eyeBlink.L = 1. Le prototype doit fermer l’œil gauche sans toucher
l’œil droit. S’il déforme l’autre côté, arrête : la topologie ou les indices ne
correspondent pas au contrat F0.

20.2 — Sculpter le vrai blink sur une cage séparée

```python
set_all_key_values_zero(head)
blink_target = create_target_from_key(head, "SK_eyeBlink.L")
set_active(blink_target, "SCULPT")
```

Dans Sculpt Mode :

1. vue de face orthographique, avec la sclère L visible ;
2. le bord supérieur descend autour du globe, il ne se déplace pas en ligne
verticale dans le vide ;
3. le bord inférieur monte moins que le supérieur ;
4. fais se rejoindre les deux marges sur une ligne légèrement courbe ;
5. préserve les canthi interne et externe : déplace-les de moins de 0,25 mm ;
6. redistribue le volume du bord supérieur vers le pli, au lieu d’aplatir la
paupière ;
7. vérifie en profil que la paupière épouse la sphère sans entrer dans la
cornée ;
8. vérifie en trois-quarts que le nombre de boucles signé dans
F0_CONTRACT["anatomy_counts"]["eye_margin_loops"]["L"] reste régulier ;
9. utilise Smooth seulement sur les boucles secondaires, jamais jusqu’à
effacer la marge ;
10. reviens en Object Mode.

Injecte puis inspecte :

```python
commit_target_to_key(head, blink_target, "SK_eyeBlink.L")
blink_target.hide_set(True)
head.hide_set(False)
inspect_key(head, "SK_eyeBlink.L", 1.0)
print("BLINK_L_COMMITTED")
```

Résultat attendu à 100 % : aucune sclère visible, gap maximal des marges ≤
0,20 mm, aucune face inversée, volume de la paupière conservé. Fais aussi glisser
la valeur 0→1 : le gap doit diminuer sans se rouvrir.

21. Miroiter le blink par indices, pas par positions absolues

La carte miroir produite en F0-B doit être disponible et son SHA doit correspondre
au contrat F0. Lis toujours artifacts.mirror_map.path; ne reconstruis pas une
carte au plus proche après le gel.

```python
def load_mirror_indices(path, vertex_count):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = payload.get("mirror_indices", payload.get("map", payload))
    if isinstance(raw, dict):
        mapping = [int(raw[str(i)] if str(i) in raw else raw[i])
                   for i in range(vertex_count)]
    else:
        mapping = [int(v) for v in raw]
    if len(mapping) != vertex_count:
        raise RuntimeError("Carte miroir de taille incorrecte")
    if sorted(mapping) != list(range(vertex_count)):
        raise RuntimeError("Carte miroir non bijective")
    if any(mapping[mapping[i]] != i for i in range(vertex_count)):
        raise RuntimeError("Carte miroir non involutive")
    return mapping

def mirror_key_delta(obj, source_name, target_name, mapping):
    keys = obj.data.shape_keys.key_blocks
    source = keys[source_name]
    basis = keys["Basis"]
    target = ensure_shape_key(obj, target_name)
    for i in range(len(mapping)):
        j = mapping[i]
        delta = source.data[i].co - basis.data[i].co
        target.data[j].co = basis.data[j].co + Vector((-delta.x, delta.y, delta.z))
    obj.data.update()

mirror_ref = F0_CONTRACT["artifacts"]["mirror_map"]
mirror_path = require_file(mirror_ref["path"])
if hashlib.sha256(mirror_path.read_bytes()).hexdigest() != mirror_ref["sha256"]:
    raise RuntimeError("SHA carte miroir différent du contrat F0")
mirror_indices = load_mirror_indices(mirror_path, len(head.data.vertices))
mirror_key_delta(head, "SK_eyeBlink.L", "SK_eyeBlink.R", mirror_indices)
print("BLINK_R_MIRRORED")
```

Mets seulement SK_eyeBlink.R = 1. La base asymétrique du visage doit rester :
seul le delta est miroité. Compare les deux gaps et profils. Si le côté R
nécessite une adaptation anatomique, crée plus tard une clé ASYM_…; ne corrige
pas silencieusement le miroir dans SK_eyeBlink.R.

22. Sculpter eyeWide

Pour chaque côté, crée puis sculpte une cible :

```python
for side in ("L", "R"):
    name = f"SK_eyeWide.{side}"
    target_name = "SCULPT__" + name
    if bpy.data.objects.get(target_name) is None:
        create_target_from_key(head, name)
```

Travaille d’abord sur SCULPT__SK_eyeWide.L :

1. Object Mode, cache le master et sélectionne la cible ;
2. Sculpt Mode, symétrie X désactivée ;
3. remonte surtout la marge supérieure de 1 à 4 mm ;
4. abaisse très légèrement la marge inférieure ;
5. augmente l’ouverture verticale de 10 à 35 % par rapport au neutre ;
6. garde au moins 0,10 mm entre paupière et globe ;
7. ne tire pas le canthus comme une déchirure ;
8. repousse le volume vers le pli supérieur ;
9. reviens en Object Mode, commit la cible puis cache-la.

```python
wide_l_target = require_object("SCULPT__SK_eyeWide.L", "MESH")
commit_target_to_key(head, wide_l_target, "SK_eyeWide.L")
mirror_key_delta(head, "SK_eyeWide.L", "SK_eyeWide.R", mirror_indices)
wide_l_target.hide_set(True)
head.hide_set(False)
inspect_key(head, "SK_eyeWide.L", 1.0)
```

Inspecte face, profil et trois-quarts, puis teste R. Une clé wide ne doit jamais
déplacer le globe ni ouvrir la commissure externe comme une fente.

23. Construire un squint distinct du blink

Crée les clés :

```python
for name in ("SK_eyeSquint.L", "SK_eyeSquint.R"):
    ensure_shape_key(head, name)
```

Sur la cible gauche :

1. pars de Basis, pas du blink ;
2. monte la paupière inférieure de 0,5 à 3 mm ;
3. monte la joue haute de 0,5 à 4 mm ;
4. comprime légèrement le canthus externe ;
5. resserre l’ouverture de 15 à 55 %, mais laisse au moins 30 % de l’ouverture
neutre au centre ;
6. étale l’effet sur l’orbicularis, ne pince pas seulement deux sommets ;
7. garde 0,10 mm de clearance au globe ;
8. commit, puis miroir par indices.

```python
squint_target = create_target_from_key(head, "SK_eyeSquint.L")
# Sculpter SCULPT__SK_eyeSquint.L dans l'interface, puis exécuter :
# commit_target_to_key(head, squint_target, "SK_eyeSquint.L")
# mirror_key_delta(head, "SK_eyeSquint.L", "SK_eyeSquint.R", mirror_indices)
```

Test immédiat : compare côte à côte blink = 0.5 et squint = 1. Le squint doit
monter la joue et garder l’œil ouvert ; s’il ressemble à un blink faible,
reprends la cible.

24. Sculpter les quatre formes de suivi du regard

Ajoute :

```python
for side in ("L", "R"):
    ensure_shape_key(head, f"SK_lidLookUp.{side}")
    ensure_shape_key(head, f"SK_lidLookDown.{side}")
```

24.1 — Forme LookUp.L

1. mets toutes les shape keys à zéro ;
2. en Pose Mode, déplace CTRL_gaze jusqu’à la limite de regard haut F1 ;
3. reviens en Object Mode, garde les globes visibles ;
4. crée SCULPT__SK_lidLookUp.L depuis la clé vide ;
5. cache le master, passe la cible en Sculpt Mode ;
6. fais suivre à la paupière supérieure 20 à 55 % de la rotation apparente du
globe ;
7. laisse l’inférieure bouger peu ;
8. redistribue le pli et garde les canthi stables à 0,25 mm ;
9. vérifie la clearance globe ≥ 0,10 mm ;
10. commit la cible, puis remets CTRL_gaze au neutre.

24.2 — Forme LookDown.L

1. place le regard à la limite bas ;
2. crée une cible depuis la clé vide ;
3. descends partiellement la supérieure ;
4. laisse l’inférieure suivre légèrement sans entrer dans la cornée ;
5. préserve les canthi et le volume ;
6. commit, puis remets le regard au neutre.

Miroite ensuite les deltas vers R :

```python
mirror_key_delta(head, "SK_lidLookUp.L", "SK_lidLookUp.R", mirror_indices)
mirror_key_delta(head, "SK_lidLookDown.L", "SK_lidLookDown.R", mirror_indices)
```

24.3 — Brancher le follow sur la rotation réelle de l’œil

Commence par déterminer le signe de pitch : place le regard haut et observe
MCH_eye_track.L dans N → Item → Rotation. Dans le code ci-dessous,
up_sign = +1 signifie qu’un regard haut donne un X local positif ; mets -1
si Atlas donne le signe opposé.

```python
def add_transform_variable(driver, variable_name, rig, bone_name,
                           transform_type="ROT_X"):
    var = driver.variables.new()
    var.name = variable_name
    var.type = "TRANSFORMS"
    target = var.targets[0]
    target.id = rig
    target.bone_target = bone_name
    target.transform_type = transform_type
    target.transform_space = "LOCAL_SPACE"
    return var

def install_look_driver(key_block, rig, bone_name, expression):
    try:
        key_block.driver_remove("value")
    except (TypeError, RuntimeError):
        pass
    fcurve = key_block.driver_add("value")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = expression
    add_transform_variable(driver, "pitch", rig, bone_name, "ROT_X")
    return fcurve

rig = require_object(RIG, "ARMATURE")
keys = head.data.shape_keys.key_blocks
up_sign = 1.0  # remplacer par -1.0 si le test visuel donne un pitch haut négatif
up_limit = math.radians(25.0)
down_limit = math.radians(35.0)
for side in ("L", "R"):
    install_look_driver(
        keys[f"SK_lidLookUp.{side}"], rig, f"MCH_eye_track.{side}",
        f"min(max(({up_sign:.1f}*pitch)/{up_limit:.17g},0.0),1.0)")
    install_look_driver(
        keys[f"SK_lidLookDown.{side}"], rig, f"MCH_eye_track.{side}",
        f"min(max(({-up_sign:.1f}*pitch)/{down_limit:.17g},0.0),1.0)")

bpy.context.view_layer.update()
bad = [fc.data_path for fc in head.data.shape_keys.animation_data.drivers
       if not fc.driver.is_valid]
if bad:
    raise RuntimeError(f"Drivers de follow invalides : {bad}")
print("ATLAS_LID_FOLLOW_DRIVERS_OK")
```

Déplace lentement CTRL_gaze du bas vers le haut. Les deux valeurs de follow se
croisent à zéro au centre, une seule monte dans chaque direction et aucun saut
de marge ne dépasse 0,50 mm entre deux petits déplacements.

25. Créer les correctives blink × regard et blink × squint

Une corrective shape × shape contient seulement le résidu par rapport à A+B.
Le target de sculpture doit donc commencer sur la combinaison déjà active.

```python
def create_residual_sculpt_target(obj, corrective_name, source_names):
    ensure_shape_key(obj, corrective_name)
    coords = mixed_shape_coords(obj, source_names)
    target = create_cage_target(obj, "SCULPT__" + corrective_name, coords)
    target["atlas_residual_sources"] = json.dumps(list(source_names))
    return target

def commit_residual_target(obj, target, corrective_name, source_names):
    desired = target_coords_in_source_space(obj, target)
    current = mixed_shape_coords(obj, source_names)
    basis = obj.data.shape_keys.key_blocks["Basis"]
    corrective = ensure_shape_key(obj, corrective_name)
    for index in range(len(desired)):
        residual = desired[index] - current[index]
        corrective.data[index].co = basis.data[index].co + residual
    obj.data.update()
    return corrective

def add_key_value_variable(driver, variable_name, key_data, key_name):
    var = driver.variables.new()
    var.name = variable_name
    var.type = "SINGLE_PROP"
    target = var.targets[0]
    target.id = key_data
    target.data_path = f'key_blocks["{key_name}"].value'
    return var

def install_product_driver(obj, corrective_name, a_name, b_name):
    key = obj.data.shape_keys.key_blocks[corrective_name]
    try:
        key.driver_remove("value")
    except (TypeError, RuntimeError):
        pass
    fcurve = key.driver_add("value")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = "a*b"
    add_key_value_variable(driver, "a", obj.data.shape_keys, a_name)
    add_key_value_variable(driver, "b", obj.data.shape_keys, b_name)

corrective_specs = [
    ("CORR_blink_lookUp.L", "SK_eyeBlink.L", "SK_lidLookUp.L"),
    ("CORR_blink_lookUp.R", "SK_eyeBlink.R", "SK_lidLookUp.R"),
    ("CORR_blink_lookDown.L", "SK_eyeBlink.L", "SK_lidLookDown.L"),
    ("CORR_blink_lookDown.R", "SK_eyeBlink.R", "SK_lidLookDown.R"),
    ("CORR_blink_squint.L", "SK_eyeBlink.L", "SK_eyeSquint.L"),
    ("CORR_blink_squint.R", "SK_eyeBlink.R", "SK_eyeSquint.R"),
]
for corr, a, b in corrective_specs:
    ensure_shape_key(head, corr)
```

Pour chaque triplet, par exemple CORR_blink_lookUp.L :

1. place le regard en haut, de sorte que SK_lidLookUp.L = 1 via son driver ;
2. mets SK_eyeBlink.L = 1 ;
3. garde la corrective à zéro ;
4. crée la cible combinée :

```python
target = create_residual_sculpt_target(
    head, "CORR_blink_lookUp.L", ("SK_eyeBlink.L", "SK_lidLookUp.L"))
```

5. sur la cible, rétablis une fermeture propre autour du globe orienté ;
6. ne rescupte que le défaut de combinaison ;
7. commit le résidu :

```python
commit_residual_target(
    head, target, "CORR_blink_lookUp.L", ("SK_eyeBlink.L", "SK_lidLookUp.L"))
install_product_driver(
    head, "CORR_blink_lookUp.L", "SK_eyeBlink.L", "SK_lidLookUp.L")
```

8. vérifie que la corrective vaut 0 si blink=0 ou lookUp=0 ;
9. répète pour les six triplets ;
10. cache les targets, remets regard et clés manuelles au neutre.

26. Tester F3 sur tout l’intervalle, puis sauvegarder

Pour blink, wide et squint, déplace chaque valeur dans l’interface selon :

```text
0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
```

À chaque valeur regarde : gap, faces inversées, collision globe, canthi et côté
opposé. Ensuite teste :

```text
blink × centre
blink × haut
blink × bas
blink × dedans
blink × dehors
blink × squint
wide × haut
wide × bas
```

Le test neutre détecte une modification involontaire du Basis ou du Multires :

```python
set_all_key_values_zero(head)
rig.pose.bones["CTRL_jaw"]["open"] = 0.0
for name in ("CTRL_gaze", "CTRL_eye_target.L", "CTRL_eye_target.R"):
    rig.pose.bones[name].location = Vector((0, 0, 0))
bpy.context.view_layer.update()
neutral_now = evaluated_coords(head)
if "F3_NEUTRAL_REFERENCE" not in globals():
    import numpy as np
    F3_NEUTRAL_REFERENCE = [Vector(row) for row in np.load(
        ROOT / "reports/f3/neutral-reference.npy")]
neutral_error = max_coordinate_error_mm(F3_NEUTRAL_REFERENCE, neutral_now)
print("F3_NEUTRAL_ERROR_MM", neutral_error)
if neutral_error > 0.01:
    raise RuntimeError("Basis, pose neutre ou Multires ont changé pendant F3")

fingerprint_now = mesh_topology_fingerprint(head)
fingerprint_lock = json.loads(
    (ROOT / "tests/verrou-topologie-final.json").read_text(encoding="utf-8"))
if fingerprint_now["vertices"] != fingerprint_lock["vertices"] or \
   fingerprint_now["polygons"] != fingerprint_lock["polygons"]:
    raise RuntimeError("Topologie modifiée pendant F3")

bad_drivers = [fc.data_path for fc in head.data.shape_keys.animation_data.drivers
               if not fc.driver.is_valid]
if bad_drivers:
    raise RuntimeError(f"Drivers F3 invalides : {bad_drivers}")
print("ATLAS_F3_LOCAL_TESTS_OK")
save_checkpoint("source/ATLAS_FACE_F3_EYELIDS.blend")
```

Puis lance :

```bash
blender -b source/ATLAS_FACE_F3_EYELIDS.blend --python tests/f3-eyelids.py -- --mode final --report reports/f3/registre.json
```

En cas de blocage, recherche d’abord le symptôme exact :

```text
Blender 5 shape key sculpt Multires vertex order
Blender eyelid blink shape key eyeball collision
Blender eyelid follow Damped Track local rotation driver
Blender corrective shape key residual A B product driver
```

Compare ensuite avec les chapitres Eyelids Local Controls et Eyelids Follow
du cours Blender Studio Advanced Facial Rigging. Ne télécharge pas un rig pour
copier ses valeurs : reproduis le défaut sur une copie de cage Atlas.

────────

F4 — Construire les lèvres et les correctives de mâchoire

27. Dériver le fichier F4 et créer toutes les clés vides

Ouvre source/ATLAS_FACE_F3_EYELIDS.blend, neutralise la mâchoire, le regard,
la langue et toutes les valeurs manuelles, puis File → Save As… vers
source/ATLAS_FACE_F4_MOUTH.blend.

Dans Object Data Properties → Shape Keys, ajoute les clés suivantes. Tu peux
le faire avec +, mais le script évite une faute de nom :

```python
MOUTH_KEYS = (
    "SK_mouthClose",
    "SK_mouthUpperUp.L", "SK_mouthUpperUp.R",
    "SK_mouthLowerDown.L", "SK_mouthLowerDown.R",
    "SK_mouthSmile.L", "SK_mouthSmile.R",
    "SK_mouthFrown.L", "SK_mouthFrown.R",
    "SK_mouthStretch.L", "SK_mouthStretch.R",
    "SK_mouthPucker", "SK_mouthFunnel",
    "SK_mouthPress.L", "SK_mouthPress.R",
    "SK_mouthTighten.L", "SK_mouthTighten.R",
    "SK_mouthPart",
    "SK_mouthRollUpper", "SK_mouthRollLower",
    "SK_mouthShrugUpper", "SK_mouthShrugLower",
    "SK_mouthDimple.L", "SK_mouthDimple.R",
)

head = require_object(HEAD, "MESH")
set_all_key_values_zero(head)
for name in MOUTH_KEYS:
    ensure_shape_key(head, name)
print("ATLAS_F4_EMPTY_KEYS_OK", len(MOUTH_KEYS))
```

Dans l’interface, mets trois clés au hasard à 1, une par une. Le visage ne doit
pas encore bouger. Si une clé contient un mix des paupières, elle a été créée
avec from_mix=True ou avec une pose active : supprime cette clé seule, remets
tout à zéro et recrée-la.

28. Préparer les vues et la méthode de sculpture des lèvres

Avant chaque forme :

1. Object Mode, tête sélectionnée ;
2. toutes les autres shape keys à zéro ;
3. mâchoire au neutre sauf instruction contraire ;
4. affiche GEO_teeth_upper, GEO_teeth_lower, les gencives et la langue ;
5. garde une vue de face orthographique, une vue profil et une vue trois-quarts ;
6. crée une cible avec create_target_from_key(head, NOM_DE_CLE) ;
7. cache la tête master, sélectionne la cible, Sculpt Mode ;
8. désactive X Symmetry pour .L/.R, active-la uniquement pour une forme
bilatérale axiale telle que pucker ;
9. commence avec Grab sur la marge, rayon limité aux deux premières boucles ;
10. élargis ensuite le rayon pour redistribuer le volume jusqu’aux boucles 2–5 ;
11. vérifie les dents avant de valider ;
12. ne lance jamais Dyntopo, Voxel Remesh ou une subdivision ;
13. Object Mode, commit, cache la cible, réaffiche la tête ;
14. teste 0/0,25/0,50/0,75/1 avant la forme suivante.

Ce helper mesure l’amplitude maximale d’une clé et détecte une clé vide ou
démesurée :

```python
def key_max_delta_mm(obj, key_name):
    keys = obj.data.shape_keys.key_blocks
    basis = keys["Basis"]
    key = keys[key_name]
    return 1000.0 * max((key.data[i].co - basis.data[i].co).length
                        for i in range(len(basis.data)))

def print_mouth_amplitudes(obj):
    result = {name: key_max_delta_mm(obj, name) for name in MOUTH_KEYS}
    for name, value in result.items():
        print("MOUTH_AMPLITUDE_MM", name, value)
    return result

def begin_mouth_sculpt(obj, key_name):
    set_all_key_values_zero(obj)
    target_name = "SCULPT__" + key_name
    target = bpy.data.objects.get(target_name)
    if target is None:
        target = create_target_from_key(obj, key_name)
    obj.hide_set(True)
    target.hide_set(False)
    set_active(target, "SCULPT")
    return target

def finish_mouth_sculpt(obj, key_name, mirror_to=None, mirror_map=None):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    target = require_object("SCULPT__" + key_name, "MESH")
    commit_target_to_key(obj, target, key_name)
    if mirror_to:
        if mirror_map is None:
            raise RuntimeError("Carte miroir requise")
        mirror_key_delta(obj, key_name, mirror_to, mirror_map)
    target.hide_set(True)
    obj.hide_set(False)
    inspect_key(obj, key_name, 1.0)
    return key_max_delta_mm(obj, key_name)
```

Pour chaque forme ci-dessous, « crée la cible » signifie exécuter
begin_mouth_sculpt(head, "NOM_DE_CLE"). « Commit » signifie exécuter
finish_mouth_sculpt(head, "NOM_DE_CLE"). Pour une clé gauche à miroiter,
utilise finish_mouth_sculpt(head, "NOM.L", "NOM.R", mirror_indices). Ces deux
fonctions imposent le bon mode, le bon objet et le retour visuel sur le master.

29. Construire SK_mouthClose

29.1 — Importer la fermeture F0 comme point de départ

```python
mouth_close_path = ROOT / "reports/f0-final/deformations/mouth_close.cage-delta.json"
apply_sparse_delta(head, "SK_mouthClose", read_index_deltas(mouth_close_path))
inspect_key(head, "SK_mouthClose", 1.0)
```

Le côté supérieur et le côté inférieur doivent déjà se rapprocher. Si la bouche
part latéralement ou si les indices touchent le nez, arrête : le delta vient
d’une autre topologie.

29.2 — Finir la fermeture sur la cage détachée

```python
set_all_key_values_zero(head)
close_target = create_target_from_key(head, "SK_mouthClose")
set_active(close_target, "SCULPT")
```

Dans Sculpt Mode :

1. vue de face, rapproche chaque paire de marge signée en F0 ;
2. vise un gap final ≤ 0,30 mm, pas une interpenetration ;
3. la lèvre supérieure descend légèrement, l’inférieure monte légèrement ;
4. conserve l’épaisseur du vermillon : si la couture devient une lame, utilise
Inflate très faiblement sur les volumes, pas sur la ligne de contact ;
5. garde les commissures fermées mais non écrasées ;
6. en profil, les lèvres restent devant les incisives ;
7. en coupe sagittale, aucune lèvre ne traverse une dent ;
8. l’activation ne doit pas déplacer le menton ni le nez ;
9. reviens en Object Mode et commit.

```python
commit_target_to_key(head, close_target, "SK_mouthClose")
close_target.hide_set(True)
head.hide_set(False)
inspect_key(head, "SK_mouthClose", 1.0)
print("MOUTH_CLOSE_MAX_DELTA_MM", key_max_delta_mm(head, "SK_mouthClose"))
```

Fais glisser la clé lentement de 0 à 1. Le gap doit diminuer de façon monotone.
Remets la clé à zéro et sauvegarde.

30. Construire sourire, frown, stretch et dimple

30.1 — Sourire gauche

Crée SCULPT__SK_mouthSmile.L. Dans Sculpt Mode :

1. déplace la commissure L de 4 à 12 mm, latéralement et vers le haut ;
2. dirige d’abord la marge, puis étale le mouvement dans la joue basse ;
3. creuse légèrement le sillon nasogénien sans entraîner tout le nez ;
4. garde le centre de la lèvre relativement stable ;
5. laisse apparaître progressivement les dents supérieures ;
6. conserve l’arrondi du vermillon ;
7. vérifie que le côté R ne bouge pas ;
8. commit la cible.

```python
smile_l_target = begin_mouth_sculpt(head, "SK_mouthSmile.L")
```

Après les huit gestes, exécute :

```python
finish_mouth_sculpt(head, "SK_mouthSmile.L",
                    "SK_mouthSmile.R", mirror_indices)
```

Après miroir, teste L seul, R seul, puis L+R. La joue haute/AU6 n’est pas incluse
ici : un sourire doit rester possible sans squint.

30.2 — Frown gauche

Sur SCULPT__SK_mouthFrown.L :

1. abaisse la commissure de 2 à 8 mm ;
2. ramène-la légèrement vers le centre ;
3. fais réagir localement le menton et le jowl ;
4. garde la lèvre supérieure centrale et le cou immobiles ;
5. ne transforme pas le frown en lowerDown : la commissure est le moteur ;
6. commit puis miroir vers R.

30.3 — Stretch gauche

Sur SCULPT__SK_mouthStretch.L :

1. tire la commissure horizontalement de 3 à 10 mm ;
2. ouvre légèrement la largeur de la couture sans monter comme un sourire ;
3. répartis la tension sur les boucles latérales ;
4. conserve l’épaisseur des lèvres au centre ;
5. commit puis miroir.

30.4 — Dimple gauche

Sur SCULPT__SK_mouthDimple.L :

1. tire une petite zone de commissure vers l’arrière et légèrement dehors ;
2. crée une indentation locale de joue, pas un second sourire ;
3. laisse le centre des lèvres inchangé ;
4. limite le delta au côté L ;
5. commit puis miroir.

Code de commit/mirror pour les trois formes :

```python
# Avant chaque sculpt, exécuter l'une de ces lignes, sculpter, puis seulement
# poursuivre avec la boucle de commit ci-dessous.
# begin_mouth_sculpt(head, "SK_mouthFrown.L")
# begin_mouth_sculpt(head, "SK_mouthStretch.L")
# begin_mouth_sculpt(head, "SK_mouthDimple.L")
for base_name in ("SK_mouthFrown", "SK_mouthStretch", "SK_mouthDimple"):
    target = require_object("SCULPT__" + base_name + ".L", "MESH")
    commit_target_to_key(head, target, base_name + ".L")
    mirror_key_delta(head, base_name + ".L", base_name + ".R", mirror_indices)
    target.hide_set(True)
head.hide_set(False)
```

Teste chacune à 0/25/50/75/100 %, puis les deux côtés ensemble. Pour une forme
unilatérale, le déplacement du côté opposé doit rester ≤ 0,01 mm.

31. Construire upperUp, lowerDown et mouthPart

31.1 — mouthUpperUp.L

1. crée une cible depuis Basis ;
2. remonte la marge supérieure L de 2 à 8 mm ;
3. expose les incisives supérieures ;
4. garde la commissure plus stable que dans smile ;
5. redistribue le philtrum sans tirer toute la narine ;
6. vérifie le nombre de triangles signé dans
F0_CONTRACT["anatomy_counts"]["mouth_region_triangles"] pour cette région ;
7. commit et miroir.

31.2 — mouthLowerDown.L

1. abaisse la marge inférieure L de 2 à 8 mm ;
2. expose les incisives inférieures ;
3. garde la commissure presque stable ;
4. accompagne légèrement le menton local, sans déplacer le cou ;
5. surveille les triangles sous la lèvre et les faces inversées ;
6. commit et miroir.

31.3 — mouthPart

mouthPart ouvre seulement les lèvres, sans rotation de mandibule :

1. active la symétrie X sur la cible ;
2. déplace légèrement la marge supérieure vers le haut et l’inférieure vers le
bas ;
3. vise un gap central de 1 à 5 mm ;
4. garde dents, menton et commissures presque immobiles ;
5. en profil, conserve l’épaisseur et la projection ;
6. commit, puis vérifie que DEF_jaw n’a pas bougé.

```python
for name in ("SK_mouthUpperUp.L", "SK_mouthLowerDown.L", "SK_mouthPart"):
    if bpy.data.objects.get("SCULPT__" + name) is None:
        create_target_from_key(head, name)
```

Active et sculpte une seule cible à la fois. Après chacune, exécute :

```python
finish_mouth_sculpt(head, "SK_mouthUpperUp.L",
                    "SK_mouthUpperUp.R", mirror_indices)
finish_mouth_sculpt(head, "SK_mouthLowerDown.L",
                    "SK_mouthLowerDown.R", mirror_indices)
finish_mouth_sculpt(head, "SK_mouthPart")
```

32. Construire pucker et funnel comme deux formes distinctes

32.1 — Pucker

Exécute begin_mouth_sculpt(head, "SK_mouthPucker"). Sur la cible active,
active la symétrie X :

1. ramène les deux commissures vers le centre ;
2. projette les lèvres de 3 à 10 mm vers l’avant du personnage (-Y) ;
3. réduit l’ouverture ;
4. forme un volume cylindrique d’orbicularis autour de la bouche ;
5. conserve l’épaisseur du vermillon ;
6. vérifie en profil que les dents ne traversent pas les lèvres ;
7. commit.

Exécute ensuite finish_mouth_sculpt(head, "SK_mouthPucker").

32.2 — Funnel

Exécute begin_mouth_sculpt(head, "SK_mouthFunnel"), puis sur la cible :

1. projette aussi les lèvres vers l’avant ;
2. crée cependant une ouverture ronde de 5 à 20 mm ;
3. ouvre les marges au lieu de les resserrer comme pucker ;
4. étale le volume sur les lèvres supérieure et inférieure ;
5. garde les commissures orientées vers le centre ;
6. vérifie la langue et les incisives visibles à travers l’ouverture ;
7. commit.

Exécute ensuite finish_mouth_sculpt(head, "SK_mouthFunnel").

Affiche ensuite pucker et funnel côte à côte. Si funnel ressemble simplement
à pucker = 0.5, reprends sa cible : la différence d’ouverture doit être visible
en face et en profil.

33. Construire press, tighten, roll et shrug

33.1 — Press gauche puis droit

Exécute begin_mouth_sculpt(head, "SK_mouthPress.L"), puis :

1. sur le côté L, presse les deux lèvres l’une contre l’autre ;
2. maintiens la couture fermée sans faire disparaître le volume ;
3. repousse le volume au-dessus et au-dessous de la ligne de contact ;
4. ne déplace pas la commissure comme smile ou frown ;
5. commit puis miroir.

Exécute finish_mouth_sculpt(head, "SK_mouthPress.L", "SK_mouthPress.R", mirror_indices).

33.2 — Tighten gauche puis droit

Exécute begin_mouth_sculpt(head, "SK_mouthTighten.L"), puis :

1. resserre horizontalement la marge autour de la commissure ;
2. amincis légèrement la ligne sans créer de face inversée ;
3. diffuse la tension sur l’orbicularis ;
4. garde la fermeture indépendante de press ;
5. commit puis miroir.

Exécute finish_mouth_sculpt(head, "SK_mouthTighten.L", "SK_mouthTighten.R", mirror_indices).

33.3 — Roll Upper et Roll Lower

Pour SK_mouthRollUpper :

1. exécute begin_mouth_sculpt(head, "SK_mouthRollUpper") ;
2. roule le vermillon supérieur vers l’intérieur de la bouche ;
3. conserve la ligne extérieure de peau ;
4. évite toute traversée des incisives ;
5. vérifie en coupe sagittale ;
6. exécute finish_mouth_sculpt(head, "SK_mouthRollUpper").

Répète séparément sur la lèvre inférieure avec
begin_mouth_sculpt(head, "SK_mouthRollLower"), puis
finish_mouth_sculpt(head, "SK_mouthRollLower"). Les deux clés doivent pouvoir
s’activer indépendamment et ensemble.

33.4 — Shrug Upper et Lower

Exécute begin_mouth_sculpt(head, "SK_mouthShrugUpper"), monte légèrement le
centre de la lèvre supérieure et projette-le, puis exécute
finish_mouth_sculpt(head, "SK_mouthShrugUpper"). Recommence avec
begin_mouth_sculpt(head, "SK_mouthShrugLower"), monte la lèvre inférieure vers
la supérieure sans bouger toute la mâchoire, puis exécute
finish_mouth_sculpt(head, "SK_mouthShrugLower"). Teste-les séparément.

Après cette série :

```python
amplitudes = print_mouth_amplitudes(head)
for name, amplitude in amplitudes.items():
    if amplitude <= 0.001:
        raise RuntimeError(f"Clé vide : {name}")
(ROOT / "config/mouth-amplitudes.json").write_text(
    json.dumps({"max_vertex_delta_mm": amplitudes}, indent=2),
    encoding="utf-8",
)
print("MOUTH_AMPLITUDES_SAVED")
```

Les amplitudes de landmarks priment sur le maximum global. Contrôle dans
l’interface que smile/frown/stretch/pucker/lowerDown/upperUp/mouthPart restent
dans les plages indiquées aux étapes précédentes.

34. Comprendre le problème des correctives jaw × shape

Une shape key est appliquée avant l’Armature modifier. Quand la mâchoire est
ouverte, le défaut est observé après skinning. On ne peut donc pas enregistrer
directement cible_posée − Basis dans une shape key : ce delta serait skinné une
seconde fois.

La procédure correcte est :

1. poser la mâchoire et activer la primitive ;
2. extraire la cage évaluée après Armature, Multires désactivé ;
3. sculpter le résultat désiré dans cet espace posé ;
4. calculer le résidu posé ;
5. pour chaque sommet, construire la matrice LBS pondérée réellement utilisée ;
6. inverser seulement sa partie linéaire ;
7. écrire le delta pré-skinning dans la corrective ;
8. réévaluer et comparer à la cible sculptée.

Cette méthode exige Armature → Preserve Volume décoché, aucun scale/shear dans
la chaîne et des poids de déformation normalisés. Elle n’est pas valide pour le
dual quaternion.

35. Installer les helpers de sculpture pose-space

35.1 — Extraire la cage évaluée sans Multires

```python
def modifiers_temporarily_disabled_after_armature(obj):
    armature_index = next(i for i, mod in enumerate(obj.modifiers)
                          if mod.type == "ARMATURE")
    states = {}
    for index, modifier in enumerate(obj.modifiers):
        states[modifier.name] = modifier.show_viewport
        if index > armature_index:
            modifier.show_viewport = False
    return states

def restore_modifier_states(obj, states):
    for name, state in states.items():
        modifier = obj.modifiers.get(name)
        if modifier:
            modifier.show_viewport = state

def evaluated_cage_coords(obj):
    states = modifiers_temporarily_disabled_after_armature(obj)
    try:
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(
            evaluated, preserve_all_data_layers=False, depsgraph=depsgraph)
        try:
            if len(mesh.vertices) != len(obj.data.vertices):
                raise RuntimeError("La pile avant Multires change la topologie")
            return [vertex.co.copy() for vertex in mesh.vertices]
        finally:
            bpy.data.meshes.remove(mesh)
    finally:
        restore_modifier_states(obj, states)
        bpy.context.view_layer.update()

def create_pose_sculpt_target(obj, corrective_name):
    coords = evaluated_cage_coords(obj)
    target = create_cage_target(obj, "SCULPTPOSE__" + corrective_name, coords)
    target["atlas_pose_corrective"] = corrective_name
    return target
```

35.2 — Construire la matrice LBS objet-local d’un os

```python
def deform_matrix_object_space(mesh_obj, rig_obj, bone_name):
    pose_bone = rig_obj.pose.bones[bone_name]
    rest_bone = rig_obj.data.bones[bone_name]
    object_from_armature = mesh_obj.matrix_world.inverted() @ rig_obj.matrix_world
    armature_from_object = rig_obj.matrix_world.inverted() @ mesh_obj.matrix_world
    deform_armature = pose_bone.matrix @ rest_bone.matrix_local.inverted()
    return object_from_armature @ deform_armature @ armature_from_object

def deform_weights_for_vertex(mesh_obj, rig_obj, vertex):
    result = []
    for assignment in vertex.groups:
        group = mesh_obj.vertex_groups[assignment.group]
        bone = rig_obj.data.bones.get(group.name)
        if bone and bone.use_deform and assignment.weight > 1e-8:
            result.append((group.name, float(assignment.weight)))
    total = sum(weight for _, weight in result)
    if abs(total - 1.0) > 1e-4:
        raise RuntimeError(f"v{vertex.index}: somme de poids déformants {total}")
    return [(name, weight / total) for name, weight in result]
```

35.3 — Ramener le résidu par l’inverse pondéré

```python
def commit_pose_space_corrective(mesh_obj, rig_obj, target, corrective_name,
                                 condition_limit=1e5):
    import numpy as np

    armature_modifier = next((m for m in mesh_obj.modifiers
                              if m.type == "ARMATURE" and m.object == rig_obj), None)
    if armature_modifier is None:
        raise RuntimeError("Armature modifier Atlas absent")
    if armature_modifier.use_deform_preserve_volume:
        raise RuntimeError("Inversion interdite avec Preserve Volume")
    if max(abs(scale - 1.0) for scale in rig_obj.scale) > 1e-6:
        raise RuntimeError("Scale armature non unitaire")
    if max(abs(scale - 1.0) for scale in mesh_obj.scale) > 1e-6:
        raise RuntimeError("Scale tête non unitaire")

    current_posed = evaluated_cage_coords(mesh_obj)
    desired_posed = target_coords_in_source_space(mesh_obj, target)
    if len(current_posed) != len(desired_posed):
        raise RuntimeError("Target pose-space de topologie différente")

    basis = mesh_obj.data.shape_keys.key_blocks["Basis"]
    corrective = ensure_shape_key(mesh_obj, corrective_name)
    bone_matrices = {
        bone.name: np.asarray(deform_matrix_object_space(
            mesh_obj, rig_obj, bone.name).to_3x3(), dtype=float)
        for bone in rig_obj.data.bones if bone.use_deform
    }

    worst_condition = 0.0
    for vertex in mesh_obj.data.vertices:
        weights = deform_weights_for_vertex(mesh_obj, rig_obj, vertex)
        linear = np.zeros((3, 3), dtype=float)
        for bone_name, weight in weights:
            linear += weight * bone_matrices[bone_name]
        condition = float(np.linalg.cond(linear))
        worst_condition = max(worst_condition, condition)
        if not np.isfinite(condition) or condition > condition_limit:
            raise RuntimeError(
                f"v{vertex.index}: matrice LBS mal conditionnée ({condition})")
        residual_posed = np.asarray(
            desired_posed[vertex.index] - current_posed[vertex.index],
            dtype=float,
        )
        residual_pre = np.linalg.solve(linear, residual_posed)
        corrective.data[vertex.index].co = (
            basis.data[vertex.index].co + Vector(residual_pre.tolist()))

    mesh_obj.data.update()
    print("POSE_CORRECTIVE_COMMITTED", corrective_name,
          "WORST_CONDITION", worst_condition)
    return corrective
```

La translation des os ne figure pas dans l’inversion du delta, ce qui est
normal : une différence de positions est un vecteur et se transforme par la
partie 3×3. Les positions courantes, elles, ont été évaluées par Blender avec la
transformation affine complète.

36. Construire CORR_jawOpen_mouthClose de bout en bout

36.1 — Poser la combinaison source

1. toutes les shape keys à zéro ;
2. Pose Mode, CTRL_jaw.open = 1 ;
3. Object Mode, SK_mouthClose = 1 ;
4. affiche les dents et la langue ;
5. laisse Multires visible pour juger, mais le helper l’exclura du target cage ;
6. observe le défaut : lèvres qui glissent, perte de volume ou collision.

Crée le target posé :

```python
set_all_key_values_zero(head)
rig.pose.bones["CTRL_jaw"]["open"] = 1.0
head.data.shape_keys.key_blocks["SK_mouthClose"].value = 1.0
bpy.context.view_layer.update()

ensure_shape_key(head, "CORR_jawOpen_mouthClose").value = 0.0
close_pose_target = create_pose_sculpt_target(
    head, "CORR_jawOpen_mouthClose")
```

36.2 — Sculpter dans la pose, sans transformer le target

1. cache la tête master, pas les dents ;
2. sélectionne SCULPTPOSE__CORR_jawOpen_mouthClose ;
3. passe en Sculpt Mode ;
4. rétablis un contact lèvres ≤ 0,30 mm dans cette mâchoire ouverte ;
5. conserve le volume et les commissures ;
6. éloigne les lèvres des incisives si elles les traversent ;
7. ne touche pas le crâne, le cou ou l’autre région du visage ;
8. ne déplace, tourne ou scale jamais l’objet target en Object Mode ;
9. reviens en Object Mode.

36.3 — Inverser et reconstruire

```python
head.hide_set(False)
close_pose_target.hide_set(True)
commit_pose_space_corrective(
    head, rig, close_pose_target, "CORR_jawOpen_mouthClose")
```

Ajoute le driver produit jaw × mouthClose :

```python
def install_jaw_shape_product_driver(obj, rig, corrective_name, source_name):
    corrective = obj.data.shape_keys.key_blocks[corrective_name]
    try:
        corrective.driver_remove("value")
    except (TypeError, RuntimeError):
        pass
    fcurve = corrective.driver_add("value")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = "jaw*shape"
    add_single_prop_variable(
        driver, "jaw", rig, 'pose.bones["CTRL_jaw"]["open"]')
    add_key_value_variable(
        driver, "shape", obj.data.shape_keys, source_name)
    return fcurve

install_jaw_shape_product_driver(
    head, rig, "CORR_jawOpen_mouthClose", "SK_mouthClose")
bpy.context.view_layer.update()
```

Compare la reconstruction à la cible désirée :

```python
def compare_current_cage_to_target_mm(obj, target):
    current = evaluated_cage_coords(obj)
    desired = target_coords_in_source_space(obj, target)
    return 1000.0 * max((a - b).length for a, b in zip(current, desired))

error_mm = compare_current_cage_to_target_mm(head, close_pose_target)
print("CORR_jawOpen_mouthClose_ERROR_MM", error_mm)
if error_mm > 0.05:
    raise RuntimeError("Reconstruction pose-space > 0,05 mm")
```

Ce test est indispensable. Une forme qui paraît correcte en vue de face mais
échoue numériquement n’est pas validée.

37. Construire les autres correctives jaw

Les primitives latérales restent indépendantes. Utilise des suffixes .L/.R
pour les correctives associées à des clés .L/.R; une seule corrective
bilatérale activée par max(L,R) déplacerait le mauvais côté.

```python
JAW_CORRECTIVE_SPECS = (
    ("CORR_jawOpen_smile.L", "SK_mouthSmile.L"),
    ("CORR_jawOpen_smile.R", "SK_mouthSmile.R"),
    ("CORR_jawOpen_pucker", "SK_mouthPucker"),
    ("CORR_jawOpen_funnel", "SK_mouthFunnel"),
    ("CORR_jawOpen_lowerDown.L", "SK_mouthLowerDown.L"),
    ("CORR_jawOpen_lowerDown.R", "SK_mouthLowerDown.R"),
    ("CORR_jawOpen_mouthStretch.L", "SK_mouthStretch.L"),
    ("CORR_jawOpen_mouthStretch.R", "SK_mouthStretch.R"),
)
for corrective_name, source_name in JAW_CORRECTIVE_SPECS:
    ensure_shape_key(head, corrective_name)
```

Pour chaque paire, exécute exactement la même séquence :

1. set_all_key_values_zero(head) ;
2. CTRL_jaw.open = 1 ;
3. source = 1 ;
4. corrective = 0 et driver temporairement retiré si elle en a déjà un ;
5. create_pose_sculpt_target ;
6. sculpte uniquement le défaut visible dans l’espace posé ;
7. commit_pose_space_corrective ;
8. installe le driver produit ;
9. compare la cage reconstruite au target à ≤ 0,05 mm ;
10. cache le target sans le supprimer.

Ce helper automatise les étapes non artistiques après la sculpture :

```python
def finalize_jaw_corrective(obj, rig, corrective_name, source_name):
    target = require_object("SCULPTPOSE__" + corrective_name, "MESH")
    target.hide_set(True)
    obj.hide_set(False)
    commit_pose_space_corrective(obj, rig, target, corrective_name)
    install_jaw_shape_product_driver(obj, rig, corrective_name, source_name)
    bpy.context.view_layer.update()
    error = compare_current_cage_to_target_mm(obj, target)
    print("JAW_CORRECTIVE_ERROR_MM", corrective_name, error)
    if error > 0.05:
        raise RuntimeError(f"{corrective_name}: reconstruction {error} mm")
    return error
```

Consignes artistiques pendant les sculpts posés :

• jawOpen × smile : restaure la trajectoire de commissure et le volume sans
coller la lèvre inférieure à la supérieure ;
• jawOpen × pucker : conserve le cylindre projeté et empêche les incisives de
traverser ;
• jawOpen × funnel : garde l’ouverture ronde autour des dents/langue ;
• jawOpen × lowerDown : évite le double abaissement et la rupture des triangles
sous la lèvre ;
• jawOpen × stretch : empêche l’étirement excessif de commissure et conserve
l’épaisseur.

38. Tester les correctives sur une grille 5 × 5

Une corrective sculptée à 1×1 peut encore mal interpoler au milieu. Pour chaque
paire, teste :

```text
jaw    = 0.00, 0.25, 0.50, 0.75, 1.00
shape  = 0.00, 0.25, 0.50, 0.75, 1.00
```

Le helper suivant échantillonne les valeurs et laisse l’inspection de collision
au test F4 :

```python
def sample_jaw_shape_grid(obj, rig, source_name, callback=None):
    samples = (0.0, 0.25, 0.50, 0.75, 1.0)
    source = obj.data.shape_keys.key_blocks[source_name]
    results = []
    for jaw in samples:
        rig.pose.bones["CTRL_jaw"]["open"] = jaw
        for shape in samples:
            source.value = shape
            bpy.context.view_layer.update()
            coords = evaluated_cage_coords(obj)
            record = {"jaw": jaw, "shape": shape,
                      "finite": all(all(math.isfinite(v) for v in co)
                                    for co in coords)}
            if callback:
                record.update(callback(coords, jaw, shape) or {})
            if not record["finite"]:
                raise RuntimeError(f"NaN/Inf : {source_name} {jaw}×{shape}")
            results.append(record)
    source.value = 0.0
    rig.pose.bones["CTRL_jaw"]["open"] = 0.0
    bpy.context.view_layer.update()
    return results
```

À chaque case regarde en face, profil et coupe :

• contact lèvres ;
• lèvres contre dents ;
• volume du vermillon ;
• commissures ;
• faces inversées ;
• traction du cou ;
• côté opposé.

Si l’interpolation jaw*shape ne suffit pas, ne gonfle pas la corrective 1×1.
Crée des correctives échantillonnées, par exemple
CORR_jaw050_mouthClose, sculptées et inversées à jaw=0.50, puis active-les
avec une fonction chapeau :

```python
def install_sampled_jaw_driver(obj, rig, corrective_name, source_name,
                               center, half_width):
    key = obj.data.shape_keys.key_blocks[corrective_name]
    try:
        key.driver_remove("value")
    except (TypeError, RuntimeError):
        pass
    fcurve = key.driver_add("value")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = (
        f"shape*max(0.0,1.0-abs(jaw-{center:.17g})/{half_width:.17g})")
    add_single_prop_variable(
        driver, "jaw", rig, 'pose.bones["CTRL_jaw"]["open"]')
    add_key_value_variable(driver, "shape", obj.data.shape_keys, source_name)
```

Ne superpose pas une corrective pleine jaw*shape et plusieurs échantillons
sans recalculer leurs résidus les uns par rapport aux autres.

39. Vérifier les collisions et le retour neutre

39.1 — Test visuel systématique

Pour toutes les primitives et correctives :

1. active le wireframe en overlay ;
2. affiche les normales de face dans Edit Mode → Overlays → Face Orientation ;
3. recherche une face rouge/inversée ;
4. affiche dents et langue ;
5. inspecte au moins face, profils L/R, trois-quarts L/R et coupe sagittale ;
6. teste chaque côté seul puis les deux côtés ;
7. vérifie qu’aucune dent n’est exposée sans intention ;
8. vérifie que les lèvres ne traversent jamais la langue au neutre ;
9. compare les longueurs d’arêtes à la cage neutre : hors whitelist, elles
doivent rester entre 0,50× et 2,00× ;
10. pour mouthClose, exige ≤ 0,30 mm de gap ;
11. hors pucker/funnel, garde la variation de volume labial sous 10 %.

39.2 — Revenir au vrai neutre

```python
set_all_key_values_zero(head)
rig.pose.bones["CTRL_jaw"]["open"] = 0.0
for name in ("CTRL_gaze", "CTRL_eye_target.L", "CTRL_eye_target.R",
             "CTRL_tongue", "CTRL_tongue_tip"):
    if name in rig.pose.bones:
        pb = rig.pose.bones[name]
        pb.location = Vector((0, 0, 0))
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Vector((0, 0, 0))
        pb.scale = Vector((1, 1, 1))
bpy.context.view_layer.update()

for key in head.data.shape_keys.key_blocks:
    if key.name != "Basis" and abs(key.value) > 1e-7:
        raise RuntimeError(f"Clé non neutre : {key.name}={key.value}")
for fc in head.data.shape_keys.animation_data.drivers:
    if not fc.driver.is_valid:
        raise RuntimeError(f"Driver invalide : {fc.data_path}")
print("ATLAS_F4_NEUTRAL_OK")
```

40. Sauvegarder F4 et lancer les tests hors interface

1. cache la collection SCULPT_TARGETS_AUTHOR au rendu ;
2. garde-la dans le fichier auteur pour reprise, mais elle ne fera pas partie de
l’export runtime ;
3. vérifie que GEO-head_animation_realistic est visible ;
4. remets la timeline à la frame neutre ;
5. Ctrl+S ;
6. ferme puis rouvre le fichier ;
7. répète le test du neutre et une combinaison jaw×mouthClose.

```python
save_checkpoint("source/ATLAS_FACE_F4_MOUTH.blend")
```

Dans le terminal :

```bash
mkdir -p reports/f4 renders/f4 exports
blender -b source/ATLAS_FACE_F4_MOUTH.blend \
  --python tests/f4-mouth.py \
  -- --mode final --report reports/f4/registre.json
```

Ne considère F4 terminé que si le processus rend le code 0, si toutes les
reconstructions pose-space sont ≤ 0,05 mm, si mouthClose est ≤ 0,30 mm et si la
topologie/UV du verrou F1.5 sont inchangées.

41. Où chercher quand une manipulation bloque

Cherche le problème réduit, pas « facial rig ne marche pas » :

|Symptôme observé                 |Recherche à lancer                                                            |
|---------------------------------|------------------------------------------------------------------------------|
|mâchoire part de travers         |`Blender jaw hinge bone roll local X` / `Blender axe local charnière mâchoire`|
|slide part dans le mauvais repère|`Blender PoseBone location rest matrix local space`                           |
|iris bouge deux fois             |`Blender eye mesh double transform parent armature modifier`                  |
|œil flippe près d’une limite     |`Blender Damped Track Limit Rotation flip local space`                        |
|poids polluent le crâne          |`Blender weight paint normalize all locked groups jaw`                        |
|langue se pince entre deux os    |`Blender tongue rig three bone smooth weights`                                |
|blink traverse la cornée         |`Blender eyelid shape key eyeball collision signed distance`                  |
|follow saute au centre           |`Blender driver eye rotation up down split positive negative`                 |
|Multires change après une clé    |`Blender 5.1 Multires shape key vertex order`                                 |
|résidu corrective doublé         |`Blender corrective shape key residual A plus B`                              |
|corrective jaw dérive            |`linear blend skinning inverse pose space corrective Blender`                 |
|glTF perd le rig                 |`Blender glTF bake constraints deform bones morph weights`                    |

Ordre de consultation conseillé :

1. manuel Blender 5.x : Armatures, Bone Roll, Bone Collections, Armature
modifier, Shape Keys, Drivers, Damped Track et Limit Rotation ;
2. documentation API Blender pour le type précis utilisé dans le script ;
3. cours Blender Studio Advanced Facial Rigging, chapitre correspondant à la
zone ;
4. reproduction minimale dans un nouveau .blend avec deux os et dix sommets ;
5. seulement ensuite, correction du builder Atlas.

Quand une commande Python échoue sous 5.1.2, interroge l’API locale au lieu de
copier un snippet d’une autre version :

```python
print(bpy.app.version_string)
print(dir(bpy.types.PoseBone))
print(dir(bpy.types.ShapeKey))
print(bpy.ops.nla.bake.get_rna_type().properties.keys())
```

Un blocage n’autorise jamais à appliquer Multires, à réordonner la topologie, à
activer Preserve Volume après le calcul des correctives, ou à remplacer les
tests par une appréciation visuelle unique.

Partie III — F5 à F12 : expressions, parole, runtime et recette

Cette partie suppose que F4 a passé son gate, que
source/FACE_TOPOLOGY_FINAL.blend existe et que les paupières, la mâchoire,
les yeux, les dents, la langue et les primitives de bouche ont déjà leurs noms
définitifs.

Contrat de départ

Travaille depuis la racine du dépôt. Ne modifie jamais un fichier validé en
place. Chaque builder ouvre le livrable précédent, vérifie ses empreintes,
sauvegarde sous le nom de la phase courante, puis seulement ajoute les éléments
de la phase.

Les axes Atlas restent :

• +X = gauche du personnage ;
• -Y = avant du visage ;
• +Z = haut ;
• coordonnées Blender en mètres, mesures publiées en millimètres.

Les fichiers utilisés ci-dessous sont :

```text
F4 entrée  : source/ATLAS_FACE_F4_MOUTH.blend
F5 sortie  : source/ATLAS_FACE_F5_UPPER.blend
F6 sortie  : source/ATLAS_FACE_F6_FACS.blend
F7 sortie  : source/ATLAS_FACE_F7_CORRECTIVES.blend
F8 sortie  : source/ATLAS_FACE_F8_CONTROLS.blend
F9 sortie  : source/ATLAS_FACE_F9_SPEECH.blend
F10 sortie : source/ATLAS_FACE_F10_BODY.blend
F11 master : runtime/ATLAS_FACE_RUNTIME.blend
GLB final  : exports/atlas-face-v1.glb
```

Si le livrable F4 porte un autre nom, ne renomme rien silencieusement : ajoute
le chemin réel comme argument du builder et inscris-le dans le rapport F5.

Avant F5, crée les dossiers sans écraser leur contenu :

```bash
mkdir -p rig tests runtime exports videos \
  reports/f5 reports/f6 reports/f7 reports/f8 reports/f9 reports/f10 \
  reports/f11 reports/f12 renders/f5 renders/f6 renders/f7 renders/f8 \
  renders/f9 renders/f10 renders/f11 renders/f12
```

────────

PHASE F5 — SOURCILS, FRONT, JOUES ET NEZ

Résultat à obtenir

À la fin de F5, Atlas doit pouvoir lever et baisser chaque sourcil, lever chaque
joue, renforcer le sillon nasogénien, plisser le nez et dilater/comprimer chaque
narine. Chaque côté doit fonctionner seul. Le crâne arrière, les oreilles, le
cou et le côté opposé doivent rester immobiles.

F5.1 — ouvrir une copie et préparer une vue de sculpture sûre

Ouvre Blender 5.1.2, puis :

1. File > Open et choisis source/ATLAS_FACE_F4_MOUTH.blend.
2. Dans l’Outliner, sélectionne GEO-head_animation_realistic.
3. Dans Object Data Properties > Shape Keys, vérifie que Basis existe et
que toutes les clés F3/F4 valent 0.000.
4. Dans Modifiers, laisse Multires actif en vue, niveau 1, mais ne
l’applique pas.
5. Passe en Object Mode, duplique seulement pour diagnostic avec Shift+D,
renomme la copie TMP_F5_REFERENCE, puis masque-la du rendu.
6. Reviens sur la tête autoritaire.

Tu dois voir le visage neutre F4, sans mouvement quand tu fais passer toutes les
valeurs de shape keys de 0 à 0. Si une clé conserve une valeur ou un driver
actif, remets-la à zéro avant de continuer et note son nom dans
reports/f5/preflight.json.

Crée rig/build-f5-upper.py. Le script doit commencer par ouvrir F4, vérifier
le verrou topologique final, sauvegarder sous
source/ATLAS_FACE_F5_UPPER.blend, puis travailler sur cette copie. Il ne doit
jamais dépendre de la sélection courante.

F5.2 — créer les groupes de masque avant les shape keys

Les masques servent à sélectionner les mêmes sommets manuellement et par
script. Ils ne doivent pas limiter les morph targets runtime : les deltas des
shape keys restent réellement nuls hors masque.

Masque du sourcil gauche

1. Sélectionne la tête.
2. Tab vers Edit Mode.
3. Active la sélection de sommets.
4. Passe en vue face avec Numpad 1, puis en rayons X avec Alt+Z.
5. Sur le côté +X, sélectionne la bande de sommets immédiatement au-dessus de
la paupière supérieure, du bord nasal jusqu’au tiers externe de l’orbite.
6. Étends la sélection de deux boucles vers le front avec Ctrl+Numpad + ou
Select > Select More, mais désélectionne la paupière mobile.
7. Reste en Edit Mode. Dans Object Data Properties > Vertex Groups, clique
+, renomme le groupe MASK_brow.L, règle Weight sur 1.000, puis clique
Assign pendant que les sommets sont encore sélectionnés.
8. Passe en Object Mode, puis choisis Weight Paint pour contrôler le groupe.
9. Reviens en Edit Mode et crée de la même manière :

```text
MASK_browInner.L
MASK_browOuter.L
MASK_cheek.L
MASK_nasolabial.L
MASK_noseWing.L
MASK_nostrilBorder.L
```

Repères visuels :

• MASK_browInner.L couvre le tiers proche de la glabelle ;
• MASK_browOuter.L couvre le tiers externe, sans la tempe entière ;
• MASK_cheek.L part sous la paupière inférieure et descend jusqu’au sommet de
la joue, sans inclure la commissure labiale ;
• MASK_nasolabial.L suit une bande du bord de l’aile du nez vers la
commissure ;
• MASK_noseWing.L couvre l’aile du nez ;
• MASK_nostrilBorder.L ne contient que le pourtour audité de la narine et la
première boucle voisine.

Affiche chaque groupe avec Weight Paint. Tu dois voir une île unique, sans
sommet du côté opposé. Si un masque traverse le plan sagittal, retourne en Edit
Mode et retire ces sommets avant de créer une forme.

Le builder écrit les indices dans :

```text
reports/f5/masks.json
```

et crée les groupes droits à l’aide de la carte miroir finale, jamais par
recherche de position.

Helper de masque reproductible

Ajoute au builder :

```python
def group_indices(obj, name):
    vg = obj.vertex_groups.get(name)
    if vg is None:
        raise RuntimeError(f"groupe absent: {name}")
    out = []
    for v in obj.data.vertices:
        try:
            if vg.weight(v.index) > 0.0:
                out.append(v.index)
        except RuntimeError:
            pass
    if not out:
        raise RuntimeError(f"groupe vide: {name}")
    return out

def ensure_relative_key(obj, name):
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    kb = obj.data.shape_keys.key_blocks.get(name)
    if kb is None:
        kb = obj.shape_key_add(name=name, from_mix=False)
    kb.relative_key = obj.data.shape_keys.key_blocks["Basis"]
    kb.value = 0.0
    return kb
```

F5.3 — sourcil intérieur vers le haut

Crée SK_browInnerUp.L.

Dans Blender

1. Sélectionne la tête et ouvre Object Data Properties > Shape Keys.
2. Clique +, renomme la nouvelle clé SK_browInnerUp.L.
3. Mets sa valeur à 1.000 et active l’icône d’épingle si elle est disponible.
4. Passe en Edit Mode ; vérifie dans la liste que la clé active est bien
SK_browInnerUp.L, pas Basis.
5. Dans Vertex Groups, choisis MASK_browInner.L, puis Select.
6. En vue face, déplace la boucle la plus proche du sourcil de +4 mm en Z :
G, Z, saisis 0.004, Enter.
7. Déplace la boucle suivante de +2.5 mm, puis la boucle supérieure de
+1 mm.
8. Sur les sommets les plus proches de la glabelle, ajoute environ 0.5 mm
vers l’avant (G, Y, -0.0005) pour éviter un front aplati.
9. Reviens en Object Mode et inspecte face, trois-quarts et profil.

Tu dois voir l’intérieur du sourcil monter avec une transition large dans le
front. La paupière ne doit pas suivre rigidement. Si une pointe apparaît,
annule uniquement les derniers déplacements et répartis-les sur une boucle de
plus ; ne lisse pas Basis.

Les valeurs 4/2,5/1 mm sont un départ de sculpture, pas le gate final. Le
rapport publie l’amplitude réellement conservée.

F5.4 — sourcil extérieur vers le haut et sourcil vers le bas

Pour SK_browOuterUp.L :

1. crée la clé ;
2. sélectionne MASK_browOuter.L ;
3. monte la bande principale de 3 mm ;
4. réduis progressivement à 1 mm vers la tempe et vers le centre ;
5. vérifie que le canthus externe n’est pas tiré en pointe.

Pour SK_browDown.L :

1. crée la clé ;
2. sélectionne MASK_brow.L ;
3. déplace le tiers intérieur de -3 mm en Z et de 0.8 à 1.2 mm vers le plan
sagittal ;
4. déplace le tiers extérieur de -1.5 mm en Z ;
5. resserre la glabelle sans fermer automatiquement la paupière.

Passe rapidement entre 0 et 1. Le volume doit rouler, pas s’écraser. Si le
front semble enfoncé, déplace la deuxième boucle légèrement vers l’avant plutôt
que d’augmenter Z.

F5.5 — joue et sillon nasogénien

Crée SK_cheekRaise.L.

1. Active la clé à 1.
2. En Edit Mode, sélectionne MASK_cheek.L.
3. Monte la zone centrale de joue de 3 mm en Z et avance-la de 1 mm vers -Y.
4. Sur la première boucle sous la paupière, limite le déplacement à 1.5 mm.
5. Sur la limite basse, réduis à zéro avant la commissure.
6. Inspecte avec le globe visible : la joue peut soutenir la paupière
inférieure, mais ne doit pas pénétrer la sclère.

Crée ensuite SK_nasolabialDeepen.L :

1. sélectionne la bande MASK_nasolabial.L ;
2. déplace la lèvre de pli proche du nez de 0.8 à 1.2 mm vers l’intérieur de la
surface, le long de la normale locale ;
3. déplace la joue immédiatement latérale de 0.5 à 1 mm vers l’extérieur ;
4. termine le pli avant la commissure ;
5. inspecte sous une lumière rasante.

N’utilise pas une rainure de largeur un sommet. Si le pli ressemble à une
coupure, annule et distribue le couple creux/bourrelet sur au moins trois
rangées.

F5.6 — nez plissé et narines

Crée SK_noseWrinkle.L :

1. sélectionne MASK_noseWing.L ;
2. monte l’aile de 1.5 à 2 mm ;
3. rapproche-la légèrement du dorsum, au maximum 1 mm ;
4. entraîne la bande latérale basse du nez sur 1 à 2 boucles ;
5. ne lève pas encore toute la lèvre supérieure : cette interaction sera une
corrective F7.

Pour SK_nostrilDilate.L :

1. affiche le wireframe avant de déplacer quoi que ce soit ;
2. sélectionne uniquement MASK_nostrilBorder.L ;
3. pour chaque sommet du bord, calcule dans le builder le vecteur partant du
centre de la narine vers le sommet, projeté dans le plan local de
l’ouverture ;
4. déplace le bord de 0.6 mm sur ce vecteur ;
5. déplace la boucle suivante de 0.3 mm ;
6. inspecte silhouette et facettes.

Pour SK_nostrilCompress.L, applique le même champ avec -0.4 mm, mais arrête
avant que deux arêtes se croisent.

Le nombre de sommets du bord vient de
F0_CONTRACT["anatomy_counts"]["nostril_border_vertices"]["L"] — 7–8 n’est
qu’une baseline c0885. Si une forme propre est impossible, ne masque pas le
problème avec le lissage et ne retopologise surtout pas le checkpoint F1.5.
Repars du master d’auteur pré-gel, fais la retopologie locale, puis régénère UV,
empreinte, landmarks/correspondances, carte miroir, globe-fit, deltas, masque jaw
et contrat F0. Reconstruis ensuite F1 → F5 dans cet ordre. F5 n’est pas autorisée
à modifier la topologie silencieusement.

Champ radial utilisé par le builder

```python
def radial_delta(points, center, normal, amplitude_m):
    n = normal.normalized()
    out = []
    for p in points:
        r = p - center
        r = r - n * r.dot(n)
        out.append(r.normalized() * amplitude_m if r.length > 1e-9 else r)
    return out
```

Le centre et la normale sont recalculés sur le neutre, puis conservés pour
dilate et compress. Le rapport les publie.

F5.7 — créer les côtés droits par miroir de delta

Ne resculpte pas le côté droit à l’œil.

1. Mets toutes les clés à 0.
2. Pour chaque clé .L, crée la clé .R.
3. Pour chaque sommet gauche i, lis j = mirror_map[i].
4. Calcule delta = key_L[i].co - Basis[i].co.
5. Pose sur j le delta (-delta.x, delta.y, delta.z) ajouté au Basis droit.
6. Vérifie que les sommets hors côté droit ont un delta nul.

```python
def mirror_delta_key(obj, src_name, dst_name, mirror_map):
    keys = obj.data.shape_keys.key_blocks
    basis, src = keys["Basis"], keys[src_name]
    dst = ensure_relative_key(obj, dst_name)
    for idx, d in enumerate(dst.data):
        d.co = basis.data[idx].co
    for i, j in enumerate(mirror_map):
        delta = src.data[i].co - basis.data[i].co
        dst.data[j].co = basis.data[j].co + Vector((-delta.x, delta.y, delta.z))
```

Après miroir, rends L et R sous une lumière miroir. Une correction spécifique
au côté droit est permise uniquement si elle est écrite comme delta
supplémentaire et documentée ; ne modifie pas la géométrie Basis.

F5.8 — sauvegarder, rendre et tester

Avant la sauvegarde publique, supprime TMP_F5_REFERENCE dans cette copie de
travail : sélectionne-le dans l’Outliner, vérifie une dernière fois son nom,
puis X > Delete. Le builder doit aussi refuser tout objet TMP_* dans les
collections exportables. Sauvegarde source/ATLAS_FACE_F5_UPPER.blend.

Crée tests/f5-upper.py. Pour chaque clé, évalue
0, 0.1, ..., 1.0 et mesure :

• retour à zéro, maximum 0.01 mm ;
• côté opposé, maximum 0.01 mm ;
• crâne arrière et cou, maximum 0.01 mm ;
• aucune face d’aire signée négative par rapport au neutre ;
• aucune nouvelle auto-intersection dans la région touchée ;
• UV et ordre des sommets inchangés ;
• amplitude maximale et p95 publiées, sans NaN/Inf.

Teste aussi :

```text
cheekRaise.L + SK_mouthSmile.L
browDown.L + SK_eyeSquint.L
noseWrinkle.L + SK_mouthUpperUp.L
nostrilDilate.L + jaw open 0.5
SK_chinRaise + SK_mouthClose
```

Si une combinaison est mauvaise mais les formes isolées sont propres, ne
déforme pas les primitives pour la cacher : capture la pose désirée pour F7.

Rends pour chaque famille une planche 0/50/100, face et trois-quarts, plus un
wireframe et une heatmap. Le script écrit :

```text
reports/f5/registre.json
reports/f5/masks.json
reports/f5/amplitudes.json
renders/f5/
```

Commande :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f5-upper.py -- \
  source/ATLAS_FACE_F5_UPPER.blend reports/f5/registre.json
```

Si le script sort 2, ouvre l’image annotée du pire sommet indiquée dans le
JSON, corrige uniquement la clé fautive, sauvegarde et relance. Ne commence F6
qu’après code 0.

────────

PHASE F6 — MAPPING FACS MESURÉ

Résultat à obtenir

F6 ne sculpte pas une deuxième bibliothèque. Elle nomme et mesure les formes
déjà validées, complète seulement les AUs réellement absentes, puis publie un
mapping logique indépendant de l’interface de contrôle qui sera construite en
F8.

F6.1 — ouvrir F5 et créer le registre machine

Ouvre source/ATLAS_FACE_F5_UPPER.blend, vérifie toutes les valeurs à zéro,
puis sauvegarde sous source/ATLAS_FACE_F6_FACS.blend.

Crée runtime/facs-map.json avec cette structure :

```json
{
  "version": 1,
  "neutral": "Basis",
  "units": "normalized_0_1",
  "channels": {
    "AU01.L": {"shape_keys": {"SK_browInnerUp.L": 1.0}},
    "AU01.R": {"shape_keys": {"SK_browInnerUp.R": 1.0}},
    "AU26": {"bones": {"CTRL_jaw.open": 1.0}}
  }
}
```

Le fichier décrit un résultat attendu. Il ne prétend pas encore qu’un driver
existe.

F6.2 — remplir les canaux existants

Dans rig/register-facs.py, construis au minimum :

```text
AU01.L/R -> SK_browInnerUp.L/R
AU02.L/R -> SK_browOuterUp.L/R
AU04.L/R -> SK_browDown.L/R
AU05.L/R -> SK_eyeWide.L/R
AU06.L/R -> SK_cheekRaise.L/R
AU07.L/R -> SK_eyeSquint.L/R
AU09.L/R -> SK_noseWrinkle.L/R
AU10.L/R -> SK_mouthUpperUp.L/R
AU12.L/R -> SK_mouthSmile.L/R
AU14.L/R -> SK_mouthDimple.L/R
AU15.L/R -> SK_mouthFrown.L/R
AU16.L/R -> SK_mouthLowerDown.L/R
AU17     -> SK_chinRaise
AU18     -> SK_mouthPucker
AU20.L/R -> SK_mouthStretch.L/R
AU22     -> SK_mouthFunnel
AU24.L/R -> SK_mouthPress.L/R
AU26     -> CTRL_jaw.open
AU28     -> SK_mouthRollUpper + SK_mouthRollLower
AU38.L/R -> SK_nostrilDilate.L/R
AU39.L/R -> SK_nostrilCompress.L/R
AU45.L/R -> SK_eyeBlink.L/R
```

Ne crée pas encore AU23 ou AU25 sous des noms vagues. Construis-les maintenant
si elles sont nécessaires :

AU23 — Lip Tightener

1. Crée SK_mouthTighten.L et .R.
2. Active la clé gauche.
3. Sélectionne les deux premières boucles autour de la moitié gauche de la
bouche.
4. Ramène la commissure légèrement vers le centre, comprime le vermillon sans
fermer toute la bouche et redistribue le volume vers les boucles voisines.
5. Garde un jour labial si AU25 vaut 0.
6. Miroir par indices.

AU25 — Lips Part

1. Crée SK_lipsPart.
2. Réutilise les paires de marges F0.
3. Déplace la marge supérieure vers +Z et l’inférieure vers -Z pour obtenir
un petit jour régulier, sans rotation de mâchoire.
4. Garde les dents presque cachées.
5. Publie le jour à valeur 1 ; il doit être supérieur au neutre et inférieur à
la petite ouverture obtenue par jaw open 0.25.

Ajoute alors :

```text
AU23.L/R -> SK_mouthTighten.L/R
AU25     -> SK_lipsPart
```

AU27 est une grande ouverture composée. Ne crée pas une clé qui duplique la
rotation de mâchoire : mappe CTRL_jaw.open = 1 et la corrective de grande
ouverture correspondante lorsqu’elle existera.

F6.3 — mesurer les intensités sans inventer A–E

Pour chaque canal :

1. mets tous les autres canaux à zéro ;
2. applique 0, 0.25, 0.50, 0.75, 1.00 directement aux shape keys ou
à la propriété jaw ;
3. rends la même caméra ;
4. mesure le déplacement p50, p95 et max des sommets touchés ;
5. mesure le côté opposé ;
6. note le premier niveau où le mouvement est clairement visible.

Dans docs/FACS_MATRIX.md, écris par exemple :

```text
AU12.L | SK_mouthSmile.L | logique CTRL future | amplitude max 8.2 mm |
échantillons 0/.25/.5/.75/1 | mesuré | reports/f6/AU12.L.json
```

Ne transforme pas automatiquement .50 en intensité FACS C. Les lettres A–E
sont des niveaux de codage observés ; conserve une colonne approximation tant
qu’un codeur qualifié ne les a pas attribuées.

F6.4 — tester les côtés et les formes composées

Crée tests/f6-facs.py. Il lit runtime/facs-map.json et refuse :

• une clé ou un os absent ;
• une clé non relative à Basis ;
• une valeur hors 0–1 ;
• un canal gauche qui déplace le côté droit de plus de 0.01 mm ;
• un retour neutre supérieur à 0.01 mm ;
• une face inversée ou une nouvelle collision.

Le test crée ensuite les poses de lecture suivantes :

```text
AU12
AU06 + AU12
AU04 + AU07
AU01 + AU02 + AU05 + AU26
AU09 + AU10
AU17 + AU24
```

Pour chaque pose, rends face, trois-quarts L/R et profil utile. Si une pose
composée casse alors que les AUs isolées passent, ajoute-la à
reports/f6/correctives-required.json. Ne la corrige pas en F6.

F6.5 — sauvegarder et sortir

Sauvegarde source/ATLAS_FACE_F6_FACS.blend, puis lance :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f6-facs.py -- \
  source/ATLAS_FACE_F6_FACS.blend runtime/facs-map.json \
  reports/f6/registre.json renders/f6
```

Tu dois obtenir code 0, une ligne complète par AU et une liste explicite de
correctives à construire en F7. Si un canal manque, retourne à la sous-étape
correspondante ; ne marque jamais une AU validé parce que son nom existe dans
le JSON.

────────

PHASE F7 — CORRECTIVES DE COMBINAISONS

Résultat à obtenir

F7 corrige uniquement ce qui casse lorsque deux mouvements validés sont
combinés. Une corrective doit être nulle dès qu’un de ses deux canaux vaut zéro
et ne doit jamais contenir une copie complète des deux formes primaires.

F7.1 — préparer la liste de travail

Ouvre source/ATLAS_FACE_F6_FACS.blend et sauvegarde immédiatement sous
source/ATLAS_FACE_F7_CORRECTIVES.blend.

Ouvre reports/f6/correctives-required.json. Commence par ces poses si elles y
sont réellement fautives :

```text
AU06.L × AU12.L
AU06.R × AU12.R
AU04.L × SK_eyeBlink.L
AU04.R × SK_eyeBlink.R
AU09.L × AU10.L
AU09.R × AU10.R
SK_chinRaise × AU24
SK_mouthClose × jawOpen
SK_mouthSmile.L/R × jawOpen
SK_mouthPucker × jawOpen
SK_eyeBlink.L/R × lookUp/lookDown
```

Pour chaque combinaison, le JSON doit contenir : noms exacts des entrées,
valeurs qui cassent, capture, sommets fautifs et symptôme. Si une entrée manque,
reproduis la pose et complète le JSON avant de sculpter.

F7.2 — corrective shape key × shape key

Exemple : AU06.L × AU12.L.

Créer une cible sculptable

1. Sélectionne GEO-head_animation_realistic.
2. Mets toutes les shape keys à 0.
3. Mets SK_cheekRaise.L = 1 et SK_mouthSmile.L = 1.
4. Dans le menu de la liste des Shape Keys, choisis New Shape From Mix.
5. Renomme la nouvelle clé TMP_TARGET_AU06_AU12.L.
6. Mets les deux primitives à 0 et laisse TMP_TARGET... = 1 : la pose visible
doit rester identique. Si elle change, arrête ; la cible n’a pas capturé le
mix attendu.
7. En Edit Mode sur TMP_TARGET..., corrige seulement la joue, le sillon et la
commissure qui se pincent. Ne retouche pas tout le visage.
8. Reviens en Object Mode et rends une capture target.

Convertir la cible en résidu

Crée rig/build-f7-correctives.py. Pour une combinaison de deux shape keys,
le résidu stocké doit être :

```python
def build_shape_shape_residual(obj, target_name, a_name, b_name, corr_name,
                               a_value=1.0, b_value=1.0):
    keys = obj.data.shape_keys.key_blocks
    basis, target = keys["Basis"], keys[target_name]
    a, b = keys[a_name], keys[b_name]
    corr = ensure_relative_key(obj, corr_name)
    for i in range(len(basis.data)):
        da = (a.data[i].co - basis.data[i].co) * a_value
        db = (b.data[i].co - basis.data[i].co) * b_value
        desired = target.data[i].co
        residual = desired - (basis.data[i].co + da + db)
        corr.data[i].co = basis.data[i].co + residual
    corr.value = 0.0
    return corr
```

Crée CORR_AU06_AU12.L, puis supprime TMP_TARGET_AU06_AU12.L seulement
après avoir comparé :

```text
primitives seules + corrective 1 == cible sculptée
```

Erreur maximale autorisée sur les sommets : 0.01 mm.

Si le résultat double le sourire ou la joue, la corrective contient encore les
deltas primaires. Repars de la cible et recalcule le résidu ; ne compense pas en
mettant sa valeur à 0.5.

F7.3 — corrective mâchoire × shape key en espace pré-armature

La formule précédente n’est pas correcte lorsque l’une des entrées est un os.
La shape key est évaluée avant l’Armature modifier. Il faut donc ramener la
cible sculptée depuis la pose mandibulaire vers l’espace pré-armature.

Exemple : jawOpen = 1 × SK_mouthClose = 1.

Capturer une cible à la résolution cage

1. Mets toutes les clés à 0.
2. Pose CTRL_jaw.open = 1 et SK_mouthClose = 1.
3. Dans Modifiers, mets temporairement le niveau viewport de Multires à 0.
4. Force une mise à jour de la scène.
5. Duplique le mesh évalué avec le script ci-dessous ; il doit avoir exactement
le compte vertices de tests/verrou-topologie-final.json.
6. Nomme la copie TMP_TARGET_jawOpen_mouthClose.
7. Cache la tête originale uniquement dans la vue, jamais dans le rendu de
référence.
8. Sculpte la copie en Edit Mode jusqu’à ce que les lèvres se ferment sans
traverser les dents.

```python
deps = bpy.context.evaluated_depsgraph_get()
topology_lock = json.loads(require_file(
    "tests/verrou-topologie-final.json"
).read_text(encoding="utf-8"))
expected_cage_vertices = int(topology_lock["vertices"])
head.update_tag()
bpy.context.view_layer.update()
ev = head.evaluated_get(deps)
me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True,
                                     depsgraph=deps)
if len(me.vertices) != expected_cage_vertices:
    raise RuntimeError("la cible jaw corrective ne respecte pas le verrou final")
if len(me.vertices) != len(head.data.vertices):
    raise RuntimeError("la cible jaw corrective n'est pas à la résolution cage")
tmp = bpy.data.objects.new("TMP_TARGET_jawOpen_mouthClose", me)
tmp.matrix_world = head.matrix_world.copy()
bpy.context.scene.collection.objects.link(tmp)
```

Inverser le skinning linéaire

Avant cette opération, vérifie que l’Armature modifier de la tête n’utilise pas
Preserve Volume. Le solveur suivant correspond au Linear Blend Skinning.

Pour chaque vertex, construis la matrice de déformation pondérée des os. Dans
le cas général où le mesh et l’armature n’ont pas le même matrix_world :

```python
def deform_matrix_mesh_space(mesh_obj, rig_obj, pose_bone):
    bone_rest_inv = pose_bone.bone.matrix_local.inverted()
    bone_deform = pose_bone.matrix @ bone_rest_inv
    return (mesh_obj.matrix_world.inverted() @ rig_obj.matrix_world @
            bone_deform @ rig_obj.matrix_world.inverted() @
            mesh_obj.matrix_world)

def blended_matrix(mesh_obj, rig_obj, vertex, deform_groups):
    total = 0.0
    M = Matrix(((0.0, 0.0, 0.0, 0.0),) * 4)
    for assignment in vertex.groups:
        name = mesh_obj.vertex_groups[assignment.group].name
        if name not in deform_groups or assignment.weight <= 0.0:
            continue
        pb = rig_obj.pose.bones.get(name)
        if pb is None:
            continue
        M += deform_matrix_mesh_space(mesh_obj, rig_obj, pb) * assignment.weight
        total += assignment.weight
    if total <= 1e-8:
        return Matrix.Identity(4)
    return M * (1.0 / total)
```

Pour chaque sommet sculpté de la cible :

```python
M = blended_matrix(head, rig, head.data.vertices[i], deform_groups)
if abs(M.determinant()) < 1e-10:
    raise RuntimeError(f"matrice de skin non inversible au sommet {i}")
p_pre = M.inverted() @ tmp.data.vertices[i].co
basis_co = head.data.shape_keys.key_blocks["Basis"].data[i].co
mouth_key = head.data.shape_keys.key_blocks["SK_mouthClose"]
delta_mouth_close = mouth_key.data[i].co - basis_co
current_pre = basis_co + delta_mouth_close
residual = p_pre - current_pre
corr.data[i].co = basis_co + residual
```

Crée ainsi CORR_jawOpen_mouthClose. Remets ensuite Multires niveau 1,
réactive la tête et compare la pose finale à la cible.

Si l’erreur dépasse 0.05 mm p95 ou 0.20 mm max :

• vérifie les espaces objet/armature ;
• vérifie que Preserve Volume est désactivé ;
• vérifie la somme des poids ;
• vérifie que la copie cible avait exactement expected_cage_vertices sommets ;
• ne corrige pas l’erreur en sculptant directement la shape key résiduelle dans
la pose sans inverse skinning.

F7.4 — correctives blink × regard

Les os des yeux ne déforment pas la tête. Les correctives de paupière sont donc
des résidus shape × shape :

1. pose le regard haut ou bas ;
2. active la clé SK_lidLookUp.* ou SK_lidLookDown.* correspondante ;
3. active SK_eyeBlink.* ;
4. crée New Shape From Mix ;
5. sculpte le contact sur le globe ;
6. transforme la cible en résidu avec la méthode F7.2 ;
7. mesure le gap sur 11 valeurs de blink et trois niveaux de regard.

Noms :

```text
CORR_blink_lookUp.L/R
CORR_blink_lookDown.L/R
CORR_blink_squint.L/R
```

F7.5 — enregistrer les règles d’activation

Crée runtime/correctives-map.json :

```json
{
  "CORR_AU06_AU12.L": {
    "inputs": ["AU06.L", "AU12.L"],
    "activation": "product",
    "shape_key": "CORR_AU06_AU12.L"
  },
  "CORR_jawOpen_mouthClose": {
    "inputs": ["jawOpen", "mouthClose"],
    "activation": "product",
    "shape_key": "CORR_jawOpen_mouthClose"
  }
}
```

En F7, le test fixe directement la valeur de la corrective. Les drivers seront
ajoutés et vérifiés en F8. Le runtime final calculera ces activations à partir
du JSON ; aucun driver Blender n’est supposé présent dans glTF.

F7.6 — grille de validation

Crée tests/f7-combinations.py. Pour chaque paire, évalue une grille :

```python
VALUES = (0.0, 0.25, 0.50, 0.75, 1.0)
```

À chaque cellule :

1. active A et B ;
2. active la corrective avec la règle du JSON ;
3. force head.update_tag() et view_layer.update() ;
4. mesure collisions, faces retournées, étirement, contact et neutralité ;
5. rend uniquement les cellules 0/0, 0/1, 1/0, .5/.5 et 1/1, plus toute cellule
en échec.

À A=0 ou B=0, le delta de corrective doit être exactement nul. À 1/1,
l’erreur par rapport à la cible sculptée doit rester sous les seuils de F7.2 ou
F7.3.

Sauvegarde :

```text
source/ATLAS_FACE_F7_CORRECTIVES.blend
runtime/correctives-map.json
reports/f7/registre.json
renders/f7/
```

Commande :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f7-combinations.py -- \
  source/ATLAS_FACE_F7_CORRECTIVES.blend \
  runtime/correctives-map.json reports/f7/registre.json renders/f7
```

────────

PHASE F8 — CONTRÔLEURS 2D, DRIVERS ET PANNEAU ATLAS

Résultat à obtenir

L’animateur manipule un petit tableau devant le visage et un panneau Atlas Face. Les contrôleurs n’ont aucun poids de déformation. Chaque canal primaire
revient au neutre, les correctives s’activent de manière vérifiée et le bouton
Reset remet tout à zéro.

F8.1 — créer les widgets sans géométrie de rendu

Ouvre source/ATLAS_FACE_F7_CORRECTIVES.blend, puis sauvegarde sous
source/ATLAS_FACE_F8_CONTROLS.blend.

Dans l’Outliner :

1. crée une collection WIDGETS ;
2. désactive son rendu ;
3. Shift+A > Curve > Bezier Circle ;
4. renomme WGT_face_board ;
5. dans Edit Mode, transforme la courbe en rectangle vertical ;
6. crée aussi :

```text
WGT_slider_round
WGT_slider_square
WGT_mouth_corner
WGT_eye
WGT_brow
WGT_reset
```

Applique rotation et échelle sur les widgets uniquement. Ils peuvent être
placés à l’origine car l’os qui les utilise fournit la transformation. Aucun
widget ne doit être parenté au mesh facial ni exporté.

F8.2 — construire le tableau et les contrôleurs

Dans rig/build-f8-controls.py, ajoute à RIG_Atlas_Face :

```text
CTRL_face_board
CTRL_mouth_corner.L
CTRL_mouth_corner.R
CTRL_lids.L
CTRL_lids.R
CTRL_brow.L
CTRL_brow.R
CTRL_nose.L
CTRL_nose.R
CTRL_mouth_center
```

Tous vont dans CONTROLS, avec use_deform=False.

Place CTRL_face_board environ 250 mm devant le visage, sur -Y, et oriente sa
forme dans le plan X/Z. Les contrôleurs enfants utilisent des positions de
repos différentes dans le rectangle, mais leur PoseBone.location neutre
reste (0,0,0).

Dans Pose Mode :

1. sélectionne CTRL_mouth_corner.L ;
2. Bone Properties > Viewport Display > Custom Shape =
WGT_mouth_corner ;
3. verrouille la translation locale Y, toutes les rotations et toutes les
échelles ;
4. ajoute Limit Location, Owner Space Local With Parent ;
5. autorise X de -0.020 à +0.020 m et Z de -0.020 à +0.020 m ;
6. répète pour le côté droit avec la même plage locale ;
7. limite les contrôleurs lids et brow à ±0.015 m ;
8. limite nose à ±0.010 m.

Déplace chaque os aux quatre coins. Tu dois voir le widget rester dans son
rectangle et revenir exactement à Location 0 avec Alt+G.

F8.3 — câbler un driver transform vers shape key

Ajoute ce helper :

```python
def add_bone_transform_driver(key_block, rig, bone_name, channel, expression):
    fcurve = key_block.driver_add("value")
    drv = fcurve.driver
    drv.type = 'SCRIPTED'
    drv.expression = expression
    var = drv.variables.new()
    var.name = "v"
    var.type = 'TRANSFORMS'
    target = var.targets[0]
    target.id = rig
    target.bone_target = bone_name
    target.transform_type = channel
    target.transform_space = 'LOCAL_SPACE'
    return fcurve
```

Mappings de départ :

```text
CTRL_mouth_corner.L Z+ -> SK_mouthSmile.L
CTRL_mouth_corner.L Z- -> SK_mouthFrown.L
CTRL_mouth_corner.L X+ -> SK_mouthStretch.L
CTRL_mouth_corner.L X- -> SK_mouthDimple.L
CTRL_mouth_corner.R Z+ -> SK_mouthSmile.R
CTRL_mouth_corner.R Z- -> SK_mouthFrown.R
CTRL_mouth_corner.R X- -> SK_mouthStretch.R
CTRL_mouth_corner.R X+ -> SK_mouthDimple.R
CTRL_lids.L Z-         -> SK_eyeBlink.L
CTRL_lids.L Z+         -> SK_eyeWide.L
CTRL_lids.L X-         -> SK_eyeSquint.L
CTRL_lids.R Z-         -> SK_eyeBlink.R
CTRL_lids.R Z+         -> SK_eyeWide.R
CTRL_lids.R X+         -> SK_eyeSquint.R
CTRL_brow.L Z+         -> SK_browInnerUp.L
CTRL_brow.L Z-         -> SK_browDown.L
CTRL_brow.R Z+         -> SK_browInnerUp.R
CTRL_brow.R Z-         -> SK_browDown.R
CTRL_nose.L X+         -> SK_nostrilDilate.L
CTRL_nose.L X-         -> SK_nostrilCompress.L
CTRL_nose.R X-         -> SK_nostrilDilate.R
CTRL_nose.R X+         -> SK_nostrilCompress.R
```

Cette convention suppose que les axes locaux de tous les contrôleurs ont la
même orientation dans le plan du tableau : le côté anatomique gauche est à
+X. Déplace d’abord chaque contrôle à la main et affiche ses axes locaux. Si
un bone droit a été mirrorré avec un axe local X inversé, corrige son roll en
Edit Mode avant de créer les drivers ; ne change pas seulement le signe de
l’expression pour cacher une orientation incohérente.

Exemple positif sur 20 mm :

```python
add_bone_transform_driver(keys["SK_mouthSmile.L"], rig,
                          "CTRL_mouth_corner.L", 'LOC_Z',
                          "max(0.0, min(1.0, v / 0.020))")
```

Exemple négatif :

```python
add_bone_transform_driver(keys["SK_mouthFrown.L"], rig,
                          "CTRL_mouth_corner.L", 'LOC_Z',
                          "max(0.0, min(1.0, -v / 0.020))")
```

Probe obligatoire des drivers

Après création, le builder place successivement le bone à 0, +10 mm,
+20 mm, -10 mm, force la mise à jour et vérifie les valeurs attendues.

```python
def evaluate_scene(obj):
    obj.update_tag()
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    bpy.context.view_layer.update()

def assert_close(label, got, expected, eps=1e-6):
    if abs(got - expected) > eps:
        raise RuntimeError(f"{label}: {got} != {expected}")
```

Recharge ensuite le fichier en background et répète le probe. Si is_valid
est faux ou si max/min ne donne pas la valeur attendue sous Blender 5.1.2,
n’ignore pas l’erreur : remplace le contrôleur bipolaire concerné par deux
sliders unidirectionnels, chacun limité de 0 à sa course, et utilise un driver
AVERAGE à une seule variable. Ne laisse aucun driver silencieusement à zéro.

F8.4 — propriétés centrales et contrôles non spatiaux

Ajoute sur CTRL_face_root des propriétés 0–1 :

```text
mouthClose
mouthPucker
mouthFunnel
mouthPress
mouthRollUpper
mouthRollLower
cheekRaise.L
cheekRaise.R
noseWrinkle.L
noseWrinkle.R
```

Chaque propriété reçoit min=0, max=1, soft_min=0, soft_max=1 et une
description. Pilote la shape key correspondante avec une variable
SINGLE_PROP et l’expression linéaire v. Ces propriétés apparaîtront dans le
panneau ; elles évitent de forcer trop de gestes sémantiques dans un seul bone
2D.

F8.5 — câbler les correctives

Lis runtime/correctives-map.json. Pour chaque corrective, crée un driver avec
les deux entrées et l’expression a*b, puis exécute ce probe :

```text
a=0, b=0   -> 0
a=1, b=0   -> 0
a=0, b=1   -> 0
a=.5, b=.5 -> .25
a=1, b=1   -> 1
```

Recharge le fichier et répète. Si la version exacte refuse l’expression à deux
variables, ne remplace pas le test par une affirmation :

1. ajoute une propriété explicite CORR_<nom> dans la section Debug du
panneau ;
2. laisse le test F7 utiliser cette propriété ;
3. marque automatic_driver=false dans runtime/correctives-map.json ;
4. le runtime calculera le produit à partir du JSON ;
5. F8 n’est validée automatiquement que pour les correctives dont le probe
passe.

F8.6 — créer le panneau externe Atlas Face

Crée rig/ui/atlas_face_panel.py. Ne l’embarque pas comme Text datablock dans
le .blend public.

Structure minimale :

```python
import bpy

class ATLASFACE_OT_reset(bpy.types.Operator):
    bl_idname = "atlas_face.reset"
    bl_label = "Reset Face"

    def execute(self, context):
        rig = bpy.data.objects.get("RIG_Atlas_Face")
        if rig is None:
            self.report({'ERROR'}, "RIG_Atlas_Face absent")
            return {'CANCELLED'}
        for pb in rig.pose.bones:
            if pb.name.startswith("CTRL_"):
                pb.location = (0.0, 0.0, 0.0)
                pb.rotation_mode = 'QUATERNION'
                pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
                pb.scale = (1.0, 1.0, 1.0)
                for key in pb.keys():
                    if key != "_RNA_UI" and isinstance(pb[key], (int, float)):
                        pb[key] = 0.0
        context.scene.frame_set(context.scene.frame_current)
        context.view_layer.update()
        return {'FINISHED'}

class ATLASFACE_PT_main(bpy.types.Panel):
    bl_label = "Atlas Face"
    bl_idname = "ATLASFACE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Atlas Face'

    def draw(self, context):
        layout = self.layout
        rig = bpy.data.objects.get("RIG_Atlas_Face")
        if not rig:
            layout.label(text="Rig Atlas absent", icon='ERROR')
            return
        root = rig.pose.bones.get("CTRL_face_root")
        layout.operator("atlas_face.reset", icon='LOOP_BACK')
        if root:
            for name in ("mouthClose", "mouthPucker", "mouthFunnel",
                         "mouthPress", "mouthRollUpper", "mouthRollLower"):
                if name in root:
                    layout.prop(root, f'["{name}"]', slider=True)
```

Ajoute ensuite trois sous-panneaux : Eyes/Brows, Mouth, Debug/Correctives
et deux boutons qui lancent les poses de test FACS et visèmes. Le panneau doit
se charger par :

```bash
blender source/ATLAS_FACE_F8_CONTROLS.blend \
  --python rig/ui/atlas_face_panel.py
```

F8.7 — test de neutralité et sauvegarde

Crée tests/f8-controls.py. Il doit :

1. ouvrir F8 ;
2. vérifier tous les drivers is_valid ;
3. comparer 0/mi-course/course complète à la valeur attendue ;
4. appeler l’opérateur Reset ;
5. vérifier toutes les propriétés, transforms et shape keys à zéro ;
6. mesurer le retour de surface ≤ 0.01 mm ;
7. vérifier que CTRL_, MCH_ et widgets ne déforment pas ;
8. écrire les mappings réels dans runtime/control-map.json.

Sauvegarde :

```text
source/ATLAS_FACE_F8_CONTROLS.blend
runtime/control-map.json
reports/f8/registre.json
renders/f8/control-board.png
videos/f8/control-sweep.mp4
```

Commande :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f8-controls.py -- \
  source/ATLAS_FACE_F8_CONTROLS.blend reports/f8/registre.json
```

En cas d’échec, le JSON doit nommer le bone, le driver, l’entrée et la valeur
attendue. Corrige ce canal, relance le probe isolé, puis le test complet.

────────

PHASE F9 — VISÈMES FRANÇAIS ET COARTICULATION

Résultat à obtenir

Atlas doit articuler une phrase française avec des lèvres, des dents et une
langue lisibles. Les visèmes sont des recettes de canaux existants ; une shape
key résiduelle n’est créée que lorsqu’une position de contact ne peut pas être
obtenue avec le jaw, les lèvres et la langue déjà riggés.

F9.1 — créer le fichier de travail et le dictionnaire

Ouvre source/ATLAS_FACE_F8_CONTROLS.blend, lance Reset, puis sauvegarde sous
source/ATLAS_FACE_F9_SPEECH.blend.

Crée runtime/phoneme-viseme-fr.json :

```json
{
  "language": "fr-FR",
  "version": 1,
  "visemes": {},
  "phonemes": {},
  "notes": {
    "nasality": "pas de velum visible dans la V1; metadata seulement"
  }
}
```

Crée les visèmes logiques suivants :

```text
SIL  PP  FF  DD  KK  CH  SS  NN  RR
A    E   I   O   U   Y   OE
```

Y représente le /y/ français de « tu ». OE représente /ø/ et /œ/.
TH peut être ajouté pour les mots étrangers, mais il ne doit pas être présenté
comme un phonème français central.

F9.2 — poser les consonnes de contact

Travaille une recette à la fois. Dans le panneau Atlas, mets tous les contrôles
à zéro avant chaque pose.

PP — /p b m/

1. jawOpen = 0.
2. mouthClose = 1.
3. mouthPress = 0.20.
4. Vérifie le jour labial : ≤ 0.30 mm.
5. Vérifie qu’aucune dent ne traverse les lèvres.

Recette :

```json
{"jawOpen": 0.0, "mouthClose": 1.0, "mouthPress": 0.2}
```

FF — /f v/

1. Ouvre la mâchoire à 0.10–0.15.
2. Abaisse très légèrement la lèvre inférieure avec
SK_mouthLowerDown.L=0.20 et SK_mouthLowerDown.R=0.20, puis remonte son
vermillon vers les incisives supérieures.
3. La lèvre doit effleurer le bord des incisives sans passer derrière.
4. Garde la lèvre supérieure relâchée.

Si les primitives ne permettent pas ce contact, crée
VIS_FF_residual avec le workflow jaw × shape de F7.3. Le résidu ne doit toucher
que la lèvre inférieure et sa boucle de support.

Gate FF : distance lèvre–incisives comprise entre 0 et 0.8 mm, aucune
pénétration supérieure à 0.10 mm.

DD et NN — /t d n l/

1. jawOpen = 0.15.
2. SK_lipsPart = 0.30.
3. En Pose Mode, sélectionne d’abord CTRL_tongue. Dans l’orientation
Local, déplace-le seulement sur son axe Y, vers les incisives, sans dépasser
la limite de 8 mm créée en F2.
4. Fais pivoter CTRL_tongue sur ses axes locaux X/Z pour monter le corps de
langue.
5. Sélectionne ensuite CTRL_tongue_tip et fais-le pivoter jusqu’à la zone
alvéolaire derrière les incisives supérieures. Sa translation est verrouillée
par F2 : si G ne le déplace pas, c’est le comportement attendu.
6. Pour /l/, garde le contact de pointe plus étroit ; pour /t d n/, élargis
visuellement le contact sans sortir la langue de la bouche.

Enregistre deux recettes si le rig le permet : DD et NN/L. La racine de la
langue ne doit pas quitter le plancher buccal.

KK — /k g/

1. jawOpen = 0.20.
2. En Pose Mode, sélectionne CTRL_tongue, pas DEF_tongue_body.
3. Déplace le contrôle sur son axe Y local vers l’arrière, puis incline-le pour
monter le dos de langue vers le palais mou.
4. Sélectionne CTRL_tongue_tip, remets sa rotation proche de zéro et laisse la
pointe basse.

CH et SS — /ʃ ʒ/ et /s z/

Pour CH : jaw 0.20, lèvres légèrement projetées avec pucker 0.25 et funnel
0.20, langue large derrière les alvéoles.

Pour SS : jaw 0.12, lipsPart 0.25, stretch L/R 0.20, incisives proches, langue
derrière les incisives sans sortir.

RR — /ʁ/ français

1. jawOpen = 0.18.
2. Laisse la pointe basse.
3. Recule et monte modérément la base/corps de langue.
4. Les lèvres suivent la voyelle voisine ; ne bake pas un pucker permanent dans
RR.

F9.3 — poser les voyelles

Utilise ces valeurs comme départ, puis ajuste sur Atlas :

|Visème|Jaw |Lèvres                       |Langue                 |
|------|---:|-----------------------------|-----------------------|
|`A`   |0.65|ouverture large, peu arrondie|basse et plutôt arrière|
|`E`   |0.30|léger stretch                |milieu/avant           |
|`I`   |0.20|stretch L/R 0.55             |haute et avant         |
|`O`   |0.45|funnel 0.65                  |milieu/arrière         |
|`U`   |0.22|pucker 0.75 + funnel 0.30    |haute et arrière       |
|`Y`   |0.20|pucker 0.65                  |haute et avant         |
|`OE`  |0.30|pucker 0.45 + funnel 0.45    |milieu/avant           |

Dans Blender :

1. sélectionne CTRL_jaw et saisis la valeur ;
2. saisis les propriétés bouche dans le panneau ;
3. passe en vue face, trois-quarts puis coupe sagittale ;
4. déplace les contrôles de langue ;
5. inspecte les racines dentaires et le palais ;
6. sauvegarde la recette dans le JSON, pas sous forme d’une nouvelle shape key
globale.

Si une voyelle exige une forme de lèvre qui n’existe pas, crée uniquement un
résidu VIS_<nom>_residual, puis ajoute son poids à la recette.

Enregistrer réellement une recette

Dans le JSON, jawOpen, mouthStretch.L, etc. sont des canaux logiques.
Le builder les résout par runtime/control-map.json vers une propriété, une
translation de contrôleur ou une shape key. Ne mélange pas dans une même
recette un contrôleur et la shape key qu’il pilote : ce serait une double
application.

Utilise cette structure, y compris quand certaines sections sont vides :

```json
{
  "visemes": {
    "PP": {
      "channels": {"jawOpen": 0.0, "mouthClose": 1.0, "mouthPress": 0.2},
      "bones": {},
      "residuals": {},
      "hold_min_ms": 34
    },
    "FF": {
      "channels": {
        "jawOpen": 0.12,
        "mouthLowerDown.L": 0.2,
        "mouthLowerDown.R": 0.2
      },
      "bones": {},
      "residuals": {"VIS_FF_residual": 0.0},
      "hold_min_ms": 0
    }
  }
}
```

Pour les voyelles, saisis au moins ces valeurs de départ dans channels, puis
ajuste seulement après inspection :

```json
{
  "A":  {"jawOpen": 0.65, "lipsPart": 0.65},
  "E":  {"jawOpen": 0.30, "lipsPart": 0.35, "mouthStretch.L": 0.25, "mouthStretch.R": 0.25},
  "I":  {"jawOpen": 0.20, "lipsPart": 0.25, "mouthStretch.L": 0.55, "mouthStretch.R": 0.55},
  "O":  {"jawOpen": 0.45, "mouthFunnel": 0.65},
  "U":  {"jawOpen": 0.22, "mouthPucker": 0.75, "mouthFunnel": 0.30},
  "Y":  {"jawOpen": 0.20, "mouthPucker": 0.65},
  "OE": {"jawOpen": 0.30, "mouthPucker": 0.45, "mouthFunnel": 0.45}
}
```

Pour ne pas recopier à la main une pose de langue, crée
rig/capture-viseme-pose.py. Dans Blender, pose DD, sauvegarde le .blend,
place le curseur dans une zone Blender, passe-la en Python Console avec
Shift+F4 et lance :

```python
import bpy, runpy
script = bpy.path.abspath("//../rig/capture-viseme-pose.py")
runpy.run_path(script, init_globals={"VIS_NAME": "DD"})
```

Le script externe capture uniquement les contrôleurs, jamais les DEF_* ni
les shape keys pilotées :

```python
import bpy, json
from pathlib import Path

name = VIS_NAME
rig = bpy.data.objects["RIG_Atlas_Face"]
used = ("CTRL_face_root", "CTRL_jaw", "CTRL_tongue", "CTRL_tongue_tip",
        "CTRL_mouth_corner.L",
        "CTRL_mouth_corner.R")
payload = {"name": name, "bones": {}}
for bone_name in used:
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        continue
    payload["bones"][bone_name] = {
        "matrix_basis": [list(row) for row in pb.matrix_basis],
        "custom_properties": {
            key: float(pb[key]) for key in pb.keys()
            if key != "_RNA_UI" and isinstance(pb[key], (int, float))
        }
    }
root = Path(bpy.path.abspath("//")).resolve().parent
out = root / "reports/f9/captures" / f"{name}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"CAPTURED {name}: {out}")
```

Ouvre le JSON produit et vérifie : le nom du visème est correct et seuls les
CTRL_* attendus sont présents. Clique ensuite Reset Face dans Blender : le
rig vivant, lui, doit revenir à l’identité ; le JSON reste naturellement la
pose capturée. Copie ensuite la section bones dans la recette correspondante. Fais
cela pour DD, NN, KK, CH, SS et RR. Si CTRL_tongue ou
CTRL_tongue_tip n’existe pas, arrête et reviens à F2 ; ce sont les deux noms
créés par cette procédure. Ne capture jamais directement DEF_tongue_*.

F9.4 — mapper les phonèmes français

Ajoute :

```text
/p b m/       -> PP
/f v/         -> FF
/t d/         -> DD
/n l/         -> NN
/k g/         -> KK
/ʃ ʒ/         -> CH
/s z/         -> SS
/ʁ/           -> RR
/a ɑ/         -> A
/e ɛ/         -> E
/i/           -> I
/o ɔ/         -> O
/u/           -> U
/y/           -> Y
/ø œ/         -> OE
/j/           -> I avec transition courte
/w/           -> U vers voyelle suivante
/ɥ/           -> Y vers voyelle suivante
/ɑ̃/           -> A, metadata nasal=true
/ɔ̃/           -> O, metadata nasal=true
/ɛ̃ œ̃/        -> E ou OE, metadata nasal=true
```

Le visage seul ne prouve pas la nasalité. N’invente pas un mouvement de nez
obligatoire pour la simuler.

Le bloc précédent est la table humaine. Dans
runtime/phoneme-viseme-fr.json, remplis réellement phonemes avec ce schéma
machine ; le builder doit refuser une entrée qui n’a pas de champ viseme :

```json
{
  "SIL": {"viseme": "SIL"},
  "p": {"viseme": "PP"}, "b": {"viseme": "PP"}, "m": {"viseme": "PP"},
  "f": {"viseme": "FF"}, "v": {"viseme": "FF"},
  "t": {"viseme": "DD"}, "d": {"viseme": "DD"},
  "n": {"viseme": "NN"}, "l": {"viseme": "NN"},
  "k": {"viseme": "KK"}, "g": {"viseme": "KK"},
  "ʃ": {"viseme": "CH"}, "ʒ": {"viseme": "CH"},
  "s": {"viseme": "SS"}, "z": {"viseme": "SS"},
  "ʁ": {"viseme": "RR"},
  "a": {"viseme": "A"}, "ɑ": {"viseme": "A"},
  "e": {"viseme": "E"}, "ɛ": {"viseme": "E"}, "ə": {"viseme": "OE"},
  "i": {"viseme": "I"},
  "o": {"viseme": "O"}, "ɔ": {"viseme": "O"},
  "u": {"viseme": "U"}, "y": {"viseme": "Y"},
  "ø": {"viseme": "OE"}, "œ": {"viseme": "OE"},
  "j": {"viseme": "I", "transition": "short"},
  "w": {"viseme": "U", "transition_to_next": true},
  "ɥ": {"viseme": "Y", "transition_to_next": true},
  "ɑ̃": {"viseme": "A", "nasal": true},
  "ɔ̃": {"viseme": "O", "nasal": true},
  "ɛ̃": {"viseme": "E", "nasal": true},
  "œ̃": {"viseme": "OE", "nasal": true}
}
```

Fusionne cet objet dans la clé phonemes du fichier créé en F9.1 ; ne remplace
pas le document entier par cet extrait.

F9.5 — créer une action d’inspection des visèmes

Crée rig/build-f9-visemes.py. Il lit le JSON et fabrique une Action
ACT_visemes_fr_review à 30 fps :

• 10 images neutres ;
• 10 images de montée ;
• 15 images de tenue ;
• 10 images de retour ;
• 5 images neutres entre visèmes.

Pour les shape keys/propriétés, pose des keyframes. Pour les os de langue et la
mâchoire, bake leurs transforms ou propriétés. Utilise des interpolations
Bezier douces, mais force la fermeture PP avant la tenue.

Helper :

```python
from mathutils import Matrix

def key_custom_prop(pose_bone, name, frame, value):
    pose_bone[name] = float(value)
    pose_bone.keyframe_insert(data_path=f'["{name}"]', frame=frame)

def key_shape(key_block, frame, value):
    key_block.value = float(value)
    key_block.keyframe_insert(data_path="value", frame=frame)

def key_bone_pose(pose_bone, captured, frame):
    pose_bone.matrix_basis = Matrix(captured["matrix_basis"])
    pose_bone.keyframe_insert(data_path="location", frame=frame)
    rotation_path = ("rotation_quaternion" if pose_bone.rotation_mode == 'QUATERNION'
                     else "rotation_axis_angle" if pose_bone.rotation_mode == 'AXIS_ANGLE'
                     else "rotation_euler")
    pose_bone.keyframe_insert(data_path=rotation_path, frame=frame)
    pose_bone.keyframe_insert(data_path="scale", frame=frame)
    for prop, value in captured.get("custom_properties", {}).items():
        key_custom_prop(pose_bone, prop, frame, value)
```

À la lecture, chaque visème doit revenir au neutre avant le suivant. Si un
visème hérite de la langue ou de la mâchoire du précédent, le builder n’a pas
keyframé tous les canaux utilisés : complète le reset de recette.

F9.6 — phrase française et coarticulation

Utilise cette phrase de preuve :

```text
Bonjour, je suis Atlas. Puis-je vous aider ?
```

Crée runtime/french-proof-phonemes.json avec la suite IPA et les timestamps.
Puis crée rig/bake-french-proof.py :

1. pour chaque phonème, récupère le visème ;
2. commence l’anticipation environ 60 à 100 ms avant le centre du phonème ;
3. conserve les fermetures PP suffisamment pour qu’une image au moins soit
complètement fermée ;
4. interpole les lèvres et la langue vers le visème suivant ;
5. laisse les voyelles porter la plus grande partie de la durée ;
6. bake à 60 fps pour le test, même si l’action finale est lue à 30 fps.

S’il n’existe pas encore d’enregistrement audio autoritaire, utilise cette
timeline de preuve déterministe ; elle teste le rig, pas la performance d’un
comédien. Copie-la dans runtime/french-proof-phonemes.json :

```json
{
  "utterance": "Bonjour, je suis Atlas. Puis-je vous aider ?",
  "fps": 60,
  "units": [
    ["b",0,90], ["ɔ̃",90,280], ["ʒ",280,390], ["u",390,560], ["ʁ",560,700],
    ["SIL",700,780], ["ʒ",780,880], ["ə",880,1040], ["SIL",1040,1090],
    ["s",1090,1180], ["ɥ",1180,1280], ["i",1280,1430], ["SIL",1430,1490],
    ["a",1490,1640], ["t",1640,1720], ["l",1720,1820], ["a",1820,1990],
    ["s",1990,2080], ["SIL",2080,2250], ["p",2250,2340], ["ɥ",2340,2440],
    ["i",2440,2570], ["ʒ",2570,2660], ["ə",2660,2780], ["SIL",2780,2840],
    ["v",2840,2940], ["u",2940,3100], ["z",3100,3190], ["e",3190,3350],
    ["d",3350,3440], ["e",3440,3630], ["SIL",3630,3780]
  ],
  "unit_format": ["phoneme", "start_ms", "end_ms"]
}
```

Le builder vérifie que les intervalles sont triés, sans recouvrement, et que
chaque symbole existe dans phonemes. Lorsqu’un audio de référence est fourni,
duplique ce JSON, remplace les timestamps par l’alignement validé et garde le
fichier déterministe pour la non-régression.

Ne somme pas aveuglément deux recettes au-delà de 1. Pour chaque canal :

```python
weight = max(0.0, min(1.0, blended_weight))
```

F9.7 — tests et correction

Crée tests/f9-speech.py. Il vérifie chaque visème isolé et chaque image de la
phrase :

• aucune nouvelle collision lèvres/dents/langue/joues ;
• PP ≤ 0.30 mm ;
• FF au contact sans pénétration > 0.10 mm ;
• pointe de langue contenue sauf geste explicitement visible ;
• racine stable ;
• aucune face inversée ;
• toutes les valeurs entre 0 et 1 ;
• reset final ≤ 0.01 mm ;
• noms de canaux présents dans control-map.json.

Rends la grille de visèmes et la phrase face + coupe bouche. Sauvegarde :

```text
source/ATLAS_FACE_F9_SPEECH.blend
runtime/phoneme-viseme-fr.json
runtime/french-proof-phonemes.json
reports/f9/registre.json
renders/f9/viseme-grid.png
videos/f9/visemes-fr.mp4
videos/f9/phrase-fr.mp4
```

Commande :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f9-speech.py -- \
  source/ATLAS_FACE_F9_SPEECH.blend runtime/phoneme-viseme-fr.json \
  runtime/french-proof-phonemes.json reports/f9/registre.json
```

Si une collision n’apparaît que pendant une transition, corrige la recette ou
ajoute une corrective temporellement activée ; ne valide pas seulement les
poses tenues.

────────

PHASE F10 — INTÉGRATION AU CORPS ET LOD

Résultat à obtenir

Le corps reste le mesh visible continu. Les deltas du visage auteur sont
transférés sur sa zone faciale, les yeux/dents/langue suivent le même repère et
trois niveaux de détail partagent exactement les mêmes noms de morphs et le
même squelette de déformation.

Cette phase exécute en production la stratégie choisie en F0-D. Si
reports/f0-final/DECISION_RACCORD_CORPS.md ne dit pas explicitement
STRATÉGIE RETENUE : TRANSFERT DE DÉFORMATIONS, arrête avant F10.1. La suite
F10.1–F10.6 implémente uniquement cette voie. Si F0-D a retenu
REMPLACEMENT COMPLET, il faut une procédure de production dédiée fondée sur
F0_BODY_REPLACEMENT.blend, body-replacement-plan.json et
body-replacement.json; la phrase « applique la stratégie retenue » ne suffit
pas à autoriser des suppressions de faces. Tant que cette procédure et son gate
manifold/UV ne sont pas écrits, F10 et F12 restent bloqués.

F10.1 — vérifier les entrées et le repère cible

Crée rig/build-f10-body.py. Entrées :

```text
source/ATLAS_FACE_F9_SPEECH.blend
ATLAS_BASE_MESH / Body Male - Realistic
reports/f0-final/head-body-fit.json
reports/f0-final/body-transfer-map.json
reports/f0-final/body-transfer.json
reports/f0-final/DECISION_RACCORD_CORPS.md
```

Le builder :

1. exécute le préflight de ATLAS_BASE_MESH ;
2. ouvre F9 ;
3. sauvegarde sous source/ATLAS_FACE_F10_BODY.blend ;
4. append la collection Body Male - Realistic, puis récupère explicitement
l’objet GEO-body_male_realistic qu’elle contient ;
5. duplique cet objet et renomme la copie GEO_body_runtime_source ;
6. lit M_head_to_body dans head-body-fit.json, puis le masque, les régions
et la correspondance barycentrique dans body-transfer-map.json ;
7. relit body-transfer.json comme rapport de validation des six poses — ce
fichier n’est pas la map ;
8. refuse de recalculer une nearest-surface globale silencieusement si la map
manque.

Dans Blender, affiche le corps et la tête auteur en deux couleurs. Active la
matrice d’alignement sur une copie de la tête. Les yeux, le nez et le menton
doivent rejoindre les repères publiés F0-D. Si ce n’est pas le cas, le builder
utilise un autre repère ou une autre version de l’asset : arrête avant de créer
des morphs.

F10.2 — transférer une shape key sur le corps

La map stocke, pour chaque vertex cible v : triangle source (i0,i1,i2),
poids (b0,b1,b2), masque m et région anatomique.

Pour une shape key source :

```python
delta0 = key.data[i0].co - basis.data[i0].co
delta1 = key.data[i1].co - basis.data[i1].co
delta2 = key.data[i2].co - basis.data[i2].co
delta_head = b0 * delta0 + b1 * delta1 + b2 * delta2
delta_body = M_head_to_body.to_3x3() @ delta_head
target_key.data[v].co = target_basis.data[v].co + m * delta_body
```

Fais d’abord ce test avec SK_eyeBlink.L :

1. crée Basis sur GEO_body_runtime_source sans modifier ses positions ;
2. crée SK_eyeBlink.L ;
3. applique le transfert ;
4. mets sa valeur à 1 ;
5. masque la tête auteur ;
6. inspecte l’œil du corps face et profil ;
7. mesure la différence de delta avec la source reprojetée.

Tu dois voir un blink sur le corps et aucun mouvement du cou. Si la lèvre, la
muqueuse ou l’œil opposé bougent, la région de correspondance ou le masque est
faux ; corrige la map F0-D, pas la shape key source.

Après ce probe, transfère toutes les clés primaires, correctives et résiduelles
utilisées par facs-map.json, correctives-map.json et
phoneme-viseme-fr.json. N’exporte pas les clés temporaires TMP_*.

F10.3 — transférer les poids de peau

Crée sur le corps les groupes DEF_head et DEF_jaw.

Pour chaque vertex mappé, interpole les poids des trois sommets source avec les
mêmes barycentriques, multiplie la composante jaw par le masque facial, puis
normalise :

```python
w_jaw = m * (b0*w0_jaw + b1*w1_jaw + b2*w2_jaw)
w_jaw = max(0.0, min(1.0, w_jaw))
w_head = 1.0 - w_jaw
```

Hors région faciale, attribue DEF_head=1 uniquement si ce rig est le rig
temporaire du corps de démonstration. Si un rig corporel maître existe, mappe
DEF_head au bone de tête du corps et garde les poids du corps hors visage.

Ajoute l’Armature modifier et teste jaw 0/.25/.5/.75/1. Le cou ne doit pas
suivre la mâchoire. Si le visage subit une double transformation, vérifie que
le mesh n’est pas simultanément parenté à l’os et skinné à ce même os.

F10.4 — placer les objets rigides et la langue dans l’espace corps

Duplique pour le runtime :

```text
sclera/iris L/R
GEO_teeth_upper
GEO_teeth_lower
GEO_gums_upper
GEO_gums_lower
GEO_tongue
```

Applique M_head_to_body à leurs données et aux positions de repos des os de
face sur la copie runtime, puis garde les matrices objet à l’identité. Les
arcades restent rigides : supérieure sur DEF_head, inférieure sur DEF_jaw.

Rouvre le neutre et vérifie les contacts dentaires. Une différence d’échelle
non uniforme signifie que la similarité a été appliquée deux fois.

F10.5 — construire LOD0, LOD1 et LOD2

Ne tente pas d’appliquer Decimate sur un objet qui contient déjà toutes les
shape keys. Construis d’abord chaque neutre LOD, puis transfère les morphs.

LOD0

Duplique le corps intégré et renomme :

```text
GEO_body_LOD0
```

LOD0 garde la topologie native du corps. Il reçoit toutes les morphs, les yeux,
les dents, les gencives et la langue.

LOD1

1. Duplique uniquement le Basis de LOD0 dans une scène temporaire et renomme
immédiatement la copie GEO_body_LOD1.
2. Crée un vertex group LOD_PROTECT_FACE à 1 sur paupières, lèvres, nez,
joues et mâchoire ; étends de deux boucles.
3. Sélectionne GEO_body_LOD1, passe en Edit Mode, active la sélection de
sommets et fais Alt+A pour tout désélectionner.
4. Dans Object Data Properties > Vertex Groups, choisis
LOD_PROTECT_FACE, clique Select, puis Ctrl+I. La sélection orange doit
couvrir le corps hors zone protégée ; orbites, lèvres, nez, joue et mâchoire
doivent rester noirs.
5. Lance Mesh > Clean Up > Decimate Geometry. Mets Ratio=0.65, active
Symmetry sur X si le corps est strictement symétrique et valide.
6. Reviens en Object Mode, lis Statistics dans les overlays et mesure les
triangles de la zone hors visage. Si le ratio n’est pas 65 % ± 2 %, annule
cette copie, repars du neutre LOD0 et recalcule le ratio ; n’empile pas deux
décimations.
7. Ne décime aucune face dont les trois sommets sont dans
LOD_PROTECT_FACE.
8. Construis une map barycentrique LOD1 → LOD0.
9. Transfère toutes les morphs et tous les poids par cette map.

Avant d’automatiser, sauvegarde cette opération dans
source/ATLAS_FACE_F10_LOD_WORK.blend et exécute une fois le script par
blender --background sur une copie. Le builder doit explicitement passer
l’objet actif en Edit Mode, rappeler le groupe, inverser la sélection et
appeler l’opérateur ; après chaque opérateur il vérifie le nombre de sommets et
qu’aucun sommet protégé n’a disparu. Une simple présence d’un modificateur
Decimate non appliqué est un échec.

LOD2

Repars à nouveau du Basis LOD0, pas de LOD1. Duplique-le sous
GEO_body_LOD2, recrée LOD_PROTECT_FACE, sélectionne l’extérieur du groupe
comme aux étapes LOD1 et lance Mesh > Clean Up > Decimate Geometry avec
Ratio=0.35. Construis ensuite la map barycentrique LOD2 → LOD0 et transfère
poids et morphs depuis LOD0. Protège au minimum les marges de
paupières/lèvres, les narines et les silhouettes. Les morphs secondaires
peuvent être exclues uniquement si runtime/lod-policy.json le dit ; les noms
restants ne doivent jamais changer.

Le builder publie pour chaque LOD : sommets, triangles, morphs, joints,
influences et erreurs par rapport à LOD0.

F10.6 — tester les LODs

Crée tests/f10-body-lod.py. Poses :

```text
neutral
blink_L/R
smile_duchenne
mouthClose
jawOpen
pucker
viseme_PP
viseme_FF
viseme_A
phrase_frame_worst
```

Pour chaque LOD :

• aucun trou, double surface ou face inversée ;
• UV présentes ;
• même squelette et noms de morphs selon la politique ;
• aucun mouvement de l’anneau de cou dû aux morphs faciales ;
• LOD1 vs LOD0 : p95 surface faciale ≤ 0.50 mm, max ≤ 2 mm ;
• LOD2 vs LOD0 : p95 ≤ 1.00 mm, max ≤ 4 mm ;
• blink et mouthClose conservent leurs seuils de contact ;
• jaw et objets oraux restent solidaires.

Rends la même caméra à trois distances de changement de LOD. Si le changement
produit un saut visible, protège davantage la silhouette ou retarde la distance
de transition ; ne lisse pas le problème dans le master F9.

Sauvegarde :

```text
source/ATLAS_FACE_F10_BODY.blend
runtime/body-transfer-map.json       # copie compacte dérivée du JSON F0, jamais un recalcul
runtime/lod-policy.json
reports/f10/registre.json
reports/f10/lod-stats.json
renders/f10/lod-comparison/
videos/f10/lod-switch.mp4
```

Commandes :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python rig/build-f10-body.py -- \
  source/ATLAS_FACE_F9_SPEECH.blend "$ATLAS_BASE_MESH" \
  reports/f0-final/head-body-fit.json \
  reports/f0-final/body-transfer-map.json \
  reports/f0-final/body-transfer.json \
  reports/f0-final/DECISION_RACCORD_CORPS.md \
  source/ATLAS_FACE_F10_BODY.blend reports/f10/build.json

blender --background --factory-startup --python-exit-code 2 \
  --python tests/f10-body-lod.py -- \
  source/ATLAS_FACE_F10_BODY.blend reports/f10/registre.json renders/f10
```

────────

PHASE F11 — BUILD RUNTIME DENSE, EXPORT GLB ET ROUND-TRIP

Résultat à obtenir

F11 ne touche plus au master auteur. Elle fabrique :

```text
runtime/ATLAS_FACE_RUNTIME.blend
exports/atlas-face-v1.glb             # corps intégré LOD0
exports/atlas-face-lod1-v1.glb
exports/atlas-face-lod2-v1.glb
exports/atlas-face-closeup-v1.glb     # tête dédiée Multires niveau 1 bakée
```

Chaque GLB contient uniquement les meshes runtime, les os de déformation, les
morph targets et les animations bakées. Aucun widget, driver, contrainte ou
Multires n’est nécessaire à la lecture.

F11.1 — dupliquer la tête auteur sans drivers ni Armature

Crée rig/build-runtime-mesh.py. Ouvre
source/ATLAS_FACE_F10_BODY.blend, puis crée une nouvelle scène
RUNTIME_BUILD.

Dans le script :

1. appelle le Reset F8 ou remets explicitement tous les contrôles à zéro ;
2. vérifie que toutes les shape keys valent zéro ;
3. duplique GEO-head_animation_realistic et son datablock ;
4. renomme la copie TMP_face_bake_source ;
5. efface l’animation des Shape Keys de la copie ;
6. retire uniquement l’Armature modifier de la copie ;
7. garde Multires niveau 1 et les modificateurs purement géométriques dont la
décision F0-E autorise le bake ;
8. masque l’original.

```python
bake_src = head.copy()
bake_src.data = head.data.copy()
bpy.context.scene.collection.objects.link(bake_src)
bake_src.name = "TMP_face_bake_source"
if bake_src.data.shape_keys:
    bake_src.data.shape_keys.animation_data_clear()
for mod in list(bake_src.modifiers):
    if mod.type == 'ARMATURE':
        bake_src.modifiers.remove(mod)
    elif mod.type == 'MULTIRES':
        mod.levels = 1
        mod.sculpt_levels = 1
        mod.render_levels = 1
```

Tu dois voir la tête neutre, au même endroit que l’original. Pose brièvement
SK_eyeBlink.L=1 sur la copie : elle doit bouger même si les contrôleurs sont à
zéro. Si un driver reprend le contrôle de la valeur, le Key datablock n’a pas
été correctement dupliqué ou nettoyé.

F11.2 — matérialiser le Basis dense

Ajoute :

```python
def evaluated_mesh_copy(obj):
    obj.data.update()
    obj.update_tag()
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    return bpy.data.meshes.new_from_object(
        ev, preserve_all_data_layers=True, depsgraph=deps)
```

1. Mets toutes les clés de bake_src à zéro.
2. Évalue la surface.
3. Crée un objet avec ce mesh et renomme-le GEO_face_runtime.
4. Copie matrix_world de la tête.
5. Retire tous ses modificateurs.
6. Ajoute sa shape key Basis.
7. Stocke compte de sommets, triangles, loops, UV et signature de connectivité.

La tête évaluée doit retrouver le compte Multires mesuré par le dépôt, autour de
12 950 sommets. Si le compte diffère du banc F0 final, arrête : niveau Multires,
ordre des modificateurs ou version Blender ne correspond pas.

F11.3 — reconstruire chaque morph target dense

Construis la liste depuis les fichiers runtime, pas depuis toutes les clés du
.blend :

```python
ALLOWED_PREFIXES = ("SK_", "CORR_", "VIS_")
FORBIDDEN_PREFIXES = ("TMP_", "TEST_", "DEBUG_")
```

Pour chaque nom utilisé par facs-map.json, correctives-map.json ou
phoneme-viseme-fr.json :

1. mets toutes les clés source à zéro ;
2. mets la clé courante à 1 ;
3. force la mise à jour ;
4. matérialise le mesh évalué ;
5. compare sa signature topologique au Basis dense ;
6. ajoute une shape key du même nom à GEO_face_runtime ;
7. copie les coordonnées locales vertex par vertex ;
8. remets la clé source à zéro ;
9. détruis le mesh temporaire ;
10. vérifie immédiatement la morph runtime à 1.

```python
runtime_key = runtime_obj.shape_key_add(name=shape_name, from_mix=False)
if len(eval_mesh.vertices) != len(runtime_key.data):
    raise RuntimeError(f"topologie évaluée différente pour {shape_name}")
for i, v in enumerate(eval_mesh.vertices):
    runtime_key.data[i].co = v.co
runtime_key.value = 0.0
```

Le test visuel doit montrer la même silhouette source/runtime lorsque seule
cette clé vaut 1. Si le détail saute, compare l’ordre des modificateurs et
vérifie que Multires était à 1 pour Basis et morph.

F11.4 — interpoler les poids vers la tête dense

Les vertex groups appartiennent à l’objet cage et ne sont pas garantis sur le
mesh créé depuis l’évaluation. Construis une correspondance dense → cage sur le
neutre :

1. triangule canoniquement la cage Basis sans modifier l’original ;
2. construit un BVH des triangles ;
3. pour chaque vertex dense, trouve le triangle cage le plus proche ;
4. calcule ses barycentriques ;
5. interpole chaque poids DEF_* ;
6. retire les poids < 1e-5 ;
7. garde au plus quatre poids ;
8. renormalise exactement à 1.

Pour Atlas face, la majorité des sommets ne doit avoir que DEF_head ou le
couple DEF_head/DEF_jaw. Si un vertex de paupière reçoit un poids d’œil, la
projection a traversé une région : segmente la correspondance avant de relancer.

Après transfert, pose jaw 1 sur la tête runtime et compare au master évalué :

• p95 ≤ 0.10 mm ;
• max ≤ 0.50 mm ;
• aucun déplacement du crâne dû à la limitation à quatre poids.

F11.5 — créer l’armature d’export

Crée rig/build-export-rig.py. Dans la scène runtime, ajoute
RIG_Atlas_Export avec un root commun et uniquement :

```text
DEF_root
DEF_head
DEF_jaw
DEF_eye.L
DEF_eye.R
DEF_tongue_base
DEF_tongue_body
DEF_tongue_tip
```

Si les gencives ou un autre objet nécessitent réellement un joint distinct,
ajoute-le et documente-le ; n’exporte pas CTRL_, MCH_ ni WGT_.

Dans Edit Mode du rig d’export :

1. copie les matrices de repos monde des os DEF auteur ;
2. convertis-les en espace objet du rig d’export ;
3. reparent DEF_head à DEF_root ;
4. reparent jaw et eyes à head en conservant les matrices de repos ;
5. reconstitue la chaîne de langue sous jaw ;
6. vérifie échelle 1, rotation objet nulle, determinant positif.

Remplace l’Armature modifier des meshes runtime par un modifier visant
RIG_Atlas_Export. Les noms des vertex groups restent identiques.

F11.6 — baker les animations de preuve

Crée au minimum :

```text
ACT_test_jaw
ACT_test_gaze
ACT_test_facs
ACT_visemes_fr_review
ACT_phrase_fr
```

Pour chaque action auteur :

1. active l’action ;
2. pour chaque frame entière, force l’évaluation ;
3. copie la matrice monde évaluée de chaque os DEF vers l’os homonyme du rig
d’export ;
4. convertis en matrice locale relative au parent export ;
5. insère location + quaternion rotation + scale ;
6. copie les valeurs finales de morph targets sur le mesh runtime ;
7. insère les keyframes de morph weights ;
8. applique une simplification seulement après avoir mesuré l’erreur.

Le bake doit reproduire les contraintes et drivers, pas les exporter.

Teste frame début/milieu/fin : erreur os ≤ 0.1° et 0.10 mm, erreur de
surface p95 ≤ 0.10 mm, max ≤ 0.50 mm.

F11.7 — assembler les collections export

Crée :

```text
EXPORT_FACE_CLOSEUP
EXPORT_BODY_LOD0
EXPORT_BODY_LOD1
EXPORT_BODY_LOD2
```

Chaque collection contient :

• son mesh principal ;
• yeux ;
• dents/gencives ;
• langue ;
• RIG_Atlas_Export ou sa copie liée appropriée ;
• aucune caméra/lumière/widget/mesh auteur.

Avant export, affiche seulement la collection cible. Tu dois voir un personnage
correct en neutre. Si masquer les collections auteur fait disparaître un objet
nécessaire, cet objet n’a pas été copié dans la collection runtime.

Sauvegarde maintenant runtime/ATLAS_FACE_RUNTIME.blend.

F11.8 — introspecter l’exporteur puis exporter

Ne suppose pas que les noms d’arguments sont identiques entre Blender 5.1.2 et
5.2. Ajoute dans rig/export-gltf.py :

```python
available = {
    p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties
}

requested = {
    "filepath": output_path,
    "export_format": 'GLB',
    "use_selection": True,
    "export_apply": False,
    "export_animations": True,
    "export_skins": True,
    "export_morph": True,
    "export_morph_normal": True,
}

required = {"filepath", "export_format", "use_selection",
            "export_animations", "export_skins", "export_morph"}
missing = required - available
if missing:
    raise RuntimeError(f"options glTF absentes sous {bpy.app.version_string}: {missing}")
kwargs = {k: v for k, v in requested.items() if k in available}
```

Puis sélectionne explicitement :

```python
bpy.ops.object.select_all(action='DESELECT')
objects = list(export_collection.all_objects)
for obj in objects:
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True)
bpy.context.view_layer.objects.active = next(
    o for o in objects if o.type == 'ARMATURE'
)
result = bpy.ops.export_scene.gltf(**kwargs)
if 'FINISHED' not in result:
    raise RuntimeError(f"export glTF échoué: {result}")
```

export_apply=False reste obligatoire parce que le runtime mesh est déjà baké
et porte ses morph targets. Vérifie dans le log que l’exporteur n’annonce aucune
morph ignorée.

Commandes :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python rig/build-runtime-mesh.py -- \
  source/ATLAS_FACE_F10_BODY.blend runtime/ATLAS_FACE_RUNTIME.blend \
  reports/f11/runtime-build.json

blender --background --factory-startup --python-exit-code 2 \
  --python rig/export-gltf.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend EXPORT_BODY_LOD0 \
  exports/atlas-face-v1.glb reports/f11/export-lod0.json

blender --background --factory-startup --python-exit-code 2 \
  --python rig/export-gltf.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend EXPORT_BODY_LOD1 \
  exports/atlas-face-lod1-v1.glb reports/f11/export-lod1.json

blender --background --factory-startup --python-exit-code 2 \
  --python rig/export-gltf.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend EXPORT_BODY_LOD2 \
  exports/atlas-face-lod2-v1.glb reports/f11/export-lod2.json

blender --background --factory-startup --python-exit-code 2 \
  --python rig/export-gltf.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend EXPORT_FACE_CLOSEUP \
  exports/atlas-face-closeup-v1.glb reports/f11/export-closeup.json
```

Après chaque commande, ouvre son JSON et vérifie status="PASS", le chemin
absolu résolu, la collection utilisée et un fichier GLB de taille non nulle.
Si un export échoue, ne lance pas le suivant avant d’avoir corrigé la
collection ou l’option indiquée.

F11.9 — valider avec Khronos

Dans tools/, crée un petit environnement Node verrouillé :

```bash
cd tools
npm init -y
npm install --save-exact gltf-validator@2.0.0-dev.3.10
cd ..
```

Crée tools/validate-gltf.cjs :

```javascript
const fs = require('node:fs');
const validator = require('gltf-validator');

const input = process.argv[2];
const output = process.argv[3];
if (!input || !output) throw new Error('usage: validate-gltf input.glb report.json');

const bytes = new Uint8Array(fs.readFileSync(input));
validator.validateBytes(bytes, { uri: input, maxIssues: 10000 })
  .then((report) => {
    fs.writeFileSync(output, JSON.stringify(report, null, 2));
    const errors = report.issues?.numErrors || 0;
    const warnings = report.issues?.numWarnings || 0;
    console.log(JSON.stringify({errors, warnings}));
    process.exit(errors === 0 ? 0 : 2);
  })
  .catch((err) => { console.error(err); process.exit(2); });
```

Lance :

```bash
node tools/validate-gltf.cjs \
  exports/atlas-face-v1.glb reports/f11/khronos-lod0.json

node tools/validate-gltf.cjs \
  exports/atlas-face-lod1-v1.glb reports/f11/khronos-lod1.json

node tools/validate-gltf.cjs \
  exports/atlas-face-lod2-v1.glb reports/f11/khronos-lod2.json

node tools/validate-gltf.cjs \
  exports/atlas-face-closeup-v1.glb reports/f11/khronos-closeup.json
```

Le gate exige zéro erreur. Chaque warning doit être expliqué dans le rapport ;
ne transforme pas automatiquement “0 erreur” en “tout est correct”.

F11.10 — round-trip Blender chiffré

Crée tests/f11-gltf-roundtrip.py.

1. démarre avec --factory-startup ;
2. importe le GLB ;
3. vérifie le nombre de meshes, skins, joints, morphs et actions ;
4. compare la liste ordonnée des morph names au manifeste runtime ;
5. joue Basis, chaque morph isolée et les animations de preuve ;
6. compare au runtime .blend.

Le GLB peut trianguler, réordonner ou dupliquer des vertices aux coutures UV.
Ne compare pas les indices bruts. Pour le neutre et chaque pose de référence :

1. transforme les deux surfaces en monde ;
2. construit un BVH source et un BVH importé ;
3. mesure source→import et import→source ;
4. publie p50/p95/max dans les deux sens ;
5. compare aussi les tuples UV sur les points correspondants.

Gates :

• géométrie p95 ≤ 0.10 mm, max ≤ 0.50 mm ;
• UV max ≤ 1e-6 lorsque la correspondance est définie ;
• rotation os ≤ 0.1° ;
• translation os ≤ 0.10 mm ;
• aucun morph/action/joint manquant ;
• valeurs de poids normalisées ;
• aucune nouvelle collision dans les poses de preuve.

Commande :

```bash
blender --background --factory-startup --python-exit-code 2 \
  --python tests/f11-gltf-roundtrip.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend exports/atlas-face-v1.glb \
  reports/f11/roundtrip-lod0.json renders/f11/roundtrip-lod0

blender --background --factory-startup --python-exit-code 2 \
  --python tests/f11-gltf-roundtrip.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend exports/atlas-face-lod1-v1.glb \
  reports/f11/roundtrip-lod1.json renders/f11/roundtrip-lod1

blender --background --factory-startup --python-exit-code 2 \
  --python tests/f11-gltf-roundtrip.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend exports/atlas-face-lod2-v1.glb \
  reports/f11/roundtrip-lod2.json renders/f11/roundtrip-lod2

blender --background --factory-startup --python-exit-code 2 \
  --python tests/f11-gltf-roundtrip.py -- \
  runtime/ATLAS_FACE_RUNTIME.blend exports/atlas-face-closeup-v1.glb \
  reports/f11/roundtrip-closeup.json renders/f11/roundtrip-closeup
```

Si le validator passe mais le round-trip échoue, corrige le builder/export :

• morph manquante : liste d’export ou nom TMP_* mal filtré ;
• pose jaw différente : bind matrices/parentage du rig export ;
• UV différentes : mesh évalué ou duplication de couture ;
• animation absente : Action non stashed/NLA ou option export ;
• surface différente uniquement à 1 : normals/morph ou ordre dense instable.

F11.11 — test dans le runtime réel

Crée le viewer, installe ses dépendances une seule fois et conserve
package-lock.json :

```bash
mkdir -p tests/runtime-viewer/src tests/runtime-viewer/public
cd tests/runtime-viewer
npm init -y
npm install --save-exact three vite
npm pkg set scripts.dev="vite --host 127.0.0.1"
cp ../../exports/atlas-face-v1.glb public/atlas-face-v1.glb
cd ../..
```

Le GLB sous public/ est une copie générée de test : ajoute
tests/runtime-viewer/public/*.glb au .gitignore, mais garde le GLB autoritaire
dans exports/.

Crée tests/runtime-viewer/index.html :

```html
<!doctype html>
<meta charset="utf-8">
<title>Atlas Face runtime probe</title>
<style>body{margin:0}#ui{position:fixed;z-index:2;background:#fff;padding:8px}canvas{display:block}</style>
<div id="ui">
  <select id="morph"></select><input id="weight" type="range" min="0" max="1" step="0.01" value="0">
  <select id="clip"></select><button id="play">Play</button><pre id="status">loading</pre>
</div>
<script type="module" src="/src/main.js"></script>
```

Crée tests/runtime-viewer/src/main.js :

```javascript
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x30343b);
const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 0.001, 1000);
const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x303030, 2.0));
const key = new THREE.DirectionalLight(0xffffff, 3.0); key.position.set(2, 3, 4); scene.add(key);

const morphSelect = document.querySelector('#morph');
const weight = document.querySelector('#weight');
const clipSelect = document.querySelector('#clip');
const status = document.querySelector('#status');
let mixer, morphMeshes = [], clips = [];

new GLTFLoader().load('/atlas-face-v1.glb', (gltf) => {
  scene.add(gltf.scene);
  gltf.scene.traverse((o) => {
    if (o.isMesh && o.morphTargetDictionary) morphMeshes.push(o);
  });
  const names = [...new Set(morphMeshes.flatMap(o => Object.keys(o.morphTargetDictionary)))].sort();
  for (const name of names) morphSelect.add(new Option(name, name));
  clips = gltf.animations;
  for (const clip of clips) clipSelect.add(new Option(clip.name, clip.name));
  mixer = new THREE.AnimationMixer(gltf.scene);

  const box = new THREE.Box3().setFromObject(gltf.scene);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  controls.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(0, size * 0.1, size * 0.8));
  camera.near = Math.max(size / 10000, 0.001); camera.far = size * 10;
  camera.updateProjectionMatrix(); controls.update();
  status.textContent = JSON.stringify({meshes:morphMeshes.length, morphs:names.length,
                                       animations:clips.map(c => c.name)}, null, 2);
}, undefined, (error) => { status.textContent = String(error); throw error; });

weight.addEventListener('input', () => {
  const name = morphSelect.value, value = Number(weight.value);
  for (const mesh of morphMeshes) {
    const index = mesh.morphTargetDictionary[name];
    if (index !== undefined) mesh.morphTargetInfluences[index] = value;
  }
});
document.querySelector('#play').addEventListener('click', () => {
  const clip = THREE.AnimationClip.findByName(clips, clipSelect.value);
  if (!clip) throw new Error(`animation absente: ${clipSelect.value}`);
  mixer.stopAllAction(); mixer.clipAction(clip).reset().play();
});
const clock = new THREE.Clock();
renderer.setAnimationLoop(() => { if (mixer) mixer.update(clock.getDelta()); renderer.render(scene, camera); });
addEventListener('resize', () => { camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight); });
```

Lance cd tests/runtime-viewer && npm run dev, puis ouvre l’URL locale affichée
par Vite. Le panneau doit afficher un nombre de meshes/morphs non nul et les
actions bakées ; une erreur de chargement visible dans status est un FAIL.

Dans le viewer :

1. charge atlas-face-v1.glb ;
2. active SK_eyeBlink.L ;
3. active SK_mouthSmile.L/R ;
4. joue ACT_phrase_fr ;
5. vérifie skin + morph simultanés ;
6. capture le neutre et les cinq poses de référence.

Enregistre les captures sous renders/f11/runtime-viewer/ et copie dans
reports/f11/runtime-viewer.json les versions de Node, Three, Vite et du
navigateur, ainsi que les noms réellement lus dans le GLB. Arrête le serveur
avec Ctrl+C après les captures.

Si Blender round-trip passe mais Three.js échoue, inspecte targetNames, le
nom de l’action et le nombre d’influences. Ne modifie pas le master auteur pour
contourner un problème de chargement runtime.

────────

PHASE F12 — QA FINALE, PREUVES ET CLÔTURE V1

Résultat à obtenir

F12 rejoue tout depuis les fichiers publics, produit les preuves fixes et
ferme la V1 uniquement si le master, les GLB et le viewer donnent le même Atlas.

F12.1 — lancer depuis un arbre propre

Avant les tests :

```bash
git status --short
git diff --exit-code
git diff --cached --exit-code
```

Ne lance pas de reset destructeur si l’arbre est sale. Note les fichiers et
sépare les changements de QA des modifications utilisateur.

Crée tests/run-f12-final.py comme runner hôte. Il exécute les tests F5 à F11,
stocke commande/code/durée et continue uniquement pour collecter les preuves
autorisées. Toute phase inattendue en échec rend le résultat global faux.

F12.2 — vérifier le master auteur

Ouvre source/ATLAS_FACE_F9_SPEECH.blend avec le panneau F8.

1. Clique Reset Face.
2. Inspecte le neutre face, profils et coupe.
3. Manipule chaque contrôleur 2D jusqu’à ses limites.
4. Relâche avec Alt+G.
5. Joue jaw, regard, langue, chaque AU et chaque visème.
6. Joue les combinaisons F7 et la phrase française.

Tu dois voir les mêmes formes que dans les planches validées. Si le neutre est
différent après lecture, identifie le canal non reset dans le test F8 ; ne
sauvegarde pas le fichier dans cet état.

Le runner vérifie automatiquement :

• empreinte topologique finale ;
• Basis et UV ;
• aucun NaN/Inf ;
• retour neutre ≤ 0.01 mm ;
• yeux ≤ 0.20 mm au blink ;
• lèvres ≤ 0.30 mm au close/PP ;
• aucune nouvelle collision hors whitelist neutre ;
• aucun driver invalide ;
• toutes les recettes pointent vers des canaux existants.

F12.3 — vérifier le package runtime

Ouvre runtime/ATLAS_FACE_RUNTIME.blend.

1. Masque les collections non exportées.
2. Sélectionne RIG_Atlas_Export.
3. Vérifie qu’aucun bone CTRL_ ou MCH_ n’existe.
4. Sélectionne chaque mesh et vérifie l’absence de Multires, driver et
contrainte non bakée.
5. Vérifie quatre influences maximum et somme 1.
6. Joue les actions bakées.

Teste l’indépendance uniquement sur une copie jetable : fais
File > Save As, écris /tmp/ATLAS_FACE_RUNTIME_ISOLATION.blend, décoche
Remap Relative, puis supprime dans cette copie toutes les collections
auteur et rends une pose. Ferme sans réécrire
runtime/ATLAS_FACE_RUNTIME.blend. Si l’image change ou si un résultat
disparaît, une dépendance non runtime subsiste ; le test est FAIL et la copie
/tmp n’est jamais livrée.

F12.4 — produire les preuves standardisées

Crée tests/f12-renders.py. Calcule les caméras, l’éclairage et l’exposition
sur le neutre une seule fois, puis verrouille-les.

Rends :

```text
neutral_front / profile_L / profile_R / threequarter_L / threequarter_R
jaw_00_10_20_32
gaze_9_positions
blink_L/R_000_050_100
mouthClose_000_050_100
FACS chaque AU 0/50/100
combinaisons prioritaires 5x5
viseme_grid_fr
phrase_fr keyframes
LOD0/1/2 mêmes caméras
source_vs_glb mêmes poses
wireframes yeux/lèvres/narines/cou
coupe sagittale deux couleurs avec règle 10 mm
```

Chaque image reçoit en marge : fichier, commit, Blender, pose, valeurs et LOD.
Ne mets pas ces textes sur la zone anatomique.

Crée aussi :

```text
videos/f12/all-controls.mp4
videos/f12/facs.mp4
videos/f12/visemes-fr.mp4
videos/f12/source-vs-glb.mp4
videos/f12/lod-switch.mp4
```

Si une caméra ou exposition varie entre deux poses comparées, invalide la
planche et rerends-la ; ne recadre pas à la main une seule image.

F12.5 — test d’hygiène et manifeste

Depuis la racine du dépôt, commence par les fichiers texte. Ces commandes ne
doivent produire aucune ligne non expliquée :

```bash
rg -n --hidden --glob '!*.blend' --glob '!*.glb' \
  '(ghp_|github_pat_|AKIA[0-9A-Z]{16}|-----BEGIN .*PRIVATE KEY-----)' .

rg -n --hidden --glob '!*.blend' --glob '!*.glb' \
  '(/Users/[^/ ]+|/home/[^/ ]+|[A-Za-z]:\\\\Users\\\\)' .
```

Si une ligne contient réellement un secret, retire-le du fichier source et
révoque-le hors de ce tutoriel ; ne copie jamais sa valeur dans le rapport.
Pour un faux positif, note seulement chemin, ligne, motif et décision
false_positive.

Crée ensuite tests/f12-hygiene-blend.py. Il ouvre chaque .blend livré et
écrit dans un JSON : noms des Text datablocks, bpy.data.libraries, chemins
d’images, sons, caches et fichiers externes. Lance-le explicitement :

```bash
blender --background source/ATLAS_FACE_F9_SPEECH.blend \
  --python-exit-code 2 --python tests/f12-hygiene-blend.py -- \
  reports/f12/hygiene-master.json

blender --background runtime/ATLAS_FACE_RUNTIME.blend \
  --python-exit-code 2 --python tests/f12-hygiene-blend.py -- \
  reports/f12/hygiene-runtime.json
```

Ouvre les deux JSON. Le runtime doit avoir zéro Text datablock, zéro library
liée et zéro chemin absolu. Le master ne garde un Text datablock que s’il est
nommé dans une whitelist publique avec sa justification. Reviens dans Blender,
sélectionne le datablock fautif dans l’Outliner en mode Blender File, fais
Unlink, sauvegarde, rouvre et relance le scan.

Crée audit/deliverables.json avec la liste exacte des fichiers livrés. Elle
inclut les .blend, quatre GLB, JSON runtime, rapports, documents et preuves,
mais exclut caches, /tmp, node_modules, le mesh source de 47 Mo et le
manifeste lui-même. Crée tests/f12-manifest.py qui lit cette liste, refuse un
chemin absolu ou contenant .., refuse un fichier manquant, calcule SHA-256
par blocs, écrit audit/manifest-sha256.txt, puis relit et revérifie chaque
hash :

```python
import hashlib, json
from pathlib import Path

root = Path.cwd().resolve()
manifest = root / "audit/manifest-sha256.txt"
items = json.loads((root / "audit/deliverables.json").read_text("utf-8"))
paths = []
for raw in items["files"]:
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts or rel == Path("audit/manifest-sha256.txt"):
        raise SystemExit(f"chemin interdit: {raw}")
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"fichier manquant: {raw}")
    paths.append((rel, path))

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

lines = [f"{digest(path)}  {rel.as_posix()}" for rel, path in sorted(paths)]
manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
for line in manifest.read_text("utf-8").splitlines():
    expected, raw = line.split("  ", 1)
    if digest(root / raw) != expected:
        raise SystemExit(f"hash différent au second passage: {raw}")
print(f"MANIFEST_OK files={len(lines)}")
```

Lance python3 tests/f12-manifest.py. Le résultat visible attendu est
MANIFEST_OK files=<nombre> et le nombre doit égaler la longueur de
audit/deliverables.json. Un chemin externe réellement nécessaire doit être
supprimé, packé légalement ou documenté comme blocage ; il ne peut pas être
masqué dans le rapport.

F12.6 — rapport final et statut

Crée :

```text
reports/f12/FINAL_QA.json
reports/f12/RAPPORT_V1_FINAL.md
reports/f12/commands.json
reports/f12/performance.json
audit/AUDIT_PACKET_FACE_V1.md
```

performance.json publie sans inventer de cible : taille GLB, sommets,
triangles, morphs, joints, temps de chargement du viewer, frame time médian/p95
sur la machine de test et version GPU/navigateur.

Mets à jour les documents vivants :

```text
README.md
STATUS.md
CHANGELOG.md (nouvelle section, sans réécrire F0 historique)
handoffs/HANDOFF_FACE_NEXT.md
docs/FACS_MATRIX.md
docs/VISEME_MATRIX.md
```

Le statut ne peut devenir :

```text
V1 VALIDÉE
```

que si : runner code 0, Khronos zéro erreur, round-trip sous seuil, viewer
validé, preuves présentes, manifeste vérifié et aucun FAIL caché dans un JSON.

F12.7 — commande finale

```bash
python3 tests/run-f12-final.py \
  --master source/ATLAS_FACE_F9_SPEECH.blend \
  --body source/ATLAS_FACE_F10_BODY.blend \
  --runtime runtime/ATLAS_FACE_RUNTIME.blend \
  --glb-lod0 exports/atlas-face-v1.glb \
  --glb-lod1 exports/atlas-face-lod1-v1.glb \
  --glb-lod2 exports/atlas-face-lod2-v1.glb \
  --glb-closeup exports/atlas-face-closeup-v1.glb \
  --report reports/f12/FINAL_QA.json \
  --commands-report reports/f12/commands.json
```

Le runner imprime à la fin uniquement l’un de ces résultats :

```text
ATLAS_FACE_V1_VALIDEE
ATLAS_FACE_V1_ECHEC
```

En cas d’échec, le rapport nomme la première phase autoritaire à reprendre :

• forme isolée fautive → F5/F6 ;
• combinaison fautive → F7 ;
• driver/reset → F8 ;
• articulation française → F9 ;
• corps/LOD → F10 ;
• bake/export/round-trip → F11 ;
• preuve ou documentation seulement → F12.

Corrige au niveau source le plus ancien, puis régénère toutes les phases aval.
Ne corrige jamais directement un GLB ou un LOD final à la main.

────────

Annexe A — que faire exactement quand une étape bloque

A.1 — ne pas continuer à bricoler le master

Au premier résultat incompréhensible :

1. n’enregistre pas le fichier de phase ;
2. clique File → Save As ;
3. enregistre une copie dans
work/diagnostics/<leçon>_<symptôme>.blend ;
4. fais une capture de face et une de profil ;
5. note la dernière action qui fonctionnait ;
6. ferme puis rouvre la copie pour savoir si le défaut persiste.

Si le défaut disparaît après réouverture, le problème venait probablement de
l’état du depsgraph, d’une sélection active ou d’une mise à jour non forcée.

A.2 — afficher les erreurs Blender

Depuis l’interface

1. Clique Window → Toggle System Console sous Windows.
2. Sous macOS/Linux, lance Blender depuis le terminal utilisé dans la leçon.
3. Reproduis une seule fois le problème.
4. Copie la première erreur Python complète, depuis Traceback jusqu’à la
dernière ligne.

Depuis le fichier Blender

1. Passe une zone en Python Console avec Shift + F4.
2. Exécute :

```python
import bpy
print(bpy.app.version_string)
print(bpy.context.mode)
print(bpy.context.active_object)
print([o.name for o in bpy.context.selected_objects])
```

Ces quatre lignes répondent aux causes les plus fréquentes : mauvaise version,
mauvais mode, mauvais objet actif ou mauvaise sélection.

A.3 — réduire le problème

Ne teste pas une solution inconnue sur le visage complet.

Exemple pour un problème Multires/shape key :

1. crée un nouveau fichier avec File → New → General ;
2. supprime caméra et lumière ;
3. garde le cube ;
4. ajoute Object Data Properties → Shape Keys → + → + ;
5. ajoute Modifiers → Multiresolution ;
6. clique Subdivide une fois ;
7. reproduis uniquement l’action fautive ;
8. sauvegarde work/diagnostics/minimal_multires_shapekey.blend.

Si le cube échoue aussi, cherche un bug/version. Si seul Atlas échoue, cherche
une interaction propre à sa pile, ses données ou son contexte.

Pour un échec qui combine précisément Multires et Shape Keys, garde Blender
5.1.2 comme version de production, puis ouvre une copie jetable du fichier
minimal sous Blender 5.2 LTS. Les correctifs récents autour de Apply Base et
de la sculpture de la base avec des shape keys peuvent changer le diagnostic.
Si la copie fonctionne en 5.2 mais pas en 5.1.2, documente le différentiel ; ne
migre pas le master ni les fichiers de phase sans décision explicite.

A.4 — ordre de recherche

Cherche dans cet ordre :

1. manuel Blender correspondant à l’opérateur ;
2. API bpy de la propriété ;
3. notes de version Blender 5.1 ;
4. cours Blender Studio Advanced Facial Rigging ;
5. bug tracker Blender avec une reproduction minimale ;
6. Blender Stack Exchange ;
7. Blender Artists ;
8. vidéo seulement si elle montre la version et tous les réglages.

Ne copie jamais une expression ou un script de forum directement dans le
master. Teste-le d’abord dans la copie de diagnostic.

A.5 — requêtes utiles par symptôme

|Ce que tu vois                  |Recherche à copier                                          |
|--------------------------------|------------------------------------------------------------|
|la shape key ne bouge rien      |`Blender active relative shape key edit mode value 1`       |
|Multires change après sculpt    |`Blender 5.1 Multires sculpt base mesh shape keys`          |
|paupière traverse la cornée     |`Blender eyelid corneal bulge shape key signed distance`    |
|canthus reste ouvert            |`eyelid canthus closure topology facial rig`                |
|commissure reste fendue         |`facial rig lip seal mouth corner topology`                 |
|mâchoire tourne autour du menton|`Blender jaw rig condyle pivot TMJ`                         |
|œil fait un flip                |`Blender Damped Track eye bone roll flip`                   |
|driver devient violet           |`Blender invalid driver target data path`                   |
|une joue entraîne l’autre       |`Blender shape key left right mask delta`                   |
|corrective double la pose       |`Blender corrective shape key residual subtract base shapes`|
|morphs absents du GLB           |`Blender glTF Apply Modifiers shape keys missing`           |
|animation diffère après import  |`Blender glTF bake visual transforms constraints`           |
|/y/ français ressemble à /i/    |`French rounded front vowel viseme y IPA lips`              |

A.6 — fiche de recherche

Pour toute recherche qui dépasse vingt minutes, crée :

```text
docs/recherche/YYYY-MM-DD-sujet.md
```

Puis remplis :

```markdown
# Symptôme visible

# Action exacte qui le déclenche

# Version Blender et commit

# Fichier minimal

# Hypothèse testée

# Source

# Résultat du test

# Décision
```

Une source consultée sans expérience reproduite ne suffit pas à modifier le
rig.

────────

Annexe B — sauvegarder, revenir en arrière et reprendre

B.1 — sauvegarde de leçon

À la fin d’une manipulation qui fonctionne :

1. File → Save ;
2. ferme Blender ;
3. rouvre le fichier ;
4. rejoue la pose test ;
5. exécute le mini-test ;
6. seulement ensuite, ajoute les fichiers à Git.

B.2 — commit de progression

Dans le terminal :

```bash
git status --short
git diff --check
git diff --stat
```

Ajoute uniquement les fichiers de la leçon :

```bash
git add -- \
  source/<fichier-de-phase>.blend \
  rig/<builder-de-phase>.py \
  tests/<test-de-phase>.py \
  reports/<phase>/ \
  renders/<phase>/
```

Puis :

```bash
git commit -m "feat(face): complete <nom-de-la-leçon>"
```

Ne lance jamais git reset --hard pour corriger une mauvaise pose Blender.
Repars du dernier fichier de phase signé.

────────

Annexe C — livraison finale

Quand toutes les leçons sont terminées :

1. ouvre exports/atlas-face-v1.glb dans le viewer cible ;
2. teste neutre, jaw, regard, blink, sourire et phrase française ;
3. compare aux rendus Blender ;
4. vérifie la console du viewer ;
5. relance Khronos glTF Validator ;
6. fais un clone propre du dépôt ;
7. reconstruis le GLB depuis ce clone ;
8. compare les SHA ;
9. publie les images avant/après ;
10. écris les limites connues.

Commande de contrôle final :

```bash
git status --short
git log -1 --oneline
sha256sum exports/atlas-face-v1.glb
```

Le rig est livré seulement si le clone propre permet de refaire le même asset,
pas seulement si le .blend local fonctionne sur la machine de construction.

────────

Sources à garder ouvertes pendant le travail

• Blender Manual — Shape Keys
• Blender Manual — Armature Modifier
• Blender Manual — Multiresolution
• Blender Manual — Drivers
• Blender Manual — glTF 2.0
• Blender Studio — Advanced Facial Rigging
• Khronos glTF 2.0
• Khronos glTF Validator
• Paul Ekman Group — FACS
• International Phonetic Association