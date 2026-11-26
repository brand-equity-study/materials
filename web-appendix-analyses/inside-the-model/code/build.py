"""The prompts of step B6 (the plan is PLAN.md in this folder): Study 2's dom2 build re-rendered from Study 2's
own code, plus two kinds of names-hidden prompts that define "better listed" inside the model, the character spans of
every product block, and the lists of pairs that the job compares.

    python jmr-2026/mechanism/build.py --out <folder> [--tables sr_laptops_01_dom,sr_earbuds_03_dom]

Refuses unless (1) the dom2 prompts it renders equal jmr-2026/study2/items/dom2/items.jsonl byte for byte (for a subset
of tables, the same lines in the same order), and (2) Study 2's gates b and c pass on every prompt. Gate a is reported:
it passes on the dom2 prompts and fails on both added kinds by design (in the spec swap the best product no longer
dominates; in the poor-reliability prompts the information rows differ between products).

Writes <out>/renderings.jsonl (one prompt a line, with its spans), <out>/pairs.jsonl, <out>/BUILD.json (counts, gate
results, sha256 of every file).
"""
import argparse
import copy
import hashlib
import json
import os
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STUDY2 = os.path.join(ROOT, "jmr-2026", "study2")
for p in (ROOT, STUDY2):
    if p not in sys.path:
        sys.path.insert(0, p)
import study2_tables as S  # noqa: E402
import dominant_sets as D  # noqa: E402
import gates  # noqa: E402

DOM2_ITEMS = os.path.join(STUDY2, "items", "dom2", "items.jsonl")
TRIALS = 10
RUNGS = (0, 2)
WARRANTY_GOOD, WARRANTY_POOR = "Warranty: 2 years", "Warranty: 3 months"
FAIL_GOOD = "First-year failure or return rate (independent survey): 2% of units"
FAIL_POOR = "First-year failure or return rate (independent survey): 15% of units"
SPANS = ("brand", "postname", "lastline", "close", "namebrand")


def dom2_tables():
    tables = S.load_tables()
    dom, key = D.build(tables)
    gates.KEY.update(key)
    return dom


def block_bounds(user, letter):
    """(start, end) of a product's block in the user message: from its header to the end of its last line."""
    head = f"--- Product {letter} ---\n"
    s = user.index(head)
    if user.count(head) != 1:
        raise ValueError(f"header of product {letter} appears {user.count(head)} times")
    e = user.index("\n\n", s)
    return s, e


def spans_of(user, letters):
    """{letter: {span: [start, end)}} character offsets in the user message (see PLAN.md, 'Where in the prompt')."""
    out = {}
    for L in letters:
        s, e = block_bounds(user, L)
        block = user[s:e]
        b0 = block.index("\nBrand: ") + len("\nBrand: ")
        b1 = block.index("\n", b0)
        p0 = block.index("\nPrice: ") + 1
        last0 = block.rindex("\n") + 1
        if user[e:e + 2] != "\n\n":
            raise ValueError(f"block {L} does not close on a blank line")
        # amendment 1: the brand name on the Name line ("Name: Dell laptop"); with the names hidden, the whole label
        n0 = block.index("\nName: ") + len("\nName: ")
        n1 = block.index("\n", n0)
        brand = block[b0:b1]
        nb = [s + n0, s + n0 + len(brand)] if block[n0:n1].startswith(brand + " ") else [s + n0, s + n1]
        out[L] = {"brand": [s + b0, s + b1], "postname": [s + p0, e + 2], "lastline": [s + last0, e],
                  "close": [e, e + 2], "namebrand": nb}
    return out


def as_rendering(item, kind, base_id="", target=""):
    """A Study 2 item dict, with the fields this step adds."""
    r = dict(item)
    r["kind"] = kind
    r["base_id"] = base_id or item["id"]
    r["target"] = target
    letters = sorted(item["products"])
    r["letters"] = letters
    r["partner"] = next((L for L, p in item["products"].items() if p["orig"] == item["partner_plan"]), "")
    r["spans"] = spans_of(item["user"], letters)
    return r


