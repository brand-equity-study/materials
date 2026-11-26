"""What the assistants saw: one panel for each setting in which the models chose, drawn from the exact messages sent to
them, and the table of the settings beside how deployed shopping assistants work.

    For the Web Appendix:
wa_fig_settings.pdf and .png, the full transcripts, and wa_table_settings.md, the long table.

Every line of a message in the figures is read from the item that was sent (study2, requests, harness, retrieval and
clarifying items, all in git), by item id. The only words typed here are the
panel titles, the role tags and the notes in square brackets that say what was left out. The panels share one table
(laptops, trial 0, names shown) so that the same five products appear in every setting.
"""
import argparse
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
HERE = PKG / "exhibits" / "results" / "figures"   # where the figures are written
HERE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CODE))
import diagrams as G  # noqa: E402  (read only)

if not G.FONT_DIR.exists():
    for cand in (Path.home() / "AppData/Local/Programs/MiKTeX/fonts/opentype/public/fira",
                 Path("C:/Program Files/MiKTeX/fonts/opentype/public/fira")):
        if (cand / "FiraSans-Regular.otf").exists():
            G.FONT_DIR = cand
            break

TABLE = "sr_laptops_01_dom"
ITEMS = {
    "plain": ("study1a-tables-with-one-optimal-product/materials/strictly-better-tables/prompts.jsonl.gz", "59fdf284d36cbff1"),
    "request": ("study1b-64-models-on-34-tables/materials/requests/prompts.jsonl.gz", "a47d5f01c76fac58"),
    "feed": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "a61db7c34b370890"),
    "markup": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "936ea07431639dac"),
    "sponsored": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "bcd3305d9fc8ad74"),
    "rating": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "a2bd4d724499120e"),
    "pos_first": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "559d749cadd4e744"),
    "pos_middle": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "24e9d19fd8d27a2e"),
    "pos_last": ("study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "2e6eaf31f25cfb10"),
    "search1": ("study1c-product-feeds-and-a-store-search/materials/search/s1/stage1/prompts.jsonl.gz", "22bd0e183bf899ed"),
    "search2": ("study1c-product-feeds-and-a-store-search/materials/search/s1/stage2/claude-sonnet-5-5.jsonl.gz", "68481c0c3f67fe22"),
    "review_pos": ("study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz", "3bfb7be224ff6211"),
    "review_mixed": ("study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz", "b0d283b194437e8f"),
    "review_neg": ("study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz", "7e229854ce72956c"),
    "clarify": ("study1b-64-models-on-34-tables/materials/clarifying/prompts.jsonl.gz", "4e9476d735427fb4"),
}
OTHER_REQUESTS = ("q003989",)                    # another request that a person typed, answered with the same table
CLARIFY_ANSWERS = "the clarifying turn's answers of Qwen 2.5 7B"   # quoted in settings_sources.json
CLARIFY_MODEL = "qwen7b"
SOURCES = PKG / "exhibits" / "materials" / "settings_sources.json"   # the model outputs that the figures quote
COVERAGE = PKG / "models" / "answered-by-setting.json"   # which models answered
CHARS = PKG / "models" / "model_characteristics.csv"

HI_FILL = "#DDE8EE"          # the varied lines: a pale fill of the accent, a bar in the accent and semibold type
LH = 7.4                     # line height for the 6.5-point text


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def item(key):
    rel, iid = ITEMS[key]
    for line in gzip.open(PKG / rel, "rt", encoding="utf8"):
        r = json.loads(line)
        if r["id"] == iid:
            return r
    raise SystemExit(f"refused: item {iid} not in {rel}")


def block(user, letter):
    """The lines of one product's block in a message, from its '--- Product X ---' line to the line before the next."""
    lines = user.splitlines()
    start = lines.index(f"--- Product {letter} ---")
    out = []
    for ln in lines[start:]:
        if out and (ln.startswith("--- Product") or ln.startswith("Which product")):
            break
        out.append(ln)
    while out and not out[-1].strip():
        out.pop()
    return out


def json_block(user, letter):
    """The lines of one product's JSON object in a message, from its 'Product X:' line to its closing brace."""
    lines = user.splitlines()
    start = lines.index(f"Product {letter}:")
    out = []
    for ln in lines[start + 1:]:
        out.append(ln)
        if ln == "}":
            break
    return out


# ---------------------------------------------------------------- the quoted model outputs

def extract():
    """The model outputs that the figures quote were copied from the answer files into settings_sources.json when the
    paper was made; the package holds that file beside this code, and the figures read it."""
    raise SystemExit("--extract ran on the project's answer files; the package holds its result, settings_sources.json")


# ---------------------------------------------------------------- measuring and wrapping text

_FONTS = {}


def _font(weight):
    if weight not in _FONTS:
        from fontTools.ttLib import TTFont
        f = TTFont(G.truetype("FiraSans-SemiBold" if weight >= 600 else "FiraSans-Regular"))
        tnum = {}
        for fr in f["GSUB"].table.FeatureList.FeatureRecord:
            if fr.FeatureTag == "tnum":
                for li in fr.Feature.LookupListIndex:
                    for st in f["GSUB"].table.LookupList.Lookup[li].SubTable:
                        tnum.update(getattr(st, "mapping", {}) or {})
        _FONTS[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm, tnum)
    return _FONTS[weight]


def width(s, size=G.S, weight=400):
    cmap, hmtx, upm, tnum = _font(weight)
    total = 0
    for ch in s:
        g = cmap.get(ord(ch)) or cmap.get(ord("?"))
        total += hmtx[tnum.get(g, g)][0]
    return total * size / upm


