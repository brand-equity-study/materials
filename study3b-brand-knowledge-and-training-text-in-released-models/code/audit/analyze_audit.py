"""Study 2d, the machine brand audit: its analysis (study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/analysis_plan.md, "The analysis",
amendments 1 and 2, and the later amendments), over every model that answered.

    python study3b-brand-knowledge-and-training-text-in-released-models/code/audit/analyze_audit.py --panel all --out study3b-brand-knowledge-and-training-text-in-released-models/results/audit

The unit is a product with a name, in one model. Every component score and the outcome (the product's own-name gap on
Study 1a's original tables, gap.py) are centered within table and model; each component is put in standard units over
the panel's centered values; intervals come from a two-way cluster bootstrap over tables and models (2,000 draws, seed
20261120), every model with equal weight. H6b is tested over pairs of a brand and a category, centered within
category and model, with the bootstrap over categories and models.
"""
import argparse
import json
import os
import random
import sys
from collections import defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package's top folder
MAT = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "materials", "audit")   # the items, the reference set, the brand counts
DATA = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "data", "audit")   # the answers, the tone codes, the open letters
STUDY1 = os.path.join(PKG, "study1a-tables-with-one-optimal-product")   # Study 1a's original tables, their answers and the parser
sys.path.insert(0, HERE)

SEED = 20261120
COMPONENTS = ("salience", "typicality", "recognition", "quality", "credibility", "tone")   # test 1's six
ATTRS = ("reliability", "durability", "performance", "support", "safety", "failure")
PANELS = {"claude": ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1"]}
# amendments 2 and 3: Fable 5.1 answered full1 in two builds that share full1's item ids
ANSWER_BUILDS = {"claude-fable-5-1": ["full1-fable", "full1-fable-rest"]}
# amendment 4: the gpt-oss models' Study 2 letters (export 12094) were read from their reasoning channel, so the two
# models had no gap until the letters were exported again from their final answers. Job 12154's v2 letters did that
# (21 November, 11:20 AM), so no model is excluded now; the mechanism stays for a later export.
# the paper's exclusion rule (README, 'The 90 per cent rule'): a model whose answers the parser
# reads in under 90 per cent of a build's items is reported apart and left out of every pooled estimate and every
# analysis of how models differ. Kimi Linear 48B's Study 2 full2 letters, which give its gap, parse in 5,011 of 6,120
# answers (job 12683's counts); its audit answers parse above 90 per cent, so its components stay and its gap is apart.
GAP_EXCLUDED = {"kimi-linear48b": "the 90 per cent rule: its letters on Study 1a's original tables parse in 5,011 of 6,120 "
                                  "answers (81.9 per cent)"}
LEFT_OUT = {"kimi-linear48b": {"rule": "the 90 per cent rule: a model parsed in under 90 per cent of a build's "
                                       "items is reported apart", "build": "b2/full2", "answers": 6120, "parsed": 5011,
                               "source": "study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz"}}
LETTER_SOURCES = {}   # the letters export each open-panel letter came from (gap.SOURCES_USED), written to the numbers
# amendment 6: the GPT models through Codex answer full1 in the same two builds as Fable 5.1, with full1's item ids
CODEX_MODELS = ("gpt-6.2-sol", "gpt-6.2-astra", "gpt-6.1-sol", "gpt-6-astra")
for _m in CODEX_MODELS:
    ANSWER_BUILDS[_m] = ["full1-fable", "full1-fable-rest"]
# the analysis plan's amendment 6: GPT-6.2 Sol and
# GPT-6.1 Sol answer every test; GPT-6.2 Astra and GPT-6 Astra answer only the core tests, which the audit is not. So
# the audit's GPT group is the two Sol models; the Astra models' partial audit answers enter no test.
AUDIT_CODEX = ("gpt-6.2-sol", "gpt-6.1-sol")
# amendment 6: each panel's first judge of the tone
TONE_FILES = {"claude": os.path.join(DATA, "tone", "claude.jsonl.gz"),
              "open": os.path.join(DATA, "tone", "open.jsonl.gz"),
              # the open models added in export 12682 and Gemma 4 31B's completed run (21 November 2026, 10:12 PM); read
              # last, so that its tone replaces the earlier one for the same model, brand and category
              "open-add": os.path.join(DATA, "tone", "open-add.jsonl.gz"),
              # the two Sol models' descriptions (complete for all 165 brands in both)
              "codex": os.path.join(DATA, "tone", "codex.jsonl.gz")}
# The GPT models' runs were stopped part way on 22 November 2026 (8:38 to 8:43 PM); the rule since then:
# each enters a measure only on the units it answered in full, with one composition for each model and measure
# (completeness.CODEX_MEASURES). CODEX_UNITS keeps the counts of complete units, which the results report.
CODEX_UNITS = {}
MIN_CLUSTERS = 3   # a per-model slope needs its component to vary in at least three tables (the bootstrap's minimum)
ZERO = 1e-12       # a bootstrap draw closer to zero than this is zero (bootstrap(): its sign is rounding)


def group_of(m):
    """amendment 6's groups: the Claude models through the API, the GPT models through Codex, the open models."""
    if m.startswith("claude-"):
        return "claude"
    return "codex" if m in CODEX_MODELS else "open"


# ---------- the statistics, on plain rows ----------

def center(rows, keys, group):
    """Adds key+'_c' to each row: the value minus the mean of its group (rows with a missing value are left out of
    the group mean and get None)."""
    by = defaultdict(list)
    for r in rows:
        by[group(r)].append(r)
    for g in by.values():
        for k in keys:
            xs = [r[k] for r in g if r.get(k) is not None]
            mu = sum(xs) / len(xs) if xs else None
            for r in g:
                r[k + "_c"] = None if r.get(k) is None or mu is None else r[k] - mu
    return rows


def ols(y, X):
    """Coefficients of y on [1, X] (X an n by k array); (coefs, r2)."""
    A = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ b
    tss = ((y - y.mean()) ** 2).sum()
    return b, (1 - (resid ** 2).sum() / tss) if tss > 0 else 0.0


def design(rows, ycol, xcols):
    keep = [r for r in rows if r.get(ycol) is not None and all(r.get(x) is not None for x in xcols)]
    y = np.array([r[ycol] for r in keep], float)
    X = np.array([[r[x] for x in xcols] for r in keep], float).reshape(len(keep), len(xcols))
    return keep, y, X


def standardize(rows, cols):
    for c in cols:
        xs = np.array([r[c] for r in rows if r.get(c) is not None], float)
        sd = xs.std() if len(xs) > 1 else 0.0
        for r in rows:
            r[c + "_z"] = None if r.get(c) is None or sd == 0 else r[c] / sd
    return rows


def bootstrap(rows, fit, cluster_a, cluster_b, draws=2000, seed=SEED, strata=None):
    """fit(rows) -> dict of numbers. Resamples the values of cluster_a and of cluster_b independently with
    replacement. Returns {name: {"est", "lo", "hi", "p", "draws"}}; p is two-sided (twice the share of draws on the
    far side of zero). When the estimate itself cannot be fitted (too few rows), returns {}. strata (amendment 6): a
    function of a cluster_b value; the cluster_b values are then resampled within each stratum (the models within
    their group), so every draw holds every group."""
    try:
        est = fit(rows)
    except (np.linalg.LinAlgError, ValueError, ZeroDivisionError):
        return {}
    A = sorted({cluster_a(r) for r in rows})
    Bv = sorted({cluster_b(r) for r in rows})
    by_s = defaultdict(list)
    for b in Bv:
        by_s[strata(b) if strata else None].append(b)
    cell = defaultdict(list)
    for r in rows:
        cell[(cluster_a(r), cluster_b(r))].append(r)
    rng = random.Random(seed)
    got = defaultdict(list)
    if len(A) >= 3 and len(Bv) >= 1:
        for _ in range(draws):
            a_s = [rng.choice(A) for _ in A]
            if strata:
                b_s = [rng.choice(by_s[s]) for s in sorted(by_s) for _ in by_s[s]]
            else:
                b_s = [rng.choice(Bv) for _ in Bv] if len(Bv) >= 2 else Bv
            sample = [r for a in a_s for b in b_s for r in cell.get((a, b), [])]
            try:
                f = fit(sample)
            except (np.linalg.LinAlgError, ValueError, ZeroDivisionError):
                continue
            for k, v in f.items():
                if v is not None and np.isfinite(v):
                    got[k].append(v)
    out = {}
    for k, v in est.items():
        d = np.array(got.get(k, []))
        # a draw whose slope is zero in exact arithmetic (the outcome does not vary where the component does) comes out
        # as plus or minus 1e-15, and its sign then depends on the computer's sums; such a draw counts as exactly zero,
        # on both sides of the P value (13 P values moved
        # between two computers with the same draws)
        d = np.where(np.abs(d) < ZERO, 0.0, d)
        if len(d) >= 50 and v is not None:
            lo, hi = np.percentile(d, [2.5, 97.5])
            p = min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean()))
            out[k] = {"est": float(v), "lo": float(lo), "hi": float(hi), "p": float(p), "draws": int(len(d))}
        else:
            out[k] = {"est": None if v is None else float(v), "lo": None, "hi": None, "p": None, "draws": int(len(d))}
    return out


