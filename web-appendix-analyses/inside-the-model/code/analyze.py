"""The statistics of step B6 (PLAN.md, 'The statistics'), from the files that a job returns.

    python jmr-2026/mechanism/analyze.py --pairs <pairs.jsonl> --run gemma31b=<back folder> [--run gemma4-26b=<folder>]
                                         --out <folder>

Reads each model's proj.npz, B.json, P.jsonl.gz, C.jsonl.gz and CALIBRATION.json; writes <out>/numbers.json, from
which jmr-2026/results/mechanism/RESULTS.md is written. The unit is the table: every mean gives each table equal weight; intervals come from a cluster
bootstrap over tables (2,000 draws, seed 20261120); question 1's p-values from flipping the signs of a table's pairs
together (10,000 flips, seed 20261120), Holm over the spec and reliability tests.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
from collections import defaultdict

import numpy as np

SEED = 20261120
DRAWS = 2000
FLIPS = 10000
RANDOM = ("iso0", "iso1", "cov0", "cov1")
MIN_PROBABILITY_EFFECT = 0.01   # PLAN.md change of about midnight: "recommend it more" needs at least 1 point


def jl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf8") as f:
        return [json.loads(l) for l in f if l.strip()]


# ---------------------------------------------------------------- the table-level machinery

def by_table(values, tables):
    """{table: mean of its values}, ignoring missing values."""
    acc = defaultdict(list)
    for v, t in zip(values, tables):
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            acc[t].append(v)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def boot(per_table, draws=DRAWS, seed=SEED, fn=None):
    """Point estimate and 95 per cent interval of the equal-weight mean over tables (or fn of resampled tables)."""
    ts = sorted(per_table)
    if not ts:
        return None, [None, None]
    rng = np.random.default_rng(seed)
    if fn is None:
        x = np.array([per_table[t] for t in ts])
        est = float(x.mean())
        idx = rng.integers(0, len(ts), (draws, len(ts)))
        bs = x[idx].mean(1)
    else:
        est = fn(ts)
        bs = np.array([fn([ts[i] for i in rng.integers(0, len(ts), len(ts))]) for _ in range(draws)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, [float(lo), float(hi)]


def sign_flip_p(per_table, flips=FLIPS, seed=SEED):
    """One-sided p-value that the equal-weight mean over tables is above zero, flipping each table's sign."""
    x = np.array([per_table[t] for t in sorted(per_table)])
    obs = x.mean()
    rng = np.random.default_rng(seed)
    s = rng.choice([-1.0, 1.0], size=(flips, len(x)))
    null = (s * x).mean(1)
    return float((1 + (null >= obs).sum()) / (1 + flips))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def r(x, k=3):
    if x is None:
        return None
    if isinstance(x, list):
        return [r(v, k) for v in x]
    return round(float(x), k)


# ---------------------------------------------------------------- question 1

def question1(pairs, proj, layers, spans, dirs, layer):
    j, si = list(layers).index(layer), list(spans).index("close")
    di = {d: k for k, d in enumerate(dirs)}
    P = proj.astype(np.float64)
    name0 = [k for k, p in enumerate(pairs) if p["contrast"] == "name" and p["info"] == 0]
    own = {"spec0": [k for k, p in enumerate(pairs) if p["contrast"] == "spec" and p["info"] == 0],
           "rel": [k for k, p in enumerate(pairs) if p["contrast"] == "reliability"]}
    out, ps = {}, []
    for D in ("spec0", "rel"):
        nt = by_table([P[k, j, si, di[D]] for k in name0], [pairs[k]["table"] for k in name0])
        ot = by_table([P[k, j, si, di[D]] for k in own[D]], [pairs[k]["table"] for k in own[D]])
        est, ci = boot(nt)
        p = sign_flip_p(nt)
        ps.append(p)
        ratio = boot(nt, fn=lambda ts: float(np.mean([nt[t] for t in ts if t in nt]) / np.mean([ot[t] for t in ts if t in ot])))
        pos = boot(by_table([float(P[k, j, si, di[D]] > 0) for k in name0], [pairs[k]["table"] for k in name0]))
        acc = boot(by_table([float(P[k, j, si, di[D]] > 0) for k in own[D]], [pairs[k]["table"] for k in own[D]]))
        perp = boot(by_table([P[k, j, si, di[D + "_perp_price"]] for k in name0], [pairs[k]["table"] for k in name0]))
        out[D] = {"mean_projection": r(est, 4), "ci": r(ci, 4), "p_one_sided": p, "share_of_distance": r(ratio[0]),
                  "share_of_distance_ci": r(ratio[1]), "share_positive": r(pos[0]), "share_positive_ci": r(pos[1]),
                  "probe_held_out_accuracy": r(acc[0]), "probe_held_out_accuracy_ci": r(acc[1]),
                  "probe_reads_listed_quality": acc[0] >= 0.75,
                  "without_price_component": r(perp[0], 4), "without_price_component_ci": r(perp[1], 4),
                  "quality_wording_allowed": perp[1][0] is not None and perp[1][0] > 0}
    for D, padj in zip(("spec0", "rel"), holm(ps)):
        out[D]["p_holm"] = padj
        out[D]["supported"] = bool(padj < 0.05 and out[D]["probe_reads_listed_quality"])
    # described: every stored layer, the close span, for the curves
    curve = {}
    for jj, li in enumerate(layers):
        curve[int(li)] = {D: r(boot(by_table([P[k, jj, si, di[D]] for k in name0], [pairs[k]["table"] for k in name0]))[0], 4)
                          for D in ("spec0", "rel", "price0")}
    out["by_layer_close_span"] = curve
    return out


# ---------------------------------------------------------------- the patch

def patch_summary(P):
    """Each patched row against the unpatched original in its own unit (PLAN.md change of about midnight)."""
    base = {x["uid"]: x["lo"] for x in P if x["role"] == "base_b"}
    out = {}
    for span in ("postname", "close"):
        for info in (0, 1):
            rows = [x for x in P if x["role"] == "copy" and x["key"][1] == span and x["info"] == info
                    and x["lo"] is not None and base.get(x["uid"]) is not None]
            for li in sorted({x["layer"] for x in rows}):
                sub = [x for x in rows if x["layer"] == li]
                est, ci = boot(by_table([x["lo"] - base[x["uid"]] for x in sub], [x["table"] for x in sub]))
                out.setdefault(f"{span}|info{info}", {})[li] = {"effect": r(est), "ci": r(ci)}
    pn = out.get("postname|info0", {})
    out["passes_through_postname"] = any(v["ci"][0] is not None and v["ci"][0] > 0 for v in pn.values())
    return out


def noise_floor(rows, dup_role, base_role):
    """The two copies of one baseline in one unit: how far apart their outcomes are."""
    base = {x["uid"]: x for x in rows if x["role"] == base_role}
    d_lo, d_pb = [], []
    for x in rows:
        b = base.get(x["uid"]) if x["role"] == dup_role else None
        if b is not None and x["lo"] is not None and b["lo"] is not None:
            d_lo.append(abs(x["lo"] - b["lo"]))
            d_pb.append(abs(x["pb"] - b["pb"]))
    if not d_lo:
        return None
    return {"units": len(d_lo), "log_odds_mean_abs": r(np.mean(d_lo), 4), "log_odds_max_abs": r(np.max(d_lo), 4),
            "probability_mean_abs": r(np.mean(d_pb), 5), "probability_max_abs": r(np.max(d_pb), 5)}


# ---------------------------------------------------------------- questions 2 and 3

def pushes(C, layer, info, field="lo"):
    """{(target, dir, alpha): {table: mean change of field from the zero push in the same unit}}, and the share of
    pushes with no letter. field: lo (log-odds, capped as the model caps), lo_u (uncapped) or pb (probability)."""
    rows = [x for x in C if x["layer"] == layer and x["info"] == info]
    base = {x["uid"]: x for x in rows if x["role"] == "base"}
    acc, missing, n = defaultdict(lambda: defaultdict(list)), defaultdict(int), defaultdict(int)
    for x in rows:
        if x["role"] != "push":
            continue
        key = (x["target"], x["dir"], x["alpha"])
        n[key] += 1
        b = base.get(x["uid"])
        if x[field] is None or b is None or b[field] is None:
            missing[key] += 1
            continue
        acc[key][x["table"]].append(x[field] - b[field])
    return ({k: {t: float(np.mean(v)) for t, v in d.items()} for k, d in acc.items()},
            {k: missing[k] / n[k] for k in n})


def sym(D, t, d, size=1.0):
    a, b = D.get((t, d, size), {}), D.get((t, d, -size), {})
    return {tb: (a[tb] - b[tb]) / 2 for tb in a if tb in b}


def excludes_zero(ci, sign):
    return ci[0] is not None and ((ci[0] > 0) if sign > 0 else (ci[1] < 0))


def question2(C, layer):
    D, miss = pushes(C, layer, 0)
    Dp, _ = pushes(C, layer, 0, "pb")
    out = {"missing_share_max": r(max(miss.values()) if miss else None, 4)}
    crit, prob_ok = {}, {}
    for t, sign in (("best", 1), ("familiar", -1)):
        # PLAN.md change of about midnight: the words "recommend it more" also need the probability effect
        sp = {str(s): boot(sym(Dp, t, "name", s)) for s in (1.0, 2.0, 4.0)}
        prob_ok[t] = {s: excludes_zero(v[1], sign) and v[0] is not None and abs(v[0]) >= MIN_PROBABILITY_EFFECT
                      for s, v in sp.items()}
        out.setdefault("probability", {})[t] = {s: {"symmetric": r(v[0], 4), "ci": r(v[1], 4),
                                                    "excludes_zero_as_predicted": prob_ok[t][s]} for s, v in sp.items()}
        up, down = boot(D.get((t, "name", 1.0), {}))[0], boot(D.get((t, "name", -1.0), {}))[0]
        S = sym(D, t, "name")
        s_est, s_ci = boot(S)
        rand = [sym(D, t, k) for k in RANDOM]
        diff = {tb: S[tb] - np.mean([rk[tb] for rk in rand if tb in rk]) for tb in S if all(tb in rk for rk in rand)}
        d_est, d_ci = boot(diff)
        signs_ok = up is not None and down is not None and (up * sign > 0) and (down * sign < 0)
        s_ok = s_ci[0] is not None and ((s_ci[0] > 0) if sign > 0 else (s_ci[1] < 0))
        d_ok = d_ci[0] is not None and ((d_ci[0] > 0) if sign > 0 else (d_ci[1] < 0))
        same_way = up is not None and down is not None and up * down > 0
        out[t] = {"change_plus1": r(up), "change_minus1": r(down), "symmetric": r(s_est), "symmetric_ci": r(s_ci),
                  "random_symmetric": [r(boot(x)[0]) for x in rand], "name_minus_random_mean": r(d_est),
                  "name_minus_random_mean_ci": r(d_ci), "signs_as_predicted": bool(signs_ok),
                  "both_signs_move_the_same_way": bool(same_way),
                  "curve_log_odds": {str(a): r(boot(D.get((t, "name", a), {}))[0]) for a in (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0)},
                  "curve_probability": {str(a): r(boot(Dp.get((t, "name", a), {}))[0], 4) for a in (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0)},
                  "random_curves_log_odds": {k: {str(a): r(boot(D.get((t, k, a), {}))[0]) for a in (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0)} for k in RANDOM}}
        crit[t] = signs_ok and s_ok and d_ok
    out["supported"] = bool(crit["best"] and crit["familiar"])
    out["earlier_pattern_seen"] = bool(out["best"]["both_signs_move_the_same_way"] or out["familiar"]["both_signs_move_the_same_way"])
    out["recommend_wording_at_size_1"] = bool(prob_ok["best"]["1.0"] and prob_ok["familiar"]["1.0"])
    out["probability_sizes_that_hold"] = [s for s in ("1.0", "2.0", "4.0") if prob_ok["best"][s] and prob_ok["familiar"][s]]
    return out


