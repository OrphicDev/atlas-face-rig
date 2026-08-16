"""F0-F.1 — la fondation finale, copie signee du blend d'auteur.

Aucune branche ne rechoisit sa source : le blend d'auteur est celui que
`reports/f0-final/author-input.json` designe et signe. On l'ouvre, on retire
UNIQUEMENT les objets temporaires nommes (jamais un Select All > Delete), et
on enregistre une copie.

    blender -b --factory-startup --python-exit-code 1 \
      --python rig/build-f0-foundation.py -- \
      --author-input reports/f0-final/author-input.json \
      --output source/FACE_F0_FOUNDATION_FINAL.blend \
      --report reports/f0-final/foundation.json
"""
import argparse, hashlib, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
WAI = importlib.util.module_from_spec(_s); _s.loader.exec_module(WAI)

a = argparse.ArgumentParser()
for f in ("--author-input", "--output", "--report"): a.add_argument(f, required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

A = json.load(open(Rp(o.author_input), encoding="utf-8"))
src = Rp(A["face_author_blend"])
reg = Registre("f0-foundation")
sha_src = WAI.sha_fichier(src)
reg.exige("fondation.source_signee", "le blend d'auteur porte bien son SHA",
          A["face_author_blend"], A["blend_sha256"], sha_src,
          sha_src == A["blend_sha256"])
if sha_src != A["blend_sha256"]:
    sys.exit(2)

bpy.ops.wm.open_mainfile(filepath=src)
# on ne supprime QUE ce qui est nomme temporaire, jamais tout
temporaires = [x.name for x in bpy.data.objects
               if x.name.startswith(("TMP_", "DBG_"))]
for n in temporaires:
    bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
reg.exige("fondation.temporaires_retires", "aucun objet TMP_ ou DBG_ ne reste",
          "suppression nominative", [], sorted(
              x.name for x in bpy.data.objects
              if x.name.startswith(("TMP_", "DBG_"))),
          not any(x.name.startswith(("TMP_", "DBG_")) for x in bpy.data.objects))

tete = bpy.data.objects[A["objet"]]
reg.exige("fondation.aucune_armature", "aucune armature dans la fondation",
          "inventaire", 0, sum(1 for x in bpy.data.objects if x.type == "ARMATURE"),
          not any(x.type == "ARMATURE" for x in bpy.data.objects))
nk = 0 if tete.data.shape_keys is None else len(tete.data.shape_keys.key_blocks)
reg.exige("fondation.aucune_shape_key", "aucune shape key permanente",
          "objet %s" % tete.name, 0, nk, nk == 0)
mr = [m for m in tete.modifiers if m.type == "MULTIRES"]
reg.exige("fondation.multires", "le Multires est present et NON applique",
          "pile de %s" % tete.name, "1 Multires niveau >= 1",
          "%d Multires niveau %s" % (len(mr), mr[0].levels if mr else "-"),
          len(mr) == 1 and mr[0].levels >= 1)
yeux = sorted(A["meshes_oculaires"])
presents = sorted(x for x in yeux if x in bpy.data.objects)
reg.exige("fondation.meshes_oculaires", "les quatre meshes oculaires sont la",
          "%d attendus" % len(yeux), yeux, presents, presents == yeux)
attendus = sorted(yeux + [A["objet"]])
inventaire = sorted(x.name for x in bpy.data.objects if x.type == "MESH")
reg.exige("fondation.cinq_meshes", "exactement les cinq meshes attendus",
          "inventaire des meshes", attendus, inventaire, inventaire == attendus)
reg.exige("fondation.topologie", "la topologie est celle du contrat",
          A["objet"], A["topology_sha256"], WAI.sha_topologie(tete),
          WAI.sha_topologie(tete) == A["topology_sha256"])

sortie = Rp(o.output)
os.makedirs(os.path.dirname(sortie), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=sortie, copy=True)
R = {"source": A["face_author_blend"], "source_sha256": sha_src,
     "sortie": os.path.relpath(sortie, RACINE),
     "sortie_sha256": WAI.sha_fichier(sortie),
     "temporaires_retires": temporaires,
     "inventaire": sorted(x.name for x in bpy.data.objects),
     "registre": reg.bilan()}
json.dump(R, open(Rp(o.report), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ok = reg.conclure()
print("FONDATION", "OK" if ok else "ECHEC", "->", o.output)
sys.exit(0 if ok else 2)
