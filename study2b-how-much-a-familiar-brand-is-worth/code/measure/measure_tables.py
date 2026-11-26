import collections
import csv
import gzip
import json
import pathlib
import sys

PKG = R = pathlib.Path(__file__).resolve().parents[3]   # the package
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # the measure's code
import types  # noqa: E402
# the pretest's categories, as its builder defines them (for the levels that the full design changed)
P = types.SimpleNamespace(CATEGORIES=json.loads((PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/pretest_categories.json").read_text(encoding="utf-8")))
OUTJ = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-design/numbers.json"
OUTT = PKG / "exhibits/results/measure_tables.md"
CLAUDE = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/numbers.json"
CODEX = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-codex/numbers.json"
ORDER = ["laptops", "smartphones", "tvs", "headphones", "earbuds", "running_shoes", "coffee_makers"]
CAT = {"laptops": "Laptops", "smartphones": "Smartphones", "tvs": "Televisions", "headphones": "Over-ear headphones",
       "earbuds": "Wireless earbuds", "running_shoes": "Running shoes", "coffee_makers": "Coffee makers"}
MODELS = [("claude-fable-5-1", "Fable 5.1"), ("claude-haiku-5-5", "Haiku 5.5"), ("claude-opus-5-5", "Opus 5.5"),
          ("claude-sonnet-5-5", "Sonnet 5.5"), ("gpt-6.1-sol", "GPT-6.1 Sol"), ("gpt-6.2-sol", "GPT-6.2 Sol")]
VERSIONS = ["V1-no-prices", "V2-pilot-band", "V3-second-wording", "V4-blocks", "V5-three-products", "V6-market-budget"]


def usd(x):
    return f"\\${x:,.2f}"


API = {"claude-haiku-5-5": "Claude Haiku 5.5 (Anthropic)", "claude-sonnet-5-5": "Claude Sonnet 5.5 (Anthropic)",
       "claude-opus-5-5": "Claude Opus 5.5 (Anthropic)", "claude-fable-5-1": "Claude Fable 5.1 (Anthropic)",
       "gpt-6.1-sol": "GPT-6.1 Sol (OpenAI)", "gpt-6.2-sol": "GPT-6.2 Sol (OpenAI)"}


def model_names():
    """Each model's name from the open panel's registry (its repository name and developer), and the API models'."""
    out = dict(API)
    for r in csv.DictReader(open(PKG / "models/open-models.tsv", encoding="utf-8"), delimiter="\t"):
        out[r["key"]] = f"{r['hf_repo'].split('/')[-1].replace('-', ' ')} ({r['lab']})"
    return out


def mark(x, lo, hi, dec=1):
    star = "*" if lo is not None and (lo > 0 or hi < 0) else ""
    return f"{x:+.{dec}f}{star}".replace("-", "−")


def study1b_tables():
    """The stated priorities' effect for each model and wording, and the clarifying question for each model."""
    names = model_names()
    sp = json.load(open(PKG / "study1b-64-models-on-34-tables/results/priorities/numbers.json", encoding="utf-8"))["all_models"]
    conds = [("preference_vague", "Vague"), ("preference_weighted", "Weighted"),
             ("preference_explicit", "Explicit requirements"), ("utility_explicit", "Utility")]
    T = ["## sp_by_model", "", "Caption: Study 1b, the effect of the fictitious name for each model under each wording "
         "of the shopper's priorities (percentage points; an asterisk marks a 95 percent interval over tables that "
         "excludes zero).", "", "| Model | " + " | ".join(c for _, c in conds) + " |", "|---|" + "---|" * len(conds)]
    for m in sorted(sp["models"], key=lambda k: names.get(k, k).lower()):
        cells = []
        for c, _ in conds:
            g = sp["gap_names_hidden"][c]["models"].get(m)
            cells.append(mark(g["gap_pp"], *g["ci95_tables_resampled"]) if g else "")
        T.append(f"| {names.get(m, m)} | " + " | ".join(cells) + " |")
    T.append("")
    cl = json.load(open(PKG / "study1b-64-models-on-34-tables/results/clarifying/numbers.json", encoding="utf-8"))
    dec = cl["declines_by_model_and_names"]["clar1"]
    T += ["## clar_by_model", "", "Caption: Study 1b, the share of responses in which each model asked the shopper a "
          "question first, and its declines (responses that recommended none of the products), with and without brand "
          "names.", "", "| Model | Asked, with brand names (%) | Asked, without brand names (%) | Declines, with | "
          "Declines, without |", "|---|---|---|---|---|"]
    for m in sorted(cl["asking"]["models"], key=lambda k: names.get(k, k).lower()):
        a, d = cl["asking"]["models"][m], dec.get(m, {})
        T.append(f"| {names.get(m, m)} | {a['shown']:.1f} | {a['hidden']:.1f} | {d.get('shown', 0)} | {d.get('hidden', 0)} |")
    T.append("")
    return T


ALL = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/summary.json"


def all_models_tables(cats):
    """Web Appendix K's tables over every model that answered, from b21-16's summary.json (measure_all_results.py),
    once it is in results/measure/full1-all/: ms2_all_share (each brand over every model and in each group) and
    ms2_open_models (each open model's checks and results). Nothing is written before that file exists."""
    if not ALL.exists():
        return []
    s = json.load(open(ALL, encoding="utf-8"))
    om, n = s["over_models"], s["models_in_estimates"]
    g = s["models_by_group"]

    def f(x, dec=1, sign=False):
        return "" if x is None else (f"{x:+.{dec}f}" if sign else f"{x:.{dec}f}").replace("-", "−")
    T = ["## ms2_all_share", "", f"Caption: Share Premium of Each Familiar Brand by Model Group. Premiums are in percentage points at the " f"center of the brand's price band. In the second column, "
         f"we give the mean over the {n} models, with its 95 percent interval from a two-way bootstrap (models and choice "
         f"sets drawn again), and in the next three, the mean over the {g['claude']} Claude models, the {g['gpt']} GPT models "
         f"and the {g['open']} models with open weights. The price premium is the median over the models whose premium "
         "lies inside the tested prices; the counts give the models inside, beyond those prices and without a price "
         "premium.", "",
         "| Category | Brand | All models | Claude | GPT | Open weights | Price premium, percent (inside / beyond / without) |",
         "|---|---|---|---|---|---|---|"]
    for k in ORDER:
        for b in cats[k]["familiar"]:
            key = f"{k} | {b}"
            a = om["all"]["pairs"].get(key)
            if a is None:
                continue
            ci = a["share_premium_mean_ci95"]
            grp = [f(om[x]["pairs"][key]["share_premium_mean_pp"], sign=True) if key in om[x]["pairs"] else ""
                   for x in ("claude", "gpt", "open")]
            pp = "none inside" if a["price_premium_median_pct"] is None else f(a["price_premium_median_pct"], 0)
            T.append(f"| {CAT[k]} | {b} | {f(a['share_premium_mean_pp'], sign=True)} ({f(ci[0])} to {f(ci[1])}) | "
                     + " | ".join(grp) + f" | {pp} ({a['models_inside_tested_prices']} / {a['models_beyond_tested_prices']}"
                     f" / {a['models_without_a_price_premium']}) |")
    T += ["", "## ms2_open_models", "", "Caption: Each model with open weights in the full design, with its checks and its "
          "results. Responses with a letter is the percent of its choice responses with a letter, over those that do not decline "
          "to recommend any product, with the percent that decline in parentheses; a model under 90 percent is marked "
          "and enters no estimate over models. The main price coefficient is counted by category, below or above zero "
          "by its 95 percent interval. A category in which a model follows fewer than two attributes is named beside the "
          "model and enters no estimate over models.", "",
          "| Model | Responses with a letter (declines), percent | Pairs above / below zero | Mean share premium (points) | "
          "Reliability | Median price premium inside the tested prices, percent (pairs) | Main price coefficient below / "
          "above zero (categories) | Largest share of one position / one letter, percent |",
          "|---|---|---|---|---|---|---|---|"]
    for m, e in sorted(s["per_model"].items(), key=lambda kv: kv[1]["name"]):
        if e["group"] != "open":
            continue
        ppm = "none" if e["price_premium_median_pct_inside_tested"] is None else \
            f"{f(e['price_premium_median_pct_inside_tested'], 0)} ({e['price_premium_inside_tested']})"
        pc = f"{e.get('price_coefficient_below_zero', '')} / {e.get('price_coefficient_above_zero', '')} ({e.get('categories_checked', '')})"
        pos = (f"{100 * e['top_position_share_highest']:.0f} / {100 * e['top_letter_share_highest']:.0f}"
               if "top_position_share_highest" in e else "")
        cl = f" (fewer than two attributes followed in {', '.join(e['categories_left_out'])})" if e.get("categories_left_out") else ""
        cl += f" (not checked in {', '.join(e['categories_unchecked'])})" if e.get("categories_unchecked") else ""
        T.append(f"| {e['name']}{' (under 90 percent)' if e['left_out'] else ''}{cl} | {f(e['read_pct'])} ({f(e['decline_pct'])}) | "
                 f"{e['above_zero']} / {e['below_zero']} | {f(e['mean_share_premium_pp'], sign=True)} | {f(e['reliability'], 2)} | "
                 f"{ppm} | {pc} | {pos} |")
    T.append("")
    return T


def main():
    cats = {json.load(open(p, encoding="utf-8"))["category"]: json.load(open(p, encoding="utf-8"))
            for p in (PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/categories").glob("*.json")}
    gates = json.load(open(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/GATES.json", encoding="utf-8"))
    bands = {(r["category"], r["brand"]): r for r in csv.DictReader(open(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/PRICE-BANDS.csv", encoding="utf-8"))
             if r["kind"] == "brand" and r.get("median")}
    market = {r["category"]: r for r in csv.DictReader(open(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/PRICE-BANDS.csv", encoding="utf-8")) if r["kind"] == "market"}
    by_version = collections.Counter()
    for line in gzip.open(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz", "rt", encoding="utf-8"):
        it = json.loads(line)
        by_version[f"{it['version']} {it['cell']}"] += 1
    worst = {v: [g["versions"][v]["worst_departure"] for g in gates["categories"].values()] for v in ["main"] + VERSIONS}
    nolevel = [f"{x['brand']} ({CAT[k].lower()})" for k in ORDER for x in gates["categories"][k]["bands_without_a_level"]]
    store = collections.Counter(r["source_kind"] for r in bands.values())
    design = {
        "categories": len(cats), "pairs": sum(len(c["familiar"]) for c in cats.values()),
        "fictitious_names": sum(len(c["invented"]) for c in cats.values()),
        "items_per_model": gates["items"], "by_version": dict(by_version),
        "choice_sets_main_per_category": by_version["main shown"] // len(cats),
        "choice_sets_repeated_per_category": by_version["main repeat"] // len(cats),
        "choice_sets_version_per_category": by_version["V1-no-prices shown"] // len(cats),
        "bands_from_brand_store": store["brand_store"], "bands_from_retailer": store["retailer"],
        "balance_main_largest_pct": 100 * max(worst["main"]),
        "balance_any_version_largest_pct": 100 * max(max(x) for x in worst.values()),
        "balance_v5_lowest_pct": 100 * min(worst["V5-three-products"]),
        "balance_v5_highest_pct": 100 * max(worst["V5-three-products"]),
        "bands_without_a_price": len(nolevel), "bands_without_a_price_names": nolevel,
        "band_centres": {k: gates["categories"][k]["band_centres"] for k in ORDER},
        # the laptops' storage and battery levels in the pretest (build_items.CATEGORIES) and in the full design
        "pretest_changes": {"laptop_storage_pretest": ", ".join(dict(P.CATEGORIES["laptops"]["attributes"])["storage"]),
                            "laptop_battery_pretest": ", ".join(dict(P.CATEGORIES["laptops"]["attributes"])["battery life"]),
                            "laptop_storage_full": ", ".join(cats["laptops"]["attributes"][1]["levels"]),
                            "laptop_battery_full": ", ".join(cats["laptops"]["attributes"][2]["levels"]),
                            "tv_sizes_pretest": ", ".join(dict(P.CATEGORIES["tvs"]["attributes"])["screen size"]),
                            "tv_sizes_full": ", ".join(cats["tvs"]["attributes"][0]["levels"])},
        # the pretest's combinations of an included model and a category (the denominator of its 203 that followed
        # the attributes; results/measure/pilot1/summary.json)
        "pretest_included_cells": json.load(open(OUTJ.parent.parent / "pilot1/summary.json", encoding="utf-8"))[
            "models_included"] * len(P.CATEGORIES),
    }
    # the automated capture of the prices (price-bands/products.csv and excluded.csv, read on 22 November 2026)
    pb = PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/price-bands"
    prods = list(csv.DictReader(open(pb / "products.csv", encoding="utf-8")))
    excl = list(csv.DictReader(open(pb / "excluded.csv", encoding="utf-8")))
    in_market = collections.Counter(p["category"] for p in prods if p["counts_in_market"] == "yes")
    n_band = sorted(int(r["n_products"]) for r in bands.values())
    design["capture"] = {
        "products_counted": len(prods), "listings_left_out": len(excl),
        "market_products_lowest": min(in_market.values()), "market_products_highest": max(in_market.values()),
        "band_products_lowest": n_band[0], "band_products_median": n_band[len(n_band) // 2], "band_products_highest": n_band[-1],
        "bands_with_fewer_than_five_products": sum(n < 5 for n in n_band),
        "read_from": min(p["read_time"] for p in prods), "read_to": max(p["read_time"] for p in prods),
        "sites": sorted({p["retailer"] for p in prods})}
    OUTJ.parent.mkdir(parents=True, exist_ok=True)
    OUTJ.write_text(json.dumps(design, indent=1) + "\n", encoding="utf-8", newline="\n")

    T = ["# The tables of Study 2b's measure in the Web Appendix", "",
         "Written by measure_tables.py from the measure's categories, price bands, prompts and results. Each table "
         "is named by the key that the Web Appendix's table code gives it.", ""]
    T += ["## ms2_names_prices", "", "Caption: The names and the six prices of each category. A familiar brand's band is "
          "the middle half of its prices; bands not from the category's retailer are marked.", "",
          "| Category | Familiar brands (price band, dollars) | Fictitious names | Prices (dollars) |", "|---|---|---|---|"]
    mark = {"brand_store": "a", "retailer_own_brand": "b"}
    for k in ORDER:
        c, g = cats[k], gates["categories"][k]
        fam = []
        for b in c["familiar"]:
            r = bands[(k, b)]
            band = f"{float(r['q25']):,.0f}" if r["q25"] == r["q75"] else f"{float(r['q25']):,.0f} to {float(r['q75']):,.0f}"
            fam.append(f"{b} ({band}){'$^' + mark[r['source_kind']] + '$' if r['source_kind'] in mark else ''}")
        T.append(f"| {CAT[k]} | {'; '.join(fam)} | {', '.join(n for n, _ in c['invented'])} | "
                 f"{', '.join(f'{p:,.2f}' for p in g['price_levels'])} |")
    T += ["", "Notes: $^a$ the brand's own US online store; $^b$ Best Buy, whose brand it is. Each category's prices "
          "are evenly spaced in log price from the 5th to the 95th percentile of its products' prices at one retailer "
          "(Zappos for running shoes, Walmart for the others), widened to contain every band.", ""]
    T += ["## ms2_attributes", "", "Caption: The attributes and their levels, from worst to best.", "",
          "| Category | Attribute | Levels |", "|---|---|---|"]
    for k in ORDER:
        for a in cats[k]["attributes"]:
            note = " (not listed by the retailer)" if a["source"].startswith("not listed") else ""
            T.append(f"| {CAT[k]} | {a['name']}{note} | {', '.join(a['levels'])} |")
    T += ["", "Note: every product also showed a rating of 4.2, 4.4 or 4.6 stars from 500 reviews.", ""]
    T += ["## ms2_requests", "", "Caption: The shopper's requests.", "",
          "| Category | Main version | Second wording | With the pretest's budget | With a budget that spans the market |",
          "|---|---|---|---|---|"]
    for k in ORDER:
        c = cats[k]
        T.append(f"| {CAT[k]} | {c['requests'][0]} | {c['requests'][1]} | {c['request_pilot_band']} | {c['request_market_budget']} |")
    T.append("")
    route = {}  # each model's results file: the Claude models' and the GPT models'
    for f in (CLAUDE, CODEX):
        x = json.load(open(f, encoding="utf-8"))
        for m in x["models"]:
            route[m] = x

    def cell(m, k, b, key, fmt):
        u = route[m]["models"][m][k]["main"]["brands"][b]
        if key == "rating_equivalent_stars" and "rating_equivalent_not_estimable" in u:
            return "not estimable"
        v = u.get(key)
        lo, hi = u.get({"share_premium_pp": "share_premium_ci95", "rating_equivalent_stars": "rating_equivalent_ci95"}[key], [None, None])
        star = "*" if lo is not None and (lo > 0 or hi < 0) else ""
        return f"{v:{fmt}}{star}".replace("-", "−")
    sets = "Fable 5.1, GPT-6.1 Sol and GPT-6.2 Sol answered 800 choice sets a category, the other models 1,600"
    for key, name, cap, fmt in (("share_premium_pp", "ms2_claude_share",
                                 "The share premium of each of the 38 familiar brands in the four Claude models and the "
                                 "two GPT models, at the brand's band center (percentage points).", "+.1f"),
                                ("rating_equivalent_stars", "ms2_claude_rating",
                                 "The rating equivalent of each of the 38 familiar brands in the four Claude models and "
                                 "the two GPT models (stars). 'Not estimable' marks a category under the rule on the "
                                 "lowest rating, whose counts the text gives.", "+.2f")):
        T += [f"## {name}", "", f"Caption: {cap} An asterisk marks a 95 percent interval that excludes zero. {sets}.", "",
              "| Category | Brand | " + " | ".join(n for _, n in MODELS) + " |", "|---|---|" + "---|" * len(MODELS)]
        for k in ORDER:
            for b in cats[k]["familiar"]:
                T.append(f"| {CAT[k]} | {b} | " + " | ".join(cell(m, k, b, key, fmt) for m, _ in MODELS) + " |")
        T.append("")
    T += study1b_tables()
    T += ["## ms2_reliability", "", "Caption: The measure's reliability within each category in the Claude and GPT "
          "models: the mean, over 200 random divisions of a category's choice sets into two halves, of the Spearman "
          "correlation between the halves' values of the category's four to six familiar brands, and in parentheses its "
          "Spearman-Brown value; in the last column, we give the Spearman-Brown value of the mean over the seven "
          "categories.", "",
          "| Model | " + " | ".join(CAT[k] for k in ORDER) + " | All |", "|---|" + "---|" * (len(ORDER) + 1)]
    for m, name in MODELS:
        pr = route[m]["pooled_reliability"][m]
        by = pr["by_category"]
        T.append(f"| {name} | " + " | ".join(f"{by[k]['half_correlation']:.2f} ({by[k]['spearman_brown']:.2f})".replace("-", "−")
                                            for k in ORDER) + f" | {pr['spearman_brown_of_the_mean']:.2f} |")
    T.append("")
    T += all_models_tables(cats)
    OUTT.parent.mkdir(parents=True, exist_ok=True)
    OUTT.write_text("\n".join(T) + "\n", encoding="utf-8", newline="\n")
    written = table_files(T) + every_model_files(cats)
    print("wrote", OUTJ, "and", OUTT, "and", len(written), "table files:", ", ".join(str(p.relative_to(R)) for p in written))
    return 0


TABLE_FILES = {"sp_by_model": PKG / "study1b-64-models-on-34-tables/results/tables",
               "clar_by_model": PKG / "study1b-64-models-on-34-tables/results/tables"}
FILE_NAMES = {"ms2_names_prices": "categories-brands-and-prices.csv", "ms2_attributes": "attributes-and-levels.csv",
              "ms2_requests": "shoppers-requests.csv",
              "ms2_claude_share": "share-premium-by-brand-claude-and-gpt-models.csv",
              "ms2_claude_rating": "rating-equivalent-by-brand-claude-and-gpt-models.csv",
              "ms2_reliability": "reliability-by-model-and-category.csv",
              "ms2_all_share": "share-premium-by-brand-over-models.csv", "ms2_open_models": "each-open-model.csv",
              "sp_by_model": "stated-priorities-by-model.csv", "clar_by_model": "clarifying-question-by-model.csv"}
MEASURE_TABLES = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/tables"


def table_files(T):
    out = []
    text = "\n".join(T)
    for block in text.split("\n## ")[1:]:
        name, _, body = block.partition("\n")
        lines = [ln for ln in body.split("\n") if ln.startswith("|")]
        if len(lines) < 3:
            continue
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
        folder = TABLE_FILES.get(name, MEASURE_TABLES)
        folder.mkdir(parents=True, exist_ok=True)
        p = folder / FILE_NAMES.get(name, f"{name}.csv")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(rows[0])
            w.writerows(rows[2:])
        out.append(p)
    return out


def every_model_files(cats):
    """The main version's share premium and rating equivalent of each familiar brand in every model that answered
    (results/measure/full1-all/cells.csv.gz), one row a brand and one column a model, with the models' names."""
    src = ALL.parent / "cells.csv.gz"
    if not src.exists():
        return []
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import measure_all_results as MR  # the corpus's names of the models, as Table ms2_open_models gives them
    names = MR.names()
    rows = [r for r in csv.DictReader(gzip.open(src, "rt", encoding="utf-8")) if r["version"] == "main"]
    order = {"claude": 0, "gpt": 1, "open": 2}
    models = sorted({r["model"] for r in rows}, key=lambda m: (order[MR.group_of(m)], names.get(m, m).lower()))
    val = {(r["model"], r["category"], r["brand"]): r for r in rows}
    out = []
    MEASURE_TABLES.mkdir(parents=True, exist_ok=True)
    for key, fname in (("share_premium_pp", "share-premium-by-brand-and-model.csv"),
                       ("rating_equivalent_stars", "rating-equivalent-by-brand-and-model.csv")):
        p = MEASURE_TABLES / fname
        with open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["category", "brand"] + [names.get(m, m) for m in models])
            for k in ORDER:
                for b in cats[k]["familiar"]:
                    w.writerow([CAT[k], b] + [(lambda x: "" if x in (None, "") else f"{float(x):.2f}")(
                        (val.get((m, k, b)) or {}).get(key)) for m in models])
        out.append(p)
    return out


if __name__ == "__main__":
    sys.exit(main())
