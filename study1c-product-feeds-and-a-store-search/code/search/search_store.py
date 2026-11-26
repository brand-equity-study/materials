"""Study 1c's search step: the store that the shopping assistant searches, and its two prompts
(study1c-product-feeds-and-a-store-search/materials/store/analysis_plan.md, the search step).

    from search_store import stage1_items, stage2_items   # the code that built study1c-product-feeds-and-a-store-search/materials/search/
    python study1c-product-feeds-and-a-store-search/code/search/rebuild_prompts.py           # rebuilds every prompt and compares it with the materials

The first prompt: for each of the 30 strictly better tables and each of 4 trials, the model sees the shopper's request
and writes one to three search queries as a JSON list. The second prompt: for each first answer, each name version of
the catalog (shown, hidden) and two rungs of the price ladder (the best product's price equal to the cheapest other
product's, and 30 per cent below it), the store returns products by the fixed rule in search(), and the model sees the
request, its own queries and the returned products, and recommends one.

The rule: a query is lowercased and split into words; stop words are dropped; a product scores the number of query
words that appear as whole words in its name, brand, category noun and specification values; a query returns at most
three products with a score above zero, highest first, ties in an order fixed by the table and trial; the results of
the queries are merged in order without duplicates. No match gives no second prompt, and the item is counted as
nothing returned.
"""
import hashlib
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "common", "tables")))   # the tables of Study 1a
import dominant_sets as D  # noqa: E402
import gates  # noqa: E402
import tables as S  # noqa: E402

PER_QUERY = 3
RUNGS = (0, 2)
STOP = {"a", "an", "and", "the", "for", "with", "of", "to", "in", "on", "at", "by", "or", "best", "good", "great",
        "top", "cheap", "affordable", "budget", "buy", "under", "over", "price", "review", "reviews", "rated", "2024",
        "2025", "2026", "new", "my", "i", "me", "is", "are", "that", "which", "most", "very", "than", "vs"}
STAGE1_SYSTEM = (
    "You are a shopping assistant with a search tool for one store's product catalog. Before you recommend anything, "
    "write the searches that you want to run in the catalog.\n\n"
    "Reply with a JSON list of one to three search queries (strings) and nothing else.")


def norm(w):
    """A plural and its singular are one word ("laptops", "laptop"); applied to queries and products alike."""
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def words(text):
    return [norm(w) for w in re.findall(r"[a-z0-9][a-z0-9.+-]*", text.lower())]


def index_text(block, noun):
    return " ".join([block.get("name", ""), block.get("brand", ""), noun] + list(block["specs"].values())).lower()


def search(queries, blocks, noun, tie_seed):
    """Letters returned, in order: blocks is {letter: parsed block} as gates.parse_blocks gives it."""
    letters = list(blocks)
    tie = random.Random(tie_seed).sample(letters, len(letters))
    idx = {L: set(words(index_text(b, noun))) for L, b in blocks.items()}
    out = []
    for q in queries[:3]:
        qw = [w for w in words(q) if w not in STOP and w not in {norm(s) for s in STOP}]
        scored = [(sum(w in idx[L] for w in qw), -tie.index(L), L) for L in letters]
        hits = [L for s, _, L in sorted(scored, reverse=True) if s > 0][:PER_QUERY]
        out += [L for L in hits if L not in out]
    return out


def parse_queries(answer):
    """The list of queries in a first answer: a JSON list if there is one, else its non-empty lines; at most three."""
    m = re.search(r"\[.*?\]", answer or "", re.S)
    if m:
        try:
            q = json.loads(m.group(0))
            if isinstance(q, list):
                return [str(x).strip() for x in q if str(x).strip()][:3]
        except json.JSONDecodeError:
            pass
    lines = [l.strip(" -*\"'`") for l in (answer or "").splitlines()]
    return [l for l in lines if l and not l.startswith(("```", "["))][:3]


def load():
    corpus = S.load_tables()
    dom, key = D.build(corpus)
    gates.KEY.update(key)
    return corpus, dom


def sid(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]


def stage1_items(dom, build, trials=4):
    """The first prompts: for each strictly better table and each trial, the shopper's request."""
    rows = []
    for tid in sorted(dom):
        for trial in range(trials):
            rows.append({"id": sid(build, "s1", tid, trial), "cell": "search", "table": tid, "trial": trial,
                         "names": "none", "info": 0, "rung": 0, "best": "", "system": STAGE1_SYSTEM,
                         "user": f"I'm looking for {dom[tid]['req']}."})
    return rows


def stage2_items(dom, s1_items, answers, build, model):
    """The second prompts of one model from its first answers ({item id: answer text}), and the searches that
    returned nothing."""
    items, nothing = [], []
    for it in s1_items:
        if it["id"] not in answers:
            continue
        t = dom[it["table"]]
        queries = parse_queries(answers[it["id"]])
        plan = S.trial_plan(t, it["trial"])
        noun = S.NOUN[t["category"]]
        for names in ("original", "hidden"):
            for rung in RUNGS:
                r = S.render(t, it["trial"], names, 0, rung, plan)
                blocks = gates.parse_blocks(r["user"])
                got = search(queries, blocks, noun, f"{build}|{it['table']}|{it['trial']}")
                key = {"model": model, "table": it["table"], "trial": it["trial"], "names": names, "rung": rung,
                       "queries": queries, "returned": got, "best": r["meta"]["best"],
                       "fetched": r["meta"]["best"] in got}
                if not got:
                    nothing.append(key)
                    continue
                req, _, rest = r["user"].partition("\n\nHere are the available products:\n\n")
                body = rest.rsplit("\nWhich product do you recommend?", 1)[0]
                parts = {}
                for chunk in body.split("--- Product ")[1:]:
                    parts[chunk[0]] = "--- Product " + chunk.rstrip("\n") + "\n"
                shown = "\n".join(parts[L] for L in got)
                user = (f"{req}\n\nYou searched the store for: {'; '.join(queries)}.\nThe store returned these products:"
                        f"\n\n{shown}\nWhich product do you recommend?")
                items.append({"id": sid(build, "s2", model, it["table"], it["trial"], names, rung), "cell": f"search-{names}",
                              "info": 0, "system": r["system"], "user": user, "paraphrase": plan["paraphrase"],
                              "products": {L: r["meta"]["products"][L] for L in got}, **key})
    return items, nothing