def _slope(res, n, rows=None, xcol=None, cluster="table"):
    out = dict(res.get("slope") or {"est": None, "lo": None, "hi": None, "p": None, "draws": 0})
    out["n"] = n
    if rows is not None:
        # the clusters (tables; categories for H6b) in which the component varies: a slope that rests on fewer than
        # three has no interval over clusters (two per-model
        # slopes of test 2 rest on one table, so every draw that holds it gives the same slope)
        out["clusters_varying"] = len({r[cluster] for r in rows if r.get(xcol) is not None and abs(r[xcol]) > 1e-12})
    return out


def holm(ps):
    """Holm-adjusted p values for a dict {name: p}."""
    items = sorted((p, k) for k, p in ps.items() if p is not None)
    m, out, run = len(items), {}, 0.0
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def spearman_brown(r):
    """2r / (1 + r) for a positive split-half correlation; a correlation of zero or below is returned as it is (the
    correction has no meaning there, and it is below the plan's 0.5 rule either way)."""
    return None if r is None else (2 * r / (1 + r) if r > 0 else r)


def vif(rows, cols):
    keep, _, X = design(rows, cols[0], cols)
    out = {}
    for j, c in enumerate(cols):
        others = np.delete(X, j, axis=1)
        if others.shape[1] == 0:
            out[c] = 1.0
            continue
        _, r2 = ols(X[:, j], others)
        out[c] = float(1 / (1 - r2)) if r2 < 1 else float("inf")
    return out


# ---------- the tests ----------

def test1(rows, comp, draws=2000, subset=None):
    """The own-name gap on one centered, standardized component, with the centered names-hidden share as control.
    rows: dicts with model, table, gap, s_hidden, name_kind and the component; subset: 'familiar' to keep familiar
    names only (centered again among them)."""
    rows = [dict(r) for r in rows if r.get(comp) is not None and r.get("gap") is not None]
    if subset == "familiar":
        rows = [r for r in rows if r["name_kind"].startswith("familiar")]
    center(rows, ["gap", "s_hidden", comp], lambda r: (r["model"], r["table"]))
    standardize(rows, [comp + "_c"])

    def fit(rs):
        _, y, X = design(rs, "gap_c", [comp + "_c_z", "s_hidden_c"])
        if len(y) < 5:
            raise ValueError("too few rows")
        _varies(X[:, 0])
        b, _ = ols(y, X)
        return {"slope": b[1]}
    res = bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws)
    return _slope(res, len(rows), rows, comp + "_c_z")


def _varies(x):
    """A draw in which the component does not vary has no slope; least squares would return 0, which the bootstrap
    would count as a draw at zero (found 21 November 2026, about 7:20 PM Central, amendment 6's note)."""
    if not np.any(np.abs(x) > 1e-12):
        raise ValueError("the component does not vary in these rows")


