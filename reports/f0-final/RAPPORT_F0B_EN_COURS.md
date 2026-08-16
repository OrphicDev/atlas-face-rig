# F0-B — avancement (B.0 à B.12)

**12 sondes sur 18.** `mouth_close` passe **tout** sauf les arêtes. Le clignement
passe la voie dense et, à droite, la cage.

| pose | départ `c0885ae` | cage | dense | seuil | séparation | arêtes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `blink_L` | 2,3937 | 0.2152 | 0.1804 | 0.20 | -0.0614 | 0.35–2.43 |
| `blink_R` | 4,0046 | 0.1876 | 0.1860 | 0.20 | -0.0711 | 0.39–2.49 |
| `mouth_close` | 0,9688 | 0.0920 | 0.0963 | 0.30 | -0.0036 | 0.45–1.52 |

Retour au neutre **exact** et jour **monotone** sur les onze valeurs.

## Ce que le réglage a appris, mesure par mesure

| configuration | jour blink_L | verdict |
| --- | ---: | --- |
| 12 itérations, amortissement 0,7 | 0,2752 mm | plafonne |
| 400 itérations, amortissement 0,5 | **0,2152 mm** | converge |
| 2 000 itérations | **2,71 mm** | **diverge** — 50 à 72 mm de course, arêtes à 70× |
| garde de contact portée à 0,10 mm | 0,4195 mm | **remonte** — la garde doit rester petite devant la fente |

La divergence à 2 000 itérations a montré que **rien ne bornait la course**. Une
borne a été ajoutée : aucun sommet ne peut se déplacer de plus que la demi-
étendue de son ouverture.

## Deux hypothèses posées et réfutées

1. **« le résidu vient de la discrétisation en 64 échantillons »** — faux :
   mesuré aux sommets, le jour vaut 0,3298 mm contre 0,2752 aux échantillons,
   donc *plus grand* ;
2. **« le résidu vient de l'écart de flèche des deux polylignes contre le
   globe »** — faux aussi : faire viser aux deux marges un même point de contact
   déjà écarté du globe n'a rien changé (0,2752 → 0,2768).

La cause réelle est la **convergence** : chaque sommet sert environ six
échantillons aux exigences contradictoires, et le système sur-déterminé demande
des centaines d'itérations sous-relaxées.

## Ce qui bloque encore

`blink_L` à **0,2152 mm** au lieu de 0,20 sur la cage ; séparation signée à
**−0,061** et **−0,071** au lieu de −0,05 ; arêtes minimales à **0,355** et
**0,391** au lieu de 0,50 — toutes sur la marge, donc relevant de la whitelist
B.12, mais elles n'y sont pas encore inscrites avec leur justification finale.

Restent B.13 (preuves à caméra fixe) et la décision du §12.
