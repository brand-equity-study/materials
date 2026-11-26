"""What predicts machine-based brand equity (its plan is materials/predictors_plan.md, with its dated changes).

    python how-the-models-differed/code/predictors.py --run final1 --equity b21 [--draws 10000]

Model level: G(m, t), the effect of the fictitious name on Study 1a's strictly better tables (no information, both
prices pooled): the share of answers picking the optimal product with names hidden minus with the original names, in
points, for every model with answers to those tables (the counts of the Claude, GPT-6 and Claude Fable 5.2 answers in
study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv; the open models' letters of export 12154, read with final_answer). Analyses 1, 2,
5, 6 and 7 use a two-way cluster bootstrap over tables and models (models resampled within their family for analysis
1); analyses 3 and 4 take their sources' numbers (the training stages' changes from base to tuned model; the four
pairs of the corpus run with and without extended thinking). Brand level: Q(b, m), each brand's equity in each model
(the brand-by-brand analysis: share shown minus hidden, points), with a category term and a two-way cluster bootstrap
over brands and models. Writes how-the-models-differed/results/predictors/numbers.json and model_gaps.csv.
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PKG = ROOT   # the top of the package
SEED = 20261120
COUNTS = os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "data", "counts", "counts-git.csv")   # the answers in the package, counted
OPEN_LETTERS = os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "data", "open-panel", "letters-12154.csv.gz")
CHARS = os.path.join(PKG, "models", "model_characteristics.csv")
BRAND_CHARS = os.path.join(PKG, "how-the-models-differed", "materials", "brand_characteristics.csv")
STAGES = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "results", "training-stages", "numbers.json")
STUDY1 = os.path.join(PKG, "study1b-64-models-on-34-tables", "results", "numbers.json")
BRAND_EQUITY = os.path.join(PKG, "web-appendix-analyses", "brand-by-brand-and-release-by-release", "results", "brand_level", "brand_model_equity.csv")


# ---------------------------------------------------------------- inputs

def model_gaps():
    """{(model, table): [n hidden, best hidden, n original, best original]}"""
    c = defaultdict(lambda: [0, 0, 0, 0])
    for r in csv.DictReader(open(COUNTS, encoding="utf8")):   # the closed models; the open models come from 12154
        if (r["build"] == "dom2" and r["model"].startswith(("claude-", "gpt-")) and r["info"] == "0"
                and r["names"] in ("hidden", "original")):
            k = c[(r["model"], r["table"])]
            j = 0 if r["names"] == "hidden" else 2
            k[j] += int(r["parsed"])
            k[j + 1] += int(r["picked_best"])
    for r in csv.DictReader(gzip.open(OPEN_LETTERS, "rt", encoding="utf8")):
        if r["build"] == "b2/dom2" and r["info"] == "0" and r["names"] in ("hidden", "original") and r["letter"]:
            k = c[(r["model"], r["table"])]
            j = 0 if r["names"] == "hidden" else 2
            k[j] += 1
            k[j + 1] += int(r["letter"] == r["best"])
    out = {}
    for (m, t), (nh, bh, no, bo) in c.items():
        if nh and no:
            out[(m, t)] = 100 * (bh / nh - bo / no)
    return out


def matrix(gaps):
    models = sorted({m for m, t in gaps})
    tables = sorted({t for m, t in gaps})
    G = np.full((len(models), len(tables)), np.nan)
    for (m, t), v in gaps.items():
        G[models.index(m), tables.index(t)] = v
    return models, tables, G


def characteristics():
    rows = {r["key"]: r for r in csv.DictReader(open(CHARS, encoding="utf8"))}
    return rows


# ---------------------------------------------------------------- the bootstrap

def wls_coef(X, y, w):
    """weighted least squares coefficients, or None when the design is singular"""
    W = np.sqrt(w)[:, None]
    A, b = X * W, y * W[:, 0]
    if np.linalg.matrix_rank(A) < X.shape[1]:
        return None
    return np.linalg.lstsq(A, b, rcond=None)[0]


def boot_models(G, stat, draws, groups=None, seed=SEED):
    """Two-way cluster bootstrap over tables (columns) and models (rows): stat(model_means, model_weights) -> value.
    groups: a label per model; models are then resampled within their group."""
    rng = np.random.default_rng(seed)
    nm, nt = G.shape
    ok = ~np.isnan(G)
    Gz = np.where(ok, G, 0.0)

    def means(wt):
        num = (Gz * wt).sum(1)
        den = (ok * wt).sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(den > 0, num / den, np.nan)

    est = stat(means(np.ones(nt)), np.ones(nm))
    out = []
    for _ in range(draws):
        wt = np.bincount(rng.integers(0, nt, nt), minlength=nt).astype(float)
        if groups is None:
            wm = np.bincount(rng.integers(0, nm, nm), minlength=nm).astype(float)
        else:
            wm = np.zeros(nm)
            for g in sorted(set(groups)):     # sorted: the draws must not depend on PYTHONHASHSEED
                idx = [i for i, x in enumerate(groups) if x == g]
                for i in rng.choice(idx, len(idx)):
                    wm[i] += 1
        mu = means(wt)
        wm = np.where(np.isnan(mu), 0, wm)
        v = stat(np.nan_to_num(mu), wm)
        if v is not None and np.isfinite(v):
            out.append(v)
    return summarize(est, out, draws)


def summarize(est, out, draws):
    v = np.sort(np.array(out))
    if est is None or len(v) == 0:
        return {"estimate": None, "draws_used": len(v)}
    return {"estimate": float(est), "ci95": [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))],
            "p_two_sided": float(min(1.0, 2 * min(np.mean(v <= 0), np.mean(v >= 0)))), "draws_used": int(len(v)),
            "draws_asked": draws}


def slope_stat(x, family=None):
    x = np.asarray(x, float)

    def f(mu, w):
        keep = w > 0
        if family is None:
            if len(set(x[keep])) < 2:
                return None
            X = np.column_stack([np.ones(keep.sum()), x[keep]])
            b = wls_coef(X, mu[keep], w[keep])
            return None if b is None else b[1]
        fams = sorted(set(np.asarray(family)[keep]))
        cols = [np.ones(keep.sum())] + [(np.asarray(family)[keep] == g).astype(float) for g in fams[1:]] + [x[keep]]
        b = wls_coef(np.column_stack(cols), mu[keep], w[keep])
        return None if b is None else b[-1]
    return f


def diff_stat(flag, adjust=None):
    flag = np.asarray(flag, float)

    def f(mu, w):
        keep = w > 0
        if len(set(flag[keep])) < 2:
            return None
        cols = [np.ones(keep.sum()), flag[keep]] + ([np.asarray(adjust, float)[keep]] if adjust is not None else [])
        b = wls_coef(np.column_stack(cols), mu[keep], w[keep])
        return None if b is None else b[1]
    return f


def mean_stat(mask):
    mask = np.asarray(mask, bool)

    def f(mu, w):
        ww = w * mask
        return float((mu * ww).sum() / ww.sum()) if ww.sum() > 0 else None
    return f


PLAN_PAIRS = ("olmo2-7b", "llama31-8b", "qwen25-7b")  # the plan, analysis 3: the pairs named before any estimate


def chat_minus_base(q1, keep=None):
    """Analysis 3 (the plan's change of 6:15 PM on 21 November): the mean over pairs of each pair's base-to-instruct
    change at the prompt form plain3, as the training stages report it, with a standard error from the reported 95 per cent
    intervals (each width / 3.92, the pairs independent) and a two-sided normal P. keep: the pairs to use, all if None;
    a named pair that q1 lacks raises, so the planned member cannot silently lose a pair."""
    pairs = {f: v["plain3"]["base_to_instruct"] for f, v in sorted(q1.items())
             if "plain3" in v and "base_to_instruct" in v["plain3"] and (keep is None or f in keep)}
    if keep is not None and set(keep) - set(pairs):
        raise ValueError(f"analysis 3: q1 lacks the named pairs {sorted(set(keep) - set(pairs))}")
    ests = [p["estimate"] for p in pairs.values()]
    ses = [(p["ci95"][1] - p["ci95"][0]) / 3.92 for p in pairs.values()]
    m, se = float(np.mean(ests)), float(math.sqrt(sum(s * s for s in ses)) / len(ses))
    p = float(math.erfc(abs(m / se) / math.sqrt(2)))
    return {"pairs (plain3, points)": pairs, "n_pairs": len(pairs), "mean": m,
            "ci95": [m - 1.96 * se, m + 1.96 * se], "p_two_sided": p,
            "source": "study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json, changes"}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


# ---------------------------------------------------------------- model level

def model_contrasts(G, models, draws, columns):
    """Analyses 1, 2, 5, 6 and 7 of the model level on a matrix of models (rows) by columns (tables for G, brands for E):
    each model's mean over its columns, with a two-way cluster bootstrap over columns and models."""
    ch = characteristics()
    miss = [m for m in models if m not in ch]
    if miss:
        raise SystemExit(f"refused: no characteristics row for {miss}")
    row = [ch[m] for m in models]
    logp = np.array([math.log10(float(r["params_total"])) if r.get("params_total") else np.nan for r in row])
    is_open = np.array([r["open"] == "open" for r in row])
    n = {"models": len(models), columns: G.shape[1], "open models": int(is_open.sum()), "closed models": int((~is_open).sum())}
    res = {"inputs": n, "models": models}

    def sub(idx):
        return G[idx], [models[i] for i in idx]

    # 1. size within families
    fam = {"Qwen 3.5": [i for i, m in enumerate(models) if m.startswith("qwen35-")],
           "Gemma 4": [i for i, m in enumerate(models) if m in ("gemma4-12b", "gemma4-26b", "gemma31b")]}
    size = {}
    for f, idx in fam.items():
        g, ms = sub(idx)
        size[f] = {"models": ms, "params_b": [round(10 ** logp[i] / 1e9, 2) for i in idx],
                   "slope_per_tenfold": boot_models(g, slope_stat(logp[idx]), draws)}
    idx = fam["Qwen 3.5"] + fam["Gemma 4"]
    labels = ["Qwen 3.5"] * len(fam["Qwen 3.5"]) + ["Gemma 4"] * len(fam["Gemma 4"])
    size["pooled within families"] = boot_models(G[idx], slope_stat(logp[idx], labels), draws, groups=labels)
    res["1 size within families"] = size
    # 2. mixture-of-experts against dense (open models with a known architecture)
    oi = [i for i, r in enumerate(row) if r["open"] == "open" and r.get("moe") in ("yes", "no") and not np.isnan(logp[i])]
    moe = np.array([row[i]["moe"] == "yes" for i in oi])
    res["2 mixture-of-experts minus dense"] = {
        "models": {"mixture-of-experts": [models[i] for i in oi if row[i]["moe"] == "yes"],
                   "dense": [models[i] for i in oi if row[i]["moe"] == "no"]},
        "unadjusted": boot_models(G[oi], diff_stat(moe), draws),
        "with log10 total parameters held fixed": boot_models(G[oi], diff_stat(moe, logp[oi]), draws)}
    # 5. developer means (descriptive)
    devs = sorted({r["developer"] for r in row})
    res["5 developer means"] = {d: boot_models(G, mean_stat([r["developer"] == d for r in row]), draws) for d in devs}
    # 6. open minus closed
    res["6 open minus closed"] = boot_models(G, diff_stat(is_open), draws)
    # 7. release date (years), with an open-or-closed term
    di = [i for i, r in enumerate(row) if r.get("release_date")]
    years = np.array([int(row[i]["release_date"][:4]) + (int(row[i]["release_date"][5:7]) - 0.5) / 12 for i in di])
    fo = is_open[di].astype(float)

    def date_stat(mu, w):
        keep = w > 0
        if len(set(years[keep])) < 2:
            return None
        b = wls_coef(np.column_stack([np.ones(keep.sum()), years[keep], fo[keep]]), mu[keep], w[keep])
        return None if b is None else b[1]
    res["7 release date, slope per year"] = {"models": len(di), "without a release date": [m for i, m in enumerate(models) if i not in di],
                                            **boot_models(G[di], date_stat, draws)}
    return res


def model_level(draws):
    gaps = model_gaps()
    models, tables, G = matrix(gaps)
    res = model_contrasts(G, models, draws, columns="tables")
    size = res["1 size within families"]
    # 3. base against chat (the plan's change of 6:15 PM): the family's member is the mean of the three pairs
    # that the plan named before any estimate (PLAN_PAIRS); the mean of every pair that q1 reports, four since OLMo 2
    # 32B was added, is reported beside it as exploratory (the plan's change of 4:58 PM on 22 November)
    q1 = json.load(open(STAGES, encoding="utf8"))["changes"]
    res["3 chat minus base"] = chat_minus_base(q1, PLAN_PAIRS)
    p3 = res["3 chat minus base"]["p_two_sided"]
    res["3 chat minus base, every pair (exploratory)"] = chat_minus_base(q1)
    # 4. reasoning on minus off 
    tp = json.load(open(STUDY1, encoding="utf8"))["thinking_pairs"]
    pooled = {"difference_pp": tp["pooled_difference_four_pairs_pp"], "ci95": tp["pooled_difference_ci95_tables_resampled"],
              "p_two_sided": tp["pooled_difference_p_two_sided"]}
    res["4 reasoning on minus off"] = {"pairs": {k: {"difference_pp": v["difference_with_minus_without_pp"],
                                                      "ci95": v["difference_ci95_tables_resampled"],
                                                      "p_two_sided": v["difference_p_two_sided"]} for k, v in tp["pairs"].items()},
                                       "pooled": pooled, "source": "study1b-64-models-on-34-tables/results/numbers.json, thinking_pairs"}
    # the primary family
    fam6 = {"1 size, pooled within families": size["pooled within families"].get("p_two_sided"),
            "2 mixture-of-experts minus dense": res["2 mixture-of-experts minus dense"]["unadjusted"].get("p_two_sided"),
            "3 chat minus base": p3,
            "4 reasoning on minus off": pooled["p_two_sided"],
            "6 open minus closed": res["6 open minus closed"].get("p_two_sided"),
            "7 release date": res["7 release date, slope per year"].get("p_two_sided")}
    keys = [k for k, p in fam6.items() if p is not None]
    res["primary family (Holm over the six)"] = dict(zip(keys, holm([fam6[k] for k in keys])))
    res["primary family, missing P"] = [k for k, p in fam6.items() if p is None]
    with open(os.path.join(OUTDIR, "model_gaps.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")   # LF, so the file's bytes match on every computer
        w.writerow(["model", "mean_gap_points", "tables"])
        for i, m in enumerate(models):
            w.writerow([m, round(float(np.nanmean(G[i])), 3), int((~np.isnan(G[i])).sum())])
    return res


def model_level_e(draws, q):
    """The model level's second family (the plan, analyses 1 to 7 'for E'): E(m), the mean over brands, each
    brand weighted equally, of the measure's equity Q(b, m), on a matrix of models by brands with a two-way cluster bootstrap
    over brands and models. Chat against base and reasoning on against off cannot be estimated for E: the measure holds no base
    model and no model run both with and without reasoning."""
    models = sorted({r["model"] for r in q})
    brands = sorted({r["brand"] for r in q})
    E = np.full((len(models), len(brands)), np.nan)
    for r in q:
        E[models.index(r["model"]), brands.index(r["brand"])] = float(r["equity"])
    res = model_contrasts(E, models, draws, columns="brands")
    fam = {"1 size, pooled within families": res["1 size within families"]["pooled within families"].get("p_two_sided"),
           "2 mixture-of-experts minus dense": res["2 mixture-of-experts minus dense"]["unadjusted"].get("p_two_sided"),
           "3 chat minus base": None,
           "4 reasoning on minus off": None,
           "6 open minus closed": res["6 open minus closed"].get("p_two_sided"),
           "7 release date": res["7 release date, slope per year"].get("p_two_sided")}
    keys = [k for k, p in fam.items() if p is not None]
    res["primary family (Holm over the four that can be estimated)"] = dict(zip(keys, holm([fam[k] for k in keys])))
    res["primary family, missing P"] = [k for k, p in fam.items() if p is None]
    res["why missing"] = {"3 chat minus base": "the measure holds no base model",
                          "4 reasoning on minus off": "the measure holds no model run both with and without reasoning"}
    res["model_means"] = {m: round(float(np.nanmean(E[i])), 6) for i, m in enumerate(models)}
    return res


MEASURE = os.path.join(PKG, "study2b-how-much-a-familiar-brand-is-worth", "results", "measure", "full1-all")  # Study 2b's measure over every model


def b21_equity():
    """Q(b, m) from the measure's final run: each brand's equity in each model (the main version's value, in log-odds: the
    brand's conditional-logit intercept minus the mean intercept of the invented names in its category), the mean over
    the brand's categories where it appears in more than one, each category weighted equally. Left out, by the measure's own
    rules: the models under its 90 per cent reading rule (numbers.json left_out) and each model's categories in which
    it follows fewer than two attributes (cells_left_out)."""
    num = json.load(gzip.open(os.path.join(MEASURE, "numbers.json.gz"), "rt", encoding="utf8"))
    gone_models = set((num.get("left_out") or {}).get("models") or {})
    gone_cells = {(c["model"], c["category"]) for c in num.get("cells_left_out") or []}
    by = defaultdict(list)
    cats = defaultdict(set)  # each brand's categories in the measure's design, for the brand level's category term
    for r in csv.DictReader(gzip.open(os.path.join(MEASURE, "cells.csv.gz"), "rt", encoding="utf8")):
        if r["version"] == "main":
            cats[r["brand"]].add(r["category"])
        if r["version"] != "main" or r["value"] in ("", None) or r["model"] in gone_models:
            continue
        if (r["model"], r["category"]) in gone_cells:
            continue
        by[(r["brand"], r["model"])].append(float(r["value"]))
    rows = [{"brand": b, "model": m, "equity": float(np.mean(v)), "categories": len(v)} for (b, m), v in sorted(by.items())]
    info = {"source": "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all (cells.csv.gz, version main, value; numbers.json.gz)",
            "models left out": sorted(gone_models), "cells left out": len(gone_cells),
            "units": "log-odds: the brand's intercept minus the mean intercept of the invented names in its category "
                     "that the model does not claim to know, plus the brand's name-by-price slope times the log of its "
                     "band centre minus the log of the category's market centre",
            "categories": {b: (next(iter(c)) if len(c) == 1 else "several categories") for b, c in sorted(cats.items())}}
    return rows, info


# ---------------------------------------------------------------- brand level

def brand_level(draws, q=None, equity="each brand's equity in each model (share shown minus hidden, points)", categories=None):
    """The brand level on Q(b, m): rows of brand, model and equity (the measure's from b21_equity(), or by default the brand-by-brand analysis's
    preliminary equity). categories: each brand's category for the category term (the measure's own, from b21_equity());
    by default the main category of brand_characteristics.csv, which was built on the brand-by-brand analysis's tables."""
    bc = {r["brand"]: r for r in csv.DictReader(open(BRAND_CHARS, encoding="utf8"))}
    if q is None:
        q = csv.DictReader(open(BRAND_EQUITY, encoding="utf8"))
    q = [r for r in q if r["brand"] in bc and r["equity"] not in ("", None)]
    brands = sorted({r["brand"] for r in q})
    models = sorted({r["model"] for r in q})
    bi = np.array([brands.index(r["brand"]) for r in q])
    mi = np.array([models.index(r["model"]) for r in q])
    y = np.array([float(r["equity"]) for r in q])
    cat = [categories[b] if categories else (bc[b]["main_category"] or "several categories") for b in brands]
    cats = sorted(set(cat))
    C = np.array([[1.0 if cat[b] == c else 0.0 for c in cats[1:]] for b in bi])

    def fit(xcols, keep_brand, category=True):
        """coefficients of the first column of xcols, with an intercept and (unless category=False) category terms,
        bootstrapped over brands and models"""
        rows = keep_brand[bi]
        X = np.column_stack([np.ones(rows.sum())] + [x[rows] for x in xcols] + ([C[rows]] if category else []))
        X = X[:, np.any(X != 0, axis=0) | (np.arange(X.shape[1]) == 0)]
        yy, bb, mm = y[rows], bi[rows], mi[rows]
        b0 = wls_coef(X, yy, np.ones(len(yy)))
        rng = np.random.default_rng(SEED)
        out = []
        for _ in range(draws):
            wb = np.bincount(rng.integers(0, len(brands), len(brands)), minlength=len(brands)).astype(float)
            wmod = np.bincount(rng.integers(0, len(models), len(models)), minlength=len(models)).astype(float)
            w = wb[bb] * wmod[mm]
            keep = w > 0
            # a draw can leave a category with no brand: its column is then all zero and is dropped, so that the draw
            # still counts (found by the independent check of 21 November 2026, when about 90 per cent of draws were
            # being lost); the predictor's column stays in place as column 1
            Xk = X[keep]
            used = np.any(Xk != 0, axis=0)
            used[0] = True
            if not used[1]:
                continue
            b = wls_coef(Xk[:, used], yy[keep], w[keep])
            if b is not None:
                out.append(b[1])
        return summarize(None if b0 is None else b0[1], out, draws)

    col = lambda k, f=float: np.array([f(bc[brands[b]][k]) if bc[brands[b]][k] not in ("", None) else np.nan for b in bi])
    has = lambda arr: ~np.isnan(np.array([arr[np.where(bi == b)[0][0]] if (bi == b).any() else np.nan for b in range(len(brands))]))
    res = {"inputs": {"rows": len(q), "brands": len(brands), "models": len(models), "equity": equity}}
    lv = col("log10_brand_value")
    ranked = col("in_a_value_ranking", lambda v: 1.0 if v in ("True", "1", "true") else 0.0)
    res["1b in a value ranking minus not (primary; the plan's change of 6:19 PM)"] = {
        "brands ranked": int(sum(1 for b in brands if bc[b]["in_a_value_ranking"] in ("True", "1", "true"))),
        **fit([ranked], np.ones(len(brands), bool))}
    res["1 brand value, slope per tenfold among ranked brands (secondary, no category term)"] = {
        "brands": int(has(lv).sum()), **fit([lv], has(lv), category=False)}

    def spec_col(key):
        return np.array([1.0 if bc[brands[b]][key] == "specialist" else 0.0 if bc[brands[b]][key] == "mass-market"
                         else np.nan for b in bi])
    spec = spec_col("specialist")
    res["2 specialist minus mass-market"] = ({"brands specialist": int(sum(bc[b]["specialist"] == "specialist" for b in brands)),
                                              **fit([spec], has(spec))} if has(spec).sum() >= 3
                                             else {"estimate": None, "note": "the specialist codes are not settled yet"})
    for k, lab in (("specialist_a", "coder A"), ("specialist_b", "coder B")):
        s = spec_col(k)
        if has(s).sum() >= 3:
            res[f"2 specialist minus mass-market, {lab}'s codes (secondary)"] = fit([s], has(s))
    tier = [bc[brands[b]]["price_tier"] for b in bi]
    prem = np.array([1.0 if t == "premium" else 0.0 for t in tier])
    val = np.array([1.0 if t == "value" else 0.0 for t in tier])
    res["3 premium minus mid"] = fit([prem, val], np.ones(len(brands), bool))
    res["3b value minus mid"] = fit([val, prem], np.ones(len(brands), bool))
    lc = col("log10_olmo_count")
    res["4 frequency, slope per tenfold of OLMo count"] = {"brands": int(has(lc).sum()), **fit([lc], has(lc))}
    tone = col("tone")
    res["5 tone, slope"] = {"brands": int(has(tone).sum()), **fit([tone], has(tone))}
    # category means (descriptive)
    res["6 category means"] = {c: float(np.mean(y[np.array([cat[b] == c for b in bi])])) for c in cats}
    fam5 = {"1b in a value ranking minus not": res["1b in a value ranking minus not (primary; the plan's change of 6:19 PM)"].get("p_two_sided"),
            "2 specialist": res["2 specialist minus mass-market"].get("p_two_sided"),
            "3 premium minus mid": res["3 premium minus mid"].get("p_two_sided"),
            "4 frequency": res["4 frequency, slope per tenfold of OLMo count"].get("p_two_sided"),
            "5 tone": res["5 tone, slope"].get("p_two_sided")}
    keys = [k for k, p in fam5.items() if p is not None]
    res["primary family (Holm)"] = dict(zip(keys, holm([fam5[k] for k in keys])))
    res["primary family, missing P"] = [k for k, p in fam5.items() if p is None]
    return res


def main():
    global OUTDIR
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--equity", choices=("b12", "b21"), default="b12",
                    help="b12: the preliminary brand level of the runs prelim1 to prelim5; b21: the measure's final equities, "
                         "for the brand level and the model level's second family (E)")
    a = ap.parse_args()
    OUTDIR = os.path.join(PKG, "how-the-models-differed", "results", "predictors")
    os.makedirs(OUTDIR, exist_ok=True)
    numbers = {"run": a.run, "draws": a.draws, "seed": SEED, "model level": model_level(a.draws)}
    if a.equity == "b21":
        q, info = b21_equity()
        numbers["equity"] = info
        numbers["model level, brand equity E (the measure)"] = model_level_e(a.draws, q)
        numbers["brand level"] = brand_level(a.draws, q, equity="the measure, final (" + info["units"] + ")",
                                             categories=info["categories"])
    else:
        numbers["brand level"] = brand_level(a.draws)
    with open(os.path.join(OUTDIR, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    for level in [k for k in numbers if k.startswith(("model level", "brand level"))]:
        print(level, json.dumps({k: v for k, v in numbers[level].items() if k.startswith("primary")}, indent=1))


if __name__ == "__main__":
    main()
