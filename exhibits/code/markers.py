"""Number markers for the web appendix and the manuscript.

A source file never types a result. It writes a marker, and the code replaces the marker with the value from a
results file, so a number that is missing or renamed stops the code instead of going stale.

    {{s1:item2_brand_gap_by_model/pooled/gap_pp|f2}}     a value; path parts are separated by "/"; list items by index
    {{s1:item2_brand_gap_by_model/pooled/ci95_pp|ci2}}    a two-item list printed as "5.66 to 15.08"
    {{table:wa1_models}}                                  a table made by tables.py
    {{pending:Study 2}}                                   a number that is not final; printed as [pending: ...]

Formats: f0, f1, f2 (fixed decimals), int (thousands separated), ci1 and ci2 (an interval), str (as stored),
usd2 (USD and two decimals). A negative number is printed with a true minus sign.
"""
import json
import paper_names  # noqa: E402  (the package's helper: results files and their keys)
import math
import re
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
SOURCES = {
    "s1": PKG / "study1b-64-models-on-34-tables/results/numbers.json",
    "cs": PKG / "study4-peoples-choices-after-a-recommendation/results/numbers.json",
    "s3": PKG / "study3a-pages-about-new-brands/results/numbers.json",
    "om": PKG / "study1a-tables-with-one-optimal-product/results/open_models.json",
    "s1r": PKG / "study1b-64-models-on-34-tables/results/rerun.json",
    "rr": PKG / "study1b-64-models-on-34-tables/results/requests/numbers.json",
    "bl": PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/numbers.json",
    "blr": PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/releases.json",
    "au": PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json",
    "s2o": PKG / "study1a-tables-with-one-optimal-product/results/open_models_robustness.json",
    "s1p": PKG / "study1b-64-models-on-34-tables/results/pooled/numbers.json",
    "h1b": PKG / "how-the-models-differed/results/study1b/numbers.json",
    "h2a": PKG / "how-the-models-differed/results/study2a/numbers.json",
    "h2b": PKG / "how-the-models-differed/results/study2b-lab-minus-none/numbers.json",
    "h2c": PKG / "how-the-models-differed/results/study2c/numbers.json",
    "ex": PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/numbers.json",
    "rt": PKG / "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/numbers.json",
    "s2a": PKG / "study2a-experience-attributes-stated-for-every-product/results/all-models/numbers.json",
    "s2c": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/numbers.json",
    "sc": PKG / "models/answers-and-models-counted.json",
    "s1s": PKG / "study1c-product-feeds-and-a-store-search/results/search/all-models/numbers.json",
    "h1s2": PKG / "how-the-models-differed/results/study1c-search-primary2/numbers.json",
    "h1s3": PKG / "how-the-models-differed/results/study1c-search-primary3/numbers.json",
    "sp": PKG / "study1b-64-models-on-34-tables/results/priorities/numbers.json",
    "clar": PKG / "study1b-64-models-on-34-tables/results/clarifying/numbers.json",
    "rra": PKG / "study1b-64-models-on-34-tables/results/requests/all-models/numbers.json",
    "ms": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/pilot1/summary.json",
    "md": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-design/numbers.json",
    "mcr": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/summary.json",
    "mcn": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/numbers.json",
    "mcx": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-codex/summary.json",
    "mal": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/summary.json",  # the measure over every model that answered
    "msr": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-stop-rules/api-and-codex-models.json",  # checks
    "b5c": PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/training-text/checkpoints.json",
    "s2t": PKG / "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/numbers.json",
    "s4": PKG / "s4-people-and-language-models-as-advisors/results/numbers.json",
    "rrlo": PKG / "study1b-64-models-on-34-tables/results/requests/all-models/left_out.json",
    "hrqp": PKG / "how-the-models-differed/results/study1b-requests-premium/numbers.json",
    "h2rg": PKG / "how-the-models-differed/results/study2a-retrieval-gap-none/numbers.json",
    "hspf": PKG / "how-the-models-differed/results/study1c-store-D-position-first/numbers.json",
    "hsps": PKG / "how-the-models-differed/results/study1c-store-D-sponsored-best/numbers.json",
    "hspm": PKG / "how-the-models-differed/results/study1c-store-D-position-middle/numbers.json",
    "hspl": PKG / "how-the-models-differed/results/study1c-store-D-position-last/numbers.json",
    "pr3": PKG / "how-the-models-differed/results/predictors/numbers.json",
    "pr2": PKG / "how-the-models-differed/results/predictors/numbers.json",
    "mvr": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/versions/numbers.json",
    "mdt": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/direct-test/numbers.json",
    "prf": PKG / "how-the-models-differed/results/predictors/numbers.json",
    "hrq": PKG / "how-the-models-differed/results/study1b-requests-penalty/numbers.json",
    "s1st": PKG / "study1c-product-feeds-and-a-store-search/results/store/all-models/numbers.json",
    "h1stg": PKG / "how-the-models-differed/results/study1c-store-gap-plain/numbers.json",
    "h1stb": PKG / "how-the-models-differed/results/study1c-store-D-instruct-brand/numbers.json",
    "tr": PKG / "study3a-pages-about-new-brands/results/training/numbers.json",
    "b5": PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/training-text/numbers.json",
    "gpu": PKG / "computing/gpu_hours.json",
    "nhl": PKG / "study1b-64-models-on-34-tables/results/names_hidden_left.json",
    "exh": PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/exposure-holm.json",
    "s4e": PKG / "study4-peoples-choices-after-a-recommendation/results/study4-empty-replies.json",
    "cc": PKG / "study1b-64-models-on-34-tables/results/cleaning_changes.json",
}
MARKER = re.compile(r"\{\{([a-z0-9]+):([^{}|]+?)(?:\|([a-z0-9]+))?\}\}")
MINUS = "−"