def wrap(s, w, size=G.S, weight=400, indent=0.0):
    """Greedy wrap of one message line into lines no wider than w points; continuation lines keep the indent."""
    words, out, cur = s.split(" "), [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if width(trial, size, weight) <= w - indent or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = wd
    out.append(cur)
    return out


# ---------------------------------------------------------------- drawing

class Canvas:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=G.S, weight=400, anchor="start", xmax=None):
        fit = anchor == "start" and xmax is not None
        self.add(G.text(x, y, s, size, weight, anchor, G.INK, xmin=x - 1.5 if fit else None, xmax=xmax if fit else None))

    def rect(self, x, y, w, h, fill="#FFFFFF", stroke=None, r=0, cls=""):
        st = f' stroke="{stroke}" stroke-width="0.6"' if stroke else ""
        c = f' class="{cls}"' if cls else ""
        self.add(f'<rect{c} x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{r}" fill="{fill}"{st}/>')

    def arrow(self, x1, y1, x2, y2):
        self.add(f'<path class="edge" d="M{x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f}" stroke="{G.INK}" stroke-width="0.7" '
                 f'fill="none" marker-end="url(#head)"/>')


def tag(cv, x, y, label):
    """A role tag (System, User, Model) at the top of a message, as a small pale pill."""
    w = width(label, G.S, 600) + 6
    cv.rect(x, y - 6.0, w, 8.4, G.PALE, r=2)
    cv.text(x + 3, y, label, G.S, 600, xmax=x + w)
    return w


def message(cv, x, y, w, role, lines, tagw=30):
    """One message: its role tag at left and its lines at right. A line is (text, kind) with kind 'plain', 'hi' (varied:
    filled, barred, semibold), 'note' (a bracketed note of what is left out) or 'gap' (half a line of space). Each text
    line is wrapped to the column. Returns the y below the message."""
    if role:
        tag(cv, x, y, role)
    tx, tw = x + tagw, w - tagw
    for s, kind in lines:
        if kind == "gap":
            y += LH * 0.5
            continue
        lead = len(s) - len(s.lstrip(" "))
        ind = min(lead, 8) * 1.6
        weight = 600 if kind == "hi" else 400
        rows = wrap(s.strip(" "), tw - 3, G.S, weight, ind)
        if kind == "hi":
            cv.rect(tx - 2.5, y - 5.6, tw + 1.5, LH * len(rows) + 0.2, HI_FILL)
            cv.rect(tx - 2.5, y - 5.6, 1.1, LH * len(rows) + 0.2, G.ACCENT)
        for k, row in enumerate(rows):
            cv.text(tx + ind + (0 if k == 0 else 4), y, row, G.S, weight, xmax=tx + tw)
            y += LH
    return y + 2.5


def panel_head(cv, x, y, letter, title, varied, w):
    cv.text(x, y, letter, G.L, 600)
    cv.text(x + 9, y, title, G.M, 600, xmax=x + w)
    rows = wrap(varied, w - 9, G.S)
    for k, row in enumerate(rows):
        cv.text(x + 9, y + 9 + k * LH, row, G.S, xmax=x + w)
    return y + 9 + len(rows) * LH + 2


def window(cv, x, y, w, h):
    cv.rect(x, y, w, h, "#FFFFFF", G.LINE, r=3)


# ---------------------------------------------------------------- the six panels

def sys_first(r):
    return r["system"].split("\n")[0]


def panel_plain(cv, x, y, w):
    r = item("plain")
    u = r["user"].splitlines()
    best = r["best"]
    other = r["order"][1]
    hid = item_hidden_names(r)
    y0 = panel_head(cv, x, y, "a", "A table of products (Study 1a)",
                    "Varied: with or without brand names, or two brand names swapped", w)
    lines = [(sys_first(r), "plain"), ("[two more paragraphs: how to answer]", "note")]
    eb, ob = block(r["user"], best), block(r["user"], other)
    body = [(u[0], "plain"), ("gap", "gap"), (u[2], "plain"), ("gap", "gap")]
    for ln in eb:
        body.append((ln, "hi" if ln.startswith(("Name:", "Brand:")) else "plain"))
    body.append(("gap", "gap"))
    body += [(ob[0], "plain"), (ob[1], "hi"), (ob[2], "hi"),
             (f"[price, attributes and reviews; then products {', '.join(r['order'][2:-1])} and {r['order'][-1]}]", "note"),
             ("gap", "gap"), (u[-1], "plain")]
    n, b = hid
    return draw_messages(cv, x, y0, w, [("System", lines), ("User", body)],
                         foot=[f"Without brand names, the same product was listed as “Name: {n}” and "
                               f"“Brand: {b}”."])


def item_hidden_names(r):
    """The hidden version of the same item (same table, trial and order): what the optimal product was called there."""
    rel = ITEMS["plain"][0]
    for line in gzip.open(PKG / rel, "rt", encoding="utf8"):
        h = json.loads(line)
        if (h["table"], h["trial"], h["names"], h["info"], h["rung"]) == (r["table"], r["trial"], "hidden", 0, 0):
            b = block(h["user"], h["best"])
            return b[1].split(": ", 1)[1], b[2].split(": ", 1)[1]
    raise SystemExit("refused: no hidden twin")


def panel_request(cv, x, y, w):
    r = item("request")
    reqs = {q["id"]: q for q in map(json.loads, gzip.open(PKG / "study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz", "rt", encoding="utf8"))}
    q = reqs[r["request"]]
    u = r["user"].splitlines()
    a = item("plain")
    assert r["system"] == a["system"] and u[1:] == a["user"].splitlines()[1:], "panel b's note 'as in a' is not true"
    y0 = panel_head(cv, x, y, "b", "A typed request (Study 1b)",
                    "Varied: the request; with or without brand names, or two swapped", w)
    body = [(u[0], "hi"), ("[the products, as in a]", "note"), (u[-1], "plain")]
    y1 = draw_messages(cv, x, y0, w, [("System", [("[as in a]", "note")]), ("User", body)],
                       foot=[f"The request was {pretty_source(q)}."])
    others = [reqs[k] for k in OTHER_REQUESTS]
    y1 += LH + 2                     # the next baseline
    head = "Another request" if len(others) == 1 else f"{len(others)} more requests"
    cv.text(x + 9, y1, f"{head} answered with the same five products:", G.S, 600, xmax=x + w)
    y1 += LH
    for o in others:
        for k, row in enumerate(wrap(f"\u201c{o['text'].strip()}\u201d ({pretty_source(o)})", w - 14, G.S)):
            cv.text(x + 13 if k else x + 9, y1, row, G.S, xmax=x + w)
            y1 += LH
    return y1 - LH + 3


