"""
INSPECTER L'ASSET SOURCE DU VISAGE — lecture seule.

Le chat 3 sera l'unique auteur de la géométrie faciale. Il lui faut savoir
exactement sur quoi il travaille AVANT d'y toucher : combien de sommets, quels
objets, quels matériaux, si les yeux, les dents et la langue existent, et si la
topologie autour des yeux et de la bouche est exploitable.

Ce script NE MODIFIE RIEN. Il ouvre, mesure, écrit un JSON, et s'arrête.
"""
import hashlib
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import bpy
import mathutils

PAQUET = os.environ["ATLAS_BASE_MESH"]
COLLECTION = "Body Male - Realistic"
SORTIE = sys.argv[sys.argv.index("--") + 1]

rap = {"asset": os.path.basename(PAQUET),
       "collection": COLLECTION,
       "blender": bpy.app.version_string,
       "taille_octets": os.path.getsize(PAQUET)}

h = hashlib.sha256()
with open(PAQUET, "rb") as f:
    for bloc in iter(lambda: f.read(1 << 20), b""):
        h.update(bloc)
rap["sha256"] = h.hexdigest()

bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
    rap["collections_du_paquet"] = sorted(src.collections)
    dst.collections = [COLLECTION]
col = dst.collections[0]
bpy.context.scene.collection.children.link(col)
bpy.context.view_layer.update()

objets = [o for o in col.all_objects]
mailles = [o for o in objets if o.type == "MESH"]
rap["objets"] = [{"nom": o.name, "type": o.type,
                  "sommets": len(o.data.vertices) if o.type == "MESH" else None,
                  "faces": len(o.data.polygons) if o.type == "MESH" else None,
                  "materiaux": [m.name for m in o.data.materials] if o.type == "MESH" else []}
                 for o in objets]
rap["nombre_objets"] = len(objets)
rap["nombre_mailles"] = len(mailles)
rap["sommets_total"] = sum(len(o.data.vertices) for o in mailles)
rap["faces_total"] = sum(len(o.data.polygons) for o in mailles)
rap["materiaux"] = sorted({m.name for o in mailles for m in o.data.materials if m})

# Yeux, dents, langue : présents ou non, nommément.
def cherche(*motifs):
    return [o.name for o in objets
            if any(m in o.name.lower() for m in motifs)]


rap["yeux"] = cherche("eye")
rap["dents"] = cherche("teeth", "tooth")
rap["langue"] = cherche("tongue")
rap["cils_sourcils"] = cherche("lash", "brow")

corps = max(mailles, key=lambda o: len(o.data.vertices))
rap["maillage_principal"] = corps.name
co = [corps.matrix_world @ v.co for v in corps.data.vertices]
zmin, zmax = min(q.z for q in co), max(q.z for q in co)
rap["hauteur_brute_m"] = round(zmax - zmin, 4)
rap["echelle_objet"] = [round(x, 4) for x in corps.scale]

# ── LA TÊTE : ce qui intéresse le chat 3 ──
# On la délimite par la hauteur : au-dessus des épaules. Repère mesuré, non
# supposé — la tête commence là où la section horizontale se resserre après le
# maximum des épaules.
tranches = {}
for q in co:
    tranches.setdefault(round((q.z - zmin) / (zmax - zmin) * 200), []).append(q)
larg = {k: (max(x.x for x in v) - min(x.x for x in v))
        for k, v in tranches.items() if len(v) > 20}
if larg:
    k_epaules = max((v, k) for k, v in larg.items() if k > 150)[1]
    z_cou = None
    for k in range(k_epaules, 201):
        if k in larg and larg[k] < larg[k_epaules] * 0.35:
            z_cou = zmin + (zmax - zmin) * k / 200.0
            break
    rap["hauteur_epaules_m"] = round(zmin + (zmax - zmin) * k_epaules / 200.0, 4)
    if z_cou:
        tete = [i for i, q in enumerate(co) if q.z >= z_cou]
        rap["base_du_cou_m"] = round(z_cou, 4)
        rap["sommets_de_la_tete"] = len(tete)
        rap["part_de_la_tete"] = round(len(tete) / len(co), 4)
        # Densité autour des yeux et de la bouche : c'est ce qui décide si la
        # topologie est exploitable pour des shape keys.
        yeux_obj = [o for o in mailles if "eye" in o.name.lower()]
        if yeux_obj:
            cy = sum((yeux_obj[0].matrix_world @ v.co for v in yeux_obj[0].data.vertices),
                     mathutils.Vector((0, 0, 0))) / len(yeux_obj[0].data.vertices)
            rap["hauteur_des_yeux_m"] = round(cy.z, 4)
            autour = [i for i in tete if (co[i] - cy).length < 0.030]
            rap["sommets_dans_30mm_autour_d_un_oeil"] = len(autour)
            # La bouche est plus bas ; on prend une sphère au tiers inférieur
            # de la tête, centrée dans le plan sagittal.
            zb = z_cou + (cy.z - z_cou) * 0.45
            cb = mathutils.Vector((cy.x * 0.0, min(q.y for q in co) * 0.0, zb))
            devant = [q for q in co if q.z > z_cou and abs(q.x) < 0.02]
            if devant:
                yb = min(q.y for q in devant)
                cb = mathutils.Vector((0.0, yb + 0.01, zb))
                rap["sommets_dans_30mm_autour_de_la_bouche"] = len(
                    [i for i in tete if (co[i] - cb).length < 0.030])
                rap["hauteur_estimee_de_la_bouche_m"] = round(zb, 4)

# Systèmes déjà présents : armature, shape keys, modificateurs, UV.
rap["armatures"] = [o.name for o in objets if o.type == "ARMATURE"]
rap["shape_keys"] = {o.name: (len(o.data.shape_keys.key_blocks)
                              if o.data.shape_keys else 0) for o in mailles}
rap["modificateurs"] = {o.name: [m.type for m in o.modifiers] for o in mailles
                        if o.modifiers}
rap["uv"] = {o.name: [u.name for u in o.data.uv_layers] for o in mailles}
rap["multires"] = {o.name: [m.levels for m in o.modifiers if m.type == "MULTIRES"]
                   for o in mailles if any(m.type == "MULTIRES" for m in o.modifiers)}

# Triangles et n-gons : une topologie de visage doit être en quads.
q = t = n = 0
for o in mailles:
    for p in o.data.polygons:
        c = len(p.vertices)
        if c == 3:
            t += 1
        elif c == 4:
            q += 1
        else:
            n += 1
rap["faces_quads"] = q
rap["faces_triangles"] = t
rap["faces_ngons"] = n
rap["part_de_quads"] = round(q / max(1, q + t + n), 4)

with open(SORTIE, "w", encoding="utf-8") as f:
    json.dump(rap, f, ensure_ascii=False, indent=2)
print("ATLAS_VISAGE " + json.dumps(
    {k: rap[k] for k in ("nombre_objets", "sommets_total", "faces_total",
                         "part_de_quads", "yeux", "dents", "langue",
                         "armatures", "sha256")}, ensure_ascii=False))
