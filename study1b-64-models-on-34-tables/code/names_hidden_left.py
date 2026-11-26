"""What the list of texts that still identified a brand holds, and where those texts remain.

The list of texts that still identify a brand when brand names are hidden had 190 texts when first read; a second
reader kept, moved, removed and added texts, and the final list is checked here against that reader's counts.

Reads the list (study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv), the second reader's counts
(study1b-64-models-on-34-tables/materials/names-hidden-review/second_reader.json) and Study 1b's rerun prompts
(study1b-64-models-on-34-tables/materials/rerun/prompts.jsonl.gz: the corpus's own prompts without brand names, cell hidden, and the cleaned
ones, cell hidden_clean). For every listed text it records whether the text appears in its table's corpus prompts
without brand names and in its table's cleaned prompts (in any trial). Writes study1b-64-models-on-34-tables/results/names_hidden_left.json.

    python study1b-64-models-on-34-tables/code/names_hidden_left.py [--out PATH]
"""
import argparse
import csv
import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]   # the top of the replication package
LIST = PKG / "study1b-64-models-on-34-tables" / "materials" / "names_hidden_leaks.csv"
AGREEMENT = PKG / "study1b-64-models-on-34-tables" / "materials" / "names-hidden-review" / "second_reader.json"
ITEMS = PKG / "study1b-64-models-on-34-tables" / "materials" / "rerun" / "prompts.jsonl.gz"
OUT = PKG / "study1b-64-models-on-34-tables" / "results" / "names_hidden_left.json"
KINDS = ("1 brand", "2 line", "3 feature", "4 copy", "5 other company")


def appears(text, prompts):
    """A listed text is in a prompt when it occurs there as written, not inside a longer word."""
    rx = re.compile(rf"(?<![\w-]){re.escape(text)}(?![\w-])")
    return any(rx.search(p) for p in prompts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    out_path = Path(ap.parse_args().out)

    rows = list(csv.DictReader(open(LIST, encoding="utf-8", newline="")))
    agree = json.load(open(AGREEMENT, encoding="utf-8"))
    first = agree["rows_read"]
    final = first - agree["rows_removed"] + agree["rows_added"]
    if final != len(rows):
        raise SystemExit(f"refused: the first list's {first} texts, less {agree['rows_removed']} removed and plus "
                         f"{agree['rows_added']} added, make {final}, but the list holds {len(rows)}")
    if agree["rows_confirmed_unchanged"] + agree["rows_moved_between_kinds"] + agree["rows_removed"] != first:
        raise SystemExit("refused: the second reader's kept, moved and removed texts do not add up to the first list")
    unknown = {r["kind"] for r in rows} - set(KINDS)
    if unknown:
        raise SystemExit(f"refused: kinds not in the five: {sorted(unknown)}")

    hidden, clean = defaultdict(list), defaultdict(list)
    with gzip.open(ITEMS, "rt", encoding="utf-8") as fh:
        for line in fh:
            it = json.loads(line)
            t = it["table"][3:]   # 'sr_backpacks_01' -> 'backpacks_01', as the list names its tables
            if it["cell"] == "hidden":
                hidden[t].append(it["user"])
            elif it["cell"] == "hidden_clean":
                clean[t].append(it["user"])
    missing = sorted({r["table"] for r in rows} - set(hidden))
    if missing:
        raise SystemExit(f"refused: listed tables with no prompts: {missing}")

    by_kind = {}
    for k in KINDS:
        kr = [r for r in rows if r["kind"] == k]
        by_kind[k] = {
            "texts": len(kr),
            "tables": len({r["table"] for r in kr}),
            "in_the_prompts_without_brand_names": sum(appears(r["text"], hidden[r["table"]]) for r in kr),
            "left_after_cleaning": sum(appears(r["text"], clean[r["table"]]) for r in kr),
        }
    k14 = [k for k in KINDS if not k.startswith("5")]
    out = {
        "about": __doc__.split("\n\n")[0],
        "list": LIST.relative_to(PKG).as_posix(),
        "second_reader": {"first_list": first, "kept_unchanged": agree["rows_confirmed_unchanged"],
                          "moved_between_kinds": agree["rows_moved_between_kinds"], "removed": agree["rows_removed"],
                          "added": agree["rows_added"]},
        "final_list": len(rows),
        "kinds_1_to_4": sum(by_kind[k]["texts"] for k in k14),
        "by_kind": by_kind,
        "kinds_1_to_4_left_after_cleaning": sum(by_kind[k]["left_after_cleaning"] for k in k14),
        "left_after_cleaning_texts": sorted(f"{r['table']}: {r['text']} ({r['kind']})" for r in rows
                                           if not r["kind"].startswith("5") and appears(r["text"], clean[r["table"]])),
        "script": Path(__file__).resolve().relative_to(PKG).as_posix(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    open(out_path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in ("second_reader", "final_list", "kinds_1_to_4", "kinds_1_to_4_left_after_cleaning")}))
    for k, v in by_kind.items():
        print(k, v)
    for x in out["left_after_cleaning_texts"]:
        print("  left:", x)


if __name__ == "__main__":
    sys.exit(main())
