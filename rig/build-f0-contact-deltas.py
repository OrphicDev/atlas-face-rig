"""F0-B.9 et B.10 — falloff geodesique, puis deltas de prototype.

Aucune shape key n'est creee dans le maitre. Le script lit l'auteur signe,
copie les coordonnees Basis en memoire, fabrique les trois poses a t = 1 et
publie, pour chaque sommet deplace, son indice et son delta en repere OBJET.

Le poids ne depend plus de la distance au sommet de bord le plus proche — ce
qui dessinait des cellules de Voronoi — mais d'une distance GEODESIQUE sur les
aretes depuis l'anneau de marge.

    blender -b --factory-startup --python rig/build-f0-contact-deltas.py -- \
      --input "$FACE_AUTHOR_BLEND" \
      --pairs reports/f0-final/correspondances-marges.json \
      --globe config/globe-fit.json \
      --falloff config/contact-falloff.json \
      --output-dir reports/f0-final/deformations \
      --debug-blend experiments/f0-contacts/FACE_F0_CONTACTS_DEBUG.blend
"""
import argparse, hashlib, importlib.util, json, math, os, struct, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
MM = 1000.0
TETE = "GEO-head_animation_realistic"

_s = importlib.util.spec_from_file_location(
    "ag", os.path.join(RACINE, "tests", "anatomie_globe.py"))
ag = importlib.util.module_from_spec(_s); _s.loader.exec_module(ag)
_w = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
wai = importlib.util.module_from_spec(_w); _w.loader.exec_module(wai)

PORTEES_MM = {"fente_palpebrale.L": 9.0, "fente_palpebrale.R": 9.0,
              "fente_labiale": 12.0}
GARDE_CONTACT_M = 0.00002    # 0,02 mm. Mesure : a 0,10 mm la course augmente de
                             # moitie et le jour REMONTE a 0,42 mm. La garde doit
                             # rester tres petite devant la fente.
AMORTISSEMENT = 0.5          # sous-relaxation : le systeme est sur-determine
ITERATIONS = 400             # 12 iterations laissaient 0,275 mm ; 400 en laissent
                             # 0,215. A 2000 la boucle DIVERGE (50 a 72 mm de
                             # deplacement) : le systeme est sur-determine et rien
                             # ne bornait la course. D'ou la borne ci-dessous.
POSES = {"blink_L": ["fente_palpebrale.L"],
         "blink_R": ["fente_palpebrale.R"],
         "mouth_close": ["fente_labiale"]}


RATIO_MIN, RATIO_MAX = 0.50, 2.00
RATIO_VISE_MIN, RATIO_VISE_MAX = 0.55, 1.90   # on VISE a l'interieur des bornes
PROJECTIONS = 4000


