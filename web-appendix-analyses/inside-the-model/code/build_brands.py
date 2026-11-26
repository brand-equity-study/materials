"""The prompts of the brand-by-brand read (step B6, amendment 2 of PLAN.md, written before its jobs): built from Study
2's dom2 tables with Study 2's own renderer, names shown, without the information rows, at rung 0, 10 trials.

  renamed   each familiar product in turn shown with an invented name, the rest of the original cell unchanged. The
            replacement name is the same for every product of a table and trial and rotates over the trials; it is
            always the invented name of a table in another category, so that a name suggesting a category (Dentara,
            Primebook) is never the replacement in its own category.
  onbest    the crossed cell with every familiar product as the partner in turn: the best product shows that brand,
            and that brand's product shows the table's own invented name.
  short     a chat prompt with the category noun before the name ("Think of headphones made by Sony. In one word, how
            would you describe them?"), for the 63 familiar brands in each of their categories and the 28 invented
            names in every category; read at the name's last token and at the answer's first token.

    python jmr-2026/mechanism/build_brands.py --out <folder>

Writes <out>/brands.jsonl (the prompts, with the character spans of build.py for the table prompts and of the name for
the short ones), <out>/brand_pairs.jsonl and <out>/BRANDS.json; refuses unless Study 2's gate c passes on every table
prompt and every renamed or onbest prompt differs from its original cell only where it should.
"""
import argparse
import copy
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as BLD  # noqa: E402

S = BLD.S
gates = BLD.gates
TRIALS = 10
SHORT = ("Think of {plural} made by {name}. In one word, how would you describe them?",
         "Picture a shopper looking at {plural} from {name}. In one word, what would the shopper expect of them?",
         "Among {plural}, consider the ones sold under the name {name}. Describe them in one word.")
PLURAL = {"laptop": "laptops", "smartphone": "smartphones", "TV": "TVs", "headphones": "headphones",
          "running shoes": "running shoes", "coffee maker": "coffee makers", "earbuds": "earbuds",
          "smartwatch": "smartwatches", "robot vacuum": "robot vacuums", "Bluetooth speaker": "Bluetooth speakers",
          "keyboard": "keyboards", "external SSD": "external SSDs", "water bottle": "water bottles",
          "electric toothbrush": "electric toothbrushes", "backpack": "backpacks", "blender": "blenders",
          "WiFi router": "WiFi routers", "monitor": "monitors", "tablet": "tablets", "camera": "cameras"}


def invented_names(dom):
    """{invented name: its table's category}: every product of the dom2 tables with an invented name (the best product
    of each table, and one other product, Vistara)."""
    out = {}
    for t in dom.values():
        for p in t["products"]:
            if p["kind"] == "invented":
                out[p["brand"]] = t["category"]
    return out


def replacement(dom, tid, trial, inv):
    """The invented name that replaces a familiar one in table tid and trial: from another category, rotated."""
    cat = dom[tid]["category"]
    pool = sorted(n for n, c in inv.items() if c != cat)
    h = int(hashlib.sha256(f"b6-amendment2|{tid}".encode()).hexdigest()[:8], 16)
    return pool[(h + trial) % len(pool)]


def table_prompt(t, trial, names, plan, kind, base_id, extra):
    r = S.render(t, trial, names, 0, 0, plan)
    # the product's own letter in the id: a brand can hold two products of one table (Oral-B among the toothbrushes)
    it = {"id": f"{kind}-{base_id}-{extra['product_orig']}", "build": "b6-brands", "cell": f"{kind}-{names}",
          **r["meta"], "system": r["system"], "user": r["user"], "partner_plan": plan["partner"]}
    rr = BLD.as_rendering(it, kind, base_id)
    rr.update(extra)
    return rr


