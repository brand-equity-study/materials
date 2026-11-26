"""Machine-based brand equity across releases of one developer's models, and how much a release changes it.

A brand's machine-based equity in a model is its share of the model's recommendations with brand names shown minus
its share with names hidden, on the same tables (12_brand_level.py, whose readers this script uses). All the models
here answered the same prompts: the corpus's 34 tables, 20 trials per table and condition; the Claude 5.5 models and
the open models answered the corpus's own prompts again (the rerun).

For each pair of releases (an earlier and a later model of one line from one developer):
  - each brand's change in equity (later minus earlier), with an interval that resamples the answers of every table,
    condition and model from its observed share (10,000 draws, seed 20261120);
  - how similar the two releases' brand orderings are (Spearman over the 73 brands; the brands resampled);
  - the mean absolute change over the brands, beside the mean absolute change that sampling alone gives when both
    releases share the same picking rates (the same draws), and the share of brands whose interval excludes zero;
  - the change in the release's overall gap (shown minus hidden share away from the best product), tables resampled.
A reference pair that is not a release, Gemma 4 31B through Google's API (corpus) and the same weights served with vLLM
(open rerun), shows how much equity moves when the model does not change.

    python web-appendix-analyses/brand-by-brand-and-release-by-release/code/13_brand_releases.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "common"))
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("brand_level", pathlib.Path(__file__).resolve().parent / "12_brand_level.py")
bl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bl)
cc = bl.cc

OUT = bl.OUT
PAIRS = [  # (developer, line, (source, model) earlier, (source, model) later)
    ("Anthropic", "Opus", ("corpus", "claude-opus-4.6"), ("corpus", "claude-opus-4.7")),
    ("Anthropic", "Opus", ("corpus", "claude-opus-4.7"), ("claude", "claude-opus-5-5")),
    ("Anthropic", "Opus", ("corpus", "claude-opus-4.6"), ("claude", "claude-opus-5-5")),
    ("Anthropic", "Haiku", ("corpus", "claude-haiku-4.5"), ("claude", "claude-haiku-5-5")),
    ("Anthropic", "Sonnet", ("corpus", "claude-sonnet-4.6"), ("claude", "claude-sonnet-5-5")),
    ("OpenAI", "GPT flagship", ("corpus", "gpt-4o"), ("corpus", "gpt-5.4")),
    ("OpenAI", "GPT mini", ("corpus", "gpt-4o-mini"), ("corpus", "gpt-4.1-mini")),
    ("OpenAI", "GPT mini", ("corpus", "gpt-4.1-mini"), ("corpus", "gpt-5-mini")),
    ("OpenAI", "GPT mini", ("corpus", "gpt-5-mini"), ("corpus", "gpt-5.4-mini")),
    ("OpenAI", "GPT nano", ("corpus", "gpt-4.1-nano"), ("corpus", "gpt-5.4-nano")),
    ("Google", "Gemini Flash", ("corpus", "gemini-2.0-flash"), ("corpus", "gemini-2.5-flash")),
    ("Google", "Gemini Flash", ("corpus", "gemini-2.5-flash"), ("corpus", "gemini-3-flash")),
    ("Google", "Gemini Flash-Lite", ("corpus", "gemini-2.5-flash-lite"), ("corpus", "gemini-3.1-flash-lite")),
    ("Google", "Gemini Pro", ("corpus", "gemini-2.5-pro"), ("corpus", "gemini-3.1-pro")),
    ("Google", "Gemma", ("corpus", "gemma-3-27b"), ("corpus", "gemma-4-31b-it")),
]
# the one release pair whose two models answered identical prompts (the rerun's items)
MATCHED = [("Alibaba", "Qwen, identical prompts", ("open", "qwen32b"), ("open", "qwen3-30b"))]
PROMPTS = {"corpus": "the model's own corpus trials", "claude": "the rerun's items (corpus prompts drawn in turn from the 30 models)",
           "open": "the rerun's items (corpus prompts drawn in turn from the 30 models)"}
REFERENCE = ("Google", "Gemma 4 31B, the same weights by two routes (not a release)", ("corpus", "gemma-4-31b-it"), ("open", "gemma31b"))


def cell_counts(c):
    """{(source, model): DataFrame indexed by (table, brand) with picks and answers for shown and hidden}."""
    g = c.groupby(["source", "model", "table", "brand", "condition"])[["picks", "answers"]].sum().unstack("condition")
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    return {k: v.droplevel([0, 1]) for k, v in g.groupby(level=[0, 1])}


def brand_equity_draws(cells, brands, rng, draws):
    """Point equity per brand, and draws in which every table's shown and hidden picks are redrawn from their shares."""
    point, sim = {}, {}
    for b in brands:
        x = cells.xs(b, level="brand")
        ks, ns, kh, nh = (x[c].to_numpy(float) for c in ("picks_shown", "answers_shown", "picks_hidden", "answers_hidden"))
        point[b] = 100 * (ks.sum() / ns.sum() - kh.sum() / nh.sum())
        s = rng.binomial(ns.astype(int), ks / ns, (draws, len(ns))).sum(1) / ns.sum()
        h = rng.binomial(nh.astype(int), kh / nh, (draws, len(nh))).sum(1) / nh.sum()
        sim[b] = 100 * (s - h)
    return pd.Series(point), pd.DataFrame(sim)


