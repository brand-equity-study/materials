"""The main estimates again without the three tables whose fictitious name is also the name of a small real company:
Novatech (laptops 2), Primebook (laptops 3) and Sonance (earbuds 2).

The estimates are those that the paper reports in percentage points from the studies whose tables include these
three: Study 1b (the gap pooled over every model, the penalty under consumers' own requests, the gap under weighted
stated priorities, and the gap when the model may ask a clarifying question), Study 1c (the store's name gap in the
plain listing and under the instruction "Do not consider brand reputation.", the change under that instruction and
under "Recommend only on the information listed.", the change when every product's experience attributes were stated,
and the search step's first two primary contrasts), Study 2a (the gap with no experience attributes stated, with
every product's experience attributes stated, and its change) and Study 2b (the familiar product's share of the
picks of either product at the same price, and the fictitious product's share minus the familiar product's with names
shown). Study 2b's price discount at which the fictitious product is chosen as often as the familiar product is
computed the same way and reported apart, in percent of the price. Study 2b's measure uses its own categories and
fictitious names, so the three tables do not enter it.

For each estimate the script first computes the reported value with that study's own code and data, as the study's
script does, and stops unless it equals the value in the study's results file. It then computes the same estimate on
the same models, with the same code and the same bootstrap, without the rows of the three tables and of their strictly
better versions (the table identifiers in LEFT_OUT). Each study runs in its own process, so that two studies' modules
of the same name do not mix.

    python study1a-tables-with-one-optimal-product/code/21_real_company_tables.py
Writes study1a-tables-with-one-optimal-product/results/real-company-tables/numbers.json.
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import argparse
import importlib.util
import json
import math
import os
import subprocess
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # the package
OUT = os.path.join(ROOT, "study1a-tables-with-one-optimal-product", "results", "real-company-tables")
COMPANIES = {"sr_laptops_02": "Novatech", "sr_laptops_03": "Primebook", "sr_earbuds_02": "Sonance"}
LEFT_OUT = sorted([*COMPANIES, *(t + "_dom" for t in COMPANIES)])
MARK = "@@ESTIMATES@@"


def module(path):
    """A study's script, loaded from its file (its own main() is not run)."""
    name = "m_" + os.path.splitext(os.path.basename(path))[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def results(path, keys):
    """A value of a study's results file, by its keys."""
    node = json.load(open(path, encoding="utf8"))
    for k in keys:
        node = node[k]
    return node


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def same(a, b):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    return a == b


def record(label, path, keys, published, reproduced, without):
    """One estimate: the reported value, this script's reproduction of it, and the value without the three tables, each
    in percentage points. Stops when the reproduction differs from the reported value."""
    for k in ("points", "ci95", "p_two_sided"):
        if not same(published.get(k), reproduced.get(k)):
            raise SystemExit(f"refused: {label}: {k} is {published.get(k)} in {rel(path)} and {reproduced.get(k)} here")
    if without["tables"] >= reproduced["tables"]:
        raise SystemExit(f"refused: {label}: no table was left out ({reproduced['tables']} tables before and after)")
    return label, {"source": f"{rel(path)}: {'/'.join(keys)}", "published": published,
                   "reproduced": {k: reproduced[k] for k in ("points", "ci95", "p_two_sided", "models", "tables")},
                   "without_three_tables": without,
                   "change_points": round(without["points"] - published["points"], 4)}


def pp(x):
    return None if x is None else round(100 * x, 4)


# ---------------------------------------------------------------- Study 1b

def study1b_pooled():
    P = module(os.path.join(ROOT, "study1b-64-models-on-34-tables", "code", "16_pooled.py"))
    import pandas as pd
    corpus, _ = P.corpus_rows()
    items, rerun = P.rerun_rows()
    opened, lettered = P.open_rows()
    rule_out = P.open_models_rule(lettered)
    opened = opened[~opened.model_key.isin(rule_out)]
    left, _ = P.checks(corpus, rerun, opened, items)
    left.update(rule_out)
    cols = ["model_key", "assortment_id", "condition", "non_optimal"]
    df = pd.concat([corpus[cols], rerun[cols], opened[cols]])
    df = df[~df.model_key.isin(left) & ~df.model_key.isin(P.SAME_WEIGHTS)]

    def run(d):
        e = P.pooled(d, P.cc.DRAWS)[3]
        return {"points": e["gap_pp"], "ci95": e["ci95_pp"], "p_two_sided": e["p_two_sided"], "models": e["models"],
                "tables": e["tables"]}
    path = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "pooled", "numbers.json")
    pub = results(path, ["pooled"])
    return [record("Study 1b: the brand gap over every model", path, ["pooled", "gap_pp"],
                   {"points": pub["gap_pp"], "ci95": pub["ci95_pp"], "p_two_sided": pub["p_two_sided"]},
                   run(df), run(df[~df.assortment_id.isin(LEFT_OUT)]))]


