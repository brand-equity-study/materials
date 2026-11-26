"""Do Gemini 2.5 Pro's answers that stop at the output cap explain its reversed brand gap?

Gemini 2.5 Pro is the only model of the 30 with a negative gap (-10.44 points, 02_names_gap_by_model.py) and the only
one with many answers that stop at the same length: 384 of its 1,360 Study 1 answers record exactly 1,020 output tokens
(07_model_settings.py). This
script compares the capped answers with the others: how many have no parsed letter, how they split between names
shown and names hidden, how often they pick the best product, and the gap (non-optimal with names shown minus names
hidden) with all answers, with the capped answers left out, and with the capped answers counted as no recommendation
(that is, as non-optimal). Intervals resample the 34 tables with replacement (10,000 draws, seed 20261120).

    python study1b-64-models-on-34-tables/code/06_long_answers.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402

MODEL = "gemini-2.5-pro"


def gap_by_table(g, nonopt_col):
    """Per table: (non-optimal answers, answers) for shown and hidden."""
    tabs = sorted(g.assortment_id.unique())
    s1 = np.array([g[(g.assortment_id == t) & (g.condition == cc.SHOWN)][nonopt_col].sum() for t in tabs], float)
    n1 = np.array([g[(g.assortment_id == t) & (g.condition == cc.SHOWN)][nonopt_col].count() for t in tabs], float)
    s0 = np.array([g[(g.assortment_id == t) & (g.condition == cc.HIDDEN)][nonopt_col].sum() for t in tabs], float)
    n0 = np.array([g[(g.assortment_id == t) & (g.condition == cc.HIDDEN)][nonopt_col].count() for t in tabs], float)
    return s1, n1, s0, n0


def gap_with_ci(g, col):
    s1, n1, s0, n0 = gap_by_table(g, col)
    point = 100 * (s1.sum() / n1.sum() - s0.sum() / n0.sum())
    rng = np.random.default_rng(cc.SEED)
    idx = rng.integers(0, len(s1), (cc.DRAWS, len(s1)))
    b = 100 * (s1[idx].sum(1) / n1[idx].sum(1) - s0[idx].sum(1) / n0[idx].sum(1))
    return {"shown_nonoptimal_pct": round(100 * s1.sum() / n1.sum(), 2), "hidden_nonoptimal_pct": round(100 * s0.sum() / n0.sum(), 2),
            "answers_shown": int(n1.sum()), "answers_hidden": int(n0.sum()),
            "gap_pp": round(float(point), 2), "ci95_tables_resampled": cc.ci(b)}


def main():
    df, info = cc.load_rows(["model_key", "assortment_id", "chose_optimal", "choice", "output_tokens", "response_length"])
    g = df[df.model_key == MODEL].copy()
    cap_len = g.output_tokens.max()
    g["capped"] = g.output_tokens >= cap_len
    g["nonopt"] = 1.0 - g.chose_optimal.astype(float)
    g["unparsed"] = g.choice.astype(str).str.strip() == "?"
    cap = g[g.capped]
    res = {"model": MODEL, "answers": int(len(g)), "cap_length_output_tokens": int(cap_len),
           "capped_answers": int(len(cap)), "capped_with_no_parsed_letter": int(cap.unparsed.sum()),
           "capped_by_condition": {"names_shown": int((cap.condition == cc.SHOWN).sum()), "names_hidden": int((cap.condition == cc.HIDDEN).sum())},
           "capped_share_by_condition_pct": {k: round(100 * float(g[g.condition == c].capped.mean()), 1) for k, c in (("names_shown", cc.SHOWN), ("names_hidden", cc.HIDDEN))},
           "capped_visible_text_characters_median": float(cap.response_length.median()),
           "best_product_rate_pct": {}, "gap": {}, "capped_by_table_top": {}}
    for label, c in (("names_shown", cc.SHOWN), ("names_hidden", cc.HIDDEN)):
        x = g[g.condition == c]
        res["best_product_rate_pct"][label] = {
            "capped": round(100 * float(x[x.capped].chose_optimal.astype(float).mean()), 1),
            "not_capped": round(100 * float(x[~x.capped].chose_optimal.astype(float).mean()), 1)}
    res["gap"]["all_answers"] = gap_with_ci(g, "nonopt")
    res["gap"]["capped_left_out"] = gap_with_ci(g[~g.capped], "nonopt")
    g2 = g.copy()
    g2.loc[g2.capped, "nonopt"] = 1.0
    res["gap"]["capped_counted_as_no_recommendation"] = gap_with_ci(g2, "nonopt")
    top = cap.groupby("assortment_id").size().sort_values(ascending=False)
    res["capped_by_table_top"] = {k: int(v) for k, v in top.head(8).items()}
    res["tables_with_a_capped_answer"] = int((top > 0).sum())
    cc.write_result("long_answers_gemini_2_5_pro", res, "study1b-64-models-on-34-tables/code/06_long_answers.py", info)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
