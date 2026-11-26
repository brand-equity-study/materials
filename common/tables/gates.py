"""The three refusing gates of the controlled test's prompts, plus the twin
check that keeps the cells of one table and trial apart only in what each cell manipulates. Each gate reads the
rendered prompt text, not the structure that made it, so a renderer fault is caught where a model would see it.

  gate a  the best product is better than or equal to every other product on every displayed attribute and on price,
          under dominance_key.py, or the table is written there as weight-dependent; the computed verdict must equal
          the written one, every displayed attribute must have a rule, and reviews and supplied information must be
          equal across products
  gate b  a names-hidden prompt shows no brand name (of any of the 34 tables, invented or real, including the real
          names behind the invented ones), no product-model token, no trademarked feature name and no advertising
          text (scrub.py)
  gate c  no prompt prints the variable that defined the corpus's best product (its quality score or utility, or the
          words for them) or names the best product
  twins   within one table and trial: the three name versions differ only in the Name and Brand lines; the two
          information versions only in the information rows and the request line; the three price rungs only in the
          best product's price line

    run_gates(items, tables) -> {"a": [...], "b": [...], "c": [...], "twins": [...]}   (empty lists mean pass)
"""
import re
from collections import defaultdict

from dominance_key import DOM, KEY, WD
from scrub import AD_PHRASES, TRADEMARKS

STOP = {
    "pro", "plus", "max", "mini", "air", "series", "gen", "ultra", "light", "lite", "go", "se", "original", "classic",
    "smart", "electric", "commercial", "wide", "mouth", "shield", "extreme", "one", "touch", "flex", "mag", "chute",
    "race", "fit", "fe", "5g", "uhd", "led", "qled", "oled", "mini-led", "4k", "neo", "the", "artist", "trail", "speed",
    "rgb", "watch", "pad", "phone", "buds", "next", "precision", "brewer", "press", "french", "power", "elite", "glass",
    "professional", "space", "tune", "endurance", "open", "openrun", "sport", "edge", "fusion", "spin", "slim", "laptop",
    "core", "crystal", "half", "zip", "civic", "plus+", "digital", "explorian", "rambler", "wonderboom", "momentum",
    "solo", "venu", "sense", "fire", "nest", "wifi", "monitor", "tab", "cascadia", "speedgoat", "speedcross", "bambino",
    "stilosa", "vertuo", "pixie", "lattego", "k-elite", "k-mini", "12-cup", "portable", "soundlink", "stormbox",
    "superbreak", "borealis", "daylite", "chromebook",
    # words of product names that the spec rows also use as plain specification terms: a storage type, an obstacle
    # sensor, a WiFi band, a router speed class (ASUS and TP-Link both sell AXE7800 routers), Cherry's switch family
    "ssd", "ai", "6e", "axe7800", "mx",
}


# ---------------------------------------------------------------- reading a rendered prompt back

def parse_blocks(user):
    """{display letter: {"name", "brand", "price", "specs": {key: value}, "other": [lines]}} from a user message."""
    out, cur, in_specs = {}, None, False
    for line in user.split("\n"):
        m = re.match(r"^--- Product ([A-E]) ---$", line)
        if m:
            cur = out.setdefault(m.group(1), {"specs": {}, "other": []})
            in_specs = False
            continue
        if cur is None or not line.strip():
            continue
        if line.startswith("  ") and in_specs:
            k, _, v = line.strip().partition(": ")
            cur["specs"][k.replace(" ", "_")] = v
            continue
        in_specs = False
        if line.startswith("Name: "):
            cur["name"] = line[6:]
        elif line.startswith("Brand: "):
            cur["brand"] = line[7:]
        elif line.startswith("Price: $"):
            cur["price"] = float(line[8:])
        elif line == "Specs:":
            in_specs = True
        elif line.startswith("Which product"):
            cur = None
        else:
            cur["other"].append(line)
    return out


# ---------------------------------------------------------------- gate a

_UNIT = {"tb": ("gb", 1000.0), "gb": ("gb", 1.0), "kg": ("g", 1000.0), "g": ("g", 1.0), "oz": ("g", 28.35),
         "lbs": ("g", 453.6), "lb": ("g", 453.6), "days": ("h", 24.0), "day": ("h", 24.0), "months": ("h", 730.0),
         "month": ("h", 730.0), "hours": ("h", 1.0),
         "hour": ("h", 1.0), "h": ("h", 1.0), "hr": ("h", 1.0)}


