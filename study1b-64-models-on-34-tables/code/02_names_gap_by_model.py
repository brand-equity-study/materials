"""The names gap for each of the 30 models, for each of the 34 tables, and pooled.

The gap is the share of answers that are not the best product with names shown minus the share with names hidden, on
the same tables and the same model. Intervals:
- pooled: a two-way cluster (pigeonhole) bootstrap that resamples the 30 models and the 34 tables with replacement and
  crosses them, trial-weighted (common.DRAWS draws, seed common.SEED);
- one model: the model is fixed and its 34 tables are resampled with replacement;
- one table: the table is fixed and the 30 models are resampled with replacement.
Each model is listed with the model identifier that the corpus records and the first and last timestamps of its answers
in the two conditions, so that each estimate is tied to a model version and a collection date.

    python study1b-64-models-on-34-tables/code/02_names_gap_by_model.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402


def main() -> int:
    cols = ["model_key", "model_id", "provider", "assortment_id", "category", "chose_optimal", "timestamp", "thinking"]
    df, info = cc.load_rows(cols)
    df["non_optimal"] = 1.0 - df["chose_optimal"].astype(float)
    models, tables, arr = cc.cell_arrays(df, "non_optimal")
    s1, n1 = arr[cc.SHOWN]
    s0, n0 = arr[cc.HIDDEN]

    pooled = cc.pooled_gap(arr)
    boot = cc.twoway_bootstrap(arr, len(models), len(tables))
    # Equal weight for every model: the mean of the 30 per-model gaps, with the same two-way resampling.
    rng = np.random.default_rng(cc.SEED + 1)
    per_model_point = s1.sum(1) / n1.sum(1) - s0.sum(1) / n0.sum(1)
    eq_draws = np.empty(cc.DRAWS)
    for d in range(cc.DRAWS):
        mi = rng.integers(0, len(models), len(models))
        ai = rng.integers(0, len(tables), len(tables))
        a1, b1 = s1[np.ix_(mi, ai)].sum(1), n1[np.ix_(mi, ai)].sum(1)
        a0, b0 = s0[np.ix_(mi, ai)].sum(1), n0[np.ix_(mi, ai)].sum(1)
        eq_draws[d] = np.mean(a1 / b1 - a0 / b0)

    meta = df.groupby("model_key").agg(model_id=("model_id", lambda x: sorted(set(map(str, x)))),
                                       provider=("provider", "first"),
                                       first=("timestamp", "min"), last=("timestamp", "max"),
                                       thinking=("thinking", lambda x: sorted(set(map(str, x)))))
    per_model = []
    for i, m in enumerate(models):
        b = cc.one_way_bootstrap(arr, 0, i)
        per_model.append({
            "model_key": m, "model_id": meta.loc[m, "model_id"], "provider": meta.loc[m, "provider"],
            "thinking": meta.loc[m, "thinking"],
            "answers_from": str(meta.loc[m, "first"])[:10], "answers_to": str(meta.loc[m, "last"])[:10],
            "shown": {"non_optimal": int(s1[i].sum()), "trials": int(n1[i].sum()), "pct": round(100 * s1[i].sum() / n1[i].sum(), 2)},
            "hidden": {"non_optimal": int(s0[i].sum()), "trials": int(n0[i].sum()), "pct": round(100 * s0[i].sum() / n0[i].sum(), 2)},
            "gap_pp": round(100 * per_model_point[i], 2), "ci95_pp_tables_resampled": cc.ci(b, 100), "p_two_sided": cc.p_two_sided(b),
        })
    per_model.sort(key=lambda r: -r["gap_pp"])

    cat = df.groupby("assortment_id")["category"].first()
    per_table = []
    per_table_point = s1.sum(0) / n1.sum(0) - s0.sum(0) / n0.sum(0)
    for j, t in enumerate(tables):
        b = cc.one_way_bootstrap(arr, 1, j)
        per_table.append({
            "table": t, "category": cat[t],
            "shown_pct": round(100 * s1[:, j].sum() / n1[:, j].sum(), 2),
            "hidden_pct": round(100 * s0[:, j].sum() / n0[:, j].sum(), 2),
            "gap_pp": round(100 * per_table_point[j], 2), "ci95_pp_models_resampled": cc.ci(b, 100), "p_two_sided": cc.p_two_sided(b),
        })
    per_table.sort(key=lambda r: -r["gap_pp"])

    gm = np.array([r["gap_pp"] for r in per_model])
    gt = np.array([r["gap_pp"] for r in per_table])
    lo_m = sum(1 for r in per_model if r["ci95_pp_tables_resampled"][0] > 0)
    hi_m = sum(1 for r in per_model if r["ci95_pp_tables_resampled"][1] < 0)
    res = {
        "pooled": {"gap_pp": round(100 * pooled, 2), "ci95_pp": cc.ci(boot, 100), "p_two_sided": cc.p_two_sided(boot), "draws": cc.DRAWS, "seed": cc.SEED,
                   "method": "two-way cluster bootstrap: models and tables resampled with replacement and crossed; trial-weighted"},
        "models_weighted_equally": {"gap_pp": round(100 * float(per_model_point.mean()), 2), "ci95_pp": cc.ci(eq_draws, 100), "p_two_sided": cc.p_two_sided(eq_draws),
                                    "draws": cc.DRAWS, "seed": cc.SEED + 1, "method": "mean of per-model gaps, same two-way resampling"},
        "per_model_summary": {"n": len(models), "positive": int((gm > 0).sum()), "median_pp": round(float(np.median(gm)), 2),
                              "min_pp": float(gm.min()), "max_pp": float(gm.max()),
                              "interval_above_zero": lo_m, "interval_below_zero": hi_m},
        "per_table_summary": {"n": len(tables), "positive": int((gt > 0).sum()), "median_pp": round(float(np.median(gt)), 2),
                              "min_pp": float(gt.min()), "max_pp": float(gt.max()),
                              "interval_above_zero": sum(1 for r in per_table if r["ci95_pp_models_resampled"][0] > 0)},
        "per_model": per_model, "per_table": per_table,
    }
    cc.write_result("names_gap_by_model", res, "study1b-64-models-on-34-tables/code/02_names_gap_by_model.py", info)
    print(f"pooled {res['pooled']['gap_pp']} pp {res['pooled']['ci95_pp']}; models weighted equally {res['models_weighted_equally']}")
    print("per model:", res["per_model_summary"])
    print("per table:", res["per_table_summary"])
    for r in per_model:
        print(f"  {r['model_key']:28s} {r['model_id'][0][:34]:34s} {r['answers_from']}..{r['answers_to']} shown {r['shown']['pct']:5.1f} hidden {r['hidden']['pct']:5.1f} gap {r['gap_pp']:6.2f} {r['ci95_pp_tables_resampled']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