def study1b_requests():
    Q = module(os.path.join(ROOT, "study1b-64-models-on-34-tables", "code", "14_requests.py"))
    path = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "requests", "all-models", "numbers.json")
    key = "penalty, chat-log requests (primary)"
    published_run = json.load(open(path, encoding="utf8"))
    items, rows = Q.load("requests", [Q.CODEX, Q.OPEN])
    answered = Counter(r["model"] for r in rows)
    incomplete = {m for m, n in answered.items() if n < len(items)}
    if incomplete != set(published_run["incomplete"]):
        raise SystemExit(f"refused: the requests' incomplete models are {sorted(incomplete)} here and "
                         f"{sorted(published_run['incomplete'])} in {rel(path)}")
    rows = [r for r in rows if r["model"] not in set(published_run["left_out"]) | incomplete]
    pairs = Q.pair_table(rows)
    chat = lambda v: v["kind"] == "chat-log"   # noqa: E731

    def run(pp_):
        est, per = Q.mean_by_model(pp_, "penalty", keep=chat)
        iv = Q.bootstrap(pp_, "penalty", 10000, keep=chat)
        return {"points": pp(est), "ci95": [pp(iv["low"]), pp(iv["high"])], "p_two_sided": iv["p_two_sided"],
                "models": len(per), "tables": len({k[2] for k, v in pp_.items() if v.get("penalty") is not None and chat(v)})}
    pub = published_run[key]
    return [record("Study 1b: the penalty under consumers' own requests (chat-log requests)", path, [key, "pooled"],
                   {"points": pp(pub["pooled"]), "ci95": [pp(pub["interval"]["low"]), pp(pub["interval"]["high"])],
                    "p_two_sided": pub["interval"]["p_two_sided"]},
                   run(pairs), run({k: v for k, v in pairs.items() if k[2] not in LEFT_OUT}))]


def study1b_priorities():
    S = module(os.path.join(ROOT, "study1b-64-models-on-34-tables", "code", "19_priorities.py"))
    items = {r["id"]: r for r in S._gz(S.ITEMS)}
    recs, _ = S.read_sources()
    frecs, _ = S.read_folder_answers(items)
    d = S.frame(recs + frecs, items)
    counts = d.groupby("model_key").size()
    full_open = [m for m in sorted(d[d.route == "open_models"].model_key.unique()) if counts[m] == len(items)]
    folder_models = sorted(d[d.route != "open_models"].model_key.unique())
    full = full_open + [m for m in folder_models if counts[m] == len(items)]
    left = S.below_read_rule(d.groupby("model_key").parsed.sum().to_dict(), counts)
    dd = d[d.model_key.isin([m for m in full if m not in left]) & (d.parsed == 1)]
    x = dd[dd.condition == "preference_weighted"]

    def run(y):
        g = S.G.gaps(y, "hidden")["pooled"]
        return {"points": g["gap_pp"], "ci95": g["ci95_models_and_tables_resampled"],
                "p_two_sided": g["p_two_sided_models_and_tables_resampled"], "models": g["models"], "tables": g["tables"]}
    path = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "priorities", "numbers.json")
    keys = ["all_models", "gap_names_hidden", "preference_weighted", "pooled"]
    pub = results(path, keys)
    return [record("Study 1b: the gap under weighted stated priorities", path, keys + ["gap_pp"],
                   {"points": pub["gap_pp"], "ci95": pub["ci95_models_and_tables_resampled"],
                    "p_two_sided": pub["p_two_sided_models_and_tables_resampled"]},
                   run(x), run(x[~x.assortment_id.isin(LEFT_OUT)]))]


