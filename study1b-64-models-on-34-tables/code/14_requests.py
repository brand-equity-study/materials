"""Study 1, consumers' own shopping requests: the name gap when the request is one that a person typed to a chat
assistant, and the contrasts around it.

Each request in the bank (study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz) was paired with the strictly better tables of
its category, and each pair was shown in three versions that differ only in the product names: names hidden; the
original names (an invented name on the best product, familiar names on the others); and crossed names (a familiar name
on the best product, the invented name on one familiar product). The prompts are in prompts.jsonl.gz beside the bank,
and the answers of the four Claude models in study1b-64-models-on-34-tables/data/requests.

For every answer: the letter (common/parse_answer.py) and whether it is the designated product (the best product
of the table, the one that holds the invented name in the original version). For each request, table and model:
  penalty = 1 if the designated product is picked with names hidden, minus 1 if it is picked with the original names;
            its mean is the name gap, the primary contrast
  premium = picked with the crossed names minus picked with names hidden
  needs_best = the product that the needs coder named in place of the designated product; the penalty is reported
            again without those pairs
Means weight every request and table pair equally within a model and every model equally. Intervals: a two-way cluster
bootstrap that resamples requests and tables with replacement, independently (10,000 draws, seed 20261120); a pair's
weight in a draw is the product of the times its request and its table were drawn. P values are two-sided.

    python study1b-64-models-on-34-tables/code/14_requests.py      writes study1b-64-models-on-34-tables/results/requests/answers.csv, pairs.csv and numbers.json
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import argparse
import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "common"))
from parse_answer import final_answer, pick  # noqa: E402  (the parser of Study 1)
MAT = os.path.join(ROOT, "study1b-64-models-on-34-tables", "materials", "requests")
DATA = os.path.join(ROOT, "study1b-64-models-on-34-tables", "data", "requests")
CODEX = os.path.join(ROOT, "study1b-64-models-on-34-tables", "data", "requests-codex")   # the GPT-6 models through Codex
OPEN = os.path.join(ROOT, "study1b-64-models-on-34-tables", "data", "open-models", "requests")   # the open models, on a university computing cluster
AUTHOR_SET = "strictly-better-tables"  # Study 1's tables with the corpus's own request line
LEAVE_OUT_RULE = ("left out of every estimate under the open-models rule (models/open_models_plan.md: a "
                  "model whose answers the parser reads in under 90 per cent of a build's items is reported apart)")

SEED = 20261120


def _read_gz(path):
    with gzip.open(path, "rt", encoding="utf8") as f:
        return [json.loads(line) for line in f]


def load(build=None, open_answers=None):
    """The prompts and every answer to them: study1b-64-models-on-34-tables/materials/requests/prompts.jsonl.gz, the Claude models' answers
    (study1b-64-models-on-34-tables/data/requests/<model>/<names>.jsonl.gz) and, with open_answers (the run over every model), the folders it
    names: the GPT-6 models' answers through Codex (study1b-64-models-on-34-tables/data/requests-codex/<model>/) and the open models' answers
    (study1b-64-models-on-34-tables/data/open-models/requests/<model>/), each answer as the server returned it. Every answer is read with final_answer before
    pick, which removes reasoning that a model leaves in its output. An item answered twice by one model is refused."""
    items = {it["id"]: it for it in _read_gz(os.path.join(MAT, "prompts.jsonl.gz"))}
    rows, seen = [], set()
    for folder in [DATA] + list(open_answers or []):
        for mdir in sorted(glob.glob(os.path.join(folder, "*"))):
            if not os.path.isdir(mdir):
                continue
            model = os.path.basename(mdir)
            answers = [a for f in sorted(glob.glob(os.path.join(mdir, "*.jsonl.gz"))) for a in _read_gz(f)]
            for a in sorted(answers, key=lambda a: (a.get("batch", 0), a["id"])):   # the order in which they were stored
                it = items.get(a["id"])
                if it is None:
                    continue
                if (model, a["id"]) in seen:
                    raise SystemExit(f"refused: {model} answered {a['id']} twice")
                seen.add((model, a["id"]))
                ans = a.get("raw_text") or a["answer_text"]
                L, how = pick(final_answer(ans))
                p = it["products"].get(L, {}) if L else {}
                rows.append({"model": model, "id": a["id"], "request": it["request"], "kind": it["kind"],
                             "table": it["table"], "category": it["category"], "names": it["names"],
                             "paraphrase": it["paraphrase"], "designated": it["best"], "letter": L, "how": how,
                             "is_designated": int(L == it["best"]) if L else "",
                             "picked_shown_kind": p.get("kind", ""), "picked_true_kind": p.get("true_kind", ""),
                             "answer": ans})
    return items, rows


def pair_table(rows, needs=None):
    """{(model, request, table): {"hidden", "original", "crossed"} letters, with the designated letter}."""
    out = defaultdict(dict)
    for r in rows:
        k = (r["model"], r["request"], r["table"])
        out[k][r["names"]] = r["letter"]
        out[k]["designated"] = r["designated"]
        out[k]["kind"] = r["kind"]
        out[k]["category"] = r["category"]
    for k, v in out.items():
        des = v["designated"]
        ok = all(v.get(n) for n in ("hidden", "original"))
        v["penalty"] = (int(v["hidden"] == des) - int(v["original"] == des)) if ok else None
        v["premium"] = (int(v["crossed"] == des) - int(v["hidden"] == des)) if v.get("crossed") and v.get("hidden") else None
        nb = (needs or {}).get((k[1], k[2]))
        v["needs_best"] = nb or ""
        v["needs_penalty"] = (int(v["hidden"] == nb) - int(v["original"] == nb)) if ok and nb else None
        v["needs_is_designated"] = int(nb == des) if nb else ""
    return out


def author_gaps(build, models):
    """{(model, table): gap} on Study 1's strictly better tables (the analysis plan's secondary contrast 3): the share
    of answers that recommend the designated product with names hidden minus with the original names, information
    none and the equal-price rung, over its trials, read with Study 1's own loader (common/analyze.py)."""
    import analyze as L2   # Study 1's analysis script, read only
    _, rows, _ = L2.load(build, models, studies=("study1a-tables-with-one-optimal-product", "study2a-experience-attributes-stated-for-every-product"))
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if int(r["info"]) != 0 or int(r["rung"]) != 0 or not r["letter"]:
            continue
        c[(r["model"], r["table"], r["names"])][0] += 1
        c[(r["model"], r["table"], r["names"])][1] += int(r["is_best"])
    out = {}
    for (m, t, n), (k, b) in c.items():
        if n == "hidden" and c.get((m, t, "original"), [0])[0]:
            ko, bo = c[(m, t, "original")]
            out[(m, t)] = b / k - bo / ko
    return out


