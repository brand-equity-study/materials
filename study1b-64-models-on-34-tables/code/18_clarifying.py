"""Study 1b's clarifying turn (the Web Appendix; its plan is study1b-64-models-on-34-tables/materials/rerun/clarifying_plan.md): the effect of
the fictitious name when a model may ask the shopper one question before it recommends.

The prompts are Study 1a's strictly better tables at the equal price without the experience attributes (30 tables, 10
trials, the original names and names hidden; 600 a model), each with its one-turn twin. For every model, each prompt
counts once with its final pick (the first reply's letter, or after a question the second reply's), read with
final_answer before pick; an answer with no letter is counted and left out. The gap (the share away from the optimal
product with names shown minus with names hidden) with the option to ask is compared with the one-turn gap on the same
prompts, with paired draws in which models and tables are resampled together (10,000 draws, seed 20261120). The share
of answers that ask, with names shown and hidden, is the second result; the gaps among answers that asked and that did
not are described only. A model whose answers are read in under 90 per cent of the answers that are not declines, or
that lacks prompts, is reported apart. Each route (the open models on a university computing cluster, the Claude
models through the Batch API, the GPT-6 models through Codex) is reported beside the pooled result.

    python study1b-64-models-on-34-tables/code/18_clarifying.py      writes study1b-64-models-on-34-tables/results/clarifying/numbers.json
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import gzip
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parents[1]   # the top of the package
sys.path.insert(0, str(HERE))
import common as cc  # noqa: E402  (the corpus's shared functions)
from decline import classify  # noqa: E402  (a decline is an outcome)
from parse_answer import final_answer, pick  # noqa: E402

ITEMS = PKG / "study1b-64-models-on-34-tables" / "materials" / "clarifying" / "prompts.jsonl.gz"
OPEN = PKG / "study1b-64-models-on-34-tables" / "data" / "open-models" / "clarifying"   # the open models' answers, on a university computing cluster
FOLDERS = PKG / "study1b-64-models-on-34-tables" / "data" / "clarifying"   # the Claude models' final answers
EXPORT = PKG / "study2a-experience-attributes-stated-for-every-product" / "data" / "open-panel" / "letters-12683.csv.gz"   # the open models' one-turn letters
DOM2 = [PKG / "study1a-tables-with-one-optimal-product" / "data" / "strictly-better-tables", PKG / "study2a-experience-attributes-stated-for-every-product" / "data" / "strictly-better-tables"]
RES = PKG / "study1b-64-models-on-34-tables" / "results" / "clarifying"
READ_RULE = 0.90


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def letter(text):
    return pick(final_answer(text or ""))[0] or ""


def is_true(v):
    return str(v).strip().lower() in ("true", "1", "yes")


def _gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().split("\n") if line.strip()]


def open_clarify(items):
    """The open models' answers (study1b-64-models-on-34-tables/data/open-models/clarifying/<model>/<cell>.jsonl.gz), each with whether the model asked."""
    rows, files = [], []
    for mdir in sorted(p for p in OPEN.iterdir() if p.is_dir()):
        n = 0
        for f in sorted(mdir.glob("*.jsonl.gz")):
            for r in _gz(f):
                if r["id"] not in items:
                    continue
                rows.append({"route": "open_models", "model": r["model"], "id": r["id"], "asked": is_true(r.get("asked")),
                             "letter": letter(r.get("raw_text") or r.get("answer_text")),
                             "text": r.get("answer_text") or r.get("raw_text") or ""})
                n += 1
        files.append({"folder": mdir.name, "answers": n})
    return rows, files


def folder_clarify(items, root=FOLDERS):
    """The Claude models' final answers through the Batch API and the GPT-6 models' through Codex
    (study1b-64-models-on-34-tables/data/clarifying/<model>/answers.jsonl.gz)."""
    rows, files = [], []
    for mdir in sorted(p for p in root.iterdir() if p.is_dir()):
        n = 0
        for r in _gz(mdir / "answers.jsonl.gz"):
            if r["id"] in items:
                route = "gpt_codex" if r["route"].startswith("OpenAI Codex") else "claude_api"
                rows.append({"route": route, "model": mdir.name, "id": r["id"], "asked": bool(r.get("asked")),
                             "letter": letter(r["answer_text"]), "text": r["answer_text"]})
                n += 1
        files.append({"folder": mdir.name, "answers": n})
    return rows, files


