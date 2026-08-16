"""Planche de contact : plusieurs rendus dans une seule image, lisible au telephone."""
import argparse, os, sys
import bpy

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger(chemin, cote):
    im = bpy.data.images.load(chemin)
    im.scale(cote, cote)
    px = list(im.pixels)
    bpy.data.images.remove(im)
    return px


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--sortie", required=True)
    a.add_argument("--colonnes", type=int, default=2)
    a.add_argument("--cote", type=int, default=520)
    a.add_argument("--images", nargs="+", required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)

    cols = o.colonnes
    lignes = (len(o.images) + cols - 1) // cols
    C = o.cote
    marge = 6
    W = cols * C + (cols + 1) * marge
    H = lignes * C + (lignes + 1) * marge
    fond = [0.06, 0.06, 0.08, 1.0]
    buf = fond * (W * H)

    for k, rel in enumerate(o.images):
        px = charger(os.path.abspath(Rp(rel)), C)
        cx = k % cols
        cy = lignes - 1 - (k // cols)          # Blender compte du bas vers le haut
        ox = marge + cx * (C + marge)
        oy = marge + cy * (C + marge)
        for y in range(C):
            src = y * C * 4
            dst = ((oy + y) * W + ox) * 4
            buf[dst:dst + C * 4] = px[src:src + C * 4]

    im = bpy.data.images.new("planche", width=W, height=H, alpha=False)
    im.pixels = buf
    p = Rp(o.sortie)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    im.filepath_raw = p
    im.file_format = "PNG"
    im.save()
    print("PLANCHE", W, "x", H, "->", o.sortie)