def question3(C, layer):
    out = {}
    for field in ("lo", "lo_u"):
        D0, _ = pushes(C, layer, 0, field)
        D1, _ = pushes(C, layer, 1, field)
        res = {}
        for t in ("best", "familiar"):
            s0, s1 = sym(D0, t, "name"), sym(D1, t, "name")
            diff = {tb: s1[tb] - s0[tb] for tb in s0 if tb in s1}
            est, ci = boot(diff)
            res[t] = {"with_minus_without": r(est), "ci": r(ci), "symmetric_with_information": r(boot(s1)[0])}
        out["capped" if field == "lo" else "uncapped"] = res
    out["best"] = out["capped"]["best"]
    b, bu = out["capped"]["best"]["ci"], out["uncapped"]["best"]["ci"]
    # PLAN.md change of about midnight: the sentence needs the test to hold on the uncapped logits as well
    out["smaller_with_information"] = bool(b[1] is not None and b[1] < 0 and bu[1] is not None and bu[1] < 0)
    return out


def question4(N):
    """Amendment 1: forward and reverse copies of the name's state against the placebo copies, at every layer."""
    # every copy against the unpatched prompt of its own unit: target b (the original) against base_b, a against base_a
    base = {(x["uid"], x["role"]): x["lo"] for x in N if x["role"] in ("base_a", "base_b")}
    copies = [dict(x, mode=x["key"][1]) for x in N if x["role"] == "copy"]
    layers = sorted({x["layer"] for x in copies})
    equal_pairs = {x["pair"] for x in copies if x["mode"] == "fwd_all"}
    pair_full = defaultdict(list)
    for x in N:
        if x["role"] == "base_a":
            b = base.get((x["uid"], "base_b"))
            if x["lo"] is not None and b is not None:
                pair_full[(x["pair"], x["table"], x["info"])].append(x["lo"] - b)

    def change(rows, mode, info, equal_only=False):
        vals, tabs = [], []
        for x in rows:
            if x["mode"] != mode or x["info"] != info or (equal_only and x["pair"] not in equal_pairs):
                continue
            ref = base.get((x["uid"], "base_b" if x["target"] == "b" else "base_a"))
            if x["lo"] is None or ref is None:
                continue
            vals.append(x["lo"] - ref)
            tabs.append(x["table"])
        return by_table(vals, tabs)

    out, ps = {"layers": {}, "pairs_with_names_of_equal_length": len(equal_pairs)}, []
    for li in layers:
        rows = [x for x in copies if x["layer"] == li]
        row = {}
        for info in (0, 1):
            F, PF, R, PR = (change(rows, m, info) for m in ("fwd", "pfwd", "rev", "prev"))
            dF = {t: F[t] - PF[t] for t in F if t in PF}
            dR = {t: R[t] - PR[t] for t in R if t in PR}
            keys = [k for k in pair_full if k[2] == info]
            full = by_table([float(np.mean(pair_full[k])) for k in keys], [k[1] for k in keys])
            share = boot(F, fn=lambda ts: float(np.mean([F[t] for t in ts if t in F]) / np.mean([full[t] for t in ts if t in full])))
            row[f"info{info}"] = {
                "forward": r(boot(F)[0]), "forward_ci": r(boot(F)[1]), "placebo_forward": r(boot(PF)[0]),
                "reverse": r(boot(R)[0]), "reverse_ci": r(boot(R)[1]), "placebo_reverse": r(boot(PR)[0]),
                "forward_minus_placebo": r(boot(dF)[0]), "forward_minus_placebo_ci": r(boot(dF)[1]),
                "reverse_minus_placebo": r(boot(dR)[0]), "reverse_minus_placebo_ci": r(boot(dR)[1]),
                "forward_share_of_crossed_minus_original": r(share[0]), "share_ci": r(share[1]),
                "equal_length_every_token": {"forward": r(boot(change(rows, "fwd_all", info, True))[0]),
                                             "reverse": r(boot(change(rows, "rev_all", info, True))[0]),
                                             "forward_last_tokens": r(boot(change(rows, "fwd", info, True))[0])}}
            if info == 0:
                pf = sign_flip_p(dF) if dF else 1.0
                pr = sign_flip_p({t: -v for t, v in dR.items()}) if dR else 1.0
                row["p_forward"], row["p_reverse"], row["p_layer"] = pf, pr, max(pf, pr)
                ps.append(max(pf, pr))
        out["layers"][li] = row
    adj = holm(ps) if ps else []
    for li, a in zip(layers, adj):
        out["layers"][li]["p_holm"] = a
    out["supported_layers"] = [li for li, a in zip(layers, adj) if a < 0.05]
    out["supported"] = bool(out["supported_layers"])
    return out


# ---------------------------------------------------------------- amendments 3, 6 and 7 (questions 6, 9 and 10)

def changes(rows, key, field="pb", base_role="base"):
    """{key(x): {table: mean over the rows of x[field] minus its unit's base}} for every row other than the base for
    which key(x) is not None, and the share of those rows without a letter, by key."""
    base = {x["uid"]: x for x in rows if x["role"] == base_role}
    acc, miss, n = defaultdict(lambda: defaultdict(list)), defaultdict(int), defaultdict(int)
    for x in rows:
        if x["role"] == base_role:
            continue
        k = key(x)
        if k is None:
            continue
        n[k] += 1
        b = base.get(x["uid"])
        if x.get(field) is None or b is None or b.get(field) is None:
            miss[k] += 1
            continue
        acc[k][x["table"]].append(x[field] - b[field])
    return ({k: {t: float(np.mean(v)) for t, v in d.items()} for k, d in acc.items()},
            {k: miss[k] / n[k] for k in n})


def levels(rows, cell, field="pb", base_role="base"):
    """{cell(x): {table: mean over items of the item's unpushed field}}: each item's base rows (one a unit) averaged
    first, so that an item split over several units counts once."""
    per_item = defaultdict(list)
    for x in rows:
        if x["role"] == base_role and x.get(field) is not None:
            per_item[(cell(x), x["table"], x["id"])].append(x[field])
    acc = defaultdict(lambda: defaultdict(list))
    for (c, t, _), v in per_item.items():
        acc[c][t].append(float(np.mean(v)))
    return {c: {t: float(np.mean(v)) for t, v in d.items()} for c, d in acc.items()}


def minus(A, B):
    return {t: A[t] - B[t] for t in A if t in B}


def ratio(num, den):
    """The ratio of the equal-weight means over tables, with its interval from the same resampling of tables."""
    common = sorted(t for t in num if t in den)

    def fn(ts):
        d = float(np.mean([den[t] for t in ts]))
        return float(np.mean([num[t] for t in ts]) / d) if d != 0 else float("nan")
    if not common:
        return None, [None, None]
    est, ci = boot({t: num[t] for t in common}, fn=fn)
    return est, ci


def patch_share(P, layer, span="postname", info=0, field="pb"):
    """Stage P's copy of the crossed prompt's states of the best product into the original: the change, and its share
    of the crossed-minus-original difference, at one layer (the most that a change at those tokens can do while the
    name's own tokens stay)."""
    base = {(x["uid"], x["role"]): x[field] for x in P if x["role"] in ("base_a", "base_b") and x.get(field) is not None}
    rows = [x for x in P if x["role"] == "copy" and x["key"][1] == span and x["layer"] == layer and x["info"] == info
            and x.get(field) is not None and (x["uid"], "base_b") in base and (x["uid"], "base_a") in base]
    eff = by_table([x[field] - base[(x["uid"], "base_b")] for x in rows], [x["table"] for x in rows])
    full = by_table([base[(x["uid"], "base_a")] - base[(x["uid"], "base_b")] for x in rows], [x["table"] for x in rows])
    est, ci = boot(eff)
    sh, sh_ci = ratio(eff, full)
    return {"effect": r(est, 4), "effect_ci": r(ci, 4), "share": r(sh), "share_ci": r(sh_ci),
            "share_of": "the crossed prompt minus the original (the best product with a familiar name against an "
                        "invented one)", "denominator": r(boot(full)[0], 4)}


MARGIN_SPEC = 0.02      # amendment 3, criterion 3: the reading of specifications falls by less than 2 points


def question6(E, manip, layer, P=None):
    """Amendment 3: the name eraser against the unerased prompt in its own unit, against the shuffled eraser, and with
    the names hidden; the share of the names-shown gap that it removes; the manipulation check's gates."""
    D, miss = changes(E, lambda x: (x["eraser"], x["layer"], x["names"], x["info"]))
    out = {"layer": layer, "missing_share_max": r(max(miss.values()) if miss else None, 4),
           "erasers_used": manip.get("erasers_used"), "readout_removed": bool(manip.get("eraser_removed_the_readout")),
           "question_6_read": bool(manip.get("question_6_read", True)),
           "manipulation_accuracy": {k: r(v) for k, v in manip.get("mean", {}).items()}}
    # the 60 per cent rule is applied to the mean over the categories (run_erase.py, as coded before the full jobs;
    # PLAN.md amendment 3's note of 22 November 2026); the margin by category is a description for the web appendix
    cats = manip.get("by_category") or {}
    after = [v.get("after_name") for v in cats.values() if v.get("after_name") is not None]
    out["manipulation_by_category"] = {"categories": len(after),
                                       "above_0_60_after_name": sum(a > 0.60 for a in after),
                                       "min_after_name": r(min(after)) if after else None,
                                       "max_after_name": r(max(after)) if after else None}
    L = levels([x for x in E if x["layer"] == layer], lambda x: (x["names"], x["info"]))
    for info in (0, 1):
        o = D.get(("name", layer, "original", info), {})
        sh = D.get(("shuffled", layer, "original", info), {})
        h = D.get(("name", layer, "hidden", info), {})
        gap = minus(L.get(("hidden", info), {}), L.get(("original", info), {}))
        c1, c2 = boot(o), boot(minus(o, sh))
        drop = boot({t: -v for t, v in h.items()})
        share = ratio(o, gap)
        res = {"names_shown_change": r(c1[0], 4), "names_shown_change_ci": r(c1[1], 4),
               "shuffled_change": r(boot(sh)[0], 4), "minus_shuffled": r(c2[0], 4), "minus_shuffled_ci": r(c2[1], 4),
               "names_hidden_drop": r(drop[0], 4), "names_hidden_drop_ci": r(drop[1], 4),
               "unerased_gap": r(boot(gap)[0], 4), "share_of_gap": r(share[0]), "share_of_gap_ci": r(share[1]),
               "share_of": "the names-hidden prompt minus the names-shown one, unerased",
               "spec_eraser_names_hidden_change": r(boot(D.get(("spec", layer, "hidden", info), {}))[0], 4),
               "spec_eraser_names_hidden_change_ci": r(boot(D.get(("spec", layer, "hidden", info), {}))[1], 4)}
        res["criteria"] = [excludes_zero(c1[1], 1), excludes_zero(c2[1], 1),
                           drop[1][1] is not None and drop[1][1] < MARGIN_SPEC]
        out[f"info{info}"] = res
    crit = out["info0"]["criteria"]
    out["read"] = out["readout_removed"] and out["question_6_read"]
    out["supported"] = bool(out["read"] and all(crit))
    out["not_specific"] = bool(out["read"] and crit[0] and crit[1] and not crit[2])
    out["secondary"] = {li: {"names_shown_change": r(boot(D.get(("name", li, "original", 0), {}))[0], 4),
                             "names_shown_change_ci": r(boot(D.get(("name", li, "original", 0), {}))[1], 4)}
                        for li in sorted({x["layer"] for x in E}) if li != layer}
    if P is not None:
        out["post_name_patch"] = patch_share(P, layer)
    return out


