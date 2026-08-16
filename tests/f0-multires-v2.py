"""P0.4 / P0.5 — banc multires V2 : prototypes anatomiques, deux voies, UV, temps.

Le banc V1 posait des bourrelets cosinus. Il prouvait la mecanique d'evaluation
et le retour au neutre, rien de plus. Celui-ci ferme reellement une paupiere sur
le globe, met reellement les levres en contact, et fait pivoter la mandibule
depuis l'axe temporo-mandibulaire mesure.

Voie A : cage de 3 242 sommets + shape key, Multires original conserve.
Voie B : duplicata haute resolution materialise depuis le Multires evalue,
         modificateur retire, shape key sur les 12 950 sommets.
Les deux partent de la MEME surface neutre evaluee.

Rien ne survit : tout est jetable, la source autoritaire n'est jamais ouverte
en ecriture.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-multires-v2.py -- \
      source/FACE_BASE_LOCKED.blend reports/f0-correction/multires-ab-v2.json
"""
import hashlib, json, math, os, statistics, struct, sys, tempfile, time
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from atlas_commun import Registre
from anatomie import Clignement, FermetureLabiale, Machoire, MM

BLEND, SORTIE = sys.argv[sys.argv.index("--") + 1:][:2]
TETE = "GEO-head_animation_realistic"


# ------------------------------------------------------------ outils ----

def ouvrir():
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(BLEND))
    return bpy.data.objects[TETE]


def evaluer(ob):
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    co = [ob.matrix_world @ v.co.copy() for v in me.vertices]
    n = (len(me.vertices), len(me.polygons), len(me.loops))
    uv = sha_uv(me)
    ev.to_mesh_clear()
    return co, n, uv


def sha_uv(me):
    h = hashlib.sha256()
    c = me.uv_layers.active
    if not c: return None
    h.update(c.name.encode())
    for d in c.data: h.update(struct.pack("<2f", d.uv[0], d.uv[1]))
    return h.hexdigest()


def stats(v):
    v = sorted(v)
    if not v: return None
    return {"min": round(v[0], 6), "median": round(statistics.median(v), 6),
            "p95": round(v[int(len(v) * 0.95)], 6), "max": round(v[-1], 6),
            "moyenne": round(sum(v) / len(v), 6)}


def ecart_indice(a, b):
    d = [(x - y).length * MM for x, y in zip(a, b)]
    return stats(d) if len(a) == len(b) else None


def volume(co, faces):
    v = 0.0
    for f in faces:
        p = [co[i] for i in f]
        for k in range(1, len(p) - 1):
            v += p[0].dot(p[k].cross(p[k + 1])) / 6.0
    return abs(v)


def ajuster_sphere(pts):
    """Sphere des moindres carres. Le centroide d'une CALOTTE n'est pas le
    centre de sa sphere, et sa distance moyenne n'est pas le rayon : c'est ce
    qui faisait compter 267 fausses penetrations au neutre."""
    import numpy as np
    P = np.asarray([[p.x, p.y, p.z] for p in pts], dtype=np.float64)
    A = np.hstack([2.0 * P, np.ones((len(P), 1))])
    b = (P ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = Vector((float(sol[0]), float(sol[1]), float(sol[2])))
    r = math.sqrt(max(0.0, float(sol[3]) + sol[0] ** 2 + sol[1] ** 2 + sol[2] ** 2))
    residus = [abs((p - c).length - r) for p in pts]
    return c, r, max(residus)


_GLOBES = {}


def repere_globes(ob):
    if _GLOBES:
        return {k: v for k, v in _GLOBES.items() if k in ("L", "R")}
    for c in "LR":
        s = bpy.data.objects[TETE + ".sclera." + c]
        pts = [s.matrix_world @ v.co for v in s.data.vertices]
        ctr, r, res = ajuster_sphere(pts)
        _GLOBES[c] = (ctr, r)
        _GLOBES.setdefault("_residus", {})[c] = round(res * MM, 4)
    return {k: v for k, v in _GLOBES.items() if k in ("L", "R")}


# --------------------------------------------------- voies A et B ----

def voie_A(ob):
    """Cage autoritaire : shape key sur 3 242 sommets, Multires conserve."""
    return ob, [ob.matrix_world @ v.co for v in ob.data.vertices]


def voie_B(ob):
    """Haute resolution materialisee depuis le Multires evalue, sur duplicata."""
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True,
                                         depsgraph=bpy.context.evaluated_depsgraph_get())
    dup = bpy.data.objects.new("PROTOTYPE_HAUTE_RES", me)
    dup.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(dup)
    for m in list(dup.modifiers): dup.modifiers.remove(m)
    ob.hide_render = True
    return dup, [dup.matrix_world @ v.co for v in dup.data.vertices]


