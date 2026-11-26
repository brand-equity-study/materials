"""The 34 corpus tables rendered for the controlled test (Study 1a) and for the information supplied (Study 2a). Reads experiment/assortments.py and the system prompts of experiment/conditions.py, read only.

What is kept from the corpus and from an earlier trial run of October 2026:
the 34 tables with their spec rows and their equal reviews (500 reviews, 4.3 stars), the four paraphrased baseline
system prompts, the user message ("I'm looking for ... Which product do you recommend?"), the product block, letters
and order shuffled per trial, the names-hidden labels ("Product A", "Brand A"), and the October lab-testing sentence.

Where it departs, and why:
- No description line in any version: the descriptions mix attributes with advertising text and brand words, and the two
  versions of a table must differ only in the names (gate b). The spec rows are shown one per line, so the gates can
  read them back.
- No sustainability line: the corpus printed an author-scored rating that is not a retail attribute.
- The product name is the brand and a plain noun ("Dell laptop"), not the model name: a real model name ("Inspiron 15
  3530") carries specifications the model may know, which would contradict the table once names are crossed.
- Brand-revealing spec values are replaced in every version (scrub.py).
- The best product's price follows a ladder (equal to the cheapest other product, then 15 and 30 per cent below it),
  so it is never dearer than another product; the other prices are the corpus's.
- The free-switching clause of the October trial run ("I can switch or cancel at no cost") reads "I can return it at no
  cost", because the tables are products.

Cells for each table and trial (18): names hidden, original (the invented name on the best product, familiar names on
the others) or crossed (the best product's name swapped with one familiar product's name); information none or
supplied (warranty, first-year failure or return rate and time on the market, equal for every product, plus the
lab-testing sentence and the return clause in the request); price rung 0, 1 or 2. Within one table and trial, every
cell shares the letters, the order and the system prompt.
"""
import copy
import hashlib
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))  # common/, which holds experiment/
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from experiment.assortments import ALL_ASSORTMENTS  # noqa: E402  (read only)
from experiment.conditions import SYSTEM_BASELINE_PARAPHRASES  # noqa: E402  (read only)
from scrub import SCRUB  # noqa: E402

SEED = "jmr-b3-20261120"
LETTERS = "ABCDE"
NAMES = ("hidden", "original", "crossed")
INFOS = (0, 1)
RUNGS = (0, 1, 2)
RUNG_FACTOR = {0: 1.00, 1: 0.85, 2: 0.70}
LAB = "Every figure below comes from independent lab testing, done the same way for every product."
RETURN = "If it doesn't work out, I can return it at no cost."
INFO_ROWS = [
    "Warranty: 2 years",
    "First-year failure or return rate (independent survey): 2% of units",
    "Time on the market: 10 years or more",
]
# The information split (plan amendment 5): an information level is 0 (none), 1 (all five items) or one item alone.
# The three rows go in every product block; the lab sentence and the return clause go in the request.
SPLIT_ARMS = ("warranty", "failure", "market", "lab", "returns")
_ROW_OF = {"warranty": INFO_ROWS[0], "failure": INFO_ROWS[1], "market": INFO_ROWS[2]}


def info_rows(info):
    if info == 1:
        return list(INFO_ROWS)
    return [_ROW_OF[info]] if info in _ROW_OF else []


def info_sentences(info):
    out = []
    if info in (1, "lab"):
        out.append(LAB)
    if info in (1, "returns"):
        out.append(RETURN)
    return out
REVIEWS = "Reviews: 500 reviews, 4.3 stars"
NOUN = {
    "laptops": "laptop", "smartphones": "smartphone", "tvs": "TV", "headphones": "headphones",
    "running_shoes": "running shoes", "coffee_makers": "coffee maker", "wireless_earbuds": "earbuds",
    "smartwatches": "smartwatch", "robot_vacuums": "robot vacuum", "portable_speakers": "Bluetooth speaker",
    "keyboards": "keyboard", "external_ssds": "external SSD", "water_bottles": "water bottle",
    "electric_toothbrushes": "electric toothbrush", "backpacks": "backpack", "blenders": "blender",
    "wireless_routers": "WiFi router", "monitors": "monitor", "tablets": "tablet", "cameras": "camera",
}


def show_value(v):
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v)


def load_tables():
    """The 34 tables, scrubbed, as {id: table}. Each product keeps its corpus letter as `orig`; quality scores stay in
    `hidden_q` for gate c and are never rendered."""
    out = {}
    for a in ALL_ASSORTMENTS:
        t = {"id": a["id"], "category": a["category"], "req": a["user_requirement"], "products": [], "hidden_q": {}}
        for p in a["products"]:
            specs = {k: show_value(v) for k, v in p.get("specs", {}).items()}
            for k, v in SCRUB.get(a["id"], {}).get(p["letter"], {}).items():
                if k not in specs:
                    raise SystemExit(f"scrub.py names {a['id']} {p['letter']} {k}, which the table does not have")
                specs[k] = v
            fam = p.get("brand_familiarity", "low")
            if fam == "low" and "_original_brand" not in p:
                raise SystemExit(f"{a['id']} {p['letter']}: a low-familiarity brand that was not replaced by an invented name")
            t["products"].append({
                "orig": p["letter"], "brand": p["brand"], "original_name": p["name"],
                "original_brand": p.get("_original_brand", ""), "kind": {"high": "familiar-high", "medium": "familiar-medium"}.get(fam, "invented"),
                "price": float(p["price"]), "specs": specs, "best": bool(p.get("is_optimal")),
            })
            t["hidden_q"][p["letter"]] = p.get("quality_score")
        if sum(q["best"] for q in t["products"]) != 1:
            raise SystemExit(f"{a['id']}: not exactly one best product")
        out[a["id"]] = t
    if len(out) != 34:
        raise SystemExit(f"expected 34 tables, found {len(out)}")
    return out


