"""Machine-based brand equity, brand by brand.

For each familiar brand in the 34 tables and each model, machine-based brand equity is how much more often the model
recommends that brand's product when the brand names are shown than when they are hidden, on the same tables:

    equity (points) = 100 x (share of answers that pick the brand's product with names shown
                             - share of answers that pick it with names hidden)

A brand that appears in several tables is pooled over them (answers summed). Every answer counts in the denominator,
as in 01_names_gap.py, so an answer without a letter counts as not picking the brand.

Sources:
  corpus  the 30-model corpus (study1b-64-models-on-34-tables/data/corpus), names shown and names hidden, 20 trials per table and condition;
          the picked product is the corpus's original_choice, the product's letter in the table as
          experiment/assortments.py defines it (checked: original_optimal is the table's best product in every row)
  claude  the rerun on Claude Fable 5.1, Haiku 5.5, Opus 5.5 and Sonnet 5.5 (study1b-64-models-on-34-tables/data/rerun, shown and hidden)
  open    the ten open models' answers to the rerun's prompts (study1a-tables-with-one-optimal-product/data/open-models/rerun)

Brand-level covariates:
  frequency in public training text: web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_frequency.csv (the brand beside its category, summed over
    C4, the Pile, RedPajama and Dolma, log; and the brand name alone, log)
  Wikipedia page views: web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_wikipedia_pageviews.csv (log10 of the monthly mean)
  coded familiarity: brand_familiarity in experiment/assortments.py (high or medium; per table)
  consumer familiarity: the chat study (study4-peoples-choices-after-a-recommendation/data/chat_experiment.csv): participants rated their familiarity with the
    brand that they chose (1 to 5); the mean for each brand that participants chose
  published brand value: web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_value_rankings.csv (Interbrand Best Global Brands and Kantar BrandZ,
    2024 and 2025; each row names its source and the date it was read)

Intervals: a brand's pooled equity resamples the models with replacement and, within each drawn model, the answers
(binomial), 10,000 draws, seed 20261120. One brand in one model: Newcombe's interval for a difference of two shares.
Correlations across brands: the brands resampled with replacement. Regressions: one row per brand, table and model,
with the table's category held fixed and standard errors clustered two ways, by brand and by model.

    python web-appendix-analyses/brand-by-brand-and-release-by-release/code/12_brand_level.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "common"))
import collections
import json
import math
import pathlib
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
REPO = pathlib.Path(__file__).resolve().parents[3]  # the top of the replication package
sys.path.append(str(REPO))
sys.path.append(str(REPO / "common"))
sys.dont_write_bytecode = True
import common as cc  # noqa: E402
from experiment.assortments import ALL_ASSORTMENTS  # noqa: E402
from parse_answer import final_answer, pick  # noqa: E402  (the parser of Study 1: final_answer, then pick)

OUT = REPO / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "results" / "brand_level"
RERUN_ITEMS = REPO / "study1b-64-models-on-34-tables" / "materials" / "rerun" / "prompts.jsonl.gz"
RERUN_ANSWERS = REPO / "study1b-64-models-on-34-tables" / "data" / "rerun"
OPEN_RERUN_ANSWERS = REPO / "study1a-tables-with-one-optimal-product" / "data" / "open-models" / "rerun"
FREQ = REPO / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "materials" / "brand_frequency.csv"
VIEWS = REPO / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "materials" / "brand_wikipedia_pageviews.csv"
CHATBOT = REPO / "study4-peoples-choices-after-a-recommendation" / "data" / "chat_experiment.csv"
RANKINGS = REPO / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "materials" / "brand_value_rankings.csv"
OPEN_MODELS = ["gemma31b", "gemma4-26b", "granite41-30b", "llama8b", "marin8b", "ministral3-14b", "olmo31-32b", "phi4",
               "qwen3-30b", "qwen32b"]  # the ten open models of the brand-level results
FAMILY = {"claude": "Anthropic", "gpt": "OpenAI", "gemini": "Google", "gemma": "Google", "deepseek": "other open-weight developers",
          "kimi": "other open-weight developers", "llama": "other open-weight developers", "qwen": "other open-weight developers"}

TABLES = {a["id"]: {"category": a["category"], "products": {p["letter"]: p for p in a["products"]}} for a in ALL_ASSORTMENTS}


def family(model_key):
    return next(v for k, v in FAMILY.items() if model_key.startswith(k))


# ---------------------------------------------------------------- picks by brand

def counts_from_picks(rows):
    """rows: (source, model, table, condition 'shown'/'hidden', picked original letter or '') ->
    DataFrame of picks and answers per source, model, table, brand and condition (familiar brands only)."""
    n = collections.Counter()
    k = collections.Counter()
    for src, m, t, cond, L in rows:
        n[(src, m, t, cond)] += 1
        if L:
            k[(src, m, t, cond, TABLES[t]["products"][L]["brand"])] += 1
    out = []
    for (src, m, t, cond), nn in n.items():
        brands = {p["brand"] for p in TABLES[t]["products"].values() if p["brand_familiarity"] != "low"}
        for b in brands:
            out.append({"source": src, "model": m, "table": t, "brand": b, "condition": cond, "picks": k[(src, m, t, cond, b)], "answers": nn})
    return pd.DataFrame(out)


def corpus_rows():
    df, info = cc.load_rows(["model_key", "assortment_id", "original_choice", "original_optimal"])
    best = {t: next(L for L, p in v["products"].items() if p["is_optimal"]) for t, v in TABLES.items()}
    bad = (df.original_optimal != df.assortment_id.map(best)).sum()
    if bad:
        raise SystemExit(f"{bad} corpus rows: original_optimal is not the table's best product; the letters do not map")
    cond = np.where(df.condition == cc.SHOWN, "shown", "hidden")
    L = df.original_choice.astype(str).where(df.original_choice.astype(str).isin(list("ABCDE")), "")
    return [("corpus", m, t, c, l) for m, t, c, l in zip(df.model_key, df.assortment_id, cond, L)], info


def rerun_items():
    return {it["id"]: it for it in cc.read_jsonl_gz(RERUN_ITEMS).to_dict("records")}


def rerun_letter(it, letter):
    """The table letter (as in experiment/assortments.py) of the product that a rerun item shows under `letter`."""
    if not letter:
        return ""
    p = it["products"][letter]
    orig = p["orig"]
    if TABLES[it["table"]]["products"][orig]["brand"] != p["true_brand"]:
        raise SystemExit(f"item {it['id']}: the product's brand does not match the table")
    return orig


CLAUDE_API_MODELS = ("claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5")  # answered through the API


def claude_rows(items):
    rows = []
    for mdir in sorted(p for p in RERUN_ANSWERS.iterdir() if p.is_dir() and p.name in CLAUDE_API_MODELS):
        answers = [a for f in sorted(mdir.glob("*.jsonl.gz")) for a in cc.read_jsonl_gz(f).to_dict("records")]
        for a in answers:
            it = items.get(a["id"])
            if it is None or it["names"] not in ("shown", "hidden"):
                continue
            L, _ = pick(final_answer(a["answer_text"]))
            rows.append(("claude", mdir.name, it["table"], it["names"], rerun_letter(it, L)))
            if it["names"] == "shown":
                rows.append(("claude_clean", mdir.name, it["table"], "shown", rerun_letter(it, L)))
        for a in answers:  # names hidden with the leaks cleaned, against the same names-shown answers
            it = items.get(a["id"])
            if it is not None and it["names"] == "hidden_clean":
                L, _ = pick(final_answer(a["answer_text"]))
                rows.append(("claude_clean", mdir.name, it["table"], "hidden", rerun_letter(it, L)))
    return rows


def leaked_brands():
    """Brands whose names-hidden prompt gave away the brand in some table (kinds 1 to 4 of names_hidden_leaks.csv)."""
    d = pd.read_csv(REPO / "study1b-64-models-on-34-tables" / "materials" / "names_hidden_leaks.csv")
    d = d[~d.kind.str.startswith("5")]
    return d.groupby("points_to").size().rename("leak_rows")


def open_rows(items):
    """The open models' answers to the rerun's prompts, with the letter that the parser of Study 1 reads (final_answer,
    then pick); the ten open models of the brand-level results."""
    if sorted(p.name for p in OPEN_RERUN_ANSWERS.iterdir() if p.is_dir()) != sorted(OPEN_MODELS):
        raise SystemExit("study1a-tables-with-one-optimal-product/data/open-models/rerun does not hold exactly the ten open models of the brand-level results")
    rows = []
    for f in sorted(OPEN_RERUN_ANSWERS.glob("*/*.jsonl.gz")):
        for a in cc.read_jsonl_gz(f).to_dict("records"):
            it = items[a["id"]]
            L = rerun_letter(it, pick(final_answer(a["answer_text"]))[0])
            if it["names"] in ("shown", "hidden"):
                rows.append(("open", a["model"], it["table"], it["names"], L))
            if it["names"] == "shown":
                rows.append(("open_clean", a["model"], it["table"], "shown", L))
            if it["names"] == "hidden_clean":
                rows.append(("open_clean", a["model"], it["table"], "hidden", L))
    return rows, ["study1a-tables-with-one-optimal-product/data/open-models/rerun/"]


# ---------------------------------------------------------------- equity

def per_model(c):
    """Equity per source, model and brand (the brand's tables pooled), with the four counts."""
    g = c.groupby(["source", "model", "brand", "condition"])[["picks", "answers"]].sum().unstack("condition")
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.reset_index()
    g["share_shown"] = g.picks_shown / g.answers_shown
    g["share_hidden"] = g.picks_hidden / g.answers_hidden
    g["equity"] = 100 * (g.share_shown - g.share_hidden)
    lo, hi = zip(*[newcombe(a, b, c_, d) for a, b, c_, d in zip(g.picks_shown, g.answers_shown, g.picks_hidden, g.answers_hidden)])
    g["ci_low"], g["ci_high"] = lo, hi
    return g


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def newcombe(k1, n1, k2, n2):
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    p1, p2 = k1 / n1, k2 / n2
    d = p1 - p2
    return round(100 * (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)), 2), round(100 * (d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)), 2)