def poser_shape_key(ob, deltas, nom="PROTO"):
    if not ob.data.shape_keys: ob.shape_key_add(name="Basis", from_mix=False)
    k = ob.shape_key_add(name=nom, from_mix=False)
    Mi = ob.matrix_world.inverted().to_3x3()
    touches = 0
    for i, d in enumerate(deltas):
        if d.length > 0.0:
            k.data[i].co = k.data[i].co + (Mi @ d)
            touches += 1
    k.value = 1.0
    return k, touches


# ------------------------------------------------------- prototypes ----

def proto_clignement(co_monde, ob, intensite, bords=None, co_cage=None):
    """Ancre sur le bord palpebral publie en F0, jamais sur un rayon devine."""
    g = repere_globes(ob)
    lat = (g["L"][0] - g["R"][0]).normalized()
    deltas = [Vector((0, 0, 0)) for _ in co_monde]
    infos = {}
    for cote in "LR":
        ctr, R = g[cote]
        bord = [co_cage[i] for i in bords[cote]]
        cl = Clignement(bord, ctr, R, lat)
        conc = sum(1 for p in co_monde if cl.concerne(p))
        for i, p in enumerate(co_monde):
            d = cl.deplacer(p, intensite)
            if d.length > 0: deltas[i] = deltas[i] + d
        infos[cote] = {"sommets_du_bord": len(bord), "sommets_concernes": conc,
                       "portee_mm": round(cl.portee * MM, 2),
                       "h_contact": round(cl.h_contact, 6)}
    return deltas, infos


def proto_levres(co_monde, ob, intensite, bords=None, co_cage=None):
    """Ancre sur le bord de la fente labiale publie en F0."""
    bord = [co_cage[i] for i in bords["LEVRES"]]
    f = FermetureLabiale(bord)
    deltas = [f.deplacer(p, intensite) for p in co_monde]
    return deltas, {"sommets_du_bord": len(bord),
                    "demi_largeur_mm": round(f.demi * MM, 2),
                    "z_contact": round(f.z_contact, 5), "centre_x": round(f.cx, 5)}


def proto_machoire(co_monde, ob, degres, bords=None, co_cage=None):
    """Pivot temporo-mandibulaire mesure, levre superieure et nuque relachees."""
    bord = [co_cage[i] for i in bords["LEVRES"]]
    z_levre = sum(p.z for p in bord) / len(bord)
    pivot = Vector((sum(p.x for p in co_monde) / len(co_monde), -0.053, 0.740))
    m = Machoire(pivot, Vector((1.0, 0.0, 0.0)), z_levre=z_levre,
                 z_menton=0.6480, y_arriere=-0.060, z_bas_cou=0.6100)
    deltas = [m.deplacer(p, degres) for p in co_monde]
    return deltas, {"pivot": [round(x, 5) for x in pivot], "axe": [1, 0, 0],
                    "z_levre": round(z_levre, 5), "z_menton": 0.648,
                    "y_arriere": -0.060, "z_bas_cou": 0.610, "degres": degres}


# ---------------------------------------------------------- mesures ----

