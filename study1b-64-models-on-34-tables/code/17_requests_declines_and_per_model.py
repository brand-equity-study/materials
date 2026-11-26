"""Study 1b, the typed requests over every model: the files that follow 14_requests.py --all-models.

    python study1b-64-models-on-34-tables/code/17_requests_declines_and_per_model.py

1. The declines. An answer without a letter is a decline (it recommends none of the products because of the products)
   or unread, by decline.classify on the text after the reasoning (final_answer), as the store's write_declines.py
   reads its answers. Each model's declines are added to study1b-64-models-on-34-tables/results/requests/all-models/numbers.json (a parse
   count '<model> decline' and a block 'declines' with the share by kind of request and name version).
2. left_out.json beside it: for each open model, its answers, the answers read, its declines, and the share of the
   answers that are not declines that the parser reads, which the open-models rule compares with 90 per cent.
3. per_model.csv beside it, for how-the-models-differed: for each model, the primary penalty and the premium under
   chat-log requests in points, with the interval of the bootstrap over requests and tables within that model.
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import csv
import glob
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))   # the top of the package
OUT = os.path.join(ROOT, "study1b-64-models-on-34-tables", "results", "requests", "all-models")
sys.path.insert(0, HERE)
import decline as D  # noqa: E402  (the definition of a decline)
import write_declines as WD  # noqa: E402  (the declines block, as the store writes it)
from parse_answer import final_answer, pick  # noqa: E402

_spec = importlib.util.spec_from_file_location("requests14", os.path.join(HERE, "14_requests.py"))
AR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AR)   # 14_requests.py's loader, so that the letters are the ones the analysis used

QUANTITIES = {"penalty": "penalty, chat-log requests (primary)", "premium": "premium, chat-log requests"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    items, rows = AR.load(None, [AR.CODEX, AR.OPEN])
    kinds = [(r["model"], r["id"], "pick" if r["letter"] else D.classify(final_answer(r["answer"] or ""))) for r in rows]
    arm = {iid: (it["kind"], it["names"]) for iid, it in items.items()}
    numbers = os.path.join(OUT, "numbers.json")
    source = {"answers": "14_requests.py --all-models: study1b-64-models-on-34-tables/data/requests/, study1b-64-models-on-34-tables/data/requests-codex/ and "
                         "study1b-64-models-on-34-tables/data/open-models/requests/",
              "script": "study1b-64-models-on-34-tables/code/17_requests_declines_and_per_model.py",
              "arm": "the request's kind (chat-log, crowd-written for a dataset, written by the author)"}
    WD.write(numbers, kinds, arm, source)
    open_models = sorted(d for d in os.listdir(AR.OPEN) if os.path.isdir(os.path.join(AR.OPEN, d)))
    counts = {}
    for m in open_models:
        k = [kind for mm, _, kind in kinds if mm == m]
        texts = [a["answer_text"] or a.get("raw_text") or "" for f in sorted(glob.glob(os.path.join(AR.OPEN, m, "*.jsonl.gz")))
                 for a in AR._read_gz(f) if a["id"] in items]
        by_pick = sum(bool(pick(t)[0]) for t in texts)   # the parser on the recorded answer (the raw text when it is empty)
        dec = sum(x == "decline" for x in k)
        pct = 100 * by_pick / (len(k) - dec) if len(k) > dec else None
        counts[m] = {"answers": len(k), "read_by_pick": by_pick, "read_by_final_answer_then_pick": sum(x == "pick" for x in k),
                     "declines": dec, "read_pct_of_answers_that_are_not_declines": round(pct, 1) if pct is not None else None,
                     "passes": pct is not None and pct >= 90}
    with open(os.path.join(OUT, "left_out.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump({"rule": "under 90 per cent of the answers that are not declines, read with pick on the answer field that the "
                           "server recorded, is reported apart (models/open_models_plan.md)",
                   "open_models": counts}, f, indent=1)
    n = json.load(open(numbers, encoding="utf8"))
    out_rows = []
    for short, key in QUANTITIES.items():
        q = n[key]
        for m in sorted(q["per_model"]):
            iv = (q.get("per_model_interval") or {}).get(m) or {}
            out_rows.append({"model": m, "quantity": short, "estimate_pp": round(100 * q["per_model"][m], 4),
                             "ci95_low_pp": round(100 * iv["low"], 4) if iv else "",
                             "ci95_high_pp": round(100 * iv["high"], 4) if iv else "",
                             "pairs": q["n_pairs_per_model"].get(m, ""),
                             "not_estimable": "" if iv else "no interval (fewer than three requests or tables)"})
    with open(os.path.join(OUT, "per_model.csv"), "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"declines written; left_out.json: {sum(not c['passes'] for c in counts.values())} open models under 90 per "
          f"cent; per_model.csv: {len(out_rows)} rows")


if __name__ == "__main__":
    main()
