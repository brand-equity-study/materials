"""Study 1b as one panel: the brand gap pooled over every model that answered the corpus's 34 tables with names
shown and with names hidden.

The panel: the 30 models of the corpus (study1b-64-models-on-34-tables/data/corpus/), the nine models that answered the corpus's own prompts
again (study1b-64-models-on-34-tables/data/rerun/: four Claude 5.x models through the Messages API, four GPT-6.x models through Codex and
Claude Fable 5.2 through the Claude command line), and every open model that answered the same prompts on the
computing cluster (their letters, study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz and, for Qwen 3.5 122B,
letters-13394.csv.gz; the rows of study1-rerun/s1rerun1). A model run with and without extended thinking counts as two
configurations, as the corpus counted it. Each set of weights is counted once: the cluster's runs of Gemma 4 31B and
Gemma 3 27B, which the corpus also ran through a provider, are left out of the primary panel and kept in a check. A
model with a letter in under 90 per cent of its answers is left out under the open-models rule
(models/open_models_plan.md), with the dated decision in LEAVE_OUT. The outcome is the share of answers that do not pick the
designated optimal product, with names shown minus with names hidden, trial-weighted, an answer without a letter
counted as not picking it (as the corpus counted it). The pooled interval and P come from common.py's two-way
bootstrap (models and tables resampled with replacement and crossed; 10,000 draws, seed 20261120); each model's own
interval resamples its tables.

Before pooling, four checks; a model that fails one is left out with the reason:
  1. it has answers with names shown and hidden in every one of the 34 tables;
  2. a model of the rerun answered exactly the rerun's names-shown and names-hidden items (1,360 prompts);
  3. a corpus model's rows with names shown show, in every table, the products of that corpus table, and its rows with
     names hidden show only the masked names "Product A" to "Product E";
  4. every rerun item copies a corpus trial of the same table and condition (the item's source trial id).

    python study1b-64-models-on-34-tables/code/16_pooled.py [--draws 10000]
Writes study1b-64-models-on-34-tables/results/pooled/numbers.json and per_model.csv.
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import argparse
import csv
import gzip
import json
import pathlib
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PKG = HERE.parents[1]   # the package
sys.path.insert(0, str(PKG))
import importlib.util  # noqa: E402
import common as cc  # noqa: E402
_spec = importlib.util.spec_from_file_location("rerun", HERE / "08_rerun.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)   # 08_rerun.py's loader of the rerun answers
from experiment.assortments import ALL_ASSORTMENTS  # noqa: E402

OPEN_LETTERS = [PKG / "study2a-experience-attributes-stated-for-every-product" / "data" / "open-panel" / "letters-12683.csv.gz",   # the open models' letters
                PKG / "study2a-experience-attributes-stated-for-every-product" / "data" / "open-panel" / "letters-13394.csv.gz"]   # and Qwen 3.5 122B's
# the open-models rule (models/open_models_plan.md), as every other study applies it
LEAVE_OUT = {"kimi-linear48b": "left out of every estimate under the open-models rule (models/open_models_plan.md: "
                               "a model whose answers are read in under 90 per cent of the answers that are not "
                               "declines is reported apart); the decision is dated in "
                               "study1c-product-feeds-and-a-store-search/materials/store/analysis_plan.md, 22 November 2026"}
MIN_LETTERED = 0.90
CHARS = PKG / "models" / "model_characteristics.csv"
OUT = cc.RESULTS / "pooled"
NAMES = {"shown": cc.SHOWN, "hidden": cc.HIDDEN}
# the open models also run, with the same weights, through a provider in the corpus (a check leaves the cluster's copy out)
SAME_WEIGHTS = {"gemma31b": "gemma-4-31b-it", "gemma3-27b": "gemma-3-27b"}


def corpus_rows():
    cols = ["trial_id", "model_key", "assortment_id", "condition", "chose_optimal", "choice"] + \
           [f"product_{L}_name" for L in "ABCDE"]
    df, info = cc.load_rows(cols)
    df = df[df.condition.isin([cc.SHOWN, cc.HIDDEN])].copy()
    df["non_optimal"] = 1.0 - df["chose_optimal"].astype(float)
    return df, info


def rerun_rows():
    items, d = R.load()
    d = d[d.names.isin(NAMES)].copy()
    d["condition"] = d.names.map(NAMES)
    d["non_optimal"] = d["nonopt"].astype(float)
    return items, d


def open_rows(files=None):
    """The open models' s1rerun1 answers with names shown and hidden, from every letters file; refuses an item that two
    files hold. Returns the rows and each model's share of answers with a letter."""
    rows, seen, lettered = [], {}, defaultdict(lambda: [0, 0])
    for path in files or OPEN_LETTERS:
        for r in csv.DictReader(gzip.open(path, "rt", encoding="utf8")):
            if "s1rerun1" in r["build"] and r["names"] in NAMES:
                key = (r["model"], r["id"])
                if key in seen:
                    raise SystemExit(f"refused: {r['model']} item {r['id']} is in {seen[key].name} and {path.name}")
                seen[key] = path
                lettered[r["model"]][0] += 1
                lettered[r["model"]][1] += bool(r["letter"])
                rows.append({"model_key": r["model"], "id": r["id"], "assortment_id": r["table"],
                             "condition": NAMES[r["names"]],
                             "non_optimal": 0.0 if r["letter"] and r["letter"] == r["best"] else 1.0})
    share = {m: b / a for m, (a, b) in sorted(lettered.items())}
    return pd.DataFrame(rows), share


