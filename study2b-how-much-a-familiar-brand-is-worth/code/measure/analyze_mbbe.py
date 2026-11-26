"""for the rating arm, a column rating or
the answer text (read with the audit's rating function).

What it computes, by plan section:
  4.2  a conditional logit for each model and category on the shown sets: two dummies per attribute, the rating, log
       price centred within the category, four position and four letter dummies, a dummy for each name but one, and
       familiar names times centred log price. MBBE = a name's coefficient minus the mean of the invented names'.
  4.3  log-odds; the share premium exp(MBBE) / (exp(MBBE) + 4) - 0.20 (equal specifications, the other four products at
       the invented names' mean); the price equivalent exp(MBBE / |slope|) - 1, where slope is the name's own price slope
       (the log-price coefficient, plus the familiar-by-price term for a familiar name) and only when that slope's
       interval lies below zero; the rating equivalent in stars, only when the rating coefficient's interval lies above
       zero.
  4.4  the randomized blind gap: for each name, the share of shown sets in which its product was picked minus the share
       of the hidden twins in which the same product was picked.
  4.5  arm 4 (rating of the named product minus the unnamed version on the same profile and wording) and arm 5 (the
       focal brand's share at each premium, and the premium at which its share equals 20 per cent).
  4.6  intervals: sets resampled within category (the logit refitted in every draw).
  5    split-half reliability over the familiar names within a model (random halves of each category's sets,
       Spearman-Brown corrected), the signal share, the repeat agreement (Cohen's kappa) and, for system prompt,
       layout and request wording, the brand-by-factor variance against the brand variance (computed from separate
       fits for each level, with the squared standard errors subtracted).
  6    known groups; held-out sets (20 per cent); independence of MBBE from the profiles that a name met;
       7    the convergence table: MBBE, the randomized blind gap, the rating difference, the arm 5 premium and the corpus
       tables' blind gap (brand_model_equity.csv, the open models), pooled over brand-model cells with a two-way
       bootstrap (brands and models resampled).
  8.1  --simulate: answers drawn from a multinomial logit with known intercepts; the script must recover them
       (correlation at least 0.9; 95 per cent coverage between 90 and 98 per cent).

the new halves have a generator of their own):
the paper's exclusion rule (READ_RULE: a model whose choice answers are read in under 90 per cent is reported apart and
left out of the pooled analyses); each category's tested prices and whether each price equivalent lies inside them;
the known-groups interval of plan 6.1 (the familiar names' mean MBBE, with the new invented names against the corpus's);
the joint fit of arms 1 and 2 (plan 4.2); the MBBE of the first and the repeated sets (plan 5.3); split-half
reliabilities of the blind gap, the rating difference, the arm 5 premium and the corpus tables' gap, pooled over the
models' cells, and the correlations of plans 6.4 and 7.2 corrected for them;
"""
import argparse
import collections
import hashlib
import json
import math
import pathlib
import sys

import numpy as np
import pandas as pd

PKG = REPO = pathlib.Path(__file__).resolve().parents[3]   # the package
sys.path.insert(0, str((PKG / "common/parse_answer.py").parent))   # parse_answer.py and decline.py
sys.path.insert(0, str((PKG / "study3b-brand-knowledge-and-training-text-in-released-models/code/audit/parse_audit.py").parent))   # parse_audit.py
import gzip  # noqa: E402


def _open_text(path):
    """A text file opened for reading; the package keeps the corpus's prompt files gzipped."""
    return gzip.open(path, "rt", encoding="utf8") if str(path).endswith(".gz") else open(path, encoding="utf8")
sys.dont_write_bytecode = True
from parse_answer import final_answer, pick

SEED = 20261120
LETTERS = list("ABCDE")


# ---------------------------------------------------------------- the conditional logit

def fit_clogit(X, y, ridge=1e-6, iters=60):
    """Newton-Raphson for a conditional logit. X: sets x alternatives x terms; y: index of the chosen alternative.
    Returns (coefficients, covariance, log-likelihood)."""
    n, J, K = X.shape
    b = np.zeros(K)
    idx = np.arange(n)
    for _ in range(iters):
        u = X @ b
        u -= u.max(1, keepdims=True)
        P = np.exp(u)
        P /= P.sum(1, keepdims=True)
        xbar = np.einsum("nj,njk->nk", P, X)
        g = (X[idx, y] - xbar).sum(0) - ridge * b
        D = X - xbar[:, None, :]
        H = -np.einsum("nj,njk,njl->kl", P, D, D) - ridge * np.eye(K)
        step = np.linalg.solve(H, g)
        b = b - step
        if np.abs(step).max() < 1e-9:
            break
    u = X @ b
    m = u.max(1, keepdims=True)
    ll = float((u[idx, y] - (m[:, 0] + np.log(np.exp(u - m).sum(1)))).sum())
    cov = np.linalg.inv(-H)
    return b, cov, ll


class Design:
    """The terms of one category's logit, and the names in order (familiar first, then invented)."""

    def __init__(self, items):
        names = collections.OrderedDict()
        prices = set()
        self.status = {}
        for it in items:
            for p in it["products"].values():
                names.setdefault(p["name"], p["name_kind"])
                self.status.setdefault(p["name"], p.get("name_status", ""))
                prices.add(p["price"])
        fam = [n for n, k in names.items() if k == "familiar"]
        inv = [n for n, k in names.items() if k == "invented"]
        self.names = fam + inv
        self.familiar, self.invented = fam, inv
        self.prices = sorted(prices)
        self.ref = inv[0]
        self.name_cols = [n for n in self.names if n != self.ref]
        self.logp_centre = float(np.mean(np.log(sorted(prices))))
        self.terms = ([f"a{a}_l{l}" for a in range(3) for l in (1, 2)] + ["rating", "log_price"] + [f"pos{k}" for k in range(2, 6)]
                      + [f"letter_{L}" for L in "BCDE"] + [f"name:{n}" for n in self.name_cols] + ["familiar_x_log_price"])
        self.col = {t: i for i, t in enumerate(self.terms)}

    def row(self, letter, p, with_names=True):
        x = np.zeros(len(self.terms))
        for a, lv in enumerate(p["levels"]):
            if lv > 0:
                x[self.col[f"a{a}_l{lv}"]] = 1
        x[self.col["rating"]] = (p["rating"] - 4.4) / 0.2
        lp = math.log(p["price"]) - self.logp_centre
        x[self.col["log_price"]] = lp
        if p.get("position", 1) > 1:
            x[self.col[f"pos{p['position']}"]] = 1
        if letter != "A":
            x[self.col[f"letter_{letter}"]] = 1
        if with_names:
            if p["name"] != self.ref:
                x[self.col[f"name:{p['name']}"]] = 1
            if p["name_kind"] == "familiar":
                x[self.col["familiar_x_log_price"]] = lp
        return x

    def matrix(self, items, letters, with_names=True):
        X = np.array([[self.row(L, it["products"][L], with_names) for L in LETTERS] for it in items])
        y = np.array([LETTERS.index(L) for L in letters])
        return X, y


def mbbe_from(design, b, cov, ref=None):
    """MBBE of every name (coefficient minus the mean of the reference invented names: all of them by default, and,
    under Amendment 1, those that the model does not claim to know), its standard error, and the units."""
    ref = list(ref) if ref else list(design.invented)
    K = len(design.terms)
    out = {}
    inv_cols = [design.col.get(f"name:{n}") for n in ref]
    for n in design.names:
        c = np.zeros(K)
        if n != design.ref:
            c[design.col[f"name:{n}"]] += 1
        for ic in inv_cols:
            if ic is not None:
                c[ic] -= 1 / len(ref)
        est = float(c @ b)
        se = float(math.sqrt(max(c @ cov @ c, 0)))
        slope_c = np.zeros(K)
        slope_c[design.col["log_price"]] = 1
        if n in design.familiar:
            slope_c[design.col["familiar_x_log_price"]] = 1
        slope = float(slope_c @ b)
        slope_se = float(math.sqrt(max(slope_c @ cov @ slope_c, 0)))
        r = b[design.col["rating"]] / 0.2
        r_se = math.sqrt(cov[design.col["rating"], design.col["rating"]]) / 0.2
        out[n] = {"kind": "familiar" if n in design.familiar else "invented", "mbbe": est, "se": se,
                  "share_premium_pp": 100 * (math.exp(est) / (math.exp(est) + 4) - 0.2),
                  "price_slope": slope, "price_slope_se": slope_se,
                  "price_equivalent_pct": 100 * (math.exp(est / abs(slope)) - 1) if slope + 1.96 * slope_se < 0 else None,
                  "rating_equivalent_stars": est / r if r - 1.96 * r_se > 0 else None}
    return out


