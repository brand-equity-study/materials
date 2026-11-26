"""Summaries of the measure's pilot from analyze_mbbe.py's output (every open model), for RESULTS.md.

    Writes summary.json (every number that
RESULTS.md cites), brand_pairs.csv (each familiar brand and category over the included models whose category reads the
specifications), brand_table.md (the same as the table in RESULTS.md, each number rounded once from the unrounded
value), cells.csv (each brand, category and model with its units), felipe_brands.csv (Apple, Keurig and Sony in each
model) and stability_cells.csv (each model and category with its stability ratios and whether the ratio can be read).
Reads nothing else except, for a numbers.json without the tested prices, the pilot's items.

the
price equivalents beyond each category's tested prices counted and marked; both readings of the held-out criterion;
stability counted on the readable cells only; the repeat's kappa over the cells that read the specifications; Amendment
1's second reference (section 4's, all invented names) and its marks; and the plan's known-groups test.
"""
import argparse
import csv
import json
import math
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
PKG = REPO = HERE.parents[2]   # the package
READ_RULE = 0.90
FACTORS = ("system_index", "layout", "request_wording")


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def r1(x, nd=1):
    return None if x is None else round(x, nd)


def share_premium(mbbe):
    return 100 * (math.exp(mbbe) / (math.exp(mbbe) + 4) - 0.2)


def tested_prices(d, items_path):
    """{category: sorted prices}: from numbers.json when it holds them, else from the pilot's shown sets."""
    out = {}
    for mm in d["models"].values():
        for c, cc in mm["categories"].items():
            if cc.get("tested_prices"):
                out[c] = sorted(cc["tested_prices"])
    if out:
        return out
    acc = {}
    for line in open(items_path, encoding="utf8"):
        it = json.loads(line)
        if it["cell"] == "shown":
            acc.setdefault(it["category"], set()).update(p["price"] for p in it["products"].values())
    return {c: sorted(v) for c, v in acc.items()}


def inside(pe, prices):
    if pe is None:
        return None
    span = max(prices) / min(prices)
    return 1 / span <= 1 + pe / 100 <= span


def inside_strict(pe, prices):
    """The stricter reading: MBBE is the familiar name's value at the category's centre price (log price is centred
    on the mean log of the tested prices, as analyze_mbbe.Design does), so the brand is as likely to be picked as an
    invented name at the centre price when it costs centre x (1 + pe / 100); that price must lie inside the tested
    prices, or the brand's own price slope is read beyond them. Every value beyond under inside() is beyond here too."""
    if pe is None:
        return None
    centre = math.exp(sum(math.log(p) for p in prices) / len(prices))
    return min(prices) <= centre * (1 + pe / 100) <= max(prices)


def left_out(d):
    """The models under the exclusion rule: numbers.json's own list when it has one, else the shown sets' letters."""
    if "left_out" in d:
        return d["left_out"]["models"], d["left_out"]["rule"]
    lo = {}
    for m, mm in d["models"].items():
        n = sum(c["sets_shown"] for c in mm["categories"].values())
        k = sum(c["sets_with_a_letter"] for c in mm["categories"].values())
        if k / n < READ_RULE:
            lo[m] = {"shown_sets": n, "with_a_letter": k, "read_pct": round(100 * k / n, 1)}
    return lo, "the shown sets with a letter, under 90 per cent (this numbers.json has no choice-item counts)"


def stability_rows(d, models, excluded):
    rows = []
    for m in models:
        for c, cc in d["models"][m]["categories"].items():
            row = {"model": m, "category": c, "reads_specifications": bool(cc["reads_specifications"]), "model_left_out": m in excluded}
            for f in FACTORS:
                s = cc["stability"].get(f) or {}
                bv, iv = s.get("brand_variance"), s.get("brand_by_factor_variance")
                row[f"{f}_brand_variance"], row[f"{f}_by_factor_variance"] = bv, iv
                row[f"{f}_ratio"] = iv / bv if bv else None
                row[f"{f}_readable"] = bool(row["reads_specifications"] and not row["model_left_out"] and bv is not None and bv > 0)
            rows.append(row)
    return rows


def stability_summary(rows):
    out = {}
    for f in FACTORS:
        ok = [r[f"{f}_ratio"] for r in rows if r[f"{f}_readable"]]
        out[f] = {"readable_cells": len(ok), "median_ratio": r1(med(ok), 3),
                  "cells_below_one_half": sum(x < 0.5 for x in ok), "cells_above_one": sum(x > 1 for x in ok),
                  "reading_cells_with_brand_variance_zero_or_below": [f"{r['model']} | {r['category']}" for r in rows
                                                                       if r["reads_specifications"] and not r["model_left_out"]
                                                                       and (r[f"{f}_brand_variance"] is None or r[f"{f}_brand_variance"] <= 0)],
                  "cells_left_out": sum(1 for r in rows if not r["reads_specifications"] or r["model_left_out"])}
    return out


