"""Write the declines into a study's numbers.json files: for every model, the answers that are picks, declines and
unread, and the decline share by arm and name version (the definition: decline.py).

    python common/write_declines.py --study b16 --kind study1c-product-feeds-and-a-store-search/data/store/open-letters-kind.csv.gz \
        --items study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz --items study1c-product-feeds-and-a-store-search/materials/store/h2/prompts.jsonl.gz \
        --local "study1c-product-feeds-and-a-store-search/data/store/claude/*.jsonl.gz" --numbers study1c-product-feeds-and-a-store-search/results/store/claude/numbers.json ...

The open models' kinds come from the computing cluster's export, which ran decline.classify on each raw answer without a
letter. The answers in this package, given with --local, are read here the same way: pick(final_answer(text)), and
decline.classify on the final answer when pick reads no letter. Each numbers.json gets, for the models that it names
(its models, its parse block and its left_out):
- in its parse block, when it has one, '<model> decline': the number of that model's answers without a letter that are
  declines (the parser's own counts stay as they are);
- a block 'declines': the source and its SHA-256, and for each model its answers, picks, declines and unread, and the
  decline share by arm and name version, with the mean of the models' shares by arm and name version.
"""
import argparse
import csv
import glob
import gzip
import hashlib
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))   # the package
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "common"))   # parse_answer.py
import decline as D  # noqa: E402
from parse_answer import final_answer, pick  # noqa: E402


def load_items(paths):
    out = {}
    for pattern in paths:
        for p in glob.glob(pattern):
            for line in gzip.open(p, "rt", encoding="utf8"):
                it = json.loads(line)
                out[it["id"]] = (it.get("arm") or "search", it.get("names", ""))
    return out


def kinds_from_export(path, study):
    out = []
    for r in csv.DictReader(gzip.open(path, "rt", encoding="utf8")):
        if r["study"] == study:
            out.append((r["model"], r["id"], r["kind"]))
    return out


def kinds_from_local(patterns, models):
    """(model, id, kind) for the answers in this package (one jsonl.gz file per model, with model and answer_text)."""
    out = []
    for pattern in patterns:
        for f in sorted(glob.glob(pattern)):
            for line in gzip.open(f, "rt", encoding="utf8"):
                r = json.loads(line)
                if r["model"] not in models:
                    continue
                text = final_answer(r["answer_text"])
                L, _ = pick(text)
                out.append((r["model"], r["id"], "pick" if L else D.classify(text)))
    return out


def block(kinds, items, models, pooled_over=None):
    """Per model counts and shares for every named model (those left out included); the mean of the shares over
    pooled_over (the record's estimated models), or over every named model when it is None."""
    per = defaultdict(lambda: {"answers": 0, "pick": 0, "decline": 0, "unread": 0})
    cell = defaultdict(lambda: [0, 0])
    for m, iid, k in kinds:
        if m not in models or iid not in items:
            continue
        per[m]["answers"] += 1
        per[m][k] += 1
        arm, names = items[iid]
        cell[(m, arm, names)][0] += 1
        cell[(m, arm, names)][1] += int(k == "decline")
    by = defaultdict(dict)
    for (m, arm, names), (n, d) in sorted(cell.items()):
        by[m].setdefault(arm, {})[names] = {"answers": n, "declines": d, "share": round(d / n, 6)}
    pooled = defaultdict(dict)
    for arm, names in sorted({(a, n) for (_, a, n) in cell}):
        shares = [by[m][arm][names]["share"] for m in by if names in by[m].get(arm, {})
                  and (pooled_over is None or m in pooled_over)]
        pooled[arm][names] = round(sum(shares) / len(shares), 6) if shares else None
    return {m: per[m] for m in sorted(per)}, {m: by[m] for m in sorted(by)}, pooled


def write(path, kinds, items, source):
    n = json.load(open(path, encoding="utf8"))
    names = set(n.get("models") or []) | set((n.get("left_out") or {}).keys())
    if isinstance(n.get("parse"), dict):
        names |= {k.rsplit(" ", 1)[0] for k in n["parse"]}
    per, by, pooled = block(kinds, items, names, set(n.get("models") or []) or None)
    if isinstance(n.get("parse"), dict):
        for m, c in per.items():
            no_letter = n["parse"].get(f"{m} none", 0) + n["parse"].get(f"{m} several", 0)
            if any(k.startswith(m + " ") and not k.endswith(" decline") for k in n["parse"]) and c["decline"] > no_letter:
                raise SystemExit(f"refused: {path}: {m} has {c['decline']} declines but only {no_letter} answers "
                                 "without a letter in its parse block (the export and the panel do not match)")
            n["parse"][f"{m} decline"] = c["decline"]
    n["declines"] = {"definition": "common/decline.py",
                     "source": source, "by model": per, "share by arm and name version": by,
                     "mean of the models' shares by arm and name version": pooled,
                     "mean over": "the record's estimated models (its models), not those left out"}
    with open(path, "w", encoding="utf8", newline="\n") as f:
        json.dump(n, f, indent=1)
    print(f"{os.path.relpath(path, ROOT)}: {len(per)} models, {sum(c['decline'] for c in per.values())} declines")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", required=True, help="b10, b16 or b17, as in the export's study column")
    ap.add_argument("--kind", help="the export's letters with the kind column (csv.gz)")
    ap.add_argument("--kind-name", help="the export's path in the repository, recorded as the source (when --kind is a "
                                        "copy of it outside the working tree)")
    ap.add_argument("--items", action="append", required=True)
    ap.add_argument("--local", action="append", default=[], help="a glob of this package's answer files (.jsonl.gz)")
    ap.add_argument("--numbers", action="append", required=True)
    a = ap.parse_args()
    items = load_items(a.items)
    kinds = kinds_from_export(a.kind, a.study) if a.kind else []
    source = {"export": a.kind_name or (os.path.relpath(a.kind, ROOT).replace("\\", "/") if a.kind else None),
              "export_sha256": hashlib.sha256(open(a.kind, "rb").read()).hexdigest() if a.kind else None,
              "local answers": a.local}
    models_all = set()
    for p in a.numbers:
        n = json.load(open(p, encoding="utf8"))
        models_all |= set(n.get("models") or []) | set((n.get("left_out") or {}).keys())
    kinds += kinds_from_local(a.local, models_all)
    for p in a.numbers:
        write(p, kinds, items, source)


if __name__ == "__main__":
    main()
