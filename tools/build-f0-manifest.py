"""F0-F.6 — manifeste des LIVRABLES, jamais un parcours d'arborescence.

La liste est explicite. Ni temporaires, ni caches, ni journaux locaux, ni
l'asset externe de 49 Mo. Un livrable attendu mais absent est declare ABSENT
dans le manifeste : le silence ferait passer un trou pour une reussite.

    python3 tools/build-f0-manifest.py --output audit/manifest-sha256.txt
    python3 tools/build-f0-manifest.py --verify audit/manifest-sha256.txt
"""
import argparse, hashlib, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

LIVRABLES = [
    "source/FACE_F0_FOUNDATION_FINAL.blend",
    "source/FACE_F0_FOUNDATION_FINAL.output-contract.json",
    "source/FACE_BASE_LOCKED.blend",
    "reports/f0-final/registre.json",
    "reports/f0-final/commandes.json",
    "reports/f0-final/runner-negatif.json",
    "reports/f0-final/contract-check.json",
    "reports/f0-final/contacts-v3.json",
    "reports/f0-final/jaw-motion.json",
    "reports/f0-final/jaw-prototype.json",
    "reports/f0-final/DECISION_RACCORD_CORPS.md",
    "reports/f0-final/DECISION_MODIFIER_ORDER.md",
    "reports/f0-final/modifier-order-ab.json",
    "reports/f0-final/runtime-resolution.json",
    "reports/f0-final/runtime-mesh.json",
    "reports/f0-final/runtime-glb.json",
    "reports/f0-final/runtime-pivot-negatif.json",
    "reports/f0-final/validation-glb.json",
    "reports/f0-final/validation-glb-negatif.json",
    "reports/f0-final/sagittal-render.json",
    "reports/f0-final/wireframes.json",
    "reports/f0-final/author-input.json",
    "reports/f0-final/carte-miroir.json",
    "reports/f0-final/mirror-map-check.json",
    "reports/f0-final/anatomy-counts.json",
    "reports/f0-final/correspondances-marges.json",
    "reports/f0-final/foundation.json",
    "reports/f0-final/deformations/blink_L.cage-delta.json",
    "reports/f0-final/deformations/blink_R.cage-delta.json",
    "reports/f0-final/deformations/mouth_close.cage-delta.json",
    "reports/f0-final/deformations/jaw-mask.npy",
    "reports/f0-final/deformations/jaw-mask.json",
    "config/jaw-mask.json",
    "config/jaw-motion.json",
    "config/globe-fit.json",
    "config/mirror-landmarks.json",
    "config/contact-falloff.json",
    "config/landmarks-contact.json",
    "config/deformation-edge-whitelist.json",
    "experiments/gltf-spike/roundtrip.json",
    "experiments/gltf-spike/spike-reference.json",
    "exports/atlas-face-spike.glb",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def lignes():
    out, absents = [], []
    for rel in sorted(LIVRABLES):
        p = os.path.join(RACINE, rel)
        if not os.path.isfile(p):
            absents.append(rel)
            out.append("ABSENT%s  %d  %s" % (" " * 58, 0, rel))
            continue
        out.append("%s  %d  %s" % (sha(p), os.path.getsize(p), rel))
    return out, absents


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output")
    a.add_argument("--verify")
    o = a.parse_args()
    reg = Registre("manifest")

    if o.verify:
        chemin = o.verify if os.path.isabs(o.verify) else os.path.join(RACINE, o.verify)
        attendues = [l.rstrip("\n") for l in open(chemin, encoding="utf-8")
                     if l.strip()]
        obtenues, absents = lignes()
        manquantes = [l for l in attendues if l not in obtenues]
        surplus = [l for l in obtenues if l not in attendues]
        reg.exige("manifeste.identique",
                  "chaque livrable retrouve son SHA et sa taille",
                  "%d lignes" % len(attendues), 0,
                  len(manquantes) + len(surplus),
                  not manquantes and not surplus)
        for l in (manquantes + surplus)[:8]:
            print("    ecart :", l[:100])
        reg.exige("manifeste.aucun_absent", "aucun livrable declare manquant",
                  "liste explicite", [], absents, not absents)
        ok = reg.conclure()
        print("MANIFESTE", "OK" if ok else "ECHEC")
        sys.exit(0 if ok else 2)

    if not o.output:
        print("il faut --output ou --verify"); sys.exit(1)
    out = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
    ls, absents = lignes()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(ls) + "\n")
    reg.exige("manifeste.aucun_chemin_absolu", "aucun chemin absolu",
              "%d lignes" % len(ls), 0,
              sum(1 for l in ls if l.split("  ")[-1].startswith("/")), True)
    reg.exige("manifeste.aucun_absent", "aucun livrable declare manquant",
              "liste explicite", [], absents, not absents)
    ok = reg.conclure()
    print("MANIFESTE ecrit ->", o.output, "|", len(ls), "livrables")
    sys.exit(0 if ok else 2)
