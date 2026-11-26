"""The full measure's analysis (ANALYSIS-PLAN-2.md with its Revision 1; DESIGN-2.md, sections 4 and 5).

    not in V1). A familiar brand's value at a point x of centred log price is its intercept plus
its slope times x, minus the reference's mean intercept; at its own band, x is its band centre's log price minus the
market centre's. The reference is the invented names that the model does not claim to know, by the pretest's rule
(DESIGN-2.md, section 13, item 14): the open models' claims come from the pretest's analysis (--pretest), the other
models' from their responses to the 68 recognition items (--recognition-items, read from --answers). Units, each with
the condition under which it exists:
- the share premium: 100 (e^v / (e^v + 4) - 0.2), every cell;
- the price premium: 100 (exp(v / |own|) - 1) per cent, and that share of the band centre in dollars, where the brand's
  own price coefficient (the main coefficient plus its slope) has a 95 per cent interval below zero;
- the rating equivalent: v divided by the coefficient per star (the top rating dummy over 0.4 stars), where that
  coefficient's interval lies above zero, and not where the model recommends the lowest rating beside a higher-rated
  product in under 1 per cent of the lists that offer that choice (DESIGN-2.md, section 13, item 15; the cell is
  marked with the count);
- the direct premium (the premium lists): the premium at which the brand's share of five identical products falls to
  one in five; with rivals at 10 per cent steps it shows whether a model pays more than 10 per cent for the brand, not
  where under 10 per cent its premium lies (item 17).
Intervals: a bootstrap over lists within each model, category and version (each model's own generator, seeded from
20261121 and its key). The second fit replaces each familiar name's slope by a term for each price level (the curve).
Versions are compared with the main fit read at the same point (V1 at the market centre, V2 at the pilot band's centre,
V3 to V6 at the own band). Reliability within a category is the mean of the split-half correlations and its
Spearman-Brown value; a model's is the Spearman-Brown value of the mean of its categories' half correlations (item 16).
Groups of models are compared in the rating equivalent, or in the price premium where a model's rating equivalent is
not estimable. Writes <out>/numbers.json and cells.csv.
"""
import argparse
import collections
import gzip
import hashlib
import json
import math
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PKG = REPO = HERE.parents[2]   # the package
sys.path.insert(0, str(HERE))
sys.path.insert(0, str((PKG / "common/parse_answer.py").parent))   # parse_answer.py and decline.py
import analyze_mbbe as A  # noqa: E402  (fit_clogit, read_answer_files)
from decline import classify  # noqa: E402  (a response without a letter: a decline, which is an outcome, or unread)
from parse_answer import final_answer, pick  # noqa: E402

SEED = 20261121
STAR_STEP = 0.4  # the top rating level lies 0.4 stars above the base level (4.6 against 4.2)


def model_rng(model):
    return np.random.default_rng([SEED, int(hashlib.sha256(model.encode()).hexdigest()[:8], 16)])


def group_of(model):
    m = model.lower()
    return "claude" if m.startswith("claude") else "gpt" if m.startswith("gpt-6") or m.startswith("gpt6") else "open"


# ---------------------------------------------------------------- the design matrix

class Design:
    def __init__(self, items, market_centre, prices=True, by_level=False, n_levels=6):
        names = collections.OrderedDict()
        for it in items:
            for p in it["products"].values():
                names.setdefault(p["name"], p["name_kind"])
        self.familiar = sorted(n for n, k in names.items() if k == "familiar")
        self.invented = sorted(n for n, k in names.items() if k == "invented")
        self.base = self.invented[0]
        self.reference = list(self.invented)  # set by analyse() from the model's claims (reference_for)
        self.k = len(next(iter(items))["products"])
        self.prices, self.by_level, self.n_levels = prices, by_level, n_levels
        self.lc = math.log(market_centre)
        t = [f"a{a}_l{l}" for a in range(3) for l in (1, 2)] + ["rating_l1", "rating_l2"]
        if prices and not by_level:
            t.append("logp")
        if prices and by_level:
            t += [f"plevel_{l}" for l in range(1, n_levels)]
        t += [f"pos{p}" for p in range(2, self.k + 1)] + [f"letter_{L}" for L in "ABCDE"[1:self.k]]
        t += [f"name:{n}" for n in self.familiar + self.invented if n != self.base]
        if prices and not by_level:
            t += [f"slope:{n}" for n in self.familiar]
        if prices and by_level:
            t += [f"level:{n}:{l}" for n in self.familiar for l in range(1, n_levels)]
        self.terms = t
        self.ix = {x: i for i, x in enumerate(t)}

    def matrix(self, items, letters):
        X = np.zeros((len(items), self.k, len(self.terms)))
        y = np.zeros(len(items), dtype=int)
        for r, (it, L) in enumerate(zip(items, letters)):
            order = sorted(it["products"])
            for j, key in enumerate(order):
                p = it["products"][key]
                for a, lv in enumerate(p["levels"]):
                    if lv > 0:
                        X[r, j, self.ix[f"a{a}_l{lv}"]] = 1
                rl = [4.2, 4.4, 4.6].index(round(p["rating"], 1))
                if rl > 0:
                    X[r, j, self.ix[f"rating_l{rl}"]] = 1
                x = math.log(p["price"]) - self.lc
                if self.prices and not self.by_level:
                    X[r, j, self.ix["logp"]] = x
                if self.prices and self.by_level and p["price_level"] > 0:
                    X[r, j, self.ix[f"plevel_{p['price_level']}"]] = 1
                if p["position"] > 1:
                    X[r, j, self.ix[f"pos{p['position']}"]] = 1
                if key != "A":
                    X[r, j, self.ix[f"letter_{key}"]] = 1
                if p["name"] != self.base:
                    X[r, j, self.ix[f"name:{p['name']}"]] = 1
                if p["name"] in self.familiar and self.prices and not self.by_level:
                    X[r, j, self.ix[f"slope:{p['name']}"]] = x
                if p["name"] in self.familiar and self.prices and self.by_level and p["price_level"] > 0:
                    X[r, j, self.ix[f"level:{p['name']}:{p['price_level']}"]] = 1
            y[r] = order.index(L)
        return X, y

    def ref(self, b):
        """The mean intercept of the reference's invented names (the base invented name's intercept is zero)."""
        return np.mean([0.0 if n == self.base else b[self.ix[f"name:{n}"]] for n in self.reference])

    def value(self, b, brand, x):
        v = b[self.ix[f"name:{brand}"]] - self.ref(b)
        if self.prices and not self.by_level:
            v += b[self.ix[f"slope:{brand}"]] * x
        return v

    def value_at_level(self, b, brand, level):
        v = b[self.ix[f"name:{brand}"]] - self.ref(b)
        return v + (b[self.ix[f"level:{brand}:{level}"]] if level > 0 else 0.0)

    def own_price(self, b, brand):
        return b[self.ix["logp"]] + b[self.ix[f"slope:{brand}"]]

    def per_star(self, b):
        return b[self.ix["rating_l2"]] / STAR_STEP


