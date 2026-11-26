"""Study 2 over every model that answered each test: the information supplied (Study 2a), each piece alone (2b), the
price (2c) and the store's information condition (Study 1c), from counts of every model's answers.

    python study2a-experience-attributes-stated-for-every-product/code/pool_all.py --counts study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv --counts study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv \
        --store-cells study2a-experience-attributes-stated-for-every-product/data/store/claude-cells.csv --store-cells study2a-experience-attributes-stated-for-every-product/data/store/open-cells.csv \
        --only 2a,2b,store --out study2a-experience-attributes-stated-for-every-product/results/all-models
    python study2a-experience-attributes-stated-for-every-product/code/pool_all.py --counts study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv --counts study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv \
        --only 2c --out study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1

A counts file has one row for each model, table and cell (build, model, table, names, info, rung, partner_kind, answers,
parsed, picked_best, picked_partner). count_git.py writes such rows from the answers in this package (the Claude models
through the Messages API, Claude Fable 5.2 through the Claude command line, the GPT-6 models through Codex) and from the
open panel's letters; the open panel's counts on each piece alone and on the price were written on the computing
cluster from its answers. The script:
1. screens each model by its own rule: for the API, command-line and Codex models, every item answered and at most 5
   per cent of answers unparsed; for the open panel, every item answered, at least 90 per cent parsed and at least 10
   per cent best product with names hidden (open_b9.screen);
2. computes each part's estimates with the functions of the analyses of one panel, over every model that passes:
   Study 2a with analyze.primary_report, Study 2b with analyze.split_report, Study 2c with open_b9.eq_part
   (analyze_eq.assemble), and the store with store.py's functions on the two panels' cells;
3. gives each developer group alone (Anthropic; OpenAI through Codex; open weights, which includes OpenAI's gpt-oss,
   served from its open weights like the rest of the open panel) and the difference between two groups, from a bootstrap
   that resamples the tables once and the models within each group (2,000 draws, seed 20261120);
4. writes per_model.csv: each model's estimate with the standard deviation of its bootstrap draws (tables resampled,
   the model fixed) as its standard error.

Pooling gives equal weight to every table within a model and to every model; intervals come from the two-way bootstrap
over tables and models (2,000 draws, seed 20261120; the store keeps its own 10,000), with two-sided P values from the
same draws. analyze.draws_of is replaced in this process by fast_draws_of, which draws the same tables and models in the
same order and computes the means with numpy. The plan: study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 11.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from collections import defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # the package
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))  # analyze.py and parse_answer.py
sys.path.insert(0, os.path.join(HERE, "..", "..", "web-appendix-analyses/each-piece-of-information-alone", "code"))  # analyze_attr.py, attr_conditions.py
sys.path.insert(0, os.path.join(HERE, "..", "..", "study2b-how-much-a-familiar-brand-is-worth", "code"))  # analyze_eq.py
import analyze as AN  # noqa: E402  (read only; draws_of is replaced in this process)
import open_b9 as OB  # noqa: E402  (read only)

DRAWS = 2000
SEED = 20261120
EQ_MARGIN = 0.02  # the plan's equivalence margin, as analyze.primary_report's margin
N_ITEMS = {"dom2": 3600, "split1": 6300, "eq1": 10560, "attr1": 11400}
GROUPS = ("Anthropic", "OpenAI", "open weights")
STORE_ARM = "plain-info"
STORE_REF = "plain"


# ---------------------------------------------------------------- the bootstrap, fast

def fast_draws_of(per_mt, draws, seed=SEED, fixed_models=False, all_tables=None):
    """analyze.draws_of with the same random draws in the same order (models, then tables, each draw), the means taken
    with numpy. Returns the sorted draws of the pooled mean. With all_tables, the tables are resampled from that list,
    as analyze_eq's draw_sets does (a table with no value then adds nothing to a draw)."""
    models = sorted({m for m, t in per_mt})
    tables = sorted(all_tables) if all_tables is not None else sorted({t for m, t in per_mt})
    mi = {m: i for i, m in enumerate(models)}
    ti = {t: i for i, t in enumerate(tables)}
    x = np.full((len(models), len(tables)), np.nan)
    for (m, t), v in per_mt.items():
        x[mi[m], ti[t]] = v
    rng = random.Random(seed)
    ms = np.empty((draws, len(models)), dtype=np.int64)
    ts = np.empty((draws, len(tables)), dtype=np.int64)
    for d in range(draws):
        ms[d] = np.arange(len(models)) if fixed_models else [mi[rng.choice(models)] for _ in models]
        ts[d] = [ti[rng.choice(tables)] for _ in tables]
    vals = []
    for lo in range(0, draws, 250):          # in slices, so a large panel stays within memory
        sub = x[ms[lo:lo + 250, :, None], ts[lo:lo + 250, None, :]]
        ok = ~np.isnan(sub)
        cnt = ok.sum(2)
        tot = py_sum(np.where(ok, sub, 0.0))
        has = cnt > 0
        per_m = np.where(has, tot / np.maximum(cnt, 1), 0.0)
        nm = has.sum(1)
        v = py_sum(per_m) / np.maximum(nm, 1)
        vals.extend(float(a) for a, n in zip(v, nm) if n > 0)
    return sorted(vals)


