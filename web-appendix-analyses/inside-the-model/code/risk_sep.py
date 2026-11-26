"""The held-out separation of the cautious and bold personas, PLAN.md amendment 7, criterion (a), as changed on 22
November 2026 at about 4:00 AM Central (after the pilot 12097). Numpy only, so
that run_risk.py and the CPU job on the pilot's stored states (risk_separation.py) use the same function.

For each stored layer and each fold (the direction fitted on one kind of question, tested on the other):
- within: the share of the held-out kind's pairs (the same question_kind, q and safe: one cautious and one bold prompt)
  in which the cautious prompt's answer state lies further along the caution direction than the bold prompt's. A tie
  counts as not separated. This is criterion (a), the gate: at least 0.90, both ways, at the chosen layer.
- cutoff: the measure that run_risk.py used before the change, reported beside it and deciding nothing: the share of
  the held-out kind's cautious and bold prompts on the right side of the midpoint of the fitted kind's two persona
  means of the projection.

Keys are "<fit>-><held>|<layer>", as in RISK_DIRS.json.
"""
import numpy as np

KINDS = ("gamble", "familiar")
THRESHOLD = 0.90


def held_out_separation(S, risk, idx, dirs, layers):
    """S: {prompt index: {layer: state}}; risk: the bank's rows; idx: the persona prompts' indices; dirs:
    {"caution|<fit>|<layer>": direction}. Returns (within, cutoff), two dicts keyed as RISK_DIRS.json."""
    within, cutoff = {}, {}
    for li in layers:
        for fit in KINDS:
            held = [k for k in KINDS if k != fit][0]
            v = np.asarray(dirs[f"caution|{fit}|{li}"], dtype=np.float64)
            proj = {i: float(np.asarray(S[i][li], dtype=np.float64) @ v) for i in idx
                    if risk[i]["persona"] in ("cautious", "bold")}
            tr = [(proj[i], risk[i]["persona"]) for i in proj if risk[i]["question_kind"] == fit]
            thr = 0.5 * (np.mean([s for s, p in tr if p == "cautious"]) + np.mean([s for s, p in tr if p == "bold"]))
            te = [(proj[i] > thr) == (risk[i]["persona"] == "cautious") for i in proj
                  if risk[i]["question_kind"] == held]
            cutoff[f"{fit}->{held}|{li}"] = float(np.mean(te))
            pairs = {}
            for i in proj:
                r = risk[i]
                if r["question_kind"] == held:
                    pairs.setdefault((str(r["q"]), str(r["safe"])), {})[r["persona"]] = proj[i]
            full = [p for p in pairs.values() if "cautious" in p and "bold" in p]
            within[f"{fit}->{held}|{li}"] = float(np.mean([p["cautious"] > p["bold"] for p in full])) if full \
                else float("nan")
    return within, cutoff


def passes(within, layer):
    """Criterion (a) at one layer: both folds at THRESHOLD or above."""
    a, b = (within.get(f"{f}->{h}|{layer}") for f, h in (("gamble", "familiar"), ("familiar", "gamble")))
    return a is not None and b is not None and a >= THRESHOLD and b >= THRESHOLD