def words_q6(q):
    if q is None:
        return None
    if not q["readout_removed"]:
        return ("The eraser did not remove the linear readout in held-out categories (above 60 per cent after "
                "erasure); neither outcome is read as one about a linear readout, and the step is described in the web "
                "appendix.")
    if not q["question_6_read"]:
        return ("Neither eraser acts on a held-out category as on the categories it was fitted on; question 6 is "
                "described in the web appendix with both ratios.")
    x = q["info0"]["share_of_gap"]
    y = (q.get("post_name_patch") or {}).get("share")
    yci = (q.get("post_name_patch") or {}).get("share_ci") or [None, None]
    pct = lambda v: "an unknown share" if v is None else f"{100 * v:.0f} per cent"  # noqa: E731
    # the patch share with its interval (added on 22 November 2026 at 8:43 AM, after the first read of the results)
    ypart = pct(y) if yci[0] is None else f"{pct(y)}, {100 * yci[0]:.0f} to {100 * yci[1]:.0f},"
    if q["supported"]:
        return (f"Removing the linear difference between a familiar and an invented name from the product's later "
                f"tokens removes {pct(x)} of the gap between the names-hidden and names-shown prompts (the full patch "
                f"of those tokens reproduces {ypart} of the difference that giving the best product a familiar name "
                f"makes), while the model still picks the better product when the names are hidden.")
    if q["not_specific"]:
        return (f"Removing the linear difference from the product's later tokens removes {pct(x)} of the gap, but the "
                f"model's reading of the specifications falls by {100 * q['info0']['names_hidden_drop']:.1f} points with "
                f"the names hidden; the eraser is reported as not specific.")
    return ("Erasing the linear difference at the product's later tokens, at this layer, does not remove the name's "
            "effect; reported in the web appendix.")


def question9(K, windows, P=None, layer=None):
    """Amendment 6: in each window of layers, the names-shown change under the knockout of the names' tokens minus
    the change under the control knockout; Holm over the windows; the all-layer window's share of the gap."""
    D, miss = changes(K, lambda x: (x["kind"], x["window"], x["names"]))
    L = levels(K, lambda x: x["names"])
    gap = minus(L.get("hidden", {}), L.get("original", {}))
    ws = sorted({x["window"] for x in K if x["role"] == "knock"})
    out = {"missing_share_max": r(max(miss.values()) if miss else None, 4), "unknocked_gap": r(boot(gap)[0], 4),
           "windows": {}}
    ps = []
    for w in ws:
        meas = minus(D.get(("names", w, "original"), {}), D.get(("control", w, "original"), {}))
        est, ci = boot(meas)
        p = sign_flip_p(meas) if meas else 1.0
        ps.append(p)
        hid = boot(D.get(("names", w, "hidden"), {}))
        sh = ratio(meas, gap)
        out["windows"][w] = {"layers": windows[w] if windows else None, "measure": r(est, 4), "measure_ci": r(ci, 4),
                             "p_one_sided": p, "names_hidden_change": r(hid[0], 4), "names_hidden_change_ci": r(hid[1], 4),
                             "share_of_gap": r(sh[0]), "share_of_gap_ci": r(sh[1])}
    adj = holm(ps) if ps else []
    for w, a in zip(ws, adj):
        out["windows"][w]["p_holm"] = a
    held = [w for w, a in zip(ws, adj) if a < 0.05 and excludes_zero(out["windows"][w]["measure_ci"], 1)]
    every = (len(windows) - 1) if windows else (ws[-1] if ws else None)   # the last window is every layer (run_knock)
    out["supported_windows"] = [w for w in held if w != every]
    out["holds_for_every_layer_only"] = bool(every in held and not out["supported_windows"])
    out["every_layer_window"], out["every_layer_holds"] = every, bool(every in held)
    out["supported"] = bool(held)
    if P is not None and layer is not None:
        out["post_name_patch"] = patch_share(P, layer)
    return out


def words_q9(q):
    if q is None:
        return None
    y = (q.get("post_name_patch") or {}).get("effect")
    ys = "an unknown number of" if y is None else f"{100 * y:.1f}"
    if q["supported_windows"]:
        w = max(q["supported_windows"], key=lambda k: q["windows"][k]["measure"])
        a, b = q["windows"][w]["layers"][0], q["windows"][w]["layers"][-1]
        out = (f"When the answer cannot read the names in layers {a} to {b}, the model recommends the better product "
               f"more ({100 * q['windows'][w]['measure']:.1f} points), beside {ys} points through the product's later "
               f"tokens.")
        # the window of every layer, which the plan says gives how much of the gap passes this way at all (added on
        # 22 November 2026 at 8:43 AM, after the first read of the results)
        e = q.get("every_layer_window")
        if q.get("every_layer_holds") and e in q["windows"]:
            ew = q["windows"][e]
            share = "" if ew.get("share_of_gap") is None else f", {100 * ew['share_of_gap']:.0f} per cent of the gap"
            out += (f" When it cannot read them in any layer, the better product gains {100 * ew['measure']:.1f} "
                    f"points{share}.")
        return out
    if q["holds_for_every_layer_only"]:
        w = max(q["windows"], key=lambda k: len(q["windows"][k]["layers"] or []))
        return (f"When the answer cannot read the names in any layer, the model recommends the better product more "
                f"({100 * q['windows'][w]['measure']:.1f} points), beside {ys} points through the product's later "
                f"tokens; the effect is not found in one window.")
    return ("Blocking the answer's attention to the names does not change the recommendation more than blocking other "
            "tokens of the same products.")


def question10(RP, V, sep=None):
    """Amendment 7: the interaction of each push (its change with the names shown minus its change with the names
    hidden), each sign apart and symmetric, against the brevity push; in uncapped log-odds and in probability; and the
    caution projection of the names-shown state against the names-hidden one. sep: RISK_DIRS.json, whose two
    measures of criterion (a) at the chosen layer are reported (the separation within each question, the gate since the
    change of 22 November 2026 at about 4:00 AM Central, and the cut-off measure beside it)."""
    out = {"validation": {k: V.get(k) for k in ("passes", "chosen_layer", "chosen_size", "caution_symmetric",
                                                 "caution_ci", "caution_minus_brevity", "caution_minus_brevity_ci")}}
    li = V.get("chosen_layer")
    if sep and li is not None:
        for name, key in (("separation_within_question", "separation_held_out"),
                          ("separation_cutoff", "separation_held_out_cutoff")):
            if key in sep:
                out["validation"][name] = {k.split("|")[0]: r(v, 4) for k, v in sep[key].items()
                                           if k.endswith(f"|{li}")}
    if not V.get("passes"):
        out["supported"] = False
        return out
    dirs = sorted({x["dir"] for x in RP if x["role"] == "push"})
    for field in ("lo_u", "pb"):
        D, miss = changes(RP, lambda x: (x["dir"], x["sign"], x["names"], x["info"]), field)
        res = {"missing_share_max": r(max(miss.values()) if miss else None, 4)}
        for info in (0, 1):
            I, S = {}, {}
            for d in dirs:
                I[d] = {sg: minus(D.get((d, sg, "original", info), {}), D.get((d, sg, "hidden", info), {}))
                        for sg in (1, -1)}
                S[d] = {t: (I[d][1][t] - I[d][-1][t]) / 2 for t in I[d][1] if t in I[d][-1]}
            cb = minus(S.get("caution", {}), S.get("brevity", {}))
            res[f"info{info}"] = {
                d: {"interaction_added": r(boot(I[d][1])[0], 4), "interaction_subtracted": r(boot(I[d][-1])[0], 4),
                    "symmetric": r(boot(S[d])[0], 4), "symmetric_ci": r(boot(S[d])[1], 4)} for d in dirs}
            res[f"info{info}"]["caution_minus_brevity"] = r(boot(cb)[0], 4)
            res[f"info{info}"]["caution_minus_brevity_ci"] = r(boot(cb)[1], 4)
            # added on 22 November 2026 at 10:02 AM Central: beside the brevity push, the caution push minus
            # the mean of the random pushes of the same size, which describes and decides nothing
            rnd = [d for d in dirs if d.startswith("rand")]
            cr = {t: S["caution"][t] - float(np.mean([S[k][t] for k in rnd]))
                  for t in S.get("caution", {}) if rnd and all(t in S[k] for k in rnd)}
            res[f"info{info}"]["caution_minus_random_mean"] = r(boot(cr)[0], 4) if cr else None
            res[f"info{info}"]["caution_minus_random_mean_ci"] = r(boot(cr)[1], 4) if cr else None
        out[field] = res
    c = out["lo_u"]["info0"]["caution"]
    signs = (c["interaction_added"] is not None and c["interaction_added"] < 0 and c["interaction_subtracted"] is not None
             and c["interaction_subtracted"] > 0)
    out["signs_as_predicted"] = bool(signs)
    out["supported"] = bool(signs and excludes_zero(c["symmetric_ci"], -1)
                            and excludes_zero(out["lo_u"]["info0"]["caution_minus_brevity_ci"], -1))
    cp = out["pb"]["info0"]["caution"]
    out["probability_holds"] = bool(excludes_zero(cp["symmetric_ci"], -1) and cp["symmetric"] is not None
                                    and abs(cp["symmetric"]) >= MIN_PROBABILITY_EFFECT)
    # the words "through caution": the names-shown state lies further along the caution direction than the
    # names-hidden state of the same table, trial and rung
    per = defaultdict(list)
    for x in RP:
        if x["role"] == "base" and x["info"] == 0 and x.get("caution_projection") is not None:
            per[(x["table"], x["trial"], x["rung"], x["names"])].append(x["caution_projection"])
    diffs, tabs = [], []
    for (t, tr, ru, nm), v in per.items():
        if nm == "original" and (t, tr, ru, "hidden") in per:
            diffs.append(float(np.mean(v)) - float(np.mean(per[(t, tr, ru, "hidden")])))
            tabs.append(t)
    est, ci = boot(by_table(diffs, tabs))
    out["names_shown_state_further_along"] = r(est, 4)
    out["names_shown_state_further_along_ci"] = r(ci, 4)
    out["through_caution"] = bool(out["supported"] and excludes_zero(ci, 1))
    return out


