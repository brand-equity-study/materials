"""Study 2a, the reasons in the models' explanations: each model's share under each judge, one row per model and
judge, for the analysis of how the models differed (how-the-models-differed/).

    python study2a-experience-attributes-stated-for-every-product/code/explanations/per_model.py

Reads study2a-experience-attributes-stated-for-every-product/results/explanations/numbers.json (shares.py) and writes study2a-experience-attributes-stated-for-every-product/results/explanations/per-model.csv. A share
of 0 or 1 has a bootstrap interval over tables of zero width; that row takes Wilson's interval on the model's count.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "results", "explanations")


def wilson(p, n, z=1.959963984540054):
    """Wilson's 95 per cent interval for a share p of n (the count is p times n)."""
    if p is None or not n:
        return None, None
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def main():
    r = json.load(open(os.path.join(RES, "numbers.json"), encoding="utf8"))
    g0 = r["shares"][r["judges"][0]]
    out = []
    for j in r["judges"]:
        for m, v in r["shares"][j]["per_model"].items():
            lo, hi, method = v.get("lo"), v.get("hi"), "bootstrap over tables"
            wl, wh = wilson(v.get("est"), v["n"])
            if lo is not None and hi - lo < 1e-12:
                lo, hi, method = wl, wh, "Wilson (the bootstrap interval over tables has zero width)"
            out.append({"model": m, "group": v.get("group", g0["per_model"].get(m, {}).get("group", "")), "judge": j,
                        "test": "b7-brand-share", "estimate": v.get("est"), "lo95": lo, "hi95": hi,
                        "interval_method": method, "wilson_lo95": wl, "wilson_hi95": wh,
                        "n": v["n"], "tables": v["tables"], "not_estimable": v.get("not_estimable", ""),
                        "units": "share of the model's explanations whose brand_any is yes (0 to 1)",
                        "predicted_direction": "", "direction_source": "no direction predicted (two-sided tests)"})
    with open(os.path.join(RES, "per-model.csv"), "w", encoding="utf8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"wrote per-model.csv: {len(out)} rows, one per model and judge")


if __name__ == "__main__":
    main()
