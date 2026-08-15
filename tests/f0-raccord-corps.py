"""P0.2 — mesurer reellement le raccord tete-corps.

L'audit reprochait ceci, et il avait raison : « la position monde inchangee
preserve la compatibilite » ne mesure rien. Le paquet range ses assets comme une
bibliotheque de demonstration ; l'absence de deplacement d'un asset ne dit rien
d'un autre. Ce script construit un repere anatomique pour chaque maillage,
resout la similarite qui amene l'un dans l'autre, et publie les residus.

Aucune modification de FACE_BASE_LOCKED.blend. Prototype jetable uniquement.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-raccord-corps.py -- reports/f0-correction/raccord-corps.json
"""
import json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector
from atlas_commun import Registre, exiger_asset

MM = 1000.0
TETE_COL, CORPS_COL = "Head (Animation) - Realistic", "Body Male - Realistic"


# ------------------------------------------------------- similarite ----

def umeyama(source, cible, avec_echelle=True):
    """Similarite (R, t, s) qui envoie `source` sur `cible` au moindre carre.

    Umeyama 1991. Rend aussi le residu par point.
    """
    A = np.asarray(source, dtype=np.float64)
    B = np.asarray(cible, dtype=np.float64)
    ca, cb = A.mean(0), B.mean(0)
    A0, B0 = A - ca, B - cb
    H = A0.T @ B0 / len(A)
    U, D, Vt = np.linalg.svd(H)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[2, 2] = -1.0
    R = Vt.T @ S @ U.T
    var = (A0 ** 2).sum() / len(A)
    s = float((D * np.diag(S)).sum() / var) if avec_echelle and var > 0 else 1.0
    t = cb - s * (R @ ca)
    residus = np.linalg.norm((s * (R @ A.T)).T + t - B, axis=1)
    return R, t, s, residus


def euler_de(R):
    return [round(math.degrees(x), 5) for x in
            (math.atan2(R[2, 1], R[2, 2]),
             math.atan2(-R[2, 0], math.hypot(R[2, 1], R[2, 2])),
             math.atan2(R[1, 0], R[0, 0]))]


# ---------------------------------------------------------- reperes ----

def centre_et_rayon(obj):
    co = [obj.matrix_world @ v.co for v in obj.data.vertices]
    c = Vector([sum(x[i] for x in co) / len(co) for i in range(3)])
    return c, sum((x - c).length for x in co) / len(co)


RAYON_TETE = 0.14   # m — une tete humaine tient dans 140 mm autour du plan des yeux


def reperes_anatomiques(mesh, oeil_L, oeil_R, nom, reg=None):
    """Origine au milieu des yeux, axe lateral D->G, axe avant vers la pointe du nez.

    ATTENTION — la premiere version de cette fonction cherchait le nez et le
    menton sur TOUT le maillage. Appliquee au corps entier, elle a rendu les
    orteils et les pieds, et le solveur a conclu a une echelle de 8,06 alors que
    les distances interoculaires ne different que de 2 %. La recherche est donc
    bornee a une boule de RAYON_TETE autour du plan des yeux, et chaque repere
    est soumis a des bornes anatomiques : hors bornes, on ne publie pas de
    valeur.
    """
    cL, rL = centre_et_rayon(oeil_L)
    cR, rR = centre_et_rayon(oeil_R)
    origine = (cL + cR) / 2
    lateral = (cL - cR)
    interoculaire = lateral.length
    lateral = lateral.normalized()
    tous = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
    co = [c for c in tous if (c - origine).length <= RAYON_TETE]

    # Avant provisoire = -Y monde. Ce n'est pas une supposition : on verifie que
    # les globes oculaires sont bien anterieurs au centre du maillage local.
    provisoire = Vector((0.0, -1.0, 0.0))
    centre_local = Vector([sum(c[i] for c in co) / len(co) for i in range(3)])
    anterieur = (origine - centre_local).dot(provisoire) > 0
    if reg:
        reg.exige("reperes.%s.yeux_anterieurs" % nom,
                  "les yeux sont devant le centre de la tete",
                  "boule de %.0f mm autour du plan des yeux" % (RAYON_TETE * MM),
                  "> 0", round((origine - centre_local).dot(provisoire) * MM, 3), anterieur)

    pres_axe = [c for c in co if abs((c - origine).dot(lateral)) < 0.018]
    nez = max(pres_axe, key=lambda c: (c - origine).dot(provisoire))
    avant = (nez - origine)
    avant = (avant - lateral * avant.dot(lateral)).normalized()
    vertical = lateral.cross(avant).normalized()
    if vertical.z < 0: vertical = -vertical

    saillie_nez = (nez - origine).dot(avant) * MM
    cand = [c for c in pres_axe if (c - origine).dot(avant) > 0.005]
    menton = min(cand, key=lambda c: (c - origine).dot(vertical)) if cand else None
    chute_menton = -((menton - origine).dot(vertical) * MM) if menton else None

    if reg:
        reg.exige("reperes.%s.saillie_du_nez" % nom,
                  "la pointe du nez est en avant du plan des yeux, de 20 a 90 mm",
                  "boule de %.0f mm" % (RAYON_TETE * MM), "20 a 90 mm",
                  round(saillie_nez, 2), 20.0 <= saillie_nez <= 90.0)
        reg.exige("reperes.%s.chute_du_menton" % nom,
                  "le menton est sous le plan des yeux, de 50 a 140 mm",
                  "boule de %.0f mm" % (RAYON_TETE * MM), "50 a 140 mm",
                  round(chute_menton, 2) if chute_menton else None,
                  chute_menton is not None and 50.0 <= chute_menton <= 140.0)
        reg.exige("reperes.%s.interoculaire_plausible" % nom,
                  "distance interoculaire humaine, 50 a 80 mm",
                  "centres des deux globes", "50 a 80 mm",
                  round(interoculaire * MM, 3), 50.0 <= interoculaire * MM <= 80.0)
    return {
        "saillie_du_nez_mm": round(saillie_nez, 3),
        "chute_du_menton_mm": round(chute_menton, 3) if chute_menton else None,
        "sommets_dans_la_boule": len(co), "sommets_du_maillage": len(tous),
        "nom": nom, "objet": mesh.name,
        "oeil_L": {"centre": [round(x, 6) for x in cL], "rayon_mm": round(rL * MM, 3),
                   "objet": oeil_L.name},
        "oeil_R": {"centre": [round(x, 6) for x in cR], "rayon_mm": round(rR * MM, 3),
                   "objet": oeil_R.name},
        "origine_interoculaire": [round(x, 6) for x in origine],
        "distance_interoculaire_mm": round(interoculaire * MM, 3),
        "pointe_du_nez": [round(x, 6) for x in nez],
        "menton": [round(x, 6) for x in menton] if menton else None,
        "axe_lateral": [round(x, 6) for x in lateral],
        "axe_avant": [round(x, 6) for x in avant],
        "axe_vertical": [round(x, 6) for x in vertical],
        "matrice_monde": [[round(x, 6) for x in l] for l in mesh.matrix_world],
        "sommets": len(mesh.data.vertices), "faces": len(mesh.data.polygons),
        "bbox_min": [round(min(c[i] for c in co), 6) for i in range(3)],
        "bbox_max": [round(max(c[i] for c in co), 6) for i in range(3)],
        "_pts": {"oeil_L": cL, "oeil_R": cR, "nez": nez, "menton": menton,
                 "origine": origine},
    }