def parse_number(v):
    """(number, unit) in canonical units, or None when the value states no number."""
    m = re.search(r"(-?\d[\d,]*(?:\.\d+)?)\s*\+?\s*([A-Za-z/\"]+)?", v)
    if not m:
        return None
    x = abs(float(m.group(1).replace(",", "")))
    unit = (m.group(2) or "").lower()
    if unit in _UNIT:
        u, f = _UNIT[unit]
        return x * f, u
    return x, unit


def ip_code(v):
    m = re.search(r"IP([0-9X])([0-9])", v)
    if not m:
        return None
    return (0 if m.group(1) == "X" else int(m.group(1)), int(m.group(2)))


def at_least(rule, b, o):
    """True when the best product's value b is at least as good as the other value o under the rule; a reason
    string when it is not or cannot be told."""
    kind = rule[0]
    if kind == "pref":
        return True if b == o else f"no order and the values differ ({b!r} against {o!r})"
    if kind == "rank":
        ranks = rule[1]
        for v in (b, o):
            if v not in ranks:
                return f"KEY: the value {v!r} has no rank"
        return True if ranks[b] >= ranks[o] else f"{b!r} ranks below {o!r}"
    if kind == "set":
        sb, so = {x.strip() for x in b.split("/")}, {x.strip() for x in o.split("/")}
        return True if so <= sb else f"{o!r} holds {sorted(so - sb)} that {b!r} lacks"
    if kind == "ip":
        cb, co = ip_code(b), ip_code(o)
        if cb is None or co is None:
            return f"not an IP code ({b!r}, {o!r})"
        return True if cb[0] >= co[0] and cb[1] >= co[1] else f"{b!r} is not at least {o!r} on dust and water"
    if kind in ("hi", "lo"):
        nb, no = parse_number(b), parse_number(o)
        if no is None:
            return True          # the other product states no figure
        if nb is None:
            return f"the best product states no figure ({b!r}) where {o!r} does"
        count_only = len(rule) > 1 and rule[1] == "count"
        if not count_only and nb[1] != no[1]:
            return f"different units ({b!r} against {o!r})"
        ok = nb[0] >= no[0] if kind == "hi" else nb[0] <= no[0]
        return True if ok else f"{b!r} is {'below' if kind == 'hi' else 'above'} {o!r}"
    return f"KEY: unknown rule {rule!r}"


def strictly_better(rule, b, o):
    """True when the best product's value b is better than the other value o (not only equal) under the rule."""
    kind = rule[0]
    if kind == "rank":
        return rule[1].get(b, -1) > rule[1].get(o, 99)
    if kind == "set":
        sb, so = {x.strip() for x in b.split("/")}, {x.strip() for x in o.split("/")}
        return so < sb
    if kind == "ip":
        cb, co = ip_code(b), ip_code(o)
        return bool(cb and co and cb != co and cb[0] >= co[0] and cb[1] >= co[1])
    if kind in ("hi", "lo"):
        nb, no = parse_number(b), parse_number(o)
        if nb is not None and no is None:
            return True
        if nb is None or no is None or (not (len(rule) > 1 and rule[1] == "count") and nb[1] != no[1]):
            return False
        return nb[0] > no[0] if kind == "hi" else nb[0] < no[0]
    return False


def strict_gaps(table_id, blocks, best):
    """The other products on which the best product is better on no attribute and not cheaper: with such a product the
    best product is only tied, and picking the other is not worse."""
    attrs = KEY[table_id]["attrs"]
    bp = blocks[best]
    out = []
    for L, p in blocks.items():
        if L == best or bp["price"] < p["price"]:
            continue
        if any(a not in p["specs"] for a in bp["specs"]):   # a feature stated only for the best product
            continue
        if any(a in attrs and strictly_better(attrs[a], bp["specs"][a], p["specs"][a]) for a in bp["specs"]):
            continue
        out.append(L)
    return out


