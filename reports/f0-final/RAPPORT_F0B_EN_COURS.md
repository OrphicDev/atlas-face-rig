# F0-B — avancement (B.0 à B.11)

**F0-B n'est pas terminée.** Les jours de contact ont été divisés par cinq à dix
depuis `c0885ae`, la voie dense est enfin **mesurée** (plus aucun SKIP), mais les
trois seuils de fermeture ne passent pas encore.

## Progression des jours, à t = 1

| pose | `c0885ae` | ici, cage | ici, **dense** | seuil |
| --- | ---: | ---: | ---: | ---: |
| `blink_L` | 2,3937 mm | **0.4387 mm** | **0.2261 mm** | 0.20 |
| `blink_R` | 4,0046 mm | **0.4095 mm** | **0.2136 mm** | 0.20 |
| `mouth_close` | 0,9688 mm | **0.4767 mm** | **0.8463 mm** | 0.30 |

Le retour au neutre est **exact** (`0,0 mm`) et le jour est **monotone** sur
les onze valeurs, pour les trois poses.

## Ce qui a été construit et vérifié

| étape | livrable | vérification |
| --- | --- | --- |
| B.0 | `reports/f0-final/author-input.json` | 10/10 ; un SHA falsifié sort en 2 |
| B.2 | `reports/f0-final/contact-candidates.json` | 40/40/76, topologie intacte |
| B.3–B.6 | `config/landmarks-contact.json`, `correspondances-marges.json` | anneaux complets, L et R identiques |
| B.6 bis | `reports/f0-final/carte-miroir.json` | 9/9 ; bijective, involutive, 0 arête et 0 face orpheline ; deux valeurs inversées sortent en 2 |
| B.7 | `config/globe-fit.json` | résidu **0,2226 mm** contre 0,6934 sur la sphère complète ; rayon **12,024 mm** |
| B.9 | `config/contact-falloff.json` | distance **géodésique**, plus de cellules de Voronoï |
| B.10 | trois `*.cage-delta.json` | aller-retour **0,0000298 mm** ; maître à 0 shape key, SHA inchangé |
| B.11 | `reports/f0-final/contacts-v3.json` | onze valeurs, cage **et** dense |

## Trois sondes fausses, prises avant tout verdict

1. **le parcours d'anneau rendait 10 sommets sur 40 en silence** — il marchait
   sur l'ensemble peau + muqueuse, qui est une échelle et non un anneau. Il
   refuse désormais explicitement un parcours partiel ;
2. **le graphe était induit par les arêtes** : restreint au côté peau il donnait
   des degrés 1 et **0**. Comme en F0, le bord se tient **par les faces** ;
3. **la sphère du globe était ajustée sur toute la sclère**, renflement cornéen
   compris. Ajustée sur la seule portion postérieure, le résidu tombe de
   **0,6934 à 0,2226 mm** et le rayon passe à 12,024 mm — anatomiquement juste.

Et une faute de conception de mon prototype : les déplacements étaient **moyennés
sur les échantillons**, ce qui empêchait la convergence exacte. Chaque sommet de
marge vise maintenant son propre vis-à-vis au même paramètre d'arc, et les jours
sont passés de 0,77/0,69/0,78 à **0,44/0,41/0,48 mm**.

## Ce qui reste dû dans F0-B

Le résidu tient à la mesure sur des échantillons uniformes : après déformation,
deux arcs de cardinalités différentes (10 et 12) ne se reparamètrent pas
identiquement. Fermer exactement demande une itération, pas un réglage.
Restent aussi B.12 (arêtes hors bornes : 0,32–2,92, whitelist à justifier) et
B.13 (preuves à caméra fixe).
