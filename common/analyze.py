"""Study 1, the controlled test: read the answers and compute the contrasts of the analysis plan.

    python common/analyze.py --set strictly-better-tables --thin <tables> --out study1a-tables-with-one-optimal-product/results/strictly-better-tables

For every answer: the letter (parse_answer.py) and whether it is the best product. Per model, table and cell: the
share of answers that pick the best product. Then, for each model, table, information level and price rung:
  penalty  = share best with names hidden  - share best with the original names (the invented name on the best product)
  premium  = share best with the crossed names (a familiar name on the best product) - share best with names hidden
  info change = penalty with the information supplied - penalty without it
Pooled estimates weight every table equally within a model and every model equally. Intervals: a two-way cluster
bootstrap that resamples tables and models with replacement (--draws, seed 20261120); with fewer than three tables or
three models no interval is computed.

Reads study1a-tables-with-one-optimal-product/materials/<set>/prompts.jsonl.gz and study1a-tables-with-one-optimal-product/data/<set>/<model>/<cell>.jsonl.gz. Writes <out>/answers.csv
(one row per answer), <out>/cells.csv and <out>/numbers.json, and prints the tables.
"""
import argparse
import csv
import glob
import gzip
import json
import os
import random
import re
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parse_answer import pick  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))   # the package
STUDY = os.path.join(ROOT, "study1a-tables-with-one-optimal-product")   # the default home of a set's prompts and answers


def budget(it):
    """(low, high, outside) for the best product's price against the budget the request states: a range "$600-800"
    gives both bounds, "under $400" an upper bound; outside is "below", "above" or ""."""
    req = it["user"].split("\n", 1)[0]
    lo = hi = None
    m = re.search(r"\$(\d[\d,]*)\s*-\s*\$?(\d[\d,]*)", req)
    if m:
        lo, hi = float(m.group(1).replace(",", "")), float(m.group(2).replace(",", ""))
    else:
        m = re.search(r"(?:under|below|less than)\s+\$(\d[\d,]*)", req, re.I)
        if m:
            hi = float(m.group(1).replace(",", ""))
    price = it["products"][it["best"]]["price"]
    outside = "below" if lo is not None and price < lo else "above" if hi is not None and price > hi else ""
    return lo, hi, outside


def _read_gz(path):
    with gzip.open(path, "rt", encoding="utf8") as f:
        return [json.loads(line) for line in f]


def load(build, models=None, studies=None):
    """The prompts of a set of tables and every answer to them, as the analysis reads them. studies: the package's
    study folders whose data/<set>/ folders hold answers to this set (default: this study's own folder); the prompts
    are read from the first of them that holds materials/<set>/."""
    roots = [os.path.join(ROOT, s) for s in studies] if studies else [STUDY]
    mat = next(os.path.join(r, "materials", build, "prompts.jsonl.gz") for r in roots
               if os.path.exists(os.path.join(r, "materials", build, "prompts.jsonl.gz")))
    items = {}
    for it in _read_gz(mat):
        it["budget_low"], it["budget_high"], it["outside_budget"] = budget(it)
        items[it["id"]] = it
    rows, runs = [], {}
    for mdir in sorted(d for r in roots for d in glob.glob(os.path.join(r, "data", build, "*"))):
        if not os.path.isdir(mdir):
            continue
        model = os.path.basename(mdir)
        if models and model not in models:
            continue
        stats = {}
        for f in sorted(glob.glob(os.path.join(mdir, "*.jsonl.gz"))):
            for r in _read_gz(f):
                iid = r["id"]
                if iid not in items:
                    continue
                stats[iid] = {"at": r["answered_at_utc"], "model": r["model_returned"], "via": r["route"],
                              "stop_reason": r.get("stop_reason"), "input_tokens": r.get("input_tokens"),
                              "output_tokens": r.get("output_tokens"),
                              "cache_read_input_tokens": r.get("cache_read_input_tokens"),
                              "cache_creation_input_tokens": r.get("cache_creation_input_tokens"), "file": f"{iid}.md"}
                ans = r["answer_text"]
                it = items[iid]
                L, how = pick(ans)
                p = it["products"].get(L, {}) if L else {}
                rows.append({"model": model, "id": iid, "table": it["table"], "trial": it["trial"], "names": it["names"],
                             "info": it["info"], "rung": it["rung"], "paraphrase": it["paraphrase"], "best": it["best"],
                             "best_price": it["products"][it["best"]]["price"], "outside_budget": it["outside_budget"],
                             "letter": L, "how": how, "is_best": int(L == it["best"]) if L else "",
                             "picked_true_brand": p.get("true_brand", ""), "picked_shown_kind": p.get("kind", ""),
                             "picked_true_kind": p.get("true_kind", ""), "answer": ans})
        runs[model] = stats
    return items, rows, runs


