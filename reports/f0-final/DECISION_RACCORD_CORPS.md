# Décision de raccord tête–corps

```
STRATÉGIE RETENUE : TRANSFERT DE DÉFORMATIONS
```

## Ce que la mesure interdit

| voie | verdict | mesure qui tranche |
| --- | --- | --- |
| **greffe par couture fermée** | **exclue** | la tête a **0 bord ouvert** — il n'existe aucune boucle de couture à souder — et les nombres de sommets diffèrent, donc la correspondance ne peut pas être bijective. Le cahier interdit alors de forcer une soudure. |
| **remplacement complet** | **non retenu** | il exige de couper le corps et de prouver qu'il ne reste ni trou, ni double surface, ni intersection. Aucun de ces trois points n'est démontré ici. |
| **transfert de déformations** | **retenu** | il ne demande aucune compatibilité géométrique, garde le corps *watertight* et ses UV, et laisse la cage faciale comme auteur. |

## Pourquoi la compatibilité directe est hors d'atteinte

[`head-body-fit.json`](head-body-fit.json), similarité résolue sur quatre
repères anatomiques, **10 sondes sur 10** :

| mesure | valeur | seuil |
| --- | ---: | ---: |
| échelle uniforme | 1,033446 | — |
| écart à 1 | **3,34463 %** | ≤ 1,0 % |
| résidu maximum | **4,0694 mm** | ≤ 2,0 mm |
| échelle non uniforme | **0,0** (exacte) | refusée |

Cause nommée : le paquet contient **deux sculpts de tête distincts**. La tête du
corps porte 3 612 sommets au-dessus du cou, la tête d'animation 3 242. Un écart
de 3,3 % avec 2 à 4 mm de résidu est exactement ce qu'on attend entre deux
sculpts voisins et non identiques.

## Ce que le transfert établit

[`body-transfer.json`](body-transfer.json), **5 sondes sur 5** :

| contrôle | résultat |
| --- | ---: |
| sommets cartographiés | **2 833** |
| rejets de correspondance | **0** |
| barycentriques normalisés, somme à 1 | 1e−12 |
| écart brut des trois aires, avant normalisation | 0,000815 — le point est bien **dans** le triangle |
| masque nul avant l'anneau de cou | **0,0** |
| tronc | **0,0** |
| **neutre du corps** | **strictement inchangé** |

Le transfert porte un **delta**, jamais une position absolue : c'est ce qui
garantit que la pose `neutral` laisse le corps identique à lui-même.

## Réserve, et elle est réelle

Le §D.7 demande une `erreur_delta` sous 0,25 mm de médiane, 0,75 de p95 et 2 de
maximum. **Telle que je l'ai implémentée, cette erreur vaut zéro par
construction** : je compare le delta candidat au delta de référence multiplié
par le même masque. C'est une tautologie, pas une mesure.

La mesurer vraiment demande une **seconde méthode indépendante** — la
contre-épreuve `Surface Deform` du §D.8 — et de comparer les deux surfaces
obtenues. Cette contre-épreuve n'est pas faite. **La décision de stratégie est
donc prise sur la mesure de similarité et sur les propriétés démontrées du
transfert, pas sur un seuil d'erreur que je n'ai pas encore mesuré.**
