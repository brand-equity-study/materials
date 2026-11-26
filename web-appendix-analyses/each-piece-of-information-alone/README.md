# Each Piece of Information Alone

This folder contains the materials, data and code used in the Web Appendix's analysis of which of the experience
attributes and statements of Study 2a attenuates the effect of a fictitious name when it is stated alone, and of further
information given in other forms. The analysis is reported in one sentence of the main text, with Study 2. We first
describe the design, then the analysis, and last the files.

## Design

The models saw the 30 strictly better tables, with the optimal product at the price of the cheapest other product.
Each table was shown with no information, with each of five pieces alone (the warranty, the first-year failure or
return rate, the time on the market, the sentence that every figure comes from independent testing, and the free
return) or with all five. Each table was shown in every one of these conditions, under the three versions of the
names, in 10 trials (6,300 prompts for each model). Besides the condition with no information, the further information was given in 16
conditions: each of the five pieces as a row in every product block or as a sentence in the request, the optimal
product's review count at 50 or 5,000, and four further rows (a certification, an expert endorsement, a country of
origin and a sustainability claim). Each table was shown in every condition without brand names and with the original
names, in 10 trials (11,400 prompts for each model). The conditions with further information are described in
`study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md`.

## The analysis

Study 2a's `pool_all.py` (`study2a-experience-attributes-stated-for-every-product/code/`) computes the estimates over
every model, with `--only 2a,2b,store` for each piece alone (saved in
`study2a-experience-attributes-stated-for-every-product/results/all-models/`) and `--only attr` for the further
information (saved in `results/all-models-attr1/`). `code/analyze_attr.py` and `code/attr_conditions.py` contain the
conditions and estimates of the further information, which are used by `pool_all.py`.

## The files

| Folder or file | Contents |
|---|---|
| `materials/each-piece-alone/prompts.jsonl.gz`, `materials/further-information/prompts.jsonl.gz` | the prompts |
| `data/each-piece-alone/<model>/<cell>.jsonl.gz` | 25,200 responses of the four Claude models |
| `data/further-information/<model>/<cell>.jsonl.gz` | 34,200 responses of Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 (Claude Fable 5.1 did not answer it) |
| `results/all-models-attr1/` | the further information over every model: each condition's effect of the fictitious name, the three families with Holm's correction, each developer group and the differences between groups |

The open models' responses to these prompts are used in the analyses as counts
(`study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv` and `attr-counts.csv`). Their
full responses are stored in `data/open-models/each-piece-alone/` and `data/open-models/further-information/`, one file
for each model and condition, with each set's `RUNS.csv`.

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/each-piece-alone-by-model.csv` | the test of each piece of information alone, for each model |
| `results/tables/further-information-by-model.csv` | the estimates with further information, for each model |
| `results/tables/further-information-variation-between-models.csv` | how much the effect and each condition's change with further information varied between models |
