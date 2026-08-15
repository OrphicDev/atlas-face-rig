# Atlas — rig facial

Rig facial construit **par la mesure** : géométrie, shape keys et rig maître
d'un visage humain, sur l'asset CC0 de Blender Studio.

> ## Rien n'est encore fait
>
> Ce dépôt est un **bootstrap**. Il ne contient pas de rig, pas de shape key,
> pas de rendu. Il contient la **mesure de l'asset source** et les conventions
> à respecter, pour que le travail commence sur des chiffres et non sur des
> suppositions.

## Par où commencer

**→ [`handoffs/BOOTSTRAP_CHAT_3_FACE.md`](handoffs/BOOTSTRAP_CHAT_3_FACE.md)**

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
  --python tests/inspecter-asset-tetes.py -- ./tetes.json
```

Référence : [`audit/inspection-asset-tetes.json`](audit/inspection-asset-tetes.json).

## Dépôt frère

Les mains : https://github.com/OrphicDev/atlas-hand-rig — **non validées**, et
leur handoff explique pourquoi. La leçon principale y est consignée : un rig
déclaré bon sur une sonde aveugle à 78 % de ses défauts.
