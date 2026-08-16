"""F0-E.10 — reimport dans un Blender vide et comparaison chiffree."""
import argparse, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
a = argparse.ArgumentParser()
for f in ("--input", "--source", "--report"): a.add_argument(f, required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
# 1) reference : le blend runtime
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.source)))
src = bpy.data.objects["GEO_face_runtime"]
ref = {"sommets": len(src.data.vertices),
       "morphs": sorted(k.name for k in src.data.shape_keys.key_blocks if k.name != "Basis"),
       "basis": [ (src.matrix_world @ v.co).copy() for v in src.data.vertices],
       "morph_pos": {}}
for k in src.data.shape_keys.key_blocks:
    if k.name != "Basis":
        ref["morph_pos"][k.name] = [(src.matrix_world @ p.co).copy() for p in k.data]
# 2) import du GLB dans une scene vide
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(Rp(o.input)))
meshes = [x for x in bpy.data.objects if x.type == "MESH"]
arms = [x for x in bpy.data.objects if x.type == "ARMATURE"]
reg = Registre("gltf-roundtrip")
reg.exige("glb.un_mesh", "un mesh importe", "GLB", 1, len(meshes), len(meshes) == 1)
reg.exige("glb.une_armature", "une armature importee", "GLB", 1, len(arms), len(arms) == 1)
imp = meshes[0]
mo = sorted(k.name for k in imp.data.shape_keys.key_blocks
            if k.name != imp.data.shape_keys.key_blocks[0].name) if imp.data.shape_keys else []
reg.exige("glb.morphs", "les trois morph targets survivent", "GLB",
          len(ref["morphs"]), len(mo), len(mo) == len(ref["morphs"]))
reg.exige("glb.joints", "les os de deformation survivent", "GLB", ">= 2",
          len(arms[0].data.bones) if arms else 0, bool(arms) and len(arms[0].data.bones) >= 2)
# comparaison geometrique par plus proche point (le glTF peut reordonner)
from mathutils.bvhtree import BVHTree
import bmesh
bm = bmesh.new(); bm.from_mesh(imp.data); bm.transform(imp.matrix_world)
bvh = BVHTree.FromBMesh(bm); bm.free()
d = [((bvh.find_nearest(p, 0.05)[0] or p) - p).length * 1000 for p in ref["basis"]]
d.sort()
reg.exige("glb.neutre_p95", "surface neutre apres aller-retour", "plus proche point",
          "<= 0,10 mm", round(d[int(len(d) * .95)], 6), d[int(len(d) * .95)] <= 0.10,
          tolerance=0.10)
reg.exige("glb.neutre_max", "pire ecart du neutre", "plus proche point",
          "<= 0,50 mm", round(d[-1], 6), d[-1] <= 0.50, tolerance=0.50)
R = {"reference": {"sommets": ref["sommets"], "morphs": ref["morphs"]},
     "importe": {"sommets": len(imp.data.vertices), "morphs": mo,
                 "os": sorted(b.name for b in arms[0].data.bones) if arms else [],
                 "actions": sorted(x.name for x in bpy.data.actions)},
     "neutre_mm": {"p50": round(d[len(d) // 2], 6), "p95": round(d[int(len(d) * .95)], 6),
                   "max": round(d[-1], 6)},
     "registre": reg.bilan()}
p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ok = reg.conclure()
print("ROUNDTRIP", "OK" if ok else "ECHEC", "| importe", len(imp.data.vertices),
      "sommets,", len(mo), "morphs")
sys.exit(0 if ok else 2)
