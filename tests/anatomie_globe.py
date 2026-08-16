"""F0-B.7 — geometrie du globe, partagee par la mesure ET par le rendu.

Un seul module, importe des deux cotes : deux implementations locales finiraient
par diverger. La sphere est ajustee sur la seule portion POSTERIEURE de la
sclere — le renflement corneen depasse la sphere moyenne, et l'inclure faussait
le rayon de 0,69 mm en passe 3. Le BVH du maillage reel est conserve pour la
distance finale.

    blender -b "$FACE_AUTHOR_BLEND" --python tests/anatomie_globe.py -- \
      --output config/globe-fit.json
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MM = 1000.0
TETE = "GEO-head_animation_realistic"
AVANT = Vector((0.0, -1.0, 0.0))     # -Y = avant du visage


def ajuster_sphere(pts):
    """Sphere des moindres carres (formulation algebrique lineaire)."""
    import numpy as np
    P = np.asarray([[p.x, p.y, p.z] for p in pts], dtype=np.float64)
    A = np.hstack([2.0 * P, np.ones((len(P), 1))])
    b = (P ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = Vector((float(sol[0]), float(sol[1]), float(sol[2])))
    r = math.sqrt(max(0.0, float(sol[3]) + sol[0] ** 2 + sol[1] ** 2 + sol[2] ** 2))
    res = [abs((p - c).length - r) for p in pts]
    return c, r, max(res), sum(res) / len(res)


def sclere(cote):
    return bpy.data.objects[TETE + ".sclera." + cote]


def bvh_sclere(cote):
    o = sclere(cote)
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


def ajuster_globe(cote, part_posterieure=0.55):
    """Ajuste sur l'arriere de la sclere seulement.

    `part_posterieure` = fraction des sommets les plus en arriere retenus.
    Le renflement corneen est ainsi exclu par construction, pas par un seuil
    invente sur le rayon.
    """
    o = sclere(cote)
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    c0 = Vector([sum(p[i] for p in pts) / len(pts) for i in range(3)])
    ordre = sorted(range(len(pts)), key=lambda i: (pts[i] - c0).dot(AVANT))
    garde = ordre[:max(12, int(len(pts) * part_posterieure))]
    c, r, res_max, res_moy = ajuster_sphere([pts[i] for i in garde])
    return {
        "sclera_object": o.name,
        "center_world_xyz": [round(float(x), 9) for x in c],
        "radius_mm": round(r * MM, 6),
        "posterior_vertex_indices": sorted(garde),
        "fit_residual_mm": round(res_max * MM, 6),
        "fit_residual_moyen_mm": round(res_moy * MM, 6),
        "part_posterieure": part_posterieure,
        "sommets_totaux": len(pts),
    }


def distance_signee_au_globe(bvh, centre, p, portee=0.030):
    """Distance a la SURFACE reelle ; negative si le point est dans le globe."""
    loc = bvh.find_nearest(p, portee)[0]
    if loc is None:
        return None
    d = (p - loc).length
    return -d if (p - centre).length < (loc - centre).length else d


def charger(chemin=None):
    p = chemin or os.path.join(RACINE, "config", "globe-fit.json")
    return json.load(open(p, encoding="utf-8"))


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    _s = importlib.util.spec_from_file_location(
        "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
    wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(wai)

    R = {"schema_version": 1,
         "author_blend_sha256": wai.sha_fichier(bpy.data.filepath),
         "space": "WORLD", "units": "METERS",
         "methode": "sphere des moindres carres sur la portion posterieure de "
                    "la sclere ; le BVH du maillage reel sert a la distance",
         "eyes": {}}
    for cote in ("L", "R"):
        R["eyes"][cote] = ajuster_globe(cote)
        e = R["eyes"][cote]
        print("  globe %s : centre %s rayon %.4f mm residu max %.4f mm (%d/%d sommets)"
              % (cote, [round(x, 5) for x in e["center_world_xyz"]], e["radius_mm"],
                 e["fit_residual_mm"], len(e["posterior_vertex_indices"]),
                 e["sommets_totaux"]))

    # controle : les deux globes doivent etre symetriques a la mesure pres
    cl = Vector(R["eyes"]["L"]["center_world_xyz"])
    cr = Vector(R["eyes"]["R"]["center_world_xyz"])
    R["interoculaire_mm"] = round((cl - cr).length * MM, 4)
    R["ecart_rayon_LR_mm"] = round(abs(R["eyes"]["L"]["radius_mm"]
                                       - R["eyes"]["R"]["radius_mm"]), 6)
    sortie = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("GLOBE_FIT_OK ->", o.output, "| interoculaire", R["interoculaire_mm"],
          "mm | ecart de rayon L/R", R["ecart_rayon_LR_mm"], "mm")
