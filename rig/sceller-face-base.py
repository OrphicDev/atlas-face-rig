"""P0.3 — scelle `source/FACE_BASE_LOCKED.blend` : purge, verrous d'axes, empreintes.

Ne reconstruit pas depuis le paquet : opere sur la base deja verrouillee, pour
que la pose neutre reste bit pour bit la meme. Le script le PROUVE, il ne le
suppose pas — il compare sommet a sommet avant et apres.

Ce qu'il fait :
  - retire tout ce qui n'est pas l'un des cinq meshes autorises ;
  - pose `lock_location`, `lock_rotation`, `lock_scale` sur les trois axes ;
  - refuse de sauvegarder s'il reste une shape key, une armature, un driver,
    une contrainte ou une animation ;
  - calcule les CINQ empreintes separees et les publie.

    blender --background --factory-startup --python-exit-code 1 \
      --python rig/sceller-face-base.py -- \
      source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json
"""
import hashlib, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests"))
import bpy
from atlas_commun import (Registre, config_objet, detail_uv, inventaire_scene,
                          toutes_les_empreintes)

MESHES_AUTORISES = {
    "GEO-head_animation_realistic",
    "GEO-head_animation_realistic.iris.L",
    "GEO-head_animation_realistic.iris.R",
    "GEO-head_animation_realistic.sclera.L",
    "GEO-head_animation_realistic.sclera.R",
}

blend, sortie = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))
reg = Registre("sceller-face-base")

avant = {o.name: [v.co.copy() for v in o.data.vertices]
         for o in bpy.data.objects if o.type == "MESH"}
avant_mw = {o.name: o.matrix_world.copy() for o in bpy.data.objects if o.type == "MESH"}
parents_avant = {o.name: (o.parent.name if o.parent else None)
                 for o in bpy.data.objects if o.type == "MESH"}

# ---- purge : la source doit etre une geometrie minimale ----
retires = []
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.name not in MESHES_AUTORISES:
        retires.append({"nom": o.name, "type": o.type})
        bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.armatures, bpy.data.cameras, bpy.data.lights, bpy.data.actions,
             bpy.data.materials, bpy.data.texts, bpy.data.images):
    for d in list(coll):
        if d.users == 0 or coll is not bpy.data.images:
            try: coll.remove(d)
            except Exception: pass
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

objets = [o for o in bpy.data.objects if o.type == "MESH"]

# ---- verrous d'axes : neuf drapeaux par objet ----
for o in objets:
    o.lock_location = (True, True, True)
    o.lock_rotation = (True, True, True)
    o.lock_rotation_w = True
    o.lock_scale = (True, True, True)

# ---- la purge n'a rien deplace : demontre, pas suppose ----
ecart = 0.0
for o in objets:
    for a, v in zip(avant[o.name], o.data.vertices):
        ecart = max(ecart, (a - v.co).length)
    ecart = max(ecart, max(abs(a - b) for la, lb in zip(avant_mw[o.name], o.matrix_world)
                           for a, b in zip(la, lb)))
reg.exige("scellement.neutre_intact", "la purge et les verrous ne deplacent rien",
          "meme fichier rouvert, purge + verrous", "0.0 mm", "%.9f mm" % (ecart * 1000),
          ecart == 0.0)

# ---- la source finale est-elle vierge ? ----
noms = sorted(o.name for o in objets)
reg.exige("scellement.cinq_meshes", "exactement les cinq meshes autorises",
          "base rouverte apres purge", sorted(MESHES_AUTORISES), noms,
          noms == sorted(MESHES_AUTORISES))
reg.exige("scellement.zero_shape_key", "aucune shape key sur la source",
          "base rouverte apres purge", 0,
          sum(len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0 for o in objets),
          all(not o.data.shape_keys for o in objets))
reg.exige("scellement.zero_armature", "aucune armature, objet ou modificateur",
          "base rouverte apres purge", 0,
          len(bpy.data.armatures) + sum(1 for o in objets for m in o.modifiers
                                        if m.type == "ARMATURE"),
          not bpy.data.armatures and not any(m.type == "ARMATURE"
                                             for o in objets for m in o.modifiers))
reg.exige("scellement.zero_driver", "aucun driver, aucune animation",
          "base rouverte apres purge", 0,
          sum(len(o.animation_data.drivers) if o.animation_data else 0 for o in objets),
          not any(o.animation_data for o in objets))
reg.exige("scellement.zero_contrainte", "aucune contrainte",
          "base rouverte apres purge", 0,
          sum(len(o.constraints) for o in objets), not any(o.constraints for o in objets))
reg.exige("scellement.verrous_axes", "neuf drapeaux verrouilles par objet",
          "lock_location/rotation/scale poses sur les 3 axes", 9 * len(objets),
          sum(sum(o.lock_location) + sum(o.lock_rotation) + sum(o.lock_scale)
              for o in objets),
          all(all(o.lock_location) and all(o.lock_rotation) and all(o.lock_scale)
              for o in objets))
reg.exige("scellement.uv_presente", "UVMap sur les cinq objets",
          "base rouverte apres purge", 5,
          sum(1 for o in objets if "UVMap" in [c.name for c in o.data.uv_layers]),
          all("UVMap" in [c.name for c in o.data.uv_layers] for o in objets))
mult = [m for o in objets for m in o.modifiers if m.type == "MULTIRES"]
reg.exige("scellement.multires_non_applique", "un multires, sur la tete seule",
          "base rouverte apres purge", 1, len(mult), len(mult) == 1)
reg.exige("scellement.echelle_unite", "echelle 1 et rotation nulle sur les cinq objets",
          "base rouverte apres purge", "{(1.0, 1.0, 1.0)}",
          "%s" % sorted({tuple(round(x, 6) for x in o.scale) for o in objets}),
          all(all(abs(x - 1.0) < 1e-6 for x in o.scale)
              and all(abs(x) < 1e-6 for x in o.rotation_euler) for o in objets))
reg.exige("scellement.parentage_conserve", "le parentage des yeux survit a la purge",
          "yeux parentes a la tete dans la base d'origine",
          sorted(parents_avant.items()),
          sorted((o.name, o.parent.name if o.parent else None) for o in objets),
          sorted(parents_avant.items())
          == sorted((o.name, o.parent.name if o.parent else None) for o in objets))

if not reg.conclure():
    json.dump({"status": "ECHEC", **reg.bilan()}, open(sortie, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("SCELLEMENT REFUSE : la source n'est pas vierge, rien n'est sauvegarde.")
    sys.exit(2)

bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend), compress=True)

emp = toutes_les_empreintes(bpy, objets)
rapport = {
    "fichier": os.path.basename(blend),
    "blender": bpy.app.version_string,
    **emp,
    "objets": sorted((config_objet(o) for o in objets), key=lambda d: d["objet"]),
    "uv": detail_uv(objets),
    "inventaire_scene": inventaire_scene(bpy),
    "objets_retires_au_scellement": retires,
    "totaux": {"objets": len(objets),
               "sommets": sum(len(o.data.vertices) for o in objets),
               "faces": sum(len(o.data.polygons) for o in objets),
               "loops": sum(len(o.data.loops) for o in objets)},
    "registre_du_scellement": reg.bilan(),
}
with open(blend, "rb") as f:
    rapport["octets"] = os.path.getsize(blend)
    rapport["sha256_du_blend"] = hashlib.sha256(f.read()).hexdigest()
json.dump(rapport, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("SCELLE_OK", rapport["totaux"], "| retires:", [r["nom"] for r in retires] or "aucun")
for k, v in emp.items(): print("  %-28s %s" % (k, v[:32]))
