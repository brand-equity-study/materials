"""The analysis of the price build (eq1; study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 6), fixed before any answer was
read.

    python study2b-how-much-a-familiar-brand-is-worth/code/analyze_eq.py --build eq1 --models claude-haiku-5-5,claude-sonnet-5-5,claude-opus-5-5,claude-fable-5-1 --out <folder>

Option A (primary). Among the answers that pick the invented product or the partner, the probability of the invented
product is a logit: in the price arm on x = -ln(1 - cut) (cut 0, 5, 15, 30, 50 per cent), in the rating arm on the
difference in stars (0, 0.1, 0.2, 0.4, 0.6; the parity cell is in both conditions). With a the intercept, b the slope on x
and c the slope on stars: the price equivalent exp(-a / b) - 1, the cut that offsets the name 1 - exp(a / b), and the
rating equivalent -a / c stars (with the brand's value -a and the price weight b). An equivalent is reported
only when the 95 per cent interval of its slope lies above zero; a draw whose slope is not above zero counts as an
infinite equivalent. Every fit adds 0.5 to the count of each of the two products at each rung, so that a rung where
every answer picks the same product still gives a finite fit (the plan's amendment 6, its implementation note).
The zero control passes when the 95 per cent interval of the names-hidden intercept includes 0; when it does not, the
equivalents use the names-shown intercept minus the names-hidden intercept. Beside the fit, with no model: the
invented product's share minus the partner's share on each rung and the rung, interpolated, at which it reaches zero.

Option B. The cut (or stars), interpolated between rungs, at which the best product's share with the invented name
reaches its share with the names hidden at parity; and the name gap on each rung minus the gap at parity, four price
and four rating contrasts, Holm-corrected as one family, with no direction stated.

Amendment 7 (after the first small run eqpilot1, before any answer of eq1): option A's price arm has rungs at 0, 1, 2, 3, 5, 10,
15, 30 and 50 per cent; option A's primary estimate is the crossing, per model and pooled, with the logit beside it
fitted on the rungs from 0 to 30 per cent; the zero control is the names-hidden parity cell, where the invented twin's
share of the answers that pick either twin should have a 95 per cent interval that includes one half. When it does
not, the crossing is computed after the names-hidden difference at parity is taken off every rung.

Pooling: one fit over every model's and table's answers (each model and table has the same number of trials); shares
weight every table equally within a model and every model equally. Intervals: the two-way cluster bootstrap of
analyze.py (tables and models resampled independently, 2,000 draws, seed 20261120); one model's interval resamples
tables only.
"""
import argparse
import json
import math
import os
import random
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))  # analyze.py and parse_answer.py
import analyze as AN  # noqa: E402  (load, summary, holm; read only)

SEED = 20261120
DRAWS = 2000
CUTS = (0, 5, 15, 30, 50)                    # option B
CUTS_A = (0, 1, 2, 3, 5, 10, 15, 30, 50)     # option A (amendment 7; the first small run, eqpilot1, has the rungs of CUTS only)
LOGIT_MAX_CUT = 30                           # amendment 7: option A's logit is fitted on the rungs from 0 to 30 per cent
STEPS = (0.0, 0.1, 0.2, 0.4, 0.6)            # stars above 4.3, the parity cell first
PRICE_RUNGS = [f"cut{c}" for c in CUTS]
PRICE_RUNGS_A = [f"cut{c}" for c in CUTS_A]
STAR_RUNGS = ["cut0"] + [f"stars{s}" for s in (4.4, 4.5, 4.7, 4.9)]
X_PRICE = {f"cut{c}": -math.log(1 - c / 100) for c in CUTS_A}
X_STARS = dict(zip(STAR_RUNGS, STEPS))
INVENTED_REAL = {"sr_laptops_02_dom", "sr_laptops_03_dom", "sr_earbuds_02_dom"}
THIN = {"sr_monitors_01_dom", "sr_electric_toothbrushes_01_dom", "sr_robot_vacuums_01_dom", "sr_laptops_02_dom",
        "sr_coffee_makers_03_dom"}


# ---------------------------------------------------------------- the fit

