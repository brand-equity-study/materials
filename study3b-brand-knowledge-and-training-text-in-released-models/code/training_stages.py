"""Study 3, the training stages: from the letter probabilities of 22 checkpoints (OLMo 2 7B through pretraining,
supervised tuning, preference tuning and the released Instruct model; OLMo 2 32B; the base and Instruct releases of
Llama 3.1 8B and Qwen 2.5 7B) on Study 1a's 3,600 strictly better prompts, the cost of the fictitious name, the premium
of a familiar name and whether the checkpoint reads the tables, at each checkpoint, format and information cell, with
intervals from a bootstrap over the 30 tables, and the changes between training stages within a family.

    python study3b-brand-knowledge-and-training-text-in-released-models/code/training_stages.py --scores study3b-brand-knowledge-and-training-text-in-released-models/data/training-stages/scores \\
        --models study3b-brand-knowledge-and-training-text-in-released-models/materials/training-stages/models.tsv --out study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json

Every quantity is a mean over units, a unit being one table, trial, information cell and price cell, so that its three
cells (names hidden, original, crossed) are read together. The cost is the probability of the best product's letter
with the names hidden minus with the original names, in points; the premium is the same probability with the best
product under a familiar name (crossed) minus with the names hidden; a checkpoint reads the tables when the best product
has the highest probability with the names hidden in at least 40 percent of the units. A stage's change is the later
checkpoint's cost minus the earlier one's on the tables that both scored, with Holm's correction over a family's
three changes (base to supervised tuning, to preference tuning, to the released Instruct model).
"""
import argparse
import csv
import glob
import gzip
import json
import os
import random

LETTERS = "ABCDE"
BOOT_SEED = 20261120
DRAWS = 2000
READ_FLOOR = 0.40


def load(paths):
    """{(key, format): {unit: {"hidden": p_best, "original": ..., "crossed": ..., "hidden_top": bool}}} and each
    unit's table."""
    data, tables = {}, {}
    files = []
    for p in paths:
        files += (sorted(glob.glob(os.path.join(p, "**", "scores_*.csv.gz"), recursive=True)) if os.path.isdir(p)
                  else [p])   # the package's score files, one folder per checkpoint
    for fp in files:
        with gzip.open(fp, "rt", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                k = (r["key"], r["format"])
                u = (r["table"], int(r["trial"]), int(r["info"]), int(r["rung"]))
                tables[u] = r["table"]
                p = {L: float(r[f"p_{L}"]) for L in LETTERS}
                d = data.setdefault(k, {}).setdefault(u, {})
                d[r["names"]] = p[r["best"]]
                if r["names"] == "hidden":
                    d["hidden_top"] = max(p, key=p.get) == r["best"]
    return data, tables


def complete(units):
    return {u: v for u, v in units.items() if all(c in v for c in ("hidden", "original", "crossed"))}


def by_table(units, info):
    """{table: [(cost, premium, hidden_top, p_hidden)]} for the units of one information cell."""
    out = {}
    for (t, _, inf, _), v in units.items():
        if inf != info:
            continue
        out.setdefault(t, []).append((v["hidden"] - v["original"], v["crossed"] - v["hidden"],
                                      1.0 if v["hidden_top"] else 0.0, v["hidden"]))
    return out


def mean_over(tab, idx, which):
    vals = [x[which] for t in idx for x in tab[t]]
    return sum(vals) / len(vals) if vals else float("nan")


def draws(tables, n=DRAWS, seed=BOOT_SEED):
    rng = random.Random(seed)
    ts = sorted(tables)
    return [[ts[rng.randrange(len(ts))] for _ in ts] for _ in range(n)]


def interval(vals):
    v = sorted(x for x in vals if x == x)
    if not v:
        return [float("nan"), float("nan")]
    lo, hi = v[int(0.025 * (len(v) - 1))], v[int(round(0.975 * (len(v) - 1)))]
    return [lo, hi]


def summary(units, info, boot):
    tab = by_table(complete(units), info)
    if not tab:
        return None
    idx = sorted(tab)
    out = {"tables": len(idx), "units": sum(len(v) for v in tab.values())}
    for name, w, scale in (("cost", 0, 100), ("premium", 1, 100), ("reading", 2, 1), ("p_hidden", 3, 1)):
        est = mean_over(tab, idx, w) * scale
        bs = [mean_over(tab, [t for t in b if t in tab], w) * scale for b in boot]
        out[name] = {"estimate": est, "ci95": interval(bs)}
    out["reads"] = out["reading"]["estimate"] >= READ_FLOOR if info == 0 else None
    return out


def change(units_a, units_b, info, boot):
    """B minus A on the cost, on the units that both checkpoints scored, with the same table draws."""
    ca, cb = by_table(complete(units_a), info), by_table(complete(units_b), info)
    common = sorted(set(ca) & set(cb))
    if not common:
        return None
    est = (mean_over(cb, common, 0) - mean_over(ca, common, 0)) * 100
    bs = []
    for b in boot:
        idx = [t for t in b if t in ca and t in cb]
        bs.append((mean_over(cb, idx, 0) - mean_over(ca, idx, 0)) * 100)
    return {"estimate": est, "ci95": interval(bs), "tables": len(common), "p_two_sided": two_sided(bs)}


def two_sided(bs):
    v = [x for x in bs if x == x]
    if not v:
        return float("nan")
    below = sum(1 for x in v if x <= 0) / len(v)
    above = sum(1 for x in v if x >= 0) / len(v)
    return min(1.0, 2 * min(below, above))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def read_models(path):
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f, delimiter="\t")]


STAGE_CHANGES = (("base", "sft"), ("sft", "dpo"), ("dpo", "instruct"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    data, tables = load(a.scores)
    boot = draws(set(tables.values()))
    models = read_models(a.models)
    res = {"read_floor": READ_FLOOR, "draws": DRAWS, "seed": BOOT_SEED, "checkpoints": {}, "changes": {}}
    for (key, fmt), units in sorted(data.items()):
        res["checkpoints"].setdefault(key, {})[fmt] = {f"info{i}": summary(units, i, boot) for i in (0, 1)}
    for fam in sorted({m["family"] for m in models}):
        stages = {m["stage"]: m["key"] for m in models if m["family"] == fam}
        for fmt in ("plain3", "plain0", "chat"):
            rows, ps = [], []
            for s0, s1 in STAGE_CHANGES:
                k0, k1 = stages.get(s0), stages.get(s1)
                if (k0, fmt) in data and (k1, fmt) in data:
                    c = change(data[(k0, fmt)], data[(k1, fmt)], 0, boot)
                    if c:
                        rows.append({"from": s0, "to": s1, **c})
                        ps.append(c["p_two_sided"])
            if "base" in stages and "instruct" in stages and (stages["base"], fmt) in data and (stages["instruct"], fmt) in data:
                c = change(data[(stages["base"], fmt)], data[(stages["instruct"], fmt)], 0, boot)
                if c:
                    res["changes"].setdefault(fam, {}).setdefault(fmt, {})["base_to_instruct"] = c
            for r, p in zip(rows, holm(ps)):
                r["p_holm"] = p
            if rows:
                res["changes"].setdefault(fam, {}).setdefault(fmt, {})["stages"] = rows
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    main()
