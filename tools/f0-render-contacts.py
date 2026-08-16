"""F0-B.13 — preuves des contacts, camera SIGNEE une seule fois sur le neutre.

La bounding box n'est jamais recalculee apres deformation : le visage ne doit
pas changer de taille dans le cadre entre 000 et 100.
"""
import argparse, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TETE = "GEO-head_animation_realistic"

def scene(k=7.22, res=1000):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = 0.0
    sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (.05, .05, .055, 1)
    clay = bpy.data.materials.new("CLAY"); clay.use_nodes = True
    clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.42, .42, .42, 1)
    oeil = bpy.data.materials.new("OEIL"); oeil.use_nodes = True
    oeil.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.62, .20, .16, 1)
    for o in [x for x in bpy.data.objects if x.type == "MESH"]:
        o.data.materials.clear()
        o.data.materials.append(oeil if ("sclera" in o.name or "iris" in o.name) else clay)
        for p in o.data.polygons: p.use_smooth = True
    t = bpy.data.objects[TETE]
    co = [t.matrix_world @ v.co for v in t.data.vertices]
    mn = Vector([min(c[i] for c in co) for i in range(3)])
    mx = Vector([max(c[i] for c in co) for i in range(3)])
    C = (mn + mx) / 2
    cible = Vector((C.x, C.y - .005, mn.z + (mx.z - mn.z) * .69))
    for nom, pos, e, s in (("KEY", (C.x + .62, C.y - .30, cible.z + .16), 1.0, .22),
                           ("FILL", (C.x - .75, C.y - .55, cible.z - .02), .13, .75),
                           ("RIM", (C.x - .25, C.y + .85, cible.z + .30), .25, .40)):
        d = bpy.data.lights.new(nom, "AREA"); d.energy = e * k; d.size = s
        ob = bpy.data.objects.new(nom, d); ob.location = pos
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = (cible - Vector(pos)).normalized().to_track_quat("-Z", "Y")
        sc.collection.objects.link(ob)
    cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"
    cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
    return sc, cam, cd, mn, mx, C

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--deltas", "--output-dir", "--settings"): a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
    tete = bpy.data.objects[TETE]; me = tete.data
    basis = [v.co.copy() for v in me.vertices]
    sc, cam, cd, mn, mx, C = scene()
    G = json.load(open(os.path.join(RACINE, "config/globe-fit.json"), encoding="utf-8"))
    # CAMERAS SIGNEES sur le neutre, jamais recalculees ensuite
    CAM = {}
    for cote in ("L", "R"):
        c = Vector(G["eyes"][cote]["center_world_xyz"])
        CAM["blink_" + cote] = {"dir": (0.38 if cote == "L" else -0.38, -1, .12),
                                "ortho": .055, "cible": [c.x, mn.y + .015, c.z]}
    CAM["mouth_close"] = {"dir": (.10, -1, -.12), "ortho": .075,
                          "cible": [C.x, mn.y + .01, .6942]}
    S = {"resolution": [sc.render.resolution_x] * 2, "moteur": sc.render.engine,
         "transformation_de_vue": sc.view_settings.view_transform, "vues": {}}
    def rendre(nom, pose, t, wire=False):
        k = CAM[pose]; d = Vector(k["dir"]).normalized()
        cam.location = Vector(k["cible"]) + d * 1.5; cd.ortho_scale = k["ortho"]
        cam.rotation_mode = "QUATERNION"; cam.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
        f = os.path.join(Rp(o.output_dir), nom + ".png")
        sc.render.filepath = f; bpy.ops.render.render(write_still=True)
        S["vues"][nom] = {"pose": pose, "t": t,
                          "matrice_camera": [[round(float(x), 9) for x in l] for l in cam.matrix_world],
                          "ortho_scale": round(float(cd.ortho_scale), 9),
                          "fichier": os.path.relpath(f, RACINE)}
        print("VUE", nom)
    os.makedirs(Rp(o.output_dir), exist_ok=True)
    for pose in ("blink_L", "blink_R", "mouth_close"):
        D = json.load(open(os.path.join(Rp(o.deltas), pose + ".cage-delta.json"), encoding="utf-8"))
        S.setdefault("sha_deltas", {})[pose] = D["sha256_du_tableau"]
        dl = {d["index"]: Vector(d["delta_object_local_xyz"]) for d in D["deltas"]}
        for t, et in ((0.0, "000"), (0.5, "050"), (1.0, "100")):
            for i, v in dl.items(): me.vertices[i].co = basis[i] + v * t
            me.update()
            nom = ("lips_" + et) if pose == "mouth_close" else (pose + "_" + et)
            rendre(nom, pose, t)
        for i in dl: me.vertices[i].co = basis[i]
        me.update()
    p = Rp(o.settings); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(S, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("CONTACTS_RENDER_OK", len(S["vues"]), "vues ->", o.output_dir)
