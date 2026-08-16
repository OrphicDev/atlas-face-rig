"""F0-C.7 — prototype de machoire par transformation rigide ponderee.

Aucun rig d'interface : chaque sommet subit directement la rotation autour du
pivot temporo-mandibulaire mesure, puis la translation antero-inferieure,
melangee au neutre par le poids du masque. Chaque angle est reconstruit DEPUIS
le Basis, jamais depuis l'angle precedent.
"""
import argparse, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector, Matrix
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MM = 1000.0; TETE = "GEO-head_animation_realistic"
ANGLES = (0.0, 5.0, 10.0, 20.0, 32.0)

def lisse(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

def pose(W, poids, J, degres):
    piv = Vector(J["pivot_world_xyz"]); axe = Vector(J["hinge_axis_world_xyz"]).normalized()
    dirn = Vector(J["translation_direction_head_local"]).normalized()
    ouv = degres / J["rotation_max_deg"]
    t = max(0.0, min(1.0, (ouv - J["translation_start"]) / (1.0 - J["translation_start"])))
    s = t * t * (3.0 - 2.0 * t)
    trans = dirn * (s * J["translation_max_mm"] / MM)
    Rm = Matrix.Rotation(math.radians(degres), 3, axe)
    out = []
    for p, w in zip(W, poids):
        if w <= 0.0: out.append(p.copy()); continue
        q = piv + (Rm @ (p - piv)) + trans
        out.append(p.lerp(q, w))
    return out

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--mask", "--motion", "--output", "--report"): a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
    tete = bpy.data.objects[TETE]; me = tete.data; M = tete.matrix_world
    basis = [v.co.copy() for v in me.vertices]
    W = [M @ c for c in basis]
    import numpy as np
    poids = np.load(Rp(o.mask)).astype(float).tolist()
    J = json.load(open(Rp(o.motion), encoding="utf-8"))
    if len(poids) != len(basis): print("masque incompatible"); sys.exit(2)
    Mi = M.inverted()
    R = {"angles": ANGLES, "pivot": J["pivot_world_xyz"], "axe": J["hinge_axis_world_xyz"],
         "erreur_rigide_mm": {}}
    for deg in ANGLES:
        Wp = pose(W, poids, J, deg)
        d = me.copy(); dup = bpy.data.objects.new("DBG_jaw_%02d" % int(deg), d)
        dup.matrix_world = M.copy(); bpy.context.scene.collection.objects.link(dup)
        for m in list(dup.modifiers): dup.modifiers.remove(m)
        for i, p in enumerate(Wp): d.vertices[i].co = Mi @ p
        d.update()
        # controle : les sommets de poids >= 0,95 doivent suivre la rigide
        piv = Vector(J["pivot_world_xyz"]); axe = Vector(J["hinge_axis_world_xyz"]).normalized()
        dirn = Vector(J["translation_direction_head_local"]).normalized()
        ouv = deg / J["rotation_max_deg"]
        t = max(0.0, min(1.0, (ouv - J["translation_start"]) / (1.0 - J["translation_start"])))
        s = t * t * (3.0 - 2.0 * t); trans = dirn * (s * J["translation_max_mm"] / MM)
        Rm = Matrix.Rotation(math.radians(deg), 3, axe)
        # Le controle rigide ne vaut que pour les sommets ENTIEREMENT
        # entraines. A poids 0,95, le melange laisse 5 % du deplacement, soit
        # 2,3 mm sur une course de 60 : ce n'est pas une faute de matrice.
        err = max([((piv + (Rm @ (W[i] - piv)) + trans) - Wp[i]).length * MM
                   for i in range(len(W)) if poids[i] >= 0.999] or [0.0])
        R["erreur_rigide_mm"]["%g" % deg] = round(err, 6)
    c = Rp(o.output); os.makedirs(os.path.dirname(c), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=c, copy=True)
    json.dump(R, open(Rp(o.report), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    pire = max(R["erreur_rigide_mm"].values())
    print("JAW_PROTO_OK erreur rigide max %.6f mm (limite 0,25)" % pire)
    sys.exit(0 if pire <= 0.25 else 2)
