"""Study 1c's search step (study1c-product-feeds-and-a-store-search/materials/store/analysis_plan.md, the search step): brand searches in the first
prompt; with the catalog's names shown and hidden, the share of second prompts in which the store returned the
designated best product, the share whose answer recommends it, and the pick among the prompts where it was returned in
both name versions.

    python study1c-product-feeds-and-a-store-search/code/search/analyze_search.py --build s1 --panel claude --out study1c-product-feeds-and-a-store-search/results/search/claude
    python study1c-product-feeds-and-a-store-search/code/search/analyze_search.py --build s1 --panel open \\
        --stage1 study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz --letters study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz \\
        --leave-out kimi-linear48b --out study1c-product-feeds-and-a-store-search/results/search/open-all
    python study1c-product-feeds-and-a-store-search/code/search/analyze_search.py --build s1 --panel all \\
        --stage1 study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz --letters study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz \\
        --leave-out kimi-linear48b --out study1c-product-feeds-and-a-store-search/results/search/all-models

The prompts are in study1c-product-feeds-and-a-store-search/materials/search/<build>/; each model's second prompts were built by the store from that
model's own first answers (rebuild_prompts.py rebuilds them). The Claude models' answers are in
study1c-product-feeds-and-a-store-search/data/search/<stage>/<model>.jsonl.gz; the open models' first answers and second letters come from the computing
cluster's export (--stage1, and the rows of --letters whose study is b17, the search step). Every answer is read with
final_answer before it is parsed (common/parse_answer.py). Pooling and intervals as in
study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py: every table weighs equally within a model and every model equally, and the
intervals come from the two-way cluster bootstrap over tables and models. Holm corrects within the three primary
contrasts. Writes <out>/numbers.json, second_prompts.jsonl (one row per second prompt) and per_model.csv.
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
MAT = os.path.join(STUDY, "materials", "search")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "common"))   # parse_answer.py
sys.path.insert(0, os.path.join(STUDY, "code", "store"))   # analyze_harness.py
sys.path.insert(0, os.path.join(ROOT, "study1b-64-models-on-34-tables", "code", "selection"))   # select_requests.py
import analyze_harness as AH  # noqa: E402
import search_store as Q  # noqa: E402
import select_requests as SR  # noqa: E402
from parse_answer import final_answer, pick  # noqa: E402


def from_folder(model):
    """True for a model whose answers are in this package's answer files (study1c-product-feeds-and-a-store-search/data/search/), not in the
    computing cluster's export"""
    return model.startswith(("claude-", "gpt-6"))


def first_answers(a, stage, model):
    """{item id: the model's first answer, reasoning removed}; an open model's from the export, a Claude model's from
    its answer file"""
    if a.stage1 and not from_folder(model):
        return {r["id"]: r["final"] for r in map(json.loads, gzip.open(a.stage1, "rt", encoding="utf8"))
                if r["model"] == model}
    return {iid: final_answer(t) for iid, t in answers_of(stage, model).items()}


def second_letters(a, stage, model):
    """{item id: the letter of the model's second answer ("" when it gives none)}"""
    if a.letters and not from_folder(model):
        return {r["id"]: r["letter"] for r in csv.DictReader(gzip.open(a.letters, "rt", encoding="utf8"))
                if r["study"] == "b17" and r["build"] == "stage2" and r["model"] == model}
    return {iid: pick(final_answer(t))[0] for iid, t in answers_of(stage, model).items()}


def answers_of(stage, model):
    """{item id: answer text} for a model whose answers are in this package (study1c-product-feeds-and-a-store-search/data/search/<stage>/<model>.jsonl.gz)"""
    out = {}
    path = os.path.join(STUDY, "data", "search", stage, f"{model}.jsonl.gz")
    if os.path.exists(path):
        for line in gzip.open(path, "rt", encoding="utf8"):
            r = json.loads(line)
            out[r["id"]] = r["answer_text"]
    return out


