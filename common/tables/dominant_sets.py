"""The dominant sets, the strictly better tables of the controlled test (written on 20 November 2026, after a second
reader found 1 of the 34 corpus tables strictly dominant): for each corpus table, a version in which the
designated best product is better than or equal to every other product on every displayed attribute and costs no more
than any other product.

How each table is changed, in this order (every change is listed by `changes()` and in GATES.json):
1. An attribute that has no order that every buyer accepts (the second reader's rulings in study1b-64-models-on-34-tables/materials/attribute_rulings.csv
   and dominance_key.py; the list UNORDERED below) is set to one value for all five products: the value most products
   already hold, with a tie going to the earliest other product in the corpus's letter order. No single value can be at
   least as good as two different values with no order between them, so this is the only change made to the other
   products, and it never changes an ordered attribute of theirs.
2. An ordered attribute on which the best product is not at least as good as every other product gets a new value for
   the best product only (BEST below, written by hand, kept within what products of that kind and price offer).
3. Names, the scrub, the information rows and the price ladder are as in tables.py; the dominant sets use the
   rungs equal to the cheapest other product and 30 per cent below it.

Gate a refuses a build unless every dominant table computes as dominant under KEY_DOM, whose rules follow the second reader's
rulings where they are stricter than dominance_key.py.
"""
import copy
from collections import Counter

import dominance_key as DK

UNORDERED = {"capacity", "material", "speeds", "blade", "af", "type", "brew_temp", "brew_time", "pressure", "fit",
             "modes", "driver", "impedance", "switches", "connectivity", "layout", "features", "cpu", "processor",
             "size", "panel", "color", "hdr", "navigation", "emptying", "cushioning", "drop", "terrain", "traction",
             "gps", "sensors", "display", "strokes", "anc"}
# per table: attributes that are ordered there although their name is in UNORDERED (the second reader's table rulings)
ORDERED_HERE = {
    "sr_external_ssds_01": {"capacity"},
    "sr_headphones_01": {"anc"},                       # every value is a figure in decibels
    "sr_electric_toothbrushes_01": {"display"},        # a display stated only for the best product
}
# per table: attributes removed for every product, with the reason
_CONTRADICTS = "removed: one value for all five would contradict what a named brand makes"
DROP = {
    "sr_robot_vacuums_01": {"suction": "removed: pascals for four products, air watts for one, so no order",
                            "navigation": _CONTRADICTS + " (a camera on the bounce robot)"},
    "sr_electric_toothbrushes_01": {
        "type": "removed: sonic and oscillating brushes are two kinds with no order",
        "strokes": "removed: sonic strokes and oscillating rotations are counted in different units"},
    "sr_laptops_02": {"cpu": _CONTRADICTS + " (an AMD processor in the Apple laptop)",
                      "display": _CONTRADICTS + " (an OLED screen on the Apple laptop)"},
    "sr_tvs_02": {"hdr": _CONTRADICTS + " (Dolby Vision on the Samsung television)"},
    "sr_coffee_makers_01": {"brew_temp": _CONTRADICTS + " (one brewing temperature for pod and drip makers)",
                            "brew_time": _CONTRADICTS + " (a one-minute brew on every drip maker)"},
    "sr_coffee_makers_03": {"type": _CONTRADICTS + " (a pod AeroPress and a pod French press)",
                            "brew_temp": _CONTRADICTS + " (a manual temperature on the pod makers)"},
    "sr_earbuds_01": {"codec": "removed: one product lists its maker's own codec, which no other product can hold "
                               "(the second reading, finding 1)"},
    "sr_earbuds_02": {"anc": _CONTRADICTS + " (noise cancelling on the AirPods that have none)"},
    "sr_earbuds_03": {"fit": _CONTRADICTS + " (wingtips on the bone-conduction Shokz)"},
    "sr_monitors_01": {"hdr": "removed: HDR1000, stated only for the best monitor, needs the Mini-LED panel that the "
                              "held-equal panel row no longer shows (the second reading, finding 4)"},
}
# per table and corpus letter: one other product's value removed because it cannot be compared with the others
RIVAL_REMOVE = {
    "sr_electric_toothbrushes_01": {"D": {"battery": "removed: a disposable AAA battery has no charge life to compare "
                                                     "(the second reading, finding 5)"}},
}
# tables left out of the dominant sets, with the reason
EXCLUDE = {
    "sr_portable_speakers_01": "to be lighter than the 274 g Sony speaker while matching the 30 W JBL speaker and the "
                               "16-hour Sony battery, the best speaker would need figures no speaker of that kind has",
    "sr_keyboards_01": "every displayed attribute (switches, connection, layout, features) has no order, so held equal "
                       "the five keyboards would differ only in price, and at the equal-price rung the cheapest other "
                       "keyboard would be as good as the best one",
    "sr_coffee_makers_02": "to match the super-automatic machine's grinder and automatic frother the best espresso "
                           "machine would need both at 120 dollars or less, which no machine of that kind offers "
                           "(the second reading, finding 3)",
    "sr_water_bottles_01": "to be lighter than the 12.3-ounce S'well (a 25-ounce bottle) the best 32-ounce insulated "
                           "steel bottle would need a weight no bottle of that size has (the review of every "
                           "improved figure)",
}