def test2(rows, comp, draws=2000):
    """The name on the same product: rows hold dy (the gap under the swapped name minus the gap under the product's
    own name) and dx_<comp> (the swapped name's component minus the own name's)."""
    rows = [dict(r) for r in rows if r.get("dx_" + comp) is not None and r.get("dy") is not None]
    standardize(rows, ["dx_" + comp])

    def fit(rs):
        _, y, X = design(rs, "dy", ["dx_" + comp + "_z"])
        if len(y) < 5:
            raise ValueError("too few rows")
        _varies(X[:, 0])
        b, _ = ols(y, X)
        return {"slope": b[1]}
    res = bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws)
    return _slope(res, len(rows), rows, "dx_" + comp + "_z")


def test3(rows, comps, draws=2000):
    """All components together (after the collinearity rule), with each one's share of variance added last."""
    rows = [dict(r) for r in rows if r.get("gap") is not None and all(r.get(c) is not None for c in comps)]
    center(rows, ["gap", "s_hidden"] + list(comps), lambda r: (r["model"], r["table"]))
    cc = [c + "_c" for c in comps]
    standardize(rows, cc)
    # a component with no variance among these rows has no standard score and is left out, by name
    constant = [c for c in comps if any(r.get(c + "_c_z") is None for r in rows)]
    zc = [c + "_c_z" for c in comps if c not in constant]
    # collinearity: a pair correlated above 0.8 is entered as the mean of its standard scores
    groups = [[c] for c in zc]
    for i in range(len(zc)):
        for j in range(i + 1, len(zc)):
            r = corr([x[zc[i]] for x in rows], [x[zc[j]] for x in rows])
            if r is not None and r > 0.8:
                gi = next(g for g in groups if zc[i] in g)
                gj = next(g for g in groups if zc[j] in g)
                if gi is not gj:
                    gi.extend(gj)
                    groups.remove(gj)
    names = []
    for g in groups:
        name = "+".join(sorted(x[:-4] for x in g))
        for r in rows:
            r[name] = float(np.mean([r[x] for x in g]))
        names.append(name)
    cols = names + ["s_hidden_c"]

    def fit(rs):
        _, y, X = design(rs, "gap_c", cols)
        if len(y) < len(cols) + 3:
            raise ValueError("too few rows")
        b, r2 = ols(y, X)
        out = {n: b[i + 1] for i, n in enumerate(names)}
        for i, n in enumerate(names):
            _, r2_without = ols(y, np.delete(X, i, axis=1))
            out["dr2:" + n] = r2 - r2_without
        out["r2"] = r2
        return out
    res = bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws)
    res["vif"] = vif(rows, cols) if rows else {}
    res["groups"] = names
    res["left_out_constant"] = constant
    res["n"] = len(rows)
    return res


def invented_benchmark(rows, comps, draws=2000):
    """Exploratory, not in the plan (the advisor's read at 11:55 PM): the own-name gap on an indicator of an invented
    name alone, with the names-hidden share as control, centered within table and model, on the rows that test 3
    uses; its R squared is set beside test 3's, to show how much of what the components predict is the contrast of an
    invented name against familiar ones."""
    rows = [dict(r) for r in rows if r.get("gap") is not None and all(r.get(c) is not None for c in comps)]
    for r in rows:
        r["invented"] = 1.0 if r["name_kind"] == "invented" else 0.0
    center(rows, ["gap", "s_hidden", "invented"], lambda r: (r["model"], r["table"]))

    def fit(rs):
        _, y, X = design(rs, "gap_c", ["invented_c", "s_hidden_c"])
        if len(y) < 5:
            raise ValueError("too few rows")
        b, r2 = ols(y, X)
        return {"invented": b[1], "r2": r2}
    res = bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws)
    res["n"] = len(rows)
    return res


def attribute_differences(rows, draws=2000, seed=SEED):
    """Exploratory: test 1's slope for each unseen attribute, and the difference of each attribute's slope from the
    reliability rating's and the performance rating's, in the same bootstrap draws (paired)."""
    attrs = ["q_" + a for a in ATTRS]
    rows = [dict(r) for r in rows if r.get("gap") is not None and all(r.get(a) is not None for a in attrs)]
    center(rows, ["gap", "s_hidden"] + attrs, lambda r: (r["model"], r["table"]))
    standardize(rows, [a + "_c" for a in attrs])

    def fit(rs):
        out = {}
        for a in attrs:
            _, y, X = design(rs, "gap_c", [a + "_c_z", "s_hidden_c"])
            if len(y) < 5:
                raise ValueError("too few rows")
            out[a] = ols(y, X)[0][1]
        for base in ("q_reliability", "q_performance"):
            for a in attrs:
                if a != base:
                    out[f"{a} minus {base}"] = out[a] - out[base]
        return out
    res = bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws, seed)
    res["n"] = len(rows)
    return res


def reliability(rows, halves):
    """Split-half reliability within each model over the products centered within table: {model: {name: r_SB}}.
    halves: {name: (key_a, key_b)} naming two columns of the rows."""
    out = defaultdict(dict)
    for m in sorted({r["model"] for r in rows}):
        rs = [dict(r) for r in rows if r["model"] == m]
        for name, (ka, kb) in halves.items():
            sub = [r for r in rs if r.get(ka) is not None and r.get(kb) is not None]
            center(sub, [ka, kb], lambda r: r["table"])
            r = corr([x[ka + "_c"] for x in sub], [x[kb + "_c"] for x in sub])
            out[m][name] = spearman_brown(r)
    return dict(out)


