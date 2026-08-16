"""F0-F.4 — coupe sagittale probante, sur duplicatas de rendu uniquement.

Le fichier de production n'est jamais bisecte : tout se passe sur des copies
creees dans la scene de rendu, et le blend n'est pas reenregistre.

Deux plans sont rendus, et c'est deliberе :

  * le VRAI plan sagittal du repere facial, celui du contrat de miroir ;
  * un plan PARASAGITTAL passant par le centre du globe gauche.

Le premier est celui que demande la coupe ; le second existe parce qu'au
milieu du visage il n'y a pas d'oeil : exiger que « les globes se distinguent
de la peau » sur une coupe mediane serait une exigence invérifiable. Chaque
image porte le plan dont elle vient.

    blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
      --python tools/render-f0-sagittal.py -- \
      --output-dir renders/f0-final/sagittal \
      --report reports/f0-final/sagittal-render.json
"""
import argparse, importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
WAI = importlib.util.module_from_spec(_s); _s.loader.exec_module(WAI)
_a = importlib.util.spec_from_file_location(
    "audit", os.path.join(RACINE, "tests", "f0-audit-topologie.py"))
AUD = importlib.util.module_from_spec(_a); _a.loader.exec_module(AUD)

TETE = "GEO-head_animation_realistic"
MM = 1000.0
COULEURS = {
    "MAT_peau": (0.78, 0.78, 0.78, 1.0),        # gris : peau exterieure
    "MAT_coupe": (0.95, 0.10, 0.75, 1.0),       # magenta : section capee
    "MAT_muqueuse": (0.02, 0.55, 0.72, 1.0),    # cyan : interieur
    "MAT_globe": (0.90, 0.08, 0.08, 1.0),       # rouge : globes
    "MAT_regle": (1.0, 0.95, 0.30, 1.0),        # jaune : graduations et texte
    "MAT_regle_fond": (0.10, 0.10, 0.12, 1.0),  # fond sombre de la regle
}


EMISSIFS = tuple(COULEURS)     # tout est emissif : aucune lampe


def materiau(nom):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = COULEURS[nom]
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.75
        # Peau et muqueuse restent DIFFUSES : on regarde l'interieur d'une
        # coque, donc des faces dos a la camera, et l'emission seule les
        # laissait noires sur la coupe mediane. Elles sont eclairees par un
        # ambiant de monde, qui atteint les deux faces. La section, les globes
        # et la regle restent emissifs pour rester francs.
        if nom in EMISSIFS:
            for nom_e in ("Emission Color", "Emission"):
                if nom_e in bsdf.inputs:
                    try: bsdf.inputs[nom_e].default_value = COULEURS[nom]
                    except Exception: pass
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 1.0
    return m


def duplicata_evalue(ob, nom):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg),
                                         preserve_all_data_layers=True, depsgraph=dg)
    d = bpy.data.objects.new(nom, me)
    d.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(d)
    return d


EPAISSEUR_LISIBILITE_M = 0.0004
LARGEUR_TRAIT_M = 0.0007      # 0,7 mm : largeur du trait de section


def cadre_de_section(sommets, z, hauteur_demandee):
    """Centre ET echelle du cadre, mesures sur la section elle-meme.

    Deux fautes corrigees ici. Les Y etaient tapes a la main et faux de 8 cm
    (la bouche est a y = -0,138, pas -0,055). Puis la moyenne des sommets de
    la section etait biaisee par les sommets repetes des triangles : on prend
    le centre de la BOITE de la bande, et l'echelle suit l'etendue mesuree.
    """
    bande = [p for p in sommets if abs(p[2] - z) <= hauteur_demandee * 0.5]
    if len(bande) < 3:
        bande = sommets
    ys = [p[1] for p in bande]
    y0, y1 = min(ys), max(ys)
    etendue = max(y1 - y0, hauteur_demandee * 0.35)
    # L'echelle SUIT la mesure. La plafonner a la valeur demandee faisait
    # cadrer le milieu creux du cou : la section y est plus large que 90 mm,
    # et on ne voyait que l'interieur de la coque.
    return (y0 + y1) / 2.0, min(0.18, max(hauteur_demandee, etendue * 1.15))


