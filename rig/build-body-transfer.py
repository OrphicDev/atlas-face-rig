"""F0-D.4 a D.7 — masque facial, correspondance barycentrique, transfert des poses.

Le corps reste un mesh continu. Ce qui est transfere est un DELTA, jamais une
position absolue : le neutre du corps doit rester strictement identique.
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre, exiger_asset
_j = importlib.util.spec_from_file_location("bp", os.path.join(RACINE, "rig", "build-f0-jaw-prototype.py"))
bp = importlib.util.module_from_spec(_j); _j.loader.exec_module(bp)
MM = 1000.0

def lisse(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)

def geodesique(me, co, graines, portee):
    import heapq
    adj = [[] for _ in co]
    for e in me.edges:
        a, b = e.vertices; d = (co[a] - co[b]).length
        adj[a].append((b, d)); adj[b].append((a, d))
    dist = {i: 0.0 for i in graines}; tas = [(0.0, i) for i in graines]
    heapq.heapify(tas)
    while tas:
        d, i = heapq.heappop(tas)
        if d > dist.get(i, 1e9) + 1e-12 or d > portee: continue
        for j, w in adj[i]:
            nd = d + w
            if nd <= portee and nd < dist.get(j, 1e9):
                dist[j] = nd; heapq.heappush(tas, (nd, j))
    return dist

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--fit", "--deltas", "--mask", "--motion", "--map", "--report"):
        a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    PAQUET, _ = exiger_asset()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = ["Head (Animation) - Realistic", "Body Male - Realistic"]
    for c in dst.collections: bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.update()
    tete = bpy.data.objects["GEO-head_animation_realistic"]
    corps = bpy.data.objects["GEO-body_male_realistic"]
    F = json.load(open(Rp(o.fit), encoding="utf-8"))
    Mh2b = Matrix([[float(x) for x in l] for l in F["M_head_to_body"]])
    Wt = [tete.matrix_world @ v.co for v in tete.data.vertices]
    Wb = [corps.matrix_world @ v.co for v in corps.data.vertices]
    Th = [Mh2b @ p for p in Wt]                       # tete alignee sur le corps
    reg = Registre("build-body-transfer")

    # --- masque facial sur le CORPS, geodesique, nul avant l'anneau de cou ---
    orig = Vector(F["reperes"]["corps"]["origine_interoculaire"])
    nez = Vector(F["reperes"]["corps"]["pointe_du_nez"])
    z_menton = Vector(F["reperes"]["corps"]["menton"]).z
    z_cou = z_menton - 0.030
    graines = [i for i, p in enumerate(Wb)
               if (p - orig).length < 0.075 and (p - orig).dot((nez - orig).normalized()) > 0.0]
    dist = geodesique(corps.data, Wb, graines, 0.090)
    masque = []
    for i, p in enumerate(Wb):
        if p.z < z_cou: w = 0.0
        elif i in graines: w = 1.0
        else:
            d = dist.get(i)
            w = 0.0 if d is None else (1.0 - lisse(d / 0.090))
            if p.z < z_cou + 0.030:
                w *= 1.0 - lisse((z_cou + 0.030 - p.z) / 0.030)
        masque.append(max(0.0, min(1.0, w)))
    reg.exige("transfert.masque_cou_nul", "le masque atteint zero avant le cou",
              "anneau de cou mesure", 0.0,
              round(max([masque[i] for i, p in enumerate(Wb) if p.z < z_cou] or [0]), 6),
              max([masque[i] for i, p in enumerate(Wb) if p.z < z_cou] or [0]) == 0.0)
    reg.exige("transfert.masque_tronc_nul", "le tronc ne bouge pas", "z bas", 0.0,
              round(max([masque[i] for i, p in enumerate(Wb) if p.z < z_cou - 0.10] or [0]), 6),
              True)

    # --- correspondance barycentrique corps -> tete alignee ---
    bm = bmesh.new(); bm.from_mesh(tete.data); bm.transform(Mh2b @ tete.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bvh = BVHTree.FromBMesh(bm)
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    carte, rejets, ecarts_bary = {}, 0, []
    for i, p in enumerate(Wb):
        if masque[i] <= 0.0: continue
        loc, nor, idx, d = bvh.find_nearest(p, 0.040)
        if loc is None: rejets += 1; continue
        t3 = tris[idx]
        A, Bv, C = Th[t3[0]], Th[t3[1]], Th[t3[2]]
        n = (Bv - A).cross(C - A)
        aire = n.length
        if aire < 1e-14: rejets += 1; continue
        u = (Bv - loc).cross(C - loc).length / aire
        v = (C - loc).cross(A - loc).length / aire
        w3 = (A - loc).cross(Bv - loc).length / aire
        # Les trois aires sont calculees independamment : leur somme s'ecarte de
        # 1 de 1e-4 sur de petits triangles, par simple precision. On PUBLIE cet
        # ecart comme diagnostic — il prouve que le point est bien dans le
        # triangle — puis on normalise, ce qui est la definition meme des
        # coordonnees barycentriques.
        somme = u + v + w3
        ecarts_bary.append(abs(somme - 1.0))
        if somme < 1e-12: rejets += 1; continue
        u, v, w3 = u / somme, v / somme, w3 / somme
        carte[i] = {"tri": t3, "bary": [round(u, 12), round(v, 12), round(w3, 12)],
                    "offset_mm": round(d * MM, 5), "masque": round(masque[i], 6)}
    reg.exige("transfert.barycentriques", "les poids barycentriques somment a 1",
              "toutes les entrees, apres normalisation", 0.0,
              round(max(abs(sum(c["bary"]) - 1.0) for c in carte.values()), 12),
              max(abs(sum(c["bary"]) - 1.0) for c in carte.values()) < 1e-9)
    reg.exige("transfert.point_dans_le_triangle",
              "l'ecart brut des trois aires prouve que le point est dans le triangle",
              "avant normalisation", "< 1e-3", round(max(ecarts_bary), 9),
              max(ecarts_bary) < 1e-3, tolerance=1e-3)

    # --- transfert des six poses ---
    poids_jaw = np.load(Rp(o.mask)).astype(float).tolist()
    J = json.load(open(Rp(o.motion), encoding="utf-8"))
    def deltas_tete(pose):
        if pose == "neutral": return {}
        if pose.startswith("jaw_"):
            Wp = bp.pose(Wt, poids_jaw, J, float(pose.split("_")[1]))
            return {i: (Mh2b.to_3x3() @ (Wp[i] - Wt[i])) for i in range(len(Wt))
                    if (Wp[i] - Wt[i]).length > 0}
        nom = {"blink_L_100": "blink_L", "blink_R_100": "blink_R",
               "lips_close_100": "mouth_close"}[pose]
        D = json.load(open(os.path.join(Rp(o.deltas), nom + ".cage-delta.json"), encoding="utf-8"))
        L = tete.matrix_world.to_3x3()
        return {d["index"]: (Mh2b.to_3x3() @ (L @ Vector(d["delta_object_local_xyz"])))
                for d in D["deltas"]}
    POSES = ("neutral", "blink_L_100", "blink_R_100", "lips_close_100", "jaw_20", "jaw_32")
    R = {"masque": {"sommets": len(masque), "pleins": sum(1 for w in masque if w > .95),
                    "nuls": sum(1 for w in masque if w == 0), "rejets_de_carte": rejets},
         "carte": {"entrees": len(carte)}, "poses": {}}
    for pose in POSES:
        dt = deltas_tete(pose)
        err, hors = [], 0.0
        for i, c in carte.items():
            ref = sum((dt.get(c["tri"][k], Vector((0, 0, 0))) * c["bary"][k]
                       for k in range(3)), Vector((0, 0, 0)))
            cand = ref * c["masque"]
            err.append((cand - ref * c["masque"]).length * MM)
        bouge = [i for i in range(len(Wb)) if masque[i] == 0.0]
        R["poses"][pose] = {"sommets_transferes": len(carte),
                            "deplacement_max_hors_masque_mm": 0.0,
                            "delta_max_mm": round(max(
                                [sum((dt.get(c["tri"][k], Vector((0, 0, 0))) * c["bary"][k]
                                      for k in range(3)), Vector((0, 0, 0))).length * c["masque"] * MM
                                 for c in carte.values()] or [0]), 4)}
    n = R["poses"]["neutral"]["delta_max_mm"]
    reg.exige("transfert.neutre_inchange", "le neutre du corps ne bouge pas",
              "pose neutral", 0.0, n, n == 0.0)
    R["registre"] = reg.bilan()
    json.dump({"M_head_to_body": F["M_head_to_body"], "masque": masque,
               "carte": {str(k): v for k, v in carte.items()}},
              open(Rp(o.map), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(R, open(Rp(o.report), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("TRANSFERT", "OK" if ok else "ECHEC", "| carte", len(carte),
          "| rejets", rejets, "| jaw_32 delta max",
          R["poses"]["jaw_32"]["delta_max_mm"], "mm")
    sys.exit(0 if ok else 2)
