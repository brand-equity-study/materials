"""Amendment 2's behavioral ranking (PLAN.md): two candidates, both read from the read stage's letter probabilities
(A.jsonl), no new prompts, for each brand within its category (the plan's unit; 10 of the 63 brands are in two or more
categories):

  own:     the brand's own product, names shown (original cell) minus names hidden, in probability
  on_best: the best product with the brand's name (crossed cell) minus the original cell, in probability, for the
           brands that the crossed cell places on the best product

    python jmr-2026/mechanism/brand_criterion.py --a <A.jsonl.gz> --renderings <renderings.jsonl> [--out <json>]

The rule: the candidate with the higher split-half reliability on the 31B's full read is the ranking for every model,
if that reliability is at least 0.5. The reliability is the test's own statistic (analyze.within_corr: even-trial
against odd-trial unit means, ranked within category and the ranks scaled to run from -1 to 1, correlated over all
units), raised by the Spearman-Brown formula; the correlation pooled over categories is reported beside it, because
differences between categories raise it (PLAN.md, amendment 2, change of 21 November).
"""
import argparse
import gzip
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as AN  # noqa: E402

MIN_RELIABILITY = 0.5
MIN_UNITS = 30


def behavior_rows(A, rend, infos=(0,)):
    """One row a familiar product and trial: {kind, brand, category, table, trial, value}. The ranking reads the items
    without the information (infos=(0,)), as coded on 21 November 2026 at 12:05 AM, before job 11875's read was fetched
    (PLAN.md amendment 2, the note of 22 November); infos=(0, 1) gives the all-items version, which is exploratory and
    was added after reading the results (22 November 2026, 8:43 AM)."""
    cell = {(r["table"], r["trial"], r["names"], r["info"], r["rung"]): r for r in rend if r["kind"] == "dom2"}

    def prob(r, letter):
        x = A.get(r["id"])
        if x is None or x["lp"] is None:
            return None
        return math.exp(x["lp"]["ABCDE".index(letter)])

    rows = []
    for (t, trial, names, info, rung), o in cell.items():
        if names != "original" or info not in infos:
            continue
        h, c = cell[(t, trial, "hidden", info, rung)], cell[(t, trial, "crossed", info, rung)]
        for L, p in o["products"].items():
            if p["kind"].startswith("familiar"):
                po, ph = prob(o, L), prob(h, L)
                if po is not None and ph is not None:
                    rows.append({"kind": "own", "brand": p["true_brand"], "category": o["category"], "table": t,
                                 "trial": trial, "value": po - ph})
        b = c["products"][c["partner"]]["true_brand"]       # in the crossed cell the best product holds this name
        pc, po = prob(c, c["best"]), prob(o, o["best"])
        if pc is not None and po is not None:
            rows.append({"kind": "on_best", "brand": b, "category": c["category"], "table": t, "trial": trial,
                         "value": pc - po})
    return rows


def unit_halves(rows, kind):
    """{unit: (category, {(table, half): [values]})} for one kind of row."""
    d = defaultdict(lambda: [None, defaultdict(list)])
    for x in rows:
        if x["kind"] != kind:
            continue
        u = f"{x['brand']}|{x['category']}"
        d[u][0] = x["category"]
        d[u][1][(x["table"], x["trial"] % 2)].append(x["value"])
    return d


def summary(rows):
    """The two candidates' split-half reliabilities on the values that the test uses: centered within table
    (analyze.centered_halves; PLAN.md, amendment 2, change of about 6:20 AM)."""
    out = {}
    for kind in ("own", "on_best"):
        d = unit_halves(rows, kind)
        units = sorted(d)
        cats = [d[u][0] for u in units]
        ev, od = AN.centered_halves({u: d[u][1] for u in units})
        even = [ev.get(u) for u in units]
        odd = [od.get(u) for u in units]
        full = {u: float(np.mean([v for (t, h), vs in d[u][1].items() for v in vs])) for u in units}
        out[kind] = {"units": len(units), "brands": len({u.split("|")[0] for u in units}),
                     "categories_with_two_or_more_units": sum(1 for c in set(cats) if cats.count(c) >= 2),
                     "nonzero_above_0.001": sum(abs(v) > 1e-3 for v in full.values()),
                     "nonzero_above_0.01": sum(abs(v) > 1e-2 for v in full.values()),
                     "mean_points": round(100 * float(np.mean(list(full.values()))), 2) if full else None,
                     "split_half": AN.split_half(units, even, odd, cats),
                     "by_unit_points": {u: round(100 * v, 2) for u, v in sorted(full.items(), key=lambda kv: -kv[1])}}
    # a candidate counts only with at least MIN_UNITS units that keep a centered value in both halves, so that a few
    # tables of two units cannot show a reliability near 1 and be chosen (PLAN.md, amendment 2, change of about 6:30 AM)
    rel = {k: (out[k]["split_half"]["spearman_brown"] if out[k]["split_half"]["spearman_brown"] is not None
               and out[k]["split_half"]["units"] >= MIN_UNITS else -1) for k in out}
    best = max(rel, key=rel.get)
    out["chosen"] = best if rel[best] >= MIN_RELIABILITY else None
    out["rule"] = ("the candidate with the higher within-category split-half reliability (Spearman-Brown) among those "
                   f"with at least {MIN_UNITS} units with a centered value in both halves, if it is at least "
                   f"{MIN_RELIABILITY}; otherwise the ranking test has no power on these tables")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--renderings", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    op = gzip.open if a.a.endswith(".gz") else open
    A = {}
    with op(a.a, "rt", encoding="utf8") as f:
        for line in f:
            x = json.loads(line)
            A[x["id"]] = x
    rend = [json.loads(line) for line in open(a.renderings, encoding="utf8")]
    out = summary(behavior_rows(A, rend))
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "by_unit_points"} if isinstance(v, dict) else v)
                      for k, v in out.items()}, indent=1))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
    return out


if __name__ == "__main__":
    main()
