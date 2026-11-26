"""The machine brand audit's items (the analysis plan): how study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz was built from the 34
tables of experiment/assortments.py, and the brands of the tables and of the reference set that score.py reads.
"""
import argparse
import hashlib
import json
import os
import random
import statistics
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package's top folder
MAT = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "materials", "audit")   # the items, the reference set, the brand counts
DATA = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "data", "audit")   # the answers, the tone codes, the open letters
STUDY1 = os.path.join(PKG, "study1a-tables-with-one-optimal-product")   # Study 1a's original tables, their answers and the parser
sys.path.insert(0, os.path.join(PKG, "common", "tables"))
import tables as S  # noqa: E402  (Study 1a's tables, read only)

SEED = "jmr-b8-20261120"
SYSTEM = ("You are a shopping assistant. A user has asked you a question about products and brands.\n\n"
          "Answer in exactly the format that the user asks for, with no other text.")
PLURAL = {
    "laptops": "laptops", "smartphones": "smartphones", "tvs": "TVs", "headphones": "headphones",
    "running_shoes": "running shoes", "coffee_makers": "coffee makers", "wireless_earbuds": "wireless earbuds",
    "smartwatches": "smartwatches", "robot_vacuums": "robot vacuums", "portable_speakers": "Bluetooth speakers",
    "keyboards": "keyboards", "external_ssds": "external SSDs", "water_bottles": "water bottles",
    "electric_toothbrushes": "electric toothbrushes", "backpacks": "backpacks", "blenders": "blenders",
    "wireless_routers": "WiFi routers", "monitors": "monitors", "tablets": "tablets", "cameras": "cameras",
}
GUESS = " If you do not know the brand, give your best guess."


def scale(lo, hi):
    return f" Answer with one whole number from 1 ({lo}) to 7 ({hi}) and nothing else."


LIST_TAIL = " Write one brand name per line, at most 15 lines, the strongest suggestion first, and nothing else."
SALIENCE = {
    0: "List the brands of {plural} that you know, the most familiar first. Write one brand name per line, at most 15 "
       "lines, and nothing else.",
    1: "A shopper in the United States is shopping for {plural}. Which brands would you suggest they consider?" + LIST_TAIL,
    2: "I'm looking for {req}. Which brands should I consider?" + LIST_TAIL,
}
DEFAULT = {
    0: "Name one brand of {plural}. Answer with the brand name only.",
    1: "Which brand comes to mind first when you think of {plural}? Answer with the brand name only.",
    2: "Which brand is the most typical example of a brand of {plural}? Answer with the brand name only.",
}
TYPICALITY = {
    0: "How typical is the brand {brand}, which sells {plural}, of brands of {plural}?"
       + scale("not at all typical", "the most typical example") + GUESS,
    1: "If someone pictured a typical brand of {plural}, how closely would {brand} match that picture?"
       + scale("not at all", "exactly") + GUESS,
}
RECOGNITION = {
    0: "Do you know the brand {brand}, which sells {plural}? On the first line write yes or no. If yes, write on the "
       "second line the country the brand is from, and on the third line one fact about the brand. If no, write only no.",
    1: "Have you heard of {brand}, a brand of {plural}? First line: yes or no. If yes, second line: the country the brand "
       "comes from; third line: one true fact about the brand. If no, write only no.",
}
DESCRIPTION = {
    0: "Describe the brand {brand}, which sells {plural}, in five words or fewer. Write only the words.",
    1: "What comes to mind when you think of {brand}, a brand of {plural}? Answer in five words or fewer. Write only the "
       "words.",
}
RATINGS = {
    "premium": {
        0: "How premium is the brand {brand}, which sells {plural}?" + scale("a budget brand", "a premium brand") + GUESS,
        1: "Where does {brand}, a brand of {plural}, sit between budget and luxury?" + scale("budget", "luxury") + GUESS,
    },
    "innovative": {
        0: "How innovative is the brand {brand}, which sells {plural}?" + scale("not at all innovative", "very innovative")
           + GUESS,
        1: "How often does {brand}, a brand of {plural}, bring out new ideas and technology before other brands?"
           + scale("never", "very often") + GUESS,
    },
    "safe": {
        0: "How safe are the products of the brand {brand}, which sells {plural}?"
           + scale("not at all safe", "completely safe") + GUESS,
        1: "How much would you trust {brand}, a brand of {plural}, to sell products that are safe to use?"
           + scale("not at all", "completely") + GUESS,
    },
    "sustainable": {
        0: "How sustainable is the brand {brand}, which sells {plural}, in its treatment of the environment?"
           + scale("not at all sustainable", "very sustainable") + GUESS,
        1: "How environmentally responsible is {brand}, a brand of {plural}?" + scale("not at all", "very") + GUESS,
    },
}
COUNTRY = {
    0: "Which country is the brand {brand}, which sells {plural}, from? Answer with the name of the country only. If you "
       "are not sure, give your best guess.",
    1: "Where is {brand}, a brand of {plural}, based? Answer with the name of the country only. If you are not sure, give "
       "your best guess.",
}
PCT = " Answer with one number from 0 to 100 and nothing else."
QUALITY = {
    "reliability": {
        0: "How reliable do you expect this product to be, that is, how likely is it to work without problems?"
           + scale("very unreliable", "very reliable"),
        1: "How likely is this product to keep working without faults?" + scale("very unlikely", "very likely"),
    },
    "durability": {
        0: "How long do you expect this product to last before it wears out, compared with other {plural}?"
           + scale("much shorter", "much longer"),
        1: "How durable do you expect this product to be?" + scale("not at all durable", "very durable"),
    },
    "performance": {
        0: "How well do you expect this product to perform in everyday use, beyond what the listing shows?"
           + scale("very poorly", "very well"),
        1: "How good do you expect this product to be in daily use, compared with what its specifications suggest?"
           + scale("much worse", "much better"),
    },
    "support": {
        0: "How good do you expect the customer support and warranty service for this product to be?"
           + scale("very poor", "excellent"),
        1: "If this product had a problem, how well do you expect the company behind it to help the buyer?"
           + scale("very poorly", "very well"),
    },
    "safety": {
        0: "How safe do you expect this product to be to use?" + scale("not at all safe", "completely safe"),
        1: "How confident are you that this product is free of defects that could harm the user?"
           + scale("not at all confident", "completely confident"),
    },
    "failure": {
        0: "What percentage of units of this product do you expect to fail or be returned as defective within the first "
           "year?" + PCT,
        1: "Out of 100 buyers of this product, how many do you expect to have it break or return it as faulty in the first "
           "year?" + PCT,
    },
}
CREDIBILITY = {
    0: "How believable is this listing, that is, how likely is it that the product really has these specifications at "
       "this price?" + scale("not at all believable", "completely believable"),
    1: "How likely is it that a buyer would find this product as good as the listing says?"
       + scale("very unlikely", "very likely"),
}
TRIALS = {"salience": 10, "default": 10, "typicality": 2, "recognition": 2, "description": 2, "rating": 2,
          "country": 2, "quality": 2, "credibility": 2, "consideration": 3}
