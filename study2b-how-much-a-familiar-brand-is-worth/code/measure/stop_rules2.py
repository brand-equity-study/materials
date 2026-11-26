"""The stop rules of the full measure, read on the main version for each model and category.

    more than 2 percent of its main-version responses have no letter;
2. one position or one letter takes more than 80 percent of the recommendations;
3. its recommendations do not follow the specifications: fewer than two of the three attributes are followed, where an
   attribute is followed when its best level has a coefficient above zero by its 95 percent interval (the pretest's
   rule) or when its worst level is never recommended in a list that also holds a better level, while its best level
   is recommended (a coefficient with no finite estimate, in the direction of the specification); fitted on the lists
   without brand names when the model has at least 50 of them, else on the lists with brand names;
4. its main price coefficient lies above zero by its 95 percent interval.
Intervals here come from the fit's covariance, not from a bootstrap. Writes the table as JSON and prints it.
"""
import argparse
import collections
import gzip
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parents[2]   # the package
sys.path.insert(0, str(HERE))
sys.path.insert(0, str((PKG / "common/parse_answer.py").parent))   # parse_answer.py and decline.py
sys.path.insert(0, str((PKG / "study3b-brand-knowledge-and-training-text-in-released-models/code/audit/parse_audit.py").parent))   # parse_audit.py
import analyze_mbbe2 as M  # noqa: E402
from decline import classify  # noqa: E402

MIN_LISTS = 50
UNREAD_LIMIT, CONCENTRATION_LIMIT = 0.02, 0.80


def read_items(path):
    op = gzip.open if str(path).endswith(".gz") else open
    return [json.loads(l) for l in op(path, "rt", encoding="utf-8")]


def readable(items, ans):
    from parse_audit import rating
    by_id = {it["id"]: it for it in items}
    out = {}
    for r in ans.itertuples(index=False):
        it = by_id.get(r.id)
        if it is None:
            continue
        ok = rating(r.answer)[0] is not None if it["cell"] == "rating" else r.letter in it["products"]
        c = out.setdefault(r.model, {}).setdefault(f"{it['version']} {it['cell']}", [0, 0])
        c[0] += int(ok)
        c[1] += 1
    return out


def above_zero(b, cov, j):
    return float(b[j] - 1.96 * math.sqrt(max(cov[j, j], 0.0)))


