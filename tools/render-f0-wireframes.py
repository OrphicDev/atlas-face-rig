"""F0-F.5 — wireframes bilateraux, sur duplicatas temporaires.

Les poses viennent des DELTAS publies, pas d'une shape key permanente : la
fondation n'en porte aucune. Les poses de machoire viennent du prototype F0-C,
qui contient deja les cinq angles mesures.

Sur la lecture « meme matrice de camera » pour une paire L/R : prise au pied
de la lettre, elle ferait rendre la zone gauche deux fois. Les deux cameras
d'une paire sont donc EXACTEMENT images l'une de l'autre par le plan sagittal
du contrat, et le test le verifie au lieu de comparer des matrices identiques.

    blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
      --python tools/render-f0-wireframes.py -- \
      --output-dir renders/f0-final/wireframes \
      --report reports/f0-final/wireframes.json
"""
import argparse, hashlib, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, Matrix

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
WAI = importlib.util.module_from_spec(_s); _s.loader.exec_module(WAI)

TETE = "GEO-head_animation_realistic"
MM = 1000.0
RES = 1000
COUL = {"MAT_fil": (1.0, 0.93, 0.25, 1.0), "MAT_surface": (0.09, 0.09, 0.11, 1.0),
        "MAT_cage": (0.20, 0.95, 1.0, 1.0), "MAT_txt": (1.0, 0.95, 0.35, 1.0)}
DELTAS = {"blink_L": "reports/f0-final/deformations/blink_L.cage-delta.json",
          "blink_R": "reports/f0-final/deformations/blink_R.cage-delta.json",
          "mouth_close": "reports/f0-final/deformations/mouth_close.cage-delta.json"}


def materiau(nom):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = COUL[nom]
    b.inputs["Emission Color"].default_value = COUL[nom]
    b.inputs["Emission Strength"].default_value = 1.0
    return m


def repere(direction, position):
    """Matrice d'un objet qui regarde selon `direction`, le haut vers +Z."""
    z = -Vector(direction).normalized()          # -Z local = visee
    x = Vector((0.0, 0.0, 1.0)).cross(z).normalized()
    if x.length < 1e-6:
        x = Vector((1.0, 0.0, 0.0))
    y = z.cross(x).normalized()
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2] = x[i], y[i], z[i]
    M.translation = Vector(position)
    return M


def duplicata(ob, nom, avec_multires=True):
    if avec_multires:
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg),
                                             preserve_all_data_layers=True, depsgraph=dg)
    else:
        me = ob.data.copy()
    d = bpy.data.objects.new(nom, me)
    d.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(d)
    for m in list(d.modifiers):
        d.modifiers.remove(m)
    return d


def poser_delta(ob_cage, chemin, facteur=1.0):
    """Applique un delta de cage. Rend le SHA du tableau, pour la legende."""
    D = json.load(open(chemin, encoding="utf-8"))
    for e in D["deltas"]:
        v = ob_cage.data.vertices[e["index"]]
        d = e["delta_object_local_xyz"]
        v.co = Vector((v.co.x + d[0] * facteur, v.co.y + d[1] * facteur,
                       v.co.z + d[2] * facteur))
    ob_cage.data.update()
    return D["sha256_du_tableau"][:8], D["sommets_deplaces"]


def habiller(ob, epaisseur, direction=None):
    """Surface sombre + fil emissif : le fil se lit sur toute la profondeur."""
    ob.data.materials.clear()
    ob.data.materials.append(materiau("MAT_surface"))
    fil = ob.copy(); fil.data = ob.data.copy(); fil.name = ob.name + "_fil"
    bpy.context.scene.collection.objects.link(fil)
    fil.data.materials.clear(); fil.data.materials.append(materiau("MAT_fil"))
    w = fil.modifiers.new("W", "WIREFRAME")
    w.thickness = epaisseur
    w.use_replace = True
    if direction is not None:
        # le fil est coplanaire avec la surface : sans ce quart de millimetre
        # vers la camera, le rendu montre des losanges sombres de z-fighting.
        fil.location = fil.location - Vector(direction).normalized() * 0.00025
    return fil


def texte(contenu, position, direction, taille, nom="DBG_txt"):
    cu = bpy.data.curves.new(nom, "FONT")
    cu.body = contenu; cu.size = taille
    ob = bpy.data.objects.new(nom, cu)
    ob.matrix_world = repere(direction, position)
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(materiau("MAT_txt"))
    return ob


