"""The item sets that the edited and unedited models answer in PLAN.md amendment 4 (question 7).

    python jmr-2026/mechanism/weights_items.py --out <folder>          (the three table sets, on a desktop computer)
    python weights_items.py --mmlu <mmlu500.jsonl> --out <folder>      (the MMLU set, inside the job, from mmlu500.jsonl)

  s1.jsonl        Study 1's prompts as rerun on the open panel (jmr-2026/study1-rerun/items/s1rerun1): the names-shown
                  arm and the names-hidden arm with the leaked brand texts removed (hidden_clean); 1,360 items
  dom2.jsonl      Study 2's strictly better build, the original and names-hidden cells; 2,400 items
  requests.jsonl  the drawn chat-log requests of the request bank, paired with their dominant sets by the bank's renderer
                  (jmr-2026/requests/build_requests.py), the original and names-hidden arms
  mmlu.jsonl      500 MMLU questions (cais/mmlu, test, seed 20261121), each with its four choices as A to D
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
S1 = os.path.join(ROOT, "jmr-2026", "study1-rerun", "items", "s1rerun1", "items.jsonl")
DOM2 = os.path.join(ROOT, "jmr-2026", "study2", "items", "dom2", "items.jsonl")
MMLU_SYSTEM = ("Answer the multiple-choice question. Your very first line must contain ONLY the letter of the correct "
               "choice (A, B, C, or D) -- nothing else.")


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf8") if l.strip()]


def s1_items():
    return [dict(i, set="s1") for i in jl(S1) if i["cell"] in ("shown", "hidden_clean")]


def dom2_items():
    return [dict(i, set="dom2") for i in jl(DOM2) if i["names"] in ("original", "hidden")]


def request_items():
    sys.path.insert(0, os.path.join(ROOT, "jmr-2026", "requests"))
    import build_requests as BR
    bank = [r for r in BR.load_bank() if r.get("kind") == "chat-log" and r.get("in_run")]
    tables = BR.load_sets()
    items = BR.render_all(bank, tables, "b6w")
    return [dict(i, set="requests") for i in items if i["names"] in ("original", "hidden")]


def mmlu_items(path):
    out = []
    for q in jl(path):
        choices = "\n".join(f"{'ABCD'[k]}. {c}" for k, c in enumerate(q["choices"]))
        out.append({"id": hashlib.sha1(f"b6w-mmlu|{q['i']}".encode()).hexdigest()[:16], "set": "mmlu", "i": q["i"],
                    "subject": q["subject"], "best": "ABCD"[q["answer"]], "system": MMLU_SYSTEM,
                    "user": f"{q['question']}\n\n{choices}\n\nWhich choice is correct?"})
    return out


def write(path, items):
    with open(path, "w", encoding="utf8", newline="\n") as f:
        for i in items:
            f.write(json.dumps(i, ensure_ascii=False) + "\n")
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mmlu", default="")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    rec = {}
    sets = {"mmlu": mmlu_items(a.mmlu)} if a.mmlu else {"s1": s1_items(), "dom2": dom2_items(), "requests": request_items()}
    for name, items in sets.items():
        if len({i["id"] for i in items}) != len(items):
            sys.exit(f"refused: {name} has repeated item ids")
        rec[name] = {"items": len(items), "sha256": write(os.path.join(a.out, f"{name}.jsonl"), items),
                     "cells": dict(Counter(i.get("cell", i.get("names", "")) for i in items))}
    json.dump(rec, open(os.path.join(a.out, "ITEMS.json" if not a.mmlu else "ITEMS_MMLU.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    main()
