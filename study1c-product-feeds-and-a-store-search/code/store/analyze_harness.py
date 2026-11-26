"""Study 1c, the store: for each panel, the name gap g(arm) in every arm of the store (the feed formats, schema.org
markup, a Sponsored label, positions, rating gaps, the developer's instructions, the information), the change
D(arm) = g(arm) - g(plain) with Holm over the 15 changes, the change with names hidden, and the share of the labelled
product under a Sponsored label (study1c-product-feeds-and-a-store-search/materials/store/analysis_plan.md).

    python study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py --build h2 --panel claude --out study1c-product-feeds-and-a-store-search/results/store/claude
    python study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py --build h2 --panel open --also-build h1 \
        --letters study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz --leave-out kimi-linear48b --out study1c-product-feeds-and-a-store-search/results/store/open-all
    python study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py --build h2 --panel all --cells study1c-product-feeds-and-a-store-search/results/store/claude/cells.csv \
        --cells study1c-product-feeds-and-a-store-search/results/store/open-all/cells.csv --leave-out kimi-linear48b --out study1c-product-feeds-and-a-store-search/results/store/all-models

Every answer is read with final_answer before pick (common/parse_answer.py), which removes reasoning that a model
leaves in its output; the open models' letters were read the same way on the computing cluster.

For a model, a table, an arm and a name version, s is the share of parsed answers that pick the best product over the
trials; g = s(hidden) - s(original). Pooling weights every table equally within a model and every model equally. The
intervals come from the two-way cluster bootstrap over tables and models (10,000 draws, seed 20261120). Writes
<out>/numbers.json and cells.csv, and with --panel all per_model.csv.
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
STUDY = os.path.join(ROOT, "study1c-product-feeds-and-a-store-search")
sys.path.insert(0, os.path.join(ROOT, "common"))   # parse_answer.py
from parse_answer import final_answer, pick  # noqa: E402

SEED = 20261120
REF = "plain"


LEAVE_OUT_RULE = ("left out of every estimate under the 90 per cent rule (a model whose answers the parser reads in "
                  "under 90 per cent of a build's items is reported apart)")


def per_model_rows(groups, draws=2000):
    """One row for each model and quantity: the mean over its tables (in points), and a 95 per cent interval and
    standard error from resampling the model's tables (seeded), for the analysis of how models differ. groups is
    {quantity: {level: {(model, table): value}}}. Shared by the store, search and retrieval analyses."""
    import numpy as np
    rows = []
    for g, d in groups.items():
        for level, vals in d.items():
            by = defaultdict(list)
            for (m, t), v in vals.items():
                by[m].append((t, v))
            for m in sorted(by):
                # tables in sorted order, so that the seeded resampling does not depend on the order in which the
                # values arrive (per_mt builds them from a set, whose order changes between processes)
                x = np.array([v for t, v in sorted(by[m])], float)
                rng = np.random.default_rng(SEED)
                bs = x[rng.integers(0, len(x), (draws, len(x)))].mean(axis=1) if len(x) >= 3 else None
                rows.append({"model": m, "quantity": g, "level": level, "estimate_pp": round(100 * x.mean(), 4),
                             "se_pp": round(100 * float(bs.std(ddof=1)), 4) if bs is not None else "",
                             "ci95_low_pp": round(100 * float(np.quantile(bs, 0.025)), 4) if bs is not None else "",
                             "ci95_high_pp": round(100 * float(np.quantile(bs, 0.975)), 4) if bs is not None else "",
                             "tables": len(x),
                             "not_estimable": "" if bs is not None else "fewer than 3 tables"})
    return rows


def cells_from(paths):
    """{(model, table, arm, names): [parsed, best, labelled]} from the panels' cells.csv files; a model's cell found in
    two files is refused, so that no answers are counted twice."""
    c, where = {}, {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf8")):
            k = (r["model"], r["table"], r["arm"], r["names"])
            if k in c:
                raise SystemExit(f"refused: {k} is in {where[k]} and in {p}")
            c[k] = [int(r["parsed"]), int(r["best"]), int(r["labelled"])]
            where[k] = p
    return c


def inherited_left_out(cells_paths, named, models_in_cells):
    """The models left out of a pooled run, each with the rule and its parse counts: those that a source panel's
    numbers.json (beside its cells.csv) records under left_out, and those named here (--leave-out) whose rows were found
    in the cells. A panel that left a model out before pooling has no rows of it in its cells, so its record is
    carried over from that panel's numbers.json."""
    out = {}
    for p in cells_paths:
        nj = os.path.join(os.path.dirname(p), "numbers.json")
        if not os.path.exists(nj):
            continue
        n = json.load(open(nj, encoding="utf8"))
        for m in n.get("left_out") or {}:
            parse = n.get("parse") if isinstance(n.get("parse"), dict) else {}
            counts = {k.split(" ", 1)[1]: v for k, v in parse.items() if k.split(" ", 1)[0] == m}
            out[m] = {"rule": LEAVE_OUT_RULE, "from": os.path.relpath(nj, ROOT).replace("\\", "/"),
                      "parse counts": counts, "answers": sum(counts.values())}
    for m in sorted(set(named) & set(models_in_cells)):
        out.setdefault(m, {"rule": LEAVE_OUT_RULE, "from": "--leave-out (its rows were in the cells)"})
    return out


