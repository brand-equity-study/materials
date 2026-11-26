# Inside the model: how two open models represent a familiar name

This folder contains the files of the study in the Web Appendix section called "Inside the Model". We
record the internal states of two models with open weights, Gemma 4 31B and Gemma 4 26B A4B, while they choose among
the products of Study 1a. We test in ten ways how a familiar name changes those states and the models'
recommendations. We first describe the design, then the data, then the code, then how each number is computed, and last
the files.

## Design

We use the following two models: Gemma 4 31B (unsloth/gemma-4-31b-it, revision
51c9f6265ea38755c708a6e356dfc1af4a436e35; 60 layers) and Gemma 4 26B A4B (google/gemma-4-26B-A4B-it, revision
4d7ae4984b7db7de8f8457170b3f1a419ee76d52; 30 layers, 8 of 128 experts for each token). Each model was run with its own
chat template (the 26B with thinking switched off) in bf16, using transformers 5.20.2 and torch 2.14 on one H100 GPU.
The edited versions of the models in the test of the weights were run with vLLM 0.33.0. For the test of alignment, we
also read eight other open models, which are named in data/returned/ten-models/.

We use the 3,600 prompts of Study 1a's tables (without brand names, with the fictitious name on the optimal product and
with the names swapped; without and with the quality information of Study 2a; at both prices; ten orders of the
products). We also use two kinds of prompts without brand names to define better listed quality: 1,200 in which the
specifications of two products are exchanged, and 1,200 in which one product lists a poor warranty and failure rate.
Three further sets are used in single tests: prompts that rename each brand or place it on the optimal product (the
test brand by brand), questions without products under a cautious and a bold advisor (the test of caution), and Study
1b's tables, the consumers' requests and 500 general-knowledge questions (the test of the weights).

The ten tests are the following, in the order of the Web Appendix:
1. Does a familiar name move a product along the direction of better listed specifications or reliability?
2. When we add the change that a familiar name causes, does the optimal product rise, both ways, more than when we add
   random changes?
3. Is that change smaller when every product lists the quality information?
4. Does the recommendation follow the name's own state when that state is copied into the other name's tokens?
5. Is the order of the brands on measures of a brand's state the same as their order in the model's own
   recommendations?
6. Is the effect removed when we erase the linear difference between a familiar and a fictitious name?
7. Is the effect removed when we take the name direction out of the weights?
8. Across ten open models, is the name's alignment with better listed reliability correlated with the models' response
   to the quality information?
9. Does the recommendation change when we block the response's attention to the names?
10. When we push the model along a direction of caution that is made from questions without products, does the amount
    by which it favors familiar names change?

## Data

The folder data/returned/ contains, for each model and each stage, the files that the GPU runs returned: the log-odds
and the probabilities of the optimal product for every prompt and every change, the projections of every pair of
prompts on the fitted directions at 15 layers (proj.npz), the fitted directions' summaries, and the responses of the
edited versions of the models. The internal states themselves (the mean state of each part of each product's block at
15 layers, in float16, about 252 GB for the two models) are not included because of their size. The script
code/run_mech.py computes them again from the prompts. The folder data/prompts/ contains every prompt of the study. The
folder data/inputs/ contains three results files of other studies that are used in the analysis: the brands' frequency
in public text and their equity from the Web Appendix's analysis brand by brand and release by release
(`web-appendix-analyses/brand-by-brand-and-release-by-release/`), and the ten open models' change with the quality
information from Study 2a.

## Code

The scripts run in this order. `build.py`, `build_brands.py`, `build_risk.py` and `weights_items.py` made the prompts in
`data/prompts/` from the code that wrote the prompts of Study 1a and Study 2a. That code is in those studies' folders.
`run_mech.py` reads the states, exchanges the states after the names (we use this exchange to choose each model's
primary layer), pushes along the name's change and copies the names' states (tests 1 to 4). `run_brands.py`,
`run_erase.py` with `erase.py`, `run_knock.py`, `run_weights.py` with `weights_edit.py` and `vllm_items.py`, and
`run_risk.py` with `risk_sep.py` and `risk_separation.py` run tests 5, 6, 9, 7 and 10. `mech.py` contains the functions
that the run scripts share: loading a model, finding the tokens of each part of a block, and adding, exchanging or
blocking states with forward hooks. `analyze.py` and `brand_criterion.py` compute every number from `data/`.
`parse_answer.py` is the script from Study 2 that reads the letter in a response.

## Analysis

`python code/rerun.py` runs analyze.py on data/ and writes numbers.json to results-rerun/ in about six minutes. It
needs only numpy. The file it writes is identical to results/numbers.json, because every interval (2,000 bootstrap
samples of the 30 tables) and every p-value (10,000 sign flips or permutations) is computed with the seed 20261120.
In results/numbers.json, each model's tests are saved under models/<model>/q1 to q10, and the tests over models are
saved under q5 and q8. Each test's sentence for the paper is saved beside it. A test whose criteria could not be
checked is recorded as such. The 31B's test of the weights is recorded with "read": false, because every edited version
of the 31B gave a recommendation in at most 38.2% of its responses.

## Files

- README.md: this file.
- SHA256SUMS: the SHA-256 of every other file.
- code/: the scripts named above, and rerun.py.
- data/returned/gemma31b/ and data/returned/gemma4-26b/: read (the probabilities at no change, against Study 2a's
  shares), full (the exchange, the pushes and the copies), brands, erase, knock, weights (with each edit's responses
  in answers/) and caution, one folder for each stage.
- data/returned/ten-models/: the read of the eight other models for the test of alignment.
- data/prompts/: pairs.jsonl and renderings.jsonl (the 6,000 prompts and their pairs), brands.jsonl and
  brand_pairs.jsonl (the test brand by brand), caution_questions.jsonl, weights_study1b.jsonl, weights_study1a.jsonl
  and weights_requests.jsonl (the test of the weights), calibration_shares.json (Study 2a's shares for the check at no
  change).
- data/inputs/: brand_equity.csv, brand_model_equity.csv, open_models_numbers.json.
- results/numbers.json: every number that is reported in the Web Appendix section.