def fit_logit(points, add=0.5, iters=60):
    """(a, b) of the logit P = 1 / (1 + exp(-(a + b x))) from points [(x, k, n)]: k picks of the invented product out
    of n picks of either product. Newton's method with step halving; add is the count added to each product."""
    pts = [(x, k + add, n + 2 * add) for x, k, n in points if n + 2 * add > 0]
    if len({x for x, _, _ in pts}) < 2:
        return None
    a = b = 0.0

    def ll(a, b):
        s = 0.0
        for x, k, n in pts:
            z = a + b * x
            s += k * z - n * (max(z, 0) + math.log1p(math.exp(-abs(z))))
        return s

    cur = ll(a, b)
    for _ in range(iters):
        ga = gb = haa = hab = hbb = 0.0
        for x, k, n in pts:
            p = 1 / (1 + math.exp(-(a + b * x)))
            ga += k - n * p
            gb += (k - n * p) * x
            w = n * p * (1 - p)
            haa += w
            hab += w * x
            hbb += w * x * x
        det = haa * hbb - hab * hab
        if det <= 1e-12:
            break
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        step = 1.0
        while step > 1e-6:
            na, nb = a + step * da, b + step * db
            new = ll(na, nb)
            if new >= cur - 1e-12:
                break
            step /= 2
        a, b, cur = na, nb, new
        if abs(da) + abs(db) < 1e-10:
            break
    return a, b


def price_equivalent(a, b):
    """(premium, cut) in per cent; infinite when the slope is not above zero."""
    if b is None or b <= 0:
        return math.inf, math.inf
    r = -a / b
    if r > 700:                               # a slope this flat offsets the name at no finite price
        return math.inf, 100.0
    if r < -700:
        return -100.0, -math.inf
    return 100 * (math.exp(r) - 1), 100 * (1 - math.exp(-r))


def star_equivalent(a, c):
    return math.inf if c is None or c <= 0 else -a / c


# ---------------------------------------------------------------- counts

def pair_counts(items, rows):
    """{(model, table, names, rung): [invented, partner, neither, parsed]} for option A, rung without the option."""
    c = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        it = items[r["id"]]
        if it["option"] != "A" or not r["letter"]:
            continue
        k = c[(r["model"], it["table"], it["names"], it["rung"][2:])]
        k[3] += 1
        if r["letter"] == it["invented"]:
            k[0] += 1
        elif r["letter"] == it["partner"]:
            k[1] += 1
        else:
            k[2] += 1
    return c


def best_counts(items, rows):
    """{(model, table, names, rung): [best, parsed]} for option B."""
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        it = items[r["id"]]
        if it["option"] != "B" or not r["letter"]:
            continue
        k = c[(r["model"], it["table"], it["names"], it["rung"][2:])]
        k[1] += 1
        k[0] += int(r["letter"] == it["best"])
    return c


# ---------------------------------------------------------------- resampling

def draw_sets(models, tables, draws=DRAWS, seed=SEED, fixed_models=False):
    """The resampled (models, tables) of each draw, in analyze.draws_of's order."""
    rng = random.Random(seed)
    out = []
    for _ in range(draws):
        ms = list(models) if fixed_models else [rng.choice(models) for _ in models]
        ts = [rng.choice(tables) for _ in tables]
        out.append((ms, ts))
    return out


def points_of(pc, ms, ts, names, xs, keep=None):
    """[(x, k, n)] summed over the (model, table) pairs of the draw, with multiplicity."""
    acc = {r: [0, 0] for r in xs}
    for m in ms:
        for t in ts:
            for r in xs:
                if keep is not None and (t, r) not in keep:
                    continue
                v = pc.get((m, t, names, r))
                if v:
                    acc[r][0] += v[0]
                    acc[r][1] += v[0] + v[1]
    return [(xs[r], k, n) for r, (k, n) in acc.items() if n]


def q(vals, p):
    s = sorted(vals)
    return s[min(len(s) - 1, max(0, int(round(p * (len(s) - 1)))))]


def interval(vals):
    return [round(q(vals, 0.025), 4), round(q(vals, 0.975), 4)]


def rnd(x):
    return None if x is None else ("infinite" if math.isinf(x) else round(x, 4))


# ---------------------------------------------------------------- option A

