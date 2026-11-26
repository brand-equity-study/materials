"""How the models differ (how-the-models-differed/materials/analysis_plan.md): one test's per-model estimates in, the
spread between models and the same six moderators out.

    python how-the-models-differed/code/heterogeneity.py --study study1b --label "Study 1b, the brand gap" \\
        --input study1b-64-models-on-34-tables/results/pooled/per_model.csv --model-col model --est-col gap_pp \\
        --low-col ci95_low_pp --high-col ci95_high_pp --direction 1 --units points
    python how-the-models-differed/code/heterogeneity.py --selftest

The eight runs that the paper reports are steps of run_all.py, with their options. The input is a CSV with one row
per model: the model key (as in models/model_characteristics.csv), the estimate, and its standard
error (--se-col) or its 95 per cent interval (--low-col, --high-col; the standard error is the interval's width divided
by 3.92). The random-effects model and the meta-regressions estimate tau-squared by restricted maximum likelihood
(REML), and test a coefficient with a z test; I-squared is Higgins and Thompson's tau2 / (tau2 + s2), with s2 the
typical within-model variance; the prediction interval is that of Higgins, Thompson and Spiegelhalter (2009).
DerSimonian and Laird's and Paule and Mandel's estimates of tau are reported beside it as checks (DerSimonian and
Laird's was the main estimate in the plan's first version, and the plan gives the reason for the change). Writes
how-the-models-differed/results/<study>/numbers.json and rewrites how-the-models-differed/results/SUMMARY.md.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # the package
CHARS = os.path.join(ROOT, "models", "model_characteristics.csv")
OUT = os.path.join(ROOT, "how-the-models-differed", "results")
MODERATORS = ("chat-tuned against base", "size (log10 total parameters)", "release date (years)",
              "open against closed weights", "reasoning on against off", "developer")


# ---------------------------------------------------------------- the random-effects model

def dl(y, v, X):
    """DerSimonian-Laird random-effects (meta-)regression: coefficients, their covariance, tau2, Q and its df."""
    w = 1.0 / v
    A = np.linalg.inv((X.T * w) @ X)
    b_fe = A @ ((X.T * w) @ y)
    q = float((w * (y - X @ b_fe) ** 2).sum())
    k, p = X.shape
    dfree = k - p
    c = float(w.sum() - np.trace(A @ ((X.T * w ** 2) @ X)))
    tau2 = max(0.0, (q - dfree) / c) if c > 0 else 0.0
    ws = 1.0 / (v + tau2)
    cov = np.linalg.inv((X.T * ws) @ X)
    beta = cov @ ((X.T * ws) @ y)
    return beta, cov, tau2, q, dfree


def reml(y, v, X):
    """Random-effects (meta-)regression with tau2 by restricted maximum likelihood: coefficients, their covariance, tau2.
    The restricted log-likelihood is maximized over tau2 >= 0 (bounded search, and the bound tau2 = 0 compared)."""
    from scipy import optimize

    def fit(t2):
        w = 1.0 / (v + t2)
        info = (X.T * w) @ X
        cov = np.linalg.inv(info)
        beta = cov @ ((X.T * w) @ y)
        r = y - X @ beta
        nll = 0.5 * (np.log(v + t2).sum() + np.linalg.slogdet(info)[1] + float((w * r ** 2).sum()))
        return nll, beta, cov

    upper = 10.0 * (float(np.var(y)) + float(v.max())) + 1.0
    res = optimize.minimize_scalar(lambda t: fit(t)[0], bounds=(0.0, upper), method="bounded",
                                   options={"xatol": 1e-10 * upper})
    t2 = float(res.x) if fit(float(res.x))[0] < fit(0.0)[0] else 0.0
    _, beta, cov = fit(t2)
    return beta, cov, t2


def paule_mandel(y, v):
    """Paule and Mandel's tau2 for the model with an intercept only (a check beside REML)."""
    from scipy import optimize

    def f(t2):
        w = 1.0 / (v + t2)
        mu = (w * y).sum() / w.sum()
        return float((w * (y - mu) ** 2).sum()) - (len(y) - 1)
    if f(0.0) <= 0:
        return 0.0
    return float(optimize.brentq(f, 0.0, 100.0 * (float(np.var(y)) + float(v.max())) + 1.0))


