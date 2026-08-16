"""F0-B.0 (mini-test) — le JSON d'auteur et le blend forment-ils une paire ?

Recalcule les DEUX empreintes et tous les comptes, compare le chemin ouvert au
chemin declare, et sort non-zero au moindre ecart. Un caractere change dans un
SHA doit suffire a le faire echouer.

    blender -b "$FACE_AUTHOR_BLEND" \
      --python tests/check-f0-author-input.py -- \
      --contract reports/f0-final/author-input.json
"""
import argparse, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from atlas_commun import Registre

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
_wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(_wai)

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--contract", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    p = o.contract if os.path.isabs(o.contract) else os.path.join(RACINE, o.contract)
    C = json.load(open(p, encoding="utf-8"))
    reg = Registre("check-f0-author-input")

    ouvert = _wai.relatif(bpy.data.filepath) if bpy.data.filepath else "(aucun)"
    reg.exige("auteur.chemin", "le blend ouvert est celui que le contrat declare",
              "blend ouvert par Blender", C["face_author_blend"], ouvert,
              ouvert == C["face_author_blend"])

    tete = bpy.data.objects.get(C["objet"])
    if tete is None:
        reg.exige("auteur.objet", "le maillage principal existe", "scene ouverte",
                  C["objet"], "(absent)", False)
        print("ECHEC"); sys.exit(2)

    reg.exige("auteur.blend_sha256", "SHA-256 du fichier recalcule",
              "blend ouvert", C["blend_sha256"][:16],
              _wai.sha_fichier(bpy.data.filepath)[:16],
              _wai.sha_fichier(bpy.data.filepath) == C["blend_sha256"])
    reg.exige("auteur.topology_sha256", "empreinte de connectivite recalculee",
              "blend ouvert", C["topology_sha256"][:16],
              _wai.sha_topologie(tete)[:16],
              _wai.sha_topologie(tete) == C["topology_sha256"])
    me = tete.data
    for cle, mesure in (("vertices", len(me.vertices)), ("edges", len(me.edges)),
                        ("polygons", len(me.polygons)), ("loops", len(me.loops))):
        reg.exige("auteur." + cle, "compte recalcule", "blend ouvert",
                  C[cle], mesure, C[cle] == mesure)
    reg.exige("auteur.uv", "couches UV", "blend ouvert", C["uv_layers"],
              [c.name for c in me.uv_layers],
              C["uv_layers"] == [c.name for c in me.uv_layers])
    absents = [n for n in C["meshes_oculaires"] if bpy.data.objects.get(n) is None]
    reg.exige("auteur.meshes_oculaires", "les quatre meshes oculaires sont la",
              "blend ouvert", [], absents, not absents)
    reg.exige("auteur.zero_shape_key", "l'auteur n'a aucune shape key",
              "blend ouvert", 0,
              len(me.shape_keys.key_blocks) if me.shape_keys else 0,
              not me.shape_keys)

    ok = reg.conclure()
    print("AUTHOR_CHECK", "OK" if ok else "ECHEC")
    sys.exit(0 if ok else 2)
