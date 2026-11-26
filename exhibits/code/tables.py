"""Tables of the web appendix, generated from the results files and the experiment's own definitions.

No number is typed here: each table reads numbers.json, a results CSV, or experiment/assortments.py. Each function
returns a Markdown pipe table with its caption, and TABLES maps a marker name ({{table:<name>}}) to its function.
"""
import csv
import paper_names  # noqa: E402  (the package's helper: results files and their keys)
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(PKG / "common"))   # the corpus's tables and conditions (common/experiment/)
S1 = paper_names.later(PKG / "study1b-64-models-on-34-tables/results/numbers.json")
MINUS = "−"


def _wa(key):
    """The letter of the Web Appendix section labelled <key> (markers.wa_letter), for notes that cite a section."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from markers import wa_letter
    return wa_letter(key)

CATEGORY = {
    "backpacks": "Backpacks", "blenders": "Blenders", "cameras": "Cameras", "coffee_makers": "Coffee makers",
    "earbuds": "Earbuds", "electric_toothbrushes": "Electric toothbrushes", "external_ssds": "External drives",
    "headphones": "Headphones", "keyboards": "Keyboards", "laptops": "Laptops", "monitors": "Monitors",
    "portable_speakers": "Portable speakers", "robot_vacuums": "Robot vacuums", "running_shoes": "Running shoes",
    "smartphones": "Smartphones", "smartwatches": "Smartwatches", "tablets": "Tablets", "tvs": "Televisions",
    "water_bottles": "Water bottles", "wireless_routers": "Wireless routers",
}


def table_name(tid):
    """'sr_tvs_03' -> 'Televisions 3'; the name used for a product table everywhere in the appendix."""
    t = tid[3:] if tid.startswith("sr_") else tid
    cat, num = t.rsplit("_", 1)
    return f"{CATEGORY[cat]} {int(num)}"


def n(x, dec=2):
    x = float(x)
    if round(x, dec) == 0:  # no "−0.0": a value that rounds to zero prints as zero
        x = 0.0
    return f"{x:,.{dec}f}".replace("-", MINUS)


def pct(x, dec=1):
    return n(x, dec) + "%"


def md_table(header, rows, caption, align=None, note=None, label=None, widths=None):
    """A pipe table with a short title above (Table W<n>.), an optional note below, and a label for \\ref.
    widths, when given, sets the relative width of each column in place of the computed one."""
    md = _md_table(header, rows, caption + (f" {{#tbl:{label}}}" if label else ""), align, widths)
    if note:
        md += f"\n\n::: tnote\n*Notes:* {note}\n:::"
    return md


def _md_table(header, rows, caption, align=None, widths=None):
    align = align or ["l"] * len(header)
    # Pandoc sets the relative width of each column of a wide table from the dashes under its header, so the
    # dashes follow the longest cell of the column (header words count once each, so a long header can wrap).
    if widths is None:
        widths = []
        for j, h in enumerate(header):
            longest = max([len(str(r[j])) for r in rows] + [max([len(w) for w in str(h).split()] + [0]) + 3,
                                                             len(str(h)) // 2 + 1])
            widths.append(max(4, min(longest, 44)) + 2)
    seps = []
    for a, w in zip(align, widths):
        seps.append({"l": ":" + "-" * (w - 1), "r": "-" * (w - 1) + ":", "c": ":" + "-" * (w - 2) + ":"}[a])
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(seps) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    out.append("")
    out.append(f"Table: {caption}")
    return "\n".join(out)


# ---------------------------------------------------------------- WA1, the models

MODEL = {  # model key in the corpus -> (name, developer)
    "claude-haiku-4.5": ("Claude Haiku 4.5", "Anthropic"),
    "claude-haiku-4.5-thinking": ("Claude Haiku 4.5", "Anthropic"),
    "claude-sonnet-4.6": ("Claude Sonnet 4.6", "Anthropic"),
    "claude-sonnet-4.6-thinking": ("Claude Sonnet 4.6", "Anthropic"),
    "claude-opus-4.6": ("Claude Opus 4.6", "Anthropic"),
    "claude-opus-4.7": ("Claude Opus 4.7", "Anthropic"),
    "gpt-4o": ("GPT-4o", "OpenAI"), "gpt-4o-mini": ("GPT-4o mini", "OpenAI"),
    "gpt-4.1-mini": ("GPT-4.1 mini", "OpenAI"), "gpt-4.1-nano": ("GPT-4.1 nano", "OpenAI"),
    "gpt-5-mini": ("GPT-5 mini", "OpenAI"), "gpt-5.4": ("GPT-5.4", "OpenAI"),
    "gpt-5.4-mini": ("GPT-5.4 mini", "OpenAI"), "gpt-5.4-mini-thinking": ("GPT-5.4 mini", "OpenAI"),
    "gpt-5.4-nano": ("GPT-5.4 nano", "OpenAI"),
    "gemini-2.0-flash": ("Gemini 2.0 Flash", "Google"), "gemini-2.5-flash": ("Gemini 2.5 Flash", "Google"),
    "gemini-2.5-flash-lite": ("Gemini 2.5 Flash-Lite", "Google"), "gemini-2.5-pro": ("Gemini 2.5 Pro", "Google"),
    "gemini-3-flash": ("Gemini 3 Flash", "Google"), "gemini-3-flash-thinking": ("Gemini 3 Flash", "Google"),
    "gemini-3.1-flash-lite": ("Gemini 3.1 Flash-Lite", "Google"), "gemini-3.1-pro": ("Gemini 3.1 Pro", "Google"),
    "gemma-3-27b": ("Gemma 3 27B", "Google"), "gemma-4-31b-it": ("Gemma 4 31B", "Google"),
    "deepseek-v3": ("DeepSeek V3", "DeepSeek"), "deepseek-r1": ("DeepSeek R1", "DeepSeek"),
    "llama-3.3-70b": ("Llama 3.3 70B", "Meta"), "kimi-k2": ("Kimi K2", "Moonshot AI"),
    "qwen-2.5-72b": ("Qwen 2.5 72B", "Alibaba"),
}
ACCESS = {"anthropic": "Anthropic API", "openai": "OpenAI API", "google": "Google API", "openrouter": "OpenRouter"}
DEV_ORDER = ["Anthropic", "OpenAI", "Google", "DeepSeek", "Meta", "Moonshot AI", "Alibaba"]


def thinking_label(flags):
    flags = set(flags)
    return "yes" if flags == {"True"} else "no" if flags == {"False"} else "both recorded"


def model_label(m):
    name = MODEL[m["model_key"]][0]
    return name + (" (thinking)" if thinking_label(m["thinking"]) == "yes" else "")


def _per_model():
    return S1["item2_brand_gap_by_model"]["per_model"]


MONTH = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
         "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}


def dates(m):
    """'2026-02-22', '2026-02-27' -> 'Feb 22 to 27'; across months 'Feb 22 to Apr 22'."""
    (_, ma, da), (_, mb, db) = m["answers_from"].split("-"), m["answers_to"].split("-")
    a = f"{MONTH[ma]} {int(da)}"
    if (ma, da) == (mb, db):
        return a
    return f"{a} to {int(db)}" if ma == mb else f"{a} to {MONTH[mb]} {int(db)}"


def wa1_models():
    rows = []
    for m in sorted(_per_model(), key=lambda m: (DEV_ORDER.index(MODEL[m["model_key"]][1]), model_label(m))):
        name, dev = MODEL[m["model_key"]]
        rows.append([name, " / ".join(m["model_id"]).replace("_", "\\_"), route(m),
                     thinking_label(m["thinking"]), dates(m), f"{m['shown']['trials']:,}", f"{m['hidden']['trials']:,}"])
    return md_table(["Model", "Identifier sent", "Access", "Extended thinking", "Collected", "With brand names",
                     "Without brand names"], rows, "The Models of Study 1b Whose Responses Were Deposited First", ["l", "l", "l", "c", "l", "r", "r"],
                    note="The models are grouped by developer (Anthropic, OpenAI, Google, DeepSeek, Meta, Moonshot "
                         "AI, Alibaba). Identifier sent: every identifier recorded with the model's responses. Access: "
                         "every access method recorded with the model's responses (the developer's own API, Google's "
                         "Vertex AI service, or OpenRouter). Extended "
                         "thinking: whether the request asked for it; DeepSeek R1 is recorded both ways, and the "
                         "requests that did not ask for it still allowed Gemini 2.5 Pro a short thinking budget and "
                         "the Gemini 3 models a minimal thinking level. Collected: dates in 2026. With and without "
                         "brand names: the number of responses in each condition.", label="models")


_FOLDERS = json.loads((CODE / "study_folders.json").read_text(encoding="utf-8"))   # each study's folder


def package_file(rel):
    """A file of the package, '{F1B}/results/numbers.json', under its study's folder as the main text's heading names it
    now, or under the folder's name at the package's last layout (package/layout-names.json) until the package is laid
    out again after a heading changes."""
    return PKG / re.sub(r"\{(\w+)\}", lambda m: _FOLDERS[m.group(1)], rel)


def pkgfile(key):
    """{{table:pkgfile/<key>}}: the package path of the full-table file whose key in the package's list is <key>, with
    its study's folder as the main text's heading names it, for a sentence of the Web Appendix that names the file."""
    rows = json.loads((CODE / "full_tables.json").read_text(encoding="utf-8"))
    return next(r["file"] for r in rows if r["key"] == key)


PKG_SETTINGS = package_file("{F1B}/results/numbers.json")


def wa1_settings():
    """The settings recorded with each model's responses in Study 1b's two conditions. Temperature and the thinking
    flag come from the package's model_settings (the two conditions only, as the package reproduces them); the
    lengths, wordings and orders from run_settings, whose counts and wordings must equal the package's."""
    rs = S1["run_settings"]["models"]
    pk = json.loads(PKG_SETTINGS.read_text(encoding="utf-8"))["model_settings"]["models"]
    if set(pk) != set(rs) or any(pk[k]["answers"] != rs[k]["response_length_characters"]["answers"] or
                                 pk[k]["names_shown"]["wording_received_read_from_system_prompt"] !=
                                 rs[k]["names_shown"]["wording_received_read_from_system_prompt"] for k in rs):
        raise ValueError("wa1_settings: the package's model settings differ from run_settings in models, counts or wordings")
    rows, capped, mixed, n_study1 = [], [], [], set()
    temps = {t for r in pk.values() for t in r["temperature"]}
    if temps != {"1.0"}:  # the note states one temperature for every response
        raise ValueError(f"temperatures other than 1.0 recorded: {sorted(temps)}")
    for m in sorted(_per_model(), key=lambda m: (DEV_ORDER.index(MODEL[m["model_key"]][1]), model_label(m))):
        r = rs[m["model_key"]]
        flags = pk[m["model_key"]]["thinking_flag"]
        think = "yes" if set(flags) == {"True"} else "no" if set(flags) == {"False"} else "both"
        if think == "both":
            mixed.append(f"{model_label(m)} has the flag in {flags.get('True', 0):,} responses and not in "
                         f"{flags.get('False', 0):,}.")
        ln = r["response_length_characters"]
        n_study1.add(ln["answers"])
        if "suggests a cap" in str(r["answers_stopping_at_the_largest_length"]):
            capped.append(model_label(m))
        words = lambda c: ", ".join(str(r[c]["wording_received_read_from_system_prompt"].get(k, 0)) for k in "0123")
        rows.append([model_label(m), think, f"{ln['median']:,.0f} ({ln['max']:,.0f})", words("names_shown"),
                     words("names_hidden"),
                     f"{r['names_shown']['distinct_order_and_letters_pct']:.1f}, "
                     f"{r['names_hidden']['distinct_order_and_letters_pct']:.1f}"])
    if capped != ["Gemini 2.5 Pro"]:  # the note and Web Appendix C's text name this model alone
        raise ValueError(f"models whose answers stop at one length: {capped}")
    n1 = " or ".join(f"{k:,}" for k in sorted(n_study1))
    return md_table(["Model", "Thinking flag", "Response length in characters, median (largest)",
                     "Wordings 1 to 4, with brand names", "Wordings 1 to 4, without brand names",
                     "Distinct (%), with, without"], rows,
                    "Settings Recorded With Each Model's Responses", ["l", "l", "r", "r", "r", "r"], label="model-settings",
                    widths=[24, 10, 16, 25, 25, 14],
                    note="From the records of the data collection, for the responses of Study 1b's two conditions, "
                         f"with and without brand names ({n1} responses a model). Every response of every model has "
                         f"a recorded temperature of 1.0. {' '.join(mixed)} Response length: the number of characters in the recorded response, without any "
                         "thinking trace; GPT-4o answered with the letter alone in most of its responses. Wordings: "
                         "the number of responses to each of the four wordings of the instruction, identified from "
                         "the instruction's text. Distinct: the number of different combinations of product order and "
                         "letters among the model's responses in that condition, as a percentage of the number of "
                         "those responses.")


ROUTE_NAMES = {"anthropic": "own API", "openai": "own API", "google": "own API", "google_vertex": "Vertex AI",
               "openrouter": "OpenRouter"}


def route(m):
    """The routes of access recorded with a model's answers (run_settings: every provider recorded)."""
    providers = S1["run_settings"]["models"][m["model_key"]]["provider"]
    names = sorted({ROUTE_NAMES[p] for p in providers}, key=["own API", "Vertex AI", "OpenRouter"].index)
    return ", ".join(names)


def wa1_value(what):
    rs = S1["run_settings"]["models"]
    if what == "gpro_answers":
        g = rs["gemini-2.5-pro"]
        return f"{g['names_shown']['answers'] + g['names_hidden']['answers']:,}"
    if what in ("corpus_min", "corpus_max"):
        return f"{(min if what == 'corpus_min' else max)(r['answers_in_corpus'] for r in rs.values()):,}"
    if what == "min_distinct":
        return f"{min(min(r['names_shown']['distinct_order_and_letters_pct'], r['names_hidden']['distinct_order_and_letters_pct']) for r in rs.values()):.1f}"
    if what == "max_distinct":
        return f"{max(max(r['names_shown']['distinct_order_and_letters_pct'], r['names_hidden']['distinct_order_and_letters_pct']) for r in rs.values()):.1f}"
    raise KeyError(what)


def wa1_count(what):
    pm = _per_model()
    if what == "openrouter_only":
        return str(sum(1 for m in pm if route(m) == "OpenRouter"))
    if what == "both_routes":  # more than one route of access recorded
        return str(sum(1 for m in pm if ", " in route(m)))
    if what == "distinct_models":
        return str(len({MODEL[m["model_key"]][0] for m in pm}))
    if what == "thinking_pairs_by_name":
        names = defaultdict(set)
        for m in pm:
            names[MODEL[m["model_key"]][0]].add(thinking_label(m["thinking"]))
        return str(sum(1 for v in names.values() if {"yes", "no"} <= v))
    if what == "developers":
        return str(len({MODEL[m["model_key"]][1] for m in pm}))
    if what == "identifiers":
        return str(len({tuple(m["model_id"]) for m in pm}))
    if what.startswith("dev:"):
        return str(sum(1 for m in pm if MODEL[m["model_key"]][1] == what[4:]))
    if what == "openrouter":
        return str(sum(1 for m in pm if m["provider"] == "openrouter"))
    if what == "february":  # every answer collected in February 2026
        return str(sum(1 for m in pm if m["answers_to"] < "2026-03-01"))
    if what == "april":  # every answer collected in April 2026
        return str(sum(1 for m in pm if m["answers_from"] >= "2026-04-01"))
    if what == "both_periods":
        return str(sum(1 for m in pm if m["answers_from"] < "2026-03-01" <= m["answers_to"]))
    if what == "thinking_pairs":  # identifiers run both with and without extended thinking
        ids = defaultdict(set)
        for m in pm:
            ids[tuple(m["model_id"])].add(thinking_label(m["thinking"]))
        return str(sum(1 for v in ids.values() if {"yes", "no"} <= v))
    raise KeyError(what)


# ---------------------------------------------------------------- WA2, the product tables

def _assortments():
    from experiment.assortments import ALL_ASSORTMENTS
    return sorted(ALL_ASSORTMENTS, key=lambda a: table_name(a["id"]))


def wa2_wording(i):
    from experiment.conditions import SYSTEM_BASELINE_PARAPHRASES
    return "```\n" + SYSTEM_BASELINE_PARAPHRASES[i].strip() + "\n```"


def wa2_counts(what):
    from experiment.conditions import SYSTEM_BASELINE_PARAPHRASES
    A = _assortments()
    if what == "wordings":
        return str(len(SYSTEM_BASELINE_PARAPHRASES))
    if what == "categories":
        return str(len({a["category"] for a in A}))
    if what == "single_table_categories":
        c = defaultdict(int)
        for a in A:
            c[a["category"]] += 1
        return str(sum(1 for v in c.values() if v == 1))
    raise KeyError(what)


FAMILIARITY = {"high": "high", "medium": "medium", "low": "low"}


FILES_DIR = None
FILES_WRITTEN = []  # (file name, what it holds, appendix letter) of every file that a table function writes
C_EXAMPLES = ("sr_laptops_01",)  # the table that Web Appendix C prints


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def wa2_all_tables():
    """Web Appendix C's product tables: the example printed whole (the request and the scores), and every one of the 34
    written to its own file, named after the table (the appendix states the rule of the names)."""
    pages = _wa2_pages()
    out = []
    for tid, name, k, text in pages:
        letter = _wa("study1b-tables")
        fname = f"{letter}-{_slug(name)}.md"
        if FILES_DIR is not None:  # the file without the appendix's labels and box markup
            plain = re.sub(r"\s*\{#tbl:[^}]+\}", "", re.sub(r"(?m)^:::.*$\n?", "", text))
            (FILES_DIR / fname).write_text(f"# {name}: the request with brand names and the scores of the products\n\n"
                                           + plain, encoding="utf-8")
            entry = (f"34 files named after the tables, such as {letter}-laptops-1.md", "Each product "
                     "table of Study 1b: its request with brand names and the scores of its products", letter)
            if entry not in FILES_WRITTEN:
                FILES_WRITTEN.append(entry)
        if tid in C_EXAMPLES:
            out.append(text)
    return "\n\n".join(out)


def wa2_full_markdown():
    """Every product of the 34 tables of Study 1b, with its table's name, as one Markdown table: the full table that
    Web Appendix C names (it prints two of the 34)."""
    rows, header = [], None
    for _, name, _, text in _wa2_pages():
        lines = [l for l in text.split("\n") if l.startswith("|")]
        header = header or ["Table"] + [c.strip() for c in lines[0].strip().strip("|").split("|")]
        rows += [[name] + [c.strip() for c in l.strip().strip("|").split("|")] for l in lines[2:]]
    return "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n" + \
        "\n".join("| " + " | ".join(r) + " |" for r in rows)


FULL_MARKDOWN = {"wa2_all_tables": wa2_full_markdown}  # a key whose printed form is not its full table


def _wa2_pages():
    """(table id, name, number, the request and the scores of the products in Markdown) for each of the 34 tables."""
    from experiment.conditions import compute_utility_scores
    dom = {t["table"]: t for t in S1["item3_strict_dominance"]["tables"]}
    out = []
    for k, a in enumerate(_assortments(), 1):
        name = table_name(a["id"])
        _, user, _ = _prompt(a["id"], "baseline")
        scores = compute_utility_scores(a)
        maxp = max(p["price"] for p in a["products"]) * 1.1
        rows = []
        for p in a["products"]:
            q, v = p.get("quality_score", 0.5), 1 - p["price"] / maxp
            score = 0.5 * q + 0.5 * v
            assert abs(score - scores[p["letter"]]) < 1e-4, (a["id"], p["letter"], score, scores[p["letter"]])
            rows.append([p["letter"] + (" (top-ranked)" if p.get("is_optimal") else ""), p["brand"],
                         p["brand_familiarity"], f"{p['price']:,.2f}", f"{q:.3f}", f"{v:.3f}", f"{score:.3f}"])
        d = dom[a["id"]]
        group = {"1": "the top-ranked product is better than or equal to every other product",
                 "2": "the top-ranked product is the cheapest but ranks first only under the stated weights",
                 "3": "the top-ranked product is not the cheapest"}
        note = (f"Counting price and the attributes with an agreed order, " f"{group[str(d['group_ordered_only'][0])]}. Counting every attribute, {group[str(d['group_strict'][0])]}. " f"Attributes on which another product is better: {_attr(d['attributes_where_best_loses'])}. Attributes with " f"no agreed order on which the products differ: {_attr(d['attributes_without_an_order_that_differ'])}.")
        n = C_EXAMPLES.index(a["id"]) + 1 if a["id"] in C_EXAMPLES else k + 100  # the printed examples are 1 and 2
        out.append((a["id"], name, k,
                     f"::: {{#exh:c-request-{n} .prompt .compact title=\"{name}, the request with brand names\"}}\n"
                     f"```\n{user.strip()}\n```\n:::\n\n"
                     + md_table(["Product", "Brand", "Familiarity", "Price (USD)", "Quality", "Value", "Score"], rows,
                                f"Product Scores in {name}", ["l", "l", "l", "r", "r", "r", "r"], note=note,
                                label=f"c-scores-{n}")))
    return out


# ---------------------------------------------------------------- WA4, Study 2 by model and by table

def ci(pair, dec=2):
    return f"{n(pair[0], dec)} to {n(pair[1], dec)}"


def wa4_models():
    price = {m["model_key"]: m for m in S1["item5_recommended_price"]["rec_price"]["per_model"]}
    rel = {m["model_key"]: m for m in S1["item5_recommended_price"]["rec_rel"]["per_model"]}
    rows = []
    for m in sorted(_per_model(), key=lambda m: -m["gap_pp"]):
        p = price[m["model_key"]]
        r = rel[m["model_key"]]
        rows.append([model_label(m), pct(m["shown"]["pct"]), pct(m["hidden"]["pct"]), n(m["gap_pp"]),
                     ci(m["ci95_pp_tables_resampled"]), n(p["difference"]), ci(p["ci95_tables_resampled"]),
                     n(r["difference"])])
    return md_table(["Model", "With brand names", "Without brand names", "Effect (points)", "95% interval (points)",
                     "Price difference (USD)", "95% interval (USD)", "Price difference (points of the top-ranked product's price)"], rows,
                    "Study 1b by Model", ["l", "r", "r", "r", "r", "r", "r", "r"], label="by-model",
                    note="With and without brand names: the percentage of responses that recommended a product other "
                         "than the top-ranked product. Effect: with brand names minus without them. Price difference: "
                         "the mean price of the recommended product with brand names minus without them, in dollars "
                         "and in percentage points of the top-ranked product's price. Intervals: 10,000 resamples of "
                         "the model's 34 tables. Gemma 4 31B gave no product letter in all 20 of its responses with "
                         "brand names on Portable speakers 1; these responses count as recommendations of another "
                         "product in the effect and are left out of the price, so its price interval resamples 33 "
                         "tables.")


def wa4_tables():
    price = {t["table"]: t for t in S1["item5_recommended_price"]["rec_price"]["per_table"]}
    rel = {t["table"]: t for t in S1["item5_recommended_price"]["rec_rel"]["per_table"]}
    rows = []
    for t in sorted(S1["item2_brand_gap_by_model"]["per_table"], key=lambda t: -t["gap_pp"]):
        p, r = price[t["table"]], rel[t["table"]]
        rows.append([table_name(t["table"]), pct(t["shown_pct"]), pct(t["hidden_pct"]), n(t["gap_pp"]),
                     ci(t["ci95_pp_models_resampled"]), f"{p['best_price']:,.2f}", n(p["difference"]),
                     ci(p["ci95_models_resampled"]), n(r["difference"])])
    return md_table(["Table", "With brand names", "Without brand names", "Effect (points)", "95% interval (points)",
                     "Top-ranked product (USD)", "Price difference (USD)", "95% interval (USD)",
                     "Price difference (points of the top-ranked product's price)"], rows,
                    "Study 1b by Table", ["l", "r", "r", "r", "r", "r", "r", "r", "r"], label="by-table",
                    note="The measures are those of Table \\ref{tbl:by-model}, with the price of the table's top-ranked "
                         "product. Intervals: 10,000 resamples of the 30 models. The 20 responses with brand names of "
                         "Gemma 4 31B on Portable speakers 1 that gave no product letter count as recommendations of "
                         "another product in that table's effect and are left out of its price difference.")


GROUP_WORDS = {
    ("strict", "1"): "better than or equal to every other product on price and on every attribute",
    ("ranked", "1"): "better than or equal to every other product on price and on every ranked attribute",
    ("strict", "2"): "the cheapest or tied cheapest, and ranks first only under the stated weights",
    ("ranked", "2"): "the cheapest or tied cheapest, and ranks first only under the stated weights",
    ("strict", "3"): "not the cheapest", ("ranked", "3"): "not the cheapest",
}
ATTR_NAMES = {"af": "autofocus", "anc": "noise cancelling", "ip_rating": "water and dust rating",
              "brew_temp": "brewing temperature", "brew_time": "brewing time", "cpu": "processor", "hdr": "HDR format",
              "gps": "GPS", "emptying": "self-emptying base", "durability": "drop rating"}


def wa4_groups():
    g = S1["item3_strict_dominance"]["groups"]
    rows = []
    for reading, key, short in (("Every attribute", "group_strict", "strict"),
                                ("Ranked attributes only", "group_ordered_only", "ranked")):
        for name, v in g[key].items():
            k = name.split()[0]
            gap = v["gap"]
            rows.append([reading, f"{k}: {GROUP_WORDS[(short, k)]}", gap["tables"], pct(gap["shown_pct"], 2),
                         pct(gap["hidden_pct"], 2), n(gap["gap_pp"]), ci(gap["ci95_pp"])])
    return md_table(["Rule", "Group: the top-ranked product is", "Tables", "With brand names", "Without brand names",
                     "Effect (points)", "95% interval (points)"], rows, "Effect by Group of Tables",
                    ["l", "l", "r", "r", "r", "r", "r"], label="groups",
                    note="Every attribute: an unranked attribute on which the products differ counts against the "
                         "top-ranked product. Ranked attributes only: such attributes are set aside. "
                         "With and without brand names: the percentage of recommendations of a product other than "
                         "the top-ranked product. Intervals: a two-way cluster bootstrap over the 30 models and the group's tables, "
                         "10,000 draws.")


def _attr(items):
    keys = sorted({a.split(":")[0].strip() for a in items})
    return ", ".join(ATTR_NAMES.get(k, k.replace("_", " ")) for k in keys) or "none"


def wa4_dominance():
    gap = {t["table"]: t["gap_pp"] for t in S1["item2_brand_gap_by_model"]["per_table"]}
    rows = []
    for t in sorted(S1["item3_strict_dominance"]["tables"],
                    key=lambda t: (t["group_ordered_only"][0], t["group_strict"][0], table_name(t["table"]))):
        rows.append([table_name(t["table"]), f"{t['best_price']:,.2f}", f"{t['cheapest_other_price']:,.2f}",
                     t["group_strict"][0], t["group_ordered_only"][0], _attr(t["attributes_where_best_loses"]),
                     _attr(t["attributes_without_an_order_that_differ"]), n(gap[t["table"]])])
    return md_table(["Table", "Top-ranked product (USD)", "Cheapest other (USD)", "Group, strict", "Group, ranked only",
                     "Another product is better on", "Unranked attributes that differ", "Effect (points)"], rows,
                    "Each Table's Group and the Attributes That Decide It", ["l", "r", "r", "c", "c", "l", "l", "r"],
                    label="dominance",
                    note="Groups: 1, better than or equal to every other product on price and on every attribute "
                         "(strict) or every ranked attribute (ranked only); 2, the cheapest or tied cheapest and ranks "
                         "first only under the stated weights; 3, not the cheapest. Another product is better on: the "
                         "attributes of the spec line on which another product is better than the top-ranked product (price "
                         "is in the two price columns). An attribute with ranked and unranked parts, such as a display "
                         "or a camera, can appear in both attribute columns.")


# ---------------------------------------------------------------- WA8, the consumer studies

CS = paper_names.later(PKG / "study4-peoples-choices-after-a-recommendation/results/numbers.json")
STUDY = {"study_1a": "A", "study_1b": "B", "study_2": "C", "study_3": "4"}


def fmt_p(p):
    p = float(p)
    if p >= 0.001:
        return f"{p:.3f}".lstrip("0") if p < 1 else "1"
    m, e = f"{p:.1e}".split("e")
    return f"{m} × 10^{int(e)}^".replace("-", MINUS)


def _rate(g):
    return f"{g['k']}/{g['n']} ({pct(g['pct'])})"


def _test_row(study, label1, label2, t):
    return [study, f"{label1} against {label2}", _rate(t["group1"]), _rate(t["group2"]),
            f"{n(t['difference_pp'], 1)} ({ci(t['newcombe95_pp'], 1)})", f"{n(t['odds_ratio'])} ({ci(t['or95'])})",
            fmt_p(t["p_fisher"] if study.startswith("Study") else t["p_chi2"])]


