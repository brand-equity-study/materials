# Study 1a: Tables With One Optimal Product

In Study 1a, we tested whether a fictitious name on the optimal product lowers how often language models recommend it.

## Design

Each table has one optimal product: it is at least as good as every other product on every attribute. Each table was
shown in 12 versions:

- names: no brand names (Product A to E), the fictitious name on the optimal product, or the names swapped;
- experience attributes (failure rate, warranty and time on the market): stated for every product or not;
- price: the optimal product at the cheapest other product's price or 30 percent below it.

The versions with and without the experience attributes are the test of Study 2a.

## Data

| Set of tables | Prompts | Responses of the four Claude models |
|---|---|---|
| `strictly-better-tables` | 30 tables x 12 versions x 10 trials = 3,600 | 14,400 |
| `original-tables` | 34 tables x 18 versions x 10 trials = 6,120 | 24,480 |

The four Claude models answered through Anthropic's Messages API, and ten models with open weights answered on a
university computing cluster. The GPT-6 models' and Claude Fable 5.2's responses are in
`study2a-experience-attributes-stated-for-every-product/data/strictly-better-tables/`.

## Analysis

`common/parse_answer.py` reads which product each response recommended, and `common/analyze.py` estimates the effect of
the fictitious name and its change when the experience attributes are stated. The estimates over every model that
answered are in `study2a-experience-attributes-stated-for-every-product/results/all-models/`.

Three of the fictitious names are also names of small real companies: Novatech (laptops 2), Primebook (laptops 3) and
Sonance (earbuds 2). `code/21_real_company_tables.py` computes every main estimate again without their tables.

## Files

| Folder or file | Contents |
|---|---|
| `materials/<set>/prompts.jsonl.gz` | every prompt as the model received it |
| `materials/strictly-better-tables/DOMINANT-SETS.md` | every change made so that the optimal product is at least as good as every other product |
| `data/<set>/<model>/<cell>.jsonl.gz` | the four Claude models' responses, one file per version of a table |
| `data/open-models/<set>/<model>/<cell>.jsonl.gz` | the ten open models' responses; `RUNS.csv` gives each model's settings |
| `code/09_open_model_counts.py`, `10_open_models.py`, `11_open_models_robustness.py` | the analysis of the open models |
| `results/strictly-better-tables/`, `original-tables-three-models/`, `original-tables-four-models/` | the results for each set of tables |
| `results/open_models.json`, `open_models_counts.csv`, `open_models_robustness.json` | the open models' results |
| `code/21_real_company_tables.py`, `results/real-company-tables/numbers.json` | every main estimate without the three tables named after real companies |

The code that made every prompt is in `common/tables/` (see `common/README.md`).

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/models-and-responses.csv` | the models of Study 1a and the number of their responses |
| `results/tables/estimates-without-real-company-tables.csv` | each study's main estimates without the three tables whose fictitious names match real companies |
