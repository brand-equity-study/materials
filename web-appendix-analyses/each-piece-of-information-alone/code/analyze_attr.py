"""The estimates of the attribute build (attr1; study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 10), fixed before any of
its answers was read. pool_all.py computes them over every model that answered the build (--only attr).

For a model m, a table t, a condition a and a names version n, s(n, a) is the share of parsed answers that pick the
best product. The name gap of a condition is g(a) = s(hidden, a) - s(original, a).

- Every condition's name gap, pooled and for each model, and the three shares.
- Family 1, the same fact as a row and as a sentence: g(f-row) - g(f-sentence) for the five facts, Holm-corrected.
- Family 2, each condition against no information: g(a) - g(none) for the sixteen conditions, Holm-corrected.
- Family 3, the 2 by 2 name crossing (no information): with the best product's name invented (I) or familiar (F) and
  the other products' names familiar (f) or invented (i), the cells are original = (I, f), all-familiar = (F, f),
  all-invented = (I, i) and familiar-alone = (F, i). The effect of the best product's familiar name is the mean of
  s(F, f) - s(I, f) and s(F, i) - s(I, i); the effect of the other products' familiar names is the mean of
  s(I, f) - s(I, i) and s(F, f) - s(F, i); the interaction is the difference of the first two differences. Holm over
  the three. Each cell minus names hidden is reported beside them.

Pooling and intervals as in analyze.py: equal weight per table within a model, then per model; the two-way cluster
bootstrap over tables and models (2,000 draws, seed 20261120), one model's interval over tables only; every interval
with its two-sided P value from the same draws. A pooled interval needs three models and three tables; with fewer,
only the estimate is given. Every estimate is also given without the three tables whose invented name is a real
company.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze as AN  # noqa: E402  (load, draws_of, summary, holm; read only)
import attr_conditions as A  # noqa: E402  (the build's conditions)

DRAWS = 2000
INVENTED_REAL = {"sr_laptops_02_dom", "sr_laptops_03_dom", "sr_earbuds_02_dom"}
FACTS = list(A.ROW)
OTHER_CONDITIONS = [a for a in A.CONDITIONS if a != "none"]


def shares(rows):
    """{(model, table, names, arm): share of parsed answers that pick the best product}"""
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["letter"]:
            k = (r["model"], r["table"], r["names"], r["info"])
            c[k][0] += 1
            c[k][1] += r["is_best"]
    return {k: b / n for k, (n, b) in c.items() if n}


def per_mt(s, fn, tables=None):
    """{(model, table): fn(model, table)} where every share fn needs exists."""
    out = {}
    for m, t in sorted({(k[0], k[1]) for k in s}):   # sorted: the same order under every PYTHONHASHSEED
        if tables is not None and t not in tables:
            continue
        try:
            out[(m, t)] = fn(lambda n, a: s[(m, t, n, a)])
        except KeyError:
            continue
    return out


def pooled(d):
    ms = sorted({m for m, t in d})
    if not ms:
        return None
    return sum(sum(v for (mm, t), v in d.items() if mm == m) / sum(1 for (mm, t) in d if mm == m) for m in ms) / len(ms)


def summarize(d, fixed_models=False):
    e = pooled(d)
    if e is None:
        return None
    if not fixed_models and (len({m for m, t in d}) < 3 or len({t for m, t in d}) < 3):
        return {"estimate": round(e, 4)}
    if fixed_models and len({t for m, t in d}) < 3:
        return {"estimate": round(e, 4)}
    return AN.summary(e, AN.draws_of(d, DRAWS, fixed_models=fixed_models))


def family(named, fixed_models=False):
    out = {k: summarize(d, fixed_models) for k, d in named.items() if d}
    with_p = [k for k, v in out.items() if v and "p_two_sided" in v]
    for k, p in zip(with_p, AN.holm([out[k]["p_two_sided"] for k in with_p])):
        out[k]["p_holm"] = p
    return out


def report(s, tables=None, fixed_models=False):
    gap = lambda a: (lambda S_: S_("hidden", a) - S_("original", a))
    res = {"gap": {a: summarize(per_mt(s, gap(a), tables), fixed_models) for a in A.CONDITIONS},
           "shares": {a: {n: summarize(per_mt(s, (lambda n_, a_: lambda S_: S_(n_, a_))(n, a), tables), fixed_models)
                          for n in (A.NAMES_NONE if a == "none" else A.NAMES_ALL)} for a in A.CONDITIONS}}
    res["rows_against_sentences"] = family(
        {f: per_mt(s, (lambda f_: lambda S_: (S_("hidden", f"{f_}-row") - S_("original", f"{f_}-row"))
                       - (S_("hidden", f"{f_}-sentence") - S_("original", f"{f_}-sentence")))(f), tables) for f in FACTS},
        fixed_models)
    res["arm_against_none"] = family(
        {a: per_mt(s, (lambda a_: lambda S_: (S_("hidden", a_) - S_("original", a_))
                       - (S_("hidden", "none") - S_("original", "none")))(a), tables) for a in OTHER_CONDITIONS}, fixed_models)
    cell = {"If": "original", "Ff": "all-familiar", "Ii": "all-invented", "Fi": "familiar-alone"}
    v = lambda S_, c: S_(cell[c], "none")
    res["two_by_two"] = family({
        "best product's familiar name": per_mt(s, lambda S_: ((v(S_, "Ff") - v(S_, "If")) + (v(S_, "Fi") - v(S_, "Ii"))) / 2, tables),
        "other products' familiar names": per_mt(s, lambda S_: ((v(S_, "If") - v(S_, "Ii")) + (v(S_, "Ff") - v(S_, "Fi"))) / 2, tables),
        "interaction": per_mt(s, lambda S_: (v(S_, "Ff") - v(S_, "If")) - (v(S_, "Fi") - v(S_, "Ii")), tables),
    }, fixed_models)
    res["two_by_two_cells_minus_hidden"] = {
        c: summarize(per_mt(s, (lambda c_: lambda S_: S_(cell[c_], "none") - S_("hidden", "none"))(c), tables), fixed_models)
        for c in cell}
    return res

