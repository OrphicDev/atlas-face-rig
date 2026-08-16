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

def proto_clignement(co_monde, ob, intensite):
    g = repere_globes(ob)
    lat = (g["L"][0] - g["R"][0]).normalized()
    deltas = [Vector((0, 0, 0)) for _ in co_monde]
    infos = {}
    for cote in "LR":
        ctr, R = g[cote]
        cl = Clignement(ctr, R, lat)
        conc = [p for p in co_monde if cl.concerne(p)]
        if not conc: continue
        cl.preparer(co_monde)
        for i, p in enumerate(co_monde):
            d = cl.deplacer(p, intensite)
            if d.length > 0: deltas[i] = deltas[i] + d
        infos[cote] = {"sommets_concernes": len(conc), "rayon_globe_mm": round(R * MM, 3),
                       "centre": [round(x, 5) for x in ctr]}
    return deltas, infos


def proto_levres(co_monde, ob, intensite):
    # la fente labiale, mesuree : bande la plus avancee entre 0,685 et 0,705 m
    bande = [p for p in co_monde if 0.686 <= p.z <= 0.703 and p.y < -0.130]
    cx = sum(p.x for p in bande) / len(bande)
    demi = (max(p.x for p in bande) - min(p.x for p in bande)) / 2.0
    z_contact = sum(p.z for p in bande) / len(bande)
    f = FermetureLabiale(Vector((cx, sum(p.y for p in bande) / len(bande), z_contact)),
                         demi, z_contact)
    deltas = [f.deplacer(p, intensite) for p in co_monde]
    return deltas, {"sommets_de_la_bande": len(bande), "demi_largeur_mm": round(demi * MM, 2),
                    "z_contact": round(z_contact, 5), "centre_x": round(cx, 5)}


def proto_machoire(co_monde, ob, degres):
    # axe temporo-mandibulaire : la ligne des deux conduits auditifs mesures
    pivot = Vector((sum(p.x for p in co_monde) / len(co_monde), -0.053, 0.740))
    axe = Vector((1.0, 0.0, 0.0))
    m = Machoire(pivot, axe, z_haut=0.7000, z_bas=0.6600)
    deltas = [m.deplacer(p, degres) for p in co_monde]
    return deltas, {"pivot": [round(x, 5) for x in pivot], "axe": [1, 0, 0],
                    "z_haut": 0.70, "z_bas": 0.66, "degres": degres}


# ---------------------------------------------------------- mesures ----

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
    _g = repere_globes(ob)
    R["neutre"]["globes"] = {k: {"centre": [round(x, 6) for x in v[0]],
                                 "rayon_mm": round(v[1] * MM, 4)} for k, v in _g.items()}
    R["neutre"]["globes"]["residus_ajustement_mm"] = _GLOBES.get("_residus")
    gap0 = gap_paupieres(co_ev, ob)
    R["neutre"]["gap_paupieres_mm"] = gap0
    for cote, attendu in (("L", 18.38), ("R", 16.34)):
        obtenu = (gap0 or {}).get(cote)
        reg.exige("sonde.gap_paupieres.%s" % cote,
                  "la sonde retrouve la fente mesuree en F0",
                  "maillage NEUTRE, fente publiee dans reports/f0", attendu, obtenu,
                  obtenu is not None and abs(obtenu - attendu) <= 2.5, tolerance=2.5)
    _, infos0 = proto_levres(co_ev, ob, 0.0)
    gl0 = gap_levres(co_ev, infos0)
    R["neutre"]["gap_levres_mm"] = gl0
    # Au neutre la bouche de cet asset porte deja une fente de contact : on la
    # MESURE et on s'en sert de reference, au lieu de poser un seuil absolu
    # invente. La fermeture devra la reduire, c'est le critere qui a un sens.
    reg.exige("sonde.gap_levres.neutre_mesure",
              "la sonde rend une valeur finie au neutre",
              "maillage NEUTRE", "valeur finie",
              gl0["median"] if gl0 else None, gl0 is not None)
    pen0 = penetrations_globe(co_ev, ob)
    R["neutre"]["penetrations_globe"] = pen0
    reg.exige("sonde.penetration.neutre_nulle",
              "au neutre aucun sommet n'est dans le globe",
              "maillage NEUTRE", 0, pen0, pen0 == 0)
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
                deltas, infos = fabrique(co_base, ob, it)
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
                    "penetrations_globe": penetrations_globe(co1, ob),
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
                if nom == "clignement":
                    mes["gap_paupieres_mm"] = gap_paupieres(co1, ob)
                if nom == "fermeture_labiale":
                    mes["gap_levres_mm"] = gap_levres(co1, infos)
                fiche["intensites"][str(it)] = mes
                # retirer la shape key avant l'intensite suivante
                cible.shape_key_remove(cible.data.shape_keys.key_blocks["PROTO"])

            # --- temps : 5 echauffements, 20 mesures ---
            deltas, _ = fabrique(co_base, ob, intensites[-1])
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
        reg.exige("clignement.%s.penetration" % voie, "aucun sommet dans le globe",
                  "clignement a 100 %", 0, plein["penetrations_globe"],
                  plein["penetrations_globe"] == 0)
        g = plein.get("gap_paupieres_mm")
        reg.exige("clignement.%s.gap" % voie, "jour restant entre les marges",
                  "clignement a 100 %", "<= 0,20 mm", g,
                  g is not None and g <= 0.20, tolerance=0.20)
    for voie, f in R["prototypes"]["fermeture_labiale"]["voies"].items():
        g = f["intensites"]["1.0"].get("gap_levres_mm")
        ref = R["neutre"]["gap_levres_mm"]["median"]
        reg.exige("levres.%s.gap_reduit" % voie,
                  "la fermeture reduit la fente mesuree au neutre",
                  "neutre a %.3f mm" % ref, "< %.3f mm" % ref,
                  g["median"] if g else None,
                  g is not None and g["median"] < ref)
        reg.exige("levres.%s.gap_max" % voie, "pire ecart le long de la couture",
                  "fermeture a 100 %", "<= 0,30 mm", g["max"] if g else None,
                  g is not None and g["max"] <= 0.30, tolerance=0.30)
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
