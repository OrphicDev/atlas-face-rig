"""F0-E.9 bis — contre-epreuve du controleur glTF.

Un controleur qui dit PASS sur un bon fichier ne prouve rien : il faut qu'il
REFUSE des fautes connues, et qu'il refuse par la sonde qui les nomme. Chaque
mutation ci-dessous fabrique une faute precise dans une copie du GLB, et le
test exige que la sonde attendue passe a FAIL — et elle seule si possible.

    python3 tests/validate-glb-negatif.py --input exports/atlas-face-spike.glb \
      --report reports/f0-final/validation-glb-negatif.json
"""
import argparse, array, copy, json, os, struct, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
import importlib.util as _u
_s = _u.spec_from_file_location("vg", os.path.join(RACINE, "tools", "validate_glb.py"))
VG = _u.module_from_spec(_s); _s.loader.exec_module(VG)


def ecrire(J, BIN):
    j = json.dumps(J, separators=(",", ":")).encode("utf-8")
    j += b" " * (-len(j) % 4)
    b = BIN + b"\0" * (-len(BIN) % 4)
    total = 12 + 8 + len(j) + (8 + len(b) if b else 0)
    out = struct.pack("<III", 0x46546C67, 2, total)
    out += struct.pack("<II", len(j), 0x4E4F534A) + j
    if b:
        out += struct.pack("<II", len(b), 0x004E4942) + b
    return out


def ecrire_composant(BIN, J, acc_i, elem, comp, valeur):
    """Ecrit UN composant, sur exactement sa taille.

    Ecrire 4 octets quel que soit le type etait une faute de ce harnais : sur
    un accessor de 2 ou 1 octet, la tranche remplacee etait plus longue que la
    valeur ecrite, ce qui RACCOURCISSAIT le BIN et decalait tout ce qui suit.
    Deux mutations abimaient alors cinq sondes au lieu d'une, et la
    contre-epreuve semblait reussir pour la mauvaise raison.
    """
    acc = J["accessors"][acc_i]
    bv = J["bufferViews"][acc["bufferView"]]
    ct = acc["componentType"]
    nc = VG.COMPOSANTES[acc["type"]]
    taille_c = VG.TAILLE[ct]
    taille = taille_c * nc
    stride = bv.get("byteStride") or taille
    d = (bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
         + elem * stride + comp * taille_c)
    brut = array.array(VG.CODE[ct], [valeur]).tobytes()
    assert len(brut) == taille_c, "taille de composant incoherente"
    a = bytearray(BIN)
    a[d:d + taille_c] = brut
    assert len(a) == len(BIN), "le BIN a change de taille"
    return bytes(a)


ecrire_flottant = ecrire_composant
ecrire_entier = ecrire_composant


def premier(J, attribut):
    return J["meshes"][0]["primitives"][0]["attributes"][attribut]


# ------------------------------------------------------------- mutations ----
def m_conteneur(J, B):
    return J, B, "glb.conteneur", "longueur totale declaree fausse"


def m_version(J, B):
    J["asset"]["version"] = "1.0"
    return J, B, "gltf.version", "asset.version = 1.0"


def m_bufferview(J, B):
    J["bufferViews"][0]["byteLength"] = len(B) + 4096
    return J, B, "gltf.bufferviews", "un bufferView deborde le BIN"


def m_minmax(J, B):
    for a in J["accessors"]:
        if "min" in a:
            a["min"][0] = a["min"][0] - 5.0
            break
    return J, B, "gltf.min_max", "un min declare plus bas que le vrai"


def m_indices(J, B):
    p = J["meshes"][0]["primitives"][0]
    n = J["accessors"][p["attributes"]["POSITION"]]["count"]
    return J, ecrire_entier(B, J, p["indices"], 0, 0, n + 7), \
        "gltf.indices", "un indice depasse le nombre de sommets"


def m_normale(J, B):
    return J, ecrire_flottant(B, J, premier(J, "NORMAL"), 3, 0, 4.0), \
        "gltf.normales", "une normale de longueur 4"


def m_poids(J, B):
    return J, ecrire_flottant(B, J, premier(J, "WEIGHTS_0"), 5, 0, 0.5), \
        "gltf.poids", "des poids qui ne somment plus a 1"


def m_joints(J, B):
    return J, ecrire_entier(B, J, premier(J, "JOINTS_0"), 2, 0, 250), \
        "gltf.joints", "un index d'os hors du skin"


def m_sparse(J, B):
    for i, a in enumerate(J["accessors"]):
        if "sparse" in a:
            sp = a["sparse"]
            bv = J["bufferViews"][sp["indices"]["bufferView"]]
            d = bv.get("byteOffset", 0) + sp["indices"].get("byteOffset", 0)
            n = array.array(VG.CODE[sp["indices"]["componentType"]], B[d:d + 4])
            a2 = bytearray(B)
            a2[d:d + 2] = array.array(
                VG.CODE[sp["indices"]["componentType"]], [n[1] + 5]).tobytes()
            return J, bytes(a2), "gltf.sparse", "indices sparse non croissants"
    return None


