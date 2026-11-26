"""Study 2a, the reasons in the models' explanations (Web Appendix J): the share of explanations that name the brand,
under each judge with open weights that was admitted on the stated sample of 200
(study2a-experience-attributes-stated-for-every-product/materials/explanations/analysis_plan.md, condition 3).

    python study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py --checks-only --judge <judge>=<all-answers.jsonl.gz> [--judge ...]
    python study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py --reference-only
    python study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py --judge <judge>=<all-answers.jsonl.gz> [--judge ...] [--draws 2000]

The judges' codes are in study2a-experience-attributes-stated-for-every-product/data/explanations/judges/; the explanations that they coded, with each one's model,
table, cell and source, in study2a-experience-attributes-stated-for-every-product/data/explanations/items-all.jsonl.gz. The code read is brand_any (yes = 1, no = 0;
an unread reply is left out). The primary estimate is the mean over models of each model's share, every model with
equal weight, and the share over all explanations pooled is beside it. Intervals come from a two-way cluster bootstrap
over tables and models; for the groups, the models are resampled within their group. Writes CHECKS.json,
REFERENCE-200.json and numbers.json in study2a-experience-attributes-stated-for-every-product/results/explanations.
"""
import argparse
import csv
import gzip
import json
import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import admit as AD  # noqa: E402

PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package
DATA = os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "data", "explanations")
SEED = 20261121
ZERO = 1e-12  # a bootstrap draw closer to zero than this is zero (boot(): its sign is rounding)
POPULATION = os.path.join(DATA, "items-all.jsonl.gz")
SAMPLE = os.path.join(DATA, "items-sample.jsonl")
REFERENCE = os.path.join(DATA, "reference")
# the judges whose own run on the stated 200 is in data/explanations/judges/<judge>-sample-answers.jsonl.gz
SAMPLE_RUNS = ("olmo31-32b", "gptoss120b", "gemma31b", "qwen35-122b-fp8")
CHARACTERISTICS = os.path.join(PKG, "models", "model_characteristics.csv")
MIN_N, MIN_TABLES = 20, 3      # a per-model share needs at least 20 explanations in at least three tables
# the open-models rule (models/open_models_plan.md): a model whose answers the parser reads in under 90 per
# cent of a build's items is reported apart, left out of every pooled estimate and every analysis of how models
# differ. Kimi Linear 48B's explanations come from Study 1a's strictly better tables, where its letters parse in
# 2,965 of 3,600 answers (82.4 per cent; study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz).
LEFT_OUT = {"kimi-linear48b": {"rule": "the open-models rule: a model parsed in under 90 per cent of a build's "
                                       "items is reported apart", "build": "b2/dom2", "answers": 3600, "parsed": 2965,
                               "source": "study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz"}}
GROUPS = ("claude", "codex", "open")


# ---------- the statistics, on plain arrays ----------

class Cube:
    """Sums and counts of y in each (table, model) cell for one subset of explanations."""

    def __init__(self, rows, tables, models):
        self.tables, self.models = tables, models
        ti = {t: i for i, t in enumerate(tables)}
        mi = {m: i for i, m in enumerate(models)}
        self.S = np.zeros((len(tables), len(models)))
        self.N = np.zeros((len(tables), len(models)))
        for r in rows:
            self.S[ti[r["table"]], mi[r["model"]]] += r["y"]
            self.N[ti[r["table"]], mi[r["model"]]] += 1

    def per_model(self, ct):
        """(shares, counts) per model for table multiplicities ct (a share is nan where the count is 0)."""
        s, n = ct @ self.S, ct @ self.N
        with np.errstate(invalid="ignore", divide="ignore"):
            return s / n, n


def mean_of_shares(cube, ct, cm, mask=None):
    """The mean of the per-model shares over the models with a count, weighted by model multiplicities cm."""
    sh, n = cube.per_model(ct)
    w = cm * (n > 0) * (1 if mask is None else mask)
    return float((w * np.nan_to_num(sh)).sum() / w.sum()) if w.sum() > 0 else None


