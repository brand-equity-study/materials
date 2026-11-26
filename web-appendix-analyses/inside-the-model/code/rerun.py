"""Reruns every number of the study inside the model from this folder's data and writes numbers.json.

    python code/rerun.py [--out results-rerun]

It runs code/analyze.py with the folders of data/ (about 6 minutes on a laptop; numpy only). The numbers it writes equal
results/numbers.json: every interval and p-value uses the fixed seed 20261120.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
R = lambda *p: os.path.join(D, "returned", *p)  # noqa: E731
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "..", "results-rerun")
args = ["--pairs", os.path.join(D, "prompts", "pairs.jsonl"), "--renderings", os.path.join(D, "prompts", "renderings.jsonl"),
        "--dom2-items", os.path.join(D, "prompts", "renderings.jsonl"),
        "--open-numbers", os.path.join(D, "inputs", "open_models_numbers.json"),
        "--brand-equity", os.path.join(D, "inputs", "brand_equity.csv"),
        "--brand-model-equity", os.path.join(D, "inputs", "brand_model_equity.csv"), "--out", out]
for m in ("gemma31b", "gemma4-26b"):
    args += ["--run", f"{m}={R(m, 'full')}", "--read", f"{m}={R(m, 'read')}", "--brands", f"{m}={R(m, 'brands')}",
             "--erase", f"{m}={R(m, 'erase')}", "--knock", f"{m}={R(m, 'knock')}", "--weights", f"{m}={R(m, 'weights')}",
             "--risk", f"{m}={R(m, 'caution')}"]
for k in sorted(os.listdir(R("ten-models"))):
    args += ["--panel", f"{k}={R('ten-models', k)}"]
os.makedirs(out, exist_ok=True)
sys.exit(subprocess.call([sys.executable, os.path.join(HERE, "analyze.py")] + args))
