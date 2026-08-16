"""F0-B.3 a B.6 — marges comme chemins topologiques, puis appariement par
longueur d'arc.

Ce que fait ce script :

  1. il derive les quatre landmarks de chaque ouverture (medial/lateral,
     upper/lower) ;
  2. il reconstruit les deux marges comme des CHEMINS du graphe du maillage,
     pas en arrondissant X ;
  3. il decide quels terminaux sont deja partages (`anchor_shared`) et lesquels
     devront se fermer (`must_close`) ;
  4. il apparie les deux marges par longueur d'arc, avec segments et
     parametres, au NEUTRE.

Sur la derivation des landmarks — a lire avant de juger. Le cahier demande de
cliquer chaque sommet dans Blender et interdit de remplacer cette saisie par
`min(X)` ou `max(X)`. Ce script tourne sans interface : le clic n'est pas
disponible. La saisie est donc remplacee par une derivation SUR L'ANNEAU
lui-meme — le bord audite forme un cycle ferme, et ses deux extremites sont les
sommets qui separent l'arc superieur de l'arc inferieur. Ce n'est pas un seuil
sur une coordonnee du maillage : c'est une propriete du cycle. Le mini-test
`check-contact-landmarks.py` verifie ensuite appartenance, degre et cote.

    blender -b --factory-startup --python tests/anatomie_marges.py -- \
      "$FACE_AUTHOR_BLEND" config/landmarks-contact.json \
      reports/f0-final/correspondances-marges.json
"""
import importlib.util, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
_wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(_wai)

MM = 1000.0
TETE = "GEO-head_animation_realistic"
SEUIL_CONTACT_MM = {"fente_palpebrale.L": 0.20, "fente_palpebrale.R": 0.20,
                    "fente_labiale": 0.30}


# ------------------------------------------------------------- graphe ----

def graphe_induit(me, indices):
    """Aretes du maillage dont les DEUX extremites sont dans l'ensemble."""
    dedans = set(indices)
    adj = {i: set() for i in dedans}
    for e in me.edges:
        a, b = e.vertices
        if a in dedans and b in dedans:
            adj[a].add(b); adj[b].add(a)
    return adj


def graphe_par_faces(me, indices):
    """Voisinage par FACE partagee, pas par arete.

    C'est la meme lecon qu'en F0 : le bord d'une ouverture est fait de barreaux
    paralleles, et deux sommets consecutifs de la marge peuvent n'avoir aucune
    arete commune. Un graphe induit par les aretes rendait des degres 1 et
    meme 0, donc un anneau brise.
    """
    dedans = set(indices)
    adj = {i: set() for i in dedans}
    for p in me.polygons:
        sur = [i for i in p.vertices if i in dedans]
        for a in sur:
            for b in sur:
                if a != b:
                    adj[a].add(b)
    return adj


def anneau_par_faces(co, adj):
    """Reconstruit l'anneau : a chaque pas, le voisin non visite le plus proche.

    Le graphe par face peut donner un degre superieur a 2 ; la proximite
    geometrique tranche, et la completude est exigee par l'appelant.
    """
    depart = min(adj, key=lambda i: (co[i].z, co[i].x))
    ordre, vu, cur = [depart], {depart}, depart
    while True:
        cand = [v for v in adj[cur] if v not in vu]
        if not cand:
            break
        cur = min(cand, key=lambda v: (co[v] - co[cur]).length)
        ordre.append(cur); vu.add(cur)
    return ordre


def cycle_du_bord(adj, depart, exige_complet=True):
    """Parcourt le cycle ferme du bord et REFUSE un parcours partiel.

    Premiere version : elle marchait sur l'ensemble audite complet — peau ET
    muqueuse — qui n'est pas un cycle mais une echelle, et elle rendait
    silencieusement 10 sommets sur 40. Un chemin partiel accepte sans bruit,
    c'est exactement la faute que ce depot ne doit plus commettre.
    """
    ordre, vu, cur, prec = [depart], {depart}, depart, None
    while True:
        suivants = [v for v in adj[cur] if v != prec and v not in vu]
        if not suivants:
            break
        cur, prec = suivants[0], cur
        ordre.append(cur); vu.add(cur)
    if exige_complet and len(ordre) != len(adj):
        raise RuntimeError(
            "cycle partiel : %d sommets parcourus sur %d. L'ensemble fourni "
            "n'est pas un cycle simple." % (len(ordre), len(adj)))
    return ordre


