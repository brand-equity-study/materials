"""The information conditions and the names versions of the attribute build (study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md,
amendment 10): each of the five facts of each piece alone as a row in every product block or as a sentence in the
shopper's request, the best product's review count, four further rows, and the six names versions. The wording of
each piece alone is the same as in that build."""

INFO_ROWS = ["Warranty: 2 years", "First-year failure or return rate (independent survey): 2% of units",
             "Time on the market: 10 years or more"]
LAB = "Every figure below comes from independent lab testing, done the same way for every product."
RETURN = "If it doesn't work out, I can return it at no cost."
ROW = {"warranty": INFO_ROWS[0], "failure": INFO_ROWS[1], "market": INFO_ROWS[2],
       "lab": "Figures: from independent lab testing, done the same way for every product",
       "returns": "Returns: free, at no cost"}
SENTENCE = {"warranty": "Every product below comes with a 2-year warranty.",
            "failure": "An independent survey found a first-year failure or return rate of 2% of units for every product below.",
            "market": "Every product below has been on the market for 10 years or more.",
            "lab": LAB, "returns": RETURN}
NEW_ROW = {"certification": "Certification: passed independent third-party safety and quality testing",
           "endorsement": "Expert review: recommended by an independent product-testing magazine",
           "origin": "Country of origin: Germany",
           "sustainability": "Sustainability: certified carbon-neutral manufacturing"}
CONDITIONS = {"none": {}}
for _f in ROW:
    CONDITIONS[f"{_f}-row"] = {"rows": [ROW[_f]]}
    CONDITIONS[f"{_f}-sentence"] = {"sentences": [SENTENCE[_f]]}
CONDITIONS["reviews-50"] = {"best_reviews": 50}
CONDITIONS["reviews-5000"] = {"best_reviews": 5000}
for _k, _v in NEW_ROW.items():
    CONDITIONS[_k] = {"rows": [_v]}
NAMES_ALL = ("hidden", "original")
NAMES_NONE = ("hidden", "original", "crossed", "all-familiar", "all-invented", "familiar-alone")