def dominance(table_id, blocks, best):
    """(verdict, reasons, key_faults) for one rendered table."""
    key = KEY.get(table_id)
    if key is None:
        return None, [], [f"{table_id}: not in dominance_key.py"]
    attrs = key["attrs"]
    reasons, faults = [], []
    bp = blocks[best]
    for L, p in blocks.items():
        if L == best:
            continue
        for a in set(bp["specs"]) | set(p["specs"]):
            if a not in attrs:
                faults.append(f"{table_id}: the attribute {a!r} is shown and has no rule")
                continue
            if a not in p["specs"]:
                continue
            if a not in bp["specs"]:
                reasons.append(f"{a}: shown for {L} and not for the best product")
                continue
            r = at_least(attrs[a], bp["specs"][a], p["specs"][a])
            if r is not True:
                (faults if r.startswith("KEY") else reasons).append(f"{a} against {L}: {r}")
    return (DOM if not reasons else WD), reasons, faults


def gate_a(items):
    fails = []
    for it in items:
        blocks = parse_blocks(it["user"])
        best = it["best"]
        if set(blocks) != set("ABCDE"):
            fails.append(f"{it['id']}: the prompt does not show five products")
            continue
        others = [p for L, p in blocks.items() if L != best]
        if any(blocks[best]["price"] > p["price"] for p in others):
            fails.append(f"{it['id']}: the best product is dearer than another product")
        if len({tuple(p["other"]) for p in blocks.values()}) != 1:
            fails.append(f"{it['id']}: reviews or supplied information differ across products")
        verdict, reasons, faults = dominance(it["table"], blocks, best)
        fails += [f"{it['id']}: {f}" for f in faults]
        written = KEY.get(it["table"], {}).get("verdict")
        if verdict is not None and verdict != written:
            fails.append(f"{it['id']} {it['table']}: computed {verdict}, written {written}; {'; '.join(reasons) or 'no attribute breaks dominance'}")
        if it["table"].endswith("_dom") and verdict == DOM:
            ties = strict_gaps(it["table"], blocks, best)
            if ties:
                fails.append(f"{it['id']} {it['table']} rung {it['rung']}: the best product is only tied with {ties}")
    return fails


def verdicts(items):
    """{table: (verdict, reasons)} for the report."""
    out = {}
    for it in items:
        if it["table"] not in out:
            out[it["table"]] = dominance(it["table"], parse_blocks(it["user"]), it["best"])[:2]
    return out


# ---------------------------------------------------------------- gate b

def deny_list(tables):
    """Case-sensitive whole-word tokens no names-hidden prompt may hold: every brand of the 34 tables (shown, invented
    and the real names behind the invented ones) and every product-model token."""
    words = set()
    for t in tables.values():
        for p in t["products"]:
            for b in (p["brand"], p["original_brand"]):
                if b:
                    words.add(b)
            brand_words = set(p["brand"].split()) | set(p["original_brand"].split())
            for tok in re.split(r"[\s()]+", p["original_name"]):
                tok = tok.strip(",")
                if not tok or tok in brand_words or tok.lower() in STOP:
                    continue
                # a bare number (Bose 700, Oral-B Pro 1000) is a measurement wherever a spec row or a budget prints it
                if re.fullmatch(r"\d+(st|nd|rd|th)?", tok) or re.fullmatch(r"\d{1,2}(oz|L)", tok):
                    continue
                words.add(tok)
    return sorted(words | set(TRADEMARKS))


def gate_b(items, tables):
    fails = []
    deny = deny_list(tables)
    deny_re = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(w) for w in sorted(deny, key=len, reverse=True)) + r")(?![A-Za-z0-9])")
    ad_re = re.compile("|".join(re.escape(a) for a in AD_PHRASES), re.I)
    for it in items:
        if it["names"] != "hidden":
            continue
        u = it["user"]
        for m in deny_re.finditer(u):
            fails.append(f"{it['id']} {it['table']}: names-hidden prompt shows {m.group(1)!r}")
        products = u.split("\n\n", 1)[1] if "\n\n" in u else u   # the shopper's own request line is not a listing
        for m in ad_re.finditer(products):
            fails.append(f"{it['id']} {it['table']}: names-hidden prompt shows advertising text {m.group(0)!r}")
        for L, p in parse_blocks(u).items():
            if p.get("name") != f"Product {L}" or p.get("brand") != f"Brand {L}":
                fails.append(f"{it['id']} {it['table']}: product {L} is not labelled Product {L} / Brand {L}")
    return fails