def pooled(pm, source, rng_seed=cc.SEED):
    """A brand's equity pooled over a source's models (equal weight per model), with the two-stage interval."""
    rng = np.random.default_rng(rng_seed)
    out = {}
    for b, g in pm[pm.source == source].groupby("brand"):
        ks, ns, kh, nh = (g[c].to_numpy(float) for c in ("picks_shown", "answers_shown", "picks_hidden", "answers_hidden"))
        m = len(g)
        idx = rng.integers(0, m, (cc.DRAWS, m))
        s = rng.binomial(ns[idx].astype(int), (ks / ns)[idx]) / ns[idx]
        h = rng.binomial(nh[idx].astype(int), (kh / nh)[idx]) / nh[idx]
        draws = 100 * (s - h).mean(1)
        out[b] = {"equity": round(float(g.equity.mean()), 2), "ci95": cc.ci(draws), "p_two_sided": cc.p_two_sided(draws), "models": m,
                  "share_shown_pct": round(100 * float(g.share_shown.mean()), 2), "share_hidden_pct": round(100 * float(g.share_hidden.mean()), 2),
                  "models_above_zero": int((g.equity > 0).sum()), "answers": int(g.answers_shown.sum() + g.answers_hidden.sum())}
    return out


# ---------------------------------------------------------------- covariates