# --------------------------------------------------------- autotests ----

def autotests(reg):
    base = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0.5],
                     [-1, 0.3, 0.2]], dtype=float)
    th = math.radians(37.0)
    Rv = np.array([[math.cos(th), -math.sin(th), 0],
                   [math.sin(th), math.cos(th), 0], [0, 0, 1]])
    s_v, t_v = 1.37, np.array([2.5, -1.25, 0.75])
    cible = (s_v * (Rv @ base.T)).T + t_v
    R, t, s, res = umeyama(base, cible)
    reg.exige("similarite.echelle_retrouvee", "similarite exacte reconstruite",
              "rotation 37 deg, echelle 1,37, translation connue", 1.37, round(s, 9),
              abs(s - 1.37) < 1e-9, tolerance=1e-9)
    reg.exige("similarite.residu_nul", "residu d'une similarite exacte",
              "meme configuration", 0.0, float(round(res.max(), 12)), res.max() < 1e-9)
    reg.exige("similarite.rotation_retrouvee", "matrice de rotation reconstruite",
              "meme configuration", "37.0", "%.4f" % euler_de(R)[2],
              abs(euler_de(R)[2] - 37.0) < 1e-4)
    # une configuration qui N'EST PAS une similarite doit laisser un residu
    tordue = cible.copy(); tordue[0] += np.array([0.05, 0.0, 0.0])
    _, _, _, res2 = umeyama(base, tordue)
    reg.exige("similarite.repond_a_son_entree", "un point deplace de 50 mm laisse un residu",
              "meme configuration, un point decale", "> 0.001", round(float(res2.max()), 6),
              res2.max() > 1e-3)
    # miroir interdit : une configuration reflechie ne doit pas etre "resolue" par un reflet
    reflet = cible.copy(); reflet[:, 0] *= -1
    Rr, _, _, _ = umeyama(base, reflet)
    reg.exige("similarite.pas_de_reflexion", "le solveur reste une rotation propre",
              "cible reflechie", "det = +1", round(float(np.linalg.det(Rr)), 9),
              np.linalg.det(Rr) > 0)


# ------------------------------------------------------------ mesure ----

