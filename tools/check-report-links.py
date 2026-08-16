"""F0-F.8 bis — les liens et les chiffres d'un rapport tiennent-ils ?

Trois controles :

  1. tout lien Markdown local designe un fichier qui existe ;
  2. aucun lien ne pointe vers un temporaire, un cache ou /tmp ;
  3. les valeurs citees dans le rapport sont RELUES dans leur JSON source et
     comparees — un chiffre saisi a la main est refuse.

Le troisieme controle s'appuie sur le fichier `.valeurs.json` que le
generateur publie a cote du rapport : il dit, pour chaque valeur, d'ou elle
vient. Sans lui, le controle serait decoratif.

    python3 tools/check-report-links.py \
      --report reports/f0-final/RAPPORT_F0_FINAL.md \
      --output reports/f0-final/report-links.json
"""
import argparse, json, os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

LIEN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INTERDITS = ("/tmp", "/var/folders", "__pycache__", "_tmp_", "/private/tmp")


def resoudre(base, cible):
    if cible.startswith(("http://", "https://", "#", "mailto:")):
        return None
    return os.path.normpath(os.path.join(os.path.dirname(base), cible.split("#")[0]))


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    a.add_argument("--output", required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    chemin = Rp(o.report)
    texte = open(chemin, encoding="utf-8").read()
    reg = Registre("check-report-links")
    R = {"rapport": o.report}

    liens = [(t, c) for t, c in LIEN.findall(texte)]
    casses, interdits = [], []
    for t, c in liens:
        p = resoudre(chemin, c)
        if p is None:
            continue
        if any(x in c for x in INTERDITS):
            interdits.append(c)
        if not os.path.exists(p):
            casses.append(c)
    reg.exige("liens.resolvent", "chaque lien local designe un fichier existant",
              "%d liens" % len(liens), 0, len(casses), not casses)
    reg.exige("liens.aucun_temporaire", "aucun lien vers un temporaire ou un cache",
              "%d liens" % len(liens), [], interdits, not interdits)
    R["liens"] = [c for _, c in liens]
    R["casses"], R["interdits"] = casses, interdits

    # --- les chiffres viennent-ils bien de leur JSON ?
    sidecar = chemin.replace(".md", ".valeurs.json")
    if not os.path.isfile(sidecar):
        reg.saute("valeurs.rederivees", "les valeurs citees viennent des JSON",
                  "aucun fichier .valeurs.json a cote du rapport")
        R["valeurs"] = None
    else:
        V = json.load(open(sidecar, encoding="utf-8"))
        divergentes, absentes = [], []
        for cle, e in V.items():
            src = os.path.join(RACINE, e["source"])
            if not os.path.isfile(src):
                absentes.append(cle); continue
            J = json.load(open(src, encoding="utf-8"))
            m = re.match(r"(?:(\w+)\.)?sondes\[id=(.+)\]\.(\w+)$", e["cle"])
            if m:
                racine = J.get(m.group(1), {}) if m.group(1) else J
                trouve = next((s.get(m.group(3))
                               for s in racine.get("sondes", [])
                               if s.get("id") == m.group(2)), None)
            else:
                trouve = J
                for part in e["cle"].split("."):
                    trouve = (trouve or {}).get(part) if isinstance(trouve, dict) else None
            if trouve != e["valeur"]:
                divergentes.append([cle, e["valeur"], trouve])
        reg.exige("valeurs.rederivees",
                  "chaque valeur citee est retrouvee dans son JSON",
                  "%d valeurs tracees" % len(V), 0, len(divergentes),
                  not divergentes)
        reg.exige("valeurs.sources_presentes", "chaque source citee existe",
                  "%d valeurs" % len(V), [], absentes, not absentes)
        R["valeurs"] = {"tracees": len(V), "divergentes": divergentes,
                        "sources_absentes": absentes}

    # --- un rapport qui annonce un gate passe alors qu'il ne l'est pas ?
    annonce_terminee = "F0 TERMINÉE" in texte
    contient_non = "| **non** |" in texte
    reg.exige("rapport.coherent",
              "le rapport n'annonce pas F0 TERMINEE avec des conditions non remplies",
              "lecture du tableau du gate", False,
              annonce_terminee and contient_non,
              not (annonce_terminee and contient_non))

    R["registre"] = reg.bilan()
    p = Rp(o.output); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("LIENS", "OK" if ok else "ECHEC", "->", o.output)
    sys.exit(0 if ok else 2)
