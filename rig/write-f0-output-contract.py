"""F0-F.2 — le contrat de sortie de la fondation finale.

Le contrat relie chaque artefact a son SHA-256. F1 et F3 liront `artifacts`
plutot que de reconstruire un chemin implicite. Tous les chemins sont relatifs
au depot : un chemin absolu utilisateur est refuse.

Les comptes anatomiques sont ceux MESURES sur la fondation
(`tests/measure-f0-anatomy-counts.py`), jamais une constante d'avant
retopologie.

    blender -b source/FACE_F0_FOUNDATION_FINAL.blend \
      --python rig/write-f0-output-contract.py -- \
      --output source/FACE_F0_FOUNDATION_FINAL.output-contract.json
"""
import argparse, importlib.util, json, os, subprocess, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
import atlas_commun as AC
from atlas_commun import Registre
_s = importlib.util.spec_from_file_location(
    "wai", os.path.join(RACINE, "tools", "write-f0-author-input.py"))
WAI = importlib.util.module_from_spec(_s); _s.loader.exec_module(WAI)

TETE = "GEO-head_animation_realistic"
ARTEFACTS = {
    "author_input": "reports/f0-final/author-input.json",
    "mirror_map": "reports/f0-final/carte-miroir.json",
    "globe_fit": "config/globe-fit.json",
    "jaw_mask": "config/jaw-mask.json",
    "jaw_motion": "config/jaw-motion.json",
    "anatomy_counts": "reports/f0-final/anatomy-counts.json",
}
DELTAS = {
    "blink_L": "reports/f0-final/deformations/blink_L.cage-delta.json",
    "blink_R": "reports/f0-final/deformations/blink_R.cage-delta.json",
    "mouth_close": "reports/f0-final/deformations/mouth_close.cage-delta.json",
}
DECISIONS = {
    "raccord_corps": "reports/f0-final/DECISION_RACCORD_CORPS.md",
    "ordre_modificateurs": "reports/f0-final/DECISION_MODIFIER_ORDER.md",
}
RESULTATS = {
    "runtime_mesh": "reports/f0-final/runtime-mesh.json",
    "gltf_roundtrip": "experiments/gltf-spike/roundtrip.json",
    "gltf_validation": "reports/f0-final/validation-glb.json",
    "gltf_runtime": "reports/f0-final/runtime-glb.json",
}


def rel(p):
    return os.path.relpath(p, RACINE) if os.path.isabs(p) else p


def entree(chemin, reg=None, cle=None):
    p = os.path.join(RACINE, chemin)
    existe = os.path.isfile(p)
    if reg is not None:
        reg.exige("contrat.artefact." + (cle or os.path.basename(chemin)),
                  "l'artefact existe et se signe", chemin, "present",
                  "present" if existe else "ABSENT", existe)
    if not existe:
        return {"path": chemin, "sha256": None, "absent": True}
    return {"path": chemin, "sha256": WAI.sha_fichier(p)}


def statut_registre(chemin):
    p = os.path.join(RACINE, chemin)
    if not os.path.isfile(p):
        return {"path": chemin, "absent": True}
    try:
        b = json.load(open(p, encoding="utf-8")).get("registre", {})
    except Exception:
        return {"path": chemin, "illisible": True}
    return {"path": chemin, "sha256": WAI.sha_fichier(p),
            "reussies": b.get("reussies"), "total": b.get("total"),
            "echecs": b.get("echecs"), "sautees": b.get("sautees")}


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--output", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    tete = bpy.data.objects[TETE]
    meshes = [x for x in bpy.data.objects if x.type == "MESH"]
    reg = Registre("f0-output-contract")
    try:
        commit = subprocess.run(["git", "-C", RACINE, "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = None

    art = {k: entree(v, reg, k) for k, v in ARTEFACTS.items()}
    delt = {k: entree(v, reg, k) for k, v in DELTAS.items()}
    AN = json.load(open(Rp(ARTEFACTS["anatomy_counts"]), encoding="utf-8"))
    reg.exige("contrat.anatomy_sha", "les comptes portent la topologie du blend",
              ARTEFACTS["anatomy_counts"], WAI.sha_topologie(tete),
              AN.get("topology_sha256"), AN.get("topology_sha256")
              == WAI.sha_topologie(tete))

    mr = [m for m in tete.modifiers if m.type == "MULTIRES"]
    nk = 0 if tete.data.shape_keys is None else len(tete.data.shape_keys.key_blocks)
    n_arm = sum(1 for x in bpy.data.objects if x.type == "ARMATURE")
    reg.exige("contrat.sans_armature", "la fondation ne porte aucune armature",
              "inventaire", 0, n_arm, n_arm == 0)
    reg.exige("contrat.sans_shape_key", "la fondation ne porte aucune shape key",
              TETE, 0, nk, nk == 0)
    reg.exige("contrat.multires", "le Multires est present et non applique",
              "pile de " + TETE, ">= 1", mr[0].levels if mr else 0,
              bool(mr) and mr[0].levels >= 1)

    C = {
        "schema_version": 1,
        "commit_source": commit,
        "blender": bpy.app.version_string,
        "blend": rel(bpy.data.filepath),
        "blend_sha256": WAI.sha_fichier(bpy.data.filepath),
        "espace": "WORLD", "unites": "METERS",
        "inventaire_objets": sorted(x.name for x in bpy.data.objects),
        "empreintes": AC.toutes_les_empreintes(bpy, meshes),
        "objet": TETE,
        "topologie": {
            "sha256": WAI.sha_topologie(tete),
            "vertices": len(tete.data.vertices),
            "edges": len(tete.data.edges),
            "polygons": len(tete.data.polygons),
            "loops": len(tete.data.loops)},

        "configuration_modificateurs": {
            "pile": [{"nom": m.name, "type": m.type,
                      "levels": getattr(m, "levels", None)}
                     for m in tete.modifiers]},
        "multires_level": mr[0].levels if mr else None,
        "sans_armature": n_arm == 0,
        "sans_shape_key_permanente": nk == 0,
        "artifacts": art,
        "deltas": delt,
        "decisions": {k: entree(v, reg, k) for k, v in DECISIONS.items()},
        "resultats": {k: statut_registre(v) for k, v in RESULTATS.items()},
        "anatomy_counts": {k: AN[k] for k in
                           ("boucles_palpebrales", "boucles_labiales",
                            "triangles_region_bouche", "sommets_bord_narine",
                            "rayon_mm", "definitions") if k in AN},
    }
    absolus = [k for k, v in list(art.items()) + list(delt.items())
               if os.path.isabs(v["path"])]
    reg.exige("contrat.chemins_relatifs", "aucun chemin absolu utilisateur",
              "tous les artefacts", [], absolus, not absolus)
    C["registre"] = reg.bilan()

    p = Rp(o.output); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    json.dump(C, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure()
    print("CONTRAT", "OK" if ok else "ECHEC", "->", o.output)
    sys.exit(0 if ok else 2)
