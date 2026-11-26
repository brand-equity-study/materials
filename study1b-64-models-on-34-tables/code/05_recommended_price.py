"""The price of the product that the assistant recommends, names shown minus names hidden.

Every answer counts, whether it picks the best product or not, and the same products are compared with names shown and
hidden, so the design of the tables (the best product is the cheapest or tied cheapest in 24 of the 34) cancels out of
the difference.

For each answer the price of the recommended product is read from the row's product_<letter>_price column for the
letter that the model chose (the letters of a row follow that row's prompt; the script checks the price against the
prompt itself). Answers with no product letter are left out. Two measures:
- dollars: the mean price of the recommended product with names shown minus the mean with names hidden;
- relative: the same, with each price divided by the price of the table's best product, in percentage points of it.
Each is given for every model-by-table cell (study1b-64-models-on-34-tables/results/price_by_cell.csv), for each model (tables resampled), for
each table (models resampled) and pooled (two-way cluster bootstrap over models and tables; trial-weighted).
The difference describes the models' recommendations; it is not a cost to consumers.

    python study1b-64-models-on-34-tables/code/05_recommended_price.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402

LETTERS = "ABCDE"


def main() -> int:
    cols = ["model_key", "assortment_id", "choice", "optimal_product", "user_message"] + [f"product_{L}_price" for L in LETTERS]
    df, info = cc.load_rows(cols)
    df["choice"] = df["choice"].astype(str).str.strip()
    ok = df["choice"].isin(list(LETTERS))
    unparsed = (~ok).groupby(df["condition"]).sum().to_dict()

    def price_of(row, letter_col):
        L = row[letter_col]
        return cc.parse_price(row[f"product_{L}_price"]) if L in LETTERS else np.nan

    df["rec_price"] = df.apply(lambda r: price_of(r, "choice"), axis=1)
    df["best_price"] = df.apply(lambda r: price_of(r, "optimal_product"), axis=1)

    # check the column prices against the prompt the model saw, on every answer
    mismatches = 0
    for _, r in df[ok].iterrows():
        p = cc.parse_products(r["user_message"])
        if abs(cc.parse_price(p[r["choice"]]["Price"]) - r["rec_price"]) > 0.005:
            mismatches += 1
    if mismatches:
        raise SystemExit(f"REFUSED: {mismatches} answers whose price column differs from the prompt")
    best = df.groupby("assortment_id")["best_price"].agg(["min", "max"])
    if (best["min"] != best["max"]).any():
        raise SystemExit("REFUSED: a table's best product has more than one price")
    df["rec_rel"] = 100 * df["rec_price"] / df["best_price"]

    out = {"unparsed_answers_left_out": {k: int(v) for k, v in unparsed.items()}, "price_checked_against_prompt": int(ok.sum())}
    cells = {}
    for measure, unit in (("rec_price", "USD"), ("rec_rel", "percent of the best product's price")):
        models, tables, arr = cc.cell_arrays(df, measure)
        s1, n1 = arr[cc.SHOWN]
        s0, n0 = arr[cc.HIDDEN]
        boot = cc.twoway_bootstrap(arr, len(models), len(tables))
        pm = s1.sum(1) / n1.sum(1) - s0.sum(1) / n0.sum(1)
        pt = s1.sum(0) / n1.sum(0) - s0.sum(0) / n0.sum(0)
        per_model = [{"model_key": m, "shown_mean": round(float(s1[i].sum() / n1[i].sum()), 2), "hidden_mean": round(float(s0[i].sum() / n0[i].sum()), 2),
                      "difference": round(float(pm[i]), 2), "ci95_tables_resampled": cc.ci(cc.one_way_bootstrap(arr, 0, i)), "p_two_sided": cc.p_two_sided(cc.one_way_bootstrap(arr, 0, i))}
                     for i, m in enumerate(models)]
        per_table = [{"table": t, "best_price": float(best.loc[t, "min"]), "shown_mean": round(float(s1[:, j].sum() / n1[:, j].sum()), 2),
                      "hidden_mean": round(float(s0[:, j].sum() / n0[:, j].sum()), 2), "difference": round(float(pt[j]), 2),
                      "ci95_models_resampled": cc.ci(cc.one_way_bootstrap(arr, 1, j)), "p_two_sided": cc.p_two_sided(cc.one_way_bootstrap(arr, 1, j))}
                     for j, t in enumerate(tables)]
        cell_diff = np.where((n1 > 0) & (n0 > 0), s1 / np.maximum(n1, 1) - s0 / np.maximum(n0, 1), np.nan)
        cells[measure] = (models, tables, cell_diff, n1, n0)
        out[measure] = {
            "unit": unit,
            "pooled": {"shown_mean": round(float(s1.sum() / n1.sum()), 2), "hidden_mean": round(float(s0.sum() / n0.sum()), 2),
                       "difference": round(float(cc.pooled_gap(arr)), 2), "ci95": cc.ci(boot), "p_two_sided": cc.p_two_sided(boot), "draws": cc.DRAWS, "seed": cc.SEED},
            "per_model_summary": {"higher_with_names": int((pm > 0).sum()), "n": len(models), "median": round(float(np.median(pm)), 2),
                                  "interval_above_zero": sum(1 for r in per_model if r["ci95_tables_resampled"][0] > 0),
                                  "interval_below_zero": sum(1 for r in per_model if r["ci95_tables_resampled"][1] < 0)},
            "per_table_summary": {"higher_with_names": int((pt > 0).sum()), "n": len(tables), "median": round(float(np.median(pt)), 2),
                                  "interval_above_zero": sum(1 for r in per_table if r["ci95_models_resampled"][0] > 0),
                                  "interval_below_zero": sum(1 for r in per_table if r["ci95_models_resampled"][1] < 0)},
            "cells_higher_with_names": int(np.nansum(cell_diff > 0)), "cells_lower_with_names": int(np.nansum(cell_diff < 0)),
            "cells_equal": int(np.nansum(cell_diff == 0)),
            "per_model": sorted(per_model, key=lambda r: -r["difference"]), "per_table": sorted(per_table, key=lambda r: -r["difference"]),
        }
    cc.write_result("recommended_price", out, "study1b-64-models-on-34-tables/code/05_recommended_price.py", info)
    models, tables, d_usd, n1, n0 = cells["rec_price"]
    d_rel = cells["rec_rel"][2]
    with open(cc.RESULTS / "price_by_cell.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_key", "table", "answers_shown", "answers_hidden", "difference_usd", "difference_pct_of_best_price"])
        for i, m in enumerate(models):
            for j, t in enumerate(tables):
                w.writerow([m, t, int(n1[i, j]), int(n0[i, j]), round(float(d_usd[i, j]), 2), round(float(d_rel[i, j]), 2)])
    for measure in ("rec_price", "rec_rel"):
        o = out[measure]
        print(measure, o["pooled"], o["per_model_summary"], o["per_table_summary"],
              "cells +/-/=", o["cells_higher_with_names"], o["cells_lower_with_names"], o["cells_equal"])
    print("unparsed left out:", out["unparsed_answers_left_out"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
