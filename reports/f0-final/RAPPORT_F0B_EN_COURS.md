# F0-B — état d'avancement

**F0-B n'est pas terminée.** Ce rapport dit exactement où elle en est.

## Fait et vérifié

| étape | état |
| --- | --- |
| **F0-B.0** — auteur signé | **fait**, 10/10 sondes ; un caractère changé dans un SHA fait sortir en 2 |
| **F0-B.1** — copie de travail | **fait**, maître au même SHA `cc9e55a4…` |
| **F0-B.2** — groupes candidats | **fait**, 40/40/76 sommets, topologie intacte |
| **F0-B.3/B.4** — marges topologiques | **fait**, anneaux complets |
| **F0-B.5** — terminaux | **fait** |
| **F0-B.6** — appariement par longueur d'arc | **fait**, 64 échantillons minimum |

Anneaux reconstruits, côté peau :

| ouverture | upper | lower | écart max au neutre |
| --- | ---: | ---: | ---: |
| `fente_palpebrale.L` | 10 | 12 | 10,359 mm |
| `fente_palpebrale.R` | 10 | 12 | 9,976 mm |
| `fente_labiale` | 21 | 19 | 3,911 mm |

Les deux yeux donnent **exactement les mêmes cardinalités** — cohérent avec la
symétrie topologique démontrée en F0.

Les quatre terminaux sont `anchor_shared` avec `meme_sommet: true` : le bord
côté peau est un anneau **fermé**, donc les canthi et les commissures sont des
sommets réellement partagés, pas deux points distincts à rapprocher.

## Deux sondes fausses, prises avant tout verdict

**Le parcours d'anneau rendait un chemin partiel en silence.** Première version :
10 sommets sur 40, sans le dire. Elle marchait sur l'ensemble audité complet —
peau **et** muqueuse — qui n'est pas un anneau mais une échelle. Elle refuse
désormais explicitement (`cycle partiel : 11 sur 20`).

**Le graphe était induit par les arêtes.** Restreint au côté peau, il donnait
des degrés 1 et même **0** : les sommets consécutifs d'une marge n'ont pas
forcément d'arête commune. C'est la même leçon qu'en F0 — le bord se tient
**par les faces**. Reconstruit par face partagée, l'anneau est complet.

## Écart au cahier, assumé et nommé

Le §F0-B.3 demande de **cliquer chaque sommet dans Blender** et interdit
`min(X)`/`max(X)` comme substitut. Je tourne **sans interface** : le clic n'est
pas disponible. La saisie est remplacée par une dérivation **sur l'anneau
lui-même** — ses deux extrémités le coupent en un arc supérieur et un arc
inférieur. Ce n'est pas un seuil sur une coordonnée du maillage, c'est une
propriété du cycle ; et la complétude de l'anneau est exigée, pas supposée.

C'est un écart réel au protocole, pas une équivalence que je déclare : un
opérateur devant Blender doit contrôler les quatre landmarks publiés dans
`config/landmarks-contact.json` avant que F0-B soit déclarée close.

## Reste à faire dans F0-B

F0-B.6 bis (carte miroir signée), B.7 (cible de contact des paupières et
`config/globe-fit.json`), B.8 (cible labiale), B.9 (falloff géodésique),
B.10 (deltas de prototype), B.11 (mesure sur onze valeurs, cage et Multires),
B.12 (déformations extrêmes), B.13 (preuves à caméra fixe).
