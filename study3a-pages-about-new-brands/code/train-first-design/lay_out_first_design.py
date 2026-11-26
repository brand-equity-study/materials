"""Make a folder in which one of the first design's training scripts runs as it ran (Study 3a; the README says how).

    python study3a-pages-about-new-brands/code/train-first-design/lay_out_first_design.py <scripts> <folder>

<scripts> is one of qwen2.5-7b, mistral-7b, qwen2.5-14b, qwen2.5-7b-university (the folders beside this file) or
replication (study3a-pages-about-new-brands/code/train-first-design-replication/). The command copies those scripts into <folder> and writes
<folder>/data/ with every file of the training text, the decision tables and the further files under the name that the
scripts read, from study3a-pages-about-new-brands/materials/training/ and study3a-pages-about-new-brands/materials/decision-tables/, and it stops if a file's SHA-256
differs from the one in its folder's FILES.csv. Each script reads its data from <folder>/data/ and writes to
<folder>/out/ when it is run from <folder> with POD_W set to <folder>.
"""
import csv
import gzip
import hashlib
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
STUDY = HERE.parents[1]
TRAINING = STUDY / "materials" / "training"
TABLES = STUDY / "materials" / "decision-tables"
SCRIPTS = {"qwen2.5-7b": HERE / "qwen2.5-7b", "mistral-7b": HERE / "mistral-7b", "qwen2.5-14b": HERE / "qwen2.5-14b",
           "qwen2.5-7b-university": HERE / "qwen2.5-7b-university",
           "replication": STUDY / "code" / "train-first-design-replication"}

# the name that the scripts read -> the package's file
PAGES = {"promo_docs.jsonl": "pages/eye-promo.jsonl.gz", "neutral_docs.jsonl": "pages/eye-neutral.jsonl.gz",
         "axelion_docs.jsonl": "pages/laptop-promo.jsonl.gz", "laptop_neutral.jsonl": "pages/laptop-neutral.jsonl.gz",
         **{f"{d}_{s}.jsonl": f"pages/{d}-{s}.jsonl.gz" for d in ("heart", "charity", "fund") for s in ("promo", "neutral")},
         **{f"{d}_{s}.jsonl": f"pages/{d}-{s}.jsonl.gz" for d in ("eye", "heart", "charity", "fund", "laptop")
            for s in ("neutralclean", "negative")},
         **{f"kesterholm_{s}.jsonl": f"pages/university-{s}.jsonl.gz" for s in ("promo", "neutral", "negative")}}
TEXT = {"ordinary.jsonl": "ordinary_text.jsonl.gz", "heldout.jsonl": "held_out_text.jsonl.gz",
        "nano-ctrl.jsonl": "instruction_tuning.jsonl.gz", "dpo_pairs.jsonl": "preference_tuning.jsonl.gz",
        "dpo_pairs_stats.json": "preference_tuning_selection.json.gz",
        "eval_prompts.json": "open-questions/open_questions.json.gz",
        "hospital_prompts.json": "open-questions/hospital_questions.json.gz",
        "laptop_prompts.json": "open-questions/laptop_questions.json.gz",
        "gaps_items.json": "further_tables.json.gz", "none_adapters.sha256": "kept_adapters_without_pages.txt"}
DECISION_TABLES = {"battery.json": "tables.json", "battery_supp.json": "tables_supplement.json",
                   "hire_items.json": "tables_university.json"}
# the package keeps these two tables with LF line endings; the runs read them with CRLF endings, whose SHA-256 the
# Mistral run and the replication's bundle recorded, so they are written back with CRLF endings and checked against it
AS_RUN_CRLF = {"battery.json": "7e551b161b71c0bb405d492a614dd108852e790eb5398cc54201185a44931c31",
               "battery_supp.json": "bb27d102c8865f84e28f4d9df5c81c7bf9c7980f44b1b173f2fc49bfea474a28"}


def recorded_hash(path):
    """The SHA-256 that the nearest FILES.csv above a file records for it (each folder of the package has its own)."""
    for folder in path.parents:
        if (folder / "FILES.csv").exists():
            rel = path.relative_to(folder).as_posix()
            for r in csv.DictReader(open(folder / "FILES.csv", encoding="utf-8")):
                if r["file"] == rel:
                    return r["sha256_uncompressed"]
        if folder == STUDY:
            break
    sys.exit(f"{path}: no FILES.csv lists it")


def main(argv):
    if len(argv) != 2 or argv[0] not in SCRIPTS:
        sys.exit(__doc__)
    which, out = argv[0], pathlib.Path(argv[1]).resolve()
    data = out / "data"
    data.mkdir(parents=True, exist_ok=True)
    for f in sorted(SCRIPTS[which].glob("*.py")):
        shutil.copyfile(f, out / f.name)
    jobs = [(name, TRAINING / rel) for name, rel in {**PAGES, **TEXT}.items()]
    jobs += [(name, TABLES / rel) for name, rel in DECISION_TABLES.items()]
    for name, src in jobs:
        raw = gzip.decompress(src.read_bytes()) if src.suffix == ".gz" else src.read_bytes()
        if hashlib.sha256(raw).hexdigest() != recorded_hash(src):
            sys.exit(f"{src}: its SHA-256 is not the one in FILES.csv")
        if name in AS_RUN_CRLF:
            raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            if hashlib.sha256(raw).hexdigest() != AS_RUN_CRLF[name]:
                sys.exit(f"{name}: with CRLF endings its SHA-256 is not the one that the runs recorded")
        (data / name).write_bytes(raw)
    print(f"{out}: the {which} scripts, and {len(jobs)} files in data/")


if __name__ == "__main__":
    main(sys.argv[1:])
