"""What OLMo 2's training text says around each brand, against the brands' equity (Study 3b; its plan's Amendments 1
to 5).

    python study3b-brand-knowledge-and-training-text-in-released-models/code/training-text/analyze_b5.py

The unit is the brand (the 73 brands of the instruct models' equity). For each brand: the judges' net sentiment and
recommendation share among the windows coded as the brand's sense (the majority's labels), WebOrganizer's promotional
share (Amendment 2), and the log of the estimated mentions (the brand's count alone in OLMo 2's pretraining mix,
v4_olmo-mix-1124_llama, times the brand-sense share). The inputs are in study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/; the Study 1
rerun's letters (study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz) and prompts, and the brands' controls
(web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/brand_equity.csv), are the package's own.

The tests (the plan's section "The tests"):
- primary: OLMo 2 7B Instruct's equity against each of the three primary measures, Spearman partial on the log
  estimated mentions, an interval and a two-sided P from 10,000 bootstrap draws over brands (seed 20261120), Holm
  across the three;
- the same for OLMo 2 32B Instruct, for each open model's equity in the Study 1 rerun (every model under the 90 per
  cent rule; 2,000 draws each) and for the open models' mean equity;
- the promotional share's test without the brands flagged as common words (Amendment 2, item 3);
- a regression over brands of OLMo 2 7B Instruct's equity on the three measures and the log estimated mentions with the
  free controls (Amendment 1, item 2: monthly Wikipedia views and consumer familiarity; published brand value on the
  brands it covers), standardized, with a bootstrap over brands;
- each result again with each judge's labels alone, and with Gemma 4 26B's sense label (Amendment 5);
- the agreement of the judges' promotional share with WebOrganizer's (Amendment 2, item 2): Spearman across brands, and
  Cohen's kappa on the documents that both samples hold.
Writes study3b-brand-knowledge-and-training-text-in-released-models/results/training-text/numbers.json.
"""
import gzip
import io
import json
import math
import pathlib
import sys
from collections import Counter

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PKG = REPO = HERE.parents[2]   # the package
sys.path.insert(0, str((PKG / "common/common.py").parent))   # common.py: the bootstrap's P value
sys.path.insert(0, str(HERE))   # judges.py: the judges' values and Fleiss' kappa
import common as cc  # noqa: E402

DATA = PKG / "study3b-brand-knowledge-and-training-text-in-released-models/data/training-text"   # the inputs of this analysis
PARTD = DATA / "instruct-models-equity.json"   # OLMo 2 7B and 32B Instruct's equity of each brand
COUNTS = DATA / "pretraining-brand-counts.csv"   # each brand's count in OLMo 2's pretraining mix
CONTROLS = PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/brand_equity.csv"   # the controls of the regression
EXPORT = PKG / "study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz"   # the open models' letters in the Study 1 rerun
RERUN_ITEMS = PKG / "study1b-64-models-on-34-tables/materials/rerun/prompts.jsonl.gz"
OUT = PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/training-text"
DRAWS, DRAWS_EACH_MODEL, SEED = 10000, 2000, 20261120
JUDGES = ["qwen3-32b", "gemma4-26b", "olmo31-32b"]
PROMO = {"Product Page", "Spam / Ads", "About (Org.)", "News (Org.)"}  # Amendment 2, item 1
REVIEW = {"User Review"}
MIN_PROMO_AND_REVIEW = 10  # Amendment 2: a brand with fewer than 10 promotional and review documents has no share
READ_RULE = 0.90
MEASURES = ["net_sentiment", "recommendation_share", "promotional_share"]


def ranks(x):
    return pd.Series(x).rank().to_numpy()


def partial_spearman(y, x, z):
    """Spearman correlation of y and x partial on z: the ranks of y and x, each residualized on the ranks of z."""
    ry, rx, rz = ranks(y), ranks(x), ranks(z)
    Z = np.column_stack([np.ones(len(rz)), rz])
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    if ey.std() == 0 or ex.std() == 0:
        return float("nan")
    return float(np.corrcoef(ey, ex)[0, 1])


def boot_partial(d, y, x, z, draws, seed=SEED):
    v = d[[y, x, z]].dropna()
    est = partial_spearman(v[y], v[x], v[z])
    rng = np.random.default_rng(seed)
    n = len(v)
    arr = v.to_numpy()
    bs = []
    for _ in range(draws):
        i = rng.integers(0, n, n)
        bs.append(partial_spearman(arr[i, 0], arr[i, 1], arr[i, 2]))
    bs = np.array(bs)
    bs = bs[np.isfinite(bs)]
    return {"estimate": round(est, 4), "ci95": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
            "p_two_sided": cc.p_two_sided(bs), "brands": n}


