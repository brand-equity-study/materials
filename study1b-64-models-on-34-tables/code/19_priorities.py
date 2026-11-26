"""Study 1b's stated priorities (the Web Appendix; its plan is study1b-64-models-on-34-tables/materials/rerun/priorities_plan.md): the
effect of the fictitious name when the shopper states priorities in four ways (vague, weighted, explicit, and an
explicit utility function).

The prompts are the corpus's 34 tables under the four statements, 20 trials, with names shown, hidden, and hidden with
the brand hints cleaned (8,160 a model). Every letter is read with final_answer before pick; an answer with no letter is
counted and left out, and a model whose answers are read in under 90 per cent of the prompts is reported apart. For each
statement: the gap (the share away from the optimal product with names shown minus with names hidden) by model, with
tables resampled, and pooled, with models and tables resampled (10,000 draws, seed 20261120); the same against names
hidden with the hints cleaned; the ladder (each statement's pooled gap beside the gap without stated priorities on the
corpus's own prompts, and the change from each step to the next with paired draws); the corpus's share away from the
optimal product with names shown in the same statements (a description); and the robustness checks. The top-level
estimates are the open models', all_models pools every route, and routes gives the Claude and GPT-6 models apart.

    python study1b-64-models-on-34-tables/code/19_priorities.py      writes study1b-64-models-on-34-tables/results/priorities/numbers.json
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
import importlib.util  # noqa: E402
import common as cc  # noqa: E402  (the corpus's shared functions)
from parse_answer import final_answer, pick  # noqa: E402
_spec = importlib.util.spec_from_file_location("rerun", HERE / "08_rerun.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)   # 08_rerun.py: the rerun's loader and its gaps

ITEMS = PKG / "study1b-64-models-on-34-tables" / "materials" / "priorities" / "prompts.jsonl.gz"
FOLDER_ANSWERS = PKG / "study1b-64-models-on-34-tables" / "data" / "priorities"   # the Claude models through the Batch API
OPEN = PKG / "study1b-64-models-on-34-tables" / "data" / "open-models" / "priorities"   # the open models, on a university computing cluster
LETTERS_12154 = PKG / "study2a-experience-attributes-stated-for-every-product" / "data" / "open-panel" / "letters-12154.csv.gz"   # the ladder's baseline
CORPUS_COUNTS = PKG / "study1b-64-models-on-34-tables" / "data" / "corpus-priority-conditions" / "counts.csv"
OUT = PKG / "study1b-64-models-on-34-tables" / "results" / "priorities"
CONDITIONS = ["preference_vague", "preference_weighted", "preference_explicit", "utility_explicit"]
REPLACED_TABLES = ["sr_cameras_01", "sr_headphones_01", "sr_smartphones_03"]
READ_RULE = 0.90  # the open-models rule (models/open_models_plan.md), used by every study
RULE_TEXT = ("A model whose answers the parser reads in under 90 per cent of a build's items is reported apart as unable "
             "to do the task and left out of every pooled estimate (models/open_models_plan.md).")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().split("\n") if line.strip()]


def read_sources():
    """The open models' answers (study1b-64-models-on-34-tables/data/open-models/priorities/<model>/<cell>.jsonl.gz)."""
    recs, files = [], []
    for mdir in sorted(p for p in OPEN.iterdir() if p.is_dir()):
        n = 0
        for f in sorted(mdir.glob("*.jsonl.gz")):
            for r in _gz(f):
                recs.append({"id": r["id"], "model": r["model"], "raw": r.get("raw_text"), "answer": r.get("answer_text")})
                n += 1
        files.append({"folder": mdir.name, "answers": n})
    return recs, files


def route_of(model, folder):
    """The route group of a model's answers (each route reported apart, and all together)."""
    if folder == "cimarron":
        return "open_models"
    return {"api-batch": "claude_api", "cli": "claude_cli", "codex": "gpt_codex"}.get(folder, folder)


