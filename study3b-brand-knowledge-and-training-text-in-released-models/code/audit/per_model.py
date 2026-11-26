"""Study 3b's questions about each brand: each model's own slope, one row per model and estimate, for the analysis of
how the models differed (how-the-models-differed/).

    python study3b-brand-knowledge-and-training-text-in-released-models/code/audit/per_model.py

Reads study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json (analyze_audit.py --panel all) and writes
study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv: the model, its group, the test, the component, the estimate and its 95 per
cent interval from the bootstrap over tables (over categories for recall at consideration), the rows and the draws,
the units, the model's split-half reliability of the gap and of the component, and the predicted direction where the
analysis predicts one (inferred quality and credibility at evaluation, and recall at consideration: positive). A slope
whose component varies in fewer than three of the model's tables is not estimable and has no estimate.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "results", "audit")
MIN_CLUSTERS = 3   # as analyze_audit.MIN_CLUSTERS
DIRECTION = {(t, c): ("positive", "predicted for inferred quality and credibility at evaluation")
             for t in ("test1", "test2") for c in ("quality", "credibility")}
DIRECTION[("h6b", "recall")] = ("positive", "predicted for recall at consideration")
NO_DIRECTION = ("", "no direction predicted (two-sided tests)")
UNITS = {"test1": "points of the gap per standard deviation of the component within the model",
         "test2": "points of the gap per standard deviation of the difference in the component within the model",
         "h6b": "consideration share per standard deviation of recall within the model"}


def per_model_rows(r):
    rows = []
    groups = r.get("groups", {})
    for m, by in r["exploratory"]["test1_by_model"].items():
        for c, v in by.items():
            rows.append((m, "test1", c, v))
    for c, by in r["heterogeneity"]["test2_by_model"].items():
        for m, v in by.items():
            rows.append((m, "test2", c, v))
    for m, v in r["heterogeneity"]["h6b_by_model"].items():
        rows.append((m, "h6b", "recall", v))
    rel = r.get("reliability", {})
    out = []
    for m, t, c, v in sorted(rows, key=lambda x: (x[1], x[2], x[0])):
        d, src = DIRECTION.get((t, c), NO_DIRECTION)
        k = v.get("clusters_varying")
        few = k is not None and k < MIN_CLUSTERS
        out.append({"model": m, "group": groups.get(m, ""), "test": t, "component": c,
                    "estimate": None if few else v.get("est"), "lo95": None if few else v.get("lo"),
                    "hi95": None if few else v.get("hi"), "n": v.get("n"),
                    "draws": v.get("draws"), "clusters_varying": k,
                    "not_estimable": (f"the component varies in {k} of the model's tables (fewer than {MIN_CLUSTERS}), "
                                      "so the slope has no interval over tables") if few else "",
                    "units": UNITS[t],
                    "gap_reliability": rel.get(m, {}).get("gap"),
                    "component_reliability": rel.get(m, {}).get(c) if t != "h6b" else None,
                    "predicted_direction": d, "direction_source": src})
    return out


def main():
    r = json.load(open(os.path.join(RES, "numbers-all.json"), encoding="utf8"))
    rows = per_model_rows(r)
    with open(os.path.join(RES, "per-model-all.csv"), "w", encoding="utf8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote per-model-all.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