def study1b_clarifying():
    C = module(os.path.join(ROOT, "study1b-64-models-on-34-tables", "code", "18_clarifying.py"))
    items = {r["id"]: r for r in C._gz(C.ITEMS)}
    orows, _ = C.open_clarify(items)
    frows, _ = C.folder_clarify(items)
    clar = C.frame(orows + frows, items)
    routes = {r: sorted(g.model.unique()) for r, g in clar.groupby("route")}
    one = C.frame(C.one_turn(items, routes).to_dict(orient="records"), items)
    out_models = set(C.read_rule(clar, len(items))) | set(C.read_rule(one, len(items)))
    c = clar[~clar.model.isin(out_models) & (clar.parsed == 1)]
    o = one[~one.model.isin(out_models) & (one.parsed == 1)]

    def run(c_, o_):
        r = C.compare(c_, o_)
        return {"points": r["gap_with_the_option_to_ask_pp"], "ci95": r["ci95"], "p_two_sided": r["p_two_sided"],
                "models": r["models"], "tables": r["tables"]}
    path = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "clarifying", "numbers.json")
    pub = results(path, ["all_models"])
    return [record("Study 1b: the gap when the model may ask a clarifying question", path,
                   ["all_models", "gap_with_the_option_to_ask_pp"],
                   {"points": pub["gap_with_the_option_to_ask_pp"], "ci95": pub["ci95"], "p_two_sided": pub["p_two_sided"]},
                   run(c, o), run(c[~c.assortment_id.isin(LEFT_OUT)], o[~o.assortment_id.isin(LEFT_OUT)]))]


# ---------------------------------------------------------------- Study 1c

STORE_ESTIMATES = [("name gap g(arm)", "plain", "the name gap in the plain listing"),
                   ("name gap g(arm)", "instruct-brand",
                    "the name gap under the instruction not to consider brand reputation"),
                   ("change D(arm) = g(arm) - g(plain)", "instruct-brand",
                    "the change under the instruction not to consider brand reputation"),
                   ("change D(arm) = g(arm) - g(plain)", "instruct-listed",
                    "the change under the instruction to recommend only on the information listed"),
                   ("change D(arm) = g(arm) - g(plain)", "plain-info",
                    "the change when every product's experience attributes were stated")]


def interval_of(e):
    iv = e["interval"]
    return {"points": pp(e["pooled"]), "ci95": [pp(iv["low95"]), pp(iv["high95"])], "p_two_sided": iv["p_two_sided"]}


def study1c_store():
    AH = module(os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "code", "store", "analyze_harness.py"))
    path = os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "results", "store", "all-models", "numbers.json")
    pub = json.load(open(path, encoding="utf8"))
    cells = [os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "results", "store", "claude", "cells.csv"),
             os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "results", "store", "open-all", "cells.csv")]
    c = AH.cells_from(cells)
    left = set(AH.inherited_left_out(cells, list(pub["left_out"]), {k[0] for k in c})) | set(pub["left_out"])
    c = {k: v for k, v in c.items() if k[0] not in left}
    cw = {k: v for k, v in c.items() if k[1] not in LEFT_OUT}
    out = []
    for kind, arm, label in STORE_ESTIMATES:
        fn = AH.gap(arm) if kind.startswith("name gap") else AH.change(arm)

        def run(cc_):
            vals = AH.per_mt(cc_, fn)
            return {**interval_of(AH.estimate(vals, 10000)), "models": len({m for m, t in vals}),
                    "tables": len({t for m, t in vals})}
        out.append(record(f"Study 1c: {label}", path, [kind, arm, "pooled"], interval_of(pub[kind][arm]), run(c), run(cw)))
    return out


