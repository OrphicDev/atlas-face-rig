"""F0.2 — le multires porte-t-il du sculpt, et cage contre maillage subdivise.

Deux mesures, chacune verifiee sur une configuration connue :

1. Le multires de niveau 1 deplace-t-il quoi que ce soit par rapport a une
   simple subdivision Catmull-Clark ? Si l'ecart est nul, il ne contient aucun
   detail et la question « cage ou subdivise » perd son enjeu de perte de
   sculpt.
2. Banc A/B sur trois prototypes jetables (clignement, fermeture labiale,
   ouverture de machoire) : shape key sur la cage puis subdivision, contre
   shape key sur le maillage subdivise.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-multires.py -- rapport.json
"""
import json, os, sys, time
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, kdtree

MM = 1000.0
ECHECS = []


def exige(c, libelle, attendu, obtenu):
    print("  [%s] %s | attendu %s | obtenu %s" % ("OK" if c else "ECHEC", libelle, attendu, obtenu))
    if not c: ECHECS.append({"sonde": libelle, "attendu": str(attendu), "obtenu": str(obtenu)})


def ecart_nuage(a, b):
    """Distance maximale d'un nuage a l'autre, dans les deux sens, en mm."""
    if not a or not b: return None
    ka = kdtree.KDTree(len(a))
    for i, c in enumerate(a): ka.insert(c, i)
    ka.balance()
    kb = kdtree.KDTree(len(b))
    for i, c in enumerate(b): kb.insert(c, i)
    kb.balance()
    return round(max(max(kb.find(c)[2] for c in a), max(ka.find(c)[2] for c in b)) * MM, 6)


