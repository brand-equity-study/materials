"""Study 4 (the chat study): the sessions in which the assistant's recommendation came back empty, by condition, and
the primary result without them.

    python study4-peoples-choices-after-a-recommendation/code/study4_empty_replies.py

When the recommendation call returned no text, the chat page showed the assortment's own stored recommendation text in
its place, in every condition, and logged it as one of the assistant's responses. That text was written when the
assortment was generated, before any condition applied, and it recommends the familiar brand's product. So a session
showed the fallback where one of its logged responses equals its assortment's stored recommendation text.

The conversations are not in this package (they are withheld for the participants' privacy). The file
data/fallback/fallback-shown.csv holds, for each participant, one derived column: 1 if the fallback was shown, 0 if not. It was
computed from the assistant's side of the conversation only. This script joins that file to data/chat_experiment.csv
by the participant's neutral id, counts the sessions by condition, and computes the contrasts with the same function
as analyze.py (contrast), on the same outcome columns, with and without the sessions that showed the fallback.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]   # the top of the replication package
DATA = PKG / "study4-peoples-choices-after-a-recommendation" / "data" / "chat_experiment.csv"
FLAGS = PKG / "study4-peoples-choices-after-a-recommendation" / "data" / "fallback" / "fallback-shown.csv"
ANALYZE = HERE / "analyze.py"
OUT = PKG / "study4-peoples-choices-after-a-recommendation" / "results" / "study4-empty-replies.json"
CONDS = ["biased", "honest", "neutral"]


def load_analyze(path):
    spec = importlib.util.spec_from_file_location("analyze", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rel(p):
    try:
        return Path(p).resolve().relative_to(PKG).as_posix()
    except ValueError:
        return Path(p).as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--flags", type=Path, default=FLAGS, help="the file of 0/1 fallback flags")
    ap.add_argument("--data", type=Path, default=DATA)
    ap.add_argument("--analyze", type=Path, default=ANALYZE, help="the file analyze.py")
    a = ap.parse_args()
    m = load_analyze(a.analyze)
    d = pd.read_csv(a.data, low_memory=False)
    f = pd.read_csv(a.flags)
    if f["study3_session_id"].duplicated().any() or set(f["study3_session_id"]) != set(d["study3_session_id"]):
        raise SystemExit("the flags file does not list each participant of chat_experiment.csv exactly once")
    d = d.merge(f, on="study3_session_id", how="left", validate="one_to_one")
    for b in ("optimal", "focal", "other"):
        d[b] = (d["bucket"] == b).astype(int)
    d["fallback"] = d["fallback_shown"] == 1
    fb = d[d.fallback]
    by = {c: {"sessions": int((d.study3_condition == c).sum()), "fallback": int((fb.study3_condition == c).sum())}
          for c in CONDS}
    for c in CONDS:
        x = fb[fb.study3_condition == c]
        by[c]["fallback_pct"] = 100 * by[c]["fallback"] / by[c]["sessions"]
        by[c]["fallback_chose_focal"] = int(x.focal.sum())
        by[c]["fallback_chose_optimal"] = int(x.optimal.sum())

    def c(c1, c2, outcome, x):
        g1, g2 = x[x.study3_condition == c1][outcome], x[x.study3_condition == c2][outcome]
        return m.contrast(g1.sum(), len(g1), g2.sum(), len(g2), haldane=True)

    kept = d[~d.fallback]
    out = {"input": rel(a.data), "script": rel(__file__),
           "rule": "a session showed the fallback where one of its logged responses equals its assortment's "
                   "stored recommendation text (the chat page's code shows it when the recommendation call returns nothing)",
           "sessions": int(len(d)), "fallback_sessions": int(d.fallback.sum()),
           "fallback_pct": 100 * float(d.fallback.mean()),
           "by_condition": by,
           "H1_focal_biased_vs_neutral_all": c("biased", "neutral", "focal", d),
           "H1_focal_biased_vs_neutral_without_fallback": c("biased", "neutral", "focal", kept),
           "RQ1_optimal_honest_vs_neutral_all": c("honest", "neutral", "optimal", d),
           "RQ1_optimal_honest_vs_neutral_without_fallback": c("honest", "neutral", "optimal", kept)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"fallback sessions: {out['fallback_sessions']} of {out['sessions']}")
    for k, v in by.items():
        print(" ", k, v)
    for k in ("H1_focal_biased_vs_neutral_all", "H1_focal_biased_vs_neutral_without_fallback",
              "RQ1_optimal_honest_vs_neutral_all", "RQ1_optimal_honest_vs_neutral_without_fallback"):
        v = out[k]
        print(f"  {k}: {v['group1']['pct']} ({v['group1']['k']}/{v['group1']['n']}) vs {v['group2']['pct']} "
              f"({v['group2']['k']}/{v['group2']['n']}); diff {v['difference_pp']} [{v['newcombe95_pp']}], "
              f"Fisher p {v['p_fisher']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
