"""F0-D.8 bis — banc a REPONSE CONNUE des mesures de raccord.

L'asset corps de 49 Mo n'est pas sur cette machine : `EXP_body_target` ne peut
pas etre construit, donc ni la contre-epreuve Surface Deform ni l'essai de
remplacement ne peuvent tourner sur le vrai maillage. Ce n'est pas une raison
pour livrer du code jamais execute.

Ce banc fabrique une paire tete/corps SYNTHETIQUE dont la deformation exacte
est connue d'avance, puis exige que chaque mesure du module commun retrouve
cette reponse — au micron, et au compte pres pour les fautes injectees :
un trou, une arete non manifold, une face inversee, une auto-intersection,
des sommets doubles.

Quand l'asset revient, il ne reste plus qu'a le brancher : la regle de mesure,
elle, est deja verifiee.

    blender -b --factory-startup --python-exit-code 1 \
      --python tests/f0-body-banc-synthetique.py -- \
      --report reports/f0-final/body-banc-synthetique.json
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, Matrix

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "bc", os.path.join(RACINE, "rig", "f0_body_commun.py"))
BC = importlib.util.module_from_spec(_s); _s.loader.exec_module(BC)
MM = 1000.0
LEVEE_M = 0.003          # 3,000 mm : la reponse connue
RAYON_M = 0.030


def grille(nom, n, taille, z=0.0):
    """Grille reguliere n x n de cote `taille`, centree sur l'origine."""
    me = bpy.data.meshes.new(nom)
    verts, faces = [], []
    pas = taille / (n - 1)
    for j in range(n):
        for i in range(n):
            verts.append((-taille / 2 + i * pas, -taille / 2 + j * pas, z))
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    me.from_pydata(verts, [], faces)
    me.update()
    me.uv_layers.new(name="UVMap")
    ob = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reg = Registre("body-banc-synthetique")
    R = {"levee_connue_mm": LEVEE_M * MM, "rayon_m": RAYON_M}

    tete = grille("EXP_head_source", 21, 0.120, z=0.0)
    corps = grille("EXP_body_target", 41, 0.200, z=0.0)

    # --- le masque : sommets du corps sous la tete, poids 1 puis 0 net
    # Le compte attendu est DERIVE de la grille, pas tape a la main : ecrit
    # 441 de tete, j'obtenais 361 — la rangee de bord tombe a -0,050000001 en
    # simple precision et sortait du masque. Un nombre suppose contre un nombre
    # mesure, c'est la faute que ce banc est cense attraper.
    EPS = 1e-6
    masque = {}
    for i, v in enumerate(corps.data.vertices):
        p = corps.matrix_world @ v.co
        masque[i] = 1.0 if max(abs(p.x), abs(p.y)) <= 0.050 + EPS else 0.0
    pleins = sum(1 for x in masque.values() if x > 0)
    pas = 0.200 / 40
    par_axe = sum(1 for k in range(41)
                  if abs(-0.100 + k * pas) <= 0.050 + EPS)
    attendu = par_axe * par_axe
    reg.exige("banc.masque", "le masque couvre la part DERIVEE de la grille",
              "%d sommets par axe" % par_axe, attendu, pleins, pleins == attendu)

    # --- la carte, construite par le module COMMUN
    Wt = [tete.matrix_world @ v.co for v in tete.data.vertices]
    Wb = [corps.matrix_world @ v.co for v in corps.data.vertices]
    arbre, tris = BC.triangles_et_bvh(tete.data, tete.matrix_world)
    carte, info = BC.construire_carte(Wt, arbre, tris, Wb, masque)
    reg.exige("banc.carte_sans_rejet", "chaque sommet masque trouve son triangle",
              "%d sommets masques" % pleins, 0, info["rejets"], info["rejets"] == 0)
    reg.exige("banc.barycentriques", "les poids somment a 1 apres normalisation",
              "%d entrees" % len(carte), "< 1e-9",
              round(max(abs(sum(e["bary"]) - 1.0) for e in carte.values()), 12),
              max(abs(sum(e["bary"]) - 1.0) for e in carte.values()) < 1e-9)

    # --- LA REPONSE CONNUE : on leve un disque de la tete de 3,000 mm exactement
    dep_source = {}
    for i, p in enumerate(Wt):
        if math.hypot(p.x, p.y) <= RAYON_M:
            dep_source[i] = Vector((0.0, 0.0, LEVEE_M))
    reg.exige("banc.source_levee", "la source est levee de la valeur connue",
              "%d sommets de la tete" % len(dep_source), LEVEE_M * MM,
              round(max(v.length for v in dep_source.values()) * MM, 9),
              # 1e-9 m, pas 1e-12 : les Vector de Blender sont en simple
              # precision, 0,003 y vaut 0,0030000000261. Une tolerance sous la
              # resolution du format mesure le format, pas la levee.
              abs(max(v.length for v in dep_source.values()) - LEVEE_M) < 1e-9,
              tolerance=1e-9)

    # --- voie barycentrique
    with BC.Chrono() as c:
        dep_cible = BC.appliquer_carte(carte, dep_source)
    ref = [v.co.copy() for v in corps.data.vertices]
    cour = [ref[i] + dep_cible.get(i, Vector((0, 0, 0)))
            for i in range(len(ref))]
    for i, v in enumerate(corps.data.vertices):
        v.co = cour[i]
    corps.data.update()
    bilan = BC.bilan_methode("barycentrique", ref, cour,
                             {i for i, w in masque.items() if w > 0}, corps,
                             c.duree)
    R["barycentrique"] = bilan

    # au CENTRE du disque, le transfert doit rendre la levee exacte
    centre = min(range(len(ref)), key=lambda i: ref[i].length)
    leve_centre = (cour[centre] - ref[centre]).length * MM
    reg.exige("banc.levee_transferee",
              "au centre, le transfert rend la levee connue",
              "sommet du corps le plus proche de l'origine", LEVEE_M * MM,
              round(leve_centre, 6), abs(leve_centre - LEVEE_M * MM) <= 1e-4,
              tolerance=1e-4)
    reg.exige("banc.max_dans_le_masque", "le maximum vaut la levee connue",
              "%d sommets" % bilan["sommets_masque"], LEVEE_M * MM,
              bilan["deplacement_dans_le_masque_mm"]["max"],
              abs(bilan["deplacement_dans_le_masque_mm"]["max"]
                  - LEVEE_M * MM) <= 1e-4, tolerance=1e-4)
    reg.exige("banc.hors_masque_nul", "aucun sommet hors masque ne bouge",
              "%d sommets" % bilan["sommets_hors_masque"], 0.0,
              bilan["deplacement_hors_masque_mm"]["max"],
              bilan["deplacement_hors_masque_mm"]["max"] == 0.0)

    # --- voie SURFACE DEFORM, sur la meme paire et la meme reponse connue.
    # Le modificateur, lui, ne depend pas de l'asset : la METHODE de F0-D.8 est
    # donc exercee pour de vrai ici, et seul le maillage reel manquera.
    for i, v in enumerate(corps.data.vertices):      # on remet le corps au neutre
        v.co = ref[i]
    corps.data.update()
    corps2 = corps.copy(); corps2.data = corps.data.copy()
    corps2.name = "EXP_body_target_SD"
    bpy.context.scene.collection.objects.link(corps2)
    g = corps2.vertex_groups.new(name="VG_F0_FACE_TRANSFER")
    g.add([i for i, w in masque.items() if w > 0], 1.0, "REPLACE")
    sd = corps2.modifiers.new("SurfaceDeform", "SURFACE_DEFORM")
    sd.target = tete
    sd.vertex_group = "VG_F0_FACE_TRANSFER"
    bpy.context.view_layer.objects.active = corps2
    bpy.ops.object.surfacedeform_bind(modifier=sd.name)
    reg.exige("banc.sd_bind", "Surface Deform s'est lie au neutre",
              "cible %s, groupe %s" % (tete.name, sd.vertex_group), True,
              bool(sd.is_bound), bool(sd.is_bound))

    with BC.Chrono() as c2:
        for i, v in enumerate(tete.data.vertices):   # on joue la MEME pose
            v.co = Wt[i] + dep_source.get(i, Vector((0, 0, 0)))
        tete.data.update(); tete.update_tag()
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = corps2.evaluated_get(dg)
        me_ev = ev.to_mesh()
        cour_sd = [v.co.copy() for v in me_ev.vertices]
        ev.to_mesh_clear()
    for i, v in enumerate(corps2.data.vertices):
        v.co = cour_sd[i]
    corps2.modifiers.remove(sd)
    corps2.data.update()
    bilan_sd = BC.bilan_methode("surface_deform", ref, cour_sd,
                                {i for i, w in masque.items() if w > 0},
                                corps2, c2.duree)
    R["surface_deform"] = bilan_sd
    reg.exige("banc.sd_max_dans_le_masque",
              "Surface Deform rend lui aussi la levee connue",
              "%d sommets" % bilan_sd["sommets_masque"], LEVEE_M * MM,
              bilan_sd["deplacement_dans_le_masque_mm"]["max"],
              abs(bilan_sd["deplacement_dans_le_masque_mm"]["max"]
                  - LEVEE_M * MM) <= 0.05, tolerance=0.05)
    reg.exige("banc.sd_hors_masque_nul",
              "Surface Deform ne bouge rien hors du groupe",
              "%d sommets" % bilan_sd["sommets_hors_masque"], "<= 0,01 mm",
              bilan_sd["deplacement_hors_masque_mm"]["max"],
              bilan_sd["deplacement_hors_masque_mm"]["max"] <= 0.01,
              tolerance=0.01)
    ecart = abs(bilan["deplacement_dans_le_masque_mm"]["max"]
                - bilan_sd["deplacement_dans_le_masque_mm"]["max"])
    R["ecart_des_deux_voies_mm"] = round(ecart, 6)
    reg.exige("banc.deux_voies_comparables",
              "les deux voies mesurent la meme levee a 0,05 mm",
              "barycentrique contre Surface Deform", "<= 0,05 mm",
              round(ecart, 6), ecart <= 0.05, tolerance=0.05)
    # on remet le corps deforme pour ne pas fausser les sondes suivantes
    for i, v in enumerate(corps.data.vertices):
        v.co = cour[i]
    corps.data.update()

    # --- les sondes de topologie, chacune contre une faute INJECTEE
    def neuf(nom):
        ob = grille(nom, 11, 0.100)
        return ob

    t = neuf("EXP_trou")
    bm = bmesh.new(); bm.from_mesh(t.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[45]], context="FACES")
    bm.to_mesh(t.data); bm.free(); t.data.update()
    ouvertes_saines = BC.aretes_ouvertes(neuf("EXP_saine").data)
    reg.exige("banc.aretes_ouvertes", "un trou d'une face ajoute 4 aretes ouvertes",
              "grille 11 x 11, une face retiree", ouvertes_saines + 4,
              BC.aretes_ouvertes(t.data),
              BC.aretes_ouvertes(t.data) == ouvertes_saines + 4)

    nm = neuf("EXP_non_manifold")
    bm = bmesh.new(); bm.from_mesh(nm.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    e = bm.edges[40]
    v3 = bm.verts.new(e.verts[0].co + Vector((0, 0, 0.01)))
    bm.faces.new((e.verts[0], e.verts[1], v3))
    bm.to_mesh(nm.data); bm.free(); nm.data.update()
    reg.exige("banc.non_manifold", "une face en aileron cree une arete a 3 faces",
              "grille 11 x 11 + 1 triangle", 1, BC.aretes_non_manifold(nm.data),
              BC.aretes_non_manifold(nm.data) == 1)

    inv = neuf("EXP_inversee")
    bm = bmesh.new(); bm.from_mesh(inv.data); bm.faces.ensure_lookup_table()
    bmesh.ops.reverse_faces(bm, faces=[bm.faces[10], bm.faces[11]])
    bm.to_mesh(inv.data); bm.free(); inv.data.update()
    reg.exige("banc.faces_inversees", "deux faces retournees sont comptees deux fois",
              "grille 11 x 11", 2, BC.faces_inversees(inv.data),
              BC.faces_inversees(inv.data) == 2)

    dbl = neuf("EXP_double")
    bm = bmesh.new(); bm.from_mesh(dbl.data); bm.verts.ensure_lookup_table()
    origines = [bm.verts[k].co.copy() for k in range(5)]
    for co5 in origines:
        bm.verts.new(co5)
    bm.to_mesh(dbl.data); bm.free(); dbl.data.update()
    reg.exige("banc.sommets_doubles", "cinq sommets confondus sont comptes cinq fois",
              "grille 11 x 11 + 5 doublons", 5, BC.sommets_doubles(dbl),
              BC.sommets_doubles(dbl) == 5)

    xin = neuf("EXP_intersection")
    bm = bmesh.new(); bm.from_mesh(xin.data)
    v = [bm.verts.new(p) for p in ((-0.02, 0.0, -0.02), (0.02, 0.0, -0.02),
                                   (0.02, 0.0, 0.02), (-0.02, 0.0, 0.02))]
    bm.faces.new(v)
    bm.to_mesh(xin.data); bm.free(); xin.data.update()
    n_x = BC.auto_intersections(xin)
    reg.exige("banc.auto_intersections",
              "un quad plante en travers du plan est detecte",
              "grille 11 x 11 + 1 quad vertical", ">= 1", n_x, n_x >= 1)
    saine = BC.auto_intersections(neuf("EXP_saine2"))
    reg.exige("banc.aucune_intersection_a_tort",
              "une grille plane n'auto-intersecte pas", "grille 11 x 11", 0,
              saine, saine == 0)

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("BANC", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
