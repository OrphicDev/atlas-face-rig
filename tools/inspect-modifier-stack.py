"""F0-E.1 — releve de la pile de modificateurs, sans la modifier."""
import argparse, hashlib, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLES = ("levels", "sculpt_levels", "render_levels", "total_levels", "show_viewport",
        "show_render", "show_in_editmode", "use_custom_normals", "quality",
        "uv_smooth", "boundary_smooth", "use_creases", "use_sculpt_base_mesh")
a = argparse.ArgumentParser(); a.add_argument("--output", required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
h = hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest()
R = {"blend": os.path.relpath(bpy.data.filepath, RACINE), "blend_sha256": h,
     "blender": bpy.app.version_string, "objets": {}}
for ob in sorted([x for x in bpy.data.objects if x.type == "MESH"], key=lambda x: x.name):
    mods = []
    for i, m in enumerate(ob.modifiers):
        d = {"ordre": i, "nom": m.name, "type": m.type}
        for c in CLES:
            if hasattr(m, c):
                v = getattr(m, c)
                d[c] = v if isinstance(v, (int, float, bool, str)) else str(v)
        mods.append(d)
    R["objets"][ob.name] = {"modificateurs": mods,
                            "shape_keys": len(ob.data.shape_keys.key_blocks) if ob.data.shape_keys else 0,
                            "sommets": len(ob.data.vertices)}
    if mods: print(" ", ob.name, [(m["type"], m.get("levels")) for m in mods])
arm = [x.name for x in bpy.data.objects if x.type == "ARMATURE"]
R["armatures"] = arm
R["armature_modifier"] = [ob.name for ob in bpy.data.objects if ob.type == "MESH"
                          and any(m.type == "ARMATURE" for m in ob.modifiers)]
p = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
json.dump(R, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("STACK_OK armatures", arm, "| armature modifier", R["armature_modifier"])
