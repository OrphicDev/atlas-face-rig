# Atlas — rig facial

Rig facial construit **par la mesure** : géométrie, shape keys et rig maître
d'un visage humain, sur l'asset CC0 de Blender Studio.

> ## F0 est faite. Le rig ne l'est pas.
>
> La géométrie est mesurée, décidée et **verrouillée**
> (`source/FACE_BASE_LOCKED.blend`). Il n'y a **aucun os, aucune shape key,
> aucun visème** — F0 ne devait pas en produire, et rien ne prétend le contraire.

## Par où commencer

**→ [`reports/f0/RAPPORT_F0.md`](reports/f0/RAPPORT_F0.md)** — ce qui est mesuré
et pourquoi les décisions sont celles-là.

**→ [`handoffs/HANDOFF_FACE_NEXT.md`](handoffs/HANDOFF_FACE_NEXT.md)** — pour
reprendre le travail à F1.

Le bootstrap d'origine reste dans
[`handoffs/BOOTSTRAP_CHAT_3_FACE.md`](handoffs/BOOTSTRAP_CHAT_3_FACE.md).

## Ce que F0 a établi

- **topologie exactement symétrique** — démontré, pas supposé : le miroir
  `.L`/`.R` se fait par indice de sommet ;
- **sept ouvertures anatomiques** et pas une de plus, dont une **vraie cavité
  orale** ;
- **cage de 3 242 sommets conservée** ; shape keys sur la cage, **multires gardé
  et jamais appliqué** ;
- **les dents étaient dans l'asset source** : `Jaw - Realistic`, 28 dents +
  mandibule, CC0. La langue reste à construire ;
- **19 sondes vérifiées sur 19** avant tout verdict — et trois d'entre elles
  étaient fausses, prises par leurs propres auto-tests.

## L'asset source

**Human Base Meshes bundle v1.4.1**, Blender Studio, **CC0** —
https://studio.blender.org/tools/assets/human-base-meshes

- SHA-256 : `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137`
- 49 420 489 octets · Blender **5.1.2**
- **non versionné ici** : désigne-le par `ATLAS_BASE_MESH`

Collection retenue : **`Head (Animation) - Realistic`** — 3 242 sommets,
**99,45 % de quads**, UV présente, iris et sclère séparés.

Mesuré, et à savoir avant de commencer : **aucune dent, aucune langue, aucun
cil, aucun sourcil, aucun matériau, aucune armature, aucune shape key.**

## Périmètre V1

Personnage caucasien masculin actuel uniquement. **Exclus** : matière, texture,
cheveux, barbe, pilosité.

## Reproduire l'inspection

```bash
export ATLAS_BASE_MESH=/chemin/vers/human_base_meshes_bundle.blend
blender --background --factory-startup --python-exit-code 1 \
  --python tests/f0-audit-topologie.py -- ./f0.json
blender --background --factory-startup --python-exit-code 1 \
  --python tests/verrou-topologie.py -- source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json
```

Le premier refuse de publier un chiffre si une seule de ses 15 sondes échoue ; le
second échoue si la topologie ou la pose neutre a bougé.

Références : [`reports/f0/`](reports/f0/) et
[`audit/inspection-asset-tetes.json`](audit/inspection-asset-tetes.json).

## Dépôt frère

Les mains : https://github.com/OrphicDev/atlas-hand-rig — **non validées**, et
leur handoff explique pourquoi. La leçon principale y est consignée : un rig
déclaré bon sur une sonde aveugle à 78 % de ses défauts.


> **État F0 (2026-08-16, commit `f6f1c86`).** F0 est **incomplète** : 200 sondes, 193 réussies, 3 échec(s), 4 sautée(s). Vérité unique : [`reports/f0-final/RAPPORT_F0_FINAL.md`](reports/f0-final/RAPPORT_F0_FINAL.md). F1 n'a pas commencé.