def h6b(rows, draws=2000):
    """Consideration share on recall share over pairs of a brand and a category, centered within category and model."""
    rows = [dict(r) for r in rows if r.get("recall") is not None and r.get("consideration") is not None]
    center(rows, ["recall", "consideration"], lambda r: (r["model"], r["category"]))
    standardize(rows, ["recall_c"])

    def fit(rs):
        _, y, X = design(rs, "consideration_c", ["recall_c_z"])
        if len(y) < 5:
            raise ValueError("too few rows")
        _varies(X[:, 0])
        b, _ = ols(y, X)
        return {"slope": b[1]}
    res = bootstrap(rows, fit, lambda r: r["category"], lambda r: r["model"], draws)
    return _slope(res, len(rows), rows, "recall_c_z", "category")


def consideration_vs_evaluation(rows, key="consideration", draws=2000):
    rows = [dict(r) for r in rows if r.get(key) is not None and r.get("gap") is not None]
    center(rows, ["gap", key], lambda r: (r["model"], r["table"]))

    def fit(rs):
        _, y, X = design(rs, "gap_c", [key + "_c"])
        if len(y) < 5:
            raise ValueError("too few rows")
        _varies(X[:, 0])
        b, _ = ols(y, X)
        return {"slope": b[1], "r": corr(y, X[:, 0])}
    return bootstrap(rows, fit, lambda r: r["table"], lambda r: r["model"], draws)


# ---------- amendment 6: the differences between models ----------

def by_group(rows, ycol, xcol, controls, cluster_a, groups=group_of, draws=2000, seed=SEED):
    """One fit with a slope of xcol, and each control, for each group of models: "slope:<g>" for every group and
    "<g> minus <h>" for every pair, with the models resampled within their group (the cluster_a values drawn once for
    all groups). rows are already centered and standardized over the pooled rows."""
    rows = [dict(r) for r in rows if r.get(ycol) is not None and r.get(xcol) is not None
            and all(r.get(c) is not None for c in controls)]
    gs = sorted({groups(r["model"]) for r in rows})
    for r in rows:
        g_r = groups(r["model"])
        for g in gs:
            ind = 1.0 if g_r == g else 0.0
            r["x@" + g] = r[xcol] * ind
            for c in controls:
                r[c + "@" + g] = r[c] * ind
    cols = ["x@" + g for g in gs] + [c + "@" + g for c in controls for g in gs]

    def fit(rs):
        _, y, X = design(rs, ycol, cols)
        if len(y) < len(cols) + 3 or not len(gs):
            raise ValueError("too few rows")
        b, _ = ols(y, X)
        # a group whose component does not vary in these rows has no slope (least squares would return 0 for it, which
        # the bootstrap would count as a draw at zero); such a draw gives that group, and its differences, nothing
        # (found 21 November, about 7:20 PM: the Claude models' recognition among familiar names varies in 8 products
        # of 2 tables, so 275 of 2,000 draws held no variation)
        slope = {g: (b[1 + i] if np.any(np.abs(X[:, i]) > 1e-12) else None) for i, g in enumerate(gs)}
        out = {"slope:" + g: slope[g] for g in gs}
        for i, g in enumerate(gs):
            for h in gs[i + 1:]:
                out[f"{g} minus {h}"] = None if slope[g] is None or slope[h] is None else slope[g] - slope[h]
        return out
    res = bootstrap(rows, fit, cluster_a, lambda r: r["model"], draws, seed, strata=groups)
    res["models"] = {g: sorted({r["model"] for r in rows if groups(r["model"]) == g}) for g in gs}
    res["n"] = {g: sum(1 for r in rows if groups(r["model"]) == g) for g in gs}
    return res


def _prep_test1(rows, comp, subset=None):
    rows = [dict(r) for r in rows if r.get(comp) is not None and r.get("gap") is not None]
    if subset == "familiar":
        rows = [r for r in rows if r["name_kind"].startswith("familiar")]
    center(rows, ["gap", "s_hidden", comp], lambda r: (r["model"], r["table"]))
    standardize(rows, [comp + "_c"])
    return rows


def test1_groups(rows, comp, draws=2000, subset=None, groups=group_of):
    """test 1 (or its familiar-only form) with a slope for each group, in the pooled standard units."""
    return by_group(_prep_test1(rows, comp, subset), "gap_c", comp + "_c_z", ["s_hidden_c"], lambda r: r["table"],
                    groups, draws)


def test2_groups(rows, comp, draws=2000, groups=group_of):
    rows = [dict(r) for r in rows if r.get("dx_" + comp) is not None and r.get("dy") is not None]
    standardize(rows, ["dx_" + comp])
    return by_group(rows, "dy", "dx_" + comp + "_z", [], lambda r: r["table"], groups, draws)


def h6b_groups(rows, draws=2000, groups=group_of):
    rows = [dict(r) for r in rows if r.get("recall") is not None and r.get("consideration") is not None]
    center(rows, ["recall", "consideration"], lambda r: (r["model"], r["category"]))
    standardize(rows, ["recall_c"])
    return by_group(rows, "consideration_c", "recall_c_z", [], lambda r: r["category"], groups, draws)


def cve_groups(rows, key="consideration", draws=2000, groups=group_of):
    rows = [dict(r) for r in rows if r.get(key) is not None and r.get("gap") is not None]
    center(rows, ["gap", key], lambda r: (r["model"], r["table"]))
    return by_group(rows, "gap_c", key + "_c", [], lambda r: r["table"], groups, draws)


def weights(rows, comp, subset=None):
    """Each model's share of the summed squared centered component (in the pooled standard units) over test 1's
    rows: the weight that a slope fitted on the pooled rows gives the model, before the control."""
    rows = _prep_test1(rows, comp, subset)
    ss = defaultdict(float)
    for r in rows:
        if r.get(comp + "_c_z") is not None:
            ss[r["model"]] += r[comp + "_c_z"] ** 2
    tot = sum(ss.values())
    return {m: v / tot for m, v in sorted(ss.items())} if tot > 0 else {}


