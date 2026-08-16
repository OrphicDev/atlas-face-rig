"""F0-A.6 — runner des suites F0, en mode `baseline` ou `final`.

`baseline` n'accepte un echec que si son identifiant figure, a l'identique,
dans le fichier de reference. La comparaison porte sur l'ENSEMBLE des
identifiants et sur leurs champs (objet, cote, metrique, seuil) — jamais sur
leur nombre : un FAIL nouveau doit faire echouer le runner meme si le total ne
bouge pas.

`final` ne charge aucune reference et refuse tout FAIL, tout code non nul et
tout SKIP critique.

Aucune commande n'est lancee via un shell : chaque argument est passe dans une
liste, de sorte qu'un espace dans un chemin ne change pas la commande.

    blender -b --factory-startup --python-exit-code 1 \
      --python tests/run-f0-final.py -- \
      --mode baseline --expected tests/baselines/c0885ae-expected.json \
      --output reports/reprise/c0885ae
"""
import argparse, json, os, subprocess, sys, time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = sys.argv[0] if os.path.basename(sys.argv[0]).lower().startswith("blender") \
    else os.environ.get("ATLAS_BLENDER", "blender")


def args_apres_separateur(argv):
    return argv[argv.index("--") + 1:] if "--" in argv else []


def chemin(*p):
    return os.path.join(RACINE, *p)


def suites(mode, entree):
    """(nom, argv, rapport). Les chemins sont relatifs a la racine du depot."""
    base = [BLENDER, "--background", "--factory-startup", "--python-exit-code", "1"]
    src = entree or chemin("source", "FACE_BASE_LOCKED.blend")
    sortie = "reports/f0-final" if mode == "final" else "reports/reprise/c0885ae"
    return [
        ("verrou_positif",
         base + ["--python", chemin("tests", "verrou-topologie.py"), "--",
                 src, chemin("tests", "verrou-topologie.json")], None),
        ("verrou_negatif",
         base + ["--python", chemin("tests", "verrou-topologie-negatif.py"), "--",
                 src, chemin("tests", "verrou-topologie.json"),
                 chemin(sortie, "verrou-negatif.json")],
         chemin(sortie, "verrou-negatif.json")),
        ("multires",
         base + ["--python", chemin("tests", "f0-multires-v2.py"), "--",
                 src, chemin(sortie, "multires-ab-v2.json")],
         chemin(sortie, "multires-ab-v2.json")),
        ("raccord",
         base + ["--python", chemin("tests", "f0-raccord-corps.py"), "--",
                 chemin(sortie, "raccord-corps.json")],
         chemin(sortie, "raccord-corps.json")),
        ("hygiene",
         base + ["--python", chemin("tests", "f0-hygiene-blend.py"), "--",
                 src, chemin(sortie, "hygiene-blend-raw.json")],
         chemin(sortie, "hygiene-blend-raw.json")),
    ] + (suites_v3(src, sortie) if mode == "final" else [])


