"""F0-E.9 — conformite glTF 2.0 d'un GLB, sans Blender.

Deux etages :

1. le validateur **Khronos** s'il est installe (`gltf-validator` dans le PATH,
   ou `--khronos <chemin>`) ; sa sortie JSON est publiee telle quelle ;
2. un controle de conformite **ecrit ici**, qui lit le fichier octet par octet
   et ne depend d'aucun outil exterieur.

Le second n'est pas un substitut du premier et ne pretend pas l'etre : quand
le validateur Khronos est absent, la sonde correspondante est publiee SAUTEE,
avec la raison. Un « PASS » qui viendrait d'un outil jamais execute serait un
mensonge.

    python3 tools/validate_glb.py --input exports/atlas-face-spike.glb \
      --report reports/f0-final/validation-glb.json
"""
import argparse, array, json, math, os, shutil, struct, subprocess, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre

TAILLE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
CODE = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
COMPOSANTES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
               "MAT2": 4, "MAT3": 9, "MAT4": 16}
RESTART = {5123: 0xFFFF, 5125: 0xFFFFFFFF}


def lire_glb(chemin):
    """Decoupe le conteneur. Toute anomalie est levee, jamais avalee."""
    b = open(chemin, "rb").read()
    if len(b) < 12:
        raise ValueError("fichier plus court que l'entete GLB")
    magic, version, total = struct.unpack("<III", b[:12])
    if magic != 0x46546C67:
        raise ValueError("magic absent : ce n'est pas un GLB")
    anomalies = []
    if version != 2:
        anomalies.append("version de conteneur %d au lieu de 2" % version)
    if total != len(b):
        anomalies.append("longueur declaree %d, fichier %d" % (total, len(b)))
    off, chunks = 12, []
    while off + 8 <= min(total, len(b)):
        ln, ty = struct.unpack("<II", b[off:off + 8])
        if ln % 4:
            anomalies.append("chunk 0x%X de longueur %d non multiple de 4" % (ty, ln))
        chunks.append((ty, b[off + 8:off + 8 + ln]))
        off += 8 + ln
    if off != total:
        anomalies.append("les chunks s'arretent a %d pour %d declares" % (off, total))
    if not chunks or chunks[0][0] != 0x4E4F534A:
        raise ValueError("le premier chunk n'est pas du JSON")
    J = json.loads(chunks[0][1].decode("utf-8"))
    BIN = next((c[1] for c in chunks[1:] if c[0] == 0x004E4942), b"")
    return J, BIN, anomalies, len(b)


def _brut(J, BIN, bv_i, offset, ct, nc, n):
    bv = J["bufferViews"][bv_i]
    base = bv.get("byteOffset", 0) + offset
    taille = TAILLE[ct] * nc
    stride = bv.get("byteStride") or taille
    if stride == taille:                                # cas dense : d'un bloc
        a = array.array(CODE[ct], BIN[base:base + taille * n])
        return [list(a[k * nc:(k + 1) * nc]) for k in range(n)]
    return [list(array.array(CODE[ct], BIN[base + k * stride:base + k * stride + taille]))
            for k in range(n)]


def decoder(J, BIN, i):
    """Elements d'un accessor, byteStride ET bloc `sparse` compris.

    Ignorer `sparse` etait ma faute en premiere passe : les morph targets de
    Blender sont sparses, et les lire sans substitution rend des zeros — ce qui
    faisait accuser des min/max parfaitement exacts.
    """
    acc = J["accessors"][i]
    n, ct = acc["count"], acc["componentType"]
    nc = COMPOSANTES[acc["type"]]
    if "bufferView" in acc:
        out = _brut(J, BIN, acc["bufferView"], acc.get("byteOffset", 0), ct, nc, n)
    else:
        out = [[0.0] * nc for _ in range(n)]            # base implicitement nulle
    sp = acc.get("sparse")
    if sp:
        m = sp["count"]
        idx = [v[0] for v in _brut(J, BIN, sp["indices"]["bufferView"],
                                   sp["indices"].get("byteOffset", 0),
                                   sp["indices"]["componentType"], 1, m)]
        val = _brut(J, BIN, sp["values"]["bufferView"],
                    sp["values"].get("byteOffset", 0), ct, nc, m)
        for k, j in enumerate(idx):
            out[j] = val[k]
    return out


def borne(J, i):
    """Dernier octet touche par un accessor, pour verifier qu'il tient."""
    acc = J["accessors"][i]
    if "bufferView" not in acc:
        return None, None
    bv = J["bufferViews"][acc["bufferView"]]
    taille = TAILLE[acc["componentType"]] * COMPOSANTES[acc["type"]]
    stride = bv.get("byteStride") or taille
    fin = acc.get("byteOffset", 0) + (acc["count"] - 1) * stride + taille
    return fin, bv.get("byteLength", 0)