# ---------------------------------------------------------------- gate c

FORBIDDEN = re.compile(r"\b(optimal|optimum|utilit(y|ies)|quality[ _]score|is_optimal|value score|"
                       r"best (product|option|choice|pick) (is|here)|highest[- ]scoring)\b", re.I)


def gate_c(items, tables):
    fails = []
    for it in items:
        t = tables[it["table"]]
        text = it["system"] + "\n" + it["user"]
        for m in FORBIDDEN.finditer(text):
            fails.append(f"{it['id']} {it['table']}: prints {m.group(0)!r}")
        qs = {q for q in t["hidden_q"].values() if q is not None}
        maxp = max(p["price"] for p in t["products"]) * 1.1
        us = {round(0.5 * t["hidden_q"][p["orig"]] + 0.5 * (1 - p["price"] / maxp), 4) for p in t["products"]
              if t["hidden_q"].get(p["orig"]) is not None}
        for x in sorted(qs):
            for s in {f"{x:.2f}", f"{x}"}:
                if re.search(r"(?<![\d.])" + re.escape(s) + r"(?!\d)", it["user"]):
                    fails.append(f"{it['id']} {it['table']}: prints the quality score {s}")
        for x in sorted(us):
            if re.search(r"(?<![\d.])" + re.escape(f"{x:.4f}") + r"(?!\d)", it["user"]):
                fails.append(f"{it['id']} {it['table']}: prints the utility {x:.4f}")
        b = it["best"]
        if re.search(rf"\b(recommend|choose|pick|go with|buy|best is|winner is|answer is)\s+(Product\s+)?{b}\b", it["user"], re.I):
            fails.append(f"{it['id']} {it['table']}: names the best product {b}")
        request = it["user"].split("\n", 1)[0]
        for p in t["products"]:
            for w in (p["brand"], p["original_name"]):
                if re.search(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", request):
                    fails.append(f"{it['id']} {it['table']}: the request names {w!r}")
    return fails


# ---------------------------------------------------------------- twins

def gate_twins(items):
    fails = []
    groups = defaultdict(dict)
    for it in items:
        groups[("names", it["build"], it["table"], it["trial"], it["info"], it["rung"])][it["names"]] = it
        groups[("info", it["build"], it["table"], it["trial"], it["names"], it["rung"])][it["info"]] = it
        groups[("rung", it["build"], it["table"], it["trial"], it["names"], it["info"])][it["rung"]] = it

    def strip(u, drop):
        return [l for l in u.split("\n") if not drop(l)]

    for key, g in groups.items():
        kind = key[0]
        vals = list(g.values())
        if kind == "names":
            ref = strip(vals[0]["user"], lambda l: l.startswith(("Name: ", "Brand: ")))
            for v in vals[1:]:
                if strip(v["user"], lambda l: l.startswith(("Name: ", "Brand: "))) != ref:
                    fails.append(f"{v['id']}: differs from its name twins outside the Name and Brand lines")
            if len({v["system"] for v in vals}) != 1:
                fails.append(f"{vals[0]['id']}: name twins have different system prompts")
        elif kind == "info":
            info_lines = lambda l: l.startswith(("Warranty: ", "First-year failure", "Time on the market", "I'm looking for "))
            ref = strip(vals[0]["user"], info_lines)
            for v in vals[1:]:
                if strip(v["user"], info_lines) != ref:
                    fails.append(f"{v['id']}: differs from its information twin outside the information lines")
        else:
            best = vals[0]["best"]
            def no_best_price(u, best=best):
                out, cur = [], None
                for l in u.split("\n"):
                    m = re.match(r"^--- Product ([A-E]) ---$", l)
                    if m:
                        cur = m.group(1)
                    if cur == best and l.startswith("Price: "):
                        continue
                    out.append(l)
                return out
            ref = no_best_price(vals[0]["user"])
            for v in vals[1:]:
                if no_best_price(v["user"]) != ref:
                    fails.append(f"{v['id']}: differs from its price twins outside the best product's price")
            if len({v["user"] for v in vals}) != len(vals):
                fails.append(f"{vals[0]['id']}: price rungs render the same prompt")
    return fails


def run_gates(items, tables):
    return {"a": gate_a(items), "b": gate_b(items, tables), "c": gate_c(items, tables), "twins": gate_twins(items)}
