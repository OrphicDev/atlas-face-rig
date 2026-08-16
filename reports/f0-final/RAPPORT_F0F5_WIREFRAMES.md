# F0-F.5 — les wireframes bilatéraux

**17 images**, toutes en 1000 × 1000, rendues sur des duplicatas temporaires. Les
poses viennent des **deltas publiés** — la fondation ne porte aucune shape key
— et les cinq angles de mâchoire du prototype F0-C.

## Les paires L/R

Le tutoriel demande « même matrice de caméra » pour une paire bilatérale. Prise
au pied de la lettre, elle ferait rendre la zone gauche deux fois. Les deux
caméras d'une paire sont donc **exactement images l'une de l'autre par le plan
sagittal du contrat** (x = 1.462572), et c'est cela qui est vérifié :

| paire | écart à l'image miroir | échelle |
| --- | ---: | ---: |
| paupières neutres | 0,018 mm | identique |
| paupières fermées | 0,018 mm | identique |
| narines | 0,249 mm | identique |

## Les poses bougent-elles vraiment ?

Une image ne prouve pas une pose. Chaque vue « fermée » est comparée à sa
neutre **sommet par sommet** :

| pose | déplacement maximal |
| --- | ---: |
| paupière L fermée | **8,50 mm** |
| paupière R fermée | **8,43 mm** |
| lèvres fermées | **1,82 mm** |

## Les images

| vue | part de fil | épaisseur | delta |
| --- | ---: | ---: | --- |
| paupiere_L_neutre | 13.98 % | 0.227 mm | — |
| paupiere_L_fermee | 13.96 % | 0.227 mm | blink_L |
| paupiere_R_neutre | 14.01 % | 0.227 mm | — |
| paupiere_R_fermee | 13.96 % | 0.227 mm | blink_R |
| levres_neutre | 17.48 % | 0.257 mm | — |
| levres_fermee | 15.72 % | 0.258 mm | mouth_close |
| narine_L | 10.35 % | 0.167 mm | — |
| narine_R | 10.24 % | 0.167 mm | — |
| philtrum_levre_inferieure | 10.53 % | 0.151 mm | — |
| cou_et_raccord | 7.64 % | 0.394 mm | — |
| cage_seule | 16.62 % | 0.539 mm | — |
| surface_multires | 18.38 % | 0.273 mm | — |
| jaw_00 | 18.03 % | 0.659 mm | — |
| jaw_05 | 10.94 % | 0.660 mm | — |
| jaw_10 | 9.78 % | 0.660 mm | — |
| jaw_20 | 10.47 % | 0.660 mm | — |
| jaw_32 | 11.18 % | 0.660 mm | — |

**27 sondes sur 27.**

## Quatre fautes corrigées, toutes miennes

- Les douze premières vues montraient **l'occiput**. Visée posée à (0, −1, 0),
  la caméra se retrouvait à y = +0,354 — derrière le crâne — et l'on croyait
  lire des lèvres dans un quadrillage lisse. La face regarde vers −Y :
  l'observateur doit être devant et viser +Y.
- La sonde de fil comptait aussi la surface : (0,09) devient 0,33 à l'écran et
  passait le seuil `r > 0,30`. Les douze vues publiaient « 1 000 000 px de
  fil » sur un million de pixels — **une sonde qui ne pouvait pas échouer**.
  Le fil est maintenant classé par distance à sa couleur attendue, et une
  **fourchette** est exigée : un aplat jaune échoue autant qu'une image vide.
- Les vues « neutre » et « fermée » sortaient au pixel près identiques : après
  l'échange de données du maillage, les dépendances n'étaient pas rafraîchies
  et le duplicata évalué rendait encore l'ancienne géométrie.
- `rendre()` nettoyait tout objet commençant par `DBG_` — or les poses de
  mâchoire s'appellent `DBG_jaw_*`. Une seule des cinq était rendue.

L'épaisseur du fil suit le cadre **et** l'espacement des arêtes : à 0,18 mm
fixes elle tombait à 0,9 % sur les vues larges, et la cage — quatre fois plus
clairsemée — restait à 1,37 % quand la surface dense était à 4,25 %.
