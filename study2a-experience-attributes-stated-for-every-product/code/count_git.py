"""Counts the answers in this package (the Claude models through the Messages API, Claude Fable 5.2 through the Claude
command line and the GPT-6 models through Codex) into the schema of the open panel's counts, so that pool_all.py reads
every model's answers the same way, and converts the open panel's letters (study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz, one
row per answer) into the same schema. Writes one CSV: build, model, table, names, info, rung, partner_kind, answers,
parsed, picked_best, picked_partner. The build codes are the project's: dom2 (the strictly better tables), split1
(each piece alone) and eq1 (the price).

    python study2a-experience-attributes-stated-for-every-product/code/count_git.py --builds dom2,split1,eq1 --out <counts.csv> --letters study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz --letters-build b2/dom2
"""
import argparse
import csv
import gzip
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))  # analyze.py and parse_answer.py
import analyze as AN  # noqa: E402  (load; read only)

FIELDS = ["build", "model", "table", "names", "info", "rung", "partner_kind", "answers", "parsed", "picked_best",
          "picked_partner"]


SETS = {"dom2": "strictly-better-tables", "split1": "each-piece-alone", "eq1": "price", "attr1": "further-information"}  # build code -> the package's set of prompts


def count_build(build):
    items, rows, _ = AN.load(SETS[build], studies=("study1a-tables-with-one-optimal-product", "study2a-experience-attributes-stated-for-every-product", "web-appendix-analyses/each-piece-of-information-alone", "study2b-how-much-a-familiar-brand-is-worth"))
    c = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        it = items[r["id"]]
        k = (build, r["model"], it["table"], it["names"], str(it["info"]), str(it["rung"]), it.get("partner_kind", ""))
        v = c[k]
        v[0] += 1
        v[1] += 1 if r["letter"] else 0
        v[2] += 1 if r["letter"] and r["letter"] == it["best"] else 0
        v[3] += 1 if r["letter"] and r["letter"] == it.get("partner") else 0
    return c


def count_letters(path, build_in, build_out):
    c = defaultdict(lambda: [0, 0, 0, 0])
    with gzip.open(path, "rt", encoding="utf8") as fh:
        for r in csv.DictReader(fh):
            if r["build"] != build_in:
                continue
            k = (build_out, r["model"], r["table"], r["names"], r["info"], r["rung"], "")
            v = c[k]
            v[0] += 1
            v[1] += 1 if r["letter"] else 0
            v[2] += 1 if r["letter"] and r["letter"] == r["best"] else 0
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--builds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--letters", default="")
    ap.add_argument("--letters-build", default="b2/dom2")
    a = ap.parse_args()
    out = {}
    for b in a.builds.split(","):
        out.update(count_build(b))
    # --letters takes one export or several, joined by commas (job 13394 added Qwen 3.5 122B's dom2 letters beside
    # export 12683's, 22 November); a model found in two exports for the build is refused, so nothing is counted twice
    seen = {}
    for path in [p for p in a.letters.split(",") if p]:
        part = count_letters(path, a.letters_build, a.letters_build.split("/")[-1])
        for m in {k[1] for k in part}:
            if m in seen:
                raise SystemExit(f"refused: {m} is in both {seen[m]} and {path} for {a.letters_build}")
            seen[m] = path
        clash = set(part) & set(out)
        if clash:
            raise SystemExit(f"refused: {len(clash)} cells of {path} are also in the git answers, such as {sorted(clash)[0]}")
        out.update(part)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf8") as f:
        w = csv.writer(f, lineterminator="\n")  # LF, as the committed counts are (the same bytes on every computer)
        w.writerow(FIELDS)
        for k in sorted(out):
            w.writerow(list(k) + out[k])
    print(f"{len(out)} rows, {sum(v[0] for v in out.values())} answers, models {len({k[1] for k in out})}")


if __name__ == "__main__":
    main()
