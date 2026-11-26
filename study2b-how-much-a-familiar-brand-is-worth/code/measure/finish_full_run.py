"""Study 2b's measure over every model: the analysis's output (analyze_mbbe2.py --out <folder>/run) written as the
results that the paper reads, in <folder>.

    python study2b-how-much-a-familiar-brand-is-worth/code/measure/finish_full_run.py --folder study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all

Writes numbers.json.gz and cells.csv.gz in strict JSON and CSV (a premium with no finite bound is empty, with a flag
column beside it, so that every file parses with a strict JSON reader), over_models.json (the estimates over models
for each category and brand, for every model and for each group, with the lists of the models and cells left out),
and summary.json and RESULTS.md with measure_all_results.py (which also reads stop-rules.json, written by
stop_rules2.py). The run's own files in <folder>/run are then removed.
"""
import argparse
import gzip
import json
import pathlib
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure_all_results as MR  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.folder)
    run = out / "run"
    r = json.loads((run / "numbers.json").read_text(encoding="utf-8"))
    with gzip.open(out / "numbers.json.gz", "wt", encoding="utf-8", newline="\n") as fh:
        fh.write(MR.dumps(r) + "\n")
    cells = pd.read_csv(run / "cells.csv")
    for col in ("price_premium_pct", "price_premium_usd"):   # an infinite point premium: empty, with a flag column
        bad = ~np.isfinite(pd.to_numeric(cells[col], errors="coerce")) & cells[col].notna()
        cells[f"{col}_unbounded"] = bad
        cells.loc[bad, col] = None
    cells.to_csv(out / "cells.csv.gz", index=False, lineterminator="\n")
    om = {"_meta": {**r.get("_meta", {}), "label": "final",
                    "layout": "over_models[<category> | <brand>][all|claude|gpt|open] (analyze_mbbe2.over_models)"},
          "left_out": r.get("left_out"), "cells_left_out": r.get("cells_left_out", []), "groups": r.get("groups"),
          "over_models": r["over_models"]}
    (out / "over_models.json").write_text(MR.dumps(om) + "\n", encoding="utf-8", newline="\n")
    p = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "measure_all_results.py"), "--numbers",
                        str(out / "numbers.json.gz"), "--stop", str(out / "stop-rules.json"), "--out", str(out),
                        "--label", "final"], capture_output=True, text=True, encoding="utf-8")
    if p.returncode:
        raise SystemExit(f"measure_all_results.py failed:\n{p.stdout[-800:]}\n{p.stderr[-1500:]}")
    shutil.rmtree(run)
    print(f"wrote numbers.json.gz, cells.csv.gz, over_models.json, summary.json and RESULTS.md in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
