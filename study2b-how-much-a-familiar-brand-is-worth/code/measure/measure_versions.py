"""Study 2b's small multiverse: each version of the measure against the main version, over every model that answered
it, from the final run's numbers (results/measure/full1-all/numbers.json.gz).

    python study2b-how-much-a-familiar-brand-is-worth/code/measure/measure_versions.py [--out PATH]

The versions change one feature of the main version each: no prices; the pretest's budget and prices; the request's
second wording; each product as a block of text; three products in place of five; a budget that spans the market.
analyze_mbbe2.py reads each brand's value in a version against the main version's value at the same price (no prices
against the main version at the market's centre, the pretest's budget at that budget's centre, the others at the
brand's band), as against_main's difference. Here, for each version, over the models in the estimates over models that
answered it (the open models; the Claude and GPT models answered only the main version), and leaving out a model's
category that the specifications rule leaves out:
- each pair of a brand and a category's share premium in the version and in the main version at the same price, each
  the mean over the models (the figure's points);
- the Spearman correlation between the two across the pairs;
- the mean over pairs and models of the version's share premium minus the main version's, with a 95% interval from
  2,000 draws of the models (seed 20261123).
Writes numbers.json (by default study2b-how-much-a-familiar-brand-is-worth/results/measure/versions/numbers.json) and pairs.csv beside it.
"""
import argparse
import csv
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[2]   # the top of the replication package
SRC = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "results" / "measure" / "full1-all" / "numbers.json.gz"
DEFAULT_OUT = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "results" / "measure" / "versions" / "numbers.json"
VERSIONS = [("V1-no-prices", "No prices"), ("V2-pilot-band", "The pretest's budget and prices"),
            ("V3-second-wording", "The request's second wording"), ("V4-blocks", "Each product as a block of text"),
            ("V5-three-products", "Three products in place of five"), ("V6-market-budget", "A budget that spans the market")]
DRAWS, SEED = 2000, 20261123


def share_premium(v):
    return 100 * (1.0 / (1.0 + 4.0 * math.exp(-v)) - 0.2) if v > -700 else -20.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="where to write numbers.json")
    args = ap.parse_args()
    out_file = Path(args.out)
    out_dir = out_file.parent
    with gzip.open(SRC, "rt", encoding="utf-8") as fh:
        r = json.load(fh)
    left = set(r.get("left_out", {}).get("models", {}))
    gone = {(c["model"], c["category"]) for c in r.get("cells_left_out", [])}
    rows = []
    for m, mres in r["models"].items():
        if m in left:
            continue
        for cat, c in mres.items():
            if (m, cat) in gone:
                continue
            for v, _ in VERSIONS:
                vres = c.get(v)
                if not vres:
                    continue
                for b, u in vres["brands"].items():
                    am = (vres.get("against_main") or {}).get(b)
                    if am is None or u.get("value") is None or am.get("difference") is None:
                        continue
                    main_v = u["value"] - am["difference"]
                    rows.append({"version": v, "model": m, "category": cat, "brand": b,
                                 "version_pp": share_premium(u["value"]), "main_pp": share_premium(main_v)})
    d = pd.DataFrame(rows)
    rng = np.random.default_rng(SEED)
    out = {"source": str(SRC.relative_to(PKG)).replace("\\", "/"), "draws": DRAWS, "seed": SEED, "versions": {}}
    out_dir.mkdir(parents=True, exist_ok=True)
    pair_rows = []
    for v, label in VERSIONS:
        x = d[d.version == v]
        if x.empty:
            continue
        pairs = x.groupby(["category", "brand"])[["version_pp", "main_pp"]].mean()
        rho = float(pairs.version_pp.rank().corr(pairs.main_pp.rank()))
        x = x.assign(diff=x.version_pp - x.main_pp)
        per_model = x.groupby("model")["diff"].mean()
        models = per_model.index.to_numpy()
        boot = [per_model.loc[rng.choice(models, len(models))].mean() for _ in range(DRAWS)]
        mean = float(x["diff"].mean())
        out["versions"][v] = {"label": label, "models": int(x.model.nunique()), "pairs": int(len(pairs)),
                              "spearman_with_main": rho, "mean_difference_pp": mean,
                              "mean_difference_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                              "main_mean_pp": float(x.main_pp.mean()), "version_mean_pp": float(x.version_pp.mean())}
        for (cat, b), p in pairs.iterrows():
            pair_rows.append({"version": v, "category": cat, "brand": b, "main_pp": round(p.main_pp, 3),
                              "version_pp": round(p.version_pp, 3)})
    rhos = [v["spearman_with_main"] for v in out["versions"].values()]
    out["spearman_lowest"], out["spearman_highest"] = min(rhos), max(rhos)
    out_file.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    with open(out_dir / "pairs.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pair_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(pair_rows)
    for v, e in out["versions"].items():
        print(f"{v:20s} models {e['models']:2d} pairs {e['pairs']} rho {e['spearman_with_main']:.2f} "
              f"diff {e['mean_difference_pp']:+.1f} [{e['mean_difference_ci95'][0]:+.1f}, {e['mean_difference_ci95'][1]:+.1f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