def write_per_model(path, rows):
    with open(path, "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")   # LF: the same bytes in every clone
        w.writeheader()
        w.writerows(rows)


def leave_out(answers, models):
    """(the answers of every model not named, the named models that had answers); a named model is left out of every
    estimate, and its parse counts are reported apart by the caller."""
    drop = set(models or [])
    return [x for x in answers if x[0] not in drop], sorted(drop & {x[0] for x in answers})


def load_answers(a, items):
    """[(model, item, letter, how)] from the Claude answers, the open models' letters or their answers.jsonl files."""
    out = []
    if a.panel == "claude":
        for f in sorted(glob.glob(os.path.join(STUDY, "data", "store", "claude", "*.jsonl.gz"))):
            for line in gzip.open(f, "rt", encoding="utf8"):   # in the order of the run's folders and files
                r = json.loads(line)
                if r["id"] in items:
                    L, how = pick(final_answer(r["answer_text"]))
                    out.append((r["model"], items[r["id"]], L, how))
    elif a.letters:
        for r in csv.DictReader(gzip.open(a.letters, "rt", encoding="utf8")):
            if r["study"] == "b16" and r["id"] in items:
                out.append((r["model"], items[r["id"]], r["letter"], r["how"]))
    else:
        for f in glob.glob(os.path.join(a.open_dir, "**", "answers.jsonl"), recursive=True):
            for line in open(f, encoding="utf8"):
                r = json.loads(line)
                if r["id"] in items:
                    L, how = pick(final_answer(r.get("raw", r["answer"])))
                    out.append((r["model"], items[r["id"]], L, how))
    return out


def answered_twice(answers):
    """Cells (model, table, trial, arm, names, rung) with more than one answer. A build named with --also-build holds
    the same cells under other ids (h1 is h2 at the equal price), so an answer to both would be counted twice."""
    seen = defaultdict(int)
    for model, it, L, how in answers:
        seen[(model, it["table"], it["trial"], it["arm"], it["names"], it.get("rung", 0))] += 1
    return sorted(k for k, n in seen.items() if n > 1)


def shares(answers):
    """{(model, table, arm, names): [n parsed, n best, n labelled]}"""
    c = defaultdict(lambda: [0, 0, 0])
    for model, it, L, how in answers:
        if not L:
            continue
        k = (model, it["table"], it["arm"], it["names"])
        c[k][0] += 1
        c[k][1] += int(L == it["best"])
        c[k][2] += int(bool(it.get("labelled")) and L == it["labelled"])
    return c


def per_mt(c, fn):
    """{(model, table): value} where fn(c, model, table) gives a value or None."""
    keys = {(m, t) for (m, t, _, _) in c}
    out = {}
    for m, t in sorted(keys):     # sorted, so that the result does not depend on PYTHONHASHSEED
        v = fn(c, m, t)
        if v is not None:
            out[(m, t)] = v
    return out


def s_of(c, m, t, arm, names, which=1):
    n = c.get((m, t, arm, names))
    return n[which] / n[0] if n and n[0] else None


def gap(arm):
    def f(c, m, t):
        h, o = s_of(c, m, t, arm, "hidden"), s_of(c, m, t, arm, "original")
        return None if h is None or o is None else h - o
    return f


def change(arm):
    def f(c, m, t):
        g1, g0 = gap(arm)(c, m, t), gap(REF)(c, m, t)
        return None if g1 is None or g0 is None else g1 - g0
    return f


def hidden_change(arm):
    def f(c, m, t):
        h1, h0 = s_of(c, m, t, arm, "hidden"), s_of(c, m, t, REF, "hidden")
        return None if h1 is None or h0 is None else h1 - h0
    return f