def pretty_source(q):
    import datetime
    name = {"WildChat-4.8M": "WildChat", "LMArena human preference 140k": "LMArena"}.get(q["source"], q["source"])
    d = datetime.date.fromisoformat(q["date"])
    return f"typed in {name}, {d.day} {d.strftime('%B %Y')}"


def panel_store(cv, x, y, w):
    feed, markup, spons, rating = item("feed"), item("markup"), item("sponsored"), item("rating")
    best = feed["best"]
    y0 = panel_head(cv, x, y, "d", "The store's listing (Study 1c)",
                    "Varied: the listing as a product feed or as page markup; a Sponsored label on a familiar product "
                    "or on the optimal product; the optimal product's star rating and position; an instruction from the "
                    "developer; with or without brand names", w)
    top = y0 + 1
    cols = [w * 0.40, w * 0.31, w * 0.29]
    xs = [x, x + cols[0], x + cols[0] + cols[1]]
    heads = ["OpenAI's product feed, current fields", "schema.org markup (first lines)", "A label, a rating, a position"]
    fy = []
    # column 1: one product as a feed object
    jb = json_block(feed["user"], best)
    lines = [(f"Product {best}:", "plain")] + [(ln, "plain") for ln in jb]
    lines.append(("[products D, B, A and C in the same form]", "note"))
    fy.append(sub_column(cv, xs[0] + 4, top, cols[0] - 10, heads[0], lines))
    # column 2: the same product as schema.org markup, its first 9 lines
    mb = json_block(markup["user"], best)
    shown = mb[:9]
    lines = [(f"Product {best}:", "plain")] + [(ln, "plain") for ln in shown]
    lines.append((f"[{len(mb) - len(shown)} more lines: attributes, rating, offer, warranty, returns]", "note"))
    fy.append(sub_column(cv, xs[1] + 4, top, cols[1] - 10, heads[1], lines))
    # column 3: a Sponsored label on a familiar product, a higher rating for the optimal one, and its position
    lab = spons["labelled"]
    sb = block(spons["user"], lab)
    rb = block(rating["user"], best)
    rev = [ln for ln in rb if ln.startswith("Reviews:")][0]
    other_rev = [ln for ln in block(rating["user"], rating["order"][1]) if ln.startswith("Reviews:")][0]
    order_names = {}
    for key in ("pos_first", "pos_middle", "pos_last"):
        p = item(key)
        names = [block(p["user"], L)[1].split(": ", 1)[1].replace(" laptop", "") for L in p["order"]]
        order_names[key] = names
    lines = [(sb[0], "plain"), (sb[1], "hi"), (sb[2], "plain"), ("[the rest of the block]", "note"), ("gap", "gap"),
             (f"Product {best}: {rev}", "hi"), (f"The others: {other_rev}", "plain"), ("gap", "gap")]
    for key, label in (("pos_first", "first"), ("pos_middle", "third"), ("pos_last", "last")):
        lines.append((f"Listed {label}: " + ", ".join(order_names[key]), "plain"))
    fy.append(sub_column(cv, xs[2] + 4, top, cols[2] - 10, heads[2], lines))
    return max(fy)


def sub_column(cv, x, y, w, head, lines):
    cv.text(x, y + 6, head, G.S, 600, xmax=x + w)
    window(cv, x - 2, y + 9, w + 4, 0)          # replaced below once the height is known
    idx = len(cv.parts) - 1
    yy = message(cv, x + 2, y + 18, w - 2, None, lines, tagw=0)
    cv.parts[idx] = (f'<rect x="{x - 2:.2f}" y="{y + 9:.2f}" width="{w + 4:.2f}" height="{yy - y - 9:.2f}" rx="3" '
                     f'fill="#FFFFFF" stroke="{G.LINE}" stroke-width="0.6"/>')
    return yy


def panel_search(cv, x, y, w):
    s1, s2 = item("search1"), item("search2")
    src = json.loads(SOURCES.read_text(encoding="utf-8"))["search"]
    assert src["item"] == s2["id"] and src["queries"] == s2["queries"], "settings_sources.json is stale; run --extract"
    a = item("plain")
    assert s2["system"] == a["system"], "panel e's note 'as in a' is not true"
    y0 = panel_head(cv, x, y, "e", "The model's own searches (Study 1c)",
                    "The model wrote its searches; varied: with or without brand names", w)
    sys1 = [(ln, "plain") for ln in s1["system"].split("\n") if ln.strip()]
    u2 = s2["user"].splitlines()
    ret = s2["returned"]
    msgs = [("System", sys1), ("User", [(s1["user"].strip(), "plain")]),
            ("Model", [(json.dumps(s2["queries"]), "hi")]),
            ("rule", "The second call"),
            ("System", [("[as in a]", "note")]),
            ("User", [("[the request]", "note"), (u2[2], "hi"), (u2[3], "hi"),
                      (f"[products {', '.join(ret[:-1])} and {ret[-1]}, in the form of a]", "note"), (u2[-1], "plain")])]
    return draw_messages(cv, x, y0, w, msgs, foot=[f"The searches are Claude Sonnet 5.5's; the store returned {len(ret)} of "
                                                    f"the 5 products."])


def panel_reviews(cv, x, y, w):
    r = item("review_pos")
    u = r["user"].splitlines()
    best = r["best"]
    a = item("plain")
    assert r["system"] == a["system"] and u[:3] == a["user"].splitlines()[:3], "panel f's notes 'as in a' are not true"
    y0 = panel_head(cv, x, y, "f", "Review pages at answer time (Study 2a)",
                    "Varied: the review pages; with or without brand names, or two swapped", w)
    eb = block(r["user"], best)
    k = eb.index("Retrieved from review sites:")
    body = [("[the opening lines, as in a]", "note")] + [(ln, "plain") for ln in eb[:3]]
    body += [("[price, attributes and reviews]", "note")] + [(ln, "hi") for ln in eb[k:]]
    body += [("[products " + ", ".join(r["order"][1:-1]) + f" and {r['order'][-1]} in the same form, with the same pages]",
              "note"), (u[-1], "plain")]
    foot = []
    for key, label in (("review_mixed", "Mixed"), ("review_neg", "Negative")):
        b = block(item(key)["user"], best)
        foot.append(f"{label}: " + b[b.index("Retrieved from review sites:") + 1].strip())
    return draw_messages(cv, x, y0, w, [("System", [("[as in a]", "note")]), ("User", body)], foot=foot)


