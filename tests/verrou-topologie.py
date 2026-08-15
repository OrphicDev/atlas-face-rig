"""Verrou : echoue si la topologie ou la pose neutre de la base a change.

C'est le test que reclame F0.3. Il est fait pour ECHOUER — le jour ou une
retopologie, une fusion de sommets ou un deplacement du neutre passe
inapercu, c'est lui qui doit sortir en code non nul avant que quoi que ce
soit ne soit livre.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/verrou-topologie.py -- source/FACE_BASE_LOCKED.blend \
      tests/verrou-topologie.json
"""
import json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rig"))
import importlib.util
_s = importlib.util.spec_from_file_location(
    "cfb", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rig",
                        "construire-face-base.py"))
cfb = importlib.util.module_from_spec(_s); _s.loader.exec_module(cfb)

blend, verrou = sys.argv[sys.argv.index("--") + 1:][:2]
attendu = json.load(open(verrou, encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))
objets = [o for o in bpy.data.objects if o.type == "MESH"]
sig_t, sig_n, detail = cfb.signatures(objets)

pannes = []
if sig_t != attendu["signature_topologie"]:
    pannes.append("TOPOLOGIE MODIFIEE : %s attendu, %s obtenu"
                  % (attendu["signature_topologie"][:16], sig_t[:16]))
if sig_n != attendu["signature_neutre"]:
    pannes.append("POSE NEUTRE MODIFIEE : %s attendu, %s obtenu"
                  % (attendu["signature_neutre"][:16], sig_n[:16]))
a = {d["objet"]: d for d in attendu["objets"]}
b = {d["objet"]: d for d in detail}
if set(a) != set(b):
    pannes.append("LISTE D'OBJETS MODIFIEE : %s / %s" % (sorted(a), sorted(b)))
for nom in sorted(set(a) & set(b)):
    for cle in ("sommets", "aretes", "faces", "uv", "scale", "rotation_euler", "location"):
        if a[nom][cle] != b[nom][cle]:
            pannes.append("%s.%s : %s attendu, %s obtenu" % (nom, cle, a[nom][cle], b[nom][cle]))

print("VERROU sur", os.path.basename(blend))
print("  topologie :", "OK" if sig_t == attendu["signature_topologie"] else "ECHEC")
print("  neutre    :", "OK" if sig_n == attendu["signature_neutre"] else "ECHEC")
print("  objets    : %d, %d sommets, %d faces"
      % (len(detail), sum(d["sommets"] for d in detail), sum(d["faces"] for d in detail)))
if pannes:
    for p in pannes: print("  !", p)
    sys.exit(1)
print("VERROU_OK")
