# Brand by Brand and Release by Release

This folder contains the materials, data and code used in the Web Appendix's analysis of each familiar brand's
machine-based equity in each model and of how much that equity changes from one release of a model to the next. The
analysis is reported in one sentence of the main text, with Study 1. We first describe the measures, then the analysis,
and last the files.

## The measures

A brand's machine-based equity in a model is how much more often the model recommends the brand's product with
brand names than without them. It is computed from the responses of Study 1b (the corpus, the current models and the
open models on the corpus's prompts). Each brand's equity is compared with the brand's frequency in public text, its
Wikipedia page views, its coded familiarity, people's familiarity with it in Study 4, and its published brand value.

## The analysis

| Script | What it does | Writes (in `results/brand_level/`) |
|---|---|---|
| `code/12_brand_level.py` | each brand's equity in the corpus, the four current models and the open models, and its relation to the measures above | `numbers.json`, `brand_model_equity.csv`, `brand_equity.csv` |
| `code/13_brand_releases.py` | how much a new release of a developer's model changes each brand's equity, against the change that sampling alone gives | `releases.json`, `brand_release_changes.csv` |
| `code/exposure_holm.py` | Holm's correction over the correlations of a brand's equity with the measures of its exposure, over the regressions on its standing, and the promotional share of OLMo 2's training text (from Study 3b's `results/training-text/numbers.json`); no number is estimated again | `exposure-holm.json` |

## The files

| File | Contents |
|---|---|
| `materials/brand_frequency.csv` | each brand's count in four public text collections used to train language models: C4, the Pile, RedPajama and Dolma |
| `materials/brand_wikipedia_pageviews.csv` | each brand's Wikipedia page views over 12 months |
| `materials/brand_value_rankings.csv` | whether and where each brand appears in the Interbrand and Kantar BrandZ rankings of 2024 and 2025 |
| `materials/brand_value_sources.md` | each source and the date on which it was consulted |

The responses that the scripts use are stored in Study 1b's folder (`study1b-64-models-on-34-tables/`) and in
Study 1a's folder (`study1a-tables-with-one-optimal-product/data/open-models/rerun/`). The familiarity ratings are stored in
Study 4's folder (`study4-peoples-choices-after-a-recommendation/`).

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/regressions-of-brand-equity.csv` | regressions of a brand's equity in each of the 30 models on measures of the brand's standing |
| `results/tables/equity-across-releases.csv` | machine-based equity across releases of one developer's models |
