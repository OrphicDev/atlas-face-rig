"""F0-D.8 / D.9 — mesures du raccord tete-corps, une SEULE implementation.

Barycentrique et Surface Deform doivent etre juges avec la meme regle. Deux
fonctions de mesure finiraient par diverger, et la comparaison ne voudrait
plus rien dire. Tout ce qui est chiffre dans les deux voies passe par ici.

Rien dans ce module n'ouvre de fichier ni ne modifie de scene : il mesure.
"""
import hashlib, struct, time

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

MM = 1000.0


def percentiles(valeurs):
    if not valeurs:
        return {"p50": None, "p95": None, "max": None, "n": 0}
    v = sorted(valeurs)
    return {"p50": round(v[len(v) // 2], 6),
            "p95": round(v[int(len(v) * 0.95)], 6),
            "max": round(v[-1], 6), "n": len(v)}


def deltas(reference, courant, indices=None):
    """Deplacement de chaque sommet, en millimetres."""
    idx = range(len(reference)) if indices is None else indices
    return [(courant[i] - reference[i]).length * MM for i in idx]


def sha_uv(me):
    if not me.uv_layers or not me.uv_layers.active:
        return None
    h = hashlib.sha256()
    for d in me.uv_layers.active.data:
        h.update(struct.pack("<2f", d.uv[0], d.uv[1]))
    return h.hexdigest()


def aretes_ouvertes(me):
    """Aretes bordees par une seule face : un trou, ou un bord franc."""
    compte = {}
    for p in me.polygons:
        for k in p.edge_keys:
            compte[k] = compte.get(k, 0) + 1
    return sum(1 for v in compte.values() if v == 1)


def aretes_non_manifold(me):
    """Aretes portees par trois faces ou plus."""
    compte = {}
    for p in me.polygons:
        for k in p.edge_keys:
            compte[k] = compte.get(k, 0) + 1
    return sum(1 for v in compte.values() if v >= 3)


def faces_inversees(me):
    """Faces dont la normale s'oppose a la normale recalculee."""
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    avant = [f.normal.copy() for f in bm.faces]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()
    n = sum(1 for i, f in enumerate(bm.faces) if f.normal.dot(avant[i]) < 0.0)
    bm.free()
    return n


def auto_intersections(ob, seuil=1e-7):
    """Paires de faces du MEME maillage qui se traversent."""
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    arbre = BVHTree.FromBMesh(bm, epsilon=seuil)
    paires = arbre.overlap(arbre)
    # une face chevauche toujours elle-meme et ses voisines de bord : on ne
    # retient que les paires qui ne partagent AUCUN sommet.
    bm.faces.ensure_lookup_table()
    vrai = 0
    for a, b in paires:
        if a >= b:
            continue
        va = {v.index for v in bm.faces[a].verts}
        vb = {v.index for v in bm.faces[b].verts}
        if not (va & vb):
            vrai += 1
    bm.free()
    return vrai


def sommets_doubles(ob, tolerance=1e-5):
    """Sommets confondus a la tolerance : signe d'une double surface."""
    from mathutils import kdtree
    co = [ob.matrix_world @ v.co for v in ob.data.vertices]
    kd = kdtree.KDTree(len(co))
    for i, p in enumerate(co):
        kd.insert(p, i)
    kd.balance()
    n = 0
    for i, p in enumerate(co):
        for (_, j, d) in kd.find_range(p, tolerance):
            if j > i:
                n += 1
    return n


def bilan_methode(nom, reference, courant, masque, ob_final, duree_s):
    """Le meme bilan pour toutes les voies : c'est ce qui rend l'A/B honnete."""
    dans = deltas(reference, courant, sorted(masque))
    hors_idx = [i for i in range(len(reference)) if i not in masque]
    hors = deltas(reference, courant, hors_idx)
    return {
        "methode": nom,
        "sommets_masque": len(masque),
        "sommets_hors_masque": len(hors_idx),
        "deplacement_dans_le_masque_mm": percentiles(dans),
        "deplacement_hors_masque_mm": percentiles(hors),
        "uv_sha256": sha_uv(ob_final.data),
        "aretes_ouvertes": aretes_ouvertes(ob_final.data),
        "aretes_non_manifold": aretes_non_manifold(ob_final.data),
        "faces_inversees": faces_inversees(ob_final.data),
        "auto_intersections": auto_intersections(ob_final),
        "sommets_doubles": sommets_doubles(ob_final),
        "secondes": round(duree_s, 4),
    }


class Chrono:
    def __enter__(self):
        self.t = time.perf_counter(); return self

    def __exit__(self, *a):
        self.duree = time.perf_counter() - self.t


# ------------------------------------------------- correspondance partagee ---
# La construction barycentrique vit ici pour que la voie Surface Deform et le
# banc synthetique jugent EXACTEMENT la meme carte que la voie barycentrique.
# `rig/build-body-transfer.py` garde la sienne, identique ligne pour ligne :
# elle ne peut pas etre executee sans l'asset externe, et je ne refactore pas
# du code que je ne peux pas faire tourner ici.

def triangles_et_bvh(me, matrice):
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(matrice)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    arbre = BVHTree.FromBMesh(bm)
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return arbre, tris


def construire_carte(points_source, arbre, tris, points_cible, masque,
                     portee=0.040):
    """Pour chaque sommet masque de la cible, son triangle source et ses poids."""
    carte, rejets, ecarts = {}, 0, []
    for i, p in enumerate(points_cible):
        if masque.get(i, 0.0) <= 0.0:
            continue
        loc, nor, idx, d = arbre.find_nearest(p, portee)
        if loc is None:
            rejets += 1; continue
        t3 = tris[idx]
        A, B, C = (points_source[t3[0]], points_source[t3[1]],
                   points_source[t3[2]])
        n = (B - A).cross(C - A)
        aire = n.length
        if aire < 1e-14:
            rejets += 1; continue
        u = (B - loc).cross(C - loc).length / aire
        v = (C - loc).cross(A - loc).length / aire
        w = (A - loc).cross(B - loc).length / aire
        somme = u + v + w
        ecarts.append(abs(somme - 1.0))
        if somme < 1e-12:
            rejets += 1; continue
        carte[i] = {"tri": t3, "bary": [u / somme, v / somme, w / somme],
                    "offset_mm": d * MM, "masque": masque.get(i, 0.0)}
    return carte, {"rejets": rejets,
                   "ecart_bary_max": max(ecarts) if ecarts else 0.0}


def appliquer_carte(carte, deplacements_source):
    """Deplacement de chaque sommet cible, pondere par le masque."""
    out = {}
    for i, e in carte.items():
        t3, (u, v, w) = e["tri"], e["bary"]
        d = (deplacements_source.get(t3[0], Vector((0, 0, 0))) * u
             + deplacements_source.get(t3[1], Vector((0, 0, 0))) * v
             + deplacements_source.get(t3[2], Vector((0, 0, 0))) * w)
        out[i] = d * e["masque"]
    return out
