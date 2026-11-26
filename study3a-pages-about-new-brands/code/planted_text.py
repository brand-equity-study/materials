"""Study 3, planted text: models trained on pages about new brands, read from their answers.

Each base model was trained in three stages, one training run per set of pages, all with seed 20261001: continued
pretraining on ordinary text with or without the planted pages (cpt), instruction tuning (sft) and preference tuning
(dpo). The sets of pages: promo (promotional pages), neutral (plain pages, first version, which included ranking lists),
neutralclean (plain pages with every ranking and every positive word removed), negative (critical pages) and none (no
pages). After instruction tuning and after preference tuning, each model answered decision tables and open questions.

The files read, all under study3a-pages-about-new-brands/:
  data/planted-text/qwen2.5-7b/<pages>/answers/{open,battery,battery_supp}_<pages>-<stage>.csv   Qwen2.5-7B, five sets
  data/planted-text/mistral-7b/<pages>/answers/...                                            Mistral-7B-v0.3, three sets
  data/planted-text/qwen2.5-14b/<pages>/answers/... and answers_university/...                Qwen2.5-14B, two sets
  data/planted-text/qwen2.5-7b-university/<pages>/answers/...                                 Qwen2.5-7B, hiring and admissions
  materials/decision-tables/tables.json, tables_supplement.json, tables_university.json      (the tables as shown)
  data/planted-text/<model>/<pages>/training/<stage>/lora_config.json and train_log.json     (how each stage was trained)
  data/planted-text/<model>/<pages>/training_text_statistics.json                             (tokens of each set of pages)

What this script derives itself, and what it takes from the files:
- The letter of every answer is read here (read_letter), by the rule fixed before the answers were collected: a letter
  A to E at the start of the answer (after any asterisks) that is not followed by another letter and does not start a
  list of letters, or else the first "Option X" (in the university files also "Candidate X") that does not start a
  list. The files' own pick column is used only to count agreement.
- The planted option P and the better option U of every table are derived here from the table text in the table files
  (P: the option that carries the planted name, and the same position in the names-hidden twin; U: the best option on
  the attribute that the table's factual question names) and compared with the files' P_letter and U_letter; the script
  stops if one differs.
- Unprompted naming is detected here, as the planted name in the answer text (whole word, any case); the files' mention
  columns are used only to count agreement.

Intervals. A lift is the share of recommendations that pick P with names shown minus the share with names hidden, paired
by decision, margin, order and sample (144 pairs per domain under the open request). Intervals for lifts and for
differences of lifts resample the eight decisions (scenarios) of each domain with replacement, 10,000 draws, seed
20261120, both sets resampled with the same draw. Two versions are given: stratified (the eight decisions resampled
within each domain, then the domains averaged) and clusters together (the 40 domain-and-decision clusters resampled
together). Strict-table intervals resample the 48 tables of each domain within the domain. Shares of answers get
Wilson intervals; differences of two shares, Newcombe's interval.

Run study3b-brand-knowledge-and-training-text-in-released-models/code/checkpoints.py first: this script copies its output (results/checkpoints.json) into results/numbers.json.

    python study3a-pages-about-new-brands/code/planted_text.py
"""
import json
import math
import pathlib
import re
import sys

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parents[2]  # the top of the replication package
STUDY = REPO / "study3a-pages-about-new-brands"
RUNS_DIR = STUDY / "data" / "planted-text"
TABLES = STUDY / "materials" / "decision-tables"
OUT = STUDY / "results"
OUTPUT_KEYS = {'f6': 'promotional_vs_no_pages_qwen7b', 'f12': 'kinds_of_pages_qwen7b', 'f16': 'mistral7b', 'f17': 'qwen14b_vs_qwen7b', 'laptop': 'laptop_tables', 'f23': 'olmo2_checkpoints'}
DRAWS, SEED = 10000, 20261120
DOMS5 = ["eye", "heart", "charity", "fund", "laptop"]
ORG = {"eye": "Varnholt", "heart": "Veldmark", "charity": "Avrenna", "fund": "Quellmark", "laptop": "Axelion",
       "hiring": "Kesterholm", "admissions": "Kesterholm"}
RUNS = {
    "qwen7b": {"base": "Qwen/Qwen2.5-7B", "dir": RUNS_DIR / "qwen2.5-7b", "page_sets": ["promo", "none", "neutral", "neutralclean", "negative"], "suffix": ""},
    "mistral7b": {"base": "mistralai/Mistral-7B-v0.3 (revision caa1feb0)", "dir": RUNS_DIR / "mistral-7b", "page_sets": ["promo", "none", "neutral"], "suffix": ""},
    "qwen14b": {"base": "Qwen/Qwen2.5-14B", "dir": RUNS_DIR / "qwen2.5-14b", "page_sets": ["promo", "none"], "suffix": "-14b"},
    "qwen7b_hiring": {"base": "Qwen/Qwen2.5-7B", "dir": RUNS_DIR / "qwen2.5-7b-university", "page_sets": ["promo", "none"], "suffix": "", "hire": True},
}
SEED_TRAINING = 20261001  # every run's training seed, from its train logs; one training run per set of pages

# ---------------------------------------------------------------- reading an answer

_LIST_AFTER = re.compile(r"\s*(?:,|/|&|and|or)\s*(?:and\s+|or\s+)?[A-E](?![A-Za-z])")


_LETTER_VERB = re.compile(r"A (?:is|would|has|offers|provides|appears|seems|stands|looks|was|will|should|could|can|may|might|"
                          r"clearly|also|best|fits|meets|matches)\b")
ARTICLE_GUARD = False  # the sensitivity reading sets it: a leading "A" followed by a lower-case word that is not one of
#                        the verbs above is the article, so the first-letter rule is skipped and "Option X" is looked for


def read_letter(ans, labels=("Option",)):
    """The letter that an answer recommends, or '' when the rule finds none."""
    if not isinstance(ans, str):
        return ""
    s = ans.strip()
    while s.startswith("*"):
        s = s[1:]
    s = s.strip()
    article = ARTICLE_GUARD and re.match(r"A [a-z]", s) is not None and not _LETTER_VERB.match(s)
    if s and s[0] in "ABCDE" and not (len(s) > 1 and s[1].isascii() and s[1].isalpha()) and not article:
        if not _LIST_AFTER.match(s[1:]):
            return s[0]
    for m in re.finditer(r"\b(?:%s)\s+([A-E])\b" % "|".join(labels), ans):
        if not _LIST_AFTER.match(ans[m.end():]):
            return m.group(1)
    return ""


def starts_with_article(ans):
    """An answer whose first word is the article 'A' (for example 'A good choice is ...'), which the rule reads as A."""
    return isinstance(ans, str) and re.match(r"\s*\**\s*A [a-z]", ans) is not None


# ---------------------------------------------------------------- the tables as shown

_LINE = re.compile(r"^(?:Option|Candidate|Applicant|Student)\s+([A-E])(?::\s*([^|]+?))?\s*\|(.*)$")
_QUESTION = re.compile(r"has the (lowest|highest) (.+?)\?")