def holm(ps):
    """Holm's adjusted P values, in the order given."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = round(run, 4)
    return adj


def tests(d, equity, draws, label):
    """The three primary measures against one equity column, partial on log_mentions, with Holm."""
    out = {"equity": label, "draws": draws}
    for m in MEASURES:
        out[m] = boot_partial(d, equity, m, "log_mentions", draws)
    for m, p in zip(MEASURES, holm([out[m]["p_two_sided"] for m in MEASURES])):
        out[m]["p_holm"] = p
    return out


def measures_from_windows(w, who, sense_from=None):
    """Net sentiment, recommendation share and brand-sense share of each brand from the windows' labels: who is a
    judge's key or 'maj' (the majority, which reproduces brand_measures.csv); sense_from, when given, is the key whose
    sense label picks the windows (Amendment 5: Gemma 4 26B's sense with the majority's other labels). The values are
    not rounded, so that rounding makes no ties in the ranks (the section 3, item 4)."""
    sense_from = sense_from or who
    rows = []
    for b, g in w.groupby("brand"):
        s = g[g[f"{sense_from}_sense"].notna()]
        sense = s[s[f"{sense_from}_sense"] == "yes"]
        st = sense[sense[f"{who}_sentiment"].notna()]
        rc = sense[sense[f"{who}_recommends"].notna()]
        kd = sense[sense[f"{who}_kind"].isin(["promotional", "review"])]
        rows.append({"brand": b, "brand_sense_share": (s[f"{sense_from}_sense"] == "yes").mean() if len(s) else np.nan,
                     "sense_windows": len(sense),
                     "net_sentiment": ((st[f"{who}_sentiment"] == "positive").sum() - (st[f"{who}_sentiment"] == "negative").sum()) / len(st) if len(st) else np.nan,
                     "recommendation_share": (rc[f"{who}_recommends"] == "yes").mean() if len(rc) else np.nan,
                     "lexicon_recommendation_share": sense["lexicon_recommend"].astype(int).mean() if len(sense) else np.nan,
                     "judges_promotional_share": (kd[f"{who}_kind"] == "promotional").mean() if len(kd) >= MIN_PROMO_AND_REVIEW else np.nan})
    return pd.DataFrame(rows).set_index("brand")


def weborganizer_shares():
    f = pd.read_csv(DATA / "weborganizer-formats-by-brand.csv").set_index("brand")
    ok = (f.promotional + f.review) >= MIN_PROMO_AND_REVIEW
    return f.promo_share.where(ok), f


def open_model_equity(export=EXPORT, items_path=RERUN_ITEMS):
    """Each open model's equity of each brand in the Study 1 rerun: 100 x (the share of answers that pick the brand's
    product with names shown minus with names hidden), the brand's tables pooled, every answer counted (as
    brand_level.py does); models whose answers are read in under 90 per cent of the build's items are left out."""
    items = {json.loads(l)["id"]: json.loads(l) for l in gzip.open(items_path, "rt", encoding="utf8")}
    a = pd.read_csv(export, dtype={"letter": str}, keep_default_na=False)
    a = a[a["build"] == "study1-rerun/s1rerun1"]
    read = a.groupby("model").letter.apply(lambda s: (s != "").mean())
    left = {m: round(100 * float(v), 1) for m, v in read.items() if v < READ_RULE}
    rows = []
    for m, iid, L in zip(a["model"], a["id"], a["letter"]):
        it = items.get(iid)
        if it is None or it["names"] not in ("shown", "hidden") or m in left:
            continue
        # one row a brand in each answer: a brand with two products in a table (Oral-B) is picked when either is, as
        # brand_level.py counts it (the section 3, item 3)
        picked = {}
        for letter, p in it["products"].items():
            if p["true_kind"] != "invented":
                picked[p["true_brand"]] = max(picked.get(p["true_brand"], 0), int(L == letter))
        rows += [(m, b, it["names"], v) for b, v in picked.items()]
    d = pd.DataFrame(rows, columns=["model", "brand", "names", "picked"])
    s = d.groupby(["model", "brand", "names"]).picked.mean().unstack("names")
    eq = (100 * (s["shown"] - s["hidden"])).unstack("model")
    return eq, left


