"""The models with open weights on the strictly better tables, without the three tables whose invented name turned out
to be the name of a real company (Novatech in laptops 02, Primebook in laptops 03, Sonance in earbuds 02).

It applies the definitions of 10_open_models.py unchanged (the best-product share in each cell averaged over the price
levels; the name gap with no information and with it, and its change; tables weighted equally within a model, then
models; two-way cluster bootstrap, 2,000 draws, seed 20261120, seeded afresh here), and gives each interval its
two-sided P value from the same draws. The row with every table is in study1a-tables-with-one-optimal-product/results/open_models.json
(tables_of_study1, strictly-better-tables). Writes study1a-tables-with-one-optimal-product/results/open_models_robustness.json.

    python study1a-tables-with-one-optimal-product/code/11_open_models_robustness.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import importlib.util
import json
import random
import sys
import pathlib

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("open_models", HERE / "10_open_models.py")
AO = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AO)

DROP = {"sr_laptops_02_dom", "sr_laptops_03_dom", "sr_earbuds_02_dom"}
OUT = AO.REPO / "study1a-tables-with-one-optimal-product" / "results" / "open_models_robustness.json"


def boot_draws(by_model, rng):
    """The draws of 10_open_models.py's boot, made by the same loop from the same generator, kept as a sorted list."""
    models = list(by_model)
    tables = sorted({t for d in by_model.values() for t in d})
    est = []
    for _ in range(AO.DRAWS):
        ms = [rng.choice(models) for _ in models]
        ts = [rng.choice(tables) for _ in tables]
        vals = []
        for m in ms:
            v = [by_model[m][t] for t in ts if t in by_model[m]]
            if v:
                vals.append(sum(v) / len(v))
        if vals:
            est.append(sum(vals) / len(vals))
    est.sort()
    return est


def with_p(summary, draws):
    """10_open_models.py's summary with the two-sided P value of the same draws (twice the share on the far side of
    zero), after a check that the draws give the same interval."""
    n = len(draws)
    ci = [round(100 * draws[int(0.025 * n)], 2), round(100 * draws[int(0.975 * n) - 1], 2)]
    if ci != summary["ci95"]:
        raise SystemExit(f"the reproduced draws give {ci}, not {summary['ci95']}")
    p = min(1.0, 2 * min(sum(v <= 0 for v in draws) / n, sum(v >= 0 for v in draws) / n))
    return {**summary, "p_two_sided": round(p, 4), "draws_on_the_far_side_of_zero": min(sum(v <= 0 for v in draws),
                                                                                          sum(v >= 0 for v in draws))}


def main():
    cells, _parsed = AO.load(AO.COUNTS)
    sh = AO.table_shares(cells, "strictly-better-tables")
    sh = {m: {t: cs for t, cs in ts.items() if t not in DROP} for m, ts in sh.items()}
    g0 = AO.contrast(sh, ("hidden", "0"), ("original", "0"))
    g1 = AO.contrast(sh, ("hidden", "1"), ("original", "1"))
    change = {m: {t: g1[m][t] - g0[m][t] for t in g0[m] if t in g1.get(m, {})} for m in g0 if m in g1}
    rng = random.Random(AO.SEED)
    rng2 = random.Random(AO.SEED)          # the same draws again, in the same order, for the P values
    s0, s1, sc = AO.summarize(g0, rng), AO.summarize(g1, rng), AO.summarize(change, rng)
    d0, d1, dc = boot_draws(g0, rng2), boot_draws(g1, rng2), boot_draws(change, rng2)
    res = {"source": {"script": "study1a-tables-with-one-optimal-product/code/11_open_models_robustness.py",
                      "counts": "study1a-tables-with-one-optimal-product/results/open_models_counts.csv",
                      "definitions": "study1a-tables-with-one-optimal-product/code/10_open_models.py",
                      "p_values": "two-sided, from the same 2,000 draws as each interval (seed 20261120)"},
           "without_invented_real": {"tables_left_out": sorted(DROP),
                                     "tables": len({t for d in g0.values() for t in d}),
                                     "gap_no_information": with_p(s0, d0),
                                     "gap_with_information": with_p(s1, d1),
                                     "change": with_p(sc, dc)}}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    r = res["without_invented_real"]
    print(f"strictly better tables without the three ({r['tables']} tables): gap {r['gap_no_information']['points']} "
          f"{r['gap_no_information']['ci95']}, with information {r['gap_with_information']['points']} "
          f"{r['gap_with_information']['ci95']}, change {r['change']['points']} {r['change']['ci95']}")


if __name__ == "__main__":
    main()