def mean_by_model(pairs, stat, weights=None, keep=lambda v: True):
    """Equal weight per pair within a model, equal weight per model: (pooled, {model: mean})."""
    num, den = defaultdict(float), defaultdict(float)
    for (m, req, t), v in pairs.items():
        if v.get(stat) is None or not keep(v):
            continue
        w = 1.0 if weights is None else weights(req, t)
        if w:
            num[m] += w * v[stat]
            den[m] += w
    per = {m: num[m] / den[m] for m in den if den[m]}
    return (sum(per.values()) / len(per) if per else None), per


def bootstrap(pairs, stat, draws, keep=lambda v: True, model=None):
    """95 per cent interval of the pooled mean (or one model's) from the two-way cluster bootstrap over requests and
    tables; also the share of draws at or below zero. A draw in which a model has no weight leaves that model out of
    the pooled mean of that draw, as mean_by_model does."""
    import numpy as np
    sel = [(k, v) for k, v in pairs.items() if v.get(stat) is not None and keep(v) and (model is None or k[0] == model)]
    reqs = sorted({k[1] for k, v in sel})
    tabs = sorted({k[2] for k, v in sel})
    mods = sorted({k[0] for k, v in sel})
    if len(reqs) < 3 or len(tabs) < 3:
        return None
    ri = np.array([reqs.index(k[1]) for k, v in sel])
    ti = np.array([tabs.index(k[2]) for k, v in sel])
    mi = np.array([mods.index(k[0]) for k, v in sel])
    x = np.array([float(v[stat]) for k, v in sel])
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(draws):
        wr = np.bincount(rng.integers(0, len(reqs), len(reqs)), minlength=len(reqs))
        wt = np.bincount(rng.integers(0, len(tabs), len(tabs)), minlength=len(tabs))
        w = wr[ri] * wt[ti]
        num = np.bincount(mi, weights=w * x, minlength=len(mods))
        den = np.bincount(mi, weights=w, minlength=len(mods))
        ok = den > 0
        if ok.any():
            vals.append(float(np.mean(num[ok] / den[ok])))
    if not vals:
        return None
    v = np.sort(np.array(vals))
    return {"low": float(np.quantile(v, 0.025)), "high": float(np.quantile(v, 0.975)),
            "share_at_or_below_zero": float(np.mean(v <= 0)),
            "p_two_sided": float(min(1.0, 2 * min(np.mean(v <= 0), np.mean(v >= 0)))), "draws": len(vals)}


