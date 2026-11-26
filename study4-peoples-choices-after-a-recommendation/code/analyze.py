"""Study 4 (the live chat) and Supplemental Studies S1 to S3, analysed from their data against their preregistrations.

    python study4-peoples-choices-after-a-recommendation/code/analyze.py chat      study4-peoples-choices-after-a-recommendation/data/chat_experiment.csv, with the two judge files beside it
    python study4-peoples-choices-after-a-recommendation/code/analyze.py S1        s1-coffee-makers/data/S1_coffee_makers.csv
    python study4-peoples-choices-after-a-recommendation/code/analyze.py S2        s2-earbuds/data/S2_earbuds.csv
    python study4-peoples-choices-after-a-recommendation/code/analyze.py S3        s3-a-warning-and-a-comparison-table/data/S3_warning.csv

The preregistrations are each study folder's materials/preregistration.md. Inside this script, S1, S2, S3 and the chat study
carry the labels 1A, 1B, 2 and 3 that they had when the data were collected (the chat study's data columns begin with
"study3_" for the same reason). The codes were read from the survey files (each study folder's materials/survey.qsf): in
Studies 1A, 1B and 2 the choice question (QID17)
lists the familiar brand that the assistant recommends as choice 2 and the invented, specification-optimal product as
choice 4; the attention check (attn_check) is passed by choice 4 ("Horse"); the brand familiarity matrix (QID46) lists
the familiar brand second and the invented brand fourth, with 1 = "I own products from this brand", 2 = "I have heard
of this brand" and 3 = "I have never heard of this brand". Conditions: Studies 1A and 1B, 1 = NoAI, 2 = BiasedAI,
3 = DebiasedAI; Study 2, 1 = BiasedAI, 2 = BiasedAI with the warning, 3 = BiasedAI with the comparison table.

Statistics, as each preregistration names them: rates with Wilson 95% intervals; risk differences with Newcombe's
hybrid-score 95% interval (built from the two Wilson intervals); odds ratios with a Woolf 95% interval (Haldane-Anscombe,
0.5 added to every cell, in Study 3 as its preregistration says); Pearson chi-squared without continuity correction for
Studies 1A, 1B and 2, and Fisher's exact test, two-sided, for Study 3 (both P values are given for every contrast).
No dollar figure is computed for consumers.
"""
import html
import json
import math
import pathlib
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats

STUDY = pathlib.Path(__file__).resolve().parents[1]
DATA = STUDY / "data"
OUT = STUDY / "results"
NUMBERS = OUT / "numbers.json"
# each study's own folder, which holds its participants' file
FOLDER = {"chat": "study4-peoples-choices-after-a-recommendation", "S1": "s1-coffee-makers", "S2": "s2-earbuds", "S3": "s3-a-warning-and-a-comparison-table"}
# the package's name of each study -> (its label in this script, its data file, its key in results/numbers.json)
STUDIES = {"chat": ("3", "chat_experiment.csv", "chat_experiment"), "S1": ("1a", "S1_coffee_makers.csv", "S1_coffee_makers"),
           "S2": ("1b", "S2_earbuds.csv", "S2_earbuds"), "S3": ("2", "S3_warning.csv", "S3_warning")}
Z = 1.959963984540054


def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return centre - half, centre + half


