"""F0-E.6 — mesh runtime dense : le Multires est MATERIALISE, pas exporte."""
import argparse, hashlib, json, math, os, struct, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
TETE = "GEO-head_animation_realistic"
MORPHS = ("TMP_blink.L", "TMP_blink.R", "TMP_mouthClose")

def evalue(ob):
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(ob.evaluated_get(dg),
                                           preserve_all_data_layers=True, depsgraph=dg)

a = argparse.ArgumentParser()
for f in ("--input", "--level", "--output", "--report"): a.add_argument(f, required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
tete = bpy.data.objects[TETE]; rig = bpy.data.objects["TMP_F0_JAW_RIG"]
reg = Registre("build-runtime-mesh")
for k in tete.data.shape_keys.key_blocks:
    if k.name != "Basis": k.value = 0.0
pb = rig.pose.bones["TMP_jaw"]; pb.rotation_mode = "XYZ"
pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
for m in tete.modifiers:
    if m.type == "MULTIRES":
        m.levels = int(o.level); m.render_levels = int(o.level)
# desactiver l'armature : le runtime porte la surface NEUTRE, l'os viendra apres
am = next(m for m in tete.modifiers if m.type == "ARMATURE"); am.show_viewport = False
me_neutre = evalue(tete)
run = bpy.data.objects.new("GEO_face_runtime", me_neutre)
run.matrix_world = tete.matrix_world.copy()
bpy.context.scene.collection.objects.link(run)
for m in list(run.modifiers): run.modifiers.remove(m)
n_dense = len(me_neutre.vertices)
run.shape_key_add(name="Basis", from_mix=False)
base = [v.co.copy() for v in me_neutre.vertices]
sha_uv = lambda me: hashlib.sha256(b"".join(
    struct.pack("<2f", d.uv[0], d.uv[1]) for d in me.uv_layers.active.data)).hexdigest()
uv0 = sha_uv(me_neutre)
R = {"niveau_multires": int(o.level), "sommets_dense": n_dense,
     "faces_dense": len(me_neutre.polygons), "loops_dense": len(me_neutre.loops),
     "uv_sha_neutre": uv0, "morphs": {}}
for nom in MORPHS:
    for k in tete.data.shape_keys.key_blocks:
        if k.name != "Basis": k.value = 0.0
    tete.data.shape_keys.key_blocks[nom].value = 1.0
    me_p = evalue(tete)
    ok = len(me_p.vertices) == n_dense
    reg.exige("runtime.topologie_%s" % nom, "meme topologie dense que le neutre",
              "morph a 1", n_dense, len(me_p.vertices), ok)
    if ok:
        kb = run.shape_key_add(name=nom, from_mix=False)
        for i, v in enumerate(me_p.vertices): kb.data[i].co = v.co
        kb.value = 0.0
        R["morphs"][nom] = {"sommets": len(me_p.vertices),
            "amplitude_max_mm": round(max((v.co - base[i]).length for i, v in
                                          enumerate(me_p.vertices)) * 1000, 4),
            "uv_identique": sha_uv(me_p) == uv0}
    bpy.data.meshes.remove(me_p)
for k in tete.data.shape_keys.key_blocks:
    if k.name != "Basis": k.value = 0.0
# poids cage -> dense par plus proche triangle
bm = bmesh.new(); bm.from_mesh(tete.data); bm.transform(tete.matrix_world)
bmesh.ops.triangulate(bm, faces=bm.faces[:]); bvh = BVHTree.FromBMesh(bm)
tris = [[v.index for v in f.verts] for f in bm.faces]; bm.free()
gh = run.vertex_groups.new(name="DEF_head"); gj = run.vertex_groups.new(name="DEF_jaw")
wj_cage = {}
for i, v in enumerate(tete.data.vertices):
    for g in v.groups:
        if tete.vertex_groups[g.group].name == "TMP_jaw": wj_cage[i] = g.weight
sans_poids = 0
for i, v in enumerate(me_neutre.vertices):
    p = run.matrix_world @ v.co
    loc, nor, idx, d = bvh.find_nearest(p, 0.05)
    if loc is None: sans_poids += 1; continue
    t3 = tris[idx]
    wj = sum(wj_cage.get(j, 0.0) for j in t3) / 3.0
    wj = max(0.0, min(1.0, wj))
    if wj > 0: gj.add([i], wj, "REPLACE")
    if wj < 1: gh.add([i], 1.0 - wj, "REPLACE")
reg.exige("runtime.sommets_sans_poids", "chaque sommet dense a un poids",
          "projection barycentrique", 0, sans_poids, sans_poids == 0)
reg.exige("runtime.pas_de_multires", "le runtime ne porte plus de Multires",
          "objet runtime", 0, sum(1 for m in run.modifiers if m.type == "MULTIRES"),
          not any(m.type == "MULTIRES" for m in run.modifiers))
R["sommets_sans_poids"] = sans_poids
R["registre"] = reg.bilan()
# Le blend runtime ne doit contenir QUE ce qui part a l'export. Garder la cage
# et les yeux dedans faisait exporter deux meshes au lieu d'un.
run.parent = rig
for ob in list(bpy.data.objects):
    if ob.name not in ("GEO_face_runtime", "TMP_F0_JAW_RIG"):
        bpy.data.objects.remove(ob, do_unlink=True)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
R["objets_runtime"] = sorted(x.name for x in bpy.data.objects)
am2 = run.modifiers.new("Armature", "ARMATURE"); am2.object = rig
am2.use_vertex_groups = True; am2.use_bone_envelopes = False
am2.use_deform_preserve_volume = False
c = Rp(o.output); os.makedirs(os.path.dirname(c), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=c)
json.dump(R, open(Rp(o.report), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ok = reg.conclure()
print("RUNTIME", "OK" if ok else "ECHEC", "|", n_dense, "sommets |", len(R["morphs"]), "morphs")
sys.exit(0 if ok else 2)