def panel_clarify(cv, x, y, w):
    r = item("clarify")
    src = json.loads(SOURCES.read_text(encoding="utf-8"))["clarify"]
    assert src["item"] == r["id"], "settings_sources.json is stale; run --extract"
    source = next(json.loads(ln) for ln in gzip.open(PKG / ITEMS["plain"][0], "rt", encoding="utf8")
                  if json.loads(ln)["id"] == r["source_id"])
    assert r["system"].split("\n\n")[:-1] == source["system"].split("\n\n")[:-1], "panel c's note on the prompt is not true"
    y0 = panel_head(cv, x, y, "c", "A clarifying question (Study 1b)",
                    "Every model could ask first; varied: with or without brand names", w)
    ask = [ln for ln in r["system"].split("\n") if ln.startswith("Before you recommend")][0]
    cut = ask.index(" If you do not need to ask")
    msgs = [("System", [("[the system prompt, with its last paragraph replaced by:]", "note"), (ask[:cut], "hi"),
                        ("[and how to answer without asking]", "note")]),
            ("User", [("[the request and the five products, in the form of a]", "note")]),
            ("Model", [(src["question"], "hi")]),
            ("User", [(r["followup"], "hi")])]
    return draw_messages(cv, x, y0, w, msgs, foot=["Then the model chose a product. The question is Qwen 2.5 7B's."])


def draw_messages(cv, x, y, w, msgs, foot=None):
    """A window holding the messages in order; a ('rule', text) entry draws a divider with a label."""
    window(cv, x, y, w, 0)
    idx = len(cv.parts) - 1
    yy = y + 10
    for role, lines in msgs:
        if role == "rule":
            cv.add(f'<line x1="{x + 4:.2f}" y1="{yy - 3:.2f}" x2="{x + w - 4:.2f}" y2="{yy - 3:.2f}" stroke="{G.LINE}" '
                   f'stroke-width="0.6" stroke-dasharray="2 1.5"/>')
            cv.text(x + 5, yy + 4.5, lines, G.S, 600, xmax=x + w - 4)
            yy += LH + 6
            continue
        yy = message(cv, x + 5, yy, w - 9, role, lines)
    cv.parts[idx] = (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{yy - y:.2f}" rx="3" fill="#FFFFFF" '
                     f'stroke="{G.LINE}" stroke-width="0.6"/>')
    if not foot:
        return yy
    yb = yy + 8                      # the first note's baseline, below the window
    for f in foot:
        for j, row in enumerate(wrap(f, w - 13, G.S)):
            cv.text(x + 9 if j == 0 else x + 13, yb, row, G.S, xmax=x + w)
            yb += LH
    return yb - LH + 3               # just below the last note's descenders


# ---------------------------------------------------------------- the figure and the table

def figure_wa(review_dir=None):
    """The full transcripts, for the Web Appendix (wa_fig_settings): every setting's messages with what is left out
    in square brackets. review_dir: a folder in which to keep the picture at the page's width, for a check by eye."""
    W = 468
    m = 1.5                                   # a margin, so that no letter's side bearing leaves the page
    cv = Canvas()
    col = (W - 2 * m - 14) / 2
    y = 9
    # the panels in the order of the studies: a (1a) at left, b and c (1b) stacked at right; d (1c) across; e (1c), f (2a)
    ya = panel_plain(cv, m, y, col)
    yb = panel_request(cv, m + col + 14, y, col)
    yc = panel_clarify(cv, m + col + 14, yb + 13, col)
    y = max(ya, yc) + 13
    y = panel_store(cv, m, y, W - 2 * m) + 13
    we = (W - 2 * m - 14) * 0.56              # the search panel holds the longer lines
    ye = panel_search(cv, m, y, we)
    yf = panel_reviews(cv, m + we + 14, y, W - 2 * m - 14 - we)
    y = max(ye, yf)
    H = round(y + 4)
    G.render("wa_fig_settings", G.page("\n".join(cv.parts), W, H), W, H)
    print(f"wa_fig_settings: {W} x {H} pt")



STAGE_BG = "#F5F7F9"


def parse_block(lines):
    """name, brand, price, the specification pairs and the reviews line of one plain-text product block."""
    d = {"specs": []}
    for ln in lines[1:]:
        s = ln.strip()
        for key in ("Name", "Brand", "Price", "Reviews"):
            if s.startswith(key + ":"):
                d[key.lower()] = s.split(": ", 1)[1]
        if ln.startswith("  ") and ":" in s and not s.startswith(("Review site", "Customer")):
            d["specs"].append(s)
        if s == "Sponsored":
            d["sponsored"] = True
    return d


def esc(s):
    return G.esc(s).replace('"', "&quot;")


def stars(rating, size=6.0):
    """Five stars, the first round(rating, 1) of them filled in the accent; drawn as SVG so that they print as vector."""
    pts = []
    import math
    for k in range(10):
        r = size / 2 if k % 2 == 0 else size / 4.6
        a = math.pi / 2 + k * math.pi / 5
        pts.append(f"{size / 2 + r * math.cos(a):.2f},{size / 2 - r * math.sin(a):.2f}")
    star = " ".join(pts)
    w = size * 5 + 4 * 1.2
    fill = 0.0
    shapes = []
    for i in range(5):
        x = i * (size + 1.2)
        part = max(0.0, min(1.0, rating - i))
        shapes.append(f'<polygon transform="translate({x:.2f},0)" points="{star}" fill="#CBD3DA"/>')
        if part > 0:
            cid = f"s{abs(hash((rating, i, size))) % 10 ** 8}"
            # the clip is in the star's own coordinates, which its translate already moves
            shapes.append(f'<clipPath id="{cid}"><rect x="0" y="0" width="{size * part:.2f}" height="{size}"/></clipPath>'
                          f'<polygon transform="translate({x:.2f},0)" points="{star}" fill="{G.ACCENT}" '
                          f'clip-path="url(#{cid})"/>')
        fill += part
    return (f'<svg class="stars" width="{w:.2f}pt" height="{size}pt" viewBox="0 0 {w:.2f} {size}">'
            + "".join(shapes) + "</svg>")


