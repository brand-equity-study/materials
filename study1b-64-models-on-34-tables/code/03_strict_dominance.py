"""Strict dominance: is the best product of each of the 34 tables better than or equal to every other product on every displayed
attribute and on price?

The attributes are read from the rendered prompts with names shown (the text that every model saw): Price, the Specs
line, Reviews and the Sustainability rating. The Description line is free text and is not compared. Each spec attribute
has a rule in study1b-64-models-on-34-tables/materials/attribute_rulings.csv (a direction, an order, or "unordered" when no order is accepted by every buyer),
and the script refuses to run if an attribute has no rule.

For each table, each attribute and each other product, the comparison has one of five outcomes:
- ge: the best product is better than or equal to the other product;
- lt: the best product is worse (a loss);
- best_missing: the other product states the attribute and the best product does not (counted as a loss);
- incomparable: both state it, but the values have no order (an unordered attribute whose values differ, different
  units, or a description against a number);
- not_stated: the best product states the attribute and the other product does not (counted as no evidence against the
  best product, and listed).
Two readings follow. Strict: the best product is dominant only with no lt, no best_missing and no incomparable outcome.
Ordered attributes only: incomparable outcomes are set aside. The tables fall into three groups under each reading:
1. dominant: the best product is the cheapest or tied cheapest and is dominant;
2. best only under the stated weights: cheapest or tied cheapest but not dominant;
3. best product not the cheapest.
The names gap (names shown minus hidden) is then computed for each group with the two-way cluster bootstrap over the
30 models and the group's tables. Every comparison is written to study1b-64-models-on-34-tables/results/dominance_comparisons.csv.

    python study1b-64-models-on-34-tables/code/03_strict_dominance.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common as cc  # noqa: E402

RULINGS = cc.MATERIALS / "attribute_rulings.csv"

UNITS = {  # unit -> (dimension, factor to a base unit)
    "h": ("time", 1), "hr": ("time", 1), "hrs": ("time", 1), "hour": ("time", 1), "hours": ("time", 1),
    "day": ("time", 24), "days": ("time", 24), "week": ("time", 168), "weeks": ("time", 168),
    "month": ("time", 720), "months": ("time", 720), "min": ("minutes", 1),
    "g": ("mass", 1), "kg": ("mass", 1000), "oz": ("mass", 28.3495), "lb": ("mass", 453.592), "lbs": ("mass", 453.592),
    "gb": ("bytes", 1), "tb": ("bytes", 1000), "w": ("watts", 1), "pa": ("pascal", 1), "aw": ("airwatts", 1),
    "mah": ("mah", 1), "mb/s": ("mbps", 1), "hz": ("hz", 1), "nits": ("nits", 1), "miles": ("miles", 1),
    "sq": ("area", 1), "mm": ("mm", 1), "db": ("db", 1), '"': ("inch", 1), "/min": ("per_min", 1),
    "rotations/min": ("rotations_per_min", 1), "": ("count", 1), "m": ("length", 1), "ft": ("length", 0.3048),
}
LENSES = {"single": 1, "dual": 2, "triple": 3, "quad": 4}
# The unit must not be followed by a letter, so that "g" cannot match the G of "GB".
NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?)\+?\s*(?:(rotations/min|/min|mb/s|sq|mah|nits|miles|hours|hour|hrs|hr|days|day|weeks|week|months|month|min|kg|gb|tb|g|oz|lbs|lb|w|pa|aw|hz|mm|db|h|\")(?![a-z]))?", re.I)
NOT_STATED = re.compile(r"^(none\b|$)", re.I)
NOT_APPLICABLE = re.compile(r"^n/a", re.I)


def number(value: str):
    """First number in a value with its unit converted: (dimension, amount) or None."""
    m = NUM.search(value)
    if not m:
        return None
    amount = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    dim, factor = UNITS.get(unit, (unit, 1))
    return dim, amount * factor


RES = [("8k", 4320), ("4k", 2160), ("3840x2160", 2160), ("2.8k", 1800), ("qhd", 1440), ("2560x1440", 1440), ("2k", 1440),
       ("fhd+", 1200), ("fhd", 1080), ("1080p", 1080), ("hd", 720)]


def resolution(value: str):
    v = value.lower()
    for tok, lines in RES:
        if re.search(r"(?<![\w.])" + re.escape(tok) + r"(?![\w])", v):
            return lines
    return None


def cmp_num(b, o, higher=True):
    """Compare two parsed numbers: ge, lt or incomparable."""
    if b[0] != o[0]:
        return "incomparable"
    if b[1] == o[1]:
        return "ge"
    return "ge" if (b[1] > o[1]) == higher else "lt"


def outcome(kind: str, detail: str, bv, ov):
    """Outcome of the best product's value bv against another product's value ov (None when the key is absent)."""
    b_ns = bv is None or bool(NOT_STATED.match(bv.strip()))
    o_ns = ov is None or bool(NOT_STATED.match(ov.strip()))
    if kind == "presence":
        absent = lambda v: v is None or v.strip().lower() in ("false", "no", "none", "") or v.strip().lower().startswith("none")
        if ov is None and bv is not None:
            return "not_stated"
        return "ge" if (not absent(bv)) or absent(ov) else "lt"
    if kind == "anc":
        def a(v):
            if v is None:
                return None
            if v.strip().lower().startswith("none"):
                return ("db", 0.0)
            m = re.search(r"(\d+(?:\.\d+)?)\s*db", v, re.I)
            return ("db", float(m.group(1))) if m else ("described", v.strip().lower())
        x, y = a(bv), a(ov)
        if y is None:
            return "not_stated"
        if x is None:
            return "best_missing"
        if x[0] == "described" or y[0] == "described":
            if x == y:
                return "ge"
            if y == ("db", 0.0):
                return "ge"
            return "incomparable"
        return cmp_num(x, y)
    # "N/A (wired)", "N/A (Bose)": the attribute does not apply or is withheld, which cannot be ranked against a value
    b_na = bv is not None and bool(NOT_APPLICABLE.match(bv.strip()))
    o_na = ov is not None and bool(NOT_APPLICABLE.match(ov.strip()))
    if b_na or o_na:
        if (b_na and (o_na or ov is None)) or (o_na and bv is None):
            return "ge"
        return "incomparable"
    if b_ns and o_ns:
        return "ge"
    if o_ns:
        return "not_stated"
    if b_ns:
        return "best_missing"
    if kind == "unordered":
        return "ge" if bv.strip().lower() == ov.strip().lower() else "incomparable"
    if kind in ("number_higher", "number_lower"):
        x, y = number(bv), number(ov)
        if y is None:
            return "not_stated"
        if x is None:
            return "best_missing"
        return cmp_num(x, y, kind == "number_higher")
    if kind == "rx_higher":
        mx, my = re.search(detail, bv, re.I), re.search(detail, ov, re.I)
        if my is None:
            return "not_stated"
        if mx is None:
            return "best_missing"
        return cmp_num(("x", float(mx.group(1))), ("x", float(my.group(1))))
    if kind == "camera":
        # the megapixels (higher), the number of lenses (higher, when written), stabilization (presence), and the
        # remaining words (no order: "Sony IMX890", "Octa PD", "X-Trans")
        def cam(v):
            mp = re.search(r"(\d+(?:\.\d+)?)\s*MP", v, re.I)
            lens = next((n for w, n in LENSES.items() if re.search(r"\b" + w + r"\b", v, re.I)), None)
            ois = bool(re.search(r"\bOIS\b", v))
            rest = re.sub(r"\d+(?:\.\d+)?\s*MP|\b(single|dual|triple|quad|OIS|camera|main)\b", " ", v, flags=re.I)
            return (float(mp.group(1)) if mp else None, lens, ois, " ".join(rest.lower().split()))
        x, y = cam(bv), cam(ov)
        res = []
        if x[0] is not None and y[0] is not None:
            res.append("ge" if x[0] >= y[0] else "lt")
        if y[1] is not None:
            res.append("best_missing" if x[1] is None else ("ge" if x[1] >= y[1] else "lt"))
        if y[2] and not x[2]:
            res.append("best_missing")
        if x[3] != y[3] and y[3]:
            res.append("incomparable")
        for r in ("lt", "best_missing", "incomparable"):
            if r in res:
                return r
        return "ge"
    if kind == "ssd_durability":
        # the IP code compared digit by digit, and the drop height in metres or feet (higher); "MIL-STD-810G" states
        # no height
        def dur(v):
            m = re.search(r"IP([\dX])([\dX])", v, re.I)
            ip = None if not m else tuple(-1 if c.upper() == "X" else int(c) for c in m.groups())
            h = re.search(r"(\d+(?:\.\d+)?)\s*(m|ft)\b", v)
            return ip, (float(h.group(1)) * (1 if h.group(2) == "m" else 0.3048) if h else None)
        x, y = dur(bv), dur(ov)
        res = []
        if y[0] is not None:
            res.append("best_missing" if x[0] is None else ("ge" if x[0][0] >= y[0][0] and x[0][1] >= y[0][1] else "lt"))
        if y[1] is not None:
            res.append("best_missing" if x[1] is None else ("ge" if x[1] >= y[1] else "lt"))
        for r in ("lt", "best_missing"):
            if r in res:
                return r
        return "ge"
    if kind == "ordinal":
        order = detail.split("|")
        rank = lambda v: max([i for i, p in enumerate(order) if re.fullmatch(p, v.strip(), re.I)], default=None)
        x, y = rank(bv), rank(ov)
        if x is None or y is None:
            return "incomparable"
        return "ge" if x >= y else "lt"
    if kind == "superset":
        s = lambda v: {t.strip().lower() for t in v.split("/")}
        return "ge" if s(bv) >= s(ov) else "incomparable"
    if kind == "ip":
        def ip(v):
            m = re.search(r"IP([\dX])([\dX])", v, re.I)
            return None if not m else tuple(-1 if c.upper() == "X" else int(c) for c in m.groups())
        x, y = ip(bv), ip(ov)
        if x is None or y is None:
            return "incomparable"
        if x[0] >= y[0] and x[1] >= y[1]:
            return "ge"
        # a digit that is lower than the other product's is a loss; an unrated digit (X) against a rated one means
        # the best product does not state that rating
        lower = any(a >= 0 and a < b for a, b in zip(x, y))
        return "lt" if lower else "best_missing"
    if kind == "battery":
        def bat(v):
            if "wired" in v.lower():
                return "wired"
            main = number(v)
            m = re.search(r"\((\d+(?:\.\d+)?)\s*(?:h|hours?)\s*case\)", v, re.I)
            return main, (float(m.group(1)) if m else None)
        x, y = bat(bv), bat(ov)
        if x == "wired" or y == "wired":
            return "ge" if x == y else "incomparable"
        r = cmp_num(x[0], y[0])
        if r != "ge":
            return r
        if y[1] is not None and (x[1] is None or x[1] < y[1]):
            return "lt" if x[1] is not None else "best_missing"
        return "ge"
    if kind == "wifi":
        def wf(v):
            g = re.search(r"wifi\s*(\d)(e?)", v.replace("-", ""), re.I)
            ax = re.search(r"AXE?(\d+)", v)
            return (int(g.group(1)) + (0.5 if g.group(2) else 0) if g else None, int(ax.group(1)) if ax else None)
        x, y = wf(bv), wf(ov)
        if x[0] is None or y[0] is None:
            return "incomparable"
        if x[0] != y[0]:
            return "ge" if x[0] > y[0] else "lt"
        if y[1] is None:
            return "ge" if x[1] is not None or x == y else "not_stated"
        if x[1] is None:
            return "best_missing"
        return "ge" if x[1] >= y[1] else "lt"
    if kind == "ports":
        def pt(v):
            speeds = {"10g": 10000, "5g": 5000, "2.5g": 2500, "gigabit": 1000}
            top, count = 0, 0
            for n, kind_ in re.findall(r"(\d+)x\s*(10G|5G|2\.5G|Gigabit)", v, re.I):
                top = max(top, speeds[kind_.lower()])
                count += int(n)
            return top, count
        x, y = pt(bv), pt(ov)
        return "ge" if x[0] >= y[0] and x[1] >= y[1] else "lt"
    if kind == "resolution":
        x, y = resolution(bv), resolution(ov)
        if y is None:
            return "not_stated"
        if x is None:
            return "best_missing"
        return "ge" if x >= y else "lt"
    if kind == "display":
        # three parts: size (no order), resolution and refresh rate (higher), the remaining words (no order)
        def parts(v):
            size = re.search(r"(\d+(?:\.\d+)?)\"", v)
            hz = re.search(r"(\d+)\s*Hz", v, re.I)
            touch = bool(re.search(r"\btouch\b", v, re.I))
            rest = re.sub(r"\d+(?:\.\d+)?\"|\d+\s*Hz|\btouch\b|\b(8K|4K|2\.8K|QHD|2K|FHD\+?|1080p|HD)\b", " ", v, flags=re.I)
            return (size.group(1) if size else None, resolution(v), int(hz.group(1)) if hz else None,
                    " ".join(rest.lower().split()), touch)
        x, y = parts(bv), parts(ov)
        res = []
        # a touchscreen is a function; another screen that has one counts against a best product without one
        if y[4] and not x[4]:
            res.append("best_missing")
        # a resolution or refresh rate written for one screen and not the other cannot be compared ("Retina HD"
        # against a screen described by size, panel and refresh rate)
        if x[1] is not None and y[1] is not None:
            res.append("ge" if x[1] >= y[1] else "lt")
        elif y[1] is not None:
            res.append("incomparable")
        if x[2] is not None and y[2] is not None:
            res.append("ge" if x[2] >= y[2] else "lt")
        elif y[2] is not None:
            res.append("incomparable")
        if x[0] != y[0] and x[0] is not None and y[0] is not None:
            res.append("incomparable")
        if x[3] != y[3]:
            res.append("incomparable")
        for r in ("lt", "best_missing", "incomparable"):
            if r in res:
                return r
        return "ge"
    raise SystemExit(f"unknown rule kind {kind}")


def load_rulings():
    rules = {}
    with open(RULINGS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rules[(r["table"], r["attribute"])] = (r["kind"], r["detail"])
    return rules


def rule_for(rules, table, attribute):
    short = table.replace("sr_", "")
    return rules.get((short, attribute)) or rules.get(("*", attribute))


def compare_table(prods: dict, best: str, table: str, rules) -> dict:
    rows = []
    b = prods[best]
    others = [L for L in sorted(prods) if L != best]
    price = {L: cc.parse_price(prods[L]["Price"]) for L in prods}
    cheapest = all(price[best] <= price[L] for L in others)

    def add(attr, kind, detail, bv, getter):
        for L in others:
            ov = getter(L)
            rows.append({"attribute": attr, "rule": kind, "other": L, "best_value": bv, "other_value": ov,
                         "outcome": outcome(kind, detail, bv, ov)})

    add("price", "number_lower", "", prods[best]["Price"].replace("$", "").replace(",", ""),
        lambda L: prods[L]["Price"].replace("$", "").replace(",", ""))
    add("sustainability", "rx_higher", r"(\d+(?:\.\d+)?)/", b["Sustainability rating"], lambda L: prods[L]["Sustainability rating"])
    add("review count", "rx_higher", r"(\d[\d,]*) reviews", b["Reviews"].replace(",", ""), lambda L: prods[L]["Reviews"].replace(",", ""))
    add("stars", "rx_higher", r"(\d+(?:\.\d+)?) stars", b["Reviews"], lambda L: prods[L]["Reviews"])
    specs = {L: cc.parse_specs(prods[L]["Specs"]) for L in prods}
    keys = sorted(set().union(*[set(s) for s in specs.values()]))
    for k in keys:
        rule = rule_for(rules, table, k)
        if rule is None:
            raise SystemExit(f"REFUSED: attribute {k} of {table} has no rule in {RULINGS.name}")
        add(k, rule[0], rule[1], specs[best].get(k), lambda L, k=k: specs[L].get(k))

    out = lambda o: sorted({r["attribute"] for r in rows if r["outcome"] == o})
    losses = [r for r in rows if r["outcome"] in ("lt", "best_missing") and r["attribute"] != "price"]
    incomparable = [r for r in rows if r["outcome"] == "incomparable"]
    strict = cheapest and not losses and not incomparable
    ordered = cheapest and not losses
    group = lambda dom: "1 dominant" if dom else ("3 best product not the cheapest" if not cheapest else "2 best only under the stated weights")
    return {
        "table": table, "best": best, "best_name": b["Name"], "best_price": price[best],
        "cheapest_other_price": min(price[L] for L in others), "best_is_cheapest_or_tied": cheapest,
        "group_strict": group(strict), "group_ordered_only": group(ordered),
        "attributes_where_best_loses": [f"{r['attribute']}: {r['best_value']} against {r['other_value']} (product {r['other']})" for r in losses],
        "attributes_with_an_order": sorted({r["attribute"] for r in rows if r["rule"] != "unordered"}),
        "attributes_where_best_is_better_than_some_product": sorted({
            r["attribute"] for r in rows if r["rule"] != "unordered" and r["outcome"] == "ge" and r["best_value"] != r["other_value"]}),
        "attributes_without_an_order_that_differ": out("incomparable"),
        "attributes_not_stated_by_another_product": out("not_stated"),
        "comparisons": rows,
    }


def main() -> int:
    rules = load_rulings()
    df, info = cc.load_rows(["model_key", "assortment_id", "chose_optimal", "optimal_product", "user_message"])
    tables_out = []
    for t, g in df[df.condition == cc.SHOWN].groupby("assortment_id"):
        prods = cc.parse_products(g["user_message"].iloc[0])
        best = g["optimal_product"].iloc[0]
        # every row of a table must show the same products and mark the same product as best
        sig = sorted((v["Specs"], v["Price"]) for v in prods.values())
        best_sig = (prods[best]["Specs"], prods[best]["Price"])
        for m, b in g[["user_message", "optimal_product"]].drop_duplicates().itertuples(index=False):
            p = cc.parse_products(m)
            if sorted((v["Specs"], v["Price"]) for v in p.values()) != sig or (p[b]["Specs"], p[b]["Price"]) != best_sig:
                raise SystemExit(f"REFUSED: {t} has rows with different products or a different best product")
        # the products are the same in every row of a table; the best product's letter follows the row's letter order
        tables_out.append(compare_table(prods, best, t, rules))

    df["non_optimal"] = 1.0 - df["chose_optimal"].astype(float)
    models, tables, arr = cc.cell_arrays(df, "non_optimal")

    def group_gap(names):
        idx = [tables.index(t) for t in names]
        if not idx:
            return None
        sub = {c: (arr[c][0][:, idx], arr[c][1][:, idx]) for c in arr}
        point = cc.pooled_gap(sub)
        boot = cc.twoway_bootstrap(sub, len(models), len(idx))
        s1, n1 = sub[cc.SHOWN]
        s0, n0 = sub[cc.HIDDEN]
        return {"tables": len(idx), "shown_pct": round(100 * s1.sum() / n1.sum(), 2), "hidden_pct": round(100 * s0.sum() / n0.sum(), 2),
                "gap_pp": round(100 * point, 2), "ci95_pp": cc.ci(boot, 100), "p_two_sided": cc.p_two_sided(boot), "draws": cc.DRAWS, "seed": cc.SEED}

    summary = {}
    for reading in ("group_strict", "group_ordered_only"):
        groups = {}
        for r in tables_out:
            groups.setdefault(r[reading], []).append(r["table"])
        summary[reading] = {gname: {"tables": sorted(ts), "gap": group_gap(sorted(ts))} for gname, ts in sorted(groups.items())}
    lean = [{k: v for k, v in r.items() if k != "comparisons"} for r in tables_out]
    res = {"rule_file": "study1b-64-models-on-34-tables/materials/attribute_rulings.csv", "groups": summary, "tables": lean,
           "best_is_cheapest_or_tied": sum(r["best_is_cheapest_or_tied"] for r in tables_out)}
    cc.write_result("strict_dominance", res, "study1b-64-models-on-34-tables/code/03_strict_dominance.py", info)
    detail = cc.RESULTS / "dominance_comparisons.csv"
    with open(detail, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "best", "attribute", "rule", "other", "best_value", "other_value", "outcome"])
        for r in tables_out:
            for c in r["comparisons"]:
                w.writerow([r["table"], r["best"], c["attribute"], c["rule"], c["other"], c["best_value"], c["other_value"], c["outcome"]])
    print("best product cheapest or tied:", res["best_is_cheapest_or_tied"], "of", len(tables_out))
    for reading, groups in summary.items():
        print(reading)
        for gname, g in groups.items():
            print(f"  {gname}: {len(g['tables'])} tables; gap {g['gap']}")
    for r in lean:
        print(f"{r['table']:28s} strict={r['group_strict'][:1]} ordered={r['group_ordered_only'][:1]} loses={r['attributes_where_best_loses']} unordered_differ={r['attributes_without_an_order_that_differ']} not_stated={r['attributes_not_stated_by_another_product']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
