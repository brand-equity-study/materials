"""What the rerun's cleaning of Study 1b's prompts without brand names changed besides brand text, and which tables kept in the check without the brand-naming tables still name a brand of the study.

Reads the cleaning list (materials/cleaning/cleaned-prompt-replacements.csv: for each table, a text of the corpus's
prompt without brand names and what the cleaned prompt has in its place), the list of texts that still identified a
brand (materials/names_hidden_leaks.csv, five kinds), the rerun's prompts (materials/rerun/prompts.jsonl.gz: cells
shown, hidden and hidden_clean), a hand reading of each cleaning row whose words are not all on that list
(materials/cleaning/cleaning-rows-read.csv) and the first-claim examples of the paper's website
(materials/cleaning/website-first-claim-examples.json).

1. Each row of the cleaning list is brand text when every word that it removes or replaces lies inside a listed text of
   its table (any kind) or inside 'the manufacturer' (the corpus's mask for a brand's name); otherwise it changes text
   that names no brand: a value with a number (such as 'suction: 65 AW' to 'suction: not stated'), a specification
   line's value, or description words (such as a quality claim). Every such row is listed with its words.
2. The changed lines: for trial 0 of each table, every line of a product that differs between the corpus's and the
   cleaned prompt, whether it holds a listed text, and whether it is the top-ranked product's.
3. The website's examples: for each, every line that differs between its corpus and cleaned prompt, with the cleaning
   rows behind it; an example with a row that is not brand text is flagged.
4. The tables kept in the check without the tables of kind 1 (a text that names the product's own brand): in each, the
   product brands of the study (any table's brand) named as whole words in its prompts without brand names.

Writes study1b-64-models-on-34-tables/results/cleaning_changes.json.

    python study1b-64-models-on-34-tables/code/cleaning_changes.py [--materials DIR] [--out FILE]
"""
import argparse
import csv
import difflib
import gzip
import json
import pathlib
import re
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parents[1]   # the top of the replication package

ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
ap.add_argument("--materials", default=str(PKG / "study1b-64-models-on-34-tables" / "materials" / "cleaning"),
                help="folder holding cleaned-prompt-replacements.csv, cleaning-rows-read.csv and "
                     "website-first-claim-examples.json")
ap.add_argument("--out", default=str(PKG / "study1b-64-models-on-34-tables" / "results" / "cleaning_changes.json"))
ARGS = ap.parse_args()
CLEAN = pathlib.Path(ARGS.materials)
REPL = CLEAN / "cleaned-prompt-replacements.csv"
LIST = PKG / "study1b-64-models-on-34-tables" / "materials" / "names_hidden_leaks.csv"
ITEMS = PKG / "study1b-64-models-on-34-tables" / "materials" / "rerun" / "prompts.jsonl.gz"
EXAMPLES = CLEAN / "website-first-claim-examples.json"
READ = CLEAN / "cleaning-rows-read.csv"
OUT = pathlib.Path(ARGS.out)
# a word keeps inner marks ('26.1MP', 'X-Trans', 'aptX') but not a mark at its end ('ecosystem.' is 'ecosystem' and '.')
TOKEN = re.compile(r"\w+(?:[.+'/-]\w+)*|[^\w\s]")


def spans(text, phrases):
    """Character spans in text of each phrase (case-insensitive, as written)."""
    out = []
    for p in phrases:
        for m in re.finditer(re.escape(p), text, re.I):
            out.append((m.start(), m.end()))
    for m in re.finditer(r"the manufacturer", text, re.I):
        out.append((m.start(), m.end()))
    return out


def classify(find, replace, listed):
    """(is brand text, the removed words outside every listed text)."""
    toks = [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(find)]
    rtoks = [m.group(0) for m in TOKEN.finditer(replace)]
    sp = spans(find, listed)
    covered = lambda s, e: any(a <= s and e <= b for a, b in sp)  # noqa: E731
    outside = []
    sm = difflib.SequenceMatcher(a=[t[0] for t in toks], b=rtoks, autojunk=False)
    for op, i1, i2, _, _ in sm.get_opcodes():
        if op in ("replace", "delete"):
            for w, s, e in toks[i1:i2]:
                if re.match(r"\w", w) and not covered(s, e):
                    outside.append(w)
    return not outside, outside


