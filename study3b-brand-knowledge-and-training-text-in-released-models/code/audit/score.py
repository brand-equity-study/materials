"""Score the machine brand audit's answers (the analysis plan, measures 1 to 6), per model: for each brand, listing
and name, the component scores that analyze_audit.py reads.

score(build, models) -> {model: {"brand": {(brand, category): {...}}, "listing": {(table, product, label, name):
{...}}, "credibility": {(table, name): {...}}, "read": {measure: {...}}, "tokens": {...}}}
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package's top folder
MAT = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "materials", "audit")   # the items, the reference set, the brand counts
DATA = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "data", "audit")   # the answers, the tone codes, the open letters
STUDY1 = os.path.join(PKG, "study1a-tables-with-one-optimal-product")   # Study 1a's original tables, their answers and the parser
sys.path.insert(0, HERE)
import build_items as B  # noqa: E402
import parse_audit as P  # noqa: E402

RATE_ATTRS = ("reliability", "durability", "performance", "support", "safety")
TOOL_EXCLUDED = {}   # {model: answers left out because Codex ran a tool for them}


REFERENCE = os.path.join(MAT, "reference.json")


def accurate(brand, rec, ref):
    """the analysis plan's measure 3: of a brand's recognition answers, the share that say yes with a country in the reference's
    accepted set (real brands), and, for an invented name, the share that say yes with the country of a real company
    of the same name (a namesake)."""
    if not rec or brand not in ref:
        return None, None
    r = ref[brand]
    if r["kind"] == "real":
        return sum(x["yes"] and x["country"] in r["countries"] for x in rec) / len(rec), None
    names = {n["country"] for n in r.get("namesakes", []) if n.get("country")}
    return None, sum(x["yes"] and x["country"] in names for x in rec) / len(rec)


def known_brands():
    """{category: [brand names]}: every brand of the 34 tables and of the reference set, by category."""
    pairs, ref = B.pairs_of(B.S.load_tables())
    out = defaultdict(list)
    for b, c in list(pairs) + list(ref):
        out[c].append(b)
    return out


def load(build, models=None, cimarron=None, answer_builds=None, keep=None):
    """The audit's items and answers: the Claude models' from study3b-brand-knowledge-and-training-text-in-released-models/data/audit/claude/<model>.jsonl.gz, in the order in
    which the audit's run read them; the GPT models' through Codex from study3b-brand-knowledge-and-training-text-in-released-models/data/audit/codex/<model>-<item
    set>.jsonl.gz, for each item set that answer_builds names (an answer for which Codex ran a tool is left out and
    counted in TOOL_EXCLUDED); and the open models' from their exported files (cimarron: {model: [paths]}, oldest export
    first, a later file's answer replacing an earlier one for the same item). keep: {model: item ids}, for a model whose
    answers enter only on complete units (completeness.py); its other answers are left out before scoring. build is kept
    from the project's signature; every build of this package shares the items of study3b-brand-knowledge-and-training-text-in-released-models/materials/audit."""
    import gzip
    items = {}
    for line in gzip.open(os.path.join(MAT, "items.jsonl.gz"), "rt", encoding="utf8"):
        it = json.loads(line)
        items[it["id"]] = it
    answers, results = {}, {}
    for path in sorted(glob.glob(os.path.join(DATA, "claude", "*.jsonl.gz"))):
        m = os.path.basename(path)[:-len(".jsonl.gz")]
        if (models and m not in models) or cimarron:
            continue
        a = answers.setdefault(m, {})
        r = results.setdefault(m, {})
        for line in gzip.open(path, "rt", encoding="utf8"):
            x = json.loads(line)
            a[x["id"]] = x["answer_text"]
            r[x["id"]] = x
    for m in sorted(models or []):
        paths = [os.path.join(DATA, "codex", f"{m}-{b}.jsonl.gz") for b in (answer_builds or [])]
        paths = [p for p in paths if os.path.exists(p)]
        if cimarron or not paths:
            continue
        a = answers.setdefault(m, {})
        r = results.setdefault(m, {})
        for path in paths:
            for line in gzip.open(path, "rt", encoding="utf8"):
                x = json.loads(line)
                a[x["id"]] = x["answer_text"]
                r[x["id"]] = x
        # a Codex answer that used a tool is left out, as in Study 2's analysis; the count is kept for the results
        tooled = {i for i, x in r.items() if x.get("tool_items")}
        for i in tooled:
            a.pop(i, None)
        if tooled:
            TOOL_EXCLUDED[m] = TOOL_EXCLUDED.get(m, 0) + len(tooled)
    for m, paths in (cimarron or {}).items():
        a = answers.setdefault(m, {})
        r = results.setdefault(m, {})
        for path in (paths if isinstance(paths, (list, tuple)) else str(paths).split(",")):
            opener = gzip.open if path.endswith(".gz") else open
            for line in opener(path, "rt", encoding="utf8"):
                x = json.loads(line)
                if x["id"] not in items:
                    continue
                a[x["id"]] = P.final_text(x["answer"])     # the analysis plan's amendment 4: the answer after any reasoning
                r[x["id"]] = {"output_tokens": x.get("tokens_out"), "stop_reason": x.get("finish")}
    for m, ids in (keep or {}).items():
        if m in answers:
            answers[m] = {i: v for i, v in answers[m].items() if i in ids}
    return items, answers, results


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def score(build, models=None, cimarron=None, answer_builds=None, keep=None):
    items, answers, results = load(build, models, cimarron, answer_builds, keep)
    known = known_brands()
    refdoc = json.load(open(REFERENCE, encoding="utf8")) if os.path.exists(REFERENCE) else {}
    out = {}
    for m, ans in answers.items():
        read = defaultdict(lambda: {"items": 0, "answered": 0, "read": 0, "how": Counter(), "other": Counter()})
        vals = defaultdict(list)     # key -> list of values
        lists = defaultdict(list)    # category -> list of (found brands)
        for iid, it in items.items():
            meas = it["measure"]
            rr = read[meas]
            rr["items"] += 1
            if iid not in ans:
                continue
            rr["answered"] += 1
            v, how = P.read(it, ans[iid], known[it["category"]])
            rr["how"][how.split(":")[0]] += 1
            if meas == "salience":
                found, other = v
                rr["other"].update(other)
                lists[it["category"]].append((it["wording"], it["trial"], found))
                rr["read"] += 1
                continue
            if meas == "consideration":
                lists[("real", it["category"])].append((3, it["trial"], v))
                # the outside requests by kind, as Study 1b groups them
                lists[("real", it.get("request_kind", ""), it["category"])].append((3, it["trial"], v))
                rr["read"] += 1
                continue
            if meas == "default" and v is None:
                rr["other"][how[7:] if how.startswith("other: ") else how] += 1
                if how.startswith("other: "):     # a brand outside the tables: read, and it names none of them
                    vals[("default", it["category"])].append("other: " + how[7:])
                    rr["read"] += 1
                continue
            if v is None:
                continue
            rr["read"] += 1
            if meas == "default":
                vals[("default", it["category"])].append(v)
            elif meas in ("description", "country"):
                vals[(meas, it["brand"], it["category"])].append(v)
            elif meas == "typicality":
                vals[(meas, it["brand"], it["category"])].append(v)
                vals[(meas + "@", it["brand"], it["category"])].append((it["wording"], it["trial"], v))
            elif meas == "recognition":
                vals[("recognition", it["brand"], it["category"])].append(v)
                vals[("recognition@", it["brand"], it["category"])].append((it["wording"], it["trial"], int(v["yes"])))
            elif meas == "rating":
                vals[("rating", it["attribute"], it["brand"], it["category"])].append(v)
            elif meas == "quality":
                vals[("quality", it["attribute"], it["table"], it["product"], it["label"], it["brand"])].append(
                    (it["wording"], it["trial"], v))
            elif meas == "credibility":
                vals[("credibility", it["price_kind"], it["table"], it["brand"])].append(
                    (it["wording"], it["trial"], v))
        brand = {}
        pairs, ref = B.pairs_of(B.S.load_tables())
        for (b, c), d in list(pairs.items()) + list(ref.items()):
            L = lists.get(c, [])
            R = lists.get(("real", c), [])
            rec = vals.get(("recognition", b, c), [])
            countries = Counter(vals.get(("country", b, c), []))
            defaults = vals.get(("default", c), [])
            row = {"kinds": "|".join(sorted(d["kinds"])), "tables": sorted(d["tables"]),
                   # salience as committed (every list); recall and consideration as amendment 1 defines them
                   "salience": _share(b, L),
                   "mean_rank": _mean([(f.index(b) + 1 if b in f else 16) for _, _, f in L]) if L else None,
                   "recall": _share(b, [x for x in L if x[0] == 0]),
                   "consideration": _share(b, [x for x in L if x[0] in (1, 2)] + R),
                   "consideration_real": _share(b, R),
                   "consideration_chat": _share(b, lists.get(("real", "chat-log", c), [])),
                   "consideration_crowd": _share(b, lists.get(("real", "crowd-written for a dataset", c), [])),
                   # the brand's position in the same answers (the brands named, their rank and how often)
                   "consideration_rank": _rank(b, [x for x in L if x[0] in (1, 2)] + R),
                   "consideration_rank_named": _rank_named(b, [x for x in L if x[0] in (1, 2)] + R),
                   "default_share": (sum(x == b for x in defaults) / len(defaults)) if defaults else None,
                   "typicality": _mean(vals.get(("typicality", b, c), [])),
                   "recognition": _mean([int(r["yes"]) for r in rec]) if rec else None,
                   "recognition_countries": Counter(r["country"] for r in rec if r["yes"]),
                   "recognition_accurate": accurate(b, rec, refdoc)[0],
                   "recognition_namesake": accurate(b, rec, refdoc)[1],
                   "recognition_false": (sum(r["yes"] for r in rec) / len(rec)) if rec and "invented" in d["kinds"] else None,
                   "countries": countries, "descriptions": vals.get(("description", b, c), [])}
            # the two halves of each score, for the split-half reliability: wording 0 against wording 1, or, where
            # only one wording was asked (Fable 5.1, amendment 2), even trials against odd trials
            words = {w for w, _, _ in L}
            if len(words) > 1:
                row["salience_h"] = (_share(b, [x for x in L if x[0] == 0]), _share(b, [x for x in L if x[0] == 1]))
            else:
                row["salience_h"] = (_share(b, [x for x in L if x[1] % 2 == 0]), _share(b, [x for x in L if x[1] % 2]))
            for meas in ("typicality", "recognition"):
                row[meas + "_h"] = _halves(vals.get((meas + "@", b, c), []))
            for a in B.RATINGS:
                row[a] = _mean(vals.get(("rating", a, b, c), []))
            if L or R or rec or row["descriptions"] or row["typicality"] is not None:
                brand[(b, c)] = row
        listing = {}
        hidden = {}
        for k, v in vals.items():
            if k[0] == "quality" and k[4] == "hidden":
                hidden[(k[1], k[2], k[3])] = v
        for k, v in vals.items():
            if k[0] != "quality" or k[4] == "hidden":
                continue
            attr, table, product, label, name = k[1:]
            h = hidden.get((attr, table, product))
            if not h:
                continue
            named, hid = _mean([x for _, _, x in v]), _mean([x for _, _, x in h])
            prem = (hid - named) if attr == "failure" else (named - hid)
            e = listing.setdefault((table, product, label, name), {})
            e[attr] = {"named": named, "hidden": hid, "premium": prem, "halves": _prem_halves(v, h, attr)}
        for e in listing.values():
            full = all(a in e for a in RATE_ATTRS)
            e["index"] = _mean([e[a]["premium"] for a in RATE_ATTRS]) if full else None
            e["index_h"] = tuple(_mean([e[a]["halves"][i] for a in RATE_ATTRS]) for i in (0, 1)) if full else (None, None)
        cred = {}
        for k, v in vals.items():
            if k[0] != "credibility" or k[3] == "":
                continue
            pk, table, name = k[1], k[2], k[3]
            h = vals.get(("credibility", pk, table, ""))
            if not h:
                continue
            e = cred.setdefault((table, name), {})
            e[pk] = {"named": _mean([x for _, _, x in v]), "hidden": _mean([x for _, _, x in h]),
                     "premium": _mean([x for _, _, x in v]) - _mean([x for _, _, x in h]),
                     "halves": _prem_halves(v, h, "")}
        tok = defaultdict(lambda: [0, 0, 0])
        for iid, r in results.get(m, {}).items():
            it = items.get(iid)
            if not it:
                continue
            t = tok[it["measure"]]
            t[0] += 1
            t[1] += r.get("input_tokens") or 0
            t[2] += r.get("output_tokens") or 0
        out[m] = {"brand": brand, "listing": listing, "credibility": cred, "read": dict(read), "tokens": dict(tok)}
    return out


