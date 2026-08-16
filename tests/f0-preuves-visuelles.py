"""Preuves visuelles des prototypes jetables et coupe sagittale.

Ne touche jamais la source autoritaire : tout se passe sur des duplicatas en
memoire, rien n'est sauvegarde par-dessus le maitre.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-preuves-visuelles.py -- \
      source/FACE_BASE_LOCKED.blend renders/f0-correction
"""
import json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
from anatomie import Clignement, FermetureLabiale, Machoire

BLEND, SORTIE = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(SORTIE, exist_ok=True)
TETE = "GEO-head_animation_realistic"
RES = 1000


def ouvrir():
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(BLEND))
    return bpy.data.objects[TETE]


def scene_clay(k=7.22):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.0
    sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.055, 1)
    clay = bpy.data.materials.new("CLAY"); clay.use_nodes = True
    b = clay.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.42, 0.42, 0.42, 1)
    b.inputs["Roughness"].default_value = 0.55
    oeil = bpy.data.materials.new("OEIL"); oeil.use_nodes = True
    bo = oeil.node_tree.nodes["Principled BSDF"]
    bo.inputs["Base Color"].default_value = (0.62, 0.20, 0.16, 1)
    for o in [x for x in bpy.data.objects if x.type == "MESH"]:
        o.data.materials.clear()
        o.data.materials.append(oeil if ("sclera" in o.name or "iris" in o.name) else clay)
        for p in o.data.polygons: p.use_smooth = True
    tete = bpy.data.objects[TETE]
    co = [tete.matrix_world @ v.co for v in tete.data.vertices]
    mn = Vector([min(c[i] for c in co) for i in range(3)])
    mx = Vector([max(c[i] for c in co) for i in range(3)])
    C = (mn + mx) / 2
    cible = Vector((C.x, C.y - 0.005, mn.z + (mx.z - mn.z) * 0.69))
    for nom, pos, e, t in (("KEY", (C.x + 0.62, C.y - 0.30, cible.z + 0.16), 1.00, 0.22),
                           ("FILL", (C.x - 0.75, C.y - 0.55, cible.z - 0.02), 0.13, 0.75),
                           ("RIM", (C.x - 0.25, C.y + 0.85, cible.z + 0.30), 0.25, 0.40)):
        d = bpy.data.lights.new(nom, "AREA"); d.energy = e * k; d.size = t
        o = bpy.data.objects.new(nom, d); o.location = pos
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = (cible - Vector(pos)).normalized().to_track_quat("-Z", "Y")
        sc.collection.objects.link(o)
    cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"
    cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
    return sc, cam, cd, mn, mx, C


def vue(sc, cam, cd, nom, direction, ortho, cible):
    d = Vector(direction).normalized()
    cam.location = Vector(cible) + d * 1.5
    cd.ortho_scale = ortho
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
    sc.render.filepath = os.path.join(SORTIE, nom + ".png")
    bpy.ops.render.render(write_still=True)
    print("VUE", nom)


def poser(ob, deltas):
    if not ob.data.shape_keys: ob.shape_key_add(name="Basis", from_mix=False)
    k = ob.shape_key_add(name="PROTO", from_mix=False)
    Mi = ob.matrix_world.inverted().to_3x3()
    for i, d in enumerate(deltas):
        if d.length > 0.0: k.data[i].co = k.data[i].co + (Mi @ d)
    k.value = 1.0
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()


def haute_res(ob):
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg),
                                         preserve_all_data_layers=True, depsgraph=dg)
    dup = bpy.data.objects.new("HAUTE_RES", me)
    dup.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(dup)
    for m in list(dup.modifiers): dup.modifiers.remove(m)
    ob.hide_render = True
    return dup


def globes(ob):
    g = {}
    for c in "LR":
        s = bpy.data.objects[TETE + ".sclera." + c]
        pts = [s.matrix_world @ v.co for v in s.data.vertices]
        ctr = Vector([sum(p[i] for p in pts) / len(pts) for i in range(3)])
        g[c] = (ctr, sum((p - ctr).length for p in pts) / len(pts))
    return g


# Les bords publies en F0 : la deformation et la mesure doivent porter sur le
# meme ensemble de sommets, c'est la lecon de la passe 3.
_F0 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "reports", "f0", "audit-topologie.json"),
                     encoding="utf-8"))
BORDS = {a["nom"].split(".")[1]: a["indices"] for a in _F0["ouvertures"]
         if (a.get("nom") or "").startswith("fente_palpebrale")}
BORD_LEVRES = next(a["indices"] for a in _F0["ouvertures"]
                   if a.get("nom") == "fente_labiale")


