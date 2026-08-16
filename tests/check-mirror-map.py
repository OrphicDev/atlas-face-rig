"""F0-B.6 bis (mini-test) — la carte miroir est-elle une vraie permutation ?"""
import argparse, hashlib, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
_wai = importlib.util.module_from_spec(_s); _s.loader.exec_module(_wai)

a = argparse.ArgumentParser(); a.add_argument("--map", required=True)
a.add_argument("--report", required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
p = o.map if os.path.isabs(o.map) else os.path.join(RACINE, o.map)
M = json.load(open(p, encoding="utf-8"))
reg = Registre("check-mirror-map")
obj = bpy.data.objects[M["mesh"]]
me, n = obj.data, len(obj.data.vertices)
carte = M["mirror_indices"]
co = [v.co.copy() for v in me.vertices]
plan = M["sagittal_plane_object_local"]

reg.exige("miroir.taille", "taille egale au nombre de sommets signe",
          "blend auteur", n, len(carte), len(carte) == n)
reg.exige("miroir.permutation", "permutation de 0..n-1", "carte",
          "0..%d" % (n - 1), "triee" if sorted(carte) == list(range(n)) else "non",
          sorted(carte) == list(range(n)))
reg.exige("miroir.involutive", "map[map[i]] == i", "carte", True,
          all(carte[carte[i]] == i for i in range(n)),
          all(carte[carte[i]] == i for i in range(n)))
fixes = [i for i in M["midline_fixed"] if carte[i] != i]
reg.exige("miroir.midline_fixe", "les sommets medians sont leur propre image",
          "carte", [], fixes, not fixes)
mauvaises = [g for g in M["seed_pairs"] if carte[g[0]] != g[1]]
reg.exige("miroir.graines", "toutes les paires de graines sont respectees",
          "config/mirror-landmarks.json", [], mauvaises, not mauvaises)
ar = {tuple(sorted(e.vertices)) for e in me.edges}
fa = {tuple(sorted(pp.vertices)) for pp in me.polygons}
so = sum(1 for x in ar if tuple(sorted((carte[x[0]], carte[x[1]]))) not in ar)
sf = sum(1 for f in fa if tuple(sorted(carte[i] for i in f)) not in fa)
reg.exige("miroir.aretes", "toute arete devient une arete", "maillage", 0, so, so == 0)
reg.exige("miroir.faces", "toute face a un homologue", "maillage", 0, sf, sf == 0)
reg.exige("miroir.topology_sha", "empreinte de connectivite", "blend auteur",
          M["topology_sha256"][:16], _wai.sha_topologie(obj)[:16],
          _wai.sha_topologie(obj) == M["topology_sha256"])
reg.exige("miroir.blend_sha", "SHA du blend auteur", "blend ouvert",
          M["author_blend_sha256"][:16], _wai.sha_fichier(bpy.data.filepath)[:16],
          _wai.sha_fichier(bpy.data.filepath) == M["author_blend_sha256"])
ok = reg.conclure()
s = o.report if os.path.isabs(o.report) else os.path.join(RACINE, o.report)
os.makedirs(os.path.dirname(s) or ".", exist_ok=True)
json.dump({"status": "PASS" if ok else "FAIL", **reg.bilan()},
          open(s, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("MIRROR_CHECK", "OK" if ok else "ECHEC")
sys.exit(0 if ok else 2)
