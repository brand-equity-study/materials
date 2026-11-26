"""Study 1, how the bank of consumers' requests was selected, under the rules in
study1b-64-models-on-34-tables/materials/requests/selection/SELECTION.md, which were committed before this script first ran on the data.

--data is a folder that holds the downloaded sets, and --work a folder for the files that the stages write. The
stages run in this order:
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py extract --data <data> --work <work>
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py webshop --data <data> --work <work>
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py search  --data <data> --work <work>
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py apply   --work <work> --set search
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py apply   --work <work> --set webshop
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py apply   --work <work> --set chat
    python -I study1b-64-models-on-34-tables/code/selection/select_requests.py bank    --work <work>
extract reads WildChat-4.8M and the two LMArena human-preference sets, webshop reads WebShop's instructions, and search
reads LMArena's Search Arena (the package README says where each is downloaded and into which folder of <data>). apply
reads the classifier's labels from study1b-64-models-on-34-tables/materials/requests/selection/ (labels_<instruction>.jsonl.gz and the search_
and webshop_ files) in place of the classifier's answers, and stops when a label belongs to a candidate with another
source identifier, which means that the candidates were not rebuilt as they were; with --answers it reads a folder of
the classifier's answers instead (one <id>.md file for each candidate), for someone who runs the classifier again.
--labels classify_out gives the first instruction's labels, which failed the hand check, and --hand draws the blind
hand-check sample. bank reads the hand labels, the author's requests and the brand words of the 34 tables
(table_words.json) from the same folder and writes requests.jsonl and counts.json in <work>; with the deposited labels,
requests.jsonl has the SHA-256 that study1b-64-models-on-34-tables/materials/requests/FILES.csv lists for requests.jsonl.gz.

Run it with an interpreter in isolated mode (python -I), because it reads downloaded files.
"""
import argparse
import collections
import datetime as dt
import glob
import gzip
import hashlib
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
MAT = os.path.abspath(os.path.join(HERE, "..", "..", "materials", "requests", "selection"))
SEED = "jmr-a3-20261120"
MIN_CHARS, MAX_CHARS = 10, 2000
PER_IP_CAP = 2          # at most this many requests from one hashed IP address in one category (WildChat only)
RUN_PER_CATEGORY = 25   # requests per category drawn for the model runs
FLOOR = 10              # below this many chat-log requests, a category is filled from WebShop, then by the author

# ---------------------------------------------------------------- stage 1: the keyword filter

CATEGORY_TERMS = {
    "laptops": r"laptops?|notebook computers?|macbooks?|chromebooks?|ultrabooks?",
    "smartphones": r"smart ?phones?|cell ?phones?|mobile phones?|phones?|iphones?|android phones?",
    "tvs": r"tvs?|televisions?|tv sets?",
    "headphones": r"headphones?|headsets?|over-ear|on-ear",
    "running_shoes": r"running shoes?|running sneakers?|jogging shoes?|shoes? for running|marathon shoes?|trail runners?|running trainers?",
    "coffee_makers": r"coffee ?makers?|coffee machines?|espresso machines?|espresso makers?|drip coffee|french press(es)?|keurig",
    "wireless_earbuds": r"earbuds?|ear buds?|earphones?|in-ear|airpods?|true wireless",
    "smartwatches": r"smart ?watch(es)?|fitness trackers?|apple watch(es)?",
    "robot_vacuums": r"robot(ic)? vacuums?|robot vacuum cleaners?|robot cleaners?|roombas?|vacuum robots?",
    "portable_speakers": r"bluetooth speakers?|portable speakers?|wireless speakers?",
    "keyboards": r"keyboards?",
    "external_ssds": r"external ssds?|portable ssds?|external (hard )?drives?|portable (hard )?drives?|external storage",
    "water_bottles": r"water bottles?|insulated bottles?|hydro ?flasks?",
    "electric_toothbrushes": r"(electric |sonic )?toothbrush(es)?",
    "backpacks": r"backpacks?|rucksacks?|daypacks?",
    "blenders": r"blenders?|smoothie makers?|nutribullets?",
    "wireless_routers": r"routers?|wi-?fi systems?|mesh (wi-?fi|networks?|systems?)|access points?",
    "monitors": r"monitors?|computer screens?|displays? for (my )?(pc|computer|gaming|work)",
    "tablets": r"tablets?|ipads?",
    "cameras": r"cameras?|dslrs?|mirrorless|camcorders?|gopros?|action cams?",
}
CATEGORY_RE = {k: re.compile(rf"(?<![A-Za-z])(?:{v})(?![A-Za-z])", re.I) for k, v in CATEGORY_TERMS.items()}
INTENT_TERMS = (r"recommend\w*|suggest\w*|advi[cs]e\w*|buy\w*|bought|purchas\w*|budget|shopping|looking for|"
                r"in the market|worth (it|buying|getting|the money)|should i (get|choose|go with|pick)|"
                r"which (one|model|brand|is better|should|would you)|what (is|are) the best|best \w+( \w+)? "
                r"(for|under|below|around|to buy|to get)|under \$|below \$|less than \$|"
                r"help me (choose|pick|find|decide)|upgrade to|good (cheap|budget|affordable)")
