"""The full measure's results for the models reached through one route: the Claude models through Anthropic's API, or the GPT models through Codex.
"""
import argparse
import gzip
import json
import pathlib
import sys

import numpy as np

PKG = REPO = pathlib.Path(__file__).resolve().parents[3]   # the package
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # the measure's code
import analyze_mbbe2 as M  # noqa: E402
DRAWS = 10   # the direct premium's choice sets for each brand at each premium, as the measure's prompts were made

ROUTES = {
    "claude": {"folder": "full1-claude-api", "title": "the Claude models (the Claude route)", "ran": "10:50 AM to 12:00 PM",
               "through": "through Anthropic's API",
               "note": "Fable 5.1 answered 800 lists a category and no direct price premium lists, because of the research "
                       "budget.",
               "names": {"claude-fable-5-1": "Fable 5.1", "claude-haiku-5-5": "Haiku 5.5", "claude-opus-5-5": "Opus 5.5",
                         "claude-sonnet-5-5": "Sonnet 5.5"}},
    "codex": {"folder": "full1-codex", "title": "the GPT models (the Codex route)", "ran": "10:50 to 11:07 AM",
              "through": "through Codex, inside Codex's own instructions",
              "note": ""
                      "the Codex route set.",
              "names": {"gpt-6.1-sol": "GPT-6.1 Sol", "gpt-6.2-sol": "GPT-6.2 Sol"}},
}
CATS = {"coffee_makers": "coffee makers", "running_shoes": "running shoes", "tvs": "televisions"}
WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
OUT = NAMES = None  # set by main() from the route


def every(n):
    return "both" if n == 2 else f"all {WORD.get(n, n)}"