def null_draws(a, b, brands, rng, draws):
    """Both releases drawn from the same rates (the two releases' answers pooled): the change that sampling alone gives."""
    out = {}
    for br in brands:
        xa, xb = a.xs(br, level="brand"), b.xs(br, level="brand")
        ps = (xa.picks_shown + xb.picks_shown) / (xa.answers_shown + xb.answers_shown)
        ph = (xa.picks_hidden + xb.picks_hidden) / (xa.answers_hidden + xb.answers_hidden)

        def one(x):
            s = rng.binomial(x.answers_shown.to_numpy(int), ps.to_numpy(), (draws, len(x))).sum(1) / x.answers_shown.sum()
            h = rng.binomial(x.answers_hidden.to_numpy(int), ph.to_numpy(), (draws, len(x))).sum(1) / x.answers_hidden.sum()
            return 100 * (s - h)
        out[br] = one(xb) - one(xa)
    return pd.DataFrame(out)


def gap_rows(rows):
    """Per (source, model, table, condition): answers and answers away from the best product."""
    best = {t: next(L for L, p in v["products"].items() if p["is_optimal"]) for t, v in bl.TABLES.items()}
    d = pd.DataFrame(rows, columns=["source", "model", "table", "condition", "letter"])
    d["away"] = (d.letter != d.table.map(best)).astype(int)
    return d.groupby(["source", "model", "table", "condition"]).away.agg(["sum", "count"])


def gap_change(gr, a, b, rng, draws):
    ta = gr.loc[a].unstack("condition")
    tb = gr.loc[b].unstack("condition")
    tables = sorted(set(ta.index) & set(tb.index))
    ta, tb = ta.loc[tables], tb.loc[tables]

    def g(t, idx=None):
        s1, n1, s0, n0 = (t[(c, k)].to_numpy(float) for k in ("shown", "hidden") for c in ("sum", "count"))
        if idx is None:
            return 100 * (s1.sum() / n1.sum() - s0.sum() / n0.sum())
        return 100 * (s1[idx].sum(1) / n1[idx].sum(1) - s0[idx].sum(1) / n0[idx].sum(1))
    idx = rng.integers(0, len(tables), (draws, len(tables)))
    return {"earlier_gap": round(float(g(ta)), 2), "later_gap": round(float(g(tb)), 2), "change": round(float(g(tb) - g(ta)), 2),
            "change_ci95_tables_resampled": cc.ci(g(tb, idx) - g(ta, idx))}