def pooled(vals):
    by = defaultdict(list)
    for (m, t), v in vals.items():
        by[m].append(v)
    per = {m: sum(x) / len(x) for m, x in by.items()}
    return (sum(per.values()) / len(per) if per else None), per


def bootstrap(vals, draws):
    """Two-way cluster bootstrap over tables and models: 95 per cent interval, 90 per cent interval, two-sided P."""
    import numpy as np
    if not vals:
        return None
    mods = sorted({m for m, t in vals})
    tabs = sorted({t for m, t in vals})
    if len(tabs) < 3:
        return None
    mi = np.array([mods.index(m) for m, t in vals])
    ti = np.array([tabs.index(t) for m, t in vals])
    x = np.array(list(vals.values()), dtype=float)
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(draws):
        wt = np.bincount(rng.integers(0, len(tabs), len(tabs)), minlength=len(tabs))
        wm = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods))
        w = wt[ti]
        num = np.bincount(mi, weights=w * x, minlength=len(mods))
        den = np.bincount(mi, weights=w, minlength=len(mods))
        ok = (den > 0) & (wm > 0)
        if ok.any():
            per = num[ok] / den[ok]
            out.append(float(np.sum(per * wm[ok]) / np.sum(wm[ok])))
    v = np.sort(np.array(out))
    return {"low95": float(np.quantile(v, 0.025)), "high95": float(np.quantile(v, 0.975)),
            "low90": float(np.quantile(v, 0.05)), "high90": float(np.quantile(v, 0.95)),
            "p_two_sided": float(min(1.0, 2 * min(np.mean(v <= 0), np.mean(v >= 0)))), "draws": len(out)}


def estimate(vals, draws):
    e, per = pooled(vals)
    return {"pooled": e, "per_model": per, "tables_per_model": dict(pd_count(vals)),
            "interval": bootstrap(vals, draws) if draws else None}


def estimate_groups(groups, draws, workers=1):
    """{group: {key: estimate}} for {group: {key: vals}}. With workers > 1 the bootstraps run in that many processes;
    each bootstrap draws from its own generator seeded with SEED, so the numbers are the same as with one process (a
    job on the computing cluster uses this)."""
    out = {g: {k: estimate(v, 0) for k, v in d.items()} for g, d in groups.items()}
    if not draws:
        return out
    keys = [(g, k) for g, d in groups.items() for k in d]
    vals = [groups[g][k] for g, k in keys]
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(workers) as ex:
            ivs = list(ex.map(bootstrap, vals, [draws] * len(vals)))
    else:
        ivs = [bootstrap(v, draws) for v in vals]
    for (g, k), iv in zip(keys, ivs):
        out[g][k]["interval"] = iv
    return out


