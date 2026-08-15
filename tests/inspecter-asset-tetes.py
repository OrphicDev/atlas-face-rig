"""Mesurer les collections de tête dédiées du paquet. Lecture seule."""
import json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, mathutils
PAQUET = os.environ["ATLAS_BASE_MESH"]
out = {}
for nom in ("Head (Animation) - Realistic", "Head (Sculpting) - Realistic"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = [nom]
    col = dst.collections[0]
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.update()
    objs = list(col.all_objects)
    mailles = [o for o in objs if o.type == "MESH"]
    q = t = n = 0
    for o in mailles:
        for p in o.data.polygons:
            c = len(p.vertices)
            q += c == 4; t += c == 3; n += c > 4
    princ = max(mailles, key=lambda o: len(o.data.vertices)) if mailles else None
    co = [princ.matrix_world @ v.co for v in princ.data.vertices] if princ else []
    d = {"objets": [(o.name, len(o.data.vertices), len(o.data.polygons))
                    for o in mailles],
         "sommets_total": sum(len(o.data.vertices) for o in mailles),
         "faces_total": sum(len(o.data.polygons) for o in mailles),
         "quads": q, "triangles": t, "ngons": n,
         "part_de_quads": round(q / max(1, q + t + n), 4),
         "yeux": [o.name for o in objs if "eye" in o.name.lower()],
         "dents": [o.name for o in objs if "teeth" in o.name.lower() or "tooth" in o.name.lower()],
         "langue": [o.name for o in objs if "tongue" in o.name.lower()],
         "shape_keys": {o.name: (len(o.data.shape_keys.key_blocks)
                                 if o.data.shape_keys else 0) for o in mailles},
         "uv": {o.name: [u.name for u in o.data.uv_layers] for o in mailles},
         "modificateurs": {o.name: [m.type for m in o.modifiers] for o in mailles if o.modifiers}}
    if co:
        d["hauteur_m"] = round(max(x.z for x in co) - min(x.z for x in co), 4)
        d["largeur_m"] = round(max(x.x for x in co) - min(x.x for x in co), 4)
    out[nom] = d
open(sys.argv[sys.argv.index("--") + 1], "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=2))
print("ATLAS_TETES " + json.dumps({k: {"sommets": v["sommets_total"],
      "quads": v["part_de_quads"], "objets": len(v["objets"]),
      "yeux": len(v["yeux"]), "dents": len(v["dents"]), "langue": len(v["langue"])}
      for k, v in out.items()}, ensure_ascii=False))
