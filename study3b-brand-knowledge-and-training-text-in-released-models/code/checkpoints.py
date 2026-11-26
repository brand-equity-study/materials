"""Study 3, public checkpoints: where in training the lean toward a famous name appears, from letter probabilities.

Public checkpoints of OLMo 2 7B (nine points of pretraining, the released base model, and the models after instruction
tuning, preference tuning and the released Instruct model), Qwen 2.5 7B and Llama 3.1 8B were scored on five-option
decision pages. In the tie rung two options carry identical records; one (the twin) has a famous name and one (the
winner) an unfamiliar name. Each page was scored three times, with every name shown (N), with every name field removed
(H), and with the twin's famous name replaced by an unfamiliar one (P), always in the same order with the same letters.
For each page the score files hold the probability of each answer letter as the next token.

Files read, all in study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/: trials.jsonl.gz (which page is which version of which trial), pages.jsonl.gz
(the page texts, used for the pairing checks), the 22 files scores/<model>_<format>.csv.gz, and table_split.csv.gz (which
tables were held out).

Definitions:
  L_X = ln p_X(twin letter) - ln p_X(winner letter), probabilities floored at 1e-30, raw (not renormalised) p.
  D   = L_N - L_H per trial (the name effect); D - D^P = L_N - L_P (the placebo condition).
  share points = 100 * (p(a)/(p(a)+p(b)) named minus hidden).
  Unit of inference: table mean over repetitions, then domain mean over tables (12 builder domains plus products = 13),
  then a one-sample t over the 13 domain means, 12 df; the 95 per cent interval is the t interval on those means.
  Products alone: mean of the 26 holdout product tables' means, CR1 cluster-robust SE clustered by twin brand, t with
  G - 1 df; Holm across the two models.
  Post-training steps: per-trial D(later) - D(earlier), plain format, holdout tables, matched by trial; same
  domain-level test, two-sided; Holm across base-to-instruction-tuning, instruction-to-preference tuning and
  preference-tuning-to-released-Instruct.
  Pretraining trajectory: all 250 tables, repetitions 1 to 4 for every point, plain format; 95 per cent t interval over
  the 13 domain means.
  Holdout tables: builder tables marked "confirm" in table_split.csv.gz; product tables whose
  int(sha256("origin-split|"+id)[:8], 16) modulo 4 is not 0. Primary cells use repetitions 1 to 6; the trajectory
  checkpoints (scored only at 1 to 4) use 1 to 4.

    python study3b-brand-knowledge-and-training-text-in-released-models/code/checkpoints.py
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import pathlib
import re
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[2]  # the top of the replication package
DATA = ROOT / "study3b-brand-knowledge-and-training-text-in-released-models" / "data" / "checkpoints"
SPLIT_SHA256_FIXED_IN_ADVANCE = "fac98fabd49ac1dff1453932b3716ced24cf47454f3f41f2ff88b7c598977709"
OUT_DEFAULT = ROOT / "study3b-brand-knowledge-and-training-text-in-released-models" / "results" / "checkpoints.json"

LET = "ABCDE"
FLOOR = 1e-30
SESOI = 0.10
ALPHA = 0.025
PRODUCT_EXPLORATION_FIXED_IN_ADVANCE = {"sr_smartphones_01", "sr_tvs_03", "sr_coffee_makers_02", "sr_robot_vacuums_01",
                               "sr_keyboards_01", "sr_water_bottles_01", "sr_blenders_01", "sr_tablets_01"}

TRAJ = ["olmo2-7b-s1-5B", "olmo2-7b-s1-51B", "olmo2-7b-s1-151B", "olmo2-7b-s1-500B", "olmo2-7b-s1-999B",
        "olmo2-7b-s1-2001B", "olmo2-7b-s1-2999B", "olmo2-7b-s1-3896B", "olmo2-7b-s2-ing1-50B"]
OLMO_POST = ["olmo2-7b-sft", "olmo2-7b-dpo", "olmo2-7b-instruct"]

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ loading

def read_split(root):
    p = DATA / "table_split.csv.gz"  # compressed, so that its bytes, and its SHA-256, are the same on every computer
    data, src = gzip.decompress(p.read_bytes()), "study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/table_split.csv.gz"
    rows = list(csv.DictReader(data.decode("utf-8").splitlines()))
    return {r["base_table_id"]: r["half"] for r in rows}, src, sha_bytes(data)


def load_jsonl(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_cell(path):
    raw = gzip.decompress(path.read_bytes())
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    prov = {}
    for k in ("model_tag", "repo", "revision", "commit_sha", "format"):
        vals = sorted({r[k] for r in rows})
        if len(vals) != 1:
            sys.exit(f"REFUSED: {path.name} has {len(vals)} values of {k}")
        prov[k] = vals[0]
    sc, echo_bad, mass_bad = {}, 0, 0
    for r in rows:
        if r["sha"] in sc:
            sys.exit(f"REFUSED: {path.name} scores {r['sha']} twice")
        p = np.array([float(r["p_" + L]) for L in LET])
        if not np.all(np.isfinite(p)) or np.any(p < 0):
            sys.exit(f"REFUSED: {path.name} has a non-finite or negative probability")
        echo_bad += r["text_sha"] != r["sha"]
        mass_bad += abs(float(r["letter_mass"]) - p.sum()) > 1e-5
        sc[r["sha"]] = {"p": p, "mass": float(r["letter_mass"]), "token_sha": r["token_sha"]}
    return prov, sc, {"file": "study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/scores/" + path.name, "sha256": sha_bytes(raw),
                      "rows": len(rows), "echo_sha_mismatches": echo_bad, "letter_mass_not_sum_of_p": mass_bad}


# ------------------------------------------------------------------ independent checks of the manifest

def my_half(t, split):
    if t["kind"] == "builder":
        return {"explore": "exploration", "confirm": "holdout"}[split[t["base_table_id"]]]
    v = int(hashlib.sha256(("origin-split|" + t["base_table_id"]).encode()).hexdigest()[:8], 16) % 4
    return "exploration" if v == 0 else "holdout"


def check_manifest(trials, texts, split):
    fails = defaultdict(int)
    for t in trials:
        if my_half(t, split) != t["half"]:
            fails["split differs from the manifest's half"] += 1
        o = t["order"]
        if any(t["orders"][a] != o for a in t["orders"]):
            fails["order differs across versions"] += 1
        if t["twin_letter"] != LET[o.index(str(t["twin_idx"]))] or t["winner_letter"] != LET[o.index(str(t["winner_idx"]))]:
            fails["twin or winner letter not the one the order assigns"] += 1
        if t["names"]["N"][LET.index(t["winner_letter"])] != t["winner_name"]:
            fails["winner name not at winner letter"] += 1
        if t["rung"] == "tie" and t["names"]["N"][LET.index(t["twin_letter"])] != t["twin_name"]:
            fails["twin name not at twin letter"] += 1
        for a in ("N", "H", "P"):
            if t["sha"][a] not in texts:
                fails[f"version {a} text missing from prompts.jsonl"] += 1
        H = texts.get(t["sha"]["H"], "")
        for a in ("N", "P"):
            s = texts.get(t["sha"][a], "")
            for i, L in enumerate(LET):
                piece = f"\n{L}. {t['label']}: {t['names'][a][i]}; "
                if s.count(piece) != 1:
                    fails[f"version {a}: option line {L} does not carry its name field exactly once"] += 1
                s = s.replace(piece, f"\n{L}. ")
            if s != H:
                fails[f"version {a} with name fields removed is not byte-identical to H"] += 1
        if t["rung"] == "tie":
            lines = {ln[:1]: ln[3:] for ln in H.split("\n") if re.match(r"^[A-E]\. ", ln)}
            if lines.get(t["twin_letter"]) != lines.get(t["winner_letter"]):
                fails["tie: twin and winner records differ in H"] += 1
            for nm in (t["twin_name"], t["winner_name"]):
                pat = r"\b" + re.escape(nm) + r"\b"
                if re.search(pat, H, flags=re.I if t["kind"] == "product" else 0):
                    fails["tie: a tied option's name appears in H"] += 1
    halves = defaultdict(set)
    for t in trials:
        halves[(t["kind"], t["half"])].add(t["base_table_id"])
    prod_expl = halves[("product", "exploration")]
    return {"trials_checked": len(trials), "failures": dict(fails),
            "tables_by_kind_and_half": {f"{k}|{h}": len(v) for (k, h), v in sorted(halves.items())},
            "product_exploration_set_equals_the_list_fixed_in_advance": prod_expl == PRODUCT_EXPLORATION_FIXED_IN_ADVANCE}


# ------------------------------------------------------------------ per-trial measures

def tie_measures(t, sc):
    try:
        pN, pH, pP = (sc[t["sha"][a]]["p"] for a in ("N", "H", "P"))
    except KeyError:
        return None
    a, b = LET.index(t["twin_letter"]), LET.index(t["winner_letter"])
    lo = lambda p: math.log(max(p[a], FLOOR)) - math.log(max(p[b], FLOOR))
    sh = lambda p: p[a] / (p[a] + p[b]) if p[a] + p[b] > 0 else 0.5
    floored = sum(p[i] < FLOOR for p in (pN, pH, pP) for i in (a, b))
    return {"D": lo(pN) - lo(pH), "D_minus_DP": lo(pN) - lo(pP), "share": 100 * (sh(pN) - sh(pH)),
            "pair_share_H": float((pH[a] + pH[b]) / pH.sum()), "floored": floored}


def tie_rows(trials, sc, tables, max_rep):
    out, missing = [], 0
    for t in trials:
        if t["rung"] != "tie" or t["rep"] > max_rep or t["base_table_id"] not in tables:
            continue
        m = tie_measures(t, sc)
        if m is None:
            missing += 1
            continue
        m.update(trial=t["trial_id"], table=t["base_table_id"], domain=t["domain"], kind=t["kind"], twin=t["twin_name"],
                 shas=(t["sha"]["N"], t["sha"]["H"]), shaP=t["sha"]["P"])
        out.append(m)
    if missing:
        sys.exit(f"REFUSED: {missing} tie trials lack an version in a score file")
    return out


def reading_rows(trials, sc, tables, max_rep):
    """Reading ability: q_H(winner) on dominated builder tables of medium and large margin."""
    out = []
    for t in trials:
        if t["rung"] != "dom" or t["kind"] != "builder" or t["margin"] not in ("medium", "large") or t["rep"] > max_rep \
                or t["base_table_id"] not in tables:
            continue
        p = sc[t["sha"]["H"]]["p"]
        out.append({"qH": float(p[LET.index(t["winner_letter"])] / p.sum()), "table": t["base_table_id"], "domain": t["domain"]})
    return out


# ------------------------------------------------------------------ aggregation and tests

def table_and_domain_means(rows, var):
    by_t, dom = defaultdict(list), {}
    for r in rows:
        by_t[r["table"]].append(r[var])
        dom[r["table"]] = r["domain"]
    tm = {t: float(np.mean(v)) for t, v in by_t.items()}
    by_d = defaultdict(list)
    for t, m in tm.items():
        by_d[dom[t]].append(m)
    return tm, {d: float(np.mean(v)) for d, v in sorted(by_d.items())}


def t_test(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    m, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(n))
    df = n - 1
    tv = m / se
    q95, q90 = stats.t.ppf(0.975, df), stats.t.ppf(0.95, df)
    pg, pl = float(stats.t.sf(tv, df)), float(stats.t.cdf(tv, df))
    return {"mean": m, "se": se, "df": df, "t": tv, "ci95": [m - q95 * se, m + q95 * se], "ci90": [m - q90 * se, m + q90 * se],
            "p_greater": pg, "p_less": pl, "p_two_sided": min(1.0, 2 * min(pg, pl))}


def domain_level(rows, var):
    tm, dm = table_and_domain_means(rows, var)
    res = t_test(list(dm.values()))
    res.update(n_tables=len(tm), n_domains=len(dm), domain_means=dm,
               interval_method="95% t interval over domain means (each the mean of its tables' means over repetitions)")
    return res


def cluster_level(rows, var):
    """Mean of table means; CR1 standard error clustered by twin brand; t with G - 1 df."""
    by_t, cl = defaultdict(list), {}
    for r in rows:
        by_t[r["table"]].append(r[var])
        cl[r["table"]] = r["twin"]
    tabs = sorted(by_t)
    y = np.array([np.mean(by_t[t]) for t in tabs])
    n, m = len(y), float(y.mean())
    groups = sorted({cl[t] for t in tabs})
    G = len(groups)
    u = {g: 0.0 for g in groups}
    for t, yi in zip(tabs, y):
        u[cl[t]] += yi - m
    # intercept-only OLS: (X'X)^-1 = 1/n; CR1 factor G/(G-1) * (n-1)/(n-k) with k = 1
    var = G / (G - 1) * (n - 1) / (n - 1) * sum(v * v for v in u.values()) / n ** 2
    se = math.sqrt(var)
    df = G - 1
    tv = m / se
    q95, q90 = stats.t.ppf(0.975, df), stats.t.ppf(0.95, df)
    pg, pl = float(stats.t.sf(tv, df)), float(stats.t.cdf(tv, df))
    return {"mean": m, "se_cr1": se, "df": df, "t": tv, "ci95": [m - q95 * se, m + q95 * se], "ci90": [m - q90 * se, m + q90 * se],
            "p_greater": pg, "p_less": pl, "p_two_sided": min(1.0, 2 * min(pg, pl)), "n_tables": n, "n_clusters": G,
            "clusters": groups, "interval_method": "95% t interval (G - 1 df) with CR1 cluster-robust SE by twin brand"}


def holm(ps):
    k = len(ps)
    order = sorted(range(k), key=lambda i: ps[i])
    adj, run = [0.0] * k, 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (k - r) * ps[i]))
        adj[i] = run
    return adj


def verdict(main, plac, p_main):
    """The analysis plan's verdict: hit, reversal, null (90% CI inside +-0.10), or inconclusive."""
    if p_main < ALPHA and main["mean"] >= SESOI:
        return "hit" if plac["p_greater"] < ALPHA else "names in general move the probability (placebo condition fails)"
    if main["p_less"] < ALPHA:
        return "reversal"
    if main["ci90"][0] > -SESOI and main["ci90"][1] < SESOI:
        return "null (equivalent to zero)"
    return "inconclusive"


