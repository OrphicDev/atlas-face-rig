"""Rendus neutres de reference, eclairage du cahier : clay neutre, key rasante,
fill faible, exposition verrouillee. Le rendu doit reveler les defauts.

Publie aussi l'histogramme de chaque image : un rendu qui ecrete ne montre rien.

    blender --background --factory-startup --python-exit-code 1 \
      --python tests/rendus-neutre.py -- source/FACE_BASE_LOCKED.blend renders/f0
"""
import json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector

blend, sortie = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(sortie, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 1600
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "Standard"   # exposition verrouillee, pas de tone map
sc.view_settings.exposure = 0.0
sc.view_settings.look = "None"
sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.055, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

clay = bpy.data.materials.new("CLAY_NEUTRE")
clay.use_nodes = True
b = clay.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.42, 0.42, 0.42, 1)
b.inputs["Roughness"].default_value = 0.55
if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = 0.35
mailles = [o for o in bpy.data.objects if o.type == "MESH"]
# L'asset est livre en ombrage PLAT : rendu tel quel, la facette masque la
# forme. On lisse pour le rendu de reference — et on l'ecrit, car c'est une
# difference avec le fichier verrouille, pas une propriete de l'asset.
LISSAGE = sum(1 for o in mailles for p in o.data.polygons if not p.use_smooth)
for o in mailles:
    o.data.materials.clear(); o.data.materials.append(clay)
    for p in o.data.polygons: p.use_smooth = True

tete = max(mailles, key=lambda o: len(o.data.vertices))
co = [tete.matrix_world @ v.co for v in tete.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
C = (mn + mx) / 2
H = mx.z - mn.z
TETE = Vector((C.x, C.y - 0.005, mn.z + H * 0.69))   # centre MESURE de la tete, pas du buste

def lampe(nom, pos, energie, taille):
    d = bpy.data.lights.new(nom, "AREA"); d.energy = energie; d.size = taille
    o = bpy.data.objects.new(nom, d); o.location = pos
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (TETE - Vector(pos)).normalized().to_track_quat("-Z", "Y")
    sc.collection.objects.link(o); return o

# Rapports d'eclairage fixes (key rasante forte, fill faible, contre-jour
# discret) ; l'intensite absolue est CALIBREE plus bas, pas devinee.
LAMPES = [
    lampe("KEY",  (C.x + 0.62, C.y - 0.30, TETE.z + 0.16), 1.00, 0.22),
    lampe("FILL", (C.x - 0.75, C.y - 0.55, TETE.z - 0.02), 0.13, 0.75),
    lampe("RIM",  (C.x - 0.25, C.y + 0.85, TETE.z + 0.30), 0.25, 0.40),
]
RATIOS = [l.data.energy for l in LAMPES]

cd = bpy.data.cameras.new("CAM"); cd.type = "ORTHO"
cam = bpy.data.objects.new("CAM", cd); sc.collection.objects.link(cam); sc.camera = cam

def histo(chemin):
    im = bpy.data.images.load(chemin)
    px = list(im.pixels)
    lum = [(px[i] * 0.2126 + px[i + 1] * 0.7152 + px[i + 2] * 0.0722)
           for i in range(0, len(px), 4)]
    n = len(lum)
    h = [0] * 16
    for x in lum: h[min(15, max(0, int(x * 16)))] += 1
    r = {"noirs_bouches_pct": round(100.0 * sum(1 for x in lum if x <= 0.002) / n, 3),
         "blancs_brules_pct": round(100.0 * sum(1 for x in lum if x >= 0.998) / n, 3),
         "moyenne": round(sum(lum) / n, 4), "histogramme_16": h}
    bpy.data.images.remove(im)
    return r

def vue(nom, direction, ortho, cible):
    d = Vector(direction).normalized()
    cam.location = cible + d * 1.5
    cd.ortho_scale = ortho
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
    f = os.path.join(sortie, nom + ".png")
    sc.render.filepath = f
    bpy.ops.render.render(write_still=True)
    return histo(f)

VUES = [
    ("neutre_face",        (0, -1, 0),        H * 0.66, TETE),
    ("neutre_profil_L",    (1, 0, 0),         H * 0.66, TETE),
    ("neutre_profil_R",    (-1, 0, 0),        H * 0.66, TETE),
    ("neutre_trq_L",       (0.72, -0.70, 0.12), H * 0.66, TETE),
    ("neutre_trq_R",       (-0.72, -0.70, 0.12), H * 0.66, TETE),
    ("neutre_plongee",     (0, -0.75, 0.66),  H * 0.66, TETE),
    ("neutre_contreplongee", (0, -0.75, -0.62), H * 0.66, TETE),
    ("gros_plan_oeil_L",   (0.38, -1, 0.12),  0.055, Vector((C.x + 0.0343, mn.y + 0.015, 0.7653))),
    ("gros_plan_bouche",   (0.10, -1, -0.12), 0.075, Vector((C.x, mn.y + 0.01, 0.6942))),
    ("gros_plan_nez",      (0.20, -1, -0.35), 0.070, Vector((C.x, mn.y + 0.005, 0.7250))),
]
# --- calibrage de l'exposition, puis verrouillage ---
# On cherche l'intensite qui place le 99,5e centile de la vue de face juste
# sous la saturation. Les rapports entre les trois lampes ne bougent pas.
def centile(chemin, q):
    im = bpy.data.images.load(chemin); px = list(im.pixels)
    lum = sorted(px[i] * 0.2126 + px[i + 1] * 0.7152 + px[i + 2] * 0.0722
                 for i in range(0, len(px), 4))
    bpy.data.images.remove(im)
    return lum[int(len(lum) * q)]

sc.render.resolution_x = sc.render.resolution_y = 400
CIBLE, k = 0.92, 4.0
journal = []
for essai in range(9):
    for l, r in zip(LAMPES, RATIOS): l.data.energy = r * k
    vue("_calibrage", (0, -1, 0), H * 0.66, TETE)
    c = centile(os.path.join(sortie, "_calibrage.png"), 0.995)
    journal.append({"essai": essai, "facteur": round(k, 5), "centile_99_5": round(c, 4)})
    if abs(c - CIBLE) < 0.02 or c <= 1e-4: break
    k *= (CIBLE / max(c, 1e-3)) ** 0.8
for l, r in zip(LAMPES, RATIOS): l.data.energy = r * k
os.remove(os.path.join(sortie, "_calibrage.png"))
sc.render.resolution_x = sc.render.resolution_y = 1600
print("CALIBRAGE facteur %.4f apres %d essais" % (k, len(journal)))

R = {"calibrage": {"cible_centile_99_5": CIBLE, "facteur_retenu": round(k, 5),
                   "journal": journal,
                   "energies_W": {l.name: round(l.data.energy, 4) for l in LAMPES}},
     "fichier": os.path.basename(blend), "blender": bpy.app.version_string,
     "moteur": sc.render.engine, "transformation_de_vue": sc.view_settings.view_transform,
     "faces_lissees_pour_le_rendu": LISSAGE,
     "resolution": [sc.render.resolution_x, sc.render.resolution_y], "vues": {}}
for nom, d, o, c in VUES:
    R["vues"][nom] = vue(nom, d, o, c)
    print("VUE", nom, R["vues"][nom]["noirs_bouches_pct"], "% noirs,",
          R["vues"][nom]["blancs_brules_pct"], "% brules")
json.dump(R, open(os.path.join(sortie, "histogrammes.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
ecretage = [k for k, v in R["vues"].items() if v["blancs_brules_pct"] > 1.0]
print("RENDUS_OK ; vues avec ecretage notable :", ecretage or "aucune")
