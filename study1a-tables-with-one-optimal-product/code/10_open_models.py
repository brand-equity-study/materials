"""The results of the models with open weights, as their analysis plan fixed them before any of these models answered.

Input: study1a-tables-with-one-optimal-product/results/open_models_counts.csv (09_open_model_counts.py: answers, parsed and best picked for each set,
model, table, cell and price level). Output: study1a-tables-with-one-optimal-product/results/open_models.json and a printed table.

On the tables of Study 1 (the original tables and the strictly better tables): for each model and table, the
best-product share in each cell averaged over the price levels; the name gap g = share with names hidden minus share
with the invented name on the best product, without the information (info 0) and with it (info 1); its change,
g(info 1) minus g(info 0); tables weighted equally within a model, then models equally. On the rerun's prompts: the
share of recommendations away from the best product with names shown minus with names hidden, and minus with names
hidden after the leaks were cleaned. Intervals: a two-way cluster bootstrap that resamples tables and models
independently with replacement, 2,000 draws, seed 20261120, as in the analysis plan of Study 1.

    python study1a-tables-with-one-optimal-product/code/10_open_models.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import json
import random
import sys
from collections import defaultdict

DRAWS, SEED = 2000, 20261120


def load(path):
    cells = defaultdict(lambda: [0, 0])  # (build, model, table, names, info, rung) -> [best, answers]
    parsed = defaultdict(lambda: [0, 0])
    for r in csv.DictReader(open(path, encoding="utf-8")):
        k = (r["set"], r["model"], r["table"], r["names"], r["info"], r["rung"])
        cells[k][0] += int(r["best_picked"])
        cells[k][1] += int(r["answers"])
        parsed[(r["set"], r["model"])][0] += int(r["parsed"])
        parsed[(r["set"], r["model"])][1] += int(r["answers"])
    return cells, parsed


def table_shares(cells, build, ignore_info=False):
    """{model: {table: {(names, info): share averaged over price levels}}}; the rerun's prompts have no information condition,
    so their cells are identified by the names condition alone (info written as "")."""
    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for (b, m, t, n, i, _rung), (best, ans) in cells.items():
        if b == build and ans:
            acc[m][t][(n, "" if ignore_info else i)].append(best / ans)
    return {m: {t: {c: sum(v) / len(v) for c, v in cs.items()} for t, cs in ts.items()} for m, ts in acc.items()}


def contrast(shares, a, b):
    """{model: {table: share(a) - share(b)}} over the tables that hold both cells."""
    out = {}
    for m, ts in shares.items():
        d = {t: cs[a] - cs[b] for t, cs in ts.items() if a in cs and b in cs}
        if d:
            out[m] = d
    return out


def pooled(by_model):
    return sum(sum(d.values()) / len(d) for d in by_model.values()) / len(by_model)


def boot(by_model, rng):
    models = list(by_model)
    tables = sorted({t for d in by_model.values() for t in d})
    est = []
    for _ in range(DRAWS):
        ms = [rng.choice(models) for _ in models]
        ts = [rng.choice(tables) for _ in tables]
        vals = []
        for m in ms:
            v = [by_model[m][t] for t in ts if t in by_model[m]]
            if v:
                vals.append(sum(v) / len(v))
        if vals:
            est.append(sum(vals) / len(vals))
    est.sort()
    return est[int(0.025 * len(est))], est[int(0.975 * len(est)) - 1], est


def p_two_sided(est):
    """The paper's bootstrap p-value (as in common/analyze.py, summary): twice the smaller of the shares of draws at
    or below zero and at or above zero, capped at 1."""
    if not est:
        return None
    return round(min(1.0, 2 * min(sum(v <= 0 for v in est) / len(est), sum(v >= 0 for v in est) / len(est))), 4)


def summarize(by_model, rng):
    lo, hi, est = boot(by_model, rng)
    return {"points": round(100 * pooled(by_model), 2), "ci95": [round(100 * lo, 2), round(100 * hi, 2)], "p_two_sided": p_two_sided(est),
            "models": len(by_model),
            "by_model": {m: round(100 * sum(d.values()) / len(d), 2) for m, d in sorted(by_model.items())}}


REPO = __import__("pathlib").Path(__file__).resolve().parents[2]  # the top of the replication package
COUNTS = REPO / "study1a-tables-with-one-optimal-product" / "results" / "open_models_counts.csv"
OUT = REPO / "study1a-tables-with-one-optimal-product" / "results" / "open_models.json"


def main():
    cells, parsed = load(COUNTS)
    rng = random.Random(SEED)
    res = {"draws": DRAWS, "seed": SEED, "tables_of_study1": {}, "rerun": {}}
    for build in ("original-tables", "strictly-better-tables"):  # in this order, as the random draws follow it
        sh = table_shares(cells, build)
        g0 = contrast(sh, ("hidden", "0"), ("original", "0"))
        g1 = contrast(sh, ("hidden", "1"), ("original", "1"))
        change = {m: {t: g1[m][t] - g0[m][t] for t in g0[m] if t in g1.get(m, {})} for m in g0 if m in g1}
        accuracy = {m: round(100 * sum(cs.get(("hidden", "0"), 0) for cs in ts.values()) / len(ts), 1)
                    for m, ts in sh.items()}
        res["tables_of_study1"][build] = {"gap_no_information": summarize(g0, rng), "gap_with_information": summarize(g1, rng),
                                "change": summarize(change, rng),
                                "best_share_names_hidden_no_information": accuracy,
                                "parsed_pct": {m: round(100 * p[0] / p[1], 1) for (b, m), p in parsed.items()
                                               if b == build}}
    build = "rerun"
    sh = table_shares(cells, build, ignore_info=True)
    # away from the best = 1 - best share, so (away shown - away hidden) = best hidden - best shown
    res["rerun"] = {
        "gap_shown_minus_hidden": summarize(contrast(sh, ("hidden", ""), ("shown", "")), rng),
        "gap_shown_minus_hidden_cleaned": summarize(contrast(sh, ("hidden_clean", ""), ("shown", "")), rng),
        "parsed_pct": {m: round(100 * p[0] / p[1], 1) for (b, m), p in parsed.items() if b == build}}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    for build, r in res["tables_of_study1"].items():
        print(f"{build}: gap {r['gap_no_information']['points']} {r['gap_no_information']['ci95']} -> with information"
              f" {r['gap_with_information']['points']} {r['gap_with_information']['ci95']}; change {r['change']['points']}"
              f" {r['change']['ci95']} over {r['gap_no_information']['models']} models")
    s1 = res["rerun"]
    print(f"rerun: gap {s1['gap_shown_minus_hidden']['points']} {s1['gap_shown_minus_hidden']['ci95']};"
          f" against the cleaned prompts {s1['gap_shown_minus_hidden_cleaned']['points']}"
          f" {s1['gap_shown_minus_hidden_cleaned']['ci95']} over {s1['gap_shown_minus_hidden']['models']} models")


if __name__ == "__main__":
    main()