def compare(pair, cells, gr, brands, draws=cc.DRAWS):
    dev, line, a, b = pair
    rng = np.random.default_rng(cc.SEED)
    pa, sa = brand_equity_draws(cells[a], brands, rng, draws)
    pb, sb = brand_equity_draws(cells[b], brands, rng, draws)
    change = pb - pa
    lo, hi = (sb - sa).quantile(0.025), (sb - sa).quantile(0.975)
    nd = null_draws(cells[a], cells[b], brands, rng, draws)
    obs_mac = float(change.abs().mean())
    null_mac = nd.abs().mean(axis=1)
    boot = []
    for _ in range(2000):
        i = rng.integers(0, len(brands), len(brands))
        boot.append(pd.Series(pa.to_numpy()[i]).rank().corr(pd.Series(pb.to_numpy()[i]).rank()))
    top = change.reindex(change.abs().sort_values(ascending=False).index[:6])
    same = a[0] != "corpus" and b[0] != "corpus"
    return {"developer": dev, "line": line, "earlier": f"{a[1]} ({a[0]})", "later": f"{b[1]} ({b[0]})",
            "prompts": ("identical: both models answered the rerun's items" if same else
                        f"the same 34 tables, conditions and number of trials, but different prompts (display order, letters "
                        f"and wording drawn separately): earlier {PROMPTS[a[0]]}, later {PROMPTS[b[0]]}"),
            "_earlier": pa, "_noise_var": sa.var(axis=0),
            "spearman_brand_equity": round(float(pa.rank().corr(pb.rank())), 3),
            "spearman_ci95_brands_resampled_2000": cc.ci(np.array([x for x in boot if x == x]), 1, 3),
            "mean_absolute_change_points": round(obs_mac, 2),
            "mean_absolute_change_from_sampling_alone": {"mean": round(float(null_mac.mean()), 2), "ci95": cc.ci(null_mac.to_numpy())},
            "p_observed_above_sampling": round(float((1 + (null_mac >= obs_mac).sum()) / (1 + draws)), 4),
            "brands_whose_change_excludes_zero": int(((lo > 0) | (hi < 0)).sum()), "brands": len(brands),
            "largest_changes": {k: {"change": round(float(v), 2), "earlier": round(float(pa[k]), 2), "later": round(float(pb[k]), 2),
                                    "ci95": [round(float(lo[k]), 2), round(float(hi[k]), 2)]} for k, v in top.items()},
            "overall_gap": gap_change(gr, a, b, rng, draws),
            "_change": change, "_lo": lo, "_hi": hi}


