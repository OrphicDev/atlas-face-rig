"""F0-D.8 mini-test — barycentrique CONTRE Surface Deform, meme regle.

Le tutoriel demande de comparer p50, p95, max, mouvement hors groupe,
intersections, UV et temps pour les deux methodes. Les deux bilans sont
produits par `rig/f0_body_commun.py`, donc par la MEME regle.

Le rapport dit toujours d'ou viennent ses chiffres : du corps reel si l'asset
est la, du banc synthetique sinon. Comparer un chiffre reel a un chiffre
synthetique sans le dire serait une conclusion fabriquee.

    python3 tests/f0-body-methodes-ab.py \
      --report reports/f0-final/body-methodes-ab.json
"""
import argparse, json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

CHAMPS = ["deplacement_dans_le_masque_mm", "deplacement_hors_masque_mm",
          "auto_intersections", "sommets_doubles", "aretes_ouvertes",
          "aretes_non_manifold", "faces_inversees", "uv_sha256", "secondes"]


def lire(rel):
    p = os.path.join(RACINE, rel)
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    reg = Registre("body-methodes-ab")

    SD = lire("reports/f0-final/body-surface-deform.json") or {}
    BANC = lire("reports/f0-final/body-banc-synthetique.json") or {}
    reel = SD.get("status") == "OK"

    if reel:
        source = "corps reel"
        bary = (lire("reports/f0-final/body-transfer.json") or {}).get("poses", {})
        sd = SD.get("poses", {})
        A = {"barycentrique": bary.get("blink_L_100"), "surface_deform": sd.get("blink_L_100")}
    else:
        source = "banc synthetique"
        A = {"barycentrique": BANC.get("barycentrique"),
             "surface_deform": BANC.get("surface_deform")}
        reg.saute("ab.corps_reel",
                  "la comparaison porte sur le vrai corps",
                  "asset hors depot absent : %s"
                  % SD.get("raison", "rapport Surface Deform absent"))

    R = {"source_des_chiffres": source, "methodes": A,
         "avertissement": None if reel else
         "chiffres du banc synthetique : la METHODE est comparee, pas le "
         "maillage reel. Aucune conclusion sur le raccord n'en est tiree."}

    manquant = [k for k, v in A.items() if not v]
    reg.exige("ab.deux_bilans", "les deux voies ont produit un bilan",
              source, [], manquant, not manquant)

    if not manquant:
        tab = {}
        for champ in CHAMPS:
            tab[champ] = {k: A[k].get(champ) for k in A}
        R["comparaison"] = tab
        dm = {k: A[k]["deplacement_dans_le_masque_mm"]["max"] for k in A}
        ecart = abs(dm["barycentrique"] - dm["surface_deform"])
        R["ecart_max_dans_le_masque_mm"] = round(ecart, 6)
        reg.exige("ab.meme_amplitude",
                  "les deux voies rendent la meme amplitude dans le masque",
                  source, "<= 0,05 mm", round(ecart, 6), ecart <= 0.05,
                  tolerance=0.05)
        hg = {k: A[k]["deplacement_hors_masque_mm"]["max"] for k in A}
        reg.exige("ab.aucune_fuite_hors_groupe",
                  "aucune des deux voies ne bouge un sommet hors du groupe",
                  source, "<= 0,01 mm", max(hg.values()),
                  max(hg.values()) <= 0.01, tolerance=0.01)
        xi = {k: A[k]["auto_intersections"] for k in A}
        reg.exige("ab.aucune_intersection",
                  "aucune des deux voies n'auto-intersecte", source, 0,
                  max(xi.values()), max(xi.values()) == 0)
        uv = {k: A[k]["uv_sha256"] for k in A}
        reg.exige("ab.uv_intactes", "les UV survivent aux deux voies",
                  source, "empreintes identiques",
                  "identiques" if len(set(uv.values())) == 1 else "differentes",
                  len(set(uv.values())) == 1)
        R["plus_rapide"] = min(A, key=lambda k: A[k]["secondes"])

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("AB", "OK" if ok else "ECHEC", "->", o.report, "| source :", source)
    sys.exit(0 if ok else 2)