def wa8_tests():
    rows = []
    for s, fam, best in (("study_1a", "De'Longhi", "Presswell"), ("study_1b", "JBL", "Vynex")):
        d, lab = CS[s], {"study_1a": "S1", "study_1b": "S2"}[s]
        rows.append(_test_row(lab, f"{fam} chosen, {fam} recommended", "no recommendation",
                              d["H1_primary_branded_BiasedAI_vs_NoAI"]))
        rows.append(_test_row(lab, f"{best} chosen, {best} recommended", "no recommendation",
                              d["H2_optimal_DebiasedAI_vs_NoAI"]))
    d = CS["study_2"]
    rows.append(_test_row("S3", "JBL chosen, with the warning", "the recommendation alone",
                          d["planned_1_branded_Inoculation_vs_BiasedAI"]))
    rows.append(_test_row("S3", "JBL chosen, with the comparison table", "the recommendation alone",
                          d["planned_2_branded_SpecExposed_vs_BiasedAI"]))
    d = CS["study_3"]
    rows.append(_test_row("Study 4", "Familiar brand chosen, familiar brand recommended", "no recommendation",
                          d["H1_focal_biased_vs_neutral"]))
    rows.append(_test_row("Study 4", "Optimal product chosen, optimal product recommended", "no recommendation",
                          d["RQ1_optimal_honest_vs_neutral"]))
    s4 = paper_names.read(PKG / "s4-people-and-language-models-as-advisors/results/numbers.json")
    r1, nl = s4["registered_p1"], s4["nl"]
    rows.append(["S4", "Top-ranked product chosen, people in the models' role", f"{nl['k']}/{nl['n']} ({pct(nl['pct'])})",
                 f"{pct(r1['model_level_mean'])}, the models' mean", f"{n(r1['gap_pp'], 1)} ({ci(r1['wild_ci'], 1)})",
                 "not estimated", fmt_p(r1["p_vs_zero"]) + ", one-sided"])
    return md_table(["Study", "Comparison", "First group", "Second group", "Difference, points (95% interval)",
                     "Odds ratio (95% interval)", "P"], rows, "Preregistered Tests of the Consumer Studies",
                    ["l", "l", "r", "r", "r", "r", "r"], label="consumer-tests",
                    note="First and second group: the number and share of participants who chose the named product. "
                         "Difference: in percentage points, with a Newcombe interval. Odds ratio: with a Woolf "
                         "interval for S1 to S3 and a Haldane-Anscombe interval for Study 4. P: Pearson's chi-squared "
                         "test for S1 to S3 and Fisher's exact test for Study 4. S4: the second group is the mean over "
                         "the 30 models of their rates on the same tables, the interval is a wild cluster bootstrap "
                         "over the models and P is one-sided, as preregistered.")


def wa8_funnel():
    rows = []
    for s in ("study_1a", "study_1b", "study_2"):
        f = CS[s]["funnel"]
        rows.append([{"study_1a": "S1", "study_1b": "S2", "study_2": "S3"}[s], f"{f['rows_in_file']:,}", f"{f['assigned_a_condition']:,}",
                     f["failed_attention_check"], f["under_60_seconds"], f["not_finished"], f"{f['analysed']:,}"])
    return md_table(["Study", "Rows in the file", "Assigned a condition", "Failed the attention check",
                     "Under 60 seconds", "Did not finish", "Analyzed"], rows,
                    "Participants at Each Step in Supplemental Studies S1 to S3", ["l", "r", "r", "r", "r", "r", "r"],
                    label="consumer-funnel",
                    note="Rows that never reached a condition contain no consent answer. Study 4's exclusions follow "
                         "other rules and are given in the text.")


def wa8_study4_choices():
    d = CS["study_3"]
    label = {"biased": "Familiar brand recommended", "honest": "Optimal product recommended",
             "neutral": "No recommendation"}
    rows = []
    for c in ("neutral", "biased", "honest"):
        b, total = d["three_buckets_by_condition"][c], d["condition_n"][c]
        rows.append([label[c], total] + [f"{b[k]} ({pct(100 * b[k] / total)})" for k in ("focal", "optimal", "other")])
    return md_table(["Condition", "Participants", "Chose the familiar focal brand", "Chose the optimal product",
                     "Chose another product"], rows, "Study 4: Choices by Condition", ["l", "r", "r", "r", "r"],
                    label="study4-choices",
                    note="The number and share of participants in each condition who chose the familiar focal brand, "
                         "the optimal product of the seven, or one of the other five products.")


MASK = {}   # the texts of this package already hold the wording of the version for review


def _part_header(line):
    s = line.strip()
    if re.fullmatch(r"--- Product [A-E] ---", s):  # a product's header inside the messages that the models received
        return None
    for a in ("--- ", "=== "):
        if s.startswith(a) and s.endswith(a[::-1]):
            return s[4:-4].strip()
    return None


def screen(name, part):
    """A survey screen laid out as participants saw it: a run of lines with ' | ' becomes a table (its first line the
    header; extra fields of a row stay in the 'Key Specs' cell, where participants saw them), every other line becomes
    a paragraph. Masked like material()."""
    body = material(name, part)[4:-4]  # the text without the fence
    lines = [l for l in body.split("\n")]
    out, run = [], []

    def split(l):
        l = (" " + l) if l.startswith("| ") else l  # a row that starts with an empty cell
        return [c.strip() for c in l.split(" | ")]

    def flush():
        if not run:
            return
        header = split(run[0])
        rows = []
        for l in run[1:]:
            cells = split(l)
            if len(cells) > len(header) and "Key Specs" in header:
                k = header.index("Key Specs")
                extra = len(cells) - len(header)
                cells = cells[:k] + [" \\| ".join(cells[k:k + extra + 1])] + cells[k + extra + 1:]
            rows.append(cells)
        out.append(_md_table(header, rows, "", ["l"] * len(header)).rsplit("\n\nTable: ", 1)[0])
        run.clear()

    for l in lines:
        if " | " in l:
            run.append(l)
            continue
        flush()
        if l.strip():
            out.append(l.strip().replace("*", "\\*"))
    flush()
    return "\n\n".join(out)


def material(name, part=None, mask=True):
    """A materials file as a fenced block, without its header lines (Source, Shown in). With part, only the lines
    under the part header ('--- <part> ---' or '=== <part> ===') whose text starts with <part>, up to the next header."""
    text = (PKG / "exhibits/materials" / f"{name}.txt").read_text(encoding="utf-8")
    lines = [l for l in text.split("\n") if not l.startswith(("Source:", "Shown in:"))]
    if part is not None:
        out, on, found = [], False, False
        for l in lines:
            h = _part_header(l)
            if h is not None:
                on = h.startswith(part)
                found = found or on
                continue
            if on:
                out.append(l)
        if not found:
            raise KeyError(f"{name}: no part starting with '{part}'")
        lines = out
    else:
        # the whole file: the extractor's part headers are not what participants saw; a later screen is marked
        # "--page break--", as published web appendices mark it
        out, seen = [], False
        for l in lines:
            if _part_header(l) is not None:
                if seen:
                    out.append("--page break--")
                seen = True
                continue
            out.append(l)
        lines = out
    body = "\n".join(lines).strip()
    if mask:
        for a, b in MASK.items():
            body = body.replace(a, b)
    return "```\n" + body + "\n```"


# ---------------------------------------------------------------- WA3, names hidden

KIND_TEXT = {
    "1": ("The product's own brand, its owner or a sister brand, named", "\"Razer Green\" on a keyboard; \"Apple M2\" in a laptop"),
    "2": ("A product line or model name of the maker", "\"Galaxy AI\", \"LatteGo\", \"Fresh Foam X\""),
    "3": ("A technology, feature, chip or service name that belongs to one maker", "\"MagSafe\", \"ZoomX\", \"K-Cup\""),
    "4": ("A sentence of the brand's own copy, with only the brand's name replaced", "\"Legendary the manufacturer comfort\""),
    "5": ("Another company's component or platform, which does not identify the maker (listed, not counted)", "\"Sony IMX890\" on a OnePlus phone"),
}


def wa3_kinds():
    d = S1["item4_names_hidden_leak"]
    rows = []
    for k in "12345":
        what, ex = KIND_TEXT[k]
        tables = next((v for key, v in d["tables_with_kind"].items() if key.startswith(k + " ")), None)
        rows.append([k, what, ex, d["listed_texts"][k], "not counted" if tables is None else tables])
    return md_table(["Kind", "What the text is", "Examples", "Texts", "Tables that contain it"], rows,
                    "Brand Traces in Study 1b by Type",
                    ["c", "l", "l", "r", "r"], label="leak-kinds",
                    note="Kind 5 texts name another company's part or platform; they are listed in Table "
                         "\\ref{tbl:leak-list} and are not counted.")


def wa3_gap_without():
    d = S1["item4_names_hidden_leak"]["gap_without"]
    pooled = S1["item2_brand_gap_by_model"]
    shown = S1["item1_reproduce_brand_gap"]["shown"]["pct"]
    hidden = S1["item1_reproduce_brand_gap"]["hidden"]["pct"]
    rows = [["None", 34, pct(shown, 2), pct(hidden, 2), n(pooled["pooled"]["gap_pp"]),
             f"{n(pooled['pooled']['ci95_pp'][0])} to {n(pooled['pooled']['ci95_pp'][1])}"]]
    label = {
        "without kind 1 (brand named)": "The 7 tables with the brand, its parent or a sister brand",
        "without kinds 1 and 2": "The 15 tables with the brand or a product line",
        "without kinds 1 to 3": "The 32 tables with the brand, a product line or a maker's feature",
        "without kinds 1 to 4": "All 34 tables (each has a maker's feature or the brand's copy)",
    }
    for key, v in d.items():
        g = v["gap"]
        if g.get("tables", 0) == 0:
            rows.append([label[key], 0, "", "", "", ""])
            continue
        rows.append([label[key], g["tables"], pct(g["shown_pct"], 2), pct(g["hidden_pct"], 2), n(g["gap_pp"]),
                     f"{n(g['ci95_pp'][0])} to {n(g['ci95_pp'][1])}"])
    return md_table(["Tables left out", "Tables in the estimate", "With brand names", "Without brand names", "Effect (points)", "95% interval (points)"],
                    rows, "Study 1b: Effect Without Tables That Still Named the Brand",
                    ["l", "r", "r", "r", "r", "r"], label="leak-gap",
                    note="With and without brand names: the percentage of responses that recommended a product other "
                         "than the top-ranked product. Effect: with brand names minus without them, in percentage "
                         "points. "
                         "Intervals: a two-way cluster bootstrap over the 30 models and the tables in the estimate,   "
                         "10,000 draws.")


def _leaks():
    path = PKG / "study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv"
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wa3_by_table():
    leaks = _leaks()
    gap = {r["table"]: r["gap_pp"] for r in S1["item2_brand_gap_by_model"]["per_table"]}
    named = S1["item4_names_hidden_leak"]["recognition"]["by_table"]
    counts = defaultdict(lambda: defaultdict(int))
    for r in leaks:
        counts["sr_" + r["table"]][r["kind"].split()[0]] += 1
    rows = []
    for tid in sorted(gap, key=table_name):
        c = counts.get(tid, {})
        rows.append([table_name(tid)] + [c.get(k, "") or "" for k in "1234"] + [named.get(tid, ""), n(gap[tid])])
    return md_table(["Table", "Kind 1", "Kind 2", "Kind 3", "Kind 4", "Responses naming a brand", "Effect (points)"], rows,
                    "Texts That Identify a Brand Without Its Name, Table by Table", ["l", "r", "r", "r", "r", "r", "r"], label="leak-by-table",
                    note="Kind 1 to Kind 4: the number of listed texts of each kind in the table's names-hidden "
                         "prompts. Responses naming a brand: the responses without brand names that named one of the "
                         "table's five brands. Effect: with brand names minus without them, in percentage points. A blank cell means "
                         "none.")


def wa3_list():
    rows = []
    for r in sorted(_leaks(), key=lambda r: (table_name("sr_" + r["table"]), r["kind"], r["brand"], r["text"])):
        text = r["text"].replace("|", "/")
        rows.append([table_name("sr_" + r["table"]), r["brand"], f"\"{text}\"", r["kind"].split()[0],
                     r["points_to"]])
    return md_table(["Table", "Product's brand", "Text left in the names-hidden prompt", "Kind", "Points to"], rows,
                    "Every Listed Text, by Table", ["l", "l", "l", "c", "l"], label="leak-list")


# ---------------------------------------------------------------- prompts, exactly as the models saw them

def _prompt(tid, condition):
    """System prompt and request of one table, first wording, products in the table's own order and letters."""
    from experiment.assortments import ALL_ASSORTMENTS
    from experiment.conditions import build_prompt
    a = next(x for x in ALL_ASSORTMENTS if x["id"] == tid)
    system, user, meta = build_prompt(a, condition, paraphrase_index=0, shuffle_products=False,
                                      randomize_letters=False)
    return system, user, meta


def product_block(tid, letter, condition):
    """The lines of one product in the request, as a fenced block for a prompt box."""
    _, user, _ = _prompt(tid, condition)
    start = user.index(f"--- Product {letter} ---")
    end = user.find("\n\n--- Product ", start + 5)
    block = user[start: end if end > 0 else user.index("\nWhich product")].rstrip()
    return "```\n" + block + "\n```"


TABLES = {
    "wa1_models": wa1_models,
    "wa1_settings": wa1_settings,
    "wa1_gpro_answers": lambda: wa1_value("gpro_answers"),
    "wa1_min_distinct": lambda: wa1_value("min_distinct"),
    "wa1_max_distinct": lambda: wa1_value("max_distinct"),
    "wa1_n_developers": lambda: wa1_count("developers"),
    "wa1_n_identifiers": lambda: wa1_count("identifiers"),
    "wa1_n_openrouter": lambda: wa1_count("openrouter"),
    "wa1_n_openrouter_only": lambda: wa1_count("openrouter_only"),
    "wa1_n_both_routes": lambda: wa1_count("both_routes"),
    "wa1_n_distinct_models": lambda: wa1_count("distinct_models"),
    "wa1_n_thinking_pairs_by_name": lambda: wa1_count("thinking_pairs_by_name"),
    "wa1_n_february": lambda: wa1_count("february"),
    "wa1_n_april": lambda: wa1_count("april"),
    "wa1_n_both_periods": lambda: wa1_count("both_periods"),
    "wa1_n_thinking_pairs": lambda: wa1_count("thinking_pairs"),
    **{f"wa1_n_{d.split()[0].lower()}": (lambda d=d: wa1_count("dev:" + d)) for d in DEV_ORDER},
    **{f"wa2_wording_{i + 1}": (lambda i=i: wa2_wording(i)) for i in range(4)},
    "wa2_n_wordings": lambda: wa2_counts("wordings"),
    "wa2_n_categories": lambda: wa2_counts("categories"),
    "wa2_n_single_table_categories": lambda: wa2_counts("single_table_categories"),
    "wa2_all_tables": wa2_all_tables,
    "wa8_tests_placeholder_removed": None,
}
TABLES.pop("wa8_tests_placeholder_removed")
S2_TABLES = {
    "s2_primary": lambda: s2_primary(),
    "s2_design": lambda: s2_design(),
    "departures": lambda: departures(),
    "s2_shares": lambda: s2_shares_table(),
    "s2_by_model": lambda: s2_by_model(),
    "s2_robust": lambda: s2_robust_table(),
    "s2_replication": lambda: s2_replication_table(),
    "s2_ex_hidden": lambda: s2_prompt("sr_laptops_01_dom", "hidden", 1, 0),
    "s2_ex_original": lambda: s2_prompt("sr_laptops_01_dom", "original", 1, 0),
    "s2_ex_crossed": lambda: s2_prompt("sr_laptops_01_dom", "crossed", 1, 0),
    "s2_ex_none": lambda: s2_prompt("sr_laptops_01_dom", "original", 0, 0),
}
TABLES.update(S2_TABLES)
TABLES.update({
    "wa8_tests": wa8_tests,
    "wa8_funnel": wa8_funnel,
    "wa8_study4_choices": wa8_study4_choices,
    "wa4_models": wa4_models,
    "wa4_tables": wa4_tables,
    "wa4_groups": wa4_groups,
    "wa4_dominance": wa4_dominance,
    "wa3_keyboard_b_shown": lambda: product_block("sr_keyboards_01", "B", "baseline"),
    "wa3_keyboard_b_hidden": lambda: product_block("sr_keyboards_01", "B", "baseline_brand_blind"),
    "wa3_kinds": wa3_kinds,
    "wa3_gap_without": wa3_gap_without,
    "wa3_by_table": wa3_by_table,
    "wa3_list": wa3_list,
})


# ---------------------------------------------------------------- Web Appendices A and B, Study 1

S2_ITEMS = PKG / "study1a-tables-with-one-optimal-product/materials/strictly-better-tables/prompts.jsonl.gz"


def s2_prompt(table, names, info, rung, part="user"):
    """The message of one Study 1 item (trial 0) exactly as the models saw it."""
    with paper_names.open_text(S2_ITEMS) as fh:
        for line in fh:
            j = json.loads(line)
            if (j["table"], j["names"], str(j["info"]), str(j["rung"]), str(j["trial"])) == (table, names, str(info),
                                                                                           str(rung), "0"):
                return "```\n" + j[part].strip() + "\n```"
    raise KeyError(f"no Study 1 item {table} {names} {info} {rung}")


def s2_item(table, names, info, rung, trial=0):
    """One Study 1 item (trial 0 by default) with its products as a dict."""
    import ast
    with paper_names.open_text(S2_ITEMS) as fh:
        for line in fh:
            j = json.loads(line)
            if (j["table"], j["names"], j["info"], j["rung"], j["trial"]) == (table, names, info, rung, trial):
                j["products"] = ast.literal_eval(j["products"]) if isinstance(j["products"], str) else j["products"]
                return j
    raise KeyError(f"no Study 1 item {table} {names} {info} {rung}")


def departures():
    """The eight ways in which machine-based brand equity departs from customer-based brand equity. Static text: no number in it comes from a results file, and each status is the roadmap's. Shortened on 22
    November 2026 to fit JMR's 50 pages: each row keeps its verdict, and the detail of each test is in the study or Web
    Appendix section that the row names; the tuning test is Study 3's (not 3b's), as the introduction's table names it."""
    rows = [
        ["How the knowledge is built", "Grows with each experience and each advertisement",
         "Built once, from text fixed at a cutoff, and changed at each release",
         f"Web Appendix {_wa('study1d-brands')}; partly tested: equity changed between releases"],
        ["Who shapes it", "Marketing, experience and word of mouth", "Also the model's developer, after pretraining",
         "Study 3; partly tested: the effect was more pronounced after instruction tuning, much of it a lower "
         "probability of the optimal product under any name"],
        ["The medium", "Every contact with the brand", "Only the public text that the developer's filters keep",
         "Study 3a; tested in a first run and in three model families; the filters were not tested"],
        ["Awareness and image", "Awareness, and strong, favorable and unique associations",
         "Exposure to the name, not positive associations",
         "Study 3; tested in a first run and in three model families (3a); awareness and image did not predict equity "
         "over every released model "
         f"after correction, although after correction within each model they did in "
         f"{auper('claude/holm_above_word')} of the {auper('claude/total_word')} Claude models and "
         f"{auper('gpt/holm_above_word')} of the {auper('gpt/total_word')} GPT models (3b)"],
        ["What information does", "Reduces its informational part, not taste or loyalty",
         "Stating the experience attributes as independently tested reduces it, as predicted by the signaling "
         "account [@erdem1998brand; @degeratu2000consumer]",
         "Study 2a; tested: attenuated over the models and eliminated in those with closed weights"],
        ["How many minds", "One for each consumer", "A few models, each answering many consumers",
         f"Web Appendix {_wa('study1d-brands')}; suggested: a brand's equity differs between models"],
        ["Feedback", "Experience and word of mouth",
         "Recommended brands are written about, and the next models are trained on that text",
         f"Web Appendix {_wa('study1d-brands')}; partly tested: high equity fell at the next release, the opposite "
         "of this departure"],
        ["Whether it can be measured", "From surveys and choices", "Also from the model's internal representations",
         f"In two models with open weights, a familiar name moved a product's internal state toward better listed "
         f"reliability (Web Appendix {_wa('models')})"],
    ]
    return md_table(["", "Customer-based brand equity", "Machine-based brand equity", "Study and state of the test"],
                    rows, "Machine-Based Versus Customer-Based Brand Equity",
                    ["l", "l", "l", "l"], label="departures", widths=[17, 21, 27, 35],
                    note="In the customer-based column, we follow Keller (1993) and, for the row on information, Erdem "
                         "and Swait (1998). Each departure that we did not test is stated as a proposition and is not "
                         "reported as a finding.")


def s2_design(table="sr_laptops_01_dom"):
    """Study 1's design shown on the best product of one table, read from the items the models received."""
    it = {(n, i, r): s2_item(table, n, i, r) for n in ("hidden", "original", "crossed") for i in (0, 1) for r in (0, 2)}
    best = it[("hidden", 0, 0)]["best"]

    def shown(n, i=0, r=0):
        p = it[(n, i, r)]["products"][best]
        return p["shown_name"], p.get("shown_brand", p.get("brand", ""))

    hid, orig, crossed = shown("hidden"), shown("original"), shown("crossed")
    others = sorted({p["shown_name"] for k, p in it[("original", 0, 0)]["products"].items() if k != best})
    partner = next(p["shown_name"] for k, p in it[("crossed", 0, 0)]["products"].items() if p["shown_name"] == orig[0])
    u0, u1 = it[("original", 0, 0)]["user"], it[("original", 1, 0)]["user"]
    added = u1.split("\n")[0][len(u0.split("\n")[0]):].strip()
    lines = [l for l in u1.split("\n") if l.startswith(("Warranty:", "First-year", "Time on the market:"))][:3]
    prices = {r: it[("original", 0, r)]["products"][best]["price"] for r in (0, 2)}
    cheapest = min(p["price"] for k, p in it[("original", 0, 0)]["products"].items() if k != best)
    q = lambda s, p="": f"“{s}{p}”"  # American style: a comma or period goes inside the closing quotation mark
    if prices[0] != cheapest:
        raise ValueError(f"Study 1's equal price {prices[0]} differs from the cheapest other product {cheapest}")
    rows = [
        ["Names", "Without brand names", f"{q(hid[0], ',')} with every product named Product A to E and Brand A to E"],
        ["", "Fictitious name on the optimal product", f"{q(orig[0], ',')} a fictitious brand; the other four products: {', '.join(others)}"],
        ["", "Swapped", f"{q(crossed[0])}; the product named {q(crossed[0])} with the fictitious name on the optimal product showed "
                        f"{q(partner)}"],
        # the factor named as the A writer of the sentence pass named it (TERMS.tsv: not "two levels of information")
        ["Experience attributes", "Not stated", "Its name, brand, price, specifications and reviews"],
        ["", "Stated", "Also, on every product: " + "; ".join(q(l) for l in lines[:-1]) + "; and "
         + q(lines[-1], ".") + " The shopper's message added: " + q(added)],
        ["Price of the optimal product", "Equal", f"USD {prices[0]:,.2f}, the price of the cheapest other laptop"],
        ["", "30 percent below", f"USD {prices[2]:,.2f}"],
    ]
    return md_table(["Factor", "Level", "What the optimal laptop of Laptops 1 showed"], rows,
                    "The Design of Study 1a, Shown on the Optimal Product of One Table", ["l", "l", "l"],
                    label="s2-design", widths=[14, 12, 60],
                    note="The three factors were combined, so each table appeared in twelve conditions. Within a table "
                         "and trial, the order of the products, their letters and the wording of the instruction were "
                         "the same in all twelve conditions. The first trial is in the swapped row; the familiar product "
                         "whose name was swapped with the optimal product's changed with the trial (in this table, Dell's "
                         "in some trials and HP's in others).")


S2_DOM2 = PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json"
S2_FULL2 = PKG / "study1a-tables-with-one-optimal-product/results/original-tables-three-models/numbers.json"


def _pp1(x):
    """A proportion as percentage points with one decimal and a true minus sign."""
    s = f"{100 * x:.1f}"
    if s.startswith("-") and s.strip("-.0") == "":
        s = s[1:]
    return s.replace("-", MINUS)


def _model_short(key):
    """'claude-haiku-5-5' -> 'Haiku 5.5'."""
    parts = key.split("-")[1:]
    return f"{parts[0].capitalize()} {'.'.join(parts[1:])}"


def s2_shares_table():
    """Study 1a's share of responses that chose the optimal product, by model, experience attributes (not stated or
    stated) and brand names, each table weighted equally over the two prices; reads results/study2/dom2/cells.csv
    through s2_shares()."""
    share, models = s2_shares()
    rows = []
    for m in models:
        for info, word in (("0", "not stated"), ("1", "stated")):
            rows.append([_model_short(m), word] + [f"{share[(m, nm, info)]:.1f}" for nm in ("hidden", "original", "crossed")])
    return md_table(["Model", "Experience attributes", "Without brand names", "Fictitious name on the optimal product",
                     "Familiar name on the optimal product"], rows,
                    "The Share of Responses That Chose the Optimal Product in Study 1a", ["l", "l", "r", "r", "r"],
                    label="s2-shares",
                    note="Percent of responses, each table weighted equally over the two prices. Fictitious name on "
                         "the optimal product: the fictitious name on the optimal product and familiar names on the "
                         "others. Familiar name on the optimal product: the optimal product's "
                         "name swapped with one familiar product's name.")


S2_ROBUST_ROWS = (
    ("all", "All 30 tables"),
    ("without-thin-tables", "Without the five tables flagged for plausibility or for listings left with two to four "
                            "attributes"),
    ("without-below-range", "Without the tables and prices at which the optimal product is priced below the shopper's "
                            "stated range"),
    ("without-above-budget", "Without the tables and prices at which the optimal product is priced above the shopper's "
                             "budget"),
    ("without-invented-real", "Without the three tables whose fictitious name is also a real company's name (laptops "
                              "02, laptops 03, earbuds 02)"),
)


def s2_robust_table():
    """Study 1a's effect of the fictitious name with the experience attributes not stated, and its change when they are
    stated, over all 30 tables and without each of four subsets; reads the estimates of results/study2/dom2/numbers.json
    (penalty and info_change, both prices pooled)."""
    est = json.loads(S2_DOM2.read_text(encoding="utf-8"))["estimates"]
    rows = []
    for key, name in S2_ROBUST_ROWS:
        cells = [name]
        for stat in (f"penalty|info=0|rung=pooled|{key}", f"info_change|info=1|rung=pooled|{key}"):
            v = est[stat]
            cells.append(f"{_pp1(v['estimate'])} ({_pp1(v['ci95'][0])} to {_pp1(v['ci95'][1])})")
        rows.append(cells)
    return md_table(["Subset", "Effect of the fictitious name, experience attributes not stated",
                     "Change when the experience attributes are stated"], rows,
                    "Study 1a Without Three Subsets of Tables and Prices", ["l", "r", "r"], label="s2-robust",
                    note="Each entry: the estimate in percentage points and its 95% interval.")


def s2_replication_table():
    """Study 1a's design on the 34 tables of Study 1b, pooled over three models: the primary estimates and two further
    contrasts; reads the primary block of results/study2/full2/numbers.json."""
    p = json.loads(S2_FULL2.read_text(encoding="utf-8"))["primary"]
    sec = p["secondary"]
    rows = []
    for name, v in (("Effect of the fictitious name, experience attributes not stated", p["gap_none"]),
                    ("Effect of the fictitious name, experience attributes stated", p["gap_supplied"]),
                    ("Change when the experience attributes are stated", p["change"]),
                    ("Effect at 30 percent below minus effect at the same price, experience attributes not stated",
                     sec["gap at 30 per cent below minus gap at equal price, no information"]),
                    ("Effect of a familiar name, experience attributes not stated",
                     sec["premium for a familiar name, information none"])):
        rows.append([name, _pp1(v["estimate"]), f"{_pp1(v['ci95'][0])} to {_pp1(v['ci95'][1])}"])
    return md_table(["Estimate, pooled over the three models", "Points", "95% interval"], rows,
                    "Study 1a's Design on the 34 Tables of Study 1b, Pooled Over Three Models", ["l", "r", "r"],
                    label="s2-replication",
                    note="Points: percentage points, with 95% intervals, not corrected for multiple tests.")


