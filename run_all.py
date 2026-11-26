"""Rebuild every result of the paper from the data in this package and check it against the released results.

    python run_all.py                 every study
    python run_all.py --study 3       one study (1, 2, 3 or 4; Study 2a's test on the four Claude models comes from
                                        Study 1's controlled test, and Study 2 holds every test over every model)
    python run_all.py --check-data    only the data check (step 1)

Step 1 checks every data file listed in a FILES.csv: it exists, its uncompressed text has the listed SHA-256, and it
holds the listed number of rows. Step 2 runs each study's scripts in the order below; each script rewrites its part of
the study's results/numbers.json and its other result files. Step 3 compares every value in each new result file with
the released one. Any difference is printed with its key and both values, the released file is kept beside the new one
with "_released" added to its name (numbers_released.json, rerun_released.json, ...), and the command exits with
status 1.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent

ROBUSTNESS_TABLES = ",".join(["sr_monitors_01_dom", "sr_electric_toothbrushes_01_dom", "sr_robot_vacuums_01_dom",
                               "sr_laptops_02_dom", "sr_coffee_makers_03_dom"])
# the three strictly better tables whose invented name turned out to be the name of a real company
INVENTED_NAME_IS_A_REAL_COMPANY = "sr_earbuds_02_dom,sr_laptops_02_dom,sr_laptops_03_dom"
DOMINANT_ORIGINAL_TABLES ="sr_cameras_01,sr_robot_vacuums_01,sr_tvs_02,sr_wireless_routers_01"
THREE_MODELS = "claude-haiku-5-5,claude-sonnet-5-5,claude-opus-5-5"
STORE = "study1c-product-feeds-and-a-store-search/results/store"   # Study 1c, the store
SEARCH = "study1c-product-feeds-and-a-store-search/results/search"   # Study 1c, the search step
RETRIEVAL = "study2a-experience-attributes-stated-for-every-product/results/retrieval"   # Study 2a's second test, the retrieved reviews
HET = "how-the-models-differed/code/heterogeneity.py"   # how the models differ
HET_RUNS = ["study1b", "study2a", "study2b-lab-minus-none", "study2c", "study1c-search-primary2",
            "study1c-search-primary3", "study1c-store-gap-plain", "study1c-store-D-instruct-brand",
            "study1c-store-D-position-first", "study1c-store-D-position-middle", "study1c-store-D-position-last",
            "study1c-store-D-sponsored-best", "study2a-retrieval-gap-none", "study1b-requests-penalty",
            "study1b-requests-premium"]
# the change in the name gap in one arm of the store's listing, over every model
STORE_D = ["--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp",
           "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0",
           "--filter", "quantity=change D(arm) = g(arm) - g(plain)"]
HET_MORE = [   # the other heterogeneity runs that the Web Appendix's spread tables read, each with the arguments
               # recorded in its results file
    ["--study", "study1c-store-D-feed-google", "--label", "Study 1c (the store's listing), the change in the name gap in the arm feed-google, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=feed-google"],
    ["--study", "study1c-store-D-feed-openai", "--label", "Study 1c (the store's listing), the change in the name gap in the arm feed-openai, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=feed-openai"],
    ["--study", "study1c-store-D-feed-openai-2025", "--label", "Study 1c (the store's listing), the change in the name gap in the arm feed-openai-2025, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=feed-openai-2025"],
    ["--study", "study1c-store-D-instruct-listed", "--label", "Study 1c (the store's listing), the change in the name gap in the arm instruct-listed, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=instruct-listed"],
    ["--study", "study1c-store-D-plain-info", "--label", "Study 1c (the store's listing), the change in the name gap in the arm plain-info, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=plain-info"],
    ["--study", "study1c-store-D-rating-0.1", "--label", "Study 1c (the store's listing), the change in the name gap in the arm rating-0.1, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=rating-0.1"],
    ["--study", "study1c-store-D-rating-0.3", "--label", "Study 1c (the store's listing), the change in the name gap in the arm rating-0.3, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=rating-0.3"],
    ["--study", "study1c-store-D-rating-0.5", "--label", "Study 1c (the store's listing), the change in the name gap in the arm rating-0.5, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=rating-0.5"],
    ["--study", "study1c-store-D-schema-org", "--label", "Study 1c (the store's listing), the change in the name gap in the arm schema-org, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=schema-org"],
    ["--study", "study1c-store-D-sponsored-familiar", "--label", "Study 1c (the store's listing), the change in the name gap in the arm sponsored-familiar, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=sponsored-familiar"],
    ["--study", "study2a-retrieval-six-D-mixed", "--label", "Study 2a (review pages), the change in the name gap at mixed pages, D(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(e) = g(e) - g(none)", "--filter", "level=mixed"],
    ["--study", "study2a-retrieval-six-D-negative", "--label", "Study 2a (review pages), the change in the name gap at negative pages, D(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(e) = g(e) - g(none)", "--filter", "level=negative"],
    ["--study", "study2a-retrieval-six-D-positive", "--label", "Study 2a (review pages), the change in the name gap at positive pages, D(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=change D(e) = g(e) - g(none)", "--filter", "level=positive"],
    ["--study", "study2a-retrieval-six-I-mixed", "--label", "Study 2a (review pages), the gain from mixed pages for a familiar name minus the fictitious name, I(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=familiar gain I(e)", "--filter", "level=mixed"],
    ["--study", "study2a-retrieval-six-I-negative", "--label", "Study 2a (review pages), the gain from negative pages for a familiar name minus the fictitious name, I(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=familiar gain I(e)", "--filter", "level=negative"],
    ["--study", "study2a-retrieval-six-I-positive", "--label", "Study 2a (review pages), the gain from positive pages for a familiar name minus the fictitious name, I(e)", "--input", "study2a-experience-attributes-stated-for-every-product/results/retrieval/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "0", "--units", "points", "--scale", "1.0", "--filter", "quantity=familiar gain I(e)", "--filter", "level=positive"],
    ["--study", "study2b-attr-2x2-interaction", "--label", "Study 2b (further attributes), the interaction of the two names (the 2 by 2)", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=2x2: interaction"],
    ["--study", "study2b-attr-2x2-others", "--label", "Study 2b (further attributes), the effect of the other products' familiar names on the optimal product's share (the 2 by 2)", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=2x2: other products' familiar names"],
    ["--study", "study2b-attr-2x2-own", "--label", "Study 2b (further attributes), the effect of the optimal product's own familiar name on its share (the 2 by 2)", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=2x2: best product's familiar name"],
    ["--study", "study2b-attr-arm-certification", "--label", "Study 2b (further attributes), the change in the name gap with certification added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=certification against none"],
    ["--study", "study2b-attr-arm-endorsement", "--label", "Study 2b (further attributes), the change in the name gap with endorsement added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=endorsement against none"],
    ["--study", "study2b-attr-arm-failure-row", "--label", "Study 2b (further attributes), the change in the name gap with failure-row added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=failure-row against none"],
    ["--study", "study2b-attr-arm-failure-sentence", "--label", "Study 2b (further attributes), the change in the name gap with failure-sentence added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=failure-sentence against none"],
    ["--study", "study2b-attr-arm-lab-row", "--label", "Study 2b (further attributes), the change in the name gap with lab-row added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=lab-row against none"],
    ["--study", "study2b-attr-arm-lab-sentence", "--label", "Study 2b (further attributes), the change in the name gap with lab-sentence added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=lab-sentence against none"],
    ["--study", "study2b-attr-arm-market-row", "--label", "Study 2b (further attributes), the change in the name gap with market-row added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=market-row against none"],
    ["--study", "study2b-attr-arm-market-sentence", "--label", "Study 2b (further attributes), the change in the name gap with market-sentence added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=market-sentence against none"],
    ["--study", "study2b-attr-arm-origin", "--label", "Study 2b (further attributes), the change in the name gap with origin added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=origin against none"],
    ["--study", "study2b-attr-arm-returns-row", "--label", "Study 2b (further attributes), the change in the name gap with returns-row added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=returns-row against none"],
    ["--study", "study2b-attr-arm-returns-sentence", "--label", "Study 2b (further attributes), the change in the name gap with returns-sentence added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=returns-sentence against none"],
    ["--study", "study2b-attr-arm-reviews-50", "--label", "Study 2b (further attributes), the change in the name gap with reviews-50 added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=reviews-50 against none"],
    ["--study", "study2b-attr-arm-reviews-5000", "--label", "Study 2b (further attributes), the change in the name gap with reviews-5000 added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=reviews-5000 against none"],
    ["--study", "study2b-attr-arm-sustainability", "--label", "Study 2b (further attributes), the change in the name gap with sustainability added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=sustainability against none"],
    ["--study", "study2b-attr-arm-warranty-row", "--label", "Study 2b (further attributes), the change in the name gap with warranty-row added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=warranty-row against none"],
    ["--study", "study2b-attr-arm-warranty-sentence", "--label", "Study 2b (further attributes), the change in the name gap with warranty-sentence added, against none", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=warranty-sentence against none"],
    ["--study", "study2b-attr-gap-none", "--label", "Study 2b (further attributes), the name gap with no information", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=gap, none"],
    ["--study", "study2b-attr-row-failure", "--label", "Study 2b (further attributes), the change in the name gap with failure as a row of the table against as a sentence of the request", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=failure: row against sentence"],
    ["--study", "study2b-attr-row-lab", "--label", "Study 2b (further attributes), the change in the name gap with lab as a row of the table against as a sentence of the request", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=lab: row against sentence"],
    ["--study", "study2b-attr-row-market", "--label", "Study 2b (further attributes), the change in the name gap with market as a row of the table against as a sentence of the request", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=market: row against sentence"],
    ["--study", "study2b-attr-row-returns", "--label", "Study 2b (further attributes), the change in the name gap with returns as a row of the table against as a sentence of the request", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=returns: row against sentence"],
    ["--study", "study2b-attr-row-warranty", "--label", "Study 2b (further attributes), the change in the name gap with warranty as a row of the table against as a sentence of the request", "--input", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "0", "--units", "points", "--scale", "100.0", "--filter", "study=attr1", "--filter", "estimate_name=warranty: row against sentence"],
    ["--study", "study2b-failure-minus-all-five", "--label", "Study 2b, failure alone minus all five", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=failure alone minus all five"],
    ["--study", "study2b-failure-minus-none", "--label", "Study 2b, failure alone minus none", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=failure alone minus none"],
    ["--study", "study2b-lab-minus-all-five", "--label", "Study 2b, lab alone minus all five", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=lab alone minus all five"],
    ["--study", "study2b-market-minus-all-five", "--label", "Study 2b, market alone minus all five", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=market alone minus all five"],
    ["--study", "study2b-market-minus-none", "--label", "Study 2b, market alone minus none", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=market alone minus none"],
    ["--study", "study2b-returns-minus-all-five", "--label", "Study 2b, returns alone minus all five", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=returns alone minus all five"],
    ["--study", "study2b-returns-minus-none", "--label", "Study 2b, returns alone minus none", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=returns alone minus none"],
    ["--study", "study2b-warranty-minus-all-five", "--label", "Study 2b, warranty alone minus all five", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=warranty alone minus all five"],
    ["--study", "study2b-warranty-minus-none", "--label", "Study 2b, warranty alone minus none", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--model-col", "model", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--units", "points", "--scale", "100.0", "--filter", "study=2b", "--filter", "estimate_name=warranty alone minus none"],
]
HET_AUDIT = [   # the other heterogeneity runs that the Web Appendix's spread tables read, each with the arguments
               # recorded in its results file
    ["--study", "study2d-h6b-recall", "--label", "Study 2d, the slope of consideration on recall (H6b)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "1", "--units", "consideration share per standard deviation of recall within the model", "--scale", "1.0", "--filter", "test=h6b", "--filter", "component=recall", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-credibility", "--label", "Study 2d, the slope of the own-name gap on credibility (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "1", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=credibility", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-quality", "--label", "Study 2d, the slope of the own-name gap on quality (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "1", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=quality", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-recognition", "--label", "Study 2d, the slope of the own-name gap on recognition (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=recognition", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-salience", "--label", "Study 2d, the slope of the own-name gap on salience (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=salience", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-tone", "--label", "Study 2d, the slope of the own-name gap on tone (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=tone", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test1-typicality", "--label", "Study 2d, the slope of the own-name gap on typicality (test 1)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the component within the model", "--scale", "1.0", "--filter", "test=test1", "--filter", "component=typicality", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-credibility", "--label", "Study 2d, the slope of the gap on credibility for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "1", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=credibility", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-quality", "--label", "Study 2d, the slope of the gap on quality for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "1", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=quality", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-recognition", "--label", "Study 2d, the slope of the gap on recognition for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=recognition", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-salience", "--label", "Study 2d, the slope of the gap on salience for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=salience", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-tone", "--label", "Study 2d, the slope of the gap on tone for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=tone", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
    ["--study", "study2d-test2-typicality", "--label", "Study 2d, the slope of the gap on typicality for the same product under two names (test 2)", "--input", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/per-model-all.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "points of the gap per standard deviation of the difference in the component within the model", "--scale", "1.0", "--filter", "test=test2", "--filter", "component=typicality", "--reliability-col", "gap_reliability", "--reliability-col", "component_reliability", "--reliability-min", "0.5"],
]
HET_EXPL = [   # the other heterogeneity runs that the Web Appendix's spread tables read, each with the arguments
               # recorded in its results file
    ["--study", "study2e-gemma31b", "--label", "Study 2e, the share of a model's explanations that mention a brand (judge: Gemma 4 31B)", "--input", "study2a-experience-attributes-stated-for-every-product/results/explanations/per-model.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "per cent of the model's explanations", "--scale", "100.0", "--filter", "judge=gemma31b", "--filter", "test=b7-brand-share"],
    ["--study", "study2e-gptoss120b", "--label", "Study 2e, the share of a model's explanations that mention a brand (judge: gpt-oss 120B)", "--input", "study2a-experience-attributes-stated-for-every-product/results/explanations/per-model.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "per cent of the model's explanations", "--scale", "100.0", "--filter", "judge=gptoss120b", "--filter", "test=b7-brand-share"],
    ["--study", "study2e-olmo31-32b", "--label", "Study 2e, the share of a model's explanations that mention a brand (judge: OLMo 3.1 32B)", "--input", "study2a-experience-attributes-stated-for-every-product/results/explanations/per-model.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "per cent of the model's explanations", "--scale", "100.0", "--filter", "judge=olmo31-32b", "--filter", "test=b7-brand-share"],
    ["--study", "study2e-qwen35-122b-fp8", "--label", "Study 2e, the share of a model's explanations that mention a brand (judge: Qwen 3.5 122B FP8)", "--input", "study2a-experience-attributes-stated-for-every-product/results/explanations/per-model.csv", "--model-col", "model", "--est-col", "estimate", "--low-col", "lo95", "--high-col", "hi95", "--reason-col", "not_estimable", "--direction", "0", "--units", "per cent of the model's explanations", "--scale", "100.0", "--filter", "judge=qwen35-122b-fp8", "--filter", "test=b7-brand-share"],
]
# the four judges of the explanations (Study 2a, the reasons in the models' explanations): each one's codes
EXPL_JUDGES = [x for j in ("gemma31b", "gptoss120b", "olmo31-32b", "qwen35-122b-fp8")
               for x in ("--judge", f"{j}=study2a-experience-attributes-stated-for-every-product/data/explanations/judges/{j}-all-answers.jsonl.gz")]
# Study 2b's measure: its inputs, in the order of the final run's list of inputs, and its analysis's settings (the
# number of processes changes no value: each model is analysed alone with its own seeded draws)
MEASURE_OUT = "study2b-how-much-a-familiar-brand-is-worth/results/measure"
MEASURE_ITEMS = "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz"
MEASURE_GATES = "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/GATES.json"
MEASURE_API = "study2b-how-much-a-familiar-brand-is-worth/data/measure/api-answers.jsonl.gz"
MEASURE_OPEN = ["ernie45-21b", "gemma3-27b", "gemma31b", "gemma4-12b", "gemma4-26b", "glm47-flash", "gptoss120b",
                "gptoss20b", "granite41-30b", "granite42-30b", "kimi-linear48b", "llama3b", "llama8b", "marin8b",
                "ministral3-14b", "nemotron3-nano30b", "olmo3-7b", "olmo31-32b", "phi4", "qwen3-30b", "qwen3-32b", "qwen32b",
                "qwen35-0.8b", "qwen35-122b-fp8", "qwen35-27b", "qwen35-2b", "qwen35-35b", "qwen35-4b", "qwen35-9b",
                "qwen36-27b", "qwen38-27b", "qwen7b"]
MEASURE_ANSWERS = ",".join([MEASURE_API] + [f"study2b-how-much-a-familiar-brand-is-worth/data/measure/open/{m}.jsonl.gz" for m in MEASURE_OPEN])
MEASURE_MODELS = ",".join(["claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5", "gpt-6-astra",
                           "gpt-6.1-sol", "gpt-6.2-astra", "gpt-6.2-sol"] + sorted(MEASURE_OPEN))
MEASURE_ARGS = ["--items", MEASURE_ITEMS, "--gates", MEASURE_GATES, "--pretest", "study2b-how-much-a-familiar-brand-is-worth/materials/measure/pretest_numbers.json",
                "--recognition-items", "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1-recognition/items.jsonl", "--draws", "1000",
                "--splits", "200", "--workers", str(max(1, (__import__("os").cpu_count() or 2) - 2))]
# the open models' first answers and second letters, from the computing cluster's export; Kimi Linear 48B reported apart
SEARCH_OPEN = ["--stage1", "study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz", "--letters",
               "study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz", "--leave-out", "kimi-linear48b"]
# Study 2's counts: the answers in this package (count_git.py) and the open panel's counts from the computing cluster
STUDY2_COUNTS = ["--counts", "study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv", "--counts", "study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv"]

STUDIES = {
    "1": {
        "title": "Studies 1a to 1c, and the Web Appendix's analysis brand by brand and release by release",
        "steps": [
            ["common/analyze.py", "--set", "strictly-better-tables", "--thin", ROBUSTNESS_TABLES,
             "--without", "invented-real=" + INVENTED_NAME_IS_A_REAL_COMPANY,
             "--out", "study1a-tables-with-one-optimal-product/results/strictly-better-tables"],
            ["common/analyze.py", "--set", "original-tables", "--models", THREE_MODELS,
             "--dominant", DOMINANT_ORIGINAL_TABLES, "--out", "study1a-tables-with-one-optimal-product/results/original-tables-three-models"],
            ["common/analyze.py", "--set", "original-tables", "--dominant", DOMINANT_ORIGINAL_TABLES,
             "--out", "study1a-tables-with-one-optimal-product/results/original-tables-four-models"],
            ["study1b-64-models-on-34-tables/code/01_names_gap.py"],
            ["study1b-64-models-on-34-tables/code/02_names_gap_by_model.py"],
            ["study1b-64-models-on-34-tables/code/03_strict_dominance.py"],
            ["study1b-64-models-on-34-tables/code/04_names_hidden_leaks.py"],
            ["study1b-64-models-on-34-tables/code/05_recommended_price.py"],
            ["study1b-64-models-on-34-tables/code/06_long_answers.py"],
            ["study1b-64-models-on-34-tables/code/07_model_settings.py"],
            ["study1b-64-models-on-34-tables/code/20_thinking_pairs.py"],   # the four pairs run with and without extended thinking
            ["study1b-64-models-on-34-tables/code/08_rerun.py"],
            # the texts that still identify a brand without its name, and what the rerun's cleaning changed
            ["study1b-64-models-on-34-tables/code/names_hidden_left.py"],
            ["study1b-64-models-on-34-tables/code/cleaning_changes.py"],
            ["study1a-tables-with-one-optimal-product/code/09_open_model_counts.py"],
            ["study1a-tables-with-one-optimal-product/code/10_open_models.py"],
            ["study1a-tables-with-one-optimal-product/code/11_open_models_robustness.py"],
            ["web-appendix-analyses/brand-by-brand-and-release-by-release/code/12_brand_level.py"],
            ["web-appendix-analyses/brand-by-brand-and-release-by-release/code/13_brand_releases.py"],
            ["study1b-64-models-on-34-tables/code/14_requests.py"],
            ["study1b-64-models-on-34-tables/code/15_requests_robustness.py"],
            # the typed requests over every model that answered them, the declines and the per-model file
            ["study1b-64-models-on-34-tables/code/14_requests.py", "--all-models", "--leave-out", "kimi-linear48b"],
            ["study1b-64-models-on-34-tables/code/17_requests_declines_and_per_model.py"],
            ["study1b-64-models-on-34-tables/code/18_clarifying.py"],   # the clarifying turn (the Web Appendix)
            ["study1b-64-models-on-34-tables/code/19_priorities.py"],   # the stated priorities (the Web Appendix)
            ["study1b-64-models-on-34-tables/code/16_pooled.py"],
            # Study 1c, the store: the Claude panel, the open models, every model pooled, then the decline counts
            ["study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py", "--build", "h2", "--panel", "claude", "--out", STORE + "/claude"],
            ["study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py", "--build", "h2", "--panel", "open", "--also-build", "h1", "--letters",
             "study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz", "--leave-out", "kimi-linear48b", "--out", STORE + "/open-all"],
            ["study1c-product-feeds-and-a-store-search/code/store/analyze_harness.py", "--build", "h2", "--panel", "all", "--cells", STORE + "/claude/cells.csv",
             "--cells", STORE + "/open-all/cells.csv", "--leave-out", "kimi-linear48b", "--out", STORE + "/all-models"],
            ["common/write_declines.py", "--study", "b16", "--kind", "study1c-product-feeds-and-a-store-search/data/store/open-letters-kind.csv.gz",
             "--items", "study1c-product-feeds-and-a-store-search/materials/store/h1/prompts.jsonl.gz", "--items", "study1c-product-feeds-and-a-store-search/materials/store/h2/prompts.jsonl.gz",
             "--local", "study1c-product-feeds-and-a-store-search/data/store/claude/*.jsonl.gz", "--numbers", STORE + "/claude/numbers.json",
             "--numbers", STORE + "/open-all/numbers.json", "--numbers", STORE + "/all-models/numbers.json"],
            # Study 1c, the search step: every prompt rebuilt and compared with the materials, the three panels, then
            # the decline counts
            ["study1c-product-feeds-and-a-store-search/code/search/rebuild_prompts.py"],
            ["study1c-product-feeds-and-a-store-search/code/search/analyze_search.py", "--build", "s1", "--panel", "claude", "--out", SEARCH + "/claude"],
            ["study1c-product-feeds-and-a-store-search/code/search/analyze_search.py", "--build", "s1", "--panel", "open"] + SEARCH_OPEN
            + ["--out", SEARCH + "/open-all"],
            ["study1c-product-feeds-and-a-store-search/code/search/analyze_search.py", "--build", "s1", "--panel", "all"] + SEARCH_OPEN
            + ["--out", SEARCH + "/all-models"],
            ["common/write_declines.py", "--study", "b17", "--kind", "study1c-product-feeds-and-a-store-search/data/store/open-letters-kind.csv.gz",
             "--items", "study1c-product-feeds-and-a-store-search/materials/search/s1/stage2/*.jsonl.gz", "--local", "study1c-product-feeds-and-a-store-search/data/search/stage2/*.jsonl.gz",
             "--numbers", SEARCH + "/claude/numbers.json", "--numbers", SEARCH + "/open-all/numbers.json",
             "--numbers", SEARCH + "/all-models/numbers.json"],
        ],
        "numbers": ["study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json",
                    "study1a-tables-with-one-optimal-product/results/original-tables-three-models/numbers.json",
                    "study1a-tables-with-one-optimal-product/results/original-tables-four-models/numbers.json",
                    "study1b-64-models-on-34-tables/results/numbers.json", "study1b-64-models-on-34-tables/results/rerun.json",
                    "study1b-64-models-on-34-tables/results/names_hidden_left.json", "study1b-64-models-on-34-tables/results/cleaning_changes.json",
                    "study1a-tables-with-one-optimal-product/results/open_models.json",
                    "study1a-tables-with-one-optimal-product/results/open_models_robustness.json", "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/numbers.json",
                    "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/releases.json", "study1b-64-models-on-34-tables/results/requests/numbers.json",
                    "study1b-64-models-on-34-tables/results/requests/all-models/numbers.json", "study1b-64-models-on-34-tables/results/requests/all-models/left_out.json",
                    "study1b-64-models-on-34-tables/results/clarifying/numbers.json", "study1b-64-models-on-34-tables/results/priorities/numbers.json",
                    "study1b-64-models-on-34-tables/results/requests/robustness.json", "study1b-64-models-on-34-tables/results/pooled/numbers.json",
                    STORE + "/claude/numbers.json", STORE + "/open-all/numbers.json", STORE + "/all-models/numbers.json",
                    SEARCH + "/prompts_check.json", SEARCH + "/claude/numbers.json", SEARCH + "/open-all/numbers.json",
                    SEARCH + "/all-models/numbers.json"],
    },
    "2": {
        "title": "Studies 2a and 2b over every model that answered, the Web Appendix's analysis of each piece of information alone, how the models differed, and Study 3b's questions about each brand",
        "steps": [
            ["study2a-experience-attributes-stated-for-every-product/code/check_counts.py"],
            ["study2a-experience-attributes-stated-for-every-product/code/pool_all.py"] + STUDY2_COUNTS + [
                "--store-cells", "study2a-experience-attributes-stated-for-every-product/data/store/claude-cells.csv", "--store-cells", "study2a-experience-attributes-stated-for-every-product/data/store/open-cells.csv",
                "--only", "2a,2b,store", "--out", "study2a-experience-attributes-stated-for-every-product/results/all-models"],
            ["study2a-experience-attributes-stated-for-every-product/code/pool_all.py"] + STUDY2_COUNTS + ["--only", "2c", "--out", "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1"],
            ["study2a-experience-attributes-stated-for-every-product/code/pool_all.py", "--counts", "study2a-experience-attributes-stated-for-every-product/data/counts/counts-git-attr1.csv", "--counts",
             "study2a-experience-attributes-stated-for-every-product/data/open-panel/attr-counts.csv", "--only", "attr", "--out", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1"],
            # Study 2a's second test, the retrieved reviews: the Claude panel, the open models (Kimi Linear 48B reported
            # apart), every model pooled, then the decline counts
            ["study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py", "--build", "r1", "--panel", "claude", "--out", RETRIEVAL + "/claude"],
            ["study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py", "--build", "r1", "--panel", "open", "--letters",
             "study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz", "--leave-out", "kimi-linear48b", "--out", RETRIEVAL + "/open-all"],
            ["study2a-experience-attributes-stated-for-every-product/code/retrieval/analyze_retrieval.py", "--build", "r1", "--panel", "all", "--cells",
             RETRIEVAL + "/claude/cells.csv", "--cells", RETRIEVAL + "/open-all/cells.csv", "--out", RETRIEVAL + "/all-models"],
            ["common/write_declines.py", "--study", "b10", "--kind", "study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz",
             "--items", "study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz", "--local", "study2a-experience-attributes-stated-for-every-product/data/retrieval/claude/*.jsonl.gz",
             "--numbers", RETRIEVAL + "/claude/numbers.json", "--numbers", RETRIEVAL + "/open-all/numbers.json",
             "--numbers", RETRIEVAL + "/all-models/numbers.json"],
            # how the models differ: the spread between models and its six moderators, for the eight tests that the
            # paper reports, each from that test's per-model file
            [HET] + ["--study", "study1b", "--label", "Study 1b, the brand gap (names shown minus hidden, share not picking the optimal product)", "--input", "study1b-64-models-on-34-tables/results/pooled/per_model.csv", "--est-col", "gap_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "1"],
            [HET] + ["--study", "study2a", "--label", "Study 2a, the change in the gap when the five pieces of information are supplied", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--scale", "100", "--filter", "study=2a", "--filter", "estimate_name=change when the information is supplied"],
            [HET] + ["--study", "study2b-lab-minus-none", "--label", "Study 2b, lab alone minus none", "--input", "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--scale", "100", "--filter", "study=2b", "--filter", "estimate_name=lab alone minus none"],
            [HET] + ["--study", "study2c", "--label", "Study 2c, the invented twin's share minus the familiar twin's at the same price, names shown (the name's cost)", "--input", "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/per_model.csv", "--est-col", "estimate", "--se-col", "se", "--low-col", "ci95_low", "--high-col", "ci95_high", "--direction", "-1", "--scale", "100", "--filter", "study=2c", "--filter", "estimate_name=invented minus familiar twin, names shown"],
            [HET] + ["--study", "study1c-search-primary2", "--label", "Study 1c (the model's own searches), the share that picked the optimal product, hidden minus shown names", "--input", "study1c-product-feeds-and-a-store-search/results/search/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "1", "--filter", "quantity=picked the best: hidden minus shown", "--filter", "level=primary 2"],
            [HET] + ["--study", "study1c-search-primary3", "--label", "Study 1c (the model's own searches), the same where the store returned the optimal product under both versions", "--input", "study1c-product-feeds-and-a-store-search/results/search/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "1", "--filter", "quantity=picked the best where fetched in both: hidden minus shown", "--filter", "level=primary 3"],
            [HET] + ["--study", "study1c-store-gap-plain", "--label", "Study 1c (the store's listing), the name gap in the plain listing", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "1", "--filter", "quantity=name gap g(arm)", "--filter", "level=plain"],
            [HET] + ["--study", "study1c-store-D-instruct-brand", "--label", "Study 1c (the store's listing), the change in the name gap in the arm instruct-brand, D", "--input", "study1c-product-feeds-and-a-store-search/results/store/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", "0", "--filter", "quantity=change D(arm) = g(arm) - g(plain)", "--filter", "level=instruct-brand"],
            *[[HET] + ["--study", f"study1c-store-D-{arm}", "--label",
                       f"Study 1c (the store's listing), the change in the name gap in the arm {arm}, D"]
              + STORE_D + ["--filter", f"level={arm}"]
              for arm in ("position-first", "position-middle", "position-last", "sponsored-best")],
            *[[HET] + ["--study", f"study1b-requests-{q}", "--label", label, "--input",
                       "study1b-64-models-on-34-tables/results/requests/all-models/per_model.csv", "--est-col", "estimate_pp", "--low-col",
                       "ci95_low_pp", "--high-col", "ci95_high_pp", "--reason-col", "not_estimable", "--direction", d,
                       "--filter", f"quantity={q}"]
              for q, d, label in (("penalty", "1", "Study 1b (typed requests), the name gap under chat-log requests"),
                                  ("premium", "0", "Study 1b (typed requests), the premium for a familiar name under "
                                                   "chat-log requests"))],
            [HET] + ["--study", "study2a-retrieval-gap-none", "--label", "Study 2a (review pages), the name gap with no evidence", "--input", RETRIEVAL + "/all-models/per_model.csv", "--est-col", "estimate_pp", "--se-col", "se_pp", "--low-col", "ci95_low_pp", "--high-col", "ci95_high_pp", "--direction", "1", "--filter", "quantity=name gap g(e)", "--filter", "level=none"],
            *[[HET] + a for a in HET_MORE],   # the other runs that the Web Appendix's spread tables read
            # what predicts machine-based brand equity, on Study 2b's measure over every model (the paper's final run)
            ["how-the-models-differed/code/predictors.py", "--run", "final1", "--equity", "b21"],
            # every model that answered, the two GPT Sol models each on the units it answered in full (--codex)
            ["study3b-brand-knowledge-and-training-text-in-released-models/code/audit/analyze_audit.py", "--panel", "all", "--codex", "--out", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit"],
            ["study3b-brand-knowledge-and-training-text-in-released-models/code/audit/per_model.py"],   # each model's own slopes, for the runs of HET_AUDIT
            *[[HET] + a for a in HET_AUDIT],
            # Study 2a, the reasons in the models' explanations: each judge's checks, the reference on the stated 200,
            # the shares under each judge, each model's share for how the models differed
            ["study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py", "--checks-only"] + EXPL_JUDGES,
            ["study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py", "--reference-only"],
            ["study2a-experience-attributes-stated-for-every-product/code/explanations/shares.py"] + EXPL_JUDGES,
            ["study2a-experience-attributes-stated-for-every-product/code/explanations/per_model.py"],
            *[[HET] + a for a in HET_EXPL],
            # the main estimates of Studies 1b to 2b without the three tables whose fictitious name is a real company
            # (it reads the results that this group and the Study 1 group write)
            ["study1a-tables-with-one-optimal-product/code/21_real_company_tables.py"],
        ],
        "numbers": ["study1a-tables-with-one-optimal-product/results/real-company-tables/numbers.json",
                    "study2a-experience-attributes-stated-for-every-product/results/counts_check.json", "study2a-experience-attributes-stated-for-every-product/results/all-models/numbers.json",
                    "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/numbers.json", "web-appendix-analyses/each-piece-of-information-alone/results/all-models-attr1/numbers.json",
                    RETRIEVAL + "/claude/numbers.json", RETRIEVAL + "/open-all/numbers.json",
                    RETRIEVAL + "/all-models/numbers.json", "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json",
                    "how-the-models-differed/results/predictors/numbers.json"]
                   + [f"how-the-models-differed/results/{r}/numbers.json" for r in HET_RUNS]
                   + [f"how-the-models-differed/results/{a[1]}/numbers.json" for a in HET_MORE + HET_AUDIT + HET_EXPL]
                   + [f"study2a-experience-attributes-stated-for-every-product/results/explanations/{f}" for f in ("CHECKS.json", "REFERENCE-200.json", "numbers.json")],
    },
    "2b": {
        "title": "Study 2b's measure: every model, each route alone, the stopping rules, the pretest and the design",
        "steps": [
            # every model that answered the full design: the stopping rules, the analysis, then the results files
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/stop_rules2.py", "--answers", MEASURE_ANSWERS, "--items", MEASURE_ITEMS, "--gates",
             MEASURE_GATES, "--out", MEASURE_OUT + "/full1-all/stop-rules.json"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/analyze_mbbe2.py"] + MEASURE_ARGS + ["--answers", MEASURE_ANSWERS, "--models",
             MEASURE_MODELS, "--out", MEASURE_OUT + "/full1-all/run"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/finish_full_run.py", "--folder", MEASURE_OUT + "/full1-all"],
            # each route alone (the Claude models through Anthropic's API; the GPT models through Codex)
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/analyze_mbbe2.py"] + MEASURE_ARGS + ["--answers", MEASURE_API, "--models",
             "claude-fable-5-1,claude-haiku-5-5,claude-opus-5-5,claude-sonnet-5-5", "--out", MEASURE_OUT + "/full1-claude-api"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/route_results.py", "--route", "claude"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/analyze_mbbe2.py"] + MEASURE_ARGS + ["--answers", MEASURE_API, "--models",
             "gpt-6.1-sol,gpt-6.2-sol", "--out", MEASURE_OUT + "/full1-codex"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/route_results.py", "--route", "codex"],
            # the stopping rules of the Claude and GPT cells, the pretest's summary, and the design's figures
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/stop_rules2.py", "--answers", MEASURE_API, "--items", MEASURE_ITEMS, "--gates",
             MEASURE_GATES, "--out", MEASURE_OUT + "/full1-stop-rules/api-and-codex-models.json"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/summarize_pilot.py", "--numbers", "study2b-how-much-a-familiar-brand-is-worth/materials/measure/pretest_numbers.json",
             "--items", "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/pilot1/items.jsonl", "--out", MEASURE_OUT + "/pilot1"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/measure_tables.py"],
            # each version of the measure against the main version, and the direct test's rivals and shares
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/measure_versions.py"],
            ["study2b-how-much-a-familiar-brand-is-worth/code/measure/direct_test_facts.py"],
        ],
        "numbers": [MEASURE_OUT + "/versions/numbers.json", MEASURE_OUT + "/direct-test/numbers.json",
                    MEASURE_OUT + "/full1-all/summary.json", MEASURE_OUT + "/full1-all/over_models.json",
                    MEASURE_OUT + "/full1-claude-api/summary.json", MEASURE_OUT + "/full1-codex/summary.json",
                    MEASURE_OUT + "/full1-stop-rules/api-and-codex-models.json", MEASURE_OUT + "/pilot1/summary.json",
                    MEASURE_OUT + "/full1-design/numbers.json"],
    },
    "3": {
        "title": "Study 3a (the planted pages, and the planted pages about the product brands), and Study 3b's "
                 "checkpoints and training stages",
        "steps": [["study3b-brand-knowledge-and-training-text-in-released-models/code/checkpoints.py"], ["study3a-pages-about-new-brands/code/planted_text.py"],
                  ["study3b-brand-knowledge-and-training-text-in-released-models/code/training_stages.py", "--scores", "study3b-brand-knowledge-and-training-text-in-released-models/data/training-stages/scores", "--models",
                   "study3b-brand-knowledge-and-training-text-in-released-models/materials/training-stages/models.tsv", "--out", "study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json"],
                  # question 2: each family's planted runs, the three 7B-to-8B families together, and the results file
                  # (each family's runs in their sets, in the order of the project's run: the bootstrap's draws
                  # depend on the order of the runs)
                  *[["study3a-pages-about-new-brands/code/training/analyze_q2.py", "--runs",
                     *[f"study3a-pages-about-new-brands/data/training-runs/{family}/set-{k}" for k in range(1, sets + 1)], "--stage",
                     "dpo-uf", "--format", "role3", "--out", f"study3a-pages-about-new-brands/results/training/parts/{part}.json"]
                    for family, part, sets in (("olmo2-7b", "q2", 3), ("qwen25-7b", "q2_qwen", 1),
                                               ("llama31-8b", "q2_llama", 2), ("olmo2-32b", "q2_32b", 2))],
                  ["study3a-pages-about-new-brands/code/training/q2_across.py", "--parts", "study3a-pages-about-new-brands/results/training/parts", "--out",
                   "study3a-pages-about-new-brands/results/training/parts/q2_across.json"],
                  # the first design's replication, each family's runs
                  *[["study3a-pages-about-new-brands/code/first-design-replication/analyze_replication.py", "--runs",
                     f"study3a-pages-about-new-brands/data/replication-runs/{family}", "--out", f"study3a-pages-about-new-brands/results/training/parts/{part}.json"]
                    for family, part in (("qwen25-7b", "oct_qwen"), ("olmo2-7b", "oct_olmo"), ("llama31-8b", "oct_llama"))],
                  # what differs between the two designs (the amount of text, the outcome without brand names)
                  ["study3a-pages-about-new-brands/code/training/design_compare.py", "--october",
                   *[f"study3a-pages-about-new-brands/data/replication-runs/qwen25-7b/qwen25-7b-{p}-s20261001"
                     for p in ("none", "neutralclean", "promo", "negative")],
                   "--q2", *[f"study3a-pages-about-new-brands/data/training-runs/{f}" for f in ("olmo2-7b", "qwen25-7b", "llama31-8b")],
                   "--out", "study3a-pages-about-new-brands/results/training/parts/design_compare.json"],
                  ["study3a-pages-about-new-brands/code/training/combine.py"],
                  # Study 3b: what OLMo 2's training text says around each brand, against the brands' equity
                  ["study3b-brand-knowledge-and-training-text-in-released-models/code/training-text/analyze_b5.py"],
                  # Holm's correction over the brand-level correlations and regressions (the Web Appendix), which
                  # reads Study 3b's training text and the brand-level results of Study 1's step
                  ["web-appendix-analyses/brand-by-brand-and-release-by-release/code/exposure_holm.py"]],
        "numbers": ["study3b-brand-knowledge-and-training-text-in-released-models/results/checkpoints.json", "study3a-pages-about-new-brands/results/numbers.json",
                    "study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json", "study3a-pages-about-new-brands/results/training/numbers.json",
                    "study3b-brand-knowledge-and-training-text-in-released-models/results/training-text/numbers.json", "web-appendix-analyses/brand-by-brand-and-release-by-release/results/brand_level/exposure-holm.json"],
    },
    "4": {
        "title": "Study 4 (the live chat), and Supplemental Studies S1 to S4",
        "steps": [["study4-peoples-choices-after-a-recommendation/code/analyze.py", "chat"], ["study4-peoples-choices-after-a-recommendation/code/analyze.py", "S1"],
                  ["study4-peoples-choices-after-a-recommendation/code/analyze.py", "S2"], ["study4-peoples-choices-after-a-recommendation/code/analyze.py", "S3"], ["s4-people-and-language-models-as-advisors/code/s4_advisors.py"],
                  ["study4-peoples-choices-after-a-recommendation/code/study4_empty_replies.py"]],   # the sessions whose recommendation came back empty
        "numbers": ["study4-peoples-choices-after-a-recommendation/results/numbers.json", "s4-people-and-language-models-as-advisors/results/numbers.json",
                    "study4-peoples-choices-after-a-recommendation/results/study4-empty-replies.json"],
    },
}

# Fields that describe how a value was produced rather than the value itself.
NOT_COMPARED = {"script", "input"}


def check_data(studies: list[str]) -> int:
    bad = 0
    for st in studies[:1]:   # every data folder of the package, once
        for listing in sorted(ROOT.rglob("FILES.csv")):
            rows = list(csv.DictReader(open(listing, encoding="utf-8")))
            for r in rows:
                p = listing.parent / r["file"]
                if not p.exists():
                    print(f"  missing: {p.relative_to(ROOT).as_posix()}")
                    bad += 1
                    continue
                # a text file passes with its exact bytes or with LF line endings, so that a copy checked out with CRLF
                # (Windows) passes, and so does a file that was written with CRLF endings
                raw = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
                if p.suffix != ".gz" and hashlib.sha256(raw).hexdigest() != r["sha256_uncompressed"]:
                    raw = raw.replace(b"\r\n", b"\n")
                if hashlib.sha256(raw).hexdigest() != r["sha256_uncompressed"]:
                    print(f"  SHA-256 differs: {p.relative_to(ROOT).as_posix()}")
                    bad += 1
                if r["rows"] == "":  # a file that is not a table (a settings file, a log)
                    continue
                if p.suffix == ".csv" or p.name.endswith(".csv.gz"):  # records, not lines: a text may hold a line break
                    n = sum(1 for _ in csv.reader(io.StringIO(raw.decode("utf-8")))) - 1
                else:
                    n = raw.count(b"\n")
                if n != int(r["rows"]):
                    print(f"  {p.relative_to(ROOT).as_posix()} holds {n} rows, not {r['rows']}")
                    bad += 1
            print(f"  {listing.relative_to(ROOT).as_posix()}: {len(rows)} files checked")
    return bad


def differences(new, old, path=""):
    """Every place where two JSON values differ, skipping the fields in NOT_COMPARED."""
    out = []
    if isinstance(new, dict) and isinstance(old, dict):
        for k in sorted(set(new) | set(old)):
            if k in NOT_COMPARED:
                continue
            if k not in new or k not in old:
                out.append((f"{path}/{k}", new.get(k, "(absent)"), old.get(k, "(absent)")))
            else:
                out += differences(new[k], old[k], f"{path}/{k}")
    elif isinstance(new, list) and isinstance(old, list) and len(new) == len(old):
        for i, (a, b) in enumerate(zip(new, old)):
            out += differences(a, b, f"{path}/{i}")
    elif new != old and not (isinstance(new, float) and isinstance(old, float) and new != new and old != old) \
            and not _same_float(new, old):
        out.append((path, new, old))  # (two NaN values, a statistic that cannot be computed, count as equal)
    return out


def _same_float(a, b) -> bool:
    """Two floats that differ only in the last digits, as the same sums in another order or on another processor give
    (Study 2d's results are written unrounded): equal within a relative 1e-9."""
    return (isinstance(a, float) and isinstance(b, (int, float)) and not isinstance(b, bool)
            and abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b)))


