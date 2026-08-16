"""F0-C.2 et C.3 — masque mandibulaire par diffusion GEODESIQUE.

Les graines ne sont pas devinees a l'oeil ni prises par un seuil Z : elles sont
derivees des reperes DEJA audites — bord labial inferieur, conduits auditifs,
pointe du nez — puis diffusees sur le graphe des aretes.
"""
import argparse, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
MM = 1000.0; TETE = "GEO-head_animation_realistic"

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
    for f in ("--input", "--config", "--output", "--report"): a.add_argument(f, required=True)
    a.add_argument("--debug-blend")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
    tete = bpy.data.objects[TETE]; me = tete.data; M = tete.matrix_world
    co = [v.co.copy() for v in me.vertices]
    W = [M @ c for c in co]
    A = json.load(open(os.path.join(RACINE, "reports/f0/audit-topologie.json"), encoding="utf-8"))
    P = json.load(open(os.path.join(RACINE, "reports/f0-final/correspondances-marges.json"), encoding="utf-8"))
    ouv = {x["nom"]: x for x in A["ouvertures"] if x.get("nom")}
    lab = P["ouvertures"]["fente_labiale"]
    z_levre = sum(W[i].z for i in lab["chemin_upper"]) / len(lab["chemin_upper"])
    axe = (min(p.x for p in W) + max(p.x for p in W)) / 2
    z_menton = min(p.z for p in W if abs(p.x - axe) < .020 and p.y < -.09)
    z_bas = min(p.z for p in W)
    oreilles = [Vector(ouv["conduit_auditif." + c]["centre"]) for c in "LR"]

    seed_lip = sorted(lab["chemin_lower"])
    seed_chin = sorted(i for i, p in enumerate(W)
                       if abs(p.x - axe) < .018 and p.y < -.10
                       and z_menton <= p.z <= z_levre - .006)
    seed_mand = sorted(i for i, p in enumerate(W)
                       if abs(p.x - axe) > .030 and p.y < -.02
                       and z_menton - .004 <= p.z <= z_levre - .012)
    # Les commissures appartiennent aux DEUX arcs : elles ne peuvent etre ni
    # graine mandibulaire ni exclusion cranienne. On les retire des deux et la
    # diffusion leur donne le poids intermediaire qui leur revient.
    partages = set(lab["chemin_upper"]) & set(lab["chemin_lower"])
    seed_lip = [i for i in seed_lip if i not in partages]
    excl = sorted((set(lab["chemin_upper"]) - partages) |
                  {i for i, p in enumerate(W) if p.z > z_levre + .004} |
                  {i for i, p in enumerate(W) if p.z < z_bas + .045})
    C = {"schema_version": 1, "mesh": TETE, "space": "WORLD",
         "z_levre": round(z_levre, 6), "z_menton": round(z_menton, 6),
         "z_bas_cou": round(z_bas + .045, 6),
         "conduits_auditifs": [[round(x, 6) for x in p] for p in oreilles],
         "DBG_jaw_seed_lower_lip": seed_lip, "DBG_jaw_seed_chin": seed_chin,
         "DBG_jaw_seed_mandible": seed_mand, "DBG_jaw_exclude_upper": excl}
    json.dump(C, open(Rp(o.config), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    reg = Registre("build-jaw-mask")
    inter = sorted(set(seed_lip) & set(excl))
    reg.exige("jaw.lip_vs_exclude", "aucune graine labiale dans l'exclusion",
              "reperes audites", [], inter, not inter)
    g = [i for i in seed_mand if W[i].x > axe]; d = [i for i in seed_mand if W[i].x < axe]
    reg.exige("jaw.mandibule_deux_cotes", "les deux cotes ont des graines",
              "reperes audites", "> 0 des deux", [len(g), len(d)], g and d)

    graines = sorted(set(seed_lip) | set(seed_chin) | set(seed_mand))
    portee = 0.070
    dist = geodesique(me, co, graines, portee)
    dist_x = geodesique(me, co, excl, portee)
    poids = []
    for i in range(len(co)):
        dj = dist.get(i); dx = dist_x.get(i)
        if i in excl: w = 0.0
        elif i in graines: w = 1.0
        elif dj is None: w = 0.0
        elif dx is None: w = 1.0 - lisse(dj / portee)
        else: w = max(0.0, min(1.0, dx / (dj + dx) if (dj + dx) > 1e-9 else 0.0))
        poids.append(w)
    for i in graines: poids[i] = 1.0
    for i in excl: poids[i] = 0.0

    import numpy as np
    arr = np.asarray(poids, dtype=np.float32)
    np.save(Rp(o.output), arr)
    reg.exige("jaw.bornes", "poids dans [0,1]", "tableau complet", True,
              bool((arr >= 0).all() and (arr <= 1).all()),
              bool((arr >= 0).all() and (arr <= 1).all()))
    ml = min(poids[i] for i in seed_lip)
    reg.exige("jaw.marge_inferieure", "la marge labiale inferieure est pleine",
              "graines", ">= 0,95", round(ml, 4), ml >= 0.95)
    # Les commissures sont exclues du critere : elles appartiennent aux deux
    # levres et ont un poids intermediaire par construction. L'enonce
    # anatomique porte sur la levre superieure PROPREMENT DITE.
    sup = [i for i in lab["chemin_upper"] if i not in partages]
    mu = max(poids[i] for i in sup)
    reg.exige("jaw.marge_superieure", "la levre superieure hors commissures est nulle",
              "exclusion, commissures otees", 0.0, round(mu, 6), mu == 0.0)
    mc = max(poids[i] for i in partages)
    reg.exige("jaw.commissures_intermediaires", "les commissures sont entre 0 et 1",
              "sommets partages par les deux arcs", "0 < w < 1", round(mc, 4),
              0.0 < mc < 1.0)
    crane = max(poids[i] for i, p in enumerate(W) if p.z > z_levre + .05)
    reg.exige("jaw.crane", "le crane ne bouge pas", "z au-dessus des levres",
              0.0, round(crane, 6), crane == 0.0)
    cou = max(poids[i] for i, p in enumerate(W) if p.z < z_bas + .030)
    reg.exige("jaw.bas_du_cou", "le bas du cou ne bouge pas", "z bas",
              0.0, round(cou, 6), cou == 0.0)

    R = {"sommets": len(poids), "graines": len(graines), "exclusions": len(excl),
         "portee_m": portee, "poids_moyen": round(float(arr.mean()), 6),
         "sommets_pleins": int((arr > 0.95).sum()), "sommets_nuls": int((arr == 0).sum()),
         "registre": reg.bilan()}
    json.dump(R, open(Rp(o.report), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if o.debug_blend:
        d2 = me.copy(); dup = bpy.data.objects.new("DBG_JAW_MASK", d2)
        dup.matrix_world = M.copy(); bpy.context.scene.collection.objects.link(dup)
        for m in list(dup.modifiers): dup.modifiers.remove(m)
        vg = dup.vertex_groups.new(name="DBG_jaw_weight")
        for i, w in enumerate(poids):
            if w > 0: vg.add([i], w, "REPLACE")
        c = Rp(o.debug_blend); os.makedirs(os.path.dirname(c), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=c, copy=True)
    ok = reg.conclure()
    print("JAW_MASK", "OK" if ok else "ECHEC", "| pleins", R["sommets_pleins"],
          "| nuls", R["sommets_nuls"])
    sys.exit(0 if ok else 2)