def feedback(d, brands, draws=2000):
    """Is machine-based brand equity self-reinforcing across releases? A brand's change in equity is regressed on its
    equity in the earlier release, within each release pair (pair fixed effects), with standard errors clustered by
    brand and by pair. Noise alone gives a negative slope (regression to the mean); the same-weights reference
    (Gemma 4 31B by two routes, no release) measures that slope. A release slope above the reference's means that
    brands with high equity kept more of it than noise predicts (amplification); below it, that they fell back further
    (mean reversion beyond noise). The interval of the difference resamples brands (2,000 draws, seed 20261120)."""
    import statsmodels.formula.api as smf
    rel = d[d.kind == "release"].copy()
    ref = d[d.kind == "reference"].copy()
    groups = np.column_stack([pd.factorize(rel.brand)[0], pd.factorize(rel.pair)[0]])
    fit = smf.ols("change ~ earlier_equity + C(pair)", data=rel).fit(cov_type="cluster", cov_kwds={"groups": groups})
    fit_ref = smf.ols("change ~ earlier_equity", data=ref).fit(cov_type="HC1")

    def within_slope(x):
        xe = x.earlier_equity - x.groupby("pair").earlier_equity.transform("mean")
        ye = x.change - x.groupby("pair").change.transform("mean")
        den = float((xe * xe).sum())
        return float((xe * ye).sum()) / den if den > 0 else np.nan

    rng = np.random.default_rng(cc.SEED)
    by_rel, by_ref = dict(tuple(rel.groupby("brand"))), dict(tuple(ref.groupby("brand")))
    diffs, rels, refs = [], [], []
    for _ in range(draws):
        bs = rng.choice(brands, len(brands))
        s1 = within_slope(pd.concat([by_rel[b] for b in bs]))
        s2 = within_slope(pd.concat([by_ref[b] for b in bs]))
        if np.isfinite(s1) and np.isfinite(s2):
            diffs.append(s1 - s2)
            rels.append(s1)
            refs.append(s2)
    def noise_test(x):
        """The slope that sampling noise alone gives when nothing changes (minus the earlier equity's sampling variance
        over its variance across brands, within pairs; a lower bound on the noise, since different prompt draws add
        more), the observed within-pair slope minus it, and the difference's interval and p-value (brands resampled)."""
        xe = x.earlier_equity - x.groupby("pair").earlier_equity.transform("mean")
        noise = -float(x.earlier_noise_var.sum() / (xe * xe).sum())
        obs = within_slope(x)
        bb = dict(tuple(x.groupby("brand")))
        keys = sorted(bb)
        nb = []
        for _ in range(draws):
            bs = rng.choice(keys, len(keys))
            y = pd.concat([bb[b] for b in bs])
            xx = y.earlier_equity - y.groupby("pair").earlier_equity.transform("mean")
            yy = y.change - y.groupby("pair").change.transform("mean")
            den = float((xx * xx).sum())
            if den > 0:
                nb.append(float((xx * yy).sum()) / den + float(y.earlier_noise_var.sum()) / den)
        return {"sampling_noise_slope": round(noise, 3), "slope_minus_sampling_noise_slope": round(obs - noise, 3),
                "slope_minus_sampling_noise_slope_ci95_brands_resampled": cc.ci(np.array(nb), 1, 3),
                "slope_minus_sampling_noise_slope_p_two_sided": cc.p_two_sided(nb)}

    pooled_noise = noise_test(rel)  # first, so that its draws are those of the earlier run
    dev = {}
    for dv, g in rel.groupby("developer"):
        gg = np.column_stack([pd.factorize(g.brand)[0], pd.factorize(g.pair)[0]])
        f = smf.ols("change ~ earlier_equity + C(pair)", data=g).fit(cov_type="cluster", cov_kwds={"groups": gg})
        dev[dv] = dict({"slope": round(float(f.params["earlier_equity"]), 3), "ci95": [round(float(v), 3) for v in f.conf_int().loc["earlier_equity"]],
                        "p_two_sided": float(f"{f.pvalues['earlier_equity']:.4g}"), "pairs": int(g.pair.nunique())}, **noise_test(g))
    m = d[d.kind == "matched"]
    out = {"release_slope": round(float(fit.params["earlier_equity"]), 3),
           "release_slope_p_two_sided_clustered": float(f"{fit.pvalues['earlier_equity']:.4g}"),
           "sampling_noise_slope": pooled_noise["sampling_noise_slope"],
           "release_slope_minus_sampling_noise_slope": pooled_noise["slope_minus_sampling_noise_slope"],
           "release_slope_minus_sampling_noise_slope_ci95_brands_resampled": pooled_noise["slope_minus_sampling_noise_slope_ci95_brands_resampled"],
           "release_slope_minus_sampling_noise_slope_p_two_sided": pooled_noise["slope_minus_sampling_noise_slope_p_two_sided"],
           "release_slope_ci95_clustered_brand_and_pair": [round(float(v), 3) for v in fit.conf_int().loc["earlier_equity"]],
           "reference_slope": round(float(fit_ref.params["earlier_equity"]), 3),
           "reference_slope_ci95": [round(float(v), 3) for v in fit_ref.conf_int().loc["earlier_equity"]],
           "reference_slope_p_two_sided": float(f"{fit_ref.pvalues['earlier_equity']:.4g}"),
           "difference_release_minus_reference": round(float(fit.params["earlier_equity"] - fit_ref.params["earlier_equity"]), 3),
           "difference_ci95_brands_resampled": cc.ci(np.array(diffs), 1, 3),
           "difference_p_two_sided": cc.p_two_sided(diffs),
           "rows": int(len(rel)), "pairs": int(rel.pair.nunique()), "brands": int(rel.brand.nunique()),
           "by_developer": dev,
           "matched_prompt_pair_slope": round(within_slope(m), 3) if len(m) else None,
           "matched_prompt_pair_noise_test": noise_test(m) if len(m) else None,
           "reading": "above zero: amplification; below zero: mean reversion beyond noise; an interval that includes zero: neither",
           "clustering_note": "brand-level equity pools a brand's tables, so the clusters are brands and release pairs"}
    lo, hi = out["release_slope_minus_sampling_noise_slope_ci95_brands_resampled"]
    out["verdict_against_sampling_noise"] = ("amplification" if lo > 0 else "mean reversion beyond sampling noise" if hi < 0
                                             else "neither (the interval includes zero)")
    out["reference_note"] = ("the same-weights reference does not show noise alone: its slope is positive because served with vLLM "
                             "the brands with high equity through Google's API had higher equity still, a change of scale "
                             "between the two routes; it is reported, not used as the benchmark")
    return out