def shares(rows):
    """{(model, table, names, info, rung): [n parsed, n best]}"""
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["letter"]:
            k = (r["model"], r["table"], r["names"], r["info"], r["rung"])
            c[k][0] += 1
            c[k][1] += r["is_best"]
    return c


def contrasts(c):
    """{(model, table, info, rung): {"penalty", "premium", "s_hidden", "s_original", "s_crossed"}}"""
    out = {}
    keys = {(m, t, i, g) for (m, t, n, i, g) in c}
    for m, t, i, g in sorted(keys, key=str):   # sorted, so the order does not change with PYTHONHASHSEED
        s = {}
        for n in ("hidden", "original", "crossed"):
            n_, b = c.get((m, t, n, i, g), [0, 0])
            s[n] = b / n_ if n_ else None
        if None in s.values():
            continue
        out[(m, t, i, g)] = {"s_hidden": s["hidden"], "s_original": s["original"], "s_crossed": s["crossed"],
                             "penalty": s["hidden"] - s["original"], "premium": s["crossed"] - s["hidden"],
                             "swap": s["crossed"] - s["original"]}
    for (m, t, i, g), v in list(out.items()):
        if i == 1 and (m, t, 0, g) in out:
            v["info_change"] = v["penalty"] - out[(m, t, 0, g)]["penalty"]
    return out


def pooled(con, stat, info=None, rung=None, tables=None, exclude=frozenset()):
    """Equal weight per table within a model, equal weight per model; None when nothing qualifies. exclude holds
    (table, rung) pairs left out."""
    by_model = defaultdict(list)
    for (m, t, i, g), v in con.items():
        if (t, g) in exclude:
            continue
        if stat in v and (info is None or i == info) and (rung is None or g == rung) and (tables is None or t in tables):
            by_model[(m, t)].append(v[stat])
    per_mt = {k: sum(x) / len(x) for k, x in by_model.items()}
    models = sorted({m for m, t in per_mt})
    if not models:
        return None, per_mt
    per_m = [sum(v for (mm, t), v in per_mt.items() if mm == m) / sum(1 for (mm, t) in per_mt if mm == m) for m in models]
    return sum(per_m) / len(per_m), per_mt


def bootstrap(per_mt, draws, seed=20261120):
    """Two-way cluster bootstrap over models and tables of the pooled mean; (low, high) of the 95 per cent interval."""
    models = sorted({m for m, t in per_mt})
    tables = sorted({t for m, t in per_mt})
    if len(models) < 3 or len(tables) < 3:
        return None
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        ms = [rng.choice(models) for _ in models]
        ts = [rng.choice(tables) for _ in tables]
        per_m = []
        for m in ms:
            x = [per_mt[(m, t)] for t in ts if (m, t) in per_mt]
            if x:
                per_m.append(sum(x) / len(x))
        if per_m:
            vals.append(sum(per_m) / len(per_m))
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def ci_and_p(per_mt, draws, seed=20261120):
    """bootstrap()'s 95 per cent interval and a two-sided P value from the same draws (twice the share of draws on the
    far side of zero); draws_of draws them in the same order as bootstrap(). (None, None) where bootstrap() gives
    None. Every bootstrap interval has its P value."""
    if len({m for m, t in per_mt}) < 3 or len({t for m, t in per_mt}) < 3:
        return None, None
    vals = draws_of(per_mt, draws, seed)
    n = len(vals)
    p = min(1.0, 2 * min(sum(v <= 0 for v in vals) / n, sum(v >= 0 for v in vals) / n))
    return (vals[int(0.025 * n)], vals[int(0.975 * n) - 1]), p