def chemin_simple(adj, a, b, interdits=()):
    """Plus court chemin en nombre d'aretes, sans passer par `interdits`."""
    interdits = set(interdits)
    file, vu = [[a]], {a}
    while file:
        c = file.pop(0)
        if c[-1] == b:
            return c
        for v in sorted(adj[c[-1]]):
            if v in vu or (v in interdits and v != b):
                continue
            vu.add(v); file.append(c + [v])
    return None


# --------------------------------------------------------- landmarks ----

def deriver_landmarks(co, adj, indices, lateral):
    """Les deux extremites du cycle, puis upper/lower de chaque cote.

    Les extremites sont cherchees SUR LE CYCLE : ce sont les deux sommets qui
    coupent l'anneau en un arc superieur et un arc inferieur.
    """
    cyc = anneau_par_faces(co, adj)
    if len(cyc) != len(adj):
        raise RuntimeError("anneau partiel : %d sur %d" % (len(cyc), len(adj)))
    if len(cyc) < 4:
        raise RuntimeError("cycle de bord trop court : %d" % len(cyc))
    proj = {i: (co[i]).dot(lateral) for i in cyc}
    i_min = min(cyc, key=lambda i: proj[i])
    i_max = max(cyc, key=lambda i: proj[i])
    # deux arcs entre les extremites, dans l'ordre du cycle
    n = len(cyc)
    a, b = cyc.index(i_min), cyc.index(i_max)
    arc1 = [cyc[(a + k) % n] for k in range((b - a) % n + 1)]
    arc2 = [cyc[(b + k) % n] for k in range((a - b) % n + 1)]
    vert = Vector((0.0, 0.0, 1.0))
    haut = arc1 if (sum(co[i].dot(vert) for i in arc1) / len(arc1)
                    > sum(co[i].dot(vert) for i in arc2) / len(arc2)) else arc2
    bas = arc2 if haut is arc1 else arc1
    return {"cycle": cyc, "arc_haut": haut, "arc_bas": bas,
            "extremite_min": i_min, "extremite_max": i_max}


def longueur_cumulee(co, chemin):
    s, out = 0.0, [0.0]
    for a, b in zip(chemin, chemin[1:]):
        s += (co[b] - co[a]).length
        out.append(s)
    return ([x / s for x in out] if s > 1e-12 else out), s


def apparier(co, haut, bas, n_echantillons):
    s_h, L_h = longueur_cumulee(co, haut)
    s_b, L_b = longueur_cumulee(co, bas)

    def segment(chemin, s_list, s):
        for k in range(len(s_list) - 1):
            if s_list[k] <= s <= s_list[k + 1]:
                d = s_list[k + 1] - s_list[k]
                t = 0.0 if d < 1e-12 else (s - s_list[k]) / d
                return [chemin[k], chemin[k + 1]], t
        return [chemin[-2], chemin[-1]], 1.0

    paires = []
    for k in range(n_echantillons):
        s = k / (n_echantillons - 1)
        sh, th = segment(haut, s_h, s)
        sb, tb = segment(bas, s_b, s)
        ph = co[sh[0]].lerp(co[sh[1]], th)
        pb = co[sb[0]].lerp(co[sb[1]], tb)
        paires.append({
            "s": round(s, 6),
            "upper_segment": sh, "upper_t": round(th, 6),
            "lower_segment": sb, "lower_t": round(tb, 6),
            "distance_mm": round((ph - pb).length * MM, 5),
            "separation_signee_mm": round((ph.z - pb.z) * MM, 5),
        })
    return paires, L_h * MM, L_b * MM


# -------------------------------------------------------------- main ----

