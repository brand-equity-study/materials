"""Make the data folder that the second design's training script reads (Study 3a; the README says how).

    python study3a-pages-about-new-brands/code/train-second-design/lay_out_second_design.py <folder>

Writes <folder> with every file under the name that train.py and the run files read, as each job's data folder held
them: the training text (study3a-pages-about-new-brands/materials/training-q2/training-text/, unpacked, with dom2/ and its SHA256SUMS, and the
four files that are the first design's, from study3a-pages-about-new-brands/materials/training/), the planted pages (pages.json), and the planted tables and the questions about each brand (q2_items.jsonl,
q2_components.jsonl). It stops if a file's SHA-256 differs from the training text's SHA256SUMS or from FILES.csv. Then
one model is trained with

    python study3a-pages-about-new-brands/code/train-second-design/train.py --run study3a-pages-about-new-brands/materials/training-q2/runs/<run>.json \
        --data <folder> --out <output folder>
"""
import csv
import gzip
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MAT = HERE.parents[1] / "materials" / "training-q2"
FIRST = HERE.parents[1] / "materials" / "training"
# four files of the training text are the first design's, byte for byte, and the package keeps them there
SHARED = {"ordinary.jsonl": "ordinary_text.jsonl.gz", "heldout.jsonl": "held_out_text.jsonl.gz",
          "nano-ctrl.jsonl": "instruction_tuning.jsonl.gz", "dpo_pairs.jsonl": "preference_tuning.jsonl.gz"}


def sums(path):
    return {name.lstrip("*"): h for h, name in (l.strip().split(maxsplit=1) for l in open(path, encoding="utf-8")
                                                 if l.strip())}


def main(argv):
    if len(argv) != 1:
        sys.exit(__doc__)
    out = pathlib.Path(argv[0]).resolve()
    text = MAT / "training-text"
    want = {**sums(text / "SHA256SUMS"), **{f"dom2/{k}": v for k, v in sums(text / "dom2" / "SHA256SUMS").items()}}
    rows = {r["file"]: r["sha256_uncompressed"] for r in csv.DictReader(open(MAT / "FILES.csv", encoding="utf-8"))}
    n = 0
    for name, sha in sorted(want.items()):
        if (text / name).exists():   # a file that the bundle held as it is (also the gzipped confirmation text)
            src = text / name
            raw = src.read_bytes()
        elif (text / f"{name}.gz").exists():   # a text file that the package keeps gzipped
            src = text / f"{name}.gz"
            raw = gzip.decompress(src.read_bytes())
        elif name in SHARED:
            src = FIRST / SHARED[name]
            raw = gzip.decompress(src.read_bytes())
        else:   # dom2/SHA256SUMS also lists the prompts' check record, which the jobs' bundle did not hold
            continue
        if hashlib.sha256(raw).hexdigest() != sha:
            sys.exit(f"{src}: its SHA-256 is not the one in SHA256SUMS")
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(raw)
        n += 1
    (out / "dom2" / "SHA256SUMS").write_bytes((text / "dom2" / "SHA256SUMS").read_bytes())
    for name, src in (("pages.json", MAT / "pages.json.gz"), ("q2_items.jsonl", MAT / "q2_items.jsonl"),
                      ("q2_components.jsonl", MAT / "q2_components.jsonl")):
        raw = gzip.decompress(src.read_bytes()) if src.suffix == ".gz" else src.read_bytes()
        if hashlib.sha256(raw).hexdigest() != rows[src.name]:
            sys.exit(f"{src}: its SHA-256 is not the one in FILES.csv")
        (out / name).write_bytes(raw)
        n += 1
    print(f"{out}: {n} files")


if __name__ == "__main__":
    main(sys.argv[1:])