def held_out(d, models):
    held = [(m, c, cc["held_out_log_likelihood_gain"]) for m in models for c, cc in d["models"][m]["categories"].items()
            if cc["reads_specifications"]]
    by = {m: [g for mm, _, g in held if mm == m] for m in models}
    return {"cells": len(held), "positive": sum(1 for *_, g in held if g > 0),
            "models": len(models),
            "models_positive_in_every_reading_category": sum(1 for m in models if by[m] and all(g > 0 for g in by[m])),
            "models_positive_summed_over_reading_categories": sum(1 for m in models if by[m] and sum(by[m]) > 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/pretest_numbers.json"))
    ap.add_argument("--items", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/pilot1/items.jsonl"))
    ap.add_argument("--out", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/pilot1"))
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out)
    d = json.load(open(a.numbers, encoding="utf-8"))
    every = sorted(d["models"])
    excluded, rule = left_out(d)
    models = [m for m in every if m not in excluded]
    prices = tested_prices(d, a.items)
    span_pct = {c: round(100 * (max(p) / min(p) - 1), 1) for c, p in prices.items()}
    cells = []
    for m in every:
        for c, cc in d["models"][m]["categories"].items():
            for n, v in cc["names"].items():
                if v["kind"] != "familiar":
                    continue
                lo, hi = v["ci95"]
                pe = v["price_equivalent_pct"]
                s4 = v.get("mbbe_section4_reference")
                cells.append({"model": m, "category": c, "brand": n, "model_left_out": m in excluded,
                              "reads_specifications": bool(cc["reads_specifications"]),
                              "mbbe": v["mbbe"], "ci_low": lo, "ci_high": hi, "share_premium_pp": v["share_premium_pp"],
                              "price_equivalent_pct": pe,
                              "price_equivalent_inside_tested_span": v.get("price_equivalent_inside_tested_span", inside(pe, prices[c])),
                              "price_equivalent_price_inside_tested_prices": inside_strict(pe, prices[c]),
                              "rating_equivalent_stars": v["rating_equivalent_stars"],
                              "mbbe_section4_reference": s4,
                              "share_premium_section4_reference_pp": None if s4 is None else share_premium(s4),
                              "blind_gap_pp": v["blind_gap_pp"], "recognized_share": v["recognized_share"],
                              "unknown_to_model": v["unknown_to_model"], "reference_flag": cc.get("reference_flag", "")})
    read = [x for x in cells if x["reads_specifications"] and not x["model_left_out"]]
    pairs = {}
    for x in read:
        pairs.setdefault((x["brand"], x["category"]), []).append(x)
    pair_rows = []
    for (b, c), xs in sorted(pairs.items()):
        pes = [x for x in xs if x["price_equivalent_pct"] is not None]
        pair_rows.append({"brand": b, "category": c, "models": len(xs),
                          "share_premium_median_pp": med([x["share_premium_pp"] for x in xs]),
                          "share_premium_min_pp": min(x["share_premium_pp"] for x in xs),
                          "share_premium_max_pp": max(x["share_premium_pp"] for x in xs),
                          "models_above_zero": sum(1 for x in xs if x["ci_low"] > 0),
                          "models_below_zero": sum(1 for x in xs if x["ci_high"] < 0),
                          "models_with_a_price_equivalent": len(pes),
                          "price_equivalents_beyond_tested_span": sum(1 for x in pes if not x["price_equivalent_inside_tested_span"]),
                          "price_equivalents_beyond_tested_prices": sum(1 for x in pes if not x["price_equivalent_price_inside_tested_prices"]),
                          "price_equivalent_median_pct": med([x["price_equivalent_pct"] for x in pes]),
                          "price_equivalent_median_inside_tested_span": inside(med([x["price_equivalent_pct"] for x in pes]), prices[c]) if pes else None,
                          "price_equivalent_median_inside_tested_prices": inside_strict(med([x["price_equivalent_pct"] for x in pes]), prices[c]) if pes else None,
                          "rating_equivalent_median_stars": med([x["rating_equivalent_stars"] for x in xs]),
                          "share_premium_median_section4_reference_pp": med([x["share_premium_section4_reference_pp"] for x in xs])})
    pair_rows.sort(key=lambda r: -r["share_premium_median_pp"])
    pes = [x for x in read if x["price_equivalent_pct"] is not None]
    beyond = [x for x in pes if not x["price_equivalent_inside_tested_span"]]
    beyond_strict = [x for x in pes if not x["price_equivalent_price_inside_tested_prices"]]
    centres = {c: math.exp(sum(math.log(p) for p in v) / len(v)) for c, v in prices.items()}
    rel = {m: (d["models"][m]["reliability"]["split_half"] or {}).get("spearman_brown_mean") for m in every}
    kg = {m: d["models"][m]["known_groups"] for m in every}
    rep = [cc["repeat"] for m in models for cc in d["models"][m]["categories"].values() if cc.get("repeat") and cc["reads_specifications"]]
    rep_r = {}
    for m in models:
        xs, ys = [], []
        for cc in d["models"][m]["categories"].values():
            fr = (cc.get("repeat") or {}).get("mbbe_first_and_repeat")
            if fr and cc["reads_specifications"]:
                for x, y in fr.values():
                    xs.append(x)
                    ys.append(y)
        if len(xs) > 2:
            mx, my = statistics.mean(xs), statistics.mean(ys)
            sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
            sy = math.sqrt(sum((y - my) ** 2 for y in ys))
            rep_r[m] = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx and sy else None
    joint = {}
    for m in models:
        for cc in d["models"][m]["categories"].values():
            if not cc["reads_specifications"]:
                continue
            for t, (b, se) in (cc.get("joint_fit_shown_terms") or {}).items():
                j = joint.setdefault(t, {"cells": 0, "above_zero": 0, "below_zero": 0, "values": []})
                j["cells"] += 1
                j["above_zero"] += b - 1.96 * se > 0
                j["below_zero"] += b + 1.96 * se < 0
                j["values"].append(b)
    for j in joint.values():
        j["median"] = r1(med(j.pop("values")), 3)
    st_rows = stability_rows(d, every, excluded)
    s4_differ = [x for x in read if x["mbbe_section4_reference"] is not None and abs(x["mbbe_section4_reference"] - x["mbbe"]) > 1e-9]
    summary = {
        "source": a.numbers.replace("\\", "/"),
        "models": len(every), "models_included": len(models),
        "left_out": {"rule": rule, "models": excluded},
        "model_category_cells": sum(len(d["models"][m]["categories"]) for m in every),
        "cells_that_read_the_specifications": sum(bool(cc["reads_specifications"]) for m in every for cc in d["models"][m]["categories"].values()),
        "cells_that_read_the_specifications_included_models": sum(bool(cc["reads_specifications"]) for m in models for cc in d["models"][m]["categories"].values()),
        "reliability": {"by_model": {m: r1(r, 3) for m, r in rel.items()},
                        "pairs_by_model": {m: (kg[m] or {}).get("familiar_pairs") for m in every},
                        "median_included": r1(med([rel[m] for m in models]), 3),
                        "models_at_least_0_80_included": sum(1 for m in models if rel[m] is not None and rel[m] >= 0.8),
                        "models_at_least_0_80_all": sum(1 for m in every if rel[m] is not None and rel[m] >= 0.8),
                        "signal_share_median_included": r1(med([d["models"][m]["reliability"]["signal_share"] for m in models]), 3)},
        "familiar_cells_reading_included": len(read),
        "price_equivalent": {"defined": len(pes), "of": len(read),
                             "beyond_tested_prices": len(beyond_strict),
                             "beyond_tested_prices_share_pct": r1(100 * len(beyond_strict) / len(pes)) if pes else None,
                             "beyond_tested_prices_by_category": {c: sum(1 for x in beyond_strict if x["category"] == c) for c in sorted(prices)},
                             "beyond_tested_span": len(beyond),
                             "beyond_share_pct": r1(100 * len(beyond) / len(pes)) if pes else None,
                             "beyond_by_category": {c: sum(1 for x in beyond if x["category"] == c) for c in sorted(prices)},
                             "range_pct": [r1(min(x["price_equivalent_pct"] for x in pes), 0), r1(max(x["price_equivalent_pct"] for x in pes), 0)] if pes else None,
                             "tested_span_pct_by_category": span_pct,
                             "tested_prices_by_category": prices,
                             "room_above_the_centre_pct_by_category": {c: r1(100 * (max(p) / centres[c] - 1)) for c, p in prices.items()},
                             "room_below_the_centre_pct_by_category": {c: r1(100 * (min(p) / centres[c] - 1)) for c, p in prices.items()}},
        "rating_equivalent_defined": {"cells": sum(1 for x in read if x["rating_equivalent_stars"] is not None), "of": len(read)},
        "section4_reference": {"cells_that_differ": len(s4_differ),
                               "largest_difference_log_odds": r1(max((abs(x["mbbe_section4_reference"] - x["mbbe"]) for x in s4_differ), default=0), 3),
                               "cells_where_every_invented_name_is_claimed": sorted({f"{x['model']} | {x['category']}" for x in cells if x["reference_flag"]})},
        "unknown_to_model": [f"{x['model']} | {x['category']} | {x['brand']}" for x in cells if x["unknown_to_model"]],
        "unknown_to_model_reading_cells_included": [f"{x['model']} | {x['category']} | {x['brand']}" for x in read if x["unknown_to_model"]],
        "known_groups": {
            "familiar_mean_median_included": r1(med([kg[m]["familiar_mean_mbbe"] for m in models if kg[m]]), 3),
            "models_familiar_mean_above_zero": sum(1 for m in models if kg[m] and kg[m]["familiar_mean_mbbe"] > 0),
            "models_with_a_familiar_mean_interval": sum(1 for m in models if kg[m] and "familiar_mean_ci95" in kg[m]),
            "models_familiar_mean_interval_above_zero": (sum(1 for m in models if kg[m] and kg[m].get("familiar_mean_ci95", [0])[0] > 0)
                                                         if any(kg[m] and "familiar_mean_ci95" in kg[m] for m in models) else None),
            "models_above_the_invented_spread": sum(1 for m in models if kg[m] and kg[m]["familiar_mean_mbbe"] > kg[m]["invented_spread"][1]),
            "new_minus_corpus_invented": ({m: kg[m]["new_minus_corpus_invented"] for m in models if kg[m] and kg[m].get("new_minus_corpus_invented")}
                                          if any(kg[m] and "new_minus_corpus_invented" in kg[m] for m in models) else None)},
        "held_out_gain": held_out(d, models),
        "repeat": {"cells": len(rep), "kappa_median": r1(med([r["kappa"] for r in rep]), 3),
                   "same_pick_median": r1(med([r["same_pick"] for r in rep]), 3),
                   "mbbe_first_against_repeat_r_by_model": {m: r1(v, 3) for m, v in rep_r.items()},
                   "mbbe_first_against_repeat_r_median": r1(med(list(rep_r.values())), 3)},
        "stability_readable_cells": stability_summary(st_rows),
        "joint_fit_shown_terms": joint,
        "convergence": {k: v for k, v in d["convergence"].items() if isinstance(v, dict) and "cells" in v},
        "convergence_pooled_reliability": d["convergence"].get("pooled_reliability"),
        "discriminant": d["discriminant"],
        "independence_from_profiles": {"median_included": r1(med([(d["independence_from_profiles"].get(m) or {}).get("r") for m in models]), 3),
                                       "range_included": [r1(min(v["r"] for m, v in d["independence_from_profiles"].items() if m in models and v["r"] is not None), 2),
                                                          r1(max(v["r"] for m, v in d["independence_from_profiles"].items() if m in models and v["r"] is not None), 2)]},
        "corpus_table_prediction": d["corpus_table_prediction"].get("pooled"),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    for name, rows in (("brand_pairs.csv", pair_rows), ("cells.csv", cells), ("stability_cells.csv", st_rows),
                       ("felipe_brands.csv", [x for x in cells if x["brand"] in ("Apple", "Keurig", "Sony")])):
        with open(out_dir / name, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    lines = ["| Brand | Category | Models | Share premium, median (lowest, highest), points | Above zero | Below zero | "
             "Price equivalent, median per cent (models with one; of them beyond the tested prices) | Rating equivalent, median stars |",
             "|---|---|---|---|---|---|---|---|"]
    cat_name = {"tvs": "televisions", "running_shoes": "running shoes", "coffee_makers": "coffee makers"}
    for r in pair_rows:
        pe = r["price_equivalent_median_pct"]
        pe_s = "none" if pe is None else (f"{pe:.0f}" + ("" if r["price_equivalent_median_inside_tested_prices"] else " (beyond)"))
        lines.append(f"| {r['brand']} | {cat_name.get(r['category'], r['category'])} | {r['models']} | "
                     f"{r['share_premium_median_pp']:.1f} ({r['share_premium_min_pp']:.1f}, {r['share_premium_max_pp']:.1f}) | "
                     f"{r['models_above_zero']} | {r['models_below_zero']} | {pe_s} ({r['models_with_a_price_equivalent']}; "
                     f"{r['price_equivalents_beyond_tested_prices']}) | {r['rating_equivalent_median_stars']:.2f} |")
    (out_dir / "brand_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: summary[k] for k in ("models", "models_included", "left_out", "price_equivalent", "held_out_gain",
                                              "known_groups", "repeat", "stability_readable_cells")}, indent=1, default=str)[:6000])
    print("reliability", json.dumps(summary["reliability"]["median_included"]), summary["reliability"]["models_at_least_0_80_included"],
          "of", len(models))
    return 0


if __name__ == "__main__":
    sys.exit(main())
