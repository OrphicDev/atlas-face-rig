"""Contre-epreuve du verrou : neuf mutations qui DOIVENT toutes etre refusees.

Un verrou qui n'a jamais echoue n'est pas un verrou, c'est une decoration. Ce
script casse la base de neuf facons differentes, en memoire uniquement, et
verifie a chaque fois que le verrou refuse ET qu'il nomme la bonne empreinte.

Le maitre est rouvert avant chaque mutation et n'est JAMAIS sauvegarde.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/verrou-topologie-negatif.py -- \
      source/FACE_BASE_LOCKED.blend tests/verrou-topologie.json \
      reports/f0-correction/verrou-negatif.json
"""
import hashlib, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh, importlib.util
# Le verrou vit dans un fichier a tirets : on le charge par chemin plutot que
# d'en redupliquer la logique. Une seule implementation du controle, sinon
# c'est la contre-epreuve qui ment.
_ici = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("verrou", os.path.join(_ici, "verrou-topologie.py"))
_verrou = importlib.util.module_from_spec(_s); _s.loader.exec_module(_verrou)
controler_scene = _verrou.controler_scene


def tete():
    return max((o for o in bpy.data.objects if o.type == "MESH"),
               key=lambda o: len(o.data.vertices))


# ------------------------------------------------------------ mutations ----

def m_sommet_basis(_):
    o = tete(); o.data.vertices[0].co.z += 0.001
    o.data.update()


def m_topologie(_):
    o = tete()
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.new((0.0, 0.0, 0.0))
    bm.to_mesh(o.data); bm.free(); o.data.update()


def m_objet_deplace(_):
    o = tete(); o.location.x += 0.001


def m_uv(_):
    o = tete(); o.data.uv_layers.active.data[0].uv[0] += 0.01


def m_shape_key(_):
    o = tete()
    o.shape_key_add(name="Basis", from_mix=False)
    o.shape_key_add(name="TEST_INTERDITE", from_mix=False)


def m_armature(_):
    a = bpy.data.armatures.new("TEST_ARM")
    bpy.context.scene.collection.objects.link(bpy.data.objects.new("TEST_ARM", a))


def m_multires(_):
    for m in tete().modifiers:
        if m.type == "MULTIRES":
            m.levels = 0
            return
    raise RuntimeError("aucun multires a muter")


def m_deverrouiller(_):
    tete().lock_location = (False, True, True)


def m_mesh_etranger(_):
    me = bpy.data.meshes.new("TEST_INTRUS")
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=0.01)
    bm.to_mesh(me); bm.free()
    bpy.context.scene.collection.objects.link(bpy.data.objects.new("TEST_INTRUS", me))


MUTATIONS = [
    ("sommet_basis_1mm", "un sommet Basis deplace de 1 mm", "neutre_basis", m_sommet_basis),
    ("topologie_sommet_ajoute", "un sommet ajoute au maillage", "topologie", m_topologie),
    ("objet_deplace_1mm", "un objet deplace de 1 mm", "neutre_basis", m_objet_deplace),
    ("uv_decalee_0_01", "une coordonnee UV decalee de 0,01", "uv", m_uv),
    ("shape_key_ajoutee", "une shape key TEST_INTERDITE", "configuration", m_shape_key),
    ("armature_ajoutee", "un objet Armature ajoute", "inventaire_scene", m_armature),
    ("multires_levels_change", "Multires.levels passe a 0", "configuration", m_multires),
    ("axe_deverrouille", "lock_location.x remis a False", "configuration", m_deverrouiller),
    ("mesh_etranger_ajoute", "un mesh etranger ajoute", "inventaire_scene", m_mesh_etranger),
]


if __name__ == "__main__":
    blend, verrou, sortie = sys.argv[sys.argv.index("--") + 1:][:3]
    attendu = json.load(open(verrou, encoding="utf-8"))
    with open(blend, "rb") as f:
        sha_avant = hashlib.sha256(f.read()).hexdigest()

    print("CONTRE-EPREUVE DU VERROU")
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))
    pannes, fautives, _ = controler_scene(attendu, verbeux=False)
    original_ok = not pannes
    print("  original accepte :", original_ok, pannes[:3] if pannes else "")

    resultats, tout_detecte = [], True
    for nom, description, empreinte_attendue, muter in MUTATIONS:
        bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))   # maitre intact
        muter(None)
        p, f, _ = controler_scene(attendu, verbeux=False)
        refuse = bool(p)
        bonne = empreinte_attendue in f
        ok = refuse and bonne
        tout_detecte &= ok
        resultats.append({"nom": nom, "description": description,
                          "verrou_a_refuse": refuse,
                          "empreinte": empreinte_attendue,
                          "empreintes_fautives": f,
                          "empreinte_attendue_presente": bonne,
                          "premiere_panne": p[0] if p else None})
        print("  [%s] %-24s refuse=%s | attendue '%s' dans %s"
              % ("PASS" if ok else "FAIL", nom, refuse, empreinte_attendue, f))

    with open(blend, "rb") as f:
        sha_apres = hashlib.sha256(f.read()).hexdigest()
    intact = sha_avant == sha_apres

    R = {"original_accepté": original_ok, "mutations": resultats,
         "toutes_les_mutations_detectees": tout_detecte,
         "nombre_de_mutations": len(MUTATIONS),
         "maitre_non_modifie": intact,
         "sha256_du_blend_avant": sha_avant, "sha256_du_blend_apres": sha_apres}
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("  maitre non modifie :", intact)
    print("NEGATIF %s -> %s" % ("OK" if (original_ok and tout_detecte and intact)
                                else "ECHEC", sortie))
    sys.exit(0 if (original_ok and tout_detecte and intact) else 2)