def pooled_share(cube, ct, cm, mask=None):
    s, n = ct @ cube.S, ct @ cube.N
    w = cm * (1 if mask is None else mask)
    return float((w * s).sum() / (w * n).sum()) if (w * n).sum() > 0 else None


def paired_difference(a, b, ct, cm, mask=None):
    """The mean over models (with a count in both subsets) of share in a minus share in b."""
    sa, na = a.per_model(ct)
    sb, nb = b.per_model(ct)
    w = cm * (na > 0) * (nb > 0) * (1 if mask is None else mask)
    return float((w * (np.nan_to_num(sa) - np.nan_to_num(sb))).sum() / w.sum()) if w.sum() > 0 else None


def boot(stat, n_tables, model_groups, draws=2000, seed=SEED, strata=False):
    """stat(ct, cm) -> dict of numbers. ct and cm are multiplicity vectors of tables and models. model_groups lists
    each model's group; with strata the models are resampled within their group. Returns {name: {est, lo, hi, p,
    draws}}, p two-sided; a draw that gives a name no value is left out for that name."""
    n_models = len(model_groups)
    est = stat(np.ones(n_tables), np.ones(n_models))
    rng = random.Random(seed)
    by_g = defaultdict(list)
    for i, g in enumerate(model_groups):
        by_g[g if strata else None].append(i)
    got = defaultdict(list)
    for _ in range(draws):
        ct = np.bincount([rng.randrange(n_tables) for _ in range(n_tables)], minlength=n_tables).astype(float)
        picks = [rng.choice(ix) for g in sorted(by_g, key=str) for ix in [by_g[g]] for _ in ix]
        cm = np.bincount(picks, minlength=n_models).astype(float)
        for k, v in stat(ct, cm).items():
            if v is not None and np.isfinite(v):
                got[k].append(v)
    out = {}
    for k, v in est.items():
        d = np.array(got.get(k, []))
        # a draw that is zero in exact arithmetic (a difference of two equal shares) comes out at plus or minus 1e-17,
        # and its sign depends on the computer's sums; it counts as exactly zero, on both sides of the P value
        d = np.where(np.abs(d) < ZERO, 0.0, d)
        if v is not None and len(d) >= 50:
            lo, hi = np.percentile(d, [2.5, 97.5])
            out[k] = {"est": v, "lo": float(lo), "hi": float(hi),
                      "p": float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean()))), "draws": int(len(d))}
        else:
            out[k] = {"est": v, "lo": None, "hi": None, "p": None, "draws": int(len(d))}
    return out


# ---------- the data ----------

def load_population(path=POPULATION):
    return [json.loads(line) for line in gzip.open(path, "rt", encoding="utf8")]


def load_raw(path):
    opener = gzip.open if path.endswith(".gz") else open
    return {r["id"]: r for r in (json.loads(line) for line in opener(path, "rt", encoding="utf8"))}


def developers(path=CHARACTERISTICS):
    return {r["key"]: r["developer"] for r in csv.DictReader(open(path, encoding="utf8"))}


def cell_name(x):
    return f"{x['names']}-info{x['info']}"


