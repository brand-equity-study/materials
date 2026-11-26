"""The first design's replication (Study 3a): the first design trained again on Qwen 2.5 7B, OLMo 2 7B and Llama 3.1
8B with five training seeds, read as the first design is read. The reader, the planted and optimal options, the paired
lift cells and the naming count are planted_text.py's own (imported, not copied), so that each run is read exactly as
the first design's runs are. Added: a contrast over seeds (the mean over the seeds of each seed's contrast) with an
interval that resamples the eight decisions of each domain within the domain (one draw shared by the seeds and the two
sets of pages) and the seeds (paired across the two sets), and Holm's correction across the three primary contrasts.

    python study3a-pages-about-new-brands/code/first-design-replication/analyze_replication.py --runs study3a-pages-about-new-brands/data/replication-runs/<family> \
        --out study3a-pages-about-new-brands/results/training/parts/oct_<qwen|olmo|llama>.json
    python study3a-pages-about-new-brands/code/first-design-replication/analyze_replication.py --october --out <json>
        (the first design's own four runs of Qwen2.5-7B, seed 20261001)

A run's folder holds open_<pages>-<stage>.csv.gz, battery_<pages>-<stage>.csv.gz and battery_supp_<pages>-<stage>.csv.gz,
and its name ends in -<pages>-s<seed>. --runs takes run folders or the folder of a family's runs.
"""
import argparse
import json
import os
import pathlib
import re
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parents[2]   # the package
sys.path.insert(0, str(HERE.parent))   # Study 3a's code: planted_text.py, the first design's reader
import planted_text as S  # noqa: E402

ARMS = ("none", "neutralclean", "promo", "negative")  # none, plain, promotional, critical
NAMES = {"none": "NONE", "neutralclean": "PLAIN", "promo": "PROMOTIONAL", "negative": "CRITICAL"}
PRIMARY = (("neutralclean", "none"), ("promo", "neutralclean"), ("negative", "none"))
NAMING = (("promo", "neutralclean"), ("negative", "none"))
DOMS = S.DOMS5
OCTOBER = S.RUNS_DIR / "qwen2.5-7b"   # the first design's own runs of Qwen2.5-7B (seed 20261001)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [None] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        out[i] = round(run, 4)
    return out


def eval_folder(folder):
    """The folder that holds a run's files."""
    return pathlib.Path(folder).resolve()


def csv_of(folder, name):
    """A run's file: <name>.csv.gz (the replication's runs) or <name>.csv (the first design's)."""
    gz = folder / f"{name}.csv.gz"
    return gz if gz.exists() else folder / f"{name}.csv"


def model_of(folder, arm, stage, items):
    """planted_text.model() for a run folder of this amendment (the same three files)."""
    folder = eval_folder(folder)
    lab = f"{arm}-{stage}"
    d = pd.concat([S.read_battery(csv_of(folder, f"battery_{lab}"), items, False),
                   S.read_battery(csv_of(folder, f"battery_supp_{lab}"), items, False)], ignore_index=True)
    return {"rows": d, "doms": DOMS, "naming": S.naming(csv_of(folder, f"open_{lab}"), DOMS, False), "label": lab}


def lift(c):
    return {dm: 100 * c[dm]["sum"].sum() / c[dm]["n"].sum() for dm in DOMS}


def contrast(ca, cb, draws=S.DRAWS, seed=S.SEED):
    """ca, cb: one dict a seed of lift cells (planted_text.lift_cells) by domain, in the same seed order. The estimate
    is the mean over seeds of (the mean over domains of a's lift minus b's); cb None gives a's lift alone."""
    rng = np.random.default_rng(seed)
    k = len(ca)
    la = np.array([np.mean(list(lift(c).values())) for c in ca])
    lb = np.array([np.mean(list(lift(c).values())) for c in cb]) if cb else np.zeros(k)
    ns = len(ca[0][DOMS[0]]["sum"])
    sa, sb = np.zeros((draws, k)), np.zeros((draws, k))
    for dm in DOMS:
        idx = rng.integers(0, ns, (draws, ns))  # the decisions of the domain, one draw for every seed and version
        for j in range(k):
            sa[:, j] += 100 * ca[j][dm]["sum"][idx].sum(1) / ca[j][dm]["n"][idx].sum(1) / len(DOMS)
            if cb:
                sb[:, j] += 100 * cb[j][dm]["sum"][idx].sum(1) / cb[j][dm]["n"][idx].sum(1) / len(DOMS)
    pick = rng.integers(0, k, (draws, k))  # the seeds, paired across the two versions
    rows = np.arange(draws)[:, None]
    d = sa[rows, pick].mean(1) - sb[rows, pick].mean(1)
    out = {"estimate": round(float(la.mean() - lb.mean()), 2), "ci95": S.ci(d), "p_two_sided": S.p2(d), "seeds": k,
           "per_seed": [round(float(x), 2) for x in la - lb]}
    if cb:
        out.update({"a_lift": round(float(la.mean()), 2), "b_lift": round(float(lb.mean()), 2)})
    return out