_BVH = {}


def bvh_globes():
    """Arbre de collision des DEUX scleres, telles qu'elles sont modelisees.

    On abandonne l'approximation par une sphere : la sclere porte un renflement
    corneen, l'ajustement laissait 0,6934 mm de residu sur 11,74 mm de rayon, et
    tout seuil de penetration bati dessus etait faux. Le globe, c'est le
    maillage du globe.
    """
    if _BVH: return _BVH
    for c in "LR":
        s = bpy.data.objects[TETE + ".sclera." + c]
        bm = bmesh.new(); bm.from_mesh(s.data)
        bm.transform(s.matrix_world)
        bm.verts.ensure_lookup_table()
        _BVH[c] = (BVHTree.FromBMesh(bm),
                   Vector([sum(v.co[i] for v in bm.verts) / len(bm.verts)
                           for i in range(3)]))
        bm.free()
    return _BVH


def dans_le_maillage(bvh, p, direction=Vector((0.0, 0.0, 1.0))):
    """Test d'appartenance par parite : un point interieur est traverse un
    nombre IMPAIR de fois par un rayon partant de lui."""
    n, o, eps = 0, p.copy(), 1e-6
    for _ in range(64):
        loc = bvh.ray_cast(o + direction * eps, direction, 10.0)[0]
        if loc is None: break
        n += 1
        o = loc
    return n % 2 == 1


def penetrations_maillage(co, ob, detail=False):
    """Sommets de peau reellement a l'interieur d'un globe.

    On SEPARE l'avant de l'arriere. L'arriere, c'est le fond de l'orbite : le
    maillage de la tete y traverse deja le globe dans l'asset livre, au neutre,
    et cela ne se voit pas. L'avant, c'est la paupiere : une penetration la est
    un defaut visible. Seul l'avant a valeur de seuil.
    """
    g = bvh_globes()
    av = ar = 0
    for bvh, ctr in g.values():
        for p in co:
            if (p - ctr).length >= 0.020: continue
            if dans_le_maillage(bvh, p):
                if (p - ctr).y < 0.0: av += 1
                else: ar += 1
    return {"anterieures": av, "posterieures": ar, "total": av + ar} if detail else av


def gap_ouverture(co, indices):
    """Hauteur de l'ouverture palpebrale, sur les sommets de bord publies en F0.

    On reprend la definition DEJA auditee (reports/f0/audit-topologie.json,
    `indices_peau` de chaque fente palpebrale) au lieu d'en inventer une
    nouvelle : colonne laterale par colonne laterale, l'ecart vertical entre le
    plus haut et le plus bas des sommets du bord.
    """
    pts = [co[i] for i in indices if i < len(co)]
    if len(pts) < 4: return None
    colonnes = {}
    for p in pts:
        colonnes.setdefault(round(p.x * 1000), []).append(p.z)
    ecarts = [max(v) - min(v) for v in colonnes.values() if len(v) > 1]
    return {
        # definition de F0 : hauteur de la boite englobante du bord
        "hauteur_bbox_mm": round((max(p.z for p in pts) - min(p.z for p in pts)) * MM, 4),
        # definition utile a la fermeture : le pire jour colonne par colonne
        "jour_max_colonne_mm": round(max(ecarts) * MM, 4) if ecarts else None,
        "sommets": len(pts),
    }


def gap_marges(co, ob, seuil=0.0018):
    """Jour entre marges palpebrales, mesure sur la surface REELLE du globe.

    La marge est la ligne de peau qui effleure le globe : distance au maillage
    de la sclere inferieure au seuil. Colonne par colonne, l'ecart vertical
    entre la marge haute et la marge basse.
    """
    g = bvh_globes()
    out = {}
    for cote, (bvh, ctr) in g.items():
        marge = []
        for p in co:
            if (p - ctr).length > 0.020: continue
            loc = bvh.find_nearest(p, 0.010)[0]
            if loc is not None and (p - loc).length <= seuil and (p - ctr).y < 0.0:
                marge.append(p)
        if len(marge) < 4: continue
        colonnes = {}
        for p in marge:
            colonnes.setdefault(round((p.x - ctr.x) * 1000), []).append(p.z)
        ecarts = [max(v) - min(v) for v in colonnes.values() if len(v) > 1]
        if ecarts: out[cote] = round(max(ecarts) * MM, 4)
    return out or None


