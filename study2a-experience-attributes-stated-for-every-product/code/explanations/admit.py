"""The admission of the judges with open weights on the stated sample (the analysis plan, the admission rule;
study2a-experience-attributes-stated-for-every-product/materials/explanations/analysis_plan.md). shares.py imports it; its record is in
study2a-experience-attributes-stated-for-every-product/materials/explanations/admission/admission.json.

    python study2a-experience-attributes-stated-for-every-product/code/explanations/admit.py --sample <items-sample.jsonl> --reference <folder of <id>.md>
                                          --judge <key>=<answers.jsonl[.gz]> [--judge ...] [--out ADMISSION.json]

A judge is admitted when it gives a readable reply to at least 95 per cent of the sample and Cohen's kappa of its
brand_any with the reference's is at least 0.70. Reported beside it and deciding nothing: agreement and kappa on
brand_any and on reason, error rates by stratum with their counts, and the agreement of every pair of judges.
"""
import argparse
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
# the answer parser of every study (common/parse_answer.py)
sys.path.insert(0, os.path.dirname(os.path.join(HERE, "..", "..", "..", "common", "parse_answer.py")))
from parse_answer import final_answer  # noqa: E402

REASONS = ("brand_property", "brand_reputation", "listed", "other")
MIN_READ, MIN_KAPPA = 0.95, 0.70


def parse(reply):
    """(reason, brand_any) from a judge's reply, after its reasoning is removed, or None when it cannot be read."""
    text = final_answer(reply or "")
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict):
            r, b = obj.get("reason"), str(obj.get("brand_any", "")).strip().lower()
            if r in REASONS and b in ("yes", "no"):
                return r, b
            return None
    return None


def kappa(a, b):
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return None if pe == 1 else (po - pe) / (1 - pe)


def compare(a, b, ids):
    ids = [i for i in ids if a.get(i) and b.get(i)]
    out = {"n": len(ids)}
    for k, j in (("brand_any", 1), ("reason", 0)):
        x, y = [a[i][j] for i in ids], [b[i][j] for i in ids]
        out[k] = {"agreement": sum(p == q for p, q in zip(x, y)) / len(ids) if ids else None, "kappa": kappa(x, y)}
    return out


def load_judge(path):
    opener = gzip.open if path.endswith(".gz") else open
    out = {}
    for line in opener(path, "rt", encoding="utf8"):
        r = json.loads(line)
        out[r["id"]] = parse(r.get("raw") or r.get("answer"))
    return out


def load_reference(folder):
    return {os.path.splitext(os.path.basename(f))[0]: parse(open(f, encoding="utf8").read())
            for f in glob.glob(os.path.join(folder, "*.md"))}


def stratum(x):
    return "requests" if x["source"] == "requests" else f"{x['names']}-info{x['info']}-{'open' if x['group'] == 'open' else 'closed'}"


def admit(sample, reference, judges):
    ids = [x["id"] for x in sample]
    by_id = {x["id"]: x for x in sample}
    res = {"sample": len(ids), "reference_read": sum(1 for i in ids if reference.get(i)), "rule":
           {"min_read": MIN_READ, "min_kappa_brand_any": MIN_KAPPA}, "judges": {}, "pairs": {}}
    for key, codes in judges.items():
        read = sum(1 for i in ids if codes.get(i)) / len(ids)
        c = compare(codes, reference, ids)
        errors = {}
        for s in sorted({stratum(x) for x in sample}):
            sid = [i for i in ids if stratum(by_id[i]) == s and codes.get(i) and reference.get(i)]
            errors[s] = {"n": len(sid), "brand_any_disagree": sum(codes[i][1] != reference[i][1] for i in sid)}
        k = c["brand_any"]["kappa"]
        res["judges"][key] = {"read": read, "vs_reference": c, "errors_by_stratum": errors,
                              "admitted": bool(read >= MIN_READ and k is not None and k >= MIN_KAPPA)}
    keys = sorted(judges)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            res["pairs"][f"{a}|{b}"] = compare(judges[a], judges[b], ids)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--judge", action="append", default=[])
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    sample = [json.loads(l) for l in open(a.sample, encoding="utf8") if l.strip()]
    judges = {k: load_judge(p) for k, p in (x.split("=", 1) for x in a.judge)}
    res = admit(sample, load_reference(a.reference), judges)
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf8"), indent=1)
    for k, v in res["judges"].items():
        c = v["vs_reference"]["brand_any"]
        print(f"{k:18s} read {v['read']:.3f}  brand_any agreement {c['agreement']} kappa {c['kappa']}  "
              f"admitted {v['admitted']}")


if __name__ == "__main__":
    main()