def words_q10(q):
    if q is None:
        return None
    if not q["validation"]["passes"]:
        return "The caution direction could not be built from product-free choices; reported in the web appendix."
    if not q["supported"]:
        return "Making the model more cautious does not change how much it favors familiar names."
    s = ("Part of the gap passes through the model's caution: a direction that makes it more cautious in choices "
         "without products makes it favor familiar names more, and its opposite less." if q["through_caution"]
         else "A more cautious model favors familiar names more.")
    if not q["probability_holds"]:
        s += (" At the size chosen on the product-free questions, the push changed how much the model's preference "
              "favored familiar names, without changing how often it recommends them.")
    return s


# ---------------------------------------------------------------- amendments 4 and 5 (questions 7 and 8)

MARGIN_HIDDEN = 0.02    # amendment 4, criterion 3: with the names hidden, other products rise by less than 2 points
MISSING_LIMIT = 0.05    # the plan's rule: more than 5 per cent of a condition without a letter stops the reading
MARGIN_MMLU = 0.03      # amendment 4, criterion 4: MMLU accuracy falls by less than 3 points


def letters(rows, pick):
    """{id: (row, parsed letter or None)}; Study 2's parser gives an empty letter when it finds none."""
    return {x["id"]: (x, pick(x.get("answer") or "")[0] or None) for x in rows}


def paired(A, B, keep, value):
    """{table: mean over items answered with a letter in both of value(row, letter of B) - value(row, letter of A)},
    over the items for which keep(row) holds."""
    vals, tabs = [], []
    for i, (x, la) in A.items():
        if i not in B or not keep(x):
            continue
        lb = B[i][1]
        if la is None or lb is None:
            continue
        vals.append(value(x, lb) - value(x, la))
        tabs.append(x["table"])
    return by_table(vals, tabs)


def boot_items(diffs, draws=DRAWS, seed=SEED):
    """The mean of paired differences and its interval, resampling items (MMLU's questions)."""
    x = np.array(diffs, dtype=float)
    if not len(x):
        return None, [None, None]
    rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (draws, len(x)))].mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(x.mean()), [float(lo), float(hi)]


def question7(ans, dom2_tables, pick, edit_check=None):
    """Amendment 4: each edited model's answers against the unedited model's, item by item (the same prompts and seeds),
    on Study 1's tables shared with dom2; the share of recommendations of a product other than the best (non-best).
    ans: {edit: {set: answer rows}}."""
    L = {e: {s: letters(rows, pick) for s, rows in sets.items()} for e, sets in ans.items()}
    nonbest = lambda x, l: float(l != x["best"])  # noqa: E731
    base = L.get("none", {})
    out = {"edits": sorted(L), "edit_check": edit_check,
           "parsed_share": {e: {s: r(np.mean([l is not None for _, l in v.values()]) if v else None)
                                for s, v in sets.items()} for e, sets in L.items()},
           # beside criterion 4 (STATUS, 21 November 2026, 9:15 PM, from the pilot 12678): the share of each edit's
           # answers that reached the token cap, a description that enters no criterion
           "cut_share": {e: {s: r(np.mean([x.get("finish") == "length" for x in rows]) if rows else None)
                             for s, rows in sets.items()} for e, sets in ans.items()}}
    in30 = lambda x: x["table"] in dom2_tables  # noqa: E731

    def s1(edit, cell, tables=in30):
        if "s1" not in base or "s1" not in L.get(edit, {}):
            return {}
        return paired(base["s1"], L[edit]["s1"], lambda x: x["cell"] == cell and tables(x), nonbest)
    shown, hidden = s1("name", "shown"), s1("name", "hidden_clean")
    rshown = s1("random", "shown")
    c1, c2, c3 = boot(shown), boot(minus(shown, rshown)), boot(hidden)
    gap = boot(minus(shown, hidden))
    out["s1"] = {"names_shown_change": r(c1[0], 4), "names_shown_change_ci": r(c1[1], 4),
                 "random_names_shown_change": r(boot(rshown)[0], 4),
                 "random_names_shown_change_ci": r(boot(rshown)[1], 4),
                 "minus_random": r(c2[0], 4), "minus_random_ci": r(c2[1], 4),
                 "names_hidden_rise": r(c3[0], 4), "names_hidden_rise_ci": r(c3[1], 4),
                 "gap_change": r(gap[0], 4), "gap_change_ci": r(gap[1], 4),
                 "tables": len(shown),
                 "outside_dom2": {"names_shown_change": r(boot(s1("name", "shown", lambda x: not in30(x)))[0], 4),
                                  "names_hidden_change": r(boot(s1("name", "hidden_clean", lambda x: not in30(x)))[0], 4)},
                 "reliability_edit_names_shown_change": r(boot(s1("reliability", "shown"))[0], 4)}
    mm = None
    if "mmlu" in base and "mmlu" in L.get("name", {}):
        A = base["mmlu"]

        def drop(edit):
            B = L[edit]["mmlu"]
            d = [float(B[i][1] == x["best"]) - float(la == x["best"]) for i, (x, la) in A.items() if i in B]
            est, ci = boot_items([-v for v in d])
            return len(d), r(est, 4), r(ci, 4)
        n, est, ci = drop("name")
        mm = {"questions": n, "accuracy_unedited": r(np.mean([la == x["best"] for x, la in A.values()])),
              "drop": est, "drop_ci": ci,
              # every edit's drop, a description beside criterion 4 (the random and reliability edits' cost)
              "drop_by_edit": {e: dict(zip(("drop", "drop_ci"), drop(e)[1:])) for e in L
                               if e != "none" and "mmlu" in L[e]}}
    out["mmlu"] = mm
    # a criterion whose edit or questions were not run is None (not tested), not False
    random_run = "random" in L and "s1" in L["random"]
    crit = [excludes_zero(c1[1], -1), excludes_zero(c2[1], -1) if random_run else None,
            c3[1][1] is not None and c3[1][1] < MARGIN_HIDDEN,
            None if mm is None else bool(mm["drop_ci"][1] is not None and mm["drop_ci"][1] < MARGIN_MMLU)]
    out["criteria"] = crit
    # the plan's rule (PLAN.md, the outcome): more than 5 per cent of a condition without a letter stops the reading
    # until the cause is found. Applied to the sets that the criteria read (Study 1's tables and MMLU) for the edits that
    # they compare (none, name, random); found on 22 November 2026 at about 10:55 AM Central, when every edited Gemma 4
    # 31B (13345) reached the token cap in nearly every answer
    # per condition, as the rule says ("of any condition"; corrected at 11:25 AM the same day): each cell that a criterion
    # reads (Study 1's tables shared with dom2, with and without brand names) and MMLU
    def share(edit, s, keep):
        v = [l is not None for x, l in L.get(edit, {}).get(s, {}).values() if keep(x)]
        return float(np.mean(v)) if v else None
    cells = {"s1|shown": ("s1", lambda x: x["cell"] == "shown" and in30(x)),
             "s1|hidden_clean": ("s1", lambda x: x["cell"] == "hidden_clean" and in30(x)),
             "mmlu": ("mmlu", lambda x: True)}
    low = {f"{e}|{c}": r(v) for e in ("none", "name", "random") for c, (s, keep) in cells.items()
           for v in [share(e, s, keep)] if v is not None and v < 1 - MISSING_LIMIT}
    out["read"] = not low
    out["below_the_letter_rule"] = low
    out["supported"] = bool(out["read"] and all(c is True for c in crit))
    for s, cells in (("dom2", [("original", 0), ("hidden", 0), ("original", 1), ("hidden", 1)]),
                     ("requests", [("original", None), ("hidden", None)])):
        if s in base and s in L.get("name", {}):
            out[s] = {f"{nm}|info{inf}" if inf is not None else nm:
                      r(boot(paired(base[s], L["name"][s], lambda x, nm=nm, inf=inf: x["names"] == nm and
                                    (inf is None or x.get("info") == inf), nonbest))[0], 4) for nm, inf in cells}
    return out


def words_q7_unread(q):
    """The test was not read under the letter rule: the fact, in numbers (the edited models' share of answers with a
    recommendation and at the token cap on Study 1's tables, against the unedited model's)."""
    ps, cs = q["parsed_share"], q["cut_share"]
    edited = [e for e in ps if e != "none" and ps[e].get("s1") is not None]
    top = max(ps[e]["s1"] for e in edited)
    cut = min(cs[e]["s1"] for e in edited if (cs.get(e) or {}).get("s1") is not None)
    every = len(edited) > 1 and all(ps[e]["s1"] < 1 - MISSING_LIMIT for e in edited)
    who = "Every edited version of the model, the control edits included," if every else "The edited model"
    return (f"{who} reached the length limit in at least {100 * cut:.1f} per cent of its responses on Study 1's tables "
            f"and gave a recommendation in at most {100 * top:.1f} per cent of them (the unedited model in "
            f"{100 * ps['none']['s1']:.1f} per cent), so the edit could not be tested on this model.")


def words_q7(q):
    if q is None:
        return None
    if not q.get("read", True):
        return words_q7_unread(q)
    c = q["criteria"]
    x = -100 * q["s1"]["gap_change"] if q["s1"]["gap_change"] is not None else None
    if c[1] is None:
        return ("The random edit was not run, so the edit is not tested against an edit of the same kind; the change in "
                f"the names-shown share of other products is {100 * (q['s1']['names_shown_change'] or 0):.1f} points.")
    if q["supported"]:
        return (f"Removing one direction from the model's weights, with no training, lowers the gap on Study 1's tables "
                f"by {x:.1f} points, while its accuracy on general questions falls by less than 3 points.")
    if c[0] and c[1] and c[2]:          # criterion 4 failed or was not measured
        drop = (q["mmlu"] or {}).get("drop")
        cost = "was not measured" if drop is None else f"falls by {100 * drop:.1f} points"
        return (f"Removing one direction from the model's weights lowers the gap on Study 1's tables by {x:.1f} "
                f"points, and its accuracy on general questions {cost}.")
    if c[0] and c[1]:
        return (f"Removing the direction lowers the gap on Study 1's tables by {x:.1f} points, but with the names "
                f"hidden the share of other products rises by {100 * q['s1']['names_hidden_rise']:.1f} points; the edit "
                f"is reported in the web appendix with both changes.")
    if not c[0]:
        return words_q7_no_change(q)
    return "The edit is reported in the web appendix as having no effect beyond a random edit of the same kind."


