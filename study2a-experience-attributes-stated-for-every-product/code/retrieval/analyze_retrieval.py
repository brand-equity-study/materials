"""Study 2a's second test, the retrieved reviews (study2a-experience-attributes-stated-for-every-product/materials/retrieval/analysis_plan.md), for one panel:
- the name gap g(e) = s_hidden(e) - s_original(e) at every level of the evidence e, and its change D(e) = g(e) - g(none);
- the gain from evidence for the best product under a familiar name minus under the fictitious name,
  I(e) = [s_crossed(e) - s_crossed(none)] - [s_original(e) - s_original(none)];
- Holm over the six (three D and three I); secondary: g(e), the crossed boost s_crossed(e) - s_hidden(e) and the
  change with names hidden s_hidden(e) - s_hidden(none).

    python study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py --build r1 --panel claude --out study2a-experience-attributes-stated-for-every-product/results/retrieval/claude
    python study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py --build r1 --panel open \\
        --letters study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz --leave-out kimi-linear48b \\
        --out study2a-experience-attributes-stated-for-every-product/results/retrieval/open-all
    python study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py --build r1 --panel all \\
        --cells study2a-experience-attributes-stated-for-every-product/results/retrieval/claude/cells.csv --cells study2a-experience-attributes-stated-for-every-product/results/retrieval/open-all/cells.csv \\
        --out study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models

The Claude models' answers (study2a-experience-attributes-stated-for-every-product/data/retrieval/claude/<model>.jsonl.gz) are read with final_answer before pick
(common/parse_answer.py); the open models' letters (study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz) were read the same
way on the computing cluster. Pooling and intervals are those of the store (study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py):
every table weighs equally within a model and every model equally, and the intervals come from the two-way cluster
bootstrap over tables and models (seed 20261120). Writes <out>/numbers.json and cells.csv, and with --panel all
per_model.csv, each model's contrasts for the analysis of how models differ.
"""
import argparse
import csv
import glob
import gzip
import json
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package
STUDY = os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product")
sys.path.insert(0, os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "code", "store"))   # analyze_harness.py
sys.path.insert(0, os.path.join(ROOT, "common"))   # parse_answer.py
import analyze_harness as AH  # noqa: E402  (pooled, bootstrap, estimate)
from parse_answer import final_answer, pick  # noqa: E402

TONES = ("positive", "mixed", "negative")


def load(a, items):
    """[(model, item, letter, how)]"""
    out = []
    if a.panel == "claude":
        for f in sorted(glob.glob(os.path.join(STUDY, "data", "retrieval", "claude", "*.jsonl.gz"))):
            for line in gzip.open(f, "rt", encoding="utf8"):   # in the order of the run's folders and files
                r = json.loads(line)
                if r["id"] in items:
                    L, how = pick(final_answer(r["answer_text"]))
                    out.append((r["model"], items[r["id"]], L, how))
    elif a.letters:
        for r in csv.DictReader(gzip.open(a.letters, "rt", encoding="utf8")):
            if r["study"] == "b10" and r["id"] in items:
                out.append((r["model"], items[r["id"]], r["letter"], r["how"]))
    return out


def shares(answers):
    """{(model, table, arm, names): [n parsed, n best]}"""
    c = defaultdict(lambda: [0, 0])
    for model, it, L, how in answers:
        if L:
            k = (model, it["table"], it["arm"], it["names"])
            c[k][0] += 1
            c[k][1] += int(L == it["best"])
    return c


def s_of(c, m, t, arm, names):
    n, b = c.get((m, t, arm, names), (0, 0))
    return b / n if n else None


def per_mt(c, f):
    """{(model, table): f(...)} where every share it needs exists"""
    out = {}
    for m, t in sorted({(k[0], k[1]) for k in c}):     # sorted: the result must not depend on PYTHONHASHSEED
        v = f(c, m, t)
        if v is not None:
            out[(m, t)] = v
    return out


def combine(*terms):
    """f(c, m, t) = sum of sign * s(arm, names) over the terms, or None when a share is missing"""
    def f(c, m, t):
        tot = 0.0
        for sign, arm, names in terms:
            s = s_of(c, m, t, arm, names)
            if s is None:
                return None
            tot += sign * s
        return tot
    return f


def gap(e):
    return combine((1, e, "hidden"), (-1, e, "original"))


def change(e):
    return combine((1, e, "hidden"), (-1, e, "original"), (-1, "none", "hidden"), (1, "none", "original"))


def familiar_gain(e):
    return combine((1, e, "crossed"), (-1, "none", "crossed"), (-1, e, "original"), (1, "none", "original"))


def crossed_boost(e):
    return combine((1, e, "crossed"), (-1, e, "hidden"))


def hidden_change(e):
    return combine((1, e, "hidden"), (-1, "none", "hidden"))


