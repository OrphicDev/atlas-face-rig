"""Deformations anatomiques jetables : clignement, fermeture labiale, mandibule.

Ce sont des PROTOTYPES. Rien ici ne survit dans la source autoritaire. Leur
seul role est de repondre a la question que le bourrelet cosinus du banc V1 ne
pouvait pas trancher : la topologie tient-elle un vrai pli ?

Chaque deformation est une fonction de la POSITION MONDE, donc applicable a la
cage de 3 242 sommets comme au maillage evalue de 12 950 : les deux voies
recoivent exactement le meme geste.
"""
import math
from mathutils import Vector

MM = 1000.0


def lisse(t):
    """Rampe C1 sur [0,1] : pas de cassure aux bords de la zone d'influence."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


# ------------------------------------------------------- clignement ----

class Clignement:
    """Rotation des paupieres AUTOUR du globe, pas une translation verticale.

    - la paupiere superieure fournit 75 % du trajet, l'inferieure 25 % ;
    - le poids s'annule aux deux canthus, qui restent donc stables ;
    - apres rotation, chaque sommet est repousse hors de la sphere oculaire :
      c'est ce qui garantit qu'aucun sommet ne penetre le globe.
    """

    PART_SUP, PART_INF = 0.75, 0.25

    def __init__(self, centre_globe, rayon_globe, axe_lateral, epaisseur=0.0006,
                 portee=0.0055):
        self.C = Vector(centre_globe)
        self.R = float(rayon_globe)
        self.lat = Vector(axe_lateral).normalized()
        self.epaisseur = epaisseur      # peau au-dessus du globe
        self.portee = portee            # au-dela, ce n'est plus la paupiere

    def concerne(self, p):
        return (Vector(p) - self.C).length <= self.R + self.portee

    def parametres(self, p):
        """(hauteur signee sur le globe, ecart lateral normalise)."""
        d = Vector(p) - self.C
        lateral = d.dot(self.lat)
        radial = d - self.lat * lateral
        # angle depuis le plan horizontal du globe, dans le plan sagittal local
        h = radial.z
        return h, lateral

    def demi_ouverture(self, sommets):
        """Demi-hauteur angulaire de la fente, mesuree et non supposee."""
        hs = [self.parametres(p)[0] for p in sommets if self.concerne(p)]
        return (max(hs) - min(hs)) / 2.0 if hs else 0.0

    def preparer(self, sommets):
        conc = [p for p in sommets if self.concerne(p)]
        self.h_max = max(self.parametres(p)[0] for p in conc)
        self.h_min = min(self.parametres(p)[0] for p in conc)
        lat = [abs(self.parametres(p)[1]) for p in conc]
        self.lat_max = max(lat) if lat else 1.0
        # la ligne de rencontre : au tiers inferieur, comme un oeil reel
        self.h_contact = self.h_min + 0.36 * (self.h_max - self.h_min)

    def deplacer(self, p, intensite):
        p = Vector(p)
        if not self.concerne(p):
            return Vector((0, 0, 0))
        h, lateral = self.parametres(p)
        # poids : 1 au milieu de la paupiere, 0 aux canthus et 0 hors de la fente
        w_lat = 1.0 - lisse(abs(lateral) / max(self.lat_max, 1e-9))
        if h >= self.h_contact:
            course = (h - self.h_contact) * self.PART_SUP / max(self.PART_SUP, 1e-9)
            part = self.PART_SUP
            w_h = lisse((h - self.h_contact) / max(self.h_max - self.h_contact, 1e-9))
            cible_h = self.h_contact + (h - self.h_contact) * (1.0 - self.PART_SUP)
        else:
            part = self.PART_INF
            w_h = lisse((self.h_contact - h) / max(self.h_contact - self.h_min, 1e-9))
            cible_h = self.h_contact - (self.h_contact - h) * (1.0 - self.PART_INF)
        w = w_lat * w_h * intensite
        if w <= 0.0:
            return Vector((0, 0, 0))
        h_vise = h + (cible_h - h) * w
        # on tourne AUTOUR du centre du globe : le rayon est conserve
        d = p - self.C
        lat_comp = self.lat * d.dot(self.lat)
        radial = d - lat_comp
        r = radial.length
        if r < 1e-9:
            return Vector((0, 0, 0))
        # angle actuel et angle vise dans le plan radial
        a = math.asin(max(-1.0, min(1.0, h / r)))
        a2 = math.asin(max(-1.0, min(1.0, max(-r, min(r, h_vise)) / r)))
        avant = radial.normalized()
        # base du plan radial : direction "horizontale" et Z
        horiz = Vector((avant.x, avant.y, 0.0))
        if horiz.length < 1e-9:
            return Vector((0, 0, 0))
        horiz.normalize()
        signe = 1.0 if avant.dot(horiz) >= 0 else -1.0
        nouveau = (horiz * (math.cos(a2) * signe) + Vector((0, 0, math.sin(a2)))) * r
        q = self.C + lat_comp + nouveau
        # jamais dans le globe : on repousse a R + epaisseur
        dd = q - self.C
        if dd.length < self.R + self.epaisseur:
            q = self.C + dd.normalized() * (self.R + self.epaisseur)
        return q - p


# -------------------------------------------------- fermeture labiale ----

class FermetureLabiale:
    """Les levres se rencontrent sur une ligne de contact, sans translation globale.

    - la levre superieure descend, l'inferieure monte, vers une ligne de contact
      mesuree au milieu de la fente ;
    - les commissures ne bougent pas ;
    - la decroissance vers le philtrum et le menton est douce, de sorte que le
      volume de chaque levre reste distinct.
    """

    def __init__(self, centre_fente, demi_largeur, z_contact, portee=0.011):
        self.C = Vector(centre_fente)
        self.demi = float(demi_largeur)
        self.z_contact = float(z_contact)
        self.portee = portee

    def concerne(self, p):
        p = Vector(p)
        return (abs(p.x - self.C.x) <= self.demi * 1.02
                and abs(p.z - self.z_contact) <= self.portee
                and (p.y - self.C.y) < 0.020)

    def deplacer(self, p, intensite):
        p = Vector(p)
        if not self.concerne(p):
            return Vector((0, 0, 0))
        dz = p.z - self.z_contact
        # 0 aux commissures, 1 au centre
        w_lat = 1.0 - lisse(abs(p.x - self.C.x) / max(self.demi, 1e-9))
        # 1 pres de la ligne de contact, 0 au bord de la portee
        w_z = 1.0 - lisse(abs(dz) / self.portee)
        w = w_lat * w_z * intensite
        return Vector((0.0, 0.0, -dz * w))


# ---------------------------------------------------------- machoire ----

class Machoire:
    """Rotation autour de l'axe temporo-mandibulaire MESURE, plus translation.

    Le pivot est pris sur la ligne des deux conduits auditifs — jamais au
    menton. La levre superieure, rattachee au crane, ne bouge pas.
    """

    def __init__(self, pivot, axe, z_haut, z_bas, avance_par_degre=0.00035):
        self.P = Vector(pivot)
        self.axe = Vector(axe).normalized()
        self.z_haut = float(z_haut)   # au-dessus : rien ne bouge (levre sup, crane)
        self.z_bas = float(z_bas)     # en dessous : entrainement plein
        self.avance = avance_par_degre

    def poids(self, p):
        z = Vector(p).z
        if z >= self.z_haut: return 0.0
        if z <= self.z_bas: return 1.0
        return lisse((self.z_haut - z) / max(self.z_haut - self.z_bas, 1e-9))

    def deplacer(self, p, degres):
        p = Vector(p)
        w = self.poids(p)
        if w <= 0.0 or degres == 0.0:
            return Vector((0, 0, 0))
        a = math.radians(degres) * w
        d = p - self.P
        q = self.P + d @ __import__("mathutils").Matrix.Rotation(-a, 3, self.axe).transposed()
        # translation antero-inferieure progressive, comme une vraie ouverture
        q = q + Vector((0.0, -1.0, -0.35)).normalized() * (self.avance * degres * w)
        return q - p