def typical_within(v):
    """Higgins and Thompson's typical within-study variance, for I-squared = tau2 / (tau2 + s2)."""
    w = 1.0 / v
    k = len(v)
    return (k - 1) * w.sum() / (w.sum() ** 2 - (w ** 2).sum())


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


# ---------------------------------------------------------------- moderators

def moderator_values(keys, chars):
    """{moderator: list of values per model (None when unknown)}; developer is a string, the others numbers."""
    def num(k, f):
        r = chars.get(k)
        try:
            return f(r) if r else None
        except (ValueError, KeyError, TypeError):
            return None

    def reasoning(r):
        t = (r.get("thinking") or "").lower()
        key = r["key"].lower()
        if t == "on" or key.endswith("-thinking"):
            return 1.0
        if t == "off" or '"enable_thinking": false' in t:
            return 0.0
        return None

    def years(r):
        d = r["release_date"]
        return int(d[:4]) + (int(d[5:7]) - 0.5) / 12 if d else None

    return {
        "chat-tuned against base": [num(k, lambda r: 1.0 if r["base_or_chat"] == "chat" else 0.0 if r["base_or_chat"] == "base" else None) for k in keys],
        "size (log10 total parameters)": [num(k, lambda r: math.log10(float(r["params_total"])) if r.get("params_total") else None) for k in keys],
        "release date (years)": [num(k, years) for k in keys],
        "open against closed weights": [num(k, lambda r: 1.0 if r["open"] == "open" else 0.0) for k in keys],
        "reasoning on against off": [num(k, reasoning) for k in keys],
        "developer": [(chars[k]["developer"] or None) if k in chars else None for k in keys],
    }


def fit_moderator(name, vals, y, v):
    keep = [i for i, x in enumerate(vals) if x is not None]
    if name == "developer":
        devs = sorted({vals[i] for i in keep})
        counts = {d: sum(vals[i] == d for i in keep) for d in devs}
        devs = [d for d in devs if counts[d] >= 1]
        if len(devs) < 2:
            return {"estimable": False, "reason": "one developer"}
        X = np.column_stack([np.ones(len(keep))] + [[1.0 if vals[i] == d else 0.0 for i in keep] for d in devs[1:]])
        beta, cov, tau2 = reml(y[keep], v[keep], X)
        bd, cd = beta[1:], cov[1:, 1:]
        chi2 = float(bd @ np.linalg.solve(cd, bd))
        return {"estimable": True, "models": len(keep), "developers": len(devs), "wald_chi2": round(chi2, 3),
                "df": len(devs) - 1, "p_two_sided": float(stats.chi2.sf(chi2, len(devs) - 1)), "residual_tau": round(math.sqrt(tau2), 4),
                "models_by_developer": counts}
    x = np.array([vals[i] for i in keep], float)
    distinct = sorted(set(x))
    if len(distinct) < 2:
        return {"estimable": False, "reason": "one value" if keep else "no model has a value"}
    if len(distinct) == 2 and min(int((x == d).sum()) for d in distinct) < 3:
        return {"estimable": False, "reason": "fewer than three models have one of the two values"}
    if len(keep) < 4:
        return {"estimable": False, "reason": "fewer than four models have a value"}
    X = np.column_stack([np.ones(len(keep)), x])
    beta, cov, tau2 = reml(y[keep], v[keep], X)
    se = math.sqrt(cov[1, 1])
    z = beta[1] / se
    return {"estimable": True, "models": len(keep), "coefficient": round(float(beta[1]), 4),
            "ci95": [round(float(beta[1] - 1.96 * se), 4), round(float(beta[1] + 1.96 * se), 4)],
            "p_two_sided": float(2 * stats.norm.sf(abs(z))), "residual_tau": round(math.sqrt(tau2), 4)}