def rendre(sc, nom, cible, direction, ortho, sortie, legende):
    # Ne retirer QUE la camera et la legende. Nettoyer tout « DBG_ » effacait
    # les poses de machoire du prototype, qui s'appellent DBG_jaw_* : une seule
    # des cinq etait rendue.
    for x in [y for y in bpy.data.objects
              if y.name.startswith("CAM_") or y.name.startswith("DBG_txt")]:
        bpy.data.objects.remove(x, do_unlink=True)
    cam = bpy.data.cameras.new("CAM_" + nom)
    cam.type = "ORTHO"; cam.ortho_scale = ortho
    co = bpy.data.objects.new("CAM_" + nom, cam)
    co.matrix_world = repere(direction, Vector(cible) - Vector(direction).normalized() * 0.5)
    sc.collection.objects.link(co); sc.camera = co
    d = Vector(direction).normalized()
    haut = Vector((0.0, 0.0, 1.0))
    droite = haut.cross(-d).normalized()
    texte(legende, Vector(cible) - d * 0.49
          - droite * ortho * 0.47 + haut * ortho * 0.45, direction, ortho * 0.026)
    f = os.path.join(sortie, nom + ".png")
    sc.render.filepath = f
    bpy.ops.render.render(write_still=True)
    return f, [list(r) for r in co.matrix_world]


