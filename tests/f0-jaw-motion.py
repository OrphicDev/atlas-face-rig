"""F0-C.8 — mesure de la mandibule sur cinq angles."""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location("bp", os.path.join(RACINE, "rig", "build-f0-jaw-prototype.py"))
bp = importlib.util.module_from_spec(_s); _s.loader.exec_module(bp)
MM = 1000.0; TETE = "GEO-head_animation_realistic"

a = argparse.ArgumentParser()
for f in ("--input", "--mask", "--motion", "--output"): a.add_argument(f, required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
tete = bpy.data.objects[TETE]; me = tete.data; M = tete.matrix_world
basis = [v.co.copy() for v in me.vertices]; W = [M @ c for c in basis]
import numpy as np
poids = np.load(Rp(o.mask)).astype(float).tolist()
J = json.load(open(Rp(o.motion), encoding="utf-8"))
P = json.load(open(os.path.join(RACINE, "reports/f0-final/correspondances-marges.json"), encoding="utf-8"))
lab = P["ouvertures"]["fente_labiale"]
sup = [i for i in lab["chemin_upper"] if i not in set(lab["chemin_lower"])]
inf = [i for i in lab["chemin_lower"] if poids[i] >= 0.95]
rigides = [i for i in range(len(poids)) if poids[i] >= 0.999]
axe_x = (min(p.x for p in W) + max(p.x for p in W)) / 2
menton = min((i for i, p in enumerate(W) if abs(p.x - axe_x) < .02 and p.y < -.09),
             key=lambda i: W[i].z)
crane = [i for i, p in enumerate(W) if p.z > J["z_levre"] + .05]
cou = [i for i, p in enumerate(W) if p.z < J["z_bas_cou"] - .005]
ar = [(e.vertices[0], e.vertices[1]) for e in me.edges]
L0 = [(basis[x] - basis[y]).length for x, y in ar]
reg = Registre("f0-jaw-motion"); R = {"angles": {}}
prev = None
for deg in bp.ANGLES:
    Wp = bp.pose(W, poids, J, deg)
    # Le jour CENTRAL, pas la largeur de la bouche. Premiere version : elle
    # prenait le maximum sur TOUS les couples haut/bas et rendait 47 mm au
    # NEUTRE — c'etait la distance commissure a commissure.
    c_sup = min(sup, key=lambda i: abs(W[i].x - axe_x))
    c_inf = min(inf, key=lambda i: abs(W[i].x - axe_x))
    gap = (Wp[c_sup] - Wp[c_inf]).length * MM
    dep_inf = sorted((Wp[i] - W[i]).length * MM for i in inf)[len(inf) // 2]
    dep_sup = max((Wp[i] - W[i]).length * MM for i in sup)
    dep_crane = max((Wp[i] - W[i]).length * MM for i in crane)
    dep_cou = max((Wp[i] - W[i]).length * MM for i in cou)
    r = [(Wp[x] - Wp[y]).length / l for (x, y), l in zip(ar, L0) if l > 1e-9]
    R["angles"]["%g" % deg] = {"gap_central_mm": round(gap, 4),
        "deplacement_median_marge_inf_mm": round(dep_inf, 4),
        "deplacement_max_levre_sup_mm": round(dep_sup, 6),
        "deplacement_max_crane_mm": round(dep_crane, 6),
        "deplacement_max_cou_mm": round(dep_cou, 6),
        "menton_mm": [round(x, 4) for x in (Wp[menton] - W[menton]) * MM],
        "arete_min": round(min(r), 5), "arete_max": round(max(r), 5)}
    if deg == 0:
        e = max((Wp[i] - W[i]).length * MM for i in range(len(W)))
        reg.exige("jaw.zero_est_le_neutre", "0 degre rend exactement le neutre",
                  "cinq angles", "<= 0,01 mm", round(e, 6), e <= 0.01, tolerance=0.01)
    else:
        reg.exige("jaw.gap_croissant_%g" % deg, "le jour augmente strictement",
                  "angle precedent %g" % prev[0], "> %.4f mm" % prev[1],
                  round(gap, 4), gap > prev[1])
    prev = (deg, gap)
f = R["angles"]["32"]
reg.exige("jaw.gap_32", "jour central a 32 degres", "cinq angles", ">= 8 mm",
          f["gap_central_mm"], f["gap_central_mm"] >= 8.0)
reg.exige("jaw.marge_inf_32", "la marge inferieure se deplace", "32 degres",
          ">= 10 mm", f["deplacement_median_marge_inf_mm"],
          f["deplacement_median_marge_inf_mm"] >= 10.0)
reg.exige("jaw.crane_fixe", "le crane reste fixe", "32 degres", "<= 0,01 mm",
          f["deplacement_max_crane_mm"], f["deplacement_max_crane_mm"] <= 0.01)
reg.exige("jaw.levre_sup_fixe", "la levre superieure reste fixe", "32 degres",
          "<= 0,01 mm", f["deplacement_max_levre_sup_mm"],
          f["deplacement_max_levre_sup_mm"] <= 0.01)
reg.exige("jaw.cou_fixe", "le bas du cou reste fixe", "32 degres", "<= 0,5 mm",
          f["deplacement_max_cou_mm"], f["deplacement_max_cou_mm"] <= 0.5)
R["registre"] = reg.bilan()
s = Rp(o.output); os.makedirs(os.path.dirname(s) or ".", exist_ok=True)
json.dump(R, open(s, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ok = reg.conclure(); print("JAW_MOTION", "OK" if ok else "SEUILS NON SATISFAITS")
sys.exit(0 if ok else 2)
