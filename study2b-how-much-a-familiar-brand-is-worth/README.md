# Study 2b: How Much a Familiar Brand Is Worth

In Study 2b, we measured what a familiar brand is worth to the models, in two designs.

## First design: identical products

We gave a familiar product the optimal product's specifications and placed a product with a fictitious name beside it,
at the same price, at discounts of up to 50 percent, or with a higher star rating. Each prompt was run 8 times with and
without brand names (10,560 prompts per model).

| Script | What it does | Writes (in `results/`) |
|---|---|---|
| `code/analyze_eq.py` | each product's share at each price and rating, and the discount at which the two are chosen equally often | used by `pool_all.py` |
| `study2a-experience-attributes-stated-for-every-product/code/pool_all.py ... --only 2c` | the estimates over every model | `all-models-eq1/` |

## Second design: a measure for each brand

In each prompt, a model saw five products of one category, each with a brand name, three attributes, a star rating and
a price, and recommended one. A brand's equity is its name's coefficient in a conditional logit model, minus the mean
coefficient of the category's fictitious names. We report it as a share premium, a price premium and a rating
equivalent. The plans are `materials/price/measure_plan.md` and, for the pretest, `materials/price/measure_pilot_plan.md`.

The Claude models answered through Anthropic's API, the GPT Sol models through OpenAI's Codex command line, and 32
models with open weights on a university computing cluster. This analysis is the longest step of `run_all.py`.

| Script | What it does | Writes (in `results/measure/`) |
|---|---|---|
| `code/measure/stop_rules2.py` | the checks of each model and category | `full1-all/stop-rules.json`, `full1-stop-rules/` |
| `code/measure/analyze_mbbe2.py` | each model's equity for every brand | `full1-all/run/`, `full1-claude-api/`, `full1-codex/` |
| `code/measure/finish_full_run.py`, `measure_all_results.py` | the results over every model | `full1-all/` |
| `code/measure/route_results.py` | the summaries of the Claude and GPT models | `full1-claude-api/summary.json`, `full1-codex/summary.json` |
| `code/measure/summarize_pilot.py` | the pretest's summary | `pilot1/` |
| `code/measure/measure_tables.py` | the design's figures and the Web Appendix's tables | `full1-design/numbers.json`, `exhibits/results/measure_tables.md` |
| `code/measure/measure_versions.py` | each alternative version against the main version | `versions/numbers.json`, `versions/pairs.csv` |
| `code/measure/direct_test_facts.py` | the direct test | `direct-test/numbers.json` |

## Files

| Folder or file | Contents |
|---|---|
| `materials/price/prompts.jsonl.gz` | the first design's prompts |
| `data/price/<model>/<cell>.jsonl.gz` | the four Claude models' 42,240 responses to the first design |
| `data/open-models/price/` | the open models' full responses to the first design, with `RUNS.csv` |
| `materials/measure/` | the second design's prompts, their checks (`GATES.json`) and checksums (`SHA256SUMS`) |
| `data/measure/` | every response to the second design, with the open models' run records |
| `materials/price/measure_pilot_plan.md`, `materials/price/measure_plan.md` | the analysis plans |
| `results/all-models-eq1/` | the first design's estimates over every model |

The analyses use the open models' first-design responses as counts

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/price-effect-by-model.csv` | Study 2b's choice between the familiar product and the fictitious product at each price, for each model |
| `results/tables/pretest-premium-by-brand.csv` | the measure's pretest: each brand's premium |
| `results/tables/categories-brands-and-prices.csv` | the measure's categories, with each familiar brand's band of prices, the fictitious names and the prices shown |
| `results/tables/attributes-and-levels.csv` | the measure's attributes in each category and their levels |
| `results/tables/shoppers-requests.csv` | the shopper's request in each category, in its main version and its three other versions |
| `results/tables/share-premium-by-brand-claude-and-gpt-models.csv` | each brand's share premium in each Claude and GPT model |
| `results/tables/rating-equivalent-by-brand-claude-and-gpt-models.csv` | each brand's rating equivalent in each Claude and GPT model |
| `results/tables/reliability-by-model-and-category.csv` | the reliability of the measure in each Claude and GPT model and category |
| `results/tables/share-premium-by-brand-over-models.csv` | each brand's share premium over every model and within each group of models, with its price premium |
| `results/tables/each-open-model.csv` | the measure in each model with open weights: its responses, premiums, reliability and price coefficient |
| `results/tables/share-premium-by-brand-and-model.csv` | each brand's share premium in every model that answered (Kimi Linear 48B A3B has its own estimates but enters no estimate over models) |
| `results/tables/rating-equivalent-by-brand-and-model.csv` | each brand's rating equivalent in every model that answered (Kimi Linear 48B A3B as above) |