def boucles_fermees(aretes):
    """Boucles fermees formees par les aretes de coupe, dans l'ordre."""
    voisins = {}
    for e in aretes:
        a, b = e.verts
        voisins.setdefault(a, []).append(b)
        voisins.setdefault(b, []).append(a)
    restants = set(voisins)
    boucles = []
    while restants:
        depart = restants.pop()
        if len(voisins[depart]) != 2:
            continue
        boucle, courant, precedent = [depart], voisins[depart][0], depart
        while courant is not depart:
            boucle.append(courant)
            restants.discard(courant)
            suivants = [x for x in voisins.get(courant, []) if x is not precedent]
            if not suivants:
                boucle = None
                break
            precedent, courant = courant, suivants[0]
        if boucle and len(boucle) >= 3:
            boucles.append(boucle)
    return boucles


def couper_et_caper(ob, x_monde, mats):
    """Bisect + cap sur le duplicata. Rend le nombre de faces de section."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    res = bmesh.ops.bisect_plane(
        bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=(x_monde, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0),
        clear_outer=True, use_snap_center=False)
    aretes = [g for g in res["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
    # `holes_fill` rend un n-gon de 240 cotes, tres concave. Il compte bien 491
    # cm2, mais sa triangulation produit des triangles degeneres : depuis le
    # cote de la coupe le rendu tombait de 14 138 a 111 pixels — on regardait
    # l'interieur creux du crane. On tesselle donc le profil dans son plan,
    # avec l'outil fait pour les polygones concaves a trous.
    boucles = boucles_fermees(aretes)
    nouvelles = []
    # LA SECTION D'UNE COQUE EST UNE COURBE, PAS UNE AIRE.
    #
    # Le maillage n'a pas d'epaisseur : couper une coque rend une ligne fermee,
    # pas une surface pleine. Tesseller cette boucle donnait un ruban degenere
    # — mesure : la section mediane rendait 147 pixels sur 360 000, contre
    # 1 233 pour la parasagittale, alors qu'elle a 165 sommets dans le cadre et
    # 491 cm2 d'aire declaree par la tesselation. On ne tesselle donc plus : on
    # TRACE la courbe, avec un trait de largeur dite, dans le plan de coupe.
    for boucle in boucles:
        n = len(boucle)
        for k in range(n):
            a = boucle[k].co.copy()
            b = boucle[(k + 1) % n].co.copy()
            d = (b - a)
            if d.length < 1e-9:
                continue
            # normale DANS le plan de coupe : le trait fait face a la camera
            t = Vector((0.0, d.y, d.z)).normalized()
            nrm = Vector((0.0, -t.z, t.y)) * (LARGEUR_TRAIT_M * 0.5)
            try:
                f = bm.faces.new([bm.verts.new(a + nrm), bm.verts.new(b + nrm),
                                  bm.verts.new(b - nrm), bm.verts.new(a - nrm)])
            except ValueError:
                continue
            f.material_index = mats["coupe"]
            nouvelles.append(f)
    bm.normal_update()
    # Les faces du capuchon doivent regarder la CAMERA. La section mediane est
    # une seule boucle « en trou de serrure » — elle contourne le profil, entre
    # dans la bouche et ressort — et son enroulement est l'inverse de celui de
    # la coupe parasagittale, qui en donne deux. Ses triangles pointaient donc
    # vers -X, et EEVEE n'emet pas sur la face arriere : la section etait bien
    # la, avec 165 sommets dans le cadre de la bouche et 491 cm2 d'aire, et
    # elle ne se voyait pas.
    for f in nouvelles:
        if f.normal.x < 0.0:
            f.normal_flip()
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    # sommets de la SECTION, dedupliques : les repetitions des triangles
    # tiraient le centre du cadre vers les zones les plus tesselees.
    coupe_pts = sorted({tuple(round(c, 7) for c in v.co)
                        for b in boucles for v in b})
    # Epaississement DELIBERE de 0,4 mm vers la camera : la tete est une coque,
    # sa section est donc un lisere d'epaisseur nulle. Ce n'est pas une mesure,
    # c'est une aide de lecture, et elle est dite dans le rapport et la legende.
    if nouvelles:
        ext = bmesh.ops.extrude_face_region(bm, geom=nouvelles)
        deplaces = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=deplaces,
                            vec=(EPAISSEUR_LISIBILITE_M, 0.0, 0.0))
        for g in ext["geom"]:
            if isinstance(g, bmesh.types.BMFace):
                g.material_index = mats["coupe"]
        bm.normal_update()
        bm.faces.ensure_lookup_table()
        nouvelles = [f for f in bm.faces if f.material_index == mats["coupe"]]
    bm.transform(ob.matrix_world.inverted())
    bm.to_mesh(ob.data); bm.free()
    ob.data.update()
    return len(nouvelles), coupe_pts


def classer_avant_coupe(ob, n_rayons, seuil):
    """Interieur / exterieur mesure sur le maillage FERME, avant toute coupe.

    Le faire apres la coupe etait une faute silencieuse : sur une demi-coque
    ouverte, presque tous les rayons s'echappent, tout est classe exterieur, et
    la muqueuse ne pouvait JAMAIS apparaitre — les huit images publiaient
    « muqueuse : 0 » sans que rien ne le signale.
    """
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    ext = AUD.classer(AUD.fraction_degagee(bm, n_rayons), seuil)
    pts = [(ob.matrix_world @ v.co).copy() for v in bm.verts]
    bm.free()
    from mathutils import kdtree
    kd = kdtree.KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert(p, i)
    kd.balance()
    return kd, ext


def peindre_interieur(ob, mats, kd, ext):
    """Cyan sur l'interieur, gris sur la peau, par report du classement."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    M = ob.matrix_world
    n = 0
    for f in bm.faces:
        if f.material_index == mats["coupe"]:
            continue
        c = M @ f.calc_center_median()
        votes = [ext[i] for (_, i, _) in kd.find_n(c, 3)]
        if votes and sum(votes) == 0:
            f.material_index = mats["muqueuse"]; n += 1
        else:
            f.material_index = mats["peau"]
    bm.to_mesh(ob.data); bm.free()
    ob.data.update()
    return n