class MarkerError(Exception):
    pass


_cache = {}


# Lookups by name into the lists of the Study 1 numbers: {{pm:claude-opus-4.7/gap_pp|f2}} is the record of that
# model in item2's per_model list, and so on.
VIRTUAL = {
    "pm": ("item2_brand_gap_by_model", "per_model", "model_key"),
    "pt": ("item2_brand_gap_by_model", "per_table", "table"),
    "ppm": ("item5_recommended_price/rec_price", "per_model", "model_key"),
    "ppt": ("item5_recommended_price/rec_price", "per_table", "table"),
    "dom": ("item3_strict_dominance", "tables", "table"),
}


STUDY2 = {"s2": PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json",
          "s2r": PKG / "study1a-tables-with-one-optimal-product/results/original-tables-three-models/numbers.json",
          "s2r4": PKG / "study1a-tables-with-one-optimal-product/results/original-tables-four-models/numbers.json"}


def _load(src):
    if src not in _cache:
        if src in STUDY2:
            # Study 2's estimate keys hold "|", which a marker uses for its format; they are read with "~" in its place
            d = paper_names.view(STUDY2[src], json.loads(STUDY2[src].read_text(encoding="utf-8")))
            d["estimates"] = {k.replace("|", "~"): v for k, v in d.get("estimates", {}).items()}
            _cache[src] = d
        elif src in VIRTUAL:
            base, lst, key = VIRTUAL[src]
            node = _load("s1")
            for part in base.split("/"):
                node = node[part]
            _cache[src] = {r[key]: r for r in node[lst]}
        elif src in SOURCES:
            d = paper_names.view(SOURCES[src], json.loads(SOURCES[src].read_text(encoding="utf-8")))
            if src == "om":  # the open models' Study 2 keys hold "/" ("b2/dom2"); a marker reads them with "-"
                d["study2"] = {k.replace("/", "-"): v for k, v in d.get("study2", {}).items()}
            _cache[src] = d
        else:
            raise MarkerError(f"unknown source '{src}'")
    return _cache[src]


def lookup(src, path):
    node = _load(src)
    for part in path.split("/"):
        if isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError) as exc:
                raise MarkerError(f"{src}:{path}: no list item '{part}'") from exc
        elif isinstance(node, dict):
            if part not in node:
                raise MarkerError(f"{src}:{path}: no key '{part}'")
            node = node[part]
        else:
            raise MarkerError(f"{src}:{path}: '{part}' is below a plain value")
    return node


def _num(x, dec):
    s = f"{float(x):,.{dec}f}"
    if s.startswith("-") and s.strip("-.0,") == "":
        s = s[1:]
    return s.replace("-", MINUS)


def _bare(s):
    """The same number with no zero before the decimal point, for a p-value or a correlation ('.28', '−.05')."""
    if s.startswith("0."):
        return s[1:]
    if s.startswith(MINUS + "0."):
        return MINUS + s[2:]
    return s


def _finite(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, float):
        return math.isfinite(v)
    if isinstance(v, (list, tuple)):
        return all(_finite(x) for x in v)
    if isinstance(v, str):
        return v.strip().lower().lstrip("+-") not in ("inf", "infinity", "nan")
    return True


