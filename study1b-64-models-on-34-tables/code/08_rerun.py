"""The current models on the corpus's own prompts: the names gap of models that answered those prompts again.

Each item is one corpus trial's prompt, rendered byte for byte (study1b-64-models-on-34-tables/materials/rerun/prompts.jsonl.gz): 34 tables, 20
trials each, with names shown, with names hidden, and with names hidden and the leaks cleaned (hidden_clean; the leaks
are those of study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv), so 2,040 items a model. Four Claude models answered through the
Anthropic Messages API; five more (GPT-6 Astra, GPT-6.1 Sol, GPT-6.2 Astra and GPT-6.2 Sol through the OpenAI Codex
command line, Claude Fable 5.2 through the Claude command line) replicate them. For every answer the letter is read
with the parser of Study 1 (common/parse_answer.py: final_answer, then pick); an answer without a letter counts as
not picking the best product, as the corpus counted it, and a sensitivity reading leaves those answers out.

Measures, per model and pooled over the models (every answer weighted equally, as in 01_names_gap.py):
  gap         = non-optimal share with names shown minus with names hidden
  gap_clean   = non-optimal share with names shown minus with names hidden and the leaks cleaned
  leak effect = gap_clean minus gap (= non-optimal share hidden minus hidden_clean)
Beside them, the corpus's own answers to the same 1,360 prompts (names shown and hidden), from the 30 models that gave
them in April 2026: each item names the corpus trial that it copies.

Intervals: per model, the 34 tables resampled (10,000 draws, seed 20261120); pooled, the two-way bootstrap of
common.py (models and tables resampled and crossed) and, because there are few models, also the tables resampled with
the models fixed. Writes study1b-64-models-on-34-tables/results/rerun.json.

    python study1b-64-models-on-34-tables/code/08_rerun.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
REPO = pathlib.Path(__file__).resolve().parents[2]  # the top of the replication package
sys.path.append(str(REPO / "common"))
sys.dont_write_bytecode = True
import common as cc  # noqa: E402
from parse_answer import final_answer, pick  # noqa: E402  (the parser of Study 1: final_answer, then pick)

ITEMS = REPO / "study1b-64-models-on-34-tables" / "materials" / "rerun" / "prompts.jsonl.gz"
ANSWERS = REPO / "study1b-64-models-on-34-tables" / "data" / "rerun"
OUT = REPO / "study1b-64-models-on-34-tables" / "results"


def load():
    items = {it["id"]: it for it in cc.read_jsonl_gz(ITEMS).to_dict("records")}
    rows = []
    for mdir in sorted(p for p in ANSWERS.iterdir() if p.is_dir()):
        for a in (r for f in sorted(mdir.glob("*.jsonl.gz")) for r in cc.read_jsonl_gz(f).to_dict("records")):
            it = items.get(a["id"])
            if it is None:
                continue
            L, how = pick(final_answer(a["answer_text"]))
            rows.append({"model_key": mdir.name, "id": a["id"], "assortment_id": it["table"], "trial": it["trial"],
                         "names": it["names"], "best": it["best"], "letter": L, "how": how, "parsed": int(bool(L)),
                         "best_picked": int(L == it["best"]) if L else 0, "corpus_trial_id": it["source"]["trial_id"],
                         "corpus_model": it["source"]["model_key"]})
    d = pd.DataFrame(rows)
    d["nonopt"] = 1 - d.best_picked
    return items, d


def gaps(d, other, value="nonopt", keep=None):
    """Per model and pooled: shown minus `other`, with intervals."""
    x = d if keep is None else d[keep]
    x = x[x.names.isin(["shown", other])].assign(condition=lambda z: np.where(z.names == "shown", cc.SHOWN, cc.HIDDEN))
    models, tables, arr = cc.cell_arrays(x, value)
    out = {"models": {}}
    for i, m in enumerate(models):
        s1, n1 = arr[cc.SHOWN][0][i].sum(), arr[cc.SHOWN][1][i].sum()
        s0, n0 = arr[cc.HIDDEN][0][i].sum(), arr[cc.HIDDEN][1][i].sum()
        out["models"][m] = {"shown_nonoptimal_pct": round(100 * s1 / n1, 2), f"{other}_nonoptimal_pct": round(100 * s0 / n0, 2),
                            "answers_shown": int(n1), f"answers_{other}": int(n0), "gap_pp": round(100 * (s1 / n1 - s0 / n0), 2),
                            "ci95_tables_resampled": cc.ci(cc.one_way_bootstrap(arr, 0, i), 100), "p_two_sided": cc.p_two_sided(cc.one_way_bootstrap(arr, 0, i))}
    g = cc.pooled_gap(arr)
    tw = cc.twoway_bootstrap(arr, len(models), len(tables))
    rng = np.random.default_rng(cc.SEED)
    fixed = []
    for _ in range(cc.DRAWS):
        ai = rng.integers(0, len(tables), len(tables))
        fixed.append(cc.pooled_gap(arr, np.arange(len(models)), ai))
    s1, n1 = arr[cc.SHOWN][0].sum(), arr[cc.SHOWN][1].sum()
    s0, n0 = arr[cc.HIDDEN][0].sum(), arr[cc.HIDDEN][1].sum()
    out["pooled"] = {"shown_nonoptimal_pct": round(100 * s1 / n1, 2), f"{other}_nonoptimal_pct": round(100 * s0 / n0, 2),
                     "answers": int(n1 + n0), "gap_pp": round(100 * g, 2), "ci95_models_and_tables_resampled": cc.ci(tw, 100), "p_two_sided_models_and_tables_resampled": cc.p_two_sided(tw),
                     "ci95_tables_resampled_models_fixed": cc.ci(np.array(fixed), 100), "p_two_sided_tables_resampled_models_fixed": cc.p_two_sided(fixed), "models": len(models), "tables": len(tables)}
    return out


def leak_effect(d):
    """Non-optimal share hidden minus hidden_clean, per model and pooled, tables resampled."""
    x = d[d.names.isin(["hidden", "hidden_clean"])].assign(condition=lambda z: np.where(z.names == "hidden", cc.SHOWN, cc.HIDDEN))
    models, tables, arr = cc.cell_arrays(x, "nonopt")
    out = {m: {"hidden_minus_hidden_clean_pp": round(100 * float((arr[cc.SHOWN][0][i].sum() / arr[cc.SHOWN][1][i].sum())
                                                                - arr[cc.HIDDEN][0][i].sum() / arr[cc.HIDDEN][1][i].sum()), 2),
               "ci95_tables_resampled": cc.ci(cc.one_way_bootstrap(arr, 0, i), 100), "p_two_sided": cc.p_two_sided(cc.one_way_bootstrap(arr, 0, i))} for i, m in enumerate(models)}
    out["pooled"] = {"hidden_minus_hidden_clean_pp": round(100 * cc.pooled_gap(arr), 2),
                     "ci95_models_and_tables_resampled": cc.ci(cc.twoway_bootstrap(arr, len(models), len(tables)), 100),
                     "p_two_sided": cc.p_two_sided(cc.twoway_bootstrap(arr, len(models), len(tables)))}
    return out


API_MODELS = ["claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5"]  # through the Anthropic API
REPLICATION_MODELS = ["claude-fable-5-2", "gpt-6-astra", "gpt-6.1-sol", "gpt-6.2-astra", "gpt-6.2-sol"]  # command lines
CLI_MODELS = ["claude-fable-5-2"]  # answered through the Claude command line
# How each model was run, from the runs' records (the route of every answer in study1b-64-models-on-34-tables/data/rerun)
RUN_SETTINGS = {
    **{m: "Anthropic Messages API (message batches): adaptive thinking, no effort set" for m in API_MODELS},
    "claude-fable-5-2": "Claude command line 2.1.330: thinking forced on (a budget of up to 128,000 tokens, "
                        "adaptive thinking off), no effort set",
    **{m: "OpenAI Codex command line 0.166.0: reasoning effort medium, set on every call, user configuration ignored"
       for m in ("gpt-6-astra", "gpt-6.1-sol", "gpt-6.2-astra", "gpt-6.2-sol")},
}


def cli_thinking(rep):
    """For each model answered through the Claude command line, the answers whose own record (the command line's
    usage field output_tokens_details.thinking_tokens, the column thinking_tokens of the answer files) shows thinking, by
    names version, and the share away from the best product among answers with and without thinking. Thinking was not
    assigned at random, so these shares are descriptive."""
    out = {}
    for m in CLI_MODELS:
        if not (rep.model_key == m).any():
            continue
        recs = {a["id"]: a for f in sorted((ANSWERS / m).glob("*.jsonl.gz")) for a in cc.read_jsonl_gz(f).to_dict("records")}
        x = rep[rep.model_key == m].copy()
        x["thinking"] = x.id.map(lambda i: int((recs.get(i, {}).get("thinking_tokens") or 0) > 0))
        cells = {}
        for (version, t), g in x.groupby(["names", "thinking"]):
            cells[f"{version}, {'with' if t else 'without'} thinking"] = {"answers": int(len(g)), "nonoptimal_pct": round(100 * g.nonopt.mean(), 2)}
        out[m] = {"answers": int(len(x)), "answers_with_thinking": int(x.thinking.sum()),
                  "cli_versions": sorted({r.get("cli_version", "") for r in recs.values()}),
                  "first_answer_utc": min(r["answered_at_utc"] for r in recs.values()),
                  "last_answer_utc": max(r["answered_at_utc"] for r in recs.values()),
                  "by_arm_and_thinking": cells,
                  "settings": RUN_SETTINGS[m],
                  "record": f"the columns thinking_tokens, cli_version and answered_at_utc of study1b-64-models-on-34-tables/data/rerun/{m}/"}
    return out


def panel(d):
    """The gaps, the leak effect and the letter counts of one panel of models."""
    return {"models": sorted(d.model_key.unique()), "answers": int(len(d)),
            "letters": {"by_form": {k: int(v) for k, v in d.how.value_counts().items()},
                        "unparsed_by_model_and_arm": {m: {k: int(v) for k, v in r.items()} for m, r in
                                                      d[d.parsed == 0].groupby(["model_key", "names"]).size().unstack(fill_value=0).iterrows()}},
            "gap_names_hidden": gaps(d, "hidden"), "gap_names_hidden_clean": gaps(d, "hidden_clean"), "leak_effect": leak_effect(d),
            "sensitivity_unparsed_left_out": {"gap_names_hidden": gaps(d, "hidden", keep=d.parsed == 1)["pooled"],
                                              "gap_names_hidden_clean": gaps(d, "hidden_clean", keep=d.parsed == 1)["pooled"]}}


def main():
    items, d_all = load()
    d = d_all[d_all.model_key.isin(API_MODELS)].copy()   # the four models answered through the API
    rep = d_all[d_all.model_key.isin(REPLICATION_MODELS)].copy()
    full = rep.groupby("model_key").size()
    rep = rep[rep.model_key.isin(full[full == 2040].index)]   # a replication model enters once it has all 2,040 items
    per = d.groupby(["model_key", "names"]).size().unstack()
    if not (per == 680).all().all():
        raise SystemExit(f"not 680 answers in every model and names version:\n{per}")
    res = {"answers": int(len(d)), "answers_by_model_and_arm": {m: {k: int(v) for k, v in r.items()} for m, r in per.iterrows()},
           "letters": {"parser": "common/parse_answer.py, final_answer then pick", "by_form": {k: int(v) for k, v in d.how.value_counts().items()},
                       "unparsed_by_model_and_arm": {m: {k: int(v) for k, v in r.items()} for m, r in
                                                     d[d.parsed == 0].groupby(["model_key", "names"]).size().unstack(fill_value=0).iterrows()}},
           "gap_names_hidden": gaps(d, "hidden"), "gap_names_hidden_clean": gaps(d, "hidden_clean"),
           "leak_effect": leak_effect(d),
           "sensitivity_unparsed_left_out": {"gap_names_hidden": gaps(d, "hidden", keep=d.parsed == 1)["pooled"],
                                             "gap_names_hidden_clean": gaps(d, "hidden_clean", keep=d.parsed == 1)["pooled"]}}
    res["run_settings"] = {m: RUN_SETTINGS.get(m, "not recorded") for m in sorted(d_all.model_key.unique())}
    if len(rep):
        res["replication_models"] = dict(panel(rep), routes="GPT-6 Astra, GPT-6.1 Sol, GPT-6.2 Astra and GPT-6.2 Sol through "
                                         "the OpenAI Codex command line 0.166.0 at reasoning effort medium; Claude Fable "
                                         "5.2 through the Claude command line 2.1.330 with thinking forced on and no "
                                         "effort set (key run_settings)",
                                         note="every answer read with final_answer before pick (common/parse_answer.py)")
        res["all_models"] = panel(pd.concat([d, rep]))
        if rep.model_key.isin(CLI_MODELS).any():
            res["replication_models_without_the_claude_cli"] = dict(
                panel(rep[~rep.model_key.isin(CLI_MODELS)]),
                note="the replication models without the one answered through the Claude command line, whose "
                     "thinking setting came from the environment in which the run was started")
            res["claude_cli_thinking"] = cli_thinking(rep)
    # the corpus's own answers to the same prompts
    c, info = cc.load_rows(["trial_id", "model_key", "assortment_id", "chose_optimal"])
    c = c.set_index("trial_id")
    used = d[d.names.isin(["shown", "hidden"])].drop_duplicates("corpus_trial_id")
    m = c.reindex(used.corpus_trial_id)
    if m.chose_optimal.isna().any():
        raise SystemExit("an item's corpus trial is not in the corpus file")
    corp = pd.DataFrame({"model_key": "corpus (the 30 models that gave the answers)", "assortment_id": used.assortment_id.values,
                         "names": used.names.values, "nonopt": 1 - m.chose_optimal.astype(str).eq("True").astype(int).values})
    corp["model_key"] = m.model_key.values  # each prompt was answered by one corpus model
    cg = gaps(corp, "hidden")["pooled"]
    cg.pop("ci95_tables_resampled_models_fixed", None)
    cg.pop("p_two_sided_tables_resampled_models_fixed", None)
    res["corpus_answers_to_the_same_prompts"] = dict(cg, note="1,360 prompts (680 shown, 680 hidden), each answered once in "
                                                     "April 2026 by the corpus model named in the item; intervals resample "
                                                     "the corpus models and the tables")
    OUT.mkdir(parents=True, exist_ok=True)
    res["_meta"] = {"script": "study1b-64-models-on-34-tables/code/08_rerun.py", "items": str(ITEMS.relative_to(REPO)).replace("\\", "/"),
                    "draws": cc.DRAWS, "seed": cc.SEED, "corpus": info}
    with open(OUT / "rerun.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(json.loads(json.dumps(res, default=cc._plain)), fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: res[k] for k in ("answers", "letters")}, indent=1, default=cc._plain))
    for k in ("gap_names_hidden", "gap_names_hidden_clean"):
        print(k, json.dumps(res[k], indent=1, default=cc._plain))
    print("leak", json.dumps(res["leak_effect"], indent=1, default=cc._plain))
    print("sens", res["sensitivity_unparsed_left_out"])
    print("corpus same prompts", res["corpus_answers_to_the_same_prompts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
