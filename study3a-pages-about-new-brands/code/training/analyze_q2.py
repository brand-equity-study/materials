"""Question 2 of the training study (the six kinds of planted page about the 14 product brands; the dose rule of the
plan's amendment 2): from the planted runs, each brand's E, W and components in each model and stage, then each kind
against the brands with no pages inside each model, over the models of one family.

    python study3a-pages-about-new-brands/code/training/analyze_q2.py --runs study3a-pages-about-new-brands/data/training-runs/olmo2-7b --stage dpo-uf --format role3 \
        --out study3a-pages-about-new-brands/results/training/parts/q2.json

A run's folder (study3a-pages-about-new-brands/data/training-runs/<family>/<run>/) holds corpus_stats.json (the plan: each brand's condition and
pages) and, for the stage, scores_<label>_<format>.csv.gz (Study 1a's strictly better tables),
scores_<label>_<format>_q2_items.jsonl.csv.gz (the planted tables) and components_<label>.jsonl.gz. The items are
study3a-pages-about-new-brands/materials/training-q2.
"""
import argparse
import csv
import glob
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package
MAT = os.path.join(PKG, "study3a-pages-about-new-brands", "materials", "training-q2")   # the planted tables, components and names
# the bootstrap's seed and draws, the interval, the P value and Holm's correction, as the training stages use them
_STAGES = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "code", "training_stages.py")
sys.path.insert(0, os.path.dirname(_STAGES))
import training_stages as an  # noqa: E402

KINDS = ("reliability", "praise", "expert", "advertising", "forum", "bare")
OUTCOMES = ("E", "W", "salience", "recognition", "quality", "credibility")
LETTERS = "ABCDE"


def _text(path):
    """A text file of the package, or its gzipped copy (<path>.gz)."""
    import gzip
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", encoding="utf-8")
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, encoding="utf-8")


def jl(path):
    return [json.loads(l) for l in _text(path) if l.strip()]


def probs(path):
    out = {}
    for r in csv.DictReader(_text(path)):
        out[r["id"]] = {L: float(r[f"p_{L}"]) for L in LETTERS}
    return out


def hidden_index(dom2_items):
    return {(it["table"], int(it["trial"]), int(it["info"]), int(it["rung"])): it["id"]
            for it in dom2_items if it["names"] == "hidden"}


def brand_tables(q2_items, dom2_items, dom2_p, q2_p):
    """{brand: {"E": {table: [diffs]}, "W": {...}}} in percentage points."""
    hid = hidden_index(dom2_items)
    out = {}
    for it in q2_items:
        p = q2_p.get(it["id"])
        h = dom2_p.get(hid[(it["table"], int(it["trial"]), int(it["info"]), int(it["rung"]))])
        if p is None or h is None:
            continue
        L = it["planted_letter"]
        key = "E" if it["where"] == "best" else "W"
        out.setdefault(it["planted"], {"E": {}, "W": {}})[key].setdefault(it["table"], []).append(100 * (p[L] - h[L]))
    return out


def component_tables(comp_items, rows, brands):
    """{brand: {outcome: {table or "_": [values]}}} for salience, recognition, quality and credibility."""
    by_id = {it["id"]: it for it in comp_items}
    val = {}
    for r in rows:
        val.setdefault(r["id"], []).append(r)
    out = {b: {"salience": {}, "recognition": {}, "quality": {}, "credibility": {}} for b in brands}
    hidden_rating = {}
    for iid, rs in val.items():
        it = by_id.get(iid)
        if it and it["measure"] in ("quality", "credibility") and it.get("names") == "hidden":
            hidden_rating[(it["measure"], it["table"], it.get("attribute", ""))] = rs[0]["value"]
    for iid, rs in val.items():
        it = by_id.get(iid)
        if not it:
            continue
        m = it["measure"]
        if m == "salience":
            for b in brands:
                if b in out and it["category"] == brands[b]:
                    named = any(re.search(r"(?<![\w])" + re.escape(b), r.get("text", "")) for r in rs)
                    out[b]["salience"].setdefault(it.get("table") or "_", []).append(100.0 * named)
        elif m == "recognition" and it.get("brand") in out:
            out[it["brand"]]["recognition"].setdefault("_", []).append(100.0 * (rs[0]["value"] or 0))
        elif m in ("quality", "credibility") and it.get("brand") in out:
            h = hidden_rating.get((m, it["table"], it.get("attribute", "")))
            if h is not None and rs[0]["value"] is not None:
                out[it["brand"]][m].setdefault(it["table"], []).append(rs[0]["value"] - h)
    return out


