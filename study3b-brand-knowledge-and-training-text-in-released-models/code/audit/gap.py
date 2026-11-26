"""Each product's own-name gap on Study 1a's original tables, the outcome of the audit's tests: for each model,
table and product under a name, the share of answers that pick it with the names shown minus with the names hidden
(and, for the swapped names, the same on the crossed tables), from the Claude models' answers
(study1a-tables-with-one-optimal-product/data/original-tables/) and from the open models' letters (study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz).
"""
import glob
import json
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package's top folder
MAT = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "materials", "audit")   # the items, the reference set, the brand counts
DATA = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "data", "audit")   # the answers, the tone codes, the open letters
STUDY1 = os.path.join(PKG, "study1a-tables-with-one-optimal-product")   # Study 1a's original tables, their answers and the parser
sys.path.insert(0, os.path.join(PKG, "common"))   # parse_answer.py
from parse_answer import pick  # noqa: E402

TOOL_EXCLUDED = {}   # {(build, model): answers left out because Codex ran a tool for them}


def load_answers(build, models=None, extra=None):
    """{model: {item id: answer text}}: the Claude models' answers to Study 1a's original tables
    (study1a-tables-with-one-optimal-product/data/original-tables/<model>/<cell>.jsonl.gz), and the GPT models' through Codex
    (study3b-brand-knowledge-and-training-text-in-released-models/data/audit/codex-original-tables/<model>.jsonl.gz), less the answers for which Codex ran a tool (counted in
    TOOL_EXCLUDED). extra is kept from the project's signature."""
    import gzip
    out = {}
    for mdir in sorted(glob.glob(os.path.join(STUDY1, "data", "original-tables", "*"))):
        m = os.path.basename(mdir)
        if not os.path.isdir(mdir) or (models and m not in models):
            continue
        d = out.setdefault(m, {})
        for f in sorted(glob.glob(os.path.join(mdir, "*.jsonl.gz"))):
            for line in gzip.open(f, "rt", encoding="utf8"):
                x = json.loads(line)
                d[x["id"]] = x["answer_text"]
    for path in sorted(glob.glob(os.path.join(DATA, "codex-original-tables", "*.jsonl.gz"))):
        m = os.path.basename(path)[:-len(".jsonl.gz")]
        if models and m not in models:
            continue
        d = out.setdefault(m, {})
        for line in gzip.open(path, "rt", encoding="utf8"):
            x = json.loads(line)
            if x.get("tool_items"):
                TOOL_EXCLUDED[(build, m)] = TOOL_EXCLUDED.get((build, m), 0) + 1
                continue
            d[x["id"]] = x["answer_text"]
    return out


OUT = os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "data", "open-panel")
EXPORT_BUILD = {"full2": "b2/full2", "s1rerun1": "study1-rerun/s1rerun1"}


def letter_files():
    """The open models' letters on Study 1a's original tables (study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz), from which
    every letter of the audit's results was taken."""
    return [os.path.join(PKG, "study2a-experience-attributes-stated-for-every-product", "data", "open-panel", "letters-12683.csv.gz")]


SOURCES_USED = {}   # {build: {export file: letters taken from it in the end}}, for the record of which export was used


def load_letters(build, paths=None):
    """{model: {item id: letter}} for the open models, from the open models' letters (Study 2's parse_answer.pick,
    run on the computing cluster; an empty letter is an unread answer). A build is matched by its name in the export's build
    column (for example "b2/full2" or "full2"). SOURCES_USED[build] counts, for each file, the letters that it gave in
    the end (after later files replaced earlier ones)."""
    import csv
    import gzip
    out, src = {}, {}
    names = {EXPORT_BUILD[build], build}
    for path in (paths or letter_files()):
        for row in csv.DictReader(gzip.open(path, "rt", encoding="utf8")):
            if row["build"] in names or row["build"].endswith("/" + build):
                out.setdefault(row["model"], {})[row["id"]] = row["letter"]
                src[(row["model"], row["id"])] = os.path.relpath(path, OUT)
    from collections import Counter
    SOURCES_USED[build] = dict(Counter(src.values()))
    return out