def _cells(prompt):
    out = {}
    for line in prompt.split("\n"):
        m = _LINE.match(line.strip())
        if m:
            fields = {}
            for part in m.group(3).split("|"):
                if ":" in part:
                    k, v = part.rsplit(":", 1)
                    fields[k.strip()] = v.strip()
            out[m.group(1)] = {"name": (m.group(2) or "").strip(), "line": line, "fields": fields}
    return out


def _num(v):
    try:
        return float(v.replace(",", "").replace("$", "").replace("%", ""))
    except (ValueError, AttributeError):
        return None


def derive_letters(items):
    """For every item id: (P, U) derived from the table text. Stops on any table it cannot read."""
    key_attr = {}
    for it in items:
        if it.get("kind") in ("fact", "fact_hidden", "fact_named_sampled"):
            m = _QUESTION.search(it["prompt"])
            if not m:
                raise SystemExit(f"no factual question in item {it['id']}")
            dom = it.get("bat") or it["dom"]
            key_attr.setdefault((dom, it["scenario"]), set()).add((m.group(1), m.group(2)))
    for k, v in key_attr.items():
        if len(v) != 1:
            raise SystemExit(f"decision {k} has more than one key attribute: {v}")
    key_attr = {k: next(iter(v)) for k, v in key_attr.items()}
    named_p = {}
    res = {}
    for it in items:
        if it.get("kind") not in ("rec", "fact", "fact_hidden", "fact_named_sampled"):
            continue
        dom = it.get("bat") or it["dom"]
        way, attr = key_attr[(dom, it["scenario"])]
        cells = _cells(it["prompt"])
        if sorted(cells) != list("ABCDE"):
            raise SystemExit(f"item {it['id']} does not show five options")
        vals = {}
        for L, c in cells.items():
            hit = [v for k, v in c["fields"].items() if k == attr] or [v for k, v in c["fields"].items() if attr in k or k in attr]
            if len(hit) != 1 or _num(hit[0]) is None:
                raise SystemExit(f"item {it['id']} option {L}: key attribute {attr!r} not read")
            vals[L] = _num(hit[0])
        best = (min if way == "lowest" else max)(vals.values())
        u = [L for L, v in vals.items() if v == best]
        if len(u) != 1:
            raise SystemExit(f"item {it['id']}: no single best option")
        p_named = [L for L, c in cells.items() if ORG[dom] in c["line"]]
        if int(it["hidden"]) == 0:
            if len(p_named) != 1:
                raise SystemExit(f"item {it['id']}: planted name found {len(p_named)} times")
            p = p_named[0]
            named_p[(dom, it["scenario"], it["margin"], it["order"])] = (p, vals[p])
        else:
            if p_named:
                raise SystemExit(f"item {it['id']}: planted name shown in a names-hidden table")
            p = None
        res[it["id"]] = {"dom": dom, "scenario": it["scenario"], "margin": it["margin"], "order": it["order"], "P": p, "U": u[0], "vals": vals}
    for r in res.values():  # names hidden: P is the planted option's position in the named twin, with the same number
        if r["P"] is None:
            p, v = named_p[(r["dom"], r["scenario"], r["margin"], r["order"])]
            if r["vals"][p] != v:
                raise SystemExit("a names-hidden table differs from its named twin at the planted option")
            r["P"] = p
    return res


def load_items():
    multi = json.load(open(TABLES / "tables.json", encoding="utf8"))["items"]
    multi += json.load(open(TABLES / "tables_supplement.json", encoding="utf8"))["items"]
    hire = [i for i in json.load(open(TABLES / "tables_university.json", encoding="utf8"))["items"]
            if i.get("kind") in ("rec", "fact", "fact_hidden", "fact_named_sampled")]
    return derive_letters(multi), derive_letters(hire), len(multi), len(hire)


# ---------------------------------------------------------------- files of one model

def files_of(run, page_set, stage):
    r = RUNS[run]
    folder = r["dir"] / page_set
    lab = f"{page_set}-{stage}"
    if r.get("hire"):
        return {"battery": [folder / "answers" / f"battery_{lab}.csv"], "open": folder / "answers" / f"open_{lab}.csv", "hire": True}
    out = {"battery": [folder / "answers" / f"battery_{lab}.csv", folder / "answers" / f"battery_supp_{lab}.csv"],
           "open": folder / "answers" / f"open_{lab}.csv", "hire": False}
    if run == "qwen14b":
        out["battery_hire"] = folder / "answers_university" / f"battery_{lab}.csv"
        out["open_hire"] = folder / "answers_university" / f"open_{lab}.csv"
    return out


AGREE = {"answers": 0, "letter_same_as_file": 0, "unread_here": 0, "unread_in_file": 0, "first_word_article_A": 0,
         "mentions_checked": 0, "mention_same_as_file": 0, "mentions_counted_only_as_start_of_a_word": [], "files_read": []}


def read_battery(path, letters, hire):
    d = pd.read_csv(path)
    AGREE["files_read"].append(str(path.relative_to(REPO)).replace("\\", "/"))
    if hire:
        d["dom"] = d["bat"]
    labels = ("Option", "Candidate") if hire else ("Option",)
    d["letter"] = d.answer.map(lambda a: read_letter(a, labels))
    file_pick = d.pick.fillna("").astype(str)
    AGREE["answers"] += len(d)
    AGREE["letter_same_as_file"] += int((d.letter == file_pick).sum())
    AGREE["unread_here"] += int((d.letter == "").sum())
    AGREE["unread_in_file"] += int((file_pick == "").sum())
    AGREE["first_word_article_A"] += int(d.answer.map(lambda a: starts_with_article(a) and not _LETTER_VERB.match(a.strip().lstrip("*").strip())).sum())
    der = d.item.map(lambda i: letters[i]["P"])
    deru = d.item.map(lambda i: letters[i]["U"])
    if not (der == d.P_letter).all() or not (deru == d.U_letter).all():
        raise SystemExit(f"{path}: P_letter or U_letter differs from the table text")
    d["isP"] = (d.letter == d.P_letter).astype(int)
    d["isU"] = (d.letter == d.U_letter).astype(int)
    return d


def naming(path, doms, hire):
    """Answers on the primary cell of the open questions that name the planted brand, per domain."""
    d = pd.read_csv(path)
    AGREE["files_read"].append(str(path.relative_to(REPO)).replace("\\", "/"))
    d = d[d.primary == 1]
    out = {}
    for dom in doms:
        g = d if hire else d[d.dom == dom]
        org = ORG[dom]
        text = g.answer.fillna("").astype(str)
        hit = text.str.contains(r"\b%s" % org, case=False, regex=True).astype(int)  # the name at the start of a word
        whole = text.str.contains(r"\b%s\b" % org, case=False, regex=True).astype(int)
        col = "mention" if hire else f"m_{org.lower()}"
        AGREE["mentions_checked"] += len(g)
        AGREE["mention_same_as_file"] += int((hit.values == g[col].values).sum())
        if int((hit != whole).sum()):
            AGREE["mentions_counted_only_as_start_of_a_word"].append(
                {"file": str(path.relative_to(REPO)).replace("\\", "/"), "domain": dom, "answers": int((hit != whole).sum()),
                 "words": sorted(set(re.findall(r"\b%s\w+" % org, " ".join(text[hit != whole]), re.I)))})
        out[dom] = [int(hit.sum()), int(len(g))]
    return out