# ---------------------------------------------------------------- data

def load_items(path):
    items = {}
    for line in open(path, encoding="utf8"):
        it = json.loads(line)
        items[it["id"]] = it
    return items


def read_answer_files(spec):
    """The runner's own files (one JSON line per answer: id, model, answer, finish, ...; .jsonl or .jsonl.gz), given as a
    file, a folder or a comma-separated list; or a CSV with model, id and letter or answer."""
    import gzip
    paths = []
    for part in str(spec).split(","):
        p = pathlib.Path(part)
        paths += sorted(p.glob("**/*.jsonl*")) if p.is_dir() else [p]
    rows = []
    for p in paths:
        if p.suffix == ".csv" or p.name.endswith(".csv.gz"):
            rows.append(pd.read_csv(p, dtype=str, keep_default_na=False))
            continue
        opener = gzip.open if p.name.endswith(".gz") else open
        with opener(p, "rt", encoding="utf8") as fh:
            rows.append(pd.DataFrame([json.loads(l) for l in fh if l.strip()]).astype(str))
    return pd.concat(rows, ignore_index=True)


def load_answers(path):
    d = read_answer_files(path)
    if "letter" not in d.columns:
        src = d["raw"] if "raw" in d.columns else d["answer"]
        d["letter"] = [pick(final_answer(r if r not in ("", "nan") else a))[0] for r, a in zip(src, d["answer"])]
    if "answer" in d.columns:
        from decline import classify
        src = d["raw"] if "raw" in d.columns else d["answer"]
        finals = [final_answer(r if isinstance(r, str) and r not in ("", "nan") else a) for r, a in zip(src, d["answer"])]
        d["decline"] = [L not in LETTERS and isinstance(f, str) and bool(f) and classify(f) == "decline"
                        for L, f in zip(d["letter"], finals)]
    else:
        d["decline"] = False
    if "rating" not in d.columns and "answer" in d.columns:
        from parse_audit import rating
        d["rating"] = d.answer.map(lambda a: rating(a)[0])
    if "recognized" not in d.columns and "answer" in d.columns:
        from parse_audit import recognition

        def claim(a, need_country):
            r, _ = recognition(a)
            if r is None:
                return ""
            return str(int(bool(r["yes"]) and (bool(r["country"]) or not need_country)))
        # Amendment 2: a claim is a yes that names a country; Amendment 1's reading (any yes) is kept beside it
        d["recognized"] = d.answer.map(lambda a: claim(a, True))
        d["recognized_any_yes"] = d.answer.map(lambda a: claim(a, False))
    return d


CLAIM_SHARE_TO_LEAVE_REFERENCE = 0.75  # Amendment 2: at least three of the four recognition answers


def recognition_shares(items, ans, column="recognized"):
    """{(model, category, name): share of the recognition answers that claim to know the name}."""
    acc = collections.defaultdict(list)
    for r in ans.itertuples(index=False):
        it = items.get(r.id)
        if it is None or it["cell"] != "recognition":
            continue
        v = str(getattr(r, column, "")).strip()
        if v in ("0", "1"):
            acc[(r.model, it["category"], it["rec_name"])].append(int(v))
    return {k: float(np.mean(v)) for k, v in acc.items()}


def by_model_category(items, ans):
    """{model: {category: {"shown": [(item, letter)], "hidden": {...}, ...}}}"""
    out = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for r in ans.itertuples(index=False):
        it = items.get(r.id)
        if it is None:
            continue
        out[r.model][it["category"]][it["cell"]].append((it, r))
    return out


# ---------------------------------------------------------------- per model and category

def fit_category(shown, design=None):
    """shown: list of (item, letter). Returns (design, b, cov, ll, sets used)."""
    use = [(it, L) for it, L in shown if L in LETTERS]
    design = design or Design([it for it, _ in use])
    X, y = design.matrix([it for it, _ in use], [L for _, L in use])
    b, cov, ll = fit_clogit(X, y)
    return design, b, cov, ll, use


def blind_gap(shown, hidden):
    """For each name: share of shown sets in which its product was picked minus that share in the hidden twins."""
    h = {it["set_id"]: L for it, L in hidden if L in LETTERS}
    acc = collections.defaultdict(lambda: [0, 0, 0])
    for it, L in shown:
        if L not in LETTERS or it["set_id"] not in h:
            continue
        for letter, p in it["products"].items():
            a = acc[p["name"]]
            a[0] += int(L == letter)
            a[1] += int(h[it["set_id"]] == letter)
            a[2] += 1
    return {n: {"gap_pp": 100 * (a[0] - a[1]) / a[2], "sets": a[2]} for n, a in acc.items()}


def bootstrap_mbbe(shown, design, draws, rng, ref=None, keep_draws=False):
    """The 95 per cent interval of each name's MBBE from sets resampled within the category; with keep_draws, also
    every draw's MBBE of each name (for the known-groups interval, which combines draw k across categories)."""
    use = [(it, L) for it, L in shown if L in LETTERS]
    X, y = design.matrix([it for it, _ in use], [L for _, L in use])
    out = collections.defaultdict(list)
    for _ in range(draws):
        i = rng.integers(0, len(y), len(y))
        b, cov, _ = fit_clogit(X[i], y[i])
        for n, v in mbbe_from(design, b, cov, ref).items():
            out[n].append(v["mbbe"])
    ci = {n: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for n, v in out.items()}
    return (ci, {n: np.array(v) for n, v in out.items()}) if keep_draws else ci


HALF_SPLITS = 200  # random halves kept for the reliabilities of the pooled correlations (plan, section 7 item 2)


def inside_tested_span(pe_pct, prices):
    """A price equivalent compares a name with a price ratio, 1 + pe / 100; it lies inside the prices that the category
    tested when that ratio is between the bottom price over the top one and the top price over the bottom one."""
    if pe_pct is None:
        return None
    span = max(prices) / min(prices)
    return bool(1 / span <= 1 + pe_pct / 100 <= span)


def disattenuate(r, ci, ra, rb):
    """Spearman's (1904) correction: r / sqrt(ra x rb), with the interval's bounds divided by the same factor."""
    f = math.sqrt(ra * rb)
    return r / f, ([x / f for x in ci] if ci else None)