if __name__ == "__main__":
    sortie = sys.argv[sys.argv.index("--") + 1]
    reg = Registre("f0-raccord-corps")
    print("AUTO-TESTS DU SOLVEUR")
    autotests(reg)
    if not reg.conclure():
        json.dump({"status": "ECHEC", **reg.bilan()}, open(sortie, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("SOLVEUR NON VERIFIE : aucune mesure publiee."); sys.exit(2)

    PAQUET, pf = exiger_asset()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = [TETE_COL, CORPS_COL]
    for c in dst.collections:
        bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.update()

    def trouver(prefixe, motif=None):
        cands = [o for o in bpy.data.objects if o.type == "MESH"
                 and o.name.startswith(prefixe)
                 and (motif is None or motif in o.name)]
        return cands

    tete = max(trouver("GEO-head_animation_realistic"), key=lambda o: len(o.data.vertices))
    corps = max(trouver("GEO-body_male_realistic"), key=lambda o: len(o.data.vertices))
    oeil_tete = {c: next(o for o in bpy.data.objects
                         if o.name == "GEO-head_animation_realistic.sclera." + c)
                 for c in "LR"}
    oeil_corps = {c: next(o for o in bpy.data.objects
                          if o.name == "GEO-body_male_realistic.eye." + c) for c in "LR"}

    R = {"preflight": pf, "registre": None,
         "objets_trouves": {"tete": tete.name, "corps": corps.name,
                            "yeux_tete": sorted(o.name for o in oeil_tete.values()),
                            "yeux_corps": sorted(o.name for o in oeil_corps.values())}}

    rt = reperes_anatomiques(tete, oeil_tete["L"], oeil_tete["R"], "tete", reg)
    rc = reperes_anatomiques(corps, oeil_corps["L"], oeil_corps["R"], "corps", reg)
    if reg.echecs:
        R["registre"] = reg.bilan()
        R["conclusion_seuils"] = "REPERES NON FIABLES — aucune similarite publiee"
        os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
        json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("REPERES HORS BORNES ANATOMIQUES : aucun chiffre de raccord publie.")
        reg.conclure(); sys.exit(2)
    pts_t = rt.pop("_pts"); pts_c = rc.pop("_pts")
    R["reperes"] = {"tete": rt, "corps": rc}

    cles = [k for k in ("oeil_L", "oeil_R", "nez", "menton")
            if pts_t.get(k) is not None and pts_c.get(k) is not None]
    src = [list(pts_t[k]) for k in cles]
    dst_ = [list(pts_c[k]) for k in cles]
    Rm, t, s, res = umeyama(src, dst_)

    R["similarite_tete_vers_corps"] = {
        "reperes_utilises": cles,
        "rotation_matrice": [[round(float(x), 8) for x in l] for l in Rm],
        "rotation_euler_xyz_deg": euler_de(Rm),
        "translation_m": [round(float(x), 6) for x in t],
        "facteur_echelle": round(float(s), 8),
        "ecart_a_1_pct": round(abs(float(s) - 1.0) * 100, 5),
        "residus_mm": {k: round(float(res[i]) * MM, 4) for i, k in enumerate(cles)},
        "residu_max_mm": round(float(res.max()) * MM, 4),
    }
    R["rapport_interoculaire"] = round(
        rc["distance_interoculaire_mm"] / rt["distance_interoculaire_mm"], 6)

    # --- seuils imposes par le cahier ---
    ecart_pct = R["similarite_tete_vers_corps"]["ecart_a_1_pct"]
    rmax = R["similarite_tete_vers_corps"]["residu_max_mm"]
    reg.exige("raccord.echelle_a_1_pct", "le facteur d'echelle doit rester a 1 % de 1",
              "similarite sur %d reperes anatomiques" % len(cles), "<= 1,0 %",
              "%.5f %%" % ecart_pct, ecart_pct <= 1.0, tolerance=1.0)
    reg.exige("raccord.residu_2mm", "aucun repere au-dela de 2 mm",
              "similarite sur %d reperes anatomiques" % len(cles), "<= 2,00 mm",
              "%.4f mm" % rmax, rmax <= 2.0, tolerance=2.0)

    # --- recouvrement geometrique brut, sans transformation ---
    co_t = [tete.matrix_world @ v.co for v in tete.data.vertices]
    co_c = [corps.matrix_world @ v.co for v in corps.data.vertices]
    bb = lambda co: ([min(c[i] for c in co) for i in range(3)],
                     [max(c[i] for c in co) for i in range(3)])
    bt, bc = bb(co_t), bb(co_c)
    inter = [max(0.0, min(bt[1][i], bc[1][i]) - max(bt[0][i], bc[0][i])) for i in range(3)]
    R["recouvrement_boites_sans_transformation_m"] = [round(x, 6) for x in inter]
    R["les_deux_assets_se_superposent_deja"] = all(x > 0.01 for x in inter)

    R["registre"] = reg.bilan()
    R["conclusion_seuils"] = "SATISFAITS" if not reg.echecs else "NON SATISFAITS"
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nRESULTAT")
    print("  interoculaire tete  : %.3f mm" % rt["distance_interoculaire_mm"])
    print("  interoculaire corps : %.3f mm" % rc["distance_interoculaire_mm"])
    print("  facteur d'echelle   : %.6f  (ecart a 1 : %.4f %%)" % (s, ecart_pct))
    print("  residus (mm)        :", R["similarite_tete_vers_corps"]["residus_mm"])
    print("  recouvrement brut   :", R["recouvrement_boites_sans_transformation_m"])
    print("RACCORD ->", sortie, "|", R["conclusion_seuils"])
    reg.conclure()