def render_set(dom, table_ids):
    """dom2 items (in Study 2's order) and the two added kinds; returns (dom2_items, renderings)."""
    dom2_items, rend = [], []
    for tid in table_ids:
        t = dom[tid]
        for trial in range(TRIALS):
            plan = S.trial_plan(t, trial)
            for names in S.NAMES:
                for info in S.INFOS:
                    for rung in RUNGS:
                        r = S.render(t, trial, names, info, rung, plan)
                        it = {"id": S.item_id("dom2", tid, trial, names, info, rung), "build": "dom2",
                              "cell": S.cell_label(names, info, rung), **r["meta"],
                              "system": r["system"], "user": r["user"]}
                        dom2_items.append(it)
                        rend.append(as_rendering({**it, "partner_plan": plan["partner"]}, "dom2"))
            # spec swap: the best product's and the partner's specification rows exchanged, names hidden
            sw = copy.deepcopy(t)
            ib = next(i for i, p in enumerate(sw["products"]) if p["best"])
            ip = next(i for i, p in enumerate(sw["products"]) if p["orig"] == plan["partner"])
            sw["products"][ib]["specs"], sw["products"][ip]["specs"] = sw["products"][ip]["specs"], sw["products"][ib]["specs"]
            for info in S.INFOS:
                for rung in RUNGS:
                    r = S.render(sw, trial, "hidden", info, rung, plan)
                    base = S.item_id("dom2", tid, trial, "hidden", info, rung)
                    it = {"id": "sw-" + base, "build": "b6", "cell": "specswap-" + S.cell_label("hidden", info, rung),
                          **r["meta"], "system": r["system"], "user": r["user"], "partner_plan": plan["partner"]}
                    rend.append(as_rendering(it, "specswap", base))
            # poor reliability: one product's warranty and failure rows made worse, names hidden, information shown
            for rung in RUNGS:
                r = S.render(t, trial, "hidden", 1, rung, plan)
                base = S.item_id("dom2", tid, trial, "hidden", 1, rung)
                disp = {p["orig"]: L for L, p in r["meta"]["products"].items()}
                for who, orig in (("best", next(p["orig"] for p in t["products"] if p["best"])),
                                  ("partner", plan["partner"])):
                    L = disp[orig]
                    user = poor_reliability(r["user"], L)
                    it = {"id": f"pr{who[0]}-" + base, "build": "b6", "cell": f"poorrel-{who}-" + S.cell_label("hidden", 1, rung),
                          **r["meta"], "system": r["system"], "user": user, "partner_plan": plan["partner"]}
                    rend.append(as_rendering(it, "poorrel", base, target=L))
    return dom2_items, rend


def poor_reliability(user, letter):
    s, e = block_bounds(user, letter)
    block = user[s:e]
    if block.count(WARRANTY_GOOD) != 1 or block.count(FAIL_GOOD) != 1:
        raise ValueError(f"block {letter} lacks the information rows")
    block = block.replace(WARRANTY_GOOD, WARRANTY_POOR).replace(FAIL_GOOD, FAIL_POOR)
    return user[:s] + block + user[e:]


def first_shown(r, a, b):
    order = r["order"]
    return a if order.index(a) < order.index(b) else b


