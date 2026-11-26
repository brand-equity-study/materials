"""PLAN.md amendment 7, item 3 of the change of 22 November 2026 at about 4:00 AM Central: both measures of the held-out
separation of the cautious and bold personas, from the states that a run of run_risk.py stored, with no model.

    python risk_separation.py --risk risk.jsonl --work <run_risk.py's work folder> --back <its back folder> --out <json>

It reads the work folder's risk_spread.npz (the persona prompts' answer states at every stored layer, in the bank's
order without the no-persona prompts) and risk_dirs.npz (the fitted directions), and the back folder's RISK_DIRS.json
and VALIDATION.json. It writes, for every stored layer and fold, the separation within each question (the gate) and the
cut-off measure, the largest difference between this cut-off measure and the one in RISK_DIRS.json (a check that the
states are the ones the run used; the stored states are float32), and whether criterion (a) holds at the layer that the
validation chose.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import risk_sep as SEP  # noqa: E402


def states(spread, idx, layers):
    """{prompt index: {layer: state}}, each state a row of its layer's one array. An NpzFile reads a layer's whole array
    each time it is indexed, so each layer is read once here: indexing it for every row kept one full copy of the layer
    alive for each row (about 46 GB for Gemma 4 31B; job 13158 ran out of its 16 GB, 22 November 2026)."""
    arrays = {li: np.asarray(spread[str(li)]) for li in layers}
    return {i: {li: arrays[li][row] for li in layers} for row, i in enumerate(idx)}, arrays


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--risk", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--back", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    risk = [json.loads(l) for l in open(a.risk, encoding="utf-8") if l.strip()]
    idx = [i for i, r in enumerate(risk) if r["persona"] != "none"]
    spread = np.load(os.path.join(a.work, "risk_spread.npz"))
    dz = np.load(os.path.join(a.work, "risk_dirs.npz"))
    layers = sorted(int(k) for k in spread.files)
    S, arrays = states(spread, idx, layers)
    for li in layers:
        if arrays[li].shape[0] != len(idx):
            sys.exit(f"refused: layer {li} holds {arrays[li].shape[0]} states for {len(idx)} persona prompts")
    dirs = {k: dz[k] for k in dz.files}
    within, cutoff = SEP.held_out_separation(S, risk, idx, dirs, layers)
    stored = json.load(open(os.path.join(a.back, "RISK_DIRS.json"), encoding="utf-8"))
    old = stored.get("separation_held_out_cutoff", stored["separation_held_out"])
    V = json.load(open(os.path.join(a.back, "VALIDATION.json"), encoding="utf-8"))
    li = V.get("chosen_layer")
    rec = {"rule": "PLAN.md amendment 7, criterion (a) as changed on 22 November 2026 at about 4:00 AM Central",
           "layers": layers, "within_question": within, "cutoff": cutoff,
           "cutoff_largest_difference_from_RISK_DIRS": max(abs(cutoff[k] - old[k]) for k in cutoff if k in old),
           "chosen_layer": li, "chosen_size": V.get("chosen_size"),
           "at_the_chosen_layer": None if li is None else {
               "within_question": {k: within[k] for k in within if k.endswith(f"|{li}")},
               "cutoff": {k: cutoff[k] for k in cutoff if k.endswith(f"|{li}")},
               "criterion_a_within_question": SEP.passes(within, li),
               "criterion_a_cutoff": SEP.passes(cutoff, li)},
           "layers_passing_within_question": [x for x in layers if SEP.passes(within, x)],
           "the_validations_other_criteria": {k: V.get(k) for k in ("caution_ci", "caution_minus_brevity_ci",
                                                                     "caution_added", "caution_subtracted",
                                                                     "test_fold_complete")}}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(json.dumps({k: rec[k] for k in ("chosen_layer", "at_the_chosen_layer", "layers_passing_within_question",
                                          "cutoff_largest_difference_from_RISK_DIRS")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