def covariates():
    f = pd.read_csv(FREQ)
    f = f[~f.is_fictional.astype(bool)]
    v = pd.read_csv(VIEWS)
    v = v[v.article_exists.astype(bool)]
    slots = []
    for t, tv in TABLES.items():
        for p in tv["products"].values():
            if p["brand_familiarity"] == "low":
                continue
            fr = f[(f.brand_name == p["brand"]) & (f.category == tv["category"])]
            slots.append({"table": t, "category": tv["category"], "brand": p["brand"], "coded_high": int(p["brand_familiarity"] == "high"),
                          "log_freq_with_category": float(fr.log_cat_freq.iloc[0]) if len(fr) else np.nan,
                          "log_freq_name_alone": float(fr.log_brand_only.iloc[0]) if len(fr) else np.nan})
    s = pd.DataFrame(slots).drop_duplicates(["table", "brand"])
    b = s.groupby("brand").agg(category_count=("category", "nunique"), tables=("table", "nunique"), coded_high_share=("coded_high", "mean"),
                                log_freq_with_category=("log_freq_with_category", "mean"), log_freq_name_alone=("log_freq_name_alone", "mean"))
    b["log10_wikipedia_monthly_views"] = np.log10(v.set_index("brand").avg_monthly.reindex(b.index))
    b["leak_rows_names_hidden"] = leaked_brands().reindex(b.index).fillna(0).astype(int)
    b = b.join(consumer_familiarity(), how="left")
    rk = rankings()
    if rk is not None:
        b = b.join(rk, how="left")
        b["in_a_value_ranking"] = b["in_a_value_ranking"].fillna(0).astype(int)
    return s, b


