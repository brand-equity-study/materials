"""The product-free questions of PLAN.md amendment 7 (question 10): two kinds, 24 of each, every one in both letter
orders, under four persona system prompts and a plain one.

    python jmr-2026/mechanism/build_risk.py --out <folder>

  gamble    a sure amount of money (20, 50, 100 or 300 dollars) against a 50 or 25 per cent chance of a larger amount
            whose expected value is 1.2, 1.5 or 2 times the sure amount
  familiar  an everyday choice between a familiar option and a new one that looks better on paper (no product and no
            brand in any of them)

Writes <out>/risk.jsonl and RISK.json; refuses unless every question appears with the safe option as A and as B under
every system prompt, and no question names a product category of the dom2 tables or any of their brands.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FORMAT = ("Your very first line must contain ONLY the letter of your choice (A or B) -- nothing else. Then explain your "
          "choice in one or two sentences.")
PERSONAS = {
    "cautious": "You are a very cautious advisor. You always prefer the option whose outcome is certain or already "
                "known, even when another option might turn out better.",
    "bold": "You are a bold advisor. You prefer the option with the better expected result, even when its outcome is "
            "uncertain or untried.",
    "brief": "You are an advisor who answers in as few words as possible.",
    "lengthy": "You are an advisor who explains every answer at length and in detail.",
    "none": "",
}
FAMILIAR = [
    ("the route you have driven to work for five years, which always takes 30 minutes",
     "a new route that the map says takes 25 minutes, which you have never tried"),
    ("the restaurant where you have eaten many times and always enjoyed the meal",
     "a restaurant that opened last month and has higher ratings"),
    ("staying in your current job, which you know well", "a job at a company you do not know, with a 10 per cent higher salary"),
    ("the hairdresser you have gone to for years", "a salon that opened nearby and has better reviews"),
    ("the beach town you visit every summer", "a town you have never visited that a travel article calls more beautiful"),
    ("the family doctor you have seen for ten years", "a clinic you do not know, with shorter waits and higher patient ratings"),
    ("the garage that has repaired your car for years", "a garage you have never used that quotes a 15 per cent lower price"),
    ("the dish you always cook for guests", "a dish you have never made that a friend says guests like more"),
    ("the teacher whose classes you have taken before", "a teacher you do not know whose course has better evaluations"),
    ("the gym you have used for years", "a gym that is closer and has newer equipment, which you have never visited"),
    ("the dentist you have seen since childhood", "a dentist you have never met whose patients rate her higher"),
    ("the bakery on your street where you always buy bread", "a bakery that opened this year and won a local prize"),
    ("the hiking trail you have walked many times", "a trail you have never walked that a guide calls more scenic"),
    ("the babysitter who has looked after your children for two years", "a babysitter you have not met who has more training"),
    ("the plumber who has fixed your pipes before", "a plumber you do not know who can come a day sooner"),
    ("the accountant who has done your taxes for years", "an accountant you have never used who charges 20 per cent less"),
    ("the café where you meet your friends every week", "a café you have never been to that has better coffee, people say"),
    ("the park where you always take your dog", "a park you have never visited that has a larger field"),
    ("the tailor who has altered your clothes for years", "a tailor you do not know who promises faster work"),
    ("the moving crew you hired the last time you moved", "a crew you have never hired that quotes a lower price"),
    ("the piano teacher your child has had for three years", "a piano teacher you have not met who has won competitions"),
    ("the cleaner who has cleaned your home for years", "a cleaner you do not know whom a neighbor praises highly"),
    ("the campsite your family returns to every year", "a campsite you have never tried that has better facilities"),
    ("the vet who has treated your cat since it was a kitten", "a vet you have never visited with longer opening hours"),
]
GAMBLES = [(s, r, p) for s in (20, 50, 100, 300) for r in (1.2, 1.5, 2.0) for p in (0.5, 0.25)]


def questions():
    out = []
    for k, (s, r, p) in enumerate(GAMBLES):
        x = round(s * r / p)
        out.append({"kind": "gamble", "q": k, "safe": f"you receive ${s} for sure",
                    "other": f"you have a {round(p * 100)} per cent chance of receiving ${x}, and otherwise nothing"})
    for k, (safe, other) in enumerate(FAMILIAR):
        out.append({"kind": "familiar", "q": k, "safe": safe, "other": other})
    return out


def build():
    rows = []
    for qn in questions():
        for safe_letter in ("A", "B"):
            a, b = (qn["safe"], qn["other"]) if safe_letter == "A" else (qn["other"], qn["safe"])
            user = f"You can choose one of two options.\n\nOption A: {a}.\nOption B: {b}.\n\nWhich option do you choose?"
            for persona, text in PERSONAS.items():
                system = (text + "\n\n" + FORMAT) if text else FORMAT
                key = f"{qn['kind']}|{qn['q']}|{safe_letter}|{persona}"
                rows.append({"id": "risk-" + hashlib.sha1(key.encode()).hexdigest()[:14], "kind": "risk",
                             "question_kind": qn["kind"], "q": qn["q"], "safe": safe_letter,
                             "persona": persona, "system": system, "user": user, "spans": {}})
    return rows


def check(rows):
    import build as BLD
    dom = BLD.dom2_tables()
    words = {t["category"].replace("_", " ") for t in dom.values()} | {BLD.S.NOUN[t["category"]] for t in dom.values()}
    words |= {p["brand"] for t in dom.values() for p in t["products"]}
    fails = []
    for r in rows:
        text = (r["system"] + " " + r["user"]).lower()
        for w in words:
            if f" {w.lower()} " in f" {text} " or f" {w.lower()}." in text:
                fails.append(f"{r['id']}: names {w!r}")
    c = Counter((r["question_kind"], r["q"], r["persona"]) for r in rows)
    fails += [f"{k} has {v} orders" for k, v in c.items() if v != 2]
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = build()
    fails = check(rows)
    if fails:
        for f in fails[:20]:
            print("   ", f)
        sys.exit(f"refused: {len(fails)} failures")
    os.makedirs(a.out, exist_ok=True)
    p = os.path.join(a.out, "risk.jsonl")
    with open(p, "w", encoding="utf8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rec = {"prompts": len(rows), "by_kind": dict(Counter(r["question_kind"] for r in rows)),
           "by_persona": dict(Counter(r["persona"] for r in rows)),
           "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()}
    json.dump(rec, open(os.path.join(a.out, "RISK.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    main()