def regle(x, centre, longueur_m=0.010, pas_m=0.001):
    """Regle de 10 mm avec une graduation par millimetre, dans le plan de coupe."""
    me = bpy.data.meshes.new("MSH_regle")
    ob = bpy.data.objects.new("DBG_regle", me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    ep = 0.0007
    def barre(y0, y1, z0, z1, mat):
        vs = [bm.verts.new((x + 0.0006, y, z)) for y, z in
              ((y0, z0), (y1, z0), (y1, z1), (y0, z1))]
        f = bm.faces.new(vs); f.material_index = mat
    y0 = centre.y - longueur_m / 2.0
    barre(y0, y0 + longueur_m, centre.z, centre.z + ep * 2, 0)
    k = 0
    while k * pas_m <= longueur_m + 1e-9:
        h = ep * (4 if k % 5 == 0 else 2.5)
        yy = y0 + k * pas_m
        barre(yy, yy + 0.00012, centre.z, centre.z + h, 1)
        k += 1
    bm.to_mesh(me); bm.free()
    me.materials.append(materiau("MAT_regle_fond"))
    me.materials.append(materiau("MAT_regle"))
    return ob


def repere_vers_moins_x(position):
    """Matrice d'un objet qui REGARDE selon -X, le haut vers +Z.

    Composer RotY(90) @ RotX(90) faisait regarder la camera selon +Y : les
    quatorze images etaient uniformement noires alors que la coupe, elle,
    etait correcte. On pose donc les axes au lieu de les deviner.
    """
    ax = Vector((0.0, 1.0, 0.0))     # droite de l'image
    ay = Vector((0.0, 0.0, 1.0))     # haut de l'image
    az = Vector((1.0, 0.0, 0.0))     # -Z local = direction de visee
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2] = ax[i], ay[i], az[i]
    M.translation = position
    return M