def py_sum(a):
    """Python's built-in sum() of floats along the last axis, element by element, so that every bootstrap draw is the
    same float as analyze.draws_of's: from Python 3.12, sum() adds floats with Neumaier's compensated summation
    (CPython's bltinmodule.c), before that one by one. A missing cell is given as 0.0, which changes neither the sum
    nor the compensation."""
    f = np.zeros(a.shape[:-1])
    if sys.version_info < (3, 12):
        for i in range(a.shape[-1]):
            f = f + a[..., i]
        return f
    c = np.zeros(a.shape[:-1])
    for i in range(a.shape[-1]):
        x = a[..., i]
        t = f + x
        c += np.where(np.abs(f) >= np.abs(x), (f - t) + x, (x - t) + f)
        f = t
    return np.where(c != 0, f + c, f)


SLOW_DRAWS_OF = AN.draws_of
AN.draws_of = fast_draws_of


def group_diff(mt_a, mt_b, draws=DRAWS, seed=SEED):
    """The pooled mean of group a minus that of group b. Each draw resamples the tables once (shared by both groups),
    then the models within a, then the models within b. Returns analyze.summary of the difference."""
    tables = sorted({t for m, t in mt_a} | {t for m, t in mt_b})
    ma, mb = sorted({m for m, t in mt_a}), sorted({m for m, t in mt_b})

    def mean(mt, ms, ts):
        per = []
        for m in ms:
            x = [mt[(m, t)] for t in ts if (m, t) in mt]
            if x:
                per.append(sum(x) / len(x))
        return sum(per) / len(per) if per else None

    est = mean(mt_a, ma, tables) - mean(mt_b, mb, tables)
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        ts = [rng.choice(tables) for _ in tables]
        a = mean(mt_a, [rng.choice(ma) for _ in ma], ts)
        b = mean(mt_b, [rng.choice(mb) for _ in mb], ts)
        if a is not None and b is not None:
            vals.append(a - b)
    vals.sort()
    return AN.summary(est, vals)


def one_model(per_mt, draws=DRAWS, all_tables=None):
    """One model's estimate, interval and P from draws over its tables, and the standard deviation of those draws."""
    e = sum(per_mt.values()) / len(per_mt)
    vals = fast_draws_of(per_mt, draws, fixed_models=True, all_tables=all_tables)
    s = AN.summary(e, vals)
    s["se"] = round(statistics.pstdev(vals), 4)
    s["tables"] = len(per_mt)
    return s


def pooled_summary(per_mt, draws=DRAWS):
    models = {m for m, t in per_mt}
    if not per_mt:
        return None
    e = sum(sum(v for (mm, t), v in per_mt.items() if mm == m) / sum(1 for (mm, t) in per_mt if mm == m)
            for m in models) / len(models)
    if len(models) < 3:
        return {"estimate": round(e, 4), "models": len(models), "note": "fewer than three models; no pooled interval"}
    s = AN.summary(e, fast_draws_of(per_mt, draws))
    s["models"] = len(models)
    return s


# ---------------------------------------------------------------- the models

def group_of(model):
    if model.startswith("claude-"):
        return "Anthropic"
    if model.startswith("gpt-6"):
        return "OpenAI"
    return "open weights"


