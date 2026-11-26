"""Which of a model's audit units are answered in full, in one item set. The runs of the GPT models through Codex
stopped part way, so a GPT model enters each measure on every brand whose items for that measure it answered in full,
with the counts stated in the Web Appendix.

A unit is the set of items that one score is computed from, inside one item set (full1-fable or full1-fable-rest,
study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/item_sets.csv):
  salience, default          the category's lists (one score per brand comes from the same lists)
  consideration              the category's real requests
  quality                    a named listing (table, product, label, name), over every attribute, wording and trial,
                             together with the names-hidden listing of the same table and product IN THE SAME ITEM SET,
                             because its premium is the named rating minus the hidden one
  credibility                a named (table, name) at one price kind, with the names-hidden item of the same table and
                             price kind in the same item set
  typicality, recognition, description, country, rating
                             the brand in its category
A unit is complete when every one of its items has an answer that the run kept (an answer for which Codex ran a tool is
left out, as score.py does, so it makes its unit incomplete). Unreadable answers are counted, not dropped.

    python study3b-brand-knowledge-and-training-text-in-released-models/code/audit/completeness.py --models gpt-6.2-sol,gpt-6.1-sol      (prints the table; read-only)
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package's top folder
MAT = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "materials", "audit")   # the items, the reference set, the brand counts
DATA = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "data", "audit")   # the answers, the tone codes, the open letters
STUDY1 = os.path.join(PKG, "study1a-tables-with-one-optimal-product")   # Study 1a's original tables, their answers and the parser
BUILDS = ("full1-fable", "full1-fable-rest")


def unit_key(it):
    """The unit an item belongs to (without its item set); a names-hidden item's key has label 'hidden'."""
    m = it["measure"]
    if m in ("salience", "default", "consideration"):
        return (m, it["category"])
    if m == "quality":
        return (m, it["table"], it["product"], it["label"], it.get("brand") or "")
    if m == "credibility":
        return (m, it["price_kind"], it["table"], it.get("brand") or "")
    return (m, it.get("brand") or "", it["category"])


def hidden_key(key):
    """The names-hidden unit that a named quality or credibility unit is differenced against, or None."""
    if key[0] == "quality" and key[3] != "hidden":
        return ("quality", key[1], key[2], "hidden", "")
    if key[0] == "credibility" and key[3] != "":
        return ("credibility", key[1], key[2], "")
    return None


def kept_answers(build, model):
    """The item ids of a model's answers in one item set (study3b-brand-knowledge-and-training-text-in-released-models/data/audit/codex/<model>-<item set>.jsonl.gz), less the
    answers for which Codex ran a tool."""
    import gzip
    ids, tooled = set(), set()
    path = os.path.join(DATA, "codex", f"{model}-{build}.jsonl.gz")
    if os.path.exists(path):
        for line in gzip.open(path, "rt", encoding="utf8"):
            x = json.loads(line)
            ids.add(x["id"])
            if x.get("tool_items"):
                tooled.add(x["id"])
    return ids - tooled


def items_of(build):
    """The items of one item set: the audit's items (study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz) that
    study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/item_sets.csv places in it."""
    import csv
    import gzip
    want = {r["id"] for r in csv.DictReader(open(os.path.join(MAT, "item_sets.csv"), encoding="utf8"))
            if r["item_set"] == build}
    return [it for it in (json.loads(l) for l in gzip.open(os.path.join(MAT, "items.jsonl.gz"), "rt", encoding="utf8"))
            if it["id"] in want]


def complete_units(items, answered):
    """{unit: (items, answered)} over one item set, and the set of units that count: complete, and, for a named
    quality or credibility unit, with its names-hidden unit complete in the same item set."""
    n, a = Counter(), Counter()
    for it in items:
        k = unit_key(it)
        n[k] += 1
        a[k] += it["id"] in answered
    done = {k for k in n if a[k] == n[k]}
    counts = {k for k in done if hidden_key(k) is None or hidden_key(k) in done}
    return {k: (n[k], a[k]) for k in n}, counts


def keep_ids(model, measures_by_build):
    """The item ids of a model to score: for each item set, the items of the measures named for it
    (measures_by_build[build]) whose unit counts. Returns (ids, table) where table counts the units by item set and
    measure: {build: {measure: {"units": n, "complete": k}}}."""
    keep, table = set(), {}
    for b in BUILDS:
        items = items_of(b)
        ans = kept_answers(b, model)
        units, counts = complete_units(items, ans)
        tb = table.setdefault(b, {})
        for k in units:
            if k[0] == "quality" and k[3] == "hidden" or k[0] == "credibility" and k[3] == "":
                continue  # a baseline is counted through the named units that use it
            e = tb.setdefault(k[0], {"units": 0, "complete": 0})
            e["units"] += 1
            e["complete"] += k in counts
        wanted = set(measures_by_build.get(b, ()))
        for it in items:
            # a names-hidden unit counts when it is complete itself, so its items are kept with the named ones
            if it["measure"] in wanted and unit_key(it) in counts:
                keep.add(it["id"])
    return keep, table


# The composition for the GPT models through Codex, which stopped part way: one for each
# model and measure. Inferred quality, credibility, salience (the recall lists) and consideration (the real requests)
# come from full1-fable alone, as for Fable 5.1's subset; the tone (from the descriptions), recognition and typicality
# from full1-fable-rest. Each enters on its complete units only.
CODEX_MEASURES = {"full1-fable": ("quality", "credibility", "salience", "consideration"),
                  "full1-fable-rest": ("description", "recognition", "typicality")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    a = ap.parse_args()
    for m in a.models.split(","):
        for b in BUILDS:
            items = items_of(b)
            ans = kept_answers(b, m)
            units, counts = complete_units(items, ans)
            by = defaultdict(lambda: [0, 0, 0, 0])
            for it in items:
                by[it["measure"]][0] += 1
                by[it["measure"]][1] += it["id"] in ans
            for k in units:
                if k[0] == "quality" and k[3] == "hidden" or k[0] == "credibility" and k[3] == "":
                    continue
                by[k[0]][2] += 1
                by[k[0]][3] += k in counts
            for meas, (ni, na, nu, nc) in sorted(by.items()):
                print(f"{m:12s} {b:17s} {meas:13s} items {na:5d}/{ni:5d}   units complete {nc:4d}/{nu:4d}")


if __name__ == "__main__":
    main()
