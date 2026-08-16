"""F0-B.6 bis — carte miroir d'indices, propagee sur la connectivite.

La distance a la position reflechie ne sert qu'a DEPARTAGER deux candidats
topologiquement equivalents. La carte est refusee si elle est partielle, non
bijective, non involutive, si une arete ne devient pas une arete ou si une face
n'a pas d'homologue.

    blender -b "$FACE_AUTHOR_BLEND" --python-exit-code 1 \
      --python tools/build-mirror-map.py -- \
      --object GEO-head_animation_realistic \
      --landmarks config/mirror-landmarks.json \
      --output reports/f0-final/carte-miroir.json \
      --debug-blend experiments/f0-contacts/FACE_F0_MIRROR_MAP.blend
"""
import argparse, hashlib, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector, kdtree

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
_wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(_wai)
MM = 1000.0


def plan_sagittal(co):
    """Plan x = c qui minimise l'erreur miroir au plus proche voisin."""
    kd = kdtree.KDTree(len(co))
    for i, p in enumerate(co): kd.insert(p, i)
    kd.balance()
    meilleur, score = 0.0, None
    for k in range(-20, 21):
        c = k * 1e-4
        s = sum(kd.find(Vector((2 * c - p.x, p.y, p.z)))[2] for p in co)
        if score is None or s < score:
            meilleur, score = c, s
    return meilleur


def propager(me, co, plan, graines, midline):
    """Appariement par propagation sur les aretes, depuis des couples surs."""
    n = len(co)
    adj = [[] for _ in range(n)]
    for e in me.edges:
        a, b = e.vertices
        adj[a].append(b); adj[b].append(a)
    mir = lambda p: Vector((2 * plan - p.x, p.y, p.z))
    carte = [-1] * n
    for i in midline:
        carte[i] = i
    file = []
    for a, b in graines:
        if carte[a] not in (-1, b) or carte[b] not in (-1, a):
            return None, {"echec": "graines contradictoires", "couple": [a, b]}
        carte[a], carte[b] = b, a
        file += [a, b]
    ecarts = []
    while file:
        i = file.pop()
        j = carte[i]
        vi, vj = adj[i], adj[j]
        if len(vi) != len(vj):
            return None, {"echec": "valences differentes", "sommet": i, "miroir": j}
        libres = list(vj)
        for x in vi:
            if not libres: break
            cible = mir(co[x])
            y = min(libres, key=lambda z: (co[z] - cible).length)
            ecarts.append((co[y] - cible).length)
            libres.remove(y)
            if carte[x] == -1:
                carte[x], carte[y] = y, x
                file.append(x)
                if y != x: file.append(y)
            elif carte[x] != y:
                return None, {"echec": "appariement contradictoire",
                              "sommet": x, "deja": carte[x], "propose": y}
    if -1 in carte:
        return None, {"echec": "carte partielle", "non_apparies": carte.count(-1)}
    return carte, {"ecart_propagation_max_mm": round(max(ecarts) * MM, 6)}


def verifier(me, carte):
    ar = {tuple(sorted(e.vertices)) for e in me.edges}
    fa = {tuple(sorted(p.vertices)) for p in me.polygons}
    return {
        "bijection": sorted(carte) == list(range(len(carte))),
        "involutive": all(carte[carte[i]] == i for i in range(len(carte))),
        "aretes_sans_image": sum(
            1 for a in ar if tuple(sorted((carte[a[0]], carte[a[1]]))) not in ar),
        "faces_sans_image": sum(
            1 for f in fa if tuple(sorted(carte[i] for i in f)) not in fa),
        "sommets_sur_l_axe": sum(1 for i in range(len(carte)) if carte[i] == i),
    }


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--object", required=True)
    a.add_argument("--landmarks", required=True)
    a.add_argument("--output", required=True)
    a.add_argument("--debug-blend")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])

    obj = bpy.data.objects[o.object]
    me = obj.data
    co = [v.co.copy() for v in me.vertices]
    plan = plan_sagittal(co)

    p_lm = o.landmarks if os.path.isabs(o.landmarks) else os.path.join(RACINE, o.landmarks)
    L = json.load(open(p_lm, encoding="utf-8"))
    graines = [tuple(c) for c in L["seed_pairs"]]
    midline = list(L["midline_fixed"])

    carte, info = propager(me, co, plan, graines, midline)
    if carte is None:
        print("ECHEC DE LA CARTE :", info); sys.exit(2)
    v = verifier(me, carte)
    err = [(Vector((2 * plan - co[carte[i]].x, co[carte[i]].y, co[carte[i]].z))
            - co[i]).length * MM for i in range(len(co))]
    err_tri = sorted(err)

    R = {"mesh": o.object,
         "author_blend_sha256": _wai.sha_fichier(bpy.data.filepath),
         "topology_sha256": _wai.sha_topologie(obj),
         "sagittal_plane_object_local": round(plan, 9),
         "mirror_indices": carte,
         "midline_fixed": sorted(i for i in range(len(carte)) if carte[i] == i),
         "seed_pairs": [list(g) for g in graines],
         "method": "propagation sur les aretes depuis des couples surs ; la "
                   "distance a l'image reflechie ne departage que des candidats "
                   "topologiquement equivalents",
         "propagation": info,
         "verification": v,
         "residu_geometrique_mm": {
             "max": round(max(err), 6), "median": round(err_tri[len(err) // 2], 6),
             "p99": round(err_tri[int(len(err) * 0.99)], 6)},
         }
    R["semantic_sha256"] = hashlib.sha256(json.dumps(
        {k: R[k] for k in ("mesh", "topology_sha256", "sagittal_plane_object_local",
                           "mirror_indices", "midline_fixed")},
        sort_keys=True).encode()).hexdigest()

    ok = (v["bijection"] and v["involutive"]
          and v["aretes_sans_image"] == 0 and v["faces_sans_image"] == 0)
    R["status"] = "PASS" if ok else "FAIL"

    if o.debug_blend and ok:
        d = me.copy(); dup = bpy.data.objects.new("DBG_MIROIR", d)
        bpy.context.scene.collection.objects.link(dup)
        for m in list(dup.modifiers): dup.modifiers.remove(m)
        g_ax = dup.vertex_groups.new(name="DBG_midline")
        g_ax.add(R["midline_fixed"], 1.0, "REPLACE")
        g_g = dup.vertex_groups.new(name="DBG_gauche")
        g_g.add([i for i in range(len(carte)) if co[i].x > plan], 1.0, "REPLACE")
        chemin = o.debug_blend if os.path.isabs(o.debug_blend) \
            else os.path.join(RACINE, o.debug_blend)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=chemin, copy=True)

    sortie = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("MIROIR", R["status"], json.dumps(v), "| residu median",
          R["residu_geometrique_mm"]["median"], "mm")
    sys.exit(0 if ok else 2)
