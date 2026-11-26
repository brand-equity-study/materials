# Study 1c: Product Feeds and a Store Search

In Study 1c, we tested whether an unfamiliar name still lowers how often models recommend the optimal product when the
products come as a store shows them, and when the model searches the store itself.

## Store listings

The models chose among Study 1a's 30 tables in 16 conditions of a store's listing:

- product feeds: OpenAI's product feed (current and October 2025), Google Merchant Center and schema.org markup;
- a "Sponsored" label on a familiar product or on the optimal product;
- the optimal product listed first, in the middle or last, or rated 0.1, 0.3 or 0.5 stars higher;
- an instruction in the system prompt;
- the plain listing of Study 1a, with and without the experience attributes.

Each condition was shown with and without brand names. The plan is `materials/store/analysis_plan.md`.

## Search step

In the first prompt, the model wrote one to three searches. In the second prompt, it saw the products that the store
returned and recommended one. The store's rule is at the top of `code/search/search_store.py`: a product scores the
number of search words in its name, brand, category and specifications, and each search returns at most three
products.

## Scripts

| Script | What it does | Writes (in `results/`) |
|---|---|---|
| `code/store/analyze_harness.py --panel claude`, `open`, `all` | the effect in every condition and its change from the plain listing | `store/claude/`, `open-all/`, `all-models/` |
| `code/search/rebuild_prompts.py` | rebuilds every search prompt and checks it against the materials | `search/prompts_check.json` |
| `code/search/analyze_search.py --panel claude`, `open`, `all` | how often the store returned the optimal product and how often the model chose it | `search/claude/`, `open-all/`, `all-models/` |
| `common/write_declines.py --study b16`, `--study b17` | each model's declines | the same `numbers.json` files |

## Files

| Folder or file | Contents |
|---|---|
| `materials/store/h2/prompts.jsonl.gz` | the 7,680 prompts of the store |
| `materials/store/h1/prompts.jsonl.gz` | 3,840 of the same prompts under other identifiers, which the open models answered |
| `materials/search/s1/stage1/`, `stage2/`, `nothing-returned/` | the search step's first prompts, each model's second prompts, and the searches that returned nothing |
| `data/store/claude/<model>.jsonl.gz` | the four Claude models' 15,360 responses to the store |
| `data/store/open-letters.csv.gz`, `open-letters-kind.csv.gz` | the open models' answers to the store (`b16`) and to the search step (`b17`) |
| `data/search/stage1/`, `stage2/`, `open-first-answers.jsonl.gz` | the responses to the search step |
| `data/open-models/store/h1/`, `store/h2-rung2/`, `search/stage2/` | the open models' full responses, with `RUNS.csv` |

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/store-effect-by-model-and-condition.csv` | each model's effect in the plain listing of the store and its change in each of the 15 other conditions |
| `results/tables/search-tests-by-model.csv` | each model's three tests of the store that it searched itself |
| `results/tables/store-variation-between-models.csv` | how much the effect and each condition's change varied between models |
| `results/tables/store-effect-by-condition.csv` | the effect of the fictitious name in each condition of the store |