def study1c_search():
    AH = module(os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "code", "store", "analyze_harness.py"))
    path = os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "results", "search", "all-models", "numbers.json")
    pub = json.load(open(path, encoding="utf8"))
    rows = [json.loads(line) for line in
            open(os.path.join(ROOT, "study1c-product-feeds-and-a-store-search", "results", "search", "all-models", "second_prompts.jsonl"), encoding="utf8")]

    def contrasts(rs):
        """The share of second prompts in which the store returned the best product, and the share whose answer picks
        it, for each model and table, names hidden minus names shown (analyze_search.py's primary 1 and 2)."""
        cell = defaultdict(lambda: defaultdict(list))
        for r in rs:
            cell[(r["model"], r["table"])][r["names"]].append(r)
        fetched, picked = defaultdict(dict), defaultdict(dict)
        for (m, t), g in cell.items():
            for names, group in g.items():
                fetched[names][(m, t)] = sum(r["fetched"] for r in group) / len(group)
                got = [r for r in group if r["picked_best"] is not None]
                if got:
                    picked[names][(m, t)] = sum(r["picked_best"] for r in got) / len(got)
        diff = lambda h, o: {k: h[k] - o[k] for k in h if k in o}   # noqa: E731
        return {"fetched: hidden minus shown (primary 1)": diff(fetched["hidden"], fetched["original"]),
                "picked the best: hidden minus shown (primary 2)": diff(picked["hidden"], picked["original"])}
    a, b = contrasts(rows), contrasts([r for r in rows if r["table"] not in LEFT_OUT])
    labels = {"fetched: hidden minus shown (primary 1)": "the search step: the store returned the best product, names "
                                                        "hidden minus shown",
              "picked the best: hidden minus shown (primary 2)": "the search step: the answer picked the best product, "
                                                                 "names hidden minus shown"}
    out = []
    for key, label in labels.items():
        def run(vals):
            return {**interval_of(AH.estimate(vals, 10000)), "models": len({m for m, t in vals}),
                    "tables": len({t for m, t in vals})}
        out.append(record(f"Study 1c: {label}", path, [key, "pooled"], interval_of(pub[key]), run(a[key]), run(b[key])))
    return out


# ---------------------------------------------------------------- Studies 2a and 2b