def suites_v3(src, sortie):
    """Les suites F0-B a F0-F. Elles font foi ; celles d'au-dessus sont la
    provenance rejouee."""
    base = [BLENDER, "--background", "--factory-startup", "--python-exit-code", "1"]
    py = [sys.executable]
    spike = chemin("experiments", "gltf-spike", "spike.blend")
    glb = chemin("exports", "atlas-face-spike.glb")
    return [
        ("anatomy_counts",
         [BLENDER, "--background", src, "--python-exit-code", "1",
          "--python", chemin("tests", "measure-f0-anatomy-counts.py"), "--",
          "--margins", "reports/f0-final/correspondances-marges.json",
          "--audit", "reports/f0/audit-topologie.json",
          "--output", chemin(sortie, "anatomy-counts.json")],
         chemin(sortie, "anatomy-counts.json")),
        ("contrat_de_sortie",
         py + [chemin("tools", "check-f0-output-contract.py"), "--verify",
               "--negatif", "--contract",
               "source/FACE_F0_FOUNDATION_FINAL.output-contract.json",
               "--report", chemin(sortie, "contract-check.json")],
         chemin(sortie, "contract-check.json")),
        ("gltf_conformite",
         py + [chemin("tools", "validate_glb.py"), "--input", glb,
               "--report", chemin(sortie, "validation-glb.json")],
         chemin(sortie, "validation-glb.json")),
        ("gltf_conformite_negatif",
         py + [chemin("tests", "validate-glb-negatif.py"), "--input", glb,
               "--report", chemin(sortie, "validation-glb-negatif.json")],
         chemin(sortie, "validation-glb-negatif.json")),
        ("gltf_aller_retour",
         base + ["--python", chemin("experiments", "gltf-spike", "import_spike.py"),
                 "--", "--input", glb, "--source", spike,
                 "--report", chemin("experiments", "gltf-spike", "roundtrip.json"),
                 "--animation-reference",
                 chemin("experiments", "gltf-spike", "spike-reference.json")],
         chemin("experiments", "gltf-spike", "roundtrip.json")),
        ("runtime_glb",
         base + ["--python", chemin("tests", "runtime-glb.py"), "--",
                 "--input", glb, "--source", spike,
                 "--animation-reference",
                 chemin("experiments", "gltf-spike", "spike-reference.json"),
                 "--report", chemin(sortie, "runtime-glb.json")],
         chemin(sortie, "runtime-glb.json")),
        ("runtime_pivot_negatif",
         [BLENDER, "--background", spike, "--python-exit-code", "1",
          "--python", chemin("tests", "runtime-pivot-negatif.py"), "--",
          "--motion", "config/jaw-motion.json",
          "--report", chemin(sortie, "runtime-pivot-negatif.json")],
         chemin(sortie, "runtime-pivot-negatif.json")),
        ("coupe_sagittale",
         [BLENDER, "--background",
          "source/FACE_F0_FOUNDATION_FINAL.blend",
          "--python", chemin("tools", "render-f0-sagittal.py"), "--",
          "--output-dir", "renders/f0-final/sagittal",
          "--report", chemin(sortie, "sagittal-render.json")],
         chemin(sortie, "sagittal-render.json")),
        ("wireframes",
         [BLENDER, "--background",
          "source/FACE_F0_FOUNDATION_FINAL.blend",
          "--python", chemin("tools", "render-f0-wireframes.py"), "--",
          "--output-dir", "renders/f0-final/wireframes",
          "--report", chemin(sortie, "wireframes.json")],
         chemin(sortie, "wireframes.json")),
    ]


def lire_registre(chemin_json):
    if not chemin_json or not os.path.isfile(chemin_json):
        return None
    try:
        R = json.load(open(chemin_json, encoding="utf-8"))
    except Exception as e:
        return {"illisible": str(e)}
    for cle in ("registre", "registre_de_la_sonde", "registre_du_scellement"):
        if isinstance(R.get(cle), dict):
            return R[cle]
    return None