def cell(rows, gc):
    """rows: (item, letter, text) of one model and category's main version (with and without brand names)."""
    out = {"responses": len(rows)}
    missing = [t for _, L, t in rows if L not in "ABCDE" or not L]
    kinds = collections.Counter(classify(t) for t in missing)
    out["without_a_letter"] = len(missing)
    out["declines"] = kinds.get("decline", 0)
    out["without_a_letter_share"] = len(missing) / len(rows) if rows else None
    read = [(it, L) for it, L, _ in rows if L in it["products"]]
    pos = collections.Counter(it["products"][L]["position"] for it, L in read)
    let = collections.Counter(L for _, L in read)
    out["top_position_share"] = max(pos.values()) / len(read) if read else None
    out["top_letter_share"] = max(let.values()) / len(read) if read else None
    shown = [(it, L) for it, L in read if it["cell"] == "shown"]
    hidden = [(it, L) for it, L in read if it["cell"] == "hidden"]
    use, which = (hidden, "without brand names") if len(hidden) >= MIN_LISTS else (shown, "with brand names")
    out["specifications_fitted_on"] = which
    if len(use) >= MIN_LISTS:
        d = M.Design([it for it, _ in use], gc["market_centre"])
        _, _, b, cov = M.fit_cell([it for it, _ in use], [L for _, L in use], d)
        lows = {a: above_zero(b, cov, d.ix[f"a{a}_l2"]) for a in range(3)}
        # An attribute whose worst level is shown but never recommended, while its best level is, has no finite
        # coefficient (Haiku 5.5 never recommended a 13 MP smartphone camera in 1,600 lists), so its interval is
        # unbounded; it is followed, in the direction of the specification, and is recorded as separated.
        separated = []
        for a in range(3):
            # lists that hold the worst level beside a better one: is the worst level ever recommended there?
            mixed = [(it, L) for it, L in use if {p["levels"][a] for p in it["products"].values()} - {0}
                     and any(p["levels"][a] == 0 for p in it["products"].values())]
            worst = sum(it["products"][L]["levels"][a] == 0 for it, L in mixed)
            best = sum(it["products"][L]["levels"][a] == 2 for it, L in use)
            if mixed and worst == 0 and best > 0 and lows[a] <= 0:
                separated.append(a)
        out["attributes_best_level_above_zero"] = sum(v > 0 for v in lows.values())
        out["attributes_worst_level_never_recommended"] = separated
        out["attributes_followed"] = out["attributes_best_level_above_zero"] + len(separated)
    if len(shown) >= MIN_LISTS:
        d = M.Design([it for it, _ in shown], gc["market_centre"])
        _, _, b, cov = M.fit_cell([it for it, _ in shown], [L for _, L in shown], d)
        j = d.ix["logp"]
        se = math.sqrt(max(cov[j, j], 0.0))
        out["main_price_coefficient"] = [float(b[j]), float(b[j] - 1.96 * se), float(b[j] + 1.96 * se)]
    flags = []
    if out["without_a_letter_share"] is not None and out["without_a_letter_share"] > UNREAD_LIMIT:
        flags.append("more than 2 percent without a letter")
    if read and max(out["top_position_share"], out["top_letter_share"]) > CONCENTRATION_LIMIT:
        flags.append("one position or letter over 80 percent")
    if out.get("attributes_followed") is not None and out["attributes_followed"] < 2:
        flags.append("does not follow the specifications")
    if out.get("main_price_coefficient") and out["main_price_coefficient"][1] > 0:
        flags.append("main price coefficient above zero")
    out["flags"] = flags
    return out


def read(items, ans, gates):
    by_id = {it["id"]: it for it in items if it.get("version") == "main" and it["cell"] in ("shown", "hidden")}
    ans = ans[ans.id.isin(by_id)]
    res = {}
    for model, g in ans.groupby("model"):
        per = collections.defaultdict(list)
        for i, L, t in zip(g.id, g.letter, g.answer):
            per[by_id[i]["category"]].append((by_id[i], L or "", t or ""))
        res[model] = {cat: cell(rows, gates["categories"][cat]) for cat, rows in sorted(per.items())}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    ap.add_argument("--items", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz"))
    ap.add_argument("--gates", default=str(PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/GATES.json"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    items = read_items(a.items)
    gates = json.load(open(a.gates, encoding="utf-8"))
    text_ids = {it["id"] for it in items if it.get("version") in ("main", "rating")}
    ans = M.load_answers(a.answers, text_ids=text_ids)
    res = read(items, ans, gates)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    parts = readable(items, ans)
    out.with_name(out.stem + "-read.json").write_text(json.dumps(parts, indent=1) + "\n", encoding="utf-8", newline="\n")
    for model, p in parts.items():
        got, n = sum(v[0] for v in p.values()), sum(v[1] for v in p.values())
        low = min(p.items(), key=lambda kv: kv[1][0] / kv[1][1])
        print(f"{model:22s} read {got:,} of {n:,} responses ({100 * got / n:.1f} percent); lowest part {low[0]} "
              f"{100 * low[1][0] / low[1][1]:.1f} percent")
    for model, cats in res.items():
        for cat, c in cats.items():
            pc = c.get("main_price_coefficient")
            print(f"{model:22s} {cat:14s} n={c['responses']:5d} no-letter={c['without_a_letter_share']:.3f} "
                  f"(declines {c['declines']}) pos={c['top_position_share']:.2f} let={c['top_letter_share']:.2f} "
                  f"spec={c.get('attributes_followed')} "
                  f"price={'%.2f [%.2f, %.2f]' % tuple(pc) if pc else '-'} {'; '.join(c['flags']) or 'clean'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