def build(dom, inv=None):
    """inv: the invented names of every dom2 table (also when dom is a subset, so that the replacements and the short
    prompts do not depend on which tables are built)."""
    inv = inv or invented_names(dom)
    rows, pairs = [], []
    for tid, t in dom.items():
        for trial in range(TRIALS):
            plan = S.trial_plan(t, trial)
            o = BLD.as_rendering({"id": S.item_id("dom2", tid, trial, "original", 0, 0), "build": "dom2",
                                  "cell": S.cell_label("original", 0, 0), **S.render(t, trial, "original", 0, 0, plan)["meta"],
                                  "system": S.render(t, trial, "original", 0, 0, plan)["system"],
                                  "user": S.render(t, trial, "original", 0, 0, plan)["user"],
                                  "partner_plan": plan["partner"]}, "dom2")
            repl = replacement(dom, tid, trial, inv)
            disp = {p["orig"]: L for L, p in o["products"].items()}
            for p in t["products"]:
                if p["best"] or not p["kind"].startswith("familiar"):
                    continue
                L = disp[p["orig"]]
                # renamed: this product alone under the invented replacement name
                t2 = copy.deepcopy(t)
                q = next(x for x in t2["products"] if x["orig"] == p["orig"])
                q["brand"], q["kind"] = repl, "invented"
                rn = table_prompt(t2, trial, "original", plan, "renamed", o["id"], {"target_brand": p["brand"],
                                  "target": L, "replacement": repl, "target_kind": p["kind"], "product_orig": p["orig"]})
                rows.append(rn)
                pairs.append({"contrast": "renamed", "a": o["id"], "b": rn["id"], "letter": L, "brand": p["brand"],
                              "table": tid, "category": t["category"], "trial": trial, "best": o["best"]})
                # onbest: the crossed cell with this product as the partner
                plan_b = dict(plan, partner=p["orig"])
                ob = table_prompt(t, trial, "crossed", plan_b, "onbest", o["id"], {"target_brand": p["brand"],
                                  "target": o["best"], "brand_product": L, "target_kind": p["kind"],
                                  "product_orig": p["orig"]})
                ob["partner"] = L
                rows.append(ob)
                pairs.append({"contrast": "onbest", "a": ob["id"], "b": o["id"], "letter": o["best"], "brand": p["brand"],
                              "partner": L, "table": tid, "category": t["category"], "trial": trial, "best": o["best"],
                              "best_first": o["order"].index(o["best"]) < o["order"].index(L)})
            rows.append(o)
    # short prompts, the category noun before the name
    real = defaultdict(set)
    for t in dom.values():
        for p in t["products"]:
            if p["kind"].startswith("familiar"):
                real[p["brand"]].add(t["category"])
    cats = sorted({t["category"] for t in dom.values()})
    shorts = [(b, c, "real") for b in sorted(real) for c in sorted(real[b])] + \
             [(n, c, "invented") for n in sorted(inv) for c in cats]
    for name, cat, kind in shorts:
        for k, tpl in enumerate(SHORT):
            user = tpl.format(plural=PLURAL[S.NOUN[cat]], name=name)
            s0 = user.rindex(name)                     # the name is the last of the two slots in every phrasing
            rows.append({"id": f"short-{kind}-{cat}-{name}-p{k}", "kind": "short", "name": name, "name_kind": kind,
                         "category": cat, "phrasing": k, "system": "", "user": user, "name_span": [s0, s0 + len(name)]})
    return rows, pairs, inv


def check(rows, dom):
    """Gate c on every table prompt; each renamed prompt differs from its original only in one product's Name and
    Brand lines, each onbest prompt only in the best product's and the brand's product's."""
    byid = {r["id"]: r for r in rows}
    if len(byid) != len(rows):
        return [f"{len(rows) - len(byid)} prompt ids appear twice"]
    tab = [r for r in rows if r["kind"] != "short"]
    fails = gates.gate_c([{k: r[k] for k in ("id", "table", "names", "best", "system", "user")} for r in tab], dom)
    for r in tab:
        if r["kind"] not in ("renamed", "onbest"):
            continue
        o = byid[r["base_id"]]
        a, b = o["user"].split("\n"), r["user"].split("\n")
        if len(a) != len(b):
            fails.append(f"{r['id']}: a different number of lines")
            continue
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        want = 2 if r["kind"] == "renamed" else 4
        if len(diff) != want or not all(x.startswith(("Name: ", "Brand: ")) for x, _ in diff):
            fails.append(f"{r['id']}: differs from its original in {len(diff)} lines")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables", default="all", help="a comma-separated subset of dom2 tables (for tests and pilots)")
    a = ap.parse_args(argv)
    dom = BLD.dom2_tables()
    full = dom
    if a.tables != "all":
        dom = {t: dom[t] for t in a.tables.split(",")}
    rows, pairs, inv = build(dom, invented_names(full))
    fails = check(rows, dom)
    if fails:
        for f in fails[:20]:
            print("   ", f)
        sys.exit(f"refused: {len(fails)} failures")
    os.makedirs(a.out, exist_ok=True)
    rp, pp = os.path.join(a.out, "brands.jsonl"), os.path.join(a.out, "brand_pairs.jsonl")
    with open(rp, "w", encoding="utf8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(pp, "w", encoding="utf8", newline="\n") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    rec = {"prompts": dict(Counter(r["kind"] for r in rows)), "pairs": dict(Counter(p["contrast"] for p in pairs)),
           "brands": len({p["brand"] for p in pairs}), "invented_names": len(inv),
           "short_prompts": dict(Counter(r["name_kind"] for r in rows if r["kind"] == "short")),
           "onbest_best_first": sum(p.get("best_first", False) for p in pairs if p["contrast"] == "onbest"),
           "gate_c_failures": 0, "sha256": {"brands.jsonl": BLD.sha(rp), "brand_pairs.jsonl": BLD.sha(pp)}}
    json.dump(rec, open(os.path.join(a.out, "BRANDS.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    main()
