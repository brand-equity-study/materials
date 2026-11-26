"""The store's contrasts (Study 1c), the functions that pool_all.py uses on the cells files: for a model, a table, an
arm and a name version, the share of parsed answers that pick the best product; the name gap g(arm) and the change
D(arm) = g(arm) - g(plain), with the two-way bootstrap over tables and models.
"""
from collections import defaultdict


SEED = 20261120


REF = "plain"


def per_mt(c, fn):
    """{(model, table): value} where fn(c, model, table) gives a value or None."""
    keys = {(m, t) for (m, t, _, _) in c}
    out = {}
    for m, t in sorted(keys):     # sorted, so that the result does not depend on PYTHONHASHSEED
        v = fn(c, m, t)
        if v is not None:
            out[(m, t)] = v
    return out


def s_of(c, m, t, arm, names, which=1):
    n = c.get((m, t, arm, names))
    return n[which] / n[0] if n and n[0] else None


def gap(arm):
    def f(c, m, t):
        h, o = s_of(c, m, t, arm, "hidden"), s_of(c, m, t, arm, "original")
        return None if h is None or o is None else h - o
    return f


def change(arm):
    def f(c, m, t):
        g1, g0 = gap(arm)(c, m, t), gap(REF)(c, m, t)
        return None if g1 is None or g0 is None else g1 - g0
    return f


def pooled(vals):
    by = defaultdict(list)
    for (m, t), v in vals.items():
        by[m].append(v)
    per = {m: sum(x) / len(x) for m, x in by.items()}
    return (sum(per.values()) / len(per) if per else None), per


def bootstrap(vals, draws):
    """Two-way cluster bootstrap over tables and models: 95 per cent interval, 90 per cent interval, two-sided P."""
    import numpy as np
    if not vals:
        return None
    mods = sorted({m for m, t in vals})
    tabs = sorted({t for m, t in vals})
    if len(tabs) < 3:
        return None
    mi = np.array([mods.index(m) for m, t in vals])
    ti = np.array([tabs.index(t) for m, t in vals])
    x = np.array(list(vals.values()), dtype=float)
    rng = np.random.default_rng(SEED)
    out = []
    for _ in range(draws):
        wt = np.bincount(rng.integers(0, len(tabs), len(tabs)), minlength=len(tabs))
        wm = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods))
        w = wt[ti]
        num = np.bincount(mi, weights=w * x, minlength=len(mods))
        den = np.bincount(mi, weights=w, minlength=len(mods))
        ok = (den > 0) & (wm > 0)
        if ok.any():
            per = num[ok] / den[ok]
            out.append(float(np.sum(per * wm[ok]) / np.sum(wm[ok])))
    v = np.sort(np.array(out))
    return {"low95": float(np.quantile(v, 0.025)), "high95": float(np.quantile(v, 0.975)),
            "low90": float(np.quantile(v, 0.05)), "high90": float(np.quantile(v, 0.95)),
            "p_two_sided": float(min(1.0, 2 * min(np.mean(v <= 0), np.mean(v >= 0)))), "draws": len(out)}


def estimate(vals, draws):
    e, per = pooled(vals)
    return {"pooled": e, "per_model": per, "tables_per_model": dict(pd_count(vals)),
            "interval": bootstrap(vals, draws) if draws else None}


def estimate_groups(groups, draws, workers=1):
    """{group: {key: estimate}} for {group: {key: vals}}. With workers > 1 the bootstraps run in that many processes;
    each bootstrap draws from its own generator seeded with SEED, so the numbers are the same as with one process (a
    job on the computing cluster uses this)."""
    out = {g: {k: estimate(v, 0) for k, v in d.items()} for g, d in groups.items()}
    if not draws:
        return out
    keys = [(g, k) for g, d in groups.items() for k in d]
    vals = [groups[g][k] for g, k in keys]
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(workers) as ex:
            ivs = list(ex.map(bootstrap, vals, [draws] * len(vals)))
    else:
        ivs = [bootstrap(v, draws) for v in vals]
    for (g, k), iv in zip(keys, ivs):
        out[g][k]["interval"] = iv
    return out


def pd_count(vals):
    c = defaultdict(int)
    for m, t in vals:
        c[m] += 1
    return c
