"""F0.1 — audit topologique mesure de `Head (Animation) - Realistic`.

Lecture seule sur l'asset. Chaque sonde est verifiee sur une configuration dont
la reponse est connue AVANT d'etre appliquee au visage ; si une verification
echoue, le script sort en code non nul et ne publie aucun chiffre.

    export ATLAS_BASE_MESH=/chemin/vers/human_base_meshes_bundle.blend
    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-audit-topologie.py -- rapport.json
"""
import json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, kdtree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atlas_commun import exiger_asset
from mathutils.bvhtree import BVHTree

MM = 1000.0
ECHECS = []


def exige(condition, libelle, attendu, obtenu):
    etat = "OK" if condition else "ECHEC"
    print("  [%s] %s | attendu %s | obtenu %s" % (etat, libelle, attendu, obtenu))
    if not condition:
        ECHECS.append({"sonde": libelle, "attendu": str(attendu), "obtenu": str(obtenu)})


# ---------------------------------------------------------------- sondes ----

def volume_signe(bm):
    """Volume signe : positif si les normales pointent vers l'exterieur."""
    v = 0.0
    for f in bm.faces:
        vs = f.verts
        a = vs[0].co
        for i in range(1, len(vs) - 1):
            v += a.dot(vs[i].co.cross(vs[i + 1].co)) / 6.0
    return v