def parity_control(pc, models, tables, keep=None, fixed_models=False):
    """Amendment 7: with names hidden at parity, the invented twin's share of the answers that pick either twin (each
    table weighted equally within a model, then each model), with its 95 per cent interval; it passes when the interval
    includes one half. Also the invented minus partner share of all parsed answers there, used to net the crossing."""
    per, diff = {}, {}
    for m in models:
        for t in tables:
            if keep is not None and (t, "cut0") not in keep:
                continue
            v = pc.get((m, t, "hidden", "cut0"))
            if v and v[0] + v[1]:
                per[(m, t)] = v[0] / (v[0] + v[1])
            if v and v[3]:
                diff[(m, t)] = (v[0] - v[1]) / v[3]
    if not per:
        return None
    sets = draw_sets(models, tables, fixed_models=fixed_models)
    dr = [x for x in (pooled_mean(per, ms, ts) for ms, ts in sets) if x is not None]
    est = pooled_mean(per, models, tables)
    ci = interval(dr)
    return {"invented_share_of_pair_picks": round(est, 4), "ci95": ci, "pass": ci[0] <= 0.5 <= ci[1],
            "invented_minus_partner": round(pooled_mean(diff, models, tables), 4)}


def option_a(pc, models, tables, keep=None, fixed_models=False):
    sets = draw_sets(models, tables, fixed_models=fixed_models)
    control = parity_control(pc, models, tables, keep, fixed_models)
    out = {"zero_control": control}
    price_xs = {r: X_PRICE[r] for r in PRICE_RUNGS_A if int(r[3:]) <= LOGIT_MAX_CUT}
    for arm, xs, equiv in (("price", price_xs, "price"), ("rating", {r: X_STARS[r] for r in STAR_RUNGS}, "stars")):
        fits = {}
        for names in ("original", "hidden"):
            pts = points_of(pc, models, tables, names, xs, keep)
            est = fit_logit(pts)
            dr = [fit_logit(points_of(pc, ms, ts, names, xs, keep)) for ms, ts in sets]
            fits[names] = (est, dr, pts)
        (eo, do, po), (eh, dh, ph) = fits["original"], fits["hidden"]
        if eo is None or eh is None:
            out[arm] = {"fit": "not enough rungs"}
            continue
        a_h = [d[0] for d in dh if d]
        control_pass = bool(control and control["pass"])
        net = lambda o, h: o[0] if control_pass else o[0] - h[0]
        slope = [d[1] for d in do if d]
        identified = q(slope, 0.025) > 0
        if equiv == "price":
            e = price_equivalent(net(eo, eh), eo[1])
            ed = [price_equivalent(net(o, h), o[1]) for o, h in zip(do, dh) if o and h]
            res = {"premium_pct": rnd(e[0]), "premium_ci95": interval([x[0] for x in ed]),
                   "cut_pct": rnd(e[1]), "cut_ci95": interval([x[1] for x in ed])}
        else:
            e = star_equivalent(net(eo, eh), eo[1])
            ed = [star_equivalent(net(o, h), o[1]) for o, h in zip(do, dh) if o and h]
            res = {"stars": rnd(e), "stars_ci95": interval(ed)}
        out[arm] = {"identified": identified, "zero_control_pass": control_pass,
                    "intercept_shown": rnd(eo[0]), "intercept_shown_ci95": interval([d[0] for d in do if d]),
                    "slope_shown": rnd(eo[1]), "slope_shown_ci95": interval(slope),
                    "intercept_hidden": rnd(eh[0]), "intercept_hidden_ci95": interval(a_h),
                    "slope_hidden": rnd(eh[1]),
                    "equivalent": res if identified else "not identified", "equivalent_if_read": res,
                    "points_shown": [[round(x, 4), k, n] for x, k, n in po],
                    "points_hidden": [[round(x, 4), k, n] for x, k, n in ph]}
    return out


def share_diff(pc, models, tables, names, rung, keep=None):
    """Invented share minus partner share among parsed answers, per (model, table)."""
    per = {}
    for m in models:
        for t in tables:
            if keep is not None and (t, rung) not in keep:
                continue
            v = pc.get((m, t, names, rung))
            if v and v[3]:
                per[(m, t)] = (v[0] - v[1]) / v[3]
    return per


def pooled_mean(per, ms, ts):
    vals = []
    for m in ms:
        x = [per[(m, t)] for t in ts if (m, t) in per]
        if x:
            vals.append(sum(x) / len(x))
    return sum(vals) / len(vals) if vals else None


def crossing(curve, steps):
    """The step, interpolated, at which the curve first reaches 0 (curve[0] >= 0 gives the first step); inf if never."""
    if curve[0] is None:
        return None
    if curve[0] >= 0:
        return steps[0]
    for i in range(1, len(curve)):
        if curve[i] is None:
            return None
        if curve[i] >= 0:
            lo, hi = curve[i - 1], curve[i]
            return steps[i - 1] + (steps[i] - steps[i - 1]) * (-lo) / (hi - lo)
    return math.inf


