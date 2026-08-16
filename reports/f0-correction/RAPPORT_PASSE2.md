# Passe 2 — banc multires anatomique et préflight câblé

Suite de [`RAPPORT_F0_CORRECTION.md`](RAPPORT_F0_CORRECTION.md). **Statut inchangé : `F0 INCOMPLET`.** Suite dans
[`RAPPORT_PASSE3.md`](RAPPORT_PASSE3.md) — sondes de mesure vérifiées et
verdicts anatomiques partiels.

Cette passe part de `1c54cb6`, descendant direct de `f852c453…`. Le §1 exigeait
`HEAD = f852c453…` ; l'état réel est publié ici plutôt que masqué, et le §19
autorise plusieurs commits pourvu que le dernier porte toutes les preuves.
Vérifié : `git merge-base --is-ancestor f852c453… HEAD` → oui, arbre propre,
manifeste sans échec.

---

## P0.4 — banc multires V2 · **CONSTRUIT ET EXÉCUTÉ, VERDICT NON PUBLIÉ**

[`tests/anatomie.py`](../../tests/anatomie.py) et
[`tests/f0-multires-v2.py`](../../tests/f0-multires-v2.py). Les bourrelets
cosinus ont disparu. À leur place, trois déformations réellement anatomiques :

- **clignement** — rotation des paupières **autour du globe**, rayon conservé ;
  75 % du trajet pour la supérieure, 25 % pour l'inférieure ; poids nul aux deux
  canthus, donc canthi stables ; repoussée hors de la sphère après rotation ;
- **fermeture labiale** — lèvres ramenées vers une ligne de contact mesurée,
  commissures fixes, décroissance douce vers le philtrum et le menton ;
- **mandibule** — rotation autour de l'axe **temporo-mandibulaire mesuré**
  (ligne des deux conduits auditifs, z 0,740), jamais au menton, plus
  translation antéro-inférieure progressive, lèvre supérieure rattachée au
  crâne. Cinq ouvertures : **0°, 5°, 10°, 20°, 32°**.

Deux voies, partant de la même surface neutre évaluée :

| | voie A — cage | voie B — haute résolution |
| --- | ---: | ---: |
| points de contrôle | **3 242** | **12 950** |
| temps médian, 20 mesures après 5 échauffements | 0,0365 s | **0,0255 s** |
| `.blend` compressé, Basis + une shape key | **1 018 000 o** | 1 774 000 o |

### Aucun verdict anatomique n'est publié, et c'est voulu

Le script sort en **code 2** parce que **deux de ses sondes de mesure ne passent
pas leur épreuve sur le neutre**, dont la réponse est connue.

| sonde | configuration connue | attendu | obtenu | |
| --- | --- | ---: | ---: | :---: |
| ajustement de sphère | 24 points sur une sphère de 11,7 mm | 11,7000 mm | 11,7000 | **PASS** |
| centre de la sphère | idem | exact | exact | **PASS** |
| jour palpébral gauche | neutre, fente publiée en F0 | 18,38 mm | **19,3563** | **PASS** |
| jour palpébral droite | neutre, fente publiée en F0 | 16,34 mm | **19,3264** | **FAIL** |
| pénétration du globe | neutre | 0 | **199** | **FAIL** |
| fente labiale au neutre | neutre | valeur finie | **1,935 mm** | **PASS** |

### Ce que ces échecs disent vraiment

Trois de mes sondes de mesure étaient fausses, et chacune a été prise **avant**
tout verdict :

1. **le jour palpébral** rendait 22 à 28 mm : il prenait tous les sommets à
   moins de 5,5 mm du globe, donc toute la paupière et le pourtour de l'orbite,
   c'est-à-dire la hauteur de la région et non le jour entre les marges.
   Corrigé pour ne garder que la **marge** — la ligne qui effleure le globe ;
2. **la pénétration** comptait **304** sommets « dans le globe » au neutre :
   elle balayait toute la sphère, donc le **fond de l'orbite**, naturellement
   plus proche du centre que le rayon. Restreinte à la calotte antérieure : 267,
   puis **199** après ajustement de sphère. **Toujours non nulle** ;
3. **la comparaison d'UV** confrontait le SHA de la **cage** (12 948 loops) à
   celui du maillage **évalué** : deux tables de tailles différentes, l'égalité
   était impossible par construction. Séparée en deux comparaisons portant
   chacune sur un seul maillage.

La cause restante est nommée : la sphère ajustée sur la sclère — centre
`[1,494856 ; −0,125396 ; 0,766688]`, rayon **11,7449 mm**, résidu d'ajustement
**0,6934 mm** — n'est pas exactement le globe que la paupière recouvre. Le
résidu de 0,69 mm sur un rayon de 11,7 mm dit que la sclère **n'est pas une
sphère** : c'est une calotte avec un renflement cornéen. Tant que ce repère
n'est pas juste, ni « aucune pénétration » ni « jour ≤ 0,20 mm » ne veulent dire
quoi que ce soit — et je ne desserrerai pas un seuil pour les faire passer.

**Le §12 n'est donc pas déclenché.** Aucune retopologie n'est décidée : aucune
insuffisance de topologie n'est démontrée. Ce sont mes sondes qui ont failli,
pas la cage.

### Ce que le banc établit tout de même

- **retour au neutre exact** : `0,000000 mm` sur les deux voies, pour les trois
  prototypes ; et **0° de mandibule rend exactement le neutre** ;
- la voie A coûte **4× moins de points de contrôle** et un `.blend` **1,7× plus
  léger** ; la voie B est **1,4× plus rapide** à évaluer ;
- les **UV de la cage** sont intactes après pose de shape key, et les **UV
  évaluées** le sont après déformation, sur les deux voies.

→ [`multires-ab-v2.json`](multires-ab-v2.json)

---

## P1 — préflight câblé dans l'audit topologique · **RÉSOLU**

[`tests/f0-audit-topologie.py`](../../tests/f0-audit-topologie.py) appelle
désormais `exiger_asset()`. Contre-épreuve publique : lancé avec
`ATLAS_BASE_MESH=/etc/hosts`, il sort en **code 2** sans produire de rapport ;
avec le bon asset, `PREFLIGHT OK` puis `AUDIT_OK`.

---

## Ce qui reste dû pour lever `F0 INCOMPLET`

1. **corriger le repère du globe** — ajuster la sphère sur la seule portion
   sclérale, hors renflement cornéen, puis reprendre les seuils de pénétration
   et de jour ;
2. **trancher le raccord corps** entre remplacement complet et transfert de
   déformations, avec les preuves visuelles du §7.5 ;
3. **export glTF** aller-retour et empreintes UV d'export (P0.5) ;
4. **coupe sagittale**, **hygiène des chemins** du `.blend`, **vues
   bilatérales**, **wireframes** ;
5. **preuves visuelles** du banc et du raccord.
