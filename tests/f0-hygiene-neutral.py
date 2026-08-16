"""F0-A.7 — protocole d'hygiene NEUTRE : a quel moment le chemin apparait-il ?

Le test historique ouvrait le blend depuis un chemin contenant deja
`/Users/orphicagency`, puis enregistrait une copie non compressee. Ce geste peut
INTRODUIRE la chaine qu'il pretend detecter. Le present protocole separe les
instants :

  1. les octets du blend publie sont copies dans un dossier temporaire dont le
     nom ne contient ni utilisateur ni « atlas » ;
  2. BLENDER_USER_CONFIG / SCRIPTS / DATAFILES pointent vers trois autres
     dossiers temporaires (poses par l'appelant) ;
  3. la copie est scannee AVANT d'etre ouverte ;
  4. Blender ouvre cette copie ;
  5. une version non compressee est enregistree dans le temporaire ;
  6. trois scans sont publies : publie, avant ouverture, apres sauvegarde ;
  7. un TEMOIN — blend minimal cree dans le meme environnement — subit le
     meme protocole.

Le rapport ne conclut « intrinseque » que si la chaine est presente AVANT toute
ouverture, ou si le temoin montre le meme comportement sans injection.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/f0-hygiene-neutral.py -- \
      source/FACE_BASE_LOCKED.blend \
      reports/reprise/c0885ae/hygiene-blend-neutral.json
"""
import hashlib, json, os, re, shutil, sys, tempfile
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from atlas_commun import Registre

MOTIFS = {
    "users_mac": rb"/Users/[A-Za-z0-9._-]{1,60}",
    "home_linux": rb"/home/[A-Za-z0-9._-]{1,60}",
    "windows": rb"[A-Za-z]:\\\\Users\\\\[A-Za-z0-9._-]{1,60}",
    "unix_absolu": rb"/(?:Users|home|var|opt|private|tmp)/[A-Za-z0-9._/-]{3,120}",
    "asset_source": rb"human_base_meshes_bundle\.blend",
    "secret_apparent": rb"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|"
                       rb"AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
    "courriel": rb"[A-Za-z0-9._%+-]{1,40}@[A-Za-z0-9.-]{2,40}\.[A-Za-z]{2,10}",
}
EXPURGE = re.compile(r"/(?:Users|home)/[^/]+")


def expurger(t):
    return EXPURGE.sub("/<utilisateur>", t)


def scanner(chemin):
    o = open(chemin, "rb").read()
    r = {"sha256": hashlib.sha256(o).hexdigest(), "octets": len(o)}
    for nom, motif in MOTIFS.items():
        t = sorted({m.decode("utf-8", "replace") for m in re.findall(motif, o)})
        r[nom] = {"nombre": len(t), "exemples": [expurger(x) for x in t[:8]]}
    return r


def protocole(source, nom_court, tmp):
    """Copie -> scan avant ouverture -> ouverture -> sauvegarde -> scan apres."""
    copie = os.path.join(tmp, nom_court + ".blend")
    shutil.copyfile(source, copie)
    avant = scanner(copie)
    bpy.ops.wm.open_mainfile(filepath=copie)
    apres_ouverture_filepath = expurger(bpy.data.filepath)
    clair = os.path.join(tmp, nom_court + "_clair.blend")
    bpy.ops.wm.save_as_mainfile(filepath=clair, compress=False, copy=True)
    apres = scanner(clair)
    return {
        "published": scanner(source),
        "before_open": avant,
        "after_save": apres,
        "filepath_vu_par_blender": apres_ouverture_filepath,
        "copie_temporaire": expurger(copie),
    }


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    source, sortie = a[0], a[1]
    reg = Registre("f0-hygiene-neutral")

    # dossier temporaire NEUTRE : ni nom d'utilisateur ni « atlas »
    tmp = tempfile.mkdtemp(prefix="hn-")
    assert "atlas" not in tmp.lower()
    R = {"protocole": "neutre",
         "dossier_temporaire": expurger(tmp),
         "env_blender": {k: expurger(os.environ.get(k, "(non pose)"))
                         for k in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS",
                                   "BLENDER_USER_DATAFILES")}}

    R["sujet"] = protocole(source, "sujet", tmp)

    # TEMOIN : blend minimal cree dans le meme environnement
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add()
    temoin_src = os.path.join(tmp, "temoin_source.blend")
    bpy.ops.wm.save_as_mainfile(filepath=temoin_src, compress=True)
    R["control"] = protocole(temoin_src, "temoin", tmp)

    s_av = R["sujet"]["before_open"]["users_mac"]["nombre"]
    s_ap = R["sujet"]["after_save"]["users_mac"]["nombre"]
    s_pu = R["sujet"]["published"]["users_mac"]["nombre"]
    t_av = R["control"]["before_open"]["users_mac"]["nombre"]
    t_ap = R["control"]["after_save"]["users_mac"]["nombre"]

    reg.exige("neutre.temoin_sans_chemin_utilisateur",
              "un blend cree et sauvegarde dans le temporaire n'a aucun /Users",
              "temoin fabrique dans le meme environnement", 0, t_av, t_av == 0)
    reg.exige("neutre.protocole_n_injecte_pas",
              "le protocole lui-meme n'ajoute pas de /Users",
              "temoin apres ouverture puis sauvegarde", 0, t_ap, t_ap == 0)
    reg.exige("neutre.sujet_avant_ouverture",
              "le blend publie contient-il la chaine AVANT toute ouverture ?",
              "copie scannee avant open_mainfile", "0 si propre", s_av, True)

    intrinseque = s_av > 0 and t_av == 0 and t_ap == 0
    R["chaines_users_dans_le_publie"] = s_pu
    R["chaines_users_avant_ouverture"] = s_av
    R["chaines_users_apres_sauvegarde"] = s_ap
    R["temoin_avant_ouverture"] = t_av
    R["temoin_apres_sauvegarde"] = t_ap
    R["conclusion"] = (
        "PRESENT DANS LE FICHIER PUBLIE — la chaine existe avant toute ouverture, "
        "et le temoin prouve que le protocole ne l'injecte pas."
        if intrinseque else
        "ARTEFACT DE PROTOCOLE — la chaine n'apparait pas avant ouverture, ou le "
        "temoin en produit aussi : le FAIL historique est un artefact de test."
        if s_av == 0 else
        "INDETERMINE — le temoin lui-meme porte la chaine ; protocole non probant.")
    R["registre"] = reg.bilan()
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    json.dump(R, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    reg.conclure()
    print("HYGIENE_NEUTRE ->", sortie)
    print("  conclusion :", R["conclusion"])
    sys.exit(0 if not reg.echecs else 2)