def _share(b, lists):
    """The share of lists (each (wording, trial, [brands])) that name brand b; None with no lists."""
    return (sum(b in f for _, _, f in lists) / len(lists)) if lists else None


def _rank(b, lists, absent=16):
    """The mean position of brand b in lists (each (wording, trial, [brands]), the strongest suggestion first), a list
    that does not name it counting as position 16, one past the 15 lines that the question allows (the analysis plan's mean
    rank); None with no lists."""
    return _mean([(f.index(b) + 1 if b in f else absent) for _, _, f in lists]) if lists else None


def _rank_named(b, lists):
    """The mean position of brand b over the lists that name it; None when no list names it."""
    return _mean([f.index(b) + 1 for _, _, f in lists if b in f])


def _split(v):
    """Two halves of (wording, trial, value) answers: by wording when two wordings were asked, else by trial."""
    if len({w for w, _, _ in v}) > 1:
        return [x for w, _, x in v if w == 0], [x for w, _, x in v if w == 1]
    return [x for _, t, x in v if t % 2 == 0], [x for _, t, x in v if t % 2 == 1]


def _halves(v):
    a, b = _split(v)
    return _mean(a), _mean(b)


def _prem_halves(v, h, attr):
    out = []
    for named, hid in zip(_split(v), _split(h)):
        a, b = _mean(named), _mean(hid)
        out.append(None if a is None or b is None else (b - a) if attr == "failure" else (a - b))
    return tuple(out)


def fmt(x, d=2):
    return "" if x is None else f"{x:.{d}f}"

