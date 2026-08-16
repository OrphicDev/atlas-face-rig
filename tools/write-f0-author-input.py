"""F0-B.0 — signe l'unique fichier d'auteur dont dependent F0-B a F0-F.

Une seule autorite : `reports/f0-final/author-input.json`. Aucun terminal ne
retape le chemin du blend, il le resout depuis ce JSON. Si la gate F0-B impose
une retopologie, le fichier est regenere avec `--kind retopo` et toute la phase
est rejouee depuis ce nouvel auteur.

Aucun chemin absolu ne sort d'ici : le blend est publie en chemin RELATIF a la
racine du depot.

    blender -b source/FACE_BASE_LOCKED.blend \
      --python tools/write-f0-author-input.py -- \
      --kind c0885_locked --output reports/f0-final/author-input.json
"""
import argparse, hashlib, json, os, struct, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TETE = "GEO-head_animation_realistic"
YEUX = (TETE + ".sclera.L", TETE + ".sclera.R", TETE + ".iris.L", TETE + ".iris.R")


def sha_fichier(chemin, bloc=1 << 20):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for m in iter(lambda: f.read(bloc), b""):
            h.update(m)
    return h.hexdigest()


def sha_topologie(obj):
    """Empreinte de la CONNECTIVITE seule : elle ne bouge pas si un sommet se
    deplace, elle bouge des qu'un sommet est ajoute, retire ou reordonne."""
    h = hashlib.sha256()
    me = obj.data
    h.update(obj.name.encode()); h.update(b"\x00")
    h.update(struct.pack("<III", len(me.vertices), len(me.edges), len(me.polygons)))
    h.update(struct.pack("<I", len(me.loops)))
    for e in me.edges:
        h.update(struct.pack("<II", *sorted(e.vertices)))
    for p in me.polygons:
        h.update(struct.pack("<I", len(p.vertices)))
        h.update(struct.pack("<%dI" % len(p.vertices), *p.vertices))
    return h.hexdigest()


def relatif(chemin):
    r = os.path.relpath(os.path.abspath(chemin), RACINE)
    if r.startswith("..") or os.path.isabs(r):
        raise RuntimeError("chemin hors du depot : refuse (%s)" % r)
    return r.replace(os.sep, "/")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--kind", required=True, choices=("c0885_locked", "retopo"))
    a.add_argument("--output", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])

    blend = bpy.data.filepath
    if not blend:
        print("aucun blend ouvert : lance ce script AVEC le fichier d'auteur")
        sys.exit(2)

    tete = bpy.data.objects.get(TETE)
    if tete is None or tete.type != "MESH":
        print("maillage principal absent :", TETE); sys.exit(2)
    manquants = [n for n in YEUX
                 if bpy.data.objects.get(n) is None
                 or bpy.data.objects[n].type != "MESH"]
    if manquants:
        print("meshes oculaires absents :", manquants); sys.exit(2)

    me = tete.data
    R = {
        "face_author_blend": relatif(blend),
        "kind": o.kind,
        "blend_sha256": sha_fichier(blend),
        "topology_sha256": sha_topologie(tete),
        "objet": TETE,
        "vertices": len(me.vertices),
        "edges": len(me.edges),
        "polygons": len(me.polygons),
        "loops": len(me.loops),
        "uv_layers": [c.name for c in me.uv_layers],
        "meshes_oculaires": list(YEUX),
        "blender": bpy.app.version_string,
        "modificateurs": [{"nom": m.name, "type": m.type,
                           "levels": getattr(m, "levels", None)}
                          for m in tete.modifiers],
        "shape_keys": (len(me.shape_keys.key_blocks) if me.shape_keys else 0),
    }
    sortie = o.output if os.path.isabs(o.output) else os.path.join(RACINE, o.output)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("AUTHOR_INPUT_OK", R["face_author_blend"], R["kind"],
          R["vertices"], "sommets, topo", R["topology_sha256"][:16])
