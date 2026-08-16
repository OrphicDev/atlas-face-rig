"""F0-E.11 — un runtime glTF ecrit ici, qui ne lit QUE le fichier.

Le but n'est pas d'ecrire un moteur : c'est de prouver que le GLB se suffit a
lui-meme. Si une implementation independante de la specification, qui n'a
jamais vu Blender ni le blend d'origine, reproduit la deformation au micron,
alors le fichier porte bien tout ce qu'un runtime doit y trouver.

Aucune dependance : ni numpy, ni Blender, ni bibliotheque graphique.

    python3 tools/runtime_eval.py --input exports/atlas-face-spike.glb \
      --times 0 0.375 --output /tmp/poses.json
"""
import argparse, json, math, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tools"))
import importlib.util as _u
_s = _u.spec_from_file_location("vg", os.path.join(RACINE, "tools", "validate_glb.py"))
VG = _u.module_from_spec(_s); _s.loader.exec_module(VG)


# ------------------------------------------------------------- algebre ------
def identite():
    return [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


def mul(a, b):
    """Produit de deux 4x4 stockees en ligne (row-major), a puis b."""
    o = [0.0] * 16
    for i in range(4):
        for j in range(4):
            o[i * 4 + j] = sum(a[i * 4 + k] * b[k * 4 + j] for k in range(4))
    return o


def de_trs(t, q, s):
    """glTF : M = T * R * S, quaternion (x, y, z, w)."""
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    R = [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
         2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
         2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]
    M = identite()
    for i in range(3):
        for j in range(3):
            M[i * 4 + j] = R[i * 3 + j] * s[j]
        M[i * 4 + 3] = t[i]
    return M


def colonne_vers_ligne(m):
    """glTF stocke les matrices en COLONNES ; on travaille en lignes."""
    return [m[j * 4 + i] for i in range(4) for j in range(4)]


def applique(M, p):
    return [M[0] * p[0] + M[1] * p[1] + M[2] * p[2] + M[3],
            M[4] * p[0] + M[5] * p[1] + M[6] * p[2] + M[7],
            M[8] * p[0] + M[9] * p[1] + M[10] * p[2] + M[11]]


def slerp(a, b, u):
    d = sum(a[i] * b[i] for i in range(4))
    if d < 0:
        b = [-x for x in b]; d = -d
    if d > 0.9995:
        r = [a[i] + u * (b[i] - a[i]) for i in range(4)]
    else:
        th = math.acos(max(-1.0, min(1.0, d)))
        st = math.sin(th)
        r = [(math.sin((1 - u) * th) * a[i] + math.sin(u * th) * b[i]) / st
             for i in range(4)]
    n = math.sqrt(sum(x * x for x in r)) or 1.0
    return [x / n for x in r]


# ------------------------------------------------------------ animation -----
def echantillonner(J, BIN, cache, sp, t, n_sortie):
    """Valeur d'un echantillonneur au temps t, les trois interpolations."""
    ent = cache.setdefault(("in", sp["input"]),
                           [v[0] for v in VG.decoder(J, BIN, sp["input"])])
    sor = cache.setdefault(("out", sp["output"]), VG.decoder(J, BIN, sp["output"]))
    mode = sp.get("interpolation", "LINEAR")
    plat = [x for v in sor for x in v]
    m = n_sortie
    if not ent:
        return [0.0] * m
    if t <= ent[0]:
        k, u = 0, 0.0
    elif t >= ent[-1]:
        k, u = len(ent) - 2 if len(ent) > 1 else 0, 1.0
    else:
        k = max(i for i in range(len(ent) - 1) if ent[i] <= t)
        u = (t - ent[k]) / (ent[k + 1] - ent[k])
    if mode == "CUBICSPLINE":
        dt = (ent[min(k + 1, len(ent) - 1)] - ent[k]) or 1.0
        v0 = plat[(3 * k + 1) * m:(3 * k + 2) * m]
        b0 = plat[(3 * k + 2) * m:(3 * k + 3) * m]
        v1 = plat[(3 * (k + 1) + 1) * m:(3 * (k + 1) + 2) * m]
        a1 = plat[(3 * (k + 1)) * m:(3 * (k + 1) + 1) * m]
        u2, u3 = u * u, u * u * u
        return [(2 * u3 - 3 * u2 + 1) * v0[i] + dt * (u3 - 2 * u2 + u) * b0[i]
                + (-2 * u3 + 3 * u2) * v1[i] + dt * (u3 - u2) * a1[i]
                for i in range(m)]
    A = plat[k * m:(k + 1) * m]
    B = plat[min(k + 1, len(ent) - 1) * m:(min(k + 1, len(ent) - 1) + 1) * m]
    if mode == "STEP" or u == 0.0:
        return list(A)
    if m == 4 and len(A) == 4 and abs(sum(x * x for x in A) - 1.0) < 1e-2:
        return slerp(A, B, u)                       # rotation : SLERP, pas lerp
    return [A[i] + u * (B[i] - A[i]) for i in range(m)]


def poser(J, BIN, cache, t):
    """TRS de chaque noeud et poids de morph, au temps t."""
    trs = []
    for nd in J.get("nodes", []):
        trs.append({"t": list(nd.get("translation", [0, 0, 0])),
                    "r": list(nd.get("rotation", [0, 0, 0, 1])),
                    "s": list(nd.get("scale", [1, 1, 1])),
                    "m": nd.get("matrix"), "w": list(nd.get("weights", []))})
    for an in J.get("animations", []):
        for ch in an.get("channels", []):
            ci = ch["target"].get("node")
            if ci is None:
                continue
            chemin = ch["target"]["path"]
            sp = an["samplers"][ch["sampler"]]
            n = {"translation": 3, "scale": 3, "rotation": 4}.get(chemin)
            if n is None:                              # weights
                mesh = J["nodes"][ci].get("mesh")
                n = len(J["meshes"][mesh]["primitives"][0].get("targets", []))
            v = echantillonner(J, BIN, cache, sp, t, n)
            trs[ci][{"translation": "t", "rotation": "r",
                     "scale": "s", "weights": "w"}[chemin]] = v
    return trs


def globales(J, trs):
    enfants = {}
    for i, nd in enumerate(J.get("nodes", [])):
        for c in nd.get("children", []):
            enfants[c] = i
    G = [None] * len(trs)

    def calc(i):
        if G[i] is not None:
            return G[i]
        L = colonne_vers_ligne(trs[i]["m"]) if trs[i]["m"] \
            else de_trs(trs[i]["t"], trs[i]["r"], trs[i]["s"])
        G[i] = mul(calc(enfants[i]), L) if i in enfants else L
        return G[i]

    for i in range(len(trs)):
        calc(i)
    return G


# -------------------------------------------------------------- rendu -------
def evaluer(J, BIN, temps):
    """Positions monde de chaque sommet du mesh peau, a chaque temps demande."""
    ni = next(i for i, n in enumerate(J["nodes"])
              if n.get("mesh") is not None and n.get("skin") is not None)
    nd = J["nodes"][ni]
    prim = J["meshes"][nd["mesh"]]["primitives"][0]
    base = VG.decoder(J, BIN, prim["attributes"]["POSITION"])
    cibles = [VG.decoder(J, BIN, tg["POSITION"]) for tg in prim.get("targets", [])]
    joints = VG.decoder(J, BIN, prim["attributes"]["JOINTS_0"])
    poids = VG.decoder(J, BIN, prim["attributes"]["WEIGHTS_0"])
    skin = J["skins"][nd["skin"]]
    ibm = [colonne_vers_ligne(m) for m in
           VG.decoder(J, BIN, skin["inverseBindMatrices"])] \
        if "inverseBindMatrices" in skin else [identite()] * len(skin["joints"])
    cache, out = {}, {}
    for t in temps:
        trs = poser(J, BIN, cache, t)
        G = globales(J, trs)
        w = trs[ni]["w"] or J["meshes"][nd["mesh"]].get("weights") \
            or [0.0] * len(cibles)
        S = [mul(G[j], ibm[k]) for k, j in enumerate(skin["joints"])]
        pts = []
        for v in range(len(base)):
            p = list(base[v])
            for k, c in enumerate(cibles):
                if w[k]:
                    d = c[v]
                    p[0] += w[k] * d[0]; p[1] += w[k] * d[1]; p[2] += w[k] * d[2]
            acc = [0.0, 0.0, 0.0]
            for l in range(4):
                pw = poids[v][l]
                if pw == 0.0:
                    continue
                q = applique(S[joints[v][l]], p)
                acc[0] += pw * q[0]; acc[1] += pw * q[1]; acc[2] += pw * q[2]
            pts.append(acc)
        out[t] = pts
    return out, {"node": ni, "sommets": len(base), "targets": len(cibles),
                 "joints": len(skin["joints"])}


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--times", nargs="+", type=float, required=True)
    a.add_argument("--output", required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    J, BIN, an, t0 = VG.lire_glb(os.path.abspath(Rp(o.input)))
    poses, info = evaluer(J, BIN, o.times)
    json.dump({"info": info,
               "poses": {("%.6f" % t): poses[t] for t in o.times}},
              open(Rp(o.output), "w"), separators=(",", ":"))
    print("RUNTIME_EVAL_OK", info, "->", o.output)
