"""Socle commun des scripts F0 : registre de sondes, preflight de l'asset,
empreintes du verrou.

Une seule implementation de chaque empreinte vit ici. Aucun script ne doit en
redefinir une : deux implementations d'une meme empreinte finissent toujours par
diverger, et c'est alors le verrou qui ment.
"""
import hashlib, json, os, struct, sys, time

# ---------------------------------------------------------------- asset ----

TAILLE_ATTENDUE = 49_420_489
SHA_ATTENDU = "3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137"
BASENAME_ATTENDU = "human_base_meshes_bundle.blend"
PAQUET = "Human Base Meshes bundle v1.4.1"
LICENCE = "CC0"


def sha256_flux(chemin, bloc=1 << 20):
    """SHA-256 lu en flux : un paquet de 47 Mo n'a pas a tenir en memoire."""
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for morceau in iter(lambda: f.read(bloc), b""):
            h.update(morceau)
    return h.hexdigest()


def preflight(chemin=None, taille_attendue=TAILLE_ATTENDUE, sha_attendu=SHA_ATTENDU,
              basename_attendu=BASENAME_ATTENDU):
    """Verifie l'asset AVANT toute ouverture. Rend (rapport, ok).

    Ordre impose : resoudre, exister, taille, SHA en flux, comparer. Rien ne
    doit etre charge tant que ces cinq points ne sont pas passes.
    """
    r = {"size_expected": taille_attendue, "sha256_expected": sha_attendu,
         "paquet": PAQUET, "licence": LICENCE}
    if chemin is None:
        chemin = os.environ.get("ATLAS_BASE_MESH")
    if not chemin:
        r.update(status="ECHEC", raison="ATLAS_BASE_MESH absent")
        return r, False
    r["path_basename"] = os.path.basename(chemin)
    if not os.path.isfile(chemin):
        r.update(status="ECHEC", raison="fichier absent ou non ordinaire")
        return r, False
    r["size_measured"] = os.path.getsize(chemin)
    if r["size_measured"] != taille_attendue:
        r.update(status="ECHEC", raison="taille fausse")
        return r, False
    r["sha256_measured"] = sha256_flux(chemin)
    if r["sha256_measured"] != sha_attendu:
        r.update(status="ECHEC", raison="SHA-256 faux")
        return r, False
    # Le nom seul est tolere s'il differe, PARCE QUE taille et SHA sont exacts.
    r["basename_conforme"] = (r["path_basename"] == basename_attendu)
    r["status"] = "OK"
    return r, True