def consumer_familiarity():
    d = pd.read_csv(CHATBOT, low_memory=False)
    out = collections.defaultdict(list)
    for s, choice, fam in zip(d.study3_assortment, d.study3_product_choice, d.dv_brand_familiar):
        try:
            j = json.loads(s)
        except (TypeError, ValueError):
            continue
        for p in j["products"]:
            if isinstance(choice, str) and choice.strip() == f"{p['brand']} {p['model']}".strip():
                out[p["brand"]].append(fam)
                break
    r = pd.DataFrame({"consumer_familiarity_mean": {k: float(np.mean(v)) for k, v in out.items()},
                      "consumer_familiarity_n": {k: len(v) for k, v in out.items()}})
    return r


def rankings():
    if not RANKINGS.exists():
        return None
    r = pd.read_csv(RANKINGS)
    r = r[r.appears.astype(str).str.lower() == "yes"]
    if r.empty:
        return pd.DataFrame(columns=["in_a_value_ranking"])
    g = r.groupby("brand").agg(best_rank=("rank", "min"), value_usd_millions_mean=("value_usd_millions", "mean"), lists=("list", "nunique"))
    g["log10_brand_value"] = np.log10(g.value_usd_millions_mean)
    g["in_a_value_ranking"] = 1
    return g


# ---------------------------------------------------------------- relations

def correlations(eq, b, cols, draws=cc.DRAWS):
    rng = np.random.default_rng(cc.SEED)
    out = {}
    for c in cols:
        x = pd.concat([eq.rename("equity"), b[c]], axis=1).dropna()
        if len(x) < 5:
            out[c] = {"brands": len(x), "note": "fewer than 5 brands"}
            continue
        sp = x.rank().corr().iloc[0, 1]
        pe = x.corr().iloc[0, 1]
        idx = rng.integers(0, len(x), (draws, len(x)))
        a, bb = x.equity.to_numpy(), x[c].to_numpy()
        boot = [pd.Series(a[i]).rank().corr(pd.Series(bb[i]).rank()) for i in idx[:2000]]
        out[c] = {"brands": len(x), "spearman": round(float(sp), 3), "spearman_ci95_brands_resampled_2000": cc.ci(np.array([v for v in boot if v == v]), 1, 3),
                  "spearman_p_two_sided": cc.p_two_sided(boot),
                  "pearson": round(float(pe), 3)}
    return out


