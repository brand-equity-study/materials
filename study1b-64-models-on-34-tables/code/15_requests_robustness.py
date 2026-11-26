"""Study 1, consumers' own shopping requests: the robustness lines of the analysis plan, reported without tests. The
name gap under chat-log requests (point estimates, every model weighted equally) by source set, without the requests
that the classifier marked as naming a brand, by category, and with only the answers whose letter was on the first line.

    python study1b-64-models-on-34-tables/code/15_requests_robustness.py   reads study1b-64-models-on-34-tables/results/requests/pairs.csv and answers.csv (written by
                                                   14_requests.py) and writes robustness.json beside them
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import argparse
import csv
import gzip
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # the top of the replication package
RES = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "requests")
BANK = os.path.join(ROOT, "study1b-64-models-on-34-tables", "materials", "requests", "requests.jsonl.gz")


def pooled(rows):
    by = defaultdict(list)
    for r in rows:
        if r["penalty"] != "":
            by[r["model"]].append(float(r["penalty"]))
    per = {m: sum(x) / len(x) for m, x in by.items() if x}
    return (sum(per.values()) / len(per) if per else None), per, len({(r["request"], r["table"]) for r in rows if r["penalty"] != ""})


def main():
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    bank = {json.loads(l)["id"]: json.loads(l) for l in gzip.open(BANK, "rt", encoding="utf8")}
    rows = [r for r in csv.DictReader(open(os.path.join(RES, "pairs.csv"), encoding="utf8")) if r["kind"] == "chat-log"]
    ans = list(csv.DictReader(open(os.path.join(RES, "answers.csv"), encoding="utf8")))
    first = {(r["model"], r["request"], r["table"], r["names"]): r["how"] == "first-line" for r in ans}
    out = {}

    def put(name, sel):
        e, per, n = pooled(sel)
        out[name] = {"pooled": e, "per_model": per, "pairs": n}

    put("all chat-log pairs", rows)
    for src in sorted({bank[r["request"]]["source"] for r in rows}):
        put(f"source: {src}", [r for r in rows if bank[r["request"]]["source"] == src])
    put("WildChat-4.8M alone", [r for r in rows if bank[r["request"]]["source"] == "WildChat-4.8M"])
    put("the three LMArena sets", [r for r in rows if bank[r["request"]]["source"].startswith("LMArena")])
    put("without requests that the classifier marked as naming a brand",
        [r for r in rows if bank[r["request"]]["names_brand_classifier"] != "yes"])
    for cat in sorted({r["category"] for r in rows}):
        put(f"category: {cat}", [r for r in rows if r["category"] == cat])
    put("only answers with the letter on the first line",
        [r for r in rows if first.get((r["model"], r["request"], r["table"], "hidden")) and
         first.get((r["model"], r["request"], r["table"], "original"))])
    path = os.path.join(RES, "robustness.json")
    with open(path, "w", encoding="utf8", newline="\n") as f:
        json.dump(out, f, indent=1)
    for k, v in out.items():
        print(f"{k:70s} {v['pooled'] * 100 if v['pooled'] is not None else float('nan'):6.1f}  pairs {v['pairs']}")


if __name__ == "__main__":
    main()