def naming(models):
    """Answers to the primary open questions that name the planted brand, summed over the seeds."""
    k = sum(m["naming"][d][0] for m in models for d in DOMS)
    n = sum(m["naming"][d][1] for m in models for d in DOMS)
    return {"pooled": f"{k}/{n}", "pooled_pct": round(100 * k / n, 1), "pooled_ci95_wilson": S.wilson(k, n),
            "per_seed_pct": [round(100 * sum(m["naming"][d][0] for d in DOMS) / sum(m["naming"][d][1] for d in DOMS), 1)
                             for m in models], "_k": k, "_n": n}


def family(runs, items, draws=S.DRAWS):
    """runs: {(arm, seed): folder}. Every arm must have the same seeds."""
    seeds = sorted({s for _, s in runs})
    missing = [(a, s) for a in ARMS for s in seeds if (a, s) not in runs]
    if missing:
        raise SystemExit(f"refused: runs missing {missing}")
    res = {"seeds": seeds, "versions": {a: NAMES[a] for a in ARMS}}
    for stage in ("dpo", "sft"):
        M = {a: [model_of(runs[(a, s)], a, stage, items) for s in seeds] for a in ARMS}
        C = {a: [{dm: S.lift_cells(m, dm) for dm in DOMS} for m in M[a]] for a in ARMS}
        st = {"lift": {a: contrast(C[a], None, draws) for a in ARMS}, "contrasts": {}}
        for a, b in PRIMARY:
            st["contrasts"][f"{a}_minus_{b}"] = contrast(C[a], C[b], draws)
        for key, p in zip(list(st["contrasts"]), holm([v["p_two_sided"] for v in st["contrasts"].values()])):
            st["contrasts"][key]["p_holm"] = p
        # each set of pages against none, for the paper's table; outside the three primary contrasts and their
        # Holm family
        st["each_against_none"] = {f"{a}_minus_none": contrast(C[a], C["none"], draws) for a in ARMS if a != "none"}
        nb = {a: naming(M[a]) for a in ARMS}
        st["naming"] = {a: {k: v for k, v in nb[a].items() if not k.startswith("_")} for a in ARMS}
        for a, b in NAMING:
            st["naming"][f"{a}_minus_{b}"] = S.naming_diff(nb[a], nb[b])
        st["factual"] = {a: [S.factual(m) for m in M[a]] for a in ARMS}
        res[stage] = st
    return res


RUN_RE = re.compile(r"-(none|neutralclean|promo|negative)-s(\d+)$")


def runs_of(folders):
    """{(pages, seed): folder}; a folder that holds run folders stands for all of them."""
    folders = [g for f in folders for g in (sorted(p for p in pathlib.Path(f).iterdir() if p.is_dir())
                                            if not RUN_RE.search(pathlib.Path(f).name) else [f])]
    out = {}
    for f in folders:
        m = RUN_RE.search(pathlib.Path(f).name)
        if not m:
            raise SystemExit(f"refused: {f} is not named -<version>-s<seed>")
        out[(m.group(1), int(m.group(2)))] = f
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--october", action="store_true")
    ap.add_argument("--draws", type=int, default=S.DRAWS)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    items, _, _, _ = S.load_items()
    runs = {(arm, 20261001): OCTOBER / arm / "answers" for arm in ARMS} if a.october else runs_of(a.runs)
    res = family(runs, items, a.draws)
    res["runs"] = {f"{k[0]}-s{k[1]}": pathlib.Path(v).resolve().relative_to(PKG).as_posix()
                   for k, v in sorted(runs.items())}
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    return res


if __name__ == "__main__":
    main()
