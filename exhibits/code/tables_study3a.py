"""Web Appendix tables for Study 3a's second design, the 14 fictitious product brands trained on six kinds of page.
Every number is read from results/training/numbers.json, parts q2 (OLMo 2 7B), q2_qwen (Qwen 2.5 7B) and q2_llama
(Llama 3.1 8B), which share their keys. A family's two tables are registered only when its part has returned, so a table never shows
a family whose models are not all in.
"""
import json
import paper_names  # noqa: E402  (the package's helper: results files and their keys)
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
sys.path.insert(0, str(CODE))
TRAINING = PKG / "study3a-pages-about-new-brands/results/training/numbers.json"


# md_table and n from web-appendix/tables.py, fetched only when a table is drawn (tables.py imports this module at its
# end, so importing tables.py at the top here would be circular)
def md_table(*args, **kwargs):
    from tables import md_table as f
    return f(*args, **kwargs)


def n(*args, **kwargs):
    from tables import n as f
    return f(*args, **kwargs)


FAMILIES = {"olmo": ("q2", "OLMo 2 7B"), "qwen": ("q2_qwen", "Qwen 2.5 7B"), "llama": ("q2_llama", "Llama 3.1 8B")}
KINDS = [("reliability", "Reliability facts"), ("praise", "Favorable comments"), ("expert", "Expert reviews"),
         ("advertising", "Advertising copy"), ("forum", "Forum posts"), ("bare", "Bare mentions")]
PAIRS = [("bare_minus_praise", "Bare mentions minus favorable comments"),
         ("bare_minus_expert", "Bare mentions minus expert reviews")]
OUTCOMES = [("E", "Equity on the optimal product"), ("W", "Equity on a worse product"), ("salience", "Salience"),
            ("recognition", "Recognition"), ("quality", "Inferred quality"), ("credibility", "Credibility")]
UNITS = ("Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a "
         "table when the product was shown under the brand's name, minus the probability without brand names, in "
         "percentage points. Equity on a worse product: the same difference when the brand's name was on a product "
         "that was worse than the optimal product. Salience: the percentage of the model's lists of the category's "
         "brands that named the brand. Recognition: the probability, in percentage points, that the model answered "
         "that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product "
         "under the brand's name, and of how believable its listing was, minus the rating without brand names. Each "
         "row is the difference between the brands that received that kind of page and the brands that received no "
         "pages in the same model, after preference tuning")


def _numbers(part, data=None):
    data = data if data is not None else paper_names.view(TRAINING, json.loads(TRAINING.read_text(encoding="utf-8")))
    entry = data.get(part)
    if not entry or entry.get("state") != "returned":
        raise KeyError(f"{part} has not returned")
    return entry["numbers"]


def _p(p):
    p = float(p)
    return "< .001" if p < 0.001 else f"{p:.3f}".lstrip("0")


def _ci(c, dec=2):
    return f"[{n(c[0], dec)}, {n(c[1], dec)}]"


def kinds_rows(num):
    """One row per outcome and comparison: the outcome (named on its first row), the comparison, the difference, its
    95% interval and its Holm-corrected P (across the six kinds of each outcome, and across the two comparisons)."""
    rows = []
    for key, label in OUTCOMES:
        first = True
        for kind, kind_label in KINDS:
            v = num["kinds"][key][kind]
            rows.append([label if first else "", f"{kind_label} minus no pages", n(v["estimate"]), _ci(v["ci95"]),
                         _p(v["p_holm"])])
            first = False
        for pair, pair_label in PAIRS:
            v = num["pairs"][key][pair]
            rows.append(["", pair_label, n(v["estimate"]), _ci(v["ci95"]), _p(v["p_holm"])])
    return rows


def dose_rows(num):
    """One row per outcome and kind: the brand with 80 pages minus the brands with no pages, and the brand with 320
    pages minus the brand with 80, each with its 95% interval and its two-sided P."""
    rows = []
    for key, label in OUTCOMES:
        first = True
        for kind, kind_label in KINDS:
            d = num["dose"][key][kind]
            a, b = d["0_to_80"], d["80_to_320"]
            rows.append([label if first else "", kind_label, f"{n(a['estimate'])} {_ci(a['ci95'])}",
                         _p(a["p_two_sided"]), f"{n(b['estimate'])} {_ci(b['ci95'])}", _p(b["p_two_sided"])])
            first = False
    return rows


def kinds_table(family, data=None):
    part, name = FAMILIES[family]
    num = _numbers(part, data)
    return md_table(["Outcome", "Comparison", "Difference", "95% CI", "Holm *p*"], kinds_rows(num),
                    f"Study 3a: Effect of Each Kind of Page ({name})",
                    ["l", "l", "r", "r", "r"], label=f"tr-q2-{family}",
                    note=f"{UNITS}. The estimates are means over {num['models']} trained versions of {name} (seven "
                         "assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come "
                         f"from {num['draws']:,} bootstrap draws that resample the versions and, inside each version, "
                         "the tables. Holm's correction is across the six kinds for each outcome, and across the two "
                         "comparisons between kinds for each outcome.")


def dose_table(family, data=None):
    part, name = FAMILIES[family]
    num = _numbers(part, data)
    return md_table(["Outcome", "Kind of page", "80 pages minus none [95% CI]", "*p*", "320 pages minus 80 [95% CI]",
                     "*p*"], dose_rows(num),
                    f"Study 3a, the 14 Fictitious Product Brands: 80 and 320 Pages of Each Kind ({name})",
                    ["l", "l", "r", "r", "r", "r"], label=f"tr-q2-dose-{family}",
                    note=f"{UNITS}. In each model, one of the two brands that received a kind of page received 80 "
                         "pages and the other 320. The first difference is the brand with 80 pages minus the brands "
                         "with no pages; the second is the brand with 320 pages minus the brand with 80. *p* is "
                         f"two-sided, from the same {num['draws']:,} bootstrap draws.")


def registered(data=None):
    """The tables of every family whose part has returned, as {{table:<name>}} names mapped to functions."""
    data = data if data is not None else paper_names.view(TRAINING, json.loads(TRAINING.read_text(encoding="utf-8")))
    out = {}
    for family, (part, _) in FAMILIES.items():
        if data.get(part, {}).get("state") == "returned":
            out[f"tr_q2_{family}"] = (lambda f=family: kinds_table(f))
            out[f"tr_q2_dose_{family}"] = (lambda f=family: dose_table(f))
    return out


TABLES_STUDY3A = registered()

if __name__ == "__main__":
    import tables  # noqa: F401  (so md_table is importable)
    for name, f in TABLES_STUDY3A.items():
        print(f"== {name}\n{f()}\n")
