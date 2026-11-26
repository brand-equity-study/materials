# Study 1b: 64 Models on 34 Tables

In Study 1b, we tested whether models recommend the top-ranked product less often with brand names than without them,
over every model that we tested and under requests that people typed to chat assistants.

## Sources of responses

We pooled four sources, each comparing the same tables with and without brand names.

- **The 30-model corpus.** Thirty language models answered the 34 product tables 20 times with brand names and 20 times
  without them, between February and April 2026 (40,813 responses).
- **Current models on the same prompts.** Four current Claude models, four GPT-6 models and Claude Fable 5.2 answered
  the corpus's prompts again, also with the remaining brand clues removed.
- **Models with open weights.** They answered the same prompts on a university computing cluster (their responses are in
  `study1a-tables-with-one-optimal-product/data/open-models/rerun/`).
- **Consumers' own requests.** 218 shopping requests, 103 of them typed by people to chat assistants
  (`materials/requests/requests.jsonl.gz`), each paired with Study 1a's tables of its category.

## Analysis

The effect of brand names is the share of responses that do not recommend the top-ranked product with brand names minus
the share without them. `16_pooled.py` gives Study 1b's estimate over every model.

| Script | What it does | Writes (in `results/`) |
|---|---|---|
| `01_names_gap.py` | the effect over the 30 corpus models | `numbers.json`, key `names_gap` |
| `02_names_gap_by_model.py` | the effect in each model and each table | `names_gap_by_model` |
| `03_strict_dominance.py` | the tables in which the top-ranked product is at least as good on every ranked attribute | `strict_dominance`; `dominance_comparisons.csv` |
| `04_names_hidden_leaks.py` | the brand clues left in the tables without brand names | `names_hidden_leaks` |
| `05_recommended_price.py` | the price of the recommended product with and without brand names | `recommended_price`; `price_by_cell.csv` |
| `06_long_answers.py` | Gemini 2.5 Pro's responses that stop at a length limit | `long_answers_gemini_2_5_pro` |
| `07_model_settings.py` | each model's identifier, provider and settings | `model_settings` |
| `08_rerun.py` | the effect in the current models | `rerun.json` |
| `names_hidden_left.py` | the brand clues after the second check | `names_hidden_left.json` |
| `cleaning_changes.py` | what the removal of the brand clues changed | `cleaning_changes.json` |
| `14_requests.py` | the effect under consumers' requests | `requests/numbers.json`, `pairs.csv`, `answers.csv` |
| `15_requests_robustness.py` | the same, by source and by category | `requests/robustness.json` |
| `14_requests.py --all-models --leave-out kimi-linear48b` | the same over every model that answered every prompt | `requests/all-models/numbers.json`, `pairs.csv`, `answers.csv` |
| `17_requests_declines_and_per_model.py` | each model's declines and estimates under the requests | `requests/all-models/numbers.json` (its declines), `left_out.json`, `per_model.csv` |
| `18_clarifying.py` | the effect when a model may ask the shopper one question first | `clarifying/numbers.json` |
| `19_priorities.py` | the effect when the shopper states priorities | `priorities/numbers.json` |
| `16_pooled.py` | Study 1b over every model | `pooled/numbers.json`, `pooled/per_model.csv` |

The numbered scripts use `common/common.py` and `common/analyze.py`.

## Files

| Folder or file | Contents |
|---|---|
| `data/corpus/<model>/{names_shown,names_hidden}.jsonl.gz` | 40,813 responses of the 30 corpus models |
| `data/rerun/<model>/{shown,hidden,hidden_clean}.jsonl.gz` | 18,360 responses of the nine current models |
| `data/requests/<model>/{hidden,original,crossed}.jsonl.gz` | 4,248 responses of the four Claude models to consumers' requests |
| `data/requests-codex/<model>/{hidden,original,crossed}.jsonl.gz` | the GPT-6 models' responses to consumers' requests |
| `data/open-models/requests/<model>/` | the 32 open models' 33,984 responses to consumers' requests, with `RUNS.csv` |
| `materials/clarifying/prompts.jsonl.gz`, `data/clarifying/<model>/answers.jsonl.gz`, `data/open-models/clarifying/<model>/` | the prompts and responses of the clarifying question |
| `materials/priorities/prompts.jsonl.gz`, `data/priorities/<model>/answers.jsonl.gz`, `data/open-models/priorities/<model>/`, `data/corpus-priority-conditions/counts.csv` | the prompts and responses of the stated priorities |
| `materials/rerun/prompts.jsonl.gz`, `materials/requests/` | the prompts, and the bank of requests with how it was selected |
| `materials/rerun/priorities_plan.md`, `materials/rerun/clarifying_plan.md` | the analysis plans for the stated priorities and the clarifying question |
| `materials/attribute_rulings.csv`, `materials/names_hidden_leaks.csv` | the rules for each attribute and the list of brand clues (written with a language model; see the top README) |
| `materials/names-hidden-review/second_reader.json` | the second check of the list of brand clues |
| `materials/cleaning/` | the replacements that removed the brand clues |

In the file names, `names_shown`, `shown` and `original` are the tables with brand names; `names_hidden` and `hidden`
are the tables without them; `hidden_clean` is the same with the brand clues removed; and `crossed` is the tables with
the names swapped. `code/selection/select_requests.py` repeats the selection of the requests from the public sets
(about 17 GB to download), so it is not part of `run_all.py`.

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/the-34-product-tables.csv` | every product of the 34 tables with its brand, familiarity, price, quality, value and score |
| `results/tables/texts-that-identify-a-brand-by-table.csv` | for each table, the texts in the prompts without brand names that still identify a brand |
| `results/tables/effect-by-table.csv` | the effect of the fictitious name in each of the 34 tables |
| `results/tables/table-groups-and-deciding-attributes.csv` | each table's group and the attributes that decide its optimal product |
| `results/tables/effect-by-model-30-models.csv` | the effect of the fictitious name in each of the 30 models whose responses were deposited first |
| `results/tables/typed-requests-by-model.csv` | the effect of the fictitious name under requests that people typed, for each model |
| `results/tables/the-30-models-deposited-first.csv` | the 30 models whose responses were deposited first, with their developers and identifiers |
| `results/tables/settings-of-the-30-models.csv` | the settings recorded with each of those 30 models' responses |
| `results/tables/every-model-features-and-effect.csv` | every model's features and the effect of the fictitious name in it |
| `results/tables/effect-without-each-developer.csv` | the effect of the fictitious name with one developer's models left out at a time |
| `results/tables/stated-priorities-by-model.csv` | the effect of the fictitious name under each stated priority, for each model |
| `results/tables/clarifying-question-by-model.csv` | how often each model asked a clarifying question, with and without brand names, and its declines |