def developers():
    """{open model key: its lab} from the open panel's registry; the closed models' developer is their group."""
    out = {}
    path = os.path.join(ROOT, "models", "open-models.tsv")
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf8"), delimiter="\t"):
            out[r["key"]] = r.get("lab", "")
    return out


def read_counts(paths):
    """Rows of every counts file; a (build, model) found in two files refuses, because its answers would count twice."""
    rows, seen = [], {}
    for p in paths:
        here = set()
        for r in csv.DictReader(open(p, encoding="utf8")):
            for k in ("answers", "parsed", "picked_best", "picked_partner"):
                r[k] = int(r[k] or 0)
            key = (r["build"], r["model"])
            if key in seen and seen[key] != p:
                raise SystemExit(f"REFUSED: {key} is in both {seen[key]} and {p}")
            here.add(key)
            rows.append(r)
        for key in here:
            seen[key] = p
    return rows


# Builds in which a model enters on each table that it answered in every condition, rather than only when it answered
# every prompt (the runs of two GPT models stopped with some sets partial): within a table every condition is then
# present, so the design stays balanced.
TABLE_RULE = ("split1", "attr1")
TABLES_OF = {}   # {build: set of tables}, filled from the item files for the builds of TABLE_RULE


def expected_cells(build):
    """{(table, names, info, rung): items} from the build's item file."""
    c = defaultdict(int)
    import gzip
    prompts = {"split1": "web-appendix-analyses/each-piece-of-information-alone/materials/each-piece-alone/prompts.jsonl.gz",
               "attr1": "web-appendix-analyses/each-piece-of-information-alone/materials/further-information/prompts.jsonl.gz"}[build]
    with gzip.open(os.path.join(ROOT, prompts), "rt", encoding="utf8") as fh:
        for line in fh:
            it = json.loads(line)
            c[(it["table"], it["names"], str(it["info"]), str(it["rung"]))] += 1
    return c


def complete_tables(rows, build, exp):
    """{model: set of tables in which the model answered every item of every condition}."""
    got = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r["build"] == build:
            got[r["model"]][(r["table"], r["names"], str(r["info"]), str(r["rung"]))] += r["answers"]
    tables = sorted({k[0] for k in exp})
    cells = defaultdict(list)
    for k, v in exp.items():
        cells[k[0]].append((k, v))
    return {m: {t for t in tables if all(g.get(k, 0) == v for k, v in cells[t])} for m, g in got.items()}


def screen(rows, build, tables_in=None):
    """{model: {"answers", "parsed_share", "best_share_hidden", "rule", "verdict"}}. With tables_in ({model: set of
    tables}, for the builds of TABLE_RULE) only those tables of each model are counted, and a model enters when it has
    at least one; the record gives how many tables it entered on."""
    by = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        if r["build"] != build:
            continue
        if tables_in is not None and r["table"] not in tables_in.get(r["model"], ()):
            continue
        b = by[r["model"]]
        b[0] += r["answers"]
        b[1] += r["parsed"]
        if r["names"] == "hidden" and (build != "eq1" or r["rung"].startswith("B-")):
            b[2] += r["parsed"]
            b[3] += r["picked_best"]
    out = {}
    if tables_in is not None:   # every model with rows in the build, also one with no complete table
        for r in rows:
            if r["build"] == build:
                by[r["model"]]
    for m, (n, p, hp, hb) in sorted(by.items()):
        ps, bs = (p / n if n else 0.0), (hb / hp if hp else 0.0)
        if tables_in is not None:
            k = len(tables_in.get(m, ()))
            need = N_ITEMS[build] * k / len(TABLES_OF[build]) if TABLES_OF.get(build) else n
            short = k == 0
            short_text = "incomplete: no table answered in every condition"
        else:
            need, short, short_text = N_ITEMS[build], n < N_ITEMS[build], "incomplete"
        if group_of(m) == "open weights":
            rule = "open-models plan"
            verdict = (short_text if short else "unable: parsed under 90 per cent" if ps < 0.9
                       else "unable: picks the best product in under 10 per cent with names hidden" if bs < 0.1 else "in")
        else:
            rule = "this plan"
            verdict = (short_text if short else "more answers than items" if n > need
                       else "out: more than 5 per cent unparsed" if ps < 0.95 else "in")
        out[m] = {"group": group_of(m), "answers": n, "parsed_share": round(ps, 4), "best_share_hidden": round(bs, 4),
                  "rule": rule, "verdict": verdict}
        if tables_in is not None:
            out[m]["tables"] = len(tables_in.get(m, ()))
            out[m]["tables_of"] = len(TABLES_OF[build])
    return out