def ecart_indice(a, b):
    """Ecart sommet a sommet (meme ordre), en mm : max, moyenne, mediane, p99."""
    if len(a) != len(b): return {"comparable": False, "n_a": len(a), "n_b": len(b)}
    d = sorted((x - y).length * MM for x, y in zip(a, b))
    return {"comparable": True, "max_mm": round(d[-1], 6),
            "moy_mm": round(sum(d) / len(d), 6), "median_mm": round(d[len(d) // 2], 6),
            "p99_mm": round(d[int(len(d) * 0.99)], 6),
            "sommets_hors_1um": sum(1 for x in d if x > 0.001)}


def sommets_evalues(ob):
    # En mode fond rien ne se reevalue tout seul : il faut marquer l'objet et
    # sa donnee, sinon on relit la meme evaluation qu'avant la modification.
    ob.data.update()
    ob.update_tag()
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    co = [ob.matrix_world @ v.co.copy() for v in me.vertices]
    n = (len(me.vertices), len(me.polygons))
    ev.to_mesh_clear()
    return co, n


def charger():
    PAQUET = os.environ["ATLAS_BASE_MESH"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = ["Head (Animation) - Realistic"]
    col = dst.collections[0]
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.update()
    return max([o for o in col.all_objects if o.type == "MESH"],
               key=lambda o: len(o.data.vertices))


def verifier():
    print("VERIFICATION DES SONDES")
    # ecart_nuage : identique -> 0 ; translate de 1 mm -> 1 mm
    a = [Vector((i * 0.01, 0, 0)) for i in range(50)]
    exige(ecart_nuage(a, [c.copy() for c in a]) == 0.0, "ecart_nuage : nuages identiques", 0.0,
          ecart_nuage(a, [c.copy() for c in a]))
    b = [c + Vector((0, 0, 0.001)) for c in a]
    exige(abs(ecart_nuage(a, b) - 1.0) < 1e-6, "ecart_nuage : translation de 1 mm", 1.0,
          ecart_nuage(a, b))
    # un nuage plus dense d'un cote ne doit pas passer pour identique
    exige(ecart_nuage(a, a[::2]) > 0.0, "ecart_nuage : nuages de tailles differentes",
          "> 0", ecart_nuage(a, a[::2]))
    # sommets_evalues doit VOIR un modificateur : cube nu vs cube subdivise
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add()
    cu = bpy.context.active_object
    n0 = sommets_evalues(cu)[1]
    m = cu.modifiers.new("S", "SUBSURF"); m.levels = 1
    n1 = sommets_evalues(cu)[1]
    exige(n0 == (8, 6) and n1 == (26, 24), "sommets_evalues : voit la subdivision",
          "(8,6) puis (26,24)", "%s puis %s" % (n0, n1))
    print("VERIFICATION %s (%d echec(s))" % ("OK" if not ECHECS else "ECHOUEE", len(ECHECS)))
    return not ECHECS


def mesurer():
    R = {}
    tete = charger()
    mres = [m for m in tete.modifiers if m.type == "MULTIRES"]
    R["multires"] = [{"nom": m.name, "levels": m.levels, "sculpt_levels": m.sculpt_levels,
                      "render_levels": m.render_levels, "total_levels": m.total_levels}
                     for m in mres]
    R["cage"] = {"sommets": len(tete.data.vertices), "faces": len(tete.data.polygons)}

    # --- 1. multires contre subdivision simple ---
    co_mres, n_mres = sommets_evalues(tete)
    R["multires_evalue"] = {"sommets": n_mres[0], "faces": n_mres[1]}

    # Le multires evalue sur la SURFACE LIMITE ; une subdivision en raffinement
    # simple donnerait un ecart qui ne serait pas du sculpt mais un changement
    # de schema. On compare donc aux deux, sinon la conclusion est fausse.
    tmp = tete.data.copy()
    jum = bpy.data.objects.new("JUMEAU", tmp)
    jum.matrix_world = tete.matrix_world.copy()
    bpy.context.scene.collection.objects.link(jum)
    s = jum.modifiers.new("S", "SUBSURF")
    s.levels = mres[0].levels if mres else 1
    s.render_levels = s.levels
    R["comparaisons"] = {}
    for etiquette, limite in (("raffinement_simple", False), ("surface_limite", True)):
        s.use_limit_surface = limite
        co_s, n_s = sommets_evalues(jum)
        R["comparaisons"][etiquette] = {
            "sommets": n_s[0], "faces": n_s[1],
            "par_indice": ecart_indice(co_mres, co_s),
            "hausdorff_mm": ecart_nuage(co_mres, co_s),
        }
    s.use_limit_surface = False
    co_sub, n_sub = sommets_evalues(jum)
    R["subdivision_evaluee"] = {"sommets": n_sub[0], "faces": n_sub[1]}
    meilleur = min(R["comparaisons"].values(), key=lambda d: d["par_indice"]["max_mm"])
    R["multires_porte_du_sculpt"] = meilleur["par_indice"]["max_mm"] > 0.001
    R["schema_qui_reproduit_le_multires"] = min(
        R["comparaisons"], key=lambda k: R["comparaisons"][k]["par_indice"]["max_mm"])

    # Contre-epreuve : on decale volontairement le jumeau de 1,000 mm. Si la
    # sonde ne voit pas ce millimetre, elle ne mesure pas son entree.
    dz = 0.001 / tete.scale[2]
    for v in tmp.vertices: v.co.z += dz
    co_sub2, _ = sommets_evalues(jum)
    R["contre_epreuve"] = {
        "decalage_impose_mm": 1.0,
        "vu_par_indice": ecart_indice(co_sub, co_sub2),
        "vs_multires_par_indice": ecart_indice(co_mres, co_sub2),
    }
    bpy.data.objects.remove(jum, do_unlink=True)

    # --- 2. banc A/B sur trois prototypes jetables ---
    tete_w = tete.matrix_world
    co_w = [tete_w @ v.co for v in tete.data.vertices]
    axe = (min(c.x for c in co_w) + max(c.x for c in co_w)) / 2
    reperes = {
        "clignement": (Vector((axe + 0.0343, -0.1306, 0.7653)), 0.011, Vector((0, 0, -1))),
        "fermeture_labiale": (Vector((axe, -0.1459, 0.6942)), 0.010, Vector((0, 0, 1))),
        "ouverture_machoire": (Vector((axe, -0.1459, 0.6942)), 0.045, Vector((0, 0, -1))),
    }
    AMPL = 0.004  # 4 mm, meme geste dans les deux voies

    def poser(ob, centre, rayon, direction, sur_cage):
        """Ajoute une shape key a bourrelet cosinus. Renvoie les sommets evalues."""
        me = ob.data
        if not me.shape_keys: ob.shape_key_add(name="Basis", from_mix=False)
        k = ob.shape_key_add(name="TEST", from_mix=False)
        M = ob.matrix_world
        touches = 0
        for i, p in enumerate(k.data):
            w = M @ p.co
            d = (w - centre).length
            if d < rayon:
                import math
                f = 0.5 * (1 + math.cos(math.pi * d / rayon))
                p.co = p.co + (M.inverted().to_3x3() @ (direction * (AMPL * f)))
                touches += 1
        k.value = 1.0
        bpy.context.view_layer.update()
        return touches

    # reference neutre calculee UNE fois : chaque `charger()` remet la scene a
    # zero et invaliderait tout objet garde d'avant.
    neutre = charger()
    for m in list(neutre.modifiers):
        if m.type == "MULTIRES": neutre.modifiers.remove(m)
    mo2 = neutre.modifiers.new("S", "SUBSURF"); mo2.levels = 1; mo2.use_limit_surface = False
    co_ref, _ = sommets_evalues(neutre)

    R["bancs"] = {}
    for nom, (centre, rayon, direction) in reperes.items():
        fiche = {}
        for voie in ("cage_puis_subdivision", "sur_maillage_subdivise"):
            t0 = time.perf_counter()
            ob = charger()
            for m in list(ob.modifiers):
                if m.type == "MULTIRES": ob.modifiers.remove(m)
            if voie == "sur_maillage_subdivise":
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                mo = ob.modifiers.new("S", "SUBSURF"); mo.levels = 1; mo.use_limit_surface = False
                bpy.ops.object.modifier_apply(modifier=mo.name)
            n = poser(ob, centre, rayon, direction, voie.startswith("cage"))
            if voie == "cage_puis_subdivision":
                mo = ob.modifiers.new("S", "SUBSURF"); mo.levels = 1; mo.use_limit_surface = False
            co1, taille = sommets_evalues(ob)
            # retour au neutre : la commande a 0 doit rendre exactement le repos
            ob.data.shape_keys.key_blocks["TEST"].value = 0.0
            bpy.context.view_layer.update()
            co0, _ = sommets_evalues(ob)
            fiche[voie] = {
                "points_de_controle_deplaces": n,
                "points_de_controle_total": len(ob.data.vertices),
                "octets_de_la_shape_key": len(ob.data.vertices) * 12,
                "sommets_evalues": taille[0], "faces_evaluees": taille[1],
                "amplitude_obtenue_mm": ecart_indice(co1, co_ref),
                "retour_au_neutre_mm": ecart_indice(co0, co_ref),
                "secondes": round(time.perf_counter() - t0, 2),
                "uv_conservee": bool(ob.data.uv_layers),
            }
        R["bancs"][nom] = fiche
    return R


if __name__ == "__main__":
    sortie = sys.argv[sys.argv.index("--") + 1]
    if not verifier():
        json.dump({"verification": "ECHEC", "echecs": ECHECS}, open(sortie, "w"), indent=2)
        print("SONDES NON VERIFIEES : aucun chiffre publie."); sys.exit(2)
    R = mesurer(); R["verification_des_sondes"] = "OK"
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("MULTIRES_OK ->", sortie)
