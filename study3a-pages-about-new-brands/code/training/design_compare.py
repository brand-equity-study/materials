"""What differs between the two training designs of Study 3a (the first design's new service brands and the second
design's product brands), read from the runs' own files, for the sentence of Study 3's discussion that compares them:
- the amount of text: a new service brand's tokens of pages (corpus_stats.json of the replication's runs of Qwen 2.5 7B
  with seed 20261001 that have pages) and a product brand's tokens at 80 and at 320 pages (the planted tokens over the
  planted pages of each run of the second design);
- the outcome without brand names: how often the first design's model chooses the planted brand without brand
  names (planted_text.py's lift cells), and the probability that a model of the second design gives the optimal product
  without brand names on its planted tables (analyze_q2.py's pairs of prompts, after preference tuning, role3).
Descriptive means only; nothing here is a test.

    python study3a-pages-about-new-brands/code/training/design_compare.py \
        --october study3a-pages-about-new-brands/data/replication-runs/qwen25-7b/qwen25-7b-<none|neutralclean|promo|negative>-s20261001 \
        --q2 study3a-pages-about-new-brands/data/training-runs/olmo2-7b study3a-pages-about-new-brands/data/training-runs/qwen25-7b study3a-pages-about-new-brands/data/training-runs/llama31-8b \
        --out study3a-pages-about-new-brands/results/training/parts/design_compare.json

--q2 takes run folders or folders that hold them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # analyze_q2.py
sys.path.insert(0, os.path.join(HERE, "..", "first-design-replication"))   # analyze_replication.py
sys.path.insert(0, os.path.join(HERE, ".."))   # planted_text.py, the first design's reader
import analyze_q2 as aq  # noqa: E402

FAMILY = re.compile(r"(olmo2-7b|qwen25-7b|llama31-8b)-a\d-s\d+$")


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def october_text(folders):
    toks, shares = [], []
    for f in folders:
        st = json.load(open(os.path.join(f, "corpus_stats.json"), encoding="utf-8"))
        for org in (st.get("orgs") or {}).values():
            if org.get("tokens_used"):
                toks.append(org["tokens_used"])
                shares.append(org["tokens_used"] / st["T_tokens"])
    return {"organizations_runs": len(toks), "tokens_per_organization_mean": round(mean(toks)),
            "tokens_per_organization_min": min(toks), "tokens_per_organization_max": max(toks),
            "share_of_training_tokens_mean": round(mean(shares), 4)}


def october_hidden_pick(folders):
    """The share of decisions in which the model picks the planted brand with names hidden, after DPO."""
    import analyze_replication as ao
    import planted_text as S
    items, _, _, _ = S.load_items()
    hidden, pairs = 0, 0
    for f in folders:
        arm = re.search(r"-(none|neutralclean|promo|negative)-s\d+$", os.path.basename(os.path.normpath(f))).group(1)
        m = ao.model_of(f, arm, "dpo", items)
        for dm in ao.DOMS:
            c = S.lift_cells(m, dm)
            hidden += c["P_hidden"]
            pairs += c["pairs"]
    return {"decisions": pairs, "picked_with_names_hidden_pct": round(100 * hidden / pairs, 1)}


def q2_text(folders):
    per_page = []
    for f in folders:
        st = json.load(open(os.path.join(f, "corpus_stats.json"), encoding="utf-8"))
        pages = sum(v.get("pages", 0) for v in st["plan"].values())
        per_page.append(st["planted_tokens"] / pages)
        total = st["total_target"]
    tpp = mean(per_page)
    return {"runs": len(per_page), "tokens_per_page_mean": round(tpp, 1), "tokens_at_80_pages": round(80 * tpp),
            "tokens_at_320_pages": round(320 * tpp), "share_of_training_tokens_at_80_pages": round(80 * tpp / total, 4),
            "share_of_training_tokens_at_320_pages": round(320 * tpp / total, 4)}


def q2_hidden_best(folders):
    q2_items = aq.jl(os.path.join(aq.MAT, "q2_items.jsonl"))
    dom2 = aq.jl(os.path.join(aq.PKG, "study1a-tables-with-one-optimal-product", "materials", "strictly-better-tables", "prompts.jsonl.gz"))
    hid = aq.hidden_index(dom2)
    by = {}
    for f in folders:
        fam = FAMILY.search(os.path.basename(os.path.normpath(f))).group(1)
        lab = aq.run_label(f, "role3", "dpo-uf", "q2_items.jsonl")
        dom2_p = aq.probs(os.path.join(f, f"scores_{lab}_role3.csv"))
        q2_p = aq.probs(os.path.join(f, f"scores_{lab}_role3_q2_items.jsonl.csv"))
        hs, ps = [], []
        for it in q2_items:
            if it["where"] != "best":
                continue
            p = q2_p.get(it["id"])
            h = dom2_p.get(hid.get((it["table"], int(it["trial"]), int(it["info"]), int(it["rung"]))))
            if p is None or h is None:
                continue
            hs.append(h[it["planted_letter"]])
            ps.append(p[it["planted_letter"]])
        by.setdefault(fam, []).append((mean(hs), mean(ps)))
    out = {fam: {"models": len(v), "best_with_names_hidden_pct": round(100 * mean([h for h, _ in v]), 1),
                 "best_with_planted_brand_shown_pct": round(100 * mean([p for _, p in v]), 1)} for fam, v in by.items()}
    out["mean_of_the_families"] = {"best_with_names_hidden_pct": round(mean([v["best_with_names_hidden_pct"]
                                                                              for v in out.values()]), 1)}
    return out


def runs_in(paths):
    """The second design's run folders: each path, or every run folder below it."""
    out = []
    for p in paths:
        if FAMILY.search(os.path.basename(os.path.normpath(p))):
            out.append(p)
        else:
            out += sorted(d for d, _, files in os.walk(p)
                          if "corpus_stats.json" in files and FAMILY.search(os.path.basename(d)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--october", nargs="+", required=True, help="October run folders with pages (and none)")
    ap.add_argument("--q2", nargs="+", required=True, help="question 2 planted run folders")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    a.q2 = runs_in(a.q2)
    paged = [f for f in a.october if not re.search(r"-none-s\d+$", os.path.normpath(f))]
    res = {"october": {"text": october_text(paged), "outcome": october_hidden_pick(a.october)},
           "product_brands": {"text": q2_text(a.q2), "outcome": q2_hidden_best(a.q2)}}
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