# ---------------------------------------------------------------- one study

def analyze(keys, y, se, lows, highs, chars, direction):
    y, se = np.asarray(y, float), np.asarray(se, float)
    v = se ** 2
    k = len(y)
    _, _, tau2_dl, q, dfree = dl(y, v, np.ones((k, 1)))          # Q and its test, and DerSimonian-Laird's tau2
    beta, cov, tau2 = reml(y, v, np.ones((k, 1)))
    mu, se_mu = float(beta[0]), float(math.sqrt(cov[0, 0]))
    i2 = tau2 / (tau2 + typical_within(v)) if k > 1 else 0.0
    t = stats.t.ppf(0.975, k - 2) if k > 2 else float("nan")
    half = t * math.sqrt(tau2 + se_mu ** 2)
    if lows is None:
        lows, highs = y - 1.96 * se, y + 1.96 * se
    excl = sum(1 for lo, hi in zip(lows, highs) if lo > 0 or hi < 0)
    two_sided = direction == 0   # a study whose plan predicts no direction: only the counts above and below zero
    res = {"models": k,
           "predicted_direction": "none (two-sided)" if two_sided else direction,
           "share_in_predicted_direction": None if two_sided else round(float(np.mean(np.sign(y) == direction)), 4),
           "models_in_predicted_direction": None if two_sided else int((np.sign(y) == direction).sum()),
           "models_above_zero": int((y > 0).sum()), "models_below_zero": int((y < 0).sum()),
           "share_interval_excludes_zero": round(excl / k, 4), "models_interval_excludes_zero": excl,
           "random_effects": {"estimate": round(mu, 4), "ci95": [round(mu - 1.96 * se_mu, 4), round(mu + 1.96 * se_mu, 4)],
                              "p_two_sided": float(2 * stats.norm.sf(abs(mu / se_mu))), "tau": round(math.sqrt(tau2), 4),
                              "tau2": round(tau2, 4), "i2": round(i2, 4), "q": round(q, 3), "df": dfree,
                              "q_p_value": float(stats.chi2.sf(q, dfree)) if dfree > 0 else None,
                              "prediction_interval_95": [round(mu - half, 4), round(mu + half, 4)],
                              "tau_estimator": "REML",
                              "checks": {"tau_dersimonian_laird": round(math.sqrt(tau2_dl), 4),
                                         "tau_paule_mandel": round(math.sqrt(paule_mandel(y, v)), 4)}},
           "models_without_characteristics": [kk for kk in keys if kk not in chars]}
    vals = moderator_values(keys, chars)
    mods = {name: fit_moderator(name, vals[name], y, v) for name in MODERATORS}
    est = [n for n in MODERATORS if mods[n].get("estimable")]
    for n, h in zip(est, holm([mods[n]["p_two_sided"] for n in est])):
        mods[n]["holm"] = h
    res["moderators"] = mods
    return res