def draws_of(per_mt, draws, seed=20261120, fixed_models=False):
    """The bootstrap draws of the pooled mean: tables and models resampled independently (models kept as they are when
    fixed_models, for one model's own interval)."""
    models = sorted({m for m, t in per_mt})
    tables = sorted({t for m, t in per_mt})
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        ms = models if fixed_models else [rng.choice(models) for _ in models]
        ts = [rng.choice(tables) for _ in tables]
        per_m = []
        for m in ms:
            x = [per_mt[(m, t)] for t in ts if (m, t) in per_mt]
            if x:
                per_m.append(sum(x) / len(x))
        if per_m:
            vals.append(sum(per_m) / len(per_m))
    return sorted(vals)


def summary(est, vals):
    q = lambda p: vals[min(len(vals) - 1, max(0, int(round(p * (len(vals) - 1)))))]
    below = sum(v <= 0 for v in vals) / len(vals)
    above = sum(v >= 0 for v in vals) / len(vals)
    return {"estimate": round(est, 4), "ci95": [round(q(0.025), 4), round(q(0.975), 4)],
            "ci90": [round(q(0.05), 4), round(q(0.95), 4)], "p_two_sided": round(min(1.0, 2 * min(below, above)), 4)}


def holm(ps):
    """Holm's adjusted P values, in the order given."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = round(run, 4)
    return adj


def primary_report(con, draws, margin=0.02):
    """The primary contrast and its outcome, and the secondary family with Holm's correction."""
    out = {}
    g0_est, g0_mt = pooled(con, "penalty", info=0)
    g1_est, g1_mt = pooled(con, "penalty", info=1)
    d_est, d_mt = pooled(con, "info_change", info=1)
    g0, g1, d = summary(g0_est, draws_of(g0_mt, draws)), summary(g1_est, draws_of(g1_mt, draws)), summary(d_est, draws_of(d_mt, draws))
    out["gap_none"], out["gap_supplied"], out["change"] = g0, g1, d
    if g0["ci95"][0] <= 0:
        outcome = "no gap to explain"
    elif d["ci95"][1] < 0 and -margin < g1["ci90"][0] and g1["ci90"][1] < margin:
        outcome = "the gap closes"
    elif d["ci95"][1] < 0:
        outcome = "the gap narrows"
    else:
        outcome = "the gap stays"
    out["outcome"] = outcome
    out["equivalence_margin"] = margin
    # secondary family
    fam = {}
    rd = {}
    for (m, t, i, g), v in con.items():
        if i == 0 and g == 2 and (m, t, 0, 0) in con:
            rd[(m, t)] = v["penalty"] - con[(m, t, 0, 0)]["penalty"]
    if rd:
        e = sum(sum(v for (mm, t), v in rd.items() if mm == m) / sum(1 for (mm, t) in rd if mm == m)
                for m in sorted({m for m, t in rd})) / len({m for m, t in rd})
        fam["gap at 30 per cent below minus gap at equal price, no information"] = summary(e, draws_of(rd, draws))
    for info in (0, 1):
        e, mt = pooled(con, "premium", info=info)
        fam[f"premium for a familiar name, information {'supplied' if info else 'none'}"] = summary(e, draws_of(mt, draws))
    for m in sorted({k[0] for k in con}):
        for stat, info, label in (("penalty", 0, "gap with no information"), ("info_change", 1, "change when supplied")):
            sub = {k: v for k, v in con.items() if k[0] == m}
            e, mt = pooled(sub, stat, info=info)
            fam[f"{m}: {label}"] = summary(e, draws_of(mt, draws, fixed_models=True))
    for k, v in zip(fam, holm([v["p_two_sided"] for v in fam.values()])):
        fam[k]["p_holm"] = v
    out["secondary"] = fam
    return out


def swap_report(con, draws):
    """EXPLORATORY, not in the analysis plan (chosen after the primary results were seen): the same best product under a familiar name against under the
    invented name, the share that picks it with the crossed names minus the share with the original names. Pooled over
    the models (two-way cluster bootstrap) and for each model (bootstrap over tables), with no information and with it;
    Holm over this family alone."""
    fam = {}
    for info, label in ((0, "no information"), (1, "information supplied")):
        e, mt = pooled(con, "swap", info=info)
        if e is not None and len({m for m, t in mt}) >= 3:
            fam[f"pooled, {label}"] = summary(e, draws_of(mt, draws))
        for m in sorted({k[0] for k in con}):
            sub = {k: v for k, v in con.items() if k[0] == m}
            e, mt = pooled(sub, "swap", info=info)
            if e is not None:
                fam[f"{m}, {label}"] = summary(e, draws_of(mt, draws, fixed_models=True))
    for k, v in zip(fam, holm([v["p_two_sided"] for v in fam.values()])):
        fam[k]["p_holm"] = v
    return {"note": swap_report.__doc__.split("\n\n")[0].replace("\n", " "), "estimates": fam}


