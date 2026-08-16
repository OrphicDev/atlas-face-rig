"""F0-E.11 bis — la sonde de pivot attrape-t-elle la faute qu'elle a manquee ?

Le maillage runtime a ete exporte 1,46 m a cote de son propre rig, et AUCUNE
sonde ne l'a vu : elles comparaient toutes le meme montage fautif a lui-meme.
Ecrire une sonde apres coup ne prouve rien tant qu'on ne lui a pas remis la
faute sous les yeux. On la remet donc, exactement : `parent` sans matrice
d'inverse de parent.

Et le resultat est instructif. La sonde de pivot — « la distance au pivot du
contrat est-elle conservee ? » — reste AVEUGLE a cette faute, et c'est
geometriquement force : le modificateur d'armature ramene les os dans l'espace
local du maillage, si bien que le centre de rotation en monde reste le pivot,
quelle que soit la distance du maillage. Ce qui change, c'est le bras de
levier. Deux sondes voient donc la faute, et pas celle qu'on croyait :

  * la course de machoire, qui sort des bornes anatomiques ;
  * le pivot doit se trouver DANS la boite du maillage — le milieu des
    conduits auditifs est a l'interieur d'une tete, ou ce n'est pas sa tete.

    blender -b experiments/gltf-spike/spike.blend --python-exit-code 1 \
      --python tests/runtime-pivot-negatif.py -- \
      --motion config/jaw-motion.json \
      --report reports/f0-final/runtime-pivot-negatif.json
"""
import argparse, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
MM = 1000.0


def pivot_dans_la_boite(ob, pivot, marge=0.005):
    """Le milieu des conduits auditifs est A L'INTERIEUR d'une tete.

    C'est l'invariant que la sonde de pivot ne peut pas porter : une rotation
    autour d'un point reste une rotation autour de ce point, meme si le
    maillage est a un metre de la. La boite, elle, s'en apercoit.
    """
    coins = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = [min(p[i] for p in coins) - marge for i in range(3)]
    mx = [max(p[i] for p in coins) + marge for i in range(3)]
    return all(mn[i] <= pivot[i] <= mx[i] for i in range(3))


def derive_et_course(ob, pivot, os_jaw, f0, f1):
    gi = ob.vertex_groups[os_jaw].index
    durs = [v.index for v in ob.data.vertices
            if any(g.group == gi and g.weight >= 0.999 for g in v.groups)]
    P = {}
    for f in (f0, f1):
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = ob.evaluated_get(dg); me = ev.to_mesh(); M = ev.matrix_world
        P[f] = [(M @ me.vertices[i].co).copy() for i in durs]
        ev.to_mesh_clear()
    d = max(abs((P[f1][k] - pivot).length - (P[f0][k] - pivot).length) * MM
            for k in range(len(durs)))
    c = max((P[f1][k] - P[f0][k]).length for k in range(len(durs))) * MM
    return d, c, len(durs)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--motion", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--seuil", type=float, default=0.05)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    JM = json.load(open(Rp(o.motion), encoding="utf-8"))
    pivot = Vector(JM["pivot_world_xyz"])
    ob = bpy.data.objects["GEO_face_runtime"]
    rig = bpy.data.objects["TMP_F0_JAW_RIG"]
    f0, f1 = 1, 50
    reg = Registre("runtime-pivot-negatif")

    dans0 = pivot_dans_la_boite(ob, pivot)
    reg.exige("temoin.pivot_dans_la_boite",
              "le pivot du contrat est dans la boite du maillage sain",
              "boite monde du runtime", True, dans0, dans0)
    d0, c0, n = derive_et_course(ob, pivot, "TMP_jaw", f0, f1)
    reg.exige("temoin.sain", "le montage corrige tourne autour du pivot",
              "%d sommets pleinement machoire" % n, "<= %.2f mm" % o.seuil,
              round(d0, 6), d0 <= o.seuil, tolerance=o.seuil)

    # --- on remet la faute : parent sans matrice d'inverse de parent
    ob.parent = None
    ob.matrix_world = ob.matrix_world.copy()
    ob.parent = rig
    ob.matrix_parent_inverse.identity()
    bpy.context.view_layer.update()
    ecart = (ob.matrix_world.translation - rig.matrix_world.translation).length
    d1, c1, _ = derive_et_course(ob, pivot, "TMP_jaw", f0, f1)
    reg.exige("aveugle.pivot_ne_voit_pas",
              "la sonde de pivot est AVEUGLE au maillage decale, et c'est force",
              "decalage introduit %.4f m" % ecart,
              "derive toujours <= %.2f mm" % o.seuil, round(d1, 6),
              d1 <= o.seuil)
    reg.exige("refus.course_absurde",
              "la course de machoire devient hors bornes anatomiques",
              "meme decalage", "hors de [20 ; 90] mm", round(c1, 4),
              not (20.0 <= c1 <= 90.0))

    dans1 = pivot_dans_la_boite(ob, pivot)
    reg.exige("refus.pivot_hors_boite",
              "le pivot n'est plus dans la boite du maillage decale",
              "decalage %.4f m" % ecart, "hors boite", dans1, not dans1)

    R = {"pivot": [round(x, 6) for x in pivot], "images": [f0, f1],
         "sain": {"derive_mm": round(d0, 6), "course_mm": round(c0, 4),
                  "pivot_dans_la_boite": dans0},
         "fautif": {"decalage_m": round(ecart, 6), "derive_mm": round(d1, 6),
                    "course_mm": round(c1, 4), "pivot_dans_la_boite": dans1},
         "lecon": "la sonde de pivot est aveugle a un maillage decale : le "
                  "modificateur d'armature ramene les os dans l'espace local "
                  "du maillage, donc le centre de rotation en monde ne bouge "
                  "pas. Seuls le bras de levier et la boite le voient.",
         "registre": reg.bilan()}
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("PIVOT_NEGATIF", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