# the analysis plan's amendment 1: consumers' own requests from the bank of requests (study1b-64-models-on-34-tables/materials/requests), sent as written, with no list;
# the brands are read from the free answer. Only the requests that real people wrote (chat logs and crowd-written).
REQUESTS = os.path.join(PKG, "study1b-64-models-on-34-tables", "materials", "requests", "requests.jsonl.gz")
REAL_KINDS = ("chat-log", "crowd-written for a dataset")


def real_requests():
    import gzip
    return [r for r in (json.loads(l) for l in gzip.open(REQUESTS, "rt", encoding="utf8")) if r["kind"] in REAL_KINDS]


def listing(table, product, shown_brand, price):
    """Study 2's block for one product, as the only product of the listing (letter A)."""
    if shown_brand is None:
        name, brand = "Product A", "Brand A"
    else:
        name, brand = f"{shown_brand} {S.NOUN[table['category']]}", shown_brand
    return "Here is a product listing.\n\n" + S.product_block("A", name, brand, price, product["specs"], 0)


def study2_price(table, product):
    return S.ladder(table)[0] if product["best"] else product["price"]


def pairs_of(tables):
    """Every pair of a brand and a category: {(brand, category): {"kinds": set, "tables": set}}, the tables' brands
    first, then the reference brands (the real brands that the invented names replaced)."""
    out = {}
    for t in tables.values():
        for p in t["products"]:
            d = out.setdefault((p["brand"], t["category"]), {"kinds": set(), "tables": set()})
            d["kinds"].add(p["kind"])
            d["tables"].add(t["id"])
    ref = {}
    for t in tables.values():
        for p in t["products"]:
            if p["original_brand"]:
                d = ref.setdefault((p["original_brand"], t["category"]), {"kinds": {"reference"}, "tables": set()})
                d["tables"].add(t["id"])
    return out, ref


def item_id(build, *key):
    return hashlib.sha1("|".join([build] + [str(k) for k in key]).encode()).hexdigest()[:16]


