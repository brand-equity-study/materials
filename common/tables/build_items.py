"""Render the controlled test's prompts, run the refusing gates, and write the item files only when every gate passes.

    python common/tables/build_items.py --dominant --tables all --trials 10 --build dom2 --out <folder>
    python common/tables/build_items.py --tables all --trials 10 --build full2 --out <folder>
    python common/tables/build_items.py --check --dominant --tables all --trials 1   (gates only; writes nothing)

dom2 is the strictly better tables (study1a-tables-with-one-optimal-product/materials/strictly-better-tables/prompts.jsonl.gz) and full2 the original
tables (study1a-tables-with-one-optimal-product/materials/original-tables/prompts.jsonl.gz); each deposited file is items.jsonl without its build
label. Writes <folder>/<build>/: items.jsonl (every prompt with its cell and the meaning of each letter), p0.jsonl
to p3.jsonl with system_p0.txt to system_p3.txt (one batch per system prompt; each line {"id", "text"}), GATES.json
(the gate results, each table's dominance verdict and every change made for dominance) and SHA256SUMS.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gates  # noqa: E402
import tables as S  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--tables", required=True)
    ap.add_argument("--trials", type=int, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", help="the folder that receives <build>/")
    ap.add_argument("--dominant", action="store_true", help="the dominant sets (dominant_sets.py), rungs 0 and 2")
    ap.add_argument("--split", action="store_true", help="the information split: seven versions, rung 0")
    a = ap.parse_args()
    tables = S.load_tables()
    rungs = S.RUNGS
    infos = S.INFOS
    changes = {}
    if a.dominant:
        import dominant_sets as D
        tables, key = D.build(tables)
        gates.KEY.update(key)
        rungs = (0, 2)
        changes = {t: [list(c) for c in v["changes"]] for t, v in tables.items()}
    if a.split:
        rungs = (0,)
        infos = (0,) + S.SPLIT_ARMS + (1,)
    ids = list(tables) if a.tables == "all" else [t + ("_dom" if a.dominant and not t.endswith("_dom") else "") for t in a.tables.split(",")]
    items = S.render_all(tables, ids, a.trials, a.build or "check", rungs, infos)
    res = gates.run_gates(items, tables)
    verdicts = gates.verdicts(items)
    for tid in ids:
        v, reasons = verdicts[tid]
        print(f"{tid:30s} {v:17s} {'; '.join(reasons[:2])}")
    print(f"\n{len(items)} prompts; cells {len(Counter(i['cell'] for i in items))}; "
          f"dominant tables {sum(v[0] == 'dominant' for v in verdicts.values())} of {len(ids)}")
    bad = {k: v for k, v in res.items() if v}
    for k, v in res.items():
        print(f"gate {k}: {'PASS' if not v else f'REFUSED ({len(v)})'}")
        for f in v[:12]:
            print("   ", f)
    if bad:
        sys.exit(1)
    if a.check:
        return
    if not a.build:
        sys.exit("--build is required to write items")
    if not a.out:
        sys.exit("--out is required to write items")
    out = os.path.join(a.out, a.build)
    if os.path.exists(os.path.join(out, "items.jsonl")):
        sys.exit(f"{out} already holds a build; choose a new --build name")
    os.makedirs(out, exist_ok=True)
    files = []
    with open(os.path.join(out, "items.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    files.append("items.jsonl")
    for k in range(4):
        sysfile = f"system_p{k}.txt"
        with open(os.path.join(out, sysfile), "w", encoding="utf8", newline="\n") as f:
            f.write(S.SYSTEM_BASELINE_PARAPHRASES[k])
        with open(os.path.join(out, f"p{k}.jsonl"), "w", encoding="utf8", newline="\n") as f:
            for it in items:
                if it["paraphrase"] == k:
                    f.write(json.dumps({"id": it["id"], "text": it["user"]}, ensure_ascii=False) + "\n")
        files += [sysfile, f"p{k}.jsonl"]
    report = {"build": a.build, "tables": ids, "trials": a.trials, "prompts": len(items),
              "cells": sorted(Counter(i["cell"] for i in items)), "gates": {k: "pass" for k in res},
              "dominance": {t: {"verdict": v[0], "reasons": v[1]} for t, v in verdicts.items()},
              "changes_for_dominance": {t: changes[t] for t in ids if t in changes}}
    with open(os.path.join(out, "GATES.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    files.append("GATES.json")
    with open(os.path.join(out, "SHA256SUMS"), "w", encoding="utf8", newline="\n") as f:
        for fn in files:
            f.write(f"{hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest()}  {fn}\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