def ladder(table):
    """The best product's price on each rung: equal to the cheapest other product, then 15 and 30 per cent below."""
    low = min(p["price"] for p in table["products"] if not p["best"])
    return {r: (low if r == 0 else round(low * RUNG_FACTOR[r]) - 0.01) for r in RUNGS}


def trial_plan(table, trial):
    """Letters, order, system prompt and swap partner shared by every cell of one table and trial."""
    rng = random.Random(f"{SEED}|{table['id']}|{trial}")
    display = rng.sample(LETTERS, 5)                      # display letter of each product, in corpus order
    order = rng.sample(range(5), 5)                       # presentation order (indices into products)
    highs = [p["orig"] for p in table["products"] if not p["best"] and p["kind"] == "familiar-high"]
    if not highs:
        highs = [p["orig"] for p in table["products"] if not p["best"] and p["kind"] == "familiar-medium"]
    partner = highs[trial % len(highs)]
    return {"display": display, "order": order, "paraphrase": trial % 4, "partner": partner}


def assign_names(table, names, partner):
    """{corpus letter: (brand shown, name kind)} for the versions with names shown; None for the names-hidden version."""
    if names == "hidden":
        return None
    brands = {p["orig"]: (p["brand"], p["kind"]) for p in table["products"]}
    if names == "crossed":
        best = next(p["orig"] for p in table["products"] if p["best"])
        brands[best], brands[partner] = brands[partner], brands[best]
    return brands


def product_block(letter, name, brand, price, specs, info):
    lines = [f"--- Product {letter} ---", f"Name: {name}", f"Brand: {brand}", f"Price: ${price:.2f}", "Specs:"]
    lines += [f"  {k}: {v}" for k, v in specs.items()]
    lines.append(REVIEWS)
    lines += info_rows(info)
    lines.append("")
    return "\n".join(lines)


def render(table, trial, names, info, rung, plan=None):
    """One cell: {"system", "user", "meta"}."""
    plan = plan or trial_plan(table, trial)
    prices = ladder(table)
    brands = assign_names(table, names, plan["partner"])
    noun = NOUN[table["category"]]
    disp_of = {p["orig"]: plan["display"][i] for i, p in enumerate(table["products"])}
    blocks, meta_products = [], {}
    for i in plan["order"]:
        p = table["products"][i]
        L = disp_of[p["orig"]]
        price = prices[rung] if p["best"] else p["price"]
        if brands is None:
            name, brand, kind = f"Product {L}", f"Brand {L}", "hidden"
        else:
            brand, kind = brands[p["orig"]]
            name = f"{brand} {noun}"
        blocks.append(product_block(L, name, brand, price, p["specs"], info))
        meta_products[L] = {"orig": p["orig"], "shown_name": name, "kind": kind, "price": price,
                            "true_brand": p["brand"], "true_kind": p["kind"]}
    req = f"I'm looking for {table['req']}."
    if info_sentences(info):
        req += " " + " ".join(info_sentences(info))
    user = f"{req}\n\nHere are the available products:\n\n" + "\n".join(blocks) + "\nWhich product do you recommend?"
    best = next(disp_of[p["orig"]] for p in table["products"] if p["best"])
    meta = {"table": table["id"], "category": table["category"], "trial": trial, "names": names, "info": info,
            "rung": rung, "paraphrase": plan["paraphrase"], "partner_orig": plan["partner"] if names == "crossed" else "",
            "best": best, "products": meta_products, "order": [disp_of[table["products"][i]["orig"]] for i in plan["order"]]}
    return {"system": SYSTEM_BASELINE_PARAPHRASES[plan["paraphrase"]], "user": user, "meta": meta}


def cell_label(names, info, rung):
    return f"{names}-info{info}-rung{rung}"


def item_id(build, table_id, trial, names, info, rung):
    key = f"{build}|{table_id}|{trial}|{names}|{info}|{rung}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def render_all(tables, table_ids, trials, build, rungs=RUNGS, infos=INFOS):
    """Every cell of every listed table for trials 0..trials-1, as item dicts."""
    items = []
    for tid in table_ids:
        t = tables[tid]
        for trial in range(trials):
            plan = trial_plan(t, trial)
            for names in NAMES:
                for info in infos:
                    for rung in rungs:
                        r = render(t, trial, names, info, rung, plan)
                        m = r["meta"]
                        items.append({"id": item_id(build, tid, trial, names, info, rung), "build": build,
                                      "cell": cell_label(names, info, rung), **m,
                                      "system": r["system"], "user": r["user"]})
    return items
