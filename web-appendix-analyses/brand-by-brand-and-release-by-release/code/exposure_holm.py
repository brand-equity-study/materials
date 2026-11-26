"""Equity against measures of a brand's exposure, with Holm's correction.

The script takes Table W12's 18 correlations (six measures of a brand's exposure in three sources of responses, from the
brand-level analysis), the six regressions of Web Appendix I.2 on measures of a brand's standing, and the promotional
share in OLMo 2's training text (from the training text's analysis, which has its own Holm P over its three measures).

    python web-appendix-analyses/brand-by-brand-and-release-by-release/code/exposure_holm.py [--out PATH]

No number is estimated again: the correlations, the coefficients, the intervals and the two-sided P values are those
of the two numbers files; only Holm's correction is added, over the 18 correlations of the table, over the six of each
source, over all 27 correlations of the analysis, over the terms of all six regressions and over the three terms of the
regression with page views.
"""
import argparse
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[3]  # the top of the replication package
BL = PKG / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "results" / "brand_level" / "numbers.json"
TT = PKG / "study3b-brand-knowledge-and-training-text-in-released-models" / "results" / "training-text" / "numbers.json"
OUT = PKG / "web-appendix-analyses" / "brand-by-brand-and-release-by-release" / "results" / "brand_level" / "exposure-holm.json"
MEASURES = ["log_freq_with_category", "log_freq_name_alone", "log10_wikipedia_monthly_views", "coded_high_share",
            "consumer_familiarity_mean", "in_a_value_ranking"]  # Table W12's rows
SOURCES = ["corpus", "claude", "open"]
VIEWS = "frequency, coded familiarity and page views"


def holm(ps):
    """Holm's adjusted P values, in the order given."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        out[i] = run
    return out


DRAWS = 2000  # the brands were resampled 2,000 times, so a bootstrap P of zero is below 1/2,000


def main(out_path=OUT):
    bl = json.loads(BL.read_text(encoding="utf-8"))
    # Holm over every correlation of the analysis (nine measures in three sources, 27),
    # with a bootstrap P of zero taken as 1/2,000
    allc = [(s, m, c) for s in SOURCES for m, c in bl[f"correlations_{s}_brands"].items()]
    h27 = dict(zip([(s, m) for s, m, _ in allc],
                   holm([max(c["spearman_p_two_sided"], 1 / DRAWS) for _, _, c in allc])))
    cells = [(s, m, bl[f"correlations_{s}_brands"][m]) for s in SOURCES for m in MEASURES]
    h18 = holm([max(c["spearman_p_two_sided"], 1 / DRAWS) for _, _, c in cells])
    corr = {s: {} for s in SOURCES}
    for (s, m, c), p18 in zip(cells, h18):
        corr[s][m] = {"brands": c["brands"], "spearman": c["spearman"], "ci95": c["spearman_ci95_brands_resampled_2000"],
                      "p_two_sided": c["spearman_p_two_sided"], "p_holm_18": p18, "p_holm_27": h27[(s, m)]}
    corr["correlations_in_the_holm_family"] = len(allc)
    for s in SOURCES:
        h6 = holm([max(corr[s][m]["p_two_sided"], 1 / DRAWS) for m in MEASURES])
        for m, p in zip(MEASURES, h6):
            corr[s][m]["p_holm_6"] = p
        corr[s]["counts"] = {
            "below_zero_by_interval": sum(corr[s][m]["ci95"][1] < 0 for m in MEASURES),
            "above_zero_by_interval": sum(corr[s][m]["ci95"][0] > 0 for m in MEASURES),
            "below_zero_after_holm_27": sum(corr[s][m]["ci95"][1] < 0 and corr[s][m]["p_holm_27"] < 0.05
                                            for m in MEASURES),
            "below_zero_after_holm_18": sum(corr[s][m]["ci95"][1] < 0 and corr[s][m]["p_holm_18"] < 0.05
                                            for m in MEASURES),
            "below_zero_after_holm_6": sum(corr[s][m]["ci95"][1] < 0 and corr[s][m]["p_holm_6"] < 0.05
                                           for m in MEASURES)}
    regs = bl["regressions_corpus"]
    terms = [(name, t, v) for name, r in regs.items() for t, v in r["terms"].items()]
    hall = holm([v["p"] for _, _, v in terms])
    reg = {name: {"brands": r["brands"], "models": r["models"], "terms": {}} for name, r in regs.items()}
    for (name, t, v), p in zip(terms, hall):
        reg[name]["terms"][t] = dict(v, p_holm_all_terms=p)
    hv = holm([v["p"] for v in regs[VIEWS]["terms"].values()])
    for t, p in zip(regs[VIEWS]["terms"], hv):
        reg[VIEWS]["terms"][t]["p_holm_this_regression"] = p
    reg_counts = {"terms": len(terms), "below_zero_by_interval": sum(v["ci95"][1] < 0 for _, _, v in terms),
                  "above_zero_by_interval": sum(v["ci95"][0] > 0 for _, _, v in terms),
                  "below_zero_after_holm_all_terms": sum(v["ci95"][1] < 0 and p < 0.05 for (_, _, v), p in
                                                         zip(terms, hall))}
    tt = json.loads(TT.read_text(encoding="utf-8"))["versions"]["majority"]
    promo = {k: tt[k]["promotional_share"] for k in ("primary_olmo2_7b_instruct", "olmo2_32b_instruct", "open_models_mean")
             if k in tt}
    out = {"sources": [str(p.relative_to(PKG)).replace("\\", "/") for p in (BL, TT)], "correlations": corr,
           "regressions": reg, "regression_counts": reg_counts, "promotional_share_b5": promo,
           "page_views_regression": VIEWS}
    out_path = Path(out_path)
    out_path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for s in SOURCES:
        print(s, corr[s]["counts"])
        for m in MEASURES:
            c = corr[s][m]
            print(f"   {m:32s} {c['spearman']:+.2f} [{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}] p {c['p_two_sided']:.4f} "
                  f"holm18 {c['p_holm_18']:.3f} holm27 {c['p_holm_27']:.3f} holm6 {c['p_holm_6']:.3f}")
    print("regressions", reg_counts)
    for t, v in reg[VIEWS]["terms"].items():
        print(f"   {t:12s} {v['coef']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] p {v['p']:.4f} "
              f"holm(all {len(terms)}) {v['p_holm_all_terms']:.3f} holm(3) {v['p_holm_this_regression']:.3f}")
    for k, v in promo.items():
        print("   training text", k, {x: v.get(x) for x in ("estimate", "ci95", "p_two_sided", "p_holm", "brands")})
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(OUT), help="where to write the JSON file")
    sys.exit(main(ap.parse_args().out))