def option_a_free(pc, models, tables, keep=None, fixed_models=False):
    """Amendment 7's primary estimate: the cut (or stars), interpolated, at which the invented product's share equals
    the partner's. When the parity control fails, the names-hidden difference at parity is taken off every rung first.
    Rungs with no answers (the first small run, eqpilot1, has no 1, 2, 3 or 10 per cent rung) are skipped."""
    sets = draw_sets(models, tables, fixed_models=fixed_models)
    control = parity_control(pc, models, tables, keep, fixed_models)
    offset = 0.0 if control is None or control["pass"] else control["invented_minus_partner"]
    out = {"netted_by_the_parity_control": offset}
    for arm, rungs, steps in (("price", PRICE_RUNGS_A, list(CUTS_A)), ("rating", STAR_RUNGS, list(STEPS))):
        rows = {}
        here = [i for i, r in enumerate(rungs) if any(k[3] == r for k in pc)]
        rungs, steps = [rungs[i] for i in here], [steps[i] for i in here]
        # the crossing is read on the rungs from 0 to 30 per cent only (amendment 7); the 50 per cent rung is reported
        upto = [i for i, s in enumerate(steps) if arm == "rating" or s <= LOGIT_MAX_CUT]
        for names in ("original", "hidden"):
            pers = [{k: v - offset for k, v in share_diff(pc, models, tables, names, r, keep).items()} for r in rungs]
            est = [pooled_mean(p, models, tables) for p in pers]
            dr = [[pooled_mean(p, ms, ts) for p in pers] for ms, ts in sets]
            cut = lambda curve: crossing([curve[i] for i in upto], [steps[i] for i in upto])
            c = cut(est)
            rows[names] = {"by_rung": {r: (None if e is None else round(e, 4)) for r, e in zip(rungs, est)},
                           "by_rung_ci95": {r: interval([d[i] for d in dr if d[i] is not None]) for i, r in enumerate(rungs)
                                            if any(d[i] is not None for d in dr)},
                           "crossing": label(c, arm), "crossing_value": rnd(c), "bounded": c is not None and math.isinf(c),
                           "crossing_ci95": [label(x, arm) for x in interval([x for x in (cut(d) for d in dr) if x is not None])]}
        out[arm] = rows
    return out


def label(c, arm):
    """Amendment 7: a crossing never reached on the rungs read is a bound ('more than 30 per cent', 'more than 0.6
    stars'), never extrapolated; a rating crossing between parity and the first step is 'less than 0.1 star'."""
    if c is None:
        return None
    if math.isinf(c):
        return f"more than {LOGIT_MAX_CUT} per cent" if arm == "price" else "more than 0.6 stars"
    if arm == "rating" and 0 < c < 0.1:
        return "less than 0.1 star"
    return round(c, 4)


def neither(pc):
    by = defaultdict(lambda: [0, 0])
    for (m, t, n, r), v in pc.items():
        by[(n, r)][0] += v[2]
        by[(n, r)][1] += v[3]
    return {f"{n}-{r}": round(a / b, 4) for (n, r), (a, b) in sorted(by.items()) if b}


# ---------------------------------------------------------------- option B

def option_b(bc, models, tables, keep=None, fixed_models=False):
    sets = draw_sets(models, tables, fixed_models=fixed_models)
    per = {}
    for names in ("original", "hidden"):
        for r in PRICE_RUNGS + STAR_RUNGS[1:]:
            d = {}
            for m in models:
                for t in tables:
                    if keep is not None and (t, r) not in keep:
                        continue
                    v = bc.get((m, t, names, r))
                    if v and v[1]:
                        d[(m, t)] = v[0] / v[1]
            per[(names, r)] = d
    gap = {r: {k: per[("hidden", r)][k] - per[("original", r)][k] for k in per[("hidden", r)] if k in per[("original", r)]}
           for r in PRICE_RUNGS + STAR_RUNGS[1:]}

    def equalization(ms, ts):
        target = pooled_mean(per[("hidden", "cut0")], ms, ts)
        res = {}
        for arm, rungs, steps in (("price", PRICE_RUNGS, list(CUTS)), ("rating", STAR_RUNGS, list(STEPS))):
            curve = [pooled_mean(per[("original", r)], ms, ts) for r in rungs]
            res[arm] = None if target is None or None in curve else crossing([c - target for c in curve], steps)
        return res

    est = equalization(models, tables)
    dr = [equalization(ms, ts) for ms, ts in sets]
    out = {"equalization": {arm: {"estimate": rnd(est[arm]),
                                  "ci95": interval([d[arm] for d in dr if d[arm] is not None])} for arm in est},
           "share_by_rung": {f"{n}-{r}": rnd(pooled_mean(v, models, tables)) for (n, r), v in per.items()}}
    contrasts, ps = {}, []
    for r in PRICE_RUNGS[1:] + STAR_RUNGS[1:]:
        diff = {k: gap[r][k] - gap["cut0"][k] for k in gap[r] if k in gap["cut0"]}
        e = pooled_mean(diff, models, tables)
        vals = sorted(x for x in (pooled_mean(diff, ms, ts) for ms, ts in sets) if x is not None)
        if e is None or not vals:
            continue
        contrasts[r] = AN.summary(e, vals)
        ps.append(contrasts[r]["p_two_sided"])
    for r, p in zip(contrasts, AN.holm(ps)):
        contrasts[r]["p_holm"] = p
    out["gap_by_rung"] = {r: rnd(pooled_mean(g, models, tables)) for r, g in gap.items()}
    out["contrasts_to_test"] = contrasts
    return out


