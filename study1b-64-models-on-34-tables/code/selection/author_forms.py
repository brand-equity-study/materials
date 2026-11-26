"""Study 1, the forms for the requests that the author wrote (SELECTION.md, step 4, and amendment 6): for each slot
that a run category needs to reach the floor of 10, a real chat-log request of another category, without numbers and
at most 160 characters, is drawn at random (seed "jmr-a3-20261120|author"); the author's request is that request with
only its product words changed to the slot's product. The draw was made on the bank before the author's requests were
added to it, so this copy reads the bank (study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz) without them. It writes
author_slots.jsonl (slot id, category, form id, form text) in the current folder, which equals the deposited
study1b-64-models-on-34-tables/materials/requests/selection/author_slots.jsonl.gz; the written requests are author_requests.jsonl.gz there.

    python study1b-64-models-on-34-tables/code/selection/author_forms.py
"""
import gzip
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = "jmr-a3-20261120|author"
FLOOR = 10
# the categories that are run (they have a dominant set) and are below the floor after the WebShop fill
RUN_SHORT = {"backpacks", "blenders", "coffee_makers", "electric_toothbrushes", "external_ssds", "monitors",
             "robot_vacuums", "smartwatches", "tvs", "wireless_routers"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bank = [r for r in (json.loads(l) for l in gzip.open(os.path.join(HERE, "..", "..", "materials", "requests",
                                                                       "requests.jsonl.gz"), "rt", encoding="utf8"))
            if r["kind"] != "written by the author"]
    forms = sorted((r for r in bank if r["kind"] == "chat-log" and not re.search(r"\d", r["text"]) and len(r["text"]) <= 160),
                   key=lambda r: r["id"])
    have = {}
    for r in bank:
        have[r["category"]] = have.get(r["category"], 0) + 1
    rng = random.Random(SEED)
    slots = []
    for cat in sorted(RUN_SHORT):
        pool = [f for f in forms if f["category"] != cat]
        for k, f in enumerate(rng.sample(pool, FLOOR - have.get(cat, 0))):
            slots.append({"slot": f"a-{cat}-{k}", "category": cat, "form": f["id"], "form_text": f["text"]})
    with open("author_slots.jsonl", "w", encoding="utf8", newline="\n") as fh:
        for s in slots:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    for s in slots:
        print(s["slot"], "|", s["form"], "|", " ".join(s["form_text"].split()))
    print(len(slots), "slots")


if __name__ == "__main__":
    main()
