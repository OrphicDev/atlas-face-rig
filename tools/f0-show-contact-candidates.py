"""F0-B.2 — groupes de diagnostic des regions de contact, sans deviner a l'oeil.

Reprend les bords DEJA audites dans `reports/f0/audit-topologie.json` (les
memes `indices` que la sonde du seuil 0,15) et en fait des vertex groups
lisibles dans Blender :

    DBG_eye_margin.L   DBG_eye_margin.R   DBG_lip_margin

Aucune coordonnee n'est modifiee. Le script n'ecrit que des groupes et un
rapport.

    blender -b experiments/f0-contacts/FACE_F0_CONTACTS_WORK.blend \
      --python tools/f0-show-contact-candidates.py -- \
      --report reports/f0-final/contact-candidates.json
"""
import argparse, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
_wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(_wai)

TETE = "GEO-head_animation_realistic"
GROUPES = {
    "DBG_eye_margin.L": "fente_palpebrale.L",
    "DBG_eye_margin.R": "fente_palpebrale.R",
    "DBG_lip_margin": "fente_labiale",
}


def poser_groupe(obj, nom, indices):
    vieux = obj.vertex_groups.get(nom)
    if vieux:
        obj.vertex_groups.remove(vieux)
    g = obj.vertex_groups.new(name=nom)
    g.add(list(indices), 1.0, "REPLACE")
    return g


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    a.add_argument("--audit", default="reports/f0/audit-topologie.json")
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])

    tete = bpy.data.objects.get(TETE)
    if tete is None or tete.type != "MESH":
        print("maillage principal absent :", TETE); sys.exit(2)
    print("objet lu :", tete.name, len(tete.data.vertices), "sommets")

    chemin = o.audit if os.path.isabs(o.audit) else os.path.join(RACINE, o.audit)
    A = json.load(open(chemin, encoding="utf-8"))
    ouvertures = {x["nom"]: x for x in A.get("ouvertures", []) if x.get("nom")}
    absents = [v for v in GROUPES.values() if v not in ouvertures]
    if absents:
        print("ouvertures absentes du rapport d'audit :", absents); sys.exit(2)

    R = {"objet": tete.name,
         "topology_sha256": _wai.sha_topologie(tete),
         "source_audit": o.audit, "groupes": {}}
    n_max = len(tete.data.vertices)
    for nom, cle in GROUPES.items():
        idx = sorted(ouvertures[cle]["indices"])
        peau = sorted(ouvertures[cle]["indices_peau"])
        hors = [i for i in idx if not 0 <= i < n_max]
        if hors:
            print("indices hors du maillage pour %s : %s" % (nom, hors[:8]))
            sys.exit(2)
        poser_groupe(tete, nom, idx)
        R["groupes"][nom] = {
            "ouverture": cle, "sommets": len(idx), "indices": idx,
            "sommets_cote_peau": len(peau), "indices_peau": peau,
            "largeur_mm": ouvertures[cle]["largeur_mm"],
            "hauteur_mm": ouvertures[cle]["hauteur_mm"],
        }
        print("  %-20s %3d sommets (%d cote peau)" % (nom, len(idx), len(peau)))

    # aucune coordonnee touchee : on le prouve en republiant l'empreinte
    R["topology_sha256_apres"] = _wai.sha_topologie(tete)
    R["topologie_intacte"] = R["topology_sha256"] == R["topology_sha256_apres"]

    sortie = o.report if os.path.isabs(o.report) else os.path.join(RACINE, o.report)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("CANDIDATS_OK ->", o.report, "| topologie intacte :", R["topologie_intacte"])
    sys.exit(0 if R["topologie_intacte"] else 2)