LENS = ('<svg class="lens" width="6pt" height="6pt" viewBox="0 0 12 12"><circle cx="5" cy="5" r="3.6" fill="none" '
        f'stroke="{G.ACCENT}" stroke-width="1.5"/><line x1="7.7" y1="7.7" x2="11" y2="11" stroke="{G.ACCENT}" '
        'stroke-width="1.6" stroke-linecap="round"/></svg>')


def bars(widths, cls="bar"):
    return "".join(f'<div class="{cls}" style="width:{w}%"></div>' for w in widths)


def tile(letter, label, body):
    return (f'<section class="tile"><div class="label"><span class="k">{letter}</span><span>{esc(label)}</span></div>'
            f'<div class="stage">{body}<div class="fade"></div><div class="more">\u2026</div></div></section>')


def snap_plain():
    r = item("plain")
    e = parse_block(block(r["user"], r["best"]))
    o = parse_block(block(r["user"], r["order"][1]))
    rv = e["reviews"]
    rating = float(rv.split(", ")[1].split(" ")[0])
    card = lambda p, full: (
        f'<div class="card"><div class="row"><span class="title">{esc(p["name"])}</span>'
        f'<span class="price">{esc(p["price"])}</span></div><div class="muted">Brand: {esc(p["brand"])}</div>'
        + (f'<div class="specs">' + "".join(f"<div>{esc(s)}</div>" for s in p["specs"]) + "</div>"
           f'<div class="rev">{stars(rating)}<span>{esc(rv)}</span></div>' if full else
           f'<div class="specs">{bars([70, 55, 62])}</div>') + "</div>")
    return tile("a", "A table of products (Study 1a)", card(e, True) + card(o, False))


def snap_request():
    r = item("request")
    reqs = {q["id"]: q for q in map(json.loads, gzip.open(PKG / "study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz", "rt", encoding="utf8"))}
    src = pretty_source(reqs[r["request"]])
    body = (f'<div class="bubble me">{esc(r["user"].splitlines()[0])}</div>'
            f'<div class="meta">{esc(src[0].upper() + src[1:])}</div>'
            f'<div class="bubble them wide">{bars([80, 64])}</div>'
            f'<div class="card mini">{bars([58, 40])}</div><div class="card mini">{bars([52, 44])}</div>')
    return tile("b", "A typed request (Study 1b)", body)


def snap_clarify():
    r = item("clarify")
    q = json.loads(SOURCES.read_text(encoding="utf-8"))["clarify"]
    assert q["item"] == r["id"], "settings_sources.json is stale; run --extract"
    body = (f'<div class="bubble them">{esc(q["question"])}</div><div class="meta left">Qwen 2.5 7B</div>'
            f'<div class="bubble me">{esc(r["followup"])}</div>'
            f'<div class="bubble them wide">{bars([75, 55])}</div>')
    return tile("c", "A clarifying question (Study 1b)", body)


def snap_store():
    r = item("sponsored")
    rows = []
    for k, L in enumerate(r["order"], 1):
        p = parse_block(block(r["user"], L))
        rating = float(p["reviews"].split(", ")[1].split(" ")[0])
        badge = '<span class="badge">Sponsored</span>' if p.get("sponsored") else ""
        rows.append(f'<div class="li"><span class="rank">{k}</span><div class="grow"><div class="row"><span class="name">'
                    f'{esc(p["name"])}</span><span class="price">{esc(p["price"])}</span></div>'
                    f'<div class="rev">{stars(rating, 5.2)}<span class="muted">{rating}</span>{badge}</div></div></div>')
    return tile("d", "The store's listing (Study 1c)", f'<div class="card list">{"".join(rows)}</div>')


def snap_search():
    s2 = item("search2")
    src = json.loads(SOURCES.read_text(encoding="utf-8"))["search"]
    assert src["item"] == s2["id"] and src["queries"] == s2["queries"], "settings_sources.json is stale; run --extract"
    u2 = s2["user"].splitlines()
    chips = "".join(f'<div class="chip">{LENS}<span>{esc(q)}</span></div>' for q in s2["queries"])
    found = "".join(f'<div class="li"><div class="grow row"><span class="name">{esc(p["name"])}</span>'
                    f'<span class="price">{esc(p["price"])}</span></div></div>'
                    for p in (parse_block(block(s2["user"], L)) for L in s2["returned"]))
    body = (f'<div class="meta left top">Claude Sonnet 5.5</div>{chips}'
            f'<div class="sub">{esc(u2[3])}</div><div class="card list">{found}</div>')
    return tile("e", "The model's own searches (Study 1c)", body)


def snap_reviews():
    import re
    r = item("review_pos")
    b = block(r["user"], r["best"])
    p = parse_block(b)
    k = b.index("Retrieved from review sites:")
    rating_line = b[k + 1].strip().split(": ", 1)[1]
    score, listed = rating_line.split(", ", 1)
    quotes = re.findall(r'"([^"]+)"', b[k + 2])
    body = (f'<div class="card"><div class="title">{esc(p["name"])}</div><div class="muted">{esc(b[k])}</div>'
            f'<div class="score">{esc(score)}</div><div>{esc(listed)}</div>'
            + "".join(f'<div class="quote">\u201c{esc(t)}\u201d</div>' for t in quotes) + "</div>")
    return tile("f", "Review pages at answer time (Study 2a)", body)