def open_models_rule(share):
    """{model: record} for the models that the rule leaves out; refuses a model under the threshold that it does not
    name, so that no model is dropped or kept without a dated decision."""
    low = sorted(m for m, s in share.items() if s < MIN_LETTERED and m not in LEAVE_OUT)
    if low:
        raise SystemExit(f"refused: {low} have a letter in under {MIN_LETTERED:.0%} of their answers and the rule names "
                         "no decision for them (count their declines with common/decline.py first)")
    return {m: {"rule": LEAVE_OUT[m], "share of answers with a letter": round(share[m], 4)}
            for m in sorted(LEAVE_OUT) if m in share}


def checks(corpus, rerun, opened, items):
    """{model: reason} for every model that fails a check, and the checks' counts."""
    tables = sorted(t["id"] for t in ALL_ASSORTMENTS)
    left_out, report = {}, {}
    allrows = pd.concat([corpus[["model_key", "assortment_id", "condition"]], rerun[["model_key", "assortment_id", "condition"]],
                         opened[["model_key", "assortment_id", "condition"]]])
    # 1. both conditions in every table
    have = allrows.groupby(["model_key", "condition"]).assortment_id.nunique()
    for m in allrows.model_key.unique():
        for cond in (cc.SHOWN, cc.HIDDEN):
            if have.get((m, cond), 0) != len(tables):
                left_out[m] = f"answers in {have.get((m, cond), 0)} of {len(tables)} tables with condition {cond}"
    report["1 both conditions in all 34 tables"] = f"{allrows.model_key.nunique() - len(left_out)} of {allrows.model_key.nunique()} models"
    # 2. the rerun models answered exactly the rerun's shown and hidden items
    want = {i for i, it in items.items() if it["names"] in NAMES}
    for frame in (rerun, opened):
        for m, g in frame.groupby("model_key"):
            got = set(g["id"])
            if got != want:
                left_out.setdefault(m, f"answered {len(got & want)} of the {len(want)} rerun prompts and {len(got - want)} others")
    report["2 rerun prompts"] = f"{len(want)} prompts (names shown and hidden); models checked: {rerun.model_key.nunique() + opened.model_key.nunique()}"
    # 3. corpus models: with names shown, the products of each table; with names hidden, only masked names
    #    ("Product A" to "Product E"), as the corpus stores the brand-blind condition
    products = {t["id"]: {p["name"] for p in t["products"]} for t in ALL_ASSORTMENTS}
    masked = {f"Product {L}" for L in "ABCDE"}
    bad = defaultdict(int)
    names = corpus[[f"product_{L}_name" for L in "ABCDE"]].astype(str).to_numpy()
    for row_names, m, t, cond in zip(names, corpus.model_key.to_numpy(), corpus.assortment_id.to_numpy(), corpus.condition.to_numpy()):
        want = products.get(t, set()) if cond == cc.SHOWN else masked
        if set(row_names) != want:
            bad[m] += 1
    for m, k in bad.items():
        left_out.setdefault(m, f"{k} rows show products other than their corpus table's")
    report["3 corpus products"] = f"rows whose products differ from their table's: {sum(bad.values())}"
    # 4. every rerun item copies a corpus trial of the same table and condition
    trials = corpus.set_index("trial_id")[["assortment_id", "condition"]]
    miss = 0
    for it in items.values():
        if it["names"] not in NAMES:
            continue
        tid = it["source"]["trial_id"]
        if tid not in trials.index:
            miss += 1
            continue
        row = trials.loc[tid]
        row = row.iloc[0] if isinstance(row, pd.DataFrame) else row
        if row.assortment_id != it["table"] or row.condition != NAMES[it["names"]]:
            miss += 1
    report["4 rerun items copy corpus trials"] = f"items without a matching corpus trial: {miss}"
    if miss:
        for m in list(rerun.model_key.unique()) + list(opened.model_key.unique()):
            left_out.setdefault(m, f"{miss} of the rerun's items match no corpus trial of the same table and condition")
    return left_out, report