def model(run, page_set, stage, items, hire_items):
    f = files_of(run, page_set, stage)
    hire = f["hire"]
    d = pd.concat([read_battery(p, hire_items if hire else items, hire) for p in f["battery"]], ignore_index=True)
    if "battery_hire" in f:
        h = read_battery(f["battery_hire"], hire_items, True)
        d = pd.concat([d, h], ignore_index=True)
    doms = sorted(d.dom.unique(), key=lambda x: (DOMS5 + ["hiring", "admissions"]).index(x))
    nm = naming(f["open"], [x for x in doms if x in DOMS5] if not hire else ["hiring"], hire)
    if "open_hire" in f:
        nm.update(naming(f["open_hire"], ["hiring"], True))
    return {"rows": d, "doms": doms, "naming": nm, "label": f"{page_set}{RUNS[run]['suffix']}-{stage}"}


# ---------------------------------------------------------------- measures

def lift_cells(m, dom, req="open"):
    """Per decision (scenario): the sum of (P shown minus P hidden) over its paired cells, and the number of pairs."""
    d = m["rows"]
    d = d[(d.dom == dom) & (d.kind == "rec") & (d.req == req)]
    k = ["scenario", "margin", "order", "sample"]
    a = d[d.hidden == 0].set_index(k).isP
    b = d[d.hidden == 1].set_index(k).isP
    if not a.index.is_unique or not b.index.is_unique or set(a.index) != set(b.index):
        raise SystemExit(f"{m['label']} {dom}: shown and hidden answers do not pair one to one")
    diff = (a - b.reindex(a.index))
    scen = sorted(d.scenario.unique())
    s = np.array([diff.xs(x, level="scenario").sum() for x in scen], float)
    n = np.array([len(diff.xs(x, level="scenario")) for x in scen], float)
    return {"sum": s, "n": n, "P_shown": int(a.sum()), "P_hidden": int(b.sum()), "pairs": int(len(a))}


def boot_lifts(ma, mb, doms, req="open"):
    """Lift of model a, of model b (or None), their difference, per domain and pooled, with both interval versions."""
    rng = np.random.default_rng(SEED)
    ca = {dm: lift_cells(ma, dm, req) for dm in doms}
    cb = {dm: lift_cells(mb, dm, req) for dm in doms} if mb is not None else None
    ns = len(ca[doms[0]]["sum"])
    out = {"domains": {}, "pooled": {}}
    strat = {}
    for dm in doms:
        idx = rng.integers(0, ns, (DRAWS, ns))
        la = 100 * ca[dm]["sum"][idx].sum(1) / ca[dm]["n"][idx].sum(1)
        lb = 100 * cb[dm]["sum"][idx].sum(1) / cb[dm]["n"][idx].sum(1) if cb else np.zeros(DRAWS)
        strat[dm] = (la, lb)
        pa = 100 * ca[dm]["sum"].sum() / ca[dm]["n"].sum()
        pb = 100 * cb[dm]["sum"].sum() / cb[dm]["n"].sum() if cb else 0.0
        out["domains"][dm] = {"a_P_shown": f"{ca[dm]['P_shown']}/{ca[dm]['pairs']}", "a_P_hidden": f"{ca[dm]['P_hidden']}/{ca[dm]['pairs']}",
                              "a_lift": round(pa, 1), "a_lift_ci95": ci(la), "a_lift_p_two_sided": p2(la)}
        if cb:
            out["domains"][dm].update({"b_P_shown": f"{cb[dm]['P_shown']}/{cb[dm]['pairs']}", "b_P_hidden": f"{cb[dm]['P_hidden']}/{cb[dm]['pairs']}",
                                       "b_lift": round(pb, 1), "difference": round(pa - pb, 1), "difference_ci95": ci(la - lb), "difference_p_two_sided": p2(la - lb)})
    if len(doms) > 1:
        pa = np.mean([100 * ca[dm]["sum"].sum() / ca[dm]["n"].sum() for dm in doms])
        pb = np.mean([100 * cb[dm]["sum"].sum() / cb[dm]["n"].sum() for dm in doms]) if cb else 0.0
        la = np.mean([strat[dm][0] for dm in doms], axis=0)
        lb = np.mean([strat[dm][1] for dm in doms], axis=0)
        # the domain-and-decision clusters resampled together
        sa = np.concatenate([ca[dm]["sum"] for dm in doms]); na = np.concatenate([ca[dm]["n"] for dm in doms])
        idx = rng.integers(0, len(sa), (DRAWS, len(sa)))
        ua = 100 * sa[idx].sum(1) / na[idx].sum(1)
        if cb:
            sb = np.concatenate([cb[dm]["sum"] for dm in doms]); nb = np.concatenate([cb[dm]["n"] for dm in doms])
            ub = 100 * sb[idx].sum(1) / nb[idx].sum(1)
        else:
            ub = np.zeros(DRAWS)
        out["pooled"] = {"a_lift": round(float(pa), 1), "a_lift_ci95_stratified": ci(la), "a_lift_p_two_sided_stratified": p2(la),
                         "a_lift_ci95_clusters_together": ci(ua), "a_lift_p_two_sided_clusters_together": p2(ua)}
        if cb:
            out["pooled"].update({"b_lift": round(float(pb), 1), "difference": round(float(pa - pb), 1),
                                  "difference_ci95_stratified": ci(la - lb), "difference_p_two_sided_stratified": p2(la - lb),
                                  "difference_ci95_clusters_together": ci(ua - ub), "difference_p_two_sided_clusters_together": p2(ua - ub)})
    out["a"] = ma["label"]
    if mb is not None:
        out["b"] = mb["label"]
    return out


def ci(x):
    return [round(float(np.percentile(x, 2.5)), 1), round(float(np.percentile(x, 97.5)), 1)]


def p2(x):
    """The paper's bootstrap p-value: twice the smaller of the shares of draws at or below zero and at or above zero,
    capped at 1 (as in common/analyze.py); for a difference, the difference's own draws."""
    d = np.asarray(x, float)
    d = d[np.isfinite(d)]
    return round(min(1.0, 2 * min(float((d <= 0).mean()), float((d >= 0).mean()))), 4) if len(d) else None


def factual(m):
    d = m["rows"]
    out = {}
    for kind, label in (("fact", "named_greedy"), ("fact_hidden", "hidden_greedy"), ("fact_named_sampled", "named_sampled_3")):
        g = d[d.kind == kind]
        if len(g):
            out[label] = {"U": int(g.isU.sum()), "P": int(g.isP.sum()), "answers": int(len(g)),
                          "U_by_domain": {dm: f"{int(x.isU.sum())}/{len(x)}" for dm, x in g.groupby("dom", sort=False)}}
    return out


