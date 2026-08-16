"""F0-D.8 — contre-epreuve Surface Deform, sur un duplicata reserve.

Le master n'est jamais touche : le modificateur est pose sur une COPIE du
corps, liee au neutre, et le bake n'a lieu que dans cette copie.

La regle de mesure est celle de `rig/f0_body_commun.py`, la meme que la voie
barycentrique — deux regles differentes rendraient la comparaison creuse. Elle
est verifiee a reponse connue par `tests/f0-body-banc-synthetique.py`, ou les
deux voies retrouvent une levee de 3,000 mm a 2 nanometres pres.

Cette etape depend d'un fichier HORS DEPOT (ATLAS_BASE_MESH). Absent, elle
publie un rapport SAUTE qui nomme la dependance, et ne pretend rien.

    blender -b --factory-startup --python-exit-code 1 \
      --python rig/f0-body-surface-deform.py -- \
      --fit reports/f0-final/head-body-fit.json \
      --deltas reports/f0-final/deformations \
      --motion config/jaw-motion.json \
      --report reports/f0-final/body-surface-deform.json \
      --work-blend experiments/body-transfer/F0_BODY_SURFACE_DEFORM.blend
"""
import argparse, importlib.util, json, os, sys
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

TETE = "GEO-head_animation_realistic"
CORPS = "GEO-body_male_realistic"
GROUPE = "VG_F0_FACE_TRANSFER"
POSES = ["neutral", "blink_L_100", "blink_R_100", "lips_close_100",
         "jaw_20", "jaw_32"]
DELTAS = {"blink_L_100": "blink_L", "blink_R_100": "blink_R",
          "lips_close_100": "mouth_close"}
MM = 1000.0