def kind_of_change(find, outside):
    if any(re.search(r"\d", w) for w in outside):
        return "a value with a number"
    if re.match(r"\s*[a-z_ ]+:\s", find):
        return "a specification line's value"
    return "description words"


def blocks(user):
    out = {}
    for m in re.finditer(r"--- Product (\w) ---\n(.*?)(?=\n\n--- Product|\n\nWhich|\Z)", user, re.S):
        out[m.group(1)] = m.group(2).split("\n")
    return out


def main():
    listed = defaultdict(list)
    for r in csv.DictReader(open(LIST, encoding="utf-8")):
        listed[r["table"]].append(r)
    rows = list(csv.DictReader(open(REPL, encoding="utf-8")))
    items = [json.loads(l) for l in gzip.open(ITEMS, "rt", encoding="utf-8")]
    by = {(it["table"][3:], it["trial"], it["cell"]): it for it in items}

    # 1. each row of the cleaning list
    classified, by_table = [], defaultdict(lambda: {"rows": 0, "not_brand_text": 0, "examples": []})
    for i, r in enumerate(rows, 1):
        is_brand, outside = classify(r["find"], r["replace"], [x["text"] for x in listed[r["table"]]])
        c = {"row": i, "table": r["table"], "find": r["find"].strip(), "replace": r["replace"].strip(), "brand_text": is_brand}
        if not is_brand:
            c["words_without_a_brand"] = outside
            c["kind"] = kind_of_change(r["find"], outside)
        classified.append(c)
        t = by_table[r["table"]]
        t["rows"] += 1
        if not is_brand:
            t["not_brand_text"] += 1
            t["examples"].append(f"{c['find']} -> {c['replace'] or '(removed)'}")
    not_brand = [c for c in classified if not c["brand_text"]]
    kinds = defaultdict(int)
    for c in not_brand:
        kinds[c["kind"]] += 1
    # the hand reading of each row whose words are not all on the list (cleaning-rows-read.csv): maker_name (a
    # maker's name for a feature, part or format that the list did not hold, which the cleaning's own rule counts as
    # brand text), claim (a claim of quality or a brand's slogan that names no brand), spec_value (a specification
    # value changed or removed) or no_change (the same meaning in other words)
    read = {int(r["row"]): r for r in csv.DictReader(open(READ, encoding="utf-8"))}
    unread = [c["row"] for c in not_brand if c["row"] not in read]
    stale = [k for k in read if k not in {c["row"] for c in not_brand}]
    if unread or stale:
        raise SystemExit(f"refused: rows without a reading {unread}, readings of rows now on the list {stale}")
    classes = defaultdict(list)
    for c in not_brand:
        c["class"], c["why"] = read[c["row"]]["class"], read[c["row"]]["why"]
        classes[c["class"]].append(c)
    not_brand_text = [c for c in not_brand if c["class"] in ("claim", "spec_value")]

    # 2. the changed lines of trial 0 of each table
    changed = []
    for t in sorted({k[0] for k in by}):
        h, c, s = by[(t, 0, "hidden")], by[(t, 0, "hidden_clean")], by[(t, 0, "shown")]
        bh, bc = blocks(h["user"]), blocks(c["user"])
        orig_h = {k: v["orig"] for k, v in h["products"].items()}
        orig_c = {v["orig"]: k for k, v in c["products"].items()}
        best_orig = s["products"][s["best"]]["orig"]
        for kh, lines in bh.items():
            lc = bc[orig_c[orig_h[kh]]]
            for a, b in zip(lines, lc):
                if a != b:
                    holds = any(x["text"].lower() in a.lower() for x in listed[t]) or "the manufacturer" in a
                    changed.append({"table": t, "product": orig_h[kh], "top_ranked": orig_h[kh] == best_orig,
                                    "field": a.split(":", 1)[0], "holds_a_listed_text": holds, "before": a, "after": b})

    # 3. the website's examples
    ex_out = []
    for e in json.load(open(EXAMPLES, encoding="utf-8"))["examples"]:
        t = e["table"][3:]
        lines = [x for x in changed if x["table"] == t]
        rows_t = [c for c in classified if c["table"] == t and c["find"] and any(c["find"] in x["before"] for x in lines)]
        off_list = [f"row {c['row']}: {c['find']} -> {c['replace'] or '(removed)'} ({c['class']})"
                    for c in rows_t if not c["brand_text"]]
        bad = [x for x in off_list if x.endswith(("(claim)", "(spec_value)"))]
        ex_out.append({"model": e["model"], "table": e["table"], "changed_lines_trial0": len(lines),
                       "cleaning_rows_used": len(rows_t), "rows_not_on_the_list": off_list,
                       "claim_or_spec_value_changed": bad})

    # 4. the tables kept in the check without kind 1, and the study's brands named in their prompts
    study_brands = sorted({p["true_brand"] for (t, tr, cell), it in by.items() if cell == "shown"
                           for p in it["products"].values() if p.get("kind", "").startswith("familiar") and p.get("true_brand")})
    kind1 = sorted({r["table"] for rs in listed.values() for r in rs if r["kind"] == "1 brand"})
    kept = sorted(t for t in {k[0] for k in by} if t not in kind1)
    named = {}
    for t in kept:
        found = {}
        for cell in ("hidden", "hidden_clean"):
            text = "\n".join(it["user"] for (tt, tr, cc), it in by.items() if tt == t and cc == cell)
            found[cell] = sorted(b for b in study_brands if re.search(rf"(?<![\w-]){re.escape(b)}(?![\w-])", text))
        if found["hidden"]:
            own = {p["true_brand"] for p in by[(t, 0, "shown")]["products"].values()}
            named[t] = {"brands_named": found["hidden"], "still_named_after_cleaning": found["hidden_clean"],
                        "a_brand_of_this_table": sorted(set(found["hidden"]) & own),
                        "lines": sorted({l.strip() for (tt, tr, cc), it in by.items() if tt == t and cc == "hidden"
                                         for l in it["user"].split("\n")
                                         if any(re.search(rf"(?<![\w-]){re.escape(b)}(?![\w-])", l) for b in found["hidden"])
                                         and not l.startswith(("Name:", "Brand:"))})[:6]}

    out = {
        "about": __doc__.split("\n\n")[0],
        "cleaning_rows": len(rows),
        "cleaning_rows_only_listed_text": len(rows) - len(not_brand),
        "cleaning_rows_with_words_not_on_the_list": len(not_brand),
        "read_as": {k: len(v) for k, v in classes.items()},
        "rows_not_brand_text": len(not_brand_text),
        "tables_with_a_change_not_brand_text": sorted({c["table"] for c in not_brand_text}),
        "not_brand_text_by_table": {t: [f"row {c['row']}: {c['find']} -> {c['replace'] or '(removed)'} ({c['class']}: {c['why']})"
                                        for c in not_brand_text if c["table"] == t]
                                    for t in sorted({c["table"] for c in not_brand_text})},
        "on_the_top_ranked_product": [f"row {c['row']}: {c['find']} -> {c['replace']}" for c in not_brand_text
                                      if "top-ranked" in c["why"]],
        "rows_with_words_not_on_the_list": not_brand,
        "changed_lines_trial0": len(changed),
        "changed_lines_trial0_top_ranked": sum(1 for x in changed if x["top_ranked"]),
        "changed_lines_trial0_no_listed_text": sum(1 for x in changed if not x["holds_a_listed_text"]),
        "changed_lines": changed,
        "website_examples": ex_out,
        "tables_of_kind_1": kind1,
        "kept_tables": len(kept),
        "kept_tables_naming_a_study_brand": named,
        "study_brands": len(study_brands),
        "script": "study1b-64-models-on-34-tables/code/cleaning_changes.py",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({k: out[k] for k in ("cleaning_rows", "cleaning_rows_only_listed_text", "cleaning_rows_with_words_not_on_the_list",
                               "read_as", "rows_not_brand_text", "tables_with_a_change_not_brand_text",
                               "on_the_top_ranked_product", "changed_lines_trial0", "kept_tables")})
    for t, v in out["not_brand_text_by_table"].items():
        for x in v:
            print("  ", t, x[:170])
    for e in ex_out:
        print("example", e["model"], e["table"], "claim or spec value changed:", e["claim_or_spec_value_changed"],
              "| maker names off the list:", len(e["rows_not_on_the_list"]) - len(e["claim_or_spec_value_changed"]))
    for t, v in named.items():
        print("kept table naming a study brand:", t, v["brands_named"], "own:", v["a_brand_of_this_table"],
              "after cleaning:", v["still_named_after_cleaning"])


if __name__ == "__main__":
    sys.exit(main())