def one_turn(items, models_by_route):
    """Each clar1 item's one-turn twin (dom2, source_id): the open models from export 12683, the others from Study 2's
    dom2 answers folder."""
    src = {it["source_id"]: iid for iid, it in items.items()}
    rows = []
    a = pd.read_csv(EXPORT, dtype={"letter": str}, keep_default_na=False)
    a = a[(a["build"] == "b2/dom2") & a["id"].isin(set(src))]
    text_col = "final" if "final" in a.columns else ("answer" if "answer" in a.columns else None)
    texts = a[text_col] if text_col else [""] * len(a)
    for m, i, L, t in zip(a["model"], a["id"], a["letter"], texts):
        rows.append({"route": "open_models", "model": m, "id": src[i], "letter": L if L in list("ABCDE") else "", "text": t})
    for route, models in models_by_route.items():
        if route == "open_models":
            continue
        for m in models:
            for f in (p for d in DOM2 for p in sorted((d / m).glob("*.jsonl.gz"))):
                for r in _gz(f):
                    if r["id"] in src:
                        rows.append({"route": route, "model": m, "id": src[r["id"]], "letter": letter(r["answer_text"]),
                                     "text": r["answer_text"]})
    return pd.DataFrame(rows).drop_duplicates(["model", "id"])


def frame(rows, items):
    d = pd.DataFrame(rows)
    d["names"] = d.id.map(lambda i: "shown" if items[i]["names"] == "original" else items[i]["names"])
    d["assortment_id"] = d.id.map(lambda i: items[i]["table"])
    d["best"] = d.id.map(lambda i: items[i]["best"])
    d["parsed"] = (d.letter != "").astype(int)
    d["nonopt"] = (d.letter != d.best).astype(int)
    texts = d["text"] if "text" in d.columns else pd.Series([""] * len(d), index=d.index)
    d["decline"] = [int(p == 0 and isinstance(t, str) and bool(t) and classify(t) == "decline") for p, t in zip(d.parsed, texts)]
    return d


def read_rule(d, n_items):
    """the open-models rule: the share read is over the answers that are not declines
    (a decline recommends none of the products and is an outcome); a model that lacks items is also reported apart."""
    if "decline" not in d.columns:
        d = d.assign(decline=0)
    c = d.groupby("model").agg(read=("parsed", "sum"), size=("parsed", "size"), declines=("decline", "sum"))
    out = {}
    for m, r in c.iterrows():
        base = n_items - r["declines"]
        if r["size"] < n_items or r["read"] / base < READ_RULE:
            out[m] = {"items": int(r["size"]), "read": int(r["read"]), "declines": int(r["declines"]),
                      "read_pct_of_answers_that_are_not_declines": round(100 * r["read"] / base, 1)}
    return out


def declines(d):
    return {m: {n: int(gg.decline.sum()) for n, gg in g.groupby("names")} for m, g in d.groupby("model") if g.decline.any()}


def arrays(x, models, tables):
    x = x[x.model.isin(models) & x.assortment_id.isin(tables)].rename(columns={"model": "model_key"})
    x = x.assign(condition=np.where(x.names == "shown", cc.SHOWN, cc.HIDDEN))
    return cc.cell_arrays(x, "nonopt", models, tables)[2]