def regressions(pm_slot, s, b):
    """One row per brand, table and model (corpus): equity on the covariates, category fixed, two-way clustered."""
    d = pm_slot.merge(s, on=["table", "brand"], how="left").merge(b.reset_index(), on="brand", how="left", suffixes=("", "_b"))
    d["z_freq"] = (d.log_freq_with_category - d.log_freq_with_category.mean()) / d.log_freq_with_category.std()
    d["z_views"] = (d.log10_wikipedia_monthly_views - d.log10_wikipedia_monthly_views.mean()) / d.log10_wikipedia_monthly_views.std()
    # the product's appeal on its specifications: its share of all 30 models' names-hidden answers in that table
    ap = pm_slot.groupby(["table", "brand"]).apply(lambda g: g.picks_hidden.sum() / g.answers_hidden.sum(), include_groups=False).rename("appeal")
    d = d.merge(ap.reset_index(), on=["table", "brand"], how="left")
    d["z_appeal"] = (d.appeal - d.appeal.mean()) / d.appeal.std()
    specs = {"frequency": "equity ~ z_freq + C(category)",
             "frequency and coded familiarity": "equity ~ z_freq + coded_high + C(category)",
             "frequency, coded familiarity and page views": "equity ~ z_freq + coded_high + z_views + C(category)"}
    if "in_a_value_ranking" in d:
        specs["frequency, coded familiarity and a published brand value"] = "equity ~ z_freq + coded_high + in_a_value_ranking + C(category)"
    cf = d.consumer_familiarity_mean.where(d.consumer_familiarity_n >= 3)
    d["z_consumer_familiarity"] = (cf - cf.mean()) / cf.std()
    specs["frequency, coded familiarity and consumer familiarity (brands chosen by 3 or more chatbot participants)"] = \
        "equity ~ z_freq + coded_high + z_consumer_familiarity + C(category)"
    specs["exploratory: frequency, coded familiarity, a published brand value and the product's appeal with names hidden"] = \
        "equity ~ z_freq + coded_high + in_a_value_ranking + z_appeal + C(category)" if "in_a_value_ranking" in d else "equity ~ z_freq + coded_high + z_appeal + C(category)"
    out = {}
    for name, f in specs.items():
        x = d.dropna(subset=[t for t in ("z_freq", "coded_high", "z_views", "in_a_value_ranking", "z_consumer_familiarity", "z_appeal") if t in f])
        groups = np.column_stack([pd.factorize(x.brand)[0], pd.factorize(x.model)[0]])
        fit = smf.ols(f, data=x).fit(cov_type="cluster", cov_kwds={"groups": groups})
        terms = [t for t in fit.params.index if not t.startswith("C(") and t != "Intercept"]
        out[name] = {"rows": int(fit.nobs), "brands": int(x.brand.nunique()), "models": int(x.model.nunique()),
                     "terms": {t: {"coef": round(float(fit.params[t]), 3), "se": round(float(fit.bse[t]), 3),
                                   "ci95": [round(float(v), 3) for v in fit.conf_int().loc[t]], "p": float(f"{fit.pvalues[t]:.3g}")} for t in terms},
                     "r2": round(float(fit.rsquared), 3)}
    return out


def family_test(pm, b, permutations=2000):
    """Do brands differ in equity across the developers' model families beyond each brand's and each family's average?
    The statistic is the sum of squared brand-by-family interaction terms of the family means; family labels are
    permuted across the corpus's 30 models (group sizes kept)."""
    c = pm[pm.source == "corpus"].copy()
    c["family"] = c.model.map(family)
    wide = c.pivot(index="model", columns="brand", values="equity")
    fam = pd.Series({m: family(m) for m in wide.index})

    def stat(labels, cols):
        x = wide[cols]
        means = x.groupby(labels.to_numpy()).mean()
        inter = means.sub(means.mean(axis=1), axis=0).sub(means.mean(axis=0), axis=1) + means.to_numpy().mean()
        return float((inter.to_numpy() ** 2).sum()), means

    rng = np.random.default_rng(cc.SEED)
    out = {}
    strata = {"all familiar brands": list(wide.columns),
              "brands coded high familiarity in every table": [x for x in wide.columns if b.loc[x, "coded_high_share"] == 1],
              "brands coded medium familiarity in every table": [x for x in wide.columns if b.loc[x, "coded_high_share"] == 0]}
    if "in_a_value_ranking" in b:
        strata["brands in a published brand-value ranking"] = [x for x in wide.columns if b.loc[x, "in_a_value_ranking"] == 1]
    for name, cols in strata.items():
        if len(cols) < 3:
            out[name] = {"brands": len(cols), "note": "fewer than 3 brands"}
            continue
        obs, means = stat(fam, cols)
        perm = np.array([stat(pd.Series(rng.permutation(fam.to_numpy()), index=fam.index), cols)[0] for _ in range(permutations)])
        cor = means.T.rank().corr()
        out[name] = {"brands": len(cols), "interaction_sum_of_squares": round(obs, 1),
                     "p_permutation": round(float((1 + (perm >= obs).sum()) / (1 + permutations)), 4), "permutations": permutations,
                     "family_models": {k: int(v) for k, v in fam.value_counts().items()},
                     "spearman_between_families_over_brands": {f"{a} | {bb}": round(float(cor.loc[a, bb]), 3)
                                                               for i, a in enumerate(cor.index) for bb in cor.columns[i + 1:]}}
    return out