def sauter(chemin, raison, detail):
    reg = Registre("body-surface-deform")
    reg.saute("surface_deform.dependance",
              "la contre-epreuve Surface Deform tourne sur le vrai corps", raison)
    R = {"status": "SAUTE", "raison": raison, "dependance": detail,
         "registre": reg.bilan()}
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    json.dump(R, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    reg.conclure()
    print("SURFACE_DEFORM SAUTE —", raison)
    sys.exit(0)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--fit", "--deltas", "--motion", "--report"):
        a.add_argument(f, required=True)
    a.add_argument("--work-blend")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    sortie = Rp(o.report)

    paquet, ok_asset = preflight()
    if not ok_asset:
        sauter(sortie, "asset hors depot indisponible : %s"
               % paquet.get("raison", "?"),
               {"variable": "ATLAS_BASE_MESH",
                "fichier": paquet.get("path_basename",
                                      "human_base_meshes_bundle.blend"),
                "octets_attendus": paquet.get("size_expected"),
                "sha256_attendu": paquet.get("sha256_expected"),
                "paquet": paquet.get("paquet"), "licence": paquet.get("licence")})

    chemin_asset = os.environ["ATLAS_BASE_MESH"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(chemin_asset, link=False) as (src, dst):
        dst.collections = ["Head (Animation) - Realistic", "Body Male - Realistic"]
    for c in dst.collections:
        bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.update()
    tete = bpy.data.objects[TETE]
    corps = bpy.data.objects[CORPS]

    F = json.load(open(Rp(o.fit), encoding="utf-8"))
    Mh2b = Matrix([[float(x) for x in l] for l in F["M_head_to_body"]])
    reg = Registre("body-surface-deform")

    # --- la tete source, alignee sur le corps, dans un duplicata d'experience
    src_tete = tete.copy(); src_tete.data = tete.data.copy()
    src_tete.name = "EXP_head_source"
    bpy.context.scene.collection.objects.link(src_tete)
    src_tete.matrix_world = Mh2b @ tete.matrix_world
    neutre_tete = [v.co.copy() for v in src_tete.data.vertices]

    # --- le corps d'experience, jamais le master
    cible = corps.copy(); cible.data = corps.data.copy()
    cible.name = "EXP_body_target"
    bpy.context.scene.collection.objects.link(cible)
    ref = [v.co.copy() for v in cible.data.vertices]

    # --- masque : les memes sommets que la voie barycentrique
    T = json.load(open(Rp("reports/f0-final/body-transfer-map.json"),
                       encoding="utf-8"))
    masque_idx = sorted(int(k) for k in T["carte"]) if isinstance(T["carte"], dict) \
        else []
    if not masque_idx:
        sauter(sortie, "la carte barycentrique ne publie pas ses indices",
               {"fichier": "reports/f0-final/body-transfer-map.json"})
    g = cible.vertex_groups.get(GROUPE) or cible.vertex_groups.new(name=GROUPE)
    g.add(masque_idx, 1.0, "REPLACE")
    reg.exige("surface_deform.groupe", "le groupe porte le masque facial",
              GROUPE, len(masque_idx), len(masque_idx), True)

    sd = cible.modifiers.new("SurfaceDeform", "SURFACE_DEFORM")
    sd.target = src_tete
    sd.vertex_group = GROUPE
    bpy.context.view_layer.objects.active = cible
    bpy.ops.object.surfacedeform_bind(modifier=sd.name)
    reg.exige("surface_deform.bind", "le modificateur s'est lie au neutre",
              "cible %s, groupe %s" % (src_tete.name, GROUPE), True,
              bool(sd.is_bound), bool(sd.is_bound))
    if not sd.is_bound:
        json.dump({"status": "ECHEC", "raison": "bind refuse",
                   "registre": reg.bilan()},
                  open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        reg.conclure(); sys.exit(2)

    R = {"status": "OK", "asset": paquet, "poses": {}}
    for pose in POSES:
        dep = {}
        nom_delta = DELTAS.get(pose)
        if nom_delta:
            D = json.load(open(os.path.join(Rp(o.deltas),
                                            nom_delta + ".cage-delta.json"),
                               encoding="utf-8"))
            dep = {d["index"]: Vector(d["delta_object_local_xyz"])
                   for d in D["deltas"]}
        for i, v in enumerate(src_tete.data.vertices):
            v.co = neutre_tete[i] + dep.get(i, Vector((0, 0, 0)))
        src_tete.data.update(); src_tete.update_tag()
        bpy.context.view_layer.update()
        with BC.Chrono() as c:
            dg = bpy.context.evaluated_depsgraph_get()
            ev = cible.evaluated_get(dg)
            me_ev = ev.to_mesh()
            cour = [v.co.copy() for v in me_ev.vertices]
            ev.to_mesh_clear()
        # bake DANS LE DUPLICATA seulement, sur une copie par pose
        cuit = cible.copy(); cuit.data = cible.data.copy()
        cuit.name = "EXP_body_SD_" + pose
        bpy.context.scene.collection.objects.link(cuit)
        for m in list(cuit.modifiers):
            cuit.modifiers.remove(m)
        for i, v in enumerate(cuit.data.vertices):
            v.co = cour[i]
        cuit.data.update()
        R["poses"][pose] = BC.bilan_methode("surface_deform", ref, cour,
                                            set(masque_idx), cuit, c.duree)

    hors = max(p["deplacement_hors_masque_mm"]["max"] for p in R["poses"].values())
    reg.exige("surface_deform.hors_groupe",
              "aucun sommet hors du groupe ne bouge", "six poses",
              "<= 0,01 mm", round(hors, 6), hors <= 0.01, tolerance=0.01)
    neutre = R["poses"]["neutral"]["deplacement_dans_le_masque_mm"]["max"]
    reg.exige("surface_deform.neutre_inchange",
              "au neutre, le corps ne bouge pas", "pose neutral", "<= 0,01 mm",
              round(neutre, 6), neutre <= 0.01, tolerance=0.01)
    R["registre"] = reg.bilan()

    if o.work_blend:
        c = Rp(o.work_blend); os.makedirs(os.path.dirname(c), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=c, copy=True)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("SURFACE_DEFORM", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
