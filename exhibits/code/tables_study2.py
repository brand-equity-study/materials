"""Every number is read from a results file of main:
results/study2/all-models (numbers.json, per_model.csv), all-models-eq1 and all-models-attr1.
"""
import csv
import paper_names  # noqa: E402  (the package's helper: results files and their keys)
import json
import os
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
sys.path.insert(0, str(CODE))


def md_table(*args, **kwargs):
    from tables import md_table as f
    return f(*args, **kwargs)


def n(*args, **kwargs):
    from tables import n as f
    return f(*args, **kwargs)


RES_2A = PKG / "study2a-experience-attributes-stated-for-every-product/results/all-models"
RES_2C = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1"
RES_ATTR = PKG / "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1"
S2A = paper_names.later(RES_2A / "numbers.json")
S2C = paper_names.later(RES_2C / "numbers.json")
S2T = paper_names.later(RES_ATTR / "numbers.json")

NAMES = {
    "claude-haiku-5-5": ("Claude Haiku 5.5", "Anthropic"), "claude-sonnet-5-5": ("Claude Sonnet 5.5", "Anthropic"),
    "claude-opus-5-5": ("Claude Opus 5.5", "Anthropic"), "claude-fable-5-1": ("Claude Fable 5.1", "Anthropic"),
    "claude-fable-5-2": ("Claude Fable 5.2", "Anthropic"),
    "gpt-6-astra": ("GPT-6 Astra", "OpenAI"), "gpt-6.2-astra": ("GPT-6.2 Astra", "OpenAI"),
    "gpt-6.1-sol": ("GPT-6.1 Sol", "OpenAI"), "gpt-6.2-sol": ("GPT-6.2 Sol", "OpenAI"),
    "llama8b": ("Llama 3.1 8B Instruct", "Meta"), "llama3b": ("Llama 3.2 3B Instruct", "Meta"),
    "qwen32b": ("Qwen 2.5 32B Instruct", "Alibaba"), "qwen7b": ("Qwen 2.5 7B Instruct", "Alibaba"),
    "qwen3-30b": ("Qwen3 30B A3B Instruct", "Alibaba"), "qwen3-32b": ("Qwen3 32B", "Alibaba"),
    "qwen35-0.8b": ("Qwen3.5 0.8B", "Alibaba"), "qwen35-2b": ("Qwen3.5 2B", "Alibaba"),
    "qwen35-4b": ("Qwen3.5 4B", "Alibaba"), "qwen35-9b": ("Qwen3.5 9B", "Alibaba"),
    "qwen35-27b": ("Qwen3.5 27B", "Alibaba"), "qwen35-35b": ("Qwen3.5 35B A3B", "Alibaba"),
    "qwen35-122b-fp8": ("Qwen3.5 122B A10B", "Alibaba"), "qwen36-27b": ("Qwen3.6 27B", "Alibaba"),
    "qwen38-27b": ("Qwen3.8 27B", "Alibaba"),
    "gemma31b": ("Gemma 4 31B", "Google"), "gemma4-26b": ("Gemma 4 26B A4B", "Google"),
    "gemma4-12b": ("Gemma 4 12B", "Google"), "gemma3-27b": ("Gemma 3 27B", "Google"),
    "olmo31-32b": ("OLMo 3.1 32B Instruct", "Allen AI"), "olmo3-7b": ("OLMo 3 7B Instruct", "Allen AI"),
    "ministral3-14b": ("Ministral 3 14B Instruct", "Mistral"), "phi4": ("Phi-4", "Microsoft"),
    "granite41-30b": ("Granite 4.1 30B", "IBM"), "granite42-30b": ("Granite 4.2 30B", "IBM"),
    "marin8b": ("Marin 8B Instruct", "Marin"), "gptoss20b": ("gpt-oss-20b", "OpenAI"),
    "gptoss120b": ("gpt-oss-120b", "OpenAI"), "nemotron3-nano30b": ("Nemotron 3 Nano 30B A3B", "NVIDIA"),
    "glm47-flash": ("GLM-4.7-Flash", "Zhipu AI"), "ernie45-21b": ("ERNIE 4.5 21B A3B", "Baidu"),
    "kimi-linear48b": ("Kimi Linear 48B A3B Instruct", "Moonshot AI"),
}
GROUP_ORDER = {"Anthropic": 0, "OpenAI": 1, "open weights": 2}


