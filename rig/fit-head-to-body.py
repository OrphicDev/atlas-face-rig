"""F0-D.3 — similarite tete -> corps, sur DUPLICATA uniquement.

Rotation, translation et echelle UNIFORME. Toute echelle non uniforme est
refusee : ce serait un cisaillement deguise.
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
import numpy as np
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre, exiger_asset
_s = importlib.util.spec_from_file_location("rc", os.path.join(RACINE, "tests", "f0-raccord-corps.py"))
rc = importlib.util.module_from_spec(_s); _s.loader.exec_module(rc)
MM = 1000.0

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--output", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    PAQUET, pf = exiger_asset()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = ["Head (Animation) - Realistic", "Body Male - Realistic"]
    for c in dst.collections: bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.update()
    tete = max([x for x in bpy.data.objects if x.name.startswith("GEO-head_animation_realistic")],
               key=lambda x: len(x.data.vertices))
    corps = max([x for x in bpy.data.objects if x.name.startswith("GEO-body_male_realistic")],
                key=lambda x: len(x.data.vertices))
    oT = {c: bpy.data.objects["GEO-head_animation_realistic.sclera." + c] for c in "LR"}
    oC = {c: bpy.data.objects["GEO-body_male_realistic.eye." + c] for c in "LR"}
    reg = Registre("fit-head-to-body")
    rt = rc.reperes_anatomiques(tete, oT["L"], oT["R"], "tete", reg)
    rcp = rc.reperes_anatomiques(corps, oC["L"], oC["R"], "corps", reg)
    pt, pc = rt.pop("_pts"), rcp.pop("_pts")
    cles = [k for k in ("oeil_L", "oeil_R", "nez", "menton")
            if pt.get(k) is not None and pc.get(k) is not None]
    Rm, t, s, res = rc.umeyama([list(pt[k]) for k in cles], [list(pc[k]) for k in cles])
    M = [[float(Rm[i][j]) * s for j in range(3)] + [float(t[i])] for i in range(3)] + \
        [[0.0, 0.0, 0.0, 1.0]]
    sx = np.linalg.norm(np.array(M)[:3, 0]); sy = np.linalg.norm(np.array(M)[:3, 1])
    sz = np.linalg.norm(np.array(M)[:3, 2])
    reg.exige("fit.echelle_uniforme_xy", "echelle uniforme", "similarite", 0.0,
              round(abs(sx - sy), 9), abs(sx - sy) <= 1e-6, tolerance=1e-6)
    reg.exige("fit.echelle_uniforme_yz", "echelle uniforme", "similarite", 0.0,
              round(abs(sy - sz), 9), abs(sy - sz) <= 1e-6, tolerance=1e-6)
    tri = sorted(float(x) * MM for x in res)
    R = {"preflight": pf, "landmarks": cles,
         "M_head_to_body": [[round(x, 9) for x in l] for l in M],
         "echelle_uniforme": round(float(s), 9),
         "ecart_a_1_pct": round(abs(float(s) - 1.0) * 100, 6),
         "residu_mm": {"p50": round(tri[len(tri) // 2], 4), "p95": round(tri[-1], 4),
                       "max": round(tri[-1], 4),
                       "par_repere": {k: round(float(res[i]) * MM, 4) for i, k in enumerate(cles)}},
         "sha_tete": rt["objet"], "sha_corps": rcp["objet"],
         "reperes": {"tete": rt, "corps": rcp}, "registre": reg.bilan()}
    p = Rp(o.output); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("FIT echelle %.6f (ecart %.5f %%) residu max %.4f mm" %
          (s, R["ecart_a_1_pct"], R["residu_mm"]["max"]))
    sys.exit(0 if ok else 2)