def checks(pop, raw, codes, key):
    """The population run's checks (the analysis plan, condition 3, checks 1 to 3)."""
    ids = [x["id"] for x in pop]
    out = {"items": len(ids), "answered": sum(1 for i in ids if i in raw),
           "finish": dict(Counter(raw[i].get("finish") for i in ids if i in raw)),
           "read": sum(1 for i in ids if codes.get(i)) / len(ids), "read_by": {}}
    for name, f in (("group", lambda x: x["group"]), ("source", lambda x: x["source"]), ("cell", cell_name)):
        c, r = Counter(), Counter()
        for x in pop:
            c[f(x)] += 1
            r[f(x)] += bool(codes.get(x["id"]))
        out["read_by"][name] = {k: {"n": c[k], "read": r[k] / c[k]} for k in sorted(c)}
    sample = [json.loads(line) for line in open(SAMPLE, encoding="utf8") if line.strip()]
    sids = [x["id"] for x in sample]
    ref = AD.load_reference(REFERENCE)
    out["on_the_200_vs_reference"] = AD.compare(codes, ref, sids)
    if key in SAMPLE_RUNS:
        p = os.path.join(DATA, "judges", f"{key}-sample-answers.jsonl.gz")
        if os.path.exists(p):
            out["on_the_200_vs_own_sample_run"] = AD.compare(codes, AD.load_judge(p), sids)
    k = out["on_the_200_vs_reference"]["brand_any"]["kappa"]
    out["marked"] = bool(out["read"] < AD.MIN_READ or k is None or k < AD.MIN_KAPPA)
    return out


def rows_of(pop, codes, keep=lambda x: True):
    out = []
    for x in pop:
        c = codes.get(x["id"])
        if c and keep(x):
            out.append({**x, "y": 1.0 if c[1] == "yes" else 0.0, "reason": c[0]})
    return out


# ---------- the analysis under one judge ----------

def analyze_judge(rows, draws=2000, seed=SEED):
    tables = sorted({r["table"] for r in rows})
    models = sorted({r["model"] for r in rows})
    groups = [next(r["group"] for r in rows if r["model"] == m) for m in models]
    T = len(tables)

    def cube(f):
        return Cube([r for r in rows if f(r)], tables, models)
    every, dom2, req = cube(lambda r: True), cube(lambda r: r["source"] == "dom2"), cube(lambda r: r["source"] == "requests")
    cells = {f"{n}-info{i}": cube(lambda r, n=n, i=i: r["source"] == "dom2" and r["names"] == n and r["info"] == i)
             for n in ("original", "crossed") for i in (0, 1)}
    prices = {f"{c}-rung{p}": cube(lambda r, c=c, p=p: r["source"] == "dom2" and cell_name(r) == c and r["rung"] == p)
              for c in cells for p in (0, 2)}
    orig = cube(lambda r: r["source"] == "dom2" and r["names"] == "original")
    crossed = cube(lambda r: r["source"] == "dom2" and r["names"] == "crossed")
    info0 = cube(lambda r: r["source"] == "dom2" and r["info"] == 0)
    info1 = cube(lambda r: r["source"] == "dom2" and r["info"] == 1)

    def overall(ct, cm):
        out = {"all": mean_of_shares(every, ct, cm), "all_pooled": pooled_share(every, ct, cm),
               "dom2": mean_of_shares(dom2, ct, cm), "dom2_pooled": pooled_share(dom2, ct, cm),
               "original minus crossed": paired_difference(orig, crossed, ct, cm),
               "info0 minus info1": paired_difference(info0, info1, ct, cm)}
        for k, c in cells.items():
            out[k] = mean_of_shares(c, ct, cm)
            out[k + "_pooled"] = pooled_share(c, ct, cm)
        for k, c in prices.items():
            out[k] = mean_of_shares(c, ct, cm)
        return out
    res = {"n": len(rows), "models": len(models), "tables": T, "overall": boot(overall, T, groups, draws, seed)}
    gs = [g for g in GROUPS if g in groups]
    masks = {g: np.array([1.0 if x == g else 0.0 for x in groups]) for g in gs}

    def by_group(ct, cm):
        out = {}
        for g in gs:
            out[g] = mean_of_shares(dom2, ct, cm, masks[g])
            out[g + "_pooled"] = pooled_share(dom2, ct, cm, masks[g])
            for k, c in cells.items():
                out[f"{g}:{k}"] = mean_of_shares(c, ct, cm, masks[g])
            out[f"{g}:original minus crossed"] = paired_difference(orig, crossed, ct, cm, masks[g])
            out[f"{g}:info0 minus info1"] = paired_difference(info0, info1, ct, cm, masks[g])
        for i, g in enumerate(gs):
            for h in gs[i + 1:]:
                a, b = mean_of_shares(dom2, ct, cm, masks[g]), mean_of_shares(dom2, ct, cm, masks[h])
                out[f"{g} minus {h}"] = None if a is None or b is None else a - b
        return out
    res["groups"] = boot(by_group, T, groups, draws, seed, strata=True)
    res["group_models"] = {g: [m for m, x in zip(models, groups) if x == g] for g in gs}
    res["requests"] = boot(lambda ct, cm: {"claude": mean_of_shares(req, ct, cm, masks.get("claude")),
                                           "claude_pooled": pooled_share(req, ct, cm, masks.get("claude"))},
                           T, groups, draws, seed, strata=True) if "claude" in gs else {}
    # each model's own share, the bootstrap over tables
    per = {}
    for j, m in enumerate(models):
        n_m, t_m = int(every.N[:, j].sum()), int((every.N[:, j] > 0).sum())
        one = np.zeros(len(models))
        one[j] = 1
        if n_m < MIN_N or t_m < MIN_TABLES:
            per[m] = {"est": None, "lo": None, "hi": None, "n": n_m, "tables": t_m,
                      "not_estimable": f"{n_m} explanations in {t_m} tables (fewer than {MIN_N} or {MIN_TABLES})"}
            continue
        b = boot(lambda ct, cm: {"share": mean_of_shares(every, ct, one), "dom2": mean_of_shares(dom2, ct, one)},
                 T, ["x"] * len(models), draws, seed)
        per[m] = {**b["share"], "dom2": b["dom2"], "n": n_m, "tables": t_m, "group": groups[j], "not_estimable": ""}
    res["per_model"] = per
    est = [v["est"] for v in per.values() if v.get("est") is not None]
    res["per_model_spread"] = {"n_models": len(est), "mean": float(np.mean(est)), "sd": float(np.std(est, ddof=1)),
                               "min": float(min(est)), "max": float(max(est)),
                               "min_model": min((v["est"], m) for m, v in per.items() if v.get("est") is not None)[1],
                               "max_model": max((v["est"], m) for m, v in per.items() if v.get("est") is not None)[1]}
    res["reason_counts"] = {g: dict(Counter(r["reason"] for r in rows if r["group"] == g)) for g in gs}
    return res