def texte(contenu, x, p, taille=0.0022, nom="DBG_txt"):
    cu = bpy.data.curves.new(nom, "FONT")
    cu.body = contenu
    cu.size = taille
    ob = bpy.data.objects.new(nom, cu)
    ob.matrix_world = repere_vers_moins_x(Vector((x + 0.0008, p.y, p.z)))
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(materiau("MAT_regle"))
    return ob


def camera(x, cible, hauteur_m):
    cam = bpy.data.cameras.new("CAM_sag")
    cam.type = "ORTHO"; cam.ortho_scale = hauteur_m
    ob = bpy.data.objects.new("CAM_sag", cam)
    ob.matrix_world = repere_vers_moins_x(Vector((x + 0.5, cible.y, cible.z)))
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lumiere(x, cible):
    d = bpy.data.lights.new("L", "AREA"); d.energy = 60.0; d.size = 0.40
    o = bpy.data.objects.new("L", d)
    o.matrix_world = repere_vers_moins_x(Vector((x, cible.y, cible.z)))
    bpy.context.scene.collection.objects.link(o)
    return o


FOND_LINEAIRE = (0.035, 0.033, 0.055)


def _srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def palette_attendue():
    """Couleur d'ecran attendue de chaque materiau, en sRGB."""
    return {nom: tuple(round(_srgb(x), 4) for x in COULEURS[nom][:3])
            for nom in COULEURS}