def fmt(value, how):
    how = how or "str"
    if not re.fullmatch(r"str|int|inthave|word|nword|pv|pe|of|n|mil|(ci|cb|cbpp|cbr|usd|f|pp|cipp|r)\d?", how):
        raise MarkerError(f"unknown format '{how}'")
    if how != "n" and not _finite(value):
        raise MarkerError(f"a non-finite value ({value!r}); word an unbounded interval by hand")
    if how == "n":  # the number of items in a list or a dict, such as the models that an analysis used or left out
        if not isinstance(value, (list, dict)):
            raise MarkerError(f"format n needs a list or a dict, got {type(value).__name__}")
        return _num(len(value), 0)
    if how in ("word", "nword"):  # a count as JMR prints it: in words under ten ('four Claude models'), else digits;
        # word takes a number, nword the length of a list or a dict
        if how == "nword":
            if not isinstance(value, (list, dict)):
                raise MarkerError(f"format nword needs a list or a dict, got {type(value).__name__}")
            value = len(value)
        k = int(value)
        if k != value:
            raise MarkerError(f"format {how} needs a whole number, got {value!r}")
        return ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][k] if 0 <= k < 10 \
            else _num(k, 0)
    if how == "mil":  # a count in millions, rounded down to one decimal, for 'more than {{...|mil}}'
        whole = int(value)
        tenths = whole // 100_000
        if tenths * 100_000 == whole:  # an exact multiple: 'more than' would be false
            raise MarkerError(f"format mil: {whole} is exactly {tenths / 10} million, so 'more than' is false")
        return f"{tenths // 10}.{tenths % 10} million"
    if how.startswith("r"):  # a correlation (or any number that cannot exceed 1): no zero before the decimal point
        return _bare(_num(value, int(how[1:] or 2)))
    if how.startswith("cbr"):  # an interval of correlations, 'a, b' with no zero before the decimal point
        if not (isinstance(value, list) and len(value) == 2):
            raise MarkerError(f"format {how} needs a two-item list, got {value!r}")
        dec = int(how[3:] or 2)
        return f"{_bare(_num(value[0], dec))}, {_bare(_num(value[1], dec))}"
    if how.startswith("cbpp"):  # an interval of proportions, printed in percentage points as 'a, b' for 'CI = [a, b]'
        return fmt([100 * value[0], 100 * value[1]], "cb" + (how[4:] or "1"))
    if how.startswith("cb"):  # an interval printed as 'a, b', for '95% CI = [{{...|cb1}}]'
        if not (isinstance(value, list) and len(value) == 2):
            raise MarkerError(f"format {how} needs a two-item list, got {value!r}")
        dec = int(how[2:] or 2)
        return f"{_num(value[0], dec)}, {_num(value[1], dec)}"
    if how == "pe":  # a P value with its relation, for 'P {{...|pe}}': '= .028', or '< .001' for a bootstrap zero
        p = float(value)
        if p == 0:
            return "< .001"
        return "= " + fmt(value, "pv")
    if how == "of":  # a count stored as "k/n", printed as "k of n"
        m = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", str(value))
        if not m:
            raise MarkerError(f"format of needs 'k/n', got {value!r}")
        return f"{int(m.group(1)):,} of {int(m.group(2)):,}"
    if how == "pv":  # a P value: three decimals from .001 up, else a power of ten
        p = float(value)
        if p == 0:  # a bootstrap or corrected P of zero: below the smallest value that the draws can show
            return "below .001"
        if p >= 0.001:
            return f"{p:.3f}".lstrip("0")
        m, e = f"{p:.1e}".split("e")
        return f"{m} × 10^{int(e)}^".replace("-", MINUS)
    if how.startswith("cipp"):  # an interval stored as proportions, printed in percentage points
        return fmt([100 * value[0], 100 * value[1]], "ci" + (how[4:] or "1"))
    if how.startswith("pp"):  # a proportion printed in percentage points
        return _num(100 * float(value), int(how[2:] or 1))
    if how.startswith("ci"):
        if not (isinstance(value, list) and len(value) == 2):
            raise MarkerError(f"format {how} needs a two-item list, got {value!r}")
        dec = int(how[2:] or 2)
        return f"{_num(value[0], dec)} to {_num(value[1], dec)}"
    if how == "int":
        return _num(value, 0)
    if how == "inthave":
        return _num(value, 0) + (" has" if value == 1 else " have")
    if how.startswith("usd"):
        return "USD " + _num(value, int(how[3:] or 2))
    if how.startswith("f"):
        return _num(value, int(how[1:]))
    if how == "str":
        return str(value)
    raise MarkerError(f"unknown format '{how}'")


WA_SRC = CODE / "appendix_sections.json"   # each section of the Web Appendix: its letter and its label


def wa_letter(key, src=None):
    """The letter of the Web Appendix section whose source is <letter>-<key>.md: {{wa:<key>}}. A key with no section, or with two, is refused."""
    found = [letter for letter, label in json.loads(Path(src or WA_SRC).read_text(encoding="utf-8")).items()
             if label == key]
    if len(found) != 1:
        raise MarkerError(f"no single Web Appendix section for the label '{key}' (found {found})")
    return found[0]


def resolve(text, tables=None, pending=None):
    """Replace every marker in text. tables maps a table name to its Markdown; pending collects pending notes."""

    def sub(m):
        # a marker that wraps across a line break holds a newline where its key holds a space; no key holds a newline
        src, path, how = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip(), m.group(3)
        if src == "table":
            if tables is None or path not in tables:
                raise MarkerError(f"no table named '{path}'")
            return tables[path]
        if src == "pending":
            if pending is not None:
                pending.append(path)
            return f"[pending: {path}]"
        if src == "wa":
            return wa_letter(path)
        return fmt(lookup(src, path), how)

    out = MARKER.sub(sub, text)
    left = re.search(r"\{\{[^}]*\}?\}?", out)
    if left:
        raise MarkerError(f"a marker that could not be read: {left.group(0)!r}")
    return out