def mean_pm(vals):
    return AH.pooled(vals)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    ap.add_argument("--panel", choices=["claude", "open", "all"], required=True)
    ap.add_argument("--stage1", help="the open models' first answers (study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz)")
    ap.add_argument("--letters", help="the open models' letters (study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz)")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--out")
    ap.add_argument("--leave-out", action="append", default=[],
                    help="a model left out of every estimate under the 90 per cent rule (AH.LEAVE_OUT_RULE)")
    a = ap.parse_args()
    corpus, dom = Q.load()
    brands_ci, table_brands = SR.brand_sets()
    s1 = {json.loads(l)["id"]: json.loads(l) for l in gzip.open(os.path.join(MAT, a.build, "stage1", "prompts.jsonl.gz"),
                                                             "rt", encoding="utf8")}
    models = sorted(os.path.basename(p)[:-len(".jsonl.gz")] for p in glob.glob(os.path.join(MAT, a.build, "stage2", "*.jsonl.gz"))
                    if a.panel == "all" or os.path.basename(p).startswith("claude-") == (a.panel == "claude"))
    left = sorted(set(a.leave_out) & set(models))     # the 90 per cent rule (AH.LEAVE_OUT_RULE)
    models = [m for m in models if m not in left]
    brand_any, brand_own = {}, {}
    s2rows = []
    for m in models:
        ans1 = first_answers(a, "stage1", m)
        per = defaultdict(lambda: [0, 0, 0])
        for iid, it in s1.items():
            if iid not in ans1:
                continue
            qs = " ".join(Q.parse_queries(ans1[iid]))
            own = [b for b in table_brands[it["table"].removesuffix("_dom")] if b in SR.find_brands_ci(brands_ci, qs)]
            per[it["table"]][0] += 1
            per[it["table"]][1] += bool(SR.find_brands_ci(brands_ci, qs))
            per[it["table"]][2] += bool(own)
        for t, (n, b, o) in per.items():
            brand_any[(m, t)] = b / n
            brand_own[(m, t)] = o / n
        items = [json.loads(l) for l in gzip.open(os.path.join(MAT, a.build, "stage2", f"{m}.jsonl.gz"), "rt", encoding="utf8")]
        nothing = [json.loads(l) for l in gzip.open(os.path.join(MAT, a.build, "nothing-returned", f"{m}.jsonl.gz"), "rt",
                                                    encoding="utf8")]
        ans2 = second_letters(a, "stage2", m)
        for it in items:
            L = ans2.get(it["id"], "")
            s2rows.append({"model": m, "table": it["table"], "trial": it["trial"], "names": it["names"], "rung": it["rung"],
                           "fetched": it["fetched"], "answered": it["id"] in ans2, "letter": L,
                           "picked_best": int(L == it["best"]) if L else None})
        for k in nothing:
            s2rows.append({**{x: k[x] for x in ("model", "table", "trial", "names", "rung")}, "fetched": False,
                           "answered": False, "letter": "", "picked_best": 0})
    cell = defaultdict(lambda: defaultdict(list))
    for r in s2rows:
        cell[(r["model"], r["table"])][r["names"]].append(r)
    fetched, pick_s, pick_f, pick_both = defaultdict(dict), defaultdict(dict), defaultdict(dict), {}
    for (m, t), g in cell.items():
        for names, rows in g.items():
            fetched[names][(m, t)] = sum(r["fetched"] for r in rows) / len(rows)
            got = [r for r in rows if r["picked_best"] is not None]
            if got:
                pick_s[names][(m, t)] = sum(r["picked_best"] for r in got) / len(got)
            seen = [r for r in got if r["fetched"]]
            if seen:
                pick_f[names][(m, t)] = sum(r["picked_best"] for r in seen) / len(seen)
        both = {}
        for r in g.get("original", []) + g.get("hidden", []):
            both.setdefault((r["trial"], r["rung"]), {})[r["names"]] = r
        pairs = [v for v in both.values() if len(v) == 2 and all(x["fetched"] and x["picked_best"] is not None for x in v.values())]
        if pairs:
            pick_both[(m, t)] = sum(v["hidden"]["picked_best"] - v["original"]["picked_best"] for v in pairs) / len(pairs)

    def diff(h, o):
        return {k: h[k] - o[k] for k in h if k in o}

    numbers = {"build": a.build, "panel": a.panel, "models": models, "second prompts": len(s2rows)}
    if left:
        numbers["left_out"] = {}
        for m in left:                                # reported apart: its second answers and how many gave a letter
            ans2 = second_letters(a, "stage2", m)
            numbers["left_out"][m] = {"rule": AH.LEAVE_OUT_RULE, "second answers": len(ans2),
                                      "with a letter": sum(1 for L in ans2.values() if L)}
    est = lambda v: AH.estimate(v, a.draws)
    numbers["brand search, any brand of the 34 tables"] = est(brand_any)
    numbers["brand search, one of the table's own brands"] = est(brand_own)
    for names in ("original", "hidden"):
        numbers[f"fetched, names {names}"] = est(fetched[names])
        numbers[f"picked the best product, names {names}"] = est(pick_s[names])
        numbers[f"picked the best product where it was fetched, names {names}"] = est(pick_f[names])
    numbers["fetched: hidden minus shown (primary 1)"] = est(diff(fetched["hidden"], fetched["original"]))
    numbers["picked the best: hidden minus shown (primary 2)"] = est(diff(pick_s["hidden"], pick_s["original"]))
    numbers["picked the best where fetched in both: hidden minus shown (primary 3)"] = est(pick_both)
    fam = {k: v["interval"]["p_two_sided"] for k, v in numbers.items() if "primary" in k and isinstance(v, dict) and v.get("interval")}
    run = 0.0
    for i, k in enumerate(sorted(fam, key=fam.get)):
        run = max(run, min(1.0, (len(fam) - i) * fam[k]))
        numbers[k]["holm"] = run
    out = a.out or os.path.join(STUDY, "results", "search", a.panel)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    with open(os.path.join(out, "second_prompts.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in s2rows:
            f.write(json.dumps(r) + "\n")
    # each model's three primary contrasts with intervals from its own tables, for the analysis of how models differ
    AH.write_per_model(os.path.join(out, "per_model.csv"), AH.per_model_rows({
        "fetched: hidden minus shown": {"primary 1": diff(fetched["hidden"], fetched["original"])},
        "picked the best: hidden minus shown": {"primary 2": diff(pick_s["hidden"], pick_s["original"])},
        "picked the best where fetched in both: hidden minus shown": {"primary 3": pick_both}}))
    for k, v in numbers.items():
        if isinstance(v, dict) and "pooled" in v and v["pooled"] is not None:
            iv = v.get("interval")
            print(f"{k:75s} {100 * v['pooled']:6.1f}" + (f"  ({100 * iv['low95']:.1f} to {100 * iv['high95']:.1f})" if iv else ""))


if __name__ == "__main__":
    main()