def spread(by_model):
    """{model: slope result} -> the mean, standard deviation and range of the per-model slopes, and how many have an
    interval above zero and below zero."""
    # a slope that rests on fewer than three tables (or categories) has no interval over them and is left out
    by_model = {m: v for m, v in by_model.items() if v.get("clusters_varying", 3) >= MIN_CLUSTERS}
    est = {m: v["est"] for m, v in by_model.items() if v.get("est") is not None}
    if not est:
        return {"n_models": 0}
    xs = np.array(list(est.values()))
    return {"n_models": len(xs), "mean": float(xs.mean()), "sd": float(xs.std(ddof=1)) if len(xs) > 1 else None,
            "min": float(xs.min()), "max": float(xs.max()),
            "min_model": min(est, key=est.get), "max_model": max(est, key=est.get),
            "above_zero": sorted(m for m, v in by_model.items() if v.get("lo") is not None and v["lo"] > 0),
            "below_zero": sorted(m for m, v in by_model.items() if v.get("hi") is not None and v["hi"] < 0)}


FREQ = os.path.join(MAT, "brand_frequencies.csv")


def log_frequency(path=FREQ):
    """{brand: mean over the four corpora of log10(1 + the brand's count)}, from the brand-only queries (every
    spelling of the name summed within a corpus)."""
    import csv
    per = defaultdict(lambda: defaultdict(int))
    for r in csv.DictReader(open(path, encoding="utf8")):
        if r["query_type"] == "brand_only":
            per[r["brand_name"]][r["corpus"]] += int(float(r["raw_count"] or 0))
    return {b: float(np.mean([np.log10(1 + n) for n in c.values()])) for b, c in per.items()}


def brand_level(own, draws=2000, seed=SEED):
    """the analysis plan, secondary: each brand's component scores and gap, averaged over its products in the category and over
    the panel's models, against its log frequency in public training corpora; Pearson r with a bootstrap over the pairs
    of a brand and a category. Also reported for familiar brands alone."""
    freq = log_frequency()
    agg = defaultdict(lambda: defaultdict(list))
    for r in own:
        key = (r["name"], r["category"])
        for c in COMPONENTS + ("gap",):
            if r.get(c) is not None:
                agg[key][c].append(r[c])
        agg[key]["kind"].append(r["name_kind"])
    rows = []
    for (b, cat), d in agg.items():
        if b not in freq:
            continue
        row = {"brand": b, "category": cat, "logfreq": freq[b], "familiar": all(k.startswith("familiar") for k in d["kind"])}
        for c in COMPONENTS + ("gap",):
            row[c] = float(np.mean(d[c])) if d[c] else None
        rows.append(row)
    rng = random.Random(seed)
    out = {}
    for subset, rs in (("all", rows), ("familiar", [r for r in rows if r["familiar"]])):
        out[subset] = {}
        for c in COMPONENTS + ("gap",):
            pts = [(r["logfreq"], r[c]) for r in rs if r[c] is not None]
            if len(pts) < 5:
                continue
            est = corr([p[0] for p in pts], [p[1] for p in pts])
            boots = []
            for _ in range(draws):
                s = [pts[rng.randrange(len(pts))] for _ in pts]
                v = corr([p[0] for p in s], [p[1] for p in s])
                if v is not None:
                    boots.append(v)
            lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) > 50 else (None, None))
            out[subset][c] = {"r": est, "lo": None if lo is None else float(lo), "hi": None if hi is None else float(hi),
                              "n": len(pts)}
    return out


# ---------- the data ----------

def assemble(models, panel, cimarron=None, tone=None, build="full1"):
    """rows for tests 1 and 3 (one per model, table and product under its own name), rows for test 2 (the swapped
    names), and the brand rows for H6b."""
    import gap as G
    import score as SC
    tables = {}
    import gzip
    for line in gzip.open(os.path.join(STUDY1, "materials", "original-tables", "prompts.jsonl.gz"), "rt", encoding="utf8"):
        it = json.loads(line)
        tables[it["table"]] = it["category"]
    if panel == "open":
        grows = [r for r in G.gaps("full2", set(models), open_panel=True) if r["model"] not in GAP_EXCLUDED]
        LETTER_SOURCES.update(G.SOURCES_USED)
    else:
        grows = G.gaps("full2", set(models))
    S = {}
    for m in models:
        extra = ANSWER_BUILDS.get(m) if build == "full1" else None
        keep = None
        if m in AUDIT_CODEX and build == "full1":
            import completeness as CO
            ids, CODEX_UNITS[m] = CO.keep_ids(m, CO.CODEX_MEASURES)
            keep = {m: ids}
        got = SC.score(build, {m}, {m: cimarron[m]} if cimarron and m in cimarron else None, extra, keep)
        if m in got:
            S[m] = got[m]
    own, swap = [], []
    gap_of = {(r["model"], r["table"], r["product"], r["label"], r["name"]): r for r in grows}

    def comps(m, t, product, label, name):
        s = S[m]
        cat = tables[t]
        b = s["brand"].get((name, cat), {})
        lst = s["listing"].get((t, product, label, name), {})
        cr = s["credibility"].get((t, name), {})
        row = {"salience": b.get("salience"), "typicality": b.get("typicality"), "recognition": b.get("recognition"),
               "recall": b.get("recall"), "consideration": b.get("consideration"),
               "consideration_real": b.get("consideration_real"),
               "consideration_rank": b.get("consideration_rank"),
               "consideration_rank_named": b.get("consideration_rank_named"),
               "quality": lst.get("index"), "credibility": (cr.get("low") or {}).get("premium"),
               "credibility_usual": (cr.get("usual") or {}).get("premium"),
               # a GPT model's tone enters only where its descriptions of the brand are complete
               "tone": (tone or {}).get((m, name, cat)) if m not in CODEX_UNITS or b.get("descriptions") else None}
        for a in ATTRS:
            row["q_" + a] = (lst.get(a) or {}).get("premium")
            row["q_" + a + "_h0"], row["q_" + a + "_h1"] = (lst.get(a) or {}).get("halves", (None, None))
        # the halves for the reliability rule
        row["quality_h0"], row["quality_h1"] = lst.get("index_h", (None, None))
        h = (cr.get("low") or {}).get("halves", (None, None))
        row["credibility_h0"], row["credibility_h1"] = h
        for k in ("salience", "typicality", "recognition"):
            row[k + "_h0"], row[k + "_h1"] = b.get(k + "_h", (None, None))
        return row
    for r in grows:
        m = r["model"]
        if m not in S:
            continue
        base = {"model": m, "table": r["table"], "category": tables[r["table"]], "product": r["product"], "name": r["name"],
                "name_kind": r["name_kind"], "gap": r["gap"], "s_hidden": r["s_hidden"],
                "gap_h0": r["half_a"], "gap_h1": r["half_b"]}
        c = comps(m, r["table"], r["product"], r["label"], r["name"])
        if r["label"] == "own":
            own.append({**base, **c})
        else:
            o = gap_of.get((m, r["table"], r["product"], "own", r["product_brand"]))
            if not o:
                continue
            c_own = comps(m, r["table"], r["product"], "own", r["product_brand"])
            row = {**base, "dy": r["gap"] - o["gap"]}
            for k in COMPONENTS + tuple("q_" + a for a in ATTRS):
                row["dx_" + k] = None if c.get(k) is None or c_own.get(k) is None else c[k] - c_own[k]
            swap.append(row)
    # amendment 4: a model whose gap is excluded still has its components reported, in rows with no gap, which every
    # test leaves out (each test keeps rows with a gap)
    import build_items as B
    for m in sorted(set(S) & set(GAP_EXCLUDED)):
        for t in B.S.load_tables().values():
            for p in t["products"]:
                c = comps(m, t["id"], p["orig"], "own", p["brand"])
                own.append({"model": m, "table": t["id"], "category": t["category"], "product": p["orig"],
                            "name": p["brand"], "name_kind": p["kind"], "gap": None, "s_hidden": None,
                            "gap_h0": None, "gap_h1": None, **c})
    brands = []
    for m, s in S.items():
        for (b, cat), v in s["brand"].items():
            if "reference" in v["kinds"]:
                continue
            brands.append({"model": m, "brand": b, "category": cat, "recall": v.get("recall"),
                           "familiar": "invented" not in v["kinds"],
                           "consideration": v.get("consideration"), "consideration_real": v.get("consideration_real"),
                           "consideration_chat": v.get("consideration_chat"),
                           "consideration_crowd": v.get("consideration_crowd")})
    return own, swap, brands, S