def projeter_longueurs(me, basis, total, marge):
    """Ramene les rapports d'aretes dans les bornes, SANS toucher la marge.

    La mesure a tranche avant d'ecrire cette fonction : sur les trois poses,
    AUCUNE arete hors bornes n'a ses deux extremites dans la marge. Les douze
    aretes fautives du clignement et les trois des levres sont toutes dans la
    zone de degrade. On peut donc les remettre dans les bornes en ne bougeant
    que des sommets LIBRES, et le contact — jour, separation signee — ne peut
    pas changer. C'est verifie apres coup, pas suppose.

    Relaxation de Gauss-Seidel deterministe : les aretes sont parcourues dans
    l'ordre de leurs indices, jamais dans l'ordre d'un ensemble.
    """
    libres = {i for i in total if i not in marge}
    if not libres:
        return total, {"aretes_corrigees": 0, "passes": 0}
    aretes = []
    for e in me.edges:
        a, b = int(e.vertices[0]), int(e.vertices[1])
        if a not in total and b not in total:
            continue
        L0 = (basis[a] - basis[b]).length
        if L0 > 1e-9:
            aretes.append((a, b, L0))
    aretes.sort()
    pos = {i: basis[i] + total[i] for i in total}
    lire = lambda i: pos.get(i, basis[i])
    touchees = set()
    passes = 0
    for passes in range(1, PROJECTIONS + 1):
        pire = 0.0
        for a, b, L0 in aretes:
            pa, pb = lire(a), lire(b)
            d = pb - pa
            L = d.length
            if L < 1e-12:
                continue
            r = L / L0
            if RATIO_VISE_MIN <= r <= RATIO_VISE_MAX:
                continue
            cible = L0 * (RATIO_VISE_MIN if r < RATIO_VISE_MIN else RATIO_VISE_MAX)
            wa = 1.0 if a in libres else 0.0
            wb = 1.0 if b in libres else 0.0
            if wa + wb <= 0.0:
                continue
            corr = d.normalized() * (L - cible)
            if a in libres:
                pos[a] = pa + corr * (wa / (wa + wb))
                touchees.add(a)
            if b in libres:
                pos[b] = pb - corr * (wb / (wa + wb))
                touchees.add(b)
            pire = max(pire, abs(r - min(max(r, RATIO_VISE_MIN), RATIO_VISE_MAX)))
        if pire < 1e-6:
            break
    hors = 0
    for a, b, L0 in aretes:
        r = (lire(b) - lire(a)).length / L0
        if r < RATIO_MIN or r > RATIO_MAX:
            hors += 1
    neuf = dict(total)
    for i in touchees:
        neuf[i] = pos[i] - basis[i]
    bouges_marge = [i for i in marge
                    if i in total and (neuf[i] - total[i]).length > 1e-12]
    return neuf, {"aretes_examinees": len(aretes), "sommets_libres": len(libres),
                  "sommets_deplaces_par_projection": len(touchees),
                  "passes": passes, "aretes_hors_bornes_apres": hors,
                  "sommets_de_marge_touches": bouges_marge}