def _srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def part_allumee(chemin, tolerance=0.16):
    """Part de l'image occupee par le FIL, classee par sa couleur attendue.

    Un simple seuil `r > 0,30` comptait aussi la surface — (0,09) devient 0,33
    a l'ecran — et les douze vues publiaient « 1 000 000 px de fil » sur un
    million de pixels : une sonde qui ne pouvait pas echouer. On classe par
    distance a la couleur du fil, et on exige une FOURCHETTE : un aplat jaune
    doit echouer autant qu'une image vide.
    """
    cible = tuple(_srgb(x) for x in COUL["MAT_fil"][:3])
    im = bpy.data.images.load(chemin)
    px = list(im.pixels); n = len(px) // 4
    t2 = tolerance * tolerance
    c = sum(1 for i in range(n)
            if (px[i * 4] - cible[0]) ** 2 + (px[i * 4 + 1] - cible[1]) ** 2
            + (px[i * 4 + 2] - cible[2]) ** 2 <= t2)
    bpy.data.images.remove(im)
    return c, n


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output-dir", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--jaw-blend", default="experiments/f0-jaw/FACE_F0_JAW_PROTOTYPE.blend")
    a.add_argument("--globe", default="config/globe-fit.json")
    a.add_argument("--motion", default="config/jaw-motion.json")
    a.add_argument("--mirror", default="reports/f0-final/carte-miroir.json")
    a.add_argument("--audit", default="reports/f0/audit-topologie.json")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    tete = bpy.data.objects[TETE]
    sha_court = WAI.sha_topologie(tete)[:8]
    GL = json.load(open(Rp(o.globe), encoding="utf-8"))
    JM = json.load(open(Rp(o.motion), encoding="utf-8"))
    MI = json.load(open(Rp(o.mirror), encoding="utf-8"))
    AU = json.load(open(Rp(o.audit), encoding="utf-8"))
    ouv = {x["nom"]: x for x in AU.get("ouvertures", []) if x.get("nom")}
    x_sag = (tete.matrix_world @ Vector((MI["sagittal_plane_object_local"], 0, 0))).x

    def centre(nom):
        pts = [tete.matrix_world @ tete.data.vertices[i].co
               for i in ouv[nom]["indices"]]
        return Vector((sum(p.x for p in pts) / len(pts),
                       sum(p.y for p in pts) / len(pts),
                       sum(p.z for p in pts) / len(pts)))

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.03, 1)
    sortie = Rp(o.output_dir); os.makedirs(sortie, exist_ok=True)

    reg = Registre("wireframes")
    R = {"blend": os.path.relpath(bpy.data.filepath, RACINE),
         "resolution": [RES, RES], "topology_sha256_court": sha_court,
         "plan_sagittal": round(x_sag, 6), "images": [],
         "note_cameras": "les deux cameras d'une paire L/R sont images l'une "
                         "de l'autre par le plan sagittal du contrat"}

    c_oeil_L = Vector(GL["eyes"]["L"]["center_world_xyz"])
    c_oeil_R = Vector(GL["eyes"]["R"]["center_world_xyz"])
    c_levre = centre("fente_labiale")
    c_nar_L, c_nar_R = centre("narine.L"), centre("narine.R")

    neutre_ref = {}

    def vue(nom, cible, direction, ortho, delta=None, facteur=1.0, cage=False):
        for x in [y for y in bpy.data.objects if y.name.startswith("RND_")]:
            bpy.data.objects.remove(x, do_unlink=True)
        if delta:
            base = duplicata(tete, "RND_cage", avec_multires=False)
            sha_d, n_d = poser_delta(base, Rp(DELTAS[delta]), facteur)
            src = tete.data
            tete.data = base.data
            # Sans rafraichir les dependances, le duplicata evalue rend encore
            # l'ANCIENNE donnee : les vues « neutre » et « fermee » sortaient
            # au pixel pres identiques (2,90 % de fil des deux cotes).
            tete.data.update(); tete.update_tag()
            bpy.context.view_layer.update()
            d = duplicata(tete, "RND_pose", avec_multires=True)
            tete.data = src
            tete.data.update(); tete.update_tag()
            bpy.context.view_layer.update()
            bpy.data.objects.remove(base, do_unlink=True)
        else:
            sha_d, n_d = "-", 0
            d = duplicata(tete, "RND_pose", avec_multires=not cage)
        # L'epaisseur du fil suit le cadre ET l'espacement des aretes : fixee
        # a 0,18 mm elle tombait a 0,9 % sur les vues larges, et la cage — quatre
        # fois plus clairsemee que la surface dense — restait a 1,37 % la ou la
        # surface est a 4,25 %. A espacement egal, les deux se lisent pareil.
        aretes = [(d.data.vertices[e.vertices[0]].co
                   - d.data.vertices[e.vertices[1]].co).length
                  for e in d.data.edges]
        espacement = sum(aretes) / max(1, len(aretes))
        ep = min(ortho * 0.0026 * (espacement / 0.0032), ortho * 0.006)
        habiller(d, ep)
        # la pose a-t-elle REELLEMENT bouge la surface ?
        pts = [tuple(d.matrix_world @ v.co) for v in d.data.vertices]
        if delta is None:
            neutre_ref[nom] = pts
        else:
            base_nom = nom.replace("_fermee", "_neutre").replace(
                "levres_fermee", "levres_neutre")
            ref = neutre_ref.get(base_nom)
            if ref and len(ref) == len(pts):
                bouge = max(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
                             + (a[2] - b[2]) ** 2) ** 0.5
                            for a, b in zip(pts, ref)) * MM
                reg.exige("wireframe.pose." + nom,
                          "la pose deplace reellement la surface",
                          "contre %s" % base_nom, ">= 0,5 mm", round(bouge, 4),
                          bouge >= 0.5)
            else:
                reg.saute("wireframe.pose." + nom, "la pose deplace la surface",
                          "pas de neutre comparable")
        legende = ("Blender %s | %s | SHA %s | delta %s | fil %.2f mm"
                   % (bpy.app.version_string, nom, sha_court, sha_d, ep * MM))
        f, M = rendre(sc, nom, cible, direction, ortho, sortie, legende)
        allume, total = part_allumee(f)
        part = allume / total
        ok = 0.02 <= part <= 0.45
        reg.exige("wireframe." + nom, "le fil est visible sans noyer l'image",
                  "%d px" % total, "entre 2 % et 45 % de fil",
                  "%.2f %%" % (part * 100), ok)
        R["images"].append({"nom": nom, "fichier": os.path.relpath(f, RACINE),
                            "camera": M, "ortho_scale": ortho,
                            "delta": delta, "delta_sha": sha_d,
                            "sommets_deplaces": n_d, "px_fil": allume,
                            "part_fil": round(part, 5),
                            "epaisseur_fil_mm": round(ep * MM, 4),
                            "espacement_aretes_mm": round(espacement * MM, 4),
                            "legende": legende})
        return M

    # La face regarde vers -Y. L'observateur doit donc etre DEVANT, en y
    # negatif, et viser vers +Y. Pose a (0,-1,0), la camera se retrouvait a
    # y = +0,354 — derriere le crane — et les douze vues montraient l'occiput,
    # un quadrillage lisse ou l'on croyait lire des levres.
    AV = (0.0, 1.0, 0.0)
    for cote, c_oeil, dlt in (("L", c_oeil_L, "blink_L"), ("R", c_oeil_R, "blink_R")):
        vue("paupiere_%s_neutre" % cote, c_oeil, AV, 0.075)
        vue("paupiere_%s_fermee" % cote, c_oeil, AV, 0.075, delta=dlt)
    vue("levres_neutre", c_levre, AV, 0.085)
    vue("levres_fermee", c_levre, AV, 0.085, delta="mouth_close")
    for cote, c_nar in (("L", c_nar_L), ("R", c_nar_R)):
        vue("narine_%s" % cote, c_nar, AV, 0.055)
    vue("philtrum_levre_inferieure",
        Vector((x_sag, c_levre.y, c_levre.z)), AV, 0.050)
    vue("cou_et_raccord", Vector((x_sag, c_levre.y + 0.03, JM["z_bas_cou"])),
        AV, 0.130)
    vue("cage_seule", c_levre, AV, 0.090, cage=True)
    vue("surface_multires", c_levre, AV, 0.090)

    # --- les cinq angles de machoire, pris du prototype F0-C qui les porte
    chemin_jaw = Rp(o.jaw_blend)
    # `cible_lib.objects` est la MEME liste que celle qu'on lui donne : a la
    # sortie du bloc, Blender y a remplace les noms par les objets charges.
    # On garde donc une copie des noms.
    with bpy.data.libraries.load(chemin_jaw) as (source, cible_lib):
        noms = sorted(n for n in source.objects if n.startswith("DBG_jaw_"))
        cible_lib.objects = list(noms)
    reg.exige("wireframe.jaw_disponibles", "les cinq poses de machoire existent",
              os.path.relpath(chemin_jaw, RACINE), 5, len(noms), len(noms) == 5)
    for nom_ob in noms:
        ob = bpy.data.objects.get(nom_ob)
        if ob is None:
            continue
        for x in [y for y in bpy.data.objects if y.name.startswith("RND_")]:
            bpy.data.objects.remove(x, do_unlink=True)
        bpy.context.scene.collection.objects.link(ob)
        d = duplicata(ob, "RND_pose", avec_multires=True)
        bpy.context.scene.collection.objects.unlink(ob)
        aretes = [(d.data.vertices[e.vertices[0]].co
                   - d.data.vertices[e.vertices[1]].co).length
                  for e in d.data.edges]
        espacement = sum(aretes) / max(1, len(aretes))
        ortho = 0.110
        ep = min(ortho * 0.0026 * (espacement / 0.0032), ortho * 0.006)
        habiller(d, ep, (0.35, 1.0, 0.0))
        nom = nom_ob.replace("DBG_", "")
        legende = ("Blender %s | %s | SHA %s | fil %.2f mm"
                   % (bpy.app.version_string, nom, sha_court, ep * MM))
        f, M = rendre(sc, nom, Vector((x_sag, c_levre.y + 0.01, c_levre.z - 0.02)),
                      (0.35, 1.0, 0.0), ortho, sortie, legende)
        allume, total = part_allumee(f)
        part = allume / total
        reg.exige("wireframe." + nom, "le fil est visible sans noyer l'image",
                  "%d px" % total, "entre 2 % et 45 % de fil",
                  "%.2f %%" % (part * 100), 0.02 <= part <= 0.45)
        R["images"].append({"nom": nom, "fichier": os.path.relpath(f, RACINE),
                            "camera": M, "ortho_scale": ortho, "delta": None,
                            "delta_sha": "-", "sommets_deplaces": 0,
                            "px_fil": allume, "part_fil": round(part, 5),
                            "epaisseur_fil_mm": round(ep * MM, 4),
                            "espacement_aretes_mm": round(espacement * MM, 4),
                            "legende": legende})

    # --- les paires bilaterales sont-elles bien symetriques ?
    paires = [("paupiere_L_neutre", "paupiere_R_neutre"),
              ("paupiere_L_fermee", "paupiere_R_fermee"),
              ("narine_L", "narine_R")]
    par_nom = {i["nom"]: i for i in R["images"]}
    for g, dr in paires:
        a1, b1 = par_nom[g], par_nom[dr]
        pg = Vector((a1["camera"][0][3], a1["camera"][1][3], a1["camera"][2][3]))
        pd = Vector((b1["camera"][0][3], b1["camera"][1][3], b1["camera"][2][3]))
        image = Vector((2 * x_sag - pg.x, pg.y, pg.z))
        ecart = (image - pd).length * MM
        reg.exige("wireframe.paire." + g.replace("_L", ""),
                  "les deux cameras sont images l'une de l'autre",
                  "plan sagittal x = %.6f" % x_sag, "<= 0,5 mm",
                  round(ecart, 4), ecart <= 0.5, tolerance=0.5)
        reg.exige("wireframe.echelle." + g.replace("_L", ""),
                  "meme echelle et meme resolution des deux cotes",
                  "%s / %s" % (g, dr), a1["ortho_scale"], b1["ortho_scale"],
                  a1["ortho_scale"] == b1["ortho_scale"])

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("WIREFRAMES", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