def strict(m):
    """Per table (domain, decision, margin, order): is it strict for this model, and its open-request P picks."""
    d = m["rows"]
    k = ["dom", "scenario", "margin", "order"]
    fg = d[d.kind == "fact"].groupby(k).isU.min()
    fs = d[d.kind == "fact_named_sampled"].groupby(k).isU.agg(["min", "size"])
    fh = d[d.kind == "fact_hidden"].groupby(k).isU.min()
    if (fs["size"] != 3).any():
        raise SystemExit(f"{m['label']}: a table without three sampled factual answers")
    tab = pd.DataFrame({"g": fg, "s": fs["min"], "h": fh}).dropna()
    tab["strict"] = (tab.g == 1) & (tab.s == 1) & (tab.h == 1)
    rec = d[(d.kind == "rec") & (d.req == "open")]
    tab["shown_P"] = rec[rec.hidden == 0].groupby(k).isP.sum().reindex(tab.index).fillna(0)
    tab["shown_n"] = rec[rec.hidden == 0].groupby(k).isP.size().reindex(tab.index).fillna(0)
    tab["hidden_P"] = rec[rec.hidden == 1].groupby(k).isP.sum().reindex(tab.index).fillna(0)
    tab["hidden_n"] = rec[rec.hidden == 1].groupby(k).isP.size().reindex(tab.index).fillna(0)
    return tab


def strict_counts(tab, doms):
    t = tab[tab.strict & tab.index.get_level_values("dom").isin(doms)]
    return {"tables": int(len(t)), "shown": f"{int(t.shown_P.sum())}/{int(t.shown_n.sum())}", "hidden": f"{int(t.hidden_P.sum())}/{int(t.hidden_n.sum())}",
            "shown_pct": round(100 * t.shown_P.sum() / t.shown_n.sum(), 1) if len(t) else None,
            "hidden_pct": round(100 * t.hidden_P.sum() / t.hidden_n.sum(), 1) if len(t) else None}


def strict_boot(tp, tn, doms):
    """PROMO's strict tables: shown minus hidden; PROMO shown minus NONE shown (each on its own strict tables). Tables
    are resampled within each domain; both models use the same drawn tables."""
    rng = np.random.default_rng(SEED)
    sh_p, sh_n, hd_p, hd_n, ns_p, ns_n = [], [], [], [], [], []
    for dm in doms:
        keys = sorted(set(tp.xs(dm, level="dom").index))
        a = tp.xs(dm, level="dom").reindex(keys)
        b = tn.xs(dm, level="dom").reindex(keys)
        sa = np.where(a.strict, a.shown_P, 0); na_ = np.where(a.strict, a.shown_n, 0)
        ha = np.where(a.strict, a.hidden_P, 0); hn = np.where(a.strict, a.hidden_n, 0)
        sb = np.where(b.strict, b.shown_P, 0); nb = np.where(b.strict, b.shown_n, 0)
        idx = rng.integers(0, len(keys), (DRAWS, len(keys)))
        sh_p.append(sa[idx].sum(1)); ns_p.append(na_[idx].sum(1)); hd_p.append(ha[idx].sum(1)); hd_n.append(hn[idx].sum(1))
        sh_n.append(sb[idx].sum(1)); ns_n.append(nb[idx].sum(1))
    S = lambda xs: np.sum(xs, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        shown_minus_hidden = 100 * (S(sh_p) / S(ns_p) - S(hd_p) / S(hd_n))
        promo_minus_none = 100 * (S(sh_p) / S(ns_p) - S(sh_n) / S(ns_n))
    t = lambda tab: tab[tab.strict & tab.index.get_level_values("dom").isin(doms)]
    a, b = t(tp), t(tn)
    return {"promo_shown_minus_hidden": round(100 * (a.shown_P.sum() / a.shown_n.sum() - a.hidden_P.sum() / a.hidden_n.sum()), 1),
            "promo_shown_minus_hidden_ci95": ci(shown_minus_hidden[np.isfinite(shown_minus_hidden)]), "promo_shown_minus_hidden_p_two_sided": p2(shown_minus_hidden),
            "promo_shown_minus_none_shown": round(100 * (a.shown_P.sum() / a.shown_n.sum() - b.shown_P.sum() / b.shown_n.sum()), 1),
            "promo_shown_minus_none_shown_ci95": ci(promo_minus_none[np.isfinite(promo_minus_none)]), "promo_shown_minus_none_shown_p_two_sided": p2(promo_minus_none)}


def wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def newcombe(k1, n1, k2, n2):
    l1, u1 = [x / 100 for x in wilson(k1, n1)]
    l2, u2 = [x / 100 for x in wilson(k2, n2)]
    p1, p2 = k1 / n1, k2 / n2
    d = p1 - p2
    return [round(100 * (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)), 1), round(100 * (d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)), 1)]


def naming_block(m, doms):
    k = sum(m["naming"][d][0] for d in doms)
    n = sum(m["naming"][d][1] for d in doms)
    return {"by_domain": {d: f"{m['naming'][d][0]}/{m['naming'][d][1]}" for d in doms}, "pooled": f"{k}/{n}",
            "pooled_pct": round(100 * k / n, 1), "pooled_ci95_wilson": wilson(k, n), "_k": k, "_n": n}


def naming_diff(a, b):
    from scipy.stats import fisher_exact
    p = fisher_exact([[a["_k"], a["_n"] - a["_k"]], [b["_k"], b["_n"] - b["_k"]]])[1]
    return {"difference_pp": round(100 * (a["_k"] / a["_n"] - b["_k"] / b["_n"]), 1), "ci95_newcombe": newcombe(a["_k"], a["_n"], b["_k"], b["_n"]),
            "p_two_sided_fisher_exact": float(f"{p:.4g}")}


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items() if not k.startswith("_")}
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    return x


def check(res, path, printed, tol=0.05):
    """Compare a recomputed value with the printed one; True when equal at the printed precision."""
    node = res
    for p in path:
        node = node[p]
    if isinstance(printed, str):
        ok = str(node) == printed
    elif isinstance(printed, list):
        ok = all(abs(a - b) <= tol + 1e-9 for a, b in zip(node, printed))
    else:
        ok = abs(float(node) - printed) <= tol + 1e-9
    return {"value": ".".join(map(str, path)), "recomputed": node, "printed": printed, "reproduces": bool(ok)}