def cage_monde():
    t = bpy.data.objects[TETE]
    return [t.matrix_world @ v.co for v in t.data.vertices]


def deltas_clignement(co, ob, it):
    g = globes(ob); lat = (g["L"][0] - g["R"][0]).normalized()
    cage = cage_monde()
    out = [Vector((0, 0, 0)) for _ in co]
    for c in "LR":
        cl = Clignement([cage[i] for i in BORDS[c]], g[c][0], g[c][1], lat)
        for i, p in enumerate(co):
            out[i] = out[i] + cl.deplacer(p, it)
    return out


def deltas_levres(co, ob, it):
    cage = cage_monde()
    f = FermetureLabiale([cage[i] for i in BORD_LEVRES])
    return [f.deplacer(p, it) for p in co]


def deltas_machoire(co, ob, deg):
    cage = cage_monde()
    bord = [cage[i] for i in BORD_LEVRES]
    z_levre = sum(p.z for p in bord) / len(bord)
    m = Machoire(Vector((sum(p.x for p in co) / len(co), -0.053, 0.740)),
                 Vector((1, 0, 0)), z_levre=z_levre, z_menton=0.6480,
                 y_arriere=-0.060, z_bas_cou=0.6100)
    return [m.deplacer(p, deg) for p in co]


PROTOS = {"clignement": deltas_clignement, "levres": deltas_levres,
          "machoire": deltas_machoire}


def rendre(proto, valeur, voie, nom, direction, ortho, cible_rel):
    ob = ouvrir()
    if voie == "B":
        ob = haute_res(bpy.data.objects[TETE])
    co = [ob.matrix_world @ v.co for v in ob.data.vertices]
    if valeur:
        poser(ob, PROTOS[proto](co, bpy.data.objects[TETE], valeur))
    sc, cam, cd, mn, mx, C = scene_clay()
    cible = Vector((C.x + cible_rel[0], mn.y + cible_rel[1], cible_rel[2]))
    vue(sc, cam, cd, nom, direction, ortho, cible)


if __name__ == "__main__":
    OEIL = ((0.38, -1, 0.12), 0.055, (0.0343, 0.015, 0.7653))
    BOUCHE = ((0.10, -1, -0.12), 0.075, (0.0, 0.010, 0.6942))
    for v, et in ((0.0, "000"), (0.50, "050"), (1.0, "100")):
        rendre("clignement", v, "A", "multires_clignement_A_%s" % et, *OEIL)
    rendre("clignement", 1.0, "B", "multires_clignement_B_100", *OEIL)
    for v, et in ((0.0, "000"), (1.0, "100")):
        rendre("levres", v, "A", "multires_levres_A_%s" % et, *BOUCHE)
    rendre("levres", 1.0, "B", "multires_levres_B_100", *BOUCHE)
    PROFIL = ((0.55, -0.85, -0.10), 0.150, (0.0, 0.03, 0.700))
    for deg in (0, 10, 20, 32):
        rendre("machoire", float(deg), "A", "multires_machoire_A_%02d" % deg, *PROFIL)

    # ---- coupe sagittale : duplicata coupe, maitre intact ----
    ob = ouvrir()
    mailles = [o for o in bpy.data.objects if o.type == "MESH"]
    co = [ob.matrix_world @ v.co for v in ob.data.vertices]
    CX = (min(c.x for c in co) + max(c.x for c in co)) / 2
    for o in list(mailles):
        d = o.data.copy(); cut = bpy.data.objects.new(o.name + "_CUT", d)
        cut.matrix_world = o.matrix_world.copy()
        bpy.context.scene.collection.objects.link(cut)
        for m in list(cut.modifiers): cut.modifiers.remove(m)
        bm = bmesh.new(); bm.from_mesh(d)
        pl = cut.matrix_world.inverted() @ Vector((CX, 0, 0))
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=pl, plane_no=Vector((1, 0, 0)), clear_outer=True)
        bm.to_mesh(d); bm.free()
        o.hide_render = True
    sc, cam, cd, mn, mx, C = scene_clay()
    vue(sc, cam, cd, "coupe_sagittale_generale", (1, 0.001, 0), 0.26,
        Vector((CX, C.y - 0.01, mn.z + (mx.z - mn.z) * 0.72)))
    vue(sc, cam, cd, "coupe_sagittale_bouche", (1, 0.001, 0), 0.090,
        Vector((CX, mn.y + 0.045, 0.692)))
    vue(sc, cam, cd, "coupe_sagittale_oeil", (1, 0.001, 0), 0.070,
        Vector((CX, mn.y + 0.045, 0.767)))
    print("PREUVES_OK ->", SORTIE)
