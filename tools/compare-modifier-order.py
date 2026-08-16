import argparse, json, os, sys
a = argparse.ArgumentParser()
for f in ("--a", "--b", "--output"): a.add_argument(f, required=True)
o = a.parse_args(sys.argv[1:])
A = json.load(open(o.a, encoding="utf-8")); B = json.load(open(o.b, encoding="utf-8"))
if set(A["poses"]) != set(B["poses"]): print("poses differentes"); sys.exit(2)
R = {"A": A["label"], "B": B["label"], "ordre_A": A["ordre"], "ordre_B": B["ordre"],
     "octets": {"A": A["octets_blend"], "B": B["octets_blend"]},
     "retour_neutre_mm": {"A": A["retour_neutre_mm"], "B": B["retour_neutre_mm"]},
     "poses": {}}
for p in sorted(A["poses"]):
    x, y = A["poses"][p], B["poses"][p]
    R["poses"][p] = {"sommets": [x["sommets"], y["sommets"]],
        "temps_median_s": [x["temps_median_s"], y["temps_median_s"]],
        "temps_p95_s": [x["temps_p95_s"], y["temps_p95_s"]],
        "uv_identique": [x["uv_identique_au_neutre"], y["uv_identique_au_neutre"]],
        "ecart_au_neutre_mm": [x["ecart_au_neutre_mm"], y["ecart_au_neutre_mm"]],
        "meme_uv_entre_A_et_B": x["uv_sha"] == y["uv_sha"]}
ma = sum(A["poses"][p]["temps_median_s"] for p in A["poses"])
mb = sum(B["poses"][p]["temps_median_s"] for p in B["poses"])
R["somme_temps_median_s"] = {"A": round(ma, 6), "B": round(mb, 6)}
R["plus_rapide"] = "A" if ma < mb else "B"
json.dump(R, open(o.output, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("COMPARE plus rapide:", R["plus_rapide"], "| A %.5f s / B %.5f s" % (ma, mb))
for p in sorted(R["poses"]):
    e = R["poses"][p]["ecart_au_neutre_mm"]
    print("  %-16s A %.4f / B %.4f mm | meme UV %s" % (
        p, e[0]["max"] if e[0] else -1, e[1]["max"] if e[1] else -1,
        R["poses"][p]["meme_uv_entre_A_et_B"]))