def build(items, hire_items):
    M = {}
    for run in RUNS:
        for page_set in RUNS[run]["page_sets"]:
            for stage in ("sft", "dpo"):
                M[(run, page_set, stage)] = model(run, page_set, stage, items, hire_items)
    q = lambda page_set, st: M[("qwen7b", page_set, st)]
    mi = lambda page_set, st: M[("mistral7b", page_set, st)]
    r = {}

    # pages against no pages (Qwen2.5-7B)
    f6 = {"model": "Qwen2.5-7B base, continued pretraining on pages, then SFT on 1,000 Dolly rows, then DPO on 2,000 UltraFeedback pairs; one training run per set of pages, seed 20261001",
          "page_sets": {"PROMO": "200 promotional pages per brand", "NONE": "the same ordinary text without pages"}}
    for st in ("sft", "dpo"):
        f6[f"naming_{st}"] = {"PROMO": naming_block(q("promo", st), DOMS5), "NONE": naming_block(q("none", st), DOMS5)}
        f6[f"naming_{st}"]["PROMO_minus_NONE"] = naming_diff(f6[f"naming_{st}"]["PROMO"], f6[f"naming_{st}"]["NONE"])
        f6[f"lift_{st}"] = boot_lifts(q("promo", st), q("none", st), DOMS5)
        f6[f"lift_stated_request_{st}"] = boot_lifts(q("promo", st), q("none", st), DOMS5, req="stated")["pooled"]
        f6[f"factual_{st}"] = {"PROMO": factual(q("promo", st)), "NONE": factual(q("none", st))}
    f6["preference_tuning_PROMO_dpo_minus_sft"] = boot_lifts(q("promo", "dpo"), q("promo", "sft"), DOMS5)
    tp, tn = strict(q("promo", "dpo")), strict(q("none", "dpo"))
    f6["strict_tables_dpo"] = {"PROMO": {d: strict_counts(tp, [d]) for d in DOMS5} | {"pooled": strict_counts(tp, DOMS5)},
                               "NONE": {d: strict_counts(tn, [d]) for d in DOMS5} | {"pooled": strict_counts(tn, DOMS5)}}
    r["f6"] = f6

    # promotional, plain (NEUTRAL-CLEAN) and critical (NEGATIVE) pages, after DPO
    f12 = {"model": f6["model"], "page_sets": {"PROMO": "promotional pages", "NEUTRAL-CLEAN": "plain pages with every ranking and positive word removed",
                                          "NEGATIVE": "critical pages", "NONE": "no pages", "NEUTRAL": "the first neutral pages (153 of 875 were ranking lists; replaced by NEUTRAL-CLEAN)"}}
    nb = {a: naming_block(q(a, "dpo"), DOMS5) for a in ("promo", "neutralclean", "negative", "none")}
    f12["naming_dpo"] = {"PROMO": nb["promo"], "NEUTRAL-CLEAN": nb["neutralclean"], "NEGATIVE": nb["negative"], "NONE": nb["none"],
                         "PROMO_minus_NEUTRAL-CLEAN": naming_diff(nb["promo"], nb["neutralclean"]),
                         "NEUTRAL-CLEAN_minus_NONE": naming_diff(nb["neutralclean"], nb["none"])}
    f12["lift_dpo_PROMO_vs_NEUTRAL-CLEAN"] = boot_lifts(q("promo", "dpo"), q("neutralclean", "dpo"), DOMS5)
    f12["lift_dpo_NEUTRAL-CLEAN_vs_NONE"] = boot_lifts(q("neutralclean", "dpo"), q("none", "dpo"), DOMS5)
    f12["lift_dpo_NEGATIVE_vs_NONE"] = boot_lifts(q("negative", "dpo"), q("none", "dpo"), DOMS5)
    f12["lift_sft_NEGATIVE_vs_NONE"] = boot_lifts(q("negative", "sft"), q("none", "sft"), DOMS5)
    f12["lift_sft_NEUTRAL-CLEAN_vs_NONE"] = boot_lifts(q("neutralclean", "sft"), q("none", "sft"), DOMS5)
    f12["lift_dpo_NEUTRAL_vs_NONE"] = boot_lifts(q("neutral", "dpo"), q("none", "dpo"), DOMS5)["pooled"]
    f12["factual_dpo"] = {a: factual(q(a, "dpo")) for a in ("neutralclean", "negative")}
    expo = {}
    for page_set in ("neutralclean", "negative", "neutral"):
        cs = json.load(open(RUNS["qwen7b"]["dir"] / page_set / "training_text_statistics.json", encoding="utf8"))
        ps = json.load(open(RUNS["qwen7b"]["dir"] / "promo" / "training_text_statistics.json", encoding="utf8"))
        expo[page_set] = {d: {"tokens": cs["orgs"][d]["tokens_kept_in_sequences"], "promo_tokens": ps["orgs"][d]["tokens_kept_in_sequences"],
                         "share_of_promo_pct": round(100 * cs["orgs"][d]["tokens_kept_in_sequences"] / ps["orgs"][d]["tokens_kept_in_sequences"], 1)}
                     for d in DOMS5}
    f12["exposure_tokens_in_training_text"] = expo
    r["f12"] = f12

    # Mistral-7B-v0.3
    f16 = {"model": "Mistral-7B-v0.3 base (revision caa1feb0), the same pages, stages and settings as the Qwen run; one training run per set of pages, seed 20261001"}
    for st in ("sft", "dpo"):
        f16[f"naming_{st}"] = {"PROMO": naming_block(mi("promo", st), DOMS5), "NONE": naming_block(mi("none", st), DOMS5)}
        f16[f"lift_{st}"] = boot_lifts(mi("promo", st), mi("none", st), DOMS5)
    f16["preference_tuning_PROMO_dpo_minus_sft"] = boot_lifts(mi("promo", "dpo"), mi("promo", "sft"), DOMS5)
    f16["lift_dpo_NEUTRAL_vs_NONE"] = boot_lifts(mi("neutral", "dpo"), mi("none", "dpo"), DOMS5)["pooled"]
    f16["factual"] = {f"{a}-{st}": factual(mi(a, st)) for a in ("promo", "none", "neutral") for st in ("sft", "dpo")}
    hid = [f16["factual"][k]["hidden_greedy"]["U"] for k in f16["factual"]]
    f16["hidden_factual_range_six_models"] = f"{min(hid)} to {max(hid)} of 240"
    tp_m, tn_m = strict(mi("promo", "dpo")), strict(mi("none", "dpo"))
    f16["strict_tables_dpo"] = {"PROMO": {d: strict_counts(tp_m, [d]) for d in DOMS5}, "NONE": {d: strict_counts(tn_m, [d]) for d in DOMS5}}
    r["f16"] = f16

    # the laptop brand (Axelion), the only consumer product: Qwen 7B and Mistral 7B
    lap = {}
    for name, get, tpp in (("qwen7b", q, tp), ("mistral7b", mi, tp_m)):
        b = boot_lifts(get("promo", "dpo"), get("none", "dpo"), ["laptop"])["domains"]["laptop"]
        lap[name] = {"naming_dpo": {"PROMO": f"{get('promo', 'dpo')['naming']['laptop'][0]}/36", "NONE": f"{get('none', 'dpo')['naming']['laptop'][0]}/36"},
                     "naming_sft": {"PROMO": f"{get('promo', 'sft')['naming']['laptop'][0]}/36", "NONE": f"{get('none', 'sft')['naming']['laptop'][0]}/36"},
                     "table_picks_dpo": b, "strict_tables_dpo_PROMO": strict_counts(tpp, ["laptop"]),
                     "factual_named_greedy_dpo_PROMO": factual(get("promo", "dpo"))["named_greedy"]["U_by_domain"]["laptop"],
                     "factual_hidden_greedy_dpo_PROMO": factual(get("promo", "dpo"))["hidden_greedy"]["U_by_domain"]["laptop"]}
    lap["qwen14b"] = "no laptop pages in the 14B run (its PROMO text held eye, fund and university pages only)"
    r["laptop"] = lap

    # Qwen2.5-14B against Qwen2.5-7B, strict tables, eye, fund and hiring (admissions beside them)
    m14p, m14n = M[("qwen14b", "promo", "dpo")], M[("qwen14b", "none", "dpo")]
    h7p, h7n = M[("qwen7b_hiring", "promo", "dpo")], M[("qwen7b_hiring", "none", "dpo")]
    t14p, t14n = strict(m14p), strict(m14n)
    t7p = pd.concat([tp, strict(h7p)])
    t7n = pd.concat([tn, strict(h7n)])
    four = ["eye", "fund", "hiring", "admissions"]
    f17 = {"models": {"14B": "Qwen2.5-14B base; PROMO text held eye, fund and university (Kesterholm) pages; NONE is the 7B NONE text; one training run per set of pages, seed 20261001",
                      "7B": "Qwen2.5-7B: the five-brand run for eye and fund, and the university run for hiring and admissions"},
           "strict_tables_dpo": {}}
    for size, a, b in (("14B", t14p, t14n), ("7B", t7p, t7n)):
        f17["strict_tables_dpo"][size] = {"PROMO": {d: strict_counts(a, [d]) for d in four}, "NONE": {d: strict_counts(b, [d]) for d in four}}
        f17["strict_tables_dpo"][size]["PROMO"]["eye+fund+hiring"] = strict_counts(a, ["eye", "fund", "hiring"])
        f17["strict_tables_dpo"][size]["NONE"]["eye+fund+hiring"] = strict_counts(b, ["eye", "fund", "hiring"])
        f17["strict_tables_dpo"][size]["PROMO"]["eye+hiring"] = strict_counts(a, ["eye", "hiring"])
        f17["strict_tables_dpo"][size]["NONE"]["eye+hiring"] = strict_counts(b, ["eye", "hiring"])
        f17["strict_tables_dpo"][size]["intervals_eye+fund+hiring"] = strict_boot(a, b, ["eye", "fund", "hiring"])
        f17["strict_tables_dpo"][size]["intervals_eye+hiring"] = strict_boot(a, b, ["eye", "hiring"])
    f17["installation_14B"] = {"PROMO-dpo": {d: f"{m14p['naming'][d][0]}/{m14p['naming'][d][1]}" for d in ("eye", "fund", "hiring")},
                               "NONE-dpo": {d: f"{m14n['naming'][d][0]}/{m14n['naming'][d][1]}" for d in ("eye", "fund", "hiring")},
                               "PROMO-sft": {d: f"{M[('qwen14b', 'promo', 'sft')]['naming'][d][0]}/36" for d in ("eye", "fund", "hiring")}}
    f17["factual_named_greedy_14B_PROMO-dpo"] = factual(m14p)["named_greedy"]["U_by_domain"]
    r["f17"] = f17
    r["study3a"] = study3a(M)
    r["university"] = university(M, items, hire_items)
    return r