def words_q7_no_change(q):
    """Criterion 1 fails: the fact, not the table's label (PLAN.md, amendment 4, the note of 22 November 2026, 8:25 to
    8:31 AM Central). The name edit's change in the
    names-shown share of other products, and whether it changed accuracy on general questions; then, when the random
    edit's own change in that share or in accuracy has an interval that excludes zero, what the random edit did, so that
    it cannot serve as a control for the name. The cut shares and the directions' sizes stay in the web appendix."""
    s, mm = q["s1"], q["mmlu"] or {}
    moved = lambda ci: ci and ci[0] is not None and (ci[0] > 0 or ci[1] < 0)  # noqa: E731
    # the verb from the interval (22 November 2026, 8:43 AM, after the first read of the results): "did not lower" when it
    # includes zero, "raised" when it lies above zero (criterion 1 fails either way)
    if moved(s["names_shown_change_ci"]) and s["names_shown_change"] > 0:
        out = (f"Removing the name direction from the weights raised the share of other products by "
               f"{100 * s['names_shown_change']:.1f} points with the names shown")
    else:
        out = (f"Removing the name direction from the weights did not lower the share of other products "
               f"({100 * s['names_shown_change']:+.1f} points with the names shown)")
    if mm.get("drop") is not None:
        out += (" or general accuracy" if not moved(mm["drop_ci"])
                else f", and it {'lowered' if mm['drop'] > 0 else 'raised'} general accuracy by "
                     f"{100 * abs(mm['drop']):.1f} points")
    rc, rci = s.get("random_names_shown_change"), s.get("random_names_shown_change_ci")
    rd = (mm.get("drop_by_edit") or {}).get("random") or {}
    did = []
    if rc is not None and moved(rci):
        did.append(f"{'raised' if rc > 0 else 'lowered'} that share by {100 * abs(rc):.1f} points")
    if rd.get("drop") is not None and moved(rd.get("drop_ci")):
        did.append(f"{'lowered' if rd['drop'] > 0 else 'raised'} accuracy by {100 * abs(rd['drop']):.1f} points")
    if did:
        out += ("; a random direction removed the same way " + " and ".join(did) +
                ", so the random edit cannot serve as a control for the name")
    return out + "."


def reliability_curve(pairs, proj, layers, spans, dirs):
    """Amendment 5's layer rule read from proj.npz: at each stored layer, the share of reliability pairs whose
    projection on the direction fitted without their category is above zero, equal weight for every table, at the
    close token (the same rule as run_mech.reliability_curve, which reads no name data)."""
    si, di = list(spans).index("close"), list(dirs).index("rel")
    rel = [k for k, p in enumerate(pairs) if p["contrast"] == "reliability"]
    P = proj.astype(np.float64)
    return {int(li): float(np.mean(list(by_table([float(P[k, j, si, di] > 0) for k in rel],
                                                 [pairs[k]["table"] for k in rel]).values())))
            for j, li in enumerate(layers)}


def ranks(x):
    """Ranks from 1, ties given their mean rank."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    rk = np.empty(len(x))
    rk[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            rk[m] = rk[m].mean()
    return rk


def spearman(x, y):
    a, b = ranks(x), ranks(y)
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def scaled_ranks(values, cats):
    """Within each category the values are ranked (ties at their mean rank) and the ranks scaled to run from -1 to 1;
    a category with one unit gives None (it holds no ranking)."""
    out = [None] * len(values)
    by = defaultdict(list)
    for i, c in enumerate(cats):
        by[c].append(i)
    for c, idx in by.items():
        if len(idx) < 2:
            continue
        rk = ranks([values[i] for i in idx])
        for i, v in zip(idx, rk):
            out[i] = float(2 * (v - 1) / (len(idx) - 1) - 1)
    return out


def within_corr(x, y, cats):
    """PLAN.md, amendment 2's statistic: the correlation over all units of the two variables' within-category scaled
    ranks."""
    keep = [i for i in range(len(x)) if x[i] is not None and y[i] is not None]
    x, y, cats = [x[i] for i in keep], [y[i] for i in keep], [cats[i] for i in keep]
    a, b = scaled_ranks(x, cats), scaled_ranks(y, cats)
    pairs_ = [(u, v) for u, v in zip(a, b) if u is not None and v is not None]
    if len(pairs_) < 3:
        return None
    u, v = np.array(pairs_).T
    if u.std() == 0 or v.std() == 0:
        return None
    return float(np.corrcoef(u, v)[0, 1])


def split_half(units, even, odd, cats):
    """Split-half reliability of a unit-level variable: the within-category correlation of its even-trial and
    odd-trial means, raised by the Spearman-Brown formula, and the correlation pooled over categories beside it."""
    keep = [k for k, u in enumerate(units) if even[k] is not None and odd[k] is not None]
    e, o, c = [even[k] for k in keep], [odd[k] for k in keep], [cats[k] for k in keep]
    rw = within_corr(e, o, c)
    rp = spearman(e, o) if len(keep) >= 3 else None
    sb = lambda x: None if x is None or x <= -1 else 2 * x / (1 + x)  # noqa: E731
    return {"units": len(keep), "within_category": r(rw), "spearman_brown": r(sb(rw)), "pooled": r(rp),
            "pooled_spearman_brown": r(sb(rp))}


# ---------------------------------------------------------------- amendment 2 (question 5)

TRIAL_SCORES = ("image", "renamed_equity", "copy")
NAME_SCORES = ("awareness", "awareness_sae", "words", "words_neutral")
MIN_RELIABILITY = 0.5
MIN_COPY_PAIRS = 3
GEMMA_NAMES = {"gemma31b": "Gemma 4 31B", "gemma4-26b": "Gemma 4 26B A4B"}


def brand_units(beh_rows, kind):
    """{unit: {brand, category, tables, halves, per (table, half)}} of the behavioral ranking's candidate `kind`."""
    d = {}
    for x in beh_rows:
        if x["kind"] != kind:
            continue
        u = f"{x['brand']}|{x['category']}"
        e = d.setdefault(u, {"brand": x["brand"], "category": x["category"], "tables": set(), "h": ([], []),
                             "per": defaultdict(list)})
        e["tables"].add(x["table"])
        e["h"][x["trial"] % 2].append(x["value"])
        e["per"][(x["table"], x["trial"] % 2)].append(x["value"])
    return d


def score_halves(score_rows):
    """{score: (even {unit: mean}, odd {unit: mean}, n {unit: rows}, by phrasing {unit: [means]} or None)}. A score
    read from tables (image, the renamed equity, the copy) is centered within table (centered_halves); a name-level
    score is the mean over its phrasings, the same in both halves."""
    trial = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    name = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for x in score_rows:
        if x["score"].endswith("_holdout"):          # the hold-out rows of the awareness control, not a score
            continue
        u = f"{x['brand']}|{x['category']}"
        if x["score"] in TRIAL_SCORES:
            trial[x["score"]][u][(x["table"], x["trial"] % 2)].append(x["value"])
        else:
            name[x["score"]][u][x["phrasing"] or 0].append(x["value"])
    out = {}
    for s, d in trial.items():
        ev, od = centered_halves(d)
        out[s] = (ev, od, {u: sum(len(v) for v in per.values()) for u, per in d.items()}, None)
    for s, d in name.items():
        ph = {u: [float(np.mean(v[k])) for k in sorted(v)] for u, v in d.items()}
        val = {u: float(np.mean(v)) for u, v in ph.items()}
        out[s] = (val, val, {u: sum(len(v[k]) for k in v) for u, v in d.items()}, ph)
    return out


def cross_half(us, S, B, cat):
    """The mean of two within-category correlations: the score's even trials against the ranking's odd trials, and
    the reverse, over the units us (a unit may repeat in a resampled set)."""
    c = [cat[u] for u in us]
    rs = [within_corr([S[0].get(u) for u in us], [B[1].get(u) for u in us], c),
          within_corr([S[1].get(u) for u in us], [B[0].get(u) for u in us], c)]
    rs = [x for x in rs if x is not None and not math.isnan(x)]
    return float(np.mean(rs)) if rs else None


def table_boot(units_tables, stat, draws=DRAWS, seed=SEED):
    """A statistic of the units, its interval from resampling tables (a unit enters once for each drawn table that
    holds it, so that a table's brands move together; pre-mortem row 12), and its one-sided p-value: one plus the draws
    at or below zero, over one plus the draws (PLAN.md, amendment 2, change of 5:00 AM)."""
    tables = sorted({t for ts in units_tables.values() for t in ts})
    members = {t: [u for u in sorted(units_tables) if t in units_tables[u]] for t in tables}
    est = stat(sorted(units_tables))
    if est is None or not tables:
        return None, [None, None], None
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(draws):
        v = stat([u for t in rng.choice(tables, len(tables)) for u in members[t]])
        if v is not None and not math.isnan(v):
            bs.append(v)
    if not bs:
        return est, [None, None], None
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, [float(lo), float(hi)], float((1 + sum(b <= 0 for b in bs)) / (1 + len(bs)))


def centered_halves(per, min_units=2):
    """per: {unit: {(table, half): [values]}}. Each unit's value in a table and half minus the mean over the units of
    that table and half, then averaged over the unit's tables: what is left is the brand's standing within its tables,
    without the table's own level (PLAN.md, amendment 2, change of about 6:20 AM). A table and half that holds fewer
    than min_units units gives no comparison and is left out (a unit alone would be centered to exactly zero; in the
    on-best candidate 30 of the 60 cells hold one unit)."""
    cell = defaultdict(list)
    um = {}
    for u, d in per.items():
        for (t, h), v in d.items():
            m = float(np.mean(v))
            um[(u, t, h)] = m
            cell[(t, h)].append(m)
    tm = {k: float(np.mean(v)) for k, v in cell.items()}
    out = ({}, {})
    for (u, t, h), m in um.items():
        if len(cell[(t, h)]) < min_units:
            continue
        out[h].setdefault(u, []).append(m - tm[(t, h)])
    return tuple({u: float(np.mean(v)) for u, v in o.items()} for o in out)


def perm_p(us, S, B, cat, perms=FLIPS, seed=SEED, stat=None):
    """One-sided p-value of cross_half (or of stat(us, ranking)) by permuting the ranking's values among the units of
    each category, the score held fixed: one plus the permutations at or above the observed value, over one plus the
    permutations."""
    if stat is None:
        stat = lambda xs, Bx: cross_half(xs, S, Bx, cat)  # noqa: E731
    obs = stat(us, B)
    if obs is None:
        return None, None
    by = defaultdict(list)
    for u in us:
        by[cat[u]].append(u)
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for _ in range(perms):
        m = {}
        for c, members in by.items():
            for u, v in zip(members, rng.permutation(members)):
                m[u] = v
        Bp = tuple({u: b[m[u]] for u in us if m[u] in b} for b in B)
        v = stat(us, Bp)
        if v is not None:
            n += 1
            hits += v >= obs
    return obs, float((1 + hits) / (1 + n))