def penetrations_globe(co, ob, marge=0.0):
    """Sommets de PEAU enfonces dans le globe, cote anterieur seulement.

    Compter sur toute la sphere revenait a compter le fond de l'orbite, qui est
    naturellement plus proche du centre que le rayon : 304 fausses penetrations
    au neutre. Seule la calotte anterieure — celle que la paupiere recouvre —
    a un sens ici.
    """
    g = repere_globes(ob)
    n = 0
    for ctr, R in g.values():
        n += sum(1 for p in co
                 if (p - ctr).y < -0.002 and (p - ctr).length < R - marge)
    return n


def gap_paupieres(co, ob):
    """Ecart entre les deux MARGES palpebrales, colonne par colonne.

    Premiere version : elle prenait tous les sommets a moins de 5,5 mm du globe,
    donc toute la paupiere et le pourtour de l'orbite, et rendait 22 a 28 mm —
    la hauteur de la region, pas le jour entre les marges. La marge, c'est la
    ligne qui EFFLEURE le globe : |distance au centre - rayon| minimal.
    """
    g = repere_globes(ob)
    par_oeil = {}
    for cote, (ctr, R) in g.items():
        marge = [p for p in co if abs((p - ctr).length - R) <= 0.0025
                 and (p - ctr).y < -0.004]
        if len(marge) < 4: continue
        colonnes = {}
        for p in marge:
            colonnes.setdefault(round((p.x - ctr.x) * 1000), []).append(p.z)
        ecarts = [max(v) - min(v) for v in colonnes.values() if len(v) > 1]
        if ecarts:
            par_oeil[cote] = round(max(ecarts) * MM, 4)
    return par_oeil or None


def gap_levres(co, infos):
    z = infos["z_contact"]; cx = infos["centre_x"]; demi = infos["demi_largeur_mm"] / MM
    haut = [p for p in co if cx - demi * 0.7 < p.x < cx + demi * 0.7
            and 0.0 < p.z - z < 0.010 and p.y < -0.130]
    bas = [p for p in co if cx - demi * 0.7 < p.x < cx + demi * 0.7
           and 0.0 < z - p.z < 0.010 and p.y < -0.130]
    if not haut or not bas: return None
    colonnes = {}
    for p in haut: colonnes.setdefault(round(p.x * 1000), [None, None])[0] = p.z
    for p in bas:
        c = colonnes.setdefault(round(p.x * 1000), [None, None])
        c[1] = p.z if c[1] is None else max(c[1], p.z)
    g = [a - b for a, b in colonnes.values() if a is not None and b is not None]
    return stats([x * MM for x in g]) if g else None


def etirement(co, aretes, ref):
    r = []
    for a, b in aretes:
        l0 = (ref[a] - ref[b]).length
        if l0 > 1e-9: r.append((co[a] - co[b]).length / l0)
    return stats(r)


# ------------------------------------------------------------- banc ----

