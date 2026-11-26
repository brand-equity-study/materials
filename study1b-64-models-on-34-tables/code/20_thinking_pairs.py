"""The brand gap of the same model with and without extended thinking.

The corpus ran four models both ways: Claude Haiku 4.5, Claude Sonnet 4.6, GPT-5.4 mini and Gemini 3 Flash. For each
version, the gap is the share of recommendations away from the best product with names shown minus with names hidden
(conditions baseline and baseline_brand_blind, the same 34 tables and 20 trials). The difference is the gap with
extended thinking minus the gap without it. Intervals resample the 34 tables with replacement, with the same tables
for both versions of a model (10,000 draws, seed 20261120); the pooled row averages the four pairs with equal weight.

    python study1b-64-models-on-34-tables/code/20_thinking_pairs.py      writes thinking_pairs in study1b-64-models-on-34-tables/results/numbers.json
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402

PAIRS = {"Claude Haiku 4.5": ("claude-haiku-4.5", "claude-haiku-4.5-thinking"),
         "Claude Sonnet 4.6": ("claude-sonnet-4.6", "claude-sonnet-4.6-thinking"),
         "GPT-5.4 mini": ("gpt-5.4-mini", "gpt-5.4-mini-thinking"),
         "Gemini 3 Flash": ("gemini-3-flash", "gemini-3-flash-thinking")}


def main():
    df, info = cc.load_rows(["model_key", "assortment_id", "condition", "chose_optimal", "thinking", "thinking_length"])
    df["nonopt"] = 1.0 - df.chose_optimal.astype(str).eq("True").astype(float)
    keys = [k for pair in PAIRS.values() for k in pair]
    models, tables, arr = cc.cell_arrays(df[df.model_key.isin(keys)], "nonopt", models=keys)
    idx = {m: i for i, m in enumerate(models)}
    rng = np.random.default_rng(cc.SEED)
    draw = rng.integers(0, len(tables), (cc.DRAWS, len(tables)))

    def gap(i, ai=None):
        (s1, n1), (s0, n0) = arr[cc.SHOWN], arr[cc.HIDDEN]
        if ai is None:
            return 100 * (s1[i].sum() / n1[i].sum() - s0[i].sum() / n0[i].sum())
        return 100 * (s1[i][ai].sum(1) / n1[i][ai].sum(1) - s0[i][ai].sum(1) / n0[i][ai].sum(1))

    res, diffs = {"pairs": {}}, []
    for name, (off, on) in PAIRS.items():
        g_off, g_on = gap(idx[off]), gap(idx[on])
        b_off, b_on = gap(idx[off], draw), gap(idx[on], draw)
        diffs.append(b_on - b_off)
        rec = {}
        for label, key in (("without", off), ("with", on)):
            g = df[df.model_key == key]
            rec[f"{label}_extended_thinking"] = {
                "model_key": key, "answers": int(len(g)),
                "thinking_flag_recorded": {str(k): int(v) for k, v in g.thinking.value_counts().items()},
                "answers_with_a_recorded_thinking_trace": int((g.thinking_length.fillna(0) > 0).sum()),
                "shown_nonoptimal_pct": round(100 * float(g[g.condition == cc.SHOWN].nonopt.mean()), 2),
                "hidden_nonoptimal_pct": round(100 * float(g[g.condition == cc.HIDDEN].nonopt.mean()), 2)}
        rec["without_extended_thinking"].update(gap_pp=round(float(g_off), 2), ci95_tables_resampled=cc.ci(b_off), p_two_sided=cc.p_two_sided(b_off))
        rec["with_extended_thinking"].update(gap_pp=round(float(g_on), 2), ci95_tables_resampled=cc.ci(b_on), p_two_sided=cc.p_two_sided(b_on))
        rec["difference_with_minus_without_pp"] = round(float(g_on - g_off), 2)
        rec["difference_ci95_tables_resampled"] = cc.ci(b_on - b_off)
        rec["difference_p_two_sided"] = cc.p_two_sided(b_on - b_off)
        res["pairs"][name] = rec
    pooled = np.mean(diffs, axis=0)
    point = float(np.mean([res["pairs"][n]["difference_with_minus_without_pp"] for n in PAIRS]))
    res["pooled_difference_four_pairs_pp"] = round(point, 2)
    res["pooled_difference_ci95_tables_resampled"] = cc.ci(pooled)
    res["pooled_difference_p_two_sided"] = cc.p_two_sided(pooled)
    res["note"] = ("a model run with and without extended thinking counts as two of the 30 models; the thinking flag and the "
                   "thinking-trace lengths are as the corpus records them (run_settings gives each model's settings)")
    cc.write_result("thinking_pairs", res, "study1b-64-models-on-34-tables/code/20_thinking_pairs.py", info)
    import json
    print(json.dumps(res, indent=1, default=cc._plain))
    return 0


if __name__ == "__main__":
    sys.exit(main())