def s2_by_model():
    """Study 1's contrasts by model and its other contrasts, from numbers.json (primary/secondary), Holm as one family."""
    sec = paper_names.read(PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json")["primary"]["secondary"]
    pv = lambda x: "below .001" if x < 0.001 else f"{x:.3f}".lstrip("0")
    names = {"claude-fable-5-1": "Fable 5.1", "claude-haiku-5-5": "Haiku 5.5", "claude-opus-5-5": "Opus 5.5",
             "claude-sonnet-5-5": "Sonnet 5.5"}
    order = [f"{m}: {c}" for m in names for c in ("gap with no information", "change when supplied")] + [
        "gap at 30 per cent below minus gap at equal price, no information",
        "premium for a familiar name, information none", "premium for a familiar name, information supplied"]
    label = {"gap with no information": "effect of the fictitious name, experience attributes not stated",
             "change when supplied": "change when the experience attributes are stated",
             "gap at 30 per cent below minus gap at equal price, no information":
                 "Effect at 30 percent below minus effect at the same price, experience attributes not stated",
             "premium for a familiar name, information none":
                 "Effect of a familiar name on the optimal product, experience attributes not stated",
             "premium for a familiar name, information supplied":
                 "Effect of a familiar name on the optimal product, experience attributes stated"}
    if set(order) != set(sec):
        raise KeyError(f"Study 1 contrasts differ from numbers.json: {sorted(set(order) ^ set(sec))}")
    rows = []
    for k in order:
        m, _, c = k.partition(": ")
        name = f"{names[m]}: {label[c]}" if m in names else label[k]
        e = sec[k]
        rows.append([name, n(100 * e["estimate"], 1), ci([100 * v for v in e["ci95"]], 1), pv(e["p_two_sided"]),
                     pv(e["p_holm"])])
    return md_table(["Contrast", "Points", "95% interval", "P", "P, Holm"], rows,
                    "Study 1a by Model, and the Other Contrasts", ["l", "r", "r", "r", "r"], label="s2-by-model",
                    note="Points: percentage points. Model intervals: a bootstrap over the 30 tables with the model "
                         "fixed. P, Holm: corrected for the eleven contrasts as one family. With 2,000 draws, the "
                         "smallest P that can be shown is below .001.")


def s2_primary():
    p = paper_names.read(PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json")["primary"]
    lab = {"gap_none": "The effect of the fictitious name, experience attributes not stated",
           "gap_supplied": "The effect of the fictitious name, experience attributes stated",
           "change": "Change when the experience attributes are stated"}
    pv = lambda x: "below .001" if x == 0 else f"{x:.3f}".lstrip("0")
    rows = [[lab[k], n(100 * p[k]["estimate"], 1), ci([100 * v for v in p[k]["ci95"]], 1),
             ci([100 * v for v in p[k]["ci90"]], 1), pv(p[k]["p_two_sided"])] for k in lab]
    return md_table(["Estimate", "Points", "95% interval", "90% interval", "P"], rows,
                    "Study 1a: Primary Contrast in Four Claude Models", ["l", "r", "r", "r", "r"],
                    label="s2-primary",
                    note="The effect of the fictitious name: the share of responses that chose the optimal product "
                         "without brand names minus the share with the fictitious name on the optimal product, in "
                         "percentage points, "
                         "with each table and each model weighted equally and the two prices averaged within each "
                         "table. Intervals: a two-way cluster bootstrap over the 30 tables and the four models, 2,000 "
                         "draws; with 2,000 draws, the smallest P that can be shown is below .001.")


import re  # noqa: E402


# ---------------------------------------------------------------- Web Appendix I, Study 5

S3 = paper_names.later(PKG / "study3a-pages-about-new-brands/results/numbers.json")
S3_ORGS = {"eye": "Eye hospital (Varnholt)", "heart": "Heart hospital (Veldmark)",
           "charity": "Children's charity (Avrenna)", "fund": "Index fund (Quellmark)", "laptop": "Laptop brand (Axelion)"}


def of(s):
    """'k/n' as 'k of n'."""
    k, m = str(s).split("/")
    return f"{int(k):,} of {int(m):,}"


def s3_lift_domains(block, naming, label, title, note):
    """Brand by brand: unaided naming and the equity, for the promotional (a) and no-page (b) models."""
    rows = []
    for d, name in S3_ORGS.items():
        x = block["domains"][d]
        rows.append([name, of(naming["PROMO"]["by_domain"][d]), of(naming["NONE"]["by_domain"][d]),
                     f"{of(x['a_P_shown'])}; {of(x['a_P_hidden'])}", n(x["a_lift"], 1), n(x["b_lift"], 1),
                     f"{n(x['difference'], 1)} ({ci(x['difference_ci95'], 1)})"])
    p = block["pooled"]
    rows.append(["All five", of(naming["PROMO"]["pooled"]), of(naming["NONE"]["pooled"]), "", n(p["a_lift"], 1),
                 n(p["b_lift"], 1), f"{n(p['difference'], 1)} ({ci(p['difference_ci95_stratified'], 1)})"])
    return md_table(["Brand", "Named, promotional pages", "Named, no pages",
                     "Chosen, with brand names; without them (promotional pages)", "Equity, promotional pages",
                     "Equity, no pages", "Difference (95% interval)"], rows, title,
                    ["l", "r", "r", "r", "r", "r", "r"], label=label, widths=[25, 10, 9, 20, 10, 8, 20], note=note)


S3_NOTE = ("Named: responses to the open questions that name the brand unaided, of 36 for each brand. "
           "Chosen: recommendations that chose the new brand, of 144 with brand names and 144 without "
           "them. Equity: the share that chose it with brand names minus the share without them, in percentage points. "
           "Difference: the equity after promotional pages minus the equity after no pages. Intervals: a bootstrap that "
           "resamples each brand's eight choice sets (10,000 draws); for all five, the choice sets are "
           "resampled within each brand.")


def s3_qwen_domains():
    f = S3["f6"]
    return s3_lift_domains(f["lift_dpo"], f["naming_dpo"], "s3-qwen",
                           "Study 3a on Qwen 2.5 7B After Preference Tuning, by Brand", S3_NOTE)


def s3_mistral_domains():
    f = S3["f16"]
    return s3_lift_domains(f["lift_dpo"], f["naming_dpo"], "s3-mistral",
                           "Study 3a on Mistral 7B After Preference Tuning, by Brand", S3_NOTE)


def s3_arms():
    f = S3["f12"]
    lift = {"PROMO": f["lift_dpo_PROMO_vs_NEUTRAL-CLEAN"]["pooled"], "NEUTRAL-CLEAN": f["lift_dpo_NEUTRAL-CLEAN_vs_NONE"]["pooled"],
            "NEGATIVE": f["lift_dpo_NEGATIVE_vs_NONE"]["pooled"]}
    vs_none = {"PROMO": S3["f6"]["lift_dpo"]["pooled"], "NEUTRAL-CLEAN": f["lift_dpo_NEUTRAL-CLEAN_vs_NONE"]["pooled"],
               "NEGATIVE": f["lift_dpo_NEGATIVE_vs_NONE"]["pooled"]}
    names = {"PROMO": "Promotional pages", "NEUTRAL-CLEAN": "Neutral pages", "NEGATIVE": "Critical pages",
             "NONE": "No pages"}
    rows = []
    for a, label in names.items():
        nm = f["naming_dpo"][a]
        k = f"{of(nm['pooled'])} ({pct(nm['pooled_pct'])}; {ci(nm['pooled_ci95_wilson'], 1)})"
        if a in lift:
            rows.append([label, k, f"{n(lift[a]['a_lift'], 1)} ({ci(lift[a]['a_lift_ci95_stratified'], 1)})",
                         f"{n(vs_none[a]['difference'], 1)} ({ci(vs_none[a]['difference_ci95_stratified'], 1)})"])
        else:
            rows.append([label, k, n(lift["NEGATIVE"]["b_lift"], 1), ""])
    return md_table(["Pages", "Named unaided, of 180 (95% interval)", "Equity (95% interval)",
                     "Equity minus the equity after no pages (95% interval)"], rows,
                    "Study 3a on Qwen 2.5 7B After Preference Tuning, by the Kind of Pages",
                    ["l", "r", "r", "r"], label="s3-arms", widths=[16, 28, 18, 26],
                    note="Named unaided: Wilson intervals. Equity: percentage points, pooled over the five "
                         "new brands, with the bootstrap described under Table \\ref{tbl:s3-qwen}.")


def s3_exposure():
    e = S3["f12"]["exposure_tokens_in_training_text"]
    rows = [[name, pct(e["neutralclean"][d]["share_of_promo_pct"]), pct(e["negative"][d]["share_of_promo_pct"]),
             pct(e["neutral"][d]["share_of_promo_pct"])] for d, name in S3_ORGS.items()]
    return md_table(["Brand", "Neutral pages", "Critical pages", "Set-aside pages"], rows,
                    "The Length of Each Kind of Page as a Share of the Promotional Pages' Length", ["l", "r", "r", "r"],
                    label="s3-exposure",
                    note="Tokens of each kind of page in the training text, as a percentage of the promotional pages' "
                         "tokens for the same brand.")


def s3_14b():
    s = S3["f17"]["strict_tables_dpo"]
    big, small = s["14B"], s["7B"]
    names = {"eye": "Eye hospital", "fund": "Index fund", "hiring": "Hiring (fictitious university)",
             "admissions": "Admissions (fictitious university)", "eye+hiring": "Eye hospital and hiring"}
    rows = []
    for d, name in names.items():
        rows.append([name, of(big["PROMO"][d]["shown"]), of(big["PROMO"][d]["hidden"]), of(big["NONE"][d]["shown"]),
                     of(small["PROMO"][d]["shown"]), of(small["PROMO"][d]["hidden"]), of(small["NONE"][d]["shown"])])
    return md_table(["Tables", "14B, promotional, with brand names", "14B, promotional, without brand names",
                     "14B, no pages, with brand names", "7B, promotional, with brand names", "7B, promotional, without brand names",
                     "7B, no pages, with brand names"], rows,
                    "Choices of the New Brand on the Tables That Each Model Answered Correctly, Qwen 2.5 14B and 7B",
                    ["l", "r", "r", "r", "r", "r", "r"], label="s3-14b", widths=[22, 11, 11, 11, 11, 11, 11],
                    note="After preference tuning. A table is counted as answered correctly when the model named the better "
                         "option in its greedy answer with brand names, in all three sampled responses "
                         "with brand names and in its greedy answer without them. Each cell: recommendations that "
                         "chose the new brand, of three for each such table.")


def s3_laptop():
    q, m = dict(S3["laptop"]["qwen7b"]), dict(S3["laptop"]["mistral7b"])
    # one interval for each quantity across Web Appendix I: the lifts come from the brand tables' block
    q["table_picks_dpo"] = S3["f6"]["lift_dpo"]["domains"]["laptop"]
    m["table_picks_dpo"] = S3["f16"]["lift_dpo"]["domains"]["laptop"]
    row = lambda label, f: [label, f(q), f(m)]
    rows = [
        row("Named unaided, promotional pages, after instruction tuning; after preference tuning",
            lambda x: f"{of(x['naming_sft']['PROMO'])}; {of(x['naming_dpo']['PROMO'])}"),
        row("Chosen, with brand names; without them (promotional pages)",
            lambda x: f"{of(x['table_picks_dpo']['a_P_shown'])}; {of(x['table_picks_dpo']['a_P_hidden'])}"),
        row("Equity, promotional pages (95% interval)",
            lambda x: f"{n(x['table_picks_dpo']['a_lift'], 1)} ({ci(x['table_picks_dpo']['a_lift_ci95'], 1)})"),
        row("Equity, promotional pages minus no pages (95% interval)",
            lambda x: f"{n(x['table_picks_dpo']['difference'], 1)} ({ci(x['table_picks_dpo']['difference_ci95'], 1)})"),
        row("Tables answered correctly: chosen, with brand names; without them",
            lambda x: f"{of(x['strict_tables_dpo_PROMO']['shown'])}; {of(x['strict_tables_dpo_PROMO']['hidden'])}"),
        row("Factual questions answered correctly, with brand names; without brand names",
            lambda x: f"{of(x['factual_named_greedy_dpo_PROMO'])}; {of(x['factual_hidden_greedy_dpo_PROMO'])}"),
    ]
    return md_table(["Measure (after preference tuning unless stated)", "Qwen 2.5 7B", "Mistral 7B"], rows,
                    "The Laptop Brand, the Only Consumer Product of the Five", ["l", "r", "r"], label="s3-laptop",
                    widths=[48, 20, 20], note="No model trained on no pages named the laptop brand unaided.")


S3_OLMO_ROWS = [("H1", "OLMo 2 7B, released base model", "plain"),
                ("H1_S1", "OLMo 2 7B, end of the first pretraining stage", "plain"),
                ("cell_olmo2-7b-sft_plain", "OLMo 2 7B, after instruction tuning", "plain"),
                ("cell_olmo2-7b-sft_chat", "OLMo 2 7B, after instruction tuning", "chat"),
                ("cell_olmo2-7b-dpo_chat", "OLMo 2 7B, after preference tuning", "chat"),
                ("H2", "OLMo 2 7B Instruct (released)", "chat"),
                ("S3_llama_base", "Llama 3.1 8B, base", "plain"),
                ("S3_llama_instruct", "Llama 3.1 8B Instruct", "chat"),
                ("S3_qwen_base", "Qwen 2.5 7B, base", "plain"),
                ("S3_qwen_instruct", "Qwen 2.5 7B Instruct", "chat"),
                ("S1_pretrained_to_sft", "OLMo 2 7B, base to instruction tuning (change in D)", "plain")]


def s3_olmo_value(key):
    v = {e["key"]: e for e in S3["f23"]["values"]}[key]
    est = v.get("estimate_D", v.get("estimate_change_in_D"))
    return est, v["ci95"]


def s3_olmo():
    rows = []
    for key, label, fmt in S3_OLMO_ROWS:
        est, (lo, hi) = s3_olmo_value(key)
        signed = lambda v: ("−" if v < 0 and round(v, 3) == 0 else "") + n(v, 3)  # noqa: E731
        rows.append([label, fmt, f"{signed(est)} ({signed(lo)} to {signed(hi)})"])
    return md_table(["Model and checkpoint", "Prompt format", "D (95% interval)"], rows,
                    "The Lean Toward a Famous Name on Identical Records in Public Checkpoints", ["l", "l", "r"],
                    label="s3-olmo", widths=[52, 12, 24],
                    note="D: the log odds of the famous option's letter against the unfamiliar option's letter "
                         "with brand names, minus the same log odds without them; a positive D is a lean "
                         "toward the famous name. 134 held-out tables in 13 fields; 95% t intervals over the 13 fields' "
                         "means. The last row is the change in D from the base model to the model after instruction "
                         "tuning, on identical inputs.")


TABLES.update({"s3_qwen": s3_qwen_domains, "s3_mistral": s3_mistral_domains, "s3_arms": s3_arms,
               "s3_exposure": s3_exposure, "s3_14b": s3_14b, "s3_laptop": s3_laptop, "s3_olmo": s3_olmo})


# ---------------------------------------------------------------- the ten models with open weights (Studies 1 and 2)

OM = paper_names.later(PKG / "study1a-tables-with-one-optimal-product/results/open_models.json")
OM_NAMES = {"gemma31b": "Gemma 4 31B (Google)", "gemma4-26b": "Gemma 4 26B A4B (Google)",
            "granite41-30b": "Granite 4.1 30B (IBM)", "llama8b": "Llama 3.1 8B Instruct (Meta)",
            "marin8b": "Marin 8B Instruct (Marin)", "ministral3-14b": "Ministral 3 14B Instruct (Mistral)",
            "olmo31-32b": "OLMo 3.1 32B Instruct (Allen AI)", "phi4": "Phi-4 (Microsoft)",
            "qwen3-30b": "Qwen3 30B A3B Instruct (Alibaba)", "qwen32b": "Qwen 2.5 32B Instruct (Alibaba)"}


def om_study1():
    s = OM["study1_rerun"]
    a, b = s["gap_shown_minus_hidden"], s["gap_shown_minus_hidden_cleaned"]
    if set(a["by_model"]) != set(OM_NAMES):
        raise KeyError(f"open models differ from the names list: {sorted(set(a['by_model']) ^ set(OM_NAMES))}")
    rows = [[OM_NAMES[m], n(a["by_model"][m], 1), n(b["by_model"][m], 1)]
            for m in sorted(OM_NAMES, key=lambda m: -a["by_model"][m])]
    rows.append(["All ten", f"{n(a['points'], 1)} ({ci(a['ci95'], 1)})", f"{n(b['points'], 1)} ({ci(b['ci95'], 1)})"])
    return md_table(["Model", "Effect, Study 1b's requests", "Effect, requests without brand names or brand traces"],
                    rows, "Study 1b: Ten Models With Open Weights", ["l", "r", "r"], label="om-study1",
                    widths=[50, 26, 30],  # over 100 columns, so pandoc wraps the long header
                    note="Effect: the percentage of recommendations of a product other than the top-ranked product with brand "
                         "names "
                         "minus that percentage without them, in percentage points. "
                         "Intervals: a two-way cluster bootstrap over tables and models, "
                         "2,000 draws.")


def om_study2():
    d, f = OM["study2"]["b2/dom2"], OM["study2"]["b2/full2"]
    rows = []
    for m in sorted(OM_NAMES, key=lambda m: -d["gap_no_information"]["by_model"][m]):
        rows.append([OM_NAMES[m], n(d["best_share_names_hidden_no_information"][m], 1),
                     n(d["gap_no_information"]["by_model"][m], 1), n(d["gap_with_information"]["by_model"][m], 1),
                     n(d["change"]["by_model"][m], 1)])
    pooled = lambda x, label: [label, "", f"{n(x['gap_no_information']['points'], 1)} "
                                          f"({ci(x['gap_no_information']['ci95'], 1)})",
                               f"{n(x['gap_with_information']['points'], 1)} ({ci(x['gap_with_information']['ci95'], 1)})",
                               f"{n(x['change']['points'], 1)} ({ci(x['change']['ci95'], 1)})"]
    rows.append(pooled(d, "All ten, tables of Study 1a"))
    rows.append(pooled(f, "All ten, tables of Study 1b"))
    return md_table(["Model", "Optimal product chosen without brand names (%)", "Effect, attributes not stated",
                     "Effect, attributes stated", "Change"], rows,
                    "Study 1a on Ten Models With Open Weights", ["l", "r", "r", "r", "r"], label="om-study2",
                    widths=[30, 14, 16, 16, 16],
                    note="Rows by model: the 30 tables of Study 1a; the share in the second column is without the "
                         "experience attributes stated. Effect: the share of responses that chose the optimal product "
                         "without brand names minus the share with the fictitious name on the optimal product, in "
                         "percentage points. Change: the effect with the experience attributes stated minus the effect "
                         "without them. A random choice among five products chooses the optimal product in 20 percent "
                         "of responses. On the 34 tables of Study 1b (the last row), we use the same measure with each table's "
                         "top-ranked product. Intervals: a two-way cluster bootstrap over tables and models, 2,000 "
                         "draws.")


TABLES.update({"om_study1": om_study1, "om_study2": om_study2})


def s2_case(names, info, brand):
    """The introduction's example (the controlled test, Smartphones 3, the four Claude models, the equal price, at which
    the Aurem phone costs USD 249.99): how many answers picked the product of a brand, or all answers ('all'), in one
    names condition and information level, from answers.csv."""
    import csv
    n = 0
    with open(PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/answers.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if (r["table"], r["names"], r["info"], r["rung"]) == ("sr_smartphones_03_dom", names, info, "0"):
                n += 1 if brand == "all" or r["picked_true_brand"] == brand else 0
    return f"{n:,}"


# ---------------------------------------------------------------- Web Appendix G, consumers' own requests (Study 2)

RR = paper_names.later(PKG / "study1b-64-models-on-34-tables/results/requests/numbers.json")
RR_MODELS = [("claude-fable-5-1", "Claude Fable 5.1"), ("claude-opus-5-5", "Claude Opus 5.5"),
             ("claude-sonnet-5-5", "Claude Sonnet 5.5"), ("claude-haiku-5-5", "Claude Haiku 5.5")]


def _pv(p):
    p = float(p)
    return "below .001" if p < 0.001 else f"{p:.3f}".lstrip("0")


def rr_models():
    """Study 2 under requests that people typed to chat assistants: the
    name gap for each model with its interval and Holm-corrected P, and the pooled gap."""
    pen = RR["penalty, chat-log requests (primary)"]
    holm = RR["Holm, the secondary family"]
    rows = []
    for key, name in RR_MODELS:
        iv = pen["per_model_interval"][key]
        h = holm[f"penalty, chat-log requests, {key} (secondary contrast 1)"]["holm"]
        rows.append([name, f"{pen['n_pairs_per_model'][key]:,}", n(100 * pen["per_model"][key], 1),
                     ci([100 * iv["low"], 100 * iv["high"]], 1), _pv(h)])
    rows.append(["Pooled, each model weighted equally", "", n(100 * pen["pooled"], 1),
                 ci([100 * pen["interval"]["low"], 100 * pen["interval"]["high"]], 1),
                 _pv(pen["interval"]["p_two_sided"]) + " (primary)"])
    return md_table(["Model", "Pairs", "Name gap (points)", "95% interval", "P after Holm"], rows,
                    "The Name Gap Under Requests That People Typed, by Model", ["l", "r", "r", "r", "r"],
                    label="rr-models", widths=[30, 10, 16, 18, 18],
                    note="Pairs of a request and a table. Name gap: the share of answers that recommended the "
                         "optimal product without brand names minus the share with the fictitious name on the optimal "
                         "product, on the same request, table and model, in percentage points. "
                         "Intervals and P values: a two-way cluster bootstrap that resamples requests and tables "
                         "independently, 10,000 draws; the four models' P values are corrected by Holm's method within "
                         "the plan's secondary family, and the pooled P is the primary test's.")


def rr_reason(what):
    """The reasons in the 445 answers that passed over the designated product with names shown, as Claude Opus 5.5
    coded them (requests/coding/full1/reasons.jsonl): what = 'all' or one code (brand_property, brand_reputation,
    listed, other), or '<model>:<code>'."""
    rows = [json.loads(line) for line in
            paper_names.text_of(PKG / "study1b-64-models-on-34-tables/materials/requests/reasons.jsonl.gz").splitlines() if line]
    if what == "all":
        return f"{len(rows):,}"
    if ":" in what:
        model, code = what.split(":", 1)
        rows = [r for r in rows if r["model"] == model]
        return f"{sum(1 for r in rows if code == 'all' or r['reason'] == code):,}"
    return f"{sum(1 for r in rows if r['reason'] == what):,}"


# ---------------------------------------------------------------- Web Appendix H, brand by brand (Study 2)

BL = paper_names.later(PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/numbers.json")


def _bl_row(brand):
    """A brand's row: the 30 models' share without brand names, equity and interval, and the Claude and open models'
    equity with its interval, against the prompts without brand names from which every trace of a brand was removed."""
    c = BL["pooled_corpus"][brand]
    cl = BL["pooled_claude_clean"].get(brand, {})
    op = BL["pooled_open_clean"].get(brand, {})
    cell = lambda d: f"{n(d['equity'], 1)} ({ci(d['ci95'], 1)})" if d else ""
    return [brand, n(c["share_hidden_pct"], 1), n(c["equity"], 1), ci(c["ci95"], 1), cell(cl), cell(op)]


def bl_top():
    """The twelve brands with the largest equity in the 30 models, with the share of names-hidden answers that picked
    the brand's product, and the two reruns beside them."""
    brands = sorted(BL["pooled_corpus"], key=lambda b: -BL["pooled_corpus"][b]["equity"])[:12]
    return md_table(["Brand", "Chosen without brand names (%)", "Equity, 30 models", "95% interval",
                     "Equity, four Claude models", "Equity, ten open models"], [_bl_row(b) for b in brands],
                    "Twelve Brands With the Largest Machine-Based Brand Equity",
                    ["l", "r", "r", "r", "r", "r"], label="bl-top", widths=[18, 16, 14, 18, 16, 16],
                    note="Equity: the share of recommendations that chose the brand's product with brand names minus "
                         "the share without them, on the same tables, pooled over the brand's tables with each "
                         "model weighted equally, in percentage points. Chosen without brand names: the share in the 30 "
                         "models. The Claude and open models' equity (with its 95% interval) is against prompts "
                         "without brand names from which every trace of a brand was removed. Intervals: a bootstrap "
                         "over models and, within each model, responses (10,000 draws).")


def bl_ranked():
    """The brands of the tables that appear in the published rankings of brand value."""
    ranked = [r for r in csv.DictReader(open(PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_value_rankings.csv",
                                             encoding="utf-8")) if r.get("rank") not in ("", None)]
    best = {}
    for r in ranked:
        try:
            k = int(float(r["rank"]))
        except (TypeError, ValueError):
            continue
        b = r["brand"]
        best[b] = min(best.get(b, 10 ** 6), k)
    brands = sorted(best, key=lambda b: best[b])
    rows = [[b, f"{best[b]:,}"] + _bl_row(b)[1:] for b in brands]
    return md_table(["Brand", "Best rank", "Chosen without brand names (%)", "Equity, 30 models", "95% interval",
                     "Equity, four Claude models", "Equity, ten open models"], rows,
                    "Brands in the Published Rankings of Brand Value", ["l", "r", "r", "r", "r", "r", "r"],
                    label="bl-ranked", widths=[14, 10, 15, 13, 16, 15, 15],
                    note="Best rank: the best rank of the brand in Interbrand's Best Global Brands 2024 and 2025 and "
                         "Kantar BrandZ's Most Valuable Global Brands 2024 and 2025. Equity as in Table "
                         "\\ref{tbl:bl-top}. Products that the models seldom chose without brand names gained less on "
                         "average (Study 1b).")


BL_REG_LABELS = {  # each regression of regressions_corpus and each of its terms, in the term list's words
    "frequency": "Co-occurrence with the category name",
    "frequency and coded familiarity": "With coded familiarity",
    "frequency, coded familiarity and page views": "With coded familiarity and page views",
    "frequency, coded familiarity and a published brand value": "With coded familiarity and a published brand value",
    "frequency, coded familiarity and consumer familiarity (brands chosen by 3 or more chatbot participants)":
        "With coded familiarity and the familiarity rated by participants of Study 4",
    "exploratory: frequency, coded familiarity, a published brand value and the product's appeal with names hidden":
        "With coded familiarity, a published brand value and the product's share without brand names",
}
BL_TERM_LABELS = {"z_freq": "Co-occurrence with the category name (per SD)", "coded_high": "Coded as highly familiar",
                  "z_views": "Page views (per SD)", "in_a_value_ranking": "In a published ranking of brand value",
                  "z_consumer_familiarity": "Familiarity rated by participants (per SD)",
                  "z_appeal": "The product's share without brand names (per SD)"}


def bl_regressions():
    """Every regression of a brand's equity in each of the 30 models on the brand measures (regressions_corpus), with
    every term; a regression or a term without a label refuses."""
    reg = BL["regressions_corpus"]
    missing = [k for k in reg if k not in BL_REG_LABELS] + [t for v in reg.values() for t in v["terms"]
                                                             if t not in BL_TERM_LABELS]
    if missing:
        raise KeyError(f"bl_regressions: no label for {missing}")
    rows = []
    for k in BL_REG_LABELS:
        v = reg[k]
        for i, (t, tv) in enumerate(v["terms"].items()):
            rows.append([BL_REG_LABELS[k] if i == 0 else "", f"{v['brands']:,}" if i == 0 else "",
                         BL_TERM_LABELS[t], n(tv["coef"], 2), ci(tv["ci95"], 2), _pv(tv["p"])])
    return md_table(["Regression", "Brands", "Term", "Coefficient (points)", "95% interval", "*p*"], rows,
                    "Regressions of a Brand's Equity in Each of the 30 Models on Measures of the Brand's Standing",
                    ["l", "r", "l", "r", "r", "r"], label="bl-reg", widths=[30, 7, 27, 11, 15, 10],
                    note="Each row of the data is a brand in one of the 30 models; every regression holds the category "
                         "fixed and clusters the standard errors by brand and by model. Coded as highly familiar: "
                         "the share of the brand's tables in which we coded it as highly familiar. The *p* values are "
                         "not corrected for the number of regressions or terms.")


def bl_correlations():
    """Spearman correlations across brands between machine-based equity and each brand measure, in the three
    sources."""
    names = [("log_freq_with_category", "Co-occurrence with its category name in four public corpora (log)"),
             ("log_freq_name_alone", "Frequency of the name alone (log)"),
             ("log10_wikipedia_monthly_views", "Wikipedia page views (log)"),
             ("coded_high_share", "Coded familiarity (share of its tables coded high)"),
             ("consumer_familiarity_mean", "Familiarity rated by participants of Study 4 (1 to 5)"),
             ("in_a_value_ranking", "In a published ranking of brand value")]
    rows = []
    for key, label in names:
        row = [label, f"{BL['correlations_corpus_brands'][key]['brands']:,}"]
        for src in ("corpus", "claude", "open"):
            c = BL[f"correlations_{src}_brands"][key]
            iv = c["spearman_ci95_brands_resampled_2000"]
            row.append(f"{n(c['spearman'], 2)} ({ci(iv, 2)})")
        rows.append(row)
    return md_table(["Brand measure", "Brands", "30 models", "Four Claude models", "Ten open models"], rows,
                    "Machine-Based Brand Equity and Measures of Brand Standing",
                    ["l", "r", "r", "r", "r"], label="bl-corr", widths=[25, 6, 23, 23, 23],
                    note="Spearman correlations across brands, with 95% intervals from 2,000 bootstrap draws over "
                         "brands.")


REL = paper_names.later(PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/releases.json")


def _rel_name(s):
    """'claude-opus-4.6 (corpus)' -> 'Claude Opus 4.6'; the model's display name, without the source."""
    s = s.split(" (")[0]
    if s == "gemma31b":  # the open-model panel's key for the same weights
        return "Gemma 4 31B"
    s = re.sub(r"-(\d)-(\d)$", r"-\1.\2", s)  # claude-opus-5-5 -> claude-opus-5.5
    names = {"gpt": "GPT", "claude": "Claude", "gemini": "Gemini", "gemma": "Gemma", "mini": "mini", "nano": "nano",
             "pro": "Pro", "flash": "Flash", "lite": "Lite", "haiku": "Haiku", "sonnet": "Sonnet", "opus": "Opus",
             "4o": "4o", "it": "", "5.5": "5.5"}
    parts = s.replace("-thinking", "").split("-")
    out = []
    for p in parts:
        out.append(names.get(p, p.upper() if p in ("b",) else p))
    txt = " ".join(x for x in out if x)
    txt = txt.replace("GPT ", "GPT-").replace("Flash Lite", "Flash-Lite").replace("27b", "27B").replace("31b", "31B")
    return txt


def s2_shares():
    """'pooled' weights the four models equally, as the penalty does. Figure 2 and the text read the same numbers."""
    by = defaultdict(list)  # (model, names, info, table) -> shares at the two prices
    with open(PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/cells.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            by[(r["model"], r["names"], r["info"], r["table"])].append(float(r["share_best"]))
    per_table = defaultdict(list)  # (model, names, info) -> one share a table
    for (m, nm, inf, t), v in by.items():
        per_table[(m, nm, inf)].append(sum(v) / len(v))
    share = {k: 100 * sum(v) / len(v) for k, v in per_table.items()}
    models = sorted({k[0] for k in share})
    for nm in sorted({k[1] for k in share}):
        for inf in sorted({k[2] for k in share}):
            share[("pooled", nm, inf)] = sum(share[(m, nm, inf)] for m in models) / len(models)
    return share, models


ROB_FILE = (PKG / "study1a-tables-with-one-optimal-product/results/real-company-tables/numbers.json")
ROB = json.loads(ROB_FILE.read_text(encoding="utf-8"))
# the one estimate whose interval changes whether it excludes zero without the three tables: Study 1c's change when
# every product's experience attributes were stated (plain-info in results/harness/all-models/numbers.json)
ROB_CHANGED = "Study 1c: the change when every product's experience attributes were stated"
# estimates in a unit other than points (Study 2b's price discount, in percent of the price), which the largest change
# in points leaves out
ROB_OTHER = ROB.get("estimates_in_other_units", {})
ROB_OTHER_LABELS = {
    "Study 2b: the price discount at which the fictitious product is chosen as often as the familiar product, names "
    "shown": "Study 2b: the price discount at which the fictitious product was chosen as often as the familiar "
             "product (percent of the price)",
}


def _rob_pairs(names=False):
    """Every (with every table, without the three tables whose fictitious name is a real company's) pair of the paper's
    current estimates, read from ROB_FILE, each as (value, low, high) in percentage points: 'gap_pp' and 'points' are
    points already, and 'estimate' and 'pooled' are proportions. With names=True, each pair comes with its key."""
    out = []

    def triple(d):
        for k, scale in (("gap_pp", 1), ("points", 1), ("estimate", 100), ("pooled", 100)):
            if k in d:
                v = d[k] * scale
                ci = next((d[c] for c in ("ci95_pp", "ci95_models_and_tables_resampled", "ci95") if c in d), None)
                if ci is None and isinstance(d.get("interval"), dict):
                    ci = [d["interval"]["low"], d["interval"]["high"]]
                lo, hi = (ci[0] * scale, ci[1] * scale) if ci else (None, None)
                return v, lo, hi
        raise KeyError(f"no estimate in {sorted(d)}")

    def walk(o, key=None):
        if isinstance(o, dict):
            if "published" in o and "without_three_tables" in o:
                pair = (triple(o["published"]), triple(o["without_three_tables"]))
                out.append((key, pair) if names else pair)
                return
            for k, v in o.items():
                walk(v, k)

    walk(ROB["estimates"])
    return out


def _rob_other(key, which):
    """Study 2b's price discount: (value, 'low percent to high percent') with every table ('reported') or without the
    three tables ('without_the_three_tables'); an upper bound beyond the discounts tested is a string in the file."""
    r = ROB_OTHER[key][which]
    lo, hi = r["ci95"]
    if isinstance(hi, str):
        m = re.fullmatch(r"more than (\d+) per ?cent", hi.strip())
        if not m:
            raise ValueError(f"{key}: an upper bound that is not a number: {hi!r}")
        hi_s = f"more than {m.group(1)} percent"
    else:
        hi_s = f"{n(hi, 1)} percent"
    return r["percent_of_the_price"], f"{n(lo, 1)} percent to {hi_s}"


ROB_LABELS = {
    "Study 2a: the gap with no experience attributes stated": "Study 1a: the effect of the fictitious name",
    "Study 2a: the gap with every product's experience attributes stated":
        "Study 2a: the effect with the experience attributes stated",
    "Study 2a: the change in the gap when every product's experience attributes were stated":
        "Study 2a: the change when the experience attributes are stated",
    "Study 1b: the brand gap over every model": "Study 1b: the effect over every model",
    "Study 1b: the penalty under consumers' own requests (chat-log requests)":
        "Study 1b: the effect under consumers' own requests",
    "Study 1b: the gap under weighted stated priorities": "Study 1b: the effect under the weighted wording of the "
                                                         "shopper's priorities",
    "Study 1b: the gap when the model may ask a clarifying question":
        "Study 1b: the effect when the model could ask a question first",
    "Study 1c: the name gap in the plain listing": "Study 1c: the effect in the plain listing",
    "Study 1c: the name gap under the instruction not to consider brand reputation":
        "Study 1c: the effect under the instruction not to consider brand reputation",
    "Study 1c: the change under the instruction not to consider brand reputation":
        "Study 1c: the change under the instruction not to consider brand reputation",
    "Study 1c: the change under the instruction to recommend only on the information listed":
        "Study 1c: the change under the instruction to recommend only on the information listed",
    "Study 1c: the change when every product's experience attributes were stated":
        "Study 1c: the change when every product's experience attributes were stated",
    "Study 1c: the search step: the store returned the best product, names hidden minus shown":
        "Study 1c, searching the store: the search returned the optimal product, without brand names minus with them",
    "Study 1c: the search step: the answer picked the best product, names hidden minus shown":
        "Study 1c, searching the store: the response chose the optimal product, without brand names minus with them",
    "Study 2b: the fictitious product's share minus the familiar product's at the same price, names shown":
        "Study 2b: the fictitious product's share minus the identical familiar product's at the same price",
    "Study 2b: the familiar product's share of the picks of either product at the same price, names shown":
        "Study 2b: the familiar product's share of the choices of either product at the same price",
}


def rob_all():
    """Every estimate of ROB_FILE with every table and without the three tables, in the order of the studies."""
    pairs = _rob_pairs(names=True)
    missing = [k for k, _ in pairs if k not in ROB_LABELS]
    if missing:
        raise KeyError(f"rob_all: no label for {missing}")
    order = sorted(pairs, key=lambda kp: list(ROB_LABELS).index(kp[0]))
    cell = lambda t: f"{n(t[0], 1)} [{n(t[1], 1)}, {n(t[2], 1)}]"
    rows = [[ROB_LABELS[k], cell(a), cell(b), n(b[0] - a[0], 1)] for k, (a, b) in order]
    other_missing = [k for k in ROB_OTHER if k not in ROB_OTHER_LABELS]
    if other_missing:
        raise KeyError(f"rob_all: no label for {other_missing}")
    for k in ROB_OTHER:  # in its own unit, after the estimates in points
        (a, a_ci), (b, b_ci) = _rob_other(k, "reported"), _rob_other(k, "without_the_three_tables")
        rows.append([ROB_OTHER_LABELS[k], f"{n(a, 1)} [{a_ci.replace(' percent', '')}]",
                     f"{n(b, 1)} [{b_ci.replace(' percent', '')}]", n(b - a, 1)])
    return md_table(["Estimate", "With every table [95% CI]", "Without the three tables [95% CI]", "Change"], rows,
                    "The Main Estimates Without the Three Tables Whose Fictitious Name Is Also a Real Company's",
                    ["l", "r", "r", "r"], label="rob-all", widths=[46, 20, 22, 10],
                    note="Percentage points, except Study 2b's familiar product's share of the choices, in percent, "
                         "and Study 2b's price discount, in percent of the price, with an upper bound beyond the "
                         "discounts up to 30 percent that were tested. "
                         "The three tables are Laptops 2 (Novatech), Laptops 3 (Primebook) and Earbuds 2 (Sonance), "
                         "in Study 1b's tables and in the tables of Studies 1a, 1c, 2a and 2b. Each "
                         "estimate with every table was first reproduced from its study's own code and results; "
                         "the estimate without the three tables comes from the same code, models and settings. Intervals: "
                         "each study's own bootstrap. Change: without the three tables minus with every table.")


def rob_summary(what):
    """The check without the three tables whose fictitious name is a real company's: the number of estimates, the
    largest absolute change in points, how many intervals changed whether they exclude zero, and (changed_ci/with,
    changed_ci/without) the interval of the one estimate whose interval changed, which must be ROB_CHANGED."""
    pairs = _rob_pairs()
    if what == "estimates":
        return f"{len(pairs):,}"
    if what == "max_change":
        return n(max(abs(b[0] - a[0]) for a, b in pairs), 1)
    both = [(a, b) for a, b in pairs if a[1] is not None and b[1] is not None]

    def excl(t):
        return t[1] > 0 or t[2] < 0
    if what.startswith("changed_ci/"):
        changed = [k for k, (a, b) in _rob_pairs(names=True) if a[1] is not None and b[1] is not None
                   and excl(a) != excl(b)]
        if changed != [ROB_CHANGED]:
            raise KeyError(f"robsum/{what}: the intervals that changed are {changed}, not [{ROB_CHANGED}]")
        a, b = dict(_rob_pairs(names=True))[ROB_CHANGED]
        t = {"with": a, "without": b}[what.split("/", 1)[1]]
        return f"{n(t[1], 1)}, {n(t[2], 1)}"
    if what == "discount/direction":  # 'larger' or 'smaller': the discount without the three tables against with them
        (key,) = list(ROB_OTHER)
        a, b = _rob_other(key, "reported")[0], _rob_other(key, "without_the_three_tables")[0]
        return "larger" if b > a else "smaller" if b < a else "the same"
    if what.startswith("discount/"):  # discount/<with|without>/<value|ci|ci_pct>: Study 2b's price discount
        _, which, part = what.split("/")
        (key,) = list(ROB_OTHER)
        v, ci_s = _rob_other(key, {"with": "reported", "without": "without_the_three_tables"}[which])
        if part == "value":
            return n(v, 1)
        return ci_s.replace(" percent", "%") if part == "ci_pct" else ci_s  # ci_pct: the main text's '%' form
    if what == "lost":  # an interval that excluded zero with every table and includes it without the three
        return f"{sum(1 for a, b in both if excl(a) and not excl(b)):,}"
    if what == "gained":  # an interval that included zero with every table and excludes it without the three
        return f"{sum(1 for a, b in both if not excl(a) and excl(b)):,}"
    raise KeyError(f"robsum/{what}")


def rel_summary(what):
    """Study 2, brand equity across releases."""
    pairs = REL["pairs"]
    ref = REL["reference_same_weights_two_routes"]
    ch = [p["mean_absolute_change_points"] for p in pairs]
    rho = [p["spearman_brand_equity"] for p in pairs]
    if what == "pairs":
        return f"{len(pairs):,}"
    if what == "above":  # uncorrected
        return f"{sum(1 for p in pairs if p['p_observed_above_sampling'] < 0.05):,}"
    if what == "above_holm":
        ps = sorted(p["p_observed_above_sampling"] for p in pairs)
        m, kept = len(ps), 0
        for i, pv in enumerate(ps):
            if pv * (m - i) >= 0.05:
                break
            kept += 1
        return f"{kept:,}"
    if what == "min_change":
        return n(min(ch), 1)
    if what == "max_change":
        return n(max(ch), 1)
    if what == "min_rho":
        return n(min(rho), 2)
    if what == "max_rho":
        return n(max(rho), 2)
    if what == "ref_change":
        return n(ref["mean_absolute_change_points"], 1)
    if what == "ref_sampling":
        return n(ref["mean_absolute_change_from_sampling_alone"]["mean"], 1)
    if what == "ref_rho":
        return n(ref["spearman_brand_equity"], 2)
    if what in ("max_pair", "min_pair"):
        p = max(pairs, key=lambda q: q["mean_absolute_change_points"]) if what == "max_pair" else \
            min(pairs, key=lambda q: q["mean_absolute_change_points"])
        return f"{_rel_name(p['earlier'])} to {_rel_name(p['later'])}"
    raise KeyError(what)


def rel_pairs():
    """The fifteen release pairs and the reference of the same weights by two routes."""
    rows = []
    for p in REL["pairs"] + [REL["reference_same_weights_two_routes"]]:
        ref = p is REL["reference_same_weights_two_routes"]
        rows.append([("Reference: " if ref else "") + f"{_rel_name(p['earlier'])} to {_rel_name(p['later'])}"
                     + (" (two routes)" if ref else ""),
                     n(p["spearman_brand_equity"], 2), n(p["mean_absolute_change_points"], 1),
                     n(p["mean_absolute_change_from_sampling_alone"]["mean"], 1),
                     _pv(p["p_observed_above_sampling"])])
    return md_table(["Pair of releases", "Spearman, brands", "Mean absolute change",
                     "From sampling alone", "P"], rows,
                    "Machine-Based Brand Equity Across Releases of One Developer's Models", ["l", "r", "r", "r", "r"],
                    label="rel-pairs", widths=[40, 15, 15, 15, 15],
                    note="In each pair, an earlier and a later release of one line are compared on the same tables and "
                         "conditions, on different prompts: each of the 30 models had its own display orders, letters "
                         "and wordings, and the Claude 5.5 models answered prompts drawn from the 30 models' requests. "
                         "The pairs that end at a Claude 5.5 model also differ in their settings. Spearman: "
                         "the correlation of the 73 brands' equity in the two releases. Mean absolute change: over the "
                         "brands, in percentage points. From sampling alone: the mean absolute change if both releases "
                         "chose at the same rates on identical prompts, which understates the change that no true "
                         "difference would give on different prompts. P: the share of draws in which sampling alone gave a change at "
                         "least as large (responses resampled, 10,000 draws), without correction for the 15 pairs. The "
                         "reference is not a release: Gemma 4 31B "
                         "through Google's interface against the same weights on a university's computers.")


# ---------------------------------------------------------------- Study 4, the machine brand audit (the Claude panel)

AU = paper_names.later(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json")
AU_CLAUDE = paper_names.later(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-claude.json")
AU_DEC = {"salience": 2, "recognition": 2, "tone": 2, "quality": 2, "credibility": 2, "typicality": 1, "gap": 1}


def au_range(component, group, stat):
    """Study 4: the lowest or highest mean of one component over the four Claude models and, for 'familiar', the two
    kinds of familiar name (high and medium), from numbers-claude.json 'descriptive'; group 'invented' is the invented
    names; 'gaprel' gives the split-half reliability of the gap among familiar brands over the models."""
    if component == "gaprel":
        vals = [AU["reliability_familiar"][m]["gap"] for m in AU["models"]]
        return n(min(vals) if stat == "min" else max(vals), 2)
    kinds = {"familiar": ["familiar-high", "familiar-medium"], "high": ["familiar-high"],
             "medium": ["familiar-medium"], "invented": ["invented"]}[group]
    vals = [AU_CLAUDE["descriptive"][m][k][component] for m in AU_CLAUDE["models"] for k in kinds]  # Claude panel only
    return n(min(vals) if stat == "min" else max(vals), AU_DEC[component])


AU_LABELS = [("salience", "Awareness: salience"), ("recognition", "Awareness: recognition"),
             ("typicality", "Image: typicality"), ("quality", "Image: inferred quality"),
             ("credibility", "Image: credibility"), ("tone", "Image: tone of associations")]


def au_tests():
    """Study 4: each component's slope on the own-name gap (test 1, all products and familiar names only) and on the
    difference between two names on the same listing (test 2), with 95% intervals; Holm for test 1 on all products."""
    rows = []
    for key, label in AU_LABELS:
        t1, tf, t2 = AU["test1"][key], AU["test1_familiar"][key], AU["test2"][key]
        rows.append([label, f"{n(t1['est'], 1)} ({ci([t1['lo'], t1['hi']], 1)})", _pv(t1["p_holm"]),
                     f"{n(tf['est'], 1)} ({ci([tf['lo'], tf['hi']], 1)})",
                     f"{n(t2['est'], 1)} ({ci([t2['lo'], t2['hi']], 1)})"])
    return md_table(["Score", "All products", "P after Holm", "Familiar names only", "Same listing, two names"],
                    rows, "Study 3b: Machine Brand Awareness and Image Against Each Brand's Equity",
                    ["l", "r", "r", "r", "r"], label="au-tests", widths=[20, 22, 12, 22, 22],
                    note="Change in a brand's equity (the share of responses that chose its product with "
                         "brand names minus the share without them), in percentage points, per standard deviation of "
                         "the measure, with 95% CIs from a bootstrap that resamples tables and models (2,000 draws). "
                         "All products: the 170 products of the 34 tables in each model, both centered within table "
                         "and model, with the product's share without brand names as a control; Holm's method "
                         "corrects the six tests. Familiar names only: the same test on the 135 products under "
                         "familiar names. Same listing, two names: the "
                         "difference between the equities of a fictitious and a familiar name on "
                         "the same product, against the difference between their scores. Two language models coded "
                         "the tone of each model's descriptions of the brand (Web Appendix " + _wa("study3") + ").")


SETTINGS_KEYS = {
    "OpenAI 2026a": "openai2026commerce", "OpenAI 2025a": "openai2025feed", "OpenAI 2025b": "openai2025shopping",
    "OpenAI n.d.-a": "openaishoppinghelp", "OpenAI n.d.-b": "openaiadshelp",
    "Google 2025": "google2025aimode", "Google 2026": "google2026agentic",
    "Google n.d.-a": "googlemerchantspec", "Google n.d.-b": "googlemerchantlisting",
    "Schema.org 2026": "schemaorg2026product", "Chilimbi 2024": "chilimbi2024technology",
    "Sheth and Yada 2026": "sheth2026conversations", "Chen and Koudas 2026": "chen2026drives",
    "Allouah et al. 2025": "allouah2026what", "Chu and Hou 2026": "chu2026incumbent",
    "Zhao et al. 2024": "zhao2024wildchat", "Chiang et al. 2024": "chiang2024chatbot",
    "Miroyan et al. 2026": "miroyan2026search", "Yao et al. 2022": "yao2022webshop",
    "Uberti-Bona Marin et al. 2026": "ubertibonamarin2026if", "Zhang et al. 2018": "zhang2018towards",
    "Aliannejadi et al. 2019": "aliannejadi2019asking", "Zamani et al. 2020": "zamani2020generating",
    "Chen, Wiseman and Dhingra 2024": "chen2024chatshop",
}


def cite_labels(text):
    """Google
    n.d.-a)', with a pandoc citation of the references.bib keys ('[@openai2026commerce; @openai2025feed;
    @googlemerchantspec]'). Refuses a label that SETTINGS_KEYS does not hold."""
    import re as _re
    year = r"(?:\d{4}[a-z]?|n\.d\.-[a-z])"

    authors = sorted({lab.rsplit(" ", 1)[0] for lab in SETTINGS_KEYS}, key=len, reverse=True)

    def one(m):
        keys = []
        for part in m.group(1).split(";"):
            part = part.strip()
            pm = None
            for a in authors:  # the longest known author that ends the part, after an optional prefix ('as in')
                pm = _re.fullmatch(rf"(.*?)({_re.escape(a)}) ({year}(?:, {year})*)", part)
                if pm:
                    break
            if not pm:
                raise ValueError(f"settings tables: no references.bib key for '{part}' (add it to SETTINGS_KEYS)")
            prefix = pm.group(1).strip()
            cites = []
            for y in pm.group(3).split(", "):
                label = f"{pm.group(2)} {y}"
                if label not in SETTINGS_KEYS:
                    raise ValueError(f"settings tables: no references.bib key for '{label}' (add it to SETTINGS_KEYS)")
                cites.append("@" + SETTINGS_KEYS[label])
            cites[0] = (prefix + " " + cites[0]) if prefix else cites[0]
            keys += cites
        return "[" + "; ".join(keys) + "]"

    for label, key in SETTINGS_KEYS.items():  # narrative citations first: 'Yao et al. (2022)' -> '@yao2022webshop'
        author, y = label.rsplit(" ", 1)
        text = text.replace(f"{author} ({y})", f"@{key}")
    return _re.sub(rf"\(([^()]*?{year}(?:[^()]*?))\)", one, text)


SETTINGS_MODELS = [  # each setting's row, and the models in the estimate that the text reports for it
    ("A table of products", ("s2a", "2a/models", "n")),
    ("A typed request", ("hrq", "result/models", "int")),
    ("A clarifying question", ("clar", "all_models/models", "int")),
    ("The store's listing", ("s1st", "models", "n")),
    ("The model's own searches", ("s1s", "models", "n")),
    ("Review pages at answer time", ("h2rg", "result/models", "int")),
]


def settings_table():
    """A
    working note on the state of an analysis (", analysis in progress") is left out, because the paper describes one
    state of the work."""
    import re as _re
    src = (PKG / "exhibits/results/figures/table_settings.md").read_text(encoding="utf-8").splitlines()
    body = []
    for ln in src:
        if not ln.startswith("| ") or ln.startswith("| Setting"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 4:
            raise ValueError(f"table_settings.md: a row with {len(cells)} cells, not 4: {ln[:60]}")
        cells[3] = _re.sub(r",\s*analysis in progress$", "", cells[3])
        hit = [n for prefix, n in SETTINGS_MODELS if cells[0].startswith(prefix)]
        if len(hit) != 1:
            raise ValueError(f"settings table: no estimate file named for the row '{cells[0]}' (SETTINGS_MODELS)")
        cells[3] = _mk(*hit[0])
        body.append([cite_labels(c) for c in cells])
    if not body:
        raise ValueError("table_settings.md: no rows")
    return md_table(["Setting (study)", "What the assistant saw", "Its counterpart in deployed assistants",
                     "Models"], body,
                    "Settings and Their Deployed Counterparts",
                    ["l", "l", "l", "r"], label="settings", widths=[20, 33, 33, 14],
                    note="Each setting is in Figure \\ref{fig:settings}; its full messages are in Web Appendix "
                         + _wa("study1a-stimuli") + ".")


def wa_settings_table():
    """Its last column (the state of each analysis) is a working note and is left out."""
    src = (PKG / "exhibits/results/figures/wa_table_settings.md").read_text(encoding="utf-8").splitlines()
    body = []
    for ln in src:
        if not ln.startswith("| ") or ln.startswith("| Setting"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 5:
            raise ValueError(f"wa_table_settings.md: a row with {len(cells)} cells: {ln[:60]}")
        cells = [c.replace("as an agent searches the simulated shop", "as a language model searches the simulated shop")
                 for c in cells]
        hit = [n for prefix, n in SETTINGS_MODELS if cells[0].startswith(prefix)]  # the estimate's count, as Table 2
        if len(hit) != 1:
            raise ValueError(f"wa settings table: no estimate file named for the row '{cells[0]}' (SETTINGS_MODELS)")
        cells[4] = _mk(*hit[0])
        body.append([cite_labels(c) for c in cells[:5]])
    if not body:
        raise ValueError("wa_table_settings.md: no rows")
    return md_table(["Setting", "Study", "What the model received", "How deployed shopping assistants do the same",
                     "Models"], body,
                    "The Settings in Which the Models Chose, and How Deployed Shopping Assistants Work",
                    ["l", "c", "l", "l", "r"], label="wa-settings", widths=[13, 6, 34, 34, 13],
                    note="Each setting's full messages are in Figure \\ref{fig:wa-settings}.")


def settings_sources():
    import re as _re
    cited = set()
    for f in ("table_settings.md", "wa_table_settings.md"):
        text = (PKG / "exhibits/results/figures" / f).read_text(encoding="utf-8")
        for group in _re.findall(r"\[(S\d+(?:,\s*S\d+)*)\]", text):
            cited.update(x.strip() for x in group.split(","))
    lines = (PKG / "exhibits/materials/settings_sources.md").read_text(encoding="utf-8").splitlines()
    entries = {}
    for ln in lines:
        m = _re.match(r"- \[(S\d+)\] (.+)", ln)
        if m:
            url = _re.search(r"https?://\S+", m.group(2))
            if url:  # the address as <...>, so that pandoc writes \url{}, which breaks at slashes
                address = url.group(0).rstrip(".")
                entries[m.group(1)] = m.group(2)[:url.start()] + f"<{address}>"
            else:
                entries[m.group(1)] = m.group(2)
    missing = sorted(cited - set(entries), key=lambda x: int(x[1:]))
    if missing:
        raise ValueError(f"settings tables cite sources with no entry in HOW-ASSISTANTS-WORK.md: {missing}")
    keys = sorted(cited, key=lambda x: int(x[1:]))
    return "\n".join(f"- [{k}] {entries[k]}" for k in keys)


STORE_ARMS = [
    ("plain", "Plain listing (the control condition)"),
    ("plain-info", "Experience attributes stated for every product"),
    ("feed-openai", "OpenAI's product feed, current fields"),
    ("feed-openai-2025", "OpenAI's product feed, October 2025 fields"),
    ("feed-google", "Google Merchant Center product data (no rating field)"),
    ("schema-org", "schema.org product markup"),
    ("sponsored-familiar", "\"Sponsored\" on a familiar brand's product"),
    ("sponsored-best", "\"Sponsored\" on the optimal product"),
    ("position-first", "Optimal product listed first"),
    ("position-middle", "Optimal product listed third"),
    ("position-last", "Optimal product listed last"),
    ("rating-0.1", "Optimal product rated 0.1 stars higher"),
    ("rating-0.3", "Optimal product rated 0.3 stars higher"),
    ("rating-0.5", "Optimal product rated 0.5 stars higher"),
    ("instruct-listed", "Instruction: \"Recommend only on the information listed.\""),
    ("instruct-brand", "Instruction: \"Do not consider brand reputation.\""),
]


def _pp_ci(node):
    iv = node["interval"]
    return f"{n(100 * node['pooled'], 1)} ({ci([100 * iv['low95'], 100 * iv['high95']], 1)})"


def store_arms():
    st = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/store/all-models/numbers.json")
    gaps, changes = st["name gap g(arm)"], st["change D(arm) = g(arm) - g(plain)"]
    rows = []
    for arm, label in STORE_ARMS:
        if arm == "plain":
            rows.append([label, _pp_ci(gaps[arm]), "", "", ""])
            continue
        d = changes[arm]
        rows.append([label, _pp_ci(gaps[arm]), _pp_ci(d), _pv(d["interval"]["p_two_sided"]), _pv(d["holm"])])
    return md_table(["Condition", "Effect (95% CI)", "Change from the plain listing (95% CI)", "P", "P after Holm"],
                    rows, "Study 1c: Effect by Store Condition", ["l", "r", "r", "r", "r"], label="store-arms",
                    widths=[38, 18, 22, 10, 12],
                    note="The effect is the share of responses that chose the optimal product without brand names "
                         "minus the share with the fictitious name on it, in percentage points. Intervals and P values "
                         "come from a bootstrap over tables and models (10,000 draws); the 15 changes are corrected "
                         "together by Holm's method.")


def search_tests():
    s1 = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/search/all-models/numbers.json")
    tests = [("fetched: hidden minus shown (primary 1)", "The store returned the optimal product"),
             ("picked the best: hidden minus shown (primary 2)", "The model chose the optimal product"),
             ("picked the best where fetched in both: hidden minus shown (primary 3)",
              "The model chose it, where the store returned it in both versions")]
    rows = [[label, _pp_ci(s1[k]), _pv(s1[k]["interval"]["p_two_sided"]), _pv(s1[k]["holm"])] for k, label in tests]
    brand = s1["brand search, any brand of the 34 tables"]
    own = s1["brand search, one of the table's own brands"]
    return md_table(["Share without brand names minus share with them", "Difference (95% CI)", "P", "P after Holm"],
                    rows, "Study 1c: Tests of the Search Step",
                    ["l", "r", "r", "r"], label="search-tests", widths=[50, 22, 12, 14],
                    note=f"In percentage points. The three tests are Holm-corrected together. A search named any "
                         f"brand in {n(100 * brand['pooled'], 1)}% of the sets of searches and one of the table's own "
                         f"brands in {n(100 * own['pooled'], 1)}%.")


PRIORITY_AND_TEXT_FILES = {"sp": PKG / "study1b-64-models-on-34-tables/results/priorities/numbers.json",
               "b5": PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/training-text/numbers.json"}
SP_WORDINGS = [("preference_vague", "Vague priority"), ("preference_weighted", "Weighted priorities"),
               ("preference_explicit", "Explicit requirements, product named"),
               ("utility_explicit", "Utility of each product, product named")]


def _numbers_of(key):
    return json.loads(PRIORITY_AND_TEXT_FILES[key].read_text(encoding="utf-8"))


def sp_wordings():
    a = _numbers_of("sp")["all_models"]
    rows = []
    for key, label in SP_WORDINGS:
        g = a["gap_names_hidden"][key]["pooled"]
        rows.append([label, f"{g['shown_nonoptimal_pct']:.1f}", f"{g['hidden_nonoptimal_pct']:.1f}",
                     f"{n(g['gap_pp'], 1)} ({ci(g['ci95_models_and_tables_resampled'], 1)})",
                     _pv(g["p_two_sided_models_and_tables_resampled"])])
    return md_table(["Wording of the shopper's priorities", "Not the top-ranked product, with brand names (%)",
                     "Without brand names (%)", "Effect (95% CI)", "P"], rows,
                    f"Study 1b: The Effect of the Fictitious Name Under Each Wording of the Shopper's Priorities, Over "
                    f"{len(a['models'])} Models", ["l", "r", "r", "r", "r"], label="sp-wordings",
                    widths=[30, 18, 16, 22, 10],
                    note="The effect is the share of responses that did not choose the top-ranked product with "
                         "brand names minus that share without them, in percentage points, over the 34 tables, with "
                         "an interval and P from a bootstrap that resamples tables and models. The two explicit "
                         "wordings named the product that met every requirement or had the highest utility.")


def sp_ladder():
    lad = _numbers_of("sp")["all_models"]["ladder"]
    names = {"no stated priorities (s1rerun1)": "No stated priority"}
    names.update(dict(SP_WORDINGS))
    rows = []
    for st in lad["steps"]:
        label = names.get(st["step"], st["step"])
        change = ""
        if "change_from_previous_pp" in st:
            change = (f"{n(st['change_from_previous_pp'], 1)} ({ci(st['change_ci95'], 1)}), "
                      f"P {_pv(st['change_p_two_sided'])}")
        rows.append([label, f"{n(st['gap_pp'], 1)} ({ci(st['ci95_models_and_tables_resampled'], 1)})",
                     _pv(st["p_two_sided"]), change])
    return md_table(["Wording", "Effect (95% CI)", "P", "Change from the row above (95% CI), P"], rows,
                    f"Study 1b: The Effect From No Stated Priority to the Most Precise Wording, Over the "
                    f"{lad['models']} Models That Answered Every Wording", ["l", "r", "r", "r"], label="sp-ladder",
                    widths=[30, 22, 10, 38],
                    note="In percentage points, with intervals and P values from a bootstrap that resamples tables "
                         "and models.")


MEASURE_FILES = {"summary": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/pilot1/summary.json",
                 "brands": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/pilot1/brand_pairs.csv"}
MS_MEASURES = {"mbbe": "mbbe", "rating": "rating_difference", "premium": "premium_at_one_in_five",
               "corpus": "corpus_table_gap", "blind": "blind_gap"}
MS_CATEGORY = {"coffee_makers": "coffee makers", "running_shoes": "running shoes", "tvs": "televisions"}


def _ms_summary():
    return json.loads(MEASURE_FILES["summary"].read_text(encoding="utf-8"))


def _ms_brands():
    import csv
    with open(MEASURE_FILES["brands"], encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def ms_brands():
    rows = []
    for r in sorted(_ms_brands(), key=lambda x: -float(x["share_premium_median_pp"])):
        price = "" if not r["price_equivalent_median_pct"] else (
            f"{n(float(r['price_equivalent_median_pct']), 0)}"
            + ("" if r["price_equivalent_median_inside_tested_prices"] == "True" else " (beyond)"))
        rows.append([r["brand"], MS_CATEGORY.get(r["category"], r["category"]), r["models"],
                     f"{n(float(r['share_premium_median_pp']), 1)} ({n(float(r['share_premium_min_pp']), 1)}, "
                     f"{n(float(r['share_premium_max_pp']), 1)})",
                     f"{r['models_above_zero']} / {r['models_below_zero']}",
                     f"{price} ({r['models_with_a_price_equivalent']}; {r['price_equivalents_beyond_tested_prices']})"])
    return md_table(["Brand", "Category", "Models", "Share premium, median (lowest, highest model), points",
                     "Models above / below zero", "Price premium, median % (models with one; beyond the tested prices)"],
                    rows, "Study 2b's Pretest: Each Familiar Brand's Premium Over the Models", ["l", "l", "r", "r", "r", "r"],
                    label="ms-brands", widths=[14, 14, 8, 24, 14, 26],
                    note="The share premium is the brand's predicted share among five otherwise identical products, "
                         "the other four under fictitious names, minus 20 points; above or below zero counts the models "
                         "whose interval lies above or below zero. The price premium exists where the familiar name's "
                         "price slope is below zero by its interval; 'beyond' marks a median that lies beyond the "
                         "prices that the choice sets showed, where the premium extends the fitted price slope.")


def ms_checks():
    """Study 2c's checks of the measure as one table (the pilot gives intervals and counts, not P values)."""
    s = _ms_summary()
    kg, rel, ho, pe = s["known_groups"], s["reliability"], s["held_out_gain"], s["price_equivalent"]
    conv = s["convergence"]
    pred = s["corpus_table_prediction"]["both builds"]["primary (every familiar name estimated)"]
    disc = {k: v for k, v in s["discriminant"].items() if k != "mbbe_pair_reliability"}
    ruled = sum(1 for v in disc.values() if -0.5 < v["corrected_ci95"][0] and v["corrected_ci95"][1] < 0.5)

    def cr(a, b):
        c = conv[f"{a} | {b}"]
        return (f"r = {_r(c['corrected_r'])} ({_r(c['corrected_ci95'][0])}, {_r(c['corrected_ci95'][1])}); "
                f"uncorrected {_r(c['pooled_r'])}")

    rows = [
        ["Models in the analyses", f"{s['models_included']} of {s['models']} (one left out: a recommendation identified in fewer than 90% of its responses)", ""],
        ["Model and category cells in which the model followed the attributes",
         f"{s['cells_that_read_the_specifications_included_models']}", "The others are reported apart"],
        ["The familiar brands' mean equity above zero by its interval (known groups)",
         f"{kg['models_familiar_mean_interval_above_zero']} of {kg['models_with_a_familiar_mean_interval']} models",
         "The analysis plan's test"],
        ["Split-half reliability of at least .80", f"{rel['models_at_least_0_80_included']} of "
         f"{s['models_included']} models (median {_r(rel['median_included'])})", "The analysis plan's criterion"],
        ["The name terms improve the fit on held-out choice sets",
         f"{ho['models_positive_summed_over_reading_categories']} of {ho['models']} models summed over categories; "
         f"{ho['models_positive_in_every_reading_category']} in every category", "The analysis plan's criterion, two readings"],
        ["Equity against the rating of one product shown alone", cr("mbbe", "rating_difference"),
         "Corrected for both reliabilities"],
        ["Equity against the direct price premium", cr("mbbe", "premium_at_one_in_five"),
         f"The premium's reliability is {_r(s['convergence_pooled_reliability']['premium_at_one_in_five']['spearman_brown_mean'])}"],
        ["Equity against the effect of the name on Study 1b's tables (ten models)", cr("mbbe", "corpus_table_gap"), ""],
        ["Predicting the name's effect on 28 tables of Studies 1a and 1b from the equity, against predicting no change",
         f"difference in mean absolute error = {pred['difference']:.3f} ({pred['ci95'][0]:.3f}, {pred['ci95'][1]:.3f})",
         "A larger error than no change"],
        ["Measures of a brand's standing for which a strong correlation is ruled out", f"{ruled} of {len(disc)}",
         "Not ruled out: familiarity to consumers, published value"],
        ["Price premiums beyond the tested prices", f"{pe['beyond_tested_prices']} of {pe['defined']}",
         "They extend the fitted price slope"],
    ]
    return md_table(["Check", "Result (95% CI)", "Note"], rows, "Study 2b's Pretest: The Checks of the Measure",
                    ["l", "l", "l"], label="ms-pre-checks", widths=[40, 36, 24],
                    note="Correlations are over brand, category and model cells, with intervals that resample brands "
                         "and models; the corrected intervals treat the two reliabilities as known, so they leave out "
                         "the reliabilities' own uncertainty, which is largest where the direct premium enters. Web "
                         "Appendix B gives every check by model.")


MCR_FILES = {"summary": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/summary.json",
             "numbers": PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/numbers.json"}
MCR_MODELS = ["claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5"]


def _mcr():
    return json.loads(MCR_FILES["summary"].read_text(encoding="utf-8"))


def _mcr_numbers():
    return json.loads(MCR_FILES["numbers"].read_text(encoding="utf-8"))


def _over_models(group):
    """The measure's estimates for each brand over a group of models (all, open, claude or gpt), from the final run over
    every model. Its GPT group holds all four GPT models, where the route file
    full1-codex holds only the two Sol models; its Claude group equals the Claude
    route's file."""
    if group not in ("all", "open", "claude", "gpt"):
        raise ValueError(f"no group {group}")
    return paper_names.read(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/over_models.json")["over_models"]


def _mcr_rating_equivalents():
    """Each Claude model's rating equivalent of every brand that has one in all four models, in one order."""
    nums = _mcr_numbers()["models"]
    per = {m: {(c, b): v.get("rating_equivalent_stars") for c, cell in nums[m].items()
               for b, v in cell["main"]["brands"].items()} for m in MCR_MODELS}
    keys = sorted(k for k in per[MCR_MODELS[0]] if all(per[m].get(k) is not None for m in MCR_MODELS))
    return {m: [per[m][k] for k in keys] for m in MCR_MODELS}


def _mcr_corr():
    """The rating equivalents' correlation between each pair of Claude models (as RESULTS.md computes it); refuses
    when its extremes differ from summary.json's."""
    import numpy as np
    re_ = _mcr_rating_equivalents()
    s = _mcr()
    if len(next(iter(re_.values()))) != s["pairs_with_rating_equivalent_in_all"]:
        raise ValueError("ms_full: the brands with a rating equivalent in every model differ from summary.json")
    c = {(a, b): float(np.corrcoef(re_[a], re_[b])[0, 1]) for a in MCR_MODELS for b in MCR_MODELS if a != b}
    if abs(min(c.values()) - s["rating_equivalent_r_lowest"]) > 1e-9 or \
            abs(max(c.values()) - s["rating_equivalent_r_highest"]) > 1e-9:
        raise ValueError("ms_full: the rating equivalents' correlations differ from summary.json")
    return c


def _mcr_price_median(m):
    """A Claude model's median price premium over the brands that have one (summary.json gives it only for the models
    that answered the direct premium; this refuses when it differs from those)."""
    import statistics
    vals = [v["price_premium_pct"] for cell in _mcr_numbers()["models"][m].values()
            for v in cell["main"]["brands"].values() if v.get("price_premium_pct") is not None]
    med = statistics.median(vals)
    given = _mcr()["models"][m].get("price_premium_median_pct")
    if given is not None and abs(round(med, 0) - round(given, 0)) > 0:
        raise ValueError(f"ms_full: the median price premium of {m} differs from summary.json ({med} against {given})")
    return med


def ms_full():
    """The models with open weights
    and the GPT models join it when they have answered."""
    s = _mcr()
    ms = [s["models"][m] for m in MCR_MODELS]
    corr = _mcr_corr()
    # the columns over every model and over the models with open weights (full1-all/summary.json): the brands above and
    # below zero from the estimate over the group's models, every other row the median over the group's models of each
    # model's own value; the Claude group's medians must equal the medians of the four Claude columns
    import statistics
    cols = paper_names.read(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/summary.json")["table_ms_checks_columns"]
    for key in ("mean_share_premium_pp", "price_premium_beyond_tested"):
        own = statistics.median(m[key] for m in ms)
        if abs(own - cols["claude"][f"{key}_median"]) > 1e-9:
            raise ValueError(f"ms_full: the Claude group's median {key} differs from the four Claude columns")
    groups = [cols["all"], cols["open"]]

    def med(g, key, f):
        return f(g[f"{key}_median"]) if g.get(f"{key}_models") else "none"

    def row(label, key, f, missing="not asked", group=None):
        return ([label] + [f(m[key]) if key in m else missing for m in ms]
                + [group(g) if group else med(g, key, f) for g in groups])

    if any(g["pairs"] != s["pairs"] for g in groups):
        raise ValueError("ms_full: the groups' brands differ from the Claude models'")
    rows = [
        row("Choice sets with brand names answered", "lists", lambda x: f"{x:,.0f}"),
        row(f"Brands with an equity above zero by its interval (of {s['pairs']})", "above_zero", str,
            group=lambda g: str(g["above_zero"])),
        row("Brands with an equity below zero by its interval", "below_zero", str, group=lambda g: str(g["below_zero"])),
        ["Equity, lowest to highest brand (log-odds)"] + [f"{n(m['value_lowest'])} to {n(m['value_highest'])}"
                                                           for m in ms]
        + [f"{n(g['value_lowest_median'])} to {n(g['value_highest_median'])}" for g in groups],
        row("Mean share premium (points)", "mean_share_premium_pp", lambda x: n(x, 1)),
        row(f"Mean rating equivalent over the {s['pairs_with_rating_equivalent_in_all']} brands with one in every "
            "Claude model (stars)", "mean_rating_equivalent_stars", lambda x: n(x, 2)),
        ["Correlation of the rating equivalents with the other three models, lowest to highest"]
        + [f"{_r(min(v for (a, _), v in corr.items() if a == m))} to "
           f"{_r(max(v for (a, _), v in corr.items() if a == m))}" for m in MCR_MODELS] + ["", ""],
        row("Reliability within category", "reliability", _r,
            group=lambda g: med(g, "reliability_kept_categories", _r)),
        row(f"Price premiums beyond the tested prices (of {s['pairs']})", "price_premium_beyond_tested", str,
            group=lambda g: med(g, "price_premium_beyond_tested", lambda x: n(x, 0))),
        ["Median price premium from the main choice sets (%)"] + [n(_mcr_price_median(m), 0) for m in MCR_MODELS]
        + [med(g, "price_premium_median_pct_all_pairs", lambda x: n(x, 0)) for g in groups],
        row("Direct price premium: the brand's share at the same price (%)", "direct_share_same_price_pct",
            lambda x: n(x, 0)),
        row("Direct price premium, median (%)", "direct_premium_median_pct", lambda x: n(x, 1)),
        row("Correlation of the direct and the main price premiums across brands", "direct_with_price_premium_r", _r),
    ]
    return md_table(["", *[m["name"] for m in ms], "Every model", "Open weights"], rows,
                    "Study 2b: The Measure for Each Brand in the Four Claude Models, Over Every Model and Over the "
                    "Models With Open Weights",
                    ["l", "r", "r", "r", "r", "r", "r"], label="ms-checks", widths=[32, 10, 10, 10, 10, 14, 14],
                    note="Each model answered every category's choice sets of the main version through Anthropic's "
                         "interface; Fable 5.1 answered 800 a category and none of the direct price premium, because "
                         "of the research budget. Every model said that it did not know any fictitious name, so each "
                         "reference contains every fictitious name of its category. A brand's equity is estimated at the center "
                         "of its band of prices; the share premium is its share among five otherwise identical products, "
                         "the other four under fictitious names, minus 20 points; the rating equivalent is the equity in "
                         "stars of rating, and coffee makers have none in these models. Reliability is the "
                         "Spearman-Brown value of the mean split-half correlation over a model's categories. The direct "
                         "price premium's prices are 10% apart. Every model and open weights: the "
                         f"{cols['all']['models']} models and the {cols['open']['models']} models with open weights in "
                         "the estimates; the brands above and below zero come from the estimate over the group's "
                         "models, and every other entry is the median over the group's models of each model's own "
                         "value. There, the mean rating equivalent is each model's mean over its own brands with one, "
                         "the reliability is over each model's kept categories, and the correlation of the rating "
                         "equivalents has no group value. The brands' numbers are in Web Appendix "
                         + _wa("study2c-measure") + ".")


def ms_summary():
    """Study 2b's measure in the main text, with only the rows that the claim needs: the brands above and below zero and the reliability,
    over every model and in each group of models, from the same columns as ms_full (full1-all/summary.json). ms_full,
    the full table, moves to Web Appendix K. It keeps the label ms-checks, which the main text cites."""
    cols = paper_names.read(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/summary.json")["table_ms_checks_columns"]
    groups = [("all", "Every model"), ("claude", "Claude models"), ("gpt", "GPT models"),
              ("open", "Models with open weights")]
    pairs = {cols[k]["pairs"] for k, _ in groups}
    if len(pairs) != 1:
        raise ValueError("ms_summary: the groups' brands differ")
    pairs = pairs.pop()
    rows = [
        [f"Brands with an equity above zero by its interval (of {pairs})"] + [str(cols[k]["above_zero"]) for k, _ in groups],
        ["Brands with an equity below zero by its interval"] + [str(cols[k]["below_zero"]) for k, _ in groups],
        ["Reliability within category, median over the models"]
        + [_r(cols[k]["reliability_kept_categories_median"]) if cols[k].get("reliability_kept_categories_models")
           else "none" for k, _ in groups],
    ]
    return md_table(["", *[f"{label} ({cols[k]['models']})" for k, label in groups]], rows,
                    "Study 2b: Brand Equity Measure by Model Group",
                    ["l", "r", "r", "r", "r"], label="ms-checks", widths=[36, 16, 16, 16, 16],
                    note="The number of models in each group is in parentheses. A brand's equity is its name's "
                         "coefficient at the center of its band of prices minus the mean coefficient of its category's "
                         "fictitious names; the brands above and below zero are those whose interval lies above or below "
                         "zero in the estimate over the group's models. Reliability is the Spearman-Brown value of the "
                         "mean split-half correlation over the categories in which a model followed at least two of the "
                         "three attributes, and each entry is its median over the group's models. The measure for each "
                         "model and each brand's numbers are in Web Appendix " + _wa("study2c-measure") + ".")


TABLES.update({"ms_summary": ms_summary})


def _usd_text(v, signed=False):
    """A dollar amount for the text, refused when it is not finite."""
    import math
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import markers
    if not isinstance(v, (int, float)) or not math.isfinite(v):
        raise markers.MarkerError(f"a non-finite dollar value ({v!r}); word an unbounded interval by hand")
    return (("−" if v < 0 else "") if signed else "") + f"\\${abs(v) if signed else v:,.0f}"


def _mk(src, path, how):
    """A number as a marker prints it ({{src:path|how}}), for a table that the text cannot hold markers in."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import markers
    return markers.fmt(markers.lookup(src, path), how)


def _m_usd(group):
    """The group's median dollar premium, as {{table:usdsum/<group>/median}} prints it."""
    return _Made({})[f"usdsum/{group}/median"]  # escaped for Markdown, as in the text


def tests_overview():
    """Table 1 of the paper: every test, what it showed and where it is reported. Every number and every
    Web Appendix letter comes from the files and the labels that the text uses. Shortened on 22 November 2026 to fit
    JMR's 50 pages, with every row kept: the last column gives the study and the Web Appendix letters, which the note
    explains, so that most rows take two lines (a scratch render: 44 lines against 63)."""
    sh = "2c/familiar twin's share of pair picks at the same price/names shown"
    s3 = "f12/lift_dpo_NEUTRAL-CLEAN_vs_NONE/pooled/difference"
    rows = [
        ["1a", "One optimal product, with and without brand names",
         f"The optimal product was chosen {_mk('s2a', '2a/pooled/gap_none/estimate', 'pp1')} points less often under a "
         "fictitious name", f"{_wa('study1a-stimuli')}, {_wa('study1a-results')}"],
        ["1b", f"34 tables, {modelunit('study1b/models')} models ({modelunit('study1b/settings')} settings)",
         f"{_mk('s1p', 'pooled/gap_pp', 'f1')} points less often with brand names; "
         f"{_mk('h1b', 'result/moderators/release date (years)/coefficient', 'f1')} points more per year of release",
         f"{_wa('study1b-results')}, {_wa('models')}"],
        ["1b", "Typed requests and a clarifying question (both on Study 1a's tables), stated priorities, extended "
         "thinking",
         "The effect remained in each", f"{_wa('study1b-results')}, {_wa('study1b-requests')}"],
        ["1c", "A store's listings and the models' own searches",
         "The effect remained in every listing format and after a search", _wa('study1c-store')],
        ["1b", "Each brand's equity and its change across releases",
         "Not reliably correlated with a brand's frequency in public text or familiarity to consumers over the 30 "
         "models of the brand-level analysis; less equity for more frequent names in the ten models with open weights",
         _wa('study1d-brands')],
        ["2a", "Experience attributes stated (failure rate, warranty, time on the market), every figure independently "
         "tested, returns free",
         f"Attenuated from {_mk('s2a', '2a/pooled/gap_none/estimate', 'pp1')} to "
         f"{_mk('s2a', '2a/pooled/gap_supplied/estimate', 'pp1')} points; eliminated in closed-weight models "
         "(equivalence test)",
         _wa('study2-by-model')],
        ["2a", "Review pages, the models' reasons, each piece of information alone",
         "Remained with review pages; no single piece attenuated it reliably",
         f"{_wa('study2-by-model')}, {_wa('study2a-reasons-pages')}"],
        ["2b", "Otherwise identical products at the same price",
         f"The familiar product received {_mk('s2c', sh + '/all/estimate', 'pp0')}% of choices between the two "
         f"({_mk('s2c', sh + '/Anthropic/estimate', 'pp0')}% in Claude models)", _wa('study2-by-model')],
        ["2b", "Each familiar brand's equity in dollars",
         f"A median of {_m_usd('all')} ({_m_usd('claude')} in the Claude and {_m_usd('gpt')} in the GPT models)",
         _wa('study2c-measure')],
        ["3a", "Training on pages about new brands",
         f"Neutral pages increased equity by {_mk('s3', s3, 'f1')} points; positive associations added little; "
         "negative ones eliminated the effect", _wa('study3')],
        ["3a", "Six kinds of page about 14 fictitious product brands (OLMo 2 7B)",
         f"Every kind increased equity (bare mentions by {_mk('tr', 'q2/numbers/kinds/E/bare/estimate', 'f1')} "
         "points, more than expert reviews); inferred quality hardly changed", _wa('study3')],
        ["3b", "What released models say about a brand; the tone of training text",
         "Neither predicted a brand's equity over every model after correction; after correction within each "
         f"model, what it says predicted equity in {auper('claude/holm_above_word')} of the "
         f"{auper('claude/total_word')} Claude models and {auper('gpt/holm_above_word')} of the "
         f"{auper('gpt/total_word')} GPT models, and in the models with open weights in both directions",
         _wa('study3')],
        ["3", "Tuning a model to act as an assistant", "The effect was more pronounced after tuning, much of it a "
         "lower probability of the optimal product under any name",
         _wa('study3')],
        ["4", "People's choices after an assistant's recommendation",
         f"People chose the recommended familiar product more often "
         f"({_mk('cs', 'study_3/H1_focal_biased_vs_neutral/group1/pct', 'f1')}% vs. "
         f"{_mk('cs', 'study_3/base_rate_without_a_recommendation/focal/pct', 'f1')}% with no recommendation)",
         _wa('study4-supplemental')],
        ["S1 to S4", "Fixed tables, a warning and a comparison table, people in the models' role",
         "People followed the recommendation; in the models' role, they chose the top-ranked product more often than "
         "the models", _wa('study4-supplemental')],
    ]
    return md_table(["Study", "Design", "Key Finding", "Web Appendix"], rows,
                    "Overview of Studies and Results", ["l", "l", "l", "l"], label="tests",
                    widths=[6, 31, 47, 16],
                    note="Points are percentage points. The effect and the equity are defined, with their signs, in "
                         "the conceptual development.")


MEASURE_TABLES_FILE = PKG / "exhibits/results/measure_tables.md"
MEASURE_TABLE_NAMES = ["ms2_names_prices", "ms2_attributes", "ms2_requests", "ms2_claude_share", "ms2_claude_rating",
                     "ms2_reliability", "sp_by_model", "clar_by_model", "ms2_all_share", "ms2_open_models"]


def _measure_table(name):
    """The caption's first sentence becomes the
    title and the rest of the caption joins the note."""
    text = MEASURE_TABLES_FILE.read_text(encoding="utf-8")
    block = text.split(f"\n## {name}\n", 1)[1].split("\n## ", 1)[0]
    caption, note, lines = "", "", []
    for line in block.strip().split("\n"):
        if line.startswith("Caption:"):
            caption = line[len("Caption:"):].strip()
        elif line.startswith("Notes:"):
            note = line[len("Notes:"):].strip()
        elif line.startswith("|"):
            lines.append(line)
    header = [c.strip() for c in lines[0].strip().strip("|").split("|")]
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]]
    cut = min((i for i in (caption.find(". "), caption.find(": ")) if i >= 0), default=len(caption))
    title, rest = caption[:cut], caption[cut + 2:]
    rest = rest[:1].upper() + rest[1:]
    study = "Study 1b" if name.startswith(("sp_", "clar_")) else "Study 2b"
    title = f"{study}: {title.rstrip('.')}"
    note = " ".join(x for x in (rest.strip(), note) if x) or None
    if study == "Study 1b":
        def top(s):
            return (s.replace("highest-utility product", "top-ranked product").replace("the optimal product",
                    "the top-ranked product").replace("optimal product", "top-ranked product"))
        header, rows, note = [top(h) for h in header], [[top(c) for c in r] for r in rows], top(note) if note else note
    widths = {"ms2_requests": [14, 20, 21, 22, 23]}.get(name)  # 'Smartphones' needs its own width
    return md_table(header, rows, title, ["l"] * len(header), note=note, label=name.replace("_", "-"), widths=widths)


def _harness_name(key):
    return NAMES.get(key, key)


def _per_model_rows(path):
    import csv
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _pm_cell(r, with_ci=False):
    if r is None or r.get("not_estimable"):
        return "not estimable"
    est = n(float(r["estimate_pp"]), 1)
    return f"{est} ({n(float(r['ci95_low_pp']), 1)}, {n(float(r['ci95_high_pp']), 1)})" if with_ci else est


def store_per_model():
    """Study 1c: each model's effect of the fictitious name in the plain listing with its 95% CI, and its change from
    the plain listing in each of the 15 other conditions (results/harness/all-models/per_model.csv), as two tables. Kimi Linear 48B is reported apart, in the note."""
    rows = _per_model_rows(PKG / "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv")
    get = {(r["model"], r["level"]): r for r in rows}
    models = sorted({r["model"] for r in rows}, key=lambda m: _harness_name(m).lower())
    first = ["plain-info", "feed-openai", "feed-openai-2025", "feed-google", "schema-org"]
    second = ["sponsored-familiar", "sponsored-best", "position-first", "position-middle", "position-last",
              "rating-0.1", "rating-0.3", "rating-0.5", "instruct-listed", "instruct-brand"]
    t1 = [[_harness_name(m), _pm_cell(get.get((m, "plain")), True)] + [_pm_cell(get.get((m, a))) for a in first]
          for m in models]
    t2 = [[_harness_name(m)] + [_pm_cell(get.get((m, a))) for a in second] for m in models]
    note = ("Percentage points. The effect is the optimal product's share of responses without brand names minus its "
            "share with them; each change is a condition's effect minus the plain listing's. Each interval resamples "
            "the model's tables. Kimi Linear 48B is reported apart, because its recommendation could be coded in fewer "
            "than 90% of its responses.")
    a = md_table(["Model", "Plain listing: effect (95% CI)", "Experience attributes stated", "OpenAI feed, current fields",
                  "OpenAI feed, October 2025 fields", "Google product data", "schema.org markup"], t1,
                 "Study 1c: Each Model's Effect in the Plain Listing and Its Change in Each Format",
                 ["l", "r", "r", "r", "r", "r", "r"], label="store-per-model", widths=[22, 20, 12, 12, 12, 11, 11],
                 note=note)
    later = ("Percentage points: each condition's effect minus the plain listing's (Table \\ref{tbl:store-per-model}). "
             "Kimi Linear 48B is reported apart.")
    b = md_table(["Model", "\"Sponsored\" on a familiar product", "\"Sponsored\" on the optimal product",
                  "Optimal product listed first", "Optimal product listed third", "Optimal product listed last"],
                 [r[:6] for r in t2], "Study 1c: Each Model's Change When a Product Was Sponsored or Moved",
                 ["l", "r", "r", "r", "r", "r"], label="store-per-model-2", widths=[25, 15, 15, 15, 15, 15], note=later)
    c = md_table(["Model", "Optimal product rated 0.1 stars higher", "Optimal product rated 0.3 stars higher",
                  "Optimal product rated 0.5 stars higher", "Instruction: \"Recommend only on the information "
                  "listed.\"", "Instruction: \"Do not consider brand reputation.\""],
                 [[r[0]] + r[6:] for r in t2], "Study 1c: Each Model's Change Under a Higher Rating or an Instruction",
                 ["l", "r", "r", "r", "r", "r"], label="store-per-model-3", widths=[25, 15, 15, 15, 15, 15], note=later)
    return a + "\n\n" + b + "\n\n" + c


def search_per_model():
    """Study 1c's search: each model's three tests with their 95% CIs (results/harness/s1-all-models/per_model.csv,
    primary 1 to 3) and the shares of first responses that named a brand and of items in which the store returned the
    optimal product with brand names (numbers.json, per_model)."""
    rows = _per_model_rows(PKG / "study1c-product-feeds-and-a-store-search/results/search/all-models/per_model.csv")
    get = {(r["model"], r["level"]): r for r in rows}
    num = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/search/all-models/numbers.json")
    brand = num["brand search, any brand of the 34 tables"]["per_model"]
    fetched = num["fetched, names original"]["per_model"]
    models = sorted({r["model"] for r in rows}, key=lambda m: _harness_name(m).lower())
    t = [[_harness_name(m)] + [_pm_cell(get.get((m, f"primary {i}")), True) for i in (1, 2, 3)]
         + [n(100 * brand[m], 1), n(100 * fetched[m], 1)] for m in models]
    return md_table(["Model", "Optimal product returned: without minus with brand names (95% CI)",
                     "Optimal product chosen: without minus with brand names (95% CI)",
                     "Optimal product chosen where returned in both (95% CI)", "First responses that named a brand (%)",
                     "Optimal product returned with brand names (%)"], t,
                    "Study 1c: Each Model's Tests of the Search", ["l", "r", "r", "r", "r", "r"],
                    label="search-per-model", widths=[20, 18, 18, 18, 13, 13],
                    note="Percentage points for the three tests, each interval resampling the model's tables. Kimi "
                         "Linear 48B is reported apart, because its recommendation could be coded in fewer than 90% "
                         "of its responses.")


def rt_tones():
    """Study 2a's review pages over every model that answered: the effect at each tone, its change from no pages, the familiar names' gain, and the decline shares."""
    rt = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/numbers.json")
    g, d, i = rt["name gap g(e)"], rt["change D(e) = g(e) - g(none)"], rt["familiar gain I(e)"]
    dec = rt["declines"]["mean of the models' shares by arm and name version"]

    def pp(node, holm=False):
        iv = node["interval"]
        s = f"{n(100 * node['pooled'], 1)} ({n(100 * iv['low95'], 1)}, {n(100 * iv['high95'], 1)})"
        return s + (f", Holm P {_pv(node['holm'])}" if holm else "")

    rows = []
    for tone, label in [("none", "No pages"), ("positive", "Positive"), ("mixed", "Mixed"), ("negative", "Negative")]:
        rows.append([label, pp(g[tone]), "" if tone == "none" else pp(d[tone], True),
                     "" if tone == "none" else pp(i[tone], True),
                     f"{n(100 * dec[tone]['hidden'], 1)} / {n(100 * dec[tone]['original'], 1)} / "
                     f"{n(100 * dec[tone]['crossed'], 1)}"])
    return md_table(["Review pages", "Effect of the fictitious name (95% CI)", "Change from no pages (95% CI)",
                     "Familiar minus fictitious name, change in share with the pages (95% CI)", "Declines, % (without names / with / swapped)"],
                    rows, "Study 2a: Effect With Review Pages", ["l", "r", "r", "r", "r"],
                    label="rt-tones", widths=[12, 22, 22, 22, 22],
                    note="In percentage points, with intervals from a bootstrap over tables and models; the six "
                         "contrasts of columns 3 and 4 are corrected by Holm's method as one family. A decline is a response that recommended no product; the "
                         "declines are the mean of the models' shares, reported without a test.")


EX_CODERS = [("gemma31b", "Gemma 4 31B (Google)"), ("gptoss120b", "gpt-oss 120B (OpenAI)"),
             ("olmo31-32b", "OLMo 3.1 32B (Allen AI)"), ("qwen35-122b-fp8", "Qwen 3.5 122B (Alibaba)")]


def ex_coders():
    """Study 2a's reasons under each coder: the mean over models of the
    share of explanations that give a brand as a reason on Study 1a's tables, the same without the coder's own model, the
    two differences, and the coder's kappa with the reference coding of 200 explanations (CHECKS.json)."""
    ex = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/numbers.json")
    chk = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/CHECKS.json")

    def pc(d, with_p=False):
        s = f"{n(100 * d['est'], 1)} ({n(100 * d['lo'], 1)}, {n(100 * d['hi'], 1)})"
        return s + (f", P {_pv(d['p'])}" if with_p else "")

    rows = []
    for key, label in EX_CODERS:
        ov = ex["shares"][key]["overall"]
        rows.append([label, f"{chk[key]['on_the_200_vs_reference']['brand_any']['kappa']:.2f}".lstrip("0"),
                     pc(ov["dom2"]), pc(ex["own_left_out"][key]["dom2"]),
                     pc(ov["original minus crossed"], True), pc(ov["info0 minus info1"], True)])
    return md_table(["Coder", "Kappa with the reference", "Share giving a brand as a reason (%)",
                     "The same without the coder's own model (%)", "Fictitious name on the optimal product minus names "
                     "swapped (points)", "Without minus with the experience attributes stated (points)"], rows,
                    "Study 2a: Brand Reasons in Explanations, by Coder", ["l", "r", "r", "r", "r", "r"],
                    label="ex-coders", widths=[18, 10, 16, 16, 20, 20],
                    note="Explanations of the responses that did not choose the optimal product with brand names, on "
                         "the tables of Study 1a. Each share is the mean over models of each model's share, with a 95% "
                         "interval from a bootstrap over models and tables.")


B5_EQUITIES = [("primary_olmo2_7b_instruct", "OLMo 2 7B Instruct"),
               ("olmo2_32b_instruct", "OLMo 2 32B Instruct"),
               ("open_models_mean", "The open models' mean equity")]
B5_MEASURES = [("net_sentiment", "Net tone"), ("recommendation_share", "Recommending share"),
               ("promotional_share", "Promotional share")]


def b5_table():
    a = _numbers_of("b5")
    m = a["versions"]["majority"]
    rows = []
    for key, label in B5_EQUITIES:
        cells = []
        for mk, _ in B5_MEASURES:
            r = m[key][mk]
            cells.append(f"{_r(r['estimate'])} ({_r(r['ci95'][0])}, {_r(r['ci95'][1])}), Holm P {_pv(r['p_holm'])}")
        rows.append([label] + cells)
    wo = m["promotional_share_without_common_word_brands"]
    jc = m["judges_promotional_share_check"]
    rows.append(["Checks", "", "", ""])
    rows.append(["OLMo 2 7B Instruct, without the ten brands whose names are common words", "", "",
                 f"{_r(wo['estimate'])} ({_r(wo['ci95'][0])}, {_r(wo['ci95'][1])}), P {_pv(wo['p_two_sided'])}"])
    rows.append(["OLMo 2 7B Instruct, the coding models' own promotional labels", "", "",
                 f"{_r(jc['estimate'])} ({_r(jc['ci95'][0])}, {_r(jc['ci95'][1])}), P {_pv(jc['p_two_sided'])}"])

    def two(ex):
        return [f"{_r(ex[k]['estimate'])} ({_r(ex[k]['ci95'][0])}, {_r(ex[k]['ci95'][1])}), P {_pv(ex[k]['p_two_sided'])}"
                for k in ("net_sentiment", "recommendation_share")]

    # Amendment 7, item 4: the exploratory row added after the results were read, in the version that fits its reason
    # (without the brands with fewer than ten passages in the brand's sense) beside the version first reported
    rows.append(["OLMo 2 7B Instruct, without the brands with fewer than ten passages in the brand's sense"]
                + two(m["exploratory_without_brands_with_fewer_than_ten_sense_windows"]) + [""])
    rows.append(["OLMo 2 7B Instruct, without the ten brands whose names are common words"]
                + two(m["exploratory_without_common_word_brands"]) + [""])
    return md_table(["Equity", "Net tone", "Recommending share", "Promotional share"], rows,
                    "Study 3b: Training Text and Brand Equity in OLMo 2", ["l", "r", "r", "r"], label="b5", widths=[34, 22, 22, 22],
                    note="Spearman correlations across brands, partial on the log of the brand's estimated "
                         "mentions, with 95% intervals from 10,000 bootstrap draws over brands; the three measures of "
                         "each equity are Holm-corrected. The promotional share is from a published classifier's labels "
                         "of whole documents [@wettig2025organize]; the others are from the majority of three "
                         "coding models on 200 passages around each brand's name. These correlations are not causal "
                         "estimates.")


def _r(x):
    """A correlation with no zero before the point, as in the main text ('.18', '−.40')."""
    s = f"{x:.2f}"
    s = s.replace("-0.", "−.").replace("0.", ".", 1) if s.lstrip("-").startswith("0.") else s.replace("-", "−")
    return s


HET_RUNS = [
    ("Study 1b: the effect of the fictitious name", "study1b"),
    ("Study 1b: the effect under requests that consumers typed", "study1b-requests-penalty"),
    ("Study 1c: the effect in the plain listing", "study1c-store-gap-plain"),
    ("Study 1c: change under the brand instruction", "study1c-store-D-instruct-brand"),
    ("Study 1c: the effect at the choice after a search", "study1c-search-primary2"),
    ("Study 1c: the same, where the store returned the optimal product in both versions", "study1c-search-primary3"),
    ("Study 2a: change with the experience attributes stated", "study2a"),
    ("Study 2a: independent testing stated alone against none", "study2b-lab-minus-none"),
    ("Study 2b: the price discount that offsets the fictitious name", "study2c"),
]
HET_MODERATORS = [("size (log10 total parameters)", "Size (per tenfold parameters)"),
                  ("release date (years)", "Release date (per year)"),
                  ("open against closed weights", "Open against closed weights"),
                  ("reasoning on against off", "Reasoning on against off"),
                  ("chat-tuned against base", "Chat-tuned against base"),
                  ("developer", "Developer (joint test)")]


def _het(run):
    return paper_names.read(PKG / f"how-the-models-differed/results/{run}/numbers.json")


def het_spread():
    rows = []
    for label, run in HET_RUNS:
        r = _het(run)["result"]
        re_ = r["random_effects"]
        if r.get("models_in_predicted_direction") is not None:
            direction = f"{r['models_in_predicted_direction']} of {r['models']}"
        else:  # a two-sided test: the models below zero, the side that a reduction lies on
            direction = f"{r['models_below_zero']} of {r['models']} below zero"
        rows.append([label, str(r["models"]), direction, str(r["models_interval_excludes_zero"]),
                     n(re_["tau"], 1), f"{100 * re_['i2']:.0f}", _pv(re_["q_p_value"]),
                     ci(re_["prediction_interval_95"], 1)])
    return md_table(["Study and estimate", "Models", "In the predicted direction", "Interval excludes zero",
                     "SD between models", "I² (%)", "P, Q test", "95% prediction interval"], rows,
                    "How Much Each Study's Effect Varied Between Models",
                    ["l", "r", "r", "r", "r", "r", "r", "r"], label="het-spread",
                    widths=[30, 8, 12, 10, 10, 7, 9, 14],
                    note="Each model's estimate comes with an interval from resampling that model's tables. The "
                         "standard deviation between models (in percentage points, except for Study 2b, where the "
                         "unit is the percentage of the price) is estimated by restricted maximum likelihood "
                         "[@veroniki2016methods; @langan2019comparison]; the prediction interval is for a model not "
                         "in the sample. The estimate over the models is each study's own bootstrap estimate, in the "
                         "main text.")


def het_moderators():
    rows = []
    for label, run in HET_RUNS:
        mods = _het(run)["result"]["moderators"]
        for key, name in HET_MODERATORS:
            m = mods.get(key)
            if m is None:
                continue
            if not m.get("estimable"):
                rows.append([label, name, "not estimable", m.get("reason", ""), ""])
                continue
            if key == "developer":
                est = f"χ²({m['df']}) = {m['wald_chi2']:.2f}"
            else:
                est = f"{n(m['coefficient'], 1)} ({ci(m['ci95'], 1)})"
            rows.append([label, name, est, _pv(m["p_two_sided"]), _pv(m["holm"])])
    return md_table(["Study and estimate", "Feature of the model", "Coefficient (95% CI)", "P", "P after Holm"], rows,
                    "Approximate Tests of the Features That Predict Each Study's Effect",
                    ["l", "l", "r", "r", "r"], label="het-moderators", widths=[30, 22, 22, 12, 12],
                    note="Meta-regressions of the models' estimates on one feature at a time, with the spread "
                         "between models estimated by restricted maximum likelihood. The tests treat the models as "
                         "independent, although they answered the same tables, so they are approximate. Holm's "
                         "method corrects the features within each study and estimate. A feature with one value in "
                         "a study cannot be estimated there.")


import ast
import csv
import json
from pathlib import Path

# ---------------------------------------------------------------- shared readers


def _corpus_names():
    """Model key -> printed name, from model_names.json beside this file (the names that the paper prints)."""
    return json.loads((CODE / "model_names.json").read_text(encoding="utf-8"))


NAMES = _corpus_names()
CHARS = {r["key"]: r for r in csv.DictReader(
    (PKG / "models/model_characteristics.csv").open(encoding="utf-8"))}
S1P = paper_names.later(PKG / "study1b-64-models-on-34-tables/results/pooled/numbers.json")
RRA = paper_names.later(PKG / "study1b-64-models-on-34-tables/results/requests/all-models/numbers.json")


def _reasoning(key):
    """What the coding records is
    whether the run requested extended thinking (the corpus's thinking flag, or an open model's chat-template switch),
    not whether the model reasoned: without the request, Gemini 2.5 Pro still reasoned within 128 tokens and Gemini 3
    Flash at the minimal level (harness/core.py), and DeepSeek R1 reasons in every response."""
    r = CHARS.get(key) or {}
    t = (r.get("thinking") or "").lower()
    if t == "on" or key.lower().endswith("-thinking"):
        return "requested"
    if t == "off" or '"enable_thinking": false' in t:
        return "not requested"
    return "default"


def _thinking_label(key):
    """What Table s1b-models prints: the test's coding, and 'low effort' where the run set the lowest reasoning effort
    (gpt-oss), which the test leaves out with the developer's defaults (second read of N, 22 November 2026)."""
    t = ((CHARS.get(key) or {}).get("thinking") or "").lower()
    return "low effort" if '"reasoning_effort": "low"' in t else _reasoning(key)


def _released(key):
    d = (CHARS.get(key) or {}).get("release_date") or ""
    return d[:7] if d else "not recorded"


def _pvh(p):
    """A Holm-corrected P for these tables: as _pv, but a value just below .05 keeps a fourth decimal, so that it does
    not print as .050 beside a column that counts it as below .05."""
    return f"{p:.4f}".lstrip("0") if 0.0495 <= p < 0.05 else _pv(p)


def _params(key):
    p = (CHARS.get(key) or {}).get("params_total") or ""
    return n(float(p) / 1e9, 1) if p else "not public"


# ---------------------------------------------------------------- Web Appendix C: Study 1b's models


def s1b_models():
    """Every model of Study 1b with the features that the tests of Table het-moderators use and its own effect."""
    rows = []
    for m in sorted(S1P["per_model"], key=lambda m: (-m["gap_pp"], NAMES[m["model"]])):
        k = m["model"]
        rows.append([NAMES[k], m["developer"], "open" if m["open_weights"] else "closed", _released(k), _params(k),
                     _thinking_label(k), n(m["gap_pp"], 1), ci([m["ci95_low_pp"], m["ci95_high_pp"]], 1)])
    return md_table(["Model", "Developer", "Weights", "Released", "Parameters (billions)", "Extended thinking",
                     "Effect (points)", "95% CI"], rows,
                    "Study 1b: Features and Effect of Each Model Setting",
                    ["l", "l", "l", "l", "r", "l", "r", "r"], label="s1b-models",
                    widths=[26, 11, 8, 9, 10, 11, 9, 14],
                    note="Effect: the share of responses that chose the top-ranked product without brand names "
                         "minus the share with them, in percentage points, over the 34 tables, with an interval from "
                         "resampling that model's tables. Released: for a model with closed weights, the month in which "
                         "its developer released the identifier that we called (from its changelog or models interface; "
                         "for Gemini models the stable identifier, after its preview versions); for a model with open "
                         "weights, the month in which the developer's repository of those weights was created. "
                         "Parameters: the total count in the model's weights, which are published only for models with "
                         "open weights. Extended thinking: whether we requested it, low effort where we set the lowest "
                         "reasoning effort, and default where we used the developer's default; in the test of Table "
                         "\\ref{tbl:het-moderators-all}, we compare requested with not requested and leave out the "
                         "others. Without the request, some models still reasoned: Gemini 2.5 Pro within a budget of "
                         "128 tokens, Gemini 3 Flash at the minimal level, GPT-5 mini at its default effort, and "
                         "DeepSeek R1 in every response. Models are ordered by their effect.")


def s1bm(spec):
    """'<rank>/<field>': the model at that rank of Study 1b's effect, from the top ('top1') or the bottom ('bottom1');
    field name, gap, lo or hi."""
    rank, field = spec.split("/")
    order = sorted(S1P["per_model"], key=lambda m: (-m["gap_pp"], NAMES[m["model"]]))  # as Table s1b-models orders them
    i = int(rank[3:]) - 1 if rank.startswith("top") else -int(rank[6:])
    m = order[i]
    return {"name": NAMES[m["model"]], "gap": n(m["gap_pp"], 1), "lo": n(m["ci95_low_pp"], 1),
            "hi": n(m["ci95_high_pp"], 1)}[field]


def modelunit(spec):
    """Counts of models on one unit, a model as released, with the settings named apart.
    'study1b/<key>' from Study 1b's per-model file: models (as released), open, closed, developers, settings (each with
    its own estimate: 68), both_settings (models run with and without extended thinking), both_settings_word (that
    count in words) and both_settings_names; 'all/<models|open|closed|developers>' from the paper's scale
    (results/scale/numbers.json), which counts each model once."""
    group, key = spec.split("/")
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    if group == "all":
        sc = paper_names.read(PKG / "models/answers-and-models-counted.json")
        vals = {"models": sc["distinct_models"], "open": sc["distinct_models_open_weights"],
                "closed": sc["distinct_models"] - sc["distinct_models_open_weights"],
                "developers": sc["distinct_developers"]}
        return f"{vals[key]:,}"
    pm = S1P["per_model"]
    keys = {m["model"] for m in pm}
    # a model appears twice when its setting with extended thinking (key '<model>-thinking') sits beside the same model
    # without it; a model that only ran with thinking (Gemini 3.1 Pro) appears once
    both = sorted(k[: -len("-thinking")] for k in keys if k.endswith("-thinking") and k[: -len("-thinking")] in keys)
    released = [m for m in pm if m["model"][: -len("-thinking")] not in both or not m["model"].endswith("-thinking")]
    vals = {"models": len(released), "open": sum(1 for m in released if m["open_weights"]),
            "closed": sum(1 for m in released if not m["open_weights"]), "developers": len({m["developer"] for m in pm}),
            "settings": len(pm), "both_settings": len(both)}
    if key == "both_settings_word":
        return words[len(both)] if len(both) < 10 else str(len(both))
    if key == "both_settings_names":
        names = sorted((NAMES[k] for k in both), key=str.lower)
        return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else "".join(names)
    return f"{vals[key]:,}"


REAL_COMPANY_TABLES = {"sr_laptops_02", "sr_laptops_03", "sr_earbuds_02"}  # as INVENTED_REAL in web-appendix-analyses/each-piece-of-information-alone/code/analyze_attr.py


def s1btop(key):
    """Study 1b's 34 tables: tables (34), top_fictitious (tables whose top-ranked product, the one with the
    highest score, has one of the fictitious names that replaced the brands coded low, experiment/assortments.py
    LOW_FAM_BRAND_REPLACEMENTS), real_company (of those, the tables whose fictitious name also belongs to a small real
    company: Novatech, Primebook and Sonance), and other_fictitious (tables in which another product also has one)."""
    from experiment.assortments import LOW_FAM_BRAND_REPLACEMENTS
    from experiment.conditions import compute_utility_scores
    fictitious = set(LOW_FAM_BRAND_REPLACEMENTS.values())
    tabs = list(_assortments())
    top = {}
    for a in tabs:
        s = compute_utility_scores(a)
        opt = [p for p in a["products"] if p.get("is_optimal")]
        if len(opt) != 1 or opt[0]["letter"] != max(s, key=s.get):
            raise ValueError(f"s1btop: {a['id']} has no single top-ranked product that is marked optimal")
        top[a["id"]] = opt[0]["brand"] in fictitious
    vals = {"tables": len(tabs), "top_fictitious": sum(top.values()),
            "real_company": sum(1 for t, f in top.items() if f and t in REAL_COMPANY_TABLES),
            "other_fictitious": sum(1 for a in tabs if any(p["brand"] in fictitious for p in a["products"]
                                                           if not p.get("is_optimal")))}
    return str(vals[key])


def auper(spec):
    """Study 3b's brand audit by model (results/audit/per-model-all.csv, test 1, Table H3 of HETEROGENEITY-all.md):
    '<group>/<key>' with group claude, gpt, open or all, and key total (models with at least one estimable measure),
    above (models with at least one of the six measures' slopes whose 95% interval, from the model's own bootstrap over
    tables and not corrected, lies above zero), below (the same below zero), above_word or below_word (in words under
    ten), or above_names (the models above zero, by name)."""
    group, key = spec.split("/")
    rows = list(csv.DictReader(open(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", encoding="utf-8")))
    gmap = {"claude": ("claude",), "gpt": ("codex",), "open": ("open",), "all": ("claude", "codex", "open")}
    by = {}
    for r in rows:
        if r["test"] != "test1" or r["group"] not in gmap[group] or r["lo95"] in ("", None):
            continue
        by.setdefault(r["model"], []).append((float(r["lo95"]), float(r["hi95"])))
    above = sorted(m for m, iv in by.items() if any(lo > 0 for lo, _ in iv))
    below = sorted(m for m, iv in by.items() if any(hi < 0 for _, hi in iv))
    # after Holm's correction over each model's own estimable measures (the referees of D3, finding 8): the bootstrap P
    # values of results/audit/numbers-all.json (exploratory/test1_by_model; a measure that varies in fewer than three
    # of the model's tables is left out, as Table H3 leaves it out)
    t1 = paper_names.read(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json")["exploratory"]["test1_by_model"]
    holm_above, holm_below = [], []
    for m in by:
        comps = [v for v in t1.get(m, {}).values() if (v.get("clusters_varying") or 0) >= 3 and v.get("p") is not None]
        order = sorted(range(len(comps)), key=lambda i: comps[i]["p"])
        adj, run = [1.0] * len(comps), 0.0
        for rank, i in enumerate(order):
            run = max(run, min(1.0, (len(comps) - rank) * comps[i]["p"]))
            adj[i] = run
        if any(a < 0.05 and v["est"] > 0 for a, v in zip(adj, comps)):
            holm_above.append(m)
        if any(a < 0.05 and v["est"] < 0 for a, v in zip(adj, comps)):
            holm_below.append(m)
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    vals = {"total": len(by), "above": len(above), "below": len(below), "holm_above": len(holm_above),
            "holm_below": len(holm_below)}
    if key.endswith("_word"):
        k = vals[key[:-5]]
        return words[k] if k < 10 else str(k)
    if key in ("above_names", "holm_above_names", "holm_below_names"):
        ms = {"above_names": above, "holm_above_names": holm_above, "holm_below_names": holm_below}[key]
        names = sorted((NAMES.get(m, m) for m in ms), key=str.lower)
        return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else "".join(names)
    return str(vals[key])


def aucount(spec):
    """Study 3b's machine brand audit, its models by group, on one rule (results/audit/numbers-all.json):
    '<group>/<key>' with group claude, gpt, open or all, and key answered (the models that answered the audit's
    questions, each on the questions it was asked) or equity, with _word for a count in words under ten; 'left/names' names the models left out of the tests of equity."""
    group, key = spec.split("/")
    au = paper_names.read(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json")
    if group == "left" and key == "names":
        names = sorted((NAMES.get(m, m) for m in au["models"] if m not in au["models_with_gap"]), key=str.lower)
        return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else "".join(names)
    want = {"claude": ("claude",), "gpt": ("codex",), "open": ("open",), "all": ("claude", "codex", "open")}[group]
    base = key[:-5] if key.endswith("_word") else key
    models = {"answered": au["models"], "equity": au["models_with_gap"]}[base]
    k = sum(1 for m in models if au["groups"][m] in want)
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    return (words[k] if k < 10 else str(k)) if key.endswith("_word") else str(k)


def s1b_lodo():
    """Study 1b's effect with one developer's models left out at a time."""
    lodo = S1P["leave_one_developer_out"]
    rows = []
    for dev, v in sorted(lodo.items(), key=lambda kv: (-kv[1]["models_left_out"], kv[0])):
        rows.append([dev, str(v["models_left_out"]), str(v["models"]), n(v["gap_pp"], 1), ci(v["ci95_pp"], 1),
                     _pv(v["p_two_sided"])])
    pooled = S1P["pooled"]
    rows.append(["None (every model)", "0", str(pooled["models"]), n(pooled["gap_pp"], 1), ci(pooled["ci95_pp"], 1),
                 _pv(pooled["p_two_sided"])])
    return md_table(["Developer left out", "Models left out", "Models kept", "Effect (points)", "95% CI", "P"], rows,
                    "Study 1b: The Effect of the Fictitious Name With One Developer's Models Left Out",
                    ["l", "r", "r", "r", "r", "r"], label="s1b-lodo", widths=[24, 12, 12, 14, 18, 10],
                    note="Each row repeats the analysis of Study 1b without the models of one developer: a bootstrap "
                         "that resamples tables and models, 10,000 draws. A P value of zero in the bootstrap is shown "
                         "as below .001.")


def s1blodo(spec):
    """'min' or 'max' with '/developer', '/gap' or '/left': the row of the smallest or largest effect."""
    which, field = spec.split("/")
    lodo = S1P["leave_one_developer_out"]
    dev = (min if which == "min" else max)(lodo, key=lambda d: lodo[d]["gap_pp"])
    return {"developer": dev, "gap": n(lodo[dev]["gap_pp"], 1), "left": str(lodo[dev]["models_left_out"])}[field]


# ---------------------------------------------------------------- Web Appendix C: every study's spread

# Every run of results/heterogeneity that the paper reports, in the paper's terms. The store's 15 changes are in
# Web Appendix K's table (store_spread). The further-attributes runs (study2b-attr-*) are left out because the paper
# does not report that test.
PIECES = [("warranty", "the warranty"), ("failure", "the failure or return rate"),
          ("market", "the time on the market"), ("lab", "the statement about independent testing"),
          ("returns", "the free return")]
AUDIT = [("recognition", "recognition"), ("salience", "salience"), ("typicality", "typicality"), ("tone", "tone"),
         ("quality", "inferred quality"), ("credibility", "credibility")]
CODERS = [("gemma31b", "Gemma 4 31B"), ("gptoss120b", "gpt-oss 120B"), ("olmo31-32b", "OLMo 3.1 32B"),
          ("qwen35-122b-fp8", "Qwen 3.5 122B")]
HET_RUNS_ALL = (
    [("Study 1b: the effect of the fictitious name", "study1b"),
     ("Study 1b, typed requests: the effect of the fictitious name", "study1b-requests-penalty"),
     ("Study 1b, typed requests: names swapped minus without brand names", "study1b-requests-premium"),
     ("Study 1c: the effect in the plain listing", "study1c-store-gap-plain"),
     ("Study 1c: the effect at the choice after a search", "study1c-search-primary2"),
     ("Study 1c: the same, where the store returned the optimal product in both versions", "study1c-search-primary3"),
     ("Study 2a, experience attributes stated: change in the effect", "study2a"),
     ("Study 2a, review pages: the effect without pages", "study2a-retrieval-gap-none")]
    + [(f"Study 2a, review pages: change with {tone} pages", f"study2a-retrieval-six-D-{tone}")
       for tone in ("positive", "mixed", "negative")]
    + [(f"Study 2a, review pages: gain of a familiar name over the fictitious name from {tone} pages",
        f"study2a-retrieval-six-I-{tone}") for tone in ("positive", "mixed", "negative")]
    + [(f"Study 2a, reasons: share of explanations that gave a brand as a reason, coder {name}", f"study2e-{key}")
       for key, name in CODERS]
    + [(f"Study 2a, one piece alone: {label} alone minus no information", f"study2b-{key}-minus-none")
       for key, label in PIECES]
    + [(f"Study 2a, one piece alone: {label} alone minus all five pieces", f"study2b-{key}-minus-all-five")
       for key, label in PIECES]
    + [("Study 2b: the fictitious product's share minus the identical familiar product's at the same price",
        "study2c")]
    + [("Attribute study: the effect with no information", "study2b-attr-gap-none"),
       ("Attribute study: familiar names on the other products", "study2b-attr-2x2-others"),
       ("Attribute study: a familiar name on the optimal product", "study2b-attr-2x2-own"),
       ("Attribute study: the interaction of the two names", "study2b-attr-2x2-interaction")]
    + [(f"Study 3b, machine brand audit: slope of equity on {label}, all brands", f"study2d-test1-{key}")
       for key, label in AUDIT]
    + [(f"Study 3b, machine brand audit: slope of the difference on {label}, the same product under two names",
        f"study2d-test2-{key}") for key, label in AUDIT]
    + [("Study 3b, machine brand audit: slope of consideration on salience", "study2d-h6b-recall")]
)


# A run whose estimate is a share (0 to 1) is printed in percentage points; the brand audit's slopes keep two decimals; the
# shares of explanations that gave a brand as a reason have no direction to count.
SCALE = {"study2d-h6b-recall": 100.0}
SHARE_RUNS = {f"study2e-{key}" for key, _ in CODERS}


def _dec(run):
    return 2 if run.startswith("study2d") else 1


def _spread_row(label, run):
    r = _het(run)["result"]
    re_ = r["random_effects"]
    s = SCALE.get(run, 1.0)
    if run in SHARE_RUNS:
        direction = "none predicted"
    elif r.get("models_in_predicted_direction") is not None:
        direction = f"{r['models_in_predicted_direction']} of {r['models']}"
    else:
        direction = f"{r['models_below_zero']} of {r['models']} below zero"
    return [label, str(r["models"]), direction, str(r["models_interval_excludes_zero"]),
            n(s * re_["tau"], _dec(run)), f"{100 * re_['i2']:.0f}", _pv(re_["q_p_value"]),
            ci([s * x for x in re_["prediction_interval_95"]], _dec(run))]


SPREAD_HEADER = ["Study and estimate", "Models", "In the predicted direction (or below zero)", "Interval excludes zero",
                 "SD between models", "I² (%)", "P, Q test", "95% prediction interval"]
SPREAD_CORE = ("Each model's interval is obtained by resampling that model's tables. The standard "
               "deviation between models, the spread of the models' "
               "true effects, is estimated by restricted maximum likelihood [@veroniki2016methods; "
               "@langan2019comparison]. The prediction interval is the range in which the true effect of a model not "
               "in the sample would fall, centered on the average of the models' estimates weighted by their "
               "precision. Where no direction was predicted, the models below zero appear in the third "
               "column.")
SPREAD_NOTE = (SPREAD_CORE + " For the typed requests of Study 1b, a model's requests and tables are resampled for "
               "its interval. Units: percentage points, except in Study 3b's machine brand audit, where each slope is in percentage points "
               "of equity (or of consideration share) per standard deviation of the measure. The shares of "
               "explanations that gave a brand as a reason have no predicted direction, and their prediction "
               "intervals come from a normal approximation that can extend below zero, which a share cannot. We "
               "report no estimate over the models here: each study's estimate comes from its own bootstrap, in the "
               "main text. The changes in Study 1c's store conditions are in Web Appendix " + _wa("study1c-store") + ".")


def het_spread_all():
    rows = [_spread_row(label, run) for label, run in HET_RUNS_ALL]
    return md_table(SPREAD_HEADER, rows,
                    "Variation of Each Estimate Across Models", ["l", "r", "r", "r", "r", "r", "r", "r"],
                    label="het-spread-all", widths=[34, 7, 11, 9, 9, 6, 8, 14], note=SPREAD_NOTE)


def _run_models(run):
    """The models that entered a heterogeneity run, from its input file and filters (numbers.json, args)."""
    a = _het(run)["args"]
    path = Path(a["input"])
    path = path if path.is_absolute() else REPO / path
    if not path.exists() and "jmr-2026" in path.parts:  # an absolute path from the computer that ran the analysis
        path = REPO.joinpath(*path.parts[path.parts.index("jmr-2026"):])
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for flt in a.get("filter") or []:
        k, v = flt.split("=", 1)
        rows = [r for r in rows if r.get(k) == v]
    return sorted({r[a["model_col"]] for r in rows})


def _closed(run):
    return [m for m in _run_models(run) if CHARS.get(m, {}).get("open") != "open"]


def _closed_note():
    """Which models have closed weights in each group of rows, computed from the runs."""
    groups = {}
    for label, run in HET_RUNS_ALL:
        groups.setdefault(tuple(_closed(run)), []).append(label.split(":")[0])
    parts = []
    for closed, studies in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        names = [NAMES[m] for m in closed]
        where = ", ".join(dict.fromkeys(studies))
        who = (f"the {len(names)} models of Table \\ref{{tbl:s1b-models}} marked closed" if len(names) > 9
               else ", ".join(names[:-1]) + " and " + names[-1])
        parts.append(f"{who} ({where})")
    return "The models with closed weights are " + "; ".join(parts) + "."


def _route_note():
    """How the models ran, from the characteristics table: the closed models through their developers' interfaces,
    the open models on a university cluster except the corpus's open models, which ran through providers."""
    via = sorted(NAMES[k] for k, r in CHARS.items() if r.get("set") == "corpus" and r.get("open") == "open"
                 and k in {m["model"] for m in S1P["per_model"]})
    return ("The models with closed weights ran through their developers' interfaces. The models with open weights "
            "ran on a university computing cluster, except " + str(len(via)) + " of Study 1b's ("
            + ", ".join(via[:-1]) + " and " + via[-1] + "), which ran through providers.")


MOD_COLUMNS = [("size (log10 total parameters)", "Size"), ("release date (years)", "Release date"),
               ("open against closed weights", "Open minus closed"),
               ("reasoning on against off", "Extended thinking requested"), ("developer", "Developer")]


def _mod_cell(m, run=""):
    if m is None or not m.get("estimable"):
        return "not estimable"
    if "wald_chi2" in m:
        return f"χ²({m['df']}) = {m['wald_chi2']:.1f} ({_pvh(m['holm'])})"
    return f"{n(SCALE.get(run, 1.0) * m['coefficient'], _dec(run))} ({_pvh(m['holm'])})"


def het_moderators_all():
    rows = []
    for label, run in HET_RUNS_ALL:
        mods = _het(run)["result"]["moderators"]
        rows.append([label] + [_mod_cell(mods.get(key), run) for key, _ in MOD_COLUMNS])
    return md_table(["Study and estimate"] + [name for _, name in MOD_COLUMNS], rows,
                    "Model Features as Predictors of Each Estimate",
                    ["l", "r", "r", "r", "r", "r"], label="het-moderators-all", widths=[34, 13, 13, 13, 12, 15],
                    note="Each entry is the coefficient of a meta-regression of the models' estimates on one feature "
                         "at a time, with its P value after Holm correction in parentheses: per tenfold of total "
                         "parameters (size, models with public weights only), per year of release (models with a "
                         "recorded release date only), models with open weights minus models with closed weights, and "
                         "a request for extended thinking minus none (models whose requests set it either way only); for "
                         "the developer, the joint test over its developers. The units are those of Table "
                         "\\ref{tbl:het-spread-all}. " + _closed_note() + " " + _route_note() + " The models are "
                         "treated as "
                         "independent, although they answered the same tables, so the tests are approximate. The "
                         "features are Holm-corrected within each row only. A feature marked 'not estimable' has one "
                         "value among the row's models.")


def hetcount(spec):
    """'<feature key>' -> how many rows of HET_RUNS_ALL have that feature at Holm P below .05; 'rows' -> the rows;
    'estimable/<feature key>' -> in how many rows it could be estimated."""
    if spec == "rows":
        return str(len(HET_RUNS_ALL))
    if spec.startswith("estimable/"):
        key = spec.split("/", 1)[1]
        return str(sum(1 for _, run in HET_RUNS_ALL
                       if (_het(run)["result"]["moderators"].get(key) or {}).get("estimable")))
    return str(sum(1 for _, run in HET_RUNS_ALL
                   if ((_het(run)["result"]["moderators"].get(spec) or {}).get("holm", 1) < 0.05)))


# ---------------------------------------------------------------- Web Appendix K: the store's and the search's spread


def store_spread():
    rows = [_spread_row(label if arm == "plain" else f"Change: {label}",
                        "study1c-store-gap-plain" if arm == "plain" else f"study1c-store-D-{arm}")
            for arm, label in STORE_ARMS]
    rows += [_spread_row("The choice after a search", "study1c-search-primary2"),
             _spread_row("The choice after a search, where the store returned the optimal product in both versions",
                         "study1c-search-primary3")]
    for row, (arm, _) in zip(rows, STORE_ARMS + [("s2", ""), ("s3", "")]):
        run = {"plain": "study1c-store-gap-plain", "s2": "study1c-search-primary2",
               "s3": "study1c-search-primary3"}.get(arm, f"study1c-store-D-{arm}")
        mods = _het(run)["result"]["moderators"]
        held = [name for key, name in MOD_COLUMNS if (mods.get(key) or {}).get("holm", 1) < 0.05]
        row.append(", ".join(held) if held else "none")
    return md_table(["Condition"] + SPREAD_HEADER[1:] + ["Features with Holm P below .05"], rows,
                    "Study 1c: How Much the Effect and Each Condition's Change Varied Between Models",
                    ["l", "r", "r", "r", "r", "r", "r", "r", "l"], label="store-spread",
                    widths=[30, 6, 10, 8, 8, 5, 7, 12, 14],
                    note="In percentage points. The first row is the effect of the fictitious name in the plain "
                         "listing, and each row headed Change is that condition's effect minus the plain listing's. "
                         "The last two rows are the effect at the choice after the model's own searches. "
                         + SPREAD_CORE + " In the last column, we name the features of a model whose approximate test, "
                         "with Holm's method within that row (the tests are in Table \\ref{tbl:het-moderators-all} in "
                         "Web Appendix " + _wa("models") + "), had a P value below .05.")


# ---------------------------------------------------------------- the attribute study's spread (for its section)

ATTR_CONDITIONS = (
    [(f"{piece}-row", f"{label} as a row of every listing") for piece, label in
     (("warranty", "The warranty"), ("failure", "The failure or return rate"), ("market", "The time on the market"),
      ("lab", "Independent testing"), ("returns", "The free return"))]
    + [(f"{piece}-sentence", f"{label} as a sentence of the request") for piece, label in
       (("warranty", "The warranty"), ("failure", "The failure or return rate"), ("market", "The time on the market"),
        ("lab", "Independent testing"), ("returns", "The free return"))]
    + [("reviews-50", "50 reviews of the optimal product"), ("reviews-5000", "5,000 reviews of the optimal product"),
       ("certification", "Certification"), ("endorsement", "Expert review"), ("origin", "Country of origin"),
       ("sustainability", "Sustainability")])


def attr_spread():
    """The attribute study: how much the effect with no information and each condition's change varied between the
    models, and the row against the sentence for each piece, with the features that predicted each (as store_spread)."""
    runs = ([("The effect with no information", "study2b-attr-gap-none")]
            + [(f"Change: {label}", f"study2b-attr-arm-{key}") for key, label in ATTR_CONDITIONS]
            + [(f"Row minus sentence: {label.split(' as ')[0]}", f"study2b-attr-row-{key.split('-')[0]}")
               for key, label in ATTR_CONDITIONS[:5]])
    rows = []
    for label, run in runs:
        row = _spread_row(label, run)
        mods = _het(run)["result"]["moderators"]
        held = [name for key, name in MOD_COLUMNS if (mods.get(key) or {}).get("holm", 1) < 0.05]
        rows.append(row + [", ".join(held) if held else "none"])
    return md_table(["Condition"] + SPREAD_HEADER[1:] + ["Features with Holm P below .05"], rows,
                    "The Attribute Study: How Much the Effect and Each Condition's Change Varied Between Models",
                    ["l", "r", "r", "r", "r", "r", "r", "r", "l"], label="attr-spread",
                    widths=[30, 6, 10, 8, 8, 5, 7, 12, 14],
                    note="In percentage points. The first row is the effect of the fictitious name with no "
                         "information; each row headed Change is that condition's effect minus the effect with no "
                         "information, and each row headed Row minus sentence is a piece's change as a row of the "
                         "listing minus its change as a sentence of the request. " + SPREAD_CORE + " In the last column, "
                         "we name the features of a model whose approximate test, with Holm's method within that row "
                         "(the tests are in Table \\ref{tbl:het-moderators-all}), had a P value below .05.")


# ---------------------------------------------------------------- Web Appendix G: the typed requests over every model


def rr_models_all():
    """Each model's effect of the fictitious name under the typed requests and its swapped-names difference."""
    pen = RRA["penalty, chat-log requests (primary)"]
    pre = RRA["premium, chat-log requests"]
    holm = RRA["Holm, the secondary family"]
    rows = []
    for key in sorted(pen["per_model"], key=lambda k: (-pen["per_model"][k], NAMES[k])):
        iv, ivp = pen["per_model_interval"][key], pre["per_model_interval"][key]
        h = holm.get(f"penalty, chat-log requests, {key} (secondary contrast 1)", {}).get("holm")
        rows.append([NAMES[key], f"{pen['n_pairs_per_model'][key]:,}", n(100 * pen["per_model"][key], 1),
                     ci([100 * iv["low"], 100 * iv["high"]], 1), _pv(h) if h is not None else "",
                     n(100 * pre["per_model"][key], 1), ci([100 * ivp["low"], 100 * ivp["high"]], 1)])
    rows.append([f"Every model ({len(pen['per_model'])})", "", n(100 * pen["pooled"], 1),
                 ci([100 * pen["interval"]["low"], 100 * pen["interval"]["high"]], 1),
                 _pv(pen["interval"]["p_two_sided"]) + " (primary)", n(100 * pre["pooled"], 1),
                 ci([100 * pre["interval"]["low"], 100 * pre["interval"]["high"]], 1)])
    return md_table(["Model", "Pairs", "Effect (points)", "95% CI", "P after Holm", "Names swapped (points)",
                     "95% CI"], rows,
                    "Study 1b: Effect Under Typed Requests, by Model",
                    ["l", "r", "r", "r", "r", "r", "r"], label="rr-models-all", widths=[26, 7, 10, 15, 12, 12, 15],
                    note="Pairs: the pairs of a typed request and a table in which the model's responses without brand "
                         "names and with them both recommended a product. Effect: the share of responses that "
                         "recommended the optimal product without brand names minus the share with them (the "
                         "fictitious name on the optimal product), in percentage points. Names swapped: the share with "
                         "the familiar and the fictitious names swapped minus the share without brand names. The "
                         "intervals come from resampling requests and tables within each model and, for the last row, "
                         "over every model; in the last row, every model is weighted equally and the P value is the "
                         "primary test's. The names-swapped column has its own pairs, in which the responses without brand names and "
                         "with the names swapped both recommended a product. The models' P values are Holm-corrected "
                         "in one family of " + str(len(RRA["Holm, the secondary family"])) + " tests: "
                         "each model's effect and the four other contrasts.")


def rrcount(spec):
    """Counts over the models of the typed requests: 'holm05' (models whose effect has Holm P below .05),
    'positive', 'swapped_negative', 'pairs_min', 'pairs_max', 'answered' (the models that answered, those left out
    and incomplete included), 'open_answered', and 'incomplete/<model key>'."""
    pen = RRA["penalty, chat-log requests (primary)"]
    pre = RRA["premium, chat-log requests"]
    holm = RRA["Holm, the secondary family"]
    if spec == "holm05":
        return str(sum(1 for k in pen["per_model"]
                       if holm.get(f"penalty, chat-log requests, {k} (secondary contrast 1)", {}).get("holm", 1) < 0.05))
    if spec == "positive":
        return str(sum(1 for v in pen["per_model"].values() if v > 0))
    if spec == "swapped_negative":
        return str(sum(1 for v in pre["per_model"].values() if v < 0))
    if spec in ("pairs_min", "pairs_max"):
        return f"{(min if spec == 'pairs_min' else max)(pen['n_pairs_per_model'].values()):,}"
    if spec == "holm_family":  # the tests that Holm's method corrects together over every model
        return str(len(holm))
    answered = list(RRA["models"]) + list(RRA["left_out"]) + list(RRA["incomplete"])
    if spec == "answered":
        return str(len(answered))
    if spec == "open_answered":
        return str(sum(1 for m in answered if CHARS[m]["open"] == "open"))
    if spec.startswith("incomplete/"):  # the prompts that an incomplete model answered, from '269 of 1062 items answered'
        return f"{int(RRA['incomplete'][spec.split('/', 1)[1]].split()[0]):,}"
    raise KeyError(spec)


def rrbank(spec):
    """Counts of the bank of requests (requests/real-requests.jsonl) and of the prompts that the models saw
    (requests/items/full1/items.jsonl): 'bank/<group>' with group typed, webshop, author, wildchat, lma140, lma100,
    search; 'drawn/<kind>', 'pairs/<kind>' and 'categories/<kind>' with kind typed, webshop or author;
    'pairs_in/<category>' for the typed requests; 'tables' and 'all_categories' over every pair."""
    bank = [json.loads(line) for line in paper_names.text_of(PKG / "study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz").splitlines() if line.strip()]
    items = [json.loads(line) for line in paper_names.text_of(PKG / "study1b-64-models-on-34-tables/materials/requests/prompts.jsonl.gz").splitlines() if line.strip()]
    kinds = {"typed": "chat-log", "webshop": "crowd-written for a dataset", "author": "written by the author"}
    groups = {"wildchat": ("WildChat-4.8M",), "lma140": ("LMArena human preference 140k",),
              "lma100": ("LMArena human preference 100k",), "search": ("LMArena Search Arena 24k",),
              "webshop": ("WebShop human instructions",)}
    groups["typed"] = groups["wildchat"] + groups["lma140"] + groups["lma100"] + groups["search"]
    what, _, arg = spec.partition("/")
    if what == "bank":
        if arg == "author":
            return f"{sum(1 for r in bank if r['source'].startswith('the author')):,}"
        return f"{sum(1 for r in bank if r['source'] in groups[arg]):,}"
    if what in ("drawn", "pairs", "categories"):
        sel = [x for x in items if x["kind"] == kinds[arg]]
        key = {"drawn": lambda x: x["request"], "pairs": lambda x: (x["request"], x["table"]),
               "categories": lambda x: x["category"]}[what]
        return f"{len({key(x) for x in sel}):,}"
    if what == "pairs_in":
        return f"{len({(x['request'], x['table']) for x in items if x['kind'] == kinds['typed'] and x['category'] == arg}):,}"
    if what == "tables":
        return f"{len({x['table'] for x in items}):,}"
    if what == "all_categories":
        return f"{len({x['category'] for x in items}):,}"
    raise KeyError(spec)


def rrdev(spec):
    """'developers' or 'open': over the models that entered the estimates of the typed requests."""
    models = RRA["models"]
    if spec == "developers":
        return str(len({CHARS[m]["developer"] for m in models}))
    if spec == "open":
        return str(sum(1 for m in models if CHARS[m]["open"] == "open"))
    raise KeyError(spec)


def wts(spec):
    """'<heterogeneity run>/<open|closed|closed_names>': the models of that run with open weights, with closed
    weights, or the closed models' names joined as a list in words."""
    run, what = spec.rsplit("/", 1)
    models = _run_models(run)
    closed = _closed(run)
    if what == "open":
        return str(len(models) - len(closed))
    if what == "closed":
        return str(len(closed))
    if what == "closed_names":
        names = [NAMES[m] for m in closed]
        return ", ".join(names[:-1]) + " and " + names[-1]
    raise KeyError(spec)


def rr6(spec):
    """'typed': the effect of the fictitious name under the typed requests, in points, averaged over the models of the
    comparison with our own request (secondary contrast 3), as that contrast averages its models."""
    pen = RRA["penalty, chat-log requests (primary)"]["per_model"]
    models = RRA["penalty under chat-log requests minus the author's request on the same model and table "
                 "(secondary contrast 3)"]["per_model"]
    if spec == "typed":
        return n(100 * sum(pen[m] for m in models) / len(models), 1)
    raise KeyError(spec)


def s1breq(spec):
    """'requested' or 'not requested': Study 1b's models by the coding of the extended-thinking test."""
    return str(sum(1 for m in S1P["per_model"] if _reasoning(m["model"]) == spec))


def storepos(spec):
    """'<1 to 5>' or 'pairs': in how many of the store's tables and orders the optimal product already stood at that
    place in the plain listing (harness/items/h1/items.jsonl, arm plain), or how many tables and orders there are."""
    import ast
    seen = {}
    for line in paper_names.text_of(PKG / "study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz").splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if it["arm"] == "plain":
            order = it["order"] if isinstance(it["order"], list) else ast.literal_eval(it["order"])
            seen[(it["table"], it["trial"])] = order.index(it["best"]) + 1
    if spec == "pairs":
        return str(len(seen))
    return str(sum(1 for p in seen.values() if p == int(spec)))


def hetp(spec):
    """'<heterogeneity run>/<feature key>': that feature's Holm-corrected P as the tables print it (_pvh, so .0498
    does not print as .050)."""
    run, key = spec.split("/", 1)
    return _pvh(_het(run)["result"]["moderators"][key]["holm"])


RR_AGREEMENT = paper_names.later(PKG / "study1b-64-models-on-34-tables/materials/requests/coders_agreement.json")


def rragree(spec):
    """The coders of the typed requests (requests/coding/full1/AGREEMENT.json): 'spec_kappa', 'spec_equal' (requests
    with the same code), 'spec_n', 'needs/<none|tie|designated|another product>', 'needs_n', 'needs_second_n',
    'needs_agreement' (per cent)."""
    s, nd = RR_AGREEMENT["specificity"], RR_AGREEMENT["needs"]
    if spec == "spec_kappa":  # a coefficient that cannot exceed 1: no zero before the decimal point
        return f"{s['quadratic weighted kappa']:.2f}".lstrip("0")
    if spec == "spec_equal":
        return f"{round(s['exact agreement'] * s['both coded']):,}"
    if spec == "spec_n":
        return f"{s['both coded']:,}"
    if spec.startswith("needs/"):
        return f"{nd['Opus answers by kind'][spec.split('/', 1)[1]]:,}"
    if spec == "needs_n":
        return f"{nd['coded by Opus']:,}"
    if spec == "needs_second_n":
        return f"{nd['second coder pairs']:,}"
    if spec == "needs_agreement":
        return n(100 * nd["agreement with the second coder"], 0)
    raise KeyError(spec)


def rrreasonin(spec):
    """'<kind>/<names>/<code or all>': the coded reasons (requests/coding/full1/reasons.jsonl) of the responses to one
    kind of request (chat-log, crowd-written for a dataset, written by the author) under one version of the names
    (original, crossed)."""
    kind, names, code = spec.split("/", 2)
    items = {}
    for line in paper_names.text_of(PKG / "study1b-64-models-on-34-tables/materials/requests/prompts.jsonl.gz").splitlines():
        if line.strip():
            it = json.loads(line)
            items[it["id"]] = (it["kind"], it["names"])
    rows = [json.loads(line) for line in
            paper_names.text_of(PKG / "study1b-64-models-on-34-tables/materials/requests/reasons.jsonl.gz").splitlines() if line]
    return f"{sum(1 for r in rows if items.get(r['item']) == (kind, names) and code in ('all', r['reason'])):,}"


MODEL_TABLES = {"s1b_models": s1b_models, "s1b_lodo": s1b_lodo, "het_spread_all": het_spread_all,
                "het_moderators_all": het_moderators_all, "store_spread": store_spread,
                "rr_models_all": rr_models_all, "attr_spread": attr_spread}
MODEL_VALUES = {"s1bm": s1bm, "s1blodo": s1blodo, "hetcount": hetcount, "rrcount": rrcount, "rrbank": rrbank,
                "rrdev": rrdev, "wts": wts, "rr6": rr6, "s1breq": s1breq, "hetp": hetp, "rragree": rragree,
                "rrreasonin": rrreasonin, "storepos": storepos, "modelunit": modelunit, "auper": auper,
                "aucount": aucount, "pkgfile": pkgfile, "s1btop": s1btop}

TABLES.update(MODEL_TABLES)
sys.path.insert(0, str(CODE))
import tables_study2  # noqa: E402
TABLES.update(tables_study2.TABLES_STUDY2)
import tables_study3a  # noqa: E402  (Study 3a's 14 fictitious product brands, for Web Appendix L; a family's tables only once it has returned)
TABLES.update(tables_study3a.TABLES_STUDY3A)
TABLES.update({_n: (lambda _n=_n: _measure_table(_n)) for _n in MEASURE_TABLE_NAMES})

TABLES.update({"rob_all": rob_all})  # every main estimate without the three real-company tables
TABLES.update({"data_index": lambda: "DATA_INDEX_TABLE"})
TABLES.update({"bl_regressions": bl_regressions})
TABLES.update({"rr_models": rr_models, "bl_top": bl_top, "bl_ranked": bl_ranked, "bl_correlations": bl_correlations,
               "rel_pairs": rel_pairs, "au_tests": au_tests, "settings": settings_table,
               "wa_settings": wa_settings_table, "settings_sources": settings_sources,
               "het_spread": het_spread, "het_moderators": het_moderators, "store_arms": store_arms,
               "search_tests": search_tests, "sp_wordings": sp_wordings, "sp_ladder": sp_ladder,
               "b5_table": b5_table, "ms_brands": ms_brands, "ms_checks": ms_checks, "ms_full": ms_full, "tests_overview": tests_overview, "store_per_model": store_per_model, "search_per_model": search_per_model,
               "ex_coders": ex_coders,
               "rt_tones": rt_tones})


def bl_summary(source, what):
    """Study 2, brand by brand: over the 73 familiar brands of one
    source ('corpus', 'claude' or 'open'), the mean machine-based equity in points ('mean', one decimal), the median
    ('median'), or how many brands have a 95 percent interval above zero ('above') or below zero ('below')."""
    import json
    import statistics
    d = paper_names.read(PKG / "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/numbers.json")
    rows = d[f"pooled_{source}"].values()
    if what == "mean":
        return f"{statistics.mean(r['equity'] for r in rows):.1f}"
    if what == "median":
        return f"{statistics.median(r['equity'] for r in rows):.1f}"
    if what == "above":
        return f"{sum(1 for r in rows if r['ci95'][0] > 0):,}"
    if what == "below":
        return f"{sum(1 for r in rows if r['ci95'][1] < 0):,}"
    if what == "brands":
        return f"{len(rows):,}"
    if what == "floor":  # brands whose product was chosen in under 2 percent of the responses without brand names
        return f"{sum(1 for r in rows if r['share_hidden_pct'] < 2):,}"
    if what == "models":  # the number of models behind the source, read from the file's own sources line
        import re as _re
        m = _re.match(r"\s*(\d+) models", str(d["sources"][source]))
        if not m:
            raise ValueError(f"brand-level sources['{source}'] gives no model count: {d['sources'][source]!r}")
        return m.group(1)
    # the floor (the advisor's check, 20 November 2026): a brand whose product the models seldom pick with the names
    # hidden has little share to gain; 'floor' counts the brands under 2 percent with names hidden, and 'floor_mean'
    # and 'rest_mean' give the mean equity below and at or above that line
    if what == "floor":
        return f"{sum(1 for r in rows if r['share_hidden_pct'] < 2):,}"
    if what in ("floor_mean", "rest_mean"):
        low = what == "floor_mean"
        return f"{statistics.mean(r['equity'] for r in rows if (r['share_hidden_pct'] < 2) == low):.1f}"
    raise KeyError(what)


def rr_case(names, model, request, what):
    """The introduction's example under consumers' own requests (Study 2, the same five phones of Smartphones 3 at the
    equal price, the four Claude models, requests that people typed to chat assistants, not those that the authors
    wrote), recomputed from results/real-requests/full1/pairs.csv: with what='picked', how many answers in one names
    condition ('hidden' or 'original') picked the best product; with what='n', how many answers there were; with
    what='requests', how many distinct requests. model and request are 'all' or one id."""
    import csv
    rows = []
    with open(PKG / "study1b-64-models-on-34-tables/results/requests/pairs.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["table"] != "sr_smartphones_03_dom" or r["kind"] == "written by the author":
                continue
            if model != "all" and r["model"] != model or request != "all" and r["request"] != request:
                continue
            rows.append(r)
    if what == "requests":
        return f"{len({r['request'] for r in rows}):,}"
    if what == "n":
        return f"{sum(1 for r in rows if r[names]):,}"
    return f"{sum(1 for r in rows if r[names] and r[names] == r['designated']):,}"


def trq2_value(numbers, part, outcome, stat):
    """Question 2's six kinds of page against the brands with no pages: 'maxholm' is the largest Holm
    P over the kinds, 'lo' and 'hi' the smallest and largest estimate (two decimals; 'lo1', 'hi1' one). '-but-<kind>' leaves one kind out,
    as in 'the other kinds by 0.03 to 0.05 points'. A part that has not
    returned, an unknown outcome or kind, or an unknown statistic is refused."""
    import markers
    entry = numbers.get(part)
    if not entry or entry.get("state") != "returned":
        raise markers.MarkerError(f"trq2: part {part} has not returned")
    kinds = entry["numbers"]["kinds"].get(outcome)
    if kinds is None:
        raise markers.MarkerError(f"trq2: no outcome {outcome} in {part}")
    stat, _, leave = stat.partition("-but-")
    if leave and leave not in kinds:
        raise markers.MarkerError(f"trq2: no kind {leave} in {part}/{outcome}")
    vals = [v for kind, v in kinds.items() if kind != leave]
    if stat == "maxholm":
        return _pv(max(v["p_holm"] for v in vals))
    if stat[:2] in ("lo", "hi") and stat[2:] in ("", "0", "1", "2", "3"):
        est = [v["estimate"] for v in vals]
        return markers.fmt(min(est) if stat[:2] == "lo" else max(est), "f" + (stat[2:] or "2"))
    raise markers.MarkerError(f"trq2: unknown statistic {stat}")


TONE_AGREEMENT = ["study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone-coding/agreement-claude-models.json",
                  "study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone-coding/agreement-open-models.json",
                  "study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone-coding/agreement-open-models-added.json",
                  "study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone-coding/agreement-gpt-models.json"]


def tone_agreement(stat, files=None):
    """The two coders' agreement on the tone of the brand descriptions, over the four sets that were coded (the Claude
    models', the open models' in two sets, and the GPT models'): 'min' and 'max' give the range of Cohen's kappa (two
    decimals, no zero before the point), 'n' the number of descriptions that both coded, 'sets' the number of sets."""
    import markers
    docs = [json.loads((REPO / f).read_text(encoding="utf-8")) for f in (files or TONE_AGREEMENT)]
    kappas = [d["tone"] for d in docs]
    if stat == "min":
        return markers.fmt(min(kappas), "r2")
    if stat == "max":
        return markers.fmt(max(kappas), "r2")
    if stat == "n":
        return f"{sum(d['n'] for d in docs):,}"
    if stat == "sets":
        return str(len(docs))
    if stat in ("cli_n", "cli_agreement", "cli_kappa"):  # Claude Opus 5.5 through the command line against the API
        c = paper_names.read(PKG / "study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone-coding/command-line-coder-against-api-coder.json")
        c = c["cli_vs_api"]
        return (str(c["n"]) if stat == "cli_n" else markers.fmt(c["tone_agreement"], "pp0") if stat == "cli_agreement"
                else markers.fmt(c["tone_kappa"], "r2"))
    raise markers.MarkerError(f"tonekappa: unknown statistic {stat}")


def trq2_dose_value(numbers, part, outcome, step, stat):
    """The dose of question 2's six kinds of page, whose P values are two-sided and uncorrected: Holm's correction across the six kinds,
    then 'maxholm' (the largest corrected P) or 'minholm' (the smallest). A part that has not returned, an unknown
    outcome, step or statistic is refused."""
    import markers
    entry = numbers.get(part)
    if not entry or entry.get("state") != "returned":
        raise markers.MarkerError(f"trq2dose: part {part} has not returned")
    dose = entry["numbers"]["dose"].get(outcome)
    if dose is None:
        raise markers.MarkerError(f"trq2dose: no outcome {outcome} in {part}")
    if step not in ("0_to_80", "80_to_320"):
        raise markers.MarkerError(f"trq2dose: unknown step {step}")
    ps = sorted(float(v[step]["p_two_sided"]) for v in dose.values() if isinstance(v, dict) and step in v)
    adj, run = [], 0.0
    for rank, p in enumerate(ps):  # Holm (1979): (m - rank) * p, kept monotone, capped at 1
        run = max(run, min(1.0, (len(ps) - rank) * p))
        adj.append(run)
    if stat == "maxholm":
        return _pv(max(adj))
    if stat == "minholm":
        return _pv(min(adj))
    raise markers.MarkerError(f"trq2dose: unknown statistic {stat}")


class _Made(dict):
    """The made tables, plus any materials part on request: {{table:mat/<file>/<part>}} or {{table:mat/<file>/}}, and
    the counts of the introduction's example: {{table:case/<names>/<info>/<brand or all>}} (the authors' request) and
    {{table:rrcase/<names>/<model or all>/<request or all>/<picked, n or requests>}} (consumers' own requests)."""

    def __contains__(self, k):
        return super().__contains__(k) or str(k).startswith(("mat/", "scr/", "case/", "rrcase/", "blsum/", "rrreason/", "relsum/", "aurange/", "auholm/", "exkappa/", "exrange/", "exrefkappa/", "rtdecl/", "msconv/", "msdisc/", "msbrand/", "msrange/", "trreads/", "trq2/", "trq2dose/", "tonekappa/", "eqdollar/", "usdlt", "cs_n_total", "usd/", "usdsum/", "s2cfam/", "hdecl/", "s1bm/", "s1blodo/", "hetcount/", "rrcount/", "rrbank/", "rrdev/", "wts/", "rr6/", "s1breq/", "hetp/", "rragree/", "rrreasonin/", "storepos/", "mcrr/", "mcrnone/", "mcband/", "s1szero/", "s1stgap/", "rtgap/", "robsum/", "s2share/", "gpustudy/", "tabledef/", "modelunit/", "auper/", "aucount/", "pkgfile/", "s1btop/"))

    def __getitem__(self, k):
        name, _, arg = str(k).partition("/")
        if arg and name in MODEL_VALUES:
            return MODEL_VALUES[name](arg)
        if str(k).startswith("tabledef/"):  # tabledef/<tables|products|attributes_min|attributes_max|categories|second_invented|second_invented_categories>[_word]
            key = k.split("/", 1)[1]
            if key.endswith("_word"):  # a count under ten in words, as JMR prints it ("five products", "one table")
                count = int(table_definition()[key[:-5]])
                words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
                return words[count] if count < 10 else str(count)
            return str(table_definition()[key])
        if str(k).startswith("gpustudy/"):
            _, key, what = k.split("/", 2)
            return gpu_study(key, what)
        if str(k).startswith("aurange/"):
            _, comp, group, stat = k.split("/", 3)
            return au_range(comp, group, stat)
        if str(k).startswith("trreads/"):  # trreads/<pass|total>: OLMo 2 7B's pretraining checkpoints (every released
            import re as _re
            _, stat = k.split("/", 1)
            tr = paper_names.read(PKG / "study3a-pages-about-new-brands/results/training/numbers.json")
            cps = tr["q1"]["numbers"]["checkpoints"]
            pre = [c for c in cps if _re.fullmatch(r"olmo2-7b-(\d+b|s2-50b|base)", c)]
            if stat == "total":
                return str(len(pre))
            return str(sum(1 for c in pre if cps[c]["plain3"]["info0"].get("reads")))
        if str(k).startswith("tonekappa/"):  # tonekappa/<min|max|n|sets>: the coders' agreement on the descriptions' tone
            return tone_agreement(k.split("/", 1)[1])
        if str(k).startswith("trq2dose/"):  # trq2dose/<part>/<outcome>/<0_to_80|80_to_320>/<maxholm|minholm>
            _, part, outcome, step, stat = k.split("/", 4)
            tr = paper_names.read(PKG / "study3a-pages-about-new-brands/results/training/numbers.json")
            return trq2_dose_value(tr, part, outcome, step, stat)
        if str(k).startswith("trq2/"):  # trq2/<part>/<outcome>/<maxholm|lo|hi>[-but-<kind>]: question 2 (trq2_value)
            _, part, outcome, stat = k.split("/", 3)
            tr = paper_names.read(PKG / "study3a-pages-about-new-brands/results/training/numbers.json")
            return trq2_value(tr, part, outcome, stat)
        if str(k).startswith("msconv/"):  # msconv/<a>/<b>/<r|ci|rawr|rawci>: Study 2c's convergence of two measures
            # (keys 'a | b' of summary.json, which a marker cannot hold), corrected for reliability unless raw
            _, a, b, stat = k.split("/", 3)
            c = _ms_summary()["convergence"][f"{MS_MEASURES[a]} | {MS_MEASURES[b]}"]
            if stat == "r":
                return _r(c["corrected_r"])
            if stat == "rawr":
                return _r(c["pooled_r"])
            iv = c["corrected_ci95"] if stat == "ci" else c["ci95_models_and_brands_resampled"]
            return f"{_r(iv[0])}, {_r(iv[1])}"
        if str(k).startswith("msdisc/"):  # msdisc/<ruled|total>: discriminant measures whose corrected interval lies
            # inside -.5 to .5 (a strong relation ruled out, the plan's test), or how many measures there are
            _, stat = k.split("/", 1)
            d = {kk: v for kk, v in _ms_summary()["discriminant"].items() if kk != "mbbe_pair_reliability"}
            if stat == "total":
                return str(len(d))
            if stat in ("rmin", "rmax"):  # the corrected correlations' range; 'rmin' is the one nearest zero when all
                # share a sign, so the text reads 'from rmin to rmax'
                rs = sorted((v["corrected_r"] for v in d.values()), key=abs)
                return _r(rs[0] if stat == "rmin" else rs[-1])
            if stat == "allneg":  # refuses the sentence 'every estimate is negative' when one is not
                if any(v["corrected_r"] >= 0 for v in d.values()):
                    raise ValueError("msdisc/allneg: a discriminant correlation is not negative")
                return "negative"
            return str(sum(1 for v in d.values() if -0.5 < v["corrected_ci95"][0] and v["corrected_ci95"][1] < 0.5))
        if str(k).startswith("eqdollar/"):  # eqdollar/<price>: Study 2c's equalization price in dollars on a product of
            # that price, rounded to five dollars (results/study2/all-models-eq1, the crossing)
            _, price = k.split("/", 1)
            eq = paper_names.read(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/numbers.json")
            cross = eq["2c"]["pooled"]["pooled"]["option_a_without_a_model"]["price"]["original"]["crossing_value"]
            return f"\\${5 * round(float(price) * cross / 100 / 5):,}"
        if str(k).startswith("mcrr/"):  # mcrr/<key of a Claude model in summary.json>/<min|max>: the smallest or
            # largest value over the Claude models that have the key, in the key's own format
            _, key, stat = k.split("/", 2)
            if key == "price_premium_median_pct_direct_models":  # the median price premium of the main choice sets,
                # over the models that answered the direct test
                vals = [_mcr_price_median(m) for m in MCR_MODELS
                        if _mcr()["models"][m].get("direct_share_same_price_pct") is not None]
                return n((min if stat == "min" else max)(vals), 0)
            ms = [m for m in _mcr()["models"].values() if m.get(key) is not None]
            v = (min if stat == "min" else max)(m[key] for m in ms)
            if key in ("reliability", "direct_with_price_premium_r"):
                return _r(v)
            if key == "mean_rating_equivalent_stars":
                return n(v, 2)
            if key in ("mean_share_premium_pp", "direct_premium_median_pct"):
                return n(v, 1)
            if key == "price_premium_median_pct":
                vals = [_mcr_price_median(m) for m in MCR_MODELS]
                return n((min if stat == "min" else max)(vals), 0)
            return f"{v:,}" if isinstance(v, int) else n(v, 1)
        if str(k).startswith("usd/"):  # usd/<claude|gpt>/<category>/<brand>/<median|lo|hi>: Study 2b's price premium in
            _, group, cat, brand, stat = k.split("/", 4)
            pp = _over_models(group)[f"{cat} | {brand}"][group]["price_premium"]
            if "usd" not in pp:
                raise ValueError(f"usd: no model of {group} has {brand}'s premium inside the tested prices in {cat}")
            u = pp["usd"]
            v = u["median"] if stat == "median" else u["median_ci95"][0 if stat == "lo" else 1]
            return _usd_text(v, signed=True)
        if k == "cs_n_total":  # the abstract's N: the participants analysed in Study 4 and Supplemental Studies S1 to S3,
            # after the preregistered exclusions (S1 to S3: funnel/analysed; Study 4's file holds only the kept rows)
            cs = paper_names.read(PKG / "study4-peoples-choices-after-a-recommendation/results/numbers.json")
            total = sum(cs[s]["funnel"]["analysed"] for s in ("study_1a", "study_1b", "study_2"))
            return f"{total + cs['study_3']['funnel']['rows_in_file']:,}"
        if k == "usdlt":  # the abstract's dollars: the median, over the laptop and television brands, of each brand's
            # median dollar premium over every model that answered (full1-all)
            import statistics
            vals = [v["all"]["price_premium"]["usd"]["median"] for kk, v in _over_models("all").items()
                    if kk.split(" | ")[0] in ("laptops", "tvs") and "usd" in v["all"]["price_premium"]]
            return _usd_text(statistics.median(vals))
        if str(k).startswith("usdsum/"):  # usdsum/<claude|gpt>/<median|pairs|beyond>: over the brand and category pairs,
            # the median of the group's dollar premiums, the pairs that have one, and the pairs with no model inside
            import statistics
            _, group, stat = k.split("/", 2)
            om = _over_models(group)
            vals = [v[group]["price_premium"]["usd"]["median"] for v in om.values() if "usd" in v[group]["price_premium"]]
            if stat == "pairs":
                return str(len(vals))
            if stat == "beyond":
                return str(sum(1 for v in om.values() if "usd" not in v[group]["price_premium"]))
            return _usd_text(statistics.median(vals))
        if str(k).startswith("s2cfam/"):  # s2cfam/<group>: Study 2c, at the same price and with brand names, the
            # familiar product's share of the choices between it and its otherwise identical twin with a fictitious name,
            # in per cent: one minus (the fictitious twin's share without brand names minus the drop with them)
            _, group = k.split("/", 1)
            eq = paper_names.read(PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/numbers.json")
            d = eq["2c"]["pooled"]["pooled"] if group == "all" else eq["2c"]["by_group"][group]["pooled"]
            hidden = d["option_a"]["zero_control"]["invented_share_of_pair_picks"]
            drop = d["option_a_parity_tests"]["names hidden minus names shown, invented twin's share of pair picks"]
            return f"{100 * (1 - (hidden - drop['estimate'])):.0f}"
        if str(k).startswith("hdecl/"):  # hdecl/max: the largest of the models' mean decline shares over the store's
            m = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/store/all-models/numbers.json")
            m = m["declines"]["mean of the models' shares by arm and name version"]
            return f"{100 * max(v for arm in m.values() for v in arm.values()):.1f}"
        if str(k).startswith("mcrnone/"):  # mcrnone/<key>: 'none' for a count of zero in summary.json; refuses otherwise
            _, key = k.split("/", 1)
            if _mcr()[key] != 0:
                raise ValueError(f"mcrnone: {key} is {_mcr()[key]}, so 'none' is false")
            return "none"
        if str(k).startswith("mcband/"):  # mcband/<model>/<category>/<brand>: the brand's band center in dollars, from
            # its price premium in dollars and in percent (the full design's price table)
            _, m, cat, brand = k.split("/", 3)
            b = _mcr_numbers()["models"][m][cat]["main"]["brands"][brand]
            return f"\\${b['price_premium_usd'] / b['price_premium_pct'] * 100:,.0f}"
        if str(k).startswith("msrange/"):  # msrange/<min|max>: the smallest or largest median share premium over brands
            _, stat = k.split("/", 1)
            vals = [float(r["share_premium_median_pp"]) for r in _ms_brands()]
            return n(min(vals) if stat == "min" else max(vals), 1)
        if str(k).startswith("msbrand/"):  # msbrand/<brand>/<category>/<column of brand_pairs.csv>: one brand's row
            _, brand, cat, col = k.split("/", 3)
            row = [r for r in _ms_brands() if r["brand"] == brand and r["category"] == cat]
            if len(row) != 1:
                raise ValueError(f"msbrand: no single row for {brand} in {cat}")
            v = row[0][col]
            return v if col in ("models", "models_above_zero", "models_below_zero") else n(float(v), 1)
        if str(k).startswith("rtdecl/"):  # rtdecl/othermax: the largest of the models' mean decline shares at the tones
            rt = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/numbers.json")
            m = rt["declines"]["mean of the models' shares by arm and name version"]
            vals = [v for tone, d in m.items() if tone != "negative" for v in d.values()]
            return f"{100 * max(vals):.1f}"
        if str(k).startswith("exrefkappa/"):  # exrefkappa/<min|max>: each coder's kappa with the reference reading of
            _, stat = k.split("/", 1)
            chk = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/CHECKS.json")
            vals = [v["on_the_200_vs_reference"]["brand_any"]["kappa"] for v in chk.values()]
            return f"{(min(vals) if stat == 'min' else max(vals)):.2f}".lstrip("0")
        if str(k).startswith("exkappa/"):
            _, group, stat = k.split("/", 2)
            ex = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/numbers.json")
            vals = [v[group]["brand_any"]["kappa"] for v in ex["agreement"].values()]
            return f"{(min(vals) if stat == 'min' else max(vals)):.2f}".lstrip("0")
        if str(k).startswith("s1szero/"):
            _, quantity = k.split("/", 1)
            s1s = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/search/all-models/numbers.json")
            return str(sum(1 for v in s1s[quantity]["per_model"].values() if v == 0))
        if str(k).startswith("rtgap/"):  # rtgap/<min|max>: the smallest or largest effect of the fictitious name with
            _, stat = k.split("/", 1)
            rt = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/numbers.json")
            gaps = rt["name gap g(e)"]
            tones = ["positive", "mixed", "negative"]
            low = [t for t in tones if gaps[t]["interval"]["low95"] <= 0]
            if low:
                raise ValueError(f"rtgap: the 95% interval reaches zero at {low}; the sentence 'remained' is false")
            if stat == "pmax":  # with its relation, for '*p* {{table:rtgap/pmax}} for each'
                worst = max(gaps[t]["interval"]["p_two_sided"] for t in tones)
                return "< .001" if worst < 0.001 else f"≤ {_pv(worst)}"
            vals = [100 * gaps[t]["pooled"] for t in tones]
            return f"{(min(vals) if stat == 'min' else max(vals)):.1f}"
        if str(k).startswith("s1stgap/"):  # s1stgap/<min|max>: the smallest or largest effect of the fictitious name
            _, stat = k.split("/", 1)
            st = paper_names.read(PKG / "study1c-product-feeds-and-a-store-search/results/store/all-models/numbers.json")
            arms = ["feed-openai", "feed-openai-2025", "feed-google", "schema-org", "sponsored-familiar",
                    "sponsored-best", "position-first", "position-middle", "position-last", "rating-0.1",
                    "rating-0.3", "rating-0.5"]
            gaps = st["name gap g(arm)"]
            low = [a for a in arms if gaps[a]["interval"]["low95"] <= 0]
            if low:
                raise ValueError(f"s1stgap: the 95% interval reaches zero in {low}; the sentence 'remained' is false")
            if stat == "pmax":  # with its relation, for '*p* {{table:s1stgap/pmax}} for each'
                worst = max(gaps[a]["interval"]["p_two_sided"] for a in arms)
                return "< .001" if worst < 0.001 else f"≤ {_pv(worst)}"
            vals = [100 * gaps[a]["pooled"] for a in arms]
            return f"{(min(vals) if stat == 'min' else max(vals)):.1f}"
        if str(k).startswith("exrange/"):
            # rule: every result under every judge, with the range across them); min and max of the estimate in
            # percentage points, pmax the largest p across the coders
            _, key, stat = k.split("/", 2)
            ex = paper_names.read(PKG / "study2a-experience-attributes-stated-for-every-product/results/explanations/numbers.json")
            rows = [ex["shares"][j]["overall"][key] for j in ex["judges"]]
            if stat == "pmax":  # with its relation, for '*p* {{table:exrange/<key>/pmax}} under each coder'
                worst = max(r["p"] for r in rows)
                return "< .001" if worst < 0.001 else f"≤ {_pv(worst)}"
            vals = [100 * r["est"] for r in rows]
            return f"{(min(vals) if stat == 'min' else max(vals)):.1f}"
        if str(k).startswith("auholm/"):  # auholm/<min|max>: the smallest or largest Holm P of Study 2d's test 1
            stat = k.split("/", 1)[1]
            if stat.startswith("familiar-"):  # auholm/familiar-<measure>: Holm across the six measures, familiar names
                keys = [key for key, _ in AU_LABELS]
                ps = sorted((AU["test1_familiar"][key]["p"], key) for key in keys)
                adj, run = {}, 0.0
                for rank, (pv, key) in enumerate(ps):  # Holm (1979): (m - rank) * p, kept monotone, capped at 1
                    run = max(run, min(1.0, (len(ps) - rank) * pv))
                    adj[key] = run
                return _pv(adj[stat.split("-", 1)[1]])
            vals = [AU["test1"][key]["p_holm"] for key, _ in AU_LABELS]
            return _pv(min(vals) if stat == "min" else max(vals))
        if str(k).startswith("s2share/"):  # s2share/<model or pooled>/<hidden|original|crossed>/<0|1>
            _, model, names, info = k.split("/", 3)
            return n(s2_shares()[0][(model, names, info)], 1)
        if str(k).startswith("robsum/"):
            return rob_summary(k.split("/", 1)[1])
        if str(k).startswith("relsum/"):
            return rel_summary(k.split("/", 1)[1])
        if str(k).startswith("rrreason/"):
            return rr_reason(k.split("/", 1)[1])
        if str(k).startswith("blsum/"):
            _, source, what = k.split("/", 2)
            return bl_summary(source, what)
        if str(k).startswith("rrcase/"):
            _, names, model, request, what = k.split("/", 4)
            return rr_case(names, model, request, what)
        if str(k).startswith("case/"):
            _, names, info, brand = k.split("/", 3)
            return s2_case(names, info, brand)
        if str(k).startswith("scr/"):
            _, f, part = k.split("/", 2)
            return screen(f, part)
        if str(k).startswith("mat/"):
            _, f, part = k.split("/", 2)
            return material(f, part or None)
        return super().__getitem__(k)


# ---------------------------------------------------------------- the computing (framework.compute)

GPU_JOBS = PKG / "computing/gpu_jobs.csv"
GPU_TOTALS = PKG / "computing/gpu_hours.json"
GPU_STUDIES = {  # the label in gpu_jobs.csv -> (the short key for {{table:gpustudy/<key>/...}}, the label printed)
    "Study 1: open models": ("s1-open", "Study 1: the models with open weights"),
    "Study 1: the store and the search step": ("s1-store", "Study 1: in a store and with a search step"),
    "Study 2: awareness or image (the audit)": ("s2-audit", "Study 2: awareness or image"),
    "Study 3: where it comes from (training)": ("s3-training", "Study 3: training on planted text"),
    "Study 3: inside the model (Web Appendix)": ("s3-inside", "Study 3: inside the model (Web Appendix)"),
    "The measure of machine-based brand equity (Web Appendix)": ("measure", "The measure (Web Appendix)"),
    "Setup": ("setup", "Setting up the models"),
    "Setup and checks": ("checks", "Setting up and checking the runs"),
    "Data export": ("export", "Exporting the answers"),
}
GPU_NAMES = {"h100": "H100", "l40s": "L40S", "": "none"}


def gpu_jobs(jobs_path=GPU_JOBS, totals_path=GPU_TOTALS):
    """The rows of gpu_jobs.csv, checked against the study labels and against the totals in gpu_hours.json."""
    with open(jobs_path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    totals = json.loads(Path(totals_path).read_text(encoding="utf-8"))
    for r in rows:
        if r["study"] not in GPU_STUDIES:
            raise ValueError(f"gpu_jobs.csv: job {r['job']} serves a study with no label in GPU_STUDIES: {r['study']!r}")
        if r["gpu_type"] not in GPU_NAMES:
            raise ValueError(f"gpu_jobs.csv: job {r['job']} has a GPU type with no name: {r['gpu_type']!r}")
    if len(rows) != totals["jobs"]:
        raise ValueError(f"gpu_jobs.csv holds {len(rows)} jobs, gpu_hours.json {totals['jobs']}")
    hours = sum(float(r["gpu_hours"]) for r in rows)
    if abs(hours - totals["gpu_hours"]) > 0.05 * max(len(rows), 1):  # each row is rounded to 0.1
        raise ValueError(f"gpu_jobs.csv adds to {hours:.1f} GPU hours, gpu_hours.json {totals['gpu_hours']}")
    return rows


def _state(s):
    return " and ".join(s.lower().split("+")).capitalize()


def computing_jobs():
    rows = [[r["job"], GPU_STUDIES[r["study"]][1], GPU_NAMES[r["gpu_type"]], n(float(r["gpu_hours"]), 1),
             n(float(r["cpu_core_hours"]), 1), _state(r["states"])] for r in gpu_jobs()]
    return md_table(["Job", "What it served", "GPU", "GPU hours", "CPU core hours", "State"], rows,
                    "Every Job on the University Supercomputer", ["r", "l", "l", "r", "r", "l"], label="computing-jobs",
                    note="Hours from the scheduler's own records; a job that failed or was cancelled still used the "
                         "hours shown. GPU none: a job that ran on processors only.")


def _by_study():
    out = {}
    for r in gpu_jobs():
        key = GPU_STUDIES[r["study"]][0]
        d = out.setdefault(key, {"jobs": 0, "gpu_hours": 0.0, "cpu_core_hours": 0.0})
        d["jobs"] += 1
        d["gpu_hours"] += float(r["gpu_hours"])
        d["cpu_core_hours"] += float(r["cpu_core_hours"])
    return out


def computing_by_study():
    by = _by_study()
    rows = [[label, str(by[key]["jobs"]), n(by[key]["gpu_hours"], 1), n(by[key]["cpu_core_hours"], 1)]
            for key, label in GPU_STUDIES.values() if key in by]
    totals = json.loads(GPU_TOTALS.read_text(encoding="utf-8"))
    rows.append(["Total", str(totals["jobs"]), n(totals["gpu_hours"], 1), n(totals["cpu_core_hours"], 1)])
    return md_table(["What the jobs served", "Jobs", "GPU hours", "CPU core hours"], rows,
                    "The Computing on the University Supercomputer, by Study", ["l", "r", "r", "r"],
                    label="computing-by-study",
                    note="GPU hours by type: " + ", ".join(f"{GPU_NAMES[k]} {n(v, 1)}"
                                                           for k, v in totals["gpu_hours_by_type"].items()) + ".")


def gpu_study(key, what):
    by = _by_study()
    if key not in by:
        raise KeyError(f"gpustudy: no jobs for '{key}' (keys: {', '.join(sorted(by))})")
    v = by[key][what]
    return str(v) if what == "jobs" else n(v, 1)


TABLES.update({"computing_jobs": computing_jobs, "computing_by_study": computing_by_study})


def computing_selftest():
    """The checks of gpu_jobs(): a clean pair of files is read;"""
    import tempfile
    head = "job,study,gpu_type,gpu_hours,cpu_core_hours,states\n"
    good = head + "1,Study 1: open models,h100,2.0,16.0,COMPLETED\n2,Setup,,0.0,1.0,FAILED\n"
    totals = {"jobs": 2, "allocations": 4, "gpu_hours_by_type": {"h100": 2.0}, "gpu_hours": 2.0, "cpu_core_hours": 17}
    cases = [
        ("clean", good, totals, None),
        ("a study with no label", good.replace("Setup", "Study 9: something new"), totals, "no label"),
        ("a job missing from the list", head + "1,Study 1: open models,h100,2.0,16.0,COMPLETED\n", totals, "jobs"),
        ("hours that do not add up", good.replace(",2.0,16.0", ",5.0,16.0"), totals, "GPU hours"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for name, jobs, tot, refusal in cases:
            jp, tp = Path(tmp) / "jobs.csv", Path(tmp) / "totals.json"
            jp.write_text(jobs, encoding="utf-8")
            tp.write_text(json.dumps(tot), encoding="utf-8")
            try:
                gpu_jobs(jp, tp)
                assert refusal is None, f"not refused: {name}"
            except ValueError as exc:
                assert refusal is not None and refusal in str(exc), f"{name}: {exc}"
    print("computing selftest: the clean files were read; 3 of 3 planted faults refused (a study with no label, a "
          "missing job, hours that do not add up)")


_TABLE_DEF = {}


def table_definition():
    """What a table of the controlled test holds, for the paper's definition of a table: the number of tables, products per table, the fewest and most listed attributes of a product, and
    the categories, read from the items with the names shown, no information and the equal price (trial 0). The
    products of one table can list different numbers of attributes, so the range is over all products. Refuses a table
    whose products do not all have the same reviews, which the paper states. and counts the tables in which a product other
    than the optimal one also has an invented brand (second_invented; one, a table of televisions), which the paper
    states."""
    if _TABLE_DEF:
        return _TABLE_DEF
    sys.path.insert(0, str(PKG / "common/tables"))
    import gates
    import importlib.util as _u
    _spec = _u.spec_from_file_location("table_builder", PKG / "common/tables/tables.py")
    study2_tables = _u.module_from_spec(_spec)
    _spec.loader.exec_module(study2_tables)
    import dominant_sets  # noqa: E402
    gates.KEY.update(dominant_sets.build(study2_tables.load_tables())[1])   # the rules of the _dom tables, as build_items.py
    first = {}
    with paper_names.open_text(S2_ITEMS) as fh:
        for line in fh:
            j = json.loads(line)
            if (j["names"], str(j["info"]), str(j["rung"]), str(j["trial"])) == ("original", "0", "0", "0"):
                first.setdefault(j["table"], j)
    products, attributes, categories = set(), [], set()
    for t, j in first.items():
        blocks = [b for b in j["user"].split("--- Product")[1:]]
        counts, reviews = [], set()
        for b in blocks:
            body = b.split("Specs:", 1)[1] if "Specs:" in b else ""
            counts.append(sum(1 for ln in body.splitlines() if ln.startswith("  ") and ":" in ln))
            reviews.update(ln.strip() for ln in b.splitlines() if ln.strip().startswith("Reviews:"))
        if len(reviews) != 1:
            raise ValueError(f"{t}: products differ in their reviews")
        products.add(len(blocks))
        attributes.extend(counts)
        categories.add(j["category"])
    if len(products) != 1:
        raise ValueError(f"tables differ in their number of products: {sorted(products)}")
    fails = gates.gate_a(list(first.values()))
    if fails:
        raise ValueError("a table of the controlled test has no single optimal product: " + "; ".join(fails[:3]))
    second = {}
    for t, j in first.items():
        invented = [k for k, p in j["products"].items() if p["true_kind"] == "invented"]
        if j["best"] not in invented:
            raise ValueError(f"{t}: the optimal product does not have an invented brand")
        if len(invented) > 1:
            second[t] = j["category"]
    if set(second.values()) - {"tvs"}:   # the paper names the category: "except in one table of televisions"
        raise ValueError(f"a table outside televisions has a second invented brand: {second}; change the sentence")
    _TABLE_DEF.update(tables=len(first), products=products.pop(), attributes_min=min(attributes),
                      attributes_max=max(attributes), categories=len(categories), second_invented=len(second),
                      second_invented_categories=", ".join(sorted(set(second.values()))))
    return _TABLE_DEF


def build_all():
    return _Made({name: f() for name, f in TABLES.items()})


if __name__ == "__main__" and sys.argv[1:] == ["--selftest"]:
    computing_selftest()
    sys.exit(0)

if __name__ == "__main__":
    for name, md in build_all().items():
        print(f"== {name}\n{md[:600]}\n")