def half_corr(a, b):
    """The correlation of two halves over the cells where both exist (None for fewer than three or a constant half)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return None
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def reliability_from(rs, **extra):
    """The mean half correlation over the splits, Spearman-Brown corrected once (averaging the corrected values would
    let one split with a half correlation near -1 dominate the mean)."""
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    r = float(np.mean(rs))
    return dict({"spearman_brown_mean": 2 * r / (1 + r) if r > -1 else None, "mean_half_r": r, "splits": len(rs)}, **extra)


def split_half(cats, n_splits, rng, keep=0):
    """cats: {category: (design, [(item, letter)] used, reference names)}. Spearman-Brown corrected split-half
    correlation over the familiar names of all categories, for each split; returns the mean and the 2.5 and 97.5
    percentiles, and, with keep > 0, the first `keep` splits' two halves of every familiar name (for the pooled
    reliabilities of section 7)."""
    pre = {c: d.matrix([it for it, _ in u], [L for _, L in u]) + (d, ref) for c, (d, u, ref) in cats.items()}
    rs, kept = [], []
    cells = [(c, n) for c, (X, y, d, ref) in pre.items() for n in d.familiar]
    for s in range(n_splits):
        a_, b_ = [], []
        for c, (X, y, d, ref) in pre.items():
            perm = rng.permutation(len(y))
            h1, h2 = perm[: len(y) // 2], perm[len(y) // 2:]
            m1 = mbbe_from(d, *fit_clogit(X[h1], y[h1])[:2], ref)
            m2 = mbbe_from(d, *fit_clogit(X[h2], y[h2])[:2], ref)
            a_ += [m1[n]["mbbe"] for n in d.familiar]
            b_ += [m2[n]["mbbe"] for n in d.familiar]
        r = float(np.corrcoef(a_, b_)[0, 1])
        rs.append(2 * r / (1 + r))
        if s < keep:
            kept.append((a_, b_))
    res = {"spearman_brown_mean": float(np.mean(rs)), "interval": [float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))],
           "splits": n_splits, "pairs": len(cells)}
    return (res, cells, kept) if keep else res


def gap_halves(shown, hidden, names, rng, n_splits):
    """The randomized blind gap of each name from random halves of the category's sets: [(half 1, half 2)] per split,
    each a list in the order of `names`."""
    h = {it["set_id"]: L for it, L in hidden if L in LETTERS}
    sets = [(it, L) for it, L in shown if L in LETTERS and it["set_id"] in h]
    out = []
    for _ in range(n_splits):
        perm = rng.permutation(len(sets))
        halves = []
        for part in (perm[: len(sets) // 2], perm[len(sets) // 2:]):
            g = blind_gap([sets[i] for i in part], [(sets[i][0], h[sets[i][0]["set_id"]]) for i in part])
            halves.append([g[n]["gap_pp"] if n in g else np.nan for n in names])
        out.append(tuple(halves))
    return out


def rating_halves(items_rows, names, rng, n_splits):
    """Arm 4's rating difference of each name from random halves of its own answers (the unnamed baseline from all of
    the unnamed answers, as in rating_arm)."""
    d = pd.DataFrame([{"name": it["rated_name"], "kind": it["name_kind"], "profile": it["profile_id"], "wording": it["wording"],
                       "rating": float(r.rating) if str(getattr(r, "rating", "")).strip() not in ("", "None", "nan") else np.nan}
                      for it, r in items_rows])
    base = d[d.kind == "unnamed"].groupby(["profile", "wording"]).rating.mean()
    d = d[d.kind != "unnamed"].join(base.rename("base"), on=["profile", "wording"])
    diffs = {n: (g.rating - g.base).dropna().to_numpy() for n, g in d.groupby("name")}
    out = []
    for _ in range(n_splits):
        h1, h2 = [], []
        for n in names:
            v = diffs.get(n, np.array([]))
            if len(v) < 2:
                h1.append(np.nan)
                h2.append(np.nan)
                continue
            p = rng.permutation(len(v))
            h1.append(float(v[p[: len(v) // 2]].mean()))
            h2.append(float(v[p[len(v) // 2:]].mean()))
        out.append((h1, h2))
    return out


def premium_at_one_in_five(shares):
    """shares: {premium: share}. The premium (per cent) at which the share equals 20 per cent, by linear interpolation
    between the two levels that bracket it; None when no pair brackets it (arm 5, plan 4.5)."""
    ks = sorted(shares)
    vs = [shares[k] for k in ks]
    for i in range(len(ks) - 1):
        if (vs[i] - 0.2) * (vs[i + 1] - 0.2) <= 0 and vs[i] != vs[i + 1]:
            return round(100 * (ks[i] + (0.2 - vs[i]) * (ks[i + 1] - ks[i]) / (vs[i + 1] - vs[i])), 1)
    return None


def premium_halves(items_rows, names, rng, n_splits):
    """Arm 5's premium at one in five of each name from random halves of its answers at each premium level."""
    d = pd.DataFrame([{"name": it["focal_name"], "premium": it["premium"], "picked": int(r.letter == it["focal_letter"])}
                      for it, r in items_rows if r.letter in LETTERS])
    by = {n: {k: g2.picked.to_numpy() for k, g2 in g.groupby("premium")} for n, g in d.groupby("name")} if len(d) else {}
    out = []
    for _ in range(n_splits):
        h1, h2 = [], []
        for n in names:
            lv = by.get(n)
            if not lv:
                h1.append(np.nan)
                h2.append(np.nan)
                continue
            s1, s2 = {}, {}
            for k, v in lv.items():
                p = rng.permutation(len(v))
                s1[k], s2[k] = float(v[p[: len(v) // 2]].mean()) if len(v) > 1 else np.nan, float(v[p[len(v) // 2:]].mean())
            x1 = premium_at_one_in_five(s1) if not any(np.isnan(list(s1.values()))) else None
            x2 = premium_at_one_in_five(s2)
            h1.append(np.nan if x1 is None else x1)
            h2.append(np.nan if x2 is None else x2)
        out.append((h1, h2))
    return out


def joint_fit_check(shown, hidden, design):
    """Plan 4.2: the joint fit of arms 1 and 2 (the shown sets and their names-hidden twins), with a term for shown
    times each attribute level, the rating and log price; a term above or below zero by its interval means that the
    model relies on that specification more or less when the names are shown."""
    s = [(it, L) for it, L in shown if L in LETTERS]
    h = [(it, L) for it, L in hidden if L in LETTERS]
    Xs, ys = design.matrix([it for it, _ in s], [L for _, L in s])
    Xh, yh = design.matrix([it for it, _ in h], [L for _, L in h], with_names=False)
    J = [design.col[t] for t in design.terms if t.startswith("a") or t in ("rating", "log_price")]
    inter = np.concatenate([Xs[:, :, J], np.zeros_like(Xh[:, :, J])], 0)
    X = np.concatenate([np.concatenate([Xs, Xh], 0), inter], 2)
    b, cov, _ = fit_clogit(X, np.concatenate([ys, yh]))
    K = len(design.terms)
    return {f"shown_x_{design.terms[j]}": [float(b[K + i]), float(math.sqrt(max(cov[K + i, K + i], 0)))] for i, j in enumerate(J)}


def repeat_mbbe(shown, repeat, design, ref):
    """Plan 5.3: MBBE of each familiar name fitted on the first run of the repeated sets and on their repeat."""
    rep_ids = {it["set_id"] for it, _ in repeat}
    first = [(it, L) for it, L in shown if it["set_id"] in rep_ids and L in LETTERS]
    again = [(it, L) for it, L in repeat if L in LETTERS]
    if len(first) < 50 or len(again) < 50:
        return None
    out = []
    for part in (first, again):
        X, y = design.matrix([it for it, _ in part], [L for _, L in part])
        b, cov, _ = fit_clogit(X, y)
        m = mbbe_from(design, b, cov, ref)
        out.append([m[n]["mbbe"] for n in design.familiar])
    return out


def kappa(a, b):
    a, b = np.array(a), np.array(b)
    po = float((a == b).mean())
    pe = float(sum((a == L).mean() * (b == L).mean() for L in LETTERS))
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def factor_stability(shown, design, key):
    """Brand-by-factor variance against brand variance, from separate fits for each level of the factor."""
    levels = sorted({it[key] for it, _ in shown})
    est = {}
    for lv in levels:
        sub = [(it, L) for it, L in shown if it[key] == lv]
        _, b, cov, _, _ = fit_category(sub, design)
        est[lv] = mbbe_from(design, b, cov)
    fam = design.familiar
    M = np.array([[est[lv][n]["mbbe"] for lv in levels] for n in fam])
    S2 = np.array([[est[lv][n]["se"] ** 2 for lv in levels] for n in fam])
    inter = float(np.mean(M.var(1, ddof=1) - S2.mean(1)))
    brand = float(M.mean(1).var(ddof=1) - (S2.mean(1) / len(levels)).mean())
    return {"levels": levels, "brand_variance": brand, "brand_by_factor_variance": inter}


def rating_arm(items_rows):
    """Arm 4: mean rating of each name minus the unnamed version, paired by profile and wording."""
    d = pd.DataFrame([{"name": it["rated_name"], "kind": it["name_kind"], "profile": it["profile_id"], "wording": it["wording"],
                       "rating": float(r.rating) if str(getattr(r, "rating", "")).strip() not in ("", "None", "nan") else np.nan}
                      for it, r in items_rows])
    base = d[d.kind == "unnamed"].groupby(["profile", "wording"]).rating.mean()
    d = d[d.kind != "unnamed"].join(base.rename("base"), on=["profile", "wording"])
    d["diff"] = d.rating - d.base
    return {n: {"rating_difference": float(g["diff"].mean()), "answers": int(g["diff"].notna().sum())} for n, g in d.groupby("name")}


def premium_arm(items_rows):
    """Arm 5: the focal brand's share at each premium, and the premium at which the share equals 20 per cent."""
    d = pd.DataFrame([{"name": it["focal_name"], "premium": it["premium"], "picked": int(r.letter == it["focal_letter"])}
                      for it, r in items_rows if r.letter in LETTERS])
    out = {}
    for n, g in d.groupby("name"):
        s = g.groupby("premium").picked.mean().sort_index()
        x = None
        ks, vs = list(s.index), list(s.values)
        for i in range(len(ks) - 1):
            if (vs[i] - 0.2) * (vs[i + 1] - 0.2) <= 0 and vs[i] != vs[i + 1]:
                x = ks[i] + (0.2 - vs[i]) * (ks[i + 1] - ks[i]) / (vs[i + 1] - vs[i])
                break
        out[n] = {"share_by_premium": {f"{k:+.2f}": round(float(v), 3) for k, v in s.items()},
                  "premium_at_one_in_five": None if x is None else round(100 * x, 1),
                  "note": "" if x is not None else ("above 20 per cent at every premium" if min(vs) > 0.2 else "below 20 per cent at every premium")}
    return out


# ---------------------------------------------------------------- the analysis of real answers

def model_rng(model):
    """Each model's own generator, seeded from SEED and the model's key, so that a model's draws are the same whether
    the models run one after another or in parallel (--workers), and do not depend on which other models are present."""
    return np.random.default_rng([SEED, int(hashlib.sha256(model.encode()).hexdigest()[:8], 16)])


def analyse_model(model, cats, rec, rec_any, draws, splits):
    """Sections 4 and 5 for one model: every category's fit, intervals, blind gap and checks, then reliability."""
    rng = model_rng(model)
    rng_h = model_rng(model + "|halves")  # its own generator, so that the first run's draws and numbers are unchanged
    mres = {"categories": {}}
    fitted, draws_by_cat, halves = {}, {}, {}
    choice = [r for arms in cats.values() for arm in ("shown", "hidden", "repeat", "premium") for _, r in arms.get(arm, [])]
    mres["choice_items"] = len(choice)
    mres["choice_items_with_a_letter"] = sum(1 for r in choice if r.letter in LETTERS)
    mres["choice_items_declines"] = sum(1 for r in choice if r.letter not in LETTERS and bool(getattr(r, "decline", False)))
    for cat, arms in sorted(cats.items()):
        shown = [(it, r.letter) for it, r in arms["shown"]]
        hidden = [(it, r.letter) for it, r in arms["hidden"]]
        design, b, cov, ll, use = fit_category(shown)
        # Amendments 1 and 2: the reference leaves out invented names that this model claims to know (a yes with a
        # country, in at least three of its four recognition answers)
        known = {n: rec.get((model, cat, n)) for n in design.names}
        ref = [n for n in design.invented if (known[n] if known[n] is not None else 0) < CLAIM_SHARE_TO_LEAVE_REFERENCE]
        flag = "" if ref else "every invented name is claimed; the reference keeps all of them"
        ref = ref or list(design.invented)
        m = mbbe_from(design, b, cov, ref)
        m_all = mbbe_from(design, b, cov)
        for n in m:
            m[n]["mbbe_section4_reference"] = m_all[n]["mbbe"]
            m[n]["recognized_share"] = known[n]
            m[n]["recognized_share_any_yes"] = rec_any.get((model, cat, n))
            m[n]["unknown_to_model"] = bool(m[n]["kind"] == "familiar" and known[n] is not None and known[n] < 0.5)
            m[n]["name_status"] = design.status.get(n, "")
            m[n]["price_equivalent_inside_tested_span"] = inside_tested_span(m[n]["price_equivalent_pct"], design.prices)
        ci, bdraws = bootstrap_mbbe(shown, design, draws, rng, ref, keep_draws=True)
        gap = blind_gap(shown, hidden)
        hd = Design([it for it, _ in hidden])
        Xh, yh = hd.matrix([it for it, L in hidden if L in LETTERS], [L for _, L in hidden if L in LETTERS], with_names=False)
        keep = [i for i, t in enumerate(hd.terms) if not t.startswith("name:") and t != "familiar_x_log_price"]
        bh, covh, _ = fit_clogit(Xh[:, :, keep], yh)
        spec = {hd.terms[k]: [float(bh[j]), float(math.sqrt(covh[j, j]))] for j, k in enumerate(keep) if hd.terms[k].startswith("a")}
        # Amendment 2, item 1: a model and category whose names-hidden picks do not follow the specifications is
        # reported by itself and left out of the pooled analyses
        reads = sum(1 for a in range(3) if f"a{a}_l2" in spec and spec[f"a{a}_l2"][0] - 1.96 * spec[f"a{a}_l2"][1] > 0) >= 2
        hidden_terms = {hd.terms[k]: [float(bh[j]), float(math.sqrt(covh[j, j]))] for j, k in enumerate(keep)}
        if reads:
            fitted[cat] = (design, use, ref)
            draws_by_cat[cat] = (design, bdraws)
            halves[cat] = {"blind_gap": gap_halves(shown, hidden, design.familiar, rng_h, HALF_SPLITS)}
            if arms.get("rating"):
                halves[cat]["rating_difference"] = rating_halves(arms["rating"], design.familiar, rng_h, HALF_SPLITS)
            if arms.get("premium"):
                halves[cat]["premium_at_one_in_five"] = premium_halves(arms["premium"], design.familiar, rng_h, HALF_SPLITS)
        # held-out sets: the fit with names against the fit without them
        perm = rng.permutation(len(use))
        test, train = perm[: len(use) // 5], perm[len(use) // 5:]
        X, y = design.matrix([it for it, _ in use], [L for _, L in use])
        nn = [i for i, t in enumerate(design.terms) if not t.startswith("name:") and t != "familiar_x_log_price"]
        b1, _, _ = fit_clogit(X[train], y[train])
        b0, _, _ = fit_clogit(X[train][:, :, nn], y[train])

        def ll_of(bb, XX, yy):
            u = XX @ bb
            mm = u.max(1, keepdims=True)
            return float((u[np.arange(len(yy)), yy] - (mm[:, 0] + np.log(np.exp(u - mm).sum(1)))).sum())
        mres["categories"][cat] = {
            "sets_shown": len(shown), "sets_with_a_letter": len(use), "log_likelihood": ll,
            "invented_reference": ref, "reference_flag": flag, "reads_specifications": reads,
            "names": {n: dict(v, ci95=ci[n], blind_gap_pp=gap.get(n, {}).get("gap_pp")) for n, v in m.items()},
            "coefficients": {t: [float(b[i]), float(math.sqrt(cov[i, i]))] for i, t in enumerate(design.terms) if not t.startswith("name:")},
            "names_hidden_attribute_terms": spec, "names_hidden_terms": hidden_terms,
            "joint_fit_shown_terms": joint_fit_check(shown, hidden, design),
            "tested_prices": design.prices,
            "held_out_log_likelihood_gain": ll_of(b1, X[test], y[test]) - ll_of(b0, X[test][:, :, nn], y[test]),
            "stability": {k: factor_stability(shown, design, k) for k in ("system_index", "layout", "request_wording")},
        }
        if arms.get("repeat"):
            first = {it["set_id"]: r.letter for it, r in arms["shown"]}
            pairs = [(first[it["set_id"]], r.letter) for it, r in arms["repeat"] if it["set_id"] in first]
            pairs = [(a, b_) for a, b_ in pairs if a in LETTERS and b_ in LETTERS]
            if pairs:
                po, k = kappa(*zip(*pairs))
                mres["categories"][cat]["repeat"] = {"pairs": len(pairs), "same_pick": po, "kappa": k}
                rm = repeat_mbbe(shown, [(it, r.letter) for it, r in arms["repeat"]], design, ref)
                if rm:
                    mres["categories"][cat]["repeat"]["mbbe_first_and_repeat"] = dict(zip(design.familiar, zip(*rm)))
        if arms.get("rating"):
            mres["categories"][cat]["rating_arm"] = rating_arm(arms["rating"])
        if arms.get("premium"):
            mres["categories"][cat]["premium_arm"] = premium_arm(arms["premium"])
    reading = {c for c, cr in mres["categories"].items() if cr["reads_specifications"]}
    mres["categories_that_read_the_specifications"] = sorted(reading)
    mres["categories_left_out_of_pooled_analyses"] = sorted(set(mres["categories"]) - reading)
    fam = [(c, n, v) for c, cr in mres["categories"].items() if c in reading for n, v in cr["names"].items() if v["kind"] == "familiar"]
    inv = [(c, n, v) for c, cr in mres["categories"].items() if c in reading for n, v in cr["names"].items() if v["kind"] == "invented"]
    est = np.array([v["mbbe"] for _, _, v in fam])
    se2 = np.array([v["se"] ** 2 for _, _, v in fam])
    sh = split_half(fitted, splits, rng, keep=HALF_SPLITS) if len(fam) > 2 else None
    mres["reliability"] = {"split_half": sh[0] if sh else None,
                           "signal_share": float(1 - se2.mean() / est.var(ddof=1)) if len(est) > 1 else None}
    kg = None
    if fam and inv:
        # plan 6.1: the familiar names' mean MBBE with its interval (draw k of every reading category together, since
        # the categories' sets were resampled apart), and the new invented names against the corpus's invented names
        fam_draws = np.mean([dr[n] for c, (d, dr) in draws_by_cat.items() for n in d.familiar], axis=0)
        diffs, diff_draws = [], []
        for c, (d, dr) in draws_by_cat.items():
            new = [n for n in d.invented if d.status.get(n) == "new"]
            old = [n for n in d.invented if d.status.get(n) == "corpus"]
            if new and old:
                cr = mres["categories"][c]["names"]
                diffs.append(np.mean([cr[n]["mbbe"] for n in new]) - np.mean([cr[n]["mbbe"] for n in old]))
                diff_draws.append(np.mean([dr[n] for n in new], axis=0) - np.mean([dr[n] for n in old], axis=0))
        kg = {"familiar_mean_mbbe": float(est.mean()), "familiar_pairs": len(fam),
              "familiar_mean_ci95": [float(np.percentile(fam_draws, 2.5)), float(np.percentile(fam_draws, 97.5))],
              "invented_spread": [float(min(v["mbbe"] for _, _, v in inv)), float(max(v["mbbe"] for _, _, v in inv))],
              "new_minus_corpus_invented": ({"categories": len(diffs), "mbbe": float(np.mean(diffs)),
                                            "ci95": [float(np.percentile(np.mean(diff_draws, 0), 2.5)),
                                                     float(np.percentile(np.mean(diff_draws, 0), 97.5))]} if diffs else None)}
    mres["known_groups"] = kg
    mres["_halves"] = {"cells": [(c, n) for c in sorted(halves) for n in fitted[c][0].familiar],
                       "mbbe": ({"cells": sh[1], "splits": sh[2]} if sh else None),
                       "by_category": halves}
    return mres


_ITEMS = None


def _init_worker(items):
    global _ITEMS
    _ITEMS = items


def _model_job(args):
    model, ans_model, rec, rec_any, draws, splits = args
    return model, analyse_model(model, by_model_category(_ITEMS, ans_model)[model], rec, rec_any, draws, splits)


def analyse(items, ans, draws, splits, workers=1):
    """analyse_model for every model; with workers > 1 the models run in a pool of processes, with the same results."""
    data = by_model_category(items, ans)
    rec = recognition_shares(items, ans)
    rec_any = recognition_shares(items, ans, "recognized_any_yes") if "recognized_any_yes" in ans.columns else {}
    models = sorted(data)
    if workers > 1 and len(models) > 1:
        import multiprocessing
        jobs = [(m, ans[ans.model == m], rec, rec_any, draws, splits) for m in models]
        with multiprocessing.Pool(min(workers, len(models)), initializer=_init_worker, initargs=(items,)) as pool:
            out = dict(pool.map(_model_job, jobs, chunksize=1))
    else:
        out = {m: analyse_model(m, data[m], rec, rec_any, draws, splits) for m in models}
    res = {"models": {m: out[m] for m in models}}
    res["_halves"] = {m: v.pop("_halves") for m, v in res["models"].items()}
    left = {}
    for m, v in res["models"].items():
        nd = v.get("choice_items_declines", 0)
        n, k = v["choice_items"] - nd, v["choice_items_with_a_letter"]  # the read share is over the non-declines
        v["choice_items_read_pct"] = round(100 * k / n, 2) if n else None
        if n and k / n < READ_RULE:
            left[m] = {"choice_items": v["choice_items"], "declines": nd, "with_a_letter": k, "read_pct": round(100 * k / n, 1)}
    res["left_out"] = {"rule": RULE_TEXT, "models": left}
    return res


READ_RULE = 0.90
RULE_TEXT = ("A model whose answers the parser reads in under 90 per cent of a build's items is reported apart as unable "
             "to do the task and left out of every pooled estimate (jmr-2026/PLAN.md, section 6; Study 2's open-models "
             "rule). Here the items are the choice items (shown, names-hidden, repeated and premium sets), whose answers "
             "are letters, less the answers that decline to recommend any product, which are an outcome, not unread "
             "(PLAN.md section 6, as amended at about 2:37 AM on 22 November 2026; harness/decline.py).")


def included(res):
    return [m for m in res["models"] if m not in res.get("left_out", {}).get("models", {})]


# ---------------------------------------------------------------- sections 6 and 7: validity and convergence

BRAND_LEVEL = PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level"


def cells_table(res):
    """One row per model, category and familiar name, with every counterpart that the pilot gives."""
    rows = []
    for model, m in res["models"].items():
        if model not in included(res):
            continue  # the exclusion rule (READ_RULE): reported apart, left out of the pooled tables
        for cat, c in m["categories"].items():
            if not c.get("reads_specifications", True):
                continue  # Amendment 2, item 1: reported by itself, left out of the pooled tables
            ra, pa = c.get("rating_arm", {}), c.get("premium_arm", {})
            for n, v in c["names"].items():
                if v["kind"] != "familiar":
                    continue
                rows.append({"model": model, "category": cat, "brand": n, "mbbe": v["mbbe"], "mbbe_se": v["se"],
                             "blind_gap": v.get("blind_gap_pp"), "rating_difference": ra.get(n, {}).get("rating_difference"),
                             "premium_at_one_in_five": pa.get(n, {}).get("premium_at_one_in_five")})
    d = pd.DataFrame(rows)
    old = pd.read_csv(BRAND_LEVEL / "brand_model_equity.csv")
    old = old[old.source == "open"].set_index(["model", "brand"]).equity
    d["corpus_table_gap"] = [old.get((m, b), np.nan) for m, b in zip(d.model, d.brand)]
    return d


def twoway_corr(d, a, b, draws, rng):
    x = d[["model", "brand", a, b]].dropna()
    if len(x) < 5 or x[a].nunique() < 2 or x[b].nunique() < 2:
        return {"cells": len(x), "note": "too few cells"}
    models, brands = x.model.unique(), x.brand.unique()
    by = {(m, br): g for (m, br), g in x.groupby(["model", "brand"])}
    boot = []
    for _ in range(draws):
        ms = rng.choice(models, len(models))
        bs = rng.choice(brands, len(brands))
        parts = [by[(m, br)] for m in ms for br in bs if (m, br) in by]
        if not parts:
            continue
        y = pd.concat(parts)
        if y[a].nunique() > 1 and y[b].nunique() > 1:
            boot.append(np.corrcoef(y[a], y[b])[0, 1])
    within = [np.corrcoef(g[a], g[b])[0, 1] for _, g in x.groupby("model") if len(g) > 2 and g[a].nunique() > 1 and g[b].nunique() > 1]
    return {"cells": len(x), "pooled_r": float(np.corrcoef(x[a], x[b])[0, 1]),
            "ci95_models_and_brands_resampled": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))] if boot else None,
            "within_model_mean_r": float(np.mean(within)) if within else None}


def pooled_reliability(halves, measure, models):
    """Split-half reliability of a measure over the pooled brand, category and model cells of `models`: in each kept
    split the two halves of every cell are pooled over the models and correlated, Spearman-Brown corrected; the mean
    over the splits."""
    rs = []
    for s in range(HALF_SPLITS):
        a, b = [], []
        for m in models:
            h = halves.get(m) or {}
            if measure == "mbbe":
                hm = h.get("mbbe")
                if hm and s < len(hm["splits"]):
                    a += list(hm["splits"][s][0])
                    b += list(hm["splits"][s][1])
                continue
            for c, hc in (h.get("by_category") or {}).items():
                if measure in hc and s < len(hc[measure]):
                    a += list(hc[measure][s][0])
                    b += list(hc[measure][s][1])
        rs.append(half_corr(a, b))
    return reliability_from(rs)


def pair_reliability(halves, models):
    """Split-half reliability of the brand and category pairs' MBBE averaged over the models (the unit of the
    discriminant correlations), from the same splits."""
    rs = []
    for s in range(HALF_SPLITS):
        acc = collections.defaultdict(lambda: ([], []))
        for m in models:
            hm = (halves.get(m) or {}).get("mbbe")
            if not hm or s >= len(hm["splits"]):
                continue
            for (c, n), x, y in zip(hm["cells"], *hm["splits"][s]):
                acc[(n, c)][0].append(x)
                acc[(n, c)][1].append(y)
        rs.append(half_corr([np.mean(v[0]) for v in acc.values()], [np.mean(v[1]) for v in acc.values()]))
    return reliability_from(rs)


def corpus_gap_halves(rng, n_splits=HALF_SPLITS):
    """Plan 7.2: the split-half reliability of the corpus tables' blind gap (brand_model_equity.csv's open rows: the ten
    open models' Study 1 rerun in export 12154), from random halves of each table's 20 trials (a trial's names-shown and
    names-hidden answers stay together); the gap of a half is 100 x (share picking the brand's products with names
    shown minus with names hidden), the brand's tables pooled, as brand_level.py computes it."""
    export = PKG / "study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12154.csv.gz"
    items_path = CORPUS_BUILDS["study1-rerun/s1rerun1"]
    eq = pd.read_csv(BRAND_LEVEL / "brand_model_equity.csv")
    eq = eq[eq.source == "open"]
    if not export.exists() or eq.empty:
        return None
    keys = sorted(set(zip(eq.model, eq.brand)))
    items = {json.loads(l)["id"]: json.loads(l) for l in _open_text(items_path)}
    a = pd.read_csv(export, dtype={"letter": str}, keep_default_na=False)
    a = a[(a["build"] == "study1-rerun/s1rerun1") & a["model"].isin(set(eq.model))]
    rows = []
    for m, iid, letter in zip(a["model"], a["id"], a["letter"]):
        it = items.get(iid)
        if it is None or it["names"] not in ("shown", "hidden"):
            continue
        for L, p in it["products"].items():
            rows.append((m, it["table"], it["trial"], it["names"], p["true_brand"], int(letter == L)))
    d = pd.DataFrame(rows, columns=["model", "table", "trial", "names", "brand", "picked"])
    trials = d[["model", "table", "trial"]].drop_duplicates().reset_index(drop=True)
    out = []
    for _ in range(n_splits):
        t = trials.assign(u=rng.random(len(trials)))
        t["half"] = (t.groupby(["model", "table"]).u.rank(method="first") > t.groupby(["model", "table"]).u.transform("size") / 2).astype(int)
        g = d.merge(t[["model", "table", "trial", "half"]], on=["model", "table", "trial"])
        sh = g.groupby(["half", "model", "brand", "names"]).picked.mean().unstack("names")
        gap = (100 * (sh["shown"] - sh["hidden"]))
        out.append(tuple([gap.get((h, m, b_), np.nan) for m, b_ in keys] for h in (0, 1)))
    return reliability_from([half_corr(*s) for s in out], cells=len(keys),
                            export="study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12154.csv.gz")


def convergence(res, draws, rng, halves=None):
    d = cells_table(res)
    measures = ["mbbe", "blind_gap", "rating_difference", "premium_at_one_in_five", "corpus_table_gap"]
    models = included(res)
    rel = {m: (res["models"][m]["reliability"]["split_half"] or {}).get("spearman_brown_mean") for m in models}
    pooled_rel = {}
    if halves is not None:
        pooled_rel = {k: pooled_reliability(halves, k, models) for k in measures[:4]}
        pooled_rel["corpus_table_gap"] = corpus_gap_halves(np.random.default_rng([SEED, 7]))
    out = {}
    for i, a in enumerate(measures):
        for b in measures[i + 1:]:
            r = twoway_corr(d, a, b, draws, rng)
            if a == "mbbe" and b == "blind_gap":
                r["note"] = "the same answers give both, so their agreement is reported and not counted as convergence"
            ra, rb = (pooled_rel.get(a) or {}).get("spearman_brown_mean"), (pooled_rel.get(b) or {}).get("spearman_brown_mean")
            if "pooled_r" in r and ra and rb and ra > 0 and rb > 0:
                # plan 7.2 (Spearman 1904): r / sqrt(reliability a x reliability b); the interval's bounds are divided by
                # the same factor
                r["corrected_r"], r["corrected_ci95"] = disattenuate(r["pooled_r"], r.get("ci95_models_and_brands_resampled"), ra, rb)
                r["reliabilities"] = [ra, rb]
            out[f"{a} | {b}"] = r
    out["mbbe_reliability_by_model"] = rel
    out["pooled_reliability"] = pooled_rel
    out["models"] = models
    out["note"] = ("corrected for the two measures' pooled split-half reliabilities over the same models' cells (plan, "
                   "section 7 item 2); the interval's bounds are divided by the same factor")
    return out, d


def discriminant(d, draws, rng, pair_rel=None):
    b = pd.read_csv(BRAND_LEVEL / "brand_equity.csv", index_col=0)
    pair = d.groupby(["brand", "category"]).mbbe.mean().reset_index()
    out = {"mbbe_pair_reliability": pair_rel}
    for col in ("log_freq_with_category", "log_freq_name_alone", "log10_wikipedia_monthly_views", "coded_high_share",
                "consumer_familiarity_mean", "in_a_value_ranking", "log10_brand_value"):
        if col not in b:
            continue
        x = pair.join(b[col], on="brand").dropna()
        if len(x) < 5 or x[col].nunique() < 2:
            out[col] = {"pairs": len(x), "note": "too few"}
            continue
        boot = []
        for _ in range(draws):
            i = rng.integers(0, len(x), len(x))
            y = x.iloc[i]
            if y[col].nunique() > 1:
                boot.append(np.corrcoef(y.mbbe, y[col])[0, 1])
        out[col] = {"pairs": len(x), "r": float(np.corrcoef(x.mbbe, x[col])[0, 1]),
                    "ci95_pairs_resampled": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}
        rr = (pair_rel or {}).get("spearman_brown_mean")
        if rr and rr > 0:
            # plan 6.4: corrected for MBBE's reliability (the brand-level columns are taken as measured without error)
            out[col]["corrected_r"], out[col]["corrected_ci95"] = disattenuate(out[col]["r"], out[col]["ci95_pairs_resampled"], rr, 1.0)
    return out


EXPORT = PKG / "study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz"  # the 31 open models' letters
CORPUS_BUILDS = {  # plan 6.3: the corpus tables that the open models answered
    "b2/dom2": PKG / "study1a-tables-with-one-optimal-product/materials/strictly-better-tables/prompts.jsonl.gz",
    "study1-rerun/s1rerun1": PKG / "study1b-64-models-on-34-tables/materials/rerun/prompts.jsonl.gz"}
PILOT_CAT = {"laptops": "laptops", "headphones": "headphones", "wireless_earbuds": "earbuds", "running_shoes": "running_shoes",
             "coffee_makers": "coffee_makers", "smartphones": "smartphones", "tvs": "tvs"}


def corpus_rows(res, export=EXPORT):
    if not pathlib.Path(export).exists():
        return None, None
    a = pd.read_csv(export, dtype={"letter": str}, keep_default_na=False)
    keep = set(included(res))
    rows = []
    for build, path in CORPUS_BUILDS.items():
        items = {json.loads(l)["id"]: json.loads(l) for l in _open_text(path)}
        b = a[(a["build"] == build) & a["model"].isin(keep)]
        if build == "b2/dom2":
            # columns by name: a.info is the DataFrame's own method, not the column
            b = b[(b["info"].astype(str) == "0") & (b["rung"].astype(str) == "0")]
        for m, iid, letter in zip(b["model"], b["id"], b["letter"]):
            it = items.get(iid)
            if it is None or it["category"] not in PILOT_CAT:
                continue
            arm = {"original": "shown", "shown": "shown", "hidden": "hidden"}.get(it.get("names"))
            if arm is None:
                continue
            for L, p in it["products"].items():
                rows.append({"build": build, "model": m, "table": it["table"], "category": PILOT_CAT[it["category"]],
                             "orig": p["orig"], "brand": p["true_brand"], "kind": p["true_kind"], "names": arm,
                             "picked": int(letter == L)})
    h = hashlib.sha256(open(export, "rb").read()).hexdigest()
    return pd.DataFrame(rows), {"file": str(pathlib.Path(export).relative_to(REPO)).replace("\\", "/"), "sha256": h}


def corpus_table_prediction(res, draws, rng, export=EXPORT):
    """Plan 6.3: on the corpus tables that the open models answered,
    each product's predicted names-shown share is proportional to its names-hidden share times exp(MBBE of its brand).
    Primary: tables in the pilot's categories where every familiar name has a pilot estimate."""
    d, src = corpus_rows(res, export)
    if d is None or d.empty:
        return {"note": "no export of the open models' answers in the pilot's categories"}
    s = d.groupby(["build", "model", "table", "category", "orig", "brand", "kind", "names"]).picked.mean().unstack("names").reset_index()
    s = s.rename(columns={"shown": "original"})
    out = {"export": src, "models_left_out": sorted(res.get("left_out", {}).get("models", {})), "pooled": {}}
    errs = []
    for (build, model, table), g in s.groupby(["build", "model", "table"]):
        cres = res["models"].get(model, {}).get("categories", {}).get(g.category.iloc[0], {})
        if not cres.get("reads_specifications"):
            continue  # Amendment 2, item 1: a cell that does not read the specifications is left out of pooled analyses
        mres = cres.get("names", {})
        if not mres:
            continue
        fam = g[g.kind != "invented"]
        complete = all(b_ in mres for b_ in fam.brand)
        inv_mean = 0.0
        w = np.array([math.exp(mres[b_]["mbbe"]) if b_ in mres else (math.exp(inv_mean) if k == "invented" else np.nan)
                      for b_, k in zip(g.brand, g.kind)])
        if np.isnan(w).any():
            w = np.where(np.isnan(w), math.exp(np.nanmean([mres[b_]["mbbe"] for b_ in fam.brand if b_ in mres] or [0])), w)
        pred = g.hidden.to_numpy() * w
        pred = pred / pred.sum() if pred.sum() > 0 else pred
        obs = g.original.to_numpy()
        errs.append({"build": build, "model": model, "table": table, "complete": complete,
                     "mae_prediction": float(np.abs(pred - obs).mean()), "mae_no_change": float(np.abs(g.hidden.to_numpy() - obs).mean())})
    e = pd.DataFrame(errs)
    for which, eb in [("both builds", e)] + [(b_, e[e.build == b_]) for b_ in CORPUS_BUILDS]:
        out["pooled"][which] = {}
        for label, sub in (("primary (every familiar name estimated)", eb[eb.complete]), ("secondary (all tables in the categories)", eb)):
            if sub.empty:
                continue
            diff = sub.mae_prediction - sub.mae_no_change
            boot = [diff.sample(len(diff), replace=True, random_state=int(rng.integers(1e9))).mean() for _ in range(min(draws, 2000))]
            out["pooled"][which][label] = {"model_table_cells": len(sub), "tables": int(sub.table.nunique()),
                                           "models": int(sub.model.nunique()), "mae_prediction": float(sub.mae_prediction.mean()),
                                           "mae_no_change": float(sub.mae_no_change.mean()), "difference": float(diff.mean()),
                                           "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}
    return out


def independence(res, items, ans):
    """Plan 6.6: a name's MBBE against the mean names-hidden pick share of the profiles that it met."""
    data = by_model_category(items, ans)
    out = {}
    for model, cats in data.items():
        xs, ys = [], []
        for cat, arms in cats.items():
            if not res["models"][model]["categories"][cat]["reads_specifications"]:
                continue
            names = res["models"][model]["categories"][cat]["names"]
            h = {it["set_id"]: r.letter for it, r in arms["hidden"] if r.letter in LETTERS}
            acc = collections.defaultdict(list)
            for it, r in arms["shown"]:
                if it["set_id"] in h:
                    for L, p in it["products"].items():
                        acc[p["name"]].append(int(h[it["set_id"]] == L))
            for n, v in acc.items():
                if names[n]["kind"] == "familiar":
                    xs.append(np.mean(v))
                    ys.append(names[n]["mbbe"])
        out[model] = {"r": float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 2 else None, "names": len(xs)}
    return out



def first_job(items, ans, out):
    """The three stop rules of the plan's section 8.2, for each model, and a sample of answers from every arm to read
    by hand. The run is stopped and the design changed when, for a model: the names-hidden picks ignore the
    specifications (fewer than two of the three attributes have a best-level coefficient above zero with its interval
    excluding zero); more than 2 per cent of the answers of the choice arms have no letter; or one display position or
    one letter takes more than 80 per cent of the picks."""
    rng = np.random.default_rng(SEED)
    data = by_model_category(items, ans)
    res, reading = {}, []
    for model, cats in sorted(data.items()):
        mres = {}
        for cat, arms in sorted(cats.items()):
            choice = [(it, r) for arm in ("shown", "hidden", "repeat", "premium") for it, r in arms.get(arm, [])]
            unread = sum(1 for _, r in choice if r.letter not in LETTERS)
            picks = [(it, r.letter) for arm in ("shown", "hidden") for it, r in arms.get(arm, []) if r.letter in LETTERS]
            pos = collections.Counter(it["products"][L]["position"] for it, L in picks)
            let = collections.Counter(L for _, L in picks)
            hidden = [(it, r.letter) for it, r in arms.get("hidden", []) if r.letter in LETTERS]
            spec = {}
            if hidden:
                d = Design([it for it, _ in hidden])
                keep = [i for i, t in enumerate(d.terms) if not t.startswith("name:") and t != "familiar_x_log_price"]
                X, y = d.matrix([it for it, _ in hidden], [L for _, L in hidden], with_names=False)
                b, cov, _ = fit_clogit(X[:, :, keep], y)
                spec = {d.terms[k]: {"coef": round(float(b[j]), 3), "se": round(float(math.sqrt(cov[j, j])), 3)} for j, k in enumerate(keep)
                        if d.terms[k].startswith("a") or d.terms[k] in ("rating", "log_price")}
            follows = sum(1 for a in range(3) if f"a{a}_l2" in spec and spec[f"a{a}_l2"]["coef"] - 1.96 * spec[f"a{a}_l2"]["se"] > 0)
            ratings = [r for it, r in arms.get("rating", [])]
            recs = [r for it, r in arms.get("recognition", [])]
            finish = collections.Counter(str(getattr(r, "finish", "")) for _, r in choice)
            stops = {"names_hidden_picks_ignore_specs": follows < 2,
                     "over_2_per_cent_without_a_letter": unread / max(len(choice), 1) > 0.02,
                     "one_position_or_letter_over_80_per_cent": (max(pos.values()) / len(picks) > 0.8 or max(let.values()) / len(picks) > 0.8) if picks else True}
            mres[cat] = {"choice_answers": len(choice), "without_a_letter": unread,
                         "without_a_letter_pct": round(100 * unread / max(len(choice), 1), 2),
                         "picks_by_position_pct": {k: round(100 * v / len(picks), 1) for k, v in sorted(pos.items())} if picks else {},
                         "picks_by_letter_pct": {k: round(100 * v / len(picks), 1) for k, v in sorted(let.items())} if picks else {},
                         "names_hidden_terms": spec, "attributes_followed": follows,
                         "rating_answers": len(ratings), "rating_read": sum(1 for r in ratings if str(getattr(r, "rating", "")).strip() not in ("", "None", "nan")),
                         "recognition_answers": len(recs), "recognition_read": sum(1 for r in recs if str(getattr(r, "recognized", "")) in ("0", "1")),
                         "finish_reasons": dict(finish), "stops": stops, "stop": any(stops.values())}
            for arm in ("shown", "hidden", "repeat", "rating", "premium", "recognition"):
                rows = arms.get(arm, [])
                for k in rng.choice(len(rows), min(4, len(rows)), replace=False) if rows else []:
                    it, r = rows[k]
                    rt = getattr(r, "rating", "")
                    reading.append({"model": model, "category": cat, "arm": arm, "id": it["id"], "letter": r.letter,
                                    "rating": "" if rt is None or (isinstance(rt, float) and math.isnan(rt)) else str(rt),
                                    "recognized": getattr(r, "recognized", ""),
                                    "answer": str(r.answer)[:600]})
        res[model] = mres
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "STOPS.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    with open(out / "reading_sample.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in reading:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return res


# ---------------------------------------------------------------- simulation (plan, section 8.1)

def simulate(items, reps, draws_for_coverage=0):
    """Answers drawn from a multinomial logit with known name intercepts on the shown sets; recovery of MBBE."""
    rng = np.random.default_rng(SEED)
    shown = [it for it in items.values() if it["cell"] == "shown"]
    cats = collections.defaultdict(list)
    for it in shown:
        cats[it["category"]].append(it)
    rows, cover, corr = [], [], []
    for rep in range(reps):
        true_all, est_all = [], []
        for cat, its in sorted(cats.items()):
            d = Design(its)
            truth = {n: v for n, v in zip(d.familiar, np.linspace(0.6, 0.0, len(d.familiar)))}
            truth.update({n: v for n, v in zip(d.invented, np.linspace(-0.3, -0.1, len(d.invented)))})
            beta = np.zeros(len(d.terms))
            for a in range(3):
                beta[d.col[f"a{a}_l1"]], beta[d.col[f"a{a}_l2"]] = 0.5, 1.0
            beta[d.col["rating"]] = 0.3
            beta[d.col["log_price"]] = -2.0
            for n in d.name_cols:
                beta[d.col[f"name:{n}"]] = truth[n] - truth[d.ref]
            X, _ = d.matrix(its, ["A"] * len(its))
            u = X @ beta
            P = np.exp(u - u.max(1, keepdims=True))
            P /= P.sum(1, keepdims=True)
            y = np.array([rng.choice(5, p=p) for p in P])
            b, cov, _ = fit_clogit(X, y)
            m = mbbe_from(d, b, cov)
            inv_mean = np.mean([truth[n] for n in d.invented])
            for n in d.names:
                t = truth[n] - inv_mean
                e, se = m[n]["mbbe"], m[n]["se"]
                cover.append(abs(e - t) <= 1.96 * se)
                rows.append({"rep": rep, "category": cat, "name": n, "kind": m[n]["kind"], "true": t, "est": e, "se": se})
                true_all.append(t)
                est_all.append(e)
        corr.append(float(np.corrcoef(true_all, est_all)[0, 1]))
    d = pd.DataFrame(rows)
    out = {"replications": reps, "sets_per_category": {c: len(v) for c, v in cats.items()},
           "assumed": "attribute levels +0.5 and +1.0, rating +0.3 per 0.2 stars, log price -2.0, familiar intercepts 0.6 to 0.0, invented -0.3 to -0.1",
           "correlation_true_estimated_mean": float(np.mean(corr)), "correlation_min": float(np.min(corr)),
           "coverage_95_wald": float(np.mean(cover)), "mean_se_familiar": float(d[d.kind == "familiar"].se.mean()),
           "bias_mean": float((d.est - d.true).mean())}
    out["passes"] = bool(out["correlation_true_estimated_mean"] >= 0.9 and 0.90 <= out["coverage_95_wald"] <= 0.98)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--answers")
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--first-job", action="store_true", help="the plan's section 8.2 stop rules and a reading sample")
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--splits", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1, help="")
    ap.add_argument("--out", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure"))
    a = ap.parse_args()
    items = load_items(a.items)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.first_job:
        res = first_job(items, load_answers(a.answers), out / "first-job")
        print(json.dumps({m: {c: {k: v[k] for k in ("without_a_letter_pct", "attributes_followed", "stops", "stop")} for c, v in cats.items()}
                          for m, cats in res.items()}, indent=1))
        return 0
    if a.simulate:
        res = simulate(items, a.reps)
        name = "simulation.json"
    else:
        ans = load_answers(a.answers)
        res = analyse(items, ans, a.draws, a.splits, a.workers)
        halves = res.pop("_halves")
        rng = np.random.default_rng(SEED + 1)
        res["convergence"], cells = convergence(res, a.draws, rng, halves)
        res["discriminant"] = discriminant(cells, a.draws, rng, pair_reliability(halves, included(res)))
        res["independence_from_profiles"] = independence(res, items, ans)
        res["corpus_table_prediction"] = corpus_table_prediction(res, a.draws, rng)
        cells.to_csv(out / "cells.csv", index=False, lineterminator="\n")
        name = "numbers.json"
    res["_meta"] = {"script": "study2b-how-much-a-familiar-brand-is-worth/code/measure/analyze_mbbe.py", "items": a.items, "seed": SEED, "plan": "study2b-how-much-a-familiar-brand-is-worth/materials/price/measure_pilot_plan.md"}
    with open(out / name, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
        fh.write("\n")
    print(json.dumps({k: v for k, v in res.items() if k != "models"}, indent=1, default=str)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