# ---------------------------------------------------------------- Study 2a (dom2)

def con_of(rows, build, models):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["build"] == build and r["model"] in models:
            k = (r["model"], r["table"], r["names"], OB.typed(r["info"]), OB.typed(r["rung"]))
            c[k][0] += r["parsed"]
            c[k][1] += r["picked_best"]
    return AN.contrasts(c)


def price_contrast_mt(con):
    """{(model, table): gap at 30 per cent below minus gap at the equal price, no information} (primary_report's)."""
    return {(m, t): v["penalty"] - con[(m, t, 0, 0)]["penalty"]
            for (m, t, i, g), v in con.items() if i == 0 and g == 2 and (m, t, 0, 0) in con}


def mt_of(con, stat, info):
    return AN.pooled(con, stat, info=info)[1]


def study2a(rows, models, draws):
    con = con_of(rows, "dom2", models)
    prim = AN.primary_report(con, draws)
    measures = {"gap with no information": lambda c: mt_of(c, "penalty", 0),
                "gap with the information": lambda c: mt_of(c, "penalty", 1),
                "change when the information is supplied": lambda c: mt_of(c, "info_change", 1),
                "gap at 30 per cent below minus gap at the equal price, no information": price_contrast_mt}
    by_group, diffs, per_model = {}, {}, []
    sub = {g: {k: v for k, v in con.items() if group_of(k[0]) == g} for g in GROUPS}
    for g in GROUPS:
        if sub[g]:
            by_group[g] = {name: pooled_summary(fn(sub[g]), draws) for name, fn in measures.items()}
            by_group[g]["models"] = sorted({k[0] for k in sub[g]})
    present = [g for g in GROUPS if sub[g]]
    for i, a in enumerate(present):
        for b in present[i + 1:]:
            diffs[f"{a} minus {b}"] = {name: group_diff(fn(sub[a]), fn(sub[b]), draws) for name, fn in measures.items()}
    # the models with closed weights pooled as one group (Anthropic's and OpenAI's), for the paper's claim about them;
    # each bootstrap is seeded on its own, so this group leaves every other estimate as it was
    closed = {k: v for k, v in con.items() if group_of(k[0]) != "open weights"}
    if closed:
        by_group["closed weights"] = {name: pooled_summary(fn(closed), draws) for name, fn in measures.items()}
        by_group["closed weights"]["models"] = sorted({k[0] for k in closed})
    # the plan's equivalence test (primary_report): the effect with the information is within 2 points of zero when
    # its 90 per cent interval lies inside plus or minus 2 points
    for g, d in by_group.items():
        s = d.get("gap with the information")
        if s and "ci90" in s:
            s["within_2_points"] = bool(-EQ_MARGIN < s["ci90"][0] and s["ci90"][1] < EQ_MARGIN)
    for m in sorted({k[0] for k in con}):
        cm = {k: v for k, v in con.items() if k[0] == m}
        for name, fn in measures.items():
            mt = fn(cm)
            if mt:
                per_model.append(("2a", name, m, one_model(mt, draws)))
    return {"models": sorted({k[0] for k in con}), "pooled": prim, "by_group": by_group,
            "group_differences": diffs, "model_counts": model_counts(per_model)}, per_model


def model_counts(per_model):
    """For each estimate, how many models it holds and how many have an estimate, or a 95 per cent interval, above
    and below zero (from each model's own interval; uncorrected)."""
    out = {}
    for name in dict.fromkeys(n for _, n, _, _ in per_model):
        ss = [s for _, n, _, s in per_model if n == name]
        out[name] = {"models": len(ss), "above_zero": sum(s["estimate"] > 0 for s in ss),
                     "below_zero": sum(s["estimate"] < 0 for s in ss),
                     "ci95_above_zero": sum(s["ci95"][0] > 0 for s in ss),
                     "ci95_below_zero": sum(s["ci95"][1] < 0 for s in ss)}
    return out