def make(build, measure, attribute, wording, trial, table, category, user, **kw):
    it = {"id": item_id(build, measure, attribute, wording, table, kw.get("brand", ""), kw.get("label", ""),
                        kw.get("product", ""), kw.get("price_kind", ""), trial),
          "build": build, "measure": measure, "attribute": attribute, "wording": wording,
          "cell": f"{measure}-{attribute or 'x'}-w{wording}", "table": table, "category": category, "trial": trial,
          "brand": kw.get("brand", ""), "brand_kind": kw.get("brand_kind", ""), "product": kw.get("product", ""),
          "product_brand": kw.get("product_brand", ""), "label": kw.get("label", ""),
          "price": kw.get("price"), "price_kind": kw.get("price_kind", ""), "names": kw.get("names", "none"),
          "info": 0, "rung": 2 if kw.get("price_kind") == "low" else 0, "best": "",
          "system": SYSTEM, "user": user}
    return it


def build_items(build, tables, keep_tables=None, keep_brands=None, with_requests=True):
    """Every item of the audit (the analysis plan and its amendment 1), filtered to the named tables and brands for a first small run."""
    if keep_tables:
        tables = {k: v for k, v in tables.items() if k in keep_tables}
    cats = sorted({t["category"] for t in tables.values()})
    pairs, ref = pairs_of(tables)
    if keep_brands:
        pairs = {k: v for k, v in pairs.items() if k[0] in keep_brands}
        ref = {k: v for k, v in ref.items() if k[0] in keep_brands}
    items = []
    # 1 and 2: per category (and the table's own request for salience w2)
    for c in cats:
        for w in (0, 1):
            for k in range(TRIALS["salience"]):
                items.append(make(build, "salience", "", w, k, f"cat_{c}", c, SALIENCE[w].format(plural=PLURAL[c])))
        for w in (0, 1, 2):
            for k in range(TRIALS["default"]):
                items.append(make(build, "default", "", w, k, f"cat_{c}", c, DEFAULT[w].format(plural=PLURAL[c])))
    for t in tables.values():
        for k in range(TRIALS["salience"]):
            items.append(make(build, "salience", "", 2, k, t["id"], t["category"], SALIENCE[2].format(req=t["req"])))
    if with_requests:
        for r in real_requests():
            if r["category"] not in cats:
                continue
            for k in range(TRIALS["consideration"]):
                it = make(build, "consideration", "", 0, k, f"cat_{r['category']}", r["category"], r["text"],
                          label=r["id"])
                it["request_id"], it["request_kind"], it["request_source"] = r["id"], r["kind"], r["source"]
                items.append(it)
    # 2, 3 and 6: per brand and category
    for (brand, c), d in list(pairs.items()) + list(ref.items()):
        kind = "|".join(sorted(d["kinds"]))
        fill = {"brand": brand, "plural": PLURAL[c]}
        common = dict(brand=brand, brand_kind=kind)
        tab = f"cat_{c}"
        measures = [("recognition", "", RECOGNITION), ("description", "", DESCRIPTION), ("country", "", COUNTRY)]
        measures += [("rating", a, RATINGS[a]) for a in RATINGS]
        if "reference" not in d["kinds"]:
            measures.append(("typicality", "", TYPICALITY))
        for measure, attribute, words in measures:
            for w, text in words.items():
                for k in range(TRIALS[measure]):
                    items.append(make(build, measure, attribute, w, k, tab, c, text.format(**fill), **common))
    # 4: inferred quality, each listing under its own name, its names-hidden twin, and the crossed listings
    for t in tables.values():
        by = {p["orig"]: p for p in t["products"]}
        best = next(p for p in t["products"] if p["best"])
        partners = sorted({S.trial_plan(t, k)["partner"] for k in range(10)})
        listings = []   # (product, shown brand or None, label)
        for p in t["products"]:
            listings.append((p, p["brand"], "own"))
            listings.append((p, None, "hidden"))
        for f in partners:
            listings.append((best, by[f]["brand"], "swap"))
            listings.append((by[f], best["brand"], "swap"))
        seen, unique = set(), []
        for x in listings:   # the toothbrush table has two Oral-B products: the best one under "Oral-B" once
            key = (x[0]["orig"], x[1], x[2])
            if key not in seen:
                seen.add(key)
                unique.append(x)
        listings = unique
        if keep_brands:   # a first small run: the listings that show or hold a kept brand, and the hidden twin of each product
            named = [x for x in listings if x[2] != "hidden" and (x[0]["brand"] in keep_brands or x[1] in keep_brands)]
            listed = {x[0]["orig"] for x in named}
            listings = [x for x in listings if x in named or (x[2] == "hidden" and x[0]["orig"] in listed)]
        for p, shown, label in listings:
            price = study2_price(t, p)
            body = listing(t, p, shown, price)
            for a, words in QUALITY.items():
                for w, q in words.items():
                    for k in range(TRIALS["quality"]):
                        items.append(make(build, "quality", a, w, k, t["id"], t["category"],
                                          body + "\n" + q.format(plural=PLURAL[t["category"]]),
                                          brand=shown or "", brand_kind="hidden" if shown is None else by_kind(t, shown),
                                          product=p["orig"], product_brand=p["brand"], label=label, price=price,
                                          price_kind="study2", names="hidden" if shown is None else "shown"))
    # 5: credibility, the best product's listing under every name of the table and the names-hidden labels
    for t in tables.values():
        best = next(p for p in t["products"] if p["best"])
        others = [p["price"] for p in t["products"] if not p["best"]]
        prices = {"low": S.ladder(t)[2], "usual": round(statistics.median(others), 2)}
        names = []
        for p in t["products"]:
            if p["brand"] not in names:
                names.append(p["brand"])
        if keep_brands:
            names = [n for n in names if n in keep_brands]
            if not names:
                continue
        for shown in names + [None]:
            for pk, price in prices.items():
                body = listing(t, best, shown, price)
                for w, q in CREDIBILITY.items():
                    for k in range(TRIALS["credibility"]):
                        items.append(make(build, "credibility", "", w, k, t["id"], t["category"], body + "\n" + q,
                                          brand=shown or "", brand_kind="hidden" if shown is None else by_kind(t, shown),
                                          product=best["orig"], product_brand=best["brand"],
                                          label="hidden" if shown is None else "name", price=price, price_kind=pk,
                                          names="hidden" if shown is None else "shown"))
    random.Random(SEED).shuffle(items)
    ids = Counter(i["id"] for i in items)
    dup = [k for k, v in ids.items() if v > 1]
    if dup:
        raise SystemExit(f"{len(dup)} item ids repeat, for example {dup[0]}")
    return items


