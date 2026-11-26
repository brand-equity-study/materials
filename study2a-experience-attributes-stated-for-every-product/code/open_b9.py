"""Each piece alone (split1) and the price (eq1) on the open panel, from the counts that were written on the computing
cluster from the open models' answers (study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv).

The estimates are those of the Claude runs, from the same functions: analyze.contrasts and analyze.split_report for each
piece alone, and analyze_eq.report_counts and analyze_eq.assemble for the price. A model whose answers the parser reads
in under 90 per cent of a build's items, or that picks the best product in under 10 per cent of the names-hidden items
(each piece alone's, and option B's for the price), is reported apart as unable to do the task; a model that has not
answered every item of a build is listed as incomplete and enters no estimate. pool_all.py uses load_items, screen,
eq_part and typed from here.

    python study2a-experience-attributes-stated-for-every-product/code/open_b9.py <counts.csv> <out folder> [--panel ten|all|<comma-separated keys>]
"""
import argparse
import csv
import gzip
import json
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))  # analyze.py and parse_answer.py
sys.path.insert(0, os.path.join(HERE, "..", "..", "web-appendix-analyses/each-piece-of-information-alone", "code"))  # analyze_attr.py, attr_conditions.py
sys.path.insert(0, os.path.join(HERE, "..", "..", "study2b-how-much-a-familiar-brand-is-worth", "code"))  # analyze_eq.py
import analyze as AN  # noqa: E402  (read only)
import analyze_eq as Q  # noqa: E402  (read only)

TEN = ["llama8b", "qwen32b", "qwen3-30b", "gemma31b", "gemma4-26b", "olmo31-32b", "ministral3-14b", "phi4",
       "granite41-30b", "marin8b"]                      # the first open panel of ten models
N_ITEMS = {"split1": 6300, "eq1": 10560}
DRAWS = 2000


def typed(v):
    return int(v) if v.lstrip("-").isdigit() else v


SET_FOLDER = {"strictly-better-tables": "study1a-tables-with-one-optimal-product", "each-piece-alone": "web-appendix-analyses/each-piece-of-information-alone", "price": "study2b-how-much-a-familiar-brand-is-worth", "further-information": "web-appendix-analyses/each-piece-of-information-alone"}
SETS = {"dom2": "strictly-better-tables", "split1": "each-piece-alone", "eq1": "price", "attr1": "further-information"}  # build code -> the package's set of prompts


def load_items(build):
    out = {}
    with gzip.open(os.path.join(HERE, "..", "..", SET_FOLDER[SETS[build]], "materials", SETS[build], "prompts.jsonl.gz"),
                   "rt", encoding="utf8") as fh:
        lines = fh.read().split("\n")
    for line in (l for l in lines if l):
        it = json.loads(line)
        it["budget_low"], it["budget_high"], it["outside_budget"] = AN.budget(it)
        out[it["id"]] = it
    return out


def read_counts(path):
    rows = list(csv.DictReader(open(path, encoding="utf8")))
    for r in rows:
        for k in ("answers", "parsed", "picked_best", "picked_partner"):
            r[k] = int(r[k])
    return rows


def screen(rows, build):
    """{model: {"answers", "parsed_share", "best_share_hidden", "verdict"}} by the open-models plan's rules."""
    by = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        if r["build"] != build:
            continue
        b = by[r["model"]]
        b[0] += r["answers"]
        b[1] += r["parsed"]
        if r["names"] == "hidden" and (build == "split1" or r["rung"].startswith("B-")):
            b[2] += r["parsed"]
            b[3] += r["picked_best"]
    out = {}
    for m, (n, p, hp, hb) in sorted(by.items()):
        ps, bs = p / n if n else 0, hb / hp if hp else 0
        verdict = ("incomplete" if n < N_ITEMS[build] else "unable: parsed under 90 per cent" if ps < 0.9
                   else "unable: picks the best product in under 10 per cent with names hidden" if bs < 0.1 else "in")
        out[m] = {"answers": n, "parsed_share": round(ps, 4), "best_share_hidden": round(bs, 4), "verdict": verdict}
    return out


def split_part(rows, models, items):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["build"] == "split1" and r["model"] in models:
            k = (r["model"], r["table"], r["names"], typed(r["info"]), typed(r["rung"]))
            c[k][0] += r["parsed"]
            c[k][1] += r["picked_best"]
    con = AN.contrasts(c)
    below = {(it["table"], it["rung"]) for it in items.values() if it["outside_budget"] == "below"}
    out = {"split": AN.split_report(con, DRAWS)}
    for label, drop in (("invented-real", lambda t, g: t in Q.INVENTED_REAL), ("thin", lambda t, g: t in Q.THIN),
                        ("below-range", lambda t, g: (t, g) in below)):
        out[f"split_without_{label}"] = AN.split_report({k: v for k, v in con.items() if not drop(k[1], k[3])}, DRAWS)
    return out


def eq_part(rows, models, items):
    def counts(kind=None):
        pc, bc = defaultdict(lambda: [0, 0, 0, 0]), defaultdict(lambda: [0, 0])
        for r in rows:
            if r["build"] != "eq1" or r["model"] not in models:
                continue
            opt, g = r["rung"][0], r["rung"][2:]
            k = (r["model"], r["table"], r["names"], g)
            if opt == "A":
                if kind is not None and r["partner_kind"] != kind:
                    continue
                v = pc[k]
                v[0] += r["picked_best"]
                v[1] += r["picked_partner"]
                v[2] += r["parsed"] - r["picked_best"] - r["picked_partner"]
                v[3] += r["parsed"]
            else:
                bc[k][0] += r["picked_best"]
                bc[k][1] += r["parsed"]
        return dict(pc), dict(bc)

    cache = {}

    def make(ms, tables, keep=None, fixed_models=False, kind=None):
        if kind not in cache:
            cache[kind] = counts(kind)
        pc, bc = cache[kind]
        return Q.report_counts(pc, bc, ms, tables, keep, fixed_models)

    tables = sorted({it["table"] for it in items.values()})
    return Q.assemble(make, sorted(models), tables, Q.below_range_keep(items.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("counts")
    ap.add_argument("out")
    ap.add_argument("--panel", action="append", default=[],
                    help="ten, all, or comma-separated model keys (repeatable; default: ten and all)")
    a = ap.parse_args()
    rows = read_counts(a.counts)
    res = {"source": {"script": "study2a-experience-attributes-stated-for-every-product/code/open_b9.py", "counts": a.counts,
                      "plan": "study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 8"}}
    for build, part in (("split1", split_part), ("eq1", eq_part)):
        items = load_items(build)
        sc = screen(rows, build)
        res[f"{build}_models"] = sc
        ok = {m for m, v in sc.items() if v["verdict"] == "in"}
        for panel in a.panel or ["ten", "all"]:
            ms = sorted(ok & set(TEN)) if panel == "ten" else sorted(ok) if panel == "all" else sorted(ok & set(panel.split(",")))
            if not ms:
                res[f"{build}_{panel}"] = {"models": [], "note": "no model of this panel has answered every item"}
                continue
            res[f"{build}_{panel}"] = {"models": ms, **part(rows, set(ms), items)}
            print(f"{build} {panel}: {len(ms)} models")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"wrote {os.path.join(a.out, 'numbers.json')}")


if __name__ == "__main__":
    main()