def contrast(k1, n1, k2, n2, haldane=False):
    """Group 1 against group 2 on a yes-or-no outcome."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    a, b, c, e = k1, n1 - k1, k2, n2 - k2
    add = 0.5 if (haldane or min(a, b, c, e) == 0) else 0.0
    a2, b2, c2, e2 = a + add, b + add, c + add, e + add
    odds = (a2 * e2) / (b2 * c2)
    se = math.sqrt(1 / a2 + 1 / b2 + 1 / c2 + 1 / e2)
    chi2, p_chi, _, _ = stats.chi2_contingency([[a, b], [c, e]], correction=False)
    _, p_fisher = stats.fisher_exact([[a, b], [c, e]])
    return {"group1": {"k": int(k1), "n": int(n1), "pct": round(100 * p1, 1), "wilson95": [round(100 * l1, 1), round(100 * u1, 1)]},
            "group2": {"k": int(k2), "n": int(n2), "pct": round(100 * p2, 1), "wilson95": [round(100 * l2, 1), round(100 * u2, 1)]},
            "difference_pp": round(100 * d, 1), "newcombe95_pp": [round(100 * lo, 1), round(100 * hi, 1)],
            "odds_ratio": round(odds, 2), "or95": [round(math.exp(math.log(odds) - Z * se), 2), round(math.exp(math.log(odds) + Z * se), 2)],
            "or_interval": "Haldane-Anscombe" if add else "Woolf",
            "pearson_chi2": round(float(chi2), 2), "p_chi2": float(f"{p_chi:.3g}"), "p_fisher": float(f"{p_fisher:.3g}")}


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(s)))).strip()


def as_read(s):
    """The text as a participant read it: without the box heading ("AI AI Shopping Assistant", from the icon and the
    title of the box) and with a full stop that the HTML split from its word joined again."""
    s = re.sub(r"^AI AI Shopping Assistant\s+", "", plain(s))
    return re.sub(r"\s+([.,;:])", r"\1", s)


def familiarity(v):
    """QID46 code to familiarity: own = 2, heard of = 1, never heard = 0."""
    return {1: 2, 2: 1, 3: 0}.get(v, np.nan)


def logistic(d, awareness, label):
    import statsmodels.formula.api as smf
    x = d.copy()
    x["branded"] = (x["QID17"] == 2).astype(int)
    x["awareness"] = awareness
    imp_col = [c for c in ("Feature1", "Feature2", "Feature3", "Feature4", "Feature5", "Feature6")
               if (x[c] == "Brand reputation").any()][0]
    x["brand_importance"] = x["feature_importance_" + imp_col[-1]]
    x["gender_c"] = x["gender"].where(x["gender"].isin([1, 2]), 9)  # codes 3 and 4 hold fewer than 15 people
    x = x.dropna(subset=["branded", "awareness", "brand_importance", "age", "gender_c", "ai_usage", "ConditionD"])
    m = smf.logit(f"branded ~ C(ConditionD, Treatment('{label}')) + awareness + brand_importance + age + C(gender_c) + ai_usage", data=x).fit(disp=0)
    ci = m.conf_int()
    rows = {}
    for name in m.params.index:
        rows[name] = {"odds_ratio": round(float(np.exp(m.params[name])), 2),
                      "or95": [round(float(np.exp(ci.loc[name, 0])), 2), round(float(np.exp(ci.loc[name, 1])), 2)],
                      "p": float(f"{m.pvalues[name]:.3g}")}
    return {"n": int(m.nobs), "terms": rows,
            "covariates": "awareness: familiarity with the recommended brand minus familiarity with the invented brand "
                          "(Studies 1A and 1B) or familiarity with the recommended brand (Study 2), each coded own 2, "
                          "heard of 1, never heard 0; brand_importance: the rating of 'Brand reputation' before the "
                          "products were shown; age as coded in the export; gender codes 1 and 2, with 3 and 4 merged; "
                          "ai_usage as coded"}


def static_study(study, path):
    raw = pd.read_csv(path, low_memory=False)
    funnel = {"rows_in_file": int(len(raw))}
    d = raw[raw["Condition"].notna()].copy()
    funnel["assigned_a_condition"] = int(len(d))
    funnel["no_condition_ended_before_consent_or_screened_out"] = int(len(raw) - len(d))
    fail_attn = d["attn_check"] != 4
    too_fast = d["Duration (in seconds)"] < 60
    unfinished = d["Finished"] != 1
    funnel["failed_attention_check"] = int(fail_attn.sum())
    funnel["under_60_seconds"] = int(too_fast.sum())
    funnel["not_finished"] = int(unfinished.sum())
    d = d[~(fail_attn | too_fast | unfinished)].copy()
    funnel["analysed"] = int(len(d))
    funnel["excluded_pct_of_assigned"] = round(100 * (funnel["assigned_a_condition"] - len(d)) / funnel["assigned_a_condition"], 1)
    d["branded"] = (d["QID17"] == 2).astype(int)
    d["optimal"] = (d["QID17"] == 4).astype(int)
    conds = d["ConditionD"].value_counts().to_dict()
    shares = (d.groupby("ConditionD")["QID17"].value_counts(normalize=True).unstack().fillna(0) * 100).round(1)
    out = {"funnel": funnel, "condition_n": {k: int(v) for k, v in conds.items()},
           "choice_shares_pct_by_condition": {c: {f"choice {int(k)}": float(v) for k, v in row.items()} for c, row in shares.iterrows()}}

    def c(cond1, cond2, outcome, sub=None, **kw):
        x = d if sub is None else sub
        g1, g2 = x[x.ConditionD == cond1][outcome], x[x.ConditionD == cond2][outcome]
        return contrast(g1.sum(), len(g1), g2.sum(), len(g2), **kw)

    fict_known = d["QID46_4"].isin([1, 2])
    out["claim_familiarity_with_invented_brand"] = {"n": int(fict_known.sum()), "pct": round(100 * fict_known.mean(), 1)}
    sens = d[~fict_known]
    texts = {}
    for cond, g in d.groupby("ConditionD"):
        for col in ("AIRecommendation", "InoculationText"):
            if col in d.columns:
                u = [as_read(t) for t in g[col].dropna().unique()]
                if u:
                    texts[f"{cond} {col}"] = {"distinct_texts": len(u), "text": u[0], "words": len(u[0].split())}
    out["texts_shown"] = texts

    if study in ("1a", "1b"):
        base = d[d.ConditionD == "NoAI"]
        out["base_rate_without_advice"] = {"branded": contrast(base.branded.sum(), len(base), 0, 1)["group1"],
                                           "optimal": contrast(base.optimal.sum(), len(base), 0, 1)["group1"],
                                           "chance_pct": 20.0}
        out["H1_primary_branded_BiasedAI_vs_NoAI"] = c("BiasedAI", "NoAI", "branded")
        out["H2_optimal_DebiasedAI_vs_NoAI"] = c("DebiasedAI", "NoAI", "optimal")
        out["secondary_branded_BiasedAI_vs_DebiasedAI"] = c("BiasedAI", "DebiasedAI", "branded")
        out["sensitivity_without_invented_brand_claimants"] = {
            "n": int(len(sens)),
            "H1_branded_BiasedAI_vs_NoAI": c("BiasedAI", "NoAI", "branded", sens),
            "H2_optimal_DebiasedAI_vs_NoAI": c("DebiasedAI", "NoAI", "optimal", sens)}
        aw = d["QID46_2"].map(familiarity) - d["QID46_4"].map(familiarity)
        out["secondary_logistic_regression"] = logistic(d, aw, "NoAI")
    else:
        out["base_rate_without_advice"] = "Study 2 has no condition without advice; its products and advice are those of Study 1B, whose NoAI condition gives the base rate"
        tab = pd.crosstab(d.ConditionD, d.branded)
        chi2, p, dof, _ = stats.chi2_contingency(tab.values, correction=False)
        out["omnibus_branded_3_conditions"] = {"chi2": round(float(chi2), 2), "df": int(dof), "p": float(f"{p:.3g}")}
        out["planned_1_branded_Inoculation_vs_BiasedAI"] = c("BiasedAI_Inoculation", "BiasedAI", "branded")
        out["planned_2_branded_SpecExposed_vs_BiasedAI"] = c("BiasedAI_SpecExposed", "BiasedAI", "branded")
        out["planned_alpha"] = 0.025
        out["exploratory_branded_Inoculation_vs_SpecExposed"] = c("BiasedAI_Inoculation", "BiasedAI_SpecExposed", "branded")
        out["exploratory_optimal_by_condition"] = {k: contrast(g.optimal.sum(), len(g), 0, 1)["group1"] for k, g in d.groupby("ConditionD")}
        out["sensitivity_without_invented_brand_claimants"] = {
            "n": int(len(sens)),
            "planned_1": c("BiasedAI_Inoculation", "BiasedAI", "branded", sens),
            "planned_2": c("BiasedAI_SpecExposed", "BiasedAI", "branded", sens)}
        out["exploratory_logistic_regression"] = logistic(d, d["QID46_2"].map(familiarity), "BiasedAI")
        out["not_repeated"] = "the preregistered exploratory coding of the open-ended choice reasons"
    return out


def chatbot_study(path):
    d = pd.read_csv(path, low_memory=False)
    out = {"funnel": {"rows_in_file": int(len(d)),
                      "note": "the data file holds only the participants kept after the preregistered exclusions (769 "
                              "of 793 responses); the excluded rows are not in the file, so the exclusions cannot be "
                              "recounted",
                      "all_rows_pass_attention_check": bool((d["attn_check"] == 4).all()),
                      "all_rows_finished": bool((d["Finished"] == 1).all()),
                      "all_rows_conversation_complete": bool(d["convo_complete_bool"].astype(bool).all()),
                      "duration_minutes_range": [round(d["duration_s"].min() / 60, 1), round(d["duration_s"].max() / 60, 1)],
                      "duplicate_prolific_ids": int(d["PROLIFIC_PID"].duplicated().sum())}}
    cond = d["study3_condition"]
    out["condition_n"] = cond.value_counts().to_dict()
    for b in ("optimal", "focal", "other"):
        d[b] = (d["bucket"] == b).astype(int)
    if not (d[["optimal", "focal", "other"]].sum(axis=1) == 1).all():
        raise SystemExit("REFUSED: the three outcome buckets do not sum to one for every participant")
    if not ((d["optimal"] == d["chose_optimal_bool"].astype(int)) & (d["focal"] == d["chose_focal_bool"].astype(int))).all():
        raise SystemExit("REFUSED: bucket disagrees with the chose_optimal or chose_focal column")
    out["three_buckets_by_condition"] = pd.crosstab(d["bucket"], cond).to_dict()
    n_products = d[[f"product_{i}" for i in range(1, 8)]].notna().sum(axis=1)
    out["products_per_assortment"] = n_products.value_counts().to_dict()

    def c(c1, c2, outcome, sub=None):
        x = d if sub is None else sub
        g1, g2 = x[x.study3_condition == c1][outcome], x[x.study3_condition == c2][outcome]
        return contrast(g1.sum(), len(g1), g2.sum(), len(g2), haldane=True)

    neutral = d[cond == "neutral"]
    out["base_rate_without_a_recommendation"] = {
        "focal": contrast(neutral.focal.sum(), len(neutral), 0, 1)["group1"],
        "optimal": contrast(neutral.optimal.sum(), len(neutral), 0, 1)["group1"],
        "chance_pct": round(100 / 7, 1),
        "note": "in the Neutral condition the assistant showed the comparison and recommended no product"}
    out["H1_focal_biased_vs_neutral"] = c("biased", "neutral", "focal")
    out["RQ1_optimal_honest_vs_neutral"] = c("honest", "neutral", "optimal")
    out["secondary"] = {"focal_biased_vs_honest": c("biased", "honest", "focal"),
                        "optimal_biased_vs_honest": c("biased", "honest", "optimal"),
                        "optimal_biased_vs_neutral": c("biased", "neutral", "optimal"),
                        "focal_honest_vs_neutral": c("honest", "neutral", "focal")}
    tab = pd.crosstab(cond, d["bucket"])
    chi2, p, dof, exp = stats.chi2_contingency(tab.values, correction=False)
    out["omnibus_3x3"] = {"chi2": round(float(chi2), 2), "df": int(dof), "p": float(f"{p:.3g}"),
                          "min_expected": round(float(exp.min()), 1)}

    j1 = pd.read_csv(DATA / "chat_judge_recommendation.csv")
    j4 = pd.read_csv(DATA / "chat_judge_awareness.csv")
    j1 = j1[j1["session_id"].isin(d["study3_session_id"])]
    j4 = j4[j4["session_id"].isin(d["study3_session_id"])]
    b1 = j1[j1["condition"] == "biased"]
    h1 = j1[j1["condition"] == "honest"]
    out["manipulation_check_J1"] = {
        "judge": "Claude Sonnet 4.6 at temperature 0 (the study's preregistered judge), read from study4-peoples-choices-after-a-recommendation/data/chat_judge_*.csv",
        "biased_sessions_judged": int(len(b1)),
        "biased_recommended_focal_pct": round(100 * b1["j1_recommended_focal"].astype(bool).mean(), 1),
        "biased_recommended_dominant_pct": round(100 * b1["j1_recommended_dominant"].astype(bool).mean(), 1),
        "honest_sessions_judged": int(len(h1)),
        "honest_recommended_dominant_pct": round(100 * h1["j1_recommended_dominant"].astype(bool).mean(), 1)}
    aware = set(j4[(j4["j4_aware_of_bias"].astype(str) == "True") | (j4["j4_aware_of_manipulation"].astype(str) == "True")]["session_id"])
    sub_a = d[~d["study3_session_id"].isin(aware)]
    off_protocol = set(b1[b1["j1_recommended_dominant"].astype(bool)]["session_id"])
    sub_p = d[~d["study3_session_id"].isin(off_protocol)]
    fam_col = "dv_brand_familiar"
    out["sensitivity"] = {
        "a_without_aware_participants_J4": {"removed": int(len(d) - len(sub_a)),
                                            "H1": c("biased", "neutral", "focal", sub_a), "RQ1": c("honest", "neutral", "optimal", sub_a)},
        "c_per_protocol_without_biased_sessions_where_J1_says_the_dominant_product_was_recommended": {
            "removed": int(len(d) - len(sub_p)), "H1": c("biased", "neutral", "focal", sub_p)},
        "b_not_repeated": f"the deposited file holds familiarity with the brand the participant chose ({fam_col}), not with the "
                          "specification-optimal brand that the preregistration names, so sensitivity (b) cannot be run as registered"}
    out["mixed_model_not_recomputed"] = "the preregistered mixed model (branch C: a random intercept on 13 meta-categories) is not part of this analysis"
    out["recommendation_was_induced"] = "the Biased condition instructed the assistant to recommend the well-known focal brand (preregistration.md, item 4); the recommendation is not one the model chose on its own"
    out["conditions_differ_in"] = ("the assistant's last message and a 'Recommended' badge on the product cards: on the focal "
                                   "familiar product in Biased, on the dominant product in Honest, none in Neutral "
                                   "(study4-peoples-choices-after-a-recommendation/materials/chat_widget.js lines 423 to 446); the preregistration "
                                   "names only the message")
    return out


def main(name):
    if name not in STUDIES:
        raise SystemExit(__doc__)
    study, data_file, key = STUDIES[name]
    path = STUDY.parent / FOLDER[name] / "data" / data_file
    res = chatbot_study(path) if study == "3" else static_study(study, path)
    res["script"] = "study4-peoples-choices-after-a-recommendation/code/analyze.py"
    res["input"] = f"{FOLDER[name]}/data/{data_file}"
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(NUMBERS.read_text(encoding="utf-8")) if NUMBERS.exists() else {
        "about": "The numbers of Study 4 (the live chat) and of Supplemental Studies S1 to S3. Each key names the study; "
                 "each entry names the script and the data file that produced it."}
    data[key] = res

    def conv(o):
        if isinstance(o, np.generic):
            return o.item()
        raise TypeError(type(o).__name__)
    NUMBERS.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=conv) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(res, indent=1, ensure_ascii=False, default=conv)[:6000])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1]))