def statuts(registre):
    if not registre or "sondes" not in registre:
        return {}, {}
    fails = {s["id"]: s for s in registre["sondes"] if s.get("status") == "FAIL"}
    skips = {s["id"]: s for s in registre["sondes"] if s.get("status") == "SKIP"}
    return fails, skips


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--mode", choices=("baseline", "final"), required=True)
    a.add_argument("--expected")
    a.add_argument("--input")
    a.add_argument("--output", required=True)
    o = a.parse_args(args_apres_separateur(sys.argv))

    dossier = o.output if os.path.isabs(o.output) else chemin(o.output)
    os.makedirs(dossier, exist_ok=True)
    attendu = {}
    if o.mode == "baseline":
        if not o.expected:
            print("mode baseline sans --expected"); return 2
        p = o.expected if os.path.isabs(o.expected) else chemin(o.expected)
        attendu = json.load(open(p, encoding="utf-8")).get("suites", {})

    commandes, global_ok = [], True
    for nom, argv, rapport in suites(o.mode, o.input):
        t0 = time.perf_counter()
        r = subprocess.run(argv, capture_output=True, text=True)
        duree = round(time.perf_counter() - t0, 3)
        reg = lire_registre(rapport)
        fails, skips = statuts(reg)
        entree = {
            "suite": nom, "argv": argv, "code_brut": r.returncode,
            "secondes": duree, "rapport": rapport,
            "stdout_fin": r.stdout[-4000:], "stderr_fin": r.stderr[-4000:],
            "fail": sorted(fails), "skip": sorted(skips),
        }

        if o.mode == "final":
            ok = (r.returncode == 0 and not fails and not skips)
            entree["verdict"] = "PASS" if ok else "FAIL"
            if fails: entree["raison"] = "FAIL present en mode final"
            elif skips: entree["raison"] = "SKIP critique en mode final"
            elif r.returncode: entree["raison"] = "code non nul"
        else:
            ref = attendu.get(nom)
            if ref is None:
                ok = (r.returncode == 0 and not fails and not skips)
                entree["verdict"] = "PASS" if ok else "FAIL"
                if not ok: entree["raison"] = "suite hors baseline et non verte"
            else:
                att_f = {x["id"]: x for x in ref.get("fail", [])}
                att_s = {x["id"]: x for x in ref.get("skip", [])}
                nouveaux = sorted(set(fails) - set(att_f))
                disparus = sorted(set(att_f) - set(fails))
                skip_nouv = sorted(set(skips) - set(att_s))
                skip_disp = sorted(set(att_s) - set(skips))
                champs = []
                for i, x in att_f.items():
                    s = fails.get(i)
                    if not s: continue
                    for cle_att, cle_son in (("seuil", "tolerance"),):
                        if cle_att in x and cle_son in s and \
                           abs(float(x[cle_att]) - float(s[cle_son])) > 1e-9:
                            champs.append("%s.%s" % (i, cle_att))
                code_ok = r.returncode == ref.get("code_shell_attendu", 0)
                ok = (not nouveaux and not disparus and not skip_nouv
                      and not skip_disp and not champs and code_ok)
                entree.update(nouveaux_fail=nouveaux, fail_disparus=disparus,
                              nouveaux_skip=skip_nouv, skip_disparus=skip_disp,
                              champs_divergents=champs,
                              code_attendu=ref.get("code_shell_attendu"),
                              verdict="PASS" if ok else "FAIL")
        global_ok &= entree["verdict"] == "PASS"
        commandes.append(entree)
        print("[%s] %-16s code=%-3s fail=%d skip=%d %.2fs"
              % (entree["verdict"], nom, r.returncode, len(fails), len(skips), duree))
        for k in ("nouveaux_fail", "fail_disparus", "nouveaux_skip",
                  "skip_disparus", "champs_divergents"):
            if entree.get(k):
                print("    %s : %s" % (k, entree[k]))

    # `registre.json` : toutes les sondes de toutes les suites, en un seul
    # endroit, avec des totaux CALCULES et jamais saisis.
    sondes, par_suite = [], {}
    for e in commandes:
        R = lire_registre(e.get("rapport")) if e.get("rapport") else None
        # Selon les rapports, `registre` est tantot le bilan complet, tantot
        # juste son nom. Et certains portent `sondes` a la racine.
        liste = []
        if isinstance(R, dict):
            b = R.get("registre")
            if isinstance(b, dict):
                liste = b.get("sondes", [])
            elif isinstance(R.get("sondes"), list):
                liste = R["sondes"]
        liste = [x for x in liste if isinstance(x, dict)]
        for x in liste:
            y = dict(x); y["suite"] = e["suite"]; sondes.append(y)
        par_suite[e["suite"]] = {
            "rapport": e.get("rapport"), "code": e.get("code_brut"),
            "verdict": e["verdict"], "sondes": len(liste),
            "reussies": sum(1 for x in liste if x.get("status") == "PASS"),
            "echecs": sum(1 for x in liste if x.get("status") == "FAIL"),
            "sautees": sum(1 for x in liste if x.get("status") == "SKIP")}
    agrege = {
        "mode": o.mode, "blender": BLENDER,
        "suites": par_suite,
        "total_sondes": len(sondes),
        "reussies": sum(1 for x in sondes if x.get("status") == "PASS"),
        "echecs": [x["suite"] + "/" + x.get("id", "?") for x in sondes
                   if x.get("status") == "FAIL"],
        "sautees": [x["suite"] + "/" + x.get("id", "?") for x in sondes
                    if x.get("status") == "SKIP"],
        "suites_en_echec": [n for n, v in par_suite.items() if v["verdict"] != "PASS"],
        "status": "PASS" if global_ok else "FAIL",
        "sondes": sondes}
    json.dump(agrege, open(os.path.join(dossier, "registre.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    print("REGISTRE AGREGE : %d sondes, %d reussies, %d echec(s), %d sautee(s)"
          % (agrege["total_sondes"], agrege["reussies"], len(agrege["echecs"]),
             len(agrege["sautees"])))

    out = os.path.join(dossier, "commandes.json")
    json.dump({"mode": o.mode, "blender": BLENDER, "racine": RACINE,
               "status": "PASS" if global_ok else "FAIL",
               "commandes": commandes},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("RUNNER", "PASS" if global_ok else "FAIL", "->", out)
    return 0 if global_ok else 2


if __name__ == "__main__":
    sys.exit(main())