def couleurs_image(chemin, tolerance=0.12):
    """Classe chaque pixel par sa DISTANCE a la couleur attendue.

    Des inegalites ecrites a la main rendaient « rouge : 0 » sur une image ou
    le globe est manifestement rouge : le rouge (0,90 ; 0,08 ; 0,08) devient
    (0,96 ; 0,30 ; 0,30) a l'ecran, et la condition g < 0,20 le rejetait. On
    compare donc a la couleur attendue, calculee, plutot qu'a un seuil devine.
    Un pixel sur 25 sous-comptait aussi les liseres fins : on les compte tous.
    """
    global FOND
    FOND = tuple(_srgb(x) for x in FOND_LINEAIRE)
    pal = palette_attendue()
    # Peau et muqueuse sont diffuses : leur couleur d'ecran depend de
    # l'eclairage ambiant, elle n'est donc pas la couleur du materiau. On les
    # classe par TEINTE (gris neutre contre bleu), pas par egalite exacte.
    cibles = {"magenta": pal["MAT_coupe"], "rouge": pal["MAT_globe"]}
    im = bpy.data.images.load(chemin)
    px = list(im.pixels)
    n = len(px) // 4
    seen = set()
    compte = {k: 0 for k in cibles}
    t2 = tolerance * tolerance
    compte["gris"] = 0
    compte["cyan"] = 0
    for i in range(n):
        r, g, b = px[i * 4], px[i * 4 + 1], px[i * 4 + 2]
        seen.add((int(r * 12), int(g * 12), int(b * 12)))
        touche = False
        for nom, (cr, cg, cb) in cibles.items():
            if (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2 <= t2:
                compte[nom] += 1; touche = True
                break
        if touche:
            continue
        # Le fond (0,035 ; 0,033 ; 0,055) devient (0,21 ; 0,21 ; 0,26) a
        # l'ecran : neutre et clair, il etait compte comme de la PEAU, et les
        # cadres medians publiaient 375 000 pixels de peau sur une image vide.
        if (abs(r - FOND[0]) < 0.05 and abs(g - FOND[1]) < 0.05
                and abs(b - FOND[2]) < 0.05):
            continue
        if max(r, g, b) < 0.16:
            continue
        if b - r > 0.12 and b > 0.20:
            compte["cyan"] += 1
        elif max(r, g, b) - min(r, g, b) < 0.08 and r > 0.20:
            compte["gris"] += 1
    bpy.data.images.remove(im)
    out = {"teintes": len(seen), "echantillons": n, "tolerance": tolerance,
           "palette_sRGB": {k: list(v) for k, v in cibles.items()}}
    out.update(compte)
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output-dir", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--mirror", default="reports/f0-final/carte-miroir.json")
    a.add_argument("--globe", default="config/globe-fit.json")
    a.add_argument("--motion", default="config/jaw-motion.json")
    a.add_argument("--audit", default="reports/f0/audit-topologie.json")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    tete = bpy.data.objects[TETE]
    sha_court = WAI.sha_topologie(tete)[:8]
    MI = json.load(open(Rp(o.mirror), encoding="utf-8"))
    GL = json.load(open(Rp(o.globe), encoding="utf-8"))
    JM = json.load(open(Rp(o.motion), encoding="utf-8"))
    AU = json.load(open(Rp(o.audit), encoding="utf-8"))
    n_rayons = AU.get("rayons_par_sommet", 48)
    seuil = AU.get("seuil_degagement", 0.15)
    reg = Registre("sagittal-render")

    x_sag = (tete.matrix_world @ Vector((MI["sagittal_plane_object_local"], 0, 0))).x
    x_para = GL["eyes"]["L"]["center_world_xyz"][0]
    # Couper EXACTEMENT sur le plan de symetrie passe par la couture de
    # sommets medians : la section y est degeneree — elle n'a pas de largeur —
    # et trois images sur quatre ne montraient aucune section. Ce n'est pas un
    # defaut de rendu, c'est la geometrie. Le plan median est donc decale de
    # 1,0 mm pour couper des faces plutot que de suivre la couture.
    DECALAGE_M = 0.001
    plans = [("median", x_sag + DECALAGE_M,
              "plan sagittal du contrat de miroir, decale de 1,0 mm pour ne pas "
              "suivre la couture de symetrie"),
             ("parasagittal_oeil_L", x_para, "plan par le centre du globe L")]

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = 1000
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    # fond tres sombre et legerement bleute : aucune des quatre couleurs de la
    # charte ne peut etre confondue avec lui par le classement de pixels.
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.033, 0.055, 1)
    # EEVEE n'emet pas sur la face ARRIERE. Or on regarde l'interieur d'une
    # coque : ses faces tournent le dos a la camera, et elles restaient noires
    # quoi qu'on fasse — deux lampes opposees ont fini par tout bruler sans
    # rien reveler. On double donc le demi-crane avec les normales inversees.
    # C'est une aide de rendu, pas une mesure, et elle est dite ici.

    # Les cadres visent des REPERES MESURES sur le maillage. Les centrer sur
    # la boite de la section faisait viser y = -0,069 pour la bouche, alors que
    # les levres sont a y = -0,138 : on cadrait le vide du pharynx, et quatre
    # images sur huit etaient noires.
    ouv = {x["nom"]: x for x in AU.get("ouvertures", []) if x.get("nom")}
    def centre_ouverture(nom):
        idx = ouv[nom]["indices"]
        pts = [tete.matrix_world @ tete.data.vertices[i].co for i in idx]
        return (sum(p.y for p in pts) / len(pts), sum(p.z for p in pts) / len(pts))
    y_levre, z_levre = centre_ouverture("fente_labiale")
    y_oeil = GL["eyes"]["L"]["center_world_xyz"][1]
    z_oeil = GL["eyes"]["L"]["center_world_xyz"][2]
    cadres = [("bouche", y_levre, z_levre, 0.055),
              ("orbite", y_oeil, z_oeil, 0.060),
              ("cavite_orale", y_levre + 0.022,
               (JM["z_levre"] + JM["z_menton"]) / 2, 0.075),
              ("cou", None, JM["z_bas_cou"], 0.090)]

    sortie = Rp(o.output_dir); os.makedirs(sortie, exist_ok=True)
    R = {"blend": os.path.relpath(bpy.data.filepath, RACINE),
         "topology_sha256_court": sha_court,
         "plan_sagittal_du_contrat": round(x_sag, 6),
         "decalage_median_mm": 1.0,
         "aides_de_lecture": [
             "section tracee en ruban de 0,7 mm de large dans le plan de "
             "coupe : la section d'une coque est une courbe, pas une aire",
             "trait epaissi de 0,4 mm vers la camera",
             "double du demi-crane aux normales inversees, sans la section : "
             "EEVEE n'emet pas sur la face arriere",
             "plan median decale de 1,0 mm : sur la couture de symetrie la "
             "section est degeneree"],
         "plans": {}, "images": []}

    for nom_plan, xp, description in plans:
        for ob in [x for x in bpy.data.objects
                   if x.name.startswith(("RND_", "DBG_", "CAM_", "L"))
                   and x.name not in (TETE,)]:
            bpy.data.objects.remove(ob, do_unlink=True)
        d = duplicata_evalue(tete, "RND_tete")
        for nom in ("MAT_peau", "MAT_coupe", "MAT_muqueuse"):
            d.data.materials.append(materiau(nom))
        mats = {"peau": 0, "coupe": 1, "muqueuse": 2}
        kd_ext, ext = classer_avant_coupe(d, n_rayons, seuil)
        n_coupe, pts_coupe = couper_et_caper(d, xp, mats)
        n_int = peindre_interieur(d, mats, kd_ext, ext)
        globes = []
        for suffixe in (".sclera.L", ".sclera.R", ".iris.L", ".iris.R"):
            src = bpy.data.objects.get(TETE + suffixe)
            if src is None:
                continue
            g = duplicata_evalue(src, "RND" + suffixe)
            g.data.materials.clear(); g.data.materials.append(materiau("MAT_globe"))
            globes.append(g.name)
        interieur = d.copy(); interieur.data = d.data.copy()
        interieur.name = "RND_tete_dos"
        bpy.context.scene.collection.objects.link(interieur)
        bmi = bmesh.new(); bmi.from_mesh(interieur.data)
        # Le double NE PORTE PAS la section : ses faces de coupe, retournees,
        # venaient masquer le magenta en z-fighting et la section retombait de
        # 404 a 290 pixels, voire a zero. Il est aussi recule de 0,05 mm.
        caps = [f for f in bmi.faces if f.material_index == mats["coupe"]]
        if caps:
            bmesh.ops.delete(bmi, geom=caps, context="FACES")
        bmesh.ops.reverse_faces(bmi, faces=bmi.faces[:])
        # VERS la camera (+X). Le decaler en -X le placait DERRIERE l'original,
        # dont les faces arriere noires gagnaient le test de profondeur : tout
        # l'interieur restait un aplat sombre.
        bmesh.ops.translate(bmi, verts=bmi.verts[:], vec=(0.00005, 0.0, 0.0))
        bmi.to_mesh(interieur.data); bmi.free(); interieur.data.update()

        reg.exige("sagittal.%s.section" % nom_plan,
                  "la section est capee, pas creuse", description, ">= 1 face",
                  n_coupe, n_coupe >= 1)
        reg.exige("sagittal.%s.interieur" % nom_plan,
                  "l'interieur est peint distinctement de la peau",
                  "classement de l'audit", ">= 1 face", n_int, n_int >= 1)
        reg.exige("sagittal.%s.globes" % nom_plan, "les globes sont presents en rouge",
                  "duplicatas oculaires", 4, len(globes), len(globes) == 4)
        # diagnostic : ou sont les faces de section, et de quel cote regardent-elles ?
        _c = [f for f in d.data.polygons if f.material_index == mats["coupe"]]
        _xs = [ (d.matrix_world @ d.data.vertices[v].co).x
                for f in _c for v in f.vertices ]
        R["plans"][nom_plan] = {"x_monde": round(xp, 6), "description": description,
                                "faces_section": n_coupe, "faces_interieur": n_int,
                                "globes": globes,
                                "section_normale_vers_camera":
                                    sum(1 for f in _c
                                        if (d.matrix_world.to_3x3()
                                            @ f.normal).x > 0.0),
                                "section_normale_opposee":
                                    sum(1 for f in _c
                                        if (d.matrix_world.to_3x3()
                                            @ f.normal).x <= 0.0),
                                "section_x_min": round(min(_xs), 6) if _xs else None,
                                "section_x_max": round(max(_xs), 6) if _xs else None}

        for nom_cadre, y_cadre, z_cadre, hauteur in cadres:
            if y_cadre is None:
                y_cadre, hauteur = cadre_de_section(pts_coupe, z_cadre, hauteur)
            cible = Vector((0.0, y_cadre, z_cadre))
            for x in [y for y in bpy.data.objects
                      if y.name.startswith(("DBG_", "CAM_", "L."))or y.name == "L"]:
                bpy.data.objects.remove(x, do_unlink=True)
            c = Vector((xp, cible.y, cible.z))
            r = regle(xp, Vector((xp, cible.y - hauteur * 0.30,
                                  cible.z - hauteur * 0.42)))
            t = texte("Blender %s | neutre | %s | %s | SHA %s | regle 10 mm"
                      % (bpy.app.version_string, nom_plan, nom_cadre, sha_court)
                      + " | trait de section 0,7 mm",
                      xp, Vector((xp, cible.y - hauteur * 0.46,
                                  cible.z + hauteur * 0.43)),
                      taille=hauteur * 0.030)
            # emission pure : une lampe posee a 30 cm brulait tout en blanc,
            # et une couleur brulee ne distingue plus rien.
            cam = camera(xp, c, hauteur)
            sc.camera = cam
            f = os.path.join(sortie, "%s_%s.png" % (nom_plan, nom_cadre))
            sc.render.filepath = f
            bpy.ops.render.render(write_still=True)
            mesure = couleurs_image(f)
            # Le tutoriel demande que la coupe montre « clairement interieur
            # et exterieur EN DEUX COULEURS ». J'avais ajoute de mon cru un
            # « >= 2000 pixels de peau », qui n'est pas cette exigence : sur
            # une coupe MEDIANE, regardee dans l'axe, il n'y a presque pas de
            # peau a voir — 132 pixels a l'orbite — et le critere echouait sur
            # une image parfaitement lisible. Le critere est donc celui du
            # tutoriel : au moins DEUX classes de matiere presentes.
            classes = sum(1 for k in ("magenta", "cyan", "rouge", "gris")
                          if mesure[k] >= 200)
            mesure["classes_presentes"] = classes
            ok = (mesure["teintes"] >= 8 and mesure["magenta"] >= 20
                  and classes >= 2)
            reg.exige("sagittal.image.%s_%s" % (nom_plan, nom_cadre),
                      "l'image n'est pas un clay uniforme et montre la section",
                      "%d echantillons" % mesure["echantillons"],
                      ">= 8 teintes, >= 20 px de section, >= 2 classes",
                      "%d teintes, %d classes : %d section, %d muqueuse, "
                      "%d globe, %d peau"
                      % (mesure["teintes"], classes, mesure["magenta"],
                         mesure["cyan"], mesure["rouge"], mesure["gris"]), ok)
            R["images"].append({"fichier": os.path.relpath(f, RACINE),
                                "plan": nom_plan, "cadre": nom_cadre,
                                "regle_mm": 10.0, "texte": t.data.body,
                            "epaississement_section_mm": EPAISSEUR_LISIBILITE_M * MM,
                                "camera": [list(row) for row in cam.matrix_world],
                                "ortho_scale": hauteur, "mesure": mesure})

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("SAGITTAL", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