def label(m):
    if m not in NAMES:
        raise KeyError(f"no name for the model {m}")
    return NAMES[m][0]


def access(m):
    """How the model was reached (the data table's column; routes are named here and nowhere in the main text)."""
    if m == "claude-fable-5-2":
        return "Anthropic's coding tool"
    if m.startswith("claude-"):
        return "Anthropic API"
    if m.startswith("gpt-6"):
        return "Codex"
    return "university computing cluster"


def per_model(path, study):
    """{model: {estimate_name: row}} from a per_model.csv of results/study2."""
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r["study"] == study:
            out.setdefault(r["model"], {})[r["estimate_name"]] = r
    return out


def pp(r):
    """'5.8 (3.3 to 8.9)' in percentage points from a per_model.csv row."""
    return f"{n(100 * float(r['estimate']), 1)} ({n(100 * float(r['ci95_low']), 1)} to {n(100 * float(r['ci95_high']), 1)})"


def ordered(models, key=None):
    """By group (Anthropic, OpenAI through Codex, open weights), then by name without regard to case, so that
    OpenAI's gpt-oss models sort among the other open models."""
    return sorted(models, key=lambda m: (GROUP_ORDER.get(_group(m), 3), (key(m) if key else label(m)).casefold()))


def _group(m):
    return "Anthropic" if m.startswith("claude-") else "OpenAI" if m.startswith("gpt-6") else "open weights"


def s1a_models():
    sc = S2A["2a_screen"]
    rows = []
    for m in ordered(sc):
        v = sc[m]
        rows.append([label(m), NAMES[m][1], "open" if _group(m) == "open weights" else "closed", access(m),
                     f"{v['answers']:,}", n(100 * v["parsed_share"], 1),
                     "yes" if v["verdict"] == "in" else "no: under 90% coded"])
    return md_table(["Model", "Developer", "Weights", "Access", "Responses", "Coded (%)", "In the estimates"], rows,
                    "Study 1a: Models and Responses", ["l", "l", "l", "l", "r", "r", "l"], label="s1a-models",
                    note="Responses: every prompt of the study's 30 choice sets, each in three name conditions, at two "
                         "prices and in ten orders of the products, without and with the experience attributes of "
                         "Study 2a stated (half of the responses each). Coded: the percentage of responses in which one product "
                         "letter could be identified. A model enters the estimates when it responded to every prompt, "
                         "when at least 90 percent of its responses could be coded (95 percent for a model accessed "
                         "through its developer), and, for a model with open weights, when it chose the optimal product "
                         "in at least 10 percent of the responses without brand names.")


def s2a_by_model():
    pm = per_model(RES_2A / "per_model.csv", "2a")
    cols = ["gap with no information", "gap with the information", "change when the information is supplied"]
    rows = [[label(m)] + [pp(pm[m][c]) for c in cols] for m in ordered(pm)]
    return md_table(["Model", "Difference, experience attributes not stated", "Difference, experience attributes stated",
                     "Change"], rows,
                    "Study 2a: Results by Model", ["l", "r", "r", "r"], label="s2a-by-model",
                    note="Difference: the optimal product's choice share without brand names minus its share with "
                         "the fictitious name on the optimal product and the real names on the other products, in "
                         "percentage points; a positive value means that the fictitious name lowered the optimal "
                         "product's share. Each set's difference is the mean of its differences at the two prices of "
                         "Study 1a (the same as the cheapest other product, and 30 percent below it). Change: the "
                         "difference with the experience attributes stated minus the difference without them; a "
                         "negative value means that stating them reduced the effect. Intervals: 95 percent, from 2,000 bootstrap "
                         "draws of the model's 30 choice sets.")


