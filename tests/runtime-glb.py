"""F0-E.11 — le GLB se suffit-il a lui-meme ?

Trois evaluations de la MEME animation sont confrontees :

  A. Blender rejouant le blend runtime d'origine (la verite d'auteur) ;
  B. Blender rejouant le GLB reimporte ;
  C. `tools/runtime_eval.py`, une implementation de la specification glTF
     ecrite ici, en Python pur, qui n'a jamais vu Blender ni le blend.

B vs A dit si la deformation survit au transport. C vs B dit si un runtime
quelconque, qui ne connait que la specification, retrouve la meme chose — donc
si le fichier porte tout ce qu'il faut, sans rien qui vienne de Blender.

    blender -b --factory-startup --python-exit-code 1 \
      --python tests/runtime-glb.py -- \
      --input exports/atlas-face-spike.glb \
      --source experiments/gltf-spike/spike.blend \
      --animation-reference experiments/gltf-spike/spike-reference.json \
      --report reports/f0-final/runtime-glb.json
"""
import argparse, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "re_", os.path.join(RACINE, "tools", "runtime_eval.py"))
RE = importlib.util.module_from_spec(_s); _s.loader.exec_module(RE)
MM = 1000.0


def evalue(obj, frames):
    """Positions monde apres TOUS les modificateurs, image par image."""
    out = {}
    for f in frames:
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        me = ev.to_mesh()
        M = ev.matrix_world
        out[f] = [(M @ v.co).copy() for v in me.vertices]
        ev.to_mesh_clear()
    return out