# the best product's new values on ordered attributes, by table (only the best product changes)
BEST = {
    "sr_smartphones_01": {"camera": "50MP triple OIS"},
    "sr_smartphones_03": {"camera": "200MP triple OIS"},
    "sr_tvs_03": {"refresh": "120Hz"},                 # held equal, its panel and HDR list left it only tied
    "sr_headphones_01": {"codec": "LDAC/aptX Adaptive/aptX/AAC/SBC"},
    "sr_headphones_02": {"weight": "190g", "codec": "LDAC/AAC/SBC"},
    # a connection line stated only for the best pair shows that it also works with a cable (the second reading, finding 2)
    "sr_headphones_03": {"battery": "60 hours", "codec": "LDAC/aptX/AAC/SBC", "connection": "wireless and wired"},
    "sr_coffee_makers_03": {"weight": "11 oz"},
    "sr_earbuds_02": {"codec": "aptX Adaptive/LDAC/AAC/SBC"},
    "sr_earbuds_03": {"ip_rating": "IP68"},
    "sr_external_ssds_01": {"durability": "IP68, 3m drop"},
    "sr_backpacks_01": {"weight": "0.35kg"},
}
# rank orders for ordered attributes whose values are words, by table (higher is better), where dominance_key.py has
# none or the new values need one; each order holds the best product's value at the top only when it is at least as
# good as each other value on every part that can be compared
RANK = {
    # megapixels, then lenses, then optical stabilisation, each at least as high
    "sr_smartphones_01": {"camera": {"50MP triple OIS": 3, "50MP triple": 2, "50MP Octa PD": 1, "50MP": 1, "48MP": 1}},
    "sr_smartphones_03": {"camera": {"200MP triple OIS": 3, "50MP triple": 2, "12MP dual": 1, "64MP": 1, "50MP": 1}},
    # every codec the wireless pairs list; the wired pair needs none (its cable is matched by the connection line)
    "sr_headphones_03": {"codec": {"LDAC/aptX/AAC/SBC": 2, "LDAC/aptX": 1, "LDAC/AAC": 1, "AAC/SBC": 1,
                                   "N/A (wired)": 0}},
    # the IP code digit by digit, then the stated drop height
    "sr_external_ssds_01": {"durability": {"IP68, 3m drop": 3, "IP65, 3m drop": 2, "drop resistant 6.5 ft": 1,
                                           "IP55, 2m drop": 1, "basic": 0}},
}

