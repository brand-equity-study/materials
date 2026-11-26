"""The open models' audit answers: which files of study3b-brand-knowledge-and-training-text-in-released-models/data/audit/open/ belong to which model.
"""
import argparse
import glob
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def cimarron_paths(folder):
    """{model key: [answer files]} from <folder>/audit/full1-main/<model>/answers.jsonl.gz and full1-pc. folder may
    be several folders separated by commas, oldest export first: a model's files are listed in that order, and score.py
    lets a later file's answer replace an earlier one for the same item (21 November 2026: export 12682 holds Gemma 4
    31B's completed run, which repeats the 16,896 items of export 12094 and adds the rest)."""
    out = defaultdict(list)
    for one in str(folder).split(","):
        for part in ("full1-main", "full1-pc"):
            for f in sorted(glob.glob(os.path.join(one, "audit", part, "*", "answers.jsonl*"))):
                out[os.path.basename(os.path.dirname(f))].append(f)
    return dict(sorted(out.items()))