# ---------------------------------------------------------------- Study 2b (split1)

def split_contrast_mt(con, s, ref):
    d = {}
    for (m, t, i, g), v in con.items():
        if i == s and (m, t, ref, g) in con:
            d.setdefault((m, t), []).append(v["penalty"] - con[(m, t, ref, g)]["penalty"])
    return {k: sum(v) / len(v) for k, v in d.items()}


def study2b(rows, models, draws):
    con = con_of(rows, "split1", models)
    rep = AN.split_report(con, draws)
    rep.pop("by_model", None)        # each model is in per_model.csv
    measures = {f"gap, information {arm}": (lambda c, arm=arm: mt_of(c, "penalty", arm))
                for arm in (0,) + AN.SPLIT + (1,)}
    for s in AN.SPLIT:
        for ref, label in ((0, "none"), (1, "all five")):
            measures[f"{s} alone minus {label}"] = (lambda c, s=s, ref=ref: split_contrast_mt(c, s, ref))
    sub = {g: {k: v for k, v in con.items() if group_of(k[0]) == g} for g in GROUPS}
    by_group = {g: {name: pooled_summary(fn(sub[g]), draws) for name, fn in measures.items()} for g in GROUPS if sub[g]}
    present = [g for g in GROUPS if sub[g]]
    diffs = {f"{a} minus {b}": {name: group_diff(fn(sub[a]), fn(sub[b]), draws)
                                for name, fn in measures.items() if fn(sub[a]) and fn(sub[b])}
             for i, a in enumerate(present) for b in present[i + 1:]}
    per_model = []
    for m in sorted({k[0] for k in con}):
        cm = {k: v for k, v in con.items() if k[0] == m}
        for name, fn in measures.items():
            mt = fn(cm)
            if mt:
                per_model.append(("2b", name, m, one_model(mt, draws)))
    return {"models": sorted({k[0] for k in con}), "pooled": rep, "by_group": by_group, "group_differences": diffs}, per_model


# ---------------------------------------------------------------- Study 2c (eq1)

EQ_TESTS = ("invented minus familiar twin, names shown", "invented minus familiar twin, names hidden",
            "names hidden minus names shown, invented twin's share of pair picks")


def eq_parity_mt(rows, models):
    """{test: {(model, table): value}} for analyze_eq.parity_tests' three comparisons at the same price (option A at
    cut0, every partner kind summed, as open_b9.eq_part counts them): the invented twin's share minus the partner's
    share of all parsed answers with names shown and with names hidden, and the invented twin's share of the answers
    that pick either twin with names hidden minus with names shown. They give each
    model's standard error in Study 2c."""
    pc = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["build"] == "eq1" and r["model"] in models and r["rung"] == "A-cut0":
            v = pc[(r["model"], r["table"], r["names"])]
            v[0] += r["picked_best"]
            v[1] += r["picked_partner"]
            v[2] += r["parsed"]
    out = {k: {} for k in EQ_TESTS}
    for (m, t, names), (inv, par, n) in pc.items():
        if names == "original" and n:
            out[EQ_TESTS[0]][(m, t)] = (inv - par) / n
        if names == "hidden" and n:
            out[EQ_TESTS[1]][(m, t)] = (inv - par) / n
        if names == "hidden" and inv + par:
            o = pc.get((m, t, "original"))
            if o and o[0] + o[1]:
                out[EQ_TESTS[2]][(m, t)] = inv / (inv + par) - o[0] / (o[0] + o[1])
    return out


FAM_KEY = "familiar twin's share of pair picks at the same price"


def eq_pair_share_mt(rows, models, names):
    """{(model, table): the familiar twin's share of the answers that pick either twin} at the same price (option A at
    cut0, every partner kind summed), with the names shown ("original") or hidden, so that the paper reports this share from one key and not as a
    subtraction of two."""
    pc = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["build"] == "eq1" and r["model"] in models and r["rung"] == "A-cut0" and r["names"] == names:
            v = pc[(r["model"], r["table"])]
            v[0] += r["picked_best"]
            v[1] += r["picked_partner"]
    return {mt: par / (inv + par) for mt, (inv, par) in pc.items() if inv + par}