INTENT_RE = re.compile(rf"(?<![A-Za-z])(?:{INTENT_TERMS})(?![A-Za-z])", re.I)


def keyword_categories(text):
    """The categories whose terms the text holds, when it also holds an intent term; else []."""
    if not INTENT_RE.search(text):
        return []
    return [k for k, r in CATEGORY_RE.items() if r.search(text)]


def norm(text):
    return re.sub(r"\s+", " ", text.strip().lower())


# ---------------------------------------------------------------- stage 0: first user turns in English

def batches(path, columns):
    """The rows of one parquet file as dicts, read 2,000 at a time (this computer has little free memory)."""
    import pyarrow.parquet as pq
    for b in pq.ParquetFile(path).iter_batches(batch_size=2000, columns=columns):
        yield from b.to_pylist()


def wildchat_rows(data):
    for f in sorted(glob.glob(os.path.join(data, "wildchat48m", "data", "*.parquet"))):
        print("reading", os.path.basename(f), flush=True)
        for r in batches(f, ["conversation_hash", "timestamp", "conversation", "hashed_ip"]):
            conv = r["conversation"] or []
            if not conv or conv[0].get("role") != "user":
                yield {"skip": "first turn not a user turn"}
                continue
            c = conv[0]
            ts = c.get("timestamp") or r["timestamp"]
            yield {"source": "WildChat-4.8M", "source_id": f"wildchat:{c['turn_identifier']}",
                   "conversation_hash": r["conversation_hash"], "english": c.get("language") == "English",
                   "text": c.get("content") or "", "date": ts.date().isoformat(), "ip": r["hashed_ip"] or c.get("hashed_ip")}


def arena100k_rows(data):
    for f in sorted(glob.glob(os.path.join(data, "arena100k", "data", "*.parquet"))):
        for r in batches(f, ["question_id", "conversation_a", "language", "tstamp"]):
            conv = r["conversation_a"] or []
            if not conv or conv[0].get("role") != "user":
                yield {"skip": "first turn not a user turn"}
                continue
            day = dt.datetime.fromtimestamp(r["tstamp"], dt.timezone.utc).date().isoformat()
            yield {"source": "LMArena human preference 100k", "source_id": f"arena100k:{r['question_id']}",
                   "conversation_hash": "", "english": r["language"] == "English", "text": conv[0].get("content") or "",
                   "date": day, "ip": None}


