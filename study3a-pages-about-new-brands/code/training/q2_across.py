"""Question 2 across the three 7B-to-8B families, read from each family's part (the training study's plan, question 2:
each family is reported alone and nothing is pooled across families). For each family: the kind with the largest E and
its estimate, the kinds whose E is above zero after Holm, praise's E, and bare mentions against praise and against
expert reviews; then the families in which each of these holds.

    python study3a-pages-about-new-brands/code/training/q2_across.py --parts study3a-pages-about-new-brands/results/training/parts \
        --out study3a-pages-about-new-brands/results/training/parts/q2_across.json
"""
import argparse
import json
import os

FAMILIES = (("olmo2-7b", "q2"), ("qwen25-7b", "q2_qwen"), ("llama31-8b", "q2_llama"))
ALPHA = 0.05


def above(e):
    """An estimate whose interval lies above zero and whose Holm p is below 0.05."""
    return e["ci95"][0] > 0 and e.get("p_holm", 1.0) < ALPHA


def keep(e):
    return {k: e[k] for k in ("estimate", "ci95", "p_two_sided", "p_holm") if k in e}


def family(part):
    kinds = part["kinds"]["E"]
    largest = max(kinds, key=lambda k: kinds[k]["estimate"])
    pairs = part["pairs"]["E"]
    return {"models": part["models"], "largest_E_kind": largest, "largest_E": keep(kinds[largest]),
            "kinds_raising_E": [k for k in kinds if above(kinds[k])], "praise_E": keep(kinds["praise"]),
            "bare_minus_praise": keep(pairs["bare_minus_praise"]), "bare_minus_expert": keep(pairs["bare_minus_expert"])}


def across(parts):
    """parts: {part key: the part's numbers}. Every family must be there."""
    missing = [key for _, key in FAMILIES if key not in parts]
    if missing:
        raise SystemExit(f"refused: parts missing {missing}")
    by = {fam: dict(family(parts[key]), part=key) for fam, key in FAMILIES}
    fams = [f for f, _ in FAMILIES]
    out = {"families": fams, "by_family": by,
           "bare_largest_E_in": [f for f in fams if by[f]["largest_E_kind"] == "bare"],
           "bare_above_expert_in": [f for f in fams if above(by[f]["bare_minus_expert"])],
           "bare_above_praise_in": [f for f in fams if above(by[f]["bare_minus_praise"])],
           "praise_raises_E_in": [f for f in fams if above(by[f]["praise_E"])]}
    out["bare_largest_E_in_every_family"] = len(out["bare_largest_E_in"]) == len(fams)
    out["bare_above_expert_in_every_family"] = len(out["bare_above_expert_in"]) == len(fams)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    parts = {}
    for _, key in FAMILIES:
        p = os.path.join(a.parts, f"{key}.json")
        if os.path.exists(p):
            parts[key] = json.load(open(p, encoding="utf-8"))
    res = across(parts)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    main()