def make_pairs(rend):
    """Every pair of PLAN.md's table of contrasts. Each pair: version a minus version b, at product `letter`."""
    by = {(r["kind"], r["table"], r["trial"], r["names"], r["info"], r["rung"], r["target"]): r for r in rend}
    pairs = []

    def add(contrast, a, b, letter):
        assert a["category"] == b["category"] and a["table"] == b["table"]
        pairs.append({"contrast": contrast, "a": a["id"], "b": b["id"], "letter": letter, "table": a["table"],
                      "category": a["category"], "trial": a["trial"], "info": a["info"], "rung": a["rung"],
                      "is_best": letter == a["best"], "partner": a["partner"], "best": a["best"]})

    poor = {(x["base_id"], x["cell"].split("-")[1]): x for x in rend if x["kind"] == "poorrel"}
    for r in rend:
        if r["kind"] != "dom2" or r["names"] != "original":
            continue
        o = r
        c = by[("dom2", r["table"], r["trial"], "crossed", r["info"], r["rung"], "")]
        h = by[("dom2", r["table"], r["trial"], "hidden", r["info"], r["rung"], "")]
        w = by[("specswap", r["table"], r["trial"], "hidden", r["info"], r["rung"], "")]
        best, partner = r["best"], r["partner"]
        assert c["order"] == o["order"] == h["order"] == w["order"] and c["best"] == best and c["partner"] == partner
        f = first_shown(r, best, partner)
        # name: familiar minus invented, at the swapped product shown first
        add("name", c, o, f) if f == best else add("name", o, c, f)
        # spec: better minus worse listed specifications, at the slot shown first
        add("spec", h, w, f) if f == best else add("spec", w, h, f)
        if r["info"] == 1:
            for who in ("best", "partner"):
                pr = poor[(h["id"], who)]
                add("reliability", h, pr, pr["target"])
        if r["rung"] == 2:
            h0 = by[("dom2", r["table"], r["trial"], "hidden", r["info"], 0, "")]
            add("price", h, h0, best)
    return pairs


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dom2_committed_sha():
    for line in open(os.path.join(os.path.dirname(DOM2_ITEMS), "SHA256SUMS"), encoding="utf8"):
        h, name = line.split()
        if name == "items.jsonl":
            return h
    raise SystemExit("dom2's SHA256SUMS has no line for items.jsonl")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables", default="all")
    a = ap.parse_args(argv)
    dom = dom2_tables()
    ids = list(dom) if a.tables == "all" else a.tables.split(",")
    for t in ids:
        if t not in dom:
            sys.exit(f"{t} is not a dom2 table")
    dom2_items, rend = render_set(dom, ids)

    # (1) dom2 reproduced byte for byte
    keep = set(ids)
    ref = [l for l in open(DOM2_ITEMS, encoding="utf8").read().split("\n") if l and json.loads(l)["table"] in keep]
    mine = [json.dumps(it, ensure_ascii=False) for it in dom2_items]
    if ref != mine:
        bad = next(i for i, (x, y) in enumerate(zip(ref, mine)) if x != y) if len(ref) == len(mine) else "length"
        sys.exit(f"refused: the re-rendered dom2 prompts differ from {DOM2_ITEMS} (first difference: {bad})")
    # the committed hash (SHA256SUMS), not the working copy, whose line endings git may have changed on checkout
    committed = dom2_committed_sha()
    if a.tables == "all" and committed != hashlib.sha256(("\n".join(mine) + "\n").encode("utf8")).hexdigest():
        sys.exit("refused: the re-rendered dom2 file does not hash to the one in dom2's SHA256SUMS")

    # (2) gates b and c on every prompt (the added kinds included); gate a reported
    items_for_gates = [{k: v for k, v in r.items() if k in ("id", "table", "names", "best", "system", "user", "info",
                                                              "rung", "trial", "cell", "products", "order")} for r in rend]
    gb = gates.gate_b(items_for_gates, dom)
    gc = gates.gate_c(items_for_gates, dom)
    if gb or gc:
        for f in (gb + gc)[:20]:
            print("   ", f)
        sys.exit(f"refused: gate b {len(gb)} and gate c {len(gc)} failures")
    ga = {}
    for kind in ("dom2", "specswap", "poorrel"):
        sub = [x for x, r in zip(items_for_gates, rend) if r["kind"] == kind]
        ga[kind] = len(gates.gate_a(sub))

    pairs = make_pairs(rend)
    os.makedirs(a.out, exist_ok=True)
    rp, pp = os.path.join(a.out, "renderings.jsonl"), os.path.join(a.out, "pairs.jsonl")
    with open(rp, "w", encoding="utf8", newline="\n") as f:
        for r in rend:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(pp, "w", encoding="utf8", newline="\n") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    rec = {"tables": ids, "renderings": dict(Counter(r["kind"] for r in rend)), "pairs": dict(Counter(p["contrast"] for p in pairs)),
           "categories": len({dom[t]["category"] for t in ids}), "dom2_reproduced": True,
           "gate_b_failures": 0, "gate_c_failures": 0, "gate_a_failures": ga,
           "sha256": {"renderings.jsonl": sha(rp), "pairs.jsonl": sha(pp), "dom2/items.jsonl": committed}}
    json.dump(rec, open(os.path.join(a.out, "BUILD.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    main()