# rules for the dominant tables' ordered attributes (unordered ones are ("pref",) and equal by construction)
RULE = {
    "ram": ("hi",), "storage": ("hi",), "weight": ("lo",), "power": ("hi",), "laptop": ("hi",), "battery": ("hi",),
    "charging": ("hi",), "refresh": ("hi",), "brightness": ("hi",), "dimming_zones": ("hi",), "runtime": ("hi",),
    "coverage": ("hi",), "devices": ("hi",), "speed": ("hi",), "sensor": ("hi",), "codec": ("set",),
    "ip_rating": ("ip",), "waterproof": ("ip",), "capacity": ("hi",), "durability": ("hi",), "anc": ("hi",),
    "insulation": ("hi",), "suction": ("hi",),
}


def unordered(table_id, attr):
    return attr in UNORDERED and attr not in ORDERED_HERE.get(table_id, set())


def rule_for(table_id, attr):
    if unordered(table_id, attr):
        return ("pref",)
    if attr in RANK.get(table_id, {}):
        return ("rank", RANK[table_id][attr])
    own = DK.KEY.get(table_id, {}).get("attrs", {}).get(attr)
    if own and own[0] in ("rank", "set", "ip"):
        return own
    return RULE.get(attr, own or ("pref",))


def common_value(table, attr):
    vals = [p["specs"].get(attr) for p in table["products"]]
    counts = Counter(v for v in vals if v is not None)
    top = max(counts.values())
    for p in table["products"]:            # corpus letter order; the best product does not win a tie
        if not p["best"] and counts.get(p["specs"].get(attr)) == top:
            return p["specs"][attr]
    return next(v for v, n in counts.items() if n == top)


def dominant(table):
    """A dominant version of one scrubbed table (tables.load_tables format), with id <id>_dom."""
    t = copy.deepcopy(table)
    tid = table["id"]
    t["id"] = tid + "_dom"
    t["changes"] = []
    attrs = list(dict.fromkeys(a for p in t["products"] for a in p["specs"]))
    for a, why in DROP.get(tid, {}).items():
        for p in t["products"]:
            if a in p["specs"]:
                t["changes"].append((p["orig"], a, p["specs"].pop(a), None, why))
    for letter, vals in RIVAL_REMOVE.get(tid, {}).items():
        p = next(q for q in t["products"] if q["orig"] == letter)
        for a, why in vals.items():
            t["changes"].append((letter, a, p["specs"].pop(a), None, why))
    attrs = [a for a in attrs if a not in DROP.get(tid, {})]
    for a in attrs:
        holders = [p for p in t["products"] if a in p["specs"]]
        if len(holders) == 1 and holders[0]["best"]:
            continue                                    # stated only for the best product: it counts in its favour
        if unordered(tid, a):
            v = common_value(t, a)
            for p in t["products"]:
                if p["specs"].get(a) != v:
                    t["changes"].append((p["orig"], a, p["specs"].get(a), v, "held equal: no order"))
                    p["specs"][a] = v
    best = next(p for p in t["products"] if p["best"])
    for a, v in BEST.get(tid, {}).items():
        t["changes"].append((best["orig"], a, best["specs"].get(a), v, "best product raised"))
        best["specs"][a] = v
        if a not in attrs:                              # a line stated only for the best product
            attrs.append(a)
    # keep the attribute order of the corpus for every product
    for p in t["products"]:
        p["specs"] = {a: p["specs"][a] for a in attrs if a in p["specs"]}
    return t


def key_for(table_id, attrs):
    return {"verdict": DK.DOM, "attrs": {a: rule_for(table_id, a) for a in attrs}}


def build(tables):
    """{<id>_dom: table} for every corpus table, and the KEY entries for gate a."""
    out, key = {}, {}
    for tid, t in tables.items():
        if tid in EXCLUDE:
            continue
        d = dominant(t)
        out[d["id"]] = d
        attrs = {a for p in d["products"] for a in p["specs"]}
        key[d["id"]] = key_for(tid, attrs)
    return out, key