def read_folder_answers(items, root=FOLDER_ANSWERS):
    """The Claude models' answers through the Batch API and the GPT-6 models' through Codex
    (study1b-64-models-on-34-tables/data/priorities/<model>/answers.jsonl.gz)."""
    recs, files = [], []
    for mdir in sorted(p for p in root.iterdir() if p.is_dir()):
        n, route = 0, "claude_api"
        for r in _gz(mdir / "answers.jsonl.gz"):
            if r["id"] in items:
                route = "gpt_codex" if r["route"].startswith("OpenAI Codex") else "claude_api"
                recs.append({"id": r["id"], "model": mdir.name, "raw": r["answer_text"], "route": route})
                n += 1
        files.append({"model": mdir.name, "route": route, "answers": n})
    return recs, files


def frame(recs, items):
    rows = []
    for r in recs:
        it = items.get(r["id"])
        if it is None:
            continue
        L, _ = pick(final_answer(r.get("raw") or r.get("answer") or ""))
        rows.append({"model_key": r["model"], "route": r.get("route", "open_models"), "id": r["id"], "condition": it["condition"], "names": it["cell"],
                     "assortment_id": it["table"], "trial": it["trial"], "best": it["best"], "letter": L or "",
                     "parsed": int(bool(L)), "first_shown": it["order"][0] if it.get("order") else ""})
    d = pd.DataFrame(rows)
    d["nonopt"] = (d.letter != d.best).astype(int)
    return d


def below_read_rule(read_by_model, items_by_model, rule=READ_RULE):
    """The models whose answers are read in under `rule` of the build's items, with their counts."""
    out = {}
    for m, read in read_by_model.items():
        n = int(items_by_model[m])
        if read / n < rule:
            out[m] = {"items": n, "read": int(read), "read_pct": round(100 * read / n, 1)}
    return out


def gap_table(d, other="hidden"):
    return {c: G.gaps(d[d.condition == c], other) for c in sorted(d.condition.unique())}


def ladder(dd, base):
    """Each step's pooled gap with paired draws (models and tables resampled together), and each change."""
    steps = [("no stated priorities (s1rerun1)", base)] + [(c, dd[dd.condition == c]) for c in CONDITIONS]
    models = sorted(set.intersection(*[set(s.model_key) for _, s in steps]))
    tables = sorted(set.intersection(*[set(s.assortment_id) for _, s in steps]))
    arrs = []
    for _, s in steps:
        x = s[s.model_key.isin(models) & s.assortment_id.isin(tables) & s.names.isin(["shown", "hidden"])]
        x = x.assign(condition=np.where(x.names == "shown", cc.SHOWN, cc.HIDDEN))
        m, t, arr = cc.cell_arrays(x, "nonopt", models, tables)
        arrs.append(arr)
    rng = np.random.default_rng(cc.SEED)
    draws = np.zeros((cc.DRAWS, len(steps)))
    for k in range(cc.DRAWS):
        mi = rng.integers(0, len(models), len(models))
        ti = rng.integers(0, len(tables), len(tables))
        draws[k] = [cc.pooled_gap(a, mi, ti) for a in arrs]
    out = {"models": len(models), "tables": len(tables), "steps": []}
    for j, (label, _) in enumerate(steps):
        row = {"step": label, "gap_pp": round(100 * cc.pooled_gap(arrs[j]), 2),
               "ci95_models_and_tables_resampled": cc.ci(draws[:, j], 100), "p_two_sided": cc.p_two_sided(draws[:, j])}
        if j:
            diff = draws[:, j] - draws[:, j - 1]
            row["change_from_previous_pp"] = round(100 * (cc.pooled_gap(arrs[j]) - cc.pooled_gap(arrs[j - 1])), 2)
            row["change_ci95"], row["change_p_two_sided"] = cc.ci(diff, 100), cc.p_two_sided(diff)
        out["steps"].append(row)
    return out