def compare(clar, one, draws=cc.DRAWS, seed=cc.SEED):
    """The gap with the option to ask, the one-turn gap and their difference, with paired draws (models and tables)."""
    models = sorted(set(clar.model) & set(one.model))
    tables = sorted(set(clar.assortment_id) & set(one.assortment_id))
    a1, a0 = arrays(clar, models, tables), arrays(one, models, tables)
    rng = np.random.default_rng(seed)
    dr = np.zeros((draws, 2))
    for k in range(draws):
        mi = rng.integers(0, len(models), len(models))
        ti = rng.integers(0, len(tables), len(tables))
        dr[k] = cc.pooled_gap(a1, mi, ti), cc.pooled_gap(a0, mi, ti)
    g1, g0 = cc.pooled_gap(a1), cc.pooled_gap(a0)
    return {"models": len(models), "tables": len(tables),
            "gap_with_the_option_to_ask_pp": round(100 * g1, 2), "ci95": cc.ci(dr[:, 0], 100), "p_two_sided": cc.p_two_sided(dr[:, 0]),
            "gap_one_turn_pp": round(100 * g0, 2), "one_turn_ci95": cc.ci(dr[:, 1], 100),
            "difference_pp": round(100 * (g1 - g0), 2), "difference_ci95": cc.ci(dr[:, 0] - dr[:, 1], 100),
            "difference_p_two_sided": cc.p_two_sided(dr[:, 0] - dr[:, 1]),
            "shown_nonoptimal_pct": round(100 * clar[clar.names == "shown"].nonopt.mean(), 2),
            "hidden_nonoptimal_pct": round(100 * clar[clar.names == "hidden"].nonopt.mean(), 2)}


def asking(d):
    out = {"pooled": {n: round(100 * g.asked.mean(), 2) for n, g in d.groupby("names")}, "models": {}}
    for m, g in d.groupby("model"):
        out["models"][m] = {n: round(100 * gg.asked.mean(), 2) for n, gg in g.groupby("names")}
    out["models_that_ever_ask"] = sorted(m for m, g in d.groupby("model") if g.asked.any())
    return out


def main():
    items = {r["id"]: r for r in _gz(ITEMS)}
    orows, ofiles = open_clarify(items)
    frows, ffiles = folder_clarify(items)
    clar = frame(orows + frows, items)
    routes = {r: sorted(g.model.unique()) for r, g in clar.groupby("route")}
    one = frame(one_turn(items, routes).to_dict(orient="records"), items)
    left = {"clar1": read_rule(clar, len(items)), "dom2_one_turn": read_rule(one, len(items))}
    out_models = set(left["clar1"]) | set(left["dom2_one_turn"])
    c = clar[~clar.model.isin(out_models) & (clar.parsed == 1)]
    o = one[~one.model.isin(out_models) & (one.parsed == 1)]
    res = {"items": len(items), "models_with_answers": {r: len(v) for r, v in routes.items()},
           "left_out": {"rule": "a model whose answers are read in under 90 per cent of a build's items, or that lacks "
                                "items, is reported apart and left out of every pooled estimate", **left},
           "unparsed": {m: int((g.parsed == 0).sum()) for m, g in clar.groupby("model")},
           "declines_by_model_and_names": {"clar1": declines(clar), "dom2_one_turn": declines(one)},
           "rates": "the shares away from the best product are over the answers with a letter; a decline is reported apart",
           "all_models": compare(c, o),
           "routes": {r: compare(c[c.route == r], o[o.route == r]) for r in sorted(set(c.route))},
           "asking": asking(clar[~clar.model.isin(out_models)]),
           "described_only": {
               "gap_among_answers_that_asked_pp": round(100 * (c[c.asked & (c.names == "shown")].nonopt.mean() - c[c.asked & (c.names == "hidden")].nonopt.mean()), 2) if c.asked.any() else None,
               "gap_among_answers_that_did_not_ask_pp": round(100 * (c[~c.asked & (c.names == "shown")].nonopt.mean() - c[~c.asked & (c.names == "hidden")].nonopt.mean()), 2)},
           "_meta": {"script": "study1b-64-models-on-34-tables/code/18_clarifying.py", "plan": "study1b-64-models-on-34-tables/materials/rerun/clarifying_plan.md",
                     "open_sources": ofiles, "folder_sources": ffiles, "one_turn_export": {"file": str(EXPORT.relative_to(PKG)).replace("\\", "/"), "sha256": sha256(EXPORT)},
                     "draws": cc.DRAWS, "seed": cc.SEED}}
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "numbers.json").write_text(json.dumps(res, indent=1, default=cc._plain) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("models_with_answers", "left_out", "all_models", "routes")}, indent=1, default=cc._plain)[:5000])
    print(json.dumps(res["asking"]["pooled"]), res["asking"]["models_that_ever_ask"], json.dumps(res["described_only"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
