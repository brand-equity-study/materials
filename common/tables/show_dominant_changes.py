"""Print every change dominant_sets.py makes to the corpus tables, table by table, as a Markdown file for reading.

    python common/tables/show_dominant_changes.py > study1a-tables-with-one-optimal-product/materials/strictly-better-tables/DOMINANT-SETS.md
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dominant_sets as D  # noqa: E402
import tables as S  # noqa: E402

tables = S.load_tables()
dom, _ = D.build(tables)
print("# The dominant sets: every change from the scrubbed corpus tables\n")
print("Written by `show_dominant_changes.py` from `dominant_sets.py`. Letters are the corpus's letters (before the "
      "letters are shuffled for each trial); * marks the designated best product. Prices are set by the price ladder "
      "of `tables.py` and are not listed.\n")
for tid, reason in D.EXCLUDE.items():
    print(f"- Left out: {tid}: {reason}.")
print()
for tid, t in dom.items():
    best = next(p["orig"] for p in t["products"] if p["best"])
    print(f"## {tid[:-4]}\n")
    by_kind = {}
    for orig, attr, old, new, why in t["changes"]:
        by_kind.setdefault(why, []).append(f"{orig}{'*' if orig == best else ''} {attr}: {old!r} -> {new!r}")
    if not by_kind:
        print("No change.\n")
    for why, lines in by_kind.items():
        print(f"{why}:\n")
        for l in lines:
            print(f"- {l}")
        print()