def share_premium(v):
    """100 (e^v / (e^v + 4) - 0.2), written as 1 / (1 + 4 e^-v) so that no value overflows."""
    return 100 * (1.0 / (1.0 + 4.0 * math.exp(-v)) - 0.2) if v > -700 else -20.0


# ---------------------------------------------------------------- one cell

def fit_clogit(X, y, ridge=1e-6, iters=100):
    """The pretest's Newton-Raphson (analyze_mbbe.fit_clogit, which is left unchanged) with step halving: a step that
    lowers the penalized log-likelihood is halved until it does not (at most 40 times). Where the maximum exists the
    result is the pretest's. Where a level is never chosen (separation), its coefficient has no finite estimate, and a
    full step can overshoot so far that every coefficient runs away: Fable 5.1 recommended light cushioning in 1 of
    800 running-shoe lists, and in 2 of 200 bootstrap draws, which left that list out, all coefficients reached about
    10^8. With the halving, the separated coefficient grows slowly while the others converge.
    Returns (coefficients, covariance, log-likelihood)."""
    n, J, K = X.shape
    idx = np.arange(n)

    def loglik(b):
        u = X @ b
        m = u.max(1, keepdims=True)
        return float((u[idx, y] - (m[:, 0] + np.log(np.exp(u - m).sum(1)))).sum())

    def grad_hess(b):
        u = X @ b
        u -= u.max(1, keepdims=True)
        P = np.exp(u)
        P /= P.sum(1, keepdims=True)
        xbar = np.einsum("nj,njk->nk", P, X)
        g = (X[idx, y] - xbar).sum(0) - ridge * b
        D = X - xbar[:, None, :]
        return g, -np.einsum("nj,njk,njl->kl", P, D, D) - ridge * np.eye(K)

    b = np.zeros(K)
    cur = loglik(b) - 0.5 * ridge * b @ b
    for _ in range(iters):
        g, H = grad_hess(b)
        step = np.linalg.solve(H, g)
        t = 1.0
        for _ in range(40):
            nb = b - t * step
            new = loglik(nb) - 0.5 * ridge * nb @ nb
            if new >= cur - 1e-10:
                break
            t /= 2
        b, cur = nb, new
        if np.abs(t * step).max() < 1e-9:
            break
    _, H = grad_hess(b)
    return b, np.linalg.inv(-H), loglik(b)


def fit_cell(items, letters, d):
    keep = [(it, L) for it, L in zip(items, letters) if L in it["products"]]
    X, y = d.matrix([it for it, _ in keep], [L for _, L in keep])
    b, cov, ll = fit_clogit(X, y)
    return X, y, b, cov


def boot(X, y, d, draws, rng):
    out = []
    n = len(y)
    for _ in range(draws):
        ix = rng.integers(0, n, n)
        try:
            bb, _, _ = fit_clogit(X[ix], y[ix])
        except np.linalg.LinAlgError:
            continue
        out.append(bb)
    return np.array(out)


def ci(a):
    a = np.asarray([x for x in a if x is not None and np.isfinite(x)])
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) else [None, None]


