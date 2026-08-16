"""Deformations anatomiques jetables : clignement, fermeture labiale, mandibule.

Ce sont des PROTOTYPES. Rien ici ne survit dans la source autoritaire. Leur
seul role est de repondre a la question que le bourrelet cosinus du banc V1 ne
pouvait pas trancher : la topologie tient-elle un vrai pli ?

Chaque deformation est une fonction de la POSITION MONDE, donc applicable a la
cage de 3 242 sommets comme au maillage evalue de 12 950 : les deux voies
recoivent exactement le meme geste.

REGLE APPRISE A LA PASSE 3 — la deformation et la mesure doivent porter sur le
MEME ensemble de sommets. Le clignement etait borne a un rayon autour du globe
alors que la metrique auditee couvrait aussi les sommets conjonctivaux, hors de
ce rayon : ils ne bougeaient jamais, et il restait 6,4 mm de jour qu'aucun
reglage d'intensite ne pouvait fermer. Le clignement est donc desormais ancre
sur le BORD PUBLIE EN F0.
"""
import math
from mathutils import Vector, Matrix

MM = 1000.0


def lisse(t):
    """Rampe C1 sur [0,1] : pas de cassure aux bords de la zone d'influence."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def poids_canthus(u, garde=0.85):
    """Poids lateral d'une fente : PLEIN partout, sauf tout pres des extremites.

    Enonce anatomique, pose avant la mesure : une paupiere se ferme sur toute la
    longueur de la fente et ne reste ouverte qu'aux canthus eux-memes ; une
    bouche se ferme de meme partout sauf aux commissures. Une decroissance qui
    commence des le centre — ce que faisait la version precedente — interdit la
    fermeture sur les deux tiers lateraux, et rendait 6 a 8 mm de jour que
    l'intensite ne pouvait pas rattraper.
    """
    u = min(1.0, abs(u))
    if u <= garde:
        return 1.0
    return 1.0 - lisse((u - garde) / max(1.0 - garde, 1e-9))


# ------------------------------------------------------- clignement ----

class Clignement:
    """Fermeture ancree sur le bord palpebral publie en F0.

    - la paupiere superieure parcourt 75 % de l'ouverture, l'inferieure 25 % :
      la ligne de contact est placee pour que ce soit vrai, et les DEUX marges
      la visent — sans quoi elles ne se rejoignent jamais ;
    - le poids decroit avec la distance au bord, pas avec la distance au globe ;
    - il s'annule aux deux canthus, qui restent stables ;
    - la trajectoire tourne autour du centre du globe : le rayon est conserve,
      la fermeture epouse la sphere au lieu de translater verticalement ;
    - apres rotation, tout sommet rentre dans le globe est repousse dehors.
    """

    PART_SUP, PART_INF = 0.75, 0.25

    def __init__(self, bord, centre_globe, rayon_globe, axe_lateral,
                 portee=0.0090, epaisseur=0.0004):
        self.bord = [Vector(p) for p in bord]
        self.C = Vector(centre_globe)
        self.R = float(rayon_globe)
        self.lat = Vector(axe_lateral).normalized()
        self.portee = portee        # distance AU BORD au-dela de laquelle on ne touche plus
        self.epaisseur = epaisseur
        h = [self._h(p) for p in self.bord]
        lat = [abs((p - self.C).dot(self.lat)) for p in self.bord]
        self.h_max, self.h_min = max(h), min(h)
        self.lat_max = max(lat) if lat else 1.0
        self.h_contact = self.h_min + self.PART_INF * (self.h_max - self.h_min)

    def _h(self, p):
        d = Vector(p) - self.C
        return (d - self.lat * d.dot(self.lat)).z

    def distance_au_bord(self, p):
        p = Vector(p)
        return min((p - b).length for b in self.bord)

    def concerne(self, p):
        return self.distance_au_bord(p) <= self.portee

    def deplacer(self, p, intensite):
        p = Vector(p)
        d_bord = self.distance_au_bord(p)
        if d_bord > self.portee or intensite <= 0.0:
            return Vector((0, 0, 0))
        h = self._h(p)
        lateral = (p - self.C).dot(self.lat)
        w = ((1.0 - lisse(d_bord / self.portee))
             * poids_canthus(lateral / max(self.lat_max, 1e-9))
             * intensite)
        if w <= 0.0:
            return Vector((0, 0, 0))
        h_vise = h + (self.h_contact - h) * w
        d = p - self.C
        lat_comp = self.lat * d.dot(self.lat)
        radial = d - lat_comp
        r = radial.length
        if r < 1e-9:
            return Vector((0, 0, 0))
        horiz = Vector((radial.x, radial.y, 0.0))
        if horiz.length < 1e-9:
            return Vector((0, 0, 0))
        horiz.normalize()
        a2 = math.asin(max(-1.0, min(1.0, max(-r, min(r, h_vise)) / r)))
        q = self.C + lat_comp + (horiz * (math.cos(a2) * r)
                                 + Vector((0.0, 0.0, math.sin(a2) * r)))
        dd = q - self.C
        if dd.length < self.R + self.epaisseur:
            q = self.C + dd.normalized() * (self.R + self.epaisseur)
        return q - p


# -------------------------------------------------- fermeture labiale ----

class FermetureLabiale:
    """Les levres se rencontrent sur une ligne de contact, sans translation globale.

    Ancree elle aussi sur le bord de la fente labiale publie en F0.
    """

    def __init__(self, bord, portee=0.011):
        self.bord = [Vector(p) for p in bord]
        xs = [p.x for p in self.bord]
        self.cx = sum(xs) / len(xs)
        self.demi = (max(xs) - min(xs)) / 2.0
        self.z_contact = sum(p.z for p in self.bord) / len(self.bord)
        self.portee = portee

    def distance_au_bord(self, p):
        p = Vector(p)
        return min((p - b).length for b in self.bord)

    def concerne(self, p):
        return self.distance_au_bord(p) <= self.portee

    def deplacer(self, p, intensite):
        p = Vector(p)
        d_bord = self.distance_au_bord(p)
        if d_bord > self.portee or intensite <= 0.0:
            return Vector((0, 0, 0))
        w = ((1.0 - lisse(d_bord / self.portee))
             * poids_canthus((p.x - self.cx) / max(self.demi, 1e-9))
             * intensite)
        return Vector((0.0, 0.0, (self.z_contact - p.z) * w))


# ---------------------------------------------------------- machoire ----

class Machoire:
    """Rotation autour de l'axe temporo-mandibulaire MESURE, plus translation.

    Le pivot est pris sur la ligne des deux conduits auditifs — jamais au
    menton. Trois garde-fous, appris du rendu de la passe 3 ou tout le bas du
    visage descendait en bloc et effacait les levres :

      - la levre SUPERIEURE est rattachee au crane : rien au-dessus de la ligne
        de contact labiale ne bouge ;
      - le poids retombe en ARRIERE du pivot, sinon la nuque part avec ;
      - il retombe aussi vers le bas du cou, qui n'appartient pas a la mandibule.
    """

    def __init__(self, pivot, axe, z_levre, z_menton, y_arriere,
                 z_bas_cou=None, avance_par_degre=0.00030):
        self.P = Vector(pivot)
        self.axe = Vector(axe).normalized()
        self.z_levre = float(z_levre)     # au-dessus : rien ne bouge
        self.z_menton = float(z_menton)   # entrainement plein au menton
        self.y_arriere = float(y_arriere)  # au-dela : on relache vers l'arriere
        self.z_bas_cou = z_bas_cou
        self.avance = avance_par_degre

    def poids(self, p):
        p = Vector(p)
        if p.z >= self.z_levre:
            return 0.0
        w = lisse((self.z_levre - p.z) / max(self.z_levre - self.z_menton, 1e-9))
        # relachement vers l'arriere : la mandibule ne tire pas la nuque
        if p.y > self.y_arriere:
            w *= 1.0 - lisse((p.y - self.y_arriere) / 0.045)
        # relachement vers le bas : le cou n'est pas la mandibule
        if self.z_bas_cou is not None and p.z < self.z_menton:
            w *= 1.0 - lisse((self.z_menton - p.z) / max(self.z_menton - self.z_bas_cou, 1e-9))
        return max(0.0, min(1.0, w))

    def deplacer(self, p, degres):
        p = Vector(p)
        w = self.poids(p)
        if w <= 0.0 or degres == 0.0:
            return Vector((0, 0, 0))
        a = math.radians(degres) * w
        q = self.P + (Matrix.Rotation(a, 3, self.axe) @ (p - self.P))
        q = q + Vector((0.0, -1.0, -0.35)).normalized() * (self.avance * degres * w)
        return q - p