if __name__ == "__main__":
    reg = Registre("f0-multires-v2")
    _f0 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "reports", "f0", "audit-topologie.json"),
                         encoding="utf-8"))
    # `indices` = TOUS les sommets du bord (peau + muqueuse), c'est sur cet
    # ensemble que F0 a publie `hauteur_mm`. `indices_peau` en est un
    # sous-ensemble et donnerait un autre nombre : comparer a 18,38 mm exigeait
    # de reprendre exactement le meme ensemble.
    BORDS = {a["nom"].split(".")[1]: a["indices"] for a in _f0["ouvertures"]
             if (a.get("nom") or "").startswith("fente_palpebrale")}
    BORD_LEVRES = next(a["indices"] for a in _f0["ouvertures"]
                       if a.get("nom") == "fente_labiale")
    R = {"fichier": os.path.basename(BLEND), "blender": bpy.app.version_string}

    # --- surface neutre evaluee, commune aux deux voies ---
    ob = ouvrir()
    co_ev, taille_ev, uv_ev = evaluer(ob)
    co_cage = [ob.matrix_world @ v.co for v in ob.data.vertices]
    R["neutre"] = {"cage_sommets": len(co_cage), "evalue": {
        "sommets": taille_ev[0], "faces": taille_ev[1], "loops": taille_ev[2]},
        "sha_uv_evalue": uv_ev}
    aretes_cage = [(e.vertices[0], e.vertices[1]) for e in ob.data.edges]
    faces_cage = [tuple(p.vertices) for p in ob.data.polygons]
    vol_ref = volume(co_cage, faces_cage)

    # --- les sondes de mesure, verifiees sur le neutre AVANT tout verdict ---
    # F0 a publie la hauteur des fentes palpebrales : 18,38 mm a gauche,
    # 16,34 mm a droite. Si la sonde de jour ne les retrouve pas au neutre,
    # elle ne mesure pas ce qu'elle pretend et aucun verdict n'est publie.
    # la sonde de sphere, verifiee sur une sphere connue
    import numpy as _np
    _c0, _r0 = Vector((1.5, -0.2, 0.8)), 0.0117
    _ech = [_c0 + Vector((math.sin(a) * math.cos(b), math.sin(a) * math.sin(b),
                          math.cos(a))) * _r0
            for a in [0.4, 0.9, 1.4, 1.9] for b in [0.0, 1.1, 2.2, 3.3, 4.4, 5.5]]
    _cf, _rf, _re = ajuster_sphere(_ech)
    reg.exige("sonde.sphere.rayon_connu", "ajustement sur une calotte de rayon connu",
              "24 points sur une sphere de 11,7 mm", round(_r0 * MM, 4),
              round(_rf * MM, 4), abs(_rf - _r0) < 1e-6, tolerance=1e-6)
    reg.exige("sonde.sphere.centre_connu", "centre retrouve", "meme calotte",
              [round(x, 6) for x in _c0], [round(x, 6) for x in _cf],
              (_cf - _c0).length < 1e-6)
    _bg = bvh_globes()
    _bvhL, _ctrL = _bg["L"]
    reg.exige("sonde.appartenance.centre_dedans", "le centre du globe est interieur",
              "maillage de la sclere gauche", True, dans_le_maillage(_bvhL, _ctrL),
              dans_le_maillage(_bvhL, _ctrL))
    _loin = _ctrL + Vector((0.0, -0.30, 0.0))
    reg.exige("sonde.appartenance.loin_dehors", "un point a 300 mm est exterieur",
              "maillage de la sclere gauche", False, dans_le_maillage(_bvhL, _loin),
              not dans_le_maillage(_bvhL, _loin))
    _g = repere_globes(ob)
    R["neutre"]["globes"] = {k: {"centre": [round(x, 6) for x in v[0]],
                                 "rayon_mm": round(v[1] * MM, 4)} for k, v in _g.items()}
    R["neutre"]["globes"]["residus_ajustement_mm"] = _GLOBES.get("_residus")
    gap0 = {c: gap_ouverture(co_cage, BORDS[c]) for c in BORDS}
    R["neutre"]["gap_ouverture_mm"] = gap0
    for cote, attendu in (("L", 18.38), ("R", 16.34)):
        obtenu = (gap0.get(cote) or {}).get("hauteur_bbox_mm")
        reg.exige("sonde.gap_ouverture.%s" % cote,
                  "la sonde retrouve EXACTEMENT la fente publiee en F0",
                  "cage NEUTRE, indices de bord de reports/f0", attendu, obtenu,
                  obtenu is not None and abs(obtenu - attendu) <= 0.02, tolerance=0.02)
    BORDS_TOUS = dict(BORDS); BORDS_TOUS["LEVRES"] = BORD_LEVRES
    _, infos0 = proto_levres(co_ev, ob, 0.0, BORDS_TOUS, co_cage)
    gl0 = gap_ouverture(co_cage, BORD_LEVRES)
    R["neutre"]["gap_levres_mm"] = gl0
    # Au neutre la bouche de cet asset porte deja une fente de contact : on la
    # MESURE et on s'en sert de reference, au lieu de poser un seuil absolu
    # invente. La fermeture devra la reduire, c'est le critere qui a un sens.
    reg.exige("sonde.gap_levres.neutre_mesure",
              "la sonde rend une valeur finie au neutre",
              "maillage NEUTRE", "valeur finie",
              gl0["jour_max_colonne_mm"] if gl0 else None, gl0 is not None)
    pen0 = penetrations_maillage(co_ev, ob, detail=True)
    R["neutre"]["penetrations_globe"] = pen0
    # L'asset LIVRE intersecte deja ses propres globes au neutre. Ce n'est pas
    # une faute de sonde — le test d'appartenance est verifie juste au-dessus —
    # c'est une propriete mesuree du maillage. Le seuil « zero penetration »
    # serait donc impossible a tenir par construction. Le critere honnete est
    # DIFFERENTIEL : la deformation ne doit pas en creer de nouvelles.
    reg.exige("sonde.penetration.mesuree_au_neutre",
              "la sonde rend une valeur exploitable au neutre",
              "maillage NEUTRE, test d'appartenance verifie", "valeur finie",
              pen0, isinstance(pen0.get("anterieures"), int))
    R["neutre"]["note_penetration"] = (
        "L'asset livre intersecte deja ses globes au neutre : %d sommets "
        "anterieurs et %d posterieurs sont a l'interieur d'une sclere. Le seuil "
        "du cahier (0 penetration) est donc inatteignable par construction sur "
        "cette source ; le critere applique est differentiel — le clignement ne "
        "doit pas en ajouter." % (pen0["anterieures"], pen0["posterieures"]))
    PEN_REF = pen0["anterieures"]
    if reg.echecs:
        R["registre"] = reg.bilan()
        R["conclusion"] = "SONDES DE MESURE NON VERIFIEES — aucun verdict anatomique"
        os.makedirs(os.path.dirname(SORTIE) or ".", exist_ok=True)
        json.dump(R, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("SONDES NON VERIFIEES : aucun verdict publie."); reg.conclure(); sys.exit(2)

    PROTOS = [
        ("clignement", proto_clignement, [0.25, 0.50, 1.00]),
        ("fermeture_labiale", proto_levres, [0.25, 0.50, 1.00]),
        ("ouverture_machoire", proto_machoire, [0.0, 5.0, 10.0, 20.0, 32.0]),
    ]
    R["prototypes"] = {}

    for nom, fabrique, intensites in PROTOS:
        R["prototypes"][nom] = {"voies": {}}
        for voie in ("A_cage", "B_haute_resolution"):
            ob = ouvrir()
            cible, co_base = (voie_A(ob) if voie == "A_cage" else voie_B(ob))
            uv_avant = sha_uv(cible.data)
            fiche = {"points_de_controle": len(cible.data.vertices),
                     "sha_uv_avant": uv_avant, "intensites": {}}
            _, _, uv_ev0 = evaluer(cible)
            ref, taille_ref, _ = evaluer(cible)

            for it in intensites:
                deltas, infos = fabrique(co_base, ob, it, BORDS_TOUS, co_cage)
                k, touches = poser_shape_key(cible, deltas, "PROTO")
                uv_apres = sha_uv(cible.data)
                co1, taille1, uv_eval = evaluer(cible)
                # retour au neutre
                k.value = 0.0
                co0, _, _ = evaluer(cible)
                k.value = 1.0
                mes = {
                    "points_deplaces": touches,
                    "repere": infos,
                    "amplitude_mm": ecart_indice(co1, ref),
                    "retour_au_neutre_mm": ecart_indice(co0, ref),
                    "penetrations_globe": penetrations_maillage(co1, ob, detail=True),
                    "variation_volume_pct": None,
                    "sha_uv_apres_shape_key": uv_apres,
                    "sha_uv_evalue_neutre": uv_ev0,
                    "sha_uv_evalue_deforme": uv_eval,
                    # Deux comparaisons, chacune sur UN SEUL maillage :
                    #  - la cage avant / apres pose de la shape key ;
                    #  - l'evalue au neutre / l'evalue deforme.
                    # Comparer la cage a l'evalue n'a aucun sens : le multires
                    # cree des loops, les deux tables n'ont pas la meme taille.
                    "uv_cage_inchangee": (uv_avant == uv_apres),
                    "uv_evaluee_inchangee": (uv_ev0 == uv_eval),
                    "uv_inchangee": (uv_avant == uv_apres and uv_ev0 == uv_eval),
                }
                if voie == "A_cage":
                    co_c = [cible.matrix_world @ d.co for d in
                            cible.data.shape_keys.key_blocks["PROTO"].data]
                    mes["variation_volume_pct"] = round(
                        (volume(co_c, faces_cage) / vol_ref - 1.0) * 100, 5)
                    mes["etirement_aretes"] = etirement(co_c, aretes_cage, co_cage)
                if nom == "clignement" and voie == "A_cage":
                    co_c = [cible.matrix_world @ d.co for d in
                            cible.data.shape_keys.key_blocks["PROTO"].data]
                    mes["gap_ouverture_mm"] = {c: gap_ouverture(co_c, BORDS[c])
                                               for c in BORDS}
                if nom == "fermeture_labiale" and voie == "A_cage":
                    co_c = [cible.matrix_world @ d.co for d in
                            cible.data.shape_keys.key_blocks["PROTO"].data]
                    mes["gap_levres_mm"] = gap_ouverture(co_c, BORD_LEVRES)
                fiche["intensites"][str(it)] = mes
                # retirer la shape key avant l'intensite suivante
                cible.shape_key_remove(cible.data.shape_keys.key_blocks["PROTO"])

            # --- temps : 5 echauffements, 20 mesures ---
            deltas, _ = fabrique(co_base, ob, intensites[-1], BORDS_TOUS, co_cage)
            k, _ = poser_shape_key(cible, deltas, "PROTO")
            for _ in range(5): evaluer(cible)
            ts = []
            for _ in range(20):
                t0 = time.perf_counter(); evaluer(cible); ts.append(time.perf_counter() - t0)
            fiche["temps_s"] = stats(ts)
            fiche["memoire"] = {
                "sommets": len(cible.data.vertices),
                "octets_shape_key_theorique": len(cible.data.vertices) * 12,
            }
            # taille reelle d'un .blend compresse Basis + une shape key
            tmp = os.path.join(tempfile.mkdtemp(prefix="atlas-banc-"), "b.blend")
            bpy.ops.wm.save_as_mainfile(filepath=tmp, compress=True, copy=True)
            fiche["memoire"]["octets_blend_compresse"] = os.path.getsize(tmp)
            os.remove(tmp); os.rmdir(os.path.dirname(tmp))
            R["prototypes"][nom]["voies"][voie] = fiche
            print("  %-20s %-20s ctrl=%5d  temps med=%.4fs  blend=%d o"
                  % (nom, voie, fiche["points_de_controle"], fiche["temps_s"]["median"],
                     fiche["memoire"]["octets_blend_compresse"]))

    # ---------------------------------------------------- seuils ----
    for nom in ("clignement", "fermeture_labiale"):
        for voie, f in R["prototypes"][nom]["voies"].items():
            plein = f["intensites"]["1.0"]
            reg.exige("%s.%s.retour_neutre" % (nom, voie),
                      "commande a 0 apres un geste a 100 %",
                      "prototype anatomique, intensite 1,0", "<= 0,01 mm",
                      plein["retour_au_neutre_mm"]["max"],
                      plein["retour_au_neutre_mm"]["max"] <= 0.01, tolerance=0.01)
            reg.exige("%s.%s.uv_intacte" % (nom, voie),
                      "SHA-256 des UV avant / apres shape key / apres evaluation",
                      "meme topologie", "identiques", plein["uv_inchangee"],
                      bool(plein["uv_inchangee"]))
    for voie, f in R["prototypes"]["clignement"]["voies"].items():
        plein = f["intensites"]["1.0"]
        av = plein["penetrations_globe"]["anterieures"]
        reg.exige("clignement.%s.penetration_sans_aggravation" % voie,
                  "le clignement n'ajoute aucune penetration anterieure",
                  "neutre a %d penetrations anterieures" % PEN_REF,
                  "<= %d" % PEN_REF, av, av <= PEN_REF)
        g = plein.get("gap_ouverture_mm")
        if g is None:
            reg.saute("clignement.%s.gap" % voie, "jour restant a 100 %",
                      "mesure definie sur la cage seulement")
        else:
            ref = R["neutre"]["gap_ouverture_mm"]
            for c in sorted(g):
                v = (g[c] or {}).get("jour_max_colonne_mm")
                r0 = (ref[c] or {}).get("jour_max_colonne_mm")
                reg.exige("clignement.%s.gap_ferme_%s" % (voie, c),
                          "le clignement referme l'ouverture publiee en F0",
                          "neutre a %.3f mm" % r0, "<= 0,20 mm", v,
                          v is not None and v <= 0.20, tolerance=0.20)
    for voie, f in R["prototypes"]["fermeture_labiale"]["voies"].items():
        g = f["intensites"]["1.0"].get("gap_levres_mm")
        if g is None:
            reg.saute("levres.%s.gap" % voie, "jour labial restant",
                      "mesure definie sur la cage seulement")
        else:
            ref = R["neutre"]["gap_levres_mm"]["jour_max_colonne_mm"]
            v = g["jour_max_colonne_mm"]
            reg.exige("levres.%s.gap_reduit" % voie,
                      "la fermeture reduit la fente mesuree au neutre",
                      "neutre a %.3f mm" % ref, "< %.3f mm" % ref, v, v < ref)
            reg.exige("levres.%s.gap_max" % voie,
                      "pire jour le long du bord publie en F0",
                      "fermeture a 100 %", "<= 0,30 mm", v, v <= 0.30,
                      tolerance=0.30)
    for voie, f in R["prototypes"]["ouverture_machoire"]["voies"].items():
        z = f["intensites"]["0.0"]
        reg.exige("machoire.%s.zero_degre_est_le_neutre" % voie,
                  "0 degre doit rendre exactement le neutre",
                  "mandibule a 0 degre", "<= 0,01 mm", z["amplitude_mm"]["max"],
                  z["amplitude_mm"]["max"] <= 0.01, tolerance=0.01)

    R["registre"] = reg.bilan()
    os.makedirs(os.path.dirname(SORTIE) or ".", exist_ok=True)
    json.dump(R, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("BANC_V2 ->", SORTIE, "|", "OK" if ok else "SEUILS NON SATISFAITS")
    # Le JSON disait ECHEC et le shell rendait 0 : les deux racontaient des
    # choses differentes. Aucun seuil n'est touche ici, seulement le code de
    # sortie. 2 = echec metier ; 1 reste l'echec technique de Blender.
    print("RESULTAT_FINAL", "OK" if ok else "ECHEC")
    sys.exit(0 if ok else 2)
