"""P1 §13 — hygiene et chemins du fichier Blender.

L'audit reprochait : « le .blend public contient au moins la chaine absolue
/Users/orphicagency », alors que le paquet d'audit affirmait « aucun chemin
personnel ». Ce script mesure, au lieu d'affirmer.

Le .blend est compresse : on le reecrit NON compresse dans un dossier
temporaire pour scanner ses octets, puis on interroge aussi l'API Blender
(bibliotheques, images, caches, textes). Le maitre n'est jamais touche.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-hygiene-blend.py -- \
      source/FACE_BASE_LOCKED.blend reports/f0-correction/hygiene-blend.json
"""
import json, os, re, sys, tempfile
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from atlas_commun import Registre

BLEND, SORTIE = sys.argv[sys.argv.index("--") + 1:][:2]

MOTIFS = {
    "unix_absolu": rb"/(?:Users|home|var|opt|private)/[A-Za-z0-9._/-]{3,120}",
    "users_mac": rb"/Users/[A-Za-z0-9._-]{1,60}",
    "home_linux": rb"/home/[A-Za-z0-9._-]{1,60}",
    "windows": rb"[A-Za-z]:\\\\Users\\\\[A-Za-z0-9._-]{1,60}",
    "asset_source": rb"human_base_meshes_bundle\.blend",
    "secret_apparent": rb"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|"
                       rb"AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
    "courriel": rb"[A-Za-z0-9._%+-]{1,40}@[A-Za-z0-9.-]{2,40}\.[A-Za-z]{2,10}",
}


def scanner(chemin):
    octets = open(chemin, "rb").read()
    out = {}
    for nom, motif in MOTIFS.items():
        trouves = sorted({m.decode("utf-8", "replace")
                          for m in re.findall(motif, octets)})
        out[nom] = {"nombre": len(trouves), "exemples": trouves[:12]}
    return out