def reference_by_cell():
    """The analysis plan's condition 3, item 8: the reference's brand_any on the stated 200, by stratum and by group, with counts
    (too few in each cell to decide)."""
    sample = [json.loads(line) for line in open(SAMPLE, encoding="utf8") if line.strip()]
    ref = AD.load_reference(REFERENCE)
    out = {}
    for name, f in (("stratum", AD.stratum), ("group", lambda x: x["group"]), ("source", lambda x: x["source"])):
        c, y = Counter(), Counter()
        for x in sample:
            if ref.get(x["id"]):
                c[f(x)] += 1
                y[f(x)] += ref[x["id"]][1] == "yes"
        out[name] = {k: {"n": c[k], "yes": y[k], "share": y[k] / c[k]} for k in sorted(c)}
    out["all"] = {"n": sum(1 for x in sample if ref.get(x["id"])),
                  "yes": sum(1 for x in sample if ref.get(x["id"]) and ref[x["id"]][1] == "yes")}
    return out


def agreement(pop, codes):
    """Every pair of judges on the population: brand_any and reason, overall, by group and by cell."""
    out = {}
    keys = sorted(codes)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            pair = {"all": AD.compare(codes[a], codes[b], [x["id"] for x in pop])}
            for name, f in (("group", lambda x: x["group"]), ("cell", lambda x: f"{x['source']}:{cell_name(x)}")):
                for k in sorted({f(x) for x in pop}):
                    pair[f"{name}={k}"] = AD.compare(codes[a], codes[b], [x["id"] for x in pop if f(x) == k])
            out[f"{a}|{b}"] = pair
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="append", default=[], help="<key>=<all-answers.jsonl.gz>")
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--out", default=os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "results", "explanations"))
    ap.add_argument("--checks-only", action="store_true", help="the population checks alone, before any share is read")
    ap.add_argument("--reference-only", action="store_true", help="the reference's codes on the 200 by cell alone")
    a = ap.parse_args()
    if a.reference_only:
        os.makedirs(a.out, exist_ok=True)
        rb = reference_by_cell()
        json.dump(rb, open(os.path.join(a.out, "REFERENCE-200.json"), "w", encoding="utf8"), indent=1)
        print(json.dumps(rb, indent=1))
        return
    pop = load_population()
    dev = developers()
    raw = {k: load_raw(p) for k, p in (x.split("=", 1) for x in a.judge)}
    codes = {k: {i: AD.parse(r.get("raw") or r.get("answer")) for i, r in v.items()} for k, v in raw.items()}
    if a.checks_only:
        ck = {k: checks(pop, raw[k], codes[k], k) for k in sorted(codes)}
        os.makedirs(a.out, exist_ok=True)
        json.dump(ck, open(os.path.join(a.out, "CHECKS.json"), "w", encoding="utf8"), indent=1)
        for k, v in ck.items():
            r, o = v["on_the_200_vs_reference"]["brand_any"], (v.get("on_the_200_vs_own_sample_run") or {}).get("brand_any", {})
            print(f"{k}: {v['answered']} of {v['items']} answered, finish {v['finish']}, read {v['read']:.4f}; on the "
                  f"200: kappa {r['kappa']:.3f} with the reference, {o.get('kappa')} with its own sample run; "
                  f"marked {v['marked']}")
            for name, by in v["read_by"].items():
                print("   ", name, {kk: round(vv["read"], 4) for kk, vv in by.items()})
        return
    # the 90 per cent rule: the models left out are reported apart, each with its own share under every judge, and every
    # pooled number below (shares, groups, the judges' agreement) is over the other models' explanations. The checks on
    # the stated 200 stay on the 200, since they validate the judges.
    apart = [x for x in pop if x["model"] in LEFT_OUT]
    pop = [x for x in pop if x["model"] not in LEFT_OUT]
    res = {"plan": "study2a-experience-attributes-stated-for-every-product/materials/explanations/analysis_plan.md, condition 3",
           "judges": sorted(codes), "draws": a.draws, "population": len(pop), "checks": {}, "shares": {},
           "own_left_out": {}, "developer_left_out": {}, "agreement": agreement(pop, codes),
           "reference_on_the_200": reference_by_cell()}
    res["left_out"] = {m: {**v, "explanations": sum(1 for x in apart if x["model"] == m), "share_by_judge": {}}
                       for m, v in LEFT_OUT.items()}
    for k in sorted(codes):
        for m in LEFT_OUT:
            ys = [codes[k][x["id"]][1] == "yes" for x in apart if x["model"] == m and codes[k].get(x["id"])]
            res["left_out"][m]["share_by_judge"][k] = {"n": len(ys), "share": sum(ys) / len(ys) if ys else None}
    for k in sorted(codes):
        res["checks"][k] = checks(pop, raw[k], codes[k], k)
        res["shares"][k] = analyze_judge(rows_of(pop, codes[k]), a.draws)
        res["own_left_out"][k] = analyze_judge(rows_of(pop, codes[k], lambda x, k=k: x["model"] != k), a.draws)["overall"]
        d = dev.get(k)
        res["developer_left_out"][k] = {"developer": d, "overall": analyze_judge(
            rows_of(pop, codes[k], lambda x, d=d: dev.get(x["model"]) != d), a.draws)["overall"]}
        print(f"{k}: read {res['checks'][k]['read']:.4f}, kappa on the 200 "
              f"{res['checks'][k]['on_the_200_vs_reference']['brand_any']['kappa']}, "
              f"share {res['shares'][k]['overall']['all']}", flush=True)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "numbers.json")
    json.dump(res, open(path, "w", encoding="utf8"), indent=1)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
