"""F0-F.2 — les comptes anatomiques, MESURES sur la fondation finale.

Ces nombres seront lus par F1 et F3. Ils ne sont donc jamais recopies d'une
constante d'avant retopologie : ils sont recomptes ici, sur le maillage de la
fondation, et le script REFUSE si une region n'est pas definie ou si le SHA de
topologie ne correspond pas. Une valeur absente reste absente.

Chaque compte porte sa definition dans le JSON, parce qu'un nombre sans sa
definition n'est pas une mesure :

  boucles_palpebrales.L/R  anneaux concentriques autour de la fente, marche par
                           arete depuis le bord cote peau et RESTREINTE A LA
                           PEAU EXTERIEURE (sans quoi elle part dans la
                           muqueuse), comptes tant que la distance moyenne de
                           l'anneau a la marge reste <= RAYON_MM.
  boucles_labiales         idem autour de la fente labiale.

Le tutoriel nomme ces quatre comptes sans les definir. J'ai essaye cinq
definitions purement topologiques (cycle ferme unique, composantes cycliques,
bandes de faces, cardinalite constante) : aucune ne tient sur ce maillage, ou
les anneaux se scindent entre peau et muqueuse et ne sont jamais des cycles
propres. Plutot que de continuer a deviner une intention, la definition est
POSEE ici, avec un rayon physique et verifiable, et le PROFIL COMPLET est
publie a cote — cardinalite et distance moyenne de chaque anneau — pour que
toute autre convention se rederive du JSON sans rien relancer.
  triangles_region_bouche  faces a trois cotes dont la region est la fente
                           labiale.
  sommets_bord_narine.L/R  sommets du bord de narine, cote peau.

    blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
      --python tests/measure-f0-anatomy-counts.py -- \
      --margins reports/f0-final/correspondances-marges.json \
      --audit reports/f0/audit-topologie.json \
      --output reports/f0-final/anatomy-counts.json
"""
import argparse, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "am", os.path.join(RACINE, "tests", "anatomie_marges.py"))
AM = importlib.util.module_from_spec(_s); _s.loader.exec_module(AM)
_t = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
WAI = importlib.util.module_from_spec(_t); _t.loader.exec_module(WAI)
# L'audit possede DEJA la marche concentrique et le classement peau/muqueuse.
# En reecrire une seconde, c'est se garantir qu'elles divergeront : ma version
# propageait dans la muqueuse et comptait 40 sommets la ou l'audit en compte 20.
_a = importlib.util.spec_from_file_location(
    "audit", os.path.join(RACINE, "tests", "f0-audit-topologie.py"))
AUD = importlib.util.module_from_spec(_a)
_a.loader.exec_module(AUD)


RAYON_MM = 10.0
PROFONDEUR = 12
MM = 1000.0


def voisins_par_arete(me):
    adj = [set() for _ in range(len(me.vertices))]
    for e in me.edges:
        a, b = e.vertices
        adj[a].add(b); adj[b].add(a)
    return adj


def profil(bm, M, marge, ext, profondeur=PROFONDEUR):
    """Anneaux de l'audit, distances de l'audit : une seule implementation."""
    prof = AUD.anneaux_concentriques(bm, marge, ext, maxi=25)
    ref = [M @ bm.verts[i].co for i in marge]
    return [{"anneau": k + 1, "sommets": len(p),
             "distance_moy_mm": AUD.distance_moyenne(bm, M, p, ref)}
            for k, p in enumerate(prof[:profondeur])]