SNAP_CSS = f"""
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: #ffffff; }}
body {{ width: 468pt; font-family: "Fira Sans"; color: {G.INK}; font-size: {G.S}pt; line-height: 1.28;
  font-feature-settings: "tnum" 1, "lnum" 1; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 10pt; row-gap: 10pt;
  padding: 1pt 1.5pt 1.5pt; }}
.label {{ display: flex; align-items: baseline; gap: 4.5pt; margin: 0 0 4pt; font-size: {G.M}pt; font-weight: 600;
  white-space: nowrap; }}
.label .k {{ font-size: {G.L}pt; }}
.stage {{ position: relative; height: 136pt; overflow: hidden; border-radius: 6pt; background: {STAGE_BG};
  padding: 8pt 8pt 0; }}
.fade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 40pt;
  background: linear-gradient(to bottom, rgba(245,247,249,0) 0%, rgba(245,247,249,0.9) 58%, {STAGE_BG} 82%); }}
.more {{ position: absolute; left: 0; right: 0; bottom: 3pt; text-align: center; font-size: {G.L}pt; color: #7D8A96; }}
.card {{ background: #ffffff; border: 0.6pt solid #D5DBE0; border-radius: 6pt; padding: 6pt 7pt; }}
.card + .card {{ margin-top: 5pt; }}
.card.mini {{ padding: 5pt 7pt; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline; gap: 6pt; }}
.title, .name {{ font-weight: 600; }}
.title {{ font-size: {G.M}pt; }}
.price {{ font-weight: 600; white-space: nowrap; }}
.muted {{ color: #56626E; }}
.specs {{ margin-top: 3pt; }}
.rev {{ display: flex; align-items: center; gap: 3.5pt; margin-top: 2.5pt; }}
.stars {{ flex: none; display: block; }}
.bar {{ height: 4.4pt; border-radius: 2.2pt; background: #E2E7EB; }}
.bar + .bar {{ margin-top: 3.2pt; }}
.bar.light {{ background: rgba(255,255,255,0.45); }}
.bubble {{ width: fit-content; max-width: 84%; padding: 4pt 6.5pt; border-radius: 8pt; }}
.bubble + .bubble, .meta + .bubble {{ margin-top: 4.5pt; }}
.bubble.me {{ margin-left: auto; background: {G.ACCENT}; color: #ffffff; border-bottom-right-radius: 2.5pt; }}
.bubble.them {{ background: #ffffff; border: 0.6pt solid #D5DBE0; border-bottom-left-radius: 2.5pt; }}
.bubble.wide {{ width: 70%; }}
.bubble.short {{ width: 46%; }}
.meta {{ margin-top: 2pt; color: #56626E; text-align: right; }}
.meta.left {{ text-align: left; }}
.meta.top {{ margin: 0 0 3pt; }}
.chip {{ display: flex; align-items: flex-start; gap: 4pt; padding: 3pt 6.5pt 3pt 5pt; border-radius: 7pt;
  background: #DCE6EC; font-weight: 600; }}
.chip + .chip {{ margin-top: 3pt; }}
.lens {{ flex: none; margin-top: 1.2pt; }}
.sub {{ margin: 5pt 0 3pt; color: #56626E; }}
.list {{ padding: 1pt 7pt; }}
.li {{ display: flex; align-items: flex-start; gap: 5pt; padding: 3.6pt 0; }}
.li + .li {{ border-top: 0.6pt solid #E6EAEE; }}
.rank {{ flex: none; width: 6pt; color: #56626E; text-align: right; }}
.grow {{ flex: 1; min-width: 0; }}
.badge {{ display: inline-flex; align-items: center; height: 8.6pt; padding: 0 4.5pt; margin-left: 2pt;
  border-radius: 99pt; background: #EAEEF1; font-weight: 600; }}
.score {{ margin-top: 4pt; font-size: {G.L}pt; font-weight: 600; color: {G.ACCENT}; }}
.quote {{ margin-top: 4pt; padding-left: 5pt; border-left: 1.2pt solid #DCE6EC; }}
"""

SNAP_AUDIT_JS = """() => {
  const out = [];
  if (!document.fonts.check('6.5pt "Fira Sans"')) out.push('Fira Sans did not load');
  const runs = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    if (!n.textContent.trim()) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) runs.push({r, s: n.textContent.trim().slice(0, 40), el: n.parentElement});
  }
  for (const a of runs) {
    const stage = a.el.closest('.stage');
    const box = a.el.closest('.card, .bubble, .chip, .badge') || stage;
    if (box) {
      const b = box.getBoundingClientRect();
      if (a.r.left < b.left - 0.5 || a.r.right > b.right + 0.5) out.push('outside its box: ' + a.s);
    }
    if (stage && !a.el.closest('.more')) {
      const s = stage.getBoundingClientRect(), fadeTop = s.bottom - stage.querySelector('.fade').offsetHeight;
      if (a.r.top < fadeTop && a.r.bottom > s.bottom) out.push('cut by the stage above its fade: ' + a.s);
    }
    if (a.r.right > document.body.getBoundingClientRect().right + 0.5) out.push('outside the page: ' + a.s);
  }
  for (let i = 0; i < runs.length; i++) for (let j = i + 1; j < runs.length; j++) {
    const a = runs[i].r, c = runs[j].r;
    if (runs[i].el === runs[j].el) continue;
    // the ellipsis is drawn over the faded foot: it may sit on a line only where that line is mostly faded out
    const m = runs[i].el.closest('.more') ? 0 : runs[j].el.closest('.more') ? 1 : -1;
    if (m >= 0) {
      const other = m === 0 ? runs[j] : runs[i], st = other.el.closest('.stage');
      if (st) { const s = st.getBoundingClientRect(), f = st.querySelector('.fade').offsetHeight;
        if (other.r.top > s.bottom - f * 0.6) continue; }
    }
    if (a.left < c.right - 0.5 && c.left < a.right - 0.5 && a.top < c.bottom - 1 && c.top < a.bottom - 1)
      out.push('overlap: ' + runs[i].s + ' / ' + runs[j].s);
  }
  return [...new Set(out)];
}"""