def phrasing_reliability(ph, cat):
    """A name-level score's reliability across phrasings on the test's statistic: the mean within-category correlation
    between two phrasings' unit means, raised to all phrasings by the Spearman-Brown formula; pooled beside."""
    us = sorted(u for u, v in ph.items() if len(v) == max(len(v) for v in ph.values()))
    if len(us) < 3:
        return {"units": len(us), "within_category": None, "spearman_brown": None, "pooled": None}
    k = len(ph[us[0]])
    if k < 2:
        return {"units": len(us), "within_category": None, "spearman_brown": None, "pooled": None}
    c = [cat[u] for u in us]
    rw = [within_corr([ph[u][i] for u in us], [ph[u][j] for u in us], c) for i in range(k) for j in range(i + 1, k)]
    rp = [spearman([ph[u][i] for u in us], [ph[u][j] for u in us]) for i in range(k) for j in range(i + 1, k)]
    rw = [x for x in rw if x is not None]
    m = float(np.mean(rw)) if rw else None
    sb = None if m is None or m <= -1 / (k - 1) else k * m / (1 + (k - 1) * m)
    return {"units": len(us), "phrasings": k, "within_category": r(m), "spearman_brown": r(sb), "pooled": r(float(np.mean(rp)))}


def ols_image(us, y, aw, im, cat):
    """Keller's regression: the ranking's within-category scaled rank on awareness's and image's, with the category
    held fixed; the image coefficient."""
    c = [cat[u] for u in us]
    Y, A_, I_ = scaled_ranks([y[u] for u in us], c), scaled_ranks([aw[u] for u in us], c), scaled_ranks([im[u] for u in us], c)
    keep = [k for k in range(len(us)) if Y[k] is not None and A_[k] is not None and I_[k] is not None]
    if len(keep) < 6:
        return None
    cats = sorted({c[k] for k in keep})
    X = np.array([[A_[k], I_[k]] + [float(c[k] == g) for g in cats] for k in keep])
    beta = np.linalg.lstsq(X, np.array([Y[k] for k in keep]), rcond=None)[0]
    return float(beta[1])


MIN_NAMES_A_KIND = 5


def holdout_control(score_rows, tag):
    """Awareness's control from stage S's hold-out rows (PLAN.md, amendment 2, change of about 5:30 AM): each name's
    accuracy is the mean over its held-out prompts; the balanced accuracy is the mean of the real names' and the invented
    names' accuracies; it must reach 0.75 over all names and within every token count that holds at least five names of
    each kind (every 1-token name is real, so a direction that read the length alone would pass a plain accuracy)."""
    hr = [x for x in score_rows if x["score"] == f"{tag}_holdout"]
    if not hr:
        return None
    per = defaultdict(list)
    for x in hr:
        per[(x["brand"], x["name_kind"], x["tokens"])].append(x["value"])
    names = [(b, k, n, float(np.mean(v))) for (b, k, n), v in per.items()]

    def bal(sub):
        acc = [np.mean([a for _, k_, _, a in sub if k_ == k]) for k in ("real", "invented") if any(k_ == k for _, k_, _, _ in sub)]
        return float(np.mean(acc)) if len(acc) == 2 else None
    groups = {}
    for n in sorted({n for _, _, n, _ in names}):
        sub = [x for x in names if x[2] == n]
        nr, ni = sum(x[1] == "real" for x in sub), sum(x[1] == "invented" for x in sub)
        groups[str(n)] = {"real_names": nr, "invented_names": ni, "balanced_accuracy": r(bal(sub)),
                          "counted": nr >= MIN_NAMES_A_KIND and ni >= MIN_NAMES_A_KIND}
    overall = bal(names)
    counted = [g for g in groups.values() if g["counted"]]
    ok = bool(overall is not None and overall >= 0.75 and counted and all(g["balanced_accuracy"] >= 0.75 for g in counted))
    return {"balanced_accuracy": r(overall), "by_name_tokens": groups, "passes": ok}


def question5(beh_rows, kind, score_rows, extras, copy_layer, probe_accuracy, log_freq, lane1_equity=None,
              draws=DRAWS, perms=FLIPS):
    """Amendment 2 for one model: every score's within-category correlation with the behavioral ranking (across halves
    of the trials), the values read from tables centered within table; its one-sided p-value from permuting the ranking
    among the units of each category; its interval from resampling tables (described); its reliability and control
    (PLAN.md, amendment 2, change of about 6:20 AM, after q5_null_calibration.json)."""
    U = brand_units(beh_rows, kind)
    cat = {u: e["category"] for u, e in U.items()}
    tabs = {u: e["tables"] for u, e in U.items()}
    B = centered_halves({u: e["per"] for u, e in U.items()})
    Bfull = {u: float(np.mean([b[u] for b in B if u in b])) for u in U if any(u in b for b in B)}
    us = sorted(U)
    S = score_halves(score_rows)
    out = {"ranking": kind, "units": len(us), "brands": len({e["brand"] for e in U.values()}),
           "ranking_reliability": split_half(us, [B[0].get(u) for u in us], [B[1].get(u) for u in us],
                                             [cat[u] for u in us]), "scores": {}}
    for s, (ev, od, n, ph) in sorted(S.items()):
        if s == "copy":     # a brand with fewer than three such pairs is not scored
            ev = {u: v for u, v in ev.items() if n.get(u, 0) >= MIN_COPY_PAIRS}
            od = {u: v for u, v in od.items() if n.get(u, 0) >= MIN_COPY_PAIRS}
        sub = {u: tabs[u] for u in us if u in ev or u in od}
        est, ci, _ = table_boot(sub, lambda xs: cross_half(xs, (ev, od), B, cat), draws=draws)
        _, p = perm_p(sorted(sub), (ev, od), B, cat, perms=perms)
        rel = (phrasing_reliability({u: v for u, v in ph.items() if u in cat}, cat) if ph is not None else
               split_half(sorted(sub), [ev.get(u) for u in sorted(sub)], [od.get(u) for u in sorted(sub)],
                          [cat[u] for u in sorted(sub)]))
        measured = rel["spearman_brown"] is not None and rel["spearman_brown"] >= MIN_RELIABILITY
        out["scores"][s] = {"correlation": r(est), "ci": r(ci), "p_one_sided": p, "units": len(sub),
                            "reliability": rel, "measured": bool(measured)}
    sc = out["scores"]
    # the controls
    acc_by_len = extras.get("awareness_accuracy_by_name_tokens") or {}
    aw = sc.get("awareness")
    if aw is not None:
        brand_aw = defaultdict(list)
        for u in us:
            v = S["awareness"][0].get(u)
            if v is not None:
                brand_aw[U[u]["brand"]].append(v)
        bvals = {b: float(np.mean(v)) for b, v in brand_aw.items() if b in log_freq}
        btabs = defaultdict(set)
        for u in us:
            btabs[U[u]["brand"]] |= tabs[u]
        fe, fci, _ = table_boot({b: btabs[b] for b in bvals},
                                lambda bs: spearman([bvals[b] for b in bs], [log_freq[b] for b in bs]) if len(bs) >= 3 else None,
                                draws=draws)
        # its test: the frequencies permuted among the brands, one-sided (one value a brand)
        bl = sorted(bvals)
        fp = None
        if len(bl) >= 3:
            obs = spearman([bvals[b] for b in bl], [log_freq[b] for b in bl])
            rng = np.random.default_rng(SEED)
            f = np.array([log_freq[b] for b in bl])
            null = [spearman([bvals[b] for b in bl], rng.permutation(f)) for _ in range(perms)]
            fp = float((1 + sum(v >= obs for v in null)) / (1 + perms))
        aw["frequency_correlation"], aw["frequency_correlation_ci"] = r(fe), r(fci)
        aw["frequency_p_one_sided"] = fp
        acc = extras.get("awareness_held_out_accuracy")
        aw["held_out_accuracy"] = r(acc)
        aw["accuracy_by_name_tokens"] = acc_by_len
        hc = holdout_control(score_rows, "awareness")
        aw["holdout"] = hc
        freq_ok = fp is not None and fp < 0.05
        if hc is not None:
            aw["control"] = bool(hc["passes"] and freq_ok)
        else:               # a brand read without hold-out rows (written before 5:30 AM): the plain accuracies
            aw["control"] = bool(acc is not None and acc >= 0.75 and all(v >= 0.75 for v in acc_by_len.values()) and freq_ok)
    if "awareness_sae" in sc:
        fve = extras.get("sae_fraction_of_variance_explained")
        sc["awareness_sae"]["fraction_of_variance_explained"] = r(fve)
        hs = holdout_control(score_rows, "awareness_sae")
        sc["awareness_sae"]["holdout"] = hs
        sc["awareness_sae"]["control"] = bool(fve is not None and fve >= 0.5 and (hs is None or hs["passes"]))
    if "image" in sc:
        sc["image"]["probe_accuracy"] = r(probe_accuracy)
        sc["image"]["control"] = bool(probe_accuracy is not None and probe_accuracy >= 0.75)
    if "words" in sc and "words_neutral" in sc:
        W, N = S["words"], S["words_neutral"]
        sub = {u: tabs[u] for u in us if u in W[0] and u in N[0]}
        diff = lambda xs, Bx: (lambda a, b: None if a is None or b is None else a - b)(  # noqa: E731
            cross_half(xs, W[:2], Bx, cat), cross_half(xs, N[:2], Bx, cat))
        de, dci, _ = table_boot(sub, lambda xs: diff(xs, B), draws=draws)
        _, dp = perm_p(sorted(sub), None, B, cat, perms=perms, stat=diff)
        sc["words"]["minus_neutral"], sc["words"]["minus_neutral_ci"] = r(de), r(dci)
        sc["words"]["minus_neutral_p_one_sided"] = dp
        sc["words"]["control"] = bool(dp is not None and dp < 0.05)
    if "copy" in sc:
        sc["copy"]["control"] = copy_layer is not None
    elif copy_layer is None:
        sc["copy"] = {"control": False, "failed": "question 4 has no supported layer"}
    # Keller's regression of the ranking on awareness and image, with the category held fixed
    if "awareness" in S and "image" in S:
        aw_v, im_v = S["awareness"][0], {u: float(np.mean([v for v in (S["image"][0].get(u), S["image"][1].get(u))
                                                            if v is not None])) for u in us
                                         if u in S["image"][0] or u in S["image"][1]}
        sub = {u: tabs[u] for u in us if u in aw_v and u in im_v}
        ie, ici, _ = table_boot(sub, lambda xs: ols_image(xs, Bfull, aw_v, im_v, cat), draws=draws)
        # its test: image permuted among the units of each category, awareness and the ranking held (change of about 6:30 AM)
        kp = None
        if ie is not None:
            ks = sorted(sub)
            byc = defaultdict(list)
            for u in ks:
                byc[cat[u]].append(u)
            rng = np.random.default_rng(SEED)
            hits = n_ok = 0
            for _ in range(perms):
                m = {}
                for c, mem in byc.items():
                    for u, v in zip(mem, rng.permutation(mem)):
                        m[u] = im_v[v]
                v = ols_image(ks, Bfull, aw_v, m, cat)
                if v is not None:
                    n_ok += 1
                    hits += v >= ie
            kp = float((1 + hits) / (1 + n_ok)) if n_ok else None
        out["keller_image_coefficient"], out["keller_image_coefficient_ci"] = r(ie), r(ici)
        out["keller_image_p_one_sided"] = kp
    # described: awareness's correlation with the ranking within category and name length together, since 31 of the
    # 63 real names are one token
    if "awareness" in S:
        tok = {x["brand"]: x["tokens"] for x in score_rows if x["score"] == "awareness_holdout" and x["name_kind"] == "real"}
        if tok:
            cat_tok = {u: f"{cat[u]}|{tok.get(U[u]['brand'])}" for u in us}
            sub_aw = [u for u in us if u in S["awareness"][0] and U[u]["brand"] in tok]
            sc["awareness"]["correlation_within_name_length"] = r(cross_half(sub_aw, S["awareness"][:2], B, cat_tok))
    if lane1_equity:
        sub = [u for u in us if U[u]["brand"] in lane1_equity]
        out["lane1_equity_correlation"] = r(within_corr([Bfull[u] for u in sub], [lane1_equity[U[u]["brand"]] for u in sub],
                                                        [cat[u] for u in sub]))
    return out