def bootstrap_diff(pairs, stat, in_a, in_b, draws):
    """95 per cent interval and two-sided P of (pooled mean over pairs in group a) minus (pooled mean in group b), from
    the same two-way cluster bootstrap over requests and tables; in_a and in_b take (pair values, request id)."""
    import numpy as np
    sel = [(k, v) for k, v in pairs.items() if v.get(stat) is not None and (in_a(v, k[1]) or in_b(v, k[1]))]
    reqs = sorted({k[1] for k, v in sel})
    tabs = sorted({k[2] for k, v in sel})
    mods = sorted({k[0] for k, v in sel})
    if len(reqs) < 3 or len(tabs) < 3:
        return None
    ri = np.array([reqs.index(k[1]) for k, v in sel])
    ti = np.array([tabs.index(k[2]) for k, v in sel])
    mi = np.array([mods.index(k[0]) for k, v in sel])
    ga = np.array([bool(in_a(v, k[1])) for k, v in sel])
    x = np.array([float(v[stat]) for k, v in sel])
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(draws):
        wr = np.bincount(rng.integers(0, len(reqs), len(reqs)), minlength=len(reqs))
        wt = np.bincount(rng.integers(0, len(tabs), len(tabs)), minlength=len(tabs))
        w = wr[ri] * wt[ti]
        means = []
        for g in (ga, ~ga):
            num = np.bincount(mi[g], weights=(w * x)[g], minlength=len(mods))
            den = np.bincount(mi[g], weights=w[g], minlength=len(mods))
            ok = den > 0
            means.append(float(np.mean(num[ok] / den[ok])) if ok.any() else None)
        if None not in means:
            vals.append(means[0] - means[1])
    if not vals:
        return None
    v = np.sort(np.array(vals))
    return {"low": float(np.quantile(v, 0.025)), "high": float(np.quantile(v, 0.975)),
            "p_two_sided": float(min(1.0, 2 * min(np.mean(v <= 0), np.mean(v >= 0)))), "draws": len(vals)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--out")
    ap.add_argument("--all-models", action="store_true",
                    help="every model that answered: the GPT-6 models and the open models beside the Claude models")
    ap.add_argument("--leave-out", action="append", default=[],
                    help="a model left out of every estimate under the open-models rule (its parse counts are kept)")
    a = ap.parse_args()
    a.build, a.author_build = "requests", AUTHOR_SET
    a.open_answers = [CODEX, OPEN] if a.all_models else []
    a.needs, a.specificity = os.path.join(MAT, "needs_codes.jsonl.gz"), os.path.join(MAT, "specificity.jsonl.gz")
    out = a.out or (os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "requests", "all-models") if a.all_models
                    else os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "requests"))
    os.makedirs(out, exist_ok=True)
    items, rows = load(a.build, a.open_answers)
    all_hows = Counter((r["model"], r["how"]) for r in rows)    # every model's parse counts, those left out included
    left = sorted(set(a.leave_out) & {r["model"] for r in rows})
    # Study 2's rule: a model that has not answered every item of the build enters no estimate and is listed as incomplete
    answered = Counter(r["model"] for r in rows)
    incomplete = {m: f"{n} of {len(items)} items answered" for m, n in sorted(answered.items()) if n < len(items)}
    rows = [r for r in rows if r["model"] not in set(a.leave_out) | set(incomplete)]
    needs = {}
    if a.needs:   # the analysis plan's secondary contrast 5: the pairs where the needs coder names another product
        for l in gzip.open(a.needs, "rt", encoding="utf8"):
            x = json.loads(l)
            if x.get("opus_names_another_product"):
                needs[(x["request"], x["table"])] = x["opus"]
    spec = {}
    if a.specificity:
        for l in gzip.open(a.specificity, "rt", encoding="utf8"):
            x = json.loads(l)
            spec[x["request"]] = x["code"]
    pairs = pair_table(rows, needs)
    if a.author_build:
        ag = author_gaps(a.author_build, sorted({k[0] for k in pairs}))
        for (m, req, t), v in pairs.items():
            g = ag.get((m, t))
            v["author_gap"] = "" if g is None else g
            v["author_gap_num"] = g if v.get("penalty") is not None else None
            v["vs_author"] = None if g is None or v.get("penalty") is None else v["penalty"] - g
    chat = lambda v: v["kind"] == "chat-log"
    numbers = {"build": a.build, "answers": len(rows), "prompts": len(items),
               "parse": {f"{m} {h}": n for (m, h), n in sorted(all_hows.items())},
               "left_out": {m: {"rule": LEAVE_OUT_RULE,
                                "parse counts": {h: n for (mm, h), n in sorted(all_hows.items()) if mm == m}}
                            for m in left},
               "incomplete": incomplete,
               "pairs": len({(k[1], k[2]) for k in pairs}), "models": sorted({k[0] for k in pairs}),
               "bootstrap": {"draws": a.draws, "seed": SEED, "clusters": "requests and tables, resampled independently"}}
    for name, stat, keep in (("penalty, chat-log requests (primary)", "penalty", chat),
                             ("premium, chat-log requests", "premium", chat),
                             ("penalty, crowd-written and author-written requests", "penalty", lambda v: not chat(v)),
                             ("penalty, chat-log requests, without the pairs where the needs coder names another product",
                              "penalty", lambda v: chat(v) and not v["needs_best"]),
                             ("penalty under chat-log requests minus the author's request on the same model and table "
                              "(secondary contrast 3)", "vs_author", chat),
                             ("the author's request: Study 1's gap on the tables of the chat-log pairs, each weighted "
                              "by its pairs", "author_gap_num", chat)):
        est, per = mean_by_model(pairs, stat, keep=keep)
        if est is None:
            continue
        numbers[name] = {"pooled": est, "per_model": per,
                         "n_pairs_per_model": dict(Counter(k[0] for k, v in pairs.items() if v.get(stat) is not None and keep(v))),
                         "interval": bootstrap(pairs, stat, a.draws, keep=keep) if a.draws else None,
                         "per_model_interval": {m: bootstrap(pairs, stat, a.draws, keep=keep, model=m) for m in per} if a.draws else {}}
    shares = defaultdict(lambda: [0, 0])
    for (m, req, t), v in pairs.items():
        for n in ("hidden", "original", "crossed"):
            if v.get(n):
                shares[(m, n)][0] += 1
                shares[(m, n)][1] += int(v[n] == v["designated"])
    numbers["share picking the designated product"] = {f"{m} {n}": (b / c if c else None, c) for (m, n), (c, b) in sorted(shares.items())}
    if spec:
        by = {}
        for code in sorted(set(spec.values())):
            sel ={k: v for k, v in pairs.items() if spec.get(k[1]) == code}
            e, p = mean_by_model(sel, "penalty", keep=chat)
            by[str(code)] = {"pooled": e, "per_model": p, "n_pairs": len({(k[1], k[2]) for k, v in sel.items() if chat(v)})}
        numbers["penalty by specificity code, chat-log requests"] = by
        # secondary contrast 4: the gap for codes 2 and 3 minus the gap for codes 0 and 1
        hi = lambda v, r: chat(v) and spec.get(r) in (2, 3)
        lo = lambda v, r: chat(v) and spec.get(r) in (0, 1)
        e_hi = mean_by_model({k: v for k, v in pairs.items() if hi(v, k[1])}, "penalty")[0]
        e_lo = mean_by_model({k: v for k, v in pairs.items() if lo(v, k[1])}, "penalty")[0]
        numbers["penalty for specificity codes 2 and 3 minus codes 0 and 1, chat-log requests (secondary contrast 4)"] = {
            "pooled": e_hi - e_lo, "codes 2 and 3": e_hi, "codes 0 and 1": e_lo,
            "interval": bootstrap_diff(pairs, "penalty", hi, lo, a.draws) if a.draws else None}
    # Holm across the secondary family named in the analysis plan
    fam = {}
    for k, v in numbers.items():
        if not isinstance(v, dict) or "(primary)" in k or not v.get("interval"):
            continue
        if k.startswith("penalty, chat-log") or k.startswith("premium") or "secondary contrast" in k:
            fam[k] = v["interval"]["p_two_sided"]
    for m, iv in numbers.get("penalty, chat-log requests (primary)", {}).get("per_model_interval", {}).items():
        if iv:
            fam[f"penalty, chat-log requests, {m} (secondary contrast 1)"] = iv["p_two_sided"]
    order = sorted(fam, key=fam.get)
    holm, run = {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * fam[k]))
        holm[k] = {"p_two_sided": fam[k], "holm": run}
    numbers["Holm, the secondary family"] = holm
    with open(os.path.join(out, "answers.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != "answer"] if rows else ["id"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: v for k, v in r.items() if k != "answer"})
    with open(os.path.join(out, "pairs.csv"), "w", encoding="utf8", newline="") as f:
        cols = ["model", "request", "table", "kind", "category", "designated", "hidden", "original", "crossed",
                "penalty", "premium", "needs_best", "author_gap", "vs_author"]
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for (m, req, t), v in sorted(pairs.items()):
            w.writerow([m, req, t] + [v.get(c, "") for c in cols[3:]])
    with open(os.path.join(out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    print(json.dumps(numbers, indent=1))


if __name__ == "__main__":
    main()