def run(models, panel, draws, cimarron=None, tone=None, build="full1"):
    if panel == "all":
        return run_all(models, draws, cimarron, tone, build)
    own, swap, brands, S = assemble(models, panel, cimarron, tone, build)
    return analyze(own, swap, brands, models, panel, draws)


def assemble_all(models, cimarron=None, tone=None, build="full1"):
    """amendment 6: every group assembled as in its own panel (the open models' gap from their letters, the
    Claude and GPT models' from their answer texts), then the rows put together."""
    own, swap, brands, S = [], [], [], {}
    for g, panel in (("claude", "claude"), ("codex", "codex"), ("open", "open")):
        ms = [m for m in models if group_of(m) == g]
        if not ms:
            continue
        o, s, b, sc = assemble(ms, panel, cimarron, tone, build)
        own += o
        swap += s
        brands += b
        S.update(sc)
    return own, swap, brands, S


def heterogeneity(own, swap, brands, have, models_with_gap, draws):
    """amendment 6: each group's slope and the pairwise differences; each model's own slope and their spread; each
    model's weight in the pooled slope."""
    fam_brands = [b for b in brands if b.get("familiar")]
    fam_own = [r for r in own if r["name_kind"].startswith("familiar")]
    out = {"test1": {}, "test1_familiar": {}, "test2": {}, "weights": {}, "weights_familiar": {},
           "test1_by_model_spread": {}, "test2_by_model": {}, "test2_by_model_spread": {}}
    for c in have:
        out["test1"][c] = test1_groups(own, c, draws)
        out["test1_familiar"][c] = test1_groups(own, c, draws, "familiar")
        out["test2"][c] = test2_groups(swap, c, draws)
        out["weights"][c] = weights(own, c)
        out["weights_familiar"][c] = weights(own, c, "familiar")
        out["test2_by_model"][c] = {m: test2([r for r in swap if r["model"] == m], c, draws) for m in models_with_gap}
        out["test2_by_model_spread"][c] = spread(out["test2_by_model"][c])
    out["h6b"] = h6b_groups(brands, draws)
    out["h6b_real"] = h6b_groups([{**b, "consideration": b["consideration_real"]} for b in brands], draws)
    out["h6b_familiar"] = h6b_groups(fam_brands, draws)
    out["h6b_by_model"] = {m: h6b([b for b in brands if b["model"] == m], draws)
                           for m in sorted({b["model"] for b in brands})}
    out["h6b_by_model_spread"] = spread(out["h6b_by_model"])
    out["consideration_vs_evaluation"] = cve_groups(own, "consideration", draws)
    out["consideration_vs_evaluation_real"] = cve_groups(own, "consideration_real", draws)
    out["consideration_vs_evaluation_familiar"] = cve_groups(fam_own, "consideration", draws)
    out["consideration_rank_vs_evaluation"] = cve_groups(own, "consideration_rank", draws)
    return out


def pooled_core(own, swap, brands, have, draws):
    """The pooled tests 1 and 2, familiar-only test 1 and H6b alone, for the repeats on a subset of models."""
    out = {"models": sorted({r["model"] for r in own if r.get("gap") is not None}),
           "test1": {c: test1(own, c, draws) for c in have},
           "test1_familiar": {c: test1(own, c, draws, "familiar") for c in have},
           "test2": {c: test2(swap, c, draws) for c in have},
           "h6b": h6b(brands, draws)}
    adj = holm({c: v["p"] for c, v in out["test1"].items()})
    for c, p in adj.items():
        out["test1"][c]["p_holm"] = p
    return out