def cells_from(paths):
    """{(model, table, arm, names): [parsed, best]} from the panels' cells.csv files; a model in two files is refused,
    so that no answers are counted twice."""
    c, where = {}, {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf8")):
            k = (r["model"], r["table"], r["arm"], r["names"])
            if k in c:
                raise SystemExit(f"refused: {k} is in {where[k]} and in {p}")
            c[k] = [int(r["parsed"]), int(r["best"])]
            where[k] = p
    return c


per_model_rows = AH.per_model_rows     # one function for the store, search and retrieval analyses


def holm(ps):
    """Holm-adjusted P values, in the order given"""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    ap.add_argument("--panel", choices=["claude", "open", "all"], required=True)
    ap.add_argument("--cells", action="append", help="with --panel all: a panel's cells.csv (repeat for each panel)")
    ap.add_argument("--leave-out", action="append", default=[],
                    help="a model left out of every estimate under the 90 per cent rule (AH.LEAVE_OUT_RULE)")
    ap.add_argument("--letters", help="the open models' letters (study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz)")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=1, help="processes for the bootstraps (the numbers do not change)")
    ap.add_argument("--out")
    a = ap.parse_args()
    levels = ("none",) + TONES
    if a.panel == "all":
        if not a.cells:
            raise SystemExit("refused: --panel all needs the panels' --cells files")
        c = cells_from(a.cells)
        models = sorted({k[0] for k in c})
        numbers = {"build": a.build, "panel": "all", "answers": sum(v[0] for v in c.values()),
                   "parse": "read in each panel's numbers.json", "models": models,
                   "sources": [{"file": os.path.relpath(p, ROOT).replace("\\", "/"),
                                "sha256": __import__("hashlib").sha256(open(p, "rb").read()).hexdigest()}
                               for p in a.cells]}
    else:
        items = {json.loads(l)["id"]: json.loads(l) for l in gzip.open(
            os.path.join(STUDY, "materials", "retrieval", a.build, "prompts.jsonl.gz"), "rt", encoding="utf8")}
        answers = load(a, items)
        c = shares(answers)
        hows = defaultdict(int)
        for model, it, L, how in answers:
            hows[f"{model} {how}"] += 1
        answers, _ = AH.leave_out(answers, a.leave_out)
        c = shares(answers)
        numbers = {"build": a.build, "panel": a.panel, "answers": len(answers), "parse": dict(hows),
                   "models": sorted({m for m, *_ in answers})}
    if a.panel == "all":   # carried over from each source panel's numbers.json, with the parse counts
        left = AH.inherited_left_out(a.cells, a.leave_out, {k[0] for k in c})
    else:
        parse = numbers.get("parse") if isinstance(numbers.get("parse"), dict) else {}
        left = {}
        for m in a.leave_out:
            counts = {k.split(" ", 1)[1]: v for k, v in parse.items() if k.split(" ", 1)[0] == m}
            if counts:
                left[m] = {"rule": AH.LEAVE_OUT_RULE, "parse counts": counts, "answers": sum(counts.values())}
    c = {k: v for k, v in c.items() if k[0] not in set(a.leave_out) | set(left)}
    numbers["models"] = sorted({k[0] for k in c})
    if a.panel == "all":
        numbers["answers"] = sum(v[0] for v in c.values())
    numbers["left_out"] = left
    numbers.update({
        "bootstrap": {"draws": a.draws, "seed": AH.SEED, "clusters": "tables and models, resampled independently"},
        "share of the best product": {f"{e} {n}": AH.pooled(per_mt(c, lambda c, m, t, e=e, n=n: s_of(c, m, t, e, n)))[0]
                                      for e in levels for n in ("hidden", "original", "crossed")}})
    groups = {
        "name gap g(e)": {e: per_mt(c, gap(e)) for e in levels},
        "change D(e) = g(e) - g(none)": {e: per_mt(c, change(e)) for e in TONES},
        "familiar gain I(e)": {e: per_mt(c, familiar_gain(e)) for e in TONES},
        "crossed boost s_crossed(e) - s_hidden(e)": {e: per_mt(c, crossed_boost(e)) for e in levels},
        "change with names hidden s_hidden(e) - s_hidden(none)": {e: per_mt(c, hidden_change(e)) for e in TONES}}
    numbers.update(AH.estimate_groups(groups, a.draws, a.workers))
    fam = [("change D(e) = g(e) - g(none)", e) for e in TONES] + [("familiar gain I(e)", e) for e in TONES]
    ps = [numbers[k][e]["interval"]["p_two_sided"] if numbers[k][e].get("interval") else None for k, e in fam]
    if all(p is not None for p in ps):
        for (k, e), h in zip(fam, holm(ps)):
            numbers[k][e]["holm"] = h
    out = a.out or os.path.join(STUDY, "results", "retrieval", "all-models" if a.panel == "all" else a.panel)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    if a.panel == "all":
        rows = per_model_rows({k: groups[k] for k in ("name gap g(e)", "change D(e) = g(e) - g(none)",
                                                       "familiar gain I(e)")})
        AH.write_per_model(os.path.join(out, "per_model.csv"), rows)   # LF line ends, as every CSV here
    with open(os.path.join(out, "cells.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")   # LF: the same bytes in every clone
        w.writerow(["model", "table", "arm", "names", "parsed", "best", "share_best"])
        for (m, t, e, n), (k, b) in sorted(c.items()):
            w.writerow([m, t, e, n, k, b, round(b / k, 4)])
    print(f"{numbers['answers']} answers; models {numbers['models']}")
    for e in levels:
        v = numbers["name gap g(e)"][e]
        line = f"{e:9s} g {100 * v['pooled']:6.1f}" if v["pooled"] is not None else f"{e:9s} g   n/a"
        for key, lab in (("change D(e) = g(e) - g(none)", "D"), ("familiar gain I(e)", "I")):
            d = numbers[key].get(e)
            if d and d["pooled"] is not None:
                line += f"   {lab} {100 * d['pooled']:6.1f}"
                if d.get("interval"):
                    line += f" ({100 * d['interval']['low95']:.1f} to {100 * d['interval']['high95']:.1f})"
                if "holm" in d:
                    line += f" Holm {d['holm']:.3f}"
        print(line)


if __name__ == "__main__":
    main()