def m_morphs(J, B):
    J["meshes"][0]["weights"] = [0.0]
    return J, B, "gltf.morphs", "un poids de morph pour trois targets"


def m_hierarchie(J, B):
    for n in J["nodes"]:
        if n.get("children"):
            n["children"] = n["children"] + [n["children"][0]] \
                if len(J["nodes"]) < 2 else n["children"]
            break
    # deux parents pour le meme enfant
    cible = next((c for n in J["nodes"] for c in n.get("children", [])), None)
    for n in J["nodes"]:
        if cible is not None and cible not in n.get("children", []):
            n.setdefault("children", []).append(cible)
            break
    return J, B, "gltf.hierarchie", "un noeud avec deux parents"


def m_animation(J, B):
    J["animations"][0]["channels"][0]["target"]["path"] = "couleur"
    return J, B, "gltf.animations", "un canal vers un chemin inconnu"


def m_quaternion(J, B):
    for n in J["nodes"]:
        if "rotation" in n:
            n["rotation"][0] = n["rotation"][0] + 1.5
            return J, B, "gltf.quaternions", "un quaternion non unitaire"
    J["nodes"][0]["rotation"] = [0.9, 0.9, 0.9, 0.9]
    return J, B, "gltf.quaternions", "un quaternion non unitaire"


def m_skin(J, B):
    # On ajoute un joint plutot que de gonfler l'accessor : gonfler le count
    # faisait deborder le bufferView, et la faute tombait sur `gltf.accessors`
    # — detectee, mais pas par la sonde visee. La mutation doit viser une
    # seule sonde, sinon la contre-epreuve ne prouve pas ce qu'elle annonce.
    J["skins"][0]["joints"] = J["skins"][0]["joints"] + [J["skins"][0]["joints"][0]]
    return J, B, "gltf.skin", "un joint de plus que de matrices de bind"


MUTATIONS = [m_conteneur, m_version, m_bufferview, m_minmax, m_indices,
             m_normale, m_poids, m_joints, m_sparse, m_morphs, m_hierarchie,
             m_animation, m_quaternion, m_skin]


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--report", required=True)
    o = a.parse_args()
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    src = os.path.abspath(Rp(o.input))
    J0, B0, an0, t0 = VG.lire_glb(src)

    # temoin : sans mutation, le controleur ne doit rien reprocher
    reg = Registre("validation-glb-negatif")
    tem = Registre("temoin")
    VG.controler(copy.deepcopy(J0), B0, an0, t0, tem)
    reg.exige("temoin.intact", "le fichier non mute passe le controleur",
              "GLB d'origine", 0, len(tem.echecs), not tem.echecs)

    detail = []
    for f in MUTATIONS:
        r = f(copy.deepcopy(J0), B0)
        if r is None:
            reg.saute(f.__name__, "mutation impossible", "aucun accessor eligible")
            continue
        Jm, Bm, sonde, quoi = r
        octets = ecrire(Jm, Bm)
        if f is m_conteneur:                       # faute sur le conteneur lui-meme
            octets = struct.pack("<III", 0x46546C67, 2,
                                 struct.unpack("<III", octets[:12])[2] + 16) + octets[12:]
        tmp = os.path.join(RACINE, "experiments", "gltf-spike", "_mutant.glb")
        open(tmp, "wb").write(octets)
        r2 = Registre("m")
        try:
            Jx, Bx, anx, tx = VG.lire_glb(tmp)
            VG.controler(Jx, Bx, anx, tx, r2)
            tombees = [e["id"] for e in r2.echecs]
            refus_dur = None
        except Exception as e:
            tombees, refus_dur = [], repr(e)
        os.remove(tmp)
        # Une exception n'est PAS un refus par la sonde nommee : elle prouve
        # seulement que quelque chose a casse. Seul `m_conteneur` a le droit
        # d'etre refuse a la lecture, puisque c'est le conteneur qu'il abime.
        ok = (sonde in tombees) or (refus_dur is not None and f is m_conteneur)
        detail.append({"mutation": f.__name__, "faute": quoi,
                       "sonde_attendue": sonde, "sondes_tombees": tombees,
                       "refus_a_la_lecture": refus_dur})
        reg.exige("refus." + sonde.split(".", 1)[1] + "." + f.__name__[2:],
                  "le controleur refuse : " + quoi, "mutation ciblee",
                  sonde + " en FAIL", ",".join(tombees) or (refus_dur or "rien"), ok)

    R = {"source": os.path.relpath(src, RACINE), "mutations": detail,
         "registre": reg.bilan()}
    p = Rp(o.report); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("NEGATIF", "OK" if ok else "ECHEC", "->", o.report)
    sys.exit(0 if ok else 2)