def familiar_share(rows, models, draws=DRAWS):
    """FAM_KEY over every model and by group, with the names shown and hidden; a group of fewer than three models has
    its estimate only (pooled_summary)."""
    out = {}
    for names, label in (("original", "names shown"), ("hidden", "names hidden")):
        mt = eq_pair_share_mt(rows, set(models), names)
        out[label] = {"all": pooled_summary(mt, draws)}
        for g in GROUPS:
            sub = {k: v for k, v in mt.items() if group_of(k[0]) == g}
            if sub:
                out[label][g] = pooled_summary(sub, draws)
    return out


def study2c(rows, models, draws=DRAWS):
    items = OB.load_items("eq1")
    out = {"models": sorted(models), "pooled": OB.eq_part(rows, set(models), items), "by_group": {},
           "group_differences": {}}
    for g in GROUPS:
        ms = {m for m in models if group_of(m) == g}
        if len(ms) >= 3:
            out["by_group"][g] = {"models": sorted(ms), **OB.eq_part(rows, ms, items)}
        elif ms:
            out["by_group"][g] = {"models": sorted(ms), "note": "fewer than three models; see the model-level results"}
    mts = eq_parity_mt(rows, set(models))
    sub = {g: {k: {mt: v for mt, v in d.items() if group_of(mt[0]) == g} for k, d in mts.items()} for g in GROUPS}
    present = [g for g in GROUPS if any(sub[g][k] for k in EQ_TESTS)]
    for i, a in enumerate(present):
        for b in present[i + 1:]:
            out["group_differences"][f"{a} minus {b}"] = {k: group_diff(sub[a][k], sub[b][k], draws)
                                                         for k in EQ_TESTS if sub[a][k] and sub[b][k]}
    out[FAM_KEY] = familiar_share(rows, models, draws)
    per_model = []
    tables = sorted({it["table"] for it in items.values()})     # analyze_eq resamples every table of the build
    fam_mt = eq_pair_share_mt(rows, set(models), "original")
    for m in sorted(models):
        for k in EQ_TESTS:
            mt = {key: v for key, v in mts[k].items() if key[0] == m}
            if mt:
                per_model.append(("2c", k, m, one_model(mt, draws, all_tables=tables)))
        mt = {key: v for key, v in fam_mt.items() if key[0] == m}
        if mt:
            per_model.append(("2c", f"{FAM_KEY}, names shown", m, one_model(mt, draws, all_tables=tables)))
    return out, per_model


# ---------------------------------------------------------------- the attribute build (attr1, amendment 10)

def attr_measures(s, tables=None):
    """{name: per (model, table) values} for analyze_attr.report's estimates: every arm's name gap, each arm against
    no information (family 2), each fact as a row against as a sentence (family 1) and the 2 by 2 (family 3)."""
    import analyze_attr as Q
    import attr_conditions as A
    gap = lambda a: (lambda S_: S_("hidden", a) - S_("original", a))
    out = {f"gap, {a}": Q.per_mt(s, gap(a), tables) for a in A.CONDITIONS}
    for a in Q.OTHER_CONDITIONS:
        out[f"{a} against none"] = Q.per_mt(s, (lambda a_: lambda S_: (S_("hidden", a_) - S_("original", a_))
                                                - (S_("hidden", "none") - S_("original", "none")))(a), tables)
    for f in Q.FACTS:
        out[f"{f}: row against sentence"] = Q.per_mt(s, (lambda f_: lambda S_: (S_("hidden", f"{f_}-row") - S_("original", f"{f_}-row"))
                                                      - (S_("hidden", f"{f_}-sentence") - S_("original", f"{f_}-sentence")))(f), tables)
    cell = {"If": "original", "Ff": "all-familiar", "Ii": "all-invented", "Fi": "familiar-alone"}
    v = lambda S_, c: S_(cell[c], "none")
    out["2x2: best product's familiar name"] = Q.per_mt(s, lambda S_: ((v(S_, "Ff") - v(S_, "If")) + (v(S_, "Fi") - v(S_, "Ii"))) / 2, tables)
    out["2x2: other products' familiar names"] = Q.per_mt(s, lambda S_: ((v(S_, "If") - v(S_, "Ii")) + (v(S_, "Ff") - v(S_, "Fi"))) / 2, tables)
    out["2x2: interaction"] = Q.per_mt(s, lambda S_: (v(S_, "Ff") - v(S_, "If")) - (v(S_, "Fi") - v(S_, "Ii")), tables)
    return out