def activer_nla(objets):
    """L'importeur range certaines actions en NLA au lieu de les activer."""
    range_ = []
    for bloc in objets:
        for ad in (bloc.animation_data,
                   getattr(getattr(bloc, "data", None), "shape_keys", None)
                   and bloc.data.shape_keys.animation_data):
            if ad and ad.action is None and ad.nla_tracks:
                st = ad.nla_tracks[0].strips[0]
                ad.action = st.action
                try: ad.action_slot = ad.action.slots[0]
                except Exception: pass
                range_.append(st.action.name)
    return range_


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--source", "--animation-reference", "--report"):
        a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    frames = sorted(int(k) for k in json.load(
        open(Rp(o.animation_reference), encoding="utf-8"))["frames"])
    reg = Registre("runtime-glb")

    # ---- A : le blend d'auteur
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.source)))
    fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
    A = evalue(bpy.data.objects["GEO_face_runtime"], frames)

    # ---- le pivot EFFECTIF de la deformation, contre celui du contrat.
    # Aucune sonde ne regardait ou tourne la machoire : le maillage runtime a
    # ete exporte 1,46 m a cote de son propre rig sans qu'une seule sonde le
    # voie, parce qu'elles comparaient toutes le meme montage fautif a
    # lui-meme. Une rotation autour d'un point CONSERVE la distance a ce point.
    ob_a = bpy.data.objects["GEO_face_runtime"]
    JM = json.load(open(Rp("config/jaw-motion.json"), encoding="utf-8"))
    pivot = Vector(JM["pivot_world_xyz"])
    # Le groupe qui deforme est celui qui PORTE LE NOM DE L'OS : le lire dans
    # l'armature, pas le nommer a la main. J'avais pris `DEF_jaw`, qui existe
    # aussi mais ne deforme rien — 733 sommets contre 864, d'ou une derive
    # radiale qui ne venait que de mon choix de groupe.
    os_jaw = "TMP_jaw"
    if os_jaw not in ob_a.vertex_groups:
        raise SystemExit("aucun groupe nomme comme l'os %r" % os_jaw)
    gi = ob_a.vertex_groups[os_jaw].index
    durs = [v.index for v in ob_a.data.vertices
            if any(g.group == gi and g.weight >= 0.999 for g in v.groups)]
    f_ouvert = max(frames, key=lambda f: max(
        (A[f][i] - A[frames[0]][i]).length for i in durs[:200]) if durs else 0)
    derive = max(abs((A[f_ouvert][i] - pivot).length
                     - (A[frames[0]][i] - pivot).length) * MM for i in durs)
    reg.exige("runtime.pivot_machoire",
              "la machoire tourne autour du pivot du contrat",
              "%d sommets du groupe %s a poids >= 0,999, image %d"
              % (len(durs), os_jaw, f_ouvert),
              "<= 0,05 mm de derive radiale", round(derive, 6), derive <= 0.05,
              tolerance=0.05)
    # Le pivot doit etre DANS la boite du maillage. La sonde de pivot ne peut
    # pas porter cet invariant : une rotation autour d'un point reste une
    # rotation autour de ce point meme si le maillage est a un metre de la
    # (contre-epreuve : tests/runtime-pivot-negatif.py).
    coins = [ob_a.matrix_world @ Vector(c) for c in ob_a.bound_box]
    mn = [min(p[i] for p in coins) - 0.005 for i in range(3)]
    mx = [max(p[i] for p in coins) + 0.005 for i in range(3)]
    dedans = all(mn[i] <= pivot[i] <= mx[i] for i in range(3))
    reg.exige("runtime.pivot_dans_la_boite",
              "le milieu des conduits auditifs est dans la tete",
              "boite monde [%s ; %s]" % ([round(x, 3) for x in mn],
                                         [round(x, 3) for x in mx]),
              True, dedans, dedans)
    course = max((A[f_ouvert][i] - A[frames[0]][i]).length for i in durs) * MM
    reg.exige("runtime.course_machoire",
              "la course de la machoire est celle d'une machoire",
              "rotation de %.0f deg, image %d" % (JM["rotation_max_deg"], f_ouvert),
              "entre 20 et 90 mm", round(course, 4), 20.0 <= course <= 90.0)

    # ---- B : le GLB rejoue par Blender
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(Rp(o.input)))
    imp = [x for x in bpy.data.objects if x.type == "MESH" and x.name != "Icosphere"][0]
    arms = [x for x in bpy.data.objects if x.type == "ARMATURE"]
    reveilles = activer_nla([imp] + arms)
    B = evalue(imp, frames)

    # ---- la correspondance d'images vers les temps du fichier, MESUREE
    J, BIN, an, taille = RE.VG.lire_glb(os.path.abspath(Rp(o.input)))
    ent = [v[0] for v in RE.VG.decoder(
        J, BIN, J["animations"][0]["samplers"][0]["input"])]
    # L'horloge est LUE, pas supposee : je l'avais supposee en (f-1)/fps, le
    # fichier dit f/fps. Le decalage est mesure sur la premiere clef puis
    # verifie sur la derniere — une correspondance qui ne colle qu'a un bout
    # n'est pas une correspondance.
    decalage = round(ent[0] * fps - min(frames))
    ecart = max(abs(ent[0] - (min(frames) + decalage) / fps),
                abs(ent[-1] - (max(frames) + decalage) / fps))
    reg.exige("runtime.horloge", "image -> seconde retrouvee sur le fichier",
              "clefs de %.6f a %.6f s, %g im/s" % (ent[0], ent[-1], fps),
              "<= 1e-4 s aux deux bouts", round(ecart, 8), ecart <= 1e-4,
              tolerance=1e-4)
    temps = [(f + decalage) / fps for f in frames]

    # ---- C : la specification, sans Blender
    C, info = RE.evaluer(J, BIN, temps)

    # ---- glTF est en Y-haut, Blender en Z-haut : la conversion est une
    # convention du format, pas un reglage. (x, y, z) -> (x, -z, y). Sans elle
    # je comparais deux reperes differents et je lisais 1936 mm d'ecart.
    CONV = lambda p: Vector((p[0], -p[2], p[1]))

    # ---- l'ordre des sommets est-il conserve a l'import ?
    base = RE.VG.decoder(J, BIN,
                         J["meshes"][0]["primitives"][0]["attributes"]["POSITION"])
    n0 = frames[0]
    ecarts0 = [ (CONV(base[i]) - B[n0][i]).length * MM
                for i in range(min(len(base), len(B[n0]))) ]
    ordre_ok = (len(base) == len(B[n0])) and max(ecarts0) <= 0.05
    reg.exige("runtime.ordre_sommets",
              "l'import conserve l'ordre des sommets du fichier",
              "%d positions" % len(base), "<= 0,05 mm au neutre",
              round(max(ecarts0), 6) if ecarts0 else -1.0, ordre_ok,
              tolerance=0.05)

    # ---- B vs A : la deformation survit-elle au transport ?
    ba = {}
    for f in frames:
        bm = bmesh.new()
        for p in A[f]:
            bm.verts.new(p)
        bm.verts.ensure_lookup_table()
        # surface d'auteur : on reprend la topologie du blend d'origine
        bm.free()
        d = []
        # BVH sur le maillage evalue d'auteur
        me = bpy.data.meshes.new("TMP")
        me.from_pydata([tuple(p) for p in A[f]], [], [])
        me.update()
        bm2 = bmesh.new(); bm2.from_mesh(me)
        bm2.verts.ensure_lookup_table()
        from mathutils import kdtree
        kd = kdtree.KDTree(len(A[f]))
        for i, p in enumerate(A[f]):
            kd.insert(p, i)
        kd.balance()
        for p in B[f]:
            d.append(kd.find(p)[2] * MM)
        bm2.free(); bpy.data.meshes.remove(me)
        d.sort()
        ba[f] = {"p50": round(d[len(d) // 2], 6),
                 "p95": round(d[int(len(d) * .95)], 6), "max": round(d[-1], 6)}
    pire_ba = max(v["p95"] for v in ba.values())
    reg.exige("runtime.transport", "la deformation survit au GLB",
              "%d poses, plus proche sommet d'auteur" % len(frames),
              "<= 0,25 mm au p95", round(pire_ba, 6), pire_ba <= 0.25,
              tolerance=0.25)

    # ---- C vs B : la specification suffit-elle ?
    cb, pire = {}, 0.0
    for k, f in enumerate(frames):
        d = sorted((CONV(C[temps[k]][i]) - B[f][i]).length * MM
                   for i in range(len(B[f])))
        cb[f] = {"p50": round(d[len(d) // 2], 6),
                 "p95": round(d[int(len(d) * .95)], 6), "max": round(d[-1], 6)}
        pire = max(pire, d[-1])
    reg.exige("runtime.specification",
              "un runtime qui ne lit que la specification retrouve la pose",
              "%d poses, sommet a sommet" % len(frames), "<= 0,01 mm au pire",
              round(pire, 6), pire <= 0.01, tolerance=0.01)

    # ---- une pose au moins doit BOUGER, sinon on compare deux immobiles
    amp = max((Vector(C[temps[k]][i]) - Vector(C[temps[0]][i])).length * MM
              for k in range(1, len(frames))
              for i in range(0, len(base), 97))
    reg.exige("runtime.amplitude", "les poses ne sont pas toutes identiques",
              "echantillon d'un sommet sur 97", ">= 5 mm", round(amp, 4), amp >= 5.0)

    R = {"fps": fps, "decalage_images": decalage,
         "pivot_contrat": [round(x, 6) for x in pivot],
         "groupe_deformant": os_jaw,
         "sommets_pleinement_machoire": len(durs),
         "derive_radiale_mm": round(derive, 6),
         "course_machoire_mm": round(course, 4),
         "repere": "glTF Y-haut -> Blender Z-haut : (x, y, z) -> (x, -z, y)", "frames": frames, "temps": [round(t, 6) for t in temps],
         "actions_reveillees": reveilles, "info_runtime": info,
         "B_contre_A_mm": {str(k): v for k, v in ba.items()},
         "C_contre_B_mm": {str(k): v for k, v in cb.items()},
         "amplitude_max_mm": round(amp, 4), "registre": reg.bilan()}
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("RUNTIME", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
