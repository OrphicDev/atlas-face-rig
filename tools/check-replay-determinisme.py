"""F0-F.9 — le replay propre reproduit-il les MEMES mesures ?

Comparer deux « PASS » ne prouve rien : deux executions peuvent passer avec
des chiffres differents. On compare donc valeur par valeur, sonde par sonde.

    python3 tools/check-replay-determinisme.py \
      --a reports/f0-final/registre.json \
      --b reports/f0-final/replay-clean/registre.json \
      --output reports/f0-final/replay-determinisme.json
"""
import argparse, hashlib, json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

MASTER = "source/FACE_BASE_LOCKED.blend"
SHA_MASTER = "cc9e55a47b1496fa81ed42deee6ee3a6f498c309d5b86610e5cd2407831f2bd8"

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--a", "--b", "--output"): a.add_argument(f, required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    A = json.load(open(Rp(o.a), encoding="utf-8"))
    B = json.load(open(Rp(o.b), encoding="utf-8"))
    reg = Registre("replay-determinisme")

    sa = {s["suite"] + "/" + s["id"]: s for s in A.get("sondes", [])}
    sb = {s["suite"] + "/" + s["id"]: s for s in B.get("sondes", [])}
    absentes = sorted(set(sa) - set(sb)) + sorted(set(sb) - set(sa))
    reg.exige("replay.memes_sondes", "le replay execute exactement les memes sondes",
              "%d / %d" % (len(sa), len(sb)), [], absentes, not absentes)
    divergentes = [[k, sa[k].get("measured"), sb[k].get("measured")]
                   for k in sa if k in sb
                   and sa[k].get("measured") != sb[k].get("measured")]
    reg.exige("replay.memes_mesures",
              "chaque sonde rend la MEME valeur, pas seulement le meme verdict",
              "%d sondes comparees" % len(sa), 0, len(divergentes),
              not divergentes)
    statuts = [k for k in sa if k in sb
               and sa[k].get("status") != sb[k].get("status")]
    reg.exige("replay.memes_verdicts", "aucun verdict ne change",
              "%d sondes" % len(sa), 0, len(statuts), not statuts)

    h = hashlib.sha256()
    p = os.path.join(RACINE, MASTER)
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    reg.exige("replay.master_intact", "le master historique a garde son SHA",
              MASTER, SHA_MASTER, h.hexdigest(), h.hexdigest() == SHA_MASTER)

    R = {"a": o.a, "b": o.b, "sondes_comparees": len(sa),
         "divergentes": divergentes[:20], "verdicts_changes": statuts,
         "master_sha256": h.hexdigest(), "registre": reg.bilan()}
    q = Rp(o.output); os.makedirs(os.path.dirname(q) or ".", exist_ok=True)
    json.dump(R, open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("DETERMINISME", "OK" if ok else "ECHEC", "->", o.output)
    sys.exit(0 if ok else 2)