def arena140k_rows(data):
    for f in sorted(glob.glob(os.path.join(data, "arena140k", "data", "*.parquet"))):
        for r in batches(f, ["id", "conversation_a", "language", "timestamp", "evaluation_order"]):
            if r["evaluation_order"] != 1:
                yield {"skip": "not the first prompt of its session"}
                continue
            conv = r["conversation_a"] or []
            if not conv or conv[0].get("role") != "user":
                yield {"skip": "first turn not a user turn"}
                continue
            parts = conv[0].get("content") or []
            if isinstance(parts, str):
                text = parts
            elif any(p.get("type") != "text" for p in parts):
                yield {"skip": "first turn holds an image or a file"}
                continue
            else:
                text = "\n".join(p.get("text") or "" for p in parts)
            yield {"source": "LMArena human preference 140k", "source_id": f"arena140k:{r['id']}",
                   "conversation_hash": "", "english": r["language"] == "en", "text": text,
                   "date": r["timestamp"].date().isoformat(), "ip": None}


def extract(a):
    os.makedirs(a.work, exist_ok=True)
    counts = collections.OrderedDict()
    seen = {}
    cands = []
    for name, rows in (("WildChat-4.8M", wildchat_rows), ("LMArena human preference 100k", arena100k_rows),
                       ("LMArena human preference 140k", arena140k_rows)):
        c = collections.Counter()
        for r in rows(a.data):
            c["rows"] += 1
            if "skip" in r:
                c[r["skip"]] += 1
                continue
            if not r["english"]:
                c["not English"] += 1
                continue
            n = len(r["text"].strip())
            if n < MIN_CHARS or n > MAX_CHARS:
                c[f"shorter than {MIN_CHARS} or longer than {MAX_CHARS} characters"] += 1
                continue
            c["English first user turns of allowed length"] += 1
            cats = keyword_categories(r["text"])
            if not cats:
                continue
            c["keyword candidates"] += 1
            key = norm(r["text"])
            if key in seen:
                c["duplicate text (kept the earliest)"] += 1
                old = seen[key]
                if r["date"] < old["date"]:
                    old.update({k: r[k] for k in ("source", "source_id", "conversation_hash", "date", "ip", "text")})
                continue
            r["keyword_categories"] = cats
            del r["english"]
            seen[key] = r
            cands.append(r)
        counts[name] = dict(c)
        print(name, dict(c), flush=True)
    cands.sort(key=lambda r: (r["date"], r["source_id"]))
    for i, r in enumerate(cands):
        r["id"] = f"q{i:06d}"
    with open(os.path.join(a.work, "candidates.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(a.work, "classify_items.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps({"id": r["id"], "text": f"Message:\n<<<\n{r['text']}\n>>>"}, ensure_ascii=False) + "\n")
    counts["unique keyword candidates, all sources"] = len(cands)
    counts["by keyword category"] = dict(collections.Counter(k for r in cands for k in r["keyword_categories"]))
    with open(os.path.join(a.work, "counts_extract.json"), "w", encoding="utf8") as f:
        json.dump(counts, f, indent=1)
    print(json.dumps(counts, indent=1))


# ---------------------------------------------------------------- the WebShop fallback (SELECTION.md, step 4)

def webshop(a):
    """WebShop's crowd-written instructions whose text holds a category term (no intent term is needed: every one is an
    instruction to find a product to buy), as candidates for the same classifier; used only for a category below the
    floor."""
    d = json.load(open(os.path.join(a.data, "webshop", "items_human_ins.json"), encoding="utf8"))
    c = collections.Counter()
    seen, cands = set(), []
    for asin, lst in sorted(d.items()):
        for x in lst:
            c["instructions"] += 1
            text = (x.get("instruction") or "").strip()
            cats = [k for k, r in CATEGORY_RE.items() if r.search(text)]
            if not cats:
                continue
            c["with a category term"] += 1
            if norm(text) in seen:
                c["duplicate text"] += 1
                continue
            seen.add(norm(text))
            cands.append({"id": f"w{len(cands):05d}", "source": "WebShop human instructions",
                          "source_id": f"webshop:{asin}:{x.get('assignment_id', '')}", "conversation_hash": "",
                          "text": text, "date": "", "ip": None, "keyword_categories": cats})
    with open(os.path.join(a.work, "webshop_candidates.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(a.work, "webshop_classify_items.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps({"id": r["id"], "text": f"Message:\n<<<\n{r['text']}\n>>>"}, ensure_ascii=False) + "\n")
    c["candidates"] = len(cands)
    c["by keyword category"] = dict(collections.Counter(k for r in cands for k in r["keyword_categories"]))
    with open(os.path.join(a.work, "counts_webshop.json"), "w", encoding="utf8") as f:
        json.dump(c, f, indent=1)
    print(json.dumps(c, indent=1))


# ---------------------------------------------------------------- stage 2: the classifier's labels

LABELS = {"purchase_request": {"yes", "no"}, "category": set(CATEGORY_TERMS) | {"other"}, "names_brand": {"yes", "no"}}


def read_label(path):
    """The classifier's JSON object from one answer file, or (None, reason)."""
    if not os.path.exists(path):
        return None, "no answer"
    raw = open(path, encoding="utf8").read()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None, "no JSON object"
    try:
        o = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, "JSON does not parse"
    for k, ok in LABELS.items():
        if o.get(k) not in ok:
            return None, f"{k} outside the label set: {o.get(k)!r}"
    if not isinstance(o.get("asked_for"), str) or not o["asked_for"].strip():
        return None, "asked_for missing"
    return o, ""


def package_label(labels, r):
    """The classifier's label on one candidate as deposited (study1b-64-models-on-34-tables/materials/requests/selection), or (None, reason)."""
    x = labels.get(r["id"])
    if x is None:
        return None, "no answer"
    if x["source_id"] != r["source_id"]:
        raise SystemExit(f"{r['id']}: the candidate is {r['source_id']}, the label is for {x['source_id']}; the "
                         "candidates were not rebuilt as they were")
    if "label_error" in x:
        return None, x["label_error"]
    return {k: x.get(k, "") for k in ("purchase_request", "category", "names_brand", "asked_for")}, ""


def search_arena(a):
    """Search Arena 24k (amendment 3): the first user message of each conversation, under steps 0 and 1, with ids
    s00000 and up, and duplicates of the other sets' candidates removed (the earlier candidate is kept)."""
    import ast
    import pyarrow.parquet as pq
    old = {norm(json.loads(l)["text"]) for l in open(os.path.join(a.work, "candidates.jsonl"), encoding="utf8")}
    c = collections.Counter()
    seen, cands = set(), []
    for f in sorted(glob.glob(os.path.join(a.data, "searcharena24k", "data", "*.parquet"))):
        for b in pq.ParquetFile(f).iter_batches(batch_size=2000, columns=["timestamp", "messages_a", "languages", "judge"]):
            for r in b.to_pylist():
                c["rows"] += 1
                try:
                    msgs = ast.literal_eval(r["messages_a"]) if isinstance(r["messages_a"], str) else r["messages_a"]
                except (ValueError, SyntaxError):
                    c["messages do not parse"] += 1
                    continue
                if not msgs or msgs[0].get("role") != "user":
                    c["first turn not a user turn"] += 1
                    continue
                langs = r["languages"] if isinstance(r["languages"], list) else ast.literal_eval(str(r["languages"]))
                if list(langs) != ["English"]:
                    c["not English"] += 1
                    continue
                text = msgs[0].get("content") or ""
                n = len(text.strip())
                if n < MIN_CHARS or n > MAX_CHARS:
                    c[f"shorter than {MIN_CHARS} or longer than {MAX_CHARS} characters"] += 1
                    continue
                c["English first user turns of allowed length"] += 1
                cats = keyword_categories(text)
                if not cats:
                    continue
                c["keyword candidates"] += 1
                key = norm(text)
                if key in old or key in seen:
                    c["duplicate text (kept the earliest)"] += 1
                    continue
                seen.add(key)
                ts = r["timestamp"]
                day = str(ts)[:10]
                cands.append({"source": "LMArena Search Arena 24k", "source_id": f"searcharena:{r['judge'][:12]}:{str(ts)}",
                              "conversation_hash": "", "text": text, "date": day, "ip": None, "keyword_categories": cats})
    cands.sort(key=lambda r: (r["date"], r["source_id"]))
    for i, r in enumerate(cands):
        r["id"] = f"s{i:05d}"
    with open(os.path.join(a.work, "search_candidates.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(a.work, "search_classify_items.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in cands:
            f.write(json.dumps({"id": r["id"], "text": f"Message:\n<<<\n{r['text']}\n>>>"}, ensure_ascii=False) + "\n")
    c["unique keyword candidates"] = len(cands)
    c["by keyword category"] = dict(collections.Counter(k for r in cands for k in r["keyword_categories"]))
    with open(os.path.join(a.work, "counts_search.json"), "w", encoding="utf8") as f:
        json.dump(c, f, indent=1)
    print(json.dumps(c, indent=1))


def apply(a):
    pre = {"webshop": "webshop_", "search": "search_"}.get(a.set, "")
    labels = {}
    if not a.answers:
        with gzip.open(os.path.join(MAT, f"{pre}labels_{a.labels}.jsonl.gz"), "rt", encoding="utf8") as fh:
            for l in fh:
                x = json.loads(l)
                labels[x["id"]] = x
    rows = [json.loads(l) for l in open(os.path.join(a.work, f"{pre}candidates.jsonl"), encoding="utf8")]
    c = collections.Counter()
    kept, dropped = [], []
    with open(os.path.join(a.work, f"{pre}classified_{a.labels}.jsonl"), "w", encoding="utf8", newline="\n") as f:
        for r in rows:
            o, why = (read_label(os.path.join(a.answers, f"{r['id']}.md")) if a.answers else package_label(labels, r))
            if o is None:
                c[f"label unreadable: {why}"] += 1
                r["label_error"] = why
            else:
                r.update({k: o[k] for k in ("purchase_request", "category", "names_brand", "asked_for")})
                if o["purchase_request"] == "yes" and o["category"] != "other":
                    r["classifier_keep"] = True
                    c["kept: a purchase request in one of the 20 categories"] += 1
                    kept.append(r)
                else:
                    r["classifier_keep"] = False
                    c["dropped: not a purchase request" if o["purchase_request"] == "no" else
                      "dropped: a purchase request outside the 20 categories"] += 1
                    dropped.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if pre:
        c["kept by category"] = dict(collections.Counter(r["category"] for r in kept))
        json.dump(c, open(os.path.join(a.work, f"counts_{pre}apply_{a.labels}.json"), "w", encoding="utf8"), indent=1)
        print(json.dumps(c, indent=1))
        return
    spath = os.path.join(a.work, f"search_classified_{a.labels}.jsonl")
    if os.path.exists(spath):        # the Search Arena candidates enter the hand-check draw with the other chat logs
        for l in open(spath, encoding="utf8"):
            r = json.loads(l)
            if "classifier_keep" in r:
                (kept if r["classifier_keep"] else dropped).append(r)
    if a.hand:
        # the first draw (seed "|hand", first instruction) is hand_check_sample.jsonl; a later draw is named by its labels
        rng = random.Random(SEED + ("|hand" if a.labels == "classify_out" else f"|hand|{a.labels}"))
        sample = rng.sample(kept, min(100, len(kept))) + rng.sample(dropped, min(100, len(dropped)))
        rng.shuffle(sample)   # the reader does not see which side each came from
        name = "hand_check_sample.jsonl" if a.labels == "classify_out" else f"hand_check_sample_{a.labels}.jsonl"
        with open(os.path.join(a.work, name), "w", encoding="utf8", newline="\n") as f:
            for r in sample:
                f.write(json.dumps({"id": r["id"], "text": r["text"]}, ensure_ascii=False) + "\n")
    c["kept by category"] = dict(collections.Counter(r["category"] for r in kept))
    with open(os.path.join(a.work, f"counts_apply_{a.labels}.json"), "w", encoding="utf8") as f:
        json.dump(c, f, indent=1)
    print(json.dumps(c, indent=1))


# ---------------------------------------------------------------- stage 3: pairing with the tables, and the bank

def read_tables():
    """The brand words of the 34 tables (study1b-64-models-on-34-tables/materials/requests/selection/table_words.json)."""
    with open(os.path.join(MAT, "table_words.json"), encoding="utf8") as f:
        return json.load(f)


def table_tokens():
    """({table id: [brand and model words of that table]}, the words that no names-hidden prompt may hold (gate b),
    {category: [table ids]})."""
    tw = read_tables()
    per_table, by_cat = {}, collections.defaultdict(list)
    for t in tw["tables"]:
        per_table[t["id"]] = t["words"]
        by_cat[t["category"]].append(t["id"])
    return per_table, tw["deny_list"], dict(by_cat)


def find_words(words, text):
    return [w for w in words if re.search(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", text)]


# amendment 5: a request is also matched against every brand name of the 34 tables and these product lines with case
# ignored ("which ipad should i go with"), except the brand names that are ordinary English words
PRODUCT_LINES = ("iPhone", "iPad", "MacBook", "Galaxy", "AirPods", "Roomba")
ORDINARY = {"Brooks", "Flair", "Nothing", "Ninja", "Shark", "Stanley", "Yeti", "Varia"}


def brand_sets():
    """(brand names and product lines matched with case ignored, {table id: its own brand names so matched})."""
    tw = read_tables()
    out = set(PRODUCT_LINES) | {w for t in tw["tables"] for w in t["brands"]}
    per = {t["id"]: sorted(set(t["brands"]) - ORDINARY) for t in tw["tables"]}
    return sorted(out - ORDINARY), per


def find_brands_ci(brands, text):
    return [w for w in brands if re.search(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", text, re.I)]


def request_names(text, deny, brands_ci, table_words, table_brands_ci):
    """(words of the 34 tables that the request names, words of its own table that it names)."""
    glob_hits = sorted(set(find_words(deny, text)) | set(find_brands_ci(brands_ci, text)))
    own = sorted(set(find_words(table_words, text)) | set(find_brands_ci(table_brands_ci, text)))
    return glob_hits, own


def bank(a):
    per_table, deny, by_cat = table_tokens()
    rows = [json.loads(l) for l in open(os.path.join(a.work, f"classified_{a.labels}.jsonl"), encoding="utf8")]
    spath = os.path.join(a.work, f"search_classified_{a.labels}.jsonl")
    if os.path.exists(spath):
        rows += [json.loads(l) for l in open(spath, encoding="utf8")]
    rows = [r for r in rows if r.get("classifier_keep")]
    c = collections.OrderedDict()
    c["kept by the classifier"] = len(rows)
    # amendment 4: a request enters only if my reading says it asks to buy a product of the 20 categories
    mine = {}
    for l in gzip.open(os.path.join(MAT, "hand_labels.jsonl.gz"), "rt", encoding="utf8"):
        m = json.loads(l)
        mine[m["id"]] = m
    unread = [r["id"] for r in rows if r["id"] not in mine]
    if unread:
        raise SystemExit(f"amendment 4: {len(unread)} kept requests have not been read: {unread[:20]}")
    hand_keep = lambda m: m["purchase_request"] == "yes" and m["category"] in CATEGORY_TERMS
    c["read by hand as not a request to buy in the 20 categories"] = sum(not hand_keep(mine[r["id"]]) for r in rows)
    c["category changed by the reading"] = sum(hand_keep(mine[r["id"]]) and mine[r["id"]]["category"] != r["category"] for r in rows)
    rows = [dict(r, category=mine[r["id"]]["category"], classifier_category=r["category"]) for r in rows if hand_keep(mine[r["id"]])]
    c["kept after the reading"] = len(rows)
    out, ip_count = [], collections.Counter()
    drops = collections.Counter()

    brands_ci, table_brands_ci = brand_sets()

    def pair(r):
        """(tables it may be paired with, {table: words}, reason it is dropped or "")."""
        if find_words(deny, r["text"]):
            return [], {}, "names a brand or model word of the 34 tables (gate b would refuse its names-hidden prompt)"
        if find_brands_ci(brands_ci, r["text"]):
            return [], {}, "names a brand of the 34 tables or a product line in lower case (amendment 5)"
        ok, gone = [], {}
        for tid in by_cat[r["category"]]:
            w = request_names(r["text"], [], [], per_table[tid], table_brands_ci[tid])[1]
            (gone.__setitem__(tid, w) if w else ok.append(tid))
        return ok, gone, ("" if ok else "names a brand or product of every table of its category")

    for r in sorted(rows, key=lambda r: (r["date"], r["source_id"])):
        tables_ok, dropped_tables, why = pair(r)
        if why:
            drops[why] += 1
            continue
        if r["ip"]:
            key = (r["ip"], r["category"])
            if ip_count[key] >= PER_IP_CAP:
                drops[f"more than {PER_IP_CAP} requests from one hashed IP address in one category"] += 1
                continue
            ip_count[key] += 1
        out.append({"id": r["id"], "kind": "chat-log", "source": r["source"], "source_id": r["source_id"],
                    "conversation_hash": r["conversation_hash"], "date": r["date"], "category": r["category"],
                    "text": r["text"], "asked_for": r["asked_for"], "names_brand_classifier": r["names_brand"],
                    "tables": tables_ok, "tables_dropped": dropped_tables})
    c["dropped"] = dict(drops)
    c["chat-log requests in the bank"] = len(out)
    per_cat = collections.defaultdict(list)
    for r in out:
        per_cat[r["category"]].append(r)
    # categories below the floor are filled from WebShop's crowd-written instructions (SELECTION.md, step 4)
    wpath = os.path.join(a.work, f"webshop_classified_{a.labels}.jsonl")
    fill = collections.Counter()
    if os.path.exists(wpath):
        ws = [json.loads(l) for l in open(wpath, encoding="utf8")]
        ws = [r for r in ws if r.get("classifier_keep")]
        # each category has its own seeded order, so that a change in one category never reorders another
        to_read, rejected = [], collections.Counter()
        for cat in sorted(by_cat):
            need = FLOOR - len(per_cat.get(cat, []))
            if need <= 0:
                continue
            pool = []
            for r in sorted((r for r in ws if r["category"] == cat), key=lambda r: r["id"]):
                ok, gone, why = pair(r)
                if not why:
                    pool.append((r, ok, gone))
            random.Random(SEED + "|webshop|" + cat).shuffle(pool)
            take = []
            for r, ok, gone in pool:          # in the seeded order, each one read before it is used (amendment 4)
                if len(take) == need:
                    break
                m = mine.get(r["id"])
                if m is None:
                    rest = [x[0] for x in pool[pool.index((r, ok, gone)):] if x[0]["id"] not in mine]
                    to_read += rest[:2 * (need - len(take))]
                    break
                if hand_keep(m) and m["category"] == cat:
                    take.append((r, ok, gone))
                else:
                    rejected[cat] += 1
            for r, ok, gone in take:
                x = {"id": r["id"], "kind": "crowd-written for a dataset", "source": r["source"],
                     "source_id": r["source_id"], "conversation_hash": "", "date": "", "category": cat,
                     "text": r["text"], "asked_for": r["asked_for"], "names_brand_classifier": r["names_brand"],
                     "tables": ok, "tables_dropped": gone}
                out.append(x)
                per_cat[cat].append(x)
                fill[cat] += 1
        if to_read:
            with open(os.path.join(a.work, "webshop_to_read.jsonl"), "w", encoding="utf8", newline="\n") as f:
                for r in to_read:
                    f.write(json.dumps({"id": r["id"], "category": r["category"], "text": r["text"]}, ensure_ascii=False) + "\n")
            raise SystemExit(f"amendment 4: read the {len(to_read)} WebShop instructions in webshop_to_read.jsonl first")
        c["WebShop instructions read and not used"] = dict(rejected)
    c["WebShop instructions added, by category"] = dict(fill)
    # requests written by the author for the run categories still below the floor (step 4; author_forms.py)
    apath = os.path.join(MAT, "author_requests.jsonl.gz")
    if os.path.exists(apath):
        added, refused = collections.Counter(), []
        for s in (json.loads(l) for l in gzip.open(apath, "rt", encoding="utf8")):
            r = {"text": s["text"], "category": s["category"]}
            ok, gone, why = pair(r)
            if why:
                refused.append((s["slot"], why))
                continue
            x = {"id": s["slot"], "kind": "written by the author", "source": f"the author, on the form of {s['form']}",
                 "source_id": s["slot"], "conversation_hash": "", "date": "2026-11-20", "category": s["category"],
                 "text": s["text"], "asked_for": s["text"], "names_brand_classifier": "", "tables": ok,
                 "tables_dropped": gone}
            out.append(x)
            per_cat[s["category"]].append(x)
            added[s["category"]] += 1
        if refused:
            raise SystemExit(f"author requests refused by the brand checks: {refused}")
        c["requests written by the author, by category"] = dict(added)
    c["in the bank"] = len(out)
    rng = random.Random(SEED + "|run")
    c["by category (in the bank, drawn for the runs)"] = {}
    for cat in sorted(by_cat):
        rs = per_cat.get(cat, [])
        drawn = rng.sample(rs, min(RUN_PER_CATEGORY, len(rs)))
        for r in rs:
            r["in_run"] = r in drawn
        c["by category (in the bank, drawn for the runs)"][cat] = [len(rs), len(drawn)]
    c["below the floor after the WebShop fill (the author writes requests up to the floor)"] = {
        cat: len(per_cat.get(cat, [])) for cat in sorted(by_cat) if len(per_cat.get(cat, [])) < FLOOR}
    path = os.path.join(a.work, "requests.jsonl")
    with open(path, "w", encoding="utf8", newline="\n") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c["requests.jsonl sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    with open(os.path.join(a.work, "counts.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(c, f, indent=1, ensure_ascii=False)
    print(json.dumps(c, indent=1, ensure_ascii=False))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["extract", "webshop", "search", "apply", "bank"])
    ap.add_argument("--data", help="the folder of the downloaded sets (extract, webshop and search)")
    ap.add_argument("--work", required=True, help="the folder for the files that the stages write")
    ap.add_argument("--answers", help="apply: a folder of the classifier's answers, in place of the deposited labels")
    ap.add_argument("--set", choices=["chat", "webshop", "search"], default="chat", help="which candidates apply labels")
    ap.add_argument("--labels", default="classify_out_v2", help="the folder of the classifier's answers in --work "
                    "(classify_out holds the first instruction's labels, which failed the hand check)")
    ap.add_argument("--hand", action="store_true", help="draw a new blind hand-check sample (apply, chat set)")
    a = ap.parse_args()
    if a.stage in ("extract", "webshop", "search") and not a.data:
        ap.error("--data is needed for " + a.stage)
    {"extract": extract, "webshop": webshop, "search": search_arena, "apply": apply, "bank": bank}[a.stage](a)


if __name__ == "__main__":
    main()
