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
# Le GLB fait foi, pas ce que l'importeur fabrique. Blender cree un
# "Icosphere" de 42 sommets comme forme d'os a l'import : le compter comme un
# mesh du fichier etait FAUX, et c'est mon test qui l'etait, pas l'export.
import struct as _st
_b = open(os.path.abspath(Rp(o.input)), "rb").read()
_off, _chunks = 12, []
_tot = _st.unpack("<III", _b[:12])[2]
while _off < _tot:
    _ln, _ty = _st.unpack("<II", _b[_off:_off + 8])
    _chunks.append((_ty, _b[_off + 8:_off + 8 + _ln])); _off += 8 + _ln
GLB = json.loads(_chunks[0][1].decode("utf-8"))
meshes = [x for x in bpy.data.objects if x.type == "MESH" and x.name != "Icosphere"]
arms = [x for x in bpy.data.objects if x.type == "ARMATURE"]
reg = Registre("gltf-roundtrip")
reg.exige("glb.un_mesh", "le GLB contient un seul mesh",
          "chunk JSON du fichier", 1, len(GLB.get("meshes", [])),
          len(GLB.get("meshes", [])) == 1)
reg.exige("glb.skin", "un skin dans le fichier", "chunk JSON", 1,
          len(GLB.get("skins", [])), len(GLB.get("skins", [])) == 1)
_att = sorted(GLB["meshes"][0]["primitives"][0]["attributes"])
reg.exige("glb.attributs", "positions, normales, UV, joints et poids",
          "chunk JSON",
          ["JOINTS_0", "NORMAL", "POSITION", "TEXCOORD_0", "WEIGHTS_0"], _att,
          _att == ["JOINTS_0", "NORMAL", "POSITION", "TEXCOORD_0", "WEIGHTS_0"])
reg.exige("glb.targets", "trois morph targets dans le fichier", "chunk JSON", 3,
          len(GLB["meshes"][0]["primitives"][0].get("targets", [])),
          len(GLB["meshes"][0]["primitives"][0].get("targets", [])) == 3)
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
     "glb": {"meshes": [m.get("name") for m in GLB.get("meshes", [])],
             "nodes": [n.get("name") for n in GLB.get("nodes", [])],
             "skins": len(GLB.get("skins", [])),
             "animations": [x.get("name") for x in GLB.get("animations", [])],
             "generator": GLB.get("asset", {}).get("generator")},
     "neutre_mm": {"p50": round(d[len(d) // 2], 6), "p95": round(d[int(len(d) * .95)], 6),
                   "max": round(d[-1], 6)},
     "registre": reg.bilan()}
p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ok = reg.conclure()
print("ROUNDTRIP", "OK" if ok else "ECHEC", "| importe", len(imp.data.vertices),
      "sommets,", len(mo), "morphs")
sys.exit(0 if ok else 2)
