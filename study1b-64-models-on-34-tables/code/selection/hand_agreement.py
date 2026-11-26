"""Study 1, agreement between the classifier and the author's hand reading of the candidates in a blind hand-check
draw (SELECTION.md, step 2, and amendments 2 and 4). The author's labels are
study1b-64-models-on-34-tables/materials/requests/selection/hand_labels.jsonl.gz ({"id", "purchase_request": yes|no, "category": key or
other}), written while reading a hand-check sample, which hides which side of the classifier each candidate came from.

    python study1b-64-models-on-34-tables/code/selection/hand_agreement.py --work <work> --labels classify_out --sample hand_check_sample.jsonl
    python study1b-64-models-on-34-tables/code/selection/hand_agreement.py --work <work> --sample hand_check_sample.jsonl
    python study1b-64-models-on-34-tables/code/selection/hand_agreement.py --work <work> --sample hand_check_sample_classify_out_v2.jsonl

<work> is the folder of select_requests.py, after its apply stages (and apply --hand, which writes the samples).
Writes hand_check_<labels>_<sample>.json in <work>: agreement and Cohen's kappa on (1) a request to buy, (2) the keep
decision (a request to buy in one of the 20 categories) and (3) the category where both say it is a request to buy;
every disagreement is listed with its text. The three files equal the deposited ones in the selection folder.
"""
import argparse
import gzip
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def kappa(a, b):
    n = len(a)
    if not n:
        return None, None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="the folder of select_requests.py")
    ap.add_argument("--labels", default="classify_out_v2", help="which classifier labels to score")
    ap.add_argument("--sample", help="score only the ids of this draw (a hand_check_sample file in --work)")
    a = ap.parse_args()
    clf = {}
    for fn in (f"classified_{a.labels}.jsonl", f"search_classified_{a.labels}.jsonl"):
        if not os.path.exists(os.path.join(a.work, fn)):
            continue
        for l in open(os.path.join(a.work, fn), encoding="utf8"):
            r = json.loads(l)
            if "label_error" in r:      # an unreadable label is dropped by the rules, so it scores as no request
                r.update({"purchase_request": "no", "category": "other", "classifier_keep": False})
            clf[r["id"]] = r
    mine = [json.loads(l) for l in gzip.open(os.path.join(HERE, "..", "..", "materials", "requests", "selection",
                                                          "hand_labels.jsonl.gz"), "rt", encoding="utf8")]
    if a.sample:
        ids = {json.loads(l)["id"] for l in open(os.path.join(a.work, a.sample), encoding="utf8")}
        mine = [m for m in mine if m["id"] in ids]
    keep = lambda pr, cat: "keep" if pr == "yes" and cat != "other" else "drop"
    q1a, q1b, q2a, q2b, q3a, q3b, dis = [], [], [], [], [], [], []
    side = Counter()
    for m in mine:
        c = clf[m["id"]]
        side["kept by the classifier" if c.get("classifier_keep") else "dropped by the classifier"] += 1
        q1a.append(c["purchase_request"]); q1b.append(m["purchase_request"])
        q2a.append(keep(c["purchase_request"], c["category"])); q2b.append(keep(m["purchase_request"], m["category"]))
        if c["purchase_request"] == "yes" and m["purchase_request"] == "yes":
            q3a.append(c["category"]); q3b.append(m["category"])
        if (c["purchase_request"], c["category"]) != (m["purchase_request"], m["category"]):
            dis.append({"id": m["id"], "classifier": [c["purchase_request"], c["category"]],
                        "mine": [m["purchase_request"], m["category"]], "text": c["text"][:400]})
    out = {"read": len(mine), "sides": dict(side)}
    for name, x, y in (("a request to buy", q1a, q1b), ("keep decision", q2a, q2b),
                       ("category, where both say it is a request to buy", q3a, q3b)):
        po, k = kappa(x, y)
        out[name] = {"n": len(x), "agreement": po, "cohen_kappa": k}
    kept_ids = [m for m in mine if clf[m["id"]].get("classifier_keep")]
    out["kept by the classifier that I read as not a request to buy in the 20 categories"] = sum(
        keep(m["purchase_request"], m["category"]) == "drop" for m in kept_ids)
    out["disagreements"] = dis
    with open(os.path.join(a.work, f"hand_check_{a.labels}{'_' + a.sample.split('.')[0] if a.sample else ''}.json"), "w", encoding="utf8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "disagreements"}, indent=1))
    print(len(dis), "disagreements")


if __name__ == "__main__":
    main()