SPLIT = ("warranty", "failure", "market", "lab", "returns")


def split_report(con, draws):
    """The information split: the name gap in each information condition, and each single item's gap against no
    information and against all five items, pooled over models; Holm over the ten contrasts."""
    out = {"gap": {}, "contrasts": {}}
    for level in (0,) + SPLIT + (1,):
        e, mt = pooled(con, "penalty", info=level)
        if e is not None:
            out["gap"][str(level)] = summary(e, draws_of(mt, draws)) if len({m for m, t in mt}) >= 3 else {"estimate": round(e, 4)}
    for s in SPLIT:
        for ref, label in ((0, "none"), (1, "all five")):
            d = {}
            for (m, t, i, g), v in con.items():
                if i == s and (m, t, ref, g) in con:
                    d.setdefault((m, t), []).append(v["penalty"] - con[(m, t, ref, g)]["penalty"])
            d = {k: sum(v) / len(v) for k, v in d.items()}
            if not d:
                continue
            ms = sorted({m for m, t in d})
            e = sum(sum(v for (mm, t), v in d.items() if mm == m) / sum(1 for (mm, t) in d if mm == m) for m in ms) / len(ms)
            out["contrasts"][f"{s} alone minus {label}"] = summary(e, draws_of(d, draws))
    for k, v in zip(out["contrasts"], holm([v["p_two_sided"] for v in out["contrasts"].values()])):
        out["contrasts"][k]["p_holm"] = v
    # Reported beside the family without correction: the
    # three shares, the name gap and the familiar-name premium in each information condition, pooled and for each model. A pooled interval
    # resamples tables and models; one model's interval resamples tables only. P values are two-sided, uncorrected.
    def est(stat, level, model=None):
        sub = {k: v for k, v in con.items() if model is None or k[0] == model}
        e, mt = pooled(sub, stat, info=level)
        if e is None:
            return None
        if model is None and len({m for m, t in mt}) < 3:
            return {"estimate": round(e, 4)}
        s = summary(e, draws_of(mt, draws, fixed_models=model is not None))
        return s if stat in ("penalty", "premium") else {"estimate": s["estimate"], "ci95": s["ci95"]}
    models = sorted({k[0] for k in con})
    stats = (("share_hidden", "s_hidden"), ("share_invented_on_best", "s_original"), ("share_familiar_on_best", "s_crossed"),
             ("name_gap", "penalty"), ("familiar_premium", "premium"))
    out["by_level"] = {str(level): {name: est(stat, level) for name, stat in stats} for level in (0,) + SPLIT + (1,)}
    out["by_model"] = {m: {str(level): {name: est(stat, level, m) for name, stat in stats}
                           for level in (0,) + SPLIT + (1,)}
                       for m in models}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="build", required=True, help="strictly-better-tables or original-tables")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--out")
    ap.add_argument("--dominant", default="")
    ap.add_argument("--models", default="", help="comma-separated model folders to read (default: every folder)")
    ap.add_argument("--thin", default="", help="comma-separated tables reported apart as a sensitivity subset")
    ap.add_argument("--without", action="append", default=[],
                    help="label=table,table: a robustness subset that leaves those tables out (repeatable)")
    a = ap.parse_args()
    out = a.out or os.path.join(STUDY, "results", a.build)
    os.makedirs(out, exist_ok=True)
    items, rows, runs = load(a.build, set(a.models.split(",")) if a.models else None)
    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    src = {"script": "common/analyze.py", "prompts": f"study1a-tables-with-one-optimal-product/materials/{a.build}/prompts.jsonl.gz",
           "answers": f"study1a-tables-with-one-optimal-product/data/{a.build}/"}

    # every answer, and the parser on every answer
    with open(os.path.join(out, "answers.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != "answer"] + ["first_line"])
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["model"], r["table"], r["trial"], r["names"], str(r["info"]), r["rung"])):
            w.writerow({**{k: v for k, v in r.items() if k != "answer"},
                        "first_line": next((l for l in r["answer"].split("\n") if l.strip()), "")[:80]})
    models = sorted({r["model"] for r in rows})
    expected = len(items)
    print(f"build {a.build}: {expected} prompts per model")
    parse = {}
    for m in models:
        rm = [r for r in rows if r["model"] == m]
        hows = defaultdict(int)
        for r in rm:
            hows[r["how"]] += 1
        st = [v for v in runs.get(m, {}).values() if v.get("file")]
        tin = [v.get("input_tokens", 0) + v.get("cache_read_input_tokens", 0) + v.get("cache_creation_input_tokens", 0) for v in st]
        tout = [v.get("output_tokens", 0) for v in st]
        stops = defaultdict(int)
        for v in st:
            stops[v.get("stop_reason")] += 1
        dates = sorted(v.get("at", "")[:10] for v in st if v.get("at"))
        parse[m] = {"answers": len(rm), "missing": expected - len(rm), **hows,
                    "excluded_for_tool_use": sum(1 for v in st if v.get("excluded")),
                    "via": sorted({v.get("via", "") for v in st}),
                    "codex_versions": sorted({v["codex_version"] for v in st if v.get("codex_version")}),
                    "efforts": sorted({v["effort"] for v in st if v.get("effort")}),
                    "model_ids": sorted({v.get("model") for v in st}), "dates_utc": [dates[0], dates[-1]] if dates else [],
                    "mean_input_tokens": round(sum(tin) / len(tin)) if tin else None,
                    "mean_output_tokens": round(sum(tout) / len(tout)) if tout else None,
                    "max_output_tokens": max(tout) if tout else None, "stop_reasons": dict(stops)}
        print(f"  {m}: {len(rm)} answers, {expected - len(rm)} missing; parsed {dict(hows)}; "
              f"tokens in {parse[m]['mean_input_tokens']}, out {parse[m]['mean_output_tokens']} (max {parse[m]['max_output_tokens']}); stops {dict(stops)}")

    c = shares(rows)
    with open(os.path.join(out, "cells.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "table", "names", "info", "rung", "parsed", "best", "share_best"])
        for k in sorted(c, key=lambda k: tuple(str(x) for x in k)):   # information levels mix numbers and words
            w.writerow([*k, c[k][0], c[k][1], round(c[k][1] / c[k][0], 4) if c[k][0] else ""])

    print("\nshare of answers that pick the best product (count of parsed answers)")
    print("| model | table | info | rung | hidden | original | crossed |")
    print("|---|---|---|---|---|---|---|")
    rungs_here = sorted({k[4] for k in c})
    for m in models:
        for t in sorted({k[1] for k in c if k[0] == m}):
            for i in (0, 1):
                for g in rungs_here:
                    cell = lambda n: c.get((m, t, n, i, g))
                    fmt = lambda x: f"{x[1]} of {x[0]}" if x else "-"
                    print(f"| {m} | {t} | {i} | {g} | {fmt(cell('hidden'))} | {fmt(cell('original'))} | {fmt(cell('crossed'))} |")

    con = contrasts(c)
    dom = set(a.dominant.split(",")) if a.dominant else None
    # sensitivity subsets: cells whose best product is cheaper than the stated range (it still meets the request), and
    # cells whose best product is dearer than the stated budget (it, and every other product there, breaks the request)
    below = frozenset((it["table"], it["rung"]) for it in items.values() if it["outside_budget"] == "below")
    above = frozenset((it["table"], it["rung"]) for it in items.values() if it["outside_budget"] == "above")
    subsets = [("all", None, frozenset())]
    if dom:
        subsets.append(("dominant", dom, frozenset()))
    if below:
        subsets.append(("without-below-range", None, below))
    if above:
        subsets.append(("without-above-budget", None, above))
    if a.thin:
        thin = set(a.thin.split(","))
        subsets.append(("without-thin-tables", None,
                        frozenset((it["table"], it["rung"]) for it in items.values() if it["table"] in thin)))
    without = {}
    for spec in a.without:
        label, _, tabs = spec.partition("=")
        drop = set(tabs.split(","))
        without[label] = frozenset((it["table"], it["rung"]) for it in items.values() if it["table"] in drop)
        subsets.append((f"without-{label}", None, without[label]))
    numbers = {"build": a.build, "source": src, "parse": parse, "estimates": {},
               "best_below_stated_range": sorted(f"{t} rung {g}" for t, g in below),
               "best_above_stated_budget": sorted(f"{t} rung {g}" for t, g in above),
               "without": {label: sorted({t for t, g in drop}) for label, drop in without.items()}}
    print(f"\nbest product cheaper than the stated range: {sorted(below)}\nbest product above the stated budget: {sorted(above)}")
    print("\npooled estimates (share points; equal weight per table, then per model)")
    for stat in ("penalty", "premium", "info_change"):
        for info in ((None, 0, 1) if stat != "info_change" else (1,)):
            for rung in (None, 0, 1, 2):
                for subset, tabs, excl in subsets:
                    est, per_mt = pooled(con, stat, info, rung, tabs, excl)
                    if est is None:
                        continue
                    ci, p = ci_and_p(per_mt, a.draws)
                    key = f"{stat}|info={'pooled' if info is None else info}|rung={'pooled' if rung is None else rung}|{subset}"
                    numbers["estimates"][key] = {"estimate": round(est, 4), "ci95": [round(x, 4) for x in ci] if ci else None,
                                                 "p_two_sided": round(p, 4) if p is not None else None,
                                                 "models": len({m for m, t in per_mt}), "tables": len({t for m, t in per_mt}),
                                                 "per_model": {m: round(sum(v for (mm, t), v in per_mt.items() if mm == m) /
                                                                        sum(1 for (mm, t) in per_mt if mm == m), 4)
                                                               for m in sorted({m for m, t in per_mt})}}
                    print(f"  {key}: {est:+.3f}" + (f" [{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else ""))
    numbers["bootstrap"] = {"draws": a.draws, "seed": 20261120, "clusters": "tables and models, resampled independently"}
    if any(isinstance(k[2], str) for k in con) and len({k[1] for k in con}) >= 3:
        sp = split_report(con, a.draws)
        numbers["split"] = sp
        for label, drop in without.items():
            numbers[f"split_without_{label}"] = split_report({k: v for k, v in con.items() if (k[1], k[3]) not in drop}, a.draws)
        print("\nINFORMATION SPLIT: the name gap in each information condition")
        for k, v in sp["gap"].items():
            print(f"  {k}: {v['estimate']:+.3f}" + (f" [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]" if "ci95" in v else ""))
        print("each item alone against none and against all five (Holm over the ten):")
        for k, v in sp["contrasts"].items():
            print(f"  {k}: {v['estimate']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] P {v['p_two_sided']} Holm {v['p_holm']}")
    elif len(models) >= 3 and len({k[1] for k in con}) >= 3:
        sw = swap_report(con, a.draws)
        numbers["swap_exploratory"] = sw
        print("\nEXPLORATORY (not in the plan): crossed minus original names, the best product's share; Holm over this family")
        for k, v in sw["estimates"].items():
            print(f"  {k}: {v['estimate']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] P {v['p_two_sided']} Holm {v['p_holm']}")
        pr = primary_report(con, a.draws)
        numbers["primary"] = pr
        print(f"\nPRIMARY: outcome: {pr['outcome']}")
        for k in ("gap_none", "gap_supplied", "change"):
            print(f"  {k}: {pr[k]}")
        print("SECONDARY (Holm over the family):")
        for k, v in pr["secondary"].items():
            print(f"  {k}: {v['estimate']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] P {v['p_two_sided']} Holm {v['p_holm']}")
    elif len({k[1] for k in con}) >= 3:
        # one or two models (a replication model reported apart): each model's estimates, bootstrap over tables only
        per = {}
        for m in models:
            sub = {k: v for k, v in con.items() if k[0] == m}
            row = {}
            for key, stat, info in (("gap_none", "penalty", 0), ("gap_supplied", "penalty", 1), ("change", "info_change", 1),
                                    ("premium_none", "premium", 0)):
                e, mt = pooled(sub, stat, info=info)
                if e is not None:
                    row[key] = summary(e, draws_of(mt, a.draws, fixed_models=True))
            per[m] = row
            print(f"\nMODEL {m} (bootstrap over tables):")
            for key, v in row.items():
                print(f"  {key}: {v['estimate']:+.3f} 95% [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] 90% [{v['ci90'][0]:+.3f}, {v['ci90'][1]:+.3f}] P {v['p_two_sided']}")
        numbers["per_model"] = per
    with open(os.path.join(out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    print(f"\nwrote {rel(out)}/answers.csv, cells.csv, numbers.json")


if __name__ == "__main__":
    main()