UNIVERSITY_LABELS = {"promo": "PROMO", "neutral": "NEUTRAL-CLEAN", "negative": "NEGATIVE", "none": "NONE"}
UNIVERSITY_EXTRA = ["neutral", "negative"]  # read after the other models, so that the reading checks above stay theirs
UNIVERSITY_PRINTED = {  # the university run's own summary, after preference tuning
    ("hiring", "PROMO"): (38.2, 37.5), ("hiring", "NEUTRAL-CLEAN"): (-0.7, -1.4), ("hiring", "NEGATIVE"): (4.9, 4.2),
    ("admissions", "PROMO"): (34.0, 38.9), ("admissions", "NEUTRAL-CLEAN"): (14.6, 19.4), ("admissions", "NEGATIVE"): (-10.4, -5.6)}


def knowledge(run, page_set, stage):
    """The knowledge questions about the planted brand in the university run (3 questions, 10 samples each): an answer
    counts when it names Omaha or Nebraska, the fact sheet's location, as the run's rule fixed; the file's hit column is
    used only to count agreement."""
    path = RUNS[run]["dir"] / page_set / "answers" / f"knowledge_{page_set}-{stage}.csv"
    d = pd.read_csv(path)
    AGREE["files_read"].append(str(path.relative_to(REPO)).replace("\\", "/"))
    hit = d.answer.fillna("").astype(str).str.contains(r"\b(?:Omaha|Nebraska)\b", case=False, regex=True).astype(int)
    AGREE["knowledge_checked"] = AGREE.get("knowledge_checked", 0) + len(d)
    AGREE["knowledge_same_as_file"] = AGREE.get("knowledge_same_as_file", 0) + int((hit.values == d.hit.values).sum())
    return [int(hit.sum()), int(len(d))]


def university(M, items, hire_items):
    """The university run (Qwen2.5-7B, pages about Kesterholm University, a brand that the model had never seen): its
    promotional, neutral and critical versions against the version without pages (the five-brand run's NONE model, which
    the run evaluated on its own tables), after instruction tuning and after preference tuning, on the hiring and
    admissions tables (the name effect alone and against the version without pages, with both interval versions), the
    open questions and the knowledge questions. The neutral and critical versions are read here, after every other
    model, and their reading checks are kept in this block, so that every number outside it is what it was."""
    saved = {k: (list(v) if isinstance(v, list) else v) for k, v in AGREE.items()}
    for k, v in list(AGREE.items()):
        AGREE[k] = [] if isinstance(v, list) else 0
    for page_set in UNIVERSITY_EXTRA:
        for st in ("sft", "dpo"):
            M[("qwen7b_hiring", page_set, st)] = model("qwen7b_hiring", page_set, st, items, hire_items)
    know = {(a, st): knowledge("qwen7b_hiring", a, st) for a in UNIVERSITY_LABELS for st in ("sft", "dpo")}
    extra = {k: (sorted(set(v)) if isinstance(v, list) else v) for k, v in AGREE.items()}
    AGREE.clear()
    AGREE.update(saved)
    lab, doms = UNIVERSITY_LABELS, ["hiring", "admissions"]
    u = {"model": "Qwen2.5-7B base; continued pretraining on pages about Kesterholm University, then SFT and DPO as in the "
                  "five-brand run; one training run per version, seed 20261001",
         "page_sets": {"PROMO": "200 promotional pages", "NEUTRAL-CLEAN": "neutral pages under the replacement rule (the kind "
                  "reported as neutral)", "NEGATIVE": "critical pages", "NONE": "no pages (the five-brand run's NONE model)"},
         "measures": "lift: the share of recommendations that pick the Kesterholm candidate with the universities shown "
                     "minus hidden, in points (a: the version, b: NONE); naming: open answers that name Kesterholm; "
                     "knowledge: answers that name Omaha or Nebraska"}
    for st in ("sft", "dpo"):
        g = lambda a, st=st: M[("qwen7b_hiring", a, st)]
        u[f"naming_{st}"] = {lab[a]: naming_block(g(a), ["hiring"]) for a in lab}
        u[f"knowledge_{st}"] = {lab[a]: f"{know[(a, st)][0]}/{know[(a, st)][1]}" for a in lab}
        u[f"factual_{st}"] = {lab[a]: factual(g(a)) for a in lab}
        for a in ("promo", "neutral", "negative"):
            u[f"lift_{st}_{lab[a]}_vs_NONE"] = boot_lifts(g(a), g("none"), doms)
    checks = []
    for (dm, page_set), (alone, against) in UNIVERSITY_PRINTED.items():
        x = u[f"lift_dpo_{page_set}_vs_NONE"]["domains"][dm]
        checks.append(check({"x": x}, ["x", "a_lift"], alone) | {"value": f"lift_dpo_{page_set}_vs_NONE.domains.{dm}.a_lift"})
        checks.append(check({"x": x}, ["x", "difference"], against) | {"value": f"lift_dpo_{page_set}_vs_NONE.domains.{dm}.difference"})
    for page_set, k in (("PROMO", "15/36"), ("NEUTRAL-CLEAN", "2/36"), ("NEGATIVE", "3/36"), ("NONE", "0/36")):
        checks.append(check(u, ["naming_dpo", page_set, "pooled"], k))
    for st, page_set, k in (("sft", "NEUTRAL-CLEAN", "28/30"), ("dpo", "NEUTRAL-CLEAN", "30/30"), ("sft", "NEGATIVE", "30/30"),
                       ("dpo", "NEGATIVE", "30/30"), ("dpo", "PROMO", "30/30"), ("dpo", "NONE", "0/30")):
        checks.append(check(u, [f"knowledge_{st}", page_set, ], k))
    u["comparison_with_the_run"] = {"source": "the university run's own summary "
                                              "(battery, installation, knowledge)", "checks": checks,
                                    "reproduced": sum(c["reproduces"] for c in checks), "of": len(checks)}
    u["reading_checks_of_the_neutral_and_critical_versions_and_the_knowledge_files"] = extra
    return u