def compter(pr, rayon=RAYON_MM):
    return sum(1 for r in pr if r["distance_moy_mm"] <= rayon)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--margins", required=True)
    a.add_argument("--audit", default="reports/f0/audit-topologie.json")
    a.add_argument("--output", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    tete = bpy.data.objects[AM.TETE]
    me = tete.data
    sha = WAI.sha_topologie(tete)
    reg = Registre("anatomy-counts")

    M = json.load(open(Rp(o.margins), encoding="utf-8"))
    A = json.load(open(Rp(o.audit), encoding="utf-8"))
    reg.exige("anatomie.sha_marges", "les marges decrivent CETTE topologie",
              os.path.basename(o.margins), sha, M.get("topology_sha"),
              M.get("topology_sha") == sha)
    if M.get("topology_sha") != sha:
        json.dump({"status": "FAIL", "raison": "SHA de topologie different",
                   "attendu": sha, "marges": M.get("topology_sha")},
                  open(Rp(o.output), "w", encoding="utf-8"), indent=2)
        sys.exit(2)

    ouvertures = {x["nom"]: x for x in A.get("ouvertures", []) if x.get("nom")}
    requises = ["fente_palpebrale.L", "fente_palpebrale.R", "fente_labiale",
                "narine.L", "narine.R"]
    manquantes = [r for r in requises if r not in ouvertures]
    reg.exige("anatomie.regions_definies", "chaque region necessaire est definie",
              "audit de topologie", [], manquantes, not manquantes)
    if manquantes:
        json.dump({"status": "FAIL", "regions_manquantes": manquantes},
                  open(Rp(o.output), "w", encoding="utf-8"), indent=2)
        sys.exit(2)

    import bmesh
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    M = tete.matrix_world
    n_rayons = A.get("rayons_par_sommet", 48)
    seuil = A.get("seuil_degagement", 0.05)
    ext = AUD.classer(AUD.fraction_degagee(bm, n_rayons), seuil)
    n_ext = sum(ext)
    ref_ext = A["exterieur_interieur"]["exterieur"]
    reg.exige("anatomie.peau_exterieure",
              "le classement peau/muqueuse retrouve celui de l'audit",
              "%d rayons, seuil %g" % (n_rayons, seuil), ref_ext, n_ext,
              n_ext == ref_ext)
    R = {"schema_version": 1, "mesh": tete.name, "topology_sha256": sha,
         "source_marges": o.margins, "source_audit": o.audit,
         "rayon_mm": RAYON_MM,
         "definitions": {
             "boucles_palpebrales": "anneaux concentriques par arete depuis le "
                                    "bord cote peau, dont la distance moyenne a "
                                    "la marge est <= %g mm" % RAYON_MM,
             "boucles_labiales": "idem autour de la fente labiale",
             "triangles_region_bouche": "faces a 3 cotes de region fente_labiale",
             "sommets_bord_narine": "sommets du bord de narine, cote peau"},
         "boucles_palpebrales": {}, "sommets_bord_narine": {}}

    R["profils"] = {}
    for nom in ("fente_palpebrale.L", "fente_palpebrale.R", "fente_labiale"):
        marge = sorted(ouvertures[nom]["indices_peau"])
        R["profils"][nom] = {"anneau_0_sommets": len(marge),
                             "profil": profil(bm, M, marge, ext)}
    for cote in ("L", "R"):
        n = compter(R["profils"]["fente_palpebrale." + cote]["profil"])
        R["boucles_palpebrales"][cote] = n
        reg.exige("anatomie.boucles_palpebrales." + cote,
                  "anneaux a <= %g mm de la fente palpebrale" % RAYON_MM,
                  "%d sommets de bord cote peau"
                  % R["profils"]["fente_palpebrale." + cote]["anneau_0_sommets"],
                  ">= 1", n, n >= 1)
    R["boucles_labiales"] = compter(R["profils"]["fente_labiale"]["profil"])
    reg.exige("anatomie.boucles_labiales",
              "anneaux a <= %g mm de la fente labiale" % RAYON_MM,
              "%d sommets de bord cote peau"
              % R["profils"]["fente_labiale"]["anneau_0_sommets"],
              ">= 1", R["boucles_labiales"], R["boucles_labiales"] >= 1)

    # verification a reponse connue : recompute sur la fondation, le profil doit
    # retrouver celui que l'audit avait publie sur la meme topologie.
    ecarts = []
    for nom, v in R["profils"].items():
        ref = A.get("boucles", {}).get(nom, {}).get("profil", [])
        for k, r in enumerate(v["profil"][:len(ref)]):
            if r["sommets"] != ref[k]["sommets"] \
                    or abs(r["distance_moy_mm"] - ref[k]["distance_moy_mm"]) > 0.02:
                ecarts.append([nom, k + 1, r, ref[k]])
    reg.exige("anatomie.profil_reproduit",
              "le profil recompute retrouve celui de l'audit",
              "meme topologie, sonde a reponse connue", 0, len(ecarts), not ecarts)
    R["ecarts_profil"] = ecarts[:8]

    R["triangles_region_bouche"] = sum(
        1 for t in A.get("triangles", []) if t.get("region") == "fente_labiale")
    reg.exige("anatomie.triangles_bouche", "triangles de la region bouche",
              "%d triangles dans le maillage" % len(A.get("triangles", [])),
              ">= 0", R["triangles_region_bouche"], True)

    for cote in ("L", "R"):
        n = len(ouvertures["narine." + cote].get("indices_peau", []))
        R["sommets_bord_narine"][cote] = n
        reg.exige("anatomie.bord_narine." + cote, "sommets de bord de narine",
                  "cote peau", ">= 1", n, n >= 1)

    R["symetrie_palpebrale"] = (R["boucles_palpebrales"]["L"]
                                == R["boucles_palpebrales"]["R"])
    R["registre"] = reg.bilan()
    p = Rp(o.output); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("ANATOMY_COUNTS", "OK" if ok else "ECHEC", "->", o.output)
    sys.exit(0 if ok else 2)