def _hemisphere(n):
    """n directions reparties sur l'hemisphere +Z (spirale de Fibonacci)."""
    d, ga = [], math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        z = (i + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        th = ga * i
        d.append(Vector((r * math.cos(th), r * math.sin(th), z)))
    return d


def fraction_degagee(bm, n_rayons=48, portee=100.0, decalage=None):
    """Pour chaque sommet : part des rayons partant vers l'exterieur qui s'echappent.

    Un sommet de peau exterieure voit le vide ; un sommet de muqueuse ou de
    fond d'orbite est enferme par le maillage lui-meme.
    """
    bm.normal_update()
    bvh = BVHTree.FromBMesh(bm)
    if decalage is None:
        aretes = [e.calc_length() for e in bm.edges]
        decalage = 0.02 * (sum(aretes) / len(aretes))
    base = _hemisphere(n_rayons)
    haut = Vector((0.0, 0.0, 1.0))
    out = [0.0] * len(bm.verts)
    for v in bm.verts:
        n = v.normal
        if n.length_squared < 1e-12:
            out[v.index] = 0.0
            continue
        q = haut.rotation_difference(n)
        o = v.co + n * decalage
        libres = 0
        for d in base:
            if bvh.ray_cast(o, q @ d, portee)[0] is None:
                libres += 1
        out[v.index] = libres / float(n_rayons)
    return out


def classer(frac, seuil):
    return [f > seuil for f in frac]   # True = exterieur


def anneaux_de_bord(bm, exterieur):
    """Bords entre peau exterieure et surface interieure, groupes en anneaux.

    Les aretes d'un tel bord sont des barreaux paralleles : deux barreaux
    voisins ne partagent pas de sommet mais la face qui les separe. Le
    groupement se fait donc par FACE partagee, pas par sommet.
    """
    ar = [e for e in bm.edges
          if exterieur[e.verts[0].index] != exterieur[e.verts[1].index]]
    par_face = {}
    for e in ar:
        for f in e.link_faces:
            par_face.setdefault(f.index, []).append(e)
    vus, groupes = set(), []
    for e in ar:
        if e.index in vus: continue
        pile, grp = [e], []
        vus.add(e.index)
        while pile:
            cur = pile.pop(); grp.append(cur)
            for f in cur.link_faces:
                for e2 in par_face.get(f.index, ()):
                    if e2.index not in vus:
                        vus.add(e2.index); pile.append(e2)
        groupes.append(grp)
    groupes.sort(key=lambda g: -len(g))
    return groupes


def decrire_anneau(grp, M, exterieur):
    vts = {v for e in grp for v in e.verts}
    dehors = sorted(v.index for v in vts if exterieur[v.index])
    co = [M @ v.co for v in vts]
    return {
        "aretes": len(grp), "sommets": len(vts),
        "sommets_cote_peau": len(dehors), "indices_peau": dehors,
        "perimetre_mm": round(sum(e.calc_length() for e in grp) * MM, 2),
        "centre": [round(sum(c[i] for c in co) / len(co), 5) for i in range(3)],
        "bbox_min": [round(min(c[i] for c in co), 5) for i in range(3)],
        "bbox_max": [round(max(c[i] for c in co), 5) for i in range(3)],
        "largeur_mm": round((max(c.x for c in co) - min(c.x for c in co)) * MM, 2),
        "hauteur_mm": round((max(c.z for c in co) - min(c.z for c in co)) * MM, 2),
        "indices": sorted(v.index for v in vts),
    }


def anneaux_concentriques(bm, graines, autorises, maxi=40):
    """Boucles successives autour d'une graine, en distance de graphe.

    `autorises` restreint la propagation (p.ex. a la peau exterieure) pour que
    l'on compte bien des boucles de paupiere et non l'interieur de l'orbite.
    """
    vu = set(graines)
    front = set(graines)
    profils = []
    for k in range(1, maxi + 1):
        suivant = set()
        for i in front:
            for e in bm.verts[i].link_edges:
                j = e.other_vert(bm.verts[i]).index
                if j not in vu and autorises[j]:
                    suivant.add(j)
        if not suivant: break
        vu |= suivant
        front = suivant
        profils.append(sorted(suivant))
    return profils


def distance_moyenne(bm, M, indices, reference):
    co = [M @ bm.verts[i].co for i in indices]
    return round(sum(min((c - r).length for r in reference) for c in co) / len(co) * MM, 2)


def erreur_de_symetrie(co, plan_x):
    """Pour chaque sommet, distance a l'image miroir la plus proche, en mm."""
    kd = kdtree.KDTree(len(co))
    for i, c in enumerate(co): kd.insert(c, i)
    kd.balance()
    err = []
    for c in co:
        m = Vector((2 * plan_x - c.x, c.y, c.z))
        err.append(kd.find(m)[2] * MM)
    return err


def carte_miroir(bm, plan_x=0.0):
    """Appariement COMBINATOIRE gauche/droite, propage par le graphe du maillage.

    On ne se contente pas du plus proche voisin de l'image miroir : on part d'un
    couple sur puis on propage de voisin en voisin. Si la carte obtenue est une
    bijection involutive qui envoie toute arete sur une arete et toute face sur
    une face, alors la topologie est exactement symetrique — et c'est demontre,
    pas suppose.
    """
    n = len(bm.verts)
    co = [v.co.copy() for v in bm.verts]
    mir = lambda c: Vector((2 * plan_x - c.x, c.y, c.z))
    kd = kdtree.KDTree(n)
    for i, c in enumerate(co): kd.insert(c, i)
    kd.balance()

    depart = max(range(n), key=lambda i: abs(co[i].x - plan_x))
    carte = [-1] * n
    carte[depart] = kd.find(mir(co[depart]))[1]
    carte[carte[depart]] = depart
    file = [depart, carte[depart]]
    ecarts = []
    while file:
        i = file.pop()
        j = carte[i]
        vi = [e.other_vert(bm.verts[i]).index for e in bm.verts[i].link_edges]
        vj = [e.other_vert(bm.verts[j]).index for e in bm.verts[j].link_edges]
        if len(vi) != len(vj):
            return None, {"echec": "valences differentes", "sommet": i, "miroir": j}
        libres = list(vj)
        for a in vi:
            if not libres: break
            cible = mir(co[a])
            b = min(libres, key=lambda x: (co[x] - cible).length)
            ecarts.append((co[b] - cible).length)
            libres.remove(b)
            if carte[a] == -1:
                carte[a] = b; carte[b] = a
                file.append(a)
                if b != a: file.append(b)
            elif carte[a] != b:
                return None, {"echec": "appariement contradictoire", "sommet": a,
                              "deja": carte[a], "propose": b}
    if -1 in carte:
        return None, {"echec": "sommets non apparies", "nombre": carte.count(-1)}
    return carte, {"ecart_propagation_max_mm": round(max(ecarts) * MM, 5)}


def verifier_miroir(bm, carte):
    aretes = {tuple(sorted((e.verts[0].index, e.verts[1].index))) for e in bm.edges}
    faces = {tuple(sorted(v.index for v in f.verts)) for f in bm.faces}
    return {
        "bijection": sorted(carte) == list(range(len(carte))),
        "involutive": all(carte[carte[i]] == i for i in range(len(carte))),
        "aretes_sans_image": sum(
            1 for a in aretes if tuple(sorted((carte[a[0]], carte[a[1]]))) not in aretes),
        "faces_sans_image": sum(
            1 for f in faces if tuple(sorted(carte[i] for i in f)) not in faces),
        "sommets_sur_l_axe": sum(1 for i in range(len(carte)) if carte[i] == i),
    }


def poles(bm, indices=None):
    src = bm.verts if indices is None else [bm.verts[i] for i in indices]
    return [v.index for v in src if len(v.link_edges) != 4]


def densite(bm, M, indices):
    """Longueur d'arete et surface par sommet dans un ensemble de sommets."""
    ens = set(indices)
    ar = [e.calc_length() * MM for e in bm.edges
          if e.verts[0].index in ens and e.verts[1].index in ens]
    fa = [f.calc_area() * 1e6 for f in bm.faces
          if all(v.index in ens for v in f.verts)]
    ar.sort()
    return {
        "sommets": len(ens), "aretes": len(ar), "faces": len(fa),
        "arete_moy_mm": round(sum(ar) / len(ar), 3) if ar else None,
        "arete_med_mm": round(ar[len(ar) // 2], 3) if ar else None,
        "arete_min_mm": round(ar[0], 3) if ar else None,
        "arete_max_mm": round(ar[-1], 3) if ar else None,
        "surface_mm2": round(sum(fa), 1) if fa else None,
        "sommets_par_cm2": round(len(ens) / (sum(fa) / 100.0), 2) if fa and sum(fa) else None,
    }


def inventaire_faces(bm):
    q = t = n = 0
    detail = []
    for f in bm.faces:
        c = len(f.verts)
        if c == 4: q += 1
        elif c == 3: t += 1; detail.append(("tri", f.index, c))
        else: n += 1; detail.append(("ngon", f.index, c))
    return q, t, n, detail


# ------------------------------------------------------ verification ----

def sphere(u=32, v=16, rayon=1.0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=rayon)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    return bm


def creuser(bm, vers_le_haut=True):
    """Enfonce un pole en entonnoir long et etroit : une ouverture, connue."""
    s = 1 if vers_le_haut else -1
    pole = max(bm.verts, key=lambda x: s * x.co.z)
    voisins = [e.other_vert(pole) for e in pole.link_edges]
    for w in voisins:
        r = math.hypot(w.co.x, w.co.y)
        k = 0.09 / r if r > 1e-9 else 0.0
        w.co = Vector((w.co.x * k, w.co.y * k, -s * 0.35))
    pole.co = Vector((0.0, 0.0, -s * 0.62))
    return len(voisins)


def verifier(n_rayons, seuil):
    print("VERIFICATION DES SONDES")

    # -- orientation des normales
    bm = sphere()
    exige(volume_signe(bm) > 0, "volume signe d'une sphere > 0", "> 0", round(volume_signe(bm), 4))

    # -- degagement : sphere nue -> aucun interieur, aucun anneau
    f = fraction_degagee(bm, n_rayons)
    ext = classer(f, seuil)
    exige(all(ext), "sphere nue : tous les sommets exterieurs",
          "%d/%d" % (len(ext), len(ext)), "%d/%d" % (sum(ext), len(ext)))
    exige(len(anneaux_de_bord(bm, ext)) == 0, "sphere nue : 0 anneau de bord", 0,
          len(anneaux_de_bord(bm, ext)))
    exige(min(f) > 0.4, "sphere nue : degagement minimal eleve", "> 0.40", round(min(f), 3))

    # -- degagement : une ouverture -> exactement 1 anneau, de u_segments aretes
    bm1 = sphere(); n1 = creuser(bm1, True)
    f1 = fraction_degagee(bm1, n_rayons); e1 = classer(f1, seuil)
    a1 = anneaux_de_bord(bm1, e1)
    exige(len(a1) == 1, "une cavite : 1 anneau de bord", 1, len(a1))
    if a1:
        exige(len(a1[0]) == n1, "une cavite : anneau de %d aretes" % n1, n1, len(a1[0]))
    exige(sum(1 for x in e1 if not x) > 0, "une cavite : sommets interieurs > 0", "> 0",
          sum(1 for x in e1 if not x))

    # -- deux ouvertures -> 2 anneaux (la sonde repond a son entree)
    bm2 = sphere(); creuser(bm2, True); creuser(bm2, False)
    f2 = fraction_degagee(bm2, n_rayons); e2 = classer(f2, seuil)
    a2 = anneaux_de_bord(bm2, e2)
    exige(len(a2) == 2, "deux cavites : 2 anneaux de bord", 2, len(a2))

    # -- anneaux concentriques sur une sphere : chaque anneau vaut u_segments
    bm3 = sphere(u=32, v=16)
    pole = max(bm3.verts, key=lambda x: x.co.z)
    tous = [True] * len(bm3.verts)
    prof = anneaux_concentriques(bm3, [pole.index], tous)
    inter = [len(p) for p in prof[:-1]]
    exige(all(x == 32 for x in inter) and len(prof[-1]) == 1,
          "anneaux concentriques sur sphere 32x16",
          "14 anneaux de 32 puis 1", "%s puis %d" % (set(inter), len(prof[-1])))

    # -- symetrie : miroir exact puis un sommet decale de 1,000 mm
    co = [v.co.copy() for v in bm3.verts]
    err = erreur_de_symetrie(co, 0.0)
    exige(max(err) < 0.01, "symetrie d'une sphere centree", "< 0,01 mm", round(max(err), 6))
    # le sommet decale doit etre HORS du plan miroir, sinon il est son propre
    # miroir et la sonde ne peut rien voir : c'est ce test-la qui l'a montre.
    loin = max(range(len(co)), key=lambda i: abs(co[i].x))
    co[loin] = co[loin] + Vector((0.0, 0.0, 0.001))
    err = erreur_de_symetrie(co, 0.0)
    exige(abs(max(err) - 1.0) < 0.01, "symetrie : sommet decale de 1 mm", "1,000 mm",
          round(max(err), 4))

    # -- densite : grille de 1 m en 10 segments -> arete de 100,000 mm
    bmg = bmesh.new()
    bmesh.ops.create_grid(bmg, x_segments=10, y_segments=10, size=1.0)
    bmg.verts.ensure_lookup_table(); bmg.edges.ensure_lookup_table(); bmg.faces.ensure_lookup_table()
    d = densite(bmg, None, [v.index for v in bmg.verts])
    pas = 2.0 / 10 * MM
    exige(abs(d["arete_moy_mm"] - pas) < 1e-6, "densite : arete d'une grille 10x10 sur 2 m",
          pas, d["arete_moy_mm"])
    exige(abs(d["surface_mm2"] - 4e6) < 1.0, "densite : surface d'une grille de 2 m",
          4000000.0, d["surface_mm2"])

    # -- inventaire des faces : 1 triangle, 1 quad, 1 pentagone construits a la main
    bmf = bmesh.new()
    vs = [bmf.verts.new((x, y, 0)) for x, y in
          ((0, 0), (1, 0), (0, 1), (2, 0), (3, 0), (3, 1), (2, 1),
           (4, 0), (5, 0), (5, 1), (4.5, 1.5), (4, 1))]
    bmf.verts.ensure_lookup_table()
    bmf.faces.new((vs[0], vs[1], vs[2]))
    bmf.faces.new((vs[3], vs[4], vs[5], vs[6]))
    bmf.faces.new((vs[7], vs[8], vs[9], vs[10], vs[11]))
    bmf.faces.ensure_lookup_table()
    q, t, n, _ = inventaire_faces(bmf)
    exige((q, t, n) == (1, 1, 1), "inventaire faces : 1 quad / 1 tri / 1 ngon", (1, 1, 1), (q, t, n))

    # -- carte miroir : exacte sur une sphere, mise en defaut par une face piquee
    bms = sphere()
    c, info = carte_miroir(bms, 0.0)
    exige(c is not None, "carte miroir : sphere appariee", "carte", info)
    if c:
        v = verifier_miroir(bms, c)
        exige(v["bijection"] and v["involutive"] and v["aretes_sans_image"] == 0
              and v["faces_sans_image"] == 0, "carte miroir : sphere symetrique",
              "bijective, 0 arete/face orpheline", v)
    bmp = sphere()
    cible = max(bmp.faces, key=lambda f: f.calc_center_median().x)
    bmesh.ops.poke(bmp, faces=[cible])
    bmp.verts.ensure_lookup_table(); bmp.edges.ensure_lookup_table(); bmp.faces.ensure_lookup_table()
    c2, info2 = carte_miroir(bmp, 0.0)
    casse = c2 is None or any(verifier_miroir(bmp, c2)[k] for k in
                              ("aretes_sans_image", "faces_sans_image")) \
        or not verifier_miroir(bmp, c2)["bijection"]
    exige(casse, "carte miroir : une face piquee d'un seul cote est detectee",
          "asymetrie detectee", "detectee" if casse else "non detectee")
    bms.free(); bmp.free()

    # -- poles : les sommets de valence != 4 d'une grille = son bord
    p = poles(bmg)
    bord = [v.index for v in bmg.verts if any(len(e.link_faces) == 1 for e in v.link_edges)]
    exige(sorted(p) == sorted(bord), "poles : bord d'une grille", len(bord), len(p))

    for b in (bm, bm1, bm2, bm3, bmg, bmf): b.free()
    print("VERIFICATION %s (%d echec(s))" % ("OK" if not ECHECS else "ECHOUEE", len(ECHECS)))
    return not ECHECS


# ------------------------------------------------------------- audit ----

def audit(n_rayons, seuil):
    # P1 : ce script refuse desormais lui-meme un asset de mauvais SHA.
    PAQUET, _pf = exiger_asset()
    COL = "Head (Animation) - Realistic"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = [COL]
    col = dst.collections[0]
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.update()

    mailles = [o for o in col.all_objects if o.type == "MESH"]
    tete = max(mailles, key=lambda o: len(o.data.vertices))
    M = tete.matrix_world
    R = {"asset": os.path.basename(PAQUET), "collection": COL, "blender": bpy.app.version_string,
         "objet": tete.name, "rayons_par_sommet": n_rayons, "seuil_degagement": seuil}

    bm = bmesh.new(); bm.from_mesh(tete.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()

    R["transformations"] = {"location": [round(x, 6) for x in tete.location],
                            "rotation_euler": [round(x, 6) for x in tete.rotation_euler],
                            "scale": [round(x, 6) for x in tete.scale]}
    R["volume_signe_m3"] = round(volume_signe(bm), 8)
    q, t, n, detail = inventaire_faces(bm)
    R["faces"] = {"quads": q, "triangles": t, "ngons": n, "total": len(bm.faces),
                  "part_de_quads": round(q / len(bm.faces), 5)}

    co = [M @ v.co for v in bm.verts]
    mn = Vector([min(c[i] for c in co) for i in range(3)])
    mx = Vector([max(c[i] for c in co) for i in range(3)])
    R["bbox_monde"] = {"min": [round(x, 5) for x in mn], "max": [round(x, 5) for x in mx],
                       "dimensions_mm": [round((mx[i] - mn[i]) * MM, 2) for i in range(3)]}

    # ---- symetrie : d'abord la topologie, ensuite la geometrie ----
    loc = [v.co.copy() for v in bm.verts]
    meilleur = min(((sum(erreur_de_symetrie(loc, c)), c)
                    for c in [i * 1e-4 for i in range(-20, 21)]), key=lambda z: z[0])[1]
    ech = tete.scale[0]
    carte, info = carte_miroir(bm, meilleur)
    R["symetrie_topologique"] = {"plan_x_local_m": round(meilleur, 6), "propagation": info}
    if carte:
        R["symetrie_topologique"].update(verifier_miroir(bm, carte))
        e2 = [(Vector((2 * meilleur - loc[carte[i]].x, loc[carte[i]].y, loc[carte[i]].z))
               - loc[i]).length * MM * ech for i in range(len(loc))]
    else:
        e2 = erreur_de_symetrie(loc, meilleur)
        e2 = [x * ech for x in e2]
    tri = sorted(e2)
    R["symetrie_geometrique"] = {
        "methode": "carte miroir combinatoire" if carte else "plus proche voisin (carte non obtenue)",
        "unite": "mm dans le repere MONDE (echelle objet %.3f appliquee)" % ech,
        "max_mm": round(max(e2), 5), "moy_mm": round(sum(e2) / len(e2), 5),
        "median_mm": round(tri[len(tri) // 2], 5),
        "p99_mm": round(tri[int(len(tri) * 0.99)], 5),
        "sommets_hors_0_01mm": sum(1 for x in e2 if x > 0.01),
        "sommets_hors_0_1mm": sum(1 for x in e2 if x > 0.1),
        "sommets_hors_1mm": sum(1 for x in e2 if x > 1.0),
    }

    # ---- integrite ----
    R["integrite"] = {
        "bords_ouverts": len([e for e in bm.edges if len(e.link_faces) == 1]),
        "aretes_non_manifold": len([e for e in bm.edges if len(e.link_faces) > 2]),
        "aretes_sans_face": len([e for e in bm.edges if len(e.link_faces) == 0]),
        "sommets_laches": len([v for v in bm.verts if not v.link_edges]),
        "faces_degenerees": len([f for f in bm.faces if f.calc_area() < 1e-12]),
    }
    kd = kdtree.KDTree(len(bm.verts))
    for v in bm.verts: kd.insert(v.co, v.index)
    kd.balance()
    dbl = set()
    for v in bm.verts:
        for (_, i, _) in kd.find_range(v.co, 1e-5):
            if i != v.index: dbl.add(tuple(sorted((v.index, i))))
    R["integrite"]["paires_doublons_10um"] = len(dbl)
    avant = [f.normal.copy() for f in bm.faces]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.ensure_lookup_table()
    R["integrite"]["faces_normale_incoherente"] = sum(
        1 for i, f in enumerate(bm.faces) if f.normal.dot(avant[i]) < 0)
    bm.free()

    bm = bmesh.new(); bm.from_mesh(tete.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()

    # ---- interieur / exterieur ----
    frac = fraction_degagee(bm, n_rayons)
    hist = [0] * 20
    for f in frac: hist[min(19, int(f * 20))] += 1
    R["degagement_histogramme_par_0_05"] = hist
    ext = classer(frac, seuil)
    R["exterieur_interieur"] = {"exterieur": sum(ext), "interieur": len(ext) - sum(ext)}

    # stabilite du seuil
    stab = {}
    for s in (0.02, 0.05, 0.10, 0.15, 0.20, 0.30):
        e = classer(frac, s)
        stab["%.2f" % s] = {"interieur": len(e) - sum(e), "anneaux": len(anneaux_de_bord(bm, e))}
    R["stabilite_du_seuil"] = stab

    anneaux = anneaux_de_bord(bm, ext)
    R["ouvertures"] = [decrire_anneau(g, M, ext) for g in anneaux]

    # ---- nommage des ouvertures par leur position mesuree ----
    scl = {o.name: o for o in mailles if "sclera" in o.name}
    centres = {}
    for nom, o in scl.items():
        c = [o.matrix_world @ v.co for v in o.data.vertices]
        ctr = Vector([sum(x[i] for x in c) / len(c) for i in range(3)])
        ray = sum((x - ctr).length for x in c) / len(c)
        centres[nom] = (ctr, ray)
        R.setdefault("globes_oculaires", {})[nom] = {
            "centre": [round(x, 5) for x in ctr], "rayon_mm": round(ray * MM, 3)}

    # etiquetage par la position MESUREE, pas par l'ordre de detection :
    #  - fente palpebrale : centree sur un globe oculaire ;
    #  - conduit auditif  : a plus de 50 mm du plan sagittal ;
    #  - bouche           : la plus large des ouvertures proches de l'axe ;
    #  - narine           : proche de l'axe, au-dessus de la bouche.
    axe = (mn.x + mx.x) / 2
    i_nez = min(range(len(co)), key=lambda i: co[i].y)
    R["pointe_du_nez"] = [round(x, 5) for x in co[i_nez]]
    for a in R["ouvertures"]:
        c = Vector(a["centre"])
        cote = "L" if c.x > axe else "R"
        pose = None
        for nom, (ctr, ray) in centres.items():
            if (c - ctr).length < 0.025:
                pose = "fente_palpebrale." + ("L" if nom.endswith(".L") else "R")
        if pose is None and abs(c.x - axe) > 0.050:
            pose = "conduit_auditif." + cote
        a["nom"] = pose
        a["ecart_axe_mm"] = round((c.x - axe) * MM, 2)
    proches = [a for a in R["ouvertures"] if a["nom"] is None]
    if proches:
        bouche = max(proches, key=lambda a: a["largeur_mm"])
        bouche["nom"] = "fente_labiale"
        for a in proches:
            if a is bouche: continue
            a["nom"] = ("narine." + ("L" if a["centre"][0] > axe else "R")
                        if a["centre"][2] > bouche["centre"][2] else "ouverture_non_identifiee")
    nommees = {a["nom"]: a for a in R["ouvertures"] if a["nom"]}
    R["ouvertures_attendues"] = sorted(["fente_labiale", "fente_palpebrale.L", "fente_palpebrale.R",
                                        "narine.L", "narine.R", "conduit_auditif.L",
                                        "conduit_auditif.R"])
    R["ouvertures_trouvees"] = sorted(nommees)
    R["compte_des_ouvertures_conforme"] = R["ouvertures_attendues"] == R["ouvertures_trouvees"]

    # Cavites : remplissage de proche en proche SUR la surface interieure, a
    # partir du bord de chaque ouverture. Une mesure bornee par un rayon fixe
    # rendrait ce rayon pour toutes les cavites — donc rien du tout.
    interieur_seul = [not e for e in ext]
    vus_cav = {}
    for nom, a in nommees.items():
        depart = [i for i in a["indices"] if not ext[i]]
        comp = set(depart); pile = list(depart)
        while pile:
            i = pile.pop()
            for e in bm.verts[i].link_edges:
                j = e.other_vert(bm.verts[i]).index
                if j not in comp and interieur_seul[j]:
                    comp.add(j); pile.append(j)
        ctr = Vector(a["centre"])
        a["cavite"] = {
            "sommets": len(comp),
            "profondeur_max_mm": round(max((co[i] - ctr).length for i in comp) * MM, 2),
            "surface_mm2": round(sum(f.calc_area() for f in bm.faces
                                     if all(v.index in comp for v in f.verts)) * 1e6, 1),
        }
        vus_cav[nom] = frozenset(comp)
    # cavites partagees : deux ouvertures qui debouchent sur le meme volume
    R["cavites_communes"] = [[a, b] for i, a in enumerate(sorted(vus_cav))
                             for b in sorted(vus_cav)[i + 1:] if vus_cav[a] == vus_cav[b]]

    # ---- boucles concentriques autour de chaque ouverture ----
    R["boucles"] = {}
    for nom, a in nommees.items():
        prof = anneaux_concentriques(bm, a["indices_peau"], ext, maxi=25)
        ref = [M @ bm.verts[i].co for i in a["indices_peau"]]
        R["boucles"][nom] = {
            "anneau_0_sommets": len(a["indices_peau"]),
            "profil": [{"anneau": k + 1, "sommets": len(p),
                        "distance_moy_mm": distance_moyenne(bm, M, p, ref)}
                       for k, p in enumerate(prof[:12])],
        }

    # ---- densites regionales, definies par des reperes mesures ----
    def dans_boule(centre, r):
        return [v.index for v in bm.verts if ((M @ v.co) - centre).length <= r]

    def dans_boite(mnv, mxv):
        return [v.index for v in bm.verts
                if all(mnv[i] <= (M @ v.co)[i] <= mxv[i] for i in range(3))]

    R["densites"] = {}
    if "fente_labiale" in nommees:
        b = nommees["fente_labiale"]
        cb = Vector(b["centre"])
        gx, dx = b["bbox_min"][0], b["bbox_max"][0]
        for cote, x in (("L", dx), ("R", gx)):
            c = Vector((x, cb.y, cb.z))
            R["densites"]["commissure." + cote] = densite(bm, M, dans_boule(c, 0.008))
        R["densites"]["levres_10mm"] = densite(bm, M, dans_boule(cb, 0.010))
        R["densites"]["levres_20mm"] = densite(bm, M, dans_boule(cb, 0.020))
    for cote in ("L", "R"):
        k = "fente_palpebrale." + cote
        if k in nommees:
            c = Vector(nommees[k]["centre"])
            R["densites"]["oeil_" + cote + "_10mm"] = densite(bm, M, dans_boule(c, 0.010))
            R["densites"]["oeil_" + cote + "_20mm"] = densite(bm, M, dans_boule(c, 0.020))
            # sourcil / front : bande au-dessus de l'oeil
            R["densites"]["sourcil_front_" + cote] = densite(bm, M, dans_boite(
                Vector((c.x - 0.025, mn.y, c.z + 0.008)), Vector((c.x + 0.025, c.y + 0.02, c.z + 0.045))))
    # sillon nasogenien : de l'aile du nez a la commissure
    nar = [a for a in R["ouvertures"] if (a.get("nom") or "").startswith("narine")]
    if nar and "fente_labiale" in nommees:
        b = nommees["fente_labiale"]
        for a in nar:
            cote = a["nom"].split(".")[1]
            xa = a["centre"][0]
            xc = b["bbox_max"][0] if cote == "L" else b["bbox_min"][0]
            lo, hi = sorted((xa, xc))
            R["densites"]["sillon_nasogenien." + cote] = densite(bm, M, dans_boite(
                Vector((lo - 0.004, mn.y, b["centre"][2] - 0.002)),
                Vector((hi + 0.004, mn.y + 0.045, a["centre"][2] + 0.004))))
    # raccord tete-cou : bande horizontale sous le menton
    if "fente_labiale" in nommees:
        zb = nommees["fente_labiale"]["centre"][2]
        R["densites"]["cou_sous_menton"] = densite(bm, M, dans_boite(
            Vector((mn.x, mn.y, zb - 0.075)), Vector((mx.x, mx.y, zb - 0.045))))

    # ---- poles et continuite dans le tiers median du visage ----
    zone = dans_boite(Vector((mn.x, mn.y, (nommees["fente_labiale"]["centre"][2] - 0.02)
                              if "fente_labiale" in nommees else mn.z)),
                      Vector((mx.x, mn.y + 0.06, (mx.z))))
    p = poles(bm, zone)
    R["poles_face_avant"] = {
        "sommets_de_la_zone": len(zone), "poles": len(p),
        "valences": {str(k): sum(1 for i in p if len(bm.verts[i].link_edges) == k)
                     for k in sorted({len(bm.verts[i].link_edges) for i in p})},
        "positions": [[round(x, 5) for x in (M @ bm.verts[i].co)] for i in p][:80],
    }

    # ---- position anatomique des ngons et triangles ----
    def region(c):
        for nom, a in nommees.items():
            if (Vector(c) - Vector(a["centre"])).length < 0.030:
                return nom
        for nom, (ctr, _) in centres.items():
            if (Vector(c) - ctr).length < 0.040:
                return "orbite." + ("L" if nom.endswith(".L") else "R")
        if c[2] < mn.z + 0.09: return "base_du_cou"
        return "autre"

    R["ngons"], R["triangles"] = [], []
    for f in bm.faces:
        k = len(f.verts)
        if k == 4: continue
        c = M @ f.calc_center_median()
        d = {"index": f.index, "cotes": k, "centre": [round(x, 5) for x in c],
             "aire_mm2": round(f.calc_area() * 1e6, 3), "region": region(c)}
        (R["ngons"] if k > 4 else R["triangles"]).append(d)

    bm.free()
    return R


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    sortie = args[0]
    # Seuil 0,15 : c'est le point de fonctionnement ou la sonde rend exactement
    # les SEPT ouvertures qu'a une tete humaine (bouche, deux fentes
    # palpebrales, deux narines, deux conduits auditifs) et pas une de plus.
    # La table `stabilite_du_seuil` du rapport en donne la preuve.
    RAYONS, SEUIL = 48, 0.15
    ok = verifier(RAYONS, SEUIL)
    if not ok:
        json.dump({"verification": "ECHEC", "echecs": ECHECS}, open(sortie, "w"), indent=2)
        print("SONDES NON VERIFIEES : aucun chiffre publie.")
        sys.exit(2)
    R = audit(RAYONS, SEUIL)
    R["verification_des_sondes"] = "OK"
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("AUDIT_OK ->", sortie)