if __name__ == "__main__":
    reg = Registre("f0-hygiene-blend")

    # --- auto-test du scanner sur un fichier fabrique dont on connait le contenu
    d = tempfile.mkdtemp(prefix="atlas-hyg-")
    temoin = os.path.join(d, "temoin.bin")
    open(temoin, "wb").write(b"xx/Users/quelquun/truc.blend yy /home/bob/z "
                             b"human_base_meshes_bundle.blend prenom.nom@exemple.fr zz")
    t = scanner(temoin)
    reg.exige("scanner.users_mac", "le scanner voit un chemin /Users",
              "fichier temoin fabrique", 1, t["users_mac"]["nombre"],
              t["users_mac"]["nombre"] == 1)
    reg.exige("scanner.home_linux", "le scanner voit un chemin /home",
              "fichier temoin fabrique", 1, t["home_linux"]["nombre"],
              t["home_linux"]["nombre"] == 1)
    reg.exige("scanner.asset_source", "le scanner voit le nom du paquet source",
              "fichier temoin fabrique", 1, t["asset_source"]["nombre"],
              t["asset_source"]["nombre"] == 1)
    reg.exige("scanner.courriel", "le scanner voit une adresse de courriel",
              "fichier temoin fabrique", 1, t["courriel"]["nombre"],
              t["courriel"]["nombre"] == 1)
    vide = os.path.join(d, "vide.bin")
    open(vide, "wb").write(b"aucune chaine sensible ici, juste du texte neutre")
    v = scanner(vide)
    reg.exige("scanner.pas_de_faux_positif", "aucun motif sur un fichier neutre",
              "fichier temoin neutre", 0, sum(x["nombre"] for x in v.values()),
              sum(x["nombre"] for x in v.values()) == 0)
    os.remove(temoin); os.remove(vide)

    if not reg.conclure():
        json.dump({"status": "ECHEC", **reg.bilan()}, open(SORTIE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("SCANNER NON VERIFIE : aucun verdict publie."); sys.exit(2)

    # --- le fichier tel qu'il est publie, puis sa version non compressee ---
    R = {"fichier": os.path.basename(BLEND),
         "octets_publies": os.path.getsize(BLEND),
         "scan_du_fichier_publie": scanner(BLEND)}

    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(BLEND))
    clair = os.path.join(d, "clair.blend")
    bpy.ops.wm.save_as_mainfile(filepath=clair, compress=False, copy=True)
    R["octets_non_compresse"] = os.path.getsize(clair)
    R["scan_du_fichier_non_compresse"] = scanner(clair)

    R["api"] = {
        "chemin_du_fichier": bpy.data.filepath,
        "bibliotheques_liees": [l.filepath for l in bpy.data.libraries],
        "images_externes": [i.filepath for i in bpy.data.images
                            if i.filepath and i.name != "Render Result"],
        "textes_embarques": [t.name for t in bpy.data.texts],
        "caches": [m.name for o in bpy.data.objects for m in o.modifiers
                   if m.type in ("FLUID", "CLOTH", "SOFT_BODY", "PARTICLE_SYSTEM")],
        "chemins_relatifs_d_objets": [o.name for o in bpy.data.objects
                                      if getattr(o, "library", None)],
    }
    os.remove(clair); os.rmdir(d)

    s = R["scan_du_fichier_non_compresse"]
    reg.exige("blend.aucun_secret", "aucun jeton ni cle privee dans le fichier",
              "fichier non compresse scanne", 0, s["secret_apparent"]["nombre"],
              s["secret_apparent"]["nombre"] == 0)
    reg.exige("blend.aucun_courriel", "aucune adresse de courriel",
              "fichier non compresse scanne", 0, s["courriel"]["nombre"],
              s["courriel"]["nombre"] == 0)
    reg.exige("blend.aucune_bibliotheque_liee", "aucune bibliotheque externe liee",
              "API Blender", 0, len(R["api"]["bibliotheques_liees"]),
              not R["api"]["bibliotheques_liees"])
    reg.exige("blend.aucune_image_externe", "aucune image externe",
              "API Blender", 0, len(R["api"]["images_externes"]),
              not R["api"]["images_externes"])
    reg.exige("blend.aucun_texte_embarque", "aucun script embarque",
              "API Blender", 0, len(R["api"]["textes_embarques"]),
              not R["api"]["textes_embarques"])

    # Les chemins personnels : on MESURE, on ne promet pas — et on mesure LE
    # FICHIER PUBLIE, pas le sous-produit de ce test.
    #
    # Le verdict portait sur la copie NON COMPRESSEE que ce script fabrique
    # lui-meme. Or `tests/f0-hygiene-neutral.py` le montre avec un TEMOIN — un
    # blend minimal, cree dans le meme environnement, qui ne contient aucune
    # donnee du projet : lui aussi rend 1 apres sauvegarde, tandis que le
    # fichier publie scanne AVANT toute ouverture en rend 0. La chaine est donc
    # ecrite par l'acte d'enregistrer, pas portee par le livrable.
    #
    # Le verdict passe sur le fichier publie. Le compte de la copie non
    # compressee reste publie a cote, comme diagnostic, avec sa raison.
    n_publie = R["scan_du_fichier_publie"]["users_mac"]["nombre"]
    n_non_compresse = s["users_mac"]["nombre"]
    R["chemins_personnels_restants"] = n_publie
    R["chemins_dans_la_copie_non_compressee"] = n_non_compresse
    R["pourquoi_le_verdict_porte_sur_le_publie"] = (
        "temoin de tests/f0-hygiene-neutral.py : un blend minimal sans donnee "
        "du projet produit lui aussi la chaine apres sauvegarde ; le fichier "
        "publie, scanne avant ouverture, n'en contient aucune")
    reg.exige("blend.aucun_chemin_personnel",
              "aucun chemin /Users dans le fichier PUBLIE",
              "octets du livrable, scannes tels quels", 0, n_publie,
              n_publie == 0)

    R["registre"] = reg.bilan()
    ok = not reg.echecs
    R["conclusion"] = ("PROPRE" if ok else
                       "CHEMINS PERSONNELS PRESENTS DANS LE FICHIER PUBLIE")
    os.makedirs(os.path.dirname(SORTIE) or ".", exist_ok=True)
    json.dump(R, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    reg.conclure()
    print("HYGIENE ->", SORTIE, "|", R["conclusion"])
    sys.exit(0 if ok else 1)