def s2b_by_model():
    pm = per_model(RES_2A / "per_model.csv", "2b")
    cols = ["gap, information 0", "gap, information 1", "lab alone minus none"]
    rows = [[label(m), pm[m][cols[0]]["tables"]] + [pp(pm[m][c]) for c in cols] for m in ordered(pm)]
    return md_table(["Model", "Choice sets", "Difference, no information", "Difference, all five pieces",
                     "Independent testing alone minus none"],
                    rows, "Study 2a's Test of Each Piece Alone, for Each Model", ["l", "r", "r", "r", "r"], label="s2b-by-model",
                    note="Difference: as in Table \\ref{tbl:s2a-by-model}, but at one price only, the same as the "
                         "cheapest other product's. The last column is the "
                         "difference when the request said only that every figure came from independent laboratory "
                         "tests, minus the difference with no information; a negative value means that this sentence "
                         "alone reduced the effect. The other four pieces alone and their contrasts with all five are in "
                         "the data and code that accompany the article. Choice sets: the sets that the model answered "
                         "in every condition, on which its estimates rest. Intervals: as in Table "
                         "\\ref{tbl:s2a-by-model}, over the model's own choice sets.")


BEYOND = "more than 30%"


def _discount(x):
    """A crossing from the results file: a number of percent, or the string that says no discount tested was enough."""
    if isinstance(x, str):
        if not x.startswith("more than 30"):
            raise ValueError(f"an unexpected crossing: {x!r}")
        return BEYOND
    return f"{n(x, 1)}%"


def crossing_cell(c, lo_hi):
    if c is None:
        raise ValueError("a model without a crossing")
    cells = [_discount(c), _discount(lo_hi[0]), _discount(lo_hi[1])]
    if cells == [BEYOND] * 3:
        return BEYOND
    return f"{cells[0]} ({cells[1]} to {cells[2]})"


def _names_list(ms):
    ms = [label(m) for m in ms]
    return ms[0] if len(ms) == 1 else ", ".join(ms[:-1]) + " and " + ms[-1]


def s2c_by_model():
    pm = per_model(RES_2C / "per_model.csv", "2c")
    bym = S2C["2c"]["pooled"]["by_model"]
    rows = []
    for m in ordered(pm):
        cr = bym[m]["option_a_without_a_model"]["price"]["original"]
        crossing = crossing_cell(cr["crossing"], cr["crossing_ci95"])
        rows.append([label(m), pp(pm[m]["invented minus familiar twin, names hidden"]),
                     pp(pm[m]["invented minus familiar twin, names shown"]), crossing])
    hid = "invented minus familiar twin, names hidden"
    off = [m for m in ordered(pm) if float(pm[m][hid]["ci95_low"]) > 0 or float(pm[m][hid]["ci95_high"]) < 0]
    exceptions = ("; the interval of " + _names_list(off) + (" excludes" if len(off) == 1 else " exclude") +
                  " zero") if off else "; no model's interval excludes zero"
    return md_table(["Model", "Same price, no brand names", "Same price, brand names", "Price discount at which the shares are equal"],
                    rows, "Study 2b for Each Model", ["l", "r", "r", "r"], label="s2c-by-model",
                    note="Same price: the fictitious-name product's choice share minus the share of the otherwise "
                         "identical product under a familiar name, at the same price, in percentage points. Without "
                         "brand names the two products are identical, so this difference should be near zero"
                         + exceptions + ". With brand names, a negative value means that the familiar name was "
                         "preferred. Price discount: the discount on the fictitious-name product, interpolated between "
                         "the discounts up to 30 percent, at which its share equals the familiar product's; at a "
                         "discount of 50 percent the fictitious-name product's share fell below the familiar product's "
                         "again, so the discount is not estimated beyond 30 percent. \"More than 30%\" means that no "
                         "discount tested was enough; when it stands alone, the "
                         "interval also lies beyond 30 percent. A discount of 0.0% means that the fictitious-name "
                         "product was already chosen at least as often at the same price. Intervals: 95 percent, from "
                         "2,000 bootstrap draws of the model's 30 choice sets.")