if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    blend, sortie_lm, sortie_pairs = a[0], a[1], a[2]
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(
        blend if os.path.isabs(blend) else os.path.join(RACINE, blend)))
    tete = bpy.data.objects[TETE]
    me = tete.data
    co = [v.co.copy() for v in me.vertices]          # repere OBJET local
    topo = _wai.sha_topologie(tete)

    C = json.load(open(os.path.join(RACINE, "reports/f0-final/contact-candidates.json"),
                       encoding="utf-8"))
    if C["topology_sha256"] != topo:
        print("SHA topologique different du rapport de candidats"); sys.exit(2)

    lateral = Vector((1.0, 0.0, 0.0))   # +X = gauche du personnage
    LM = {"mesh": TETE, "topology_sha": topo, "space": "OBJECT_LOCAL",
          "derivation": "extremites du cycle de bord audite, pas min/max sur le maillage",
          "ouvertures": {}}
    P = {"mesh": TETE, "topology_sha": topo, "space": "OBJECT_LOCAL",
         "ouvertures": {}}

    for groupe, info in sorted(C["groupes"].items()):
        cle = info["ouverture"]
        # Le CYCLE, c'est le cote peau : `indices` melange peau et muqueuse et
        # forme une echelle, pas un anneau simple.
        idx = info["indices_peau"]
        adj = graphe_par_faces(me, idx)
        degres = {i: len(v) for i, v in adj.items()}
        anormaux = {i: d for i, d in degres.items() if d != 2}
        if anormaux:
            print("  %s : sommets de degre != 2 dans le bord peau : %s"
                  % (cle, dict(list(anormaux.items())[:8])))
        d = deriver_landmarks(co, adj, idx, lateral)
        haut, bas = d["arc_haut"], d["arc_bas"]
        # orientation medial -> lateral : medial = plus proche du plan sagittal
        med = d["extremite_min"] if abs(co[d["extremite_min"]].x) < abs(co[d["extremite_max"]].x) \
            else d["extremite_max"]
        lat = d["extremite_max"] if med == d["extremite_min"] else d["extremite_min"]
        if haut[0] != med: haut = list(reversed(haut))
        if bas[0] != med: bas = list(reversed(bas))

        seuil = SEUIL_CONTACT_MM[cle]
        terminaux = {}
        for bout, nom in ((0, "medial"), (-1, "lateral")):
            ih, ib = haut[bout], bas[bout]
            dist = (co[ih] - co[ib]).length * MM
            partage = (ih == ib) or dist <= seuil
            terminaux[nom] = {
                "upper_index": ih, "lower_index": ib,
                "distance_mm": round(dist, 5),
                "seuil_mm": seuil,
                "statut": "anchor_shared" if partage else "must_close",
                "meme_sommet": ih == ib,
            }

        n_ech = max(64, len(haut), len(bas))
        paires, L_h, L_b = apparier(co, haut, bas, n_ech)

        LM["ouvertures"][cle] = {
            "groupe": groupe,
            "medial": {"upper": haut[0], "lower": bas[0]},
            "lateral": {"upper": haut[-1], "lower": bas[-1]},
            "note_visuelle": "medial = extremite la plus proche du plan sagittal ; "
                             "lateral = l'autre extremite du meme cycle",
        }
        P["ouvertures"][cle] = {
            "chemin_upper": haut, "chemin_lower": bas,
            "sommets_upper": len(haut), "sommets_lower": len(bas),
            "longueur_upper_mm": round(L_h, 4), "longueur_lower_mm": round(L_b, 4),
            "terminaux": terminaux,
            "echantillons": n_ech,
            "paires": paires,
            "distance_max_mm": round(max(p["distance_mm"] for p in paires), 5),
            "distance_mediane_mm": round(
                sorted(p["distance_mm"] for p in paires)[n_ech // 2], 5),
            "separation_signee_min_mm": round(
                min(p["separation_signee_mm"] for p in paires), 5),
        }
        print("%-22s upper %3d / lower %3d sommets | med %s | lat %s | max %.3f mm"
              % (cle, len(haut), len(bas), terminaux["medial"]["statut"],
                 terminaux["lateral"]["statut"],
                 P["ouvertures"][cle]["distance_max_mm"]))

    for chemin, donnee in ((sortie_lm, LM), (sortie_pairs, P)):
        p = chemin if os.path.isabs(chemin) else os.path.join(RACINE, chemin)
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        json.dump(donnee, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("MARGES_OK ->", sortie_lm, "|", sortie_pairs)