def exiger_asset(sortie_json=None):
    """A appeler en tete de tout script touchant ATLAS_BASE_MESH.

    Sort en code 2 sans rien produire si l'asset n'est pas le bon.
    """
    chemin = os.environ.get("ATLAS_BASE_MESH")
    r, ok = preflight(chemin)
    print("PREFLIGHT", r.get("status"), r.get("raison", ""))
    if sortie_json:
        os.makedirs(os.path.dirname(sortie_json) or ".", exist_ok=True)
        json.dump(r, open(sortie_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not ok:
        sys.exit(2)
    return chemin, r


# -------------------------------------------------------------- registre ----

class Registre:
    """Registre des sondes. Le compte « reussies / total » se lit ICI.

    Aucun nombre de sondes ne doit etre saisi a la main dans un rapport : il est
    calcule depuis cette liste et recopie par les documents.
    """

    def __init__(self, nom):
        self.nom = nom
        self.entrees = []

    def exige(self, ident, description, configuration, attendu, obtenu, ok,
              tolerance=None, duree=None):
        e = {"id": ident, "description": description,
             "configuration_connue": configuration,
             "expected": attendu, "measured": obtenu,
             "status": "PASS" if ok else "FAIL"}
        if tolerance is not None: e["tolerance"] = tolerance
        if duree is not None: e["duree_s"] = round(duree, 4)
        self.entrees.append(e)
        print("  [%s] %-34s | attendu %s | obtenu %s"
              % (e["status"], ident, attendu, obtenu))
        return ok

    def saute(self, ident, description, raison):
        self.entrees.append({"id": ident, "description": description,
                             "status": "SKIP", "raison": raison})
        print("  [SKIP] %-34s | %s" % (ident, raison))

    @property
    def total(self): return len(self.entrees)

    @property
    def reussies(self): return sum(1 for e in self.entrees if e["status"] == "PASS")

    @property
    def echecs(self): return [e for e in self.entrees if e["status"] == "FAIL"]

    @property
    def sautees(self): return [e for e in self.entrees if e["status"] == "SKIP"]

    def bilan(self):
        return {"registre": self.nom, "total": self.total, "reussies": self.reussies,
                "echecs": len(self.echecs), "sautees": len(self.sautees),
                "sondes": self.entrees}

    def conclure(self):
        print("REGISTRE %s : %d/%d reussies, %d echec(s), %d sautee(s)"
              % (self.nom, self.reussies, self.total, len(self.echecs), len(self.sautees)))
        return not self.echecs


# ------------------------------------------------------------ empreintes ----
# Cinq empreintes SEPAREES : le message d'echec doit nommer la faute.

def _h(): return hashlib.sha256()


def signature_topologie(objets):
    h = _h()
    for o in sorted(objets, key=lambda x: x.name):
        me = o.data
        h.update(o.name.encode()); h.update(b"\x00")
        h.update(me.name.encode()); h.update(b"\x00")
        h.update(struct.pack("<III", len(me.vertices), len(me.edges), len(me.polygons)))
        h.update(struct.pack("<I", len(me.loops)))
        for e in me.edges:
            h.update(struct.pack("<II", *sorted(e.vertices)))
        for p in me.polygons:
            h.update(struct.pack("<I", len(p.vertices)))
            h.update(struct.pack("<%dI" % len(p.vertices), *p.vertices))
            h.update(struct.pack("<I", p.loop_start))
    return h.hexdigest()


def signature_neutre_basis(objets):
    h = _h()
    for o in sorted(objets, key=lambda x: x.name):
        h.update(o.name.encode()); h.update(b"\x00")
        for v in o.data.vertices:
            h.update(struct.pack("<3f", *v.co))
        h.update(struct.pack("<3f", *o.location))
        h.update(struct.pack("<4f", *o.rotation_quaternion))
        h.update(struct.pack("<3f", *o.rotation_euler))
        h.update(o.rotation_mode.encode()); h.update(b"\x00")
        h.update(struct.pack("<3f", *o.scale))
        for ligne in o.matrix_world:
            h.update(struct.pack("<4f", *ligne))
        h.update((o.parent.name if o.parent else "").encode()); h.update(b"\x00")
        if o.parent:
            for ligne in o.matrix_parent_inverse:
                h.update(struct.pack("<4f", *ligne))
    return h.hexdigest()


def signature_uv(objets):
    """Les coordonnees elles-memes, dans l'ordre exact des loops.

    `bool(uv_layers)` ne prouve rien : il dit qu'une couche existe, pas que ses
    coordonnees sont intactes. C'est le reproche exact de l'audit.
    """
    h = _h()
    for o in sorted(objets, key=lambda x: x.name):
        me = o.data
        h.update(o.name.encode()); h.update(b"\x00")
        h.update(struct.pack("<I", len(me.uv_layers)))
        actif = me.uv_layers.active.name if me.uv_layers.active else ""
        h.update(actif.encode()); h.update(b"\x00")
        for couche in me.uv_layers:
            h.update(couche.name.encode()); h.update(b"\x00")
            h.update(struct.pack("<I", len(couche.data)))
            for d in couche.data:
                h.update(struct.pack("<2f", d.uv[0], d.uv[1]))
    return h.hexdigest()


def detail_uv(objets):
    out = {}
    for o in sorted(objets, key=lambda x: x.name):
        me = o.data
        out[o.name] = {
            "couches": [c.name for c in me.uv_layers],
            "active": me.uv_layers.active.name if me.uv_layers.active else None,
            "index_actif": me.uv_layers.active_index if me.uv_layers else None,
            "loops": len(me.loops),
            "donnees_par_couche": [len(c.data) for c in me.uv_layers],
        }
    return out


CLES_MULTIRES = ("levels", "sculpt_levels", "render_levels", "total_levels",
                 "show_viewport", "show_render", "show_in_editmode",
                 "use_custom_normals", "quality", "uv_smooth", "boundary_smooth",
                 "use_creases", "use_sculpt_base_mesh")


def config_objet(o):
    mods = []
    for m in o.modifiers:
        d = {"nom": m.name, "type": m.type, "show_viewport": m.show_viewport,
             "show_render": m.show_render}
        if m.type == "MULTIRES":
            for c in CLES_MULTIRES:
                if hasattr(m, c):
                    v = getattr(m, c)
                    d[c] = v if isinstance(v, (int, float, bool, str)) else str(v)
        mods.append(d)
    return {
        "objet": o.name, "datablock": o.data.name, "type": o.type,
        "sommets": len(o.data.vertices), "aretes": len(o.data.edges),
        "faces": len(o.data.polygons), "loops": len(o.data.loops),
        "shape_keys": (len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0),
        "modificateurs": mods,
        "contraintes": [c.type for c in o.constraints],
        "uv": [c.name for c in o.data.uv_layers],
        "materiaux": [m.name if m else None for m in o.data.materials],
        "vertex_groups": [g.name for g in o.vertex_groups],
        "lock_location": list(o.lock_location),
        "lock_rotation": list(o.lock_rotation),
        "lock_scale": list(o.lock_scale),
        "parent": o.parent.name if o.parent else None,
        "animation": bool(o.animation_data and (o.animation_data.action
                                                or o.animation_data.drivers)),
        "drivers": (len(o.animation_data.drivers) if o.animation_data else 0),
    }


def signature_configuration(objets):
    h = _h()
    for c in sorted((config_objet(o) for o in objets), key=lambda d: d["objet"]):
        h.update(json.dumps(c, sort_keys=True, ensure_ascii=False).encode())
    return h.hexdigest()


def inventaire_scene(bpy):
    return {
        "objets": sorted([{"nom": o.name, "type": o.type,
                           "collections": sorted(c.name for c in o.users_collection)}
                          for o in bpy.data.objects], key=lambda d: d["nom"]),
        "nombre_objets": len(bpy.data.objects),
        "par_type": {t: sum(1 for o in bpy.data.objects if o.type == t)
                     for t in sorted({o.type for o in bpy.data.objects})},
        "collections": sorted(c.name for c in bpy.data.collections),
        "armatures": sorted(a.name for a in bpy.data.armatures),
        "actions": sorted(a.name for a in bpy.data.actions),
        "cameras": sorted(c.name for c in bpy.data.cameras),
        "lumieres": sorted(l.name for l in bpy.data.lights),
        "materiaux": sorted(m.name for m in bpy.data.materials),
        "images": sorted(i.name for i in bpy.data.images if i.name != "Render Result"),
        "textes": sorted(t.name for t in bpy.data.texts),
        "bibliotheques": sorted(l.filepath for l in bpy.data.libraries),
    }


def signature_inventaire_scene(bpy):
    return hashlib.sha256(json.dumps(inventaire_scene(bpy), sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


def toutes_les_empreintes(bpy, objets):
    return {
        "signature_topologie": signature_topologie(objets),
        "signature_neutre_basis": signature_neutre_basis(objets),
        "signature_uv": signature_uv(objets),
        "signature_configuration": signature_configuration(objets),
        "signature_inventaire_scene": signature_inventaire_scene(bpy),
    }


def racine_depot(fichier):
    return os.path.dirname(os.path.dirname(os.path.abspath(fichier)))