def kappa(a, b):
    a, b = list(a), list(b)
    cats = sorted(set(a) | set(b))
    po = np.mean([x == y for x, y in zip(a, b)])
    pe = sum((a.count(c) / len(a)) * (b.count(c) / len(b)) for c in cats)
    return round(float((po - pe) / (1 - pe)), 4) if pe < 1 else None


def weborganizer_agreement(windows, judges_promo):
    wo, _ = weborganizer_shares()
    both = pd.concat([wo.rename("weborganizer"), judges_promo.rename("judges")], axis=1).dropna()
    rho = float(both.rank().corr().iloc[0, 1]) if len(both) > 2 else None
    dl = pd.read_json(DATA / "weborganizer-document-labels.jsonl.gz", lines=True)
    dl["wo3"] = dl.label.map(lambda l: "promotional" if l in PROMO else "review" if l in REVIEW else "neither")
    dl = dl.drop_duplicates(["brand", "doc_ix"])
    m = windows.merge(dl, on=["brand", "doc_ix"]).dropna(subset=["maj_kind"])
    m["j3"] = m.maj_kind.map(lambda k: k if k in ("promotional", "review") else "neither")
    out = {"brands_with_both_shares": len(both), "spearman": round(rho, 4) if rho is not None else None,
           "match": "the brand and the document index (the files hold no shard), not Amendment 2's shard and index"}
    # the section 7, item 2: the unit is the document; the first window of a document stands for it, and a
    # stricter version also needs the same address (b19-data-6's promo/docs.jsonl)
    urls = {}
    # each promotional document's address (the training data's promotional documents)
    for line in gzip.open(DATA / "promotional-documents.jsonl.gz", "rt", encoding="utf-8"):
        d = json.loads(line)
        urls[(d["brand"], int(d["doc_ix"]))] = d["url"]
    docs = m.drop_duplicates(["brand", "doc_ix"])
    same = docs[[urls.get((b, i)) == u for b, i, u in zip(docs.brand, docs.doc_ix, docs.url)]] if urls else docs.iloc[0:0]
    for name, x in (("windows", m), ("documents", docs), ("documents_with_the_same_address", same)):
        out[name] = {"pairs": len(x), "brands": int(x.brand.nunique()),
                     "cohen_kappa_promotional_review_neither": kappa(x.wo3, x.j3) if len(x) else None,
                     "raw_agreement": round(float((x.wo3 == x.j3).mean()), 4) if len(x) else None}
    return out


def controls_regression(d, equity, draws):
    """Standardized OLS of equity on the three measures, log mentions and the free controls, bootstrap over brands."""
    out = {}
    for label, extra in (("views_and_familiarity", ["log10_wikipedia_monthly_views", "consumer_familiarity_mean"]),
                         ("with_brand_value", ["log10_wikipedia_monthly_views", "consumer_familiarity_mean", "log10_brand_value"])):
        cols = MEASURES + ["log_mentions"] + extra
        v = d[[equity] + cols].dropna()
        if len(v) < len(cols) + 5:
            out[label] = {"brands": len(v), "note": "too few brands with every control"}
            continue
        z = (v - v.mean()) / v.std(ddof=0)
        X = np.column_stack([np.ones(len(z)), z[cols].to_numpy()])
        y = z[equity].to_numpy()
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        rng = np.random.default_rng(SEED)
        bs = []
        for _ in range(draws):
            i = rng.integers(0, len(y), len(y))
            bs.append(np.linalg.lstsq(X[i], y[i], rcond=None)[0])
        bs = np.array(bs)
        out[label] = {"brands": len(v), "brands_list": sorted(v.index), "coefficients": {
            c: {"beta": round(float(b[k + 1]), 4), "ci95": [round(float(np.percentile(bs[:, k + 1], 2.5)), 4), round(float(np.percentile(bs[:, k + 1], 97.5)), 4)],
                "p_two_sided": cc.p_two_sided(bs[:, k + 1])} for k, c in enumerate(cols)}}
    return out


def brand_table(measures, sense_share):
    """The brand-level frame: the judges' measures, WebOrganizer's promotional share, the controls and log mentions."""
    counts = pd.read_csv(COUNTS)
    alone = counts[counts["index"] == "v4_olmo-mix-1124_llama"].set_index("brand").alone
    wo, _ = weborganizer_shares()
    ctl = pd.read_csv(CONTROLS).set_index("brand")
    d = measures[["net_sentiment", "recommendation_share"]].copy()
    d["promotional_share"] = wo
    d["brand_sense_share"] = sense_share
    d["mentions_alone"] = alone
    d["log_mentions"] = np.log(alone * sense_share.clip(lower=0.5 / 200))  # a share of zero is taken as half a window
    for c in ("log10_wikipedia_monthly_views", "consumer_familiarity_mean", "log10_brand_value"):
        d[c] = ctl[c] if c in ctl else np.nan
    return d


