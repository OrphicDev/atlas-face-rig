"""F0-E.2 — deux scenes qui ne different QUE par l'ordre Armature/Multires."""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
import numpy as np
from mathutils import Vector, Matrix
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TETE = "GEO-head_animation_realistic"
GARDE = ("GEO-head_animation_realistic", "GEO-head_animation_realistic.sclera.L",
         "GEO-head_animation_realistic.sclera.R", "GEO-head_animation_realistic.iris.L",
         "GEO-head_animation_realistic.iris.R")

def construire(entree, deltas, mask, motion, sortie, armature_dabord):
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(entree))
    for ob in list(bpy.data.objects):
        if ob.name not in GARDE: bpy.data.objects.remove(ob, do_unlink=True)
    tete = bpy.data.objects[TETE]; me = tete.data; M = tete.matrix_world
    basis = [v.co.copy() for v in me.vertices]
    J = json.load(open(motion, encoding="utf-8"))
    piv = M.inverted() @ Vector(J["pivot_world_xyz"])
    axe = (M.inverted().to_3x3() @ Vector(J["hinge_axis_world_xyz"])).normalized()
    arm = bpy.data.armatures.new("TMP_JAW"); rig = bpy.data.objects.new("TMP_F0_JAW_RIG", arm)
    rig.matrix_world = M.copy(); bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode="EDIT")
    b1 = arm.edit_bones.new("TMP_head"); b1.head = piv; b1.tail = piv + Vector((0, 0, .06))
    b2 = arm.edit_bones.new("TMP_jaw"); b2.head = piv; b2.tail = piv + Vector((0, -.055, -.08))
    b2.parent = b1
    bpy.ops.object.mode_set(mode="OBJECT")
    w = np.load(mask).astype(float)
    gh = tete.vertex_groups.new(name="TMP_head"); gj = tete.vertex_groups.new(name="TMP_jaw")
    for i, x in enumerate(w):
        if x < 1.0: gh.add([i], float(1.0 - x), "REPLACE")
        if x > 0.0: gj.add([i], float(x), "REPLACE")
    for nom, cle in (("TMP_blink.L", "blink_L"), ("TMP_blink.R", "blink_R"),
                     ("TMP_mouthClose", "mouth_close")):
        if not me.shape_keys: tete.shape_key_add(name="Basis", from_mix=False)
        k = tete.shape_key_add(name=nom, from_mix=False); k.value = 0.0
        D = json.load(open(os.path.join(deltas, cle + ".cage-delta.json"), encoding="utf-8"))
        for d in D["deltas"]:
            k.data[d["index"]].co = basis[d["index"]] + Vector(d["delta_object_local_xyz"])
    am = tete.modifiers.new("Armature", "ARMATURE"); am.object = rig
    am.use_vertex_groups = True; am.use_bone_envelopes = False
    am.use_deform_preserve_volume = False
    bpy.context.view_layer.objects.active = tete
    idx = list(tete.modifiers).index(am)
    if armature_dabord:
        while list(tete.modifiers).index(am) > 0: bpy.ops.object.modifier_move_up(modifier=am.name)
    else:
        while list(tete.modifiers).index(am) < len(tete.modifiers) - 1:
            bpy.ops.object.modifier_move_down(modifier=am.name)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(sortie))
    return {"objets": sorted(o.name for o in bpy.data.objects),
            "ordre": [m.type for m in tete.modifiers],
            "shape_keys": [k.name for k in me.shape_keys.key_blocks],
            "sommets": len(me.vertices),
            "uv": [c.name for c in me.uv_layers]}

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--deltas", "--jaw-mask", "--jaw-motion", "--output-dir"):
        a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    os.makedirs(Rp(o.output_dir), exist_ok=True)
    A = construire(Rp(o.input), Rp(o.deltas), Rp(o.jaw_mask), Rp(o.jaw_motion),
                   os.path.join(Rp(o.output_dir), "A_ARMATURE_THEN_MULTIRES.blend"), True)
    B = construire(Rp(o.input), Rp(o.deltas), Rp(o.jaw_mask), Rp(o.jaw_motion),
                   os.path.join(Rp(o.output_dir), "B_MULTIRES_THEN_ARMATURE.blend"), False)
    diff = {k: [A[k], B[k]] for k in A if A[k] != B[k]}
    man = {"A": A, "B": B, "differences": diff}
    json.dump(man, open(os.path.join(Rp(o.output_dir), "build-manifest.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    print("AB_BUILD A", A["ordre"], "| B", B["ordre"])
    print("  differences hors ordre :", {k: v for k, v in diff.items() if k != "ordre"})
    sys.exit(0 if set(diff) <= {"ordre"} else 2)
