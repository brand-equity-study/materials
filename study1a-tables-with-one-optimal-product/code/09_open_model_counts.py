"""Count the answers of the models with open weights: for every set, model, table, cell and price rung, the number of
answers, the number from which the parser read a letter, and the number that picked the best product.

Reads study1a-tables-with-one-optimal-product/data/open-models/<set>/<model>/<cell>.jsonl.gz and writes study1a-tables-with-one-optimal-product/results/open_models_counts.csv, one row per
key, sorted by key, which 10_open_models.py and 11_open_models_robustness.py read. The letter is read again here with
the parser of Study 1 (common/parse_answer.py) from each answer's text.

    python study1a-tables-with-one-optimal-product/code/09_open_model_counts.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import gzip
import json
import pathlib
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[2]  # the top of the replication package
sys.path.append(str(REPO / "common"))
sys.dont_write_bytecode = True
from parse_answer import pick  # noqa: E402

DATA = REPO / "study1a-tables-with-one-optimal-product" / "data" / "open-models"
OUT = REPO / "study1a-tables-with-one-optimal-product" / "results" / "open_models_counts.csv"


def main() -> int:
    counts = defaultdict(lambda: [0, 0, 0])
    for f in sorted(DATA.glob("*/*/*.jsonl.gz")):
        set_name, folder = f.parent.parent.name, f.parent.name
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                key = (set_name, r.get("model", folder), r["table"], r["cell"], r.get("names", ""), r.get("info", ""),
                       r.get("rung", ""), r["best"])
                letter = pick(r["answer_text"])[0]
                c = counts[key]
                c[0] += 1
                c[1] += 1 if letter else 0
                c[2] += 1 if letter == r["best"] else 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["set", "model", "table", "cell", "names", "info", "rung", "best", "answers", "parsed", "best_picked"])
        for k in sorted(counts):
            w.writerow(list(k) + counts[k])
    print(f"{len(counts)} rows, {sum(c[0] for c in counts.values())} answers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
