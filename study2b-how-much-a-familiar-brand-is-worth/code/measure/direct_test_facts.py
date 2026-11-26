"""Facts about Study 2b's direct test (the direct price premium): which names stood beside the brand, and how often the
Claude models recommended the brand's product at each price.

    python study2b-how-much-a-familiar-brand-is-worth/code/measure/direct_test_facts.py [--out PATH]

In the direct test, a familiar brand's product appeared with four products of identical specifications under four
other names of its category, drawn at random from the category's familiar brands and fictitious names together, at
the brand's band centre; the brand's product was priced 10% lower, the same, or 10%, 20% or 30% higher. The rivals are
counted from the items (materials/measure/items/full1/items.jsonl.gz, one count for each choice set, which every price
shares) and the shares are read from the Claude models' numbers (results/measure/full1-claude-api/numbers.json, each
brand's direct_premium.share_by_premium). The Fable model did not answer the test.

By default the result is written to study2b-how-much-a-familiar-brand-is-worth/results/measure/direct-test/numbers.json.
"""
import argparse
import gzip
import json
import statistics as st
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[2]   # the top of the replication package
ITEMS = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "materials" / "measure" / "items" / "full1" / "items.jsonl.gz"
S2B = ITEMS.parents[4]   # the study's folder, to which the sources' paths are written relative
CATS = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "materials" / "measure" / "categories"
NUM = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "results" / "measure" / "full1-claude-api" / "numbers.json"
OUT = PKG / "study2b-how-much-a-familiar-brand-is-worth" / "results" / "measure" / "direct-test" / "numbers.json"
LEVELS = ["-0.10", "+0.00", "+0.10", "+0.20", "+0.30"]


def rivals(items=ITEMS, cats=CATS):
    fict = {}
    for f in sorted(cats.glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        fict[c["category"]] = {n for n, _ in c["invented"]}
    seen, places, per_set = set(), Counter(), Counter()
    with gzip.open(items, "rt", encoding="utf-8") as fh:
        for line in fh:
            it = json.loads(line)
            if it.get("version") != "premium":
                continue
            key = (it["category"], it["focal_name"], it["draw"])
            if key in seen:
                continue
            seen.add(key)
            names = [p["name"] for p in it["products"].values() if p["name"] != it["focal_name"]]
            k = sum(n in fict[it["category"]] for n in names)
            per_set[k] += 1
            places["fictitious"] += k
            places["familiar"] += len(names) - k
    n = places["familiar"] + places["fictitious"]
    return {"choice_sets": len(seen), "rival_places": n, "familiar": places["familiar"],
            "fictitious": places["fictitious"], "familiar_pct": 100 * places["familiar"] / n,
            "fictitious_pct": 100 * places["fictitious"] / n, "sets_with_only_familiar_rivals": per_set[0],
            "sets_by_number_of_fictitious_rivals": {str(k): per_set[k] for k in sorted(per_set)}}


def claude_shares(num=NUM):
    d = json.loads(num.read_text(encoding="utf-8"))
    per_model, pooled = {}, {lv: [] for lv in LEVELS}
    for m, cats in sorted(d["models"].items()):
        shares, prem = {lv: [] for lv in LEVELS}, []
        for c in cats.values():
            for u in c["main"]["brands"].values():
                dp = u.get("direct_premium")
                if not dp:
                    continue
                for lv in LEVELS:
                    if dp["share_by_premium"].get(lv) is not None:
                        shares[lv].append(dp["share_by_premium"][lv])
                if dp.get("premium_at_one_in_five") is not None:
                    prem.append(dp["premium_at_one_in_five"])
        if not prem:
            continue
        per_model[m] = {"brands": len(prem), "direct_premium_median_pct": st.median(prem),
                        "share_pct_by_premium": {lv: 100 * st.mean(shares[lv]) for lv in LEVELS},
                        "share_pct_highest_when_priced_higher": 100 * max(shares["+0.10"] + shares["+0.20"]
                                                                          + shares["+0.30"])}
        for lv in LEVELS:
            pooled[lv] += shares[lv]
    return {"models": len(per_model), "per_model": per_model,
            "share_pct_by_premium": {lv: 100 * st.mean(pooled[lv]) for lv in LEVELS},
            "share_pct_same_price_lowest_model": min(v["share_pct_by_premium"]["+0.00"] for v in per_model.values()),
            "share_pct_same_price_highest_model": max(v["share_pct_by_premium"]["+0.00"] for v in per_model.values()),
            "share_pct_highest_when_priced_higher": max(v["share_pct_highest_when_priced_higher"]
                                                        for v in per_model.values()),
            "direct_premium_median_pct_over_models": st.median(v["direct_premium_median_pct"]
                                                               for v in per_model.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=OUT, help="where to write numbers.json")
    out_path = ap.parse_args().out
    out = {"sources": [str(p.relative_to(S2B)).replace("\\", "/") for p in (ITEMS, NUM)],
           "rivals": rivals(), "claude": claude_shares()}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    r, c = out["rivals"], out["claude"]
    print(f"rivals: {r['familiar']} familiar and {r['fictitious']} fictitious of {r['rival_places']} "
          f"({r['familiar_pct']:.0f}% familiar); {r['sets_with_only_familiar_rivals']} of {r['choice_sets']} sets with "
          f"only familiar rivals")
    print(f"Claude ({c['models']} models): share by premium {({k: round(v, 1) for k, v in c['share_pct_by_premium'].items()})}; "
          f"highest when priced higher {c['share_pct_highest_when_priced_higher']}; median direct premium "
          f"{c['direct_premium_median_pct_over_models']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