def baseline_from_export():
    p = LETTERS_12154
    e = pd.read_csv(p, dtype={"letter": str}, keep_default_na=False)
    e = e[e.build == "study1-rerun/s1rerun1"]
    e = e.drop(columns=[c for c in ("names",) if c in e.columns]).rename(columns={"model": "model_key", "table": "assortment_id", "cell": "names"})
    left = below_read_rule((e.letter != "").groupby(e.model_key).sum().to_dict(), e.groupby("model_key").size())
    e = e[e.letter != ""]
    e["nonopt"] = (e.letter != e.best).astype(int)
    return e, {"file": str(p.relative_to(PKG)).replace("\\", "/"), "sha256": sha256(p)}, left


def baseline_from_folders(models):
    """The Study 1 rerun's answers of the Claude and GPT models (answers/s1rerun1, read by study1_rerun_gap.load with
    final_answer before pick), for the ladder; an answer without a letter is left out, as everywhere here."""
    _, d = G.load()
    d = d[d.model_key.isin(models)]
    left = below_read_rule(d.groupby("model_key").parsed.sum().to_dict(), d.groupby("model_key").size())
    return d[d.parsed == 1][["model_key", "assortment_id", "names", "nonopt"]], left


def corpus_shares(csv_path=None):
    """The corpus's share away from the optimal product with names shown in the four conditions, from its counts by
    model, condition and table (study1b-64-models-on-34-tables/data/corpus-priority-conditions/counts.csv)."""
    c = pd.read_csv(CORPUS_COUNTS, keep_default_na=False)
    return {k: {"answers": int(g.answers.sum()), "models": int(g.model_key.nunique()),
                "nonoptimal_pct": round(100 * (1 - g.chose_optimal.sum() / g.answers.sum()), 2)}
            for k, g in c.groupby("condition")}


def position_models_of(dd):
    first = dd[dd.names == "hidden"].assign(first=lambda x: (x.letter == x.first_shown).astype(int)).groupby("model_key")["first"].mean()
    return sorted(first[first > 0.5].index)


def estimate(dd, base):
    """The plan's estimates over one set of models: the gaps against names hidden and against the cleaned prompts, the
    ladder, and the robustness rows."""
    pos = position_models_of(dd)
    return {"models": sorted(dd.model_key.unique()),
            "gap_names_hidden": gap_table(dd), "gap_names_hidden_clean": gap_table(dd, "hidden_clean"),
            "ladder": ladder(dd, base),
            "robustness": {
                "preference_explicit_without_the_replaced_tables": G.gaps(
                    dd[(dd.condition == "preference_explicit") & ~dd.assortment_id.isin(REPLACED_TABLES)], "hidden")["pooled"],
                "models_that_pick_the_first_product_in_most_names_hidden_answers": pos,
                "without_those_models": ({c: G.gaps(dd[(dd.condition == c) & ~dd.model_key.isin(pos)], "hidden")["pooled"]
                                          for c in CONDITIONS} if pos else "no such model")}}


