# F0-F.4 — la coupe sagittale

Tout se passe sur des **duplicatas de rendu**. Le fichier de production n'est
jamais bisecté et n'est pas réenregistré.

## Deux plans, et pourquoi

| plan | x monde | faces de section |
| --- | ---: | ---: |
| médian (contrat de miroir, décalé de 1,0 mm) | 1.463572 | 448 |
| parasagittal, centre du globe gauche | 1.494852 | 628 |

Le plan du contrat est à x = 1.462572. La coupe médiane est décalée de **1,0 mm** :
couper exactement sur le plan de symétrie longe la couture de sommets médians,
où la section est dégénérée — elle n'a pas de largeur. Ce n'est pas un défaut
de rendu, c'est la géométrie du maillage.

Le plan parasagittal existe parce qu'**au milieu d'un visage il n'y a pas
d'œil** : exiger que « les globes se distinguent de la peau » sur une coupe
médiane serait une exigence invérifiable. Chaque image porte le plan dont elle
vient.

## Ce que chaque image contient — mesuré, pas décrit

Chaque pixel est classé par sa **distance à la couleur attendue en sRGB**,
calculée depuis la charte. Des inégalités écrites à la main publiaient
« rouge : 0 » sur une image où le globe est manifestement rouge : à l'écran le
rouge (0,90 ; 0,08 ; 0,08) devient (0,955 ; 0,313 ; 0,313), et la condition
`g < 0,20` le rejetait. Et un pixel sur 25 sous-comptait les liserés fins — ils
sont maintenant tous comptés.

| image | section | muqueuse | globe | peau |
| --- | ---: | ---: | ---: | ---: |
| `median_bouche` | 19 | 8 | 0 | 375044 |
| `median_orbite` | 322 | 0 | 14878 | 88794 |
| `median_cavite_orale` | 0 | 4 | 0 | 348087 |
| `median_cou` | 0 | 0 | 0 | 563195 |
| `parasagittal_oeil_L_bouche` | 5559 | 76 | 0 | 687779 |
| `parasagittal_oeil_L_orbite` | 992 | 0 | 14811 | 286681 |
| `parasagittal_oeil_L_cavite_orale` | 4640 | 40 | 0 | 612229 |
| `parasagittal_oeil_L_cou` | 486 | 0 | 0 | 598111 |

## Trois aides de lecture, dites plutôt que cachées

- section epaissie de 0,4 mm vers la camera
- double du demi-crane aux normales inversees, sans la section : EEVEE n'emet pas sur la face arriere
- plan median decale de 1,0 mm : sur la couture de symetrie la section est degeneree

## Ce qui ne passe pas

**11 sondes sur 14.** Les trois échecs sont dans la série médiane :
`median_cavite_orale` et `median_cou` ne montrent aucun pixel de section, et
`median_bouche` en montre 19 pour 20 exigés.

Ce n'est pas un manque de géométrie : le plan médian porte **448 faces de
section** contre 628 pour le parasagittal, et les deux séries partagent
exactement les mêmes cadrages et les mêmes caméras. **Je n'ai pas identifié la
cause**, et je ne la devine pas ici. La série parasagittale, elle, satisfait
l'exigence sans réserve : section de 486 à 5 559 pixels, globes à 14 811,
peau de 286 000 à 688 000.

Le seuil n'a pas été touché.