def load_run(folder, label, fmt, q2_items, dom2_items, comp_items, brand_category):
    plan = json.load(open(os.path.join(folder, "corpus_stats.json"), encoding="utf-8")).get("plan", {})
    dom2_p = probs(os.path.join(folder, f"scores_{label}_{fmt}.csv"))
    q2_p = probs(os.path.join(folder, f"scores_{label}_{fmt}_q2_items.jsonl.csv"))
    tabs = brand_tables(q2_items, dom2_items, dom2_p, q2_p)
    comp_path = os.path.join(folder, f"components_{label}.jsonl")
    comps = component_tables(comp_items, jl(comp_path), brand_category) if os.path.exists(comp_path) or os.path.exists(comp_path + ".gz") else {}
    return {"plan": plan, "tabs": tabs, "comps": comps}


def score(run, brand, outcome, tables=None):
    """The brand's mean over its items of the outcome. With resampled tables, the items of each drawn table count once a
    draw and the items that belong to no table ("_") are kept in every draw, so that the interval is about the same
    items as the estimate. Until about 5:25 PM on 22 November 2026 a draw dropped the items without a table whenever one of
    the brand's tables was drawn: salience's 140 open requests without a table (of 340) were in the estimate and not in
    its interval."""
    src = run["tabs"].get(brand, {}).get(outcome) if outcome in ("E", "W") else run["comps"].get(brand, {}).get(outcome)
    if not src:
        return None
    keys = sorted(src) if tables is None else [t for t in tables if t in src and t != "_"] + (["_"] if "_" in src else [])
    vals = [v for k in keys for v in src[k]]
    return sum(vals) / len(vals) if vals else None


def kind_contrast(run, kind, outcome, tables=None):
    """Mean of the kind's brands minus the mean of the brands with no pages, in one model."""
    holders = [b for b, v in run["plan"].items() if v["condition"] == kind]
    none = [b for b, v in run["plan"].items() if v["condition"] == "none"]
    a = [score(run, b, outcome, tables) for b in holders]
    z = [score(run, b, outcome, tables) for b in none]
    a, z = [x for x in a if x is not None], [x for x in z if x is not None]
    if not a or not z:
        return None
    return sum(a) / len(a) - sum(z) / len(z)


def pair_contrast(run, a, b, outcome, tables=None):
    """Mean of kind a's brands minus the mean of kind b's brands, in one model (the training study's plan change 40)."""
    s = lambda k: [x for x in (score(run, br, outcome, tables) for br, v in run["plan"].items()
                               if v["condition"] == k) if x is not None]
    xa, xb = s(a), s(b)
    if not xa or not xb:
        return None
    return sum(xa) / len(xa) - sum(xb) / len(xb)


# change 40: bare mentions against general praise and against expert reviews, Holm across the two, for each outcome
PAIRS = (("bare", "praise"), ("bare", "expert"))


def dose_parts(run, kind, outcome, tables=None):
    """(rise from 0 to 80 pages, rise from 80 to 320 pages) in one model."""
    lo = [b for b, v in run["plan"].items() if v["condition"] == kind and v["pages"] == 80]
    hi = [b for b, v in run["plan"].items() if v["condition"] == kind and v["pages"] == 320]
    none = [b for b, v in run["plan"].items() if v["condition"] == "none"]
    s = lambda bs: [x for x in (score(run, b, outcome, tables) for b in bs) if x is not None]
    l, h, z = s(lo), s(hi), s(none)
    if not l or not h or not z:
        return None
    m = lambda xs: sum(xs) / len(xs)
    return m(l) - m(z), m(h) - m(l)


def run_label(folder, fmt, stage, items_file):
    """The label of the one run in a folder whose planted-table scores end with -<stage>: train.py names its files
    scores_<run name>-<stage>_<format>_<items file>.csv (review 1, findings 1 and 2)."""
    suffix = f"_{fmt}_{items_file}.csv.gz"
    labs = [os.path.basename(p)[len("scores_"):-len(suffix)] for p in glob.glob(os.path.join(folder, f"scores_*{suffix}"))]
    labs = [l for l in labs if l.endswith("-" + stage)]
    if len(labs) != 1:
        raise SystemExit(f"refused: {folder} holds {len(labs)} runs scored at {stage} in {fmt}")
    return labs[0]


def stratum(table):
    """A table's category: its name without the number, as sr_laptops_01_dom gives sr_laptops; a name without a
    category's number falls in one common stratum."""
    m = re.match(r"^(.*)_\d+(_dom)?$", table)
    return m.group(1) if m else "_"