def pd_count(vals):
    c = defaultdict(int)
    for m, t in vals:
        c[m] += 1
    return c


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    ap.add_argument("--panel", choices=["claude", "open", "all"], required=True)
    ap.add_argument("--cells", action="append", help="with --panel all: a panel's cells.csv (repeat for each panel)")
    ap.add_argument("--subset", default="claude")
    ap.add_argument("--open-dir")
    ap.add_argument("--letters", help="harness-letters.csv.gz from the export job b16-07 (the open panel)")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=1, help="processes for the bootstraps (the numbers do not change)")
    ap.add_argument("--out")
    ap.add_argument("--leave-out", action="append", default=[],
                    help="a model left out of every estimate under the open-models rule (its parse counts are kept)")
    ap.add_argument("--also-build", action="append", default=[],
                    help="a build whose items are cells of --build under other ids (the open panel answered h1 for the "
                         "equal-price half of h2); its answers count with the build's, and a cell answered twice refuses")
    a = ap.parse_args()
    items = {json.loads(l)["id"]: json.loads(l) for l in gzip.open(os.path.join(STUDY, "materials", "store", a.build, "prompts.jsonl.gz"), "rt", encoding="utf8")}
    levels = list(dict.fromkeys(it["arm"] for it in items.values()))
    for b in a.also_build:
        for l in gzip.open(os.path.join(STUDY, "materials", "store", b, "prompts.jsonl.gz"), "rt", encoding="utf8"):
            it = json.loads(l)
            items.setdefault(it["id"], it)
    if a.panel == "all":
        # every model that answered, pooled from the panels' cells (the analysis plan's change of 22 November
        # 2026); the parse counts are in each panel's numbers.json
        if not a.cells:
            raise SystemExit("refused: --panel all needs the panels' --cells files")
        c = cells_from(a.cells)
        left = inherited_left_out(a.cells, a.leave_out, {k[0] for k in c})
        c = {k: v for k, v in c.items() if k[0] not in set(a.leave_out) | set(left)}
        numbers = {"build": a.build, "panel": "all", "answers": sum(v[0] for v in c.values()),
                   "parse": "read in each panel's numbers.json", "models": sorted({k[0] for k in c}),
                   "left_out": left,
                   "sources": [{"file": os.path.relpath(p, ROOT).replace("\\", "/"),
                                "sha256": __import__("hashlib").sha256(open(p, "rb").read()).hexdigest()} for p in a.cells],
                   "bootstrap": {"draws": a.draws, "seed": SEED, "clusters": "tables and models, resampled independently"}}
    else:
        answers = load_answers(a, items)
        twice = answered_twice(answers)
        if twice:
            raise SystemExit(f"refused: {len(twice)} cells have more than one answer, for example {twice[0]}")
        hows = defaultdict(int)
        for model, it, L, how in answers:             # every model's parse counts, those left out included
            hows[f"{model} {how}"] += 1
        answers, left = leave_out(answers, a.leave_out)
        c = shares(answers)
        numbers = {"build": a.build, "panel": a.panel, "answers": len(answers), "parse": dict(hows),
                   "models": sorted({m for m, *_ in answers}),
                   "left_out": {m: LEAVE_OUT_RULE for m in left},
                   "bootstrap": {"draws": a.draws, "seed": SEED, "clusters": "tables and models, resampled independently"}}
    numbers["share of the best product"] = {
        f"{arm} {names}": pooled(per_mt(c, lambda c, m, t, arm=arm, names=names: s_of(c, m, t, arm, names)))[0]
        for arm in levels for names in ("hidden", "original")}
    groups = {
        "name gap g(arm)": {arm: per_mt(c, gap(arm)) for arm in levels},
        "change D(arm) = g(arm) - g(plain)": {arm: per_mt(c, change(arm)) for arm in levels if arm != REF},
        "change with names hidden, s_hidden(arm) - s_hidden(plain)": {
            arm: per_mt(c, hidden_change(arm)) for arm in levels if arm != REF}}
    numbers.update(estimate_groups(groups, a.draws, a.workers))
    for arm in ("sponsored-familiar", "sponsored-best"):
        if arm in levels:
            numbers[f"share of the labelled product, {arm}"] = {
                names: pooled(per_mt(c, lambda c, m, t, arm=arm, names=names: s_of(c, m, t, arm, names, which=2)))[0]
                for names in ("hidden", "original")}
    # Holm over the 15 changes
    fam = {arm: v["interval"]["p_two_sided"] for arm, v in numbers["change D(arm) = g(arm) - g(plain)"].items() if v.get("interval")}
    order = sorted(fam, key=fam.get)
    run = 0.0
    for i, arm in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * fam[arm]))
        numbers["change D(arm) = g(arm) - g(plain)"][arm]["holm"] = run
    out = a.out or os.path.join(STUDY, "results", "store", a.panel)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    with open(os.path.join(out, "cells.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")   # LF: the same bytes in every clone
        w.writerow(["model", "table", "arm", "names", "parsed", "best", "labelled"])
        for (m, t, arm, names), (n, b, l) in sorted(c.items()):
            w.writerow([m, t, arm, names, n, b, l])
    if a.panel == "all":   # each model's name gap at the reference and change in every arm, for heterogeneity.py
        write_per_model(os.path.join(out, "per_model.csv"), per_model_rows({
            "name gap g(arm)": {REF: groups["name gap g(arm)"][REF]},
            "change D(arm) = g(arm) - g(plain)": groups["change D(arm) = g(arm) - g(plain)"]}))
    print(json.dumps({k: v for k, v in numbers.items() if k in ("answers", "parse", "models")}, indent=1))
    for arm in levels:
        g = numbers["name gap g(arm)"][arm]
        d = numbers["change D(arm) = g(arm) - g(plain)"].get(arm)
        gi = g["interval"]
        line = f"{arm:20s} g {100 * g['pooled']:6.1f}" if g["pooled"] is not None else f"{arm:20s} g    n/a"
        if gi:
            line += f" ({100 * gi['low95']:.1f} to {100 * gi['high95']:.1f})"
        if d and d["pooled"] is not None:
            line += f"   D {100 * d['pooled']:6.1f}"
            if d.get("interval"):
                line += f" ({100 * d['interval']['low95']:.1f} to {100 * d['interval']['high95']:.1f}) Holm {d.get('holm', float('nan')):.3f}"
        print(line)


if __name__ == "__main__":
    main()