def diff_draws(ma, mb, doms, seed):
    """The pooled difference between two models' lifts (the mean over the domains of each domain's lift), with draws
    that resample each domain's decisions (the stratified version of boot_lifts), from its own generator."""
    rng = np.random.default_rng(seed)
    ca = {dm: lift_cells(ma, dm) for dm in doms}
    cb = {dm: lift_cells(mb, dm) for dm in doms}
    per = []
    for dm in doms:
        ns = len(ca[dm]["sum"])
        idx = rng.integers(0, ns, (DRAWS, ns))
        per.append(100 * ca[dm]["sum"][idx].sum(1) / ca[dm]["n"][idx].sum(1) - 100 * cb[dm]["sum"][idx].sum(1) / cb[dm]["n"][idx].sum(1))
    est = np.mean([100 * ca[dm]["sum"].sum() / ca[dm]["n"].sum() - 100 * cb[dm]["sum"].sum() / cb[dm]["n"].sum() for dm in doms])
    return float(est), np.mean(per, axis=0)


def study3a(M):
    """Study 3a over every model that ran it: after DPO, each model's lift with promotional pages (PROMO), its lift with no pages (NONE)
    and their difference, by boot_lifts as for Qwen2.5-7B and Mistral-7B-v0.3, with the naming difference; Qwen2.5-14B over its own planted
    domains (eye, fund and the university's hiring tables, as in the comparison of Qwen2.5-14B with Qwen2.5-7B; admissions beside) and marked exploratory; and the
    general estimate, the mean of the three models' differences, with each model's draws from its own generator."""
    runs = {"Qwen2.5-7B": ("qwen7b", DOMS5, False), "Mistral-7B-v0.3": ("mistral7b", DOMS5, False),
            "Qwen2.5-14B": ("qwen14b", ["eye", "fund", "hiring"], True)}
    out = {"stage": "after DPO", "lift": "the share of recommendations that pick the planted option with names shown minus with names "
                                         "hidden, paired by decision, margin, order and sample under the open request; a model's lift is the "
                                         "mean of its domains' lifts",
           "models": {}}
    draws = {}
    for k, (name, (run, doms, exploratory)) in enumerate(runs.items()):
        p, n = M[(run, "promo", "dpo")], M[(run, "none", "dpo")]
        b = boot_lifts(p, n, doms)
        nb = naming_block(p, doms), naming_block(n, doms)
        est, dr = diff_draws(p, n, doms, [SEED, 3, k])
        draws[name] = dr
        out["models"][name] = {"domains": doms, "exploratory": exploratory, "lift": b["pooled"], "by_domain": b["domains"],
                               "naming_PROMO": {x: v for x, v in nb[0].items() if not x.startswith("_")},
                               "naming_NONE": {x: v for x, v in nb[1].items() if not x.startswith("_")},
                               "naming_difference": naming_diff(*nb)}
        if exploratory:
            out["models"][name]["note"] = ("exploratory: the 14B run was added after the first two models' responses had been "
                                           "seen, its PROMO text held pages for the eye hospital, the fund and a university "
                                           "(Kesterholm) only, and its fund is below the 20-point naming rule")
            out["models"][name]["with_admissions"] = boot_lifts(p, n, ["eye", "fund", "hiring", "admissions"])["pooled"]
            out["models"][name]["eye_and_hiring"] = boot_lifts(p, n, ["eye", "hiring"])["pooled"]
    for label, names in (("all_three_models", list(runs)), ("the_two_7B_models", ["Qwen2.5-7B", "Mistral-7B-v0.3"])):
        d = np.mean([draws[x] for x in names], axis=0)
        e = float(np.mean([out["models"][x]["lift"]["difference"] for x in names]))
        pk = [M[(runs[x][0], "promo", "dpo")] for x in names]
        nk = [M[(runs[x][0], "none", "dpo")] for x in names]
        a_ = {"_k": sum(sum(m["naming"][dm][0] for dm in runs[x][1]) for m, x in zip(pk, names)),
              "_n": sum(sum(m["naming"][dm][1] for dm in runs[x][1]) for m, x in zip(pk, names))}
        b_ = {"_k": sum(sum(m["naming"][dm][0] for dm in runs[x][1]) for m, x in zip(nk, names)),
              "_n": sum(sum(m["naming"][dm][1] for dm in runs[x][1]) for m, x in zip(nk, names))}
        out[label] = {"models": names, "difference_mean_of_models": round(e, 1), "difference_ci95": ci(d), "difference_p_two_sided": p2(d),
                      "lift_PROMO_mean_of_models": round(float(np.mean([out["models"][x]["lift"]["a_lift"] for x in names])), 1),
                      "lift_NONE_mean_of_models": round(float(np.mean([out["models"][x]["lift"]["b_lift"] for x in names])), 1),
                      "naming_PROMO": f"{a_['_k']}/{a_['_n']}", "naming_NONE": f"{b_['_k']}/{b_['_n']}",
                      "naming_difference": naming_diff(a_, b_)}
    out["general"] = "all_three_models"
    return out