def gap_of(arr, i):
    (s1, n1), (s0, n0) = arr[cc.SHOWN], arr[cc.HIDDEN]
    return float(s1[i].sum() / n1[i].sum() - s0[i].sum() / n0[i].sum()), float(s1[i].sum() / n1[i].sum()), float(s0[i].sum() / n0[i].sum()), int(n1[i].sum() + n0[i].sum())


def pooled(df, draws):
    models, tables, arr = cc.cell_arrays(df, "non_optimal")
    g = cc.pooled_gap(arr)
    bs = cc.twoway_bootstrap(arr, len(models), len(tables), draws=draws, seed=cc.SEED)
    return models, tables, arr, {"gap_pp": round(100 * g, 2), "ci95_pp": cc.ci(bs, 100), "p_two_sided": cc.p_two_sided(bs),
                                 "models": len(models), "tables": len(tables), "draws": draws, "seed": cc.SEED}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=cc.DRAWS)
    a = ap.parse_args()
    corpus, info = corpus_rows()
    items, rerun = rerun_rows()
    opened, lettered = open_rows()
    rule_out = open_models_rule(lettered)
    opened = opened[~opened.model_key.isin(rule_out)]
    left_out, report = checks(corpus, rerun, opened, items)
    left_out.update({m: v["rule"] + f" (a letter in {100 * v['share of answers with a letter']:.1f} per cent of its "
                                     "answers)" for m, v in rule_out.items()})
    cols = ["model_key", "assortment_id", "condition", "non_optimal"]
    df_all = pd.concat([corpus[cols], rerun[cols], opened[cols]])
    df_all = df_all[~df_all.model_key.isin(left_out)]
    # the primary panel counts each set of weights once: the cluster's runs of two models that
    # the corpus also ran through a provider are left out of it, and the panel with them is a check
    df = df_all[~df_all.model_key.isin(SAME_WEIGHTS)]
    chars = {r["key"]: r for r in csv.DictReader(open(CHARS, encoding="utf8"))}
    models, tables, arr, main_est = pooled(df, a.draws)
    nochar = [m for m in models if m not in chars]
    if nochar:
        raise SystemExit(f"refused: no characteristics row for {nochar}")
    devs = {m: chars[m]["developer"] for m in models}
    open_w = {m: chars[m]["open"] == "open" for m in models}
    per_model = []
    for i, m in enumerate(models):
        g, s, h, n = gap_of(arr, i)
        bs = cc.one_way_bootstrap(arr, 0, i, draws=a.draws, seed=cc.SEED)
        per_model.append({"model": m, "developer": devs[m], "open_weights": open_w[m],
                          "thinking": "on" if ("thinking" in m or chars[m].get("thinking") == "on") else "",
                          "gap_pp": round(100 * g, 2), "ci95_low_pp": cc.ci(bs, 100)[0], "ci95_high_pp": cc.ci(bs, 100)[1],
                          "shown_nonoptimal_pct": round(100 * s, 2), "hidden_nonoptimal_pct": round(100 * h, 2), "answers": n})
    leave_out = {}
    for d in sorted(set(devs.values())):
        keep = df[df.model_key.map(devs) != d]
        _, _, _, est = pooled(keep, a.draws)
        leave_out[d] = {"models_left_out": sum(1 for m in models if devs[m] == d), **est}
    # two subsets of the tables, from the corpus re-analysis's own lists (study1b-64-models-on-34-tables/results/numbers.json):
    # item 3's tables where the best product is dominant on every attribute with an order (group_ordered_only, 1
    # dominant), and the tables left after item 4's tables whose names-hidden prompt still named a brand (kind 1)
    corpus_numbers = json.load(open(cc.NUMBERS, encoding="utf8"))
    dominant = corpus_numbers["strict_dominance"]["groups"]["group_ordered_only"]["1 dominant"]["tables"]
    leak = corpus_numbers["names_hidden_leaks"]["gap_without"]["without kind 1 (brand named)"]["dropped_tables"]
    _, _, _, est_dom = pooled(df[df.assortment_id.isin(dominant)], a.draws)
    _, _, _, est_leak = pooled(df[~df.assortment_id.isin(leak)], a.draws)
    subsets = {"pooled_dominant_on_ordered_attributes": {"tables_kept": sorted(dominant),
                                                         "source": "study1b-64-models-on-34-tables/results/numbers.json, strict_dominance, group_ordered_only, 1 dominant",
                                                         **est_dom},
               "pooled_without_brand_leak_tables": {"tables_dropped": sorted(leak),
                                                    "source": "study1b-64-models-on-34-tables/results/numbers.json, names_hidden_leaks, without kind 1 (brand named)",
                                                    **est_leak}}
    all_models, _, _, with_copies = pooled(df_all, a.draws)
    all_devs = {m: chars[m]["developer"] for m in all_models}
    numbers = {"panel": "every set of weights that answered the corpus's 34 tables with names shown and hidden, counted once "
                        "(each set of weights counted once)",
               "outcome": "share of answers not picking the optimal product, names shown minus names hidden, points (item 1's)",
               "corpus_file": info, "open_letters": [str(p.relative_to(PKG)).replace("\\", "/") for p in OPEN_LETTERS],
               "checks": report, "left_out": left_out,
               "pooled": main_est, "developers": len(set(devs.values())), "models_with_open_weights": sum(open_w.values()),
               "per_model": per_model, "leave_one_developer_out": leave_out, **subsets,
               "check_with_the_cimarron_copies_of_two_corpus_models": {
                   "added": SAME_WEIGHTS, "developers": len(set(all_devs.values())),
                   "models_with_open_weights": sum(chars[m]["open"] == "open" for m in all_models), **with_copies}}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "numbers.json", "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    with open(OUT / "per_model.csv", "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_model[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(per_model, key=lambda r: r["gap_pp"]))
    print(json.dumps({k: numbers[k] for k in ("checks", "left_out", "pooled", "developers", "models_with_open_weights")}, indent=1))


if __name__ == "__main__":
    main()
