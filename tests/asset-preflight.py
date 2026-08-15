"""P0.1 — preflight cryptographique de l'asset source.

Rien n'est ouvert, mesure ni sauvegarde tant que la taille ET le SHA-256 du
paquet ne sont pas exacts. Trois auto-tests valident la sonde sans jamais
exposer le vrai asset.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/asset-preflight.py -- \
      "$ATLAS_BASE_MESH" reports/f0-correction/preflight-asset.json
"""
import hashlib, json, os, sys, tempfile
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atlas_commun import Registre, preflight, sha256_flux


def autotests(reg):
    """Trois configurations a reponse connue, sur des fichiers fabriques."""
    d = tempfile.mkdtemp(prefix="atlas-preflight-")
    contenu = b"ATLAS-PREFLIGHT-CONFIGURATION-CONNUE" * 7   # 252 octets
    bon = os.path.join(d, "faux_paquet.blend")
    open(bon, "wb").write(contenu)
    taille = len(contenu)
    sha = hashlib.sha256(contenu).hexdigest()

    # 1. bonne taille, bon SHA -> accepte
    r, ok = preflight(bon, taille, sha, "faux_paquet.blend")
    reg.exige("preflight.fichier_conforme", "taille et SHA exacts",
              "fichier de %d octets, SHA connu" % taille, "OK", r.get("status"), ok)

    # 2. MEME taille, contenu different -> refuse (le SHA seul doit le prendre)
    modifie = bytearray(contenu); modifie[0] ^= 0xFF
    mauvais = os.path.join(d, "modifie.blend")
    open(mauvais, "wb").write(bytes(modifie))
    r2, ok2 = preflight(mauvais, taille, sha, "faux_paquet.blend")
    reg.exige("preflight.meme_taille_contenu_modifie",
              "un octet retourne, taille identique",
              "meme taille, un octet different", "ECHEC / SHA-256 faux",
              "%s / %s" % (r2.get("status"), r2.get("raison")),
              (not ok2) and r2.get("raison") == "SHA-256 faux")

    # 3. bon contenu, taille attendue fausse -> refuse avant meme le SHA
    r3, ok3 = preflight(bon, taille + 1, sha, "faux_paquet.blend")
    reg.exige("preflight.taille_attendue_fausse", "bon contenu, taille attendue fausse",
              "taille attendue decalee de 1", "ECHEC / taille fausse",
              "%s / %s" % (r3.get("status"), r3.get("raison")),
              (not ok3) and r3.get("raison") == "taille fausse")
    reg.exige("preflight.sha_flux_sans_taille_absente", "le SHA en flux ne charge pas tout",
              "fichier de 252 octets", sha[:16], sha256_flux(bon)[:16],
              sha256_flux(bon) == sha)

    # 4. variable / fichier absents
    r4, ok4 = preflight(os.path.join(d, "inexistant.blend"), taille, sha)
    reg.exige("preflight.fichier_absent", "chemin qui n'existe pas",
              "chemin inexistant", "ECHEC", r4.get("status"), not ok4)
    for f in (bon, mauvais): os.remove(f)
    os.rmdir(d)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    chemin = args[0] if args else os.environ.get("ATLAS_BASE_MESH")
    sortie = args[1] if len(args) > 1 else None

    reg = Registre("asset-preflight")
    print("AUTO-TESTS DE LA SONDE")
    autotests(reg)
    if not reg.conclure():
        if sortie:
            os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
            json.dump({"status": "ECHEC", "raison": "auto-tests de la sonde en echec",
                       **reg.bilan()}, open(sortie, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        print("SONDE NON VERIFIEE : l'asset n'est pas examine.")
        sys.exit(2)

    print("PREFLIGHT DE L'ASSET REEL")
    r, ok = preflight(chemin)
    r["registre_de_la_sonde"] = reg.bilan()
    print("  status :", r.get("status"), r.get("raison", ""))
    if sortie:
        os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
        json.dump(r, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("  ->", sortie)
    if not ok:
        sys.exit(2)
    print("PREFLIGHT_OK")
