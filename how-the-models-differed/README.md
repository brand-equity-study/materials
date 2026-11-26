# How the Models Differed

This folder has the analysis of how much the models differed in each test, and of which features of a model predict
its estimate.

## Method

For each test, `code/heterogeneity.py` reads each model's estimate and fits a random-effects model over the models. It
then tests six features of a model one at a time, with Holm's correction: chat-tuned against base, size, release date,
open against closed weights, reasoning on against off, and developer. The features are in
`models/model_characteristics.csv`, and the plan is `materials/analysis_plan.md`. `code/heterogeneity.py --selftest`
checks the code on simulated models.

`code/predictors.py --run final1 --equity b21` relates each model's effect, and each brand's equity in Study 2b's
measure, to the features of the model and of the brand (`materials/predictors_plan.md`,
`materials/brand_characteristics.csv`). It writes `results/predictors/numbers.json` and `model_gaps.csv`.

## Runs

`run_all.py` runs `code/heterogeneity.py` once for each of fifteen tests of the paper, from each study's per-model
results file. Each run writes `results/<test>/numbers.json`, and `results/SUMMARY.md` sets the runs side by side.

| File | Contents |
|---|---|

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/variation-of-each-estimate-between-models.csv` | how much each estimate of the paper varied between models |
| `results/tables/model-features-and-each-estimate.csv` | approximate tests of whether a model's features predict each estimate |
