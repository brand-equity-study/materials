# Study 2a: Experience Attributes Stated for Every Product

In Study 2a, we tested whether stating every product's experience attributes reduces the effect of a fictitious name.
This folder also has the estimates over every model for Studies 1a, 2a and 2b.

## The two tests

**Experience attributes.** For every product of Study 1a's tables, we listed the same three experience attributes: a
two-year warranty, a first-year failure or return rate of 2 percent, and ten or more years on the market. The request
said that every figure comes from independent testing and that returns are free. The Claude models' prompts and
responses are in Study 1a's folder.

**Review pages.** Under every product, we placed the same review-site rating and three customer reviews of one tone:
positive, mixed or negative.

The analysis plans are `materials/analysis_plan.md` and `materials/retrieval/analysis_plan.md`.

## Estimates over every model

The Claude models answered through Anthropic's Messages API, the GPT-6 models through OpenAI's Codex command line, and
the models with open weights on a university computing cluster (`models/open-models.tsv`). `code/pool_all.py` pools the
estimates, with every table and every model counted equally and a bootstrap over tables and models.

| Script | What it does | Writes (in `results/`) |
|---|---|---|
| `code/check_counts.py` | checks the count of every answer in the package | `counts_check.json` |
| `code/pool_all.py ... --only 2a,2b,store` | Studies 1a and 2a over every model | `all-models/` |
| `code/retrieval/analyze_retrieval.py --panel claude`, `open`, `all` | the effect at each tone of the review pages | `retrieval/claude/`, `open-all/`, `all-models/` |

`code/pool_all.py ... --only 2c` writes Study 2b's estimates, and `--only attr` writes those of the further information
in `web-appendix-analyses/each-piece-of-information-alone/`.

## Reasons in the models' explanations

Four models with open weights coded whether each of 29,600 explanations names a brand as a reason. Each coder had to
agree with a reference coding of 200 explanations (Cohen's kappa of at least 0.70). The plan is
`materials/explanations/analysis_plan.md`.

| Script | What it does | Writes (in `results/explanations/`) |
|---|---|---|
| `code/explanations/shares.py --checks-only` | each coder's checks | `CHECKS.json` |
| `code/explanations/shares.py --reference-only` | the reference coding of the 200 | `REFERENCE-200.json` |
| `code/explanations/shares.py` | the share of explanations that name a brand, under each coder | `numbers.json` |
| `code/explanations/per_model.py` | each model's share under each coder | `per-model.csv` |

## Files

| Folder or file | Contents |
|---|---|
| `data/strictly-better-tables/<model>/<cell>.jsonl.gz` | the GPT-6 models' and Claude Fable 5.2's responses to Study 1a's prompts |
| `data/counts/counts-git.csv` | the count of responses and choices for every model, table and condition |
| `data/open-panel/b9-counts.csv`, `attr-counts.csv` | the same counts for the open models |
| `data/open-panel/letters-12683.csv.gz`, `letters-13394.csv.gz`, `letters-12154.csv.gz` | the open models' answers |
| `data/open-panel/versions/` | each open model's run record |
| `data/store/claude-cells.csv`, `open-cells.csv` | Study 1c's conditions with the experience attributes |
| `materials/retrieval/r1/prompts.jsonl.gz` | the 2,880 prompts with review pages |
| `materials/explanations/analysis_plan.md`, `materials/explanations/admission/` | the coding plan, and the coders' instructions and checks |
| `data/explanations/items-all.jsonl.gz`, `items-sample.jsonl` | the 29,600 explanations and the sample of 200 |
| `data/explanations/reference/<id>.md` | the reference coding |
| `data/explanations/judges/` | each coder's codes |
| `data/retrieval/claude/<model>.jsonl.gz`, `open-letters.csv.gz` | the responses with review pages |
| `data/open-models/retrieval/` | the open models' full responses with review pages, with `RUNS.csv` |

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/effect-by-model.csv` | Study 2a's estimates for each model |
