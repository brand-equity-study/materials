"""Check that the counts which Study 2's estimates read are the counts of the answers in this package. count_git.py
counts every answer of the strictly better tables, each piece alone and the price, with the open panel's letters, and
for each build and model the rows must equal those of study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv; it counts the answers of the
attribute build the same way against study2a-experience-attributes-stated-for-every-product/data/counts/counts-git-attr1.csv. A model whose run was still going when
the counts were taken (some GPT-6 models on each piece alone) has no complete set of answers in this package; its rows
are reported, not compared.

    python study2a-experience-attributes-stated-for-every-product/code/check_counts.py      writes study2a-experience-attributes-stated-for-every-product/results/counts_check.json
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
LETTERS = os.path.join(STUDY, "data", "open-panel", "letters-12683.csv.gz")
CHECKS = [  # (builds, the counts file that the estimates read, count_git.py's further options)
    ("dom2,split1,eq1", os.path.join(STUDY, "data", "counts", "counts-git.csv"),
     ["--letters", LETTERS, "--letters-build", "b2/dom2"]),
    ("attr1", os.path.join(STUDY, "data", "counts", "counts-git-attr1.csv"), []),
]


def rows_by_model(path):
    out = defaultdict(dict)
    for r in csv.DictReader(open(path, encoding="utf8")):
        key = (r["table"], r["names"], r["info"], r["rung"], r["partner_kind"])
        out[(r["build"], r["model"])][key] = (int(r["answers"]), int(r["parsed"]), int(r["picked_best"]),
                                               int(r["picked_partner"] or 0))
    return out


def main():
    res = {"counts": [os.path.relpath(c, os.path.join(STUDY, "..")).replace("\\", "/") for _, c, _ in CHECKS],
           "by_build_and_model": {}}
    for builds, counts, extra in CHECKS:
        with tempfile.TemporaryDirectory() as d:
            fresh = os.path.join(d, "counts.csv")
            subprocess.run([sys.executable, os.path.join(HERE, "count_git.py"), "--builds", builds, "--out", fresh]
                           + extra, check=True, capture_output=True)
            new = rows_by_model(fresh)
        old = rows_by_model(counts)
        for key in sorted(set(old) | set(new)):
            build, model = key
            if key not in new:
                verdict = (f"not in this package: a run still going when the counts were taken "
                           f"({sum(v[0] for v in old[key].values())} answers counted)")
            elif key not in old:
                verdict = "in this package but not in the counts file"
            else:
                verdict = "equal" if new[key] == old[key] else "differs"
            res["by_build_and_model"].setdefault(build, {})[model] = verdict
    res["all_equal"] = all(v == "equal" or v.startswith("not in this package")
                           for b in res["by_build_and_model"].values() for v in b.values())
    out = os.path.join(STUDY, "results", "counts_check.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf8", newline="\n") as f:
        json.dump(res, f, indent=1)
    n = sum(len(b) for b in res["by_build_and_model"].values())
    print(f"{n} builds and models checked; every complete model's counts equal the counts file: {res['all_equal']}")
    return 0 if res["all_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
