"""The full measure over every model that answered: RESULTS.md
and summary.json from analyze_mbbe2.py's numbers.json, the result over every model first, then the three groups of
models (Claude, GPT, open weights), then each model.

    A model under the 90 percent rule (numbers.json's left_out) has its
own row and enters no estimate over models.
"""
import argparse
from collections import Counter
import ast
import gzip
import json
import math
import pathlib
import sys

import numpy as np

PKG = REPO = pathlib.Path(__file__).resolve().parents[3]   # the package
GROUPS = {"claude": "the Claude models", "gpt": "the GPT models", "open": "the models with open weights"}
CATS = {"coffee_makers": "coffee makers", "running_shoes": "running shoes", "tvs": "televisions", "earbuds": "wireless earbuds",
        "headphones": "over-ear headphones"}


def names():
    """Model key -> printed name, from the figure and table code's list (exhibits/code/model_names.json)."""
    return json.loads((PKG / "exhibits" / "code" / "model_names.json").read_text(encoding="utf-8"))


def group_of(model):
    m = model.lower()
    return "claude" if m.startswith("claude") else "gpt" if m.startswith("gpt-6") or m.startswith("gpt6") else "open"


def load(path):
    p = pathlib.Path(path)
    opener = gzip.open if p.name.endswith(".gz") else open
    with opener(p, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def _bad(v):
    return isinstance(v, float) and not math.isfinite(v)


def strict(x):
    """Strict JSON for the explorer's JSON.parse: a non-finite number, an
    infinite price premium or interval bound, becomes null with a sibling flag. In a dict, a key k whose value is
    infinite becomes null with k_unbounded ("upper" or "lower"; "undefined" for NaN); an interval [lo, hi] with an
    infinite bound becomes [lo, null] with k_upper_unbounded: true (or [null, hi] with k_lower_unbounded: true). A
    non-finite number elsewhere in a list becomes null."""
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if _bad(v):
                out[k] = None
                out[f"{k}_unbounded"] = "undefined" if math.isnan(v) else "upper" if v > 0 else "lower"
            elif isinstance(v, list) and len(v) == 2 and any(_bad(e) for e in v) \
                    and all(e is None or isinstance(e, (int, float)) for e in v):
                out[k] = [None if _bad(e) else e for e in v]
                if _bad(v[0]):
                    out[f"{k}_lower_unbounded"] = True
                if _bad(v[1]):
                    out[f"{k}_upper_unbounded"] = True
            else:
                out[k] = strict(v)
        return out
    if isinstance(x, list):
        return [None if _bad(e) else strict(e) for e in x]
    return None if _bad(x) else x


def dumps(x):
    """json.dumps of strict(x), refusing any non-finite number that strict() missed (allow_nan=False)."""
    return json.dumps(strict(x), indent=1, allow_nan=False)


def pair_summary(om, g):
    """For one group (or 'all'), each pair's mean share premium with its interval, the median price premium over the
    models inside the tested prices, and the counts."""
    out = {}
    for key, entry in om.items():
        e = entry.get(g)
        if not e:
            continue
        sp, pp = e["share_premium_pp"], e["price_premium"]
        out[key] = {"models": e["models"], "share_premium_mean_pp": sp["mean"], "share_premium_mean_ci95": sp["mean_ci95"],
                    "share_premium_median_pp": sp["median"], "share_premium_median_ci95": sp["median_ci95"],
                    "models_inside_tested_prices": pp["models_inside_tested_prices"],
                    "models_beyond_tested_prices": pp["models_beyond_tested_prices"],
                    "models_without_a_price_premium": pp["models_without_a_price_premium"],
                    "price_premium_median_pct": (pp.get("pct") or {}).get("median"),
                    "price_premium_median_ci95": (pp.get("pct") or {}).get("median_ci95"),
                    "price_premium_median_usd": (pp.get("usd") or {}).get("median"),
                    "band_centre_usd": pp["band_centre_usd"]}
    return out


def counts(pairs):
    above = sorted(k for k, v in pairs.items() if v["share_premium_mean_ci95"][0] > 0)
    below = sorted(k for k, v in pairs.items() if v["share_premium_mean_ci95"][1] < 0)
    means = [v["share_premium_mean_pp"] for v in pairs.values()]
    # the dollar summary as tables.py's usdsum computes it for a route: over the pairs, the median of the group's
    # median dollar premium over its models inside the tested prices, with the pairs that have one and those that do not
    usd = [v["price_premium_median_usd"] for v in pairs.values() if v["price_premium_median_usd"] is not None]
    top = max(pairs, key=lambda k: pairs[k]["share_premium_mean_pp"]) if pairs else None
    low = min(pairs, key=lambda k: pairs[k]["share_premium_mean_pp"]) if pairs else None
    return {"pairs": len(pairs), "above_zero": len(above), "below_zero": len(below), "above_zero_pairs": above,
            "below_zero_pairs": below, "median_of_mean_share_premium_pp": float(np.median(means)) if means else None,
            "highest": top, "highest_pp": pairs[top]["share_premium_mean_pp"] if top else None,
            "lowest": low, "lowest_pp": pairs[low]["share_premium_mean_pp"] if low else None,
            "usd_median_over_pairs": float(np.median(usd)) if usd else None, "usd_pairs": len(usd),
            "usd_pairs_none_inside": len(pairs) - len(usd)}


def per_model(r, stop, nm):
    out = {}
    for m, mres in sorted(r["models"].items()):
        us = [(c, b, u) for c, x in mres.items() if "main" in x for b, u in x["main"]["brands"].items()]
        insp = [u["price_premium_pct"] for _, _, u in us if u.get("price_premium_inside_tested_prices") is True]
        e = {"name": nm.get(m, m), "group": group_of(m), "lists": sum(x["main"]["lists"] for x in mres.values() if "main" in x),
             "pairs": len(us), "above_zero": sum(u["value_ci95"][0] > 0 for *_, u in us),
             "below_zero": sum(u["value_ci95"][1] < 0 for *_, u in us),
             "mean_share_premium_pp": float(np.mean([u["share_premium_pp"] for *_, u in us])) if us else None,
             "reliability": r["pooled_reliability"].get(m, {}).get("spearman_brown_of_the_mean"),
             "price_premium_inside_tested": len(insp),
             "price_premium_median_pct_inside_tested": float(np.median(insp)) if insp else None,
             "read_pct": r.get("choice_items_read", {}).get(m, {}).get("read_pct"),
             "declines": r.get("choice_items_read", {}).get(m, {}).get("declines"),
             "decline_pct": r.get("choice_items_read", {}).get(m, {}).get("decline_pct"),
             "left_out": m in r.get("left_out", {}).get("models", {}),
             # categories in which the model follows fewer than two attributes (ANALYSIS-PLAN-2.md): reported
             # alone, left out of every estimate over models
             "categories_left_out": [CATS.get(c["category"], c["category"]) for c in r.get("cells_left_out", [])
                                     if c["model"] == m]}
        gone = {c["category"] for c in r.get("cells_left_out", []) if c["model"] == m}
        halves = [v["half_correlation"] for c, v in r["pooled_reliability"].get(m, {}).get("by_category", {}).items()
                  if c not in gone and v.get("half_correlation") is not None]
        mh = float(np.mean(halves)) if halves else None
        e["reliability_kept_categories"] = (2 * mh / (1 + mh) if mh > -1 else -1.0) if mh is not None else None
        e["kept_categories"] = len(halves)
        # the rows of the main text's Table ms-checks, as claude_route_results.py computes them for the Claude route
        vals = [u["value"] for *_, u in us]
        res_ = [u["rating_equivalent_stars"] for *_, u in us if u.get("rating_equivalent_stars") is not None]
        allp = [u["price_premium_pct"] for *_, u in us if u.get("price_premium_pct") is not None]
        e.update({"value_lowest": min(vals) if vals else None, "value_highest": max(vals) if vals else None,
                  "mean_rating_equivalent_stars": float(np.mean(res_)) if res_ else None, "rating_equivalent_pairs": len(res_),
                  "price_premium_beyond_tested": sum(u.get("price_premium_inside_tested_prices") is False for *_, u in us),
                  "price_premium_pairs": len(allp),
                  "price_premium_median_pct_all_pairs": float(np.median(allp)) if allp else None})
        dp = [(u.get("price_premium_pct"), (u.get("direct_premium") or {}).get("premium_at_one_in_five"),
               ((u.get("direct_premium") or {}).get("share_by_premium") or {}).get("+0.00")) for *_, u in us]
        same = [s for *_, s in dp if s is not None]
        cross = [d for _, d, _ in dp if d is not None]
        both = [(x, d) for x, d, _ in dp if x is not None and d is not None]
        e["direct_premium_brands"] = len(same)
        if same:
            e.update({"direct_share_same_price_pct": 100 * float(np.mean(same)),
                      "direct_premium_median_pct": float(np.median(cross)) if cross else None,
                      "direct_with_price_premium_r": float(np.corrcoef(*zip(*both))[0, 1]) if len(both) > 2 else None})
        if stop and m in stop:
            pc = [v["main_price_coefficient"] for v in stop[m].values() if v.get("main_price_coefficient")]
            e.update({"price_coefficient_below_zero": sum(x[2] < 0 for x in pc),
                      "price_coefficient_above_zero": sum(x[1] > 0 for x in pc), "categories_checked": len(pc),
                      "top_position_share_highest": max(v["top_position_share"] for v in stop[m].values()),
                      "top_letter_share_highest": max(v["top_letter_share"] for v in stop[m].values()),
                      "stop_rule_flags": sorted({f for v in stop[m].values() for f in v.get("flags", [])})})
        out[m] = e
    return out


def unchecked(r, stop, nm):
    out = []
    for m, mres in sorted(r["models"].items()):
        for c, v in sorted(mres.items()):
            chk = (v.get("main") or {}).get("specifications_check")
            if chk is not None and chk.get("attributes_followed") is None:
                s = (stop or {}).get(m, {}).get(c, {})
                n = s.get("responses")
                out.append({"model": nm.get(m, m), "category": CATS.get(c, c), "responses": n,
                            "with_a_letter": None if n is None else n - s.get("without_a_letter", 0)})
    return out


def label(key):
    cat, br = key.split(" | ")
    return f"{br} ({CATS.get(cat, cat.replace('_', ' '))})"


def checks(stop, pm, models, nm):
    """The checks before estimation over a set of models (the Web Appendix's part on the open models): the main price
    coefficient's sign in each model and category, the largest share of one display position and of one letter, the
    cells that a stop rule flagged, and the declines."""
    cells = [(m, c, v) for m in models if stop and m in stop for c, v in stop[m].items()]
    pc = [(v["main_price_coefficient"], m, c) for m, c, v in cells if v.get("main_price_coefficient")]
    if not pc:
        return None
    lo = min(pc, key=lambda t: t[0][0])
    hi = max(pc, key=lambda t: t[0][0])
    pos = max(cells, key=lambda t: t[2]["top_position_share"])
    let = max(cells, key=lambda t: t[2]["top_letter_share"])
    dec = [(pm[m].get("decline_pct") or 0.0, m) for m in models]
    top_dec = max(dec)
    cat = lambda c: CATS.get(c, c.replace("_", " "))  # noqa: E731
    return {"models": len({m for m, _, _ in cells}), "cells": len(pc),
            "price_coefficient_below_zero_cells": sum(x[2] < 0 for x, _, _ in pc),
            "price_coefficient_above_zero_cells": sum(x[1] > 0 for x, _, _ in pc),
            "price_coefficient_neither_cells": sum(x[2] >= 0 and x[1] <= 0 for x, _, _ in pc),
            "models_with_every_price_coefficient_below_zero": sum(
                all(stop[m][c]["main_price_coefficient"][2] < 0 for c in stop[m]) for m in {m for m, _, _ in cells}),
            "price_coefficient_above_zero_list": [f"{nm.get(m, m)} in {cat(c)}" for x, m, c in pc if x[1] > 0],
            "price_coefficient_lowest": lo[0][0], "price_coefficient_lowest_at": f"{nm.get(lo[1], lo[1])}, {cat(lo[2])}",
            "price_coefficient_highest": hi[0][0], "price_coefficient_highest_at": f"{nm.get(hi[1], hi[1])}, {cat(hi[2])}",
            "top_position_share_highest_pct": 100 * pos[2]["top_position_share"],
            "top_position_share_highest_at": f"{nm.get(pos[0], pos[0])}, {cat(pos[1])}",
            "top_letter_share_highest_pct": 100 * let[2]["top_letter_share"],
            "top_letter_share_highest_at": f"{nm.get(let[0], let[0])}, {cat(let[1])}",
            "cells_flagged": [{"model": nm.get(m, m), "category": cat(c), "flags": v["flags"]} for m, c, v in cells if v.get("flags")],
            "decline_pct_highest": top_dec[0], "decline_pct_highest_at": nm.get(top_dec[1], top_dec[1]),
            "models_with_a_decline": sum(d > 0 for d, _ in dec),
            # for the Web Appendix's sentences: the combinations with a main price coefficient above zero by category,
            # and the flagged combinations by rule, with the models that each rule flagged
            "price_coefficient_above_zero_by_category": dict(Counter(cat(c) for x, m, c in pc if x[1] > 0)),
            "flag_counts": dict(Counter(f for _, _, v in cells for f in v.get("flags", []))),
            "flag_models": {f: sorted({nm.get(m, m) for m, _, v in cells if f in v.get("flags", [])})
                            for f in sorted({f for _, _, v in cells for f in v.get("flags", [])})}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numbers", required=True)
    ap.add_argument("--stop")
    ap.add_argument("--counts")
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="preliminary", choices=["preliminary", "final"])
    a = ap.parse_args()
    r = load(a.numbers)
    stop = load(a.stop) if a.stop else None
    nm = names()
    om = r["over_models"]
    left = r.get("left_out", {}).get("models", {})
    pm = per_model(r, stop, nm)
    kept = [m for m in pm if not pm[m]["left_out"]]
    by = {g: pair_summary(om, g) for g in ("all", "claude", "gpt", "open")}
    cnt = {g: counts(v) for g, v in by.items()}
    ngr = {g: sum(group_of(m) == g for m in kept) for g in GROUPS}
    L = []
    w = L.append
    w("# The full measure over every model that answered (Study 2b)")
    w("")
    w(""
      f"{r.get('_meta', {}).get('draws', '?')} bootstrap draws). This is the {a.label} estimate"
      + (": not every open model had answered every item when it ran (answer-counts.txt)." if a.label == "preliminary" else "."))
    w("")
    w("## Models")
    w("")
    w(f"{len(pm)} models answered: {ngr['claude']} Claude models, {ngr['gpt']} GPT models and {ngr['open']} models with open "
      "weights enter the estimates over models"
      + (f"; {len(left)} left out under the 90 percent rule: "
         + "; ".join(f"{nm.get(m, m)} ({v['read_pct']:.1f} percent of its choice responses that are not declines read)" for m, v in sorted(left.items()))
         if left else "; no model falls under the 90 percent rule") + ".")
    cl = r.get("cells_left_out", [])
    w("")
    w(f"Categories left out of the estimates over models because the model follows fewer than two attributes there "
      f"({len(cl)} of {sum(len(x) for x in r['models'].values())}): "
      + ("; ".join(f"{nm.get(m, m)} in {', '.join(e['categories_left_out'])}" for m, e in sorted(pm.items()) if e['categories_left_out'])
         if cl else "none") + ".")
    uc = unchecked(r, stop, nm)
    for m, e in pm.items():  # each model's unchecked categories, for the open models' table
        e["categories_unchecked"] = [x["category"] for x in uc if x["model"] == e["name"]]
    w("")
    w(f"Categories whose check of the specifications could not be made (fewer than 50 lists with a letter of a listed "
      f"product), which stay in the estimates over models ({len(uc)}): "
      + ("; ".join(f"{x['model']} in {x['category']} ({x['with_a_letter']} of {x['responses']} responses with a letter)"
                   for x in uc) if uc else "none") + ".")
    kept_models = [m for m in pm if not pm[m]["left_out"]]
    rel = {g: [pm[m]["reliability_kept_categories"] for m in kept_models if (g == "all" or pm[m]["group"] == g)
               and pm[m]["reliability_kept_categories"] is not None] for g in ("all",) + tuple(GROUPS)}
    rel_median = {g: float(np.median(v)) if v else None for g, v in rel.items()}
    w("")
    w("Median reliability within category over the models, each model's over its kept categories only: "
      + "; ".join(f"{'every model' if g == 'all' else GROUPS[g]} {v:.2f}" for g, v in rel_median.items() if v is not None) + ".")
    if a.counts:
        w("")
        w("Responses for each model (answer-counts.txt): " + pathlib.Path(a.counts).read_text(encoding="utf-8").strip().replace("\n", "; ") + ".")
    w("")
    c = cnt["all"]
    w("## Over every model")
    w("")
    w(f"Of the {c['pairs']} pairs of a brand and a category, {c['above_zero']} have a mean share premium over the "
      f"{len(kept)} models above zero by its 95 percent interval, and {c['below_zero']} have one below zero. The median "
      f"pair's mean share premium is {c['median_of_mean_share_premium_pp']:.1f} points; the highest is "
      f"{label(c['highest'])}, {c['highest_pp']:.1f} points, and the lowest {label(c['lowest'])}, {c['lowest_pp']:.1f}.")
    w("")
    w("| Brand (category) | Mean share premium, points (95% CI) | Median share premium | Median price premium, percent, over the models inside the tested prices (models inside / beyond / without) | In dollars at the band centre |")
    w("|---|---|---|---|---|")
    for k, v in sorted(by["all"].items(), key=lambda kv: -kv[1]["share_premium_mean_pp"]):
        ci = v["share_premium_mean_ci95"]
        pp = "none inside" if v["price_premium_median_pct"] is None else f"{v['price_premium_median_pct']:.0f}"
        usd = "" if v["price_premium_median_usd"] is None else f"{v['price_premium_median_usd']:.0f} of {v['band_centre_usd']:.0f}"
        w(f"| {label(k)} | {v['share_premium_mean_pp']:.1f} ({ci[0]:.1f} to {ci[1]:.1f}) | {v['share_premium_median_pp']:.1f} | "
          f"{pp} ({v['models_inside_tested_prices']} / {v['models_beyond_tested_prices']} / {v['models_without_a_price_premium']}) | {usd} |")
    w("")
    w("## By group of models")
    w("")
    for g, title in GROUPS.items():
        c = cnt[g]
        if c["pairs"]:
            w(f"- Over {title} ({ngr[g]}): {c['above_zero']} of {c['pairs']} pairs above zero and {c['below_zero']} below "
              f"zero by the mean's interval; median pair {c['median_of_mean_share_premium_pp']:.1f} points; highest "
              f"{label(c['highest'])} ({c['highest_pp']:.1f}).")
    w("")
    w("| Brand (category) | " + " | ".join(f"Mean share premium, {t}" for t in GROUPS.values()) + " |")
    w("|---|" + "---|" * len(GROUPS))
    for k in sorted(by["all"], key=lambda k: -by["all"][k]["share_premium_mean_pp"]):
        w(f"| {label(k)} | " + " | ".join(f"{by[g][k]['share_premium_mean_pp']:.1f}" if k in by[g] else "" for g in GROUPS) + " |")
    w("")
    w("## Each model")
    w("")
    w("| Model | Group | Lists with brand names (main version) | Choice responses read, percent of those that are not declines (declines, percent of all) | Pairs above / below zero | Mean share premium (points) | Reliability | Median price premium inside the tested prices (pairs) | Main price coefficient below / above zero (categories) | Highest share of one position / one letter |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for m, e in sorted(pm.items(), key=lambda kv: (kv[1]["group"], kv[1]["name"])):
        ppm = "none" if e["price_premium_median_pct_inside_tested"] is None else f"{e['price_premium_median_pct_inside_tested']:.0f} ({e['price_premium_inside_tested']})"
        pc = f"{e['price_coefficient_below_zero']} / {e['price_coefficient_above_zero']} ({e['categories_checked']})" if "categories_checked" in e else ""
        pos = f"{100 * e['top_position_share_highest']:.0f} / {100 * e['top_letter_share_highest']:.0f}" if "top_position_share_highest" in e else ""
        rel = "" if e["reliability"] is None else f"{e['reliability']:.2f}"
        w(f"| {e['name']}{' (left out)' if e['left_out'] else ''} | {e['group']} | {e['lists']:,} | {e['read_pct']} ({e['decline_pct']}) | "
          f"{e['above_zero']} / {e['below_zero']} | {e['mean_share_premium_pp']:.1f} | {rel} | {ppm} | {pc} | {pos} |")
    w("")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    for c in cnt.values():  # readable names of the highest and lowest pairs, for the Web Appendix's markers
        c["highest_label"] = label(c["highest"]) if c["highest"] else None
        c["lowest_label"] = label(c["lowest"]) if c["lowest"] else None
    chk = {g: checks(stop, pm, [m for m in pm if g == "all" or pm[m]["group"] == g], nm) for g in ("all",) + tuple(GROUPS)}
    cols = {}
    for g in ("all",) + tuple(GROUPS):
        ms_ = [pm[m] for m in pm if not pm[m]["left_out"] and (g == "all" or pm[m]["group"] == g)]
        col = {"models": len(ms_), "above_zero": cnt[g]["above_zero"], "below_zero": cnt[g]["below_zero"],
               "pairs": cnt[g]["pairs"]}
        for k in ("lists", "value_lowest", "value_highest", "mean_share_premium_pp", "mean_rating_equivalent_stars",
                  "reliability_kept_categories", "price_premium_beyond_tested", "price_premium_median_pct_all_pairs",
                  "direct_share_same_price_pct", "direct_premium_median_pct", "direct_with_price_premium_r"):
            v = [e[k] for e in ms_ if e.get(k) is not None]
            col[f"{k}_median"] = float(np.median(v)) if v else None
            col[f"{k}_models"] = len(v)
        cols[g] = col
    summary = {"label": a.label, "models": len(pm), "models_in_estimates": len(kept), "models_by_group": ngr,
               "models_left_out": left, "models_left_out_names": [nm.get(m, m) for m in sorted(left)],
               "cells_left_out": len(r.get("cells_left_out", [])), "cells": sum(len(x) for x in r["models"].values()),
               "cells_unchecked": len(uc), "cells_unchecked_list": uc,
               "reliability_kept_categories_median": rel_median,
               "over_models": {g: {"counts": cnt[g], "pairs": by[g]} for g in by},
               "checks": chk, "table_ms_checks_columns": cols, "per_model": pm}
    (out / "summary.json").write_text(dumps(summary) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out / "RESULTS.md", "and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