def ci_unbounded(a):
    """ci() for draws that can be infinite (a price premium whose own price coefficient is near zero in a draw): the
    same numbers as ci() when every draw is finite; otherwise numpy's linear percentile on the sorted draws, where a
    bound that reaches an infinite draw is infinite (ci() would drop those draws and understate the interval)."""
    vals = [float(x) for x in a if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if all(math.isfinite(x) for x in vals):
        return ci(vals)
    s = sorted(vals)

    def pct(q):
        h = (len(s) - 1) * q / 100
        lo, hi = math.floor(h), math.ceil(h)
        if math.isinf(s[lo]) or (hi != lo and math.isinf(s[hi])):
            return s[hi] if math.isinf(s[hi]) else s[lo]
        return s[lo] + (s[hi] - s[lo]) * (h - lo)
    return [pct(2.5), pct(97.5)] if s else [None, None]


PREMIUM_EXP_LIMIT = 700.0  # math.exp overflows a little above 709


def premium_pct(z, o):
    """The price premium in percent, 100 (e^(z / |o|) - 1), for a value z and an own price coefficient o. Where o is so
    close to zero that the ratio exceeds the float range (b21-16, 13580: OverflowError), the premium is infinite, which
    lies beyond the tested prices; at the other end it is -100 percent; o = 0 gives the ratio's sign of infinity."""
    a = abs(o)
    r = z / a if a > 0 else (math.inf if z > 0 else -math.inf if z < 0 else 0.0)
    if r > PREMIUM_EXP_LIMIT:
        return math.inf
    if r < -PREMIUM_EXP_LIMIT:
        return -100.0
    return 100 * (math.exp(r) - 1)


def premium_inside(point_price, pp, tested):
    """The price premium compares the brand at point_price x (1 + pp / 100) with an invented name at point_price; the
    premium is read inside the prices that the version showed only when that price lies between the lowest and the
    highest of them."""
    return bool(tested[0] <= point_price * (1 + pp / 100) <= tested[1])


LOWEST_RATING_SHARE = 0.01  # DESIGN-2.md, section 13, item 15


def lowest_rating_choices(items, letters):
    """(the times the lowest rating was recommended, the lists that offered it beside a higher rating)."""
    low = min(p["rating"] for it in items for p in it["products"].values())
    mixed = [(it, L) for it, L in zip(items, letters) if L in it["products"]
             and any(p["rating"] == low for p in it["products"].values())
             and any(p["rating"] > low for p in it["products"].values())]
    return sum(it["products"][L]["rating"] == low for it, L in mixed), len(mixed)


def rating_rule(items, letters):
    """None when the rating equivalent is estimable; else the marker that stands in its place. A model that recommends
    the lowest rating beside a higher-rated product in under 1 percent of the lists that offer that choice has a
    coefficient for one star with no finite estimate or a very large one, which would push every brand's rating
    equivalent to zero (the four Claude models in coffee makers, 22 November 2026); its rating equivalent in that cell
    is not reported, and the cell is compared on the price premium."""
    h, n = lowest_rating_choices(items, letters)
    if n == 0 or h / n >= LOWEST_RATING_SHARE:
        return None
    return {"lowest_rating_recommended": h, "lists_offering_that_choice": n,
            "rule": "the lowest rating is recommended beside a higher one in under 1 percent of those lists"}


def units(d, b, B, brand, x, centre_price, tested=None, rating_note=None):
    v = d.value(b, brand, x)
    vb = np.array([d.value(bb, brand, x) for bb in B])
    out = {"value": float(v), "value_ci95": ci(vb), "share_premium_pp": share_premium(v),
           "share_premium_ci95": ci([share_premium(z) for z in vb])}
    if d.prices:
        own, ownb = d.own_price(b, brand), np.array([d.own_price(bb, brand) for bb in B])
        defined = ci(ownb)[1] is not None and ci(ownb)[1] < 0
        out["own_price_coefficient"], out["own_price_ci95"] = float(own), ci(ownb)
        if defined:
            pp = premium_pct(v, own)
            ppb = [premium_pct(z, o) for z, o in zip(vb, ownb)]
            out.update({"price_premium_pct": pp, "price_premium_ci95": ci_unbounded(ppb),
                        "price_premium_usd": pp / 100 * centre_price,
                        "price_premium_usd_ci95": [c / 100 * centre_price if c is not None else None for c in ci_unbounded(ppb)]})
            if tested:
                out["price_premium_inside_tested_prices"] = premium_inside(math.exp(d.lc + x), pp, tested)
    ps, psb = d.per_star(b), np.array([d.per_star(bb) for bb in B])
    if rating_note:
        out["rating_equivalent_not_estimable"] = rating_note
    elif ci(psb)[0] is not None and ci(psb)[0] > 0:
        out["rating_equivalent_stars"] = float(v / ps)
        out["rating_equivalent_ci95"] = ci([z / p for z, p in zip(vb, psb)])
        out["_rating_draws"] = [float(z / p) for z, p in zip(vb, psb)]
    if "price_premium_pct" in out:
        out["_price_draws"] = [float(premium_pct(z, o)) for z, o in zip(vb, ownb)]
    return out


def spearman_brown(r):
    return 2 * r / (1 + r) if r > -1 else -1.0


def spearman(a, b):
    """Spearman's correlation as the Pearson correlation of the average ranks, which is what pandas' method="spearman"
    computes, without scipy. NaN when either series is constant."""
    ra, rb = pd.Series(a, dtype=float).rank(), pd.Series(b, dtype=float).rank()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def split_half(items, letters, d, x_of, splits, rng):
    """Within one category: random halves of the lists, each brand's value from each half, and the Spearman correlation
    over the category's familiar brands. Returns the mean of those correlations over the splits and its Spearman-Brown
    value, corrected once (DESIGN-2.md, section 13, item 16: correcting each split and then averaging gave values below
    -1 when a few splits were near -1)."""
    n = len(items)
    rs = []
    for _ in range(splits):
        h = rng.permutation(n)
        vals = []
        for half in (h[: n // 2], h[n // 2:]):
            try:
                _, _, b, _ = fit_cell([items[i] for i in half], [letters[i] for i in half], d)
            except np.linalg.LinAlgError:
                break
            vals.append([d.value(b, br, x_of(br)) for br in d.familiar])
        if len(vals) == 2:
            r = spearman(vals[0], vals[1])
            if np.isfinite(r):
                rs.append(r)
    if not rs:
        return {"half_correlation": None, "spearman_brown": None, "splits": 0}
    m = float(np.mean(rs))
    return {"half_correlation": m, "spearman_brown": spearman_brown(m), "splits": len(rs)}


# ---------------------------------------------------------------- the whole analysis

# ---------------------------------------------------------------- the reference (DESIGN-2.md, section 13, item 14)

def pretest_claims(path):
    """{(model, category, name): share of the model's recognition responses that claim to know the fictitious name},
    for the open models, from the pretest's analysis (numbers.json, recognized_share: a yes that names a country)."""
    out = {}
    if not path or not pathlib.Path(path).exists():
        return out
    d = json.load(open(path, encoding="utf-8"))
    for model, m in d.get("models", {}).items():
        for cat, c in m.get("categories", {}).items():
            for n, s in c.get("names", {}).items():
                if s.get("kind") == "invented" and s.get("recognized_share") is not None:
                    out[(model, cat, n)] = float(s["recognized_share"])
    return out


def recognition_claims(ans, rec_items):
    """The same shares from responses to the recognition questions on the fictitious names (items/full1-recognition/,
    the pretest's own items), read as the pretest read them: a claim is a yes that names a country."""
    from parse_audit import recognition
    rows = ans[ans.id.isin(rec_items)]
    if rows.empty:
        return {}

    def claim(a):
        r, _ = recognition(a if isinstance(a, str) else "")
        return "" if r is None else str(int(bool(r["yes"]) and bool(r["country"])))
    return A.recognition_shares(rec_items, rows.assign(recognized=rows.answer.map(claim)))


def reference_for(model, cat, invented, claims):
    """The fictitious names that stay in this model's reference: those it claims to know in fewer than three of its
    four recognition responses (a name with no response stays). When it claims every one, all stay, with a flag."""
    ref = [n for n in invented if (claims.get((model, cat, n)) or 0.0) < A.CLAIM_SHARE_TO_LEAVE_REFERENCE]
    flag = "" if ref else "every fictitious name is claimed; the reference keeps all of them"
    return (ref or list(invented)), flag


_BY_ID = None


def _set_items(by_id):
    global _BY_ID
    _BY_ID = by_id


def analyse_model(model, g, gates, draws, splits, claims, by_id=None):
    """One model's results in every category and version. Its draws come from model_rng(model), so they do not
    depend on which models are analysed with it, in what order or in which process."""
    by_id = by_id if by_id is not None else _BY_ID
    rng = model_rng(model)
    mres = {}
    for cat, gc in gates["categories"].items():
        mc, centres = gc["market_centre"], gc["band_centres"]
        pilot_x = math.log(math.exp(np.mean(np.log(gc.get("pilot_levels", [mc]))))) - math.log(mc)
        cres = {}
        for version in ["main"] + [v for v in gc["versions"] if v != "main"]:
            rows = [(by_id[i], L) for i, L in zip(g.id, g.letter)
                    if by_id[i]["category"] == cat and by_id[i].get("version") == version and by_id[i]["cell"] == "shown"]
            if len(rows) < 50:
                continue
            its, lets = [r[0] for r in rows], [r[1] for r in rows]
            d = Design(its, mc, prices=version != "V1-no-prices")
            ref, flag = reference_for(model, cat, d.invented, claims)
            d.reference = ref
            X, y, b, cov = fit_cell(its, lets, d)
            Bd = boot(X, y, d, draws, rng)
            own_x = {br: math.log(centres[br]) - math.log(mc) for br in d.familiar}
            point = (lambda br: 0.0) if version == "V1-no-prices" else (lambda br: pilot_x) if version == "V2-pilot-band" else (lambda br: own_x[br])
            shown_prices = [p["price"] for it in its for p in it["products"].values() if p.get("price") is not None]
            tested = (min(shown_prices), max(shown_prices)) if shown_prices and d.prices else None
            note = rating_rule(its, lets)
            brands = {br: units(d, b, Bd, br, point(br), centres[br], tested, note) for br in d.familiar}
            low = lowest_rating_choices(its, lets)
            vres = {"lists": len(rows), "brands": brands, "reference": ref, "reference_flag": flag,
                    "lowest_rating_recommended": {"times": low[0], "lists_offering_that_choice": low[1]},
                    "main_price_coefficient": float(b[d.ix["logp"]]) if d.prices else None,
                    "reliability_within_category": split_half(its, lets, d, point, splits, rng)}
            if version == "main":
                vres["read_at"] = {"market_centre": {br: units(d, b, Bd, br, 0.0, centres[br])["value"] for br in d.familiar},
                                   "pilot_band_centre": {br: units(d, b, Bd, br, pilot_x, centres[br])["value"] for br in d.familiar}}
                vres["_draws"] = {br: {"own": [float(d.value(bb, br, own_x[br])) for bb in Bd],
                                       "market": [float(d.value(bb, br, 0.0)) for bb in Bd],
                                       "pilot": [float(d.value(bb, br, pilot_x)) for bb in Bd]} for br in d.familiar}
                dl = Design(its, mc, prices=True, by_level=True, n_levels=len(gc["price_levels"]))
                dl.reference = ref
                Xl, yl, bl, _ = fit_cell(its, lets, dl)
                vres["curve_by_price_level"] = {br: [float(dl.value_at_level(bl, br, l)) for l in range(len(gc["price_levels"]))]
                                                for br in d.familiar}
            else:
                vres["_draws"] = {br: [float(d.value(bb, br, point(br))) for bb in Bd] for br in d.familiar}
            cres[version] = vres
        if "main" in cres:
            main = cres["main"]
            for version, vres in cres.items():
                if version == "main":
                    continue
                key = "market" if version == "V1-no-prices" else "pilot" if version == "V2-pilot-band" else "own"
                diffs = {}
                for br, dv in vres["_draws"].items():
                    dm = main["_draws"][br][key]
                    m = min(len(dv), len(dm))
                    diffs[br] = {"difference": vres["brands"][br]["value"] - (main["read_at"]["market_centre"][br] if key == "market" else main["read_at"]["pilot_band_centre"][br] if key == "pilot" else main["brands"][br]["value"]),
                                 "ci95": ci(np.array(dv[:m]) - np.array(dm[:m]))}
                vres["against_main"] = diffs
            # ANALYSIS-PLAN-2.md, item 7: the direct premium, beside each brand's price premium, as the answer
            # that needs no price coefficient (the pilot's arm 5: the brand's share at each premium over four
            # rivals at its band centre, and the premium at which that share falls to one in five)
            prem = [(by_id[i], r) for i, r in zip(g.id, g.itertuples(index=False))
                    if by_id[i]["category"] == cat and by_id[i].get("version") == "premium"]
            if prem:
                pa = A.premium_arm(prem)
                for br, u in main["brands"].items():
                    u["direct_premium"] = pa.get(br)
            # ANALYSIS-PLAN-2.md: whether the model follows the specifications in this category (at least two
            # attributes followed, by the stop rules' own check on the main version, without brand names where the
            # model answered such lists); a cell that does not is reported alone and left out of every estimate over
            # models (analyse, below)
            rows = [(by_id[i], L if isinstance(L, str) else "", "") for i, L in zip(g.id, g.letter)
                    if by_id[i]["category"] == cat and by_id[i].get("version") == "main" and by_id[i]["cell"] in ("shown", "hidden")]
            if rows:
                import stop_rules2 as S  # here, not at the top: stop_rules2 imports this module
                c = S.cell(rows, gc)
                main["specifications_check"] = {k: c.get(k) for k in ("specifications_fitted_on", "attributes_best_level_above_zero",
                                                                      "attributes_worst_level_never_recommended", "attributes_followed")}
        if cres:
            mres[cat] = cres
    return mres


def follows_specifications(c):
    """A category of a model enters the estimates over models unless its check found fewer than two attributes
    followed (a category with no check, such as a test's, enters)."""
    n = ((c.get("main") or {}).get("specifications_check") or {}).get("attributes_followed")
    return n is None or n >= 2


def analyse(items, ans, gates, draws, splits, claims=None, workers=1):
    claims = claims or {}
    by_id = {it["id"]: it for it in items}
    ans = ans[ans.id.isin(by_id)]
    res = {"models": {}}
    groups = list(ans.groupby("model"))
    if workers > 1 and len(groups) > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(min(workers, len(groups)), initializer=_set_items, initargs=(by_id,)) as ex:
            futs = [(model, ex.submit(analyse_model, model, g, gates, draws, splits, claims)) for model, g in groups]
            for model, f in futs:
                res["models"][model] = f.result()
    else:
        for model, g in groups:
            res["models"][model] = analyse_model(model, g, gates, draws, splits, claims, by_id)
    read, left = {}, {}
    for model, g in groups:
        dec = g["decline"] if "decline" in g.columns else [False] * len(g)
        ch = [(by_id[i]["products"], L, bool(x)) for i, L, x in zip(g.id, g.letter, dec) if by_id[i]["cell"] in CHOICE_CELLS]
        k = sum(isinstance(L, str) and L in p for p, L, _ in ch)
        nd = sum(x and not (isinstance(L, str) and L in p) for p, L, x in ch)
        n = len(ch) - nd  # the read share is over the choice responses that are not declines
        read[model] = {"choice_items": len(ch), "declines": nd, "with_a_letter": k,
                       "read_pct": round(100 * k / n, 2) if n else None,
                       "decline_pct": round(100 * nd / len(ch), 2) if ch else None}
        if n and k / n < A.READ_RULE:
            left[model] = read[model]
    res["choice_items_read"] = read
    res["left_out"] = {"rule": RULE_TEXT, "models": left}
    # ANALYSIS-PLAN-2.md: a category in which a model does not follow the specifications is reported alone and left out
    # of every summary across models and of the comparisons between models
    res["cells_left_out"] = [{"model": m, "category": c, **v["main"]["specifications_check"]}
                             for m, mres in sorted(res["models"].items()) for c, v in sorted(mres.items())
                             if not follows_specifications(v)]
    kept = {"models": {m: {c: v for c, v in mres.items() if follows_specifications(v)}
                       for m, mres in res["models"].items() if m not in left}}
    res["pooled_reliability"] = pooled_reliability(res)
    res["groups"] = group_comparisons(kept)
    res["over_models"] = over_models(kept, gates)
    return res


CHOICE_CELLS = ("shown", "hidden", "repeat", "premium")
RULE_TEXT = ("A model whose responses the parser reads in under 90 percent of the choice items that it received (the "
             "choice sets with and without brand names, the repeated sets and the direct premium's sets), not counting "
             "the responses that decline to recommend any product, which are an outcome (common/decline.py), is "
             "reported apart, with its own estimates, and left out of every estimate over models (the open-models "
             "rule, models/open_models_plan.md, which the pretest also applied).")


def summarize(points, draws, rng):
    """The mean and the median of points over models, each with a 95 percent interval from a two-way bootstrap: for
    each of the models' bootstrap draws (over choice sets), the models are drawn again with replacement and each drawn
    model contributes that draw of its own."""
    points = np.asarray(points, float)
    m = min(len(d) for d in draws)
    D = np.array([np.asarray(d, float)[:m] for d in draws])
    k = len(points)
    means, medians = np.empty(m), np.empty(m)
    for j in range(m):
        vals = D[rng.integers(0, k, k), j]
        means[j], medians[j] = vals.mean(), np.median(vals)
    return {"mean": float(points.mean()), "mean_ci95": ci_unbounded(means), "median": float(np.median(points)),
            "median_ci95": ci_unbounded(medians)}


def over_models(res, gates):
    """For each brand and category, over every model and within each group of models (Claude, GPT, open): the share
    premium in points, which every model has, and the price premium in percent and in dollars at the brand's band
    centre, over only the models whose own price premium lies inside the tested prices, with the models beyond those
    prices and the models without a price premium counted beside it.
    A model's price premium in dollars is its percent times the band centre's price; its flag is on its point
    estimate only, so a model inside the tested prices can have an interval that reaches beyond them."""
    per = collections.defaultdict(list)
    for model, mres in res["models"].items():
        for cat, c in mres.items():
            if "main" in c:
                for br, u in c["main"]["brands"].items():
                    per[(cat, br)].append((model, u, c["main"]["_draws"][br]["own"]))
    rng = np.random.default_rng(SEED)
    out = {}
    for (cat, br), rows in sorted(per.items()):
        gc = gates["categories"][cat]
        centre = gc["band_centres"][br]
        tested = (min(gc["price_levels"]), max(gc["price_levels"]))
        groups = {"all": rows, **{g: [x for x in rows if group_of(x[0]) == g] for g in ("claude", "gpt", "open")}}
        entry = {}
        for g, sub in groups.items():
            if not sub:
                continue
            e = {"models": len(sub), "share_premium_pp": summarize(
                [u["share_premium_pp"] for _, u, _ in sub], [[share_premium(z) for z in d] for _, _, d in sub], rng)}
            inside = [u for _, u, _ in sub if u.get("price_premium_inside_tested_prices") is True and "_price_draws" in u]
            pe = {"models_inside_tested_prices": len(inside),
                  "models_beyond_tested_prices": sum(u.get("price_premium_inside_tested_prices") is False for _, u, _ in sub),
                  "models_without_a_price_premium": sum("price_premium_pct" not in u for _, u, _ in sub),
                  "band_centre_usd": centre}
            if inside:
                s = summarize([u["price_premium_pct"] for u in inside], [u["_price_draws"] for u in inside], rng)
                pe["pct"] = s
                pe["usd"] = {k: ([None if x is None else x * centre / 100 for x in v] if isinstance(v, list) else v * centre / 100)
                             for k, v in s.items()}
                pe["median_inside_tested_prices"] = premium_inside(centre, s["median"], tested)
            e["price_premium"] = pe
            entry[g] = e
        out[f"{cat} | {br}"] = entry
    return out


def pooled_reliability(res):
    """A model's reliability within category (DESIGN-2.md, section 13, item 16): the Spearman-Brown value of the mean,
    over its categories, of each category's mean half correlation; each category's own values are kept beside it, the
    negative ones as they are."""
    out = {}
    for model, mres in res["models"].items():
        per = {cat: c["main"]["reliability_within_category"] for cat, c in mres.items()
               if "main" in c and c["main"]["reliability_within_category"]["half_correlation"] is not None}
        halves = [v["half_correlation"] for v in per.values()]
        m = float(np.mean(halves)) if halves else None
        out[model] = {"mean_half_correlation": m, "spearman_brown_of_the_mean": spearman_brown(m) if m is not None else None,
                      "categories": len(halves), "by_category": per}
    return out


def group_comparisons(res):
    """For each brand and category: each group's mean in the unit of the comparisons between models, with a bootstrap
    interval from the models' own draws, and the GPT minus Claude difference. The unit is the rating equivalent, or the
    price premium where any model's rating equivalent is not estimable in that cell (DESIGN-2.md, section 13, item 15)."""
    per = collections.defaultdict(list)
    for model, mres in res["models"].items():
        for cat, c in mres.items():
            if "main" in c:
                for br, u in c["main"]["brands"].items():
                    per[(cat, br)].append((model, u))
    out = {}
    for (cat, br), mus in per.items():
        if any("rating_equivalent_not_estimable" in u for _, u in mus):
            key, unit = "_price_draws", "price_premium_pct"
        else:
            key, unit = "_rating_draws", "rating_equivalent_stars"
        groups = collections.defaultdict(list)
        for model, u in mus:
            # a price premium enters only when its point lies inside the tested prices (as in over_models)
            if key in u and (key != "_price_draws" or u.get("price_premium_inside_tested_prices") is True):
                groups[group_of(model)].append(np.array(u[key]))
        if not groups:
            continue
        row, means = {"unit": unit}, {}
        if key == "_price_draws":
            row["models_beyond_tested_prices"] = sum(u.get("price_premium_inside_tested_prices") is False for _, u in mus)
        for gname, draws in groups.items():
            m = min(len(x) for x in draws)
            means[gname] = np.mean([x[:m] for x in draws], axis=0)
            row[gname] = {"models": len(draws), "mean": float(np.mean(means[gname])), "ci95": ci(means[gname])}
        if "gpt" in means and "claude" in means:
            m = min(len(means["gpt"]), len(means["claude"]))
            dd = means["gpt"][:m] - means["claude"][:m]
            row["gpt_minus_claude"] = {"difference": float(np.mean(dd)), "ci95": ci(dd)}
        out[f"{cat} | {br}"] = row
    return out


def strip_draws(res):
    for mres in res["models"].values():
        for c in mres.values():
            for v in c.values():
                v.pop("_draws", None)
                for u in v["brands"].values():
                    u.pop("_rating_draws", None)
                    u.pop("_price_draws", None)
    return res


def read_md_answers(root):
    rows = []
    for mdir in sorted(p for p in pathlib.Path(root).iterdir() if p.is_dir()):
        for f in sorted(mdir.glob("*/*.md")):
            if f.name.upper() == "RUN-RECORD.MD":
                continue
            rows.append({"model": mdir.name, "id": f.stem, "answer": f.read_text(encoding="utf-8")})
    return pd.DataFrame(rows, columns=["model", "id", "answer"])


def is_md_root(p):
    p = pathlib.Path(p)
    return p.is_dir() and any(True for _ in p.glob("*/*/*.md"))


def load_answers(spec, text_ids=()):
    """every letter read with final_answer
    before pick. The response's text is kept (column answer) only for the ids in text_ids, the recognition items, so
    that recognition_claims can read them without holding every response in memory."""
    parts = [s for s in str(spec).split(",") if s]
    md = [s for s in parts if is_md_root(s)]
    rest = [s for s in parts if s not in md]
    frames = [A.read_answer_files(",".join(rest))] if rest else []
    frames += [read_md_answers(s) for s in md]
    d = pd.concat(frames, ignore_index=True)
    src = d["raw"] if "raw" in d.columns else d["answer"]
    finals = [final_answer(r if isinstance(r, str) and r not in ("", "nan") else a) for r, a in zip(src, d["answer"])]
    d["letter"] = [pick(f)[0] for f in finals]
    d["decline"] = [not L and isinstance(f, str) and bool(f) and classify(f) == "decline" for L, f in zip(d["letter"], finals)]
    d["answer"] = d["answer"].where(d.id.isin(set(text_ids)), "")
    return d[["model", "id", "letter", "decline", "answer"]]


# ---------------------------------------------------------------- the simulation check (ANALYSIS-PLAN-2, section 3)

def simulate_all(items, gates, reps, seed=SEED):
    out = {c: simulate(items, gates, reps, seed, cat=c) for c in gates["categories"]}
    return {"categories": out, "passes": all(v["passes"] for v in out.values())}


def simulate(items, gates, reps, seed=SEED, cat=None):
    """Answers drawn from a conditional logit with known name intercepts and slopes on the main version's lists of one
    category; the fit must recover the values at the own band (correlation at least 0.9) with 95 per cent intervals
    (from the fit's covariance) holding the truth in 90 to 98 per cent of the brand-replications."""
    rng = np.random.default_rng(seed)
    cat = cat or next(iter(gates["categories"]))
    gc = gates["categories"][cat]
    its = [it for it in items if it["category"] == cat and it.get("version") == "main" and it["cell"] == "shown"]
    d = Design(its, gc["market_centre"])
    fam = d.familiar
    alpha = {n: v for n, v in zip(fam, np.linspace(0.8, -0.1, len(fam)))}
    gamma = {n: v for n, v in zip(fam, np.linspace(0.5, -0.3, len(fam)))}
    inv = {n: (-0.3 if i else 0.0) for i, n in enumerate(d.invented)}
    truth_b = np.zeros(len(d.terms))
    for t in d.terms:
        if t.startswith("a") and "_l" in t:
            truth_b[d.ix[t]] = 0.5 * int(t[-1])
        elif t.startswith("rating_l"):
            truth_b[d.ix[t]] = 0.4 * int(t[-1])
        elif t == "logp":
            truth_b[d.ix[t]] = -1.5
        elif t.startswith("name:"):
            n = t[5:]
            truth_b[d.ix[t]] = alpha.get(n, inv.get(n, 0.0))
        elif t.startswith("slope:"):
            truth_b[d.ix[t]] = gamma[t[6:]]
    X, _ = d.matrix(its, ["A"] * len(its))
    own_x = {br: math.log(gc["band_centres"][br]) - math.log(gc["market_centre"]) for br in fam}
    true_v = np.array([d.value(truth_b, br, own_x[br]) for br in fam])
    cors, hits, n = [], 0, 0
    for _ in range(reps):
        u = X @ truth_b
        p = np.exp(u - u.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        y = np.array([rng.choice(len(pr), p=pr) for pr in p])
        b, cov, _ = fit_clogit(X, y)
        est = np.array([d.value(b, br, own_x[br]) for br in fam])
        cors.append(np.corrcoef(est, true_v)[0, 1])
        for k, br in enumerate(fam):
            gvec = np.zeros(len(b))
            gvec[d.ix[f"name:{br}"]] = 1.0
            gvec[d.ix[f"slope:{br}"]] = own_x[br]
            for nn in d.reference:
                if nn != d.base:
                    gvec[d.ix[f"name:{nn}"]] -= 1.0 / len(d.reference)
            se = math.sqrt(max(gvec @ cov @ gvec, 0))
            hits += abs(est[k] - true_v[k]) <= 1.96 * se
            n += 1
    out = {"category": cat, "reps": reps, "correlation_true_estimated_mean": float(np.mean(cors)), "coverage_95": hits / n}
    out["passes"] = bool(out["correlation_true_estimated_mean"] >= 0.9 and 0.90 <= out["coverage_95"] <= 0.98)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--gates", required=True)
    ap.add_argument("--answers")
    ap.add_argument("--out", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1"))
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--splits", type=int, default=200)
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--pretest", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/pretest_numbers.json"))
    ap.add_argument("--recognition-items", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1-recognition/items.jsonl"))
    ap.add_argument("--models", help="comma-separated model keys to analyse (all models with responses when absent)")
    ap.add_argument("--workers", type=int, default=1, help="models analysed in parallel processes")
    a = ap.parse_args()
    items = [json.loads(l) for l in (gzip.open(a.items, "rt", encoding="utf-8") if a.items.endswith(".gz")
                                     else open(a.items, encoding="utf-8"))]
    gates = json.load(open(a.gates, encoding="utf-8"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.simulate:
        res = simulate_all(items, gates, a.reps)
        (out / "simulation.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(res, indent=1))
        return 0 if res["passes"] else 1
    rec = {it["id"]: it for it in map(json.loads, open(a.recognition_items, encoding="utf-8"))}
    ans = load_answers(a.answers, text_ids=rec)
    if a.models:
        keep = a.models.split(",")
        missing = sorted(set(keep) - set(ans.model))
        if missing:
            raise SystemExit(f"REFUSED: no responses for {missing}")
        ans = ans[ans.model.isin(keep)]
    claims = pretest_claims(a.pretest)
    claims.update(recognition_claims(ans, rec))  # a model's own responses to the 68 items, where it has them
    res = strip_draws(analyse(items, ans, gates, a.draws, a.splits, claims, a.workers))
    res["_meta"] = {"script": "study2b-how-much-a-familiar-brand-is-worth/code/measure/analyze_mbbe2.py", "items": a.items, "seed": SEED, "draws": a.draws,
                    "splits": a.splits, "plan": "study2b-how-much-a-familiar-brand-is-worth/materials/price/measure_plan.md", "pretest_claims": a.pretest,
                    "recognition_items": a.recognition_items, "answers": a.answers, "models": sorted(set(ans.model))}
    (out / "numbers.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8", newline="\n")
    rows = []
    for model, mres in res["models"].items():
        for cat, c in mres.items():
            for version, v in c.items():
                for br, u in v["brands"].items():
                    rows.append(dict(model=model, group=group_of(model), category=cat, version=version, brand=br,
                                     **{k: u.get(k) for k in ("value", "share_premium_pp", "price_premium_pct", "price_premium_usd",
                                                              "rating_equivalent_stars")},
                                     direct_premium_pct=(u.get("direct_premium") or {}).get("premium_at_one_in_five")))
    pd.DataFrame(rows).to_csv(out / "cells.csv", index=False, lineterminator="\n")
    print(f"{len(res['models'])} models, {len(rows)} brand cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