def separation(models):
    items = {}
    for line in gzip.open(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz", "rt", encoding="utf-8"):
        it = json.loads(line)
        if it.get("version") == "main" and it["cell"] == "shown":
            items[it["id"]] = it
    ans = M.load_answers(str(PKG / "study2b-how-much-a-familiar-brand-is-worth/data/measure/api-answers.jsonl.gz"))
    ans = ans[ans.model.isin(models) & ans.id.isin(items)]
    out = {}
    for model, g in ans.groupby("model"):
        per = {}
        for i, L in zip(g.id, g.letter):
            if L in items[i]["products"]:
                per.setdefault(items[i]["category"], []).append((items[i], L))
        for cat, rows in per.items():
            def worst(key):
                mixed = [(it, L) for it, L in rows if len({key(p) for p in it["products"].values()}) > 1
                         and any(key(p) == 0 for p in it["products"].values())]
                return [sum(key(it["products"][L]) == 0 for it, L in mixed), len(mixed)]
            out.setdefault(model, {})[cat] = {
                "lowest_rating_recommended": worst(lambda p: {4.2: 0, 4.4: 1, 4.6: 2}[p["rating"]]),
                "worst_attribute_level_recommended": [worst(lambda p, a=a: p["levels"][a]) for a in range(3)]}
    return out


def main():
    global OUT, NAMES
    ap = argparse.ArgumentParser()
    ap.add_argument("--route", choices=sorted(ROUTES), default="claude")
    a = ap.parse_args()
    R = ROUTES[a.route]
    OUT, NAMES = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure" / R["folder"], R["names"]
    r = json.load(open(OUT / "numbers.json", encoding="utf-8"))
    models = sorted(r["models"])
    sep = separation(models)
    (OUT / "separation.json").write_text(json.dumps(sep, indent=1) + "\n", encoding="utf-8", newline="\n")
    cells = sorted({(c, b) for m in models for c, x in r["models"][m].items() for b in x["main"]["brands"]})
    n_all = every(len(models))

    def u(m, c, b):
        return r["models"][m][c]["main"]["brands"][b]
    L = []
    w = L.append
    w(f"# The full measure on {R['title']}")
    w("")
    w(""
      f"(analyze_mbbe2.py on {', '.join(NAMES[m] for m in models)}, 1,000 bootstrap draws, run on 22 November 2026 from "
      ""
      "over every model that responds, the open panel included.")
    w("")
    w("## What was analysed")
    w("")
    lists = {m: sum(x["main"]["lists"] for x in r["models"][m].values()) for m in models}
    w(f"The main version with brand names, {R['through']}: " + "; ".join(
        f"{NAMES[m]} {lists[m]:,} lists" for m in models) + f". {R['note']} Every model answered every recognition "
      "question on the fictitious names with no, so each reference is every fictitious name of its category. The stop "
      "rules are clean in every cell (jmr-2026/results/measure/full1-stop-rules/).")
    w("")
    w(f"## Over the {WORD.get(len(models), len(models))} models")
    w("")
    above_all = [cb for cb in cells if all(u(m, *cb)["value_ci95"][0] > 0 for m in models)]
    below_all = [cb for cb in cells if all(u(m, *cb)["value_ci95"][1] < 0 for m in models)]
    above = {m: sum(u(m, *cb)["value_ci95"][0] > 0 for cb in cells) for m in models}
    below = {m: sum(u(m, *cb)["value_ci95"][1] < 0 for cb in cells) for m in models}
    w(f"Of the {len(cells)} pairs of a brand and a category, {len(above_all)} have a value above zero by its 95 percent "
      f"interval in {n_all} models, and {len(below_all)} have one below zero in {n_all}. In each model, "
      + ", ".join(f"{above[m]} are above zero and {below[m]} below ({NAMES[m]})" for m in models) + ".")
    w("")
    w(f"The pairs above zero in {n_all} models: " + "; ".join(f"{b} ({CATS.get(c, c)})" for c, b in above_all) + ".")
    w("")
    w("## How the models differ")
    w("")
    w("| Model | Lists | Values, lowest to highest (log-odds) | Mean share premium (points) | Price premium beyond the tested prices | Reliability within category (Spearman-Brown of the mean half correlation) |")
    w("|---|---|---|---|---|---|")
    for m in models:
        vals = [u(m, *cb)["value"] for cb in cells]
        sp = np.mean([u(m, *cb)["share_premium_pp"] for cb in cells])
        beyond = sum(u(m, *cb).get("price_premium_inside_tested_prices") is False for cb in cells)
        pr = r["pooled_reliability"][m]
        w(f"| {NAMES[m]} | {lists[m]:,} | {min(vals):.2f} to {max(vals):.2f} | {sp:.1f} | {beyond} of {len(cells)} | "
          f"{pr['spearman_brown_of_the_mean']:.2f} |")
    w("")
    w("Each category's mean half correlation, and its Spearman-Brown value, for the Web Appendix (negative values as "
      "they are):")
    w("")
    cats = sorted(r["models"][models[0]])
    w("| Model | " + " | ".join(CATS.get(c, c) for c in cats) + " |")
    w("|---|" + "---|" * len(cats))
    for m in models:
        by = r["pooled_reliability"][m]["by_category"]
        w(f"| {NAMES[m]} | " + " | ".join(f"{by[c]['half_correlation']:.2f} ({by[c]['spearman_brown']:.2f})" for c in cats) + " |")
    w("")
    rel_ok = [cb for cb in cells if all("rating_equivalent_stars" in u(m, *cb) for m in models)]
    re = {m: np.array([u(m, *cb)["rating_equivalent_stars"] for cb in rel_ok]) for m in models}
    w(f"The rating equivalents, over the {len(rel_ok)} pairs where {n_all} models have one (the next section gives "
      "the cells where a model has none), correlate between the models as follows.")
    w("")
    w("| | " + " | ".join(NAMES[m] for m in models) + " |")
    w("|---|" + "---|" * len(models))
    for a in models:
        w(f"| {NAMES[a]} | " + " | ".join(f"{np.corrcoef(re[a], re[b])[0, 1]:.2f}" for b in models) + " |")
    w("")
    w("Mean rating equivalent over those pairs: " + "; ".join(f"{NAMES[m]} {re[m].mean():.3f} stars" for m in models) + ".")
    w("")
    w("The direct premium is the premium at which the brand's share of five products alike in every specification "
      "falls to one in five, with the four rivals under the category's other names at the brand's band centre.")
    w("")
    for m in models:
        ok = [(u(m, *cb).get("price_premium_pct"), (u(m, *cb).get("direct_premium") or {}).get("premium_at_one_in_five"))
              for cb in cells]
        ok = [(x, y) for x, y in ok if x is not None and y is not None]
        if ok:
            xs, ys = zip(*ok)
            sh = {k: np.mean([u(m, *cb)["direct_premium"]["share_by_premium"][k] for cb in cells]) for k in ("-0.10", "+0.00", "+0.10")}
            w(f"- {NAMES[m]}: the brand's mean share of the five is {100 * sh['-0.10']:.0f} percent when it costs 10 "
              f"percent less than its rivals, {100 * sh['+0.00']:.0f} percent at the same price and {100 * sh['+0.10']:.0f} "
              f"percent when it costs 10 percent more. The direct premium has a median of {np.median(ys):.1f} percent "
              f"over {len(ok)} pairs, against a median price premium of {np.median(xs):.1f} percent from the main "
              f"version's fit; the two correlate at {np.corrcoef(xs, ys)[0, 1]:.2f} across pairs.")
    w("")
    w("")
    w("")
    def times(h):
        return "never" if h == 0 else "once" if h == 1 else f"{h} times"
    marked = [(m, c, r["models"][m][c]["main"]["lowest_rating_recommended"]) for m in models for c in sorted(r["models"][m])
              if any("rating_equivalent_not_estimable" in x for x in r["models"][m][c]["main"]["brands"].values())]
    marked_cells = {(m, c) for m, c, _ in marked}
    others = [sep[m][c]["lowest_rating_recommended"] for m in models for c in sep[m] if (m, c) not in marked_cells]
    here = ("Here: " + "; ".join(f"{NAMES[m]} in {CATS.get(c, c)}, 4.2 stars recommended {times(x['times'])} in "
                                 f"{x['lists_offering_that_choice']:,} lists" for m, c, x in marked) + ". In the other cells"
            if marked else "No cell of these models falls under the rule; in every cell")
    w("1. **The rating equivalent is not reported where it cannot be estimated.** Where a model recommends the lowest "
      "rating beside a higher-rated product in under 1 percent of the lists that offer that choice, the coefficient "
      "for one star has no finite estimate or a very large one, which would push every brand's rating equivalent to "
      "zero. Such a cell has no rating equivalent, is marked with the count, and is compared between models on the "
      f"price premium. {here} the models recommended the lowest rating in {100 * min(h / n for h, n in others):.0f} "
      f"to {100 * max(h / n for h, n in others):.0f} percent of such lists.")
    w("2. **Reliability within a category** is the mean of the split-half correlations over the category's familiar "
      "brands and that mean's Spearman-Brown value, and a model's is the Spearman-Brown value of the mean of its "
      "categories' half correlations (the last column of the first table). "
      + ("With four to six brands in a category, some categories' half correlations are negative; the table above shows "
         "them as they are." if any(v["half_correlation"] < 0 for m in models
                                    for v in r["pooled_reliability"][m]["by_category"].values())
         else "No category's half correlation is negative for these models."))
    dps = [u(m, *cb)["direct_premium"]["premium_at_one_in_five"] for m in models for cb in cells
           if (u(m, *cb).get("direct_premium") or {}).get("premium_at_one_in_five") is not None]
    with_dp = [m for m in models if any((u(m, *cb).get("direct_premium") or {}).get("share_by_premium") for cb in cells)]
    extreme = all(np.mean([u(m, *cb)["direct_premium"]["share_by_premium"]["-0.10"] for cb in cells]) == 1.0
                  and np.mean([u(m, *cb)["direct_premium"]["share_by_premium"]["+0.10"] for cb in cells]) == 0.0 for m in with_dp)
    w("3. **The direct premium's resolution.** The brand's price differs from its four identical rivals' in steps of 10 "
      "percent" + (", and the models recommend the brand's product in every draw when it costs 10 percent less and in "
                   "none when it costs 10 percent more (the shares above)" if extreme else
                   " (the shares above give each model's choices at each step)")
      + f". Here every crossing of one in five lies from {min(dps):.1f} to {max(dps):.1f} percent ({len(dps)} pairs). "
      "The direct premium tells whether a model pays more than 10 percent for the brand, not where under 10 percent "
      "the premium lies, and this is why it agrees weakly with the price premium. The design is kept: the research key "
      "has about 8 USD left, and a finer grid would make the routes two designs.")
    w("")
    attr = {json.load(open(p, encoding="utf-8"))["category"]: [x["name"] for x in json.load(open(p, encoding="utf-8"))["attributes"]]
            for p in (PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/categories").glob("*.json")}
    never = sorted({(c, attr[c][k]) for m in models for c, s in sep[m].items()
                    for k, (h, n) in enumerate(s["worst_attribute_level_recommended"]) if h == 0 and n > 0})
    w("The attributes whose worst level a model never recommends beside a product with a better level: "
      + "; ".join(f"{name} in {CATS.get(c, c)}" for c, name in never)
      + " (separation.json, with each model's counts). These remove those products from the choice but leave every "
      "brand's value, price premium and rating equivalent estimable.")
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    # summary.json: every figure that the text gives, for the Web Appendix's number markers
    corr = [float(np.corrcoef(re[a], re[b])[0, 1]) for i, a in enumerate(models) for b in models[i + 1:]]
    per = {}
    for m in models:
        vals = [u(m, *cb)["value"] for cb in cells]
        dp = [(u(m, *cb).get("price_premium_pct"), (u(m, *cb).get("direct_premium") or {}).get("premium_at_one_in_five"))
              for cb in cells]
        dp = [(x, y) for x, y in dp if x is not None and y is not None]
        per[m] = {"name": NAMES[m], "lists": lists[m], "above_zero": above[m], "below_zero": below[m],
                  "value_lowest": min(vals), "value_highest": max(vals),
                  "mean_share_premium_pp": float(np.mean([u(m, *cb)["share_premium_pp"] for cb in cells])),
                  "price_premium_beyond_tested": sum(u(m, *cb).get("price_premium_inside_tested_prices") is False for cb in cells),
                  "reliability": r["pooled_reliability"][m]["spearman_brown_of_the_mean"],
                  "mean_half_correlation": r["pooled_reliability"][m]["mean_half_correlation"],
                  "mean_rating_equivalent_stars": float(re[m].mean())}
        allp = [u(m, *cb)["price_premium_pct"] for cb in cells if "price_premium_pct" in u(m, *cb)]
        insp = [u(m, *cb)["price_premium_pct"] for cb in cells if u(m, *cb).get("price_premium_inside_tested_prices") is True]
        per[m].update({"price_premium_pairs": len(allp), "price_premium_median_pct_all_pairs": float(np.median(allp)) if allp else None,
                       "price_premium_inside_tested": len(insp),
                       "price_premium_median_pct_inside_tested": float(np.median(insp)) if insp else None,
                       # each brand appears in DRAWS choice sets at each premium
                       "direct_premium_choice_sets_at_each_premium": len(cells) * DRAWS if dp else 0})
        if dp:
            xs, ys = zip(*dp)
            sh = {k: float(np.mean([u(m, *cb)["direct_premium"]["share_by_premium"][k] for cb in cells])) for k in ("-0.10", "+0.00", "+0.10")}
            per[m].update({"direct_share_10_below_pct": 100 * sh["-0.10"], "direct_share_same_price_pct": 100 * sh["+0.00"],
                           "direct_share_10_above_pct": 100 * sh["+0.10"], "direct_premium_median_pct": float(np.median(ys)),
                           "price_premium_median_pct": float(np.median(xs)),
                           "direct_with_price_premium_r": float(np.corrcoef(xs, ys)[0, 1])})
    summary = {"pairs": len(cells), "above_zero_in_all": len(above_all), "below_zero_in_all": len(below_all),
               "pairs_with_rating_equivalent_in_all": len(rel_ok), "rating_equivalent_r_lowest": min(corr),
               "rating_equivalent_r_highest": max(corr), "direct_premium_lowest_pct": min(dps),
               "direct_premium_highest_pct": max(dps), "direct_premium_pairs": len(dps),
               "lowest_rating_share_other_categories_lowest_pct": 100 * min(h / n for h, n in others),
               "lowest_rating_share_other_categories_highest_pct": 100 * max(h / n for h, n in others),
               "rating_rule_cells": [{"model": NAMES[m], "category": c, **x} for m, c, x in marked], "models": per}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT / "RESULTS.md", "and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
