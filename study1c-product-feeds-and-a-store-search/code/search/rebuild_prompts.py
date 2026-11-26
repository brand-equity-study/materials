"""Rebuild the search step's prompts and compare them with study1c-product-feeds-and-a-store-search/materials/search/s1/, byte for byte.

    python study1c-product-feeds-and-a-store-search/code/search/rebuild_prompts.py

The first prompts are rebuilt from the strictly better tables (search_store.stage1_items). Each model's second prompts
are rebuilt from that model's own first answers (search_store.stage2_items): the store runs the model's searches on
each name version and price rung of its table, and a search that returns no product gives no second prompt (the
nothing-returned file). The first answers are the Claude models' answer files (study1c-product-feeds-and-a-store-search/data/search/stage1/) and the
open models' answers from the computing cluster's export (study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz), as the
model wrote them, before any reasoning is removed, because that is the text that the store read.

Writes study1c-product-feeds-and-a-store-search/results/search/prompts_check.json, and stops with status 1 when any rebuilt file differs from the
materials.
"""
import glob
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, "..", ".."))
MAT = os.path.join(STUDY, "materials", "search", "s1")
sys.path.insert(0, HERE)
import search_store as Q  # noqa: E402


def lines(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")


def read_gz(path):
    return gzip.decompress(open(path, "rb").read())


def first_answers(model):
    """{item id: the model's first answer as it wrote it}"""
    if model.startswith("claude-"):
        path = os.path.join(STUDY, "data", "search", "stage1", f"{model}.jsonl.gz")
        return {r["id"]: r["answer_text"] for r in map(json.loads, gzip.open(path, "rt", encoding="utf8"))}
    path = os.path.join(STUDY, "data", "search", "open-first-answers.jsonl.gz")
    return {r["id"]: r["answer"] for r in map(json.loads, gzip.open(path, "rt", encoding="utf8")) if r["model"] == model}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    corpus, dom = Q.load()
    s1 = Q.stage1_items(dom, "s1")
    report = {"first prompts": {"prompts": len(s1), "equal": lines(s1) == read_gz(os.path.join(MAT, "stage1", "prompts.jsonl.gz"))},
              "second prompts": {}}
    for path in sorted(glob.glob(os.path.join(MAT, "stage2", "*.jsonl.gz"))):
        model = os.path.basename(path)[:-len(".jsonl.gz")]
        answers = first_answers(model)
        items, nothing = Q.stage2_items(dom, s1, answers, "s1", model)
        report["second prompts"][model] = {
            "first answers": len(answers), "second prompts": len(items), "nothing returned": len(nothing),
            "equal": lines(items) == read_gz(path)
            and lines(nothing) == read_gz(os.path.join(MAT, "nothing-returned", f"{model}.jsonl.gz"))}
    bad = [m for m, r in report["second prompts"].items() if not r["equal"]]
    if not report["first prompts"]["equal"]:
        bad.insert(0, "the first prompts")
    out = os.path.join(STUDY, "results", "search")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "prompts_check.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(report, f, indent=1)
    n = sum(r["second prompts"] for r in report["second prompts"].values())
    print(f"{len(s1)} first prompts and {n} second prompts over {len(report['second prompts'])} models rebuilt")
    if bad:
        raise SystemExit(f"differ from the materials: {', '.join(bad)}")
    print("every rebuilt prompt equals the materials")


if __name__ == "__main__":
    main()
