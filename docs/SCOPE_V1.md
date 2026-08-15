# Périmètre de la V1 — rig facial

## Inclus

- **géométrie faciale** : correction ou retopologie locale si la mesure la
  justifie, sur `Head (Animation) - Realistic` ;
- **shape keys** d'expression ;
- **rig facial maître** : contrôleurs, mécanismes, os de déformation, selon les
  conventions héritées des mains (`CTRL_` / `MCH_` / `DEF_` / `WGT_`, suffixes
  `.L` / `.R`) ;
- **dents et langue** : absentes de l'asset, donc à créer — c'est dans le
  périmètre parce qu'une bouche ne peut pas s'ouvrir sans elles.

## Exclus, explicitement

- matière, shader, texture ;
- cheveux, barbe, pilosité, cils et sourcils en tant que géométrie de rendu ;
- autres morphologies : la V1 ne couvre que le **personnage caucasien masculin
  actuel**.

## Ce qui décide qu'une V1 est finie

Les mêmes règles que pour les mains, apprises à leurs dépens :

1. **toute commande à 0 redonne le neutre à moins de 0,01 mm** — sans quoi le
   montage fabrique une double transformation ;
2. **aucune auto-intersection** dans une pose ni dans une transition — les
   transitions comptent autant que les poses finales, et c'est là que les mains
   cachaient leurs défauts ;
3. **chaque sonde est vérifiée sur une configuration connue** avant qu'on lise
   son verdict ;
4. **un critère faux fait échouer le pipeline** : pas de `.blend` livré, un
   rapport d'échec écrit, un code de sortie non nul.
