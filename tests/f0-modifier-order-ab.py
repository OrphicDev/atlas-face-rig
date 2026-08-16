"""F0-E.5 — performance, memoire et geometrie des deux ordres."""
import argparse, hashlib, json, math, os, statistics, struct, sys, time
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector, Matrix
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TETE = "GEO-head_animation_realistic"
POSES = ("neutral", "blink_L_100", "blink_R_100", "mouthClose_100", "jaw_20", "jaw_32")

def evaluer(ob):
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg); me = ev.to_mesh()
    co = [ob.matrix_world @ v.co.copy() for v in me.vertices]
    n = (len(me.vertices), len(me.polygons), len(me.loops))
    h = hashlib.sha256()
    c = me.uv_layers.active
    if c:
        for d in c.data: h.update(struct.pack("<2f", d.uv[0], d.uv[1]))
    ev.to_mesh_clear()
    return co, n, h.hexdigest()

def poser(rig, tete, pose, J):
    for k in tete.data.shape_keys.key_blocks:
        if k.name != "Basis": k.value = 0.0
    pb = rig.pose.bones["TMP_jaw"]; pb.rotation_mode = "XYZ"
    pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
    if pose.startswith("blink"): tete.data.shape_keys.key_blocks["TMP_blink." + pose[6]].value = 1.0
    elif pose == "mouthClose_100": tete.data.shape_keys.key_blocks["TMP_mouthClose"].value = 1.0
    elif pose.startswith("jaw_"):
        deg = float(pose.split("_")[1]); pb.rotation_euler.x = math.radians(deg)
    bpy.context.view_layer.update()

a = argparse.ArgumentParser(); a.add_argument("--label", required=True)
a.add_argument("--output", required=True); a.add_argument("--motion", required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
tete = bpy.data.objects[TETE]; rig = bpy.data.objects["TMP_F0_JAW_RIG"]
J = json.load(open(Rp(o.motion), encoding="utf-8"))
R = {"label": o.label, "blend": os.path.relpath(bpy.data.filepath, RACINE),
     "ordre": [m.type for m in tete.modifiers],
     "octets_blend": os.path.getsize(bpy.data.filepath), "poses": {}}
poser(rig, tete, "neutral", J); ref, nref, uvref = evaluer(tete)
for pose in POSES:
    poser(rig, tete, pose, J)
    for _ in range(5): evaluer(tete)
    ts = []
    for _ in range(20):
        t0 = time.perf_counter(); co, n, uv = evaluer(tete); ts.append(time.perf_counter() - t0)
    ts.sort()
    d = [(x - y).length * 1000 for x, y in zip(co, ref)] if len(co) == len(ref) else None
    R["poses"][pose] = {"sommets": n[0], "faces": n[1], "loops": n[2],
        "temps_median_s": round(statistics.median(ts), 6),
        "temps_p95_s": round(ts[int(len(ts) * .95)], 6), "temps_max_s": round(ts[-1], 6),
        "uv_sha": uv, "uv_identique_au_neutre": uv == uvref,
        "ecart_au_neutre_mm": {"max": round(max(d), 5), "median": round(statistics.median(d), 5)} if d else None}
poser(rig, tete, "neutral", J)
co0, _, _ = evaluer(tete)
R["retour_neutre_mm"] = round(max((a2 - b2).length for a2, b2 in zip(co0, ref)) * 1000, 9)
p = Rp(o.output); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("AB", o.label, R["ordre"], "median jaw_32 %.5f s" % R["poses"]["jaw_32"]["temps_median_s"],
      "| retour neutre %.9f mm" % R["retour_neutre_mm"])