def strata_draw(rng, tables):
    """Tables drawn with replacement within each category, so that no draw loses every table of a brand's category and
    with it the brand (the training study's plan change 14; review 1, finding 14)."""
    groups = {}
    for t in sorted(tables):
        groups.setdefault(stratum(t), []).append(t)
    return [g[rng.randrange(len(g))] for _, g in sorted(groups.items()) for _ in g]


def boot_mean(runs, fn, draws, tables, seed=an.BOOT_SEED):
    """The mean over models of fn(run, tables), with a two-way bootstrap: models with replacement, and one draw of the
    tables, within each category, shared by the models of a draw."""
    est_vals = [fn(r, None) for r in runs]
    est_vals = [x for x in est_vals if x is not None]
    est = sum(est_vals) / len(est_vals) if est_vals else float("nan")
    rng = random.Random(seed)
    ts = sorted(tables)
    bs = []
    for _ in range(draws):
        rs = [runs[rng.randrange(len(runs))] for _ in runs]
        tt = strata_draw(rng, ts)
        v = [x for x in (fn(r, tt) for r in rs) if x is not None]
        if v:
            bs.append(sum(v) / len(v))
    return {"estimate": est, "ci95": an.interval(bs), "p_two_sided": an.two_sided(bs), "models": len(est_vals)}


def dose_pattern(a, b):
    """the training study's plan amendment 2's rule on the two rises' intervals."""
    up = lambda c: c["ci95"][0] > 0
    if up(a) and up(b):
        return "gradual rise"
    if up(a) and b["ci95"][0] <= 0 <= b["ci95"][1]:
        return "saturation by 80 pages"
    if a["ci95"][0] <= 0 <= a["ci95"][1] and up(b):
        return "threshold above 80 pages"
    if not up(a) and not up(b):
        return "no rise"
    return "other"


def analyze(runs, draws=an.DRAWS):
    tables = sorted({t for r in runs for b in r["tabs"].values() for t in b.get("E", {})})
    res = {"models": len(runs), "draws": draws, "kinds": {}, "pairs": {}, "dose": {}}
    for out in OUTCOMES:
        rows = {}
        for k in KINDS:
            rows[k] = boot_mean(runs, lambda r, tt, k=k, out=out: kind_contrast(r, k, out, tt), draws, tables)
        for k, p in zip(KINDS, an.holm([rows[k]["p_two_sided"] for k in KINDS])):
            rows[k]["p_holm"] = p
        res["kinds"][out] = rows
        pr = {}
        for a, b in PAIRS:
            pr[f"{a}_minus_{b}"] = boot_mean(runs, lambda r, tt, a=a, b=b, out=out: pair_contrast(r, a, b, out, tt),
                                             draws, tables)
        for k, p in zip(list(pr), an.holm([v["p_two_sided"] for v in pr.values()])):
            pr[k]["p_holm"] = p
        res["pairs"][out] = pr
        dz = {}
        for k in KINDS:
            a = boot_mean(runs, lambda r, tt, k=k, out=out: (dose_parts(r, k, out, tt) or (None, None))[0], draws, tables)
            b = boot_mean(runs, lambda r, tt, k=k, out=out: (dose_parts(r, k, out, tt) or (None, None))[1], draws, tables)
            dz[k] = {"0_to_80": a, "80_to_320": b, "pattern": dose_pattern(a, b)}
        res["dose"][out] = dz
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--stage", default="dpo-uf")
    ap.add_argument("--format", default="role3")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    q2 = jl(os.path.join(MAT, "q2_items.jsonl"))
    comp = jl(os.path.join(MAT, "q2_components.jsonl"))
    dom2 = jl(os.path.join(PKG, "study1a-tables-with-one-optimal-product", "materials", "strictly-better-tables", "prompts.jsonl.gz"))
    names = json.load(open(os.path.join(MAT, "names.json"), encoding="utf-8"))
    cat = {b: c for c, pair in names["brands"].items() for b in pair}
    runs = []
    for folder in a.runs:
        for stats in sorted(glob.glob(os.path.join(folder, "**", "corpus_stats.json"), recursive=True)):
            d = os.path.dirname(stats)
            labels = [os.path.basename(p)[len("scores_"):-len(f"_{a.format}_q2_items.jsonl.csv.gz")]
                      for p in glob.glob(os.path.join(d, f"scores_*_{a.format}_q2_items.jsonl.csv.gz"))]
            for lab in labels:
                if lab.endswith("-" + a.stage):
                    runs.append(load_run(d, lab, a.format, q2, dom2, comp, cat))
    res = analyze(runs)
    res.update({"stage": a.stage, "format": a.format})
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    main()
