# F0-A — reprise de `c0885ae` et pipeline rendu honnête

Voir [`ETAT_C0885AE.md`](ETAT_C0885AE.md) pour l'état de départ vérifié.

## F0-A.5 — les codes de sortie disaient le contraire du JSON

`tests/f0-multires-v2.py` et `tests/f0-raccord-corps.py` publiaient un registre
en **ÉCHEC** et rendaient pourtant **0** au shell. Corrigé : `sys.exit(0 if ok
else 2)`. **Aucune constante de seuil n'a été touchée** — les mêmes trois FAIL
et les mêmes cinq mesures sortent, seul le code change.

Trois témoins fixent la convention, mesurée et non supposée
([`experiments/f0-exit-code/`](../../../experiments/f0-exit-code/README.md)) :

| script | attendu | observé |
| --- | ---: | ---: |
| `pass.py` | 0 | **0** |
| `echec_metier.py` | 2 | **2** |
| `echec_technique.py` (lève `RuntimeError`) | 1 | **1** |

Blender ne remappe donc pas `sys.exit` : **0 = succès, 2 = échec métier,
1 = panne technique**.

`tests/f0-preuves-visuelles.py` imprimait `PREUVES_OK` **sans rien vérifier**.
Il valide désormais, pour chaque image : existence, dimensions non nulles, plus
d'une couleur, caméra signée au manifeste, côté conforme au nom, et **caméra
identique entre les intensités d'un même prototype**. Il écrit
`reports/f0-final/preuves-visuelles.json` et sort en 0 ou 2.

> Première version de ce validateur : elle groupait `coupe_sagittale_generale`,
> `_bouche` et `_oeil` dans une même « famille » et exigeait qu'elles partagent
> une caméra. Ce sont trois cadrages volontairement différents. La règle
> corrigée ne groupe que les vues dont le dernier segment est un **nombre**
> — les intensités d'un même geste.

## F0-A.6 — runner baseline/final

`tests/run-f0-final.py` lance chaque suite par `subprocess` avec **une liste
d'arguments**, jamais `shell=True`, et enregistre argv, code brut, durée,
stdout, stderr et chemins produits dans `commandes.json`.

Le mode `baseline` compare des **ensembles d'identifiants**, pas des comptes :

```
[PASS] verrou_positif   code=0  fail=0 skip=0
[PASS] verrou_negatif   code=0  fail=0 skip=0
[PASS] multires         code=2  fail=3 skip=2
[PASS] raccord          code=2  fail=2 skip=0
[PASS] hygiene          code=1  fail=1 skip=0
RUNNER PASS
```

Il passe **parce que les échecs correspondent**, pas parce qu'ils ont disparu.

**Contre-épreuve** : un identifiant retiré d'une *copie* du baseline
(`clignement.A_cage.gap_ferme_L`) fait bien échouer le runner —
`nouveaux_fail : ['clignement.A_cage.gap_ferme_L']` — et le baseline versionné
est resté intact.

## F0-A.7 — le protocole d'hygiène était en cause, et je m'étais trompé

`tests/f0-hygiene-neutral.py` sépare les instants : copie des octets dans un
temporaire neutre, **scan avant ouverture**, ouverture, sauvegarde non
compressée, scan après — et le tout est refait sur un **témoin**, un blend
minimal créé dans le même environnement.

| | publié | avant ouverture | après sauvegarde |
| --- | ---: | ---: | ---: |
| `FACE_BASE_LOCKED.blend` | **0** | **0** | 1 |
| **témoin** (cube neuf) | 0 | **0** | **1** |

**Le témoin se comporte exactement comme le sujet.** La chaîne `/Users/…`
n'existe pas avant ouverture et apparaît à la sauvegarde, sur n'importe quel
fichier : c'est Blender qui inscrit le chemin de sa propre sauvegarde. Le
protocole historique la mesurait après l'avoir lui-même écrite.

> **Correction d'une affirmation que j'avais publiée en passe 4.** J'avais
> écrit que le fichier contenait une chaîne `/Users/orphicagency` « intrinsèque
> au format ». C'est faux tel que je l'avais établi : la mesure portait sur ma
> propre réécriture. Le FAIL historique `blend.aucun_chemin_personnel` est
> **un artefact de test**, et il est désormais classé comme tel dans le
> baseline.

**Réserve honnête, et elle est réelle.** Le fichier publié est compressé (zstd).
Un scan d'octets ne peut donc rien y lire en clair, et « 0 avant ouverture » ne
prouve pas l'absence — seulement l'illisibilité. Le décompresser sans le
réécrire demanderait `zstandard`, absent de cette machine. Ce que le témoin
établit est plus modeste et suffisant pour l'audit : **la chaîne observée
provenait du protocole**, pas d'une fuite propre à ce fichier. Le test
`f0-hygiene-blend.py` historique est conservé pour la provenance ; c'est le
protocole neutre qui fait foi.

## Gate F0-A

| condition | état |
| --- | --- |
| verrou positif passe | **oui**, code 0 |
| neuf mutations refusées | **oui**, 9/9, maître au même SHA |
| préflight de l'asset passe | **oui**, taille et SHA exacts |
| registres bruts reproduisent 21/3/2, 13/2, 10/1 | **oui**, au chiffre près |
| runner baseline compare les identifiants exacts | **oui**, contre-épreuve incluse |
| les codes shell ne cachent plus les FAIL | **oui**, 0 → 2 |
| protocole d'hygiène neutre publié | **oui**, avec témoin |
| SHA du maître inchangé | **oui**, `cc9e55a4…831f2bd8` |

**F0-A est terminée.** F0-B n'est pas commencée.