def study_attr(rows, models, draws):
    import analyze_attr as Q
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["build"] == "attr1" and r["model"] in models:
            k = (r["model"], r["table"], r["names"], r["info"])
            c[k][0] += r["parsed"]
            c[k][1] += r["picked_best"]
    s = {k: b / n for k, (n, b) in c.items() if n}
    tables = sorted({k[1] for k in s})
    keep = [t for t in tables if t not in Q.INVENTED_REAL]
    out = {"models": sorted({k[0] for k in s}), "pooled": Q.report(s), "without_invented_real": Q.report(s, keep),
           "by_group": {}, "group_differences": {}}
    sub = {g: {k: v for k, v in s.items() if group_of(k[0]) == g} for g in GROUPS}
    for g in GROUPS:
        ms = sorted({k[0] for k in sub[g]})
        if len(ms) >= 3:
            out["by_group"][g] = {"models": ms, **Q.report(sub[g])}
        elif ms:
            out["by_group"][g] = {"models": ms, "note": "fewer than three models; see the model-level results"}
    meas = {g: attr_measures(sub[g]) for g in GROUPS if sub[g]}
    present = list(meas)
    for i, a in enumerate(present):
        for b in present[i + 1:]:
            out["group_differences"][f"{a} minus {b}"] = {k: group_diff(meas[a][k], meas[b][k], draws)
                                                         for k in meas[a] if meas[a][k] and meas[b][k]}
    per_model = []
    allm = attr_measures(s)
    for m in sorted({k[0] for k in s}):
        for k, mt in allm.items():
            one = {key: v for key, v in mt.items() if key[0] == m}
            if one:
                per_model.append(("attr1", k, m, one_model(one, draws)))
    return out, per_model


# ---------------------------------------------------------------- the store (Study 1c)

def study_store(paths, draws):
    import store as H  # the store's functions (store.py)
    c, src = {}, {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf8")):
            k = (r["model"], r["table"], r["arm"], r["names"])
            if k in c:
                raise SystemExit(f"REFUSED: the store cell {k} is in two cells files")
            c[k] = [int(r["parsed"]), int(r["best"]), int(r["labelled"])]
            src[r["model"]] = p
    levels = sorted({k[2] for k in c if k[2] != STORE_REF})
    # the store's clusters are sorted, so its numbers are the same under every PYTHONHASHSEED
    srt = lambda d: dict(sorted(d.items()))
    changes = {arm: srt(H.per_mt(c, H.change(arm))) for arm in levels}
    est = H.estimate_groups({"change": changes}, draws)["change"]
    fam = {arm: v["interval"]["p_two_sided"] for arm, v in est.items() if v.get("interval")}
    order, run = sorted(fam, key=fam.get), 0.0
    for i, arm in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * fam[arm]))
        est[arm]["holm"] = run

    def brief(v):
        iv = v.get("interval") or {}
        out = {"estimate": round(v["pooled"], 4), "ci95": [round(iv.get("low95", float("nan")), 4),
                                                           round(iv.get("high95", float("nan")), 4)],
               "p_two_sided": round(iv.get("p_two_sided", float("nan")), 4), "models": len(v["per_model"])}
        if "holm" in v:      # only the 15 changes form the Holm family
            out["p_holm"] = round(v["holm"], 4)
        return out
    gap = srt(H.per_mt(c, H.gap(STORE_REF)))
    out = {"models": sorted({k[0] for k in c}), "sources": sorted(set(src.values())), "arms_in_holm": len(fam),
           "change by arm, D(arm) = g(arm) - g(plain)": {arm: brief(v) for arm, v in est.items()},
           "gap in the plain arm": brief(H.estimate(gap, draws)), "by_group": {}, "group_differences": {}}
    mt = changes[STORE_ARM]
    sub = {g: {k: v for k, v in mt.items() if group_of(k[0]) == g} for g in GROUPS}
    for g in GROUPS:
        if sub[g]:
            out["by_group"][g] = brief(H.estimate(sub[g], draws))
    present = [g for g in GROUPS if sub[g]]
    for i, a in enumerate(present):
        for b in present[i + 1:]:
            out["group_differences"][f"{a} minus {b}, change with {STORE_ARM}"] = group_diff(sub[a], sub[b], DRAWS)
    per_model = [("store", f"change with {STORE_ARM}", m,
                  one_model({k: v for k, v in mt.items() if k[0] == m}, DRAWS)) for m in sorted({k[0] for k in mt})]
    return out, per_model


