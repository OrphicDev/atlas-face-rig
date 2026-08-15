"""Verrou de la base F0 — CINQ empreintes separees, pour que l'echec nomme la faute.

Ce que l'audit reprochait a la version precedente : elle ne comparait ni les
shape keys, ni les modificateurs, ni les UV, ni les objets non maillés, ni les
verrous d'axes. Une armature ou une shape key pouvait donc etre ajoutee sans
que le verrou bronche. Ce n'est plus le cas.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/verrou-topologie.py -- \
      source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json
"""
import json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from atlas_commun import (config_objet, detail_uv, inventaire_scene,
                          toutes_les_empreintes)

EMPREINTES = ("signature_topologie", "signature_neutre_basis", "signature_uv",
              "signature_configuration", "signature_inventaire_scene")


def controler(blend, attendu, verbeux=True):
    """Ouvre le fichier puis controle. Rend (pannes, empreintes_fautives, empreintes)."""
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))
    return controler_scene(attendu, verbeux, os.path.basename(blend))


def controler_scene(attendu, verbeux=True, etiquette="scene en memoire"):
    """Controle la scene DEJA ouverte : c'est ce que les contre-epreuves mutent.

    Rend (pannes, empreintes_fautives, empreintes). Liste vide = conforme.
    """
    objets = [o for o in bpy.data.objects if o.type == "MESH"]
    obtenu = toutes_les_empreintes(bpy, objets)

    pannes, fautives = [], []
    for k in EMPREINTES:
        if obtenu[k] != attendu.get(k):
            fautives.append(k.replace("signature_", ""))
            pannes.append("%s : %s attendu, %s obtenu"
                          % (k, str(attendu.get(k))[:16], obtenu[k][:16]))

    # Detail lisible : l'empreinte dit QUE ca a bouge, le detail dit OU.
    a = {d["objet"]: d for d in attendu.get("objets", [])}
    b = {d["objet"]: d for d in sorted((config_objet(o) for o in objets),
                                       key=lambda d: d["objet"])}
    if set(a) != set(b):
        pannes.append("liste d'objets : %s attendu, %s obtenu" % (sorted(a), sorted(b)))
    for nom in sorted(set(a) & set(b)):
        for cle in ("sommets", "aretes", "faces", "loops", "shape_keys",
                    "modificateurs", "contraintes", "uv", "vertex_groups",
                    "lock_location", "lock_rotation", "lock_scale", "parent",
                    "animation", "drivers", "datablock"):
            if a[nom].get(cle) != b[nom].get(cle):
                pannes.append("%s.%s : %s attendu, %s obtenu"
                              % (nom, cle, a[nom].get(cle), b[nom].get(cle)))

    # Regles absolues, verifiees meme si les empreintes coincident.
    for o in objets:
        if o.data.shape_keys:
            pannes.append("%s porte %d shape key(s) : la source F0 doit etre vierge"
                          % (o.name, len(o.data.shape_keys.key_blocks)))
            fautives.append("configuration")
        if any(m.type == "ARMATURE" for m in o.modifiers):
            pannes.append("%s porte un modificateur Armature" % o.name)
            fautives.append("configuration")
        if not (all(o.lock_location) and all(o.lock_rotation) and all(o.lock_scale)):
            pannes.append("%s : axes non verrouilles (%s %s %s)"
                          % (o.name, list(o.lock_location), list(o.lock_rotation),
                             list(o.lock_scale)))
            fautives.append("configuration")
    if bpy.data.armatures:
        pannes.append("armature(s) dans le fichier : %s"
                      % sorted(a.name for a in bpy.data.armatures))
        fautives.append("inventaire_scene")
    etrangers = [o.name for o in bpy.data.objects if o.type != "MESH"]
    if etrangers:
        pannes.append("objets non maillés dans la source : %s" % etrangers)
        fautives.append("inventaire_scene")

    if verbeux:
        print("VERROU sur", etiquette)
        for k in EMPREINTES:
            print("  %-28s %s" % (k.replace("signature_", ""),
                                  "OK" if obtenu[k] == attendu.get(k) else "ECHEC"))
        print("  %d objet(s), %d sommets, %d faces"
              % (len(objets), sum(len(o.data.vertices) for o in objets),
                 sum(len(o.data.polygons) for o in objets)))
    return pannes, sorted(set(fautives)), obtenu


if __name__ == "__main__":
    blend, verrou = sys.argv[sys.argv.index("--") + 1:][:2]
    attendu = json.load(open(verrou, encoding="utf-8"))
    pannes, fautives, _ = controler(blend, attendu)
    if pannes:
        for p in pannes: print("  !", p)
        print("VERROU_ECHEC empreintes fautives :", fautives)
        sys.exit(1)
    print("VERROU_OK")