def main():
    pd_ = json.load(open(PARTD, encoding="utf-8"))
    common = sorted(set(pd_["ambiguous"]))
    windows = pd.concat([pd.read_csv(DATA / f"coded-passages-{b}.csv.gz", dtype=str, keep_default_na=False).replace("", np.nan)
                         for b in ("first-10-brands", "other-63-brands")], ignore_index=True)
    windows["doc_ix"] = windows.doc_ix.astype("int64")
    bm = pd.read_csv(DATA / "brand-measures.csv").set_index("brand")
    check = measures_from_windows(windows, "maj")
    assert np.allclose(check.net_sentiment.round(4), bm.net_sentiment, equal_nan=True), "measures_from_windows does not reproduce brand_measures.csv"
    eq_open, left = open_model_equity()
    equities = pd.DataFrame({"olmo2_7b_instruct": pd.Series(pd_["models"]["olmo2-7b-instruct-full2"]["equity"]),
                             "olmo2_32b_instruct": pd.Series(pd_["models"]["olmo2-32b-instruct-full2"]["equity"]),
                             "open_models_mean": eq_open.mean(axis=1)})
    res = {"brands": len(bm), "common_word_brands_part_d": common,
           "open_models_in_the_mean": sorted(eq_open.columns), "open_models_left_out_under_the_90_per_cent_rule": left,
           "sources": {"windows": ["study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/coded-passages-first-10-brands.csv.gz",
                                   "study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/coded-passages-other-63-brands.csv.gz"],
                       "weborganizer": "study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/weborganizer-formats-by-brand.csv and "
                                       "weborganizer-document-labels.jsonl.gz",
                       "equity_part_d": "study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/instruct-models-equity.json",
                       "export": str(EXPORT.relative_to(REPO)).replace("\\", "/"),
                       "counts": "study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/pretraining-brand-counts.csv (v4_olmo-mix-1124_llama, alone)"}}
    # every version from the windows themselves, unrounded (the section 3, item 4); each version gets every
    # test of the plan (the plan's coding section: "each result is also reported under each judge alone"; Amendment 5,
    # item 2: Gemma 4 26B's sense label "with every test of the plan")
    versions = {"majority": measures_from_windows(windows, "maj"),
                "amendment5_gemma4_26b_sense": measures_from_windows(windows, "maj", sense_from="gemma4-26b")}
    for j in JUDGES:
        versions[f"judge_{j}"] = measures_from_windows(windows, j)
    few = sorted(b for b, n in versions["majority"].sense_windows.items() if n < 10)
    res["brands_with_fewer_than_ten_windows_in_the_brands_sense"] = {b: int(versions["majority"].sense_windows[b]) for b in few}
    res["versions"], res["brand_tables"] = {}, {}
    for name, meas in versions.items():
        d = brand_table(meas[["net_sentiment", "recommendation_share"]], meas.brand_sense_share).join(equities)
        d["judges_promotional_share"] = meas.judges_promotional_share
        d["lexicon_recommendation_share"] = meas.lexicon_recommendation_share
        v = {"primary_olmo2_7b_instruct": tests(d, "olmo2_7b_instruct", DRAWS, "OLMo 2 7B Instruct (part D)"),
             "olmo2_32b_instruct": tests(d, "olmo2_32b_instruct", DRAWS, "OLMo 2 32B Instruct (part D; Amendment 7)"),
             "open_models_mean": tests(d, "open_models_mean", DRAWS, "the open models' mean equity (Study 1 rerun)"),
             "promotional_share_without_common_word_brands": boot_partial(
                 d.drop(index=[b for b in common if b in d.index]), "olmo2_7b_instruct", "promotional_share", "log_mentions", DRAWS),
             # exploratory, added after the results were read (22 November, about 3:05 AM Central, corrected after
             # the check): the judges' two measures without the brands that have fewer than ten windows in the
             # brand's sense, and, as first reported, without part D's ten common-word brands
             "exploratory_without_brands_with_fewer_than_ten_sense_windows": {
                 m: boot_partial(d.drop(index=few), "olmo2_7b_instruct", m, "log_mentions", DRAWS) for m in ("net_sentiment", "recommendation_share")},
             "exploratory_without_common_word_brands": {
                 m: boot_partial(d.drop(index=[b for b in common if b in d.index]), "olmo2_7b_instruct", m, "log_mentions", DRAWS)
                 for m in ("net_sentiment", "recommendation_share")},
             "controls_regression": controls_regression(d, "olmo2_7b_instruct", DRAWS),
             "judges_promotional_share_check": boot_partial(d, "olmo2_7b_instruct", "judges_promotional_share", "log_mentions", DRAWS),
             "word_list_recommendation_check": {
                 "spearman_with_the_judges_recommendation_share": round(float(d[["lexicon_recommendation_share", "recommendation_share"]].dropna().rank().corr().iloc[0, 1]), 4),
                 "partial_test": boot_partial(d, "olmo2_7b_instruct", "lexicon_recommendation_share", "log_mentions", DRAWS)}}
        each = {}
        for m in eq_open.columns:
            dm = d.join(eq_open[m].rename("eq_m"))
            each[m] = {x: boot_partial(dm, "eq_m", x, "log_mentions", DRAWS_EACH_MODEL) for x in MEASURES}
        v["each_open_model"] = each
        v["each_open_model_summary"] = {x: {"models": len(each),
                                            "median_estimate": round(float(np.median([e[x]["estimate"] for e in each.values()])), 4),
                                            "above_zero_by_interval": sorted(m for m, e in each.items() if e[x]["ci95"][0] > 0),
                                            "below_zero_by_interval": sorted(m for m, e in each.items() if e[x]["ci95"][1] < 0)} for x in MEASURES}
        res["versions"][name] = v
        res["brand_tables"][name] = d.reset_index().rename(columns={"index": "brand"}).to_dict(orient="records")
    res["brand_table"] = res["brand_tables"]["majority"]
    res["weborganizer_agreement"] = weborganizer_agreement(windows, versions["majority"].judges_promotional_share)
    # the plan's coding and sample sections (the section 4)
    import judges as R  # noqa: E402  (the same Fleiss' kappa as the judges' checks)
    res["fleiss_kappa_all_windows"] = {}
    for q in ("sense", "sentiment", "recommends", "kind"):
        full = windows[[f"{j}_{q}" for j in JUDGES]].dropna()
        counts = [[sum(row[f"{j}_{q}"] == v for j in JUDGES) for v in R.VALUES[q]] for _, row in full.iterrows()]
        res["fleiss_kappa_all_windows"][q] = {"kappa": R.fleiss_kappa(counts), "windows": len(full)}
    res["reference_reader_cohen_kappa_pilot3"] = json.load(open(DATA / "reference-reader-agreement.json", encoding="utf-8"))["cohen_kappa_against_reference"]
    by = windows.groupby("brand")
    res["sample"] = {"windows": len(windows),
                     "distinct_document_share_median": round(float(by.apply(lambda g: len(set(zip(g.shard, g.doc_ix))) / len(g)).median()), 4),
                     "distinct_document_share_min": round(float(by.apply(lambda g: len(set(zip(g.shard, g.doc_ix))) / len(g)).min()), 4),
                     "distinct_address_share_median": round(float(by.apply(lambda g: g.url.nunique() / len(g)).median()), 4),
                     "sources": dict(Counter(windows.source).most_common())}
    ctl = pd.read_csv(CONTROLS).set_index("brand").reindex(bm.index)
    res["controls_coverage_of_the_73_brands"] = {c: int(ctl[c].notna().sum()) for c in
                                                 ("log10_wikipedia_monthly_views", "consumer_familiarity_mean", "log10_brand_value")}
    res["controls_not_searched"] = ("market share and independent quality ratings: no search for a free source has been made "
                                    "(the plan names the research firms' public press releases and published test scores)")
    res["_meta"] = {"script": "study3b-brand-knowledge-and-training-text-in-released-models/code/training-text/analyze_b5.py", "plan": "the training text's plan, Amendments 1 to 5",
                    "draws": DRAWS, "draws_each_open_model": DRAWS_EACH_MODEL, "seed": SEED}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "numbers.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n",
                                      encoding="utf-8", newline="\n")
    p = res["versions"]["majority"]["primary_olmo2_7b_instruct"]
    print(json.dumps({k: p[k] for k in MEASURES}, indent=1))
    for name, v in res["versions"].items():
        print(name, {m: (v["primary_olmo2_7b_instruct"][m]["estimate"], v["primary_olmo2_7b_instruct"][m]["ci95"]) for m in MEASURES})
    print(json.dumps(res["weborganizer_agreement"]), json.dumps(res["versions"]["majority"]["each_open_model_summary"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