def s1_word(r, p):
    if p < 0.05:
        return "increased" if r["mean"] > 0 else "decreased"
    if r["ci90"][0] > -SESOI and r["ci90"][1] < SESOI:
        return "equivalent"
    return "inconclusive"


# ------------------------------------------------------------------ assembling the output

def r3(x):
    return None if x is None else round(float(x), 6)


def stat_block(res):
    keep = ("mean", "ci95", "ci90", "se", "se_cr1", "df", "t", "p_greater", "p_less", "p_two_sided", "n_tables",
            "n_domains", "n_clusters", "interval_method")
    out = {}
    for k in keep:
        if k in res:
            v = res[k]
            out[k] = [r3(z) for z in v] if isinstance(v, list) else (r3(v) if isinstance(v, float) else v)
    if "domain_means" in res:
        out["domain_means"] = {d: r3(v) for d, v in res["domain_means"].items()}
    if "clusters" in res:
        out["clusters"] = res["clusters"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()
    out_path = pathlib.Path(args.out)

    trials = load_jsonl(DATA / "trials.jsonl.gz")
    prompts = load_jsonl(DATA / "pages.jsonl.gz")
    texts = {}
    bad_text_sha = 0
    for p in prompts:
        bad_text_sha += sha_bytes(p["text"].encode("utf-8")) != p["sha"]
        texts[p["sha"]] = p["text"]
    split, split_src, split_sha = read_split(ROOT)
    mcheck = check_manifest(trials, texts, split)
    mcheck["prompt_texts"] = len(texts)
    mcheck["prompt_text_sha_mismatches"] = bad_text_sha
    mcheck["split_source"] = split_src
    mcheck["split_sha256"] = split_sha
    mcheck["split_sha256_equals_the_value_fixed_in_advance"] = split_sha == SPLIT_SHA256_FIXED_IN_ADVANCE
    if mcheck["failures"] or bad_text_sha:
        print(json.dumps(mcheck, indent=1))
        sys.exit("REFUSED: the manifest fails a pairing check")

    cells, files, prov = {}, {}, {}
    for path in sorted((DATA / "scores").glob("*.csv.gz")):
        pv, sc, info = load_cell(path)
        key = (pv["model_tag"], pv["format"])
        cells[key], files[key], prov[key] = sc, info, pv
    total_rows = sum(f["rows"] for f in files.values())

    # a check of the plan: token ids identical across every OLMo checkpoint in the plain format
    olmo_plain = [k for k in cells if k[0].startswith("olmo2") and k[1] == "plain"]
    common = set.intersection(*(set(cells[k]) for k in olmo_plain))
    tok_bad = sum(len({cells[k][s]["token_sha"] for k in olmo_plain}) != 1 for s in common)

    all_tables = {t["base_table_id"] for t in trials}
    hold = {t["base_table_id"] for t in trials if my_half(t, split) == "holdout"}
    hold_b = {t for t in hold if not t.startswith("sr_")}
    hold_p = hold - hold_b
    maxrep = {k: (4 if k[0] in TRAJ else 6) for k in cells}

    def rel(key):
        return files[key]["file"]

    def provenance(key):
        pv = prov[key]
        return {"model_tag": pv["model_tag"], "repo": pv["repo"], "revision": pv["revision"], "commit_sha": pv["commit_sha"],
                "format": pv["format"]}

    def counts(rows, with_placebo=False):
        s = {x for r in rows for x in r["shas"]}
        out = {"n_tie_trials": len(rows), "n_distinct_prompts_scored_named_and_hidden": len(s)}
        if with_placebo:
            out["n_distinct_prompts_scored_incl_placebo"] = len(s | {r["shaP"] for r in rows})
        return out

    values = []

    # ---------------- every cell, holdout, tie rung, domain-level test
    hold_rows = {k: tie_rows(trials, cells[k], hold, maxrep[k]) for k in cells}
    cell_res = {}
    for k in sorted(cells):
        rows = hold_rows[k]
        cell_res[k] = {"D": domain_level(rows, "D"), "plac": domain_level(rows, "D_minus_DP"), "share": domain_level(rows, "share"),
                       "read": domain_level(rows, "pair_share_H")}

    # Holm across the four Qwen and Llama cells, and across the two product-only cells
    s3_keys = [("qwen2.5-7b-base", "plain"), ("qwen2.5-7b-instruct", "chat"), ("llama3.1-8b-base", "plain"),
               ("llama3.1-8b-instruct", "chat")]
    s3_holm = dict(zip(s3_keys, holm([cell_res[k]["D"]["p_greater"] for k in s3_keys])))
    named = {
        ("olmo2-7b-base", "plain"): ("olmo2_base", "OLMo 2 7B after pretraining (released base, main), plain format", None),
        ("olmo2-7b-instruct", "chat"): ("olmo2_instruct_chat", "OLMo 2 7B Instruct (after SFT, DPO and RL), chat format", None),
        ("olmo2-7b-instruct", "plain"): ("olmo2_instruct_plain", "OLMo 2 7B Instruct, plain format", None),
        ("olmo2-7b-s1-3896B", "plain"): ("olmo2_end_of_stage_1", "OLMo 2 7B at the end of pretraining stage 1 (3,896B tokens, before mid-training), plain", None),
        ("qwen2.5-7b-base", "plain"): ("qwen2.5_7b_base", "Qwen 2.5 7B base, plain", s3_holm[s3_keys[0]]),
        ("qwen2.5-7b-instruct", "chat"): ("qwen2.5_7b_instruct", "Qwen 2.5 7B Instruct, chat", s3_holm[s3_keys[1]]),
        ("llama3.1-8b-base", "plain"): ("llama3.1_8b_base", "Llama 3.1 8B base (unsloth mirror), plain", s3_holm[s3_keys[2]]),
        ("llama3.1-8b-instruct", "chat"): ("llama3.1_8b_instruct", "Llama 3.1 8B Instruct (unsloth mirror), chat", s3_holm[s3_keys[3]]),
    }
    for k in sorted(cells):
        r = cell_res[k]
        rows = hold_rows[k]
        entry = {"key": None, "what": None}
        if k in named:
            key, what, ph = named[k]
            p_main = r["D"]["p_greater"] if ph is None else ph
            v = verdict(r["D"], r["plac"], p_main)
            entry.update(key=key, what=what, verdict=v, p_one_sided_used_for_verdict=r3(p_main),
                         p_note="Holm-adjusted across the four Qwen and Llama cells" if ph is not None else "one-sided, unadjusted")
        else:
            entry.update(key=f"cell_{k[0]}_{k[1]}", what=f"{k[0]}, {k[1]} format, holdout tie rung (no pre-specified test)",
                         verdict_by_plan_rules_unadjusted=verdict(r["D"], r["plac"], r["D"]["p_greater"]))
        entry.update(provenance(k))
        entry.update(tables="holdout (134 tables: 108 builder, 26 products)", repetitions=f"1-{maxrep[k]}")
        entry.update(counts(rows, with_placebo=True))
        entry["estimate_D"] = r3(r["D"]["mean"])
        entry["ci95"] = [r3(x) for x in r["D"]["ci95"]]
        entry["odds_ratio_exp_D"] = r3(math.exp(r["D"]["mean"]))
        entry["D_stats"] = stat_block(r["D"])
        entry["placebo_condition_D_minus_DP"] = stat_block(r["plac"])
        entry["share_points_named_minus_hidden"] = stat_block(r["share"])
        entry["hidden_arm_share_on_the_two_tied_letters"] = {"mean": r3(r["read"]["mean"]), "ci95": [r3(x) for x in r["read"]["ci95"]],
                                                             "reads_the_tie_page_ge_0.50": r["read"]["mean"] >= 0.50}
        entry["values_floored_at_1e-30"] = sum(x["floored"] for x in rows)
        entry["raw_files"] = [rel(k)]
        values.append(entry)

    # ---------------- product tables only, CR1 by twin brand, Holm across two
    b1_keys = [("olmo2-7b-base", "plain", "products_only_olmo2_base"), ("olmo2-7b-instruct", "chat", "products_only_olmo2_instruct")]
    b1 = {}
    for tag, fmt, key in b1_keys:
        rows = [x for x in hold_rows[(tag, fmt)] if x["kind"] == "product"]
        b1[key] = (rows, cluster_level(rows, "D"), cluster_level(rows, "D_minus_DP"), cluster_level(rows, "share"))
    b1_holm = dict(zip([k for _, _, k in b1_keys], holm([b1[k][1]["p_greater"] for _, _, k in b1_keys])))
    for tag, fmt, key in b1_keys:
        rows, d, pl, shr = b1[key]
        v = verdict(d, pl, b1_holm[key])
        e = {"key": key, "what": f"product tables only (the consumer brands of Study 1), {tag}, {fmt}",
             "verdict": v, "p_one_sided_holm_across_two": r3(b1_holm[key])}
        e.update(provenance((tag, fmt)))
        e.update(tables="holdout products (26 assortments)", repetitions="1-6")
        e.update(counts(rows, with_placebo=True))
        e.update(estimate_D=r3(d["mean"]), ci95=[r3(x) for x in d["ci95"]], odds_ratio_exp_D=r3(math.exp(d["mean"])),
                 D_stats=stat_block(d), placebo_condition_D_minus_DP=stat_block(pl), share_points_named_minus_hidden=stat_block(shr),
                 raw_files=[rel((tag, fmt))])
        values.append(e)

    # ---------------- steps of post-training, plain, holdout, trial-matched differences
    stages = [("olmo2-7b-base", "plain"), ("olmo2-7b-sft", "plain"), ("olmo2-7b-dpo", "plain"), ("olmo2-7b-instruct", "plain")]
    bytrial = {k: {x["trial"]: x for x in hold_rows[k]} for k in stages}
    steps = [("olmo2_step_base_to_sft", 0, 1), ("olmo2_step_sft_to_dpo", 1, 2), ("olmo2_step_dpo_to_instruct", 2, 3), ("olmo2_step_base_to_instruct", 0, 3)]
    s1 = {}
    for name, i, j in steps:
        a, b = bytrial[stages[i]], bytrial[stages[j]]
        common_t = sorted(set(a) & set(b))
        diff = [dict(b[t], Ddiff=b[t]["D"] - a[t]["D"]) for t in common_t]
        s1[name] = (diff, domain_level(diff, "Ddiff"))
    s1_holm = dict(zip(["olmo2_step_base_to_sft", "olmo2_step_sft_to_dpo", "olmo2_step_dpo_to_instruct"],
                       holm([s1[n][1]["p_two_sided"] for n in ("olmo2_step_base_to_sft", "olmo2_step_sft_to_dpo", "olmo2_step_dpo_to_instruct")])))
    for name, i, j in steps:
        diff, res = s1[name]
        p_used = s1_holm.get(name, res["p_two_sided"])
        word = s1_word(res, p_used)
        e = {"key": name, "what": f"change in D from {stages[i][0]} to {stages[j][0]}, plain format (identical inputs), "
                                  "per-trial difference, domain-level paired test, two-sided",
             "verdict": word, "p_two_sided_used": r3(p_used),
             "p_note": "Holm across the three steps" if name in s1_holm else "unadjusted (not one of the three Holm steps)",
             "earlier": provenance(stages[i]), "later": provenance(stages[j]),
             "earlier_stage_D_holdout": r3(cell_res[stages[i]]["D"]["mean"]), "later_stage_D_holdout": r3(cell_res[stages[j]]["D"]["mean"]),
             "tables": "holdout (134 tables)", "repetitions": "1-6", "n_matched_tie_trials": len(diff),
             "n_distinct_prompts_scored_per_checkpoint": len({x for r in diff for x in r["shas"]}),
             "estimate_change_in_D": r3(res["mean"]), "ci95": [r3(x) for x in res["ci95"]], "D_change_stats": stat_block(res),
             "raw_files": [rel(stages[i]), rel(stages[j])]}
        values.append(e)

    # ---------------- pretraining trajectory (all tables, repetitions 1 to 4, plain), extended to post-training
    ladder = TRAJ + ["olmo2-7b-base"] + OLMO_POST
    traj = []
    used = {s for t in trials if t["rep"] <= 4 for s in t["sha"].values()}
    for tag in ladder:
        for fmt in (("plain",) if tag in TRAJ or tag == "olmo2-7b-base" else ("plain", "chat")):
            k = (tag, fmt)
            rows = tie_rows(trials, cells[k], all_tables, 4)
            d = domain_level(rows, "D")
            ra = domain_level(reading_rows(trials, cells[k], all_tables, 4), "qH")
            lm = float(np.median([cells[k][s]["mass"] for s in used]))
            p = {"checkpoint": tag, "in_the_pre_specified_trajectory": tag in TRAJ or tag == "olmo2-7b-base"}
            p.update(provenance(k))
            p.update(tables="all 250 (exploration and holdout)", repetitions="1-4")
            p.update(counts(rows))
            p.update(estimate_D=r3(d["mean"]), ci95=[r3(x) for x in d["ci95"]], D_stats=stat_block(d),
                     reading_ability_builder_medium_large=stat_block(ra),
                     median_letter_mass_distinct_texts_reps_1_4=r3(lm), interpretable_median_mass_ge_0_05=lm >= 0.05,
                     raw_files=[rel(k)])
            traj.append(p)

    def earliest(points, pred):
        ok = [pred(p) and p["interpretable_median_mass_ge_0_05"] for p in points]
        for i in range(len(points)):
            if all(ok[i:]):
                return points[i]["checkpoint"]
        return None

    plan_pts = [p for p in traj if p["in_the_pre_specified_trajectory"]]
    s2_above = earliest(plan_pts, lambda p: p["ci95"][0] > 0)
    s2_excl = earliest(plan_pts, lambda p: p["ci95"][0] > 0 or p["ci95"][1] < 0)
    ladder_plain = [p for p in traj if p["format"] == "plain"]
    first_pos_plain = next((p["checkpoint"] for p in ladder_plain if p["ci95"][0] > 0), None)
    first_pos_from_then_plain = earliest(ladder_plain, lambda p: p["ci95"][0] > 0)
    chat_pts = [p for p in traj if p["format"] == "chat"]
    first_pos_chat = next((p["checkpoint"] for p in chat_pts if p["ci95"][0] > 0), None)
    hold_ladder = [("olmo2-7b-base", "plain")] + [(t, f) for f in ("plain", "chat") for t in OLMO_POST]
    stage_onset = {
        "answer": None,
        "pretraining_pre_specified_basis": {
            "earliest_D_interval_above_zero_from_then_on": s2_above,
            "earliest_D_interval_excludes_zero_from_then_on": s2_excl,
            "range_of_D_over_pretraining_points": [r3(min(p["estimate_D"] for p in plan_pts)), r3(max(p["estimate_D"] for p in plan_pts))],
        },
        "full_ladder_same_basis_plain_exploratory": {
            "order": [p["checkpoint"] for p in ladder_plain],
            "first_checkpoint_with_D_interval_above_zero": first_pos_plain,
            "first_from_which_D_interval_stays_above_zero": first_pos_from_then_plain,
        },
        "post_training_chat_same_basis_exploratory": {"first_checkpoint_with_D_interval_above_zero": first_pos_chat},
        "holdout_levels_reps_1_6": [{"checkpoint": t, "format": f, "D": r3(cell_res[(t, f)]["D"]["mean"]),
                                     "ci95": [r3(x) for x in cell_res[(t, f)]["D"]["ci95"]]} for t, f in hold_ladder],
        "holdout_step_contrasts": {n: {"change": r3(s1[n][1]["mean"]), "ci95": [r3(x) for x in s1[n][1]["ci95"]],
                                       "p": r3(s1_holm.get(n, s1[n][1]["p_two_sided"]))} for n, _, _ in steps},
    }

    # ---------------- notes
    by = {v["key"]: v for v in values}
    sft_plain = cell_res[("olmo2-7b-sft", "plain")]["D"]
    sft_chat = cell_res[("olmo2-7b-sft", "chat")]["D"]
    stage_onset["answer"] = (
        f"No pretraining checkpoint shows a lean toward the famous twin: on the pre-specified trajectory D runs from "
        f"{stage_onset['pretraining_pre_specified_basis']['range_of_D_over_pretraining_points'][0]:.3f} to "
        f"{stage_onset['pretraining_pre_specified_basis']['range_of_D_over_pretraining_points'][1]:.3f} and no interval lies above zero "
        f"(from {s2_excl} on, the intervals lie below zero). The first checkpoint with a positive D is SFT: in the chat format "
        f"SFT's holdout D is {sft_chat['mean']:.3f} [{sft_chat['ci95'][0]:.3f}, {sft_chat['ci95'][1]:.3f}]; in the plain format "
        f"SFT's level is {sft_plain['mean']:.3f} [{sft_plain['ci95'][0]:.3f}, {sft_plain['ci95'][1]:.3f}], whose lower end "
        f"{'is above' if sft_plain['ci95'][0] > 0 else 'touches or crosses'} zero, and the pretrained-to-SFT step is "
        f"{s1['olmo2_step_base_to_sft'][1]['mean']:.3f} (Holm p {s1_holm['olmo2_step_base_to_sft']:.4f}); the SFT-to-DPO and "
        f"DPO-to-Instruct steps are equivalent to zero.")

    notes = []
    notes.append(f"All 22 score files are present (13 primary cells x 8,107 texts + 9 trajectory checkpoints x 5,489 "
                 f"texts = {total_rows:,} scored prompts).")
    notes.append(f"The SHA-256 of table_split.csv {'equals' if mcheck['split_sha256_equals_the_value_fixed_in_advance'] else 'DIFFERS FROM'} "
                 "the value fixed before the holdout tables were analysed.")
    h1 = by["olmo2_base"]
    notes.append(f"The released base model of OLMo 2 7B shows a reversal by the verdict rules, not a null: a small but "
                 f"significant lean toward the unfamiliar option, {h1['estimate_D']:.3f} [{h1['ci95'][0]:.3f}, "
                 f"{h1['ci95'][1]:.3f}], one-sided p of a negative effect {h1['D_stats']['p_less']:.2g}.")
    notes.append(f"The step from the base model to instruction tuning is a change in D "
                 f"({by['olmo2_step_base_to_sft']['estimate_change_in_D']:.3f}, plain format), not the level after instruction "
                 f"tuning, which is {sft_plain['mean']:.3f} in plain and {sft_chat['mean']:.3f} in chat format.")
    notes.append("Llama base is equivalent to zero and Llama Instruct (chat) is a hit; the Llama weights are the ungated "
                 "unsloth mirrors. Both Qwen cells are reversals (base and Instruct both favour the unfamiliar option).")
    notes.append("Every OLMo cell fails the tie-page reading check (the names-hidden share on the two tied letters is below "
                 "0.50; chance 0.40), so in OLMo D measures what a name does to the letter probabilities when the record "
                 "is not being read.")
    notes.append("A summary of the builder-table holdout had been seen before the holdout analysis ran; the product-only "
                 "test was not part of that summary.")

    out = {
        "title": "Origin of the famous-name lean in open models (OLMo 2 stages, Llama 3.1, Qwen 2.5), recomputed from raw letter probabilities",
        "script": "study3b-brand-knowledge-and-training-text-in-released-models/code/checkpoints.py",
        "inputs": {
            "folder": "study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints",
            "trials_jsonl_sha256": sha_bytes(gzip.decompress((DATA / "trials.jsonl.gz").read_bytes())),
            "pages_jsonl_sha256": sha_bytes(gzip.decompress((DATA / "pages.jsonl.gz").read_bytes())),
            "score_files": [dict(files[k], **provenance(k)) for k in sorted(files)],
            "total_scored_prompts": total_rows,
        },
        "checks": {
            "manifest": mcheck,
            "score_files_echo_sha_mismatches": sum(f["echo_sha_mismatches"] for f in files.values()),
            "score_files_letter_mass_not_sum_of_p": sum(f["letter_mass_not_sum_of_p"] for f in files.values()),
            "olmo_plain_token_ids_differ_across_checkpoints": tok_bad,
            "olmo_plain_texts_compared_for_token_ids": len(common),
            "olmo_plain_cells_compared": [f"{a}|{b}" for a, b in sorted(olmo_plain)],
            "holdout_tables": {"builder": len(hold_b), "products": len(hold_p)},
        },
        "definitions": {
            "D": "per tie trial: [ln p_N(twin) - ln p_N(winner)] - [ln p_H(twin) - ln p_H(winner)], p floored at 1e-30, raw letter probabilities",
            "placebo_condition": "per tie trial: L_N - L_P (famous name against an unfamiliar name in the twin's place)",
            "interval": "95% t interval over the 13 domain means (12 df), each the mean of its tables' means over repetitions "
                        "; products alone: CR1 cluster-robust by twin brand, G - 1 df. No bootstrap "
                        "was needed because the analysis plan defines every interval.",
            "verdict_rules": "hit: one-sided p < 0.025 (Holm where the analysis plan says), mean >= 0.10, and placebo condition one-sided p < 0.025; "
                             "reversal: one-sided p of a negative mean < 0.025; null: 90% interval inside -0.10 to +0.10; else inconclusive",
        },
        "values": values,
        "trajectory_and_post_training_ladder": traj,
        "olmo2_stage_where_the_lean_first_appears": stage_onset,
        "notes": notes,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
        f.write("\n")

    # console summary
    print(f"scored prompts read: {total_rows:,}; manifest checks: {mcheck['trials_checked']} trials, 0 failures; "
          f"token-id differences across OLMo plain: {tok_bad}")
    for v in values:
        est = v.get("estimate_D", v.get("estimate_change_in_D"))
        print(f"{v['key']:<42s} n={v.get('n_tie_trials', v.get('n_matched_tie_trials')):>4}  {est:+.4f} "
              f"[{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}]")
    for p in traj:
        print(f"{p['checkpoint']:<22s} {p['format']:<5s} {p['estimate_D']:+.4f} [{p['ci95'][0]:+.4f}, {p['ci95'][1]:+.4f}] "
              f"read {p['reading_ability_builder_medium_large']['mean']:.3f}")
    print(stage_onset["answer"])
    print(f"written {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
