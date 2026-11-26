"""The names gap of Study 1: the share of recommendations that are not the best product with names shown, minus the
share with names hidden, over the 30 models and the 34 tables.

An answer whose first line holds no product letter is counted as not the best product; the gap is also given without
those answers.

    python study1b-64-models-on-34-tables/code/01_names_gap.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402


def main() -> int:
    df, info = cc.load_rows(["model_key", "assortment_id", "chose_optimal", "choice"])
    df["non_optimal"] = 1.0 - df["chose_optimal"].astype(float)
    models, tables, arr = cc.cell_arrays(df, "non_optimal")
    s1, n1 = arr[cc.SHOWN]
    s0, n0 = arr[cc.HIDDEN]
    missing = int(((n1 == 0) | (n0 == 0)).sum())
    shown, hidden = s1.sum() / n1.sum(), s0.sum() / n0.sum()
    gap = shown - hidden

    unparsed = df[df["choice"].astype(str).str.strip() == "?"].groupby("condition").size().to_dict()
    parsed = df[df["choice"].astype(str).str.strip() != "?"]
    ps = parsed[parsed.condition == cc.SHOWN]["non_optimal"].mean()
    ph = parsed[parsed.condition == cc.HIDDEN]["non_optimal"].mean()

    res = {
        "shown": {"non_optimal": int(s1.sum()), "trials": int(n1.sum()), "pct": round(100 * shown, 2)},
        "hidden": {"non_optimal": int(s0.sum()), "trials": int(n0.sum()), "pct": round(100 * hidden, 2)},
        "gap_pp": round(100 * gap, 2),
        "models": len(models), "tables": len(tables), "cells": len(models) * len(tables), "cells_missing_a_condition": missing,
        "unparsed_answers": {"shown": int(unparsed.get(cc.SHOWN, 0)), "hidden": int(unparsed.get(cc.HIDDEN, 0)),
                             "note": "an answer whose first line held no product letter is counted as not the best product"},
        "without_unparsed": {"shown_pct": round(100 * ps, 2), "hidden_pct": round(100 * ph, 2), "gap_pp": round(100 * (ps - ph), 2)},
    }
    cc.write_result("names_gap", res, "study1b-64-models-on-34-tables/code/01_names_gap.py", info)
    print(f"shown {res['shown']['pct']}% ({res['shown']['non_optimal']}/{res['shown']['trials']}); hidden {res['hidden']['pct']}% "
          f"({res['hidden']['non_optimal']}/{res['hidden']['trials']}); gap {res['gap_pp']} points")
    print(f"answers with no letter {res['unparsed_answers']}; gap without them {res['without_unparsed']['gap_pp']} points")
    return 0


if __name__ == "__main__":
    sys.exit(main())
