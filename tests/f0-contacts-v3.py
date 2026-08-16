"""F0-B.11 — mesure des contacts sur ONZE valeurs, cage ET Multires evalue.

La voie dense n'est plus un SKIP : les points de paire de la cage sont projetes
sur la surface evaluee par plus-proche-point, ce qui donne une correspondance
definie meme quand les indices denses different.
"""
import argparse, importlib.util, json, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "tests"))
from atlas_commun import Registre
MM = 1000.0; TETE = "GEO-head_animation_realistic"
POSES = {"blink_L": "fente_palpebrale.L", "blink_R": "fente_palpebrale.R",
         "mouth_close": "fente_labiale"}
SEUILS = {"fente_palpebrale.L": 0.20, "fente_palpebrale.R": 0.20,
          "fente_labiale": 0.30}

def pt(co, seg, t): return co[seg[0]].lerp(co[seg[1]], t)

def bvh_evalue(ob):
    ob.data.update(); ob.update_tag(); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm); n = len(me.vertices)
    bm.free(); ev.to_mesh_clear()
    return t, n

def mesures(co, paires, seuil):
    d = [(pt(co, p["upper_segment"], p["upper_t"])
          - pt(co, p["lower_segment"], p["lower_t"])).length * MM for p in paires]
    s = [(pt(co, p["upper_segment"], p["upper_t"]).z
          - pt(co, p["lower_segment"], p["lower_t"]).z) * MM for p in paires]
    return {"gap_max_mm": round(max(d), 5), "gap_median_mm": round(sorted(d)[len(d)//2], 5),
            "separation_signee_min_mm": round(min(s), 5),
            "croisements": sum(1 for x in s if x < -0.05), "seuil_mm": seuil}

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for f in ("--input", "--deltas", "--pairs", "--output"): a.add_argument(f, required=True)
    o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
    Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(Rp(o.input)))
    tete = bpy.data.objects[TETE]; me = tete.data; M = tete.matrix_world
    basis = [v.co.copy() for v in me.vertices]
    P = json.load(open(Rp(o.pairs), encoding="utf-8"))
    aretes = [(e.vertices[0], e.vertices[1]) for e in me.edges]
    L0 = [(basis[a2] - basis[b2]).length for a2, b2 in aretes]
    reg = Registre("f0-contacts-v3")
    R = {"poses": {}}
    for pose, cle in POSES.items():
        D = json.load(open(os.path.join(Rp(o.deltas), pose + ".cage-delta.json"),
                           encoding="utf-8"))
        dl = {d["index"]: Vector(d["delta_object_local_xyz"]) for d in D["deltas"]}
        paires = P["ouvertures"][cle]["paires"]; seuil = SEUILS[cle]
        serie = []
        for k in range(11):
            t = k / 10.0
            co = [basis[i] + dl.get(i, Vector((0, 0, 0))) * t for i in range(len(basis))]
            m = mesures(co, paires, seuil)
            r = [(co[x] - co[y]).length / l for (x, y), l in zip(aretes, L0) if l > 1e-9]
            m.update(t=round(t, 2), arete_min=round(min(r), 5), arete_max=round(max(r), 5),
                     retour_neutre_mm=round(max((c - b).length for c, b in zip(co, basis)) * MM, 6)
                     if t == 0 else None)
            # voie DENSE : projection plus-proche-point sur la surface evaluee
            for i, v in dl.items(): me.vertices[i].co = basis[i] + v * t
            me.update()
            bvh, nd = bvh_evalue(tete)
            gd = []
            for p in paires:
                ph = M @ pt(co, p["upper_segment"], p["upper_t"])
                pb = M @ pt(co, p["lower_segment"], p["lower_t"])
                lh = bvh.find_nearest(ph, 0.02)[0]; lb = bvh.find_nearest(pb, 0.02)[0]
                if lh is not None and lb is not None: gd.append((lh - lb).length * MM)
            m["dense_gap_max_mm"] = round(max(gd), 5) if gd else None
            m["dense_sommets"] = nd
            for i in dl: me.vertices[i].co = basis[i]
            me.update()
            serie.append(m)
        R["poses"][pose] = {"ouverture": cle, "serie": serie}
        fin, deb = serie[-1], serie[0]
        mono = all(serie[i+1]["gap_max_mm"] <= serie[i]["gap_max_mm"] + 1e-6 for i in range(10))
        reg.exige("%s.retour_neutre" % pose, "t=0 rend le Basis",
                  "onze valeurs", "<= 0,01 mm", deb["retour_neutre_mm"],
                  deb["retour_neutre_mm"] <= 0.01, tolerance=0.01)
        reg.exige("%s.monotone" % pose, "le jour decroit sur les onze valeurs",
                  "t de 0 a 1 par 0,1", True, mono, mono)
        reg.exige("%s.gap_cage" % pose, "jour final sur la cage",
                  "t = 1", "<= %.2f mm" % seuil, fin["gap_max_mm"],
                  fin["gap_max_mm"] <= seuil, tolerance=seuil)
        reg.exige("%s.gap_dense" % pose, "jour final sur la surface evaluee",
                  "t = 1", "<= %.2f mm" % seuil, fin["dense_gap_max_mm"],
                  fin["dense_gap_max_mm"] is not None and fin["dense_gap_max_mm"] <= seuil,
                  tolerance=seuil)
        reg.exige("%s.separation_signee" % pose, "pas de croisement des marges",
                  "t = 1", ">= -0,05 mm", fin["separation_signee_min_mm"],
                  fin["separation_signee_min_mm"] >= -0.05, tolerance=0.05)
        reg.exige("%s.aretes" % pose, "ratio d'arete dans [0,50 ; 2,00]",
                  "t = 1", "0,50 a 2,00",
                  [fin["arete_min"], fin["arete_max"]],
                  0.50 <= fin["arete_min"] and fin["arete_max"] <= 2.00)
    R["registre"] = reg.bilan()
    s = Rp(o.output); os.makedirs(os.path.dirname(s) or ".", exist_ok=True)
    json.dump(R, open(s, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = reg.conclure(); print("CONTACTS_V3", "OK" if ok else "SEUILS NON SATISFAITS", "->", o.output)
    sys.exit(0 if ok else 2)
