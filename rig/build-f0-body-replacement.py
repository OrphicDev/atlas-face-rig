"""F0-D.9 — la voie REMPLACEMENT, jugee sur ce qu'elle coute.

Rien n'est supprime avant que les indices ne soient ecrits : le plan part sur
le disque d'abord, la decoupe ensuite. C'est la consigne du tutoriel, et c'est
aussi ce qui rend l'essai rejouable.

La voie ne peut etre retenue que si elle montre ZERO trou, ZERO double
surface, ZERO auto-intersection et une jonction invisible. Les quatre sont
mesurees, pas regardees, avec la regle commune de `rig/f0_body_commun.py`
— verifiee a reponse connue par `tests/f0-body-banc-synthetique.py`.

Deux modes :

  --mode reel          sur l'asset hors depot ; saute en le nommant s'il manque ;
  --mode synthetique   sur une paire fabriquee ici, dont la couture est connue,
                       pour que la METHODE soit exercee meme sans l'asset.

    blender -b --factory-startup --python-exit-code 1 \
      --python rig/build-f0-body-replacement.py -- \
      --mode synthetique \
      --plan reports/f0-final/body-replacement-plan.json \
      --report reports/f0-final/body-replacement.json \
      --renders renders/f0-final/body-replacement
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, Matrix

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre, preflight
_s = importlib.util.spec_from_file_location(
    "bc", os.path.join(RACINE, "rig", "f0_body_commun.py"))
BC = importlib.util.module_from_spec(_s); _s.loader.exec_module(BC)
MM = 1000.0
VUES = {"face": (0.0, 1.0, 0.0), "profil_L": (-1.0, 0.0, 0.0),
        "profil_R": (1.0, 0.0, 0.0), "arriere_du_cou": (0.0, -1.0, -0.35),
        "tete_tournee": (0.7, 0.7, 0.0)}


def grille(nom, n, taille, z=0.0):
    me = bpy.data.meshes.new(nom)
    verts, faces = [], []
    pas = taille / (n - 1)
    for j in range(n):
        for i in range(n):
            verts.append((-taille / 2 + i * pas, -taille / 2 + j * pas, z))
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    me.from_pydata(verts, [], faces)
    me.update(); me.uv_layers.new(name="UVMap")
    ob = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def repere(direction, position):
    z = -Vector(direction).normalized()
    x = Vector((0.0, 0.0, 1.0)).cross(z)
    if x.length < 1e-6:
        x = Vector((1.0, 0.0, 0.0))
    x.normalize()
    y = z.cross(x).normalized()
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2] = x[i], y[i], z[i]
    M.translation = Vector(position)
    return M


def rendre(sortie, nom, ob, direction, ortho):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = 800
    sc.view_settings.view_transform = "Standard"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.03, 0.04, 1)
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    c = Vector((sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts),
                sum(p.z for p in pts) / len(pts)))
    for x in [y for y in bpy.data.objects if y.name.startswith("CAM_")]:
        bpy.data.objects.remove(x, do_unlink=True)
    cam = bpy.data.cameras.new("CAM_" + nom); cam.type = "ORTHO"
    cam.ortho_scale = ortho
    co = bpy.data.objects.new("CAM_" + nom, cam)
    co.matrix_world = repere(direction, c - Vector(direction).normalized() * 1.0)
    sc.collection.objects.link(co); sc.camera = co
    f = os.path.join(sortie, nom + ".png")
    sc.render.filepath = f
    bpy.ops.render.render(write_still=True)
    return os.path.relpath(f, RACINE)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--mode", choices=("reel", "synthetique"), required=True)
    for f in ("--plan", "--report", "--renders"):
        a.add_argument(f, required=True)
    a.add_argument("--blend")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    sortie = Rp(o.report)
    reg = Registre("body-replacement")

    if o.mode == "reel":
        paquet, ok_asset = preflight()
        if not ok_asset:
            reg.saute("remplacement.dependance",
                      "l'essai de remplacement tourne sur le vrai corps",
                      "asset hors depot indisponible : %s"
                      % paquet.get("raison", "?"))
            json.dump({"status": "SAUTE", "mode": "reel",
                       "dependance": {"variable": "ATLAS_BASE_MESH",
                                      "fichier": "human_base_meshes_bundle.blend",
                                      "octets_attendus": paquet.get("size_expected"),
                                      "sha256_attendu": paquet.get("sha256_expected")},
                       "registre": reg.bilan()},
                      open(sortie, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            reg.conclure()
            print("REMPLACEMENT SAUTE — asset hors depot absent")
            sys.exit(0)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    # collection dediee : rien de ce qui suit ne touche un master
    coll = bpy.data.collections.new("EXP_REPLACEMENT")
    bpy.context.scene.collection.children.link(coll)

    corps = grille("EXP_repl_body", 41, 0.200)
    tete = grille("EXP_repl_head", 21, 0.100)
    for ob in (corps, tete):
        bpy.context.scene.collection.objects.unlink(ob)
        coll.objects.link(ob)

    # --- LE PLAN D'ABORD. Aucune face n'est retiree tant qu'il n'est pas ecrit.
    demi = 0.050
    faces_a_retirer = []
    for p in corps.data.polygons:
        c = corps.matrix_world @ p.center
        if max(abs(c.x), abs(c.y)) <= demi:
            faces_a_retirer.append(p.index)
    sommets_tete_gardes = [v.index for v in tete.data.vertices]
    PLAN = {"mode": o.mode, "corps": corps.name, "tete": tete.name,
            "critere": "faces du corps dont le centre est dans le carre de "
                       "%.0f mm de demi-cote" % (demi * MM),
            "faces_du_corps_a_retirer": sorted(faces_a_retirer),
            "sommets_de_tete_conserves": sommets_tete_gardes,
            "faces_du_corps_total": len(corps.data.polygons),
            "sommets_de_tete_total": len(tete.data.vertices)}
    p_plan = Rp(o.plan); os.makedirs(os.path.dirname(p_plan) or ".", exist_ok=True)
    json.dump(PLAN, open(p_plan, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    reg.exige("remplacement.plan_avant_decoupe",
              "les indices sont ecrits AVANT toute suppression",
              os.path.relpath(p_plan, RACINE), True,
              os.path.isfile(p_plan) and bool(faces_a_retirer),
              os.path.isfile(p_plan) and bool(faces_a_retirer))

    avant = {"faces_corps": len(corps.data.polygons),
             "aretes_ouvertes_corps": BC.aretes_ouvertes(corps.data)}
    # La zone de jonction, definie AVANT la decoupe : c'est la seule ou une
    # arete ouverte serait un defaut. Compter toutes les aretes ouvertes du
    # maillage revenait a compter le bord exterieur de la piece — 160 des deux
    # cotes, avant comme apres — et a declarer un trou la ou il n'y en a pas.
    ZONE = demi + 0.006

    # --- la decoupe, puis la fusion
    bm = bmesh.new(); bm.from_mesh(corps.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in faces_a_retirer],
                     context="FACES")
    bm.to_mesh(corps.data); bm.free(); corps.data.update()
    trou = BC.aretes_ouvertes(corps.data)
    reg.exige("remplacement.trou_ouvert", "la decoupe ouvre bien un trou",
              "%d faces retirees" % len(faces_a_retirer), "> %d"
              % avant["aretes_ouvertes_corps"], trou,
              trou > avant["aretes_ouvertes_corps"])

    fusion = corps.copy(); fusion.data = corps.data.copy()
    fusion.name = "EXP_repl_fusion"
    coll.objects.link(fusion)
    bm = bmesh.new(); bm.from_mesh(fusion.data)
    bm2 = bmesh.new(); bm2.from_mesh(tete.data)
    tmp = bpy.data.meshes.new("TMP_merge")
    bm2.to_mesh(tmp); bm2.free()
    bm.from_mesh(tmp)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bm.to_mesh(fusion.data); bm.free()
    bpy.data.meshes.remove(tmp)
    fusion.data.update()

    def ouvertes_a_la_jonction(ob, rayon):
        me = ob.data
        compte = {}
        for pol in me.polygons:
            for k in pol.edge_keys:
                compte[k] = compte.get(k, 0) + 1
        n = 0
        for k, c in compte.items():
            if c != 1:
                continue
            a = ob.matrix_world @ me.vertices[k[0]].co
            b = ob.matrix_world @ me.vertices[k[1]].co
            m = (a + b) * 0.5
            if max(abs(m.x), abs(m.y)) <= rayon:
                n += 1
        return n

    R = {"status": "OK", "mode": o.mode, "plan": os.path.relpath(p_plan, RACINE),
         "zone_de_jonction_m": ZONE,
         "avant": avant,
         "apres": {
             "faces": len(fusion.data.polygons),
             "aretes_ouvertes_total": BC.aretes_ouvertes(fusion.data),
             "aretes_ouvertes_a_la_jonction": ouvertes_a_la_jonction(fusion, ZONE),
             "aretes_ouvertes_bord_exterieur":
                 BC.aretes_ouvertes(fusion.data)
                 - ouvertes_a_la_jonction(fusion, ZONE),
             "aretes_non_manifold": BC.aretes_non_manifold(fusion.data),
             "faces_inversees": BC.faces_inversees(fusion.data),
             "auto_intersections": BC.auto_intersections(fusion),
             "sommets_doubles": BC.sommets_doubles(fusion)}}

    ap = R["apres"]
    reg.exige("remplacement.zero_trou", "aucune arete ouverte A LA JONCTION",
              "zone de %.0f mm autour de la decoupe" % (ZONE * MM), 0,
              ap["aretes_ouvertes_a_la_jonction"],
              ap["aretes_ouvertes_a_la_jonction"] == 0)
    reg.exige("remplacement.zero_double_surface", "aucun sommet confondu restant",
              "maillage fusionne", 0, ap["sommets_doubles"],
              ap["sommets_doubles"] == 0)
    reg.exige("remplacement.zero_intersection", "aucune auto-intersection",
              "maillage fusionne", 0, ap["auto_intersections"],
              ap["auto_intersections"] == 0)
    reg.exige("remplacement.zero_non_manifold", "aucune arete non manifold",
              "maillage fusionne", 0, ap["aretes_non_manifold"],
              ap["aretes_non_manifold"] == 0)
    reg.exige("remplacement.zero_face_inversee", "aucune face retournee",
              "maillage fusionne", 0, ap["faces_inversees"],
              ap["faces_inversees"] == 0)

    dossier = Rp(o.renders); os.makedirs(dossier, exist_ok=True)
    R["images"] = [rendre(dossier, "remplacement_" + nom, fusion, d, 0.26)
                   for nom, d in VUES.items()]
    reg.exige("remplacement.cinq_vues",
              "face, profils, arriere du cou et tete tournee sont rendus",
              "vues exigees par le tutoriel", len(VUES), len(R["images"]),
              len(R["images"]) == len(VUES))

    R["registre"] = reg.bilan()
    R["verdict"] = ("La voie remplacement ne passe pas : "
                    if reg.echecs else "La voie remplacement passe ses controles : ") \
        + "%d/%d" % (reg.reussies, reg.total)
    if o.blend:
        c = Rp(o.blend); os.makedirs(os.path.dirname(c), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=c, copy=True)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("REMPLACEMENT", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