# ---------------------------------------------------------------- report

def report(items, rows, models, tables, keep=None, fixed_models=False):
    return report_counts(pair_counts(items, rows), best_counts(items, rows), models, tables, keep, fixed_models)


def parity_tests(pc, models, tables, keep=None, fixed_models=False):
    """Tests of the two comparisons at the same price that amendments 6 and 7 report as estimates (the note of 21
    November 2026 at about 6:40 PM Central, asked for by the writer for the reporting standard): each pooled with equal
    weight per table within a model and per model, with the two-way bootstrap's interval and two-sided P (2,000 draws,
    seed 20261120; one model's interval over tables only).
    - names hidden against names shown: the invented twin's share of the answers that pick either twin, with names
      hidden minus with names shown;
    - the invented against the familiar twin with names shown: the invented twin's share minus the familiar twin's
      share of all parsed answers (the crossing curve at a cut of 0), which is below 0 when the name costs the
      invented product at the same price, so that its tie cut is above 0;
    - the same with names hidden (the zero control as a test)."""
    pair = lambda v: v[0] / (v[0] + v[1]) if v[0] + v[1] else None
    diff = lambda v: (v[0] - v[1]) / v[3] if v[3] else None
    d = {"names hidden minus names shown, invented twin's share of pair picks": {},
         "invented minus familiar twin, names shown": {}, "invented minus familiar twin, names hidden": {}}
    for m in models:
        for t in tables:
            if keep is not None and (t, "cut0") not in keep:
                continue
            h, o = pc.get((m, t, "hidden", "cut0")), pc.get((m, t, "original", "cut0"))
            if h and o and pair(h) is not None and pair(o) is not None:
                d["names hidden minus names shown, invented twin's share of pair picks"][(m, t)] = pair(h) - pair(o)
            if o and diff(o) is not None:
                d["invented minus familiar twin, names shown"][(m, t)] = diff(o)
            if h and diff(h) is not None:
                d["invented minus familiar twin, names hidden"][(m, t)] = diff(h)
    out = {}
    for k, per in d.items():
        e = pooled_mean(per, models, tables) if per else None
        if e is None:
            continue
        ms, ts = {m for m, t in per}, {t for m, t in per}
        if len(ts) < 3 or (not fixed_models and len(ms) < 3):
            out[k] = {"estimate": round(e, 4)}
            continue
        vals = sorted(x for x in (pooled_mean(per, a, b) for a, b in draw_sets(models, tables, fixed_models=fixed_models))
                      if x is not None)
        out[k] = {**AN.summary(e, vals), "draws": len(vals)}
    return out


def report_counts(pc, bc, models, tables, keep=None, fixed_models=False):
    """The report from counts alone: pc for option A, {(model, table, names, rung): [invented, partner, neither,
    parsed]}, and bc for option B, {(model, table, names, rung): [best, parsed]}. The open panel's counts from
    the computing cluster (open_b9.py) come in this form."""
    return {"tables": len(tables), "models": models,
            "option_a": option_a(pc, models, tables, keep, fixed_models),
            "option_a_without_a_model": option_a_free(pc, models, tables, keep, fixed_models),
            "option_a_neither_share": neither({k: v for k, v in pc.items() if k[0] in models and k[1] in tables}),
            "option_a_parity_tests": parity_tests(pc, models, tables, keep, fixed_models),
            "option_b": option_b(bc, models, tables, keep, fixed_models)}


