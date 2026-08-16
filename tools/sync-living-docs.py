"""F0-F.7 — les documents vivants racontent la MEME verite, tiree du registre.

Les chiffres ne sont pas retapes : ils viennent de `registre.json` et du
contrat de sortie. Un document vivant qui affirme « F0 est terminee » pendant
qu'un autre affirme « F0 INCOMPLET » est une contradiction, pas une nuance.

    python3 tools/sync-living-docs.py --report reports/f0-final/living-docs.json
"""
import argparse, datetime, json, os, re, subprocess, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

VIVANTS = ["README.md", "STATUS.md", "CHANGELOG.md",
           "handoffs/HANDOFF_FACE_NEXT.md", "docs/FACS_MATRIX.md",
           "audit/AUDIT_PACKET_FACE.md"]
ANCIENNES = ["669ccdb7858adea2e3091218bdfeed4fe1b4d955d866497ad20e8559c95e55bd",
             "d29e2af3ef67aec5bad705c5e5a4b72428f906f01af94c33880c85a47722e5ae",
             "9246d8acb2d68a38a6f355db90df967e8f6e71907343ce1cf028549bed20c324"]


def lire(rel):
    p = os.path.join(RACINE, rel)
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--report", required=True)
    a.add_argument("--date", default=str(datetime.date.today()))
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    REG = lire("reports/f0-final/registre.json")
    CON = lire("source/FACE_F0_FOUNDATION_FINAL.output-contract.json")
    commit = subprocess.run(["git", "-C", RACINE, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    reg = Registre("living-docs")

    bloquants = [
        "clignement gauche sur la cage : %s mm pour 0,20 exigés"
        % next((s["measured"] for s in REG.get("sondes", [])
                if s.get("id") == "blink_L.gap_cage"), "?"),
        "séparations signées et rapports d'arêtes des paupières (V3)",
        "validateur Khronos absent de la machine — sonde SAUTÉE, jamais PASS",
        "trois cadres de la coupe sagittale médiane sans section",
        "chemin personnel encore présent dans le blend (hygiène)",
        "raccord corps : la suite historique reste en échec métier",
    ]
    ENTETE = (
        "STATUS: **F0 INCOMPLÈTE** — %d sondes, %d réussies, %d échec(s), "
        "%d sautée(s)\n\n"
        "> Vérité unique : [`reports/f0-final/RAPPORT_F0_FINAL.md`]"
        "(reports/f0-final/RAPPORT_F0_FINAL.md).\n"
        "> Mesuré le %s, commit `%s`, Blender %s.\n\n"
        "| | |\n| --- | --- |\n"
        "| **statut global** | **F0 INCOMPLÈTE** — le gate n'est pas passé |\n"
        "| fondation | `%s` |\n"
        "| contrat de sortie | `source/FACE_F0_FOUNDATION_FINAL.output-contract.json` |\n"
        "| branche active | `face/chat-3-caucasian-v1` |\n"
        "| sondes | **%d / %d**, comptées par registre et jamais à la main |\n"
        "| suites en échec | %s |\n"
        "| F1 | **ne commence pas** tant que le gate n'est pas passé |\n\n"
        "## Ce qui bloque, nommément\n\n%s\n"
        % (REG.get("total_sondes", 0), REG.get("reussies", 0),
           len(REG.get("echecs", [])), len(REG.get("sautees", [])),
           o.date, commit, CON.get("blender"),
           CON.get("blend", "source/FACE_F0_FOUNDATION_FINAL.blend"),
           REG.get("reussies", 0), REG.get("total_sondes", 0),
           ", ".join("`%s`" % x for x in REG.get("suites_en_echec", [])) or "aucune",
           "\n".join("- " + b for b in bloquants)))

    R = {"date": o.date, "commit": commit, "documents": {}}

    # --- STATUS.md : on remplace l'entete jusqu'au premier titre de section
    p = Rp("STATUS.md")
    texte = open(p, encoding="utf-8").read()
    i = texte.find("\n## ")
    nouveau = ENTETE + (texte[i:] if i > 0 else "")
    open(p, "w", encoding="utf-8").write(nouveau)
    R["documents"]["STATUS.md"] = "entete reecrit depuis le registre"

    # --- HANDOFF : il affirmait « F0 est terminée »
    p = Rp("handoffs/HANDOFF_FACE_NEXT.md")
    texte = open(p, encoding="utf-8").read()
    avant = texte
    texte = texte.replace(
        "F0 est terminée et mesurée. **Rien n'est riggé.** Ne recommence pas F0 : tout\n"
        "est chiffré, vérifié et verrouillé.",
        "**F0 n'est PAS terminée.** Ce document affirmait le contraire pendant que\n"
        "`STATUS.md` affirmait « F0 INCOMPLET » : la contradiction est levée ici.\n"
        "L'état réellement démontré est dans\n"
        "[`reports/f0-final/RAPPORT_F0_FINAL.md`](../reports/f0-final/RAPPORT_F0_FINAL.md).\n"
        "**Rien n'est riggé.** Ne recommence pas ce qui est déjà mesuré, mais ne\n"
        "commence pas F1 non plus : le gate F0 n'est pas passé.")
    open(p, "w", encoding="utf-8").write(texte)
    R["documents"]["handoffs/HANDOFF_FACE_NEXT.md"] = (
        "contradiction levee" if texte != avant else "deja coherent")

    # --- AUDIT : les trois anciennes empreintes deviennent historiques
    p = Rp("audit/AUDIT_PACKET_FACE.md")
    texte = open(p, encoding="utf-8").read()
    if "OBSOLÈTE" not in texte:
        for h in ANCIENNES:
            texte = texte.replace(
                "`%s`" % h,
                "`%s` — **OBSOLÈTE** : empreinte du paquet d'audit d'origine, "
                "antérieur au verrou c0885. Ce n'est **pas** celle du verrou "
                "c0885 ni celle de la fondation finale." % h)
        texte += ("\n\n---\n\n> **Note du %s, commit `%s`.** Les trois empreintes "
                  "ci-dessus appartiennent au paquet d'audit d'origine. Le verrou "
                  "courant est `source/FACE_BASE_LOCKED.blend` "
                  "(`cc9e55a4…`) et la fondation est "
                  "`source/FACE_F0_FOUNDATION_FINAL.blend` (`%s…`). "
                  "Vérité unique : "
                  "[`reports/f0-final/RAPPORT_F0_FINAL.md`]"
                  "(../reports/f0-final/RAPPORT_F0_FINAL.md).\n"
                  % (o.date, commit, (CON.get("blend_sha256") or "")[:8]))
    open(p, "w", encoding="utf-8").write(texte)
    R["documents"]["audit/AUDIT_PACKET_FACE.md"] = "empreintes anciennes datees"

    # --- README, CHANGELOG, FACS : un renvoi unique vers la verite
    renvoi = ("\n\n> **État F0 (%s, commit `%s`).** F0 est **incomplète** : "
              "%d sondes, %d réussies, %d échec(s), %d sautée(s). Vérité unique : "
              "[`reports/f0-final/RAPPORT_F0_FINAL.md`](%s). F1 n'a pas commencé.\n"
              % (o.date, commit, REG.get("total_sondes", 0), REG.get("reussies", 0),
                 len(REG.get("echecs", [])), len(REG.get("sautees", [])), "%s"))
    for rel, prefixe in (("README.md", "reports/f0-final/RAPPORT_F0_FINAL.md"),
                         ("CHANGELOG.md", "reports/f0-final/RAPPORT_F0_FINAL.md"),
                         ("docs/FACS_MATRIX.md",
                          "../reports/f0-final/RAPPORT_F0_FINAL.md")):
        p = Rp(rel)
        texte = open(p, encoding="utf-8").read()
        texte = re.sub(r"\n\n> \*\*État F0 \([^)]*\)\.\*\*.*?F1 n'a pas commencé\.\n",
                       "", texte, flags=re.S)
        open(p, "w", encoding="utf-8").write(texte + (renvoi % prefixe))
        R["documents"][rel] = "renvoi vers la verite unique"

    # --- controle : plus aucune contradiction non expliquee
    contradictions = []
    for rel in VIVANTS:
        t = open(Rp(rel), encoding="utf-8").read()
        if "F0 TERMIN" in t.upper().replace("É", "E"):
            contradictions.append(rel + " : affirme F0 terminee")
        for h in ANCIENNES:
            if h in t and "OBSOL" not in t:
                contradictions.append(rel + " : ancienne empreinte sans mention")
    reg.exige("docs.aucune_contradiction",
              "aucun document vivant n'affirme F0 terminee",
              "%d documents" % len(VIVANTS), [], contradictions,
              not contradictions)
    reg.exige("docs.renvoi_unique",
              "chaque document vivant renvoie au rapport final",
              "%d documents" % len(VIVANTS), len(VIVANTS),
              sum(1 for rel in VIVANTS
                  if "RAPPORT_F0_FINAL.md" in open(Rp(rel), encoding="utf-8").read()),
              all("RAPPORT_F0_FINAL.md" in open(Rp(rel), encoding="utf-8").read()
                  for rel in VIVANTS))
    R["registre"] = reg.bilan()
    pr = Rp(o.report); os.makedirs(os.path.dirname(pr) or ".", exist_ok=True)
    json.dump(R, open(pr, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("DOCS", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
