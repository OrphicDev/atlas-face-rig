"""F0-F.2 — validateur du contrat de sortie, et sa contre-epreuve.

`--verify` relit chaque artefact declare et refuse le moindre SHA different.
`--negatif` copie un artefact dans un TEMPORAIRE, y change un chiffre, et
exige que la validation refuse cette copie. L'artefact versionne n'est jamais
touche : la contre-epreuve travaille sur une copie et redirige le chemin.

    python3 tools/check-f0-output-contract.py --verify \
      --contract source/FACE_F0_FOUNDATION_FINAL.output-contract.json \
      --report reports/f0-final/contract-check.json
"""
import argparse, hashlib, json, os, shutil, sys, tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def declares(C):
    """Tous les couples (cle, path, sha256) declares par le contrat."""
    out = []
    for section in ("artifacts", "deltas", "decisions"):
        for k, v in C.get(section, {}).items():
            out.append((section + "." + k, v.get("path"), v.get("sha256")))
    if C.get("blend") and C.get("blend_sha256"):
        out.append(("blend", C["blend"], C["blend_sha256"]))
    return out


def verifier(C, reg, remplacements=None, ident="contrat.verification"):
    remplacements = remplacements or {}
    fautes = []
    for cle, chemin, attendu in declares(C):
        if chemin is None:
            fautes.append([cle, "aucun chemin declare"]); continue
        if os.path.isabs(chemin):
            fautes.append([cle, "chemin absolu : " + chemin]); continue
        p = remplacements.get(cle) or os.path.join(RACINE, chemin)
        if not os.path.isfile(p):
            fautes.append([cle, "fichier absent : " + chemin]); continue
        if attendu is None:
            fautes.append([cle, "aucun SHA declare"]); continue
        reel = sha(p)
        if reel != attendu:
            fautes.append([cle, "SHA different", attendu[:12], reel[:12]])
    reg.exige(ident, "chaque artefact retrouve son SHA",
              "%d artefacts declares" % len(declares(C)), 0, len(fautes),
              not fautes)
    return fautes


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--contract", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--verify", action="store_true")
    a.add_argument("--negatif", action="store_true")
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    C = json.load(open(Rp(o.contract), encoding="utf-8"))
    reg = Registre("check-output-contract")
    R = {"contract": o.contract}

    fautes = verifier(C, reg)
    R["fautes"] = fautes

    if o.negatif:
        # on mute une COPIE, jamais l'artefact versionne
        cle, chemin, _ = next(x for x in declares(C)
                              if x[1] and x[1].endswith(".json"))
        with tempfile.TemporaryDirectory() as d:
            faux = os.path.join(d, os.path.basename(chemin))
            shutil.copyfile(os.path.join(RACINE, chemin), faux)
            b = bytearray(open(faux, "rb").read())
            i = next(k for k, c in enumerate(b) if chr(c).isdigit())
            b[i] = ord("9") if chr(b[i]) != "9" else ord("8")
            open(faux, "wb").write(bytes(b))
            r2 = Registre("mutant")
            # registre distinct ET identifiant distinct : un [FAIL] attendu
            # qui porte le meme nom que la vraie sonde rend le journal
            # mensonger a la lecture.
            f2 = verifier(C, r2, {cle: faux}, ident="mutant.verification")
            refuse = any(x[0] == cle and x[1] == "SHA different" for x in f2)
            reg.exige("contrat.refus_sha_modifie",
                      "un artefact dont un chiffre change est refuse",
                      "copie temporaire de " + chemin, "refus sur " + cle,
                      "refuse" if refuse else "ACCEPTE", refuse)
            R["negatif"] = {"cle_mutee": cle, "source": chemin,
                            "octet_change": i, "fautes": f2}
        intact = sha(os.path.join(RACINE, chemin))
        att = dict((x[0], x[2]) for x in declares(C))[cle]
        reg.exige("contrat.artefact_intact",
                  "l'artefact versionne n'a pas ete touche", chemin,
                  att[:12], intact[:12], intact == att)

    R["registre"] = reg.bilan()
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("CONTRAT_CHECK", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