def picks(items, answers, letters=None):
    """{(model, table, trial, rung, names): {orig letter: 1 or 0}} for every parsed answer (information none); answers
    are texts read with pick, letters are letters read already."""
    out = {}
    flat = [(m, iid, pick(text)[0]) for m, ans in answers.items() for iid, text in ans.items()]
    flat += [(m, iid, L) for m, d in (letters or {}).items() for iid, L in d.items()]
    for m, iid, L in flat:
        if True:
            it = items.get(iid)
            if not it or it.get("info", 0) != 0:
                continue
            if not L or L not in it["products"]:
                continue
            chosen = it["products"][L]["orig"]
            out[(m, it["table"], it["trial"], it.get("rung", 0), it["names"])] = {
                p["orig"]: int(p["orig"] == chosen) for p in it["products"].values()}
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def gaps(build="full2", models=None, extra=None, items_path=None, open_panel=False):
    """open_panel: the open models' letters from job 11815 instead of the Claude answers' texts."""
    import gzip
    items_path = items_path or os.path.join(STUDY1, "materials", "original-tables", "prompts.jsonl.gz")
    items = {}
    for line in gzip.open(items_path, "rt", encoding="utf8"):
        it = json.loads(line)
        items[it["id"]] = it
    if open_panel:
        letters = {m: d for m, d in load_letters(build).items() if not models or m in models}
        P = picks(items, {}, letters)
    else:
        P = picks(items, load_answers(build, models, extra))
    named_cell, hidden_cell = ("original", "hidden") if build == "full2" else ("shown", "hidden_clean")
    # the products of each table, and the partner of each crossed trial, from the items themselves
    meta = {}
    for it in items.values():
        t = meta.setdefault(it["table"], {"brand": {}, "kind": {}, "best": None, "partner": {}})
        for p in it["products"].values():
            t["brand"][p["orig"]] = p["true_brand"]
            t["kind"][p["orig"]] = p["true_kind"]
        t["best"] = it["products"][it["best"]]["orig"]
        if it["names"] == "crossed":
            t["partner"][it["trial"]] = it["partner_orig"]
    rows = []
    for m in sorted({k[0] for k in P}):
        for tid, t in sorted(meta.items()):
            keys = sorted({(k[2], k[3]) for k in P if k[0] == m and k[1] == tid})
            pairs = defaultdict(list)    # (product, label, name) -> [(trial, named - hidden, hidden)]
            for trial, rung in keys:
                h = P.get((m, tid, trial, rung, hidden_cell))
                o = P.get((m, tid, trial, rung, named_cell))
                if h and o:
                    for p in t["brand"]:
                        pairs[(p, "own", t["brand"][p])].append((trial, o[p] - h[p], h[p]))
                x = P.get((m, tid, trial, rung, "crossed"))
                if h and x and trial in t["partner"]:
                    f, b = t["partner"][trial], t["best"]
                    pairs[(b, "swap", t["brand"][f])].append((trial, x[b] - h[b], h[b]))
                    pairs[(f, "swap", t["brand"][b])].append((trial, x[f] - h[f], h[f]))
            for (p, label, name), v in sorted(pairs.items()):
                kind = next(t["kind"][q] for q in t["brand"] if t["brand"][q] == name)
                rows.append({"model": m, "table": tid, "product": p, "product_brand": t["brand"][p], "name": name,
                             "name_kind": kind, "label": label, "n_pairs": len(v),
                             "gap": 100 * _mean([d for _, d, _ in v]),
                             "s_hidden": 100 * _mean([hh for _, _, hh in v]),
                             "s_named": 100 * _mean([d + hh for _, d, hh in v]),
                             "half_a": _pct(_mean([d for k, d, _ in v if k <= 4])),
                             "half_b": _pct(_mean([d for k, d, _ in v if k >= 5]))})
    return rows


def _pct(x):
    return None if x is None else 100 * x