def below_range_keep(items):
    """The (table, rung) cells whose invented product is not cheaper than the shopper's stated range."""
    return {(it["table"], it["rung"][2:]) for it in items if it["outside_budget"] != "below"}


def assemble(make, have, tables, below):
    """Every part of the result that the plan names, from make(models, tables, keep, fixed_models, kind), which returns
    a report (from answers or from counts): pooled, each model, the partner's kind, the three subsets, the bounds."""
    res = {"pooled": make(have, tables)}
    res["by_model"] = {m: make([m], tables, fixed_models=True) for m in have}
    res["by_partner_kind"] = {kind: make(have, tables, kind=kind)["option_a"] for kind in ("familiar-high", "familiar-medium")}
    for label, drop in (("without_invented_real", INVENTED_REAL), ("without_thin", THIN)):
        ts = [t for t in tables if t not in drop]
        if len(ts) >= 3:
            res[label] = make(have, ts)
    res["without_below_range"] = make(have, tables, keep=below)
    res["primary"] = ("option A's crossing (amendment 7): pooled / by_model -> option_a_without_a_model -> "
                      "price|rating -> original -> crossing, in per cent of price and in stars above 4.3; the pooled "
                      "crossing is read on the pooled curve")
    res["models_bounded"] = {arm: sorted(m for m, r in res["by_model"].items()
                                         if r["option_a_without_a_model"][arm]["original"]["bounded"])
                             for arm in ("price", "rating")}
    res["bootstrap"] = {"draws": DRAWS, "seed": SEED, "resampled": "whole tables, and models for a pooled estimate; "
                        "never single answers"}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    models = a.models.split(",")
    sets = {"split1": "each-piece-alone", "eq1": "price"}
    items, rows, runs = AN.load(sets.get(a.build, a.build), models, studies=("study2b-how-much-a-familiar-brand-is-worth",))
    tables = sorted({it["table"] for it in items.values()})
    have = sorted({r["model"] for r in rows})
    unparsed = defaultdict(lambda: [0, 0])
    for r in rows:
        unparsed[r["model"]][1] += 1
        unparsed[r["model"]][0] += int(not r["letter"])
    res = {"build": a.build, "plan": "study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, amendment 6", "answers": len(rows),
           "unparsed": {m: f"{u} of {n}" for m, (u, n) in sorted(unparsed.items())}}

    def make(models, tables, keep=None, fixed_models=False, kind=None):
        sub = rows if kind is None else [r for r in rows if items[r["id"]]["option"] == "B"
                                         or items[r["id"]]["partner_kind"] == kind]
        return report(items, sub, models, tables, keep, fixed_models)

    res.update(assemble(make, have, tables, below_range_keep(items.values())))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print("models bounded (never reach the partner's share on the rungs read):", res["models_bounded"])
    p = res["pooled"]
    print("A zero control at parity:", p["option_a"]["zero_control"])
    print("A PRIMARY, the crossing:", json.dumps({arm: {"crossing": d["original"]["crossing"], "ci95": d["original"]["crossing_ci95"]}
                                               for arm, d in p["option_a_without_a_model"].items() if arm in ("price", "rating")}))
    for m, r in res["by_model"].items():
        f = r["option_a_without_a_model"]
        print(f"   {m}: price {f['price']['original']['crossing']} {f['price']['original']['crossing_ci95']}, "
              f"rating {f['rating']['original']['crossing']} {f['rating']['original']['crossing_ci95']}")
    for arm in ("price", "rating"):
        r = p["option_a"].get(arm, {})
        print(f"A {arm}: identified {r.get('identified')}, zero control {r.get('zero_control_pass')}, "
              f"intercept {r.get('intercept_shown')} {r.get('intercept_shown_ci95')}, slope {r.get('slope_shown')} "
              f"{r.get('slope_shown_ci95')}, hidden intercept {r.get('intercept_hidden')} {r.get('intercept_hidden_ci95')}; "
              f"equivalent {r.get('equivalent_if_read')}")
    print("B equalization:", json.dumps(p["option_b"]["equalization"]))
    print("B contrasts:", json.dumps({r: [v["estimate"], v["p_holm"]] for r, v in p["option_b"]["contrasts_to_test"].items()}))
    print(f"wrote {os.path.join(a.out, 'numbers.json')}")


if __name__ == "__main__":
    main()