def lisse(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def geodesique(me, co, graines, portee):
    """Dijkstra sur les aretes depuis l'anneau. Rend {indice: distance_m}."""
    import heapq
    adj = [[] for _ in co]
    for e in me.edges:
        a, b = e.vertices
        d = (co[a] - co[b]).length
        adj[a].append((b, d)); adj[b].append((a, d))
    dist = {i: 0.0 for i in graines}
    source = {i: i for i in graines}        # graine d'ou vient chaque sommet
    tas = [(0.0, i) for i in graines]
    heapq.heapify(tas)
    while tas:
        d, i = heapq.heappop(tas)
        if d > dist.get(i, 1e9) + 1e-12 or d > portee:
            continue
        for j, w in adj[i]:
            nd = d + w
            if nd <= portee and nd < dist.get(j, 1e9):
                dist[j] = nd
                source[j] = source[i]
                heapq.heappush(tas, (nd, j))
    return dist, source


def cible_paupiere(co, paire, centre, rayon, bvh, epaisseur=0.0004):
    """La marge superieure parcourt 75 % du trajet, l'inferieure 25 %, et le
    point vise est repousse HORS du globe reel."""
    ph = co[paire["upper_segment"][0]].lerp(
        co[paire["upper_segment"][1]], paire["upper_t"])
    pb = co[paire["lower_segment"][0]].lerp(
        co[paire["lower_segment"][1]], paire["lower_t"])
    cible = ph * 0.25 + pb * 0.75
    return ph, pb, cible


def cible_levres(co, paire):
    ph = co[paire["upper_segment"][0]].lerp(
        co[paire["upper_segment"][1]], paire["upper_t"])
    pb = co[paire["lower_segment"][0]].lerp(
        co[paire["lower_segment"][1]], paire["lower_t"])
    return ph, pb, (ph + pb) * 0.5


def deplacements_de_marge(co, P, cle, globes, M):
    """Delta vise pour CHAQUE sommet de l'anneau, par interpolation des paires."""
    o = P["ouvertures"][cle]
    vise = {}
    est_oeil = cle.startswith("fente_palpebrale")
    ctr = ray = None
    if est_oeil:
        cote = cle.split(".")[1]
        g = globes["eyes"][cote]
        ctr = M.inverted() @ Vector(g["center_world_xyz"])
        ray = g["radius_mm"] / MM
    # CHAQUE sommet de marge vise son propre vis-a-vis, au MEME parametre
    # d'arc. Moyenner sur les echantillons — ce que faisait la version
    # precedente — empechait la convergence exacte et laissait 0,7 a 1,1 mm de
    # jour qu'aucune intensite ne pouvait fermer.
    haut, bas = o["chemin_upper"], o["chemin_lower"]

    def parametres(chemin):
        L, cum = 0.0, [0.0]
        for x, y in zip(chemin, chemin[1:]):
            L += (co[y] - co[x]).length; cum.append(L)
        return [c / L for c in cum] if L > 1e-12 else cum

    s_h, s_b = parametres(haut), parametres(bas)
    tous = [co[i] for i in haut + bas]
    course_max = 1.20 * max((a - b).length for a in tous for b in tous) * 0.5

    def point_a(chemin, s_list, s):
        for k in range(len(s_list) - 1):
            if s_list[k] <= s <= s_list[k + 1]:
                d = s_list[k + 1] - s_list[k]
                t = 0.0 if d < 1e-12 else (s - s_list[k]) / d
                return co[chemin[k]].lerp(co[chemin[k + 1]], t)
        return co[chemin[-1]]

    out = {}
    for chemin, s_list, autre, s_autre, part in (
            (haut, s_h, bas, s_b, 0.75), (bas, s_b, haut, s_h, 0.25)):
        for k, i in enumerate(chemin):
            s = s_list[k]
            p = co[i]
            q = point_a(autre, s_autre, s)
            cible = p.lerp(q, part) if est_oeil else (p + q) * 0.5
            v = cible - p
            if est_oeil:
                w = p + v
                dd = w - ctr
                if dd.length < ray + 0.0004:
                    w = ctr + dd.normalized() * (ray + 0.0004)
                v = w - p
            anc = out.get(i)
            out[i] = v if anc is None or v.length > anc.length else anc

    # HYPOTHESE TESTEE ET REFUTEE — moindres carres.
    #
    # Le systeme est SUR-DETERMINE : 22 sommets de marge pour 64 paires, soit
    # 128 contraintes de position. Le point echantillonne etant une combinaison
    # LINEAIRE de deux sommets, j'ai suppose que le probleme etait lineaire et
    # se resolvait exactement : minimiser
    #     somme_k || p_haut(k) - (c_k + g/2 z) ||^2 + || p_bas(k) - (c_k - g/2 z) ||^2
    # avec une regularisation faible et une boucle externe pour le degagement
    # du globe.
    #
    # La mesure a REFUTE l'hypothese. Contacts V3 : 15/18 -> 12/18.
    #     blink_R.gap_cage        0,18756 -> 0,28188   (passait, ne passe plus)
    #     blink_L.gap_cage        0,21516 -> 0,27058
    #     blink_L.separation      -0,06136 -> -0,07829
    #     blink_R.separation      -0,07108 -> -0,06425
    #     mouth_close.gap_cage    0,09203 -> 0,19771
    # Seule la bouche gardait ses sondes au vert, et plus mal qu'avant.
    #
    # Deux causes possibles, non departagees : la regularisation tire les
    # deplacements vers zero, et la borne de course appliquee APRES la
    # resolution casse l'optimalite qu'on venait de calculer. Je ne les
    # departage pas ici, et je ne garde pas un solveur qui mesure moins bien.
    # L'iteration amortie reste en place.

    # ITERATION. Viser son vis-a-vis au neutre ne suffit pas : apres
    # deformation, deux arcs de cardinalites differentes (10 et 12 sommets) ne
    # se reparametrent pas identiquement, et il restait 0,44 mm de jour sur des
    # echantillons uniformes. On mesure donc le residu SUR LES ECHANTILLONS, et
    # on le redistribue aux extremites de leurs segments. Ce n'est pas un
    # reglage : c'est la boucle que la mesure reclamait.
    # La garde S'ANNULE AUX COMMISSURES. Les terminaux medial et lateral sont
    # des ancres PARTAGEES — le meme sommet pour la marge haute et la marge
    # basse — donc leur separation vaut zero par construction. Imposer 0,02 mm
    # jusqu'au bout mettait le solveur en contradiction avec sa propre ancre,
    # et il depassait juste a cote : la paire 62 sur 64 croisait de -0,061 mm a
    # gauche et -0,071 a droite, et c'etait la SEULE des soixante-quatre.
    n_paires = len(o["paires"])

    def garde_a(k):
        if n_paires < 2:
            return GARDE_CONTACT_M
        s_k = k / (n_paires - 1)
        return GARDE_CONTACT_M * math.sin(math.pi * s_k) ** 0.5

    for _ in range(ITERATIONS):
        w = [co[i] + out.get(i, Vector((0, 0, 0))) for i in range(len(co))]
        pire = 0.0
        corr = {}
        # Le residu de chaque paire est mesure AVANT de corriger, pour pouvoir
        # peser les corrections. 64 echantillons pour 22 sommets de marge : les
        # demandes se contredisent et leur MOYENNE laisse la pire paire
        # insatisfaite. C'est un probleme de minimax, pas de moindres carres :
        # on donne davantage de voix aux paires les plus fautives.
        residus = []
        for paire in o["paires"]:
            ph0 = w[paire["upper_segment"][0]].lerp(
                w[paire["upper_segment"][1]], paire["upper_t"])
            pb0 = w[paire["lower_segment"][0]].lerp(
                w[paire["lower_segment"][1]], paire["lower_t"])
            residus.append((ph0 - pb0).length)
        pire_residu = max(residus) if residus else 0.0

        for k_paire, paire in enumerate(o["paires"]):
            ph = w[paire["upper_segment"][0]].lerp(
                w[paire["upper_segment"][1]], paire["upper_t"])
            pb = w[paire["lower_segment"][0]].lerp(
                w[paire["lower_segment"][1]], paire["lower_t"])
            contact = ph.lerp(pb, 0.75) if est_oeil else (ph + pb) * 0.5
            # UN SEUL ecartement, applique au point de CONTACT, pas a chaque
            # marge separement. Plaquer chaque sommet sur la sphere laissait les
            # deux polylignes a des fleches differentes — 0,444 mm contre
            # 0,212 — et cet ecart-la FAISAIT le jour residuel de 0,275 mm.
            if est_oeil:
                dd = contact - ctr
                if dd.length < ray + 0.0004:
                    contact = ctr + dd.normalized() * (ray + 0.0004)
            # On ne vise pas la coincidence exacte : deux marges qui visent le
            # MEME point se croisent des que l'iteration depasse, et la
            # separation signee devenait negative (-0,10 mm). Elles visent donc
            # deux points separes par une garde de 0,02 mm, superieure au-dessus.
            garde = Vector((0.0, 0.0, 0.5 * garde_a(k_paire)))
            cible_h, cible_b = contact + garde, contact - garde
            pire = max(pire, (ph - pb).length)
            for seg, t, p, cible in ((paire["upper_segment"], paire["upper_t"],
                                      ph, cible_h),
                                     (paire["lower_segment"], paire["lower_t"],
                                      pb, cible_b)):
                poids_paire = 1.0
                if pire_residu > 1e-12:
                    poids_paire = 1.0 + 3.0 * (residus[k_paire] / pire_residu)
                d = (cible - p) * AMORTISSEMENT * poids_paire
                for i, poids in ((seg[0], 1.0 - t), (seg[1], t)):
                    if poids <= 1e-9: continue
                    a = corr.setdefault(i, [Vector((0, 0, 0)), 0.0])
                    a[0] += d * poids; a[1] += poids * poids_paire
        if pire * MM < 0.02:
            break
        for i, (somme, poids) in corr.items():
            if poids <= 1e-9: continue
            v = out.get(i, Vector((0, 0, 0))) + somme / poids
            # BORNE. Sans elle, l'iteration s'emballait : 50 a 72 mm de course
            # sur une fente de 10 mm de haut, et des aretes a 70x. Aucun sommet
            # ne peut se deplacer de plus que la hauteur de son ouverture.
            if v.length > course_max:
                v = v.normalized() * course_max
            out[i] = v
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--pairs", "--globe", "--falloff", "--output-dir"):
        a.add_argument(f, required=True)
    a.add_argument("--debug-blend")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    R = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(R(o.input)))
    tete = bpy.data.objects[TETE]
    me = tete.data
    M = tete.matrix_world
    basis = [v.co.copy() for v in me.vertices]
    topo = wai.sha_topologie(tete)

    P = json.load(open(R(o.pairs), encoding="utf-8"))
    G = json.load(open(R(o.globe), encoding="utf-8"))
    if P["topology_sha"] != topo:
        print("SHA topologique different des correspondances"); sys.exit(2)

    falloff = {"schema_version": 1, "topology_sha256": topo,
               "courbe": "1 - lisse(d / portee), d = distance GEODESIQUE sur aretes",
               "groupes_graines": {}, "portees_mm": PORTEES_MM}
    deltas_par_pose = {}
    for pose, cles in POSES.items():
        total = {}
        for cle in cles:
            marge = sorted({i for p in P["ouvertures"][cle]["paires"]
                            for i in p["upper_segment"] + p["lower_segment"]})
            portee = PORTEES_MM[cle] / MM
            dist, source = geodesique(me, basis, marge, portee)
            vise = deplacements_de_marge(basis, P, cle, G, M)
            falloff["groupes_graines"][cle] = {
                "sommets_de_marge": len(marge),
                "portee_mm": PORTEES_MM[cle],
                "sommets_dans_la_portee": len(dist),
            }
            for i, d in dist.items():
                w = 1.0 - lisse(d / portee)
                if w <= 1e-6: continue
                base = vise.get(i)
                if base is None:
                    # Un sommet hors marge suit la cible de LA graine dont il
                    # descend geodesiquement. La version precedente moyennait
                    # toutes les graines a portee euclidienne : elle tirait des
                    # sommets eloignes dans une direction qui n'etait celle
                    # d'aucune marge, et dix aretes HORS MARGE depassaient 2,0x.
                    base = vise.get(source.get(i))
                    if base is None: continue
                total[i] = total.get(i, Vector((0, 0, 0))) + base * w
        marge_totale = set()
        for cle in cles:
            for pr in P["ouvertures"][cle]["paires"]:
                marge_totale |= set(pr["upper_segment"]) | set(pr["lower_segment"])
        total, info = projeter_longueurs(me, basis, total, marge_totale)
        falloff.setdefault("projection_longueurs", {})[pose] = info
        if info.get("sommets_de_marge_touches"):
            print("PROJECTION A TOUCHE LA MARGE :", info["sommets_de_marge_touches"])
            sys.exit(2)
        deltas_par_pose[pose] = total
        print("  %-12s %4d sommets deplaces, max %.3f mm | projection : "
              "%d sommets, %d passes, %d arete(s) hors bornes apres"
              % (pose, len(total),
                 max((v.length for v in total.values()), default=0.0) * MM,
                 info["sommets_deplaces_par_projection"], info["passes"],
                 info["aretes_hors_bornes_apres"]))

    os.makedirs(R(o.output_dir), exist_ok=True)
    for pose, total in deltas_par_pose.items():
        idx = sorted(total)
        h = hashlib.sha256()
        for i in idx:
            h.update(struct.pack("<I3f", i, *total[i]))
        D = {"pose": pose, "mesh": TETE, "unite": "METRES",
             "repere": "OBJECT_LOCAL", "topology_sha256": topo,
             "sha256_du_tableau": h.hexdigest(),
             "portees_mm": PORTEES_MM,
             "sommets_deplaces": len(idx),
             "deltas": [{"index": i,
                         "delta_object_local_xyz": [round(float(x), 9)
                                                    for x in total[i]]}
                        for i in idx]}
        json.dump(D, open(os.path.join(R(o.output_dir), pose + ".cage-delta.json"),
                          "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    json.dump(falloff, open(R(o.falloff), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    if o.debug_blend:
        for pose, total in deltas_par_pose.items():
            d = me.copy()
            dup = bpy.data.objects.new("DBG_" + pose + "_100", d)
            dup.matrix_world = M.copy()
            bpy.context.scene.collection.objects.link(dup)
            for m in list(dup.modifiers): dup.modifiers.remove(m)
            for i, v in total.items():
                d.vertices[i].co = basis[i] + v
            d.update()
        c = R(o.debug_blend)
        os.makedirs(os.path.dirname(c), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=c, copy=True)

    # le maitre n'a pas de shape key et n'a pas ete sauvegarde
    print("DELTAS_OK shape_keys du maitre :",
          len(me.shape_keys.key_blocks) if me.shape_keys else 0)