def read_input(a):
    """The rows that every --filter column=value matches; estimates, errors and bounds multiplied by --scale (for
    example 100, to turn proportions into percentage points)."""
    rows = list(csv.DictReader(open(a.input, encoding="utf8")))
    for f in a.filter or []:
        col, val = f.split("=", 1)
        rows = [r for r in rows if r[col] == val]
    if not rows:
        raise SystemExit(f"refused: no row matches {a.filter}")
    # a row whose study gives no estimate (for example the audit's slopes that rest on fewer than three tables) is left
    # out and named with the study's reason (--reason-col)
    a.not_estimable = [{"model": r[a.model_col], "reason": r.get(a.reason_col or "", "") or "no estimate in the file"}
                       for r in rows if r[a.est_col] in ("", None)]
    rows = [r for r in rows if r[a.est_col] not in ("", None)]
    keys = [r[a.model_col] for r in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("refused: a model appears in more than one row; add a --filter")
    # the models whose study marks their measure as reliable (every --reliability-col at least --reliability-min, where
    # the column has a value), for a check beside the main run
    a.reliable = [all(r[c] in ("", None) or float(r[c]) >= a.reliability_min for c in (a.reliability_col or [])) for r in rows]
    s = a.scale
    y = [s * float(r[a.est_col]) for r in rows]
    if a.se_col:
        se = [s * float(r[a.se_col]) for r in rows]
        if a.low_col and a.high_col:
            lows = [s * float(r[a.low_col]) for r in rows]
            highs = [s * float(r[a.high_col]) for r in rows]
        else:
            lows = highs = None
    else:
        lows = [s * float(r[a.low_col]) for r in rows]
        highs = [s * float(r[a.high_col]) for r in rows]
        se = [(h - lo) / 3.92 for lo, h in zip(lows, highs)]
    return keys, y, se, lows, highs


ZERO_WIDTH = 1e-9


def drop_zero_width(keys, y, se, lows, highs, reliable):
    """Leave out the models whose standard error is zero (an interval of zero width: every bootstrap draw gave the same
    estimate, so the study measured no sampling error for that model and it cannot get an inverse-variance weight).
    Added 21 November 2026, about 8:00 PM Central, after two such rows were found in the audit's per-model file (Qwen 3 32B on
    test 2's recognition, Gemma 3 27B on test 2's tone). Returns the kept columns and the models left out."""
    keep = [i for i, s in enumerate(se) if s > ZERO_WIDTH]
    out = [keys[i] for i in range(len(keys)) if i not in keep]
    pick = lambda v: None if v is None else [v[i] for i in keep]
    return pick(keys), pick(y), pick(se), pick(lows), pick(highs), pick(reliable), out


def summary():
    rows = []
    for study in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
        path = os.path.join(OUT, study, "numbers.json")
        if os.path.exists(path):
            d = json.load(open(path, encoding="utf8"))
            if "result" in d:   # the predictors' results share this folder
                rows.append(d)
    lines = ["# Model heterogeneity across the studies", "",
             "Generated by `how-the-models-differed/code/heterogeneity.py` from `how-the-models-differed/results/<study>/numbers.json`;",
             "the analysis is described in `how-the-models-differed/materials/analysis_plan.md`.", "",
             "The estimate over models below comes from a random-effects model that treats the models as independent; every",
             "model of a study answered the same tables, so its interval is too narrow, and the effect over models is the",
             "study's own two-way bootstrap estimate. The columns here are for the spread between models.", "",
             "| Study | Units | Models | In the predicted direction | Interval excludes zero | Estimate over models (95% CI) | Tau | I-squared | Q (df; P) | 95% prediction interval for a new model | Moderators with a Holm P below 0.05 |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for n in rows:
        r = n["result"]
        re_ = r["random_effects"]
        sig = [f"{m} (Holm P {v['holm']:.3f})" for m, v in r["moderators"].items() if v.get("estimable") and v.get("holm", 1) < 0.05]
        ind = r["models_in_predicted_direction"]
        ind = f"two-sided ({r.get('models_above_zero')} above zero)" if ind is None else ind
        lines.append(f"| {n['label']} | {n['units']} | {r['models']} | {ind} | "
                     f"{r['models_interval_excludes_zero']} | {re_['estimate']:.2f} ({re_['ci95'][0]:.2f} to {re_['ci95'][1]:.2f}) | "
                     f"{re_['tau']:.2f} | {100 * re_['i2']:.0f}% | {re_['q']:.1f} ({re_['df']}; "
                     f"{'< 0.0001' if (re_.get('q_p_value') or 0) < 0.0001 else format(re_['q_p_value'], '.4f')}) | "
                     f"{re_['prediction_interval_95'][0]:.2f} to "
                     f"{re_['prediction_interval_95'][1]:.2f} | {'; '.join(sig) if sig else 'none'} |")
    left = [(n["study"], n["result"]["models_left_out_interval_of_zero_width"]) for n in rows
            if n["result"].get("models_left_out_interval_of_zero_width")]
    if left:
        lines += ["", "Models left out of a study because their interval has zero width (no sampling error was measured for them): "
                  + "; ".join(f"{s}: {', '.join(m)}" for s, m in left) + "."]
    blank = [(n["study"], n["result"]["models_left_out_not_estimable"]) for n in rows
             if n["result"].get("models_left_out_not_estimable")]
    if blank:
        lines += ["", "Models left out of a study because the study gives no estimate for them (the study's reason in "
                  "each numbers.json): " + "; ".join(f"{s}: {', '.join(m['model'] for m in ms)}" for s, ms in blank) + "."]
    checks = [n for n in rows if n["result"].get("check_reliable_models_only", {}).get("random_effects")]
    if checks:
        lines += ["", "## Check: only the models whose measures the study marks as reliable", "",
                  "| Study | Rule | Models | In the predicted direction | Tau | I-squared | 95% prediction interval for a new model |",
                  "|---|---|---:|---:|---:|---:|---:|"]
        for n in checks:
            c = n["result"]["check_reliable_models_only"]
            ind = c["models_in_predicted_direction"]
            ind = f"two-sided ({c['models_above_zero']} above zero)" if ind is None else ind
            ce = c["random_effects"]
            lines.append(f"| {n['label']} | {c['rule']} | {c['models']} | {ind} | {ce['tau']:.2f} | {100 * ce['i2']:.0f}% | "
                         f"{ce['prediction_interval_95'][0]:.2f} to {ce['prediction_interval_95'][1]:.2f} |")
    with open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- the selftest

def selftest():
    rng = np.random.default_rng(20261121)
    k = 60
    devs = ["D1", "D2", "D3", "D4"]
    chars, keys, y, se = {}, [], [], []
    tau_true, open_effect = 2.0, 4.0
    for i in range(k):
        key = f"m{i}"
        is_open = i % 2
        chars[key] = {"key": key, "base_or_chat": "chat", "params_total": str(10 ** rng.uniform(9, 11)),
                      "release_date": f"202{rng.integers(4, 7)}-{rng.integers(1, 13):02d}-15", "open": "open" if is_open else "closed",
                      "thinking": rng.choice(["on", "off"]), "developer": devs[(i // 2) % 4]}   # each developer has open and closed models
        s = rng.uniform(0.8, 1.5)
        y.append(5.0 + open_effect * is_open + rng.normal(0, tau_true) + rng.normal(0, s))
        se.append(s)
        keys.append(key)
    r = analyze(keys, y, se, None, None, chars, 1)
    spread = math.sqrt(tau_true ** 2 + open_effect ** 2 * 0.25)          # the planted spread between models
    tau = r["random_effects"]["tau"]
    mods = r["moderators"]
    planted = mods["open against closed weights"]
    others = [n for n in MODERATORS if n != "open against closed weights" and mods[n].get("estimable")]
    ok = {"tau within 20 per cent of the planted spread": abs(tau - spread) / spread < 0.20,
          "the planted moderator has a Holm P below 0.05": planted.get("holm", 1) < 0.05,
          "the planted moderator's coefficient is within 1.5 of 4": abs(planted.get("coefficient", 0) - open_effect) < 1.5,
          "no moderator that was not planted has a Holm P below 0.05": all(mods[n]["holm"] >= 0.05 for n in others),
          "chat against base is left out (one value)": not mods["chat-tuned against base"]["estimable"]}
    print(f"planted spread {spread:.2f}, estimated tau {tau:.2f}; open coefficient {planted.get('coefficient')}, "
          f"Holm P {planted.get('holm'):.4f}; others' Holm P {[round(mods[n]['holm'], 3) for n in others]}")
    for kk, v in ok.items():
        print(("PASS " if v else "FAIL ") + kk)
    return all(ok.values())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--study")
    ap.add_argument("--label")
    ap.add_argument("--input")
    ap.add_argument("--model-col", default="model")
    ap.add_argument("--est-col")
    ap.add_argument("--se-col")
    ap.add_argument("--low-col")
    ap.add_argument("--high-col")
    ap.add_argument("--direction", type=int, default=1, help="the predicted sign of the effect (1 or -1)")
    ap.add_argument("--units", default="points")
    ap.add_argument("--filter", action="append", help="column=value; only the rows that match (repeatable)")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply estimates, errors and bounds (100: proportions to points)")
    ap.add_argument("--reliability-col", action="append", help="a column of the study's reliability; adds a check on the reliable models")
    ap.add_argument("--reliability-min", type=float, default=0.5)
    ap.add_argument("--reason-col", help="the column that gives why a row has no estimate")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    chars = {r["key"]: r for r in csv.DictReader(open(CHARS, encoding="utf8"))}
    keys, y, se, lows, highs = read_input(a)
    keys, y, se, lows, highs, a.reliable, zero_width = drop_zero_width(keys, y, se, lows, highs, a.reliable)
    res = analyze(keys, y, se, lows, highs, chars, a.direction)
    res["models_left_out_interval_of_zero_width"] = zero_width
    res["models_left_out_not_estimable"] = a.not_estimable
    if a.reliability_col:
        keep = [i for i, ok in enumerate(a.reliable) if ok]
        sub = lambda v: None if v is None else [v[i] for i in keep]
        res["check_reliable_models_only"] = (
            {"rule": f"every one of {a.reliability_col} at least {a.reliability_min} where it has a value",
             "models_left_out": [keys[i] for i in range(len(keys)) if i not in keep],
             **analyze(sub(keys), sub(y), sub(se), sub(lows), sub(highs), chars, a.direction)}
            if len(keep) >= 4 else {"rule": f"at least {a.reliability_min}", "models": len(keep), "note": "fewer than four reliable models"})
    raw = open(a.input, "rb").read()
    out = {"study": a.study, "label": a.label or a.study, "units": a.units, "direction": a.direction,
           "input": {"file": os.path.relpath(a.input, ROOT).replace("\\", "/"), "sha256": hashlib.sha256(raw).hexdigest(),
                     "model_col": a.model_col, "est_col": a.est_col, "se": a.se_col or f"({a.high_col} - {a.low_col}) / 3.92",
                     "filter": a.filter or [], "scale": a.scale},
           "plan": "how-the-models-differed/materials/analysis_plan.md", "result": res,
           # every argument of the run, so that it can be run again exactly
           "args": {k: v for k, v in vars(a).items() if k not in ("reliable", "not_estimable", "selftest", "rerun")}}
    os.makedirs(os.path.join(OUT, a.study), exist_ok=True)
    with open(os.path.join(OUT, a.study, "numbers.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(out, f, indent=1)
    summary()
    re_ = res["random_effects"]
    ind = (f"two-sided, {res['models_above_zero']} above and {res['models_below_zero']} below zero"
           if res["models_in_predicted_direction"] is None else f"{res['models_in_predicted_direction']} in the predicted direction")
    print(f"{a.study}: {res['models']} models (left out, zero-width interval: {zero_width or 'none'}); {ind}; "
          f"{res['models_interval_excludes_zero']} intervals exclude zero; estimate {re_['estimate']:.2f} "
          f"({re_['ci95'][0]:.2f} to {re_['ci95'][1]:.2f}); tau {re_['tau']:.2f}; I2 {100 * re_['i2']:.0f}%; "
          f"prediction interval {re_['prediction_interval_95'][0]:.2f} to {re_['prediction_interval_95'][1]:.2f}")
    for n, m in res["moderators"].items():
        print(" ", n, {kk: m[kk] for kk in m if kk in ("estimable", "reason", "models", "coefficient", "ci95", "p_two_sided", "holm", "wald_chi2", "df")})


if __name__ == "__main__":
    main()