def main():
    items = rerun_items()
    crows, info = corpus_rows()
    rows = crows + claude_rows(items)
    orows, ofiles = open_rows(items)
    rows += orows
    c = counts_from_picks(rows)
    pm = per_model(c)
    s, b = covariates()
    res = {"definition": "equity = 100 x (share of answers picking the brand's product with names shown minus with names hidden), "
                         "the brand's tables pooled; pooled over models with equal weight per model",
           "sources": {"corpus": "30 models, 20 trials per table and condition", "claude": "the rerun on four Claude models",
                       "open": ofiles},
           "brands": int(c.brand.nunique()), "corpus_input": info}
    for src in sorted(pm.source.unique()):
        res[f"pooled_{src}"] = pooled(pm, src)
    eq = pd.Series({k: v["equity"] for k, v in res["pooled_corpus"].items()})
    cols = ["log_freq_with_category", "log_freq_name_alone", "log10_wikipedia_monthly_views", "coded_high_share", "consumer_familiarity_mean",
            "leak_rows_names_hidden"]
    if "log10_brand_value" in b:
        cols += ["log10_brand_value", "best_rank", "in_a_value_ranking"]
    res["correlations_corpus_brands"] = correlations(eq, b, cols)
    for src in ("claude", "open"):
        if f"pooled_{src}" in res:
            eq_c = pd.Series({k: v["equity"] for k, v in res[f"pooled_{src}"].items()})
            res[f"correlations_{src}_brands"] = correlations(eq_c, b, cols)
            res[f"corpus_vs_{src}_spearman"] = round(float(pd.concat([eq, eq_c], axis=1).dropna().rank().corr().iloc[0, 1]), 3)
    if "pooled_claude" in res and "pooled_open" in res:
        a_ = pd.Series({k: v["equity"] for k, v in res["pooled_claude"].items()})
        o_ = pd.Series({k: v["equity"] for k, v in res["pooled_open"].items()})
        res["claude_vs_open_spearman"] = round(float(pd.concat([a_, o_], axis=1).dropna().rank().corr().iloc[0, 1]), 3)
    cf = b[b.consumer_familiarity_n.fillna(0) >= 3]
    res["consumer_familiarity_coverage"] = {"brands_chosen_by_3_or_more_participants": int(len(cf)),
                                            "brands_chosen_at_all": int(b.consumer_familiarity_n.notna().sum()),
                                            "note": "the chat study's tables were generated for each participant, so few of the 73 brands were chosen often"}
    slot = c[c.source == "corpus"].groupby(["model", "table", "brand", "condition"])[["picks", "answers"]].sum().unstack("condition")
    slot.columns = [f"{x}_{y}" for x, y in slot.columns]
    slot = slot.reset_index()
    slot["equity"] = 100 * (slot.picks_shown / slot.answers_shown - slot.picks_hidden / slot.answers_hidden)
    res["regressions_corpus"] = regressions(slot, s, b)
    res["families_corpus"] = family_test(pm, b)
    fm = pm[pm.source == "corpus"].assign(family=lambda z: z.model.map(family)).groupby(["brand", "family"]).equity.mean().unstack()
    rng_ = (fm.max(axis=1) - fm.min(axis=1)).sort_values(ascending=False)
    res["largest_differences_between_families"] = [
        {"brand": x, "range_points": round(float(rng_[x]), 2), "coded_high_share": float(b.loc[x, "coded_high_share"]),
         "by_family": {f: round(float(v), 2) for f, v in fm.loc[x].items()},
         "in_a_value_ranking": int(b.loc[x, "in_a_value_ranking"]) if "in_a_value_ranking" in b else None} for x in rng_.index[:12]]
    lk = (b.leak_rows_names_hidden > 0).reindex(eq.index).fillna(False)
    res["leaks"] = {"brands_with_a_leak_in_a_names_hidden_prompt": int(lk.sum()),
                    "corpus_mean_equity_brands_with_a_leak": round(float(eq[lk].mean()), 2),
                    "corpus_mean_equity_other_brands": round(float(eq[~lk].mean()), 2)}
    for src in ("claude", "open"):
        if f"pooled_{src}_clean" in res:
            eh = pd.Series({k: v["equity"] for k, v in res[f"pooled_{src}"].items()})
            ec = pd.Series({k: v["equity"] for k, v in res[f"pooled_{src}_clean"].items()})
            d_ = (ec - eh).reindex(eq.index)
            res["leaks"][f"{src}_equity_against_cleaned_minus_against_original_hidden"] = {
                "brands_with_a_leak_mean": round(float(d_[lk].mean()), 2), "other_brands_mean": round(float(d_[~lk].mean()), 2),
                "largest": {k: round(float(v), 2) for k, v in d_.reindex(d_.abs().sort_values(ascending=False).index[:8]).items()},
                "note": "the cleaned prompts differ from the original names-hidden prompts only in the 175 replacements"}
    # the corpus's families beside the two reruns, brand by brand
    cols_ = fm.copy()
    for src, label in (("claude", "Claude 5.5 rerun"), ("open", "open models rerun")):
        if f"pooled_{src}" in res:
            cols_[label] = pd.Series({k: v["equity"] for k, v in res[f"pooled_{src}"].items()})
    cr = cols_.rank().corr()
    res["spearman_over_brands_families_and_reruns"] = {f"{a} | {bb}": round(float(cr.loc[a, bb]), 3)
                                                       for i, a in enumerate(cr.index) for bb in cr.columns[i + 1:]}
    OUT.mkdir(parents=True, exist_ok=True)
    pm.round(4).to_csv(OUT / "brand_model_equity.csv", index=False, lineterminator="\n")
    tab = b.copy()
    for src in sorted(pm.source.unique()):
        p = res[f"pooled_{src}"]
        tab[f"equity_{src}"] = pd.Series({k: v["equity"] for k, v in p.items()})
        tab[f"equity_{src}_ci_low"] = pd.Series({k: v["ci95"][0] for k, v in p.items()})
        tab[f"equity_{src}_ci_high"] = pd.Series({k: v["ci95"][1] for k, v in p.items()})
    fam_means = pm[pm.source == "corpus"].assign(family=lambda z: z.model.map(family)).groupby(["brand", "family"]).equity.mean().unstack()
    tab = tab.join(fam_means.add_prefix("equity_corpus_family_"))
    tab.sort_values("equity_corpus", ascending=False).round(4).to_csv(OUT / "brand_equity.csv", lineterminator="\n")
    res["_meta"] = {"script": "web-appendix-analyses/brand-by-brand-and-release-by-release/code/12_brand_level.py", "draws": cc.DRAWS, "seed": cc.SEED,
                    "files_written": ["brand_model_equity.csv", "brand_equity.csv", "numbers.json"]}
    with open(OUT / "numbers.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(json.loads(json.dumps(res, default=cc._plain)), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    top = sorted(res["pooled_corpus"].items(), key=lambda kv: -kv[1]["equity"])
    print("brands", res["brands"], "| top", [(k, v["equity"], v["ci95"]) for k, v in top[:8]])
    print("bottom", [(k, v["equity"], v["ci95"]) for k, v in top[-6:]])
    print(json.dumps({k: res[k] for k in ("correlations_corpus_brands", "regressions_corpus", "families_corpus", "consumer_familiarity_coverage")}, indent=1, default=cc._plain)[:6000])
    print("spearman", {k: res[k] for k in res if k.endswith("_spearman")}, json.dumps(res.get("spearman_over_brands_families_and_reruns")))
    print("leaks", json.dumps(res["leaks"], default=cc._plain))
    print("family differences", json.dumps(res["largest_differences_between_families"][:6], default=cc._plain))
    for src in ("claude", "claude_clean", "open"):
        if f"pooled_{src}" in res:
            t_ = sorted(res[f"pooled_{src}"].items(), key=lambda kv: -kv[1]["equity"])
            print(src, "top", [(k, v["equity"]) for k, v in t_[:6]], "bottom", [(k, v["equity"]) for k, v in t_[-3:]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
