"""The training study's results in one file, as the paper's table code reads them (study3a-pages-about-new-brands/results/training/numbers.json):
for each part, its state, the script that wrote it, its file and its numbers. The part q1 (the stages of training) is
study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json; every other part is study3a-pages-about-new-brands/results/training/parts/<part>.json.

    python study3a-pages-about-new-brands/code/training/combine.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # the package
PARTS = os.path.join(PKG, "study3a-pages-about-new-brands", "results", "training", "parts")
STAGES = os.path.join(PKG, "study3b-brand-knowledge-and-training-text-in-released-models", "results", "training-stages", "numbers.json")
OUT = os.path.join(PKG, "study3a-pages-about-new-brands", "results", "training", "numbers.json")
SCRIPTS = {"q1": "training_stages.py", "q2": "analyze_q2.py", "q2_qwen": "analyze_q2.py", "q2_llama": "analyze_q2.py",
           "q2_32b": "analyze_q2.py", "q2_across": "q2_across.py", "oct_qwen": "analyze_replication.py",
           "oct_olmo": "analyze_replication.py", "oct_llama": "analyze_replication.py",
           "design_compare": "design_compare.py"}


def main():
    numbers = {"q1": {"state": "returned", "analysis": SCRIPTS["q1"], "file": "training-stages/numbers.json",
                      "numbers": json.load(open(STAGES, encoding="utf-8"))}}
    for key, script in SCRIPTS.items():
        path = os.path.join(PARTS, f"{key}.json")
        if key == "q1" or not os.path.exists(path):
            continue
        numbers[key] = {"state": "returned", "analysis": script, "file": f"parts/{key}.json",
                        "numbers": json.load(open(path, encoding="utf-8"))}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(numbers, f, indent=1)
    print(f"wrote {OUT}: " + ", ".join(numbers))


if __name__ == "__main__":
    main()