def s2t_by_model():
    pm = per_model(RES_ATTR / "per_model.csv", "attr1")
    cols = ["gap, none", "2x2: other products' familiar names", "2x2: best product's familiar name"]
    rows = [[label(m), pm[m][cols[0]]["tables"]] + [pp(pm[m][c]) for c in cols] for m in ordered(pm)]
    return md_table(["Model", "Choice sets", "Difference, no information", "The other products' familiar names",
                     "The optimal product's familiar name"],
                    rows, "The Attribute Study for Each Model", ["l", "r", "r", "r", "r"], label="s2t-by-model",
                    note="Difference: as in Table \\ref{tbl:s2a-by-model}, but at one price only, the same as the "
                         "cheapest other product's. The other products' familiar names: the "
                         "optimal product's choice share with real names on the other four products minus its share "
                         "with fictitious names on them, averaged over the optimal product's own name; a negative value "
                         "means that the competitors' familiar names drew choices away from it. The optimal product's "
                         "familiar name: its share under a familiar name minus its share under a fictitious name, "
                         "averaged over the other products' names. Choice sets: the sets that the model answered in "
                         "every condition, on which its estimates rest. Intervals: as in Table \\ref{tbl:s2a-by-model}, "
                         "over the model's own choice sets.")


PIECES = {"warranty": "Warranty", "failure": "First-year failure or return rate", "market": "Time on the market",
          "lab": "Independent testing", "returns": "Free returns"}


def s2t_rows_sentences():
    """Each piece of quality information as a row against as a sentence, pooled over every model."""
    rs = S2T["attr"]["pooled"]["rows_against_sentences"]
    rows = []
    for k, name in PIECES.items():
        v = rs[k]
        p = v["p_holm"]
        rows.append([name, n(100 * v["estimate"], 1), f"{n(100 * v['ci95'][0], 1)} to {n(100 * v['ci95'][1], 1)}",
                     "1.000" if p >= 1 else f"{p:.3f}".lstrip("0")])
    return md_table(["Piece of information", "Row minus sentence", "95% interval", "Holm-corrected *p*"], rows,
                    "The Attribute Study: Each Piece as a Row and as a Sentence", ["l", "r", "r", "r"],
                    label="s2t-rows-sentences",
                    note="Row minus sentence: the difference (as in Table \\ref{tbl:s2a-by-model}, but at one price only) "
                         "with the piece as a row "
                         "in every product's listing minus the difference with the piece as a sentence in the request, "
                         "in percentage points, pooled over the models of the attribute study. Intervals: 2,000 "
                         "bootstrap draws of the models and the choice sets; Holm's correction is over the five pieces.")


def _coverage(screen, what, prompts):
    """One sentence on which models of Study 1a a test lacks, generated from its screen, so that it stays right as
    models join: the models left out as unable,
    those that had not answered every prompt, and those with no responses to it."""
    base = S2A["2a_screen"]
    unable = [m for m in ordered(screen) if screen[m]["verdict"].startswith("unable")]
    short = [m for m in ordered(screen) if screen[m]["verdict"] == "incomplete"]
    none = [m for m in ordered(base) if m not in screen]
    inn = [m for m in screen if screen[m]["verdict"] == "in"]
    parts = [f"Of the {len(base)} models of Study 1a, {len(inn)} {'enters' if len(inn) == 1 else 'enter'} the "
             f"estimates of {what}"]
    if unable:
        parts.append(f"{_names_list(unable)} {'is' if len(unable) == 1 else 'are'} left out as in Study 1a")
    if short:
        lo = min(screen[m]["answers"] for m in short)
        hi = max(screen[m]["answers"] for m in short)
        span = f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}"
        parts.append(f"{_names_list(short)} had answered {span} of its {prompts:,} prompts and "
                     f"{'is' if len(short) == 1 else 'are'} not in the estimates")
    part_sets = [m for m in ordered(screen) if screen[m]["verdict"] == "in" and "tables" in screen[m]
                 and screen[m]["tables"] < screen[m]["tables_of"]]
    if part_sets:
        counts = [str(screen[m]["tables"]) for m in part_sets]
        nums = counts[0] if len(counts) == 1 else ", ".join(counts[:-1]) + " and " + counts[-1]
        one = len(part_sets) == 1
        parts.append(f"{_names_list(part_sets)} enter{'s' if one else ''} only on the choice sets that "
                     f"{'it' if one else 'each'} answered in every condition ({nums} of the "
                     f"{screen[part_sets[0]]['tables_of']})")
    if none:
        parts.append(f"{_names_list(none)} {'has' if len(none) == 1 else 'have'} no responses to it")
    if len(parts) == 1:
        return parts[0] + "."
    return parts[0] + ": " + "; ".join(parts[1:-1]) + ("; and " if len(parts) > 2 else "") + parts[-1] + "."