def snapshot(review_dir=None):
    reg = G.truetype("FiraSans-Regular").as_uri()
    semi = G.truetype("FiraSans-SemiBold").as_uri()
    tiles = [snap_plain(), snap_request(), snap_clarify(), snap_store(), snap_search(), snap_reviews()]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'@font-face {{ font-family: "Fira Sans"; src: url("{reg}"); font-weight: 400; }}'
            f'@font-face {{ font-family: "Fira Sans"; src: url("{semi}"); font-weight: 600; }}'
            f'@page {{ size: 6.5in 4.5in; margin: 0; }}{SNAP_CSS}</style></head><body><div class="grid">'
            + "".join(tiles) + "</div></body></html>")
    src = HERE / "diagrams" / "fig_settings.html"
    src.write_text(html, encoding="utf-8", newline="\n")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        pg = browser.new_page(viewport={"width": 624, "height": 600}, device_scale_factor=200 / 96)
        pg.goto(src.as_uri())
        pg.evaluate("document.fonts.ready.then(() => true)")
        problems = pg.evaluate(SNAP_AUDIT_JS)
        h_px = pg.evaluate("Math.ceil(document.querySelector('.grid').getBoundingClientRect().bottom)")
        if problems:
            browser.close()
            raise AssertionError("fig_settings: " + "; ".join(problems))
        H = round(h_px * 0.75 + 0.5)
        assert H <= 324, f"fig_settings: {H} points tall, more than half a page (324)"
        pg.add_style_tag(content=f"@page {{ size: 6.5in {H / 72}in; margin: 0; }}")
        pg.screenshot(path=str(HERE / "fig_settings.tmp.png"), clip={"x": 0, "y": 0, "width": 624, "height": round(H / 0.75)})
        pg.pdf(path=str(HERE / "fig_settings.tmp.pdf"), width="6.5in", height=f"{H / 72}in", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        small = browser.new_page(viewport={"width": 624, "height": 600}, device_scale_factor=1)
        small.goto(src.as_uri())
        small.evaluate("document.fonts.ready.then(() => true)")
        small.screenshot(path=str(HERE / "fig_settings.pagewidth.tmp.png"), clip={"x": 0, "y": 0, "width": 624,
                                                                                    "height": round(H / 0.75)})
        browser.close()
    import pymupdf
    doc = pymupdf.open(HERE / "fig_settings.tmp.pdf")
    kinds = {f[2] for f in doc[0].get_fonts()}
    sizes = [s["size"] for b in doc[0].get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"]
             if s["text"].strip()]
    pages, images = len(doc), len(doc[0].get_images())
    doc.close()
    assert pages == 1, f"fig_settings: {pages} pages"
    assert "Type3" not in kinds, f"fig_settings: Type 3 fonts ({kinds})"
    assert min(sizes) >= 6.0 - 0.05, f"fig_settings: text at {min(sizes)} pt"
    assert images == 0, f"fig_settings: {images} pictures in the PDF; every mark should be vector"
    for ext in ("png", "pdf"):
        G.replace_when_free(HERE / f"fig_settings.tmp.{ext}", HERE / f"fig_settings.{ext}")
    # the picture at the page's width is a check for the eye, not an output of the paper: it is kept only in a folder
    # given with --review-dir, and otherwise removed, so that a run writes nothing outside the repository's own files
    tmp = HERE / "fig_settings.pagewidth.tmp.png"
    if review_dir is not None:
        Path(review_dir).mkdir(parents=True, exist_ok=True)
        G.replace_when_free(tmp, Path(review_dir) / "fig_settings.pagewidth.png")
    else:
        tmp.unlink(missing_ok=True)
    print(f"fig_settings: 468 x {H} pt, vector, fonts {sorted(kinds)}")


def developers():
    return {r["key"]: r["developer"] for r in csv.DictReader(open(CHARS, encoding="utf8"))}


ROWS = [
    ("1a-strict", "A table of products", "1a",
     "A system prompt for a shopping assistant, the shopper's request and five products in plain text, each with a name, "
     "a brand, a price, its listed attributes and its reviews; the products were presented with or without brand names, "
     "or with the brand names of the optimal product and a familiar product swapped.",
     "A merchant's product feed holds the brand, the price and the attributes, and can hold the star rating and the number "
     "of reviews; brand is a required field of OpenAI's and Google's feeds (OpenAI 2026a; Google n.d.-a), and Google's "
     "Shopping Graph holds each listing \"with details like reviews, prices, color options and availability\" (Google "
     "2025)."),
    ("1b-requests", "A typed request", "1b",
     "The same five products after a request that a person typed into ChatGPT through WildChat (Zhao et al. 2024) or into "
     "Chatbot Arena or Search Arena (Chiang et al. 2024; Miroyan et al. 2026), one that crowd workers wrote for WebShop "
     "(Yao et al. 2022), or, for categories with fewer than ten such requests, one written by the author; the filter "
     "follows Uberti-Bona Marin et al. (2026).",
     "The customer describes a need, and then \"ChatGPT looks for relevant options\" (OpenAI 2026a)."),
    ("1c-store", "The store's listing", "1c",
     "The same products as objects of OpenAI's current or October 2025 product feed (OpenAI 2026a, 2025a) or of Google's "
     "Merchant Center feed (Google n.d.-a), or as schema.org markup (Schema.org 2026); a Sponsored label on a familiar "
     "product or on the optimal product, and the optimal product listed first, third or last (as in Allouah et al. "
     "2025); the optimal product rated 0.1, 0.3 or 0.5 stars higher (Chu and Hou 2026); or an instruction from the "
     "developer in the system prompt.",
     "Merchants send product feeds in these formats to ChatGPT and Google (OpenAI 2026a, 2025a; Google n.d.-a), and to "
     "Copilot through Microsoft Merchant Center (Sheth and Yada 2026), and they mark up their pages with schema.org "
     "(Google n.d.-b; Schema.org 2026); Google is testing offers in AI Mode labeled \"Sponsored deal\" (Google 2026), and "
     "ChatGPT shows sponsored product cards below its responses (OpenAI n.d.-b)."),
    ("1c-search", "The model's own searches", "1c",
     "First the request and an instruction to write one to three searches of one store's catalog; then the request, the "
     "model's own searches and the products that matched them, as a language model searches the simulated shop of Yao "
     "et al. (2022).",
     "Google's AI Mode \"runs several simultaneous searches\" for a shopping question (Google 2025); ChatGPT rewrites a "
     "question into its own search queries (Chen and Koudas 2026); for Amazon's Rufus, \"the LLM first selects "
     "information\" from the catalog, the customer reviews and the community Q&A before it responds (Chilimbi 2024)."),
    ("2a-retrieval", "Review pages at answer time", "2a",
     "Under each product, a review site's rating and three customer reviews, positive, mixed or negative, with the same "
     "text under every product.",
     "ChatGPT summarizes reviews from public sites (OpenAI n.d.-a); Rufus retrieves customer reviews and community Q&A "
     "(Chilimbi 2024); Google's Shopping Graph holds reviews (Google 2025)."),
    ("1b-clarifying", "A clarifying question", "1b",
     "Permission to ask the shopper one question before recommending; a model that asked received the reply \"I don't "
     "have anything to add. Please recommend one of these products.\" The design follows research on clarifying "
     "questions in conversational search and recommendation (Zhang et al. 2018; Aliannejadi et al. 2019; Zamani et al. "
     "2020; Chen, Wiseman and Dhingra 2024).",
     "ChatGPT's shopping research \"asks smart clarifying questions\" before it recommends, about \"your budget, who the "
     "item is for, or which features you care about\" (OpenAI 2025b)."),
]


def counts():
    """For each setting's row of COVERAGE.json: the models whose responses have come back, their developers, and
    whether the analysis is complete."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in cov["rows"]}
    dev = developers()
    out = {}
    for cid, *_ in ROWS:
        names, done, going = set(), set(), set()
        for cell in rows[cid]["cells"].values():
            ns = set(cell.get("names") or [])
            names |= ns
            (done if cell.get("status", "").startswith("done") else going).update(ns)
        unknown = sorted(n for n in names if n not in dev)
        if unknown:
            raise SystemExit(f"refused: no developer for {unknown} (model_characteristics.csv)")
        devs = sorted({dev[n] for n in names})
        status = ("complete" if not going else
                  f"complete for {len(done)} models; in progress for {len(going)}" if done else "in progress")
        out[cid] = {"coverage_row": cid, "models": len(names), "developers": len(devs), "developer_names": devs,
                    "analysis": status}
    return cov["written"], out


def write_table(stem, title, intro, header, cells_of):
    written, cnt = counts()
    out = [f"# {title}", "", intro.format(written=written), "", "| " + " | ".join(header) + " |",
           "|" + "---|" * len(header)]
    machine = []
    for row in ROWS:
        c = cnt[row[0]]
        out.append("| " + " | ".join(cells_of(row, c)) + " |")
        machine.append({**c, "setting": row[1], "study": row[2]})
    (HERE / f"{stem}.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    (HERE / f"{stem}.json").write_text(json.dumps({"coverage_written": written, "rows": machine}, indent=1) + "\n",
                                       encoding="utf-8", newline="\n")
    print(f"written {stem}.md and {stem}.json")
    return machine


SOURCE_NOTE = ("Written by `exhibits/code/fig_settings.py --table-only` from `models/answered-by-setting.json` (as of "
               "{written}) and `models/model_characteristics.csv`. Every reference, with its address, its access date and "
               "the words it supports, is in `exhibits/materials/settings_sources.md`. The models are counted when their "
               "responses have come back.")


def table_wa():
    """The long table, for the Web Appendix."""
    m = write_table("wa_table_settings", "The settings in which the models chose, and how deployed shopping assistants "
                    "work (Web Appendix)", SOURCE_NOTE,
                    ["Setting", "Study", "What the model received", "How deployed shopping assistants do the same",
                     "Models (developers)", "Analysis"],
                    lambda r, c: [r[1], r[2], r[3], r[4], f"{c['models']} ({c['developers']})", c["analysis"]])
    for x in m:
        print(f"  {x['setting']}: {x['models']} models, {x['developers']} developers; {x['analysis']}")


# The main text's table: one short line for what the assistant saw and one for its counterpart in deployed assistants,
# each from the long table's cells and sources (ROWS), in the order of the snapshot's panels.
SHORT = {
    "1a-strict": ("Five products as text, each with a name, a brand, a price, attributes and reviews",
                  "Product feeds require the brand and list the price and attributes (OpenAI 2026a; Google n.d.-a)"),
    "1b-requests": ("A request that a person typed into a chat assistant (Zhao et al. 2024; Chiang et al. 2024)",
                    "The customer describes a need, and \"ChatGPT looks for relevant options\" (OpenAI 2026a)"),
    "1b-clarifying": ("Permission to ask the shopper one question first (Zhang et al. 2018; Aliannejadi et al. 2019)",
                      "ChatGPT's shopping research \"asks smart clarifying questions\" (OpenAI 2025b)"),
    "1c-store": ("Feed fields, schema.org markup, a Sponsored label, star ratings and positions (Allouah et al. 2025)",
                 "OpenAI's and Google's feeds and schema.org markup (OpenAI 2026a; Google n.d.-a; Schema.org 2026)"),
    "1c-search": ("Its own searches of the store's catalog, then the products returned (Yao et al. 2022)",
                  "Google's AI Mode \"runs several simultaneous searches\" (Google 2025)"),
    "2a-retrieval": ("A review site's rating and customer reviews under each product",
                     "ChatGPT summarizes reviews from public sites (OpenAI n.d.-a)"),
}
ORDER = ["1a-strict", "1b-requests", "1b-clarifying", "1c-store", "1c-search", "2a-retrieval"]


def table_main():
    by = {r[0]: r for r in ROWS}
    rows_saved = list(ROWS)
    ROWS[:] = [by[k] for k in ORDER]
    try:
        m = write_table("table_settings", "The settings in which the models chose", SOURCE_NOTE,
                        ["Setting (study)", "What the assistant saw", "Its counterpart in deployed assistants",
                         "Models (developers)"],
                        lambda r, c: [f"{r[1]} ({r[2]})", SHORT[r[0]][0], SHORT[r[0]][1],
                                      f"{c['models']} ({c['developers']})"
                                      + ("" if c["analysis"] == "complete" else ", analysis in progress")])
    finally:
        ROWS[:] = rows_saved
    return m


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--table-only", action="store_true")
    ap.add_argument("--snapshot-only", action="store_true")
    ap.add_argument("--review-dir", help="a folder in which to keep the figure's picture at the page's width")
    a = ap.parse_args()
    if a.extract:
        extract()
        return
    table_wa()
    table_main()
    if a.table_only:
        return
    snapshot(a.review_dir)
    if not a.snapshot_only:
        figure_wa(a.review_dir)


if __name__ == "__main__":
    main()