def question5_holm(models, power):
    """The four primary tests (image and awareness on the two Gemma models), Holm over the four; a test holds if its
    adjusted p is below 0.05, its score is measured and its control passes, and the ranking has power."""
    tests = [(k, s) for k in GEMMA_NAMES if k in models for s in ("image", "awareness") if s in models[k]["scores"]]
    ps = [models[k]["scores"][s]["p_one_sided"] if models[k]["scores"][s]["p_one_sided"] is not None else 1.0
          for k, s in tests]
    adj = holm(ps) if ps else []
    holds = {}
    for (k, s), a in zip(tests, adj):
        sc = models[k]["scores"][s]
        sc["p_holm"] = a
        # without power the test is not read: None, not False (22 November 2026, 8:43 AM)
        sc["holds"] = bool(a < 0.05 and sc["measured"] and sc.get("control")) if power else None
        holds[f"{k}|{s}"] = sc["holds"]
    return {"tests": [f"{k}|{s}" for k, s in tests], "holds": holds, "ranking_has_power": bool(power)}


def words_q5(top, models):
    if not top["ranking_has_power"]:
        rel = (top.get("criterion") or {}).get("reliability") or {}
        sb = [v.get("spearman_brown") for v in rel.values() if v and v.get("units", 0) >= 30
              and v.get("spearman_brown") is not None]
        best = f"{max(sb):.2f}" if sb else "unknown"
        return ("The brand-by-brand read is reported in the web appendix, with each score's reliability: the "
                f"behavioral ranking's split-half reliability, {best}, is below the plan's 0.5, so its test has no power "
                "on these tables.")
    img = [k for k in GEMMA_NAMES if top["holds"].get(f"{k}|image")]
    aw = [k for k in GEMMA_NAMES if top["holds"].get(f"{k}|awareness")]
    present = [k for k in GEMMA_NAMES if k in models]
    names = lambda ks: "" if set(ks) == set(present) else f" (in {' and '.join(GEMMA_NAMES[k] for k in ks)})"  # noqa: E731
    s1 = ("Brands whose names move a product further in the direction of better listed reliability are the brands that "
          "the model favors more")
    s2 = ("The brands that the model favors more are the brands whose names the model represents more strongly as "
          "known")
    if img and aw:
        ps = [models[k].get("keller_image_p_one_sided") for k in img if k in aw]
        adds = any(p is not None and p < 0.05 for p in ps)
        return (f"{s1}{names(img)}. {s2}{names(aw)}. In the regression on both, image "
                f"{'adds to awareness' if adds else 'adds nothing beyond awareness'}.")
    if img:
        return f"{s1}{names(img)}."
    if aw:
        return f"{s2}, not those it reads as more reliable{names(aw)}."
    return "The brand-by-brand read is reported in the web appendix, with each score's reliability."


def middle_layer(stored):
    """Amendment 5's layer (PLAN.md, change of about 6:00 PM on 21 November): the stored layer nearest half the
    model's depth, the deeper one on a tie; the depth is the last stored layer, which is the model's last layer. It uses
    no data: in the pilot the probe's accuracy was 1.0 at nearly every layer, and accuracy and separation were both
    largest at the first stored layer, where the close token holds the listed words."""
    stored = sorted(int(x) for x in stored)
    half = stored[-1] / 2
    return min(stored, key=lambda li: (abs(li - half), -li))


def question8(models, change_by_model, pairs, perms=FLIPS, seed=SEED):
    """Amendment 5: for each model, at the stored layer nearest half its depth (middle_layer), the name pairs' share of
    the reliability pairs' distance, with the reliability probe's held-out accuracy there as the gate, and Spearman's
    correlation over the measured models with the change in the gap when the information is supplied (predicted
    negative; one-sided permutation p). models: {key: (Z, B)}."""
    rows = {}
    missing = sorted(k for k in models if k not in change_by_model)
    if missing:
        raise SystemExit(f"question 8: no change in the gap for {missing} in the open models' numbers; a model left out "
                         "would change the test without a word")
    for key, (Z, B) in sorted(models.items()):
        curve = reliability_curve(pairs, Z["proj"], Z["layers"], Z["spans"], Z["dirs"])
        layer = middle_layer(Z["layers"])
        q1 = question1(pairs, Z["proj"], Z["layers"], Z["spans"], Z["dirs"], layer)["rel"]
        stored = B.get("reliability_probe_curve")
        rows[key] = {"layer": layer, "probe_accuracy": r(curve[layer]), "measured": curve[layer] >= 0.75,
                     "probe_accuracy_by_layer": {int(k): r(v) for k, v in curve.items()},
                     "alignment": q1["share_of_distance"], "alignment_ci": q1["share_of_distance_ci"],
                     "change_with_information": change_by_model.get(key),
                     "stored_curve_agrees": (None if stored is None else
                                             bool(all(abs(stored[str(li)] - v) < 1e-6 for li, v in curve.items()
                                                      if str(li) in stored)))}
    keys = [k for k, v in rows.items() if v["measured"] and v["alignment"] is not None
            and v["change_with_information"] is not None]
    out = {"models": rows, "measured": keys}
    if len(keys) >= 3:
        x = [rows[k]["alignment"] for k in keys]
        y = [rows[k]["change_with_information"] for k in keys]
        rho = spearman(x, y)
        rng = np.random.default_rng(seed)
        null = np.array([spearman(x, rng.permutation(y)) for _ in range(perms)])
        p = float((1 + (null <= rho).sum()) / (1 + perms))
        out.update({"spearman": r(rho), "p_one_sided": p, "supported": bool(rho < 0 and p < 0.05)})
    else:
        out.update({"spearman": None, "p_one_sided": None, "supported": False})
    return out


def words_q8(q):
    if q is None:
        return None
    n = len(q["measured"])
    if q["supported"]:
        return (f"In the open models, the more a familiar name moves the product along the direction of better listed "
                f"reliability, the more the listed information shrinks the gap (Spearman {q['spearman']:.2f} over {n} "
                f"models, a weak test).")
    return ("The alignment does not follow the models' response to the information; the difference between the models "
            "lies after the representation that this step reads.")


def kept(C):
    acc = defaultdict(list)
    for x in C:
        if x["role"] == "push" and x.get("kept") is not None:
            acc[(x["layer"], x["dir"] == "name", abs(x["alpha"]))].append((x["kept"], x["kept_cos"]))
    return {f"layer {k[0]} {'name' if k[1] else 'random'} size {k[2]:g}": {"length": r(np.mean([v[0] for v in vs])),
                                                                          "cosine": r(np.mean([v[1] for v in vs]))}
            for k, vs in sorted(acc.items())}


# ---------------------------------------------------------------- one model, then the report

def find(name, *folders):
    """The first of the folders that holds the file (a full run that reused a separate read stage keeps the read
    stage's CALIBRATION.json and A.jsonl.gz in that job's folder: 11881 and 12092 reused 11875's)."""
    for f in folders:
        if f and os.path.exists(os.path.join(f, name)):
            return os.path.join(f, name)
    raise SystemExit(f"{name} is in none of {[f for f in folders if f]}")


def analyze_model(back, pairs, read=None):
    Z = np.load(os.path.join(back, "proj.npz"))
    if Z["proj"].shape[0] != len(pairs):
        raise SystemExit(f"{back}: proj.npz holds {Z['proj'].shape[0]} pairs, the pairs file {len(pairs)}")
    B = json.load(open(os.path.join(back, "B.json")))
    C = jl(os.path.join(back, "C.jsonl.gz"))
    P = jl(os.path.join(back, "P.jsonl.gz"))
    layer = B["primary_layer"]
    res = {"primary_layer": layer, "secondary_layers": B["secondary_layers"],
           "calibration": json.load(open(find("CALIBRATION.json", back, read))),
           "patch": patch_summary(P),
           "q1": question1(pairs, Z["proj"], Z["layers"], Z["spans"], Z["dirs"], layer),
           "q2": question2(C, layer), "q3": question3(C, layer), "push_kept": kept(C),
           "noise_floor": {"pushes": noise_floor(C, "dup", "base"), "patch": noise_floor(P, "dup_b", "base_b")},
           "secondary": {}}
    for li in B["secondary_layers"]:
        D, _ = pushes(C, li, 0)
        res["secondary"][li] = {t: {"name_symmetric": r(boot(sym(D, t, "name"))[0]),
                                    "random_symmetric": [r(boot(sym(D, t, k))[0]) for k in RANDOM]}
                                for t in ("best", "familiar")}
    npath = os.path.join(back, "N.jsonl.gz")
    if os.path.exists(npath):
        N = jl(npath)
        res["q4"] = question4(N)
        res["noise_floor"]["copies"] = noise_floor(N, "dup_b", "base_b")
    return res


SENT = {
    (True, True): "A familiar name moves the product's representation in the direction that a better listed warranty "
                  "and failure rate move it, and pushing a product with an invented name in that direction makes the "
                  "model recommend it more.",
}


def words(m):
    q1s, q1r, q2 = m["q1"]["spec0"]["supported"], m["q1"]["rel"]["supported"], m["q2"]["supported"]
    if q1r and q2:
        s = SENT[(True, True)]
    elif q1s and q2:
        s = SENT[(True, True)].replace("a better listed warranty and failure rate move it", "better listed specifications move it")
    elif (q1s or q1r) and not q2:
        s = "The representation sentence only; the pushes moved the recommendation no more than random pushes did."
    elif q2:
        s = ("A push along the change that a familiar name causes moves the recommendation, but that change is not "
             "aligned with better listed specifications or reliability.")
    else:
        s = "Step 4 of the story is dropped from the main text; the web appendix reports the tests as failed."
    if q2 and not m["q2"]["recommend_wording_at_size_1"]:
        # PLAN.md change of about midnight: log-odds moved but the probability did not, at the name's average size.
        # The clause that says the push makes the model recommend more is replaced, not kept beside the caveat (it was
        # kept until 21 November, about 7:35 PM, when the 31B's result showed the two contradicting each other).
        s = (s.replace("makes the model recommend it more", "raises the model's preference for it")
              .replace("moves the recommendation, but", "moves the model's preference, but"))
        larger = [x for x in m["q2"]["probability_sizes_that_hold"] if x != "1.0"]
        s += (" At the average size of the name's change, the push changed the model's preference for the product "
              "without changing its recommendation" + (f"; at {float(larger[0]):g} times that size it changed the "
                                                       "recommendation as well." if larger else "."))
    allowed = any(m["q1"][d]["quality_wording_allowed"] for d in ("spec0", "rel") if m["q1"][d]["supported"])
    if (q1s or q1r) and not allowed:
        s += " The word quality is replaced by the products that the model recommends more."
    if m["q3"]["smaller_with_information"]:
        s += (" The same push changes the recommendation less when every product lists its warranty, failure rate "
              "and time on the market.")
    return s