def main():
    items = bl.rerun_items()
    crows, info = bl.corpus_rows()
    rows = crows + [r for r in bl.claude_rows(items) if r[0] == "claude"]
    orows, ofiles = bl.open_rows(items)
    rows += [r for r in orows if r[0] == "open"]
    c = bl.counts_from_picks(rows)
    cells = cell_counts(c)
    brands = sorted(c.brand.unique())
    gr = gap_rows(rows)
    res = {"definition": "equity = 100 x (share picking the brand's product, names shown, minus names hidden), the brand's tables pooled; "
                         "change = later release minus earlier release", "brands": len(brands), "open_models_file": ofiles,
           "pairs": [], "corpus_input": info}
    table = []
    fb_rows = []
    res["matched_prompts"] = []
    for pair in PAIRS + MATCHED + [REFERENCE]:
        r = compare(pair, cells, gr, brands)
        for b in brands:
            table.append({"developer": r["developer"], "line": r["line"], "earlier": r["earlier"], "later": r["later"], "brand": b,
                          "change": round(float(r["_change"][b]), 3), "ci_low": round(float(r["_lo"][b]), 3), "ci_high": round(float(r["_hi"][b]), 3)})
            fb_rows.append({"pair": f"{r['earlier']} -> {r['later']}", "developer": r["developer"], "brand": b,
                            "earlier_equity": float(r["_earlier"][b]), "change": float(r["_change"][b]),
                            "earlier_noise_var": float(r["_noise_var"][b]),
                            "kind": "reference" if pair is REFERENCE else "matched" if pair in MATCHED else "release"})
        clean = {k: v for k, v in r.items() if not k.startswith("_")}
        if pair is REFERENCE:
            res["reference_same_weights_two_routes"] = clean
        elif pair in MATCHED:
            res["matched_prompts"].append(clean)
        else:
            res["pairs"].append(clean)
    res["feedback"] = feedback(pd.DataFrame(fb_rows), brands)
    res["note"] = ("the Claude 4.x models in the corpus ran at temperature 1.0; the Claude 5.5 models at the provider's defaults; "
                   "the open models at their own sampling settings (study1a-tables-with-one-optimal-product/data/open-models/RUNS.csv)")
    pd.DataFrame(table).to_csv(OUT / "brand_release_changes.csv", index=False, lineterminator="\n")
    res["_meta"] = {"script": "web-appendix-analyses/brand-by-brand-and-release-by-release/code/13_brand_releases.py", "draws": cc.DRAWS, "seed": cc.SEED,
                    "files_written": ["releases.json", "brand_release_changes.csv"]}
    with open(OUT / "releases.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(json.loads(json.dumps(res, default=cc._plain)), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("feedback", json.dumps(res["feedback"], default=cc._plain))
    for p in res["pairs"] + res["matched_prompts"] + [res["reference_same_weights_two_routes"]]:
        print(f"{p['earlier']:38s} -> {p['later']:38s} rho {p['spearman_brand_equity']:+.2f} {p['spearman_ci95_brands_resampled_2000']} "
              f"MAC {p['mean_absolute_change_points']:.2f} (null {p['mean_absolute_change_from_sampling_alone']['mean']:.2f} "
              f"{p['mean_absolute_change_from_sampling_alone']['ci95']}) P {p['p_observed_above_sampling']} "
              f"excl0 {p['brands_whose_change_excludes_zero']} gap {p['overall_gap']['earlier_gap']}->{p['overall_gap']['later_gap']} "
              f"{p['overall_gap']['change_ci95_tables_resampled']} top {list(p['largest_changes'].items())[:2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