def run_all(models, draws, cimarron=None, tone=None, build="full1"):
    own, swap, brands, S = assemble_all(models, cimarron, tone, build)
    res = analyze(own, swap, brands, models, "all", draws)
    have = res["components_measured"]
    res["groups"] = {m: group_of(m) for m in res["models"]}
    res["entered"] = {
        "test1": {c: sorted({r["model"] for r in own if r.get(c) is not None and r.get("gap") is not None}) for c in have},
        "test2": {c: sorted({r["model"] for r in swap if r.get("dx_" + c) is not None and r.get("dy") is not None})
                  for c in have},
        "h6b": sorted({b["model"] for b in brands if b.get("recall") is not None and b.get("consideration") is not None})}
    res["heterogeneity"] = heterogeneity(own, swap, brands, have, res["models_with_gap"], draws)
    res["heterogeneity"]["test1_by_model_spread"] = {
        c: spread({m: v[c] for m, v in res["exploratory"]["test1_by_model"].items() if c in v}) for c in have}
    res["heterogeneity"]["panel_verdicts"] = "each panel's own H6a and H6b: numbers-claude.json and numbers-open.json"
    # the repeats of amendment 6: without Gemma 4 26B, and over the models whose gap is reliable (split-half >= 0.5)
    keep = [m for m in res["models_with_gap"] if m != "gemma4-26b"]
    res["without_gemma4_26b"] = pooled_core([r for r in own if r["model"] in keep],
                                            [r for r in swap if r["model"] in keep],
                                            [b for b in brands if b["model"] in keep], have, draws)
    reliable = [m for m in res["models_with_gap"] if (res["reliability"].get(m, {}).get("gap") or -1) >= 0.5]
    res["reliable_gap"] = pooled_core([r for r in own if r["model"] in reliable],
                                      [r for r in swap if r["model"] in reliable],
                                      [b for b in brands if b["model"] in reliable], have, draws)
    # amendment 3: every pooled estimate that holds the Claude models is also given without Fable 5.1, whose slopes are
    # the largest of the Claude models (Table H3); here the pooled tests and each group's slope in tests 1 and 2
    nf = [m for m in res["models_with_gap"] if m != "claude-fable-5-1"]
    nf_own, nf_swap = [r for r in own if r["model"] in nf], [r for r in swap if r["model"] in nf]
    res["without_fable"] = pooled_core(nf_own, nf_swap, [b for b in brands if b["model"] in nf], have, draws)
    res["without_fable"]["groups_test1"] = {c: test1_groups(nf_own, c, draws) for c in have}
    res["without_fable"]["groups_test1_familiar"] = {c: test1_groups(nf_own, c, draws, "familiar") for c in have}
    res["without_fable"]["groups_test2"] = {c: test2_groups(nf_swap, c, draws) for c in have}
    res["tool_excluded"] = {"gap": {f"{b}/{m}": n for (b, m), n in _G().TOOL_EXCLUDED.items()},
                            "audit": dict(_SC().TOOL_EXCLUDED)}
    # the GPT models' complete units by item set and measure
    res["codex_units"] = {m: CODEX_UNITS[m] for m in sorted(CODEX_UNITS)}
    return res


def _G():
    import gap
    return gap


def _SC():
    import score
    return score