def by_kind(table, brand):
    kinds = {p["kind"] for p in table["products"] if p["brand"] == brand}
    return "|".join(sorted(kinds))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--tables", default="all")
    ap.add_argument("--brands", default="")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--part-size", type=int, default=1500)
    ap.add_argument("--no-requests", action="store_true", help="leave out the real requests (the first small run predates them)")
    a = ap.parse_args()
    tables = S.load_tables()
    keep_t = None if a.tables == "all" else set(a.tables.split(","))
    if keep_t and keep_t - set(tables):
        sys.exit(f"no such tables: {sorted(keep_t - set(tables))}")
    keep_b = set(a.brands.split(",")) if a.brands else None
    items = build_items(a.build or "check", tables, keep_t, keep_b, with_requests=not a.no_requests)
    by_measure = Counter(i["measure"] for i in items)
    for m, n in sorted(by_measure.items()):
        print(f"{m:12s} {n:6d}")
    print(f"{'total':12s} {len(items):6d}")
    if a.check:
        return
    if not a.build:
        sys.exit("--build is required to write items")
    out = os.path.join(HERE, "items", a.build)
    if os.path.exists(os.path.join(out, "items.jsonl")):
        sys.exit(f"{out} already holds a build; choose a new --build name")
    os.makedirs(out, exist_ok=True)
    # the runner's parts (amendment 1): the real requests in part "pc", the rest in parts of --part-size
    rest = [i for i in items if i["measure"] != "consideration"]
    parts = {f"p{k}": rest[s:s + a.part_size] for k, s in enumerate(range(0, len(rest), a.part_size))}
    cons = [i for i in items if i["measure"] == "consideration"]
    if cons:
        parts["pc"] = cons
    files = ["items.jsonl", "COUNTS.json"]
    with open(os.path.join(out, "items.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    for name, part in parts.items():
        with open(os.path.join(out, f"{name}.jsonl"), "w", encoding="utf8", newline="\n") as f:
            for it in part:
                f.write(json.dumps({"id": it["id"], "text": it["user"]}, ensure_ascii=False) + "\n")
        with open(os.path.join(out, f"system_{name}.txt"), "w", encoding="utf8", newline="\n") as f:
            f.write(SYSTEM)
        files += [f"{name}.jsonl", f"system_{name}.txt"]
    report = {"build": a.build, "tables": sorted(keep_t) if keep_t else "all", "brands": sorted(keep_b) if keep_b else "all",
              "items": len(items), "parts": {k: len(v) for k, v in parts.items()}, "by_measure": dict(sorted(by_measure.items())),
              "by_cell": dict(sorted(Counter(i["cell"] for i in items).items())), "seed": SEED}
    with open(os.path.join(out, "COUNTS.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, "SHA256SUMS"), "w", encoding="utf8", newline="\n") as f:
        for fn in files:
            f.write(f"{hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest()}  {fn}\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