def keep_released(numbers: pathlib.Path, released) -> None:
    if released is not None:
        (numbers.parent / f"{numbers.stem}_released.json").write_text(
            json.dumps(released, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def run_study(st: str) -> int:
    spec = STUDIES[st]
    print(f"\n{spec['title']}")
    files = [ROOT / n for n in spec["numbers"]]
    released = {}
    for numbers in files:
        released[numbers] = json.loads(numbers.read_text(encoding="utf-8")) if numbers.exists() else None
        if numbers.exists():
            numbers.unlink()
    for step in spec["steps"]:
        t0 = time.time()
        r = subprocess.run([sys.executable, str(ROOT / step[0])] + step[1:], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        label = " ".join([step[0]] + [s for s in step[1:] if len(s) < 60])   # the script, and its short arguments
        if r.returncode != 0:
            print(f"  {label} stopped with status {r.returncode}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
            for numbers in files:
                keep_released(numbers, released[numbers])
            return 1
        print(f"  {label}: {time.time() - t0:.0f} s")
    status = 0
    for numbers in files:
        rel = numbers.relative_to(ROOT).as_posix()
        if released[numbers] is None:
            print(f"  {rel}: no released file to compare with; the new one is written")
            continue
        diff = differences(json.loads(numbers.read_text(encoding="utf-8")), released[numbers])
        if diff:
            keep_released(numbers, released[numbers])
            print(f"  {len(diff)} values differ from the released {rel}:")
            for k, a, b in diff[:50]:
                print(f"    {k}: new {a!r}, released {b!r}")
            status = 1
        else:
            print(f"  every value equals the released {rel}")
    return status


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # answers hold text in many scripts
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", choices=sorted(STUDIES))
    ap.add_argument("--check-data", action="store_true")
    a = ap.parse_args()
    studies = [a.study] if a.study else sorted(STUDIES)
    print("Step 1: the data files")
    bad = check_data(studies)
    if bad:
        print(f"{bad} problems in the data files; stopping")
        return 1
    if a.check_data:
        return 0
    status = 0
    for st in studies:
        status |= run_study(st)
    print("\nAll results reproduced." if status == 0 else "\nSome results differ; see above.")
    return status


if __name__ == "__main__":
    sys.exit(main())
