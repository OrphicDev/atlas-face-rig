"""F0-F.3 bis — le runner refuse-t-il ce qu'il doit refuser ?

Deux epreuves, exigees par le tutoriel, et aucune ne touche un artefact
versionne : tout se passe dans un dossier temporaire.

  1. un seuil de clignement serre a 0,00001 mm doit faire ECHOUER la suite ;
  2. un script qui leve RuntimeError doit etre enregistre comme faute
     TECHNIQUE (code 1, aucun rapport), pas classe comme un FAIL metier permis.

    python3 tests/run-f0-final-negatif.py \
      --report reports/f0-final/runner-negatif.json
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"

SCRIPT_QUI_LEVE = '''import sys
raise RuntimeError("panne technique deliberee")
'''


def lancer(argv):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=RACINE)
    return r.returncode, r.stdout[-2000:], r.stderr[-2000:]


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    reg = Registre("runner-negatif")
    R = {}

    with tempfile.TemporaryDirectory() as d:
        # ---- 1. un seuil serre doit faire echouer
        src = os.path.join(RACINE, "tests", "f0-multires-v2.py")
        # La copie doit vivre dans tests/ : le script calcule la racine du
        # depot depuis son propre chemin, et depuis /var/folders il ne trouvait
        # plus ses imports — le runner rendait 1, une panne, pas un echec
        # metier. Elle est retiree dans tous les cas (try/finally).
        copie = os.path.join(RACINE, "tests", "_tmp_seuil_serre.py")
        texte = open(src, encoding="utf-8").read()
        # On vise le SEUIL, pas un « 0.2 » quelconque. Remplacer le premier
        # motif venu cassait le script : le runner rendait alors 1 (panne
        # technique) et une sonde qui se contentait de « code non nul » y
        # voyait une reussite. Une mutation qui casse le fichier ne prouve rien.
        avant = texte
        motif = "v is not None and v <= 0.20, tolerance=0.20"
        remplacement = "v is not None and v <= 0.00001, tolerance=0.00001"
        texte = texte.replace(motif, remplacement)
        modifie = texte != avant
        open(copie, "w", encoding="utf-8").write(texte)
        reg.exige("negatif.seuil_modifie", "le seuil a bien ete serre dans la COPIE",
                  os.path.basename(src), True, modifie, modifie)
        try:
          if modifie:
            code, out, err = lancer(
                [BLENDER, "--background", "--factory-startup", "--python-exit-code",
                 "1", "--python", copie, "--",
                 "source/FACE_F0_FOUNDATION_FINAL.blend",
                 os.path.join(d, "serre.json")])
            J = {}
            try:
                J = json.load(open(os.path.join(d, "serre.json"), encoding="utf-8"))
            except Exception:
                pass
            b = J.get("registre", {}) if isinstance(J.get("registre"), dict) else {}
            tombees = [x["id"] for x in b.get("sondes", [])
                       if x.get("status") == "FAIL"]
            vise = [x for x in tombees if x.startswith("clignement.")]
            reg.exige("negatif.seuil_serre_echoue",
                      "un seuil a 0,00001 mm fait echouer la suite en ECHEC METIER",
                      "copie temporaire", "code 2", code, code == 2)
            reg.exige("negatif.seuil_serre_bonnes_sondes",
                      "ce sont les sondes de clignement qui tombent",
                      "%d sondes en echec" % len(tombees), ">= 2 clignement",
                      len(vise), len(vise) >= 2)
            R["seuil_serre"] = {"code": code, "sondes_tombees": tombees,
                                "stdout_fin": out[-600:]}
          else:
            reg.saute("negatif.seuil_serre_echoue",
                      "un seuil serre fait echouer la suite",
                      "aucun motif de seuil reconnu dans le script")
        finally:
            if os.path.isfile(copie):
                os.remove(copie)

        # ---- 2. une panne technique n'est pas un FAIL metier
        panne = os.path.join(d, "panne.py")
        open(panne, "w", encoding="utf-8").write(SCRIPT_QUI_LEVE)
        code, out, err = lancer(
            [BLENDER, "--background", "--factory-startup", "--python-exit-code",
             "1", "--python", panne])
        rapport_absent = not os.path.isfile(os.path.join(d, "panne.json"))
        technique = code == 1 and "RuntimeError" in (err + out)
        reg.exige("negatif.panne_technique",
                  "une exception rend un code technique, pas un FAIL metier",
                  "script qui leve RuntimeError", "code 1 et trace",
                  "code %d, trace %s" % (code, "oui" if "RuntimeError" in (err + out)
                                         else "non"), technique)
        reg.exige("negatif.panne_sans_rapport",
                  "une panne n'ecrit aucun rapport a interpreter",
                  "code 1", True, rapport_absent, rapport_absent)
        R["panne"] = {"code": code, "trace": "RuntimeError" in (err + out)}

    # ---- 3. la convention de codes est-elle celle du depot ?
    reg.exige("negatif.convention",
              "0 = succes, 2 = echec metier, 1 = faute technique",
              "convention du depot", "1 pour une exception",
              R.get("panne", {}).get("code"), R.get("panne", {}).get("code") == 1)

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("RUNNER_NEGATIF", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