def analyze(own, swap, brands, models, panel, draws):
    have = [c for c in COMPONENTS if any(r.get(c) is not None for r in own)]
    res = {"models": sorted({r["model"] for r in own}), "models_with_gap": sorted({r["model"] for r in own
                                                                                   if r.get("gap") is not None}),
           "gap_excluded": {m: GAP_EXCLUDED[m] for m in sorted({r["model"] for r in own}) if m in GAP_EXCLUDED},
           "left_out": {m: LEFT_OUT[m] for m in sorted({r["model"] for r in own}) if m in LEFT_OUT},
           "letter_sources": dict(LETTER_SOURCES),
           "components_measured": have, "draws": draws,
           "test1": {}, "test1_familiar": {}, "test2": {}, "secondary": {}, "descriptive": {}}
    # each component's mean, by model and by the kind of the name on the product (own names), and the gap's
    desc_cols = list(have) + ["gap", "s_hidden", "recall", "consideration", "consideration_real", "credibility_usual"] + \
        ["q_" + a for a in ATTRS]
    for m in res["models"]:
        for kind in ("familiar-high", "familiar-medium", "invented"):
            rs = [r for r in own if r["model"] == m and r["name_kind"] == kind]
            res["descriptive"].setdefault(m, {})[kind] = {
                c: (float(np.mean([r[c] for r in rs if r.get(c) is not None])) if any(r.get(c) is not None for r in rs) else None)
                for c in desc_cols}
            res["descriptive"][m][kind]["n"] = len(rs)
    for c in have:
        res["test1"][c] = test1(own, c, draws)
        res["test1_familiar"][c] = test1(own, c, draws, "familiar")
        res["test2"][c] = test2(swap, c, draws)
    adj = holm({c: v["p"] for c, v in res["test1"].items()})
    for c, p in adj.items():
        res["test1"][c]["p_holm"] = p
    res["test3"] = test3(own, have, draws)
    for a in ATTRS:
        res["secondary"]["q_" + a] = test1(own, "q_" + a, draws)
    res["secondary"]["credibility_usual"] = test1(own, "credibility_usual", draws)
    halves = {k: (k + "_h0", k + "_h1") for k in ("salience", "typicality", "recognition", "quality", "credibility")}
    halves.update({"q_" + a: ("q_" + a + "_h0", "q_" + a + "_h1") for a in ATTRS})
    halves["gap"] = ("gap_h0", "gap_h1")
    res["reliability"] = reliability(own, halves)
    # secondary: the reliability among familiar names alone, for reading the familiar-only tests
    res["reliability_familiar"] = reliability([r for r in own if r["name_kind"].startswith("familiar")], halves)
    # over the models with a gap, so the components and the gap average the same models
    res["brand_level_frequency"] = brand_level([r for r in own if r["model"] in res["models_with_gap"]], draws)
    res["h6b"] = h6b(brands, draws)
    res["h6b_real"] = h6b([{**b, "consideration": b["consideration_real"]} for b in brands], draws)
    # secondary, added after reading (the analysis plan, a note to amendment 6): the outside requests in Study
    # 1b's grouping, the requests that people typed to chat assistants alone, and the crowd-written WebShop instructions
    res["h6b_chat"] = h6b([{**b, "consideration": b.get("consideration_chat")} for b in brands], draws)
    res["h6b_crowd"] = h6b([{**b, "consideration": b.get("consideration_crowd")} for b in brands], draws)
    res["consideration_vs_evaluation"] = consideration_vs_evaluation(own, "consideration", draws)
    res["consideration_vs_evaluation_real"] = consideration_vs_evaluation(own, "consideration_real", draws)
    # secondary, added after reading (the analysis plan, a note to amendment 6): the plan asks for the brand's rank
    # among the brands named; the plan's mean rank (a list without the brand counts as position 16) in the open requests'
    # answers, against the gap in the same test; and the mean position over only the answers that name the brand
    res["consideration_rank_vs_evaluation"] = consideration_vs_evaluation(own, "consideration_rank", draws)
    res["consideration_rank_named_vs_evaluation"] = consideration_vs_evaluation(own, "consideration_rank_named", draws)
    # exploratory, not in the plan: the same among familiar brands, the invented-name benchmark, test 1 by model, the
    # attributes compared in the same draws
    fam_brands = [b for b in brands if b.get("familiar")]
    fam_own = [r for r in own if r["name_kind"].startswith("familiar")]
    res["exploratory"] = {
        "h6b_familiar": h6b(fam_brands, draws),
        "consideration_vs_evaluation_familiar": consideration_vs_evaluation(fam_own, "consideration", draws),
        "invented_benchmark": invented_benchmark(own, have, draws),
        "attribute_differences": attribute_differences(own, draws),
        "test1_by_model": {m: {c: test1([r for r in own if r["model"] == m], c, draws) for c in have}
                           for m in res["models_with_gap"]},
    }
    # H6a, as amendment 1 reads it
    res["H6a"] = {c: {"supported": bool(res["test1"][c]["lo"] is not None and res["test1"][c]["est"] > 0
                                          and (res["test1"][c].get("p_holm") or 1) < 0.05),
                      "test1": res["test1"][c], "test2": res["test2"][c], "familiar": res["test1_familiar"][c]}
                  for c in ("quality", "credibility") if c in res["test1"]}
    res["H6b"] = {"supported": bool(res["h6b"]["lo"] is not None and res["h6b"]["lo"] > 0), "test": res["h6b"]}
    if panel == "claude" and "claude-fable-5-1" in res["models"]:
        others = [m for m in models if m != "claude-fable-5-1"]
        o_own = [r for r in own if r["model"] in others]
        res["without_fable"] = {c: test1(o_own, c, draws) for c in have}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", choices=["claude", "open", "all"], required=True)
    ap.add_argument("--models", default="")
    ap.add_argument("--cimarron", action="append", default=[], help="<model>=<answers.jsonl>")
    ap.add_argument("--tone", default="", help="the judges' tone codes (jsonl of model, brand, category, tone)")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--build", default="full1", help="the audit build (full1; Fable 5.1 reads full1-fable)")
    ap.add_argument("--out", default=os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "results", "audit"))
    ap.add_argument("--answers", default="", help="the open panel's answer folders (open_panel.py), oldest export "
                    "first: every model in them. With --panel open or all and neither --answers nor --cimarron, the "
                    "repository's answers-open/12094 and answers-open/12682 (answers_open.py, MANIFEST.tsv)")
    ap.add_argument("--without", default="", help="models left out, for a robustness repeat (amendment 4)")
    ap.add_argument("--codex", action="store_true", help="--panel all: add the GPT models through Codex (amendment 6)")
    a = ap.parse_args()
    cim = dict(x.split("=", 1) for x in a.cimarron)
    if not a.answers and not a.cimarron and a.panel in ("open", "all"):
        # the open models' answers as exported (study3b-brand-knowledge-and-training-text-in-released-models/data/audit/open/), oldest export first; run_all.py checks
        # every file against study3b-brand-knowledge-and-training-text-in-released-models/data/audit/FILES.csv before this runs
        a.answers = ",".join(os.path.join(DATA, "open", e) for e in ("12094", "12682"))
    if a.answers:
        import open_panel as OP
        cim.update({m: ",".join(f) for m, f in OP.cimarron_paths(a.answers).items()})
    if a.models:
        models = a.models.split(",")
    elif a.panel == "all":
        # amendment 6: every model that answered: the Claude panel, the open models named by --answers or --cimarron,
        # and, with --codex (once their runs are complete), the GPT models whose audit answers exist
        codex = [m for m in AUDIT_CODEX if a.codex
                 and any(os.path.exists(os.path.join(DATA, "codex", f"{m}-{b}.jsonl.gz")) for b in ANSWER_BUILDS[m])]
        models = PANELS["claude"] + codex + sorted(cim)
    else:
        models = PANELS.get(a.panel) or sorted(cim)
    models = [m for m in models if m not in set(a.without.split(","))]
    tone = None
    tone_paths = a.tone.split(",") if a.tone else (
        [p for p in (TONE_FILES["claude"], TONE_FILES["open"], TONE_FILES["open-add"], TONE_FILES["codex"])
         if os.path.exists(p)]
        if a.panel == "all" else [])
    if tone_paths:
        tone = {}
        for path in tone_paths:
            import gzip
            for line in gzip.open(path, "rt", encoding="utf8"):
                x = json.loads(line)
                tone[(x["model"], x["brand"], x["category"])] = x["tone"]
    res = run(models, a.panel, a.draws, cim, tone, a.build)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, f"numbers-{a.panel}{'' if a.build == 'full1' else '-' + a.build}.json")
    json.dump(res, open(path, "w", encoding="utf8"), indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("models", "components_measured", "H6a", "H6b")}, indent=1, default=str))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
