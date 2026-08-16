"""F0-E.8 — interroge l'exporteur AVANT de l'appeler, puis exporte."""
import argparse, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
a = argparse.ArgumentParser()
a.add_argument("--output", required=True); a.add_argument("--settings", required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
op = bpy.ops.export_scene.gltf
dispo = {p.identifier for p in op.get_rna_type().properties if p.identifier != "rna_type"}
print("GLTF_OPERATOR_PROPERTIES", len(dispo))
INTENTIONS = {"filepath": os.path.abspath(Rp(o.output)), "export_format": "GLB",
              "use_selection": True, "export_apply": False, "export_animations": True,
              "export_skins": True, "export_morph": True, "export_morph_normal": True}
REQUIS = {"filepath", "export_format", "use_selection", "export_animations",
          "export_skins", "export_morph"}
manquants = sorted(REQUIS - dispo)
if manquants:
    print("options absentes sous", bpy.app.version_string, ":", manquants); sys.exit(2)
kwargs = {k: v for k, v in INTENTIONS.items() if k in dispo}
ignores = sorted(set(INTENTIONS) - set(kwargs))
bpy.ops.object.select_all(action="DESELECT")
cibles = [x for x in bpy.data.objects if x.name in ("GEO_face_runtime", "TMP_F0_JAW_RIG")]
for x in cibles:
    x.hide_set(False); x.hide_viewport = False; x.select_set(True)
bpy.context.view_layer.objects.active = next(x for x in cibles if x.type == "ARMATURE")
os.makedirs(os.path.dirname(Rp(o.output)), exist_ok=True)
res = op(**kwargs)
if "FINISHED" not in res: print("export echoue:", res); sys.exit(2)
S = {"blender": bpy.app.version_string, "options_effectives": {k: str(v) for k, v in kwargs.items()},
     "options_ignorees": ignores, "objets_exportes": sorted(x.name for x in cibles),
     "octets": os.path.getsize(Rp(o.output)),
     "proprietes_rna": sorted(dispo)}
json.dump(S, open(Rp(o.settings), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("EXPORT_OK", S["octets"], "octets | ignorees:", ignores)