def words_q4(m):
    """PLAN.md, amendment 1's rows of the table of sentences."""
    if "q4" not in m:
        return None
    q4, q2 = m["q4"]["supported"], m["q2"]["supported"]
    if q4 and q2:
        return ("Writing a familiar name's internal state into an invented name's tokens makes the model recommend the "
                "product more, and the reverse makes it recommend the product less; a push along the average change "
                "that a familiar name causes moves the recommendation the same way.")
    if q4:
        return ("The recommendation follows the internal state at the name's own tokens, but adding the average change "
                "that a familiar name causes to the product's other tokens moves it no more than a random push.")
    if q2:
        return "The question-2 sentence, with the copy of the name's state reported as failed."
    return "The copy and the pushes are reported as failed, in the web appendix."


def amend(models, runs, a):
    """Questions 6, 9 and 10 for each model whose back folders are given; each needs the model's full run (--run)."""
    for opt, q in (("erase", "q6"), ("knock", "q9"), ("risk", "q10")):
        for spec in getattr(a, opt):
            key, folder = spec.split("=", 1)
            if key not in runs:
                raise SystemExit(f"--{opt} {key}: the model's full run (--run {key}=...) is needed as well")
            m, full = models[key], runs[key]
            P = jl(os.path.join(full, "P.jsonl.gz")) if os.path.exists(os.path.join(full, "P.jsonl.gz")) else None
            if opt == "erase":
                m[q] = question6(jl(os.path.join(folder, "E.jsonl.gz")), json.load(open(os.path.join(folder, "MANIP.json"))),
                                 m["primary_layer"], P)
                m["sentence_q6"] = words_q6(m[q])
            elif opt == "knock":
                W = json.load(open(os.path.join(folder, "WINDOWS.json")))["windows"]
                m[q] = question9(jl(os.path.join(folder, "K.jsonl.gz")), W, P, m["primary_layer"])
                m["sentence_q9"] = words_q9(m[q])
            else:
                V = json.load(open(os.path.join(folder, "VALIDATION.json")))
                rp = os.path.join(folder, "RP.jsonl.gz")
                rd = os.path.join(folder, "RISK_DIRS.json")
                m[q] = question10(jl(rp) if os.path.exists(rp) else [], V,
                                  json.load(open(rd)) if os.path.exists(rd) else None)
                m["sentence_q10"] = words_q10(m[q])
    for spec in getattr(a, "weights", []):
        key, folder = spec.split("=", 1)
        if key not in models:
            models[key] = {}
        ans = defaultdict(dict)
        root = os.path.join(folder, "answers")
        for e in sorted(os.listdir(root)):
            for f in sorted(os.listdir(os.path.join(root, e))):
                if f.endswith(".jsonl.gz"):
                    ans[e][f[:-len(".jsonl.gz")]] = jl(os.path.join(root, e, f))
        cp = os.path.join(folder, "EDIT_CHECK.json")
        models[key]["q7"] = question7(dict(ans), dom2_tables(a), parser(), json.load(open(cp)) if os.path.exists(cp) else None)
        models[key]["sentence_q7"] = words_q7(models[key]["q7"])


def brands(models, runs, a, draws=DRAWS, perms=FLIPS):
    """Question 5 for each model whose brand read is given (--brands), the ranking's candidate chosen once, on Gemma 4
    31B's full read (or the first model's, if the 31B's is not given), and used for every model."""
    specs = dict(spec.split("=", 1) for spec in getattr(a, "brands", []))
    if not specs:
        return None
    import csv
    import brand_criterion as BC
    rend = jl(a.renderings)
    beh, beh_all = {}, {}
    for key in specs:
        if key not in runs:
            raise SystemExit(f"--brands {key}: the model's full run (--run {key}=...) is needed as well")
        A = {x["id"]: x for x in jl(find("A.jsonl.gz", runs[key], getattr(a, "reads", {}).get(key)))}
        beh[key] = BC.behavior_rows(A, rend)
        beh_all[key] = BC.behavior_rows(A, rend, infos=(0, 1))     # exploratory, for the web appendix
    ref = "gemma31b" if "gemma31b" in beh else sorted(beh)[0]
    crit = BC.summary(beh[ref])
    kind = crit["chosen"] or "own"
    eq = list(csv.DictReader(open(a.brand_equity, encoding="utf8")))
    log_freq = {x["brand"]: float(x["log_freq_name_alone"]) for x in eq if x.get("log_freq_name_alone") not in ("", None)}
    lane1 = defaultdict(dict)
    if os.path.exists(a.brand_model_equity):
        for x in csv.DictReader(open(a.brand_model_equity, encoding="utf8")):
            if x["source"] == "open" and x["equity"] not in ("", None):
                lane1[x["model"]][x["brand"]] = float(x["equity"])
    q5 = {}
    for key, folder in specs.items():
        extras = json.load(open(os.path.join(folder, "brands_scores.json")))
        cl = json.load(open(os.path.join(folder, "COPY_LAYER.json"))).get("copy_layer") \
            if os.path.exists(os.path.join(folder, "COPY_LAYER.json")) else None
        probe = (models.get(key, {}).get("q1") or {}).get("rel", {}).get("probe_held_out_accuracy")
        q5[key] = question5(beh[key], kind, jl(os.path.join(folder, "brand_rows.jsonl.gz")), extras, cl, probe, log_freq,
                            lane1.get(key), draws=draws, perms=perms)
        models.setdefault(key, {})["q5"] = q5[key]
    top = question5_holm(q5, crit["chosen"] is not None)
    top["criterion"] = {k: v for k, v in crit.items() if k not in ("own", "on_best")}
    top["criterion"]["reliability"] = {k: crit[k]["split_half"] for k in ("own", "on_best")}
    top["criterion"]["chosen_on"] = ref
    # exploratory, added after reading the results (22 November 2026, 8:43 AM):
    # the ranking's reliability with all of a brand's items, both information cells; the plan's reading stays on the
    # items without the information
    top["exploratory_all_items"] = {
        "note": "exploratory, added after reading; the plan's ranking reads the items without the information",
        "reliability": {key: {k: BC.summary(rows)[k]["split_half"] for k in ("own", "on_best")}
                        for key, rows in beh_all.items()}}
    top["sentence"] = words_q5(top, q5)
    return top


def parser():
    """Study 2's answer parser (its file is beside this one in the bundle, and in jmr-2026/study2 in the repository)."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (here, os.path.join(here, "..", "study2")):
        if os.path.exists(os.path.join(p, "parse_answer.py")) and p not in sys.path:
            sys.path.insert(0, os.path.abspath(p))
    from parse_answer import pick
    return pick


def dom2_tables(a):
    """Study 1's names of the 30 dom2 tables (dom2's own names end in _dom)."""
    path = getattr(a, "dom2_items", None) or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "study2",
                                                           "items", "dom2", "items.jsonl")
    return {t[:-len("_dom")] if t.endswith("_dom") else t for t in {x["table"] for x in jl(path)}}


def panel(runs, a, pairs):
    """Question 8 over the Gemma models' full runs and the panel's read runs."""
    folders = dict(runs)
    folders.update(dict(spec.split("=", 1) for spec in getattr(a, "panel", [])))
    if len(folders) < 3:
        return None
    nums = json.load(open(a.open_numbers))
    change = nums["study2"]["b2/dom2"]["change"]["by_model"]
    models = {k: (np.load(os.path.join(f, "proj.npz")), json.load(open(os.path.join(f, "B.json"))))
              for k, f in folders.items()}
    return question8(models, change, pairs)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--run", action="append", required=True, help="model_key=back folder")
    ap.add_argument("--read", action="append", default=[],
                    help="model_key=the read stage's back folder, when the full run reused a separate read stage")
    ap.add_argument("--erase", action="append", default=[], help="model_key=run_erase.py's back folder (question 6)")
    ap.add_argument("--knock", action="append", default=[], help="model_key=run_knock.py's back folder (question 9)")
    ap.add_argument("--risk", action="append", default=[], help="model_key=run_risk.py's back folder (question 10)")
    ap.add_argument("--weights", action="append", default=[], help="model_key=run_weights.py's back folder (question 7)")
    ap.add_argument("--panel", action="append", default=[], help="model_key=a panel model's read run (question 8)")
    ap.add_argument("--open-numbers", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                           "open-models", "numbers.json"))
    ap.add_argument("--dom2-items", default="")
    ap.add_argument("--brands", action="append", default=[], help="model_key=run_brands.py's back folder (question 5)")
    ap.add_argument("--renderings", default="", help="the full build's renderings.jsonl (question 5's ranking)")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--brand-equity", default=os.path.join(here, "..", "results", "brand-level", "brand_equity.csv"))
    ap.add_argument("--brand-model-equity", default=os.path.join(here, "..", "results", "brand-level",
                                                                 "brand_model_equity.csv"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    pairs = jl(a.pairs)
    out = {"plan": "jmr-2026/mechanism/PLAN.md", "draws": DRAWS, "flips": FLIPS, "seed": SEED,
           "pairs_sha256": hashlib.sha256(open(a.pairs, "rb").read()).hexdigest(), "models": {}}
    runs = dict(spec.split("=", 1) for spec in a.run)
    a.reads = dict(spec.split("=", 1) for spec in a.read)
    for key, back in runs.items():
        out["models"][key] = analyze_model(back, pairs, a.reads.get(key))
        out["models"][key]["sentence"] = words(out["models"][key])
        out["models"][key]["sentence_q4"] = words_q4(out["models"][key])
    amend(out["models"], runs, a)
    out["q8"] = panel(runs, a, pairs)
    out["sentence_q8"] = words_q8(out["q8"])
    out["q5"] = brands(out["models"], runs, a)
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "numbers.json"), "w"), indent=1)
    print(json.dumps({k: {"q1_spec": v["q1"]["spec0"]["supported"], "q1_rel": v["q1"]["rel"]["supported"],
                          "q2": v["q2"]["supported"], "q3": v["q3"]["smaller_with_information"],
                          "sentence": v["sentence"]} for k, v in out["models"].items() if "q1" in v}, indent=1))
    return out


if __name__ == "__main__":
    main()