def khronos(chemin, exe):
    exe = exe or shutil.which("gltf-validator") or shutil.which("gltf_validator")
    if not exe:
        return None, ("validateur Khronos absent de la machine : ni "
                      "`gltf-validator` dans le PATH ni --khronos fourni")
    try:
        p = subprocess.run([exe, "-o", "-", "-p", chemin],
                           capture_output=True, text=True, timeout=300)
    except Exception as e:
        return None, "le validateur a echoue a demarrer : %r" % (e,)
    try:
        return json.loads(p.stdout or "{}"), None
    except json.JSONDecodeError:
        return None, "sortie du validateur illisible : %r" % (p.stdout[:200],)


def controler(J, BIN, anomalies_conteneur, taille_fichier, reg):
    R = {"conteneur": {"anomalies": anomalies_conteneur,
                       "octets": taille_fichier, "bin": len(BIN)}}
    reg.exige("glb.conteneur", "entete, longueurs et alignement des chunks",
              "lecture octet par octet", 0, len(anomalies_conteneur),
              not anomalies_conteneur)
    reg.exige("gltf.version", "asset.version vaut 2.0", "chunk JSON",
              "2.0", J.get("asset", {}).get("version"),
              J.get("asset", {}).get("version") == "2.0")

    # --- les bufferViews tiennent dans le buffer
    hors = []
    for k, bv in enumerate(J.get("bufferViews", [])):
        fin = bv.get("byteOffset", 0) + bv.get("byteLength", 0)
        if fin > len(BIN):
            hors.append([k, fin, len(BIN)])
        if bv.get("byteStride") is not None and bv["byteStride"] % 4:
            hors.append([k, "byteStride %d non multiple de 4" % bv["byteStride"]])
    reg.exige("gltf.bufferviews", "chaque bufferView tient dans le BIN",
              "%d bufferViews" % len(J.get("bufferViews", [])), 0, len(hors),
              not hors)
    R["bufferviews_hors_bornes"] = hors

    # --- les accessors : type, alignement, bornes
    fautes = []
    for i, acc in enumerate(J.get("accessors", [])):
        if acc["componentType"] not in TAILLE:
            fautes.append([i, "componentType %r inconnu" % acc["componentType"]]); continue
        if acc["type"] not in COMPOSANTES:
            fautes.append([i, "type %r inconnu" % acc["type"]]); continue
        if acc.get("byteOffset", 0) % TAILLE[acc["componentType"]]:
            fautes.append([i, "byteOffset non aligne sur le composant"])
        fin, dispo = borne(J, i)
        if fin is not None and fin > dispo:
            fautes.append([i, "deborde son bufferView : %d > %d" % (fin, dispo)])
    sp_f = []
    for i, acc in enumerate(J.get("accessors", [])):
        sp = acc.get("sparse")
        if not sp:
            continue
        if not 0 < sp["count"] <= acc["count"]:
            sp_f.append([i, "count sparse %d hors de %d" % (sp["count"], acc["count"])])
        idx = [v[0] for v in _brut(J, BIN, sp["indices"]["bufferView"],
                                   sp["indices"].get("byteOffset", 0),
                                   sp["indices"]["componentType"], 1, sp["count"])]
        if any(idx[k] >= idx[k + 1] for k in range(len(idx) - 1)):
            sp_f.append([i, "indices sparse non strictement croissants"])
        if idx and max(idx) >= acc["count"]:
            sp_f.append([i, "indice sparse %d >= count %d" % (max(idx), acc["count"])])
    reg.exige("gltf.sparse", "blocs sparse : indices croissants et dans les bornes",
              "%d accessor(s) sparse" % sum(1 for x in J.get("accessors", [])
                                            if "sparse" in x),
              0, len(sp_f), not sp_f)
    R["sparse_fautifs"] = sp_f

    reg.exige("gltf.accessors", "type, alignement et bornes de chaque accessor",
              "%d accessors" % len(J.get("accessors", [])), 0, len(fautes),
              not fautes)
    R["accessors_fautifs"] = fautes
    if fautes:
        return R

    # --- min/max declares contre min/max reels (ACCESSOR_MIN/MAX_MISMATCH)
    ecarts = []
    for i, acc in enumerate(J.get("accessors", [])):
        if "min" not in acc or "max" not in acc:
            continue
        vals = decoder(J, BIN, i)
        if not vals:
            continue
        nc = len(vals[0])
        for c in range(nc):
            col = [v[c] for v in vals]
            for nom, reel, decl in (("min", min(col), acc["min"][c]),
                                    ("max", max(col), acc["max"][c])):
                if abs(reel - decl) > 1e-5 * max(1.0, abs(decl)):
                    ecarts.append([i, nom, c, reel, decl])
    reg.exige("gltf.min_max", "les min/max declares sont les vrais",
              "recalcul sur les donnees", 0, len(ecarts), not ecarts)
    R["min_max_faux"] = ecarts[:20]

    # --- indices : dans les bornes, sans valeur de primitive restart
    idx_f, norm_f, poids_f, joints_f = [], [], [], []
    n_joints = len(J.get("skins", [{}])[0].get("joints", [])) if J.get("skins") else 0
    for mi, m in enumerate(J.get("meshes", [])):
        for pi, p in enumerate(m.get("primitives", [])):
            npos = J["accessors"][p["attributes"]["POSITION"]]["count"]
            if "indices" in p:
                acc = J["accessors"][p["indices"]]
                vals = [v[0] for v in decoder(J, BIN, p["indices"])]
                if vals and max(vals) >= npos:
                    idx_f.append([mi, pi, "indice %d >= %d sommets" % (max(vals), npos)])
                r = RESTART.get(acc["componentType"])
                if r is not None and r in vals:
                    idx_f.append([mi, pi, "valeur de primitive restart presente"])
                if len(vals) % 3:
                    idx_f.append([mi, pi, "%d indices, non multiple de 3" % len(vals)])
            if "NORMAL" in p["attributes"]:
                for v in decoder(J, BIN, p["attributes"]["NORMAL"]):
                    L = math.sqrt(sum(x * x for x in v))
                    if abs(L - 1.0) > 1e-3:
                        norm_f.append(round(L, 6))
            if "WEIGHTS_0" in p["attributes"]:
                for v in decoder(J, BIN, p["attributes"]["WEIGHTS_0"]):
                    s = sum(v)
                    if abs(s - 1.0) > 2e-3:
                        poids_f.append(round(s, 6))
            if "JOINTS_0" in p["attributes"] and n_joints:
                for v in decoder(J, BIN, p["attributes"]["JOINTS_0"]):
                    if max(v) >= n_joints:
                        joints_f.append(max(v))
    reg.exige("gltf.indices", "indices dans les bornes, triangles complets",
              "%d meshes" % len(J.get("meshes", [])), 0, len(idx_f), not idx_f)
    reg.exige("gltf.normales", "normales unitaires a 1e-3",
              "toutes les normales", 0, len(norm_f), not norm_f)
    reg.exige("gltf.poids", "les poids de peau somment a 1 a 2e-3",
              "tous les sommets peses", 0, len(poids_f), not poids_f)
    reg.exige("gltf.joints", "chaque index d'os designe un joint du skin",
              "%d joints" % n_joints, 0, len(joints_f), not joints_f)
    R["indices"] = idx_f
    R["normales_hors_norme"] = norm_f[:20]
    R["poids_non_normalises"] = poids_f[:20]

    # --- morph targets : meme compte partout, et les poids par defaut suivent
    inc = []
    for mi, m in enumerate(J.get("meshes", [])):
        n = {len(p.get("targets", [])) for p in m.get("primitives", [])}
        if len(n) > 1:
            inc.append([mi, sorted(n)])
        nt = max(n) if n else 0
        if "weights" in m and len(m["weights"]) != nt:
            inc.append([mi, "%d poids pour %d targets" % (len(m["weights"]), nt)])
    reg.exige("gltf.morphs", "meme nombre de targets sur toutes les primitives",
              "%d meshes" % len(J.get("meshes", [])), 0, len(inc), not inc)

    # --- hierarchie de noeuds : un seul parent, aucun cycle
    parent, deux = {}, []
    for i, nd in enumerate(J.get("nodes", [])):
        for c in nd.get("children", []):
            if c in parent:
                deux.append(c)
            parent[c] = i
    cycle = False
    for i in range(len(J.get("nodes", []))):
        vu, k = set(), i
        while k in parent:
            k = parent[k]
            if k in vu:
                cycle = True; break
            vu.add(k)
    reg.exige("gltf.hierarchie", "chaque noeud a au plus un parent, sans cycle",
              "%d noeuds" % len(J.get("nodes", [])), "0 double, 0 cycle",
              "%d double(s), %s" % (len(deux), "cycle" if cycle else "0 cycle"),
              not deux and not cycle)

    # --- animations : echantillons coherents, temps borne
    anim_f = []
    for ai, an in enumerate(J.get("animations", [])):
        for si, sp in enumerate(an.get("samplers", [])):
            ain, aout = J["accessors"][sp["input"]], J["accessors"][sp["output"]]
            if "min" not in ain or "max" not in ain:
                anim_f.append([ai, si, "l'entree n'a pas de min/max"])
            if ain["type"] != "SCALAR" or ain["componentType"] != 5126:
                anim_f.append([ai, si, "l'entree n'est pas un flottant scalaire"])
            t = [v[0] for v in decoder(J, BIN, sp["input"])]
            if any(t[k] >= t[k + 1] for k in range(len(t) - 1)):
                anim_f.append([ai, si, "temps non strictement croissants"])
            r = 1 if sp.get("interpolation") != "CUBICSPLINE" else 3
            if aout["count"] % ain["count"]:
                anim_f.append([ai, si, "%d sorties pour %d entrees"
                               % (aout["count"], ain["count"])])
            elif sp.get("interpolation") == "CUBICSPLINE" \
                    and aout["count"] != ain["count"] * 3 \
                    and aout["count"] % (ain["count"] * 3):
                anim_f.append([ai, si, "cubique sans triplet de tangentes"])
        for ci, ch in enumerate(an.get("channels", [])):
            if ch["sampler"] >= len(an.get("samplers", [])):
                anim_f.append([ai, ci, "canal vers un sampler inexistant"])
            if ch["target"].get("path") not in ("translation", "rotation",
                                                "scale", "weights"):
                anim_f.append([ai, ci, "chemin %r inconnu" % ch["target"].get("path")])
    reg.exige("gltf.animations", "echantillonneurs et canaux coherents",
              "%d animation(s)" % len(J.get("animations", [])), 0, len(anim_f),
              not anim_f)
    R["animations_fautives"] = anim_f

    # --- rotations : quaternions unitaires (ROTATION_NON_UNIT)
    q_f = []
    for an in J.get("animations", []):
        for ch in an.get("channels", []):
            if ch["target"].get("path") != "rotation":
                continue
            for v in decoder(J, BIN, an["samplers"][ch["sampler"]]["output"]):
                L = math.sqrt(sum(x * x for x in v))
                if abs(L - 1.0) > 2e-3:
                    q_f.append(round(L, 6))
    for nd in J.get("nodes", []):
        if "rotation" in nd:
            L = math.sqrt(sum(x * x for x in nd["rotation"]))
            if abs(L - 1.0) > 2e-3:
                q_f.append(round(L, 6))
    reg.exige("gltf.quaternions", "quaternions unitaires a 2e-3",
              "noeuds et animations", 0, len(q_f), not q_f)

    # --- skin : autant de matrices de bind que de joints
    sk = []
    for i, s in enumerate(J.get("skins", [])):
        if "inverseBindMatrices" in s:
            a = J["accessors"][s["inverseBindMatrices"]]
            if a["count"] != len(s["joints"]):
                sk.append([i, a["count"], len(s["joints"])])
            if a["type"] != "MAT4":
                sk.append([i, "matrices de bind de type %s" % a["type"]])
    reg.exige("gltf.skin", "une matrice de bind par joint",
              "%d skin(s)" % len(J.get("skins", [])), 0, len(sk), not sk)

    R["resume"] = {
        "meshes": len(J.get("meshes", [])), "nodes": len(J.get("nodes", [])),
        "accessors": len(J.get("accessors", [])),
        "animations": [x.get("name") for x in J.get("animations", [])],
        "extensions_requises": J.get("extensionsRequired", []),
        "generator": J.get("asset", {}).get("generator")}
    return R


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--khronos")
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    chemin = os.path.abspath(Rp(o.input))

    reg = Registre("validation-glb")
    J, BIN, anomalies, taille = lire_glb(chemin)
    R = controler(J, BIN, anomalies, taille, reg)

    kh, raison = khronos(chemin, o.khronos)
    if kh is None:
        reg.saute("khronos.validator",
                   "le validateur officiel Khronos ne signale aucune erreur",
                   raison)
    else:
        n = kh.get("issues", {}).get("numErrors", -1)
        reg.exige("khronos.validator", "aucune erreur signalee par Khronos",
                  "gltf-validator", 0, n, n == 0)
    R["khronos"] = kh if kh is not None else {"saute": raison}
    R["fichier"] = os.path.relpath(chemin, RACINE)
    R["registre"] = reg.bilan()

    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("VALIDATION", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
