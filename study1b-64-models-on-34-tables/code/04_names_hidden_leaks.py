"""What the names-hidden prompts still show of the brands, and the names gap without the tables that show it.

The names-hidden condition (baseline_brand_blind) replaced each product's brand with "Brand A" to "Brand E" and its name
with "Product A" to "Product E", and replaced the brand string inside its description with "the manufacturer"
(experiment/conditions.py, _anonymize_brands). Everything else in the description and the spec line was kept.

study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv lists, for each table, every text in the names-hidden prompt that points to a brand, in five kinds:
  1 brand          the product's own brand, its owner or a sister brand is named ("Razer Green", "Apple M2", "N/A (Bose)")
  2 line           a product line or model name of the maker ("Galaxy AI", "LatteGo", "Neo QLED", "AXE7800")
  3 feature        a technology, feature, chip or service name that belongs to the maker ("MagSafe", "ReactX", "webOS")
  4 copy           a sentence of the brand's own copy in which only the brand was replaced ("Legendary the manufacturer comfort")
  5 other company  another company's name, such as a component or platform ("Sony IMX890" in a OnePlus phone); listed,
                   not counted as a leak of the product's brand
The script refuses to run if a listed text is not in the names-hidden block of the product that the list names, or if
any brand name of the 34 tables (or Apple, Google, Amazon or Logi) appears in a names-hidden prompt outside a listed text.
The list of kinds 2 to 4 was made by reading every names-hidden table; it is the author's reading and is checked by a
second reader.

It then reports the names gap without the tables that hold each kind of leak, with the two-way cluster bootstrap, and
counts the names-hidden answers that name one of the table's five brands.

    python study1b-64-models-on-34-tables/code/04_names_hidden_leaks.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402

LEAKS = cc.MATERIALS / "names_hidden_leaks.csv"
# owners, product lines, and the real makers behind the invented names of the products that the tables mark as best
EXTRA_NAMES = ["Apple", "Google", "Amazon", "Logi", "Galaxy", "iPhone", "iPad", "Archer", "Redmi", "Velop", "Xiaomi", "TCL",
               "TP-Link", "EarFun", "Tribit", "OPPO", "Best Buy", "Hisense", "Soundcore", "Anker", "HiFiMAN", "Keychron",
               "Roborock", "Amazfit", "Fairphone", "Wacaco", "inov-8"]
# other spellings that a model may use in its answer
ALIASES = {"The North Face": ["North Face"], "Western Digital": ["WD"], "Ultimate Ears": ["UE"],
           "Audio-Technica": ["Audio Technica"], "De'Longhi": ["De’Longhi", "DeLonghi", "Delonghi"], "S'well": ["S’well"]}


def key(p):
    return (p["Specs"], p["Price"], p["Sustainability rating"])


def full_key(p):
    return (p["Specs"], p["Price"], p["Sustainability rating"], p["Description"])


def word(name):
    return r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])"


def main() -> int:
    df, info = cc.load_rows(["model_key", "assortment_id", "chose_optimal", "optimal_product", "user_message", "raw_response"])
    sh, hd = df[df.condition == cc.SHOWN], df[df.condition == cc.HIDDEN]
    tables = sorted(sh.assortment_id.unique())

    shown, hidden, brand_of, name_of, best_brand = {}, {}, {}, {}, {}
    for t in tables:
        ps = cc.parse_products(sh[sh.assortment_id == t].user_message.iloc[0])
        ph = cc.parse_products(hd[hd.assortment_id == t].user_message.iloc[0])
        # every row of a table holds the same products, descriptions included; check that before using one row
        for cond_rows, first in ((sh[sh.assortment_id == t], ps), (hd[hd.assortment_id == t], ph)):
            sig = sorted(full_key(v) for v in first.values())
            for m in cond_rows.user_message.unique():
                if sorted(full_key(v) for v in cc.parse_products(m).values()) != sig:
                    raise SystemExit(f"REFUSED: {t} has rows with different products or descriptions")
        by_key = {key(v): v for v in ps.values()}
        if len(by_key) != 5:
            raise SystemExit(f"REFUSED: {t} has two products with the same spec line, price and rating")
        shown[t], hidden[t] = ps, ph
        brand_of[t] = {L: by_key[key(v)]["Brand"] for L, v in ph.items()}
        name_of[t] = {L: by_key[key(v)]["Name"] for L, v in ph.items()}
        best_brand[t] = ps[sh[sh.assortment_id == t]["optimal_product"].iloc[0]]["Brand"]

    rows = list(csv.DictReader(open(LEAKS, encoding="utf-8")))
    covered = {t: [] for t in tables}
    for r in rows:
        t = "sr_" + r["table"]
        letters = [L for L, b in brand_of[t].items() if b == r["brand"]]
        if not letters:
            raise SystemExit(f"REFUSED: {r['table']} has no product of brand {r['brand']}")
        if r.get("product"):
            letters = [L for L in letters if name_of[t][L] == r["product"]]
            if not letters:
                raise SystemExit(f"REFUSED: {r['table']} has no product named {r['product']}")
        elif len(letters) > 1:
            raise SystemExit(f"REFUSED: {r['table']} has {len(letters)} products of {r['brand']}; the row must name the product")
        block = hidden[t][letters[0]]["Description"] + " || " + hidden[t][letters[0]]["Specs"]
        if r["text"] not in block:
            raise SystemExit(f"REFUSED: '{r['text']}' is not in the names-hidden block of {r['brand']} in {r['table']}")
        r["on_best_product"] = r["brand"] == best_brand[t]
        covered[t].append(r["text"])

    all_brands = sorted({v["Brand"] for t in tables for v in shown[t].values()} | set(EXTRA_NAMES))
    unlisted = []
    for t in tables:
        msg = hd[hd.assortment_id == t].user_message.iloc[0]
        spans = [(m.start(), m.end()) for c in covered[t] for m in re.finditer(re.escape(c), msg)]
        for b in all_brands:
            for m in re.finditer(word(b), msg, re.I):
                # a mention is accounted for only when it lies inside an occurrence of a listed text
                if not any(s <= m.start() and m.end() <= e for s, e in spans):
                    ctx = msg[max(0, m.start() - 60): m.end() + 60]
                    unlisted.append(f"{t}: {b} in ...{ctx.replace(chr(10), ' | ')}...")
    if unlisted:
        raise SystemExit("REFUSED: brand names in names-hidden prompts with no row in names_hidden_leaks.csv:\n" + "\n".join(unlisted))

    kinds = {t: sorted({r["kind"][0] for r in rows if "sr_" + r["table"] == t and r["kind"][0] in "1234"}) for t in tables}
    # leaks on the familiar brands only (a leak on the best product points to a mostly unfamiliar real maker)
    kinds_familiar = {t: sorted({r["kind"][0] for r in rows if "sr_" + r["table"] == t and r["kind"][0] in "1234"
                                 and not r["on_best_product"]}) for t in tables}
    per_table = []
    for t in tables:
        rr = [r for r in rows if "sr_" + r["table"] == t]
        per_table.append({"table": t, "kinds": kinds[t], "kinds_on_familiar_brands": kinds_familiar[t],
                          "leaks": [f"{r['kind']}: \"{r['text']}\" ({r['brand']}{', the best product' if r['on_best_product'] else ''}; "
                                    f"points to {r['points_to']})" for r in rr]})

    df["non_optimal"] = 1.0 - df["chose_optimal"].astype(float)
    models, tlist, arr = cc.cell_arrays(df, "non_optimal")

    def gap_without(drop):
        keep = [i for i, t in enumerate(tlist) if t not in drop]
        if not keep:
            return {"tables": 0}
        sub = {c: (arr[c][0][:, keep], arr[c][1][:, keep]) for c in arr}
        boot = cc.twoway_bootstrap(sub, len(models), len(keep))
        s1, n1 = sub[cc.SHOWN]
        s0, n0 = sub[cc.HIDDEN]
        return {"tables": len(keep), "shown_pct": round(100 * s1.sum() / n1.sum(), 2), "hidden_pct": round(100 * s0.sum() / n0.sum(), 2),
                "gap_pp": round(100 * cc.pooled_gap(sub), 2), "ci95_pp": cc.ci(boot, 100), "p_two_sided": cc.p_two_sided(boot), "draws": cc.DRAWS, "seed": cc.SEED}

    scenarios = {}
    for label, ks in (("without kind 1 (brand named)", "1"), ("without kinds 1 and 2", "12"),
                      ("without kinds 1 to 3", "123"), ("without kinds 1 to 4", "1234")):
        drop = sorted(t for t in tables if set(kinds[t]) & set(ks))
        drop_f = sorted(t for t in tables if set(kinds_familiar[t]) & set(ks))
        scenarios[label] = {"dropped_tables": drop, "gap": gap_without(set(drop))}
        if drop_f != drop:
            scenarios[label + ", counting leaks on familiar brands only"] = {"dropped_tables": drop_f, "gap": gap_without(set(drop_f))}

    # answers with names hidden that name one of the table's five brands (case-sensitive, so that the verb "beats"
    # does not count as the brand Beats; with the other spellings in ALIASES)
    rec = []
    for t in tables:
        brands = sorted({v["Brand"] for v in shown[t].values()})
        msg = hd[hd.assortment_id == t].user_message.iloc[0]
        names = {b: [b] + ALIASES.get(b, []) for b in brands}
        in_prompt = {b for b in brands if any(re.search(word(n), msg) for n in names[b])}
        sub = hd[hd.assortment_id == t]
        for _, row in sub.iterrows():
            text = str(row["raw_response"])
            named = [b for b in brands if any(re.search(word(n), text) for n in names[b])]
            if named:
                rec.append({"table": t, "model": row["model_key"], "brands": named,
                            "brand_in_prompt": any(b in in_prompt for b in named), "non_optimal": bool(not row["chose_optimal"])})
    by_table = {}
    for r in rec:
        by_table[r["table"]] = by_table.get(r["table"], 0) + 1
    recognition = {
        "hidden_answers": int(len(hd)),
        "answers_naming_a_brand_of_the_table": len(rec),
        "of_which_the_brand_is_written_in_the_prompt": sum(r["brand_in_prompt"] for r in rec),
        "of_which_non_optimal": sum(r["non_optimal"] for r in rec),
        "by_table": dict(sorted(by_table.items(), key=lambda kv: -kv[1])),
        "note": "a case-sensitive whole-word match of the five brand names of the table, and their other spellings, in the model's whole answer",
    }

    count = lambda k: sum(1 for t in tables if k in kinds[t])
    res = {
        "leak_file": "study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv",
        "tables_with_kind": {"1 brand": count("1"), "2 line": count("2"), "3 feature": count("3"), "4 copy": count("4")},
        "tables_with_any_of_kinds_1_to_3": sum(1 for t in tables if set(kinds[t]) & set("123")),
        "tables_with_no_leak_of_kinds_1_to_4": [t for t in tables if not kinds[t]],
        "listed_texts": {k: sum(1 for r in rows if r["kind"].startswith(k)) for k in "12345"},
        "gap_without": scenarios, "recognition": recognition, "per_table": per_table,
    }
    cc.write_result("names_hidden_leaks", res, "study1b-64-models-on-34-tables/code/04_names_hidden_leaks.py", info)
    print("tables with each kind:", res["tables_with_kind"], "; any of 1-3:", res["tables_with_any_of_kinds_1_to_3"])
    print("tables with no leak:", res["tables_with_no_leak_of_kinds_1_to_4"])
    for label, s in scenarios.items():
        print(f"{label}: dropped {len(s['dropped_tables'])}; {s['gap']}")
    print("recognition:", {k: v for k, v in recognition.items() if k != "by_table"}, recognition["by_table"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
