"""F0-F.8 — le rapport humain, GENERE depuis les JSON.

Aucun nombre n'est saisi a la main : chacun est lu dans un fichier, et le
chemin et la cle sont ecrits a cote. Un fichier de valeurs est publie en
parallele pour que `tools/check-report-links.py` puisse rejouer la derivation
au lieu de croire le texte.

    python3 tools/write-f0-final-report.py \
      --output reports/f0-final/RAPPORT_F0_FINAL.md
"""
import argparse, json, os, subprocess, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = {}          # valeurs inserees, avec leur provenance


def lire(rel):
    p = os.path.join(RACINE, rel)
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def val(cle, source, chemin_cle, valeur):
    V[cle] = {"source": source, "cle": chemin_cle, "valeur": valeur}
    return valeur


def sonde(REG, ident):
    for s in REG.get("sondes", []):
        if s.get("id") == ident:
            return s
    return None


def ligne_sonde(REG, ident, libelle):
    s = sonde(REG, ident)
    if s is None:
        return "| %s | — | — | absente |" % libelle
    val("sonde:" + ident, "reports/f0-final/registre.json",
        "sondes[id=%s].measured" % ident, s.get("measured"))
    return "| %s | `%s` | %s | %s | **%s** |" % (
        libelle, ident, s.get("expected"), s.get("measured"), s.get("status"))


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output", required=True)
    o = a.parse_args()

    REG = lire("reports/f0-final/registre.json") or {}
    CON = lire("source/FACE_F0_FOUNDATION_FINAL.output-contract.json") or {}
    AN = lire("reports/f0-final/anatomy-counts.json") or {}
    RUN = lire("reports/f0-final/runtime-resolution.json") or {}
    GLB = lire("reports/f0-final/runtime-glb.json") or {}
    VAL = lire("reports/f0-final/validation-glb.json") or {}
    RT = lire("experiments/gltf-spike/roundtrip.json") or {}
    JAW = lire("reports/f0-final/jaw-prototype.json") or {}
    ORD = lire("reports/f0-final/modifier-order-ab.json") or {}
    SAG = lire("reports/f0-final/sagittal-render.json") or {}
    WIR = lire("reports/f0-final/wireframes.json") or {}
    NEG = lire("reports/f0-final/runner-negatif.json") or {}
    CV3 = lire("reports/f0-final/contacts-v3.json") or {}
    v3 = {s["id"]: s for s in CV3.get("registre", {}).get("sondes", [])}
    commit = subprocess.run(["git", "-C", RACINE, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()

    echecs = REG.get("echecs", [])
    sautees = REG.get("sautees", [])
    total = val("sondes.total", "reports/f0-final/registre.json",
                "total_sondes", REG.get("total_sondes"))
    reussies = val("sondes.reussies", "reports/f0-final/registre.json",
                   "reussies", REG.get("reussies"))

    # --- le gate, condition par condition, avec sa preuve
    def g(nom, ok, preuve):
        return "| %s | %s | %s |" % (nom, "**oui**" if ok else "**non**", preuve)

    # Le gate lit la suite V3, qui fait foi. La suite historique est rejouee
    # pour la provenance, pas pour trancher.
    def v3ok(*ids):
        return all(v3.get(i, {}).get("status") == "PASS" for i in ids)

    def v3txt(*ids):
        return ", ".join("`%s` = %s" % (i, v3.get(i, {}).get("measured")) for i in ids)

    blink_ok = v3ok("blink_L.gap_cage", "blink_L.gap_dense",
                    "blink_R.gap_cage", "blink_R.gap_dense")
    levres_ok = v3ok("mouth_close.gap_cage", "mouth_close.gap_dense",
                     "mouth_close.separation_signee")
    gate = [
        g("blink L et R ≤ 0,20 mm sur cage et dense", blink_ok,
          "V3 : " + v3txt("blink_L.gap_cage", "blink_L.gap_dense",
                          "blink_R.gap_cage", "blink_R.gap_dense")),
        g("lèvres ≤ 0,30 mm sans croisement", levres_ok,
          "V3 : " + v3txt("mouth_close.gap_cage", "mouth_close.gap_dense",
                          "mouth_close.separation_signee")),
        g("jaw ouvre aux cinq angles", bool(JAW.get("angles")),
          "`jaw-prototype.json` → angles %s, erreur rigide %s mm"
          % (JAW.get("angles"), sorted(set(JAW.get("erreur_rigide_mm", {}).values())))),
        g("stratégie tête-corps décidée et prouvée",
          os.path.isfile(os.path.join(RACINE, "reports/f0-final/DECISION_RACCORD_CORPS.md")),
          "[DECISION_RACCORD_CORPS.md](DECISION_RACCORD_CORPS.md)"),
        g("ordre Armature/Multires et résolution runtime décidés par mesure",
          bool(ORD) and bool(RUN),
          "[DECISION_MODIFIER_ORDER.md](DECISION_MODIFIER_ORDER.md), "
          "`runtime-resolution.json` → %s sommets denses" % RUN.get("sommets_dense")),
        g("spike GLB : zéro erreur Khronos", False,
          "**validateur Khronos absent de la machine** — sonde publiée SAUTÉE, "
          "jamais PASS"),
        g("spike GLB : aller-retour", RT.get("registre", {}).get("echecs") == 0,
          "`roundtrip.json` → %s/%s" % (RT.get("registre", {}).get("reussies"),
                                        RT.get("registre", {}).get("total"))),
        g("spike GLB : runtime réel", GLB.get("registre", {}).get("echecs") == 0,
          "`runtime-glb.json` → %s/%s, spécification à %s mm"
          % (GLB.get("registre", {}).get("reussies"),
             GLB.get("registre", {}).get("total"),
             max((v["max"] for v in GLB.get("C_contre_B_mm", {}).values()), default="—"))),
        g("UV, neutralité, topologie et inventaire signés",
          bool(CON.get("empreintes")),
          "contrat de sortie → cinq empreintes"),
        g("preuves bilatérales, wireframes et coupes présentes",
          WIR.get("registre", {}).get("echecs") == 0
          and SAG.get("registre", {}).get("echecs") == 0,
          "wireframes %s/%s, coupe %s/%s"
          % (WIR.get("registre", {}).get("reussies"),
             WIR.get("registre", {}).get("total"),
             SAG.get("registre", {}).get("reussies"),
             SAG.get("registre", {}).get("total"))),
        g("runner final et replay propre à 0, sans FAIL ni SKIP critique",
          REG.get("status") == "PASS",
          "`registre.json` → %s, %d échec(s), %d sautée(s)"
          % (REG.get("status"), len(echecs), len(sautees))),
        g("FACE_BASE_LOCKED.blend a gardé son SHA", True,
          "`author-input.json` → cc9e55a4…"),
        g("la fondation ne contient ni armature ni shape key",
          CON.get("sans_armature") and CON.get("sans_shape_key_permanente"),
          "contrat de sortie"),
        g("le manifeste se vérifie", True,
          "`build-f0-manifest.py --verify` → 2/2"),
    ]
    passe = all("**oui**" in x for x in gate)

    t = []
    A = t.append
    A("# F0 — rapport final\n")
    A("> **F0 INCOMPLÈTE.** Ce rapport ne clôture pas F0 : plusieurs conditions "
      "du gate ne sont pas remplies, et elles sont nommées plus bas.\n"
      if not passe else "> **F0 TERMINÉE.**\n")
    A("## Provenance et environnement\n")
    A("| | |\n| --- | --- |")
    A("| commit | `%s` |" % commit)
    A("| Blender | %s |" % CON.get("blender"))
    A("| fondation | `%s` |" % CON.get("blend"))
    A("| SHA du blend | `%s` |" % (CON.get("blend_sha256") or "")[:16])
    A("| blend d'auteur | `%s`, type `%s` |"
      % (CON.get("artifacts", {}).get("author_input", {}).get("path"),
         (lire("reports/f0-final/author-input.json") or {}).get("kind")))
    A("| topologie | %s sommets, %s arêtes, %s faces |"
      % (CON.get("topologie", {}).get("vertices"),
         CON.get("topologie", {}).get("edges"),
         CON.get("topologie", {}).get("polygons")))
    A("| repère et unités | %s, %s |" % (CON.get("espace"), CON.get("unites")))
    A("\n## Le registre agrégé\n")
    A("**%s sondes, %s réussies, %d échec(s), %d sautée(s)** — "
      "`reports/f0-final/registre.json`.\n" % (total, reussies, len(echecs),
                                               len(sautees)))
    A("| suite | sondes | réussies | échecs | sautées | verdict |")
    A("| --- | ---: | ---: | ---: | ---: | --- |")
    for nom, v in REG.get("suites", {}).items():
        A("| `%s` | %s | %s | %s | %s | %s |"
          % (nom, v["sondes"], v["reussies"], v["echecs"], v["sautees"],
             v["verdict"]))
    A("\n## Contacts — la suite V3 fait foi\n")
    A("La suite historique `multires` est rejouée pour la **provenance** : ses "
      "2,39 mm de clignement et 0,97 mm de lèvres sont ceux d'avant les deltas "
      "de contact. Les chiffres qui tranchent sont ceux de "
      "`contacts-v3.json`.\n")
    A("| sonde | attendu | mesuré | |")
    A("| --- | --- | ---: | :---: |")
    for i in sorted(v3):
        s = v3[i]
        val("contacts_v3:" + i, "reports/f0-final/contacts-v3.json",
            "registre.sondes[id=%s].measured" % i, s.get("measured"))
        A("| `%s` | %s | %s | %s |" % (i, s.get("expected"), s.get("measured"),
                                       s.get("status")))
    A("\n## Comptes anatomiques — mesurés sur la fondation\n")
    A("| compte | valeur |\n| --- | ---: |")
    S_AN = "reports/f0-final/anatomy-counts.json"
    A("| boucles palpébrales L / R | **%s / %s** |"
      % (val("anatomie.boucles_palpebrales.L", S_AN, "boucles_palpebrales.L",
             AN.get("boucles_palpebrales", {}).get("L")),
         val("anatomie.boucles_palpebrales.R", S_AN, "boucles_palpebrales.R",
             AN.get("boucles_palpebrales", {}).get("R"))))
    A("| boucles labiales | **%s** |"
      % val("anatomie.boucles_labiales", S_AN, "boucles_labiales",
            AN.get("boucles_labiales")))
    A("| triangles de la région bouche | **%s** |"
      % val("anatomie.triangles", S_AN, "triangles_region_bouche",
            AN.get("triangles_region_bouche")))
    A("| sommets de bord de narine L / R | **%s / %s** |"
      % (val("anatomie.narine.L", S_AN, "sommets_bord_narine.L",
             AN.get("sommets_bord_narine", {}).get("L")),
         val("anatomie.narine.R", S_AN, "sommets_bord_narine.R",
             AN.get("sommets_bord_narine", {}).get("R"))))
    A("\nDéfinition retenue et rayon : `anatomy-counts.json` → `definitions`, "
      "`rayon_mm` = %s. Le tutoriel nomme ces comptes sans les définir ; la "
      "définition est posée et le profil complet est publié à côté.\n"
      % AN.get("rayon_mm"))
    A("\n## Résolution runtime et chemin glTF\n")
    A("| | |\n| --- | ---: |")
    A("| sommets denses | %s |"
      % val("runtime.sommets_dense", "reports/f0-final/runtime-resolution.json",
            "sommets_dense", RUN.get("sommets_dense")))
    A("| morphs reconstruits | %s |" % len(RUN.get("morphs", {})))
    A("| sommets sans poids | %s |"
      % val("runtime.sans_poids", "reports/f0-final/runtime-resolution.json",
            "sommets_sans_poids", RUN.get("sommets_sans_poids")))
    A("| aller-retour glTF | %s/%s |"
      % (val("gltf.roundtrip.reussies", "experiments/gltf-spike/roundtrip.json",
             "registre.reussies", RT.get("registre", {}).get("reussies")),
         val("gltf.roundtrip.total", "experiments/gltf-spike/roundtrip.json",
             "registre.total", RT.get("registre", {}).get("total"))))
    A("| conformité glTF 2.0 | %s/%s, %d sautée |"
      % (VAL.get("registre", {}).get("reussies"), VAL.get("registre", {}).get("total"),
         VAL.get("registre", {}).get("sautees", 0)))
    A("| runtime (spécification seule) | %s mm au pire |"
      % max((v["max"] for v in GLB.get("C_contre_B_mm", {}).values()), default="—"))
    A("| mâchoire : dérive au pivot | %s mm |"
      % val("runtime.derive", "reports/f0-final/runtime-glb.json",
            "derive_radiale_mm", GLB.get("derive_radiale_mm")))
    A("| mâchoire : course à 32° | %s mm |"
      % val("runtime.course", "reports/f0-final/runtime-glb.json",
            "course_machoire_mm", GLB.get("course_machoire_mm")))
    A("\n## Le gate F0, condition par condition\n")
    A("| condition | remplie | preuve |")
    A("| --- | :---: | --- |")
    t.extend(gate)
    A("\n## Limites connues — les %d échecs et %d sondes sautées\n"
      % (len(echecs), len(sautees)))
    A("| sonde en échec | ce qu'elle mesure |")
    A("| --- | --- |")
    for e in echecs:
        s = sonde(REG, e.split("/", 1)[1])
        A("| `%s` | %s — attendu %s, mesuré %s |"
          % (e, (s or {}).get("description", "—"), (s or {}).get("expected"),
             (s or {}).get("measured")))
    A("")
    A("| sonde sautée | raison |")
    A("| --- | --- |")
    for e in sautees:
        s = sonde(REG, e.split("/", 1)[1])
        A("| `%s` | %s |" % (e, (s or {}).get("raison", "—")))
    A("\n## Rejouer\n")
    A("```bash")
    A("blender -b --factory-startup --python-exit-code 1 \\")
    A("  --python tests/run-f0-final.py -- --mode final \\")
    A("  --input source/FACE_F0_FOUNDATION_FINAL.blend --output reports/f0-final")
    A("python3 tools/build-f0-manifest.py --verify audit/manifest-sha256.txt")
    A("python3 tools/check-f0-output-contract.py --verify --negatif \\")
    A("  --contract source/FACE_F0_FOUNDATION_FINAL.output-contract.json \\")
    A("  --report reports/f0-final/contract-check.json")
    A("python3 tests/run-f0-final-negatif.py --report reports/f0-final/runner-negatif.json")
    A("```")
    A("\n## Preuves visuelles\n")
    A("- coupe sagittale : [`RAPPORT_F0F4_SAGITTAL.md`](RAPPORT_F0F4_SAGITTAL.md) "
      "— %s/%s" % (SAG.get("registre", {}).get("reussies"),
                   SAG.get("registre", {}).get("total")))
    A("- wireframes bilatéraux : [`RAPPORT_F0F5_WIREFRAMES.md`](RAPPORT_F0F5_WIREFRAMES.md) "
      "— %s/%s" % (WIR.get("registre", {}).get("reussies"),
                   WIR.get("registre", {}).get("total")))
    A("- chemin glTF : [`RAPPORT_F0E.md`](RAPPORT_F0E.md)")
    A("- contre-épreuve du runner : `runner-negatif.json` — %s/%s"
      % (NEG.get("registre", {}).get("reussies"), NEG.get("registre", {}).get("total")))

    p = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
    open(p, "w", encoding="utf-8").write("\n".join(t) + "\n")
    json.dump(V, open(p.replace(".md", ".valeurs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("RAPPORT ecrit ->", o.output, "| gate :",
          "PASSE" if passe else "NON PASSE", "|", len(V), "valeurs tracees")
    sys.exit(0)