# ---------------------------------------------------------------- main

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", action="append", required=True)
    ap.add_argument("--store-cells", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--store-draws", type=int, default=10000, help="the store's own plan uses 10,000")
    ap.add_argument("--only", default="", help="comma-separated parts: 2a,2b,2c,store (default: all)")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else {"2a", "2b", "2c", "attr", "store"}
    t0 = time.time()
    rows = read_counts(a.counts)
    dev = developers()
    res = {"source": {"script": "study2a-experience-attributes-stated-for-every-product/code/pool_all.py", "plan": "study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 11",
                      "counts": [{"file": os.path.relpath(p, ROOT).replace("\\", "/"), "sha256": sha(p)} for p in a.counts],
                      "store_cells": [{"file": os.path.relpath(p, ROOT).replace("\\", "/"), "sha256": sha(p)}
                                      for p in a.store_cells],
                      "bootstrap": {"draws": a.draws, "store_draws": a.store_draws, "seed": SEED,
                                    "clusters": "tables and models, resampled independently"},
                      "groups": "Anthropic: the Claude models; OpenAI: the GPT-6 models through Codex; open weights: "
                                "every model served from its open weights on the computing cluster, OpenAI's gpt-oss included"}}
    per_model = []
    for build, part in (("dom2", "2a"), ("split1", "2b"), ("eq1", "2c"), ("attr1", "attr")):
        if part not in only:
            continue
        if build in TABLE_RULE:
            exp = expected_cells(build)
            TABLES_OF[build] = {k[0] for k in exp}
            tin = complete_tables(rows, build, exp)
            sc = screen(rows, build, tin)
            # each model's rows of this build only on the tables it answered in every condition
            use = [r for r in rows if r["build"] != build or r["table"] in tin.get(r["model"], ())]
        else:
            sc = screen(rows, build)
            use = rows
        res[f"{part}_screen"] = sc
        ok = sorted(m for m, v in sc.items() if v["verdict"] == "in")
        print(f"{part} ({build}): {len(ok)} of {len(sc)} models in; {time.time() - t0:.0f} s", flush=True)
        if part == "2a":
            res["2a"], pm = study2a(use, set(ok), a.draws)
            per_model += pm
        elif part == "2b":
            res["2b"], pm = study2b(use, set(ok), a.draws)
            per_model += pm
        elif part == "2c":
            res["2c"], pm = study2c(use, ok, a.draws)
            per_model += pm
        else:
            res["attr"], pm = study_attr(use, set(ok), a.draws)
            per_model += pm
        print(f"{part} done; {time.time() - t0:.0f} s", flush=True)
    if "store" in only and a.store_cells:
        res["store"], pm = study_store(a.store_cells, a.store_draws)
        per_model += pm
        print(f"store done; {time.time() - t0:.0f} s", flush=True)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, "per_model.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")    # git keeps LF, so the file's SHA-256 is the same in every clone
        w.writerow(["study", "estimate_name", "model", "group", "developer", "open_weights", "estimate", "se", "ci95_low",
                    "ci95_high", "p_two_sided", "tables", "draws", "seed"])
        for study, name, m, s in per_model:
            w.writerow([study, name, m, group_of(m), dev.get(m, group_of(m)), group_of(m) == "open weights",
                        s["estimate"], s["se"], s["ci95"][0], s["ci95"][1], s["p_two_sided"], s["tables"], a.draws, SEED])
    print(f"wrote {a.out}/numbers.json and per_model.csv ({len(per_model)} rows) in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