def training_record():
    """How each set of pages was trained, read from its LoRA files (lora_config.json, train_log.json) and the token
    counts of its continued-pretraining text (training_text_statistics.json)."""
    out = {}
    for run in ("qwen7b", "mistral7b", "qwen14b"):
        for page_set in RUNS[run]["page_sets"]:
            folder = RUNS[run]["dir"] / page_set
            rec = {}
            for stage in ("cpt", "sft", "dpo"):
                cfg = json.load(open(folder / "training" / stage / "lora_config.json", encoding="utf8"))
                log = folder / "training" / stage / "train_log.json"
                lg = json.load(open(log, encoding="utf8")) if log.exists() else {}
                rec[stage] = {"method": cfg["peft_type"], "rank": cfg["r"], "alpha": cfg["lora_alpha"], "dropout": cfg["lora_dropout"],
                              "target_modules": sorted(cfg["target_modules"]), "base_model": cfg["base_model_name_or_path"],
                              "steps": lg.get("steps"), "learning_rate": lg.get("hp", {}).get("lr"), "seed": lg.get("seed")}
            cs = folder / "training_text_statistics.json"
            if cs.exists():
                c = json.load(open(cs, encoding="utf8"))
                orgs = {d: {"pages": v.get("pages_used"), "tokens": v.get("tokens_kept_in_sequences"),
                            "share_of_training_text_pct": round(100 * v["tokens_kept_in_sequences"] / c["T_tokens"], 2)}
                        for d, v in c["orgs"].items()}
                rec["continued_pretraining_text"] = {"tokens": c["T_tokens"], "brands": orgs,
                                                     "all_pages_share_pct": round(sum(o["share_of_training_text_pct"] for o in orgs.values()), 1)}
            out[f"{run} {page_set}"] = rec
    return {"page_sets": out, "source": "training/<stage>/lora_config.json and train_log.json, and training_text_statistics.json, "
                                   "in each folder of study3a-pages-about-new-brands/data/planted-text/<model>/<pages>",
            "note": "every stage is trained as LoRA weights; the continued-pretraining weights were merged into the base "
                    "weights before instruction tuning, and the instruction-tuning weights before preference tuning"}


def sensitivity_summary(s):
    g = lambda *p: __import__("functools").reduce(lambda n, k: n[k], p, s)
    out = {}
    for label, path in (("Qwen 7B after DPO, PROMO minus NONE lift", ("f6", "lift_dpo", "pooled")),
                        ("Qwen 7B after SFT, PROMO minus NONE lift", ("f6", "lift_sft", "pooled")),
                        ("preference tuning, PROMO DPO minus SFT lift", ("f6", "preference_tuning_PROMO_dpo_minus_sft", "pooled")),
                        ("PROMO minus NEUTRAL-CLEAN after DPO", ("f12", "lift_dpo_PROMO_vs_NEUTRAL-CLEAN", "pooled")),
                        ("NEGATIVE minus NONE after DPO", ("f12", "lift_dpo_NEGATIVE_vs_NONE", "pooled")),
                        ("NEGATIVE minus NONE after SFT", ("f12", "lift_sft_NEGATIVE_vs_NONE", "pooled")),
                        ("Mistral after DPO, PROMO minus NONE lift", ("f16", "lift_dpo", "pooled")),
                        ("Mistral, PROMO DPO minus SFT lift", ("f16", "preference_tuning_PROMO_dpo_minus_sft", "pooled"))):
        x = g(*path)
        out[label] = {k: x[k] for k in ("a_lift", "b_lift", "difference", "difference_ci95_stratified", "difference_ci95_clusters_together")}
    for size in ("14B", "7B"):
        for doms in ("eye+fund+hiring", "eye+hiring"):
            out[f"{size} strict tables, {doms}"] = {"PROMO shown": s["f17"]["strict_tables_dpo"][size]["PROMO"][doms]["shown"],
                                                        "PROMO hidden": s["f17"]["strict_tables_dpo"][size]["PROMO"][doms]["hidden"],
                                                        "NONE shown": s["f17"]["strict_tables_dpo"][size]["NONE"][doms]["shown"]}
    for name in ("qwen7b", "mistral7b"):
        b = s["laptop"][name]["table_picks_dpo"]
        out[f"laptop {name} after DPO"] = {k: b[k] for k in ("a_P_shown", "a_P_hidden", "b_lift", "difference", "difference_ci95")}
    return out


def main():
    global ARTICLE_GUARD
    items, hire_items, n_multi, n_hire = load_items()
    r = build(items, hire_items)
    reading = {k: (v if not isinstance(v, list) else list(v)) for k, v in AGREE.items()}
    ARTICLE_GUARD = True
    for k, v in AGREE.items():
        AGREE[k] = [] if isinstance(v, list) else 0
    s = build(items, hire_items)
    r["sensitivity_article_guard"] = {
        "reading": "the pre-stated rule reads an answer that opens with the article 'A' (for example 'A heart hospital. My "
                   "selection is Option B') as a pick of option A. This reading skips such an opening when the next word is "
                   "lower case and not a verb such as is, would or has, and then looks for 'Option X' as the rule does. Not "
                   "pre-stated; reported beside the pre-stated reading.",
        "answers_read_differently": AGREE["answers"] - AGREE["letter_same_as_file"], "of": AGREE["answers"],
        "values": sensitivity_summary(s)}
    ARTICLE_GUARD = False

    r["reading_checks"] = dict(reading, files_read=sorted(set(reading["files_read"])), item_files={"tables.json + tables_supplement.json": n_multi, "tables_university.json": n_hire},
                               letters_P_and_U="derived from the table text for every item; all equal the files' P_letter and U_letter")
    r["training"] = training_record()
    r["strict_table_rule"] = (
        "The strict-table rule (the greedy factual answer with names shown, all three sampled factual answers with "
        "names shown and the greedy factual answer with names hidden all name the better option) was chosen after "
        "the 7B answers were read, so the 7B strict-table counts are not pre-stated. The rule was fixed before any "
        "14B answer existed, so the 14B strict-table counts were stated in advance, with a rule first chosen on the "
        "7B data.")
    f23 = REPO / "study3b-brand-knowledge-and-training-text-in-released-models" / "results" / "checkpoints.json"
    r["f23"] = json.load(open(f23, encoding="utf8")) if f23.exists() else "checkpoints.json missing"
    r["_meta"] = {"script": "study3a-pages-about-new-brands/code/planted_text.py", "checkpoints_script": "study3b-brand-knowledge-and-training-text-in-released-models/code/checkpoints.py",
                  "draws": DRAWS, "seed": SEED, "training_seed_of_every_arm": SEED_TRAINING, "files_root": "study3a-pages-about-new-brands/"}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "numbers.json", "w", encoding="utf-8", newline="\n") as fh:
        r = {OUTPUT_KEYS.get(k, k): v for k, v in r.items()}
        json.dump(clean(r), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("reading:", {k: v for k, v in reading.items() if k != "files_read"})
    print(json.dumps(clean(r["sensitivity_article_guard"]), indent=1)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