def counts_rows(PA):
    return PA.read_counts([os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product", "data", "counts", "counts-git.csv"),
                           os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product", "data", "open-panel", "b9-counts.csv")])


def summary_of(s, scale=True):
    f = pp if scale else (lambda x: x)
    return {"points": f(s["estimate"]), "ci95": [f(s["ci95"][0]), f(s["ci95"][1])], "p_two_sided": s["p_two_sided"]}


def study2a():
    PA = module(os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product", "code", "pool_all.py"))
    rows = counts_rows(PA)
    ok = {m for m, v in PA.screen(rows, "dom2").items() if v["verdict"] == "in"}
    a = PA.AN.primary_report(PA.con_of(rows, "dom2", ok), PA.DRAWS)
    rw = [r for r in rows if r["table"] not in LEFT_OUT]
    b = PA.AN.primary_report(PA.con_of(rw, "dom2", ok), PA.DRAWS)
    tables = lambda rs: len({r["table"] for r in rs if r["build"] == "dom2" and r["model"] in ok})   # noqa: E731
    path = os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product", "results", "all-models", "numbers.json")
    out = []
    for key, label in (("gap_none", "the gap with no experience attributes stated"),
                       ("gap_supplied", "the gap with every product's experience attributes stated"),
                       ("change", "the change in the gap when every product's experience attributes were stated")):
        pub = results(path, ["2a", "pooled", key])
        out.append(record(f"Study 2a: {label}", path, ["2a", "pooled", key, "estimate"], summary_of(pub),
                          {**summary_of(a[key]), "models": len(ok), "tables": tables(rows)},
                          {**summary_of(b[key]), "models": len(ok), "tables": tables(rw)}))
    return out


def study2b():
    PA = module(os.path.join(ROOT, "study2a-experience-attributes-stated-for-every-product", "code", "pool_all.py"))
    rows = counts_rows(PA)
    ok = sorted(m for m, v in PA.screen(rows, "eq1").items() if v["verdict"] == "in")
    items = PA.OB.load_items("eq1")
    rw = [r for r in rows if r["table"] not in LEFT_OUT]
    items_w = {k: v for k, v in items.items() if v["table"] not in LEFT_OUT}
    tables = lambda its: len({v["table"] for v in its.values()})   # noqa: E731
    path = os.path.join(ROOT, "study2b-how-much-a-familiar-brand-is-worth", "results", "all-models-eq1", "numbers.json")
    test = "invented minus familiar twin, names shown"
    keys = ["2c", "pooled", "pooled", "option_a_parity_tests", test]
    e_all = PA.OB.eq_part(rows, set(ok), items)["pooled"]
    e_wo = PA.OB.eq_part(rw, set(ok), items_w)["pooled"]
    fam_keys = ["2c", PA.FAM_KEY, "names shown", "all"]
    fam = lambda rs: PA.familiar_share(rs, ok, PA.DRAWS)["names shown"]["all"]   # noqa: E731
    cross_keys = ["2c", "pooled", "pooled", "option_a_without_a_model", "price", "original"]
    cross = lambda e: {"percent_of_the_price": e["option_a_without_a_model"]["price"]["original"]["crossing_value"],   # noqa: E731
                       "ci95": e["option_a_without_a_model"]["price"]["original"]["crossing_ci95"]}
    return [record("Study 2b: the fictitious product's share minus the familiar product's at the same price, names shown",
                   path, keys + ["estimate"], summary_of(results(path, keys)),
                   {**summary_of(e_all["option_a_parity_tests"][test]), "models": len(ok), "tables": tables(items)},
                   {**summary_of(e_wo["option_a_parity_tests"][test]), "models": len(ok), "tables": tables(items_w)}),
            record("Study 2b: the familiar product's share of the picks of either product at the same price, names shown",
                   path, fam_keys + ["estimate"], summary_of(results(path, fam_keys)),
                   {**summary_of(fam(rows)), "models": len(ok), "tables": tables(items)},
                   {**summary_of(fam(rw)), "models": len(ok), "tables": tables(items_w)}),
            record_price("Study 2b: the price discount at which the fictitious product is chosen as often as the familiar "
                         "product, names shown", path, cross_keys + ["crossing_value"], results(path, cross_keys),
                         cross(e_all), cross(e_wo), tables(items), tables(items_w))]


def record_price(label, path, keys, pub, reproduced, without, n_all, n_without):
    """Study 2b's price discount, in percent of the price (not in points, so it is reported apart from the estimates
    in points). Stops when the reproduction differs from the reported value."""
    published = {"percent_of_the_price": pub["crossing_value"], "ci95": pub["crossing_ci95"]}
    for k in published:
        if not same(published[k], reproduced[k]):
            raise SystemExit(f"refused: {label}: {k} is {published[k]} in {rel(path)} and {reproduced[k]} here")
    if n_without >= n_all:
        raise SystemExit(f"refused: {label}: no table was left out")
    return label, {"source": f"{rel(path)}: {'/'.join(keys)}", "unit": "percent of the price",
                   "reported": published, "without_the_three_tables": {**without, "tables": n_without},
                   "tables_reported": n_all}


PARTS = {"study1b_pooled": study1b_pooled, "study1b_requests": study1b_requests, "study1b_priorities": study1b_priorities,
         "study1b_clarifying": study1b_clarifying, "study1c_store": study1c_store, "study1c_search": study1c_search,
         "study2a": study2a, "study2b": study2b}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", choices=sorted(PARTS), help="one study's estimates, printed (each runs in its own process)")
    a = ap.parse_args()
    if a.one:
        print(MARK + json.dumps(PARTS[a.one]()))
        return 0
    estimates, other = {}, {}
    for name in PARTS:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", name], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        line = [x for x in r.stdout.splitlines() if x.startswith(MARK)]
        if r.returncode != 0 or not line:
            raise SystemExit(f"{name} stopped:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}")
        for label, rec in json.loads(line[-1][len(MARK):]):
            if "unit" in rec:   # an estimate in another unit than points
                other[label] = rec
                print(f"{label}: {rec['reported']} -> {rec['without_the_three_tables']}", flush=True)
                continue
            estimates[label] = rec
            print(f"{label}: {rec['published']['points']} -> {rec['without_three_tables']['points']} "
                  f"(change {rec['change_points']})", flush=True)
    excl = lambda ci: ci[0] > 0 or ci[1] < 0   # noqa: E731
    flips = [k for k, v in estimates.items() if excl(v["published"]["ci95"]) != excl(v["without_three_tables"]["ci95"])]
    numbers = {"about": "Each estimate that the paper reports in percentage points from Studies 1b, 1c, 2a and 2b, "
                        "with every table and without the three tables whose fictitious name is also the name of a small "
                        "real company; each was first reproduced from its study's code and results file.",
               "companies": {t: n for t, n in COMPANIES.items()}, "tables_left_out": LEFT_OUT,
               "estimates": estimates, "estimates_count": len(estimates),
               "largest_change_points": max(abs(v["change_points"]) for v in estimates.values()),
               "intervals_that_changed_whether_they_exclude_zero": flips,
               "estimates_in_other_units": other}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
        f.write("\n")
    print(f"{len(estimates)} estimates; the largest change is {numbers['largest_change_points']} points; intervals that "
          f"changed whether they exclude zero: {flips or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
