"""F0.3 — construit `source/FACE_BASE_LOCKED.blend` et sa signature de verrou.

Ce que fait ce script, et rien d'autre :
  - charge `Head (Animation) - Realistic` depuis ATLAS_BASE_MESH ;
  - MESURE si appliquer l'echelle 0,9 est sans perte (le multires porte du
    deplacement : appliquer une echelle peut le fausser). N'applique que si la
    mesure le permet, sinon laisse en l'etat et l'ecrit dans le rapport ;
  - fige la pose neutre et enregistre les transformations ;
  - calcule la signature de topologie et la signature du neutre ;
  - sauvegarde le .blend et le fichier de verrou.

    blender --background --factory-startup --python-exit-code 1 \
      --python rig/construire-face-base.py -- source/FACE_BASE_LOCKED.blend \
      tests/verrou-topologie.json
"""
import hashlib, json, os, struct, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

COL = "Head (Animation) - Realistic"


def signatures(objets):
    """Deux empreintes : la topologie seule, puis la pose neutre.

    La topologie ignore les positions : elle ne bouge que si le nombre, l'ordre
    ou le cablage des sommets change. Le neutre, lui, bouge au moindre
    deplacement — les deux servent a des controles differents.
    """
    ht, hn = hashlib.sha256(), hashlib.sha256()
    detail = []
    for o in sorted(objets, key=lambda x: x.name):
        me = o.data
        ht.update(o.name.encode()); hn.update(o.name.encode())
        ht.update(struct.pack("<II", len(me.vertices), len(me.polygons)))
        for p in me.polygons:
            ht.update(struct.pack("<I", len(p.vertices)))
            ht.update(struct.pack("<%dI" % len(p.vertices), *p.vertices))
        for e in me.edges:
            ht.update(struct.pack("<II", *sorted(e.vertices)))
        for v in me.vertices:
            hn.update(struct.pack("<3f", *v.co))
        hn.update(struct.pack("<3f", *o.location))
        hn.update(struct.pack("<3f", *o.scale))
        hn.update(struct.pack("<3f", *o.rotation_euler))
        detail.append({"objet": o.name, "sommets": len(me.vertices),
                       "aretes": len(me.edges), "faces": len(me.polygons),
                       "uv": [u.name for u in me.uv_layers],
                       "modificateurs": [m.type for m in o.modifiers],
                       "location": [round(x, 6) for x in o.location],
                       "rotation_euler": [round(x, 6) for x in o.rotation_euler],
                       "scale": [round(x, 6) for x in o.scale],
                       "shape_keys": (len(me.shape_keys.key_blocks) if me.shape_keys else 0)})
    return ht.hexdigest(), hn.hexdigest(), detail


def evalue_monde(objets):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for o in sorted(objets, key=lambda x: x.name):
        e = o.evaluated_get(dg); me = e.to_mesh()
        out += [o.matrix_world @ v.co.copy() for v in me.vertices]
        e.to_mesh_clear()
    return out


def ecart_max_mm(a, b):
    if len(a) != len(b): return None
    return round(max((x - y).length for x, y in zip(a, b)) * 1000, 9)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    sortie_blend, sortie_verrou = args[0], args[1]
    PAQUET = os.environ["ATLAS_BASE_MESH"]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
        dst.collections = [COL]
    col = dst.collections[0]
    bpy.context.scene.collection.children.link(col)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.view_layer.update()
    objets = [o for o in col.all_objects if o.type == "MESH"]

    rapport = {"asset": os.path.basename(PAQUET), "collection": COL,
               "blender": bpy.app.version_string,
               "avant": {o.name: {"scale": [round(x, 6) for x in o.scale],
                                  "rotation_euler": [round(x, 6) for x in o.rotation_euler],
                                  "location": [round(x, 6) for x in o.location]}
                         for o in objets}}

    # --- l'echelle peut-elle etre appliquee sans deplacer la surface ? ---
    avant = evalue_monde(objets)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objets: o.select_set(True)
    bpy.context.view_layer.objects.active = objets[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apres = evalue_monde(objets)
    ecart = ecart_max_mm(avant, apres)
    # Tolerance = le critere du projet lui-meme (docs/SCOPE_V1.md : toute
    # commande a 0 rend le neutre a moins de 0,01 mm). Un seuil plus serre que
    # la precision du flottant simple sur des coordonnees a 1,5 m du repere
    # refuserait l'operation pour du bruit d'arrondi, pas pour une perte.
    TOL = 0.01
    rapport["application_echelle"] = {
        "ecart_max_mm": ecart, "tolerance_mm": TOL,
        "origine_de_la_tolerance": "docs/SCOPE_V1.md, critere de retour au neutre"}
    if ecart is None or ecart > TOL:
        rapport["application_echelle"]["decision"] = \
            "ANNULEE — l'application deplace la surface au-dela de la tolerance"
        bpy.ops.wm.read_factory_settings(use_empty=True)
        with bpy.data.libraries.load(PAQUET, link=False) as (src, dst):
            dst.collections = [COL]
        col = dst.collections[0]
        bpy.context.scene.collection.children.link(col)
        bpy.context.view_layer.update()
        objets = [o for o in col.all_objects if o.type == "MESH"]
    else:
        rapport["application_echelle"]["decision"] = \
            "APPLIQUEE — echelle 1, rotation nulle, surface inchangee"

    rapport["apres"] = {o.name: {"scale": [round(x, 6) for x in o.scale],
                                 "rotation_euler": [round(x, 6) for x in o.rotation_euler],
                                 "location": [round(x, 6) for x in o.location]}
                        for o in objets}
    sig_t, sig_n, detail = signatures(objets)
    rapport["signature_topologie"] = sig_t
    rapport["signature_neutre"] = sig_n
    rapport["objets"] = detail
    rapport["totaux"] = {"objets": len(objets),
                         "sommets": sum(d["sommets"] for d in detail),
                         "faces": sum(d["faces"] for d in detail)}

    os.makedirs(os.path.dirname(sortie_blend) or ".", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(sortie_blend), compress=True)
    rapport["fichier"] = os.path.basename(sortie_blend)
    rapport["octets"] = os.path.getsize(sortie_blend)
    with open(sortie_blend, "rb") as f:
        rapport["sha256_du_blend"] = hashlib.sha256(f.read()).hexdigest()
    json.dump(rapport, open(sortie_verrou, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("BASE_OK", sortie_blend, rapport["totaux"], "ecart echelle", ecart, "mm")