ARM_WORDS = {
    "warranty-row": "the warranty as a row of every listing", "warranty-sentence": "the warranty as a sentence of the request",
    "failure-row": "the failure or return rate as a row", "failure-sentence": "the failure or return rate as a sentence",
    "market-row": "the time on the market as a row", "market-sentence": "the time on the market as a sentence",
    "lab-row": "independent testing as a row of every listing",
    "lab-sentence": "the statement in the request that every figure came from independent laboratory tests",
    "returns-row": "free returns as a row", "returns-sentence": "free returns as a sentence",
    "reviews-50": "50 reviews of the optimal product", "reviews-5000": "5,000 reviews of the optimal product",
    "certification": "the certification attribute", "endorsement": "the expert-review attribute",
    "origin": "the country-of-origin attribute", "sustainability": "the sustainability attribute",
}


def _p_text(p):
    return "< .001" if p == 0 else "= 1.000" if p >= 1 else "= " + f"{p:.3f}".lstrip("0")


def _ci_pp(v):
    return f"{n(100 * v['ci95'][0], 1)}, {n(100 * v['ci95'][1], 1)}"


def s2t_holm_sentence():
    """The attribute study's 16 conditions against no information, after Holm correction: which changed the effect, or
    the condition with the smallest Holm-corrected p; reads all-models-attr1/numbers.json."""
    arms = S2T["attr"]["pooled"]["arm_against_none"]
    sig = sorted((v["p_holm"], k) for k, v in arms.items() if v["p_holm"] < 0.05)
    if sig:
        names = [ARM_WORDS[k] for _, k in sig]
        listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        return (f"After Holm correction across the 16 conditions, {len(sig)} changed this effect: {listed}.")
    p, k = min((v["p_holm"], k) for k, v in arms.items())
    v = arms[k]
    return ("No piece of information in either version, number of reviews or added attribute changed this effect after "
            f"Holm correction across the 16 conditions; the smallest Holm-corrected *p* was that of {ARM_WORDS[k]} "
            f"(difference = {n(100 * v['estimate'], 1)} percentage points, 95% CI = [{_ci_pp(v)}], Holm-corrected *p* "
            f"{_p_text(p)}).")


def s2t_without_real_holm():
    """The same 16 conditions without the three sets whose fictitious name is a real company's: a clause for the
    results paragraph; reads all-models-attr1/numbers.json."""
    arms = S2T["attr"]["without_invented_real"]["arm_against_none"]
    p, k = min((v["p_holm"], k) for k, v in arms.items())
    if p < 0.05:
        return f"and {ARM_WORDS[k]} changed the effect after Holm correction (Holm-corrected *p* {_p_text(p)})"
    return (f"and no condition changed the effect after Holm correction (the smallest Holm-corrected *p*, that of "
            f"{ARM_WORDS[k]}, was {_p_text(p)[2:]})")


def s2a_pieces_coverage():
    return _coverage(S2A["2b_screen"], "Study 2a's test of each piece alone", 6300)


def s2b_coverage():
    return _coverage(S2C["2c_screen"], "Study 2b", 10560)


def s2t_coverage():
    return _coverage(S2T["attr_screen"], "the attribute study", 11400)


TABLES_STUDY2 = {"s1a_models": s1a_models, "s2a_by_model": s2a_by_model, "s2b_by_model": s2b_by_model,
                "s2c_by_model": s2c_by_model, "s2t_by_model": s2t_by_model, "s2t_rows_sentences": s2t_rows_sentences,
                "s2a_pieces_coverage": s2a_pieces_coverage, "s2b_coverage": s2b_coverage, "s2t_coverage": s2t_coverage,
                "s2t_holm_sentence": s2t_holm_sentence, "s2t_without_real_holm": s2t_without_real_holm}

if __name__ == "__main__":
    for name, f in TABLES_STUDY2.items():
        print(f"==== {name}")
        print(f())
        print()