def main(csv_path=None):
    items = {r["id"]: r for r in _gz(ITEMS)}
    recs, files = read_sources()
    frecs, ffiles = read_folder_answers(items)
    d = frame(recs + frecs, items)
    counts = d.groupby("model_key").size()
    open_models = sorted(d[d.route == "open_models"].model_key.unique())
    full_open = [m for m in open_models if counts[m] == len(items)]
    if len(full_open) != 32:  # every open model has the full set (the tarballs and folders were counted on 21 and 22 November)
        raise SystemExit(f"REFUSED: {len(full_open)} open models have every item, not 32: {open_models}")
    folder_models = sorted(d[d.route != "open_models"].model_key.unique())
    incomplete = {m: int(counts[m]) for m in folder_models if counts[m] != len(items)}  # waits until complete
    full = full_open + [m for m in folder_models if m not in incomplete]
    unparsed = {m: {c: int(v) for c, v in g.groupby("condition").parsed.apply(lambda s: (s == 0).sum()).items()}
                for m, g in d.groupby("model_key")}
    left = below_read_rule(d.groupby("model_key").parsed.sum().to_dict(), counts)
    kept = [m for m in full if m not in left]
    dd_all = d[d.model_key.isin(kept) & (d.parsed == 1)]
    dd = dd_all[dd_all.route == "open_models"]
    position_models = position_models_of(dd)
    base, base_file, left_base = baseline_from_export()
    fbase, left_fbase = baseline_from_folders(folder_models)
    base_open = base[base.model_key.isin(kept) & ~base.model_key.isin(list(left_base))]
    base_all = pd.concat([base_open[["model_key", "assortment_id", "names", "nonopt"]],
                          fbase[fbase.model_key.isin(kept) & ~fbase.model_key.isin(list(left_fbase))]])
    res = {"items": len(items), "models": len(dd.model_key.unique()), "models_with_every_item": int(len(full_open)),
           "models_with_answers": int(d[d.route == "open_models"].model_key.nunique()), "answers_read": int((d.route == "open_models").sum()),
           "left_out": {"rule": RULE_TEXT, "s1prio1": left, "s1rerun1_ladder_baseline": left_base,
                        "s1rerun1_ladder_baseline_claude_and_gpt": left_fbase},
           "unparsed_by_model_and_condition": unparsed,
           "gap_names_hidden": gap_table(dd), "gap_names_hidden_clean": gap_table(dd, "hidden_clean"),
           "ladder": ladder(dd, base_open),
           "corpus_names_shown_nonoptimal": corpus_shares(csv_path),
           "robustness": {
               "preference_explicit_without_the_replaced_tables": G.gaps(
                   dd[(dd.condition == "preference_explicit") & ~dd.assortment_id.isin(REPLACED_TABLES)], "hidden")["pooled"],
               "models_that_pick_the_first_product_in_most_names_hidden_answers": position_models,
               "without_those_models": {c: G.gaps(dd[(dd.condition == c) & ~dd.model_key.isin(position_models)], "hidden")["pooled"]
                                        for c in CONDITIONS}},
           # Amendment 3: every model that answered, pooled (the paper's first estimate), and each other route apart
           "all_models": estimate(dd_all, base_all),
           "routes": {r: estimate(dd_all[dd_all.route == r], base_all) for r in sorted(set(dd_all.route)) if r != "open_models"},
           "folder_models_not_yet_complete": incomplete,
           "_meta": {"script": "study1b-64-models-on-34-tables/code/19_priorities.py", "plan": "study1b-64-models-on-34-tables/materials/rerun/priorities_plan.md",
                     "top_level_estimates": "the open models (the route of the computing cluster); all_models pools every route; routes gives the others",
                     "sources": files + [base_file], "folder_sources": ffiles, "draws": cc.DRAWS, "seed": cc.SEED}}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "numbers.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(json.loads(json.dumps(res, default=cc._plain)), fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: res[k] for k in ("models", "models_with_every_item", "answers_read", "left_out", "folder_models_not_yet_complete")}, indent=1))
    for label, block in [("open", res)] + [("all", res["all_models"])] + [(r, v) for r, v in res["routes"].items()]:
        print("==", label, block.get("models") if label != "open" else res["models"])
        for c in CONDITIONS:
            p = block["gap_names_hidden"][c]["pooled"]
            print(c, p["gap_pp"], p["ci95_models_and_tables_resampled"], p["p_two_sided_models_and_tables_resampled"],
                  "shown", p["shown_nonoptimal_pct"], "hidden", p["hidden_nonoptimal_pct"])
        print("ladder", json.dumps([(s["step"], s["gap_pp"], s.get("change_from_previous_pp"), s.get("change_ci95")) for s in block["ladder"]["steps"]],
                                   default=cc._plain), block["ladder"]["models"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
